#!/bin/zsh
# Resume RL stage 3 after rl3-mix-vocab-e3's trainer died at step 288 (2026-11-01): a new run, rl3b-resume275-e3,
# from the step-275 adapter for the remaining 225 steps, same config. A new seed reorders the prompts (the old order
# can't be skipped exactly, so some of the 2,200 prompts seen in steps 1-275 recur). Then, one at a time with nothing
# else on the GPU: rl3's checkpoints and rl3b's, on the frozen sets. Watchdog alongside.
#   nohup training/rl/resume_rl3.sh > /Users/david/AI/pie-runs/rl/rl3b.pipeline.log 2>&1 &
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
OLD=rl3-mix-vocab-e3; NEW=rl3b-resume275-e3; RUNS=/Users/david/AI/pie-runs/rl/runs
say() { echo "$(date '+%F %T') $*"; }
pgrep -f "watch.sh $NEW" >/dev/null || { nohup $HERE/watch.sh $NEW > $RUNS/$NEW.watch.log 2>&1 & }
pgrep -f "sync_dashboard.sh $NEW" >/dev/null || { nohup $HERE/sync_dashboard.sh $NEW > $RUNS/$NEW.sync.log 2>&1 & }
if [ ! -f $RUNS/$NEW/pid ]; then
  say train
  cd $ROOT && $HERE/run.sh $NEW $HERE/rl3.yaml --resume-adapter-file $RUNS/$OLD/adapters/0000275_adapters.safetensors \
    --iters 225 --seed 20261102
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NEW 0000100 0000200 final
$HERE/after_run.sh $OLD 0000100 0000250 0000275
say "pipeline done"
