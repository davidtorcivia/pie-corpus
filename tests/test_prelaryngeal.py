import pytest

from pie.prelaryngeal import convert

# Brugmann-style forms (pre-laryngeal handbooks)
CASES = [
    ("dʰeh₁-", "dʰē"), ("steh₂-", "stā"), ("deh₃-", "dō"), ("ph₂tḗr", "pətḗr"), ("h₂eǵ-", "aǵ"),
    ("h₁ésti", "ésti"), ("h₃ekʷ-", "okʷ"), ("bʰuH-", "bʰū"), ("ǵr̥h₂nóm", "ǵr̥̄nóm"), ("méǵh₂", "méǵə"),
    ("dʰugh₂tḗr", "dʰugətḗr"), ("h₂ówis", "ówis"), ("gʷih₃wós", "gʷīwós"),
]


@pytest.mark.parametrize("form,expected", CASES)
def test_brugmann_forms(form, expected):
    assert convert(form)[0] == expected


def test_effects_mark_gold_positions():
    text, eff = convert("ph₂tḗr")
    assert [(e.kind, e.laryngeal, e.offset) for e in eff] == [("schwa", "h2", 1)]
    assert text[1] == "ə"
    _, eff = convert("steh₂-")
    assert {(e.kind, e.offset) for e in eff} == {("length", 2), ("color", 2)}
