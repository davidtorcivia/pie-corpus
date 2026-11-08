#!/bin/bash
# stop/resume test, final Stage 1 settings: run, STOP at ~step 30, resume, run to step 60 of the epoch, check the events
W=/mnt/q/AI/PIE/train/kokoro/wsl; D=/mnt/q/AI/PIE/runs/kokoro-v2/resume-test
rm -rf $D; mkdir -p $D
E="PIE_BENCH=1;PIE_EPOCHS=1;PIE_BATCH=12;PIE_CKPT=decoder,mpd,msd;PIE_LOG_DIR=$D"
bash $W/run_stage.sh 1 v2l_stage1 $D "$E" &
until grep -q '"step": 30' $D/metrics.jsonl 2>/dev/null; do sleep 5; done
touch $D/STOP; wait
echo "after stop: exit line: $(grep EXIT $D/console.log | tail -1)"
bash $W/run_stage.sh 1 v2l_stage1 $D "$E;PIE_MAX_STEPS=30"
python3 - <<PY
import json
ev = [json.loads(l) for l in open("$D/metrics.jsonl")]
for e in ev:
    if e["event"] != "train" or e["step"] in (30, 40, 60):
        print({k: e[k] for k in e if k in ("event", "epoch", "step", "iters", "why", "resumed", "start_step", "mel", "seconds", "bytes")})
PY
