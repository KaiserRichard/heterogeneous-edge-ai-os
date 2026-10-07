# Handoff prompt for ChatGPT (paste as the first message)

Written 2026-10-07 by Claude. Paste everything between the lines into ChatGPT, then attach or
paste the files listed under "Read first" if ChatGPT cannot open the repository.

---

You are taking over as my main assistant for our university Operating Systems course project.
Another assistant (Claude) worked on it with me from 2026-10-06 to 2026-10-07; this message
brings you up to date. Reply in English unless I ask for Vietnamese. I am a 4th-year
Electronics and Telecommunications student (embedded, STM32, C/C++, Linux); skip beginner
explanations, explain mechanisms, and mark claims as KNOWN / SOURCE / CALCULATED / ASSUMED /
UNKNOWN. Never present a number as measured unless we measured it.

## Team and course
- Team "3 Stars": Nguyễn Quốc Khánh 20233464 (team lead), Nguyễn Trung Hiếu 20233398,
  Nguyễn Quang Vinh 20233718.
- Supervisor (GVHD): TS. Nguyễn Quang Minh. Tutorial class code: 173876.
- Note: PROJECT.md still says "two-person project"; the team is three people.

## Repository
- GitHub: KaiserRichard, repo `heterogeneous-edge-ai-os`, working branch
  `claude/project-thread-eq9yql` (not merged to main yet).
- Local path: `~/Desktop/OS/OS-project/heterogeneous-edge-ai-os` (macOS host).
- Rules in `AGENTS.md`: no ROS 2, no Docker, no Yocto/Buildroot, no kernel patching (the packaged
  Real-time Ubuntu 24.04 kernel is allowed only as profile P3), no hypervisors, UART only (no
  SPI/CAN/Ethernet bridge), no ML on the STM32, do not edit `third_party/`.

## Read first (in this order)
1. `PROJECT.md` – objectives, scope, non-goals.
2. `docs/SYSTEM_GUIDE.md` – plain-language system guide, work items, glossary (most up to date).
3. `docs/SYSTEM_OVERVIEW.md`, `docs/ROADMAP.md`, `docs/ENVIRONMENT_AND_HARDWARE.md`.
4. `docs/research/RELATED_WORK.md`, `R1.md`–`R8.md`, `DESIGN_CHANGES.md` – cited research notes.
5. `docs/SLIDES_OVERVIEW.md` – slide content (English source of the deck).

## The system in one paragraph
Raspberry Pi 5 (Ubuntu 24.04) runs a source (input every 100 ms, DESIGN), MobileNetV2 inference
on ONNX Runtime (20–50 ms, PUBLISHED for other setups), and a bridge that sends results over UART
(Pi GPIO14/15 ↔ STM32 PA10/PA9, GPIO17 → PA0 timer capture for clock validation) to an STM32
Nucleo-F446RE running FreeRTOS. The STM32 supervisor (1 kHz, highest app priority) keeps two
timers – heartbeat liveness and result freshness – with states INIT → FRESH → HOLD → FAILSAFE;
FAILSAFE is latched until explicit rearm. This is a System-Level Simplex pattern (Bak et al.,
RTAS 2009). Frame: SOF A5 5A | ver | type | seq | len | payload ≤64 B | CRC-16. Clock sync: NTP-style
T1–T4 exchange plus GPIO edge as ground truth. Runtime profiles: P0 stock, P1 tuned (SCHED_FIFO 50,
CPU pinning, cgroups, mlockall), P2 = P1 + latest-value buffer, P3 = P1 on PREEMPT_RT kernel.
Experiments E1 contention, E2 tuning/kernel, E3 freshness (Age of Information), E4 fault injection
(failsafe latency on a logic analyzer). Hypotheses H1–H4 in `docs/SLIDES_OVERVIEW.md` §17.

## Current status (2026-10-07)
- Done: design, research pass (8 notes), protocol library + host tests, supervisor skeleton
  (one timer, 113 assertions, on branch `feat/software-skeleton-wip`), CI, Pi provisioning scripts.
- Not done: supervisor v2 (two timers + latched FAILSAFE), clock-sync math, rig setup, FreeRTOS
  firmware, bridge daemon, experiments E1–E4. No hardware measurement exists yet.
- Slides: `slides/main.tex` (Beamer, XeLaTeX, moloch theme). Build: `cd slides && latexmk -xelatex
  main.tex && open main.pdf`. Being rewritten into Vietnamese (25 main + 4 appendix frames, larger
  font, table of contents, sections, abbreviations expanded on first use, team info on the title).
  If that rewrite is not committed yet, the last committed English version is `e604b20`.
- Images: `slides/images/V01.png`–`V24.png` (user-generated, mapped in `slides/images/MAPPING.md`).
  Only V04 is worth regenerating (its MCU board is drawn green). Prompts for regeneration:
  `slides/image-prompts/PART_A.md` (V01–V12) and `PART_B.md` (V13–V24); one prompt per message,
  never "continue".
- References (verified against DBLP/arXiv): Bak et al. RTAS 2009; Kaul, Yates, Gruteser INFOCOM 2012
  and CISS 2012; Yun et al. MemGuard RTAS 2013; Bechtel et al. DeepPicar RTCSA 2018;
  Giacomossi et al. arXiv:2604.19275 (Pi 5 PREEMPT_RT; SCHED_FIFO 99 max 1.8 ms stock vs 0.22 ms RT,
  stressed – their result, not ours).

## Next steps (suggested order)
1. Review the Vietnamese deck; fill any gaps; regenerate V04 if wanted.
2. Supervisor v2 in pure C with host tests (heartbeat lost, stale-but-alive, duplicates, CRC errors,
   rearm).
3. Clock-sync math (offset/delay from T1–T4, drift fit, min-delay filter) with synthetic-clock tests.
4. Pi bootstrap + cyclictest + inference latency baseline → sets source period and HOLD/FAILSAFE
   thresholds.
5. Flash Nucleo, UART link, then E1–E4.
Work items with acceptance tests: `docs/SYSTEM_GUIDE.md` (work-item table).

## How to work with me
- Codex (OpenAI CLI) does implementation in the repo; you plan, review and write bounded tasks for it.
- Give commands with: COMMAND / PURPOSE / EXPECTED / DECISION.
- Challenge my assumptions; do not declare PASS without evidence.

First, confirm you understood, list what you still need from me (files you cannot see), and
suggest the next concrete task.

---
