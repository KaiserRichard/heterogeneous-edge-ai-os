# Slide content: Heterogeneous Edge-AI Runtime (progress report)

Version 2 (2026-10-06), after the research pass. One section per slide: **title**, the
**bullets** that go on the slide (short), the **image** ID, and **notes** (what you say).
Image IDs A1–D4 are in `IMAGE_PROMPTS.md`; IDs marked ★ are new or replaced, in
`IMAGE_PROMPTS_V2.md`.

---

## 1. Title
- Heterogeneous Edge-AI Runtime: Linux + FreeRTOS on Raspberry Pi 5 and STM32
- Team names, course, date
- Image: A1 (with corrected green Pi / white Nucleo)
- Notes: one sentence: "We study how a general-purpose OS and a real-time OS can share an AI workload safely, and we measure it."

## 2. Motivation
- Linux: high throughput, no timing guarantees
- Under load, results arrive late, and the delay is invisible to the receiver
- If Linux hangs, nothing on Linux can be trusted to notice
- Image: A2
- Notes: example: the Pi runs a neural network every 100 ms and sends "obstacle / no obstacle" to a microcontroller that drives a motor. A late or frozen answer is a safety problem, not just a performance one.

## 3. Problem statement
- How much does Linux resource contention delay a time-sensitive data path?
- Which stock OS mechanisms recover that delay, and which cannot?
- Can an independent real-time supervisor bound the reaction to Linux failures?
- Image: A3
- Notes: we do not write a new OS or patch the kernel; we combine and configure existing OS mechanisms and measure the effect.

## 4. Related work and our position ★
- System-Level Simplex (Bak et al., RTAS 2009): complex untrusted subsystem + simple safety subsystem on separate hardware
- Age of Information (Kaul, Yates, Gruteser, 2012): newest-first delivery keeps data freshest
- Multicore interference (MemGuard 2013, DeepPicar 2018): dedicated cores do not isolate memory bandwidth
- Pi 5 + PREEMPT_RT (arXiv 2604.19275, 2026): SCHED_FIFO worst case 1.8 ms stock vs 0.22 ms RT kernel, under stress
- **Gap we fill:** Simplex papers report no failsafe-latency numbers; we measure them end to end on commodity Linux + FreeRTOS
- Image: E1★
- Notes: sources in `docs/research/RELATED_WORK.md`. Say clearly that these are their results, not ours.

## 5. Resource contention on a multicore SoC
- 4 × Cortex-A76, 512 KB private L2 each, 2 MB shared L3, shared LPDDR4X
- CPU scheduling controls *who runs*, not *who uses memory bandwidth*
- Image: A4
- Notes: this is why we expect tuning to fix CPU contention but not memory contention (hypothesis H2).

## 6. System architecture
- Linux domain (Pi 5, Ubuntu 24.04): sensor source, inference, bridge, stressors
- Real-time domain (STM32F446RE, FreeRTOS): UART RX task, supervisor, status task, failsafe output
- One UART link + one GPIO sync line
- Image: B1
- Notes: the STM32 has final authority over the (simulated) actuator; Pi outputs are proposals.

## 7. Hardware platform
- Raspberry Pi 5 (4 GB), active cooler, 27 W PSU
- STM32 Nucleo-F446RE (Cortex-M4F, 180 MHz)
- UART: Pi GPIO14/15 ↔ STM32 PA10/PA9; GPIO17 → PA0 timer capture; shared GND
- Image: B2
- Notes: STM32 flashed from the Pi over ST-LINK, so the rig runs unattended.

## 8. End-to-end data path and freshness
- Capture → inference → buffer → UART → supervisor → action
- Age of Information (AoI): how old the newest data at the MCU is, at every instant
- Image: B3 (+ E4★ sawtooth for the AoI definition)
- Notes: AoI grows linearly between deliveries and drops at each fresh delivery. Average AoI and the fraction of time above a threshold are our freshness metrics.

