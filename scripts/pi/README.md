# Run on the Raspberry Pi 5

These scripts target Ubuntu 24.04 ARM64 on the course rig. Host tests can run on
macOS; Pi provisioning, scheduler settings, power monitoring and real UART access
run on the Pi. Read [hardware setup](../../docs/ENVIRONMENT_AND_HARDWARE.md) and
[UART bring-up](UART.md) before connecting the boards.

| Script | Purpose |
|---|---|
| `bootstrap.sh` | One-time Pi package installation, serial group access and UART boot configuration; run explicitly with sudo, then reboot |
| `collect_metadata.sh` | Record kernel, governor, affinity, power and environment metadata |
| `run_pipeline.sh` | Source → inference → bridge pipeline; PTY by default, real UART with `--serial`; `--help` lists options |
| `uart_tools.py` | Serial/GPIO helper used by the pipeline |
| `fault_inject.sh` | Explicit process kill/stop injections; see [UART.md](UART.md) |
| `run_experiment.sh` | Older generic tmux wrapper writing `experiments/runs/`; uses before/after sticky power gating. Prefer campaign runners for current validity rules |
| `conductor.service` | Optional service template; deployment details in [historical conductor state](../../docs/CONDUCTOR_STATE.md) |

Build and inspect on the Pi:

```sh
make -C linux all
bash scripts/pi/run_pipeline.sh --help
bash scripts/pi/collect_metadata.sh
```

For a new short real-UART run after the matching firmware is flashed:

```sh
bash scripts/pi/run_pipeline.sh --serial /dev/ttyAMA0 --baud 921600 --duration 60
```

The firmware uses USART1 PA9 TX / PA10 RX and shared ground, with 3.3 V signaling.
Confirm the Pi device and wiring against the [firmware README](../../stm32/firmware/README.md).
Default output paths and process-local scheduler/affinity options are documented
in [linux/README.md](../../linux/README.md). For matched measurements use
[tools/experiments](../../tools/experiments/README.md),
[tools/timing](../../tools/timing/README.md) and
[tools/la](../../tools/la/README.md); they document run windows, applied-setting
checks, power exclusions and capture requirements. Preserve raw failed runs;
write new captures to new directories. The submitted evidence inventory is
[results/README.md](../../results/README.md).
