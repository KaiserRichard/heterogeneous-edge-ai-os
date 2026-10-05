#!/usr/bin/env bash
# Run one measurement detached from SSH, with before/after metadata, then push results.
# Usage: run_experiment.sh <name> -- <command...>
#   The command runs with cwd = the run directory, so relative output files land there.
# Status: UNVERIFIED on hardware.
set -euo pipefail

name="${1:?usage: run_experiment.sh <name> -- <command...>}"; shift
[[ "${1:-}" == "--" ]] && shift
[[ $# -gt 0 ]] || { echo "missing command" >&2; exit 2; }

repo="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
run="$repo/experiments/runs/$(date -u +%Y%m%dT%H%M%SZ)_${name}"
mkdir -p "$run"
printf '%q ' "$@" > "$run/command.txt"

inner=$(cat <<INNER
cd "$run"
"$repo/scripts/pi/collect_metadata.sh" > meta_before.json
set +e
$(printf '%q ' "$@") > stdout.log 2> stderr.log
echo \$? > exit_code
set -e
"$repo/scripts/pi/collect_metadata.sh" > meta_after.json
t=\$(jq -r .throttled meta_after.json)
if [[ "\$t" == "unavailable" ]]; then echo UNKNOWN > validity
elif [[ "\$t" != "0x0" ]]; then echo "INVALID throttled=\$t" > validity
else echo OK > validity; fi
cd "$repo"
git add -f "$run" && git commit -qm "run: $(basename "$run")" && git push -q || echo "push failed; results kept locally" >> "$run/validity"
INNER
)

# tmux keeps the run alive if SSH drops; attach with: tmux attach -t <name>
tmux new-session -d -s "$name" "bash -c $(printf '%q' "$inner")"
echo "started in tmux session '$name' -> $run"
