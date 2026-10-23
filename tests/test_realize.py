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


def test_t012_review_forms():
    """t012 review: earth keeps dʰ- in the weak stem, u-stem adjective nom. pl. -éwes,
    CCu- before a vowel keeps the vowel with a glide."""
    from pie.realize import Lexicon
    lx = Lexicon.load()
    earth = lx.cells("pie-lex-dhegjhoxm")
    assert "dʰǵʰém" in earth["LOC.SG"] and earth["GEN.SG"][0] == "dʰǵʰmés"
    assert lx.cells("pie-lex-mldus", "m")["NOM.PL"][0] == "ml̥déwes"
    assert lx.cells("pie-lex-kjlewt")["PTCP.ACT"][0] == "ḱluwónts"


def test_indefinite_and_hortative_negation():
    """t013 review: 'no one' is the enclitic indefinite (ne kʷis), not the question word;
    'let us not' takes mē (Gk μή + hortatory subjunctive)."""
    from pie.realize import Lexicon, realize
    lx = Lexicon.load()
    p = {"english": "No one came. Let us not go.", "clauses": [
        {"neg": True, "slots": [{"lex_id": "closed:indefinite_kwi", "role": "SUBJ"},
                                {"lex_id": "pie-lex-gwemt", "role": "V", "verb": {"tense": "AOR"}}]},
        {"neg": True, "slots": [{"lex_id": "pie-lex-gwemt", "role": "V",
                                 "verb": {"mood": "SBJV", "person": 1, "num": "PL"}}]}]}
    assert realize(p, lx)["pie"].startswith("ne kʷis gʷémt mē ")


EARTH, SKY = "pie-lex-dhegjhoxm", "pie-lex-dyexws"


@pytest.fixture(scope="module")
def ix():
    from pie.validate import load_index
    return load_index()


def _passes(text, ix):
    from pie.validate import validate_text
    return validate_text(text, ix)["status"] == "pass"


def test_near_and_far_deictics_as_modifiers(ix):
    # "this earth, that heaven": *ḱo- (Hitt. kā-) and *h₁eno- (OCS onъ) agree with their heads
    r = R({"english": "This earth sees that heaven.", "clauses": [{"slots": [
        {"lex_id": EARTH, "role": "SUBJ"}, {"lex_id": "closed:deictic_ki", "role": "MOD", "head": 0},
        {"lex_id": SKY, "role": "OBJ"}, {"lex_id": "closed:deictic_eno", "role": "MOD", "head": 2}, V(SEE)]}]})
    assert r["pie"] == "ḱéh₂ dʰéǵʰōm h₁énom dyḗm spéḱyeti."
    assert _passes(r["pie"], ix)


def test_anaphoric_and_deictics_as_pronouns(ix):
    r = R({"english": "He sees this.", "clauses": [{"slots": [
        {"lex_id": "closed:anaphoric_i", "role": "SUBJ", "gender": "m"},
        {"lex_id": "closed:deictic_ki", "role": "OBJ", "gender": "n"}, V(SEE)]}]})
    assert r["pie"] == "h₁éy ḱód spéḱyeti."            # Ringe 2017 p. 56 éy; Hitt. kā- < *ḱo-
    assert _passes(r["pie"], ix)
    r = R({"english": "That one yonder sees it. These sheep see her.", "clauses": [
        {"slots": [{"lex_id": "closed:deictic_eno", "role": "SUBJ", "gender": "f"},
                   {"lex_id": "closed:anaphoric_i", "role": "OBJ", "gender": "n"}, V(SEE)]},
        {"break": True, "slots": [{"lex_id": SHEEP, "role": "SUBJ", "num": "PL"},
                                  {"lex_id": "closed:deictic_ki", "role": "MOD", "head": 0},
                                  {"lex_id": "closed:anaphoric_i", "role": "OBJ", "gender": "f"}, V(SEE)]}]})
    assert r["pie"].startswith("h₁éneh₂ h₁íd spéḱyeti.") and "h₁íh₂m̥" in r["pie"]
    assert _passes(r["pie"], ix)


def test_anaphoric_has_no_dual():
    # Ringe 2017 p. 56 prints '???' for the dual: the cell is left out, so the plan is rejected
    from pie.realize import check_plan
    errs = check_plan({"english": "x", "clauses": [{"slots": [
        {"lex_id": "closed:anaphoric_i", "role": "SUBJ", "gender": "m", "num": "DU"}, V(SEE)]}]})
    assert errs


# --- compounds (pie/compound.py) ----------------------------------------------------------

