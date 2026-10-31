# Slide image-generation prompts

Use [PART_A.md](PART_A.md) for V01–V12 and [PART_B.md](PART_B.md) for V13–V24 in two independent ChatGPT image-generation sessions. Each part includes identical STYLE GUIDE and HARDWARE REFERENCE blocks; neither needs the other file. These are prompts only, not generated assets.

## Procedure

1. Open a fresh ChatGPT image-generation chat for each part. Paste only that file's STYLE GUIDE and HARDWARE REFERENCE as setup; request acknowledgement without an image. Do not paste the whole file as a generation request.
2. Paste exactly one fenced V prompt per message. Each begins “Generate exactly ONE image for Vxx. Do not create variants or a second image.”
3. Wait for the single finished image. Check its subject, aspect ratio, allowed labels and board fidelity. Download it as `Vxx.png` to the exact save path below before sending the next prompt. If the download has another format, export/convert it to a real PNG; renaming the extension is insufficient.
4. Send the next specific V prompt. Never send “continue,” multiple prompts at once, or a request for variants. Two comparison panels, where requested, belong in one image.
5. If ChatGPT repeats an earlier image, start a new chat and paste the STYLE GUIDE + HARDWARE REFERENCE again. Then paste only the current V prompt; do not ask it to continue the earlier sequence. Use the UNIQUE SUBJECT and MUST NOT SHOW lines to check the replacement before saving it.
6. Keep one approved file for each V-id. The workflow saves future generated images under `slides/images/`; this prompt-writing task creates files only under `slides/image-prompts/`. No deck edits or commit are required.

## Deduplication and save-path table

Slide numbering follows `slides/README.md`; subjects follow the actual `\slideimg` captions read from `slides/main.tex`. The source deck may be rewritten independently. “Backup” means the supporting-illustrations appendix frame, not a numbered talk slide. Aspect ratios are explicit: 16:9 by default; 1:1 for the four clearly small icon slots. The slot preserves image proportions.

Every subject below has a distinct visual purpose. In particular, V08 describes domain ownership, V10 traces one result, V09 shows the whole bench, and V22 specifies signal endpoints. V11 shows scheduler behaviour, V12 profile relationships, and V13 the individual tuning mechanisms. V16 is an output gate, V17 a timer pair, and V18 a state machine.

| V-id | Slide | Unique subject | Aspect ratio | Part | Save path |
|---|---|---|---|---|---|
| V01 | 1 — Title | Paired-board title emblem | 16:9 | A | `slides/images/V01.png` |
| V02 | 2 — Motivation | Late inference result under contention | 16:9 | A | `slides/images/V02.png` |
| V03 | 2 — Motivation | Receiver cannot see result age | 1:1 | A | `slides/images/V03.png` |
| V04 | 2 — Motivation | Linux hang stops a colocated monitor | 1:1 | A | `slides/images/V04.png` |
| V05 | 5 — Multicore contention | Private L2 versus shared L3 and DRAM | 16:9 | A | `slides/images/V05.png` |
| V06 | 4 — Related work | Related-work concept map | 16:9 | A | `slides/images/V06.png` |
| V07 | 3 — Problem statement | Three research questions | 16:9 | A | `slides/images/V07.png` |
| V08 | 6 — Architecture | Two-domain authority architecture | 16:9 | A | `slides/images/V08.png` |
| V09 | 7 — Hardware | Complete cooled hardware rig | 16:9 | A | `slides/images/V09.png` |
| V10 | 8 — Data path and AoI | Life of one input through the data path | 16:9 | A | `slides/images/V10.png` |
| V11 | 10 — Runtime profiles | Stock versus tuned CPU scheduling | 16:9 | A | `slides/images/V11.png` |
| V12 | 10 — Runtime profiles | Branched runtime-profile ladder | 16:9 | A | `slides/images/V12.png` |
| V13 | Backup — Supporting illustrations | P1 tuning mechanisms checklist | 16:9 | B | `slides/images/V13.png` |
| V14 | 11 — Queue vs latest value | FIFO storage versus latest-value replacement | 16:9 | B | `slides/images/V14.png` |
| V15 | Backup — Supporting illustrations | UART frame anatomy and CRC coverage | 16:9 | B | `slides/images/V15.png` |
| V16 | 13 — Supervisor | Supervisor gates the simulated output | 1:1 | B | `slides/images/V16.png` |
| V17 | 13 — Supervisor | Independent liveness and freshness timers | 1:1 | B | `slides/images/V17.png` |
| V18 | Backup — Supporting illustrations | Latched supervisor state transitions | 16:9 | B | `slides/images/V18.png` |
| V19 | Backup — Supporting illustrations | Clock exchange and independent GPIO check | 16:9 | B | `slides/images/V19.png` |
| V20 | 8 — Data path and AoI | Conceptual Age of Information sawtooth | 16:9 | B | `slides/images/V20.png` |
| V21 | 15 — Experiments | Four-experiment plan matrix | 16:9 | B | `slides/images/V21.png` |
| V22 | 7 — Hardware | Signal-level UART and timing wiring | 16:9 | B | `slides/images/V22.png` |
| V23 | 16 — Failsafe latency | External analyzer observes fault, decision and output | 16:9 | B | `slides/images/V23.png` |
| V24 | 18 — Progress | Software progress and hardware next steps | 16:9 | B | `slides/images/V24.png` |

