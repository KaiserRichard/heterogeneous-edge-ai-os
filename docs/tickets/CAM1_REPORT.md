# CAM1 worker report — 2026-10-29

CAM1 implementation is ready for conductor review. Host `make test` passed.
No commit, push, flash, SSH, or Pi contact was performed. Changes are confined to
CAM1's write scope and this report; normal existing build/test artifacts were
created by the required repository checks.

## Changes

| Files | Change |
| --- | --- |
| `linux/camera/hea_cam.cpp`, `camera.h` | Source CLI, existing runtime parser/scheduling integration, fake patterns/offset/drop injection, unchanged 12-byte source records, CSV and startup clock metadata |
| `linux/camera/libcamera_backend.cpp` | Conditional real backend: capture buffer sequence, SensorTimestamp, first-action MONOTONIC receive timestamp, requested dimensions/FPS, reusable mapped DMA buffers and request lifecycle |
| `linux/camera/ring.h`, `ring.cpp` | Bounded shared-memory RGB ring; exclusive producer, atomic seqlock publication and bounded native reader; C ABI for Python ctypes |
| `linux/camera/Makefile`, `README.md` | C++17 build, clear libcamera skip, native reader library, sanitizer tests; architecture justification, ABI, commands, lifecycle, clocks and limitations |
| `linux/camera/analyze_t1.py` | Interval mean, P99 absolute jitter, sequence gaps/drop accounting, offset P50/P99/max, explicit metric definitions and no overall hardware-validity claim |
| `linux/inference/infer_server.py`, `model_runtime.py` | `--image-source fixed\|shm:NAME`; lazy native copy, camera-sized nearest-neighbor preprocessing, overwritten/torn skip rows/counters; explicit POSIX MONOTONIC only in camera mode |
| `linux/camera/tests/test_ring.cpp`, `test_camera.py` | Concurrent producer/reader with verified successful copies, odd/changed sequence rejection, slot reuse, exclusive ownership/cleanup, CSV, exact datagrams, injected drops and analyzer checks |
| `linux/inference/tests/test_camera_source.py` | Real fake-camera executable and Unix datagram socketpairs through native image reader and real numpy preprocessing, deterministic model; overwrite/torn handling, preserved timestamps, fixed default/explicit CSV equality and tensor byte equality |
| root `Makefile` | Adds camera fake/native tests to `test`, before inference tests |

The ring uses POSIX shared memory on Linux (`/dev/shm/NAME`) and a documented
mmap file on macOS (`/tmp/hea-cam-NAME`). A normal source exit retains the ring so
queued notifications remain readable; after consumers stop, remove that run's
object explicitly. Existing names are refused, never truncated. The README
justifies separate bounded pixel storage while preserving the IPC/protocol bytes.

## Commands and actual outputs

Host identification:

```text
$ uname -srm
Darwin 24.6.0 x86_64
$ python3 --version
Python 3.11.0rc2
$ pkg-config --exists libcamera
[no output; exit 1]
```

Read `AGENTS.md` and `PROJECT.md` first, followed by all ticket inputs and existing
inference tests. Before editing, ran root `make` (default target `test`), exit 0.
Representative real output:

```text
all protocol tests passed
clock-sync tests passed (51 checks; tolerances offset/drift 0.01 us, jitter 0.55 us, drift 0.001 ppm)
24 supervisor scenarios passed (66822 checks, including exhaustive 16-bit increment wrap).
PASS: IPC golden packing/validation; FIFO order/full/wrap; latest overwrite
SKIP: named Unix socket bind denied by sandbox; exercising the same datagram ABI via socketpair
SKIP: Linux clock_nanosleep/RAW/sched_setaffinity checks (macOS host)
Ran 43 tests in 23.513s
OK (skipped=3)
```

First camera build, `make -C linux/camera`, exit 0. No compiler errors occurred:

```text
libcamera unavailable via pkg-config: skipping real backend; building fake backend
mkdir -p build
cc -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_DARWIN_C_SOURCE -D_POSIX_C_SOURCE=200809L -I../include -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Werror -c ../src/hea_runtime.c -o build/hea_runtime.o
cc -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_DARWIN_C_SOURCE -D_POSIX_C_SOURCE=200809L -I../include -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Werror -c ../src/hea_ipc.c -o build/hea_ipc.o
c++ -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_DARWIN_C_SOURCE -D_POSIX_C_SOURCE=200809L -I../include -std=c++17 -O2 -g -Wall -Wextra -Wpedantic -Werror  hea_cam.cpp ring.cpp  build/hea_runtime.o build/hea_ipc.o   -pthread -o build/hea_cam
c++ -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_DARWIN_C_SOURCE -D_POSIX_C_SOURCE=200809L -I../include -std=c++17 -O2 -g -Wall -Wextra -Wpedantic -Werror -fPIC -dynamiclib ring.cpp  -o build/libhea_camera.dylib
```

The first new inference integration run failed, exit 1:

```text
test_fake_camera_to_inference_overwrites_and_rgb ... ERROR
TimeoutError: timed out
Ran 4 tests in 3.286s
FAILED (errors=1)
```

