# FW4 CAN output — build summary

Date: 2026-10-30  
Scope: optional STM32 supervisor-state CAN output; no hardware was flashed.

## Implementation

- Added register-level bxCAN1 transmit and bxCAN2 FIFO0 receive, enabled only by
  `CAN_OUT=1` (default `0`). UART remains the Pi-MCU bridge.
- CAN1 sends standard ID `0x120`, DLC 8: state u8, reason u8, sequence u16 LE,
  last inference `input_seq` accepted while FRESH, u32 LE. The frame ID holds
  through HOLD/FAILSAFE and resets on session change. It sends on first service, state or
  reason change, and every 100 ms.
- CAN2 filter bank 14 accepts only standard, non-remote ID `0x120`. The RX0 ISR
  counts valid frames and captures RX time and payload. Debugger-visible
  `can_out_stats` includes RX/TX/drop/error/TEC/REC counters, state-delivery
  misses, and 100 μs state-to-RX latency buckets. An eight-entry pending ring
  tracks multiple state changes that are still in flight together.
- CAN1/2 set MCR.ABOM for hardware bus-off recovery. NART avoids retrying a
  failed state frame indefinitely. A full mailbox is dropped and counted
  immediately; supervisor service never waits for transmission.
- `CAN_OUT=1` installs a 512-byte-aligned RAM vector table for CAN2 RX0. The
  default image retains the flash vector table unchanged.

## APB1 and BTR calculation

Both configured clock sources produce 84 MHz SYSCLK and APB1 divide-by-two:

| Build | PLL input | APB1 | BTR |
|---|---:|---:|---:|
| HSE | 8 MHz / M=8, N=336, P=4 | 42 MHz | `0x001A0005` |
| HSI | 16 MHz / M=16, N=336, P=4 | 42 MHz | `0x001A0005` |

For 500 kbit/s, select prescaler 6, BS1 11 tq, BS2 2 tq, SJW 1 tq. Total bit
time is 14 tq; `42 MHz / (6 × 14) = 500 kbit/s`, with a 2 μs bit and an 85.7%
sample point. BTR encodes BRP=`6−1=5`, TS1=`11−1=10`, TS2=`2−1=1`,
SJW=`1−1=0`; therefore `(0<<24) | (1<<20) | (10<<16) | 5 = 0x001A0005`.
The initializer derives BRP from the APB1 frequency supplied by `main.c` and
stores the programmed BTR in `can_out_stats.btr`. ABOM behavior follows [ST
RM0390 §30.7.6](https://www.st.com/resource/en/reference_manual/dm00135183.pdf).

## Validation

All builds used Arm GNU Toolchain with `-Wall -Wextra -Werror`; no compiler or
linker warnings were emitted.

| Command | Result | ELF text / data / BSS |
|---|---|---:|
| `make -C stm32/firmware firmware CLOCK_SOURCE=HSE RX_MODE=DMA UART_BAUD=921600` | pass, CAN_OUT default 0 | 12,740 / 4 / 11,880 B |
| `make -C stm32/firmware firmware CLOCK_SOURCE=HSE RX_MODE=DMA UART_BAUD=921600 CAN_OUT=1` | pass | 14,580 / 8 / 12,952 B |
| `make -C stm32/firmware firmware CLOCK_SOURCE=HSI CAN_OUT=1` | pass | 14,468 / 8 / 12,952 B |
| `make -C stm32 test` | pass | Existing supervisor, DMA cursor and tick diagnostics passed; CAN payload packing passed 3 cases |

The CAN host test checks mixed-endian, all-zero, and all-maximum payloads.
Cross-builds and host packing do not verify transceiver wiring or physical CAN
timing. OS-T8 remains a bench task after H5 is wired with two transceivers and
120 Ω terminations at each end. No firmware image was flashed.
