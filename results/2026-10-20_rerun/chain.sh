#!/usr/bin/env bash
# 2026-10-20 re-run chain: waits for P1, then PS1 -> E4 -> LA -> E1-E3B.
set -u
cd ~/os-rerun
R=results/2026-10-20_rerun
export HEA_COOLER="Pi 5 active cooler" HEA_GPIO_CHIP=gpiochip4
while pgrep -f /tmp/p1.sh >/dev/null; do sleep 10; done
echo "[$(date -Is)] P1 finished"
bash scripts/pi/run_pipeline.sh --serial /dev/ttyAMA0 --baud 921600 --duration 60 --bridge-cpu 2 --sync-gpio 17 --run-dir $R/PS1/link60_fixed > $R/PS1_fixed.log 2>&1
echo "[$(date -Is)] PS1 rc=$?"; cat $R/PS1/link60_fixed/summary.json
n=$(($(wc -l < $R/PS1/link60_fixed/mcu_status.csv)-1)); echo "mcu_status rows=$n"
[ "$n" -gt 100 ] || { echo "PS1 FAILED: no MCU status"; exit 1; }
sudo -v
bash tools/experiments/e4_campaign.sh $R/E4/e4-real 5 > $R/E4.log 2>&1; echo "[$(date -Is)] E4 rc=$?"
python3 analysis/e4_summary.py $R/E4/e4-real > $R/E4_summary.log 2>&1; echo "E4 summary rc=$?"
for f in F2 F1 F4; do bash tools/la/la_e4_local.sh $R/LA/$f 5 fault=$f > $R/LA_$f.log 2>&1; echo "[$(date -Is)] LA $f rc=$?"; done
PYTHON=/home/richard/osbuild/venv/bin/python bash tools/experiments/e_campaign.sh ALL $R/E123/e-onnx 3 60 --stage onnx --model /home/richard/osbuild/wheels/mobilenetv2-12.onnx > $R/E123.log 2>&1; echo "[$(date -Is)] E123 rc=$?"
python3 analysis/e_summary.py $R/E123/e-onnx > $R/E123_summary.log 2>&1; echo "E123 summary rc=$?"
echo "[$(date -Is)] CHAIN DONE"
