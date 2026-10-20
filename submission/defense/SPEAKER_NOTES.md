# Defense speaker notes

21 main slides; target **1,020 seconds = 17:00**. Backup pages are for questions and have no allocated talk time. Read the scripts naturally; use the remaining time on each slide to point to the figure or table and pause. Page numbers match main.pdf. Team identities follow the approved study deck; the older PROJECT.md description of a two-person project is historical, not used to invent a new roster.

| Page | Slide | Target seconds | Cumulative |
|---|---|---:|---|
| 1 | Title | 20 | 0:20 |
| 2 | Motivation | 45 | 1:05 |
| 3 | Problem and research questions | 45 | 1:50 |
| 4 | System architecture | 60 | 2:50 |
| 5 | Scheduling and contention profiles | 65 | 3:55 |
| 6 | IPC and buffering policy | 60 | 4:55 |
| 7 | Clocks and freshness | 65 | 6:00 |
| 8 | Independent supervisor | 60 | 7:00 |
| 9 | Experimental method | 50 | 7:50 |
| 10 | Run validity and rule versions | 50 | 8:40 |
| 11 | Timer wake-up under contention | 60 | 9:40 |
| 12 | Inference baseline | 50 | 10:30 |
| 13 | E1 contention | 45 | 11:15 |
| 14 | E2 tuning | 45 | 12:00 |
| 15 | E3 queue placement | 65 | 13:05 |
| 16 | E4 transition reasons | 65 | 14:10 |
| 17 | Analyzer cross-check | 50 | 15:00 |
| 18 | Limitations | 45 | 15:45 |
| 19 | Conclusion and contributions | 40 | 16:25 |
| 20 | Future work | 30 | 16:55 |
| 21 | References | 5 | 17:00 |

## 1 — Title (20 s)

We study operating-system timing on a Raspberry Pi running Linux and an independent STM32 running FreeRTOS. The key questions are how old a result becomes and what the supervisor observes when Linux stops delivering useful work. Inference is a repeatable workload for the OS experiment.

## 2 — Motivation (45 s)

A correct inference result may arrive too late to be useful. Average execution time does not tell us whether the consumer sees a fresh result during contention. A second problem is that a bridge can remain alive while the model has stopped producing new results. The illustration locates the consumer boundary. We therefore separate liveness from freshness, and place the judgment on a processor whose task execution does not depend on Linux. Our experiment studies that boundary; it does not certify a physical application.

## 3 — Problem and research questions (45 s)

Our three questions connect directly to OS mechanisms. First, how do scheduling and shared-resource contention change timing tails? Second, if we discard old work, which queue must the policy act on? Third, can an independent MCU distinguish missing heartbeats from stale results? We measure timer wake-up, input-to-reception delay, the age of the held useful value, and transitions with reasons. Those metrics answer different questions; we do not substitute a model percentile for consumer freshness.

## 4 — System architecture (60 s)

Follow Figure 2 from left to right. The source releases timestamped inputs. The inference process computes MobileNetV2 results. A separate bridge receives results through Unix datagram IPC and sends framed results and heartbeats. Contention runs on Linux. UART is the sole inter-board link. On the right, FreeRTOS owns the supervisor and local state outputs. The bridge proposes information; the MCU judges whether it is usable. Software experiments replace the physical endpoint with a pseudo-terminal receiver on the Pi. Those experiments measure Linux behavior, whereas the physical fault experiments record MCU state changes.

## 5 — Scheduling and contention profiles (65 s)

P0 uses ordinary scheduling. In the recorded P1 pipeline campaign, the source uses FIFO priority 60 and the bridge priority 70. In both profiles source and bridge run on CPU 1. P0 leaves their memory unlocked; P1 locks it. Inference remains ordinary on CPU 0 and unlocked in both profiles. E2 therefore changes scheduling and locking together; it cannot isolate either contribution. These are applied settings, rather than an older planned profile in the guide. Affinity selects CPU placement. Memory locking removes paging as one source of delay. Cgroups can cap CPU service, but quota comparisons were not measured here. Cyclictest uses a separate FIFO-50 configuration. These mechanisms reduce particular scheduling delays; they do not reserve the shared memory bus. A high-priority task that never blocks can also starve the bridge, which motivates the F4 experiment.

## 6 — IPC and buffering policy (60 s)

Figure 3 distinguishes two waiting points. The bridge FIFO preserves ordered results in a bounded 256-record queue, dropping new arrivals if full. Bridge latest retains one unsent result and counts overwrites. But neither policy removes inputs already waiting before inference. The later input-latest policy drains waiting source datagrams and keeps the newest valid input before starting the next inference. It does not cancel work already executing. This is an IPC and overload-policy choice: where we discard information determines whether compute time is spent on obsolete work. E3 measures bridge queue behavior; its upstream-backlog explanation remains inferred until a clean input-policy comparison is available.

