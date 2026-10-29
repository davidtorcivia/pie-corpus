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


# 2. requested and everyday words (data/lexicon/overrides.jsonl, "vocab push") -------------------------------------

REQUESTED = {   # keyword -> lexeme, each offered by default with a dictionary (override) gloss
    "roof": "pie-lex-stegos", "bed": "pie-lex-leghos", "wait": "pie-lex-meneti", "owe": "pie-lex-dhlgheti",
    "swear": "pie-lex-h3mneh3ti", "hornet": "pie-lex-kjrh2sexr", "suckle": "pie-lex-dheh1yeti",
    "sweat": "pie-lex-sweydos", "wash": "pie-lex-lewh3eti", "lick": "pie-lex-leygjheti", "fortress": "pie-lex-tpolHis",
    "womb": "pie-lex-gwelbhus", "elk": "pie-lex-h1olkjis", "grief": "pie-lex-kjeh2dos", "wipe": "pie-lex-wrseti",
    "beech": "pie-lex-bheh2gjos", "tooth": "pie-lex-h3donts",
}


@pytest.mark.parametrize("kw,lid", sorted(REQUESTED.items()))
def test_requested_word_is_offered(lx, pool, kw, lid):
    assert lid in pool
    assert lx.meaning(lid)[1] in ("override", "wiktionary")      # a dictionary gloss, not a derived one
    ms = runpy.run_path(str(ROOT / "scripts/make_slice.py"))
    assert ms["keyword_hit"](lx, lid, [kw])


def test_tooth_has_the_checked_hysterokinetic_paradigm(lx):
    c = lx.cells("pie-lex-h3donts")
    assert (c["NOM.SG"][0], c["ACC.SG"][0], c["GEN.SG"][0]) == ("h₃dónts", "h₃dóntm̥", "h₃dn̥tés")   # Ved. datás
    r = produce({"english": "x", "clauses": [{"slots": [
        {"lex_id": "pie-lex-h3donts", "role": "OBJ"},
        {"lex_id": "pie-lex-bhereti", "role": "V", "verb": {"tense": "PRS", "mood": "IND", "voice": "ACT"}}]}]}, lx)
    assert r["pie"] == "h₃dóntm̥ bʰéreti."


def test_beech_takes_the_printed_accent(lx):
    c = lx.cells("pie-lex-bheh2gjos")
    assert c["NOM.SG"][0] == "bʰeh₂ǵós" and lx.gender("pie-lex-bheh2gjos") == "f"
    assert lx.accent_status("pie-lex-bheh2gjos") == "resolved"


def test_unsourced_accents_stay_unresolved(lx, pool):
    """debt, grey, yew: glossed now, but no source gives an accent, so they stay out of the pool."""
    for lid in ("pie-lex-dhlghos", "pie-lex-polHwos", "pie-lex-h1eyHwos"):
        assert lx.meaning(lid)[1] == "override" and lid not in pool
        assert lx.accent_status(lid) == "unresolved"


# 3. reflex-confirmed glosses (docs/lexicon.md) ----------------------------------------------------------------------

def _confirmed():
    return [json.loads(x) for x in (ROOT / "data/lexicon/confirmed_glosses.jsonl").read_text("utf-8").splitlines()]


def test_confirmed_glosses_reach_the_default_pool(lx, pool):
    assert lx.meaning("pie-lex-lokus") == ("lake", "reflex-confirmed")
    assert "pie-lex-lokus" in pool
    assert lx.meaning("pie-lex-bhendheti") == ("to bind", "reflex-confirmed")


def test_confirmed_glosses_rest_on_two_branches_of_the_lexemes_own_reflexes(lx):
    from pie.glosses import branch
    for c in _confirmed():
        e = lx.entries[c["id"]]
        assert e.get("meaning_source") == "reflex-confirmed", c["id"]
        assert len({branch(x["lang"]) for x in c["evidence"]}) >= 2, c["id"]
        langs = set(e.get("reflexes", {}))
        assert {x["lang"] for x in c["evidence"]} <= langs, c["id"]


def test_secondary_senses_do_not_make_a_consensus(lx):
    ids = {c["id"] for c in _confirmed()}
    for i in ("pie-lex-nemeti", "pie-lex-bhewdhtis", "pie-lex-koseh2"):   # 'enjoy', 'information', 'hair-net'
        assert i not in ids and lx.meaning(i)[1] == "derived"


def test_dictionary_gloss_wins_over_confirmation():
    lex = {json.loads(x)["id"]: json.loads(x) for x in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()}
    assert all(not lex[c["id"]]["meaning"] for c in _confirmed())


def test_slice_items_flag_confirmed_glosses(tmp_path, lx):
    import subprocess, sys
    name = "zz-test-confirmed"
    out = ROOT / "data/generation/slices" / f"{name}.json"
    try:
        subprocess.run([sys.executable, "-I", str(ROOT / "scripts/make_slice.py"), name, "--size", "20",
                        "--keywords", "lake"], check=True, capture_output=True, cwd=ROOT)
        items = {it["lex_id"]: it for it in json.loads(out.read_text("utf-8"))["lexemes"]}
        assert items["pie-lex-lokus"]["gloss_source"] == "reflex-confirmed"
    finally:
        out.unlink(missing_ok=True)


# 4. accents from Vedic or Greek reflexes (pie/accent_reflex.py) ---------------------------------------------------

def _accent_overrides():
    rows = [json.loads(x) for x in (ROOT / "data/lexicon/overrides.jsonl").read_text("utf-8").splitlines()]
    return [r for r in rows if r.get("accent_source")]


def test_every_reflex_accent_is_rederived_from_the_lexicon(lx):
    from pie.accent_reflex import accented, position
    rows = _accent_overrides()
    assert len(rows) == 69
    for r in rows:
        e = lx.entries[r["id"]]
        assert e["form"] == r["form"], r["id"]
        old = e["variants"][-1]           # the form override keeps the old headword as the last variant
        p = position(old, lx.specs[r["id"]]["rule"], e["reflexes"])
        assert p is not None and accented(old, p[0]) == r["form"], r["id"]
        cited = {(u["lang"], u["form"]) for u in r["accent_source"]}
        assert cited <= {(lang, x["form"]) for lang, xs in e["reflexes"].items() for x in xs}, r["id"]
        assert lx.accent_status(r["id"]) == "resolved"


def test_reflex_accent_rule_cases():
    from pie.accent_reflex import position
    G = lambda *f: {"Ancient Greek": [{"form": x, "roman": x} for x in f]}
    assert position("loǵos", "shape:thematic", G("lógos"))[0] == 2
    assert position("kerpos", "shape:thematic", G("karpós"))[0] == 1
    # recessive antepenult (ἄσπετος, a compound) and a Greek finite verb say nothing
    assert position("n̥skʷetos", "shape:thematic", G("áspetos")) is None
    assert position("bʰereti", "shape:thematic-present", G("phérō")) is None
    # Vedic decides a thematic present; Vedic and Greek disagreeing decide nothing
    V = {"Sanskrit": [{"form": "x", "roman": "bhárati"}]}
    assert position("bʰereti", "shape:thematic-present", V)[0] == 3
    assert position("woros", "shape:thematic", {**G("ourós"), "Sanskrit": [{"form": "x", "roman": "vā́ra"}]}) is None
    # a different syllable count (prothesis, compounds) says nothing
    assert position("stegos", "shape:thematic", G("astégos")) is None
