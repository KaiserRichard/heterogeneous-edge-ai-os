# Builder round 2

Addressed the defects in `slides/review/latest.md` in `slides/main.tex`. Page references below use the review's original numbering; references now occupy pages 44–47 and the closing slide is page 48.

- **p1–2:** Enlarged the cover's lower composition with equal-height 0.42/0.54 columns, a larger V01, and explicitly left-aligned member information. Rebuilt contents as a two-column, three-row grid with shared baselines.
- **p5, p26:** Aligned separate comparison blocks with their illustrations; moved the buffer definition above the columns and reserved a consistent caption-to-takeaway gap.
- **p6:** Added the Figure 3 explanation of Linux proposals and RTOS supervisory authority.
- **p9–10:** Expanded RQ and UART before their first diagram, and CPU and cgroups in RQ2 at first use.
- **p12–13:** Replaced both Simplex raster diagrams with a shared full-row TikZ diagram, normal-size labels, separate hardware boundary, and unobstructed proposal/decision labels. Separated Figure 8's explanation from the nested list.
- **p14–15:** Kept the scheduler definition in an introductory bullet; replaced both scheduling images with a large timeline using body-font headings, core labels, time axis, and colour legend.
- **p17–18:** Rebuilt contention illustrations with readable core labels and traffic legends. Gave paired diagrams equal figure regions and aligned caption tops/bottoms; referenced both figures explicitly. Expanded LPDDR4X, PCIe and I/O, clarified L2/L3, and retained the memory controller and separate RP1 connection.
- **p19–20:** Replaced both AoI images with a large labelled graph showing peak, mean, every above-threshold interval, and an explicit illustrative qualifier.
- **p22, p42:** Reused a corrected, readable architecture diagram: Supervisor directly drives Failsafe/Output, with an independent status branch. Explained GPIO at its first use.
- **p23–24:** Added the TX/RX/GND wiring legend and ISR expansion. Rebuilt the pipeline with an AoI measurement bracket physically connected to sampling and Output.
- **p28–29:** Used “lệnh khởi động lại tường minh” consistently, retained the distinct HOLD timeout and FRESH heartbeat labels, added a transition explanation, and corrected the design frequency to “1 kHz (chu kỳ 1 ms)”.
- **p30:** Redrew heartbeat and result-age traces with normal-size labels, a marked threshold crossing, and age continuing to rise without updates.
- **p31:** Grouped timestamp definitions, equations and symmetry assumption in a labelled block; kept implementation bullets separate and constrained the diagram/caption to one figure unit.
- **p33–34:** Set the violation ratio as a body-size display equation; placed run controls in a compact block directly beneath the experiment table.
- **p35–36:** Reused a large timing chart with one State decision, aligned markers for all three timestamps, readable signal labels, and the reaction interval.
- **p37, p39:** Reworded H2 as reducing CPU-contention tail latency without eliminating memory-bandwidth contention; narrowed/wrapped the progress table's first column and added a fixed gutter.
- **p44–45:** Redistributed all eight bibliography entries over four normal-size pages, with uniform entry spacing and comma-separated author lists.

Validation: `latexmk -xelatex -interaction=nonstopmode main.tex` completed with zero errors, warnings or overfull boxes. Rendered all 48 pages into `slides/preview/` with `swift render.swift` (workspace module cache) and opened every PNG, repeating inspection after refinements. `git diff --check` passed. No commit made; the pre-existing edit to `slides/review_loop.sh` was left untouched. This validates the deck locally, not the proposed hardware system.
