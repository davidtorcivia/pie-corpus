"""Phase 8c Stage C builder (scripts/build_8c_stageC.py): pivots from the Stage C corpora only, decoy share,
licence tags carried into slabs and loci copies, decoy partners without beyond-chance root overlap, and
determinism under a fixed seed. Small invented units only; no corpus is loaded."""

import importlib.util
import json
import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_8c_stageC", ROOT / "scripts" / "build_8c_stageC.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["build_8c_stageC"] = C
_spec.loader.exec_module(C)
SB, B = C.SB, C.B

# two pivot corpora (Celtic, Germanic) and three partner-only corpora in other branches
TAGS = {"mga": ("consent-train", "research"), "menota": ("cc-by-sa",), "rv": ("cc-by",), "hom": ("cc-by-sa",),
        "xto": ("nc",)}
PIVOTS = ("mga", "menota")
N_GROUPS = 240


def fixture_units(seed: int = 3) -> dict:
    rng = random.Random(seed)
    weights = [1 / (k + 1) for k in range(N_GROUPS)]
    pool = [f"pie-root-g{k:03d}" for k in range(N_GROUPS)]
    units = {}
    for c, tags in TAGS.items():
        us = []
        for k in range(300):
            book, n = k // 50, rng.randint(3, 7)
            ids = rng.choices(pool, weights, k=n)
            if k % 25 == 7:                      # planted parallel: the same three rare roots in every corpus
                ids[:3] = [pool[200 + k % 30], pool[210 + k % 30 // 2], pool[230 + k % 10]]
            words = [(f"w{c}{k}_{j}", f"l{x}", (x,)) for j, x in enumerate(ids)]
            tag = tags[k % len(tags)]
            lic, ro = (C.CELTIC_LICENCE[tag] if c in C.CELTIC else (f"licence {tag}", tag in C.RESEARCH_TAGS))
            u = B.Unit(c, f"{c}{k}", f"{c} {book}.{k}", f"{c}-book{book}", " ".join(w[0] for w in words), words,
                       frozenset(ids), lic, ro)
            u.tag = tag
            us.append(u)
        units[c] = us
    B.assign_pids(units)
    return units


@pytest.fixture
def small(monkeypatch):
    monkeypatch.setattr(SB, "SLAB_TARGET", 20_000)
    monkeypatch.setattr(SB, "SLAB_MAX", 30_000)
    monkeypatch.setattr(SB, "SLAB_FLUSH_AT_CORPUS", 10_000)
    return fixture_units()


def run(units, seed=0):
    return C.build(units, {}, None, procs=1, log=lambda *a: None, pivot_corpora=PIVOTS, seed=seed)


def test_licence_tag():
    assert C.licence_tag("CC BY-NC-SA 3.0 (ReA): non-commercial") == "nc"
    assert C.licence_tag("CC BY-SA 4.0 (Menota)") == "cc-by-sa"
    assert C.licence_tag("CC BY 4.0 (DCS)") == "cc-by"
    assert C.licence_tag("Public domain") == "pd"
    assert C.licence_tag("CC BY 4.0 (VedaWeb Zurich annotation; the NC text layers are not used)") == "cc-by"
    assert C.licence_tag("LASLA: non-commercial") == "nc"
    assert C.licence_tag("GLAUx; source text licence: CC BY-NC-ND 4.0") == "nc"
    assert C.licence_tag("GLAUx; source text licence: NA") == "unchecked"
    for t in C.CELTIC_LICENCE:
        assert C.licence_tag(t) == t
    assert C.CELTIC_LICENCE["research"][1] and C.CELTIC_LICENCE["nc"][1] and not C.CELTIC_LICENCE["consent-train"][1]


def test_load_celtic_uses_celt_licence_rule(monkeypatch, tmp_path):
    from pie import celtic_mapping as cm

    cases = [
        ("celt-ucc/G400001", "consent-train", "research"),
        ("celt-ucc/G400058", "research", "research"),
        ("celt-ucc/G400065", "research", "consent-train"),
        ("celt-ucc/G400090", "research", "consent-train"),
        ("celt-ucc/G100055", "nc", "consent-train"),
        ("celt-ucc/G301035", "consent-train", "consent-train"),
        ("invented/G400001", "consent-train", "consent-train"),
        ("invented/G400065", "research", "research"),
        ("invented/edition", "nc", "nc"),
    ]
    rows = [{"id": f"invented{i}:1", "source": source, "licence": tag,
             "text": "invented", "kind": "l", "lang": "mga", "genre": "verse",
             "date_from": 1200, "date_to": 1300}
            for i, (source, tag, _) in enumerate(cases)]
    monkeypatch.setattr(C, "celtic_rows", lambda *args: rows)
    monkeypatch.setattr(cm, "build_mappings", lambda *args, **kwargs: SimpleNamespace(irish={}, welsh={}))
    monkeypatch.setattr(cm, "irish_lemmatizer", lambda *args, **kwargs: SimpleNamespace(level={}))
    monkeypatch.setattr(cm, "welsh_lemmatizer", lambda *args, **kwargs: None)
    monkeypatch.setattr(cm, "read_table", lambda *args: {})
    monkeypatch.setattr(cm, "gloss_tokens", lambda *args: [])
    monkeypatch.setattr(cm, "irish_words", lambda text: text.split())
    monkeypatch.setattr(cm, "lemmatize_words", lambda lz, words: words)
    monkeypatch.setattr(cm, "content_of", lambda *args: True)

    units, meta, notes = C.load_celtic(tmp_path, [], log=lambda *args: None)

    by_id = {u.key: u for u in units["mga"]}
    assert len(by_id) == len(rows)
    for row, (_, original, expected) in zip(rows, cases):
        unit = by_id[row["id"]]
        assert unit.tag == expected
        assert (unit.licence, unit.research_only) == C.CELTIC_LICENCE[expected]
        assert meta[row["id"]]["licence"] == expected
        assert row["licence"] == original
    assert notes["celt_research_tag_mismatch"] == 4


def test_celtic_unit_helpers():
    wb = {"id": "wb:1a:1", "kind": "gloss", "lang": "sga", "ref": "Wb. 1a1 (Thes. Pal. I p. 499)", "source": "x"}
    sg = {"id": "sg:2b3:21", "kind": "gloss", "lang": "sga", "ref": "Sg. 2b3", "source": "y"}
    assert C.gloss_unit_key(wb) == "Wb 1a1" and C.gloss_unit_key(sg) == "sg 21"
    assert C.celtic_corpus(wb) == "sga-gl" and C.celtic_book(wb) == "wb:1a" and C.celtic_book(sg) == "sg:2b"
    celt = {"id": "G301035:#1/x:3", "kind": "l", "lang": "mga", "source": "celt-ucc/G301035"}
    assert C.celtic_corpus(celt) == "mga" and C.celtic_book(celt) == "G301035"
    assert C.celtic_corpus({**celt, "lang": "owl"}) == "cy" and C.celtic_corpus({**celt, "lang": "ga-early"}) == "ga-early"


def test_pivots_decoys_and_tags(small, tmp_path):
    res = run(small)
    idx, bundles, decoy = res["idx"], res["bundles"], res["decoy"]
    assert bundles
    for b in bundles:
        assert idx.ref[b["pivot"]][0] in PIVOTS
        assert any(g >= idx.n_common for g in SB.bundle_shared(idx, b))
        if not b["merged"]:
            assert all(idx.branch[v] != idx.branch[b["pivot"]] for v in b["units"][1:])
    # decoy share: one bundle in every block of five
    st = res["stats"]
    assert 0.12 <= st["decoy_share"] <= 0.25 and decoy
    assert st["decoy_bundles"] + st["real_bundles"] == st["bundles"] == len(bundles)
    g = st["pivot_groups"]
    assert g["celtic"]["bundles"] + g["other"]["bundles"] == len(bundles)
    assert g["celtic"]["decoys"] + g["other"]["decoys"] == len(decoy)
    # no decoy partner shares a non-common root group with its pivot (and at most one root in all)
    for bi, rep in decoy.items():
        p = bundles[bi]["pivot"]
        for real, d in rep.items():
            assert idx.ref[d][0] == idx.ref[real][0] and d not in bundles[bi]["units"]
            sh = set(idx.ugids[p]) & set(idx.ugids[d])
            assert len(sh) <= 1 and all(gid < idx.n_common for gid in sh)
    # the key agrees: decoy partners listed for decoy bundles only, pivot group recorded
    kinds = [e for s in res["key"]["slabs"].values() for e in s.values()]
    assert sum(e["kind"] == "decoy" for e in kinds) == len(decoy)
    assert all(("decoy_partners" in e) == (e["kind"] == "decoy") for e in kinds)
    assert all(e["pivot_group"] == ("celtic" if e["pivot_corpus"] == "mga" else "other") for e in kinds)
    # licence tags: every passage carries its unit's tag; slabs count them; loci copies keep them
    tag_of = {u.pid: u.tag for us in small.values() for u in us}
    ro_of = {u.pid: u.research_only for us in small.values() for u in us}
    for sid, s in res["slabs"].items():
        assert sid.startswith("SC-")
        assert all(b["bundle"].startswith("BC-") for b in s["bundles"])
        assert "kind" not in json.dumps(s["bundles"])
        for p in s["passages"]:
            assert p["licence_tag"] == tag_of[p["id"]] and p["research_only"] == ro_of[p["id"]]
        cnt = {}
        for p in s["passages"]:
            cnt[p["licence_tag"]] = cnt.get(p["licence_tag"], 0) + 1
        assert s["licence_tags"] == dict(sorted(cnt.items()))
        assert s["research_only_passages"] == sum(p["research_only"] for p in s["passages"])
    assert {"research", "nc", "consent-train"} <= {p["licence_tag"] for s in res["slabs"].values()
                                                    for p in s["passages"]}
    key = tmp_path / "keys" / "k.json"
    C.write(res, out_dir=tmp_path / "out", key_path=key)
    assert json.loads(key.read_text("utf-8"))["slabs"]
    for f in (tmp_path / "out" / "slabs-loci").glob("SC-*.json"):
        d = json.loads(f.read_text("utf-8"))
        assert all("licence_tag" in p and "lines" in p and all("text" not in ln for ln in p["lines"])
                   for p in d["passages"])
        assert "words" not in f.read_text("utf-8")
    full = sorted((tmp_path / "out" / "slabs").glob("SC-*.json"))
    assert len(full) == len(res["slabs"]) and json.loads(full[0].read_text("utf-8"))["licence_tags"]


def test_determinism_under_fixed_seed(small):
    a, b = run(small), run(fixture_units())
    assert json.dumps(a["slabs"], ensure_ascii=False) == json.dumps(b["slabs"], ensure_ascii=False)
    assert a["key"] == b["key"] and a["assignment"] == b["assignment"]
    assert a["stats"]["decoy_bundles"] == b["stats"]["decoy_bundles"]
    c = run(fixture_units(), seed=1)
    assert set(c["slabs"]) != set(a["slabs"]) or c["key"] != a["key"]


def test_frozen_floor_is_used(small):
    res = run(small)
    p = dict(res["params"])
    p["floor"] = 1e9
    res2 = C.build(small, {}, p, procs=1, log=lambda *a: None, pivot_corpora=PIVOTS)
    assert res2["bundles"] == [] and res2["slabs"] == {}


def test_low_mapped_units_stay_pivots():
    w = lambda f, ids: (f, f, tuple(ids))
    unmapped = [w(f"x{k}", []) for k in range(8)]
    rare = ["pie-root-r1", "pie-root-r2"]
    units = {"mga": [B.Unit("mga", "a", "mga 1", "b", "", [w("p", [rare[0]]), w("q", [rare[1]])] + unmapped,
                            frozenset(), "", False)],
             "rv": [B.Unit("rv", "b", "RV 1.1.1a", "h", "", [w("y", [rare[0]]), w("z", [rare[1]])],
                           frozenset(), "", False)]}
    B.assign_pids(units)
    assert C.mapped_share(units["mga"][0]) < C.LOW_MAPPED
    idx = SB.Index(units, {}, n_common=0)
    assert C.pivots_of(idx, ("mga",)) == [0]
    parts = C.pivot_partners(idx, [0], procs=1)
    assert parts[0][0][1] == 1                     # its partner, found through its two mapped words
