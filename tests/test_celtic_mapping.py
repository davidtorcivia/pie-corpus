"""Celtic lemmatizer and lemma → PIE tables (pie/celtic_mapping.py, scripts/build_celtic_mapping.py;
docs/research/mapping-precision-celtic.md). Pure-function tests plus checks on the committed tables
data/research/formulas/mapping/{celt,sga-glosses,cy}.jsonl (nothing here reads raw/)."""

import collections
import json
from pathlib import Path

from pie import celtic_mapping as cm
from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "data" / "research" / "formulas" / "mapping"
OVERRIDES = ROOT / "data" / "research" / "formulas" / "mapping-overrides" / "celtic.json"


# ---------------------------------------------------------------- mutations and spelling

def test_irish_demutate_strips_marked_mutations():
    assert "iarthar" in cm.irish_demutate("h-Iarthar")             # h-prothesis
    assert "murbulg" in cm.irish_demutate("m-Murbulg")             # eclipsis written apart
    assert cm.irish_demutate("mBuide")[0] == "buide"               # eclipsis mb-
    assert "céadna" in cm.irish_demutate("gcéadna")                # gc-
    assert "céd" in cm.irish_demutate("c-céd")                     # CELT writes gc- as c-
    assert cm.irish_demutate("bhfear")[0] == "fear"                # bhf- before bh- → b-
    assert "súil" in cm.irish_demutate("ts-úil")                   # t-prothesis before s
    assert "clúasa" in cm.irish_demutate("chlúasa")                # written lenition
    assert "fer" in cm.irish_demutate("ḟer")
    assert "éirinn" in cm.irish_demutate("nÉirinn")                # n- before a capital vowel
    assert cm.irish_demutate("d'écc") == ["écc"]                   # elided do
    assert "duit" in cm.irish_demutate("duit-siu")                 # emphatic enclitic
    assert "bliadain" in cm.irish_demutate("bliadain-sin")


def test_irish_demutate_leaves_radicals_and_unmarked_vowels():
    assert cm.irish_demutate("fer") == []
    assert cm.irish_demutate("cath") == []
    assert "athair" not in cm.irish_demutate("tathair")            # unmarked t + vowel is not stripped
    assert "ech" not in cm.irish_demutate("nech")                  # nor unmarked n + vowel


def test_irish_skeleton_meets_middle_irish_spellings():
    sk = cm.irish_skeleton
    assert sk("marbhadh") == sk("marbad")                          # dh, bh
    assert sk("cind") == sk("cinn")                                # nd / nn
    assert sk("fear") == sk("fer")                                 # ea / e
    assert sk("aon") == sk("óen") == sk("áen")                     # ao / óe / áe
    assert sk("beag") == sk("becc")                                # post-vocalic c → g, cc → c
    assert sk("tighęrna") == sk("tigerna")                         # e caudata


def test_welsh_demutate_and_skeleton():
    assert {"mab", "bab"} <= set(cm.welsh_demutate("fab"))         # soft mutation of m-/b-
    assert "cymru" in cm.welsh_demutate("nghymru")                 # nasal
    assert "gwr" in cm.welsh_demutate("wr")                        # lost g-
    assert "pen" in cm.welsh_demutate("ben")
    assert cm.welsh_skeleton("tat") == cm.welsh_skeleton("tad")    # MW final t = /d/
    assert cm.welsh_skeleton("kyuoeth") == cm.welsh_skeleton("cyfoeth")
    assert cm.welsh_norm("hOnnO", diplomatic=True) == "hwnnw"      # insular w read as O
    assert cm.welsh_norm("yz", diplomatic=True) == "yr"            # long r read as z


def test_function_words_keep_length_marks_apart():
    assert cm.is_function_word("isna") and cm.is_function_word("bo") and cm.is_function_word("ri")
    assert not cm.is_function_word("bó") and not cm.is_function_word("rí") and not cm.is_function_word("fer")
    assert cm.is_function_word("oed", "cy") and not cm.is_function_word("mab", "cy")


# ---------------------------------------------------------------- lemmatizer and merge logic (synthetic)

def _lm(lang="sga"):
    return fm.LangMapping(lang)