## 9. Workload
- MobileNetV2 (ONNX, FP32, batch 1) on ONNX Runtime CPU
- Published Pi 5 range: about 20–50 ms per inference (1–4 threads)
- Input period 100 ms (provisional, calibrated on our Pi)
- Notes: AI is the workload, not the contribution. It is realistic, compute- and memory-heavy, and variable.

## 10. Runtime profiles ★
- P0 stock: Linux defaults
- P1 tuned: SCHED_FIFO bridge (priority 50), CPU pinning, cgroup CPU caps, locked memory
- P2 = P1 + latest-value buffer (newest result replaces unsent old one)
- P3 = P1 on the packaged Real-time Ubuntu kernel (PREEMPT_RT)
- Image: E2★ (and C1 for stock vs tuned scheduling)
- Notes: each comparison changes one thing: P0→P1 tuning, P1→P2 buffering, P1→P3 kernel.

## 11. Freshness: queue vs latest value
- FIFO queue: under overload, results wait and arrive old
- Latest value: old unsent results are dropped
- Image: C2
- Notes: theory predicts lower average age, but no hard bound; we measure how much it helps.

## 12. UART protocol
- Frame: SOF `A5 5A` | ver | type | seq | len | payload ≤ 64 B | CRC-16
- Messages: HEARTBEAT, INFERENCE, ECHO_REQ/RESP (clock sync), MCU_STATUS
- Host-tested: every single-bit error detected; 99.99 % frame recovery under random noise
- Image: C3
- Notes: the byte-wise parser runs unchanged on Linux and on the STM32.

## 13. STM32 supervisor ★
- Two independent timers: heartbeat liveness and result freshness
- INIT → FRESH → HOLD → FAILSAFE; FAILSAFE is latched until an explicit rearm
- Duplicates and corrupt frames never refresh a timer
- Highest application priority, 1 kHz, absolute release
- Image: C4★ (replaced) and E3★
- Notes: why two timers: a live bridge can keep forwarding stale results. Stale data moves FRESH to HOLD; a lost heartbeat goes straight to FAILSAFE (proposed transition table; thresholds are set after measuring inference latency).

## 14. Clock alignment ★
- Two clock domains: Linux `CLOCK_MONOTONIC_RAW` (ns) and STM32 timer (µs)
- Four-timestamp exchange over UART (T1–T4, as in NTP), offset + drift estimate
- GPIO edge + timer input capture as independent ground truth
- Image: C5★ (replaced)
- Notes: never subtract timestamps from different clocks without this mapping. Target accuracy: sub-millisecond, to be measured.

## 15. Experiments
- E1 contention impact: P0 idle vs CPU / memory-bandwidth / cache / I/O stressors
- E2 tuning and kernel: P0 vs P1, P1 vs P3
- E3 freshness: P1 vs P2 at rising load (average AoI, peak AoI, violation fraction)
- E4 fault injection: kill bridge, stop process, CPU hog; failsafe latency on STM32
- Image: D1
- Notes: every run logs temperature, frequency and throttling; throttled runs are excluded.

## 16. Fault injection and failsafe latency
- Measure fault onset t_f, decision t_d, safe output t_s on one logic-analyzer clock
- Report detection, activation and total latency separately
- Expected budget: timeout + supervisor period + dispatch delay + execution + output delay
- Image: D2
- Notes: Linux logs cannot time a freeze; that is why the STM32 and the logic analyzer observe it.

## 17. Hypotheses
- H1: contention inflates P99 far more than P50
- H2: tuning recovers CPU-contention tails, not memory-contention tails
- H3: latest-value lowers average AoI and violation time (no hard bound)
- H4: STM32 failsafe latency stays within its budget for every fault type
- Notes: these are predictions; results slides come after the experiments.

## 18. Progress and next steps
- Done: design, research pass (8 cited notes), protocol library + tests, supervisor state machine + tests (113 assertions), CI, Pi provisioning scripts
- Next: rig setup, firmware, bridge daemon, then E1–E4
- Image: D3, timeline D4
- Notes: update before presenting; see "Progress slide text" at the end of `IMAGE_PROMPTS.md`.
