# From the OS project to WBRobot and an article

Updated 2026-10-10. Intended endpoint: an academic research article. This is a work
plan, not a claim of completed experiments or publication readiness.

**A: Pi software → B: external MCU → C: physical experiments → D: WBR shadow mode
→ E: controlled robot integration → F: article.** Related-work review and methods
writing can start early; results sections wait for verified data.

## Where we actually are

| Label | Verified status | Reference |
|---|---|---|
| KNOWN | Supervisor Step 1: heartbeat liveness, result receipt silence, sequence checks, latched FAILSAFE and local rearm | 98fe2ee, merged in cf2295b |
| HOST-TEST | Noise stream matches on Mac/Pi in both char modes: 20,000/20,000 decoded, zero false accepts | bba23d0; loss proof in protocol/PROTOCOL.md |
| KNOWN | Protocol v2 carries age_at_send_us and decodes v1; supervisor still uses receipt silence | 2a06589, merged in a22fa2b |
| HOST-TEST | Protocol/supervisor tests, target object compilation and merged CI passed | [CI for a22fa2b](https://github.com/KaiserRichard/heterogeneous-edge-ai-os/actions/runs/37747548984) |
| KNOWN | Interrupted clock-sync worktree contains the T3 brief, no completed math code | feat/clock-sync at a22fa2b |
| UNKNOWN | Accepted performance baselines, full Linux pipeline, MCU firmware, physical fault latency and WBR behavior | Still required |

Stage A is incomplete. Running library tests on the Pi is software verification,
not an inference benchmark or a physical STM32 measurement. Approved slides remain
a separate artifact and are not changed by this roadmap.

## Stage A — finish everything possible without STM32

Goal: one reproducible command runs the Pi data path and produces usable raw data.
The virtual MCU is a Linux wrapper around the **real supervisor C code**.

| Order | Work | Completion gate |
|---|---|---|
| A1 | Restore access and audit interrupted work | Reach richard@192.168.50.2 and confirm dedicated OS Pi; record source/version state, power/cooling and pending work. Never substitute the WBR Pi. |
| A2 | Finish T3 clock math | Offset/delay, min-delay window, drift fit and uint32-us wrap tests pass within declared synthetic tolerances; asymmetric-delay bias documented. |
| A3 | Close rearm/restart edges | Rearm generation changes; older-generation events rejected/counted, including the same-tick case. HEARTBEAT session_id resets sequence history on bridge restart; INIT returns unless FAILSAFE remains latched pending local rearm. Compatibility/replay tests pass. |
| A4 | Add supervisor Step 2 | Source-age estimate uses Pi age-at-send, MCU-local elapsed duration and configured transit allowance; legacy absence, saturation, delayed queues and invalid data are tested. |
| A5 | Source, inference and CSV logger | MobileNetV2/ONNX Runtime plus separately labelled synthetic fallback; preserve input sequence and t_input/t_done/t_sent; record model hash, input/preprocessing, runtime and threads. |
| A6 | Bridge and virtual MCU | Unix socket → bounded FIFO/latest-value → pty → supervisor. Heartbeat/session, echo and MCU_STATUS work; end-to-end stop/restart/stale/corruption tests pass. |
| A7 | Profiles and experiment tooling | Reversible P0/P1/P2; record actual thread policy, affinity, cgroups and memory locking; runner captures failures and before/after metadata. |
| A8 | Pi campaign, analysis and thresholds | At least five independent valid repeats per condition, raw samples, summaries, CDF/AoI figures and measured threshold rationale are stored in the repo. |

Generation is local queue bookkeeping; session_id identifies a restarted sender.
They solve different problems. Latest-value replaces an unsent result; it does not
automatically cancel inference already in progress.

Use the latest approved **Pi CLOCK_MONOTONIC** consistently for t_input, t_done,
t_sent and age-at-send. Reconcile older RAW-clock notes when implementing the
sender. Never mix clock types or subtract a Pi timestamp from an MCU timestamp.

Step 2 uses:

```
source_age_estimate_us = age_at_send_us
                       + (now_MCU_us - received_at_MCU_us)
                       + transit_bound_us
```

Each difference is within one clock domain. PROVISIONAL: transit_bound_us until
the full send-to-receive path is validated. Include software queues, serialization
and clock-rate uncertainty; baud time alone is insufficient. This is an estimate
under stated assumptions, not automatically an exact AoI or proven upper bound.
Clock mapping/GPIO later provides a separate cross-check.

### Stage A measurements

| Study | Compare | Evidence |
|---|---|---|
| Timing diagnostic | Stock-kernel cyclictest, idle vs stress-ng | Raw timing evidence and kernel/governor/temperature/throttle metadata |
| Inference baseline | Intra-op threads 1–4, idle, fixed FP32 model/input | At least 1,000 timed inferences per run; P50/P95/P99/max; retain spikes, distinguish startup/warm-up |
| E1 | Idle vs cpu/vm/cache/stream stress | Service/delivery latency, CPU/RAM, drops/overflows and exact load |
| E2 preview | P0 vs P1 under matching loads | Same metrics; verify applied settings; isolate individual mechanisms with ablations if claiming their separate effects |
| E3 preview | FIFO vs latest-value under matching profile/source/load | Time-average/peak AoI, age-violation time, deadline misses, generated/delivered/replaced counts |

KNOWN requirement: at least five independent valid repeats per condition.
Declare run lengths, warm-up, source period and observation windows before comparing.
Pause all Codex workers on the Pi while measuring. Use performance governor
consistently and disclose this common control even for P0; restore the original
governor afterward. P0/P1 otherwise differ only as documented by their profiles;
P2 changes waiting-result policy relative to P1.

A run is INVALID if get_throttled is not 0x0. Missing data is UNKNOWN, not valid.
Retain failures/exclusions and their reasons. Balance/interleave condition order
to reduce warm-up and ambient-temperature confounding.

All runs use scripts/pi/run_experiment.sh and land in
`experiments/runs/<timestamp>_<name>/`: exact command/config, source commit,
model/runtime/input identity, raw samples, platform metadata and exit status.
Quiet cyclictest min/mean/max cannot supply P95/P99; use a separately specified
histogram/sample run when those quantiles are required.

Reconstruct AoI over the full time window, including no-delivery periods and the
final tail. Delivered-latency percentiles are not average AoI. Direct subtraction
in the virtual-MCU path is valid only for timestamps on the same Pi clock; modeled
independent clocks require durations or an explicit tested mapping. These are
software measurements, not hardware failsafe latency.

**A is done when:** clean source/config reproduces the pipeline and accepted runs;
analysis/figures and threshold rationale exist; CI and second-account review pass;
CONDUCTOR_STATE, LEARNING_NOTES and a Stage A report identify remaining hardware work.
No STM32, jumper wires or robot connection are required here.

## Stage B — validate an MCU independent of Linux

Goal: real F446RE supervision and a local safe output when the Pi cannot help.
This is the first stage that needs your STM32.

| Session | Work | Your physical action | Gate |
|---|---|---|---|
| B1: USB only | Flash FreeRTOS; bounded UART RX handoff, single supervisor owner, periodic task, status and safe-output pin | Nucleo-F446RE + data-capable Mini-B USB cable to the Mac | Safe startup; priorities, stack margins, release behavior and rearm/generation checked on board |
| B2: direct UART | Replace pty endpoint with physical UART using shared code | With power off, connect validated TX/RX/GND wiring | Levels/routing/console ownership, baud, errors, sequence/session and overload behavior verified |
| B3: timing | Real clock exchange, GPIO capture, decision/output instrumentation | Validated sync wire and logic analyzer/oscilloscope connections | Clock uncertainty, transit behavior and timing channels documented |

USB flashing precedes direct UART wiring. Disabling ttyAMA0's serial console needs
your approval and is not required for Stage A. Confirm PSU/cooling, board revision,
cable and instrument availability before hardware sessions. LED demonstrations or
Linux traces alone do not finish the independent physical-timing gate.

## Stage C — complete the measured OS experiment story

Goal: a defensible empirical comparison, not only a working demo.

- Repeat E1/E2 with the real link where endpoint timing matters; keep workload,
  profile, input and thermal controls matched.
- Repeat E3 at the MCU decision point; quantify age/mapping uncertainty and use
  explicit informative-delivery/deadline denominators.
- E4 injects killed/stopped bridge, stopped inference with live heartbeat,
  delayed/replayed/corrupt traffic, restart and controlled CPU starvation.
  Boot-affecting/kernel-freeze tests are not automatically authorized.
- Capture fault onset, supervisor decision and physical safe output on one timing
  instrument. Report detection, activation and total response separately.
- Revisit source period and heartbeat/result/rearm thresholds using the complete
  path. Inference P99 alone is not a safety budget; account for scheduling,
  IPC/link delay, uncertainty and acceptable false trips. Freeze thresholds before
  final comparisons. Observed maxima are not proven worst-case bounds.
- Produce the course report/demo and a claim-to-commit/config/raw-run/figure table.

**C is done when:** physical E1–E4 evidence, reproducible analysis, documented
limitations and course deliverables exist. P3/PREEMPT_RT remains optional and gated.

## Stage D — qualify the WBR boundary in shadow mode

Goal: check actual robot compatibility before granting Pi-derived data authority.
This is proposed future work requiring an explicitly approved WBR handoff. Do not
access the WBR Pi or another repository during the OS stage.

1. Inventory actual MCU/firmware, Pi/perception, links, clocks, rates and fallback.
   Earlier notes mention STM32H7 and ORB-SLAM3; current versions and interfaces
   are UNKNOWN in this workspace.
2. Review the WBR contract: message meaning/units, generation time, sequence/session,
   validity, deadlines, restart and allowed control authority.
3. Port reusable protocol/supervisor/clock code behind a WBR hardware layer. Re-test
   UART/DMA, cache/memory ownership, timer wrap and FreeRTOS scheduling. Cortex-M7
   object compilation does not qualify an H7 firmware port.
4. Shadow mode receives/judges actual perception and logs hypothetical decisions
   without actuator authority. Measure real latency, stale data, false trips and
   restart behavior; re-establish budgets rather than copying OS-rig numbers.

**D is done when:** reviewed contract/port and repeatable shadow data exist; local
balance-loop timing is checked for interference. Methods and selected code can
transfer; performance and safe thresholds need new measurements.

## Stage E — controlled WBR integration

Goal: test a defined fallback alongside validated local control. This needs your
operator presence, a test fixture and reviewed trial/abort procedures.

PROPOSED policy: Pi perception/autonomy provides bounded high-level proposals;
the MCU retains local balance/control authority. Pi loss gates those proposals and
selects a locally defined fallback. Do not transplant a generic "motors off" rule
into a balancing robot; review its actual safe behavior against the controller.

Progress from simulation/replay → constrained bench/fixture → supervised operation.
Verify normal operation before perception loss, stale inputs, bridge restart and
Pi disconnection. Record local control timing, body/tracking state, interventions,
false trips and fallback metrics; stop at predefined abort criteria.

**E is done when:** defined fallback/recovery works within the tested envelope,
with control-timing evidence. Formal stability, plant safety and trusted-component
faults remain separate claims unless explicitly analyzed and validated.

## Stage F — turn verified evidence into an article

Working question: **under Linux contention/overload, how do runtime tuning and
delivery policy affect freshness, and what does an independent MCU observe and
enforce?** A WBR article additionally needs measured effects on approved robot
control/fallback behavior.

PROVISIONAL contribution candidates: reproducible profile/load/policy comparisons,
restart/rearm-aware supervision with independent timing validation, and a measured
WBR transfer case study. These are not verified novelty. Simplex and AoI queueing
are prior work; MobileNetV2 is our OS workload, not an AI model contribution.

Formal Simplex guarantees require more than timeout logic
([Bak et al., RTSS 2014](https://stanleybak.com/papers/bak2014rtss.pdf)). Waiting-packet
replacement differs from preempting in-service work
([Kaul et al., CISS 2012](https://www.winlab.rutgers.edu/~gruteser/papers/Status%20Updates%20Through%20Queues.pdf)).
Audit the primary full texts and a related-work matrix before claiming a gap.

| Paper part | Required evidence |
|---|---|
| Problem/related work | Verified citations, comparable baselines, explicit gap and scope |
| Design/method | Reproducible ownership/fault model, clock boundaries, policies and threshold rationale |
| Evaluation | Matched conditions, valid repeat counts, run-level uncertainty, drops and failures |
| Figures | Raw-data-generated latency CDFs, profile/load comparisons, AoI/violation curves, physical fault timelines; robot metrics for WBR claims |
| Discussion | Confounders, uncertainty, exclusions, no-improvement cases and limits of generalization |
| Artifact | Tagged source/config/model/runtime, run manifest and commands regenerating tables/figures |

Write introduction/methods while building; results come only from accepted runs.
Report uncertainty across independent runs, not by treating correlated samples as
independent. After lecturer/adviser review of contribution and evidence, select a
venue and verify its current requirements. Article readiness does not guarantee
acceptance. A course demonstrator can support a technical report even if research
novelty is insufficient.

A standalone OS article can use Stage C evidence after novelty review. An article
claiming WBR integration needs D/E. Do not delay course completion for robot work.

## Ownership, gates and the immediate next step

The lead agent plans/implements/delegates, reviews diffs/logs/tests, runs the
dedicated OS Pi campaign and updates state. Each item uses feat/*: push → green CI
→ second Codex-account diff review → fixes → merge commit into
claude/project-thread-eq9yql. Preserve the dirty primary checkout; no rebase/force-push.

You handle physical connection and missing credentials. Stop for boot-affecting/P3
or serial-console changes, physical action, credentials, outside-repo work or two
failed attempts after root-cause analysis. Never touch the WBR Pi in Stage A.

Resume at **A1 → T3/A2 → A3/A4 → Linux pipeline**. You need no Nucleo now. Once A
passes, bring Nucleo/USB for B1, then jumpers/instrument for B2/B3. Set calendar dates
from demonstrated progress and equipment availability, not the earlier unverified
14-working-day estimate.
