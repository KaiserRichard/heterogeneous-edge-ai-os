# System Guide: understand the system and what we build

For the team. Read this first; it assumes no prior OS course. Terms in **bold** are
explained in the glossary at the end. Version 2026-10-06 (after the research pass).

---

## Part 1. The system in one page

**Setup.** A Raspberry Pi 5 runs Linux and an AI model. Every 100 ms it takes an input,
runs the model (20–50 ms), and sends the result over a serial cable (**UART**) to an
STM32 microcontroller running **FreeRTOS**. The STM32 stands for the part of a robot that
moves things (a motor). It must act only on *recent* results.

**Two problems.**
1. *Late data.* When other programs load the Pi, Linux shares the CPU between everyone, so
   our program waits its turn. Results arrive late, and nobody can tell they are old.
2. *Silent failure.* If our program crashes or Linux freezes, the STM32 keeps using the last
   result forever. A checker program on the Pi does not help: it freezes too.

**Two fixes.**
1. *On Linux:* use Linux's own features (no kernel changes) to give the small program that
   sends results priority over heavy work, and send only the newest result.
2. *On the STM32:* an independent supervisor with a stopwatch. If data or heartbeats stop
   arriving on time, it switches to a safe state by itself.

**Then we measure** how much each fix helps. Measuring is the main deliverable.

This design pattern has a name in research: **Simplex** (a complex, untrusted part watched
by a simple, trusted part on separate hardware).

---

## Part 2a. The life of one result (follow this and you understand the system)

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

In parallel, all the time:
- **Heartbeat:** the bridge sends HEARTBEAT every 20 ms (ASSUMED), even when no new result exists.
- **Clock sync:** the bridge sends ECHO_REQ; the STM32 answers with its receive and send
  times, so the Pi can map the two clocks (section 6).
- **Stressors:** `stress-ng` loads CPUs 2-3 with CPU, memory-bandwidth or cache pressure.

**Age of Information (AoI)** at any moment = now minus `t_input` of the newest result the
STM32 holds. This is the number that tells us "how old is the world view the MCU uses".

---

## Part 2. The parts, one by one

### 2.1 On the Pi (Linux)

```
 [source] --> [inference] --Unix socket--> [bridge] --UART--> STM32
                                    ^
                  [stressors] compete for CPU and memory
```

| Part | What it does | OS idea it shows |
|---|---|---|
| **source** | Makes a fake "camera frame" every 100 ms and stamps the time it was made. | Periodic task, timestamps |
| **inference** | Runs MobileNetV2 (an image classifier) on each frame with ONNX Runtime. | CPU-heavy, memory-heavy process |
| **bridge** | Small, fast program. Gets results through a **Unix domain socket**, packs them into frames, sends them over UART. Also sends a **heartbeat** every 20 ms and answers clock-sync messages. | **IPC**, device I/O, real-time priority |
| **stressors** | `stress-ng` processes that deliberately overload CPU, memory, cache or disk. | **Resource contention** |
| **runner** | Script that starts an experiment, records the system state (temperature, CPU speed, throttling) and saves results. | Reproducible measurement |

### 2.2 The four runtime profiles

The same programs run under four configurations. Each step changes exactly one thing.

| Profile | What changes | Question it answers |
|---|---|---|
| **P0 stock** | Nothing. Linux defaults. | Baseline |
| **P1 tuned** | Bridge gets **SCHED_FIFO** priority 50, programs are pinned to their own cores (**CPU affinity**), heavy work is capped with **cgroups**, bridge memory is locked (**mlockall**). | How much do Linux's own tools help? |
| **P2 = P1 + latest value** | The bridge keeps only the newest result; an older unsent one is thrown away. | Does dropping old data keep things fresher? |
| **P3 = P1 on RT kernel** | Same as P1, but booted on Ubuntu's ready-made real-time kernel (**PREEMPT_RT**). | How much does a real-time kernel add? |

### 2.3 The link (UART protocol)

Every message is a small **frame**: start bytes `A5 5A`, version, type, sequence number,
length, data, and a **CRC** checksum. The receiver reads byte by byte, finds the start bytes,
and throws away anything whose checksum is wrong. Message types:

- **HEARTBEAT** (Pi → STM32): "I'm alive."
- **INFERENCE** (Pi → STM32): the result plus the time its input was made.
- **ECHO_REQ / ECHO_RESP**: used to line up the two clocks (2.5).
- **MCU_STATUS** (STM32 → Pi): the supervisor's current state.

Already written and tested: every single-bit error is caught, and the parser recovers from
random noise.

### 2.4 On the STM32 (FreeRTOS)

FreeRTOS runs several **tasks**; the one with the highest **priority** that is ready always runs.

| Task | Priority | Job |
|---|---|---|
| UART receive | High | An **interrupt** collects bytes; the task parses frames. |
| Supervisor | Highest, every 1 ms | Keeps two stopwatches: time since last heartbeat, and age of the newest result. |
| Status | Low, every 100 ms | Reports the state back to the Pi. |
| Failsafe output | n/a | An LED and a pin a logic analyzer can watch. |

