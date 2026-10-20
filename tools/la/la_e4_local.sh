#!/usr/bin/env bash
# Pi-local variant of la_e4.sh: ST-LINK, FX2 analyzer, UART and GPIO all on the Pi.
# The capture runs on the system under test, pinned away from the bridge core.
set -euo pipefail
[[ $# -ge 2 && $# -le 3 ]] || { echo 'Usage: tools/la/la_e4_local.sh <outdir> <n_faults> [fault=F1|F2|F4]' >&2; exit 2; }
out=$1
count=$2
fault=${3:-F1}; fault=${fault#fault=}
[[ $count =~ ^[0-9]+$ && $count -ge 1 && $count -le 100 ]] || exit 2
case "$fault" in F1|F2|F4) ;; *) exit 2;; esac
root=$(cd "$(dirname "$0")/../.." && pwd)
serial=${LA_SERIAL:-/dev/ttyAMA0}
sigrok=${SIGROK_CLI:-/usr/bin/sigrok-cli}
rate=${LA_SAMPLERATE:-8m}
la_cpu=${LA_CPU:-3}
[[ ! -e $out ]] || { echo 'Output directory already exists' >&2; exit 2; }
command -v st-flash >/dev/null
[[ -x $sigrok ]] || exit 2
mkdir -p "$out"
out=$(cd "$out" && pwd)
printf '{"analyzer_host": "Pi (system under test)", "samplerate": "%s", "sigrok_cpu": %s}\n' "$rate" "$la_cpu" > "$out/la_host.json"
pi_pid= capture_pid= watchdog_pid=
cleanup() {
  [[ -z $watchdog_pid ]] || kill "$watchdog_pid" 2>/dev/null || true
  [[ -z $capture_pid ]] || sudo -n kill "$capture_pid" 2>/dev/null || true
  [[ -z $pi_pid ]] || kill "$pi_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT TERM
for ((i=1; i<=count; i++)); do
  name=$(printf '%s-r%02d' "$fault" "$i")
  local_run="$out/$name"
  mkdir "$local_run"
  pi_run="$root/results/la-$(date +%Y%m%d-%H%M%S)-$$-$i"
  go="$pi_run.go"
  st-flash reset >"$local_run/reset.log" 2>&1
  (cd "$root" && sudo -n python3 tools/experiments/e4_campaign.py "$pi_run" --single "$fault" --marker-gpio 27 --serial "$serial" --rearm-command true --wait-go "$go") >"$local_run/pi.log" 2>&1 &
  pi_pid=$!
  ready=0
  for ((attempt=0; attempt<60; attempt++)); do
    if [[ -f $go.ready ]]; then ready=1; break; fi
    kill -0 "$pi_pid" 2>/dev/null || { wait "$pi_pid"; exit 1; }
    sleep 1
  done
  [[ $ready == 1 ]] || { echo 'Pi did not become ready' >&2; exit 1; }
  # FX2 software rising-edge trigger, 20% pre-trigger, 3 s sample depth.
  sudo -n taskset -c "$la_cpu" "$sigrok" --driver fx2lafw --config "samplerate=$rate:captureratio=20" --triggers D3=r --channels D0,D1,D2,D3 --time 3s --output-file "$local_run/capture.sr" >"$local_run/sigrok.log" 2>&1 &
  capture_pid=$!
  (sleep 30; sudo -n kill "$capture_pid" 2>/dev/null || true) &
  watchdog_pid=$!
  sleep 1
  kill -0 "$capture_pid" 2>/dev/null || { wait "$capture_pid"; exit 1; }
  sudo -n touch "$go"
  wait "$capture_pid" || true; capture_pid=
  kill "$watchdog_pid" 2>/dev/null || true
  wait "$watchdog_pid" 2>/dev/null || true
  watchdog_pid=
  wait "$pi_pid"; pi_pid=
  sudo -n cp -r "$pi_run" "$local_run/pi"
  sudo -n chown -R "$(id -u):$(id -g)" "$local_run"
  "$sigrok" --input-file "$local_run/capture.sr" --output-format vcd --output-file "$local_run/capture.vcd"
done
python3 "$root/tools/la/la_analyze.py" "$out"
