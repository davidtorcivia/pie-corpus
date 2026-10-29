#!/usr/bin/env python3
"""Objective (machine) estimates for the TTS bake-off (docs/research/tts-bakeoff-objective.md).

Nobody but the owner can listen; these numbers come from a phone recognizer and from acoustic measures, so that the
owner's ear ratings have something to be compared with. Runs in the VC experiment's eval env, which already has the
recognizer (facebook/wav2vec2-xlsr-53-espeak-cv-ft @ 2c73378, weights in tts/vc/cache/hf, gitignored), torch,
librosa and parselmouth:

  tts/vc/.venv-eval/bin/python -I scripts/tts_bakeoff_objective.py recognize --cache <dir>   # CTC log-probs per clip
  tts/vc/.venv-eval/bin/python -I scripts/tts_bakeoff_objective.py analyze --cache <dir>     # objective.json + tables

Inputs: tts/bakeoff/manifest.json and the clip wavs in tts/bakeoff/audio/ (gitignored). The manifest is read only.
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tts" / "bakeoff" / "manifest.json"
AUDIO = ROOT / "tts" / "bakeoff" / "audio"
OUT_JSON = ROOT / "tts" / "bakeoff" / "objective.json"
FRAME = 0.02            # wav2vec2 frame stride (320 samples at 16 kHz)

# ---------------------------------------------------------------- symbols
# Both sides are normalized to one decomposed alphabet before any comparison (the mapping table in the write-up).
NFD = lambda s: unicodedata.normalize("NFD", s)  # noqa: E731
ACUTE, SYL, LONG = "́", "̩", "ː"
MODS = "ʰʱʷʲ"

# target (converter IPA) unit → recognizer-alphabet units
TARGET_MAP = {"bʱ": ["bʰ"], "dʱ": ["dʰ"], "ɡʱ": ["ɡʰ"], "ɟʱ": ["ɟʰ"], "ɡʷʱ": ["ɡʰ", "w"], "kʷ": ["k", "w"],
              "ɡʷ": ["ɡ", "w"], "ɣʷ": ["ɣ", "w"], "l" + SYL: ["ə", "l"], "m" + SYL: ["ə", "m"],
              "n" + SYL: ["ə", "n"], "r" + SYL: ["ə", "r"]}
# recognizer token → units (diphthongs and syllabic/schwa tokens decomposed; length and tone digits are stripped)
HYP_SPLIT = {"aʊ": ["a", "w"], "aɪ": ["a", "j"], "eɪ": ["e", "j"], "oʊ": ["o", "w"], "ɔɪ": ["o", "j"],
             "oɪ": ["o", "j"], "əʊ": ["ə", "w"], "əl": ["ə", "l"], "l̩": ["ə", "l"], "n̩": ["ə", "n"],
             "r̩": ["ə", "r"], "ɚ": ["ə", "r"], "ɑːɹ": ["a", "r"], "ɔːɹ": ["o", "r"], "oːɹ": ["o", "r"],
             "ɛɹ": ["e", "r"], "ɪɹ": ["i", "r"], "ʊɹ": ["u", "r"], "iə": ["i", "ə"], "eə": ["e", "ə"],
             "ʊə": ["u", "ə"], "ja": ["j", "a"], "ju": ["j", "u"], "kh": ["kʰ"], "th": ["tʰ"], "ph": ["pʰ"],
             "dZ": ["dʒ"], "tS": ["tʃ"], "S": ["ʃ"], "X": ["χ"], "N": ["ŋ"]}
# broad PER only: vowel quality and rhotic type collapsed (the recognizer's English/Romance vowel labels and its
# five rhotics are not what is being tested)
BROAD = {"ɛ": "e", "e̞": "e", "ɔ": "o", "o̞": "o", "ɪ": "i", "ɨ": "i", "ᵻ": "i", "ʊ": "u", "ʉ": "u", "ɑ": "a",
         "æ": "a", "ä": "a", "ɐ": "ə", "ʌ": "ə", "ɜ": "ə", "ɵ": "o", "ɾ": "r", "ɹ": "r", "ʁ": "r", "ɻ": "r",
         "ɫ": "l", "y": "i"}
VOWELS = set("aeiouəɛɔɪʊɐʌɜɑæɨᵻʉɵøœyäɒɯ") | {"e̞", "o̞"}


def is_vowel(u: str) -> bool:
    return NFD(u)[0] in VOWELS


def target_units(ipa: str) -> tuple[list[str], list[int]]:
    """Converter IPA → (units, syllable index per unit). Acutes, length, dots are removed; dots give syllables."""
    units, syl = [], []
    for si, s in enumerate(NFD(ipa).split(".")):
        s = s.replace(ACUTE, "").replace(LONG, "")
        i = 0
        while i < len(s):
            j = i + 1
            while j < len(s) and (s[j] in MODS or s[j] == SYL):
                j += 1
            ph = unicodedata.normalize("NFC", s[i:j])
            for u in TARGET_MAP.get(ph, [ph]):
                units.append(u)
                syl.append(si)
            i = j
    return units, syl


def hyp_units(tok: str) -> list[str]:
    t = tok.replace("ː", "").replace(":", "").rstrip("12345ɜ")
    t = t.replace(".", "").replace("[", "").replace("^", "").replace('"', "") or tok
    return HYP_SPLIT.get(tok, HYP_SPLIT.get(t, [t]))


def broad(u: str) -> str:
    return BROAD.get(u, u)


# ---------------------------------------------------------------- alignment
GROUPS = [set("hxχçħʁɣ") | {"X"}, {"ɟ", "dʒ", "ɡ", "ɡʲ", "j", "dʑ", "ɟʰ", "ʝ"}, {"c", "tʃ", "k", "kʲ", "tɕ", "kʰ", "q"},
          {"b", "bʰ", "p", "pʰ", "β", "v"}, {"d", "dʰ", "t", "tʰ", "ð", "ts"}, {"ɡ", "ɡʰ", "k", "ɣ", "x"},
          {"w", "ʋ", "u", "v"}, {"l", "ɫ", "ɭ"}, {"m", "n", "ŋ"}, {"r", "ɾ", "ɹ", "ʁ"}, {"s", "z", "ʃ"}]


def subcost(a: str, b: str) -> float:
    if a == b or broad(a) == broad(b):
        return 0.0
    va, vb = is_vowel(a), is_vowel(b)
    if va and vb:
        return 0.6
    if va != vb:
        return 2.1  # never cheaper than a deletion plus an insertion
    return 0.6 if any(a in g and b in g for g in GROUPS) else 1.0


def align(ref: list[str], hyp: list[str]) -> list[tuple[int | None, int | None]]:
    """Weighted Levenshtein alignment (phonetic substitution costs), as (ref index | None, hyp index | None) pairs."""
    n, m = len(ref), len(hyp)
    D = np.zeros((n + 1, m + 1))
    D[:, 0] = np.arange(n + 1)
    D[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(D[i - 1, j] + 1, D[i, j - 1] + 1, D[i - 1, j - 1] + subcost(ref[i - 1], hyp[j - 1]))
    out, i, j = [], n, m
    while i or j:
        if i and j and np.isclose(D[i, j], D[i - 1, j - 1] + subcost(ref[i - 1], hyp[j - 1])):
            out.append((i - 1, j - 1)); i -= 1; j -= 1
        elif i and np.isclose(D[i, j], D[i - 1, j] + 1):
            out.append((i - 1, None)); i -= 1
        else:
            out.append((None, j - 1)); j -= 1
    return out[::-1]


def lev(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


# ---------------------------------------------------------------- recognition
def recognize(args) -> None:
    import librosa
    import torch
    sys.path.insert(0, str(ROOT / "tts" / "vc"))
    import recognize as R  # tts/vc/recognize.py: pinned repo + revision, cache in tts/vc/cache/hf

    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    m = json.loads(MANIFEST.read_text())
    p, mod = R.model()
    for c in m["clips"]:
        if c["ipa"] is None or c["same_as"]:
            continue
        f = cache / (c["id"] + ".npy")
        if f.exists():
            continue
        x, _ = librosa.load(str(AUDIO / (c["id"] + ".wav")), sr=16000)
        with torch.no_grad():
            lp = mod(p(x, sampling_rate=16000, return_tensors="pt").input_values).logits.log_softmax(-1)[0]
        np.save(f, lp.numpy().astype(np.float16))
    (cache / "_vocab.json").write_text(json.dumps(R._M["v"], ensure_ascii=False))


def greedy(lp: np.ndarray, vocab: dict[int, str]) -> list[dict]:
    """Greedy CTC: tokens with their frame runs (start, end in seconds)."""
    ids = lp.argmax(-1)
    out, prev = [], None
    for f, i in enumerate(ids.tolist()):
        if i != prev:
            t = vocab[i]
            if not t.startswith("<"):
                out.append({"tok": t, "t0": f * FRAME, "t1": (f + 1) * FRAME})
        elif out and vocab[i] == out[-1]["tok"]:
            out[-1]["t1"] = (f + 1) * FRAME
        prev = i
    return out


def units_with_times(toks: list[dict]) -> list[dict]:
    out = []
    for t in toks:
        for u in hyp_units(t["tok"]):
            out.append({"u": u, "t0": t["t0"], "t1": t["t1"], "tok": t["tok"]})
    return out


# ---------------------------------------------------------------- per-word design
# word → (sound class, indices of the tested sound in target_units(word ipa))
SLOTS = {"h2ewsos": ("h2", [0]), "h2owis": ("h2", [0]), "h2egjeti": ("dorsal", [2]), "gjenh1tor": ("dorsal", [0]),
         "kjlewos": ("dorsal", [0]), "bhreh2ter": ("murmur", [0]), "dhugh2ter": ("murmur", [0]),
         "gwhenti": ("murmur", [0]), "kwetwores": ("kw", [0, 1]), "h3esth1": ("h3", [0, 1]),
         "wlkwos": ("syllabic", [1, 2]), "kmtom": ("syllabic", [1, 2]), "ph2ter": ("vocalized", [1]),
         "dyews": ("accent", []), "h1esti": ("h1", [0])}


def slot_hyp(pairs, slot: list[int]) -> tuple[list[int], list[int]]:
    """Hyp indices in the tested slot (aligned to it, or inserted inside/right after it) and inserted right before."""
    pos = [k for k, (r, _) in enumerate(pairs) if r in slot]
    if not pos:
        return [], []
    a, b = pos[0], pos[-1]
    while b + 1 < len(pairs) and pairs[b + 1][0] is None:
        b += 1
    pre, k = [], a - 1
    while k >= 0 and pairs[k][0] is None:
        pre.insert(0, pairs[k][1]); k -= 1
    return [h for _, h in pairs[a:b + 1] if h is not None], pre


# ---------------------------------------------------------------- acoustics
HOP = 0.005


class Acoustic:
    """Frame features of one clip at a 5 ms hop: intensity, voicing/F0 (Praat AC pitch), spectral centroid, HF ratio."""

    def __init__(self, wav: Path):
        import parselmouth
        self.snd = parselmouth.Sound(str(wav))
        self.sr = int(self.snd.sampling_frequency)
        x = self.snd.values[0]
        self.x = x
        win, hop = int(0.015 * self.sr), int(HOP * self.sr)
        n = max(1, (len(x) - win) // hop + 1)
        frames = np.stack([x[i * hop:i * hop + win] for i in range(n)]) * np.hanning(win)
        spec = np.abs(np.fft.rfft(frames, axis=1)) ** 2
        f = np.fft.rfftfreq(win, 1 / self.sr)
        band = (f >= 300) & (f <= 10000)
        tot = spec[:, band].sum(1) + 1e-12
        self.t = (np.arange(n) * hop + win / 2) / self.sr
        self.db = 10 * np.log10(spec.sum(1) + 1e-12)
        self.db -= self.db.max()
        self.centroid = (spec[:, band] * f[band]).sum(1) / tot
        self.hf = spec[:, f >= 2500].sum(1) / (spec[:, f >= 100].sum(1) + 1e-12)
        pitch = self.snd.to_pitch_ac(time_step=HOP, pitch_floor=60, pitch_ceiling=500)
        f0 = np.array([pitch.get_value_at_time(t) or np.nan for t in self.t], dtype=float)
        self.f0 = f0
        self.voiced = ~np.isnan(f0)
        act = np.flatnonzero(self.db > -35)
        self.on = self.t[act[0]] if act.size else 0.0
        self.off = self.t[act[-1]] if act.size else self.t[-1]

    def idx(self, t0: float, t1: float) -> np.ndarray:
        return np.flatnonzero((self.t >= t0) & (self.t < t1))

    def fric_run(self, t0: float, t1: float, *, floor=-40.0) -> tuple[float, float, float]:
        """Longest run of unvoiced energetic frames in [t0, t1): (ms, start time, power-weighted centroid Hz)."""
        ix = self.idx(t0, t1)
        best, cur = (0, None), []
        runs = []
        for i in ix:
            if not self.voiced[i] and self.db[i] > floor:
                cur.append(i)
            else:
                if cur:
                    runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        if not runs:
            return 0.0, t0, float("nan")
        r = max(runs, key=len)
        w = 10 ** (self.db[r] / 10)
        return len(r) * HOP * 1000, float(self.t[r[0]]), float((self.centroid[r] * w).sum() / w.sum())

    def hf_noise(self, t0: float, t1: float, *, ratio=0.3, floor=-35.0) -> dict:
        """Release noise of a stop in [t0, t1): the longest run of frames whose energy is mostly above 2.5 kHz
        (ratio >= 0.3) and above -35 dB, one-frame gaps bridged. A stop burst gives 5-20 ms, an affricate ([dʒ tʃ])
        30-70 ms. Voicing is allowed, so a voiced affricate counts."""
        ix = self.idx(t0, t1)
        on = [i for i in ix if self.hf[i] >= ratio and self.db[i] > floor]
        runs, cur = [], []
        for i in on:
            if cur and i - cur[-1] > 2:
                runs.append(cur); cur = []
            cur.append(i)
        if cur:
            runs.append(cur)
        if not runs:
            return {"noise_ms": 0.0, "noise_t": None, "noise_centroid": None}
        r = max(runs, key=lambda q: q[-1] - q[0])
        return {"noise_ms": (r[-1] - r[0] + 1) * HOP * 1000, "noise_t": round(float(self.t[r[0]]), 3),
                "noise_centroid": round(float(np.mean(self.centroid[r[0]:r[-1] + 1])))}

    def h1h2(self, t0: float, dur: float = 0.04) -> tuple[float | None, float | None]:
        """Mean uncorrected H1–H2 (dB) and HNR (dB) over the first `dur` s of voicing at or after t0."""
        import parselmouth  # noqa: F401
        v = np.flatnonzero(self.voiced & (self.t >= t0))
        if not v.size:
            return None, None
        s = self.t[v[0]]
        vals = []
        n = int(0.04 * self.sr)
        for i in self.idx(s, s + dur):
            if not self.voiced[i]:
                continue
            f0 = self.f0[i]
            c = int(self.t[i] * self.sr)
            seg = self.x[max(0, c - n // 2):c + n // 2]
            if len(seg) < n:
                continue
            sp = 20 * np.log10(np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 8192)) + 1e-9)
            fr = np.fft.rfftfreq(8192, 1 / self.sr)
            pk = lambda h: sp[(fr > h * f0 * 0.85) & (fr < h * f0 * 1.15)].max()  # noqa: E731
            vals.append(pk(1) - pk(2))
        harm = self.snd.extract_part(s, min(s + dur, self.snd.xmax)).to_harmonicity_cc(time_step=0.005,
                                                                                       minimum_pitch=60)
        hv = harm.values[harm.values > -200]
        return (float(np.mean(vals)) if vals else None), (float(np.mean(hv)) if hv.size else None)

    def f0_median(self, t0: float, t1: float) -> float | None:
        ix = self.idx(t0, t1)
        v = self.f0[ix][self.voiced[ix]]
        return float(np.median(v)) if v.size >= 3 else None


# ---------------------------------------------------------------- per clip
def accented_syllable(ipa: str) -> int:
    return next(i for i, s in enumerate(NFD(ipa).split(".")) if ACUTE in s)


def measure_clip(c: dict, word: dict, lp: np.ndarray, vocab: dict[int, str]) -> dict:
    cls, slot = SLOTS[c["word"]]
    ref, rsyl = target_units(word["ipa"])
    toks = greedy(lp, vocab)
    hyp = units_with_times(toks)
    hu = [h["u"] for h in hyp]
    pairs = align(ref, hu)
    rb, hb = [broad(u) for u in ref], [broad(u) for u in hu]
    r = {"recognized": " ".join(t["tok"] for t in toks), "target_units": " ".join(ref),
         "per_strict": lev(ref, hu) / len(ref), "per_broad": lev(rb, hb) / len(rb),
         "insertions": sum(1 for a, _ in pairs if a is None), "class": cls}
    sh, pre = slot_hyp(pairs, slot)
    r["slot"] = [hu[i] for i in sh]
    r["slot_pre"] = [hu[i] for i in pre]
    # first hyp unit aligned to the target before / after the slot (times for the acoustic windows)
    ref2hyp = {a: b for a, b in pairs if a is not None and b is not None}
    ac = Acoustic(AUDIO / (c["id"] + ".wav"))
    r["speech_on"] = round(ac.on, 3)

    def t_of(ri, edge):
        h = ref2hyp.get(ri)
        return None if h is None else hyp[h][edge]

    nxt = (slot[-1] + 1) if slot else None
    if cls == "h1":
        r["onset_noise_ms"] = ac.hf_noise(ac.on - 0.02, ac.on + 0.05)["noise_ms"]
    if cls in ("h2", "h1"):
        tv = t_of(nxt, "t0")
        tv = tv + FRAME if tv is not None else ac.on + 0.3
        ms, t0, cen = ac.fric_run(ac.on - 0.02, max(tv, ac.on + 0.05))
        r["fric_ms"], r["fric_start"], r["fric_centroid"] = ms, round(t0 - ac.on, 3), (None if np.isnan(cen)
                                                                                       else round(cen))
        # onset abruptness for h₁/ʔ: rise of intensity over the first 30 ms of the first voiced frames
        v = np.flatnonzero(ac.voiced & (ac.t >= ac.on))
        if v.size:
            i0 = v[0]
            r["voice_onset"] = round(float(ac.t[i0] - ac.on), 3)
            r["onset_rise_db"] = round(float(ac.db[min(i0 + 6, len(ac.db) - 1)] - ac.db[max(i0 - 2, 0)]), 1)
    if cls in ("dorsal", "murmur"):
        s0 = slot[0]
        ta = ac.on - 0.02 if s0 == 0 else (t_of(s0 - 1, "t1") or ac.on)
        nv = next((i for i in range(slot[-1] + 1, len(ref)) if is_vowel(ref[i]) and i in ref2hyp), None)
        tb = (t_of(nv, "t0") + FRAME) if nv is not None else ta + 0.25
        r["window"] = [round(ta - ac.on, 3), round(tb - ac.on, 3)]
        r.update(ac.hf_noise(ta, tb))
        if cls == "murmur":
            start = r["noise_t"] or ta
            r["h1h2"], r["hnr"] = ac.h1h2(start + 0.01)
            r["asp_ms"] = ac.fric_run(start, start + 0.12)[0]
    # accent: F0 per syllable, boundaries halfway between the aligned vowel nuclei
    nsyl = rsyl[-1] + 1
    acc = accented_syllable(word["ipa"])
    r["accent_syllable"] = acc
    centers = []
    for s in range(nsyl):
        vu = [i for i, u in enumerate(ref) if rsyl[i] == s and is_vowel(u)]
        h = ref2hyp.get(vu[0]) if vu else None
        centers.append(None if h is None or not is_vowel(hu[h]) else (hyp[h]["t0"] + hyp[h]["t1"]) / 2)
    r["syllable_f0"] = None
    if nsyl > 1 and all(x is not None for x in centers) and centers == sorted(centers):
        edges = [ac.on] + [(a + b) / 2 for a, b in zip(centers, centers[1:])] + [ac.off]
        f0s = [ac.f0_median(edges[i], edges[i + 1]) for i in range(nsyl)]
        r["syllable_f0"] = [None if f is None else round(f, 1) for f in f0s]
        if all(f is not None for f in f0s):
            other = max(f for i, f in enumerate(f0s) if i != acc)
            r["accent_st"] = round(12 * np.log2(f0s[acc] / other), 2)
    if nsyl == 1:
        ix = ac.idx(ac.on, ac.off)
        v = ac.f0[ix][ac.voiced[ix]]
        if v.size > 5:
            r["f0_range_st"] = round(float(12 * np.log2(np.percentile(v, 95) / np.percentile(v, 5))), 2)
            k = len(v) // 3
            r["f0_rise_st"] = round(float(12 * np.log2(np.median(v[k:2 * k]) / np.median(v[:k]))), 2)
            r["peak_pos"] = round(float(np.argmax(v) / len(v)), 2)
    for k, v in list(r.items()):
        if isinstance(v, float):
            r[k] = round(v, 3)
    return r


def measure_all(cache: Path) -> dict[str, dict]:
    m = json.loads(MANIFEST.read_text())
    vocab = {int(k): v for k, v in json.loads((cache / "_vocab.json").read_text()).items()}
    words = {w["id"]: w for w in m["words"]}
    out = {}
    for c in m["clips"]:
        if c["ipa"] is None or c["same_as"]:
            continue
        lp = np.load(cache / (c["id"] + ".npy")).astype(np.float32)
        out[c["id"]] = measure_clip(c, words[c["word"]], lp, vocab)
    return out


# ---------------------------------------------------------------- grading
# Each tested sound gets one of correct / near / wrong / missing, from the recognizer's phone(s) in the slot and,
# where the recognizer cannot hear the distinction, from the acoustic measure. The rules are stated in the write-up.
HIT = {"correct": 1.0, "near": 0.5, "wrong": 0.0, "missing": 0.0}
CLASSES = ["h2", "dorsal", "murmur", "kw", "h3", "syllabic", "h1", "accent"]
CLASS_LABEL = {"h2": "χ (h₂)", "dorsal": "ǵ/ḱ", "murmur": "breathy", "kw": "kʷ", "h3": "h₃", "syllabic": "syllabic",
               "h1": "h₁", "accent": "accent", "vocalized": "H̥ → ə"}
DORSAL_FRIC = {"χ", "x", "X"}
FRICATIVE = DORSAL_FRIC | {"h", "ħ", "ç", "ʁ", "ɣ", "ɦ"}
AFFRICATE = {"dʒ", "tʃ", "ʒ", "ʃ", "z", "s", "ts", "dʑ", "tɕ", "ɕ", "ʑ"}
CENTRAL = {"ə", "ʌ", "ɐ", "ɨ", "ɪ", "ᵻ", "ɜ", "ɘ"}
STOP_PLACE = {"bhreh2ter": ("b", "p"), "dhugh2ter": ("d", "t"), "gwhenti": ("ɡ", "k")}
H2_LONG, H2_SOME = 80.0, 30.0       # ms of voiceless frication; eSpeak's [χ] is 130 ms, its [h] 70-80 ms
AFFR_MS = 30.0                      # ms of >2.5 kHz release noise: a stop burst is 5-20 ms, [dʒ tʃ] 25-75 ms
ACCENT_ST = 1.0                     # semitones above the highest other syllable


def cons(us):
    return [u for u in us if not is_vowel(u)]


def grade(r: dict, variant: str, pair: dict | None) -> tuple[str, str]:
    """(grade, basis) for the tested sound of one clip; pair = the same voice's plain-variant clip (murmur)."""
    cls, slot, pre = r["class"], r["slot"], r["slot_pre"]
    sc, pv = cons(slot), any(is_vowel(u) for u in pre)
    if cls == "h2":
        f, lab = r["fric_ms"], set(sc)
        if lab & DORSAL_FRIC:
            g, b = "correct", "recognizer: dorsal fricative"
        elif lab & (FRICATIVE | {"f", "θ", "ʃ"}):   # eSpeak's [χ] is sometimes labelled [f]
            if f >= H2_LONG and variant != "h":
                g, b = "correct", f"acoustic: {f:.0f} ms voiceless frication (recognizer hears [{'/'.join(sorted(lab))}])"
            elif f >= H2_SOME or (f >= H2_LONG and variant == "h"):
                g, b = "near", f"acoustic: {f:.0f} ms frication"
            else:
                g, b = "wrong", f"weak [{'/'.join(sorted(lab))}]: {f:.0f} ms frication, not a dorsal fricative"
        elif sc:
            g, b = ("near", f"acoustic: {f:.0f} ms frication, recognizer [{' '.join(sc)}]") if f >= H2_SOME else \
                ("wrong", f"recognizer: [{' '.join(sc)}]")
        else:
            g, b = ("near", f"acoustic: {f:.0f} ms frication") if f >= H2_SOME else ("missing", "vowel onset")
        if pv and g == "correct":
            g, b = "near", b + "; vowel inserted before it"
        return g, b
    if cls == "dorsal":
        seq = cons(pre) + sc
        n = r.get("noise_ms") or 0.0
        if set(seq) & AFFRICATE:
            return "wrong", f"recognizer: affricate/sibilant [{' '.join(seq)}], {n:.0f} ms release noise"
        if set(seq) & {"ɟ", "c", "ɡʲ", "kʲ"} or ({"ɡ", "k"} & set(seq) and "j" in seq):
            return ("correct", "recognizer: palatal(ized) stop") if n < AFFR_MS + 15 else \
                ("near", f"recognizer: palatal stop, but {n:.0f} ms release noise")
        if seq == ["j"]:
            return ("correct", f"acoustic: [j] with a {n:.0f} ms burst = palatal stop") if 0 < n < AFFR_MS else \
                ("near", "recognizer: [j], no burst")
        if {"ɡ", "k"} & set(seq):
            ins = any(is_vowel(u) for u in slot)
            return "near", "recognizer: plain velar" + (" + inserted [i]" if ins else "")
        return ("wrong", f"recognizer: [{' '.join(seq)}]") if seq else ("missing", "no consonant")
    if cls == "murmur":
        vo, vl = STOP_PLACE[r["word"]]
        seq = cons(pre[-1:] + slot)
        if any(u in seq for u in (vo + "ʰ",)) or (vo in seq and "h" in seq):
            return "correct", "recognizer: voiced stop + aspiration"
        if vo in seq:
            if pair and variant != "plain" and r.get("h1h2") is not None and pair.get("h1h2") is not None \
                    and r.get("hnr") is not None and pair.get("hnr") is not None:
                d1, d2 = r["h1h2"] - pair["h1h2"], r["hnr"] - pair["hnr"]
                if d1 >= 3 and d2 <= -2:
                    return "correct", f"acoustic: H1–H2 {d1:+.1f} dB, HNR {d2:+.1f} dB vs plain"
            return "near", "recognizer: plain voiced stop (murmur not detected)"
        if vl in seq or vl + "ʰ" in seq:
            asp = "h" in seq or vl + "ʰ" in seq or (r.get("asp_ms") or 0) >= 40
            return ("near", "voiceless aspirated stop") if asp else ("wrong", "voiceless unaspirated stop")
        return ("wrong", f"recognizer: [{' '.join(seq)}]") if seq else ("missing", "no stop")
    if cls == "kw":
        if "k" in sc and "w" in slot:
            return "correct", "recognizer: [k w]"
        if ("ɡ" in sc and "w" in slot) or sc == ["k"]:
            return "near", f"recognizer: [{' '.join(slot)}]"
        return ("wrong", f"recognizer: [{' '.join(slot)}]") if sc else ("missing", "no consonant")
    if cls == "h3":
        lab = set(sc)
        w = "w" in slot or "u" in slot
        if lab & {"ɣ", "x", "ʁ", "χ"}:
            return ("correct" if w else "near"), f"recognizer: [{' '.join(slot)}]"
        if "ɡ" in lab or ("h" in lab and w):
            return "near", f"recognizer: [{' '.join(slot)}]"
        return ("wrong", f"recognizer: [{' '.join(slot)}]") if sc else ("missing", "vowel onset")
    if cls == "syllabic":
        res = "l" if r["word"] == "wlkwos" else "m"
        vs = [u for u in slot if is_vowel(u)]
        if res not in slot:
            return ("wrong", f"recognizer: [{' '.join(slot)}]") if slot else ("missing", "nothing")
        if not vs or set(vs) <= CENTRAL:
            return "correct", f"recognizer: [{' '.join(slot)}]"
        return "near", f"recognizer: full vowel [{' '.join(slot)}]"
    if cls == "vocalized":
        vs = [u for u in slot if is_vowel(u)]
        if vs and set(vs) <= CENTRAL:
            return "correct", f"recognizer: [{' '.join(slot)}]"
        return ("near", f"recognizer: full vowel [{' '.join(slot)}]") if vs else ("missing", "no vowel")
    if cls == "h1":
        n = r.get("onset_noise_ms") or 0.0
        if "h" in sc or "ɦ" in sc:
            return ("near", "recognizer: [h] after an inserted vowel") if pv else ("correct", "recognizer: [h]")
        if "ʔ" in sc:
            return "near", "recognizer: [ʔ]"
        if sc and sc[0] in ("f", "x", "ç", "s", "ʃ", "θ") and (r.get("fric_ms") or 0) >= 40:
            return "near", f"acoustic: {r['fric_ms']:.0f} ms voiceless onset (recognizer [{sc[0]}])"
        if sc and sc[0] in ("d", "t", "b", "p", "v"):
            return ("wrong", f"recognizer: [{sc[0]}] with a {n:.0f} ms burst") if n >= 5 else \
                ("near", f"acoustic: no burst under the recognizer's [{sc[0]}] = glottal onset")
        return ("wrong", f"recognizer: [{' '.join(sc)}]") if sc else ("missing", "vowel onset ([ʔ] cannot be verified)")
    return "n/a", ""


