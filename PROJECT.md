# Heterogeneous Edge-AI Operating System Project

## 1. Project Objective
This is a two-person Operating Systems course project demonstrating fundamental operating system principles on a real heterogeneous computing platform:
- An **application-grade general-purpose OS (Ubuntu Server 24.04 LTS on Raspberry Pi 5)** handling dynamic computation and I/O.
- A **deterministic real-time OS (FreeRTOS on STM32F446RE)** acting as an external supervisor and safety-critical controller.
- A dedicated **UART physical link** bridging the two domains with a lightweight framed communication protocol.

The core goal is to empirically observe and analyze OS concepts—CPU scheduling, resource contention, inter-domain (Linux-MCU) communication latency, data freshness (Age of Information), and watchdog supervision—rather than building a machine learning system. (Priority inversion may be studied later if shared-resource synchronization makes it relevant.)

---

## 2. Hardware Architecture
- **Host / Application Processor**: Raspberry Pi 5 (Broadcom BCM2712 quad-core Cortex-A76 @ 2.4 GHz, 4 GB LPDDR4X RAM).
- **Microcontroller / Real-Time Supervisor**: STM32F446RE Nucleo-64 (ARM Cortex-M4 with FPU @ 180 MHz, 512 KB Flash, 128 KB SRAM).
- **Interconnect**: Dedicated full-duplex UART physical link bridging Raspberry Pi 5 and STM32F446RE.

### Hardware Decisions (OPEN / TBD)
- **Raspberry Pi UART Device Node**: TBD (e.g., PL011 `/dev/ttyAMA*` on 40-pin GPIO header vs. USB serial device node `/dev/ttyUSB*`).
- **Raspberry Pi GPIO Pinout**: TBD (dependent on selected UART controller and any external signaling pins).
- **STM32 USART Instance**: TBD (e.g., USART1, USART2, USART3, or UART4/5; dependent on board routing and ST-LINK VCP considerations).
- **STM32 Pin Mapping**: TBD (TX/RX pins, failsafe/status indicators, and oscilloscope probe points).
- **UART Baud Rate**: TBD (e.g., standard 115200 baud vs. high-speed 921600+ baud; trade-off between transfer latency and line noise margin).
- **USB-to-UART Topology**: TBD (Direct 3.3V GPIO-to-GPIO jumper link with shared ground vs. USB-to-UART adapter vs. ST-LINK Virtual COM Port).

---

## 3. Linux & FreeRTOS Architecture

```
+-------------------------------------------------------------+
|               Raspberry Pi 5 (Ubuntu 24.04 ARM64)           |
|                                                             |
|  +---------------------+  Linux |     UART Bridge /      |  |
|  |  Edge-AI Workload   |   IPC  |    Telemetry Daemon    |  |
|  | (Inference Workload)| -----> |                        |  |
|  +---------------------+  (TBD) +------------------------+  |
|             ^                               |               |
|             | Resource                      v               |
|  +---------------------+        +------------------------+  |
|  | Contention Workload |        | Linux Kernel / TTY     |  |
|  | (stress-ng / fork)  |        | (Device Node TBD)      |  |
|  +---------------------+        +------------------------+  |
+---------------------------------------------|---------------+
                                              | Hardware UART
                                              | (Topology & Baud TBD)
                                              v
+-------------------------------------------------------------+
|               STM32F446RE Nucleo (FreeRTOS)                 |
|                                                             |
|  +--------------------+  RTOS IPC  +---------------------+  |
|  |  UART RX/TX Task   | ---------> | Real-Time Supervisor|  |
|  | (Driver TBD)       |   (TBD)    | (Deadline Monitor)  |  |
|  +--------------------+            +---------------------+  |
|                                              |              |
|                                              v              |
|                                    +---------------------+  |
|                                    | Watchdog & Failsafe |  |
|                                    | (Indicator/StateTBD)|  |
|                                    +---------------------+  |
+-------------------------------------------------------------+
```

### Linux Side (Raspberry Pi 5)
- Runs standard Ubuntu Server 24.04 LTS (stock ARM64 kernel).
- Executes an AI/inference workload (framework and model pipeline TBD; e.g., ONNX Runtime / TFLite or synthetic matrix computation).
- Manages an outbound telemetry stream to the STM32 containing inference timestamps, state classifications, and health heartbeats.
- Subjected to controlled synthetic stress tasks (CPU cycles, memory allocation, cache thrashing, I/O saturation).
- **Linux IPC Mechanism (OPEN / TBD)**: Communication between the AI workload and UART bridge daemon. Unix domain sockets are a likely option, but the IPC mechanism remains TBD until the Linux runtime architecture lesson/design phase.

