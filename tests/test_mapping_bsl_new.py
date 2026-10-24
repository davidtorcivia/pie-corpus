"""Balto-Slavic round-4 mappings (pie/bsl_mapping.py, scripts/build_bsl_mapping.py): keys, spelling
variants, the CCMH transliteration, the strict union rule, and the shipped tables and override file.
Fixtures are invented records or dictionary headwords, not corpus text."""

import json
from pathlib import Path

import pytest

from pie import bsl_mapping as bm
from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "data/research/formulas/mapping"
OVR = ROOT / "data/research/formulas/mapping-overrides/balto-slavic-new.json"
CORPORA = ("vuk", "byliny", "dainos", "ccmh")


def lexicon_ids():
    return {json.loads(l)["id"] for l in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines() if l}


# ---------------------------------------------------------------- keys and normalisation

def test_keys():
    assert bm.key_sh("зѐмља") == bm.key_sh("zèmlja") == "zemlja"
    assert bm.key_sh("ћу") == "ću" and bm.key_sh("ћу", True) != bm.key_sh("чу", True)   # Vuk's ћу is not чу
    assert bm.key_sh("ѝћи") == "ići"                                                     # precomposed Cyrillic accents
    assert bm.key_ru("землѣ́") == "земле" and bm.key_ru("богъ") == "бог" and bm.key_ru("ёлка") == "елка"
    assert bm.key_ru("объ") == "об" and bm.key_ru("объезд") == "объезд" and bm.key_ru("й") == "й"
    assert bm.key_lt("žẽmė") == "žemė" and bm.key_lt("dievas") == "dievas" and bm.key_lt("ąžuolas", True) == "azuolas"
    assert bm.lt_norm("szirdis") == "širdis" and bm.lt_norm("ůsis") == "uosis" and bm.lt_norm("żwakė") == "žvakė"


def test_spelling_variants():
    assert "или" in bm.vuk_variants("ил'")                       # elision
    assert "дјевојка" in bm.vuk_variants("ђевојка")              # Vuk's jotation
    assert "хоћу" in bm.vuk_variants("оћу")                      # dropped initial х
    assert "бијелим" in bm.vuk_variants("бијелијем")             # ijekavian long ending
    v = bm.ru_variants("добраго")
    assert "доброго" in v
    assert "чистую" in bm.ru_variants("чисту") and "пошел" in bm.ru_variants("пошол")
    assert "себе" in bm.ru_variants("себ")                       # OCR lost the final ѣ
    assert bm.ru_norm_ocr("в$ренъ") == "вѣренъ" and bm.ru_norm_ocr("отношен1я") == "отношенія"
    lt = bm.lt_variants("brolelej")
    assert "broleliai" in lt
    assert bm.HEAD_ONLY + "laivas" in bm.lt_variants("laivužis")  # diminutives reach headwords only


def test_ccmh_transliteration():
    assert bm.ccmh_word("dar&") == "даръ"
    assert bm.ccmh_word("pr@d&") == "прѣдъ"
    assert bm.ccmh_word("svojO") == "своѭ"
    assert bm.ccmh_word("ljuby") == "любꙑ"
    assert bm.ccmh_word("!gljO") is None                          # under titlo: an abbreviation
    assert bm.ccmh_word("sl?vo") is None
    assert fm.key_cu(bm.ccmh_word("uv@qajE", "marianus")) == fm.key_cu("оувѣщаѩ")


def test_main_word_of_multiword_forms():
    assert bm._main_word("ìšao sam", "ìći") == "ìšao"
    assert bm._main_word("бу́ду идти́", "идти́") == "идти́"
    assert bm._main_word("sagledao se", "sagledati") == "sagledao"


def test_intra_family_borrowing():
    d = {"word": "солнце", "etymology_templates": [
        {"name": "lbor", "args": {"1": "ru", "2": "zle-mru", "3": "солнце"}},
        {"name": "der", "args": {"1": "ru", "2": "sla-pro", "3": "*sъlnьce"}}]}
    e = fm.parse_entry(bm._intra_family(d, "ru"), "ru")
    assert not e.rejected and ("sla-pro", "*sъlnьce", "der") in e.links
    cs = {"word": "глава", "etymology_templates": [{"name": "bor", "args": {"1": "ru", "2": "cu", "3": "глава"}}]}
    e = fm.parse_entry(bm._intra_family(cs, "ru"), "ru")
    assert not e.rejected and e.links == [("cu", "глава", "der")]
    loan = {"word": "x", "etymology_templates": [{"name": "bor", "args": {"1": "ru", "2": "trk-pro", "3": "y"}}]}
    assert fm.parse_entry(bm._intra_family(loan, "ru"), "ru").rejected


def test_lithuanian_verb_forms():
    f = bm.lt_verb_forms("nešti", "neša", "nešė")
    assert {"nešu", "neši", "nešame", "nešiau", "nešei", "neš", "nešk", "neštų"} <= f
    assert "manę" not in bm.lt_verb_forms("manyti", "mano", "manė")     # 'me', not a participle of manyti


