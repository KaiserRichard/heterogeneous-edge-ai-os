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

# PART B: V13–V24

This file is self-contained for a fresh image-generation chat. First paste STYLE GUIDE and HARDWARE REFERENCE together as setup and ask the session to acknowledge them without generating an image. Then paste only one fenced prompt per message, in V-number order. Wait for the image and save it before sending the next prompt. Never send “continue,” several prompts together, or the whole file as a generation request. On repetition, start a fresh chat, paste both setup blocks again, and send only the current V prompt. The other part is not required.

## V13 — P1 tuning mechanisms checklist

Slide: Backup — Supporting illustrations. Save as `slides/images/V13.png`.

```text
Generate exactly ONE image for V13. Do not create variants or a second image.
UNIQUE SUBJECT: A mechanism checklist explains the contents of P1 only.
MUST NOT SHOW: Profile ladder (V12), stock/tuned execution lanes (V11), kernel build imagery, numerical gains, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Create one P1 card with four large icon-and-label entries: bridge scheduling priority, CPU affinity, cgroup CPU caps and locked memory. Show simple priority arrow, core placement, quota boundary and lock symbols. Priority 50 is the only numerical design setting allowed. No profile branches or P2/P3 cards.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: P1 tuned; SCHED_FIFO; Priority 50; CPU affinity; cgroup CPU caps; mlockall; DESIGN.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V14 — FIFO storage versus latest-value replacement

Slide: 11 — Queue vs latest value. Save as `slides/images/V14.png`.

```text
Generate exactly ONE image for V14. Do not create variants or a second image.
UNIQUE SUBJECT: Buffer contents show retention versus overwrite of unsent data.
MUST NOT SHOW: CPU scheduling lanes, AoI sawtooth, profile ladder, packet fields, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Compare two storage diagrams in one image. FIFO retains several unsent result cards ordered from old to new; the oldest is next to transmit. Latest value has a single slot holding the newest card, with a neutral dashed discarded-old card outside the slot. Dropping an unsent old card is normal policy, so use navy/teal rather than fault orange. Do not claim a hard freshness bound.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: FIFO queue; Old; New; Next to send; Latest value; Unsent old replaced.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V15 — UART frame anatomy and CRC coverage

Slide: Backup — Supporting illustrations. Save as `slides/images/V15.png`.

```text
Generate exactly ONE image for V15. Do not create variants or a second image.
UNIQUE SUBJECT: The on-wire frame fields and integrity coverage, not wiring.
MUST NOT SHOW: Physical connectors, boards, queue comparison, supervisor logic, clock exchange, fabricated bytes.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Create a clean horizontal segmented frame: SOF containing A5 5A, then ver, type, seq, len, payload, CRC-16. Allow payload ≤ 64 B as a design limit. Put a simple bracket above ver through payload labelled CRC coverage; exclude SOF and the transmitted CRC field from that bracket. Keep fields symbolic, with no invented sequence values or payload contents.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: SOF; A5 5A; ver; type; seq; len; payload; ≤ 64 B; CRC-16; CRC coverage; DESIGN.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V16 — Supervisor gates the simulated output

Slide: 13 — Supervisor. Save as `slides/images/V16.png`.

```text
Generate exactly ONE image for V16. Do not create variants or a second image.
UNIQUE SUBJECT: A compact authority gate controls a GPIO/LED output.
MUST NOT SHOW: Full state machine (V18), paired stopwatches (V17), Nucleo board portrait, UART parser, architecture overview.
ASPECT RATIO: 1:1.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw a large shield-like supervisor gate receiving a small proposal arrow and controlling one simple GPIO/LED symbol. The gate-to-output link is the visual focus. No board silhouette, clock pair, states or timing values.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Supervisor; Proposal; GPIO / LED.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V17 — Independent liveness and freshness timers

Slide: 13 — Supervisor. Save as `slides/images/V17.png`.

