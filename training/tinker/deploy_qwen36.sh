#!/bin/zsh
# Merge a Tinker LoRA checkpoint of the Qwen3.6-35B-A3B run into the local bf16 base and quantize it with omlx's oQ
# (oQ5 enhanced, MTP draft head kept: <name>-oQ5e-mtp in omlx's model dir /Users/david/AI), then delete the merged
# bf16 copy. Owner, 2026-10-31: merge, quantize and test in omlx, no inference on Tinker; "use the omlx quant
# method ... preserve draft heads".
#   training/tinker/deploy_qwen36.sh RUN NAME TAG [LEVEL]
#     the checkpoint comes from tr-desktop Q:\AI\PIE\tinker\ckpt\RUN\NAME (fetch_ckpt.py); TAG names the model
#     (PIE-qwen36-TAG-oQ5e-mtp); LEVEL default 5
set -euo pipefail
RUN=$1; NAME=$2; TAG=$3; LEVEL=${4:-5}
HERE=${0:A:h}
BASE=/Users/david/AI/Qwen3.6-35B-A3B-995ad96e
WORK=/Users/david/AI/pie-runs/tinker/$RUN
ADAPTER=$WORK/$NAME
MERGED=$WORK/PIE-qwen36-$TAG
export UV_CACHE_DIR=/tmp/pie-uv-cache
mkdir -p $WORK
if [ ! -d $ADAPTER ]; then
  scp -rq "tr-desktop:Q:/AI/PIE/tinker/ckpt/$RUN/$NAME" $WORK/
fi
uv run --quiet --python 3.12 --with tinker-cookbook --with torch --with transformers --with safetensors python -I -c "
from tinker_cookbook import weights
weights.build_hf_model(base_model='$BASE', adapter_path='$ADAPTER', output_path='$MERGED')
"
# the draft head must survive the merge, or there is nothing for oQ to preserve
python3 -I -c "
import json, sys
k = lambda p: [x for x in json.load(open(p))['weight_map'] if x.startswith('mtp')]
b, m = k('$BASE/model.safetensors.index.json'), k('$MERGED/model.safetensors.index.json')
print(f'mtp tensors: base {len(b)}, merged {len(m)}')
sys.exit(0 if b and sorted(b) == sorted(m) else 'merge dropped MTP tensors')
"
OUT=$(python3 -I $HERE/omlx_oq.py $MERGED $LEVEL | tail -1)
rm -rf $MERGED
du -sh $OUT
