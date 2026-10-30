"""Degrees of comparison: the primary comparative *-yos-/*-is- and the superlative *-isto-, built on the root.

The decisions, their sources and the rejected alternatives are in docs/morphology-comparison-and-comitative.md;
the planner-facing schema is in pie/realize.py's docstring ("degree"). This module holds the machinery, shared by
the realizer (pie.realize), the validator (pie.validate.index_plan_degrees) and the backtest
(data/morph/degree_backtest.json, tests/test_degree.py), so a degree form is generated and recognized by one
function, as with compounds (pie.compound).

  base(lex_id, lx) → Base         the accented full-grade root the suffix is added to, or DegreeError
  cells(lex_id, degree, gender, lx) → Cells

The base (Fortson §6.78 'added to the full grade of the root'; Beekes §14.4 'added to the root, not to the stem';
Handbook ch. 122 (Lundquist & Yates) 'directly to the adjectival root'; Ringe 2006 §2.4.2(iii) 'part of the Caland system'):
the adjective's headword minus its ending and its primary suffix (-u-, -ro-, -mo-, simple thematic -o-, or none
for a root adjective like méǵh₂s), accented on the root nucleus (Vedic root accent, Greek recessive: Handbook
ch. 122). A root left in the zero or o-grade by the adjective (h₂r̥ǵrós, polh₁ús) takes the e-grade of the lexicon
root it is linked to (root_id), and only when the two have the same consonants; otherwise the full grade is not
known and the adjective is rejected. Adjectives that are not primary (Caland-type) adjectives take no primary
degree: -tó-/-nó- verbal adjectives, -yo-/-wo- relational and possessive derivatives, -tero-, compounds,
participles, o-grade deverbal thematic adjectives, and lexemes that are already comparatives or superlatives
(Handbook ch. 122: relational adjectives are not gradable; Handbook ch. 111 (Indo-Iranian): the primary suffixes
'could only be used for primary adjectives').

Comparative (m./f. = common gender, Beekes §14.4 and Gk -ίων, Lat. -ior; amphikinetic suffix, Fortson §6.78):
  strong cases root-accented R-yos- (Fortson; Handbook ch. 122 Gk *swā́d-(i)yos-m̥; Ved. -yāṃs-): nom. *R-yōs,
  voc. *R-yos, acc. *R-yosm̥, nom. pl. *R-yoses, acc. pl. *R-yosn̥s, nom.-acc. du. *R-yosh₁e (Myc. me-zo-e);
  weak cases the zero-grade suffix *-is- with the ending accented (Fortson weak *-is-; Beekes gen. *-is-ós; Ringe
  *-is-´): gen. *R°-isés (-ós), dat. *R°-iséy, ins. *R°-iséh₁, obl. pl. *R°-isbʰós …; loc. *R-yosi (Ved., Handbook
  ch. 111 PII *u̯ási̯as-i). Alternatives kept in the cells: Sievers' *-iyos- (Handbook ch. 122), Beekes's
  suffix-accented acc. *-yésm̥, the generalized strong stem of the weak cases (Ved. vásyasas, Gk -ονος),
  Wiktionary's root-accented weak stem *R-is-, the amphikinetic loc. *-yés(i).
  Neuter: *R-yos (Beekes; Lat. maius, Ved. vásyas), the older *R-is (Beekes: Lat. magis) as an alternative;
  nom.-acc. pl. *R-yosh₂ (Lat. maiōra, Gk -ω < *-oha), collective *R-yōs alternative.
Superlative: thematic *R-isto- (-os, -eh₂, -om) with root accent (Fortson §6.81, Beekes §14.4, Mallory & Adams,
  Handbook ch. 122: Ved. svā́diṣṭha-, Gk ἥδιστος, Goth. -ista); *R-isth₂o- (Ved. -iṣṭha-, Handbook ch. 27, the
  lexicon's Wiktionary headwords) as the alternative.
Status (flagged on every token, Word.degree_status): the comparative is absent from Anatolian and Tocharian
  (Fortson §9.4; Handbook ch. 122), an elative of 'West IE at the latest' (Ringe): "nuclear-IE". The superlative was
  built on it later (Ringe: *-is-to- in most daughters, *-is-m̥mo- in Italic and Celtic; Fortson §6.80: PIE need not
  have marked a superlative at all): "late-IE".
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .morph import AdjSpec, Cells, NounSpec, _bare, _uniq, decline, decline_adj
from .phon import Seg, deaccent, parse, render

DEGREES = ("CMP", "SUP")
STATUS = {"CMP": "nuclear-IE", "SUP": "late-IE"}
GLOSS = {"CMP": "CMP", "SUP": "SUP"}


class DegreeError(ValueError):
    """A degree the engine cannot build; the message is for the planner."""


@dataclass(frozen=True)
class Base:
    root: str      # accented full-grade root: swéh₂d, méǵh₂, pléh₁
    method: str    # "stem" (the adjective's own full-grade root) | "root" (the linked root's e-grade)
    suffix: str    # the primary suffix removed: "u", "ro", "mo", "o", "", "H" (méǵ-h₂-)
    alts: tuple = ()  # other bases whose forms the cells keep as alternatives (méǵh₂-)


def degree_id(degree: str, lex_id: str) -> str:
    return f"degree:{degree}:{lex_id}"


def parse_id(lex_id: str) -> tuple[str, str] | None:
    """(degree, base lex_id) of a realized degree token's lex_id, or None."""
    if not lex_id.startswith("degree:"):
        return None
    _, d, lid = lex_id.split(":", 2)
    return d, lid


