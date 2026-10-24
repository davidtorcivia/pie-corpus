"""Morphology engine: inflect PIE stems.

Layer 1 (this module): (strong stem, weak stem, class) → cells. The spec
format deliberately mirrors Wiktionary's inflection-template args, so that
pie.crosscheck can regenerate every Wiktionary table and compare cells.
Layer 2 (lemma → spec by shape, for lexemes without a table) comes later.

Conventions: one reconstruction can be written several ways, so every
cell is a list of forms, primary first.
  "wiktionary" reproduces Wiktionary's module: uncontracted thematic
               (*-oes*, *-oey*, *-ead*), gen. pl. *-oHom*, eh₂-stem acc.
               *-ām*, *-mos* before *-bʰos*.
  "handbook"   the contracted thematic forms of Fortson, Beekes, Lundquist &
               Yates and Mallory & Adams (*-ōs*, *-ōy*, *-ōd*; Ringe prints the
               uncontracted *-oes*, *-oey*, *-ead*, which are the "wiktionary"
               forms), gen. pl. *-ōm* (a project convention: Fortson §6.56 has
               *-oHom*, Ringe *-ooHom*, L&Y *-oh₁/₃om*, Beekes and M&A *-om*;
               Danka, Voyles and Lehmann write *-ōm*), *-bʰ-* first, gen. sg.
               *-és* ~ *-ós*. Checked against the books in the engine sweep
               (docs/audits/engine-sweep/); see "Conventions (engine sweep)" below.
With alternatives=True (the default), the other convention's forms follow
the primary ones, so nothing is lost.

Conventions (engine sweep, 2026-10-24; docs/audits/engine-sweep/INTEGRATION.md,
docs/STATUS.md "Conventions (engine sweep)"). Rule: follow the majority of the
handbooks together with the Vedic/Greek evidence; the other form stays an
alternative cell (or, for a lexeme spec, in extra_specs), never deleted.
  - eh₂ vocative *-a*, retracted (Fortson §6.70: h₂ékʷa, bʰóra); Ringe's
    unretracted *-á* and *-eh₂* follow.
  - devī acc. sg. *-ih₂m* by Stang's law (Fortson §17.12, Beekes p. 204, L&Y);
    Ringe's *-ih₂m̥* second. Athematic *-eh₂* stems likewise *-eh₂m*, *-ās*.
  - u-stem loc. *-éw(i)* primary, Beekes's *-ḗw* an alternative; i-stem loc.
    order unchanged (Fortson prints no i-stem locative, so the condition
    "Fortson and Ringe agree" on *-ḗy* first is not met).
  - u-adjectives with suffix accent where L&Y and Vedic/Greek agree
    (pl̥th₂ús, gʷr̥h₂ús, sweh₂dús, h₁wr̥Hús, h₁ln̥gʷʰús, bʰn̥ǵʰús; mr̥ǵʰús and
    dlukús on Greek): lexeme specs, data/lexicon/overrides.jsonl.
  - thematic dat./abl. pl. *-oybʰos* stays primary.
  - vocative plural (and dual) retract the accent like the singular
    (Fortson §6.52: Ved. voc. pl. dévās); non-neuter, every declension.
  - consonant-stem nom.-acc. dual *-h₁e* (Ringe; Beekes §13.2.11; L&Y §2.1.1;
    Fortson §6.13 either), *-h₁* second; i/u-stems keep *-h₁* first.
  - boukólos: the handbook thematic and eh₂ declensions keep the labiovelar
    before syllabic u (Mallory & Adams *perkʷunos*); Wiktionary's full scope is
    the alternative and the Wiktionary convention (phon.delabialize).
  - 2du primary *-tes* = 3du (Ringe 2006 p. 31); Beekes's tentative *-tHe/os*
    as the alternative *-th₁es*.
  - lexeme decisions (overrides.jsonl): h₁ed- Narten (h₁ḗdti, h₁édn̥ti);
    ḱéytor t-less middle (VerbSpec.mid_t_less); dédeh₃ti mobile weak stem
    (dedh₃més). Closed class: 'I' h₁eǵóh₂, 'ten' déḱm̥ (closed_class.json _refs).

Features: nouns "NOM.SG", "GEN.PL", …; verbs "PRS.3SG", "PST.1PL",
"IMP.2SG", "PRF.3PL", "AOR.3SG" (active; indicative unless IMP).
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field, replace

from .phon import (Seg, contract_eh2m, delabialize, has_accent, join, junction_laryngeal_loss,
                   lengthen_last_vowel, parse, pinault, stang, szemerenyi, zero_grade_suffix)
from .phon import render as _render

CASES = ["NOM", "VOC", "ACC", "GEN", "ABL", "DAT", "LOC", "INS"]
NUMBERS = ["SG", "DU", "PL"]
PERSONS = ["1SG", "2SG", "3SG", "1DU", "2DU", "3DU", "1PL", "2PL", "3PL"]
CONVENTIONS = ("wiktionary", "handbook")

Cells = dict[str, list[str]]


def _p(s: str) -> list[Seg]:
    return parse(s) if s else []


def render(segs: list[Seg]) -> str:
    return _render(delabialize(segs))


def _render_kw(segs: list[Seg]) -> str:
    """Handbook rendering for the thematic and eh₂ declensions: the labiovelar is kept before syllabic u
    (Mallory & Adams *perkʷunos, 7 times), i.e. boukólos only next to consonantal w. The fully
    delabialized Wiktionary-module form follows as an alternative (_with_delabialized)."""
    return _render(delabialize(segs, before_u=False))


def _with_delabialized(out: Cells) -> Cells:
    return {k: _uniq(v + [render(_p(f)) for f in v]) for k, v in out.items()}


def _add(stem: list[Seg], ending: str) -> list[Seg]:
    return join(stem, _p(ending))


def _uniq(xs) -> list[str]:
    return list(dict.fromkeys(x for x in xs if x))


def _merge(primary: Cells, other: Cells) -> Cells:
    return {k: _uniq(v + other.get(k, [])) for k, v in primary.items()}


def _bare(s: str) -> str:
    return s.strip().lstrip("*").rstrip("-")


# =============================================================================
# Nominal
# =============================================================================

@dataclass
class NounSpec:
    """A nominal stem. `strong`/`weak` follow Wiktionary's template args 1 and 2."""
    strong: str
    weak: str | None = None
    accent_class: str | None = None   # acrostatic | proterokinetic | hysterokinetic | amphikinetic
    gender: str = "m"                 # m | f | n
    nom_sg: str | None = None         # lexical override (lengthened grade: pṓds, gʷṓws, dyḗws)
    loc_sg: list[str] = field(default_factory=list)  # explicit LOC.SG forms or stems
    devi: bool = False                # ih₂/yeh₂ feminine: asigmatic nominative, weak locative
    adjective: bool = False           # Wiktionary's adjective module differs in places (nom. pl. dlukúes)

    @property
    def kind(self) -> str:
        s = _bare(self.strong)
        if self.weak is None and s[-1:] in ("o", "ó"):
            return "thematic"
        if self.weak is None and s.endswith(("eh₂", "éh₂")) and self.gender != "n":
            return "eh2"
        return "athematic"


