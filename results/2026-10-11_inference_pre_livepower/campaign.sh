#!/usr/bin/env bash
export PYTHON=$HOME/osbuild/venv/bin/python
cd $HOME/osbuild/src
for r in 1 2 3; do
  bash linux/inference/sweep.sh /home/richard/osbuild/results/20261008T083143Z_inference/idle_r$r -- --model $HOME/osbuild/wheels/mobilenetv2-12.onnx --warmup 50 --runs 1000 > /home/richard/osbuild/results/20261008T083143Z_inference/idle_r$r.log 2>&1
  bash linux/inference/sweep.sh /home/richard/osbuild/results/20261008T083143Z_inference/cpu23_r$r --stress taskset -c 2,3 stress-ng --cpu 2 --timeout 3600s -- --model $HOME/osbuild/wheels/mobilenetv2-12.onnx --warmup 50 --runs 1000 > /home/richard/osbuild/results/20261008T083143Z_inference/cpu23_r$r.log 2>&1
done
touch /home/richard/osbuild/results/20261008T083143Z_inference/DONE