def accent_grade(r: dict) -> tuple[str, str] | None:
    if r.get("syllable_f0") is None or r.get("accent_st") is None:
        return None
    a = r["accent_st"]
    if a >= ACCENT_ST:
        return "correct", f"F0 peak on the accented syllable, {a:+.1f} st"
    return ("near", f"F0 peak on the accented syllable, only {a:+.1f} st") if a > 0 else \
        ("wrong", f"F0 peak elsewhere ({a:+.1f} st)")


# ---------------------------------------------------------------- aggregation
VARIANT_PROFILE = {  # variant → how to ask pie.speak for it (PROFILES name, or the pie.ipa dorsal Convention)
    ("h2", "chi"): "default", ("h2", "x"): "h2-velar", ("h2", "voiced-uvular"): "h2-voiced-uvular",
    ("h2", "h"): "h2-h", ("dorsal", "palatal"): "convention dorsals=palatal (default)",
    ("dorsal", "fronted"): "convention dorsals=fronted", ("dorsal", "plain"): "convention dorsals=plain",
    ("murmur", "breathy"): "default", ("murmur", "aspirated"): "murmur-aspirated", ("murmur", "plain"): "murmur-plain",
    ("kw", "labialized"): "default", ("kw", "cluster"): "labiovelar-cluster", ("h3", "gw-labialized"): "default",
    ("h3", "gw-cluster"): "h3-unrounded-w", ("h3", "rw-cluster"): "h3-voiced-uvular-w",
    ("syllabic", "syllabic"): "default", ("syllabic", "schwa"): "syllabic-schwa", ("h1", "h"): "default",
    ("h1", "glottal-stop"): "h1-glottal-stop"}
