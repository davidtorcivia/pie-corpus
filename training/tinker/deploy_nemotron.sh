#!/bin/zsh
# Merge a Tinker LoRA checkpoint of the Nemotron 3.5 Super run into the local text-only bf16 base
# (build_text_base.py, from the VL checkpoint) and quantize it with omlx's oQ (enhanced, no MTP: mlx-lm's nemotron_h
# drops the draft head), then delete the merged bf16 copy.
#   training/tinker/deploy_nemotron.sh RUN NAME TAG [LEVEL]
#     the checkpoint comes from tr-desktop Q:\AI\PIE\tinker\ckpt\RUN\NAME (fetch_ckpt.py); TAG names the model
#     (PIE-nemotron35-TAG-oQ<LEVEL>e); LEVEL default 5
set -euo pipefail
RUN=$1; NAME=$2; TAG=$3; LEVEL=${4:-5}
HERE=${0:A:h}
BASE=/Users/david/AI/NVIDIA-Nemotron-3.5-Super-120B-A12B-BF16-text
WORK=/Users/david/AI/pie-runs/tinker/$RUN
ADAPTER=$WORK/$NAME
MERGED=$WORK/PIE-nemotron35-$TAG
export UV_CACHE_DIR=/tmp/pie-uv-cache
mkdir -p $WORK
if [ ! -d $ADAPTER ]; then
  scp -rq "tr-desktop:Q:/AI/PIE/tinker/ckpt/$RUN/$NAME" $WORK/
fi
uv run --quiet --python 3.12 --with tinker-cookbook --with torch --with transformers --with safetensors python -I -c "
from tinker_cookbook import weights
weights.build_hf_model(base_model='$BASE', adapter_path='$ADAPTER', output_path='$MERGED', merge_strategy='shard')
"
# the merge must have changed the weights the adapter targets: compare one LoRA-targeted tensor with the base
uv run --quiet --python 3.12 --with torch --with safetensors python -I -c "
import json
from safetensors import safe_open
bi = json.load(open('$BASE/model.safetensors.index.json'))['weight_map']
mi = json.load(open('$MERGED/model.safetensors.index.json'))['weight_map']
assert sorted(bi) == sorted(mi), 'merged tensor names differ from the base'
for k in ('backbone.layers.7.mixer.q_proj.weight', 'backbone.layers.0.mixer.out_proj.weight'):
    if k in bi:
        a = safe_open('$BASE/' + bi[k], framework='pt').get_tensor(k).float()
        b = safe_open('$MERGED/' + mi[k], framework='pt').get_tensor(k).float()
        print(k, 'relative change', float((a - b).norm() / a.norm()))
"
OUT=$(python3 -I $HERE/omlx_oq.py $MERGED $LEVEL --no-mtp | tail -1)
rm -rf $MERGED
du -sh $OUT
