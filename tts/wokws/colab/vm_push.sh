#!/bin/bash
# On the Colab VM: push <run>'s checkpoints to the private repo while it trains. Each new generator export (stepN.pt,
# small) as it appears; the full resume state (last.pt, ~0.8 GB) and train.log every 30 min; a final push of both once
# the trainer has exited, then the DONE marker colab_check.sh waits for before releasing the VM.
RUN=$1; REPO=disinfozone/pie-voice-train; W=/content/w; R=$W/runs/$RUN; export HF_XET_HIGH_PERFORMANCE=1
settled() { [ -f "$1" ] && [ $(( $(date +%s) - $(stat -c %Y "$1") )) -ge 90 ]; }   # written >= 90 s ago: not mid-save
push() { hf upload $REPO "$1" "ckpt/$RUN/$(basename "$1")" --repo-type dataset --commit-message "$RUN: $(basename "$1")" -q && echo "$(date +%T) pushed $(basename "$1")"; }
seen=""; last=0
while true; do
  for f in $R/step*.pt; do settled "$f" || continue; case " $seen " in *" $f "*) ;; *) push "$f" && seen="$seen $f";; esac; done
  now=$(date +%s)
  if [ -f $W/TRAIN_EXIT ]; then
    sleep 5; for f in $R/step*.pt; do case " $seen " in *" $f "*) ;; *) push "$f";; esac; done
    push $R/last.pt && push $R/train.log && touch $W/DONE; echo "DONE exit=$(cat $W/TRAIN_EXIT)"; exit 0
  fi
  if [ $((now - last)) -ge 1800 ] && settled $R/last.pt; then push $R/last.pt; push $R/train.log; last=$now; fi
  sleep 60
done
