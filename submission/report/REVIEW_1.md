# Independent report review 1

**Verdict: FAIL.** Two MAJOR and four MINOR defects; no BLOCKER build or layout defect. This verdict concerns the written report, not hardware qualification.

Reviewed against `submission/briefs/R_REPORT.md`, `submission/briefs/COMMON.md`, `PROJECT.md`, `results/README.md`, retained results and `docs/STAGE_REPORT.md`. Page references below use **PDF page numbers**, counting the cover; printed page numbers are one less.

## Verification performed

- Built from `submission/report/` with `latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=/tmp/review_R1 main.tex`. Successful 24-page PDF: `/tmp/review_R1/main.pdf`. The final log contains no LaTeX errors, overfull/underfull boxes, undefined references/citations or missing-character warnings.
- Rendered with the repository's `slides/render.swift`, with Swift/Clang caches redirected into `/tmp/review_R1`. Inspected **each of pages 1–24 individually at original 1280 × 1810 resolution**, including all tables, equations, references and appendices. No clipping, overlap, unresolved image placeholders or unreadably small text found.
- Executed the evidence generator with outputs redirected to `/tmp/review_R1/regenerated`, leaving the deliverable untouched. All 11 result tables, acquisition metadata and the 298-input SHA-256 manifest match the retained generated files byte-for-byte. Compared table numbers and narrative quantities against the stage report and retained summaries/raw records. Independently checked completion intervals, real-UART threshold fractions and reception states, E4 acceptance counts, smoke exclusions/echo fits, the F5 clock check and DMA-capacity arithmetic.
- Checked implementation/configuration assertions against protocol documentation and relevant Linux/STM32 source, and background assertions against the cited repository research notes. No target experiments, flashing or hardware qualification were performed. The only repository file written by this review is `submission/report/REVIEW_1.md`.

## Numbered defects

1. **MAJOR — PDF pp. 11 and 14 (printed pp. 10 and 13), §5.2 / §6.3, Table 8: central E3 freshness outcomes are defined but not reported.**

   The method defines time above strict 100/150 ms thresholds and reception deadline misses, yet Table 8 removes both columns. The prose supplies only approximately 60.2 s of loaded violation time. It omits the educationally important idle result: FIFO/latest spend **26.85/26.79 s above 100 ms**, despite **0/0 reception misses of 602** at the two thresholds. The retained >150 ms violation times are **0.0104/0.001595 s**; loaded misses are **480/480 of 480** and **472/472 of 472**. This evidence directly demonstrates why held-value age and delivery latency are different, a distinction introduced in the background and central to RQ2. The current presentation leaves that part of the story unsupported by displayed results.

   Evidence: `docs/STAGE_REPORT.md`, “E3 bridge FIFO versus latest-value”; `results/2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx/summary/E3_table.csv` and `summary/README.md`. Restore these outcomes in a readable table or companion table and interpret the idle contrast. Preserve MEASURED-under-v1 labels, strict thresholds, initialized-time/window rules, per-run median aggregation and reception denominators; do not convert reception misses into per-generated-input misses.

2. **MAJOR — PDF p. 24 (printed p. 23), Appendix C, Table 17: the course mapping upgrades explanations into established causes.**

   “E1/E2 demonstrate that CPU separation does not isolate memory service” assigns a specific shared-memory mechanism to experiments that measure latency under stress without causal isolation or hardware counters. “Broad interrupt masks were a receive hazard” similarly presents the suspected regression cause as settled. The main report is appropriately more cautious (“plausible receive hazard,” historical counters do not prove a unique root cause), and the stage report explicitly labels regression localization and upstream overload as **INFERRED** and says the measurements do not establish a causal memory-bus mechanism. The appendix is still part of the submitted report and must preserve those limits.

   Evidence: `docs/STAGE_REPORT.md`, “E1 contention and E2 tuning” and “Problems found and how they were traced”; report §4.3 on PDF p. 9. State the observed latency increase under cross-core stress, label its mechanism INFERRED, and describe broad masking as an inferred/plausible hazard addressed by source changes, with final hardware verification still UNKNOWN. Retain the v1 scope for E1/E2.

