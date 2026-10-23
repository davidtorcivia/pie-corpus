"""Classify crosscheck mismatches against Wiktionary into known causes.

Each detector recognizes one documented Wiktionary-module idiosyncrasy (see
docs/morphology.md). A mismatch no detector explains is "unexplained" and is
treated as a potential engine bug until triaged by hand.
"""

from __future__ import annotations

import collections
import re
import unicodedata

_FINAL_MOD = re.compile("[ʰʷ]$")
_LARYNGEAL = re.compile("h[₁₂₃]|H")


def _nfd(s):
    return unicodedata.normalize("NFD", s)


def _strip_final_mods(s: str) -> str:
    # bʰérǵʰ → bʰérǵ, h₃ókʷ → h₃ók, snígʷʰ → sníg
    return re.sub("[ʰʷ]+$", "", s)


def _drop_laryngeals(s: str) -> str:
    return _LARYNGEAL.sub("", s)


# Forms whose nominative is lexical, not derivable from the stem args (*ḱérd- → ḱḗr).
# Handled by a nom_sg override in the lexicon, not by a rule.
_LEXICAL = {"ḱḗr"}
_NUMERALS = {"tréyes", "kʷetwóres", "óynos", "dwóh₁", "pénkʷe", "swéḱs", "septḿ̥", "oḱtṓ", "h₁néwn̥", "déḱm̥"}


def _final_laryngeal_lengthening(s: str) -> str:
    m = re.match(r"^(.*?)([aeiou])(\u0301?)([rlmnwy]?)(?:h[₁₂₃]|H)$", _nfd(s))
    if not m:
        return s
    return unicodedata.normalize("NFC", m[1] + m[2] + "\u0304" + m[3] + m[4])


def classify(m: dict) -> str:
    w, e = set(m["wiktionary"]), set(m["engine"])
    if not e:
        return "engine-missing-cell"
    # numerals have special tables in Wiktionary; ours are hand tables (closed class)
    if m["form"] in _NUMERALS:
        return "numeral-hand-table"
    if m["form"] in _LEXICAL:
        return "lexical-exception"
    # final deaspiration / delabialization in bare (endingless) forms
    if all(x in w or _strip_final_mods(x) in w for x in e) and any(_strip_final_mods(x) != x for x in e - w):
        return "wikt-final-deaspiration"
    # final laryngeal loss with compensatory lengthening in bare forms (tetólh₂ → tetṓl, gʷénh₂ → gʷḗn)
    if all(x in w or _final_laryngeal_lengthening(x) in w for x in e) and any(x not in w for x in e):
        return "wikt-final-laryngeal-lengthening"
    # -imn- syllabified two ways across Wiktionary pages (h₂imn̥-és → h₂ym̥nés, but poh₂imnés)
    if any("ym̥n" in x for x in w) and any("imn" in x for x in e):
        return "wikt-inconsistent-syllabification"
    # Wiktionary drops a laryngeal its own stem args contain (Pinault's law, méǵh₂- → méǵ-)
    if w - e and ({_drop_laryngeals(x) for x in w} == {_drop_laryngeals(x) for x in e} or
                  all(any(_drop_laryngeals(y) == _drop_laryngeals(x) for y in e) for x in w - e)):
        return "wikt-laryngeal-dropped"
    # Wiktionary lists both a labialized and a delabialized variant (h₁ln̥gʷʰuyéh₂s / h₁ln̥gʰuyéh₂s)
    if e < w and any(re.sub("ʷ", "", x) != x and re.sub("ʷ", "", x) in w for x in w):
        return "wikt-inconsistent-delabialization"
    # partial table: Wiktionary shows a subset (missing genders or second template)
    if w < e:
        return "wikt-subset"
    return "unexplained"


def summarize(mismatches: list[dict]) -> dict:
    by = collections.defaultdict(list)
    for m in mismatches:
        by[classify(m)].append(m)
    return by
