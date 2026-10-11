#!/usr/bin/env bash
# Connected Mac: download a self-contained Python 3.12 Linux aarch64 wheel bundle.
set -euo pipefail
if [[ $# -ne 1 ]]; then
    echo 'Usage: fetch_offline_deps.sh NEW_BUNDLE_DIR' >&2
    exit 2
fi
bundle_dir="$1"
python_bin="${PYTHON:-python3}"
ort_version="${ORT_VERSION:-1.20.1}"
numpy_version="${NUMPY_VERSION:-2.1.3}"
model_ref="${MODEL_REF:-main}"
model_url="https://media.githubusercontent.com/media/onnx/models/$model_ref/validated/vision/classification/mobilenet/model/mobilenetv2-12.onnx"
mkdir -p -- "$(dirname -- "$bundle_dir")"
mkdir -- "$bundle_dir"
bundle_dir="$(cd -- "$bundle_dir" && pwd)"
mkdir -- "$bundle_dir/wheels"
"$python_bin" -m pip download --dest "$bundle_dir/wheels" \
    --platform manylinux_2_28_aarch64 --platform manylinux_2_27_aarch64 \
    --platform manylinux_2_17_aarch64 --platform manylinux2014_aarch64 \
    --implementation cp --python-version 312 --abi cp312 --only-binary=:all: \
    "onnxruntime==$ort_version" "numpy==$numpy_version"
curl --fail --location --retry 3 "$model_url" --output "$bundle_dir/mobilenetv2-12.onnx"
"$python_bin" - "$bundle_dir" "$model_url" "$ort_version" "$numpy_version" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
model = root / 'mobilenetv2-12.onnx'
with model.open('rb') as stream:
    prefix = stream.read(256)
if model.stat().st_size < 1_000_000 or prefix.startswith(b'version https://git-lfs') or prefix.lstrip().startswith(b'<'):
    raise SystemExit('model download is too small, an LFS pointer, or HTML; bundle incomplete')
(root / 'fetch-config.json').write_text(json.dumps({
    'model_url': sys.argv[2], 'onnxruntime': sys.argv[3], 'numpy': sys.argv[4],
    'target': 'Ubuntu 24.04 Linux aarch64 CPython 3.12',
    'platforms': ['manylinux_2_28_aarch64', 'manylinux_2_27_aarch64',
                  'manylinux_2_17_aarch64', 'manylinux2014_aarch64']}, indent=2) + '\n')
lines = []
for path in sorted(root.rglob('*')):
    if path.is_file() and path.name != 'SHA256SUMS':
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        lines.append(f'{digest.hexdigest()}  {path.relative_to(root).as_posix()}\n')
(root / 'SHA256SUMS').write_text(''.join(lines))
PY
printf 'Bundle ready: %s (verify SHA256SUMS on the Pi before installing)\n' "$bundle_dir"
