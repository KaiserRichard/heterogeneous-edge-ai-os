# Environment and Hardware Plan

Status: PROPOSED (2026-10-05). Nothing in this file has been verified on hardware yet.

## 1. Does the Pi need to be carried and powered 24/7?

No. The Raspberry Pi 5 is only needed for measurements that must run on the
real Linux target (scheduling, contention, end-to-end latency). Everything
else runs on the Mac, on any Linux machine, or in CI.

Two workable modes; pick by whether you have a fixed place with power + Wi-Fi:

| Mode | How it works | Carrying | Recommended when |
|---|---|---|---|
| A. Parked rig | Pi 5 + Nucleo wired together permanently at home/lab, powered, reachable over the network (Tailscale). STM32 is flashed *from the Pi* (`openocd` / `st-flash`). | Nothing | You have a fixed desk with an outlet. **Preferred.** |
| B. Session-based | Pi is off and in the bag; powered only for a bounded hardware session (see section 3). | Per bring-list | No fixed place. |

Idle Pi 5 power is a few watts, so leaving a parked rig on is cheap. The
microSD is disposable, so the only risk of a power cut is losing results
that were not pushed yet; the run script (section 5) pushes results at the
end of every run.

## 2. Hardware inventory and what each part is for

| Item | Needed for | Notes |
|---|---|---|
| Raspberry Pi 5, 4 GB | Linux-side measurements | Separate from the WBR Pi. Disposable microSD. |
| Official 27 W USB-C PSU (5 V / 5 A) | Every Pi session | Under-voltage throttles the CPU and silently corrupts contention results. Every run logs `get_throttled`; a run with throttling is invalid. |
| Active cooler for Pi 5 | Every Pi session | `stress-ng` on 4 cores will thermally throttle without it. Temperature and frequency are logged per run. |
| microSD (>= 32 GB), pre-flashed | Every Pi session | Ubuntu Server 24.04 LTS arm64, provisioned once (section 4). |
| STM32F446RE Nucleo-64 | Any STM32 session | On-board ST-LINK gives flashing + a USB virtual COM port (USART2, PA2/PA3). |
| USB Mini-B cable | Any STM32 session | Nucleo-64 (MB1136) ST-LINK connector is Mini-B. |
| 4x female-female jumpers | Pi + STM32 sessions | TX, RX, GND, plus one GPIO "sync" line for clock alignment. |
| Logic analyzer (optional) | Pi + STM32 timing validation | Independent ground truth for UART latency and failsafe reaction time. |
| Network for the Pi | Every Pi session | Wi-Fi + Tailscale, or Ethernet to the same LAN as the Mac. |

## 3. Work split by hardware needed

### H0: No hardware (Mac or cloud). Most of the work lives here.
- Protocol spec, C framing/CRC library, host unit tests (started: `protocol/`).
- Linux bridge daemon logic, tested against a pseudo-terminal pair instead of a real UART.
- Supervisor/watchdog state machine written as plain C, unit-tested on the host, then reused in the FreeRTOS task.
- FreeRTOS firmware *compilation* (`arm-none-eabi-gcc`), no flashing.
- Experiment design, metric definitions (AoI, deadline-miss rate, failsafe latency), related work.
- Analysis scripts, developed against synthetic logs.

### S1: STM32 only. Bring: Nucleo-F446RE, USB Mini-B cable, Mac.
- Flash FreeRTOS, verify tick, task priorities, LED (LD2, PA5) as failsafe indicator.
- Protocol bring-up against a host tool on the Mac over the ST-LINK virtual COM port.
- Watchdog/failsafe tests: kill the Mac sender, measure detection on the STM32.
- Limitation: the ST-LINK virtual COM port goes through USB (1 ms full-speed frames), so latency numbers from S1 are functional only, not final measurements.

### P1: Pi only. Bring: Pi 5, 27 W PSU, active cooler, provisioned microSD, network.
- One-time provisioning check (section 4).
- Baseline inference latency, then under `stress-ng` contention.
- `SCHED_OTHER` vs `SCHED_FIFO`, CPU pinning, `cyclictest` baseline of the stock kernel.
- No STM32 needed: experiment directions 1 and 2 on the Linux side.

### PS1: Pi + STM32. Bring: everything in S1 and P1, plus 4 jumpers (and the logic analyzer if available).
- Direct 3.3 V UART: Pi GPIO14 (pin 8, TX) to STM32 RX, Pi GPIO15 (pin 10, RX) to STM32 TX, GND to GND. Both sides are 3.3 V; no level shifter. Proposed STM32 side: USART1 (PA9 TX / PA10 RX) so USART2 stays on the ST-LINK console.
- One extra GPIO from the Pi to an STM32 timer input-capture pin for clock alignment (see section 6).
- End-to-end AoI, deadline misses under contention, fault injection (kill bridge, freeze Linux), failsafe latency.
- The Nucleo can be powered and flashed from a Pi USB port, so the Mac is optional in this session.

Suggested order: H0 now, S1 whenever the Nucleo is at hand, P1 once, then PS1.
In mode A, S1/P1/PS1 all collapse into remote sessions on the parked rig.

## 4. Pi environment (one-time provisioning)

1. Flash Ubuntu Server 24.04 LTS (64-bit) with Raspberry Pi Imager. In the
   Imager settings: hostname `osedge`, user, your SSH public key, Wi-Fi,
   locale. Password login off.
2. First boot, then run `scripts/pi/bootstrap.sh` (installs the toolchain,
   diagnostics, `stress-ng`, `rt-tests`, `openocd`, `stlink-tools`, enables the
   GPIO UART). Reboot once.
