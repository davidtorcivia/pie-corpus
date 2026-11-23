# gʷerh runs the Colab kit can resume: trainer arguments per run (sourced by vm_run.sh).
# Each resumes from ckpt/<run>/last.pt in the private dataset repo and pushes its checkpoints back there.
case "$RUN" in
  g2)  ARGS="--pred_mel wB4b8000 --pred_prob 0.5" ;;
  g2f) ARGS="--pred_mel wB4b8000 --pred_prob 0.5 --voice_weight W02=2,VALERIA=1.5" ;;
  *)   echo "unknown run $RUN"; exit 2 ;;
esac
COMMON="--batch 4 --mem_frac 0.9 --save_every 2000 --val_every 2000 --log_every 50 --resume"
