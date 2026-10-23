import json
from pathlib import Path

import pytest

from pie.classify import by_shape, zero_grade

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("stem,want", [
    ("gʷʰén", "gʷʰn̥"), ("dyéw", "dyu"), ("wóyd", "wid"), ("linékʷ", "linkʷ"),
    ("h₁és", "h₁s"), ("ḱwón", "ḱwn̥"), ("h₁éy", "h₁i"), ("bʰebʰówdʰ", "bʰebʰudʰ"), ("h₁nó", "h₁n̥"),
])
def test_zero_grade(stem, want):
    assert zero_grade(stem) == want


def test_zero_grade_needs_an_accented_short_vowel():
    assert zero_grade("h₁ḗd") is None and zero_grade("bʰer") is None


@pytest.mark.parametrize("entry,rule,strong,weak", [
    ({"form": "bʰéreti", "pos": "verb"}, "shape:thematic-present", "bʰére", None),
    ({"form": "h₁ésti", "pos": "verb"}, "shape:athematic-root", "h₁és", "h₁s"),
    ({"form": "wóyde", "pos": "verb", "aspect": "stat"}, "shape:perfect", "wóyd", "wid"),
    ({"form": "wĺ̥kʷos", "pos": "noun", "gender": "m"}, "shape:thematic", "wĺ̥kʷo", None),
    ({"form": "ǵénh₁os", "pos": "noun", "gender": "n"}, "shape:s-stem-neuter", "ǵénh₁os", "ǵénh₁es"),
    ({"form": "ph₂tḗr", "pos": "noun", "gender": "m"}, "shape:er-stem", "ph₂tér", "ph₂tr̥"),
    ({"form": "kólHō", "pos": "noun"}, "shape:n-stem-ak", "kólHon", "kl̥Hn̥"),
    ({"form": "h₁nómn̥", "pos": "noun", "gender": "n"}, "shape:men-neuter", "h₁nómn̥", "h₁n̥mén"),
])
def test_shape_rules(entry, rule, strong, weak):
    c = by_shape(entry)
    assert c.rule == rule
    assert c.spec.strong == strong and c.spec.weak == weak


def test_indeclinables():
    assert by_shape({"form": "nu", "pos": "adv"}).rule == "indeclinable"


def test_backtest_floor():
    """The rules Tier 3 leans on most must keep their measured accuracy."""
    p = ROOT / "data" / "morph" / "classify_report.json"
    if not p.exists():
        pytest.skip("classification not run")
    bt = json.loads(p.read_text("utf-8"))["backtest"]
    assert bt["shape:thematic-present"]["cell_accuracy"] >= 0.99
    assert bt["shape:perfect"]["cell_accuracy"] >= 0.95
    assert bt["shape:thematic-adj"]["cell_accuracy"] >= 0.95
