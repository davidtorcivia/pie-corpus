"""pie/speak.py: eSpeak mapping coverage and round trip, Kokoro front end, CLI.

Tests that need espeak-ng and the compiled PIE voice (sh tts/espeak/build.sh) skip without them; Kokoro
rendering skips unless the kokoro group is importable (Python < 3.13 env) and the weights are cached;
the remote server is only contacted with PIE_TEST_KOKORO_REMOTE=1.
"""

import json
import os
import subprocess
import sys
import unicodedata
import wave
from pathlib import Path

import pytest

from pie import ipa as I
from pie import speak as S

ROOT = Path(__file__).resolve().parent.parent
NFD = lambda s: unicodedata.normalize("NFD", s)  # noqa: E731

needs_espeak = pytest.mark.skipif(S.espeak_status() is not None, reason=str(S.espeak_status()))

# The presets plus every Convention option eSpeak supports; uvular and syllabic are expected to raise.
SUPPORTED = {**I.CONVENTIONS,
             "fronted": I.Convention("fronted", dorsals="fronted"),
             "colored": I.Convention("colored", vocalized="colored"),
             "voiceless": I.Convention("voiceless", laryngeals="voiceless"),
             "generic-glottal": I.Convention("generic-glottal", generic="ʔ")}


def emitted_phones(conv: I.Convention) -> tuple[list[str], list[str]]:
    """(margin phones, nucleus phones) the converter can emit under conv, read from pie.ipa's own tables."""
    margins = sorted(set(conv.consonants.values()) | set(I._RESONANT.values()))
    nuclei = set(I._SYL_RESONANT.values()) | set("aeiou")
    nuclei |= {conv.vocalized_laryngeal(h) for h in ("h1", "h2", "h3", "H")}
    return margins, sorted(nuclei)


def probe_words(conv: I.Convention) -> list[str]:
    """Each phone in an IPA test word: margins as onset and coda, nuclei short, long, accented."""
    margins, nuclei = emitted_phones(conv)
    out = [f"a.{m}a" for m in margins] + [f"a{m}" for m in margins]
    vocalized = {conv.vocalized_laryngeal(h) for h in ("h1", "h2", "h3", "H")}
    out += [f"t{v}.ta" for v in sorted(vocalized)]          # never long, never accented (pie.ipa._nucleus)
    for v in sorted(set(nuclei) - vocalized):
        out += [f"t{v}", f"t{v}{I.LONG}", unicodedata.normalize("NFC", f"t{v}{I.HIGH}.ta")]
        if v not in "iu":
            out.append(unicodedata.normalize("NFC", f"t{v}{I.HIGH}{I.LONG}"))
    return out


@pytest.mark.parametrize("name", sorted(SUPPORTED))
def test_mapping_covers_every_emitted_phone(name):
    """Pure: every phone of the convention maps to eSpeak mnemonics and to Kokoro's vocab."""
    for w in probe_words(SUPPORTED[name]):
        S.espeak_codes(w, tone=True)
        S.espeak_codes(S.acute_to_stress(w), tone=False)
        S.kokoro_chunks(w)


def test_mapping_codepoints_cover_converter_symbols():
    """Every code point to_ipa can put in a string is mapped, or is handled as a whole phone or a mark."""
    syms = set()
    for conv in SUPPORTED.values():
        for w in probe_words(conv):
            syms |= set(NFD(w))
    handled = set(S.ESPEAK_MAP["codepoints"]) | {I.HIGH, I.SYLLABIC, "."} | set(NFD("".join(S.ESPEAK_MAP["phone_substitutions"])))
    assert syms - handled == set()


@pytest.mark.parametrize("conv", [I.Convention("u", dorsals="uvular"), I.Convention("s", vocalized="syllabic")])
def test_unsupported_conventions_raise(conv):
    with pytest.raises(S.UnsupportedPhone):
        S.espeak_codes(I.to_ipa("ph₂tḗr gʰóstis", convention=conv), tone=True)


@needs_espeak
@pytest.mark.parametrize("name", sorted(SUPPORTED))
@pytest.mark.parametrize("tone", [True, False])
def test_every_emitted_phone_round_trips(name, tone):
    """Production path: the exact codes for each probe word are read back by espeak-ng --ipa unchanged."""
    words = probe_words(SUPPORTED[name])
    ipa = " ".join(w if tone else S.acute_to_stress(w) for w in words)
    voice = S.VOICE_TONE if tone else S.VOICE_STRESS
    S.check_round_trip(ipa, S.espeak_codes(ipa, tone=tone), voice)