**Supervisor states:**

```
INIT --valid data--> FRESH --data stale--> HOLD --timeout--> FAILSAFE
                       ^                     |                  |
                       +----fresh data-------+                  |
          FRESH --heartbeat lost--> FAILSAFE --explicit rearm--> INIT
```

- *Why two stopwatches?* The bridge can be alive (heartbeats arrive) while the AI is stuck
  (results stop). Only the second stopwatch catches that.
- *Why latched FAILSAFE?* Once unsafe, stay safe until someone deliberately re-arms. No flapping.
- Duplicate or corrupted messages never reset a stopwatch.

### 2.5 Two clocks

The Pi counts time in nanoseconds; the STM32 has its own timer. They are separate **clock
domains**: you cannot subtract one from the other directly. We line them up like internet
time sync (NTP): the Pi sends a message at T1, the STM32 notes arrival T2 and reply T3, the Pi
notes arrival T4. From these four times we get the offset between clocks and the link delay.
A GPIO wire with a pulse gives a second, independent check.

### 2.6 What we measure

| Exp | Question | Main numbers |
|---|---|---|
| E1 | How much do stressors slow the data path? | **P50/P95/P99** latency for each stressor type |
| E2 | How much do tuning (P1) and the RT kernel (P3) recover? | Same, plus **jitter** |
| E3 | Does "latest value" (P2) keep data fresher? | **Age of Information**: average age, peak age, % of time too old |
| E4 | How fast does the STM32 react when Linux fails? | Fault time → decision time → safe output time |

Predictions: contention hurts the slow tail (P99) most; tuning fixes CPU contention but not
memory contention; latest-value lowers average age; the STM32 always reacts within its budget.

---

## Part 3. What has to be built

Status: ✓ done, ◐ partly, ○ not started. Hardware column says what must be connected.

| # | Work item | Status | Hardware |
|---|---|---|---|
| 1 | Design, research notes R1–R8, design changes | ✓ | None |
| 2 | UART protocol library + tests | ✓ | None |
| 3 | Portable supervisor v2, Step 1 (`feat/supervisor-v2`; `stm32/README.md`) | ◐ two receipt timers, sequence checks, latched FAILSAFE + explicit rearm implemented; hardware and source AoI pending | None |
| 4 | Merge skeleton; drop its duplicate `protocol.c` in favour of `hea_proto`; fix the Linux build bug (`%llu`) | ○ | None |
| 5 | CI: host tests + STM32 compile | ✓ | None |
| 6 | Pi provisioning and experiment runner scripts | ◐ written, never run | Pi |
| 7 | Inference program (MobileNetV2, ONNX Runtime) | ○ | None to write, Pi to run |
| 8 | Source + bridge (Unix socket, UART, heartbeat, clock sync, latest-value option) | ○ | None to write, Pi to run |
| 9 | Profile switcher P0–P2 (priorities, pinning, cgroups, mlockall) | ○ | Pi |
| 10 | RT kernel install for P3 | ○ | Pi |
| 11 | FreeRTOS firmware: UART RX, supervisor task, status task, failsafe pin, timer capture | ○ | None to write, Nucleo to run |
| 12 | Link bring-up: Pi ↔ STM32 over UART, clock sync check | ○ | Pi + Nucleo + jumpers |
| 13 | Experiments E1–E4 | ○ | Pi + Nucleo (+ logic analyzer for E4) |
| 14 | Analysis scripts and plots | ○ | None |
| 15 | Report and slides | ◐ outline done | None |

Order: 4 → 3 → 7, 8, 11 in parallel (Codex) → 6, 9, 10 on the Pi → 12 → 13 → 14 → 15.

The same work as an ordered plan with a "done when" check per step:

### Implementation plan, in order

Each step has a "done when" check. Do them in this order; later steps depend on earlier ones.

### Stage 1: software only (Mac, no hardware)

**Implementation scope correction (2026-10-08).** Step 1 uses MCU-local receipt
silence, not source AoI. FRESH currently means recently received heartbeat and
advancing result. Step 2 adds source-age accounting after a separately approved
payload/clock contract; there is no clock-mapping prerequisite for Step 1.
The diagrams above describe the eventual design. The other skeleton modules
remain unmerged; Step 1 adapts only the supervisor and reuses `hea_proto`.
See `stm32/README.md` for the exact state/sequence/rearm acceptance matrix.

| # | Work | Done when |
|---|---|---|
| 1 | Merge the skeleton into the main branch; one protocol library; one byte order | CI green; one `protocol/` |
| 2 | Supervisor v2, Step 1: heartbeat + result receipt silence, sequence check, latched FAILSAFE + local rearm, pure C with caller-supplied MCU time | `make -C stm32 test`: heartbeat lost, results silent but heartbeat alive, duplicates, real-parser CRC errors, latch and rearm; source AoI is Step 2 |
| 3 | Clock-sync math: offset/delay from T1-T4, drift fit, min-delay filter | host test with synthetic clocks (known offset + drift) recovers them |
| 4 | Linux bridge: Unix socket in, latest-value or FIFO (config), UART out, heartbeat, echo, MCU_STATUS in | runs against a pseudo-terminal pair (`socat`/`openpty`) with a fake MCU script |
| 5 | Linux source + workload (ORT MobileNetV2; synthetic fallback) + CSV logger | runs on the Mac or the Pi; CSV has `t_input`, `t_done`, `t_sent` per frame |
| 6 | FreeRTOS project for F446RE: ISR + stream buffer, RX task, supervisor, status task, GPIO/LED output | compiles in CI with `arm-none-eabi-gcc` |

