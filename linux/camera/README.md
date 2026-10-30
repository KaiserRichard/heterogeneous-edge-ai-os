# CAM1 camera source

Pixels use a bounded shared-memory ring; the existing 12-byte little-endian
`hea_input {frame_id, t_input_ns}` datagram remains the notification. This keeps
bridge/UART framing unchanged and exposes OS scheduling, IPC freshness and buffer
overwrite effects without placing large images in the socket queue. One producer
owns the ring; readers never block it. Four slots are the default. A native reader
copies atomic bytes between two sequence checks so ARM memory ordering is enforced;
a busy/torn copy or reused slot is logged and never sent to inference.

Build and host checks: `make -C linux/camera`, `make -C linux/camera test`.
The Makefile builds fake capture everywhere and includes the libcamera backend only
when `pkg-config --exists libcamera` succeeds. No camera software is vendored.
Run `make -C linux/camera clean all` after changing the installed libcamera or build
flags so an earlier fake-only binary is rebuilt. The backend targets the C++17
libcamera API; compilation against the conductor's Pi installation remains pending.

## Running (conductor on the Pi later)

Start the result receiver first, then inference (the ring is opened lazily after
the first notification), then the camera. Example, with a receiver already bound
at `/tmp/hea-results.sock`:

```sh
python3 linux/inference/infer_server.py --socket /tmp/hea-input.sock \
  --output /tmp/hea-results.sock --image-source shm:cam_t1 --csv inference.csv
linux/camera/build/hea_cam --backend libcamera --output /tmp/hea-input.sock \
  --csv frames.csv --count 9000 --width 640 --height 480 --fps 30 --shm cam_t1
python3 linux/camera/analyze_t1.py frames.csv --fps 30 --output summary.json
```

On macOS replace `--backend libcamera` with `--backend fake`. `--count 0` runs
until SIGINT/SIGTERM; positive counts include capture/drop callbacks. `--fps`
defaults to 30; the inherited `--period-ms` is also supported but cannot be combined
with `--fps`. `--output-fd` accepts a connected Unix datagram socket for tests.
Scheduling uses the existing `hea_options_parse` / `hea_schedule` (`--cpu`,
`--fifo-priority`, `--mlock`); these require Linux and suitable privileges.
Libcamera creates its own event/worker threads after scheduling is applied.
No new application capture thread is created; the callback copies and publishes
one frame, and the main thread handles shutdown. Callback CSV and pixel-copy cost
are included in source overhead and must be measured on the Pi.

Fake pixels at (x,y) are `(x+frame_id, y+frame_id, frame_id)` modulo 256.
`--fake-offset-ns N` defaults to 1000000 and subtracts N from the generated
capture time; `t_input_ns` is represented in the host bridge clock domain.
`--fake-drop-every N` suppresses every Nth capture
(sequence  N-1, 2N-1, ...); zero disables injection. Missed fake releases advance
the sequence without a callback and are reported separately. Frame IDs never wrap
within a run. Use a fresh name for each run.

## Storage and lifetime

Linux uses POSIX `shm_open`, visible as `/dev/shm/NAME`. macOS uses a mode-0600,
exclusively created mmap file `/tmp/hea-cam-NAME` because it has no `/dev/shm`;
this is only a host-test surrogate, not camera timing evidence. Names accept an
optional leading slash, then 1..100 letters, digits, underscores or hyphens.
The creator refuses existing objects; it never truncates another producer's ring.
The ring is retained on normal completion/SIGTERM so queued notifications can be
drained. After all consumers stop, remove that run's `/dev/shm/NAME` on Linux or
`/tmp/hea-cam-NAME` on macOS. A crash may also leave the object. Never remove a live
ring or restart a producer under a name still mapped by a consumer.

ABI v1 is little endian (macOS ARM64/x86_64, Pi ARM64), with a 64-byte header:

| Offset | Type | Meaning |
| --- | --- | --- |
| 0 | uint32 | magic 0x43414548 (HEAC) |
| 4 | uint32 | version 1 |
| 8, 12 | uint32 | width, height |
| 16, 20 | uint32 | slots, pixel bytes (width × height × 3) |
| 24, 28 | uint32 | slot stride, header-ready flag |
| 32 | 32 bytes | reserved zero |

Slot `frame_id % slots` starts at `64 + index * stride`. Its first 16 bytes are
uint64 sequence counter, uint32 frame_id, uint32 reserved, then tightly packed
R,G,B bytes. Stride is `round_up(16 + pixels, 64)`. Zero counter means unpublished;
the single writer publishes odd -> atomic pixel/ID writes -> even. Readers make
one bounded copy with acquire loads and fences; no spin retry or blocking lock.
Counter mismatch/odd is `torn`; stable wrong ID/unpublished is `overwritten`.
The native reader library owns the memory-ordering operations, including atomic
byte accesses to avoid C++ data races. Build requires lock-free 64-bit atomics.
Dimensions are limited to 4096 per axis, slots to 64, total storage to 256 MiB.
The source and Python reader each allocate a reusable frame buffer. Python
preprocessing owns a verified copy and uses nearest-neighbor indexing to 224×224,
then the existing normalization. For fixed 256×256 input, tensor bytes and CSV
bytes remain unchanged. `--max-frames` counts selected valid notifications,
including rejected ring images, so a finite all-overwritten run terminates.
`--input-policy latest` continues logging discarded notifications as `skipped_stale`.

