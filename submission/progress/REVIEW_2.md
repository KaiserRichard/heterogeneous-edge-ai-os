# Independent progress-deck review — round 2

**Verdict: FAIL — 2 MAJOR defects, 4 MINOR defects; no BLOCKER.**

Reviewed on 2026-10-13 against `submission/briefs/P_PROGRESS.md`,
`submission/briefs/COMMON.md`, the supplied repository rules and the parent
workspace's `PROJECT.md`. Page numbers below are PDF pages (1–29).

## Numbered defects

1. **MAJOR — Page 11: the real-UART rerun omits six failed startups.**
   The last bullet reports 18 live-power flags, three clock flags and one
   setting failure, but leaves out **six pipeline failures**. In
   `results/2026-10-12_e3_real_uart_rerun/20261012T160628Z_e3real2/summary/per_run.csv`,
   six rows also report `pipeline failed` and missing `pipeline/window_start_ns`.
   Their individual `pipeline.log` files all contain
   `TimeoutError: no FRESH STATE_EVENT before startup deadline`: loaded input
   FIFO / bridge FIFO r1–r3 and input FIFO / bridge latest r1–r3.
   The printed counts are correct, but this is a materially incomplete account
   of why the campaign failed. These attempts never opened the intended
   measurement window; an owner following the current story could expect a PSU
   replacement alone to address the rerun. Add the six startup failures, retain
   overlapping exclusions, distinguish attempts from completed windows, and
   connect this evidence to the startup/rearm pilot gate on pages 25 and 29.
   Do not infer the root cause of the missing FRESH event from these logs alone.

2. **MAJOR — Page 19: physical campaign commands depend on an undocumented external helper.**
   Both exact commands require
   `/home/richard/osbuild/rearm_via_mac.sh`. No implementation of that helper is
   retained in this checkout. `tools/experiments/README.md` says the runner does
   not create the user's rearm procedure; the deliverable's README merely says
   the helper must exist. Naming this dependency does not explain how to restore
   it after a fresh deployment. This prevents reproducible execution of a core
   next step, particularly because the Pi runs the campaign while the Mac owns
   ST-LINK. Supply an owner-facing setup procedure or documented helper template
   with the Mac destination, reset command, required connection setup and an
   observable success check. Label unconfirmed deployment values UNKNOWN.
   Keep a failed reset fatal; do not substitute `true` for rearm verification.

3. **MINOR — Pages 14 and 16: provisioning lacks its network prerequisite.**
   Page 14 assumes no Pi internet; page 16 then presents
   `sudo bash scripts/pi/bootstrap.sh` without explaining that this is an
   online provisioning command. The script unconditionally runs `apt-get update`
   and package installation before configuring UART. It will not provision the
   described isolated Pi without reachable package sources. Mark the command
   as initial provisioning requiring package-network access, or give an offline
   provisioning alternative and a dependency audit for the already provisioned
   rig. Git bundles and Python wheels alone do not satisfy its apt dependencies.

4. **MINOR — Page 23: measured timing examples lack explicit evidence labels.**
   The approximately 175 ms, 100 ms and earlier 98 ms examples are consistent
   with `docs/STAGE_REPORT.md`, “Physical faults” and “Problems found,” and their
   reference events are correctly distinguished. However, the numeric bullet
   has no MEASURED label or inherited result caption. Add MEASURED and scope the
   examples to the retained accepted fault observations. Retain the warning that
   these are different reference intervals; do not present them as configured
   thresholds or worst-case bounds. Label the proposed supply change PLANNED
   separately from the recorded 5 V / 3 A setup.

5. **MINOR — Page 20: firmware artifact path is incomplete.**
   The flash description says `firmware/build/firmware.elf`. From the repository
   root, `scripts/stm32/flash.sh` actually verifies and programs
   `stm32/firmware/build/firmware.elf`. Correct the path in the slide and command
   companion so the owner can locate the exact artifact to hash and flash.
   The shell invocation itself is correct.

6. **MINOR — Page 28: the requested Obsidian M-lesson lookup remains incomplete.**
   Checked long-deck page references and learning-plan module numbers are useful,
   but they do not identify the Obsidian M-lessons required by P_PROGRESS.md.
   UNKNOWN is the honest label for unavailable external filenames, so this is
   a missing handoff item, not a fabricated-evidence finding. Add an explicit
   pending owner lookup and completion gate for the mechanism-to-M-lesson index;
   populate it only from supplied or authorized notes. Do not search unrelated
   personal directories to close this item.

