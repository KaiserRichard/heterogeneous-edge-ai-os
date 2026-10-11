# Offline inference workload (Pi-only item 2.5, inference part)

This is a CPU/memory workload for studying scheduling and contention, not an ML
accuracy experiment. No C changes, priority changes, UART changes, or new imaging
library are required. Only NumPy and ONNX Runtime (and its wheel dependencies) are
needed at runtime. Standard-library tests run without either package.

## Prepare on the connected Mac, install on the offline Pi

Run from the repository root on the Mac with Python/pip and curl available:

```sh
bash linux/inference/fetch_offline_deps.sh offline-bundle
```

The script downloads CPython 3.12 Linux aarch64 binary wheels, including transitive
wheel dependencies, and `mobilenetv2-12.onnx`. Defaults are ONNX Runtime 1.20.1 and
NumPy 2.1.3; override with `ORT_VERSION` / `NUMPY_VERSION` if required. `MODEL_REF`
can be a fixed onnx/models commit (default `main`). The resulting `SHA256SUMS`
identifies every downloaded artifact and `fetch-config.json` records its source.
A checksum pins the retrieved content; it is not an upstream signature. Keep the
whole bundle for repeat runs. The destination must be new; failed fetches leave an
incomplete directory for inspection. Do not use it until a successful fetch finishes.

Copy the bundle by hand to the Pi. On Ubuntu 24.04 aarch64 with Python 3.12:

```sh
(cd offline-bundle && sha256sum -c SHA256SUMS)
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --no-index --find-links offline-bundle/wheels \
    onnxruntime==1.20.1 numpy==2.1.3
```

Use the matching version pins if the bundle was fetched with overrides. No build
step is needed for these Python scripts. Neither runtime script downloads anything.
Do not install the Linux wheels into a Mac venv.

