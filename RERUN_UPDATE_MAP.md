# Re-run update map — 2026-10-20

This is a read-only source audit, not a new measurement or a document rebuild. Paths and line numbers refer to this worktree before any re-run integration. Only this file was written. No hardware commands were run. The re-run directories were not yet present when inspected; new values below are deliberately left pending. `PROJECT.md:5`–`PROJECT.md:11` defines the OS experiment objective.

## Reading the map

The following abbreviations expand to exact repository-relative directories. A suffix after an abbreviation is relative to that directory; braces/globs identify every matching file, not a selected example.

| ID | Original results directory | Acquisition date / scope |
|---|---|---|
| C0 | `results/2026-10-11_cyclictest/20261008T091937Z_cyc_P0` | 2026-10-11; OTHER timer |
| C1 | `results/2026-10-11_cyclictest/20261008T091937Z_cyc_P1` | 2026-10-11; FIFO-50 timer |
| I | `results/2026-10-11_inference_baseline` | 2026-10-11; standalone inference |
| E | `results/2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx` | 2026-10-11; ONNX, PTY |
| B | `results/2026-10-12_e3b_input_latest/20261012T091415Z_e3b` | 2026-10-12; input-policy PTY |
| U | `results/2026-10-12_e3_real_uart/20261012T105039Z_e3real` | 2026-10-12; original physical E3 |
| U2 | `results/2026-10-12_e3_real_uart_rerun/20261012T160628Z_e3real2` | 2026-10-12; later physical E3 diagnostic re-run |
| F | `results/2026-10-12_e4_faults/20261012T093526Z_e4` | 2026-10-12; original full E4 |
| X | `results/2026-10-12_f4_extra/{20261012T102112Z_f4,20261012T105039Z_f4b}` | 2026-10-12; extra short-window F4 |
| S | `results/2026-10-12_f5_stale/20261012T101949Z_f5` | 2026-10-12; short-window F5 |
| L | `results/2026-10-12_logic_analyzer` | 2026-10-12; analyzer captures |

Folder dates are acquisition dates. October 8 inner timestamps reflect a Pi wall clock about three days behind (`results/README.md:5`–`results/README.md:8`), not a different October 8 baseline. The deck's 2026-10-13 cover is an evidence snapshot date (`submission/defense/main.tex:16`). Label historical observations **original (2026-10-11)** or **original (2026-10-12)**, as appropriate.

Historical v1 summaries must remain byte-for-byte intact. Current v2 replay accepts only 6/30 timer runs and 0/45 E1–E3 runs because additional evidence was not recorded; this is not retrospective proof those runs malfunctioned (`results/README.md:35`–`results/README.md:48`). Commands below are recipes for later use, not commands executed in this audit.

## 1. Defense deck: every measured plot, table and numeric statement

`submission/defense/main.tex` contains seven measured plots, two included E4 tables, and hand-authored summary/configuration tables. `submission/defense/build_evidence.py:26` writes plots; `:137` writes E4 tables; `:189`–`:191` write the capture key, computed records and source hashes. It does not generate `main.tex` prose or its inline tables.

