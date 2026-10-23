import json
from pathlib import Path

import pytest

from pie.morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj
from pie.phon import join, parse, render

ROOT = Path(__file__).resolve().parent.parent


def j(stem, ending):
    return render(join(parse(stem), parse(ending)))


@pytest.mark.parametrize("stem,ending,want", [
    ("dyu", "és", "diwés"),          # stem-final u → w, cascade y → i
    ("ḱwn̥", "és", "ḱunés"),
    ("deh₂nu", "és", "deh₂n̥wés"),
    ("dʰugtr̥", "és", "dʰugtrés"),
    ("dʰugtr̥", "bʰós", "dʰugtr̥bʰós"),
    ("h₂ówi", "m", "h₂ówim"),         # ending resonant stays consonantal after a vowel
    ("ph₂tér", "ms", "ph₂térm̥s"),
    ("h₁és", "si", "h₁ési"),          # s + s → s
    ("gʷʰn̥", "énti", "gʷʰnénti"),
    ("h₁s", "wós", "h₁swós"),
    ("bʰér", "és", "bʰéres"),         # accented stem de-accents the ending
])
def test_join(stem, ending, want):
    assert j(stem, ending) == want


# Paradigm spot checks in the Wiktionary convention (exact module agreement).
@pytest.mark.parametrize("spec,feat,want", [
    (NounSpec("ph₂tér", "ph₂tr̥", "hysterokinetic"), "NOM.SG", ["ph₂tḗr"]),
    (NounSpec("ph₂tér", "ph₂tr̥", "hysterokinetic"), "GEN.SG", ["ph₂trés"]),
    (NounSpec("ph₂tér", "ph₂tr̥", "hysterokinetic"), "DAT.PL", ["ph₂tr̥mós", "ph₂tr̥bʰós"]),
    (NounSpec("dyéw", "dyu", "hysterokinetic", nom_sg="dyḗws"), "ACC.SG", ["dyḗm"]),   # Stang
    (NounSpec("dyéw", "dyu", "hysterokinetic", nom_sg="dyḗws"), "GEN.SG", ["diwés"]),
    (NounSpec("gʷów", "gʷéw", "acrostatic", nom_sg="gʷṓws"), "ACC.SG", ["gʷṓm"]),
    (NounSpec("gʷów", "gʷéw", "acrostatic", nom_sg="gʷṓws"), "GEN.SG", ["gʷéws"]),
    (NounSpec("pód", "ped", "acrostatic", nom_sg="pṓds", loc_sg=["péd"]), "GEN.SG", ["pedés"]),
    (NounSpec("h₂ówi", "h₂éwi", "acrostatic", "f"), "NOM.PL", ["h₂óweyes"]),
    (NounSpec("h₂ówi", "h₂éwi", "acrostatic", "f"), "DAT.SG", ["h₂éwyey"]),
    (NounSpec("ḱwón", "ḱwn̥", "hysterokinetic", loc_sg=["ḱwén", "ḱwéni"]), "NOM.SG", ["ḱwṓ"]),
    (NounSpec("ḱwón", "ḱwn̥", "hysterokinetic", loc_sg=["ḱwén", "ḱwéni"]), "GEN.SG", ["ḱunés"]),
    (NounSpec("bʰéh₂ǵʰu", "bʰeh₂ǵʰéw", "proterokinetic"), "DAT.PL", ["bʰeh₂ǵʰúmos", "bʰeh₂ǵʰúbʰos"]),
    (NounSpec("déḱos", "déḱes", "acrostatic", "n"), "NOM.PL", ["déḱōs"]),
    (NounSpec("h₁éḱwo"), "NOM.PL", ["h₁éḱwoes"]),
    (NounSpec("h₁éḱwo"), "GEN.SG", ["h₁éḱwosyo"]),
    (NounSpec("yugó", gender="n"), "NOM.PL", ["yugéh₂"]),
])
def test_decline_wiktionary(spec, feat, want):
    assert decline(spec, "wiktionary", alternatives=False)[feat] == want


