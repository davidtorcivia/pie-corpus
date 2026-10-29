"""TTS finals: the finalist systems on the 18 hard words and lines of tts/vc/manifest.json and 10 corpus hymns,
for the owner's ratings (page: tts/finals/index.html, manifest: tts/finals/manifest.json).

Systems: eSpeak tone (accuracy reference); Kokoro + pitch patch with each voice's recommended profile
(docs/research/tts-bakeoff-objective.md, tts/vc/words.VOICE_PROFILE); eSpeak -> Seed-VC F0 mode
(docs/research/tts-voice-conversion.md) into em_santa, em_alex, bf_isabella, af_nicole.

Run from the repo root, each step in its env:
    python3 tts/finals/finals.py items                                  # -> tts/finals/items.json (HEAD corpus)
    .venv/bin/python -I tts/finals/finals.py espeak                     # eSpeak sources + Seed-VC segments
    .venv-kokoro/bin/python -I tts/finals/finals.py kokoro              # Kokoro + profile, 3 voices
    python3 tts/finals/finals.py queue --voices a,b [--shift N] [--items x,y] [--trial]
    tts/finals/workers.sh N                                             # N Seed-VC workers on the queue
    python3 tts/finals/finals.py join                                   # segment outputs -> one wav per item
    tts/vc/.venv-eval/bin/python -I tts/finals/finals.py shifts         # semitone-shift trials -> shift_trials.json
    tts/vc/.venv-eval/bin/python -I tts/finals/finals.py eval           # -> tts/finals/results.json
    tts/vc/.venv-eval/bin/python -I tts/finals/finals.py build          # sprites, manifest.json, files.json

Long sources (the hymns) are cut for Seed-VC at eSpeak's pauses into segments of at most SEG_MAX seconds,
converted one by one and joined in order. With a 25 s reference prompt Seed-VC's own window holds only about
5 s of source; cutting at pauses puts every seam in silence instead of wherever its window ends.
Audio (tts/finals/audio/) is gitignored; items.json, results.json, manifest.json, files.json and the page are
committed. Paths in the committed files are repo-relative."""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIN = ROOT / "tts" / "finals"
AUDIO = FIN / "audio"
VC = ROOT / "tts" / "vc"
QUEUE = AUDIO / "queue"
SCHEMA = "pie-tts-bakeoff/1"

# Record ids in the Voice Lab's order; text read from corpus/tier3/<work>.jsonl at HEAD.
HYMNS = ["t3-t026-00015", "t3-t026-00016", "t3-t026-00017", "t3-t026-00001", "t3-t026-00005",
         "t3-t005-00001", "t3-t005-00005", "t3-t032-00001", "t3-t032-00003", "t3-t002-00001"]
KOKORO_VOICES = ["bf_isabella", "af_nicole", "em_santa"]
VC_VOICES = ["em_santa", "em_alex", "bf_isabella", "af_nicole"]
FEMALE = ["bf_isabella", "af_nicole"]
SHIFT_TRIALS = [0, 5, 7, 9, 11, 13]
TRIAL_ITEMS = ["kjlewos", "hymn-1"]
SEG_MAX = 4.6          # seconds per Seed-VC segment (its source window is ~5.0 s beside a 25 s prompt)
SPRITE_GAP = 0.5       # seconds of silence between clips in a sprite (as scripts/tts_bakeoff.py)
TARGET_DBFS = -20.0    # page loudness: speech RMS level of every clip, peak capped at -1 dBFS


def rel(p) -> str:
    return str(Path(p).resolve().relative_to(ROOT))


def load(name):
    return json.loads((FIN / name).read_text("utf-8")) if (FIN / name).exists() else None


