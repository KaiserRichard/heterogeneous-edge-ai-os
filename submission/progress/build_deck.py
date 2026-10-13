from pathlib import Path
import json
import re
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
# Reuse the reference family's preamble, without its project-specific helpers.
preamble=(HERE/'reference-preamble.tex').read_text()
preamble+=r'''
\setbeamertemplate{navigation symbols}{}
\setbeamersize{text margin left=6mm,text margin right=6mm}
\setbeamertemplate{footline}{\hfill\color{muted}\small\insertframenumber/\inserttotalframenumber\hspace{6mm}\vspace{2mm}}
\linespread{1.10}
\newcommand{\src}[1]{\par\vfill{\small\color{muted}Source: #1}}
\newcommand{\takeaway}[1]{\par\medskip\begin{beamercolorbox}[sep=2mm,wd=\linewidth]{block body}\color{navy}\textbf{#1}\end{beamercolorbox}}
\begin{document}
'''
slides=[]
def esc(s):
    return s.replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('_',r'\_').replace('#',r'\#').replace('%',r'\%').replace('$',r'\$').replace('→',r'$\rightarrow$').replace('←',r'$\leftarrow$').replace('--','-{}-')
def add(title,items,take,source):
    body='\\begin{itemize}\n'+''.join('\\item '+esc(i)+'\n' for i in items)+'\\end{itemize}\n'
    slides.append((title,body+r'\takeaway{'+esc(take)+'}'+r'\src{'+esc(source)+'}'))
