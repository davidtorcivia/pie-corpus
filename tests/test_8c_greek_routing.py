"""Production research loaders with shipped Greek links and reviewed decisions."""

import importlib.util
import sys
from pathlib import Path

import pytest

from pie import formula_search as fs
from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("eng02_stageC", ROOT / "scripts/build_8c_stageC.py")
C = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = C
spec.loader.exec_module(C)

EXPECTED = {
    "ὦμος": ("pie-lex-h2oxms",),
    "ἕπομαι": ("pie-root-sekw-follow",),
    "δαμάζω": ("pie-root-demh2-tame",),
    "ὠμός": ("pie-lex-h2eh3mos",),
    "eng02-unmapped-probe": (),
}


@pytest.fixture(scope="module")
def inputs():
    lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
    toks = [fs.Token("grc", w, w, f"probe {i}", {"book": "probe", "line": f"probe:{i}"},
                     True, "verb" if w in ("ἕπομαι", "δαμάζω") else "noun")
            for i, w in enumerate(EXPECTED)]
    return lex, fs.group_map(lex), toks


@pytest.mark.parametrize("corpus", ["grc", "grc-late"])
def test_reviewed_greek_loader(corpus, inputs, monkeypatch):
    lex, groups, toks = inputs
    selection = [{"TLG": "probe", "SOURCE_LICENSE": "CC BY-SA 4.0"}]
    monkeypatch.setattr(C.SB, "glaux_selection_b", lambda root: selection)
    monkeypatch.setattr(C, "glaux_late_selection", lambda root: selection)
    monkeypatch.setattr(C.SB, "load_glaux_b", lambda sel, root: (toks, [t.surface for t in toks]))
    loader = C.SB.load_greek_b if corpus == "grc" else C.load_greek_late
    units, count = loader(ROOT, lex, groups)
    C.B.assign_pids({corpus: units})
    assert count == 1
    assert {lemma: ids for u in units for _, lemma, ids in u.words} == EXPECTED
    assert [u.key for u in units] == [t.units["line"] for t in toks]
    assert [u.locus for u in units] == [t.locus for t in toks]
    assert all(u.corpus == corpus and u.book == "probe" for u in units)
    assert [u.pid for u in units] == [f"{corpus}:{t.locus}" for t in toks]
    assert all(u.licence == "GLAUx; source text licence: CC BY-SA 4.0" for u in units)
    assert all(not u.research_only for u in units)


def test_homer_keeps_hom_population(inputs, monkeypatch):
    lex, groups, toks = inputs
    backoff = fs.build_homer_mapping(lex, toks)
    original = fm.apply_lemma_overrides
    baseline = original("hom", fs.build_kaikki_mapping("grc", lex, toks, backoff, pseudo=True), groups)
    calls = []

    def observed(population, *args, **kwargs):
        calls.append(population)
        return original(population, *args, **kwargs)

    monkeypatch.setattr(fm, "apply_lemma_overrides", observed)
    actual = C.SB.live("hom", "grc", toks, backoff, lex, groups, ROOT)
    assert actual == {k: tuple(v) for k, v in baseline.lemma_lex.items()}
    assert calls == ["hom"]
    assert {w: actual.get(w, ()) for w in EXPECTED} == EXPECTED
