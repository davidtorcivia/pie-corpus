"""Speak PIE: canonical text → IPA (pie.ipa.to_ipa) → audio. Setup, usage and limits: docs/pronunciation.md "Speech".

    speak("h₂ówis h₁éḱwōs-kʷe", backend="espeak", out_wav="ovis.wav")              # eSpeak-NG, level tones
    speak("h₂ówis h₁éḱwōs-kʷe", backend="kokoro", out_wav="ovis.wav")              # Kokoro-82M, imposed F0 accent
    speak("h₂ówis h₁éḱwōs-kʷe", backend="kokoro-remote", out_wav="ovis.wav")       # Kokoro-FastAPI server
    speak("h₂ówis h₁éḱwōs-kʷe", backend="kokoro-erebus", out_wav="ovis.wav")       # pie-tts service (F0 accent)
    speak_ipa("ʔés.ti", backend="espeak", out_wav="esti.wav")                        # IPA in (minimal pairs)

Backends:
- "espeak": eSpeak-NG 1.52.0 with the custom pie table (tts/espeak/, compiled by tts/espeak/build.sh into a
  private data dir). Robotic but segmentally right. tone=True uses voice pie/pie-tone, a high level tone on the
  accented syllable and a low one elsewhere; tone="stress" or False uses pie/pie with ' stress marks.
  eSpeak silently truncates a word at an unknown phoneme code, so every rendering is round-tripped through
  `espeak-ng --ipa` and compared with the converter's IPA: a mismatch raises RoundTripError (strict=True) or
  warns loudly (strict=False).
- "kokoro": Kokoro-82M v1.0, local PyTorch (the `kokoro` dependency group; Python < 3.13, so a separate env).
  Converter IPA goes through KOKORO_SUBST (Kokoro has no ʱ ʷ ̩ ħ ʕ ɢ ɵ); with tone=True and pitch=True the
  predicted F0 is flattened and raised on the accented vowel (docs/research/tts-options.md §4.2). pitch=False
  sends ˈ before the accented syllable instead ("raw").
- "kokoro-remote": the same substituted input to a Kokoro-FastAPI server's /dev/generate_from_phonemes. No F0
  access, so the accent is sent as ˈ. Transport: PIE_KOKORO_URL (e.g. http://localhost:8880 through
  `ssh -N -L 8880:localhost:8880 erebus`) if set, else `ssh $PIE_KOKORO_SSH curl ...` (default host erebus).
- "kokoro-erebus": the "kokoro" backend itself (pitch patch included) run as the pie-tts service on erebus
  (tts/erebus/, docs/pronunciation.md "Deployment on erebus"). The converter IPA is posted to its /speak_ipa;
  PIE_KOKORO_PITCH_URL, default http://localhost:8881 through `ssh -N -L 8881:localhost:8881 erebus`.

Every phone a Kokoro backend receives is checked against Kokoro's vocab (tts/kokoro/vocab.json); KModel would
otherwise drop unknown symbols silently.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
import warnings
import wave
from dataclasses import dataclass, field
from pathlib import Path

from .ipa import HIGH, LONG, STRESS, SYLLABIC, to_ipa

ROOT = Path(__file__).resolve().parent.parent
ESPEAK_DIR = ROOT / "tts" / "espeak"
ESPEAK_DATA = Path(os.environ.get("PIE_ESPEAK_DATA", ESPEAK_DIR / "build" / "data"))
ESPEAK_VERSION = "1.52.0"
VOICE_STRESS, VOICE_TONE = "pie/pie", "pie/pie-tone"
ESPEAK_MAP = json.loads((ESPEAK_DIR / "mapping.json").read_text("utf-8"))
HIGH_TONE, LOW_TONE = "5", "1"           # tone phonemes defined in tts/espeak/ph_pie

BACKENDS = ("espeak", "kokoro", "kokoro-remote", "kokoro-erebus")
BREAKS = ("‖", "|")

# Kokoro-82M v1.0, pinned (docs/pronunciation.md "Speech" lists URLs and checksums).
KOKORO_REPO = "hexgrad/Kokoro-82M"
KOKORO_REVISION = "f3ff3571791e39611d31c381e3a41a3af07b4987"
KOKORO_FILES = {
    "config.json": "5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f",
    "kokoro-v1_0.pth": "496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4",
    "voices/hf_alpha.pt": "06906fe05746d13a79c5c01e21fd7233b05027221a933c9ada650f5aafc8f044",
    "voices/hf_beta.pt": "63c0a1a6272e98d43f4511bba40e30dd9c8ceaf5f39af869509b9f51a71c503e",
    "voices/hm_omega.pt": "b55f02a8e8483fffe0afa566e7d22ed8013acf47ad4f6bbee2795a840155703e",
    "voices/hm_psi.pt": "2f0f055cea4f1083f4ef127ece48d71606347f6557dbb961c0ca5740a2da485b",
}
KOKORO_CACHE = Path(os.environ.get("PIE_KOKORO_CACHE", ROOT / "tts" / "cache" / "hf"))
KOKORO_VOCAB = json.loads((ROOT / "tts" / "kokoro" / "vocab.json").read_text("utf-8"))["vocab"]
KOKORO_RATE = 24000
KOKORO_MAX_TOKENS = 510
KOKORO_ENV_HINT = ("UV_PROJECT_ENVIRONMENT=.venv-kokoro uv run --python 3.12 --group kokoro --no-default-groups "
                   "python -I scripts/speak.py ...")
# Converter IPA symbol → nearest symbol in Kokoro's vocab. The syllabic mark is handled separately
# (C̩ → əC, the accent moving to ə), and so are the breaks (‖ ends a chunk, | → ",").
KOKORO_SUBST = {"ʱ": "ʰ", "ʷ": "w", "ħ": "χ", "ʕ": "ɣ", "ɢ": "ɡ", "ɵ": "o"}
REMOTE_PATH = "/dev/generate_from_phonemes"


class SpeechError(RuntimeError):
    """A backend is missing or failed."""


class UnsupportedPhone(SpeechError, ValueError):
    """The converter's IPA contains a phone the backend cannot say."""


