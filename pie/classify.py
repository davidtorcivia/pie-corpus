"""Layer 2: lexicon entry → inflection spec.

  1. A Wiktionary inflection table, if the entry has one (source "table").
  2. Otherwise a shape rule on the lemma. Each rule's accuracy is measured
     by backtesting it on entries that do have tables
     (scripts/classify_lexicon.py), and every spec records which rule made it.
  3. Otherwise None: indeclinable, or out of scope (middle-only verbs,
     heteroclite plurals, ...).

Shape rules guess. Their confidence comes from the backtest, never from
how plausible the rule looks.
"""

from __future__ import annotations

import unicodedata

from dataclasses import dataclass, replace

from .morph import AdjSpec, NounSpec, VerbSpec
from .phon import Seg, parse, render

INDECLINABLE_POS = {"adv", "particle", "conj", "prep", "postp", "intj", "phrase", "num"}


def _split(v: str | None) -> list[str]:
    return [x.strip().lstrip("*") for x in v.split(",")] if v else []


def spec_from_template(t: dict):
    """Spec from one Wiktionary inflection template: (family, spec), or None."""
    name, a = t["name"], t["args"]
    if any(" " in v for k, v in a.items() if k.isdigit()):
        return None  # phrases are out of scope
    if name in ("ine-decl-noun-mf", "ine-decl-noun-n"):
        strong = a["1"]
        gender = "n" if name.endswith("-n") else ("f" if strong.endswith(("eh₂", "éh₂")) else "m")
        return "noun", NounSpec(strong, a.get("2"), a.get("ac"), gender,
                                nom_sg=_split(a.get("nom_sg"))[0] if a.get("nom_sg") else None,
                                loc_sg=_split(a.get("loc_sg")))
    if name == "ine-decl-adj":
        return "adj", AdjSpec(a["1"], a.get("2"), a.get("3"), a.get("4"), a.get("ac"), _split(a.get("loc_sg")))
    if name.startswith("ine-conj-"):
        return "verb", VerbSpec(a["1"], a.get("2"), name.removeprefix("ine-conj-"))
    return None


@dataclass
class Classified:
    spec: NounSpec | AdjSpec | VerbSpec | None
    rule: str           # "table", "shape:<name>", "indeclinable", "unknown"
    family: str | None  # noun | adj | verb


def _segs(s: str) -> list[Seg]:
    return parse(s)


def _redup_weak(stem: str) -> str | None:
    """Reduplicated presents keep the reduplication and zero-grade the root: dʰédʰeh₁ → dʰedʰh₁,
    dédeh₃ → dedh₃, sísteh₂ → sisth₂ (Ved. dadhmás, dadmás; tier3-t010 review). zero_grade() alone
    would delete the accented reduplication vowel (dʰdʰeh₁-)."""
    segs = _segs(stem)
    red = segs[1] if len(segs) > 1 else None   # the reduplication vowel: e, or i (parsed as syllabic y)
    if len(segs) < 4 or not red.acc or not ((red.kind == "V" and red.base == "e") or (red.syl and red.base == "y")):
        return None
    if segs[0].kind == "V" or segs[0].base != segs[2].base:
        return None
    root = list(segs[2:])
    j = next((i for i, x in enumerate(root) if x.kind == "V" and x.base in "eo"), None)
    if j is None:
        return None
    root = [replace(x, acc=(i == j)) for i, x in enumerate(root)]
    # zero-grade the root with the (deaccented) reduplication in place, so that a glide next to the deleted
    # vowel sees the reduplication vowel: wé-woḱ → wewḱ, wí-wekʷ → wiwkʷ, yé-yes → yeys (zero-grading the root
    # alone gave weuḱ, wiukʷ, yeis: two nuclei in hiatus). Engine sweep, athematic-verbs.md S3.
    return zero_grade(render([replace(x, acc=False) for x in segs[:2]] + root))


