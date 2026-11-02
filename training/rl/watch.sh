#!/bin/zsh
# Watchdog for an RL run, independent of any Claude session: every 5 minutes, check the trainer is alive and that
# metrics.jsonl or train.log moved in the last 15 minutes; on a crash or stall, write ALERT lines to RUN.watch.log
# and post a macOS notification. Exits once the trainer has exited and after_run's summary says done.
#   nohup training/rl/watch.sh NAME > /Users/david/AI/pie-runs/rl/runs/NAME.watch.log 2>&1 &
# Added 2026-11-02 after rl3's trainer died unnoticed for 11 hours (docs/research/rl-lessons.md).
set -uo pipefail
NAME=$1; RUN=/Users/david/AI/pie-runs/rl/runs/$NAME
say() { echo "$(date '+%F %T') $*"; }
alert() { say "ALERT $*"; osascript -e "display notification \"$*\" with title \"PIE RL $NAME\"" >/dev/null 2>&1; }
until [ -f $RUN/pid ]; do sleep 30; done
warned=0
while true; do
  now=$(date +%s)
  age=$(( now - $(stat -f %m $RUN/train.log 2>/dev/null || echo 0) ))
  step=$(grep -o '"iteration": [0-9.]*' $RUN/metrics.jsonl 2>/dev/null | tail -1 | grep -o '[0-9]*' | head -1)
  if kill -0 $(cat $RUN/pid) 2>/dev/null; then
    if (( age > 900 )); then (( warned )) || alert "stalled: train.log idle ${age}s at step ${step:-?}"; warned=1
    else warned=0; say "ok step ${step:-?}, log age ${age}s"; fi
  else
    if grep -q '"event": "done"' $RUN/metrics.jsonl 2>/dev/null; then say "trainer finished at step ${step:-?}"
    else alert "trainer died at step ${step:-?}"; fi
    grep -q 'after_run done' $RUN/eval/summary.txt 2>/dev/null && { say "evals done"; exit 0; }
  fi
  sleep 300
done
