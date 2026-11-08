#!/bin/bash
# Stage 1 benchmark, round 2: compile (less memory) vs checkpointing at larger batches.
B=/mnt/q/AI/PIE/runs/kokoro-v2/bench1-wsl; W=/mnt/q/AI/PIE/train/kokoro/wsl
D="decoder,mpd,msd"
until [ -f $B/DONE ]; do sleep 20; done
while read -r name envs; do
  [ -z "$name" ] && continue
  [ -f $B/$name/metrics.jsonl ] && grep -q '"train"' $B/$name/metrics.jsonl && continue
  rm -rf $B/$name
  bash $W/run_stage.sh 1 v2l_stage1 $B/$name "PIE_FRESH=1;PIE_BENCH=1;PIE_EPOCHS=1;PIE_LOG_DIR=$B/$name;$envs"
done <<LIST
b8-cdisc PIE_BATCH=8;PIE_MAX_STEPS=60;PIE_COMPILE=$D
b12-cdisc PIE_BATCH=12;PIE_MAX_STEPS=40;PIE_COMPILE=$D
b16-ckpt PIE_BATCH=16;PIE_MAX_STEPS=30;PIE_CKPT=$D
b16-ckpt-cdisc PIE_BATCH=16;PIE_MAX_STEPS=30;PIE_CKPT=$D;PIE_COMPILE=$D
LIST
touch $B/DONE2
