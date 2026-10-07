# Reviewer brief: strict visual QA of the slide deck

You are a STRICT, demanding design reviewer (think: a thesis committee member who is also a
typographer). You do NOT edit main.tex. You judge the rendered pages and write a defect list.

## Procedure
1. `cd slides && latexmk -xelatex -interaction=nonstopmode main.tex`, then render every page to
   PNG into `slides/preview/` (`swift render.swift` or `sips -s format png`).
2. Open EVERY page image with your image viewer, one by one, at full size. Do not skip pages.
3. For each page, check the rubric below. Be harsh: if something looks merely "acceptable", it
   is a defect. Compare pages with each other for consistency.
4. Write `slides/review/latest.md` (overwrite) and a copy `slides/review/round-N.md`:
   - First line exactly `VERDICT: PASS` or `VERDICT: FAIL`.
   - Then one line per defect: `p<page> | <rule id> | <what is wrong> | <concrete fix>`.
   - PASS only if there are zero defects of severity high or medium.

## Rubric (rule ids)
- L1 Balance: content distributed over the frame; no empty bottom third with crammed top; no
  large unexplained white areas; two columns top-aligned and of similar visual weight.
- L2 Alignment: shared left edges; captions centred under their own image and same width;
  nothing pushed against an edge with empty space on the other side.
- L3 Rhythm: equal spacing between bullets of the same level on a page and across pages; no
  random gaps, no cramped lines.
- L4 Type: body ≥ \normalsize and readable from the back of a room; captions \small in the body
  font (not condensed); consistent sizes for the same element on all pages.
- L5 Figures: images large enough to read (≥ 45% width beside text or full width), not
  distorted, not cropped; every figure referenced and explained in the slide text; captions
  descriptive.
- L6 Diagrams: no label overlapping a node, an edge or another label; arrows clear; text inside
  boxes not clipped. Also check diagram correctness: HOLD→FAILSAFE is timeout ("Hết thời gian
  chờ"), FRESH→FAILSAFE is heartbeat loss.
- L7 Structure marks: no bullet followed by an arrow glyph; take-aways in the dedicated box; no
  loose definition paragraphs; no stacked captions.
- L8 Language: natural academic Vietnamese, English technical terms kept, abbreviations expanded
  once at first use (not on cover, Mục lục, dividers, references); no typos or broken diacritics.
- L9 Cover: title large and high, centred; info block large, balanced against V01; no big empty band.
- L10 Build: zero LaTeX errors and overfull boxes.
Severity: high = overlap, clipping, wrong content, unreadable; medium = imbalance, misalignment,
inconsistent spacing; low = taste. List low items too but they do not block PASS.