@needs_espeak
@pytest.mark.parametrize("conv", ["default", "pharyngeal", "uncolored"])
def test_tier1_round_trips(conv):
    for f in sorted((ROOT / "corpus" / "tier1").glob("*.jsonl")):
        for line in f.read_text("utf-8").splitlines():
            r = json.loads(line)
            if not r.get("pie"):
                continue
            for tone in (True, "stress"):
                ipa = I.to_ipa(r["pie"], convention=conv, tone=tone)
                S.check_round_trip(ipa, S.espeak_codes(ipa, tone=tone is True),
                                   S.VOICE_TONE if tone is True else S.VOICE_STRESS)


@needs_espeak
@pytest.mark.parametrize("codes", ["H'eKw0s", "H'ekw0s", "He5Kw0s1"])
def test_round_trip_catches_truncation(codes):
    """An unknown mnemonic makes eSpeak silently drop the rest of the word ([[H'eKw0s]] -> ħˈe)."""
    with pytest.raises(S.RoundTripError, match="word 1"):
        S.check_round_trip("ħé.kʷos", codes, S.VOICE_STRESS)


@needs_espeak
def test_round_trip_catches_a_bad_mapping(monkeypatch, tmp_path):
    """A wrong entry in mapping.json is caught at render time, not shipped as a truncated wav."""
    monkeypatch.setitem(S.ESPEAK_MAP["codepoints"], "χ", "X0")
    with pytest.raises(S.RoundTripError):
        S.speak("h₂ówis", out_wav=str(tmp_path / "never.wav"))
    assert not (tmp_path / "never.wav").exists()


@needs_espeak
def test_non_strict_warns(recwarn, capsys):
    S.check_round_trip("ħé.kʷos", "H'eKw0s", S.VOICE_STRESS, strict=False)
    assert any("round trip mismatch" in str(w.message) for w in recwarn.list)
    assert "WARNING" in capsys.readouterr().err


@needs_espeak
def test_long_input_is_split_into_pieces(tmp_path):
    """eSpeak reads [[...]] longer than ~750 characters as two clauses, the second as English text."""
    ipa = I.to_ipa(" ".join(["h₂ówis h₁éḱwōs-kʷe dʰugh₂tḗr"] * 40))
    codes = S.espeak_codes(ipa, tone=True)
    assert len(codes) > 1000 and all(len(p) <= S.ESPEAK_PIECE for p in S.espeak_pieces(codes))
    unsplit = S._espeak(["-v", S.VOICE_TONE, "-q", "--ipa", f"[[{codes}]]"])
    assert S.normalize_espeak_ipa(unsplit) != S.expected_espeak_ipa(ipa)      # the failure being guarded
    r = S.speak_ipa(ipa, out_wav=str(tmp_path / "long.wav"))
    with wave.open(r.out_wav) as w:
        assert w.getnframes() / w.getframerate() > 20


@needs_espeak
@pytest.mark.parametrize("tone", [True, "stress", False])
def test_speak_espeak_writes_wav(tmp_path, tone):
    r = S.speak("h₂ówis h₁éḱwōs-kʷe. ḱléwos ń̥dʰgʷʰitom", out_wav=str(tmp_path / "a.wav"), tone=tone)
    assert r.voice == (S.VOICE_TONE if tone is True else S.VOICE_STRESS)
    with wave.open(r.out_wav) as w:
        assert w.getframerate() == 22050 and w.getnframes() > 22050


def test_tone_codes():
    assert S.espeak_codes("χá.ɟe.ti", tone=True) == "Xa5Je1ti1"
    assert S.espeak_codes("ń̩dʱ.ɡʷʱi.tom", tone=True) == "n-d#5g#wi1tom1"
    assert S.espeak_codes("pə.ˈteːr ‖ kʷe", tone=False) == "p@'te:R _: kwe"


def test_kokoro_front_end():
    [(ph, high)] = S.kokoro_chunks("n̩dʱ.ɡʷʱi.tóm")
    assert ph == NFD("əndʰɡʰwitom") and [c for c, h in zip(ph, high) if h] == ["o"]
    [(ph, high)] = S.kokoro_chunks("ɟʱi.méː")
    assert [c for c, h in zip(ph, high) if h] == ["e", "ː"]
    [(ph, high)] = S.kokoro_chunks("wĺ̩.kʷos")
    assert ph == "wəlkwos" and high[1]
    chunks = S.kokoro_chunks("ħé.kʷos | ʕʷé ‖ dʱu.ɡə.téːr")
    assert [c for c, _ in chunks] == [NFD("χekwos, ɣwe."), NFD("dʰuɡəteːr")]
    assert S.acute_to_stress("χó.wis héc.woːs.kʷe") == "ˈχo.wis ˈhec.woːs.kʷe"


