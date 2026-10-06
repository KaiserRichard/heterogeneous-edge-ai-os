# Related work: first pass (2026-10-06)

Status: first pass by Claude, from abstracts and summaries only. Each entry separates what
the source says (SOURCE) from what it means for us (IMPLICATION). Deeper reading is
dispatched to Codex workers (see `CODEX_TICKETS.md`). Entries marked [verify] still need
their full text read.

## 1. Architecture pattern: Simplex / System-Level Simplex
- SOURCE: Bak, Chivukula, Adekunle, Sun, Caccamo, Sha, "The System-Level Simplex Architecture
  for Improved Real-Time Embedded System Safety", IEEE RTAS 2009, pp. 99-107. A complex,
  unverified subsystem runs next to a simple safety subsystem on separate hardware. This
  protects against application faults and also against faults in the RTOS and processor of
  the complex side. Demonstrated with fault injection on an inverted pendulum.
  https://researchconnect.stonybrook.edu/en/publications/the-system-level-simplex-architecture-for-improved-real-time-embe/
- IMPLICATION: our Pi + STM32 split is a System-Level Simplex instance. This is the
  academic framing for the project: we are not inventing the pattern, we measure it on a
  commodity Linux + FreeRTOS platform. Difference: our STM32 supervises freshness and
  liveness; it does not run a full backup controller.

## 2. Freshness: Age of Information (AoI)
- SOURCE: Kaul, Yates, Gruteser, "Real-time status: How often should one update?",
  IEEE INFOCOM 2012; and "Status Updates Through Queues". LCFS (newest first) beats FCFS
  for AoI, and LCFS with preemption gives the smallest age for any utilization.
  https://www.winlab.rutgers.edu/~gruteser/papers/Status%20Updates%20Through%20Queues.pdf
- IMPLICATION: the "latest-value buffer" (profile P2) is LCFS with preemption. Theory
  predicts it bounds AoI where a FIFO queue lets age grow. E3 tests this prediction on real
  hardware instead of assuming it.

## 3. Multicore interference: CPU isolation is not enough
- SOURCE: Yun, Yao, Pellizzoni, Caccamo, Sha, "MemGuard: Memory Bandwidth Reservation System
  for Efficient Performance Isolation in Multi-core Platforms", IEEE RTAS 2013. Dedicated
  cores do not isolate memory bandwidth; per-core bandwidth regulation does.
  https://experts.illinois.edu/en/publications/memguard-memory-bandwidth-reservation-system-for-efficient-perfor/
- SOURCE: Bechtel et al., "DeepPicar: A Low-cost Deep Neural Network-based Autonomous Car",
  arXiv:1712.08644 (2018). On a Raspberry Pi 3, the CNN control loop slowed by up to 11.6x
  from shared-resource contention. Cache partitioning was ineffective; memory-bandwidth
  throttling was effective. https://arxiv.org/abs/1712.08644
- SOURCE: RT-Gang (arXiv:1903.00999): one real-time gang at a time plus throttling of
  best-effort cores. [verify authors/venue] https://arxiv.org/abs/1903.00999
- IMPLICATION: strong prior support for hypothesis H2 (tuning fixes CPU contention, not
  memory contention). Our contribution is quantifying it on the Pi 5 with an inference
  workload and an external observer. Bandwidth regulation (MemGuard-style) needs a
  kernel module, which is out of scope; we can cite it as the known remedy.

## 4. Linux timing on the Raspberry Pi 5
- SOURCE: arXiv:2604.19275 (2026), "Scheduling Analysis of UAV Flight Control Workloads on
  PREEMPT_RT Linux Using a Raspberry Pi 5". 250 Hz loop under heavy stress: stock kernel
  worst case above 9 ms, PREEMPT_RT below 225 us. Residual jitter is attributed mainly to
  memory contention. [verify authors, setup, stressors] https://arxiv.org/abs/2604.19275
- SOURCE: PREEMPT_RT is mainline since Linux 6.12 (x86, RISC-V, ARM64).
  https://phoronix.com/review/linux-612-features
- SOURCE: Canonical, "Real-time Ubuntu 24.04 LTS": optimized and tested for Raspberry Pi 4
  and 5, free for personal use on up to 5 machines via Ubuntu Pro
  (`pro enable realtime-kernel --variant=raspi`). https://ubuntu.com/blog/real-time-24-04
- IMPLICATION: our "no PREEMPT_RT" non-goal assumed it meant patching a kernel. It no
  longer does on this exact OS. Adding an RT-kernel profile (P3) is now an install
  step, not kernel work. It makes E2 much stronger: stock vs tuned vs RT kernel.
  Scope decision for the user/course.

## 5. Observing timing from outside
- SOURCE: Swami, Chougule, arXiv:2605.17701 (2026), Jetson Orin Nano. Interference can
  corrupt the timing-measurement infrastructure itself; storage-stress runs logged
  "normal" in software while external timing showed failures.
  https://arxiv.org/abs/2605.17701
- IMPLICATION: supports measuring AoI and failsafe latency on the STM32 (and with a logic
  analyzer), not only with Linux-side logs.

## 6. Linux mechanisms we rely on
- SOURCE: Linux Foundation RT wiki: defaults `sched_rt_period_us = 1000000`,
  `sched_rt_runtime_us = 950000`, so RT tasks get at most 95% of each period.
  https://wiki.linuxfoundation.org/realtime/documentation/technical_basics/sched_rt_throttling
- IMPLICATION: a runaway `SCHED_FIFO` bridge cannot fully lock the system; the "FIFO CPU
  hog" fault in E4 will hit this limit, which is itself worth reporting.

## Design changes this suggests
1. Frame the project as a System-Level Simplex instance on commodity Linux + FreeRTOS. (No code change.)
2. Justify the latest-value buffer with AoI theory (LCFS with preemption). (No code change.)
3. Make memory-bandwidth contention a first-class stressor in E1/E2, since prior work
   predicts it is where tuning fails.
4. Decision needed: add an RT-kernel profile (P3) via Real-time Ubuntu.
5. Keep the STM32 as the primary timing observer.
