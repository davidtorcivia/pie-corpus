"""Validator: tokenize PIE text, lemmatize each token to a lexeme and root,
and classify every miss.

The form index holds every cell the engine generates for every spec in
data/morph/inflection_specs.jsonl (both conventions, with alternatives),
plus the closed-class tables and the lexicon's own lemma forms. Usability
gates generation, not recognition: non-usable specs are indexed too, at a
lower source rank.

Lookup is tiered. Older reconstructions differ in accent, length and
laryngeal notation, and coverage without tiers would be meaningless:
  exact      the canonical string
  noaccent   acute removed
  nolength   acute and macron removed
  decolored  also a next to h₂ → e (Byrd writes h₂-coloring: h₂áwey = h₂éwey)
  generic-H  also h₁/h₂/h₃ → H, and a next to H → e

Clitics (-kʷe, -wē, -ge, -de, -r) and the augment (h₁e-/é-) are split off
when the whole token fails.
"""

from __future__ import annotations

import collections
import difflib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj
from .translit import ACUTE, MACRON, is_canonical

ROOT = Path(__file__).resolve().parent.parent
TIERS = ("exact", "noaccent", "nolength", "decolored", "generic-H")
CLITICS = ["kʷe", "wē", "we", "ge", "de", "dʰe", "r"]
AUGMENTS = ["h₁é", "h₁e", "é", "e"]
_PUNCT = re.compile(r"[.,;:!?\"()\[\]…*=]+")


def _strip_marks(s: str, marks: str) -> str:
    """Remove accent/length marks from nuclei only. The acute on k/g is the
    palatal (ḱ = k + U+0301 in NFD) and must survive."""
    d = unicodedata.normalize("NFD", s)
    out = []
    for c in d:
        if c in marks:
            j = len(out) - 1
            while j >= 0 and unicodedata.combining(out[j]):
                j -= 1
            if j >= 0 and out[j] in "kg":
                out.append(c)
                continue
            continue
        out.append(c)
    return unicodedata.normalize("NFC", "".join(out))


def key(form: str, tier: str) -> str:
    f = form
    if tier != "exact":
        f = _strip_marks(f, ACUTE)
    if tier in ("nolength", "decolored", "generic-H"):
        f = _strip_marks(f, MACRON)
    if tier in ("decolored", "generic-H"):
        # laryngeal coloring written out (h₂a, ah₂) vs. underlying e
        f = re.sub("(h₂|H)a", r"\1e", re.sub("a(h₂|H)", r"e\1", f))
    if tier == "generic-H":
        f = re.sub("h[₁₂₃]", "H", f)
        f = re.sub("Ha", "He", re.sub("aH", "eH", f))
    return f


@dataclass(frozen=True)
class Analysis:
    lex_id: str
    root_id: str | None
    features: str          # e.g. "NOM.SG", "PRS.3SG", "LEMMA", "PARTICLE"
    source: str            # engine:<rule> | closed | lexicon
    gender: str | None = None


@dataclass
class Token:
    surface: str
    tier: str | None = None
    analyses: list[Analysis] = field(default_factory=list)
    clitic: str | None = None
    augment: str | None = None
    miss: str | None = None          # classification when not found
    miss_detail: str | None = None

    @property
    def found(self) -> bool:
        return bool(self.analyses)


