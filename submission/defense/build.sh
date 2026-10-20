#!/bin/sh
# Offline additive rebuild. RERUN_COMPARE_DIR can select a fresh replay output.
set -eu
DECK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$DECK_DIR/../../tools/rerun/build_documents.py"
latexmk -cd -xelatex -interaction=nonstopmode -halt-on-error "$DECK_DIR/main.tex"
