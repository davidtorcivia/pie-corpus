"""Engine audit sweep (docs/audits/engine-sweep/*.md, integrated in INTEGRATION.md): one test per applied fix,
against the composed engine. The report and item are named in each test."""

import pytest

from pie.morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj


def hb(spec):
    return decline(spec, "handbook")


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


# --- thematic.md -----------------------------------------------------------------------------------------

def test_thematic_neuter_dual_is_oyh1():
    """thematic.md defect 9: *-o-ih₁ (Fortson §6.50, L&Y §2.1.1); Wiktionary's -oy first in its own convention."""
    assert hb(NounSpec("yugó", gender="n"))["NOM.DU"][:2] == ["yugóyh₁", "yugóy"]
    assert decline(NounSpec("yugó", gender="n"), "wiktionary", alternatives=False)["NOM.DU"][0] == "yugóy"


def test_thematic_table_paradigm_has_one_stem(lx):
    """thematic.md defect 5 (the two lexemes an override fixes on its own; silver waits for PENDING-realize.md)."""
    c = lx.cells("pie-lex-lowh3trom")
    assert c["NOM.SG"][0] == "lówh₃trom" and c["GEN.SG"][0] == "lówh₃trosyo"
    assert lx.cells("pie-lex-sh2eytlom")["GEN.SG"][0] == "sh₂éytlosyo"


def test_thematic_spec_overrides(lx):
    """thematic.md defects 3, 4, 7, 10."""
    assert lx.cells("pie-lex-Hroth2os")["NOM.SG"][0] == "Hróth₂os"          # Ved. rátha-
    assert lx.cells("pie-lex-dhubhros")["ACC.SG"][0] == "dʰubʰróm"          # aspirate restored
    c = lx.cells("pie-lex-kjeh2dos")                                         # Gk κῆδος, -εος n.
    assert c["ACC.SG"][0] == "ḱéh₂dos" and c["GEN.SG"][0].startswith("ḱéh₂des")
    assert lx.cells("pie-lex-h1rudhyos", "f")["NOM.SG"][0] == "h₁rudʰyeh₂"   # 'red' agrees with a feminine


def test_thematic_neuter_shape_rule_is_usable(lx):
    """thematic.md "Gating": the backtest skips tables that disagree with their own headword."""
    import json
    from pathlib import Path
    r = json.loads((Path(__file__).resolve().parent.parent / "data/morph/classify_report.json").read_text("utf-8"))
    assert r["backtest"]["shape:thematic-neuter"]["cell_accuracy"] == 1.0


# --- feminine.md -----------------------------------------------------------------------------------------

def test_athematic_eh2_stang():
    """feminine.md D6: Ringe 2006 §2.3.4 dn̥ǵʰwéh₂m (-ām), dn̥ǵʰwéh₂ns (-ās); C+H and *-oh₁ keep -m̥."""
    t = NounSpec("dn̥ǵʰwéh₂", "dn̥ǵʰuh₂", "hysterokinetic", "f", nom_sg="dn̥ǵʰwéh₂s")
    assert hb(t)["ACC.SG"] == ["dn̥ǵʰwéh₂m", "dn̥ǵʰwéh₂m̥", "dn̥ǵʰwā́m"]
    assert hb(t)["ACC.PL"][:3] == ["dn̥ǵʰwā́s", "dn̥ǵʰwéh₂ns", "dn̥ǵʰwéh₂n̥s"]
    assert hb(NounSpec("gʷénh₂", "gʷnéh₂", "proterokinetic", "f"))["ACC.SG"] == ["gʷénh₂m̥"]
    assert hb(NounSpec("póntoh₁", "pn̥th₁", "hysterokinetic"))["ACC.SG"] == ["póntoh₁m̥"]
    assert hb(NounSpec("wl̥kʷíh₂", "wl̥kʷih₂", "hysterokinetic", "f", nom_sg="wl̥kʷíh₂s"))["ACC.SG"] == ["wl̥kʷíh₂m̥"]