class FormIndex:
    def __init__(self, lexicon: list[dict], specs: list[dict], closed: dict):
        self.lex = {e["id"]: e for e in lexicon}
        self.idx: dict[str, dict[str, list[Analysis]]] = {t: collections.defaultdict(list) for t in TIERS}
        self.lemma_forms: dict[str, list[str]] = collections.defaultdict(list)   # for miss classification
        for r in specs:
            if r["spec"]:
                self._add_spec(r)
        self._add_closed(closed)
        for e in lexicon:
            if e["kind"] == "root":
                continue
            for f in [e["form"], *e.get("variants", [])]:
                if f.startswith("-") or f.endswith("-"):
                    continue
                self._add(f, Analysis(e["id"], e.get("root_id"), "LEMMA", "lexicon"))
            self.lemma_forms[key(e["form"].strip("-"), "generic-H")].append(e["id"])

    def _add(self, form: str, a: Analysis) -> None:
        for t in TIERS:
            lst = self.idx[t][key(form, t)]
            if a not in lst:
                lst.append(a)

    def _add_spec(self, r: dict) -> None:
        e = self.lex.get(r["id"], {})
        root = e.get("root_id")
        src = f"engine:{r['rule']}" + ("" if r.get("usable") else ":unusable")
        fam, sp = r["family"], r["spec"]
        if fam == "noun":
            cells = {(None, k): v for k, v in decline(NounSpec(**sp)).items()}
        elif fam == "adj":
            cells = {(g, k): v for g, cs in decline_adj(AdjSpec(**sp)).items() for k, v in cs.items()}
        else:
            cells = {(None, k): v for k, v in conjugate(VerbSpec(**sp)).items()}
        for (g, feat), forms in cells.items():
            for f in forms:
                self._add(f, Analysis(r["id"], root, feat, src, g or e.get("gender")))

    def _add_closed(self, closed: dict) -> None:
        def walk(node, path):
            if isinstance(node, list):
                for f in node:
                    self._add(f, Analysis(f"closed:{'/'.join(path[:-1])}", None, path[-1], "closed"))
            elif isinstance(node, dict):
                for k, v in node.items():
                    if k.startswith("_"):
                        continue
                    if isinstance(v, str):   # particles: form → gloss
                        self._add(k.lstrip("-"), Analysis(f"closed:particle:{k}", None, "PARTICLE", "closed"))
                    else:
                        walk(v, path + [k])
        walk(closed, [])

    def lookup(self, form: str) -> tuple[str | None, list[Analysis]]:
        for t in TIERS:
            hit = self.idx[t].get(key(form, t))
            if hit:
                return t, hit
        return None, []


