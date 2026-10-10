# Portable supervisor — Step 2 and A3 restart/rearm edges

Status: implemented and host-tested; firmware, physical UART and safe-output timing
are not validated. The core is pure C99 with no heap, HAL, FreeRTOS or clock calls.
`hea_proto` remains the only wire library; no wire format changes are needed.

## Scope and meaning of FRESH

Step 2 checks heartbeat liveness and result freshness independently, using
caller-supplied extended MCU-local **microseconds**. The existing `_ticks` API names
are retained, but arbitrary tick units are no longer permitted. For v2/v3 results:

```
source_age_estimate_us = age_at_send_us
                       + (now_MCU_us - received_at_MCU_us)
                       + transit_bound_us
```

The age at send is a Pi-local duration. The subtraction above is entirely MCU-local;
Pi timestamps are never subtracted from MCU timestamps. The estimate includes MCU
queue delay because receipt time is captured before handoff and retained at dispatch.
All additions saturate at UINT64_MAX. The diagnostic `source_age_estimate_us` is
updated on each valid-time evaluation and is meaningful only while `has_result` is
true. It clears on rearm/session reset.

`transit_bound_us` is an explicit uint32 configuration value marked **PROVISIONAL**.
Zero is allowed for controlled tests, not a claim of zero transport delay. No measured
or proven default is supplied. It must account for the entire send-to-receive path,
including software queues and serialization after age capture, plus clock-rate
uncertainty. Sender input and send timestamps must use the same Pi CLOCK_MONOTONIC;
age must cover input to the stated send boundary. Comparable microsecond units,
monotonic local clocks and sufficiently small rate error are assumed. This is an
**estimate under those assumptions, not an exact AoI or a proven upper bound**.
Hardware measurement and clock mapping remain separate future validation.

FRESH requires heartbeat receipt silence below its limit and result age below
`result_hold_ticks`. HOLD and FAILSAFE use the same configured result thresholds for
source age as Step 1 used for receipt silence, including equality at each boundary.
An initial source result at/above hold stays safe INIT; at/above failsafe it latches
FAILSAFE immediately. Source-age expiry in INIT is evaluated before accepting a
replacement, including one arriving exactly at the failsafe deadline.
A stale result cannot establish rearm health. Periodic updates
must continue without traffic. A packet arriving at an already-expired failsafe
boundary cannot hide expiry; valid recovery traffic never clears the latch itself.
`SUPERVISOR_REASON_SOURCE_AGE_HOLD/TIMEOUT` distinguish source-age transitions.

V1 results lack age. They retain receipt-silence behavior, **without adding transit
allowance**, flagged by `receipt_silence_fallback`. For these results the diagnostic
field reports receipt silence, not source age; FRESH has only the legacy receipt
meaning. A v2/v3 zero age is present, not a legacy marker. Each accepted advancing
result replaces the flag/age metadata; duplicate or rejected results cannot replace it.

The core accepts ages 0..UINT32_MAX when `has_age_at_send` is true and rejects wider
values before advancing watermarks or renewing health. UINT32_MAX is the sender's
legitimate saturation value; it is treated conservatively as a very old result, never
as absence. A saturated sender value loses its true age, so the estimate cannot be
claimed as an upper bound. At the adapter, age must be at least the Pi-only
input-to-done duration rounded up to microseconds. Sender saturation is exempt from
this plausibility check (and still evaluated as old); v1 retains legacy validation.
Malformed length, reversed Pi timestamps and confidence above 100 remain invalid.
No receiver can verify that a plausible sender age is truthful.

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

All times and thresholds use microseconds. Receipt times must be no later than evaluation time and no earlier than the
current initialization/rearm epoch; invalid times do not refresh any timer.
A hardware timer wrap must
be extended into nondecreasing uint64 microseconds. `supervisor_extend_mcu_us` takes
the previous extended sample and current raw uint32 timer. Initialize the previous
value to the first raw sample; sample strictly within 2^31 us (about 35.8 minutes).
Unsigned deltas support wrap; half-range/ambiguous gaps, apparent regression and
uint64 overflow return false without writing the output. The owner must treat a
failed extension as a clock fault and select safe output, not silently continue
with a frozen clock. Multiple wraps or sufficiently large backward jumps cannot be
inferred from two raw samples. Extend chronologically at receipt/evaluation, never
when dispatching an old queued raw timestamp. Clock regression latches
FAILSAFE, ignores that event, and breaks the observed healthy interval.

The caller must supply nonzero `heartbeat_timeout_ticks`, `result_hold_ticks`,
`result_failsafe_ticks` and `rearm_healthy_ticks`; result failsafe must exceed hold.
There are no silently calibrated defaults. Invalid configuration leaves a safe,
unrearmable FAILSAFE until a valid initialization.

| State | Behavior |
|---|---|
| INIT | Safe output; waits until both a valid heartbeat and advancing result are recently received. No-data startup remains safe INIT. |
| FRESH | Both conditions valid; missing heartbeat goes directly to FAILSAFE, result age reaches HOLD. |
| HOLD | Heartbeat continues but results are stale; a fresh result recovers FRESH; heartbeat expiry or result failsafe deadline latches FAILSAFE. |
| FAILSAFE | Safe output is retained; traffic may establish health but never clears the latch by itself. |

