# Camera source and freshness-aware pipeline

*English working draft. Camera hardware results are pending; historical values below are explicitly identified by their source and scope.*

## Motivation and scope

The earlier Linux source generated synthetic frame IDs and timestamps. It exercised scheduling and IPC, but contained no pixels and its timestamp did not represent when a scene was exposed. Replacing it with the Raspberry Pi Camera v2 (IMX219) makes source-to-result age meaningful while retaining the project's operating-systems focus: scheduling, queueing, IPC, and freshness. Inference remains a workload; this chapter makes no claim about model accuracy. See the [project scope](../../PROJECT.md), [camera roadmap](../CAMERA_ROADMAP.md), and [CAM1 ticket](../tickets/CAM1_CAMERA_SOURCE.md).

## Design

### Capture and the AoI origin

`hea_cam` uses libcamera's request-completion callback to receive packed camera frames. The backend requests the chosen width, height, and frame rate, reads the `FrameMetadata::sequence` as the frame ID, maps camera buffers, synchronizes DMA-buffer reads, and removes per-row stride padding when copying RGB bytes. The callback records `t_recv_mono_ns` from `CLOCK_MONOTONIC` as its first action. A request's `controls::SensorTimestamp` marks the start of exposure of its first line; CAM1 preserves that timestamp in `t_sensor_ns` and passes it unchanged as `t_input_ns`.

libcamera defines `SensorTimestamp` in the `CLOCK_BOOTTIME` domain. The design treats it as a `CLOCK_MONOTONIC` AoI origin only under the no-suspend assumption, for which the mapping is identity: $t_{sensor}^{mono} \approx t_{sensor}^{boot}$. Startup metadata records a paired `CLOCK_BOOTTIME` / `CLOCK_MONOTONIC` sample. The sensor-origin assumption is falsified if any measured offset

\[
\delta_i = t_{recv,mono,i} - t_{sensor,i}
\]

is non-positive or is not bounded by approximately one frame period plus readout. OS-T1 makes this operational: offsets must be positive and their P99 must be below $T_f+10\,ms$, where $T_f=1/fps$. A single startup pair does not prove that the clock relationship stayed constant. If the check fails, the roadmap's fallback is to use `t_recv_mono_ns` as the AoI origin and report that substitution; CAM1 itself preserves the raw sensor timestamp and its analyzer reports the failed check rather than silently rewriting it. The [camera README](../../linux/camera/README.md) documents the clock assumption and the limits of the startup sample.

### Bounded pixel ring and unchanged input record

Pixels travel through a bounded shared-memory slot ring; the source-to-inference Unix datagram remains the existing 12-byte little-endian `hea_input { frame_id: u32, t_input_ns: u64 }` (`<IQ`). The image is too large to put in that notification: sending only the identifier and timestamp keeps the IPC record byte-compatible and avoids putting image payloads into the socket queue. The inference process opens the named shared-memory object and reads the slot selected by `frame_id % N`.

There is one ring writer. This is a seqlock-style slot protocol: for each write it changes the sequence counter from even to odd, writes the frame ID and pixels, then publishes an even counter. A reader makes one bounded copy and checks the counter again. An odd or changed counter is a `torn` read; a stable slot holding another frame ID is `overwritten`. Both are counted and skipped. This avoids a blocking lock in the producer and prevents inference from using a partially copied or already replaced image. Four slots are the default; the ring is bounded, not lossless. The camera README describes its ABI, atomic access, limits, and lifetime.

Freshness is also a policy at the input queue. With `--input-policy latest`, inference drains pending 12-byte notifications before each inference and uses the newest valid notification. If inference is slower than capture, queued older frames are superseded and logged as `skipped_stale`; a ring slot can also be overwritten before it is copied. The bridge has its own selectable latest-value policy for unsent inference results. Together these policies bound stale backlog by dropping work, at the cost of completeness. They do not make inference faster or guarantee a delivery deadline. The inference implementation and options are in [`infer_server.py`](../../linux/inference/infer_server.py).

### One-frame path

```mermaid
sequenceDiagram
    participant S as IMX219 / libcamera
    participant C as hea_cam callback
    participant R as Shared-memory ring
    participant I as infer_server
    participant B as hea_bridge
    participant M as STM32 FreeRTOS supervisor
    S->>C: Completed request: sequence, SensorTimestamp, RGB buffer
    C->>C: Sample t_recv_mono_ns; copy packed RGB; retain t_sensor_ns as t_input_ns
    C->>R: Publish frame_id and pixels (odd → data → even)
    C->>I: 12-byte hea_input(frame_id, t_input_ns)
    I->>I: Select latest valid notification; verify and preprocess ring slot
    I->>B: Inference result datagram (frame_id, t_input, t_done, class, confidence)
    B->>M: UART-framed result and heartbeat
    M->>M: Validate reception; track heartbeat and result freshness; update FRESH / HOLD / FAILSAFE
```