Diagnosis from real clock readings:

```text
monotonic_ns 1163562286779422
CLOCK_MONOTONIC 2396662143106000
perf_counter_ns 1163562286789334
```

The receiver had rejected all source timestamps as future inputs because Python's
Mac monotonic clock had a different epoch from the C source's POSIX clock. Fixed
camera-mode inference to use `time.clock_gettime_ns(time.CLOCK_MONOTONIC)`; the
fixed-image clock remains unchanged. Also fixed two ResourceWarnings in the first
camera test fixture by closing the CSV and removing an unused socketpair.

After that fix:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s linux/inference/tests -p test_camera_source.py -v
test_fixed_default_and_explicit_csv_identical ... ok
test_shm_cli_selects_monotonic_and_closes_reader ... ok
test_fake_camera_to_inference_overwrites_and_rgb ... ok
test_fixed_preprocessing_bit_identical ... ok
Ran 4 tests in 0.367s
OK
```

Full regression run:

```text
$ make test > linux/camera/build/make-test.log 2>&1
[exit 0]
```

Selected exact lines from the log (suite order: Linux summary, analysis, logic
analyzer, camera Python tests, inference):

```text
Ran 6 tests in 0.026s
OK
Ran 78 tests in 102.922s
OK
Ran 9 tests in 1.494s
OK
Ran 3 tests in 1.077s
OK
Ran 47 tests in 19.620s
OK (skipped=3)
```

The protocol, supervisor, DMA/tick, IPC and sanitized native pipeline tests also
passed in that run. The three inference skips were existing platform restrictions:
Linux affinity and two filesystem Unix socket bind tests. CAM1's Unix socketpair
integration test ran and passed; it was not skipped.

After strengthening the native concurrency test to require successful checked
copies while the producer remains active, reran its full camera target:

```text
$ make -C linux/camera test > linux/camera/build/camera-test.log 2>&1
[exit 0]
libcamera unavailable via pkg-config: skipping real backend; building fake backend
PASS: concurrent atomic copies (valid=11, torn=497971, overwritten=10); no torn payload accepted
PASS: unpublished slot, odd sequence and changed-after-copy rejected, slot reuse, exclusive owner, cleanup
Ran 3 tests in 0.380s
OK
```

Contention counts are scheduling-dependent, not timing benchmarks. Tests include a
deterministic sequence change between copy and verification, so rejection coverage
does not depend on winning a scheduling race. Both logs remain in the ignored
`linux/camera/build/` directory; the excerpts above preserve evidence in this report.

`git diff --check`: no output, exit 0. Final status inspection showed only the
scoped Makefile/inference edits and new camera/test/report files.

## Limitations and conductor decisions

1. **Clock-domain conflict in the unchanged bridge.** `hea_bridge.c` calls
   `hea_raw_now()` for send timestamps and age validation. CAM1 is explicitly
   required to send SensorTimestamp and measure reception in MONOTONIC. On Linux
   RAW and MONOTONIC are distinct; the unchanged bridge can reject these results
   or compute biased ages. This cannot be corrected while both preserving the
   ticket's timestamp requirement and respecting its prohibition on bridge/runtime
   edits. CAM1 keeps the 12-byte ABI but does not claim full-pipeline clock
   compatibility. Resolve this in a separately authorized clock-domain change
   before any end-to-end AoI experiment.
2. Libcamera's documented SensorTimestamp is BOOTTIME. CAM1 preserves it exactly
   and records the startup BOOTTIME/MONOTONIC pair, following the roadmap's
   no-suspend assumption. It does not silently map clocks or fall back to receive
   time. Offset positivity/bounds and clock constancy require Pi measurements.
3. **Real backend not compiled or executed here.** `pkg-config libcamera` fails on
   this Mac; its C++17 API, frame format/stride, DMA coherency, actual FPS, request
   lifecycle, sensor sequence behavior, and sensor timing must be checked against
   the conductor's Pi libcamera installation. After installing/changing libcamera,
   use `make -C linux/camera clean all`. No vendoring or guessed hardware claim.
4. Real images/ORT inference, Pi scheduling/affinity/mlock, five-minute OS-T1 runs,
   throttle/governor evidence, and physical IMX219 capture remain untested. Host
   integration uses real numpy and a deterministic fake model, not ORT performance.
5. macOS shared memory is the documented file-backed surrogate. Linux POSIX shm
   and ARM atomic behavior still require Pi execution. Named Unix socket binding
   is sandbox-denied; real Unix socketpairs validate the byte stream locally.
6. `FrameMetadata::sequence` reports buffer gaps. Whether the selected Pi pipeline
   exposes every sensor/frontend drop through it must be established on hardware.
   One clock pair cannot prove constant BOOTTIME−MONOTONIC; the summary reports
   that limitation explicitly. Normal-exit rings need documented manual cleanup.

No edits were made to protocol, STM32, third-party references, bridge, UART,
`hea_runtime`, or `bench_common` sources.
