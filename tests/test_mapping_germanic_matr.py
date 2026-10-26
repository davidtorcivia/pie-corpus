"""ON matr: Kroonen 2013 p. 358 (scan p0398), s.v. *mati-."""

import json
from pathlib import Path

from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent
TARGET = "pie-root-med-become_full"


def test_matr_replaces_both_meh2d_homonyms():
    stale = {"matr": ("pie-root-meh2d-be_wet", "pie-root-meh2d-meet")}
    assert fm.apply_table_overrides("non", stale, root=ROOT)["matr"] == (TARGET,)
    lexicon = [json.loads(line) for line in (ROOT / "data/lexicon/lexicon.jsonl").read_text().splitlines()]
    target = next(row for row in lexicon if row["id"] == TARGET)
    assert target["form"] == "med-"
    assert "to become full, become sated" in target["meaning"]


def test_matr_regenerated_table_has_reviewed_target_and_path():
    rows = [json.loads(line) for line in
            (ROOT / "data/research/formulas/mapping/non.jsonl").read_text().splitlines()]
    row, = [row for row in rows if row["lemma"] == "matr"]
    assert row["lex_id"] == [TARGET]
    assert row["path"] == ["non:matr", f"erratum:remapped to {TARGET}"]
    assert row["how"] == "erratum"
