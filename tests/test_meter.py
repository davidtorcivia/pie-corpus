import pytest

from pie.meter import measure, word_syllables


# dʰugh₂tḗr has a vocalized interconsonantal laryngeal: dʰu-gə-tḗr (Gk θυ-γά-τηρ).
@pytest.mark.parametrize("word,n", [
    ("h₂ówis", 2), ("ph₂tḗr", 2), ("dʰugh₂tḗr", 3), ("wĺ̥kʷos", 2), ("ḱléwos", 2),
    ("ń̥dʰgʷʰitom", 3), ("gʷʰnénti", 2), ("h₁éḱwōs-kʷe", 3), ("septḿ̥", 2), ("h₂stḗr", 1),
    ("dyḗws", 1), ("só", 1), ("kʷetwóres", 3),
])
def test_word_syllables(word, n):
    assert word_syllables(word) == n


def test_laryngeal_option():
    assert word_syllables("ph₂tḗr", laryngeals="none") == 1


def test_sievers_option():
    # *-yo- after a heavy syllable: Sievers adds a syllable
    assert word_syllables("wĺ̥kʷosyo") == 3
    assert word_syllables("h₂ŕ̥tḱyos", sievers=True) == word_syllables("h₂ŕ̥tḱyos") + 1


def test_meter_label_only_on_match():
    m = measure("ḱléwos ń̥dʰgʷʰitom")   # 2 + 3 = 5 syllables
    assert m["syllables"] == 5 and m["meter"] is None
    assert measure("h₂ówis h₂ówis h₂ówis h₂ówis")["meter"] == "octosyllable"   # 4 × 2
