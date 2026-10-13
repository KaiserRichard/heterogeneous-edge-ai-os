# Progress deck review log

## Author repair round 1 — 2026-10-13, responding to REVIEW_1.md

**Final author verdict: PASS for the two reported blockers.** This is an author self-review; it does not replace an independent second review.

### Defects and resolutions

1. **BLOCKER: entire deliverable absent — FIXED.** Created `main.tex` and the 29-page `main.pdf`. Pages 1–2 orient the owner and map execution/data/control ownership; 3–4 cover dated implementation and integration; 5–7 distinguish host tests, earlier rig observations, clean/flagged measurements and v1/v2 validity. Pages 8–13 explain every retained campaign family (including the separately retained real-UART rerun), counts, exclusions and interpretation. Pages 14–15 cover access/wiring; 16–21 catalog production commands and outputs; 22–23 cover pitfalls; 24–26 provide ordered completion gates; 27 connects to roadmap A–F; 28 gives study pointers; 29 gives the first-session checklist.
2. **BLOCKER: no build, render, visual review or log — FIXED.** Added the generator, local preamble/study snapshot, build instructions, command companion, page index, full-page PNG renders and this review record. Kept `REVIEW_1.md` intact and `image-prompts/NEEDS.md` as `NONE`.

There were no separately numbered MAJOR or MINOR defects in REVIEW_1.md. No review item was rejected.

### Build and visual loop

- Generated 29 frames with `python3 build_deck.py`. The generator now reads only retained files in this deliverable; it does not depend on the external long-deck checkout.
- Built with `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` (exit 0), producing 29 pages.
- Also built into `/tmp/progress-repair-check` using `latexmk -xelatex -outdir=/tmp/progress-repair-check -interaction=nonstopmode -halt-on-error submission/progress/main.tex` from the repository root (exit 0).
- Final log scans for `Overfull|Underfull|Missing character|undefined|^!` produced **no matches** in either build. `rg` exit 1 here means no matches, not a failed TeX build.
- Initial Swift rendering hit the sandbox's inaccessible default compiler-cache path. Redirected Clang/Swift module caches to `/tmp`; the required repository `slides/render.swift` then successfully rendered all 29 pages at 1280 × 720. A local equivalent PDFKit fallback (`render.m`) also worked; no dependency was installed.
- Opened and inspected **all 29 pages at full size**, individually, in batches. The first inspection found page 2 map arrow labels overlapping boxes. Widened node spacing and split arrow labels; rebuilt, rendered and re-inspected page 2.
- Corrected the analyzer command (it has no `--outdir` option), escaped missing Unicode arrows into math glyphs, preserved literal `--` in copyable commands, clarified F3, and counted the long-deck section-divider pages when generating study pointers.
- Re-inspected final affected pages **2, 11, 12, 16, 17, 18, 19, 21, 22 and 28** at full size. Final changed-page inspection found no overflow, overlap or clipped/tiny text. Commands remain 12 pt; source captions use the family's smaller caption font.
- Exactly one figure: the TikZ system map, Figure 1, numbered/captioned and explained on page 2. No data plots or invented measurements were added.

### Evidence and command checks

- Counts and exclusions checked against `results/README.md` and `docs/STAGE_REPORT.md`: PTY 45/45 v1 versus 0/45 v2; cyclictest 15/15 each v1 versus 3/15 each v2; inference 21/24 accepted; input-latest 3/12; original real E3 0/18; original E4 17/25 planned entries (20 performed); extra F4 5/9 limited scope; separate F5 5/5 limited scope; analyzer 16 attempts / 15 captures with the incomplete F1 capture; all seven smoke summaries remain flagged.
- Direct CSV recount of retained PTY rows: E1 15, E2 18, E3 12; 45 stored-v1 valid rows. No analysis was rerun in results/.
- Direct recount of the separate real-UART rerun's `per_run.csv`: 18 rows, 0 MCU-local valid and 0 mapped valid, 18 live-power flags, 3 clock flags and 1 setting failure (overlapping). Page 11 reports this separately from the original campaign.
- v2 requirements, old report/analyzer chronology, reason-based transition timing, uncertain transit calibration and compiled-but-unflashed review fixes stay explicit. Observed maxima are not represented as bounds.
- Checked CLI definitions and shell usage for all documented production commands. Verified coverage of every `.sh`/`.py` under `tools/`, `scripts/` and `analysis/`, including regression scripts in `TOOL_CATALOG.md`: **zero uncatalogued scripts**. Experiment, provisioning, flashing and deployment commands were documented, not executed during this repair.
- Python generator parsed successfully; final frame count and PNG count both 29. Source changes and retained-result edits: none.

### Explicit limitations (not rejected defects)

Exact external Obsidian M-lesson filenames are absent from this permitted workspace. Page 28 uses checked long-deck page pointers and the retained learning-plan modules, and labels exact external paths UNKNOWN; no personal vault was accessed. PR state is the supplied brief's snapshot, not a live remote check. Hardware verification, new measurements and merging PR #6 are next-step gates, not work claimed to have been performed during this deck repair.

