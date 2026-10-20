# Defense build and self-review log

Scope: D_DEFENSE.md and COMMON.md; only submission/defense changed. The repository academic-beamer-deck skill and study-deck visual system were reused. No new illustrations needed; NEEDS.md was written before slide construction. No delegation or hardware experiment was used.

## Round 1 — initial build and evidence audit

- Built with `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`: 30 pages, no LaTeX errors, all references resolve after the second pass.
- MAJOR, page 27: local E4 backup material produces a 9.76 pt overfull vertical box. Fix pending: replace the three-item explanation with concise parallel text and reduce redundant spacing, retaining body size.
- Source validation: reason-selected E4 table values reproduce STAGE_REPORT.md to the displayed precision. Original E4 stored local-first values for F1/F2 used the wrong reference; plotting uses raw reason 9 and last accepted inference. All original, extra F4 and F5 denominators retain their different scopes.
- Analyzer raw recomputation: all 15 supplied interval rows reproduced; protocol-CRC decoding gives 10 HEARTBEAT final frames and five different final-frame references. Matching differences 47.524–67.649 µs. No FLAGGED collection promoted to wholly clean.
- Timing: 21 scripts; targets recomputed to exactly 1,020 s. Cumulative time column regenerated to agree.
- Renderer first attempt could not write default Swift cache under the sandbox; rerun with Swift and Clang module caches inside qa/swift-cache. This is a tooling-cache issue, not a PDF error.

Visual review and corrected final verdict will be appended after full-page inspection.

## Round 1 — full visual inspection findings

Opened **every page 1–30 individually at 1280×720**, not only thumbnails.

1. MAJOR, page 8: state-edge labels crowded the state boxes. Increased horizontal spacing and moved labels above the arrows.
2. MAJOR, page 10: missing paragraph end after the table allowed “V2” to begin beside it. Added explicit paragraph boundaries to tables.
3. MAJOR, page 12: the two-thread inference annotations overlapped. Placed idle values below and loaded values above their points.
4. MAJOR, page 17: the shared analyzer axis obscured the 47–68 µs matching subset; long axis text clipped. Split into matching-reference microseconds and different-reference milliseconds panels, with short labels and a unique F2-check identifier.
5. MAJOR, page 27: vertical overflow confirmed visually. Replaced the long three-item reason explanation with two concise lines.
6. MINOR, most content pages: theme alignment left a large empty band above the content. Set explicit top alignment and anchored takeaways at the bottom, without shrinking fonts.

## Round 2 — corrected build, render and complete self-review

- Rebuilt with XeLaTeX: **30 pages; zero errors, zero Overfull/Underfull boxes, zero missing characters, zero unresolved references**. Log scan returned no matches.
- Rendered the complete PDF using the required repository Swift renderer with sandbox-local module caches.
- Opened **all 30 corrected pages individually at full 1280×720 size**. All Round 1 readability and layout defects are fixed. Body remains 12 pt; captions use the shared small style; no per-frame scaling or scriptsize fit hacks.
- All 11 figures have unique increasing numbers, captions directly beneath, and explicit body references. Reused illustration W01 plus three exact TikZ diagrams and seven data-generated vector plots; none dropped. NEEDS.md remains NONE.
- Confirmed every shown numeric statistic against the retained summaries / stage report and computed E4 records. The eight backup slides cover protocol, clock math, threshold rationale, validity, full local/mapped E4, claim map and tools/branch provenance.
- Evidence audit retains v1/v2 limitations, PTY scope, accepted inference subset and exclusions, provisional thresholds, source-age versus heartbeat reference times, differing F4/F5 exposure, FLAGGED input-policy and physical collections, and compiled-but-not-reflashed firmware fixes.
- Scripts allocate **1,020 seconds = 17:00** across 21 main slides; backup questions are outside the allocation.

## Final pass — semantic cross-check and final rendering

