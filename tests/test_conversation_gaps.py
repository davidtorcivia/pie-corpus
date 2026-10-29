"""t024 review: the conversation planner had no 'why', 'when', 'how many', and no personal names.
Interrogative and correlative adverbs (closed_class.json interrogative_adv, correlative_adv), the h₂nr̥- zero
grade for h₂nḗr-names (pie/compound.py ZERO_GRADE_FIRST), and the ids make_slice offers. Run through
tests/helpers.produce (check_plan, then realize) and the validator."""

from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")

HORSE, SEE, GO, CARRY = "pie-lex-h1ekjwos", "pie-lex-spekjyeti", "pie-lex-h1eyti", "pie-lex-bhereti"
MAN, MIND, FAME = "pie-lex-h2nexr", "pie-lex-menos", "pie-lex-kjlewos"


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


@pytest.fixture(scope="module")
def ix():
    from pie.validate import load_index
    return load_index()


def _passes(text, ix, plan=None):
    """The validator's verdict; a plan's compounds are indexed first, as realize_plans.py does."""
    from pie.validate import index_plan_compounds, validate_text
    if plan:
        index_plan_compounds(ix, plan)
    return validate_text(text, ix)["status"] == "pass"


def V(lex, person=None, tense="PRS", mood="IND"):
    return {"lex_id": lex, "role": "V", "verb": {"tense": tense, "mood": mood, "voice": "ACT", "person": person}}


def _q(slots, **kw):
    return {"english": "x", "clauses": [{"question": True, "slots": slots, **kw}]}


def test_interrogative_adverbs_front_and_validate(lx, ix):
    # wh-adverbs open the clause like the pronouns: kúdʰe (Skt kúha, OCS kъde), kʷóm (Lat. quom), kʷíd 'why'
    # (Ved. kím, Lat. quid, Gk τί), kʷíh₁ 'how' (Lat. quī)
    for key, form in (("where", "kúdʰe"), ("when", "kʷóm"), ("why", "kʷíd"), ("how", "kʷíh₁")):
        r = produce(_q([{"lex_id": HORSE, "role": "SUBJ"}, V(GO),
                        {"lex_id": f"closed:interrogative_adv/{key}", "role": "ADV"}]), lx)
        assert r["pie"] == f"{form} h₁éḱwos h₁éyti?", key
        assert _passes(r["pie"], ix)
    # 'why do you not see?': ne stays before the verb, after the fronted adverb
    r = produce(_q([V(SEE, person=2), {"lex_id": "closed:interrogative_adv/why", "role": "ADV"}], neg=True), lx)
    assert r["pie"] == "kʷíd ne spéḱyesi?"


def test_how_many_takes_a_plural_head_and_fronts(lx, ix):
    # Lat. quot equos, Skt káti: indeclinable, the counted noun plural even with num unset (like a numeral)
    r = produce(_q([{"lex_id": HORSE, "role": "OBJ"},
                    {"lex_id": "closed:interrogative_adv/how_many", "role": "MOD", "head": 0}, V(SEE, person=2)]), lx)
    assert r["pie"] == "kʷóti h₁éḱwons spéḱyesi?"
    assert _passes(r["pie"], ix)
    # the correlatives are not fronted: 'so many horses carry' (Lat. tot), 'as many' h₁yóti (Skt yáti)
    for key, form in (("so_many", "tóti"), ("as_many", "h₁yóti")):
        r = produce({"english": "x", "clauses": [{"slots": [
            {"lex_id": HORSE, "role": "SUBJ"}, {"lex_id": f"closed:correlative_adv/{key}", "role": "MOD", "head": 0},
            V(CARRY)]}]}, lx)
        assert r["pie"] == f"{form} h₁éḱwōs bʰéronti."
        assert _passes(r["pie"], ix)


