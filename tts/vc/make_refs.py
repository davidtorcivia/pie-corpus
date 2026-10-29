"""Kokoro target-timbre references (20-30 s of plain speech) for the voice-conversion test.

    .venv-kokoro/bin/python -I tts/vc/make_refs.py
hm_omega reads English (en-us), ef_dora and em_alex read Spanish (es); G2P is misaki.espeak.EspeakG2P, the
same path KPipeline uses for Spanish (misaki en would need a spaCy model download). The texts
pack in sounds a kNN-VC frame pool needs: Spanish [x] (jota), English aspirated p t k, labialised qu-/tw-,
ʃ, θ, ɾ, ŋ and a full vowel range. Pinned Kokoro model and voices through pie.speak (sha256-checked).
Writes tts/vc/audio/ref/<voice>.wav and ref.json."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from misaki.espeak import EspeakG2P  # noqa: E402
from pie.speak import KOKORO_RATE, _kokoro_model, _kokoro_synth, _kokoro_voice, _silence, _write_wav  # noqa: E402

EN = ("The quick brown fox jumps over the lazy dog, while the queen quietly plays a game of chess beside the "
      "water. Twenty thick clouds gathered over the hills, and the children ran home through the cold rain. "
      "Keep the kettle hot, she called; we will want tea, toast and honey before the long journey begins. "
      "Peter took a cup of coffee to the porch and watched the sheep graze in the purple evening light.")
ES = ("El viejo general cruzó la sierra con su caballo rojo. Junto al río, la gente cocinaba jamón, queso y "
      "garbanzos. Cuando llegó la noche, quiso escribir una carta a su hija Ximena, pero la tinta se había "
      "secado. Mañana, dijo, iremos juntos hacia el pueblo, y cada uno traerá algo: pan, vino, ajo, "
      "guitarras y un cuaderno lleno de canciones antiguas.")
REFS = {"hm_omega": ("en-us", EN), "ef_dora": ("es", ES), "em_alex": ("es", ES),
        # fair-comparison round: the bake-off top 3, each in its own language
        "bf_isabella": ("en-gb", EN), "af_nicole": ("en-us", EN), "em_santa": ("es", ES)}
ONLY = [v for v in os.environ.get("VC_VOICES", "").split(",") if v]

out_dir = ROOT / "tts" / "vc" / "audio" / "ref"
out_dir.mkdir(parents=True, exist_ok=True)
model = _kokoro_model()
meta = {}
for voice, (lang, text) in REFS.items():
    if ONLY and voice not in ONLY:
        continue
    g2p = EspeakG2P(language=lang)
    pack = _kokoro_voice(voice)
    parts, phs = [], []
    for sent in [t.strip() + "." for t in text.split(".") if t.strip()]:
        ps = g2p(sent)[0]
        ps = "".join(c for c in ps if c in model.vocab)
        parts += [_kokoro_synth(model, pack[len(ps) - 1], ps, [False] * len(ps), pitch=False, speed=1.0),
                  _silence(0.25)]
        phs.append(ps)
    audio = np.concatenate(parts)
    _write_wav(out_dir / f"{voice}.wav", audio)
    meta[voice] = dict(lang=lang, text=text, phonemes=phs, seconds=round(len(audio) / KOKORO_RATE, 2))
    print(voice, meta[voice]["seconds"], "s", flush=True)
old = json.loads((out_dir / "ref.json").read_text("utf-8")) if (out_dir / "ref.json").exists() else {}
(out_dir / "ref.json").write_text(json.dumps({**old, **meta}, ensure_ascii=False, indent=1), "utf-8")
