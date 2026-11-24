"""Trill strength, beyond the share measure: on each /r/ segment of 60 ms or longer (Chimera timing), the amplitude-envelope
modulation DEPTH in the tap band (18-45 Hz band-passed envelope, RMS over mean envelope; a deep trill dips toward
silence between taps, a weak one wobbles). Reports share (as trill.py) and depth, male / female.
  trilldepth.py SPEC DIR [DIR...]   (paid44 = paid)"""
import json, os, sys, numpy as np, librosa
from scipy.signal import butter, sosfiltfilt, hilbert
D = os.path.expanduser('~/AI/chimera-pie-data'); E = f'{D}/sts-eval'; SR, ESR = 16000, 1000; MALE = {'ZAZY', 'ANTONIO'}
def env(seg):
    bp = sosfiltfilt(butter(4, [300, 4000], 'bandpass', fs=SR, output='sos'), seg)
    e = sosfiltfilt(butter(4, 80, 'lowpass', fs=SR, output='sos'), np.abs(hilbert(bp)))[::SR // ESR]
    return e
def measures(seg):
    e = env(seg); m = e.mean()
    if m <= 0 or len(e) < 40: return None
    w = (e - m) * np.hanning(len(e)); p = np.abs(np.fft.rfft(w, ESR)) ** 2; f = np.fft.rfftfreq(ESR, 1 / ESR)
    tot = p[(f >= 2) & (f <= 60)].sum(); share = p[(f >= 18) & (f <= 45)].sum() / tot if tot > 0 else np.nan
    tap = sosfiltfilt(butter(2, [18, 45], 'bandpass', fs=ESR, output='sos'), e - m)
    return share, float(np.sqrt(np.mean(tap ** 2)) / m)
lines = json.load(open(sys.argv[1]))['lines']
print(f'{"":22s} {"male: share / depth (n)":>28s} {"female: share / depth (n)":>30s}')
for d in sys.argv[2:]:
    out = {}
    for g in 'mf':
        vals = []
        for v, s, _ in lines:
            if (v in MALE) != (g == 'm'): continue
            p = f'{D}/full/restored-v2/{v}/{s}.wav' if d == 'PAID' else f'{D}/full/chimera-v2/renders/{s}.wav' if d == 'CHIM' else f'{E}/{d}/{v}/{s}.wav'
            if not os.path.exists(p): continue
            x, _ = librosa.load(p, sr=SR)
            for w in json.load(open(f'{D}/full/timing/{s}.json'))['words']:
                for ph in w['phones']:
                    if ph['phone'] not in ('r', 'r̩') or (ph['end'] - ph['start']) < .06: continue
                    i, j = int((ph['start'] - .01) * SR), int((ph['end'] + .01) * SR)
                    if i < 0 or j > len(x): continue
                    r = measures(x[i:j])
                    if r and np.isfinite(r[0]): vals.append(r)
        out[g] = f'{np.mean([a for a, _ in vals]):.3f} / {np.mean([b for _, b in vals]):.3f} ({len(vals)})' if vals else '-'
    print(f'{d:22s} {out["m"]:>28s} {out["f"]:>30s}', flush=True)
