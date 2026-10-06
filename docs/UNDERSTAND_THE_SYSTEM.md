# Understanding the system, and what we must build

A reader's guide for the team. It explains how the system works end to end and lists the
work still to be done, in order, with how to check each piece. Design source:
`docs/SYSTEM_OVERVIEW.md` and `docs/research/DESIGN_CHANGES.md` (2026-10-06).
Nothing is MEASURED yet. All numbers are design values (ASSUMED) or calculations (CALCULATED).

---

## 1. One sentence

A Raspberry Pi 5 (Linux) runs a neural network under deliberate load and streams its
results over UART to an STM32 (FreeRTOS). The STM32 independently judges whether those
results are fresh enough to trust and falls back to a safe state within a bounded time when
they are not. We measure how Linux tuning affects freshness, and how fast the failsafe reacts.

## 2. The two questions the project answers

1. **Freshness under load.** When Linux is busy, how old is the data the MCU acts on, and
   how much do stock Linux mechanisms (scheduler class, CPU pinning, cgroups, mlockall,
   "latest value only" buffering, RT kernel) improve it? (Experiments E1, E2, E3)
2. **Bounded failure detection.** If the Linux process crashes, stops or is starved, does
   the MCU reach a safe state within a known time, whatever Linux does? (Experiment E4)

The AI model is only a realistic heavy workload. The topic is OS behaviour: scheduling,
contention, IPC, deadlines, clocks and watchdogs.

## 3. The life of one result (follow this and you understand the system)

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

## 4. Where each part runs

| Part | Machine | Language | Notes |
|---|---|---|---|
| source, workload, bridge, logger | Pi 5, Ubuntu 24.04 | C (bridge, timing), C or Python (workload via ONNX Runtime) | CPU 0 = inference, CPU 1 = bridge, CPUs 2-3 = stressors |
| stressors | Pi 5 | `stress-ng` | started by the experiment runner |
| firmware | STM32F446RE | C, FreeRTOS | USART1 (PA9/PA10) to the Pi; USART2 stays the ST-LINK debug console |
| protocol library | both | C99 | same source compiled for Linux and Cortex-M4 |
| build, analysis, docs | Mac | | flashing can be done from the Pi (`openocd`/`st-flash`) on the parked rig |

## 5. The Linux side in detail

### 5.1 Processes
- **source**: periodic timer (`clock_nanosleep`, absolute time), 100 ms period (provisional,
  set after measuring inference time). Produces frame id + `t_input`. Starts the AoI clock.
- **workload**: ONNX Runtime CPU, MobileNetV2 FP32, batch 1, intra-op threads swept 1/2/4,
  inter-op 1. Synthetic matrix computation as fallback if ORT causes trouble.
- **bridge**: small, short, critical. Reads results from a Unix domain socket, keeps only the
  latest, writes frames to the UART, sends heartbeats and clock-sync requests, reads MCU_STATUS.

### 5.2 Runtime profiles (same binaries, different configuration)
| Profile | What changes |
|---|---|
| P0 stock | Linux defaults: `SCHED_OTHER`, no pinning, FIFO queue between workload and bridge |
| P1 tuned | bridge `SCHED_FIFO` priority 50 on CPU 1; inference pinned to CPU 0; stressors capped by cgroup v2 `cpu.max` and pinned to CPUs 2-3; `mlockall` + preallocated buffers; RT throttling stays at the default 95% |
| P2 | P1 + latest-value buffer instead of the FIFO queue |
| P3 | P1 on the packaged Real-time Ubuntu kernel (`pro enable realtime-kernel --variant=raspi`) |

Each comparison changes one thing: P0 vs P1 = tuning, P1 vs P2 = buffering, P1 vs P3 = kernel.

### 5.3 Why each mechanism (the OS concept behind it)
- `SCHED_FIFO`: a real-time class task preempts every `SCHED_OTHER` task. The fair scheduler
  (EEVDF in 6.x kernels) otherwise makes the bridge wait behind stressors.
- CPU affinity: removes migration and keeps the bridge's cache warm.
- cgroup `cpu.max`: limits how much CPU time bulk work can take per period.
- `mlockall`: no page faults (which can stall for milliseconds) in the critical path.
- Latest-value buffer: under overload, a FIFO queue grows and every delivered result gets
  older. Dropping old data keeps the delivered data young.
- What these cannot fix (INFERRED, tested by H2): memory-bandwidth and shared-L3 contention.
  The scheduler controls who runs, not how fast memory is.

## 6. Time: the hardest "small" part

- The Pi stamps with `CLOCK_MONOTONIC_RAW` (ns). The STM32 stamps with a hardware timer (µs).
  They are separate clock domains: different origins and slightly different rates.
  Never subtract one from the other directly.
- **Four-timestamp exchange** (NTP-style, RFC 4330 §5): Pi sends at T1, STM32 receives at T2,
  STM32 replies at T3, Pi receives at T4.
  offset = ((T2 - T1) + (T3 - T4)) / 2, round-trip delay = (T4 - T1) - (T3 - T2).
  Repeating it gives offset + drift (a straight-line fit). Keep the samples with the smallest delay.
- **Validation:** a GPIO edge from the Pi captured by an STM32 timer input capture gives an
  independent check. Target: sub-millisecond agreement (to be measured).
