"""Invented fixtures only: full layers, postings, proximity and CLI behaviour."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from pie.corpus_index import CorpusIndex, build_index


def word(form, lemma, *roots):
    return dict(form=form, lemma=lemma, root_ids=list(roots),
                root_groups=["group-" + r for r in roots])


def record(n, words=(), corpus="a", book="one", mask=1):
    return dict(corpus=corpus, branch="Greek" if corpus == "a" else "Celtic",
                book=book, ordinal=n, locus=f"{book}:{n}", text="invented fixture",
                words=list(words), class_mask=mask, main_class_mask=mask,
                layer_status="included" if mask else "excluded", licence_tag="pd")


@pytest.fixture
def index(tmp_path):
    path = tmp_path / "index.sqlite"
    records = [record(0), record(1, [word("α", "alpha", "x"), word("gap", "gap"), word("β", "beta", "y")], mask=0),
               record(2, [word("ambiguous", "amb", "x", "y")]),
               record(3, [word("α", "alpha", "x"), word("β", "beta", "y")], book="two"),
               record(0, [word("α", "alpha", "x"), word("β", "beta", "y")], corpus="b")]
    assert build_index(path, iter(records)) == 5
    idx = CorpusIndex(path)
    yield idx, path
    idx.close()


def test_all_units_and_metadata(index):
    idx, _ = index
    rows = list(idx.search(limit=None))
    assert len(rows) == 5 and rows[0]["words"] == []
    assert rows[1]["class_mask"] == 0
    assert rows[1]["words"][0]["root_groups"] == ["group-x"]


def test_root_and_group_and_near(index):
    idx, _ = index
    assert len(list(idx.search(roots=["x", "group-y"]))) == 4
    assert len(list(idx.search(roots=["x", "y"], near=1))) == 2
    assert len(list(idx.search(roots=["x", "y"], near=2))) == 3
    assert not list(idx.search(roots=["x", "y"], near=0))
    assert not list(idx.search(roots=["missing"]))
    assert not list(idx.search(roots=["x", "x"], near=2))


def test_filters_regex_limits_and_context(index):
    idx, _ = index
    rows = list(idx.search(lemmas=["alpha", "beta"], form="^α$", branches=["Greek"],
                           corpora=["a", "b"], not_corpora=["b"], limit=1, context=2))
    assert len(rows) == 1 and rows[0]["locus"] == "one:1"
    assert [r["locus"] for r in rows[0]["context"]] == ["one:0", "one:2"]
    assert not list(idx.search(lemmas=["Alpha"]))
    assert not list(idx.search(form="never"))
    assert not list(idx.search(limit=0))
    with pytest.raises(ValueError):
        list(idx.search(near=2))
    with pytest.raises(ValueError):
        list(idx.search(context=-1))


def test_atomic_failure_preserves_index(index):
    idx, path = index
    with pytest.raises(KeyError):
        build_index(path, [{}])
    assert len(list(idx.search())) == 5
    assert len(list(path.parent.iterdir())) == 1


def test_cli(index):
    _, path = index
    script = Path(__file__).resolve().parents[1] / "scripts/search_corpora.py"
    def run(*args):
        return subprocess.run([sys.executable, "-I", str(script), "--index", str(path), *args],
                              capture_output=True, text=True)
    result = run("--root", "x", "--root", "y", "--near", "2", "--count", "--limit", "1")
    assert result.returncode == 0 and result.stdout == "3\n"
    result = run("--lemma", "alpha", "--json", "--limit", "1")
    assert json.loads(result.stdout)["locus"] == "one:1"
    assert "one:1" in run("--lemma", "alpha", "--text").stdout
    assert run("--form", "[").returncode == 2
    assert run("--near", "-1").returncode == 2
    assert run("--help").returncode == 0


def test_context_skips_interleaved_books(tmp_path):
    path = tmp_path / "context.sqlite"
    build_index(path, [record(0), record(1, book="other"), record(2, [word("f", "target")])])
    idx = CorpusIndex(path)
    try:
        hit = next(idx.search(lemmas=["target"], context=1))
        assert [r["locus"] for r in hit["context"]] == ["one:0"]
    finally:
        idx.close()
