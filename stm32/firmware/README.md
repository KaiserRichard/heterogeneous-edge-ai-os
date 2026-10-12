# Nucleo-F446RE FreeRTOS firmware

**UNVERIFIED ON HARDWARE:** the clock/event changes described here require a new
hardware run. User-reported `hw_smoke1` measured full-duplex USART1 at 921600:
322 status frames, zero CRC errors, FRESH held, then HOLD/FAILSAFE after stopping
the bridge. HSI time ran fast (31 echoes: slope 1.01884, residual RMS about 1.08 ms;
100.004 ms MCU status intervals per 98.19 ms Pi). Those observations describe the
previous firmware, not validation of these changes.

From the repository root on macOS:

```sh
make -C stm32 firmware
make -C stm32 test
make -C protocol test
```

Artifacts: `stm32/firmware/build/firmware.elf`, `firmware.bin`, `firmware.map`,
`size.txt`. `scripts/stm32/build.sh` wraps the build. GCC defaults to
`/usr/local/bin/arm-none-eabi-gcc`. On the Pi use
`make -C stm32 firmware CROSS_COMPILE=arm-none-eabi-`.

`FREERTOS_REF` defaults to
`/Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/third_party/nucleo-f446re-freertos`.
Override it with the absolute reference checkout path on another machine.
The kernel and GCC ARM_CM4F port are compiled directly from `ThirdParty/FreeRTOS`;
the device/CMSIS headers and linker script are read directly from
`004LEDsNotifyISR/src` and `004LEDsNotifyISR/lnk/lk_f446re.ld`. There are no vendored
reference sources, HAL, heap implementation, or SEGGER dependencies. The reference
startup and examples 004/006 were studied; this port has its own small assembly
startup, enables the FPU before C, and maps the FreeRTOS exception handlers.
`stack.ld` adds a 2 KiB MSP reservation assertion to the reference linker script
(which conservatively declares flash/RAM one byte smaller than their physical size).

Build options (command-line changes automatically rebuild objects):

```sh
make -C stm32 firmware CLOCK_SOURCE=HSE UART_BAUD=921600 DEBUG_VCP=0 BRINGUP_BLINK=0
make -C stm32 firmware CLOCK_SOURCE=HSI # deliberate fallback profile
make -C stm32 firmware DEBUG_VCP=1 BRINGUP_BLINK=1
```

Default flags include `-mcpu=cortex-m4 -mthumb -mfloat-abi=hard
-mfpu=fpv4-sp-d16 -Os -Wall -Wextra -Werror`. No RTOS dynamic allocation is enabled;
all three tasks, idle task, stream buffer and queues have static storage. Each app
stack is 512 words (2 KiB); idle is 128 words. Linker size includes these stacks,
not the separately reserved 2 KiB interrupt stack. Stack high-water margins still
need measurement under traffic and nested interrupts.

Clock and timing decisions:

- Default `CLOCK_SOURCE=HSE`: 8 MHz ST-LINK MCO enters PH0/OSC_IN in HSE bypass
  mode, PLL M=8/N=336/P=4. `CLOCK_SOURCE=HSI` uses nominal 16 MHz with M=16 and
  the same N/P. Both give nominal 84 MHz core/AHB/APB2, 42 MHz APB1 and 84 MHz
  TIM2 input. TIM2 PSC=83 therefore preserves nominal 1 MHz; USART BRR is derived
  from the unchanged PCLK. HSE removes the measured HSI drift from E4 timing
  and improves baud margin while keeping scheduling and deadline configuration.
- HSE startup waits at most 200000 SysTick HSI/8 cycles (nominal 100 ms; actual
  duration has HSI tolerance). If not ready, PLL uses HSI and status sets
  `clock_fallback=1`. Deliberate HSI selection sets no fallback flag. This is a
  startup fallback, not recovery from loss of MCO after switching to HSE.
  FreeRTOS reconfigures SysTick when starting the scheduler.
