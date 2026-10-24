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
LARYNGEALS = {"h1", "h2", "h3", "H"}
_LABIOVELAR = {"kw": "k", "gw": "g", "gwh": "gh"}


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
    5. A stem-final consonantal resonant between non-vocalic segments becomes
       syllabic (gʷʰn+h₂ér → gʷʰn̥h₂ér).
    """
    if has_accent(stem):
        ending = deaccent(ending)
    if stem and ending and stem[-1].base in _LABIOVELAR and ending[0].base == "w" and not ending[0].syl:
        stem = stem[:-1] + [Seg(_LABIOVELAR[stem[-1].base], "C")]   # kʷ-w → kw (linkʷ-wós → linkwós)
    if stem and ending and stem[-1].base == "s" and ending[0].base == "s" and stem[-1].kind == "C":
        ending = ending[1:]
    out = list(stem)
    n = len(out)
    out += ending
    if not stem or not ending:
        return out

    # 2. stem-final syllabic before a vowel-initial ending. (A full rightmost-first
    #    re-syllabification of the run was tried and rejected: Wiktionary keeps
    #    poh₂imn̥+és → poh₂imnés; see docs/morphology.md.)
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

    # 2b. stem-final consonantal resonant before a vocalic ending: a consonantal resonant before it, between
    #     non-vocalic segments, becomes syllabic (h₂ḱmn+és → h₂ḱm̥nés, as Ringe 2006 §2.3.4 h₁n̥h₃m̥nés;
    #     engine sweep, r-n-stems.md defect 1)
    if n >= 3 and n < len(out) and out[n - 1].kind == "R" and not out[n - 1].syl and out[n].vocalic \
            and out[n - 2].kind == "R" and not out[n - 2].syl and not _fixed(out[n - 2]) \
            and not out[n - 3].vocalic:
        out[n - 2] = replace(out[n - 2], syl=True)

    # 3. ending resonants, left to right within the initial resonant run
    i = n
    while i < len(out) and out[i].kind == "R" and not _fixed(out[i]):
        left_v = out[i - 1].vocalic
        right_v = i + 1 < len(out) and out[i + 1].vocalic
        out[i] = replace(out[i], syl=not (left_v or right_v))
        i += 1

    # 5. a stem-final consonantal resonant between non-vocalic segments becomes syllabic,
    #    after the ending's own resonants are settled (right to left): gʷʰn+h₂ér → gʷʰn̥h₂ér,
    #    gʷʰn+tór → gʷʰn̥tór, but gʷʰn+n̥tór stays gʷʰnn̥tór
    j = n - 1
    if j > 0 and out[j].kind == "R" and not out[j].syl and not _fixed(out[j]) and not out[n].vocalic \
            and not out[j - 1].vocalic:          # (a bare infix -n- has no left neighbour: left alone)
        out[j] = replace(out[j], syl=True)
    return out


def lengthen_last_vowel(segs: list[Seg]) -> list[Seg]:
    for i in range(len(segs) - 1, -1, -1):
        if segs[i].vocalic:
            return segs[:i] + [replace(segs[i], long=True)] + segs[i + 1:]
    return segs


def szemerenyi(segs: list[Seg]) -> list[Seg]:
    """-V(r|n|m|l|s)s# → -V̄R# (ph₂tḗr, dʰéǵʰōm, gʰébʰōl); then -ōn# → -ō# (ḱwṓ, but bʰudʰmḗn)."""
    if len(segs) >= 3 and segs[-1].base == "s" and segs[-2].base in ("r", "n", "m", "l", "s") \
            and not segs[-2].syl and segs[-3].kind == "V" and not segs[-3].long:
        out = segs[:-3] + [replace(segs[-3], long=True), segs[-2]]
        if out[-1].base == "n" and out[-2].base == "o":
            out = out[:-1]
        return out
    return segs