def test_closed_adverbs_are_checked(lx):
    from pie.realize import check_plan

    def errs(slot):
        return check_plan({"english": "x", "clauses": [{"slots": [slot, V(SEE)]}]}, lx)
    assert any("role ADV" in e for e in errs({"lex_id": "closed:interrogative_adv/why", "role": "OBJ"}))
    assert any("role ADV" in e for e in errs({"lex_id": "closed:interrogative_adv/where", "role": "MOD", "head": 0}))
    assert any("unknown closed id" in e for e in errs({"lex_id": "closed:interrogative_adv/whence", "role": "ADV"}))
    for head in (None, 9):
        assert any("nominal head" in e for e in errs({"lex_id": "closed:interrogative_adv/how_many", "role": "MOD",
                                                      "head": head}))


def test_closed_adverbs_are_the_pronoun_cells_and_lexicon_words(lx):
    """One form per word: why/when are the pronouns' neut./masc. accusatives, the others the lexicon's adverbs."""
    c = lx.closed
    assert c["interrogative_adv"]["why"][0] == c["interrogative_kwi"]["n"]["ACC.SG"][0] == "kʷíd"
    assert c["interrogative_adv"]["when"][0] == c["interrogative_kwo"]["m"]["ACC.SG"][0] == "kʷóm"
    assert c["interrogative_adv"]["how"][0] == c["interrogative_kwi"]["mf"]["INS.SG"][0]
    for key, lid in (("interrogative_adv/where", "pie-lex-kudhe"), ("interrogative_adv/how", "pie-lex-kwih1"),
                     ("interrogative_adv/how_many", "pie-lex-kwoti"), ("correlative_adv/so_many", "pie-lex-toti")):
        sec, k = key.split("/")
        assert c[sec][k][0] == lx.entries[lid]["form"], key
    # every new form is cited
    for sec in ("interrogative_adv", "correlative_adv"):
        for k in c[sec]:
            if not k.startswith("_"):
                assert f"{sec}/{k}" in c["_refs"], (sec, k)


def test_make_slice_offers_the_closed_adverbs_once(lx):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_slice
    from pie.realize import closed_adverb_ids
    ids = closed_adverb_ids(lx)
    assert {"closed:interrogative_adv/why", "closed:interrogative_adv/how_many",
            "closed:correlative_adv/as_many"} <= set(ids)
    assert set(ids) <= set(make_slice.CLOSED)
    # the lexicon adverbs with the same form leave the adverb list (one word, one id); kʷór, kú stay
    advs = {a["lex_id"] for a in make_slice.slice_adverbs(lx, lambda i: len(lx.entries[i].get("reflexes", {})), 80)}
    assert not advs & {"pie-lex-kudhe", "pie-lex-kwih1", "pie-lex-kwoti", "pie-lex-toti"}
    assert "pie-lex-kwor" in advs
    # 'which of two', 'dear', 'healthy' pass the slice gates, so CONVERSATION puts them in every slice
    for i in make_slice.CONVERSATION:
        assert lx.specs[i]["usable"] and i not in lx.blocked and make_slice.planner_accent_ok(lx, i), i


def _name(first, second, role="SUBJ", gender="m"):
    return {"lex_id": "compound", "compound": {"first": first, "second": second, "type": "bahuvrihi"},
            "role": role, "gender": gender}


def test_dithematic_names_as_nouns(lx, ix):
    # *h₁su-ḱléwes- 'Good-Fame' (Ved. Suśrávas-, Av. Haosravah-, Gk Εὐκλῆς; West 2007 ch. 10) as a subject
    # and in address; *h₁wesu-ḱléwes- (Illyr. Vescleves-); a feminine thematic name in -eh₂
    p = {"english": "x", "clauses": [{"slots": [_name("closed:prefix/h1su", FAME), V(SEE)]}]}
    r = produce(p, lx)
    assert r["pie"] == "h₁suḱléwēs spéḱyeti." and _passes(r["pie"], ix, p)
    r = produce({"english": "x", "clauses": [{"slots": [_name("closed:prefix/h1su", FAME, "VOC"), V(SEE, person=2)]}]},
                lx)
    assert r["pie"] == "h₁súḱlewes spéḱyesi."
    r = produce({"english": "x", "clauses": [{"slots": [_name("pie-lex-h1wesus", FAME, "OBJ"), V(SEE)]}]}, lx)
    assert r["pie"] == "h₁wesuḱléwesm̥ spéḱyeti."
    r = produce({"english": "x", "clauses": [{"slots": [_name("closed:prefix/h1su", HORSE, gender="f"), V(SEE)]}]},
                lx)
    assert r["pie"] == "h₁suh₁éḱweh₂ spéḱyeti."


