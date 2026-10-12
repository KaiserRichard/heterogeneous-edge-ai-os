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

# E4 real UART fault campaign

Run on the Raspberry Pi 5 with the STM32 attached. This runner and its analysis
are locally tested with synthetic fixtures; the real campaign remains **UNVERIFIED
ON HARDWARE**. No measurement results are included here.

Use the bridge/firmware from `feat/hw-fixes`: `hea_bridge` must decode
`STATE_EVENT` into `state_events.csv` with exactly these columns:

```text
seq,t_rx_pi_ns,mcu_us,old,new,reason,last_hb_mcu_us,last_inf_mcu_us,lost_count,t_mcu_pi_est_ns
```

The runner starts the bridge with its working directory set to each pipeline
directory, so its default `state_events.csv` lands there. If that branch exposes
an explicit filename option instead, pass, for example,
`--state-events-option=--state-events-csv` using the option it actually implements.
The runner requires the existing `--serial-fd` bridge option. Missing CSV/schema
or a failure to reach FRESH aborts before injecting a fault. This ticket does not
implement any firmware or bridge protocol changes.

From the repository root, the exact default run command is:

```bash
tools/experiments/e4_campaign.sh results/e4-real-001 5
```

The directory must be new. Defaults: `/dev/ttyAMA0`, 921600 baud, bridge CPU 2,
controller/source/inference CPU 0, synthetic inference work 20000 CPU us, source
period 100 ms, heartbeat period 20 ms, latest policy, echo period 500 ms. The
controller and monitor run away from the hog core so they can resume children,
observe power state, and bound cleanup. This affinity choice isolates the OS
scheduling fault to the bridge's core, as required by the experiment.

Each repetition executes four faults. Five repetitions reserve at least **10.7
minutes** for steady/observation/recovery-fit windows; allow about **34 minutes**
for startup, rearm and timeout allowances, plus the initial build. Actual runtime
depends on reset/startup time; the campaign prints its command and estimate before
running. A failed readiness check ends the campaign early. Preview without
hardware, sudo, builds or creating output:

```bash
tools/experiments/e4_campaign.sh results/e4-real-001 5 --estimate-only
```

Requirements are the existing Pi build tools and Python standard library,
`vcgencmd`, UART permissions, and `sudo` with `CAP_SYS_NICE` privileges for F4.
The runner calls `sudo -v` once up front and `sudo -n` for each hog. Each hog
self-terminates after one second measured on CLOCK_MONOTONIC_RAW; it makes no
system configuration changes. Linux's existing RT bandwidth limit still applies;
the campaign does not disable it.

The default local rearm command is `bash scripts/stm32/reset.sh`, which uses
OpenOCD/ST-LINK to reset the board. The current port latches FAILSAFE and has no
remote or automatic rearm. To use an already implemented local rearm procedure,
pass `--rearm-command 'COMMAND ARG ...'` or set `HEA_E4_REARM`. This is an argv
string parsed with `shlex`, run from the repository root, with a 15 s timeout;
shell expressions require an explicit `bash -c ...`. Reset must retain UART
connectivity. This runner makes no new rearm protocol.

Before each fault the board is rearmed/reset and a new pipeline must report FRESH
and a usable echo fit. It must remain continuously FRESH for 20 seconds: even
brief exits detected between polls abort the run. Then:

| Fault | Action | Fault end |
| --- | --- | --- |
| F1 | SIGKILL bridge; passive UART capture for 10 s | Start of restore/rearm after capture decoding |
| F2 | SIGSTOP bridge for 1 s, then SIGCONT | Immediately before SIGCONT |
| F3 | SIGSTOP inference for 1 s, then SIGCONT | Immediately before SIGCONT |
| F4 | sudo SCHED_FIFO 99 busy loop on the pinned bridge CPU for 1 s | End of the busy loop |
| F5 | SIGUSR1 bridge: suppress INFERENCE for 1 s; HEARTBEAT and ECHO continue | Acknowledged second SIGUSR1 resumes INFERENCE |

For F2–F5 the 10 s observation window starts at onset and includes the one second
fault. The onset clock read is immediately before the signal or the hog loop,
with no intervening file I/O. The hog records its own actual start/end. After
observation, stop the pipeline, rearm/reset, and start a fresh pipeline; retain
recovery events until FRESH and two further echo periods. Startup/recovery waits
default to 15 s (`--ready-timeout`). Cleanup resumes stopped children, terminates
and reaps all owned processes. F5 uses `pipeline/bridge_control.csv` acknowledgements
for effective onset/end (CLOCK_MONOTONIC_RAW); run metadata also records the
controller request times. A partially written INFERENCE finishes; the CSV records
its remaining bytes. Detection is timed from the last accepted inference in
STATE_EVENT, including any such in-flight frame. No queued results are replayed
on resume. F5 hardware behavior is **UNVERIFIED ON HARDWARE**. F3 tests a bounded
inference stall while the bridge continues its independent heartbeats.