def raw(title,body): slides.append((title,body))
add('Owner checkpoint | 13 October 2026',[
'The Linux workload, UART protocol and FreeRTOS supervisor are implemented; inference is an OS workload.',
'Retained evidence covers Pi software timing, physical MCU transitions and analyzer captures, with explicit exclusions.',
'Immediate work: document the rig, verify the review fixes, restore clean power, then rerun under v2 rules.'
], 'The code is ahead of the clean physical evidence.', 'P_PROGRESS.md; results/README.md; docs/STAGE_REPORT.md')
raw('System map | execution and ownership',r'''
\centering
\begin{tikzpicture}[x=1cm,y=1cm,>=Stealth,box/.style={draw=navy,fill=white,rounded corners,align=center,text width=3.2cm,minimum height=1cm,font=\normalsize}]
\node[box] (s) at (0,0) {Pi source\\input timestamp};
\node[box] (i) at (6,0) {Pi inference\\ONNX / synthetic};
\node[box] (b) at (12,0) {Pi bridge\\heartbeat + echo};
\node[box] (m) at (12,-2.7) {STM32 UART RX\\DMA + parser};
\node[box] (u) at (6,-2.7) {FreeRTOS supervisor\\liveness + freshness};
\node[box] (g) at (0,-2.7) {State GPIO outputs\\FRESH / HOLD / FAILSAFE};
\draw[->,thick,navy] (s)--node[above,font=\small,align=center]{Unix\\datagram}(i);
\draw[->,thick,navy] (i)--node[above,font=\small,align=center]{Unix\\datagram}(b);
\draw[<->,thick,teal] (b)--node[right,font=\small,align=left]{UART\\+ status}(m);
\draw[->,thick,navy] (m)--node[above,font=\small,align=center]{RTOS\\handoff}(u);
\draw[->,thick,navy] (u)--(g);
\end{tikzpicture}
\par\medskip{\small\color{muted}Figure 1: data flows to the supervisor; echo/status return to the Pi.}
\par\medskip Figure 1 locates the decision on the MCU. Mac: builds, ST-LINK and analyzer; Pi: Linux processes and stressors. PTY runs replace the physical UART/MCU path.
\takeaway{An alive bridge and a fresh inference result are separate conditions.}
\src{docs/STAGE\_REPORT.md, What was built; linux/README.md; stm32/firmware/README.md}
''')
add('Timeline | foundations, 5–10 October',[
'5 October: project scope, heterogeneous architecture and environment plan documented.',
'6 October: rig plan and packaged real-time Ubuntu test profile P3 decision; P3 is not a completed measurement.',
'Early roadmap snapshot (a22fa2b): A2 clock math pending. Later 10 October: A2 implemented (e456e6b), integer-offset / zero-spread review fix (e3b81ab); A3/A4 also landed.',
'Portable clock math is implemented; independent physical clock calibration remains open. Full Linux pipeline landed 11 October (fc37e3b).'
], 'Read the stage report for current state, the roadmap for sequencing.', 'PROJECT.md; docs/ENVIRONMENT_AND_HARDWARE.md; roadmap snapshot; git e456e6b / e3b81ab / f19d05f / bc07462 / fc37e3b')
add('Timeline | implementation and integration, 11–13 October',[
'11 October: feat/pi-timing-tools and feat/inference-baseline; cyclictest correction, live power logs, UART return path and PTY campaign tools.',
'12 October: input-latest E3b, HSE clock, DMA RX, physical E4/F5, real UART E3, analyzer captures and stage report.',
'12 October: component branches merged into release/os-final; cleanup commit 5575cef unifies tests and indexes retained results.',
'13 October: 5e3f461 fixes all 11 review findings and records v1/v2 validity limits. PR #6 release/os-final is open; #3–#5 superseded (brief snapshot).'
], 'Merge status does not certify the new firmware on the rig.', 'git log: 172e415, fdeaa6f, 241d36f, 5575cef, 5e3f461; P_PROGRESS.md')
add('Status board | software and protocol',[
'IMPLEMENTED + TESTED (host): shared parser/CRC, portable supervisor, restart/session checks, DMA cursor and tick diagnostics.',
'IMPLEMENTED + TESTED (host): Linux source, inference, bridge, receiver and analysis/tooling; retained tests are historical checks.',
'MEASURED: Pi inference and software/PTY campaigns under the stated v1 scopes; these are not physical UART AoI.',
'FLAGGED: loaded input-latest and physical E3 comparisons. NOT DONE: clean physical E1/E2 and complete held-value AoI.'
], 'Host logic, target operation and accepted measurements are different milestones.', 'docs/STAGE_REPORT.md; results/README.md; Makefile')
add('Status board | firmware and rig',[
'VERIFIED ON RIG (narrow scope): earlier firmware exchanged status, echo and transition records; later analyzer captures are retained.',
'MEASURED: accepted MCU-local E4/F5 transitions. FLAGGED: bring-up smoke, mixed faults and analyzer inventory.',
'IMPLEMENTED + TESTED (host/cross-build): 11 review fixes. NOT DONE: flash and rig verification of this revision.',
'NOT DONE: independent clock calibration, stack margin qualification, calibrated transit/rearm margins and hardware watchdog integration.'
], 'A previous rig run cannot verify a newer binary.', 'stm32/firmware/README.md; results/README.md; review commit 5e3f461')
add('Evidence rules | v1 history and v2 reruns',[
'MEASURED under v1: E1/E2/E3 PTY 45/45 accepted. v2 replay: 0/45, because RAW monitor timestamps were not retained.',
'MEASURED under v1: cyclictest 15/15 per profile. v2 replay: 3/15 per profile; loaded runs lack stressor-liveness evidence.',
'E4 stays 17/25 on replay; analyzer captures unchanged. Missing v2 evidence does not prove historical runs malfunctioned.',
'v2 requires whole-window RAW monitor coverage, gaps ≤1.5 s, stressors alive and clock fits no older than 5 s.'
], 'Retain v1 observations with their scope; every new campaign uses v2.', 'results/README.md, Validity rule versions; docs/STAGE_REPORT.md')
add('Experiments | timer and inference baselines',[
'MEASURED: cyclictest timer wake-up latency, 30 runs, five loads × two profiles × three repeats; 120 s per run.',
'MEASURED: explicit P0 OTHER and P1 FIFO policies checked on the measured thread. v2 retains only the six idle runs.',
'FLAGGED mixed inference baseline: 21/24 accepted; three four-thread runs excluded for live under-voltage.',
'FLAGGED initial inference collection: 22/24 excluded by original sticky-bit rules; no continuous live-power log. Superseded, not reclassified.'
], 'Timer wake-up and synchronous inference-call time measure different mechanisms.', 'results/2026-10-11_cyclictest/SUMMARY.md; results/2026-10-11_inference_baseline/SUMMARY.md; results/README.md')
add('Experiments | E1 contention and E2 scheduling',[
'E1 measures service/delivery under idle, CPU, stream, cache and memory-rate load; 15/15 accepted under v1.',
'E2 compares scheduling profiles under matched loads; 18/18 accepted under v1. Applied policy and placement belong beside results.',
'Service includes input waiting and preprocessing; delivery ends at a Pi PTY receiver. Neither is a physical MCU latency.',
'INFERRED: memory contention and upstream queueing explain large tails; priority alone did not remove them. v2 cannot confirm these 33 historical runs.'
], 'Before rerunning, verify both the applied profile and the observer evidence.', 'docs/STAGE_REPORT.md, E1 contention and E2 tuning; results/README.md')
add('Experiments | E3 replacement and E3b input policy',[
'E3 changes bridge FIFO/latest policy; 12/12 accepted under v1, PTY only. Replacing after inference cannot clear its input backlog.',
'INFERRED from advancing completions and zero bridge replacements: the overload queue was upstream of the bridge.',
'E3b moves latest-value selection before inference; 12 runs, only 3 accepted. All six loaded plus three idle runs fail live power checks.',
'FLAGGED loaded observations support debugging, not a clean benefit claim. Latest selection does not cancel inference already running.'
], 'Rerun input policy under clean power before claiming a physical freshness gain.', 'docs/STAGE_REPORT.md, Freshness; results/2026-10-12_e3b_input_latest/')
add('Experiments | physical E3 and bring-up',[
'FLAGGED physical E3: 18 runs, 0 accepted; 16 live-power flags, 9 loaded clock-fit failures and 14 missing transition records overlap.',
'Clock residual RMS over 200 µs under memrate prevents clean mapped-time claims. Empty-event rejection has a documented validity limitation.',
'FLAGGED bring-up: seven retained smoke directories, all excluded by summaries. DMA smoke6 has zero UART/CRC counters in its nominal 60 s run.',
'FLAGGED separate real-UART rerun: 18 attempts, 0/18 valid; 18 power, 3 clock, 1 setting and 6 pipeline failures overlap. Six never opened a measurement window: no FRESH before startup deadline.'
], 'Missing FRESH root cause is UNKNOWN; require startup/rearm pilots (pp. 25, 29), beyond PSU replacement.', 'results/README.md; docs/STAGE_REPORT.md; results/2026-10-12_e3_real_uart_rerun/')
add('Experiments | E4 faults and F5 stale data',[
'Original E4: 25 planned entries; 20 performed, 17 accepted. F1 bridge kill, F2 bridge stop, F3 inference stop each 5/5; F4 FIFO hog 2/5; original F5 unperformed.',
'Extra F4: 9 attempts, 5 accepted for short-window transitions; 3 startup failures and one RMS exclusion. No original recovery qualification.',
'Separate F5: 5/5 accepted short-window stale-result transitions. SIGUSR1 suppresses inference while heartbeat continues.',
'MEASURED MCU-local transitions are not independently calibrated safe-output bounds; observed maxima remain observations.'
], 'Keep acceptance denominator, exposure and transition reference together.', 'results/README.md; docs/STAGE_REPORT.md, Physical faults / Extra F4')
add('Analyzer evidence | later than the stage report',[
'FLAGGED inventory: 16 fault attempts, 15 captures, plus channel check; F1-r05 incomplete.',
'F1, F2 and F4 captures compare GPIO marker, UART activity and state GPIO edges on one analyzer clock.',
'Generated comparisons retain UNVERIFIED ON HARDWARE labels and differing MCU/analyzer reference events; no collection-wide promotion.',
'The stage report predates these captures. Its pending-analyzer statements describe the earlier measurement scope.'
], 'Compare like reference events and retain each capture’s qualification.', 'results/README.md chronology note; tools/la/README.md; results/2026-10-12_logic_analyzer/')
add('Rig | access, deployment and separation',[
'Last recorded OS Pi access: richard@192.168.50.2 over direct Ethernet; reconfirm reachability and identity. No Pi internet is assumed.',
'Transfer Git bundles and ARM64 wheels from Mac. Initial bootstrap needs reachable apt sources; bundles/wheels do not provision system packages.',
'Nucleo ST-LINK and FX2 analyzer belong to the Mac in the current runner; Pi owns UART and the fault-marker GPIO.',
'UART serial console must be disabled before opening /dev/ttyAMA0. Direct Ethernet is management access; Pi–MCU data stays UART.'
], 'Reconfirm the actual rig before running old deployment notes.', 'docs/CONDUCTOR_STATE.md; P_PROGRESS.md; tools/la/la_e4.sh; scripts/pi/UART.md')
add('Rig | wiring and readiness gate',[
'Pi pin 8/GPIO14 TX → PA10/USART1 RX; pin 10/GPIO15 RX ← PA9/USART1 TX; shared ground.',
'GPIO17/pin 11 → PA0/TIM2_CH1 is the sync route; GPIO27 marks faults. Confirm actual routing and analyzer channels in a rig photo.',
'USART1 runs at configured 921600 baud; USART2/ST-LINK VCP is a separate debug path. HSE bypass depends on ST-LINK MCO.',
'PLANNED gate: 5 V/5 A supply, cooling, console ownership, zero live flags, correct binary/hash and healthy FRESH startup.'
], 'Photograph and record the setup; configured values are not calibrations.', 'stm32/firmware/README.md wiring; tools/la/README.md; P_PROGRESS.md')
# Tool slides: readable exact invocations with purpose/output for each executable.
def tools(title,rows,source):
    body=''
    for purpose,cmd,out in rows:
        body+=r'\textbf{'+esc(purpose)+r'}\par{\ttfamily '+esc(cmd)+r'}\par '+esc(out)+r'\par\medskip'+'\n'
    raw(title,body+r'\src{'+esc(source)+'}')
