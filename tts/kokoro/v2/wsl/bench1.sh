#!/bin/bash
# Stage 1 speed benchmark (WSL), fp32 (TF32): each variant trains PIE_MAX_STEPS steps from kokoro_base, fresh.
B=/mnt/q/AI/PIE/runs/kokoro-v2/bench1-wsl; W=/mnt/q/AI/PIE/train/kokoro/wsl
D="decoder,mpd,msd"
while read -r name envs; do
  [ -z "$name" ] && continue
  [ -f $B/$name/metrics.jsonl ] && grep -q '"train"' $B/$name/metrics.jsonl && continue      # done already
  rm -rf $B/$name
  bash $W/run_stage.sh 1 v2l_stage1 $B/$name "PIE_FRESH=1;PIE_BENCH=1;PIE_EPOCHS=1;PIE_LOG_DIR=$B/$name;$envs"
done <<LIST
b8-ckpt PIE_BATCH=8;PIE_MAX_STEPS=50;PIE_CKPT=$D
b4-cdisc PIE_BATCH=4;PIE_MAX_STEPS=80;PIE_COMPILE=$D
b12-ckpt PIE_BATCH=12;PIE_MAX_STEPS=40;PIE_CKPT=$D
b6-plain PIE_BATCH=6;PIE_MAX_STEPS=60
b8-ckpt-cdisc PIE_BATCH=8;PIE_MAX_STEPS=60;PIE_CKPT=$D;PIE_COMPILE=$D
LIST
touch $B/DONE