def test_strict_union_rule():
    lm = fm.LangMapping("sh")
    rec = lambda k, ids: fm.MapRec(k, k, frozenset(ids), (f"sh:{k}",), "chain", "high", ())
    lm.recs.update({"dan": rec("dan", {"pie-lex-dinos"}), "dati": rec("dati", {"pie-lex-dedeh3ti"}),
                    "drag": rec("drag", {"pie-lex-x"}), "vidjeti": rec("vidjeti", {"pie-root-weyd-see"})})
    lm.lemma_words |= {"draga", "videti", "reći"}
    g = {}
    assert bm.map_lemma("dan|dati", lm, g) is None                       # different etyma
    assert bm.map_lemma("drag|draga", lm, g).ids == {"pie-lex-x"}       # same stem, one part unmapped
    assert bm.map_lemma("vidjeti|videti", lm, g).ids == {"pie-root-weyd-see"}   # ijekavian / ekavian
    assert bm.map_lemma("reći|dati", lm, g) is None                      # unmapped part of another stem
    assert bm.map_lemma("?xyz", lm, g) is None


def test_names_are_not_mapped():
    assert bm.is_name("vuk", "Иве", 3) and not bm.is_name("vuk", "Иве", 0) and not bm.is_name("ccmh", "J", 2)


# ---------------------------------------------------------------- shipped tables and overrides

def _table(c):
    p = TABLES / f"{c}.jsonl"
    if not p.exists():
        pytest.skip(f"{p} not built")
    return [json.loads(l) for l in p.read_text("utf-8").splitlines() if l.strip()]


def test_tables_format_and_licence():
    ids = lexicon_ids()
    for c in CORPORA:
        rows = _table(c)
        assert len(rows) > 1000, c
        for r in rows[:: max(1, len(rows) // 400)]:
            assert r["corpus"] == c and r["lang"] == bm.CORPUS_LANG[c]
            assert set(r) >= {"lemma", "word", "lex_id", "path", "how", "confidence", "sources", "tokens", "licence",
                              "mapping_licence"}
            assert r["lex_id"] and all(i in ids or i.startswith("kaikki:") for i in r["lex_id"]), r
            assert set(r["licence"]) <= set(bm.SOURCES[c]), r
        attested = [r for r in rows if r["tokens"]]
        assert attested and all(r["licence"] for r in attested)


def test_override_file():
    d = json.loads(OVR.read_text("utf-8"))
    ids = lexicon_ids()
    for r in d["lemma"]:
        assert r["corpus"] in CORPORA and r["note"] and r["erratum"] and all(i in ids for i in r["lex_id"])
    for r in d["proto"]:
        assert r["code"] in ("sla-pro", "ine-bsl-pro", "bat-pro") and r["term"].startswith("*") and r["note"]
        assert all(i in ids for i in r["lex_id"])
    for r in d["key"]:
        assert r["lang"] in ("sh", "ru", "lt", "cu") and r["note"] and all(i in ids for i in r["lex_id"])
    assert not d["form"]          # form rows for sh/ru/lt would break fm.load_overrides without this module
    ov = fm.load_overrides(ROOT)
    assert ov["lemma"]["ccmh"]["богъ"][0] == frozenset()


LOANS = {"vuk": ("bog", "car", "knjiga", "kula", "puška", "sablja", "vino", "raj"),
         "byliny": ("бог", "богатый", "богатырь", "рай", "собака", "топор", "князь", "хлеб", "шлем", "лошадь", "царь"),
         "ccmh": ("богъ", "божии", "богатъ", "хлѣбъ", "кънѧзь", "цѣсарь"),
         "dainos": ("dvaras_is_inherited",)}


def test_loan_vetoes_hold():
    for c, words in LOANS.items():
        t = bm.read_table(c, ROOT) if (TABLES / f"{c}.jsonl").exists() else pytest.skip("tables not built")
        for w in words:
            if not w.endswith("_is_inherited"):
                assert w not in t, (c, w, t.get(w))


KNOWN = {"vuk": {"zemlja": "pie-lex-dhegjhoxm", "voda": "pie-lex-wodr", "sin": "pie-lex-suHnus",
                 "brat": "pie-lex-bhreh2texr", "biti": None, "grad": None, "jesam": "pie-root-h1es-be"},
         "byliny": {"земля": "pie-lex-dhegjhoxm", "вода": "pie-lex-wodr", "мать": "pie-lex-meh2texr",
                    "сын": "pie-lex-suHnus", "быть": "pie-root-bhuH-be", "солнце": "pie-lex-soh2wl", "град": None},
         "dainos": {"dievas": "pie-lex-deywos", "saulė": "pie-lex-soh2wl", "žemė": "pie-lex-dhegjhoxm",
                    "sūnus": "pie-lex-suHnus", "aukštas": "pie-root-h2ewg-increase"},
         "ccmh": {"бꙑти": "pie-root-bhuH-be", "есмь": "pie-root-h1es-be", "землѧ": "pie-lex-dhegjhoxm"}}


def test_known_mappings():
    for c, words in KNOWN.items():
        if not (TABLES / f"{c}.jsonl").exists():
            pytest.skip("tables not built")
        t = bm.read_table(c, ROOT)
        for w, want in words.items():
            if want is None:
                assert w not in t, (c, w, t.get(w))          # homograph of different etyma: unmapped
            else:
                assert want in t.get(w, ()), (c, w, t.get(w))
