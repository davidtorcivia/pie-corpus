from pie.liv import headword


def test_headword_parsing():
    assert headword("1.*bʰeh₂-") == ("bʰeh₂-", 1, False)
    assert headword("?*bʰeh₁-") == ("bʰeh₁-", None, True)
    assert headword("*bʰeh₁ĝʰ-") == ("bʰeh₁ǵʰ-", None, False)


def test_uncertain_series_and_placeholders():
    assert headword("*g⁽ᵘ̯⁾eĝʰ-") == ("gʷeǵʰ-", None, True)       # g or gʷ: labialized form first
    assert headword("*ĝ⁽ʼ⁾el-") == ("ǵel-", None, True)
    assert headword("?*g⁽ᵘ̯⁾eRĝʰ-")[0] is None                    # R = any resonant: not a form