def test_handbook_convention_contracts_thematic_and_keeps_alternatives():
    d = decline(NounSpec("h₁éḱwo"), "handbook")
    assert d["NOM.PL"][0] == "h₁éḱwōs" and "h₁éḱwoes" in d["NOM.PL"]
    assert d["DAT.SG"][0] == "h₁éḱwōy" and "h₁éḱwoey" in d["DAT.SG"]
    assert d["GEN.PL"][0] == "h₁éḱwōm" and "h₁éḱwoHom" in d["GEN.PL"]


@pytest.mark.parametrize("spec,feat,want", [
    (VerbSpec("bʰére"), "PRS.3SG", ["bʰéreti"]),
    (VerbSpec("bʰére"), "PRS.3PL", ["bʰéronti"]),
    (VerbSpec("bʰére"), "PRS.1SG", ["bʰéroh₂"]),
    (VerbSpec("h₁és", "h₁s"), "PRS.3SG", ["h₁ésti"]),
    (VerbSpec("h₁és", "h₁s"), "PRS.3PL", ["h₁sénti"]),
    (VerbSpec("h₁és", "h₁s"), "PRS.2SG", ["h₁ési"]),
    (VerbSpec("gʷʰén", "gʷʰn̥"), "PRS.3PL", ["gʷʰnénti"]),
    (VerbSpec("gʷʰén", "gʷʰn̥"), "PRS.1PL", ["gʷʰn̥mós"]),
    (VerbSpec("wóyd", "wid", "stat"), "PRF.3SG", ["wóyde"]),
    (VerbSpec("wóyd", "wid", "stat"), "PRF.3PL", ["widḗr"]),
    (VerbSpec("wóyd", "wid", "stat"), "PRF.1PL", ["widmé"]),
    (VerbSpec("h₁éy", "h₁i"), "PST.1SG", ["h₁ḗm"]),                  # Stang
    (VerbSpec("bʰúH", "bʰúH", "pf"), "AOR.3PL", ["bʰúHn̥t"]),         # accented stem: zero-grade 3pl
])
def test_conjugate_wiktionary(spec, feat, want):
    assert conjugate(spec, "wiktionary", alternatives=False)[feat] == want


def test_thematic_adjective_genders():
    a = decline_adj(AdjSpec("néwo"), "wiktionary", alternatives=False)
    assert a["m"]["NOM.SG"] == ["néwos"] and a["f"]["NOM.SG"] == ["néweh₂"] and a["n"]["NOM.SG"] == ["néwom"]


def test_crosscheck_agreement_and_no_unexplained():
    """Phase 2 acceptance: regenerate every Wiktionary table; every mismatch
    must have a documented cause (docs/morphology.md)."""
    paras = ROOT / "data" / "lexicon" / "paradigms.jsonl"
    if not paras.exists():
        pytest.skip("lexicon not built")
    from pie.crosscheck import run
    from pie.triage import summarize
    r = run(paras)
    t = r["total"]
    assert t["cells_ok"] / (t["cells_ok"] + t["cells_bad"]) >= 0.985
    by = summarize(r["mismatches"])
    assert not by.get("unexplained"), [(m["form"], m["feature"]) for m in by["unexplained"][:10]]


GOLDEN = json.loads((ROOT / "tests" / "data" / "golden_paradigms.json").read_text("utf-8"))


@pytest.mark.parametrize("para", GOLDEN["paradigms"], ids=lambda p: p["lemma"])
def test_golden_paradigms_handbook_unverified(para):
    """PLAN's golden paradigms. Source is handbook-standard but UNVERIFIED
    until the books arrive; see the file header."""
    s = dict(para["spec"])
    kind = s.pop("type")
    if kind == "noun":
        cells = decline(NounSpec(**s), "handbook")
    else:
        cells = conjugate(VerbSpec(**s), "handbook")
    for feat, acceptable in para["cells"].items():
        assert set(acceptable) & set(cells.get(feat, [])), (para["lemma"], feat, acceptable, cells.get(feat))


def _walk_forms(node):
    if isinstance(node, list):
        yield from node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("_"):
                continue
            if isinstance(v, str):     # particle table: the key is the form
                yield k
            else:
                yield from _walk_forms(v)


def test_closed_class_forms_canonical():
    from pie.translit import is_canonical
    data = json.loads((ROOT / "data" / "morph" / "closed_class.json").read_text("utf-8"))
    forms = list(_walk_forms(data))
    assert len(forms) > 100
    bad = [f for f in forms if not is_canonical(f)]
    assert not bad, bad
