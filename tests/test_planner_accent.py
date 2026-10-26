"""P10 admits resolved paradigms even when their display headword lacks accent."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from pie.phon import has_accent, parse
from pie.realize import Lexicon, accent_manifest

SPEC = importlib.util.spec_from_file_location(
    "make_slice", Path(__file__).resolve().parents[1] / "scripts/make_slice.py")
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)

RESOLVED = {
    "pie-lex-h2elut", "pie-lex-suH", "pie-lex-wekwsperos", "pie-lex-dinos",
    "pie-lex-Hrewdos", "pie-lex-h1rowdhos-2", "pie-lex-leh2dhos", "pie-lex-medos",
    "pie-lex-moyth2os", "pie-lex-sterkjos", "pie-lex-stugos",
}
GLOSSED = {
    "pie-lex-h2elut", "pie-lex-suH", "pie-lex-wekwsperos", "pie-lex-dinos",
    "pie-lex-medos", "pie-lex-sterkjos",
}


@pytest.fixture(scope="module")
def lx():
    return Lexicon.load()


def test_eleven_resolved_paradigms_pass(lx):
    for lid in RESOLVED:
        assert not has_accent(parse(lx.entries[lid]["form"].strip("-")))
        assert lx.accent_status(lid) == "resolved"
        assert all(sum(s.acc for s in parse(v[0])) == 1 for v in lx.cells(lid).values())
        assert S.planner_accent_ok(lx, lid)


def test_unresolved_lexemes_stay_usable_but_out_of_planner(lx):
    for lid in accent_manifest()["unresolved_ids"]:
        assert not S.planner_accent_ok(lx, lid), lid
    assert lx.specs["pie-lex-kreydhrom"]["usable"]
    assert S.planner_accent_ok(lx, "pie-lex-ph2texr")  # representation exception, not unresolved


@pytest.mark.parametrize("cells", [
    {}, {"NOM.SG": []}, {"NOM.SG": ["medos", "médos"]},
    {"NOM.SG": ["médós"]}, {"NOM.SG": ["médos"], "VOC.SG": ["medos"]},
])
def test_manifest_absence_or_accented_alternative_is_not_evidence(cells):
    lx = SimpleNamespace(entries={"x": {"form": "medos"}}, specs={"x": {"family": "noun"}},
                         accent_status=lambda _: "resolved", cells=lambda *args: cells)
    assert not S.planner_accent_ok(lx, "x")


def test_slice_admits_six_glossed_words_and_keeps_other_gates(lx, monkeypatch, tmp_path):
    # Exercise the actual pool and output without writing a production slice or batch.
    subset = Lexicon(lx.entries, {i: lx.specs[i] for i in RESOLVED | {"pie-lex-kreydhrom"}},
                     lx.closed, lx.derived)
    monkeypatch.setattr(S.Lexicon, "load", lambda: subset)
    monkeypatch.setattr(S, "ROOT", tmp_path)
    monkeypatch.setattr(S.sys, "argv", ["make_slice.py", "accent-test", "--size", "100"])
    out = tmp_path / "data/generation/slices"
    out.mkdir(parents=True)
    assert S.main() == 0
    result = json.loads((out / "accent-test.json").read_text())
    assert {x["lex_id"] for x in result["lexemes"]} == GLOSSED
