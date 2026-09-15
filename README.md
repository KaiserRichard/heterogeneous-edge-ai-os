# heterogeneous-edge-ai-os

Operating Systems course project exploring a heterogeneous Embedded Linux-FreeRTOS Edge-AI system on Raspberry Pi 5 and STM32F446RE, focusing on scheduling, resource contention, timing, communication, and real-time supervision.

## Documentation
- [`PROJECT.md`](file:///Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/PROJECT.md): Detailed technical specification, architecture, experiment directions, and non-goals.
- [`AGENTS.md`](file:///Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/AGENTS.md): Operational boundaries and developer guidelines for AI coding agents.

## Repository Layout
- `linux/`: Linux-side user-space workloads (Edge-AI inference, contention generators, UART bridge daemon).
- `stm32/`: STM32F446RE FreeRTOS firmware (UART handling, real-time supervisor, watchdog, failsafe).
- `protocol/`: Shared packet structure, framing definitions, and serialization/integrity verification logic.
- `experiments/`: Experiment orchestrators, latency/freshness loggers, and analysis scripts.
- `scripts/`: Tooling for building, flashing, and device configuration.
- `third_party/`: Git submodules of reference implementations (read-only references).
