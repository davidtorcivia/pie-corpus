"""Fine-detail ratios measured on the RENDERED audio (mel of the wav, 32 kHz, wokʷs format) vs the paid clip's audio.
audiostats.py SPEC DIR [DIR...]  -> dF / dT ratios per band (bins 0-25/25-50/50-75/75-100), so vocoder-added grain shows."""
import sys, json, os, numpy as np, torch, librosa
sys.path.insert(0, os.path.expanduser('~/AI/PIE/tts/wokws')); import audio as A
E = os.path.expanduser('~/AI/chimera-pie-data/sts-eval'); lines = json.load(open(sys.argv[1]))['lines']
B = [(0, 25), (25, 50), (50, 75), (75, 100)]
def st(p):
    y, _ = librosa.load(p, sr=32000); y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05
    x = A.mel(torch.from_numpy(y).float()[None])[0].numpy(); x = x if x.shape[1] == 100 else x.T
    dF = [np.abs(2 * x[:, max(a,1):min(b,99)] - x[:, max(a,1)-1:min(b,99)-1] - x[:, max(a,1)+1:min(b,99)+1]).mean() for a, b in B]
    dT = [np.abs(np.diff(x[:, a:b], axis=0)).mean() for a, b in B]
    return np.array(dF + dT)
ref = np.mean([st(f'{E}/paid44/{v}/{s}.wav') for v, s, _ in lines], 0)
print(f'{"":24s} dF b0-b3               | dT b0-b3   (ratio to paid44 audio)')
for d in sys.argv[2:]:
    r = np.mean([st(f'{E}/{d}/{v}/{s}.wav') for v, s, _ in lines if os.path.exists(f'{E}/{d}/{v}/{s}.wav')], 0) / ref
    print(f'{d:24s}', ' '.join(f'{v:.2f}' for v in r[:4]), ' |', ' '.join(f'{v:.2f}' for v in r[4:]))
