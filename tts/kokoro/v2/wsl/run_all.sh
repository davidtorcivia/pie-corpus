#!/bin/bash
# The Kokoro v2 training run (tr-desktop, WSL): Stage 1, then Stage 2. Rerun this script to resume after a stop or a
# crash: a finished stage (its "done" event) is skipped, an unfinished one resumes from its last.pth.
#   stop:   powershell -File Q:\AI\PIE\train\kokoro\wsl\stop_stage.ps1 -Name stage1|stage2   (saves, exits 0)
#   start/resume: powershell -File Q:\AI\PIE\train\kokoro\wsl\launch.ps1 -Task PIE-kokoro-v2 -Cmd run_all.sh
# Speed settings (2026-11-08 benchmarks, tts/kokoro/v2/README.md): Stage 1 batch 12, Stage 2 batch 8, activation
# checkpointing on decoder/mpd/msd (exact), TF32, no anomaly detection.
W=/mnt/q/AI/PIE/train/kokoro/wsl; R=/mnt/q/AI/PIE/runs/kokoro-v2
CK="PIE_CKPT=decoder,mpd,msd"
done_stage() { [ -f $R/$1/metrics.jsonl ] && grep -q '"event": "done"' $R/$1/metrics.jsonl; }
echo "$(date '+%F %T') run_all start" >> $R/run_all.log
if ! done_stage stage1; then
  bash $W/run_stage.sh 1 v2l_stage1 "" "$CK"
  done_stage stage1 || { echo "$(date '+%F %T') stage1 not done (stopped or crashed); stage2 not started" >> $R/run_all.log; exit 1; }
fi
if ! done_stage stage2; then
  bash $W/run_stage.sh 2 v2l_stage2 "" "$CK"
  done_stage stage2 || { echo "$(date '+%F %T') stage2 not done (stopped or crashed)" >> $R/run_all.log; exit 1; }
fi
echo "$(date '+%F %T') run_all finished" >> $R/run_all.log
