# OS course project: stage report

Draft from retained evidence. The project now has a Linux workload and telemetry
pipeline, a shared UART protocol, and an external FreeRTOS supervisor. The evidence
shows Linux timing under contention, an upstream freshness problem, and MCU state
transitions during injected faults. FLAGGED real-UART observations now extend the reception-age pattern to STM32.
They do not establish clean physical AoI, a worst-case reaction bound, or robot safety.

This report fulfils the stage-report purpose in `docs/STAGE_PI_ONLY_BRIEF.md`,
section 2.6, using the filename requested for this ticket. It includes later
hardware evidence. `docs/SYSTEM_GUIDE.md` and `docs/ROADMAP.md` describe the plan;
their older completion markers are not used as proof of the present implementation.
The scope remains the OS mechanisms in `PROJECT.md`: scheduling, contention,
IPC, freshness, and independent supervision. Inference is a workload.

## Evidence labels and reading rules

| Label | Meaning here |
|---|---|
| MEASURED | Recorded target observations or statistics reported by the supplied measurement summaries. The environment and validity exclusions still apply. |
| FLAGGED | Retained diagnostic observations from INVALID runs; excluded from clean comparison claims. |
| CALCULATED | Arithmetic from stated configuration or retained raw observations; the calculation is described. |
| INFERRED | An explanation supported by observations, without a controlled proof of the cause. |
| ASSUMED | A configured experimental choice or provisional allowance, not a measured bound. |
| UNKNOWN | Missing evidence, an unperformed experiment, or an unresolved calibration. |

Sources: `PROJECT.md`; `docs/STAGE_PI_ONLY_BRIEF.md`; `scratch/pi-timing-tools/results/cyclictest/SUMMARY.md`; `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/README.md`; main-checkout `slides_course/REVIEW_LOG.md`, rounds 11–12. The label definitions above also follow this ticket's requested vocabulary.

Full source paths are relative to the main repository root. Bare sibling filenames
in a source list use the directory of the preceding full path; braces and globs
identify matching retained files. A label in a table caption applies to all numeric
cells unless a cell says otherwise. Version,
profile, fault, pin, and path names are identifiers. Observed maxima are not
proven bounds. Missing statistics remain UNKNOWN rather than receiving substitute
values. No experiment was rerun for this draft.

## What was built

| Part | Built behavior | OS purpose and evidence status |
|---|---|---|
| Linux pipeline | Separate source, inference, bridge, and receiver processes; Unix datagram IPC; MobileNetV2 through ONNX Runtime, with a synthetic alternative; nonblocking serial output; heartbeat and echo traffic; CSV timestamps and counters. FIFO and latest-value bridge policies are selectable. | Makes CPU service, input waiting, IPC residence, and dispatch distinguishable. MEASURED Pi operation in the software campaign; its receiver used a pty. |
| Protocol v3 | Shared small C framing/parser library, CRC-16/CCITT-FALSE, sequence checking, age-at-send, heartbeat session identity, echo exchange, extended MCU_STATUS, and optional STATE_EVENT. Legacy decoding remains version-aware. | Studies framing, integrity, restart handling, and clock domains. Hardware logs contain status, echo, and transition records. |
| Portable supervisor | Separate heartbeat liveness and result freshness; INIT/FRESH/HOLD/FAILSAFE; duplicate/old-event rejection, generation/session handling, expiry before arrivals, and latched FAILSAFE. Source age adds age-at-send, receipt elapsed time, and a configured transit allowance. | An alive bridge cannot alone make an old result fresh. Host checks support the logic; E4 records MCU transitions. |
| Board firmware | Statically allocated FreeRTOS tasks/queues, supervisor ownership, HSE bypass from ST-LINK MCO with HSI fallback, TIM2 timestamps, circular DMA UART RX with IRQ fallback, GPIO state outputs, diagnostics, and a transition ring feeding STATE_EVENT. | Separates real-time supervision from Linux and exposes reception/timing failures. DMA removes the per-byte interrupt service deadline. |
| Tooling | Offline workload bundle, build/flash/reset scripts, applied-setting and power monitors, shuffled campaigns, latency/AoI analysis, fault injection, raw logs and exclusion records. | Reproducible experiments with explicit failures and validity checks. Recorded build/tests are software verification; hardware runs have separate limitations. |

Sources: `scratch/stage-report/linux/README.md`; `scratch/stage-report/linux/inference/README.md`; `scratch/stage-report/protocol/PROTOCOL.md`; `scratch/stage-report/stm32/README.md`; `scratch/fw-rx-fix/stm32/firmware/README.md`; `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/README.md`; `scratch/fw-rx-fix/results/e4/20261012T093526Z_e4/e4_runs.csv`; main-checkout `slides_course/REVIEW_LOG.md`, round 12.

The firmware README records local cross-compilation, sanitizer checks, parser,
supervisor, DMA-cursor, pipeline and analysis tests. These are historical checks,
not tests rerun for this report. Its earlier UNVERIFIED notes describe the state
at implementation time; later smoke and E4 logs provide narrower hardware
observations, without closing every item in that README.

## Setup, run counts, and validity