## 7 — Clocks and freshness (65 s)

Linux has two clocks relevant here. MONOTONIC supports absolute release deadlines. Recorded pipeline timestamps and age-at-send use MONOTONIC_RAW. We never subtract a timestamp from one domain from a timestamp in the other. The Pi computes input-to-send duration on its own clock. The MCU then adds elapsed time since receipt and a provisional five-millisecond transit allowance. This estimate lets the supervisor reject old results without subtracting absolute Pi and MCU clocks. Echo exchanges provide a separate offset-and-drift map for analysis. An asymmetric link can bias that map. The allowance is a configured choice, not a proven bound. Held-value AoI measures how old the newest useful input remains as time passes.

## 8 — Independent supervisor (60 s)

Figure 4 separates the liveness and result-age paths. Healthy input brings INIT to FRESH. Source age at 200 milliseconds enters HOLD, and at 500 milliseconds enters FAILSAFE. Heartbeat age at 100 milliseconds can enter FAILSAFE directly. These are provisional configured values. Fresh results may recover HOLD, but FAILSAFE is latched. The portable core has a local healthy-rearm operation; the present board port requires reset. One FreeRTOS task owns the supervisor with static resources. There is no independent MCU hardware watchdog or physical actuator in this implementation. The crucial point is that a healthy heartbeat cannot renew the age of an old result.

## 9 — Experimental method (50 s)

The rig uses the stock Ubuntu kernel and F446RE UART with DMA reception at 921600 baud. The load key defines the treatments: CPU computes on cores 2 and 3; Stream performs sequential array operations on core 2; Cache stresses a two-mebibyte working set on core 2; Memrate reads and writes on cores 2 and 3. The timer and pipeline inference use core 0; source and bridge use core 1. Thus loaded timing can change even when stress runs elsewhere. Model-only inference instead allows cores 0 through 3. Timer and pipeline use performance governor; model-only uses ondemand. Three pipeline repeats fall below the planned five-repeat gate. Exact commands and exclusions are retained. PTY and physical measurements have separate scopes.

## 10 — Run validity and rule versions (50 s)

The stored summaries used the v1 acceptance rules. Final code review tightened monitoring: RAW timestamps must prove full-window power coverage, loaded runs must prove stressor liveness, and MCU mapping needs recent fits. Read-only v2 replay accepts only six idle cyclictest runs and rejects all 45 old PTY runs for missing RAW monitoring times. This is missing evidence, not proof that every run was physically bad. We retain their measured v1 observations with this limitation. E4 original acceptance is unchanged at 17 of 25 planned entries. New experiments must use v2. This distinction prevents a historical result from becoming a stronger claim after cleanup.

## 11 — Timer wake-up under contention (60 s)

Figure 5 compares median per-run P99 values on a logarithmic axis. The measured thread is pinned and memory locked. FIFO has a nine-microsecond idle P99, but memrate on other cores raises it to 239 microseconds. CPU stress produces a much smaller FIFO tail here. Priority therefore helps the observed CPU scheduling tail while shared contention persists. The ordinary-task P50 includes Linux timer slack, so its gap is not pure scheduling latency. These are observations over three 120-second runs per cell, not worst-case bounds. The stressed rows passed v1; v2 requires stressor-liveness records that this acquisition did not retain.

## 12 — Inference baseline (50 s)

Figure 6 reports model-only P99, with preprocessing excluded. Idle inference benefits from two or three threads, but loaded performance changes when workers can run on stressed cores. Four threads reach a loaded P99 of 100.5 milliseconds. The collection is mixed: 21 runs are accepted and three four-thread runs are excluded for live under-voltage. Valid repetition counts are unequal, particularly at four threads. The inference governor and placement differ from the pipeline campaign. Therefore this plot characterizes the workload and its contention sensitivity; it is not a controlled cross-campaign tuning comparison.

## 13 — E1 contention (45 s)

Figure 7 moves to the full software data path. Delivery means input to Pi reception through a pseudo-terminal. Median run P99 is about 48 milliseconds at idle and nearly 14 seconds under memrate. These seconds include input waiting; they do not mean one model call ran for 14 seconds. The logarithmic axis makes the scale difference visible. Memory traffic is associated with sustained pipeline overload in these observations. Establishing a specific memory-bus cause would require controlled counters or isolation. Again, these are measured v1 results with the missing v2 monitoring evidence stated.

## 14 — E2 tuning (45 s)