_THEMATIC = {
    "wiktionary": {
        "NOM.SG": ["os"], "VOC.SG": ["e"], "ACC.SG": ["om"], "GEN.SG": ["osyo"], "ABL.SG": ["ead"],
        "DAT.SG": ["oey"], "LOC.SG": ["ey", "oy"], "INS.SG": ["oh₁"],
        "NOM.DU": ["oh₁"], "VOC.DU": ["oh₁"], "ACC.DU": ["oh₁"],
        "NOM.PL": ["oes"], "VOC.PL": ["oes"], "ACC.PL": ["oms"], "GEN.PL": ["oHom"],
        "ABL.PL": ["omos", "obʰos"], "DAT.PL": ["omos", "obʰos"], "LOC.PL": ["oysu"], "INS.PL": ["ōys"],
    },
    "handbook": {
        "NOM.SG": ["os"], "VOC.SG": ["e"], "ACC.SG": ["om"], "GEN.SG": ["osyo"], "ABL.SG": ["ōd", "ōt"],
        "DAT.SG": ["ōy"], "LOC.SG": ["oy", "ey"], "INS.SG": ["oh₁"],
        "NOM.DU": ["oh₁"], "VOC.DU": ["oh₁"], "ACC.DU": ["oh₁"],
        # ACC.PL: -ons (Fortson §6.45, Ringe -o-ns), lengthened -ōns (Byrd), -oms (pre-form)
        "NOM.PL": ["ōs"], "VOC.PL": ["ōs"], "ACC.PL": ["ons", "ōns", "oms"], "GEN.PL": ["ōm"],
        # -oybʰyos: Indo-Iranian-style variant written by Byrd 2013 and Adams 1997
        "ABL.PL": ["oybʰos", "omos", "oybʰyos"], "DAT.PL": ["oybʰos", "omos", "oybʰyos"], "LOC.PL": ["oysu"],
        "INS.PL": ["ōys"],
    },
}
_THEMATIC_NEUTER = {
    "NOM.SG": ["om"], "VOC.SG": ["om"], "ACC.SG": ["om"],
    "NOM.DU": ["oy", "oyh₁"], "VOC.DU": ["oy", "oyh₁"], "ACC.DU": ["oy", "oyh₁"],
    "NOM.PL": ["eh₂"], "VOC.PL": ["eh₂"], "ACC.PL": ["eh₂"],
}


def _thematic(spec: NounSpec, conv: str) -> Cells:
    stem = _p(_bare(spec.strong))
    assert stem[-1].base == "o", spec.strong
    base, tv_acc = stem[:-1], stem[-1].acc
    table = dict(_THEMATIC[conv])
    if spec.gender == "n":
        table.update(_THEMATIC_NEUTER)
        if conv == "handbook":
            # neuter dual *-o-ih₁ (Fortson §6.50, L&Y ch. 122 §2.1.1; Ringe -oy(h₁)); bare -oy kept second.
            # Wiktionary's module puts -oy first, so the shared table keeps that order for its convention.
            for k in ("NOM.DU", "VOC.DU", "ACC.DU"):
                table[k] = ["oyh₁", "oy"]
    hb = conv == "handbook"
    rd = _render_kw if hb else render
    out = {}
    for feat, ends in table.items():
        forms = []
        for e in ends:
            es = _p(e)
            if tv_acc:  # accent on the thematic vowel stays on the vowel that replaces it
                es = [replace(es[0], acc=True)] + es[1:]
            forms.append(rd(base + es))
        out[feat] = forms
    if conv == "handbook" and spec.gender != "n" and has_accent(stem):
        # vocative accent on the first syllable (Ved. vŕ̥ka, Gk ἄδελφε): wĺ̥kʷe, moysé → móyse
        out["VOC.SG"] = _uniq([rd(_initial_accent(base + _p("e")))] + out["VOC.SG"])
    return _with_delabialized(out) if hb else out


_EH2 = {
    "NOM.SG": [""], "VOC.SG": [""], "ACC.SG": ["m"], "GEN.SG": ["s"], "ABL.SG": ["s"],
    "DAT.SG": ["ey"], "LOC.SG": ["i", ""], "INS.SG": ["h₁"],   # -eh₂i first: the endingless form = NOM
    "NOM.DU": ["h₁", "h₁e"], "VOC.DU": ["h₁", "h₁e"], "ACC.DU": ["h₁", "h₁e"],
    "NOM.PL": ["es"], "VOC.PL": ["es"], "ACC.PL": ["ms"], "GEN.PL": ["oHom"],
    "ABL.PL": ["mos", "bʰos"], "DAT.PL": ["mos", "bʰos"], "LOC.PL": ["su"], "INS.PL": ["mis", "bʰis"],
}


def _eh2(spec: NounSpec, conv: str) -> Cells:
    stem = _p(_bare(spec.strong))
    hb = conv == "handbook"
    render = _render_kw if hb else globals()["render"]   # noqa: the handbook keeps kʷ before u (see _render_kw)
    out = {feat: [render(_add(stem, e)) for e in ends] for feat, ends in _EH2.items()}
    if conv == "wiktionary":
        out["ACC.SG"] = [render(contract_eh2m(_add(stem, "m")))]
    else:
        # *-eh₂m (> *-ām): the m is consonantal after the eh₂ nucleus, never *-eh₂m̥
        out["ACC.SG"] = [render(stem + [Seg("m", "R")])]
        out["GEN.PL"] = [render(_add(stem, "ōm"))]
        # acc. pl. *-ās < *-eh₂ns (Fortson §6.70; Ringe -eh₂ns)
        e = stem[-2]
        out["ACC.PL"] = [render(stem[:-2] + [Seg("a", "V", long=True, acc=e.acc), Seg("s", "C")]),
                         render(stem + [Seg("n", "R"), Seg("s", "C")])]
        for k in ("ABL.PL", "DAT.PL", "INS.PL"):
            out[k] = out[k][::-1]
        # vocative *-a (Fortson §6.70: *-ah₂ with the laryngeal lost before a pause; Ringe 2006 §2.3.4 *-[a];
        # Ringe p. 21: utterance-final laryngeal loss) with the retracted accent of Fortson §6.70 (Gk νύμφα,
        # OCS ženo); Ringe's unretracted *-á, then the nominative-like *-eh₂ forms (Mallory & Adams Table 4.6,
        # Beekes *-h₂e?) follow as alternatives (engine sweep convention, feminine.md D2)
        voc_a = stem[:-2] + [Seg("a", "V", acc=stem[-2].acc)]
        out["VOC.SG"] = _uniq([render(_initial_accent(voc_a)), render(voc_a), render(_initial_accent(stem))]
                              + out["VOC.SG"])
        # gen. sg. *-eh₂es beside -eh₂s (Beekes, Lundquist & Yates)
        out["GEN.SG"] = _uniq(out["GEN.SG"] + [render(_add(stem, "es"))])
        # instr. sg. *-eh₂eh₁ beside *-eh₂h₁ (Ringe 2006 §2.3.4 *-eh₂(e)h₁; Mallory & Adams Table 4.6)
        out["INS.SG"] = _uniq(out["INS.SG"] + [render(_add(stem, "eh₁"))])
        # nom.-acc. du. *-eh₂ih₁ (Beekes §13.2.11: Ved. -e, OCS -ě) beside the generic *-h₁/-h₁e
        for k in ("NOM.DU", "VOC.DU", "ACC.DU"):
            out[k] = _uniq(out[k] + [render(_add(stem, "ih₁"))])
        out = _with_delabialized(out)
    return out


