# Pi-only pipeline

DESIGN: four independent C99 processes make scheduling, IPC residence and serial
dispatch measurable. Source → inference and inference → bridge use Unix datagrams;
the bridge owns one event loop and one wire sequence shared by heartbeat and
inference. FIFO (default) preserves order in a bounded 256-record queue and drops
new arrivals when full. `latest` retains one unsent result and counts overwrites.
Serial writes are nonblocking and partial frames finish before another frame starts;
heartbeats take priority between frames. This implements the queue comparison in
SYSTEM_GUIDE Part 2a without changing the shared protocol or adding threads.

## Socket ABI (for the separate Python ONNX ticket)

The receiver binds `--socket PATH`; its producer sends one record per AF_UNIX,
SOCK_DGRAM datagram to that path. Paths must be unused and fit `sockaddr_un.sun_path`.
Native C structs are **not** the ABI: use the packers in `include/hea_ipc.h`.
All fields are little-endian, without padding:

| Record | Python struct format | Fields | Bytes |
|---|---|---|---|
| Input | `<IQ` | frame_id u32, t_input_ns u64 | 12 |
| Result | `<IQQBB` | frame_id u32, t_input_ns u64, t_done_ns u64, class_id u8, confidence u8 | 22 |

`confidence` is an integer percentage 0..100, matching `hea_proto`.
Frame IDs start at zero, increase per generated input and must not repeat within
one run. Datagrams of the wrong size, confidence >100, or done before input are
rejected. The bridge also rejects done/input times in the future at dispatch.
Python must stamp with `time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)` on Linux:

```python
import socket, struct, time
sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
done = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
sock.sendto(struct.pack('<IQQBB', frame_id, t_input_ns, done, class_id, confidence),
            bridge_socket_path)
```

Do not mix CLOCK_MONOTONIC and CLOCK_MONOTONIC_RAW timestamps in a run. Absolute
release deadlines use CLOCK_MONOTONIC because Linux does not support RAW for
clock_nanosleep. Timestamp fields all use RAW. macOS software tests use MONOTONIC
for timestamps and a relative sleep repeatedly checked against an absolute
deadline; Linux sleep/scheduler/affinity checks are skipped on macOS.

## Build and test

```sh
make -C linux all
make -C linux test
```

Native Ubuntu 24.04 aarch64/Pi builds use the system C compiler and libc; tests
link `libutil` for `openpty`. macOS uses `<util.h>` and libc's `openpty`.
`CFLAGS` defaults to the protocol's C99 warning flags, including `-Werror`.
`SAN` defaults to ASan/UBSan for the tests **and every executable they launch**.
Tests cover independent golden IPC bytes, malformed records, FIFO order/full/wrap,
latest overwrites, shared wire sequence, heartbeat before results, rounded age, CRC recovery,
and two process integrations over `openpty`: 32 injected results and 8 complete
source/stub results. Python tests check analysis with synthetic fixtures, never
reported as measurements. Test artifacts remain under `linux/build/`.
On sandboxes that prohibit named socket bind (EPERM/EACCES), the integrations use
AF_UNIX datagram `socketpair` descriptors and explicitly report that limitation.
On normal hosts they exercise the named socket path.

## Programs

```sh
# Start consumers before producers. Use a private directory with short paths.
linux/build/hea_rx --serial /dev/pts/4 --csv rx.csv
linux/build/hea_bridge --serial /dev/pts/3 --socket /tmp/hea/bridge.sock \
  --policy fifo --heartbeat-ms 20 --csv bridge.csv
linux/build/hea_infer_stub --socket /tmp/hea/source.sock --output /tmp/hea/bridge.sock \
  --work-us 20000 --csv infer.csv
linux/build/hea_source --output /tmp/hea/source.sock --period-ms 100 --csv source.csv
```

The `/dev/pts/*` paths above are examples: use a socat pair or a real serial path.
TTYs are raw 8N1, no hardware/software flow control, default baud 921600. Supported
Linux baud values: 9600, 19200, 38400, 57600, 115200, and platform-provided
230400/460800/921600. A non-TTY path is opened without termios configuration.
On macOS `IOSSIOSPEED` sets numeric baud; PTYs ignore it where unsupported.
PTYs do not emulate baud-rate transmission time.

All programs accept `--csv PATH` (stdout if omitted), `--fifo-priority 1..99`
and `--cpu N`. Priority 0/default keeps normal scheduling. Requested real-time
scheduling or affinity failures terminate with a permission/allowed-CPU message;
they never silently fall back. These options require Linux; on macOS they fail
explicitly. Use suitable RLIMIT_RTPRIO/CAP_SYS_NICE permissions when testing them
on the Pi. This ticket does not implement cgroups/mlockall or the full P1 profile.
`--count N` limits generated inputs (source), completed results (stub), or decoded
inferences (rx); 0/default runs until SIGINT/SIGTERM. Bridge runs until signaled.

Source schedules its first sample immediately, then sleeps to absolute monotonic
deadlines. It skips missed releases rather than emitting a burst, counting them
as `missed_releases`; frame IDs advance for generated samples only. Nonblocking
IPC sends drop/count an input/result if the downstream socket is full.
The stub's default workload is 20000 **CPU microseconds** measured with
CLOCK_THREAD_CPUTIME_ID: preemption increases wall latency rather than reducing
the amount of synthetic computation. `--work-us N` accepts 0..60000000.
`--durations FILE` overrides it with 1..4096 integer CPU-us lines in that range,
cycling through the file. The stub does not sleep to simulate inference.

