"""Render the hard-word set with pie.speak: eSpeak tone (VC source) or Kokoro pitch-patched (baseline).

    .venv/bin/python -I tts/vc/render_pie.py espeak
    .venv-kokoro/bin/python -I tts/vc/render_pie.py kokoro      # hm_omega, ef_dora, em_alex
    .venv-kokoro/bin/python -I tts/vc/render_pie.py kokoro-prof # top-3 voices, recommended profiles, SUBSET only
    .venv/bin/python -I tts/vc/render_pie.py espeak-p80         # control: same codes, eSpeak pitch 80 (default 50)
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
from pie.ipa import Convention  # noqa: E402
from pie.speak import speak_ipa  # noqa: E402
from words import SUBSET, TIMBRES, TIMBRES2, VOICE_PROFILE, WORDS  # noqa: E402

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
    elif backend == "kokoro-prof":
        if wid not in SUBSET:
            continue
        for v in TIMBRES2:
            prof, dors = VOICE_PROFILE[v]
            vipa = to_ipa(pie, convention=Convention(dors, dorsals=dors), tone=True)
            out = AUDIO / "kokoro-prof" / f"{wid}.kokoro-prof-{v}.wav"
            r = speak_ipa(vipa, backend="kokoro", out_wav=str(out), tone=True, voice=v, pitch=True, profile=prof)
            rows.append(dict(id=wid, pie=pie, target=target, ipa=r.ipa, voice=v, profile=prof, dorsals=dors,
                             wav=str(out), engine_input=engine_input(vipa, backend="kokoro", voice=v, profile=prof)))
    elif backend == "espeak-p80":
        out = AUDIO / "ctrl" / f"{wid}.ctrl-espeak-p80-none.wav"
        speak(pie, backend="espeak", out_wav=str(out), tone=True, espeak_pitch=80)
        rows.append(dict(id=wid, pie=pie, ipa=ipa, wav=str(out)))
    else:
        for v in TIMBRES:
            out = AUDIO / "kokoro" / f"{wid}.kokoro-pitch-{v}.wav"
            speak(pie, backend="kokoro", out_wav=str(out), tone=True, voice=v, pitch=True)
            rows.append(dict(id=wid, pie=pie, target=target, ipa=ipa, voice=v, wav=str(out),
                             engine_input=engine_input(ipa, backend="kokoro", voice=v)))
    print(wid, ipa, flush=True)
(AUDIO / f"{backend}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), "utf-8")
