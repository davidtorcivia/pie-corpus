"""Engine fixes from the Tier 2 round-2 review (docs/audits/tier2-review-r2.md, P6)."""

import pytest

from pie.morph import AdjSpec, NounSpec, decline, decline_adj


def hb(spec, **kw):
    return decline(spec, "handbook", **kw)


@pytest.mark.parametrize("spec,feat,want", [
    # u/i-stems: zero-grade suffix, accented, before consonant-initial oblique plural endings
    # (Ringe 2006 §2.3.4–5: ǵustúbʰi, tn̥h₂úsu; Ved. sūnúbhis, agníbhis, urúbhis)
    (NounSpec("suHnú", "suHnów"), "INS.PL", "suHnúbʰis"),
    (NounSpec("suHnú", "suHnów"), "LOC.PL", "suHnúsu"),
    (NounSpec("suHnú", "suHnów"), "DAT.PL", "suHnúbʰos"),
    (NounSpec("h₁n̥gʷní", "h₁n̥gʷnéy"), "INS.PL", "h₁n̥gʷníbʰis"),
    # a diphthongal root noun is not an u-stem (Ved. góbhis): weak stem unchanged
    (NounSpec("gʷów", "gʷéw", "acrostatic", nom_sg="gʷṓws"), "INS.PL", "gʷéwbʰis"),
    # the acrostatic type keeps its root accent (Ringe: h₂éwibʰi)
    (NounSpec("h₂ówi", "h₂éwi", "acrostatic"), "INS.PL", "h₂éwibʰis"),
    # mon-stem whose Wiktionary weak stem lost the m: *-mn- kept after a short vowel
    (NounSpec("sh₂imón", "sh₂in̥", "hysterokinetic", loc_sg=["sh₂imén"]), "INS.SG", "sh₂imnéh₁"),
    (NounSpec("sh₂imón", "sh₂in̥", "hysterokinetic", loc_sg=["sh₂imén"]), "GEN.SG", "sh₂imnés"),
    (NounSpec("sh₂imón", "sh₂in̥", "hysterokinetic", loc_sg=["sh₂imén"]), "DAT.SG", "sh₂imnéy"),
    (NounSpec("sh₂imón", "sh₂in̥", "hysterokinetic", loc_sg=["sh₂imén"]), "INS.PL", "sh₂imn̥bʰís"),
    # after a heavy syllable the Asno law deletes the m (Byrd: *h₂éḱmn-es → Ved. áśnas): left as given
    (NounSpec("h₂éḱmon", "h₂ḱn̥", "amphikinetic", loc_sg=["h₂ḱmén"]), "GEN.SG", "h₂ḱnés"),
    # devī vocative in short *-i (Ringe §2.3.5 tn̥h₂éwi) with initial accent (Ved. pŕ̥thivi, dévi)
    (NounSpec("pl̥th₂éwih₂", "pl̥th₂uyéh₂", "proterokinetic", "f", devi=True), "VOC.SG", "pĺ̥th₂ewi"),
    (NounSpec("déywih₂", "diwyéh₂", "proterokinetic", "f"), "VOC.SG", "déywi"),
])
def test_handbook_primary(spec, feat, want):
    assert hb(spec)[feat][0] == want


def test_proterokinetic_u_adjective_obliques():
    m = decline_adj(AdjSpec("HéHḱu", "HHḱéw", "HHḱéwih₂", "HHḱuyéh₂", "proterokinetic"), "handbook")["m"]
    assert m["INS.PL"][0] == "HHḱúbʰis"
    assert m["DAT.PL"][0] == "HHḱúbʰos"
    assert m["LOC.PL"][0] == "HHḱúsu"
    assert "HHḱéwbʰis" in m["INS.PL"]          # the old form survives as an alternative


def test_wiktionary_forms_kept_as_alternatives():
    c = hb(NounSpec("sh₂imón", "sh₂in̥", "hysterokinetic", loc_sg=["sh₂imén"]))
    assert "sh₂inéh₁" in c["INS.SG"] and "sh₂inés" in c["GEN.SG"]
    v = hb(NounSpec("pl̥th₂éwih₂", "pl̥th₂uyéh₂", "proterokinetic", "f", devi=True))["VOC.SG"]
    assert "pl̥th₂éwi" in v and "pl̥th₂éwih₂" in v
    # the Wiktionary convention itself is unchanged
    w = decline(NounSpec("sh₂imón", "sh₂in̥", "hysterokinetic", loc_sg=["sh₂imén"]), "wiktionary", alternatives=False)
    assert w["INS.SG"] == ["sh₂inéh₁"]