3. **MINOR — PDF p. 9 (printed p. 8), §4.3: DMA ring capacity arithmetic is incorrect.**

   A 2048-byte ring at nominal 921600 baud, 8N1, represents `2048 × 10 / 921600 = 0.022222… s`, or **22.22 ms**, rather than 22.19 ms. If the intended figure accounts for reserved capacity, state the usable byte count and formula. This is a CALCULATED quantity and can be corrected without a hardware claim.

   Evidence: `stm32/firmware/main.c` (`DMA_RX_SIZE = 2048`, `UART_BAUD = 921600`), plus the report's stated 8N1 assumption.

4. **MINOR — PDF pp. 11 and 14 (printed pp. 10 and 13), §5.2 and Table 9: quantile scope and metric labels are incomplete.**

   §5.2 says reported P50/P99 values are medians of per-run quantiles without limiting that statement to aggregate tables. Table 9 instead reports each individual E3b run. Its caption and column headings do not identify what P50/P99 measure: the prose says only that they are regenerated from reception/inference CSVs. Appendix A later gives nearest-rank selection, but a reader should not have to infer the endpoint from code or another table.

   Evidence: `submission/report/generate_evidence.py`, E3b extraction; `docs/STAGE_REPORT.md`, “E3b input latest-value fix, still power-flagged.” Qualify the aggregation statement and label Table 9 explicitly as per-run input-to-software-reception age `(t_rx_ns − t_input_ns)/1e6`, nearest-rank over CRC-valid inference receptions including shutdown drain. Keep every loaded row FLAGGED.

5. **MINOR — PDF pp. 13–14 (printed pp. 12–13), Tables 6–8: machine-style scientific notation hinders comparison.**

   Dense slash-separated cells mix ordinary milliseconds with strings such as `1.398e+04`, making the main multi-second backlog contrast harder to scan. There is no overflow, but this format adds unnecessary decoding effort precisely where the report asks readers to compare tails across loads and policies. The stage report expands the same rounded source values to 13980, 15120, 13660 and so forth without introducing precision.

   Evidence: retained `summary/E1_table.csv`, `E2_table.csv`, `E3_table.csv`; expanded tables in `docs/STAGE_REPORT.md`. Use consistent human-readable milliseconds, or clearly marked seconds for the large values, while preserving the source rounding.

6. **MINOR — PDF p. 23 (printed p. 22), Appendix B.2: verification commands lack a working-directory reset.**

   B.1 explicitly changes directory to `submission/report`. B.2 then lists root-level `make test`, `make firmware`, relative module targets and Python paths without returning to the repository root. Following the appendix sequentially leaves the reader in a directory without the required Makefile/paths. The distinction between host and target checks is otherwise clear.

   Evidence: `submission/report/main.tex`, Appendix B; repository root/module Makefiles and the named script locations. State “from the repository root” and supply the directory reset before B.2 commands, or make each command block independently explicit about its working directory.

## Evidence and story assessment

The displayed measured quantities otherwise agree with their cited evidence. The v1/v2 replay counts are correctly separated from fault observations; the report does not promote loaded E3b or real-UART runs to clean comparisons. E4/F5 references follow transition reasons, the 175/475 ms intervals are not mislabeled as configured source-age thresholds, and observed maxima are not presented as guarantees. Analyzer qualification and unflashed final firmware limitations remain explicit. Intentional cover placeholders comply with the brief and are not defects.

The main progression—scheduling, upstream waiting, then independent liveness/freshness decisions—serves the written course-report purpose. No section was found to require removal for a different deliverable purpose. Resolve defects 1–2 before acceptance; defects 3–6 should be corrected in the same report revision. **Final verdict: FAIL.**