- Page 8: added heartbeat-timeout eligibility from HOLD as well as FRESH, matching the raw F1/F2 HOLD→FAILSAFE reason-3 sequence. A first TikZ coordinate expression failed compilation; corrected it with a named coordinate, rebuilt with halt-on-error, and repeated rendering. Final log is clean.
- Pages 18/26: qualified the original physical E3 count and included the retained later 18-run rerun. Both have 0/18 clean accepted runs; later MCU-local validity is independent of mapping but power exclusions persist. Updated CLAIMS.md and source manifest accordingly. No late physical observation is promoted to clean evidence.
- Re-rendered all pages. Compared SHA-256 PNG hashes with Round 2: **only pages 8, 18 and 26 changed**; all other 27 reviewed pages are pixel-identical. Reopened all three changed pages individually; clear labels, no clipping or overlaps. Inspected the final contact sheet (`qa/contact-sheet.png`) for story and visual continuity.
- `check_deck.py`: **PASS** — clean log; 30 pages; 11 uniquely numbered/referenced figures; 21 scripts = 1,020 s; **151 source hashes unchanged**; E4 27/34 retained performed attempts accepted in stated scopes; analyzer 10/15 matching references.
- Presentation and source stay entirely in submission/defense. Git branch/index/commits, code, results and third_party were not changed. No hardware was accessed or reflashed during this task.

### Final page register

| Page | Title | Verdict |
|---:|---|---|
| 1 | Freshness and Independent Supervision | PASS |
| 2 | Motivation | PASS |
| 3 | Problem and research questions | PASS |
| 4 | System architecture | PASS |
| 5 | Scheduling and contention profiles | PASS |
| 6 | IPC and buffering policy | PASS |
| 7 | Clocks and freshness | PASS |
| 8 | Independent supervisor | PASS |
| 9 | Experimental method | PASS |
| 10 | Run validity and rule versions | PASS |
| 11 | Timer wake-up under contention | PASS |
| 12 | Inference baseline | PASS |
| 13 | E1: contention reaches the data path | PASS |
| 14 | E2: runtime tuning has limits | PASS |
| 15 | E3: replace at the overloaded queue | PASS |
| 16 | E4: interpret the transition reason | PASS |
| 17 | Independent analyzer cross-check | PASS |
| 18 | Limitations | PASS |
| 19 | Conclusion and contributions | PASS |
| 20 | Future work | PASS |
| 21 | References | PASS |
| 22 | Backup divider | PASS |
| 23 | B1: UART protocol frame | PASS |
| 24 | B2: Clock math and measurement boundaries | PASS |
| 25 | B3: Threshold rationale and rearm | PASS |
| 26 | B4: Full run-validity inventory | PASS |
| 27 | B5: Full E4 table, MCU-local timing | PASS |
| 28 | B6: Full E4 table, mapped fault-onset timing | PASS |
| 29 | B7: Claim-to-evidence map | PASS |
| 30 | B8: Tools and branch map | PASS |

**Final verdict: PASS (build and self-review).** No unresolved artifact defects or missing illustrations. The declared experimental and hardware limitations remain visible and are not treated as artifact defects.


## Round 3 — independent REVIEW_1 remediation (13 October 2026)

The independent review superseded the earlier self-review: three MAJOR interpretation/label defects and three MINOR method/readability defects, with no BLOCKER build defect. Read PROJECT.md, D_DEFENSE.md, COMMON.md, REVIEW_1.md and the referenced academic Beamer guidance before editing. All six numbered items are accepted and resolved; **no item rejected or deferred**. Page numbers below are physical PDF pages.