# headword endings that mark an adjective as not primary: (ending, reason)
_NOT_PRIMARY = (
    ("isth₂os", "is already a superlative"), ("istos", "is already a superlative"),
    ("yōs", "is already a comparative"), ("ēs", "is an s-stem compound adjective"),
    ("teros", "is a -tero- (contrastive) adjective, not a gradable primary one (Fortson §6.79)"),
    ("tós", "is a -tó- verbal adjective"), ("tos", "is a -to- verbal adjective"),
    ("yós", "is a -yo- relational adjective (Handbook ch. 122: not gradable)"),
    ("yos", "is a -yo- relational adjective (Handbook ch. 122: not gradable)"),
    ("wós", "is a -wo- derivative"), ("wos", "is a -wo- derivative"),
    ("onts", "is a participle"), ("nts", "is a participle"), ("ōr", "is a compound"),
)
# the primary (Caland-type) adjective suffixes removed to reach the root (Beekes §14.4 and p. 181: -ro-, -u-, -mo-)
_SUFFIXES = (("ús", "u"), ("us", "u"), ("rós", "ro"), ("ros", "ro"), ("mós", "mo"), ("mos", "mo"),
             ("ós", "o"), ("os", "o"))
_DELAB = {"kw": "k", "gw": "g", "gwh": "gh"}


def _nuclei(segs: list[Seg]) -> list[int]:
    return [i for i, x in enumerate(segs) if x.vocalic]


def _skeleton(segs: list[Seg], delabialize: bool = False) -> tuple:
    """The non-vowel segments in order, a syllabic resonant counted as its consonant (r̥ = r): what ablaut leaves
    unchanged (h₂r̥ǵ ~ h₂erǵ; polh₁ ~ pleh₁ have the same segments, in a different order: compared as a multiset)."""
    return tuple(sorted(_DELAB.get(x.base, x.base) if delabialize else x.base for x in segs if x.kind != "V"))


def _accent_root(segs: list[Seg], i: int) -> str:
    out = deaccent(segs)
    out[i] = replace(out[i], acc=True)
    return render(out)


def _stem(lex_id: str, form: str) -> tuple[str, str]:
    """(root stem, suffix removed) of a primary adjective's headword, or DegreeError."""
    for end, why in _NOT_PRIMARY:
        if form.endswith(end):
            if end[0] in "ywt" and end not in ("teros",):
                pre = parse(form[: -len(end)])
                if not pre or pre[-1].kind == "V":
                    continue                                 # néw-os, not *né-wos: the glide is the root's
            raise DegreeError(f"{lex_id} ({form}) {why}: the primary comparative and superlative are built on the "
                              f"root of primary adjectives only (Handbook chs. 111 and 122; Beekes §14.4)")
    for end, suf in _SUFFIXES:
        if form.endswith(end):
            rest = parse(form[: -len(end)])
            if suf in ("ro", "mo") and (not rest or rest[-1].vocalic):
                continue                                     # bʰor-ós is thematic, not *bʰo-rós
            return form[: -len(end)], suf
    segs = parse(form)
    if len(segs) > 2 and segs[-1].base == "s" and not segs[-2].vocalic:
        if len(segs) > 3 and segs[-2].base in ("h1", "h2", "h3", "H") and not segs[-3].vocalic:
            # a root adjective in C+H: the laryngeal is the adjective's suffix (Beekes EDG s.v. μέγας *meǵ-h₂-),
            # and the degrees are built without it: *meǵ-yos- (Fortson §6.78; Handbook ch. 41 (Greek) *meǵi̯os-,
            # *meǵist(h₂)o-; Lat. maior, Gk μείζων, μέγιστος, Av. mazišta-)
            return render(segs[:-2]), "H"
        return form[:-1], ""                                 # root adjective
    raise DegreeError(f"{lex_id} ({form}): no primary adjective suffix (-u-, -ro-, -mo-, -o-) the engine can remove "
                      f"to reach the root")