| Location | What is shown, including numbers repeated in prose | Results input and computation | Producer / regeneration recipe |
|---|---|---|---|
| `submission/defense/main.tex:134`–`:136` | Method: timer 3×120 s/cell; E1–E3 3×60 s/cell; inference 50 warm-ups + 1,000 calls; 15 analyzer captures; governors | C0/C1 per-run `cyclictest_cmd.txt`, `meta_before.json`, `meta_after.json`, `thermal.csv`; I `*/threads-*/bench/summary.json`; E `campaign.json`, `E*/condition.json`, `E*/pipeline/config.json`; L `*/la_e4.csv`. Stored method also in `results/2026-10-11_cyclictest/SUMMARY.md:3`, I `SUMMARY.md:3`–`:6`, E `summary/README.md` | Hand-authored; evidence builder records selected settings/load files at `:51`–`:56`. Use R1/R2/R4/R5 below and inspect metadata; do not replace durations globally. |
| `submission/defense/main.tex:141`–`:150` | v1/v2 table: cyclic 30/30 vs 6/30; PTY 45/45 vs 0/45; original E4 17/25 unchanged; fit age ≤5 s | `results/README.md:41`–`:48`; C0/C1 `summary.csv`, E `summary/per_run.csv`, F `e4_runs.csv` are stored v1 counts. v2 numbers are documented replay outcomes, not a second retained summary directory | Inline table, no automatic producer. R1/R2/R4 produce separate v2 outputs; preserve stored v1. |
| `submission/defense/main.tex:156` | Figure 5, `images/cyclic.pdf`: median per-run P99, P0/P1 across idle, CPU, stream, cache, memrate. P0 = 57,68,300,203,613 µs; P1 = 9,11,39,35,239 µs. Prose repeats 9→239 | C0/C1 `summary_by_condition.csv:2`–`:6`, column `p99_us`; display order differs from CSV order. Raw: each `<load>_r*/cyclictest_hist.txt`, metadata, `thermal.csv`, `sched_check.txt`, `stress_cmd.txt`, `stress_exit_code` | `build_evidence.py:28`–`:39`; `analysis/cyclictest_summary.py:122`, `:218`–`:235`, `:254`–`:291`. R1 + R6. |
| `submission/defense/main.tex:163`–`:164` | Figure 6, `images/inference.pdf`: P99 by 1–4 ORT threads. Idle 48,42.9,38.5,70.7 ms; loaded 53.7,46.1,77.6,100.5 ms. 21/24 accepted; repeats idle 3/3/3/1, loaded 3/3/3/2; three 4-thread exclusions | I `SUMMARY.md:8`–`:19` is the direct plot input. Underlying `idle_r{1,2,3}/threads-{1,2,3,4}/bench/{samples.csv,summary.json}` and `cpu23_r{1,2,3}/threads-{1,2,3,4}/bench/{samples.csv,summary.json}`; I `power.csv`, per-thread metadata/logs | `build_evidence.py:40`–`:50` plots the retained Markdown; `linux/inference/infer_bench.py:48`–`:63` produces per-run summaries; `bench_common.py:15`–`:31` uses interpolated quantiles. No retained cross-run Markdown aggregator identified. R7 explains limits; not rerun by today's ONNX pipeline campaign. |
| `submission/defense/main.tex:169`–`:171` | Figure 7, `images/E1.pdf`: delivery P99 = 48.47,89.02,13980,98.83,48.3 ms (idle, stream, memrate, cache, CPU); stored 15/15, v2 0/15 | E `summary/E1_table.csv:2`–`:6`, slash component 2 of `Delivery latency`; numeric identities in `E1_per_condition.csv`; raw `E1*/pipeline/{source.csv,infer.csv,bridge.csv,rx.csv}` | `build_evidence.py:57`–`:68`; `analysis/e_summary.py:122`–`:171`, `:175`–`:225`, `:251`–`:293`; `pipeline_summary.py:136`–`:140`. R2 + R6. |
| `submission/defense/main.tex:176`–`:178` | Figure 8, `images/E2.pdf`: delivery P99 P0 idle/mem/cache = 49.29/13260/73.57; P1 = 48.98/12890/97.16 ms; stored 18/18, v2 0/18 | E `summary/E2_table.csv:2`–`:7`; identities in `E2_per_condition.csv`; same raw pipeline files under `E2*` | Same plot loop and analysis as E1. R2 + R6. Join profile **and load**, not row number. |
| `submission/defense/main.tex:183`–`:186` | Figure 9, `images/E3.pdf`: initialized mean AoI idle FIFO/latest 94.69/94.59; memrate FIFO/latest 6660/6958 ms; 12/12 stored, v2 0/12. Zero bridge replacements; 100 ms input period; completion intervals approximately 122–130 ms | E `summary/E3_table.csv:2`–`:5`, `Time-average AoI` and `Replaced count`; `E3_per_condition.csv`; loaded `E3_P1_B2_memrate_c23_{fifo,latest}_r*/pipeline/infer.csv`. Completion medians are 121.72/125.89/127.99 and 129.07/123.32/130.49 ms (`docs/STAGE_REPORT.md:216`–`:222`). The rounded deck range conceals 121.72 and 130.49 endpoints | Plot loop `:57`–`:68`; held AoI integral `e_summary.py:80`–`:119`, window handling `:151`–`:162`, aggregation `:175`–`:190`. R2 + R6; R8 for intervals. |
| `submission/defense/main.tex:185` | E3b diagnostic reception P99 latest 254–268 ms vs FIFO 13.8–15.9 s; all six loaded runs power-invalid | B `E3B_P1_B2_memrate_c23_{fifo,latest}_r*/pipeline/{rx.csv,infer.csv}`, validity/thermal records; `summary/E3B_per_run.csv`; exact per-run values in `docs/STAGE_REPORT.md:236`–`:243`: FIFO 15891.0/13821.6/15579.1; latest 254.0/256.0/267.9 ms | **Not generated by defense builder.** Raw diagnostic extraction example: `submission/report/generate_evidence.py:46`–`:55` (different LaTeX report, not the Vietnamese builder). R2 for accepted new E3B; R8 for diagnostics. |
| `submission/defense/main.tex:191`–`:193` | Figure 10, `images/E4.pdf`: every accepted first/safe transition, colored by reason; about 175/475 ms from inference receipt. F1/F2/F3/F5 five accepted each; F4 7/14, with six first HB reason-3 and one HOLD reason-9 | F `e4_runs.csv`, each performed `F*/run.json`, `pipeline/state_events.csv`, plus F1 `capture/state_events.csv`; X/S `r*/F{4,5}-r01/{run.json,power.csv,pipeline/echo.csv,pipeline/state_events.csv}`. Combined 27/34; original F5 NOT_DONE entries excluded from 34. Reason 3 subtracts `last_hb_mcu_us`; reasons 9/10 subtract `last_inf_mcu_us` | `build_evidence.py:73`–`:123`, `:124`–`:137`; retained acceptance F vs locally checked extra scopes at `:90`–`:104`. R4 + R6; do not pool today's full campaign with old short runs. Appendix A lists all plotted runs. |
| `submission/defense/main.tex:202`–`:204` | Figure 11, `images/LA.pdf`: Δ=(last UART byte end→both GPIO low)−(last accepted HB→FAILSAFE event). 10/15 final HEARTBEAT references +47.5–67.6 µs; remaining 5 different final frames. 8 MHz; no absolute calibration | L `{check_F2,run_F1,run_F2,run_F4}/la_e4.csv`; each row's `<capture>/capture.vcd`, `<capture>/pi/F*/run.json`, `pipeline/state_events.csv` (and capture events if present). Last-frame CRC decode splits 10 HB / 4 inference / 1 echo. Full paths in `submission/defense/qa/LA_capture_key.md:7` onward | `build_evidence.py:138`–`:189` reanalyzes, checks retained values, CRC-decodes at `:140`–`:158`. `tools/la/la_analyze.py:89`–`:144` computes intervals but does not classify packet type. R5 + R6. Appendix B identifies all points. |
| `submission/defense/main.tex:209`–`:213` | 5 V/3 A supply, 18/18 original UART E3 flagged; firmware fixes not reflashed in old evidence | I `SUMMARY.md:6`; U `summary/{README.md,per_run.csv}`; `results/README.md:26`; snapshot qualification `submission/defense/CLAIMS.md:22`. No measurement from a 2026-10-20 flash was in this deck | Hand-authored. R3 can analyze a separately acquired E3_REAL campaign; S1/PS1 are new evidence, not replacements for U. |
| `submission/defense/main.tex:281`–`:285` | B3 threshold table: HB observation 100.128–100.641 ms; F5 HOLD 174.950–175.917 ms; F5 FAILSAFE 474.950–475.917 ms. Configured 100/200/500/1000/5 ms | F F1/F2 accepted events and S `r*/F5-r01/pipeline/state_events.csv`; source-derived configured values, **not measured** thresholds. `docs/STAGE_REPORT.md:106`–`:113`, `:350`–`:359` | Reason-aware event extraction `build_evidence.py:76`–`:89`; table text is manual. R4/R6 exports intervals; use min/max, not P50, for these ranges. |
| `submission/defense/main.tex:293`–`:304` | B4 full validity table: cyclic 30/30 v1, 6/30 v2; inference 21/24; E1/E2/E3 15/18/12, v2 0/45; E3b 3/12, six loaded flagged; U/U2 0/18 each; E4 17/25 (20 performed, five unperformed); extras F4 5/9 and F5 5/5; LA 15 plus one incomplete attempt | `results/README.md:18`–`:28`, `:41`–`:48`; E/B/U/U2 `summary/per_run.csv`; F `e4_runs.csv`; X/S `run.json`, power/echo/events; L retained `la_e4.csv`, incomplete `run_F1/F1-r05` | Manual inventory; `build_evidence.py:69`–`:72` asserts U2 18 invalid and `:104` asserts combined E4 34/27; `:169` asserts LA 15/10. R1–R5 recompute **separate new** inventories. |
| `submission/defense/main.tex:309`–`:311` | B5 MCU-local E4 P50/P95/max table, milliseconds; F4 mixed reasons and scopes | `submission/defense/qa/E4_local.tex:2`–`:6` holds every printed cell. Inputs same as Figure 10. F1 first 175.317/175.535/175.535, safe 100.456/100.641/100.641; F2 175.206/175.709/175.709 and 100.577/100.596/100.596; F3 175.754/175.815/175.815 and 475.754/475.815/475.815; F4 100.639/175.229/175.229 and 100.556/100.931/100.931; F5 175.596/175.917/175.917 and 475.596/475.917/475.917 | `build_evidence.py:124`–`:137`: nearest rank across accepted runs, P95=max at these sample sizes. R4 + R6. |
| `submission/defense/main.tex:317`–`:321` | B6 mapped onset E4 P50/P95/max; zero false transitions in checked pre-fault windows | `submission/defense/qa/E4_mapped.tex:2`–`:6`: F1 first 83.342/83.561/83.561, safe 85.357/86.209/86.209; F2 83.151/83.715/83.715 and 85.715/86.113/86.113; F3 83.646/85.914/85.914 and 383.620/385.888/385.888; F4 85.625/87.871/87.871 and 87.277/97.344/97.344; F5 83.608/85.563/85.563 and 383.603/385.558/385.558 ms. F `e4_runs.csv` has stored detection/failsafe µs and false-transition counts; extra X/S use mapped event minus onset | `build_evidence.py:86`–`:88`, `:124`–`:137`; zero false transitions is manually stated, checked by `analysis/e4_summary.py` during validity. R4 + R6; retain censoring/recovery fields. |
| `submission/defense/main.tex:325`–`:336` | B7 claim table, including zero replacements, slow completions and 10/15 matching analyzer references | Same E3, E3b, E4 and L files above; this table adds no new statistic | Manual synopsis; use R2/R4/R5/R8; do not automatically promote inferred backlog or unknown clean benefit. |

### Deck figures and tables that are not measurements

These still belong in the inventory so a re-run does not accidentally turn design choices into observations.

| Location | Asset/table and provenance | Regeneration / results input |
|---|---|---|
| `submission/defense/main.tex:23` | Figure 1 motivation, `images/W01.jpg`; reuse documented at `CLAIMS.md:7` | Existing illustration copied from `slides_course/images/W01.jpg`; no result input or data-producing script. Include unchanged at TeX build. |
| `submission/defense/main.tex:40`–`:52` | Figure 2 architecture, inline TikZ | TeX compilation only; source/configuration, no results-derived values. |
| `submission/defense/main.tex:73`–`:82` | Figure 3 queues; bridge FIFO capacity 256 and latest slot 1 | Inline TikZ + manual prose; `linux/src/hea_bridge.c`, `linux/inference/infer_server.py`; no measured count. |
| `submission/defense/main.tex:103`–`:116` | Figure 4 state machine; thresholds 100/200/500 ms and 1 s rearm | Inline TikZ + source configuration `stm32/firmware/main.c`, `stm32/src/supervisor.c`; no measured threshold or independent hardware watchdog. |
| `submission/defense/main.tex:59`, `:66`, `:95`, `:122`–`:132`, `:274`, `:281`–`:285` | Priorities 60/70, FIFO-50 timer, CPU placement, 4 GB, kernel, UART 921600, 3.3 V, cache 2 MiB, transit 5 ms, clock RMS ceiling 200 µs, maximum fit age 5 s | Configuration/metadata, not measured performance. E `E2_P{0,1}_B0_idle_latest_r1/{settings.json,pipeline/config.json}`, C0/C1 metadata, source and `CLAIMS.md:9`–`:13`, `:36`–`:50`. No performance-figure regeneration. |
| `submission/defense/main.tex:261`–`:266` | B1 frame table: 2/1/1/2/1/0–64+2 bytes; 35-byte INFERENCE; calculated 0.380 ms | `protocol/PROTOCOL.md`; no results. Calculation: `python3 -c 'print(f"{35*10/921600*1000:.3f} ms")'`. |
| `submission/defense/main.tex:271`–`:275` | B2 clock equations and configured acceptance ceilings | `protocol/CLOCK_SYNC.md`; TeX only. No fitted offset/drift number is printed. |
| `submission/defense/main.tex:238`, `:246`–`:254`, `:339`–`:355` | Five-valid-repeat future target, references, branch/source snapshot table-like columns | Planning/bibliographic/provenance material; no measured results. Preserve old snapshot as historical; document new acquisition commit/firmware separately. |

