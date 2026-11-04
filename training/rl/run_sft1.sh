#!/bin/zsh
# Gap SFT 1, end to end: the data (make_sft1.py, from data/rl7's pass rates), one pass of supervised LoRA training
# from the latest RL adapter (grpo.py's wrapper: metrics.jsonl, the val-loss stop; its GRPO patches stay idle in SFT
# mode), watchdog and dashboard sync, then the frozen-set evals. Resumable.
#   FROM=<adapter dir> nohup training/rl/run_sft1.sh > /Users/david/AI/pie-runs/rl/sft1.pipeline.log 2>&1 &
# FROM defaults to stage 7's final adapter. Start it only when nothing else uses the GPU (no trainer, eval or omlx).
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
NAME=sft1-nemotron-gaps; RUNS=/Users/david/AI/pie-runs/rl/runs
DS=/Users/david/AI/pie-runs/rl/data/sft1
FROM=${FROM:-$RUNS/rl7-nemotron-band/adapters}
say() { echo "$(date '+%F %T') $*"; }
pgrep -f omlx-server >/dev/null && { say "omlx-server is running: stop it first"; exit 1; }
pgrep -f "grpo.py|eval_ckpt.py|after_run.sh" >/dev/null && { say "a trainer or eval is running: wait for it"; exit 1; }
[ -s $FROM/adapters.safetensors ] || { say "no adapter at $FROM"; exit 1; }
[ -s $DS/train.jsonl ] || (cd $ROOT && UV_CACHE_DIR=/Users/david/AI/pie-runs/rl/uv-cache uv run --quiet python -I training/rl/make_sft1.py --out $DS)
pgrep -f "sync_dashboard.sh $NAME" >/dev/null || { nohup $HERE/sync_dashboard.sh $NAME /Users/david/AI/pie-runs/rl/sft1.pipeline.log $DS > $RUNS/$NAME.sync.log 2>&1 & }
pgrep -f "watch.sh $NAME" >/dev/null || { nohup $HERE/watch.sh $NAME > $RUNS/$NAME.watch.log 2>&1 & }
if [ ! -f $RUNS/$NAME/pid ]; then
  n=$(wc -l < $DS/train.jsonl); iters=$(( (n + 7) / 8 ))
  cfg=$RUNS/$NAME.config.yaml
  sed -e "s/^iters: .*/iters: $iters/" \
      -e "s/^lr_schedule: .*/lr_schedule: {name: cosine_decay, arguments: [1.0e-5, $(( iters - 20 )), 1.0e-6], warmup: 20}/" \
      $HERE/sft1.yaml > $cfg
  say "train: $n examples, $iters steps from $FROM"
  cd $ROOT && PIE_VAL_STOP=1.5 $HERE/run.sh $NAME $cfg --resume-adapter-file $FROM/adapters.safetensors
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NAME 0000200 0000400 final
say "pipeline done"
