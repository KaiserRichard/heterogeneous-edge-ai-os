# Builder round 1 — layout pass

No `slides/review/latest.md` existed at the start of this round. Read `PROJECT.md`, `LAYOUT_BRIEF.md`, `RESTRUCTURE_SPEC.md`, and `REVISION_V4.md` before editing.

- Established 12pt normal body text, 1.12 line spacing, and global itemize spacing (0.55em / 0.25em), removing local overrides and condensed captions.
- Added `\fig[height]{file}{caption}` with an image-width minipage, centred small captions, automatic figure numbers, and linked references. Shortened captions to at most two lines and converted numeric source references to LaTeX citations.
- Rebalanced the cover with a huge two-line title, Large subtitle, teal rule, equal-width/equal-height columns, normal-sized member names, and Large group/adviser/class lines.
- Rebuilt the throughput slide with full-width definitions, aligned explanation/image columns, and a bottom takeaway. Replaced all arrow-headed conclusion bullets with navy-tinted boxes and a 3pt teal rule.
- Folded cgroups and RQ definitions into their sentences. Split dense sections into continuation slides rather than reduce body fonts; enlarged meaningful illustrations and added native diagrams to sparse continuations. Final deck: 46 pages, including six dividers and two reference pages.
- Redrew the supervisor transitions with horizontal, separated labels. HOLD → FAILSAFE now reads “Hết thời gian chờ”; FRESH → FAILSAFE alone reads “Mất heartbeat”. “Giữ chốt” is clear below FAILSAFE, and explicit dashed rearm returns to INIT. This corrects the slide's two-timer explanation; no runtime or firmware code was changed.
- Reworked the BCM2712 diagram into four clearly separated cores in two rows, preserving private L2, shared L3/memory, and the external RP1 connection. Removed sloped labels from the clock exchange.

Validation: `cd slides && latexmk -xelatex -interaction=nonstopmode main.tex` completed successfully. Final `main.log` contains zero errors, zero overfull boxes, and no warnings. `git diff --check` passed. Rebuilt `slides/main.pdf`, rendered every page into `slides/preview/` with Ghostscript at approximately 1280 × 720, opened every page across the review iterations, and rechecked changed pages after corrections. Swift initially failed because its default module cache was outside the writable sandbox; Ghostscript supplied the final previews.

No commit or push was made. Existing `slides/review_loop.sh` edits were preserved. Validation concerns the document on macOS, not hardware behaviour.