For a supervisor-compatible restart, the bridge samples a random 32-bit session
ID from OS randomness once per start, zero-extends it into the existing **uint64
v3 wire field**, and sends its establishing heartbeat first. Zero is a valid ID;
32-bit randomness has a collision possibility. Sequence is global uint16, starts
at zero and wraps across both message types. No framing changes are made.

The bridge drains at most 256 IPC records per event-loop turn, prioritizes due
heartbeats when selecting a new frame, and skips missed heartbeat releases.
One partially transmitted frame is immutable. Before its first successful write,
an unsent latest result can still be replaced. `t_send` is sampled immediately
before the first write accepting bytes; after EAGAIN it is recomputed. It includes
queue residence, but excludes subsequent kernel/TTY buffering and physical line
time. On signal the bridge discards/counts queued and partial results; it never
blocks indefinitely to flush a disconnected serial device. Heartbeat periods are
requested release intervals, not guaranteed deadlines during OS/serial stalls.

For portable PTY/process tests, `--serial-fd N` accepts an inherited serial fd;
`--socket-fd N` and `--output-fd N` accept inherited datagram descriptors (output
must be connected). Each replaces its corresponding path option. These avoid
reopening a Linux PTY master through `/dev/fd`, which could allocate another PTY.

## Reproducible Pi run

Requires `socat`, `make`, `python3` and a C compiler on the Linux target:

```sh
scripts/pi/run_pipeline.sh --duration 10 --policy fifo
scripts/pi/run_pipeline.sh --duration 10 --policy latest --work-us 50000 \
  --source-cpu 0 --infer-cpu 1 --bridge-cpu 2 --bridge-priority 50
```

The second example requires permission to use SCHED_FIFO. The script builds the
programs, creates socat's raw PTY pair, starts rx → bridge → stub → source,
checks startup/liveness, runs for the requested source duration, and stops them
in producer-to-consumer order. Default inference drain is one second
(`--drain-seconds N`), followed by 200 ms each for bridge and rx. Drain time
is extra to the requested duration; a remaining backlog is counted as missing or
discarded, not assumed delivered. Each process is given five seconds to stop
before SIGKILL. Cleanup also runs on startup failure, SIGINT and SIGTERM.

Default output: `results/YYYY-MM-DD/pipeline-HHMMSS-PID/`; `--run-dir PATH` selects
a new directory (existing directories are refused). It contains all four CSVs,
stderr counters, socat logs, exact script/process commands, before/after
`collect_metadata.sh` snapshots, `config.json`, copied durations if used,
`summary.json`, `validity`, `exit_code`, and DONE or FAILED. Set `HEA_COOLER` to
record the cooling setup. Short-lived socket/PTY links use a private `/tmp`
directory which cleanup removes. No system configuration changes are needed.

## Logs and analysis

- Source CSV: `frame_id,t_input_ns,status` (`sent`/`dropped`).
- Stub CSV: `frame_id,t_input_ns,t_done_ns,work_us,status`.
- Bridge CSV: `seq,frame_id,t_input_ns,t_done_ns,t_send_ns` for completed sends.
- Rx CSV: `type,seq,frame_id,t_input_ns,t_send_ns,t_rx_ns,age_at_send_us,crc_ok`.

INFERENCE has no exact `t_send_ns` on the wire. Rx reconstructs it as
`t_input_ns + age_at_send_us*1000`, an upper rounding of less than 1 us for
unsaturated v2/v3 ages. The field is empty for legacy/saturated ages. HEARTBEAT
has an exact wire send timestamp and blank input/frame/age fields. CRC failures
log `CRC_ERROR` with unknown identity fields empty and `crc_ok=0`; parser length,
version and payload errors appear in stderr counters. `t_rx` is software parser
completion after reading bytes, including any receiver scheduling/backlog delay.

```sh
python3 analysis/pipeline_summary.py results/YYYY-MM-DD/pipeline-HHMMSS-PID
```

The script joins by unique frame_id and verifies seq, input time and rounded age.
It uses the bridge's exact `t_send_ns` for transit latency. Output is JSON in us,
with sample counts and nearest-rank P50/P95/P99/max. Inference uses every completed
stub result (bridge sends if the stub CSV is absent), including results later
dropped/overwritten; dispatch uses all bridge sends. Transit and arrival AoI use
joined receives. Arrival AoI
is `t_rx - t_input`; time-average/peak age of the held latest value is a separate
E3 analysis. It reports source/stub IPC drops, bridge FIFO drops/latest overwrites,
shutdown discards and missing deliveries separately; these overlap and must not
be added together. Absent upstream CSVs/counters yield null, not invented counts.
Nonzero before/after throttling flags exclude the run from latency summaries;
unavailable metadata is labeled UNKNOWN. Empty samples produce null percentiles.

KNOWN: host checks are software verification, with a macOS clock fallback.
UNKNOWN: Ubuntu aarch64 execution, Linux real-time permission/affinity behavior,
the Pi runner, physical UART throughput and STM32 timing until run on those
targets. No Pi benchmark numbers are supplied by this implementation ticket.
