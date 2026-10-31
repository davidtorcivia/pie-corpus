#!/bin/zsh
# Merge a Tinker LoRA checkpoint of the Qwen3.6-35B-A3B run into the local bf16 base, convert it to a quantized
# MLX model in omlx's model dir (/Users/david/AI), and delete the merged bf16 copy (owner, 2026-10-31: merge,
# quantize and test in omlx; no inference on Tinker).
#   training/tinker/deploy_qwen36.sh RUN NAME [BITS]
#     the checkpoint comes from tr-desktop Q:\AI\PIE\tinker\ckpt\RUN\NAME (fetch_ckpt.py); BITS default 8
set -euo pipefail
RUN=$1; NAME=$2; BITS=${3:-8}
BASE=/Users/david/AI/Qwen3.6-35B-A3B-995ad96e
WORK=/Users/david/AI/pie-runs/tinker/$RUN
ADAPTER=$WORK/$NAME
MERGED=$WORK/merged-$NAME
OUT=/Users/david/AI/PIE-qwen36-35b-a3b-${RUN#qwen36-35b-a3b-}-$NAME-MLX-q$BITS
export UV_CACHE_DIR=/tmp/pie-uv-cache
mkdir -p $WORK
if [ ! -d $ADAPTER ]; then
  scp -rq "tr-desktop:Q:/AI/PIE/tinker/ckpt/$RUN/$NAME" $WORK/
fi
uv run --quiet --python 3.12 --with tinker-cookbook --with torch --with transformers --with safetensors python -I -c "
from tinker_cookbook import weights
weights.build_hf_model(base_model='$BASE', adapter_path='$ADAPTER', output_path='$MERGED')
"
uv run --quiet --python 3.12 --with mlx-lm python -I -m mlx_lm convert --hf-path $MERGED --mlx-path $OUT -q --q-bits $BITS
rm -rf $MERGED
du -sh $OUT
