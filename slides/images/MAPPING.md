# Image mapping and visual quality review

All 24 originals were opened individually with the image viewing tool before resizing. Assignment uses visible content; suffixes were secondary hints. Renames are archival assignments, not approval of defective illustrations. `yes` means the subject fits; it does not certify exact compliance with every style/label instruction. Hardware checks are visual asset checks only, not physical rig validation.

## Mapping

| V-id | Original filename | What the image shows | Fits intended slot? | Hardware check |
|---|---|---|---|---|---|
| V01 | Kết nối Raspberry Pi và STM32-1.png | Cooled green Pi-like board and white Nucleo-like board joined by three jumpers, with floating neural-network and timing panels. | partial | Green/white colours and blue USER/black RESET present; oversized axial cooler, questionable HDMI/port geometry, invented board silkscreen; mini-USB fidelity uncertain. |
| V02 | Dòng xe hỗn loạn, tàu đúng nhịp-2.png | Busy multilane roads labelled Throughput versus a train with clocks labelled Determinism. | no | N/A: no target boards. |
| V03 | Băng chuyền phong bì chờ xử lý-3.png | Clock-bearing envelopes queue on a conveyor into a receiver machine; a person handles an orange envelope. | partial | N/A: abstract machines. |
| V04 | Xung đều, dữ liệu cũ-4.png | Two panels compare a pulsing computer connected to a green MCU-like board with a frozen computer and warning/old retained bars. | partial | Generic green MCU board with display; not white Nucleo-F446RE; no identifiable Pi. |
| V05 | Nút thắt bộ nhớ CPU bốn lõi-5.png | Four core blocks and small unlabelled cache-like blocks feed Shared L3, then a DIMM-like Memory module through a glowing bottleneck. | partial | Conceptual chip/DIMM, not Pi or Nucleo; DIMM must not imply actual Pi LPDDR4X package. |
| V06 | Sơ đồ kiến trúc Simplex an toàn-6.png | Complex subsystem and separately housed safety supervisor feed a decision block and motor actuator. | partial | N/A: abstract subsystem housings and motor. |
| V07 | Bận rộn, giám sát thời gian-7.png | Busy office worker amid paperwork; standing observer holds stopwatch and clipboard beside a status light. | no | N/A: no target boards. |
| V08 | Sơ đồ kiến trúc Linux–FreeRTOS-8.png | Linux Source/Inference/Bridge/Stressors domain links by UART to FreeRTOS UART RX/Supervisor/Status/Failsafe domain. | partial | No boards; cable connectors are decorative, not validated hardware endpoints. |
| V09 | Raspberry Pi and STM32 Test Bench-10.png | Desk rig with cooled green Pi-like board, white Nucleo-like board, jumpers, analyzer box/probes and laptop showing qualitative traces. | partial | Green/white boards and button colours present; generic axial cooler, full-size-looking HDMI, invented tiny silkscreen; Nucleo USB shape not reliably mini-B. |
| V10 | Sơ đồ đường ống chín trạm-10.png | Nine-stage Capture/Inference/Buffer/UART/ISR/Parse/Supervisor/Output/Status pipeline with AoI bracket and Status-to-Buffer return. | partial | N/A: conceptual stage icons; DB9 icon is not project GPIO wiring. |
| V11 | So sánh lịch CPU Stock và Tuned-11.png | Stock has irregular interleaved coloured work on four lanes; Tuned has regularly spaced teal work on an isolated lane and grey work below. | partial | N/A: no boards. |
| V12 | Sơ đồ phân nhánh bốn thẻ-12.png | P0 Stock flows to P1 Tuned; independent buffering and kernel branches lead to P2 Latest value and P3 RT kernel. | yes | N/A: no target boards. |
| V13 | Locked memory in RAM-1.png | Padlocked teal pages remain on a RAM-module metaphor while other pages move to and from a hard disk. | partial | Generic RAM and disk metaphor; no target boards. |
| V14 | FIFO queue versus latest value-2.png | FIFO tube retains a line of ageing envelopes; single latest-value box replaces an older envelope with a teal new one. | yes | N/A: no boards. |
| V15 | Eight-field protocol packet with CRC coverage-3.png | Frame fields A5, 5A, Ver, Type, Seq, Len, Payload, CRC-16; bracket spans Ver through Payload; magnifier highlights a payload cell. | yes | N/A: no boards. |
| V16 | FreeRTOS task priority ladder-4.png | Supervisor above UART RX, Status and Idle on a priority ladder; interrupt icon and small buffer feed UART RX. | no | N/A: no boards. |
| V17 | Heartbeat and freshness timing-6.png | Heartbeat pulses continue while result-age sawtooth stops resetting, rises through threshold and is marked stale detected. | partial | N/A: no boards. |
| V18 | Data freshness state machine-5.png | INIT→FRESH, FRESH↔HOLD, FRESH/HOLD→FAILSAFE, and explicit rearm FAILSAFE→INIT, with readable transition labels. | yes | N/A: no boards. |
| V19 | Linux–STM32 timing exchange-7.png | Linux and STM32 lifelines exchange T1→T2 and T3→T4 arrows with separate GPIO-edge pulse below. | partial | N/A: no boards. |
| V20 | Sawtooth age-of-information threshold chart-8.png | Illustrative age/time sawtooth drops to nonzero ages at marked arrivals, with dashed threshold and orange above-threshold regions. | yes | N/A: no boards. |
| V21 | Four-Panel Engineering Systems Diagnostics-9.png | Four metaphor panels labelled E1 Contention, E2 Tuning & kernel, E3 Freshness and E4 Fault injection. | partial | N/A: no target boards. |
| V22 | Kết nối Raspberry Pi 5–STM32 Nucleo-9.png | Cooled green Pi-like and white Nucleo-like boards with TX/RX/GND/SYNC jumpers and a USB cable. | partial | Board colours/buttons present; two full-size-looking HDMI ports, generic axial cooler and tiny fake silkscreen; exact header endpoints are guessed. |
| V23 | Heartbeat fault response timing diagram-11.png | Heartbeat stops at Fault; State steps and Output changes later; Reaction time bracket spans fault to output. | partial | N/A: no boards or analyzer. |
| V24 | Five-stage engineering roadmap-12.png | Design checked complete, Software partially filled, then pending Bring-up, Experiments and Report along a roadmap. | partial | N/A: generic circuit icon, not a target board. |

