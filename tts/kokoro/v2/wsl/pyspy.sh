#!/bin/bash
# install py-spy into the trainer venv, then dump the running trainer's main-thread stack a few times
/root/uvenv/bin/uv pip install --python /root/kokoro-ft/venv/bin/python -q py-spy || exit 1
P=$(pgrep -f "python train_second.py" | head -1); echo "pid $P"
[ -z "$P" ] && exit 0
/root/kokoro-ft/venv/bin/py-spy record -p $P -d 20 -r 50 -f raw -o /tmp/s2.txt --nonblocking >/dev/null 2>&1
sort -t' ' -k2 -nr /tmp/s2.txt 2>/dev/null | head -0
python3 - <<'PY'
import collections
c = collections.Counter(); tot = 0
for line in open("/tmp/s2.txt"):
    stack, n = line.rsplit(" ", 1); n = int(n); tot += n
    for fr in set(stack.split(";")):
        c[fr] += n
for fr, n in c.most_common(40):
    print(f"{100*n/tot:5.1f}%  {fr[:170]}")
PY
