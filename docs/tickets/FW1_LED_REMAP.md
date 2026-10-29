# FW1 — Bench LED map D4/D5/D6/D9 for supervisor states

Goal: show supervisor state on the bench LEDs: D4 (PB5) green = FRESH, D5 (PB4) yellow = HOLD,
D6 (PB10) red = FAILSAFE (latched until rearm), D9 (PC7) blue = toggles on each accepted frame
(link activity). PA5 (LD2) keeps the FRESH signal so the old logic-analyzer channel still works.
Authority: owner request 2026-10-29; roadmap phase 0. Pins per UM1724 Arduino table; state the
table/figure you used in the README.

Inputs: AGENTS.md, PROJECT.md, docs/CAMERA_ROADMAP.md, stm32/firmware/main.c, stm32/README.md,
stm32/include/supervisor.h, tools/la/ (decoder of the old PA5/PB5 two-wire code) and tests.
Write scope: stm32/firmware/main.c (GPIO init + state output only), new
stm32/firmware/board_leds.h, stm32/firmware/README.md, tools/la/ decoder + tests (add a
one-hot LED mode, keep the old two-wire mode for the archived captures), this ticket.
No supervisor logic, protocol, timer budgets or UART changes. No flashing.

Implementation: one function maps `supervisor_state` -> pin set/reset via BSRR (atomic, no
read-modify-write); enable GPIOB/GPIOC clocks; all LEDs off before the scheduler starts; INIT
= all off; exactly one of D4/D5/D6 on in any state. D9 toggle happens in the task that
accepts a frame, not in an ISR. Keep the diagnostic image behaviour documented.

Acceptance: `make firmware` with arm-none-eabi-gcc builds with no new warnings (report text,
data, bss vs before); `make test` green; host test of the state->pin-mask table covers every
state; LA decoder tests pass in both modes. Report: commands with output, the pin table, and
"not flashed, not verified on hardware". No commit/push: the conductor reviews and commits on
`feat/bench-leds`.