def test_kokoro_rejects_out_of_vocab():
    with pytest.raises(S.UnsupportedPhone):
        S.kokoro_chunks("tθ̼")


def _cached(name):
    return (S.KOKORO_CACHE / "models--hexgrad--Kokoro-82M" / "snapshots" / S.KOKORO_REVISION / name).exists()


@pytest.mark.skipif(S.kokoro_status() is not None or not _cached("kokoro-v1_0.pth"),
                    reason="kokoro group not importable here, or weights not cached")
@pytest.mark.parametrize("pitch", [True, False])
def test_kokoro_local_renders(tmp_path, pitch):
    r = S.speak("ǵʰimḗ", backend="kokoro", out_wav=str(tmp_path / "k.wav"), pitch=pitch)
    assert r.voice.startswith("hf_alpha") and ("pitch" in r.voice) == pitch
    with wave.open(r.out_wav) as w:
        assert w.getframerate() == 24000 and w.getnframes() > 4800


@pytest.mark.skipif(os.environ.get("PIE_TEST_KOKORO_REMOTE") != "1", reason="set PIE_TEST_KOKORO_REMOTE=1")
def test_kokoro_remote_renders(tmp_path):
    r = S.speak("ǵʰimḗ", backend="kokoro-remote", out_wav=str(tmp_path / "r.wav"), voice="hm_omega")
    with wave.open(r.out_wav) as w:
        assert w.getnframes() > 4800


_EREBUS = S.kokoro_erebus_status()


@pytest.mark.skipif(_EREBUS is not None, reason=str(_EREBUS))
def test_kokoro_erebus_renders(tmp_path):
    """The pie-tts service (tts/erebus/) through PIE_KOKORO_PITCH_URL: pitch-patched, same front end."""
    r = S.speak("ǵʰimḗ", backend="kokoro-erebus", out_wav=str(tmp_path / "e.wav"))
    assert r.backend == "kokoro-erebus" and r.voice == "hf_alpha +pitch"
    assert r.engine_input == unicodedata.normalize("NFC", S.kokoro_chunks(r.ipa)[0][0])
    with wave.open(r.out_wav) as w:
        assert w.getframerate() == 24000 and w.getnchannels() == 1 and w.getnframes() > 4800
    with pytest.raises(S.UnsupportedPhone):
        S.speak_ipa("tθ̼", backend="kokoro-erebus", out_wav=str(tmp_path / "x.wav"))
    with pytest.raises(S.SpeechError, match="limit"):
        S.speak_ipa("ta " * 700, backend="kokoro-erebus", out_wav=str(tmp_path / "y.wav"))


# ---------------------------------------------------------------- CLI

def _cli(*args, stdin=None):
    return subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "speak.py"), *args], input=stdin,
                          capture_output=True, text=True, cwd=ROOT)


@needs_espeak
def test_cli_text_and_stdin(tmp_path):
    p = _cli("-o", str(tmp_path / "a.wav"), "h₂ówis h₁éḱwōs-kʷe")
    assert p.returncode == 0, p.stderr
    assert "χó.wis" in p.stdout and "[[Xo5wis1" in p.stdout and (tmp_path / "a.wav").stat().st_size > 10000
    p = _cli("--ascii", "--tone", "stress", "-o", str(tmp_path / "b.wav"), stdin="h2o/wis\nph2te:/r\n")
    assert p.returncode == 0, p.stderr
    assert "ˈχo.wis ‖ pə.ˈteːr" in p.stdout and (tmp_path / "b.wav").exists()
    p = _cli("--ipa", "-o", str(tmp_path / "c.wav"), "ʔés.ti")
    assert p.returncode == 0 and "[[?es5ti1]]" in p.stdout


@needs_espeak
def test_cli_unsupported_phone_exit_1(tmp_path):
    p = _cli("--ipa", "-o", str(tmp_path / "x.wav"), "ɢá")
    assert p.returncode == 1 and "voiced uvular" in p.stderr


def test_cli_bad_text_exit_2(tmp_path):
    p = _cli("-o", str(tmp_path / "x.wav"), "qqq%%")
    assert p.returncode == 2 and "error" in p.stderr
