"""PIE → analyses: the inverse of the engine. Every form the engine can build for a usable lexeme (each cell of
each noun, verb, adjective and participle), every closed-class form (data/morph/closed_class.json) and every
indeclinable headword, indexed by its written form.

    from pie.translator.analyze import Analyzer
    Analyzer.load().analyze("h₂ówis h₁éḱwōs-kʷe dedórḱe")

A word may have several analyses (h₂ówis is NOM.SG and GEN.SG); all are returned, most frequent in the corpus
first when Analyzer.load() was given corpus counts. A word the index does not have is looked up without its
accents, then reported unknown. Enclitics written with a hyphen (-kʷe, -wē, -ge) are split off first.
"""
from __future__ import annotations

import functools
import hashlib
import pickle
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from ..realize import Lexicon
from .gloss import readable_word

ENCLITICS = {"kʷe": "and", "wē": "or", "ge": "indeed", "ḱe": "here"}
_ACCENT = "́̀̂"
_PUNCT = ".,;:!?\"“”'‘’()[]«»"
ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "translator"
# what the index is built from: a change to any of these rebuilds it (the build takes about a minute)
_INPUTS = ["data/lexicon/lexicon.jsonl", "data/morph/inflection_specs.jsonl", "data/morph/closed_class.json",
           "data/generation/blocklist.jsonl", "data/lexicon/neologisms.jsonl", "data/lexicon/derived_glosses.jsonl",
           "data/lexicon/confirmed_glosses.jsonl", "data/lexicon/project_reconstructions.jsonl",
           "data/morph/accent_unresolved.json", "pie/realize.py", "pie/morph.py", "pie/phon.py", "pie/compound.py",
           "pie/neologism.py", "pie/translator/analyze.py"]


def _inputs_hash() -> str:
    h = hashlib.sha256()
    for rel in _INPUTS:
        p = ROOT / rel
        if p.exists():
            h.update(rel.encode() + p.read_bytes())
    return h.hexdigest()[:16]


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def unaccented(s: str) -> str:
    return nfc("".join(c for c in unicodedata.normalize("NFD", s) if c not in _ACCENT))


@dataclass
class Analysis:
    lex_id: str
    lemma: str
    features: str          # PRS.3SG, NOM.SG, M.NOM.SG (adjective: gender first), PTCP.ACT.M.NOM.SG, ADV …
    english: str           # the lexeme's English gloss (Lexicon.gloss), readable for closed-class words
    pos: str               # noun, verb, adj, ptcp, pron, num, adv, particle

    def gloss(self) -> str:
        return readable_word(f"{self.english}-{self.features}") if self.features else self.english


