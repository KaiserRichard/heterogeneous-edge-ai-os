#!/usr/bin/env bash
# One-time provisioning of the OS-project Raspberry Pi 5 (Ubuntu Server 24.04 arm64).
# Run on the Pi:  sudo ./scripts/pi/bootstrap.sh   then reboot once.
# Status: UNVERIFIED on hardware.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then echo "run with sudo" >&2; exit 1; fi

apt-get update
apt-get install -y --no-install-recommends \
  build-essential cmake git python3 python3-venv python3-pip \
  stress-ng rt-tests htop tmux picocom socat jq \
  openocd stlink-tools gcc-arm-none-eabi \
  linux-tools-common linux-tools-raspi cpufrequtils

# Optional packages: names differ between releases, failures are non-fatal.
for p in libraspberrypi-bin raspi-config; do
  apt-get install -y --no-install-recommends "$p" || echo "optional package $p not installed"
done

# Serial access for the login user without sudo.
user="${SUDO_USER:-ubuntu}"
usermod -aG dialout,plugdev "$user"

# Enable PL011 UART0 on GPIO14/15 (header pins 8/10) -> /dev/ttyAMA0 on Pi 5.
cfg=/boot/firmware/config.txt
if ! grep -q '^dtparam=uart0=on' "$cfg"; then
  printf '\n# OS project: UART link to STM32\ndtparam=uart0=on\n' >> "$cfg"
fi

echo "Done. Reboot, then check: ls -l /dev/ttyAMA0 && groups $user"