def test_gwen_vocative_is_the_nominative(lx):
    """feminine.md D4: Ringe 2006 §2.3.4 voc. = nom. gʷḗn; bare *gʷénh₂ (Fortson, Beekes) as the alternative."""
    c = lx.cells("pie-lex-gwexn")
    assert c["NOM.SG"] == ["gʷḗn", "gʷénh₂"] and c["VOC.SG"][0] == "gʷḗn"


def test_eh2_instrumental_and_dual_alternatives():
    """feminine.md D9: Ringe *-eh₂(e)h₁, Beekes *-eh₂ih₁ as alternatives; primaries unchanged."""
    c = hb(NounSpec("h₂ékʷeh₂", gender="f"))
    assert c["INS.SG"] == ["h₂ékʷeh₂h₁", "h₂ékʷeh₂eh₁"] and c["NOM.DU"][-1] == "h₂ékʷeh₂ih₁"


def test_feminine_spec_overrides(lx):
    """feminine.md D3, D7, D8, D11."""
    assert lx.cells("pie-lex-h3mighleh2")["LOC.SG"][0] == "h₃mígʰleh₂i"
    assert lx.cells("pie-lex-gjhorneh2")["ACC.SG"][0] == "ǵʰórneh₂m"
    assert lx.cells("pie-lex-h2yuHnteh2")["LOC.SG"][0] == "h₂yuHn̥téh₂i"
    assert lx.cells("pie-lex-sexm", "f")["GEN.SG"][0] == "sm̥yéh₂s"


# --- i-u-stems.md ----------------------------------------------------------------------------------------

def test_iu_instrumental_on_zero_grade_suffix():
    """i-u-stems.md #5: Ringe 2006 pp. 47, 49; Fortson §6.10; Beekes §13.2.6a."""
    assert hb(NounSpec("ménti", "mn̥téy", "proterokinetic", "f"))["INS.SG"][:2] == ["mn̥tíh₁", "mn̥téyh₁"]
    assert hb(NounSpec("ǵéwstu", "ǵustéw", "proterokinetic", "m"))["INS.SG"][0] == "ǵustúh₁"
    assert hb(NounSpec("dóru", "dréw", "proterokinetic", "n"))["INS.SG"][0] == "drúh₁"
    assert hb(NounSpec("h₁n̥gʷní", "h₁n̥gʷnéy"))["INS.SG"][0] == "h₁n̥gʷníh₁"
    assert hb(NounSpec("h₂ówi", "h₂éwi", "acrostatic", "f"))["INS.SG"] == ["h₂éwih₁"]


def test_u_stem_locative_lengthened_grade_is_an_alternative():
    """i-u-stems.md #2 (convention: Ringe's -éw(i) primary, Beekes's -ḗw an alternative); i-stem order unchanged."""
    assert hb(NounSpec("ǵéwstu", "ǵustéw", "proterokinetic", "m"))["LOC.SG"] == ["ǵustéwi", "ǵustéw", "ǵustḗw"]
    assert hb(NounSpec("ménti", "mn̥téy", "proterokinetic", "f"))["LOC.SG"][0] == "mn̥téy"
    assert "suHnṓw" not in hb(NounSpec("suHnú", "suHnów"))["LOC.SG"]


def test_iu_neuter_dual():
    """i-u-stems.md #15: Fortson §6.13 (*h₃ekʷih₁, Ved. urvī́); Ringe p. 47 dórwih₁."""
    assert hb(NounSpec("dóru", "dréw", "proterokinetic", "n"))["NOM.DU"][0] == "dórwih₁"
    assert hb(NounSpec("móri", "mréy", "proterokinetic", "n"))["NOM.DU"][0] == "mórih₁"
    adj = decline_adj(AdjSpec("ml̥dú", "ml̥déw", "ml̥déwih₂", "ml̥duyéh₂", "proterokinetic"))
    assert adj["n"]["NOM.DU"][0] == "ml̥dwíh₁"