def save(name, obj):
    (FIN / name).parent.mkdir(parents=True, exist_ok=True)
    (FIN / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", "utf-8")


def systems() -> list[dict]:
    sys.path.insert(0, str(VC))
    from words import VOICE_PROFILE
    out = [{"id": "finals-espeak-tone", "label": "eSpeak (tone)", "short": "eSpeak", "family": "espeak",
            "language": "pie (hi base)", "licence": "GPL-3.0 engine; output unrestricted", "reference": True,
            "group": "eSpeak"}]
    for v in KOKORO_VOICES:
        prof, dors = VOICE_PROFILE[v]
        out.append({"id": f"finals-kokoro-{v}", "label": f"Kokoro {v} ({prof} + dorsals={dors})", "short": v,
                    "family": "kokoro", "voice": v, "profile": prof, "dorsals": dors, "licence": "Apache-2.0",
                    "reference": False, "group": "Kokoro + profile"})
    for v in VC_VOICES:
        out.append({"id": f"finals-seedvc-f0-{v}", "label": f"eSpeak→Seed-VC F0 {v}", "short": v, "family": "vc",
                    "method": "seedvc-f0", "voice": v, "licence": "GPL-3.0 (Seed-VC code and weights)",
                    "repo": "Plachtaa/seed-vc@51383ef", "reference": False, "group": "eSpeak → Seed-VC F0"})
    return out


def wav_path(system: str, item: str) -> Path:
    return AUDIO / system / f"{item}.wav"


# ---------------------------------------------------------------- items

def items(_):
    vc = json.loads((VC / "manifest.json").read_text("utf-8"))
    rows = []
    for hid in HYMNS:
        work = hid.split("-")[1]
        text = subprocess.run(["git", "show", f"HEAD:corpus/tier3/{work}.jsonl"], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout
        rec = next(json.loads(ln) for ln in text.splitlines() if ln.strip() and json.loads(ln)["id"] == hid)
        rows.append({"id": hid, "kind": "hymn", "pie": rec["pie"], "english": rec["english"],
                     "genre": rec.get("genre"), "theme": rec.get("theme"), "meter": rec.get("meter"),
                     "source": f"corpus/tier3/{work}.jsonl@HEAD"})
    for w in vc["words"]:
        kind = "line" if w["target"] == "line" else "word"
        rows.append({"id": w["id"], "kind": kind, "pie": w["pie"], "english": w["gloss"], "target": w["target"],
                     "sound": w.get("sound"), "source": "tts/vc/manifest.json"})
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    save("items.json", {"corpus_head": head, "items": rows})
    print(len(rows), "items;", sum(r["kind"] == "hymn" for r in rows), "hymns at", head)


# ---------------------------------------------------------------- eSpeak (+ segments for Seed-VC)

def read_wav(path):
    """Mono float32 samples and rate; soundfile when present (Seed-VC writes float wavs), else stdlib wave."""
    import numpy as np
    try:
        import soundfile as sf
    except ImportError:
        with wave.open(str(path)) as w:
            assert w.getsampwidth() == 2, path
            a = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype("float32") / 32768
            if w.getnchannels() > 1:
                a = a.reshape(-1, w.getnchannels()).mean(1)
            return a, w.getframerate()
    a, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if a.ndim > 1:
        a = a.mean(1)
    return np.asarray(a, dtype="float32"), sr


def write_pcm16(path, a, sr):
    import numpy as np
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 32767 / 32768) * 32768).astype("<i2").tobytes())


