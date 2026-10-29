# FW4 — Optional CAN supervisor state output

## Scope and rationale

This is the phase 4/H5 bench extra approved in `docs/CAMERA_ROADMAP.md`. The Pi to
MCU bridge remains USART1 UART. CAN is an output-only observation path from the
existing supervisor; it does not feed control decisions back into the MCU. It
lets OS-T8 observe state messages and CAN controller counters on one two-node
bench bus without an external analyzer, while leaving the supervisor task and
priority scheme unchanged.

Build with `CAN_OUT=1` to include the implementation. The default `CAN_OUT=0`
image omits the CAN source, hooks, and receive-vector override.
The enabled image copies the current 113-word vector table to a 512-byte-aligned
RAM table and replaces the CAN2_RX0 entry. This keeps the existing flash startup
table intact; the RX ISR is bounded and does not call FreeRTOS.

## Frame and timing

CAN1 sends standard data frames with ID `0x120` and DLC 8:

| Byte(s) | Meaning |
|---|---|
| 0 | `supervisor_state_t` value |
| 1 | `supervisor_reason_t` last transition reason |
| 2–3 | Output sequence, little-endian u16 |
| 4–7 | Last `input_seq` (frame ID) accepted while the supervisor is FRESH, little-endian u32; it holds through HOLD/FAILSAFE and resets to zero on a session change |

The supervisor sends immediately on its first service, on every state/reason
change, and on a 100 ms periodic schedule. A full CAN1 TX mailbox drops that
message and increments `can_out_stats.tx_mailbox_full`; no wait or retry loop is
run in the supervisor. NART disables retransmission of an individual failed
frame, while MCR.ABOM enables hardware bus-off recovery per [ST RM0390
§30.7.6](https://www.st.com/resource/en/reference_manual/dm00135183.pdf). CAN2 FIFO0 accepts only
standard, non-remote ID `0x120` frames through filter bank 14; its bounded RX0
interrupt counts valid 8-byte messages and captures TIM2 time.

### BTR calculation

Both clock profiles use SYSCLK 84 MHz and APB1 divide-by-two, so bxCAN sees 42 MHz:

| Profile | PLL source | APB1 clock | Rate calculation | BTR |
|---|---:|---:|---:|---:|
| HSE | 8 MHz / M=8 | 42 MHz | 42 MHz / (6 × 14) = 500 kbit/s | `0x001A0005` |
| HSI | 16 MHz / M=16 | 42 MHz | 42 MHz / (6 × 14) = 500 kbit/s | `0x001A0005` |

At 500 kbit/s, one bit is 2 μs. The time-quanta period is
`6 / 42 MHz = 142.857 ns`; one bit has 14 quanta (`1 + BS1 11 + BS2 2`).
Thus `42 MHz / (6 × 14) = 500 kbit/s`, with sample point `(1 + 11) / 14 =
85.7%`. The encoded fields are BRP=`6−1=5`, TS1=`11−1=10`, TS2=`2−1=1`,
SJW=`1−1=0`, producing `(0<<24) | (1<<20) | (10<<16) | 5 = 0x001A0005`.
The same BTR is derived at initialization from the APB1 frequency passed by
`main.c`; `can_out_stats.btr` records the programmed value.

## H5 wiring

Use two 3.3 V-compatible CAN transceivers. MCU CAN pins are logic-side signals;
do not connect PB pins directly to CANH/CANL. Power down the setup before
changing jumpers.

| Nucleo-F446RE pin | Function | Transceiver connection |
|---|---|---|
| PB8 / D15 | CAN1_RX, AF9 | Transceiver 1 RXD output |
| PB9 / D14 | CAN1_TX, AF9 | Transceiver 1 TXD input |
| PB12 / CN10-16 | CAN2_RX, AF9 | Transceiver 2 RXD output |
| PB13 / CN10-30 | CAN2_TX, AF9 | Transceiver 2 TXD input |

Connect transceiver 1 CANH to transceiver 2 CANH and CANL to CANL. Join their
signal grounds to Nucleo GND. Confirm each transceiver supply and logic-level
requirements from its own datasheet. Put one 120 Ω termination across CANH/CANL
at each physical end of the bus, for exactly two end terminators total; if
modules have selectable terminators, enable one at each end only. Keep a short
linear bus and short stubs.

## Run OS-T8

After physically completing H5, build and flash the FW4 image manually; this
ticket work does not flash hardware. Connect CAN1 and CAN2 through their
transceivers as above, then reset the Nucleo. Run the OS-T6 fault cases: kill
the bridge, stop inference, apply the FIFO CPU hog, and send stale results with
live heartbeats; collect 10 trials per fault. Check that every state change is
followed by a matching CAN2 RX interrupt and that the CAN2 receive count grows.

The debugger-visible `can_out_stats` contains TX queued/completed/failed and
mailbox-full counts; RX valid/invalid/overrun counts; CAN1/CAN2 ESR snapshots and
TEC/REC; bus-off, warning and passive event counts; last RX timestamp/payload;
and state delivery latency data. An eight-entry fixed ring tracks transitions
that can be in flight together. `state_latency_bins[0..9]` cover 0–99 through
900–999 μs in 100 μs buckets; bin 10 is ≥1000 μs. `state_announcements` counts
the initial state and each state/reason change. `state_rx_count` counts the
first valid RX frame matching each announcement's state, reason, and output
sequence. `state_delivery_missed` counts announcements that could not be tracked
because the ring was full. For OS-T8, require
`state_announcements == state_rx_count`, `state_delivery_missed == 0`, bin 10
zero (therefore P99 under 1 ms), and CAN1/CAN2 TEC/REC remaining zero.
`rx_frames` also includes periodic frames, which are excluded from the
state-change latency buckets.

Example debugger inspection:

```gdb
p can_out_stats
p can_out_stats.state_latency_bins
p can_out_stats.can1_tec
p can_out_stats.can2_rec
```

## Host validation

Run the register-independent payload test on macOS with the existing STM32 host
test target:

```sh
make -C stm32 test
```

It checks little-endian sequence and frame-ID packing for mixed, zero, and
maximum values. Cross-build both HSE variants (CAN off/on) and the HSI CAN image
with `arm-none-eabi-gcc`; build success is compile/link validation only. Actual
bus timing, transceiver wiring, CAN error counters, and OS-T8 latency require
the bench run.
