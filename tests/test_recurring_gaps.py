"""The recurring engine gaps of docs/NEXT.md (t056, t062, t073, t076, t085, t086 reviews): an apposition's own
number, the case of a short (np) answer, and the 2du/3du middle. Run through tests/helpers.produce (check_plan,
then realize), and plan_warnings as realize_plans.py calls it."""

from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")

COW, PRICE, ASK, HORSE, SHEEP = ("pie-lex-gwoxws", "pie-lex-kwoyneh2", "pie-lex-prexkjst", "pie-lex-h1ekjwos",
                                 "pie-lex-h2owis")
CHIEF, RETURN, CARRY = "pie-lex-wikjpotis", "pie-lex-nesetor", "pie-lex-bhereti"
HUNDRED, TEN = "closed:numerals/indeclinable/100", "closed:numerals/indeclinable/10"
ASK_V = {"lex_id": ASK, "role": "V", "verb": {"tense": "AOR", "mood": "SBJV", "voice": "ACT"}}


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


def _feats(r):
    return {w["lex_id"]: w["features"] for w in r["words"]}


# --- 1. an apposition agrees in case; its number is its own when the plan sets it ----------------------------

def test_apposition_keeps_its_own_number(lx):
    # 'the blood-price, a hundred cows' (t076-0018, t086-0002 first attempt): SG head, PL apposition
    r = produce({"english": "He will ask the blood-price, a hundred cows.", "clauses": [{"slots": [
        {"lex_id": PRICE, "role": "OBJ"}, {"lex_id": COW, "role": "APPOS", "head": 0, "num": "PL", "gender": "f"},
        {"lex_id": HUNDRED, "role": "MOD", "head": 1}, ASK_V]}]}, lx)
    f = _feats(r)
    assert f[PRICE] == "ACC.SG" and f[COW] == "ACC.PL"
    assert "gʷṓs" in r["pie"].split() and "gʷṓm" not in r["pie"].split()
    # a numeral on the apposition sets its number even with num unset
    r = produce({"english": "He will ask the blood-price, a hundred cows.", "clauses": [{"slots": [
        {"lex_id": PRICE, "role": "OBJ"}, {"lex_id": COW, "role": "APPOS", "head": 0, "gender": "f"},
        {"lex_id": HUNDRED, "role": "MOD", "head": 1}, ASK_V]}]}, lx)
    assert _feats(r)[COW] == "ACC.PL"


def test_apposition_without_num_takes_its_heads(lx):
    r = produce({"english": "The horses, the cattle, carry.", "clauses": [{"slots": [
        {"lex_id": HORSE, "role": "SUBJ", "num": "PL"}, {"lex_id": COW, "role": "APPOS", "head": 0},
        {"lex_id": CARRY, "role": "V"}]}]}, lx)
    assert _feats(r)[COW] == "NOM.PL"


# --- 2. a short answer takes the case of what its question asks ----------------------------------------------

QUESTION = {"english": "What will the chief ask?", "question": True, "slots": [
    {"lex_id": "closed:interrogative_kwi", "role": "OBJ", "gender": "n"}, {"lex_id": CHIEF, "role": "SUBJ"}, ASK_V]}


def _answer(**case):
    return {"english": "Ten horses and a hundred sheep.", "type": "np", "break": True, **case, "slots": [
        {"lex_id": HORSE, "role": "NP", "num": "PL"}, {"lex_id": TEN, "role": "MOD", "head": 0},
        {"lex_id": SHEEP, "role": "NP", "num": "PL", "and": True}, {"lex_id": HUNDRED, "role": "MOD", "head": 2}]}


def test_np_answer_takes_the_case_the_plan_sets(lx):
    from pie.realize import plan_warnings
    plan = {"english": "What will the chief ask? Ten horses and a hundred sheep.",
            "clauses": [QUESTION, _answer(case="ACC")]}
    r = produce(plan, lx)
    assert r["pie"].endswith("déḱm̥ h₁éḱwons ḱm̥tóm-kʷe h₂ówins.")
    assert _feats(r)[HORSE] == "ACC.PL" and _feats(r)[SHEEP] == "ACC.PL"
    assert not any("np answer" in w for w in plan_warnings(plan, lx))


def test_np_answer_without_case_warns(lx):
    from pie.realize import plan_warnings
    plan = {"english": "What will the chief ask? Ten horses and a hundred sheep.",
            "clauses": [QUESTION, _answer()]}
    assert _feats(produce(plan, lx))[HORSE] == "NOM.PL"         # the default, unchanged
    w = [x for x in plan_warnings(plan, lx) if "np answer" in x]
    assert len(w) == 1 and '"case": "ACC"' in w[0] and "OBJ" in w[0]
    # a question about the subject: the nominative is right, no warning
    who = {**QUESTION, "english": "Who will ask?", "slots": [
        {"lex_id": "closed:interrogative_kwi", "role": "SUBJ", "gender": "m"}, ASK_V]}
    assert not any("np answer" in x for x in plan_warnings({"english": "x", "clauses": [who, _answer()]}, lx))


# --- 3. the 2du/3du middle: the plural stands in, flagged and warned -----------------------------------------

def test_dual_middle_falls_back_flagged_and_warns(lx):
    from pie.realize import plan_warnings
    plan = {"english": "The two horses returned.", "clauses": [{"slots": [
        {"lex_id": HORSE, "role": "SUBJ", "num": "DU"},
        {"lex_id": RETURN, "role": "V", "verb": {"tense": "PST", "voice": "MID"}}]}]}
    verb = produce(plan, lx)["words"][-1]
    assert verb["features"].endswith("3PL") and verb["num_fallback"] == "du->pl"
    w = [x for x in plan_warnings(plan, lx) if "num_fallback" in x]
    assert len(w) == 1 and "Ringe 2006 p. 32" in w[0] and verb["form"] in w[0]


@pytest.mark.parametrize("voice,person", [("ACT", 3), ("MID", 1)])
def test_no_dual_warning_where_the_dual_cell_exists(lx, voice, person):
    from pie.realize import plan_warnings
    plan = {"english": "We two carry.", "clauses": [{"slots": [
        {"lex_id": CARRY, "role": "V", "verb": {"voice": voice, "person": person, "num": "DU"}}]}]}
    verb = produce(plan, lx)["words"][-1]
    assert verb["features"].endswith(f"{person}DU") and verb["num_fallback"] is None
    assert not any("num_fallback" in x for x in plan_warnings(plan, lx))


# --- solh₂wós 'whole, all' is an adjective (lexicon round 3 Notes; t079 review) --------------------------------

def test_all_is_an_adjective(lx):
    r = produce({"english": "All the horses carry.", "clauses": [{"slots": [
        {"lex_id": HORSE, "role": "SUBJ", "num": "PL"}, {"lex_id": "pie-lex-solh2wos", "role": "MOD", "head": 0},
        {"lex_id": CARRY, "role": "V"}]}]}, lx)
    assert r["pie"] == "solh₂wṓs h₁éḱwōs bʰéronti."
    # a feminine noun use agrees: solh₂wéh₂, not the masculine solh₂wós
    r = produce({"english": "The whole one carries.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-solh2wos", "role": "SUBJ", "gender": "f"}, {"lex_id": CARRY, "role": "V"}]}]}, lx)
    assert r["pie"].startswith("solh₂wéh₂ ")
