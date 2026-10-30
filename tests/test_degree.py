"""Degrees of comparison (pie.degree) and personal pronouns under adpositions (pie.realize).

docs/morphology-comparison-and-comitative.md states the decisions; the backtest set is
data/morph/degree_backtest.json. Every plan goes through check_plan first (tests/helpers.produce)."""

import json
from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")

HORSE, WOLF, MARE = "pie-lex-h1ekjwos", "pie-lex-wlkwos", "pie-lex-h1ekjweh2"
SWIFT, SWEET, BIG, NEW = "pie-lex-HeHkjus", "pie-lex-sweh2dus", "pie-lex-megjh2s", "pie-lex-newos"
WITH, GO = "pie-lex-kjom", "pie-lex-h1eyti"


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


def V(lex=GO, tense="PRS"):
    return {"lex_id": lex, "role": "V", "verb": {"tense": tense, "mood": "IND", "voice": "ACT"}}


def plan(english, slots, **kw):
    return {"english": english, "clauses": [{"slots": slots, **kw}]}


# --- comparative and superlative -------------------------------------------------------------------------------

def test_comparative_paradigm(lx):
    from pie.degree import cells
    m = cells(SWEET, "CMP", "m", lx)
    assert m["NOM.SG"][0] == "swéh₂dyōs" and m["ACC.SG"][0] == "swéh₂dyosm̥" and m["VOC.SG"][0] == "swéh₂dyos"
    assert m["GEN.SG"][0] == "sweh₂disés" and "sweh₂disós" in m["GEN.SG"]       # weak *-is-, accented ending
    assert m["NOM.PL"][0] == "swéh₂dyoses" and m["LOC.SG"][0] == "swéh₂dyosi"
    assert "swéh₂diyōs" in m["NOM.SG"]                                         # Sievers' variant, alternative
    assert cells(SWEET, "CMP", "f", lx) == m                                    # common gender (Beekes §14.4)
    n = cells(SWEET, "CMP", "n", lx)
    assert n["NOM.SG"][:2] == ["swéh₂dyos", "swéh₂dis"] and n["NOM.PL"][0] == "swéh₂dyosh₂"


def test_superlative_paradigm(lx):
    from pie.degree import cells
    assert cells(SWEET, "SUP", "m", lx)["NOM.SG"] == ["swéh₂distos", "swéh₂disth₂os"]
    assert cells(SWEET, "SUP", "f", lx)["NOM.SG"][0] == "swéh₂disteh₂"
    assert cells(SWEET, "SUP", "n", lx)["NOM.SG"][0] == "swéh₂distom"


def test_base_from_the_root(lx):
    from pie.degree import base
    assert base("pie-lex-h2rgjros", lx).root == "h₂érǵ"     # zero grade → the linked root's e-grade
    assert base("pie-lex-polh1us", lx).root == "pléh₁"      # Gk πλείων, lexicon pléh₁yōs
    assert base("pie-lex-h1lenghus", lx).root == "h₁léngʷʰ"  # boukólos: Ringe *h₁léngʷʰistos
    assert base(NEW, lx).root == "néw" and base("pie-lex-senos", lx).root == "sén"


@pytest.mark.parametrize("lid", ["pie-lex-bhrtos", "pie-lex-diwyos", "pie-lex-megjyoxs", "pie-lex-sweh2disth2os",
                                 "pie-lex-h1sonts", "pie-lex-weydos", "pie-lex-bhoros", "pie-lex-h1eteros"])
def test_check_plan_rejects_non_primary_adjectives(lx, lid):
    from pie.realize import check_plan
    errs = check_plan(plan("x", [{"lex_id": HORSE, "role": "SUBJ"},
                                 {"lex_id": lid, "role": "PRED", "degree": "CMP"}], type="nominal"), lx)
    assert errs and "primary" in " ".join(errs)


