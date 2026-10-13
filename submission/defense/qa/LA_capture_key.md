# Analyzer plot capture key

Figure 11 plots Δ = analyzer UART-byte-end → both GPIOs low interval minus MCU accepted-heartbeat receipt → FAILSAFE STATE_EVENT interval. Positive means the analyzer interval is longer. Capture indices restart in each panel; no matching-frame classification qualifies collection validity. Collection: FLAGGED.

| Panel / index | Capture | Last CRC-valid frame | Δ (µs) |
|---|---|---|---:|
| Matched / 1 | results/2026-10-12_logic_analyzer/check_F2/F2-r01 | HEARTBEAT | +67.024 |
| Matched / 2 | results/2026-10-12_logic_analyzer/run_F1/F1-r01 | HEARTBEAT | +47.524 |
| Matched / 3 | results/2026-10-12_logic_analyzer/run_F1/F1-r02 | HEARTBEAT | +67.524 |
| Matched / 4 | results/2026-10-12_logic_analyzer/run_F1/F1-r04 | HEARTBEAT | +61.899 |
| Matched / 5 | results/2026-10-12_logic_analyzer/run_F2/F2-r01 | HEARTBEAT | +47.899 |
| Matched / 6 | results/2026-10-12_logic_analyzer/run_F2/F2-r05 | HEARTBEAT | +67.274 |
| Matched / 7 | results/2026-10-12_logic_analyzer/run_F4/F4-r02 | HEARTBEAT | +67.649 |
| Matched / 8 | results/2026-10-12_logic_analyzer/run_F4/F4-r03 | HEARTBEAT | +65.649 |
| Matched / 9 | results/2026-10-12_logic_analyzer/run_F4/F4-r04 | HEARTBEAT | +67.149 |
| Matched / 10 | results/2026-10-12_logic_analyzer/run_F4/F4-r05 | HEARTBEAT | +61.649 |
| Different / 1 | results/2026-10-12_logic_analyzer/run_F1/F1-r03 | INFERENCE | -2922.601 |
| Different / 2 | results/2026-10-12_logic_analyzer/run_F2/F2-r02 | ECHO_REQ | -4937.226 |
| Different / 3 | results/2026-10-12_logic_analyzer/run_F2/F2-r03 | INFERENCE | -484.101 |
| Different / 4 | results/2026-10-12_logic_analyzer/run_F2/F2-r04 | INFERENCE | -2939.601 |
| Different / 5 | results/2026-10-12_logic_analyzer/run_F4/F4-r01 | INFERENCE | -3053.101 |
