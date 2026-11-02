#!/bin/zsh
# RL stage 4, end to end: data (stage 3's candidates and validation, pass rates re-measured on the merge), training
# from the merge with KL to the merge, watchdog, then the frozen-set evals. Resumable (each step skips done work).
#   nohup training/rl/run_rl4.sh > /Users/david/AI/pie-runs/rl/rl4.pipeline.log 2>&1 &
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
NAME=rl4-from-merge-half; RUNS=/Users/david/AI/pie-runs/rl/runs
MERGE=/Users/david/AI/pie-runs/rl/merges/half
D3=/Users/david/AI/pie-runs/rl/data/rl3; D4=/Users/david/AI/pie-runs/rl/data/rl4
BASE=$(awk '/^model:/{print $2}' $HERE/rl4.yaml)
say() { echo "$(date '+%F %T') $*"; }
mkdir -p $D4
for f in candidates.jsonl valid.jsonl test.jsonl manifest.json; do [ -s $D4/$f ] || cp $D3/$f $D4/$f; done
[ -s $D4/train.jsonl ] || { say passrate; caffeinate -i $PY -I $HERE/passrate.py --model $BASE --adapter $MERGE --data $D4 --mix rl4 --n 2000; }
pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
if [ ! -f $RUNS/$NAME/pid ]; then
  say train
  cd $ROOT && PIE_REF_ADAPTER=$MERGE PIE_KL_STOP=0.3 PIE_VAL_STOP=1.5 \
    $HERE/run.sh $NAME $HERE/rl4.yaml --resume-adapter-file $MERGE/adapters.safetensors
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000100 0000200 final
say "pipeline done"