def contract_eh2m(segs: list[Seg]) -> list[Seg]:
    """-eh₂m# → -ām# (Wiktionary convention: *bʰéh₂-m → bʰā́m*, eh₂-stem acc. *-ām*)."""
    if len(segs) >= 3 and segs[-1].base == "m" and segs[-2].base == "h2" and segs[-3].base == "e" \
            and segs[-3].kind == "V":
        return segs[:-3] + [Seg("a", "V", long=True, acc=segs[-3].acc), Seg("m", "R")]
    return segs


def zero_grade_suffix(segs: list[Seg]) -> list[Seg]:
    """Weak stem -éy/-éw → accented syllabic -í/-ú (proterokinetic oblique plural:
    bʰeh₂ǵʰéw- → bʰeh₂ǵʰú-). Returns segs unchanged if the stem has no such suffix."""
    if len(segs) >= 2 and segs[-1].kind == "R" and segs[-1].base in ("y", "w") and not segs[-1].syl \
            and segs[-2].base == "e" and segs[-2].acc:
        return segs[:-2] + [Seg(segs[-1].base, "R", syl=True, acc=True)]
    return segs


def stang(segs: list[Seg]) -> list[Seg]:
    """-V(w|y|m)m# → -V̄m# (dyéw-m → dyḗm, gʷów-m → gʷṓm, h₁éy-m → h₁ḗm, dʰéǵʰom-m → dʰéǵʰōm)."""
    # The final m may already be syllabic from junction syllabification (dyéw+m → dyéwm̥).
    if len(segs) >= 3 and segs[-1].base == "m" and segs[-2].base in ("w", "y", "m") \
            and not segs[-2].syl and segs[-3].kind == "V":
        return segs[:-3] + [replace(segs[-3], long=True), Seg("m", "R")]
    return segs


def pinault(segs: list[Seg]) -> list[Seg]:
    """Pinault's law, C H y → C y (wérh₁ye- → wérye-). Debated; Wiktionary convention only."""
    out = list(segs)
    i = 1
    while i < len(out) - 1:
        if out[i].base in LARYNGEALS and out[i + 1].base == "y" and not out[i + 1].syl \
                and not out[i - 1].vocalic:
            del out[i]
        else:
            i += 1
    return out


def junction_laryngeal_loss(stem: list[Seg], ending: list[Seg]) -> list[Seg]:
    """Perfect stem-final R H before a consonant-initial ending loses H
    (tetólh₂-th₂e → tetólth₂e, bʰebʰóyh₂-h₂e → bʰebʰóyh₂e). Wiktionary's module
    does this in the perfect only (bʰh₂-wós, HréwdH-mi keep H). Wiktionary convention only."""
    if len(stem) >= 2 and stem[-1].base in LARYNGEALS and stem[-2].kind == "R" and not stem[-2].syl \
            and ending and not ending[0].vocalic:
        return stem[:-1]
    return stem


def delabialize(segs: list[Seg], before_u: bool = True) -> list[Seg]:
    """Boukólos rule as Wiktionary's module applies it: a labiovelar loses
    labialization after consonantal w (wéwkʷe- → wéwke-), before consonantal w
    (linkʷ-wós → linkwós), or before unaccented u (ḱm̥tógʷu- → ḱm̥tógu-). It is
    kept after u (lúkʷos) and before accented ú (pr̥kʷúmos). Applied to whole forms.
    before_u=False drops the before-syllabic-u clause (handbook thematic/eh₂ declension: M&A *pérkʷunos)."""
    out = list(segs)
    for i, x in enumerate(out):
        if x.base in _LABIOVELAR:
            prev_w = i > 0 and out[i - 1].base == "w" and not out[i - 1].syl
            nxt = out[i + 1] if i + 1 < len(out) else None
            next_w = nxt is not None and nxt.base == "w" and (not nxt.syl or (before_u and not nxt.acc))
            if prev_w or next_w:
                out[i] = Seg(_LABIOVELAR[x.base], "C")
    return out
