# Retained experiment results

Start with [the stage report](../docs/STAGE_REPORT.md) for interpretations and
acceptance rules. Every original file is retained byte-for-byte, including failed
runs, raw captures, logs, and older generated summaries. Folder dates are acquisition
dates: the October 11 Pi-only collections have October 8 timestamps inside them
because the Pi wall clock was about three days behind. Inner names and recorded
absolute paths remain unchanged as provenance.

VALID means accepted within the stated measurement scope. FLAGGED marks mixed,
excluded, incomplete, or unqualified collections; use only the accepted subset
where specified. It does not mean that every observation in a folder is unusable.
Counts describe runs/attempts, not individual CSV samples. No new acceptance
criteria or measurements were introduced during repository cleanup.

| Folder | What it contains | Run counts | Validity status and scope | Summary to read |
|---|---|---|---|---|
| [2026-10-11_cyclictest](2026-10-11_cyclictest/) | P0 SCHED_OTHER / P1 FIFO timer wake-up campaigns across five loads | 30 runs; 3 per profile/load cell | VALID: 30/30, measured thread policy and live/new sticky power checks passed | [SUMMARY.md](2026-10-11_cyclictest/SUMMARY.md) |
| [2026-10-11_inference_pre_livepower](2026-10-11_inference_pre_livepower/) | Initial inference sweep using before/after power metadata | 24 runs; 8 cells × 3 repeats | FLAGGED: 22/24 excluded by the original sticky-bit rule; no continuous live-power log. Superseded by the next collection; not reclassified | Per-run `threads-N/validity.json` and `bench/summary.json`, e.g. [idle_r1/threads-1](2026-10-11_inference_pre_livepower/idle_r1/threads-1/bench/summary.json) |
| [2026-10-11_inference_baseline](2026-10-11_inference_baseline/) | MobileNetV2 inference sweep with continuous power sampling | 24 runs; 21 accepted, 3 excluded | FLAGGED: mixed collection; accepted subset VALID under live-bit checks, three 4-thread runs excluded for live under-voltage | [SUMMARY.md](2026-10-11_inference_baseline/SUMMARY.md) |
| [2026-10-11_e1_e2_e3_pty](2026-10-11_e1_e2_e3_pty/) | Contention, scheduling and bridge-policy software campaigns | E1 15, E2 18, E3 12; total 45, 3 per cell | VALID: 45/45 for software/PTY only; no physical UART/MCU claim | [summary/README.md](2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx/summary/README.md) and [per_run.csv](2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx/summary/per_run.csv) |
| [2026-10-12_e3b_input_latest](2026-10-12_e3b_input_latest/) | FIFO vs latest input policy before inference, PTY | 12 runs; 3 accepted, 9 excluded | FLAGGED: all six loaded runs plus three idle runs fail live power/throttle checks; loaded observations are diagnostic | [E3B_per_run.csv](2026-10-12_e3b_input_latest/20261012T091415Z_e3b/summary/E3B_per_run.csv) and [report](../docs/STAGE_REPORT.md#freshness-the-queue-was-in-the-wrong-place) |
| [2026-10-12_e4_faults](2026-10-12_e4_faults/) | Original physical fault campaign | 25 planned entries: 20 performed, 5 F5 unperformed; 17 accepted | FLAGGED: F1–F3 each 5/5 VALID; F4 2/5 accepted (power/clock-fit exclusions). Unperformed F5 retained | [e4_runs.csv](2026-10-12_e4_faults/20261012T093526Z_e4/e4_runs.csv); [report](../docs/STAGE_REPORT.md#physical-faults-state-timing-not-output-timing) supersedes older local references in `e4_faults.csv` |
| [2026-10-12_f4_extra](2026-10-12_f4_extra/) | Two extra FIFO-99 hog batches | 9 attempts (6 + 3); 5 accepted | FLAGGED: 3 startup failures, 1 RMS >200 µs; 5 VALID for short-window transitions only, not original recovery/exposure gates | [Extra F4 report table](../docs/STAGE_REPORT.md#extra-f4-attempts--round-14), per-attempt `run.json` |
| [2026-10-12_f5_stale](2026-10-12_f5_stale/) | SIGUSR1 suppresses inference while heartbeat stays alive | 5 runs; 5 accepted | VALID for short-window stale-result transitions; no long-window recovery qualification | [F5 report table](../docs/STAGE_REPORT.md#physical-faults-state-timing-not-output-timing), per-repeat `F5-r01/run.json` |
| [2026-10-12_e3_real_uart](2026-10-12_e3_real_uart/) | Input/bridge policy combinations with STM32 reception | 18 runs; 3 per six cells; 0 accepted | FLAGGED: 16 live-power flags, 9 loaded clock-fit failures, 14 missing transition records (overlapping reasons). Empty-event rejection has a documented limitation | [summary/README.md](2026-10-12_e3_real_uart/20261012T105039Z_e3real/summary/README.md), [per_run.csv](2026-10-12_e3_real_uart/20261012T105039Z_e3real/summary/per_run.csv) and [report](../docs/STAGE_REPORT.md#e3-real-uart--stm32--round-14-all-flagged) |
| [2026-10-12_logic_analyzer](2026-10-12_logic_analyzer/) | FX2 fault captures, F2 preflight, channel checks and generated comparisons | 16 fault attempts (F1/F2/F4 5 each + 1 F2 check); 15 fault captures, plus channel check | FLAGGED: F1-r05 incomplete; generated tables retain `UNVERIFIED ON HARDWARE` labels and differing MCU/analyzer reference events. No collection-wide validity promotion | [run_F1/la_e4.csv](2026-10-12_logic_analyzer/run_F1/la_e4.csv), [run_F2/la_e4.csv](2026-10-12_logic_analyzer/run_F2/la_e4.csv), [run_F4/la_e4.csv](2026-10-12_logic_analyzer/run_F4/la_e4.csv), [check_F2/la_e4.csv](2026-10-12_logic_analyzer/check_F2/la_e4.csv) |
| [2026-10-12_hw_bringup](2026-10-12_hw_bringup/) | Clock, firmware, UART IRQ/DMA and per-inference RX smoke diagnostics | 7 smoke directories; 7 excluded by retained summaries | FLAGGED: before/after throttling/history bits; retain link diagnostics, not clean timing claims. Report discusses the first six; smoke7 is also retained | Per-run `summary.json`, e.g. [hw_smoke6_dma](2026-10-12_hw_bringup/hw_smoke6_dma/summary.json), [hw_smoke7_infrx](2026-10-12_hw_bringup/hw_smoke7_infrx/summary.json) |

The report predates the retained logic-analyzer collection; its pending analyzer
checks are historical limits of those reported measurements, not a claim that
this repository contains no captures. Read analyzer comparisons with
[tools/la/README.md](../tools/la/README.md).

## Validity rule versions (read before re-running any summary)

The summaries stored in these folders were produced with the validity rules in force when each run was recorded (rule set v1). The final code review (docs/STAGE_REPORT.md, "Validity rule versions") tightened the rules (v2): monitor samples must carry RAW timestamps, cover the whole measurement window with gaps of at most 1.5 s, stressors must be shown alive during measurement, and clock fits older than 5 s may not map MCU time.

Re-running the v2 analysis on the stored data (read-only replay, 2026-10-13):

| Data set | v1 (stored) | v2 replay | Why |
|---|---|---|---|
| E1/E2/E3 over pty | 45/45 valid | 0/45 | v1 monitor files have no RAW `t_pi_ns` timestamps, so window coverage cannot be proven. Not evidence of a bad run. |
| cyclictest P0, P1 | 15/15 each | 3/15 each | Stressed runs did not record stressor liveness; the 3 idle runs per profile stay valid. |
| E4 faults | 17/25 | 17/25 | Unchanged. Detection values now follow the transition reason code (result-age HOLD ~175 ms vs heartbeat FAILSAFE ~100 ms), as already reported. |
| Logic analyzer | 15 captures | unchanged | No number or flag changed. |

So the v1 numbers are reported as measured, with the stated limitation that the stricter v2 evidence was not recorded for them. Any rerun uses v2.
