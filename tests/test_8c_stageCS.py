"""Phase 8c Stage C-S builder (scripts/build_8c_stageCS.py): the layer and genre table, partners sharing a
class with their pivot, the per-corpus cap, left-out units never indexed, decoys from the same corpus and a
shared class. Small invented units only; no corpus is loaded."""

import importlib.util
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_8c_stageCS", ROOT / "scripts" / "build_8c_stageCS.py")
S = importlib.util.module_from_spec(_spec)
sys.modules["build_8c_stageCS"] = S
_spec.loader.exec_module(S)
C, SB, B = S.C, S.SB, S.B

CORPORA = ("mga", "menota", "rv", "hom", "hit")
N_GROUPS = 240
MASKS = (S.NARR, S.CULT, S.NARR | S.LAW, S.LYR)


def fixture(seed: int = 5):
    rng = random.Random(seed)
    weights = [1 / (k + 1) for k in range(N_GROUPS)]
    pool = [f"pie-root-g{k:03d}" for k in range(N_GROUPS)]
    units, cls = {}, {}
    for c in CORPORA:
        us, ms = [], []
        for k in range(300):
            ids = rng.choices(pool, weights, k=rng.randint(3, 7))
            if k % 25 == 7:                  # planted parallel in every corpus
                ids[:3] = [pool[200 + k % 30], pool[210 + k % 30 // 2], pool[230 + k % 10]]
            words = [(f"w{c}{k}_{j}", f"l{x}", (x,)) for j, x in enumerate(ids)]
            u = B.Unit(c, f"{c}{k}", f"{c} {k // 50}.{k}", f"{c}-book{k // 50}", " ".join(w[0] for w in words),
                       words, frozenset(ids), "licence cc-by", False)
            u.tag = "cc-by"
            us.append(u)
            ms.append(0 if k % 10 == 9 else MASKS[k % len(MASKS)])
        units[c], cls[c] = us, ms
    B.assign_pids(units)
    return units, cls


@pytest.fixture
def small(monkeypatch):
    monkeypatch.setattr(SB, "SLAB_TARGET", 20_000)
    monkeypatch.setattr(SB, "SLAB_MAX", 30_000)
    monkeypatch.setattr(SB, "SLAB_FLUSH_AT_CORPUS", 10_000)
    monkeypatch.setattr(S, "PIVOTS", ("mga", "menota"))
    return fixture()


def run(units, cls, seed=0):
    view = S.indexed_view(units, cls)
    idx = S.SIndex(view, {}, cls)
    parts = C.pivot_partners(idx, C.pivots_of(idx, S.PIVOTS), procs=1)
    params = S.make_params(idx, parts, None)
    return S.build(units, {}, cls, params, procs=1, log=lambda *a: None, seed=seed)


def test_partners_share_a_class_and_respect_the_cap(small):
    units, cls = small
    idx = S.SIndex(S.indexed_view(units, cls), {}, cls)
    n = 0
    for u in C.pivots_of(idx, S.PIVOTS):
        ps = idx.partners(u)
        per = {}
        for _, v, _ in ps:
            assert idx.cls[v] & idx.cls[u]
            assert idx.branch[v] != idx.branch[u]
            per[idx.corp[v]] = per.get(idx.corp[v], 0) + 1
        assert all(k <= S.CORPUS_CAP for k in per.values())
        n += bool(ps)
    assert n


def test_left_out_units_are_not_indexed(small):
    units, cls = small
    idx = S.SIndex(S.indexed_view(units, cls), {}, cls)
    assert all(cls[c][i] for c, i in idx.ref)
    assert len(idx.ref) < sum(len(us) for us in units.values())


def test_build_bundles_decoys_and_key(small):
    units, cls = small
    res = run(units, cls)
    idx, bundles, decoy = res["idx"], res["bundles"], res["decoy"]
    assert bundles and decoy
    for b in bundles:
        assert idx.ref[b["pivot"]][0] in S.PIVOTS
        assert all(idx.cls[v] & idx.cls[b["pivot"]] for v in b["units"][1:])
    assert any(b["merged"] for b in bundles)         # the class rule holds in merged bundles too
    for bi, rep in decoy.items():
        p = bundles[bi]["pivot"]
        for real, d in rep.items():
            assert idx.ref[d][0] == idx.ref[real][0] and idx.cls[d] & idx.cls[p]
            sh = set(idx.ugids[p]) & set(idx.ugids[d])
            assert len(sh) <= 1 and all(g < idx.n_common for g in sh)
    ents = [e for s in res["key"]["slabs"].values() for e in s.values()]
    assert all(e["pivot_classes"] and all(r["classes"] for r in e["real_partners"]) for e in ents)
    assert all(sid.startswith("SS-") for sid in res["slabs"])
    assert all(b["bundle"].startswith("BS-") for s in res["slabs"].values() for b in s["bundles"])
    assert set(res["assignment"]["slabs"].values()) == {f"RS{k + 1:03d}" for k in range(len(res["slabs"]))}
    a, b2 = run(*fixture()), res
    assert a["key"] == b2["key"]


def test_layer_table():
    clf = S.Classifier(None, meta={
        "G1:1": {"date_from": 800, "date_to": 900, "genre": "saga"},
        "G1:2": {"date_from": 1400, "date_to": 1500, "genre": "saga"},
        "G1:3": {"date_from": 800, "date_to": 900, "genre": "religious"},
        "G1:4": {"date_from": 1000, "date_to": 1100, "genre": "verse"}})
    clf.glaux = {"0016-001": {"ENDDATE": "-420", "GENRE_STANDARD": "History"},
                 "0627-006": {"ENDDATE": "-350", "GENRE_STANDARD": "Medicine"},
                 "0020-002": {"ENDDATE": "-650", "GENRE_STANDARD": "Epic poetry"}}
    clf.cth = {"KBo 3.7": 321, "KUB 33.98": 345, "KUB 13.4": 264, "KBo 6.2": 291, "KUB 25.1": 627}
    U = lambda book, key="x": type("U", (), {"book": book, "key": key})()
    assert clf("mga", U("G1", "G1:1")) == S.NARR
    assert clf("mga", U("G1", "G1:2")) == 0 and clf("mga", U("G1", "G1:3")) == 0
    assert clf("cy", U("G1", "G1:4")) == S.CULT | S.LYR | S.NARR
    assert clf("menota", U("NRA-norrfragm-7")) == S.LAW
    assert clf("menota", U("NRA-norrfragm-77")) == 0             # Gregory's Dialogues, not the law fragment
    assert clf("menota", U("AM-132-fol-Njals-saga")) == S.NARR and clf("menota", U("AM-619-4to")) == 0
    assert clf("grc", U("0016-001")) == S.NARR and clf("grc", U("0627-006")) == 0
    assert clf("grc", U("0020-002")) == S.NARR | S.WISDOM
    assert clf("grc-late", U("0016-001")) == 0
    assert clf("hit", U("KBo 3.7")) == S.NARR | S.CULT and clf("hit", U("KUB 33.98")) == 0
    assert clf("hit", U("KUB 13.4")) == S.LAW | S.WISDOM and clf("hit", U("KBo 6.2")) == S.LAW
    assert clf("hit", U("KUB 25.1")) == 0                          # festival description
    assert clf("non", U("Sólarljóð")) == 0 and clf("non", U("Völuspá")) == S.NARR | S.WISDOM
    assert clf("ang", U("Beo.")) == S.NARR and clf("ang", U("I:Genesis")) == 0
    assert clf("rea-goh", U("Kleinere_Althochdeutsche_Denkmäler/MZ_MerseburgerZaubersprueche")) == S.CULT
    assert clf("rea-goh", U("Otfrid/O_Otfr.Ev.1.1")) == 0
    assert clf("lat", U("PlAmphi")) == 0 and clf("lat", U("CatAgr")) == S.CULT
    assert clf("xto", U("993.359")) == 0 and clf("sqo", U("buzuku")) == 0
    assert clf("sa-ep", U("MBh, 12, 136")) == S.WISDOM | S.LAW and clf("sa-ep", U("MBh, 1, 2")) == S.NARR