| Evidence set | Exposure and accepted runs | Environment / rule |
|---|---|---|
| Cyclictest | MEASURED: 3 repeats per cell, 120 s each; 30/30 accepted. | Stock `6.8.0-1064-raspi` PREEMPT_DYNAMIC, performance governor, one locked-memory measured thread on CPU 0, 1 ms interval. Reject live or new sticky power/throttle flags; power sampled every 0.5 s. Actual measured thread class was checked. |
| Inference baseline | MEASURED: 1,000 timed calls per run after 50 warm-ups; CALCULATED from listed cells: 21/24 runs accepted, 3 excluded. | Same stock kernel, ondemand governor, affinity CPUs 0–3; CPU stress on CPUs 2–3. Reject any live `get_throttled & 0xF` sample in the 0.5 s power log. |
| E1–E3 software campaign | CALCULATED from per_run.csv: E1 15/15, E2 18/18, E3 12/12 accepted; 3 repeats per cell, ASSUMED nominal source window 60 s. | Same stock kernel, performance governor, pty receiver on the Pi; no physical UART or MCU. Require complete monitor/applied-setting evidence, successful pipeline/stressors, no live `0xF` bits and no new sticky bits. Pre-existing sticky bits alone do not exclude. |
| E3b input-policy campaign | CALCULATED from validity records: 3/12 accepted. Idle FIFO 2/3, idle latest 1/3; loaded FIFO 0/3 and loaded latest 0/3. | Software/pty. All loaded runs and the other idle runs are INVALID for live power/throttle bits. Flagged raw observations below are excluded from clean comparison summaries. |
| E3 real UART | FLAGGED: 0/18 valid; three repeats in each of six load/policy cells. | 16/18 live power flags; all nine memrate runs exceed 200 µs RMS; 14/18 have no STATE_EVENT. Empty-event rejection is a validity-rule limitation, not proof of bad freshness. |
| E4 physical faults | MEASURED: 17/25 campaign entries valid; F1/F2/F3 each 5/5; F4 2/5; the original F5 entries were unperformed. Separate F5 campaign: MEASURED 5/5. Extra F4: 5/9 accepted for short-window transitions. Combined retained attempts: CALCULATED 27/34 accepted, 7 excluded (including 3 startup failures). Original F4 2/5 plus extra 5/9 gives 7/14; acceptance scopes differ. | MCU plus Pi timestamps, no logic analyzer. Power gating plus usable clock/event records and a healthy pre-fault state; ASSUMED clock-sync residual RMS acceptance ceiling 200 µs. |
| F5 stale results, heartbeat alive | MEASURED: 5/5 retained short-window runs; SIGUSR1 inference suppression for about 1 s. No live power events or new sticky bits. | MCU/Pi state timestamps; shorter steady/observation windows than original E4, no recovery qualification. Accepted for the measured stale-result transitions, not the original 20 s steady / 10 s observation gate. |
| Hardware smoke | CALCULATED: 6 retained smoke directories, all marked excluded by their summary.json. | These summaries flag before/after throttling. Keep their link/diagnostic observations visible; do not call them clean timing runs or apply the newer live-bit rule retrospectively. |

Sources: `scratch/pi-timing-tools/results/cyclictest/SUMMARY.md`; `scratch/inference-baseline/results/20261008T085429Z_inference_livepower/SUMMARY.md`; `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/per_run.csv` and `README.md`; `scratch/e3-input-latest/results/e3b/20261012T091415Z_e3b/summary/E3B_per_run.csv`; `scratch/fw-rx-fix/results/e4/20261012T093526Z_e4/e4_runs.csv` and `campaign.json`; `scratch/fw-rx-fix/results/hw_bringup/hw_smoke*/summary.json`.

MEASURED metadata: the Pi used a **5 V / 3 A PSU**. The inference summary reports
a loaded rail of **4.66–4.92 V**, and a wall clock about **3 days** behind; monotonic
durations are unaffected. Source: `scratch/inference-baseline/results/20261008T085429Z_inference_livepower/SUMMARY.md`.
The small campaign has fewer repeats than the ASSUMED planned acceptance gate of
**5 valid repeats** per cell (`scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/README.md`).
Sampled power gating cannot prove that no short disturbance occurred between samples.

### Applied settings, rather than planned settings

| Setting | Value and label |
|---|---|
| Cyclictest policies | MEASURED: P0 measured thread SCHED_OTHER; P1 SCHED_FIFO priority 50. |
| Software campaign P1 | MEASURED: source FIFO priority 60 and bridge FIFO priority 70, both CPU 1 and memory locked; inference SCHED_OTHER on CPU 0. This differs from the guide's ASSUMED bridge-priority-50 plan. |
| Source / heartbeat | ASSUMED configured periods: 100 ms / 20 ms. Requested periods are not guaranteed under stalls. |
| Physical firmware | ASSUMED nominal clocks: HSE MCO 8 MHz, core 84 MHz, TIM2 1 MHz, FreeRTOS tick 1 kHz; USART1 921600 baud, circular DMA. |
| Supervisor thresholds | ASSUMED source configuration: heartbeat timeout 100 ms, result HOLD 200 ms, result FAILSAFE 500 ms, healthy rearm 1000 ms, transit allowance 5 ms. Calibration and safe margins are UNKNOWN. |
| Frame line time | CALCULATED: v3 INFERENCE is 35 bytes; 8N1 requires 350 bits, giving about 0.380 ms at nominal 921600 baud. Excludes every software/buffering delay. |

Sources: `scratch/pi-timing-tools/results/cyclictest/SUMMARY.md`; `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/E2_P1_B0_idle_latest_r1/settings.json`, `command.txt`, and `pipeline/config.json`; `docs/SYSTEM_GUIDE.md`; `scratch/fw-rx-fix/stm32/firmware/README.md` and `main.c`; `scratch/fw-rx-fix/stm32/src/supervisor.c`; `scratch/fw-rx-fix/protocol/PROTOCOL.md`.