## 2. Vietnamese report: every table, figure and measured numeric passage

The report is **not** fed by `submission/report/generate_evidence.py`. Its builder reads `content.md` at `report_vi/build_docx.py:76`–`:77`, embeds named images at `:115`–`:130`, and converts literal Markdown tables at `:132`–`:146`. It writes `report_vi/BaoCao_HDH_Nhom3Stars.docx` at `:185`–`:193`. Rebuilding the DOCX does not recompute any measured number.

| Location in `report_vi/content.md` | Complete content / numeric scope | Results provenance and producer | Regenerate |
|---|---|---|---|
| `:3`, `:9`–`:16`, `:26`–`:52` | Cover logo, member table, glossary table | `report_vi/figures/logo_hust.jpg`; manually authored identity/definitions, no measured input | R9 DOCX conversion; existing image reused. |
| `:84` | Figure 2.1 AoI (`figures/aoi.png`) | Conceptual sawtooth, no results. `report_vi/figures/draw_figures.py:78`–`:85` uses invented illustrative coordinates and unlabeled ticks | R9 conceptual-AoI command. |
| `:96` | Figure 3.1 architecture (`figures/Hinh_3_1_System_architecture.png`) | Student-authored asset; corresponding SVG retained. Not the `architecture.png` produced by `draw_figures.py:33`–`:53`. `report_vi/README.md:11`–`:13` | Existing PNG/SVG reuse; no results command or retained exact crop/export script. R9. |
| `:102` | Figure 3.2 UART (`figures/Hinh_3_2_UART_frame.png`) | Student-authored PNG/SVG, no results; not `frame.png` from `draw_figures.py:55`–`:63` | Same asset reuse/export limitation. R9. |
| `:104`–`:111` | Table 1 frame: 2-byte SOF, 1-byte version/type, 2-byte seq, 1-byte length, payload ≤64, 2-byte CRC | Manual protocol design; `protocol/PROTOCOL.md`, not a measurement | R9 converts literal table; no results input. |
| `:125` | Figure 3.3 queues (`figures/Hinh_3_3_Queue_policies.png`) | Student-authored PNG/SVG, no results; not `queues.png` from `draw_figures.py:65`–`:76` | Same asset reuse/export limitation. R9. |
| `:135`, `:139` | MobileNetV2-12 / ORT 1.31.0; P1 60/70, CPU1, inference OTHER CPU0; earlier bridge priority 50 | I `SUMMARY.md:1`, per-run `bench/summary.json` config; E `E2*/settings.json`, `pipeline/config.json`; design history is not a measured effect | Metadata inspection; R9 converts prose. |
| `:153`, `:155`–`:164` | Table 2 counts: timer 30/30 v1, 3/15 per profile v2; standalone 21/24, three excluded; E1/E2/E3 45/45→0/45; E3b 3/12, six loaded excluded; U 0/18; F 17/25 incl. five unperformed; S 5/5 | Exact inventory `results/README.md:18`–`:28`, `:41`–`:48`; stored C0/C1 `summary.csv`; I `SUMMARY.md:19`; E/B/U `summary/per_run.csv`; F `e4_runs.csv`; S raw short-window records | Manual Markdown table. R1–R5 produce separate re-run counts, not replacements for this table. |
| `:166` | Kernel 6.8.0-1064-raspi; supply 5 V/3 A; measured rail 4.66–4.92 V; 1.5 s monitor-gap and 5 s fit-age rules; Pi clock ≈3 days behind | I `SUMMARY.md:4`–`:6`, I `power.csv`/metadata; `results/README.md:5`–`:8`, `:37` (rules are configured acceptance limits) | No retained voltage-range aggregation script; inspect power log. R1–R5 apply current gates; do not treat these constants as performance results. |
| `:170`, `:172`–`:178` | Table 3 timer idle and memrate: P0 P50/P99/max 53/57/2659 and 55/613/5170; P1 3/9/92 and 5/239/1094 µs. 120 s×3, 1 ms period, FIFO50. Prose repeats P99 endpoints | C0/C1 `summary_by_condition.csv:2`, `:4`; `results/2026-10-11_cyclictest/SUMMARY.md:3`–`:16`; histograms/metadata as deck Figure 5 | Manual selected rows, not a report figure. R1 gives new numeric/TeX tables; R6 timer plot if desired; R9 typesets content. |
| `:180`–`:189` | Table 4 inference: idle1 3/44.0/48.0/57.0; idle3 3/29.4/38.5/52.8; idle4 1/31.4/70.7/94.1; CPU1 3/45.1/53.7/65.5; CPU4 2/60.3/100.5/150.3 (n/P50/P99/max ms). Prose repeats P50 values, 1000 timed/50 warmups | I `SUMMARY.md:10`, `:12`–`:14`, `:17`; raw bench summaries/samples, as deck Figure 6 | Manual selection. R7; keep original, since standalone inference is not in today's stated re-run. |
| `:193`, `:195`–`:207`, `:209` | Table 5: E1 idle delivery 44.37/48.47, memrate 6626/13980; E2 cache P0 66.81/73.57 and P1 70.19/97.16; E3 mean/peak idle FIFO 94.69/158, latest 94.59/156; memrate FIFO 6660/13660, latest 6958/14170 ms. Three reps/cell. Prose repeats E1 P50, E3 means and zero bridge replacements; defines AoI denominator | E `summary/E1_table.csv:2`, `:4`; `E2_table.csv:4`, `:7`; `E3_table.csv:2`–`:5`; `E3_per_condition.csv`; raw pipeline logs. E1/E2 use delivery P50/P99; E3 uses mean/max peak, not delivery quantiles | `analysis/e_summary.py:175`–`:225`, `:251`–`:293` supplies these values; Markdown manually selected/formatted. R2 + R6; no measured plots are embedded in the current Vietnamese report. |
| `:211` | E3b discussion, no additional numeric measurement | B acceptance/diagnostic distinction from Table 2; deck diagnostic ranges are not printed here | R2/R8; do not invent a clean original comparison. |
| `:215` | Original physical E3 0/18, 16/18 power flags, all memory-loaded clock failures; U2 another 18 all undervoltage; loaded input/bridge latest r1 FAILSAFE entire window, r2/r3 HOLD 92.15%/91.44% | U `summary/per_run.csv`, `README.md` (`results/README.md:26`); U2 `summary/per_run.csv:17`–`:19` with `init_seconds`, `fresh_seconds`, `hold_seconds`, `failsafe_seconds`. Percent =100×hold/sum(all four state durations), not packets or nominal 60 s; r1 failsafe=60.379060372 s. r2 hold=55.637133852 of 60.374146852 s; r3 hold=55.092590149 of 60.252413149 s | `analysis/e3_real_summary.py:55`–`:101`, `:104`–`:178`, `:225`–`:257`; report percentages manually rounded. R3 and R8. This is the **October 12** re-run, separate from October 20. |
| `:217`, `:219`–`:227` | Table 6 accepted MCU-local FAILSAFE P50/max: F1 5/5 100.456/100.641; F2 5/5 100.577/100.596; F3 5/5 475.754/475.815; F5 5/5 475.596/475.917 ms. Prose repeats F5 P50, configured 100/200/500 and transit 5 ms | Same raw F/S events as deck Figure 10/B5; exactly `submission/defense/qa/E4_local.tex:2`–`:4`, `:6` FAILSAFE columns (table omits F4). Reason selects HB or inference receipt reference | `build_evidence.py:76`–`:89`, `:124`–`:137`; report table manually transcribed, not linked by builder. Current `e4_summary.py:190`–`:207`, `:229`–`:265` can produce new reason-aware intervals. R4 + R6. |
| `:229` | LA marker→safe ranges: F1 86.938–95.541, F2 86.947–98.676, F4 82.852–91.302 ms; F2 includes check capture. 10/15 agree within 0.07 ms, five use different final frame | L `run_F1/la_e4.csv:2`–`:5`, `run_F2/la_e4.csv:2`–`:6` plus `check_F2/la_e4.csv:2`, `run_F4/la_e4.csv:2`–`:6`; min/max of `marker_safe_us`/1000, **not** `uart_safe_us`. Reference matching and Δ bound use deck CRC analysis and `qa/LA_capture_key.md` | `la_analyze.py:89`–`:144`, `:147`–`:180`; `build_evidence.py:138`–`:189` for CRC split. No report plot here. R5/R6/R8. |
| `:247`, `:249`–`:259` | Table 7 roadmap A–F; at least five valid repeats target; current three-repeat cells preliminary | Manual planning table, not results-derived; no measured completion claim | R9 literal conversion. Do not mark stages complete solely from S1 or PS1. |