def _athematic(spec: NounSpec, conv: str) -> Cells:
    strong = _p(_bare(spec.strong))
    weak = _p(_bare(spec.weak or spec.strong))
    weak_acc = has_accent(weak)
    neuter = spec.gender == "n"
    hb = conv == "handbook"
    # Wiktionary: proterokinetic INS.SG and oblique plural take the zero-grade
    # suffix, accented (bʰeh₂ǵʰéw- → bʰeh₂ǵʰú-mos). Handbook: plain weak stem.
    root_accented = any(x.acc and x.kind == "V" for x in strong)
    if hb:
        # men-/mon-stems whose given weak stem has lost the m (Wiktionary's sh₂in̥ for sh₂imṓ): *-mn- is kept
        # after a short vowel (Byrd, Handbook ch. 8 §2, the Asno law deletes the m only after a heavy
        # syllable: *h₂éḱmn-es → áśnas; Ringe 2006 §2.3.4: limn̥bʰí, sh₁m̥néh₁; Hitt. išḫimanta, OE sīmon).
        # The m-less Wiktionary forms follow as alternatives. After a heavy syllable an m-less weak stem is
        # left as given (h₂ḱn̥-, the Asno-law reading); the h₂éḱmō lexeme itself has a hand override with the m
        # kept (h₂ḱmn-, t017 review: Ved. aśnás as a later loss), so the corpus follows the override (engine
        # sweep r-n-stems.md notes the contradiction; open for the lead).
        weak = _restore_mn(strong, weak)
    obl = zero_grade_suffix(weak) if (spec.accent_class == "proterokinetic" and root_accented and not hb) else weak
    # Handbook: i/u-stems with an accented full-grade suffix in the weak stem (-éw-/-éy-/-ów-) take the
    # zero-grade suffix, accented, before the consonant-initial oblique plural endings: Ringe 2006 §2.3.4–5
    # (mn̥tíbʰi, ǵustúbʰi, ǵustúmos, ǵustúsu; tn̥h₂úbʰi, tn̥h₂úsu), Beekes §13.2.6a (*-u-bʰi, *-u-su);
    # Ved. sūnúbhis, agníbhis, pṛthúbhis, urúbhis. The acrostatic type keeps its root accent (h₂éwibʰi).
    # Only true i/u-stems (strong stem in syllabic -i/-u), not diphthongal root nouns (gʷṓws: Ved. góbhis).
    iu_stem = bool(strong) and strong[-1].kind == "R" and strong[-1].syl and strong[-1].base in ("y", "w")
    obl_pl = _zero_grade_iu(weak) if (hb and iu_stem) else obl
    obl_iu = obl_pl          # the i/u zero grade alone (instrumental sg. below), before the men-stem rule
    if hb and neuter and spec.accent_class == "proterokinetic":
        # men-neuters: zero-grade suffix before consonant-initial endings, accented as in the proterokinetic
        # weak cases (Lundquist & Yates, Handbook ch. 122 §2.4.1: Ved. dhā́mabhis < *dʰéh₁-mn̥-bʰis; Gk -μασι
        # < *-mn̥-si; cf. Ringe 2006 §2.3.4 mn̥tíbʰi): ḱlumén- → ḱlumń̥bʰos, ḱlumń̥su (engine sweep, r-n-stems.md
        # defect 2; L&Y's fixed root accent is the dissent)
        obl_pl = _zero_grade_men(obl_pl)

    def w(acc_ending: str, plain_ending: str, stem: list[Seg] | None = None) -> str:
        st = weak if stem is None else stem
        return render(_add(st, plain_ending if has_accent(st) else acc_ending))

    out: Cells = {}
    # --- singular, strong
    if neuter:
        out["NOM.SG"] = out["VOC.SG"] = out["ACC.SG"] = [render(strong)]
    else:
        if spec.nom_sg:
            nom = _p(_bare(spec.nom_sg))
        elif spec.devi or (strong[-1].base == "h2" and len(strong) > 1 and strong[-2].base == "y" and strong[-2].syl):
            nom = strong                              # asigmatic ih₂-feminine: déywih₂, pótnih₂
        elif strong[-1].base == "s" and strong[-1].kind == "C":
            # the stem already ends in -s: -os-s → -ōs (Szemerényi); C+s stays (ǵʰh₂éns)
            nom = lengthen_last_vowel(strong) if strong[-2].kind == "V" else strong
        else:
            nom = szemerenyi(_add(strong, "s"))
        out["NOM.SG"] = [render(nom)]
        out["VOC.SG"] = [render(strong)]
        if hb:
            # vocative accent on the first syllable (Ved. pítar, Gk πάτερ): dʰugh₂tér → dʰúgh₂ter
            out["VOC.SG"] = _uniq([render(_initial_accent(strong))] + out["VOC.SG"])
            if strong[-1].syl and strong[-1].base in ("y", "w"):
                # i/u-stem vocative in full-grade *-ey/-ew (Ved. ágne, sū́no; Fortson): h₁ń̥gʷney, súHnew
                full = strong[:-1] + [Seg("e", "V"), Seg(strong[-1].base, "R")]
                out["VOC.SG"] = _uniq([render(_initial_accent(full))] + out["VOC.SG"])
            if nom is strong and len(strong) > 2 and strong[-1].base == "h2" and strong[-2].base == "y" \
                    and strong[-2].syl:
                # ih₂-feminine vocative in short *-i: Ringe 2006 §2.3.5 (tn̥h₂éwih₂, voc. tn̥h₂éwi; h₁sóntih₂,
                # voc. h₁sónti; sémih₂, voc. sémi); with the vocative's initial accent (Fortson §6.7) as in
                # Ved. pŕ̥thivi, dévi. Ringe's unretracted form and the -ih₂ forms follow as alternatives.
                short = strong[:-1]
                out["VOC.SG"] = _uniq([render(_initial_accent(short)), render(short)] + out["VOC.SG"])
            if spec.nom_sg and len(strong) > 1 and strong[-1].base == "h2" and not strong[-2].vocalic:
                # asigmatic C+h₂ stem with a lexical nominative (gʷḗn): voc. = nom. (Ringe 2006 §2.3.4 gʷḗn),
                # and the bare stem *gʷénh₂ (Fortson §6.70, Beekes §13.2.6) as an alternative nominative
                out["NOM.SG"] = _uniq(out["NOM.SG"] + [render(strong)])
                out["VOC.SG"] = _uniq([render(nom)] + out["VOC.SG"])
        if hb:
            # a bare-stem vocative ending in a consonantal resonant after a non-vowel is syllabic (néh₂w- → néh₂u)
            def _syl_final(f: str) -> str:
                x = _p(f)
                if len(x) > 1 and x[-1].kind == "R" and not x[-1].syl and not x[-2].vocalic:
                    x = x[:-1] + [replace(x[-1], syl=True)]
                return render(x)
            out["VOC.SG"] = _uniq([_syl_final(f) for f in out["VOC.SG"]])
        acc = stang(_add(strong, "m"))
        out["ACC.SG"] = [render(contract_eh2m(acc) if not hb else acc)]
        # athematic stem in *-eh₂ (dn̥ǵʰwéh₂-): Stang's law after the laryngeal (Fortson §3.38, §6.70) gives
        # *-eh₂m, not *-eh₂m̥ (Ringe 2006 §2.3.4 dn̥ǵʰwéh₂m (-ām)); C+H stems keep -m̥ (Ringe gʷénh₂m̥), and so do
        # *-oh₁ (Beekes p. 199: Ved. pánthām scans disyllabic) and the vr̥kī́ type (Ved. vr̥kíyam)
        eh2_stem = len(strong) > 1 and strong[-1].base == "h2" and strong[-2].kind == "V" and strong[-2].base == "e"
        # devī type (asigmatic -ih₂): acc. sg. *-ih₂m by Stang's law (Fortson §17.12; Beekes §13.2.6 p. 204, Ved.
        # devī́m; L&Y Table 122.3 note), Ringe 2006 §2.3.5's *-ih₂m̥ kept second (engine sweep convention, feminine.md D1)
        devi_stem = nom is strong and len(strong) > 1 and strong[-1].base == "h2" and strong[-2].syl \
            and strong[-2].base == "y"
        if hb and (eh2_stem or devi_stem):
            out["ACC.SG"] = _uniq([render(strong + [Seg("m", "R")])] + out["ACC.SG"])
    # --- singular, weak
    if not weak_acc:
        # primary -és; -ós as an alternative (Beekes, Lundquist & Yates; Fortson §6.8 calls it a spread)
        gen = [w("és", "")] + ([w("ós", "")] if hb else [])
    else:
        last = weak[-1]
        gen = [render(_add(weak, "os" if (last.base == "s" and last.kind == "C") else "s"))]
    if hb and spec.weak and weak[-1].syl and weak[-1].base == "y":
        # i-stem gen. *-eys beside -is (h₂éweys; Beekes, Lundquist & Yates)
        gen = _uniq(gen + [render(_add(weak[:-1] + [Seg("e", "V"), Seg("y", "R")], "s"))])
    out["GEN.SG"] = out["ABL.SG"] = gen
    out["DAT.SG"] = [w("éy", "ey")]
    if hb and spec.weak is None and strong[-1].syl and strong[-1].base in ("y", "w"):
        # i/u-stem with no weak stem given: full-grade suffix -ey-/-ew- (gʰóstipoteys, Ved. -es, Goth. -ais),
        # not strong + s, which would equal the nominative
        full = strong[:-1] + [Seg("e", "V", acc=strong[-1].acc), Seg(strong[-1].base, "R")]   # suHnú- → suHnéws
        out["GEN.SG"] = out["ABL.SG"] = _uniq([render(_add(full, "s"))] + gen)
        out["DAT.SG"] = _uniq([render(_add(full, "ey"))] + out["DAT.SG"])

    out["INS.SG"] = [w("éh₁", "h₁", obl)]
    if hb and obl_iu is not weak:
        # i/u-stem instrumental *-i-h₁/*-u-h₁ on the accented zero-grade suffix: Fortson §6.10 (Ved. matī́),
        # Ringe 2006 pp. 47, 49 (mn̥tíh₁, ǵustúh₁, mríh₁, drúh₁, tn̥h₂úh₁), Beekes §13.2.6a (*-u-h₁).
        # The full-grade form (mn̥téyh₁) follows as an alternative (engine sweep, i-u-stems.md #5).
        out["INS.SG"] = _uniq([render(_add(obl_iu, "h₁"))] + out["INS.SG"])
    out["LOC.SG"] = _locative(spec, strong, weak, hb)
    if hb:   # prefer the -i (or i-stem -ēy) locative to the endingless one (which looks like the nominative)
        out["LOC.SG"] = sorted(out["LOC.SG"], key=lambda f: not f.endswith(("i", "í", "y")))
    # --- dual
    if neuter:
        # s-stem neuters take the e-grade (weak) suffix: déḱos → déḱesih₁; others the strong stem
        e_grade_s = len(weak) > 1 and weak[-1].base == "s" and weak[-2].base == "e"
        du = [render(_add(weak if (e_grade_s and spec.weak) else strong, "ih₁"))]
        if hb and strong[-1].syl and strong[-1].base in ("y", "w"):
            if strong[-1].base == "y":
                # i-stem: -i-ih₁ → -ih₁ (Fortson §6.13 *h₃ekʷih₁ 'both eyes'; Ringe 2006 p. 47 mórīh₁ (?))
                du = [render(_add(strong[:-1], "íh₁" if strong[-1].acc else "ih₁"))]
            elif strong[-1].acc:
                # accented -ú + ih₁ → -wíh₁ (Ved. urvī́, Fortson §6.13), not -úyh₁ (engine sweep, i-u-stems.md #15)
                du = [render(_add(strong[:-1] + [Seg("w", "R")], "íh₁"))]
    else:
        du = [render(_add(strong, "h₁")), render(_add(strong, "h₁e"))]
        iu = strong[-1].syl and strong[-1].base in ("y", "w")
        vh2 = len(strong) > 1 and strong[-1].base == "h2" and strong[-2].vocalic     # ā-/ī-stems: see feminine.md
        if hb and not iu and not vh2:
            # consonant stems: *-h₁e (Ringe 2006 throughout; Beekes §13.2.11 C-stems *-h₁e, u-stems *-h₁; L&Y
            # ch. 122 §2.1.1 *-h₁e, glide-final stems *-h₁; Fortson §6.13 either), *-h₁ kept second
            # (engine sweep convention, t020 review)
            du = du[::-1]
    out["NOM.DU"] = out["VOC.DU"] = out["ACC.DU"] = du
    # --- plural
    if neuter:
        if len(strong) > 1 and strong[-1].base in ("s", "n", "r") and not strong[-1].syl and strong[-2].kind == "V":
            # collective: -os-h₂ → -ōs, -or-h₂ → -ōr, -on-h₂ → -ō
            coll = lengthen_last_vowel(strong if strong[-1].base == "s" else strong[:-1])
            npl = [render(coll)]
            if hb and strong[-1].base == "s" and e_grade_s and spec.weak:
                # s-stem neuters: handbook *-es-h₂ (Fortson; Gk γένεα, Ved. -āṃsi, Lat. genera), the
                # collective -ōs kept as the alternative (t019 review: nébʰōs read as a plural)
                npl = [render(_add(weak, "h₂"))] + npl
        elif hb and len(strong) > 2 and strong[-1].kind == "R" and strong[-1].syl and strong[-1].base in ("r", "l") \
                and any(x.acc and x.kind == "V" for x in strong):
            # r/n (l/n) heteroclite: collective *CéC-ōr < *-or-h₂ (Fortson §6.15 *ud-ōr, Hitt. widār; Ringe 2006
            # §2.3.4(ii) *wédōr; Wiktionary coll= wédor, péh₂wor, déh₃or, yékʷor): accented e-grade root,
            # lengthened -ōr/-ōl. The pre-form *-r̥-h₂ stays as the alternative (engine sweep,
            # s-root-heteroclite.md F1)
            i = next(j for j, x in enumerate(strong) if x.acc and x.kind == "V")
            root = strong[:i] + [Seg("e", "V", acc=True)] + strong[i + 1:-1]
            npl = [render(root + [Seg("o", "V", long=True), Seg(strong[-1].base, "R")]), render(_add(strong, "h₂"))]
        else:
            npl = [render(_add(strong, "h₂"))]
        out["NOM.PL"] = out["VOC.PL"] = out["ACC.PL"] = npl
    else:
        pl = strong
        last = strong[-1]
        if last.kind == "R" and last.syl and last.base in ("y", "w") and not last.long:
            if not last.acc:
                pl = strong[:-1] + [Seg("e", "V"), Seg(last.base, "R")]   # h₂ówi- → h₂óweyes
            elif not spec.adjective and spec.weak and len(weak) > 1 and weak[-1].base == last.base \
                    and weak[-2].base == "e":
                pl = weak                                                 # h₁n̥gʷní- → h₁n̥gʷnéyes
        out["NOM.PL"] = out["VOC.PL"] = [render(_add(pl, "es"))]
        # (not when the plural already took the e-grade weak stem or the unaccented -ey-/-ew- above)
        if hb and pl is strong and strong[-1].syl and strong[-1].base in ("y", "w"):
            # i/u-stem nominative plural in the full-grade suffix (Ved. sūnávas, agnáyas): suHnéwes
            full = strong[:-1] + [Seg("e", "V", acc=strong[-1].acc), Seg(strong[-1].base, "R")]
            out["NOM.PL"] = out["VOC.PL"] = _uniq([render(_add(full, "es"))] + out["NOM.PL"])
        out["ACC.PL"] = [render(_add(strong, "ms"))]
        if hb:
            # *-ns/-n̥s (< *-ms; Fortson §6.14, Ringe): pódn̥s, ph₂térn̥s, h₂ówins
            acc_pl = [render(_add(strong, "ns"))]
            if len(strong) > 1 and strong[-1].base == "w" and not strong[-1].syl and strong[-2].kind == "V":
                # Stang's law first: gʷṓs (Ringe; Ved. gā́s, Gk dial. βῶς), not the pre-form gʷówn̥s
                acc_pl.insert(0, render(lengthen_last_vowel(strong[:-1]) + [Seg("s", "C")]))
            if eh2_stem:
                # *-eh₂ns > *-ās (Fortson §6.70; Ringe 2006 §2.3.4 dn̥ǵʰwéh₂ns (-ās)); -eh₂n̥s kept as an alternative
                acc_pl = [render(strong[:-2] + [Seg("a", "V", long=True, acc=strong[-2].acc), Seg("s", "C")]),
                          render(strong + [Seg("n", "R"), Seg("s", "C")])] + acc_pl
            out["ACC.PL"] = acc_pl + out["ACC.PL"]
    out["GEN.PL"] = ([w("ṓm", "ōm")] if hb else []) + [w("óHom", "oHom")]
    mos, bhos = w("mós", "mos", obl_pl), w("bʰós", "bʰos", obl_pl)
    # -bʰyos: variant written by Byrd 2013 and Adams 1997 (h₂áwibʰyos)
    out["DAT.PL"] = out["ABL.PL"] = [bhos, mos, w("bʰyós", "bʰyos", obl_pl)] if hb else [mos, bhos]
    out["LOC.PL"] = [w("sú", "su", obl_pl)]
    mis, bhis = w("mís", "mis", obl_pl), w("bʰís", "bʰis", obl_pl)
    out["INS.PL"] = [bhis, mis] if hb else [mis, bhis]
    if hb and obl_pl is not weak:     # the full-grade weak stem stays as an alternative (HHḱéwbʰis)
        for k, e in (("DAT.PL", ("bʰós", "bʰos")), ("ABL.PL", ("bʰós", "bʰos")), ("LOC.PL", ("sú", "su")),
                     ("INS.PL", ("bʰís", "bʰis"))):
            out[k] = _uniq(out[k] + [w(*e)])
    return out


