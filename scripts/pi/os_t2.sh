#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
model="${MODEL_PATH:-$HOME/osbuild/wheels/mobilenetv2-12.onnx}"
result_root="${RESULTS_DIR:-$repo/results/$(date -u +%F)_os_t2_infer}"
source_socket=/tmp/hea_src.sock
shm_name=hea_cam
camera_pid=
sink_pid=
temperature_pid=

if [[ ! -f "$model" ]]; then
  echo "model not found: $model" >&2
  exit 2
fi
mkdir -p "$result_root"
if [[ -n "$(find "$result_root" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "results directory is not empty: $result_root" >&2
  exit 2
fi

cleanup() {
  [[ -z "$temperature_pid" ]] || kill "$temperature_pid" 2>/dev/null || true
  [[ -z "$camera_pid" ]] || kill "$camera_pid" 2>/dev/null || true
  [[ -z "$sink_pid" ]] || kill "$sink_pid" 2>/dev/null || true
  [[ -z "$camera_pid" ]] || wait "$camera_pid" 2>/dev/null || true
  [[ -z "$sink_pid" ]] || wait "$sink_pid" 2>/dev/null || true
  rm -f "/dev/shm/$shm_name"
  rm -f "$source_socket"
}
trap cleanup EXIT INT TERM

for threads in 1 2 4; do
  run_dir="$result_root/threads$threads"
  mkdir -p "$run_dir"
  rm -f "$source_socket" "/dev/shm/$shm_name"
  python3 "$repo/scripts/pi/hea_sink.py" "$source_socket" \
    >"$run_dir/sink.log" 2>&1 &
  sink_pid=$!
  for _ in $(seq 1 100); do
    [[ -S "$source_socket" ]] && break
    sleep 0.05
  done
  if [[ ! -S "$source_socket" ]]; then
    echo "hea_sink did not bind $source_socket" >&2
    exit 1
  fi

  camera_command=("$repo/linux/camera/build/hea_cam" --backend libcamera --fps 10
    --width 640 --height 480 --shm "$shm_name" --output "$source_socket" --count 70000)
  printf '%q ' "${camera_command[@]}" > "$run_dir/camera-command.txt"
  printf '\n' >> "$run_dir/camera-command.txt"
  "${camera_command[@]}" >"$run_dir/camera.log" 2>&1 &
  camera_pid=$!

  for _ in $(seq 1 200); do
    [[ -e "/dev/shm/$shm_name" ]] && break
    kill -0 "$camera_pid" 2>/dev/null || break
    sleep 0.05
  done
  if [[ ! -e "/dev/shm/$shm_name" ]]; then
    echo "camera did not create /dev/shm/$shm_name; see $run_dir/camera.log" >&2
    exit 1
  fi

  "$repo/scripts/pi/collect_metadata.sh" > "$run_dir/platform-metadata.json"
  vcgencmd get_throttled > "$run_dir/throttled.before.txt"
  vcgencmd measure_temp > "$run_dir/temp.before.txt"
  {
    printf 'timestamp,temp\n'
    while kill -0 "$camera_pid" 2>/dev/null; do
      printf '%s,%s\n' "$(date -Iseconds)" "$(vcgencmd measure_temp | sed -E "s/^temp=([^']+).*/\1/")"
      sleep 5
    done
  } > "$run_dir/temperature.csv" &
  temperature_pid=$!

  bench_command=(python3 "$repo/linux/inference/infer_bench.py" --model "$model"
    --warmup 1000 --runs 5000 --threads "$threads" --image-source "shm:$shm_name"
    --output "$run_dir/bench")
  printf '%q ' "${bench_command[@]}" > "$run_dir/command.txt"
  printf '\n' >> "$run_dir/command.txt"
  "${bench_command[@]}" > "$run_dir/bench.stdout.log" 2> "$run_dir/bench.stderr.log"

  vcgencmd get_throttled > "$run_dir/throttled.after.txt"
  vcgencmd measure_temp > "$run_dir/temp.after.txt"
  python3 - "$run_dir" "$model" "$threads" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run, model, threads = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
metadata = {
    'scenario': 'OS-T2', 'utc': datetime.now(timezone.utc).isoformat(),
    'threads': threads, 'model': str(Path(model).resolve()),
    'camera': {'backend': 'libcamera', 'fps': 10, 'width': 640, 'height': 480,
               'shm': 'hea_cam', 'count': 70000},
    'inference': {'warmup': 1000, 'runs': 5000, 'image_source': 'shm:hea_cam'},
    'throttled_before': (run / 'throttled.before.txt').read_text().strip(),
    'throttled_after': (run / 'throttled.after.txt').read_text().strip(),
    'temp_before': (run / 'temp.before.txt').read_text().strip(),
    'temp_after': (run / 'temp.after.txt').read_text().strip(),
    'command': (run / 'command.txt').read_text().strip(),
    'camera_command': (run / 'camera-command.txt').read_text().strip(),
}
(run / 'meta.json').write_text(json.dumps(metadata, indent=2) + '\n')
PY
  kill "$temperature_pid" 2>/dev/null || true
  wait "$temperature_pid" 2>/dev/null || true
  temperature_pid=
  kill "$camera_pid" 2>/dev/null || true
  wait "$camera_pid" 2>/dev/null || true
  camera_pid=
  kill "$sink_pid" 2>/dev/null || true
  wait "$sink_pid" 2>/dev/null || true
  sink_pid=
  rm -f "/dev/shm/$shm_name" "$source_socket"
done

python3 - "$result_root" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
print('threads  P50 ms  P95 ms  P99 ms  P99/P50  temp max  throttled before/after')
for threads in (1, 2, 4):
    run = root / f'threads{threads}'
    report = json.loads((run / 'bench' / 'summary.json').read_text())
    infer = report['summary']['inference']
    temps = []
    for path in (run / 'temperature.csv', run / 'temp.before.txt', run / 'temp.after.txt'):
        temps.extend(float(value) for value in re.findall(r'temp=([0-9.]+)', path.read_text()))
        if path.name == 'temperature.csv':
            temps.extend(float(value) for value in re.findall(r',([0-9.]+)', path.read_text()))
    before = (run / 'throttled.before.txt').read_text().strip().split('=')[-1]
    after = (run / 'throttled.after.txt').read_text().strip().split('=')[-1]
    p50 = infer['p50_ns'] / 1e6
    p95 = infer['p95_ns'] / 1e6
    p99 = infer['p99_ns'] / 1e6
    print(f'{threads:>7}  {p50:>6.2f}  {p95:>6.2f}  {p99:>6.2f}  '
          f'{p99 / p50:>7.3f}  {max(temps) if temps else float("nan"):>7.1f} C  {before}/{after}')
PY