Expiration uses `elapsed >= threshold` and is evaluated **before** processing an
event at that time. Thus a packet at an already-expired failsafe deadline cannot
hide expiry. HOLD can recover if a result arrives before its failsafe deadline.
`last_transition_reason` records a state transition, not each packet diagnostic.

Only explicit `supervisor_rearm` can leave FAILSAFE, after heartbeat and result freshness conditions
have stayed healthy for the configured interval. Expiry during the interval resets
it, including an event arriving exactly at a timeout. Rearm returns to safe INIT and
clears receipt/health flags, preserving sequence watermarks. New post-rearm heartbeat
and advancing result are needed for FRESH. This API is a local request: **no UART
rearm message** is added. The hardware/user command that invokes it is later work.

Every event carries a local `generation` captured alongside `received_at_ticks`
at receipt/handoff. `supervisor_receive_frame` takes that captured generation as an
explicit argument; reading `sv.generation` at delayed dispatch would incorrectly
make old traffic current. The owner serializes capture with update/rearm. Successful
rearm increments `sv.generation`; mismatches are rejected even in the same coarse
tick and counted in saturating `rejected_generation_events`. Failed rearm leaves
generation unchanged. Timer evaluation still precedes rejection. No queue or
concurrency mechanism is introduced by this portable API.

V3 HEARTBEAT carries an opaque uint64 `session_id`; v1/v2 have no session. The first
explicit ID or a changed ID increments local generation to invalidate outstanding
queue entries, clears wire/input sequence and receipt/health history, and accepts
the establishing heartbeat. It returns to INIT unless FAILSAFE remains latched.
Zero is a valid session ID. New results are required for FRESH; in FAILSAFE, traffic
can establish the healthy interval but only local rearm clears the latch. Rearm
preserves the session ID and sequence history. Same-session replays cannot reset
history. A legacy heartbeat cannot downgrade an established session. Legacy-only
operation preserves the existing sequence policy and cannot detect sender restart.
See `protocol/PROTOCOL.md` for exact version/length and sender ordering rules.

Generation and session ID are distinct: generation belongs to local queue ownership;
session ID belongs to the sender incarnation. Never derive either from receipt ticks
or reset generation when the sender restarts. Generation must not wrap: exhaustion
refuses rearm/session reset; clear the queue and reinitialize before exhaustion.
Any full initialization must also invalidate all outstanding queue entries.

Sequence arithmetic is unsigned half-range: delta 0 is duplicate, below half-range
is newer, above is older, exact half-range is ambiguous. The header is uint16 and
one per-Pi stream across HEARTBEAT, INFERENCE and ECHO_REQ, per `PROTOCOL.md`.
The inference input sequence is independently uint32. Invalid, duplicate, old and
ambiguous events never refresh timers. A valid new header with a repeated/old input
advances the wire watermark but never refreshes result silence or heartbeat.
ECHO_REQ advances only the wire watermark. MCU-to-Pi/unknown frames are ignored.

This assumes strictly ordered delivery from a single Pi sender and fewer than half
the counter space between accepted frames. The bridge changes session ID on every
restart and sends its heartbeat before results/echoes. Old queued sessions are
rejected by generation. An arbitrary historical session replayed on the wire under
a current local stamp cannot be distinguished from a restart; CRC/sequence checks
do not authenticate the sender. Results/echoes have no session ID. Source-age estimates do not authenticate or validate the sender clock.

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
| Queued old events and pre-rearm backlog | Receipt time and generation retained; same-tick older-generation events rejected and counted |
| Sender reset | Changed session resets both watermarks and receipts; INIT unless FAILSAFE latched |
| Large nonzero MCU clock | Deadlines depend on elapsed ticks |
| Clock regression/invalid config | Safe FAILSAFE; no timer renewal |
| Pi timestamps near uint64 maximum | Same-domain plausibility only; no cross-clock subtraction |
| V2/v3 age, transit allowance and delayed queue | Source estimate drives hold/failsafe and rearm health |
| V1 absence vs v2/v3 zero | Flagged receipt fallback vs present zero age |
| Age exceeds wire range or understates input-to-done | Rejected without watermark/health renewal |
| Saturated sender age and estimate arithmetic | Old result remains old; addition saturates instead of overflowing |
| Uint32 MCU timer wrap and invalid sampling | Correct extended duration; rejected ambiguous/regressing/overflow sample |

Hardware follow-up: first flash a minimal FreeRTOS Nucleo image using its Mini-B
ST-LINK USB connection (no Pi UART wires yet). Verify task release and safe output.
Then, with power off, connect Pi TX GPIO14 to PA10 RX, Pi RX GPIO15 to PA9 TX, and
shared GND. GPIO17 to PA0 is for later clock validation. Validate pin routing,
UART console ownership and electrical levels before power-on. Run CRC/sequence
fault tests on the real link; observe failsafe with an analyzer. A successful host
or cross-compile check does not establish electrical reliability or bounded latency.

Rollback: keep this feature branch isolated; revert its commit if required. No
primary-checkout user changes, boot/UART settings or slides are changed. The separate
v3 HEARTBEAT extension retains v1/v2 decoding.
