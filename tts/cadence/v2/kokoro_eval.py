"""Old vs new Kokoro PIE voices on the three defect contexts and the trill (2026-11-06), on CUDA:
  python kokoro_eval.py OLD_DIR NEW_DIR eval_lines.json val_list.txt OUT.json
Each model dir: config.json, kokoro_pie_*.pth, voices/pie_{m,f}.pt. Lines: the crafted test lines in both voices + the
validation lines in their own voice. Phone times come from the model's own predicted durations (600 samples a frame).
Recognizer wav2vec2-xlsr-53-espeak-cv-ft @ 2c73378, greedy CTC, on:
  h before e/i/j (word-initial): hushing onset (ʃ ʒ ɕ ʑ ç, tʃ dʒ) / stop onset (t k p d) / clean
  phrase-final r (before . , or the end): a hiss after it (ʃ ʒ ɕ ʑ ç s)
  s+t inside a word: on the whole word, the sound heard right after the s: velar / alveolar / labial / dropped
Trill: contacts (>= 6 dB dips, 300-3000 Hz envelope) inside each r's predicted span +-10 ms, as tts-corpus trill_scan."""
import os
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "8"
import sys, json, types, collections, unicodedata
from pathlib import Path
import numpy as np, torch
DEV = os.environ.get("DEV", "cuda")
torch.set_num_threads(8)
if DEV == "cuda": torch.cuda.set_per_process_memory_fraction(0.25, 0)
KIKIRI = os.path.expanduser("~/kokoro-ft/kikiri-tts/kokoro/kokoro")
_pkg = types.ModuleType("kokoro"); _pkg.__path__ = [KIKIRI]; sys.modules["kokoro"] = _pkg
try:
    import loguru  # noqa: F401
except ImportError:   # the model code logs through it; a quiet stand-in (as the site's render_dict_audio.py)
    _lg = types.ModuleType("loguru"); _lg.logger = types.SimpleNamespace(**{k: (lambda *x, **y: None) for k in ("debug", "info", "warning", "error")}); sys.modules["loguru"] = _lg
from kokoro.model import KModel
from huggingface_hub import hf_hub_download
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
from scipy.signal import butter, sosfiltfilt, resample_poly
OLD, NEW, LINES, VAL, OUT = sys.argv[1:6]
REPO, REV = "facebook/wav2vec2-xlsr-53-espeak-cv-ft", "2c733782da5604684829819a5eb744c193fe9398"
P = Wav2Vec2FeatureExtractor.from_pretrained(REPO, revision=REV)
VOC = {i: t for t, i in json.load(open(hf_hub_download(REPO, "vocab.json", revision=REV))).items()}
REC = Wav2Vec2ForCTC.from_pretrained(REPO, revision=REV).eval().to(DEV)
SR = 24000
B = lambda c: unicodedata.normalize("NFD", c)[0]

def load(d):
    d = Path(d); m = KModel(config=str(d / "config.json"), model=str(sorted(d.glob("kokoro_pie_*.pth"))[-1])).eval().to(DEV)
    return m, {n: torch.load(d / f"voices/pie_{n}.pt", weights_only=True).to(DEV) for n in ("m", "f")}

def zlib_crc(x):
    import zlib
    return zlib.crc32(x.encode())


def synth(model, packs, label, v):
    keep = [i for i, c in enumerate(label) if c in model.vocab]
    ids = [model.vocab[label[i]] for i in keep]
    torch.manual_seed(zlib_crc(label + v))          # the decoder's noise: the same per line in both models
    with torch.no_grad():
        wav, dur = model.forward_with_tokens(torch.LongTensor([[0, *ids, 0]]).to(DEV), packs[v][min(len(label), 509) - 1], 1.0)
    y = wav.float().cpu().numpy().ravel(); d = dur.cpu().numpy().ravel() * 600
    ends = np.cumsum(d); starts = ends - d
    span = {ci: (starts[k + 1] / SR, ends[k + 1] / SR) for k, ci in enumerate(keep)}    # char index -> (s, e)
    return y, span

def contexts(label):
    """(kind, char index of the key phone, word char span)"""
    out = []; i = 0
    words = [(m_s, m_s + len(w)) for m_s, w in _words(label)]
    for a, b in words:
        w = label[a:b]
        letters = [k for k in range(a, b) if label[k].isalpha() or unicodedata.category(label[k]).startswith("L")]
        if len(letters) > 1 and label[letters[0]] == "h" and B(label[letters[1]]) in "eij": out.append(("h front", letters[0], a, b))
        for k in range(a + 1, b):
            if label[k] == "t" and label[k - 1] == "s": out.append(("s+t", k, a, b))
        for k in range(a, b):
            if label[k] == "r":
                out.append(("trill", k, a, b))
                rest = label[k + 1:b + 1].strip()
                if k == letters[-1] and (b >= len(label) or label[b] in ".,;!?"): out.append(("final r", k, a, b))
    return out

