#!/bin/bash
# Mirror the Kokoro fine-tune's logs from WSL to a Windows folder for the dashboard's /tts page (training/dashboard.py
# --tts): the \\wsl.localhost share is not visible to the dashboard's task session. Every 20 s: the stage logs, a
# GPU sample (gpu.csv), the checkpoint list. Runs inside WSL (Ubuntu-26.04), e.g. as a scheduled task:
#   wsl.exe -d Ubuntu-26.04 -- bash /mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/tts_monitor.sh
K=~/kokoro-ft/kikiri-tts
OUT=/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/kokoro-monitor
mkdir -p $OUT
while true; do
  for s in stage1 stage2; do [ -f $K/$s.log ] && tr '\r' '\n' < $K/$s.log | grep -a -v '^\s*$' | tail -n 20000 > $OUT/$s.log.tmp && mv $OUT/$s.log.tmp $OUT/$s.log; done
  echo "$(date +%s),$(nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader,nounits | tr -d ' ')" >> $OUT/gpu.csv
  tail -n 5000 $OUT/gpu.csv > $OUT/gpu.csv.tmp && mv $OUT/gpu.csv.tmp $OUT/gpu.csv
  ( cd $K/StyleTTS2 && ls -l --time-style=+%s logs/pie-stage*/epoch_*.pth 2>/dev/null | awk '{print $6, $5, $7}' ) > $OUT/ckpts.txt
  date +%s > $OUT/updated.txt
  sleep 20
done
