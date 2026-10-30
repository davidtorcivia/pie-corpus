"""Where a PIE word comes from, for the translator's labels (owner, 2026-10-30): attested, inferred or coined.

No PIE word is attested itself; "attested" here means the standard reconstruction from attested daughter words.
- attested: a lexicon reconstruction whose reflexes (non-borrowed, non-analogical) are in at least two branches, a
  standard handbook reconstruction (NIL, LIV²), or a closed-class word from the handbook tables;
- inferred: our own project reconstruction (data/lexicon/project_reconstructions.jsonl), a reconstruction resting on
  one branch, or one whose meaning is inferred from its root and suffix rather than given by a dictionary;
- coined: a modern coinage (data/lexicon/neologisms.jsonl), built from inherited roots.
"""
from __future__ import annotations

import functools

from ..glosses import branch
from ..realize import Lexicon

LABELS = {
    "attested": "reconstructed from words attested in two or more daughter branches",
    "inferred": "inferred: one branch, our own reconstruction, or a meaning read from its root",
    "coined": "coined for modern use from inherited roots",
}


@functools.lru_cache(maxsize=1)
def _lexicon():
    from ..neologism import with_neologisms
    return with_neologisms(Lexicon.load())


def branches(entry: dict) -> set[str]:
    out = set()
    for lang, xs in (entry.get("reflexes") or {}).items():
        if any(not (x.get("borrowed") or x.get("analogical")) for x in xs):
            out.add(branch(lang))
    return out


@functools.lru_cache(maxsize=None)
def provenance(lex_id: str | None) -> str | None:
    """"attested" | "inferred" | "coined", or None for an unknown id."""
    if not lex_id or lex_id == "compound":
        return None
    if lex_id.startswith("closed:"):
        return "attested"
    lx = _lexicon()
    coined = lx.coined(lex_id)
    if coined == "neologism" or lex_id.startswith("pie-neo-"):
        return "coined"
    if coined == "project" or lex_id.startswith("pie-proj-"):
        return "inferred"
    e = lx.entries.get(lex_id)
    if e is None:
        return None
    if not e.get("meaning") or e.get("meaning_source") in ("derived",):
        return "inferred"
    # a standard handbook reconstruction (NIL's nominal formations, LIV²'s verb stems) counts as attested even
    # where the lexicon's own reflex list is thin
    if len(branches(e)) >= 2 or e.get("meaning_source") == "nil" or e.get("nil") or e.get("liv"):
        return "attested"
    return "inferred"
