#!/bin/bash
# score Stage 2 epochs 12-15 (kokoro_select_v3.py) on the val set, render demos; results copied to Q:
. /root/kokoro-ft/venv/bin/activate
export PYTHONUNBUFFERED=1 HF_HOME=/root/.cache/huggingface
S=/mnt/q/AI/PIE/runs/kokoro-v2/stage2; O=/root/kokoro-ft/select-v3
cd /mnt/q/AI/PIE/train/kokoro
python kokoro_select_v3.py $O $S/epoch_2nd_00011.pth $S/epoch_2nd_00012.pth $S/epoch_2nd_00013.pth $S/epoch_2nd_00014.pth > /mnt/q/AI/PIE/runs/kokoro-v2/select.log 2>&1
echo "EXIT $?" >> /mnt/q/AI/PIE/runs/kokoro-v2/select.log
mkdir -p /mnt/q/AI/PIE/runs/kokoro-v2/select
rsync -a --exclude 'audio-*' $O/ /mnt/q/AI/PIE/runs/kokoro-v2/select/
