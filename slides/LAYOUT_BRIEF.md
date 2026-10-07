# Builder brief: layout pass (v5)

You are the BUILDER. You edit `slides/main.tex` (XeLaTeX Beamer) so every page looks balanced,
calm and professional, like a well-designed thesis defence deck. Content is mostly approved;
this pass is about LAYOUT. Keep wording unless a rule below asks for a change.
Specs that still apply: `slides/RESTRUCTURE_SPEC.md`, `slides/REVISION_V4.md`.

If `slides/review/latest.md` exists, it is the strict reviewer's list of defects from the last
round: fix EVERY item in it first, then continue with the rules below.

## 1. Global layout system (implement once in the preamble, use everywhere)
1. **Vertical rhythm.** Body text `\normalsize` at 12pt base with `\linespread{1.12}`. Uniform
   bullet spacing: `\setlength{\itemsep}{0.55em}` for level 1 and `0.25em` for level 2 in EVERY
   itemize (define a `\setbeamertemplate`/`\AtBeginEnvironment{itemize}` hook so it is global).
   No manual `\vspace` between bullets, no empty lines inside itemize, no `\\` line breaks in bullets.
2. **Fill the frame evenly.** Content starts top-left under the title (class option `t`), but a
   frame must not leave the bottom third empty while text is crammed at the top. Use
   `\vfill` between logical blocks (text block / figure block / conclusion box) so blocks
   spread over the frame height. If a frame is still sparse, enlarge the figure, not the text.
3. **Two-column frames:** `\begin{columns}[T,onlytextwidth]`, columns 0.48/0.48 or 0.42/0.54 of
   `\textwidth` with the gap in between; both columns top-aligned at the same baseline. The
   figure column contains a `minipage` with the image `\centering` and its caption directly
   below, centred, exactly as wide as the image. Never push an image flush against the right edge
   with empty space on its left.
4. **Captions:** one macro `\fig[height]{file}{caption}` that renders image + caption as a unit:
   caption `\small`, same font family as the body (NOT a condensed font), muted colour, centred,
   width = image width, 2 lines max. Figure numbers auto-increment.
5. **Conclusions / take-aways:** never a bullet followed by an arrow ("■ ⇒ ..."). Use a
   dedicated macro `\takeaway{...}`: a full-width tinted box (navy 6% background, teal left rule
   3pt, `\normalsize`, no bullet) placed at the bottom of the frame after `\vfill`. Inside text,
   if an implication arrow is needed, use math `$\Rightarrow$` inline in a sentence, never as a
   bullet head.
6. **Definitions:** fold term definitions into the sentence that uses them, e.g. "tác vụ nền bị
   giới hạn bằng cgroups (control groups, cơ chế giới hạn tài nguyên cho một nhóm tiến trình),
   nên tác vụ quan trọng chạy đều đặn." Never a loose paragraph of definitions at the bottom.
7. **Text density:** max 4 level-1 bullets, max 3 lines each at full width (2 lines in a half
   column). If more, split the frame ("(tiếp)") — never shrink fonts below `\normalsize` for body
   or `\small` for captions.
8. **TikZ diagrams:** labels must never overlap nodes, edges or other labels. Use horizontal
   labels (no `sloped`), `auto`/`above`/`below` with explicit offsets, enough `node distance`,
   label backgrounds `fill=paper`. Check every diagram in the rendered PNG at 100% zoom.

## 2. Specific defects from the owner's screenshots (must fix)
- **Cover (p1):** too much empty space; unbalanced.
  - Title "NỀN TẢNG THỰC THI EDGE-AI / KHÔNG ĐỒNG NHẤT" larger (`\huge` bold) and moved up;
    "Heterogeneous Edge-AI Runtime" larger (`\Large`) under it; thin teal rule.
  - Below: two balanced columns of equal height. Left column vertically centred against the
    image: "Nhóm thực hiện: 3 Stars" (`\large` bold label), member lines (`\normalsize`), a gap,
    "GVHD: TS. Nguyễn Quang Minh" and "Mã lớp bài tập: 173876" (`\large`). Right: V01 filling
    its column (height ≈ 50% of page). The whole group is centred on the page; no big empty band.
- **p5 (1.1 tiếp):** uneven gaps between bullets (big gap before the "Hình 1" bullets); figure
  sits pushed right with its caption misaligned. Rebuild as: definitions full width at top;
  then two columns (Hình 1 explanation bullets left | image + centred caption right) top-aligned;
  then the conclusion in `\takeaway{}` at the bottom (no bullet, no ⇒ glyph as bullet).
- **p6 (1.2):** layout is fine; remove the "■ ⇒" bullet (use `\takeaway{}`), body text slightly
  larger, captions in body font.
- **p10 (2.2):** delete the loose bottom paragraph about cgroups; fold the definition into the
  "Hình 5 (dưới)" bullet as in rule 6. Spread content vertically; image and text columns top-aligned
  and of similar height.
- **p21 (state machine):** labels overlap boxes and each other ("Dữ liệu hợp lệ" over the INIT/
  FRESH border, sloped "Mất heartbeat" over FAILSAFE/HOLD, "Giữ chốt" hidden). Redraw with
  more spacing and horizontal labels. ALSO a correctness bug: HOLD → FAILSAFE must be labelled
  "Hết thời gian chờ" (timeout), only FRESH → FAILSAFE is "Mất heartbeat". Put "Giữ chốt" clearly
  under FAILSAFE. Edges: INIT→FRESH "Dữ liệu hợp lệ", FRESH→HOLD "Quá cũ", HOLD→FRESH "Mới lại",
  FAILSAFE→INIT (dashed) "Khởi động lại rõ ràng".
- Apply the same fixes to every similar frame (any "■ ⇒", any loose definition paragraph, any
  crowded diagram, any sparse frame).

## 3. Procedure
1. Edit main.tex. 2. `cd slides && latexmk -xelatex -interaction=nonstopmode main.tex`; zero
errors, zero overfull boxes. 3. Render all pages to PNG (`swift render.swift` or `sips`), into
`slides/preview/`. 4. Open EVERY PNG with your image viewer and compare against sections 1–2;
fix and repeat until you find nothing. 5. Do not commit; the loop script commits.
Write a short changelog of what you changed to `slides/review/builder-round-N.md` (N given in the prompt).
