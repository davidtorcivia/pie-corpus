# every r in the clips that keep their v10 conversion: is final_v2 sample-identical to v10 final inside the r itself
# (render timing + the repair's own alignment)? And how much of each r does the trill scan count inside [start, end]?
import os
os.environ["OMP_NUM_THREADS"] = "1"
import json, sys, multiprocessing as mp, unicodedata, numpy as np, soundfile as sf, librosa
sys.path.insert(0, "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/v11test/pie-vtl")
W = "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/work"; S = json.load(open(f"{W}/final_v2_sources.json"))
B = lambda p: unicodedata.normalize("NFD", p)[0]
def one(stem):
    from restore import lag_s
    J = json.load(open(f"{W}/renders/{stem}.json")); rs = [(i == len(w["phones"]) - 1, p) for w in J["words"] for i, p in enumerate(w["phones"]) if B(p["phone"]) == "r"]
    if not rs: return []
    a, sr = sf.read(f"{W}/final/{stem}.wav"); b, _ = sf.read(f"{W}/final_v2/{stem}.wav")
    y, s44 = librosa.load(f"{W}/murmured/{stem}.wav", sr=None); ref, _ = librosa.load(f"{W}/renders/{stem}.wav", sr=None)
    d = lag_s(y, s44, ref, s44)
    out = []
    for fin, p in rs:
        i0, i1 = int((p["start"] + d) * sr), int((p["end"] + d) * sr) - 2   # (resampling smears ~1 sample at the edge)
        x, z = a[i0:i1], b[i0:i1]
        rel = float(np.abs(x - z).max() / (np.abs(x).max() + 1e-9)) if len(x) else 0.0
        out.append((fin, rel))
    return out
if __name__ == "__main__":
    st = [s for s, w in S.items() if w == "v10" and os.path.exists(f"{W}/final_v2/{s}.wav")]
    with mp.Pool(8) as p: res = [r for rr in p.map(one, st, chunksize=16) for r in rr]
    for fin in (True, False):
        r = [x for f, x in res if f == fin]
        print("final r" if fin else "other r", "n", len(r), "inside the r: identical (rel diff < 1e-3)", sum(x < 1e-3 for x in r), "max rel diff", round(max(r), 4), "rel diff > 1%", sum(x > .01 for x in r))
