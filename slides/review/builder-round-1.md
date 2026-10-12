# Builder round 1

Applied `LAYOUT_BRIEF.md`, the complete `latest.md` defect list, and all seven owner overrides in `OWNER_FIXES_V6.md` (including the additions made during this round).

- Fixed repeated-figure numbering and caption reuse for RQ, Simplex, scheduling, AoI, reaction timing and the architecture recap. Updated all text references; caption audit is in `captions-round-1.txt`.
- Balanced the cover with uniform large text and unwrapped member lines; replaced the contents with six numbered rows.
- Rebuilt p5 and p26 with centred figures, captions directly underneath, adjacent explanation columns and bottom takeaways. Cropped V02's embedded headings at inclusion time and added normal-size body-font labels. Replaced FIFO, wiring and profile illustrations with readable vector diagrams; preserved the independent P1→P2 and P1→P3 branches.
- Centred the memory traffic legend; merged the AoI, heartbeat and reaction qualifiers into their numbered captions.
- Cleared the architecture boundary from UART, displaced GPIO's label and rerouted its arrow into Supervisor. The conclusion reuses this corrected diagram.
- Redistributed the state-machine group and placed its explanation in a labelled block. Kept horizontal transition labels, the HOLD timeout label and visible FAILSAFE latch text.
- Added a fixed metric-table gutter. Consolidated all eight references into one two-column page using the owner's explicitly permitted footnotesize exception.

Validation: `latexmk -xelatex -interaction=nonstopmode main.tex` completed successfully with zero errors, zero overfull boxes and no warnings in `main.log`. Rendered all 45 pages with `swift -module-cache-path preview/.swift-cache render.swift main.pdf preview`; opened every page and rechecked changed pages after rebuilds. `git diff --check` passed. Removed obsolete preview pages 46–48. No commit made; existing changes to the owner brief and review loop were preserved.

The two p5 explanation sentences occupy two lines each at normal size; they remain on the same row with equal columns. This preserves the owner's exact wording and the body-font minimum, but differs from the owner's requested single-line sentences.