The diagram describes the intended complete path. The camera-mode inference timestamps use `CLOCK_MONOTONIC`, while the existing bridge's age validation and clock synchronization use `CLOCK_MONOTONIC_RAW`. The 12-byte input record is unchanged, but that does not make these clock domains interchangeable. The camera branch must resolve this boundary before its data can support end-to-end AoI claims through the current bridge and supervisor. See the integration limitation in the [camera README](../../linux/camera/README.md).

### Age of Information and a worked sawtooth cycle

Let $g_i$ be the frame's exposure timestamp mapped to the consumer's clock domain, and $r_i$ its successful result-reception time. If $u(t)$ is the generation time of the newest result available at time $t$, Age of Information is

\[
\Delta(t)=t-u(t), \qquad
\bar{\Delta}(H)=\frac{1}{H}\int_0^H \Delta(t)\,dt.
\]

Immediately after reception $i$, the age is $\Delta_i=r_i-g_i$. Until the next reception, age rises linearly. For an interarrival interval $Y_i=r_i-r_{i-1}$, the area under that part of the sawtooth is

\[
A_i=\Delta_{i-1}Y_i+\frac{Y_i^2}{2}, \qquad
\bar{\Delta}_i=\frac{A_i}{Y_i}=\Delta_{i-1}+\frac{Y_i}{2}.
\]

As a worked arithmetic example—not camera evidence—take the first two inference receptions in the retained software/pty run [`E3_P1_B2_memrate_c23_fifo_r1/pipeline/rx.csv`](../../results/2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx/E3_P1_B2_memrate_c23_fifo_r1/pipeline/rx.csv). Its timestamps give $g_0=2{,}996{,}803{,}181{,}824\,ns$, $r_0=2{,}996{,}965{,}095{,}880\,ns$, $g_1=2{,}996{,}903{,}236{,}621\,ns$, and $r_1=2{,}997{,}105{,}784{,}491\,ns$. Thus $\Delta_0=161.914056\,ms$, $Y_1=140.688611\,ms$, and

\[
A_1=(161.914056)(140.688611)+\frac{(140.688611)^2}{2}
   =32{,}676.106273\,ms^2,
\qquad \bar{\Delta}_1=232.258362\,ms.
\]

The age just before the second update is $302.602667\,ms$, after which the newer result resets it to $202.547870\,ms$. This is one interarrival interval from an earlier synthetic-input run, not a camera measurement or a whole-run average. A campaign time-average must sum the areas over its initialized measurement window and divide by that window's duration.

## Test scenarios

Every run is valid only when `vcgencmd get_throttled` is `0x0` before and after, the governor is `performance`, the SSH session is idle, and metadata is saved. Subtract timestamps only within Pi `CLOCK_MONOTONIC` or within the MCU timer; cross-clock results require the synchronization line and must be labelled. The default is three 5-minute repetitions per configuration unless the scenario specifies another exposure. The full source table is [TEST_SCENARIOS.md](../TEST_SCENARIOS.md).

| ID | Setup and procedure | Metrics and pass criterion |
|---|---|---|
| OS-T1 | Pi 5 + Pi Camera v2, no load; 640×480 at 30 fps and 10 fps, 5 min each; save sensor/receive timestamps and startup BOOTTIME/MONOTONIC pair. | Mean frame interval within 1% of nominal; P99 absolute interval jitter < 2 ms; capture drops < 0.1%; `t_recv−t_sensor` positive and P99 < $T_f+10\,ms$; BOOTTIME−MONOTONIC difference stable. A start-only pair cannot establish constancy; record another pair near the end or leave that criterion unresolved. |
| OS-T2 | P0 stock profile, MobileNetV2 ONNX, camera at 10 fps; 1,000 warm-ups then 5,000 timed inferences at each of 1, 2, and 4 threads; record throttle state and SoC temperature. | Throttle `0x0` before/after; inference P50/P95/P99 and maximum temperature; chosen thread setting has P99/P50 < 1.5. |
| OS-T3 | Compare P0 with P1 (`SCHED_FIFO`, CPU pinning, cgroup `cpu.max`, `mlockall`) under CPU, VM, cache, and I/O stressors. | Camera-to-result P50/P99, deadline-miss fraction (deadline = frame period), and cyclictest maximum; P1 P99 no worse than P0 for each stressor and P1 miss fraction ≤ 1%. Report any reversal. |
| OS-T4 | Camera at 30 fps with inference slower than the period; compare input/bridge FIFO, input/bridge latest-value, and mixed policies, three runs each. | Time-average and peak AoI, deadline misses, queue length; latest-value time-average AoI must be lower than FIFO in every run. FIFO queue growth is observed; otherwise the hypothesis fails. |
| OS-T5 | Pi UART ↔ Nucleo OS firmware; send 10,000 valid frames, inject CRC-corrupt, truncated, and wrong-version frames, and measure echo RTT. | All valid accepted, zero invalid accepted, RTT P99 < 5 ms. Runs at 921600 baud (OS firmware); the scenario table's earlier 115200 was corrected on 2026-10-30. |
| OS-T6 | Full camera pipeline and OS firmware; inject bridge kill, inference `SIGSTOP`, FIFO CPU hog, and stale results with a live heartbeat; 10 trials per fault, then rearm. Observe D4 FRESH, D5 HOLD, D6 FAILSAFE, D9 link activity with a logic analyzer. | Every trial reaches the expected state; reaction ≤ timer budget + one tick; FAILSAFE stays latched until rearm; no false FAILSAFE in a 30-minute healthy run. |
| OS-T7 (extra) | FW3 MPU6050 task at 200 Hz while UART is idle, saturated with valid frames, and sent corrupted-frame bursts. | MCU-timer period jitter P99 < 100 μs, zero missed samples, and OS-T6 reaction unchanged. |
| OS-T8 (extra) | FW4 sends supervisor state on change and every 100 ms over CAN1; CAN2 receives on the same board; repeat OS-T6 faults. The Pi–MCU bridge remains UART. | Every state change received; state-to-CAN2 latency P99 < 1 ms; TEC/REC remain zero. |

