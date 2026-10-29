"""Render the hard-word set with pie.speak: eSpeak tone (VC source) or Kokoro pitch-patched (baseline).

    .venv/bin/python -I tts/vc/render_pie.py espeak
    .venv-kokoro/bin/python -I tts/vc/render_pie.py kokoro      # hm_omega, ef_dora, em_alex
Writes tts/vc/audio/src/<id>.espeak-tone.wav or tts/vc/audio/kokoro/<id>.kokoro-pitch-<voice>.wav and
tts/vc/audio/<backend>.json (id, pie, ipa, engine input)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tts" / "vc"))
from pie.ipa import to_ipa  # noqa: E402
from pie.speak import engine_input, speak  # noqa: E402
from words import TIMBRES, WORDS  # noqa: E402

AUDIO = ROOT / "tts" / "vc" / "audio"

backend = sys.argv[1]
rows = []
for wid, pie, target in WORDS:
    ipa = to_ipa(pie, tone=True)
    if backend == "espeak":
        out = AUDIO / "src" / f"{wid}.espeak-tone.wav"
        speak(pie, backend="espeak", out_wav=str(out), tone=True)
        rows.append(dict(id=wid, pie=pie, target=target, ipa=ipa, wav=str(out),
                         engine_input=engine_input(ipa, backend="espeak")))
    else:
        for v in TIMBRES:
            out = AUDIO / "kokoro" / f"{wid}.kokoro-pitch-{v}.wav"
            speak(pie, backend="kokoro", out_wav=str(out), tone=True, voice=v, pitch=True)
            rows.append(dict(id=wid, pie=pie, target=target, ipa=ipa, voice=v, wav=str(out),
                             engine_input=engine_input(ipa, backend="kokoro", voice=v)))
    print(wid, ipa, flush=True)
(AUDIO / f"{backend}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), "utf-8")
