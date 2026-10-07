# Final builder pass — 2026-10-07

Implemented every defect in `review/latest.md`, following `LAYOUT_BRIEF.md` and the overriding `OWNER_FIXES_V6.md`. No commit made.

| Pages | Changes |
| --- | --- |
| 5 | Shortened Hình 2 caption to one line; parallel, one-line explanations in equal columns; explicit caption-to-explanation space. |
| 6 | Expanded RTOS as Real-Time Operating System at its first occurrence; used RTOS subsequently. |
| 15 | Removed repeated cgroups expansion; retained its first introduction on p10. |
| 17 | Associated RP1/PCIe, I/O and L2 details with the right-hand Hình 11 in a compact labeled block; kept the caption separate; adjusted diagram spacing so memory-controller arrows remain visible. |
| 19, 20 | Corrected all five AoI rises to slope 1 on the same linear axes. Recomputed threshold crossings, orange shading and mean line; reused Hình 13 with the same caption. |
| 22, 42 | Added explicit Linux and STM32 enclosing boundaries. Supervisor, Failsafe / Output and Báo trạng thái all sit inside STM32. Rerouted GPIO synchronization separately from failsafe/status arrows. Preserved Hình 14 and its caption. |
| 23 | Added labeled connection-symbol and hardware-specification blocks associated with the table and illustration; adjusted vertical figure spacing to fit without overflow. |
| 25 | Placed buffer/kernel labels outside their branches with clear space; both P1-to-P2/P3 arrows remain continuous and unobscured. |
| 26 | FIFO boxes read **4 3 2 1**, with oldest **1** at the send end; arrow reads **Gửi cũ nhất**. **FIFO queue** has its own heading line. **Thứ tự đến: 1, 2, 3, 4** is right-aligned above the send arrow on a separate line. Latest-value row retains only **4**. Caption is one line, explanations are one line each in equal columns, and explicit .8em spacing creates a visible gap below Hình 18. |
| 31 | Raised ECHO_REQ and ECHO_RESP labels clear of the entire diagonal arrows. |
| 33 | Added a consistent table-to-list gap; changed the displayed fraction to a compact inline formula to preserve uniform bullet spacing. |
| 34 | Increased table row spacing and distributed the table/control block over the available frame height. |
| 40 | Distributed space through the six steps; placed the figure explanation directly above the diagram with normal paragraph spacing. |

## Validation

- Built with `cd slides && latexmk -xelatex -interaction=nonstopmode main.tex`.
- Final `main.log`: zero errors, overfull boxes, underfull boxes, Missing character messages, or LaTeX/package warnings. `git diff --check` passes.
- Rendered all 45 pages using `cd slides && swift render.swift main.pdf preview`, with `CLANG_MODULE_CACHE_PATH` and `SWIFT_MODULECACHE_PATH` directed to a temporary workspace-local cache because the sandbox blocks the default host cache. Removed that cache after rendering.
- Personally opened and visually inspected all 45 page PNGs. Reopened every subsequently changed page after rendering; specifically checked p26 repeatedly for heading/arrival-order overlap, FIFO direction, one-line explanations and caption separation.
- Numerical AoI check: rises all have slope 1; threshold 2.8 crossings occur at 2.1, 3.7, 6.2, 7.7 and 11.0. Integral over [0, 12.3] is 29.425; mean is 2.3922764 (drawn at 2.39228). Both occurrences use the same macro.
- References remain exactly one slide, p44; no `allowframebreaks`.
- AUX labels confirm 26 distinct figures numbered sequentially 1–26; repeated assets reuse their original number and caption.

## Caption-number audit (page: figures)

4: 1; 5: 2; 6: 3; 7: 4; 8: 5; 9: 6; 10: 6 (repeat); 12: 7; 13: 7 (repeat); 14: 8; 15: 8 (repeat); 16: 9; 17: 10, 11; 18: 12; 19: 13; 20: 13 (repeat); 22: 14; 23: 15; 24: 16; 25: 17; 26: 18; 27: 19; 28: 20; 29: 21; 30: 22; 31: 23; 35: 24; 36: 24 (repeat); 40: 25; 42: 14 (architecture recap); 43: 26.

The existing modification to `slides/review_loop.sh` was left untouched. Work was limited to the presentation source, generated PDF/previews and this validation record; no hardware behavior was changed.
