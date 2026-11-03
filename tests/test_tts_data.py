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
    assert T.STOP_RANGE[0] <= ws[3]["pause_after"] <= T.STOP_RANGE[1]
    assert [w["line"] for w in ws] == [1, 1, 1, 1, 2, 2, 2]          # one pitch line per sentence
    assert ws[3].get("rise") and not any(w.get("rise") for w in ws[4:])
    assert c[0].timeline()[3]["rise"] is True


def test_comma_is_a_caesura_inside_the_line():
    ws = T.prose_words("h₁ésti wl̥kʷos, h₁ésti h₁éḱwos.", "k")
    assert {w["line"] for w in ws} == {1}
    assert ws[1]["pause_after"] == T.PROSE_COMMA < 0.5 <= T.STOP_RANGE[0]
    pv = T._pie_vtl()
    plain = sum(pv.default_durations(pv.parse_word(ws[0]["ipa"]), False))
    rate = plain / (ws[0]["end"] - ws[0]["start"])                     # an unpunctuated word: rate only
    comma = sum(pv.default_durations(pv.parse_word(ws[1]["ipa"]), False)) / rate * T.CAESURA_LEN
    assert abs((ws[1]["end"] - ws[1]["start"]) - comma) < 1e-3 and T.RATE_RANGE[0] <= rate <= T.RATE_RANGE[1]


V10 = ROOT / "tts/cadence/eleven/v10/zip/pie-vtl"


@pytest.mark.skipif(not V10.is_dir(), reason="v10 bundle not extracted")
def test_v10_1_contour_unchanged_without_rise():
    """pie_vtl v10.1 only adds the question rise: a timeline without "rise" gets v10's exact F0 targets."""
    import importlib.util
    def load(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    old, new = load(V10 / "pie_vtl.py", "pie_vtl_v10"), load(ROOT / "tts/vtl/pie_vtl.py", "pie_vtl_v101")
    tl = json.loads((V10 / "dawn-hymn-cadence.json").read_text("utf-8"))
    def contour(m, words):
        timed, total, ws = m.build_timeline([dict(w) for w in words], 1.0, cadence=True)
        g = m.f0_contour(timed, ws, 0.0)
        return [round(g(i * 0.01), 9) for i in range(int(total * 100))]
    assert contour(old, tl) == contour(new, tl)
    risen = [dict(w) for w in tl]; risen[-1]["rise"] = True
    a, b = contour(new, tl), contour(new, risen)
    assert a != b and a[:int(risen[-1]["start"] * 100) - 5] == b[:int(risen[-1]["start"] * 100) - 5]


def test_filenames_ascii():
    assert T.filename("t3-b001-00001-p00", "W02-PIE") == "t3-b001-00001-p00__W02-PIE.wav"
    with pytest.raises(ValueError):
        T.filename("ḱ", "JD3-PIE")


def test_trill_auto_by_position():
    pv = T._pie_vtl()
    assert pv.TRILL == "auto"
    def n(ipa):
        segs = pv.parse_word(ipa); pv.mark_trills(segs)
        return [pv.trill_n(x) for x in segs if x.base == "r" and not x.syllabic]
    assert n("réːɟs") == [3]                    # word-initial
    assert n("bʱráχ.teːr") == [2, 1]            # after a consonant; final r after a vowel: tap
    assert n("wé.ro.s") == [1]                   # between vowels
    segs = pv.parse_word("χŕ̩t.cos"); pv.mark_trills(segs)
    assert not any(hasattr(x, "trill") for x in segs if x.syllabic)
    w = T.prose_words("rḗḱs.", "k")[0]
    plain = sum(pv.default_durations(pv.parse_word(T.word_ipa("rḗḱs")), True))
    assert w["end"] - w["start"] > plain / T.RATE_RANGE[1]   # the trill's 3 x 40 ms are in the timing
