"""Vocabulary round 6 (docs/audits/lexicon-gaps-round6-2026-11-01.md): the four lexicon fixes (lexq ids, the
one-branch 'bridge', woǵʰéyeti causative only, gʷr̥Htós 'welcome'), the word-search check, the mare, móḱs, the new
glosses and the round's idioms. Plans run through tests/helpers.produce (check_plan, then realize), warnings through
plan_warnings as realize_plans.py calls it."""

import importlib.util
import json
from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "data/morph/inflection_specs.jsonl").exists(), reason="specs not built")

H, MAN, COW, V = "pie-lex-h1ekjwos", "pie-lex-wiHros", "pie-lex-gwoxws", {"lex_id": "pie-lex-bhereti", "role": "V"}
GO = {"lex_id": "pie-lex-gwmyeti", "role": "V"}
IDIOMS = json.loads((ROOT / "data/lexicon/idioms.json").read_text("utf-8"))["idioms"]

_spec = importlib.util.spec_from_file_location("lexq", ROOT / "scripts" / "lexq.py")
lexq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lexq)


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


@pytest.fixture(scope="module")
def pool(lx):
    return lexq.pool(lx, False)


def _one(slots, lx, **clause):
    return produce({"english": "x", "clauses": [{"slots": slots, **clause}]}, lx)


def _first(term, lx, pool, n=3):
    return [h["lex_id"] for h in lexq.search(term, lx, pool, lexq.corpus_uses(), n)]


# --- fix 1: lexq --id names the id to use (t096: sleh2gwt, gjhlh2dhros) --------------------------------------

def test_lexq_id_for_a_word_planners_cannot_use(lx, pool):
    from pie.realize import check_plan
    # the bare stem has no usable spec: an error, and the aorist that the planners may use
    r = lexq.lookup_id("pie-lex-sleh2gwt", lx, pool)
    assert "error" in r and "cells" not in r and r["use"] == ["pie-lex-sleh2gwt-2"]
    # an id typed from the form (ǵʰ for gʰ): unknown, and the real id
    r = lexq.lookup_id("pie-lex-gjhlh2dhros", lx, pool)
    assert r["error"] == "unknown id" and r["use"] == ["pie-lex-ghlh2dhros"]
    # both suggestions are what the engine accepts
    for i, role in (("pie-lex-sleh2gwt-2", "V"), ("pie-lex-ghlh2dhros", "PRED")):
        slots = [{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": i, "role": role, **({"verb": {"tense": "AOR"}}
                                                                               if role == "V" else {})}]
        assert not check_plan({"english": "x", "clauses": [{"type": "nominal" if role == "PRED" else "verbal",
                                                             "slots": slots}]}, lx)
    # an offered word still comes back in full
    assert lexq.lookup_id("pie-lex-bhereti", lx, pool)["cells"]["PRS.3SG"] == ["bʰéreti"]


# --- fix 2: tl̥h₂tóm 'bridge' is Baltic only ------------------------------------------------------------------

def test_bridge_is_marked_one_branch(lx):
    assert lx.gloss("pie-lex-tlh2tom") == "bridge"            # gloss lines of the 5 corpus records unchanged
    assert lx.meaning("pie-lex-tlh2tom")[0] == "bridge"         # 'ford' dropped; no caveat sense for the translator
    assert "Baltic" in lx.entries["pie-lex-tlh2tom"]["override_note"]
    e = lexq.idioms("bridge")                                   # lexq prints the caveat with the word
    assert e and {"pie-lex-tlh2tom", "pie-lex-pertus"} <= set(e[0]["ids"]) and "one branch" in e[0]["how"]


# --- fix 3: woǵʰéyeti is a causative ---------------------------------------------------------------------------

def test_wogjheyeti_is_causative_only(lx):
    from pie.realize import check_plan
    item = lexq.ms.slice_item(lx, "pie-lex-wogjheyeti")
    assert "causative only" in item["gloss"] and item["valency"] == "tr"
    errs = check_plan({"english": "x", "clauses": [{"slots": [{"lex_id": MAN, "role": "SUBJ"},
                                                              {"lex_id": "pie-lex-wogjheyeti", "role": "V"}]}]}, lx)
    assert any("transitive" in e for e in errs)


# --- fix 4: 'welcome' is not gʷr̥Htós (the in-world brief) -------------------------------------------------------

