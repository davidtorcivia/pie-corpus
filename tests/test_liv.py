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


def test_plain_keeps_palatals():
    from pie.liv import _depal, _plain
    assert _plain("ḱel-") != _plain("kel-")
    assert _plain("bʰéydʰ-") == "bʰeydʰ-" and _plain("ŕ̥") == "r̥" and _plain("ṓ") == "ō"
    assert _depal("ḱel-") == _depal("kel-")


def test_apply_other_series_needs_the_gloss():
    from pie.liv import apply

    class Reg:
        def get(self, key, base):
            return base

    def root(i, form, meaning):
        return {"id": i, "kind": "root", "form": form, "variants": [], "meaning": [meaning]}

    def rec(form, en):
        return {"root": form, "root_alternatives": [], "headword_printed": "*" + form, "homograph": None,
                "uncertain": False, "meaning_de": en, "meaning_en": en, "iew": None, "stems": [],
                "neubildungen": [], "page": {"djvu": 10, "printed": 6}, "ocr_check": {}}
    entries = {r["id"]: r for r in [root("touch", "teh₂g-", "to touch"), root("hot", "ḱleh₁-", "hot, warm")]}
    rep = apply(entries, [rec("teh₂ǵ-", "to touch, grasp"), rec("kleh₁-", "to call")], Reg())
    assert entries["touch"]["liv"][0]["headword_printed"] == "*teh₂ǵ-"     # LIV ĝ⁽ʼ⁾ = Wiktionary g
    assert "liv" not in entries["hot"]                                    # *kleh₁- 'call' ≠ ḱleh₁- 'hot'
    assert (rep["matched_form"], rep["new"]) == (1, 1)
