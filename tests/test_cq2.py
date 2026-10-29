"""Corpus-quality batch 2: production-path regressions (no review slabs or claims).

Evidence: data/research/8c/corpus-quality/error-verdicts-cq2.jsonl; docs/research/8c-corpus-quality-batch2.md."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from pie import bsl_mapping as bm
from pie import celtic_mapping as cm
from pie import compound_members as cmem
from pie import corpus_index as ci
from pie import formula_search as fs
from pie import formula_search_multi as fm
from pie import mapping as mp
from pie import material_units as mu

ROOT = Path(__file__).resolve().parents[1]
CQ = ROOT / "data/research/8c/corpus-quality"


def tok(corpus, lemma, surface, pos="noun", locus="elsewhere"):
    return fs.Token(corpus, lemma, surface, locus, {}, True, pos)


# ---------------------------------------------------------------- Greek capitalised lemmas

@pytest.mark.parametrize("corpus,lemma,surface,pos,expected,content", [
    ("grc", "Μακεδών", "Μακεδόνες", "noun", "Μακεδών (name)", False),    # ethnonym, not *meh₂ḱ-
    ("grc", "Ἀρκάς", "Ἀρκάδες", "noun", "Ἀρκάς (name)", False),          # not ἄρκτος 'bear'
    ("grc-late", "Θεσσαλός", "Θεσσαλοί", "adj", "Θεσσαλός (name)", False),
    ("hom", "Κύκλωψ", "Κύκλωψ", "noun", "Κύκλωψ (name)", False),
    ("grp", "Θρᾷξ", "Θρῇκες", "noun", "Θρᾷξ (name)", False),
    ("grc", "Ζεύς", "Ζεὺς", "noun", "Ζεύς", True),                       # THEONYMS keep lemma and ids
    ("grc-late", "Ἠώς", "Ἠώς", "noun", "Ἠώς", True),
    ("grc", "Ἥλιος", "Ἥλιος", "noun", "Ἥλιος", True),
    ("grc", "Βορέας", "Βορέας", "noun", "Βορέας", True),
    ("grc", "Καί", "Καί", "noun", "καί", False),                         # capitalised function word
    ("grc-late", "Περι", "Περι", "noun", "περι", False),
    ("grc", "Μέγας", "Μέγας", "adj", "μέγας", True),                      # adjective: lower-cased, content
    ("grc", "Φαίνω", "Φαίνεται", "verb", "φαίνω", True),                  # verb
    ("grc", "Εἰμί", "Ἐστι", "verb", "εἰμί", True),
    ("grc", "Λόγος", "Λόγος", "noun", "λόγος", True),                     # measured common list
    ("grc", "Α", "Α", "noun", "Α", False),                                # letter label
    ("grc-late", "ΔΕ", "ΔΕ", "noun", "ΔΕ", False),                        # capitals inscription
])
def test_greek_capitalised_lemmas(corpus, lemma, surface, pos, expected, content):
    t = tok(corpus, lemma, surface, pos)
    assert (t.lemma, t.content) == (expected, content)


def test_capital_rule_leaves_lowercase_and_sentence_initial_common_words():
    assert tok("grc", "καί", "Καί", "other").content is False
    assert (tok("grc", "λόγος", "Λόγος").lemma, tok("grc", "λόγος", "Λόγος").content) == ("λόγος", True)
    assert tok("grc", "μέγας", "Μέγας", "adj").content is True     # a lower-case adjective lemma stays content
    # the measured list is frozen data, written by scripts/cq2_greek_capitals.py
    table = json.loads((ROOT / "data/research/formulas/cq2-greek-capitalised.json").read_text("utf-8"))
    assert "Λόγος" in table["common"] and "Μακεδών" not in table["common"] and "Ζεύς" not in table["common"]


def test_aous_is_dawn_not_aon():
    for locus in ("Bacchylides Dithyrambi 17.42", "Pindarus Olympia 2.83"):
        t = tok("grc", "Ἀών", "Ἀοῦς", locus=locus)
        assert (t.lemma, t.content) == ("Ἠώς", True)
    assert tok("grc", "Ἀών", "Ἀόνων").lemma == "Ἀών (name)"         # the Aonians stay a name


# ---------------------------------------------------------------- Armenian gan (lead decision)

def test_gam_present_follows_the_cq1_gan_rule():
    for loc in ("MH_1_2_12_Movses_Khor ed. page 2195 - PDF page 452 (word id 82268)",
                "MH_1_1_06_Yeghishe ed. page 648 - PDF page 128 (word id 20801)"):
        t = tok("xcl", "gan", "գան", locus=loc)
        assert (t.lemma, t.content) == ("gam", True)
    # gam is reviewed as *weh₂(dʰ)- 'go' (arm-toch-alb.json, Martirosyan EDAIL 196), not *gʷem-
    assert mp.resolve_table("xcl")["gam"].ids == {"pie-root-weh2dh-go"}


# ---------------------------------------------------------------- Tier 2 round-3 mapping rows

@pytest.mark.parametrize("corpus,lemma,ids,formation", [
    ("hom", "νεφέλη", {"pie-lex-nebhelos"}, None),
    ("grp", "νεφέλη", {"pie-lex-nebhelos"}, None),
    ("grp", "νέφος", {"pie-lex-nebhos"}, None),
    ("grp", "ποίκιλμα", {"pie-lex-poykjos"}, "derivative"),
    ("grp", "εἰμί", {"pie-lex-h1esti", "pie-lex-h1esmi"}, None),
    ("hom", "εἰμί", {"pie-lex-h1esti", "pie-lex-h1esmi"}, None),
    ("rv", "√dhr̥ṣ-", {"pie-lex-dhers", "pie-root-dhers-be_bold"}, None),
    ("av", "dhṛṣ", {"pie-lex-dhers", "pie-root-dhers-be_bold"}, None),
    ("rv", "√vas- 2", {"pie-lex-westor", "pie-root-wes-dress"}, None),
    ("rv", "ūrdhvá-", {"pie-lex-h3rdhwos"}, None),
    ("av", "ūrdhva", {"pie-lex-h3rdhwos"}, None),
    ("rv", "mártya-", {"kaikki:mortyos", "pie-lex-mrtos"}, "derivative"),
])
def test_tier2_round3_rows(corpus, lemma, ids, formation):
    got, ds = mp.decide(corpus, lemma, {"wrong-auto-id"})
    assert got == ids and ds
    assert ds[-1].formation == formation


def test_avestan_mashiia_key_row_caps_the_dictionary_route():
    d = mp.path_decision(["ae:𐬨𐬀𐬴𐬌𐬌𐬀", "iir-pro:*mr̥tás", "ine-pro:*mr̥tós"], "ae")
    assert d is not None and d.derivative and "pie-lex-mrtos" in d.ids


def test_unreadable_headword_key_matches_only_itself():
    # regression: key_ae reads transliteration only, so the Avestan-script key row keyed to "" and capped
    # every Avestan-script dictionary path (16,232 ae index words keyed *mr̥tós, vohu- lost *h₁wésus)
    assert mp.path_decision(["ae:𐬬𐬊𐬵𐬎", "iir-pro:Hwásuš", "ine-pro:*h₁wésus"], "ae") is None
    assert mp.headword_key("ae", "𐬨𐬀𐬴𐬌𐬌𐬀") == "𐬨𐬀𐬴𐬌𐬌𐬀" and mp.headword_key("ae", "vohu-") == "vohu"
    ov = mp.load_overrides(ROOT)
    assert all(k for rows in ov["key"].values() for k in rows)
    assert all(k for rows in ov["form"].values() for k in rows)
    assert mp.resolve_table("ae")["vohu"].ids == {"pie-lex-h1wesus"}


@pytest.mark.parametrize("corpus,lemma,ids,formation", [
    ("sa-ep", "dam", {"pie-lex-domh2eyeti", "pie-root-demh2-tame"}, None),     # lead expansion
    ("rv", "√damⁱ-", {"pie-lex-domh2eyeti", "pie-root-demh2-tame"}, None),
    ("sa-ep", "dama", {"pie-root-demh2-tame"}, "derivative"),
    ("rv", "dám-", {"pie-lex-doxm"}, None),
    ("rv", "dáma-", {"pie-lex-doxm"}, "derivative"),
    ("av", "dama", {"pie-lex-doxm"}, "derivative"),
    ("cy", "deint", {"pie-lex-h3donts"}, "same"),
    ("celt", "focal", set(), None),
    ("celt", "focul", set(), None),
    ("rv", "√śī-", {"pie-lex-kjeytor", "pie-root-kjey-be_lying_down"}, None),   # tier2-r6
    ("av", "śī", {"pie-lex-kjeytor", "pie-root-kjey-be_lying_down"}, None),
    ("ae", "saē", {"pie-lex-kjeytor"}, None),
    ("ae", "sōire", {"pie-lex-kjeytor"}, None),
    ("ae", "jan", {"pie-lex-gwhenti"}, None),
    ("ae", "janāni", {"pie-lex-gwhenti"}, None),
    ("hom", "ἠέλιος", {"pie-lex-soh2wl"}, "derivative"),
    ("grp", "ἥλιος", {"pie-lex-soh2wl"}, "derivative"),
])
def test_cq2_late_rows(corpus, lemma, ids, formation):
    got, ds = mp.decide(corpus, lemma, {"wrong-auto-id"})
    assert got == ids and ds
    assert ds[-1].formation == formation
    if not ids:
        assert lemma not in mp.resolve_table(corpus)


def test_avestan_forms_reach_their_verbs_in_the_cab_lemmatizer():
    lem = fm.AvestanLemmatizer(fm.LangMapping("ae"), {})
    assert lem("janāni") == "jan" and lem("sōire") == "saē"
    t = mp.resolve_table("ae")
    assert t["jan"].ids == {"pie-lex-gwhenti"} and t["saē"].ids == {"pie-lex-kjeytor"}


def test_epic_lemma_decisions_win_over_the_shared_av_table():
    # build_8c_stageC.load_extra applies corpus "sa-ep" decisions after the 'av' table
    src = (ROOT / "scripts/build_8c_stageC.py").read_text("utf-8")
    assert 'mp.load_overrides(root)["decisions"].get("sa-ep", {})' in src
    assert mp.decide("sa-ep", "dama", {"x"})[0] == {"pie-root-demh2-tame"}
    assert mp.decide("av", "dama", {"x"})[0] == {"pie-lex-doxm"}


def test_welsh_neint_is_nant_not_teeth():
    assert tok("cy", "deint", "neint").lemma == "nant"
    assert tok("cy", "deint", "deint").lemma == "deint"


# ---------------------------------------------------------------- Irish

def lz(form, baseline):
    key = fm.key_sga(cm._ir_clean(form))
    return cm.CelticLemmatizer(fm.LangMapping("sga"), cm.irish_demutate, cm.irish_skeleton,
                               form_overrides={key: baseline}, use_skeleton=False)


@pytest.mark.parametrize("words,index,baseline,target", [
    (["do", "chuir", "Dia", "aingeal"], 2, "día|dia", "día@god"),
    (["ar", "gradh", "do", "Dhia"], 3, "dia", "día@god"),
    (["mac", "na", "Día"], 2, "día", "día@god"),
    (["cúigeadh", "deug", "Dia", "Sathairn"], 2, "día|dia", "día@day"),     # weekday
    (["atbert", "Cormac", "Dia", "nderntar"], 2, "día|dia", "día|dia"),      # conjunction before nasalisation
    (["ar", "Dia", "m-beo", "co"], 1, "día|dia", "día@god"),                 # 'the living God'
    (["Dia", "mbeinnsea", "etraib"], 0, "día|dia", "día|dia"),               # unit-initial: the cq1 rule
    (["in", "dos", "dítin"], 1, "gus|dos", "dos@bush"),
    (["Dos", "rala", "cum"], 0, "gus|dos", "do"),                            # preverb + infixed pronoun
    (["Dub", "Dá", "Dos", "mac"], 2, "gus|dos", "gus|dos"),                  # medial capital: the name rule
    (["fichi", "bó", "fichi", "each"], 0, "fichid", "fiche"),
    (["Fichi", "bliadan"], 0, "fichid", "fiche"),
])
def test_irish_cq2_rules(words, index, baseline, target):
    assert cm.lemmatize_words(lz(words[index], baseline), words)[index] == target


def test_dia_god_is_content_and_keeps_its_root_in_the_loader():
    assert "día@god" in cm.CQ2_DEITY_LEMMAS
    assert mp.resolve_table("celt")["día@god"].ids == {"pie-lex-deywos"}
    src = (ROOT / "scripts/build_8c_stageC.py").read_text("utf-8")
    assert "lem not in cm.CQ2_DEITY_LEMMAS" in src      # the medial-capital name marker skips Dia 'God'


# ---------------------------------------------------------------- byliny sentence-initial capitals

def test_sentence_initial_common_word_is_not_a_name():
    low = {"говоритъ", "больше"}
    text = "Тутъ князь. Говоритъ Добрыня"
    ws = bm.corpus_words("byliny", text)
    assert bm.name_flags("byliny", text, ws, low) == [False, False, False, True]
    text = "А Илья. Иванъ пошелъ"            # never written lower-case: still a name
    ws = bm.corpus_words("byliny", text)
    assert bm.name_flags("byliny", text, ws, low) == [False, True, True, False]
    text = "Больше всего. Больше"
    assert bm.name_flags("byliny", text, bm.corpus_words("byliny", text), low) == [False, False, False]
    # without punctuation context the old rule applies
    assert bm.name_flags("byliny", "князь Говоритъ", ["князь", "Говоритъ"], low) == [False, True]
    assert bm.lowercase_surfaces("byliny", [(None, None, "Илья говоритъ"), (None, None, "Больше")]) == {"говоритъ"}


def test_bessonov_essay_excluded_with_exact_boundaries():
    rows = json.loads((CQ / "material-unit-rules-cq2-other.json").read_text("utf-8"))
    assert len(rows) == 1
    f = "pesnisobrannyepnrybnikovymch2narod72_djvu.txt"
    assert mu.excluded_source("byliny", f, 21980) and mu.excluded_source("byliny", f, 38731)
    assert not mu.excluded_source("byliny", f, 21977)       # the last song's closing line
    assert not mu.excluded_source("byliny", "pesnisobrannyepnrybnikovymch4narod9_djvu.txt", 21990)


# ---------------------------------------------------------------- one work in two CELT files

def test_siaburcharpat_is_one_work():
    w = mu.same_work("sga", "G301008:#1/#1:13")
    assert w and mu.same_work("sga", "G301900:#1/#25:12") == w
    assert mu.same_work("sga", "G301900:#1/#25:12~w2") == w
    assert mu.same_work("sga", "G301900:#1/#24:12") is None
    assert mu.same_work("sga", "G301900:#1/#250:1") is None
    assert mu.same_work("vuk", "G301008:#1/#1:13") is None


# ---------------------------------------------------------------- compound members

LEMMA_IDS = {
    "grc": {"ιπποσ": frozenset({"pie-lex-h1ekjwos"}), "ανηρ": frozenset({"pie-lex-h2nexr"}),
            "θεινω": frozenset({"pie-root-gwhen-strike"}), "ονομα": frozenset({"pie-lex-h1nomn"}),
            "μενοσ": frozenset({"pie-lex-menos"}), "πουσ": frozenset({"pie-lex-poxds"}),
            "χεω": frozenset({"pie-lex-gjheweti"})},
    "sa": {"aśva": frozenset({"pie-lex-h1ekjwos"}), "nāman": frozenset({"pie-lex-h1nomn"}),
           "manas": frozenset({"pie-lex-menos"}), "pad": frozenset({"pie-lex-poxds"})},
}


@pytest.mark.parametrize("corpus,lemma,ids", [
    ("grc", "εὔιππος", {"pie-lex-h1su", "pie-lex-h1ekjwos"}),          # template εὐ- + ἵππος
    ("hom", "ἀνδροφόνος", {"pie-lex-h2nexr", "pie-root-gwhen-strike"}),  # ἀνδρο- + θείνω
    ("grc", "πολυώνυμος", {"pie-lex-pelh1u", "pie-lex-h1nomn"}),
    ("grc", "δυσμενής", {"pie-lex-dus", "pie-lex-menos"}),
    ("grc", "τετράπους", {"pie-lex-kwetwores", "pie-lex-poxds"}),
    ("rv", "suáśva-", {"pie-lex-h1su", "pie-lex-h1ekjwos"}),              # split su- + áśva-
    ("rv", "puruṇā́man-", {"pie-lex-pelh1u", "pie-lex-h1nomn"}),
    ("rv", "durmánas-", {"pie-lex-dus", "pie-lex-menos"}),
    ("rv", "dvipád-", {"pie-lex-dwoh1", "pie-lex-poxds"}),
    ("grc", "ἐκχέω", set()),                                            # preverb + verb: no compound
    ("grc", "Εὔιππος (name)", set()),
    ("grc", "ἵππος", set()),
])
def test_compound_members(corpus, lemma, ids):
    assert set(cmem.members(corpus, lemma, LEMMA_IDS[cmem.CORPUS_LANG[corpus]])) == ids


def test_members_are_posted_and_searchable_but_kept_apart(tmp_path):
    rec = dict(corpus="grc", branch="Greek", book="b", ordinal=0, key="k", locus="l", text="εὔιππος ἀνήρ",
               words=[dict(form="εὔιππος", lemma="εὔιππος", root_ids=["pie-lex-h1ekjwos"], root_groups=["g-horse"],
                           member_ids=["pie-lex-h1su"], member_groups=[]),
                      dict(form="ἀνήρ", lemma="ἀνήρ", root_ids=["pie-lex-h2nexr"], root_groups=["g-man"])])
    p = tmp_path / "i.sqlite"
    ci.build_index(p, [rec])
    idx = ci.CorpusIndex(p)
    try:
        hits = list(idx.search(roots=["pie-lex-h1su"], limit=None))
        assert len(hits) == 1 and hits[0]["words"][0]["root_ids"] == ["pie-lex-h1ekjwos"]
        assert len(list(idx.search(roots=["pie-lex-h1su", "pie-lex-h2nexr"], near=1, limit=None))) == 1
    finally:
        idx.close()


# ---------------------------------------------------------------- DCS verse citations

def test_dcs_sentence_index_is_cited_as_its_verse():
    spec = importlib.util.spec_from_file_location("search_corpora_cq2_test", ROOT / "scripts/search_corpora.py")
    sc = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = sc
    spec.loader.exec_module(sc)
    cites = sc.dcs_citations(())
    toks = {t.locus: t for t in fm.load_dcs(texts=("Atharvaveda (Śaunaka)",), corpus="av")}
    for locus, verse in (("AVŚ, 3, 16.s6", "AVŚ 3.16.3"), ("AVŚ, 12, 1.s53", "AVŚ 12.1.25")):
        t = toks[locus]
        cite, status = cites[("av", t.units["sentence"])]
        assert cite.startswith(verse) and status == "counter"
    # AVŚ 4.12 has no stanza counters: its verses are inferred, and say so
    assert cites[("av", toks["AVŚ, 4, 12.s6"].units["sentence"])][1] == "inferred"
