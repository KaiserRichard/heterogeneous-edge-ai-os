#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 5 || ! "$2" =~ ^[0-9]+$ || ! "$3" =~ ^[0-9]+$ || ! "$4" =~ ^[0-9]+$ ]]; then
  echo 'Usage: fault_inject.sh kill|stop|hog BRIDGE_PID DURATION_MS BRIDGE_CORE CSV' >&2
  exit 2
fi
[[ "$1" == kill || "$1" == stop || "$1" == hog ]] || { echo 'unknown fault' >&2; exit 2; }
if [[ "$1" == hog && $EUID != 0 ]]; then
  echo 'SCHED_FIFO hog needs sudo: sudo scripts/pi/fault_inject.sh hog PID MS CORE CSV' >&2
  exit 2
fi
exec python3 "$(dirname "${BASH_SOURCE[0]}")/uart_tools.py" fault "$@"
