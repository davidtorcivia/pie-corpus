#!/bin/bash
# Kokoro v2 retrain (2026-11-06): the same kikiri recipe as v10 (base Kokoro-82M, Stage 1 10 epochs batch 6, best by
# validation -> Stage 2 10 epochs batch 4, expandable segments, slmadv max_len 400), on work/final_v2 (repair v2:
# h before e/i as a plain breath, phrase-final r with no breath after it). Resumable: rerun this script and it picks up
# from the last saved epoch of whichever stage is unfinished. VRAM: the whole card stays <= 0.82 with the display's
# ~4.6 GB, so the trainer's own cap is 0.66 (+ ~0.5 GB CUDA context): Stage 1 at batch 4 (v10: 6, peak 22.2 GiB),
# Stage 2 at batch 3 (v10: 4, 22.6 GiB). CPU: 8 threads, 12 loader workers.
# Log: ~/kokoro-ft/kikiri-tts/v2.log   Logs/checkpoints: StyleTTS2/logs/pie-v2-stage{1,2}   Selection: ~/kokoro-ft/select-v2
K=~/kokoro-ft/kikiri-tts; cd $K; . ../venv/bin/activate
W=/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/work
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
log() { echo "$(date '+%F %T') $*" | tee -a $K/v2.log; }
mkdir -p dataset/audio_v2
n=$(ls dataset/audio_v2 | wc -l)
if [ "$n" -lt 3492 ]; then cp -n $W/final_v2/*.wav dataset/audio_v2/; log "audio_v2: $(ls dataset/audio_v2 | wc -l) files"; fi
miss=$(cut -d'|' -f1 training/train_list.txt training/val_list.txt | while read f; do [ -f dataset/audio_v2/$f ] || echo $f; done | wc -l)
[ "$miss" -eq 0 ] || { log "list files missing from audio_v2: $miss; stopping"; exit 1; }
cfg() {  # stage log_dir batch frac-unused  -> configs/config_pie_v2_<stage>.yml
python3 - "$@" <<'PY'
import sys, yaml
st, logdir, bs = sys.argv[1], sys.argv[2], int(sys.argv[3]); extra = sys.argv[4:]
c = yaml.safe_load(open("configs/config_pie.yml"))
c["log_dir"] = logdir; c["batch_size"] = bs; c["epochs_1st"] = 10; c["epochs_2nd"] = 10; c["save_freq"] = 1
c["data_params"].update(train_data="../training/train_list.txt", val_data="../training/val_list.txt", root_path="../dataset/audio_v2", num_workers=12)
if st == "2": c["slmadv_params"]["max_len"] = 400
if extra:
    c.update(pretrained_model=extra[0], load_only_params=False)
    if st == "2": c["second_stage_load_pretrained"] = True
yaml.safe_dump(c, open(f"configs/config_pie_v2_{st}.yml", "w"), allow_unicode=True, sort_keys=False)
PY
}
cd StyleTTS2; L1=logs/pie-v2-stage1; L2=logs/pie-v2-stage2; mkdir -p $L1 $L2
# ---- Stage 1
if [ ! -f $L1/DONE ]; then
  LAST=$(ls $L1/epoch_1st_*.pth 2>/dev/null | sort | tail -1)
  (cd .. && cfg 1 $L1 ${S1_BATCH:-4} $LAST)
  log "Stage 1 ${LAST:+resuming from $LAST}${LAST:-starting}"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PIE_GPU_MEM_FRAC=0.66 accelerate launch --num_processes 1 --mixed_precision no train_first.py --config_path ../configs/config_pie_v2_1.yml >> ../v2-stage1.log 2>&1
  rc=$?; log "Stage 1 exit $rc"
  [ -f $L1/epoch_1st_00009.pth ] || { log "Stage 1 incomplete: rerun to resume"; exit 1; }
  touch $L1/DONE
fi
# ---- best Stage 1 epoch (by the last validation loss logged for each epoch, so a resume does not shift them)
if [ ! -f $L2/first_stage.pth ]; then
  BEST=$(python3 - <<'PY'
import re
v = {}
for n, x in re.findall(r"Epochs: (\d+)\s+Validation loss: ([0-9.]+)", open("../v2-stage1.log").read()): v[int(n)] = float(x)
b = min(v, key=v.get); print(b - 1, v[b], " ".join(f"{k}:{v[k]:.3f}" for k in sorted(v)))
PY
)
  set -- $BEST; IDX=$1; LOSS=$2; shift 2
  F=$L1/$(printf 'epoch_1st_%05d.pth' $IDX)
  log "Stage 1 validation by epoch: $*  -> best $F ($LOSS)"
  [ -f $F ] || { log "best checkpoint $F missing: stopping"; exit 1; }
  cp $F $L2/first_stage.pth.tmp && mv $L2/first_stage.pth.tmp $L2/first_stage.pth
fi
# ---- Stage 2
if [ ! -f $L2/DONE ]; then
  LAST=$(ls $L2/epoch_2nd_*.pth 2>/dev/null | sort | tail -1)
  (cd .. && cfg 2 $L2 ${S2_BATCH:-3} $LAST)
  log "Stage 2 ${LAST:+resuming from $LAST}${LAST:-starting}"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PIE_GPU_MEM_FRAC=0.66 accelerate launch --num_processes 1 --mixed_precision no train_second.py --config_path ../configs/config_pie_v2_2.yml >> ../v2-stage2.log 2>&1
  rc=$?; log "Stage 2 exit $rc"
  [ -f $L2/epoch_2nd_00009.pth ] || { log "Stage 2 incomplete: rerun to resume"; exit 1; }
  touch $L2/DONE
fi
# ---- select among the last epochs (as v10: MCD / log-F0 / duration on the validation lines, voicepacks from audio_v2)
cd $K
if [ ! -f ~/kokoro-ft/select-v2/summary.json ]; then
  sed 's#dataset/audio"#dataset/audio_v2"#g; s#"dataset/audio" /#"dataset/audio_v2" /#g' kokoro_select.py > kokoro_select_v2.py
  grep -c audio_v2 kokoro_select_v2.py | xargs -I{} echo "select script: {} audio_v2 refs" >> v2.log
  PYTHONPATH=/root/kokoro-ft/stubs python3 kokoro_select_v2.py ~/kokoro-ft/select-v2 StyleTTS2/$L2/epoch_2nd_0000{5,6,7,8,9}.pth >> v2-select.log 2>&1
  log "select exit $?"
fi
log "ALL DONE"
