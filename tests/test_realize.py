from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")


def R(plan):
    from pie.realize import realize
    return realize(plan)


def V(lex, tense="PRS", mood="IND", voice="ACT", person=None):
    return {"lex_id": lex, "role": "V", "verb": {"tense": tense, "mood": mood, "voice": voice, "person": person}}


SHEEP, HORSE, SEE = "pie-lex-h2owis", "pie-lex-h1ekjwos", "pie-lex-spekjyeti"


def test_sov_with_case_and_number():
    r = R({"english": "The sheep sees the horses.", "clauses": [{"slots": [
        {"lex_id": SHEEP, "role": "SUBJ", "num": "SG"}, {"lex_id": HORSE, "role": "OBJ", "num": "PL"}, V(SEE)]}]})
    assert r["pie"] == "h₂ówis h₁éḱwoms spéḱyeti."
    assert r["gloss"].split()[0] == "sheep-NOM.SG"


def test_adjective_agrees_with_its_head():
    r = R({"english": "The great horse carries.", "clauses": [{"slots": [
        {"lex_id": HORSE, "role": "SUBJ", "num": "PL"}, {"lex_id": "pie-lex-megjh2s", "role": "MOD", "head": 0},
        V("pie-lex-bhereti")]}]})
    words = r["words"]
    assert words[0]["lex_id"] == "pie-lex-megjh2s" and words[0]["features"] == "NOM.PL"
    assert r["pie"].endswith("bʰéronti.")            # plural subject → 3pl


def test_conjunction_and_wackernagel_enclitic():
    r = R({"english": "The horses carry, and the sheep sees me.", "clauses": [
        {"slots": [{"lex_id": HORSE, "role": "SUBJ", "num": "PL"}, V("pie-lex-bhereti")]},
        {"conj": "kʷe", "slots": [{"lex_id": SHEEP, "role": "SUBJ", "num": "SG"},
                                   {"lex_id": "closed:personal/1", "role": "OBJ", "num": "SG", "enclitic": True},
                                   V(SEE)]}]})
    assert "h₂ówis-kʷe me spéḱyeti" in r["pie"]   # clitic boundary written with a hyphen


def test_negation_and_prohibitive():
    r = R({"english": "The sheep does not see.", "clauses": [{"neg": True, "slots": [
        {"lex_id": SHEEP, "role": "SUBJ"}, V(SEE)]}]})
    assert r["pie"] == "h₂ówis ne spéḱyeti."
    r = R({"english": "Do not see!", "clauses": [{"neg": True, "slots": [V(SEE, mood="IMP", person=2)]}]})
    assert r["pie"].startswith("mē ")


def test_verb_initial():
    r = R({"english": "Sees the sheep.", "clauses": [{"order": "VSO", "slots": [
        {"lex_id": SHEEP, "role": "SUBJ"}, V(SEE)]}]})
    assert r["pie"] == "spéḱyeti h₂ówis."


def test_first_person_subject_drives_the_verb():
    r = R({"english": "I see the sheep.", "clauses": [{"slots": [
        {"lex_id": "closed:personal/1", "role": "SUBJ", "num": "SG"}, {"lex_id": SHEEP, "role": "OBJ"}, V(SEE)]}]})
    assert r["pie"].endswith("spéḱyoh₂.")


def test_check_plan_rejects():
    from pie.realize import check_plan
    assert check_plan({"english": "x", "clauses": [{"slots": [{"lex_id": "pie-lex-nope", "role": "SUBJ"}, V(SEE)]}]})
    assert check_plan({"english": "x", "clauses": [{"slots": [{"lex_id": SHEEP, "role": "SUBJ"}]}]})  # no verb
    assert check_plan({"english": "x", "clauses": [{"slots": [
        {"lex_id": "pie-lex-megjh2s", "role": "MOD"}, V(SEE)]}]})                                       # no head
    assert check_plan({"english": "x", "clauses": [{"slots": [{"lex_id": SEE, "role": "SUBJ"}, V(SEE)]}]})
    assert not check_plan({"english": "x", "clauses": [{"slots": [{"lex_id": SHEEP, "role": "SUBJ"}, V(SEE)]}]})


def test_realized_text_validates_exactly():
    """The realizer's output must pass the validator at the exact tier."""
    from pie.validate import load_index, validate_text
    r = R({"english": "The great horses see the sheep.", "clauses": [{"slots": [
        {"lex_id": HORSE, "role": "SUBJ", "num": "PL"}, {"lex_id": "pie-lex-megjh2s", "role": "MOD", "head": 0},
        {"lex_id": SHEEP, "role": "OBJ"}, V(SEE)]}]})
    v = validate_text(r["pie"], load_index())
    assert v["coverage"] == 1.0 and set(v["tiers"]) == {"exact"}, v


def test_feminine_noun_takes_feminine_adjective():
    # Regression: table specs default to m; the lexicon says dʰugh₂tḗr is f.
    from pie.realize import Lexicon
    lx = Lexicon.load()
    assert lx.gender("pie-lex-dhugh2texr") == "f"
    r = R({"english": "The new daughter sees.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-dhugh2texr", "role": "SUBJ"}, {"lex_id": "pie-lex-newos", "role": "MOD", "head": 0},
        V(SEE)]}]})
    assert r["pie"].startswith("néweh₂ dʰugh₂tḗr")
