# Where this project sits in WBR, and the path to the Damiao STM32H7

Status: PROPOSED (2026-10-05). Labels follow the WBR evidence convention:
SOURCE-SUPPORTED / MEASURED / INFERRED / ASSUMED / UNKNOWN.

## 1. The WBR stack and the slice this project builds

```
 WBR robot (long term)                         This OS project (now)
 -----------------------------------------     ------------------------------------
 L5 Autonomy / planning (Pi)                   -
 L4 Perception: D435i, ORB-SLAM3, ROS 2 (Pi)   stand-in: inference workload on Pi 5 4 GB
 L3 Pi <-> MCU boundary: link, protocol,       BUILT HERE: framed UART protocol,
    timestamps, freshness, health              clock alignment, AoI, heartbeat
 L2 Hard real-time control (STM32H7):          BUILT HERE (supervisor part only):
    balance LQR/VMC, FSM, body IMU, safety     FRESH/HOLD/FAILSAFE supervisor on FreeRTOS
 L1 Motors/drivers (Damiao, CAN)               -
```

The project builds L3 and the supervisor part of L2, and it characterizes the
Linux runtime under L4. In WBR gate terms:
- **N5 (profiling):** the measurement method (contention, scheduling class, pinning,
  throttling-aware validity, P50/P95/P99) is reused for ORB-SLAM3 on the WBR Pi.
- **N6 (perception-health interface):** the heartbeat + freshness supervisor is the
  first concrete design of "how the MCU decides Pi output is stale or dead".
- **N7 (integration boundary):** protocol, timestamp alignment and failsafe-latency
  numbers become the interface contract between the Pi and the H7.

What does not transfer: the numbers themselves (4 GB vs 8 GB Pi, a synthetic workload
vs ORB-SLAM3, F446 vs H7). The methods, code and contract transfer.

## 2. F446RE now, Damiao H7 later: what changes

The Damiao controller board is ASSUMED to use an STM32H723 (Cortex-M7, up to 550 MHz).
Confirm the exact part number printed on the chip before planning the port.

| Part | Change on H7 | Why |
|---|---|---|
| `protocol/` framing + CRC | None | Pure C99, no HAL, works on any byte stream. |
| Supervisor state machine | None | Pure C, time is passed in; no hardware access. |
| Linux side (bridge, logger, experiments) | None | Only the link endpoint changes. |
| Clock alignment math | None | Only the timer used for timestamps changes. |
| UART/DMA driver | Rewrite in the port layer | H7 has a D-cache: DMA buffers must sit in non-cacheable RAM (MPU) or be cleaned/invalidated, and DMA cannot reach DTCM. The classic H7 porting bug. |
| Clock tree, pins, timer | Rewrite in the port layer | Different board, different free UART and capture pins. |
| FreeRTOS port | Switch to the ARM_CM7 port | Check the core revision; early CM7 parts need the r0p1 port. |
| Failsafe action | Redesign | F446: LED and a status flag. WBR: ignore Pi setpoints, keep balancing in place. Losing the Pi must never cause loss of balance. |
| Task priorities | Redesign | On the F446 the supervisor owns the MCU. On the WBR H7 it is a low-priority guest beside the balance loop and must have a bounded, measured CPU cost. |
| Transport | Possibly | The Damiao board may expose a different UART, or only USB CDC. The protocol does not care; USB adds polling latency that must be measured again. |

INFERRED conclusion: roughly 70-80% of the code moves unchanged. The work that
remains is a port layer plus a priority and failsafe design inside your brother's
control firmware. That design is the real integration work, and it is about
coordination more than code.

## 3. Rules applied from day 1 so the port stays cheap

1. **Port layer.** All hardware access goes through `stm32/port/<board>/`
   (`port_uart_*`, `port_time_us()`, `port_gpio_*`). Protocol and supervisor code never
   include STM32 headers.
2. **CI builds for both cores.** Cortex-M4F (F446) and Cortex-M7 (H7) compile on every
   push, so nothing F446-specific leaks into portable code.
3. **Supervisor CPU budget is measured.** Worst-case execution time of the RX parser and
   the supervisor tick goes into the results, because the WBR H7 has to fit them next
   to the control loop.
4. **Failsafe as a policy hook.** The supervisor outputs a state (FRESH/HOLD/FAILSAFE);
   what each state does is board code. The F446 lights an LED; WBR maps it to
   "hold position, ignore Pi commands".

## 4. Working without the H7

- Everything in this project runs on the F446RE at home.
- Optional: a Nucleo-H723ZG at home would rehearse the H7 port (cache, DMA, CM7 FreeRTOS)
  without borrowing the lab board. Only worth it if the Damiao chip is confirmed H723.
- The lab H7 is needed only at WBR integration time: one bring-up session for the port,
  then sessions coordinated with whoever owns the motor firmware.

## 5. Open questions for WBR integration (not blocking this project)

- Exact MCU part number on the Damiao board. (UNKNOWN)
- Does the lower-level motor firmware use FreeRTOS, and at what control-loop rate? (UNKNOWN)
- Which UART or USB port on that board is free for the Pi link? (UNKNOWN)
