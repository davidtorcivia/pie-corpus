"""Vocabulary round 5 (docs/audits/lexicon-gaps-round5-2026-10-31.md): h₂élyos 'other' a pronominal adjective,
the gʷṓws gender warning, lexq's plural lookup, and the round's idioms. Plans run through
tests/helpers.produce (check_plan, then realize), warnings through plan_warnings as realize_plans.py calls it."""

import importlib.util
from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")

OTHER, COW, WHITE = "pie-lex-h2elyos", "pie-lex-gwoxws", "pie-lex-albhos"
DAUGHTER, MAN, CARRY = "pie-lex-dhugh2texr", "pie-lex-wiHros", "pie-lex-bhereti"
V = {"lex_id": CARRY, "role": "V"}

_spec = importlib.util.spec_from_file_location("lexq", ROOT / "scripts" / "lexq.py")
lexq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lexq)


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


def _one(slots, lx, english="x"):
    return produce({"english": english, "clauses": [{"slots": slots}]}, lx)


# --- h₂élyos 'other': a pronominal adjective (neuter in -od) ------------------------------------------------

def test_pronominal_adjective_cells():
    from pie.morph import AdjSpec, decline_adj, spec_dict
    plain, pron = decline_adj(AdjSpec("h₂élyo")), decline_adj(AdjSpec("h₂élyo", pronominal=True))
    for feat in ("NOM.SG", "ACC.SG", "VOC.SG"):
        assert pron["n"][feat] == ["h₂élyod"] and plain["n"][feat] == ["h₂élyom"]
    # only the neuter direct cases differ: the rest is an ordinary o/eh₂ adjective (Ringe 2006 p. 55)
    assert {g: {k: v for k, v in c.items() if not (g == "n" and k in ("NOM.SG", "ACC.SG", "VOC.SG"))}
            for g, c in pron.items()} == \
           {g: {k: v for k, v in c.items() if not (g == "n" and k in ("NOM.SG", "ACC.SG", "VOC.SG"))}
            for g, c in plain.items()}
    # stored only when set, so no other row of inflection_specs.jsonl changes
    assert "pronominal" not in spec_dict(AdjSpec("h₂élyo"))
    assert spec_dict(AdjSpec("h₂élyo", pronominal=True))["pronominal"] is True


def test_other_is_an_adjective(lx):
    assert lx.specs[OTHER]["family"] == "adj" and lx.specs[OTHER]["spec"]["pronominal"] is True
    # 'another girl' (t090): a feminine head takes h₂élyeh₂
    r = _one([{"lex_id": DAUGHTER, "role": "SUBJ"}, {"lex_id": OTHER, "role": "MOD", "head": 0}, V], lx)
    assert r["pie"].startswith("h₂élyeh₂ dʰugh₂tḗr ")
    # 'something else' (neuter, as a noun): h₂élyod, Lat. aliud, Gk ἄλλο
    r = _one([{"lex_id": OTHER, "role": "OBJ", "gender": "n"}, V], lx)
    assert r["pie"].startswith("h₂élyod ")
    # masculine uses come out as before (the old noun spec): 'other men' h₂élyōs wiHrṓs
    r = _one([{"lex_id": MAN, "role": "SUBJ", "num": "PL"}, {"lex_id": OTHER, "role": "MOD", "head": 0}, V], lx)
    assert r["pie"].startswith("h₂élyōs wiHrṓs ")
    r = _one([{"lex_id": OTHER, "role": "SUBJ", "gender": "m"}, V], lx)
    assert r["pie"].startswith("h₂élyos ")


def test_other_as_a_noun_needs_a_gender(lx):
    from pie.realize import check_plan
    errs = check_plan({"english": "Another carries.", "clauses": [{"slots": [{"lex_id": OTHER, "role": "SUBJ"}, V]}]},
                      lx)
    assert any("needs a gender" in e for e in errs)


# --- gʷṓws 'cattle': masculine in the engine, a cow is the slot gender f (lead decision, round 5) -------------

def _cows(anaphor_gender, cow_gender=None):
    cow = {"lex_id": COW, "role": "SUBJ", "num": "PL", **({"gender": cow_gender} if cow_gender else {})}
    return {"english": "The cows were in the field. The boy drove them home.", "clauses": [
        {"slots": [cow, {"lex_id": "pie-lex-h2egjros", "role": "LOC"},
                   {"lex_id": "pie-lex-h1esti", "role": "V", "verb": {"tense": "PST"}}]},
        {"break": True, "slots": [{"lex_id": "closed:demonstrative_so", "role": "OBJ", "gender": anaphor_gender,
                                   "num": "PL"},
                                  {"lex_id": "pie-lex-doxm", "role": "GOAL"},
                                  {"lex_id": "pie-lex-h2egjeti", "role": "V", "verb": {"tense": "PST"}}]}]}


def test_cattle_stay_masculine_a_cow_is_slot_gender_f(lx):
    assert lx.gender(COW) == "m"                      # common gender in the daughters; the feminine default reverted
    r = _one([{"lex_id": COW, "role": "SUBJ"}, {"lex_id": WHITE, "role": "MOD", "head": 0}, V], lx)
    assert r["pie"].startswith("albʰós gʷṓws ")
    r = _one([{"lex_id": COW, "role": "SUBJ", "gender": "f"}, {"lex_id": WHITE, "role": "MOD", "head": 0}, V], lx)
    assert r["pie"].startswith("albʰéh₂ gʷṓws ")


