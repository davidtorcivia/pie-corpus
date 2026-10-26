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


def test_base_inherits_reviewed_decisions_without_mutating_shared_mapping():
    from pie import mapping as mp

    rec = fm.MapRec("daioni", "daioni", frozenset({"old-id"}),
                    ("cy:daioni", "base:da", "cy:da"), "base", "low", ("base",))
    recs = {"daioni": rec}
    for ids in (frozenset(), frozenset({"corrected-id"})):
        ov = mp.as_overrides({"cy": {"da": (ids, {"note": "reviewed base"})}})
        got = cm.apply_base_overrides(recs, "cy", ov)
        assert (got["daioni"].ids if "daioni" in got else frozenset()) == ids
        assert cm.apply_base_overrides(recs, "other-corpus", ov) == recs
        assert recs["daioni"] == rec
        # An explicit derived-word decision wins over its base's decision.
        ov = mp.as_overrides({"cy": {"da": (ids, {}),
                                    "daioni": (frozenset({"own-id"}), {})}})
        assert cm.apply_base_overrides(recs, "cy", ov)["daioni"].ids == {"own-id"}
    # Without a base edge, an etymological mention must not inherit lemma overrides.
    own = fm.MapRec("other", "other", rec.ids, ("cy:other", "cy:da"), "chain", "high", ())
    assert cm.apply_base_overrides({"other": own}, "cy", ov) == {"other": own}


def test_remaining_celtic_sample_rows_are_unmapped():
    for corpus, lemmas in (("celt", ("bua", "úar")), ("sga-glosses", ("bua", "úar")),
                           ("cy", ("dal", "budd", "crwn", "coret", "daioni"))):
        # Check generated rows as well as the shared resolver's view.
        rows = {r["lemma"]: r for r in map(json.loads, (TABLES / f"{corpus}.jsonl").read_text().splitlines())}
        table = cm.read_table(corpus, ROOT)
        for lemma in lemmas:
            assert lemma not in rows
            assert not table.get(lemma)


def test_table_mapper_base_removal_blocks_loose_fallback():
    from pie import mapping as mp
    from scripts.build_celtic_mapping import TableMapper

    lm = _lm("cy")
    lm.recs["daioni"] = fm.MapRec("daioni", "daioni", frozenset({"old-id"}),
                                 ("cy:daioni", "base:da", "cy:da"), "base", "low", ())
    lm.recs["daioní"] = fm.MapRec("daioní", "daioní", frozenset({"other-id"}),
                                 ("cy:daioní",), "chain", "high", ())
    ov = mp.as_overrides({"cy": {"da": (frozenset(), {})}})
    mapper = TableMapper(lm, {}, "cy", ov)
    assert mapper("daioni") is None
    assert mapper("daioní").ids == {"other-id"}


# ---------------------------------------------------------------- round 2 (independent blind check)

def test_tig_is_resolved_by_the_preceding_word():
    """tig is the dat. of tech 'house' after a preposition / article and ·tic of do·icc elsewhere: the
    lemmatizer alone gives the ambiguous union (unmapped), lemmatize_words resolves it from context."""
    lm = _lm()
    lz = cm.CelticLemmatizer(lm, cm.irish_demutate, cm.irish_skeleton,
                             form_overrides={"tig": "tech|doicc", "tic": "doicc"})
    words = ["Luid", "isin", "tig", "ocus", "tig", "i", "tig", "ní", "thig"]
    got = cm.lemmatize_words(lz, words)
    assert got[2] == "tech" and got[6] == "tech"                   # isin tig, i tig
    assert got[4] == "tech|doicc"                                  # no deciding word: ambiguous
    assert got[8] == "doicc"                                       # ní thig 'does not come'
    assert lz("tig") == "tech|doicc"
    ov = fm.load_overrides(ROOT)["form"]["sga"]
    assert ov["tig"] == "tech|doicc" and ov["tic"] == "doicc"
    celt = cm.read_table("celt", ROOT)
    assert "tech|doicc" not in celt                                # the union stays unmapped
    assert celt["tech"] == ("pie-lex-stegos",)


def test_tuc_forms_are_do_uccai_brings():
    """The kaikki table of do·ucai 'understands' (*h₁ewk-) also lists ·tuc-, ·tucus, ·tuctar of do·uccai
    'brings' (do·uic, causative of do·icc, *h₂neḱ-): STEM_SPLITS moves the non-palatal forms."""
    lm = _lm()
    for f in ("tuc", "tucus", "tuctar", "tucsat", "tuicci", "doucci"):
        lm.forms[f]["doucai"] += 1
    lm.recs["doicc"] = fm.MapRec("doicc", "do·icc", frozenset({"pie-root-h2nekj-reach"}), ("sga:doicc",), "root", "low", ())
    lm.recs["doucai"] = fm.MapRec("doucai", "do·ucai", frozenset({"pie-lex-h1unekti"}), ("sga:doucai",), "chain", "high", ())
    moved = cm._stem_splits(lm, cm.STEM_SPLITS["sga"])
    assert sorted(moved["douccai"]) == ["tuc", "tucsat", "tuctar", "tucus"]
    assert dict(lm.forms["tuicci"]) == {"doucai": 1} and dict(lm.forms["doucci"]) == {"doucai": 1}
    assert lm.recs["douccai"].ids == frozenset({"pie-root-h2nekj-reach"})
    celt = cm.read_table("celt", ROOT)
    assert celt["douccai"] == ("pie-root-h2nekj-reach",)
    assert celt["doucai"] == ("pie-lex-h1unekti",)                 # 'understand' keeps its own etymon


