# T2 — Versioned Pi age-at-send payload

Goal: carry input-to-send duration without comparing Pi and MCU timestamps.
Authority: user approval on 2026-10-08; Step 1 remains receipt silence only.

Inputs: AGENTS.md, PROJECT.md, protocol/PROTOCOL.md, protocol/include/hea_proto.h,
protocol/src/hea_proto.c, protocol/tests/test_proto.c and the supervisor adapter.
Scope: those protocol files, adapter/tests, relevant docs; no third-party, hardware
configuration, clock mapping or source-AoI supervisor policy.

Implementation: append uint32 microseconds at offset 22; emit version 2, decode
legacy version 1 with absent age; provide same-Pi-clock conversion with upward
microsecond rounding, saturation and clock-regression rejection. Reject mismatched
version/payload lengths. Keep header size, CRC and other payload layouts unchanged.

Acceptance: round-trip, captured independent legacy frame, explicit version/length
rejection, saturating conversion edge cases, legacy/new receipt-only supervisor
behavior. Run protocol and supervisor ASan/UBSan tests on Mac and Pi in both char
modes, then CI and Cortex-M4 compilation. Review before committing. Report commit,
evidence and limitations; no measured hardware AoI claim.