tools('Tools | Pi provisioning and individual runs',[
('Initial provision (Pi; apt network required)', 'sudo bash scripts/pi/bootstrap.sh', 'Requires reachable apt sources; installs packages/configures UART. Offline rig: audit dependencies first (README).'),
('Metadata snapshot (Pi)', 'bash scripts/pi/collect_metadata.sh > meta.json', 'Writes platform, power and revision metadata to meta.json.'),
('Detached command wrapper (Pi)', 'bash scripts/pi/run_experiment.sh check -- /usr/bin/true', 'experiments/runs/<UTC>_check/: metadata, logs, exit_code, validity, DONE.')], 'scripts/pi/{bootstrap,collect_metadata,run_experiment}.sh')
tools('Tools | pipeline and controlled faults',[
('Single PTY pipeline (Pi)', 'bash scripts/pi/run_pipeline.sh --duration 60 --run-dir /tmp/pipe', '/tmp/pipe/: config, CSV timestamps, counters and logs; stub by default.'),
('Stop bridge briefly (Pi; substitute its recorded PID)', 'bash scripts/pi/fault_inject.sh stop "$BRIDGE_PID" 1000 2 /tmp/fault.csv', '/tmp/fault.csv onset; stop/continue target process only.'),
('GPIO sync helper (Pi)', 'python3 scripts/pi/uart_tools.py gpio 17 /tmp/sync.csv', '/tmp/sync.csv RAW markers; Ctrl-C ends. fault mode is used by wrapper.')], 'scripts/pi/run_pipeline.sh; fault_inject.sh; uart_tools.py')
tools('Tools | software and timing campaigns',[
('E1/E2/E3/E3B (Pi)', 'bash tools/experiments/e_campaign.sh ALL /tmp/e 3 60 --stage onnx --model "$MODEL"', '/tmp/e/: per-run pipeline/monitor/settings, validity; summary/. ALL follows runner cells.'),
('Timing profile (Pi)', 'bash tools/timing/cyclictest_campaign.sh P0 /tmp/cyc 3 120', '/tmp/cyc/: histogram, thread policy, power/liveness and summary; repeat with P1/new directory.'),
('Python entry point behind shell wrapper', 'python3 tools/experiments/e_campaign.py E3B /tmp/e3b 3 60 --stage onnx --model "$MODEL"', '/tmp/e3b/: input-policy campaign. MODEL is an existing offline ONNX model.')], 'tools/experiments/e_campaign.{sh,py}; tools/timing/cyclictest_campaign.sh')
tools('Tools | physical campaigns and startup',[
('Real-UART E3 (Pi; Mac reset helper required)', 'bash tools/experiments/e3_real.sh /tmp/e3real 3 60 --model "$MODEL" --rearm-command "bash /home/richard/osbuild/rearm_via_mac.sh"', 'Setup Mac SSH/reset via REARM_SETUP.md first. /tmp/e3real/: pipeline, validity, summary; e3_real.py accepts same arguments.'),
('E4 single stale-data trial (Pi)', 'bash tools/experiments/e4_campaign.sh /tmp/f5 1 --single F5 --rearm-command "bash /home/richard/osbuild/rearm_via_mac.sh"', '/tmp/f5/F5-r01/: power, fault/run JSON and pipeline; e4_campaign.py accepts identical arguments.'),
('Startup helper (Pi; usually called by pipeline)', 'python3 tools/experiments/e3_startup.py /tmp/e3real/run/pipeline 30', 'Waits for post-reset FRESH event; writes fresh_start.json, errors on timeout/loss.')], 'tools/experiments/{e3_real,e4_campaign}.{sh,py}; e3_startup.py')
tools('Tools | Mac flashing and analyzer',[
('Flash/reset ST-LINK (Mac with tools installed)', 'bash scripts/stm32/flash.sh openocd', 'Verifies stm32/firmware/build/firmware.elf and resets. reset.sh: bash scripts/stm32/reset.sh; no output file.'),
('Capture fault with FX2 (Mac)', 'bash tools/la/la_e4.sh /tmp/la 5 F2', '/tmp/la/: capture.sr/VCD, Pi logs, la_e4.csv/tex and optional timing PNG. Needs Mac ST-LINK / st-flash, FX2 / sigrok, Mac-to-Pi SSH and confirmed LA_PI / LA_PI_REPO. Reset is local.'),
('Analyze retained/new capture copies (Mac)', 'python3 tools/la/la_analyze.py /tmp/la', '/tmp/la/: comparisons and optional PNG. Analyze a copied capture tree to preserve originals.')], 'scripts/stm32/{flash,reset}.sh; tools/la/{la_e4.sh,la_analyze.py}')
tools('Tools | analysis entry points',[
('One pipeline JSON report', 'python3 analysis/pipeline_summary.py /tmp/pipe > /tmp/pipe-summary.json', 'Reception age/latency distributions; not time-average held-value AoI.'),
('E campaign and cyclictest summaries', 'python3 analysis/e_summary.py /tmp/e --outdir /tmp/e-summary', 'CSV/TeX + README in /tmp/e-summary. Timing: python3 analysis/cyclictest_summary.py /tmp/cyc --outdir /tmp/cyc-summary'),
('Physical E4 and real-E3 summaries', 'python3 analysis/e4_summary.py /tmp/f5 --outdir /tmp/f5-summary', 'Fault CSV/TeX in /tmp/f5-summary. Real E3: python3 analysis/e3_real_summary.py /tmp/e3real → campaign/summary/.')], 'analysis/{pipeline_summary,e_summary,cyclictest_summary,e4_summary,e3_real_summary}.py')
add('Pitfalls | policies, processes and worktrees',[
'cyclictest -p 0 can select FIFO rather than OTHER. Use explicit --policy=other/--policy=fifo and inspect measured thread sched_check.txt.',
'pkill -f can match its own launching shell. Target recorded PIDs; validate ownership and use bounded stop/continue helpers.',
'Worktree firmware build: set FREERTOS_REF to the existing reference kernel path. Do not initialize/reorganize reference code to repair a path.',
'Cleanly rebuild configuration variants; stale objects after rapid configuration switches previously threatened reproducibility.'
], 'A command’s requested setting is not proof of the applied setting.', 'tools/timing/README.md; stm32/firmware/README.md; P_PROGRESS.md')
add('Pitfalls | power, reason codes and clocks',[
'Recorded rig: 5 V/3 A; live under-voltage contaminates loaded comparisons. PLANNED: 5 V/5 A supply and continuous live/new-sticky checks.',
'STATE_EVENT reason 9: source-age HOLD, reference last inference. Reason 3: heartbeat FAILSAFE, reference last heartbeat. Reason 10: source-age FAILSAFE.',
'MEASURED accepted fault observations: about 175 ms after inference, 100 ms after heartbeat; earlier 98 ms HOLD heartbeat age was mislabelled. Different intervals, not bounds/thresholds.',
'Keep Pi RAW and MCU timer domains separate; mapping needs fresh fit/RMS qualification. Internal tick self-check is not absolute calibration.'
], 'Read transition reason before choosing the reference timestamp.', 'docs/STAGE_REPORT.md, Problems found; results/README.md; analysis/e4_summary.py')
add('Next gate 1 | rig record and review-fix verification',[
'PLANNED: add a dated rig photo with board, supply, cooler, TX/RX/GND, ST-LINK and analyzer channels; confirm console ownership.',
'Build exact revision 5e3f461 (or documented successor), record binary hash, configuration and FREERTOS_REF, then flash through Mac ST-LINK.',
'Check five pipeline/firmware fixes: baud transit budget, partial-write expiry, signal-safe waits, bounded latest drain and input timestamp validation.',
'Check six observer/tool fixes: fit age, monitor coverage/gaps, stressor liveness, decoder resync, CPU sample instants and failed-command invalidation.'
], 'Exit gate: all 11 fixes have recorded checks; new firmware reaches FRESH on rig.', 'git show 5e3f461; stm32/firmware/README.md; P_PROGRESS.md')
add('Next gate 2 | clean v2 evidence',[
'PLANNED: rerun timing, software policies, loaded E3b and physical E3 with 5 V/5 A PSU, matched workload and recorded cooling.',
'Capture monitor RAW timestamps across the whole window, ≤1.5 s gaps, applied settings and stressor liveness. Preserve every failure.',
'Physical pilot gate: verify reset and post-reset FRESH in idle + loaded cells, including both failed FIFO-input cells; retain startup failures. Fit age ≤5 s; RMS ≤200 µs.',
'Target five independent valid repeats per cell. Extend F5 to original exposure/recovery; compare analyzer reference events and calibrate clocks.'
], 'Exit gate: valid-repeat target plus raw evidence, exclusions and scoped summaries.', 'docs/STAGE_REPORT.md, Next steps; results/README.md; campaign summary/README.md')
add('Next gate 3 | PR and final submission package',[
'PLANNED: reconcile the review-fix revision with PR #6 release/os-final; check CI, review findings and rig-verification record before merge.',
'PR #3–#5 are superseded in the brief snapshot. Avoid integrating stale component branches over the release candidate.',
'Package defense, report and owner deck with sources, PDFs, reproducible build commands, evidence inventory and review logs.',
'Exit gate: fresh checkout builds; links and paths resolve; retained flags/v1-v2 limits survive packaging; final page review has no overflow.'
], 'Merge and submission are explicit completion gates, not inferred from a build.', 'P_PROGRESS.md; submission/briefs/COMMON.md; git log release integration')
add('WBR connection | roadmap A–F',[
'PLANNED roadmap: A Pi software → B external MCU → C physical experiments → D WBR shadow logging → E controlled integration → F article.',
'Current evidence advances A–C, with power/clock/verification gates still open. Older roadmap completion markers are historical.',
'Transfer timestamp discipline, liveness/freshness separation, upstream replacement and independent fault observation.',
'Before D/E, review actual interface and fallback: reject stale Pi commands while preserving local balancing control. Re-measure all thresholds.'
], 'The method transfers; this rig’s timing numbers and safe-output semantics do not.', 'docs/ROADMAP_TO_WBROBOT_AND_ARTICLE.md; docs/STAGE_REPORT.md, Limits and transfer')
# Study index generated from actual long-deck frame sequence, avoiding guessed page references.
long_titles=json.loads((HERE/'study-reference.json').read_text())['titles']
def pages(term):
    return ', '.join(str(i+1) for i,t in enumerate(long_titles) if term.lower() in t.lower()) or 'see contents'