def test_check_plan_rejects_bad_degree_slots(lx):
    from pie.realize import check_plan
    bad = [
        [{"lex_id": HORSE, "role": "SUBJ", "degree": "CMP"}, V()],                    # a noun
        [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": SWIFT, "role": "MOD", "head": 0, "degree": "MORE"}, V()],
        [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": "pie-lex-bhereti", "role": "MOD", "head": 0,
                                             "participle": {"voice": "ACT"}, "degree": "CMP"}, V()],
        # the standard of comparison is an ABL
        [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": SWIFT, "role": "MOD", "head": 0, "degree": "CMP"},
         {"lex_id": WOLF, "role": "GOAL", "dep": 1}, V()],
        # a superlative's partitive is a POSS
        [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": SWIFT, "role": "MOD", "head": 0, "degree": "SUP"},
         {"lex_id": WOLF, "role": "ABL", "dep": 1, "num": "PL"}, V()],
    ]
    for slots in bad:
        assert check_plan(plan("x", slots), lx), slots


def test_swifter_than_the_wolf(lx):
    r = produce(plan("The horse is swifter than the wolf.", [
        {"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": WOLF, "role": "ABL", "dep": 2},
        {"lex_id": SWIFT, "role": "PRED", "degree": "CMP"}], type="nominal"), lx)
    assert r["pie"] == "h₁éḱwos wĺ̥kʷōd HéHḱyōs."           # standard (ablative) before the comparative
    w = r["words"][2]
    assert w["lex_id"] == f"degree:CMP:{SWIFT}" and w["gloss"] == "swift.CMP" and w["degree_status"] == "nuclear-IE"


def test_comparative_mod_agrees_and_carries_its_standard(lx):
    r = produce(plan("The swifter mares go.", [
        {"lex_id": MARE, "role": "SUBJ", "num": "PL"}, {"lex_id": SWIFT, "role": "MOD", "head": 0, "degree": "CMP"},
        {"lex_id": WOLF, "role": "ABL", "dep": 1}, V()]), lx)
    assert r["pie"] == "wĺ̥kʷōd HéHḱyoses h₁éḱweh₂es h₁yénti."  # the feminine is the masculine: common gender


def test_superlative_with_partitive_genitive(lx):
    r = produce(plan("The sweetest of the mares goes.", [
        {"lex_id": SWEET, "role": "SUBJ", "degree": "SUP", "gender": "f"},
        {"lex_id": MARE, "role": "POSS", "dep": 0, "num": "PL"}, V()]), lx)
    assert r["pie"].startswith("h₁éḱweh₂ōm swéh₂disteh₂ ")
    assert r["words"][1]["degree_status"] == "late-IE"


def test_degree_tokens_validate_and_flag(lx):
    from pie.realize import realize, token_cell
    from pie.validate import all_exact, index_plan_degrees, load_index, validate_text
    p = plan("The new horse is bigger than the wolf.", [
        {"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": NEW, "role": "MOD", "head": 0},
        {"lex_id": WOLF, "role": "ABL", "dep": 3}, {"lex_id": BIG, "role": "PRED", "degree": "CMP"}], type="nominal")
    r = realize(p, lx)
    ix = load_index()
    assert index_plan_degrees(ix, p) == [f"degree:CMP:{BIG}"]
    assert all_exact(validate_text(r["pie"], ix))
    assert token_cell(r["words"][-1]) == {"gender": "m", "degree_status": "nuclear-IE"}


def test_export_offers_the_same_degree_cell(lx):
    from pie.export import token_variants
    rec = {"tier": 3, "tokens": [{"form": "swéh₂dyōs", "lex_id": f"degree:CMP:{SWEET}", "features": "NOM.SG",
                                  "gender": "m"}]}
    alts = token_variants(rec, lx)[0]
    assert alts[0] == "swéh₂dyōs" and "swéh₂diyōs" in alts and "swéh₂dyosm̥" not in alts


