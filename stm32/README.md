# Portable supervisor v2 — Step 1

Status: implemented and host-tested; firmware, physical UART and safe-output timing
are not validated. The core is pure C99 with no heap, HAL, FreeRTOS or clock calls.
It adapts the earlier `feat/software-skeleton-wip` supervisor design but does not
merge that branch or its second protocol implementation. `hea_proto` remains the
only wire library. Protocol v2 appends Pi-local `age_at_send_us`; the adapter accepts
v1 and v2 but Step 1 deliberately ignores source-age fields.

## Scope and meaning of FRESH

Step 1 checks **heartbeat liveness** and **result receipt silence** independently,
using caller-supplied extended MCU-local ticks. FRESH means both receipt conditions
are within their configured limits. It does **not** establish source freshness or
Age of Information (AoI). A delayed input with a genuinely advancing `input_seq`
can still pass this step. No Pi timestamp is subtracted from MCU time.

Source age is Step 2. A possible estimate is:

```
age_upper = pi_age_at_send + MCU_elapsed_since_receive + transit_bound
```

Offset synchronization is not required to add durations, but units and clock-rate
uncertainty must be accounted for. `pi_age_at_send` must cover input to actual send;
`transit_bound` must cover every remaining send-to-receive delay, including software
queues/serialization, not only nominal baud time. This would be an upper estimate
under stated assumptions, not exact measured source AoI. No validated transit bound
exists yet. The separately approved protocol v2 now supplies an age-at-send field,
but the supervisor does not use it yet. Source-age policy, clock mapping and GPIO
validation remain later work.

## Files and ownership

- `include/supervisor.h`, `src/supervisor.c`: state, local deadlines, sequence rules,
  explicit rearm; no protocol dependencies.
- `include/supervisor_protocol.h`, `src/supervisor_protocol.c`: bounded adapter from
  CRC-checked `hea_proto` frames. Only frames emitted by `hea_parser_feed` may enter
  this adapter. CRC is a parser responsibility, not a boolean supplied by the wire.
- `tests/test_supervisor.c`: synthetic-time state tests and real encoder/parser tests.
- `Makefile`: host tests using the existing shared wire implementation and sanitizers.

The core has **one owner**: serialize every update and rearm call. Future RX task
handoff must pass bounded events to the supervisor owner, not concurrently mutate
this structure from an ISR or status task. Events carry `received_at_ticks` from
the actual MCU receipt boundary separately from evaluation time. Queued backlog
must retain that timestamp; dispatch time must never masquerade as receipt time. Firmware ownership/queues are not built.
Call update periodically even without incoming traffic. Tick thresholds and the
future 1 kHz release period must be calibrated/verified on hardware.

## Contract

All times and thresholds use the same local tick unit. Receipt times must be no later than evaluation time and no earlier than the
current initialization/rearm epoch; invalid times do not refresh any timer.
A hardware timer wrap must
be extended by the port into nondecreasing uint64 ticks. Clock regression latches
FAILSAFE, ignores that event, and breaks the observed healthy interval.

The caller must supply nonzero `heartbeat_timeout_ticks`, `result_hold_ticks`,
`result_failsafe_ticks` and `rearm_healthy_ticks`; result failsafe must exceed hold.
There are no silently calibrated defaults. Invalid configuration leaves a safe,
unrearmable FAILSAFE until a valid initialization.

| State | Behavior |
|---|---|
| INIT | Safe output; waits until both a valid heartbeat and advancing result are recently received. No-data startup remains safe INIT. |
| FRESH | Both conditions valid; missing heartbeat goes directly to FAILSAFE, result silence reaches HOLD. |
| HOLD | Heartbeat continues but results are silent; timely new result recovers FRESH; heartbeat expiry or result failsafe deadline latches FAILSAFE. |
| FAILSAFE | Safe output is retained; traffic may establish health but never clears the latch by itself. |

Expiration uses `elapsed >= threshold` and is evaluated **before** processing an
event at that time. Thus a packet at an already-expired failsafe deadline cannot
hide expiry. HOLD can recover if a result arrives before its failsafe deadline.
`last_transition_reason` records a state transition, not each packet diagnostic.

Only explicit `supervisor_rearm` can leave FAILSAFE, after both receipt conditions
have stayed healthy for the configured interval. Expiry during the interval resets
it, including an event arriving exactly at a timeout. Rearm returns to safe INIT and
clears receipt/health flags, preserving sequence watermarks. New post-rearm heartbeat
and advancing result are needed for FRESH. This API is a local request: **no UART
rearm message** is added. The hardware/user command that invokes it is later work.

