"""Engine queue from the wave-1 Tier 3 reviews (docs/audits/engine-queue-wave1.md). Each fix is tested on the production
path: tests/helpers.produce (check_plan, then realize), plan_warnings, the validator, and scripts/make_slice.py."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")

MARE, TAIL, WASP = "pie-lex-h1ekjweh2", "pie-lex-h1orseh2", "pie-lex-wobhseh2"
OX, SALT, FOX = "pie-lex-ugwsexn", "pie-lex-sexh2l", "pie-lex-h2wlpis"
WHITE, SHINING = "pie-lex-bhlHos", "pie-lex-h2rgjros"
KNOW, GIVE, CARRY, FOLLOW, BE, EAT = ("pie-lex-woyde", "pie-lex-deh3t", "pie-lex-bhereti", "pie-lex-sekwetor",
                                      "pie-lex-h1esti", "pie-lex-h1edti")
SAY, DRIVE = "pie-lex-h2egjt", "pie-lex-h2egjeti"
HORSE, SHEEP, CATTLE, SKY, BIG = "pie-lex-h1ekjwos", "pie-lex-h2owis", "pie-lex-gwoxws", "pie-lex-dyexws", "pie-lex-megjh2s"


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    Lexicon.load.cache_clear()
    return Lexicon.load()


@pytest.fixture(scope="module")
def ix():
    from pie.validate import load_index
    return load_index()


def V(lex, tense="PRS", mood="IND", voice="ACT", person=None, num=None):
    return {"lex_id": lex, "role": "V", "verb": {"tense": tense, "mood": mood, "voice": voice, "person": person,
                                                  "num": num}}


def P(*clauses, english="x"):
    return {"english": english, "clauses": list(clauses)}


def _errs(plan, lx):
    from pie.realize import check_plan
    return check_plan(plan, lx)


def _warns(plan, lx):
    from pie.realize import plan_warnings
    return plan_warnings(plan, lx)


def _ok(text, ix):
    from pie.validate import validate_text
    return validate_text(text, ix)["status"] == "pass"


# 1. eh₂-stems ---------------------------------------------------------------------------------------------------

def test_eh2_backtest_skips_tables_on_another_spelling():
    rep = json.loads((ROOT / "data/morph/classify_report.json").read_text("utf-8"))
    eh2 = rep["backtest"]["shape:eh2"]
    assert eh2["cell_accuracy"] == 1.0 and eh2["cells"] == 285
    assert rep["usable_for_tier3"] >= 4609


def test_eh2_nouns_are_usable_and_realize(lx, ix):
    for i in (MARE, TAIL, WASP):
        assert lx.inadmissible(i) is None and lx.gender(i) == "f"
    r = produce(P({"slots": [{"lex_id": MARE, "role": "SUBJ"}, {"lex_id": WHITE, "role": "MOD", "head": 0},
                             {"lex_id": SHEEP, "role": "OBJ", "num": "PL"}, V(CARRY)]}), lx)
    assert r["pie"] == "bʰl̥Héh₂ h₁éḱweh₂ h₂ówins bʰéreti."
    assert _ok(r["pie"], ix)


def test_ox_salt_fox_have_checked_specs(lx):
    assert lx.cells(OX)["NOM.SG"][0] == "ugʷsḗn" and lx.cells(OX)["GEN.SG"][0] == "ugʷsnés"
    assert lx.cells(SALT)["NOM.SG"][0] == "sḗh₂l" and lx.cells(SALT)["GEN.SG"][0] == "sh₂lés"
    assert lx.cells(FOX)["NOM.SG"][0] == "h₂wĺ̥pis" and lx.gender(FOX) == "f" and lx.gloss(FOX) == "fox"
    for i in (OX, SALT, FOX):
        assert lx.inadmissible(i) is None


def test_colour_words_are_adjectives_and_agree(lx):
    # t031: bʰl̥Hós with neuter dʰéyǵʰos, h₂r̥ǵrós with the neuter fire
    assert lx.specs[WHITE]["family"] == "adj" and lx.specs[SHINING]["family"] == "adj"
    r = produce(P({"type": "nominal", "slots": [{"lex_id": "pie-lex-peh2wr", "role": "SUBJ"},
                                                {"lex_id": SHINING, "role": "PRED"}]}), lx)
    assert r["pie"] == "péh₂wr̥ h₂r̥ǵróm."


# 2. no 2du/3du perfect ------------------------------------------------------------------------------------------

def test_dual_perfect_is_rejected(lx):
    two = [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": SHEEP, "role": "SUBJ", "and": True}]
    errs = _errs(P({"slots": two + [V(KNOW, tense="PRF")]}), lx)
    assert any("perfect has no 3du" in e for e in errs)
    errs = _errs(P({"slots": [V(KNOW, tense="PRF", person=2, num="DU")]}), lx)
    assert any("perfect has no 2du" in e for e in errs)
    # the escape: a dual subject with an explicit plural perfect
    assert any("perfect" in e for e in _errs(P({"slots": two + [V(KNOW, tense="PRF", num="PL")]}), lx))
    # the 1du exists (*-wé), the aorist dual exists
    produce(P({"slots": [V(KNOW, tense="PRF", person=1, num="DU")]}), lx)
    r = produce(P({"slots": two + [V(GIVE, tense="AOR")]}), lx)
    assert r["words"][-1]["features"] == "AOR.3DU"


def test_middle_dual_keeps_the_flagged_fallback(lx):
    two = [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": SHEEP, "role": "SUBJ", "and": True}]
    r = produce(P({"slots": two + [V(FOLLOW, tense="PST", voice="MID")]}), lx)
    assert r["words"][-1]["features"] == "MID.PST.3PL" and r["words"][-1]["num_fallback"] == "du->pl"


# 3. middle 2sg secondary: Fortson §5.16 and Ringe 2006 p. 30 print *-th₂e ---------------------------------------

def test_middle_2sg_secondary_is_th2e(lx):
    assert lx.cells(FOLLOW)["MID.PST.2SG"][0] == "sékʷeth₂e"


# 4. neg "ne" with the 1st-person subjunctive ---------------------------------------------------------------------

def test_neg_ne_with_first_person_subjunctive(lx):
    obj = {"lex_id": HORSE, "role": "OBJ"}
    hort = produce(P({"neg": True, "slots": [obj, V(GIVE, tense="AOR", mood="SBJV", person=1)]}), lx)
    assert hort["pie"].startswith("h₁éḱwom mē ")            # 'let me not give'
    fut = produce(P({"neg": "ne", "slots": [obj, V(GIVE, tense="AOR", mood="SBJV", person=1)]}), lx)
    assert fut["pie"] == hort["pie"].replace("mē", "ne")    # 'I shall not give'
    assert any("prohibition" in e for e in _errs(P({"neg": "ne", "slots": [V(CARRY, mood="IMP", person=2)]}), lx))
    assert any("statement takes ne" in e for e in _errs(P({"neg": "mē", "slots": [V(CARRY)]}), lx))
    assert any("neg must be" in e for e in _errs(P({"neg": "no", "slots": [V(CARRY)]}), lx))


# 5. silent defaults ---------------------------------------------------------------------------------------------

def test_imperative_beside_a_vocative_needs_a_person(lx):
    voc = {"lex_id": SKY, "role": "VOC"}
    errs = _errs(P({"slots": [voc, V(CARRY, mood="IMP")]}), lx)
    assert any("imperative beside a VOC needs a person" in e for e in errs)
    r = produce(P({"slots": [voc, V(CARRY, mood="IMP", person=2)]}), lx)
    assert r["words"][-1]["features"] == "IMP.2SG"
    # no VOC: a 3rd-person command stays allowed ('let him carry')
    r = produce(P({"slots": [V(CARRY, mood="IMP")]}), lx)
    assert r["words"][-1]["features"] == "IMP.3SG"
    # any mood: a person-less verb after a vocative clause warns
    plan = P({"type": "np", "case": "VOC", "slots": [{"lex_id": SKY, "role": "NP"}]},
             {"slots": [V(CARRY)]})
    assert any("VOC is near" in w for w in _warns(plan, lx))


def test_verb_only_clause_after_plural_subject_warns(lx):
    plan = P({"slots": [{"lex_id": CATTLE, "role": "SUBJ", "num": "PL"}, V(CARRY)]},
             {"conj": "kʷe", "slots": [V(EAT)]})
    assert any("verb-only clause after a PL subject" in w for w in _warns(plan, lx))
    plan["clauses"][1]["slots"][0]["verb"].update(person=3, num="PL")
    assert not any("verb-only" in w for w in _warns(plan, lx))


def test_ungendered_pronoun_with_adjective_warns(lx):
    plan = P({"type": "nominal", "slots": [{"lex_id": "closed:personal/2", "role": "SUBJ"},
                                           {"lex_id": BIG, "role": "PRED"}]})
    assert any("pronoun has no gender" in w for w in _warns(plan, lx))
    plan["clauses"][0]["slots"][0]["gender"] = "f"
    assert not any("pronoun has no gender" in w for w in _warns(plan, lx))
    assert produce(plan, lx)["pie"] == "túH méǵh₂ih₂."


def test_pred_gender_contradicting_the_subject_is_rejected(lx):
    plan = P({"type": "nominal", "slots": [{"lex_id": "closed:personal/2", "role": "SUBJ"},
                                           {"lex_id": BIG, "role": "PRED", "gender": "f"}]})
    assert any("its own gender f is ignored" in e for e in _errs(plan, lx))
    plan["clauses"][0]["slots"][0]["gender"] = "f"
    produce(plan, lx)


def test_say_drive_homophony_warns(lx):
    said = P({"slots": [{"lex_id": "pie-lex-kjwox", "role": "SUBJ"}, V(SAY, tense="AOR")]})
    w = _warns(said, lx)
    assert any("h₂éǵt" in x and "h₂éǵet" in x for x in w)          # t030: 'said' for 'drove'
    drives = P({"slots": [{"lex_id": "pie-lex-kjwox", "role": "SUBJ"}, {"lex_id": SHEEP, "role": "OBJ"}, V(DRIVE)]})
    assert any("is also h₂éǵeti" in x for x in _warns(drives, lx))  # = the say-aorist's subjunctive
    assert not any("one letter" in x or "is also" in x
                   for x in _warns(P({"slots": [{"lex_id": "pie-lex-kjwox", "role": "SUBJ"}, V(CARRY)]}), lx))


def test_narten_imperative_is_zero_grade(lx):
    # Fortson §5.54 *-dʰí on the zero grade; Ved. addhí (t027 review: h₁éddʰi)
    assert lx.cells(EAT)["IMP.2SG"][:2] == ["h₁ddʰí", "h₁éddʰi"]
    # no nucleus left (*ttḱ-) or a root in a laryngeal (Ved. vā́hi): the stem form stays
    assert lx.cells("pie-lex-textkjti")["IMP.2SG"][0] == "tétḱdʰi"
    assert lx.cells("pie-lex-h2wexh1ti")["IMP.2SG"][0] == "h₂wéh₁dʰi"


# 6. 'here' ------------------------------------------------------------------------------------------------------

def test_here_adverb_realizes_in_place_and_validates(lx, ix):
    r = produce(P({"slots": [{"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": "closed:deictic_adv/here", "role": "ADV"},
                             V("pie-lex-h1eyti")]}), lx)
    assert r["pie"] == "h₁éḱwos h₁idʰé h₁éyti."
    assert _ok(r["pie"], ix)


# 6-7. make_slice: 'here' offered, 'cow' finds the cattle ---------------------------------------------------------

def test_slice_offers_here_and_matches_synonyms(tmp_path, monkeypatch):
    ms = runpy.run_path(str(ROOT / "scripts/make_slice.py"))
    monkeypatch.setitem(ms["main"].__globals__, "ROOT", tmp_path)
    (tmp_path / "data/generation/slices").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["make_slice.py", "herd", "--keywords", "cow", "milk", "--size", "60"])
    assert ms["main"]() == 0
    s = json.loads((tmp_path / "data/generation/slices/herd.json").read_text("utf-8"))
    assert "closed:deictic_adv/here" in s["closed"]
    assert CATTLE in s["theme_core"]


# census: shape rules fixed at the source --------------------------------------------------------------------------

def test_o_grade_i_stem_is_acrostatic_and_rc_root_stays_proterokinetic():
    from pie.classify import by_shape
    sheep = by_shape({"form": "h₂ówis", "pos": "noun", "gender": "f"}).spec
    assert (sheep.strong, sheep.weak, sheep.accent_class) == ("h₂ówi", "h₂éwi", "acrostatic")   # = the table
    testis = by_shape({"form": "h₁órǵʰis", "pos": "noun"}).spec                                  # Fortson §6.27
    assert (testis.weak, testis.accent_class) == ("h₁r̥ǵʰéy", "proterokinetic")
    thought = by_shape({"form": "méntis", "pos": "noun", "gender": "f"}).spec
    assert (thought.weak, thought.accent_class) == ("mn̥téy", "proterokinetic")


def test_amphikinetic_n_stem_root_resonant_is_consonantal():
    from pie.classify import by_shape
    eagle = by_shape({"form": "h₃érō", "pos": "noun", "gender": "m"}).spec
    assert (eagle.weak, eagle.loc_sg) == ("h₃rn̥", ["h₃rén"])                                     # = the table
    assert by_shape({"form": "gléwō", "pos": "noun"}).spec.weak == "glun̥"


def test_census_rules_pass_the_backtest_and_their_lexemes_are_usable(lx):
    rep = json.loads((ROOT / "data/morph/classify_report.json").read_text("utf-8"))
    assert rep["backtest"]["shape:pk-iu-stem"]["cell_accuracy"] >= 0.85
    assert rep["backtest"]["shape:n-stem-ak"]["cell_accuracy"] >= 0.85
    assert rep["usable_for_tier3"] >= 4885
    rows = [json.loads(x) for x in (ROOT / "data/morph/inflection_specs.jsonl").read_text("utf-8").splitlines()]
    for rule in ("shape:pk-iu-stem", "shape:n-stem-ak"):
        assert all(r["usable"] for r in rows if r["rule"] == rule), rule
    lid = next(r["id"] for r in rows if r["rule"] == "shape:n-stem-ak" and r["form"] == "stérō")
    assert lx.admissible_cells(lid)["GEN.SG"][0] == "str̥nés"