def zero_grade(stem: str) -> str | None:
    """Delete the accented short e/o and re-syllabify its neighbours only,
    then de-accent: gʷʰén → gʷʰn̥, dyéw → dyu, wóyd → wid, linékʷ → linkʷ,
    h₁és → h₁s, ḱwón → ḱwn̥, h₁éy → h₁i."""
    segs = _segs(stem)
    idx = next((i for i, x in enumerate(segs) if x.kind == "V" and x.acc and not x.long and x.base in "eo"), None)
    if idx is None:
        return None
    out = [replace(x, acc=False) for x in segs[:idx] + segs[idx + 1:]]

    def vocalic(i):
        return 0 <= i < len(out) and out[i].vocalic

    for i in (idx, idx - 1):  # right neighbour first, then left
        if 0 <= i < len(out) and out[i].kind == "R" and not out[i].long:
            out[i] = replace(out[i], syl=not (vocalic(i - 1) or vocalic(i + 1)))
    return render(out)


def _strip(form: str, suffix: str) -> str:
    assert form.endswith(suffix)
    return form[: len(form) - len(suffix)]


def _deaccent(s: str) -> str:
    return render([replace(x, acc=False) for x in _segs(s)])


def _plain_roman(x: dict) -> str:
    s = unicodedata.normalize("NFD", (x.get("roman") or x.get("form") or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _reflex_evidence(e: dict) -> str | None:
    """What the daughters say about an -os noun's stem class, from citation forms.

    s-stem: a Sanskrit citation form in -as (thematic nouns are cited as -a
    stems: vŕ̥ka-, but s-stems as -as: óhas, mánas), a Greek plural in -εα
    (μήδεα), or ḗ/é ablaut in the stems (mḗdos ~ médos, Narten).
    neuter: a Greek reflex in -ον or a Latin one in -um, with no s-stem sign.
    """
    r = e.get("reflexes", {})
    usable = lambda xs: [x for x in xs if not (x.get("borrowed") or x.get("analogical"))]
    skt = [_plain_roman(x) for k in ("Sanskrit", "Vedic Sanskrit") for x in usable(r.get(k, []))]
    grc = [x.get("form", "") for x in usable(r.get("Ancient Greek", []))]
    lat = [_plain_roman(x) for x in usable(r.get("Latin", []))]
    stems = e.get("stems", [])
    if any(x.endswith("as") for x in skt) or any(x.endswith("εα") for x in grc) or \
            (any("ḗ" in x for x in stems) and any("é" in x for x in stems)):
        return "s-stem"
    if any(x.endswith(("ον", "όν")) for x in grc) or any(x.endswith("um") for x in lat):
        return "neuter"
    return None


def by_shape(e: dict) -> Classified:
    f, pos, g = e["form"], e.get("pos"), e.get("gender")
    if pos == "num" and f.endswith(("os", "ós")):
        return Classified(AdjSpec(f[:-1]), "shape:thematic-adj", "adj")   # óynos "one"
    if pos in INDECLINABLE_POS or f.startswith("-") or f.endswith("-") or " " in f:
        return Classified(None, "indeclinable" if pos in INDECLINABLE_POS else "unknown", None)
    is_verb = pos == "verb" or (pos is None and f.endswith(("ti", "tor", "toy")))

    # s-aorist (Ringe 2006 p. 34 *dḗyḱ-s-t, *wḗǵʰ-s-t; Fortson §5.47): lengthened grade in the active indicative,
    # full grade elsewhere (Wiktionary's ine-conj-pf args wḗǵʰs / wéǵʰs). Many are LIV derivatives without pos.
    # Engine sweep, thematic-verbs.md defect 8.
    if f.endswith("st") and "ḗ" in f and pos in (None, "verb") and e.get("aspect") in (None, "pf"):
        st = f[:-1]
        return Classified(VerbSpec(st, st.replace("ḗ", "é"), "pf"), "shape:s-aorist", "verb")
    if is_verb:
        if f.endswith(("etor", "étor")):     # thematic media tantum: *mr̥-yé-tor, *sékʷ-e-tor (L&Y §4.2.3, §4.3.1)
            return Classified(VerbSpec(_strip(f, "tor")), "shape:thematic-middle", "verb")
        if f.endswith(("tor", "toy")):
            return Classified(None, "unknown:middle-only", "verb")
        if e.get("aspect") == "stat" and f.endswith("e"):
            st = f[:-1]
            wk = zero_grade(st)
            return Classified(VerbSpec(st, wk, "stat") if wk else None, "shape:perfect", "verb")
        if f.endswith(("eti", "éti")):
            return Classified(VerbSpec(_strip(f, "ti")), "shape:thematic-present", "verb")
        if f.endswith("ti"):
            st = _strip(f, "ti")
            wk = _redup_weak(st) or zero_grade(st)
            if wk is None:
                return Classified(None, "unknown:athematic-no-ablaut", "verb")
            kind = "pf" if e.get("aspect") == "pf" else "impf"
            return Classified(VerbSpec(st, wk, kind), "shape:athematic-root", "verb")
        if f.endswith("t") and e.get("aspect") == "pf":
            st = f[:-1]
            if st.endswith(("e", "é")):   # thematic aorist (widét): stem widé-, no ablaut
                return Classified(VerbSpec(st, None, "pf"), "shape:thematic-aorist", "verb")
            wk = e.get("aorist_weak") or zero_grade(st)      # LIV² prints the weak stem
            return Classified(VerbSpec(st, wk, "pf") if wk else None, "shape:root-aorist", "verb")
        return Classified(None, "unknown:verb-shape", "verb")

    if pos == "adj":
        if f.endswith(("os", "ós")):
            return Classified(AdjSpec(_strip(f, "s")), "shape:thematic-adj", "adj")
        if f.endswith(("us", "ús")):
            st = _strip(f, "s")
            wk = zero_grade(st)
            if wk:
                weak = _deaccent(wk[:-1]) + "éw"
                return Classified(AdjSpec(st, weak, _deaccent(wk[:-1]) + "éwih₂", _deaccent(wk) + "yéh₂",
                                          "proterokinetic"), "shape:u-adj", "adj")
        return Classified(None, "unknown:adj-shape", "adj")

    # nouns, and derivatives with an unknown part of speech
    s_stem_evidence = any(x.rstrip("-").endswith(("esos", "és", "es"))     # tree stems end in "-" (sélpes-)
                          for x in e.get("stems", []) + e.get("variants", []))
    refl = _reflex_evidence(e)
    # neuter s-stems are barytone, so reflex evidence only counts for -os, never oxytone -ós
    if f.endswith(("os", "ós")) and (g == "n" or s_stem_evidence or (refl == "s-stem" and not f.endswith("ós"))):
        # neuter s-stem (téwh₂os ~ téwh₂esos), not a thematic masculine
        st = f
        segs = parse(st)
        if not any(x.acc for x in segs):
            # acrostatic: root accent throughout (Ringe 2006 §2.3.4(ii) nébʰos ~ nébʰes-; Fortson §6.38). An
            # unaccented headword (medos, stugos) would get ending accent in the oblique (medesés): engine
            # sweep, s-root-heteroclite.md F3
            i = next((j for j, x in enumerate(segs[:-2]) if x.vocalic), None)
            if i is not None:              # ḱh₂dos has no root vowel: left alone
                segs[i] = replace(segs[i], acc=True)
                st = render(segs)
        return Classified(NounSpec(st, _strip(st, "os") + "es", "acrostatic", "n"), "shape:s-stem-neuter", "noun")
    if f.endswith("os") and not f.endswith("ós") and g not in ("m", "f") and refl == "neuter":
        # the daughters agree on a neuter (Gk -ον, Lat. -um): plówyos → plówyom
        return Classified(NounSpec(_strip(f, "s"), gender="n"), "shape:thematic-neuter-reflex", "noun")
    if f.endswith(("os", "ós")):
        return Classified(NounSpec(_strip(f, "s"), gender=g if g in ("m", "f") else "m"), "shape:thematic", "noun")
    if f.endswith(("om", "óm")):
        return Classified(NounSpec(_strip(f, "m"), gender="n"), "shape:thematic-neuter", "noun")
    if f.endswith(("ih₂", "íh₂")):
        if pos == "pron":     # síh₂ 'she': pronominal inflection is closed-class (data/morph/closed_class.json)
            return Classified(None, "unknown:pronoun", "noun")
        st = f
        base = _strip(f, "íh₂") if f.endswith("íh₂") else _strip(f, "ih₂")
        bs = _segs(base)
        acc = next((x for x in bs if x.kind == "V" and x.acc), None)
        if f.endswith("ih₂") and acc is not None and (acc.base == "o" or acc.long):
            # an accented o-grade or lengthened-grade root keeps the root accent throughout (fixed accent, as in
            # acrostatic nouns, Fortson §6.21; Ved. pátnī, gen. pátnyāḥ; rā́jñī, gen. rā́jñyāḥ) and, as Wiktionary's
            # tables write it, its grade (pótnih₂ ~ pótn̥yeh₂, h₃rḗǵnih₂ ~ h₃rḗǵn̥yeh₂): Vedic cannot tell *o from
            # *e, and §6.21's o/e ablaut is not applied here.
            # zero_grade() deleted the only root vowel instead (pótnih₂ → ptnyéh₂). A resonant after a consonant
            # is syllabic before -yeh₂, as the tables write it.
            if len(bs) > 1 and bs[-1].kind == "R" and not bs[-2].vocalic:
                bs = bs[:-1] + [replace(bs[-1], syl=True)]
            return Classified(NounSpec(st, render(bs) + "yeh₂", "proterokinetic", "f", devi=True), "shape:devi",
                              "noun")
        if acc is None and not f.endswith("íh₂"):
            # no accent on the headword: the oblique accent depends on it (Ved. devī́, devyā́s against pátnī,
            # pátnyāḥ), and an unaccented athematic stem would take accented endings, so any paradigm would guess
            # one (the accent is missing information: docs/morphology.md accent policy)
            return Classified(None, "unknown:devi-no-accent", "noun")
        root = zero_grade(base) if f.endswith("ih₂") else None
        weak = (root or _deaccent(base)) + "yéh₂"
        return Classified(NounSpec(st, weak, "proterokinetic", "f", devi=True), "shape:devi", "noun")
    if f.endswith(("eh₂", "éh₂")):
        return Classified(NounSpec(f, gender="f"), "shape:eh2", "noun")
    if f.endswith(("tḗr", "ḗr")) and g != "n":   # not the neuter root noun ḱḗr (a d-stem, ḱérd-/ḱr̥d-)
        st = f.replace("ḗr", "ér")
        # zero-grade suffix only (Fortson §6.23, §6.37: *ph₂tér-/*ph₂tr-, *dh₃tḗr): zero_grade() reduced the root
        # of a doubly accented lemma instead (spéḱtḗr → spḱter-); such lemmas get no spec (engine sweep,
        # r-n-stems.md defect 8)
        one_accent = sum(x.acc for x in _segs(st)) == 1      # (not a count of U+0301: ḱ/ǵ carry one too)
        wk = _deaccent(st[:-2]) + "r̥" if one_accent else None
        return Classified(NounSpec(st, wk, "hysterokinetic", g if g in ("m", "f") else "m") if wk else None,
                          "shape:er-stem", "noun")
    if f.endswith("tōr"):                       # amphikinetic agent noun: ǵʰéwtōr, ǵʰéwtorm̥
        root = _strip(f, "tōr")
        wk = zero_grade(root)
        if wk:
            # locative in the accented e-grade suffix with zero-grade root, as in the tables (dh₃tér, pkʷtér;
            # Fortson §6.24 amphikinetic), not the strong stem (dʰéh₁tori): engine sweep, r-n-stems.md defect 7
            return Classified(NounSpec(root + "tor", wk + "tr̥", "amphikinetic", g if g in ("m", "f") else "m",
                                       nom_sg=f, loc_sg=[wk + "tér"]), "shape:tor-agent", "noun")
    if f.endswith(("ís", "ús")):
        st = _strip(f, "s")
        weak = _deaccent(st[:-1]) + ("éy" if f.endswith("ís") else "éw")
        return Classified(NounSpec(st, weak, "hysterokinetic", g if g in ("m", "f") else "f"), "shape:hk-iu-stem",
                          "noun")
    if f.endswith(("is", "us")):
        st = _strip(f, "s")
        segs = _segs(st)
        ai = next((j for j, x in enumerate(segs) if x.kind == "V" and x.acc), None)
        acc = segs[ai] if ai is not None else None
        # Fortson §6.27: mobile (proterokinetic) inflection spread at the expense of acrostatic in roots ending in a
        # resonant + consonant, so ó + RC (h₁órǵʰis ~ h₁r̥ǵʰéys, ḱlównis ~ ḱlunéys) keeps the zero grade below
        rc = ai is not None and ai + 2 < len(segs) - 1 and segs[ai + 1].kind == "R" and not segs[ai + 1].syl \
            and segs[ai + 2].kind in ("C", "R") and not segs[ai + 2].syl
        if acc is not None and acc.base == "o" and not acc.long and not rc:
            # an accented o-grade root is acrostatic with o/e ablaut, root accent throughout (Fortson §6.21: *nókʷt-s
            # ~ *nékʷt-; the tables h₂ówis ~ h₂éwis 'sheep', h₁ógʷʰis ~ h₁égʷʰis 'snake', h₂óḱris ~ h₂éḱris 'edge');
            # the proterokinetic zero grade (h₂wéys) is the e-grade pattern (Fortson §6.22: ménti- ~ mn̥téy-).
            # Backtest 84.7% → see data/morph/classify_report.json (engine-queue-wave1 census)
            weak = render([replace(x, base="e") if x is acc else x for x in segs])
            return Classified(NounSpec(st, weak, "acrostatic", g if g in ("m", "f") else "f"),
                              "shape:pk-iu-stem", "noun")
        wk = zero_grade(st)
        if wk:
            weak = wk[:-1] + ("éy" if f.endswith("is") else "éw")
            return Classified(NounSpec(st, weak, "proterokinetic", g if g in ("m", "f") else "f"),
                              "shape:pk-iu-stem", "noun")
    if f.endswith("ṓ"):                       # final accent: hysterokinetic (ḱwṓ, ḱwn̥-)
        st = f[:-1] + "ón"
        wk = zero_grade(st)
        # the locative has the accented e-grade suffix, -én(i), not the o-grade of the strong stem (the tables
        # ḱwṓ: ḱwén, ḱwéni; sh₂imṓ: sh₂imén; Fortson §6.24 hysterokinetic loc. in *-ér/-én)
        loc = [wk[:-2] + "én", wk[:-2] + "éni"] if wk and wk.endswith("n̥") else []
        return Classified(NounSpec(st, wk, "hysterokinetic", g if g in ("m", "f") else "m", loc_sg=loc)
                          if wk else None, "shape:n-stem-hk", "noun")
    if f.endswith("ō"):                        # root accent: amphikinetic (kólHō, kl̥Hn̥-, loc. kl̥Hén)
        root = zero_grade(f[:-1])
        # (liquids and nasals only: a glide stays vocalic, gléwō → glun̥ as pléwmō → plumn̥ in the tables)
        if root and _segs(root)[-1].kind == "R" and _segs(root)[-1].syl and _segs(root)[-1].base in "rlmn":
            # a root-final resonant before -n̥ / -én is consonantal: h₃érō → h₃rn̥, loc. h₃rén (the table's), not
            # h₃r̥n̥, h₃r̥én; zero_grade() syllabified it before the suffix was added (engine-queue-wave1 census)
            rs = _segs(root)
            root = render(rs[:-1] + [replace(rs[-1], syl=False)])
        if root:
            return Classified(NounSpec(f[:-1] + "on", root + "n̥", "amphikinetic", g if g in ("m", "f") else "m",
                                       loc_sg=[root + "én"]), "shape:n-stem-ak", "noun")
    if f.endswith("mn̥") and g in (None, "n"):
        root = zero_grade(_strip(f, "mn̥"))          # h₁nómn̥ → h₁nó- → h₁n̥-
        if root:
            return Classified(NounSpec(f, root + "mén", "proterokinetic", "n"), "shape:men-neuter", "noun")
    return Classified(None, "unknown:noun-shape", "noun")