W_PER, W_HIT = 0.3, 0.7
FORMULA = ("score = 1 + 4 × (0.3 × (1 − min(PER_broad, 1)) + 0.7 × mean over the 8 classes of the best-spelling "
           "hit rate); hit rate = (correct + 0.5 × near) / graded clips")


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def voice_summary(per_clip: dict, sy: str, variants: dict, exclude_word: str | None = None) -> dict:
    """Per-voice PER, per-class hit rates (best spelling and mean over spellings), score and profile.
    Rates over unique audio for PER and accent; spelling comparisons use every row (same_as rows copied)."""
    mine = {k: v for k, v in per_clip.items() if v["system"] == sy and v["word"] != exclude_word}
    uniq = [v for k, v in mine.items() if v["audio_of"] == k]
    cl = {}
    for c in CLASSES + ["vocalized"]:
        if c == "accent":
            gs = [v["accent"] for v in uniq if v["accent"]]
            cl[c] = {"hit": mean([HIT[g] for g in gs]), "n": len(gs),
                     "counts": {g: gs.count(g) for g in HIT if gs.count(g)}}
            continue
        byvar = {}
        for var in variants.get(c, ["default"]):
            rows = [v for v in mine.values() if v["class"] == c and v["variant"] == var]
            if rows:
                byvar[var] = {"hit": mean([HIT[v["grade"]] for v in rows]), "n": len(rows),
                              "grades": {v["word"]: v["grade"] for v in rows}}
        if not byvar:
            continue
        order = variants.get(c, ["default"])
        best = max(byvar, key=lambda k: (byvar[k]["hit"], -order.index(k)))   # ties → the earlier (default) spelling
        cl[c] = {"best_variant": best, "hit": byvar[best]["hit"],
                 "mean_over_variants": mean([b["hit"] for b in byvar.values()]), "by_variant": byvar}
    hits = [cl[c]["hit"] for c in CLASSES if c in cl and cl[c]["hit"] is not None]
    per_b = mean([v["per_broad"] for v in uniq])
    score = 1 + 4 * (W_PER * (1 - min(per_b, 1)) + W_HIT * mean(hits))
    prof = {c: {"variant": cl[c]["best_variant"], "spell": VARIANT_PROFILE.get((c, cl[c]["best_variant"]))}
            for c in CLASSES if c in cl and "best_variant" in cl[c]}
    return {"per_strict": mean([v["per_strict"] for v in uniq]), "per_broad": per_b,
            "insertions_per_clip": mean([v["insertions"] for v in uniq]), "clips": len(uniq),
            "classes": cl, "score": score, "profile": prof}


