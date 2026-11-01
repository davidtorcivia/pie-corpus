#!/bin/zsh
# RL stage 1b end to end, unattended: candidates, e3's pass rate, training, then the frozen-set eval; the dashboard
# sync runs beside it. Each step is skipped when its output exists, so a rerun resumes.
#   nohup training/rl/pipeline.sh NAME CONFIG > /Users/david/AI/pie-runs/rl/NAME.pipeline.log 2>&1 &
set -euo pipefail
NAME=$1; CFG=$2
HERE=${0:A:h}; ROOT=${HERE:h:h}
PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
DATA=$(awk '/^data:/{print $2}' $CFG); MODEL=$(awk '/^model:/{print $2}' $CFG)
RUN=/Users/david/AI/pie-runs/rl/runs/$NAME
say() { echo "$(date '+%F %T') $*"; }
[ -s $DATA/candidates.jsonl ] || { say candidates; (cd $ROOT && uv run --quiet python -I training/rl/make_rl_prompts.py --mix v2 --out $DATA); }
[ -s $DATA/train.jsonl ] || { say passrate; caffeinate -i $PY -I $HERE/passrate.py --model $MODEL --data $DATA; }
pgrep -f "sync_dashboard.sh $NAME" >/dev/null || { nohup $HERE/sync_dashboard.sh $NAME > $RUN.sync.log 2>&1 & }
if [ ! -f $RUN/pid ]; then say train; $HERE/run.sh $NAME $CFG; fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000100 0000250 0000400 final
say "pipeline done"
