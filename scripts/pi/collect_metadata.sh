#!/usr/bin/env bash
# Print a JSON snapshot of the platform state that can invalidate a timing run.
# Usage: collect_metadata.sh > meta.json
set -uo pipefail

read_or() { cat "$1" 2>/dev/null || echo "$2"; }

throttled="unavailable"
if command -v vcgencmd >/dev/null 2>&1; then
  throttled="$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2)"
fi

freqs=""
for c in /sys/devices/system/cpu/cpu[0-9]*; do
  freqs+="\"$(basename "$c")\":$(read_or "$c/cpufreq/scaling_cur_freq" null),"
done

cat <<JSON
{
  "utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "host": "$(hostname)",
  "kernel": "$(uname -r)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo unknown)",
  "git_dirty": $(if ! git rev-parse 2>/dev/null; then echo null; elif [ -z "$(git status --porcelain)" ]; then echo false; else echo true; fi),
  "governor": "$(read_or /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor unknown)",
  "cpu_khz": {${freqs%,}},
  "temp_millic": $(read_or /sys/class/thermal/thermal_zone0/temp null),
  "throttled": "$throttled",
  "loadavg": "$(cut -d' ' -f1-3 /proc/loadavg)"
}
JSON
