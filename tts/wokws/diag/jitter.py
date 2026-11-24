"""Pitch wavering screen: frame-to-frame F0 change (semitones, pyin 60-500 Hz, 10 ms hop) in voiced frames, per render set
and voice group, plus the share of voiced frames with a jump > 1 semitone. jitter.py SPEC DIR [DIR...]"""
import json, os, sys, numpy as np, librosa
E = os.path.expanduser('~/AI/chimera-pie-data/sts-eval'); lines = json.load(open(sys.argv[1]))['lines']; MALE = {'ZAZY', 'ANTONIO'}
def jit(p):
    y, sr = librosa.load(p, sr=16000)
    f0, vf, _ = librosa.pyin(y, fmin=60, fmax=500, sr=sr, frame_length=1024, hop_length=160)
    st = 12 * np.log2(np.where(vf, f0, np.nan) / 100.0); d = np.abs(np.diff(st)); d = d[np.isfinite(d)]
    return (np.median(d), np.mean(d > 1.0)) if len(d) else (np.nan, np.nan)
print(f'{"":22s} {"male: median step / jumps>1st":>32s} {"female: median step / jumps>1st":>34s}')
for d in sys.argv[2:]:
    r = {g: [jit(f'{E}/{d}/{v}/{s}.wav') for v, s, _ in lines if (v in MALE) == (g == 'm') and os.path.exists(f'{E}/{d}/{v}/{s}.wav')] for g in 'mf'}
    f = lambda L: f'{np.nanmean([a for a, _ in L]):.3f} st / {100 * np.nanmean([b for _, b in L]):.1f}%' if L else '-'
    print(f'{d:22s} {f(r["m"]):>32s} {f(r["f"]):>34s}', flush=True)
