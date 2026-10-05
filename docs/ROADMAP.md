# Roadmap (PROPOSED, 2026-10-05)

About 14 working days with Claude conducting Codex workers. Each day lists the hardware it needs.
With the parked rig (Pi + Nucleo left wired on Ethernet), the hardware days run remotely.
The course deadline is not recorded yet; the plan compresses or stretches around it.

| Day | Work | Hardware |
|---|---|---|
| 1 | Merge the P0.5 skeleton (timing, workload harness, supervisor INIT/FRESH/HOLD/FAILSAFE, tests) with the protocol framing; settle one byte order; GitHub Actions CI: host tests + `arm-none-eabi-gcc` build. | None |
| 2-3 | Linux: real inference workload (small CNN via ONNX Runtime, synthetic fallback), bridge daemon (Unix socket IPC to UART), CSV logger; tested over a pseudo-terminal. STM32: FreeRTOS project for F446RE (RX task, supervisor task, status task), compiled only. | None |
| 3 | Pi bootstrap, `cyclictest` baseline of the stock kernel, first inference-latency baseline. | Pi (parked or P1 list) |
| 4 | Flash Nucleo; UART bring-up over ST-LINK VCP; heartbeat loss drives LED failsafe. | Nucleo + Mini-B (S1) |
| 5-6 | Direct Pi-STM32 UART; GPIO sync line for clock alignment; validate end-to-end AoI (Age of Information) chain, logic analyzer cross-check if available. | Pi + Nucleo + jumpers (PS1) |
| 7-9 | Experiment campaign, unattended, repeated runs: E1 baseline vs `stress-ng` (cpu, vm, cache, io); E2 `SCHED_OTHER` vs `SCHED_FIFO`, pinning, cgroup quota; E3 AoI and deadline-miss rate vs load; E4 fault injection (kill bridge, SIGSTOP, FIFO CPU hog) and failsafe latency. | PS1 rig |
| 10-11 | Analysis: P50/P95/P99, CDFs, deadline-miss tables, validity filtering (throttled runs excluded). | None |
| 12-14 | Report, slides, demo video; one final live demo run. | None, PS1 for the demo |

## What it gives WBR (INFERRED: transferable method, not transferable numbers)

The OS project is a scaled-down model of WBR's Pi-to-STM32 ownership boundary
("if the Pi fails, the robot must not immediately lose balance").

1. **Perception-health interface prototype (WBR N6/N7).** The heartbeat + freshness
   supervisor (FRESH, HOLD, FAILSAFE) and its measured detection/reaction latency are a
   first design for how the STM32H7 should treat stale or missing Pi perception output.
2. **Linux profiling method (WBR N5).** Contention generation, scheduling classes, CPU
   pinning, throttling detection and P50/P95/P99 reporting carry over to profiling
   ORB-SLAM3 on the WBR Pi. The numbers do not carry over (4 GB vs 8 GB Pi, different workload).
3. **Cross-clock timestamping.** GPIO-edge and echo-based offset/drift estimation between
   Linux `CLOCK_MONOTONIC` and an MCU timer is the same problem as aligning Pi-side
   perception time with the STM32 body-IMU time.
4. **Freshness metric.** AoI gives a concrete number for "how old is the pose the
   controller is using", which WBR needs before any perception output reaches control.
5. **Evidence tooling.** The run wrapper (metadata, validity flag, results layout) can be
   reused for WBR experiments.

Not covered: ROS 2, SLAM, camera pipelines (out of scope for the course project).
