"""Corpus-quality batch 1, Classical Armenian (DMHP): production-path regressions.

Verdicts: data/research/8c/corpus-quality/error-verdicts-cq1-armenian.jsonl. Never reads review slabs
or claims.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from pie import cq1_mapping, cq1_xcl, formula_search as fs, mapping as mp

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "daughters" / "armenian-dmhp-matenagirk"
READINGS = [r for r in json.loads((ROOT / "data/research/formulas/cq1-readings-xcl.json").read_text("utf-8"))]
LAZ, MOV, AGA = "MH_1_2_13_Lazar_Parp", "MH_1_2_12_Movses_Khor", "MH_1_2_11_Agathangelos"
FAU, YEG, EZN, GRE = "MH_1_1_04_Faustos", "MH_1_1_06_Yeghishe", "MH_1_1_05_Eznik", "MH_1_1_01_Gregor_Lus"


def tok(lemma, surface, locus="unreviewed (word id 1)"):
    return fs.Token("xcl", lemma, surface, locus, {}, True, "other")


@pytest.fixture(scope="module")
def loader():
    if not RAW.exists():
        pytest.skip("raw corpora absent")
    spec = importlib.util.spec_from_file_location("cq1_xcl_test_stage_c", ROOT / "scripts/build_8c_stageC.py")
    sc = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = sc
    spec.loader.exec_module(sc)
    return {cq1_xcl.coord(t.locus): t for t in sc.dmhp_tokens(ROOT)}


def test_exact_readings_apply_only_at_their_word():
    assert READINGS and all(r["corpus"] == "xcl" for r in READINGS)
    for r in READINGS:
        t = tok(r["old"], r["surface"], r["locus"])
        assert t.lemma == r["lemma"], r
        assert t.content == (not (r.get("noncontent") or r["lemma"].endswith(" (name)"))), r
        other = tok(r["old"], r["surface"])
        assert other.lemma == cq1_xcl.contextual_lemma("xcl", r["old"], r["surface"], other.locus), r


@pytest.mark.parametrize("coord,surface,lemma,content", [
    ((MOV, 1245), "արանցն", "ayr", True),               # w10 r17
    ((LAZ, 54833), "արամբ", "ayr", True),               # w10 r17 obs5
    ((LAZ, 53808), "արամբ", "ayr", True),               # w11 r1
    ((MOV, 17579), "արա՞նցն", "ayr", True),             # w10 r55
    ((AGA, 45163), "յարեան", "yar̄nem", True),           # w10 r17 obs0
    ((LAZ, 46984), "Արեաց", "ari (name)", False),       # w10 r17 obs9
    ((MOV, 74363), "Արիք,", "ari (name)", False),       # w10 r76
    ((LAZ, 60712), "Արի", "ari (name)", False),         # w10 r76 obs5 (exact)
    ((AGA, 67056), "Յունաց՝", "yoyn (name)", False),    # w10 r18
    ((AGA, 59802), "տո՛ւր", "tam", True),               # w10 r22
    ((AGA, 43311), "տուաւ", "tam", True),               # w10 r33
    ((LAZ, 62754), "տուք", "tam", True),                # w10 r110
    ((MOV, 22643), "տաս", "tam", True),                 # w10 r57
    ((LAZ, 18765), "տաւթոյն", "tawtʻ", True),           # w10 r33 obs0
    ((MOV, 430), "Լ.", "30@numeral", False),            # w10 r46, w11 r27
    ((LAZ, 22013), "ԼԸ.", "38@numeral", False),         # w10 r46 obs2
    ((AGA, 45004), "ԿԶ.", "66@numeral", False),         # w10 r47
    ((MOV, 74363 - 1), "լթ.", "39@numeral", False),     # Geography list number before Arikʻ
    ((LAZ, 3086), "գեղջէ,", "geł@village", True),       # w10 r89
    ((LAZ, 51730), "գեղջն,", "geł@village", True),      # w10 r106, w11 r9
    ((MOV, 74610), "էրէ", "erē", True),                 # w10 r83
    ((MOV, 80910), "երէ,", "erē", True),                # w10 r96
    ((LAZ, 48736), "գան,", "gam", True),                # w10 r103
    ((FAU, 9496), "գան", "gam", True),                  # formula scan item 10
    ((EZN, 15023), "տուիչ", "towičʻ", True),            # formula scan item 11
    ((MOV, 3229), "լով", "asem", False),                # formula scan item 9
    ((AGA, 44938), "գինւոյ", "gini", True),             # w10 r39
    ((LAZ, 49023), "գունոյ", "goyn", True),             # w10 r39 obs2
    ((AGA, 51940), "գոյն", "goyn", True),               # w10 r31
    ((AGA, 41936), "ելից", "lnowm", True),              # w10 r28
    ((AGA, 65196), "մտի,", "mit", True),                # w10 r21
    ((MOV, 6496), "Գառնի։", "Gar̄ni (name)", False),     # w10 r34
    ((AGA, 64779), "Որմզդի,", "Ormizd (name)", False),  # w10 r35
    ((MOV, 5844), "Հարք,", "Harkʻ (name)", False),      # w10 r37
    ((MOV, 4271), "Մար", "Mar (name)", False),          # w10 r16
    ((MOV, 59827), "Մարք,", "Markʻ (name)", False),     # w10 r16 obs2
    ((MOV, 59823), "Մեդաց", "Medkʻ (name)", False),     # w10 r61
    ((MOV, 79768), "Ուտի", "Owti (name)", False),       # w10 r71
    ((MOV, 79777), "Կուր", "Kowr (name)", False),       # w10 r73
    ((MOV, 67276), "Ասիոյ", "Asia (name)", False),      # w10 r75
    ((MOV, 31714), "Կարէն,", "Karēn (name)", False),    # w11 r7
    ((MOV, 63138), "զԱլիս,", "Alis (name)", False),     # w11 r16
    ((AGA, 23688), "ծփանաց", "cpʻan", True),            # w10 r3
    ((AGA, 54861), "Ա՛ղէ,", "ałē", True),               # w10 r24
    ((MOV, 3695), "զրոյցս", "zroycʻ", True),            # w10 r19
    ((LAZ, 54622), "որեար", "orear", True),             # w10 r19 obs3
    ((AGA, 31216), "բանիւ", "ban", True),               # w11 r29
    ((AGA, 56685), "յարիւն,", "ariwn", True),           # w11 r33
    ((LAZ, 60637), "յականջս", "akanǰ", True),           # w10 r121
    ((MOV, 64178), "հարաւ", "haraw", True),             # w10 r81
    ((AGA, 59836), "Հաւը", "hayr", True),               # w10 r43 (surface kept)
    ((AGA, 53555), "յինէնա.", "es", False),             # w10 r20
    ((MOV, 12952), "հեր", "her", True),                 # w10 r63: content word DMHP tagged I+Adv
])
def test_reported_loci_in_the_production_loader(loader, coord, surface, lemma, content):
    t = loader[coord]
    assert (t.surface, t.lemma, t.content) == (surface, lemma, content)


@pytest.mark.parametrize("coord,lemma", [
    ((YEG, 85663), "ariwn"),      # i arean 'in blood'
    ((GRE, 17587), "hayr"),       # Harkʻ 'the fathers' ate sour grapes
    ((FAU, 59682), "yar̄nem"),     # Arikʻ 'arise!'
    ((YEG, 94044), "yar̄nem"),
    ((AGA, 8484), "gan"),         # arbcʻē gan 'shall receive a beating'
    ((EZN, 21313), "gan"),
    ((LAZ, 25016), "gan"),
    ((EZN, 827), "gom"),          # i Goyn 'the Existent'
    ((YEG, 34671), "mtanem"),     # mti 'I entered'
    ((MOV, 64564), "elkʻ"),       # əst elicʻ 'to the east'
    ((LAZ, 22715), "elkʻ"),
    ((YEG, 27866), "harkanem"),   # zahi haraw 'was struck with fear'
    ((AGA, 19874), "harkanem"),
])
def test_rule_exceptions_keep_their_lemma(loader, coord, lemma):
    assert loader[coord].lemma == lemma


@pytest.mark.parametrize("lemma,surface", [
    ("ariwn", "արեան"), ("ariwn", "արիւն"), ("ariwn", "արեամբ"), ("towr", "տուրս"), ("tawn", "տաւն"),
    ("tasn", "տասն"), ("gin", "գին"), ("gin", "գինս"), ("ownim", "ունիմ"), ("li", "լի"), ("mayr", "մայր"),
    ("hayr", "հայր"), ("hayr", "հարք"), ("kam", "կամ"), ("geł", "գեղ"), ("em", "է"), ("asem", "ասէ."),
    ("na", "նա."), ("mi", "մի."), ("em", "Է"), ("i", "Ի"), ("gan", "գանիւ"), ("yar̄nem", "արի"),
])
def test_unrelated_homographs_are_left_alone(lemma, surface):
    t = tok(lemma, surface)
    assert t.lemma == lemma


def test_numeral_values_and_exceptions():
    assert cq1_xcl.numeral_value("ԿԶ") == 66
    assert cq1_xcl.numeral_value("ՃԺԹ") == 119
    assert cq1_xcl.numeral_value("ՅԻԱ") == 321
    assert cq1_xcl.numeral_value("ԶԵ") is None and cq1_xcl.numeral_value("ՈՔ") is None
    assert tok("li", "Լ.").lemma == "30@numeral" and not tok("li", "Լ.").content
    assert tok("na", "ՆԱ.", "MH_1_1_10_Mandakuni ed. page 1 - PDF page 1 (word id 1)").lemma == "na"
    assert tok("ža", "ժա.", "MH_1_2_12_Movses_Khor ed. page 1 - PDF page 1 (word id 1)").lemma == "11@numeral"
    assert tok("ža", "ժա.", "MH_1_1_06_Yeghishe ed. page 1 - PDF page 1 (word id 1)").lemma == "ža"
    assert tok("mi", "մի.", "MH_1_2_12_Movses_Khor ed. page 1 - PDF page 1 (word id 1)").lemma == "mi"


@pytest.mark.parametrize("lemma,ids", [
    ("ali", {"pie-root-pelH-pale"}), ("alikʻ", {"pie-root-pelH-pale"}), ("bov", set()), ("elkʻ", set()),
    ("towičʻ", {"pie-root-deh3-give"}), ("akanǰ", {"pie-lex-h2oxws"}),
])
def test_reviewed_mapping_rows(lemma, ids):
    assert mp.decide("xcl", lemma, {"wrong-auto-root"})[0] == ids


def test_unreviewed_mappings_are_preserved():
    t = mp.resolve_table("xcl")
    assert t["gan"].ids == {"pie-lex-gwhonis"}          # gan 'beating'
    assert t["ǰnǰem"].ids == {"pie-lex-gwhenyeti"}      # Martirosyan: *gʷʰen-i̯e/o-
    assert t["ayr"].ids == {"pie-lex-h2nexr"}
    assert t["tam"].ids == {"pie-root-deh3-give"}
    assert t["gini"].ids and t["ariwn"].ids == {"pie-lex-h1esh2r"}


def test_names_and_numerals_are_non_content():
    assert cq1_mapping.noncontent("xcl", "Kowr (name)", "Կուր", "x")
    assert cq1_mapping.noncontent("xcl", "66@numeral", "ԿԶ.", "x")
    assert not cq1_mapping.noncontent("xcl", "kowr", "կուր", "x")
    assert not cq1_xcl.noncontent("grc", "Κῦρος (name)", "Κῦρος", "x")
