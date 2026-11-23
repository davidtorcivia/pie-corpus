#!/bin/bash
# Status of a Colab gʷerh run, with the spending guard: below FLOOR compute units (default 300) the run is told to stop.
# Once the VM's pusher reports DONE (final last.pt pushed), the VM is released. Usage: colab_check.sh RUN [FLOOR]
RUN=$1; FLOOR=${2:-300}; S=pie-$RUN
BAL=$(colab usage 2>/dev/null | grep -oE "balance: [0-9.]+" | grep -oE "[0-9.]+"); RATE=$(colab usage 2>/dev/null | grep -oE "rate: [0-9.]+/hr")
echo "balance $BAL CU, $RATE"
if ! colab ssh -s $S -- true </dev/null >/dev/null 2>&1; then
  echo "session $S not reachable (released or reclaimed by Colab): resume with colab_train.sh $RUN"; exit 1; fi
colab ssh -s $S -- 'W=/content/w; R=$W/runs/'"$RUN"'; grep -E "^step" $R/train.log | tail -1 | cut -c1-120; grep -E "^val" $R/train.log | tail -3; tail -2 $W/push.log; grep -c Traceback $W/train.out; [ -f $W/DONE ] && echo DONE; nvidia-smi --query-gpu=memory.used --format=csv,noheader' </dev/null
if [ -n "$BAL" ] && awk "BEGIN{exit !($BAL < $FLOOR)}"; then
  echo "balance below floor $FLOOR: stopping $RUN"; colab ssh -s $S -- "touch /content/w/runs/$RUN/STOP" </dev/null
fi
if colab ssh -s $S -- 'test -f /content/w/DONE' </dev/null; then colab stop -s $S && echo "released $S"; fi