@dataclass
class Analyzer:
    index: dict[str, list[Analysis]]
    loose: dict[str, list[Analysis]] = field(default_factory=dict)     # unaccented keys

    @classmethod
    @functools.lru_cache(maxsize=1)
    def load(cls, neologisms: bool = True) -> "Analyzer":
        """The index, from .cache/translator/ when its inputs are unchanged (_INPUTS), else built and cached."""
        path = CACHE / f"analyzer-{'neo' if neologisms else 'base'}-{_inputs_hash()}.pkl"
        if path.exists():
            return pickle.loads(path.read_bytes())
        a = cls.build(neologisms)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(a))
        return a

    @classmethod
    def build(cls, neologisms: bool = True) -> "Analyzer":
        lx = Lexicon.load()
        if neologisms:
            from ..neologism import with_neologisms
            lx = with_neologisms(lx)
        idx: dict[str, list[Analysis]] = {}

        def add(form: str, a: Analysis):
            for f in form.split("/"):
                f = nfc(f.strip().strip("*-"))
                if f and a not in idx.setdefault(f, []):
                    idx[f].append(a)

        for lid, r in lx.specs.items():
            if lx.inadmissible(lid) or not lx.entries.get(lid, {}).get("meaning") and lid not in lx.derived:
                continue
            fam, lemma, en = r["family"], lx.entries[lid]["form"], lx.gloss(lid)
            if fam not in ("noun", "verb", "adj"):            # indeclinables (adverbs, adpositions): the headword
                add(lemma, Analysis(lid, lemma, "", en, "adv"))
                continue
            try:
                if fam == "adj":
                    for g in ("m", "f", "n"):
                        for f, forms in lx.admissible_cells(lid, g).items():
                            for x in forms:
                                add(x, Analysis(lid, lemma, f"{g.upper()}.{f}", en, "adj"))
                    continue
                for f, forms in lx.admissible_cells(lid).items():
                    for x in forms:
                        add(x, Analysis(lid, lemma, f, en, fam))
                if fam == "verb":
                    for v in lx.voices(lid):
                        for g in ("m", "f", "n"):
                            try:
                                cells = lx.admissible_participle_cells(lid, v, g)
                            except KeyError:
                                continue
                            for f, forms in cells.items():
                                for x in forms:
                                    add(x, Analysis(lid, lemma, f"PTCP.{v}.{g.upper()}.{f}", en, "ptcp"))
            except Exception:          # a spec the engine cannot build is skipped, as make_slice does
                continue

        def walk(node, path: list[str]):
            if isinstance(node, dict):
                for k, v in node.items():
                    if not k.startswith("_"):
                        walk(v, path + [k])
            elif isinstance(node, list) and node and all(isinstance(x, str) for x in node):
                feats = [p for p in path if re.fullmatch(r"[A-Z0-9][A-Z0-9.]*", p) and not p.isdigit()]
                ids = [p for p in path if p not in feats and p not in ("m", "f", "n", "mf", "fn")]
                gender = next((p for p in path if p in ("m", "f", "n", "mf", "fn")), None)
                lid = "closed:" + "/".join(ids)
                feat = ".".join(feats)
                if gender and ids[0] not in ("personal",):
                    feat = (gender[0].upper() + "." if gender in ("m", "f", "n") else "") + feat
                en = "/".join(ids)
                pos = "num" if ids[0] == "numerals" else "adv" if ids[0].endswith("_adv") else "pron"
                for x in node:
                    add(x, Analysis(lid, node[0], feat, en, pos))

        for sec, node in lx.closed.items():
            if sec.startswith("_") or sec == "particles":
                continue
            walk(node, [sec])
        for form, meaning in lx.closed.get("particles", {}).items():
            if isinstance(meaning, str):
                add(form, Analysis(f"closed:particle:{form.strip('-')}", form, "", meaning.split("(")[0].strip().replace(" ", "."),
                                   "particle"))
        add("h₁yód", Analysis("closed:relative_yo/n", "h₁yód", "", "if/when", "particle"))   # the conjunction
        # indeclinables: lexicon headwords without an inflection spec (adverbs, particles, adpositions)
        for lid, e in lx.entries.items():
            if lid in lx.specs or e.get("kind") == "root" or not e.get("meaning"):
                continue
            if e.get("pos") in ("adv", "particle", "conj", "prep", "postp", "adp", "interj", "num"):
                add(e["form"], Analysis(lid, e["form"], "", lx.gloss(lid), "adv"))
        loose: dict[str, list[Analysis]] = {}
        for f, xs in idx.items():
            loose.setdefault(unaccented(f), []).extend(xs)
        return cls(idx, loose)

    def word(self, w: str) -> tuple[list[Analysis], str]:
        """(analyses, how): exact, unaccented, or unknown."""
        w = nfc(w.strip(_PUNCT))
        if w in self.index:
            return self.index[w], "exact"
        if unaccented(w) in self.loose:
            return self.loose[unaccented(w)], "unaccented"
        return [], "unknown"

    def analyze(self, text: str) -> list[dict]:
        """Per written word: its analyses (and the split-off enclitic's), with readable glosses."""
        out = []
        for raw in text.split():
            w = raw.strip(_PUNCT)
            if not w:
                continue
            clitic = None
            if "-" in w[1:]:
                head, tail = w.rsplit("-", 1)
                if tail in ENCLITICS:
                    w, clitic = head, tail
            an, how = self.word(w)
            out.append({"word": raw, "form": w, "match": how, "analyses": an,
                        "clitic": (clitic, ENCLITICS[clitic]) if clitic else None})
        return out