## Assignment conflicts and gaps

- The language/suffix hypothesis is not fully correct: Vietnamese suffix 9 becomes V22 and English suffix 10 becomes V09; English suffix 6 becomes V17 and English suffix 5 becomes V18. All other assignments preserve the proposed order.
- V09 and V22 both depict the board pair. The English test bench is the stronger complete-rig match; the Vietnamese TX/RX/GND/SYNC drawing is the stronger wiring-detail match. Neither meets the current prompt. The analyzer-equipped bench also fits part of V23, but it lacks the required fault/decision/output callouts; assigning it to V23 would leave an even weaker V09. V23 retains the qualitative fault-response timing image as a partial fit.
- No fitting image exists for V02 late inference/deadline, V07 three research questions, or V16 supervisor output gate. No exact image exists for V03 unknown age, V04 colocated frozen monitor, V06 related-work map, V13 full P1 checklist, V17 separate timer icons, V21 intervention/metric matrix, V22 endpoint wiring, or V23 common-clock external observation. Partial rows retain related concepts and explicitly record the gap.
- Substantial content overlap: V01/V09/V22 repeat a cooled paired-board composition; V03/V14 repeat queued clock-bearing envelopes; V17/V20 repeat age sawtooths. Keep V09 as the rig, V14 as the storage comparison and V20 as AoI; regenerate the other members for their distinct subjects.

## Regenerate

Use the STYLE GUIDE and HARDWARE REFERENCE from the same part, then the single original V prompt linked below. Do not regenerate by continuing the previous chats.