## Hardware verification and sources

The board descriptions were checked against official Raspberry Pi product documentation and ST's board-specific UM1724 manual. The ST product page includes features shared across several Nucleo models; use the MB1136/F446RE manual rather than importing another board's USB connector or debugger.

- [Raspberry Pi 5 specifications and official product photographs](https://www.raspberrypi.com/products/raspberry-pi-5/) and [product brief](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf): BCM2712 and RP1 identity, 40-pin GPIO, USB 3.0/2.0 counts, Gigabit Ethernet, USB-C, dual micro-HDMI, dual 4-lane MIPI interfaces, PCIe and power button. The physical reference is the green credit-card board, central metal-lidded SoC and actual connector arrangement; USB port tongues retain blue/black rather than the diagram palette. The fan header is also documented by the cooler reference below. Ethernet is present but unused for the project link.
- [Official Active Cooler](https://www.raspberrypi.com/products/active-cooler/): aluminium heatsink plus small temperature-controlled blower, attached to the Pi and powered from its fan header. Render its silver/black appearance, not a generic tower cooler. The fitted cooler can hide the SoC.
- [ST NUCLEO-F446RE product page](https://www.st.com/en/evaluation-tools/nucleo-f446re.html) and [UM1724, STM32 Nucleo-64 boards (MB1136)](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf): Nucleo-64 identity, attached ST-LINK/V2-1 section and mini-B USB, central LQFP64 MCU, Arduino Uno V3 and morpho headers, USER/RESET controls, green LD2. See the board photograph, section 7.1 top layout, and section 7.7 for buttons; preserve white PCB, blue USER and black RESET. Do not substitute a green board or Blue Pill.

GPIO14 TX → PA10 RX, GPIO15 RX ← PA9 TX, GPIO17 → PA0 and shared GND are **project design connections from the slide**, not new pinout decisions. V22 deliberately uses labelled signal endpoint boxes instead of guessed physical header-hole positions. V23 similarly uses abstract test-point callouts rather than invented measurement-pin assignments.

## Content and number policy

The prompts were written from `PROJECT.md`, `slides/main.tex`, `slides/README.md`, `docs/SLIDES_OVERVIEW.md` and `docs/SYSTEM_GUIDE.md`; no older prompt file was used. Older overview IDs are superseded by the V-id mapping in the current deck. These assets illustrate OS scheduling, contention, UART communication, freshness, independent supervision and reproducible evaluation.

Images contain no invented rig measurements. Conceptual timing plots have no numeric scales. Numeric design labels are restricted to the specified priority, buffer size and protocol design fields; profile IDs, experiment IDs, timestamps and chip/pin names are identifiers. Hardware counts in the setup blocks guide geometry, not extra printed specifications. V24 keeps Supervisor v2 in progress and hardware experiments pending; host tests do not establish physical performance. No hardware verification is claimed for the project rig.
