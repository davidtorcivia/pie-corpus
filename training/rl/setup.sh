#!/bin/zsh
# The RL venv (mlx-lm-lora, pinned to the version benchmarked on 2026-11-01), outside the repo.
set -euo pipefail
V=/Users/david/AI/pie-runs/rl/.venv
export UV_CACHE_DIR=/tmp/pie-uv-cache
[ -x $V/bin/python ] || uv venv -q --python 3.12 $V
uv pip install -q --python $V/bin/python mlx-lm-lora==5.10.2 mlx-lm==0.32.2 mlx==0.32.4 anthropic==2.3.0
$V/bin/python -I -c "import mlx_lm_lora, mlx_lm; print('mlx-lm', mlx_lm.__version__)"
