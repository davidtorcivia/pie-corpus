from pie.liv import headword_alternatives, headword


def test_headword_parsing():
    assert headword("1.*bʰeh₂-") == ("bʰeh₂-", 1, False)
    assert headword("?*bʰeh₁-") == ("bʰeh₁-", None, True)
    assert headword("*bʰeh₁ĝʰ-") == ("bʰeh₁ǵʰ-", None, False)


def test_uncertain_series_and_placeholders():
    assert headword("*g⁽ᵘ̯⁾eĝʰ-") == ("gʷeǵʰ-", None, True)       # g or gʷ: labialized form first
    assert headword("*ĝ⁽ʼ⁾el-") == ("ǵel-", None, True)
    # placeholders expand: R = a resonant, K = a tectal of unknown series; the root is uncertain
    assert headword("?*g⁽ᵘ̯⁾eRĝʰ-") == ("gʷerǵʰ-", None, True)
    assert headword_alternatives("*preK-") == ["preḱ-", "prek-", "prekʷ-"]
    assert headword("*k(u̯)lei̯k̑-")[0] == "kʷleyḱ-"               # (u̯) written on the line