### Stage 2: hardware bring-up
| # | Work | Done when |
|---|---|---|
| 7 | Pi bootstrap; `cyclictest` on the stock kernel; inference latency baseline (sets the source period and the HOLD/FAILSAFE thresholds) | numbers recorded with metadata and validity = OK |
| 8 | Flash the Nucleo; talk over the ST-LINK virtual COM port first; heartbeat loss drives the LED to FAILSAFE | LED reacts when the sender is stopped |
| 9 | Direct Pi-STM32 UART (GPIO14/15 to PA10/PA9, shared GND); measure CRC errors at the chosen baud | zero or counted errors over a long run |
| 10 | Clock sync on real hardware + GPIO-edge validation | offset error distribution measured |
| 11 | End-to-end AoI chain; logic-analyzer cross-check if available | AoI from logs matches the analyzer within the sync error |

### Stage 3: experiments and analysis
| # | Work | Done when |
|---|---|---|
| 12 | E1 contention: P0, idle vs each stressor (`--stream`, `--cache` 256K-8M, `--memrate`) | P50/P95/P99 per condition, repeated runs |
| 13 | E2 tuning: P0 vs P1, P1 vs P3 | same metrics + bridge dispatch jitter |
| 14 | E3 freshness: P1 vs P2 at rising load | time-average AoI, peak AoI, V(τ), deadline-miss fraction |
| 15 | E4 faults: kill bridge, SIGSTOP, FIFO CPU hog; t_f, t_d, t_s on one analyzer clock | per-fault distribution of detection and reaction time |
| 16 | Analysis: CDFs, tables, throttled runs excluded; report + slides + demo | |

### Who does what (suggestion for two people)

- **Person A, Linux side:** steps 4, 5, 7, 12-14 (bridge, workload, profiles, contention experiments).
- **Person B, MCU side:** steps 2, 3, 6, 8-11, 15 (supervisor, clock sync, firmware, bring-up, fault experiments).
- Together: step 1 (merge) and step 16 (analysis, report).
The protocol is the contract between the two; change it only together.


---

## Glossary

- **Scheduler**: the part of the OS that decides which program runs on which CPU core, and when.
- **SCHED_OTHER**: Linux's default, "fair share" scheduling. Everyone gets a turn.
- **SCHED_FIFO**: a real-time scheduling class. A FIFO task runs before any normal task, as long as it wants. Priority 1–99.
- **RT throttling**: Linux safety limit: real-time tasks may use at most 95% of each second, so a runaway task cannot freeze the system.
- **CPU affinity / pinning**: telling Linux which cores a program may run on.
- **cgroups**: Linux feature to cap how much CPU (or memory) a group of programs may use.
- **mlockall / page fault**: memory can be moved to disk and back; touching moved memory causes a *page fault*, a pause of milliseconds. `mlockall` forbids moving our program's memory.
- **PREEMPT_RT**: a Linux kernel variant where almost all kernel code can be interrupted, so high-priority tasks wait less. Ubuntu ships it ready-made.
- **IPC (inter-process communication)**: ways for programs to talk. **Unix domain socket**: a fast local "network connection" between two programs on the same machine.
- **RTOS (real-time OS)**: an OS built for predictable timing. **FreeRTOS** is a small RTOS for microcontrollers.
- **Task / priority**: in FreeRTOS, a task is like a thread; the ready task with the highest priority always runs.
- **Interrupt (ISR)**: hardware stops the CPU briefly to run a small handler, e.g. when a UART byte arrives.
- **Heartbeat / watchdog**: periodic "I'm alive" message / a timer that triggers if the heartbeat stops.
- **Failsafe**: the safe state a system enters when something goes wrong.
- **UART**: simple serial link, one wire each way plus ground. **Frame**: one message on that link. **CRC**: checksum that detects corrupted bytes.
- **Resource contention**: programs slowing each other down by competing for shared CPU, cache or memory bandwidth.
- **Cache (L2/L3)**: small fast memory near the CPU. Pi 5: 512 KB per core (L2), 2 MB shared by all cores (L3).
- **Latency / jitter**: delay / how much that delay varies.
- **P50 / P95 / P99**: the delay that 50% / 95% / 99% of samples stay under. P99 shows the rare bad cases.
- **Age of Information (AoI)**: at any moment, how old the newest data at the receiver is.
- **Clock domain**: a set of timestamps from one clock. Timestamps from different domains need conversion before comparison.
- **Simplex architecture**: a complex part does the work; a simple, trusted part checks it and can override it.