| Image | Source prompt | Reason |
|---|---|---|
| V01 | [PART_A.md — V01](../image-prompts/PART_A.md) | Extra panels/cooler instead of bare-board emblem; hardware/silkscreen defects; substantially repeats V09/V22 board-pair composition. |
| V02 | [PART_A.md — V02](../image-prompts/PART_A.md) | No inference execution lane, deadline or late result; broad transport metaphor. |
| V03 | [PART_A.md — V03](../image-prompts/PART_A.md) | Shows visible clocks/backlog rather than unknown age; substantially overlaps V14 FIFO storage; not a compact square receiver icon. |
| V04 | [PART_A.md — V04](../image-prompts/PART_A.md) | Wrong MCU depiction; external monitor instead of both process and colocated checker frozen inside Linux; wrong aspect ratio. |
| V05 | [PART_A.md — V05](../image-prompts/PART_A.md) | Private L2 is unlabelled; BCM2712/Cortex-A76/LPDDR4X identity missing; generic DIMM metaphor obscures actual memory hierarchy. |
| V06 | [PART_A.md — V06](../image-prompts/PART_A.md) | Simplex-only architecture; missing four-strand related-work concept map; motor application scene outside current prompt. |
| V07 | [PART_A.md — V07](../image-prompts/PART_A.md) | No three research-question cards; office metaphor cannot express the intended questions. |
| V08 | [PART_A.md — V08](../image-prompts/PART_A.md) | Final output authority is not explicit; Status is misleadingly in series before Failsafe; return status path is unclear. |
| V09 | [PART_A.md — V09](../image-prompts/PART_A.md) | Wrong cooler/port rendering and fake silkscreen; power and ST-LINK USB cable missing; analyzer scene violates V09 prompt; overlaps V01/V22. |
| V10 | [PART_A.md — V10](../image-prompts/PART_A.md) | AoI bracket stops at Supervisor rather than Output; no same-input token or t_input/t_action; extra return lane/stages differ from one-result path. |
| V11 | [PART_A.md — V11](../image-prompts/PART_A.md) | No Bridge/Other work legend or policy labels; regular tuned spacing can imply guaranteed periodic dispatch rather than conceptual priority. |
| V13 | [PART_B.md — V13](../image-prompts/PART_B.md) | Only locked memory shown; missing scheduling priority, CPU affinity and cgroup CPU caps in P1 checklist. |
| V16 | [PART_B.md — V16](../image-prompts/PART_B.md) | Task priority diagram is not supervisor proposal-to-GPIO/LED authority gate; no fitting gate image exists. |
| V17 | [PART_B.md — V17](../image-prompts/PART_B.md) | Not the separate timer-pair square icon; substantially overlaps V20 sawtooth and resets age to zero, suggesting zero delivery age. |
| V21 | [PART_B.md — V21](../image-prompts/PART_B.md) | Missing intervention-to-metric matrix, PLAN label and metric families; E3 says freshness rather than buffering. |
| V22 | [PART_B.md — V22](../image-prompts/PART_B.md) | Wrong board details; substantially repeats V01/V09; missing GPIO14→PA10, GPIO15←PA9, GPIO17→PA0 endpoint labels; no fitting signal-endpoint diagram exists. |
| V23 | [PART_B.md — V23](../image-prompts/PART_B.md) | Standalone timing diagram lacks external analyzer, external fault marker and common-clock observation setup required by current V23 prompt. |
| V24 | [PART_B.md — V24](../image-prompts/PART_B.md) | Too generic/outdated status: omits done Protocol tests/CI, in-progress Supervisor v2 and pending rig/firmware/bridge/E1–E4. |

## Remaining per-image quality checks

- V12: branch topology is correct (P2 and P3 independently derive from P1); labels are readable. Minor prompt omissions: Packaged PREEMPT_RT and DESIGN. No numerical performance claim.
- V14: storage/replacement subject is clear and text readable. Old/New/Next to send labels would improve clarity; orange ageing envelopes depart from the prompt palette. No claimed freshness bound.
- V15: field ordering and CRC bracket coverage are correct. SOF, CRC coverage, ≤64 B and DESIGN labels are omitted; illustrative payload cells contain no fabricated byte values. A5/5A and CRC-16 are protocol identifiers, not measurements.
- V18: transition topology and explicit rearm are correct; no automatic FAILSAFE-to-FRESH recovery. Latched and DESIGN labels are omitted, although double-ring FAILSAFE and rearm convey latching. Text is readable and there are no numerical thresholds.
- V19: four timestamp exchange and separate GPIO concept fit; ECHO_REQ/ECHO_RESP, Offset + drift, UART and Timer capture labels are missing. No claimed synchronization accuracy. Useful as a partial illustration; refine if exact prompt compliance is needed.
- V20: drops stay above zero and threshold violations are qualitative. Readable illustrative label; no numeric axes or measurement claim. Fresh arrival label/dots differ from requested labels but arrival triangles convey the event.
- Across all 24 images: no visible robot, robot text, or invented numerical measurements found. Numbers on V10 are stage indices, V12 profile IDs, V15 protocol identifiers, V19 timestamps and V21 experiment IDs. Main diagram text is readable; tiny generated board silkscreen in V01/V09/V22 is the fake-text concern. Generic laptop/analyzer traces in V09 are invented illustrations, not validated captures.

## File validation

- Before processing: 40,779,601 bytes of regular files (including .DS_Store).
- Every source was resized with `sips -Z 1920` before moving; PNG retained. All resulting images are 1920 × 1080 (16:9), so V03/V04/V16/V17 also need their specified square aspect ratio when regenerated.
- Exactly V01–V24 (now JPEG, quality 85), MAPPING.md and the preserved .gitkeep remain. .DS_Store was removed. No deck or prompt files were edited; no commit was made.

- Applied lossless PNG recompression after sips; decoded pixels were verified identical for each image.
