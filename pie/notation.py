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


_SUBSCRIPT_DIGIT = {"1": "₁", "2": "₂", "3": "₃"}
_SUPERSCRIPT_DIGIT = {"¹": "₁", "²": "₂", "³": "₃"}

RULES: dict[str, Rule] = {
    r.id: r
    for r in [
        # --- generic -------------------------------------------------------
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
        Rule("G-NFC", "Unicode NFC", lambda s: unicodedata.normalize("NFC", s)),
        # --- profile -------------------------------------------------------
        Rule("P-ASP-PLAIN-H", "plain h after b d g ǵ gʷ (not a laryngeal) → ʰ (Mallory–Adams style *bher-)",
             _sub("([bdgǵ]|g" + LAB + ")h(?![₁₂₃ₓ])", "\\1" + ASP)),
        Rule("P-LAB-W-AFTER-K", "plain k g followed by w is a labiovelar (Hirt/older *kw-) → kʷ gʷ",
             _sub("([kg])w", "\\1" + LAB)),
        Rule("P-SCHWA", "ə (schwa indogermanicum) → H (generic laryngeal)",
             lambda s: s.replace("ə", "H")),
        Rule("P-V-W", "v (older notation for the glide) → w", lambda s: s.replace("v", "w")),
        Rule("P-J-Y", "j (older/German notation for the glide) → y", lambda s: s.replace("j", "y")),
        Rule("P-APOS-PAL", "palatal written k' g' (or k’) → ḱ ǵ",
             _sub("([kg])['’]", "\\1" + ACUTE)),
    ]
}

_GENERIC = ["G-NFC", "G-WS", "G-QUOTES", "G-ELLIPSIS", "G-LAR-DIGIT", "G-LAR-X", "G-CASE",
            "G-PAL-CIRC", "G-LAB-U", "G-GLIDE", "G-RING-ABOVE", "G-SYL-DOT",
            "G-MARK-ORDER", "G-NFC"]

# Source profiles: generic rules plus source-specific ones, applied in order.
# Profile rules run after G-NFC (so regexes see precomposed ḱ ǵ) and before
# the rest of the generic cleanup. Add a profile
# per source family as sources arrive, and log it in docs/notation.md.
PROFILES: dict[str, list[str]] = {
    "default": _GENERIC,
    "wiktionary": _GENERIC,
    "plain-h-aspirates": ["G-NFC", "P-ASP-PLAIN-H"] + _GENERIC,
    "schleicher-1868": ["G-NFC", "P-V-W", "P-J-Y"] + _GENERIC,
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
        t = RULES[rid].fn(s)
        if t != s:
            if rid not in applied:
                applied.append(rid)
            s = t
    return NormalizeResult(s, applied, is_canonical(s))
