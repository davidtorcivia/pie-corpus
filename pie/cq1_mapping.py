"""Corpus-quality fix batch 1 (waves 10-12 reader reports and the formula witness scan).

Verdicts: data/research/8c/corpus-quality/error-verdicts-cq1-<area>.jsonl; report
docs/research/8c-corpus-quality-batch1.md.

Three kinds of reviewed decision meet here, each applied once for every consumer
(search index, Stage C/C-S builders, packets, Tier 2 secure check):
  - exact word-coordinate readings, data/research/formulas/cq1-readings-<area>.json:
    [{"corpus", "locus", "surface", "old", "lemma", "report", "evidence"}]; keys are the
    loader's actual word coordinates, not review-window labels. A reviewed lemma ending in
    " (name)" or "@numeral", or a row with "noncontent": true, makes the word non-content;
  - general rules with exception lists, in the per-area modules pie/cq1_<area>.py
    (contextual_lemma / noncontent), called from pie.other_mapping.contextual_lemma and
    pie.formula_search.Token;
  - root-group splits, data/research/formulas/group-splits.json: a lexicon entry whose
    Wiktionary tree puts it under a root it does not continue (the "mountain" derivatives
    filed under *gʷerH- "praise") is given its own group by pie.formula_search.group_of.
"""
from __future__ import annotations

import importlib
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# batch 2 (cq2, docs/research/8c-corpus-quality-batch2.md) adds cq2-readings-<area>.json and pie/cq2_other.py
READINGS_GLOB = "data/research/formulas/cq[0-9]-readings-*.json"
GROUP_SPLITS = ROOT / "data/research/formulas/group-splits.json"
AREA_MODULES = ("cq1_xcl", "cq1_other", "cq1_formulas", "cq2_other")


@lru_cache(maxsize=1)
def reading_rows() -> tuple:
    rows = []
    for path in sorted(ROOT.glob(READINGS_GLOB)):
        rows += json.loads(path.read_text("utf-8"))
    return tuple(rows)


@lru_cache(maxsize=1)
def _readings() -> tuple[dict, frozenset]:
    rows = reading_rows()
    readings = {(r["corpus"], r["locus"], r["surface"], r["old"]): r["lemma"] for r in rows}
    noncontent = frozenset((r["corpus"], r["locus"], r["surface"], r["lemma"]) for r in rows
                           if r.get("noncontent") or r["lemma"].endswith((" (name)", "@numeral")))
    return readings, noncontent


@lru_cache(maxsize=1)
def _areas() -> tuple:
    return tuple(importlib.import_module(f"{__package__}.{m}") for m in AREA_MODULES)


def reviewed_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    """Exact readings first, then the area rules (each sees the lemma the previous step gave)."""
    lemma = _readings()[0].get((corpus, locus, surface, lemma), lemma)
    for mod in _areas():
        lemma = mod.contextual_lemma(corpus, lemma, surface, locus)
    return lemma


def noncontent(corpus: str, lemma: str, surface: str, locus: str) -> bool:
    if (corpus, locus, surface, lemma) in _readings()[1]:
        return True
    return any(mod.noncontent(corpus, lemma, surface, locus) for mod in _areas())


@lru_cache(maxsize=1)
def group_splits() -> dict:
    """lexicon entry id -> reviewed root group (only entries listed in group-splits.json)."""
    if not GROUP_SPLITS.exists():
        return {}
    data = json.loads(GROUP_SPLITS.read_text("utf-8"))
    return {i: g["group"] for g in data["groups"] for i in g["ids"]}
