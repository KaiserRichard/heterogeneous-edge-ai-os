# FW1 implementation report

## Changes

- Added `stm32/firmware/board_leds.h` with a host-testable state-to-BSRR-mask
  mapping and task-context D9 activity toggle. `main.c` enables GPIOA/B/C,
  preloads all four LEDs off before configuring outputs, applies one-hot state
  output, and toggles D9 when the supervisor accepts a new wire sequence or
  establishes a sender session. PA5 remains on for FRESH in the normal image.
- Added a host C test that covers INIT, FRESH, HOLD, and FAILSAFE. Updated the
  firmware README with the pin table, source reference, and diagnostic-image
  behavior.
- Added `--mode one-hot` to the LA decoder for D4/D5/D6/D9 captures. The default
  remains the archived PA5/PB5 two-wire decoder. Added tests for both modes and
  rejection of overlapping state LEDs.

## Pin map

| Supervisor state | PA5 / LD2 | D4 / PB5 green | D5 / PB4 yellow | D6 / PB10 red |
|---|---:|---:|---:|---:|
| INIT | off | off | off | off |
| FRESH | on | on | off | off |
| HOLD | off | off | on | off |
| FAILSAFE | off | off | off | on |

D9 / PC7 blue starts off and toggles for each accepted wire-sequence advance or
sender-session establishment. Pins D4/D5/D6/D9 follow UM1724 Rev. 17 Table 19,
“ARDUINO® connectors on NUCLEO-F446RE” (CN5/CN9 digital rows).

## Commands and output

Baseline and post-change firmware build command:

```text
$ make firmware
arm-none-eabi-gcc ... -c main.c -o build/main.o
main.c:2:10: fatal error: stm32f446xx.h: No such file or directory
    2 | #include "stm32f446xx.h"
      |          ^~~~~~~~~~~~~~~
compilation terminated.
make[2]: *** [build/main.o] Error 1
make[1]: *** [firmware] Error 2
make: *** [firmware] Error 2
```

The configured `third_party/nucleo-f446re-freertos` reference submodule is
uninitialized in this worktree. I left it untouched. Since neither build reached
linking, `text`, `data`, and `bss` sizes are unavailable both before and after;
the ARM build also cannot establish whether changed firmware sources add warnings.

Host state-map test:

```text
$ cc -std=c11 -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror \
    -Istm32/firmware -Istm32/include -Iprotocol/include \
    stm32/firmware/board_leds_test.c -o /tmp/fw1_board_leds_test
$ /tmp/fw1_board_leds_test
PASS: all four supervisor states map to the expected atomic LED pin masks
```

LA decoder tests:

```text
$ python3 -m unittest discover -s tools/la/tests -v
Ran 12 tests in 3.788s
OK
```

Full repository suite:

```text
$ make test
24 supervisor scenarios passed (66822 checks, including exhaustive 16-bit increment wrap).
Ran 78 tests in 108.754s
OK
Ran 12 tests in 1.062s
OK
Ran 43 tests in 16.038s
OK (skipped=3)
```

Python syntax and whitespace checks:

```text
$ python3 -m py_compile tools/la/la_analyze.py
# exit 0, no output
$ git diff --check
# exit 0, no output
```

## Limitations

The full `make test` suite passes on this macOS host; its output records expected
environment skips for Unix socket bind/affinity checks. The standalone C mapping
test compiles with warnings treated as errors. Firmware cross-compilation and
before/after image sizes remain blocked by the missing reference submodule header.
The diagnostic image (`BRINGUP_BLINK=1`) deliberately forces D4 off and blinks
PA5 at 1 Hz; D5/D6 continue to show HOLD/FAILSAFE and D9 continues to toggle.

Not flashed, not verified on hardware.
