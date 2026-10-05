#!/usr/bin/env bash
set -euo pipefail

# build_and_test_host.sh
# Builds and runs host-side test suite on macOS / Linux.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Building host targets with CMake ==="
cmake -S "${REPO_ROOT}" -B "${REPO_ROOT}/build"
cmake --build "${REPO_ROOT}/build"

echo "=== Running CTest suite ==="
ctest --test-dir "${REPO_ROOT}/build" --output-on-failure

echo "=== Running host test binaries directly ==="
"${REPO_ROOT}/build/test_protocol"
"${REPO_ROOT}/build/test_supervisor"
"${REPO_ROOT}/build/test_workload"

echo "=== Host test verification completed successfully! ==="
