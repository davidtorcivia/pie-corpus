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


def test_doubtful_annotations_preserve_retrieval(small):
    import copy
    import json
    from pie import hittite_mapping as hm

    units, cls = small
    baseline = run(units, cls)
    annotated = copy.deepcopy(units)
    qualifications = {}
    hm.read_union_table(qualifications=qualifications)
    q = qualifications["arun=a-@Meer"]
    for u in annotated["hit"]:
        u.qualifications = {lem: q for _, lem, _ in u.words}
    result = run(annotated, cls)
    assert result["idx"].groups == baseline["idx"].groups
    assert result["idx"].ugids == baseline["idx"].ugids
    assert result["parts"] == baseline["parts"]
    assert result["bundles"] == baseline["bundles"]
    assert result["decoy"] == baseline["decoy"]
    p = SB.render(annotated, "hit", 1, {})
    assert len(p["lines"]) == 3  # context annotations retain the qualification too
    for line in p["lines"]:
        for word in line["words"]:
            assert all(e["qualification"] == q for e in word["etymon"])
    assert json.loads(json.dumps(p))["lines"] == p["lines"]


def test_hittite_paragraph_carries_doubtful_qualification(monkeypatch):
    from pie import formula_search as fs, formula_search_multi as fm, hittite_mapping as hm
    lemma = "arun=a-@Meer"
    qualifications = {}
    table = hm.read_union_table(qualifications=qualifications)
    tok = fs.Token("hit", lemma, "fixture", "fixture 1", {"line": "fixture|1", "para": "fixture|1"}, True, "noun")
    monkeypatch.setattr(fm, "load_hittite", lambda root: [tok])
    monkeypatch.setattr(B, "_hit_lines", lambda fm, root: ({}, ["fixture"]))
    monkeypatch.setattr(S, "hittite_paragraph_texts", lambda root: {})
    us = S.hittite_paragraph_units()
    assert us[0].words == [("fixture", lemma, table[lemma])]
    p = SB.render({"hit": us}, "hit", 0, {})
    assert p["lines"][0]["words"][0]["etymon"][0]["qualification"] == qualifications[lemma]

    # An old cached unit has no annotation metadata; prepare must refresh it without
    # rebuilding the corpus or changing the retrieval words and groups.
    words, groups = list(us[0].words), us[0].groups
    del us[0].qualifications
    monkeypatch.setattr(C, "_cached", lambda cache, name, fn: us)
    monkeypatch.setattr(S, "Classifier", lambda root, meta: None)
    monkeypatch.setattr(S, "classify", lambda units, clf: {"hit": [S.NARR]})
    monkeypatch.setattr(S, "thin_corpora", lambda idx: frozenset())
    units = {}
    S.prepare(units, {}, {}, log=lambda *a: None)
    assert units["hit"][0].words == words and units["hit"][0].groups == groups
    assert units["hit"][0].qualifications == {lemma: qualifications[lemma]}