def test_lemmatizer_keeps_competing_lemmas_of_a_headword_form():
    lm = _lm("cy")
    lm.forms["benn"]["benn"] += 2                                  # MW benn 'cart'
    lm.forms["benn"]["penn"] += 1                                  # soft mutation of penn 'head'
    lm.forms["fer"]["fer"] += 8
    lm.forms["fer"]["feraid"] += 1
    lz = cm.CelticLemmatizer(lm, cm.welsh_demutate, cm.welsh_skeleton, norm=cm.welsh_norm, form_overrides={})
    assert lz("benn") == "benn|penn"
    assert lz("fer") == "fer"                                      # a rare competing form-of is dropped
    assert lz("xyzq").startswith("?")


def test_lemmatizer_demutates_only_after_a_miss():
    lm = _lm()
    lm.forms["clúasa"]["clúas"] += 1
    lm.recs["clúas"] = fm.MapRec("clúas", "clúas", frozenset({"x"}), (), "chain", "high", ())
    lz = cm.irish_lemmatizer(cm.CelticMappings(lm, _lm("cy"), {}, []), form_overrides={})
    assert lz("chlúasa") == "clúas" and lz.level["chlúasa"] == "demutated"
    assert lz("clúasa") == "clúas" and lz.level["clúasa"] == "form"


def test_suppletive_forms_do_not_inherit():
    lm = _lm()
    lm.forms["bá"]["attá"] += 1
    lm.forms["atá"]["attá"] += 1
    lm.forms["rug"]["beirid"] += 1
    lm.forms["birt"]["beirid"] += 1
    lm.recs["bia"] = fm.MapRec("bia", "bia", frozenset({"pie-lex-sth2eh1yeti"}),
                               ("sga:bia", "form-of:at·tá", "ine-pro:*sth₂éh₁yeti"), "desc", "medium", ())
    cm._suppletive(lm, cm.SUPPLETIVE["sga"])
    assert "bá" not in lm.forms and "rug" not in lm.forms
    assert lm.forms["atá"]["attá"] == 1 and lm.forms["birt"]["beirid"] == 1
    assert "bia" not in lm.recs


def test_merge_prefers_a_headword_over_an_inflected_form():
    a, b = _lm(), _lm()
    a.recs["bia"] = fm.MapRec("bia", "bia", frozenset({"pie-lex-sth2eh1yeti"}), ("sga:bia", "form-of:at·tá"), "desc",
                              "medium", ())
    b.recs["bia"] = fm.MapRec("bia", "bia", frozenset({"pie-lex-gweyh3tom"}), ("ga:bia", "cel-pro:*beitom"), "chain",
                              "high", ())
    m = cm._merge("sga", [a, b], {})
    assert m.recs["bia"].ids == {"pie-lex-gweyh3tom"}
    # two headword mappings that disagree: kept only when the earliest is the word's own chain
    a.recs["x"] = fm.MapRec("x", "x", frozenset({"g1"}), ("sga:x",), "desc", "medium", ())
    b.recs["x"] = fm.MapRec("x", "x", frozenset({"g2"}), ("ga:x",), "chain", "high", ())
    assert "x" not in cm._merge("sga", [a, b], {}).recs


def test_hedged_etymologies_are_rejected():
    for text in ("Unclear. Pokorny tentatively derived it from …", "Unknown. MacBain associates it with …",
                 "From Proto-Celtic *ulkos, of uncertain etymology.",
                 "From Middle Welsh dayar … Further etymology is unknown; Morris Jones associates it …"):
        assert cm._HEDGE.search(text), text
    assert not cm._HEDGE.search("From Proto-Celtic *wiros, from Proto-Indo-European *wiHrós.")


def test_celt_licence_tags():
    assert cm.celt_licence("G400001") == cm.celt_licence("G400058") == "research"
    assert cm.celt_licence("G100001A") == "consent-train"
    assert len(cm.CELT_RESEARCH_ONLY) == 58


# ---------------------------------------------------------------- committed tables

def _rows(corpus):
    return [json.loads(l) for l in (TABLES / f"{corpus}.jsonl").read_text("utf-8").splitlines() if l.strip()]


