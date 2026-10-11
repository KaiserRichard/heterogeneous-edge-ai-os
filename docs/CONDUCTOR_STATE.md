# Conductor state

Updated 2026-10-10. Evidence snapshot; Stage A is incomplete.

## Intent and communication

- KNOWN: current request is a roadmap to WBRobot and an academic article. This is
  a documentation task; it does not resume experiments or interrupted code workers.
- KNOWN: always reply in English regardless of the user's prompt language.
- KNOWN: broader authorization is the latest Stage A user instruction. Its
  CLOCK_MONOTONIC, five-repeat and experiments/runs rules supersede older briefs
  naming RAW, three repeats or results/.
- KNOWN: implementation head verified remotely: a22fa2b on
  claude/project-thread-eq9yql; main is not the merge target.

## Access and isolation

- KNOWN (last recorded connection): dedicated OS Pi richard@192.168.50.2, hostname
  os, direct Ethernet. Not rechecked after the user's disconnection; old os@osedge
  examples are not current access details.
- KNOWN: Mac repo /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os.
- KNOWN: primary Mac checkout has user prompt deletions and unresolved
  prompts/README.md conflict. Preserve these; use separate feature worktrees.
- KNOWN: no WBR Pi access/changes during Stage A. WBR stages are proposed later work.

## Verified state

| Label | Item | State |
|---|---|---|
| KNOWN | Supervisor Step 1 | 98fe2ee; merged in cf2295b; receipt silence only |
| HOST-TEST | Noise determinism | bba23d0; both Mac/Pi char modes: 20,000/20,000, zero false accepts |
| KNOWN | age_at_send protocol v2 | 2a06589; merge a22fa2b; v1 retained; source-age policy pending |
| HOST-TEST | Merged implementation CI | [a22fa2b green](https://github.com/KaiserRichard/heterogeneous-edge-ai-os/actions/runs/37747548984) |
| KNOWN | T3 interruption | feat/clock-sync at a22fa2b; only untracked docs/tickets/T3_CLOCK_SYNC.md at inspection; no completed math code |
| UNKNOWN | Performance campaign | No accepted baseline or full E1/E2/E3 software campaign recorded |
| UNKNOWN | Hardware/robot | MCU firmware, physical link/fault timing and WBR behavior unverified |

## Next tickets

1. Recheck access/source/workers and resume T3: offset/delay/filter/drift, uint32-us wrap.
2. Add rearm generation and stale-generation rejection/counters. Firmware must
   invalidate queued pre-rearm events or tag them with the generation, including
   same-tick events. Timestamp filtering alone is insufficient; this remains open.
3. HEARTBEAT session_id/restart semantics and compatible sequence-reset tests.
4. Source-age Step 2 using Pi duration, local receipt elapsed and PROVISIONAL
   transit allowance; handle legacy absence, saturation and clock-rate uncertainty.
5. Source/inference/logger, bridge/virtual MCU, P0/P1/P2, runner/analysis, repeated
   valid Pi measurements, threshold note and LEARNING_NOTES/Stage A report.

All results land in experiments/runs/<timestamp>_<name>/ with source/config/raw data.

## Gates and prerequisites

- KNOWN (last sudo audit): noninteractive sudo allowed exact apt commands for
  stress-ng/rt-tests/socat, not all authorized measurement/governor commands.
  Recheck; stop for a needed credential rather than claiming access.
- UNKNOWN: current reachability, power/cooling and temperature/throttle state.
- Gated: P3/boot/serial-console changes, physical action, credentials, outside-repo
  work and repeated failure after root-cause analysis.
- Open: WBR interface/fallback review and article novelty/venue assessment.

Next milestone: reproducible Stage A software and measurements. STM32 first needed
at Stage B USB flashing. Full plan:
[ROADMAP_TO_WBROBOT_AND_ARTICLE.md](ROADMAP_TO_WBROBOT_AND_ARTICLE.md).
