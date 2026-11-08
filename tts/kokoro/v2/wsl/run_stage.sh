#!/bin/bash
# Launch one Kokoro v2 training stage in WSL (Ubuntu-26.04 on tr-desktop). Code, configs, lists and run logs live on
# Q:\AI\PIE (/mnt/q/AI/PIE); the audio is read from a local ext4 copy (/root/kokoro-ft/data-v2/wavs) for speed.
# Resumes from <log_dir>/last.pth when present; stop with stop_stage.ps1 (STOP file -> saves, exits 0).
#   run_stage.sh STAGE CONFIG [LOG_DIR] [ENV="K=V;K=V"]
set -u
STAGE=$1; CONFIG=$2; LOGDIR=${3:-}; ENVS=${4:-}
K=/mnt/q/AI/PIE/train/kokoro
. /root/kokoro-ft/venv/bin/activate
export PYTHONUNBUFFERED=1 PYTHONUTF8=1
export HF_HOME=/root/.cache/huggingface
export TORCHINDUCTOR_CACHE_DIR=/root/.cache/inductor-pie TRITON_CACHE_DIR=/root/.cache/triton-pie
export PIE_GPU_MEM_FRAC=0.80 PIE_TF32=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True   # fragmentation: b6 OOMed with 3.7 GiB reserved-but-free
IFS=';' read -ra KV <<< "$ENVS"; for kv in "${KV[@]}"; do [[ "$kv" == *=* ]] && export "$kv"; done
CFG=$K/configs/$CONFIG.yml
[ -z "$LOGDIR" ] && LOGDIR=$(grep '^log_dir:' $CFG | sed 's/^log_dir: *//')
[ -n "${PIE_LOG_DIR:-}" ] && LOGDIR=$PIE_LOG_DIR
# the trainer writes where the console log goes (a LOG_DIR argument alone used to leave it on the config's log_dir)
[ -n "$LOGDIR" ] && export PIE_LOG_DIR=$LOGDIR
mkdir -p "$LOGDIR"; CON=$LOGDIR/console.log
# the audio: refresh the local copy from Q: when the corpus changed
rsync -a --delete /mnt/q/AI/PIE/data/tts-corpus-v2/wavs/ /root/kokoro-ft/data-v2/wavs/
SCRIPT=$([ "$STAGE" = 1 ] && echo train_first.py || echo train_second.py)
cd $K/StyleTTS2
echo "$(date '+%F %T') START stage $STAGE $CONFIG env=[$ENVS] (WSL)" >> "$CON"
python $SCRIPT -p $CFG >> "$CON" 2>&1
echo "$(date '+%F %T') EXIT $?" >> "$CON"