3. Optional for mode A: install Tailscale so the Pi is reachable from anywhere.
4. Clone this repository on the Pi. Results go to `experiments/runs/` and are
   pushed from the Pi, so nothing depends on copying files by hand.

Kept out on purpose (per `PROJECT.md` non-goals): containers, PREEMPT_RT,
custom kernels.

## 5. How experiments run unattended

Every measurement goes through `scripts/pi/run_experiment.sh <name> -- <command>`:
- Runs detached from the SSH session (`systemd-run --user` or `tmux`), so a dropped connection does not kill or perturb the run.
- Captures metadata before and after: git commit, kernel, CPU governor and frequencies, temperature, `get_throttled`, load average, UART config.
- Writes everything to `experiments/runs/<UTC timestamp>_<name>/`.
- Marks the run INVALID if throttling or under-voltage was observed.
- Writes `DONE` into the run directory when it finishes. The Mac pulls results with
  `rsync -a osedge:heterogeneous-edge-ai-os/experiments/runs/ experiments/runs/`
  and commits them there, so the Pi needs no GitHub credentials (`HEA_PUSH=1` pushes from the Pi instead).

Measurement hygiene: `performance` CPU governor during runs, SSH session idle
(no `htop` running), Wi-Fi traffic minimal during runs.

## 6. Clocks and timestamps

Two clock domains exist and must never be subtracted directly:
- Linux: `CLOCK_MONOTONIC` (ns) on the Pi.
- STM32: a free-running hardware timer (us).

Proposed alignment: the Pi toggles the sync GPIO and records its
`CLOCK_MONOTONIC` time; the STM32 timestamps the edge with timer input
capture. Pairs of (Linux time, STM32 time) give offset and drift. Round-trip
echo over UART is the fallback (half-RTT bound, no extra wire).

## 7. Agent workflow (Claude conductor + Codex workers)

Roles:
- **Claude (conductor)** runs as a Remote Control session on the Mac, in the local clone
  of this repo. It splits work into bounded tickets, runs Codex on them, reviews diffs,
  runs tests, and is the only agent that talks to the Pi (over SSH) and to hardware.
- **Codex (workers)** run with `codex exec` on code-only tickets, each in its own git
  worktree and branch so parallel workers never touch the same checkout. Workers do
  not SSH to the Pi; the conductor deploys and runs experiments.

### Mac prerequisites (one time, no hardware)
1. Clone the repo to `~/Desktop/OS/OS-project/heterogeneous-edge-ai-os` (the path `AGENTS.md` names)
   and check out `claude/project-thread-eq9yql`.
2. Install the Codex CLI (`npm install -g @openai/codex`). Log in each account into its own
   home so they never overwrite each other:
   `CODEX_HOME=~/.codex-a codex login`, `CODEX_HOME=~/.codex-b codex login`, ...
3. STM32 toolchain: `brew install --cask gcc-arm-embedded` and `brew install open-ocd stlink`.
4. SSH key for the Pi: `ssh-keygen -t ed25519` if `~/.ssh/id_ed25519.pub` does not exist yet.
5. Start Remote Control from that folder (`claude remote-control`) so the conductor can work there.

### Pi headless setup (session P0). Bring: Pi 5, 27 W PSU, active cooler, microSD, microSD reader for the Mac.
1. Raspberry Pi Imager on the Mac: Ubuntu Server 24.04 LTS 64-bit. Settings: hostname `osedge`,
   user `os`, SSH with public-key only (paste `~/.ssh/id_ed25519.pub`), Wi-Fi of the place the Pi will live.
2. Boot the Pi. From the Mac: `ssh os@osedge.local` (or the IP from the router).
3. Add to the Mac's `~/.ssh/config`:
   ```
   Host osedge
     HostName osedge.local
     User os
   ```
   After that, `ssh osedge true` must succeed with no password. This is the check the conductor needs.
4. On the Pi: clone the repo, `sudo ./scripts/pi/bootstrap.sh`, reboot.
5. If the Mac and the Pi will not be on the same network, install Tailscale on both and use the
   Tailscale name as `HostName`.

## 8. Parked-rig wiring and self-recovery (setup day, 2026-10-06)

Wiring (both sides 3.3 V, no level shifter; Nucleo powered and flashed from a Pi USB port):

| Pi 5 header | Signal | Nucleo-F446RE |
|---|---|---|
| pin 8, GPIO14 (UART0 TX) | Pi to STM32 | PA10 = USART1 RX (Arduino D2) |
| pin 10, GPIO15 (UART0 RX) | STM32 to Pi | PA9 = USART1 TX (Arduino D8) |
| pin 6, GND | ground | GND |
| pin 11, GPIO17 | clock-sync edge | PA0 = TIM2_CH1 input capture (Arduino A0) |

Self-recovery so nobody has to walk over and power-cycle:
- Pi hardware watchdog via systemd (`RuntimeWatchdogSec=15s` in `/etc/systemd/system.conf`):
  a hung kernel reboots by itself.
- STM32 reset and reflash from the Pi through the ST-LINK (`openocd ... -c "reset run"`).
- Fault injection stays at process level (kill, SIGSTOP, FIFO CPU hog). No deliberate kernel
  freezes on the parked rig.
- Agents (Claude/Codex) are paused while a measurement runs, so they do not add load to the
  system under test.

NVMe boot on Pi 5 needs an M.2 HAT and a recent bootloader EEPROM. If NVMe boot is not
working within an hour, use a microSD; the project does not depend on disk speed.