The E4 captured `supervisor_thresholds.json` is empty and `e4_thresholds.json`
contains null threshold values. The threshold row above cites source configuration,
as the slide review did; it is not a populated run-time threshold snapshot.
No measured cgroup-quota benefit or packaged real-time-kernel comparison is claimed.
The summary states that P2 quotas were not done.

Reason-based threshold interpretation: MEASURED F1/F2 heartbeat FAILSAFE (reason
3) occurs 100.128–100.641 ms after the last accepted heartbeat. Their earlier
HOLD (reason 9) occurs about 175 ms after the last accepted inference, when
receipt elapsed + age-at-send + the ASSUMED 5 ms transit allowance reaches the
200 ms source-age threshold. Its roughly 98 ms heartbeat age is not heartbeat
detection. F5 reaches HOLD/FAILSAFE (reasons 9/10) at 174.950–175.917 /
474.950–475.917 ms after inference, consistent with the configured 200/500 ms
source-age thresholds. MEASURED SysTick/TIM2 self-check is -8 ppm over 1000 ms;
there is no tick-rate bug behind the earlier interpretation.

Sources: raw E4/F5 state events and F5 r5 MCU status cited in the physical-fault
section below; source configuration and age arithmetic cited above.

## Linux measurements

### Timer wake-up diagnostic

MEASURED, µs. Each cell has 3 valid repeats. P50/P99/P99.9 are per-run medians
across repeats; max is the largest observed maximum.

| Load | P0 P50 / P99 / P99.9 / max | P1 P50 / P99 / P99.9 / max |
|---|---:|---:|
| Idle | 53 / 57 / 678 / 2659 | 3 / 9 / 15 / 92 |
| CPU, CPUs 2–3 | 54 / 68 / 914 / 2636 | 3 / 11 / 17 / 73 |
| Stream, CPU 2 | 56 / 300 / 1573 / 3565 | 5 / 39 / 51 / 211 |
| Cache 2M, CPU 2 | 54 / 203 / 1463 / 4780 | 3 / 35 / 52 / 233 |
| Memrate, CPUs 2–3 | 55 / 613 / 2092 / 5170 | 5 / 239 / 588 / 1094 |

Source: `scratch/pi-timing-tools/results/cyclictest/SUMMARY.md`.

INFERRED: the P0 median includes the default timer-slack effect, so the median gap
cannot be attributed entirely to scheduler waiting. The memory-loaded FIFO tail
remains much worse than idle: priority does not isolate shared memory/cache.
This diagnostic is not inference/UART latency. P95, minimum and average are
UNKNOWN in the supplied summary; no substitutes are inserted.

### Inference workload alone

MEASURED, ms. Same timed-call exposure as the run-count table. Percentiles are
medians across valid repeats; max is the largest retained maximum. This is
synchronous inference-call time, not pipeline service latency.

| Load | ORT threads | Valid repeats | P50 | P99 | Max |
|---|---:|---:|---:|---:|---:|
| Idle | 1 | 3 | 44.0 | 48.0 | 57.0 |
| Idle | 2 | 3 | 31.1 | 42.9 | 51.8 |
| Idle | 3 | 3 | 29.4 | 38.5 | 52.8 |
| Idle | 4 | 1 | 31.4 | 70.7 | 94.1 |
| CPU, CPUs 2–3 | 1 | 3 | 45.1 | 53.7 | 65.5 |
| CPU, CPUs 2–3 | 2 | 3 | 33.2 | 46.1 | 105.5 |
| CPU, CPUs 2–3 | 3 | 3 | 45.5 | 77.6 | 91.1 |
| CPU, CPUs 2–3 | 4 | 2 | 60.3 | 100.5 | 150.3 |

Source: `scratch/inference-baseline/results/20261008T085429Z_inference_livepower/SUMMARY.md`.

MEASURED: model `mobilenetv2-12.onnx`, ONNX Runtime **1.31.0**, preprocessing P50
approximately **2.4 ms**, recorded separately in that summary. Inference P95 and
cold-start values are UNKNOWN in this summary. Unequal valid repeat counts and
the different governor prevent a direct controlled comparison with the pipeline.

### E1 contention and E2 tuning

MEASURED software/pty, ms; 3 valid repeats per row. Triples are median per-run
P50 / median per-run P99 / largest observed maximum. Service includes input
waiting and pre/postprocessing; delivery is input-to-Pi-receiver time.

| Experiment / profile | Load | Service P50 / P99 / max | Delivery P50 / P99 / max |
|---|---|---:|---:|
| E1 P0 | Idle | 44.25 / 48.28 / 56.31 | 44.37 / 48.47 / 56.47 |
| E1 P0 | Stream CPU 2 | 76.46 / 88.50 / 202.80 | 76.99 / 89.02 / 203.40 |
| E1 P0 | Memrate CPUs 2–3 | 6626 / 13980 / 15120 | 6626 / 13980 / 15120 |
| E1 P0 | Cache 2M CPU 2 | 67.58 / 97.30 / 121.60 | 68.00 / 98.83 / 121.80 |
| E1 P0 | CPU CPUs 2–3 | 45.20 / 48.13 / 80.74 | 45.41 / 48.30 / 80.98 |
| E2 P0 | Idle | 43.90 / 49.15 / 58.33 | 44.02 / 49.29 / 58.51 |
| E2 P1 | Idle | 43.94 / 48.81 / 56.24 | 44.07 / 48.98 / 56.41 |
| E2 P0 | Memrate CPUs 2–3 | 6506 / 13260 / 13410 | 6506 / 13260 / 13410 |
| E2 P1 | Memrate CPUs 2–3 | 6000 / 12890 / 14070 | 6002 / 12890 / 14070 |
| E2 P0 | Cache 2M CPU 2 | 66.36 / 73.10 / 108.80 | 66.81 / 73.57 / 109.60 |
| E2 P1 | Cache 2M CPU 2 | 69.80 / 96.58 / 135.70 | 70.19 / 97.16 / 136.10 |

