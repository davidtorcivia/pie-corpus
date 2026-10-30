"""English word → PIE lexemes, for the transfer translator.

Every usable lexeme's English senses (Lexicon.meaning: "stallion, horse"; "to be giving") are lemmatized with spaCy,
and each sense's head word ("horse", "give") points back to the lexeme. Candidates are ranked by:
1. the sense's position (a lexeme's first sense is its main meaning);
2. how often the reviewed corpus uses the lexeme (corpus/ tokens: the planners' and reviewers' choices);
3. how many branches attest it (lexicon reflexes).
Verbs are listed per lexeme with the tenses its cells have, so the caller can pick the stem that has the tense it
needs (déh₃t for "gave", dédeh₃ti for "gives").

The map is cached in .cache/translator/ like the analyzer's index (analyze._inputs_hash, plus corpus/).
"""
from __future__ import annotations

import collections
import functools
import hashlib
import json
import math
import pickle
import re
from dataclasses import dataclass

from ..realize import Lexicon
from .analyze import CACHE, ROOT, _inputs_hash

FAMILY_POS = {"noun": "NOUN", "verb": "VERB", "adj": "ADJ"}
# English words whose everyday sense the glosses don't reach (or reach only through a rare lexeme): the lexemes the
# planner briefs name for them (planner-brief-3b.md §1 and §3, planner-brief-v4.md "Greetings and thanks")
OVERRIDES = {
    ("friend", "noun"): "pie-lex-priHos", ("dear", "adj"): "pie-lex-kjeywos", ("guest", "noun"): "pie-lex-ghostis",
    ("language", "noun"): "pie-lex-dngjhweh2s", ("tongue", "noun"): "pie-lex-dngjhweh2s",
    ("word", "noun"): "pie-lex-wekwos", ("joy", "noun"): "pie-lex-mowdos", ("pleasure", "noun"): "pie-lex-sweh2dos",
    ("name", "noun"): "pie-lex-h1nomn", ("new", "adj"): "pie-lex-newos", ("well", "adj"): "pie-lex-keh2ilos",
    ("healthy", "adj"): "pie-lex-keh2ilos", ("good", "adj"): "pie-lex-h1wesus", ("fast", "adj"): "pie-lex-HeHkjus",
    ("quick", "adj"): "pie-lex-HeHkjus", ("horse", "noun"): "pie-lex-h1ekjwos", ("home", "noun"): "pie-lex-doxm",
    ("house", "noun"): "pie-lex-doxm", ("day", "noun"): "pie-lex-dinos", ("hungry", "adj"): None,
    ("want", "verb"): "pie-lex-wekjti", ("wish", "verb"): "pie-lex-wekjti", ("dream", "noun"): "pie-lex-supniyom",
    ("grief", "noun"): "pie-lex-kjeh2dos", ("sorrow", "noun"): "pie-lex-kjeh2dos", ("grandfather", "noun"): "pie-lex-h2ewh2os",
}


@dataclass
class Candidate:
    lex_id: str
    family: str             # noun, verb, adj
    sense_rank: int         # 0 = first sense
    corpus_uses: int
    branches: int
    tenses: frozenset       # verbs: PRS PST AOR PRF IMP SBJV OPT (from the admissible cells)
    gender: str | None

    def score(self) -> float:
        """Corpus use counts most (reviewed choices), then attestation, minus a step per later sense."""
        return 2 * math.log1p(self.corpus_uses) + math.log1p(self.branches) - 1.5 * self.sense_rank

    def key(self):
        return -self.score()


def _corpus_counts() -> collections.Counter:
    c = collections.Counter()
    for f in sorted((ROOT / "corpus").glob("tier*/*.jsonl")):
        for line in f.read_text("utf-8").splitlines():
            for t in json.loads(line).get("tokens") or []:
                if t.get("lex_id"):
                    c[t["lex_id"]] += 1
    return c


def _corpus_hash() -> str:
    h = hashlib.sha256()
    for f in sorted((ROOT / "corpus").glob("tier*/*.jsonl")):
        h.update(f.name.encode() + str(f.stat().st_size).encode())
    return h.hexdigest()[:12]


def _senses(meaning: str) -> list[str]:
    out = []
    for s in re.split(r"[;,]", meaning):
        s = re.sub(r"\(.*?\)|\[.*?\]", "", s).strip().lower()
        s = re.sub(r"^(to )", "", s)
        if s:
            out.append(s)
    return out


def head_lemma(nlp, phrase: str) -> str | None:
    """The head word of a gloss phrase, lemmatized: 'be giving' → give, 'take a step' → take, 'swift horse' → horse."""
    doc = nlp(phrase)
    toks = [t for t in doc if t.is_alpha]
    if not toks:
        return None
    root = next((t for t in doc if t.dep_ == "ROOT"), toks[0])
    if root.lemma_ == "be" and len(toks) > 1:                  # "be giving", "be afraid"
        nxt = [t for t in toks if t.i > root.i]
        if nxt:
            root = nxt[0]
    return root.lemma_.lower()


@dataclass
class LexMap:
    by_lemma: dict[str, list[Candidate]]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def load(cls, nlp=None) -> "LexMap":
        path = CACHE / f"lexmap-{_inputs_hash()}-{_corpus_hash()}.pkl"
        if path.exists():
            return pickle.loads(path.read_bytes())
        m = cls.build(nlp)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(m))
        return m

    @classmethod
    def build(cls, nlp=None) -> "LexMap":
        if nlp is None:
            import spacy
            nlp = spacy.load("en_core_web_sm", disable=["ner"])
        lx = Lexicon.load()
        uses = _corpus_counts()
        by: dict[str, list[Candidate]] = collections.defaultdict(list)
        for lid, r in lx.specs.items():
            fam = r["family"]
            if fam not in FAMILY_POS or lx.inadmissible(lid):
                continue
            meaning, _ = lx.meaning(lid)
            if not meaning:
                continue
            tenses = frozenset()
            gender = None
            try:
                if fam == "verb":
                    tenses = frozenset(p for f in lx.admissible_cells(lid) for p in f.split(".")
                                       if p in ("PRS", "PST", "AOR", "PRF", "IMP", "SBJV", "OPT"))
                    if not tenses:
                        continue
                elif fam == "noun":
                    gender = lx.gender(lid)
                    if not lx.admissible_cells(lid):
                        continue
            except Exception:
                continue
            branches = len(lx.entries[lid].get("reflexes") or {})
            seen = set()
            for rank, s in enumerate(_senses(meaning)[:6]):
                lem = head_lemma(nlp, s)
                if lem and lem not in seen:
                    seen.add(lem)
                    by[lem].append(Candidate(lid, fam, rank, uses[lid], branches, tenses, gender))
        for v in by.values():
            v.sort(key=Candidate.key)
        return cls(dict(by))

    def candidates(self, lemma: str, family: str | None = None) -> list[Candidate]:
        """Ranked candidates; an OVERRIDES lexeme of that family comes first."""
        xs = [c for c in self.by_lemma.get(lemma.lower(), []) if family is None or c.family == family]
        o = OVERRIDES.get((lemma.lower(), family))
        if o:
            hit = [c for c in xs if c.lex_id == o] or [c for v in self.by_lemma.values() for c in v if c.lex_id == o][:1]
            xs = hit + [c for c in xs if c.lex_id != o]
        return xs
