#!/bin/bash
# Pause a Colab gʷerh run: STOP file (the trainer saves last.pt and exits), wait for the pusher's final push, release
# the VM. Resume later with colab_train.sh RUN. Usage: colab_stop.sh RUN
RUN=$1; S=pie-$RUN
colab ssh -s $S -- "touch /content/w/runs/$RUN/STOP" </dev/null
for i in $(seq 1 60); do colab ssh -s $S -- 'test -f /content/w/DONE' </dev/null && break; sleep 20; done
colab ssh -s $S -- 'tail -3 /content/w/push.log' </dev/null; colab stop -s $S && echo "released $S"
