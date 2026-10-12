#!/usr/bin/env bash
# Pi only: sweep.sh RUN_ROOT [--stress COMMAND ARG...] [-- BENCH_ARG...]
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"
python_bin="${PYTHON:-python3}"
if [[ $# -lt 1 ]]; then
    echo 'Usage: sweep.sh RUN_ROOT [--stress stress-ng ARG...] [-- BENCH_ARG...]' >&2
    exit 2
fi
run_root="$1"
shift
stress_command=()
if [[ ${1:-} == --stress ]]; then
    shift
    while [[ $# -gt 0 && $1 != -- ]]; do
        stress_command+=("$1")
        shift
    done
    if [[ ${#stress_command[@]} -eq 0 ]]; then
        echo '--stress requires a command' >&2
        exit 2
    fi
fi
if [[ ${1:-} == -- ]]; then shift; fi
for arg in "$@"; do
    case "$arg" in
        --threads|--threads=*|--output|--output=*)
            echo 'sweep owns --threads and --output' >&2; exit 2 ;;
    esac
done
if [[ $(uname -s) != Linux ]]; then
    echo 'sweep requires Linux (Pi platform metadata and setsid)' >&2
    exit 2
fi
mkdir -p -- "$(dirname -- "$run_root")"
mkdir -- "$run_root"  # A new root prevents accidental sample replacement.
run_root="$(cd -- "$run_root" && pwd)"
cd -- "$repo_root"

run_one() (
    threads="$1"
    shift
    run_dir="$run_root/threads-$threads"
    mkdir -- "$run_dir"
    stress_pid=''
    bench_finished=0
    finish() {
        status=$?
        trap - EXIT
        if [[ $bench_finished -ne 1 && $status -eq 0 ]]; then status=1; fi
        bash "$repo_root/scripts/pi/collect_metadata.sh" > "$run_dir/metadata-after.json"
        if [[ -n $stress_pid ]]; then
            if ! kill -0 "$stress_pid" 2>/dev/null; then
                echo 'stressor exited before run completion' >&2
                status=1
            fi
            kill -TERM -- "-$stress_pid" 2>/dev/null || true
            wait "$stress_pid" 2>/dev/null || true
        fi
        "$python_bin" - "$run_dir" "$status" <<'PY'
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
status = int(sys.argv[2])
flags = []
for phase in ('before', 'after'):
    try:
        meta = json.loads((root / f'metadata-{phase}.json').read_text())
        value = meta['throttled']
        if int(value, 16) != 0:
            flags.append(f'{phase}: throttled/history bits {value}')
    except (OSError, ValueError, KeyError, TypeError):
        flags.append(f'{phase}: throttle state unavailable')
if status:
    flags.append(f'run exit status {status}')
(root / 'validity.json').write_text(json.dumps({
    'exit_status': status, 'eligible_for_aggregate': not flags,
    'reasons': flags}, indent=2) + '\n')
PY
        exit "$status"
    }
    trap finish EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    command=("$python_bin" "$script_dir/infer_bench.py" --threads "$threads" --output "$run_dir/bench" "$@")
    printf '%q ' "${command[@]}" > "$run_dir/command.txt"
    printf '\n' >> "$run_dir/command.txt"
    : > "$run_dir/stress-command.txt"
    if [[ ${#stress_command[@]} -gt 0 ]]; then
        printf '%q ' "${stress_command[@]}" > "$run_dir/stress-command.txt"
    fi
    printf '\n' >> "$run_dir/stress-command.txt"
    printf '%s\n' "${COOLER_DESCRIPTION:-unknown}" > "$run_dir/cooler.txt"
    if [[ ${#stress_command[@]} -gt 0 ]]; then
        setsid "${stress_command[@]}" > "$run_dir/stress.log" 2>&1 &
        stress_pid=$!
        sleep 1
        kill -0 "$stress_pid"
    fi
    bash "$repo_root/scripts/pi/collect_metadata.sh" > "$run_dir/metadata-before.json"
    "${command[@]}" > "$run_dir/bench.log" 2>&1
    bench_finished=1
)
for threads in 1 2 3 4; do
    run_one "$threads" "$@"
done
