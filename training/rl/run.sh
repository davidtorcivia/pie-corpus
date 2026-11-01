#!/bin/zsh
# Start an RL run in the background, kept awake (caffeinate), logging to /Users/david/AI/pie-runs/rl/runs/NAME.
#   training/rl/run.sh NAME CONFIG.yaml [extra mlx-lm-lora args]
# Stop: kill $(cat /Users/david/AI/pie-runs/rl/runs/NAME/pid)
set -euo pipefail
NAME=$1; CFG=$2; shift 2
HERE=${0:A:h}
DIR=/Users/david/AI/pie-runs/rl/runs/$NAME
mkdir -p $DIR
cp $CFG $DIR/config.yaml
(cd $HERE/../.. && git rev-parse HEAD) > $DIR/commit
PIE_RL_RUN_DIR=$DIR nohup caffeinate -i /Users/david/AI/pie-runs/rl/.venv/bin/python -I $HERE/grpo.py \
  --config $CFG --adapter-path $DIR/adapters "$@" > $DIR/train.log 2>&1 &
echo $! > $DIR/pid
echo "started $NAME pid $(cat $DIR/pid), log $DIR/train.log"