def base(lex_id: str, lx) -> Base:
    """The accented full-grade root the degree suffixes attach to; DegreeError says why there is none.

    1. The headword minus its ending and primary suffix must be one root syllable.
    2. With a linked root (root_id) of the same consonants, the root's e-grade is the base (h₂r̥ǵrós → h₂érǵ-,
       polh₁ús → pléh₁-); a root that differs only in labialization gives its labiovelar back (h₁léngʰus beside
       *h₁lengʷʰ-: the boukólos delabialization next to u, Fortson §3.39; Ringe 2006 *h₁léngʷʰistos); one that
       has only an extra s-mobile leaves the adjective's own root. A linked root with other consonants means the
       stem holds a further suffix (bʰeh₂n-ós to *bʰeh₂-): rejected.
    3. Without a linked root, an e-grade stem is the base (swéh₂d-, sén-, h₁wés-); a zero or o-grade one is
       rejected (its full grade is not known)."""
    r = lx.specs.get(lex_id)
    if r is None or r.get("family") != "adj":
        raise DegreeError(f"{lex_id}: a degree of comparison is built on an adjective")
    if lex_id in getattr(lx, "blocked", {}):
        raise DegreeError(f"{lex_id} is blocked from generation: {lx.blocked[lex_id]}")
    if not r.get("usable"):
        raise DegreeError(f"{lex_id} has no usable spec (rule {r.get('rule')})")
    e = lx.entries[lex_id]
    form = e["form"].strip("*")
    stem, suffix = _stem(lex_id, form)
    segs = parse(stem)
    nuc = _nuclei(segs)
    if not nuc and any(x.base in ("h1", "h2", "h3", "H") for x in segs):
        # a zero-grade root whose nucleus is a laryngeal (mh₂ḱ-rós): its full grade comes from the root check
        nuc = [next(k for k, x in enumerate(segs) if x.base in ("h1", "h2", "h3", "H"))]
    if len(nuc) != 1:
        raise DegreeError(f"{lex_id} ({form}): the stem {stem}- is not a single root syllable; the primary degrees "
                          f"attach to the root (Beekes §14.4), and this adjective is derived")
    i = nuc[0]
    if segs[i].long:
        raise DegreeError(f"{lex_id} ({form}): a lengthened-grade (vr̥ddhi) root marks a derivative, not a primary "
                          f"adjective")
    e_grade = segs[i].kind == "V" and segs[i].base == "e"
    if suffix in ("o", "mo") and segs[i].kind == "V" and segs[i].base == "o":
        raise DegreeError(f"{lex_id} ({form}): an o-grade thematic adjective is a deverbal or denominal derivative "
                          f"(bʰorós 'carrying', ḱóymos 'homely'), not a primary adjective")
    if suffix == "o" and e_grade and not segs[i].acc:
        # a simple thematic adjective on an e-grade root counts as primary only with the accent on the root
        # (néwos, sénos: Ved. návyas-, Lat. senior); an accented thematic vowel there makes deverbal (weydós
        # 'seen') and denominal possessive adjectives (Handbook ch. 122: 'in this role is accented'), which are not
        # gradable. A zero-grade root with accented *-ó- is the Caland pattern of *-ró- (priHós: Ved. priyá-,
        # préyas-, préṣṭha-, Handbook ch. 27) and goes on to the root check
        raise DegreeError(f"{lex_id} ({form}): a thematic adjective with the accent on the thematic vowel is a "
                          f"deverbal or possessive derivative (Handbook ch. 122), not a primary adjective; only "
                          f"root-accented ones (néwos, sénos), zero-grade *-ó- (priHós) and -u-, -ro-, -mo- "
                          f"adjectives take the primary degrees")
    rid = e.get("root_id")
    root = lx.entries.get(rid, {}).get("form", "").strip("*-") if rid else ""
    if root:
        rs = parse(root)
        rn = _nuclei(rs)
        r_ok = len(rn) == 1 and rs[rn[0]].kind == "V" and rs[rn[0]].base == "e"
        if r_ok and _skeleton(rs) == _skeleton(segs):
            return Base(_accent_root(rs, rn[0]), "root" if not e_grade else "stem", suffix)
        if r_ok and _skeleton(rs, True) == _skeleton(segs, True):
            return Base(_accent_root(rs, rn[0]), "root-labiovelar", suffix)
        if e_grade and rs and rs[0].base == "s" and _skeleton(rs[1:]) == _skeleton(segs):
            return Base(_accent_root(segs, i), "stem", suffix)
        raise DegreeError(f"{lex_id} ({form}): the stem {stem}- has consonants its root {root}- lacks (or the "
                          f"reverse): the adjective holds a further suffix, so it is not a primary adjective")
    if e_grade:
        alts = ()
        if suffix == "H":             # the base with the laryngeal kept (the Wiktionary spec's méǵh₂yos-) stays
            alts = (_accent_root(parse(form[:-1]), i),)
        return Base(_accent_root(segs, i), "stem", suffix, alts)
    raise DegreeError(f"{lex_id} ({form}): the root is in the {'o' if segs[i].base == 'o' else 'zero'} grade and no "
                      f"linked root gives its full grade; the primary degrees need the full-grade root "
                      f"(Fortson §6.78)")


