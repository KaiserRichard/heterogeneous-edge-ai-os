# System Overview: what we build, what it improves, where it fits

Status: PROPOSED (2026-10-05). Numbers marked ASSUMED are starting values that the
experiments will tune or justify. Nothing here is MEASURED yet.

## 1. The idea in plain terms

**Example scenario** (numbers are illustrative, not measured). The Pi takes a camera-like
input every 33 ms, runs a neural network on it (about 20 ms normally), and sends the
result, e.g. "obstacle / no obstacle", to the STM32. The STM32 controls something physical
(e.g. a motor) and must act on a *recent* answer.

**Problem 1: late data.** When other programs load the Pi, Linux shares the CPU "fairly",
so our program sometimes waits its turn. A 20 ms answer can become 200 ms. Worse, results
pile up in a queue, so the STM32 acts on an answer about the world 200 ms ago without
knowing it is old.

**Problem 2: silent failure.** If the program crashes or Linux freezes, the STM32 keeps
seeing the last answer ("no obstacle") forever. A watchdog program on the Pi does not help,
because it freezes together with Linux.

**Fix 1, on Linux (built-in features only, no kernel changes).** Give the small program
that sends results top priority (`SCHED_FIFO`) and its own CPU core, cap the heavy
programs (cgroups), and always send only the newest result, dropping old ones.
Goal: the important data stays on time even when the Pi is busy.

**Fix 2, on the STM32.** Every message carries a timestamp, and the Pi sends a heartbeat
every 20 ms. The STM32 checks the clock: no heartbeat for 60 ms means HOLD (stop trusting
new Pi decisions); 200 ms means FAILSAFE (go to a safe state, e.g. stop the motor). The
STM32 is a separate chip with its own real-time OS, so this works even when Linux is dead.

**Then we measure** how late the data gets with and without Fix 1, and how fast Fix 2
reacts to each kind of failure.

Analogy: the Pi is a smart but easily distracted worker; the STM32 is a strict
supervisor with a stopwatch who does not depend on the worker to report its own failure.

We do not write a new OS or patch the kernel (see `PROJECT.md` non-goals). The "OS
design" is how work is partitioned across two operating systems and how the stock
mechanisms (scheduler classes, CPU affinity, cgroups, memory locking, RTOS priorities,
watchdogs) are configured and combined.

## 2. Stock setup vs this design

"Stock" = everything on the Pi with Linux defaults: one inference process, default
scheduler, no pinning, an ordinary queue between stages, no external supervisor.

| Concern | Stock Linux, defaults | This design | Why it matters |
|---|---|---|---|
| Who decides "the data is too old"? | Nobody, or a thread on the same Linux that may itself be stalled | STM32 supervisor in a separate OS on separate silicon | A safety check must not depend on the thing it checks. |
| Linux hangs or the process crashes | Silent; consumers keep using the last value | Heartbeat timeout drives HOLD then FAILSAFE within a bounded time | Bounded failsafe reaction is the core safety property. |
| Data path under CPU load | Bridge competes equally with stressors (`SCHED_OTHER`) | Bridge runs `SCHED_FIFO` on a pinned core; workload and stressors capped by cgroup `cpu.max` | Keeps the short, critical path from waiting behind bulk work. |
| Page faults in the critical path | Possible | Bridge uses `mlockall` and preallocated buffers | Removes a source of multi-ms stalls. |
| Queueing between stages | FIFO queue; under load it grows, so outputs get older | Latest-value buffer: a new result overwrites an unsent old one | Under overload, sending old data late is worse than dropping it. |
| Time | Each side has its own clock, never related | Linux and STM32 clocks aligned via GPIO edge capture (UART echo as fallback) | Freshness can only be measured end-to-end if clocks are related. |
| Evidence | "It feels fast" | Every run logs P50/P95/P99, AoI, deadline misses, throttling validity | Claims become measurements. |

Costs we accept and will report:
- `SCHED_FIFO` can starve other tasks if the bridge misbehaves. Mitigation: the kernel's
  default RT throttling (`sched_rt_runtime_us`, 95%) stays on, and the bridge does very little work.
- CPU scheduling does not fix memory-bandwidth or cache contention. INFERRED from how the
  Pi 5's shared L3 cache and LPDDR4X work; the experiments test this explicitly instead of assuming the tuning fixes everything.
- One more board, one more firmware, one more link to maintain.

## 3. What we will implement

