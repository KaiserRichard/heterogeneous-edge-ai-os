#!/usr/bin/env bash
# Build Raspberry Pi's libcamera fork + rpicam-apps on Ubuntu 24.04 (Pi 5) into $PREFIX.
# Nothing is installed system-wide except apt build dependencies; use `. $PREFIX/env.sh`.
# Needs network and sudo. Safe to re-run (re-uses clones and build dirs).
set -euo pipefail
PREFIX=${PREFIX:-/opt/rpi-cam}
SRC=${SRC:-$HOME/src/rpi-cam}
JOBS=${JOBS:-2}
mkdir -p "$SRC"
# Optional: PROXY=socks5h://127.0.0.1:1080 when the Pi reaches the internet only through
# `ssh -N -R 127.0.0.1:1080 <pi>` from the Mac (bench Ethernet has no route out).
APT_PROXY=()
if [ -n "${PROXY:-}" ]; then
  APT_PROXY=(-o "Acquire::http::Proxy=$PROXY" -o "Acquire::https::Proxy=$PROXY")
  export ALL_PROXY="$PROXY" all_proxy="$PROXY" https_proxy="$PROXY" http_proxy="$PROXY"
fi

sudo DEBIAN_FRONTEND=noninteractive apt-get "${APT_PROXY[@]}" update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get "${APT_PROXY[@]}" install -y --no-install-recommends \
  git g++ cmake meson ninja-build pkg-config python3-yaml python3-ply python3-jinja2 \
  libyaml-dev libgnutls28-dev openssl libdw-dev libunwind-dev libudev-dev libevent-dev \
  libdrm-dev libjpeg-dev libpng-dev libtiff-dev libexif-dev libboost-program-options-dev

cd "$SRC"
[ -d libcamera ] || git clone --depth 1 https://github.com/raspberrypi/libcamera.git
[ -d rpicam-apps ] || git clone --depth 1 https://github.com/raspberrypi/rpicam-apps.git
echo "libcamera $(git -C libcamera rev-parse HEAD)" > "$SRC/versions.txt"
echo "rpicam-apps $(git -C rpicam-apps rev-parse HEAD)" >> "$SRC/versions.txt"

cd "$SRC/libcamera"
[ -d build ] || meson setup build --prefix="$PREFIX" --buildtype=release \
  -Dpipelines=rpi/pisp,rpi/vc4 -Dipas=rpi/pisp,rpi/vc4 -Dv4l2=true -Dgstreamer=disabled \
  -Dtest=false -Dlc-compliance=disabled -Dcam=enabled -Dqcam=disabled \
  -Ddocumentation=disabled -Dpycamera=disabled
nice -n 15 ninja -C build -j"$JOBS"
sudo ninja -C build install

libdir=$(dirname "$(find "$PREFIX" -name libcamera.pc -path '*pkgconfig*' | head -1)")
export PKG_CONFIG_PATH="$libdir${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
cd "$SRC/rpicam-apps"
[ -d build ] || meson setup build --prefix="$PREFIX" --buildtype=release \
  -Denable_libav=disabled -Denable_drm=enabled -Denable_egl=disabled -Denable_qt=disabled \
  -Denable_opencv=disabled -Denable_tflite=disabled -Denable_hailo=disabled
nice -n 15 ninja -C build -j"$JOBS"
sudo ninja -C build install

pkglib=$(dirname "$libdir")
sudo tee "$PREFIX/env.sh" >/dev/null <<EOF
export PATH="$PREFIX/bin:\$PATH"
export LD_LIBRARY_PATH="$pkglib\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export PKG_CONFIG_PATH="$libdir\${PKG_CONFIG_PATH:+:\$PKG_CONFIG_PATH}"
EOF
. "$PREFIX/env.sh"
cam --version 2>&1 | head -1 || true
rpicam-hello --version 2>&1 | head -2 || true
echo "SETUP DONE: next, with the camera plugged in: . $PREFIX/env.sh && rpicam-hello --list-cameras"
