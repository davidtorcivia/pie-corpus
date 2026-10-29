"""A missing headword accent supplied from the lexeme's own accented Vedic or Greek reflex (docs/morphology.md
"Accent from a Vedic or Greek reflex").

A missing accent is missing information, so it is supplied only from evidence. The evidence here is the lexeme's
own reflex (its Wiktionary descendant tree, data/lexicon/lexicon.jsonl reflexes), and only when the correspondence
is regular:

  * the language is Ancient Greek or Sanskrit with a written accent (a Vedic accent in the romanization); no
    reconstructed form (*…), borrowing or analogical form;
  * the shape class has an accent-faithful reflex type: thematic nouns and adjectives (-os/-om : Gk -ος/-ον,
    Ved. -a-), eh₂-stems (-eh₂ : Gk -ᾱ/-η/-α, Ved. -ā), thematic presents (-eti : Ved. -ati only; Greek finite
    verbs have recessive accent and say nothing);
  * the reflex has as many syllables as the PIE form, so the accented syllable is the same one counted from the
    end;
  * in a Greek word of three or more syllables, an antepenult accent is the recessive position (compounds such
    as ἄσπετος, βλάσφημος are recessive by rule), and a penult accent before a long final may come from the law
    of limitation; neither is used. Final accents, penult accents before a short final, and disyllables are;
  * every usable reflex agrees on the position; Greek and Vedic disagreeing gives nothing.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

from .phon import has_accent, parse, render

LANGS = {"Ancient Greek": "greek", "Sanskrit": "vedic", "Vedic Sanskrit": "vedic"}
# shape rule -> (reflex endings allowed, by language); romanized, accents stripped
ENDINGS = {
    "shape:thematic": {"greek": ("os", "on"), "vedic": ("a", "as", "am")},
    "shape:thematic-adj": {"greek": ("os",), "vedic": ("a", "as")},
    "shape:thematic-neuter": {"greek": ("on",), "vedic": ("a", "am")},
    "shape:thematic-neuter-reflex": {"greek": ("on",), "vedic": ("a", "am")},
    "shape:eh2": {"greek": ("a", "ā", "ē"), "vedic": ("ā",)},
    "shape:thematic-present": {"vedic": ("ati",)},
}
_ACC = {"́", "̂", "͂"}            # acute, circumflex (Latin and Greek perispomeni)
_VOWELS = {"greek": "aeiouyāēīōū", "vedic": "aeiouāīūṛṝḷ"}
_DIPH = {"greek": ("ai", "ei", "oi", "ui", "au", "eu", "ou", "ēu"), "vedic": ("ai", "au")}
_LONG_FINAL = ("ā", "ē", "ī", "ō", "ū", "ei", "ou", "au", "eu", "ēu")


def _syllables(roman: str, kind: str) -> tuple[list[str], int | None] | None:
    """(nuclei, index of the accented nucleus) of a romanized word, or None if it is not a plain word."""
    d = unicodedata.normalize("NFD", roman.strip().lower())
    if not d or not re.fullmatch(r"[a-zāēīōūṛṝḷṃḥśṣṇṭḍñṅ̀-ͯ]+", d):
        return None
    chars: list[tuple[str, bool]] = []          # base letter (NFC with macron/dot kept), accented?
    for ch in d:
        if unicodedata.combining(ch):
            if ch in _ACC and chars:
                chars[-1] = (chars[-1][0], True)
            elif ch in ("̄", "̣") and chars:          # macron, dot below: part of the letter
                chars[-1] = (unicodedata.normalize("NFC", chars[-1][0] + ch), chars[-1][1])
            elif ch == "̈" and chars:                       # diaeresis: hiatus, mark it
                chars[-1] = (chars[-1][0] + "|", chars[-1][1])
            continue                                             # breve, grave …: ignored
        chars.append((ch, False))
    vow = _VOWELS[kind]
    nuclei, acc, i = [], None, 0
    while i < len(chars):
        c, a = chars[i]
        base = c.rstrip("|")
        if base in vow:
            nxt = chars[i + 1] if i + 1 < len(chars) else None
            if nxt and not c.endswith("|") and not nxt[0].endswith("|") and base + nxt[0] in _DIPH[kind]:
                nuclei.append(base + nxt[0])
                if a or nxt[1]:
                    acc = len(nuclei) - 1
                i += 2
                continue
            nuclei.append(base)
            if a:
                acc = len(nuclei) - 1
        i += 1
    return nuclei, acc


def _plain(roman: str) -> str:
    d = unicodedata.normalize("NFD", roman.lower())
    return unicodedata.normalize("NFC", "".join(c for c in d if c not in _ACC and c not in ("̆", "̀")))


def position(form: str, rule: str, reflexes: dict) -> tuple[int, list[dict]] | None:
    """(accented nucleus counted from the end, 1 = last; the reflexes used) for an unaccented PIE form, or None."""
    if rule not in ENDINGS or has_accent(parse(form.strip("-"))):
        return None
    n_pie = sum(1 for s in parse(form) if s.vocalic)
    votes, used = set(), []
    for lang, xs in reflexes.items():
        kind = LANGS.get(lang)
        if kind is None or kind not in ENDINGS[rule]:
            continue
        for x in xs:
            roman = x.get("roman") or (x["form"] if kind == "greek" and x["form"].isascii() else None)
            if not roman or x["form"].startswith("*") or x.get("borrowed") or x.get("analogical") or \
                    roman[:1].isupper():                   # a reconstruction, loan, or name (Νεμέα)
                continue
            if not _plain(roman).endswith(ENDINGS[rule][kind]):
                continue
            syl = _syllables(roman, kind)
            if syl is None:
                continue
            nuclei, acc = syl
            if acc is None or len(nuclei) != n_pie:
                continue
            from_end = len(nuclei) - acc
            if kind == "greek" and len(nuclei) >= 3 and (from_end >= 3 or nuclei[-1] in _LONG_FINAL and from_end == 2):
                continue      # the recessive position, or one the law of limitation may have produced
            votes.add(from_end)
            used.append({"lang": lang, "form": x["form"], "roman": roman})
    if len(votes) != 1:
        return None
    return votes.pop(), used


def accented(form: str, from_end: int) -> str:
    segs = parse(form)
    idx = [i for i, s in enumerate(segs) if s.vocalic]
    k = idx[len(idx) - from_end]
    segs[k] = replace(segs[k], acc=True)
    return render(segs)
