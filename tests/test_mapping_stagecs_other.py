"""Reviewed C-S errors: preserve homonyms and reject spurious root candidates."""
from pathlib import Path

from pie import formula_search as fs
from pie import formula_search_multi as fm
from pie import germanic_new_mapping as gm
from pie import other_mapping as om

ROOT = Path(__file__).resolve().parents[1]


def test_menota_names_do_not_consume_common_words():
    for lemma in ("bera", "bjǫrn", "oddr", "helga"):
        assert gm.reviewed_menota_lemma(lemma, "xNP gM", "X") == lemma + " (name)"
        assert gm.reviewed_menota_lemma(lemma, "xNC gM", "X") == lemma
    assert gm.reviewed_menota_lemma("bera", "xVB", "Ber") == "bera"
    assert gm.reviewed_menota_lemma(None, "", "Beru") is None


def test_menota_byname_is_contextual():
    assert gm.reviewed_menota_lemma("máni", "xNC", "mána", "AM-113-b-fol", "Þorkels") == "máni (name)"
    assert gm.reviewed_menota_lemma("máni", "xNC", "mána", "AM-113-b-fol", "sá") == "máni"


def test_menota_source_tags_split_homonyms():
    assert gm.reviewed_menota_lemma("egg", "xNC gF nS", "egg") == "egg@edge"
    assert gm.reviewed_menota_lemma("egg", "xNC gN nS", "egg") == "egg"
    assert gm.reviewed_menota_lemma("nema", "xVB", "nam") == "nema@take"
    assert gm.reviewed_menota_lemma("nema", "xCC", "nema") == "nema"
    assert gm.reviewed_menota_lemma("vár", "xNC", "várit") == "vár@spring"
    assert gm.reviewed_menota_lemma("vár", "xAJ", "vár") == "vár"


def test_homer_fire_and_motion_are_separate():
    assert om.homer_lemma("αὔω", "αὔοι") == "αὔω@kindle"
    assert om.homer_lemma("αὔω", "ἤϋσεν") == "αὔω"
    assert om.homer_lemma("ἔπειμι", "ἐπιόντα") == "ἔπειμι@go"
    assert om.homer_lemma("ἔπειμι", "ἔπεστι") == "ἔπειμι"


def test_latin_lexical_identifiers_disambiguate():
    assert om.latin_lemma("edo", "edere", ["lilaLemma:100577"]) == "edo@give"
    assert om.latin_lemma("edo", "edere", []) == "edo"
    assert om.latin_lemma("os", "oris", ["lilaLemma:115327"]) == "os@mouth"
    assert om.latin_lemma("os", "ossis", []) == "os"


def test_suppletive_sanskrit_is_stem_sensitive():
    assert om.dcs_lemma("dṛś", "paśyataḥ") == "paś@see"
    assert om.dcs_lemma("dṛś", "dṛṣṭa") == "dṛś"
    assert om.dcs_lemma("paś", "paśyati") == "paś"


def test_contextual_corrections_reach_shared_tokens_and_preserve_controls():
    for corpus, lemma, form, locus, expected in [
        ("menota", "mál", "mól", "AM-63-fol 326:", "mala"),
        ("menota", "móðr", "mǫðr", "AM-36-fol 473:29", "móðir"),
        ("menota", "heill", "heila", "AM-36-fol 427:29", "heili"),
        ("menota", "vinr", "vín", "AM-242-fol 24:10", "vín"),
        ("xcl", "haw", "հաւուց։", "MH_1_1_06_Yeghishe ed. page 579 - PDF page 59 (word id 9391)", "haw@ancestor"),
        ("xcl", "geł", "գեղն՝", "MH_1_1_04_Faustos ed. page 428 - PDF page 152 (word id 61990)", "geł@village"),
        ("cy", "cae", "kae", "welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L17235-L17250", "cau@close"),
    ]:
        token = fs.Token(corpus, lemma, form, locus, {}, True, "noun")
        assert token.lemma == expected
        assert token.surface == form
        assert om.contextual_lemma(corpus, lemma, form, "unreviewed locus") == lemma


def test_hittite_review_selects_source_alternative_only_at_locus():
    a = {"trans": "ešta", "mrp0sel": "1", "mrp1": "eš-@sitzen@2SG.PST@I.1.1.1@",
         "mrp2": "eš-@sein@{ a → 2.SG.PST} { b → 3SG.PST}@I.2.3@"}
    fixed = om.hittite_selection(a, "KUB 36.89", "Rs. 57′")
    assert fm.hit_analysis(fixed)[0] == "eš-@sein"
    assert om.hittite_selection(a, "another tablet", "Rs. 57′") is a
    assert a["mrp0sel"] == "1"


def test_overrides_remove_wrong_candidates_without_erasing_other_senses():
    ov = fm.load_overrides(ROOT)
    def ids(c, l):
        return set(ov["lemma"][c][l][0])
    assert ids("hom", "αὔω") == set()
    assert ids("hom", "Τυδεύς") == set()
    assert ids("grp", "Κῦρος") == set()
    assert ids("hom", "ἀφύσσω") == {"pie-root-h2ews-draw_water"}
    assert ov["lemma"]["hom"]["ἀφύσσω"][1]["uncertain"]
    assert ids("menota", "egg@edge") == {"pie-lex-h2ekjih2"}
    assert ids("menota", "nema@take") == {"pie-lex-nemeti"}
    assert ids("ang", "swat|swāt") == {"pie-root-sweyd-sweat"}
    assert ids("cy", "maur") == {"pie-lex-meh2ros"}


def test_real_homer_and_latin_loaders_use_reviewed_lemmas():
    if not (ROOT / fs.HOMER).exists():
        return
    h = fs.load_homer(ROOT)
    assert any(t.surface == "αὔοι" and t.lemma == "αὔω@kindle" for t in h)
    assert any(t.locus == "Il. 13.477" and t.lemma == "ἔπειμι@go" for t in h)
    l = fs.load_latin(ROOT)
    assert any(t.locus == "LucrDRN6 6.1258" and t.lemma == "edo@give" for t in l)
    assert any(t.locus == "LucrDRN2 2.511" and t.lemma == "os@mouth" for t in l)