def _restore_mn(strong: list[Seg], weak: list[Seg]) -> list[Seg]:
    """sh₂imón / sh₂in̥ → sh₂imn̥: a -mon-/-men- stem whose weak stem ends in a short vowel (or syllabic
    i/u) + n̥ with the m missing gets the m back (see _athematic). Anything else is returned unchanged."""
    if (len(strong) >= 3 and strong[-1].base == "n" and not strong[-1].syl and strong[-2].kind == "V"
            and strong[-3].base == "m" and len(weak) >= 2 and weak[-1].base == "n" and weak[-1].syl
            and not weak[-2].long and (weak[-2].kind == "V" or (weak[-2].syl and weak[-2].base in ("y", "w")))):
        return weak[:-1] + [Seg("m", "R"), weak[-1]]
    return weak


def _zero_grade_men(weak: list[Seg]) -> list[Seg]:
    """Weak stem -mén- → accented syllabic -mń̥- (ḱlumén- → ḱlumń̥-); unchanged otherwise."""
    if len(weak) >= 3 and weak[-1].base == "n" and weak[-1].kind == "R" and not weak[-1].syl \
            and weak[-2].base == "e" and weak[-2].acc and weak[-3].base == "m" and not weak[-3].syl:
        return weak[:-2] + [Seg("n", "R", syl=True, acc=True)]
    return weak


