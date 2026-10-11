# UART bring-up and E4 (UNVERIFIED ON HARDWARE)

COMMAND: `bash scripts/pi/run_pipeline.sh --serial /dev/ttyAMA0 --baud 921600 --duration 60 --bridge-cpu 2 --sync-gpio 17`

PURPOSE: run source/inference/bridge with a real full-duplex UART. This mode starts neither socat nor hea_rx. Omit `--serial` to keep the software PTY mode. Match baud to the flashed firmware; confirm the UART device, 3.3 V wiring/shared ground and firmware pinout before running. N in `--sync-gpio N` is a GPIO chip line offset, not a header pin. Select the correct chip with `HEA_GPIO_CHIP=gpiochipN`; confirm it with existing libgpiod tools. No pinout is changed by this implementation.

EXPECTED: bridge.csv records sends; mcu_status.csv records base and optional v3 diagnostics (blank fields indicate absent diagnostics); echo.csv records Pi RAW T1/T4 in ns, raw MCU T2/T3 in us and extended MCU times. `--echo-ms N` defaults to 1000; zero disables it. Estimator accepts only replies matching the latest outstanding request. Parser rejects corrupt frames and recovers. The 60-s/60-sample window logs minimum-delay offset/reference/delay and least-squares drift/RMS; drift is blank until two distinct sample times exist. Offset means MCU minus Pi. Minimum-delay offset and fit drift are separate estimates. Additional mapping columns use the full fitted offset/drift at reference_pi_us when available, or minimum-delay offset with zero drift for one sample; they express T1/T4 in MCU us and T2/T3 in Pi us. These are estimated times, subject to delay asymmetry and fit residuals. No cross-domain AoI is calculated. Timer gaps >= 2^31 us and MCU restarts require restarting the bridge. T1 is first write acceptance, T4 is completed userspace frame decode, so serialization and scheduling affect estimates.

DECISION: preserve one bridge poll loop and shared framing/sequence stream to measure OS scheduling and UART round-trip effects. Real-UART summary reports status/echo counts and Pi-local dispatch latency; MCU_STATUS lacks per-inference reception identity, so transit/AoI is unavailable.

GPIO uses installed gpioset (v1 or v2 syntax) and holds each requested value until the next second. gpio.csv logs RAW time immediately before gpioset launch and after its startup check, **not an electrically timestamped edge**. Line release/reacquisition can glitch depending on controller bias; only pair verified intended edges with TIM2 captures, and inspect capture_count/capture_lost. Verify on a scope and characterize command-to-edge uncertainty before using it for accuracy claims. SIGTERM cleans up the active gpioset. If gpioset is absent, the script fails clearly: omit --sync-gpio and use an external calibrated edge source or install the target's libgpiod CLI separately; no package installation or dependency is added here.

COMMAND: `bash scripts/pi/fault_inject.sh kill PID 1 2 faults.csv`

PURPOSE: SIGKILL the bridge (PID is saved as bridge.pid in the run directory).

EXPECTED: UART heartbeats stop; MCU transitions according to its watchdog policy. Runner detects dead bridge and ends the run, so use a separately launched bridge for longer post-fault observations.

DECISION: compare the RAW fault command onset to MCU state transitions only through a validated clock mapping; onset is logged immediately before kill, not an acknowledgement from the scheduler.

COMMAND: `bash scripts/pi/fault_inject.sh stop PID 500 2 faults.csv`

PURPOSE: SIGSTOP bridge for 500 ms then SIGCONT (also resumes on ordinary termination of the injector).

EXPECTED: missed heartbeats/stale state during the pause; subsequent behavior follows firmware rearm policy. Kill -9 of the injector cannot execute cleanup.

DECISION: isolate process scheduling stalls from inference overload.

COMMAND: `sudo bash scripts/pi/fault_inject.sh hog PID 500 2 faults.csv`

PURPOSE: run a bounded priority-99 SCHED_FIFO busy loop on bridge core 2. Pin bridge to that core; choose a lower bridge priority. Duration is limited to 60000 ms; kernel RT throttling remains in effect.

EXPECTED: bridge dispatch stalls subject to RT throttling. Non-root use fails with a sudo message; invalid affinity or failed scheduler setup fails clearly. Onset is recorded inside the hog after affinity and scheduling are applied.

DECISION: measure fixed-priority contention without changing kernel configuration. UART, GPIO/TIM2 pairing and all E4 effects remain UNVERIFIED ON HARDWARE.
