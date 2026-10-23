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
  "handbook"   the contracted forms of Fortson/Ringe/Byrd (*-ōs*, *-ōy*,
               *-ōd*, gen. pl. *-ōm*), *-bʰ-* first, gen. sg. *-és* ~ *-ós*.
               Not yet verified against the books (docs/morphology.md).
With alternatives=True (the default), the other convention's forms follow
the primary ones, so nothing is lost.

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
    out = {}
    for feat, ends in table.items():
        forms = []
        for e in ends:
            es = _p(e)
            if tv_acc:  # accent on the thematic vowel stays on the vowel that replaces it
                es = [replace(es[0], acc=True)] + es[1:]
            forms.append(render(base + es))
        out[feat] = forms
    if conv == "handbook" and spec.gender != "n" and has_accent(stem):
        # vocative accent on the first syllable (Ved. vŕ̥ka, Gk ἄδελφε): wĺ̥kʷe, moysé → móyse
        out["VOC.SG"] = _uniq([render(_initial_accent(base + _p("e")))] + out["VOC.SG"])
    return out


_EH2 = {
    "NOM.SG": [""], "VOC.SG": [""], "ACC.SG": ["m"], "GEN.SG": ["s"], "ABL.SG": ["s"],
    "DAT.SG": ["ey"], "LOC.SG": ["i", ""], "INS.SG": ["h₁"],   # -eh₂i first: the endingless form = NOM
    "NOM.DU": ["h₁", "h₁e"], "VOC.DU": ["h₁", "h₁e"], "ACC.DU": ["h₁", "h₁e"],
    "NOM.PL": ["es"], "VOC.PL": ["es"], "ACC.PL": ["ms"], "GEN.PL": ["oHom"],
    "ABL.PL": ["mos", "bʰos"], "DAT.PL": ["mos", "bʰos"], "LOC.PL": ["su"], "INS.PL": ["mis", "bʰis"],
}


