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
make -C stm32 firmware CLOCK_SOURCE=HSE RX_MODE=DMA UART_BAUD=921600 DEBUG_VCP=0 BRINGUP_BLINK=0
make -C stm32 firmware CLOCK_SOURCE=HSI # deliberate fallback profile
make -C stm32 firmware RX_MODE=IRQ # per-byte ISR fallback
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
| rx | 2 | Circular DMA bytes (or IRQ stream records) to `hea_parser`; CRC-valid frames queued with receipt time and generation; valid echo requests queued for reply |
| status_tx | 1 | Sole USART1 transmitter; checks every tick, one echo per iteration, transition ring every tick, status every 100 ms; drains bounded capture queue |

Default `RX_MODE=DMA` uses a static 2048-byte circular buffer on DMA2 Stream2,
Channel 4 (USART1_RX), direct byte mode, high DMA arbitration priority. The RX task
wakes on USART IDLE/error notification and polls with a one-tick timeout (1 ms).
There is no per-byte RX interrupt or DMA IRQ. Each drain snapshots NDTR and reads
only that bounded batch; notifications may coalesce without losing positions.
This removes the per-byte CPU service deadline while retaining the scheduling,
queueing and freshness mechanisms studied by this project. Pinout and task/IRQ
priorities are unchanged. Register mapping and SR/DR clearing follow
[ST RM0390](https://www.st.com/resource/en/reference_manual/rm0390-stm32f446xx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf).

DMA T2/receipt is the TIM2 sample when the RX task reads the last CRC byte. It is
later than physical receipt by at most the poll period **plus** task release jitter,
higher-priority execution and batch drain time; IDLE usually wakes it sooner. The
poll contribution is bounded by 1 ms, but a strict total 1 ms bound is not claimed
without a hardware scheduling measurement. At nominal baud the ring holds about
22.19 ms of continuous traffic. A possible whole unseen lap (including a stalled
drain) discards the batch and resets partial parsing rather than treating equal
indices as empty. This guard assumes the configured line rate; it is not an
unbounded-lossless buffer. DMA bus/FIFO/direct-mode errors fail closed. UART errors
or an RXNE byte possibly consumed by IDLE clearing mark a discontinuity; the next
drain discards its snapshot. `rx_dropped` counts such incidents, not exact DMA bytes.

`RX_MODE=IRQ` retains the 256 fixed-size timestamped byte records (2 KiB), with T2
sampled in RXNE handling. A full stream marks the next retained byte as a gap.
Both modes reconstruct extended receipt from a current chronological clock sample
and capture generation in a short critical section. They never extend an old raw
timestamp as a new clock sample. Frame/echo queues each have eight slots; capture
has eight. Overflow never blocks the supervisor or refreshes liveness. UART
PE/FE/NE/ORE counters and aggregate error count saturate rather than wrap.

The adapter is called only by the supervisor owner, not concurrently from RX.
T3 is sampled after the previous UART transmission completes and before response
packing/encoding/TX. ISR entry delay, CRC encoding, task preemption and serialization
remain timestamp uncertainty; echo is not a hardware TX timestamp. TIM2_CH1 rising
edges on PA0 are captured by hardware, queued by the ISR, and reported in status.
Overcapture and queue loss share a counter. Match GPIO pulses slowly enough to avoid
losing correspondence (start at 1 Hz); status reports only the latest retained edge.

MCU_STATUS uses the optional 58-byte v3 extension documented in
`protocol/PROTOCOL.md`: normal state/counters plus last capture, capture count,
RX drops, split UART errors, queue drops, capture losses, clock fallback, event losses
and maximum observed IRQ-masked cycles. Update the Pi decoder to this
shared library; older strict nine/33/38-byte decoders reject this status.
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
measurement without changing task priorities or supervisor policy.
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

## RX regression investigation (2026-10-12)

**UNVERIFIED ON HARDWARE.** The ticket's 40 s A/B measurements are user-supplied;
no new rig measurements or numeric DWT maxima are available from this host.

Static inspection of `git diff 68aa5be..fec09e1 -- stm32/` found transition-ring
recording added inside the existing critical sections around `supervisor_update`
and `supervisor_receive_frame`, plus a new critical section copying events on
status wakeups. The adapter includes 64-bit division for inference validation
(already present before this regression). Masking that entire call is unnecessary
and leaves RXNE vulnerable to the added work. This patch removes those masked
calls: the priority-3 supervisor is the sole writer; lower-priority status readers
suspend scheduling for ring dequeue/snapshots while leaving interrupts enabled.
Only clock/generation and short ISR-counter snapshots need application masking.
This is a statically verified latency hazard/remediation, **not proof** that those
extra instructions account for 99–125 errors. ORE vs FE/NE and timing must be
measured on the rig before assigning the physical root cause.

`supervisor_pop_transition` does decrement `transition_count`; its host test drains
the ring to empty. Thus the never-cleared-count hypothesis is false. The old status
task already polled each tick. Notifications now occur only on an empty-to-nonempty
ring transition, avoiding repeated notifications when TX has pending events.
STATE_EVENT and default HSE remain enabled.

DWT CYCCNT instrumentation uses a local `portmacro.h` wrapper, leaving the reference
kernel untouched. It tracks outermost BASEPRI intervals across task critical
sections, kernel queue/notification masks, ISR API masks and SysTick. A linker
wrapper additionally measures the masked `vTaskSwitchContext` body in PendSV.
Disassembly verifies these hook calls. `max_irq_masked_cycles` is the maximum
observed **instrumented body**, not exact edge-to-edge interrupt latency: the
entry/exit bookkeeping and PendSV instructions outside its wrapped call are not
included, while bookkeeping inside an outer measurement is included. No attempt
is made to subtract instrumentation overhead. It excludes boot and fatal PRIMASK
fault loops, resets when the supervisor starts, and tolerates DWT wrap for intervals
shorter than 51 s. The next status reports the maximum; cycles / 84 gives us.
An observed value below 21 us alone does not prove RXNE can always meet its deadline.

Build validation also exposed a reproducibility bug: macOS GNU make 3.81 can reuse
some objects when configuration stamps change within the same second, producing a
mixed HSI/HSE or IRQ/DMA image. Changed configurations now force every object,
ELF and binary to rebuild irrespective of timestamp resolution. This does not
establish that the ticket's measured images were affected.

Reproduce the checks from the worktree root:

```sh
make -C protocol test-char-modes
make -C stm32 test
make -C linux all test
python3 -m unittest discover -s linux/inference/tests -v
python3 -m unittest discover -s analysis/tests -v
scripts/stm32/build.sh CLOCK_SOURCE=HSE RX_MODE=DMA
scripts/stm32/build.sh CLOCK_SOURCE=HSE RX_MODE=IRQ
```

For the hardware rerun, repeat the same 40 s workload in both RX modes and capture
`mcu_status.csv`, CRC failures and STATE_EVENT transitions. Compare deltas in ORE,
FE, NE, PE, drops and `max_irq_masked_cycles`; retain the exact build configuration.
Also exercise continuous RX (no IDLE), a split frame across DMA wrap and sender
stop/restart. DMA timestamp offset/jitter, error recovery and absence of spurious
HOLD remain **UNVERIFIED ON HARDWARE**.

Local validation after this patch (Arm GCC 14.2.1, `-Wall -Wextra -Werror`):

| Clock / RX | Flash (text + data) | Static RAM (data + bss) | RAM incl. 2048 B MSP |
|---|---:|---:|---:|
| HSE / DMA (default) | 11576 B | 11332 B | 13380 B |
| HSE / IRQ | 12344 B | 11364 B | 13412 B |
| HSI / DMA | 11448 B | 11324 B | 13372 B |
| HSI / IRQ | 12232 B | 11364 B | 13412 B |

All four configurations built with zero warnings; unchanged default rebuild reused
objects, and rapid configuration switches rebuilt all objects. Protocol/clock-sync
passed ASan/UBSan in both char modes. Supervisor: 23 scenarios, 66744 checks. New
DMA cursor tests cover every physical wrap and frame split, NDTR reload, possible
unseen laps and TIM2 wrap. Pi C executables and sanitized PTY tests passed, including
9/33/38/58-byte status CSV compatibility. Summary tests: 6 passed; inference Python:
34 tests, 3 platform/environment skips; E4 analysis: 21 passed. Unix socket bind is
sandbox-denied (PTY tests use socketpair); Linux-only runtime checks skip on macOS.
These tests do not emulate STM32 DMA arbitration, IDLE clearing or interrupt timing.


## E4 apparent tick-rate fault investigation (2026-10-12)

The stored `feat/fw-rx-fix:results/e4/20261012T093526Z_e4` evidence does not
establish an early heartbeat timeout. In `F2-r01/pipeline/state_events.csv`:

- Last accepted heartbeat: 20,634,512 us.
- HOLD (reason 9, SOURCE_AGE_HOLD): 20,733,108 us, or 98,596 us after heartbeat.
- FAILSAFE (reason 3, HEARTBEAT_TIMEOUT): 20,735,108 us, or **100,596 us** after heartbeat.

The summary used the first FRESH exit as detection, assigned its clock reference
and threshold from the injected fault, and therefore compared source-age HOLD
with heartbeat timeout. That is the cause of the apparent ~1.8% discrepancy.
Stored F1/F2 heartbeat FAILSAFE times are 100,128–100,641 us; F4 is
100,045–100,931 us. F3-r01 HOLD is 175,766 us after inference receipt; its
approximately 20 ms input-to-send age plus 5 ms transit allowance makes this
consistent with 200 ms source-age HOLD. Those policy terms are preserved.
Analysis now selects each event's reference and comparison from its reason.

Established by reading the raw STATE_EVENT and summary CSV blobs with `git show`,
then tracing `supervisor_update`, `now_task`/`now_locked`, the clock setup and the
compiled reference FreeRTOS port. The supervisor already uses extended TIM2 us,
not xTaskGetTickCount. Nominal HSE 8 MHz / M=8 (or HSI 16 MHz / M=16), N=336,
P=4 gives 84 MHz; AHB /1 and APB1 /2 with timer doubling give TIM2 84 MHz.
PSC=83 gives 1 MHz. FreeRTOS configCPU_CLOCK_HZ=84 MHz and configTICK_RATE_HZ=1000
produce LOAD=83,999 with HCLK selected. The startup HCLK/8 SysTick timeout is
stopped and cleared; the kernel reinitializes it. No stale HSI clock assumption
was found. Nominal clocks now share `clock_config.h`; changing oscillator
compensation would be unsupported by these results.

TIM2 remains the deadline source: it keeps supervisor policy independent of
scheduler tick quantization/rate while FreeRTOS still schedules the 1 ms task.
This supports deterministic portable timeout tests and separates deadline policy
from scheduling latency, an OS learning objective. Task priorities are unchanged.
The highest-priority owner asserts actual SysTick LOAD/control at startup and
samples coherent tick/TIM2 pairs in a short critical section. Ppm arithmetic
runs with interrupts enabled. The first ratio is available after one second,
then every ten seconds of TIM2 time; it is repeated in status and Pi CSV.
See `protocol/PROTOCOL.md` for sign, unavailable sentinel, and quantization.
A shared oscillator error cannot be detected by this relative-rate check alone.

New behavior is **UNVERIFIED ON HARDWARE**. No flash, reset, serial-device or GPIO
operation was performed for this ticket. Host tests include the measured F2 event
ordering as a synthetic regression, exact heartbeat expiry, F5's source-age HOLD
with live heartbeats, and ratio startup/cadence/sign/counter-wrap checks.


Local validation for this ticket: all four HSE/HSI × DMA/IRQ firmware profiles
cross-compiled with `-Wall -Wextra -Werror` and zero warnings; final artifacts use
HSE/DMA, 921600 baud, VCP/blink disabled. Default image is 12,008 B flash,
11,348 B static RAM plus 2,048 B reserved MSP. Protocol/clock tests passed
ASan/UBSan in both char modes; supervisor (24 scenarios, 66,768 checks), DMA and
ratio tests passed. Linux C builds and sanitized PTY tests passed, including
9/33/38/58/64-byte status compatibility and SIGUSR1 suppression/resume with live
heartbeats and delayed IPC backlog discarded. E4 analysis: 23 tests; pipeline
summary: 6; inference: 34 (3 platform/sandbox skips); analyzer: 6. Named Unix
sockets are sandbox-denied (C tests use socketpair); Linux RAW clock/scheduler
checks require the Pi and were skipped on macOS. **UNVERIFIED ON HARDWARE**.

### E3 real INF_RX instrumentation (locally verified only)

Every accepted inference queues one optional v3 INF_RX with its wire sequence,
extended TIM2 receipt timestamp, supervisor age at evaluation, and resulting
state. A static 16-entry ring drops new reports when full and saturates its boot
loss counter. The existing TX owner drains up to four per iteration; no UART
work is added to the supervisor/ISR. At 10 Hz this adds only 320 wire bytes/s.
Task priorities, HSE/DMA configuration and pins are unchanged. Receipt continues
to mean when RX reads the final CRC byte, with the documented DMA polling delay;
it is not the physical arrival instant at the UART pin.

HSE+DMA, default 921600-baud build with `-Wall -Wextra -Werror`: zero warnings.
GNU size: text 12,468 B, data 4 B, bss 11,872 B; flash text+data **12,472 B**,
static RAM data+bss **11,876 B**. The linker additionally reserves 2,048 B for
MSP, so static RAM plus that reservation is **13,924 B**. Static RTOS task stacks
are included in bss. These are linked sizes, not measured stack high-water marks.
Physical flash/run verification is outstanding; no hardware was touched.
