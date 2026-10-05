# Linux Workload Module

## Purpose
Provides a lightweight, portable compute workload and timing harness for benchmarking iteration latency and evaluating OS scheduling/contention effects before integrating heavy AI frameworks.

## Components
- `include/timing.h`, `src/timing.c`: Monotonic clock abstraction using POSIX `clock_gettime(CLOCK_MONOTONIC)`.
- `include/workload.h`, `src/workload.c`: Configurable synthetic arithmetic workload, warmup handling, and CSV telemetry output.
- `src/main.c`: Standalone CLI runner (`workload_runner`).

## CSV Output Schema
```csv
sequence_id,workload_start_ns,workload_end_ns,latency_ns,valid
```

## Running
```bash
./build/workload_runner -n 100 -w 10 -i 500 -o output.csv
```
