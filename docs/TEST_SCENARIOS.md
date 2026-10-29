# OS test scenarios (Pi Camera v2 + bench rig)

Refines the seed list OS-T1..T8 from the 2026-10-29 handoff. Vietnamese version for the report:
[TEST_SCENARIOS_VI.md](TEST_SCENARIOS_VI.md). Roadmap: [CAMERA_ROADMAP.md](CAMERA_ROADMAP.md).

Rules for every scenario:
- A run is VALID only if `vcgencmd get_throttled` = `0x0` before and after, the governor is
  `performance`, the SSH session is idle, and `scripts/pi/collect_metadata.sh` output is saved.
  An invalid run is kept and labelled, never deleted.
- Timestamps are subtracted only within one clock: Pi `CLOCK_MONOTONIC`, or the MCU timer.
  Cross-clock numbers need the clock-sync line (PA0) and are labelled as such.
- Evidence goes under `results/<YYYY-MM-DD>_<id>/` with the raw CSV, `meta.json`, the command
  line and a `summary.json` from the analysis script. A pass criterion is fixed **before** the run.
- Default repetitions: 3 runs per configuration, 5 min each, unless stated.

| ID | Purpose | Setup | Steps | Metric | Pass criterion | Evidence |
|---|---|---|---|---|---|---|
| OS-T1 | Camera source timing is regular and the AoI origin is valid | Pi 5 + Pi Camera v2, `hea_cam` (CAM1), no load | 1) 30 fps 640x480 for 5 min; 2) 10 fps for 5 min; 3) record `t_sensor_ns`, `t_recv_mono_ns`, BOOTTIME/MONOTONIC pair at start | frame interval mean, P99 jitter (|Δt − T|), dropped frames (sequence gaps), offset `t_recv − t_sensor` P50/P99/max | interval mean within 1 % of nominal; P99 jitter < 2 ms; drops < 0.1 %; offset > 0 and P99 < T + 10 ms; BOOTTIME − MONOTONIC constant | `results/<date>_os_t1_camera/frames.csv` |
| OS-T2 | Clean inference baseline on camera frames (replaces the invalid 0x50000 baseline) | P0 stock profile, MobileNetV2 ONNX, 1/2/4 threads, camera at 10 fps | 1) record throttle; 2) 1000 warm-up + 5000 timed inferences per thread count; 3) record throttle and SoC temperature | inference P50/P95/P99 (ms), temperature max | throttle 0x0 before and after; P99/P50 < 1.5 at the chosen thread count | `results/<date>_os_t2_infer/` |
| OS-T3 | Does the P1 profile protect the pipeline under contention? | P0 stock vs P1 (SCHED_FIFO + CPU pinning + cgroup `cpu.max` + `mlockall`); stress-ng cpu / vm / cache / io on the other cores | 1) baseline no-stress; 2) each stressor × profile, 3 runs | end-to-end camera->result latency P50/P99, deadline-miss fraction (deadline = frame period), cyclictest max (μs) | P1 P99 ≤ P0 P99 for every stressor and P1 miss fraction ≤ 1 %; any reversal is reported, not hidden | `results/<date>_os_t3_contention/` |
| OS-T4 | FIFO vs latest-value hand-off under overload (bridge and input side) | camera 30 fps, inference forced slower than the frame period (4 threads off, or stress-ng) | 1) input FIFO + bridge FIFO; 2) input latest + bridge latest; 3) mixed; 3 runs each | time-average AoI, peak AoI, deadline-miss fraction, queue length | latest-value time-average AoI < FIFO AoI in every run and FIFO queue grows without bound; else hypothesis FAIL | `results/<date>_os_t4_policy/` |
| OS-T5 | UART link: only valid frames refresh the supervisor | Pi `/dev/ttyAMA0` 921600 ↔ Nucleo OS firmware (FW1 image) | 1) 10 000 valid frames; 2) inject CRC-corrupted, truncated, wrong-version frames (`uart_tools.py`); 3) echo RTT | accepted / rejected counts per class, RTT P50/P99 on the Pi clock | 0 corrupted/truncated frames accepted; all valid frames accepted; RTT P99 < 5 ms | `results/<date>_os_t5_uart/` |
| OS-T6 | Fault -> HOLD/FAILSAFE on the LEDs, then rearm | full pipeline with camera; D4 green FRESH, D5 yellow HOLD, D6 red FAILSAFE, D9 blue link activity | faults: kill bridge, SIGSTOP inference, FIFO CPU hog, stale results with live heartbeat (F5); 10 trials each; then healthy interval -> rearm | MCU-timestamped fault-to-state time, LED state seen by the logic analyzer, rearm time | every trial reaches the expected state; reaction ≤ timer budget + 1 tick; FAILSAFE stays latched until rearm; 0 false FAILSAFE in a 30 min healthy run | `results/<date>_os_t6_faults/` + LA `.sr` files |
| OS-T7 (extra) | FreeRTOS keeps a periodic sensor task on time while the supervisor handles UART bursts | FW3 image: MPU6050 task at 200 Hz (I2C1, D10/CN7-21) | 1) idle link; 2) back-to-back valid frames at max rate; 3) corrupted-frame bursts | MPU task period jitter (MCU timer), missed samples, supervisor reaction unchanged | period P99 jitter < 100 μs and 0 missed samples in all three; OS-T6 reaction times unchanged | `results/<date>_os_t7_rtos_load/` |
| OS-T8 (extra) | Supervisor state leaves the MCU as a CAN frame (output only; bridge stays UART) | FW4 image: CAN1 sends state on change + 100 ms; CAN2 on the same board receives (loop through transceivers, 500 kbit/s) | repeat OS-T6 faults, 10 trials each | MCU time from state change to CAN2 RX interrupt, CAN error counters | every state change received; latency P99 < 1 ms; TEC/REC stay 0 | `results/<date>_os_t8_can/` |

What each result can and cannot claim:
- OS-T1/T2 are Pi-only facts; they do not show anything about the MCU.
- OS-T4 compares policies on this workload; it does not prove latest-value is always better.
- OS-T6 numbers on the MCU clock do not include Pi-side detection time unless PA0 sync is wired.