## Author repair round 2 — 2026-10-13, responding to REVIEW_2.md

**Author verdict: PASS for the six numbered repair requests.** Self-review, not an independent review. No BLOCKER was reported; both MAJORs and all four MINORs were addressed. No item was rejected.

1. **MAJOR 1 — FIXED:** page 11 now reports 18 attempts, zero accepted and six pipeline failures alongside overlapping 18 power / 3 clock / 1 setting flags. Six attempts never opened measurement windows because FRESH timed out. Pages 25/29 require reset/FRESH pilots including the two loaded FIFO-input cells. Root cause remains UNKNOWN; PSU replacement alone is not a completion gate.
2. **MAJOR 2 — FIXED:** added `REARM_SETUP.md` with Pi-to-Mac SSH preparation, UNKNOWN deployment values, retained helper template using the actual OpenOCD reset command, fatal status propagation, intended-board/reset checks and separate FRESH/window verification. Page 19 and command companion point to it. Template is documented, not installed or rig-verified.
3. **MINOR 3 — FIXED:** pages 14/16 identify bootstrap as initial provisioning requiring apt network access. README provides an installed-package/UART audit and explains that wheels/bundles do not supply apt dependencies.
4. **MINOR 4 — FIXED:** page 23 labels retained accepted fault observations MEASURED, preserves distinct reference intervals and excludes bounds/threshold interpretation. Proposed 5 V/5 A supply is separately PLANNED.
5. **MINOR 5 — FIXED:** page 20 and TOOL_CATALOG use `stm32/firmware/build/firmware.elf`.
6. **MINOR 6 — FIXED handoff:** page 28/README explicitly assign the pending owner lookup and mechanism-to-note title/path completion gate. Exact external M-lessons remain UNKNOWN because no supplied/authorized notes identify them; no personal vault was searched.

Validation: generator Python syntax parsed; embedded helper passed `bash -n`. Direct CSV recount confirmed 18 attempts and six pipeline failures; six retained pipeline logs contain the specified FRESH timeout. Generated 29 frames and rebuilt with `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` (exit 0). Final log scan `Overfull|Underfull|Missing character|undefined|^!` had no matches. Swift PDFKit renderer with redirected module caches exited 0, producing 29 PNGs. Inspected changed pages **11, 14, 16, 19, 20, 23, 25, 28, 29** individually at 1280 × 720: no visible clipping, overlap, overflow or tiny body text. Other pages retain round 2's independent full-page inspection. Figure 1 is unchanged; no new figures/images required.

Only submission/progress deliverable files were edited. No provisioning, SSH configuration, flashing, hardware reset, new measurement or result reanalysis was performed. Hardware helper deployment/pilots and owner M-lesson lookup remain explicit next-step gates, not rejected review items.

## Author repair round 3 — 2026-10-13, responding to REVIEW_3.md

**Author verdict: PASS for both numbered defects.** Self-review, not an independent review. No BLOCKER was reported; the MAJOR and MINOR were fixed. No item was rejected.

1. **MAJOR 1 — FIXED:** page 3 distinguishes the early roadmap snapshot at `a22fa2b` from later 10 October implementation: A2 `e456e6b`, integer-offset/zero-spread review fix `e3b81ab`, and A3/A4. Portable clock math remains distinct from open independent physical clock calibration. The full Linux pipeline is correctly dated 11 October (`fc37e3b`). Commit dates and subjects were checked in retained read-only git history. Updated the generator and regenerated `main.tex`.
2. **MINOR 2 — FIXED:** page 20 and `TOOL_CATALOG.md` now require Mac-owned ST-LINK / `st-flash`, FX2/sigrok, Mac-to-Pi SSH and confirmed `LA_PI` / `LA_PI_REPO` values. Checked `tools/la/la_e4.sh`: it performs local `st-flash reset` and launches the Pi campaign with `--rearm-command true`. The Pi-to-Mac reset helper remains a prerequisite for page 19 campaigns.

Validation: Python generator syntax passed; regenerated 29 frames. `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` in this folder exited 0 and rebuilt the 29-page `main.pdf`; `build-output.txt` retains build output. Final LaTeX log scan for `Overfull|Underfull|Missing character|undefined|^!` had no matches. Required repository Swift renderer, with Clang/Swift module caches redirected to `/tmp/progress-r3-*`, exited 0 and rendered all 29 pages to `preview/`. The local PDFKit fallback also rendered successfully while Swift compiled. Inspected final changed pages **3 and 20** individually at full 1280 × 720 resolution after Swift rendering: readable body and commands, no clipping, overflow or overlap. Unchanged pages retain the independent round-3 full-page inspection. Figure 1 is unchanged; no new image or data figure was required.

All retained edits and regenerated artifacts are within `submission/progress/`. No code/results edits, provisioning, remote actions, flashing, resets or measurements were performed.
