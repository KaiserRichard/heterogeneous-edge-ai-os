# Report review log

## Scope and sources
- Read PROJECT.md, repository instructions, R_REPORT.md and COMMON.md before authoring.
- Wrote image-prompts/NEEDS.md (`NONE`) before authoring. No new raster illustration needed.
- Reused the academic-deck palette, Avenir Next/Menlo fonts and missing-asset convention; article structure follows the report brief.
- Report-only writes. No acquisition, firmware flashing, code edits or changes to retained results.

## Round 1 — build and evidence audit
- XeLaTeX built, but found overfull body lines, justified narrow appendix columns, a duplicate title-page PDF anchor and unwanted pagination.
- Fixed paragraph line-breaking, ragged appendix columns, PDF page anchors and removed the optional contents page.
- Found F1 pipeline logs stop before fault events; changed extraction to passive capture logs. Recomputed intervals now agree with the reason-based stage report.
- Replaced reporting commit identifiers in the evidence table with acquisition metadata where recorded; unknown image identities remain explicit.
- Corrected campaign entry-point filename in reproduction commands.
- Renderer initially attempted a disallowed user cache. Redirected Swift module cache inside the report folder.

## Round 2 — pending final render and page inspection
- Rebuilt after layout/evidence corrections. Final checks and page-by-page verdict follow below.

## Round 2 — full-size visual review
Inspected all 24 rendered pages at 1280 × 1810 pixels, individually (not only thumbnails).

| PDF pages | Content | Review |
|---|---|---|
| 1 | Cover | Found rule/subtitle sharing a line; fixed in round 3. |
| 2–5 | Abstract, introduction, background | Readable text, equations and citations; PASS. |
| 6 | Architecture / protocol | Found crowded datagram labels; fixed in round 3. |
| 7–9 | Supervisor and implementation | Tables, equation and ownership description clear; PASS. |
| 10–11 | Method and validity | Counts, scopes and v1/v2 distinction legible; PASS. |
| 12–14 | Timer, inference, E1/E2/E3/E3b | Labels and units readable; flagged rows explicitly excluded; PASS. |
| 15–17 | Real UART, faults, bring-up/analyzer | FLAGGED status, reason-specific references and short-window limits retained; PASS. |
| 18–20 | Discussion, conclusion, references | No clipping; limitations and future-work status explicit; PASS. |
| 21–24 | Evidence, reproduction, OS mapping | Long paths wrap within columns; commands readable; PASS. |

## Round 3 — final build and review
- Corrected cover rule with an explicit paragraph break.
- Widened architecture spacing and used IPC labels, with Unix datagrams identified in the caption.
- Rebuilt using `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` and rendered with the required shared Swift renderer (local module cache).
- Renderer reports **24 pages**: 20 main pages including cover and references, plus four appendix pages. Printed numbering excludes the cover.
- Reopened pages 1 and 6 at full size: PASS. Compared PNG SHA-256 hashes against round 2: only these two pages changed; the other 22 inspected pages are byte-identical.
- Final LaTeX scan (`Overfull|Underfull|undefined|Missing character|^!`) returns **no matches**. No LaTeX errors, overfull/underfull boxes, missing glyphs or undefined references/citations.
- One numbered architecture figure, referenced and explained. Eleven data-generated result tables; 17 tables total including design/method/appendices. No unused raster figures or unresolved placeholders.
- Evidence generation rerun is byte-for-byte deterministic. Source manifest covers 298 files, including the 60 table inputs and acquisition metadata. No source dataset is rewritten.
- F1 passive-capture extraction reproduces 175.317/175.535 ms HOLD P50/max and 100.456/100.641 ms heartbeat FAILSAFE P50/max. E3b/real-UART/F5 raw calculations agree with the stage-report values.
- Appendix A uses recorded acquisition commits where found and does not equate them with flashed image identity. Full provenance is in `generated/acquisition-commits.json`.

**Final verdict: PASS.** Full build → render → inspect → fix → rebuild → inspect loop complete. Owner-fill names, IDs and lecturer remain intentional cover macros. Hardware qualification limits are documented, not unresolved report defects.

## Round 4 — resolve independent REVIEW_1 (13 October 2026)

Accepted all six findings: two MAJOR and four MINOR; REVIEW_1 reported no BLOCKER. No item rejected or deferred. This round supersedes round 3's report verdict in light of the independent review.

