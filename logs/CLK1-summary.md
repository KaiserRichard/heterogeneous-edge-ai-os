# CLK1 — camera timestamps on the bridge clock

Implemented camera timestamp conversion so `hea_input.t_input_ns` uses the
bridge's `CLOCK_MONOTONIC_RAW` domain on Linux. Libcamera preserves the original
BOOTTIME `SensorTimestamp` in the CSV, samples three nearby BOOTTIME/RAW pairs
at request completion, and maps with the narrowest pair. The CSV appends
`t_clock_offset_ns`; analysis accepts both the previous and current schemas and
reports per-frame offset stability. Fake capture also emits input timestamps in
the host bridge clock domain. Camera inference selects the shared
`bench_common.clock()` implementation.

AoI origin is the sensor exposure timestamp mapped to CLOCK_MONOTONIC_RAW. The
mapping assumes no suspend and negligible clock slew between the clock-pair
samples. Check stability of `t_clock_offset_ns` across the run before using the
data for AoI conclusions.

Verification on macOS: `make test` passed (49 Python analysis tests, 3 expected
environment skips, plus protocol, STM32 and Linux suites); `make -C
linux/camera test` passed, including fake CSV/datagram behavior and mapping
arithmetic. `git diff --check` passed. The libcamera backend could not be built
because libcamera is unavailable through `pkg-config` on this host. No Pi or
hardware run was performed.
