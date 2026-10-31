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
    ("tell", "verb"): "pie-lex-mlewHti", ("want", "verb"): "pie-lex-wekjti", ("wish", "verb"): "pie-lex-wekjti", ("dream", "noun"): "pie-lex-supniyom",
    ("grief", "noun"): "pie-lex-kjeh2dos", ("sorrow", "noun"): "pie-lex-kjeh2dos", ("grandfather", "noun"): "pie-lex-h2ewh2os",
    # dialogue gaps 2026-10-30 (docs/audits/lexicon-gaps-dialogue-2026-10-30.md)
    ("rage", "verb"): "pie-lex-ghremeti", ("anger", "verb"): "pie-lex-ghromeyeti", ("hunger", "noun"): "pie-lex-gwoldhos",
    ("hunger", "verb"): "pie-lex-kenketi", ("milk", "noun"): "pie-lex-h2melgjos", ("play", "verb"): "pie-lex-loygeti",
    ("weave", "verb"): "pie-lex-teksti", ("cup", "noun"): "pie-lex-peh3tlom", ("pot", "noun"): "pie-lex-kweros",
    ("kettle", "noun"): "pie-lex-kweros", ("knife", "noun"): "pie-lex-kjstrom", ("feast", "noun"): "pie-lex-dh2pnom",
    ("sad", "adj"): "pie-lex-lugjros", ("story", "noun"): "pie-proj-spelom", ("tale", "noun"): "pie-proj-spelom",
    ("grandmother", "noun"): "pie-proj-h2enHos",
    # core gaps 2026-10-30 (docs/audits/lexicon-gaps-core-2026-10-30.md)
    ("person", "noun"): "pie-lex-mortos", ("human", "noun"): "pie-lex-mortos", ("child", "noun"): "pie-lex-tekjnom",
    ("small", "adj"): "pie-lex-peh2uros", ("little", "adj"): "pie-lex-peh2uros", ("tail", "noun"): "pie-lex-h1orseh2",
    ("leg", "noun"): "pie-lex-skelos", ("thigh", "noun"): "pie-lex-skelos", ("bark", "noun"): "pie-lex-lowbhos",
    ("flower", "noun"): "pie-lex-h2endhos", ("blossom", "noun"): "pie-lex-h2endhos", ("grass", "noun"): "pie-lex-ghreh1mn",
    ("belly", "noun"): "pie-lex-uderos", ("guts", "noun"): "pie-lex-gjhorneh2", ("entrails", "noun"): "pie-lex-gjhorneh2",
    ("ice", "noun"): "pie-lex-h1yegos", ("shadow", "noun"): "pie-lex-skjeh3ih2", ("shade", "noun"): "pie-lex-skjeh3ih2",
    ("wood", "noun"): "pie-lex-doru", ("timber", "noun"): "pie-lex-doru", ("soil", "noun"): "pie-lex-dhegjhoxm",
    ("goat", "noun"): "pie-lex-kapros", ("bad", "adj"): "pie-lex-h2eghos-2", ("evil", "adj"): "pie-lex-h2eghos-2",
    ("rot", "verb"): "pie-lex-puHyeti", ("straight", "adj"): "pie-lex-h3regjtos", ("smooth", "adj"): "pie-lex-ghlh2dhros",
    ("beautiful", "adj"): "pie-lex-kjubhros", ("pretty", "adj"): "pie-lex-kjubhros", ("happy", "adj"): "pie-lex-mudros",
    ("glad", "adj"): "pie-lex-mudros", ("rejoice", "verb"): "pie-lex-mewdeti", ("hunt", "verb"): "pie-lex-wregeti",
    ("walk", "verb"): "pie-lex-steygheti", ("rub", "verb"): "pie-lex-teryeti", ("freeze", "verb"): "pie-lex-goleti",
    ("cough", "verb"): "pie-lex-kweh2se", ("smell", "verb"): "pie-lex-h3edeti", ("carry", "verb"): "pie-lex-bhereti",
    ("show", "verb"): "pie-lex-deykjeti", ("hate", "verb"): "pie-lex-h3eh3ode-2", ("teach", "verb"): "pie-lex-kjeHst",
    ("lack", "noun"): "pie-lex-h1egos", ("grateful", "adj"): "pie-lex-gwrHtos", ("thankful", "adj"): "pie-lex-gwrHtos",
    ("decide", "verb"): "pie-lex-h2reh1dheti", ("council", "noun"): "pie-lex-dhh1tleh2",
    ("assembly", "noun"): "pie-lex-dhh1tleh2", ("wise", "adj"): "pie-lex-gjnh3ros", ("enemy", "noun"): "pie-lex-poykjos-2",
    ("foe", "noun"): "pie-lex-poykjos-2",
    # round 3 2026-10-31 (docs/audits/lexicon-gaps-round3-2026-10-31.md)
    ("booty", "noun"): "pie-lex-Hrowpos", ("spoils", "noun"): "pie-lex-Hrowpos", ("loot", "noun"): "pie-lex-Hrowpos",
    ("plunder", "noun"): "pie-lex-Hrowpos", ("boast", "noun"): "pie-lex-h1eh1ughos", ("vow", "noun"): "pie-lex-h1eh1ughos",
    ("threaten", "verb"): "pie-lex-tergweti", ("shield", "noun"): "pie-lex-skeytos", ("battle", "noun"): "pie-lex-keh3tus",
    ("victory", "noun"): "pie-lex-segjhos-2", ("brave", "adj"): "pie-lex-dhrsus", ("bold", "adj"): "pie-lex-dhrsus",
    ("pay", "verb"): "pie-lex-kwinewti", ("atone", "verb"): "pie-lex-kwinewti", ("repay", "verb"): "pie-lex-gheldheti",
    ("punish", "verb"): "pie-lex-kweyeti", ("avenge", "verb"): "pie-lex-kweyeti", ("ransom", "noun"): "pie-lex-kwoyneh2",
    ("revenge", "noun"): "pie-lex-kwoyneh2", ("vengeance", "noun"): "pie-lex-kwoyneh2",
    ("weep", "verb"): "pie-lex-HrewdHti", ("wail", "verb"): "pie-lex-HrewdHti", ("lament", "verb"): "pie-lex-HrewdHti",
    ("mourn", "verb"): "pie-lex-HrewdHti", ("summer", "noun"): "pie-lex-semeh2", ("obey", "verb"): "pie-lex-kjlowseyeti",
    ("heed", "verb"): "pie-lex-kjlowseyeti", ("persuade", "verb"): "pie-lex-bhoydheyeti", ("kick", "verb"): "pie-lex-sprneHti",
    ("spill", "verb"): "pie-lex-gjhewt-2", ("cow", "noun"): "pie-lex-gwoxws", ("cost", "verb"): "pie-lex-h2elgwheti",
    ("deserve", "verb"): "pie-lex-h2elgwheti", ("value", "noun"): "pie-lex-h2elgwhos", ("price", "noun"): "pie-lex-h2elgwhos",
    ("worth", "noun"): "pie-lex-h2elgwhos", ("debt", "noun"): "pie-lex-dhlghos", ("plague", "noun"): "pie-lex-moro",
    ("pestilence", "noun"): "pie-lex-moro", ("murder", "noun"): "pie-lex-gwhonos-2", ("slayer", "noun"): "pie-lex-gwhentoxr",
    ("killer", "noun"): "pie-lex-gwhentoxr", ("snatch", "verb"): "pie-lex-h1rh1pyeti", ("abandon", "verb"): "pie-lex-leykwt",
    ("bride", "noun"): "pie-lex-snusos", ("spin", "verb"): "pie-lex-sneh1", ("loom", "noun"): "pie-lex-tentlom",
    ("curse", "verb"): "pie-neo-curse", ("wealth", "noun"): "pie-lex-h3epnos", ("goods", "noun"): "pie-lex-h3epnos",
    ("promise", "verb"): "pie-lex-h1wogwheyeti", ("heir", "noun"): "pie-lex-h3orbhos", ("autumn", "noun"): "pie-lex-sh1esox",
    # round 5 2026-10-31 (docs/audits/lexicon-gaps-round5-2026-10-31.md)
    ("other", "adj"): "pie-lex-h2elyos", ("another", "adj"): "pie-lex-h2elyos", ("bull", "noun"): "pie-lex-uksexn",
    ("ox", "noun"): "pie-lex-uksexn", ("tear", "noun"): "pie-lex-dakjru", ("face", "noun"): "pie-lex-h1enih3kwo",
    ("age", "noun"): "pie-lex-h2oyu", ("generation", "noun"): "pie-lex-gjenh1eseh2", ("pray", "verb"): "pie-lex-gwhedhyeti",
    ("holy", "adj"): "pie-lex-sh2kros", ("sacred", "adj"): "pie-lex-sh2kros", ("host", "noun"): "pie-lex-ghostipotis",
    ("heal", "verb"): "pie-lex-mexdeti", ("cure", "verb"): "pie-lex-mexdeti", ("herb", "noun"): "pie-lex-ghreh1mn",
    ("fever", "noun"): "pie-lex-tepos", ("serve", "verb"): "pie-lex-sekwetor", ("anvil", "noun"): "pie-lex-h2ekjmox",
    ("bellows", "noun"): "pie-lex-bholgjhis", ("bag", "noun"): "pie-lex-bholgjhis", ("sack", "noun"): "pie-lex-bholgjhis",
    ("axle", "noun"): "pie-lex-h2ekjs", ("reins", "noun"): "pie-lex-sh2eymn", ("bridle", "noun"): "pie-lex-sh2eymn",
    ("dye", "verb"): "pie-lex-pinekjti", ("roast", "verb"): "pie-lex-bhrgjyeti", ("fry", "verb"): "pie-lex-bhrgjyeti",
    ("sacrifice", "verb"): "pie-lex-h1yagjeti", ("worship", "verb"): "pie-lex-h1yagjeti", ("howl", "verb"): "pie-lex-HrewdHti",
    ("roar", "verb"): "pie-lex-HrewdHti", ("month", "noun"): "pie-lex-mexh1ns", ("thunder", "noun"): "pie-lex-ghromos",
    ("deer", "noun"): "pie-lex-h1olkjis", ("stag", "noun"): "pie-lex-h1olkjis", ("slow", "adj"): "pie-lex-gwerdus",
    ("east", "adj"): "pie-lex-h2ewsteros",
    # round 6 2026-11-01 (docs/audits/lexicon-gaps-round6-2026-11-01.md)
    ("mare", "noun"): "pie-lex-h1ekjweh2", ("law", "noun"): "pie-lex-h2yewos", ("oar", "noun"): "pie-lex-h1erh1trom",
    ("bake", "verb"): "pie-lex-pekweti", ("bark", "verb"): "pie-lex-leh2yeti",
    ("pasture", "verb"): "pie-lex-peh2skjeti", ("knead", "verb"): "pie-lex-dheygjhti", ("loud", "adj"): "pie-lex-klh1ros",
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
    approx: bool = False    # the gloss is the approximate derived one (root + suffix function), not a dictionary's
    phrase: bool = False    # the sense is a phrase whose head isn't the meaning ('take a step' for 'take')

    def score(self) -> float:
        """Corpus use counts most (reviewed choices), then attestation, minus a step per later sense."""
        return (2 * math.log1p(self.corpus_uses) + math.log1p(self.branches) - 1.5 * self.sense_rank
                - 5 * self.approx - 3 * self.phrase - 6 * self.lex_id.startswith("pie-neo-"))

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
            from .transfer import MODEL
            nlp = spacy.load(MODEL, disable=["ner"])
        from ..neologism import with_neologisms
        lx = with_neologisms(Lexicon.load())     # coinages too (ranked last: Candidate.score), for bread, forest …
        uses = _corpus_counts()
        by: dict[str, list[Candidate]] = collections.defaultdict(list)
        for lid, r in lx.specs.items():
            fam = r["family"]
            if fam not in FAMILY_POS or lx.inadmissible(lid):
                continue
            meaning, msource = lx.meaning(lid)
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
                    content = [w for w in re.findall(r"[a-z]+", s) if w not in ("a", "an", "the", "be", "one", "s")]
                    by[lem].append(Candidate(lid, fam, rank, uses[lid], branches, tenses, gender,
                                             approx=msource == "derived", phrase=len(content) > 1))
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
