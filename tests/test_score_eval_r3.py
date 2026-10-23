"""Scoring helpers of scripts/score_eval_r3.py (Phase 8a confirmatory evaluation).
Synthetic items and rows only; no corpus is loaded."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

_spec = importlib.util.spec_from_file_location(
    "score_eval_r3", Path(__file__).resolve().parent.parent / "scripts" / "score_eval_r3.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def item(**kw):
    base = {"item_id": "x", "phrase_branches": [], "phrase_corpora_confirmed": [], "pairs_root": [], "pairs": [],
            "held_out_core": False, "verdict": "accepted"}
    return {**base, **kw}


def test_eligibility_rules():
    gi = item(phrase_branches=["Greek", "Indo-Iranian"])
    gii = item(phrase_branches=["Greek", "Indo-Iranian", "Italic"])
    it_toch = item(phrase_branches=["Italic", "Tocharian"])
    ii_celt = item(phrase_branches=["Celtic", "Indo-Iranian"])
    assert S.eligible(gi, "R2") and S.eligible(gi, "R3-c")
    assert not S.eligible(gi, "R3-a") and not S.eligible(gi, "R3-b")
    assert S.eligible(gii, "R3-a") and S.eligible(gii, "R3-b") and S.eligible(gii, "R3-c")
    assert not S.eligible(it_toch, "R3-b")            # no Tocharian corpus
    assert S.eligible(ii_celt, "R3-b") and not S.eligible(ii_celt, "R2")
    # Phrygian has no corpus: three listed branches, two covered
    assert not S.eligible(item(phrase_branches=["Celtic", "Italic", "Phrygian"]), "R3-a")
    assert S.eligible(item(branches=["Greek", "Indo-Iranian"]), "R2", "branches")


def test_corpus_confirmed_subset():
    x = item(phrase_branches=["Greek", "Indo-Iranian"], phrase_corpora_confirmed=["avesta", "glaux"])
    assert S.in_subset(x, "corpus_confirmed", "R2")
    y = item(phrase_branches=["Greek", "Indo-Iranian"], phrase_corpora_confirmed=["rv"])
    assert not S.in_subset(y, "corpus_confirmed", "R2")
    z = item(phrase_branches=["Germanic", "Greek", "Indo-Iranian"], phrase_corpora_confirmed=["rv", "homer", "oe"])
    assert S.in_subset(z, "corpus_confirmed", "R3-a")
    assert not S.in_subset(item(phrase_branches=["Germanic", "Greek", "Indo-Iranian"],
                                phrase_corpora_confirmed=["rv", "homer"]), "corpus_confirmed", "R3-a")
    assert S.in_subset(item(verdict="accepted"), "uncontested", "R2")
    assert not S.in_subset(item(verdict="contested"), "uncontested", "R2")
    assert S.in_subset(item(held_out_core=True), "held_out_core", "R2")


def test_hit_rule_min_over_pairs_root():
    idx = S.rank_index([["a", "b"], ["c", "d"], ["d", "e"], ["c", "d"]])
    assert idx == {("a", "b"): 1, ("c", "d"): 2, ("d", "e"): 3}
    assert S.item_rank(item(pairs_root=[["e", "d"], ["d", "c"]]), idx) == 2      # order-free, minimum
    assert S.item_rank(item(pairs_root=[["x", "y"]]), idx) is None
    assert S.item_rank(item(pairs_root=[]), idx) is None                         # unscoreable: a miss
    assert S.item_rank(item(pairs_root=[["a", "a"]]), {("a", "a"): 1}) is None    # self pair never counts
    b = S.recall_block([1, 60, 150, None])
    assert b["n"] == 4 and b["recall@50"] == 0.25 and b["recall@100"] == 0.5 and b["recall@200"] == 0.75
    assert b["hits"] == {"@50": 1, "@100": 2, "@200": 3}


def test_fold_twins_matches_candidate_loop():
    W = lambda corp: [SimpleNamespace(corpora=corp)]
    rows = [{"pair": ("l1", "l2"), "witnesses": W({"rv": 3, "hom": 1})},
            {"pair": ("l1", "l2b"), "witnesses": W({"rv": 3, "hom": 1})},   # twin of the first: folded
            {"pair": ("l3", "l4"), "witnesses": W({"rv": 3, "hom": 1})},    # same counts, not a twin: kept
            {"pair": ("l1", "l2c"), "witnesses": W({"rv": 9, "hom": 1})},   # same group pair as row 1: dropped
            {"pair": ("l5", "l5b"), "witnesses": W({"rv": 1, "hom": 1})}]   # one group: dropped
    groups = {"l1": "g1", "l2": "g2", "l2b": "g2b", "l2c": "g2", "l3": "g3", "l4": "g4", "l5": "g5", "l5b": "g5"}

    def project(p):
        a, b = groups[p[0]], groups[p[1]]
        return None if a == b else tuple(sorted((a, b)))

    def twins(p, q):
        return bool(set(p) & set(q))
    top, alts = S.fold_twins(rows, project, twins)
    assert [gp for _, gp in top] == [("g1", "g2"), ("g3", "g4")]
    assert alts[("g1", "g2")] == [("g1", "g2b")]