def test_thin_corpora_rules(small, monkeypatch):
    units, cls = small
    monkeypatch.setattr(S, "THIN_MAX_UNITS", 260)        # the fixture's partner corpora have ~270 kept units each
    idx = S.SIndex(S.indexed_view(units, cls), {}, cls)
    cnt = {c: sum(1 for c2, _ in idx.ref if c2 == c) for c in ("rv", "hom", "hit")}
    monkeypatch.setattr(S, "THIN_MAX_UNITS", max(cnt.values()) + 1)
    thin = S.thin_corpora(idx)
    assert thin == {"rv", "hom", "hit"} and not thin & set(S.PIVOTS)
    for c in thin:                                       # genre waived for thin corpora
        cls[c] = [S.ALL if m else 0 for m in cls[c]]
    idx = S.SIndex(S.indexed_view(units, cls), {}, cls)
    idx.set_thin(thin)
    n = 0
    for u in C.pivots_of(idx, S.PIVOTS):
        tp = idx.thin_partners(u)
        assert len(tp) <= S.THIN_SLOTS and len({idx.corp[v] for _, v, _ in tp}) == len(tp)
        assert all(idx.corp[v] in thin and idx.branch[v] != idx.branch[u] for _, v, _ in tp)
        n += bool(tp)
    assert n
    reg, tparts = S.all_partners(idx, C.pivots_of(idx, S.PIVOTS), procs=1)
    kept = S.kept_partners(reg, tparts, floor=1e9, thin_floor=0.0)
    assert kept and all(idx.corp[v] in thin for ps in kept.values() for _, v, _ in ps)
    clf = S.Classifier(None)
    clf.cth = {"KUB 25.1": 627, "KUB 33.98": 345}
    U = lambda book: type("U", (), {"book": book, "key": "x"})()
    assert S.loose_class("hit", U("KUB 25.1"), clf) == S.ALL and S.loose_class("hit", U("KUB 33.98"), clf) == 0
    assert S.loose_class("ang", U("I:Genesis"), clf) == S.ALL and S.loose_class("ang", U("II:Psalmen"), clf) == 0
    assert S.loose_class("ang", U("II:Lxxxti,"), clf) == 0 and S.loose_class("ang", U("II:Juliana"), clf) == S.ALL
    assert S.loose_class("ang", U("I:Literarische Notizen"), clf) == 0
    assert S.loose_class("lat", U("PlAmphi"), clf) == S.ALL


def test_exclusion_inputs_use_only_loci(tmp_path):
    import json
    loci = tmp_path / 'slabs-loci'
    loci.mkdir()
    (loci / 'SS-1234.json').write_text(json.dumps({
        'slab': 'SS-1234', 'bundles': [{'bundle': 'BS-12345', 'pivot': 'mga:one'}]}))
    path = tmp_path / 'read.json'
    path.write_text(json.dumps(['SS-1234', 'mga:two', 'mga:one']))
    assert S.read_pivot_exclusions(path, loci) == {'mga:one', 'mga:two'}
    assert S.historical_ids(loci) == {'SS-1234', 'BS-12345'}
    for invalid in ({'ids': []}, [1], [''], ['SS-../secret'], ['bad-id']):
        path.write_text(json.dumps(invalid))
        with pytest.raises(ValueError):
            S.read_pivot_exclusions(path, loci)
    path.write_text('["SS-dead"]')
    with pytest.raises(FileNotFoundError):
        S.read_pivot_exclusions(path, loci)


def test_rebuild_requires_fresh_destinations(tmp_path):
    out, key = tmp_path / 'wave2', tmp_path / 'key.json'
    S.validate_rebuild_paths(out, key)
    for old_out, old_key in ((S.OUT, key), (S.OUT / 'nested', key),
                             (S.OUT.parent, key), (out, S.KEY)):
        with pytest.raises(ValueError):
            S.validate_rebuild_paths(old_out, old_key)
    out.mkdir()
    with pytest.raises(ValueError):
        S.validate_rebuild_paths(out, key)
    out.rmdir()
    key.write_text('historical sentinel')
    with pytest.raises(ValueError):
        S.validate_rebuild_paths(out, key)
    assert key.read_text() == 'historical sentinel'