The abstract (`content.md:19`), earlier interpretation (`:68`, `:127`), discussion (`:235`–`:241`) and conclusion (`:263`) repeat qualitative interpretations of the mapped measurements; they contain no additional measured numeric cells. Bibliographic years/page numbers at `:266`–`:273`, team IDs, figure/table/RQ numbers, OS versions and design capacities are not experimental statistics.

## 3. Exact regeneration recipes

### R0 — bind actual new directories, keep generated files separate

Run later from repository root on macOS (analysis/build only), or on Pi with the same Python tools. These paths are explicit placeholders: replace the angle-bracket run names with directories actually received. Do not assume timestamp names or classify a directory just by its name. Commands in R1–R9 are not part of this read-only audit's execution.

```bash
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR=/tmp/os-rerun-mpl
export RERUN_ROOT="$PWD/results/2026-10-20_rerun"
export NEW_C0="$RERUN_ROOT/<P0-run>"
export NEW_C1="$RERUN_ROOT/<P1-run>"
export NEW_E="$RERUN_ROOT/<ALL-onnx-run>"
export NEW_F="$RERUN_ROOT/<full-E4-run>"
export NEW_L="$RERUN_ROOT/<analyzer-batches-parent>"
export OUT=/tmp/os-rerun-2026-10-20
mkdir -p "$OUT"
```

`NEW_L` is a parent containing F1/F2/F4 batch directories, each with `<capture>/capture.vcd` and `<capture>/pi/F*/run.json`. If all captures share one batch, set `NEW_L` to that batch's parent and limit enumeration to its `la_e4.csv`. Actual Pi-local collection must preserve this analysis layout or be explicitly adapted. No acquisition command is prescribed here: the checked-in `la_e4.sh` is a Mac/SSH acquisition workflow, while the user reports acquisition now runs on the Pi. Analysis consumes files regardless of collector host. `tools/la/README.md:33` still says 24 MHz, but `tools/la/la_e4.sh:78` requests **8m**, and the old deck already says 8 MHz (`main.tex:203`); record actual new capture metadata, not the stale README rate.

### R1 — timer tables (all five conditions and selected report Table 3)

```bash
python3 analysis/cyclictest_summary.py "$NEW_C0" --outdir "$OUT/cyclic-P0"
python3 analysis/cyclictest_summary.py "$NEW_C1" --outdir "$OUT/cyclic-P1"
```

Outputs: `summary.csv`, `summary_by_condition.csv`, `summary_table.tex` per profile (`analysis/cyclictest_summary.py:254`–`:291`). Report Table 3 selects idle/memrate and P50/P99/max. Deck selects all five P99 values. V2 applies to new data; original `summary_by_condition.csv` must not be overwritten.

### R2 — E1/E2/E3/E3B tables from ALL ONNX

```bash
python3 analysis/e_summary.py "$NEW_E" --outdir "$OUT/pipeline"
```

Produces `per_run.csv`, `per_condition.csv`, `excluded.csv`, plus each `E{1,2,3,3B}_{table,per_condition,per_run}.csv` and LaTeX tables (`e_summary.py:251`–`:293`). Select metrics described in the document maps, with `valid_reps/total_reps`. For a single PTY pipeline diagnostic, `python3 analysis/pipeline_summary.py "$NEW_E/<condition-run>/pipeline"` prints JSON without writing results (`pipeline_summary.py:143`–`:152`).

**Do not assume E2/E3 new load identities.** `tools/experiments/e_campaign.py:40`–`:49`, `:313`–`:325` ranks E1 and chooses two worst stressors for E2 and one for E3; `worst_stressors.json` records them. ALL includes E3B. Its software summarizer expressly rejects a serial pipeline (`e_summary.py:132`–`:133`). ONNX stage does not imply physical UART.

### R3 — optional physical E3 tables, only if separately acquired

PS1 is a link smoke run, not an E3_REAL policy campaign. Today's stated list has no separate E3_REAL campaign. There is therefore no new physical E3 policy statistic to fill merely because ALL or PS1 completed.

`analysis/e3_real_summary.py` has **no `--outdir` option** and normally writes into `<campaign>/summary` (`:225`–`:257`). To retain raw input unchanged, redirect only this module's output directory in memory:

```bash
export NEW_U="$RERUN_ROOT/<separate-E3_REAL-run-if-acquired>"
python3 - <<'PY'
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path('analysis').resolve()))
import e3_real_summary as m
source = Path(m.__file__).read_text()
old = "out = campaign / 'summary'"
assert source.count(old) == 1
source = source.replace(old, "out = Path(__import__('os').environ['OUT']) / 'physical-E3'")
namespace = {'__name__': 'rerun_physical', '__file__': m.__file__}
exec(compile(source, m.__file__, 'exec'), namespace)
namespace['write_summary'](Path(os.environ['NEW_U']))
PY
```

Produces per-run/per-condition physical MCU/mapped receipt-age, state-duration, validity tables. MCU-local validity and mapped validity are separate (`:159`–`:162`). Its current prerequisites specifically include `/dev/ttyAMA0`, 921600, ONNX/P1 and stricter 0.75 s power sample gaps (`:115`–`:135`); a differently configured PS1 cannot simply be passed here.

### R4 — full physical E4 tables

```bash
python3 analysis/e4_summary.py "$NEW_F" --outdir "$OUT/e4" --max-calibration-age-s 5
```

Produces `e4_runs.csv`, `e4_faults.csv`, `e4_faults.tex`, `e4_thresholds.json` (`e4_summary.py:290`–`:320`). Units in CSV are µs. MCU-local report cells divide by 1000. P50/P95/max are nearest rank across accepted runs (`:229`–`:265`); mixed reason groups retain their warning. Thresholds come from campaign `supervisor_thresholds.json` when present, otherwise include defaults (`:303`–`:311`): do not describe fallback source defaults as measured flashed thresholds. Review full-campaign recovery/exposure validity separately from old short-window checks and LA single mode (`tools/la/README.md:25`–`:31`).

### R5 — analyzer tables and first-capture waveform

The stock CLI writes in the supplied batch directory (`tools/la/la_analyze.py:147`–`:180`). To keep raw batches untouched, analyze them directly and export only to OUT using the same functions. This command also reports marker-safe ranges used by Vietnamese paragraph 229:

```bash
python3 - <<'PY'
import csv, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('tools/la').resolve()))
import la_analyze as la
base = Path(os.environ['NEW_L'])
out = Path(os.environ['OUT']) / 'la'
out.mkdir(parents=True, exist_ok=True)
all_records = []
for batch in sorted({p.parent.parent for p in base.rglob('capture.vcd')}):
    records, traces = [], []
    for p in sorted(batch.glob('*/capture.vcd')):
        run = list(p.parent.glob('pi/F*/run.json'))
        assert len(run) == 1, str(p)
        trace = la.read_trace(p)
        r = dict(capture=str(p.parent.resolve()), **la.analyze(trace, run[0].parent))
        records.append(r); traces.append(trace)
    if not records:
        continue
    dest = out / batch.name
    dest.mkdir(exist_ok=True)
    with (dest / 'la_e4.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    all_records.extend(records)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12,4))
    marker = records[0]['t_marker_rise_s']
    for i, label in enumerate(('PA5','PB5','UART','marker')):
        ax.step([(t-marker)*1000 for t,p in traces[0]], [p[i]*.7+i for t,p in traces[0]], where='post', label=label)
    ax.set_xlabel('Analyzer time from marker (ms)'); ax.legend()
    fig.savefig(dest / 'la_timing.png', dpi=160); plt.close(fig)
    vals = [r['marker_safe_us']/1000 for r in records if r['marker_safe_us'] is not None]
    print(batch, 'captures', len(records), 'marker-safe ms', (min(vals), max(vals)) if vals else 'unavailable')
(out / 'records.json').write_text(json.dumps(all_records, indent=2) + '\n')
PY
```

This is an audit-supplied output adapter, not a pre-existing repository script. It preserves `la_analyze.analyze` qualification strings. VCD needs D0..D3 and valid timescale (`la_analyze.py:11`–`:51`). Original CLI equivalents, for a disposable batch copy only: `python3 tools/la/la_analyze.py <copied-batch>` produces `la_e4.csv`, `la_e4.tex`, optional `la_timing.png`. No CRC/frame-matching claim follows from that CLI alone.

### R6 — new deck-style measured plots and the two E4 table views

