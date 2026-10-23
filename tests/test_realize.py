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
    assert r["pie"] == "h₂ówis h₁éḱwons spéḱyeti."   # acc. pl. -ns (Fortson §6.14)
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


def test_pronoun_gender_and_kwid():
    r = R({"english": "What does the sheep see?", "clauses": [{"question": True, "slots": [
        {"lex_id": SHEEP, "role": "SUBJ"}, {"lex_id": "closed:interrogative_kwi", "role": "OBJ", "gender": "n"},
        V(SEE)]}]})
    assert r["pie"] == "kʷíd h₂ówis spéḱyeti?"          # fronted, neuter, question mark


def test_predicate_adjective_agrees_with_subject():
    r = R({"english": "The daughter is new.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-dhugh2texr", "role": "SUBJ"}, {"lex_id": "pie-lex-newos", "role": "PRED"},
        V("pie-lex-h1esti")]}]})
    assert "néweh₂" in r["pie"]


def test_prohibitive_is_injunctive():
    r = R({"english": "Do not see!", "clauses": [{"neg": True, "slots": [V(SEE, mood="IMP", person=2)]}]})
    assert r["pie"] == "mē spéḱyes."
    assert "INJ.2SG" in r["gloss"]


def test_nested_possessor_modifier_is_kept():
    r = R({"english": "The great king's daughter sees.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-dhugh2texr", "role": "SUBJ"},
        {"lex_id": "pie-lex-h3rexgjs", "role": "POSS", "head": 0},
        {"lex_id": "pie-lex-megjh2s", "role": "MOD", "head": 1},
        V(SEE)]}]})
    # "great" agrees with "king's" (genitive, weak stem), and nothing is dropped
    assert r["pie"] == "m̥ǵh₂és h₃rēǵés dʰugh₂tḗr spéḱyeti."   # lengthened grade throughout (Lat. rēgis)


def test_sentence_break_and_noun_coordination():
    r = R({"english": "Sheep and horses see. They see.", "clauses": [
        {"slots": [{"lex_id": SHEEP, "role": "SUBJ", "num": "PL"}, {"lex_id": HORSE, "role": "SUBJ", "num": "PL",
                                                                     "and": True}, V(SEE)]},
        {"break": True, "slots": [{"lex_id": "closed:demonstrative_so", "role": "SUBJ", "num": "PL"}, V(SEE)]}]})
    assert r["pie"].count(".") == 2 and "-kʷe" in r["pie"]


def test_unattached_slot_is_an_error_not_a_silent_drop():
    from pie.realize import check_plan
    errs = check_plan({"english": "x", "clauses": [{"slots": [
        {"lex_id": SHEEP, "role": "SUBJ"}, {"lex_id": "pie-lex-megjh2s", "role": "MOD", "head": 2},
        {"lex_id": "pie-lex-newos", "role": "MOD", "head": 1}, V(SEE)]}]})
    assert errs


def test_pro_drop_person_and_number_on_the_verb():
    r = R({"english": "Let us see the sheep!", "clauses": [{"slots": [
        {"lex_id": SHEEP, "role": "OBJ"},
        {"lex_id": SEE, "role": "V", "verb": {"mood": "SBJV", "voice": "ACT", "person": 1, "num": "PL"}}]}]})
    assert r["pie"] == "h₂ówim spéḱyōmes."   # 1pl -mes (Lundquist & Yates, Beekes, Fortson)


def test_blocked_and_deponent_lexemes_are_rejected():
    from pie.realize import Lexicon, check_plan
    lx = Lexicon.load()
    assert "pie-lex-kjekjlowe" in lx.blocked
    errs = check_plan({"english": "x", "clauses": [{"slots": [{"lex_id": SHEEP, "role": "SUBJ"},
                                                              V("pie-lex-kjekjlowe", tense="PRF")]}]}, lx)
    assert any("blocked" in e for e in errs)
    dep = next((i for i, r in lx.specs.items() if r.get("usable") and r["family"] == "verb"
                and lx.entries[i]["form"].endswith("tor")), None)
    if dep:
        assert any("deponent" in e for e in check_plan(
            {"english": "x", "clauses": [{"slots": [{"lex_id": SHEEP, "role": "SUBJ"}, V(dep)]}]}, lx))


