"""Objective checks for the eSpeak + voice-conversion test (docs/research/tts-voice-conversion.md).

    tts/vc/.venv-eval/bin/python -I tts/vc/evaluate.py         # -> tts/vc/results.json
Per clip (each VC method x timbre, and raw pitch-patched Kokoro for comparison), against the eSpeak source:
- per_src: phone edit distance between recognizer output on the source and on the clip, / source length.
  The recognizer (recognize.py) is itself unreliable on these sounds (it never emits χ, ʔ or murmured stops),
  so this measures stability of what it hears, not correctness. per_src_base does the same after folding
  length, tone digits, aspiration/murmur and ɡ/g (BASE below).
- post_dtw: mean cosine distance between the recognizer's frame-level CTC logits for source and clip along
  the DTW path (librosa.sequence.dtw). Continuous, so less jumpy than the greedy phone string on 1 s clips.
- per_ipa: base-character edit distance between the clip's recognized phones and the converter IPA, / IPA length.
- f0_r: Pearson r of F0 in semitones on a common normalised-time grid (speech span, 200 points), frames voiced
  in both; F0 from Praat autocorrelation (parselmouth, 10 ms, 50-600 Hz),
  octave jumps folded to within 6 st of the clip median.
- peak_src / peak: normalised time of the F0 maximum; peak_ok if within 0.12.
- contrast_src / contrast: mean semitone difference between the frames that are high in the source (eSpeak's
  level high tone = the accented syllable) and the rest; contrast_ratio = clip / source.
- onset_ms: voiceless noise before voicing starts (onset_unvoiced_ms); the χ check for χ-initial words.
- dur_ratio: speech-span length of the clip / source (librosa trim at 35 dB), len_ratio: whole-file length."""
import json
import re
import unicodedata
from pathlib import Path

import librosa
import numpy as np
import parselmouth

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recognize import decode, logits  # noqa: E402

VC = Path(__file__).resolve().parent
AUDIO = VC / "audio"
METHODS = ["knnvc", "openvoice", "seedvc", "seedvc-f0"]
TIMBRES = ["hm_omega", "ef_dora", "em_alex"]
TIMBRES2 = ["bf_isabella", "af_nicole", "em_santa"]  # fair-comparison round (words.SUBSET only)
GRID = np.linspace(0, 1, 200)


def base(tok: str) -> str:
    s = unicodedata.normalize("NFD", tok)
    s = re.sub(r"[ːˑ0-9ˈˌ.̀-ͯ‖|ʰʱ]", "", s).replace("ɡ", "g")
    return s


def lev(a, b) -> int:
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[-1]


def per(ref, hyp) -> float:
    return round(lev(ref, hyp) / max(1, len(ref)), 3)


def span(wav):
    y, sr = librosa.load(wav, sr=16000)
    _, (a, b) = librosa.effects.trim(y, top_db=35)
    return a / sr, b / sr, len(y) / sr


def f0_track(wav):
    a, b, total = span(wav)
    snd = parselmouth.Sound(str(wav))
    p = snd.to_pitch_ac(time_step=0.01, pitch_floor=50, pitch_ceiling=600)
    t, f = p.xs(), p.selected_array["frequency"]
    keep = (t >= a) & (t <= b)
    t, f = (t[keep] - a) / max(b - a, 1e-6), f[keep]
    st = np.where(f > 0, 12 * np.log2(np.maximum(f, 1) / 100), np.nan)
    if (~np.isnan(st)).any():
        # fold octave errors: the accent contrast is ~3 st, so any frame > 6 st from the median is a tracker jump
        med = np.nanmedian(st)
        st = st - 12 * np.round((st - med) / 12)
    # nearest-frame lookup on the grid (no interpolation across unvoiced gaps)
    idx = np.clip(np.searchsorted(t, GRID), 0, len(t) - 1) if len(t) else np.zeros(len(GRID), int)
    g = st[idx] if len(t) else np.full(len(GRID), np.nan)
    return g, (a, b, total)


