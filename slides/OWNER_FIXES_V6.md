# Owner fixes v6 (2026-10-07 17:36) — HIGHEST PRIORITY for the builder

1. **Figure numbering bug (whole deck, severe).** The same figure must keep the same number
   everywhere. Today a figure repeated on a "(tiếp)" slide gets a new number (e.g. the RQ
   diagram is "Hình 6" on p9 and "Hình 7" on p10). Rules:
   - Each distinct figure is numbered once, at its first appearance (`\label{fig:key}`).
   - If the same figure appears again (continuation slide, recap in the conclusion), show it
     with the SAME number and caption (do not step the counter): implement a macro, e.g.
     `\figagain{key}` that reuses the stored number/caption, or `\caption*{Hình~\ref{fig:key}: ...}`.
   - Text references use `Hình~\ref{fig:key}`; numbers must match what is under the image.
   - Prefer not repeating a figure at all; on a continuation slide keep the figure and add the
     extra explanation as text (e.g. 1.3: keep the RQ diagram as the same Hình, explain more).
   - Check every page: list all captions in order; numbers strictly increase except repeats,
     which must equal the original.
2. **Cover (p1):** "Nhóm thực hiện" block and "GVHD / Mã lớp" lines the SAME font size
   (`\large`, label in bold); member names on one line each (no wrapping "(Nhóm trưởng)").
   The left block and V01 together fill the space below the rule (no empty bottom band):
   enlarge V01 and the text block, vertically centre the text block against the image.
3. **Mục lục (p2):** one vertical column 1→6, each section in its own box: a filled navy
   square with the number in white on the left, the section title to its right inside a light
   rounded rectangle; six equal rows spanning the frame height, left-aligned, large text.
4. **p5 (1.1 tiếp):** layout top to bottom: (a) the two definitions full width; (b) Hình V02
   centred, large, with its caption centred directly under it; (c) one row with two equal
   columns: "Hình n (trái): xa lộ tối ưu lưu lượng, không bảo đảm giờ đến." | "Hình n (phải):
   tín hiệu và đồng hồ bảo đảm từng chuyến đúng giờ." (each one line); (d) the take-away box.
   Apply the same pattern to other slides where a left/right image explanation is split into
   bullets far apart.
5. Re-check every slide for the same classes of defects (repeated-figure numbering, unequal
   font sizes in one block, explanations far from their figure).
6. **p26** has the same defect and layout problem as p5: apply the p5 pattern (figure centred
   with caption under it, left/right explanations on one row below, take-away box at the bottom).
7. **References on ONE slide.** "Tài liệu tham khảo (1/4)" etc. must become a single slide:
   no allowframebreaks; use `\footnotesize` (or `\scriptsize` if needed) for the entries,
   compact entries (authors, title, venue, year; drop URLs/DOIs if space is short), two columns
   if necessary. Exactly one references page.
