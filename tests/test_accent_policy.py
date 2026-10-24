"""Accent policy (David, 2026-10-24): a lexeme whose headword has no accent stays usable and is classified
accent: unresolved (missing information, not evidence of an unaccented word). The manifest
data/morph/accent_unresolved.json is the one source; reports and exported tasks carry the status, and the
accent-sensitive eval view omits the unresolved tasks."""

import random

import pytest

from pie import export
from pie.phon import has_accent as phon_has_accent, parse
from pie.realize import Lexicon, accent_manifest, accent_status
from pie.validate import has_accent

KREYDHROM = "pie-lex-kreydhrom"     # kreydʰrom 'sieve': unaccented headword, an inflection and a cognate eval task


@pytest.fixture(scope="module")
def lx():
    return Lexicon.load()


def test_status_lookup(lx):
    assert lx.accent_status(KREYDHROM) == accent_status(KREYDHROM) == "unresolved"
    assert lx.accent_status("pie-lex-ph2texr") == "resolved"          # a representation exception, not missing info
    assert lx.accent_status("pie-lex-kwe") == "resolved"              # a genuinely unaccented clitic
    assert accent_status("closed:particles/ne") == accent_status(None) == "resolved"
    m = accent_manifest()
    assert len(m["unresolved_ids"]) == sum(f["lexemes"] for f in m["unresolved_lexical_accent"]["by_family"].values())
    # the usable flag is unchanged: unresolved lexemes still inflect
    assert all(lx.specs[i]["usable"] for i in m["unresolved_ids"])
    # every unresolved lexeme's headword really has no accent (by the phonological parser, not a search for ´)
    assert not any(phon_has_accent(parse(lx.entries[i]["form"].strip("*-").replace("-", ""))) for i in m["unresolved_ids"])


def test_parser_does_not_read_the_palatal_acute_as_an_accent():
    for f in ("ḱerd", "ǵenh₁os", "ḱerh₂wos", "ǵʰleystos"):
        assert not has_accent(f) and not phon_has_accent(parse(f)), f
    for f in ("ḱérd", "ǵénh₁os", "ḱléwos", "h₁éḱwos"):
        assert has_accent(f) and phon_has_accent(parse(f)), f


def test_inflection_and_cognate_tasks_carry_the_flag(lx):
    inf = [t for t in export.inflection_tasks(lx, random.Random(0)) if t["source_id"] == KREYDHROM]
    assert inf and all(t["accent"] == "unresolved" for t in inf)
    cog = [t for t in export.cognate_tasks(lx) if t["source_id"] == KREYDHROM]
    assert cog and all(t["accent"] == "unresolved" for t in cog)
    # a resolved lexeme's tasks carry no flag
    assert not any(t.get("accent") for t in export.cognate_tasks(lx) if t["source_id"] == "pie-lex-kjlewos")


def test_record_tasks_flag_engine_records_only():
    tok = {"form": "kreydʰrom", "lex_id": KREYDHROM, "features": "ACC.SG"}
    rec = {"id": "t3-x-00001", "tier": 3, "pie": "kreydʰrom", "english": "a sieve", "gloss": "sieve.ACC", "tokens": [tok]}
    assert {t["accent"] for t in export.record_tasks(rec)} == {"unresolved"}
    assert not any("accent" in t for t in export.record_tasks({**rec, "tier": 1}))      # the author's accents
    voc = {"form": "ph₂ter", "lex_id": "pie-lex-ph2texr", "features": "VOC.SG"}
    assert {t["accent"] for t in export.record_tasks({**rec, "tokens": [voc]})} == {"representation"}


def test_accent_sensitive_view_omits_kreydhrom(lx):
    tasks = export.inflection_tasks(lx, random.Random(0)) + export.cognate_tasks(lx)
    view = export.accent_specified(tasks)
    assert not [t for t in view if t["source_id"] == KREYDHROM]
    assert not [t for t in view if t.get("accent") == "unresolved"]
    assert len(view) == len([t for t in tasks if t.get("accent") != "unresolved"]) < len(tasks)


def test_unresolved_reasons_name_listed_lexemes():
    rec = accent_manifest()["unresolved_lexical_accent"]
    assert rec["reasons"] and set(rec["reasons"]) <= accent_manifest()["unresolved_ids"]
