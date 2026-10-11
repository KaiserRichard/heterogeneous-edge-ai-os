# Pi timing campaigns and analysis

These tools probe Linux scheduling latency for the OS project. Run campaigns on
the Raspberry Pi 5 with Ubuntu 24.04 aarch64. The Python analysis and synthetic
tests also run on macOS. No C build or third-party Python packages are needed.
Pi execution and hardware timing remain **UNKNOWN** until real campaigns run;
the committed fixture is explicitly synthetic.

## `cyclictest_campaign.sh`

**COMMAND** (from the repository root, as a regular user):

```sh
COOLER='describe installed cooling' bash tools/timing/cyclictest_campaign.sh P0 results/2026-10-11/p0 3 600
COOLER='describe installed cooling' bash tools/timing/cyclictest_campaign.sh P1 results/2026-10-11/p1 3 600
```

**PURPOSE:** compare P0 (`--policy=other -p 0`, no sudo) and P1
(`sudo -n cyclictest --policy=fifo -p 50`). Both retain the original probe's
`-m -t1 -a 0 -i 1000 -h 20000 -q`: locked memory, one thread on CPU 0,
1 ms interval, microsecond histogram bins 0 through 19999. Keeping placement,
memory locking, and stress commands constant isolates scheduling policy in this
probe. This is a cyclictest comparison, not the full application P1 profile:
it does not configure cgroup quotas or change the governor/kernel.

Arguments are profile, new output directory, repetitions (default 3), and
**measurement seconds** (default 600). Each loaded run adds 5 seconds of warm-up;
stressors have a timeout of measurement seconds + 10 to cover the probe. Every
run ends with 5 seconds of cooldown. This corrects the old script's subtraction
of 10 seconds from its duration argument. Order is shuffled with Python's local
PRNG seeded with 42 and saved in `order.txt`.

The preserved conditions are `B0_idle`, `CPU_c23` (two CPU workers on 2/3),
`B1_stream_c2` (one STREAM worker, 2M L3 size, index 0), `C1_cache2M_c2`
(one cache worker, level 3, 2M, no affinity changes), and `B2_memrate_c23`
(two unrestricted memrate workers, 64M, on 2/3). This is the original script's
subset of [R5](../../docs/research/R5.md); it does not implement its full size/rate
sweep. Stressors on separate cores study cross-core resource contention rather
than same-core CPU saturation. Exact commands are retained for interpretation.

**EXPECTED:** prerequisites `rt-tests` (`cyclictest`), `stress-ng`, `taskset`,
`vcgencmd`, `python3`, `lscpu`, Git, and sudo for P1 must already be available.
P1 authenticates once with `sudo -v`; a later expired credential is a recorded
failure, never a silent fallback. P0 still requires a sufficient existing
memlock limit for `-m`; inspect `cyclictest.err` if the installed tool refuses
unprivileged execution. No permissions or system configuration are changed.

Each `<condition>_rN/` contains:

- `meta_before.json` and `meta_after.json`: existing metadata collector fields
  (UTC, host, kernel, Git commit/dirty state, governor, CPU frequencies,
  temperature, throttle flags, load), plus profile, cooler, and exact command.
- `thermal.csv`: timestamp, millidegrees C, CPU 0 kHz, throttle flags, every
  2 seconds, with a header.
- `cyclictest_hist.txt` and `cyclictest.err`: untouched stdout and stderr.
- `cyclictest_cmd.txt`, `exit_code`, and, for loaded runs, `stress_cmd.txt`,
  `stress.log`, `stress_exit_code`.

`platform.txt` records tool versions and CPU topology. `DONE` appears only after
all commands complete successfully; failed runs retain their evidence and the
campaign exits nonzero. Existing output directories are refused. Interrupts
stop monitoring and stress processes; incomplete runs are invalid in analysis.

**DECISION:** retain every raw run. Repeat invalid runs in a new campaign
directory after resolving the recorded cause. Label actual measurements
**MEASURED** with valid run counts, kernel, cooling, governor, and profile.
Observed maxima are not WCET guarantees.

## `p0_cyclictest.sh`

**COMMAND:**

```sh
bash tools/timing/p0_cyclictest.sh results/2026-10-11/p0-legacy-entry 3 600
```

