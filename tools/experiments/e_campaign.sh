#!/usr/bin/env bash
# Pi only; measurements and process-local scheduling, no persistent OS changes.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "$repo/tools/experiments/e_campaign.py" "$@"