```text
Generate exactly ONE image for V17. Do not create variants or a second image.
UNIQUE SUBJECT: Two separate timers can disagree: bridge alive, result stale.
MUST NOT SHOW: Full state machine (V18), supervisor shield gate (V16), AoI curve, board portraits.
ASPECT RATIO: 1:1.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Show two large adjacent stopwatch icons. Heartbeat has a teal check; Result age has an orange stale warning. Their separation must be obvious: a live bridge does not imply a fresh result. No numbered dials, thresholds or timeout values.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Heartbeat; Result age; Alive; Stale.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V18 — Latched supervisor state transitions

Slide: Backup — Supporting illustrations. Save as `slides/images/V18.png`.

```text
Generate exactly ONE image for V18. Do not create variants or a second image.
UNIQUE SUBJECT: The supervisor transition topology includes explicit rearm.
MUST NOT SHOW: Two-stopwatch icon (V17), shield-output icon (V16), task priority graph, physical boards, invented thresholds.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw the planned state machine with legible generous spacing: INIT to FRESH labelled Valid data; FRESH to HOLD labelled Stale data; HOLD to FRESH labelled Fresh data; HOLD to FAILSAFE labelled Timeout; FRESH to FAILSAFE labelled Heartbeat lost; FAILSAFE back to INIT labelled Explicit rearm. FAILSAFE is orange and marked Latched. All other states use navy/teal. No automatic recovery arrow from FAILSAFE to FRESH and no numerical thresholds.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: INIT; FRESH; HOLD; FAILSAFE; Valid data; Stale data; Fresh data; Timeout; Heartbeat lost; Explicit rearm; Latched; DESIGN.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V19 — Clock exchange and independent GPIO check

Slide: Backup — Supporting illustrations. Save as `slides/images/V19.png`.

```text
Generate exactly ONE image for V19. Do not create variants or a second image.
UNIQUE SUBJECT: UART clock mapping is checked by a separate captured GPIO edge.
MUST NOT SHOW: AoI sawtooth, fault-analyzer rig (V23), physical pinout (V22), invented sync accuracy, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Use two abstract vertical clock lifelines labelled Linux clock and STM32 timer. A descending ECHO_REQ arrow goes from T1 to T2; ECHO_RESP returns from T3 to T4. Below, show a separate GPIO edge arrow landing on Timer capture, visually independent of UART. A small Offset + drift label links the exchange to clock mapping. No numerical offsets, measured errors, formulas with unmatched units, board icons or analyzer probes.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Linux clock; STM32 timer; T1; T2; T3; T4; ECHO_REQ; ECHO_RESP; UART; Offset + drift; GPIO edge; Timer capture.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V20 — Conceptual Age of Information sawtooth

Slide: 8 — Data path and AoI. Save as `slides/images/V20.png`.

```text
Generate exactly ONE image for V20. Do not create variants or a second image.
UNIQUE SUBJECT: AoI rises between arrivals and falls to the delivered input age.
MUST NOT SHOW: Capture-to-output strip (V10), FIFO storage panels (V14), latency histogram, measured ticks, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw one conceptual AoI curve on qualitative axes: straight rising ramps between fresh arrivals and downward jumps at arrivals, each ending above zero because delivery takes time. Add a dashed unspecified threshold and lightly shade time above it in orange as a freshness violation. Mark fresh arrivals with teal dots. No tick values, trace data, percentages or claim of a bounded age.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Age of Information; Time; Fresh arrival; Threshold; Above threshold; Conceptual.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V21 — Four-experiment plan matrix

Slide: 15 — Experiments. Save as `slides/images/V21.png`.

