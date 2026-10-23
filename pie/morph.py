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
        "NOM.SG": ["os"], "VOC.SG": ["e"], "ACC.SG": ["om"], "GEN.SG": ["osyo"], "ABL.SG": ["ōd"],
        "DAT.SG": ["ōy"], "LOC.SG": ["oy", "ey"], "INS.SG": ["oh₁"],
        "NOM.DU": ["oh₁"], "VOC.DU": ["oh₁"], "ACC.DU": ["oh₁"],
        "NOM.PL": ["ōs"], "VOC.PL": ["ōs"], "ACC.PL": ["oms"], "GEN.PL": ["ōm"],
        "ABL.PL": ["oybʰos", "omos"], "DAT.PL": ["oybʰos", "omos"], "LOC.PL": ["oysu"], "INS.PL": ["ōys"],
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
    return out


_EH2 = {
    "NOM.SG": [""], "VOC.SG": [""], "ACC.SG": ["m"], "GEN.SG": ["s"], "ABL.SG": ["s"],
    "DAT.SG": ["ey"], "LOC.SG": ["", "i"], "INS.SG": ["h₁"],
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
        out["GEN.PL"] = [render(_add(stem, "ōm"))]
        for k in ("ABL.PL", "DAT.PL", "INS.PL"):
            out[k] = out[k][::-1]
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
    obl = zero_grade_suffix(weak) if (spec.accent_class == "proterokinetic" and root_accented and not hb) else weak

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
        acc = stang(_add(strong, "m"))
        out["ACC.SG"] = [render(contract_eh2m(acc) if not hb else acc)]
    # --- singular, weak
    if not weak_acc:
        gen = [w("és", "")] + ([w("ós", "")] if hb else [])
    else:
        last = weak[-1]
        gen = [render(_add(weak, "os" if (last.base == "s" and last.kind == "C") else "s"))]
    out["GEN.SG"] = out["ABL.SG"] = gen
    out["DAT.SG"] = [w("éy", "ey")]
    out["INS.SG"] = [w("éh₁", "h₁", obl)]
    out["LOC.SG"] = _locative(spec, strong, weak)
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
        out["ACC.PL"] = [render(_add(strong, "ms"))]
    out["GEN.PL"] = ([w("ṓm", "ōm")] if hb else []) + [w("óHom", "oHom")]
    mos, bhos = w("mós", "mos", obl), w("bʰós", "bʰos", obl)
    out["DAT.PL"] = out["ABL.PL"] = [bhos, mos] if hb else [mos, bhos]
    out["LOC.PL"] = [w("sú", "su", obl)]
    mis, bhis = w("mís", "mis", obl), w("bʰís", "bʰis", obl)
    out["INS.PL"] = [bhis, mis] if hb else [mis, bhis]
    return out


def _locative(spec: NounSpec, strong: list[Seg], weak: list[Seg]) -> list[str]:
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
            continue                                   # i-stem: bare only (h₂éwi)
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


def conjugate(spec: VerbSpec, convention: str = "handbook", alternatives: bool = True) -> Cells:
    """Active indicative and imperative cells. Middle, subjunctive, optative
    and participles are Phase B."""
    assert convention in CONVENTIONS
    out = _conjugate(spec, convention)
    if alternatives:
        out = _merge(out, _conjugate(spec, "handbook" if convention == "wiktionary" else "wiktionary"))
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
        return out

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
    for pn, e in _ATH_IMP.items():
        if weak_acc and e.startswith("én"):
            e = e[1:]
        st = strong if pn == "3SG" else weak
        if wk and spec.kind == "stat":
            st = junction_laryngeal_loss(st, _p(e))
        out[f"IMP.{pn}"] = [render(_add(st, e))]
    return out