The original builder has **no CLI inputs** and runs at import/top level. `RES` is fixed at `build_evidence.py:13`, C paths at `:29`, I at `:41`, E at `:51`, U2 at `:70`, F/X/S at `:74`–`:95`, L at `:160`. Assertions at `:72`, `:104`, `:169`–`:170` encode original counts and residual ranges; labels/denominators at `:119`, `:134`, `:175` also encode old outcomes. Running it after dropping a new directory into results would still plot originals.

For the **unchanged historical** seven plots/two tables, the exact command is `python3 submission/defense/build_evidence.py`; it writes under `submission/defense/` and must not be run during this read-only task. To generate new counterparts without editing it, run the explicit adapter below after R1/R2/R4/R5. This reuses its plotting header and UART CRC decoder in memory, reads new analysis outputs, and writes separate files. It derives labels from condition identities; missing/invalid cells stay missing. It does not assert that the new run repeats old outcomes.

```bash
python3 - <<'PY'
import csv, json, math, os
from pathlib import Path
src = Path('submission/defense/build_evidence.py').resolve()
lines = src.read_text().splitlines(True)
g = {'__file__': str(src), '__name__': 'rerun_plots'}
exec(compile(''.join(lines[:27]), str(src), 'exec'), g)
exec(compile(''.join(lines[139:158]), str(src), 'exec'), g)  # decode(), no data reads
out = Path(os.environ['OUT'])
g['HERE'] = out
(out/'images').mkdir(exist_ok=True)
plt, save = g['plt'], g['save']
def rows(p):
    with Path(p).open() as f: return list(csv.DictReader(f))
def bars(key, labels, values, ylabel):
    fig, ax = plt.subplots(figsize=(12,4))
    ax.bar(range(len(values)), values, color=g['TEAL'])
    ax.set_xticks(range(len(values)), labels, rotation=25, ha='right', fontsize=9)
    ax.set_ylabel(ylabel); ax.set_title('Re-run (2026-10-20)')
    ax.set_yscale('log'); save(fig, key)
loads = ['B0_idle','CPU_c23','B1_stream_c2','C1_cache2M_c2','B2_memrate_c23']
fig, ax = plt.subplots(figsize=(11,3.2))
for k in (0,1):
    rr = rows(out/f'cyclic-P{k}/summary_by_condition.csv')
    by = {r['condition'].split('_',1)[1]:r for r in rr}
    values = [float(by[n]['p99_us']) if by[n]['p99_us'] else math.nan for n in loads]
    ax.bar([i+(k-.5)*.34 for i in range(5)], values, .34, label=f'P{k}')
ax.set_xticks(range(5), loads, rotation=20, fontsize=9)
ax.set_ylabel('Wake-up P99 (µs)'); ax.set_yscale('log'); ax.legend(); save(fig,'cyclic')
for experiment in ('E1','E2','E3','E3B'):
    rr = rows(out/f'pipeline/{experiment}_per_condition.csv')
    if experiment in ('E1','E2'):
        metric, ylabel = 'delivery_p99_ms', 'Delivery P99 (ms)'
    elif experiment == 'E3':
        metric, ylabel = 'aoi_time_average_ms', 'Initialized mean AoI (ms)'
    else:
        metric, ylabel = 'delivery_p99_ms', 'Reception P99 (ms)'
    labels = [' / '.join(r[k] for k in ('profile','stressor','input_policy','policy')) for r in rr]
    vals = [float(r[metric]) if r.get(metric) else math.nan for r in rr]
    if rr: bars(experiment, labels, vals, ylabel)
rr = rows(out/'e4/e4_runs.csv')
valid = [r for r in rr if r['validity']=='VALID']
fig, axes = plt.subplots(1,2,figsize=(12,3.5))
for ax, metric in zip(axes, ('detection_mcu_us','failsafe_mcu_us')):
    prefix = metric.split('_')[0]
    for i, fault in enumerate(('F1','F2','F3','F4','F5')):
        members = [r for r in valid if r['fault']==fault and r.get(metric)]
        for j,r in enumerate(members):
            reason = r.get(prefix+'_reason','')
            color, marker = {'3':(g['FAULT'],'s'),'9':(g['NAVY'],'^'),'10':(g['TEAL'],'o')}.get(reason,('gray','x'))
            ax.scatter(i+(j-(len(members)-1)/2)*.11, float(r[metric])/1000, color=color, marker=marker)
    ax.set_xticks(range(5),('F1','F2','F3','F4','F5'))
    ax.set_ylabel('Receipt to event (ms)'); ax.set_title(metric)
save(fig,'E4')
def nr(v,q): return sorted(v)[math.ceil(len(v)*q)-1]
for domain, metrics in [('local',('detection_mcu_us','failsafe_mcu_us')),('mapped',('detection_us','failsafe_us'))]:
    tex = [r'\begin{tabular}{lrrr}', r'Fault & Valid & First P50/P95/max (ms) & Safe P50/P95/max (ms) \\']
    for fault in ('F1','F2','F3','F4','F5'):
        members = [r for r in valid if r['fault']==fault]
        denom = sum(r['fault']==fault for r in rr)
        cells = []
        for metric in metrics:
            v = [float(r[metric])/1000 for r in members if r.get(metric)]
            cells.append(' / '.join(f'{x:.3f}' for x in (nr(v,.5),nr(v,.95),max(v))) if v else 'unavailable')
        tex.append(f'{fault} & {len(members)}/{denom} & '+ ' & '.join(cells)+r' \\')
    (out/f'E4_{domain}.tex').write_text('\n'.join(tex+[r'\end{tabular}'])+'\n')
# CRC split for LA plot: raw paths are recorded by R5.
import sys
sys.path.insert(0, str(Path('tools/la').resolve()))
import la_analyze as la
records = json.loads((out/'la/records.json').read_text())
classified = []
for r in records:
    if r['t_safe_s'] is None or r['delta_safe_us'] is None: continue
    trace = la.read_trace(Path(r['capture'])/'capture.vcd')
    frames = g['decode'](trace,r['t_safe_s'])
    # The final physical byte must end a decoded CRC-valid frame.
    frame = frames[-1] if frames else None
    matching_end = frame and abs(frame['end']-r['t_last_uart_byte_s'])<1e-9
    r['last_frame_type'] = frame['type'] if matching_end else None
    r['matching'] = bool(matching_end and frame['type']==1)
    classified.append(r)
fig, axes = plt.subplots(1,2,figsize=(12,3.1))
for ax, matched, scale in zip(axes,(True,False),(1,1000)):
    members = [r for r in classified if r['matching']==matched]
    ax.scatter(range(1,len(members)+1),[r['delta_safe_us']/scale for r in members])
    ax.set_title(f'{len(members)} '+('final HEARTBEAT' if matched else 'different or undecoded final frame'))
    ax.set_xlabel('Capture index'); ax.set_ylabel('Δ (µs)' if matched else 'Δ (ms)')
save(fig,'LA')
(out/'la/classified.json').write_text(json.dumps(classified,indent=2)+'\n')
print('New plots and E4 tables:', out)
PY
```

This adapter's E4 table reports original-style mixed first-transition summaries, so include reason distributions alongside it and use `e4_faults.csv` warnings. Counts are new actual counts. Censored transitions are not zero. The new LA “different” panel may include undecodable final frames; list those separately in the new capture key. Original deck code asserts every final byte ends a CRC-valid frame; that may fail for new captures and must not be assumed.

### R7 — standalone inference is outside today's stated re-run

The historical plot/table can be regenerated from retained I `SUMMARY.md` by the original defense builder; the Vietnamese table remains a manual selection. Today's ONNX E campaign measures end-to-end pipeline service/delivery, not the model-only 1–4-thread sweep. Therefore keep Figure 6 / Table 4 dated 2026-10-11 and put “not repeated” in the comparison unless a separate sweep is acquired.

For a separately acquired sweep, per-run data can be recomputed exactly from `bench/samples.csv` using `linux/inference/bench_common.py:15`–`:31` (interpolation, not nearest rank):

```bash
export NEW_I="$RERUN_ROOT/<separate-inference-sweep-if-acquired>"
python3 - <<'PY'
import csv, json, os, statistics, sys
from pathlib import Path
sys.path.insert(0,str(Path('linux/inference').resolve()))
from bench_common import summarize
for p in sorted(Path(os.environ['NEW_I']).glob('*/threads-*/bench/samples.csv')):
    with p.open() as f: samples=list(csv.DictReader(f))
    d=summarize([int(r['infer_ns']) for r in samples])
    print(p.parent.parent.parent.name,p.parent.parent.name,{k:v/1e6 for k,v in d.items() if k in ('p50_ns','p99_ns','max_ns')})
PY
```