Libcamera requests packed `formats::BGR888` (R,G,B **byte** order on little-endian
hosts), checks the negotiated dimensions/format, maps allocated DMA buffers once,
brackets CPU reads with DMA_BUF_IOCTL_SYNC, and strips per-row stride padding.
There is no camera-side resize in this implementation. Unsupported adjusted
formats/sizes fail explicitly. It selects the first enumerated camera; use a
single connected IMX219 for these experiments. Four libcamera request buffers are
separate from the configurable IPC slot count. The callback uses
`FrameMetadata::sequence` for frame_id/CSV seq, preserving observable capture-buffer
gaps rather than request queue numbering. Those counters may not expose every
sensor/frontend loss on every pipeline; confirm Pi pipeline behavior during T1.
Missing/nonpositive SensorTimestamp or failed buffers are logged without publishing.

## Clocks, output, and analysis

CSV is:

```text
frame_id,seq,t_sensor_ns,t_recv_raw_ns,t_input_ns,status,t_clock_offset_ns
```

`seq` is capture sequence, **not** the internal slot seqlock. `t_sensor_ns` keeps
the unmodified SensorTimestamp. `t_recv_raw_ns` is a nearby RAW clock sample and
`t_input_ns` is the sensor time mapped to CLOCK_MONOTONIC_RAW; this is the value
sent in `hea_input`. `t_clock_offset_ns` (`t_input_ns - t_sensor_ns`) is appended,
preserving the prior column order. Status is `sent`, `dropped` (IPC backpressure), `injected_drop`,
`missing_timestamp`, or `capture_error`. The callback logs unsuccessful capture
rows too; an unavailable timestamp is zero. Startup metadata is JSON on stderr
and `<csv>.meta.json` when `--csv` is specified, including requested configuration
and startup BOOTTIME/MONOTONIC/RAW readings (BOOTTIME is null where unavailable).
Stderr ends with generated/sent/dropped/missed_releases counts. Camera inference
retains the old CSV schema, using blank completion times for `overwritten`/`torn`,
and counts these statuses on stderr.

Libcamera specifies SensorTimestamp in CLOCK_BOOTTIME. For each completed request
the callback takes three BOOTTIME/RAW pairs, selecting the narrowest RAW bracket,
then maps sensor time by subtracting `(boottime_now - raw_now)`. AoI origin is the
sensor exposure timestamp mapped to CLOCK_MONOTONIC_RAW. This assumes no suspend
and negligible clock slew between samples. Check that per-frame
`t_clock_offset_ns` remains stable. Camera inference uses the bridge clock
(`CLOCK_MONOTONIC_RAW` on Linux, `perf_counter_ns` elsewhere).

Camera timestamps now share the bridge's RAW clock domain, so bridge age validation
and AoI use compatible timestamps under the stated no-suspend assumption.

The analyzer uses capture rows (`sent` and IPC `dropped`) for sensor intervals,
absolute jitter `|delta - 1e9/fps|`, and recv−sensor offset percentiles. Percentiles
use linear interpolation at `(n-1)*p/100`. `sequence_gaps` counts missing captures
between successful captures. `missing_sequences` counts absent CSV sequence IDs;
`capture_drops` adds those to explicitly logged capture errors/injections, counting
boundary injections once. IPC drops are separate. No inference is made about
unobserved IDs before the first or after the last CSV row. Empty samples produce
null metrics; empty CSV, non-increasing sensor times, and sequence regressions are
errors. These definitions and nominal FPS must accompany any T1 report.

API references checked during implementation:
[libcamera application guide](https://github.com/libcamera-org/libcamera/blob/master/Documentation/guides/application-developer.rst),
[SensorTimestamp control definition](https://github.com/raspberrypi/libcamera/blob/main/src/libcamera/control_ids_core.yaml),
[Request sequence/reuse](https://docs.libcamera.org/master/public-api/classlibcamera_1_1Request.html),
[Pi pixel-format documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf).

Host tests exercise ASan/UBSan native concurrent reads, a deterministic sequence change
between copy and verification, slot reuse, fake CSV/drop accounting, exact timestamp datagrams,
and the native reader with real numpy preprocessing and a fake model over Unix
socketpairs. Physical camera capture, DMA coherency, sensor colors, negotiated FPS,
Pi scheduling, and libcamera compilation remain conductor checks on the Pi.
