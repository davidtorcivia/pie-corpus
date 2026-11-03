#!/bin/zsh
# RL stage 6, end to end: pass rates of the rl6 candidates on the starting policy, training (about one pass over the
# filtered prompts), watchdog and dashboard sync, then the frozen-set evals. Resumable (each step skips done work).
#   RL6_FROM=<adapter dir, optional> nohup training/rl/run_rl6.sh > /Users/david/AI/pie-runs/rl/rl6.pipeline.log 2>&1 &
# Build the data first: uv run python -I training/rl/make_rl6.py
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
NAME=rl6-nemotron-unseen; RUNS=/Users/david/AI/pie-runs/rl/runs
D6=/Users/david/AI/pie-runs/rl/data/rl6
BASE=$(awk '/^model:/{print $2}' $HERE/rl6.yaml)
FROM=${RL6_FROM:-}
PA=(); RA=(); [ -n "$FROM" ] && { PA=(--adapter $FROM); RA=(--resume-adapter-file $FROM/adapters.safetensors); }   # zsh does not split ${x:+a b}
say() { echo "$(date '+%F %T') $*"; }
[ -s $D6/candidates.jsonl ] || { echo "no candidates: run make_rl6.py"; exit 1; }
pgrep -f "sync_dashboard.sh $NAME" >/dev/null || { nohup $HERE/sync_dashboard.sh $NAME /Users/david/AI/pie-runs/rl/rl6.pipeline.log $D6 > $RUNS/$NAME.sync.log 2>&1 & }
[ -s $D6/train.jsonl ] || { say passrate; caffeinate -i $PY -I $HERE/passrate.py --model $BASE $PA --data $D6 --mix rl6 --n 2000 --batch 256 --max-per-kind 900; }
pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
if [ ! -f $RUNS/$NAME/pid ]; then
  n=$(wc -l < $D6/train.jsonl); iters=$(( (n + 7) / 8 )); (( iters > 250 )) && iters=250
  cfg=$RUNS/$NAME.config.yaml
  sed -e "s/^iters: .*/iters: $iters/" -e "s/^lr_schedule: .*/lr_schedule: {name: cosine_decay, arguments: [5.0e-6, $iters, 5.0e-7], warmup: 0}/" $HERE/rl6.yaml > $cfg
  say "train: $n prompts, $iters steps${FROM:+, from $FROM}"
  cd $ROOT && PIE_REF_SHARED=1 PIE_KL_STOP=0.3 PIE_VAL_STOP=1.5 $HERE/run.sh $NAME $cfg $RA
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000050 0000100 0000150 0000200 final
say "pipeline done"
