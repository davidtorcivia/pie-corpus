"""Canonical PIE → IPA, for speech synthesis. The conventions are in docs/pronunciation.md.

    to_ipa("h₂ówis h₁éḱwōs-kʷe")                 → "χó.wis héc.woːs.kʷe"
    to_ipa("ph₂tḗr", tone="stress")              → "pə.ˈteːr"
    to_ipa("h2o/wis", ascii=True, tone=False)    → "χo.wis"

Segmentation is pie.phon.parse, and syllable nuclei are pie.meter's (meter.word_nuclei), so a word has
exactly as many IPA syllables as meter counts. Nothing here re-derives syllabicity.

Syllable boundaries follow the rule pie.meter.weights assumes (the Vedic one): a single consonant between
nuclei begins the next syllable (V.CV); in a cluster the first consonant closes the syllable and the rest
begin the next (VC.CV, VC.CCV). A word-initial cluster is the first onset, a word-final one the last coda.

A Convention fixes the phonetic values. CONVENTIONS holds the named presets. The default one colors a short e
next to h₂/h₃ (h₂e → [χa], h₃e → [ɣʷo]), which is the biggest surface choice here; preset "uncolored" turns it
off.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, replace

from .meter import word_nuclei, words
from .phon import LARYNGEALS, Seg
from .translit import to_unicode

SYLLABIC = "̩"     # combining vertical line below: r̩ l̩ m̩ n̩
HIGH = "́"         # combining acute: IPA high tone
LONG = "ː"
STRESS = "ˈ"

_STOPS = {"p": "p", "b": "b", "bh": "bʱ", "t": "t", "d": "d", "dh": "dʱ",
          "kw": "kʷ", "gw": "ɡʷ", "gwh": "ɡʷʱ", "s": "s", "z": "z"}
DORSALS = {
    "palatal": {"k'": "c", "g'": "ɟ", "g'h": "ɟʱ", "k": "k", "g": "ɡ", "gh": "ɡʱ"},
    "fronted": {"k'": "kʲ", "g'": "ɡʲ", "g'h": "ɡʲʱ", "k": "k", "g": "ɡ", "gh": "ɡʱ"},
    # the uvular hypothesis: the written palatovelars are plain velars and the plain velars uvulars
    "uvular": {"k'": "k", "g'": "ɡ", "g'h": "ɡʱ", "k": "q", "g": "ɢ", "gh": "ɢʱ"},
    # ḱ ǵ ǵʰ said as plain velars (a centum-style merger): a speech choice for engines that hear [c ɟ] as
    # affricates (docs/research/tts-bakeoff.md), not a claim about PIE
    "plain": {"k'": "k", "g'": "ɡ", "g'h": "ɡʱ", "k": "k", "g": "ɡ", "gh": "ɡʱ"},
}
LARYNGEAL_VALUES = {
    "fricative": {"h1": "h", "h2": "χ", "h3": "ɣʷ"},      # default
    "pharyngeal": {"h1": "ʔ", "h2": "ħ", "h3": "ʕʷ"},
    "voiceless": {"h1": "h", "h2": "χ", "h3": "χʷ"},
}
# A vocalized (syllabic) laryngeal: the meter counts it as a short nucleus.
VOCALIZED = {
    "schwa": {"h1": "ə", "h2": "ə", "h3": "ə", "H": "ə"},              # default
    "colored": {"h1": "ə", "h2": "ɐ", "h3": "ɵ", "H": "ə"},            # after the Greek triple reflex e/a/o
}
_RESONANT = {"r": "r", "l": "l", "m": "m", "n": "n", "y": "j", "w": "w"}
_SYL_RESONANT = {"r": "r" + SYLLABIC, "l": "l" + SYLLABIC, "m": "m" + SYLLABIC, "n": "n" + SYLLABIC,
                 "y": "i", "w": "u"}
_COLOR = {"h2": "a", "h3": "o"}
# punctuation → prosodic break (IPA major / minor group); the rest of meter's non-word characters are dropped
_BREAK = {".": "‖", "?": "‖", "!": "‖", "…": "‖", ",": "|", ";": "|", ":": "|"}
_CHUNK = re.compile(r"([.?!…,;:])")


@dataclass(frozen=True)
class Convention:
    """Phonetic values for each segment class (docs/pronunciation.md)."""
    name: str = "default"
    laryngeals: str = "fricative"     # key of LARYNGEAL_VALUES
    generic: str | None = None        # IPA for consonantal H; None = the value of h₁
    dorsals: str = "palatal"          # key of DORSALS
    vocalized: str = "schwa"          # key of VOCALIZED, or "syllabic" (the laryngeal itself + ◌̩)
    coloring: bool = True             # short e next to h₂ → a, next to h₃ → o
    consonants: dict = field(default_factory=dict, compare=False, repr=False)

    def __post_init__(self):
        lar = dict(LARYNGEAL_VALUES[self.laryngeals])
        lar["H"] = self.generic or lar["h1"]
        if self.vocalized not in VOCALIZED and self.vocalized != "syllabic":
            raise ValueError(f"unknown vocalized laryngeal style {self.vocalized!r}")
        object.__setattr__(self, "consonants", {**_STOPS, **DORSALS[self.dorsals], **lar})

    def vocalized_laryngeal(self, base: str) -> str:
        if self.vocalized == "syllabic":
            c = self.consonants[base]
            return c[0] + SYLLABIC + c[1:]
        return VOCALIZED[self.vocalized][base]


CONVENTIONS = {
    "default": Convention(),
    "pharyngeal": Convention("pharyngeal", laryngeals="pharyngeal"),
    "uncolored": Convention("uncolored", coloring=False),
}


def _convention(c: str | Convention) -> Convention:
    if isinstance(c, Convention):
        return c
    try:
        return CONVENTIONS[c]
    except KeyError:
        raise ValueError(f"unknown convention {c!r}; known: {sorted(CONVENTIONS)}") from None


def color(segs: list[Seg]) -> list[Seg]:
    """Laryngeal coloring: a short e next to h₂ becomes a, next to h₃ becomes o (the preceding laryngeal
    decides when both neighbours are laryngeals). Long ē is not colored (Eichner's law); h₁ and H do not color."""
    out = list(segs)
    for i, s in enumerate(segs):
        if s.kind != "V" or s.base != "e" or s.long:
            continue
        prev = segs[i - 1].base if i > 0 else None
        nxt = segs[i + 1].base if i + 1 < len(segs) else None
        new = _COLOR.get(prev) or _COLOR.get(nxt)
        if new:
            out[i] = replace(s, base=new)
    return out


def _nucleus(s: Seg, conv: Convention, tone: bool) -> str:
    if s.base in LARYNGEALS:                       # a vocalized laryngeal: never accented, never long
        return conv.vocalized_laryngeal(s.base)
    if s.kind == "R":
        v = _SYL_RESONANT[s.base]
    else:
        v = s.base
    return v + (HIGH if tone and s.acc else "") + (LONG if s.long else "")


def _margin(s: Seg, conv: Convention) -> str:
    if s.kind == "R":
        return _RESONANT[s.base]
    if s.kind == "V":                              # cannot happen: every vowel is a nucleus
        raise ValueError(f"vowel {s.base!r} outside a nucleus")
    return conv.consonants[s.base]


def _split(segs: list[Seg], nuclei: list[int]) -> list[list[int]]:
    """Segment indices per syllable: V.CV, VC.C(C)V; edge clusters go to the first onset / last coda."""
    if not nuclei:
        return []
    bounds = [0]
    for a, b in zip(nuclei, nuclei[1:]):
        between = b - a - 1
        bounds.append(a + 1 if between <= 1 else a + 2)
    bounds.append(len(segs))
    return [list(range(x, y)) for x, y in zip(bounds, bounds[1:])]


def _word(word: str, conv: Convention, tone: bool | str) -> tuple[list[str], str]:
    """(syllables, rendering) of one word. A word without a nucleus has no syllables and is rendered
    as its bare consonants."""
    segs, nuclei = word_nuclei(word)
    if conv.coloring:
        segs = color(segs)
    nset = set(nuclei)
    acute = tone is True

    def seg(i: int) -> str:
        return _nucleus(segs[i], conv, acute) if i in nset else _margin(segs[i], conv)

    sylls = []
    for idx in _split(segs, nuclei):
        text = "".join(seg(i) for i in idx)
        if tone == "stress" and any(segs[i].acc for i in idx if i in nset):
            text = STRESS + text
        sylls.append(unicodedata.normalize("NFC", text))
    rendering = ".".join(sylls) if sylls else unicodedata.normalize("NFC", "".join(seg(i) for i in range(len(segs))))
    return sylls, rendering


def _check_tone(tone) -> None:
    if tone not in (True, False, "stress"):
        raise ValueError(f"tone must be True, False or 'stress', not {tone!r}")


def syllables(word: str, *, convention: str | Convention = "default", tone: bool | str = True,
              ascii: bool = False) -> list[str]:
    """The IPA syllables of one word (one per pie.meter nucleus; [] for a word with no nucleus)."""
    _check_tone(tone)
    if ascii:
        word = to_unicode(word)
    return _word(word, _convention(convention), tone)[0]


def to_ipa(text: str, *, convention: str | Convention = "default", tone: bool | str = True,
           ascii: bool = False, breaks: bool = True) -> str:
    """IPA for canonical PIE text (or its pie_ascii form with ascii=True).

    tone=True marks the accented nucleus with a high tone (acute); "stress" puts ˈ before the accented
    syllable instead; False marks nothing. Syllables are separated by ".", words by a space. With
    breaks=True, . ? ! become ‖ and , ; : become |. Raises ValueError on text the notation rejects."""
    _check_tone(tone)
    conv = _convention(convention)
    if ascii:
        text = to_unicode(text)
    out: list[str] = []
    for chunk in _CHUNK.split(text):
        if chunk in _BREAK:
            if breaks and out and out[-1] not in ("‖", "|"):
                out.append(_BREAK[chunk])
            elif breaks and out and _BREAK[chunk] == "‖":
                out[-1] = "‖"
            continue
        out += [_word(w, conv, tone)[1] for w in words(chunk)]
    return " ".join(out)


def respell(ipa: str, subst: dict[str, str]) -> str:
    """Converter IPA with whole phones replaced: one left-to-right pass over the NFD string, longest key first
    (so ɣʷ → ʁw wins over ʷ → w), replacements never re-scanned. Dots, accents and breaks pass through.
    pie.speak.Profile uses it for per-engine respellings."""
    if not subst:
        return ipa
    keys = sorted((unicodedata.normalize("NFD", k) for k in subst), key=len, reverse=True)
    table = {unicodedata.normalize("NFD", k): unicodedata.normalize("NFD", v) for k, v in subst.items()}
    pat = re.compile("|".join(re.escape(k) for k in keys))
    return unicodedata.normalize("NFC", pat.sub(lambda m: table[m.group(0)], unicodedata.normalize("NFD", ipa)))


# X-SAMPA, for engines that take ASCII phoneme codes. Applied to the NFD of to_ipa's output.
XSAMPA = {
    "p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "ɡ": "g", "c": "c", "ɟ": "J\\", "q": "q", "ɢ": "G\\",
    "s": "s", "z": "z", "h": "h", "ʔ": "?", "χ": "X", "ħ": "X\\", "ɣ": "G", "ʕ": "?\\",
    "m": "m", "n": "n", "r": "r", "l": "l", "j": "j", "w": "w",
    "a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "ə": "@", "ɐ": "6", "ɵ": "8",
    "ʷ": "_w", "ʲ": "'", "ʱ": "_t", LONG: ":", SYLLABIC: "=", HIGH: "_H", STRESS: "\"",
    ".": ".", " ": " ", "|": "|", "‖": "||",
}


def to_xsampa(ipa: str) -> str:
    """X-SAMPA for an IPA string from to_ipa (tone after length: é ː → e:_H)."""
    s = unicodedata.normalize("NFD", ipa).replace(HIGH + LONG, LONG + HIGH)
    try:
        return "".join(XSAMPA[ch] for ch in s)
    except KeyError as e:
        raise ValueError(f"no X-SAMPA for {e.args[0]!r} in {ipa!r}") from None
