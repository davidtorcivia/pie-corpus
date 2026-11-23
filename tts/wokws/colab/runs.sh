# gʷerh runs the Colab kit can start or resume: trainer arguments per run (sourced by vm_run.sh).
# A run resumes from ckpt/<run>/last.pt in the private dataset repo; a new fork (no ckpt/<run>/ yet) starts from
# ckpt/<INIT>/last.pt. Checkpoints go back to ckpt/<run>/.
#   g2, g2f : the desktop runs (batch 4, resblock checkpointing), kept resumable as they were.
#   g3, g3f : the Colab A/B (2026-11-23): both forked from g2 at step 177,729, identical but for female oversampling
#             in g3f; G4 settings: no generator checkpointing (+8% clips/s), batch 4 (the G4 benchmark: clips/s is flat
#             from batch 4 to 24, so a bigger batch only means fewer, slower steps), LR unchanged, fp32; held-out set
#             balanced over the four voices (8 each) and scored per voice / male / female; MAX_STEPS per launch.
BATCH=${BATCH:-4}; MEM_FRAC=${MEM_FRAC:-0.9}; MAX_STEPS=${MAX_STEPS:-40000}
case "$RUN" in
  g2)  INIT=g2;  ARGS="--batch 4 --gen_checkpoint 1 --pred_mel wB4b8000 --pred_prob 0.5" ;;
  g2f) INIT=g2f; ARGS="--batch 4 --gen_checkpoint 1 --pred_mel wB4b8000 --pred_prob 0.5 --voice_weight W02=2,VALERIA=1.5" ;;
  g3)  INIT=g2;  ARGS="--batch $BATCH --gen_checkpoint 0 --val_per_voice 8 --pred_mel wB4b8000 --pred_prob 0.5" ;;
  g3f) INIT=g2;  ARGS="--batch $BATCH --gen_checkpoint 0 --val_per_voice 8 --pred_mel wB4b8000 --pred_prob 0.5 --voice_weight W02=2,VALERIA=1.5" ;;
  *)   echo "unknown run $RUN"; exit 2 ;;
esac
COMMON="--mem_frac $MEM_FRAC --max_steps $MAX_STEPS --save_every 2000 --val_every 2000 --log_every 50 --resume"