The owner must atomically invalidate queued pre-rearm events on successful rearm
(or attach a local epoch generation to queued events). Receipt-time filtering
rejects strictly earlier ticks, but a pre-rearm event received in the same coarse
tick as rearm is indistinguishable by timestamp alone. Queue invalidation belongs
to the future firmware port; the portable core does not own a queue.

Sequence arithmetic is unsigned half-range: delta 0 is duplicate, below half-range
is newer, above is older, exact half-range is ambiguous. The header is uint16 and
one per-Pi stream across HEARTBEAT, INFERENCE and ECHO_REQ, per `PROTOCOL.md`.
The inference input sequence is independently uint32. Invalid, duplicate, old and
ambiguous events never refresh timers. A valid new header with a repeated/old input
advances the wire watermark but never refreshes result silence or heartbeat.
ECHO_REQ advances only the wire watermark. MCU-to-Pi/unknown frames are ignored.

This assumes strictly ordered delivery from a single Pi sender and fewer than half
the counter space between accepted frames. After Pi reboot, counters may restart:
a session/sequence-reset policy needs a separate design; rearm does not silently
accept old counters. CRC/sequence checks do not authenticate an adversarial sender.

## Build and test

On macOS or Ubuntu/Pi, from repository root:

```sh
make -C protocol test
make -C stm32 test
```

Expected: both exit 0, protocol reports tests passed, supervisor reports all scenarios
passed, and no compiler/sanitizer errors. Check count includes an exhaustive uint16
increment/wrap check; it is not a count of independent hardware tests.

Compile-only for STM32F446RE, from repository root:

```sh
mkdir -p stm32/build
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
  -std=c99 -Os -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror \
  -Istm32/include -c stm32/src/supervisor.c -o stm32/build/supervisor_m4.o
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
  -std=c99 -Os -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror \
  -Istm32/include -Iprotocol/include -c stm32/src/supervisor_protocol.c \
  -o stm32/build/supervisor_protocol_m4.o
```

This compiles object files, not linked FreeRTOS firmware. No board is needed.

## Acceptance matrix

| Check | Expected evidence |
|---|---|
| Startup, heartbeat-only, result-only | INIT safe until both are healthy |
| Results continue, heartbeat lost | FAILSAFE at heartbeat boundary |
| Heartbeats continue, results stop | HOLD at receipt-silence boundary, FAILSAFE at result boundary |
| Timely result while HOLD | FRESH before failsafe; arrival exactly at failsafe remains latched |
| Duplicates/old/ambiguous counters | No health timer renewals |
| Header/input counter wrap | Legal increments accepted; old pre-wrap frame rejected |
| New header, repeated input | Wire watermark advances, result timer unchanged |
| Corrupted encoded frame through real parser | No delivered event; timers unchanged; CRC counter increments |
| CRC-valid malformed/unknown/semantically invalid payload | Adapter ignores; deadlines still evaluated |
| Healthy traffic after FAILSAFE | Latch remains, including after healthy interval completes |
| Missing/early rearm and interrupted healthy interval | Rearm refused |
| Eligible explicit rearm | INIT; anti-replay history preserved |
| Queued old events and pre-rearm backlog | Actual receipt time retained; strictly pre-epoch events rejected; same-tick queue invalidation is a firmware requirement |
| Sender reset | Old input watermark preserved; reboot needs separate session policy |
| Large nonzero MCU clock | Deadlines depend on elapsed ticks |
| Clock regression/invalid config | Safe FAILSAFE; no timer renewal |
| Pi timestamps near uint64 maximum | MCU receipt deadlines unaffected; no cross-clock subtraction |

Hardware follow-up: first flash a minimal FreeRTOS Nucleo image using its Mini-B
ST-LINK USB connection (no Pi UART wires yet). Verify task release and safe output.
Then, with power off, connect Pi TX GPIO14 to PA10 RX, Pi RX GPIO15 to PA9 TX, and
shared GND. GPIO17 to PA0 is for later clock validation. Validate pin routing,
UART console ownership and electrical levels before power-on. Run CRC/sequence
fault tests on the real link; observe failsafe with an analyzer. A successful host
or cross-compile check does not establish electrical reliability or bounded latency.

Rollback: keep this feature branch isolated; revert its commit if required. No
primary-checkout user changes, boot/UART settings or slides are changed. The separate
protocol-v2 ticket changes payload/version, with legacy decoding retained.
