"""Word → PIE mapping resolution: the one place where reviewed overrides meet the automatic mapping.

Every consumer resolves through this module: formula search and the 8c builders (through
pie.formula_search_multi.apply_table_overrides / apply_lemma_overrides / apply_rec_overrides, which are
thin wrappers), the Tier 2 secure check (pie/tier2_secure.py) and the mapping-precision measurement
(scripts/mapping_population.py). The audit and the checker therefore see the same population:
`iter_resolved`.

Inputs (formats unchanged):
  - automatic tables, data/research/formulas/mapping/<corpus>.jsonl: one row per corpus lemma
    {"corpus", "lang", "lemma", "word", "lex_id", "path", "how", "confidence", "sources"}; any corpus name;
  - reviewed overrides, data/research/formulas/mapping-overrides.json and mapping-overrides/*.json
    (read in that order, files sorted by name):
      {"lemma": [{"corpus", "lemma", "lex_id": [...], "erratum" / "note",
                  optional "formation": "derivative" | "same",
                  optional "uncertain": true (or "confidence": "uncertain" / "low"),
                  optional "sense": "<gloss>"}],
       "form":  [{"lang", "form", "lemma"}]}

Semantics of a lemma row (a *decision* for its corpus, lemma and sense):
  - remap: lex_id replaces the automatic ids; removal: an empty lex_id unmaps the lemma;
    addition: a row whose lemma is absent from the table adds it (status 'added');
  - "formation": "derivative": the lemma continues a derivative of the listed lexeme (Ved. mahā́nt-
    for *méǵh₂s): the mapping stands, but as another formation (the secure check counts it at root level);
  - "uncertain": the reviewer could not confirm the equation: the ids stay in the mapping (formula
    search keeps them, confidence 'low'), but they are never secure evidence;
  - "sense": the decision is about the lemma in that sense only. Without it, the sense is the gloss the
    erratum quotes after the word ("pūrs 'dowry chest' mapped to ..."). A query that names a sense is
    decided only by rows whose sense is unknown or overlaps it (pūrs 'fire', if attested, is not
    pūrs 'dowry chest'); a query without a sense (a lemma-keyed table, a citation) is decided by all
    rows of the lemma, their ids united. Several rows with the same (corpus, lemma, sense): the last one
    read wins (per-language files refine the shared errata file).
Precedence: a decision is final for its (corpus, lemma, sense). The automatic routes (tables, kaikki
links, dictionary chains, lexicon reflex lists, form lemmatizers) apply only where no decision applies;
pie/tier2_secure.py applies the decisions of every corpus of a language to every route there, so no
later route can restore what a decision removed.

BLOCKED_IDS: ids the etymology resolver attaches by key collision; no automatic mapping may use them
(an explicit override row still can).
"""

from __future__ import annotations

import collections
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES = "data/research/formulas/mapping-overrides.json"
MAPPING = "data/research/formulas/mapping"

# pie-lex-sh1es (a derivative of *seh₁- 'sow, impress') collects 'be' words (OE wesan, sindon; Goth.
# wisan; Latv. būt) and *h₁sónt- words (Goth. sunja, OE synn): mapping-errata.md, Germanic precision report
BLOCKED_IDS = frozenset({"pie-lex-sh1es"})

# corpora whose mapping is built live (no table in mapping/), with their language code
CORPUS_LANG = {"rv": "sa", "av": "sa", "hom": "grc", "grp": "grc", "lat": "la", "orv": "orv"}

_OVR_CACHE: dict = {}
_TABLE_CACHE: dict = {}


def strip_blocked(ids) -> tuple:
    return tuple(i for i in ids if i not in BLOCKED_IDS)


# ---------------------------------------------------------------- decisions

_QUOTED = re.compile(r"^\s*\S+\s+'([^']+)'")
_STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "be", "with", "by", "as", "at", "one"}


def _sense_words(s: str | None) -> set:
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if len(w) > 2 and w not in _STOP}


def senses_overlap(a: str | None, b: str | None) -> bool:
    """True when either sense is unknown or they share a content word ('dowry chest' / 'fire': False)."""
    wa, wb = _sense_words(a), _sense_words(b)
    return not wa or not wb or bool(wa & wb)


@dataclass(frozen=True)
class Decision:
    """One reviewed override row."""
    corpus: str
    lemma: str
    ids: frozenset
    formation: str | None = None          # 'derivative' | 'same' | None
    uncertain: bool = False
    sense: str | None = None
    note: str = "override"
    row: dict = field(default_factory=dict, compare=False, hash=False, repr=False)

    @property
    def removal(self) -> bool:
        return not self.ids

    @property
    def derivative(self) -> bool:
        return self.formation == "derivative"


