"""Lexicon hints for a language model translating English into PIE: the project's word for each English content word,
looked up the way the transfer translator does (Transfer.lookup: the word, a synonym, a derivational base; LexMap's
ranking and OVERRIDES), so the model chooses and inflects a given lemma instead of recalling a rare one.

    from pie.translator.hints import hints, hint_line
    hint_line(hints("The king wanted a son."))
    # 'Lexicon: king = h₃rḗḱs (noun, m.); want = wélh₁ti (verb); son = suHnús (noun, m.)'

Only nouns, verbs and adjectives are looked up (pronouns, particles and numbers the model knows); words of the
prompt's instruction ("Translate this into Proto-Indo-European") and PIE words in a mixed prompt are skipped.
"""
from __future__ import annotations

import functools
import re

FAMILIES = {"NOUN": ("noun",), "PROPN": ("noun",), "VERB": ("verb",), "ADJ": ("adj",)}
# instruction words of the benchmark's and the SFT export's prompts, never part of the sentence to translate
INSTRUCTION = {"translate", "render", "reply", "answer", "respond", "write", "put", "reconstruct",
               "reconstructed", "proto", "indo", "european", "proto-indo-european", "pie", "english", "language",
               "please", "sentence", "following", "convention", "handbook",
               "be", "have", "do"}      # light verbs: PIE says "to me is" for have; the model knows the copula
_PIE_CHARS = re.compile(r"[₁₂₃ʰʷḱǵ̥]")


@functools.lru_cache(maxsize=1)
def _transfer():
    from .transfer import Transfer
    return Transfer()


def hints(english: str, limit: int = 12) -> list[dict]:
    from .transfer import nlp
    tr = _transfer()
    out, seen = [], set()
    doc = nlp()(english)
    for t in doc:
        fams = FAMILIES.get(t.pos_)
        # a part of a hyphenated compound (daughter-in-law): its parts alone would mislead
        joined = (t.i + 1 < len(doc) and not t.whitespace_ and doc[t.i + 1].text == "-") or \
                 (t.i > 0 and doc[t.i - 1].text == "-" and not doc[t.i - 1].whitespace_)
        if joined:
            continue
        lem = t.lemma_.lower()
        if not fams or not t.is_alpha or lem in INSTRUCTION or lem in seen or _PIE_CHARS.search(t.text):
            continue
        seen.add(lem)
        lid, fam = tr.lookup(t, fams, [])
        if not lid:
            continue
        e = tr.lx.entries.get(lid, {})
        out.append({"english": lem, "lex_id": lid, "form": e.get("form", "").strip("*"), "family": fam,
                    "gender": tr.lx.gender(lid) if fam == "noun" else None})
        if len(out) >= limit:
            break
    return out


def hint_line(hs: list[dict]) -> str:
    if not hs:
        return ""
    parts = [f"{h['english']} = {h['form']} ({h['family']}{', ' + h['gender'] + '.' if h['gender'] else ''})"
             for h in hs]
    return "Lexicon: " + "; ".join(parts)