def rounded(x):
    if isinstance(x, float):
        return round(x, 3)
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rounded(v) for v in x]
    return x


def analyze(args) -> None:
    cache = Path(args.cache)
    raw = json.loads((cache / "_raw.json").read_text())
    m = json.loads(MANIFEST.read_text())
    variants = {t["id"]: [v["id"] for v in t["variants"]] for t in m["targets"]}
    clips = {c["id"]: c for c in m["clips"]}
    systems = [s["id"] for s in m["systems"]]
    per_clip = {}
    for cid, c in clips.items():
        if c["ipa"] is None:
            continue
        src = c["same_as"] or cid
        r = dict(raw[src], word=c["word"])
        pair = None
        if r["class"] == "murmur":
            pid = f"{c['word']}__plain__{c['system']}"
            pc = clips.get(pid)
            pair = raw.get((pc["same_as"] or pid)) if pc and pc["ipa"] else None
        g, basis = grade(r, c["variant"], pair)
        ag = accent_grade(r)
        per_clip[cid] = {"word": c["word"], "variant": c["variant"], "system": c["system"], "audio_of": src,
                         "class": r["class"], "recognized": r["recognized"], "target": r["target_units"],
                         "per_strict": r["per_strict"], "per_broad": r["per_broad"], "insertions": r["insertions"],
                         "slot": " ".join(r["slot"]), "grade": g, "basis": basis,
                         "accent": ag[0] if ag else None, "accent_basis": ag[1] if ag else None,
                         "measures": {k: v for k, v in raw[src].items() if k not in (
                             "recognized", "target_units", "per_strict", "per_broad", "insertions", "slot",
                             "slot_pre", "class")}}
    voices = {sy: voice_summary(per_clip, sy, variants) for sy in systems}
    kokoro = [s for s in systems if s.startswith("kokoro-")]
    by_class = {}
    for c in CLASSES + ["vocalized"]:
        cand = [s for s in kokoro if c in voices[s]["classes"]]
        if not cand:
            continue
        key = lambda s: (voices[s]["classes"][c]["hit"] or 0, voices[s]["classes"][c].get("mean_over_variants") or 0,  # noqa: E731
                         -voices[s]["per_broad"])
        top = max(key(s)[:2] for s in cand)
        best_voices = [s for s in sorted(cand, key=key, reverse=True) if key(s)[:2] == top]
        entry = {"best_voices": best_voices, "best_hit": top[0]}
        if c != "accent":
            vh = {}
            for var in variants.get(c, ["default"]):
                xs = [voices[s]["classes"][c]["by_variant"].get(var, {}).get("hit") for s in kokoro]
                xs = [x for x in xs if x is not None]
                if xs:
                    vh[var] = mean(xs)
            entry["variant_hit_kokoro_mean"] = vh
            entry["best_variant"] = max(vh, key=vh.get)
        e = voices["espeak-tone"]["classes"].get(c)
        entry["espeak"] = e and e["hit"]
        by_class[c] = entry
    ranking = sorted(kokoro, key=lambda s: -voices[s]["score"])
    # stability: drop one word at a time (15 runs) and count how often each voice is in the top 3
    top3_count = {s: 0 for s in kokoro}
    for w in sorted({v["word"] for v in per_clip.values()}):
        sc = {s: voice_summary(per_clip, s, variants, exclude_word=w)["score"] for s in kokoro}
        for s in sorted(kokoro, key=lambda s: -sc[s])[:3]:
            top3_count[s] += 1
    out = {"schema": "pie-tts-bakeoff-objective/1", "manifest": "tts/bakeoff/manifest.json",
           "recognizer": "facebook/wav2vec2-xlsr-53-espeak-cv-ft@2c733782da5604684829819a5eb744c193fe9398",
           "note": "machine estimates from a phone recognizer and acoustic measures; not listening judgements",
           "formula": FORMULA, "thresholds": {"h2_frication_correct_ms": H2_LONG, "h2_frication_near_ms": H2_SOME,
                                              "affricate_release_noise_ms": AFFR_MS, "accent_correct_st": ACCENT_ST},
           "ranking": ranking, "top3": ranking[:3],
           "top3_leave_one_word_out": {s: n for s, n in sorted(top3_count.items(), key=lambda kv: -kv[1]) if n}, "voices": voices, "by_class": by_class, "clips": per_clip}
    OUT_JSON.write_text(json.dumps(rounded(out), ensure_ascii=False, indent=1) + "\n")
    report(out)