def test_tables_have_the_round3_format():
    for c in ("celt", "sga-glosses", "cy"):
        rows = _rows(c)
        assert len(rows) > 5000
        for r in rows[:: max(1, len(rows) // 200)]:
            assert {"corpus", "lang", "lemma", "word", "lex_id", "path", "how", "confidence", "sources"} <= set(r)
            assert r["corpus"] == c and r["lex_id"]
            if c == "celt":
                assert set(r["celt_licence"]) <= {"research", "consent-train"}


def test_lemma_to_pie_cases():
    celt, gl, cy = cm.read_table("celt", ROOT), cm.read_table("sga-glosses", ROOT), cm.read_table("cy", ROOT)
    assert celt["fer"] == ("pie-lex-wiHros",)
    assert celt["cath"] == ("pie-lex-keh3tus",)
    assert celt["éc"] == ("pie-lex-nekjus",)
    assert celt["athair"] == ("pie-lex-ph2texr",)
    assert celt["bia"] == ("pie-lex-gweyh3tom",)                  # Ir. bia 'food', not the at·tá form
    assert gl["dobeir"] == ("pie-root-bher-bear",)
    assert cy["dydd"] == ("pie-lex-dyexws",)
    assert cy["brenhin"] == ("pie-lex-bhergjhonts",)


# the wrong ids of the round-0 sample errors fixed at the source or by override (docs/research/mapping-precision-celtic.md)
WRONG = {
    ("celt", "uair"): {"kaikki:h₃ewǵ"},                            # úair 'hour' < Latin hōra
    ("celt", "úar|úair"): {"kaikki:h₃ewǵ"},
    ("celt", "bá"): {"pie-lex-sth2eh1yeti"},                       # suppletive b-forms of at·tá
    ("celt", "bís"): {"pie-lex-sth2eh1yeti"},
    ("celt", "fír"): {"pie-lex-wiHros"},                           # 'true', not 'man'
    ("celt", "ingen"): {"pie-lex-h3noxghs"},                       # 'daughter', not 'nail'
    ("celt", "cenél"): {"pie-lex-sken"},
    ("celt", "muin"): {"pie-lex-mon"},
    ("celt", "fiabhras"): {"pie-root-dhegwh-burn"},                # French/Latin loan
    ("celt", "pós"): {"pie-root-spend-libate", "pie-root-spend-stretch"},
    ("celt", "brat"): {"pie-root-bhrewh1-boil"},                   # English broth homograph
    ("celt", "ór"): {"pie-lex-poros"},                             # Latin aurum
    ("celt", "lá"): {"pie-lex-lh1yeti"},
    ("celt", "tol"): {"pie-root-telh2-bear", "pie-root-telh2-ground"},
    ("celt", "druimm"): {"pie-lex-termn"},
    ("sga-glosses", "inne"): {"kaikki:dʰǵʰyesi"},
    ("sga-glosses", "robad"): {"pie-lex-h1esti"},
    ("sga-glosses", "gnúis"): {"pie-lex-gjenus"},
    ("cy", "bu"): {"pie-lex-gwoxws", "pie-lex-gwowdhi"},           # MW bu 'was', not 'cow'
    ("cy", "gwyr"): {"pie-lex-weh1iros"},                          # 'men', not 'crooked'
    ("cy", "sais"): {"pie-root-sek-cut", "pie-root-sek-dry_out"},  # Latin Saxō
    ("cy", "eur"): {"pie-root-h2ews-become_light", "pie-root-h2ews-draw_water"},
    ("cy", "daear"): {"pie-lex-dhegjhoxm"},
    ("cy", "gallu"): {"pie-root-gelH-naked"},
    ("cy", "kenedyl"): {"pie-lex-sken"},
}


def test_no_wrong_ids_for_fixed_sample_errors():
    tables = {c: cm.read_table(c, ROOT) for c in ("celt", "sga-glosses", "cy")}
    for (c, lem), wrong in WRONG.items():
        assert not (set(tables[c].get(lem, ())) & wrong), (c, lem, tables[c].get(lem))


def test_no_rows_for_function_words():
    celt, cy = cm.read_table("celt", ROOT), cm.read_table("cy", ROOT)
    for w in ("in", "ocus", "do", "isna", "bo", "ri"):
        assert w not in celt, w
    for w in ("oed", "yw", "yny"):
        assert w not in cy, w


def test_override_file_rows_cite_a_source():
    d = json.loads(OVERRIDES.read_text("utf-8"))
    for r in d["lemma"]:
        assert r["corpus"] in ("celt", "sga-glosses", "cy") and r["note"]
    for r in d["form"]:
        assert r["lang"] == "sga" and r["note"]         # load_overrides keys form rows with KEYS[lang]
    ov = fm.load_overrides(ROOT)
    assert ov["lemma"]["celt"]["uair"][0] == frozenset()
    assert ov["form"]["sga"]["fir"] == "fer"
    counts = collections.Counter((r["corpus"], r["lemma"]) for r in d["lemma"])
    assert max(counts.values()) == 1