Sources: `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/E1_table.csv`, `E2_table.csv`, `per_condition.csv`, and `README.md`. Scientific notation in the supplied tables is expanded here without adding precision.

INFERRED: memory traffic creates sustained upstream overload; priority helps the
small bridge's dispatch but does not remove input waiting. The measured cache
comparison does not show a blanket P1 improvement. These results do not establish
a causal memory-bus mechanism without further counters or controlled isolation.

## Freshness: the queue was in the wrong place

### E3 bridge FIFO versus latest-value

MEASURED software/pty, 3 valid repeats per row. Mean AoI uses initialized time
only, includes stalls and the final tail to the recorded window end. Before the
first informative delivery, AoI is undefined. Violation time uses strict
**>100 / >150 ms** thresholds (ASSUMED reporting thresholds). Deadline misses use
those same strict thresholds at reception; denominator is all CRC-valid inference
receptions, including shutdown drain. Missing deliveries are separate.

| Load / bridge policy | Mean / peak AoI, ms | Violation time, s | Misses >100 / >150 ms of receptions | Generated / delivered / missing | Replaced |
|---|---:|---:|---|---:|---:|
| Idle / FIFO | 94.69 / 158 | 26.85 / 0.0104 | 0 / 0 of 602 | 602 / 602 / 0 | 0 |
| Idle / latest | 94.59 / 156 | 26.79 / 0.001595 | 0 / 0 of 602 | 602 / 602 / 0 | 0 |
| Memrate / FIFO | 6660 / 13660 | 60.23 / 60.23 | 480 / 480 of 480 | 605 / 480 / 125 | 0 |
| Memrate / latest | 6958 / 14170 | 60.24 / 60.24 | 472 / 472 of 472 | 605 / 472 / 132 | 0 |

Sources: `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/E3_table.csv`, `E3_per_condition.csv`, and `README.md`. Counts/time/rates are medians per run, not pooled totals; peak is the maximum across runs. Expanded peak values retain the source table's rounding.

The bridge replaced no results under load, while input-to-completion latency grew.
MEASURED completion-interval medians were **121.72 / 125.89 / 127.99 ms** for FIFO
and **129.07 / 123.32 / 130.49 ms** for latest, versus the ASSUMED **100 ms** source
period. INFERRED: work accumulated before inference, upstream of the bridge's
latest-value slot. Multi-second service age was not multi-second model compute
time. Source: main-checkout `slides_course/REVIEW_LOG.md`, round 11, tracing to
`scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/E3_P1_B2_memrate_c23_{fifo,latest}_r*/pipeline/infer.csv`.

### E3b input latest-value fix, still power-flagged

The fix drains available source datagrams before each inference, retains the
latest valid arrival, and logs superseded inputs as `skipped_stale`. It leaves
the bridge policy at latest and compares input FIFO against input latest.
Source: `scratch/e3-input-latest/linux/inference/infer_server.py` and `README.md`.

CALCULATED from MEASURED raw software timestamps, ms: nearest-rank reception age
P50/P99 over all CRC-valid INFERENCE receptions, including drain. **Every loaded
row below is INVALID for live under-voltage/power flags.** These are diagnostic
observations, not accepted causal evidence for the improvement.

| Loaded input policy / repeat | Receptions | Age P50 | Age P99 | Inputs skipped |
|---|---:|---:|---:|---:|
| FIFO r1 | 455 | 8676.0 | 15891.0 | 0 |
| FIFO r2 | 475 | 6527.4 | 13821.6 | 0 |
| FIFO r3 | 457 | 7193.5 | 15579.1 | 0 |
| Latest r1 | 435 | 189.3 | 254.0 | 171 |
| Latest r2 | 435 | 190.3 | 256.0 | 172 |
| Latest r3 | 432 | 190.7 | 267.9 | 173 |

Sources: `scratch/e3-input-latest/results/e3b/20261012T091415Z_e3b/E3B_P1_B2_memrate_c23_{fifo,latest}_r*/pipeline/rx.csv`, `infer.csv`, and per-run `validity`; main-checkout `slides_course/REVIEW_LOG.md`, round 12. Age = `(t_rx_ns - t_input_ns) / 1e6`; nearest rank selects sorted sample `ceil(p*n)`. Skips count `status=skipped_stale`, separate from drops, replacements, and misses.

CALCULATED idle P50 spans **46.9–47.5 ms** over the raw idle records; its unequal
valid repeats are in the run-count table. No clean loaded E3b comparison exists.
The corrected policy is implemented; its benefit under clean power remains
UNKNOWN. Source: the same campaign's `E3B_P1_B0_idle_*/pipeline/rx.csv` and `validity`.

### E3 real UART / STM32 — Round 14, all FLAGGED

CALCULATED from raw `inf_rx.csv`, nearest-rank `ceil(p*n)` over all logged
receptions, including drain. `age_mcu_us` is STM32-computed source age including
the ASSUMED 5 ms transit allowance. `aoi_mapped_us` is mapped MCU receipt minus
Pi `t_input`; it is a different measurement with clock-fit uncertainty. Neither
table reports time-average held-value AoI. All 18 runs remain INVALID / FLAGGED.

