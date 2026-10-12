#!/usr/bin/env bash
# Pi-only PTY or physical UART run. No system configuration changes or pushes.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
serial=""
sync_gpio=""
echo_ms=1000
stage=stub
model=""
threads=1
infer_python="${PYTHON:-python3}"
duration=10
policy=fifo
period_ms=100
heartbeat_ms=20
work_us=20000
baud=921600
durations=""
run=""
source_options=()
infer_options=()
bridge_options=()
original_args=("$@")
usage() {
  cat <<'EOF'
Usage: scripts/pi/run_pipeline.sh [--duration SECONDS] [--policy fifo|latest]
  [--period-ms N] [--heartbeat-ms N] [--work-us N | --durations FILE]
  [--stage stub|onnx] [--model PATH] [--threads N]
  [--serial DEVICE] [--sync-gpio N] [--echo-ms N] [--baud N] [--run-dir PATH] [--drain-seconds N]
  [--source-priority N] [--source-cpu N] [--infer-priority N] [--infer-cpu N]
  [--bridge-priority N] [--bridge-cpu N]
Defaults: stub stage, 1 ONNX thread, 10 s, FIFO, source 100 ms, heartbeat 20 ms, work 20000 CPU us, 921600 baud.
PYTHON selects the ONNX interpreter (default python3); ONNX requires --model PATH.
Set HEA_COOLER to record the cooler description. Requires Linux, make, python3; PTY mode also requires socat.
--sync-gpio uses HEA_GPIO_CHIP (default gpiochip0); N is a chip line offset.
EOF
}
drain_seconds=1
while (($#)); do
  case "$1" in
    --help) usage; exit 0 ;;
    --serial|--sync-gpio|--echo-ms|--stage|--model|--threads|--duration|--policy|--period-ms|--heartbeat-ms|--work-us|--durations|--baud|--run-dir|--drain-seconds|--source-priority|--source-cpu|--infer-priority|--infer-cpu|--bridge-priority|--bridge-cpu)
      (($# >= 2)) || { echo "missing value for $1" >&2; exit 2; }
      key="$1"; value="$2"; shift 2
      case "$key" in
        --serial) serial="$value" ;;
        --sync-gpio) sync_gpio="$value" ;;
        --echo-ms) echo_ms="$value" ;;
        --stage) stage="$value" ;;
        --model) model="$value" ;;
        --threads) threads="$value" ;;
        --duration) duration="$value" ;;
        --policy) policy="$value" ;;
        --period-ms) period_ms="$value" ;;
        --heartbeat-ms) heartbeat_ms="$value" ;;
        --work-us) work_us="$value" ;;
        --durations) durations="$value" ;;
        --baud) baud="$value" ;;
        --run-dir) run="$value" ;;
        --drain-seconds) drain_seconds="$value" ;;
        --source-priority) source_options+=(--fifo-priority "$value") ;;
        --source-cpu) source_options+=(--cpu "$value") ;;
        --infer-priority) infer_options+=(--fifo-priority "$value") ;;
        --infer-cpu) infer_options+=(--cpu "$value") ;;
        --bridge-priority) bridge_options+=(--fifo-priority "$value") ;;
        --bridge-cpu) bridge_options+=(--cpu "$value") ;;
      esac ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$duration" =~ ^[1-9][0-9]*$ && ${#duration} -le 5 ]] && ((10#$duration <= 86400)) || {
  echo "--duration must be an integer in 1..86400 seconds" >&2; exit 2;
}
[[ "$drain_seconds" =~ ^[0-9]+$ && ${#drain_seconds} -le 2 ]] || { echo "invalid drain duration" >&2; exit 2; }
[[ "$policy" == fifo || "$policy" == latest ]] || { echo "invalid policy" >&2; exit 2; }
[[ "$stage" == stub || "$stage" == onnx ]] || { echo "invalid stage" >&2; exit 2; }
if [[ "$stage" == onnx ]]; then
  [[ -f "$model" ]] || { echo "--stage onnx requires --model PATH to an existing file" >&2; exit 2; }
  [[ "$threads" =~ ^[1-4]$ ]] || { echo "--threads must be 1..4" >&2; exit 2; }
  command -v "$infer_python" >/dev/null || { echo "missing dependency: $infer_python" >&2; exit 2; }
fi
[[ "$(uname -s)" == Linux ]] || { echo "run_pipeline.sh requires the Linux Pi target; use make -C linux test on macOS" >&2; exit 2; }
for tool in make python3; do command -v "$tool" >/dev/null || { echo "missing dependency: $tool" >&2; exit 2; }; done
if [[ -z "$serial" ]]; then command -v socat >/dev/null || { echo "PTY mode requires socat" >&2; exit 2; }; fi
if [[ -n "$sync_gpio" ]]; then
  [[ "$sync_gpio" =~ ^[0-9]+$ ]] || { echo "invalid GPIO line offset" >&2; exit 2; }
  command -v gpioset >/dev/null || { echo "--sync-gpio requires libgpiod gpioset; see scripts/pi/UART.md" >&2; exit 2; }
fi
if [[ -n "$durations" ]]; then
  durations="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve(strict=True))' "$durations")"
fi
make -C "$repo/linux" all
[[ -n "$run" ]] || run="$repo/results/$(date -u +%Y-%m-%d)/pipeline-$(date -u +%H%M%S)-$$"
mkdir -p "$(dirname "$run")"
mkdir "$run" # Refuse to overwrite an existing run.
run="$(cd "$run" && pwd)"
ipc_dir=""
source_pid=""; infer_pid=""; bridge_pid=""; rx_pid=""; socat_pid=""; timer_pid=""; gpio_pid=""
stop_pid() {
  local pid="${1:-}" i
  [[ -n "$pid" ]] || return 0
  if kill -0 "$pid" 2>/dev/null; then
    kill -TERM "$pid" 2>/dev/null || true
    for ((i=0; i<50; i++)); do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.1
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "process $pid did not stop; sending SIGKILL" >&2
      kill -KILL "$pid" 2>/dev/null || true
    fi
  fi
  wait "$pid"
}
cleanup() {
  local rc=$?
  trap - EXIT INT TERM
  set +e
  stop_pid "$gpio_pid"
  stop_pid "$timer_pid"
  stop_pid "$source_pid"
  stop_pid "$infer_pid"
  stop_pid "$bridge_pid"
  stop_pid "$rx_pid"
  stop_pid "$socat_pid"
  [[ -z "$ipc_dir" ]] || rm -rf "$ipc_dir"
  (cd "$repo" && bash scripts/pi/collect_metadata.sh) > "$run/meta_after.json" 2> "$run/meta_after.stderr.log"
  python3 "$repo/analysis/pipeline_summary.py" "$run" > "$run/summary.json" 2> "$run/summary.stderr.log"
  local summary_rc=$?
  if ((rc == 0 && summary_rc != 0)); then rc=$summary_rc; fi
  if [[ -s "$run/summary.json" ]]; then
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["validity"])' "$run/summary.json" > "$run/validity"
  else echo "UNKNOWN: run failed before summary" > "$run/validity"; fi
  printf '%s\n' "$rc" > "$run/exit_code"
  if ((rc == 0)); then touch "$run/DONE"; else touch "$run/FAILED"; fi
  echo "Run directory: $run"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%q ' "$0" "${original_args[@]}" > "$run/command.txt"
printf '\n' >> "$run/command.txt"
python3 - "$run" "${HEA_COOLER:-unknown}" "$duration" "$drain_seconds" "$policy" "$period_ms" "$heartbeat_ms" "$work_us" "$baud" "$stage" "$model" "$threads" "$serial" <<'PY'
import json, sys
from pathlib import Path
run, cooler, duration, drain, policy, period, hb, work, baud, stage, model, threads, serial = sys.argv[1:]
config = dict(evidence=("real UART: UNVERIFIED ON HARDWARE" if serial else "software PTY stand-in, no physical UART/STM32"), cooler=cooler,
              duration_seconds=int(duration), drain_seconds=int(drain), policy=policy,
              period_ms=int(period), heartbeat_ms=int(hb), work_us=int(work), baud=int(baud),
              serial=serial or None, stage=stage, model=model if stage == "onnx" else None, threads=int(threads))
(Path(run) / "config.json").write_text(json.dumps(config, indent=2) + "\n")
PY
if [[ "$stage" == stub ]]; then
  if [[ -n "$durations" ]]; then
    cp "$durations" "$run/durations.txt"
    infer_options+=(--durations "$run/durations.txt")
  else infer_options+=(--work-us "$work_us"); fi
fi
(cd "$repo" && bash scripts/pi/collect_metadata.sh) > "$run/meta_before.json" 2> "$run/meta_before.stderr.log"
# Short socket paths avoid the AF_UNIX path-length limit for deeply nested checkouts.
ipc_dir="$(mktemp -d /tmp/hea-pipeline.XXXXXX)"
if [[ -z "$serial" ]]; then
socat -d -d "pty,raw,echo=0,link=$ipc_dir/tx" "pty,raw,echo=0,link=$ipc_dir/rx" > "$run/socat.stdout.log" 2> "$run/socat.stderr.log" & socat_pid=$!
fi
wait_ready() {
  local path="$1" pid="$2" mode="$3" i
  for ((i=0; i<100; i++)); do
    kill -0 "$pid" 2>/dev/null || { echo "startup failed for $path; inspect $run/*.stderr.log" >&2; return 1; }
    if [[ "$mode" == socket && -S "$path" ]] || [[ "$mode" == file && -s "$path" ]] || [[ "$mode" == tty && -e "$path" ]]; then return 0; fi
    sleep 0.05
  done
  echo "startup timed out: $path" >&2; return 1
}
if [[ -z "$serial" ]]; then
wait_ready "$ipc_dir/tx" "$socat_pid" tty
wait_ready "$ipc_dir/rx" "$socat_pid" tty
serial="$ipc_dir/tx"
fi
launch() {
  local name="$1"; shift
  printf '%q ' "$repo/linux/build/$name" "$@" >> "$run/process_commands.txt"
  printf '\n' >> "$run/process_commands.txt"
  "$repo/linux/build/$name" "$@" &
  launched_pid=$!
}
if [[ -n "$socat_pid" ]]; then
launch hea_rx --serial "$ipc_dir/rx" --baud "$baud" --csv "$run/rx.csv" > "$run/rx.stdout.log" 2> "$run/rx.stderr.log"
rx_pid=$launched_pid
wait_ready "$run/rx.csv" "$rx_pid" file
fi
launch hea_bridge --serial "$serial" --baud "$baud" --socket "$ipc_dir/bridge.sock" --csv "$run/bridge.csv" --status-csv "$run/mcu_status.csv" --echo-csv "$run/echo.csv" --state-events-csv "$run/state_events.csv" --echo-ms "$echo_ms" --policy "$policy" --heartbeat-ms "$heartbeat_ms" "${bridge_options[@]}" > "$run/bridge.stdout.log" 2> "$run/bridge.stderr.log"
bridge_pid=$launched_pid
printf '%s\n' "$bridge_pid" > "$run/bridge.pid"
if [[ -n "$sync_gpio" ]]; then
  python3 "$repo/scripts/pi/uart_tools.py" gpio "$sync_gpio" "$run/gpio.csv" > "$run/gpio.stdout.log" 2> "$run/gpio.stderr.log" & gpio_pid=$!
fi
wait_ready "$ipc_dir/bridge.sock" "$bridge_pid" socket
if [[ "$stage" == stub ]]; then
  launch hea_infer_stub --socket "$ipc_dir/source.sock" --output "$ipc_dir/bridge.sock" --csv "$run/infer.csv" "${infer_options[@]}" > "$run/infer.stdout.log" 2> "$run/infer.stderr.log"
  infer_pid=$launched_pid
else
  onnx_command=("$infer_python" "$repo/linux/inference/infer_server.py" --model "$model" --threads "$threads" --socket "$ipc_dir/source.sock" --output "$ipc_dir/bridge.sock" "${infer_options[@]}")
  printf '%q ' "${onnx_command[@]}" >> "$run/process_commands.txt"
  printf '\n' >> "$run/process_commands.txt"
  "${onnx_command[@]}" > "$run/infer.stdout.log" 2> "$run/infer.stderr.log" &
  infer_pid=$!
fi
wait_ready "$ipc_dir/source.sock" "$infer_pid" socket
launch hea_source --output "$ipc_dir/source.sock" --period-ms "$period_ms" --csv "$run/source.csv" "${source_options[@]}" > "$run/source.stdout.log" 2> "$run/source.stderr.log"
source_pid=$launched_pid
sleep "$duration" & timer_pid=$!
while kill -0 "$timer_pid" 2>/dev/null; do
  for pid in "$source_pid" "$infer_pid" "$bridge_pid" "$rx_pid" "$socat_pid" "$gpio_pid"; do
    [[ -n "$pid" ]] || continue
    kill -0 "$pid" 2>/dev/null || { echo "pipeline process exited early; inspect $run/*.stderr.log" >&2; exit 1; }
  done
  sleep 0.1
done
wait "$timer_pid"; timer_pid=""
stop_pid "$source_pid"; source_pid=""
sleep "$drain_seconds"
stop_pid "$infer_pid"; infer_pid=""
sleep 0.2
stop_pid "$bridge_pid"; bridge_pid=""
sleep 0.2
stop_pid "$rx_pid"; rx_pid=""
# Socat normally reports its requested termination with a nonzero exit status.
stop_pid "$socat_pid" || true; socat_pid=""