def _eh2(spec: NounSpec, conv: str) -> Cells:
    stem = _p(_bare(spec.strong))
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
        # vocative with initial accent (Ved. ámba, Gk νύμφα), as in the other declensions
        out["VOC.SG"] = _uniq([render(_initial_accent(stem))] + out["VOC.SG"])
        # gen. sg. *-eh₂es beside -eh₂s (Beekes, Lundquist & Yates)
        out["GEN.SG"] = _uniq(out["GEN.SG"] + [render(_add(stem, "es"))])
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
        # The m-less Wiktionary forms follow as alternatives.
        weak = _restore_mn(strong, weak)
    obl = zero_grade_suffix(weak) if (spec.accent_class == "proterokinetic" and root_accented and not hb) else weak
    # Handbook: i/u-stems with an accented full-grade suffix in the weak stem (-éw-/-éy-/-ów-) take the
    # zero-grade suffix, accented, before the consonant-initial oblique plural endings: Ringe 2006 §2.3.4–5
    # (mn̥tíbʰi, ǵustúbʰi, ǵustúmos, ǵustúsu; tn̥h₂úbʰi, tn̥h₂úsu), Beekes §13.2.6a (*-u-bʰi, *-u-su);
    # Ved. sūnúbhis, agníbhis, pṛthúbhis, urúbhis. The acrostatic type keeps its root accent (h₂éwibʰi).
    # Only true i/u-stems (strong stem in syllabic -i/-u), not diphthongal root nouns (gʷṓws: Ved. góbhis).
    iu_stem = bool(strong) and strong[-1].kind == "R" and strong[-1].syl and strong[-1].base in ("y", "w")
    obl_pl = _zero_grade_iu(weak) if (hb and iu_stem) else obl

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
        acc = stang(_add(strong, "m"))
        out["ACC.SG"] = [render(contract_eh2m(acc) if not hb else acc)]
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
    out["LOC.SG"] = _locative(spec, strong, weak, hb)
    if hb:   # prefer the -i (or i-stem -ēy) locative to the endingless one (which looks like the nominative)
        out["LOC.SG"] = sorted(out["LOC.SG"], key=lambda f: not f.endswith(("i", "í", "y")))
    # --- dual
    if neuter:
        # s-stem neuters take the e-grade (weak) suffix: déḱos → déḱesih₁; others the strong stem
        e_grade_s = len(weak) > 1 and weak[-1].base == "s" and weak[-2].base == "e"
        du = [render(_add(weak if (e_grade_s and spec.weak) else strong, "ih₁"))]
    else:
        du = [render(_add(strong, "h₁")), render(_add(strong, "h₁e"))]
    out["NOM.DU"] = out["VOC.DU"] = out["ACC.DU"] = du
    # --- plural
    if neuter:
        if len(strong) > 1 and strong[-1].base in ("s", "n", "r") and not strong[-1].syl and strong[-2].kind == "V":
            # collective: -os-h₂ → -ōs, -or-h₂ → -ōr, -on-h₂ → -ō
            coll = lengthen_last_vowel(strong if strong[-1].base == "s" else strong[:-1])
            npl = [render(coll)]
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
    if first_v is not None and any(x.base in ("h1", "h2", "h3", "H") and 0 < i < first_v and out[i - 1].kind == "C"
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
    return _uniq(out)


def decline(spec: NounSpec, convention: str = "handbook", alternatives: bool = True) -> Cells:
    """All case × number cells for a nominal stem."""
    assert convention in CONVENTIONS

    def run(conv: str) -> Cells:
        k = spec.kind
        return _thematic(spec, conv) if k == "thematic" else _eh2(spec, conv) if k == "eh2" else _athematic(spec, conv)

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
        out["PTCP.MID"] = _uniq([f.replace("omnos", "omh₁nos") for f in out["PTCP.MID"]] + out["PTCP.MID"])
    # primary 2du *-th₁es, distinct from 3du *-tes (Ved. -thas vs -tas; Ringe)
    for k in ("PRS.2DU", "SBJV.2DU"):
        if k in out:
            out[k] = _uniq([re.sub("t([eé])s$", lambda m: "th₁" + m[1] + "s", f) for f in out[k]] + out[k])
    # *CCu-/CCi- before a vowel keeps the vowel with a glide (Sievers/Lindeman; LIV ḱluwónt-, not ḱl̥wónt-):
    # the junction rule would vocalize the liquid instead (ḱlu+ént → ḱl̥wént)
    wk = _p(_bare(spec.weak or ""))
    if (not spec.thematic and len(wk) > 2 and wk[-1].base in ("w", "y") and wk[-1].syl
            and wk[-2].kind != "V" and wk[-3].kind != "V" and wk[-2].base not in ("w", "y")):
        bad = render(join(wk, _p("e")))[:-1]
        good = render(wk) + wk[-1].base
        if bad != good:
            for k, forms in out.items():
                new = [good + f[len(bad):] for f in forms if f.startswith(bad)]
                if new:
                    out[k] = _uniq(new + forms)
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

    def on(stem, e: str) -> str:
        if has_accent(stem) and e in ("ih₁ént", "ónts"):
            e = {"ih₁ént": "ih₁n̥t", "ónts": "n̥ts"}[e]   # accented stem: zero-grade -n̥t (bʰúHih₁n̥t, h₁édn̥ts)
        return render(fix(join(stem, _p(e))))

    # subjunctive stem: the strong stem, e-grade in the perfect (wóyd- → wéyd-)
    sbjv = [replace(x, base="e") if (spec.kind == "stat" and x.kind == "V" and x.base == "o" and x.acc) else x
            for x in strong]
    out.update(_slots("SBJV", _SH_SBJV, lambda e: on(sbjv, e)))
    out.update({k: v for k, v in _slots("OPT", [*_ATH_OPT_SG, *_ATH_OPT_PL], lambda e: on(weak, e)).items()})
    if spec.kind == "stat":
        out["PTCP.ACT"] = [on(weak, "wṓs")]
        return out
    if spec.kind == "impf":
        out.update(_slots("MID.PRS", _ATH_MID_PRS, lambda e: on(weak, e)))
    out.update(_slots("MID.PST" if spec.kind == "impf" else "MID.AOR", _ATH_MID_PST, lambda e: on(weak, e)))
    if conv == "handbook":
        out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = [on(strong, "tōd")]
    out["MID.IMP.2SG"] = [on(weak, "só")]
    out["MID.IMP.2PL"] = [on(weak, "dʰh₂wé")]
    out.update(_slots("MID.SBJV", _SH_MID_SBJV, lambda e: on(sbjv, e)))
    out.update(_slots("MID.OPT", _ATH_MID_OPT, lambda e: on(weak, e)))
    out["PTCP.ACT"] = [on(weak, "ónts")]
    out["PTCP.MID"] = [on(weak, "m̥h₁nós")]
    return out


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

    def sg_or_pl(i: int, e: str) -> str:
        st = strong if i < 3 else weak
        if wk and spec.kind == "stat":
            st = junction_laryngeal_loss(st, _p(e))
        if weak_acc and e.startswith("én"):
            e = e[1:]   # accented stem: zero-grade 3pl -n̥t(i) (bʰúHn̥t)
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
        if weak_acc and e.startswith("én"):
            e = e[1:]
        st = strong if pn == "3SG" else weak
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
