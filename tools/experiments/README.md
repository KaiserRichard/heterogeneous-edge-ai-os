# Pi E1/E2/E3 software campaign

Run from the repository root on Ubuntu ARM64 on the Pi, with the existing pipeline
requirements (`make`, Python 3, `socat`), `stress-ng`, `taskset`, `vcgencmd`, `git`,
`lscpu`, and passwordless sudo for E2/E3. No STM32 or physical UART is involved.
No system settings are permanently changed. Use a new output directory.

```sh
tools/experiments/e_campaign.sh ALL results/e-campaign-all 3 60 --stage stub
```

Estimated wall time: **about 53 minutes plus build/model-startup and metadata
collection**. ALL has 45 runs: E1 15, E2 18, E3 12, giving 45 measurement minutes;
33 loaded runs add 5 s stress warm-up, all 45 add 5 s cooldown and approximately
1.4 s shutdown drain. This is an estimate, not a measured Pi runtime. Default
stub work is 20 ms CPU time per frame. For an actual fixed ONNX workload:

```sh
PYTHON=/path/to/onnx/venv/bin/python3 tools/experiments/e_campaign.sh ALL results/e-campaign-onnx 3 60 --stage onnx --model /path/to/mobilenetv2-12.onnx
```

Use a compatible fixed-shape FP32 model as described in
`linux/inference/README.md`. ONNX uses one thread and the existing fixed input;
the model hash, interpreter, exact commands, stage and thread settings are kept.
ONNX startup adds model-dependent time. This campaign declares no inference
warm-up exclusion: all source/inference samples, including initial calls, are
retained. The stressor alone has a 5 s warm-up.

`E1`, `E2`, `E3` and `ALL` accept `[reps=3] [seconds=60]` followed by `--stage`
and `--model`. E2 and E3 invoked alone first perform E1 in the same new output
directory. Their rankings use valid E1 condition medians of per-run delivery
P99; ties use maximum delivery latency, then stressor name. At least two stress
conditions need a valid repetition. No ranking or timing numbers are invented
if thermal failures prevent selection. The seed is 42, separately shuffling
each experiment's complete repetition/condition matrix.

Placement and scheduling serve the OS scheduling/contention comparison: source
and bridge on CPU 1, inference on CPU 0, independent stress-ng invocations on CPU
2 and, for CPU/memrate, CPU 3. P0 is SCHED_OTHER everywhere. P1 changes only source
to FIFO 60 and bridge to FIFO 70; inference stays SCHED_OTHER. C source, bridge,
and stub inference use `mlockall(MCL_CURRENT | MCL_FUTURE)` in P1; failure is fatal.
Python ONNX inference has no memory-lock interface. The observed policy,
priority, affinity and VmLck of every process are retained in `settings.json` and
checked against the requested profile. FIFO priorities are process-local and
only those two workers enter FIFO. The pipeline is elevated as a unit to retain
consistent Unix datagram socket ownership; only its new output subtree is
returned to the invoking user's ownership on completion.

E1 uses idle, CPU_c23, B1_stream_c2, C1_cache2M_c2 and unrestricted
B2_memrate_c23 with latest-value. E2 compares P0/P1 on idle and the two worst
E1 stressors. E3 compares FIFO/latest on idle and the worst stressor under P1.
P2 is **not done**: systemd scope delegation and cgroup-v2 quotas have not been
validated on the target. No quota comparison is labeled as measured.

Each run has the existing `pipeline/` CSVs, command and before/after metadata,
plus campaign before/after snapshots, stress-ng commands/metrics, scheduling
evidence, pipeline exit status, resource samples and a 0.5 s power/thermal CSV
(`get_throttled`, PMIC EXT5V_V, sysfs temperature and CPU0 frequency). Unknown
telemetry/settings and pipeline/stressor failures are excluded. Any live bits
(mask 0xF), or newly appearing sticky bits relative to the before snapshot,
exclude the run. Previously set sticky bits alone are allowed by this ticket's
validity rule. Nothing deletes an excluded run. A finished campaign containing
exclusions returns 1; `DONE` denotes completion of the planned matrix, not
acceptance of every run. Fatal preflight/ranking failures return 2.

Regenerate analysis without sudo or load:

```sh
python3 analysis/e_summary.py results/e-campaign-all
python3 -m unittest discover -s analysis/tests
```

`summary/` contains per-run/per-condition CSVs, an excluded manifest, and E1/E2/E3
CSV and LaTeX booktabs tables with the **exact rendered deck column names**.
Use `\usepackage{booktabs}` when including the LaTeX fragments. The fragments
state MEASURED, software timestamps, pty, no physical UART, no MCU. Companion
condition CSVs and LaTeX labels identify matched loads and valid repeat counts.
Latency cells are P50/P99/max in ms: median of per-run percentiles, maximum of
per-run maxima. Companion CSVs also retain dispatch latency, reception AoI,
drop/overwrite/shutdown-discard counts, missing deliveries and repeat counts.
CPU is aggregate source/inference/bridge usage, with one core = 100%; RAM is
summed RSS, not unique physical memory. Condition counts and rates are medians
of per-run values, not pooled counts.

The source period is 100 ms. A **deadline miss is reception AoI >100 ms**;
>150 ms is also reported, with CRC-valid inference receptions as the denominator.
Missing receptions, source/inference IPC drops, queue overflows, replacements
and shutdown discards are separate counts. ONNX logs every completion and uses
nonblocking result delivery, matching the C stub's drop-on-full IPC behavior.
This keeps backpressure from silently hiding completion samples.

Held-value AoI integrates the freshest received generation timestamp over the
RAW-clock observation window, including stalls and the final tail. The interval
before the first informative delivery is undefined, not zero: its duration is
reported as `uninitialized_seconds`; the time-average denominator is explicitly
`initialized_seconds`. Age-violation time uses >100/>150 ms over that initialized
interval. Reception distributions and misses include the shutdown drain;
held-value AoI uses the recorded measurement window, excluding drain. Neither
pty timing nor software clocks establish physical UART or MCU performance.
Three repeats match this ticket's default but do not meet the deck Stage A gate
of at least five independent valid repeats.