def report(o: dict) -> None:
    f = lambda x: "–" if x is None else f"{x:.2f}"  # noqa: E731
    print("| voice | score | PER broad | PER strict | ins/clip | " + " | ".join(CLASS_LABEL[c] for c in CLASSES)
          + " |")
    print("|---" * (5 + len(CLASSES)) + "|")
    for s in ["espeak-tone"] + o["ranking"]:
        v = o["voices"][s]
        print(f"| {s.replace('kokoro-', '')} | {v['score']:.2f} | {v['per_broad']:.2f} | {v['per_strict']:.2f} | "
              f"{v['insertions_per_clip']:.1f} | " + " | ".join(
                  f(v["classes"].get(c, {}).get("hit")) + (f" ({v['classes'][c]['best_variant']})"
                                                           if "best_variant" in v["classes"].get(c, {}) else "")
                  for c in CLASSES) + " |")
    print()
    for c, e in o["by_class"].items():
        print(c, e)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("recognize", "measure", "analyze"):
        p = sub.add_parser(name)
        p.add_argument("--cache", required=True, help="directory for log-probs and raw measures (not in the repo)")
    a = ap.parse_args(argv)
    if a.cmd == "recognize":
        recognize(a)
    elif a.cmd == "measure":
        raw = measure_all(Path(a.cache))
        (Path(a.cache) / "_raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=0))
        print(len(raw), "clips measured")
    else:
        analyze(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