- [ST UM1724 §6.7](https://www.st.com/resource/en/user_manual/dm00105823.pdf)
  specifies ST-LINK MCO fixed at 8 MHz: SB54/SB16/SB50 ON, SB55 OFF, R35/R37
  removed. MB1136 C-02 and later default to MCO; C-01 defaults to no HSE. Check
  the actual board revision/routing and keep ST-LINK powered; no UART pin changes.
- Flash uses two wait states at the board's 3.3 V supply, per
  [ST RM0390](https://www.st.com/resource/en/reference_manual/dm00135183.pdf).
- FreeRTOS owns SysTick at 1 kHz; TIM2 PSC=83/ARR=0xffffffff gives nominal 1 MHz.
  Raw timer wraps every 4294.967296 s. A critical-section-protected extended clock
  is sampled by the supervisor every millisecond; ambiguous deltas fail closed.
- USART1 is 8N1, no flow control, oversampling 16. At 84 MHz and requested 921600,
  BRR=91, calculated baud=923076.923, error **+0.16026%** for both clock sources
  before oscillator error. HSE total error is this divider error plus MCO accuracy
  (not measured here). With the `hw_smoke1` HSI slope 1.01884, inferred baud is
  940467.692 (**+2.04728%** relative to 921600); this is inferred from timer drift,
  not directly measured UART bit timing. HSI fallback retains that risk and its
  oscillator/temperature variation. `UART_BAUD` selects rounded BRR. USART2 debug at 115200 uses BRR=365 at 42 MHz:
  115068.493, **-0.11416%**, excluding HSI error.
- IRQs USART1 and TIM2 use preemption priority 6; four priority bits, grouping 3,
  syscall ceiling 5 (0x50), SysTick/PendSV 15. Both use `FromISR` APIs and yield.

Ownership and scheduling support the OS experiments:

| Task | Priority | Work |
|---|---:|---|
| supervisor | 3 | Absolute 1 ms releases; periodic update even without traffic; at most eight queued frames/release; sole supervisor owner; output update |
| rx | 2 | ISR stream records to `hea_parser`; CRC-valid frames queued with receipt time and generation; valid echo requests queued for reply |
| status_tx | 1 | Sole USART1 transmitter; checks every tick, one echo per iteration, transition ring every tick, status every 100 ms; drains bounded capture queue |

The byte stream holds 256 fixed-size timestamped byte records (2 KiB). T2 is the
TIM2 sample at final CRC-byte RXNE handling, before task/queue delay. RX reconstructs
its extended time from a current chronological clock sample, then stamps generation
at handoff under the same critical section used by the owner. It never extends an
old raw timestamp as a new chronological sample. Session changes can deliberately
invalidate already queued frames; subsequent sender traffic establishes health.
Frames/echoes each have eight slots; capture has eight slots. Overflow is counted,
never blocks the supervisor, and does not refresh liveness. A stream overflow marks
the next retained byte as a discontinuity to reset partial parsing. UART PE/FE/NE/ORE
are counted and discard the affected byte. Saturating counters do not wrap.

The adapter is called only by the supervisor owner, not concurrently from RX.
T3 is sampled after the previous UART transmission completes and before response
packing/encoding/TX. ISR entry delay, CRC encoding, task preemption and serialization
remain timestamp uncertainty; echo is not a hardware TX timestamp. TIM2_CH1 rising
edges on PA0 are captured by hardware, queued by the ISR, and reported in status.
Overcapture and queue loss share a counter. Match GPIO pulses slowly enough to avoid
losing correspondence (start at 1 Hz); status reports only the latest retained edge.

MCU_STATUS uses the optional 38-byte v3 extension documented in
`protocol/PROTOCOL.md`: normal state/counters plus last capture, capture count,
RX drops, UART errors, queue drops, capture losses, clock fallback and event losses. Update the Pi decoder to this
shared library; older strict nine/33-byte decoders reject this status.
No heartbeat, inference, echo, sequence, or supervisor policy format changes.
`missed_heartbeats` counts transitions into heartbeat-timeout FAILSAFE, not the
number of absent 20 ms packets. Queue drops aggregate frame and echo queue failures.
CRC count is saturated to 16 bits in status; internal parser counters are uint32.
Capture count is the number dequeued; count zero means no capture, even if timestamp zero.

Thresholds in `main.c` are explicit **PROVISIONAL**, not calibrated bounds:
heartbeat 100 ms; result HOLD 200 ms; result FAILSAFE 500 ms; rearm health 1 s;
transit allowance 5 ms. Source-age estimates retain the core's documented assumptions.
FAILSAFE remains latched. This port exposes no remote or automatic rearm; reset the
board for a fresh test. Healthy traffic alone never clears FAILSAFE. No physical
actuator or independent MCU watchdog is implemented.

Wiring (power off before changing jumpers; 3.3 V signals, common ground):

| Pi / analyzer | Signal | Nucleo pin |
|---|---|---|
| Pi pin 8 / GPIO14 TX | USART1 RX | PA10 / Arduino D2 |
| Pi pin 10 / GPIO15 RX | USART1 TX | PA9 / Arduino D8 |
| Pi pin 6 GND | Common ground | GND |
| Pi pin 11 / GPIO17 | Rising sync edge | PA0 / Arduino A0 / AF1 |
| Analyzer channel 0 | Fresh output / LD2 | PA5 / Arduino D13 |
| Analyzer channel 1 | State/grace output | PB5 / Arduino D4 |
| ST-LINK VCP | Optional USART2 TX/RX | PA2/PA3, Arduino D1/D0; no Pi UART jumpers here |
| Pi USB host | Power, SWD flash, VCP | ST-LINK Mini-B USB |

| State | PA5 / LD2 | PB5 / D4 |
|---|---:|---:|
| INIT | 0 | 0 |
| FRESH | 1 | 1 |
| HOLD | 0 | 1 |
| FAILSAFE / fatal hook | 0 | 0 |

Two analyzer channels distinguish FRESH/HOLD/FAILSAFE transitions without PWM
measurement delay; MCU_STATUS distinguishes INIT from FAILSAFE. HOLD inhibits the
simulated fresh output rather than retaining it. GPIO stores have a few instruction
cycles of skew; measure both. Assertion, stack overflow, malloc-failure, unhandled
interrupt and CPU fault vectors disable interrupts, drive both pins low and halt.
Fatal hook output is not a certified safety mechanism. `BRINGUP_BLINK=1` replaces
PA5 state indication with a 1 Hz blink and holds PB5 low; never use that diagnostic
image for failsafe timing experiments.

Flash/run commands below are **for the Pi**, from the repository root, with the
Nucleo connected by USB. They were not executed for this ticket. Choose one flasher:

```sh
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
  -c 'program stm32/firmware/build/firmware.elf verify reset exit'
# Alternative:
st-flash --reset write stm32/firmware/build/firmware.bin 0x08000000
# Reset/run without flashing:
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
  -c 'init; reset run; shutdown'
```

Wrappers: `scripts/stm32/flash.sh openocd` (or `st-flash`) and
`scripts/stm32/reset.sh`. Build with `CROSS_COMPILE=arm-none-eabi-` and an appropriate
`FREERTOS_REF` on the Pi, or transfer the compiled ELF/bin from macOS. Pi serial
controller/device node must be verified against its provisioning; do not assume
`/dev/ttyAMA0`. VCP appears as `/dev/ttyACM*`, enumerate it before opening at 115200.

Bring-up checklist, in this order; record results as UNVERIFIED until measured:

1. **Blink:** build/flash `BRINGUP_BLINK=1`; verify 1 Hz LD2 and PB5 low. Measure
   period on analyzer, inspect task tick and TIM2 rate. Stop on clock/setup errors.
2. **VCP print:** add `DEBUG_VCP=1`; reset with the console open at 115200 8N1 and
   observe the startup banner. USART2 is debug only, not a protocol transport.
3. **USART1 loopback:** disconnect Pi TX/RX and bridge PA9 to PA10. Restore
   `BRINGUP_BLINK=0`. Observe outgoing status and returning RX on analyzer; with
   GDB/SWD inspect `parser.stats.frames_ok` increasing, CRC/drop/error counters
   zero. Received status frames must not establish FRESH. Remove loopback.
4. **Heartbeat:** connect Pi as above; use v3 CRC-framed HEARTBEAT every 20 ms
   (one stable session ID) followed by advancing INFERENCE at e.g. 50 ms, with
   plausible age and shared wire sequence. Heartbeat alone leaves safe INIT;
   both valid streams yield FRESH/11. Decode extended status and check counters.
5. **Failsafe:** stop only results while heartbeats continue: FRESH/11 → HOLD/01
   at 200 ms source age → FAILSAFE/00 at 500 ms. Reset, establish FRESH, stop
   heartbeats: FAILSAFE/00 after 100 ms receipt silence. Continued traffic must
   not clear the latch. Measure actual detection/output latency on analyzer.
6. **Echo/clock sync:** reset, send ECHO_REQ, verify unchanged T1 and advancing
   T2/T3. Extend raw timestamps chronologically on Pi per `CLOCK_SYNC.md`, then
   fit offset/drift. Test wrap, traffic load and asymmetric delays; no accuracy
   claims until independently measured.
7. **Input capture:** toggle GPIO17 slowly (1 Hz), verify PA0 edge against
   `last_capture_us` and increasing capture count. Check losses, then compare
   capture pairs with echo mapping. Run sustained UART traffic and inspect
   stack high-water marks, overrun/drop counters and supervisor release jitter.

Compile-only validation (macOS, Arm GNU Toolchain 14.2.Rel1 / GCC 14.2.1):

- Default image: text 11,356 B, data 4 B, BSS 10,652 B. Flash image **11,360 B**;
  static RAM **10,656 B**, plus 2,048 B reserved MSP = **12,704 B** budgeted RAM.
- VCP + blink + 115200 variant also compiles with warnings treated as errors.
  Final build artifacts are restored to the default configuration.
- Supervisor tests pass (22 scenarios, 66,626 checks); protocol and clock-sync
  tests pass, including signed/unsigned-char protocol runs and status-extension
  validation under ASan/UBSan.
- Linked vector addresses/Thumb bits, initial MSP, RAM reservation and hard-float
  ELF attributes checked. No heap allocator linked. Shell wrappers pass `sh -n`.

These checks establish build/interface consistency only: **UNVERIFIED ON HARDWARE**.

Each core state change records a 64-bit TIM2 timestamp, reason and last accepted
heartbeat/inference receipt timestamps in a 16-entry static ring. Recording inside
the transition function preserves multiple changes within one supervisor update.
The supervisor notifies the status/TX owner, which drains it on wakeup
(and polls every tick) using optional v3 STATE_EVENT, independent
of 10 Hz status. Overflow drops the newest event and increments a saturating loss
counter in events/status. This instrumentation serves E4 deadline/fault latency
measurement without changing task priorities, ISR work or supervisor policy.
See `protocol/PROTOCOL.md` for the wire layout and Pi mapped-time CSV semantics.

Local validation for this change: protocol/clock-sync and supervisor tests passed
under ASan/UBSan with both signed and unsigned char; Linux programs and PTY pipeline
(including fake-MCU event/status logging and estimator wrap alignment) passed with
warnings treated as errors. Python host suite: 34 tests, 3 environment/platform
skips; summary tests: 6 passed. Named Unix socket bind is denied in this sandbox;
the C pipeline used socketpair and Linux-only checks were skipped on macOS.
Both HSE and HSI firmware profiles cross-compiled with zero warnings. Default HSE
image: text 11996 B, data 4 B, bss 11332 B: **12000 B flash**, **11336 B static RAM**
(includes task stacks/queues), plus **2048 B reserved MSP** (13384 B RAM budget).
HSI image: 11872 B flash, same RAM. Timer accuracy, HSE timeout/fallback, event TX
latency and GPIO correspondence remain **UNVERIFIED ON HARDWARE**.