def _zero_grade_iu(weak: list[Seg]) -> list[Seg]:
    """Weak stem -éw-/-éy-/-ów-/-óy- → accented syllabic -ú-/-í- (suHnów- → suHnú-, HHḱéw- → HHḱú-);
    unchanged otherwise (acrostatic h₂éwi-)."""
    if len(weak) >= 2 and weak[-1].kind == "R" and weak[-1].base in ("y", "w") and not weak[-1].syl \
            and weak[-2].base in ("e", "o") and weak[-2].acc:
        return weak[:-2] + [Seg(weak[-1].base, "R", syl=True, acc=True)]
    return weak


def _initial_accent(segs: list[Seg]) -> list[Seg]:
    out = [replace(x, acc=False) for x in segs]
    # a syllabic laryngeal as the first nucleus (ph₂ter: Ved. pítar, Gk πάτερ) carries the accent,
    # which the notation cannot mark: leave the form unaccented rather than accent a later vowel
    first_v = next((i for i, x in enumerate(out) if x.kind == "V" or (x.kind == "R" and x.syl)), None)
    # (a laryngeal right before the first vowel is consonantal: ǵʰh₂éns → voc. ǵʰh₂éns; s-root-heteroclite.md F9)
    if first_v is not None and any(x.base in ("h1", "h2", "h3", "H") and 0 < i < first_v - 1 and out[i - 1].kind == "C"
                                   for i, x in enumerate(out[:first_v])):
        return out
    for i, x in enumerate(out):
        if x.kind == "V" or (x.kind == "R" and x.syl):
            out[i] = replace(x, acc=True)
            break
    return out


def _locative(spec: NounSpec, strong: list[Seg], weak: list[Seg], hb: bool = True) -> list[str]:
    if len(spec.loc_sg) > 1:
        return [render(_p(_bare(x))) for x in spec.loc_sg]
    if spec.loc_sg:
        stems = [_p(_bare(spec.loc_sg[0]))]
    elif spec.devi or (spec.weak and spec.accent_class in ("acrostatic", "proterokinetic")):
        stems = [weak]
    elif spec.gender == "n" and spec.weak and strong[-1].base == "s" and strong[-2].base == "o":
        stems = [weak]   # s-stem neuter: e-grade suffix (léwkos → léwkes, léwkesi)
    else:
        # The locative wants the accented full grade: prefer the stem with an
        # accented true vowel (suHnú- → suHnów-), then any accented stem (múHs).
        def score(st):
            return 2 if any(x.acc and x.kind == "V" for x in st) else 1 if has_accent(st) else 0
        stems = [weak] if spec.weak and score(weak) > score(strong) else [strong]
    out = []
    for s in stems:
        if not has_accent(s) and (has_accent(strong) or has_accent(weak)):
            # an unaccented locative stem (mobile weak stem, zero-grade h₃sth₁-) takes the accented ending,
            # as in Ved. pad-í, Gk ποδί (Fortson §6.11): never an accentless form (s-root-heteroclite.md F8)
            out.append(render(_add(s, "í")))
            continue
        out.append(render(s))
        if s[-1].kind == "R" and s[-1].syl and s[-1].base == "y":
            if not hb:
                continue                               # Wiktionary: bare -i (h₂éwi)
            # i-stem: *-ēy (Fortson, Ringe; Ved. agnā́, Gk πόληι), then -ey; bare -i stays as an alternative
            full = s[:-1] + [Seg("e", "V"), Seg("y", "R")]
            out[-1:] = [render(lengthen_last_vowel(s[:-1] + [Seg("e", "V")]) + [Seg("y", "R")]), render(full),
                        render(s)]
            continue
        if len(s) >= 2 and s[-1].base == "y" and not s[-1].syl and s[-2].base == "e" and s[-2].acc:
            out.append(render(lengthen_last_vowel(s)))  # -éy → -ḗy (bʰr̥tḗy)
        else:
            out.append(render(_add(s, "i")))
            if hb and strong[-1].syl and strong[-1].base == "w" and len(s) >= 2 and s[-1].base == "w" \
                    and not s[-1].syl and s[-2].base == "e" and s[-2].acc:
                # u-stem endingless locative in the lengthened grade *-ēw (Beekes §13.2.6a; Ved. sūnáu, Goth.
                # sunau) as an alternative; Ringe's -éw(i) stay primary (engine sweep convention, i-u-stems.md #2)
                out.append(render(lengthen_last_vowel(s)))
    return _uniq(out)


def decline(spec: NounSpec, convention: str = "handbook", alternatives: bool = True) -> Cells:
    """All case × number cells for a nominal stem."""
    assert convention in CONVENTIONS

    def run(conv: str) -> Cells:
        k = spec.kind
        c = _thematic(spec, conv) if k == "thematic" else _eh2(spec, conv) if k == "eh2" else _athematic(spec, conv)
        if conv == "handbook" and spec.gender != "n":
            # the vocative plural retracts the accent like the singular (Fortson §6.52: Ved. voc. pl. dévās vs nom.
            # devā́s); the dual likewise (an extrapolation: Fortson states it for the plural). The unretracted
            # nominative form stays as the alternative (engine sweep convention, thematic.md defect 2)
            for feat in ("VOC.PL", "VOC.DU"):
                if c.get(feat) and has_accent(_p(c[feat][0])):
                    rd = _render_kw if k in ("thematic", "eh2") else render     # keep the boukólos choice
                    ret = _initial_accent(_p(c[feat][0]))
                    c[feat] = _uniq([rd(ret)] + c[feat] + [render(ret)])
        return c

    out = run(convention)
    if alternatives:
        out = _merge(out, run("handbook" if convention == "wiktionary" else "wiktionary"))
    return {k: _uniq(v) for k, v in out.items()}


@dataclass
class AdjSpec:
    """Adjective: Wiktionary ine-decl-adj args. 1 arg = thematic o/eh₂;
    4 args = athematic m/n (1, 2) + ih₂/yeh₂ feminine (3, 4)."""
    m_strong: str
    m_weak: str | None = None
    f_strong: str | None = None
    f_weak: str | None = None
    accent_class: str | None = None
    loc_sg: list[str] = field(default_factory=list)

    def genders(self) -> dict[str, NounSpec]:
        if self.m_weak is None:
            o = _bare(self.m_strong)
            fem = o[:-1] + ("é" if o.endswith("ó") else "e") + "h₂"
            return {"m": NounSpec(o, gender="m"), "f": NounSpec(fem, gender="f"), "n": NounSpec(o, gender="n")}
        return {
            "m": NounSpec(self.m_strong, self.m_weak, self.accent_class, "m", loc_sg=self.loc_sg, adjective=True),
            "f": NounSpec(self.f_strong or self.m_strong, self.f_weak, self.accent_class, "f", devi=True,
                          adjective=True),
            "n": NounSpec(self.m_strong, self.m_weak, self.accent_class, "n", loc_sg=self.loc_sg, adjective=True),
        }


def decline_adj(spec: AdjSpec, convention: str = "handbook", alternatives: bool = True) -> dict[str, Cells]:
    return {g: decline(s, convention, alternatives) for g, s in spec.genders().items()}


# =============================================================================
# Verbal
# =============================================================================

