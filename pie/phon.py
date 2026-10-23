"""Segment-level phonology for the morphology engine.

A form is a list of Seg. Resonants (r l m n y w) carry a `syl` flag: i, u,
r̥, l̥, m̥, n̥ are the syllabic resonants y, w, r, l, m, n. True vowels are
a e o (and long or accented i/u stay fixed as syllabic).

Only four phonological rules are implemented, on purpose. The sources we
compare against write underlying forms, without cluster assimilations.
  - junction syllabification (join)
  - accent: an accented stem de-accents the ending (join)
  - Szemerényi's law: -VRs# → -V̄R#, plus the n-stem -ōn# → -ō# (szemerenyi)
  - Stang's law: -Vwm# → -V̄m# (stang)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace

from .translit import to_ascii, to_unicode

_TOKEN = re.compile(
    r"(k'|g'h(?![123])|g'|gwh(?![123])|kw|gw|bh(?![123])|dh(?![123])|gh(?![123])|h[123]|H|[ptbdkgsz]"
    r"|[rlmn]_|[rlmnwy]|[aeiou])(:)?(/)?|(\\w)|(-)"
)
RESONANTS = set("rlmnwy")


@dataclass(frozen=True)
class Seg:
    base: str          # ASCII base: "k'", "gwh", "h2", "r", "y", "e", …
    kind: str          # V (vowel) | R (resonant) | C (other consonant, incl. laryngeals)
    syl: bool = False  # resonants: syllabic
    long: bool = False
    acc: bool = False

    @property
    def vocalic(self) -> bool:
        return self.kind == "V" or (self.kind == "R" and self.syl)

    def ascii(self) -> str:
        if self.kind == "R" and self.syl:
            b = {"y": "i", "w": "u"}.get(self.base, self.base + "_")
        else:
            b = self.base
        return b + (":" if self.long else "") + ("/" if self.acc else "")


def parse(form: str) -> list[Seg]:
    a = to_ascii(form)
    segs: list[Seg] = []
    pos = 0
    while pos < len(a):
        m = _TOKEN.match(a, pos)
        if not m:
            raise ValueError(f"cannot segment {form!r} at {a[pos:]!r}")
        pos = m.end()
        if m[4]:
            segs.append(Seg("w", "R"))
            continue
        if m[5]:
            continue  # morpheme boundaries are not segments
        tok, long, acc = m[1], bool(m[2]), bool(m[3])
        if tok in ("i", "u"):
            segs.append(Seg({"i": "y", "u": "w"}[tok], "R", syl=True, long=long, acc=acc))
        elif tok.endswith("_"):
            segs.append(Seg(tok[0], "R", syl=True, long=long, acc=acc))
        elif tok in RESONANTS:
            segs.append(Seg(tok, "R"))
        elif tok in ("a", "e", "o"):
            segs.append(Seg(tok, "V", long=long, acc=acc))
        else:
            segs.append(Seg(tok, "C"))
    return segs


def render(segs: list[Seg]) -> str:
    # Serialize each segment separately: plain k/g + w must not read as kʷ.
    return unicodedata.normalize("NFC", "".join(to_unicode(s.ascii()) for s in segs))


def has_accent(segs: list[Seg]) -> bool:
    return any(s.acc for s in segs)


def deaccent(segs: list[Seg]) -> list[Seg]:
    return [replace(s, acc=False) for s in segs]


def _fixed(s: Seg) -> bool:
    """Long or accented syllabics never lose syllabicity."""
    return s.kind == "R" and s.syl and (s.long or s.acc)


def join(stem: list[Seg], ending: list[Seg]) -> list[Seg]:
    """Concatenate with junction syllabification and accent resolution.

    1. If the stem is accented, the ending loses its accent.
    2. If the stem ends in a non-fixed syllabic resonant and the ending
       begins with a vocalic segment, it becomes consonantal. Then, moving
       left, a consonantal resonant now flanked by non-vocalic segments
       becomes syllabic (dyu+és → diwés, ḱwn̥+és → ḱunés, deh₂nu+és → deh₂n̥wés).
    3. Ending-initial resonants are syllabic iff not adjacent to a vocalic
       segment (ph₂tér+ms → ph₂térm̥s; h₂ówi+m → h₂ówim).
    4. s+s → s across the junction (h₁és+si → h₁ési).
    """
    if has_accent(stem):
        ending = deaccent(ending)
    if stem and ending and stem[-1].base == "s" and ending[0].base == "s" and stem[-1].kind == "C":
        ending = ending[1:]
    out = list(stem)
    n = len(out)
    out += ending
    if not stem or not ending:
        return out

    # 2. stem-final syllabic before a vowel-initial ending
    if n < len(out) and out[n - 1].kind == "R" and out[n - 1].syl and not _fixed(out[n - 1]) \
            and out[n].vocalic:
        out[n - 1] = replace(out[n - 1], syl=False)
        i = n - 2
        while i >= 0 and out[i].kind == "R" and not out[i].syl:
            left_v = i > 0 and out[i - 1].vocalic
            right_v = out[i + 1].vocalic
            if left_v or right_v:
                break
            out[i] = replace(out[i], syl=True)
            i -= 1

    # 3. ending resonants, left to right within the initial resonant run
    i = n
    while i < len(out) and out[i].kind == "R" and not _fixed(out[i]):
        left_v = out[i - 1].vocalic
        right_v = i + 1 < len(out) and out[i + 1].vocalic
        out[i] = replace(out[i], syl=not (left_v or right_v))
        i += 1
    return out


def lengthen_last_vowel(segs: list[Seg]) -> list[Seg]:
    for i in range(len(segs) - 1, -1, -1):
        if segs[i].vocalic:
            return segs[:i] + [replace(segs[i], long=True)] + segs[i + 1:]
    return segs


def szemerenyi(segs: list[Seg]) -> list[Seg]:
    """-V(r|n|s)s# → -V̄(r|n|s)#, then -ōn#/-ēn# → -ō#/-ē# (n-stem nominative)."""
    if len(segs) >= 3 and segs[-1].base == "s" and segs[-2].base in ("r", "n", "s") \
            and not segs[-2].syl and segs[-3].kind == "V" and not segs[-3].long:
        out = segs[:-3] + [replace(segs[-3], long=True), segs[-2]]
        if out[-1].base == "n":
            out = out[:-1]
        return out
    return segs


def stang(segs: list[Seg]) -> list[Seg]:
    """-V w m# → -V̄ m# (dyéw-m → dyḗm, gʷów-m → gʷṓm)."""
    if len(segs) >= 3 and segs[-1].base == "m" and not segs[-1].syl and segs[-2].base == "w" \
            and not segs[-2].syl and segs[-3].kind == "V":
        return segs[:-3] + [replace(segs[-3], long=True), segs[-1]]
    return segs