| Load | Input / bridge | Repeat | Receptions | MCU age P50 / P99, ms | Mapped age P50 / P99, ms |
|---|---|---:|---:|---:|---:|
| idle | fifo / fifo | 1 | 601 | 52.685 / 72.760 | 47.854 / 68.257 |
| idle | fifo / fifo | 2 | 601 | 53.438 / 73.463 | 48.344 / 68.421 |
| idle | fifo / fifo | 3 | 601 | 53.706 / 89.010 | 48.598 / 83.632 |
| idle | fifo / latest | 1 | 602 | 52.854 / 65.607 | 47.761 / 60.752 |
| idle | fifo / latest | 2 | 602 | 52.562 / 60.748 | 47.565 / 56.194 |
| idle | fifo / latest | 3 | 601 | 54.008 / 62.271 | 49.113 / 57.275 |
| idle | latest / latest | 1 | 602 | 53.118 / 59.727 | 48.030 / 54.323 |
| idle | latest / latest | 2 | 602 | 53.083 / 60.704 | 47.964 / 55.301 |
| idle | latest / latest | 3 | 602 | 53.208 / 64.860 | 48.137 / 60.159 |
| memrate | fifo / fifo | 1 | 433 | 9412.861 / 17995.587 | 9408.471 / 17991.042 |
| memrate | fifo / fifo | 2 | 447 | 8900.786 / 16784.222 | 8895.885 / 16779.707 |
| memrate | fifo / fifo | 3 | 440 | 9405.502 / 17389.963 | 9400.958 / 17385.575 |
| memrate | fifo / latest | 1 | 429 | 9380.214 / 18520.423 | 9375.129 / 18515.654 |
| memrate | fifo / latest | 2 | 439 | 8638.846 / 17483.123 | 8633.728 / 17478.095 |
| memrate | fifo / latest | 3 | 428 | 9207.069 / 18588.409 | 9202.044 / 18583.201 |
| memrate | latest / latest | 1 | 449 | 189.510 / 253.305 | 184.895 / 248.357 |
| memrate | latest / latest | 2 | 476 | 183.432 / 260.011 | 178.599 / 255.572 |
| memrate | latest / latest | 3 | 427 | 196.503 / 254.537 | 191.875 / 249.705 |

The real-link endpoint reproduces the E3/E3b pattern: idle age is about 53 ms;
input FIFO accumulates seconds of age under memrate on CPUs 2,3 even with bridge
latest-value; input latest-value keeps reception age near the 200 ms HOLD
threshold. This is a FLAGGED observation, not a clean causal comparison.
With stale inputs, the supervisor correctly refuses data under configured
HOLD/FAILSAFE source-age thresholds of 200/500 ms. Loaded FIFO/FIFO r1 records
one FRESH→HOLD reason 9 and one HOLD→FAILSAFE reason 10; its reception states
are 1 FRESH, 4 HOLD, 428 FAILSAFE. Other loaded FIFO runs have no events and
report FAILSAFE at every reception; a new transition cannot be inferred.

Latest/latest loaded reception age is near HOLD, so occasional HOLD is expected
for a freshly armed supervisor. **It is not measured as occasional HOLD here:**
all three loaded latest/latest event files are empty and all reception states
are FAILSAFE. Reception ages strictly above 200 ms are respectively
r1: 182/449 (40.5%), r2: 156/476 (32.8%), r3: 193/427 (45.2%). These are reception-age fractions, not HOLD occupancy or transition rates.

Only four runs contain events: idle FIFO/FIFO r1 and r3, idle FIFO/latest r3,
and loaded FIFO/FIFO r1. Each logs INIT→FRESH, FRESH→HOLD (9), HOLD→FAILSAFE
(10). Idle tails must not be counted as loaded-policy HOLD. All reception/event
lost counters are zero. The other 14 runs lack transitions: the runner's
“state occupancy unknown” rejection is a validity-rule limitation because
steady FRESH can have no transitions. In these specific empty-event captures,
reception states are FAILSAFE, so absence of transitions does not prove FRESH.
No time occupancy is reconstructed from missing events.

Validity reasons overlap: live power/throttle bits in 16/18, clock-sync RMS
above 200 µs in all nine memrate runs, and missing STATE_EVENT in 14/18.
Idle FIFO/FIFO r1 also flags negative age (12 negative mapped samples, retained
in the mapped quantiles). Pi supply: 5 V / 3 A. No run is promoted to VALID.

Sources: `scratch/e3-real/results/e3_real/*_e3real/E3_REAL_P1_*/pipeline/{inf_rx,state_events}.csv`,
per-run `condition.json`, `settings.json`, and `validity`.
Reproduction: `PYTHONPATH=slides_course python3 slides_course/qa/round14_evidence.py`
from repository root. Calculated records and SHA-256 source manifest:
`slides_course/qa/round14-{computed,source-hashes}.json`.

## Physical faults: state timing, not output timing

E4 records transitions using STM32 TIM2 inside the state machine. Select the
MCU-local reference by **transition reason**, not injected fault: source-age
HOLD/FAILSAFE (9/10) uses last accepted INFERENCE; heartbeat timeout (3) uses
last accepted HEARTBEAT. Mapped durations start at Pi fault onset through the
echo estimator. These references differ. The first transition and FAILSAFE
are reported separately, even when they are the same event (six of seven accepted F4 runs).

MEASURED, ms, nearest-rank P50 / P95 / max over valid runs, rounded from µs.
P95 equals max for these small samples.

