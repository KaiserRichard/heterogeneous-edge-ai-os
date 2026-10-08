# Autonomous brief: finish the Pi-only stage (no STM32)

Paste to ChatGPT Work as one task. It should run to completion without asking, except at the
gates in section 4.

---

You own the whole **Pi-only stage** of `heterogeneous-edge-ai-os` and work autonomously until
every item in section 2 meets its Definition of Done, or you hit a gate in section 4. Do not ask
me for routine decisions: the decisions in section 3 are pre-approved. You have the Mac checkout,
Codex accounts and SSH to the Pi (`richard@192.168.50.2`); use them. Follow `AGENTS.md`,
`PROJECT.md`, `docs/SYSTEM_GUIDE.md` and the evidence labels (KNOWN / MEASURED / CALCULATED /
SOURCE / ASSUMED / UNKNOWN). Never invent data. Host/Pi software verification is not hardware
timing of the STM32 — label it so.

## 1. Working rules
- One feature branch per item, from `claude/project-thread-eq9yql`; small commits; push; open a
  draft PR per item; let CI run; fix until green. **You may merge a PR into
  `claude/project-thread-eq9yql` yourself when CI is green and its DoD is met**; never into `main`.
- Never reset or overwrite the primary Mac checkout; work in separate worktrees (as you did in
  `scratch/`). Leave my uncommitted `prompts/` changes untouched.
- Reproducibility: every measurement run writes raw data + metadata (commit, `uname -r`,
  governor, `vcgencmd measure_temp`, `vcgencmd get_throttled`, cooler, date, exact command) into
  `results/<date>/<run-id>/`. Throttled runs are flagged and excluded from summaries.
- After each item, append a short entry to `docs/obsidian/2026-10-08-pi5-phase.md` (tick the
  checkbox, add result + commit) so I can follow progress in Obsidian.

## 2. Work items and Definition of Done (in this order; 2.3–2.5 may run in parallel)

2.1 **Close supervisor v2 step 1** (`feat/supervisor-v2`, commit 98fe2ee):
- replace `rand()` in the noise test with a fixed-seed in-house PRNG; Mac and Pi give identical
  counts; still zero false accepts;
- add a `generation` counter (rearm increments; events from an old generation rejected and
  counted) with the "queued before rearm, delivered after, same tick" test;
- add `session_id` handling (section 3c) with tests;
- DoD: tests pass on Mac + Pi with sanitizers, Cortex-M4 compile passes, CI green, merged.

2.2 **Protocol: `age_at_send` field** (section 3b), with versioned decoding and tests in
`protocol/`; update the supervisor adapter to use it for freshness
`age_MCU = age_at_send + (now_MCU − rx_MCU) + TRANSIT_BOUND` (TRANSIT_BOUND a config value,
DESIGN, documented as to be measured). DoD: protocol + supervisor tests green on Mac + Pi, CI
green, docs updated, merged.

2.3 **Clock-sync math** (`feat/clock-sync`, pure C): offset/delay from T1–T4, min-delay filter,
linear drift fit; host tests with synthetic clocks (known offset, drift ppm, jitter, asymmetric
delay case documented as a known bias). DoD: recovers synthetic parameters within stated
tolerances, CI green, merged.

2.4 **Pi timing baseline** (`tools/` scripts + `results/`):
- metadata-logging script; `cyclictest` with sudo (pre-approved), idle 10 min and loaded with
  stress-ng profiles from `docs/research/R5.md` (CPU, `--stream`, `--cache`, `--memrate`);
- profiles P0 (stock) and P1 (SCHED_FIFO 50, pinning, cgroups, mlockall);
- summary table P50/P95/P99/max per configuration, labelled MEASURED with run counts.
DoD: scripts committed, raw data + summary committed, every run has metadata.

2.5 **Inference baseline + Linux pipeline:**
- ONNX Runtime + MobileNetV2 on the Pi (fixed model, input, threads); measure cold start,
  preprocessing and inference separately; keep all samples; P50/P95/P99/max;
- `source` (100 ms, `CLOCK_MONOTONIC_RAW`, absolute `clock_nanosleep`), `inference`, `bridge`
  (Unix domain socket in, `hea_proto` frames out, FIFO vs latest-value, heartbeat 20 ms), logger
  CSV with `t_input, t_done, t_send, t_rx`;
- UART stand-in: a `socat` pty pair (no system config change needed); receiver on the same Pi
  clock;
- run E1 (P0 idle vs stressors), E2 (P0 vs P1), E3 partial (P1 vs P2, AoI at the receiver).
DoD: code with unit tests, runs reproducible from one script, results + summary committed,
limitations stated (no MCU, no physical UART).

2.6 **Stage report** `docs/STAGE_PI_ONLY_REPORT.md`: what was built, every number with its label
and run count, what is still UNKNOWN until the STM32 arrives, and the ready-to-run hardware
checklist for the next stage.

## 3. Pre-approved decisions
a) Supervisor: two timers, latched FAILSAFE, local rearm after `REARM_HEALTHY_MS` (500 ms
   DESIGN), one global uint16 wire sequence, time regression → reject + count, thresholds in a
   config struct, expiry evaluated before arrivals.
b) `age_at_send`: uint32 µs, `t_send − t_input` on the Pi `CLOCK_MONOTONIC_RAW`; bump the
   protocol version; the decoder accepts the old version (field absent → fall back to receipt
   silence, flagged) and the new one; tests for both.
c) Session: HEARTBEAT carries a random 32-bit `session_id` chosen at bridge start; a new
   `session_id` resets sequence watermarks and returns to INIT unless in FAILSAFE; FAILSAFE still
   requires local rearm.
d) Stressors and run lengths: follow `docs/research/R5.md`; at least 3 repetitions per
   configuration; exclude throttled runs.
e) Installing user-space packages on the Pi (`rt-tests`, `stress-ng`, `socat`, Python/ONNX
   Runtime in a venv) and running measurement commands with sudo: approved.

## 4. Gates — stop and ask me only for these
1. Any change to system configuration of the Pi: boot files (`/boot/firmware/*`), disabling the
   serial console, kernel install (P3 / Real-time Ubuntu), reboot.
2. Anything touching `main`, force-push, deleting branches or files you did not create.
3. A result that contradicts a hypothesis or the design in a way that changes the plan.
4. Anything needing physical action (wiring, STM32, logic analyzer).
When blocked by a gate, continue with the other items and batch your questions into one message.

## 5. Final report to me
One message: per item — status, branch/PR/merge commit, evidence (commands, test counts, CI),
measured numbers with labels; open gates/questions; what I must do next (with COMMAND / PURPOSE /
EXPECTED / DECISION).

---