def test_welcome_agrees_with_the_in_world_brief(lx):
    brief = (ROOT / "docs/generation/planner-brief-dialogue-inworld.md").read_text("utf-8")
    assert "never gʷr̥Htós" in brief
    assert "welcome" not in lx.meaning("pie-lex-gwrHtos")[0] and lx.gloss("pie-lex-gwrHtos") == "praised"
    # no idiom offers gʷr̥Htós for 'welcome'
    for e in IDIOMS:
        if "welcome" in e["idiom"] or any("welcome" in k for k in e["english"]):
            assert "pie-lex-gwrHtos" not in e["ids"], e["english"]
    w = lexq.idioms("welcome")
    assert w and "priHós" in w[0]["idiom"]
    np = {"english": "Welcome, guest!", "clauses": [{"type": "np", "case": "VOC", "slots": [
        {"lex_id": "pie-lex-ghostis", "role": "NP"}, {"lex_id": "pie-lex-priHos", "role": "MOD", "head": 0}]}]}
    assert produce(np, lx)["pie"] == "príHe gʰóstey."


# --- the word-search check: judge, oath, swear, witness, every, each ------------------------------------------

def test_word_search_for_the_law_words(lx, pool):
    assert {"pie-lex-h1oytos", "pie-lex-bhoydheh2"} <= set(_first("oath", lx, pool))
    assert "pie-lex-h3mneh3ti" in _first("swear", lx, pool)
    assert _first("law", lx, pool)[0] == "pie-lex-h2yewos"     # before the in-law words
    for q in ("judge", "witness", "each"):                     # no word: the idiom answers
        assert lexq.idioms(q), q
    assert _first("every", lx, pool) == ["pie-lex-solh2wos"]
    # solh₂wós is an adjective (994f7fc): the idiom no longer says it cannot be a MOD
    e = lexq.idioms("each")[0]
    assert "NOUN" not in e["how"] and "MOD" in e["how"] and lx.specs["pie-lex-solh2wos"]["family"] == "adj"
    assert _one([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "pie-lex-solh2wos", "role": "MOD", "head": 0}, V],
                lx)["pie"] == "solh₂wós wiHrós bʰéreti."


def test_gloss_side_plural(lx, pool):
    # 'ash' finds kónHis 'ashes, dust' (t100); a gloss's plural no longer hides it
    assert _first("ash", lx, pool)[0] == "pie-proj-konHis"
    assert lexq.gloss_words("ashes, dust") >= {"ash", "ashes", "dust"}


# --- the mare ----------------------------------------------------------------------------------------------------

def test_mare(lx, pool):
    assert "pie-lex-h1ekjweh2" in pool and _first("mare", lx, pool)[0] == "pie-lex-h1ekjweh2"
    assert lx.gender("pie-lex-h1ekjweh2") == "f"
    r = _one([{"lex_id": "pie-lex-h1ekjweh2", "role": "SUBJ"}, {"lex_id": "pie-lex-albhos", "role": "MOD", "head": 0},
              {"lex_id": "pie-lex-tekweti", "role": "V"}], lx)
    assert r["pie"] == "albʰéh₂ h₁éḱweh₂ tékʷeti."


# --- soon: móḱs ---------------------------------------------------------------------------------------------------

def test_soon_is_accented(lx, pool):
    from pie.validate import load_index, validate_text
    assert lx.entries["pie-lex-mokjs"]["form"] == "móḱs" and "moḱs" in lx.entries["pie-lex-mokjs"]["variants"]
    assert "soon" in lx.meaning("pie-lex-mokjs")[0] and lx.gloss("pie-lex-mokjs") == "quickly"
    r = _one([{"lex_id": "pie-lex-mokjs", "role": "ADV"}, GO], lx)
    assert r["pie"] == "móḱs gʷm̥yéti."
    v = validate_text(r["pie"], load_index())
    assert v["status"] == "pass" and not v["accentless"]      # the lint no longer calls it an accent defect


# --- rung 1: the new glosses find their word, and the first senses (gloss lines) did not move -----------------------

