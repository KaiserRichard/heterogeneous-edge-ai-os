# Research tickets for Codex workers

Rules for every ticket: read full texts (not only abstracts), cite exact sections, separate
SOURCE from IMPLICATION, mark anything unread as [unverified], write the output to
`docs/research/<ticket-id>.md`, and do not change code. Max ~2 pages per output.

| ID | Question | Output |
|---|---|---|
| R1 | System-Level Simplex (RTAS 2009) and follow-ups: decision logic, fault model, how failsafe latency was measured. What should our supervisor copy? | Supervisor design recommendations |
| R2 | AoI with LCFS/preemption: what metrics (average AoI, peak AoI, violation probability) suit a periodic sensor + variable inference service? | Metric definitions for E3 |
| R3 | Read arXiv:2604.19275 fully: Pi 5 setup, stressors, cyclictest/rtla method, results. What can we reuse directly? | Method checklist for E1/E2 |
| R4 | Real-time Ubuntu 24.04 on Pi 5: install steps, kernel version, known issues, interaction with `cpufreq`/thermal. | P3 profile setup notes |
| R5 | DeepPicar, RT-Gang, MemGuard: which stress-ng options reproduce memory-bandwidth and cache contention on Cortex-A76? | Stressor profiles for E1 |
| R6 | Reference repos in `third_party/` (4 submodules): what to reuse for UART framing, FreeRTOS task layout, gateway logging. | Reuse table with file paths |
| R7 | ONNX Runtime on Pi 5 (arm64): model choice (MobileNetV2/V3, SqueezeNet), threads, expected latency range from published benchmarks. | Workload spec |
| R8 | Clock alignment Linux and MCU: GPIO-edge vs round-trip echo; expected accuracy; prior embedded examples. | Sync method spec |
