# FW3 implementation and build summary

## Implementation

- Added an optional register-level MPU6050 driver on I2C1 PB6/PB7 AF4 at 400 kHz.
- The `IMU=1` image adds a static 200 Hz FreeRTOS task at idle priority 0. It verifies
  WHO_AM_I, wakes the device, reads the 14-byte burst at 0x3B, and updates the
  public `imu_state` sample, DWT timestamp, counters, and release-jitter histogram.
- The default `IMU=0` build does not include the driver or task. UART framing and
  supervisor logic were not changed.
- Added pure-C big-endian parsing and unit conversion coverage to `make -C stm32 test`.

## Verification

Host builds on macOS, `-Wall -Wextra -Werror`:

| Configuration | text | data | bss |
|---|---:|---:|---:|
| `CLOCK_SOURCE=HSE RX_MODE=DMA UART_BAUD=921600 IMU=0` | 12,740 B | 4 B | 11,880 B |
| `CLOCK_SOURCE=HSE RX_MODE=DMA UART_BAUD=921600 IMU=1` | 13,740 B | 4 B | 14,096 B |

Both images built with `make -C stm32/firmware firmware`. `make -C stm32 test`
passed all four test programs, including the MPU6050 parser test. No image was
flashed; I2C operation, sample timing, and OS-T7 criteria remain to be checked
on the physical bench.

## OS-T7 bench follow-up

Follow the wiring and three UART load configurations in
[`docs/tickets/FW3_MPU6050.md`](../docs/tickets/FW3_MPU6050.md). Retain raw
`imu_state` observations and metadata beneath
`results/<YYYY-MM-DD>_os_t7_rtos_load/`. The task exposes counters/histogram for
debugger capture; no telemetry protocol extension is included.

## Conductor review (Claude, 2026-10-30)
- Fixed I2C CCR: DUTY bit was set (16/9), giving 42 MHz/(25*35) = 48 kHz; now DUTY=0, 42 MHz/(3*35) = 400 kHz. Rebuilt IMU=0/1, host tests pass. Not run on hardware.
