import math

import pytest

from pie import backtest as bt
from pie.prelaryngeal import convert


def row(target, effects=(), id="w", root=None):
    return {"id": id, "root_id": root, "target": target, "inputs": {},
            "effects": [{"kind": k, "laryngeal": "h2", "offset": o} for k, o in effects]}


def test_segments_keep_marks_and_modifiers():
    assert bt.segments("dʰugətḗr") == ["dʰ", "u", "g", "ə", "t", "ḗ", "r"]
    assert bt.segments("gʷʰn̥̄") == ["gʷʰ", "n̥̄"]


def test_offset_to_slot_nfc_and_end():
    # n̥dʰí: n(0) ̥(1) d(2) ʰ(3) í(4); len 5 = end slot
    t = "n̥dʰí"
    assert [bt.offset_to_slot(t, o) for o in (0, 2, 4, 5)] == [0, 1, 2, 3]
    with pytest.raises(ValueError):
        bt.offset_to_slot(t, 7)


def test_effect_slots_shared_offset():
    r = row("ḗḱus", [("loss", 0), ("length", 0)])
    assert bt.effect_slots(r) == {0: {"loss", "length"}}


def test_effect_slots_from_transducer():
    text, eff = convert("ph₂tḗr")
    r = {"target": text, "effects": [{"kind": e.kind, "offset": e.offset} for e in eff]}
    assert bt.effect_slots(r) == {1: {"schwa"}}
    assert bt.segments(text)[1] == "ə"
    text, eff = convert("h₂eǵ-")
    r = {"target": text, "effects": [{"kind": e.kind, "offset": e.offset} for e in eff]}
    assert bt.effect_slots(r) == {0: {"color", "loss"}}


def test_loss_at_end_slot():
    r = row("tos", [("loss", 3)])
    assert bt.effect_slots(r) == {3: {"loss"}}
    assert bt.stratum(bt.segments("tos"), 3) == (bt.EOS, "end")


def test_strata():
    us = bt.segments("ḗtāt")
    assert bt.stratum(us, 0) == ("ḗ", "initial")
    assert bt.stratum(us, 2, "class") == ("V", True, False, "medial")
    assert bt.stratum(us, 3, "class") == ("C", False, False, "final")
    assert bt.stratum(bt.segments("ǵónu"), 0, "class") == ("C", False, False, "initial")  # palatal acute is not accent
    assert bt.is_vowel("r̥̄") and not bt.is_vowel("r")


def word(target, eff_slots, metric, id="w", fam=None):
    us = bt.segments(target)
    return bt.Word(id, fam or id, us, {s: {k} for s, k in eff_slots.items()}, {"m": metric})


def test_match_prefers_same_word_then_corpus():
    # t é t é s : effect at slot 1 (medial é); slot 3 is a same-word control
    a = word("tétés", {1: "length"}, [0, 1, 0, 0, 0, 0], id="a")
    # b: effect at medial é with no same-word control; a's slot 3 is the corpus control
    b = word("tés", {1: "loss"}, [0, 1, 0, 0], id="b")
    m = {x["word"]: x for x in bt.match([a, b], min_families=1)}
    assert m[0]["controls"] == [(0, 3)] and m[0]["where"] == "word"
    assert m[1]["controls"] == [(0, 3)] and m[1]["where"] == "corpus"


def test_match_none_when_stratum_has_no_controls():
    a = word("tə", {1: "schwa"}, [0, 1, 0], id="a")
    assert bt.match([a])[0]["where"] == "none"
    r = bt.matched_contrast([a], "m")
    assert r["n_matched"] == 0 and r["diff"] is None


def test_matched_contrast_value_and_ci():
    ws = [word("tétés", {1: "length"}, [0, 1.0, 0, 0.0, 0, 0], id=f"a{i}") for i in range(5)]
    r = bt.matched_contrast(ws, "m", n_boot=200)
    assert r["n_matched"] == 5 and r["n_same_word"] == 5
    assert r["diff"] == pytest.approx(1.0) and r["ci"] == [pytest.approx(1.0), pytest.approx(1.0)]
    assert bt.matched_contrast(ws, "m", kind="loss")["n_matched"] == 0
    assert bt.matched_contrast(ws, "m", kind="length")["diff"] == pytest.approx(1.0)


def test_matched_contrast_null_ci_covers_zero():
    import random
    rng = random.Random(1)
    ws = [word("tétés", {1: "length"}, [0, rng.random(), 0, rng.random(), 0, 0], id=f"a{i}") for i in range(60)]
    r = bt.matched_contrast(ws, "m", n_boot=500)
    assert r["ci"][0] < 0 < r["ci"][1]