**PURPOSE:** preserve the old P0 entry point by forwarding to the generalized
campaign script.

**EXPECTED:** identical P0 artifacts and checks. The duration argument now means
measurement seconds, as described above.

**DECISION:** existing P0 callers can keep this entry point; use the generalized
script when selecting P1.

## `analysis/cyclictest_summary.py`

**COMMAND:**

```sh
python3 analysis/cyclictest_summary.py results/2026-10-11/p0
python3 analysis/cyclictest_summary.py results/2026-10-11/p1
```

**PURPOSE:** summarize direct `<condition>_rN/` children into `summary.csv`,
`summary_by_condition.csv`, and `summary_table.tex` inside the campaign directory.
The profile from metadata prefixes condition names (e.g. `P1_B0_idle`) so results
remain distinguishable. Legacy metadata without a profile is also accepted.

**EXPECTED:** Python 3.8+ stdlib only. Single-thread `cyclictest -h -q` output in
microseconds is required; multiple histogram columns are rejected rather than
silently mixed. Analysis reads raw artifacts and replaces only its three output
files. It prints run/invalid counts; a successful exit means reports were written,
not that all runs were valid.

Per-run columns contain min, average, P50, P95, P99, P99.9, max (all microseconds),
sample count, overflow count, status/reason, kernel, governor, maximum observed
temperature (both metadata and thermal samples), and observed throttle values.
Percentiles use nearest rank `ceil(p * N)` without interpolation.

The upstream [rt-tests histogram writer](https://kernel.googlesource.com/pub/scm/utils/rt-tests/rt-tests/+/refs/tags/v1.10/src/cyclictest/cyclictest.c)
prints `# Total` as the sum of in-range bins; **sample count is that sum plus
`# Histogram Overflows`**. Max always comes from `# Max Latencies`, never the last
histogram bin. Overflow cycle numbers are not latency samples. The mean is
weighted from histogram counts when there are no overflows (`avg_source=histogram`).
With overflow, it uses the printed integer `# Avg Latencies` value
(`avg_source=cyclictest_footer_truncated`); this is a truncated mean, not a
reconstructed exact mean. A percentile whose rank lies in the overflow tail is
blank, except rank N, whose value is the known maximum. A wider histogram is
needed to recover other tail values. Blanks are `--` in LaTeX.

Any nonzero throttle bit, including historical bits, in either metadata snapshot
or any thermal row marks the run **INVALID**. Headerless thermal CSV from the
original script is supported. Missing/malformed health data or histogram,
changed kernel/governor/profile, and a recorded nonzero command exit code also
invalidate the run. Metadata/thermal temperatures must be in millidegrees C.

Aggregates exclude INVALID runs and report valid `runs`, `invalid_runs`, medians
of each per-run percentile, maximum of run maxima, and maximum temperature among
valid runs. These are not pooled-sample percentiles. A median stays unknown if
any contributing valid run has that percentile unknown. Conditions with zero
valid runs remain present with blank statistics. Kernel/governor values are
listed if they differ across runs. The booktabs table has the requested columns:
condition, runs, P50, P99, max (us), kernel, governor, max temp (C), throttled.
Include it with `\usepackage{booktabs}` and `\input{.../summary_table.tex}`.

**DECISION:** inspect `summary.csv` reasons and valid run counts before quoting
results. Do not substitute maxima for unknown percentiles or include throttled
runs. A zero-valid-run condition needs replacement measurements.

## Local validation

**COMMAND:**

```sh
bash -n tools/timing/cyclictest_campaign.sh tools/timing/p0_cyclictest.sh
python3 -m py_compile analysis/cyclictest_summary.py
python3 -m unittest discover -s analysis/tests -v
```

**PURPOSE:** check shell/Python syntax and exercise synthetic histogram parsing,
validity checks, aggregates, CSV/LaTeX output, and campaign orchestration.

**EXPECTED:** tests pass on macOS and Linux without Pi tools or sudo. Campaign
tests inject fake commands and skip when run as root, because the campaign
requires a regular user. All temporary artifacts stay inside this worktree.

**DECISION:** passing these tests validates software behavior only. Real
unprivileged memlock, FIFO permissions, CPU placement, stress duration and
physical thermal behavior still need verification on the Pi.
