# STM32 Real-Time Supervisor Module

## Purpose
Provides the core real-time deadline monitoring and safety state machine for the STM32 supervisor.

## Design Constraints
- Zero STM32 HAL / CMSIS dependencies in the core state machine.
- Zero FreeRTOS dependencies in the core state machine.
- Operates strictly in the MCU receiver's local time domain (`current_time_ticks`).
- No dynamic memory allocation.

## Sequence Arithmetic
Sequence IDs are 32-bit unsigned integers evaluated using explicit modular half-range semantics:
- `delta = current_seq - last_seq` (modulo 2^32)
- `delta == 0`: Duplicate
- `0 < delta < 2^31`: Strictly newer
- `delta > 2^31`: Older / stale
- `delta == 2^31`: Ambiguous / half-range boundary

## State Machine
```
   [INIT]
     | (first valid packet)
     v
  [FRESH] <--------------------+
   |   |                       |
   |   | (timeout >= fresh)    | (fresh valid packet)
   |   v                       |
   | [HOLD] -------------------+
   |   |
   |   | (timeout >= failsafe)
   v   v
[FAILSAFE] --------------------+ (recovery packet)
```

## Threshold & Policy Configuration
- `fresh_timeout_ticks`: Maximum delay before entering `HOLD`.
- `failsafe_timeout_ticks`: Maximum delay before entering `FAILSAFE`.
- `max_consecutive_invalid`: **Provisional Policy**. Max consecutive invalid packets before immediate `FAILSAFE` (set to `0` to disable and use pure timeout model).
- `recovery_valid_required`: **Provisional Policy**. Number of consecutive valid packets required to recover from `FAILSAFE` (default: `1`).
