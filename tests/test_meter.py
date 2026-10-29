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


# Audit 2026-10-28 (docs/audits/meter-census.md): the counts a Vedic or Greek reflex fixes.
@pytest.mark.parametrize("word,n,why", [
    ("méǵh₂", 2, "CH#: Ved. máhi, Gk μέγα (was 1: word-final laryngeals were never counted)"),
    ("h₃ésth₁", 2, "CH#: Ved. ásthi"),
    ("wékʷesh₂", 3, "CH#: Gk ἔπεα"),
    ("h₃ésth₁-kʷe", 3, "the clitic makes -th₁kʷ- interconsonantal"),
    ("h₃ésth₁h₂", 2, "-CHH#: only the first laryngeal vocalizes"),
    ("méǵh₂h₂", 2, "-CHH#"),
    ("h₂Hséh₂i", 2, "#HHC: a word-initial laryngeal cluster stays consonantal, like #HC"),
    ("h₂wĺ̥h₁neh₂h₁", 2, "-VHH# adds nothing"),
    ("bʰéroyh₁t", 2, "V y H C: Ved. bháret, Gk φέροι (was 3)"),
    ("gʷíh₃woyh₁t", 2, "Ved. jī́vet (was 3)"),
    ("dwóyh₁", 1, "Ved. dvé (was 2 under CH#)"),
    ("dayh₂wḗr", 2, "Ved. devár- (was 3)"),
    ("kréwh₂s", 2, "after -w the laryngeal vocalizes: Ved. kravíṣ"),
    ("mléwHt", 2, "Ved. ábravīt"),
    ("ǵénh₁tor", 3, "RHC: Ved. janitár-"),
    ("h₂érh₃trom", 3, "Gk ἄροτρον"),
    ("h₂énh₁mos", 3, "Gk ἄνεμος"),
    ("bʰoydʰéh₂m", 2, "-eh₂m: the m is not syllabic"),
    ("pĺ̥h₂seh₂m", 2, "a laryngeal after a syllabic resonant is not a nucleus"),
    ("ph₂wénh₁", 3, "CH# after a consonantal resonant"),
])
def test_audited_counts(word, n, why):
    assert word_syllables(word) == n, why


def test_weights_and_cadence():
    from pie.meter import cadence, weights
    # dʰéǵʰom wiHrós mért tóm stérge: closed syllables are heavy across word boundaries
    line = "dʰéǵʰom wiHrós mért tóm stérge"
    assert len(weights(line)) == 8
    assert weights("só h₂ówis") == "LLL"            # só.h₂ó.wis: one consonant (h₂) after só, one after ó
    assert weights("ph₂tḗr") == "LH"                # pə (light) + tḗr (long)
    assert cadence("só só só só só só só só", 8) is False    # all light: no iambic close
    assert cadence("só tḗ só tḗ só tḗ só só", 8) is True     # … ⏑ – ⏑ ×
    assert cadence("só só", 8) is None                       # shorter than the cadence


def test_record_meter_fields():
    from pie.meter import record_meter, summary
    assert record_meter("h₂ówis.", "law") is None
    m = record_meter("h₂ówis h₂ówis h₂ówis h₂ówis. h₂ówis h₂ówis h₂ówis h₂ówis h₂ówis.", "hymn")
    assert m["line_syllables"] == [8, 10] and m["fit"] == 2 and m["exact"] == 1 and m["targets"] == [8, 11]
    assert len(m["cadence"]) == 2 and m["cadence"][1] is None
    assert record_meter("h₂ówis h₂ówis h₂ówis h₂ówis h₂ówis h₂ówis.", "hymn", declared=12)["exact"] == 1
    assert record_meter("h₂ówis h₂ówis h₂ówis h₂ówis h₂ówis h₂ówis.", "hymn")["exact"] == 0
    assert record_meter("h₂ówis.", "work song") is not None          # work songs are metered
    s = summary([m])
    assert (s["lines"], s["near"], s["exact"], s["exact_share"]) == (2, 2, 1, 0.5)
    # an old stored field (no exact/cadence) still summarizes
    old = {"line_syllables": [8, 9, 11], "fit": 3, "targets": [8, 11]}
    assert summary([old])["exact"] == 2 and summary([old])["cadence"] == {}