def test_matasovic_entry_parser_skips_starred_forms_inside_etym():
    lines = ["*luxtu- 'contents; crowd, people'", "[Noun]", "GOlD: Olr. lucht [u m]",
             "ETYM: The etymology in IEW (686) deriving these Celtic words from PIE", "*lewg- 'break'",
             "is not convincing", "because of the difference", "*bowd-ro-", "'dirty'", "[Adj]"]
    assert cm._mat_is_head(lines, 0)
    assert not cm._mat_is_head(lines, 4)                           # a form quoted in ETYM
    assert cm._mat_is_head(lines, 7)                               # head, gloss and tag on three lines


def test_matasovic_verdicts():
    lex = [{"id": "pie-root-perh3-provide", "form": "perh₃-", "kind": "root", "meaning": ["to provide, bestow"]},
           {"id": "pie-root-kjerd-heart", "form": "ḱerd-", "kind": "root", "meaning": ["heart"]}]
    fz = fm.FuzzyPie(lex)
    mean = {e["id"]: " ".join(e["meaning"]) for e in lex}
    e = lambda pie, etym="": {"pie": pie, "etym": etym}
    assert cm._mat_verdict(e("", "The IE etymology is unknown."), fz, mean)[0] == "reject"
    assert cm._mat_verdict(e("", "deriving it from *lewg- 'break' is not convincing"), fz, mean)[0] == "reject"
    assert cm._mat_verdict(e("", "Germanic words are loanwords from Celtic."), fz, mean) is None   # no stance
    assert cm._mat_verdict(e(" *perh3- 'bestow' (IEW: 817)"), fz, mean) == ("ids", frozenset({"pie-root-perh3-provide"}))
    assert cm._mat_verdict(e(" *kerd- 'swing'"), fz, mean) is None             # OCR homograph: gloss fits no id
    assert cm._mat_verdict(e(" *perh3- 'bestow'", "this etymology is quite uncertain"), fz, mean) is None
    assert not cm._mat_is_loan("could be early loanwords from Celtic")
    assert cm._mat_is_loan("probably a loanword from some non-IE language")


def test_matasovic_takes_precedence_over_wiktionary():
    """Where EDPC speaks to a headword it wins (docs/research/mapping-precision-celtic.md, round 2)."""
    log = json.loads((ROOT / "data/research/formulas/celtic-precision/systematic-rules-log.json").read_text("utf-8"))
    assert log["sga"]["lucht"][1] is None                          # EDPC p0265: IEW's *lewǵ- 'is not convincing'
    assert log["sga"]["caill"][1] is None and log["cy"]["daly"][1] is None
    assert log["sga"]["toísech"][1] == ["pie-root-weyd-see"]       # EDPC p0402: *weyd-, not *wedʰ-
    assert log["cy"]["atal"][2] == "via daly"                      # propagated along the chain
    assert "cymru" in log["preverb-only"]["cy"] and "íadaid" in log["preverb-only"]["sga"]
    celt, gl, cy = cm.read_table("celt", ROOT), cm.read_table("sga-glosses", ROOT), cm.read_table("cy", ROOT)
    for t, lem in ((celt, "lucht"), (celt, "caill"), (celt, "aimser"), (celt, "bran"), (cy, "caer"), (cy, "daly"),
                   (cy, "atal"), (celt, "brisid"), (celt, "coill")):
        assert not t.get(lem), lem
    assert celt["toísech"] == ("pie-root-weyd-see",) and celt["taoiseach"] == ("pie-root-weyd-see",)
    assert gl["rann"] == ("pie-root-perh3-provide",)
    assert "íad" not in celt and cm.is_function_word("íad")


def test_matasovic_precedence_on_a_small_mapping():
    lex = [{"id": "pie-root-weyd-see", "form": "weyd-", "kind": "root", "meaning": ["to see, know"]},
           {"id": "pie-root-wedh-lead", "form": "wedʰ-", "kind": "root", "meaning": ["to lead"]}]
    gmap = {e["id"]: e["id"] for e in lex}
    ir, cy = _lm(), _lm("cy")
    ir.recs["toísech"] = fm.MapRec("toísech", "toísech", frozenset({"pie-root-wedh-lead"}),
                                   ("sga:toísech", "ine-pro:*wedʰ-"), "chain", "high", (), "leader, chief; first")
    ir.recs["taoiseach"] = fm.MapRec("taoiseach", "taoiseach", frozenset({"pie-root-wedh-lead"}),
                                     ("ga:taoiseach", "sga:toísech", "ine-pro:*wedʰ-"), "chain-sga", "medium", ())
    import pie.celtic_mapping as mod
    ents = [{"head": "*to-wissako-", "page": "p0402", "goid": " OIr. toísech [o m] 'leader'", "w": "",
             "pie": "", "gloss": "leader, chief, first",
             "etym": "PCelt. *to-wissako- < *-wid-t-ako- < PIE *weyd- 'see, know'."}]
    orig = mod.matasovic_entries
    mod.matasovic_entries = lambda root=None: ents
    try:
        log = mod.matasovic_precedence(ir, cy, lex, gmap)
    finally:
        mod.matasovic_entries = orig
    assert ir.recs["toísech"].ids == frozenset({"pie-root-weyd-see"})
    assert ir.recs["taoiseach"].ids == frozenset({"pie-root-weyd-see"}) and log["sga"]["taoiseach"][2] == "via toísech"
