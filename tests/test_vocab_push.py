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
    """An unaccented devī headword gets no spec: any paradigm would guess the oblique accent. (sḱeh₃ih₂ 'shadow',
    the old example, got its sourced accent in the core-gaps round: test_core_gap_paradigms.)"""
    assert lx.specs["pie-lex-bherontih2"]["rule"] == "unknown:devi-no-accent"
    assert not lx.specs["pie-lex-bherontih2"]["usable"]


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
    """grey, yew: glossed now, but no source gives an accent, so they stay out of the pool. (debt left this list in
    round 3, 2026-10-31: Derksen's Slavic AP (c) for *dьlgъ gives dʰl̥gʰós, as for gʷoldʰós.)"""
    for lid in ("pie-lex-polHwos", "pie-lex-h1eyHwos"):
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


def test_a_causative_reflex_does_not_confirm_the_plain_sense():
    """t3b-003 review: Ved. svāpáyati, PGmc *swabjaną 'put to sleep' had confirmed swopéyeti as plain 'to sleep',
    and planners used it for 'sleep'. A causative reflex confirms only a causative sense."""
    import json
    from pathlib import Path
    from pie.glosses import _CAUSATIVE
    rows = {json.loads(x)["id"]: json.loads(x) for x in
            (Path(__file__).resolve().parents[1] / "data/lexicon/confirmed_glosses.jsonl").read_text("utf-8").splitlines()}
    assert rows["pie-lex-swopeyeti"]["gloss"] == "to put to sleep"
    assert _CAUSATIVE.match("to put to sleep") and _CAUSATIVE.match("make wet")
    assert not _CAUSATIVE.match("to make a mistake") and not _CAUSATIVE.match("to sleep")


# 4. dialogue gaps (docs/audits/lexicon-gaps-dialogue-2026-10-30.md) -----------------------------------------------

DIALOGUE = {   # keyword -> lexeme, offered by default with an override gloss that carries the keyword
    "angry": "pie-lex-ghremeti", "anger": "pie-lex-ghromeyeti", "hungry": "pie-lex-kenketi",
    "hunger": "pie-lex-gwoldhos", "milk": "pie-lex-h2melgjos", "play": "pie-lex-loygeti", "weave": "pie-lex-teksti",
    "cup": "pie-lex-peh3tlom", "pot": "pie-lex-kweros", "knife": "pie-lex-kjstrom", "feast": "pie-lex-dh2pnom",
    "sad": "pie-lex-lugjros",
}


@pytest.mark.parametrize("kw,lid", sorted(DIALOGUE.items()))
def test_dialogue_word_is_offered(lx, pool, kw, lid):
    assert lid in pool and lx.meaning(lid)[1] == "override"
    ms = runpy.run_path(str(ROOT / "scripts/make_slice.py"))
    assert ms["keyword_hit"](lx, lid, [kw]) and lid in ms["TIER3B_INHERITED"]


def test_dialogue_paradigms(lx):
    """The two spec changes (knife: headword ḱéstrom, Skt. śástra-; sad: an adjective) and spot cells of the rest."""
    assert lx.entries["pie-lex-kjstrom"]["form"] == "ḱéstrom" and "ḱstrom" in lx.entries["pie-lex-kjstrom"]["variants"]
    assert lx.cells("pie-lex-kjstrom")["GEN.SG"][0] == "ḱéstrosyo" and lx.accent_status("pie-lex-kjstrom") == "resolved"
    assert lx.specs["pie-lex-lugjros"]["family"] == "adj" and lx.cells("pie-lex-lugjros", "f")["NOM.SG"][0] == "luǵréh₂"
    assert lx.cells("pie-lex-teksti")["PRS.3PL"][0] == "tksénti"            # Hitt. takšanzi
    assert lx.cells("pie-lex-ghremeti")["PTCP.ACT"][0] == "gʰrémonts"       # YAv. gramant- 'raging'
    assert lx.cells("pie-lex-h2melgjos")["GEN.SG"][0] == "h₂mélǵesos"
    r = produce({"english": "The sad man is hungry.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-wiHros", "role": "SUBJ"}, {"lex_id": "pie-lex-lugjros", "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-kenketi", "role": "V", "verb": {"tense": "PRS", "mood": "IND", "voice": "ACT"}}]}]}, lx)
    assert r["pie"] == "luǵrós wiHrós kénketi."         # MOD precedes its head


