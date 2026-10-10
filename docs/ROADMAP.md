# Roadmap: OS project → WBRobot → article

Updated 2026-10-10. This replaces the earlier proposed calendar with completion
gates. Dates depend on restored Pi access and hardware availability.

Read [the full roadmap](ROADMAP_TO_WBROBOT_AND_ARTICLE.md) for tasks, acceptance
criteria, hardware sessions and the publication evidence plan. Read
[CONDUCTOR_STATE.md](CONDUCTOR_STATE.md) for the current verified state.

| Stage | What we finish | What it establishes | Hardware |
|---|---|---|---|
| A — current | Linux pipeline, virtual MCU, profiles and repeatable Pi experiments | Software correctness and Linux-side timing/freshness measurements | Mac + dedicated OS Pi |
| B | F446RE firmware, direct UART, clock validation and safe-output pin | External MCU operation independent of Linux | Add Nucleo, USB, jumpers and timing instrument |
| C | Physical E1–E4 campaign and OS report | Measured end-to-end freshness and fault response on the OS rig | Pi + Nucleo rig |
| D | WBR interface review, target-MCU port and shadow-mode logging | Compatibility with WBR's actual workload and control boundary | Separate approved WBR setup |
| E | Gated WBR use and controlled fault trials | Defined fallback behavior within tested conditions | WBRobot, operator and test fixture |
| F | Related-work gap, reproducible evidence, paper and submission | An article supported by completed experiments | No new hardware unless an evidence gap remains |

Stages D/E are proposed future work, not permission to access the WBR Pi. Stage A
needs no STM32 and cannot establish hardware failsafe latency or robot safety.
A standalone OS article can use Stage C evidence after a novelty review; an article
claiming WBR integration needs D/E evidence.

## Resume point

KNOWN: supervisor Step 1 and protocol v2 are merged. Stage A is incomplete.

Next: restore access to richard@192.168.50.2; finish clock-sync ticket T3; add
rearm generation/session handling and source-age supervision; then implement and
measure the Linux pipeline. Inspect interrupted workers and worktrees before resuming.
