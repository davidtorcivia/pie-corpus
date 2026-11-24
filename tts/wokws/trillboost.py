"""Trill enhancer (experiment, parked 2026-11-16, never rendered or heard): on every /r/ and syllabic /r̩/ (Chimera timing), impose Chimera's own tap envelope on the
converted audio. Chimera's envelope (300-4000 Hz band, Hilbert, 80 Hz low-pass) over the segment, normalised to its mean,
becomes a gain curve g = 1 + depth * (e/mean - 1), clipped to [0.12, 1.8], with 10 ms ramps at the edges, so the taps land
where Chimera puts them. depth 0 = unchanged. Phonemes are not changed, only how strongly /r/ is trilled.
  trillboost.py SRC_DIR OUT_DIR DEPTH SPEC   (sts-eval dirs; Chimera renders from full/chimera-v2/renders)"""
import json, os, sys, numpy as np, soundfile as sf, librosa
from scipy.signal import butter, sosfiltfilt, hilbert
D = os.path.expanduser('~/AI/chimera-pie-data'); E = f'{D}/sts-eval'
src, out, depth, spec = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
for v, s, _ in json.load(open(spec))['lines']:
    y, sr = sf.read(f'{E}/{src}/{v}/{s}.wav'); y = y.astype(np.float64)
    c, _ = librosa.load(f'{D}/full/chimera-v2/renders/{s}.wav', sr=sr)
    bp = butter(4, [300, 4000], 'bandpass', fs=sr, output='sos'); lp = butter(4, 80, 'lowpass', fs=sr, output='sos')
    g = np.ones_like(y); ramp = int(0.01 * sr)
    for w in json.load(open(f'{D}/full/timing/{s}.json'))['words']:
        for ph in w['phones']:
            if ph['phone'] not in ('r', 'r̩'): continue
            i, j = max(0, int((ph['start'] - .01) * sr)), min(len(y), len(c), int((ph['end'] + .01) * sr))
            if j - i < int(.03 * sr): continue
            e = sosfiltfilt(lp, np.abs(hilbert(sosfiltfilt(bp, c[i:j])))); e = np.maximum(e, 0)
            gg = np.clip(1 + depth * (e / (e.mean() + 1e-9) - 1), 0.12, 1.8)
            win = np.ones(j - i); r = min(ramp, (j - i) // 2); win[:r] = np.linspace(0, 1, r); win[-r:] = np.linspace(1, 0, r)
            g[i:j] = 1 + (gg - 1) * win
    os.makedirs(f'{E}/{out}/{v}', exist_ok=True); sf.write(f'{E}/{out}/{v}/{s}.wav', np.clip(y * g, -1, 1), sr)
print('DONE', out)
