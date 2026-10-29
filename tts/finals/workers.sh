#!/bin/sh
# Start N Seed-VC F0 workers on tts/finals/audio/queue (tts/vc/convert_seedvc.py queue mode), each capped at
# cores/N torch threads; they exit when the queue is empty. Logs: tts/finals/audio/queue/worker-<i>.log
#     tts/finals/workers.sh 5
set -e
N=${1:-5}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
CORES=$(sysctl -n hw.ncpu 2>/dev/null || nproc)
T=$(( CORES / N ))
Q="$ROOT/tts/finals/audio/queue"
mkdir -p "$Q"
cd "$ROOT/tts/vc/src/seed-vc"
i=1
while [ "$i" -le "$N" ]; do
  HF_HUB_ENABLE_HF_TRANSFER=0 OMP_NUM_THREADS=$T MKL_NUM_THREADS=$T SEEDVC_THREADS=$T \
    ../../.venv-seedvc/bin/python ../../convert_seedvc.py f0 --queue "$Q" > "$Q/worker-$i.log" 2>&1 &
  i=$((i + 1))
done
wait
