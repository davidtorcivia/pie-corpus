"""Food-family mappings: Kroonen 2013 p. 358 (scan p0398), s.v. *mati-."""

import json
from pathlib import Path

import pytest

from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent
TARGET = "pie-root-med-become_full"
CASES = [
    ("ang", "met"), ("ang", "mete"), ("ang", "mete|met"),
    ("got", "mats"), ("got", "matjan"), ("got", "ga-matjan"),
    ("got", "miþ-matjan"), ("rea-osx", "meti"),
]


@pytest.mark.parametrize("corpus,lemma", CASES)
def test_food_overrides_replace_stale_roots_and_lexeme(corpus, lemma):
    stale = {lemma: ("pie-root-meh2d-be_wet", "pie-root-meh2d-meet", "pie-lex-mh2dyeti")}
    assert fm.apply_table_overrides(corpus, stale, root=ROOT)[lemma] == (TARGET,)
    overrides = json.loads((ROOT / "data/research/formulas/mapping-overrides/germanic.json").read_text())
    row, = [r for r in overrides["lemma"] if (r["corpus"], r["lemma"]) == (corpus, lemma)]
    assert "p. 358 (scan p0398)" in row["note"]


@pytest.mark.parametrize("corpus,lemma", CASES)
def test_food_table_matches_reviewed_override(corpus, lemma):
    rows = [json.loads(line) for line in
            (ROOT / f"data/research/formulas/mapping/{corpus}.jsonl").read_text().splitlines()]
    row, = [r for r in rows if r["lemma"] == lemma]
    assert row["lex_id"] == [TARGET]
    assert row["path"] == [f"{corpus}:{lemma}", f"erratum:remapped to {TARGET}"]
    assert row["how"] == "erratum"
    assert row["sources"] == ["mapping-overrides"]


def test_distinct_lapping_measuring_and_meeting_families_stay_separate():
    # *matjan- / ON metja: p. 358; *metan-: p. 367 (scan p0407).
    lapping = "pie-lex-mh2dyeti"
    assert fm.apply_table_overrides("non", {"metja|metta": (lapping,)}, root=ROOT)["metja|metta"] == (lapping,)
    rows = fm.apply_table_overrides("ang", {
        "gemet": ("pie-root-meh2d-be_wet",),
        "mētan": ("pie-root-meh2d-meet",),
    }, root=ROOT)
    assert rows["gemet"] == ("pie-root-med-measure",)
    assert rows["mētan"] == ("pie-root-meh2d-meet",)
