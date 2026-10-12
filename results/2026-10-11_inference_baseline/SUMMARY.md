# Inference baseline, MobileNetV2 (mobilenetv2-12.onnx), ONNX Runtime 1.31.0, Pi 5 4 GB

MEASURED. 1000 timed runs per cell after 50 warm-up runs; inference time only (preprocessing ~2.4 ms P50 separately).
Kernel 6.8.0-1064-raspi, governor ondemand (not performance), inference unpinned (affinity 0-3), stress-ng --cpu 2 pinned to CPUs 2,3.
Validity: a run is excluded if the live get_throttled bits (0xF) were ever set in the 0.5 s power log during it (power.csv).
PSU: 5 V / 3 A, rail 4.66-4.92 V under load. Pi clock is ~3 days behind (no NTP); time differences unaffected.

| Condition | Threads | Valid reps | P50 (ms, median) | P99 (ms, median) | Max (ms) |
|---|---|---|---|---|---|
| idle | 1 | 3 | 44.0 | 48.0 | 57.0 |
| idle | 2 | 3 | 31.1 | 42.9 | 51.8 |
| idle | 3 | 3 | 29.4 | 38.5 | 52.8 |
| idle | 4 | 1 | 31.4 | 70.7 | 94.1 |
| cpu stress c2,3 | 1 | 3 | 45.1 | 53.7 | 65.5 |
| cpu stress c2,3 | 2 | 3 | 33.2 | 46.1 | 105.5 |
| cpu stress c2,3 | 3 | 3 | 45.5 | 77.6 | 91.1 |
| cpu stress c2,3 | 4 | 2 | 60.3 | 100.5 | 150.3 |

Excluded: idle_r1/threads-4, idle_r3/threads-4, cpu23_r3/threads-4 (live under-voltage).
