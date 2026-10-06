# Design changes from the research pass (2026-10-06)

Each change cites the note that motivated it. Status: applied to the design docs; not yet
implemented in code unless marked.

| # | Change | Why | Source |
|---|---|---|---|
| 1 | Supervisor tracks heartbeat liveness and result freshness as two separate timers. | A live bridge can keep forwarding stale inference results; heartbeat alone misses it. | R1 |
| 2 | FAILSAFE is latched; leaving it needs an explicit rearm after a healthy interval. The skeleton's `recovery_valid_required` becomes that policy knob. | Conservative Simplex-style recovery; avoids flapping. | R1 |
| 3 | Duplicates, old sequence numbers and malformed frames never refresh any timer. | Otherwise a replaying or corrupted link looks healthy. | R1, R2 |
| 4 | E4 measures t_f (fault), t_d (decision), t_s (safe output) on one logic-analyzer clock, and reports the budget W + T + J + C + A. | Linux logs cannot time a freeze; Simplex papers report no latency numbers, so this is a gap we fill. | R1 |
| 5 | P3 = P1 on the RT kernel (was P2 on RT). P1 vs P3 isolates the kernel; P1 vs P2 isolates buffering. | The old P3 mixed two changes. | R3, R4 |
| 6 | H3 restated: P2 lowers average AoI and violation fraction, no hard bound claimed. | Queueing theory gives no deterministic bound from a small buffer. | R2 |
| 7 | E3 metrics: time-average AoI, peak AoI, V(τ), per-input deadline misses with explicit denominators, reconstructed from the age sawtooth. | Delivered-latency percentiles are not AoI. | R2 |
| 8 | Clock sync baseline = four-timestamp UART exchange (T1..T4), Linux `CLOCK_MONOTONIC_RAW` mapped to STM32 ticks with offset + rate; GPIO edge as validation. Target sub-millisecond, to be measured. | A userspace GPIO toggle is not the physical edge time; the exchange works on the existing link. | R8 |
| 9 | Protocol: ECHO_RESP carries both `mcu_rx_us` (T2) and `mcu_tx_us` (T3). **Implemented**, host tests updated. | Needed for change 8. | R8 |
| 10 | Workload = MobileNetV2 ONNX FP32, ORT CPU, intra-op 1/2/4, sequential, inter-op 1. Source period 100 ms provisional (was 30 Hz). | Published Pi 5 ORT means are 20-50 ms per inference; 30 Hz would overload by design. | R7 |
| 11 | E1 stressors: `stress-ng --stream`, `--cache` swept 256K to 8M, `--memrate` rate sweep, pinned to CPUs 2-3; inference on CPU 0, bridge on CPU 1. | Pi 5 cache layout differs from the Pi 3 used in prior work; sizes must be re-derived. | R5 |
| 12 | E2 uses SCHED_FIFO priority 50 and keeps default RT throttling (95%); no `isolcpus`, no `sched_rt_runtime_us=-1`. | Keeps the tuned profile honest and safe; the Pi 5 paper used more aggressive settings. | R3 |
| 13 | Reference repos are used for concepts only (ISR-to-task notification, RX/handler separation, measurement vs reporting split). No code copied. | Their framing has no CRC/sequence/timestamps; licenses not reviewed. | R6 |
| 14 | Corrected first-pass claims: Pi 5 ">9 ms" was SCHED_OTHER; DeepPicar slowdown 9.6x (revised) vs 11.6x (arXiv). | Accuracy. | R3, R5 |

Open: spot-check key citations against the papers themselves (R1 relies on a ResearchGate copy; R5 stressor commands are unexecuted).