| REVIEW_1 item | Resolution | Final PDF pages (cover counted) |
|---|---|---|
| 1 — MAJOR, missing E3 threshold outcomes | Added generator-backed Table 9 from retained E3_table.csv, with strict >100/>150 ms violation seconds and reception misses/denominators. Explained idle 26.85/26.79 s above 100 ms despite zero misses of 602 receptions, and retained nonzero >150 ms times and loaded counts. Preserved v1 status, per-run medians, initialized-time integration, measurement-window exclusion of drain, and inclusion of drain in reception denominators. | 11, 14 |
| 2 — MAJOR, causal overclaims in course mapping | Appendix C now states the observed v1 latency increase; shared-memory interference and broad masking as a receive hazard are INFERRED. Source changes address the suspected hazard; final hardware verification remains UNKNOWN. | 25 |
| 3 — MINOR, DMA arithmetic | Corrected nominal full-ring capacity to 2048 × 10 / 921600 = 0.022222… s = 22.22 ms; remains CALCULATED, not a service guarantee. | 9 |
| 4 — MINOR, quantile scope/endpoint | Limited median-of-per-run wording to aggregate latency tables. E3b Table 10 explicitly gives per-run input-to-software-reception age, timestamp subtraction in ns divided by 10^6, nearest-rank selection, CRC-valid inference receptions and shutdown drain. All six loaded rows remain FLAGGED. | 11, 15 |
| 5 — MINOR, scientific notation | Generator expands retained E1/E2/E3 scientific notation with Decimal, preserving rounded values (13980, 15120, 13660, etc.) in milliseconds. | 13–14 |
| 6 — MINOR, reproduction directory | B.2 explicitly requires repository root and begins with cd ../.. after B.1. Tightened nearby build prose to keep the appendix on one readable page. | 24 |

Validation and layout loop:
- Ran `sh submission/report/build.sh`: evidence generation, `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`, shared Swift renderer with report-local module cache.
- First render had 26 pages: the added reproduction guidance spilled a short paragraph onto an extra page. Tightened Appendix B prose, gave E3b its own numbered subsection/page, rebuilt and re-rendered to **25 pages** (21 including cover/references, four appendix pages). The brief's page count is a guide; the extra results page keeps restored evidence readable.
- Inspected every changed/new page individually at 1280 × 1810: **9, 11, 13–25**. Checked the restored tables, arithmetic, captions, updated table/section references, appendix paths and course mapping. No clipping, overlap, tiny text or unresolved placeholders found.
- Pages **1–8, 10, 12** are byte-identical to the previously fully inspected render. Before/after hashes are retained in `preview-hashes-before-review1-fixes.json` and `preview-hashes-round4.json`. Removed stale page-26.png from the intermediate render.
- Final LaTeX log has no errors, overfull/underfull boxes, undefined references/citations or missing-character warnings.
- Regenerated all **12 result tables** and metadata a second time; all generated files match byte-for-byte. The manifest still covers **298 source inputs**. Checked restored E3 values against the retained CSV and stage report; checked selected E3b inference rows have crc_ok=1; numeric E3b outputs remain unchanged.
- Writes stayed in submission/report. No retained data/code edits, target experiments or firmware flashing. Hardware limitations remain unchanged.

**Round verdict: PASS for all six REVIEW_1 corrections and report build/layout.** Hardware qualification is not claimed.

## Round 5 — resolve independent REVIEW_2 (13 October 2026)

Accepted all three findings: one MAJOR and two MINOR; no BLOCKER was reported. No item rejected or deferred.

| REVIEW_2 item | Resolution | Final PDF pages (cover counted) |
|---|---|---|
| 1 — MAJOR, causal claim in synthesis | §7.1 now identifies elevated latency under cross-core memrate stress despite P1 as MEASURED under v1. Shared-memory interference is explicitly INFERRED and not causally isolated, consistent with the stage report and Appendix C. | 19 |
| 2 — MINOR, partial-frame completion | §4.1 describes immutable partial submissions, the 2 ms budget, and abandonment through queued-output flush, expired accounting, sequence advance and quiet interval. Explains bounded submission delay/loss accounting and distinguishes current software from historical acquisitions. Checked against hea_bridge.c and uart_budget.h. | 8 |
| 3 — MINOR, missing later UART rerun | Table 3 distinguishes original U from later U2. A generated FLAGGED note inventories U2's 18 attempts, zero accepted, 18 live-power exclusions and six pipeline failures. Appendix A supplies its exact root, summary/config paths and cleanup-versus-acquisition identity distinction. U2 diagnostic ages/state durations are explicitly excluded from the presented comparisons, not pooled with U or used to validate clean HOLD occupancy. | 10, 16, 22–23 |

Validation and layout loop:
- Ran `sh submission/report/build.sh`: evidence generation, XeLaTeX through latexmk, then the shared Swift renderer with report-local module cache. Final PDF remains **25 pages**.
- Inspected all six changed pages individually at 1280 × 1810: **8, 10, 16, 19, 22, 23**. No clipping, overlap, tiny text or unresolved references found. Added a paragraph break before the separate rerun note, rebuilt/re-rendered, and reopened page 16; PASS. Only page 16 changed in that final layout adjustment.
- The other 19 pages are byte-identical to the previously inspected render. Before/final hashes are retained in `preview-hashes-before-review2-fixes.json` and `preview-hashes-round5.json`.
- Final LaTeX log scan found no errors, overfull/underfull boxes, undefined references/citations or missing-character warnings.
- Regenerated all 12 result tables, the new rerun note and metadata again: byte-identical. The source manifest now covers **301 inputs**, including the later rerun's per-run summary, campaign configuration and README. Acceptance/exclusion counts derive from per-run flags, not the README's generic MEASURED heading.
- All writes stayed in submission/report. No retained data/code changes, target experiments or flashing; hardware qualification is not claimed.

**Round verdict: PASS for all three REVIEW_2 corrections and report build/layout.**