def onset_unvoiced_ms(wav):
    """Length of the voiceless noise before voicing starts (Praat unvoiced, RMS within 35 dB of the clip max).
    For χ-initial words this is the χ itself: if a converter drops or voices it, the value collapses."""
    a, b, _ = span(wav)
    p = parselmouth.Sound(str(wav)).to_pitch_ac(time_step=0.01, pitch_floor=50, pitch_ceiling=600)
    y, sr = librosa.load(wav, sr=16000)
    rms = librosa.feature.rms(y=y, frame_length=400, hop_length=160)[0]
    db = 20 * np.log10(np.maximum(rms, 1e-6) / rms.max())
    n, t = 0, a
    while t < b:
        f = p.get_value_at_time(t)
        if f == f and f > 0:  # voiced (NaN when unvoiced)
            break
        if db[min(int(t * 100), len(db) - 1)] > -35:
            n += 1
        t += 0.01
    return n * 10


def compare(src, clip):
    out = {}
    gs, (sa, sb, stot) = src["f0"], src["span"]
    gc, (ca, cb, ctot) = f0_track(clip)
    both = ~np.isnan(gs) & ~np.isnan(gc)
    out["f0_r"] = round(float(np.corrcoef(gs[both], gc[both])[0, 1]), 3) if both.sum() >= 10 else None
    out["peak_src"] = round(float(GRID[np.nanargmax(gs)]), 3)
    out["peak"] = round(float(GRID[np.nanargmax(gc)]), 3) if (~np.isnan(gc)).any() else None
    out["peak_ok"] = out["peak"] is not None and abs(out["peak"] - out["peak_src"]) <= 0.12
    high = src["high"]
    vc = ~np.isnan(gc)
    if (high & vc).any() and (~high & vc).any():
        out["contrast"] = round(float(np.nanmean(gc[high & vc]) - np.nanmean(gc[~high & vc])), 2)
        out["contrast_ratio"] = round(out["contrast"] / src["contrast"], 2) if src["contrast"] else None
    else:
        out["contrast"] = out["contrast_ratio"] = None
    out["contrast_src"] = src["contrast"]
    out["onset_src_ms"] = src["onset"]
    out["onset_ms"] = onset_unvoiced_ms(clip)
    out["dur_ratio"] = round((cb - ca) / (sb - sa), 3)
    out["len_ratio"] = round(ctot / stot, 3)
    lg = logits(str(clip))
    rec = decode(lg)
    D, wp = librosa.sequence.dtw(X=src["logits"].T, Y=lg.T, metric="cosine")
    out["post_dtw"] = round(float(D[-1, -1] / len(wp)), 3)
    out["rec"] = " ".join(rec)
    out["per_src"] = per(src["rec"], rec)
    out["per_src_base"] = per([base(x) for x in src["rec"]], [base(x) for x in rec])
    out["per_ipa"] = per(list(src["ipa_base"]), list("".join(base(x) for x in rec)))
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(float(np.mean(xs)), 3) if xs else None


CHI = ("h2ewsos", "h2owis", "h2egjeti", "hymn-1")  # χ-initial items


def summarize(rows):
    if not rows:
        return None
    chi = [r["onset_ms"] / r["onset_src_ms"] for r in rows if r["id"] in CHI and r["onset_src_ms"]]
    return dict(chi_onset_ratio=mean(chi), n=len(rows), per_src=mean([r["per_src"] for r in rows]), post_dtw=mean([r["post_dtw"] for r in rows]),
                per_src_base=mean([r["per_src_base"] for r in rows]), per_ipa=mean([r["per_ipa"] for r in rows]),
                f0_r=mean([r["f0_r"] for r in rows]), f0_r_median=round(float(np.median([r["f0_r"] for r in rows if r["f0_r"] is not None])), 3),
                peak_ok=mean([float(r["peak_ok"]) for r in rows]),
                contrast_ratio=mean([r["contrast_ratio"] for r in rows]), dur_ratio=mean([r["dur_ratio"] for r in rows]),
                len_ratio=mean([r["len_ratio"] for r in rows]))


srcs = {s["id"]: s for s in json.loads((AUDIO / "espeak.json").read_text("utf-8"))}
for s in srcs.values():
    s["f0"], s["span"] = f0_track(s["wav"])
    v = s["f0"][~np.isnan(s["f0"])]
    thr = (np.percentile(v, 10) + np.percentile(v, 90)) / 2
    s["high"] = ~np.isnan(s["f0"]) & (s["f0"] > thr)
    s["contrast"] = round(float(np.nanmean(s["f0"][s["high"]]) - np.nanmean(s["f0"][~s["high"] & ~np.isnan(s["f0"])])), 2)
    s["onset"] = onset_unvoiced_ms(s["wav"])
    s["logits"] = logits(s["wav"])
    s["rec"] = decode(s["logits"])
    s["ipa_base"] = "".join(base(c) for c in s["ipa"] if not c.isspace())
    s["per_ipa"] = per(list(s["ipa_base"]), list("".join(base(x) for x in s["rec"])))
    print("src", s["id"], " ".join(s["rec"]), flush=True)

