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
    words: list[dict] = field(default_factory=list)     # {form, gloss, status}: attested / inferred / coined


def _ipa(pie: str | None) -> str | None:
    if not pie:
        return None
    from ..ipa import to_ipa
    try:
        return to_ipa(pie)
    except Exception:
        return None


def _words(pie: str | None, gloss: str | None, lex_ids: list | None) -> list[dict]:
    from .provenance import provenance
    if not pie:
        return []
    forms = pie.split()
    gl = (gloss or "").split()
    ids = lex_ids if lex_ids and len(lex_ids) == len(forms) else [None] * len(forms)
    if len(gl) != len(forms):
        # a memory record whose gloss doesn't align word for word: each word's own reading (the site lays out a
        # gloss under every word, and a None there broke the page)
        from .analyze import Analyzer
        an = Analyzer.load()
        gl = []
        for f in forms:
            a = an.analyze(f)
            gl.append(a[0]["analyses"][0].gloss() if a and a[0]["analyses"] else "")
    return [{"form": f.strip(".,;:?!"), "gloss": gl[i], "status": provenance(ids[i])} for i, f in enumerate(forms)]


# a period after these ends no sentence ('Dr. Smith saw the wolf.' was cut into 'Dr.' and 'Smith saw the wolf.')
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "st", "sr", "jr", "prof", "mt", "vs", "etc", "e.g", "i.e", "vol", "ch",
                 "cf", "approx"}


def split_sentences(text: str) -> list[str]:
    """Sentences: a break after . ? ! and white space, except after an abbreviation or a lone initial ('J. Smith'),
    and not inside an ellipsis that runs on in lower case ('The wolf... saw the sheep')."""
    out, cur = [], ""
    for piece in re.split(r"(?<=[.?!])\s+", text.strip()):
        cur = f"{cur} {piece}" if cur else piece
        last = cur.rsplit(None, 1)[-1].lower() if cur.split() else ""
        if last.endswith(".") and (last[:-1].strip("(\"'") in ABBREVIATIONS or re.fullmatch(r"[a-z]\.", last)
                                   or last.endswith("...")):
            continue
        out.append(cur.strip())
        cur = ""
    if cur.strip():
        out.append(cur.strip())
    return [x for x in out if x]


def english_to_pie(text: str) -> list[dict]:
    from .formulas import rewrite
    from .gloss import readable
    from .memory import Memory
    mem = Memory.load()
    out = []
    transfer = None
    for sentence in split_sentences(text):
        parts = rewrite(sentence) or [(sentence, None)]
        for k, (s, pre) in enumerate(parts):
            shown = sentence if len(parts) == 1 else s if k else sentence[: len(sentence) - len(parts[-1][0])].strip()
            pre = [pre] if pre else []
            if not s:                       # a word with no PIE counterpart ('Yes.', 'Please.'): the note says why
                out.append(Sentence(shown, None, None, None, "rules", None, None, [shown.strip(" .!?,;:")], pre))
                continue
            hits = mem.search(s, k=1)
            if hits and hits[0][0] >= MEMORY_ACCEPT:
                score, p = hits[0]
                out.append(Sentence(shown, p.pie, readable(p.gloss), _ipa(p.pie), "memory", p.source_id, score,
                                    notes=pre, words=_words(p.pie, readable(p.gloss), p.lex_ids)))
                continue
            if transfer is None:
                from .transfer import Transfer
                transfer = Transfer()
            r = transfer.translate(s)
            notes = pre + r.notes + [f"could not build: {e}" for e in r.errors]
            out.append(Sentence(shown, r.pie, readable(r.gloss), _ipa(r.pie), "rules", None, None, r.unknown, notes,
                                _words(r.pie, readable(r.gloss), r.lex_ids)))
    return [asdict(x) for x in out]


def pie_to_english(text: str) -> dict:
    from .analyze import Analyzer
    from .memory import Memory
    from .provenance import provenance
    an = Analyzer.load()
    words = an.analyze(text)
    rough = []
    for w in words:
        if w["analyses"]:
            a = w["analyses"][0]
            # a near spelling is a guess ('hello' read as h₂éloh₂ 'nourish'): marked, so it doesn't read as a word
            g = re.sub(r"^(.*)\.(CMP|SUP)$", lambda m: ("more " if m[2] == "CMP" else "most ") + m[1],
                       a.gloss().split("-")[0])           # big.CMP → more big
            rough.append(g.replace(".", " ") + (" (?)" if w["match"] == "close" else ""))
        else:
            rough.append(f"[{w['form']}]")
        if w["clitic"]:
            rough.append(w["clitic"][1])
    mem = Memory.load()
    from .analyze import skeleton
    key = " ".join(skeleton(w) for w in text.split()).strip(" .?!")
    exact = next((p for p in mem.pairs if p.pie.strip() == text.strip()), None) or next(
        (p for p in mem.pairs if " ".join(skeleton(w) for w in p.pie.split()).strip(" .?!") == key), None)
    # the IPA of the corpus spelling a typed word was read as (wekwos → wékʷos), not of the typing
    read = " ".join((w["spelled"] or w["form"]) + (f"-{w['clitic'][0]}" if w["clitic"] else "") for w in words)
    return {"pie": text, "read_as": read if read != text.strip(" .?!") else None, "ipa": _ipa(read),
            "words": [{"word": w["word"], "match": w["match"], "clitic": w["clitic"], "spelled": w.get("spelled"),
                       "analyses": [{"lex_id": a.lex_id, "lemma": a.lemma, "features": a.features, "gloss": a.gloss(),
                                     "pos": a.pos, "status": provenance(a.lex_id)} for a in w["analyses"][:6]]}
                      for w in words],
            "rough_english": " ".join(rough),
            "memory": {"english": exact.english, "source_id": exact.source_id} if exact else None}
