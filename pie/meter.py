"""Measured meter: deterministic syllable counts from canonical PIE.

A `meter` label is set only when the measured count matches; it is never a
hand label (IDEAS.md #6). Syllable counts in PIE depend on choices about
laryngeals and glides, so those are explicit, documented options:

  laryngeals="interconsonantal" (default): a laryngeal is syllabic (a
      nucleus, "ə") when it follows a consonant and precedes a consonant
      or the end of the word (the handbook rule: interconsonantal and
      word-final postconsonantal laryngeals vocalize; Fortson 2010 ch. 3):
        ph₂tḗr = pə-tḗr (Ved. pitā́, 2); dʰugh₂tḗr = dʰu-gə-tḗr (3);
        ǵénh₁tor = ǵé-nə-tor (Ved. janitár-, 3);
        CH#: méǵh₂ = mé-ǵə (Ved. máhi, Gk μέγα, 2); h₃ésth₁ (Ved. ásthi, 2);
        wékʷesh₂ (Gk ἔπεα, 3).
      Not syllabic:
        - word-initial #HC, including a word-initial laryngeal cluster
          #HHC (h₂stḗr, 1; h₂Hséh₂i): the Indo-Iranian treatment, not the
          Greek prothetic vowel;
        - a laryngeal right after another laryngeal: of -CHH- only the first
          vocalizes (h₃ésth₁h₂ = h₃é-stə-h₂, 2; méǵh₂h₂, 2), and -VHH# adds
          nothing;
        - a laryngeal after a diphthong in -y (V y H C or V y H#): the
          laryngeal joins the diphthong. Thematic optative -oyh₁t = Ved.
          -et, Gk -οι (bʰéroyh₁t = Ved. bháret, 2); dual dwóyh₁ = Ved. dvé
          (1); dayh₂wḗr = Ved. devár- (2); péyh₂wr̥ = Ved. pī́var- (2).
          After -w the laryngeal does vocalize (kréwh₂s = Ved. kravíṣ, 2;
          mléwHt = Ved. ábravīt, 2).
      "none": laryngeals never count.
  Resonants: syllabic r̥ l̥ m̥ n̥ i u (as written with the ring below, or as
      i/u) are nuclei; y w r l m n without the mark are not. The module trusts
      the engine's marks (phon.join already did junction syllabification); it
      does not re-derive resonant syllabicity. Glides are not split: dyḗws
      is 1 syllable (no Lindeman's law).
  sievers=False (default): no Sievers' law. True: after a heavy syllable,
      a prevocalic consonantal y/w counts as -iy-/-uw- (adds a syllable).

The count runs over words; punctuation and clitic hyphens are ignored (a
clitic joins its host, so h₃ésth₁-kʷe counts -th₁kʷ- as interconsonantal).
Word order therefore never changes a line's count.

Verse lines (`verse_lines`): a line is a sentence, split at . ? ! — the
realizer ends a sentence at every plan clause with "break": true. Metered
genres (`METERED_GENRES`) are scored against exact targets 8 (gāyatrī) and
11 (triṣṭubh), plus 12 (jagatī) when the plan record declares "meter": 12.
`cadence` reports (never gates) whether a line's close is the Vedic one.
"""

from __future__ import annotations

import re

from .phon import LARYNGEALS, Seg, parse

METERS = {8: "octosyllable", 11: "hendecasyllable", 12: "dodecasyllable"}
_NONWORD = re.compile(r"[.,;:!?\"()\[\]*=…]")

# Genres whose sentences are verse lines (realize_plans, meter_report and the census read this set).
METERED_GENRES = frozenset({"hymn", "prayer", "charm", "praise", "lament", "wedding", "work song"})
TARGETS = (8, 11)              # Vedic gāyatrī and triṣṭubh line lengths
DECLARABLE = (12,)             # jagatī: a target only for a plan record that declares "meter": 12
# The Vedic closes, last four syllables (L light, H heavy, X anceps): gāyatrī iambic ⏑ – ⏑ ×, triṣṭubh
# trochaic – ⏑ – ×, jagatī iambic ⏑ – ⏑ ×.
CADENCES = {8: "LHLX", 11: "HLHX", 12: "LHLX"}


def _syllabic_laryngeals(segs: list[Seg]) -> set[int]:
    """Indices of laryngeals that are nuclei (see the module docstring)."""
    out: set[int] = set()
    initial = True          # still inside the word-initial run of laryngeals
    for i, s in enumerate(segs):
        if s.base not in LARYNGEALS:
            initial = False
            continue
        if initial or i == 0:
            continue
        prev = segs[i - 1]
        if prev.vocalic or prev.base in LARYNGEALS:
            continue
        if prev.base == "y" and i >= 2 and segs[i - 2].kind == "V":
            continue        # V y H: the laryngeal joins the diphthong (-oyh₁t = Ved. -et)
        if i + 1 < len(segs) and segs[i + 1].vocalic:
            continue
        out.add(i)
    return out


def _nuclei(segs: list[Seg], laryngeals: str) -> list[int]:
    idx = [i for i, s in enumerate(segs) if s.vocalic]
    if laryngeals == "interconsonantal":
        idx += _syllabic_laryngeals(segs)
    return sorted(idx)


def _heavy_before(segs: list[Seg], i: int, nuclei: list[int]) -> bool:
    """Is the syllable before position i heavy (long vowel, or a vowel followed by ≥2 consonants)?"""
    prev = [n for n in nuclei if n < i]
    if not prev:
        return False
    n = prev[-1]
    return segs[n].long or (i - n - 1) >= 1