```text
Generate exactly ONE image for V21. Do not create variants or a second image.
UNIQUE SUBJECT: Four experiment rows map interventions to metric families.
MUST NOT SHOW: Results dashboard, numerical performance bars, hardware rig, profile ladder, literature map.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Make a sparse four-row plan matrix with icons and only short row labels: E1 contention to latency; E2 tuning / kernel to jitter; E3 buffering to AoI; E4 faults to failsafe latency. Keep this a planned-study map, not recorded outcomes. Only E4 uses an orange fault icon.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: PLAN; E1 Contention; Latency; E2 Tuning / kernel; Jitter; E3 Buffering; AoI; E4 Faults; Failsafe latency.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V22 — Signal-level UART and timing wiring

Slide: 7 — Hardware. Save as `slides/images/V22.png`.

```text
Generate exactly ONE image for V22. Do not create variants or a second image.
UNIQUE SUBJECT: An enlarged endpoint diagram specifies crossed UART and separate timing.
MUST NOT SHOW: Complete physical bench portrait (V09), chips/ports rendered as generic boards, USB bridge, Ethernet bridge, analyzer, software stages.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw connector endpoint boxes only, explicitly no PCBs or board silhouettes. Left box is Pi GPIO, right is STM32 pins. Connect GPIO14 TX to PA10 RX, GPIO15 RX to PA9 TX, shared GND to GND, and GPIO17 to PA0 with an arrow labelled Timer capture. UART directions must be visibly crossed TX-to-RX; timing is a separate teal path and GND a neutral navy line. This is a signal-level design diagram, not an exact header-hole map: do not add physical pin numbers or guessed connector positions.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Pi GPIO; STM32 pins; GPIO14 TX; GPIO15 RX; PA10 RX; PA9 TX; GND; GPIO17; PA0; UART; Timer capture; DESIGN.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V23 — External analyzer observes fault, decision and output

Slide: 16 — Failsafe latency. Save as `slides/images/V23.png`.

```text
Generate exactly ONE image for V23. Do not create variants or a second image.
UNIQUE SUBJECT: One external instrument timestamps all fault-reaction observations.
MUST NOT SHOW: Standalone t_f-to-t_s timeline, complete bench power/cooling portrait (V09), UART pinout (V22), clock-sync exchange (V19), measured traces.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Draw a simplified physical observation setup: accurate bare Pi 5 on left, accurate Nucleo-F446RE on right, and a generic unbranded logic analyzer below. Thin neutral inter-board UART jumpers remain in the background. Analyzer leads attach to abstract enlarged test-point callouts for an external fault marker, MCU decision marker and safe output; avoid claiming exact physical pin locations. All three observations feed the same instrument. Orange marks the injected Linux fault only. Explain through the fault-marker label that fault onset is externally marked, not reliably logged by frozen Linux. No waveform screen or numeric latency.

BOARD KEY FACTS: Pi 5 = green credit-card PCB, central metal-lidded BCM2712 plus separate RP1, long-edge 40-pin GPIO, short-edge stacked blue USB 3.0 / black USB 2.0 and Ethernet jack, opposite-edge USB-C / two micro-HDMI with two MIPI FPC connectors nearby, separate PCIe FPC, power button and fan header. No blue/red/black Pi PCB or full-size HDMI. Nucleo-F446RE = white Nucleo-64 PCB, attached upper ST-LINK/V2-1 with mini-USB, central black LQFP64 STM32F446RE, blue USER / black RESET, Arduino female and bilateral morpho male headers, green LD2. No green Nucleo or Blue Pill. No invented logos, brand text or tiny silkscreen; only the allowed labels.

ALLOWED LABELS ONLY: Raspberry Pi 5; STM32 Nucleo-F446RE; Logic analyzer; External fault marker; Decision marker; Safe output; One clock.
No added measurements, numbers, captions, watermarks or miniature text.
```

## V24 — Software progress and hardware next steps

Slide: 18 — Progress. Save as `slides/images/V24.png`.

```text
Generate exactly ONE image for V24. Do not create variants or a second image.
UNIQUE SUBJECT: A status roadmap separates host work from pending hardware evaluation.
MUST NOT SHOW: Dated project calendar, completion percentages, experiment result matrix, completed-hardware claims, boards.
ASPECT RATIO: 16:9.
Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.

COMPOSITION: Create a left-to-right status roadmap with three groups. Done: Design / research, Protocol tests, CI. In progress: Supervisor v2. Next: Rig setup, Firmware / bridge, E1–E4. Use teal checks for completed host work, navy outlined markers for ongoing and future work, and no orange. Provisioning scripts may be omitted to keep labels readable; do not imply they ran on hardware. No dates, assertion counts, percentage completion or measured results.

HARDWARE: No boards or PCB silhouettes; use only the specified abstract elements.

ALLOWED LABELS ONLY: Done; Design / research; Protocol tests; CI; In progress; Supervisor v2; Next; Rig setup; Firmware / bridge; E1–E4; HOST-TEST.
No added measurements, numbers, captions, watermarks or miniature text.
```

