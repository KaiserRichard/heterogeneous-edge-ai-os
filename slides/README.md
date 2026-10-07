# Slides: progress-report deck (Beamer, XeLaTeX)

Source of content: `docs/SLIDES_OVERVIEW.md` (18 slides + notes) and `docs/SYSTEM_GUIDE.md`.

## Build

```sh
cd slides
latexmk -xelatex -interaction=nonstopmode main.tex  # -> main.pdf (ignored by git)
latexmk -c                     # remove aux files
```

Requires TeX Live with the `moloch` Beamer theme and the macOS fonts Avenir Next and Menlo.
Speaker notes are in `\note{}`; uncomment one `\setbeameroption` line at the top of `main.tex`
to show them (second screen for pdfpc, or notes only).

## Images

Put generated images in `slides/images/` as `V01.png` ... `V24.png`. A missing file shows a
gray labelled placeholder, so the deck always compiles. Images are scaled to fit their box
(aspect ratio kept). The UART frame, supervisor state machine, T1-T4 clock exchange and
profile ladder are TikZ drawings, not images.

| Slide | Title (short) | Images |
|---:|---|---|
| 1 | Title | V01 |
| 2 | Motivation | V02, V03, V04 |
| 3 | Problem statement | V07 |
| 4 | Related work | V06 |
| 5 | Multicore contention | V05 |
| 6 | Architecture | V08 |
| 7 | Hardware | V09, V22 |
| 8 | Data path and AoI | V10, V20 |
| 9 | Workload | (TikZ timeline) |
| 10 | Runtime profiles | V12, V11 (+ TikZ ladder) |
| 11 | Queue vs latest value | V14 |
| 12 | UART protocol | (TikZ frame) |
| 13 | Supervisor | V16, V17 (+ TikZ state machine) |
| 14 | Clock alignment | (TikZ T1-T4) |
| 15 | Experiments | V21 |
| 16 | Failsafe latency | V23 |
| 17 | Hypotheses | none |
| 18 | Progress | V24 |
| backup | Supporting illustrations | V13, V15, V18, V19 |

## Number policy

No number in the deck is a measurement on our rig. Each is tagged as DESIGN, CALCULATED,
HOST-TEST (unit tests on the host) or PUBLISHED (other setups, cited).

## Presentation review

The deck has 18 talk slides, two bibliography pages in the appendix, and one supporting-illustrations page.
Sentence titles carry each slide's message; secondary details stay in speaker notes. Diagram labels and
bibliography text are kept readable, and orange is reserved for fault paths and FAILSAFE.
The V01–V24 mapping and missing-image placeholders are unchanged.

Presentation guidance consulted:
- [Michael Alley, assertion-evidence tutorial](https://www.craftscicom.org/ae_tutorial.html): message titles, visual evidence, readable callouts, secondary details in notes.
- [Carnegie Mellon, slide-design handout](https://www.cmu.edu/student-success/other-resources/handouts/comm-supp-pdfs/designing-powerpoint-slides.pdf): one distinct point and essential text per slide.
- [Carnegie Mellon, presentation guidance](https://www.stat.cmu.edu/cmsac/sure/2022/materials/lectures/slides/08-Presentations.html): references beside claims and in backup material for sharing.

Bibliography metadata was checked against DBLP and arXiv; each entry links to its primary record.
The CISS authors/pages are also confirmed by [Marco Gruteser's DBLP bibliography](https://dblp.org/pid/87/88.html).
DeepPicar's published venue is IEEE RTCSA 2018, pp. 11–21. The scheduling paper is cited as an arXiv preprint.

PDF previews: `swift render.swift main.pdf preview` (macOS PDFKit; pdftoppm not needed). If Swift's default cache is blocked,
pass `-module-cache-path .swift-module-cache` so its cache stays within `slides/`. Remove that generated
cache after rendering. Previews live in `preview/` and are ignored by Git.