def _word_segs(word: str) -> list[Seg]:
    return parse(word.replace("-", ""))


def word_syllables(word: str, laryngeals: str = "interconsonantal", sievers: bool = False) -> int:
    segs = _word_segs(word)
    nuclei = _nuclei(segs, laryngeals)
    count = len(nuclei)
    if sievers:
        for i, s in enumerate(segs):
            if s.kind == "R" and s.base in ("y", "w") and not s.syl and i > 0 and i + 1 < len(segs) \
                    and segs[i + 1].vocalic and not segs[i - 1].vocalic and _heavy_before(segs, i, nuclei):
                count += 1
    return count


def _words(text: str) -> list[str]:
    return [w for w in _NONWORD.sub(" ", text).split() if w.strip("-")]


def line_syllables(text: str, **opts) -> list[int]:
    return [word_syllables(w, **opts) for w in _words(text)]


def measure(text: str, **opts) -> dict:
    per_word = line_syllables(text, **opts)
    total = sum(per_word)
    return {"syllables": total, "per_word": per_word, "meter": METERS.get(total),
            "options": {"laryngeals": opts.get("laryngeals", "interconsonantal"),
                        "sievers": opts.get("sievers", False)}}


def weights(text: str) -> str:
    """Syllable weights of a line, one letter per syllable (default options): H heavy, L light.

    The line is one stream (Vedic syllabification runs across word boundaries): a syllable is heavy when its
    nucleus is long or two or more non-nuclear segments follow it before the next nucleus (a diphthong's
    glide counts as one of them). A syllabic laryngeal or resonant is a short nucleus. The line's last
    syllable is weighed the same way here; `cadence` treats it as anceps."""
    segs: list[Seg] = []
    nuclei: list[int] = []
    for w in _words(text):
        ws = _word_segs(w)
        nuclei += [len(segs) + i for i in _nuclei(ws, "interconsonantal")]
        segs += ws
    out = []
    for k, n in enumerate(nuclei):
        nxt = nuclei[k + 1] if k + 1 < len(nuclei) else len(segs)
        out.append("H" if segs[n].long or nxt - n - 1 >= 2 else "L")
    return "".join(out)


def cadence(text: str, target: int) -> bool | None:
    """Does the line close with the Vedic cadence for `target` syllables (CADENCES)? None if no pattern."""
    pat = CADENCES.get(target)
    w = weights(text)
    if not pat or len(w) < len(pat):
        return None
    return all(p == "X" or p == x for p, x in zip(pat, w[-len(pat):]))


def verse_lines(pie: str) -> list[str]:
    """A record's verse lines: its sentences (split at . ? !), as realize() ends them at each break."""
    return [x.strip() for x in re.split(r"[.?!]", pie) if x.strip()]


def targets_for(declared: int | None = None) -> tuple[int, ...]:
    """The exact line lengths a text is scored against: 8 and 11, plus 12 if the text declares it."""
    return TARGETS + ((declared,) if declared in DECLARABLE else ())


def nearest_target(n: int, targets: tuple[int, ...] = TARGETS) -> int:
    """The target closest to n (ties go to the shorter line)."""
    return min(targets, key=lambda t: (abs(n - t), t))


def record_meter(pie: str, genre: str | None, declared: int | None = None) -> dict | None:
    """The `meter` field of a corpus record: None outside METERED_GENRES. `fit` keeps its original meaning
    (lines within ±1 of a target); `exact` counts lines of exactly a target length; `cadence` has one entry
    per line: for a line of exactly a target length, whether it closes with that length's Vedic cadence,
    else None (information only, never a gate)."""
    if genre not in METERED_GENRES:
        return None
    tg = targets_for(declared)
    lines = verse_lines(pie)
    syl = [measure(x)["syllables"] for x in lines]
    return {"line_syllables": syl, "fit": sum(any(abs(n - t) <= 1 for t in tg) for n in syl),
            "targets": list(tg), "exact": sum(n in tg for n in syl),
            "cadence": [cadence(x, n) if n in tg else None for x, n in zip(lines, syl)]}


def summary(metered: list[dict]) -> dict | None:
    """Batch meter numbers from records' `meter` fields (record_meter output; an older field without
    `exact` gets it from line_syllables, and without `cadence` contributes no cadence numbers).
    near = within ±1 of a target (the original meter_fit); exact = exactly a target length."""
    if not metered:
        return None
    lines = sum(len(m["line_syllables"]) for m in metered)
    fit = sum(m["fit"] for m in metered)
    exact = sum(m["exact"] if "exact" in m else sum(n in m["targets"] for n in m["line_syllables"])
                for m in metered)
    cad: dict[str, dict] = {}
    for m in metered:
        for n, c in zip(m["line_syllables"], m.get("cadence") or []):
            if c is not None:
                d = cad.setdefault(str(n), {"lines": 0, "cadence": 0, "pattern": CADENCES[n]})
                d["lines"] += 1
                d["cadence"] += c
    for d in cad.values():
        d["share"] = round(d["cadence"] / d["lines"], 3)
    return {"lines": lines, "near": fit, "near_share": round(fit / max(1, lines), 3),
            "exact": exact, "exact_share": round(exact / max(1, lines), 3),
            "cadence": dict(sorted(cad.items(), key=lambda kv: int(kv[0])))}
