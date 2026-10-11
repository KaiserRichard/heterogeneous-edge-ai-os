#!/usr/bin/env bash
# Pi-only scheduling probe. Keep placement/stressors identical across P0 and P1.
set -euo pipefail

usage() {
  echo "Usage: $0 <P0|P1> <new-outdir> [reps=3] [measurement-seconds=600]"
  echo "Optional: COOLER='description of installed cooling'"
}
if [[ ${1:-} == --help || ${1:-} == -h ]]; then usage; exit 0; fi
if [[ $# -lt 2 || $# -gt 4 ]]; then usage >&2; exit 2; fi
profile=$1; out=$2; reps=${3:-3}; secs=${4:-600}
case "$profile" in P0|P1) ;; *) usage >&2; exit 2 ;; esac
for value in "$reps" "$secs"; do
  if [[ ! $value =~ ^[1-9][0-9]*$ || ${#value} -gt 8 ]]; then
    echo "Repetitions and seconds must be positive decimal integers (at most 8 digits)." >&2
    exit 2
  fi
done
if [[ $(uname -s) != Linux ]]; then echo "Run on the Linux Pi target." >&2; exit 2; fi
if [[ $EUID == 0 ]]; then
  echo "Run as a regular user; P1 elevates only cyclictest with sudo." >&2; exit 2
fi
for tool in cyclictest stress-ng taskset vcgencmd python3 lscpu git; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 2; }
done
if [[ $profile == P1 ]]; then command -v sudo >/dev/null; sudo -v; fi
if [[ -e $out ]]; then echo "Refusing to overwrite campaign: $out" >&2; exit 2; fi
mkdir -p "$out"
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
mon=; sp=
cleanup() {
  if [[ -n $sp ]]; then kill "$sp" 2>/dev/null || :; wait "$sp" 2>/dev/null || :; fi
  if [[ -n $mon ]]; then kill "$mon" 2>/dev/null || :; wait "$mon" 2>/dev/null || :; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

meta() {
  (cd "$repo" && bash scripts/pi/collect_metadata.sh) |
    python3 -c 'import json,sys; d=json.load(sys.stdin); d.update(profile=sys.argv[1], cooler=sys.argv[2], cyclictest_command=sys.argv[3]); print(json.dumps(d))' \
      "$profile" "${COOLER:-unknown}" "$command_text"
}
read_or_unknown() { cat "$1" 2>/dev/null || echo unknown; }
monitor() {
  echo 'timestamp,temp_millic,cpu0_khz,throttled'
  while :; do
    throttled=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2) || throttled=unknown
    printf '%s,%s,%s,%s\n' "$(date +%s.%N)" \
      "$(read_or_unknown /sys/class/thermal/thermal_zone0/temp)" \
      "$(read_or_unknown /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)" \
      "${throttled:-unknown}"
    sleep 2
  done
}
{
  stress-ng --version
  cyclictest --version 2>&1 || :
  lscpu
} > "$out/platform.txt"
python3 - "$reps" > "$out/order.txt" <<'PY'
import random
import sys
conditions = ['B0_idle', 'CPU_c23', 'B1_stream_c2', 'C1_cache2M_c2', 'B2_memrate_c23']
order = [f'{condition}:{r}' for r in range(1, int(sys.argv[1]) + 1) for condition in conditions]
random.Random(42).shuffle(order)
print('\n'.join(order))
PY
failed=0
while IFS=: read -r condition repetition; do
  d="$out/${condition}_r${repetition}"
  mkdir "$d"
  cmd=(cyclictest --policy=other -p 0 -m -t1 -a 0 -i 1000 -D "${secs}s" -h 20000 -q)
  if [[ $profile == P1 ]]; then
    cmd=(sudo -n cyclictest --policy=fifo -p 50 -m -t1 -a 0 -i 1000 -D "${secs}s" -h 20000 -q)
  fi
  printf -v command_text '%q ' "${cmd[@]}"
  printf '%s\n' "$command_text" > "$d/cyclictest_cmd.txt"
  meta > "$d/meta_before.json"
  monitor > "$d/thermal.csv" & mon=$!
  stress=()
  case "$condition" in
    CPU_c23) stress=(taskset -c 2,3 stress-ng --cpu 2) ;;
    B1_stream_c2) stress=(taskset -c 2 stress-ng --stream 1 --stream-l3-size 2M --stream-index 0) ;;
    C1_cache2M_c2) stress=(taskset -c 2 stress-ng --cache 1 --cache-level 3 --cache-size 2M --cache-no-affinity) ;;
    B2_memrate_c23) stress=(taskset -c 2,3 stress-ng --memrate 2 --memrate-bytes 64M) ;;
  esac
  if [[ ${#stress[@]} -gt 0 ]]; then
    stress+=(--timeout "$((secs + 10))s" --metrics-brief)
    printf '%q ' "${stress[@]}" > "$d/stress_cmd.txt"
    printf '\n' >> "$d/stress_cmd.txt"
    "${stress[@]}" > "$d/stress.log" 2>&1 & sp=$!
    sleep 5
  fi
  rc=0
  "${cmd[@]}" > "$d/cyclictest_hist.txt" 2> "$d/cyclictest.err" || rc=$?
  echo "$rc" > "$d/exit_code"
  if [[ $rc -ne 0 ]]; then failed=1; fi
  if [[ -n $sp ]]; then
    stress_rc=0
    wait "$sp" || stress_rc=$?
    echo "$stress_rc" > "$d/stress_exit_code"
    if [[ $stress_rc -ne 0 ]]; then failed=1; fi
    sp=
  fi
  kill "$mon" 2>/dev/null || :
  wait "$mon" 2>/dev/null || :
  mon=
  meta > "$d/meta_after.json"
  sleep 5
done < "$out/order.txt"
if [[ $failed -ne 0 ]]; then echo "Campaign has failed runs; inspect raw errors." >&2; exit 1; fi
touch "$out/DONE"
