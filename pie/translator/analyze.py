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


_SKEL = [("ʷ", "w"), ("ʰ", "h"), ("₁", ""), ("₂", ""), ("₃", ""), ("ː", ""), ("ə", "e"), ("i̯", "y"), ("u̯", "w"),
         ("j", "y"), ("þ", "t")]


def skeleton(s: str) -> str:
    """How people type PIE without the special letters: wekwos, *wékʷos, we/kwos, h2owis, H2OWIS, k'mtom,
    gwhenti, dhugh2te:r all meet the corpus form here. Lower case; accents, length, syllabic and palatal marks
    dropped (ḱ → k, m̥ → m, ē → e); ʷ → w, ʰ → h; laryngeals h₁ h₂ h₃ H (or h1 h2 h3) all → h; the project's
    ASCII marks (/ accent, : length, ' palatal, _ syllabic) and a leading * removed."""
    s = unicodedata.normalize("NFD", s.lower().lstrip("*"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    for a, b in _SKEL:
        s = s.replace(a, b)
    s = re.sub(r"[/:'_`´]", "", s)
    s = re.sub(r"h[123]", "h", s)
    s = re.sub(r"(?<=[aeiou])u", "w", s)      # diphthongs as people write them: dyeus, deiwos → dyews, deywos
    s = re.sub(r"(?<=[aeiou])i", "y", s)
    return s


def _overlap(a: str, b: str) -> int:
    """Shared characters, to rank the typed matches: the form that keeps more of what was typed comes first."""
    return sum(1 for x, y in zip(unicodedata.normalize("NFD", a), unicodedata.normalize("NFD", b)) if x == y)


def bare(s: str) -> str:
    """skeleton() without laryngeals, for input that leaves them out (ekwos for h₁éḱwos, ster for h₂stḗr). In a
    corpus form a laryngeal is h₁ h₂ h₃ H; in typed input any h not after b d g k p t (an aspirate) counts as one."""
    s = unicodedata.normalize("NFC", s)
    if re.search(r"h[₁₂₃]|H", s):
        s = re.sub(r"h[₁₂₃]|H", "", s)
        return skeleton(s)
    k = skeleton(s)
    return re.sub(r"(?<![bdgkptw])h", "", k)


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
        return readable_word(f"{self.english}-{self.features}" if self.features else self.english)


@dataclass
class Analyzer:
    index: dict[str, list[Analysis]]
    loose: dict[str, list[Analysis]] = field(default_factory=dict)     # unaccented keys
    skel: dict[str, list[tuple[str, Analysis]]] = field(default_factory=dict)   # skeleton() keys → (form, analysis)
    bare_: dict[str, list[tuple[str, Analysis]]] = field(default_factory=dict)  # bare() keys

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

    def _skeleton_index(self) -> dict:
        if not self.skel:
            for f, xs in self.index.items():
                for a in xs:
                    self.skel.setdefault(skeleton(f), []).append((f, a))
                    self.bare_.setdefault(bare(f), []).append((f, a))
        return self.skel

    def word(self, w: str) -> tuple[list[Analysis], str]:
        """(analyses, how): exact, unaccented, typed (skeleton(): plain letters, ASCII, a leading *), or unknown.
        A typed match may fit several forms; the ones closest to what was typed come first."""
        w = nfc(w.strip(_PUNCT).lstrip("*"))
        if w in self.index:
            return self.index[w], "exact"
        if unaccented(w) in self.loose:
            return self.loose[unaccented(w)], "unaccented"
        hits = self._skeleton_index().get(skeleton(w), []) or self.bare_.get(bare(w), [])
        how = "typed"
        if not hits:
            hits, how = self._close(w), "close"
        if hits:
            hits = sorted(hits, key=lambda fa: -_overlap(fa[0], w))
            out, seen = [], set()
            for _, x in hits:
                k = (x.lex_id, x.features)
                if k not in seen:
                    seen.add(k)
                    out.append(x)
            return out, how
        return [], "unknown"

    def _close(self, w: str) -> list[tuple[str, Analysis]]:
        """A near spelling (a misremembered vowel: bhrater for bʰréh₂tēr): bare() keys with the same first letter,
        length within 2 and similarity ≥ 0.8; the best key's forms."""
        import difflib
        k = bare(w)
        if len(k) < 4:
            return []
        self._skeleton_index()
        if not hasattr(self, "_by_first"):
            self._by_first = {}
            for key in self.bare_:
                if key:
                    self._by_first.setdefault(key[0], []).append(key)
        cands = [x for x in self._by_first.get(k[0], []) if abs(len(x) - len(k)) <= 2]
        best = difflib.get_close_matches(k, cands, n=6, cutoff=0.75)
        if not best:
            return []
        # among the near spellings, the word the corpus uses most (méh₂tēr, not a rare verb form)
        if not hasattr(self, "_uses"):
            from .lexmap import _corpus_counts
            self._uses = _corpus_counts()
        score = lambda key: (difflib.SequenceMatcher(None, k, key).ratio()
                             + 0.05 * max(__import__("math").log1p(self._uses[a.lex_id]) for _, a in self.bare_[key]))
        return self.bare_[max(best, key=score)]

    def forms_for(self, w: str) -> list[str]:
        """The corpus spellings a typed word stands for (for showing 'did you mean')."""
        w = w.strip(_PUNCT)
        hits = self._skeleton_index().get(skeleton(w), []) or self.bare_.get(bare(w), []) or self._close(w)
        return list(dict.fromkeys(f for f, _ in sorted(hits, key=lambda fa: -_overlap(fa[0], w))))

    def analyze(self, text: str) -> list[dict]:
        """Per written word: its analyses (and the split-off enclitic's), with readable glosses."""
        out = []
        for raw in text.split():
            w = raw.strip(_PUNCT).lstrip("*")
            if not w:
                continue
            clitic = None
            if "-" in w[1:]:
                head, tail = w.rsplit("-", 1)
                tail_key = {skeleton(k): k for k in ENCLITICS}.get(skeleton(tail))
                if tail_key:
                    w, clitic = head, tail_key
            an, how = self.word(w)
            spelled = None
            if how in ("typed", "close", "unaccented"):
                spelled = next((f for f in self.forms_for(w)), None)
            out.append({"word": raw, "form": w, "match": how, "analyses": an, "spelled": spelled,
                        "clitic": (clitic, ENCLITICS[clitic]) if clitic else None})
        return out