FAME, MIND, MAN = "pie-lex-kjlewos", "pie-lex-menos", "pie-lex-h2nexr"


def _cmp(first, second, type_="bahuvrihi", **slot):
    return {"lex_id": "compound", "compound": {"first": first, "second": second, "type": type_}, **slot}


def _man_plan(compound, man_role="SUBJ"):
    return {"english": "x", "clauses": [{"slots": [
        {"lex_id": MAN, "role": man_role}, {**compound, "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-wiHros" if man_role == "OBJ" else "closed:anaphoric_i",
         "role": "SUBJ" if man_role == "OBJ" else "OBJ", "gender": "m"}, V(SEE)]}]}


def test_h1su_klewes_nominative_and_accusative():
    # *h₁su-ḱléwes- 'having good fame' (Ved. suśrávas-, Gk εὐκλεής): s-stem adjective, 2M accent (BAP)
    from pie.realize import check_plan
    p = _man_plan(_cmp("closed:prefix/h1su", FAME))
    assert check_plan(p, _lx()) == []
    assert R(p)["pie"].startswith("h₁suḱléwēs h₂nḗr ")
    r = R(_man_plan(_cmp("closed:prefix/h1su", FAME), man_role="OBJ"))
    assert "h₁suḱléwesm̥ h₂nérm̥" in r["pie"]
    w = next(w for w in r["words"] if w["lex_id"].startswith("compound:"))
    assert w["lex_id"] == "compound:bahuvrihi:closed:prefix/h1su+pie-lex-kjlewos" and w["features"] == "ACC.SG"
    # common gender: the feminine is the masculine (Gk εὐκλεής f.), the neuter in -es
    from pie.compound import resolve
    c = resolve({"first": "pie-lex-h1su", "second": FAME}, _lx())
    assert c.cells("f")["NOM.SG"][0] == "h₁suḱléwēs" and c.cells("n")["NOM.SG"][0] == "h₁suḱléwes"
    assert c.cells("m")["GEN.SG"][0] == "h₁suḱléwesos"
    assert "h₁suḱlewḗs" in c.cells("m")["NOM.SG"]          # suffix-accented alternative (Gk -ḗs) is recognized


def test_dus_compound_is_common_gender_and_matches_the_lexical_word():
    r = R({"english": "The daughter is ill-minded.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-dhugh2texr", "role": "SUBJ"}, _cmp("closed:prefix/dus", MIND, role="PRED"),
        V("pie-lex-h1esti")]}]})
    assert r["pie"] == "dʰugh₂tḗr dusménēs h₁ésti."
    # the lexicon's (unaccented) dusmenēs agrees cell for cell once accents are removed
    from pie.compound import resolve
    from pie.validate import key
    lx = _lx()
    c, lex = resolve({"first": "closed:prefix/dus", "second": MIND}, lx).cells("m"), lx.cells("pie-lex-dusmenexs")
    for f in ("NOM.SG", "ACC.SG", "GEN.SG", "NOM.PL"):
        assert key(c[f][0], "noaccent") in {key(x, "noaccent") for x in lex[f]}, f


def test_privative_and_thematic_bahuvrihis():
    from pie.compound import resolve
    lx = _lx()
    # privative: accented first member (Ringe *ń̥gʷʰdʰsitos), n̥ stays syllabic before the laryngeal
    assert resolve({"first": "closed:prefix/n", "second": HORSE}, lx).cells("m")["NOM.SG"][0] == "ń̥h₁eḱwos"
    assert resolve({"first": "closed:prefix/n", "second": FAME}, lx).cells("m")["NOM.SG"][0] == "ń̥ḱlewēs"
    # *h₁su-h₁éḱwo- 'having good horses' (Ved. suáśva-, Gk εὔιππος): thematic -os/-eh₂/-om
    c = resolve({"first": "closed:prefix/h1su", "second": HORSE}, lx)
    assert [c.cells(g)["NOM.SG"][0] for g in "mfn"] == ["h₁suh₁éḱwos", "h₁suh₁éḱweh₂", "h₁suh₁éḱwom"]
    # u-stem adjective first member yields the accent (Ved. āśu-héṣas-); thematic one keeps it (ugrá-bāhu-)
    assert resolve({"first": "pie-lex-HeHkjus", "second": HORSE}, lx).cells("m")["ACC.PL"][0] == "HeHḱuh₁éḱwons"
    assert resolve({"first": "pie-lex-newos", "second": HORSE}, lx).cells("m")["NOM.SG"][0] == "néwoh₁eḱwos"
    # determinative: a noun with the head's gender and accent
    d = resolve({"first": "pie-lex-newos", "second": EARTH, "type": "determinative"}, lx)
    assert d.head_gender == "f" and d.cells()["ACC.SG"][0] == "newodʰéǵʰōm"


