# Heterogeneous Edge-AI OS — course submission

A Raspberry Pi 5 running Ubuntu 24.04 executes an inference workload and sends
results and heartbeats over UART to an STM32F446RE running FreeRTOS. The external
supervisor distinguishes Linux liveness from result freshness and enters HOLD or
latched FAILSAFE when its configured limits are exceeded. The course contribution
is the study of scheduling, resource contention, IPC, data age and independent
supervision; inference supplies the workload. Start with the
[stage report](docs/STAGE_REPORT.md) for measured findings and validity limits,
and [PROJECT.md](PROJECT.md) for objectives and scope.

The Pi → STM32 diagram from [SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md#part-2a-the-life-of-one-result-follow-this-and-you-understand-the-system):

```
 Pi 5 (Linux)                                                STM32 (FreeRTOS)
 ------------                                                ----------------
 [1] source: makes frame #k, stamps t_input  (CLOCK_MONOTONIC_RAW)
        |
 [2] workload: MobileNetV2 inference, ~20-50 ms (SOURCE, other setups)
        |   stamps t_done
        |  Unix domain socket
 [3] bridge: stores result in a 1-slot "latest value" buffer
        |    (a newer result overwrites an unsent older one)
        |    frames it: SOF | ver | type | seq | len | payload | CRC
        v
     UART, 3.3 V direct wire, ~0.34 ms per frame at 921600 baud (CALCULATED)
        |
        +-------------------------------------------------> [4] UART ISR puts bytes in a
                                                                 stream buffer
                                                            [5] RX task parses the frame,
                                                                 checks CRC + sequence number
                                                            [6] supervisor task (1 kHz):
                                                                 updates the timers, decides
                                                                 FRESH / HOLD / FAILSAFE
                                                            [7] output: GPIO + LED show the state
                                                            [8] status task (10 Hz) sends
        <-------------------------------------------------      MCU_STATUS back to the Pi
 [9] bridge logs MCU_STATUS; the logger writes CSV
```

This guide diagram describes the earlier IRQ/stream-buffer design. The submitted
firmware defaults to circular DMA RX; protocol v3 INFERENCE line time is about
0.380 ms at 921600 baud. Diagram workload times are illustrative, not the final
measurements. See [firmware details](stm32/firmware/README.md) and the report.

## Repository map

| Path | Purpose |
|---|---|
| [docs/](docs/README.md) | Reading index, stage report, system guides and historical planning |
| [protocol/](protocol/PROTOCOL.md) | Shared framing, integrity, clock estimation and host tests |
| [linux/](linux/README.md) | Source, inference, bridge and receiver processes; Unix datagram IPC |
| [linux/inference/](linux/inference/README.md) | Synthetic/ONNX workloads and offline dependency preparation |
| [stm32/](stm32/README.md) | Portable supervisor tests and FreeRTOS [board firmware](stm32/firmware/README.md) |
| [analysis/](analysis/) | Result summaries and Python tests |
| [scripts/](scripts/) | Pi setup/running and STM32 flashing/resetting |
| [tools/experiments/](tools/experiments/README.md), [tools/timing/](tools/timing/README.md), [tools/la/](tools/la/README.md) | Campaign runners, timer diagnostics and independent captures |
| [results/](results/README.md) | Dated retained evidence, run counts and exclusions |
| `third_party/` | Pinned read-only architectural references; firmware reads FreeRTOS/CMSIS/linker inputs from one submodule |
| `prompts/`, `slides/` | Supporting course material, outside this cleanup |

## Build and test on a Mac or Linux host

Install a C compiler (Clang/Xcode Command Line Tools on macOS or GCC on Linux),
GNU make and Python 3. Host C tests use AddressSanitizer/UndefinedBehaviorSanitizer;
PTY tests do not require the rig. NumPy is optional locally (three numerical
checks skip without it); CI installs it. ONNX Runtime and a model are unnecessary
for host tests, which use synthetic workloads and fake runtime APIs.

```sh
make test
make firmware
make clean
```

`make test` builds Linux programs and runs all protocol, STM32 portable, Linux C,
Linux summary, analysis, logic-analyzer and inference Python suites. `make clean`
removes generated build outputs and source-tree bytecode caches, preserving results.

Firmware cross-compilation additionally needs `arm-none-eabi-gcc`, binutils and
newlib on PATH and the pinned firmware reference:

```sh
git submodule update --init -- third_party/nucleo-f446re-freertos
make firmware
# Optional alternate toolchain/reference locations:
make firmware CROSS_COMPILE=/path/to/arm-none-eabi- FREERTOS_REF=/path/to/reference
```

Outputs are `stm32/firmware/build/firmware.elf` and `firmware.bin`. Build-profile
options are in the [firmware README](stm32/firmware/README.md). Cross-compilation
checks the image; physical timing and electrical behavior require the rig.

## Run on the rig

Use the [Pi scripts README](scripts/pi/README.md) for bootstrap, metadata and the
pipeline, then the [experiment README](tools/experiments/README.md) for software
E1–E3 and physical E3/E4. [Timing tools](tools/timing/README.md) cover cyclictest;
[logic-analyzer tools](tools/la/README.md) cover FX2 acquisition and comparison.
The Pi runs the Linux binaries; the Mac can cross-compile, flash/reset via
`scripts/stm32/`, and acquire analyzer traces. Wiring, 3.3 V signaling, shared
ground, USART1 pins, HSE/ST-LINK clock requirements and firmware profiles are
in the [firmware README](stm32/firmware/README.md) and
[UART guide](scripts/pi/UART.md). Use a new output directory for each run and
retain failed captures and validity records.

## Four main findings

1. FIFO improves wake-up tails, but memory contention still raises latency;
   the median gap also includes timer slack. [Timer measurements](docs/STAGE_REPORT.md#timer-wake-up-diagnostic).
2. More inference threads do not consistently improve latency under contention;
   four-thread runs include power exclusions. [Inference baseline](docs/STAGE_REPORT.md#inference-workload-alone).
3. Bridge latest-value replacement cannot remove age accumulated before inference.
   Input latest-value supports the expected improvement in flagged reruns.
   [Freshness evidence](docs/STAGE_REPORT.md#freshness-the-queue-was-in-the-wrong-place).
4. MCU supervision distinguishes lost heartbeat from stale results while heartbeat
   remains alive; reason-based local timing uses different reference events.
   [Physical fault results](docs/STAGE_REPORT.md#physical-faults-state-timing-not-output-timing).

## Known limitations

The 5 V / 3 A PSU produced under-voltage/throttle flags; excluded observations are
retained and labelled. Most comparison cells have only three repetitions, below
the planned five-valid-repeat gate. E1–E3 use PTY transport and establish software
behavior; all 18 real-UART E3 runs are flagged. E4/F5 and extra F4 have differing
exposure/recovery scopes. Observed maxima are not worst-case bounds, clock mapping
is an estimate, and this demo has no physical actuator or independent hardware
watchdog. Retained analyzer captures have separate qualification limits; they do
not automatically validate older reported output-timing claims. See
[report limitations](docs/STAGE_REPORT.md#limits-and-transfer-to-wbr) and the
[result inventory](results/README.md).