def test_bootstrap_clusters_by_family():
    # two families: one with a big effect, one with none; CI must reflect between-family spread
    ws = [word("tétés", {1: "length"}, [0, 1.0, 0, 0.0, 0, 0], id=f"a{i}", fam="A") for i in range(10)]
    ws += [word("tétés", {1: "length"}, [0, 0.0, 0, 0.0, 0, 0], id=f"b{i}", fam="B") for i in range(10)]
    r = bt.matched_contrast(ws, "m", n_boot=500, min_families=1)
    assert r["n_families"] == 2 and r["diff"] == pytest.approx(0.5)
    assert r["ci"][0] == pytest.approx(0.0) and r["ci"][1] == pytest.approx(1.0)


def test_slot_metrics():
    m = bt.slot_metrics([{"a": 0.5, "b": 0.5}, {"a": 0.9, "b": 0.1}], ["a", "b"])
    assert m["entropy"][0] == pytest.approx(math.log(2))
    assert m["error"] == [0.0, 1.0]
    assert m["surprisal"][1] == pytest.approx(-math.log(0.1))


def test_freq_baseline():
    fb = bt.FreqBaseline(["ta", "ta", "to"], order=2)
    for prev in ("<s>", "t", "a"):
        assert sum(fb.dist(prev).values()) == pytest.approx(1.0)
    m = fb.word_metrics("ta")
    assert len(m["error"]) == 3 and m["error"][1] == 0.0      # after t, a is the most frequent
    uni = bt.FreqBaseline(["ta", "ta", "to"], order=1)
    assert len(set(uni.word_metrics("to")["entropy"])) == 1      # unigram entropy is constant


def test_encode_and_shuffle():
    order = ["Latin", "Sanskrit"]
    seq = bt.encode_inputs({"Sanskrit": ["ā", "b", "c"], "Latin": ["x"]}, order, max_forms=2)
    syms = [s for s, _ in seq]
    assert syms == ["<lang>", "x", "<sep>", "<lang>", "a", "̄", "<sep>", "b", "<sep>"]
    rows = [{"id": str(i), "inputs": {"L": [str(i)]}, "target": f"t{i}"} for i in range(20)]
    sh = bt.shuffle_inputs(rows, seed=3)
    assert [r["target"] for r in sh] == [r["target"] for r in rows]
    assert sorted(r["inputs"]["L"][0] for r in sh) == sorted(r["inputs"]["L"][0] for r in rows)
    assert any(r["inputs"] != s["inputs"] for r, s in zip(rows, sh))


def test_hittite_clean_and_slots():
    assert bt.hittite_clean("pa-aḫ-ḫur") == "paHur"
    assert bt.hittite_clean("GÍD.DA-aš") is None
    # ḫ inserted before the first unit of "ag" (h₂eǵ- → aǵ, Hitt. ḫa-)
    assert bt.hittite_slots(bt.segments("ag"), "Hag") == [{0}]
    # ḫ against schwa: p-ə-t-ḗ-r vs p-a-H-...: ḫ sits next to the schwa slot
    slots = bt.hittite_slots(bt.segments("pəwōr"), "paHur")
    assert slots and slots[0] & {1, 2}


def test_decolor_and_confusions():
    assert bt.decolor("ā́") == "ḗ" and bt.decolor("o") == "e" and bt.decolor("t") == "t"
    # color effect at medial á predicted as é; its control (same unit, other word) predicted correctly
    a = word("tát", {1: "color"}, [0, 0, 0, 0], id="a")
    b = word("tát", {}, [0, 0, 0, 0], id="b")
    am = [["t", "é", "t", "</w>"], ["t", "á", "t", "</w>"]]
    c = bt.confusions([a, b], am, "color", min_families=1)
    assert c["n_effect"] == 1 and c["decolored_share_effect"] == 1.0 and c["decolored_share_control"] == 0.0
    br = bt.stratum_breakdown([a, b], "m", kind="color", min_families=1)
    assert br[0]["stratum"] == ["á", "medial"] and br[0]["n"] == 1


def test_stratum_needs_controls_from_several_families():
    # 5 effect slots at medial é, one stray control word: unusable under the family rule
    ws = [word("tét", {1: "length"}, [0, 1.0, 0, 0], id=f"e{i}") for i in range(5)]
    ws.append(word("tét", {}, [0, 0.0, 0, 0], id="stray"))
    assert bt.matched_contrast(ws, "m")["n_matched"] == 0
    assert bt.matched_contrast(ws, "m", min_families=1)["n_matched"] == 5
    ws += [word("tét", {}, [0, 0.0, 0, 0], id=f"c{i}") for i in range(2)]
    assert bt.matched_contrast(ws, "m")["n_matched"] == 5
    row = next(r for r in bt.strata_table(ws) if r["stratum"] == ["é", "medial"])
    assert row["control_families"] == 3 and row["usable"]
