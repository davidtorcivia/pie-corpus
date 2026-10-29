"""Kokoro Hindi-encoding probe: the hard words + the first finals hymn, written in the encoding Kokoro's
Hindi voices were trained on (espeak-hi via misaki: भ ध घ झ → bʰ dʰ ɡʰ ɟʰ, च ज → c ɟ, ख़ → x, ग़ → ɣ),
fed straight to KModel (pie.speak's kokoro backend, pitch patch on) with hm_omega and hf_alpha.

    HF_HUB_OFFLINE=1 .venv-kokoro/bin/python -I tts/hindi/probe.py
"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pie.ipa import Convention, to_ipa
from pie.speak import get_profile, speak_ipa

OUT = ROOT / "tts/hindi/audio"
VOICES = ["hm_omega", "hf_alpha"]
# h₂ → x (ख़), h₃ → ɣ + w (ग़ + व); murmur → ʰ is pie.speak's own KOKORO_SUBST
PROFILE = get_profile("h2-velar") + get_profile("h3-unrounded-w")
VARIANTS = {"palatal": "ḱ ǵ as c ɟ (Hindi च ज)", "plain": "ḱ ǵ as k ɡ"}

m = json.load(open(ROOT / "tts/finals/manifest.json"))
items = [w for w in m["words"] if w["kind"] == "word"] + [m["words"][0]]
espeak = {c["word"]: c for c in m["clips"] if c["system"] == "finals-espeak-tone"}
OUT.mkdir(parents=True, exist_ok=True)
rows = []
for w in items:
    ref = OUT / f"{w['id']}__espeak.wav"
    shutil.copy(ROOT / espeak[w["id"]]["wav"], ref)
    clips = [{"system": "espeak", "file": ref.name, "input": w["ipa"]}]
    for var in VARIANTS:
        ipa = PROFILE.apply(to_ipa(w["pie"], convention=Convention(dorsals=var)))
        for v in VOICES:
            f = OUT / f"{w['id']}__{v}__{var}.wav"
            r = speak_ipa(ipa, backend="kokoro", out_wav=str(f), voice=v, pitch=True)
            clips.append({"system": f"{v}/{var}", "file": f.name, "input": r.engine_input})
            print(w["id"], v, var, r.engine_input, flush=True)
    rows.append({"id": w["id"], "pie": w["pie"], "ipa": w["ipa"], "english": w.get("english"), "clips": clips})
for f in OUT.glob("*.wav"):
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "64000", str(f), str(f.with_suffix(".mp4"))], check=True)
json.dump({"voices": VOICES, "variants": VARIANTS, "profile": "h2-velar + h3-unrounded-w", "items": rows},
          open(ROOT / "tts/hindi/manifest.json", "w"), ensure_ascii=False, indent=1)
