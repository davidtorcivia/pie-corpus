"""Buzz check calibrated by the owner's marks: at every distinct spot the owner marked "buzz" (listen page db, exported to
marks_rows.json), the 400 ms window before the mark; HF (2.5-7 kHz) envelope periodicity at the pitch period, render minus
paid in the same window. Higher = more pitch-locked HF = the buzz the owner hears. Also the same on random unmarked control
windows (should sit near 0).  buzzspots.py MARKS_ROWS.json DIR [DIR...]
NEGATIVE RESULT (2026-11-16): ~0 for every converter and for paid-mel copy synthesis alike, so it does not capture the
buzz the owner hears. Kept as a record; do not use it as a buzz score."""
import json, os, random, sys, numpy as np, librosa, scipy.signal as sg
E = os.path.expanduser('~/AI/chimera-pie-data/sts-eval'); SR = 16000
rows = json.load(open(sys.argv[1]))
spots = sorted({(r['voice'], r['stem'], round(float(r['t']), 1)) for r in rows if r['kind'] == 'buzz'})
sos = sg.butter(4, [2500, 7000], 'bandpass', fs=SR, output='sos'); cache = {}
def load(p):
    if p not in cache: cache[p] = librosa.load(p, sr=SR)[0]
    return cache[p]
def hp(y, T):
    e = np.abs(sg.hilbert(sg.sosfiltfilt(sos, y))); e = e - e.mean()
    return (e[:-T] * e[T:]).sum() / (np.sqrt((e[:-T] ** 2).sum() * (e[T:] ** 2).sum()) + 1e-12)
def period(y):
    f0, vf, _ = librosa.pyin(y, fmin=60, fmax=500, sr=SR, frame_length=1024, hop_length=160)
    v = f0[vf] if vf is not None else []
    return int(SR / np.median(v)) if len(v) >= 5 else None
random.seed(0)
ctrl = []
for v, s, t in spots:
    dur = len(load(f'{E}/paid44/{v}/{s}.wav')) / SR; ts = [x[2] for x in spots if x[0] == v and x[1] == s]
    for _ in range(30):
        c = round(random.uniform(0.5, dur), 2)
        if all(abs(c - x) > 0.6 for x in ts): ctrl.append((v, s, c)); break
def score(d, where):
    out = []
    for v, s, t in where:
        po, pp = f'{E}/{d}/{v}/{s}.wav', f'{E}/paid44/{v}/{s}.wav'
        if not os.path.exists(po): continue
        i, j = int(max(0, t - .4) * SR), int(t * SR)
        a, b = load(po)[i:j], load(pp)[i:j]
        if len(a) < .2 * SR or len(b) < .2 * SR: continue
        T = period(b)
        if T: out.append(hp(a, T) - hp(b, T))
    return np.mean(out), len(out)
print(f'{len(spots)} buzz spots, {len(ctrl)} control windows; excess HF periodicity vs paid (lower is better)')
for d in sys.argv[2:]:
    (m, n), (mc, nc) = score(d, spots), score(d, ctrl)
    print(f'{d:24s} buzz spots {m:+.3f} (n={n})   control {mc:+.3f} (n={nc})', flush=True)