def load_index(root: Path = ROOT) -> FormIndex:
    lex = [json.loads(x) for x in (root / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()]
    specs = [json.loads(x) for x in (root / "data/morph/inflection_specs.jsonl").read_text("utf-8").splitlines()]
    closed = json.loads((root / "data/morph/closed_class.json").read_text("utf-8"))
    return FormIndex(lex, specs, closed)


# --- tokenization and analysis -----------------------------------------------

def tokenize(text: str) -> list[str]:
    out = []
    for raw in text.split():
        w = _PUNCT.sub("", raw)
        if not w:
            continue
        parts = [p for p in w.split("-") if p]
        if len(parts) > 1 and parts[-1] in CLITICS:     # host-kʷe
            out += parts[:-1] + ["-" + parts[-1]]
        else:
            out.append(w.replace("-", ""))
    return out


# Endings of form classes the engine does not build yet (Phase B). A miss is
# put here only when a known lemma's stem also matches the token.
_PHASE_B = [
    (re.compile(r"(?:tor|toy|ntor|ntoy|h₂er|h₂ey|soy|medʰh₂|dʰh₂we)$"), "phase-b:middle"),
    (re.compile(r"(?:oyh₁m\u0325|oys|oyt|oyh₁n\u0325t|yéh₁m\u0325|yéh₁s|yéh₁t|ih₁mé|ih₁té|ih₁ént)$"), "phase-b:optative"),
    (re.compile(r"(?:ēti|ēsi|ōh₂|ōmos|ōnti|ēt)$"), "phase-b:subjunctive"),
    (re.compile(r"(?:onts|ónts|n\u0325ts|mh₁nos|mh₁nóm|wōs|wṓs)$"), "phase-b:participle"),
]


def _stem_match(form: str, ix: FormIndex) -> tuple[str, list[str]] | None:
    """Longest prefix of the token (generic-H key) that is a known lemma
    (or lemma minus -s): evidence that the lexeme exists."""
    g = key(form, "generic-H")
    for n in range(len(g), 2, -1):
        cand = ix.lemma_forms.get(g[:n]) or ix.lemma_forms.get(g[:n] + "s")
        if cand:
            return g[:n], cand
    return None


def _classify_miss(tok: Token, ix: FormIndex, laryngealist: bool = True) -> None:
    """Every miss gets exactly one class (Phase 3 acceptance: every miss explained)."""
    f = tok.surface
    if not is_canonical(f):
        tok.miss = "notation"
        return
    stem = _stem_match(f, ix)
    if stem:
        for rx, label in _PHASE_B:
            if rx.search(f):
                tok.miss, tok.miss_detail = label, f"stem {stem[0]!r} → {stem[1][:3]}"
                return
        if len(stem[0]) >= max(3, len(key(f, "generic-H")) - 4):
            tok.miss, tok.miss_detail = "engine-gap", f"lemma {stem[1][:3]} shares stem {stem[0]!r}"
            return
    if not laryngealist and not re.search("h[₁₂₃]|H", f) and re.search("[aā]", f):
        tok.miss, tok.miss_detail = "pre-laryngeal", "a-vocalism without laryngeals"
        return
    near = difflib.get_close_matches(key(f, "generic-H"), list(ix.lemma_forms), n=3, cutoff=0.8)
    if near:
        # the lexeme is known, reconstructed differently (wl\u0325h₂néh₂ vs h₂wĺ\u0325h₂neh₂)
        tok.miss = "variant-of-known-lexeme"
        tok.miss_detail = "; ".join(f"{n} → {ix.lemma_forms[n][:2]}" for n in near)
        return
    tok.miss = "lexicon-gap"


def analyze_token(surface: str, ix: FormIndex, laryngealist: bool = True) -> Token:
    tok = Token(surface)
    if surface.startswith("-"):
        tier, an = ix.lookup(surface[1:])
        # a clitic is a particle when one is known (-kʷe "and", not the vocative of kʷos)
        an = [a for a in an if a.features == "PARTICLE"] or an
        tok.tier, tok.analyses, tok.clitic = tier, an, surface
        if not an:
            tok.miss = "lexicon-gap"
        return tok
    tier, an = ix.lookup(surface)
    if an:
        tok.tier, tok.analyses = tier, an
        return tok
    for c in CLITICS:                           # unhyphenated host+clitic
        if surface.endswith(c) and len(surface) > len(c) + 2:
            tier, an = ix.lookup(surface[: -len(c)])
            if an:
                tok.tier, tok.analyses, tok.clitic = tier, an, "-" + c
                return tok
    for aug in AUGMENTS:                        # augmented past: h₁e-bʰeret
        if surface.startswith(aug) and len(surface) > len(aug) + 2:
            tier, an = ix.lookup(surface[len(aug):])
            sec = [a for a in an if a.features.startswith(("PST", "AOR"))]
            if sec:
                tok.tier, tok.analyses, tok.augment = tier, sec, aug
                return tok
    _classify_miss(tok, ix, laryngealist)
    return tok


def _cases(tok: Token) -> set[tuple[str, str]]:
    return {tuple(a.features.split(".")[:2]) for a in tok.analyses
            if re.match(r"^(NOM|VOC|ACC|GEN|ABL|DAT|LOC|INS)\.", a.features)}


def validate_text(text: str, ix: FormIndex, laryngealist: bool = True) -> dict:
    """`laryngealist=False` for pre-laryngeal versions (Schleicher, Hirt, ...):
    only then is "pre-laryngeal" a miss class."""
    toks = [analyze_token(t, ix, laryngealist) for t in tokenize(text)]
    # Agreement heuristic: two adjacent nominal tokens that can only be
    # analyzed with disjoint case/number sets are flagged (warning only).
    agreement = []
    for a, b in zip(toks, toks[1:]):
        ca, cb = _cases(a), _cases(b)
        if ca and cb and not (ca & cb) and all(x.root_id for x in a.analyses[:1] + b.analyses[:1]):
            agreement.append(f"{a.surface} {b.surface}")
    found = [t for t in toks if t.found]
    tiers = collections.Counter(t.tier for t in found)
    misses = collections.Counter(t.miss for t in toks if not t.found)
    status = "pass" if len(found) == len(toks) and tiers.get("exact", 0) == len(found) else \
        "warn" if not any(t.miss in ("notation", "lexicon-gap") for t in toks) else "fail"
    return {
        "tokens": toks,
        "coverage": len(found) / len(toks) if toks else 1.0,
        "tiers": dict(tiers),
        "misses": dict(misses),
        "agreement_warnings": agreement,
        "status": status,
        "unknown_roots": sorted({t.surface for t in toks if t.found and not any(a.root_id for a in t.analyses)
                                 and not any(a.source == "closed" for a in t.analyses)}),
        "bad_forms": [t.surface for t in toks if not t.found],
    }