| Fault / accepted runs | First transition / reason | Local first | FAILSAFE reason | Local FAILSAFE | Mapped first | Mapped FAILSAFE |
|---|---|---:|---|---:|---:|---:|
| F1 bridge kill -9; 5/5 | FRESH→HOLD / 9 | 175.317 / 175.535 / 175.535 | 3 (heartbeat) | 100.456 / 100.641 / 100.641 | 83.342 / 83.561 / 83.561 | 85.357 / 86.209 / 86.209 |
| F2 bridge SIGSTOP; 5/5 | FRESH→HOLD / 9 | 175.206 / 175.709 / 175.709 | 3 (heartbeat) | 100.577 / 100.596 / 100.596 | 83.151 / 83.715 / 83.715 | 85.715 / 86.113 / 86.113 |
| F3 inference SIGSTOP; 5/5 | FRESH→HOLD / 9 | 175.754 / 175.815 / 175.815 | 10 (source age) | 475.754 / 475.815 / 475.815 | 83.646 / 85.914 / 85.914 | 383.620 / 385.888 / 385.888 |
| F4 FIFO-99 hog; 7/14 attempts | Six direct FAILSAFE / 3; one HOLD / 9 | 100.639 / 175.229 / 175.229 | 3 (heartbeat) | 100.556 / 100.931 / 100.931 | 85.625 / 87.871 / 87.871 | 87.277 / 97.344 / 97.344 |
| F5 SIGUSR1 inference suppression; 5/5 | FRESH→HOLD / 9 | 175.596 / 175.917 / 175.917 | 10 (source age) | 475.596 / 475.917 / 475.917 | 83.608 / 85.563 / 85.563 | 383.603 / 385.558 / 385.558 |

Sources: raw `scratch/fw-rx-fix/results/e4/20261012T093526Z_e4/F*/pipeline/state_events.csv`
and `F1-r01/capture/state_events.csv`, with run/power/echo records;
`scratch/tick-f5/results/f5/20261012T101949Z_f5/r{1,2,3,4,5}/F5-r01/pipeline/state_events.csv`,
`run.json`, and `power.csv`. Recomputed using the reason-based logic in
`scratch/tick-f5/analysis/e4_summary.py`, read-only with temporary outputs.
The older `e4_faults.csv` local first-transition references are superseded here.

ASSUMED injection duration for F2/F3/F4 was 1 s. F5 uses documented SIGUSR1
inference suppression while heartbeat continues. The new F5 captures replace
the earlier unperformed entries; they use shorter windows and do not demonstrate
legacy recovery qualification or a long-exposure false-trip rate.

CALCULATED from MEASURED F5 CSVs:

| F5 repeat | HOLD reason 9, ms after inference | Heartbeat age at HOLD, ms | FAILSAFE reason 10, ms after inference |
|---|---:|---:|---:|
| r1 | 175.917 | 18.462 | 475.917 |
| r2 | 175.343 | 18.510 | 475.343 |
| r3 | 174.950 | 17.459 | 474.950 |
| r4 | 175.596 | 18.336 | 475.596 |
| r5 | 175.767 | 18.494 | 475.767 |

F5 HOLD spans 174.950–175.917 ms after inference, with heartbeat only
17.459–18.510 ms old, hence alive. FAILSAFE spans 474.950–475.917 ms after
inference. All five power logs have no live power bits and no new sticky bits;
pre-existing sticky bits do not invalidate them.

F1/F2 HOLD reason 9 is a source-age transition about 175 ms after inference;
its roughly 98 ms heartbeat age was previously misinterpreted as heartbeat
detection. Heartbeat timeout is HOLD→FAILSAFE reason 3 at 100.128–100.641 ms
from the last accepted heartbeat, matching the configured 100 ms. Original accepted F4 records show direct FRESH→FAILSAFE reason 3. With the
new runs, six of seven accepted F4 runs go directly to FAILSAFE and one first
enters HOLD reason 9. The mixed local-first summary therefore combines two
references and must not be interpreted as a heartbeat-latency distribution.
Combined heartbeat FAILSAFE spans 100.405–100.931 ms.

Result age = receipt elapsed + age-at-send + the ASSUMED 5 ms transit allowance;
the 175/475 ms receipt durations do not redefine configured 200/500 ms source-age
thresholds. MEASURED F5 r5 `mcu_status.csv`, `tick_rate_ppm` with
`tick_window_ms=1000`, reports -8 ppm for the SysTick/TIM2 self-check. There is
**no tick-rate bug** explaining the roughly 98 ms value. This is an internal
clock check, not an independent GPIO/analyzer calibration.

The measured transitions support independent MCU supervision for these faults;
safe-pin activation delay remains UNKNOWN without an independent capture.
There is no physical actuator or independent MCU watchdog in this port.

MEASURED: all accepted runs report **0 false transitions** during the checked
pre-fault interval. Original E4 accepted-run maximum residual RMS spans **55.123–77.609 µs**; extra F4 values are listed below.
Sources: the same `e4_runs.csv`; `scratch/fw-rx-fix/stm32/firmware/README.md`.
These observations do not establish a false-trip rate or worst-case safety bound.

### Extra F4 attempts — Round 14

All nine raw power logs retain only pre-existing `0x50000`: no live bits and
no new sticky bits. Five runs pass the **short-window transition-only** checks:
complete run, power coverage without gaps above 0.75 s, clock RMS ≤200 µs,
FRESH before the steady interval, no pre-fault false transitions, zero lost
events, and observed reason-3 FAILSAFE. They do not meet the original 20 s
steady / 10 s observation / recovery protocol; the old strict summary parser
rejects their absent recovery fields. Pooling here describes transition samples,
not equal-exposure reliability or recovery performance.