### FreeRTOS Side (STM32F446RE)
- Runs a preemptive, priority-based FreeRTOS kernel.
- **Supervisor Task**: Periodically verifies reception of Linux heartbeats and validates packet timeliness.
- **Actuator / Telemetry Task**: Simulates deterministic control loops reacting to AI decisions (actuation output mechanism TBD).
- **Watchdog / Failsafe Handler**: Detects deadline overruns, missed heartbeats, or corrupted packets, immediately triggering safe fallback states.
- **Embedded Architecture Decisions (OPEN / TBD)**: UART RX/TX reception mechanics (interrupt-driven ring buffer vs. DMA) and intra-task communication (FreeRTOS queues, stream buffers, or direct task notifications) remain TBD until firmware design.

---

## 4. Role of AI: Workload, Not Contribution
- AI (e.g., lightweight computer vision or anomaly detection) is treated solely as a **realistic, compute- and memory-intensive Linux workload**.
- **No TinyML on STM32**: The microcontroller is strictly a real-time supervisor, not an AI accelerator.
- We do not innovate on neural network architectures or training algorithms. Instead, we study how variable inference latency and non-deterministic execution affect downstream real-time system guarantees.

---

## 5. Key Operating System Topics
1. **CPU Scheduling & Priorities**:
   - Evaluating Linux scheduling classes (`SCHED_OTHER` vs. real-time `SCHED_FIFO` / `SCHED_RR`).
   - Priority levels, nice values, CPU affinity pinning (`taskset`), and cgroup quota restrictions.
   - Contrasting with FreeRTOS fixed-priority preemptive scheduling and Rate-Monotonic scheduling.
2. **Resource Contention & Multi-tenancy**:
   - Impact of CPU saturation, memory bandwidth exhaustion, and cache thrashing on inference throughput and dispatch latency.
3. **Inter-Process & Inter-Node Communication**:
   - Linux IPC mechanisms (Unix domain sockets are a leading candidate; comparative evaluation with pipes and POSIX shared memory remains TBD for the Linux runtime architecture phase).
   - Serial UART framing, packet integrity validation (framing & CRC/checksum TBD), buffer management, and reception mechanics (interrupts vs. DMA TBD).
4. **Real-Time Deadlines, Freshness & Safety**:
   - Age of Information (AoI) metrics: measuring elapsed time from raw input ingestion to MCU actuator trigger.
   - Independent hardware/firmware watchdog timers and failsafe transitions under Linux kernel freeze or process crash.

---

## 6. Core Experiment Directions
1. **Baseline vs. Contention Profiling**: Measure AI inference latency, packet dispatch jitter, and end-to-end delay under zero load vs. aggressive multi-core stress (`stress-ng`).
2. **Scheduling Policy Comparison**: Compare Linux `SCHED_OTHER` vs. `SCHED_FIFO` for the AI and bridge tasks under high system load.
3. **Freshness & Deadline Miss Rate**: Quantify end-to-end Age of Information (AoI) and deadline violation frequencies across varying workload intensities.
4. **Fault Injection & Failsafe Latency**: Intentionally crash the Linux bridge process or stall the Linux kernel; benchmark the detection time and safe-state activation time on STM32.

---

## 7. Non-Goals
To keep the project grounded, robust, and aligned with course goals, the following are explicitly **out of scope**:
- ROS 2 or micro-ROS
- Containerization (Docker, Podman, Kubernetes)
- Embedded Linux build systems (Yocto, Buildroot)
- Custom Linux kernel drivers or kernel recompilation
- Patching or building our own kernel (the packaged Real-time Ubuntu 24.04 kernel is allowed as test profile P3; decision 2026-10-06)
- Hypervisors (Xen, KVM, Jailhouse)
- SPI / CAN / Ethernet interconnects (UART only)
- TinyML / model inference running on the STM32
- Heavy middleware frameworks or distributed pub/sub brokers

---

## 8. Development Environments
- **Workstation (macOS)**:
  - Code editing and version control.
  - Cross-compilation toolchain for STM32 (`arm-none-eabi-gcc`, `openocd`, `stlink`, serial terminals).
- **Edge Application Platform (Raspberry Pi 5)**:
  - Ubuntu Server 24.04 LTS (ARM64).
  - Native C / C++ / Python development.
  - OS diagnostic tools (`chrt`, `taskset`, `perf`, `htop`, `stress-ng`).
- **Real-Time Platform (STM32F446RE)**:
  - C99/C11 firmware with CMSIS and FreeRTOS.
  - Bare-metal HAL or LL drivers with minimal overhead.
