from pie.soundlaw import check_entry


def _entry(form, lang, roman, **flags):
    return {"id": "x", "form": form, "reflexes": {lang: [{"form": roman, "roman": roman, **flags}]}}


def results(e):
    return [(code, law, ok) for code, law, ok, *_ in check_entry(e)]


def test_satem_and_centum():
    assert results(_entry("ḱm̥tóm", "Sanskrit", "śatám")) == [("skt", "satem", True)]
    assert results(_entry("ḱm̥tóm", "Latin", "centum")) == [("lat", "centum", True)]
    assert results(_entry("ḱm̥tóm", "Sanskrit", "katám")) == [("skt", "satem", False)]


def test_grimm_and_aspirates():
    assert results(_entry("ph₂tḗr", "Proto-Germanic", "*fadēr")) == [("gem", "grimm", True)]
    assert results(_entry("bʰéreti", "Latin", "fert")) == [("lat", "aspirate", True)]


def test_grassmann():
    assert results(_entry("bʰendʰ-", "Sanskrit", "bandh")) == [("skt", "grassmann", True)]


def test_greek_prothesis_and_s_mobile():
    assert results(_entry("h₂nḗr", "Ancient Greek", "anḗr")) == [("grc", "prothesis", True)]
    assert results(_entry("snusós", "Ancient Greek", "nuós")) == [("grc", "s-mobile", True)]


def test_skips_loans_and_prefixed_forms():
    assert results(_entry("ḱm̥tóm", "Sanskrit", "katám", borrowed=True)) == []
    assert results(_entry("dʰéh₁t", "Ancient Greek", "éthēka")) == []      # augment
