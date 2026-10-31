## STYLE GUIDE

Flat technical illustration on a light off-white background (#FAFAF7). Use navy #1F3A5F for structure and text, teal #2A9D8F for normal operation, and orange #E76F51 only for faults/failure. Hardware fidelity overrides the diagram palette: real green/white PCBs, blue USB tongues and USER button, black chips/buttons, and silver metal must retain their real colours. No photorealistic people. Use clean consistent outlines, restrained flat shading, generous whitespace, minimal English labels, and large readable sans-serif text. No watermark, decorative branding, tiny fake text, or invented logos. Render only the labels explicitly allowed in the individual prompt; leave board silkscreen blank. Do not render the V-id, save path, instructions, or source URLs inside the image.

One prompt produces one finished image, even if it contains comparison panels. Do not create variants, contact sheets, or an extra image. Follow the stated aspect ratio. Do not invent measurements, performance results, numeric axes, timeout values, dates, or completion percentages. Numbers may appear only when explicitly allowed by that prompt and already present as design values in the deck; model names, pin identifiers, protocol fields and profile IDs are identifiers. Schematic curves and bars convey concepts, never measured results. Use generic GPIO/LED outputs; no application scene. The bridge is UART only; no Ethernet connection, SPI, CAN, middleware, virtual machines, containers, or model inference on the STM32.

## HARDWARE REFERENCE

Use the actual Raspberry Pi 5 and STM32 Nucleo-F446RE shapes, not generic development boards. Hardware features describe geometry; they are not permission to add text or specification callouts.

- **Raspberry Pi 5:** GREEN PCB, credit-card size. A metal-lidded Broadcom BCM2712 SoC sits near the centre; RP1 is a separate I/O chip. The 40-pin GPIO header runs along one long edge. One short edge carries two stacked USB port blocks: 2x USB 3.0 with blue tongues and 2x USB 2.0 with black tongues, plus a Gigabit Ethernet jack. The opposite long edge to GPIO carries USB-C power and 2x micro-HDMI; preserve the two 4-lane MIPI camera/display FPC connectors in their actual edge-side positions. Include the separate PCIe FPC connector, power button, and fan header in their reference positions. When active cooler is requested, show the official Active Cooler: black/silver aluminium heatsink with a small black blower fan, fitted over the SoC and connected to the fan header. Covered chips may be occluded; do not duplicate them outside the cooler.
- **STM32 Nucleo-F446RE:** WHITE PCB, elongated Nucleo-64 form factor. Keep the top ST-LINK/V2-1 debugger section attached, with its mini-USB connector. A black LQFP64 STM32F446RE chip occupies the main board's middle. Include the blue USER button, black RESET button, Arduino Uno V3 female headers, ST morpho male pin headers along both long edges, and the green user LED LD2. Do not detach the debugger or substitute another Nucleo family.
- **Explicit negatives:** Pi 5 is NOT a blue, red, or black PCB and has NO full-size HDMI. Nucleo is NOT green and NOT a Blue Pill. Do not invent logos or brand text. Avoid tiny fake text; use only the labels given by each prompt. Ethernet is an unused physical jack, never the inter-board bridge.
- In board-bearing prompts, repeat the short key facts below the composition instructions. For abstract diagrams explicitly marked “no boards,” use boxes/icons rather than inaccurate board silhouettes.

Official references checked for identity, interfaces and layout:
[Raspberry Pi 5 product/specification page](https://www.raspberrypi.com/products/raspberry-pi-5/), [Pi 5 product brief](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf), [official Active Cooler](https://www.raspberrypi.com/products/active-cooler/), [ST NUCLEO-F446RE](https://www.st.com/en/evaluation-tools/nucleo-f446re.html), [ST UM1724, board photo and top layout, sections 7.1 and 7.7](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf).

# PART A: V01–V12

This file is self-contained for a fresh image-generation chat. First paste STYLE GUIDE and HARDWARE REFERENCE together as setup and ask the session to acknowledge them without generating an image. Then paste only one fenced prompt per message, in V-number order. Wait for the image and save it before sending the next prompt. Never send “continue,” several prompts together, or the whole file as a generation request. On repetition, start a fresh chat, paste both setup blocks again, and send only the current V prompt. The other part is not required.

## V01 — Paired-board title emblem

Slide: 1 — Title. Save as `slides/images/V01.png`.

```text
Generate exactly ONE image for V01. Do not create variants or a second image.
UNIQUE SUBJECT: A clean paired-board emblem introducing the two computing platforms.
MUST NOT SHOW: Architecture boxes, process stages, detailed wiring labels, bench equipment, charts.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Place an accurately drawn bare Pi 5 and attached-section Nucleo side by side in a balanced shallow isometric view. Connect them with one simple abstract teal link labelled UART, with no pin detail. The boards and link are the entire visual; leave breathing room for the slide title outside this asset. Do not add a cooler or power supply.

BOARD KEY FACTS: Pi 5 = green credit-card PCB, central metal-lidded BCM2712 plus separate RP1, long-edge 40-pin GPIO, short-edge stacked blue USB 3.0 / black USB 2.0 and Ethernet jack, opposite-edge USB-C / two micro-HDMI with two MIPI FPC connectors nearby, separate PCIe FPC, power button and fan header. No blue/red/black Pi PCB or full-size HDMI. Nucleo-F446RE = white Nucleo-64 PCB, attached upper ST-LINK/V2-1 with mini-USB, central black LQFP64 STM32F446RE, blue USER / black RESET, Arduino female and bilateral morpho male headers, green LD2. No green Nucleo or Blue Pill. No invented logos, brand text or tiny silkscreen; only the allowed labels.

ALLOWED LABELS ONLY: Raspberry Pi 5; STM32 Nucleo-F446RE; UART.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V02 — Late inference result under contention

Slide: 2 — Motivation. Save as `slides/images/V02.png`.

```text
Generate exactly ONE image for V02. Do not create variants or a second image.
UNIQUE SUBJECT: CPU competitors delay an inference result before dispatch.
MUST NOT SHOW: Hidden-age receiver metaphor (V03), frozen Linux icon (V04), profile comparison, measured latency charts, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw one conceptual horizontal execution lane. A navy inference block is interrupted by several competing CPU-work blocks; a result envelope emerges only after a dashed deadline marker. Highlight the late envelope and missed deadline in orange. Keep the lane qualitative, without tick values, durations or percentiles.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Inference; CPU load; Deadline; Late result.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V03 — Receiver cannot see result age

Slide: 2 — Motivation. Save as `slides/images/V03.png`.

```text
Generate exactly ONE image for V03. Do not create variants or a second image.
UNIQUE SUBJECT: A receiver sees a result payload whose age is missing.
MUST NOT SHOW: CPU load lanes, crashes, two-timer monitor, AoI sawtooth, boards.
ASPECT RATIO: 1:1.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Make a compact icon: a result envelope enters a simple receiver box. Beside the envelope show a large clock outline with a question mark; the payload has no timestamp. This illustrates missing freshness information, not the actual timestamped project protocol. Use navy and teal, no orange.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Result; Receiver; Age?.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V04 — Linux hang stops a colocated monitor

Slide: 2 — Motivation. Save as `slides/images/V04.png`.

```text
Generate exactly ONE image for V04. Do not create variants or a second image.
UNIQUE SUBJECT: A hang freezes both a Linux process and its same-domain checker.
MUST NOT SHOW: Late-result timeline, receiver-age icon, external MCU supervisor, boards.
ASPECT RATIO: 1:1.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw a single Linux domain box containing a process tile and a monitor tile, both visibly paused. Use an orange fault mark spanning the shared boundary to show both are affected by one hang. Keep this a sparse compact icon, with no UART or other platform.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Linux; Process; Monitor; Hang.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V05 — Private L2 versus shared L3 and DRAM

Slide: 5 — Multicore contention. Save as `slides/images/V05.png`.

```text
Generate exactly ONE image for V05. Do not create variants or a second image.
UNIQUE SUBJECT: Shared-memory fan-in persists despite separate CPU cores.
MUST NOT SHOW: PCB rendering, two-domain architecture, scheduling lanes, benchmarks, invented cache capacities.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Use a chip-level block schematic, no board. Four Cortex-A76 core boxes each connect to their own private L2 box. All four L2 branches converge on one shared L3 box and then one shared LPDDR4X memory box. Emphasise the shared bottleneck with thicker navy branches, not orange. Omit capacity/frequency numbers.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: BCM2712; Cortex-A76; Private L2; Shared L3; LPDDR4X; Shared bandwidth.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V06 — Related-work concept map

Slide: 4 — Related work. Save as `slides/images/V06.png`.

```text
Generate exactly ONE image for V06. Do not create variants or a second image.
UNIQUE SUBJECT: Four research strands converge on the planned evaluation question.
MUST NOT SHOW: Author lists, paper screenshots, published timing figures, experiment matrix, architecture, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Arrange four readable concept cards around a central evaluation card: separate supervisor, data freshness, shared-memory interference, and RT scheduling. Link them toward the centre as intellectual motivation rather than runtime data flow. Use neutral line and clock symbols; no numerical claims or outcomes.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Simplex; Age of Information; Multicore interference; PREEMPT_RT; End-to-end evaluation.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V07 — Three research questions

Slide: 3 — Problem statement. Save as `slides/images/V07.png`.

```text
Generate exactly ONE image for V07. Do not create variants or a second image.
UNIQUE SUBJECT: Three question cards frame contention, tuning and fault reaction.
MUST NOT SHOW: Research-paper map, experiment IDs, results, process architecture, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Create three equal spacious cards in one row with abstract icons: competing arrows, tuning sliders, and a shield beside a clock. Each has one question label. Use navy and teal; no fault event is being depicted, so no orange.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Contention delay?; OS tuning benefit?; Bounded fault reaction?.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V08 — Two-domain authority architecture

Slide: 6 — Architecture. Save as `slides/images/V08.png`.

```text
Generate exactly ONE image for V08. Do not create variants or a second image.
UNIQUE SUBJECT: Ownership boundaries show that STM32 has final output authority.
MUST NOT SHOW: Sequential capture-to-action strip (V10), board portraits, pinout, physical bench, latency charts.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw two large domain containers. Linux contains Source, Inference, Bridge and Stressors; FreeRTOS contains UART RX, Supervisor, Status and Safe output. The UART proposal arrow enters UART RX, then Supervisor gates Safe output. A return status arrow leads back to Bridge. Make the final-authority relationship dominant. These are abstract software boxes, no PCB icons; omit timing wire and physical pins.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Linux; FreeRTOS; Source; Inference; Bridge; Stressors; UART RX; Supervisor; Status; Safe output; UART; Proposals; Final authority.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V09 — Complete cooled hardware rig

Slide: 7 — Hardware. Save as `slides/images/V09.png`.

```text
Generate exactly ONE image for V09. Do not create variants or a second image.
UNIQUE SUBJECT: The complete physical bench assembly with cooling and power.
MUST NOT SHOW: Software boxes, arrows for execution stages, enlarged labelled pinout (V22), logic analyzer (V23), measured results.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Show a flat technical bench illustration, oblique top view: real Pi 5 with official Active Cooler fitted, real Nucleo-F446RE with attached debugger, a simple USB-C power supply for the Pi and an unlabelled USB cable from a Pi USB-A port to Nucleo ST-LINK mini-USB. Keep UART jumpers, shared ground and one timing jumper visually present as thin unlabelled wires, no pin-position claims. Ethernet and HDMI remain unconnected. Label only the main objects. Active cooler must be a black/silver heatsink with a small black blower fan, not a large PC fan.

BOARD KEY FACTS: Pi 5 = green credit-card PCB, central metal-lidded BCM2712 plus separate RP1, long-edge 40-pin GPIO, short-edge stacked blue USB 3.0 / black USB 2.0 and Ethernet jack, opposite-edge USB-C / two micro-HDMI with two MIPI FPC connectors nearby, separate PCIe FPC, power button and fan header. No blue/red/black Pi PCB or full-size HDMI. Nucleo-F446RE = white Nucleo-64 PCB, attached upper ST-LINK/V2-1 with mini-USB, central black LQFP64 STM32F446RE, blue USER / black RESET, Arduino female and bilateral morpho male headers, green LD2. No green Nucleo or Blue Pill. No invented logos, brand text or tiny silkscreen; only the allowed labels.

ALLOWED LABELS ONLY: Raspberry Pi 5; Active cooler; STM32 Nucleo-F446RE; Power; UART.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V10 — Life of one input through the data path

Slide: 8 — Data path and AoI. Save as `slides/images/V10.png`.

```text
Generate exactly ONE image for V10. Do not create variants or a second image.
UNIQUE SUBJECT: One result travels from input capture to the MCU output.
MUST NOT SHOW: System ownership containers (V08), complete bench rig, AoI plot (V20), profile ladder, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw a single left-to-right strip: Capture, Inference, Buffer, UART, Supervisor, Output. Carry one teal input token through the stages; place symbolic t_input at capture and t_action at output. A light bracket spanning capture to output denotes the age of that same input at action. No branch network, domain boxes, return status lane or numerical timing.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Capture; Inference; Buffer; UART; Supervisor; Output; t_input; t_action; Input age at action.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V11 — Stock versus tuned CPU scheduling

Slide: 10 — Runtime profiles. Save as `slides/images/V11.png`.

```text
Generate exactly ONE image for V11. Do not create variants or a second image.
UNIQUE SUBJECT: Qualitative scheduler lanes compare dispatch opportunities.
MUST NOT SHOW: Profile dependency ladder (V12), tuning checklist (V13), queue storage (V14), memory hierarchy, numeric timing, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Use two aligned conceptual CPU lanes: stock has bridge work interleaved with competing work; tuned shows the ready bridge dispatched ahead of ordinary load. Equal visual width is only compositional, not a duration claim. Use a distinct teal bridge block and navy workload blocks; no axes or claimed latency reduction.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Stock; Tuned; Bridge; Other work; SCHED_OTHER; SCHED_FIFO; Conceptual.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V12 — Branched runtime-profile ladder

Slide: 10 — Runtime profiles. Save as `slides/images/V12.png`.

```text
Generate exactly ONE image for V12. Do not create variants or a second image.
UNIQUE SUBJECT: P2 and P3 independently branch from P1.
MUST NOT SHOW: CPU execution bars (V11), detailed knobs (V13), linear P0-P1-P2-P3 chain, results, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw a sparse dependency ladder: P0 stock below P1 tuned, then separate branches from P1 to P2 latest value and P3 RT kernel. Label the first edge OS tuning, the P2 edge Buffer, the P3 edge Packaged PREEMPT_RT. Do not connect P2 to P3: P3 is P1 on the packaged RT kernel, not P2 plus RT.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: P0 stock; P1 tuned; P2 latest value; P3 RT kernel; OS tuning; Buffer; Packaged PREEMPT_RT; DESIGN.
No added measurements, numbers, captions, watermarks or miniature text.
```