def _unacc(form: str) -> str:
    return render(deaccent(parse(form)))


def _comparative(root: str, gender: str, alt_roots: tuple = ()) -> Cells:
    """Cells of *root-yos-/*-is- (see the module docstring); m. and f. alike, n. its own."""
    r0 = _unacc(root)
    neuter = gender == "n"
    g = "n" if neuter else "m"
    prim = decline(NounSpec(root + "yos", r0 + "is", None, g), "handbook")
    alts = [
        decline(NounSpec(root + "iyos", r0 + "is", None, g), "handbook"),     # Sievers' variant
        decline(NounSpec(root + "yos", root + "yos", None, g), "handbook"),   # strong stem generalized (Ved., Gk)
        decline(NounSpec(root + "yos", root + "is", None, g), "handbook"),    # root-accented weak *R-is- (Wikt.)
    ]
    out = {k: list(v) for k, v in prim.items()}
    out["LOC.SG"] = _uniq([root + "yosi", r0 + "yési", r0 + "yés"] + out["LOC.SG"])
    if not neuter:
        out["ACC.SG"] = _uniq(out["ACC.SG"] + [r0 + "yésm̥"])               # Beekes *-iés-m
    else:
        for k in ("NOM.SG", "ACC.SG", "VOC.SG"):
            out[k] = _uniq([root + "yos", root + "is"] + out[k])             # Beekes: older *-is (Lat. magis)
        for k in ("NOM.PL", "ACC.PL", "VOC.PL"):
            out[k] = _uniq([root + "yosh₂", root + "yōs"] + out[k])
    rs = parse(root)
    if len(rs) > 2 and rs[-1].base in ("h1", "h2", "h3", "H") and not rs[-2].vocalic:
        # C+H before *-y-: Pinault's law (*CHy > *Cy; pie.phon.pinault, a debated rule the engine applies only
        # in the Wiktionary convention) gives Ringe's *h₁wér-yos- beside our h₁wérH-: an alternative only
        lost = render(rs[:-1])
        alts.append(decline(NounSpec(lost + "yos", _unacc(lost) + "is", None, g), "handbook"))
    for a in alt_roots:
        alts.append(_comparative(a, gender))
    for a in alts:
        for k, v in a.items():
            out[k] = _uniq(out.get(k, []) + v)
    return out


