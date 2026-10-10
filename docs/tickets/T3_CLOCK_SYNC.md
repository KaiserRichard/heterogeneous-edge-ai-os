# T3 — Portable clock-sync math

Goal: validate offset, delay and drift math before hardware clock alignment.
Authority: user approval 2026-10-08. No source-AoI supervisor policy or hardware work.
Read AGENTS.md, PROJECT.md, docs/research/R8.md, protocol/PROTOCOL.md, protocol's
Makefile/style and this ticket. User scope supersedes the broader PI-only brief.

Write scope: protocol/include/hea_clock_sync.h, protocol/src/hea_clock_sync.c,
protocol/tests/test_clock_sync.c, protocol/Makefile, protocol/CLOCK_SYNC.md, this
ticket only. Everything else read-only; the lead integrates CI. No third_party.
Pure C99, no heap, OS, HAL, firmware, network calls or wire-format changes.

Steps:
1. Implement RFC 4330 section 5 formula in common microsecond units:
   theta=((T2-T1)+(T3-T4))/2; delta=(T4-T1)-(T3-T2). T1/T4 Pi, T2/T3 MCU.
   Source: https://www.rfc-editor.org/rfc/rfc4330.html#section-5.
2. Avoid unsigned subtraction underflow and catastrophic loss from converting
   large absolute timestamps before subtracting. Validate ordering, finite values
   and unusable samples explicitly; document any rejected negative delay.
3. Provide bounded caller-owned min-delay window filter; reject invalid samples,
   expire old samples, document ties and insufficient-data behavior.
4. Implement centred least-squares offset vs Pi reference-time fit; expose offset
   at a reference, drift (ppm or dimensionless with conversion), residual diagnostics.
   Reject insufficient data, zero time spread and nonfinite/overflow cases.
5. Extend uint32 MCU microsecond timer wrap into uint64. Reject regressions/exact
   half-range ambiguity and preserve state on errors. State the required gap below
   2^31 us and arbitrary initial epoch; do not invent epoch alignment from raw ticks.
6. Host tests for known positive/negative offsets and drift, deterministic jitter,
   filter eviction, asymmetric-delay bias, wrap through T2/T3, large timestamps,
   invalid input and singular fits. State numeric tolerances before claiming PASS.
   No tolerance adjusted just to hide a failing implementation.
7. Run strict ASan/UBSan tests in both char modes. Document build/reproduction,
   actual synthetic counts/tolerances and hardware limitations.

Acceptance: tests recover synthetic parameters within documented tolerances,
correctly demonstrate rather than remove asymmetric-delay bias, extend timer wrap,
reject invalid data without corrupting state and pass sanitizers. Inspect diffs.
Report: paths, API/contract choices, commands and outputs, real limitations.
No commit/push: lead reviews, then commits. One writer per file.