class RoundTripError(SpeechError):
    """eSpeak's own IPA for what it was sent differs from the converter's IPA (e.g. a truncated word)."""


@dataclass
class SpeechResult:
    backend: str
    voice: str
    ipa: str                     # the converter IPA that was rendered
    engine_input: str            # exactly what the engine received
    out_wav: str
    round_trip: str | None = None          # espeak only: what espeak-ng --ipa read back
    notes: list[str] = field(default_factory=list)


def _nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _phones(ipa: str) -> str:
    """NFD with the whole-phone substitutions applied and ʷʱ reordered to ʱʷ (murmur on the stop, then w)."""
    s = _nfd(ipa)
    for a, b in ESPEAK_MAP["phone_substitutions"].items():
        s = s.replace(_nfd(a), _nfd(b))
    return s.replace("ʷʱ", "ʱʷ")


def acute_to_stress(ipa: str) -> str:
    """Converter IPA with high-tone acutes → the same with ˈ before each accented syllable (dots kept)."""
    out = []
    for tok in ipa.split(" "):
        sylls = []
        for syl in tok.split("."):
            if HIGH in _nfd(syl):
                syl = STRESS + _nfc(_nfd(syl).replace(HIGH, ""))
            sylls.append(syl)
        out.append(".".join(sylls))
    return " ".join(out)


# ---------------------------------------------------------------- eSpeak-NG

def _espeak_chunk(s: str) -> str:
    """Map an NFD phone string (no dots, no acutes) to mnemonics."""
    cp, syl, uns = ESPEAK_MAP["codepoints"], ESPEAK_MAP["syllabic"], ESPEAK_MAP["unsupported"]
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch in syl and i + 1 < len(s) and s[i + 1] == SYLLABIC:
            out.append(syl[ch])
            i += 2
            continue
        if ch == SYLLABIC or ch not in cp:
            reason = uns.get(ch, "not in tts/espeak/mapping.json")
            raise UnsupportedPhone(f"eSpeak cannot say {ch!r} (U+{ord(ch):04X}) in {_nfc(s)!r}: {reason}")
        out.append(cp[ch])
        i += 1
    return "".join(out)