def test_between_wave_cli_keeps_frozen_floors(small, monkeypatch, tmp_path):
    """Between-wave rebuilds reuse the frozen Stage C-S floors (pre-registration correction of 2026-10-25)."""
    import json
    import numpy as np
    units, cls = small
    thin = frozenset({'hit'})
    cls['hit'] = [S.ALL if m else 0 for m in cls['hit']]
    idx = S.SIndex(S.indexed_view(units, cls), {}, cls)
    idx.set_thin(thin)
    pivots = C.pivots_of(idx, S.PIVOTS)
    reg, tp = S.all_partners(idx, pivots, procs=1)
    # Exclude the highest-scoring half, so freezing before filtering would
    # produce different floors. The same indexed units remain partners.
    ordered = sorted(reg, key=lambda u: reg[u][0][0], reverse=True)
    removed = set(ordered[:len(ordered)//2])
    excluded = {units[idx.ref[u][0]][idx.ref[u][1]].pid for u in removed}
    path = tmp_path / 'read.json'
    path.write_text(json.dumps(sorted(excluded)))
    out, key = tmp_path / 'wave2', tmp_path / 'wave2-key.json'
    reserved = {'SS-1234', 'BS-12345'}
    monkeypatch.setattr(S, 'historical_ids', lambda: reserved)
    monkeypatch.setattr(C, 'load_all', lambda *a: (units, {}, {}, {}))
    monkeypatch.setattr(S, 'prepare', lambda *a: (cls, thin))
    frozen = S.make_params(idx, reg, None, thin_parts=tp)
    fpath = tmp_path / 'frozen.json'
    fpath.write_text(json.dumps(frozen))
    # without the frozen floors an exclusion rebuild is refused
    monkeypatch.setattr(sys, 'argv', ['build', '--exclude-read-pivots', str(path),
                        '--out-dir', str(out), '--key', str(key), '--reader-start', '13', '--procs', '1'])
    with pytest.raises(SystemExit):
        S.main()
    monkeypatch.setattr(sys, 'argv', ['build', '--exclude-read-pivots', str(path), '--frozen-params', str(fpath),
                        '--out-dir', str(out), '--key', str(key), '--reader-start', '13', '--procs', '1'])
    assert S.main() == 0
    params = json.loads((out / 'params.json').read_text())
    remaining_reg = {u:p for u,p in reg.items() if u not in removed}
    assert params['floor'] == frozen['floor'] and params['thin_floor'] == frozen['thin_floor']
    assert params['excluded_read_pivots'] == sorted(excluded)
    result = S.build(units, {}, cls, params, procs=1, log=lambda *a:None,
                     parts=(reg, tp), thin=thin, excluded=excluded, reader_start=13)
    assert result['idx'].ref == idx.ref
    assert result['idx'].idf.tolist() == idx.idf.tolist()
    assert all(b['pivot'] not in removed for b in result['bundles'])
    # read pivots stay indexed and can still be retrieved as partners (before the floor is applied)
    assert any(v in removed for ps in result['parts'].values() for _, v, _ in ps)
    assert len(result['parts']) == len(remaining_reg)
    assignment = json.loads((out / 'assignment.json').read_text())['slabs']
    assert list(assignment.values()) == [f'RS{k+13:03d}' for k in range(len(assignment))]
    assert not set(assignment) & reserved
    for slab in json.loads(key.read_text())['slabs'].values():
        assert not set(slab) & reserved
        assert all(b['pivot'] not in excluded for b in slab.values())
    # A rerun refuses to touch the completed wave, before loading anything.
    monkeypatch.setattr(C, 'load_all', lambda *a: pytest.fail('loaded before validation'))
    before = key.read_bytes()
    with pytest.raises(SystemExit):
        S.main()
    assert key.read_bytes() == before


def test_new_ids_skip_old_series():
    baseline = S.fresh_ids('SS', 4, 3, random.Random(7), set())
    new = S.fresh_ids('SS', 4, 3, random.Random(7), set(baseline))
    assert len(set(new)) == 3 and not set(new) & set(baseline)


def test_historical_ids_cover_every_wave(tmp_path, monkeypatch):
    import json
    base = tmp_path / "stageCS"
    for d, sid, bid in ((base, "SS-0001", "BS-00001"), (tmp_path / "stageCS-w2", "SS-0002", "BS-00002")):
        (d / "slabs-loci").mkdir(parents=True)
        (d / "slabs-loci" / f"{sid}.json").write_text(json.dumps({"slab": sid, "bundles": [{"bundle": bid}]}))
    monkeypatch.setattr(S, "OUT", base)
    assert S.historical_ids() == {"SS-0001", "BS-00001", "SS-0002", "BS-00002"}
