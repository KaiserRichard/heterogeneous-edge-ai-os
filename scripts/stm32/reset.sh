#!/bin/sh
# Run explicitly on the Pi. UNVERIFIED ON HARDWARE.
set -eu
exec openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
  -c 'init; reset run; shutdown'