def _has_nucleus(syl: str) -> bool:
    return any(c in "aeiouəɐɵ" or c == SYLLABIC for c in syl)


def espeak_codes(ipa: str, *, tone: bool = True) -> str:
    """eSpeak [[...]] mnemonics for converter IPA. tone=True: every syllable gets a tone phoneme, 5 (high) on
    the one with the acute and 1 (low) elsewhere, for voice pie/pie-tone. tone=False: acutes are dropped and
    ˈ becomes ', for voice pie/pie."""
    words = []
    for tok in _phones(ipa).split(" "):
        if not tok:
            continue
        if tok in BREAKS:
            words.append(ESPEAK_MAP["codepoints"][tok])
            continue
        if not tone:
            words.append(_espeak_chunk(tok.replace(".", "").replace(HIGH, "")))
            continue
        parts = []
        for syl in tok.split("."):
            mark = HIGH_TONE if HIGH in syl else LOW_TONE
            syl = syl.replace(HIGH, "").replace(STRESS, "")
            parts.append(_espeak_chunk(syl) + (mark if _has_nucleus(syl) else ""))
        words.append("".join(parts))
    return " ".join(words)


_SYLLABIC_RUN = re.compile(r"((?:[rlmn]̩)|ɐ|ɵ)\1+")


def expected_espeak_ipa(ipa: str) -> str:
    """The converter IPA as espeak-ng --ipa should read it back: no dots, accents or stress; murmur written ʰ;
    labiovelars as C+w (eSpeak has no ʷ); breaks as word spaces; length on a syllabic resonant dropped
    (eSpeak writes r̩ː as r̩r̩)."""
    s = _phones(ipa)
    for a in (".", HIGH, STRESS):
        s = s.replace(a, "")
    s = s.replace("ʱ", "ʰ").replace("ʷ", "w")
    s = re.sub(r"([rlmn]̩)ː", r"\1", s)
    for b in BREAKS:
        s = s.replace(b, " ")
    return _nfc(" ".join(s.split()))


def normalize_espeak_ipa(out: str) -> str:
    """espeak-ng --ipa output, comparable with expected_espeak_ipa: stress marks and tone digits removed, a tap
    read as r, and the doubled syllabic/colored vowels eSpeak prints for a tone-bearing or long one collapsed."""
    s = _nfd(out)
    s = re.sub(r"[ˈˌ0-9]", "", s).replace("ɾ", "r")
    s = _SYLLABIC_RUN.sub(r"\1", s)
    return _nfc(" ".join(s.split()))


def espeak_status() -> str | None:
    """None when the espeak backend is usable, else the reason it is not."""
    exe = shutil.which("espeak-ng")
    if not exe:
        return "espeak-ng not installed (brew install espeak-ng)"
    if not (ESPEAK_DATA / "espeak-ng-data" / "phontab").exists() or \
            not (ESPEAK_DATA / "espeak-ng-data" / "voices" / "pie" / "pie-tone").exists():
        return f"PIE eSpeak voice not built in {ESPEAK_DATA} (run: sh tts/espeak/build.sh)"
    return None


def _espeak(args: list[str]) -> str:
    why = espeak_status()
    if why:
        raise SpeechError(why)
    env = dict(os.environ, ESPEAK_DATA_PATH=str(ESPEAK_DATA))
    p = subprocess.run(["espeak-ng", *args], capture_output=True, text=True, env=env)
    if p.returncode:
        raise SpeechError(f"espeak-ng failed ({p.returncode}): {p.stderr.strip()}")
    return p.stdout


ESPEAK_PIECE = 400     # characters per [[...]] call: beyond ~750, eSpeak cuts the input mid-word into a new
                       # clause and reads the rest as ordinary (English) text


def espeak_pieces(codes: str, limit: int = ESPEAK_PIECE) -> list[str]:
    """Split mnemonics at word boundaries into pieces short enough for one [[...]] call."""
    pieces, cur = [], []
    for w in codes.split(" "):
        if len(w) > limit:
            raise SpeechError(f"one word of {len(w)} phoneme codes exceeds the {limit}-character eSpeak piece")
        if cur and len(" ".join(cur + [w])) > limit:
            pieces.append(" ".join(cur))
            cur = []
        cur.append(w)
    if cur:
        pieces.append(" ".join(cur))
    return pieces


