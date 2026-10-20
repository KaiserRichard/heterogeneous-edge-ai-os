# Defense deck

English OS-course defense for a 15–20 minute talk: 21 main slides, one Backup divider, and eight backup slides (30 PDF pages). The target script is 17:00 in SPEAKER_NOTES.md. Sources are the retained final-code results, not the historical roadmap's completion markers.

Open `main.pdf` for presentation and submission. `main.tex` uses the copied study-deck preamble, Avenir Next / Menlo, the same palette, canvas and figure system. W01.jpg is the reused study-deck motivation illustration; no new bitmap is required (`image-prompts/NEEDS.md` = `NONE`). Missing illustrations compile as visible placeholder boxes.

From this repository root, on the **macOS host**:

```sh
python3 submission/defense/build_evidence.py
cd submission/defense
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
mkdir -p qa/swift-cache
SWIFT_MODULECACHE_PATH="$PWD/qa/swift-cache" \
CLANG_MODULE_CACHE_PATH="$PWD/qa/swift-cache" \
swift ../../slides/render.swift main.pdf preview
python3 check_deck.py
```

Dependencies already used here: Python 3 with matplotlib and Pillow, TeX Live with latexmk/XeLaTeX/moloch, macOS Swift/PDFKit/AppKit, Avenir Next and Menlo. The renderer is the repository's existing renderer. Its cache variables keep compilation inside this deliverable under the sandbox. First rendering can spend several minutes compiling system framework modules.

`build_evidence.py` regenerates seven vector plots and two E4 tables, checks accepted-run counts, recomputes reason-based local transitions, reanalyzes all 15 analyzer VCDs, and CRC-decodes the final UART frame to check the 10/15 matching references. Original E4 mapped values and acceptance follow retained summaries; extra F4/F5 scopes follow the stage report. It keeps computed records and SHA-256 input manifests in `qa/`, including the applied P0/P1 settings and retained contention commands. `qa/LA_capture_key.md` maps the analyzer plot’s short capture indices to the full raw capture paths. It writes only in this folder and does not contact or exercise hardware.

`CLAIMS.md` maps every slide to sources and qualification. `REVIEW_LOG.md` records defects, fixes and final visual review. `check_deck.py` checks the final log, timing, figure references, sources, and page counts; it complements visual inspection.

Preserved limitations: v1/v2 evidence differences; power-invalid diagnostics; PTY vs physical UART; small samples; differing fault reference events and short-window exposures; no calibrated worst-case bound or actuator safety; final firmware review fixes compiled but not reflashed on this rig. Upstream backlog is INFERRED from measured queue observations; clean input-policy benefit remains UNKNOWN and E3b remains FLAGGED. The analyzer comparison is calculated from retained physical observations in a FLAGGED collection: Δ = (last physical UART byte end → both state GPIOs low) − (last accepted heartbeat receipt → FAILSAFE STATE_EVENT timestamp). Positive means the analyzer interval is longer. The residual includes timestamp placement, reception/output delays and clock effects; absolute calibration remains UNKNOWN. Matching frame types do not establish run validity. Generic UNVERIFIED ON HARDWARE strings remain in raw evidence.

Source inventory: source code snapshot `5e3f461`, branch `feat/os-submission`, based on the final release; git index, branches and commits were not changed.

Dated update (20 October 2026): five additive slides follow the original analyzer
slide. The deck now has 26 main slides and 9 backup pages (35 pages); the expanded
speaker script totals 20:00. All original slide bodies, plot inputs and numbers
remain the earlier snapshot. Its limitations and future-work statements retain
that historical scope. The new frames show the later S1 flash and PS1 link evidence.

Rebuild the update with `submission/defense/build.sh` from the repository root;
it refreshes the generated fragment before XeLaTeX. For refreshed E1–E3B evidence,
set `RERUN_COMPARE_DIR` to the new output of `tools/rerun/build_rerun.py` (see its
README). Do not regenerate the historical evidence merely to refresh this update.
The new source hashes are separate in `qa/rerun_2026-10-20_sources.json`.
