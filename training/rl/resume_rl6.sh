#!/bin/zsh
# Resume RL stage 6 after rl6-nemotron-unseen's trainer died at step 61 (2026-11-03 22:09: an omlx client loaded an
# 87 GB model beside it; omlx is stopped for the run). A new run, rl6b-resume50, from the step-50 adapter for the
# remaining 151 steps, the cosine schedule picked up where step 50 left it (4.35e-6 -> 5e-7) and a new seed (the
# prompt order can't be skipped exactly). Then, one at a time: rl6's step-50 checkpoint and rl6b's on the frozen sets.
#   nohup training/rl/resume_rl6.sh > /Users/david/AI/pie-runs/rl/rl6b.pipeline.log 2>&1 &
set -euo pipefail
HERE=${0:A:h}; ROOT=${HERE:h:h}
OLD=rl6-nemotron-unseen; NEW=rl6b-resume50; RUNS=/Users/david/AI/pie-runs/rl/runs
D6=/Users/david/AI/pie-runs/rl/data/rl6
say() { echo "$(date '+%F %T') $*"; }
pgrep -f "sync_dashboard.sh $NEW" >/dev/null || { nohup $HERE/sync_dashboard.sh $NEW /Users/david/AI/pie-runs/rl/rl6b.pipeline.log $D6 > $RUNS/$NEW.sync.log 2>&1 & }
pgrep -f "watch.sh $NEW" >/dev/null || { nohup $HERE/watch.sh $NEW > $RUNS/$NEW.watch.log 2>&1 & }
if [ ! -f $RUNS/$NEW/pid ]; then
  cfg=$RUNS/$NEW.config.yaml
  sed -e "s/^iters: .*/iters: 151/" -e "s/^seed: .*/seed: 20261105/" \
      -e "s/^lr_schedule: .*/lr_schedule: {name: cosine_decay, arguments: [4.35e-6, 151, 5.0e-7], warmup: 0}/" \
      $RUNS/$OLD.config.yaml > $cfg
  say "train: 151 steps from $OLD step 50"
  cd $ROOT && PIE_REF_SHARED=1 PIE_KL_STOP=0.3 PIE_VAL_STOP=1.5 $HERE/run.sh $NEW $cfg \
    --resume-adapter-file $RUNS/$OLD/adapters/0000050_adapters.safetensors
fi
say "waiting for the trainer, then evaluating"
$HERE/after_run.sh $NEW 0000050 0000100 final
$HERE/after_run.sh $OLD 0000050
say "pipeline done"
