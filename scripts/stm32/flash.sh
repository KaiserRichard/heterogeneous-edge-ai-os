#!/bin/sh
# Run explicitly on the Pi with ST-LINK attached. UNVERIFIED ON HARDWARE.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$root"
case "${1:-openocd}" in
  openocd)
    test -f stm32/firmware/build/firmware.elf
    exec openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
      -c 'program stm32/firmware/build/firmware.elf verify reset exit' ;;
  st-flash)
    test -f stm32/firmware/build/firmware.bin
    exec st-flash --reset write stm32/firmware/build/firmware.bin 0x08000000 ;;
  *) echo 'usage: flash.sh [openocd|st-flash]' >&2; exit 2 ;;
esac