Sources: [ONNX MobileNet model and normalization contract](https://github.com/onnx/models/tree/main/validated/vision/classification/mobilenet),
[ORT Python session API](https://onnxruntime.ai/docs/api/python/api_summary.html).

## Benchmark

```sh
python linux/inference/infer_bench.py \
    --model offline-bundle/mobilenetv2-12.onnx --threads 1 --cpu 0 \
    --warmup 50 --runs 1000 --output results/inference-single
```

`--model` defaults to `mobilenetv2-12.onnx` in the current directory. The model must
have exactly one float32 input compatible with `1x3x224x224`; symbolic dimensions
are allowed, but the supplied tensor is always that fixed shape. CPUExecutionProvider is the sole provider;
intra-op threads are explicitly 1–4, inter-op threads 1, execution sequential.
`--cpu 0,1` pins the process before imports/session creation so workers inherit the
mask; affinity is optional and Linux-only. Record the effective mask in the report.
Requested threads can exceed cores in the mask; choose masks deliberately.

The fixed image is seeded (`--seed 12345`) NumPy uint8 RGB noise, 256x256. The same
image is reused for every run. Optional `--image path.npy` accepts a uint8 array
of shape `(256,256,3)`; `--image path.ppm` accepts binary RGB PPM (P6, maxval 255,
256x256). NumPy array loading disables pickle. JPEG/PNG decoding is intentionally
not included. Image reading/generation is outside all measured intervals.

Preprocessing uses NumPy only: nearest-neighbor resize to 224x224 (index
`floor(i*256/224)`), divide RGB by 255, subtract ImageNet mean `[.485,.456,.406]`,
divide by std `[.229,.224,.225]`, convert to contiguous float32 NCHW. This is a fixed
workload transform, not the zoo's accuracy-validation center-crop procedure.

Timing is `time.clock_gettime_ns(CLOCK_MONOTONIC_RAW)` on Linux where exposed and
`time.perf_counter_ns()` elsewhere. The clock name is recorded. Never mix clock
domains when subtracting pipeline timestamps.

- Cold start: session creation plus exactly one first `run`, with input prepared
  beforehand. Imports, file hashing, image load and preprocessing are excluded;
  model loading/optimization is included. One observation per process, not a
  distribution of repeated cold launches; OS filesystem cache is not cleared.
- After cold start, 50 additional warm-up runs by default are excluded.
- Each of the 1000 measured runs by default separately times preprocessing and
  synchronous `session.run`, including Python/ORT call overhead. No pacing or
  concurrent requests. Allocation/release of tensors is included in preprocessing.
- CSV/JSON writing and summary calculation happen after the measured loop.

The output directory must be new. `samples.csv` contains every measured
`run_idx,pre_ns,infer_ns` (zero-based index, integer nanoseconds). `summary.json`
contains config, model/input file hashes, versions, affinity, seed, clock,
`cold_start_ns`, and count/P50/P95/P99/max/mean for each interval. Percentiles use
linear interpolation at `(n-1)*p/100`, not nearest rank. A cold-start summary has
count 1; its percentile fields describe that single observation only.

## Four-thread sweep (Pi/Linux only)

From the repository root, with the venv active:

```sh
COOLER_DESCRIPTION='active cooler, fixed setup' \
    bash linux/inference/sweep.sh results/inference-idle -- \
    --model offline-bundle/mobilenetv2-12.onnx

bash linux/inference/sweep.sh results/inference-loaded \
    --stress stress-ng --cpu 2 --taskset 2,3 -- \
    --model offline-bundle/mobilenetv2-12.onnx --cpu 0,1
```

`PYTHON` selects an interpreter (default `python3`). Arguments after `--` go to the
benchmark, except `--threads`/`--output`, which the sweep owns. `--stress` takes a
command and its argument vector up to `--`; no shell-string evaluation occurs.
Install stress-ng beforehand on the Pi. Each thread setting gets a fresh stressor
process group (Linux `setsid`), a 1-second startup allowance (not a readiness
measurement), and group cleanup on exit/signals. Early stressor exit fails the run.
A stressor should last for the entire run; omit short stress-ng timeouts.

Each new root has `threads-{1,2,3,4}/` with before/after snapshots from
`scripts/pi/collect_metadata.sh`, exact quoted benchmark/stress commands, cooler
note, logs, `bench/samples.csv`, `bench/summary.json`, and `validity.json`. Nonzero
throttle/history bits or unavailable throttle state mark
`eligible_for_aggregate=false`; failed runs are also ineligible. Individual raw
summaries remain for inspection, but exclude ineligible runs from comparisons.
This script does not combine distributions or invent missing platform data.
Repeat the whole sweep into new roots at least three times for study results.
No cooler description means `unknown`, which must be resolved for a reproducible
hardware experiment. No P1 scheduling policy/cgroup setup is performed here.

## Pipeline server and IPC contract

Start the bridge receiver first, then:

```sh
python linux/inference/infer_server.py \
    --model offline-bundle/mobilenetv2-12.onnx --threads 2 --cpu 0,1 \
    --source-socket /tmp/hea-infer.sock --bridge-socket /tmp/hea-bridge.sock
```

One blocking Unix datagram receiver processes one input at a time. No application
queue, latest-value overwrite, worker pool, or warm-up is added: kernel socket
queueing and inference delays remain observable OS effects. Records contain IDs
and timestamps only; this workload runs the same deterministic image per frame.
The first pipeline frame therefore includes first-run effects. `--max-frames N`
allows a finite integration run; default is unlimited.

KNOWN: `linux/include/hea_ipc.h` is absent on this branch. The requested fallback
contract is therefore defined here and in `bench_common.py`, with little-endian
fields, no native padding:

| Datagram | Python struct | Size | Fields in order |
|---|---|---|---|
| source → inference | `<QQ` | 16 bytes | frame_id u64, t_input_ns u64 |
| inference → bridge | `<QQQIf` | 32 bytes | frame_id u64, t_input_ns u64, t_done_ns u64, class_id u32, confidence IEEE-754 f32 |

`t_input_ns` is copied unchanged. Source, inference, and bridge must use the same
Pi `CLOCK_MONOTONIC_RAW` clock; the Mac fallback is for software verification only.
`t_done_ns` is sampled after preprocessing, inference and stable-softmax
postprocessing, before packing/sending. `class_id` is the zero-based ImageNet
argmax (0–999); confidence is softmax probability (0–1) for the zoo logits.
Malformed datagram lengths are reported/dropped, including oversized datagrams;
future input timestamps are rejected. Missing bridge, inference errors or send
errors fail visibly rather than silently discarding valid results. SIGINT/SIGTERM
clean up the server's bound socket; existing endpoints are never removed at
startup. After SIGKILL, manually remove a stale socket only after confirming its
owner is gone. Socket queues may block/drop under load; this is not a lossless IPC
or authenticated input contract.

This layout **must be reconciled with the C pipeline** when its IPC header is
added. It is distinct from `protocol/PROTOCOL.md` UART framing: the bridge must
explicitly map u64 frame IDs to the protocol's u32 input sequence, map class IDs
(the UART u8 cannot represent every ImageNet class), quantize confidence to a
percentage, and calculate age-at-send on the same clock. Those mappings require
an explicit pipeline decision; these datagrams must not be sent directly to UART.

## Local verification and evidence

```sh
python3 -m unittest discover -s linux/inference/tests -v
python3 -m compileall -q linux/inference
bash -n linux/inference/sweep.sh linux/inference/fetch_offline_deps.sh
```

The standard-library tests cover percentile interpolation/errors, summary/CSV
preservation, independent IPC golden bytes and size/range rejection, clock/CPU
handling, mock benchmark warm-up exclusion, Unix datagram server behavior, offline
bundle hashes/target selection, sweep metadata/throttle flags, and stressor cleanup.
Script tests use fake downloads and fake inference, never performance samples.
Linux affinity tests skip on macOS. Real socket tests also skip if the sandbox
denies Unix socket binding; mock IPC tests still run. Optional NumPy numerical
tests skip when NumPy is absent. No C implementation is introduced, so C99
compiler/sanitizer checks are not applicable to this ticket.

UNKNOWN until target verification: real-model execution, full offline wheel
resolution/download, Pi latency distributions, thermal behavior under stress,
and interoperability with the future C pipeline. Fake-model tests establish only
software behavior, not real inference performance. This ticket does not complete
the source/bridge/logger or item 2.5 experiments and supplies no measurement data.
