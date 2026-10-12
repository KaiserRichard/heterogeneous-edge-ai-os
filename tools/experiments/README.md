# E4 real UART fault campaign

Run on the Raspberry Pi 5 with the STM32 attached. This runner and its analysis
are locally tested with synthetic fixtures; the real campaign remains **UNVERIFIED
ON HARDWARE**. No measurement results are included here.

Use the bridge/firmware from `feat/hw-fixes`: `hea_bridge` must decode
`STATE_EVENT` into `state_events.csv` with exactly these columns:

```text
seq,t_rx_pi_ns,mcu_us,old,new,reason,last_hb_mcu_us,last_inf_mcu_us,lost_count,t_mcu_pi_est_ns
```

The runner starts the bridge with its working directory set to each pipeline
directory, so its default `state_events.csv` lands there. If that branch exposes
an explicit filename option instead, pass, for example,
`--state-events-option=--state-events-csv` using the option it actually implements.
The runner requires the existing `--serial-fd` bridge option. Missing CSV/schema
or a failure to reach FRESH aborts before injecting a fault. This ticket does not
implement any firmware or bridge protocol changes.

From the repository root, the exact default run command is:

```bash
tools/experiments/e4_campaign.sh results/e4-real-001 5
```

The directory must be new. Defaults: `/dev/ttyAMA0`, 921600 baud, bridge CPU 2,
controller/source/inference CPU 0, synthetic inference work 20000 CPU us, source
period 100 ms, heartbeat period 20 ms, latest policy, echo period 500 ms. The
controller and monitor run away from the hog core so they can resume children,
observe power state, and bound cleanup. This affinity choice isolates the OS
scheduling fault to the bridge's core, as required by the experiment.

Each repetition executes four faults. Five repetitions reserve at least **10.7
minutes** for steady/observation/recovery-fit windows; allow about **34 minutes**
for startup, rearm and timeout allowances, plus the initial build. Actual runtime
depends on reset/startup time; the campaign prints its command and estimate before
running. A failed readiness check ends the campaign early. Preview without
hardware, sudo, builds or creating output:

```bash
tools/experiments/e4_campaign.sh results/e4-real-001 5 --estimate-only
```

Requirements are the existing Pi build tools and Python standard library,
`vcgencmd`, UART permissions, and `sudo` with `CAP_SYS_NICE` privileges for F4.
The runner calls `sudo -v` once up front and `sudo -n` for each hog. Each hog
self-terminates after one second measured on CLOCK_MONOTONIC_RAW; it makes no
system configuration changes. Linux's existing RT bandwidth limit still applies;
the campaign does not disable it.

The default local rearm command is `bash scripts/stm32/reset.sh`, which uses
OpenOCD/ST-LINK to reset the board. The current port latches FAILSAFE and has no
remote or automatic rearm. To use an already implemented local rearm procedure,
pass `--rearm-command 'COMMAND ARG ...'` or set `HEA_E4_REARM`. This is an argv
string parsed with `shlex`, run from the repository root, with a 15 s timeout;
shell expressions require an explicit `bash -c ...`. Reset must retain UART
connectivity. This runner makes no new rearm protocol.

Before each fault the board is rearmed/reset and a new pipeline must report FRESH
and a usable echo fit. It must remain continuously FRESH for 20 seconds: even
brief exits detected between polls abort the run. Then:

| Fault | Action | Fault end |
| --- | --- | --- |
| F1 | SIGKILL bridge; passive UART capture for 10 s | Start of restore/rearm after capture decoding |
| F2 | SIGSTOP bridge for 1 s, then SIGCONT | Immediately before SIGCONT |
| F3 | SIGSTOP inference for 1 s, then SIGCONT | Immediately before SIGCONT |
| F4 | sudo SCHED_FIFO 99 busy loop on the pinned bridge CPU for 1 s | End of the busy loop |
| F5 | SIGUSR1 bridge: suppress INFERENCE for 1 s; HEARTBEAT and ECHO continue | Acknowledged second SIGUSR1 resumes INFERENCE |

For F2–F5 the 10 s observation window starts at onset and includes the one second
fault. The onset clock read is immediately before the signal or the hog loop,
with no intervening file I/O. The hog records its own actual start/end. After
observation, stop the pipeline, rearm/reset, and start a fresh pipeline; retain
recovery events until FRESH and two further echo periods. Startup/recovery waits
default to 15 s (`--ready-timeout`). Cleanup resumes stopped children, terminates
and reaps all owned processes. F5 uses `pipeline/bridge_control.csv` acknowledgements
for effective onset/end (CLOCK_MONOTONIC_RAW); run metadata also records the
controller request times. A partially written INFERENCE finishes; the CSV records
its remaining bytes. Detection is timed from the last accepted inference in
STATE_EVENT, including any such in-flight frame. No queued results are replayed
on resume. F5 hardware behavior is **UNVERIFIED ON HARDWARE**. F3 tests a bounded
inference stall while the bridge continues its independent heartbeats.