def decision(row: dict, corpus: str | None = None, lemma: str | None = None, ids=None) -> Decision:
    sense = row.get("sense")
    if sense is None:
        m = _QUOTED.match(str(row.get("erratum") or ""))
        sense = m.group(1) if m else None
    unc = bool(row.get("uncertain")) or str(row.get("confidence", "")).lower() in ("uncertain", "low")
    return Decision(corpus if corpus is not None else row.get("corpus"), lemma if lemma is not None else row.get("lemma"),
                    frozenset(row.get("lex_id", ()) if ids is None else ids), row.get("formation"), unc, sense,
                    row.get("erratum") or row.get("note") or "override", row)


def _form_key(lang: str):
    from .formula_search_multi import KEYS
    return KEYS.get(lang) or (lambda s, loose=False: s.lower())


def load_overrides(root: Path = ROOT) -> dict:
    """{"lemma": {corpus: {lemma: (ids frozenset, row)}}, "form": {lang: {form key: lemma}},
        "decisions": {corpus: {lemma: [Decision, ...]}}} (one Decision per sense).
    "lemma" is the sense-free view: the ids of all senses of the lemma united, the last row read."""
    p = Path(root) / OVERRIDES
    if p not in _OVR_CACHE:
        d = json.loads(p.read_text("utf-8")) if p.exists() else {}
        d = {"lemma": list(d.get("lemma", [])), "form": list(d.get("form", []))}
        # per-language override files (one agent per language edits its own file):
        # data/research/formulas/mapping-overrides/<name>.json with the same {"lemma": [...], "form": [...]}
        for f in sorted((Path(root) / OVERRIDES.replace(".json", "")).glob("*.json")):
            x = json.loads(f.read_text("utf-8"))
            d["lemma"] += x.get("lemma", [])
            d["form"] += x.get("form", [])
        per: dict = collections.defaultdict(lambda: collections.defaultdict(dict))
        for r in d["lemma"]:
            dc = decision(r)
            per[dc.corpus][dc.lemma][(dc.sense or "").strip().lower() if r.get("sense") else None] = dc
        form: dict = collections.defaultdict(dict)
        for r in d["form"]:
            form[r["lang"]][_form_key(r["lang"])(r["form"])] = r["lemma"]
        _OVR_CACHE[p] = _pack({c: {lem: list(v.values()) for lem, v in rows.items()} for c, rows in per.items()},
                              dict(form))
    return _OVR_CACHE[p]


def _pack(decisions: dict, form: dict) -> dict:
    lem = {c: {l: (frozenset().union(*(x.ids for x in ds)), ds[-1].row) for l, ds in rows.items()}
           for c, rows in decisions.items()}
    return {"lemma": lem, "form": form, "decisions": decisions}


def as_overrides(ov: dict | None, root: Path = ROOT) -> dict:
    """Accept load_overrides() output, its "lemma" part ({corpus: {lemma: (ids, row)}}), or None (disk)."""
    if ov is None:
        return load_overrides(root)
    if "decisions" in ov:
        return ov
    if "lemma" in ov and isinstance(ov.get("lemma"), dict) and "form" in ov:
        lemma, form = ov["lemma"], ov["form"]
    else:
        lemma, form = ov, {}
    dec = {c: {l: [decision(row or {}, c, l, ids)] for l, (ids, row) in rows.items()} for c, rows in lemma.items()}
    return _pack(dec, form)


def decisions_for(corpus: str, lemma: str, overrides: dict | None = None, sense: str | None = None,
                  root: Path = ROOT) -> list[Decision]:
    """The decisions that apply to (corpus, lemma) in the queried sense ([] = none: the automatic mapping)."""
    ds = as_overrides(overrides, root)["decisions"].get(corpus, {}).get(lemma, [])
    if sense is None:
        return list(ds)
    return [d for d in ds if senses_overlap(d.sense, sense)]


def decide(corpus: str, lemma: str, auto_ids=(), overrides: dict | None = None, sense: str | None = None,
           root: Path = ROOT) -> tuple[frozenset, list[Decision]]:
    """(resolved ids, the decisions used). With decisions: their ids united (empty: unmapped); without:
    the automatic ids minus BLOCKED_IDS."""
    ds = decisions_for(corpus, lemma, overrides, sense, root)
    if ds:
        return frozenset().union(*(d.ids for d in ds)), ds
    return frozenset(strip_blocked(auto_ids)), []


# ---------------------------------------------------------------- resolved tables

@dataclass(frozen=True)
class Resolved:
    """One resolved mapping: a corpus lemma and its lexicon ids after the reviewed decisions."""
    corpus: str
    lang: str
    lemma: str
    word: str
    ids: frozenset
    auto_ids: frozenset                  # the automatic ids (empty for an added lemma)
    path: tuple
    how: str
    confidence: str
    sources: tuple
    status: str                          # 'auto' | 'remapped' | 'confirmed' | 'added'
    formation: str | None = None
    uncertain: bool = False
    decisions: tuple = ()

    @property
    def derivative(self) -> bool:
        return self.formation == "derivative"


