#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 generate_evidence.py
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > build.log 2>&1
swift -module-cache-path .swift-cache /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/render.swift main.pdf preview
