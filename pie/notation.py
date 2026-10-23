"""Normalization of foreign notations into the canonical inventory.

Every rewrite is a named rule (see RULES); docs/notation.md logs each one
with its rationale. normalize() returns the rules that actually fired, so a
record can say exactly how its `pie` was derived from its `source_form`.

Normalization is notational only. It maps symbols, and never modernizes a
reconstruction: Schleicher's *avis akvāsas ka* becomes *awis akwāsas ka*, not
*h₂ówis h₁éḱwōs-kʷe*.

Rules come in two kinds:
  - generic: safe for any source, because the input symbol has no other
    reading in IE notation; always applied by the "default" profile.
  - profile: only correct for sources that use a given convention (plain-h
    aspirates, ə for laryngeals, ...); opted into by a named source profile.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Callable

from .translit import ACUTE, ASP, LAB, MACRON, RING, is_canonical

__all__ = ["Rule", "RULES", "PROFILES", "normalize", "NormalizeResult"]


@dataclass(frozen=True)
class Rule:
    id: str
    summary: str
    fn: Callable[[str], str]


def _sub(pattern: str, repl: str, flags: int = 0) -> Callable[[str], str]:
    rx = re.compile(pattern, flags)
    return lambda s: rx.sub(repl, s)


def _nfd(fn: Callable[[str], str]) -> Callable[[str], str]:
    """Run fn on the NFD form, so marks are separate code points."""
    return lambda s: unicodedata.normalize("NFC", fn(unicodedata.normalize("NFD", s)))


_LARYNGEAL_DIGITS = set("₁₂₃123")


def _lowercase_keep_H(s: str) -> str:
    # `H` alone is the generic laryngeal and must survive; `H₂` is a
    # capitalized h₂ (sentence-initial) and is lowered like any other letter.
    out = []
    for i, c in enumerate(s):
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if c == "H" and nxt not in _LARYNGEAL_DIGITS:  # a set: "" in "₁₂₃" is True
            out.append(c)
        else:
            out.append(c.lower())
    return "".join(out)


# Applied to NFD text, so accented Greek letters arrive as base + U+0301 and
# only base letters need mapping. None of these letters is valid PIE notation.
_HOMOGLYPHS = str.maketrans({
    # Greek
    "ο": "o", "α": "a", "ε": "e", "ι": "i", "υ": "u",
    # Cyrillic
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "у": "y", "х": "x", "і": "i", "ј": "j",
})

_SUBSCRIPT_DIGIT = {"1": "₁", "2": "₂", "3": "₃"}
_SUBSUP = {"b": {"1": "₁", "2": "₂", "3": "₃", "4": "₄", "x": "ₓ", "a": "\u2090"},
           "p": {"h": ASP, "w": LAB}}
_SUPERSCRIPT_DIGIT = {"¹": "₁", "²": "₂", "³": "₃"}

RULES: dict[str, Rule] = {
    r.id: r
    for r in [
        # --- generic -------------------------------------------------------
        Rule("G-HTML-SUBSUP", "HTML <sub>/<sup> markup → Unicode (h<sub>1</sub> → h₁, k<sup>w</sup> → kʷ, <sub>x</sub> → ₓ)",
             lambda s: re.sub(r"<su([bp])>([^<]*)</su[bp]>",
                              lambda m: "".join(_SUBSUP[m[1]].get(c, c) for c in m[2]), s)),
        Rule("G-WS", "trim and collapse runs of whitespace to one space",
             lambda s: " ".join(s.split())),
        Rule("G-MARK-ORDER", "acute+macron on one base → macron+acute (ḗ, not é\u0304)",
             _nfd(_sub(ACUTE + MACRON, MACRON + ACUTE))),
        Rule("G-RING-ABOVE", "ring above (U+030A) on r l m n → ring below (U+0325)",
             _nfd(_sub("([rlmn])((?:[\u0300-\u036f])*)\u030a", "\\1" + RING + "\\2"))),
        Rule("G-SYL-DOT", "dot below on r l m n (ṛ ḷ ṃ ṇ) → ring below (r\u0325 l\u0325 m\u0325 n\u0325)",
             _nfd(_sub("([rlmn])((?:[\u0300-\u036f])*)\u0323", "\\1" + RING + "\\2"))),
        Rule("G-PAL-CIRC", "circumflex or inverted breve above on k g (k\u0302 ĝ k\u0311 g\u0311) → acute (ḱ ǵ)",
             _nfd(_sub("([kg])[\u0302\u0311]", "\\1" + ACUTE))),
        Rule("G-GLIDE", "non-syllabic i\u032f u\u032f (inverted breve below) → y w",
             _nfd(lambda s: s.replace("i\u032f", "y").replace("u\u032f", "w"))),
        Rule("G-LAB-U", "superscript u (\u1d58, \u1d58\u032f) or modifier capital W (\u1d42) after k g → ʷ",
             _sub("([kg])[\u1d58\u1d42]\u032f?", "\\1" + LAB)),
        Rule("G-LAR-DIGIT", "laryngeal written with ASCII or superscript digit (h2, h²) → subscript (h₂)",
             lambda s: re.sub(r"([hH])([123¹²³])",
                              lambda m: m[1] + _SUBSCRIPT_DIGIT.get(m[2], _SUPERSCRIPT_DIGIT.get(m[2], m[2])), s)),
        Rule("G-LAR-X", "hₓ / Hₓ (laryngeal of unknown color) → H",
             _sub("[hH]ₓ", "H")),
        Rule("G-CASE", "lowercase, except generic laryngeal H (H₂ → h₂ but H stays)",
             _lowercase_keep_H),
        Rule("G-QUOTES", "typographic double quotes “ ” „ « » → \"",
             _sub("[“”„«»]", '"')),
        Rule("G-ELLIPSIS", "… → ...", lambda s: s.replace("…", "...")),
        Rule("G-HOMOGLYPH", "Greek/Cyrillic look-alike letters → Latin (ό → ó, Cyrillic е → e)",
             _nfd(lambda s: s.translate(_HOMOGLYPHS))),
        Rule("G-LAR-RING", "ring below on a laryngeal (h̥₁, vocalized) → plain (h₁); syllabicity is re-derived",
             _nfd(_sub("([hH])̥", "\\1"))),
        Rule("G-MOD-ORDER", "aspiration before labialization (gʰʷ) → canonical order (gʷʰ)",
             lambda s: s.replace(ASP + LAB, LAB + ASP)),
        Rule("G-NFC", "Unicode NFC", lambda s: unicodedata.normalize("NFC", s)),
        # --- profile -------------------------------------------------------
        Rule("P-ASP-PLAIN-H", "plain h after b d g (with any palatal mark or ʷ), not a laryngeal → ʰ (Mallory–Adams style *bher-)",
             _nfd(_sub("([bdg][\u0300-\u036f]*" + LAB + "?)h(?![₁₂₃ₓ\u2090₄123x])", "\\1" + ASP))),
        Rule("P-LAB-W-AFTER-K", "plain k g followed by w is a labiovelar (Hirt/older *kw-) → kʷ gʷ",
             _sub("([kg])w", "\\1" + LAB)),
        Rule("P-SCHWA", "ə (schwa indogermanicum) → H (generic laryngeal)",
             lambda s: s.replace("ə", "H")),
        Rule("P-V-W", "v (older notation for the glide) → w", lambda s: s.replace("v", "w")),
        Rule("P-J-Y", "j (older/German notation for the glide) → y", lambda s: s.replace("j", "y")),
        Rule("P-APOS-PAL", "palatal written k' g' (or k’), and gh' → ḱ ǵ ǵʰ",
             lambda s: re.sub("([kg])['’]", "\\1" + ACUTE, re.sub("([kg])h['’]", "\\1" + ACUTE + ASP, s))),
        Rule("P-H-BARE", "bare h that is neither aspiration nor numbered (laryngeal of unknown color) → H",
             _sub("(?<![bdgǵʷ\u0301])h(?![₁₂₃ₓʰ123])", "H")),
        Rule("P-H4", "h₄ and hₐ (Adams's fourth / a-coloring laryngeal) → H",
             _sub("[hH][₄\u2090]", "H")),
        Rule("P-CARET-SUP", "superscript written with a caret (EPUB <sup> flattened): g^w → gʷ, b^h → bʰ",
             lambda s: s.replace("^w", LAB).replace("^h", ASP)),
        Rule("P-HX-ASCII", "ASCII hx (laryngeal of unknown color) → H", _sub("[hH]x", "H")),
        Rule("P-SPACING-RING", "spacing ring after a resonant (r˚ l˚ m˚ n˚) → syllabic (r̥ l̥ m̥ n̥)",
             _sub("([rlmn])[\u02da\u00b0]", "\\1" + RING)),
        Rule("P-SPACING-DIACRITICS", "spacing macron/acute after a vowel or resonant (e¯´ → ḗ, e´ → é)",
             lambda s: re.sub("([aeiourlmn\u0325]+?)([\u00af\u00b4]+)",
                              lambda m: m[1] + m[2].replace("\u00af", MACRON).replace("\u00b4", ACUTE), s)),
        Rule("P-DASH", "em/en dash used as punctuation → comma",
             lambda s: re.sub(r"\s*[—–]\s*", ", ", s)),
    ]
}

_GENERIC = ["G-NFC", "G-HTML-SUBSUP", "G-WS", "G-HOMOGLYPH", "G-QUOTES", "G-ELLIPSIS", "G-LAR-DIGIT", "G-LAR-X",
            "G-LAR-RING", "G-CASE",
            "G-PAL-CIRC", "G-LAB-U", "G-GLIDE", "G-RING-ABOVE", "G-SYL-DOT",
            "G-MARK-ORDER", "G-MOD-ORDER", "G-NFC"]

# Source profiles: generic rules plus source-specific ones, applied in order.
# Profile rules run after G-NFC (so regexes see precomposed ḱ ǵ) and before
# the rest of the generic cleanup. Add a profile
# per source family as sources arrive, and log it in docs/notation.md.
# Profile rules run after H-safe lowercasing, so a sentence-initial capital
# (K'erd, Jégeswo, Bher-) gets the same treatment as lowercase.
_PRE = ["G-NFC", "G-HTML-SUBSUP", "G-CASE"]

PROFILES: dict[str, list[str]] = {
    "default": _GENERIC,
    "wiktionary": _GENERIC,
    "plain-h-aspirates": _PRE + ["P-ASP-PLAIN-H"] + _GENERIC,
    "schleicher-1868": _PRE + ["P-V-W", "P-J-Y", "P-ASP-PLAIN-H"] + _GENERIC,
    # Tier 1 source profiles (docs/notation.md §Profiles). Profile rules run in order.
    "hirt-1939": _PRE + ["P-J-Y", "P-APOS-PAL", "P-ASP-PLAIN-H", "P-SCHWA"] + _GENERIC,
    "lehmann-zgusta-1979": _PRE + ["P-ASP-PLAIN-H", "P-H-BARE", "P-SCHWA"] + _GENERIC,
    "danka-1986": _PRE + ["P-J-Y", "P-APOS-PAL", "P-ASP-PLAIN-H", "P-SCHWA", "P-DASH"] + _GENERIC,
    "adams-1997": _PRE + ["P-H4", "P-ASP-PLAIN-H"] + _GENERIC,
    "luhr-2008": _PRE + ["P-J-Y", "P-APOS-PAL"] + _GENERIC,
    "voyles-barrack-2009": _PRE + ["P-J-Y"] + _GENERIC,
    # Reference books (raw/books/); digits and hx are resolved before plain-h aspiration
    "fortson": _PRE + ["P-CARET-SUP", "G-LAR-DIGIT", "P-ASP-PLAIN-H"] + _GENERIC,
    "mallory-adams": _PRE + ["P-HX-ASCII", "G-LAR-DIGIT", "P-ASP-PLAIN-H", "P-SCHWA"] + _GENERIC,
    "west": _PRE + ["P-SPACING-RING"] + _GENERIC,
    "ringe": _PRE + ["P-SPACING-DIACRITICS", "P-SPACING-RING", "G-LAR-DIGIT", "P-ASP-PLAIN-H"] + _GENERIC,
}


@dataclass
class NormalizeResult:
    text: str
    applied: list[str]
    canonical: bool


def normalize(text: str, profile: str = "default") -> NormalizeResult:
    """Apply a profile's rules in order; report which rules changed the text."""
    applied: list[str] = []
    s = text
    for rid in PROFILES[profile]:
        # NFC after every rule, so later regexes see precomposed ḱ ǵ
        t = unicodedata.normalize("NFC", RULES[rid].fn(s))
        if t != s:
            if rid not in applied:
                applied.append(rid)
            s = t
    return NormalizeResult(s, applied, is_canonical(s))