def test_iu_spec_overrides(lx):
    """i-u-stems.md #4, #6, #8–#13."""
    assert lx.cells("pie-lex-deh2nu")["GEN.SG"][0] == "déh₂news"
    assert lx.cells("pie-lex-neh2us")["GEN.SG"][0] == "neh₂wés"
    assert lx.cells("pie-lex-HeHkjus", "f")["NOM.SG"][0] == "HeHḱéwih₂"
    assert lx.cells("pie-lex-pekju")["INS.SG"][0] == "pḱúh₁"
    assert lx.cells("pie-lex-bheh2gjhus")["ACC.SG"][0] == "bʰeh₂ǵʰúm"
    assert lx.cells("pie-lex-Hrughis")["ACC.SG"][0] == "Hrugʰím"
    assert lx.cells("pie-lex-perkus")["NOM.PL"][0] == "pérkʷewes"
    assert lx.cells("pie-lex-sweh2dus")["GEN.SG"][0] == "sweh₂déws"


# --- r-n-stems.md ----------------------------------------------------------------------------------------

def test_resonant_between_consonants_before_vocalic_ending():
    """r-n-stems.md defect 1: h₂ḱmn+és → h₂ḱm̥nés (Ringe 2006 §2.3.4 h₁n̥h₃m̥nés); others unchanged."""
    s = NounSpec("h₂éḱmon", "h₂ḱmn", "amphikinetic", loc_sg=["h₂ḱmén"])
    assert hb(s)["GEN.SG"][0] == "h₂ḱm̥nés" and hb(s)["INS.PL"][0] == "h₂ḱmn̥bʰís"
    assert hb(NounSpec("tétḱon", "tetḱn", "amphikinetic", loc_sg=["tetḱén"]))["GEN.SG"][0] == "tetḱnés"


def test_men_neuter_oblique_plural_zero_grade():
    """r-n-stems.md defect 2: L&Y §2.4.1 *-mn̥- before consonant-initial endings."""
    c = hb(NounSpec("ḱléwmn̥", "ḱlumén", "proterokinetic", "n"))
    assert c["INS.PL"][0] == "ḱlumń̥bʰis" and c["LOC.PL"][0] == "ḱlumń̥su" and c["DAT.PL"][0] == "ḱlumń̥bʰos"
    assert "ḱluménbʰis" in c["INS.PL"] and c["GEN.PL"][0] == "ḱluménōm"
    assert hb(NounSpec("h₁nómn̥", "h₁némn̥", "acrostatic", "n"))["INS.PL"][0] == "h₁némn̥bʰis"


def test_er_and_tor_shape_rules():
    """r-n-stems.md defects 7-8."""
    from pie.classify import by_shape
    assert by_shape({"form": "ḱḗr", "pos": "noun", "gender": "n"}).rule != "shape:er-stem"
    c = by_shape({"form": "ǵenh₁tḗr", "pos": "noun", "gender": "m"})
    assert (c.rule, c.spec.weak) == ("shape:er-stem", "ǵenh₁tr̥")
    assert by_shape({"form": "spéḱtḗr", "pos": "noun"}).spec is None
    c = by_shape({"form": "dʰéh₁tōr", "pos": "noun", "gender": "m"})
    assert hb(c.spec)["LOC.SG"][0] == "dʰh₁téri"


def test_rn_spec_overrides(lx):
    """r-n-stems.md defects 3-6."""
    assert lx.cells("pie-lex-meh2texr")["LOC.SG"][0] == "méh₂teri"
    assert lx.cells("pie-lex-dayh2wexr")["DAT.PL"][0] == "dayh₂wr̥bʰós"
    assert lx.cells("pie-lex-gjhesoxr")["GEN.SG"][0] == "ǵʰesrés"
    assert lx.cells("pie-lex-keh2nmn")["GEN.SG"][0] == "kh₂n̥méns"


# --- s-root-heteroclite.md -------------------------------------------------------------------------------