def test_forest_stays_unoffered_without_an_accent(lx, pool):
    """h₁widʰh₁us 'tree, wood; forest' (Kroonen, Matasović): glossed, but no source gives an accent and the engine has
    no spec for it, so Tier 3b has the calque pie-neo-forest instead."""
    assert lx.meaning("pie-lex-h1widhh1us")[1] == "override" and "pie-lex-h1widhh1us" not in pool
    assert lx.inadmissible("pie-lex-h1widhh1us")


# 5. core gaps (docs/audits/lexicon-gaps-core-2026-10-30.md) ----------------------------------------------------------

CORE = {   # concept keyword -> lexeme, offered by default with an override gloss that carries the keyword
    "person": "pie-lex-mortos", "child": "pie-lex-tekjnom", "small": "pie-lex-peh2uros", "tail": "pie-lex-h1orseh2",
    "leg": "pie-lex-skelos", "thigh": "pie-lex-skelos", "bark": "pie-lex-lowbhos", "flower": "pie-lex-h2endhos",
    "grass": "pie-lex-ghreh1mn", "belly": "pie-lex-uderos", "guts": "pie-lex-gjhorneh2", "ice": "pie-lex-h1yegos",
    "wood": "pie-lex-doru", "soil": "pie-lex-dhegjhoxm", "goat": "pie-lex-kapros", "bad": "pie-lex-h2eghos-2",
    "rot": "pie-lex-puHyeti", "straight": "pie-lex-h3regjtos", "smooth": "pie-lex-ghlh2dhros",
    "beautiful": "pie-lex-kjubhros", "glad": "pie-lex-mudros", "rejoice": "pie-lex-mewdeti", "hunt": "pie-lex-wregeti",
    "walk": "pie-lex-steygheti", "rub": "pie-lex-teryeti", "freeze": "pie-lex-goleti", "cough": "pie-lex-kweh2se",
    "smell": "pie-lex-h3edeti", "carry": "pie-lex-bhereti", "show": "pie-lex-deykjeti", "silent": "pie-lex-th2keh1yeti",
    "hate": "pie-lex-h3eh3ode-2", "tired": "pie-lex-kjekjomh2e", "teach": "pie-lex-kjeHst", "lack": "pie-lex-h1egos",
    "thankful": "pie-lex-gwrHtos", "decide": "pie-lex-h2reh1dheti", "council": "pie-lex-dhh1tleh2",
    "wise": "pie-lex-gjnh3ros", "enemy": "pie-lex-poykjos-2",
}


@pytest.mark.parametrize("kw,lid", sorted(CORE.items()))
def test_core_gap_word_is_offered_to_every_slice(lx, pool, kw, lid):
    assert lid in pool and lx.meaning(lid)[1] == "override"
    ms = runpy.run_path(str(ROOT / "scripts/make_slice.py"))
    assert ms["keyword_hit"](lx, lid, [kw]) and lid in ms["TIER3B_INHERITED"] + ms["EVERYDAY"]


def test_core_gap_concepts_reach_the_holdout_matcher(lx):
    """scripts/build_holdout.py's concept matcher (trusted glosses only) now finds these concepts in an offered
    lexeme; the hold-out files themselves are frozen and not redrawn."""
    hb = runpy.run_path(str(ROOT / "scripts/build_holdout.py"))
    ms = hb["_make_slice"]()
    pool = set(ms.offered(lx))
    found = {c: set(ids) & pool for d in hb["concept_matches"](lx, ms).values() for c, ids in d.items()}
    for c in ("human being/person", "child", "small/little", "tail", "leg", "thigh", "bark", "flower", "grass",
              "belly", "guts/bowels/entrails", "ice", "wood", "soil", "goat", "bad/evil", "rotten/rot", "straight",
              "smooth", "pretty/beautiful", "happy/glad/be glad/joyful", "rejoice", "hunt", "walk", "rub",
              "freeze/be cold", "cough", "smell", "carry", "show", "silent/be silent", "hate", "be tired", "teach",
              "lack", "shade/shadow"):
        assert found[c], c