def test_h2ner_names_compose_in_the_zero_grade(lx, ix):
    # *h₂nr̥-mén-es- (Ved. nṛmáṇas-, Av. Nərəmanah-, Gk Ἀνδρομένης): zero grade, second-member accent;
    # other consonant stems are still rejected
    from pie.compound import CompoundError, resolve
    c = resolve({"first": MAN, "second": MIND, "type": "bahuvrihi"}, lx)
    assert c.cells("m")["NOM.SG"][0] == "h₂nr̥ménēs"
    p = {"english": "x", "clauses": [{"slots": [_name(MAN, MIND), V(SEE)]}]}
    r = produce(p, lx)
    assert r["pie"] == "h₂nr̥ménēs spéḱyeti." and _passes(r["pie"], ix, p)
    with pytest.raises(CompoundError):
        resolve({"first": "pie-lex-dyexws", "second": FAME, "type": "bahuvrihi"}, lx)


def test_greeting_constructions_of_the_brief(lx, ix):
    """planner-brief-v4 'Greetings and thanks': no reconstructed formula, only daughter-text constructions built
    from slice words (make_slice.CONVERSATION): VOC + IMP 'come!' (Ved. ā́ gahi), 'be whole!' (Goth. hails),
    'be dear to us' (Od. 1.123), the optative wish 'may the gods give you good things' (Od. 24.402)."""
    def VV(lex, tense, mood, person=None):
        return {"lex_id": lex, "role": "V", "verb": {"tense": tense, "mood": mood, "voice": "ACT", "person": person}}
    guest, dear, good = "pie-lex-ghostis", "pie-lex-priHos", "pie-lex-h1wesus"
    cases = [
        ([{"lex_id": guest, "role": "VOC"}, {"lex_id": dear, "role": "MOD", "head": 0},
          VV("pie-lex-gwemt", "AOR", "IMP", 2)], "príHe gʰóstey gʷm̥dʰí."),
        ([{"lex_id": "pie-lex-keh2ilos", "role": "PRED"}, VV("pie-lex-h1esti", "PRS", "IMP", 2)], "kéh₂ilos h₁sdʰí."),
        ([{"lex_id": guest, "role": "VOC"}, {"lex_id": "closed:personal/1", "role": "IO", "num": "PL"},
          {"lex_id": dear, "role": "PRED"}, VV("pie-lex-h1esti", "PRS", "IMP", 2)], "gʰóstey n̥sméy priHós h₁sdʰí."),
        ([{"lex_id": "pie-lex-deywos", "role": "SUBJ", "num": "PL"},
          {"lex_id": "closed:personal/2", "role": "IO", "enclitic": True},
          {"lex_id": good, "role": "OBJ", "num": "PL", "gender": "n"}, VV("pie-lex-deh3t", "AOR", "OPT")],
         "deywṓs toy h₁wésuh₂ dh₃ih₁ént."),
    ]
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_slice
    for slots, pie in cases:
        r = produce({"english": "x", "clauses": [{"slots": slots}]}, lx)
        assert r["pie"] == pie and _passes(r["pie"], ix), pie
        for s in slots:
            if s["lex_id"].startswith("pie-lex-") and s["lex_id"] not in make_slice.CORE_NOUNS:
                assert s["lex_id"] in make_slice.CONVERSATION or s["lex_id"] == "pie-lex-h1esti", s["lex_id"]