def _words(label):
    import re
    return [(m.start(), m.group(0)) for m in re.finditer(r"[^\s.,;!?]+", label)]

def recog(segs):
    out = []
    for i in range(0, len(segs), 32):
        bt = [resample_poly(s, 2, 3) for s in segs[i:i + 32]]
        inp = P(bt, sampling_rate=16000, return_tensors="pt", padding=True, return_attention_mask=True)
        with torch.no_grad(): ids = REC(inp.input_values.to(DEV), attention_mask=inp.attention_mask.to(DEV)).logits.argmax(-1).cpu().numpy()
        for x, d in zip(bt, ids):
            ph, prev = [], None
            for j in d[:max(1, len(x) // 320)].tolist():
                if j != prev and not VOC[j].startswith("<") and VOC[j] not in ("|", " "): ph.append(VOC[j])
                prev = j
            out.append("".join(ph))
    return out

SOS = butter(4, [300, 3000], "bandpass", fs=SR, output="sos")
def n_contacts(y, t0, t1):
    x = sosfiltfilt(SOS, y); h, w = int(.002 * SR), int(.008 * SR)
    e = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9 for i in range(0, len(x) - w, h)]))
    a, b = max(1, int(t0 * SR / h)), min(len(e) - 1, int(t1 * SR / h)); k = int(.030 * SR / h); n = 0
    for i in range(a, b):
        if e[i] <= e[i - 1] and e[i] < e[i + 1] and e[max(0, i - k):i].max() - e[i] >= 6 and e[i + 1:i + 1 + k].max() - e[i] >= 6: n += 1
    return n

items = [(x["label"], v) for x in json.load(open(LINES)) for v in ("m", "f")]
items = items[:int(os.environ.get("LIMIT", "100000"))]
items += [] if os.environ.get("LIMIT") else [(l.split("|")[1], "m" if l.strip().split("|")[2] == "0" else "f") for l in open(VAL, encoding="utf-8") if l.strip()]
res = {}
for tag, d in (("old", OLD), ("new", NEW)):
    model, packs = load(d); segs, meta = [], []
    for label, v in items:
        y, span = synth(model, packs, label, v)
        for kind, k, a, b in contexts(label):
            if k not in span: continue
            s, e = span[k]
            wa = span.get(next((j for j in range(a, b) if j in span), k))[0]; we = span.get(max(j for j in range(a, b) if j in span))[1]
            if kind == "trill":
                meta.append({"kind": kind, "v": v, "word": label[a:b], "contacts": n_contacts(y, s - .01, e + .01), "dur_ms": round((e - s) * 1000)}); continue
            if kind == "h front": seg = y[max(0, int((s - .005) * SR)):int((we + .05) * SR)]
            elif kind == "final r": seg = y[max(0, int((s - .05) * SR)):int((e + .25) * SR)]
            else: seg = y[max(0, int((wa - .03) * SR)):int((we + .06) * SR)]   # s+t: the whole word (short windows decode to nothing)
            segs.append(seg); meta.append({"kind": kind, "v": v, "word": label[a:b], "seg": len(segs) - 1})
    heard = recog(segs)
    for m in meta:
        if "seg" in m:
            h = heard[m.pop("seg")]; m["heard"] = h
            if m["kind"] == "h front": m["cls"] = "hushing" if any(c in h[:3] for c in "ʃʒɕʑç") or h.startswith(("tʃ", "dʒ")) else "stop onset" if h[:1] in "tkpd" else "clean"
            elif m["kind"] == "final r": m["cls"] = "hiss" if any(c in h for c in "ʃʒɕʑçs") else "clean"
            else:   # what the recognizer hears right after the word's s (or anywhere, if it hears no s)
                tail = h[h.index("s") + 1:h.index("s") + 3] if "s" in h else h
                m["cls"] = "velar" if any(q in tail for q in "kɡgcq") else "alveolar" if any(q in tail for q in "tdθ") else "labial" if any(q in tail for q in "pb") else "dropped"
    res[tag] = meta; del model
    if DEV == "cuda": torch.cuda.empty_cache()
json.dump(res, open(OUT, "w"), ensure_ascii=False)
for kind in ("h front", "final r", "s+t", "trill"):
    for v in ("m", "f"):
        line = []
        for tag in ("old", "new"):
            r = [m for m in res[tag] if m["kind"] == kind and m["v"] == v]
            if kind == "trill":
                line.append(f"{tag}: n={len(r)} >=2 contacts {np.mean([m['contacts'] >= 2 for m in r]):.2f} >=1 {np.mean([m['contacts'] >= 1 for m in r]):.2f} mean {np.mean([m['contacts'] for m in r]):.2f} dur {np.median([m['dur_ms'] for m in r]):.0f} ms")
            else:
                c = collections.Counter(m["cls"] for m in r); line.append(f"{tag}: n={len(r)} " + " ".join(f"{k} {c[k]/max(1,len(r)):.0%}" for k in sorted(c)))
        print(f"{kind:<8} {v}  |  " + "  |  ".join(line))
