# cyclictest baseline, Pi 5 4 GB, stock kernel 6.8.0-1064-raspi (PREEMPT_DYNAMIC)

MEASURED. cyclictest 2.50, one measured thread pinned to CPU 0, 1 ms interval, mlockall, 120 s per run,
3 runs per condition in shuffled order (seed 42), governor performance, PSU 5 V / 3 A.
Stressors on CPU 2 (and 3) per docs/research/R5.md. Values in microseconds; per-condition
P50/P99 = median of per-run values, max = max over runs. 0 of 30 runs invalid (no live or new sticky
throttle/under-voltage bits; 0.5 s power log). Thread class verified per run (sched_check.txt):
P0 measured thread TS (SCHED_OTHER), P1 measured thread FF prio 50.

| Load | P0 P50 | P0 P99 | P0 P99.9 | P0 max | P1 P50 | P1 P99 | P1 P99.9 | P1 max |
|---|---|---|---|---|---|---|---|---|
| idle | 53 | 57 | 678 | 2659 | 3 | 9 | 15 | 92 |
| cpu c2,3 | 54 | 68 | 914 | 2636 | 3 | 11 | 17 | 73 |
| stream c2 | 56 | 300 | 1573 | 3565 | 5 | 39 | 51 | 211 |
| cache 2M c2 | 54 | 203 | 1463 | 4780 | 3 | 35 | 52 | 233 |
| memrate c2,3 | 55 | 613 | 2092 | 5170 | 5 | 239 | 588 | 1094 |

Interpretation (INFERRED, to be tested):
- P0 P50 ~53 us is dominated by the default 50 us timer slack applied to SCHED_OTHER tasks
  (RT tasks get zero slack), not by scheduling delay. Do not report the P50 gap as "scheduling".
- SCHED_FIFO removes most CPU-contention tail latency (max 2.6 ms -> <0.1 ms), but memory-bandwidth
  contention on other cores still raises P1 P99 ~25x over idle (9 -> 239 us): priority does not
  isolate shared memory/cache. Matches the MemGuard/RT-Gang motivation in docs/research.
- Max values are from 3 x 120 s per cell; rare events need longer runs before claiming a bound.
