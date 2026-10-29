#!/usr/bin/env python3
"""Render the fixed listening pack to tts/samples/ (wavs gitignored; manifest.json committed).

  UV_PROJECT_ENVIRONMENT=.venv-kokoro UV_CACHE_DIR=/tmp/pie-uv-cache \\
      uv run --python 3.12 --group kokoro --no-default-groups python -I scripts/speech_pack.py
  uv run python -I scripts/speech_pack.py --systems espeak-stress,espeak-tone     # main env: no local Kokoro

Phrases (PHRASES below): the openings of Schleicher's fable and "The King and the God" (Tier 1, Byrd 2013),
three Tier 3 hymn lines and the minimal pairs of docs/research/tts-options.md §2.4. Systems (SYSTEMS): eSpeak
stress and tone, local Kokoro raw and pitch-patched, Kokoro-FastAPI on erebus with Hindi and non-Hindi voices,
and Piper hi_IN-rohan through the researcher's temporary venv when it still exists. A system that is not
available is skipped and listed under "skipped" in the manifest; a failure on one clip is recorded on that clip.

Every clip in manifest.json: phrase id, source record id, PIE, English, converter IPA (tone and stress forms),
system, backend, voice, exact engine input, eSpeak read-back, and the wav path (relative and absolute).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

from pie.batch_release import batch_eligibility
from pie.ipa import to_ipa
from pie import speak as S

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tts" / "samples"

# Tier 1 (Byrd 2013 versions); lines 2-3 of the fable have no English in the record, so the pack gives the
# standard rendering of Byrd's text (english_source "pack").
TIER1 = [
    ("schleicher-1", "corpus/tier1/schleicher-fable.jsonl", "t1-schleicher-fable-byrd-2013-0001", None),
    ("schleicher-2", "corpus/tier1/schleicher-fable.jsonl", "t1-schleicher-fable-byrd-2013-0002",
     "A sheep that had no wool saw horses."),
    ("schleicher-3", "corpus/tier1/schleicher-fable.jsonl", "t1-schleicher-fable-byrd-2013-0003",
     "One was pulling a heavy wagon, one a great load, one was carrying a man quickly."),
    ("king-1", "corpus/tier1/king-and-god.jsonl", "t1-king-and-god-byrd-2013-0001", None),
    ("king-2", "corpus/tier1/king-and-god.jsonl", "t1-king-and-god-byrd-2013-0002", None),
    ("king-3", "corpus/tier1/king-and-god.jsonl", "t1-king-and-god-byrd-2013-0003", None),
]
# Tier 3 hymn lines. As of 2026-10-28 no batch with hymns is currently eligible (all pending re-approval after
# the meter-repair re-realize pass). These three are from b003's last approved release (commit 2febd65,
# review "approved", sha256-bound to the records), and their text is unchanged since; the script checks that
# the current text still matches APPROVED_TEXT and records the batch's current eligibility.
HYMNS = [
    ("hymn-1", "corpus/tier3/b003.jsonl", "t3-b003-00001", "dyḗws ph₂tḗr h₁ésti dʰéǵʰōm méh₂tēr h₁ésti."),
    ("hymn-2", "corpus/tier3/b003.jsonl", "t3-b003-00002", "h₂éwsos diwés dʰúgh₂ter h₂usdʰí. h₁érkʷomes te."),
    ("hymn-3", "corpus/tier3/b003.jsonl", "t3-b003-00004", "déywe lewkós h₁ési ǵn̥néh₃si-kʷe nos."),
]
HYMN_APPROVAL = {"batch": "b003", "approved_release_commit": "2febd65"}
# Minimal pairs (tts-options.md §2.4), as converter-style IPA with the acute; spoken one item at a time.
PAIRS = [
    ("mp-kwe", "kʷé", "labiovelar"), ("mp-ke", "ké", "plain velar"),
    ("mp-bher", "bʱér", "murmured stop"), ("mp-ber", "bér", "plain voiced stop"),
    ("mp-Xowis", "χó.wis", "h2 = χ (default)"), ("mp-howis", "hó.wis", "h = h1 (default)"),
    ("mp-qesti", "ʔés.ti", "h1 = ʔ (pharyngeal preset)"), ("mp-esti", "és.ti", "no laryngeal"),
    ("mp-wlkwos", "wĺ̩.kʷos", "syllabic l"), ("mp-welkwos", "wə́l.kʷos", "schwa + l"),
    ("mp-Hekwos", "ħé.kʷos", "h2 = ħ (pharyngeal preset)"),
]

# system id -> (backend, speak_ipa options)
SYSTEMS = {
    "espeak-stress": ("espeak", {"tone": "stress"}),
    "espeak-tone": ("espeak", {"tone": True}),
    "kokoro-raw-hf_alpha": ("kokoro", {"voice": "hf_alpha", "pitch": False}),
    "kokoro-pitch-hf_alpha": ("kokoro", {"voice": "hf_alpha", "pitch": True}),
    "remote-hf_alpha": ("kokoro-remote", {"voice": "hf_alpha"}),
    "remote-hm_omega": ("kokoro-remote", {"voice": "hm_omega"}),
    "remote-bm_george": ("kokoro-remote", {"voice": "bm_george"}),
    "remote-im_nicola": ("kokoro-remote", {"voice": "im_nicola"}),
    "piper-hi_IN-rohan": ("piper", {}),
}
SCRATCH_TTS = Path("/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/tts")

# Piper runs in its own venv; this program reads [(ipa_in, wav)] as JSON on stdin.
PIPER_PROG = r"""
import json, sys, wave
from piper import PiperVoice
v = PiperVoice.load(sys.argv[1]); idmap = v.config.phoneme_id_map
out = []
for text, wav in json.load(sys.stdin):
    missing = sorted({c for c in text if c not in idmap and c not in " []"})
    with wave.open(wav, "wb") as f:
        v.synthesize_wav("[[ " + text + " ]]", f)
    out.append(missing)