No retained command automatically reconstructs the accepted cross-run `SUMMARY.md`. The old per-thread `validity.json` is **not** an accepted-subset selector: e.g. `I/idle_r1/threads-1/validity.json:3` says false because of historical sticky flags, although the live-power baseline includes it. Use I `SUMMARY.md:5`, `:19`, `campaign.sh:2`–`:15`, the continuous power log and actual windows to establish eligibility; median eligible per-run P50/P99, maximum eligible max. For a new sweep require an explicit accepted-run manifest, then aggregate and plot that manifest; do not silently import old exclusions. This is a reproducibility gap, not an existing script interface.

### R8 — supplementary prose diagnostics

Completion intervals (deck slide 14), raw E3B diagnostic P99, physical state occupancy, and report LA ranges are not separate deck figures. Exact read-only extraction commands for any directory of the corresponding format:

```bash
python3 - <<'PY'
import csv, math, os, statistics
from pathlib import Path
base=Path(os.environ['NEW_E'])
def rows(p):
    with p.open() as f: return list(csv.DictReader(f))
for p in sorted(base.glob('E3_*/pipeline/infer.csv')):
    t=sorted(int(r['t_done_ns']) for r in rows(p) if r.get('t_done_ns') and r.get('status')!='skipped_stale')
    if len(t)>1: print('completion interval ms',p,statistics.median([b-a for a,b in zip(t,t[1:])])/1e6)
for p in sorted(base.glob('E3B_*/pipeline/rx.csv')):
    age=[(int(r['t_rx_ns'])-int(r['t_input_ns']))/1e6 for r in rows(p) if r.get('crc_ok')=='1' and r.get('type')=='INFERENCE']
    if age: print('DIAGNOSTIC, eligibility separate',p,'P99 ms',sorted(age)[math.ceil(.99*len(age))-1])
out=Path(os.environ['OUT'])
u=out/'physical-E3/per_run.csv'
if u.exists():
    for r in rows(u):
        if not r.get('hold_seconds'): continue
        total=sum(float(r[k]) for k in ('init_seconds','fresh_seconds','hold_seconds','failsafe_seconds'))
        print('state occupancy',r['run'],'HOLD %',100*float(r['hold_seconds'])/total if total else None,'valid',r['valid'])
PY
```

Use `NEW_E=...` pointing at E for original intervals or B for original E3B if reproducing those passages; inspect the run's status/CRC semantics before including rows. R5 prints LA marker-safe ranges; R6 exports reason-aware local/mapped E4 tables. Use new `e4_runs.csv` grouped by event reason for threshold observation min/max, not a nominal timeout subtraction.

### R9 — report conceptual figures and document builds

For only the report's reproducible conceptual AoI image in a separate directory:

```bash
python3 - <<'PY'
import os, runpy
from pathlib import Path
g=runpy.run_path('report_vi/figures/draw_figures.py',run_name='report_diagrams')
g['aoi'].__globals__['ROOT']=Path(os.environ['OUT'])
g['aoi']()
PY
```

`python3 report_vi/figures/draw_figures.py` instead emits four conceptual files (`architecture.png`, `frame.png`, `queues.png`, `aoi.png`); three do **not** replace the student-named report assets (`report_vi/README.md:11`–`:13`). The existing named PNGs/SVGs have no results parameter and need no re-run regeneration. No exact student SVG-to-cropped-PNG generation command is retained in this path; reuse the retained PNGs.

After a **separate authorized integration**, rebuild with these existing commands (they write tracked/generated outputs, so were not executed here):

```bash
python3 report_vi/build_docx.py
python3 report_vi/validate_docx.py
python3 report_vi/style_check.py
(cd submission/defense && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex)
```

The defense check currently expects the old deck shape; insertion requires updating expectations and speaker timing before using `python3 submission/defense/check_deck.py` (`submission/defense/README.md:3`, `:9`–`:24`). Report validation also checks table/figure counts (`report_vi/README.md:33`–`:35`). Rebuilding documents alone never reruns measurements or fills new Markdown/TeX prose.

### R10 — emit new counterparts of the report's measured Markdown tables

After R1/R2/R4, this exact command emits selected report-shaped tables under OUT. It does not edit `content.md`. Table 2's new counterpart keeps the new full-E4 F5 count within E4, and explicitly marks standalone inference and physical E3 as not repeated. Table 5 requests the original load identities; unmatched cells stay unavailable instead of substituting a differently ranked load. The complete R2 condition tables must accompany it if new loads differ. Table 6 splits reference domains when necessary. Table 4 remains the dated original unless a separate accepted sweep is supplied (R7).

```bash
python3 - <<'PY'
import csv, math, os
from pathlib import Path
out=Path(os.environ['OUT'])
def rows(p):
    with p.open() as f: return list(csv.DictReader(f))
def table(title, headers, data):
    text=[title,'| '+' | '.join(headers)+' |','|'+'---|'*len(headers)]
    text += ['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in data]
    return '\n'.join(text)+'\n\n'
def val(row,key):
    return row.get(key) or 'unavailable' if row else 'unavailable / unmatched'
c={k:rows(out/f'cyclic-P{k}/summary_by_condition.csv') for k in (0,1)}
cr=[r for k in (0,1) for r in rows(out/f'cyclic-P{k}/summary.csv')]
pr=rows(out/'pipeline/per_run.csv')
fr=rows(out/'e4/e4_runs.csv')
counts=[]
counts.append(['cyclictest',f"{sum(r['status']=='VALID' for r in cr)}/{len(cr)}",'v2; 60 s requested, check actual windows'])
counts.append(['Standalone inference','not repeated','original 2026-10-11 remains'])
for exp in ('E1','E2','E3','E3B'):
    members=[r for r in pr if r['experiment']==exp]
    counts.append([exp,f"{sum(r['valid']=='True' for r in members)}/{len(members)}",'v2; software PTY'])
counts.append(['Physical E3','not repeated by ALL/PS1','separate E3_REAL acquisition required'])
counts.append(['Full E4',f"{sum(r['validity']=='VALID' for r in fr)}/{len(fr)}",'includes actual F5 entries; retain NOT_DONE/censoring'])
text=table('New counterpart of Table 2 — re-run (2026-10-20)',['Collection','Accepted/total','Scope'],counts)
by={k:{r['condition'].split('_',1)[1]:r for r in c[k]} for k in (0,1)}
data=[]
for load in ('B0_idle','B2_memrate_c23'):
    data.append([load]+[val(by[k].get(load),key) for k in (0,1) for key in ('p50_us','p99_us','max_us')])
text+=table('New counterpart of Table 3 — µs; 2026-10-20, 60 s runs',['Load','P0 P50','P0 P99','P0 max','P1 P50','P1 P99','P1 max'],data)
conditions=rows(out/'pipeline/per_condition.csv')
def find(exp,profile,load,policy):
    return next((r for r in conditions if (r['experiment'],r['profile'],r['stressor'],r['policy'])==(exp,profile,load,policy)),None)
data=[]
for exp,profile,load,policy in [('E1','P0','B0_idle','latest'),('E1','P0','B2_memrate_c23','latest'),('E2','P0','C1_cache2M_c2','latest'),('E2','P1','C1_cache2M_c2','latest')]:
    r=find(exp,profile,load,policy)
    data.append([f'{exp}/{profile}/{load}',val(r,'delivery_p50_ms'),val(r,'delivery_p99_ms')])
for load in ('B0_idle','B2_memrate_c23'):
    for policy in ('fifo','latest'):
        r=find('E3','P1',load,policy)
        data.append([f'E3/{load}/{policy}',val(r,'aoi_time_average_ms'),val(r,'aoi_peak_ms')])
text+=table('New counterpart of Table 5 — ms; 2026-10-20',['Metric/condition','Delivery P50 or mean AoI','Delivery P99 or peak AoI'],data)
data=[]
for fault in ('F1','F2','F3','F5'):
    all_runs=[r for r in fr if r['fault']==fault]
    valid=[r for r in all_runs if r['validity']=='VALID' and r.get('failsafe_mcu_us')]
    for ref in sorted({r['failsafe_reference'] for r in valid}) or ['unavailable']:
        samples=sorted(float(r['failsafe_mcu_us'])/1000 for r in valid if r['failsafe_reference']==ref)
        data.append([fault,f'{len(valid)}/{len(all_runs)}',ref,len(samples),f'{samples[math.ceil(.5*len(samples))-1]:.3f}' if samples else 'unavailable',f'{max(samples):.3f}' if samples else 'unavailable'])
text+=table('New counterpart of Table 6 — MCU-local ms; 2026-10-20',['Fault','Accepted/total','Reference','Samples in reference group','P50','Max'],data)
(out/'report_tables.md').write_text(text)
print(out/'report_tables.md')
PY
```