def test_round6_words_are_found(lx, pool):
    for term, want in [("law", "pie-lex-h2yewos"), ("enough", "pie-lex-seh2tis"), ("oar", "pie-lex-h1erh1trom"),
                       ("bake", "pie-lex-pekweti"), ("graze", "pie-lex-peh2skjeti"), ("clay", "pie-lex-dheygjhti"),
                       ("grandfather", "pie-lex-h2ewh2os"), ("loud", "pie-lex-klh1ros"), ("can", "pie-lex-memoghe"),
                       ("mare", "pie-lex-h1ekjweh2")]:
        assert _first(term, lx, pool)[0] == want, term
    assert "pie-lex-leh2yeti" in _first("bark", lx, pool, 2)       # beside lowbʰós 'bark (of a tree)'
    assert "pie-lex-dheh1mn" in _first("law", lx, pool)
    assert any(h["lex_id"] == "pie-lex-posti" for h in lexq.search("behind", lx, pool, lexq.corpus_uses(), 3))
    for i, g in [("pie-lex-tlh2tom", "bridge"), ("pie-lex-gwrHtos", "praised"), ("pie-lex-h2ewh2os", "maternal.grandfather"),
                 ("pie-lex-mokjs", "quickly"), ("pie-lex-pekweti", "be.cooking"), ("pie-lex-posti", "after"),
                 ("pie-lex-dheh1mn", "that.which.is.established"), ("pie-lex-memoghe", "have.power")]:
        assert lx.gloss(i) == g, i


def test_round6_cells(lx):
    c = lx.admissible_cells
    assert c("pie-lex-h2yewos")["NOM.SG"] == ["h₂yéwos"] and lx.gender("pie-lex-h2yewos") == "n"
    assert c("pie-lex-seh2tis")["GEN.SG"][0] == "sh₂téys" and lx.gender("pie-lex-seh2tis") == "f"
    assert c("pie-lex-h1erh1trom")["NOM.SG"] == ["h₁érh₁trom"]
    assert c("pie-lex-leh2yeti")["PRS.3SG"] == ["léh₂yeti"]
    assert _one([{"lex_id": "pie-lex-kjwox", "role": "SUBJ"}, {"lex_id": "pie-lex-leh2yeti", "role": "V"}],
                lx)["pie"] == "ḱwṓ léh₂yeti."
    # kl̥h₁rós is an adjective now (it had a masculine noun spec): it agrees
    assert lx.specs["pie-lex-klh1ros"]["family"] == "adj" and c("pie-lex-klh1ros", "f")["NOM.SG"] == ["kl̥h₁réh₂"]
    # peh₂sḱéti 'pasture' is transitive; the cattle graze in the middle
    assert lexq.ms.slice_item(lx, "pie-lex-peh2skjeti")["valency"] == "tr"


# --- the round's idioms ------------------------------------------------------------------------------------------------

def _round6_entries():
    return [e for e in IDIOMS if "round 6" in e["source"]]


def test_round6_idiom_ids_are_planner_words(lx, pool):
    adverbs = {e["lex_id"] for e in lexq.ms.slice_adverbs(lx, lambda i: lexq.ms.attested_in(lx, i), n=10_000)}
    ok = set(pool) | adverbs
    assert len(_round6_entries()) >= 35
    for e in _round6_entries():
        for i in e["ids"]:
            assert i in ok or i.startswith("closed:"), (e["english"][0], i)    # no coinage, nothing unoffered
        assert "pie-neo" not in json.dumps(e["ids"])