## Build and full-page inspection

From `submission/progress/`, built the supplied source without regeneration:

```sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=/tmp/review_P2 main.tex
```

Exit **0**, **29 pages**, PDF `/tmp/review_P2/main.pdf`. The final log has no
matches for `Overfull|Underfull|Missing character|undefined|^!`.

The initial required Swift renderer encountered a sandbox compiler-cache error.
Redirecting its caches allowed it to complete:

```sh
CLANG_MODULE_CACHE_PATH=/tmp/review_P2/clang-cache SWIFT_MODULECACHE_PATH=/tmp/review_P2/swift-cache swift /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/render.swift /tmp/review_P2/main.pdf /tmp/review_P2/preview
```

The supplied Objective-C PDFKit fallback was also compiled and run entirely in
`/tmp/review_P2`. Inspected **every page, 1–29**, individually at original image
resolution, 1280 pixels wide. No visible overflow, clipping, overlapping text,
missing glyphs, placeholders or unreadably small body text was found. Figure 1
is captioned and explained. Page 19 is dense but readable; wrapped commands have
copyable counterparts in `TOOL_CATALOG.md`.

Story flow serves the owner: orientation → history/status → evidence → rig/tools
→ pitfalls → gates → WBR connection/study → first-session checklist. No slide
was found to serve an unrelated deliverable purpose. The major defects concern
the completeness of the failure story and the ability to execute its next steps.

## Evidence and claim audit

Checked every displayed numerical assertion and substantive claim against the
results inventory, stage report and relevant retained summaries/logs; checked
implementation, configuration, CLI and historical identifiers against repository
documentation, scripts and read-only git history. Exceptions and incomplete
claims are numbered above. In particular:

- Pages 7–10: historical PTY acceptance **45/45**, split **15/18/12**, versus
  v2 replay **0/45**; cyclictest **30 runs**, **15/15 per profile** under v1,
  **3/15 per profile** under v2, **six idle runs**, **120 s**, **five loads**,
  **two profiles**, **three repeats**; baseline **21/24**, three excluded
  four-thread runs; initial inference **22/24 excluded**; E3b **3/12 accepted**,
  six loaded and three idle exclusions. These match the inventory and summaries.
  Direct CSV recount confirmed PTY and E3b totals. Missing v2 evidence is correctly
  described as a qualification limit rather than proof of malfunction.
- Pages 11–13: original real-UART E3 **0/18**, overlapping **16/9/14** flags;
  **seven** excluded smokes, smoke6's zero UART/CRC counters and nominal **60 s**;
  separate rerun **0/18** MCU-local and mapped acceptance, **18/3/1** stated
  flags; original E4 **25 planned / 20 performed / 17 accepted**, F1–F3 **5/5**,
  F4 **2/5**; extra F4 **5/9**, three startup failures and one RMS exclusion;
  separate F5 **5/5**; analyzer **16 attempts / 15 captures**, incomplete F1-r05
  and separate channel check. Counts agree; the rerun's additional six failures
  are defect 1. Restricted F4/F5 exposure, analyzer qualifications and report
  chronology are preserved. No FLAGGED collection is promoted to a clean result.
- Pages 3–6 and 14–27: dated commits/integration, the **11** review-fix categories,
  configured pins/USART/baud, recorded access address and management/data-link
  separation agree with the cited history and documentation. The **1.5 s** monitor
  gap, **5 s** fit-age rule, declared **200 µs** RMS ceiling and planned **five**
  valid repeats agree with the validity note and roadmap. Firmware fixes remain
  explicitly compiled/host-tested rather than flashed/rig-verified. PR numbers
  and status are attributed to the supplied brief snapshot, not independently
  verified current remote state.
- Pages 16–21: inspected CLI definitions and output paths rather than executing
  provisioning, flashing or physical experiments. The companion includes all
  production `.sh`/`.py` entry points and the eight regression-test scripts under
  `tools/`, `scripts/` and `analysis/`. Defects 2, 3 and 5 qualify usability.
- Page 28: long-deck pages **9–16** and **82** match its actual frame/section
  sequence, including generated section dividers; page 82 is “Inference baseline:
  CPU contention.” Learning-plan module numbers match the named mechanisms.
  External M-lesson identities remain UNKNOWN, as stated.

No new measurement, independent clock calibration or hardware verification was
performed. Only `submission/progress/REVIEW_2.md` was written in the repository;
build/render artifacts were placed under `/tmp/review_P2`.
