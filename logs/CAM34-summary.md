# CAM34 implementation and local verification

Implemented a camera source option for the E campaign. Synthetic remains the
default. Camera runs use the Pi libcamera backend at 640x480, with 15 fps for
E1/E2 and 30 fps for E3/E3B, a fresh `hea_cam` shared memory ring, and ONNX
inference reading `shm:hea_cam`. The source inherits the campaign source CPU,
FIFO priority, and memory-lock options.

Added `scripts/pi/os_t3_t4.sh` for the requested 3-repetition, 60-second OS-T3
and OS-T4 runs. It uses the Pi's local date in result directory names, reads
`PYTHON` and `MODEL_PATH` overrides, and prints per-condition CSV tables with
the scenario pass criteria. All pipeline runs stay on the existing socat PTY
path; no physical UART is opened.

Local checks on macOS:

- `make test` passed. Linux-only affinity and Unix socket tests were skipped by
  their existing platform/environment guards.
- `python3 -m unittest tools.experiments.tests.test_e_campaign -v` passed.
- `python3 -m py_compile tools/experiments/e_campaign.py` passed.
- `bash -n tools/experiments/camera_pipeline.sh scripts/pi/os_t3_t4.sh` passed.
- `git diff --check` passed.

No Pi run or hardware verification was performed. Camera capture, Pi
libcamera compilation, real-time scheduling, thermals, and observed OS-T3/T4
criteria remain unverified on the target.
