"""The TTS corpus builder (pie/tts_data.py): one IPA convention end to end, labels in vocab, sane timelines."""
import json
import unicodedata
from pathlib import Path

import pytest

from pie import tts_data as T

ROOT = Path(__file__).resolve().parents[1]
CLIPS = ROOT / "tts/cadence/eleven/v10/zip/pie-vtl/batch_example/clips"


@pytest.mark.skipif(not CLIPS.is_dir(), reason="v10 batch example not extracted")
def test_word_ipa_is_what_vtl_renders():
    for f in CLIPS.glob("*.json"):
        for w in json.loads(f.read_text("utf-8")):
            assert T.word_ipa(w["word"]) == unicodedata.normalize("NFC", w["ipa"]), (f.name, w["word"])


def test_label_symbols_and_conventions():
    s = T.text_label("dyḗws ph₂tḗr h₁ésti, nébʰesh₂-kʷe gʷm̥sḱéti?")
    assert "." not in s[:-1] and "-" not in s and s.endswith("?") and ", " in s
    assert all(c in T.LABEL_VOCAB for c in s)
    assert unicodedata.normalize("NFD", s) == s
    assert {"ʱ", "ʷ", "́"} <= set(s)


def test_extra_ids_unused_in_kokoro():
    assert not set(T.KOKORO_EXTRA.values()) & set(T.KOKORO_VOCAB.values())
    assert max(T.LABEL_VOCAB.values()) < 178


def test_prose_timeline_monotonic_and_label_matches():
    c = T.clips_for_work([{"id": "t3-x-00001", "pie": "kʷíd wóǵʰosyo bʰórom bʰéreti? wéǵʰeti kʷékʷlos tóm.",
                           "genre": "dialogue"}])
    assert len(c) == 1
    ws = c[0].words
    t = 0.0
    for w in ws:
        assert w["start"] >= t - 1e-9 and w["end"] > w["start"]
        t = w["end"] + w["pause_after"]
    assert c[0].label == T.text_label(c[0].pie)
    assert ws[3]["pause_after"] == T.PROSE_STOP


def test_filenames_ascii():
    assert T.filename("t3-b001-00001-p00", "W02-PIE") == "t3-b001-00001-p00__W02-PIE.wav"
    with pytest.raises(ValueError):
        T.filename("ḱ", "JD3-PIE")
