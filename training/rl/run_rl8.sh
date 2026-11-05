#!/bin/zsh
# RL stage 8 (2026-11-05): GRPO on top of the vocabulary pilot's SFT (vocab1-nemotron final), to repair the EN->PIE
# drift it brought (v1 chrF 73.09 -> 71.31) while keeping the words it taught (never-right 78 -> 2). Stage 6's
# prompts (data/rl6/train.jsonl: translations both ways, dialogue, vocabulary, drills) plus, twice each, the bare
# prompts of the pilot's trained words it does not yet always get right; stage 6's validation. KL to the starting
# policy (PIE_REF_START: the pilot adapter), not to e3, which lacks the words. 150 steps (~8 h at stage 6's pace).
# Then the frozen sets and the pilot's measurements (held-out sentences, bare prompts of trained and control words).
#   nohup training/rl/run_rl8.sh > /Users/david/AI/pie-runs/rl/rl8.pipeline.log 2>&1 &
# Start it only when nothing else uses the GPU (no trainer, eval or omlx).
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
NAME=rl8-nemotron-vocab; RUNS=/Users/david/AI/pie-runs/rl/runs
D6=/Users/david/AI/pie-runs/rl/data/rl6; DV=/Users/david/AI/pie-runs/rl/data/vocab1; D8=/Users/david/AI/pie-runs/rl/data/rl8
FROM=$RUNS/vocab1-nemotron/adapters
M=/Users/david/AI/PIE-nemotron35-e3-oQ5e; PY=/Users/david/AI/pie-runs/rl/.venv/bin/python
UVR=(env UV_CACHE_DIR=/Users/david/AI/pie-runs/rl/uv-cache uv run --quiet --group translator python -I)
ITERS=150
say() { echo "$(date '+%F %T') $*"; }
pgrep -f omlx-server >/dev/null && { say "omlx-server is running: stop it first"; exit 1; }
pgrep -f "grpo.py|eval_ckpt.py|passrate.py" >/dev/null && { say "a trainer or eval is running: wait for it"; exit 1; }
[ -s $FROM/adapters.safetensors ] || { say "no adapter at $FROM"; exit 1; }

if [ ! -s $D8/train.jsonl ]; then
  mkdir -p $D8
  $PY -I - $D6 $DV $D8 <<'EOF'
import json, sys
from pathlib import Path
d6, dv, d8 = map(Path, sys.argv[1:])
rows = d6.joinpath("train.jsonl").read_text("utf-8").splitlines()
cands = dv.joinpath("words/candidates.jsonl").read_text("utf-8").splitlines()
rates = [json.loads(l) for l in dv.joinpath("eval-final/words/passrate.jsonl").read_text("utf-8").splitlines()]
weak = [cands[r["i"]] for r in rates if sum(r["scores"]) / len(r["scores"]) <= 0.8]
d8.joinpath("train.jsonl").write_text("\n".join(rows + weak + weak) + "\n", "utf-8")
for f in ("valid.jsonl", "test.jsonl"):
    d8.joinpath(f).write_text(d6.joinpath(f).read_text("utf-8"), "utf-8")
json.dump({"from": str(d6), "rl6_rows": len(rows), "vocab_words_not_always": len(weak), "vocab_rows": 2 * len(weak)},
          open(d8 / "manifest.json", "w"), indent=1)
print(f"rl8 data: {len(rows)} stage-6 prompts + {2 * len(weak)} vocabulary rows ({len(weak)} words)")
EOF
fi

pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
if [ ! -f $RUNS/$NAME/pid ]; then
  cfg=$RUNS/$NAME.config.yaml
  sed -e "s#^data: .*#data: $D8#" -e "s/^iters: .*/iters: $ITERS/" -e "s/^seed: .*/seed: 20261106/" \
      -e "s/^lr_schedule: .*/lr_schedule: {name: cosine_decay, arguments: [5.0e-6, $ITERS, 5.0e-7], warmup: 0}/" \
      $HERE/rl6.yaml > $cfg
  say "train: $(wc -l < $D8/train.jsonl) prompts, $ITERS steps from $FROM, KL to the starting adapter"
  cd $ROOT && PIE_REF_SHARED=1 PIE_REF_START=1 PIE_KL_STOP=0.3 PIE_VAL_STOP=1.5 $HERE/run.sh $NAME $cfg \
    --resume-adapter-file $FROM/adapters.safetensors
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000050 0000100 final

measure() {   # $1 tag, $2 adapter file: the pilot's held-out sentences and bare prompts (as run_vocab1.sh)
  local out=$DV/eval-$1 ad=$RUNS/$NAME/ckpt-$1; mkdir -p $out $ad
  ln -sf $2 $ad/adapters.safetensors; ln -sf $RUNS/$NAME/adapters/adapter_config.json $ad/adapter_config.json
  [ -s $out/test.jsonl ] || caffeinate -i $PY -I $HERE/eval_ckpt.py --model $M --adapter $ad/adapters.safetensors \
    --prompts $DV/heldout.jsonl --out $out/test.jsonl --batch 16
  for s in words control; do
    local d=$out/$s; mkdir -p $d; cp $DV/$s/candidates.jsonl $DV/$s/manifest.json $d/
    # passrate's selection step fails on a set without every kind of the mix (KeyError); its passrate.jsonl is complete
    [ -s $d/passrate.jsonl ] || PIE_RL_JUDGE_LOG=$d/passrate-judge.jsonl caffeinate -i $PY -I $HERE/passrate.py \
      --model $M --adapter $ad --data $d --mix rl7 --full --n 1000 --batch 256 || true
    [ "$(wc -l < $d/passrate.jsonl 2>/dev/null || echo 0)" -eq "$(wc -l < $d/candidates.jsonl)" ] || { say "passrate $1/$s incomplete"; exit 1; }
  done
  (cd $ROOT && $UVR training/rl/score_vocab1.py $out/test.jsonl --pass $out/words $out/control) | tee $out/score.txt
}
for c in 0000100 final; do
  f=$RUNS/$NAME/adapters/${c}_adapters.safetensors; [ $c = final ] && f=$RUNS/$NAME/adapters/adapters.safetensors
  [ -f $f ] && { say "vocabulary measures $c"; measure rl8-$c $f; }
done
say "pipeline done"
