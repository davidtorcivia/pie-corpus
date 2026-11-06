"""Old vs new on the 288 re-converted s+t clips, zero credits, CUDA batched (wav2vec2-xlsr-53-espeak-cv-ft @ 2c73378):
1. every t before a vowel/glide (s+t and the rest) in the conversion: heard as alveolar, velar, labial, or dropped;
2. word-initial h before e/i after repair v2: hushing onset / stop onset;
3. phrase-final r after repair v2: a hushing/hissing sound after it."""
import os
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "8"
import json, sys, collections, unicodedata
import numpy as np, librosa, torch
from huggingface_hub import hf_hub_download
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
torch.set_num_threads(8); torch.cuda.set_per_process_memory_fraction(0.10, 0)
C = "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1"; W = f"{C}/work"; RC = f"{C}/reconv-st/work"
sys.path.insert(0, f"{C}/v11test/pie-vtl"); from restore import lag_s
REPO, REV = "facebook/wav2vec2-xlsr-53-espeak-cv-ft", "2c733782da5604684829819a5eb744c193fe9398"
P = Wav2Vec2FeatureExtractor.from_pretrained(REPO, revision=REV)
V = {i: t for t, i in json.load(open(hf_hub_download(REPO, "vocab.json", revision=REV))).items()}
M = Wav2Vec2ForCTC.from_pretrained(REPO, revision=REV).eval().cuda()
SR = 16000; B = lambda p: unicodedata.normalize("NFD", p)[0]
SRC = json.load(open(f"{W}/final_v2_sources.json")); R = [s for s in json.load(open(f"{C}/reconv-st/stems.json")) if SRC[s] == "reconv-st"]
segs = []
for stem in R:
    for ver, rd, conv, rep in (("old", f"{W}/renders", f"{W}/eleven", f"{W}/repaired_v2_old"), ("new", f"{RC}/renders", f"{RC}/eleven", f"{W}/repaired_v2")):
        J = json.load(open(f"{rd}/{stem}.json")); ref, _ = librosa.load(f"{rd}/{stem}.wav", sr=SR)
        y, _ = librosa.load(f"{conv}/{stem}.wav", sr=SR); o = lag_s(y, SR, ref, SR)
        z, _ = librosa.load(f"{rep}/{stem}.wav", sr=SR); oz = lag_s(z, SR, ref, SR)
        ws = J["words"]
        for wi, w in enumerate(ws):
            ph = w["phones"]; nxt = ws[wi + 1] if wi + 1 < len(ws) else None
            for i in range(len(ph) - 1):
                if ph[i]["phone"] == "t" and ph[i + 1]["kind"] in ("V", "Ns", "Ls", "Rs", "G"):
                    ctx = "s+t" if i and ph[i - 1]["phone"] == "s" else "other t"
                    a, b = max(0, int((ph[i]["start"] - .09 + o) * SR)), int((ph[i]["end"] + .10 + o) * SR)
                    segs.append(({"stem": stem, "ver": ver, "test": ctx, "word": w["word"]}, y[a:b]))
            if len(ph) > 1 and ph[0]["phone"] == "h" and (B(ph[1]["phone"]) in "ei" or ph[1]["phone"] == "j"):
                a, b = max(0, int((ph[0]["start"] - .005 + oz) * SR)), int((w["end"] + .05 + oz) * SR)
                segs.append(({"stem": stem, "ver": ver, "test": "h front", "word": w["word"]}, z[a:b]))
            if ph and ph[-1]["phone"] == "r" and (nxt is None or nxt["line"] != w["line"] or nxt["start"] - w["end"] > .15):
                a, b = max(0, int((ph[-1]["start"] - .05 + oz) * SR)), int((ph[-1]["end"] + .25 + oz) * SR)
                segs.append(({"stem": stem, "ver": ver, "test": "final r", "word": w["word"]}, z[a:b]))
def decode(ids):
    out, prev = [], None
    for i in ids:
        if i != prev:
            t = V[i]
            if not t.startswith("<") and t not in ("|", " "): out.append(t)
        prev = i
    return out
segs.sort(key=lambda s: len(s[1])); rows = []
for i in range(0, len(segs), 64):
    bt = segs[i:i + 64]
    inp = P([s[1] for s in bt], sampling_rate=SR, return_tensors="pt", padding=True, return_attention_mask=True)
    with torch.no_grad(): ids = M(inp.input_values.cuda(), attention_mask=inp.attention_mask.cuda()).logits.argmax(-1).cpu().numpy()
    for (meta, x), d in zip(bt, ids):
        h = "".join(decode(d[:max(1, len(x) // 320)].tolist())); meta["heard"] = h
        if meta["test"] in ("s+t", "other t"):
            meta["cls"] = "velar" if any(q in h for q in "kɡgcq") else "alveolar" if any(q in h for q in "td") else "labial" if any(q in h for q in "pb") else "dropped"
        elif meta["test"] == "h front":
            meta["cls"] = "hushing" if any(c in h[:3] for c in "ʃʒɕʑç") or h.startswith(("tʃ", "dʒ")) else "stop onset" if h[:1] in "tkpd" else "clean"
        else:
            meta["cls"] = "hiss" if any(c in h for c in "ʃʒɕʑçs") else "clean"
        rows.append(meta)
json.dump(rows, open(f"{C}/reconv-st/reg288.json", "w"), ensure_ascii=False)
print("clips", len(R))
for test in ("s+t", "other t", "h front", "final r"):
    for ver in ("old", "new"):
        r = [x for x in rows if x["test"] == test and x["ver"] == ver]
        c = collections.Counter(x["cls"] for x in r)
        print(f"{test:<8} {ver}  n={len(r):4d}  " + "  ".join(f"{k} {v} ({v / max(1, len(r)):.1%})" for k, v in c.most_common()))
