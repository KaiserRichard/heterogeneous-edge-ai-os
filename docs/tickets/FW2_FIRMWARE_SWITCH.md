# FW2 — One-command Nucleo firmware switch (backup -> write -> verify)

Goal: switch the shared Nucleo-F446RE between the WBR micro-ROS image and the OS supervisor
image safely, from the Pi, over the UART system bootloader (`/dev/ttyAMA0`, the ST-LINK path
is unreliable on this bench).
Authority: owner request 2026-10-29; roadmap phase 0. Flashing itself stays manual and needs
the owner's `CONFIRM flash nucleo <image>`; this ticket only writes and tests the script.

Inputs: AGENTS.md, scripts/stm32/flash.sh, scripts/pi/README.md, docs/CAMERA_ROADMAP.md,
and `scripts/stm32/stm32boot_ref.py`: a copy of the owner's WBR bootloader client (the one
that read the 2026-10-29 backups), placed there by the conductor. Do not read other repos.
Write scope: new `scripts/stm32/nucleo_switch.py`, `scripts/stm32/stm32boot.py` (AN3155 client:
sync 0x7F, GET_ID, READ_MEMORY, ERASE/EXTENDED_ERASE, WRITE_MEMORY, GO), new
`scripts/stm32/tests/` (fake bootloader over a pty), `scripts/stm32/README.md`, this ticket.

CLI: `nucleo_switch.py --port /dev/ttyAMA0 --image PATH --expect-sha256 HEX --archive DIR
[--dry-run]`. Steps: 1) prompt "hold BOOT0 high, press RESET" and sync; 2) check product id
0x421; 3) read all 512 KiB to `DIR/<UTC>-backup.bin`, write `SHA256SUMS`, refuse to continue
if the read fails; 4) check the image hash equals `--expect-sha256`, else stop; 5) erase only
the sectors the image needs, write, read back and compare byte for byte; 6) print the
"set BOOT0 low and press RESET" instruction and a one-line JSON result. Never deletes an
existing backup; refuses an archive path that already contains a file of the same name.

Acceptance: pty fake-bootloader tests cover sync failure, wrong product id, read failure
(no write happens), hash mismatch (no erase happens), write + verify success, verify mismatch.
`python3 -m unittest discover -s scripts/stm32/tests -v` passes on the Mac; add it to
`make test`. Report: commands with output; "not run on hardware". No commit/push: the conductor
reviews and commits on `feat/nucleo-switch`.