F1 needs reception while its decoder is dead. A second descriptor keeps the real
tty open across SIGKILL. After reaping the killed bridge, the controller becomes
the only reader, saves `capture/uart.bin` and original chunk receipt times, and
never transmits on the UART. After observation, it feeds these bytes into the
same bridge decoder over an isolated socketpair; all decoder-generated TX is
discarded. The pipeline's latest pre-fault echo fit maps captured MCU events.
`capture/state_events.csv` receipt/mapping fields belong to replay and are **not**
used as physical arrival/onset times. Original byte arrival times remain in
`capture/chunks.csv`. There is no extra relay in the live bridge path and no
duplicate implementation of STATE_EVENT framing. Byte loss or a frame partially
consumed inside the killed bridge is a hardware verification concern: the summary
checks the event chain and reported `lost_count`; these cannot prove absence of
all UART/driver losses. Verify F1 transitions and capture completeness on the rig.

The power/thermal monitor samples at 0.5 s throughout each executed run, recording
RAW Pi time, `get_throttled`, temperature and all four CPU frequencies. INVALID:
any live bits 0–3, sticky bits 16–19 newly set relative to that run's initial
sample, unavailable monitor data, a gap over 0.75 s, uncovered measurement windows,
clock fit unavailable, residual RMS over `--rms-bound-us` (default 200 us), any
STATE_EVENT `lost_count > 0`, event state/time discontinuity, interrupted/failed
run, or failure of the prescribed steady/observation windows. Preexisting sticky
bits alone do not invalidate a new run.

Analysis writes `e4_runs.csv`, `e4_faults.csv`, `e4_faults.tex`, and
`e4_thresholds.json` in the campaign directory:

```bash
python3 analysis/e4_summary.py results/e4-real-001 --thresholds supervisor.json --rms-bound-us 200
```

The campaign saves the resolved configured values in `supervisor_thresholds.json`
and their original source in `campaign.json`. Reanalysis with no options uses
that snapshot and the campaign's saved RMS bound. Explicit analysis options
override those saved settings.

All latency columns are microseconds. Detection is the first FRESH exit within
observation, using `t_mcu_pi_est_ns` from the estimator, minus onset. Missing mappings
are reconstructed with the logged inverse affine echo estimator. Startup events
can use the first fit from that same MCU epoch. F1 replay uses the latest original
fit. Reset/restart has a separate `recovery/echo.csv` and MCU epoch; never subtract
MCU timestamps across reset. MCU-local detection/FAILSAFE metrics subtract
`last_hb_mcu_us` for heartbeat-timeout reasons and `last_inf_mcu_us` for result
timeout/HOLD reasons, recorded in `detection_reference` / `failsafe_reference`.
The legacy `local_reference` column names the injected fault's intended timer. These
measure elapsed time since the last accepted packet, rather than elapsed time
since the Pi signal. FAILSAFE Pi latency uses onset as its reference. Recovery
uses the first return to FRESH after fault end, including the prescribed wait
until local rearm; for F1 it includes restore/reset/startup. A fault with no
observed exit has no recovery latency. False transitions count all state changes
inside the 20 s steady phase.

No detected transition, no FAILSAFE, or no recovery is reported as censored with
blank values, never as zero. Per-fault distributions use only VALID runs and
nonmissing samples, nearest-rank P50/P95/max, with separate run and sample counts
and counts of INVALID/NOT_DONE. Reports carry the label **MEASURED (MCU timestamps
+ Pi timestamps, no logic analyzer)**. Synthetic tests are not campaign results.

Thresholds are read from literal `*_US` macros in `stm32/include/*.h` (optional
`SUPERVISOR_`/`HEA_` prefix), or the JSON passed through `--thresholds`:

```json
{
  "heartbeat_timeout_us": 100000,
  "result_hold_us": 200000,
  "result_failsafe_us": 500000,
  "rearm_healthy_us": 1000000,
  "transit_bound_us": 5000
}
```

Those example values are the **provisional configured constants** in this
worktree's `stm32/firmware/main.c`, not measurements; supply the values actually
flashed on your rig. The present `stm32/include` declares fields but contains no
numeric defaults, so omission of JSON leaves comparisons UNKNOWN. The runner
does not guess them. Keep the supplied configuration as campaign evidence.
Table comparisons select the threshold from the actual transition reason. A HOLD
can precede heartbeat FAILSAFE during F1/F2; comparing that first FRESH exit with
100 ms heartbeat timeout creates a false early-timeout diagnosis. Mixed reasons
are not pooled into a single threshold comparison. Source-age HOLD/FAILSAFE
labels show `threshold - age_at_send_us - transit_bound_us`; their raw receipt
elapsed time is not compared numerically with the full source-age threshold.
Inspect the recorded transition reasons: source age, last-packet phase, and the
supervisor evaluation period affect agreement. Source-age expiry includes the
last result's age-at-send plus transit allowance, so receipt-silence time alone
need not equal the source-age threshold. Pi onset and reset recovery latencies
have no direct supervisor timeout equivalent; their comparison cells say so.
The reset recovery used here bypasses healthy-interval rearm and therefore does
not test `rearm_healthy_us`.

Local tests, without sudo or hardware:

```bash
python3 -m unittest discover -s analysis/tests -v
bash -n tools/experiments/e4_campaign.sh
python3 -m py_compile tools/experiments/e4_campaign.py analysis/e4_summary.py
```
