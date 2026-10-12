#!/usr/bin/env bash
# Real Pi + STM32 only. No commits, pushes, or firmware changes.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "$repo/tools/experiments/e4_campaign.py" "$@"