| REVIEW_1 item | Severity / pages | Resolution |
|---|---|---|
| 1 | MAJOR / 15, 19, 29 | Preserve MEASURED for AoI, zero bridge replacements and completion intervals. Explicitly label upstream backlog INFERRED in E3, conclusion and claim map. State clean input-policy benefit UNKNOWN; loaded E3b remains FLAGGED. Split measured observations from the inferred explanation in the backup table; align SPEAKER_NOTES.md, CLAIMS.md and README.md. |
| 2 | MAJOR / 17 | Define Δ = L − M, positive when L is longer. L: analyzer last physical UART byte end → both PA5/PB5 low. M: MCU last accepted heartbeat receipt → FAILSAFE STATE_EVENT timestamp. Axes plot Δ in µs/ms. Explain timestamp placement, reception/output delay and clock effects; endpoints remain distinct even for HEARTBEAT. Absolute calibration remains UNKNOWN; speaker notes explicitly reject interpreting this residual as echo accuracy or isolated decision-to-output delay. |
| 3 | MAJOR / 29 | Analyzer row explicitly reads CALCULATED; collection FLAGGED. The adjacent scope explains calculation from retained MEASURED captures and that frame-type matching does not establish run validity. No collection-wide promotion. |
| 4 | MINOR / 5, 9, 11–15 | Main method slide defines CPU compute / Stream sequential arrays / Cache 2 MiB working set / Memrate read-write traffic and placement: CPU+Memrate on 2/3, Stream+Cache on 2, timer/inference on 0, source/bridge on 1. Keep model-only affinity 0–3 distinct. Exact timer commands and pipeline exact_load paths/worker construction are in CLAIMS.md; source manifest now covers these retained inputs. |
| 5 | MINOR / 5, 14 | Explicit P0 source/bridge: CPU 1, unlocked; P1 source/bridge: FIFO 60/70, CPU 1, locked. Both inference processes: OTHER, CPU 0, unlocked. Notes/register retain measured 0 versus 2928 KiB. E2 explicitly compares profiles changing priority and locking together. |
| 6 | MINOR / 16–17 | Enlarge E4 panel titles, ticks, axis labels and samples. Color/shape key distinguishes heartbeat reason 3 / inference HOLD 9 / inference FAILSAFE 10; wider horizontal offsets expose close samples without changing their times. Annotate F4 six heartbeat first events versus one HOLD. Enlarge analyzer typography and replace rotated IDs with simple capture indices; generated qa/LA_capture_key.md retains every full path, frame type and signed value. |

### Rebuild and verification

- Regenerated all seven vector plots and both E4 tables using build_evidence.py. Reanalysis reproduces **27/34** retained E4 attempts accepted in their stated scopes; **15 analyzer captures, 10 matching references**, matched Δ **+47.524–67.649 µs**. qa/evidence.json and both qa/E4_*.tex tables are byte-identical to the pre-fix artifact. All numeric findings retain their original qualifications.
- Added 13 method/profile/qualification source inputs to the original 151-entry manifest; **164/164 SHA-256 hashes match**. Source data, application/firmware code, results and third_party are read-only throughout this round.
- First correction pass exposed an expanded claim-map vertical overflow and a matplotlib tick-label API error/missing arrow glyph. Shortened the table label while spelling out its qualification below; supplied explicit tick labels and used a supported axis string. Re-ran evidence generation and rebuilt after correction. No figure or evidence item was dropped to fit.
- Final command from submission/defense: `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`. **30 pages; zero errors, Overfull/Underfull boxes, missing characters or undefined references.** Final build output: qa/build-review1.txt. No per-frame font reduction; body remains 12 pt.
- Rendered all pages using the repository slides/render.swift with deliverable-local Swift/Clang caches. Render output: qa/render-review1.txt. Opened **every page 1–30 individually at original 1280 × 719 size**, including every changed page; no clipping, overlap or unreadable changed labels. Refreshed and inspected qa/contact-sheet.png for continuity.
- Final polish moved the E4 legend away from its panel titles and clarified the method-page reference. Rebuilt and rendered again; PNG hashes show only pages **5 and 16** changed relative to the inspected first correction render. Reopened both at original size. All other inspected pages are pixel-identical to that render.
- Relative to the independent-review baseline, final changed pages are **5, 9, 14, 15, 16, 17, 19 and 29**; the other **22 pages are pixel-identical**. Baseline/current PNG manifests: qa/review1-baseline-preview-hashes.json and qa/review1-preview-hashes.json; final-preview-hashes.json now identifies the current render.
- Final check_deck.py: **PASS** — clean log; 30 pages; 11 uniquely increasing, numbered and referenced figures; 21 main scripts totaling **1,020 s = 17:00**; 164 source hashes match; E4 27/34 and analyzer 10/15. Output: qa/check-review1.txt.
- Only submission/defense was written. No hardware run, firmware build/flash, delegation, external communication or Git branch/index/commit mutation. Power exclusions, v1/v2 missing evidence, provisional thresholds, differing fault scopes and compiled-but-not-reflashed firmware fixes remain visible.