def test_heteroclite_collective():
    """F1: Fortson §6.15 *ud-ōr, Ringe 2006 *wédōr; the pre-form -r̥h₂ stays an alternative."""
    c = hb(NounSpec("wódr̥", "wédn̥", "acrostatic", "n"))
    assert c["NOM.PL"][0] == c["ACC.PL"][0] == "wédōr" and "wódr̥h₂" in c["NOM.PL"]
    assert hb(NounSpec("sóh₂wl̥", "sh₂wén", "proterokinetic", "n"))["NOM.PL"][0] == "séh₂wōl"
    assert hb(NounSpec("ḱérd", "ḱr̥d", "amphikinetic", "n"))["NOM.PL"][0] == "ḱérdh₂"
    assert decline(NounSpec("wódr̥", "wédn̥", "acrostatic", "n"), "wiktionary", alternatives=False)["NOM.PL"] == ["wódr̥h₂"]


def test_no_accentless_locative_and_laryngeal_onset_vocative():
    """F8, F9."""
    assert hb(NounSpec("h₃ésth₁", "h₃sth₁", "proterokinetic", "n"))["LOC.SG"][0] == "h₃sth₁í"
    assert hb(NounSpec("ǵʰh₂éns", "ǵʰh₂n̥s", "amphikinetic", "f"))["VOC.SG"][0] == "ǵʰh₂éns"
    assert hb(NounSpec("ph₂tér", "ph₂tr̥", "hysterokinetic", "m"))["VOC.SG"][0] == "ph₂ter"


def test_unaccented_s_stem_headword_gets_root_accent():
    """F3."""
    from pie.classify import by_shape
    c = by_shape({"form": "medos", "pos": "noun", "gender": "n"})
    assert (c.rule, c.spec.strong, c.spec.weak) == ("shape:s-stem-neuter", "médos", "médes")


def test_srh_overrides(lx):
    """F2, F4, F6, F7, F10, F11 (F2/F4/F10 use the new `form` key of overrides.jsonl)."""
    assert lx.entries["pie-lex-yokwr"]["form"] == "yḗkʷr̥" and "yókʷr̥" in lx.entries["pie-lex-yokwr"]["variants"]
    assert lx.cells("pie-lex-yokwr")["NOM.SG"][0] == "yḗkʷr̥" and lx.cells("pie-lex-yokwr")["NOM.PL"][0] == "yékʷōr"
    assert lx.cells("pie-lex-h3okws")["NOM.SG"][0] == "h₃ókʷ"
    assert lx.cells("pie-lex-dhgjhuHs")["GEN.SG"][0] == "dʰǵʰuHés"
    assert lx.cells("pie-lex-h3rexgjs")["LOC.SG"][0] == "h₃rḗǵi"
    assert lx.cells("pie-lex-dusmenexs")["GEN.SG"][0] == "dusménesos"
    assert lx.cells("pie-lex-nokwts")["GEN.SG"][0] == "nékʷts"


# --- athematic-verbs.md, thematic-verbs.md ---------------------------------------------------------------

def cj(strong, weak=None, kind="impf", **kw):
    return conjugate(VerbSpec(strong, weak, kind, **kw), "handbook")


def test_glide_only_after_a_true_cluster():
    """athematic E1, thematic-verbs 2-3: L&Y §4.3.1 *ḱl̥-n-w-énti; LIV ḱluwónt-; Gk δειδίασι."""
    assert cj("ḱl̥néw", "ḱl̥nu")["PRS.3PL"][0] == "ḱl̥nwénti"
    assert cj("tn̥néw", "tn̥nu")["PRS.3PL"][0] == "tn̥nwénti"
    assert cj("ksnéw", "ksnu")["PRS.3PL"][0] == "ksnuwénti"
    assert cj("tḱéy", "tḱi")["PRS.3PL"][0] == "tḱiyénti"
    assert cj("ḱléw", "ḱlu", "pf")["PTCP.ACT"][0] == "ḱluwónts"
    assert cj("ḱléw", "ḱlu", "pf")["MID.AOR.3SG"] == ["ḱlutó", "ḱluwó", "ḱl̥wó"]
    assert cj("ksnéw", "ksnu")["MID.PRS.3SG"][0] == "ksnutór"
    assert cj("dedwóy", "dedwi", "stat")["PRF.3PL"][0] == "dedwiyḗr"


