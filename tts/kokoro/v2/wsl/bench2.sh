#!/bin/bash
# Stage 2 speed benchmark (WSL), fp32/TF32, joint (SLM-adversarial) training on from the first step as in epochs 4-10.
B=/mnt/q/AI/PIE/runs/kokoro-v2/bench2-wsl; W=/mnt/q/AI/PIE/train/kokoro/wsl
FS="PIE_FIRST_STAGE=/mnt/q/AI/PIE/runs/kokoro-v2/smoke1/first_stage.pth;PIE_JOINT_EPOCH=0"
D="decoder,mpd,msd"
while read -r name envs; do
  [ -z "$name" ] && continue
  [ -f $B/$name/metrics.jsonl ] && grep -q '"train"' $B/$name/metrics.jsonl && continue
  rm -rf $B/$name
  bash $W/run_stage.sh 2 v2l_stage2 $B/$name "PIE_FRESH=1;PIE_BENCH=1;PIE_EPOCHS=1;PIE_LOG_DIR=$B/$name;$FS;$envs"
done <<LIST
b3-eager PIE_BATCH=3;PIE_MAX_STEPS=60
b6-ckpt PIE_BATCH=6;PIE_MAX_STEPS=50;PIE_CKPT=$D
b8-ckpt PIE_BATCH=8;PIE_MAX_STEPS=40;PIE_CKPT=$D
b12-ckpt PIE_BATCH=12;PIE_MAX_STEPS=30;PIE_CKPT=$D
b16-ckpt PIE_BATCH=16;PIE_MAX_STEPS=24;PIE_CKPT=$D
LIST
touch $B/DONE