def test_degree_token_roots_and_members(lx):
    from pie.compound import member_ids
    assert member_ids(f"degree:SUP:{SWEET}") == [SWEET]


# --- personal pronouns under adpositions --------------------------------------------------------------------------

@pytest.mark.parametrize("person,num,form", [("1", "SG", "méǵʰye"), ("2", "SG", "tébʰye"), ("1", "PL", "n̥sméy"),
                                             ("2", "PL", "usméy"), ("1", "DU", "n̥sméy")])
def test_with_me_is_the_dative_under_kom(lx, person, num, form):
    r = produce(plan("He goes with me.", [{"lex_id": WITH, "role": "ADV"},
                                          {"lex_id": f"closed:personal/{person}", "role": "INS", "dep": 0, "num": num},
                                          V()]), lx)
    assert r["pie"] == f"{form} ḱóm h₁éyti."
    w = r["words"][0]
    assert w["features"] == "DAT.PL" if num != "SG" else w["features"] == "DAT.SG"
    assert w["case_fallback"] == "ins->dat"


def test_among_us_locative_falls_back_to_the_dative(lx):
    r = produce(plan("He is among us.", [{"lex_id": "pie-lex-medhi", "role": "ADV"},
                                          {"lex_id": "closed:personal/1", "role": "LOC", "dep": 0, "num": "PL"},
                                          V("pie-lex-h1esti")]), lx)
    assert r["pie"] == "n̥sméy médʰi h₁ésti." and r["words"][0]["case_fallback"] == "loc->dat"


def test_pronoun_cases_it_has_need_no_fallback(lx):
    r = produce(plan("He goes from me.", [{"lex_id": "pie-lex-h2epo", "role": "ADV"},
                                          {"lex_id": "closed:personal/1", "role": "ABL", "dep": 0}, V()]), lx)
    assert r["pie"] == "méd h₂epó h₁éyti." and not r["words"][0].get("case_fallback")


def test_pronoun_without_the_case_is_rejected_with_a_reason(lx):
    from pie.realize import check_plan
    errs = check_plan(plan("by me", [{"lex_id": "closed:personal/1", "role": "INS"}, V()]), lx)
    assert errs and "Ringe 2006 p. 57" in errs[0] and "ḱóm" in errs[0]
    errs = check_plan(plan("with me", [{"lex_id": WITH, "role": "ADV"},
                                       {"lex_id": "closed:personal/1", "role": "INS", "dep": 0, "enclitic": True},
                                       V()]), lx)
    assert errs and "stressed form" in errs[0]


def test_nouns_under_kom_keep_the_instrumental(lx):
    r = produce(plan("He goes with the wolf.", [{"lex_id": WITH, "role": "ADV"},
                                                {"lex_id": WOLF, "role": "INS", "dep": 0}, V()]), lx)
    assert r["pie"] == "wĺ̥kʷoh₁ ḱóm h₁éyti." and not r["words"][0].get("case_fallback")


# --- the backtest -------------------------------------------------------------------------------------------------

def test_degree_backtest(lx):
    """data/morph/degree_backtest.json: every handbook-reconstructed or multi-branch comparative/superlative whose
    positive the lexicon has; the engine's result for each is recorded in the file (expect), so a change in the
    engine that turns a hit into a miss, or a miss into a hit, fails here and the doc's table must be updated."""
    from pie.degree import backtest
    data = json.loads((ROOT / "data/morph/degree_backtest.json").read_text("utf-8"))
    rows = backtest(data["items"], lx)
    got = {r["id"]: r["result"] for r in rows}
    want = {it["id"]: it["expect"] for it in data["items"]}
    assert got == want
    s = data["summary"]
    scored = [r for r in rows if r["result"] != "excluded"]
    assert s["scored"] == len(scored)
    assert s["hit"] == sum(r["result"] == "hit" for r in rows)
    assert s["alt"] == sum(r["result"] == "alt" for r in rows)
