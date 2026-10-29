# CAM1 — Pi Camera v2 frame source with sensor timestamps

Goal: replace synthetic frames with real IMX219 frames while keeping the 12-byte
`hea_input` datagram (`frame_id`, `t_input_ns`) and the rest of the pipeline unchanged.
Authority: owner request 2026-10-29 (OS/CN handoff); roadmap `docs/CAMERA_ROADMAP.md` phase 0.
Architecture note (AGENTS.md §7): pixels move through a shared-memory slot ring instead of the
datagram, so the IPC record, bridge and UART protocol stay byte-identical; justify this in the
README you write.

Inputs: AGENTS.md, PROJECT.md, docs/CAMERA_ROADMAP.md, docs/TEST_SCENARIOS.md (OS-T1),
linux/src/hea_source.c, linux/src/hea_runtime.c, linux/include/hea_ipc.h, hea_runtime.h,
linux/inference/infer_server.py, model_runtime.py, bench_common.py and their tests.
Write scope: new `linux/camera/` (C++17 or C11 + C++ libcamera backend, Makefile, README),
`linux/inference/infer_server.py` + `model_runtime.py` (new `--image-source` option only),
new tests under `linux/camera/tests/` and `linux/inference/tests/`, the top-level Makefile
`test` target (add the camera fake-backend tests), this ticket. No protocol/, stm32/,
third_party/, bridge or UART changes.

Implementation:
1. `hea_cam` program: same CLI conventions as `hea_source` (`--output`, `--csv`, `--count`,
   scheduling options via `hea_options_parse`), plus `--backend fake|libcamera`, `--width`,
   `--height`, `--fps`, `--shm NAME`, `--slots N` (default 4).
2. Shared memory `/dev/shm/<NAME>`: header + N slots of RGB888 (or the model's input size
   after a documented resize). Each slot has a seqlock counter and `frame_id`; the writer
   bumps seq odd -> writes -> even. Readers copy and re-check; a torn or overwritten slot is
   counted, never used.
3. Per frame: `t_sensor_ns` from libcamera `controls::SensorTimestamp`, `t_recv_mono_ns` =
   `CLOCK_MONOTONIC` in the request-completed handler. Send `hea_input{frame_id,
   t_input_ns=t_sensor_ns}`. At startup log one pair of `CLOCK_BOOTTIME`/`CLOCK_MONOTONIC`
   readings into the run metadata. CSV columns:
   `frame_id,seq,t_sensor_ns,t_recv_mono_ns,t_input_ns,status`.
4. `fake` backend (builds on macOS and Linux without libcamera): deterministic test pattern,
   synthetic sensor timestamps = monotonic − configurable offset, optional injected drops.
   `libcamera` backend compiles only when `pkg-config libcamera` succeeds; Makefile skips it
   with a clear message otherwise (Mac). Do not vendor libcamera.
5. `infer_server.py --image-source fixed|shm:NAME` (default `fixed` = today's behaviour,
   byte-identical CSV): with `shm`, read slot `frame_id % N`, preprocess that image; if the
   slot no longer holds `frame_id`, record status `overwritten` and skip.
6. `linux/camera/analyze_t1.py`: from the CSV compute OS-T1 metrics (interval mean, P99
   jitter, sequence gaps, recv−sensor offset P50/P99/max) into `summary.json`.

Acceptance (Mac): fake-backend unit tests for seqlock (concurrent writer/reader, torn read
detected), slot reuse, CSV schema, drop accounting; `infer_server` `fixed` default unchanged
(existing tests pass) and `shm` path tested with the fake backend end to end on a Unix socket;
`make test` green. On the Pi (later, conductor): `make -C linux/camera` builds the libcamera
backend. Report: files, commands with output, what is untested until the Pi (no hardware claim).
No commit/push: the conductor reviews, then commits on `feat/camera-source`.
