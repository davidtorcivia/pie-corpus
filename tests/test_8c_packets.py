"""Phase 8c packet builder (scripts/build_8c_packets.py): seed matching,
passage selection, decoys, reader assignment and blinding. Small invented
lexicon and units only; no corpus is loaded."""

import importlib.util
import json
import random
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "build_8c_packets", Path(__file__).resolve().parent.parent / "scripts" / "build_8c_packets.py")
B = importlib.util.module_from_spec(_spec)
sys.modules["build_8c_packets"] = B
_spec.loader.exec_module(B)

LETTERS = "abcdefghijklmnop"


def word(t: int, j: int) -> str:
    return "zq" + LETTERS[t - 1] + LETTERS[j]


def fixture_themes():
    return [(t, f"theme name {t}", [word(t, j) for j in range(3)], []) for t in range(1, 17)]


def fixture_lexicon():
    lex = []
    for t in range(1, 17):
        for j in range(3):
            lex.append({"id": f"pie-root-t{t}r{j}", "kind": "root", "form": f"r{t}{j}-",
                        "meaning": [f"to {word(t, j)}"], "root_id": f"pie-root-t{t}r{j}"})
            lex.append({"id": f"pie-lex-t{t}d{j}", "kind": "derivative", "form": f"d{t}{j}",
                        "meaning": [], "root_id": f"pie-root-t{t}r{j}"})
    lex.append({"id": "pie-suffix-x", "kind": "affix", "form": "-x", "meaning": [f"{word(1, 0)} suffix"]})
    return lex


def make_unit(c, k, book, ids):
    words = [(f"f{x}", f"l{x}", (x,)) for x in ids]
    return B.Unit(c, f"{c}{k}", f"{c} {k}", book, " ".join(w[0] for w in words), words,
                  frozenset(ids), "test licence", False)


def fixture_units():
    """Per corpus: for every theme a run of qualifying units (2-3 seed roots each) separated by
    filler units; Germanic has only 3 for odd themes (→ omitted)."""
    rng = random.Random(1)
    units = {}
    for c in ("rv", "hom", "non", "lat"):
        us, k = [], 0
        for t in range(1, 17):
            n = 3 if (c == "non" and t % 2) else 45
            for i in range(n):
                roots = [f"pie-root-t{t}r{j}" for j in range(3)]
                ids = rng.sample(roots, 2 if i % 3 else 3)
                us.append(make_unit(c, k, f"b{t}", ids))
                k += 1
                us.append(make_unit(c, k, f"b{t}", ["pie-root-filler"]))
                k += 1
        units[c] = us
    B.assign_pids(units)
    return units


def test_word_and_phrase_matching():
    assert B.word_matches("horses", "horse") and B.word_matches("killed", "kill")
    assert B.word_matches("burning", "burn") and B.word_matches("died", "die")
    assert not B.word_matches("cower", "cow") and not B.word_matches("horsefly", "horse")
    assert B.phrase_in(B.gloss_words("to give birth to"), "give birth")
    assert not B.phrase_in(B.gloss_words("to give, to birth"), "give birth")


def test_match_seeds_roots_affix_and_exclusion():
    lex = fixture_lexicon() + [{"id": "pie-lex-y", "kind": "word", "form": "y", "meaning": [f"{word(2, 0)} up"]}]
    themes = fixture_themes()
    themes[1] = (2, "t2", [word(2, 0)], [f"{word(2, 0)} up"])
    s = B.match_seeds(lex, themes)
    assert s[1]["roots"] == sorted(f"pie-root-t1r{j}" for j in range(3))
    assert all(x["id"] != "pie-suffix-x" for x in s[1]["seeds"])
    assert all(x["gloss"] and x["concept"] for x in s[1]["seeds"])
    assert [x["id"] for x in s[2]["seeds"]] == ["pie-root-t2r0"]      # the excluded sense does not match


def test_qualifying_dedup_and_select_block():
    units = fixture_units()
    roots = {f"pie-root-t1r{j}" for j in range(3)}
    q = B.qualifying(units, ["rv"], roots)
    assert q and all(s >= 2 for s, _, _ in q)
    # duplicates (same content lemmas) are kept once
    lemmas = [tuple(l for _, l, _ in units[c][i].words) for _, c, i in q]
    assert len(lemmas) == len(set(lemmas))
    blk = B.select_block(q, random.Random(0))
    assert len(blk) == min(len(q), B.TOP + B.EXTRA)
    idx = sorted(i for _, _, i in blk)
    assert all(b - a > 1 for a, b in zip(idx, idx[1:]))
    assert B.select_block(q[:4], random.Random(0)) is None


def test_select_block_top_then_random():
    cands = [(5 if i < 40 else 2, "rv", 2 * i) for i in range(100)]
    blk = B.select_block(cands, random.Random(3), top=30, extra=6)
    assert sum(1 for s, _, _ in blk if s == 5) >= 30 and len(blk) == 36


def build_fixture():
    return B.build(fixture_units(), {e["id"]: e for e in fixture_lexicon()}, fixture_lexicon(), seed=0,
                   themes=fixture_themes())


def test_build_decoys_assignment_and_blinding():
    res = build_fixture()
    key, packets = res["key"], res["packets"]
    assert len(packets) == 24 and sum(v["kind"] == "decoy" for v in key.values()) == 8
    used = []
    for pid, v in key.items():
        if v["kind"] == "decoy":
            assert len(set(v["themes"].values())) == len(v["themes"]) >= 2
            used += list(v["themes"].items())
        else:
            assert ("Germanic" in packets[pid]["branches"]) == (v["theme"] % 2 == 0)
    assert len(used) == len(set(used))
    readers = res["assignment"]["readers"]
    assert len(readers) == 8 and all(len(r["packets"]) == 3 for r in readers)
    assert sorted(res["assignment"]["order"]) == sorted(packets)
    for r in readers:
        kinds = {key[p]["kind"] for p in r["packets"]}
        assert kinds == {"real", "decoy"}
        th = [{key[p]["theme"]} if key[p]["kind"] == "real" else set(key[p]["themes"].values())
              for p in r["packets"]]
        assert all(not (th[i] & th[j]) for i in range(3) for j in range(i + 1, 3))
    for pid, p in packets.items():
        assert pid.startswith("P-") and len(pid) == 6
        assert set(p) == {"packet", "header", "format", "branches", "passage_ids", "blocks"}
        meta = json.dumps({k: v for k, v in p.items() if k != "blocks"})
        assert "theme" not in meta and "decoy" not in meta and "real" not in meta
        assert p["header"] == B.HEADER
        assert p["passage_ids"] == [x["id"] for bl in p["blocks"] for x in bl["passages"]]
        assert all(x["lines"][[l["role"] for l in x["lines"]].index("passage")]["words"]
                   for bl in p["blocks"] for x in bl["passages"])
        assert json.loads(B.dump_packet(p)) == p


def test_build_is_deterministic():
    a, b = build_fixture(), build_fixture()
    assert a["key"] == b["key"] and a["assignment"] == b["assignment"]
    assert json.dumps(a["packets"], sort_keys=True) == json.dumps(b["packets"], sort_keys=True)


def test_neighbours_stay_in_text():
    us = [make_unit("rv", 0, "a", ["x"]), make_unit("rv", 1, "b", ["x"]), make_unit("rv", 2, "b", ["x"])]
    assert B.neighbours(us, 1) == (None, us[2])
    assert B.neighbours(us, 0) == (None, None)
