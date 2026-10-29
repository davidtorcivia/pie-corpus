"""Measure renders that share one phone timeline (a pie_vtl.py --timeline .json): pitch and laryngeal friction.

    tts/vc/.venv-eval/bin/python -I tts/cadence/vtl_check.py <phones.json> name=file.wav [name=file.mp3 ...]

The first file is the melody reference ("r ref"). Per file:
- step: median frame-to-frame F0 change (st), where eSpeak ≈ 0.07 is robotic and speech ≈ 0.2;
- accent: mean F0 of accented nuclei minus unaccented (st);
- decl/line: fitted F0 slope over the unaccented nuclei of each line (st);
- voiced nuclei.
Then for each laryngeal (χ ɣ ɣʷ h), the 2–8 kHz energy share and spectral flatness over its exact interval."""
import json, sys
import librosa, numpy as np, parselmouth

SR = 22050
J = json.load(open(sys.argv[1], encoding="utf-8"))
A = {k: librosa.load(p, sr=SR, mono=True)[0] for k, p in (x.split("=", 1) for x in sys.argv[2:])}
nuc = [p for w in J["words"] for p in w["phones"] if p["kind"] in ("V", "Ns")]


def st(a):
    f = parselmouth.Sound(a, SR).to_pitch_ac(0.01, 75, 400).selected_array["frequency"]
    s = 12 * np.log2(np.where(f > 0, f, np.nan)); m = np.nanmedian(s); s = np.where(s - m > 6, s - 12, s)
    return np.where(m - s > 6, s + 12, s)


def wr(X, Y):
    n = min(len(X), len(Y)); m = ~np.isnan(X[:n]) & ~np.isnan(Y[:n])
    return np.nanmedian([np.corrcoef(X[w:w + 100][m[w:w + 100]], Y[w:w + 100][m[w:w + 100]])[0, 1]
                         for w in range(0, n - 100, 100) if m[w:w + 100].sum() > 20])


def feats(a, t0, t1):
    seg = a[int(t0 * SR):int(t1 * SR)]
    S = np.abs(librosa.stft(seg, n_fft=512, hop_length=110, center=len(seg) < 512)) ** 2
    fr = librosa.fft_frequencies(sr=SR, n_fft=512)
    return np.mean(S[(fr > 2000) & (fr < 8000)].sum(0) / (S.sum(0) + 1e-12)), np.mean(librosa.feature.spectral_flatness(S=np.sqrt(S)))


F = {k: st(a) for k, a in A.items()}; ref = next(iter(F.values()))
print(f"{'file':18s}{'dur':>7s}{'step':>7s}{'HNR':>6s}{'r ref':>7s}{'accent':>8s}{'decl/line':>10s}{'voiced':>9s}")
for k, a in A.items():
    S = F[k]; d = np.abs(np.diff(S)); d = d[~np.isnan(d)]
    h = parselmouth.Sound(a, SR).to_harmonicity_cc(0.01, 75, 0.1, 1.0); hv = h.values[h.values > -100]
    acc, un, byline = [], [], {}
    for p in nuc:
        seg = S[int(p["start"] / 0.01):int(p["end"] / 0.01) + 1]; seg = seg[~np.isnan(seg)]
        if len(seg) < 2: continue
        m = np.median(seg); (acc if p["accent"] else un).append(m)
        if not p["accent"]: byline.setdefault(p["line"], []).append((p["start"], m))
    dec = [np.polyfit(t - t[0], m, 1)[0] * (t[-1] - t[0]) for t, m in (np.array(x).T for x in byline.values() if len(x) >= 3)]
    print(f"{k:18s}{len(a) / SR:7.2f}{np.median(d):7.3f}{hv.mean():6.1f}{wr(S, ref):7.2f}"
          f"{np.mean(acc) - np.mean(un):+8.1f}{np.mean(dec):+10.1f}{len(acc) + len(un):>5d}/{len(nuc)}")
print("\nlaryngeals on exact phone intervals: 2–8 kHz share / flatness")
print(f"{'word':18s}{'ph':4s}" + "".join(f"{k:>16s}" for k in A))
for w in J["words"]:
    for p in w["phones"]:
        if p["phone"].rstrip("ʷ") in ("χ", "ɣ", "h"):
            print(f"{w['word']:18s}{p['phone']:4s}" + "".join(f"{h:>11.2f}/{f:.2f}" for h, f in (feats(a, p["start"], p["end"]) for a in A.values())))
