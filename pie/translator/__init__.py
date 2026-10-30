"""The translator app's engine: English ↔ PIE without a language model (owner, 2026-10-30).

English → PIE, per sentence:
1. translation memory (memory.py): the corpus's own reviewed sentence pairs; a match scoring at least MEMORY_ACCEPT
   is used as it stands;
2. otherwise transfer (transfer.py): spaCy parses the English, the rules build a plan in the planners' format,
   and the engine (pie.realize) builds the PIE, so every form is grammatical by construction.
PIE → English: the inverse form index (analyze.py) gives each word its lexeme and features; the English is the
glosses in PIE order (a rough reading, marked as such), plus the memory's English when the PIE is a corpus sentence.

Every answer carries a readable word-by-word gloss (gloss.py), the IPA (pie.ipa), where it came from (memory or
rules) and notes on anything left out.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

MEMORY_ACCEPT = 0.92


@dataclass
class Sentence:
    english: str
    pie: str | None
    gloss: str | None
    ipa: str | None
    source: str                 # "memory" (with the corpus record id) or "rules"
    source_id: str | None = None
    score: float | None = None
    unknown: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _ipa(pie: str | None) -> str | None:
    if not pie:
        return None
    from ..ipa import to_ipa
    try:
        return to_ipa(pie)
    except Exception:
        return None


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]


def english_to_pie(text: str) -> list[dict]:
    from .gloss import readable
    from .memory import Memory
    mem = Memory.load()
    out = []
    transfer = None
    for s in split_sentences(text):
        hits = mem.search(s, k=1)
        if hits and hits[0][0] >= MEMORY_ACCEPT:
            score, p = hits[0]
            out.append(Sentence(s, p.pie, readable(p.gloss), _ipa(p.pie), "memory", p.source_id, score))
            continue
        if transfer is None:
            from .transfer import Transfer
            transfer = Transfer()
        r = transfer.translate(s)
        notes = r.notes + [f"could not build: {e}" for e in r.errors]
        out.append(Sentence(s, r.pie, readable(r.gloss), _ipa(r.pie), "rules", None, None, r.unknown, notes))
    return [asdict(x) for x in out]


def pie_to_english(text: str) -> dict:
    from .analyze import Analyzer
    from .memory import Memory
    an = Analyzer.load()
    words = an.analyze(text)
    rough = []
    for w in words:
        if w["analyses"]:
            a = w["analyses"][0]
            rough.append(a.gloss().split("-")[0].replace(".", " ") if a.features else a.english.replace(".", " "))
        else:
            rough.append(f"[{w['form']}]")
        if w["clitic"]:
            rough.append(w["clitic"][1])
    mem = Memory.load()
    exact = next((p for p in mem.pairs if p.pie.strip() == text.strip()), None)
    return {"pie": text, "ipa": _ipa(text),
            "words": [{"word": w["word"], "match": w["match"], "clitic": w["clitic"],
                       "analyses": [{"lex_id": a.lex_id, "lemma": a.lemma, "features": a.features, "gloss": a.gloss(),
                                     "pos": a.pos} for a in w["analyses"][:6]]} for w in words],
            "rough_english": " ".join(rough),
            "memory": {"english": exact.english, "source_id": exact.source_id} if exact else None}