@dataclass
class VerbSpec:
    """A verbal stem. kind: impf (present) | pf (aorist) | stat (perfect).
    One thematic stem ending in -e (bʰére), or strong + weak athematic stems."""
    strong: str
    weak: str | None = None
    kind: str = "impf"
    mid_t_less: bool = False   # handbook: middle 3sg *-o(r), 3pl *-ro(r) first (*ḱéy-or 'lies': Fortson §5.16, L&Y §4.3.1)

    @property
    def thematic(self) -> bool:
        return self.weak is None and _bare(self.strong)[-1:] in ("e", "é")


_TH_PRS = ["oh₂", "esi", "eti", "owos", "etes", "etes", "omos", "ete", "onti"]
_TH_PST = ["om", "es", "et", "owe", "etom", "etām", "ome", "ete", "ont"]
_TH_IMP = {"2SG": "e", "3SG": "etu", "2DU": "etom", "3DU": "etām", "2PL": "ete", "3PL": "ontu"}

_ATH_PRS = ["mi", "si", "ti", "wós", "tés", "tés", "mós", "té", "énti"]
_ATH_PST = ["m", "s", "t", "wé", "tóm", "tā́m", "mé", "té", "ént"]
_PRF = ["h₂e", "th₂e", "e", "wé", None, None, "mé", "é", "ḗr"]
_ATH_IMP = {"3SG": "tu", "2DU": "tóm", "3DU": "tā́m", "2PL": "té", "3PL": "éntu"}


def _voiced_secondary(out: Cells, conv: str) -> Cells:
    """Handbook convention: the secondary 3sg/3pl endings are also written with
    final -d (*-ed*, *-ond*: Byrd 2013; word-final voicing of *-t*)."""
    if conv != "handbook":
        return out
    for k, forms in out.items():
        if k.startswith(("PST.3", "AOR.3")):
            out[k] = forms + [f[:-1] + "d" for f in forms if f.endswith("t")]
    return out


def conjugate(spec: VerbSpec, convention: str = "handbook", alternatives: bool = True,
              phase_b: bool = True) -> Cells:
    """Active indicative and imperative (Phase A), plus middle, subjunctive,
    optative and participles (Phase B) unless phase_b=False.
    Feature names: PRS.3SG, MID.PRS.3SG, SBJV.3SG, MID.OPT.1PL, PTCP.ACT, ..."""
    assert convention in CONVENTIONS

    def run(conv):
        cells = _conjugate(spec, conv)
        if phase_b:
            cells.update(_phase_b(spec, conv))
        return cells

    out = run(convention)
    if convention == "handbook":
        out = _handbook_verbal(spec, out)
    if alternatives:
        out = _merge(out, run("handbook" if convention == "wiktionary" else "wiktionary"))
    return out


def _handbook_verbal(spec: VerbSpec, out: Cells) -> Cells:
    """Handbook forms where Fortson and Beekes agree against the Wiktionary module
    (raw/books/extract/beekes-ly/diff.jsonl): middle 2pl *-dʰwe (no h₂; Fortson §5.16,
    Beekes p. 268), with -dʰh₂we kept as an alternative; and 2sg *h₁és-si beside the
    degeminated h₁ési (Fortson, Beekes p. 16). Lundquist & Yates (Handbook ch. 122) add:
    1pl -mes, middle 1pl -mesdʰh₂, thematic middle participle -omh₁nos."""
    out = dict(out)
    for k, forms in out.items():
        if k.startswith("MID.") and any("dʰh₂w" in f for f in forms):
            out[k] = _uniq([f.replace("dʰh₂w", "dʰw") for f in forms] + forms)
    # 1pl *-mes (o-grade -mos is Italic/Slavic; Lundquist & Yates §122, Beekes, Fortson), and
    # middle 1pl *-mesdʰh₂ (L&Y, Beekes): bʰéromes, h₁smés, bʰéromesdʰh₂
    for k, forms in out.items():
        if k.endswith(".1PL") and any(re.search("m[oó]s(dʰh₂)?$", f) for f in forms):
            new = [re.sub("m([oó])s(dʰh₂)?$", lambda m: "m" + ("é" if m[1] == "ó" else "e") + "s" + (m[2] or ""), f)
                   for f in forms]
            out[k] = _uniq(new + forms)
    # thematic middle participle *-omh₁nos (L&Y, Beekes; Fortson's *-mh₁no-)
    if spec.thematic and "PTCP.MID" in out:
        # (also after an accented thematic vowel: widómh₁nos; engine sweep, thematic-verbs.md defect 7)
        out["PTCP.MID"] = _uniq([re.sub("([oó])mnos$", r"\1mh₁nos", f) for f in out["PTCP.MID"]] + out["PTCP.MID"])
    # primary 2du *-tes = 3du (Ringe 2006 p. 31 prints *-tés for both; Fortson and L&Y give no distinct 2du);
    # Beekes §18.6 p. 271's tentative *-tHe/os ("perhaps *-th₁-", Ved. -thas) is kept as the alternative
    # *-th₁es (engine sweep convention, thematic-verbs.md defect 1 / athematic-verbs.md N1)
    for k in ("PRS.2DU", "SBJV.2DU"):
        if k in out:
            out[k] = _uniq(out[k] + [re.sub("t([eé])s$", lambda m: "th₁" + m[1] + "s", f) for f in out[k]])
    # *CCu-/CCi- before a vowel keeps the vowel with a glide (Sievers/Lindeman; LIV ḱluwónt-, not ḱl̥wónt-):
    # the junction rule would vocalize the liquid instead (ḱlu+ént → ḱl̥wént)
    # Only a true CC cluster counts: after a syllabic resonant (ḱl̥-nu-, tn̥-nu-, mi-nu-, tr̥h₂-u-) the stem ends in
    # VCu and takes the plain glide (L&Y §4.3.1 *ḱl̥-n-w-énti; Ringe 2006 p. 28 *tn̥-nw-; Ved. śr̥ṇvánti); a glide
    # before the cluster counts unless it is the same glide (dedwi- → dedwiyḗr, Gk δειδίασι; but not *-wu-, *-yi-).
    # The glided form replaces the form it rewrites in place, so a cell keeps its ranking (-tó before -ó);
    # the junction forms follow as alternatives. Engine sweep, athematic-verbs.md E1, thematic-verbs.md 2-3.
    wk = _p(_bare(spec.weak or ""))
    if (not spec.thematic and len(wk) > 2 and wk[-1].base in ("w", "y") and wk[-1].syl
            and not wk[-2].vocalic and not wk[-3].vocalic and wk[-2].base != wk[-1].base):
        bad = render(join(wk, _p("e")))[:-1]
        good = render(wk) + wk[-1].base
        if bad != good:
            for k, forms in out.items():
                if any(f.startswith(bad) for f in forms):
                    out[k] = _uniq([good + f[len(bad):] if f.startswith(bad) else f for f in forms] + forms)
    st = _p(_bare(spec.strong))
    if not spec.thematic and st and st[-1].base == "s" and st[-1].kind == "C" and "PRS.2SG" in out:
        out["PRS.2SG"] = _uniq(out["PRS.2SG"] + [render(st) + "si"])
    return out


