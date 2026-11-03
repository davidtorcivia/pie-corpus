#!/bin/zsh
# Copy RL run logs to tr-desktop for the dashboard's /rl page (Q:\AI\PIE\rl\runs\NAME), every 5 minutes, until the
# run's after_run eval has finished; also deploys the dashboard files (training/dashboard.py, rl.html) and restarts the
# PIE-dashboard task the first time tr-desktop answers. A sleep loop, not a clock: unaffected by the DST change.
#   nohup training/rl/sync_dashboard.sh NAME [PIPELINE_LOG DATA_DIR] &
# With a pipeline log (run_rl5.sh and later) the page also shows the prompt-filter phase before training starts, and
# with the data dir the filter's kept-prompt counts (manifest.json).
NAME=$1; PIPE=${2:-}; DATA=${3:-}
RUN=/Users/david/AI/pie-runs/rl/runs/$NAME
DEST="Q:/AI/PIE/rl/runs/$NAME"
HERE=${0:A:h}
deployed=
while true; do
  if [ -z "$deployed" ] && ssh -o ConnectTimeout=10 tr-desktop "powershell -NoProfile -Command \"New-Item -ItemType Directory -Force '$DEST/eval' | Out-Null\"" 2>/dev/null; then
    scp -q $HERE/../dashboard.py $HERE/../dashboard.html $HERE/../rl.html $HERE/../tts.html "tr-desktop:Q:/AI/PIE/train/" && \
      ssh tr-desktop "schtasks /End /TN PIE-dashboard; Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -match 'dashboard.py' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }; Start-Sleep 2; schtasks /Run /TN PIE-dashboard" >/dev/null 2>&1 && deployed=1
    echo "$(date '+%F %T') deployed dashboard"
  fi
  scp -q $RUN/config.yaml $RUN/metrics.jsonl $RUN/rewards.jsonl "tr-desktop:$DEST/" 2>/dev/null
  [ -n "$PIPE" ] && [ -f $PIPE ] && { grep -v -i warn $PIPE | tail -400 > $RUN.pipeline-tail.log; scp -q $RUN.pipeline-tail.log "tr-desktop:$DEST/pipeline.log" 2>/dev/null; }
  [ -n "$DATA" ] && [ -f $DATA/manifest.json ] && scp -q $DATA/manifest.json "tr-desktop:$DEST/" 2>/dev/null
  [ -f $RUN/eval/summary.txt ] && scp -q $RUN/eval/summary.txt "tr-desktop:$DEST/eval/" 2>/dev/null
  [ -n "$deployed" ] && grep -q "after_run done" $RUN/eval/summary.txt 2>/dev/null && break
  sleep 300
done