def test_check_plan_rejects_unsupported_compounds():
    from pie.realize import check_plan
    lx = _lx()

    def errs(compound, **slot):
        return check_plan(_man_plan({**_cmp(**compound), **slot}), lx)

    assert any("s-stem neuter" in e for e in errs(dict(first="closed:prefix/h1su", second="pie-lex-ph2texr")))
    assert any("Caland" in e for e in errs(dict(first="pie-lex-h1rudhros", second=HORSE)))
    assert any("prefix" in e for e in errs(dict(first="closed:prefix/dus", second=HORSE, type_="determinative")))
    assert any("type" in e for e in errs(dict(first="closed:prefix/dus", second=HORSE, type_="dvandva")))
    assert any("verb" in e for e in errs(dict(first="closed:prefix/dus", second=SEE)))
    # a bahuvrihi used as a noun needs a gender; a determinative is not a MOD
    p = {"english": "x", "clauses": [{"slots": [_cmp("closed:prefix/h1su", FAME, role="SUBJ"), V(SEE)]}]}
    assert any("gender" in e for e in check_plan(p, lx))
    assert any("determinative" in e for e in errs(dict(first="pie-lex-newos", second=HORSE, type_="determinative")))


def test_compound_text_validates_exactly(ix):
    from pie.validate import index_plan_compounds, validate_text
    p = {"english": "The man of good fame sees the men with swift horses; the horseless one is ill-minded.",
         "clauses": [
             {"slots": [{"lex_id": MAN, "role": "SUBJ"}, {**_cmp("closed:prefix/h1su", FAME), "role": "MOD", "head": 0},
                        {"lex_id": "pie-lex-wiHros", "role": "OBJ", "num": "PL"},
                        {**_cmp("pie-lex-HeHkjus", HORSE), "role": "MOD", "head": 2}, V(SEE)]},
             {"break": True, "slots": [_cmp("closed:prefix/n", HORSE, role="SUBJ", gender="m"),
                                       _cmp("closed:prefix/dus", MIND, role="PRED"), V("pie-lex-h1esti")]}]}
    r = R(p)
    assert r["pie"] == "h₁suḱléwēs h₂nḗr HeHḱuh₁éḱwons wiHróns spéḱyeti. ń̥h₁eḱwos dusménēs h₁ésti."
    assert sorted(index_plan_compounds(ix, p)) == sorted({w["lex_id"] for w in r["words"]
                                                          if w["lex_id"].startswith("compound:")})
    v = validate_text(r["pie"], ix)
    assert v["status"] == "pass" and set(v["tiers"]) == {"exact"}, v["bad_forms"]


def test_prodrop_predicate_adjective_takes_verb_number():
    """t014 review: 'may they be many' with a dropped subject: polh₁éwes, not singular polh₁ús."""
    from pie.realize import Lexicon, realize
    lx = Lexicon.load()
    p = {"english": "May they be many.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-polh1us", "role": "PRED"},
        {"lex_id": "pie-lex-h1esti", "role": "V", "verb": {"mood": "OPT", "person": 3, "num": "PL"}}]}]}
    assert realize(p, lx)["pie"].startswith("polh₁éwes")


def test_t014_review_fixes():
    """-kʷe on the last conjunct; u-stem nom. pl. -éwes with a weak stem given; earth feminine;
    *h₂erh₃- keeps its h₃."""
    from pie.realize import Lexicon, realize
    lx = Lexicon.load()
    p = {"english": "He saw cows and sheep.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-gwoxws", "role": "OBJ", "num": "PL", "and": True},
        {"lex_id": "pie-lex-h2owis", "role": "OBJ", "num": "PL"},
        {"lex_id": "pie-lex-widet", "role": "V", "verb": {"tense": "AOR"}}]}]}
    words = realize(p, lx)["pie"].split()
    assert words[1].endswith("-kʷe") and not words[0].endswith("-kʷe")
    assert lx.cells("pie-lex-suHnus")["NOM.PL"][0] == "suHnéwes"
    assert lx.gender("pie-lex-dhegjhoxm") == "f"
    assert lx.cells("pie-lex-h2eryeti")["PRS.3SG"][0].startswith("h₂érh₃")
