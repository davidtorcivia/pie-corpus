#!/bin/zsh
# RL stage 5, end to end: data (stage 3's candidates and validation, pass rates measured on Nemotron e3), training from
# e3 with KL to e3, watchdog, then the frozen-set evals. Resumable (each step skips done work).
#   nohup training/rl/run_rl5.sh > /Users/david/AI/pie-runs/rl/rl5.pipeline.log 2>&1 &
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
NAME=rl5-nemotron-e3; RUNS=/Users/david/AI/pie-runs/rl/runs
D3=/Users/david/AI/pie-runs/rl/data/rl3; D5=/Users/david/AI/pie-runs/rl/data/rl5
BASE=$(awk '/^model:/{print $2}' $HERE/rl5.yaml)
say() { echo "$(date '+%F %T') $*"; }
mkdir -p $D5
pgrep -f "sync_dashboard.sh $NAME" >/dev/null || { nohup $HERE/sync_dashboard.sh $NAME /Users/david/AI/pie-runs/rl/rl5.pipeline.log $D5 > $RUNS/$NAME.sync.log 2>&1 & }
for f in candidates.jsonl valid.jsonl test.jsonl manifest.json; do [ -s $D5/$f ] || [ ! -f $D3/$f ] || cp $D3/$f $D5/$f; done
[ -s $D5/train.jsonl ] || { say passrate; caffeinate -i $PY -I $HERE/passrate.py --model $BASE --data $D5 --mix rl3 --n 2000 --batch 256 --max-per-kind 700; }
pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
if [ ! -f $RUNS/$NAME/pid ]; then
  say train
  cd $ROOT && PIE_REF_SHARED=1 PIE_KL_STOP=0.3 PIE_VAL_STOP=1.5 $HERE/run.sh $NAME $HERE/rl5.yaml
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000100 0000200 final
say "pipeline done"
