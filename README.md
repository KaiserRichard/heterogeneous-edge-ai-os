# heterogeneous-edge-ai-os

Operating Systems course project exploring a heterogeneous Embedded Linux-FreeRTOS Edge-AI system on Raspberry Pi 5 and STM32F446RE, focusing on scheduling, resource contention, timing, communication, and real-time supervision.

## Documentation
- [`PROJECT.md`](file:///Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/PROJECT.md): Detailed technical specification, architecture, experiment directions, and non-goals.
- [`docs/ENVIRONMENT_AND_HARDWARE.md`](docs/ENVIRONMENT_AND_HARDWARE.md): Which hardware each work session needs, Pi provisioning, unattended experiment runs.
- [`docs/WBR_INTEGRATION.md`](docs/WBR_INTEGRATION.md): Where this project sits in the WBR robot and the port path to the STM32H7.
- [`docs/ROADMAP.md`](docs/ROADMAP.md): Day-by-day plan with hardware per day.
- [`protocol/PROTOCOL.md`](protocol/PROTOCOL.md): Proposed UART frame format and messages.
- [`AGENTS.md`](file:///Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/AGENTS.md): Operational boundaries and developer guidelines for AI coding agents.

## Repository Layout
- `linux/`: Linux-side user-space workloads (Edge-AI inference, contention generators, UART bridge daemon).
- `stm32/`: STM32F446RE FreeRTOS firmware (UART handling, real-time supervisor, watchdog, failsafe).
- `protocol/`: Shared packet structure, framing definitions, and serialization/integrity verification logic.
- `experiments/`: Experiment orchestrators, latency/freshness loggers, and analysis scripts.
- `scripts/`: Tooling for building, flashing, and device configuration.
- `third_party/`: Git submodules of reference implementations (read-only references).
