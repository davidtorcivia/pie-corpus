"""Wave 2 source corrections and controls; no copied book running text."""
from pathlib import Path

from pie.formula_search import Token
from pie.formula_search_multi import load_overrides
from pie.material_units import byliny_wiki_lines, excluded_source
from pie.other_mapping import contextual_lemma

ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_homographs_preserve_unreviewed_contexts():
    cases = [
        ("grc", "ἔρχομαι", "ᾖσαν", "Thucydides Historiae 1.1.1 s1", "εἰμί"),
        ("grc", "ξαλες", "Κάλητα", "Thucydides Historiae 4.75.2 s1", "Κάλης (name)"),
        ("vuk", "seći", "секу", "Vuk 22093:40", "seka"),
        ("vuk", "?mrkloj", "мрклој", "Vuk 33208:10", "mrkli"),
        ("byliny", "стон|стонать", "стБну", "pesnisobrannyepvkireevskimch2pes74:203", "стена"),
        ("lv", "vilkt|vilks", "vilka", "p0216", "vilkt"),
    ]
    for c, lemma, form, locus, expected in cases:
        t = Token(c, lemma, form, locus, {}, True, "other")
        assert (t.lemma, t.surface) == (expected, form)
        assert contextual_lemma(c, lemma, form, "control") == lemma


def test_verified_stems_do_not_replace_other_paradigm_members():
    for c in ("grc", "grp", "grc-late"):
        assert contextual_lemma(c, "ὁράω", "εἶδε", "x") == "εἶδον@see"
        assert contextual_lemma(c, "λέγω", "εἶπε", "x") == "εἶπον@say"
        assert contextual_lemma(c, "ὁράω", "ὁρᾷ", "x") == "ὁράω"
        assert contextual_lemma(c, "λέγω", "λέγει", "x") == "λέγω"
    assert contextual_lemma("orv", "поити", "поидоша", "suz-lav") == "поити@go"
    assert contextual_lemma("orv", "поити", "поити", "suz-lav") == "поити"


def test_legacy_text_loader_disambiguates_before_discarding_surface():
    from pie.formula_search_multi import text_tokens
    units = [("p0216", {"song": "p0216:1046"}, ["vilka"]),
             ("control", {"song": "control"}, ["vilka"])]
    ts = text_tokens("lv", units, lambda _: "vilkt|vilks", lambda _: True)
    assert [t.lemma for t in ts] == ["vilkt", "vilkt|vilks"]


def test_reviewed_mapping_decisions_and_rejected_reports():
    ov = load_overrides(ROOT)["lemma"]
    for c, lemma, ids in [
        ("grp", "εἶδον@see", {"pie-root-weyd-see"}),
        ("grp", "εἶπον@say", {"pie-root-wekw-speak"}),
        ("orv", "поити@go", {"pie-root-h1ey-go"}),
        ("av", "svasṛ", {"pie-lex-swesoxr"}),
    ]:
        assert set(ov[c][lemma][0]) == ids
    for lemma in ("Ἴων", "Φρυγία", "Ναύκρατις", "Ὅμηρος"):
        assert not ov["grp"][lemma][0]
    assert ov["hom"]["ἀφύσσω"][1]["uncertain"]


def test_reviewed_notes_do_not_shift_numbering_or_affect_other_pages():
    rows = [("425083", "song", 128, "verse"),
            ("425083", "song", 129, "Примечания"),
            ("425083", "song", 130, "editorial"),
            ("next", "other", 1, "verse"),
            ("next", "other", 2, "Примечания")]
    assert list(byliny_wiki_lines(rows)) == [rows[0], rows[3], rows[4]]
    assert excluded_source("byliny", "10945725bsb_djvu.txt", 14048)
    assert not excluded_source("byliny", "10945725bsb_djvu.txt", 14054)
    assert excluded_source("celtic", "revueceltique13pari_djvu.txt", 1311, 1312)


def test_menota_comments_are_removed_before_embedded_tags_are_parsed(tmp_path):
    from pie.germanic_new_mapping import menota_words
    xml = ('<text><pb n="75"/><w><me:dipl>'
           '<!--</add> removed CHECK FG--><!--flb-->Halfdan</me:dipl></w>'
           '<!--<w><me:dipl>editorial</me:dipl></w>-->'
           '<pb n="129"/><w><me:dipl><!--<me:punct>&comma;</me:punct>'
           ' not visible in picture FG --><hi>&thorn;a</hi></me:dipl></w></text>')
    p = tmp_path / "sample.xml"
    p.write_text(xml)
    ws = menota_words(p, "sample")
    assert [(w.folio, w.form) for w in ws] == [("75", "Halfdan"), ("129", "þa")]