def _superlative(root: str, gender: str, alt_roots: tuple = ()) -> Cells:
    out = decline_adj(AdjSpec(root + "isto"), "handbook")[gender]
    for r in (root, *alt_roots):
        for suf in ("isto", "isth₂o"):
            alt = decline_adj(AdjSpec(r + suf), "handbook")[gender]
            out = {k: _uniq(v + alt.get(k, [])) for k, v in out.items()}
    return out


def cells(lex_id: str, degree: str, gender: str, lx) -> Cells:
    """Every cell of the degree in one gender, primary form first."""
    if degree not in DEGREES:
        raise DegreeError(f"degree must be one of {DEGREES}, not {degree!r}")
    if gender not in ("m", "f", "n"):
        raise ValueError("a degree's cells need a gender (m, f or n)")
    key = ("DEG", lex_id, degree, gender)
    cache = getattr(lx, "_cache", {})
    if key in cache:
        return cache[key]
    b = base(lex_id, lx)
    c = _comparative(b.root, gender, b.alts) if degree == "CMP" else _superlative(b.root, gender, b.alts)
    cache[key] = c
    return c


def primary(lex_id: str, degree: str, lx) -> str:
    """The citation form: masc. nom. sg. (swéh₂dyōs, swéh₂distos)."""
    return cells(lex_id, degree, "m", lx)["NOM.SG"][0]


# --- backtest (data/morph/degree_backtest.json; tests/test_degree.py; the doc's table) ---------------------------

def _norm(form: str) -> str:
    """A printed reconstruction in the engine's notation: no asterisk, no morpheme hyphens (*swéh₂d-yos- →
    swéh₂dyos, a stem keeps a final '-')."""
    import unicodedata
    f = unicodedata.normalize("NFC", form.strip().lstrip("*"))
    stem = f.endswith("-")
    return f.strip("-").replace("-", "") + ("-" if stem else "")


def _strip_acute(form: str) -> str:
    import unicodedata
    d = unicodedata.normalize("NFD", form)
    # keep the palatal mark on k/g (ḱ = k + U+0301): drop an acute only after a vowel or syllabic resonant
    out, prev = [], ""
    for ch in d:
        if ch == "́" and prev not in ("k", "g"):
            continue
        out.append(ch)
        if not unicodedata.combining(ch):
            prev = ch
    return unicodedata.normalize("NFC", "".join(out))


def _engine_forms(lex_id: str, degree: str, lx) -> tuple[str, list[str], list[str]]:
    """(primary stem, all stems, masc. nom. sg. forms primary first)."""
    b = base(lex_id, lx)
    suf = ("yos", "iyos") if degree == "CMP" else ("isto", "isth₂o")
    stems = [r + s for r in (b.root, *b.alts) for s in suf]
    rs = parse(b.root)
    if degree == "CMP" and len(rs) > 2 and rs[-1].base in ("h1", "h2", "h3", "H") and not rs[-2].vocalic:
        stems.append(render(rs[:-1]) + "yos")
    return stems[0], stems, cells(lex_id, degree, "m", lx)["NOM.SG"]


def backtest(items: list[dict], lx) -> list[dict]:
    """Score each item's printed PIE form against the engine. result: "hit" (the engine's primary form), "alt" (one
    of its alternative forms), "miss" (the engine builds another form), "rejected" (the engine refuses the
    adjective), "no-lexeme" (the positive is not in the lexicon: not scored). A target printed without an accent
    is compared without accents; a target ending in '-' is a stem, compared with the engine's stems."""
    out = []
    for it in items:
        row = {"id": it["id"], "target": it["target"], "degree": it["degree"]}
        lid = it.get("lex_id")
        if not lid or lid not in lx.specs:
            out.append({**row, "result": "no-lexeme", "engine": None})
            continue
        try:
            prim, stems, noms = _engine_forms(lid, it["degree"], lx)
        except DegreeError as e:
            out.append({**row, "result": "rejected", "engine": str(e)})
            continue
        t = _norm(it["target"])
        is_stem = t.endswith("-")
        t = t.rstrip("-")
        cand = stems if is_stem else noms
        primary_form = prim if is_stem else noms[0]
        acc = t != _strip_acute(t)
        f = (lambda x: x) if acc else _strip_acute
        if f(primary_form) == f(t):
            res = "hit"
        elif any(f(c) == f(t) for c in cand):
            res = "alt"
        else:
            res = "miss"
        out.append({**row, "result": res, "engine": primary_form})
    return out