DECAD = "pie-lex-dekjmt"
IDIOM_PLANS = [
    # numerals: 'N tens' (Ringe 2006 p. 53), the teens 'ten and two'
    ([{"lex_id": DECAD, "role": "OBJ"}, {"lex_id": "closed:numerals/2", "role": "MOD", "head": 0},
      {"lex_id": H, "role": "POSS", "head": 0, "num": "PL"}, V], "dwóyh₁ h₁éḱwōm déḱm̥tih₁ bʰéreti."),
    ([{"lex_id": DECAD, "role": "OBJ"}, {"lex_id": "closed:numerals/3", "role": "MOD", "head": 0},
      {"lex_id": H, "role": "POSS", "head": 0, "num": "PL"}, V], "tríh₂ h₁éḱwōm déḱm̥th₂ bʰéreti."),
    ([{"lex_id": DECAD, "role": "OBJ"}, {"lex_id": "closed:numerals/indeclinable/5", "role": "MOD", "head": 0},
      {"lex_id": H, "role": "POSS", "head": 0, "num": "PL"}, V], "pénkʷe h₁éḱwōm déḱm̥th₂ bʰéreti."),
    ([{"lex_id": DECAD, "role": "OBJ"}, {"lex_id": "closed:numerals/2", "role": "MOD", "head": 0},
      {"lex_id": H, "role": "POSS", "head": 0, "num": "PL"},
      {"lex_id": "closed:numerals/indeclinable/5", "role": "OBJ", "and": True}, V],
     "dwóyh₁ h₁éḱwōm déḱm̥tih₁ pénkʷe-kʷe bʰéreti."),
    ([{"lex_id": DECAD, "role": "SUBJ"}, {"lex_id": "closed:numerals/3", "role": "MOD", "head": 0},
      {"lex_id": H, "role": "POSS", "head": 0, "num": "PL"}, {"lex_id": "pie-lex-sesti", "role": "V"}],
     "tríh₂ h₁éḱwōm déḱm̥th₂ sésti."),
    ([{"lex_id": H, "role": "OBJ"}, {"lex_id": "closed:numerals/indeclinable/10", "role": "MOD", "head": 0},
      {"lex_id": "closed:numerals/2", "role": "OBJ", "gender": "m", "and": True}, V], "déḱm̥ h₁éḱwons dwóh₁-kʷe bʰéreti."),
    # every / all
    ([{"lex_id": COW, "role": "OBJ", "num": "PL", "gender": "f"}, {"lex_id": "pie-lex-solh2wos", "role": "MOD", "head": 0},
      V], "solh₂wā́s gʷṓs bʰéreti."),
    ([{"lex_id": "pie-lex-solh2wos", "role": "SUBJ", "gender": "m", "num": "PL"},
      {"lex_id": "pie-lex-gwemt", "role": "V", "verb": {"tense": "AOR"}}], "solh₂wṓs gʷmént."),
    # enough, law, bread, must, hope, can
    ([{"lex_id": "pie-lex-seh2tis", "role": "SUBJ"}, {"lex_id": "pie-lex-dhoHneh2", "role": "POSS", "head": 0},
      {"lex_id": "pie-lex-h1esti", "role": "V"}], "dʰoHnéh₂s séh₂tis h₁ésti."),
    ([{"lex_id": "pie-lex-h2yewos", "role": "OBJ"}, {"lex_id": "pie-lex-deykjeti", "role": "V"}], "h₂yéwos déyḱeti."),
    ([{"lex_id": "pie-lex-dhoHneh2", "role": "OBJ"}, {"lex_id": "pie-lex-pekweti", "role": "V"}], "dʰoHnéh₂m pékʷeti."),
    ([{"lex_id": "pie-lex-h1eyti", "role": "V", "verb": {"mood": "IMP", "person": 3, "num": "SG"}}], "h₁éytu."),
    ([{"lex_id": "pie-lex-gwemt", "role": "V", "verb": {"tense": "AOR", "mood": "OPT", "person": 3, "num": "SG"}}],
     "gʷm̥yéh₁t."),
    ([{"lex_id": "pie-lex-memoghe", "role": "V", "verb": {"tense": "PRF", "person": 1, "num": "SG"}}], "memógʰh₂e."),
    ([{"lex_id": "closed:demonstrative_so", "role": "OBJ", "gender": "n"},
      {"lex_id": "pie-lex-bhereti", "role": "V", "verb": {"mood": "OPT", "person": 1, "num": "SG"}}], "tód bʰéroyh₁m̥."),
    # the last (remaining) cow, sickness, healer, nurse, potter, singer, coward, winner
    ([{"lex_id": COW, "role": "OBJ", "gender": "f"}, {"lex_id": "pie-lex-loykwos", "role": "MOD", "head": 0}, V],
     "loykʷéh₂m gʷṓm bʰéreti."),
    ([{"lex_id": "pie-proj-swerghos", "role": "SUBJ"}, {"lex_id": MAN, "role": "OBJ"},
      {"lex_id": "pie-lex-segjheti", "role": "V"}], "swérgʰos wiHróm séǵʰeti."),
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "pie-lex-mexdeti", "role": "MOD", "head": 0,
                                        "participle": {"voice": "ACT"}}, GO], "mḗdonts wiHrós gʷm̥yéti."),
    ([{"lex_id": "pie-lex-gwexn", "role": "SUBJ"}, {"lex_id": "pie-lex-dheh1yeti", "role": "MOD", "head": 0,
                                                    "participle": {"voice": "ACT"}}, GO], "dʰéh₁yontih₂ gʷḗn gʷm̥yéti."),
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "pie-lex-dheygjhti", "role": "MOD", "head": 0,
                                        "participle": {"voice": "ACT"}}, GO], "dʰiǵʰónts wiHrós gʷm̥yéti."),
    ([{"lex_id": "pie-lex-dhegjhoxm", "role": "OBJ"}, {"lex_id": "pie-lex-dheygjhti", "role": "V"}], "dʰéǵʰōm dʰéyǵʰti."),
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "pie-lex-gweHyeti", "role": "MOD", "head": 0,
                                        "participle": {"voice": "ACT"}}, GO], "gʷéHyonts wiHrós gʷm̥yéti."),
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "pie-lex-treseti", "role": "MOD", "head": 0,
                                        "participle": {"voice": "ACT"}},
      {"lex_id": "pie-lex-bhewgt-3", "role": "V", "verb": {"tense": "AOR"}}], "trésonts wiHrós bʰéwgt."),
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "pie-lex-segjheti", "role": "MOD", "head": 0,
                                        "participle": {"voice": "ACT"}}, GO], "séǵʰonts wiHrós gʷm̥yéti."),
    # kind / cruel (bahuvrihis), full moon, mud, the father's brother, thatch, manner adverbs, faster
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "compound", "role": "MOD", "head": 0, "compound": {
        "first": "closed:prefix/h1su", "second": "pie-lex-menos", "type": "bahuvrihi"}}, GO], "h₁suménēs wiHrós gʷm̥yéti."),
    ([{"lex_id": MAN, "role": "SUBJ"}, {"lex_id": "compound", "role": "MOD", "head": 0, "compound": {
        "first": "closed:prefix/dus", "second": "pie-lex-menos", "type": "bahuvrihi"}}, GO], "dusménēs wiHrós gʷm̥yéti."),
    ([{"lex_id": "pie-lex-lowksneh2", "role": "SUBJ"}, {"lex_id": "pie-lex-plh1nos", "role": "MOD", "head": 0},
      {"lex_id": "pie-lex-sesti", "role": "V"}], "pl̥h₁néh₂ lówksneh₂ sésti."),
    ([{"lex_id": "pie-lex-dhegjhoxm", "role": "OBJ"}, {"lex_id": "pie-lex-h1wersos", "role": "MOD", "head": 0}, V],
     "h₁werséh₂m dʰéǵʰōm bʰéreti."),
    ([{"lex_id": "pie-lex-bhreh2texr", "role": "SUBJ"}, {"lex_id": "pie-lex-ph2texr", "role": "POSS", "head": 0}, GO],
     "ph₂trés bʰréh₂tēr gʷm̥yéti."),
    ([{"lex_id": "pie-lex-stegos", "role": "OBJ"}, {"lex_id": "pie-lex-ghreh1mn", "role": "INS"},
      {"lex_id": "pie-lex-stegeti", "role": "V"}], "stégos gʰr̥h₁ménh₁ stégeti."),
    ([{"lex_id": "pie-lex-h3regjtos", "role": "GOAL", "gender": "n"}, {"lex_id": "pie-lex-mlewHti", "role": "V"}],
     "h₃reǵtóm mléwHti."),
    ([{"lex_id": "pie-lex-klh1ros", "role": "GOAL", "gender": "n"}, {"lex_id": "pie-lex-mlewHti", "role": "V"}],
     "kl̥h₁róm mléwHti."),
    ([{"lex_id": "pie-lex-HeHkjus", "role": "GOAL", "gender": "n", "degree": "CMP"},
      {"lex_id": "pie-lex-tekweti", "role": "V", "verb": {"tense": "PST"}}], "HéHḱyos tékʷet."),
    # graze (middle), pasture (active)
    ([{"lex_id": COW, "role": "SUBJ", "num": "PL", "gender": "f"},
      {"lex_id": "pie-lex-peh2skjeti", "role": "V", "verb": {"voice": "MID"}}], "gʷówes peh₂sḱóntor."),
    ([{"lex_id": COW, "role": "OBJ", "num": "PL"}, {"lex_id": "pie-lex-peh2skjeti", "role": "V"}], "gʷṓs peh₂sḱéti."),
]


@pytest.mark.parametrize("slots,pie", IDIOM_PLANS)
def test_round6_idiom_plans(slots, pie, lx):
    """Every PIE form a round-6 idiom's `how` gives is the engine's output for its plan, with no warning."""
    from pie.realize import plan_warnings
    plan = {"english": "x", "clauses": [{"slots": slots}]}
    assert produce(plan, lx)["pie"] == pie
    assert not plan_warnings(plan, lx)
    stem = pie.rstrip(".").split()[0]
    assert any(stem in e["how"] for e in _round6_entries()), pie     # the idiom shows this form


def test_you_are_dear_to_us(lx):
    from pie.realize import plan_warnings
    plan = {"english": "You are dear to us.", "clauses": [{"type": "nominal", "slots": [
        {"lex_id": "closed:personal/2", "role": "SUBJ", "gender": "m"}, {"lex_id": "pie-lex-priHos", "role": "PRED"},
        {"lex_id": "closed:personal/1", "role": "IO", "num": "PL"}]}]}
    assert produce(plan, lx)["pie"] == "túH n̥sméy priHós." and not plan_warnings(plan, lx)
