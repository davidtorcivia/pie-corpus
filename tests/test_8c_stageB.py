"""Phase 8c Stage B builder (scripts/build_8c_stageB.py): windows, word-matched retrieval, bundles,
embedded decoys, slabs and blinding. Small invented units only; no corpus is loaded."""

import importlib.util
import json
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_8c_stageB", ROOT / "scripts" / "build_8c_stageB.py")
S = importlib.util.module_from_spec(_spec)
sys.modules["build_8c_stageB"] = S
_spec.loader.exec_module(S)
B = S.B

CORP = {"rv": "b", "hom": "b", "non": "b", "lat": "b"}
N_GROUPS = 240


def fixture_units(seed: int = 3) -> dict:
    """Four corpora in four branches, 240 root groups with skewed frequencies, 300 units each, plus
    planted cross-branch triples of rare roots."""
    rng = random.Random(seed)
    weights = [1 / (k + 1) for k in range(N_GROUPS)]
    pool = [f"pie-root-g{k:03d}" for k in range(N_GROUPS)]
    units = {}
    for ci, c in enumerate(CORP):
        us = []
        for k in range(300):
            book, n = k // 50, rng.randint(3, 7)
            ids = rng.choices(pool, weights, k=n)
            if k % 25 == 7:                      # planted parallel: the same three rare roots in every corpus
                ids[:3] = [pool[200 + k % 30], pool[210 + k % 30 // 2], pool[230 + k % 10]]
            words = [(f"w{c}{k}_{j}", f"l{x}", (x,)) for j, x in enumerate(ids)]
            locus = {"rv": f"RV {book + 1}.{k}.1a", "hom": f"Il. {book + 1}.{k}"}.get(c, f"{c} {book}.{k}")
            u = B.Unit(c, f"{c}{k}", locus, f"{c}-book{book}", " ".join(w[0] for w in words), words,
                       frozenset(ids), "test licence", False)
            us.append(u)
        units[c] = us
    B.assign_pids(units)
    return units


@pytest.fixture
def small(monkeypatch):
    monkeypatch.setattr(S, "SLAB_TARGET", 20_000)
    monkeypatch.setattr(S, "SLAB_MAX", 30_000)
    monkeypatch.setattr(S, "SLAB_FLUSH_AT_CORPUS", 10_000)
    monkeypatch.setattr(S, "ORDER", tuple(CORP))
    return fixture_units()


def run(units):
    return S.build(units, {}, None, procs=1, log=lambda *a: None)


def test_split_windows():
    assert S.split_windows(10, 16) == [10]
    assert S.split_windows(40, 16) == [14, 13, 13]
    assert sum(S.split_windows(33, 16)) == 33


def test_units_from_tokens_windows():
    from pie.formula_search import Token
    toks = [Token("lat", f"l{k}", f"f{k}", "Cato 1.1", {"line": "x", "book": "b"}, k % 4 != 3, "noun")
            for k in range(40)]
    us = S.units_from_tokens("lat", toks, "line", lambda t: "b", [t.surface for t in toks], {},
                             lambda t: ("lic", False), max_words=12)
    assert [len(u.words) for u in us] == [10, 10, 10]
    assert [u.locus for u in us] == ["Cato 1.1 (w1/3)", "Cato 1.1 (w2/3)", "Cato 1.1 (w3/3)"]
    assert " ".join(u.text for u in us) == " ".join(t.surface for t in toks)


def test_match_counts_an_ambiguous_word_once():
    w = lambda f, ids: (f, f, tuple(ids))
    units = {"rv": [B.Unit("rv", "a", "RV 1.1.1a", "h", "", [w("x", ["pie-root-a", "pie-root-b"])],
                           frozenset(), "", False)],
             "hom": [B.Unit("hom", "b", "Il. 1.1", "1", "", [w("y", ["pie-root-a", "pie-root-b"])],
                            frozenset(), "", False),
                     B.Unit("hom", "c", "Il. 1.2", "1", "", [w("y", ["pie-root-a"]), w("z", ["pie-root-b"])],
                            frozenset(), "", False)]}
    idx = S.Index(units, {}, n_common=0)
    assert len(idx.match(0, 1)[1]) == 1 and len(idx.match(0, 2)[1]) == 1
    assert idx.partners(0, top_k=6, min_shared=2) == []          # one word on the pivot side: never 2 roots


def test_build_invariants_and_determinism(small, tmp_path):
    res = run(small)
    res2 = run(fixture_units())
    assert json.dumps(res["slabs"], ensure_ascii=False) == json.dumps(res2["slabs"], ensure_ascii=False)
    assert res["key"] == res2["key"] and res["assignment"] == res2["assignment"]
    idx, bundles = res["idx"], res["bundles"]
    assert bundles
    for b in bundles:
        p = b["pivot"]
        assert any(g >= idx.n_common for g in S.bundle_shared(idx, b))
        if not b["merged"]:
            assert all(idx.branch[v] != idx.branch[p] for v in b["units"][1:])
            assert len(b["units"]) <= 1 + S.TOP_K
        assert len(b["units"]) <= S.MERGE_CAP
    # decoys: about a fifth, and no root overlap with the pivot beyond chance
    st = res["stats"]
    assert 0.12 <= st["decoy_share"] <= 0.25
    assert res["decoy"]
    for bi, rep in res["decoy"].items():
        p = bundles[bi]["pivot"]
        for real, d in rep.items():
            assert idx.ref[d][0] == idx.ref[real][0] and d not in bundles[bi]["units"]
            sh = set(idx.ugids[p]) & set(idx.ugids[d])
            assert len(sh) <= 1 and all(g < idx.n_common for g in sh)
    # slabs: several, bounded, neutral ids; every bundle in exactly one slab
    assert len(res["slabs"]) >= 2
    seen = []
    for sid, s in res["slabs"].items():
        assert sid.startswith("S-") and set(s) == {"slab", "header", "format", "bundles", "passages"}
        assert len(S.dump_slab(s)) / S.CHARS_PER_TOKEN <= S.SLAB_MAX or len(s["bundles"]) == 1
        ids = {p["id"] for p in s["passages"]}
        for b in s["bundles"]:
            assert b["bundle"].startswith("B-") and {b["pivot"], *b["partners"]} <= ids
            seen.append(b["bundle"])
        assert "kind" not in json.dumps(s["bundles"])
    assert len(seen) == len(set(seen)) == len(bundles)
    assert set(res["key"]["slabs"]) == set(res["slabs"])
    # writing: key at the given path, loci-only copies without daughter text
    key = tmp_path / "keys" / "k.json"
    S.write(res, out_dir=tmp_path / "out", key_path=key)
    assert json.loads(key.read_text("utf-8"))["slabs"]
    loci = sorted((tmp_path / "out" / "slabs-loci").glob("S-*.json"))
    assert len(loci) == len(res["slabs"])

    def keys_of(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k
                yield from keys_of(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys_of(v)

    for f in loci:
        d = json.loads(f.read_text("utf-8"))
        assert not {"text", "words", "form", "lemma", "etymon"} & set(keys_of(d))
    full = json.loads(next((tmp_path / "out" / "slabs").glob("S-*.json")).read_text("utf-8"))
    assert full["passages"][0]["lines"][0]["text"]


def test_frozen_floor_is_used(small):
    res = run(small)
    p = dict(res["params"])
    p["floor"] = 1e9
    res2 = S.build(small, {}, p, procs=1, log=lambda *a: None)
    assert res2["bundles"] == [] and res2["slabs"] == {}