| Batch / repeat | Transition acceptance | Max fit RMS, µs | HB→FAILSAFE, ms | Exclusion / sequence |
|---|---|---:|---:|---|
| 20261012T102112Z_f4/r1 | VALID | 46.951 | 100.405 | HOLD 9 then FAILSAFE 3 |
| 20261012T102112Z_f4/r2 | VALID | 85.423 | 100.533 | Direct FAILSAFE 3 |
| 20261012T102112Z_f4/r3 | VALID | 57.505 | 100.525 | Direct FAILSAFE 3 |
| 20261012T102112Z_f4/r4 | INVALID | 70.125 | Not observed | no FRESH STATE_EVENT plus clock fit before startup/recovery deadline |
| 20261012T102112Z_f4/r5 | INVALID | 71.366 | Not observed | no FRESH STATE_EVENT plus clock fit before startup/recovery deadline |
| 20261012T102112Z_f4/r6 | INVALID | 52.339 | Not observed | no FRESH STATE_EVENT plus clock fit before startup/recovery deadline |
| 20261012T105039Z_f4b/r1 | INVALID | 213.413 | 100.545 | clock RMS >200 us |
| 20261012T105039Z_f4b/r2 | VALID | 79.403 | 100.556 | Direct FAILSAFE 3 |
| 20261012T105039Z_f4b/r3 | VALID | 70.352 | 100.818 | Direct FAILSAFE 3 |

The first batch accepts 3/6 attempts; the second accepts 2/3. Extra accepted
heartbeat FAILSAFE is 100.405–100.818 ms. Original F4 2/5 plus extra 5/9 is
7/14 retained attempts (7/11 completed fault runs; 3 failed startups excluded).
The accepted first-batch r1 HOLD occurs 175.229 ms after inference, before
heartbeat FAILSAFE at 100.405 ms after heartbeat. These intervals use different
reference events. Sources: `scratch/e3-real/results/e4_f4_more/{20261012T102112Z_f4,20261012T105039Z_f4b}/r*/F4-r01/{run.json,power.csv,pipeline/state_events.csv,pipeline/echo.csv}`.

## Problems found and how they were traced

| Problem | Trace, correction, and remaining uncertainty |
|---|---|
| Cyclictest `-p 0` silently selected SCHED_FIFO | The initial incident is reported in this ticket; the supplied final summary retains the corrected campaign rather than its original erroneous numbers. Correction: explicit `--policy=other` for P0 and `--policy=fifo` for P1, plus per-thread `sched_check.txt`. MEASURED final P0 threads are TS and P1 measured threads FF. No initial misconfigured latency is reported. |
| PSU under-voltage contaminated workload comparisons | Continuous live-bit logs exposed exclusions that a sticky before/after flag alone could not attribute to a run. Use live bits and newly set sticky bits; retain exclusions. MEASURED baseline exclusions and E3b flags show why PSU metadata belongs beside every result. |
| HSI clock error | MEASURED smoke1 echo fit: 31 echoes, drift 18839.975 ppm, residual RMS 1083.883 µs. CALCULATED slope 1.01884, about 1.88% fast. Switching to HSE gives smoke6 final fit drift 89.040 ppm and RMS 39.581 µs. Echo-derived rate is not direct UART bit timing or independent clock calibration. |
| RX overrun regression | A/B retained logs: MEASURED final UART/CRC counters were smoke2 138/10; HSI smoke3 125/0; battery smoke4 99/4; old firmware smoke5 2/0. Changing clock or Pi supply did not remove the newer-firmware errors; reverting firmware largely did. INFERRED regression localization, rather than proof of one instruction's cause. Inspection found transition work inside interrupt-masked supervisor calls; the fix removes those broad masks and defaults to DMA. |
| DMA correction | MEASURED smoke6 has 0 UART/CRC errors in the nominal ASSUMED 60 s run. CALCULATED from raw status: 616 records, all split UART error counters, drops, event losses and clock-fallback flags zero. This smoke is power-flagged, so it establishes a retained link observation, not clean timing or a lossless guarantee. |
| E3 backlog upstream of replacement | Advancing inference completions arrived slower than source releases while bridge replacements stayed zero. INFERRED input queue overload. E3b adds latest-value before inference; raw observations support the mechanism, but all loaded reruns fail power validity. |
| F4 clock-sync starvation | A higher-priority FIFO hog starved the bridge. MEASURED excluded RMS maxima: 226.585 / 445.817 / 346.040 µs, exceeding the ASSUMED 200 µs gate; one also has live power flags. MCU events remain recorded, but all invalid runs are excluded from both timing summaries. The fault also disrupts its mapped-time observer. |
| Corrected transition interpretation; tick-rate issue closed | The earlier roughly 98 ms value measures heartbeat age at source-age HOLD (reason 9), not heartbeat timeout. Recompute each local interval using its event reason. F1/F2 HOLD is about 175 ms after INFERENCE; heartbeat FAILSAFE reason 3 is 100.128–100.641 ms after HEARTBEAT. Original accepted F4 is direct FAILSAFE reason 3; one extra accepted run first enters HOLD (see Round 14). MEASURED F5 r5 SysTick/TIM2 self-check: -8 ppm over a 1000 ms window (`tick_rate_ppm`, `tick_window_ms`). There is no tick-rate bug behind this value. Independent absolute clock/GPIO calibration remains pending. |

