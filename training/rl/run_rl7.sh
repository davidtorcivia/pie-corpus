#!/bin/zsh
# RL stage 7, end to end: stage 6's candidates and validation copied to data/rl7, pass rates on stage 6's final
# policy with the training reward itself (passrate.py --full, judge included), training (about one pass over the
# band), watchdog and dashboard sync, then the frozen-set evals. Resumable (each step skips done work).
#   nohup training/rl/run_rl7.sh > /Users/david/AI/pie-runs/rl/rl7.pipeline.log 2>&1 &
# Stop omlx first (launchctl bootout gui/501/ai.omlx.serve): a model it loads beside the trainer killed stage 6.
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
NAME=rl7-nemotron-band; RUNS=/Users/david/AI/pie-runs/rl/runs
D6=/Users/david/AI/pie-runs/rl/data/rl6; D7=/Users/david/AI/pie-runs/rl/data/rl7
FROM=$RUNS/rl6b-resume50/adapters
BASE=$(awk '/^model:/{print $2}' $HERE/rl7.yaml)
say() { echo "$(date '+%F %T') $*"; }
pgrep -f omlx-server >/dev/null && { say "omlx-server is running: stop it first"; exit 1; }
mkdir -p $D7
for f in candidates valid valid_full test; do [ -s $D7/$f.jsonl ] || cp $D6/$f.jsonl $D7/; done
[ -s $D7/manifest.json ] || cp $D6/manifest.json $D7/
pgrep -f "sync_dashboard.sh $NAME" >/dev/null || { nohup $HERE/sync_dashboard.sh $NAME /Users/david/AI/pie-runs/rl/rl7.pipeline.log $D7 > $RUNS/$NAME.sync.log 2>&1 & }
if [ ! -s $D7/train.jsonl ]; then
  say "passrate (full reward) on $FROM"
  PIE_RL_JUDGE_LOG=$D7/passrate-judge.jsonl caffeinate -i $PY -I $HERE/passrate.py --model $BASE --adapter $FROM \
    --data $D7 --mix rl7 --full --n 1000 --batch 256 --max-per-kind 500
fi
pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
if [ ! -f $RUNS/$NAME/pid ]; then
  n=$(wc -l < $D7/train.jsonl); iters=$(( (n + 7) / 8 )); (( iters > 250 )) && iters=250
  cfg=$RUNS/$NAME.config.yaml
  sed -e "s/^iters: .*/iters: $iters/" \
      -e "s/^lr_schedule: .*/lr_schedule: {name: cosine_decay, arguments: [1.0e-5, $(( iters - 5 )), 1.0e-6], warmup: 5}/" \
      $HERE/rl7.yaml > $cfg
  say "train: $n prompts, $iters steps from $FROM"
  cd $ROOT && PIE_REF_SHARED=1 PIE_KL_STOP=0.3 PIE_VAL_STOP=1.5 $HERE/run.sh $NAME $cfg \
    --resume-adapter-file $FROM/adapters.safetensors
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000050 0000100 final
say "pipeline done"
