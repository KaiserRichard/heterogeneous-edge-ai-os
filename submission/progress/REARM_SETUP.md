# Restore Pi-to-Mac rearm — PLANNED, not rig-verified

Pi runs campaigns; Mac owns Nucleo ST-LINK. Historical helper implementation is absent. UNKNOWN deployment values: Mac SSH user/address reachable from Pi, Mac checkout path and absolute OpenOCD path. Confirm and record these before deployment.

On Mac: enable Remote Login for the rig account, confirm the direct-link route from Pi, attach ST-LINK, locate OpenOCD (`command -v openocd`) and the checkout, and close competing ST-LINK sessions. On Pi: configure SSH key authentication, verify the Mac host fingerprint through a trusted channel and test `ssh -o BatchMode=yes MAC_USER@MAC_ADDRESS /usr/bin/true`. This tests connectivity only, not reset.

Install the following as `/home/richard/osbuild/rearm_via_mac.sh` on Pi after replacing UNKNOWN values with confirmed values. It implements `scripts/stm32/reset.sh` on Mac; an absolute tool path avoids noninteractive PATH differences.

```bash
#!/usr/bin/env bash
set -euo pipefail
MAC_DEST='UNKNOWN'
MAC_CHECKOUT='UNKNOWN'
MAC_OPENOCD='UNKNOWN'
if [[ "$MAC_DEST" == UNKNOWN || "$MAC_CHECKOUT" == UNKNOWN || "$MAC_OPENOCD" == UNKNOWN ]]; then
  echo 'Configure confirmed Mac destination, checkout and OpenOCD path' >&2
  exit 2
fi
exec ssh -o BatchMode=yes -o ConnectTimeout=10 "$MAC_DEST" \
  "cd '$MAC_CHECKOUT' && '$MAC_OPENOCD' -f interface/stlink.cfg -f target/stm32f4x.cfg -c 'init; reset run; shutdown'"
```

Run `bash /home/richard/osbuild/rearm_via_mac.sh` on Pi and retain output/status. Gate: OpenOCD identifies the intended STM32/ST-LINK and reset completes with exit 0. Failure is fatal; never replace reset with `true` or append `|| true`. This resets, does not flash, and bypasses healthy-interval rearm; it does not qualify that interval.

Then run idle and loaded pilots with page 19 commands in fresh output directories, including loaded input FIFO / bridge FIFO and input FIFO / bridge latest. Gate: new post-reset FRESH STATE_EVENT, `fresh_start.json`, `window_start_ns` and passing v2 checks. Inspect `rearm.log` and `pipeline.log`. Missing FRESH/window fails even after reset exit 0; retain failures and investigate. The six historical timeouts alone do not establish root cause. No SSH setup, reset or physical pilot was executed during this repair.
