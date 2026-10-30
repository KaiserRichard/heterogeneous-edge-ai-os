#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo"
python_bin="${PYTHON:-$HOME/course-stage/cn-venv/bin/python3}"
model="${MODEL_PATH:-$HOME/osbuild/wheels/mobilenetv2-12.onnx}"
date_local="$(date +%F)"
t3="$repo/results/${date_local}_os_t3_contention"
t4="$repo/results/${date_local}_os_t4_policy"

[[ -x "$python_bin" ]] || { echo "PYTHON interpreter unavailable: $python_bin" >&2; exit 2; }
[[ -f "$model" ]] || { echo "ONNX model not found: $model" >&2; exit 2; }
"$python_bin" -c 'import numpy, onnxruntime' || {
  echo "PYTHON must provide numpy and onnxruntime" >&2; exit 2;
}
for output in "$t3" "$t4"; do
  if [[ -e "$output" ]]; then echo "Refusing existing results directory: $output" >&2; exit 2; fi
done

mkdir -p "$repo/results"
PYTHON="$python_bin" tools/experiments/e_campaign.sh E2 "$t3" 3 60 --stage onnx --model "$model" --source camera
PYTHON="$python_bin" tools/experiments/e_campaign.sh E3+E3B "$t4" 3 60 --stage onnx --model "$model" --source camera

echo
echo 'OS-T3: compare matched P0/P1 rows per stressor; pass when P1 P99 <= P0 P99 and P1 misses <= 1% for every stressor.'
python3 "$repo/analysis/e_summary.py" "$t3"
python3 - "$t3/summary/per_condition.csv" <<'PYTABLE'
import csv, sys
for row in csv.reader(open(sys.argv[1], newline='')):
    print('\t'.join(row))
PYTABLE
echo
echo 'OS-T4 bridge policy: latest time-average AoI must be lower than FIFO in every run, and FIFO queue must grow without bound.'
python3 "$repo/analysis/e_summary.py" "$t4"
python3 - "$t4/summary/per_condition.csv" <<'PYTABLE'
import csv, sys
for row in csv.reader(open(sys.argv[1], newline='')):
    print('\t'.join(row))
PYTABLE
echo
echo 'OS-T4 input policy (E3B): latest time-average AoI must be lower than FIFO in every run, and FIFO queue must grow without bound.'
python3 "$repo/analysis/e_summary.py" "$t4" --outdir "$t4/summary"