def test_core_gap_paradigms(lx):
    """The seven spec changes: an accent from the handbooks (shadow), a present headword (cough), two stative
    perfects (hate, be tired) and three adjectives (small, bad, smooth)."""
    c = lx.cells("pie-lex-skjeh3ih2")                     # EWAia s.v. chāyā́-: *sḱéh₃-ih₂, gen. *sḱh₃-iéh₂-s
    assert (c["NOM.SG"][0], c["GEN.SG"][0]) == ("sḱéh₃ih₂", "sḱh₃yéh₂s") and "sḱeh₃ih₂" in lx.entries["pie-lex-skjeh3ih2"]["variants"]
    assert lx.cells("pie-lex-kweh2se")["PRS.3SG"][0] == "kʷéh₂seti"
    assert lx.cells("pie-lex-h3eh3ode-2")["PRF.3SG"][0] == "h₃eh₃óde"          # Lat. ōdī
    assert lx.cells("pie-lex-kjekjomh2e")["PRF.3PL"][0] == "ḱeḱm̥h₂ḗr"          # Ved. śaśāma, Hom. κεκμηώς
    for lid, f in (("pie-lex-peh2uros", "péh₂ureh₂"), ("pie-lex-h2eghos-2", "h₂egʰéh₂"),
                   ("pie-lex-ghlh2dhros", "gʰl̥h₂dʰréh₂")):
        assert lx.specs[lid]["family"] == "adj" and lx.cells(lid, "f")["NOM.SG"][0] == f
    r = produce({"english": "The small child rubs the goat.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-tekjnom", "role": "SUBJ"}, {"lex_id": "pie-lex-peh2uros", "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-kapros", "role": "OBJ"},
        {"lex_id": "pie-lex-teryeti", "role": "V", "verb": {"tense": "PRS", "mood": "IND", "voice": "ACT"}}]}]}, lx)
    assert r["pie"] == "péh₂urom téḱnom káprom téryeti."        # neuter subject: nom. = acc. -om


def test_tail_nil_flag_lifted_on_evidence(lx, pool):
    """h₁orséh₂ (NIL no. 247) was held by nil-single-branch; Gk οὐρά and OIr. err (Beekes) are two branches, so the
    override clears the flag (pie.lexicon applies an override's `uncertain`) and NIL_ADMIT admits it."""
    assert lx.entries["pie-lex-h1orseh2"]["uncertain"] == [] and "pie-lex-h1orseh2" in pool


def test_round3_specs_and_cells():
    """docs/audits/lexicon-gaps-round3-2026-10-31.md: the hand-checked and form-fixed specs give these cells, and
    a realized plan uses them (check_plan, then realize)."""
    from pie.realize import Lexicon, check_plan, realize
    lx = Lexicon.load()
    want = {("pie-lex-dhlghos", None, "NOM.SG"): "dʰl̥gʰós", ("pie-lex-skeytos", None, "GEN.SG"): "skéytosyo",
            ("pie-lex-moro", None, "NOM.SG"): "móros", ("pie-lex-gjlh2oxws", None, "ACC.SG"): "ǵl̥h₂ṓm",
            ("pie-lex-gjlh2oxws", None, "GEN.SG"): "ǵl̥h₂éws", ("pie-lex-h1yenh2texr", None, "ACC.SG"): "h₁yénh₂term̥",
            ("pie-lex-swekjruh2", None, "GEN.SG"): "sweḱruh₂és", ("pie-lex-sneh1", None, "PRS.3SG"): "snéh₁ti",
            ("pie-lex-gheldheti", None, "PRS.3SG"): "gʰéldʰeti", ("pie-lex-dhrsus", "m", "GEN.SG"): "dʰr̥séws",
            ("pie-lex-dhrsus", "f", "NOM.SG"): "dʰr̥séwih₂"}
    for (i, g, cell), form in want.items():
        assert lx.cells(i, g)[cell][0] == form, (i, cell)
    assert lx.specs["pie-lex-h2eti"]["rule"] == "indeclinable" and lx.entries["pie-lex-h2eti"]["pos"] == "adv"
    plan = {"english": "The brave mother-in-law spins.", "clauses": [{"english": "The brave mother-in-law spins.", "slots": [
        {"lex_id": "pie-lex-swekjruh2", "role": "SUBJ"}, {"lex_id": "pie-lex-dhrsus", "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-sneh1", "role": "V", "verb": {"tense": "PRS", "mood": "IND", "voice": "ACT"}}]}]}
    assert not check_plan(plan, lx)
    assert realize(plan, lx)["pie"] == "dʰr̥séwih₂ sweḱrúh₂ snéh₁ti."
