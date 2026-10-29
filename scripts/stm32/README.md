# Nucleo firmware switch

`nucleo_switch.py` backs up and verifies the STM32F446RE through its system UART
bootloader. It uses the Python standard library and a POSIX serial device; no
`pyserial` installation is needed. The default port and baud are `/dev/ttyAMA0`
and 57600 8E1.

Before an owner-approved switch, check the firmware artifact and its SHA-256,
then run on the Pi:

```sh
python3 scripts/stm32/nucleo_switch.py \
  --port /dev/ttyAMA0 \
  --image path/to/firmware.bin \
  --expect-sha256 <64-hex-character-sha256> \
  --archive path/to/flash-archive
```

At the prompt, hold BOOT0 high and press RESET to enter the ROM loader. The
script checks product ID `0x421`, reads and archives the full 512 KiB flash,
appends its digest to `SHA256SUMS`, and only then checks the requested image
digest. A failed backup or image hash check stops before erase. It erases only
the F446 sectors intersecting the image, writes the image (padding the final
write with `0xff` to a word boundary), reads back that range, and compares every
byte. On success it prints the instruction to set BOOT0 low and press RESET,
followed by one JSON result line. Existing timestamp-named backups are opened
exclusively and never replaced.

`--dry-run` still requires the ROM loader, makes the complete backup, and checks
the image digest; it skips erase and write. It is useful for validating a
candidate image and the backup path without changing firmware.

The AN3155 module implements sync, GET_ID, READ_MEMORY, extended sector erase,
WRITE_MEMORY, and GO. The switch command deliberately does not issue GO: the
operator resets with BOOT0 low after reviewing the success result. This keeps
the boot-mode change explicit.

Run the host-side fake-loader checks on macOS or Linux:

```sh
python3 -m unittest discover -s scripts/stm32/tests -v
```

The test uses a PTY and exercises sync failure, unexpected product ID, backup
read failure, hash mismatch, successful write/read-back, and verification
mismatch. These tests validate protocol handling only; they do not replace a
physical UART/board check. **Not run on hardware.**
