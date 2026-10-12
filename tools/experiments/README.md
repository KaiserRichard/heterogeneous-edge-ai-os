# Pi E1/E2/E3/E3B software campaign

Run from the repository root on Ubuntu ARM64 on the Pi, with the existing pipeline
requirements (`make`, Python 3, `socat`), `stress-ng`, `taskset`, `vcgencmd`, `git`,
`lscpu`, and passwordless sudo for E2/E3/E3B. No STM32 or physical UART is involved.
No system settings are permanently changed. Use a new output directory.

```sh
tools/experiments/e_campaign.sh ALL results/e-campaign-all 3 60 --stage stub
```

Estimated wall time: **about 67 minutes plus build/model-startup and metadata
collection**. ALL has 57 runs: E1 15, E2 18, E3 12, E3B 12, giving 57 measurement minutes;
39 loaded runs add 5 s stress warm-up, all 57 add 5 s cooldown and approximately
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

`E1`, `E2`, `E3`, `E3B` and `ALL` accept `[reps=3] [seconds=60]` followed by `--stage`
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
Those policies control the bridge; their inference input remains FIFO.
E3B compares **inference input FIFO/latest**, with bridge latest fixed, on idle
and B2_memrate_c23 under P1. Its four conditions run once per repetition (12 runs
with reps=3), independently of E1 ranking. To reproduce the ONNX input experiment
from the repository root on the Pi, using the documented offline bundle/venv:

```sh
PYTHON=.venv/bin/python3 bash tools/experiments/e_campaign.sh E3B results/e3b-input-latest 3 60 --stage onnx --model offline-bundle/mobilenetv2-12.onnx
```

Use the installed ONNX interpreter and model paths if they differ. The output
directory must be new. E3B uses the same scheduling, stress warm-up, shutdown
drain, cooldown and validity rules as E3; it does not claim a measured improvement
until the Pi campaign is run. `ALL` includes E3B after E3.
For the paths recorded by `results/e_campaign/20261008T103412Z_e_onnx/campaign.json`:

```sh
PYTHON=/home/richard/osbuild/venv/bin/python bash tools/experiments/e_campaign.sh E3B results/e_campaign/e3b-input-latest 3 60 --stage onnx --model /home/richard/osbuild/wheels/mobilenetv2-12.onnx
```
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
E3B adds its own CSV/LaTeX tables: input/bridge policy, time-average and peak held
AoI, reception AoI P50/P99, skipped count, >100/>150 ms deadline misses with
reception denominator, and delivered count. Conditions include `input_policy`
so the two input policies remain separate when the bridge policy is identical.
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
`--input-policy latest` drains available source datagrams before each inference,
keeping the last valid arrival. Every superseded frame is logged in `infer.csv`
with its original frame ID/timestamp and `status=skipped_stale`; `t_done_ns` is
empty (stub `work_us=0`). The inference stderr summary includes `skipped`.
Skips are counted separately from IPC drops and bridge overwrites, excluded from
completion/service samples, and remain part of the source-to-reception missing
count. FIFO is the default for both inference implementations and the runner.

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