Figure 8 compares matched pipeline loads under P0 and P1. Memrate delivery P99 remains approximately 13.3 and 12.9 seconds. The cache row does not show a universal improvement either. The profile changes source and bridge priority and memory locking together, at the same affinity; this is not a scheduling-class-only experiment. Those mechanisms do not provide shared-bandwidth isolation. The upstream queue explanation is inferred, rather than established by this profile comparison. We therefore do not claim that the whole tuned profile solves every type of contention. Quotas and the packaged real-time kernel were not compared. The useful result is the limit of priority and placement under this workload, rather than a blanket endorsement of one profile.

## 15 — E3 queue placement (65 s)

Figure 9 shows initialized time-average held-value age, including stalls and the final tail. Idle FIFO and latest are near 95 milliseconds. Under memory load, both bridge policies reach multi-second average age. There were zero bridge replacements. Inference completed about every 122 to 130 milliseconds while inputs were released every 100 milliseconds. Those are measured observations. Accumulation before inference is an inferred explanation consistent with them, not a controlled proof of backlog location or cause. This is the rationale for moving latest-value to the input queue. The later E3b loaded reception P99 is about 254 to 268 milliseconds with input latest, versus roughly 14 to 16 seconds with input FIFO. However, every loaded E3b run is power-invalid. That pattern is flagged diagnostic evidence; a clean input-policy benefit remains unknown.

## 16 — E4 transition reasons (65 s)

Figure 10 uses a local reference selected by the state-event reason. Reason 3 is heartbeat timeout and subtracts the last accepted heartbeat. Reasons 9 and 10 subtract the last accepted inference for source-age HOLD and FAILSAFE. Thus a HOLD about 175 milliseconds after inference is consistent with the 200-millisecond source-age threshold, because the result already had age when received and the estimate adds transit allowance. F5 suppresses inference while keeping heartbeat alive; it reaches HOLD and then FAILSAFE after about 175 and 475 milliseconds from receipt. F1 and F2 instead reach heartbeat FAILSAFE about 100 milliseconds from heartbeat. The plot uses orange squares for heartbeat reason 3, navy triangles for inference HOLD reason 9, and teal circles for inference FAILSAFE reason 10. Horizontal offsets separate nearly coincident runs without changing their measured times. F4 first events split into six heartbeat timeouts and one inference-age HOLD. Its extra runs and F5 use shorter windows, so pooled points do not qualify equal-exposure recovery or reliability.

## 17 — Analyzer cross-check (50 s)

Figure 11 plots delta equal to L minus M. L runs from the last physical UART byte end to both GPIOs low; M runs from accepted heartbeat receipt to the FAILSAFE event timestamp. Positive means L is longer. Ten final frames decode as HEARTBEAT; their residuals are positive 47.5 to 67.6 microseconds. Frame matching makes references comparable, but the endpoints remain distinct. The residual includes reception and output delays, timestamp placement and clock effects. It does not isolate decision-to-output delay or echo accuracy. Five other captures end with inference or echo and give negative residuals of 0.484 to 4.937 milliseconds. Full IDs are in the capture key. Marker-to-safe is 82.9 to 98.7 milliseconds. Sampling is eight megahertz; absolute calibration remains unknown. Matching frames do not qualify the flagged collection or establish actuator safety.

## 18 — Limitations (45 s)

The five-volt, three-ampere supply produced live under-voltage exclusions. All 18 original real-UART E3 runs are flagged; the later 18-run rerun also retains power exclusions. Clean physical AoI remains missing. V2 replay also reveals missing monitoring proof in older software acquisitions. Our small repeat counts and observed maxima cannot prove worst-case response. The final firmware review fixes were compiled, but the changed image was not reflashed and validated on this rig. Analyzer captures add a narrow GPIO timing observation to the older report; they do not validate all transit, oscillator or rearm assumptions. These limits define what we can defend today.

## 19 — Conclusion and contributions (40 s)

The experiment connects four OS lessons. Scheduling affects timer tails while shared contention remains. The measured zero replacements and slow completion intervals support an inferred upstream backlog. The input-latest pattern is flagged; its clean causal benefit remains unknown. Same-domain durations and explicit clock mapping keep freshness measurements meaningful. An independent supervisor distinguishes missing liveness from stale results. The artifact includes a shared protocol, instrumented processes, raw runs, exclusions and reproducible analysis. These are course-project contributions, not a claim of new model architecture, certified safety or formal worst-case guarantees.

## 20 — Future work (30 s)

The immediate task is restoring adequate power and repeating input-policy and physical E3 experiments with v2 evidence. Then flash the reviewed firmware, verify the new image, match analyzer reference events, and calibrate the transit and rearm margins. Longer fault and recovery exposures are needed. Quota and packaged-kernel comparisons are optional later experiments with matched conditions.

## 21 — References (5 s)

The primary documentation and exact evidence paths are listed here and in the artifact. Thank you; the backup slides support questions.