def test_pronoun_of_another_gender_for_ungendered_cattle_warns(lx):
    from pie.realize import plan_warnings
    warn = lambda p: [w for w in plan_warnings(p, lx) if "has no gender" in w]
    # 'them' f for cows whose slot has no gender (so m): warn, naming the slot to fix
    assert "tā́s" in produce(_cows("f"), lx)["pie"].split()
    w = warn(_cows("f"))
    assert len(w) == 1 and 'set "gender": "f" on that slot' in w[0] and "clause 0 slot 0" in w[0]
    # consistent plans do not warn: both f, or both m
    assert not warn(_cows("f", cow_gender="f")) and not warn(_cows("m"))
    assert not [x for x in plan_warnings(_cows("f", cow_gender="f"), lx) if "matches no referent" in x]


# --- lexq: a plural finds its singular ------------------------------------------------------------------------

def test_plural_query_finds_the_singular(lx):
    ids, uses = lexq.pool(lx, False), lexq.corpus_uses()
    hits = [h["lex_id"] for h in lexq.search("tears", lx, ids, uses, 8)]
    assert "pie-lex-dakjru" in hits and "pie-lex-h2ekjru" in hits
    assert lexq.singular("grass") == "grass" and lexq.singular("cows") == "cow"


# --- the round's idioms ---------------------------------------------------------------------------------------

def test_round5_idioms(lx):
    ids = set(lexq.pool(lx, False))
    for q in ("bull", "ox", "with two hands", "teach me to", "cow"):
        es = lexq.idioms(q)
        assert es, q
        for e in es:
            for i in e["ids"]:
                assert i in ids or i.startswith("closed:"), (q, i)       # every id is a word the planner may use
    assert lexq.idioms("bull")[0]["ids"][0] == "pie-lex-uksexn"


def test_dual_oblique_idiom_plan(lx):
    # 'he carries it with two hands': the plural instrumental, no numeral (the oblique dual is not reconstructable)
    r = _one([{"lex_id": "pie-lex-gjhesoxr", "role": "INS", "num": "PL"}, V], lx)
    assert r["pie"] == "ǵʰesr̥bʰís bʰéreti."


def test_teach_me_to_idiom_plans(lx):
    imp = {"tense": "AOR", "mood": "IMP", "voice": "ACT", "person": 2, "num": "SG"}
    me = {"lex_id": "closed:personal/1", "role": "OBJ", "enclitic": True}
    # the dative of a -tu- verbal noun (Ved. pā́tave type): 'teach me to cross'
    r = _one([me, {"lex_id": "pie-lex-kjeHst", "role": "V", "verb": imp}, {"lex_id": "pie-lex-pertus", "role": "IO"}],
             lx)
    assert r["pie"] == "pr̥téwey me ḱHsdʰí."
    # otherwise parataxis: the imperative, then the verb in the 1st-person subjunctive ('teach me: I shall swim')
    r = produce({"english": "Teach me to swim.", "clauses": [
        {"slots": [me, {"lex_id": "pie-lex-kjeHst", "role": "V", "verb": imp}]},
        {"slots": [{"lex_id": "pie-lex-sneh2ti", "role": "V",
                    "verb": {"tense": "PRS", "mood": "SBJV", "voice": "ACT", "person": 1, "num": "SG"}}]}]}, lx)
    assert r["pie"] == "ḱHsdʰí me snéh₂oh₂."


def test_round5_words_are_found(lx):
    """Round-5 rung-1 fixes: the planners' concepts now find the lexeme first, with the cells checked by hand."""
    ids, uses = lexq.pool(lx, False), lexq.corpus_uses()
    first = lambda t: lexq.search(t, lx, ids, uses, 3)[0]["lex_id"]
    for term, want in [("face", "pie-lex-h1enih3kwo"), ("holy", "pie-lex-sh2kros"), ("month", "pie-lex-mexh1ns"),
                       ("bellows", "pie-lex-bholgjhis"), ("axle", "pie-lex-h2ekjs"), ("slow", "pie-lex-gwerdus"),
                       ("roast", "pie-lex-bhrgjyeti"), ("worship", "pie-lex-h1yagjeti"), ("anvil", "pie-lex-h2ekjmox"),
                       ("howl", "pie-lex-HrewdHti"), ("age", "pie-lex-h2oyu"), ("generation", "pie-lex-gjenh1eseh2"),
                       ("pray", "pie-lex-gwhedhyeti"), ("host", "pie-lex-ghostipotis"), ("right", "pie-lex-dekjsiwos"),
                       ("other", OTHER)]:
        assert first(term) == want, term
    c = lx.admissible_cells
    assert c("pie-lex-h1enih3kwo")["NOM.SG"][0] == "h₁énih₃kʷom" and lx.gender("pie-lex-h1enih3kwo") == "n"
    assert c("pie-lex-mexh1ns")["NOM.SG"][0] == "mḗh₁n̥s" and c("pie-lex-mexh1ns")["GEN.SG"][0] == "méh₁nsos"
    assert c("pie-lex-h2ekjs")["NOM.SG"][0] == "h₂éḱsis" and c("pie-lex-bholgjhis")["ACC.SG"][0] == "bʰólǵʰim"
    assert lx.admissible_cells("pie-lex-gwerdus", "m")["NOM.SG"][0] == "gʷr̥dús"
    assert lx.admissible_cells("pie-lex-sh2kros", "f")["NOM.SG"][0] == "sh₂kréh₂"
    # gloss-only fixes keep the first sense, so the token gloss lines of corpus records do not change
    assert lx.gloss("pie-lex-h2oyu") == "long.time" and lx.gloss("pie-lex-ghostipotis") == "lord"
