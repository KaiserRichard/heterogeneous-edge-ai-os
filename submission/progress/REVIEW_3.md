# Independent progress-deck review — round 3

Verdict: FAIL

Reviewed 2026-10-13 against `submission/briefs/P_PROGRESS.md`,
`submission/briefs/COMMON.md`, the repository instructions and the parent
workspace's `PROJECT.md`. Page numbers are PDF pages, 1–29.
One MAJOR and one MINOR defect; no BLOCKER.

## Numbered defects

1. **MAJOR — Page 3: the 10 October timeline incorrectly leaves clock math unimplemented.**
   The third bullet says that, by 10 October, “clock math and full pipeline were
   still roadmap work.” The roadmap records an earlier snapshot at `a22fa2b`,
   not the end-of-day state. Retained commit `e456e6b`, dated **2026-10-10
   15:50:47 +0700**, implements A2 clock math, including
   `protocol/src/hea_clock_sync.c`, its API, tests and `protocol/CLOCK_SYNC.md`.
   Commit `e3b81ab`, **15:54:38** that day, fixes the integer-offset combination
   and adds the zero-spread fit test. A3/A4 also appear that day as `f19d05f`
   and `bc07462`. This is a material error in the requested implementation
   timeline: it treats an outdated planning snapshot as proof of what had not
   yet been built. State that the early roadmap snapshot still listed A2 as
   pending, then record the later 10 October implementation/review fix. Keep
   portable clock math distinct from independent physical clock calibration,
   which remains open. The Linux pipeline commit `fc37e3b` is dated 11 October.

2. **MINOR — Page 20: the analyzer command is assigned the wrong reset dependency.**
   Its description says “Requires SSH/reset helper.” The matching entry in
   `TOOL_CATALOG.md` repeats this. Unlike the page 19 Pi campaigns,
   `tools/la/la_e4.sh` resets directly on the Mac using `st-flash reset`,
   checks that `st-flash` exists, and launches the Pi runner with
   `--rearm-command true` after that local reset. It does not invoke
   `/home/richard/osbuild/rearm_via_mac.sh`. Describe its actual prerequisites:
   Mac-owned ST-LINK with `st-flash`, FX2/sigrok, Mac-to-Pi SSH, and confirmed
   `LA_PI`/`LA_PI_REPO` deployment values. Reserve the Pi-to-Mac reset-helper
   prerequisite for page 19. The printed analyzer command and output paths
   themselves agree with the runner.

## Build and full-size visual inspection

Built the existing source, without regeneration or source edits, from
`submission/progress/`:

```sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=/tmp/review_P3 main.tex
```

Exit **0**, **29 pages**, `/tmp/review_P3/main.pdf`. The final log has no
matches for `Overfull|Underfull|Missing character|undefined|^!`.

The required renderer completed with caches redirected into the review directory:

```sh
CLANG_MODULE_CACHE_PATH=/tmp/review_P3/clang-cache SWIFT_MODULECACHE_PATH=/tmp/review_P3/swift-cache swift /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/render.swift /tmp/review_P3/main.pdf /tmp/review_P3/preview
```

While Swift compiled, the supplied `render.m` PDFKit fallback also rendered all
29 pages, with its executable and outputs confined to `/tmp/review_P3`.
Inspected **every page individually, 1–29, at original 1280 × 720 resolution**.
No visible clipping, overflow, overlap, missing glyphs, missing images or
unreadably small body text. Page 19 is dense but readable; commands have
copyable counterparts. Figure 1 is numbered, captioned and explained.
`image-prompts/NEEDS.md` contains `NONE`; no measured-data figure requires a
generation script. Every slide serves owner orientation, evidence assessment,
operation, next steps or study; no unrelated-purpose slide was found.

## Numbers and claims checked

Checked the complete slide source and rendered pages against `results/README.md`,
`docs/STAGE_REPORT.md`, retained summaries/CSVs/logs, configuration documentation,
script interfaces and read-only git history. The substantive exceptions are
numbered above. Specific checks include:

- **Pages 7–10:** PTY v1 acceptance **45/45**, split **15/18/12**, and v2
  replay **0/45**; cyclictest **30** runs, **15/15** per profile under v1,
  **3/15** under v2, **six** idle survivors, **120 s**, five loads, two
  profiles, three repeats. Inference baseline **21/24** with three four-thread
  exclusions; initial collection **22/24** excluded. E3b **3/12** accepted,
  six loaded and three idle exclusions. CSV recount agrees. The queue-location
  explanation remains INFERRED, and PTY endpoints are not promoted to hardware.
- **Pages 11–13:** first real-UART campaign **0/18**, overlapping **16/9/14**
  flags; seven excluded smokes, smoke6 zero UART/CRC counters over nominal
  **60 s**. Rerun **0/18**, overlapping **18/3/1/6** exclusions; all six
  failed pipeline logs confirm no FRESH before startup deadline and missing
  measurement-window starts. Original E4 **25 entries / 20 performed / 17
  accepted**, F1–F3 each **5/5**, F4 **2/5**; extra F4 **5/9**, three startup
  failures and one RMS exclusion; separate F5 **5/5**, with restricted exposure.
  Analyzer inventory **16 attempts / 15 captures**, incomplete F1-r05 and
  separate channel check agree with the inventory and retained files.
- **Pages 4–6, 14–27 and 29:** integration commits, all **11** review-fix
  categories (five pipeline/firmware, six observer/tool), configured pins and
  **921600** baud, last-recorded access address, management/data-link separation,
  **1.5 s** monitor gaps, **5 s** fit age, **200 µs** RMS gate and planned
  **five** valid repeats agree with the cited sources. Page 23's approximately
  **175/100/98 ms** intervals match the reason-based stage-report interpretation.
  Firmware fixes remain host/cross-build verified and explicitly unverified on
  the rig. PR status is attributed to the supplied brief snapshot, rather than
  presented as a newly verified remote status.
- **Pages 16–21 and companions:** compared production and eight test-script
  entries with the files under `tools/`, `scripts/` and `analysis/`; checked
  command arguments and output locations without executing provisioning or
  hardware operations. `REARM_SETUP.md` supplies a fail-fast reset template,
  UNKNOWN deployment fields, SSH prerequisites, reset identity/exit checks and
  a separate post-reset FRESH/window gate. Provisioning now explicitly requires
  reachable apt sources; the firmware artifact path is correct.
- **Page 28:** independently checked long-deck pages **9–16** and **82**
  against its actual frame/section sequence and module numbers against
  `docs/LEARNING_PLAN.md`. Exact external M-lessons remain UNKNOWN, with an
  explicit pending owner lookup and completion gate; no external vault was
  searched.

Round 2's startup omission, missing rearm procedure, provisioning prerequisite,
timing labels and artifact-path defects are addressed. Its M-lesson handoff now
has the requested pending lookup/gate. Historical validity scopes, FLAGGED
collections, calibration limits and observed-maxima qualifications are preserved.

No measurement, flash, reset, physical verification or remote PR action was
performed. Only `submission/progress/REVIEW_3.md` was written in the repository;
build and render artifacts are under `/tmp/review_P3`.