The old report's cover/glossary, Table 1 protocol and Table 7 roadmap have no results dependency; R9 converts their unchanged literals. New S1/PS1 evidence must be summarized only after its actual output files and scope are known. Nothing in this command supplies a new model-only or physical-policy campaign.

## 4. Concrete additive integration plan

### Placement and preservation

1. **Deck:** insert a new frame titled **“Re-run (2026-10-20): original vs re-run”** immediately after the original analyzer frame's `\end{frame}` at `submission/defense/main.tex:205`, before original limitations begin at `:207`. Keep original slides 9–16 and backup tables intact; add date labels to original measured captions/scopes (2026-10-11 timer/inference/PTY; 2026-10-12 E3B/E4/LA), leaving every old cell and original acceptance rule visible. If too dense, use this main slide for accepted counts + selected comparable metrics and add full re-run metric tables after B6 at `:322`, before B7 at `:324`. Reference distinct `images/rerun_2026-10-20_*.pdf` and `qa/rerun_2026-10-20_*` files; never overwrite the original seven plot names or E4 includes. Existing snapshot date `:16` stays explicitly historical; add a separate update date.
2. **Vietnamese report:** insert **“## 5.5 Đo lại (2026-10-20): đối chiếu với kết quả gốc”** after `report_vi/content.md:229`, before Part 6 at `:231`. Keep Tables 2–6 and their original prose as historical observations; date their captions without altering numbers. Add **Table 8** for original/new qualification and numeric comparisons, preserving existing roadmap **Table 7** at `:249` (or use a clearly distinct “Bảng đo lại 2026-10-20” caption to avoid out-of-order numbering). Put provenance, run IDs, S1/PS1 status, methods, new results and interpretation in 5.5. Current report has no measured charts: add new charts only if useful, with new names such as `figures/rerun_2026-10-20_cyclic.png`, never replace conceptual Figures 2.1/3.1–3.3. Builder embeds the exact named image and converts literal tables; it does not ingest analysis CSV automatically.
3. **New limitations and conclusion:** append dated follow-up paragraphs/frames referring to 5.5/new slide, rather than rewriting old numbers or claiming prior limitations never existed. In particular, the old “not reflashed” statement (`main.tex:213`) describes the old snapshot. A successful S1 plus PS1 may establish a new flash/link observation, not automatically DMA loss bounds, stack margins, calibrated clocks, rearm, long-exposure qualification, or clean E3 policy benefit. Update future-work status only for evidence actually received and validated.

### Comparison table to populate after acquisition

Use columns **metric + unit / configuration and scope / original date / original value + accepted n/total + rule / re-run (2026-10-20) value + accepted n/total + rule / comparability note + source**. Keep separate rows by load/profile/policy/reason and by local/mapped clock domain. Do not calculate a percentage improvement for mismatched scopes or an unaccepted original.

| Comparison row(s) | Original cells to retain | New source / treatment |
|---|---|---|
| S1 flash identity + verification; PS1 60 s physical link | No equivalent original measured table; historical bring-up is seven flagged diagnostics (`results/README.md:28`), not a clean reference | New S1 flash stdout/stderr/exit status, firmware hash/build commit and reset record; PS1 `config.json`, window markers, command/exit/DONE, `summary.json`, `echo.csv`, `inf_rx.csv`, `mcu_status.csv`, `state_events.csv`, power/metadata if retained. File names must be taken from actual delivered runs; no S1/PS1-specific aggregation interface was found. `scripts/stm32/flash.sh:6`–`:14` itself writes no result bundle. Show status/observed counts only, no invented latency. |
| Timer P0/P1 × all 5 conditions, P50/P99/max µs, valid counts | Original Figure 5 / Table 3 and C0/C1 v1 summaries; 3×120 s/cell, v2 accepts idle only | R1 new 3×60 s/cell. Explicit unequal-duration note; maxima depend on exposure. Do not present 60 s maxima as a matched 120 s extreme-value comparison. |
| Model-only thread sweep | Figure 6 / Table 4, 2026-10-11, 21/24 | “Not repeated in this campaign”; ONNX stage is not the standalone sweep. |
| E1 load × delivery P50/P99/max ms | E1_table rows, 2026-10-11 PTY v1 | R2 accepted v2 cells. Keep “software PTY” unless config proves another separately supported scope. |
| E2 profile × matched stressor × delivery P50/P99 ms | Original idle/memrate/cache, P0/P1, E2_table | R2 condition IDs and `worst_stressors.json`. If new ranking chooses another stressor, show unmatched/new-only row; no old-vs-new causal delta. |
| E3 load × bridge FIFO/latest: initialized mean/peak AoI, overwritten, delivered/generated, initialized/uninitialized duration | Original idle/memrate rows 94.69/94.59 and 6660/6958 means; all old replacements zero | R2 accepted E3 outputs. Include count/denominator and load identity; mean AoI ≠ receipt P99. |
| E3B input FIFO/latest with bridge latest: reception P99, skipped count and eligibility | 2026-10-12 diagnostic latest 254–267.9 vs FIFO 13821.6–15891 ms; six loaded exclusions; no accepted original loaded benefit | R2 accepted v2 E3B rows. Clean new results may be a first qualified measurement; original diagnostic contrast is not a clean baseline. |
| Physical E3 AoI/state occupancy | U and U2 2026-10-12 each 0/18; U2 HOLD 92.15/91.44% diagnostic only | “Not repeated” unless a separate E3_REAL campaign exists. PS1 and ALL cannot fill this row. |
| E4 F1–F5 × first and FAILSAFE × reason, MCU-local P50/P95/max ms | Preserve full historical B5/B6 and report Table 6; F4 original 2/5 and extra 5/9 must remain distinguishable, F5 old short-window 5/5 | R4 full new five requested repetitions/fault; report actual valid/attempted, not automatically 5/5. Compare matched timer references/reasons. New full F5 may change qualification relative to old short runs. |
| E4 mapped onset timing ms, false transitions and recovery/censoring | B6 old mapped cells, checked zero false transitions, no population false-trip bound | R4 new e4_runs/e4_faults + threshold source; mapping-fit ages/residuals, exposure and recovery qualification visible. |
| LA F1/F2/F4 marker→safe min/max ms | `content.md:229` historical ranges (F2 includes preflight) | R5 new fault groups, requested five each; report actual completed/usable captures and separate any preflight. Pi-local USB capture is a changed acquisition topology. |
| LA UART-byte→safe interval and matching-reference Δ µs | Deck Figure 11: 10/15 final HB, +47.5–67.6 µs in flagged collection | R5/R6 new CRC classification; do not assume 10/15 or old range. Record 8 MHz, 125 ns nominal sample period and unknown absolute calibration. Keep marker and UART references separate. |

Before filling a new cell, retain acquisition date, run ID, acquisition commit, binary/model hashes, board/PSU/kernel, actual scheduler/affinity/locking, requested/measured durations, load commands, power monitoring, validity rule and reason, and relevant clock-fit/event-loss evidence. Hash raw inputs and generated comparison outputs separately. Store originals under their existing dated directories and new evidence only under `results/2026-10-20_rerun/<run>/`; never merge raw samples across dates. The generated comparison must link each row to a specific new run and output file, since future directory names and results cannot be cited yet.

## 5. Verification and limits of this map

Source inspection establishes dependencies and available CLI interfaces. No experiment, deck builder, figure generator, DOCX builder, validator that writes output, or hardware tool was run during this audit. Embedded Python recipes are provided for future regeneration and syntax checked separately; they have not been exercised on absent 2026-10-20 data. Missing retained producers (manual Markdown tables, standalone sweep aggregation, student SVG crop/export, S1/PS1 packaging) are called out rather than represented as existing automation.


## Appendix A. Exact E4 point-to-raw-event inventory

Values below are the retained computed records from `submission/defense/qa/evidence.json`, generated at `build_evidence.py:190`. Each accepted row supplies two Figure 10 points and contributes to B5/B6 and report Table 6 as mapped above. Event references include the header as line 1. Invalid attempts contribute to denominators only. The raw files, not this retained computed JSON alone, are the primary evidence.

