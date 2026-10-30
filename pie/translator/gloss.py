"""Readable word-by-word glosses for the translator (and the chat export's translation examples).

The corpus glosses name closed-class words by their table id (`personal/1-GEN.SG.ENCL`,
`demonstrative_so-ACC.SG`); readable() puts an English word in their place and keeps the grammatical tags:
`my-GEN.SG.ENCL`, `that-ACC.SG`. Pronouns of person take the English case form (I / me / my), so the gloss
reads without knowing the labels. Every other gloss word passes through unchanged.
"""
from __future__ import annotations

import re

# personal pronouns: (person, number) → English by case (NOM, ACC, GEN; every other case uses ACC's word)
_PERSONAL = {
    ("1", "SG"): ("I", "me", "my"), ("1", "PL"): ("we", "us", "our"), ("1", "DU"): ("we.two", "us.two", "our.two's"),
    ("2", "SG"): ("you", "you", "your"), ("2", "PL"): ("you.all", "you.all", "your.all's"),
    ("2", "DU"): ("you.two", "you.two", "your.two's"),
}
# other closed-class ids → English; a pair is (singular, plural)
CLOSED_EN = {
    "demonstrative_so": ("that", "those"),
    "anaphoric_i": ("he/she/it", "they"),
    "deictic_ki": ("this", "these"),
    "deictic_eno": ("that.yonder", "those.yonder"),
    "relative_yo": ("who/which", "who/which"),
    "interrogative_kwi": ("who?/what?", "who?/what?"),
    "indefinite_kwi": ("someone/something", "some"),
    "interrogative_kwo": ("which?", "which?"),
    "his/her/their.own.(reflexive.possessive)": ("own", "own"),
}
_NUMBERS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight",
            "9": "nine", "10": "ten", "100": "hundred", "1000": "thousand"}
_TAGS = re.compile(r"-(?=[A-Z0-9][A-Z0-9.]*$)")


def _word(lemma: str, tags: str) -> str:
    parts = tags.split(".") if tags else []
    num = next((p for p in parts if p in ("SG", "PL", "DU")), "SG")
    m = re.fullmatch(r"personal/([12])", lemma)
    if m:
        case = next((p for p in parts if p in ("NOM", "ACC", "GEN", "DAT", "ABL", "LOC", "INS", "VOC")), "NOM")
        nom, acc, gen = _PERSONAL[(m[1], num)]
        return nom if case in ("NOM", "VOC") else gen if case == "GEN" else acc
    if lemma in CLOSED_EN:
        sg, pl = CLOSED_EN[lemma]
        return pl if num == "PL" else sg
    m = re.fullmatch(r"numerals/(?:indeclinable/)?(\d+)", lemma)
    if m:
        return _NUMBERS.get(m[1], m[1])
    m = re.fullmatch(r"(?:interrogative|correlative|deictic)_adv/(\w+)", lemma)
    if m:
        w = m[1].replace("_", ".")
        return w + "?" if lemma.startswith("interrogative") else w
    return lemma


def readable_word(w: str) -> str:
    """One gloss word, clitics (=and) kept: personal/1-GEN.SG.ENCL → my-GEN.SG.ENCL."""
    out = []
    for part in w.split("="):
        bits = _TAGS.split(part, maxsplit=1)
        lemma, tags = (bits[0], bits[1]) if len(bits) == 2 else (part, "")
        new = _word(lemma, tags)
        out.append(new + ("-" + tags if tags else ""))
    return "=".join(out)


def readable(gloss: str | None) -> str | None:
    """A whole gloss line, word by word."""
    return None if gloss is None else " ".join(readable_word(w) for w in gloss.split())
