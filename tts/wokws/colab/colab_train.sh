#!/bin/bash
# Start a gʷerh run on a Colab GPU (default G4), resuming from the private repo. Usage: colab_train.sh RUN [GPU]
# Session name pie-<run>. The trainer saves last.pt every 2000 steps; vm_push.sh pushes it to the repo every 30 min.
set -e
RUN=$1; GPU=${2:-G4}; S=pie-$RUN; HERE=$(cd "$(dirname "$0")" && pwd); WK=$(dirname "$HERE")
TOKEN=${HF_COLAB_TOKEN_FILE:-$HOME/.config/pie/hf_colab_token}
[ -f "$TOKEN" ] || { echo "no token file $TOKEN"; exit 2; }
BV=${BIGVGAN:-$HOME/AI/chimera-pie-data/wokws/BigVGAN}; PL=${PYLIB:-$HOME/AI/chimera-pie-data/wokws/pylib}
T=$(mktemp -d); mkdir -p $T/code $T/kit
cp $WK/gwerh_train.py $WK/gwerh.py $WK/audio.py $WK/mps_fixes.py $T/code/; cp $HERE/runs.sh $HERE/vm_push.sh $HERE/vm_run.sh $T/kit/
cp -R "$BV" $T/BigVGAN; rm -rf $T/BigVGAN/.git; cp -R "$PL" $T/pylib
tar -czf $T/code.tgz -C $T code kit BigVGAN pylib
# GPUs are often refused for lack of capacity: retry every 90 s for up to TRIES (default 20, ~30 min)
for i in $(seq 1 ${TRIES:-20}); do colab new -s $S --gpu $GPU 2>&1 | grep -q "Session READY" && break; [ $i = ${TRIES:-20} ] && { echo "no $GPU after $i tries"; exit 3; }; sleep 90; done
echo "$S on $GPU (try $i)"
trap 'echo "start failed: releasing $S"; colab stop -s $S' ERR      # a VM that never trains must not keep billing
colab upload -s $S $T/code.tgz /content/code.tgz
colab ssh -s $S -- 'mkdir -p /root/.cache/huggingface' </dev/null
colab upload -s $S "$TOKEN" /root/.cache/huggingface/token
colab ssh -s $S -- 'chmod 600 /root/.cache/huggingface/token && tar xzf /content/code.tgz -C /tmp kit/vm_run.sh && BATCH='"${BATCH:-16}"' MEM_FRAC='"${MEM_FRAC:-0.9}"' bash /tmp/kit/vm_run.sh '"$RUN" </dev/null
trap - ERR; rm -rf $T
echo "$RUN running on $S; check with colab_check.sh $RUN"