F1 needs reception while its decoder is dead. A second descriptor keeps the real
tty open across SIGKILL. After reaping the killed bridge, the controller becomes
the only reader, saves `capture/uart.bin` and original chunk receipt times, and
never transmits on the UART. After observation, it feeds these bytes into the
same bridge decoder over an isolated socketpair; all decoder-generated TX is
discarded. The pipeline's latest pre-fault echo fit maps captured MCU events.
`capture/state_events.csv` receipt/mapping fields belong to replay and are **not**
used as physical arrival/onset times. Original byte arrival times remain in
`capture/chunks.csv`. There is no extra relay in the live bridge path and no
duplicate implementation of STATE_EVENT framing. Byte loss or a frame partially
consumed inside the killed bridge is a hardware verification concern: the summary
checks the event chain and reported `lost_count`; these cannot prove absence of
all UART/driver losses. Verify F1 transitions and capture completeness on the rig.

The power/thermal monitor samples at 0.5 s throughout each executed run, recording
RAW Pi time, `get_throttled`, temperature and all four CPU frequencies. INVALID:
any live bits 0–3, sticky bits 16–19 newly set relative to that run's initial
sample, unavailable monitor data, a gap over 0.75 s, uncovered measurement windows,
clock fit unavailable, residual RMS over `--rms-bound-us` (default 200 us), any
STATE_EVENT `lost_count > 0`, event state/time discontinuity, interrupted/failed
run, or failure of the prescribed steady/observation windows. Preexisting sticky
bits alone do not invalidate a new run.

Analysis writes `e4_runs.csv`, `e4_faults.csv`, `e4_faults.tex`, and
`e4_thresholds.json` in the campaign directory:

```bash
python3 analysis/e4_summary.py results/e4-real-001 --thresholds supervisor.json --rms-bound-us 200
```

The campaign saves the resolved configured values in `supervisor_thresholds.json`
and their original source in `campaign.json`. Reanalysis with no options uses
that snapshot and the campaign's saved RMS bound. Explicit analysis options
override those saved settings.

All latency columns are microseconds. Detection is the first FRESH exit within
observation, using `t_mcu_pi_est_ns` from the estimator, minus onset. Missing mappings
are reconstructed with the logged inverse affine echo estimator. Startup events
can use the first fit from that same MCU epoch. F1 replay uses the latest original
fit. Reset/restart has a separate `recovery/echo.csv` and MCU epoch; never subtract
MCU timestamps across reset. MCU-local detection/FAILSAFE metrics subtract
`last_hb_mcu_us` for heartbeat-timeout reasons and `last_inf_mcu_us` for result
timeout/HOLD reasons, recorded in `detection_reference` / `failsafe_reference`.
The legacy `local_reference` column names the injected fault's intended timer. These
measure elapsed time since the last accepted packet, rather than elapsed time
since the Pi signal. FAILSAFE Pi latency uses onset as its reference. Recovery
uses the first return to FRESH after fault end, including the prescribed wait
until local rearm; for F1 it includes restore/reset/startup. A fault with no
observed exit has no recovery latency. False transitions count all state changes
inside the 20 s steady phase.

No detected transition, no FAILSAFE, or no recovery is reported as censored with
blank values, never as zero. Per-fault distributions use only VALID runs and
nonmissing samples, nearest-rank P50/P95/max, with separate run and sample counts
and counts of INVALID/NOT_DONE. Reports carry the label **MEASURED (MCU timestamps
+ Pi timestamps, no logic analyzer)**. Synthetic tests are not campaign results.

Thresholds are read from literal `*_US` macros in `stm32/include/*.h` (optional
`SUPERVISOR_`/`HEA_` prefix), or the JSON passed through `--thresholds`:

```json
{
  "heartbeat_timeout_us": 100000,
  "result_hold_us": 200000,
  "result_failsafe_us": 500000,
  "rearm_healthy_us": 1000000,
  "transit_bound_us": 5000
}
```

