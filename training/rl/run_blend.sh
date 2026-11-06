#!/bin/zsh
# Blend rl6b's adapter with stage 8's (training/rl/blend_adapters.py, exact: a·ΔW_rl6b + (1-a)·ΔW_rl8) and measure the
# blend on everything stage 8's bar used: v1 and drills_v2 (as after_run.sh), the vocabulary pilot's held-out
# sentences and bare prompts (as run_rl8.sh), and dialogue against rl8 with the Opus judge (dialogue_compare.py).
#   training/rl/run_blend.sh 0.5          (omlx stopped; nothing else on the GPU)
# Writes runs/blend-rl6b-rl8-aNN/{adapters,eval}, data/vocab1/eval-blend-aNN/score.txt, data/dialogue_cmp/*-aNN*
set -euo pipefail
A=$1; TAG=a${${A#0.}[1,2]}
HERE=${0:A:h}; ROOT=${HERE:h:h}
RUNS=/Users/david/AI/pie-runs/rl/runs; DV=/Users/david/AI/pie-runs/rl/data/vocab1; DC=/Users/david/AI/pie-runs/rl/data/dialogue_cmp
M=/Users/david/AI/PIE-nemotron35-e3-oQ5e; PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
UVR=(env UV_CACHE_DIR=/Users/david/AI/pie-runs/rl/uv-cache uv run --quiet --group translator python -I)
NAME=blend-rl6b-rl8-$TAG; RUN=$RUNS/$NAME; AD=$RUN/adapters
say() { echo "$(date '+%F %T') $*"; }
mkdir -p $RUN/eval
[ -s $AD/adapters.safetensors ] || caffeinate -i $PY -I $HERE/blend_adapters.py \
  $RUNS/rl6b-resume50/adapters/adapters.safetensors $RUNS/rl8-nemotron-vocab/adapters/adapters.safetensors $A $AD
say "blend $A ready"
for set in v1 drills_v2; do
  out=$RUN/eval/generations-$set-final.jsonl
  [ -s $out ] || caffeinate -i $PY -I $HERE/eval_ckpt.py --model $M --adapter $AD --prompts $ROOT/training/gen_prompts_$set.jsonl --out $out
  (cd $ROOT && UV_CACHE_DIR=/Users/david/AI/pie-runs/rl/uv-cache uv run --quiet python -I training/score_generations.py $out) >> $RUN/eval/summary.txt 2>&1
done
say "v1 and drills_v2 scored"
out=$DV/eval-blend-$TAG; mkdir -p $out
[ -s $out/test.jsonl ] || caffeinate -i $PY -I $HERE/eval_ckpt.py --model $M --adapter $AD --prompts $DV/heldout.jsonl --out $out/test.jsonl --batch 16
for s in words control; do
  d=$out/$s; mkdir -p $d; cp $DV/$s/candidates.jsonl $DV/$s/manifest.json $d/
  [ -s $d/passrate.jsonl ] || PIE_RL_JUDGE_LOG=$d/passrate-judge.jsonl caffeinate -i $PY -I $HERE/passrate.py \
    --model $M --adapter $AD --data $d --mix rl7 --full --n 1000 --batch 256 || true
done
(cd $ROOT && $UVR training/rl/score_vocab1.py $out/test.jsonl --pass $out/words $out/control) | tee $out/score.txt
say "vocabulary measured"
[ -s $DC/gen-$TAG.jsonl ] || caffeinate -i $PY -I $HERE/eval_ckpt.py --model $M --adapter $AD --prompts $DC/prompts.jsonl --out $DC/gen-$TAG.jsonl
$PY -I $HERE/dialogue_compare.py judge $DC/gen-rl8.jsonl $DC/gen-$TAG.jsonl --names rl8 $TAG -o $DC/judge-rl8-$TAG.json | tee $DC/judge-rl8-$TAG.txt
say "pipeline done"
