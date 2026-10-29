# FW2 report — UART Nucleo firmware switch

## Changes

- Added `scripts/stm32/stm32boot.py`, a standard-library POSIX UART AN3155
  client for sync, GET_ID, READ_MEMORY, extended sector erase, WRITE_MEMORY,
  and GO.
- Added `scripts/stm32/nucleo_switch.py`. It checks the F446RE product ID,
  backs up all 512 KiB before validating the requested image SHA-256, erases
  only sectors touched by the image, writes, reads back, and compares the
  image bytes. Backup files are exclusive-created and their SHA-256 values are
  appended to `SHA256SUMS`.
- Added six PTY fake-loader tests for sync failure, wrong product ID, read
  failure without write, hash mismatch without erase, successful write and
  verify, and verify mismatch.
- Added `scripts/stm32/README.md` and added FW2 discovery to the root `make test`
  target.

## Commands run

`python3 -m unittest discover -s scripts/stm32/tests -v`:

```text
test_hash_mismatch_does_not_erase ... ok
test_read_failure_does_not_write ... ok
test_sync_failure ... ok
test_verify_mismatch ... ok
test_write_and_verify_success ... ok
test_wrong_product_id ... ok

Ran 6 tests in 6.474s

OK
```

`python3 -m py_compile scripts/stm32/nucleo_switch.py scripts/stm32/stm32boot.py scripts/stm32/tests/test_nucleo_switch.py` completed with exit status 0 and no output.

`make test` exited 2. Protocol tests passed (`all protocol tests passed`; clock
sync `51 checks` passed), and STM32 tests passed (`24 supervisor scenarios
passed` plus RX-DMA and tick-diagnostic checks). Linux binaries built and
`test_core` passed, then `test_pipeline` stopped the run:

```text
Assertion failed: (seq == next), function check_csv, file test_pipeline.c, line 113.
SKIP: named Unix socket bind denied by sandbox; exercising the same datagram ABI via socketpair
make[1]: *** [test] Abort trap: 6
make: *** [test] Error 2
```

The FW2 tests were run again after this full-suite attempt and all six passed.

## Limitations

- Not run on hardware. No Pi was contacted and no firmware was flashed.
- PTY tests verify the local protocol exchange; physical UART electrical and
  board behavior still needs owner-directed bench verification.
- `make test` remains blocked by the Linux pipeline assertion above; that
  failure is outside the FW2 files.