# --- Phase B: middle, subjunctive, optative, participles --------------------
# Endings follow Wiktionary's conjugation module; the cross-check measures it.
# Each slot lists alternatives; None = no form.
_P = PERSONS
_TH_MID_PRS = ["oh₂er", "eth₂er", "etor", "owosdʰh₂", None, None, "omosdʰh₂", "edʰh₂we", "ontor"]
_TH_MID_PST = ["oh₂e", "eth₂e", "eto", "owedʰh₂", None, None, "omedʰh₂", "edʰh₂we", "onto"]
_TH_SBJV = ["ōh₂", "ēsi", "ēti", "ōwos", "ētes", "ētes", "ōmos", "ēte", "ōnti"]
_TH_MID_SBJV = ["ōh₂er", "ēth₂er", "ētor", "ōwosdʰh₂", None, None, "ōmosdʰh₂", "ēdʰh₂we", "ōntor"]
_TH_OPT = ["oyh₁m̥", "oys", "oyt", "oywe", "oytom", "oytām", "oyme", "oyte", "oyh₁n̥t"]
# handbook: *-oyh₁- in every person and 3pl *-oyh₁ent (Fortson §5.57, Beekes p. 275)
_TH_OPT_HB = ["oyh₁m̥", "oyh₁s", "oyh₁t", "oyh₁we", "oyh₁tom", "oyh₁tām", "oyh₁me", "oyh₁te", "oyh₁ent"]
_TH_MID_OPT = ["oyh₂e", "oyth₂e", ["oyto", "oyh₁o"], "oywedʰh₂", None, None, "oymedʰh₂", "oydʰh₂we", "oyro"]
# handbook: the optative suffix keeps *h₁ in the middle as in the active (*-oyh₁-; Fortson §5.57)
_TH_MID_OPT_HB = ["oyh₁h₂e", "oyh₁th₂e", "oyh₁to", "oyh₁wedʰh₂", None, None, "oyh₁medʰh₂", "oyh₁dʰwe", "oyh₁ro"]
# short-vowel subjunctive of athematic stems (strong stem + thematic vowel)
_SH_SBJV = ["oh₂", "esi", "eti", "owos", "etes", "etes", "omos", "ete", "onti"]
_SH_MID_SBJV = ["oh₂er", "eth₂er", "etor", "owosdʰh₂", None, None, "omosdʰh₂", "edʰh₂we", "ontor"]
_ATH_MID_PRS = ["h₂ér", "th₂ér", ["tór", "ór"], "wósdʰh₂", None, None, "mósdʰh₂", "dʰh₂wé", ["n̥tór", "rór"]]
_ATH_MID_PST = ["h₂é", "th₂é", ["tó", "ó"], "wédʰh₂", None, None, "médʰh₂", "dʰh₂wé", ["n̥tó", "ró"]]
_ATH_OPT_SG = ["yéh₁m̥", "yéh₁s", "yéh₁t"]
_ATH_OPT_PL = ["ih₁wé", "ih₁tóm", "ih₁tā́m", "ih₁mé", "ih₁té", "ih₁ént"]
_ATH_MID_OPT = ["ih₁h₂é", "ih₁th₂é", ["ih₁tó", "ih₁ó"], "ih₁wédʰh₂", None, None, "ih₁médʰh₂", "ih₁dʰh₂wé", "ih₁ró"]


def _slots(prefix: str, table, make) -> Cells:
    out: Cells = {}
    for pn, e in zip(_P, table):
        if e is None:
            continue
        out[f"{prefix}.{pn}"] = [make(x) for x in (e if isinstance(e, list) else [e])]
    return out


def _phase_b(spec: VerbSpec, conv: str) -> Cells:
    wk = conv == "wiktionary"
    fix = pinault if wk else (lambda x: x)
    out: Cells = {}
    tense = {"impf": "PRS", "pf": "AOR", "stat": "PRF"}[spec.kind]
    if spec.thematic:
        stem = fix(_p(_bare(spec.strong)))
        base, tv_acc = stem[:-1], stem[-1].acc

        def th(e: str) -> str:
            es = _p(e)
            if tv_acc:
                es = [replace(es[0], acc=True)] + es[1:]
            return render(fix(base + es))

        if spec.kind == "impf":
            out.update(_slots("MID.PRS", _TH_MID_PRS, th))
        out.update(_slots("MID.PST" if spec.kind == "impf" else f"MID.{tense}", _TH_MID_PST, th))
        out["MID.IMP.2SG"] = [th("eso")] + ([th("eswo")] if conv == "handbook" else [])   # -eswo: Byrd 2013
        out["MID.IMP.2PL"] = [th("edʰh₂we")]
        if conv == "handbook":
            out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = [th("etōd")]   # future imperative -tōd (Byrd ǵn̥h₁yetōd)
        out.update(_slots("SBJV", _TH_SBJV, th))
        out.update(_slots("MID.SBJV", _TH_MID_SBJV, th))
        out.update(_slots("OPT", _TH_OPT if wk else _TH_OPT_HB, th))
        out.update(_slots("MID.OPT", _TH_MID_OPT if wk else _TH_MID_OPT_HB, th))
        out["PTCP.ACT"] = [th("onts")]
        out["PTCP.MID"] = [th("omnos")]
        return out

    strong = fix(_p(_bare(spec.strong)))
    weak = fix(_p(_bare(spec.weak or spec.strong)))
    hb = conv == "handbook"
    red = _redup_weak_accented(strong, weak) if (hb and spec.kind == "impf") else None

    def on(stem, e: str) -> str:
        # accented stem: participle -n̥ts (h₁édn̥ts); optative 3pl -n̥t only in the Wiktionary module (handbook:
        # always *-ent, Fortson §5.57; engine sweep, thematic-verbs.md defect 4)
        if has_accent(stem) and (e == "ónts" or (e == "ih₁ént" and wk)):
            e = {"ih₁ént": "ih₁n̥t", "ónts": "n̥ts"}[e]
        return render(fix(join(stem, _p(e))))

    # subjunctive stem: the strong stem, e-grade in the perfect (wóyd- → wéyd-); a Narten / s-aorist stem
    # (ḗ in the singular, accented é elsewhere) takes the e-grade, i.e. the weak stem: the lengthened grade is
    # indicative-only (Ringe 2006 p. 30 *h₁éd-e/o- to *h₁ḗd-, *déyḱ-s-e/o- to *dḗyḱ-s-; Fortson §5.55;
    # Beekes §18.3.1c). Engine sweep, athematic-verbs.md E3, thematic-verbs.md defect 5.
    sbjv = [replace(x, base="e") if (spec.kind == "stat" and x.kind == "V" and x.base == "o" and x.acc) else x
            for x in strong]
    if hb and has_accent(weak) and any(x.long and x.acc and x.kind == "V" for x in strong):
        sbjv = weak
    out.update(_slots("SBJV", _SH_SBJV, lambda e: on(sbjv, e)))
    # optative: *-yéh₁-/-ih₁- on the weak stem; when the weak stem is accented (Narten, fixed-accent stems,
    # s-aorist) or the stem is reduplicated, the suffix is zero-grade throughout (Fortson §5.57; Ringe 2006
    # p. 30 *h₁éd-ih₁-, *dʰé-dʰh₁-ih₁-; Beekes §18.8.4 *dʰe-dʰh₁-ih₁-t); the full-grade forms stay as
    # alternatives (engine sweep, athematic-verbs.md E2, thematic-verbs.md defect 6)
    zero_opt = hb and spec.kind != "stat" and (has_accent(weak) or red is not None)
    opt_sg = ["ih₁m̥", "ih₁s", "ih₁t"] if zero_opt else _ATH_OPT_SG
    out.update(_slots("OPT", [*opt_sg, *_ATH_OPT_PL], lambda e: on(weak, e)))
    if zero_opt:
        for pn, e in zip(_P[:3], _ATH_OPT_SG):
            out[f"OPT.{pn}"] = _uniq(out[f"OPT.{pn}"] + [on(weak, e)])
    if spec.kind == "stat":
        out["PTCP.ACT"] = [on(weak, "wṓs")]
        return out
    if spec.kind == "impf":
        out.update(_slots("MID.PRS", _ATH_MID_PRS, lambda e: on(weak, e)))
    out.update(_slots("MID.PST" if spec.kind == "impf" else "MID.AOR", _ATH_MID_PST, lambda e: on(weak, e)))
    if red is not None:
        # reduplicated present, middle 3pl: accent on the reduplication, *-n̥to(r) (Ved. dádhate, dádhata)
        for k, e in (("MID.PRS.3PL", "n̥tór"), ("MID.PST.3PL", "n̥tó")):
            if k in out:
                out[k] = _uniq([on(red, e)] + out[k])
    if hb and spec.mid_t_less:
        # t-less middle 3sg/3pl first (*ḱéy-or, 3pl *-ror: Fortson §5.16, §5.18; L&Y §4.2, §4.3.1; Beekes §18.7),
        # the -t- forms as alternatives (engine sweep, athematic-verbs.md D5)
        for k in ("MID.PRS.3SG", "MID.PST.3SG", "MID.AOR.3SG", "MID.PRS.3PL", "MID.PST.3PL", "MID.AOR.3PL"):
            if k in out and len(out[k]) > 1:
                out[k] = out[k][1:] + out[k][:1]   # [-tór, -ór] → [-ór, -tór]; [-n̥tór, -rór] → [-rór, -n̥tór]
    if hb:
        # *-tṓd on the zero-grade stem, accented (zero grade: Fortson §5.54 Ved. dhattā́t; accent: Ringe 2006
        # p. 31 *-tṓd, Beekes §18.8.5 Ved. itā́t); the strong-stem form stays as an alternative (athematic E5)
        out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = _uniq([on(weak, "tṓd"), on(strong, "tōd")])
    out["MID.IMP.2SG"] = [on(weak, "só")]
    out["MID.IMP.2PL"] = [on(weak, "dʰh₂wé")]
    out.update(_slots("MID.SBJV", _SH_MID_SBJV, lambda e: on(sbjv, e)))
    out.update(_slots("MID.OPT", _ATH_MID_OPT, lambda e: on(weak, e)))
    out["PTCP.ACT"] = [on(weak, "ónts")] + ([on(red, "n̥ts")] if red is not None else [])   # Ved. dádhat-
    out["PTCP.MID"] = [on(weak, "m̥h₁nós")]
    return out


