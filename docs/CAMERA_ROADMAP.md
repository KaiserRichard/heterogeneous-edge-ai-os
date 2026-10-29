# Roadmap: Pi Camera v2 source, bench rig and final tests (Nov 2026)

Written 2026-10-29 (Claude, from the OS/CN handoff). Deadline: report + demo end of Nov 2026
(owner, 2026-10-29). Drafts in English; the submitted report is Vietnamese.
Scenario tables: [TEST_SCENARIOS.md](TEST_SCENARIOS.md) (English) and
[TEST_SCENARIOS_VI.md](TEST_SCENARIOS_VI.md) (Vietnamese, for the report).
Tickets: `docs/tickets/CAM1..` (one ticket = one worktree + `feat/<topic>` branch).

## Where we start (checked 2026-10-29)

| Item | Status | Evidence |
|---|---|---|
| Linux pipeline, protocol, supervisor host tests | KNOWN: on `release/os-final` (PR #6) | `make test` |
| Source of frames | KNOWN: synthetic (`hea_source` sends `frame_id,t_input_ns`, no pixels) | `linux/src/hea_source.c` |
| Pi reachable as `wbr-pi5`, Ubuntu 24.04.4, kernel 6.8.0-1065-raspi, `throttled=0x0` at idle | MEASURED | `ssh wbr-pi5` 2026-10-29 |
| RAM on `wbr-pi5` | MEASURED `free -g` total 3 GiB, so this is the **4 GB** board, not the 8 GB one used for the old results | same |
| IMX219 seen by the kernel | MEASURED: no `imx219` line in `dmesg` (camera not plugged) | same |
| libcamera / rpicam-apps | MEASURED: no packages, no `rpicam-hello` | `dpkg -l` |
| `camera_auto_detect=1` in `/boot/firmware/config.txt` | MEASURED | same |
| Nucleo flash tool on the Pi | MEASURED: UART system bootloader via WBR `stm32boot.py` (BOOT0 high + RESET by hand); ST-LINK path unreliable | `~/wbr-evidence-archive/f446-home-test-20261029/05-*.txt` |
| Firmware now on the Nucleo | UNKNOWN exact image. Last write 2026-10-29 was WBR `agv_f446_home_canfix01.bin` (SHA256 `f614cde0…f296`); backup before it `94b25d8c…3006`. Neither matches the handoff hash `fcc29359…2517e`. | archive SHA256SUMS |
| OS firmware LEDs | KNOWN: two-wire code on PA5 (LD2) + PB5 (= D4) | `stm32/firmware/main.c:98` |
| Old gaps | real-UART freshness FLAGGED; review fixes not flashed; inference baseline invalid (throttle 0x50000); input policy under load UNKNOWN | `docs/STAGE_REPORT.md` |

Bench pins (Nucleo-F446RE, UM1724 Arduino/Morpho tables; SOURCE-SUPPORTED, recheck on the board):
D4=PB5 green, D5=PB4 yellow, D6=PB10 red, D9=PC7 blue; UART1 PA9 (D8, TX) / PA10 (D2, RX)
to Pi pins 10/8; I2C1 SCL PB6 (D10), SDA PB7 (CN7-21); CAN1 PB8/PB9 (D15/D14); CAN2 PB12/PB13
(CN10-16/CN10-30); clock-sync Pi GPIO17 (pin 11) -> PA0 (TIM2_CH1), wiring UNKNOWN.

## Decisions recorded here
- **AoI origin = libcamera `SensorTimestamp`** (start of exposure of the first line, ns),
  mapped to `CLOCK_MONOTONIC`. Assumption: on Pi kernels the V4L2 buffer timestamp is
  monotonic and BOOTTIME = MONOTONIC while the Pi never suspends. CAM2 records both clocks
  at startup and `t_recv_mono` per frame; the assumption is falsified if
  `t_recv - t_sensor` is negative or not bounded by about one frame period + readout. Then
  the origin falls back to `t_recv_mono` and the report says so.
- **OS-T8 CAN output is an approved extra** (owner, 2026-10-29). The Pi-MCU bridge stays UART
  only; CAN carries supervisor state out of the MCU and never feeds back. This is the only
  exception to the AGENTS.md "No CAN" rule.
- Camera work runs on the Pi only after the WBR demo (31 Oct); until then tickets build and
  test on the Mac.
- Every firmware switch: back up flash first, hash it, then write, then verify read-back.

## Phases

Legend: **[HANDS]** = needs the owner physically; **[CONFIRM]** = owner types a confirmation.

### Phase 0 — software on the Mac (29 Oct – 1 Nov, no bench)
- CAM1: camera source with a fake backend + real libcamera backend (compiled on Pi in phase 1).
- FW1: LED remap to D4/D5/D6/D9 + firmware build + host tests.
- FW2: one-command firmware switch script (backup -> write -> verify) with a fake-bootloader test.
- Done when: the three tickets are merged into `release/os-final` after review, `make test` green.

### Phase 1 — camera bring-up on the Pi (from 1 Nov)
- **[HANDS] H1**: power off the Pi, connect Pi Camera v2 to CAM/DISP 0 with a 22-to-15-pin cable.
- CAM0 (conductor on the Pi): `dmesg | grep -i imx219`, then build Raspberry Pi's `libcamera`
  + `rpicam-apps` from source into `/opt/rpi-cam` (does not touch WBR ROS paths), then
  `rpicam-hello --list-cameras`, `rpicam-still -o /tmp/t.jpg`. Fix from the actual errors.
  Fallback: Raspberry Pi OS on a spare card (needs H-card from the owner).
- Build CAM1's real backend on the Pi; run OS-T1.
- Done when: OS-T1 passes and the AoI-origin check above holds or the fallback is recorded.

### Phase 2 — Pi-only measurements (camera, no MCU)
- **[HANDS] H2**: confirm which Pi 5 (4 GB vs 8 GB) and PSU are used for the report runs, and
  that the active cooler is fitted. The old results used the 8 GB board.
- INF1: clean inference baseline on camera frames (OS-T2), throttle check before/after.
- Rerun OS-T3 (P0 vs P1 under stress-ng) and OS-T4 (FIFO vs latest-value, bridge and input
  side) with the camera source. Uses the existing `tools/experiments` runners.

### Phase 3 — supervisor firmware on the bench
- **[HANDS] H3**: confirm LED resistor values and D9 colour; check whether GPIO17 -> PA0 is wired.
- **[CONFIRM] + [HANDS] H4**: `CONFIRM flash nucleo os-supervisor`, then BOOT0 high + RESET for the
  FW2 script; it backs up the WBR image, writes the OS image and verifies. Switching back to WBR
  is the same script with the WBR image.
- Run OS-T5 (UART link validity) and OS-T6 (fault injection -> LEDs, MCU-timestamped). This
  closes the "review fixes not flashed" and "real-UART FLAGGED" gaps if the runs pass.

### Phase 4 — rig extras (only after phase 3 passes)
- FW3: MPU6050 sampling task (OS-T7).
- FW4 + **[HANDS] H5**: connect CAN1 and CAN2 transceivers on one bus (CANH-CANH, CANL-CANL,
  120 Ω at each end); FAILSAFE as a CAN frame (OS-T8).

### Phase 5 — report and demo (16 – 30 Nov)
- RPT1: English draft chapter "Camera source and bench results" with the scenario table and
  measured numbers (owner reviews).
- RPT2: Vietnamese submission version (English technical terms kept, glossary), slides,
  demo script (camera -> inference -> bridge -> LEDs).

## Codex tickets per phase

| Phase | Ticket | Account tier | Runs where | Depends on |
|---|---|---|---|---|
| 0 | CAM1 camera source | hard (codex-e) | Mac (fake backend) | — |
| 0 | FW1 LED remap | medium | Mac (arm-none-eabi-gcc, host tests) | — |
| 0 | FW2 firmware switch script | medium | Mac (fake bootloader) | — |
| 1 | CAM0 libcamera build | conductor (needs Pi, network) | Pi | H1 |
| 2 | INF1 camera inference baseline | medium | Pi (conductor runs) | CAM1, CAM0 |
| 4 | FW3 MPU6050 task | medium | Mac build, bench run | FW1 |
| 4 | FW4 CAN state output | medium | Mac build, bench run | FW1, H5 |
| 5 | RPT1 / RPT2 report chapters | medium | Mac | phase 2–3 data |

Each ticket needs one review by a different account before merge.
