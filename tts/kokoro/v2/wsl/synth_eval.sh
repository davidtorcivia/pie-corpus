#!/bin/bash
# the val sentences from the old model (Nov 6 e10, two voices) and the new run's epochs 14 and 15, with word spans
. /root/kokoro-ft/venv/bin/activate
cd /mnt/q/AI/PIE/train/kokoro
O=/root/kokoro-ft/synth-eval; S=/root/kokoro-ft/select-v3; L=/mnt/q/AI/PIE/runs/kokoro-v2/synth_eval.log
NEW="0:pie_zazy,1:pie_valeria,2:pie_antonio,3:pie_w02"
python synth_eval.py $O old-e10 /root/kokoro-ft/final/kokoro_pie_stage2_e10.pth /root/kokoro-ft/final/voices "0:pie_m,1:pie_f,2:pie_m,3:pie_f" > $L 2>&1
python synth_eval.py $O new-e14 $S/e00013/kokoro_pie_e00013.pth $S/e00013/voices $NEW >> $L 2>&1
python synth_eval.py $O new-e15 $S/e00014/kokoro_pie_e00014.pth $S/e00014/voices $NEW >> $L 2>&1
echo "EXIT $?" >> $L
