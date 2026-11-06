"""Corpus-wide s+t check (2026-11-06), zero credits: the phone recognizer (wav2vec2-xlsr-53-espeak-cv-ft @ 2c73378,
greedy CTC, as tts/vc/recognize.py) on every s+t segment of every clip, in the VTL render (baseline), the existing
conversion (eleven/) and the female conversion (control). Window: t start - 90 ms .. t end + 100 ms (the s, the t and
the start of the next sound), conversion aligned to the render by restore.lag_s. On CUDA, batched; 8 CPU threads.
Writes st_scan.jsonl (one row per occurrence and stage) and prints the rates."""
import os
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "8"
import glob, json, sys, collections
import numpy as np, librosa, torch
from huggingface_hub import hf_hub_download
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
torch.set_num_threads(8)
torch.cuda.set_per_process_memory_fraction(0.06, 0)
sys.path.insert(0, "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/pie-vtl")
from restore import lag_s
W = "/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1/work"; OUT = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/Users/David/Downloads/PIE/st_scan.jsonl"
REPO, REV = "facebook/wav2vec2-xlsr-53-espeak-cv-ft", "2c733782da5604684829819a5eb744c193fe9398"
P = Wav2Vec2FeatureExtractor.from_pretrained(REPO, revision=REV)
V = {i: t for t, i in json.load(open(hf_hub_download(REPO, "vocab.json", revision=REV))).items()}
M = Wav2Vec2ForCTC.from_pretrained(REPO, revision=REV).eval().cuda()
VEL = [i for i, t in V.items() if t in ("k", "c", "ɡ", "g", "q", "x", "kʰ", "ɟ")]
ALV = [i for i, t in V.items() if t in ("t", "d", "tʰ", "ʈ", "ɖ")]
SR = 16000

def decode(ids):
    out, prev = [], None
    for i in ids:
        if i != prev:
            t = V[i]
            if not t.startswith("<") and t not in ("|", " "): out.append(t)
        prev = i
    return out

segs = []   # (meta, audio)
stems = sorted(os.path.basename(f)[:-5] for f in glob.glob(f"{W}/renders/*__*.json"))
for stem in stems:
    J = json.load(open(f"{W}/renders/{stem}.json"))
    occ = [(w["word"], ph[i]["start"], ph[i]["end"]) for w in J["words"] for ph in [w["phones"]] for i in range(1, len(ph))
           if ph[i]["phone"] == "t" and ph[i - 1]["phone"] == "s"]
    if not occ: continue
    ref, _ = librosa.load(f"{W}/renders/{stem}.wav", sr=SR)
    y, _ = librosa.load(f"{W}/eleven/{stem}.wav", sr=SR); o = lag_s(y, SR, ref, SR)
    for k, (word, p0, p1) in enumerate(occ):
        for stage, x, off in (("render", ref, 0.0), ("conv", y, o)):
            a, b = max(0, int((p0 - .09 + off) * SR)), int((p1 + .10 + off) * SR)
            segs.append(({"stem": stem, "spk": "m" if "JD3" in stem else "f", "k": k, "word": word, "stage": stage}, x[a:b]))
print("segments", len(segs), flush=True)
segs.sort(key=lambda s: len(s[1]))
with open(OUT, "w") as f:
    for i in range(0, len(segs), 64):
        batch = segs[i:i + 64]
        inp = P([s[1] for s in batch], sampling_rate=SR, return_tensors="pt", padding=True, return_attention_mask=True)
        with torch.no_grad():
            lg = M(inp.input_values.cuda(), attention_mask=inp.attention_mask.cuda()).logits.float()
        pr = lg.softmax(-1).cpu().numpy(); ids = lg.argmax(-1).cpu().numpy()
        for (meta, x), p, d in zip(batch, pr, ids):
            n = max(1, int(len(x) / 320))
            ph = decode(d[:n].tolist())
            meta.update(heard="".join(ph), velar=any(V[j] in ("k", "c", "ɡ", "g", "q", "x", "kʰ", "ɟ") for j in set(d[:n].tolist())),
                        alveolar=any(t in ("t", "d", "tʰ") for t in ph),
                        p_velar=round(float(p[:n][:, VEL].sum(-1).max()), 3), p_alv=round(float(p[:n][:, ALV].sum(-1).max()), 3))
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
rows = [json.loads(l) for l in open(OUT)]
for spk in ("m", "f"):
    for st in ("render", "conv"):
        r = [x for x in rows if x["spk"] == spk and x["stage"] == st]
        clips = collections.defaultdict(list)
        for x in r: clips[x["stem"]].append(x["velar"])
        print(f"{spk} {st:<6} occurrences {len(r)}: heard velar {sum(x['velar'] for x in r)} ({sum(x['velar'] for x in r)/len(r):.1%}); "
              f"clips {len(clips)}, with >=1 velar {sum(any(v) for v in clips.values())}; median p_velar {np.median([x['p_velar'] for x in r]):.3f}")
