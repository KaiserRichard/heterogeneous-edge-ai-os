# D: defense deck (presented and submitted to the lecturer)  -> folder submission/defense/
Read submission/briefs/COMMON.md first.
Audience: OS course lecturer (and a senior student). Live talk of 15-20 minutes.
Size: about 20 main slides + about 8 backup slides (after a "Backup" divider) for Q&A.
Story (paper logic, one idea per slide, large readable figures, minimal text):
title -> motivation (why freshness and independent supervision matter on Linux edge AI)
-> problem + research questions -> system architecture (Pi 5 Linux + STM32 FreeRTOS, UART)
-> the OS mechanisms, one slide each: scheduling/contention profiles (P0/P1, cgroups,
affinity, mlock), IPC + buffering policy (FIFO vs latest-value), clocks and freshness
(CLOCK_MONOTONIC, age-at-send, clock sync), independent supervisor (state machine,
heartbeat/result-age HOLD/FAILSAFE, rearm) -> method (rig, runs, validity rules)
-> key measured results (cyclictest idle vs stress, inference baseline, E1-E3, E4 fault
timings with STATE_EVENT reason codes, logic-analyzer cross-check 10/15 within 47-68 us)
each with what it shows and its validity label -> limitations (PSU under-voltage flags,
v2 replay, not worst-case, firmware fixes not re-flashed) -> conclusion + contributions
-> future work (one slide) -> references (one slide).
Speaker notes: write a short talk script per main slide (\note{} or a SPEAKER_NOTES.md)
with target seconds per slide summing to about 17 minutes.
Backup: protocol frame, clock math, thresholds rationale, run validity table, full E4 table,
claim-to-evidence table, tools/branch map.
