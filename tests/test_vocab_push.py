"""Vocabulary push (docs/audits/vocab-push.md): shape-rule fixes, checked overrides for requested and everyday
words, reflex-confirmed glosses and evidence-sourced accents. Each is tested on the production path: the built
specs (data/morph/inflection_specs.jsonl), Lexicon.cells, check_plan + realize, and make_slice's pool."""

import json
import runpy
from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    Lexicon.load.cache_clear()
    return Lexicon.load()


@pytest.fixture(scope="module")
def pool(lx):
    return set(runpy.run_path(str(ROOT / "scripts/make_slice.py"))["offered"](lx))


def _report():
    return json.loads((ROOT / "data/morph/classify_report.json").read_text("utf-8"))


# 1. shape rules ---------------------------------------------------------------------------------------------------

def test_devi_o_grade_and_lengthened_roots_keep_their_grade():
    from pie.classify import by_shape
    # Ved. pátnī, gen. pátnyāḥ; rā́jñī, rā́jñyāḥ (the Wiktionary tables pótn̥yeh₂-, h₃rḗǵn̥yeh₂-)
    assert by_shape({"form": "pótnih₂", "pos": "noun"}).spec.weak == "pótn̥yeh₂"
    assert by_shape({"form": "h₃rḗǵnih₂", "pos": "noun"}).spec.weak == "h₃rḗǵn̥yeh₂"
    assert by_shape({"form": "déywih₂", "pos": "noun"}).spec.weak == "diwyéh₂"
    bt = _report()["backtest"]["shape:devi"]
    assert bt["cells_ok"] == 66 and bt["cells"] == 76 and bt["cell_accuracy"] >= 0.85


def test_devi_without_an_accent_gets_no_paradigm(lx):
    """An unaccented devī headword gets no spec: any paradigm would guess the oblique accent."""
    assert lx.specs["pie-lex-skjeh3ih2"]["rule"] == "unknown:devi-no-accent"
    assert not lx.specs["pie-lex-skjeh3ih2"]["usable"]


def test_devi_noun_realizes(lx):
    c = lx.cells("pie-lex-smorih2")
    assert (c["NOM.SG"][0], c["GEN.SG"][0]) == ("smórih₂", "smóryeh₂s")
    r = produce({"english": "x", "clauses": [{"slots": [
        {"lex_id": "pie-lex-h2ekjih2", "role": "SUBJ"},
        {"lex_id": "pie-lex-h1esti", "role": "V", "verb": {"tense": "PRS", "mood": "IND", "voice": "ACT"}}]}]}, lx)
    assert r["pie"].startswith("h₂éḱih₂ ")


def test_pronoun_sih2_is_not_a_devi_noun(lx):
    assert lx.specs["pie-lex-sih2"]["rule"] == "unknown:pronoun" and not lx.specs["pie-lex-sih2"]["usable"]


def test_hysterokinetic_n_stem_locative_is_e_grade():
    from pie.classify import by_shape
    sp = by_shape({"form": "ḱwṓ", "pos": "noun"}).spec
    assert sp.loc_sg == ["ḱwén", "ḱwéni"]
    bt = _report()["backtest"]["shape:n-stem-hk"]
    assert (bt["cells_ok"], bt["cells"]) == (29, 38)          # still below 0.85: not usable


def test_hk_iu_backtest_skips_tables_on_another_headword():
    bt = _report()["backtest"]["shape:hk-iu-stem"]
    assert (bt["cells_ok"], bt["cells"]) == (33, 57)          # Hrugʰís, bʰeh₂ǵʰús skipped; still not usable