### Linux side (Pi 5)
| Component | Role |
|---|---|
| `source` | Synthetic "sensor" producing timestamped input frames at a fixed rate (30 Hz, ASSUMED). This is the AoI origin. |
| `workload` | Inference on each frame (small CNN via ONNX Runtime; synthetic compute as fallback). Variable latency by nature. |
| `bridge` | Receives results over a Unix domain socket, keeps the latest value, frames it onto the UART, sends heartbeats (every 20 ms, ASSUMED) and clock-sync echoes. |
| Runtime profiles | `P0 stock` (all defaults), `P1 tuned` (FIFO + pinning + cgroups + mlockall), `P2 tuned + latest-value` buffer. Same code, selected by config. |
| Stressors | `stress-ng` profiles: CPU, memory/VM, cache, I/O. |
| Runner + logger | `run_experiment.sh` wrapper, CSV per run, metadata, validity flag. |

### STM32 side (F446RE, FreeRTOS)
| Task / part | Priority | Role |
|---|---|---|
| UART RX ISR + RX task | High | Bytes into a stream buffer, parsed by the shared protocol library. |
| Supervisor task | High, periodic 1 kHz | Tracks heartbeat age and data AoI. State machine: FRESH, then HOLD (3 missed heartbeats, about 60 ms, ASSUMED), then FAILSAFE (about 200 ms, ASSUMED). |
| Status task | Low, 10 Hz | Sends MCU_STATUS back to the Pi. |
| Sync capture | Timer input capture | Timestamps the Pi's GPIO edge for clock alignment. |
| Failsafe output | GPIO + LED | Visible state, and a pin a logic analyzer can time. |

### Shared
- `protocol/`: framing + CRC, already written and host-tested.
- Your P0.5 skeleton (timing, workload harness, supervisor INIT/FRESH/HOLD/FAILSAFE) gets merged in and reused.

## 4. What the experiments must show

| ID | Question | Compare | Main metric |
|---|---|---|---|
| E1 | How much does Linux contention hurt the data path? | P0 with no load vs each stressor | Inference + bridge latency P50/P95/P99 |
| E2 | How much does runtime tuning recover? | P0 vs P1 under each stressor | Same, plus bridge dispatch jitter |
| E3 | Does latest-value delivery keep data fresh under overload? | P1 vs P2 at rising load | End-to-end AoI distribution, deadline-miss rate |
| E4 | Is failsafe reaction bounded no matter what Linux does? | Kill bridge, SIGSTOP, FIFO CPU hog | Detection and safe-state latency on the STM32 |

Expected outcomes (hypotheses, not results):
- H1: CPU stressors inflate P99 far more than P50.
- H2: P1 recovers most of the CPU-contention tail but little of the memory/cache-contention tail.
- H3: Under overload, P2 bounds AoI while P0/P1 let it grow with the queue.
- H4: STM32 failsafe latency stays within timeout + one supervisor tick for every fault type,
  including ones that leave Linux unable to react.

## 5. Where this sits in WBR

```
 WBR robot                                     This project
 L5 Autonomy (Pi)                              -
 L4 Perception: D435i, ORB-SLAM3, ROS 2 (Pi)   stand-in: inference workload
 L3 Pi <-> MCU boundary                        BUILT: protocol, clock sync, AoI, heartbeat
 L2 Hard real-time control (STM32H7)           BUILT (supervisor part): FRESH/HOLD/FAILSAFE
 L1 Motors (Damiao, CAN)                       -
```

WBR gives the safety rule "if the Pi fails, the robot must not immediately lose balance".
This project is the measured, small-scale version of that rule:
- **N5 profiling:** the same contention and scheduling method later profiles ORB-SLAM3 on the WBR Pi.
- **N6 perception-health interface:** the supervisor is the first concrete design of how the MCU decides Pi output is stale or dead.
- **N7 integration boundary:** protocol, clock alignment and failsafe-latency numbers become the starting Pi-to-MCU contract.

Methods and code transfer; the numbers do not (different Pi, workload and MCU).

## 6. Later: moving to the Damiao STM32H7 (not in scope now)

Kept short on purpose. Portable code (protocol, supervisor, Linux side) moves unchanged
because hardware access stays behind a small port layer and CI already compiles for
Cortex-M7. The H7 port itself (UART/DMA with D-cache, clocks, FreeRTOS CM7 port) and the
WBR failsafe policy ("ignore Pi commands, keep balancing") are WBR integration work for later.