def test_optative_zero_grade_after_an_accented_or_reduplicated_stem():
    """athematic E2, thematic-verbs 4/6: Fortson §5.57, Ringe 2006 p. 30, Beekes §18.8.4."""
    n = cj("h₂wḗh₁", "h₂wéh₁")
    assert n["OPT.3SG"][0] == "h₂wéh₁ih₁t" and n["OPT.3PL"][0] == "h₂wéh₁ih₁ent"
    assert cj("h₁és", "h₁s")["OPT.3SG"][0] == "h₁syéh₁t"
    assert cj("wḗǵʰs", "wéǵʰs", "pf")["OPT.3SG"][0] == "wéǵʰsih₁t"
    assert cj("h₁rudʰéh₁")["OPT.3SG"][0] == "h₁rudʰéh₁ih₁t"
    assert conjugate(VerbSpec("bʰúH", "bʰúH", "pf"), "wiktionary", alternatives=False)["OPT.3PL"] == ["bʰúHih₁n̥t"]


def test_reduplicated_present_3pl():
    """athematic E4: Fortson §5.27 *de-dh₃-n̥ti; Beekes §18.1.3 *dʰé-dʰh₁-n̥ti; Ved. dádhati."""
    r = cj("dʰédʰeh₁", "dʰedʰh₁")
    assert r["PRS.3PL"][0] == "dʰédʰh₁n̥ti" and r["PST.3PL"][0] == "dʰédʰh₁n̥t" and r["IMP.3PL"][0] == "dʰédʰh₁n̥tu"
    assert r["MID.PRS.3PL"][0] == "dʰédʰh₁n̥tor" and r["PRS.1PL"][0] == "dʰedʰh₁més"
    assert r["OPT.3SG"][0] == "dʰedʰh₁ih₁t" and "dʰedʰh₁énti" in r["PRS.3PL"]


def test_narten_and_s_aorist_subjunctive_on_the_e_grade():
    """athematic E3, thematic-verbs 5: Ringe 2006 p. 30; Fortson §5.55."""
    assert cj("h₂wḗh₁", "h₂wéh₁")["SBJV.3SG"][0] == "h₂wéh₁eti"
    s = cj("wḗǵʰs", "wéǵʰs", "pf")
    assert s["AOR.3SG"][0] == "wḗǵʰst" and s["SBJV.3SG"][0] == "wéǵʰseti" and s["IMP.FUT.3SG"][0] == "wéǵʰstōd"


def test_future_imperative_on_the_zero_grade():
    """athematic E5: Ved. dhattā́t, itā́t; Ringe 2006 p. 31 *-tṓd."""
    assert cj("h₁és", "h₁s")["IMP.FUT.2SG"][:2] == ["h₁stṓd", "h₁éstōd"]


def test_thematic_middle_participle_keeps_h1():
    """thematic-verbs 7: L&Y §4.4.1 *-o-mh₁no-."""
    assert cj("widé", None, "pf")["PTCP.MID"][0] == "widómh₁nos"
    assert cj("bʰére")["PTCP.MID"][0] == "bʰéromh₁nos"


def test_t_less_middle_flag():
    """athematic D5 (the flag; the ḱéytor override is a lead decision)."""
    m = cj("ḱéy", None, mid_t_less=True)
    assert m["MID.PRS.3SG"][0] == "ḱéyor" and "ḱéytor" in m["MID.PRS.3SG"] and m["MID.PRS.3PL"][0] == "ḱéyror"
    assert cj("wés")["MID.PRS.3SG"][0] == "wéstor"


