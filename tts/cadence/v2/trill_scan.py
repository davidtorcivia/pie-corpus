"""Trill contacts per r (2026-11-06): for every r / r̥ segment in the render timings, the 300-3000 Hz envelope (2 ms
hop, 8 ms window) of the audio aligned to the render (restore.lag_s); a contact is a dip >= DIP dB under the peaks on
both sides within 30 ms (VTL trill contacts are -20 dB, 40 ms apart). Counted in the render (the design), v10 final/
and final_v2/. 8 workers x 1 thread."""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"): os.environ[v] = "1"
import sys, glob, json, unicodedata, multiprocessing as mp, collections
import numpy as np
C = "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1"; W = f"{C}/work"; RC = f"{C}/reconv-st/work"
sys.path.insert(0, f"{C}/v11test/pie-vtl")
DIP = float(os.environ.get("DIP", "6"))
SRC = json.load(open(f"{W}/final_v2_sources.json"))
B = lambda p: unicodedata.normalize("NFD", p)[0]

def env(y, sr):
    from scipy.signal import butter, sosfiltfilt
    x = sosfiltfilt(butter(4, [300, 3000], "bandpass", fs=sr, output="sos"), y)
    h, w = int(.002 * sr), int(.008 * sr)
    e = np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9 for i in range(0, len(x) - w, h)])
    return 20 * np.log10(e), h / sr

def contacts(e, hop, t0, t1):
    a, b = max(1, int(t0 / hop)), min(len(e) - 1, int(t1 / hop)); n = 0; k = int(.030 / hop)
    for i in range(a, b):
        if e[i] <= e[i - 1] and e[i] < e[i + 1]:
            if e[max(0, i - k):i].max() - e[i] >= DIP and e[i + 1:i + 1 + k].max() - e[i] >= DIP: n += 1
    return n

def one(stem):
    import librosa
    from restore import lag_s
    rd = f"{RC}/renders" if SRC.get(stem) == "reconv-st" else f"{W}/renders"
    J = json.load(open(f"{rd}/{stem}.json"))
    rs = []
    for wi, w in enumerate(J["words"]):
        ph = w["phones"]
        for i, p in enumerate(ph):
            if B(p["phone"]) == "r":
                pos = "final" if i == len(ph) - 1 else "initial" if i == 0 else "syllabic" if p["kind"] == "Rs" else "medial"
                rs.append((pos, p["start"], p["end"]))
    if not rs: return stem, []
    ref, sr = librosa.load(f"{rd}/{stem}.wav", sr=16000)
    out = {}
    for lab, path, rpath in (("render", f"{rd}/{stem}.wav", None), ("v10", f"{W}/final/{stem}.wav", f"{W}/renders/{stem}.wav"),
                             ("v2", f"{W}/final_v2/{stem}.wav", f"{rd}/{stem}.wav")):
        y, _ = librosa.load(path, sr=16000)
        if rpath:
            r_, _ = librosa.load(rpath, sr=16000); o = lag_s(y, 16000, r_, 16000)
        else: o = 0.0
        e, hop = env(y, 16000)
        # v10 final is aligned to the v10 render; the r timings of the v11 render equal v10's except for the s/t shift
        out[lab] = [contacts(e, hop, s0 + o - .01, s1 + o + .01) for _, s0, s1 in rs]
    return stem, [{"pos": pos, "render": out["render"][k], "v10": out["v10"][k], "v2": out["v2"][k]} for k, (pos, _, _) in enumerate(rs)]

if __name__ == "__main__":
    stems = sorted(f[:-4] for f in os.listdir(f"{W}/final_v2"))
    res = {}
    with mp.Pool(8) as p:
        for s, r in p.imap_unordered(one, stems, chunksize=8): res[s] = r
    json.dump(res, open(f"{W}/trill_scan.json", "w"))
    for spk in ("JD3", "W02"):
        rows = [x for s, r in res.items() if spk in s for x in r]
        for pos in ("initial", "medial", "syllabic", "final", "all"):
            r = [x for x in rows if pos == "all" or x["pos"] == pos]
            if not r: continue
            f = lambda k, n: sum(x[k] >= n for x in r) / len(r)
            lost = sum(1 for x in r if x["v10"] >= 2 and x["v2"] < 2)
            print(f"{spk} {pos:<8} n={len(r):5d}  >=2 contacts: render {f('render', 2):.3f}  v10 {f('v10', 2):.3f}  v2 {f('v2', 2):.3f}   "
                  f">=1: v10 {f('v10', 1):.3f} v2 {f('v2', 1):.3f}   v10>=2 but v2<2: {lost}   mean contacts v10 {np.mean([x['v10'] for x in r]):.2f} v2 {np.mean([x['v2'] for x in r]):.2f}")