def espeak_read_back(codes: str, voice: str) -> str:
    """What espeak-ng --ipa says it will pronounce for [[codes]] under voice (piece by piece)."""
    return " ".join(_espeak(["-v", voice, "-q", "--ipa", f"[[{p}]]"]).strip() for p in espeak_pieces(codes))


def check_round_trip(ipa: str, codes: str, voice: str, *, strict: bool = True) -> str:
    """Compare espeak-ng --ipa for codes against the converter IPA. Returns the read-back. On a mismatch, raise
    RoundTripError (strict) or warn on stderr and through warnings (not strict)."""
    back = espeak_read_back(codes, voice)
    want, got = expected_espeak_ipa(ipa), normalize_espeak_ipa(back)
    if want != got:
        ww, gw = want.split(" "), got.split(" ")
        diff = next((f"word {i + 1}: expected {a!r}, eSpeak read {b!r}"
                     for i, (a, b) in enumerate(zip(ww, gw)) if a != b),
                    f"{len(ww)} words expected, eSpeak read {len(gw)}")
        msg = (f"eSpeak round trip mismatch ({diff}).\n  converter IPA: {ipa}\n  sent: [[{codes}]]\n"
               f"  espeak --ipa:  {back}\n  expected (normalized): {want}\n  got (normalized):      {got}")
        if strict:
            raise RoundTripError(msg)
        print("WARNING: " + msg, file=sys.stderr)
        warnings.warn(msg, stacklevel=2)
    return back


