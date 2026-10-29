# Bench runbook: plug in and run (OS + CN camera)

Staged on the Pi (`wbr-pi5`) on 2026-10-29: `~/course-stage/os` (branch `feat/camera-source`,
built: `linux/`, fake camera backend), `~/course-stage/fw` (images + `SHA256SUMS` + `nucleo_switch.py`).

| Image | SHA256 | Use |
|---|---|---|
| `os-supervisor-fw1-HSE.bin` | `0681be78…c9df` | OS supervisor, LEDs D4/D5/D6/D9, USART1 921600, clock from ST-LINK MCO |
| `os-supervisor-fw1-HSI.bin` | `f392b681…c127` | same, internal RC clock (use if HSE build gives no UART frames) |
| `wbr-agv_f446_home_canfix01.bin` | `f614cde0…f296` | switch back to WBR micro-ROS |

Note: the OS link is **921600 baud** (`stm32/firmware/Makefile`), not 115200 (that is WBR).

## 0. Before anything (Pi)
```bash
vcgencmd get_throttled            # expect throttled=0x0
date                              # the Pi clock was ~1 h behind on 2026-10-29 (no NTP)
```

## 1. Camera (owner: power off, connect Pi Camera v2 to CAM/DISP 0, 22-to-15-pin cable, boot)
```bash
dmesg | grep -i imx219            # expect: imx219 ... probe / registered
PROXY= bash ~/course-stage/os/scripts/pi/camera_setup.sh   # needs internet + your approval; ~30-40 min
. /opt/rpi-cam/env.sh && rpicam-hello --list-cameras       # expect: 0 : imx219 [3280x2464 ...]
cd ~/course-stage/os && make -C linux/camera               # now builds the libcamera backend
```
Decision: no `imx219` in dmesg -> reseat the cable (contacts face the board on Pi 5 side, check
both ends), then `dtoverlay=imx219,cam0` in `/boot/firmware/config.txt` if auto-detect fails.

## 2. OS-T1 (camera timing)
```bash
cd ~/course-stage/os && mkdir -p results/$(date +%F)_os_t1_camera
linux/camera/build/hea_cam --backend libcamera --fps 30 --width 640 --height 480 \
  --shm hea_cam --output /tmp/hea_src.sock --csv results/$(date +%F)_os_t1_camera/frames.csv --count 9000
python3 linux/camera/analyze_t1.py results/$(date +%F)_os_t1_camera/frames.csv --fps 30 \
  --output results/$(date +%F)_os_t1_camera/summary.json
```
Pass criteria: `docs/TEST_SCENARIOS.md` OS-T1. Exact CLI flags: `linux/camera/README.md`.
A receiver must be bound to `--output` first: `hea_runtime` stops on the first failed `sendto`.
For timing only, start `python3 scripts/pi/hea_sink.py /tmp/hea_src.sock &` before `hea_cam`;
for the full pipeline start `linux/inference/infer_server.py --image-source shm:hea_cam` (README).
After a crash, remove the stale ring with `rm -f /dev/shm/hea_cam` (`open ring: File exists`).
The first frames after start carry libcamera `FrameStartup` (AGC/AWB settling); they are used.

## 3. Switch the Nucleo to the OS firmware (owner types `CONFIRM flash nucleo os-supervisor`)
Owner's hands: BOOT0 to 3V3 (jumper CN7-5 to CN7-7), press RESET when the script asks.
```bash
cd ~/course-stage/fw
python3 nucleo_switch.py --port /dev/ttyAMA0 --image os-supervisor-fw1-HSE.bin \
  --expect-sha256 0681be7834f20d6d525457a466c17de459977f51484977cf947a190df3d1c9df \
  --archive ~/wbr-evidence/nucleo-switch-$(date +%Y%m%d)
```
Then BOOT0 back to GND, RESET. Expect: all LEDs off (INIT), green D4 once the bridge runs.
Switch back to WBR: same command with `wbr-agv_f446_home_canfix01.bin` and its SHA256.

## 4. OS-T5 / OS-T6 on the bench
Use `scripts/pi/run_pipeline.sh` and `scripts/pi/fault_inject.sh` with `UART_BAUD=921600`;
scenarios and pass criteria in `docs/TEST_SCENARIOS.md`.
