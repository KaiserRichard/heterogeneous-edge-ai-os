# Coding Agent Guidelines & Rules

All AI coding agents working on this repository must strictly adhere to the following rules:

## 1. Workspace Boundary
- Treat `/Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os` (or `~/Desktop/OS/OS-project/heterogeneous-edge-ai-os`) as the **only** intended workspace.
- Do not inspect, access, modify, or leak files from unrelated directories, other university coursework, or personal directories on the host machine.

## 2. Read PROJECT.md First
- Always read and respect [`PROJECT.md`](file:///Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/PROJECT.md) before designing, modifying, or proposing code or architecture.
- All implementations must serve the educational OS objectives described in `PROJECT.md`.

## 3. Strict Scope & Technology Bounds
- **Never** introduce technologies explicitly listed as non-goals:
  - No ROS 2 or micro-ROS.
  - No Docker / Podman / containers.
  - No Yocto or Buildroot.
  - No PREEMPT_RT or kernel patching.
  - No hypervisors or virtualization layers.
  - No SPI, CAN, or Ethernet (the bridge is strictly UART).
  - No TinyML or neural inference on the STM32.
  - No bloated enterprise frameworks or unnecessary dependencies.
- Keep the codebase lightweight, modular, and focused on core OS mechanisms.

## 4. Respect Reference Code (`third_party/`)
- Code inside `third_party/` consists of Git submodules added purely for architectural reference and study.
- **Do not modify**, commit changes to, or reorganize files within `third_party/` unless explicitly instructed by the user.
- Do not blindly copy-paste reference code; adapt relevant design concepts cleanly into `linux/`, `stm32/`, or `protocol/`.

## 5. Distinguish Execution Environments
Be mindful of the three distinct environments when proposing code, commands, or build steps:
1. **Host Workstation (macOS)**:
   - Primary development machine for Git, documentation, and cross-compilation (e.g., `arm-none-eabi-gcc`).
   - Do not execute Linux-specific binaries or assume Linux system headers (`sys/epoll.h`, `sched.h`, `/dev/tty*`) run directly on macOS.
2. **Linux Target (Raspberry Pi 5 - Ubuntu 24.04 ARM64)**:
   - Target for Linux C/C++ applications, Python orchestrators, `stress-ng`, and UART serial interfaces (device node and topology TBD).
3. **Real-Time Target (STM32F446RE Nucleo)**:
   - Bare-metal / FreeRTOS embedded C firmware.
   - Resource-constrained (128 KB RAM, 512 KB Flash); no dynamic heap thrashing or heavy runtime libraries.

## 6. Preserve Reproducibility & Modularity
- Every experiment, build script, and test must be straightforward to run and replicate.
- Maintain clear build instructions, reproducible compiler flags, and documented configuration parameters.
- Provide clean scripts under `scripts/` for building, flashing, and running benchmarks.

## 7. Explain Architecture-Changing Edits
- Any proposal that alters data framing, task priority schemes, threading models, or hardware pinouts must be explicitly justified with respect to OS learning goals before implementation.

## 8. Validate Before Claiming Success
- Do not claim an implementation works without running appropriate linting, syntax checking, compilation, or simulation where possible.
- Clearly differentiate between code verified locally vs. code that requires physical verification on hardware (Raspberry Pi 5 or STM32F446RE).