def segment_points(a, sr, seg_max=SEG_MAX, min_gap=0.03):
    """Cut points (samples) in the middle of quiet runs (10 ms RMS 40 dB under the max, >= min_gap long). eSpeak's
    sentence pause in pie-tone is short (30-60 ms, no longer than a stop closure), so the cut is the longest quiet
    run in the second half of each window of seg_max seconds: a pause or a closure, never inside voicing."""
    import numpy as np
    f = int(0.01 * sr)
    n = len(a) // f
    rms = np.sqrt((a[: n * f].reshape(n, f) ** 2).mean(1) + 1e-12)
    quiet = 20 * np.log10(rms / rms.max()) < -40
    runs, i = [], 0          # (middle sample, length in frames)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_gap and i > 0 and j < n:
                runs.append((((i + j) // 2) * f, j - i))
            i = j
        else:
            i += 1
    cuts, start = [], 0
    limit = int(seg_max * sr)
    while len(a) - start > limit:
        ok = [r for r in runs if start + limit // 2 < r[0] <= start + limit] or \
             [r for r in runs if start < r[0] <= start + limit]
        if ok:
            nxt = max(ok, key=lambda r: (r[1], r[0]))[0]
        else:
            later = [r for r in runs if r[0] > start]
            if not later:
                break
            nxt = later[0][0]       # no quiet run in reach: a longer segment (Seed-VC then chunks it itself)
        cuts.append(nxt)
        start = nxt
    return cuts


def espeak(_):
    sys.path.insert(0, str(ROOT))
    from pie.ipa import to_ipa
    from pie.speak import engine_input, speak
    it = load("items.json")["items"]
    rows = []
    for r in it:
        out = wav_path("finals-espeak-tone", r["id"])
        res = speak(r["pie"], backend="espeak", out_wav=str(out), tone=True)
        a, sr = read_wav(out)
        cuts = segment_points(a, sr)
        bounds = [0, *cuts, len(a)]
        segs = []
        for k, (s0, s1) in enumerate(zip(bounds, bounds[1:])):
            p = AUDIO / "espeak-seg" / f"{r['id']}.s{k:02d}.wav"
            write_pcm16(p, a[s0:s1], sr)
            segs.append({"wav": rel(p), "start": round(s0 / sr, 4), "seconds": round((s1 - s0) / sr, 4)})
        rows.append({"id": r["id"], "pie": r["pie"], "ipa": to_ipa(r["pie"], tone=True), "wav": rel(out),
                     "engine_input": engine_input(to_ipa(r["pie"], tone=True), backend="espeak"),
                     "round_trip": res.round_trip, "seconds": round(len(a) / sr, 3), "segments": segs})
        print(r["id"], rows[-1]["seconds"], "s,", len(segs), "segments, longest",
              max(s["seconds"] for s in segs), flush=True)
    save("audio/espeak.json", rows)


# ---------------------------------------------------------------- Kokoro + profile

def kokoro(_):
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(VC))
    import torch
    from pie.ipa import Convention, to_ipa
    from pie.speak import engine_input, speak
    from words import VOICE_PROFILE
    it = load("items.json")["items"]
    rows = []
    for v in KOKORO_VOICES:
        prof, dors = VOICE_PROFILE[v]
        conv = Convention(dors, dorsals=dors)
        for r in it:
            out = wav_path(f"finals-kokoro-{v}", r["id"])
            torch.manual_seed(0)
            res = speak(r["pie"], backend="kokoro", out_wav=str(out), convention=conv, tone=True, voice=v,
                        pitch=True, profile=prof)
            vipa = to_ipa(r["pie"], convention=conv, tone=True)
            rows.append({"id": r["id"], "voice": v, "profile": prof, "dorsals": dors, "ipa": res.ipa,
                         "engine_input": engine_input(vipa, backend="kokoro", voice=v, profile=prof),
                         "speed": 0.9, "seed": 0, "wav": rel(out)})
            print(v, r["id"], flush=True)
    save("audio/kokoro.json", rows)


# ---------------------------------------------------------------- Seed-VC queue

def trial_dir(voice, shift):
    return AUDIO / "trials" / f"{voice}{shift:+d}"


def queue(a):
    srcs = load("audio/espeak.json")
    voices = a.voices.split(",")
    keep = set(a.items.split(",")) if a.items else None
    for d in ("pending", "claimed", "done"):
        (QUEUE / d).mkdir(parents=True, exist_ok=True)
    n = 0
    for v in voices:
        shift = a.shift if a.shift is not None else 0
        for s in srcs:
            if keep and s["id"] not in keep:
                continue
            base = trial_dir(v, shift) if a.trial else AUDIO / f"finals-seedvc-f0-{v}"
            for k, seg in enumerate(s["segments"]):
                out = base / "seg" / f"{s['id']}.s{k:02d}.wav"
                if out.exists() and not a.force:
                    continue
                # longest jobs first, so the pool drains evenly; prefix = priority
                name = f"{a.priority}-{int(9999 - seg['seconds'] * 100):04d}-{v}{shift:+d}-{s['id']}.s{k:02d}.json"
                job = {"source": str(ROOT / seg["wav"]), "voice": v, "shift": shift, "out": str(out),
                       "item": s["id"], "segment": k}
                (QUEUE / "pending" / name).write_text(json.dumps(job), "utf-8")
                n += 1
    print(n, "jobs queued")


def join(_):
    import numpy as np
    import soundfile as sf
    srcs = load("audio/espeak.json")
    bases = [AUDIO / f"finals-seedvc-f0-{v}" for v in VC_VOICES]
    bases += sorted(p for p in (AUDIO / "trials").glob("*") if p.is_dir()) if (AUDIO / "trials").exists() else []
    made = missing = 0
    for b in bases:
        for s in srcs:
            parts = [b / "seg" / f"{s['id']}.s{k:02d}.wav" for k in range(len(s["segments"]))]
            if not parts[0].exists():
                continue
            if not all(p.exists() for p in parts):
                missing += 1
                print("incomplete", b.name, s["id"], flush=True)
                continue
            out = b / f"{s['id']}.wav"
            if out.exists() and out.stat().st_mtime >= max(p.stat().st_mtime for p in parts):
                continue
            ys, sr = [], None
            for p in parts:
                y, r = read_wav(p)
                sr = sr or r
                assert r == sr, p
                ys.append(y)
            sf.write(str(out), np.concatenate(ys), sr, subtype="FLOAT")
            made += 1
    print(made, "joined;", missing, "incomplete")


# ---------------------------------------------------------------- measures

def f0_hz(wav):
    import numpy as np
    import parselmouth
    p = parselmouth.Sound(str(wav)).to_pitch_ac(time_step=0.01, pitch_floor=50, pitch_ceiling=600)
    f = p.selected_array["frequency"]
    return f[f > 0] if len(f) else np.zeros(0)


def voice_range(voice):
    """The target voice's F0 range from its Seed-VC reference clip (the first 25 s, what Seed-VC hears):
    median and interquartile range in Hz. The interquartile range, not 10-90 %, because the tracker halves
    af_nicole's breathy/creaky frames (its 10th percentile is 80 Hz)."""
    import numpy as np
    import parselmouth
    snd = parselmouth.Sound(str(VC / "audio" / "ref" / f"{voice}.wav"))
    snd = snd.extract_part(0, min(25, snd.duration))
    f = snd.to_pitch_ac(time_step=0.01, pitch_floor=50, pitch_ceiling=600).selected_array["frequency"]
    f = f[f > 0]
    q = np.percentile(f, [10, 25, 50, 75, 90])
    return {k: round(float(x), 1) for k, x in zip(("p10", "p25", "median", "p75", "p90"), q)}


def st(a, b):
    import math
    return 12 * math.log2(a / b)


def shifts(_):
    """Semitone-shift trials for the female targets: median F0 of the converted trial clips vs the target
    voice's range; the chosen shift is the one whose median is nearest the voice's median (in semitones) among
    those inside its interquartile range."""
    import numpy as np
    sys.path.insert(0, str(VC))
    from evaluate import compare, prepare_source
    srcs = {s["id"]: s for s in load("audio/espeak.json")}
    src_med = {i: float(np.median(f0_hz(ROOT / srcs[i]["wav"]))) for i in TRIAL_ITEMS}
    prepared = {i: prepare_source({**srcs[i], "wav": str(ROOT / srcs[i]["wav"])}) for i in TRIAL_ITEMS}
    out = {"items": TRIAL_ITEMS, "source_median_hz": {i: round(v, 1) for i, v in src_med.items()}, "voices": {}}
    for v in FEMALE:
        rng = voice_range(v)
        trials = []
        for sh in SHIFT_TRIALS:
            d = trial_dir(v, sh)
            wavs = [d / f"{i}.wav" for i in TRIAL_ITEMS]
            if not all(w.exists() for w in wavs):
                continue
            meds = [float(np.median(f0_hz(w))) for w in wavs]
            m = [compare(prepared[i], w) for i, w in zip(TRIAL_ITEMS, wavs)]
            med = float(np.exp(np.mean(np.log(meds))))
            trials.append({"shift": sh, "median_hz": round(med, 1),
                           "per_item_median_hz": dict(zip(TRIAL_ITEMS, [round(x, 1) for x in meds])),
                           "st_from_voice_median": round(st(med, rng["median"]), 2),
                           "in_iqr": rng["p25"] <= med <= rng["p75"],
                           "f0_r": [x["f0_r"] for x in m], "contrast_ratio": [x["contrast_ratio"] for x in m],
                           "per_src": [x["per_src"] for x in m], "dur_ratio": [x["dur_ratio"] for x in m]})
        ok = [t for t in trials if t["in_iqr"]] or trials
        pick = min(ok, key=lambda t: abs(t["st_from_voice_median"]))["shift"] if ok else None
        out["voices"][v] = {"range_hz": rng, "trials": trials, "chosen": pick}
        print(v, rng, flush=True)
        for t in trials:
            print(f"  {t['shift']:+3d} st: median {t['median_hz']:6.1f} Hz ({t['st_from_voice_median']:+.1f} st from "
                  f"voice median), in IQR {t['in_iqr']}, F0 r {t['f0_r']}, contrast {t['contrast_ratio']}, "
                  f"PER {t['per_src']}", flush=True)
        print("  chosen", pick, flush=True)
    save("shift_trials.json", out)


def clip_stats(path) -> dict:
    """Silent / clipped / truncated checks (the bake-off's wav_stats rules, on float audio)."""
    import numpy as np
    a, sr = read_wav(path)
    f = int(0.01 * sr)
    n = len(a) // f
    rms = np.sqrt((a[: n * f].reshape(n, f) ** 2).mean(1)) if n else np.zeros(1)
    active = rms > max(0.02 * rms.max(), 1e-4)
    idx = np.flatnonzero(active)
    speech = (idx[-1] - idx[0] + 1) * 0.01 if idx.size else 0.0
    tail = (n - 1 - idx[-1]) * 0.01 if idx.size else 0.0
    return {"duration_s": round(len(a) / sr, 3), "speech_s": round(float(speech), 3),
            "tail_s": round(float(tail), 3), "amp_peak": round(float(np.abs(a).max()), 3) if a.size else 0.0,
            "clipped": int((np.abs(a) >= 0.999).sum()), "rate": sr}


def flags_for(c, src_stats) -> list[str]:
    """Re-render triggers: silent, clipped, truncated. Seed-VC keeps the source's length by construction, so a
    converted clip is truncated when its file is more than 5 % shorter than the source or its speech runs into
    the last frame; Kokoro, a separate rendering, when its speech is under 0.65x eSpeak's."""
    fl = []
    if c["amp_peak"] < 0.02 or c["speech_s"] < 0.1:
        fl.append("silent")
    if c["clipped"] > 10:
        fl.append(f"clipped ({c['clipped']} samples)")
    if c["tail_s"] < 0.005 and c["family"] != "espeak":
        fl.append("speech runs to the last frame (cut off?)")
    if c["family"] == "vc" and c["duration_s"] / src_stats["duration_s"] < 0.95:
        fl.append(f"truncated: file {c['duration_s'] / src_stats['duration_s']:.2f}x the source")
    r = c["speech_s"] / max(src_stats["speech_s"], 1e-6)
    if c["family"] == "kokoro" and r < 0.65:
        fl.append(f"short: speech {r:.2f}x eSpeak's")
    return fl


def notes_for(c) -> list[str]:
    """Not re-render triggers, shown beside the clip: a word-initial voiceless onset (eSpeak's χ, h, ʔ) that
    lost more than half its noise."""
    if c["family"] == "vc" and c.get("onset_src_ms", 0) >= 80 and c.get("onset_ms", 0) < 0.5 * c["onset_src_ms"]:
        return [f"onset noise {c['onset_ms']} ms of the source's {c['onset_src_ms']} ms"]
    return []


def evaluate(_):
    """tts/vc/evaluate.py's checks on every finals clip, against its eSpeak source; plus QC flags."""
    sys.path.insert(0, str(VC))
    from evaluate import compare, prepare_source, split, summarize
    it = {r["id"]: r for r in load("items.json")["items"]}
    srcs = {s["id"]: s for s in load("audio/espeak.json")}
    chi = {i for i, s in srcs.items() if s["ipa"].startswith("χ")}
    prepared = {}
    rows = []
    rer = load("rerenders.json") or []
    for sy in systems():
        for i in it:
            w = wav_path(sy["id"], i)
            if not w.exists():
                print("MISSING", sy["id"], i, flush=True)
                continue
            if i not in prepared:
                prepared[i] = prepare_source({**srcs[i], "wav": str(ROOT / srcs[i]["wav"])})
                prepared[i]["stats"] = clip_stats(ROOT / srcs[i]["wav"])
            st_ = clip_stats(w)
            r = {"id": i, "kind": it[i]["kind"], "system": sy["id"], "family": sy["family"], "wav": rel(w), **st_}
            if sy["family"] != "espeak":
                r.update(compare(prepared[i], w))
            r["flags"] = flags_for(r, prepared[i]["stats"])
            r["notes"] = notes_for(r)
            rr = [x for x in rer if x["system"] == sy["id"] and x["item"] == i]
            if rr:
                r["rerendered"] = rr[-1]
            rows.append(r)
            print(sy["id"], i, r.get("per_src"), r.get("f0_r"), r.get("dur_ratio"), r["flags"], flush=True)
    summary = {}
    for sy in systems():
        if sy["family"] == "espeak":
            continue
        rr = [r for r in rows if r["system"] == sy["id"]]
        summary[sy["id"]] = {"all": summarize(rr, chi), "hymns": summarize([r for r in rr if r["kind"] == "hymn"], chi),
                             "lines": summarize([r for r in rr if r["kind"] == "line"], chi),
                             "words": summarize([r for r in rr if r["kind"] == "word"], chi)}
    sources = {i: {"rec": " ".join(p["rec"]), "per_ipa": p["per_ipa"], "contrast": p["contrast"],
                   "onset_ms": p["onset"]} for i, p in prepared.items()}
    save("results.json", {"generated": datetime.date.today().isoformat(), "metrics": "tts/vc/evaluate.py",
                          "chi_items": sorted(chi), "summary": summary, "sources": sources, "clips": rows})
    bad = [(r["system"], r["id"], r["flags"]) for r in rows if r["flags"]]
    print(len(rows), "clips;", len(bad), "flagged")
    for b in bad:
        print("  FLAG", *b)


# ---------------------------------------------------------------- page build

def to_mp4(wav: Path, mp4: Path) -> None:
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(wav), str(mp4)], check=True,
                   capture_output=True)


def level(a, sr):
    """Gain that puts the clip's active-speech RMS at TARGET_DBFS, capped so the peak stays under -1 dBFS."""
    import numpy as np
    f = int(0.01 * sr)
    n = len(a) // f
    rms = np.sqrt((a[: n * f].reshape(n, f) ** 2).mean(1))
    act = rms[rms > 0.1 * rms.max()]
    cur = 20 * np.log10(np.sqrt((act ** 2).mean()) + 1e-9)
    g = 10 ** ((TARGET_DBFS - cur) / 20)
    peak = np.abs(a).max() + 1e-9
    return float(min(g, 10 ** (-1 / 20) / peak))


def build(_):
    import numpy as np
    it = load("items.json")
    res = load("results.json")
    trials = load("shift_trials.json")
    srcs = {s["id"]: s for s in load("audio/espeak.json")}
    kok = {(r["voice"], r["id"]): r for r in load("audio/kokoro.json")}
    metrics = {(r["system"], r["id"]): r for r in res["clips"]}
    order = [r for r in it["items"] if r["kind"] == "hymn"] + [r for r in it["items"] if r["kind"] != "hymn"]
    syss = systems()
    chosen = {v: (trials["voices"][v]["chosen"] if trials and v in trials["voices"] else 0) for v in VC_VOICES}
    for sy in syss:
        if sy["family"] == "vc":
            sy["semi_tone_shift"] = chosen[sy["voice"]]
            if chosen[sy["voice"]]:
                sy["label"] += f" ({chosen[sy['voice']]:+d} st)"
    sys.path.insert(0, str(ROOT))
    from pie.ipa import to_ipa
    clips = []
    sprite_dir = AUDIO / "sprites"
    sprite_dir.mkdir(parents=True, exist_ok=True)
    for sy in syss:
        parts, t, rate = [], 0.0, None
        for r in order:
            w = wav_path(sy["id"], r["id"])
            a, sr = read_wav(w)
            rate = rate or sr
            if sr != rate:
                raise SystemExit(f"{w}: rate {sr} != {rate}")
            g = level(a, sr)
            a = np.clip(a * g, -1, 1)
            m = metrics.get((sy["id"], r["id"]), {})
            cid = f"finals__{r['id']}__{sy['id']}"
            c = {"id": cid, "word": r["id"], "variant": "default", "system": sy["id"],
                 "audio": f"{sy['id']}.mp4", "sprite": {"file": f"{sy['id']}.mp4", "start": round(t, 4),
                                                        "duration": round(len(a) / sr, 4)},
                 "gain_db": round(20 * np.log10(g), 2), "rate": sr, "wav": rel(w),
                 "duration_s": m.get("duration_s"), "speech_s": m.get("speech_s"), "peak": m.get("amp_peak"),
                 "clipped": m.get("clipped"), "same_as": None,
                 "qc": {"ok": not m.get("flags"), "flags": m.get("flags", []), "notes": m.get("notes", []),
                        "rerendered": m.get("rerendered")}}
            if sy["family"] == "espeak":
                s = srcs[r["id"]]
                c.update(ipa=s["ipa"], engine_input=s["engine_input"], profile=None, method="espeak-source")
            elif sy["family"] == "kokoro":
                k = kok[(sy["voice"], r["id"])]
                c.update(ipa=k["ipa"], engine_input=k["engine_input"], profile=f"{k['profile']} + dorsals={k['dorsals']}",
                         method="kokoro-profiled", timbre=sy["voice"])
            else:
                s = srcs[r["id"]]
                c.update(ipa=s["ipa"], engine_input=s["engine_input"], profile=None, method="seedvc-f0",
                         timbre=sy["voice"], semi_tone_shift=chosen[sy["voice"]], source_wav=s["wav"],
                         segments=len(s["segments"]))
            if sy["family"] != "espeak":
                c["metrics"] = {k: m.get(k) for k in ("per_src", "per_src_base", "per_ipa", "post_dtw", "f0_r",
                                                      "contrast_ratio", "peak_ok", "onset_src_ms", "onset_ms",
                                                      "dur_ratio", "len_ratio", "rec")}
            clips.append(c)
            gap = np.zeros(int(SPRITE_GAP * sr), dtype="float32")
            parts += [a.astype("float32"), gap]
            t += (len(a) + len(gap)) / sr
        wav = sprite_dir / f"{sy['id']}.wav"
        import soundfile as sf
        sf.write(str(wav), np.concatenate(parts), rate, subtype="PCM_16")
        to_mp4(wav, sprite_dir / f"{sy['id']}.mp4")
        print(sy["id"], f"{t:.1f} s sprite", flush=True)
    words = []
    for r in order:
        w = {"id": r["id"], "pie": r["pie"], "gloss": r["english"], "english": r["english"], "kind": r["kind"],
             "target": r.get("target", "hymn"), "ipa": to_ipa(r["pie"], tone=True), "source": r["source"]}
        if r.get("sound"):
            w["sound"] = r["sound"]
        words.append(w)
    vcm = json.loads((VC / "manifest.json").read_text("utf-8"))
    manifest = {
        "schema": SCHEMA, "source": "finals", "generated": datetime.date.today().isoformat(), "audio_base": "audio/",
        "corpus_head": it["corpus_head"],
        "settings": {
            "espeak": vcm["settings"]["espeak"],
            "kokoro": {**vcm["settings"]["kokoro"], "profile": "per voice (systems[].profile, dorsals)", "seed": 0},
            "seedvc": {"repo": "Plachtaa/seed-vc@51383ef", "mode": "f0", "f0_condition": True, "auto_f0_adjust": False,
                       "diffusion_steps": 30, "inference_cfg_rate": 0.7, "length_adjust": 1.0, "device": "cpu",
                       "reference": "tts/vc/audio/ref/<voice>.wav (Kokoro speech, first 25 s)",
                       "segments": f"sources cut at eSpeak pauses into <= {SEG_MAX} s, converted separately, joined",
                       "semi_tone_shift": chosen},
            "shift_trials": trials,
            "audio": "AAC 48 kb/s in .mp4 (afconvert -f m4af -d aac -b 48000), one sprite per system, clips "
                     f"{SPRITE_GAP} s apart; each clip levelled to {TARGET_DBFS} dBFS speech RMS (gain_db), peak <= -1 dBFS",
            "metrics": "tts/vc/evaluate.py via tts/finals/finals.py eval; tts/finals/results.json"},
        "targets": vcm["targets"] + [{"id": "hymn", "label": "hymn", "note": "whole corpus record", "variants": []}],
        "words": words,
        "systems": syss,
        "summary": res["summary"],
        "clips": clips,
    }
    save("manifest.json", manifest)
    files = {"manifest.json": "tts/finals/manifest.json"}
    files.update({f"audio/{s['id']}.mp4": f"tts/finals/audio/sprites/{s['id']}.mp4" for s in syss})
    save("files.json", files)
    size = sum((ROOT / p).stat().st_size for p in files.values())
    print(len(clips), "clips;", len(files), "files +index.html,", f"{size / 1e6:.1f} MB")


def pick_rerenders(_):
    """Second renders (Seed-VC is a sampler) of first segments whose onset noise was weak: seg-r2/<id>.s00.wav.
    Keep whichever render keeps more of eSpeak's word-initial voiceless noise; the old one is kept as
    seg-r1/. Writes rerenders.json; run join and eval after it."""
    import shutil
    sys.path.insert(0, str(VC))
    from evaluate import onset_unvoiced_ms
    srcs = {x["id"]: x for x in load("audio/espeak.json")}
    out = load("rerenders.json") or []
    for new in sorted(AUDIO.glob("finals-seedvc-f0-*/seg-r2/*.s00.wav")):
        base = new.parent.parent
        item = new.name.split(".")[0]
        old = base / "seg" / new.name
        src = ROOT / srcs[item]["segments"][0]["wav"]
        a, b, s0 = onset_unvoiced_ms(old), onset_unvoiced_ms(new), onset_unvoiced_ms(src)
        keep = "second" if b > a else "first"
        (base / "seg-r1").mkdir(exist_ok=True)
        shutil.copy2(old, base / "seg-r1" / new.name)
        if keep == "second":
            shutil.copy2(new, old)
        new.rename(new.with_suffix(".done.wav"))
        out.append({"system": base.name, "item": item, "segment": 0, "onset_src_ms": s0, "first_ms": a, "second_ms": b,
                    "kept": keep})
        print(base.name, item, s0, a, b, keep, flush=True)
    save("rerenders.json", out)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("items", "espeak", "kokoro", "join", "shifts", "eval", "build", "pick-rerenders"):
        sub.add_parser(name)
    q = sub.add_parser("queue")
    q.add_argument("--voices", required=True)
    q.add_argument("--shift", type=int)
    q.add_argument("--items")
    q.add_argument("--trial", action="store_true", help="write under audio/trials/<voice><shift>/")
    q.add_argument("--priority", default="5", help="job-name prefix; lower runs first")
    q.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    {"items": items, "espeak": espeak, "kokoro": kokoro, "queue": queue, "join": join, "shifts": shifts,
     "eval": evaluate, "build": build, "pick-rerenders": pick_rerenders}[a.cmd](a)


if __name__ == "__main__":
    main()
