# E4 independent hardware clock cross-check

**UNVERIFIED ON HARDWARE.** Only synthetic tests and local syntax checks have
been run. No Pi, ST-LINK, or analyzer commands were executed during implementation.
No new dependencies are installed. Python standard library suffices for analysis;
an existing matplotlib installation enables the optional timing PNG.

Wiring (3.3 V logic; shared ground): D0 PA5, D1 PB5, D2 PA10 UART RX from Pi
921600 8N1 idle high, D3 Pi GPIO27/header pin 13. State codes in D0/D1 order:
11 FRESH, 01 HOLD, 00 INIT/FAILSAFE. The analyzer requires FRESH before the
marker and selects subsequent HOLD/safe transitions, avoiding startup INIT.
A heartbeat outage may go directly to FAILSAFE: absent HOLD is left blank.

The optional GPIO marker uses the existing Linux GPIO character-device v1 ABI,
not a gpioset invocation for each edge. `gpioinfo` discovers the unique GPIO27
label and its actual chip/line offset. One requested output fd retains ownership.
Each ioctl logs CLOCK_MONOTONIC_RAW before and after and the bracket width in
`run.json`. This brackets software execution, **not a proven electrical edge
bound**: compare against the analyzer. The marker rises immediately before
SIGKILL/SIGSTOP or the F4 FIFO busy loop; it falls at resume, hog end, or F1
restore start. F4 owns the marker in its sudo helper, initialized before the
Mac release handshake. GPIO changes are instrumentation only: firmware framing,
priorities and UART pins remain as configured.

The single-fault entry point reaches FRESH and an echo clock fit, holds FRESH
for 2 s, publishes `FILE.ready`, then waits up to 90 s for `FILE`. The Mac
resets ST-LINK directly before each run, starts capture, then creates FILE.
Single mode observes 2 s after onset and does not run recovery/reset on the Pi.
It is distinct from the 20 s steady/10 s observation campaign, and must not be
fed to `analysis/e4_summary.py` as a full campaign. F1 retains passive capture
and existing bridge replay decoding. F4 remains subject to Linux RT throttling.

Capture uses fx2lafw at 24 MHz (41.67 ns samples), D3 rising trigger,
`capture_ratio=20`, and 3 s depth. A 30 s watchdog bounds missing triggers.
The 1 s launch delay is a readiness allowance, not evidence the USB acquisition
is armed. Confirm sufficient prehistory and actual marker presence; analyzer
validation rejects absent marker or non-FRESH pre-marker state. Save raw `.sr`
and sparse VCD rather than a huge sample CSV. Trigger support follows the
[fx2lafw source](https://github.com/sigrokproject/libsigrok/blob/master/src/hardware/fx2lafw/api.c).

From this worktree root, transfer the changed runner and existing code to the
Pi checkout using your normal deployment procedure first. Set the actual remote
repository and UART node, then run these **on the Mac**:

```bash
export LA_PI=richard@192.168.50.2
export LA_PI_REPO=/home/richard/heterogeneous-edge-ai-os
export LA_SERIAL=/dev/ttyAMA0
export SIGROK_CLI=/usr/local/bin/sigrok-cli
tools/la/la_e4.sh results/la-e4-F1-001 5 fault=F1
tools/la/la_e4.sh results/la-e4-F2-001 5 fault=F2
tools/la/la_e4.sh results/la-e4-F4-001 5 fault=F4
python3 tools/la/la_analyze.py results/la-e4-F1-001
```

Directories must be new. Pi requires existing build tools, gpiod 1.6.3
`gpioinfo`, vcgencmd, passwordless sudo, and the E4-compatible bridge decoder.
The script runs the Pi entry point with sudo for GPIO permissions and F4;
outputs are copied back by scp. `--rearm-command true` acknowledges the Mac's
completed reset. No Pi request file or remote ST-LINK reset is used. Mac cleanup
terminates local capture/SSH; if SSH disconnects the remote release wait is
bounded and the fault's own duration/observation remains bounded. Remote evidence
is retained under the Pi checkout's results directory.

Outputs: `la_e4.csv`, `la_e4.tex`, optional `la_timing.png` for the first capture.
All timestamps use analyzer seconds; latency/comparison fields use microseconds.
VCD channels must be named D0..D3. Synthetic CSV accepts `time,D0,D1,D2,D3`
with time in seconds. UART parsing recognizes start and stop bit centers at
921600 baud and estimates the complete stop-bit end; last activity separately
reports the final physical edge. This is not proof of CRC acceptance or packet
type. MCU metrics subtract `last_hb_mcu_us` from the corresponding STATE_EVENT;
deltas compare that with physical byte-end latency, so differing reference
packets can produce real differences. Missing events/byte/HOLD/safe stay blank;
reported STATE_EVENT loss disables comparison. GPIO update skew and analyzer
oscillator accuracy must be checked on hardware. A 24 MHz nominal sample clock
is independent of Pi/MCU clocks, not a calibrated frequency reference.

Local checks (no hardware):

```bash
python3 -m unittest discover -s tools/la/tests -v
python3 -m unittest discover -s analysis/tests -v
python3 -m py_compile tools/experiments/e4_campaign.py tools/la/la_analyze.py
bash -n tools/la/la_e4.sh
```
