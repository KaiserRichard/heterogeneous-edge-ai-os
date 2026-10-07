# Slides: progress-report deck (Beamer, XeLaTeX)

Source of content: `docs/SLIDES_OVERVIEW.md` (18 slides + notes) and `docs/SYSTEM_GUIDE.md`.

## Build

```sh
cd slides
latexmk -xelatex main.tex      # -> main.pdf (ignored by git)
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
