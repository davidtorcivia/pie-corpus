"""Translation memory: the corpus's own English ↔ PIE sentence pairs, searched by English.

The pairs come from the exported records (export/train.jsonl, export/eval.jsonl), split into sentences and aligned
the way the chat export aligns them (pie.export_chat.align_english); a record whose English does not align is one
pair when it is short. A query is matched on its content words (an inverted index narrows the candidates), then
scored by the word-sequence similarity of the whole sentence (difflib), 0..1. An exact match (after lower-casing
and dropping punctuation) scores 1.0.

    from pie.translator.memory import Memory
    Memory.load().search("The wolf saw the sheep.", k=3)
"""
from __future__ import annotations

import collections
import difflib
import functools
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STOP = set("a an the and or of to in on at by for with from is are was were be been am i you he she it we they "
           "me him her us them my your his its our their this that these those not no do does did will shall "
           "would should can could may might must have has had".split())
SHORT = 3          # an unaligned record is one pair when it has at most this many sentences


def words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", s.lower().replace("’", "'"))


@dataclass
class Pair:
    english: str
    pie: str
    gloss: str | None
    source_id: str
    tier: int | None
    lex_ids: list | None = None     # per written word (an enclitic token joins the word before it)


@dataclass
class Memory:
    pairs: list[Pair]
    inv: dict[str, list[int]]
    exact: dict[str, int]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def load(cls, root: Path = ROOT) -> "Memory":
        from ..export_chat import align_english, sentences
        pairs: list[Pair] = []
        for name in ("train.jsonl", "eval.jsonl"):
            p = root / "export" / name
            if not p.exists():
                continue
            for line in p.read_text("utf-8").splitlines():
                r = json.loads(line)
                if not r.get("english") or not r.get("pie"):
                    continue
                pie = sentences(r["pie"])
                en, _ = align_english(r)
                glosses = _split_gloss(r.get("gloss"), pie)
                ids = [t.get("lex_id") for t in r.get("tokens") or [] if not t["form"].startswith("-")]
                per = _split_list(ids, pie)
                if en and len(en) == len(pie):
                    for i, (e, s) in enumerate(zip(en, pie)):
                        pairs.append(Pair(e, s, glosses[i] if glosses else None, r["id"], r.get("tier"),
                                          per[i] if per else None))
                elif len(pie) <= SHORT:
                    pairs.append(Pair(" ".join(r["english"].split()), r["pie"], r.get("gloss"), r["id"], r.get("tier"),
                                      ids if len(ids) == len(r["pie"].split()) else None))
        inv: dict[str, list[int]] = collections.defaultdict(list)
        exact: dict[str, int] = {}
        for i, p in enumerate(pairs):
            ws = words(p.english)
            exact.setdefault(" ".join(ws), i)
            for w in set(ws) - STOP:
                inv[w].append(i)
        return cls(pairs, dict(inv), exact)

    def search(self, english: str, k: int = 5) -> list[tuple[float, Pair]]:
        """The k best pairs for an English sentence, best first, as (score, pair)."""
        ws = words(english)
        if not ws:
            return []
        if " ".join(ws) in self.exact:
            return [(1.0, self.pairs[self.exact[" ".join(ws)]])]
        content = set(ws) - STOP or set(ws)
        hits = collections.Counter(i for w in content for i in self.inv.get(w, ()))
        cands = [i for i, _ in hits.most_common(200)]
        scored = []
        for i in cands:
            sm = difflib.SequenceMatcher(None, ws, words(self.pairs[i].english), autojunk=False)
            scored.append((round(sm.ratio(), 3), self.pairs[i]))
        scored.sort(key=lambda x: -x[0])
        return scored[:k]


def _split_list(xs: list, pie_sents: list[str]) -> list[list] | None:
    """xs (one per written word) cut at the PIE sentences' word counts, or None if the counts differ."""
    n = [len(s.split()) for s in pie_sents]
    if sum(n) != len(xs):
        return None
    out, at = [], 0
    for k in n:
        out.append(xs[at:at + k])
        at += k
    return out


def _split_gloss(gloss: str | None, pie_sents: list[str]) -> list[str] | None:
    """The record's gloss cut at the same word counts as its PIE sentences, or None if the counts differ."""
    if not gloss:
        return None
    g = gloss.split()
    n = [len(s.split()) for s in pie_sents]
    if sum(n) != len(g):
        return None
    out, at = [], 0
    for k in n:
        out.append(" ".join(g[at:at + k]))
        at += k
    return out
