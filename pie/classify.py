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


def by_shape(e: dict) -> Classified:
    f, pos, g = e["form"], e.get("pos"), e.get("gender")
    if pos == "num" and f.endswith(("os", "ós")):
        return Classified(AdjSpec(f[:-1]), "shape:thematic-adj", "adj")   # óynos "one"
    if pos in INDECLINABLE_POS or f.startswith("-") or f.endswith("-") or " " in f:
        return Classified(None, "indeclinable" if pos in INDECLINABLE_POS else "unknown", None)
    is_verb = pos == "verb" or (pos is None and f.endswith(("ti", "tor", "toy")))

    if is_verb:
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
            wk = zero_grade(st)
            if wk is None:
                return Classified(None, "unknown:athematic-no-ablaut", "verb")
            kind = "pf" if e.get("aspect") == "pf" else "impf"
            return Classified(VerbSpec(st, wk, kind), "shape:athematic-root", "verb")
        if f.endswith("t") and e.get("aspect") == "pf":
            st = f[:-1]
            wk = zero_grade(st)
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
    if f.endswith(("os", "ós")) and g == "n":
        st = f
        return Classified(NounSpec(st, _strip(f, "os") + "es", "acrostatic", "n"), "shape:s-stem-neuter", "noun")
    if f.endswith(("os", "ós")):
        return Classified(NounSpec(_strip(f, "s"), gender=g if g in ("m", "f") else "m"), "shape:thematic", "noun")
    if f.endswith(("om", "óm")):
        return Classified(NounSpec(_strip(f, "m"), gender="n"), "shape:thematic-neuter", "noun")
    if f.endswith(("ih₂", "íh₂")):
        st = f
        base = _strip(f, "íh₂") if f.endswith("íh₂") else _strip(f, "ih₂")
        root = zero_grade(base) if f.endswith("ih₂") else None
        weak = (root or _deaccent(base)) + "yéh₂"
        return Classified(NounSpec(st, weak, "proterokinetic", "f", devi=True), "shape:devi", "noun")
    if f.endswith(("eh₂", "éh₂")):
        return Classified(NounSpec(f, gender="f"), "shape:eh2", "noun")
    if f.endswith(("tḗr", "ḗr")):
        st = f.replace("ḗr", "ér")
        wk = zero_grade(st)
        return Classified(NounSpec(st, wk, "hysterokinetic", g if g in ("m", "f") else "m") if wk else None,
                          "shape:er-stem", "noun")
    if f.endswith(("ís", "ús")):
        st = _strip(f, "s")
        weak = _deaccent(st[:-1]) + ("éy" if f.endswith("ís") else "éw")
        return Classified(NounSpec(st, weak, "hysterokinetic", g if g in ("m", "f") else "f"), "shape:hk-iu-stem",
                          "noun")
    if f.endswith(("is", "us")):
        st = _strip(f, "s")
        wk = zero_grade(st)
        if wk:
            weak = wk[:-1] + ("éy" if f.endswith("is") else "éw")
            return Classified(NounSpec(st, weak, "proterokinetic", g if g in ("m", "f") else "f"),
                              "shape:pk-iu-stem", "noun")
    if f.endswith("ṓ"):                       # final accent: hysterokinetic (ḱwṓ, ḱwn̥-)
        st = f[:-1] + "ón"
        wk = zero_grade(st)
        return Classified(NounSpec(st, wk, "hysterokinetic", g if g in ("m", "f") else "m") if wk else None,
                          "shape:n-stem-hk", "noun")
    if f.endswith("ō"):                        # root accent: amphikinetic (kólHō, kl̥Hn̥-, loc. kl̥Hén)
        root = zero_grade(f[:-1])
        if root:
            return Classified(NounSpec(f[:-1] + "on", root + "n̥", "amphikinetic", g if g in ("m", "f") else "m",
                                       loc_sg=[root + "én"]), "shape:n-stem-ak", "noun")
    if f.endswith("mn̥") and g in (None, "n"):
        root = zero_grade(_strip(f, "mn̥"))          # h₁nómn̥ → h₁nó- → h₁n̥-
        if root:
            return Classified(NounSpec(f, root + "mén", "proterokinetic", "n"), "shape:men-neuter", "noun")
    return Classified(None, "unknown:noun-shape", "noun")
