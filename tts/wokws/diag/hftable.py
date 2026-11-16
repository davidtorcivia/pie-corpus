"""High-frequency detail of gʷerh checkpoints for the run-check table: paid's own spectrogram through gʷerh step N,
fine detail (|2nd diff across mel bins| of the rendered audio's mel, ratio to paid's audio) in mel bands 50-75 and 75-100
(the two highest), averaged separately over the male and female eval lines. Renders on CPU, caches results.
  hftable.py STEP [STEP ...]   (fetches runs/g1/stepN.pt from tr-desktop if missing)  ->  prints one line per step"""
import json, os, subprocess, sys, numpy as np, torch, librosa
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); import audio as A
W = os.path.expanduser('~/AI/chimera-pie-data/wokws'); E = os.path.expanduser('~/AI/chimera-pie-data/sts-eval')
S = '/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad'
CACHE = f'{W}/logs/hftable.json'; cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
lines = json.load(open(f'{S}/spec_wc24.json'))['lines']; MALE = {'ZAZY', 'ANTONIO'}
def dF(p):
    y, _ = librosa.load(p, sr=32000); y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05
    x = A.mel(torch.from_numpy(y).float()[None])[0].numpy(); x = x if x.shape[1] == 100 else x.T
    return [np.abs(2 * x[:, max(a, 1):min(b, 99)] - x[:, max(a, 1) - 1:min(b, 99) - 1] - x[:, max(a, 1) + 1:min(b, 99) + 1]).mean() for a, b in ((50, 75), (75, 100))]
ref = {(v, s): dF(f'{E}/paid44/{v}/{s}.wav') for v, s, _ in lines}
def score(d):
    out = {}
    for g, keep in (('male', lambda v: v in MALE), ('female', lambda v: v not in MALE)):
        r = [np.array(dF(f'{E}/{d}/{v}/{s}.wav')) / np.array(ref[(v, s)]) for v, s, _ in lines if keep(v)]
        out[g] = [round(float(x), 2) for x in np.mean(r, 0)]
    return out
if 'v4' not in cache: cache['v4'] = score('v4copy-wokws')
for st in sys.argv[1:]:
    if st in cache: continue
    ck = f'{W}/runs/g1/step{st}.pt'
    if not os.path.exists(ck):
        subprocess.run(f'ssh tr-desktop "wsl -d Ubuntu-26.04 -- tar -C /root/wokws/runs/g1 -cf - step{st}.pt" 2>/dev/null | tar -C {W}/runs/g1 -xf -', shell=True, check=True)
    env = dict(os.environ, BIGVGAN=f'{W}/BigVGAN', OMP_NUM_THREADS='8')
    subprocess.run([os.path.expanduser('~/AI/chimera-pie-data/gsv-mac/venv/bin/python'), os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'render.py'),
                    f'gwerh{st}-copy', '--copy', '--lines', f'{S}/spec_wc24.json', '--vocoder', ck], env=env, check=True, capture_output=True)
    cache[st] = score(f'gwerh{st}-copy'); json.dump(cache, open(CACHE, 'w'))
json.dump(cache, open(CACHE, 'w'))
for k in ['v4'] + sys.argv[1:]:
    c = cache[k]; print(f"{k}: male {c['male'][0]:.2f}/{c['male'][1]:.2f}  female {c['female'][0]:.2f}/{c['female'][1]:.2f}")
