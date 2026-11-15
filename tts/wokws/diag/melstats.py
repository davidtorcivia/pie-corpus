"""Over-smoothing / rattle diagnostics in the mel domain (model output vs paid mel, same frames).
melstats.py SPEC CKPT [CKPT...]   per band (bins 0-25 / 25-50 / 50-75 / 75-100 of 100 mel):
 GV = time variance of log-mel (ratio to paid), dT = mean |frame-to-frame change| (ratio), dF = mean |2nd diff along
 frequency| (ratio; harmonic detail), mod = share of 20-50 Hz in the 2-50 Hz modulation spectrum of band energy."""
import sys, json, os, numpy as np, torch
sys.path.insert(0, os.path.expanduser('~/AI/PIE/tts/wokws')); import wokws as W
from tiny_voca.config import Config
D = os.path.expanduser('~/AI/chimera-pie-data/wokws/data'); lines = json.load(open(sys.argv[1]))['lines']
B = [(0, 25), (25, 50), (50, 75), (75, 100)]
def stats(x):  # x [T,100] natural-log mel
    out = []
    for a, b in B:
        s = x[:, a:b]; e = s.mean(1); E = np.abs(np.fft.rfft(e - e.mean())) ** 2; f = np.fft.rfftfreq(len(e), 0.01)
        out.append([s.var(0).mean(), np.abs(np.diff(s, axis=0)).mean(),
                    np.abs(x[:, max(a, 1):min(b, 99)] * 2 - x[:, max(a, 1) - 1:min(b, 99) - 1] - x[:, max(a, 1) + 1:min(b, 99) + 1]).mean(),
                    E[(f >= 20) & (f < 50)].sum() / (E[(f >= 2) & (f < 50)].sum() + 1e-12)])
    return np.array(out)  # [4 bands, 4 stats]
models = []
for p in sys.argv[2:]:
    ck = torch.load(p, map_location='cpu', weights_only=False); c = Config.from_dict(ck['config']); v = ck['vocab']
    m = W.Wokws(c, v['n_tokens'], len(v['kinds'])); m.load_state_dict(ck['model']); models.append((os.path.basename(os.path.dirname(p)) + '/' + os.path.basename(p), m.eval()))
acc = {'paid': [], 'chimera': [], **{n: [] for n, _ in models}}
for v, s, _ in lines:
    d = torch.load(f'{D}/feats/{v}/{s}.pt', weights_only=True); P = d['paid_mel'].float().numpy()
    acc['paid'].append(stats(P)); acc['chimera'].append(stats(d['chim_mel'].float().numpy()))
    for n, m in models:
        with torch.inference_mode(): y = m.convert(W.collate([W.item(d, v)], 'cpu'))[0][0].float().numpy()
        T = min(len(y), len(P)); acc[n].append(stats(y[:T]))
ref = np.mean(acc['paid'], 0)
print(f'n={len(lines)} lines. paid absolute: ' + ' | '.join(f'b{i}: GV {ref[i,0]:.3f} dT {ref[i,1]:.3f} dF {ref[i,2]:.3f} mod {ref[i,3]:.3f}' for i in range(4)))
print(f'{"":26s}' + ''.join(f'{"band "+str(i)+" GV/dT/dF ratio, mod":>34s}' for i in range(4)))
for n, L in acc.items():
    if n == 'paid': continue
    r = np.mean(L, 0)
    print(f'{n:26s}' + ''.join(f'   {r[i,0]/ref[i,0]:5.2f} {r[i,1]/ref[i,1]:5.2f} {r[i,2]/ref[i,2]:5.2f}  {r[i,3]:.3f}' for i in range(4)))