def test_verbal_classify_rules_and_overrides(lx):
    """thematic-verbs 8-9 (s-aorist, thematic deponents), athematic S1-S3, D4."""
    from pie.classify import by_shape
    c = by_shape({"form": "dḗyḱst", "pos": "verb", "aspect": "pf"})
    assert (c.rule, c.spec) == ("shape:s-aorist", VerbSpec("dḗyḱs", "déyḱs", "pf"))
    c = by_shape({"form": "mr̥yétor", "pos": "verb", "kind": "word"})
    assert c.spec == VerbSpec("mr̥yé") and conjugate(c.spec)["MID.PRS.3SG"][0] == "mr̥yétor"
    assert lx.cells("pie-lex-h2werst")["IMP.2SG"][0] == "h₂wr̥sdʰí"
    assert lx.cells("pie-lex-tetkjti")["PRS.3PL"][0] == "tétḱn̥ti"
    assert lx.specs["pie-lex-wewokjti"]["spec"]["weak"] == "wewḱ"
    assert lx.cells("pie-lex-bhuHt")["AOR.3PL"][0] == "bʰuHént"


# --- closed-class-compounds.md (closed class and compound.py; realize.py fixes are tested in test_realize.py) --

def test_closed_class_table_consistency(lx):
    """C3-C6: masc. = neut. obliques, dat. pl. = abl. pl., accented fem. 'three', VOC cells, kʷi- ACC.PL."""
    d = lx.closed
    for t in ("demonstrative_so", "interrogative_kwo", "interrogative_kwi", "relative_yo", "deictic_ki", "deictic_eno"):
        m, n = d[t].get("m") or d[t]["mf"], d[t]["n"]
        for k in set(m) & set(n):
            if k.split(".")[0] in ("GEN", "ABL", "DAT", "LOC", "INS"):
                assert m[k][0] == n[k][0], (t, k)
        for g, c in d[t].items():
            if isinstance(c, dict) and "DAT.PL" in c:
                assert c["DAT.PL"][0] == c["ABL.PL"][0], (t, g)
    assert d["numerals"]["3"]["f"]["ACC.PL"][0] == "tísrn̥s"
    assert d["numerals"]["3"]["m"]["VOC.PL"] == d["numerals"]["3"]["m"]["NOM.PL"]
    assert d["interrogative_kwi"]["n"]["ACC.PL"] == ["kʷíh₂"]


def test_compound_hiatus_and_numeral_aliases(lx):
    """P1, P2."""
    from pie.compound import PREFIX_ALIASES
    assert PREFIX_ALIASES["pie-lex-dwoh1"] == "closed:numerals/2" and PREFIX_ALIASES["pie-lex-sm"] == "closed:prefix/sm"


# --- conventions decided by the lead (docs/STATUS.md "Conventions (engine sweep)") -----------------------

def test_convention_eh2_vocative_a():
    """Fortson §6.70 *-a, retracted; Ringe's unretracted *-á and the *-eh₂ forms as alternatives."""
    assert hb(NounSpec("bʰoréh₂", gender="f"))["VOC.SG"] == ["bʰóra", "bʰorá", "bʰóreh₂", "bʰoréh₂"]
    assert decline_adj(AdjSpec("néwo"))["f"]["VOC.SG"][0] == "néwa"


def test_convention_devi_accusative():
    """Stang's law *-ih₂m (Fortson §17.12, Beekes p. 204, L&Y); Ringe's *-ih₂m̥ second; vr̥kī́ type unchanged."""
    assert hb(NounSpec("déywih₂", "diwyéh₂", "proterokinetic", "f"))["ACC.SG"] == ["déywih₂m", "déywih₂m̥"]
    f = decline_adj(AdjSpec("ténh₂u", "tn̥h₂éw", "tn̥h₂éwih₂", "tn̥h₂uyéh₂", "proterokinetic"))["f"]
    assert f["ACC.SG"][:2] == ["tn̥h₂éwih₂m", "tn̥h₂éwih₂m̥"]


def test_convention_vocative_plural_retracts():
    """Fortson §6.52 (Ved. dévās); the dual likewise; neuters unchanged."""
    c = hb(NounSpec("deywó"))
    assert c["VOC.PL"][:2] == ["déywōs", "deywṓs"] and c["VOC.DU"][0] == "déywoh₁"
    assert hb(NounSpec("yugó", gender="n"))["VOC.PL"][0] == "yugéh₂"