OS-T8 is the roadmap-approved extra: CAN is an MCU state output only and does not replace or join the UART bridge.

## Results and evidence status

| Item | Status and evidence | What it supports |
|---|---|---|
| OS-T1 camera timing and AoI-origin check | **PENDING — not run on the physical Pi camera.** The analyzer and fake backend exist; the real backend's Pi build and OS-T1 capture are still listed as conductor checks. | No measured camera FPS, jitter, loss rate, or sensor-to-receive offset is claimed. |
| OS-T2 camera inference baseline | **PENDING — not run on camera frames.** | No camera-based inference latency or temperature result is claimed. |
| Camera-source OS-T3 / OS-T4 | **PENDING.** Historical E1–E3/E3b used the synthetic source or software/pty path. | No camera-based contention or FIFO/latest-value comparison is claimed. |
| Earlier fixed-image inference baseline | MEASURED under its earlier setup: idle P50/P99 were 44.0/48.0 ms (1 thread), 31.1/42.9 ms (2), 29.4/38.5 ms (3), and 31.4/70.7 ms (4; one valid repeat). | Context for OS-T2 only. These fixed-image samples used different exposure/settings and are not OS-T2 camera results. Source: [`STAGE_REPORT.md`](../STAGE_REPORT.md#inference-workload-alone) and [`results/2026-10-11_inference_baseline/SUMMARY.md`](../../results/2026-10-11_inference_baseline/SUMMARY.md). |
| Earlier input latest-value study (E3b) | MEASURED raw software/pty timestamps, but all loaded rows were **INVALID / FLAGGED** by live under-voltage/power flags. FIFO input age P50 ranged 6,527.4–8,676.0 ms and P99 13,821.6–15,891.0 ms; input-latest P50 was 189.3–190.7 ms and P99 254.0–267.9 ms, with 171–173 stale inputs skipped. | Diagnostic support for placing latest-value selection before inference. It is not clean causal evidence and does not test the camera ring. Sources: [`STAGE_REPORT.md`](../STAGE_REPORT.md#e3b-input-latest-value-fix-still-power-flagged), [`E3B_per_run.csv`](../../results/2026-10-12_e3b_input_latest/20261012T091415Z_e3b/summary/E3B_per_run.csv), and the retained per-run `rx.csv` / validity records. |

The roadmap's 29 October inventory recorded that the Pi camera was not connected, `imx219` was absent from `dmesg`, and libcamera/rpicam applications were not installed. It also identifies that Pi as the 4 GB board, whereas the older inference results used the 8 GB board. These are historical inventory facts; recheck them when the bench run begins. No result from the synthetic backend should be relabelled as camera evidence.

### Switching the bench between OS and WBR firmware

Follow [RUNBOOK_BENCH.md](../RUNBOOK_BENCH.md): the owner confirms an OS firmware switch, uses the staged `nucleo_switch.py` process and the runbook's BOOT0/RESET steps, and returns BOOT0 to GND and resets after the write. The runbook requires an archived backup, image hash, and read-back verification. To return to WBR, use the same process with `wbr-agv_f446_home_canfix01.bin` and its recorded hash. The OS supervisor link is 921600 baud; WBR uses 115200 baud. The runbook reports the expected INIT/all-off state, then green D4 when the bridge runs. No additional flashing procedure is specified here.

## Limitations

- Physical Pi camera capture, libcamera compilation against the Pi installation, negotiated frame timing, sensor-color correctness, DMA coherency, and Pi scheduling overhead remain unverified until OS-T1 on hardware. Capture-buffer sequence gaps may not expose every loss inside a camera pipeline.
- The no-suspend clock assumption and positive/bounded offset check are necessary for the sensor origin but do not prove long-run clock equivalence. If the check fails, report the receive-time fallback; do not present sensor-origin AoI as valid.
- `hea_cam` copies pixels and writes CSV in the completion callback; those costs are part of source overhead. The ring can overwrite frames and readers deliberately skip torn or stale slots.
- Camera mode and the current bridge use different Linux clock domains (`CLOCK_MONOTONIC` versus `CLOCK_MONOTONIC_RAW`). Resolve that interface before using bridge or MCU age as camera AoI.
- Earlier synthetic-input, pty, and invalid power-flagged data cannot establish camera performance, clean loaded-policy benefit, electrical reliability, or a worst-case deadline.
