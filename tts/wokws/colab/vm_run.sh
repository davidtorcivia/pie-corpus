#!/bin/bash
# On the Colab VM: fetch the data and <run>'s resume state from the private repo, then start the trainer and the
# checkpoint pusher, both detached (so the CLI call returns). Expects /content/code.tgz and the HF token at
# ~/.cache/huggingface/token (uploaded by colab_train.sh). Usage: bash vm_run.sh RUN
set -e
RUN=$1; REPO=disinfozone/pie-voice-train; W=/content/w
cd /content; mkdir -p $W/runs/$RUN; tar xzf code.tgz -C $W
source $W/kit/runs.sh
pip install -q -U "huggingface_hub[hf_xet]" librosa >/dev/null 2>&1
export HF_XET_HIGH_PERFORMANCE=1
hf download $REPO --repo-type dataset --include "data/*" "ckpt/$RUN/*" --local-dir $W/repo > $W/download.log 2>&1
cp $W/repo/ckpt/$RUN/last.pt $W/runs/$RUN/last.pt
[ -f $W/repo/ckpt/$RUN/train.log ] && cp $W/repo/ckpt/$RUN/train.log $W/runs/$RUN/train.log
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader > $W/gpu.txt
cd $W
export PYTHONPATH=$W/pylib BIGVGAN=$W/BigVGAN PYTHONUNBUFFERED=1
nohup bash -c "python code/gwerh_train.py --name $RUN --data=$W/repo/data --runs=$W/runs $COMMON $ARGS > $W/train.out 2>&1; echo \$? > $W/TRAIN_EXIT" > /dev/null 2>&1 &
nohup bash $W/kit/vm_push.sh $RUN > $W/push.log 2>&1 &
sleep 5; echo "started $RUN on $(cat $W/gpu.txt)"
