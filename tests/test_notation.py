import unicodedata

import pytest

from pie.notation import PROFILES, RULES, normalize

from .test_translit import TRICKY

NFC = lambda s: unicodedata.normalize("NFC", s)  # noqa: E731

# (input, profile, expected, rule that must fire)
CASES = [
    ("  h₂ówis   h₁éḱwōs-kʷe ", "default", "h₂ówis h₁éḱwōs-kʷe", "G-WS"),
    ("“ḱḗr”", "default", '"ḱḗr"', "G-QUOTES"),
    ("ne…", "default", "ne...", "G-ELLIPSIS"),
    ("h2ówis", "default", "h₂ówis", "G-LAR-DIGIT"),
    ("h²ówis", "default", "h₂ówis", "G-LAR-DIGIT"),
    ("hₓéw-", "default", "Héw-", "G-LAR-X"),
    ("H₂ówis", "default", "h₂ówis", "G-CASE"),
    ("Gʷṓws", "default", "gʷṓws", "G-CASE"),
    ("k̂léwos", "default", "ḱléwos", "G-PAL-CIRC"),
    ("ĝʰew-", "default", "ǵʰew-", "G-PAL-CIRC"),
    ("k̑m̥tóm", "default", "ḱm̥tóm", "G-PAL-CIRC"),
    ("kᵘ̯e", "default", "kʷe", "G-LAB-U"),
    ("dei̯u̯os", "default", "deywos", "G-GLIDE"),
    ("wr̊", "default", "wr̥", "G-RING-ABOVE"),
    ("ŕ̊tḱos", "default", "ŕ̥tḱos", "G-RING-ABOVE"),
    ("wṛ", "default", "wr̥", "G-SYL-DOT"),
    ("ṃ́ǵeh₂", "default", "ḿ̥ǵeh₂", "G-SYL-DOT"),
    ("é̄", "default", "ḗ", "G-MARK-ORDER"),
    ("pé̄ds", "default", "pḗds", "G-MARK-ORDER"),
    ("mṛh₂-ό-", "default", "mr̥h₂-ó-", "G-HOMOGLYPH"),
    ("ǵʰеydʰis", "default", "ǵʰeydʰis", "G-HOMOGLYPH"),
    ("gʰh̥₁bʰ-yé-ti", "default", "gʰh₁bʰ-yé-ti", "G-LAR-RING"),
    ("bhéreti", "plain-h-aspirates", "bʰéreti", "P-ASP-PLAIN-H"),
    ("dhugh₂tḗr", "plain-h-aspirates", "dʰugh₂tḗr", "P-ASP-PLAIN-H"),
    ("gʷhén-", "plain-h-aspirates", "gʷʰén-", "P-ASP-PLAIN-H"),
    ("ǵhew-", "plain-h-aspirates", "ǵʰew-", "P-ASP-PLAIN-H"),
    ("Avis akvāsas ka", "schleicher-1868", "awis akwāsas ka", "P-V-W"),
    ("jugom", "schleicher-1868", "yugom", "P-J-Y"),
]


@pytest.mark.parametrize("src,profile,want,rule", CASES)
def test_rule(src, profile, want, rule):
    r = normalize(src, profile)
    assert r.text == want
    assert rule in r.applied
    assert r.canonical


def test_every_rule_in_a_profile_has_a_case():
    used = {rid for p in PROFILES.values() for rid in p} - {"G-NFC"}
    covered = {c[3] for c in CASES}
    assert used <= covered, used - covered


def test_profiles_reference_known_rules():
    for rules in PROFILES.values():
        assert all(r in RULES for r in rules)


def test_generic_H_survives_case_folding():
    assert normalize("dʰéH- H₁éḱwos").text == "dʰéH- h₁éḱwos"


def test_plain_h_rule_leaves_laryngeals():
    # The danger case for plain-h profiles: g + h₂ must not become gʰ.
    assert normalize("dhugh₂tḗr bhh₁-", "plain-h-aspirates").text == "dʰugh₂tḗr bʰh₁-"


@pytest.mark.parametrize("uni,_asc", TRICKY)
def test_canonical_input_is_untouched(uni, _asc):
    if uni != uni.strip() or "  " in uni:
        pytest.skip("whitespace case")
    r = normalize(NFC(uni))
    assert r.text == NFC(uni)
    assert r.applied == []


@pytest.mark.parametrize("src,profile,want,rule", CASES)
def test_idempotent(src, profile, want, rule):
    once = normalize(src, profile).text
    assert normalize(once, profile).text == once
