from pie.glosses import build


def _lex():
    return [
        {"id": "r", "kind": "root", "form": "bʰer-", "meaning": ["to bear, carry"], "root_id": "r"},
        {"id": "a-tos", "kind": "affix", "form": "-tós", "meaning": ["Creates verbal adjectives."]},
        {"id": "a-s", "kind": "affix", "form": "-s", "meaning": ["Derives root nouns."]},
        {"id": "a-nos", "kind": "affix", "form": "-nós", "meaning": ["Creates verbal adjectives from roots."]},
        {"id": "d1", "kind": "derivative", "form": "bʰr̥tós", "segmented": "bʰr̥-tós", "meaning": [], "root_id": "r"},
        {"id": "d2", "kind": "derivative", "form": "bʰernos", "segmented": "bʰer-no-s", "meaning": [], "root_id": "r"},
        {"id": "d3", "kind": "derivative", "form": "bʰēr-s", "segmented": "bʰēr-s", "meaning": [], "root_id": "r"},
        {"id": "d4", "kind": "derivative", "form": "bʰerenos", "segmented": "bʰer-eno-s", "meaning": [], "root_id": "r"},
    ]


def test_derived_gloss_composes_root_and_suffix():
    d = build(_lex())
    assert d["d1"]["gloss"] == "to bear, carry [-tós: verbal adjective, 'X-ed']"


def test_affix_match_ignores_accent():
    assert "-nós" in build(_lex())["d2"]["gloss"]          # bʰer-no-s matches -nós


def test_final_s_is_a_suffix_only_on_root_plus_s():
    d = build(_lex())
    assert "root noun" in d["d3"]["gloss"]
    assert "d4" not in d                                  # -s there is the nominative ending