def _lx():
    from pie.realize import Lexicon
    return Lexicon.load()


def _ptcp_plan(subj, voice, subj_role="SUBJ"):
    return {"english": "x", "clauses": [{"slots": [
        {"lex_id": subj, "role": subj_role, "num": "SG"},
        {"lex_id": "pie-lex-bhereti", "role": "MOD", "head": 0, "participle": {"voice": voice}},
        {"lex_id": "pie-lex-bhoros", "role": "OBJ", "num": "SG", "dep": 1, "gender": "m"},
        {"lex_id": "pie-lex-h1ekjwos", "role": "OBJ" if subj_role == "SUBJ" else "SUBJ", "num": "PL"},
        {"lex_id": "pie-lex-dedorkje", "role": "V", "verb": {"tense": "PRF"}}]}]}


def test_participle_phrase_agrees_and_takes_its_own_object():
    from pie.realize import check_plan, realize
    lx = _lx()
    p = _ptcp_plan("pie-lex-h2nexr", "ACT")
    assert check_plan(p, lx) == []
    assert realize(p, lx)["pie"] == "bʰoróm bʰéronts h₂nḗr h₁éḱwons dedórḱe."
    assert "bʰérontih₂" in realize(_ptcp_plan("pie-lex-meh2texr", "ACT"), lx)["pie"]      # feminine -ih₂
    assert "bʰéromh₁nos" in realize(_ptcp_plan("pie-lex-h2nexr", "MID"), lx)["pie"]        # middle -omh₁no- (L&Y, Beekes)


def test_thematic_participle_genitive_has_no_ablaut():
    lx = _lx()
    assert lx.participle_cells("pie-lex-bhereti", "ACT", "m")["GEN.SG"] == ["bʰérontos"]   # Ved. bháratas


def test_dep_must_point_at_a_participle():
    from pie.realize import check_plan
    p = _ptcp_plan("pie-lex-h2nexr", "ACT")
    del p["clauses"][0]["slots"][1]["participle"]
    assert any("dep must point" in e for e in check_plan(p, _lx()))


def test_or_and_emphatic_enclitics():
    from pie.realize import realize
    lx = _lx()
    p = {"english": "x", "clauses": [
        {"slots": [{"lex_id": "pie-lex-h1ekjwos", "role": "SUBJ", "num": "SG"},
                   {"lex_id": "pie-lex-h1esti", "role": "V", "verb": {"tense": "PRS"}}]},
        {"conj": "wē", "particle": "ge", "slots": [{"lex_id": "pie-lex-gwoxws", "role": "SUBJ", "num": "SG"},
                                                  {"lex_id": "pie-lex-h1esti", "role": "V", "verb": {"tense": "PRS"}}]}]}
    assert realize(p, lx)["pie"] == "h₁éḱwos h₁ésti gʷṓws-wē-ge h₁ésti."


def test_numerals_govern_number():
    from pie.realize import realize
    lx = _lx()
    p = {"english": "x", "clauses": [{"slots": [
        {"lex_id": "pie-lex-h1ekjwos", "role": "SUBJ", "num": "PL"},
        {"lex_id": "closed:numerals/3", "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-bhewgt-3", "role": "V", "verb": {"tense": "AOR"}}]}]}
    assert realize(p, lx)["pie"] == "tréyes h₁éḱwōs bʰugént."
    p["clauses"][0]["slots"][1]["lex_id"] = "closed:numerals/indeclinable/7"
    assert realize(p, lx)["pie"].startswith("septḿ̥ ")