- Without this mapping, end-to-end AoI cannot be computed. This is why ECHO_RESP carries T2 and T3.

## 7. The STM32 side in detail

### 7.1 Tasks
| Task | Priority | Job |
|---|---|---|
| UART RX ISR | interrupt | push bytes into a FreeRTOS stream buffer, nothing else |
| RX task | high | run the byte-wise parser; deliver valid frames to the supervisor; answer ECHO_REQ immediately |
| supervisor | highest application priority, 1 kHz, absolute release (`vTaskDelayUntil`) | timers + state machine + output |
| status | low, 10 Hz | send MCU_STATUS (state, missed heartbeats, CRC errors) |

### 7.2 Supervisor logic (the safety core)
- **Two timers:** `last_heartbeat` (is the bridge alive?) and `last_fresh_result`
  (is the data recent?). The bridge can be alive yet forward stale results, so heartbeat
  alone is not enough (R1, Simplex architecture).
- **What refreshes a timer:** only a frame with a valid CRC and a *newer* sequence number.
  Duplicates, older sequence numbers and malformed frames refresh nothing.
- **States:**
  - INIT: until the first valid result.
  - FRESH: both timers within limits; Pi decisions are used.
  - HOLD: a timer exceeded 60 ms (ASSUMED); stop using new Pi decisions, keep the last safe action.
  - FAILSAFE: exceeded 200 ms (ASSUMED); drive the safe output.
- **Latched FAILSAFE:** leaving FAILSAFE needs an explicit rearm after a healthy interval,
  so the system does not flap between states.
- **Worst-case reaction (what E4 checks):** timeout + one supervisor tick (1 ms) + output time.

## 8. The protocol (already written)

`protocol/PROTOCOL.md`, code in `protocol/src/hea_proto.c`, tests pass on the host.
Frame: `A5 5A | version | type | seq(2) | len | payload(0-64) | CRC-16/CCITT(2)`.
Messages: HEARTBEAT, INFERENCE (`t_input`, `t_done`, input seq, class, confidence),
ECHO_REQ, ECHO_RESP (T1, T2, T3), MCU_STATUS.

## 9. What exists today vs what must be built

| Item | Status | Where |
|---|---|---|
| Protocol library + host tests + CI (host tests, Cortex-M4 and M7 compile) | DONE (host only) | `protocol/`, `.github/workflows/ci.yml` |
| P0.5 skeleton: timing helpers, workload harness, supervisor INIT/FRESH/HOLD/FAILSAFE, tests | EXISTS on branch `feat/software-skeleton-wip`, **not merged** | `linux/`, `stm32/`, `tests/` there |
| Pi provisioning + experiment runner + metadata/validity | WRITTEN, UNVERIFIED on hardware | `scripts/pi/` |
| Research notes + design revision | DONE (citations not spot-checked) | `docs/research/` |
| Everything else below | TODO | |

Two things to reconcile when merging the skeleton:
1. The skeleton has its own `protocol/protocol.c`; the main branch has `hea_proto.c`. Keep one.
2. The skeleton supervisor uses **one** timer and recovers after 1 valid packet. The design now
   needs **two** timers and a latched FAILSAFE with rearm (DESIGN_CHANGES #1-#3).
   Also align state names: PROTOCOL.md says NORMAL/DEGRADED/FAILSAFE, the design says FRESH/HOLD/FAILSAFE.

## 10. Implementation plan, in order

Each step has a "done when" check. Do them in this order; later steps depend on earlier ones.

### Stage 1: software only (Mac, no hardware)
| # | Work | Done when |
|---|---|---|
| 1 | Merge the skeleton into the main branch; one protocol library; one byte order; state names aligned | CI green; one `protocol/` |
| 2 | Supervisor v2: two timers, sequence check, latched FAILSAFE + rearm, pure C with no FreeRTOS calls (time passed in as an argument) | host unit tests for: heartbeat lost, results stale but heartbeat alive, duplicates, CRC errors, rearm |
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

## 11. Who does what (suggestion for two people)

- **Person A, Linux side:** steps 4, 5, 7, 12-14 (bridge, workload, profiles, contention experiments).
- **Person B, MCU side:** steps 2, 3, 6, 8-11, 15 (supervisor, clock sync, firmware, bring-up, fault experiments).
- Together: step 1 (merge) and step 16 (analysis, report).
The protocol is the contract between the two; change it only together.

## 12. Words you will see

| Term | Meaning here |
|---|---|
| AoI, Age of Information | now minus the capture time of the newest data the MCU holds |
| V(τ) | fraction of time AoI is above threshold τ |
| P50/P95/P99 | median, 95th and 99th percentile of a latency distribution |
| Jitter | variation in timing around the intended time |
| SCHED_FIFO / SCHED_OTHER | Linux real-time fixed-priority class / default fair class |
| cgroup `cpu.max` | Linux limit on CPU time per period for a group of processes |
| `mlockall` | locks a process's memory in RAM so it cannot page-fault |
| PREEMPT_RT | Linux kernel configuration that makes most of the kernel preemptible |
| Simplex architecture | a safe, simple controller supervises a complex one and takes over when it misbehaves |
| Latched | stays in that state until explicitly reset |
| t_f, t_d, t_s | fault onset, supervisor decision, safe output (E4 timestamps) |
