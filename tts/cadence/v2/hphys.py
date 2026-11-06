# physical measures of word-initial h before e/i/j in the Kokoro output (old v10 e10 vs new e00005): 2-8 kHz energy share
# (as restore.share; the corpus h gate is 0.25-0.60; v10 training audio ~0.93, v2 ~0.47), spectral centroid, and the
# voiced share (the "zh" percept) by autocorrelation; same lines, voices and seeds as kokoro_eval.py
import sys, os, json
os.environ.setdefault("DEV", "cuda")
sys.argv = ["x", "/root/kokoro-ft/final", "/root/kokoro-ft/cand-e00005", "/mnt/c/Users/David/Downloads/PIE/eval_lines.json", "/root/kokoro-ft/kikiri-tts/training/val_list.txt", "/tmp/x.json"]
src = open("/mnt/c/Users/David/Downloads/PIE/kokoro_eval.py").read().split("res = {}")[0]
exec(src)
def share(x):
    S = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; f = np.fft.rfftfreq(len(x), 1 / SR)
    return S[(f >= 2000) & (f < 8000)].sum() / max(S[f >= 50].sum(), 1e-12), float((S * f).sum() / max(S.sum(), 1e-12))
def voiced(x):
    fr = int(.03 * SR); n = v = 0
    for i in range(0, len(x) - fr, fr // 2):
        w = x[i:i + fr] - x[i:i + fr].mean(); ac = np.correlate(w, w, "full")[fr - 1:]
        lo, hi = SR // 400, SR // 70
        if ac[0] > 0: n += 1; v += ac[lo:hi].max() / ac[0] > 0.5
    return v / max(n, 1)
for tag, d in (("old", OLD), ("new", NEW)):
    model, packs = load(d); out = {"m": [], "f": []}
    for label, v in items:
        y, span = synth(model, packs, label, v)
        for kind, k, a, b in contexts(label):
            if kind != "h front" or k not in span: continue
            s, e = span[k]; x = y[int(s * SR):int(e * SR)]
            if len(x) < 400: continue
            sh, c = share(x); out[v].append((sh, c, voiced(x)))
    for v in ("m", "f"):
        a = np.array(out[v]); print(f"{tag} {v} n={len(a)}  2-8k share median {np.median(a[:,0]):.2f}  centroid median {np.median(a[:,1]):.0f} Hz  voiced share mean {a[:,2].mean():.2f}")
