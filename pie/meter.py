"""Measured meter: deterministic syllable counts from canonical PIE.

A `meter` label is set only when the measured count matches; it is never a
hand label (IDEAS.md #6). Syllable counts in PIE depend on choices about
laryngeals and glides, so those are explicit, documented options:

  laryngeals="interconsonantal" (default): a laryngeal between two
      non-vocalic segments is syllabic (ph₂tḗr = pə-tḗr, 2 syllables); an
      initial #HC is not (h₂stḗr, 1). "none": laryngeals never count.
  sievers=False (default): no Sievers' law. True: after a heavy syllable,
      a prevocalic consonantal y/w counts as -iy-/-uw- (adds a syllable).

The count runs over words; punctuation and clitic hyphens are ignored.
"""

from __future__ import annotations

import re

from .phon import LARYNGEALS, Seg, parse

METERS = {8: "octosyllable", 11: "hendecasyllable", 12: "dodecasyllable"}
_NONWORD = re.compile(r"[.,;:!?\"()\[\]*=…]")


def _nuclei(segs: list[Seg], laryngeals: str) -> list[int]:
    idx = [i for i, s in enumerate(segs) if s.vocalic]
    if laryngeals == "interconsonantal":
        for i, s in enumerate(segs):
            if s.base in LARYNGEALS and 0 < i < len(segs) - 1 \
                    and not segs[i - 1].vocalic and not segs[i + 1].vocalic:
                idx.append(i)
    return sorted(idx)


def _heavy_before(segs: list[Seg], i: int, nuclei: list[int]) -> bool:
    """Is the syllable before position i heavy (long vowel, or a vowel followed by ≥2 consonants)?"""
    prev = [n for n in nuclei if n < i]
    if not prev:
        return False
    n = prev[-1]
    return segs[n].long or (i - n - 1) >= 1


def word_syllables(word: str, laryngeals: str = "interconsonantal", sievers: bool = False) -> int:
    segs = parse(word.replace("-", ""))
    nuclei = _nuclei(segs, laryngeals)
    count = len(nuclei)
    if sievers:
        for i, s in enumerate(segs):
            if s.kind == "R" and s.base in ("y", "w") and not s.syl and i > 0 and i + 1 < len(segs) \
                    and segs[i + 1].vocalic and not segs[i - 1].vocalic and _heavy_before(segs, i, nuclei):
                count += 1
    return count


def line_syllables(text: str, **opts) -> list[int]:
    words = [w for w in _NONWORD.sub(" ", text).split() if w.strip("-")]
    return [word_syllables(w, **opts) for w in words]


def measure(text: str, **opts) -> dict:
    per_word = line_syllables(text, **opts)
    total = sum(per_word)
    return {"syllables": total, "per_word": per_word, "meter": METERS.get(total),
            "options": {"laryngeals": opts.get("laryngeals", "interconsonantal"),
                        "sievers": opts.get("sievers", False)}}