def table_corpora(root: Path = ROOT) -> list[str]:
    return sorted(p.stem for p in (Path(root) / MAPPING).glob("*.jsonl"))


def read_table(corpus: str, root: Path = ROOT) -> list[dict]:
    """The automatic rows of data/research/formulas/mapping/<corpus>.jsonl ([] when there is none)."""
    p = Path(root) / MAPPING / f"{corpus}.jsonl"
    k = (p, p.stat().st_mtime_ns if p.exists() else None)
    if k not in _TABLE_CACHE:
        _TABLE_CACHE[k] = [json.loads(x) for x in p.read_text("utf-8").splitlines() if x.strip()] if p.exists() else []
    return _TABLE_CACHE[k]


def corpus_lang(corpus: str, rows: list[dict] | None = None) -> str | None:
    """A corpus's language code: the table rows' majority 'lang', else CORPUS_LANG, else None."""
    c = collections.Counter(r.get("lang") for r in rows or () if r.get("lang"))
    return c.most_common(1)[0][0] if c else CORPUS_LANG.get(corpus)


def resolve_rows(corpus: str, rows: list[dict], overrides: dict | None = None, root: Path = ROOT,
                 sense: str | None = None) -> dict[str, Resolved]:
    """{lemma: Resolved} for one corpus: its automatic rows with the decisions applied (removed lemmas
    left out), plus the lemmas that only an override row maps (status 'added')."""
    ov = as_overrides(overrides, root)
    lang = corpus_lang(corpus, rows)
    out: dict[str, Resolved] = {}
    for r in rows:
        lem = r["lemma"]
        auto = frozenset(strip_blocked(r.get("lex_id", ())))
        ids, ds = decide(corpus, lem, r.get("lex_id", ()), ov, sense, root)
        if not ids:
            continue
        if ds:
            out[lem] = _from_decisions(corpus, r.get("lang") or lang, lem, r.get("word") or lem, ids, auto, ds,
                                       r.get("path", [])[:1])
        else:
            out[lem] = Resolved(corpus, r.get("lang") or lang, lem, r.get("word") or lem, ids, auto,
                                tuple(r.get("path", ())), r.get("how", ""), r.get("confidence", ""),
                                tuple(r.get("sources", ())), "auto")
    seen = {r["lemma"] for r in rows}
    for lem in ov["decisions"].get(corpus, {}):
        if lem in seen:
            continue
        ids, ds = decide(corpus, lem, (), ov, sense, root)
        if ids:
            out[lem] = _from_decisions(corpus, lang, lem, lem, ids, frozenset(), ds, [f"{lang}:{lem}"] if lang else [])
    return out


def _from_decisions(corpus, lang, lem, word, ids, auto, ds, head) -> Resolved:
    note = "; ".join(dict.fromkeys(d.note for d in ds))
    certain = [d for d in ds if not d.uncertain and d.ids]
    unc = not certain
    deriv = bool(certain) and all(d.derivative for d in certain)
    status = "added" if not auto else "confirmed" if ids == auto else "remapped"
    return Resolved(corpus, lang, lem, word, ids, auto, tuple(head) + ("erratum:" + note,), "erratum",
                    "low" if unc else "high", ("mapping-overrides",), status,
                    "derivative" if deriv else (ds[-1].formation if ds[-1].formation == "same" else None),
                    unc, tuple(ds))


def resolve_table(corpus: str, root: Path = ROOT, overrides: dict | None = None,
                  sense: str | None = None) -> dict[str, Resolved]:
    """The resolved mapping of one corpus: data/research/formulas/mapping/<corpus>.jsonl + decisions."""
    return resolve_rows(corpus, read_table(corpus, root), overrides, root, sense)


def iter_resolved(root: Path = ROOT, corpora=None, overrides: dict | None = None):
    """Every resolved mapping (Resolved), corpus by corpus: the tables in mapping/ and the corpora that
    only override rows map (rv, hom, lat: their mapping is built live). This is THE population: the
    secure checker loads it and the precision measurement samples it."""
    ov = as_overrides(overrides, root)
    names = sorted(set(table_corpora(root)) | set(ov["decisions"]))
    for c in names:
        if corpora is not None and c not in corpora:
            continue
        yield from resolve_table(c, root, ov).values()


def removals(root: Path = ROOT, overrides: dict | None = None):
    """(corpus, lemma, Decision) of every removal row."""
    ov = as_overrides(overrides, root)
    for c, rows in ov["decisions"].items():
        for lem, ds in rows.items():
            for d in ds:
                if d.removal:
                    yield c, lem, d