Those example values are the **provisional configured constants** in this
worktree's `stm32/firmware/main.c`, not measurements; supply the values actually
flashed on your rig. The present `stm32/include` declares fields but contains no
numeric defaults, so omission of JSON leaves comparisons UNKNOWN. The runner
does not guess them. Keep the supplied configuration as campaign evidence.
Table comparisons select the threshold from the actual transition reason. A HOLD
can precede heartbeat FAILSAFE during F1/F2; comparing that first FRESH exit with
100 ms heartbeat timeout creates a false early-timeout diagnosis. Mixed reasons
are not pooled into a single threshold comparison. Source-age HOLD/FAILSAFE
labels show `threshold - age_at_send_us - transit_bound_us`; their raw receipt
elapsed time is not compared numerically with the full source-age threshold.
Inspect the recorded transition reasons: source age, last-packet phase, and the
supervisor evaluation period affect agreement. Source-age expiry includes the
last result's age-at-send plus transit allowance, so receipt-silence time alone
need not equal the source-age threshold. Pi onset and reset recovery latencies
have no direct supervisor timeout equivalent; their comparison cells say so.
The reset recovery used here bypasses healthy-interval rearm and therefore does
not test `rearm_healthy_us`.

Local tests, without sudo or hardware:

```bash
python3 -m unittest discover -s analysis/tests -v
bash -n tools/experiments/e4_campaign.sh
python3 -m py_compile tools/experiments/e4_campaign.py analysis/e4_summary.py
```

# E3 freshness at the STM32, real UART

The new runner measures accepted inference receipt with INF_RX from the updated
firmware; no PTY receiver is used. Code is locally verified with synthetic data
and a fake MCU over openpty; physical verification remains outstanding. Run on
the Pi after separately flashing the HSE+DMA firmware. This development task
does not flash, reset, open UART hardware or run load on the rig.

Exact command using the existing campaign's installed ONNX paths:

```bash
PYTHON=/home/richard/osbuild/venv/bin/python bash tools/experiments/e3_real.sh results/e3-real-001 3 60 --model /home/richard/osbuild/wheels/mobilenetv2-12.onnx --rearm-command 'bash /home/richard/osbuild/rearm_via_mac.sh'
```

Output must be new. Arguments are `<new-outdir> [reps=3] [seconds=60] --model PATH`.
`PYTHON` selects ONNX as in `e_campaign`; one inference thread, source period
100 ms. Default rearm is `bash $HOME/osbuild/rearm_via_mac.sh`, parsed as argv
with shlex, executed before **every** run with a 15 s timeout, and retained in
`rearm.log`. FAILSAFE is latched, so each run requires successful rearm/reset.
The script does not create or change the user's rearm procedure.

There are 18 runs by default: B0_idle and B2_memrate_c23 crossed with
input FIFO / bridge FIFO, input FIFO / bridge latest, input latest / bridge
latest, each repeated three times. Whole matrix shuffle seed is 42. All runs
use P1: source CPU1 FIFO60, bridge CPU1 FIFO70, inference CPU0 SCHED_OTHER;
source/bridge mlock, stress-ng memrate pinned independently to CPUs2 and3.
Serial is `/dev/ttyAMA0`, 921600 baud; echo period 100 ms supports a fit near
each report. Stress warmup is 5 s on loaded runs; cooldown is 5 s per run.

Wall-time estimate: **18 minutes of measured windows; budget about 27 minutes
plus initial build and model startup** (90 s per run including startup/rearm,
drain, metadata and cooldown allowances). Runtime depends on the existing rearm
procedure and ONNX startup. The runner prints the command and estimate.

Validity includes the existing E campaign process/settings checks, a 0.5 s
power monitor covering the measurement window (no gap >0.75 s), no live power
bits, no new sticky bits, echo fit RMS <=200 us, no INF_RX loss, and no
STATE_EVENT losses/discontinuities. Preexisting sticky bits are allowed. Counts
and accepted-delivery age quantiles include shutdown drain; state occupancy is
clipped to the source observation window. Missing MCU reports remain separate
as bridge_unreported, rather than silently counting them as delivered.

```bash
python3 analysis/e3_real_summary.py results/e3-real-001
```

`summary/per_run.{csv,tex}` and `summary/per_condition.{csv,tex}` report mapped
receipt AoI P50/P99/max and MCU-computed age P50/P99/max in microseconds, strict
>100/>150 ms miss counts/rates, delivered/skipped/overwritten counts, and seconds
in INIT/FRESH/HOLD/FAILSAFE from STATE_EVENT. Valid condition distributions pool
accepted deliveries; counts/times sum across valid repetitions. Invalid runs
stay in per_run with their reasons and are excluded from condition aggregation.
Tables use **MEASURED (real UART, MCU timestamps)** to identify the measurement
method, not to claim the development host has produced physical measurements.
Mapped AoI and MCU age have different definitions: MCU age includes the delay
from receipt to supervisor evaluation and a provisional 5 ms transit allowance.
See `protocol/PROTOCOL.md` for exact INF_RX layout and offline mapping policy.

Local validation (no hardware):

```bash
make -C protocol test
make -C stm32 test
make -C linux test
make -C stm32/firmware all
python3 -m unittest discover -s analysis/tests -v
bash -n tools/experiments/e3_real.sh scripts/pi/run_pipeline.sh
```
