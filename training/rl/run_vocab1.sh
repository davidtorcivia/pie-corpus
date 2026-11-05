#!/bin/zsh
# Vocabulary pilot, end to end (make_vocab1.py): baseline on RL stage 6 final (held-out sentences, bare prompts of
# the trained and control words), two passes of SFT from it, the frozen-set evals of the final adapter, then the same
# measurements on it. One GPU job at a time; resumable (each step skips what exists).
#   nohup training/rl/run_vocab1.sh > /Users/david/AI/pie-runs/rl/vocab1.pipeline.log 2>&1 &
# Start it only when nothing else uses the GPU (no trainer, eval or omlx).
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
NAME=vocab1-nemotron; RUNS=/Users/david/AI/pie-runs/rl/runs
DS=/Users/david/AI/pie-runs/rl/data/vocab1
FROM=${FROM:-$RUNS/rl6b-resume50/adapters}
M=/Users/david/AI/PIE-nemotron35-e3-oQ5e; PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
UVR=(env UV_CACHE_DIR=/Users/david/AI/pie-runs/rl/uv-cache uv run --quiet --group translator python -I)
say() { echo "$(date '+%F %T') $*"; }
pgrep -f omlx-server >/dev/null && { say "omlx-server is running: stop it first"; exit 1; }
pgrep -f "grpo.py|eval_ckpt.py|after_run.sh|passrate.py" >/dev/null && { say "a trainer or eval is running: wait for it"; exit 1; }
[ -s $FROM/adapters.safetensors ] || { say "no adapter at $FROM"; exit 1; }
[ -s $DS/train.jsonl ] || (cd $ROOT && $UVR training/rl/make_vocab1.py --out $DS)

measure() {   # $1 tag, $2 adapter dir
  local out=$DS/eval-$1; mkdir -p $out
  [ -s $out/test.jsonl ] || caffeinate -i $PY -I $HERE/eval_ckpt.py --model $M --adapter $2/adapters.safetensors \
    --prompts $DS/heldout.jsonl --out $out/test.jsonl --batch 16
  for s in words control; do
    local d=$out/$s; mkdir -p $d; cp -n $DS/$s/candidates.jsonl $DS/$s/manifest.json $d/
    # passrate's selection step fails on a set without every kind of the mix (KeyError); its passrate.jsonl is complete
    [ -s $d/passrate.jsonl ] || PIE_RL_JUDGE_LOG=$d/passrate-judge.jsonl caffeinate -i $PY -I $HERE/passrate.py \
      --model $M --adapter $2 --data $d --mix rl7 --full --n 1000 --batch 256 || true
    [ "$(wc -l < $d/passrate.jsonl 2>/dev/null || echo 0)" -eq "$(wc -l < $d/candidates.jsonl)" ] || { say "passrate $1/$s incomplete"; exit 1; }
  done
  (cd $ROOT && $UVR training/rl/score_vocab1.py $out/test.jsonl --pass $out/words $out/control) | tee $out/score.txt
}

say "baseline on $FROM"
measure base $FROM
if [ ! -f $RUNS/$NAME/pid ]; then
  n=$(wc -l < $DS/train.jsonl); iters=$(( (2 * n + 7) / 8 ))
  cfg=$RUNS/$NAME.config.yaml
  sed -e "s/^iters: .*/iters: $iters/" \
      -e "s/^lr_schedule: .*/lr_schedule: {name: cosine_decay, arguments: [1.0e-5, $(( iters - 20 )), 1.0e-6], warmup: 20}/" \
      $HERE/vocab1.yaml > $cfg
  say "train: $n examples, two passes, $iters steps from $FROM"
  pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
  cd $ROOT && PIE_VAL_STOP=1.5 $HERE/run.sh $NAME $cfg --resume-adapter-file $FROM/adapters.safetensors
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME final
measure final $RUNS/$NAME/adapters
say "pipeline done"