add('Study pointers | mechanisms behind the checks',[
f'Processes / scheduling / contention: long deck pp. {pages("Processes")}, {pages("Scheduling")}, {pages("contention")}; learning-plan modules 0, 1, 4, 7.',
f'Queues / freshness: long deck pp. {pages("Queueing")}, {pages("Age of Information")}; modules 5, 6 and 12.',
f'RTOS / supervision / clocks: long deck pp. {pages("Real-time task")}, {pages("Independent supervision")}, {pages("Clock domains")}; modules 8, 10, 11.',
'PENDING owner lookup: exact Obsidian M-lessons UNKNOWN. Gate: map every mechanism above to a supplied/authorized note title + path; see README. No external vault searched.'
], 'Read the mechanism, then trace its implementation and one retained run.', 'slides_course/main.tex frame sequence; docs/LEARNING_PLAN.md; docs/obsidian/2026-10-08-pi5-phase.md')
add('First session | concrete checklist',[
'Confirm dedicated OS Pi identity and direct-link access; photograph the rig and install the clean supply/cooling.',
'Build, hash, flash and validate the review-fix firmware; retain startup/status/counter logs and all 11 verification outcomes.',
'Run idle + loaded v2 pilots, including input FIFO / bridge FIFO and latest. Gate: verified reset, post-reset FRESH and opened window; then audit power, coverage, settings, clocks.',
'Archive raw runs and scoped summaries; resolve PR #6 gate, then rebuild all final deliverables and record their visual review.'
], 'Start with an accepted pilot; scale only after the evidence pipeline passes.', 'P_PROGRESS.md; results/README.md; docs/STAGE_REPORT.md, Next steps')
assert len(slides)==29,len(slides)
(HERE/'main.tex').write_text(preamble+'\n'.join(r'\begin{frame}{'+esc(t)+'}\n'+b+'\n'+r'\end{frame}' for t,b in slides)+ '\n\\end{document}\n')
(HERE/'PAGE_INDEX.md').write_text('# Progress deck page index\n\n'+'\n'.join(f'{i+1}. {t}' for i,(t,b) in enumerate(slides))+'\n')
print(f'Generated {len(slides)} slides')
