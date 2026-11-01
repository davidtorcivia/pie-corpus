#!/bin/zsh
# After an RL run: wait for its trainer to exit, then generate and score the frozen v1 and v2 prompt sets with the
# SFT model alone (baseline) and with checkpoints of the run, through the same mlx_lm path (eval_ckpt.py).
#   training/rl/after_run.sh NAME [CKPT ...]        CKPT: 0000100 0000250 ... or final (default: 0000100 0000250 final)
# Writes RUN/eval/generations-<set>-<ckpt>.jsonl and scores-*.json; RUN/eval/summary.txt
set -uo pipefail
NAME=$1; shift
CKPTS=(${@:-0000100 0000250 final})
HERE=${0:A:h}; ROOT=${HERE:h:h}
RUN=/Users/david/AI/pie-runs/rl/runs/$NAME
PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
MODEL=$(awk '/^model:/{print $2}' $RUN/config.yaml)
while kill -0 $(cat $RUN/pid) 2>/dev/null; do sleep 60; done
mkdir -p $RUN/eval
for c in base $CKPTS; do
  case $c in
    base) AD=() ;;
    final) AD=(--adapter $RUN/adapters/adapters.safetensors) ;;
    *) AD=(--adapter $RUN/adapters/${c}_adapters.safetensors) ;;
  esac
  for set in v1 drills_v2; do
    f=$ROOT/training/gen_prompts_$set.jsonl
    out=$RUN/eval/generations-$set-$c.jsonl
    [ -s $out ] || caffeinate -i $PY -I $HERE/eval_ckpt.py --model $MODEL $AD --prompts $f --out $out
    (cd $ROOT && UV_CACHE_DIR=/tmp/pie-uv-cache uv run --quiet python -I training/score_generations.py $out) >> $RUN/eval/summary.txt 2>&1
  done
done
echo "$(date '+%F %T') after_run done" >> $RUN/eval/summary.txt