Sources: this ticket's cyclictest incident description; `scratch/pi-timing-tools/tools/timing/cyclictest_campaign.sh`, `scratch/pi-timing-tools/results/cyclictest/SUMMARY.md`, and `scratch/pi-timing-tools/results/cyclictest/20261008T091937Z_cyc_P0/B0_idle_r1/sched_check.txt`; `scratch/inference-baseline/results/20261008T085429Z_inference_livepower/SUMMARY.md`; `scratch/fw-rx-fix/results/hw_bringup/hw_smoke{1,2,3_hsi,4_batt,5_oldfw,6_dma}/mcu_status.csv`, `echo.csv`, `config.json`, and `summary.json`; `scratch/fw-rx-fix/stm32/firmware/README.md`; E3/E3b sources above; `scratch/fw-rx-fix/results/e4/20261012T093526Z_e4/e4_runs.csv`; main-checkout `slides_course/REVIEW_LOG.md`, rounds 11–13. UART/CRC pairs are cumulative counters at the final retained status, not normalized equal-duration error rates.

The RX fix also exposed a build reproducibility hazard: rapid configuration
switches could reuse objects with coarse make timestamps. Configuration changes
now force rebuilding. INFERRED hazard from static/build checks; UNKNOWN whether
any earlier measured image was affected. Source: `scratch/fw-rx-fix/stm32/firmware/README.md`.

Additional correction sources: `scratch/tick-f5/results/f5/20261012T101949Z_f5/r5/F5-r01/pipeline/mcu_status.csv`; raw E4/F5 events and power records cited above.

## Limits and transfer to WBR

| Boundary | What the present stage supports | What it does not support |
|---|---|---|
| Power and repetitions | Selected clean runs under the documented supply; flagged runs preserved. | Clean loaded E3b evidence, long-tail bounds, or broad statistical confidence from the small repeat count. |
| Software transport | Linux scheduling, IPC and freshness measurements using pty. | Physical UART serialization, MCU reception AoI, electrical reliability, or a pty-to-hardware latency equivalence. |
| Physical E3 | FLAGGED STM32 reception-age pattern across 18 invalid runs. | Clean power/clock-valid comparison, measured latest-policy HOLD occupancy, or independent held-value AoI. |
| Physical E4 | MCU-local and mapped state-transition observations. | Independently measured safe-output timing; no logic analyzer yet, no calibrated transit/rearm/false-trip margin; F5 has 5/5 shorter-window stale-result observations. |
| Firmware | External supervisor, static RTOS resources, GPIO state indication. | Proven stack margins, unrestricted DMA losslessness, automatic recovery from lost MCO, independent hardware watchdog, or actuator safety. |
| WBR method | Timestamp each stage; separate liveness from freshness; place latest-value before costly work; record actual priorities/power; use fault injection and an independent observer. | Transferring this rig's latency numbers, thresholds, baud accuracy, or safe-state definition to another workload, MCU and control loop. |
| Balancing-robot FAILSAFE | Proposed semantic boundary: reject stale Pi commands and preserve local balancing control. | Copying this demo's low GPIO outputs or stopping all motor control as the robot's safe action. Actual WBR fallback and rearm behavior require a control/interface review and measured trials. |

Sources: `PROJECT.md`; `docs/ROADMAP.md`; `docs/SYSTEM_OVERVIEW.md` (WBR fallback distinction); `scratch/e-campaign/results/e_campaign/20261008T103412Z_e_onnx/summary/README.md`; `scratch/e3-input-latest/results/e3b/20261012T091415Z_e3b/summary/E3B_per_run.csv`; `scratch/fw-rx-fix/stm32/firmware/README.md`; `scratch/fw-rx-fix/results/e4/20261012T093526Z_e4/e4_runs.csv`; main-checkout `slides_course/REVIEW_LOG.md`, round 12.

**Method transfers; numbers do not.** WBR integration remains proposed future
work. This report does not establish compatibility with its target MCU, motor
interface, real sensor workload, or control deadline, and does not authorize
access to its separate Pi (`docs/ROADMAP.md`).

## Next steps

- [ ] Restore clean power, retain supply/rail/cooling metadata, and rerun loaded
  E3b and real-UART E3; fix empty-event validity handling and confirm rearm/state initialization. Reach the planned valid-repeat gate; keep failed runs and raw data.
- [ ] Independently measure SysTick, TIM2 and state GPIO edges for absolute
  calibration; the internal -8 ppm check closes the suspected tick-rate bug.
- [ ] Capture fault onset, MCU decision and safe GPIO output on one analyzer
  clock. Cross-check echo mapping under idle, traffic, load and F4 starvation.
- [ ] Repeat matched HSE IRQ/DMA trials with exact build settings; retain ORE,
  FE/NE/PE, CRC, drops, event losses, masked-cycle maxima, stack margins and task
  release timing. Exercise continuous RX, ring wrap, split frames and restart.
- [x] Documented SIGUSR1 inference suppression preserves heartbeat; F5 is
  MEASURED 5/5, with source-age HOLD/FAILSAFE reasons 9/10.
- [ ] Extend F5 to the original long-window/recovery protocol for comparable
  exposure and false-trip/rearm assessment.
- [ ] Populate run-time threshold snapshots; calibrate transit allowance, rearm
  health and false-trip margins against workload timing. Preserve the latch.
- [ ] Run physical E1/E2, repeat FLAGGED physical E3, and obtain MCU held-value AoI with independent clock
  validation. Keep reception misses, time violations, skips and missing inputs
  separate. Extend exposure before discussing rare-event bounds.
- [ ] If evaluating quotas or packaged P3, hold workload and queue policy
  matched, record applied settings, and follow the existing system-change gate.
- [ ] Review WBR's actual interface and fallback semantics, then port and use
  shadow logging before any gated control/fault trial. Re-measure every timing
  claim on that rig.

Checklist basis: `docs/STAGE_PI_ONLY_BRIEF.md`; `docs/ROADMAP.md`;
`scratch/fw-rx-fix/stm32/firmware/README.md`; the experiment limitations and
exclusion records cited above. These are proposed checks, not completed results.