def _redup_weak_accented(strong: list[Seg], weak: list[Seg]) -> list[Seg] | None:
    """Athematic reduplicated present with an unaccented weak stem (dʰédʰeh₁- / dʰedʰh₁-): the weak stem
    with the accent on the reduplication vowel (dʰédʰh₁-), which the 3pl takes before *-n̥ti (Fortson §5.27
    *de-dh₃-n̥ti; Beekes §18.1.3, §18.2.3 *dʰé-dʰh₁-n̥ti, *bʰé-bʰr̥-n̥ti; Ved. dádhati). None otherwise."""
    if has_accent(weak) or len(strong) < 4 or len(weak) < 3:
        return None
    for n in (1, 2):   # Ce-, and sCe-/HCe- (Beekes §18.1.3 *sti-st(e)h₂-)
        if len(strong) <= 2 * n + 1:
            continue
        v = strong[n]
        if not (v.acc and ((v.kind == "V" and v.base == "e") or (v.syl and v.base == "y"))):
            continue
        if all(x.kind != "V" and not x.syl for x in strong[:n]) \
                and [x.base for x in strong[:n]] == [x.base for x in strong[n + 1:2 * n + 1]] \
                and [x.base for x in weak[:n + 1]] == [x.base for x in strong[:n + 1]]:
            return weak[:n] + [replace(weak[n], acc=True)] + weak[n + 1:]
    return None


def _conjugate(spec: VerbSpec, conv: str) -> Cells:
    wk = conv == "wiktionary"
    fix = pinault if wk else (lambda x: x)
    out: Cells = {}
    if spec.thematic:
        stem = fix(_p(_bare(spec.strong)))
        base, tv_acc = stem[:-1], stem[-1].acc

        def th(e: str) -> str:
            es = _p(e)
            if tv_acc:
                es = [replace(es[0], acc=True)] + es[1:]
            return render(base + es)

        tense = {"impf": "PRS", "pf": "AOR", "stat": "PRF"}[spec.kind]
        if spec.kind == "impf":
            for pn, e in zip(PERSONS, _TH_PRS):
                out[f"PRS.{pn}"] = [th(e)]
        for pn, e in zip(PERSONS, _TH_PST):
            out[f"{'PST' if spec.kind == 'impf' else tense}.{pn}"] = [th(e)]
        for pn, e in _TH_IMP.items():
            out[f"IMP.{pn}"] = [th(e)]
        return _voiced_secondary(out, conv)

    strong = fix(_p(_bare(spec.strong)))
    weak = fix(_p(_bare(spec.weak or spec.strong)))
    weak_acc = has_accent(weak)
    # reduplicated present: the 3pl accents the reduplication and takes *-n̥ti (dʰédʰh₁n̥ti; athematic-verbs.md E4)
    red = _redup_weak_accented(strong, weak) if (not wk and spec.kind == "impf") else None

    def sg_or_pl(i: int, e: str) -> str:
        st = strong if i < 3 else weak
        if wk and spec.kind == "stat":
            st = junction_laryngeal_loss(st, _p(e))
        if weak_acc and e.startswith("én"):
            e = e[1:]   # accented stem: zero-grade 3pl -n̥t(i) (bʰúHn̥t)
        elif red is not None and e.startswith("én"):
            st, e = red, e[1:]
        if e == "m":
            # 1sg secondary is -m̥, syllabic even after a vowel (ném̥, h₁ésm̥, térh₂wm̥),
            # with contractions: -em-m̥ → -ḗm, -ey/-ew-m̥ → -ḗm (Stang), -eh₂-m̥ → -ām
            if st[-1].base == "m" and not st[-1].syl and st[-2].kind == "V":
                return render(lengthen_last_vowel(st))
            if st[-1].kind == "R" and st[-1].syl and not st[-1].acc and not st[-1].long:
                st = st[:-1] + [replace(st[-1], syl=False)]
            f = st + [Seg("m", "R", syl=True)]
            return render(stang(contract_eh2m(f)))
        return render(stang(contract_eh2m(_add(st, e))))

    if spec.kind == "stat":
        for i, (pn, e) in enumerate(zip(PERSONS, _PRF)):
            if e is not None:
                out[f"PRF.{pn}"] = [sg_or_pl(i, e)]
    else:
        if spec.kind == "impf":
            for i, (pn, e) in enumerate(zip(PERSONS, _ATH_PRS)):
                out[f"PRS.{pn}"] = [sg_or_pl(i, e)]
        tense = "PST" if spec.kind == "impf" else "AOR"
        for i, (pn, e) in enumerate(zip(PERSONS, _ATH_PST)):
            out[f"{tense}.{pn}"] = [sg_or_pl(i, e)]
    out["IMP.2SG"] = [render(strong), render(_add(weak, "dʰí"))]
    if conv == "handbook":   # zero grade + -dʰí is the usual athematic 2sg imperative (h₁sdʰí, ḱludʰí)
        out["IMP.2SG"].reverse()
    for pn, e in _ATH_IMP.items():
        st = strong if pn == "3SG" else weak
        if weak_acc and e.startswith("én"):
            e = e[1:]
        elif red is not None and e.startswith("én"):
            st, e = red, e[1:]
        if wk and spec.kind == "stat":
            st = junction_laryngeal_loss(st, _p(e))
        out[f"IMP.{pn}"] = [render(_add(st, e))]
    return _voiced_secondary(out, conv)


def decline_participle(nom: str, voice: str, gender: str, thematic: bool) -> Cells:
    """Case forms of a participle from its nominative (conjugate()'s PTCP.ACT / PTCP.MID).

    Active: nt-stems. Thematic (bʰéront-) has no ablaut and gen. -os (bʰérontos,
    Ved. bháratas); athematic ablauts (h₁sónt-/h₁sn̥t-, gen. h₁sn̥tés, Ved. satás).
    Feminine in -ih₂ (bʰérontih₂, h₁sn̥tíh₂). Middle: the -mh₁no- / -mno- adjective.
    The perfect participle (-wōs) is not supported: raises KeyError.
    """
    if voice == "MID" and nom.endswith("nos"):
        return decline_adj(AdjSpec(nom[:-1]), "handbook")[gender]
    if voice != "MID" and nom.endswith("n̥ts"):
        # an accented (Narten, fixed-accent) stem: non-ablauting *-n̥t- (h₁édn̥ts, Ved. adat-), gen. -os,
        # feminine -ih₂ (engine sweep: h₁ed- Narten)
        stem = nom[:-1]
        if gender == "f":
            return decline(NounSpec(stem + "ih₂", stem + "yeh₂", "proterokinetic", "f", devi=True), "handbook")
        c = decline(NounSpec(stem, stem, "acrostatic", gender), "handbook")
        return {**c, "GEN.SG": [stem + "os"], "ABL.SG": [stem + "os"]}
    if voice != "MID" and nom.endswith("nts"):
        from .classify import zero_grade
        stem = nom[:-1]
        weak = None if thematic else zero_grade(stem)
        if gender == "f":
            fs = weak or stem
            return decline(NounSpec(fs + ("íh₂" if weak else "ih₂"), fs + ("yéh₂" if weak else "yeh₂"),
                                    "proterokinetic", "f", devi=True), "handbook")
        c = decline(NounSpec(stem, weak, "proterokinetic" if weak else None, gender), "handbook")
        return {**c, "GEN.SG": [stem + "os"], "ABL.SG": [stem + "os"]} if thematic else c
    raise KeyError(f"no declinable {voice} participle for {nom!r}")
