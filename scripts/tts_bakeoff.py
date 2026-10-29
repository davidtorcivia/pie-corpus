#!/usr/bin/env python3
"""TTS bake-off (docs/research/tts-bakeoff.md): Kokoro voices (pitch patch) × respellings of the hard sounds, with
eSpeak (tone) as the reference. Runs in the Kokoro env:

  UV_PROJECT_ENVIRONMENT=.venv-kokoro uv run --python 3.12 --group kokoro --no-default-groups \\
      python -I scripts/tts_bakeoff.py render              # tts/bakeoff/audio/*.wav|mp4 + tts/bakeoff/manifest.json
  ... python -I scripts/tts_bakeoff.py coverage --texts <unzipped nltk udhr dir>   # coverage table (markdown)
  ... python -I scripts/tts_bakeoff.py qc                  # re-run the automatic checks on rendered clips
  ... python -I scripts/tts_bakeoff.py page-files          # rating-page/files.txt + files-N.json for publishing

Every clip is one word with one target sound respelled one way (a pie.ipa Convention for the dorsals, a
pie.speak Profile for the rest); the word's other sounds use the base spelling (BASE_PROFILE for Kokoro, the
converter default for eSpeak, which has no [x]). A clip whose engine input equals an earlier clip's for the same
system is not rendered again: it is recorded with same_as. eSpeak clips keep the strict round-trip check.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pie import ipa as I  # noqa: E402
from pie import speak as S  # noqa: E402

OUT = ROOT / "tts" / "bakeoff"
AUDIO = OUT / "audio"
SCHEMA = "pie-tts-bakeoff/1"

# Kokoro voices (all pinned in pie.speak.KOKORO_FILES); language = the misaki/espeak-ng G2P its labels came from.
KOKORO_VOICES = {
    "hf_alpha": "hi", "hf_beta": "hi", "hm_omega": "hi", "hm_psi": "hi",
    "ef_dora": "es", "em_alex": "es", "em_santa": "es",
    "pf_dora": "pt-br", "pm_alex": "pt-br", "pm_santa": "pt-br",
    "ff_siwis": "fr-fr", "if_sara": "it", "im_nicola": "it",
    "af_heart": "en-us", "af_nicole": "en-us", "bf_emma": "en-gb", "bf_isabella": "en-gb", "bm_lewis": "en-gb",
    "bm_george": "en-gb",
}
# The owner's χ test: [x] beats [χ] in every Kokoro voice, so it is the base spelling of h₂ outside the h₂ rows.
BASE_PROFILE = S.PROFILES["h2-velar"]

DEFAULT = I.CONVENTIONS["default"]
CONV = {"fronted": I.Convention("fronted", dorsals="fronted"), "plain": I.Convention("plain", dorsals="plain")}


def V(vid, label, doc, *, profile="default", convention=None):
    return {"id": vid, "label": label, "doc": doc, "profile": profile, "convention": convention}


TARGETS = [
    {"id": "h2", "label": "h₂", "note": "converter default [χ], voiceless uvular fricative", "variants": [
        V("chi", "[χ]", "converter default", profile=S.Profile("h2-uvular", (("χ", "χ"),), "h₂ as [χ]")),
        V("x", "[x]", "velar", profile="h2-velar"),
        V("voiced-uvular", "[ʁ]", "voiced uvular", profile="h2-voiced-uvular"),
        V("h", "[h]", "glottal", profile="h2-h")]},
    {"id": "dorsal", "label": "ǵ / ḱ", "note": "palatovelars; [ɟ c] are heard as affricates", "variants": [
        V("palatal", "[ɟ c]", "converter default"),
        V("fronted", "[ɡʲ kʲ]", "fronted velars", convention="fronted"),
        V("plain", "[ɡ k]", "plain velars", convention="plain")]},
    {"id": "murmur", "label": "bʰ dʰ gʷʰ", "note": "breathy-voiced stops", "variants": [
        V("breathy", "[bʱ]", "converter default (Kokoro has no ʱ: sent as ʰ)"),
        V("aspirated", "[bʰ]", "written ʰ", profile="murmur-aspirated"),
        V("plain", "[b]", "plain voiced", profile="murmur-plain")]},
    {"id": "kw", "label": "kʷ", "note": "labiovelar", "variants": [
        V("labialized", "[kʷ]", "converter default (Kokoro has no ʷ: sent as w)"),
        V("cluster", "[kw]", "k + w", profile="labiovelar-cluster")]},
    {"id": "h3", "label": "h₃", "note": "converter default [ɣʷ]", "variants": [
        V("gw-labialized", "[ɣʷ]", "converter default (Kokoro: ɣw)"),
        V("gw-cluster", "[ɣw]", "ɣ + w", profile="h3-unrounded-w"),
        V("rw-cluster", "[ʁw]", "ʁ + w", profile="h3-voiced-uvular-w")]},
    {"id": "syllabic", "label": "l̥ m̥", "note": "syllabic resonants", "variants": [
        V("syllabic", "[l̩ m̩]", "converter default (Kokoro has no ̩: sent as əl)"),
        V("schwa", "[əl əm]", "schwa + resonant", profile="syllabic-schwa")]},
    {"id": "vocalized", "label": "H̥", "note": "vocalized laryngeal [ə]", "variants": [V("default", "as is", "")]},
    {"id": "accent", "label": "accent", "note": "long accented diphthong", "variants": [V("default", "as is", "")]},
    {"id": "h1", "label": "h₁", "note": "converter default [h]", "variants": [
        V("h", "[h]", "converter default"),
        V("glottal-stop", "[ʔ]", "glottal stop", profile="h1-glottal-stop")]},
]
WORDS = [
    ("h2ewsos", "h₂éwsos", "dawn", "h2"), ("h2owis", "h₂ówis", "sheep", "h2"),
    ("h2egjeti", "h₂éǵeti", "drives", "dorsal"), ("gjenh1tor", "ǵénh₁tor", "begetter", "dorsal"),
    ("kjlewos", "ḱléwos", "fame", "dorsal"),
    ("bhreh2ter", "bʰréh₂tēr", "brother", "murmur"), ("dhugh2ter", "dʰugh₂tḗr", "daughter", "murmur"),
    ("gwhenti", "gʷʰénti", "strikes", "murmur"),
    ("kwetwores", "kʷetwóres", "four", "kw"),
    ("h3esth1", "h₃ésth₁", "bone", "h3"),
    ("wlkwos", "wĺ̥kʷos", "wolf", "syllabic"), ("kmtom", "ḱm̥tóm", "hundred", "syllabic"),
    ("ph2ter", "ph₂tḗr", "father", "vocalized"),
    ("dyews", "dyḗws", "sky, day", "accent"),
    ("h1esti", "h₁ésti", "is", "h1"),
]
TARGET = {t["id"]: t for t in TARGETS}


def systems() -> list[dict]:
    out = [{"id": "espeak-tone", "label": "eSpeak (tone)", "family": "espeak", "language": "pie (hi base)",
            "licence": "GPL-3.0 engine; output unrestricted", "reference": True}]
    for v, lang in KOKORO_VOICES.items():
        out.append({"id": f"kokoro-{v}", "label": f"Kokoro {v}", "family": "kokoro", "language": lang,
                    "licence": "Apache-2.0", "reference": False, "voice": v})
    return out


def variant_ipa(pie: str, target: str, var: dict, family: str) -> tuple[str, S.Profile]:
    """(converter IPA, profile) for one word × variant × engine family."""
    conv = CONV[var["convention"]] if var["convention"] else DEFAULT
    ipa = I.to_ipa(pie, convention=conv, tone=True)
    prof = S.get_profile(var["profile"])
    if family == "kokoro" and target != "h2":
        prof = BASE_PROFILE + prof
    return ipa, prof


# ---------------------------------------------------------------- automatic checks

def wav_stats(path: Path) -> dict:
    import numpy as np
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32767
    dur = len(a) / sr
    peak = float(np.abs(a).max()) if a.size else 0.0
    f = int(0.01 * sr)
    rms = np.sqrt((a[: len(a) // f * f].reshape(-1, f) ** 2).mean(1)) if len(a) >= f else np.zeros(1)
    active = rms > max(0.02 * rms.max(), 1e-4)
    idx = np.flatnonzero(active)
    speech = (idx[-1] - idx[0] + 1) * 0.01 if idx.size else 0.0
    return {"duration_s": round(dur, 3), "speech_s": round(float(speech), 3), "peak": round(peak, 3),
            "clipped": int((np.abs(a) > 0.999).sum())}


def phone_count(ipa: str) -> int:
    s = unicodedata.normalize("NFD", ipa)
    return sum(1 for c in s if c.isalpha() and unicodedata.category(c) != "Lm")


def qc(clips: list[dict]) -> None:
    """Flags: silent, clipped, too short per phone, and duration far from the median of the same word × variant
    across Kokoro voices (a dropped or doubled segment)."""
    import statistics
    groups: dict = {}
    for c in clips:
        if c["audio"] and c["system"].startswith("kokoro-"):
            groups.setdefault((c["word"], c["variant"]), []).append(c["speech_s"])
    for c in clips:
        if not c["audio"]:
            continue
        flags = []
        if c["peak"] < 0.02 or c["speech_s"] < 0.1:
            flags.append("silent")
        if c["clipped"] > 10:
            flags.append(f"clipped ({c['clipped']} samples)")
        n = phone_count(c["ipa"])
        if c["speech_s"] / max(n, 1) < 0.045:
            flags.append(f"short: {c['speech_s']:.2f}s for {n} phones")
        g = groups.get((c["word"], c["variant"]))
        if c["system"].startswith("kokoro-") and g and len(g) >= 5:
            med = statistics.median(g)
            r = c["speech_s"] / med
            if r < 0.65 or r > 1.6:
                flags.append(f"duration {r:.2f}× the voices' median ({med:.2f}s)")
        c["qc"] = {"ok": not flags, "flags": flags}


# ---------------------------------------------------------------- render

def to_mp4(wav: Path, mp4: Path) -> None:
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(wav), str(mp4)], check=True,
                   capture_output=True)


def render(args) -> None:
    import torch
    if shutil.which("afconvert") is None:
        sys.exit("afconvert (macOS) is needed for the .mp4 files")
    AUDIO.mkdir(parents=True, exist_ok=True)
    syss = systems()
    if args.voices:
        keep = set(args.voices.split(","))
        syss = [s for s in syss if s["family"] == "espeak" or s["voice"] in keep]
    clips, seen = [], {}
    for wid, pie, gloss, tid in WORDS:
        for var in TARGET[tid]["variants"]:
            for sy in syss:
                fam = sy["family"]
                ipa, prof = variant_ipa(pie, tid, var, fam)
                cid = f"{wid}__{var['id']}__{sy['id']}"
                rec = {"id": cid, "word": wid, "variant": var["id"], "system": sy["id"], "audio": None,
                       "ipa": None, "engine_input": None, "profile": prof.name, "same_as": None, "qc": None}
                backend = "espeak" if fam == "espeak" else "kokoro"
                try:
                    inp = S.engine_input(ipa, backend=backend, tone=True, profile=prof)
                except S.UnsupportedPhone as e:
                    rec["unsupported"] = str(e).split("\n")[0]
                    clips.append(rec)
                    continue
                rec["ipa"], rec["engine_input"] = prof.apply(ipa), inp
                key = (sy["id"], inp)
                if key in seen:
                    rec["same_as"] = seen[key]
                    clips.append(rec)
                    continue
                seen[key] = cid
                wav, mp4 = AUDIO / f"{cid}.wav", AUDIO / f"{cid}.mp4"
                if not (args.resume and wav.exists() and mp4.exists()):
                    torch.manual_seed(0)
                    if fam == "espeak":
                        r = S.speak_ipa(ipa, backend="espeak", out_wav=str(wav), tone=True, strict=True, profile=prof)
                        rec["round_trip"] = r.round_trip
                    else:
                        r = S.speak_ipa(ipa, backend="kokoro", out_wav=str(wav), tone=True, pitch=True, speed=0.9,
                                        voice=sy["voice"], profile=prof)
                    planned = unicodedata.normalize("NFD", inp)
                    if fam == "kokoro":                # engine_input marks the pitch-raised phonemes with an acute
                        planned = planned.replace(I.HIGH, "")
                    if unicodedata.normalize("NFD", r.engine_input) != planned:
                        raise SystemExit(f"{cid}: rendered input {r.engine_input!r} != planned {inp!r}")
                    to_mp4(wav, mp4)
                elif fam == "espeak":
                    rec["round_trip"] = S.espeak_read_back(inp.strip("[]"), S.VOICE_TONE)
                rec["audio"] = mp4.name
                rec.update(wav_stats(wav))
                clips.append(rec)
                print(cid, rec["engine_input"], rec["speech_s"], flush=True)
    qc(clips)
    manifest = {
        "schema": SCHEMA, "source": "kokoro", "generated": datetime.date.today().isoformat(), "audio_base": "audio/",
        "settings": {"kokoro": {"model": f"{S.KOKORO_REPO}@{S.KOKORO_REVISION}", "pitch_patch": True, "speed": 0.9,
                                "base_profile": BASE_PROFILE.name, "seed": 0},
                     "espeak": {"voice": S.VOICE_TONE, "version": S.ESPEAK_VERSION, "rate": 130,
                                "round_trip": "strict"},
                     "audio": "AAC 48 kb/s in .mp4 (afconvert -f m4af -d aac -b 48000)"},
        "targets": [{**{k: t[k] for k in ("id", "label", "note")},
                     "variants": [{k: v[k] for k in ("id", "label", "doc")} for v in t["variants"]]} for t in TARGETS],
        "words": [{"id": w, "pie": p, "gloss": g, "target": t, "ipa": I.to_ipa(p)} for w, p, g, t in WORDS],
        "systems": syss,
        "clips": clips,
    }
    build_sprites(manifest)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", "utf-8")
    summarize(manifest)


def summarize(m: dict) -> None:
    from collections import Counter
    rendered = Counter(c["system"] for c in m["clips"] if c["audio"])
    alias = Counter(c["system"] for c in m["clips"] if c["same_as"])
    unsup = Counter(c["system"] for c in m["clips"] if c.get("unsupported"))
    bad = [(c["id"], c["qc"]["flags"]) for c in m["clips"] if c.get("qc") and not c["qc"]["ok"]]
    for s in m["systems"]:
        print(f"{s['id']:24} rendered {rendered[s['id']]:3}  same_as {alias[s['id']]:3}  unsupported {unsup[s['id']]:3}")
    print(f"{sum(rendered.values())} audio clips; {len(bad)} flagged")
    for cid, f in bad:
        print("  FLAG", cid, "; ".join(f))


def rerun_qc(args) -> None:
    p = OUT / "manifest.json"
    m = json.loads(p.read_text("utf-8"))
    for c in m["clips"]:
        if c["audio"]:
            c.update(wav_stats(AUDIO / c["audio"].replace(".mp4", ".wav")))
    qc(m["clips"])
    p.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", "utf-8")
    summarize(m)


# ---------------------------------------------------------------- coverage

SYMBOLS = "χ x ʁ h ʔ ħ ɣ c ɟ kʲ ɡʲ k ɡ bʱ dʱ ɡʱ ɟʱ kʷ ɡʷ r̩ l̩ m̩ n̩ ə ː".split()
# Sample text per training language: the NLTK copy of the UDHR (udhr.zip from nltk_data, ~1,500 words each).
UDHR_FILE = {"hi": ("Hindi-UTF8", "utf-8"), "es": ("Spanish-Latin1", "latin-1"),
             "pt-br": ("Portuguese_Portugues-Latin1", "latin-1"), "fr-fr": ("French_Francais-Latin1", "latin-1"),
             "it": ("Italian-Latin1", "latin-1")}


def language_labels(lang: str, texts: Path) -> str:
    """Phoneme labels the way Kokoro's training data got them: misaki's EspeakG2P (espeak-ng + misaki's
    mapping) over the language's UDHR text, or, for English, misaki's own gold and silver lexicons."""
    if lang.startswith("en"):
        import misaki
        d = Path(misaki.__file__).parent / "data"
        pre = "us" if lang == "en-us" else "gb"
        out = []
        for f in (f"{pre}_gold.json", f"{pre}_silver.json"):
            for v in json.loads((d / f).read_text("utf-8")).values():
                out += list(v.values()) if isinstance(v, dict) else [v]
        return unicodedata.normalize("NFD", " ".join(x for x in out if isinstance(x, str)))
    from misaki.espeak import EspeakG2P
    name, enc = UDHR_FILE[lang]
    lines = [ln.strip() for ln in (texts / name).read_text(enc, errors="replace").splitlines() if ln.strip()]
    g2p = EspeakG2P(language=lang)
    return unicodedata.normalize("NFD", " ".join(g2p(ln)[0] or "" for ln in lines))


def coverage(args) -> None:
    """Markdown coverage table: what the Kokoro front end sends for each symbol, whether that is in the vocab, and
    how often the sent form occurs in each training language's labels; and what eSpeak's pie table can say."""
    vocab = S.KOKORO_VOCAB
    langs = sorted(set(KOKORO_VOICES.values()))
    labels = {lang: language_labels(lang, Path(args.texts)) for lang in langs}
    rows = []
    for sym in SYMBOLS:
        probe = f"a{sym}a" if sym != "ː" else "aː"
        try:
            sent = S.engine_input(probe, backend="kokoro", tone=False)
            sent = unicodedata.normalize("NFD", sent)
            sent_sym = sent[1:-1] if sym != "ː" else "ː"
            ok = "native" if sent_sym == unicodedata.normalize("NFD", sym) else f"sent as {unicodedata.normalize('NFC', sent_sym)}"
        except S.UnsupportedPhone:
            sent_sym, ok = None, "no"
        try:
            S.espeak_codes(probe if sym not in ("r̩", "l̩", "m̩", "n̩") else f"t{sym}", tone=True)
            esp = "yes"
            if sym in S.ESPEAK_MAP["phone_substitutions"]:
                esp = f"as {S.ESPEAK_MAP['phone_substitutions'][sym]}"
        except S.UnsupportedPhone:
            esp = "no"
        counts = [str(labels[lang].count(sent_sym)) if sent_sym else "–" for lang in langs]
        rows.append([sym, ok, esp, *counts])
    head = ["symbol", "Kokoro input", "eSpeak pie", *[f"{lang} labels" for lang in langs]]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    sizes = {lang: len(labels[lang].split()) for lang in langs}
    print("\n".join(lines))
    print("\nlabel words per language:", sizes)


SPRITE_GAP = 0.5             # seconds of silence between clips in a sprite


def build_sprites(m: dict) -> None:
    """One AAC sprite per system (audio/<system>.mp4): its rendered clips back to back, SPRITE_GAP apart, so the page
    publishes 20 audio files instead of one per clip (an artifact version holds at most 511 files). Each clip gets
    "sprite": {"file", "start", "duration"} in seconds; "audio" keeps the per-clip file name for local use."""
    import numpy as np
    for sy in m["systems"]:
        clips = [c for c in m["clips"] if c["system"] == sy["id"] and c["audio"]]
        parts, t, rate = [], 0.0, None
        for c in clips:
            with wave.open(str(AUDIO / c["audio"].replace(".mp4", ".wav"))) as w:
                rate = rate or w.getframerate()
                if w.getframerate() != rate:
                    raise SystemExit(f"{c['id']}: sample rate {w.getframerate()} != {rate}")
                a = np.frombuffer(w.readframes(w.getnframes()), "<i2")
            gap = np.zeros(int(SPRITE_GAP * rate), dtype="<i2")
            c["sprite"] = {"file": f"{sy['id']}.mp4", "start": round(t, 4), "duration": round(len(a) / rate, 4)}
            parts += [a, gap]
            t += (len(a) + len(gap)) / rate
        if not clips:
            continue
        wav = AUDIO / "sprites" / f"{sy['id']}.wav"
        wav.parent.mkdir(exist_ok=True)
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(rate)
            w.writeframes(np.concatenate(parts).tobytes())
        to_mp4(wav, wav.with_suffix(".mp4"))


def sprites(args) -> None:
    p = OUT / "manifest.json"
    m = json.loads(p.read_text("utf-8"))
    build_sprites(m)
    p.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{sum(1 for c in m['clips'] if c.get('sprite'))} clips in {len(list((AUDIO / 'sprites').glob('*.mp4')))} sprites")


PAGE = OUT / "rating-page"
PUBLISH_BATCH = 250          # files per Artifact publish (the tool takes at most 255)


def page_files(args) -> None:
    """Write rating-page/files.txt (published path <- source path, one per line) and files-N.json (Artifact `files`
    maps in batches): the page, manifests/kokoro.json, one audio sprite per system under audio/, and, when present,
    tts/vc/manifest.json as manifests/vc.json with its audio (sprites, or single clips) under its own audio_base."""
    m = json.loads((OUT / "manifest.json").read_text("utf-8"))
    pairs = [("manifests/kokoro.json", "tts/bakeoff/manifest.json")]
    pairs += [(m["audio_base"] + f, f"tts/bakeoff/audio/sprites/{f}")
              for f in sorted({c["sprite"]["file"] for c in m["clips"] if c.get("sprite")})]
    vc = ROOT / "tts" / "vc" / "manifest.json"
    if vc.exists():
        v = json.loads(vc.read_text("utf-8"))
        pairs.append(("manifests/vc.json", "tts/vc/manifest.json"))
        src_dir = v.get("audio_dir", "tts/vc/audio")
        files = {c["sprite"]["file"] if c.get("sprite") else c["audio"] for c in v["clips"] if c.get("audio")}
        pairs += [(v["audio_base"] + f, f"{src_dir}/{f}") for f in sorted(files)]
    missing = [src for _, src in pairs if not (ROOT / src).exists()]
    if missing:
        sys.exit(f"{len(missing)} source files missing, e.g. {missing[:3]}")
    total = sum((ROOT / src).stat().st_size for _, src in pairs) + (PAGE / "index.html").stat().st_size
    for old in PAGE.glob("files-*.json"):
        old.unlink()
    (PAGE / "files.txt").write_text("index.html <- tts/bakeoff/rating-page/index.html\n" +
                                    "".join(f"{a} <- {b}\n" for a, b in pairs), "utf-8")
    for i in range(0, len(pairs), PUBLISH_BATCH):
        part = dict(pairs[i:i + PUBLISH_BATCH])
        (PAGE / f"files-{i // PUBLISH_BATCH + 1}.json").write_text(json.dumps(part, indent=1) + "\n", "utf-8")
    if len(pairs) + 1 > 511:
        sys.exit(f"{len(pairs) + 1} files: over the 511 files an artifact version may hold")
    print(f"{len(pairs)} files + index.html, {total / 1e6:.1f} MB, {-(-len(pairs) // PUBLISH_BATCH)} publish batches")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("--voices", help="comma-separated Kokoro voices (default all)")
    r.add_argument("--resume", action="store_true", help="keep clips already rendered")
    sub.add_parser("qc")
    sub.add_parser("page-files")
    sub.add_parser("sprites")
    c = sub.add_parser("coverage")
    c.add_argument("--texts", required=True, help="directory with the NLTK udhr files named in UDHR_FILE")
    a = ap.parse_args(argv)
    {"render": render, "qc": rerun_qc, "coverage": coverage, "page-files": page_files, "sprites": sprites}[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