print(json.dumps(out))
"""


def piper_input(ipa_stress: str) -> str:
    """Nearest-neighbour map for Piper (tts-options.md §5): ʱ → ʰ, ʷ → w, ħ → χ, ʕ → ɣ; ̩ is kept."""
    s = unicodedata.normalize("NFD", ipa_stress).replace(".", "").replace("ʷʱ", "ʱʷ")
    for a, b in {"ʱ": "ʰ", "ʷ": "w", "ħ": "χ", "ʕ": "ɣ", "‖": ".", "|": ","}.items():
        s = s.replace(a, b)
    return unicodedata.normalize("NFC", " ".join(s.split()))


def phrases() -> list[dict]:
    out = []
    for pid, path, rid, eng in TIER1:
        r = next(json.loads(l) for l in (ROOT / path).open(encoding="utf-8") if json.loads(l)["id"] == rid)
        out.append(dict(phrase=pid, group="tier1", source_id=rid, pie=r["pie"], english=eng or r["english"],
                        english_source="pack" if eng else "record"))
    for pid, path, rid, approved in HYMNS:
        r = next(json.loads(l) for l in (ROOT / path).open(encoding="utf-8") if json.loads(l)["id"] == rid)
        if r["pie"] != approved:
            raise SystemExit(f"{rid}: text changed since the approved release; re-pick the hymn lines")
        out.append(dict(phrase=pid, group="tier3-hymn", source_id=rid, pie=r["pie"], english=r["english"],
                        english_source="record"))
    for p in out:
        p["ipa"] = to_ipa(p["pie"])
        p["ipa_stress"] = to_ipa(p["pie"], tone="stress")
    for pid, ipa, note in PAIRS:
        ipa = unicodedata.normalize("NFC", ipa)
        out.append(dict(phrase=pid, group="minimal-pair", source_id=None, pie=None, english=None, note=note,
                        ipa=ipa, ipa_stress=S.acute_to_stress(ipa)))
    return out


def available(system: str, piper_venv: Path, piper_voice: Path) -> str | None:
    backend = SYSTEMS[system][0]
    if backend == "espeak":
        return S.espeak_status()
    if backend == "kokoro":
        return S.kokoro_status()
    if backend == "piper":
        if not (piper_venv / "bin" / "python").exists() or not piper_voice.exists():
            return f"Piper venv or voice not found ({piper_venv}, {piper_voice})"
    return None


def render_piper(items: list[dict], piper_venv: Path, piper_voice: Path) -> None:
    jobs = [(piper_input(c["ipa_stress"]), c["path"]) for c in items]
    p = subprocess.run([str(piper_venv / "bin" / "python"), "-I", "-c", PIPER_PROG, str(piper_voice)],
                       input=json.dumps(jobs), capture_output=True, text=True)
    if p.returncode:
        for c in items:
            c["error"] = p.stderr.strip()[-500:]
        return
    for c, (text, _), missing in zip(items, jobs, json.loads(p.stdout.strip().splitlines()[-1])):
        c["engine_input"] = f"[[ {text} ]]"
        if missing:
            c["dropped"] = missing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--systems", default=",".join(SYSTEMS), help="comma-separated subset of: " + ", ".join(SYSTEMS))
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--piper-venv", type=Path, default=SCRATCH_TTS / "piper-venv")
    ap.add_argument("--piper-voice", type=Path, default=SCRATCH_TTS / "voices" / "hi_IN-rohan-medium.onnx")
    a = ap.parse_args(argv)
    systems = a.systems.split(",")
    for s in systems:
        if s not in SYSTEMS:
            ap.error(f"unknown system {s!r}")
    a.out.mkdir(parents=True, exist_ok=True)
    items = phrases()
    clips, skipped = [], {}
    for system in systems:
        why = available(system, a.piper_venv, a.piper_voice)
        if why:
            skipped[system] = why
            print(f"skip {system}: {why}", file=sys.stderr)
            continue
        backend, opts = SYSTEMS[system]
        batch = []
        for p in items:
            name = f"{p['phrase']}.{system}.wav"
            c = dict(p, system=system, backend=backend, voice=opts.get("voice"), wav=name,
                     path=str((a.out / name).resolve()))
            if backend == "piper":
                c["voice"] = "hi_IN-rohan-medium"
                batch.append(c)
            else:
                try:
                    src = p["ipa_stress"] if opts.get("tone") == "stress" else p["ipa"]
                    r = S.speak_ipa(src, backend=backend, out_wav=c["path"], **opts)
                    c.update(voice=r.voice, engine_input=r.engine_input, espeak_read_back=r.round_trip,
                             notes=r.notes or None)
                except S.SpeechError as e:
                    c["error"] = str(e)
            clips.append(c)
        if batch:
            render_piper(batch, a.piper_venv, a.piper_voice)
        for c in clips:
            if c["system"] == system:
                print(f"{system:24} {c['phrase']:14} {'ERROR ' + c['error'][:60] if c.get('error') else 'ok'}")
    hymn_now = batch_eligibility(ROOT, HYMN_APPROVAL["batch"])
    manifest = {
        "generated": dt.date.today().isoformat(),
        "root": str(a.out.resolve()),
        "converter": "pie.ipa.to_ipa, convention default (tone form with acutes; ipa_stress with ˈ)",
        "systems": {s: {"backend": SYSTEMS[s][0], **SYSTEMS[s][1]} for s in systems if s not in skipped},
        "skipped": skipped,
        "hymn_provenance": {**HYMN_APPROVAL, "current_eligible": hymn_now.get("eligible"),
                            "current_reasons": hymn_now.get("reasons")},
        "clips": [{k: v for k, v in c.items() if v is not None} for c in clips],
    }
    (a.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", "utf-8")
    bad = [c for c in clips if c.get("error")]
    print(f"{len(clips) - len(bad)} clips ok, {len(bad)} failed, {len(skipped)} systems skipped -> {a.out}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