# Control: the source itself pitch-shifted by +3 semitones (librosa phase vocoder). Same phones, different F0
# level and a slightly shifted spectrum: the recognizer's noise floor for per_src on these short clips.
ctrl = AUDIO / "ctrl"
ctrl.mkdir(exist_ok=True)
for sid, s in srcs.items():
    out = ctrl / f"{sid}.ctrl-shift3-none.wav"
    if not out.exists():
        y, sr = librosa.load(s["wav"], sr=None)
        import soundfile as sf
        sf.write(out, librosa.effects.pitch_shift(y, sr=sr, n_steps=3), sr)
    # Control 2: AAC 48 kb/s round trip of the source (what the listening page plays). Control 3,
    # ctrl-espeak-p80, is rendered by render_pie.py: the same eSpeak codes at eSpeak pitch 80.
    out = ctrl / f"{sid}.ctrl-aac-none.wav"
    if not out.exists():
        import subprocess
        m4 = ctrl / f"{sid}.aac.mp4"
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", s["wav"], str(m4)], check=True)
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(m4), str(out)], check=True)

clips = []
systems = [(m, f"{m}-{{v}}", AUDIO / m) for m in METHODS] + [("kokoro", "kokoro-pitch-{v}", AUDIO / "kokoro"),
                                                               ("kokoro-prof", "kokoro-prof-{v}", AUDIO / "kokoro-prof"),
                                                               ("ctrl-shift3", "ctrl-shift3-{v}", ctrl),
                                                               ("ctrl-aac", "ctrl-aac-{v}", ctrl),
                                                               ("ctrl-espeak-p80", "ctrl-espeak-p80-{v}", ctrl)]
for method, pat, d in systems:
    for v in (["none"] if method.startswith("ctrl") else TIMBRES + TIMBRES2):
        for sid, s in srcs.items():
            wav = d / f"{sid}.{pat.format(v=v)}.wav"
            if not wav.exists():
                continue
            r = dict(id=sid, method=method, timbre=v, wav=str(wav), **compare(s, wav))
            clips.append(r)
            print(method, v, sid, r["per_src"], r["f0_r"], r["dur_ratio"], flush=True)

summary = {}
SUB = ("h2ewsos", "h2egjeti", "kjlewos", "bhreh2ter", "hymn-1", "hymn-2")


def split(rows):
    return dict(all=summarize(rows), words=summarize([r for r in rows if not r["id"].startswith("hymn")]),
                lines=summarize([r for r in rows if r["id"].startswith("hymn")]))


for method in METHODS + ["kokoro", "kokoro-prof", "ctrl-shift3", "ctrl-aac", "ctrl-espeak-p80"]:
    rows = [r for r in clips if r["method"] == method]
    if not rows:
        continue
    main = [r for r in rows if r["timbre"] in TIMBRES + ["none"]]
    top = [r for r in rows if r["timbre"] in TIMBRES2]
    summary[method] = dict(**(split(main) if main else {}),
                           # the six-item subset, on the first timbres (comparable with top3) and on the top-3 voices
                           subset={k: v for k, v in split([r for r in main if r["id"] in SUB]).items()} if main else None,
                           top3=split(top) if top else None,
                           **{v: split([r for r in rows if r["timbre"] == v])
                              for v in TIMBRES + TIMBRES2 + ["none"] if any(r["timbre"] == v for r in rows)})
# controls on the six-item subset (noise floor for the top3 comparison)
sources = {sid: dict(rec=" ".join(s["rec"]), ipa=s["ipa"], per_ipa=s["per_ipa"], contrast=s["contrast"], onset_ms=s["onset"],
                     peak=round(float(GRID[np.nanargmax(s["f0"])]), 3)) for sid, s in srcs.items()}
summary["espeak-source"] = dict(per_ipa=mean([s["per_ipa"] for s in sources.values()]))
(VC / "results.json").write_text(json.dumps(dict(summary=summary, sources=sources, clips=clips),
                                            ensure_ascii=False, indent=1), "utf-8")
print(json.dumps(summary, indent=1))
