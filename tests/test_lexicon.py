import json
from pathlib import Path

import pytest

from pie.lexicon import gloss_tag, parse_form, slug
from pie.translit import is_canonical

LEX = Path(__file__).resolve().parent.parent / "data" / "lexicon"


@pytest.mark.parametrize("raw,lemma,segmented,variants,stems", [
    ("*bʰér-e-ti", "bʰéreti", "bʰér-e-ti", [], []),
    ("bʰer-", "bʰer-", None, [], []),
    ("*-éyeti", "-éyeti", None, [], []),
    ("*bʰer-H-men-", "bʰerHmen-", "bʰer-H-men-", [], []),
    ("(s)teg-", "steg-", None, ["teg-"], []),
    ("tú(h₂)", "túh₂", None, ["tú"], []),
    ("g⁽ʷ⁾ew-", "gʷew-", None, ["gew-"], []),
    ("*gʰrewh₂-ǵ(ʰ)-", "gʰrewh₂ǵʰ-", "gʰrewh₂-ǵʰ-", ["gʰrewh₂ǵ-"], []),
    ("*pér-wr̥ ~ *pr̥-wén-s", "pérwr̥", "pér-wr̥", [], ["pérwr̥", "pr̥wéns"]),
])
def test_parse_form(raw, lemma, segmented, variants, stems):
    p = parse_form(raw)
    assert p.reject is None
    assert (p.lemma, p.segmented, p.variants, p.stems) == (lemma, segmented, variants, stems)


@pytest.mark.parametrize("raw", [
    "Ø-és", "(∅)-(é)-", "*pr̥s- ~ *pors-V́-", "*ǵʰl̥h₃-T-tó-s", "*s(ə)p-yé-ti or *sh₁p-yé-ti",
    "*sup-r̥-yé/ó-ti", "*mogʰ-tus?", "*keh₂-tó-s, *kh₂-tó-s", "tī̆́",
])
def test_parse_form_rejects(raw):
    assert parse_form(raw).reject


def test_parse_form_repairs_homoglyph_and_laryngeal_ring():
    p = parse_form("*mṛh₂-ό-")
    assert p.lemma == "mr̥h₂ó-" and "G-HOMOGLYPH" in p.rules
    assert parse_form("*gʰh̥₁bʰ-yé-ti").lemma == "gʰh₁bʰyéti"


def test_ids():
    assert slug("h₂ówis") == "h2owis"
    assert slug("ḱléwos") == "kjlewos"
    assert slug("bʰēr-eh₂") == "bhexreh2"
    assert gloss_tag("to bear, carry") == "bear"
    assert gloss_tag("(transitive) to stand out, to tower") == "stand_out"
    assert gloss_tag(None) == "nogloss"


# --- integrity of the built lexicon (skipped until it is built) -------------

def _load(name):
    p = LEX / name
    if not p.exists():
        pytest.skip(f"{name} not built")
    return [json.loads(line) for line in p.read_text("utf-8").splitlines()]


def test_lexicon_integrity():
    lex = _load("lexicon.jsonl")
    ids = {e["id"] for e in lex}
    assert len(ids) == len(lex), "duplicate ids"
    for e in lex:
        assert is_canonical(e["form"]), e["id"]
        assert all(is_canonical(v) for v in e["variants"] + e["stems"]), e["id"]
        if e.get("segmented"):
            assert is_canonical(e["segmented"]), e["id"]
        refs = [e.get("root_id"), *e.get("parents", []), *e.get("derivatives", []), *e.get("target_ids", [])]
        for ref in refs:
            assert ref is None or ref in ids, (e["id"], ref)
        if e["kind"] == "root":
            assert e["id"].startswith("pie-root-") and e["root_id"] == e["id"]
            assert e["root_type"] in ("verbal", "nominal")


def test_root_links_point_at_roots():
    lex = _load("lexicon.jsonl")
    kinds = {e["id"]: e["kind"] for e in lex}
    for e in lex:
        if e.get("root_id"):
            assert kinds[e["root_id"]] == "root", e["id"]


def test_parent_child_symmetry():
    lex = _load("lexicon.jsonl")
    by = {e["id"]: e for e in lex}
    for e in lex:
        for c in e.get("derivatives", []):
            assert e["id"] in by[c].get("parents", []), (e["id"], c)


def test_paradigms_clean():
    paras = _load("paradigms.jsonl")
    assert len(paras) > 500
    for p in paras:
        assert p["source"] == "wiktionary-module"
        for cell in p["cells"]:
            assert cell["forms"] and all(is_canonical(f) for f in cell["forms"])


def test_registry_covers_lexicon():
    lex = _load("lexicon.jsonl")
    reg = {r["id"] for r in _load("id_registry.jsonl")}
    assert {e["id"] for e in lex} <= reg


def test_homonym_derivatives_stay_apart():
    # Regression (provisional review, 2026-10-23): two *kretós under the two
    # *kret- homograph roots were merged into one entry with both meanings.
    lex = _load("lexicon.jsonl")
    kretos = [e for e in lex if e["form"] == "kretós"]
    assert len(kretos) == 2
    assert {e["root_id"] for e in kretos} == {"pie-root-kret-be_strong", "pie-root-kret-shake"}


def test_reflexes_deduped_and_loans_flagged():
    lex = _load("lexicon.jsonl")
    n_borrowed = 0
    for e in lex:
        for lang, refl in e.get("reflexes", {}).items():
            keys = [(r["form"], r.get("roman")) for r in refl]
            assert len(keys) == len(set(keys)), (e["id"], lang)
            n_borrowed += sum(1 for r in refl if r.get("borrowed"))
    assert n_borrowed > 400