| Run directory (repository-relative) | Validity | First reason; local / mapped ms | Safe reason; local / mapped ms | Raw first / safe event file:line |
|---|---|---|---|---|
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r01` | VALID | 9; 175.287 / 83.342 | 3; 100.128 / 85.342 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r01/capture/state_events.csv:2` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r01/capture/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r02` | VALID | 9; 175.399 / 83.357 | 3; 100.574 / 85.357 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r02/capture/state_events.csv:2` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r02/capture/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r03` | VALID | 9; 175.535 / 83.561 | 3; 100.641 / 85.560 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r03/capture/state_events.csv:2` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r03/capture/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r04` | VALID | 9; 175.317 / 83.256 | 3; 100.165 / 85.256 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r04/capture/state_events.csv:2` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r04/capture/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r05` | VALID | 9; 175.041 / 83.209 | 3; 100.456 / 86.209 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r05/capture/state_events.csv:2` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F1-r05/capture/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r01` | VALID | 9; 175.709 / 83.715 | 3; 100.596 / 85.715 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r01/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r02` | VALID | 9; 175.206 / 83.113 | 3; 100.508 / 86.113 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r02/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r02/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r03` | VALID | 9; 175.099 / 83.151 | 3; 100.465 / 85.151 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r03/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r03/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r04` | VALID | 9; 175.325 / 83.226 | 3; 100.581 / 85.226 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r04/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r04/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r05` | VALID | 9; 175.086 / 83.014 | 3; 100.577 / 86.014 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r05/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F2-r05/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r01` | VALID | 9; 175.766 / 83.767 | 10; 475.766 / 383.741 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r01/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r02` | VALID | 9; 175.815 / 85.914 | 10; 475.815 / 385.888 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r02/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r02/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r03` | VALID | 9; 175.371 / 83.406 | 10; 475.371 / 383.379 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r03/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r03/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r04` | VALID | 9; 175.240 / 83.154 | 10; 475.240 / 383.128 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r04/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r04/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r05` | VALID | 9; 175.754 / 83.646 | 10; 475.754 / 383.620 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r05/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F3-r05/pipeline/state_events.csv:4` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r01` | INVALID | — | — | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r01/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r02` | VALID | 3; 100.931 / 87.871 | 3; 100.931 / 87.871 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r02/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r02/pipeline/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r03` | INVALID | — | — | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r03/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r04` | VALID | 3; 100.639 / 87.277 | 3; 100.639 / 87.277 | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r04/pipeline/state_events.csv:3` / `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r04/pipeline/state_events.csv:3` |
| `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r05` | INVALID | — | — | `results/2026-10-12_e4_faults/20261012T093526Z_e4/F4-r05/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_f5_stale/20261012T101949Z_f5/r1/F5-r01` | VALID | 9; 175.917 / 83.793 | 10; 475.917 / 383.786 | `results/2026-10-12_f5_stale/20261012T101949Z_f5/r1/F5-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f5_stale/20261012T101949Z_f5/r1/F5-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_f5_stale/20261012T101949Z_f5/r2/F5-r01` | VALID | 9; 175.343 / 83.186 | 10; 475.343 / 383.182 | `results/2026-10-12_f5_stale/20261012T101949Z_f5/r2/F5-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f5_stale/20261012T101949Z_f5/r2/F5-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_f5_stale/20261012T101949Z_f5/r3/F5-r01` | VALID | 9; 174.950 / 82.825 | 10; 474.950 / 382.819 | `results/2026-10-12_f5_stale/20261012T101949Z_f5/r3/F5-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f5_stale/20261012T101949Z_f5/r3/F5-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_f5_stale/20261012T101949Z_f5/r4/F5-r01` | VALID | 9; 175.596 / 85.563 | 10; 475.596 / 385.558 | `results/2026-10-12_f5_stale/20261012T101949Z_f5/r4/F5-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f5_stale/20261012T101949Z_f5/r4/F5-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_f5_stale/20261012T101949Z_f5/r5/F5-r01` | VALID | 9; 175.767 / 83.608 | 10; 475.767 / 383.603 | `results/2026-10-12_f5_stale/20261012T101949Z_f5/r5/F5-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f5_stale/20261012T101949Z_f5/r5/F5-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_f4_extra/20261012T102112Z_f4/r1/F4-r01` | VALID | 9; 175.229 / 56.344 | 3; 100.405 / 97.344 | `results/2026-10-12_f4_extra/20261012T102112Z_f4/r1/F4-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f4_extra/20261012T102112Z_f4/r1/F4-r01/pipeline/state_events.csv:4` |
| `results/2026-10-12_f4_extra/20261012T102112Z_f4/r2/F4-r01` | VALID | 3; 100.533 / 84.839 | 3; 100.533 / 84.839 | `results/2026-10-12_f4_extra/20261012T102112Z_f4/r2/F4-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f4_extra/20261012T102112Z_f4/r2/F4-r01/pipeline/state_events.csv:3` |
| `results/2026-10-12_f4_extra/20261012T102112Z_f4/r3/F4-r01` | VALID | 3; 100.525 / 85.625 | 3; 100.525 / 85.625 | `results/2026-10-12_f4_extra/20261012T102112Z_f4/r3/F4-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f4_extra/20261012T102112Z_f4/r3/F4-r01/pipeline/state_events.csv:3` |
| `results/2026-10-12_f4_extra/20261012T102112Z_f4/r4/F4-r01` | INVALID | — | — | `results/2026-10-12_f4_extra/20261012T102112Z_f4/r4/F4-r01/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_f4_extra/20261012T102112Z_f4/r5/F4-r01` | INVALID | — | — | `results/2026-10-12_f4_extra/20261012T102112Z_f4/r5/F4-r01/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_f4_extra/20261012T102112Z_f4/r6/F4-r01` | INVALID | — | — | `results/2026-10-12_f4_extra/20261012T102112Z_f4/r6/F4-r01/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r1/F4-r01` | INVALID | — | — | `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r1/F4-r01/run.json:1`; see power/echo/startup logs |
| `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r2/F4-r01` | VALID | 3; 100.556 / 87.767 | 3; 100.556 / 87.767 | `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r2/F4-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r2/F4-r01/pipeline/state_events.csv:3` |
| `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r3/F4-r01` | VALID | 3; 100.818 / 85.440 | 3; 100.818 / 85.440 | `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r3/F4-r01/pipeline/state_events.csv:3` / `results/2026-10-12_f4_extra/20261012T105039Z_f4b/r3/F4-r01/pipeline/state_events.csv:3` |

## Appendix B. Exact analyzer point inventory

These are all 15 Figure 11 points, from `submission/defense/qa/evidence.json` and `qa/LA_capture_key.md`. `L` expands as above. Every capture also supplies `capture.vcd` and `pi/F*/{run.json,pipeline/state_events.csv}`. Summary line identifies the original retained result; raw VCD is reanalyzed by `build_evidence.py:160`–`:168`. Marker-safe is the separate report metric, not Δ.

| Capture relative to L | Retained summary file:line relative to L | Last CRC-valid type | Δ µs | Marker-safe ms |
|---|---|---|---:|---:|
| `check_F2/F2-r01` | `check_F2/la_e4.csv:2` | HEARTBEAT | +67.024306 | 87.034125 |
| `run_F1/F1-r01` | `run_F1/la_e4.csv:2` | HEARTBEAT | +47.524306 | 92.691750 |
| `run_F1/F1-r02` | `run_F1/la_e4.csv:3` | HEARTBEAT | +67.524306 | 88.813750 |
| `run_F1/F1-r03` | `run_F1/la_e4.csv:4` | INFERENCE | -2922.600694 | 86.938250 |
| `run_F1/F1-r04` | `run_F1/la_e4.csv:5` | HEARTBEAT | +61.899306 | 95.541000 |
| `run_F2/F2-r01` | `run_F2/la_e4.csv:2` | HEARTBEAT | +47.899306 | 90.990000 |
| `run_F2/F2-r02` | `run_F2/la_e4.csv:3` | ECHO_REQ | -4937.225694 | 87.313750 |
| `run_F2/F2-r03` | `run_F2/la_e4.csv:4` | INFERENCE | -484.100694 | 89.196250 |
| `run_F2/F2-r04` | `run_F2/la_e4.csv:5` | INFERENCE | -2939.600694 | 86.947000 |
| `run_F2/F2-r05` | `run_F2/la_e4.csv:6` | HEARTBEAT | +67.274306 | 98.675750 |
| `run_F4/F4-r01` | `run_F4/la_e4.csv:2` | INFERENCE | -3053.100694 | 87.474750 |
| `run_F4/F4-r02` | `run_F4/la_e4.csv:3` | HEARTBEAT | +67.649306 | 82.851625 |
| `run_F4/F4-r03` | `run_F4/la_e4.csv:4` | HEARTBEAT | +65.649306 | 91.302000 |
| `run_F4/F4-r04` | `run_F4/la_e4.csv:5` | HEARTBEAT | +67.149306 | 85.442000 |
| `run_F4/F4-r05` | `run_F4/la_e4.csv:6` | HEARTBEAT | +61.649306 | 87.906125 |
