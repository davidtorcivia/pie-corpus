"""Repair v2 over the whole corpus -> work/repaired_v2 (44.1 kHz) and work/final_v2 (24 kHz, the clips that passed the
v10 gate), rebuilt from scratch. The 288 s+t clips come from reconv-st (v11 render + new conversion + v1 repairs) when
their new conversion passes the gate, else from the v10 stages (counted). For those 288 the v10-source repair is also
written to repaired_v2_old/ for the old-vs-new checks. 8 workers x 1 thread, atomic writes, resumable."""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"): os.environ[v] = "1"
import sys, glob, json, multiprocessing as mp, contextlib, io
C = "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1"; W = f"{C}/work"; RC = f"{C}/reconv-st/work"
sys.path.insert(0, f"{C}/v11test/pie-vtl")
R = set(json.load(open(f"{C}/reconv-st/stems.json")))
QC = {f"{q['clip']}__{q['speaker']}": q["pass"] for q in map(json.loads, open(f"{RC}/qc.jsonl"))}
FINAL = set(os.listdir(f"{W}/final"))

def src(stem):
    if stem in R and QC.get(stem):
        return f"{RC}/murmured/{stem}.wav", f"{RC}/renders/{stem}", "reconv-st"
    return f"{W}/murmured/{stem}.wav", f"{W}/renders/{stem}", "v10"

def to24(a, b):
    import librosa, numpy as np, soundfile as sf
    y, sr = librosa.load(a, sr=None, mono=True); y = librosa.resample(y, orig_sr=sr, target_sr=24000, res_type="soxr_vhq")
    pk = float(np.abs(y).max()); y = y / pk * 0.99 if pk > 0.99 else y
    sf.write(b + ".part.wav", y, 24000, subtype="PCM_16"); os.replace(b + ".part.wav", b)

def rep(m, r, out):
    from repair_v2 import repair
    if not os.path.exists(out):
        with contextlib.redirect_stdout(io.StringIO()):
            repair(m, r + ".wav", r + ".json", out + ".part.wav", report=False)
        os.replace(out + ".part.wav", out)

def one(stem):
    m, r, where = src(stem)
    rep(m, r, f"{W}/repaired_v2/{stem}.wav")
    if stem + ".wav" in FINAL and not os.path.exists(f"{W}/final_v2/{stem}.wav"):
        to24(f"{W}/repaired_v2/{stem}.wav", f"{W}/final_v2/{stem}.wav")
    if stem in R:
        rep(f"{W}/murmured/{stem}.wav", f"{W}/renders/{stem}", f"{W}/repaired_v2_old/{stem}.wav")
    return stem, where

if __name__ == "__main__":
    for d in ("repaired_v2", "final_v2", "repaired_v2_old"): os.makedirs(f"{W}/{d}", exist_ok=True)
    stems = sorted(os.path.basename(p)[:-4] for p in glob.glob(f"{W}/murmured/*.wav"))
    srcs = {}
    with mp.Pool(8) as p:
        for k, (s, w) in enumerate(p.imap_unordered(one, stems, chunksize=8), 1):
            srcs[s] = w
            if k % 500 == 0: print(k, "/", len(stems), flush=True)
    json.dump(srcs, open(f"{W}/final_v2_sources.json", "w"), indent=0)
    n_new = sum(1 for s in R if srcs.get(s) == "reconv-st")
    print("done", len(os.listdir(f"{W}/repaired_v2")), "repaired,", len(os.listdir(f"{W}/final_v2")), "final;",
          f"s+t clips from the new conversion {n_new}/{len(R)}, kept v10 (new failed the gate) {len(R) - n_new}")