def test_convention_consonant_stem_dual():
    """*-h₁e (Ringe, Beekes §13.2.11, L&Y §2.1.1; Fortson either), *-h₁ second; i/u-stems keep *-h₁ first."""
    assert hb(NounSpec("pód", "ped", "acrostatic", nom_sg="pṓds"))["NOM.DU"] == ["pódh₁e", "pódh₁"]
    assert hb(NounSpec("ménti", "mn̥téy", "proterokinetic", "f"))["NOM.DU"][0] == "méntih₁"


def test_convention_boukolos_before_u_in_the_handbook():
    """Mallory & Adams *perkʷunos; Wiktionary's module keeps its full boukólos scope."""
    c = hb(NounSpec("pérkʷuno"))
    assert c["NOM.SG"] == ["pérkʷunos", "pérkunos"]
    assert c["VOC.PL"][0] == "pérkʷunōs" and c["VOC.DU"][0] == "pérkʷunoh₁"
    assert decline(NounSpec("pérkʷuno"), "wiktionary", alternatives=False)["NOM.SG"] == ["pérkunos"]


def test_convention_2du_primary_tes():
    """Ringe 2006 p. 31 *-tés for 2du and 3du; Beekes's tentative *-tHe/os as the alternative *-th₁es."""
    assert cj("bʰére")["PRS.2DU"] == ["bʰéretes", "bʰéreth₁es"]
    assert cj("h₁és", "h₁s")["PRS.2DU"] == ["h₁stés", "h₁sth₁és"]


def test_convention_lexeme_decisions(lx):
    """u-adjective suffix accent (L&Y, Vedic + Greek), h₁ed- Narten, ḱéytor t-less, dédeh₃ti mobile, 'I', 'ten'."""
    assert lx.cells("pie-lex-pleth2us")["NOM.SG"][0] == "pl̥th₂ús"
    assert lx.cells("pie-lex-sweh2dus")["NOM.SG"][0] == "sweh₂dús"
    assert lx.cells("pie-lex-tenh2us")["NOM.SG"][0] == "ténh₂us"       # Ringe's model word: left for the lead
    e = lx.cells("pie-lex-h1edti")
    assert e["PRS.3SG"][0] == "h₁ḗdti" and e["PRS.3PL"][0] == "h₁édn̥ti"
    assert any(x.get("displaced_by_override") for x in lx.specs["pie-lex-h1edti"]["extra_specs"])
    assert lx.cells("pie-lex-kjeytor")["MID.PRS.3SG"][:2] == ["ḱéyor", "ḱéytor"]
    assert lx.cells("pie-lex-dedeh3ti")["PRS.1PL"][0] == "dedh₃més"
    assert lx.closed["personal"]["1"]["NOM.SG"][0] == "h₁eǵóh₂"
    assert lx.closed["numerals"]["indeclinable"]["10"][0] == "déḱm̥"


def test_men_neuter_instrumental_singular_keeps_the_full_grade():
    """The i/u instrumental rule must not fire for men-neuters (Ringe 2006 sh₁m̥énh₁)."""
    assert hb(NounSpec("séh₁mn̥", "sh₁mén", "proterokinetic", "n"))["INS.SG"][0] == "sh₁ménh₁"


def test_regressions_found_by_the_dry_rerealization(lx):
    """Narten participle h₁édn̥ts declines (gen. h₁édn̥tos); néh₂w- 'ship' still composes as néh₂u-."""
    assert lx.participle_cells("pie-lex-h1edti", "ACT", "m")["GEN.SG"] == ["h₁édn̥tos"]
    from pie.compound import resolve
    c = resolve({"first": "pie-lex-neh2us", "second": "pie-lex-wiHros", "type": "determinative"}, lx)
    assert c.first_form == "néh₂u"
    assert lx.cells("pie-lex-neh2us")["VOC.SG"][0] == "néh₂u"
