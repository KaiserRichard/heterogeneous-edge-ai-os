#!/usr/bin/env bash
# UNVERIFIED ON HARDWARE. Mac owns ST-LINK and FX2; Pi owns UART/GPIO.
set -euo pipefail
dry_run=0
if [[ ${1:-} == --dry-run ]]; then dry_run=1; shift; fi
if ((dry_run)); then set -- "${1:-unused}" "${2:-1}" "${3:-F2}"; fi
[[ $# -ge 2 && $# -le 3 ]] || { echo 'Usage: tools/la/la_e4.sh [--dry-run] <outdir> <n_faults> [fault=F1|F2|F4]' >&2; exit 2; }
out=$1
count=$2
fault=${3:-F1}; fault=${fault#fault=}
[[ $count =~ ^[0-9]+$ && $count -ge 1 && $count -le 100 ]] || exit 2
case "$fault" in F1|F2|F4) ;; *) exit 2;; esac
root=$(cd "$(dirname "$0")/../.." && pwd)
pi=${LA_PI:-richard@192.168.50.2}
pi_repo=${LA_PI_REPO:-/home/richard/heterogeneous-edge-ai-os}
serial=${LA_SERIAL:-/dev/ttyAMA0}
sigrok=${SIGROK_CLI:-/usr/local/bin/sigrok-cli}
# Remote paths are interpolated in remote commands; reject shell metacharacters.
[[ $pi_repo =~ ^/[a-zA-Z0-9_./-]+$ && $serial =~ ^/[a-zA-Z0-9_./-]+$ ]] || exit 2
[[ ! -e $out ]] || { echo 'Output directory already exists' >&2; exit 2; }
command -v st-flash >/dev/null
[[ -x $sigrok ]] || exit 2
if ((dry_run)); then
  "$sigrok" --scan | python3 -c 'import sys; text=sys.stdin.read(); print(text, end=""); sys.exit(0 if "fx2lafw" in text else 1)'
  # Read-only discovery: no GPIO request, edge, reset, flash write or capture.
  ssh -o BatchMode=yes -o ConnectTimeout=10 "$pi" 'sudo -n python3 -' <<'PYDRY'
from pathlib import Path
import os, re, shlex, subprocess
subprocess.run(['gpioset', '--version'], check=True)
matches = []
for chip in sorted(Path('/dev').glob('gpiochip*')):
    info = subprocess.check_output(['gpioinfo', str(chip)], text=True)
    for offset, label, rest in re.findall(r'line\s+(\d+):\s+"([^"]+)"([^\n]*)', info):
        if label == 'GPIO27':
            matches.append((chip, offset, rest))
if len(matches) != 1:
    raise SystemExit(f'expected one GPIO27: {matches}')
chip, offset, rest = matches[0]
if '[used]' in rest or not os.access(chip, os.R_OK | os.W_OK):
    raise SystemExit('GPIO27 is in use or inaccessible')
print('Pi reachable; GPIO27 available (toggle not executed). Would run:')
print(shlex.join(['gpioset', '--mode=time', '--sec=1', str(chip), f'{offset}=1']))
print(shlex.join(['gpioset', str(chip), f'{offset}=0']))
PYDRY
  st-flash read /dev/null 0x08000000 4
  echo 'Dry-run checks passed; GPIO toggling and acquisition still require physical verification.'
  exit 0
fi
mkdir -p "$out"
out=$(cd "$out" && pwd)
remote_pid= capture_pid= watchdog_pid=
cleanup() {
  [[ -z $watchdog_pid ]] || kill "$watchdog_pid" 2>/dev/null || true
  [[ -z $capture_pid ]] || kill "$capture_pid" 2>/dev/null || true
  [[ -z $remote_pid ]] || kill "$remote_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT TERM
for ((i=1; i<=count; i++)); do
  name=$(printf '%s-r%02d' "$fault" "$i")
  local_run="$out/$name"
  mkdir "$local_run"
  # Unique path, retained remotely as original evidence. sudo GPIO access only.
  remote="$pi_repo/results/la-$(date +%Y%m%d-%H%M%S)-$$-$i"
  go="$remote.go"
  st-flash reset >"$local_run/reset.log" 2>&1
  ssh "$pi" "cd '$pi_repo' && sudo -n python3 tools/experiments/e4_campaign.py '$remote' --single '$fault' --marker-gpio 27 --serial '$serial' --rearm-command true --wait-go '$go'" >"$local_run/pi.log" 2>&1 &
  remote_pid=$!
  ready=0
  for ((attempt=0; attempt<60; attempt++)); do
    if ssh "$pi" "test -f '$go.ready'"; then ready=1; break; fi
    kill -0 "$remote_pid" 2>/dev/null || { wait "$remote_pid"; exit 1; }
    sleep 1
  done
  [[ $ready == 1 ]] || { echo 'Pi did not become ready' >&2; exit 1; }
  # FX2 software rising-edge trigger, 20% pre-trigger, 3 s sample depth.
  # No --wait-trigger: it discards the prehistory required for last UART byte.
  "$sigrok" --driver fx2lafw --config samplerate=8m:captureratio=20 --triggers D3=r --channels D0,D1,D2,D3 --time 3s --output-file "$local_run/capture.sr" >"$local_run/sigrok.log" 2>&1 &
  capture_pid=$!
  # Bound a missing trigger; preserve sigrok stderr and partial session.
  (sleep 30; kill "$capture_pid" 2>/dev/null || true) &
  watchdog_pid=$!
  sleep 1
  kill -0 "$capture_pid" 2>/dev/null || { wait "$capture_pid"; exit 1; }
  ssh "$pi" "sudo -n touch '$go'"
  wait "$capture_pid"; capture_pid=
  kill "$watchdog_pid" 2>/dev/null || true
  wait "$watchdog_pid" 2>/dev/null || true
  watchdog_pid=
  wait "$remote_pid"; remote_pid=
  scp -r "$pi:$remote" "$local_run/pi"
  "$sigrok" --input-file "$local_run/capture.sr" --output-format vcd --output-file "$local_run/capture.vcd"
done
python3 "$root/tools/la/la_analyze.py" "$out"
