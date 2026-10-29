#!/usr/bin/env python3
"""Speak PIE text to a wav (pie.speak; setup and limits: docs/pronunciation.md "Speech").

  uv run python -I scripts/speak.py -o ovis.wav "h₂ówis h₁éḱwōs-kʷe"           # eSpeak, level tones
  uv run python -I scripts/speak.py --tone stress --play "ph₂tḗr"                # eSpeak, stress; afplay
  echo "h2o/wis" | uv run python -I scripts/speak.py --ascii -o ovis.wav          # stdin, pie_ascii
  uv run python -I scripts/speak.py --ipa -o esti.wav "ʔés.ti"                    # IPA in
  uv run python -I scripts/speak.py --profile h1-glottal-stop -o esti.wav "h₁ésti"  # respelled (pie.speak.PROFILES)
  uv run python -I scripts/speak.py --backend kokoro-remote --voice hm_omega -o x.wav "deywós"
  UV_PROJECT_ENVIRONMENT=.venv-kokoro uv run --python 3.12 --group kokoro --no-default-groups \\
      python -I scripts/speak.py --backend kokoro -o x.wav "deywós"                # local Kokoro (Python 3.12)

With no text arguments, reads stdin; each non-empty line is one utterance and lines are joined with a major
pause (‖). Prints the IPA and the exact engine input. Exit status: 0 ok, 1 speech error (including an eSpeak
round-trip mismatch), 2 bad input.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from pie.ipa import CONVENTIONS, to_ipa
from pie.speak import BACKENDS, PROFILES, SpeechError, speak_ipa

TONES = {"tone": True, "stress": "stress", "none": False}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="*", help="PIE text (canonical, or pie_ascii with --ascii, or IPA with --ipa)")
    ap.add_argument("-o", "--out", default="speak.wav", help="output wav (default speak.wav)")
    ap.add_argument("--backend", choices=BACKENDS, default="espeak")
    ap.add_argument("--voice", help="espeak voice (default pie/pie-tone or pie/pie) or Kokoro voice (default hf_alpha)")
    ap.add_argument("--convention", choices=sorted(CONVENTIONS), default="default")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="default",
                    help="respell the IPA before the backend (e.g. h2-velar: h₂ as [x])")
    ap.add_argument("--tone", choices=TONES, default="tone", help="accent as pitch (tone), stress, or none")
    ap.add_argument("--ascii", action="store_true", help="input is pie_ascii")
    ap.add_argument("--ipa", action="store_true", help="input is already converter IPA")
    ap.add_argument("--no-strict", action="store_true", help="eSpeak round-trip mismatch warns instead of failing")
    ap.add_argument("--no-pitch", action="store_true", help="kokoro: no imposed F0 accent (ˈ instead)")
    ap.add_argument("--rate", type=int, default=130, help="espeak words per minute (default 130)")
    ap.add_argument("--speed", type=float, default=0.9, help="kokoro speed (default 0.9)")
    ap.add_argument("--play", action="store_true", help="play the result with afplay (macOS)")
    a = ap.parse_args(argv)

    lines = a.text and [" ".join(a.text)] or [ln.strip() for ln in sys.stdin if ln.strip()]
    if not lines:
        ap.error("no text given")
    tone = TONES[a.tone]
    try:
        ipa = " ‖ ".join(ln if a.ipa else to_ipa(ln, convention=a.convention, tone=tone, ascii=a.ascii)
                         for ln in lines)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.play and not shutil.which("afplay"):
        print("error: --play needs afplay (macOS)", file=sys.stderr)
        return 2
    try:
        r = speak_ipa(ipa, backend=a.backend, out_wav=a.out, tone=tone, voice=a.voice, strict=not a.no_strict,
                      pitch=not a.no_pitch, rate=a.rate, speed=a.speed, profile=a.profile)
    except SpeechError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"ipa:    {r.ipa}\ninput:  {r.engine_input}\nvoice:  {r.backend} {r.voice}\nwav:    {r.out_wav}")
    if r.round_trip is not None:
        print(f"espeak: {r.round_trip}")
    for n in r.notes:
        print(f"note:   {n}")
    if a.play:
        subprocess.run(["afplay", r.out_wav], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