**Round 3 verdict: PASS (build, evidence checks and self-review). All REVIEW_1 MAJOR and MINOR artifact defects resolved; no rejected items.** REVIEW_1.md is preserved as the independent historical review; this remediation is not a new independent approval or hardware qualification.

## 20 October 2026 — additive re-run integration

Added five generated slides immediately after the original analyzer slide (PDF
pages 18–22). Visually inspected all five rendered pages: tables, firmware hash,
reference equations, pending slots, scopes and takeaways fit the existing canvas.
The original eleven figure labels and seven plot files remain unchanged. The
expanded notes allocate 1,200 s across 26 main slides; backup pages remain untimed.

Validation: XeLaTeX/latexmk produced `main.pdf`, 35 pages, with no overfull,
underfull, missing-character or undefined-reference diagnostics. The existing
Swift renderer produced 35 preview PNGs. `check_deck.py` passes with the expanded
page/timing checks, unchanged historical 164-source manifest and separate rerun
source hashes. Historical E4 27/34 and analyzer 10/15 checks still apply solely
to the original evidence, not to the new 25/25 and 15/15 collections.

The DOCX ZIP/XML, styles, relationships, cached TOC and deterministic rebuild
checks pass, as does the Vietnamese prose-style check. No Word pagination was
performed; the older 20-page target remains unverified after adding section 5.5.
Pre-existing DOCX validator assumptions were aligned with the retained builder:
five media files including the logo, front-matter paragraph page breaks, and
16 × 10 cm maximum figure bounds. Original word-budget checks remain scoped to
the preserved original text; six new tables bring the content-table count to 13.

A temporary comparison fixture verified that a future E1 value and n/N populate
both documents; the real pending inputs were restored afterward. Removing the
additive blocks recovers original `main.tex` and `content.md` byte-for-byte.
No acquisition, hardware, SSH, push or commit was performed.

### Full pipeline evidence refresh — 20 October 2026

Reviewed all five additive re-run frames and report section 5.5 against the
retained comparison (E1–E3B: 57/57 accepted). E2 now compares matching memrate
conditions and includes the new stream condition without inventing an original
counterpart. The E1 ranking changed from memrate/cache to memrate/stream;
cache was not repeated in E2. Unmatched-condition status is preserved rather
than converted to pending. Pipeline availability and paired interpretations
are generated from the comparison, including explicit missing-evidence text.

The pipeline frame distinguishes PS1 physical UART from PTY experiments and
retains MEASURED evidence wording. E1 shows contention reaching delivery;
E2 tuning leaves substantial backlog; E3 bridge policy leaves upstream backlog;
E3B now has separate valid loaded input-policy evidence, without treating the
invalid original loaded runs as a clean comparison. The setup, timer, E4 and
analyzer statements remain consistent with the retained full evidence.

Ran build.sh and forced latexmk -g, check_deck.py, build_docx.py,
validate_docx.py and style_check.py successfully. Regression tests cover both
complete and missing pipeline parts. Rendered the deck with the repository
Swift renderer and visually inspected re-run pages 18–22: no clipping,
overlap or content extending into the footer. DOCX structural and deterministic
build validation passes; Word pagination was not rendered. Original snapshot
slides and source data are preserved. No hardware, SSH, commit or push.
