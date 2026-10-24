"""Status of non-primary forms (docs/audits/alt-form-status.md): primary and supported forms validate
exact, legacy forms as tier "legacy" (a warning), rejected forms as a known error; the accent lint."""

import json
import re
from pathlib import Path

import pytest

from pie.validate import FormIndex, all_exact, has_accent, validate_text

ROOT = Path(__file__).resolve().parent.parent
FISH = {"strong": "dʰǵʰúH", "weak": "dʰǵʰuH", "accent_class": "hysterokinetic", "gender": "m",
        "nom_sg": None, "loc_sg": [], "devi": False, "adjective": False}


def _mini(status: str, note: str = "a note") -> FormIndex:
    """'fish' with its displaced Wiktionary spec (the thematization note read as a weak stem)."""
    old = {**FISH, "weak": "dʰǵʰúH-o", "accent_class": "acrostatic"}
    lex = [{"id": "fish", "kind": "word", "form": "dʰǵʰúHs", "root_id": None, "gender": "m"}]
    specs = [{"id": "fish", "rule": "table", "family": "noun", "spec": FISH, "usable": True,
              "extra_specs": [{"family": "noun", "spec": old, "displaced_by_override": True,
                               "status": status, "status_note": note}]}]
    return FormIndex(lex, specs, {})


def test_status_plumbing_and_gate():
    for status, tier, verdict, gate in (("supported", "exact", "pass", True), ("legacy", "legacy", "warn", False),
                                        ("rejected", "rejected", "fail", False)):
        ix = _mini(status, "mis-parsed")
        v = validate_text("dʰǵʰúHoey", ix)
        t = v["tokens"][0]
        assert t.status == status and t.tier == tier and v["status"] == verdict, (status, v)
        assert all_exact(v) is gate          # realize_plans' all_exact gate, Tier 1/2 "verified"
    # a form both specs generate keeps the primary analysis only
    v = validate_text("dʰǵʰúHs dʰǵʰuHéy", _mini("rejected"))
    assert all_exact(v) and v["status"] == "pass"
    assert {a.status for t in v["tokens"] for a in t.analyses} == {"primary"}
    # unclassified displaced specs default to legacy
    ix = _mini("legacy")
    ix2 = FormIndex(list(ix.lex.values()), [{**r, "extra_specs": [{k: x for k, x in e.items() if k != "status"}
                                                                  for e in r["extra_specs"]]}
                                            for r in ix.specs.values()], {})
    assert validate_text("dʰǵʰúHoey", ix2)["tokens"][0].tier == "legacy"


@pytest.fixture(scope="module")
def ix():
    if not (ROOT / "data" / "morph" / "inflection_specs.jsonl").exists():
        pytest.skip("specs not built")
    from pie.validate import load_index
    return load_index()


def test_fish_dative_is_a_known_error(ix):
    """David's review: the mis-parsed dat. dʰǵʰúHoey validated as pass / exact / engine:table."""
    v = validate_text("dʰǵʰúHoey", ix)
    t = v["tokens"][0]
    assert v["status"] == "fail" and v["coverage"] == 0.0 and not t.found
    assert t.miss == "known-error" and t.miss_detail.startswith("known error: ") and "mis-parsed" in t.miss_detail
    assert t.rejected and all(a.lex_id == "pie-lex-dhgjhuHs" for a in t.rejected)
    assert not all_exact(v)
    v = validate_text("dʰǵʰuHéy", ix)                   # the primary dative
    assert v["status"] == "pass" and v["tokens"][0].status == "primary"


def test_rejected_table_cells_share_the_status(ix):
    """The verbatim Wiktionary cells of an overridden table are not a back door (gʷénh₂s, unhyphenated)."""
    v = validate_text("gʷénh₂s", ix)
    t = v["tokens"][0]
    assert t.miss == "known-error" and any(a.source == "wiktionary-cell" for a in t.rejected)
    assert validate_text("gʷénh₂ gʷḗn", ix)["status"] == "pass"     # the alternative cell and the primary


def test_legacy_alternative(ix):
    v = validate_text("yókʷr̥", ix)                     # the old headword, kept as a variant
    assert v["tokens"][0].tier == "legacy" and v["status"] == "warn" and v["legacy"] == ["yókʷr̥"]
    assert not all_exact(v)
    assert all_exact(validate_text("yḗkʷr̥", ix))


def test_supported_alternative(ix):
    v = validate_text("h₁dénti pléth₂us", ix)          # convention alternatives (h₁ed- D1, u-adjectives)
    assert all_exact(v) and v["status"] == "pass"
    assert [t.status for t in v["tokens"]] == ["supported", "supported"]


def test_every_displacement_is_classified_and_listed():
    doc = (ROOT / "docs" / "audits" / "alt-form-status.md").read_text("utf-8")
    listed = dict(re.findall(r"^\| `(pie-lex-[^`]+)` \|[^|]*\| (supported|legacy|rejected) \|", doc, re.M))
    for x in (ROOT / "data" / "morph" / "inflection_specs.jsonl").read_text("utf-8").splitlines():
        r = json.loads(x)
        for e in r["extra_specs"]:
            assert e["status"] in ("supported", "legacy", "rejected"), r["id"]
            if e.get("displaced_by_override"):
                assert listed.get(r["id"]) == e["status"], r["id"]


def test_accent_lint(ix):
    assert has_accent("ḱléwos") and not has_accent("ḱerd")      # the palatal acute is not an accent
    v = validate_text("ph₂tḗr ph₂ter h₁éḱwōs-kʷe ne kʷis gʰe", ix)
    # the vocative ph₂ter is a representation exception, not a defect; the enclitic, the particle ne, the
    # indefinite and gʰe are genuinely unaccented (exempt)
    assert v["accentless"] == [] and v["accent_representation"] == ["ph₂ter"] and v["accent_unresolved"] == []
    assert v["status"] == "pass"                # a lint, not a status change
    # an unresolved-accent lexeme (kreydʰrom: the headword has no accent) is missing information, not a defect;
    # a resolved word written without its accent is a defect
    v = validate_text("kreydʰrom bʰereti", ix)
    assert v["accent_unresolved"] == ["kreydʰrom"] and v["accentless"] == ["bʰereti"]
