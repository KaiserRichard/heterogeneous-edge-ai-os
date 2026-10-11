#!/usr/bin/env bash
# Compatibility entry point: p0_cyclictest.sh <new-outdir> [reps] [measurement-seconds]
set -euo pipefail
exec bash "$(dirname "${BASH_SOURCE[0]}")/cyclictest_campaign.sh" P0 "$@"
