# Independent report review 2

**Verdict: FAIL — one MAJOR and two MINOR defects; no BLOCKER.**

Reviewed the current report independently against `submission/briefs/R_REPORT.md`, `submission/briefs/COMMON.md`, `PROJECT.md`, repository instructions, `results/`, and `docs/STAGE_REPORT.md`. Page references count the cover as **PDF page 1**; printed page numbers are one less. This verdict concerns the written submission, not hardware qualification.

## Verification performed

- Built from `submission/report/` with `latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=/tmp/review_R2 main.tex`. The resulting PDF is `/tmp/review_R2/main.pdf`, **25 pages**. The final log contains no LaTeX errors, overfull/underfull boxes, undefined references/citations, or missing-character warnings.
- Rendered the fresh PDF using the repository's `slides/render.swift`, with the Swift module cache and PNG output redirected into `/tmp/review_R2`. Opened **every page, 1–25, individually at original 1280 × 1810 resolution**. No contact-sheet or previous-render substitution was used. Text, tables, equations, references, and appendix commands remain readable; no clipping, overlap, unresolved placeholders, or tiny text was found.
- Executed the evidence generator with only its output destination redirected to `/tmp/review_R2/regenerated`. All **12 generated result tables**, acquisition metadata, and the **298-input source manifest** match the submitted generated files byte-for-byte. Compared all displayed result numbers and narrative quantities with retained summaries and the stage report. Checked raw extraction for E3b, real-UART reception age, reason-specific E4 intervals, and F5 intervals through regeneration; separately checked E3 completion intervals, real-UART threshold counts/states, smoke echo fits/counters, and the F5 tick diagnostic.
- The six loaded E3 completion-interval medians are 121.717, 127.987, 125.888, 130.493, 123.324, and 129.065 ms, consistent with the report's approximate 122–130 ms range. Latest/latest real-UART threshold counts are 182/449, 156/476, and 193/427, reproducing 40.5%, 32.8%, and 45.2%; their original reception states are all FAILSAFE. Loaded E3b reception records used by the generator all have `crc_ok=1`.
- Checked implementation/configuration claims against protocol documentation, Linux bridge/runtime/queue code, firmware and supervisor code; checked background claims against the cited repository research notes. Checked acquisition provenance against retained metadata and read-only Git history. Also examined the later real-UART rerun omitted from the report and from the dated result inventory.
- No target experiments, source tests that generate repository artifacts, firmware flashing, or hardware qualification were performed. Review artifacts are in `/tmp/review_R2`; the only repository file written is `submission/report/REVIEW_2.md`.

## Numbered defects

1. **MAJOR — PDF p. 19 (printed p. 18), §7.1: the discussion still promotes a proposed cause into an established experimental finding.**

   The opening says: “The experiments connect three OS mechanisms. First, processor priority changes runnable service but leaves shared-memory interference.” In this results synthesis, the specific shared-memory mechanism is stated without the INFERRED qualification. The experiments establish increased latency under the selected cross-core stressors; they do not causally isolate memory-bus/cache interference from other effects. This conflicts with the corrected Appendix C on PDF p. 25, which explicitly says shared-memory interference is INFERRED and not causally isolated.

   Evidence: `docs/STAGE_REPORT.md`, “E1 contention and E2 tuning,” explicitly says these results do not establish a causal memory-bus mechanism without further counters or controlled isolation. The retained E1/E2 summaries measure stage latency under stress, rather than providing that causal isolation. The report itself defines INFERRED on PDF p. 11.

   **Required correction:** state the MEASURED-under-v1 observation—latency remains elevated under cross-core memrate stress despite the P1 configuration—and identify shared-memory interference as an INFERRED explanation. General architectural facts about priority not reserving bandwidth may remain in the background, but the discussion must preserve the evidence status when attributing this rig's result to a mechanism. The previous review's causal-label correction is present in the appendix but has not been carried consistently into the main synthesis.