def _speak_espeak(ipa: str, out_wav: str, *, tone: bool, strict: bool, rate: int, pitch: int | None,
                  voice: str | None) -> SpeechResult:
    voice = voice or (VOICE_TONE if tone else VOICE_STRESS)
    codes = espeak_codes(ipa, tone=tone)
    back = check_round_trip(ipa, codes, voice, strict=strict)
    args = ["-v", voice, "-s", str(rate)]
    if pitch is not None:
        args += ["-p", str(pitch)]
    params, frames = None, []
    for i, piece in enumerate(espeak_pieces(codes)):
        tmp = f"{out_wav}.part{i}.wav"
        try:
            _espeak(args + ["-w", tmp, f"[[{piece}]]"])
            with wave.open(tmp) as w:
                params = params or w.getparams()
                frames.append(w.readframes(w.getnframes()))
        finally:
            Path(tmp).unlink(missing_ok=True)
    with wave.open(str(out_wav), "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(frames))
    return SpeechResult("espeak", voice, ipa, f"[[{codes}]]", str(out_wav), round_trip=back)


# ---------------------------------------------------------------- Kokoro (shared front end)

def kokoro_chunks(ipa: str) -> list[tuple[str, list[bool]]]:
    """Converter IPA → [(Kokoro phoneme string, per-character high-tone flags)], one chunk per ‖ group.
    ˈ is kept (it is in Kokoro's vocab); acutes become flags. Raises UnsupportedPhone if anything is left
    outside Kokoro's vocab, since KModel would drop it silently."""
    s = _nfd(ipa).replace(".", "").replace("ʷʱ", "ʱʷ")
    for a, b in KOKORO_SUBST.items():
        s = s.replace(a, b)
    chunks, chars, high = [], [], []

    def flush(end: str):
        while chars and chars[-1] == " ":
            chars.pop(), high.pop()
        if chars:
            if end:
                chars.append(end), high.append(False)
            chunks.append(("".join(chars), list(high)))
        chars.clear(), high.clear()

    for ch in s:
        if ch == "‖":
            flush(".")
        elif ch == "|":
            while chars and chars[-1] == " ":
                chars.pop(), high.pop()
            chars.append(","), high.append(False)
        elif ch == HIGH:
            high[-1] = True
        elif ch == SYLLABIC:               # C̩ → əC; the schwa carries the accent and length
            chars.insert(len(chars) - 1, "ə"), high.insert(len(high) - 1, False)
        elif ch == " " and not chars:
            continue
        else:
            chars.append(ch), high.append(False)
    flush("")
    out = []
    for ph, hi in chunks:
        for i, c in enumerate(ph):
            if hi[i] and c in "rlmn" and i and ph[i - 1] == "ə":
                hi[i - 1] = True               # the accent on a syllabic resonant goes to its schwa
            if c == LONG and i and hi[i - 1]:
                hi[i] = True                   # a long accented vowel is high through its length mark
        bad = sorted({c for c in ph if c not in KOKORO_VOCAB})
        if bad:
            raise UnsupportedPhone(f"not in Kokoro's vocab: {bad} in {_nfc(ph)!r} (from {ipa!r})")
        if len(ph) > KOKORO_MAX_TOKENS:
            raise SpeechError(f"chunk of {len(ph)} phonemes exceeds Kokoro's {KOKORO_MAX_TOKENS}; add breaks")
        out.append((ph, hi))
    return out


def _write_wav(path: str, samples, rate: int = KOKORO_RATE) -> None:
    import numpy as np
    a = (np.clip(np.asarray(samples, dtype=np.float32), -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1), f.setsampwidth(2), f.setframerate(rate)
        f.writeframes(a.tobytes())


def _silence(seconds: float, rate: int = KOKORO_RATE):
    import numpy as np
    return np.zeros(int(seconds * rate), dtype=np.float32)


# ---------------------------------------------------------------- Kokoro local

_KOKORO = {}


def kokoro_file(name: str) -> Path:
    """Download (once) a pinned Kokoro file into the gitignored cache and verify its sha256."""
    from huggingface_hub import hf_hub_download
    p = Path(hf_hub_download(KOKORO_REPO, name, revision=KOKORO_REVISION, cache_dir=str(KOKORO_CACHE)))
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != KOKORO_FILES[name]:
        raise SpeechError(f"{name}: sha256 {h} != pinned {KOKORO_FILES[name]}")
    return p


def kokoro_status() -> str | None:
    """None when the local kokoro backend is importable, else the reason it is not."""
    try:
        import kokoro  # noqa: F401
        import torch  # noqa: F401
    except ImportError as e:
        return f"kokoro not importable ({e}); it needs Python < 3.13: {KOKORO_ENV_HINT}"
    return None


def _kokoro_model():
    why = kokoro_status()
    if why:
        raise SpeechError(why)
    if "model" not in _KOKORO:
        from kokoro import KModel
        _KOKORO["model"] = KModel(repo_id=KOKORO_REPO, config=str(kokoro_file("config.json")),
                                  model=str(kokoro_file("kokoro-v1_0.pth"))).eval()
    return _KOKORO["model"]


def _kokoro_voice(name: str):
    import torch
    key = "voice:" + name
    if key not in _KOKORO:
        f = f"voices/{name}.pt"
        if f not in KOKORO_FILES:
            raise SpeechError(f"voice {name!r} not pinned; known: {sorted(k[7:-3] for k in KOKORO_FILES if k.startswith('voices/'))}")
        _KOKORO[key] = torch.load(kokoro_file(f), weights_only=True)
    return _KOKORO[key]


def _kokoro_synth(model, ref_s, ph: str, high: list[bool], *, pitch: bool, speed: float,
                  boost: float = 1.3, flat: float = 0.92):
    """One chunk through KModel; with pitch, the predicted F0 is flattened (flat × median) and raised
    (boost × median) on the frames of the high-flagged phonemes (docs/research/tts-options.md §4.2)."""
    import torch
    ids = torch.LongTensor([[0, *[model.vocab[c] for c in ph], 0]])
    if not pitch or not any(high):
        with torch.no_grad():
            audio, _ = model.forward_with_tokens(ids, ref_s, speed)
        return audio.numpy()
    hmask = torch.tensor([False, *high, False])
    with torch.no_grad():
        _, dur = model.forward_with_tokens(ids, ref_s, speed)
    orig = model.predictor.F0Ntrain

    def patched(en, s):
        F0, N = orig(en, s)
        frames = torch.repeat_interleave(torch.repeat_interleave(hmask, dur), 2)[: F0.shape[-1]]
        if frames.shape[0] < F0.shape[-1]:
            frames = torch.nn.functional.pad(frames, (0, F0.shape[-1] - frames.shape[0]))
        voiced = F0[0] > 10
        base = F0[0][voiced].median() if voiced.any() else torch.tensor(150.0)
        target = torch.where(frames, base * boost, base * flat)
        target = torch.nn.functional.conv1d(target[None, None], torch.ones(1, 1, 9) / 9, padding=4)[0, 0]
        return torch.where(voiced, target, F0[0])[None], N

    model.predictor.F0Ntrain = patched
    try:
        with torch.no_grad():
            audio, _ = model.forward_with_tokens(ids, ref_s, speed)
    finally:
        model.predictor.F0Ntrain = orig
    return audio.numpy()


def _speak_kokoro(ipa: str, out_wav: str, *, tone, voice: str | None, pitch: bool, speed: float) -> SpeechResult:
    import numpy as np
    voice = voice or "hf_alpha"
    use_pitch = pitch and tone is True
    src = ipa if use_pitch else acute_to_stress(ipa)
    model, pack = _kokoro_model(), _kokoro_voice(voice)
    parts, inputs = [], []
    for ph, high in kokoro_chunks(src):
        parts += [_kokoro_synth(model, pack[len(ph) - 1], ph, high, pitch=use_pitch, speed=speed), _silence(0.3)]
        inputs.append(ph)
    _write_wav(out_wav, np.concatenate(parts) if parts else _silence(0.1))
    return SpeechResult("kokoro", voice + (" +pitch" if use_pitch else ""), ipa, _nfc(" ‖ ".join(inputs)), str(out_wav))


# ---------------------------------------------------------------- Kokoro remote (Kokoro-FastAPI)

def _remote_wav(phonemes: str, voice: str) -> bytes:
    body = json.dumps({"phonemes": phonemes, "voice": voice}, ensure_ascii=False).encode("utf-8")
    url = os.environ.get("PIE_KOKORO_URL")
    if url:
        req = urllib.request.Request(url.rstrip("/") + REMOTE_PATH, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.read()
    host = os.environ.get("PIE_KOKORO_SSH", "erebus")
    port = os.environ.get("PIE_KOKORO_PORT", "8880")
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host,
           f"curl -sS -f -m 180 -X POST localhost:{port}{REMOTE_PATH} -H 'Content-Type: application/json' --data-binary @-"]
    p = subprocess.run(cmd, input=body, capture_output=True)
    if p.returncode:
        raise SpeechError(f"kokoro-remote via ssh {host} failed ({p.returncode}): {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def _speak_kokoro_remote(ipa: str, out_wav: str, *, voice: str | None) -> SpeechResult:
    import numpy as np
    voice = voice or "hf_alpha"
    parts, inputs, rate = [], [], None
    for ph, _ in kokoro_chunks(acute_to_stress(ipa)):
        data = _remote_wav(_nfc(ph), voice)
        try:
            with wave.open(io.BytesIO(data)) as w:
                if w.getsampwidth() != 2 or w.getnchannels() != 1:
                    raise SpeechError("kokoro-remote returned a non-16-bit-mono wav")
                rate = rate or w.getframerate()
                a = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32767
        except wave.Error as e:
            raise SpeechError(f"kokoro-remote returned no wav ({e}): {data[:200]!r}") from None
        parts += [a, _silence(0.3, rate)]
        inputs.append(ph)
    rate = rate or KOKORO_RATE
    _write_wav(out_wav, np.concatenate(parts) if parts else _silence(0.1, rate), rate)
    return SpeechResult("kokoro-remote", voice, ipa, _nfc(" ‖ ".join(inputs)), str(out_wav),
                        notes=["accent sent as ˈ (no F0 control on the server)"])


# ---------------------------------------------------------------- Kokoro on erebus (pie-tts, tts/erebus/)

def kokoro_erebus_url() -> str:
    return os.environ.get("PIE_KOKORO_PITCH_URL", "http://localhost:8881").rstrip("/")


def kokoro_erebus_status(timeout: float = 2.0) -> str | None:
    """None when the pie-tts service answers GET /health, else the reason it does not."""
    url = kokoro_erebus_url() + "/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            if json.loads(r.read()).get("status") == "ok":
                return None
            return f"{url}: not ok"
    except Exception as e:  # noqa: BLE001 - any failure means "not reachable"
        return f"pie-tts not reachable at {url} ({e}); tunnel: ssh -N -L 8881:localhost:8881 erebus"


def _speak_kokoro_erebus(ipa: str, out_wav: str, *, tone, voice: str | None, pitch: bool,
                         speed: float) -> SpeechResult:
    from urllib.error import HTTPError, URLError
    from urllib.parse import unquote
    voice = voice or "hf_alpha"
    body = json.dumps({"ipa": ipa, "tone": tone, "voice": voice, "pitch": pitch, "speed": speed},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(kokoro_erebus_url() + "/speak_ipa", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data, hdr = r.read(), r.headers
    except HTTPError as e:
        try:
            err = json.loads(e.read())
        except ValueError:
            err = {"error": str(e)}
        cls = UnsupportedPhone if err.get("type") == "UnsupportedPhone" else SpeechError
        raise cls(f"kokoro-erebus: {e.code} {err.get('error')}") from None
    except URLError as e:
        raise SpeechError(f"kokoro-erebus: {kokoro_erebus_url()} unreachable ({e.reason}); "
                          "tunnel: ssh -N -L 8881:localhost:8881 erebus") from None
    try:
        with wave.open(io.BytesIO(data)) as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1 or w.getframerate() != KOKORO_RATE:
                raise SpeechError("kokoro-erebus returned a wav that is not 16-bit mono 24 kHz")
    except wave.Error as e:
        raise SpeechError(f"kokoro-erebus returned no wav ({e}): {data[:200]!r}") from None
    Path(out_wav).write_bytes(data)
    return SpeechResult("kokoro-erebus", unquote(hdr.get("X-PIE-Voice", voice)), ipa,
                        unquote(hdr.get("X-PIE-Engine-Input", "")), str(out_wav))


# ---------------------------------------------------------------- API

def speak_ipa(ipa: str, *, backend: str = "espeak", out_wav: str = "out.wav", tone: bool | str = True,
              voice: str | None = None, strict: bool = True, pitch: bool = True, rate: int = 130,
              espeak_pitch: int | None = None, speed: float = 0.9) -> SpeechResult:
    """Render converter IPA (to_ipa output, with acutes for tone=True or ˈ for tone="stress").

    tone: True renders the acute as pitch (espeak: level tones; kokoro: imposed F0 when pitch=True);
    "stress"/False render ˈ marks only. voice: espeak voice (default pie/pie-tone or pie/pie) or Kokoro voice
    (default hf_alpha). strict: espeak round-trip mismatch raises (True) or warns (False)."""
    if backend not in BACKENDS:
        raise ValueError(f"unknown backend {backend!r}; known: {BACKENDS}")
    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    if backend == "espeak":
        return _speak_espeak(ipa, out_wav, tone=tone is True, strict=strict, rate=rate, pitch=espeak_pitch,
                             voice=voice)
    if backend == "kokoro":
        return _speak_kokoro(ipa, out_wav, tone=tone, voice=voice, pitch=pitch, speed=speed)
    if backend == "kokoro-erebus":
        return _speak_kokoro_erebus(ipa, out_wav, tone=tone, voice=voice, pitch=pitch, speed=speed)
    return _speak_kokoro_remote(ipa, out_wav, voice=voice)


def speak(pie_text: str, backend: str = "espeak", out_wav: str = "out.wav", convention="default",
          tone: bool | str = True, *, ascii: bool = False, **kw) -> SpeechResult:
    """Canonical PIE (or pie_ascii with ascii=True) → wav. See speak_ipa for the keyword options."""
    ipa = to_ipa(pie_text, convention=convention, tone=tone, ascii=ascii)
    return speak_ipa(ipa, backend=backend, out_wav=out_wav, tone=tone, **kw)
