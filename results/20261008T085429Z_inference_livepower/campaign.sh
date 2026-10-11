#!/usr/bin/env bash
# Rerun with live power gating: poll get_throttled + EXT5V every 0.5 s; a run is valid only if live bits 0x1/0x2/0x4/0x8 never set.
export PYTHON=$HOME/osbuild/venv/bin/python
cd $HOME/osbuild/src
( while :; do echo "$(date +%s.%N),$(vcgencmd get_throttled | cut -d= -f2),$(vcgencmd pmic_read_adc EXT5V_V | cut -d= -f2),$(cat /sys/class/thermal/thermal_zone0/temp),$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)"; sleep 0.5; done ) > /home/richard/osbuild/results/20261008T085429Z_inference_livepower/power.csv &
mon=$!
for r in 1 2 3; do
  for c in idle cpu23; do
    echo "$(date +%s.%N) start ${c}_r$r" >> /home/richard/osbuild/results/20261008T085429Z_inference_livepower/marks.txt
    if [ $c = idle ]; then bash linux/inference/sweep.sh /home/richard/osbuild/results/20261008T085429Z_inference_livepower/${c}_r$r -- --model $HOME/osbuild/wheels/mobilenetv2-12.onnx --warmup 50 --runs 1000 > /home/richard/osbuild/results/20261008T085429Z_inference_livepower/${c}_r$r.log 2>&1
    else bash linux/inference/sweep.sh /home/richard/osbuild/results/20261008T085429Z_inference_livepower/${c}_r$r --stress taskset -c 2,3 stress-ng --cpu 2 --timeout 3600s -- --model $HOME/osbuild/wheels/mobilenetv2-12.onnx --warmup 50 --runs 1000 > /home/richard/osbuild/results/20261008T085429Z_inference_livepower/${c}_r$r.log 2>&1; fi
    echo "$(date +%s.%N) end ${c}_r$r" >> /home/richard/osbuild/results/20261008T085429Z_inference_livepower/marks.txt
  done
done
kill $mon; touch /home/richard/osbuild/results/20261008T085429Z_inference_livepower/DONE