2. **MINOR — PDF p. 8 (printed p. 7), §4.1: the partial-frame completion description omits the current bounded-abort behavior.**

   “A partially emitted frame must finish consistently” is an unconditional completion statement. The current bridge preserves an emitted prefix against replacement, but it also aborts submission when the **2 ms** write budget expires. It flushes queued output, counts `expired`, advances the sequence, and waits a quiet interval before sending another frame. Prefix immutability and guaranteed completion are different contracts; the report currently describes only the former as though it implied the latter.

   Evidence: `linux/src/hea_bridge.c`, `transmit()` and the main-loop partial-write expiration paths; `stm32/firmware/uart_budget.h`, `HEA_UART_WRITE_US`. These are current source behavior, not a newly verified hardware result.

   **Required correction:** say that partially submitted frames are immutable and are completed within the submission budget or abandoned through the counted flush/quiet-interval path. Briefly connect the timeout to preventing arbitrarily delayed frame submission and to loss accounting. Preserve the distinction between current software behavior and historical acquisitions.

3. **MINOR — PDF pp. 10, 16, and 22–23 (printed pp. 9, 15, and 21–22), Table 3 / §6.5 / Appendix A: the real-UART evidence scope omits a retained later rerun.**

   The report inventories only the original `20261012T105039Z_e3real` campaign, with 18 runs and no accepted comparisons. The checkout also retains `results/2026-10-12_e3_real_uart_rerun/20261012T160628Z_e3real2/`, added by cleanup commit `5575cef`. Its `summary/per_run.csv` contains **18 further attempts, 0 accepted**, with live-power exclusions in every attempt and six pipeline failures. Its three loaded latest/latest rows contain 403/410/417 deliveries and MCU-age P50 values of 208.649/204.178/203.316 ms. Unlike the original campaign, two of these rows retain FRESH/HOLD state durations. Thus the original campaign's all-FAILSAFE/empty-event observations are scoped correctly within §6.5, but the report's evidence inventory is incomplete and does not explain why the later diagnostic material was omitted.

   Evidence: the rerun's `summary/README.md`, `summary/per_run.csv`, `summary/per_condition.csv`, and `campaign.json`; read-only `git log`. `results/README.md` and the stage report also omit this later campaign, so their inventory alone does not settle the checkout's complete evidence scope. The rerun README's generic MEASURED heading must not override its per-run invalidity flags.

   **Required correction:** identify the original campaign explicitly in the exposure table and add a brief FLAGGED rerun inventory/traceability note with its exclusions. Either discuss the later diagnostic observations or explicitly state their exclusion from the presented comparison. Keep both campaigns separate; do not pool them, promote their observations, or imply the later rows validate HOLD occupancy under clean conditions.

## Evidence, readability, and story assessment

The numeric corrections requested by REVIEW_1 are present. Table 9 now reports the idle held-value violation times despite zero reception misses, with strict thresholds and delivery denominators. DMA capacity is correctly calculated as 22.22 ms. Aggregate versus per-run quantile scope is clear, E3b names its endpoint, scientific notation has been expanded, and Appendix B resets the working directory.

All displayed result-table values agree with the retained evidence. v1/v2 acceptance scopes remain distinct. FLAGGED E3b, original real-UART, bring-up, and analyzer observations are not promoted into clean comparisons. E4/F5 intervals follow transition reasons, source-age thresholds remain distinct from receipt-relative intervals, maxima remain observations rather than guarantees, and the unflashed firmware limitation is explicit. The main story—scheduling, upstream queueing, then independent liveness/freshness supervision—serves the written course-report purpose. No section was found to require removal for serving a different deliverable purpose. Intentional title-page placeholders comply with the brief.

Visual inspection covered the cover (p. 1), abstract/introduction/background (pp. 2–5), design/implementation (pp. 6–9), method (pp. 10–11), all results (pp. 12–18), discussion/conclusion/references (pp. 19–21), and all appendices (pp. 22–25). All pages pass layout/readability inspection. The page target is a guide; 25 pages including four appendix pages is not treated as a defect.

Resolve defect 1 before acceptance and correct defects 2–3 in the same revision. **Final verdict: FAIL.**
