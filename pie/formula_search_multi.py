"""Formula discovery (Phase 8a), round 3: every branch with a corpus.

Three parts, each usable on its own:

  1. **Mapping** (daughter lemma → PIE lexicon entry). Sources, most
     specific first:
       chain     the daughter's own kaikki entry: inh/der/inh+/der+/uder/
                 etymon templates whose source is the daughter's ancestor
                 (Proto-Norse, Proto-Germanic, …, PIE), followed through the
                 intermediate proto-language dumps (PGmc, PCelt, PSlav,
                 PBSl, PIIr, PIran, PItal, PBryth) until a PIE term or a
                 lexicon-listed proto-form is reached
       desc      the proto-language dumps' `descendants` trees (a PGmc page
                 that lists the daughter word, not marked borrowed)
       lexicon   the lexicon's own reflex lists (PIE-page descendants)
       base      a same-language base word (one-base affix/derivation
                 template) that is itself mapped
     An entry with any borrowing template (bor, lbor, bor+, …) or with an
     inh/der from a language outside its own ancestry (der la, der gml,
     der ira-pro in Armenian, der qfa-sub …) is rejected, and so is a
     proto-form whose own page is a borrowing.
     Each mapping carries its path (e.g. non:úlfr → gem-pro:*wulfaz →
     ine-pro:*wĺ̥kʷos) and a confidence:
       high      a lexicon lexeme reached by a chain or by two agreeing sources
       medium    a lexicon root, or one source with a multi-step chain
       low       a PIE etymon our lexicon lacks (pseudo id 'kaikki:<key>'),
                 a `root` template only, or a base-word chain
  2. **Corpora** (loaders below): each yields formula_search.Token lists with
     units; the registry CORPORA gives branch, licence and unit.
  3. **N-branch scoring**: per corpus the exact one-sided test of round 2;
     per branch a stratified test over the branch's corpora; across
     branches Fisher's method over the branches where the pair co-occurs.

Nothing here executes anything from raw/; the dumps are parsed as JSON or
text only. Outputs never contain corpus text: mapping tables hold dictionary
headwords, corpus lemmas and ids; candidates hold loci.
"""

from __future__ import annotations

import bisect
import collections
import json
import math
import random
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from . import formula_search as fs
from .formula_search import PieIndex, Token, pie_key

ROOT = fs.ROOT
KD = "raw/daughters"

# ---------------------------------------------------------------- language registry (mapping side)

PROTO_NAMES = {
    "gem-pro": "Proto-Germanic", "gmw-pro": "Proto-West Germanic", "gmq-pro": "Proto-Norse",
    "cel-pro": "Proto-Celtic", "cel-bry-pro": "Proto-Brythonic", "pgl": "Primitive Irish",
    "sla-pro": "Proto-Slavic", "ine-bsl-pro": "Proto-Balto-Slavic", "bat-pro": "Proto-Baltic",
    "iir-pro": "Proto-Indo-Iranian", "ira-pro": "Proto-Iranian", "inc-pro": "Proto-Indo-Aryan",
    "itc-pro": "Proto-Italic", "grk-pro": "Proto-Hellenic", "hyx-pro": "Proto-Armenian",
    "ine-ana-pro": "Proto-Anatolian",
}
PROTO_DUMPS = {
    "gem-pro": "kaikki-protogermanic/kaikki.org-dictionary-ProtoGermanic.jsonl",
    "cel-pro": "kaikki-protoceltic/kaikki.org-dictionary-ProtoCeltic.jsonl",
    "cel-bry-pro": "kaikki-protobrythonic/kaikki.org-dictionary-ProtoBrythonic.jsonl",
    "ine-bsl-pro": "kaikki-protobaltoslavic/kaikki.org-dictionary-ProtoBaltoSlavic.jsonl",
    "sla-pro": "kaikki-protoslavic/kaikki.org-dictionary-ProtoSlavic.jsonl",
    "iir-pro": "kaikki-protoindoiranian/kaikki.org-dictionary-ProtoIndoIranian.jsonl",
    "ira-pro": "kaikki-protoiranian/kaikki.org-dictionary-ProtoIranian.jsonl",
    "itc-pro": "kaikki-protoitalic/kaikki.org-dictionary-ProtoItalic.jsonl",
    # per-language lines cut from the all-languages dump (filtered by lang_code on reading)
    "grk-pro": "kaikki-all-20261021/split/proto-hellenic.jsonl",
    "gmq-pro": "kaikki-all-20261021/split/proto-norse.jsonl",
    "gmw-pro": "kaikki-all-20261021/split/proto-west-germanic.jsonl",
    "inc-pro": "kaikki-all-20261021/split/proto-indo-aryan.jsonl",
    "ine-ana-pro": "kaikki-all-20261021/split/proto-anatolian.jsonl",
    "hyx-pro": "kaikki-all-20261021/split/proto-armenian.jsonl",
    "bat-pro": "kaikki-all-20261021/split/proto-baltic.jsonl",
}
# ancestors of each language or proto-language (nearest first); ine-pro is implicit
ANCESTORS = {
    "gem-pro": [], "gmw-pro": ["gem-pro"], "gmq-pro": ["gem-pro"],
    "cel-pro": [], "cel-bry-pro": ["cel-pro"], "pgl": ["cel-pro"],
    "ine-bsl-pro": [], "sla-pro": ["ine-bsl-pro"], "bat-pro": ["ine-bsl-pro"],
    "iir-pro": [], "ira-pro": ["iir-pro"], "inc-pro": ["iir-pro"],
    "itc-pro": [], "grk-pro": [], "hyx-pro": [], "ine-ana-pro": [],
    "non": ["gmq-pro", "gem-pro"], "ang": ["gmw-pro", "gem-pro"], "got": ["gem-pro"],
    "sga": ["pgl", "cel-pro"], "cu": ["sla-pro", "ine-bsl-pro"], "lv": ["bat-pro", "ine-bsl-pro"],
    "xcl": ["hyx-pro"], "hit": ["ine-ana-pro"], "xum": ["itc-pro"], "ae": ["ira-pro", "iir-pro"],
    "orv": ["sla-pro", "ine-bsl-pro"],
    "sa": ["inc-pro", "iir-pro"], "la": ["itc-pro"], "grc": ["grk-pro"],
}


@dataclass
class LangSpec:
    code: str                 # Wiktionary code
    name: str                 # kaikki / lexicon language name
    dump: str | tuple | None  # kaikki daughter dump(s) under raw/daughters
    lex_names: tuple          # lexicon reflex language names
    script: str = "latin"     # headword script: latin, gothic, cyrillic, armenian, cuneiform
    desc_codes: tuple = ()    # codes under which the language appears in descendants trees


LANGS = {
    "non": LangSpec("non", "Old Norse", "kaikki-oldnorse/kaikki.org-dictionary-OldNorse.jsonl",
                    ("Old Norse", "Old Icelandic", "Old West Norse"), desc_codes=("non",)),
    "ang": LangSpec("ang", "Old English", "kaikki-oldenglish/kaikki.org-dictionary-OldEnglish.jsonl",
                    ("Old English",), desc_codes=("ang",)),
    "got": LangSpec("got", "Gothic", "kaikki-gothic/kaikki.org-dictionary-Gothic.jsonl", ("Gothic",),
                    script="gothic", desc_codes=("got",)),
    "sga": LangSpec("sga", "Old Irish", "kaikki-oldirish/kaikki.org-dictionary-OldIrish.jsonl",
                    ("Old Irish",), desc_codes=("sga",)),
    "cu": LangSpec("cu", "Old Church Slavonic",
                   "kaikki-oldchurchslavonic/kaikki.org-dictionary-OldChurchSlavonic.jsonl",
                   ("Old Church Slavonic",), script="cyrillic", desc_codes=("cu",)),
    "orv": LangSpec("orv", "Old East Slavic",
                    "kaikki-oldeastslavic/kaikki.org-dictionary-OldEastSlavic.jsonl",
                    ("Old East Slavic",), script="cyrillic", desc_codes=("orv",)),
    "lv": LangSpec("lv", "Latvian", "kaikki-latvian/kaikki.org-dictionary-Latvian.jsonl", ("Latvian",),
                   desc_codes=("lv",)),
    "xcl": LangSpec("xcl", "Old Armenian", "kaikki-oldarmenian/kaikki.org-dictionary-OldArmenian.jsonl",
                    ("Old Armenian",), script="armenian", desc_codes=("xcl",)),
    "hit": LangSpec("hit", "Hittite", "kaikki-hittite/kaikki.org-dictionary-Hittite.jsonl", ("Hittite",),
                    script="cuneiform", desc_codes=("hit",)),
    "xum": LangSpec("xum", "Umbrian", "kaikki-umbrian/kaikki.org-dictionary-Umbrian.jsonl", ("Umbrian",),
                    desc_codes=("xum",)),
    "ae": LangSpec("ae", "Avestan", ("kaikki-all-20261021/split/avestan.jsonl",
                                      "kaikki-all-20261021/split/old-avestan.jsonl",
                                      "kaikki-all-20261021/split/younger-avestan.jsonl"),
                   ("Avestan", "Old Avestan", "Younger Avestan"), script="avestan",
                   desc_codes=("ae", "ae-old", "ae-yng")),
}

_LINK = ("inh", "inh+", "der", "der+", "uder")
_BOR = ("bor", "bor+", "lbor", "lbor+", "slbor", "obor", "ubor", "learned borrowing", "semi-learned borrowing",
        "clq", "calque", "pcal", "translit")       # sl (semantic loan) keeps the inherited etymon
_AFFIX = ("af", "affix", "suffix", "prefix", "confix", "suf", "pre")


def _strip_inline(s: str) -> str:
    """`*ḱom-o-<id:x>` → `*ḱom-o-`; stray brackets of nested etymon syntax off."""
    s = re.sub(r"<[^>]*>", "", s or "")
    return re.sub(r"[<>\[\]'\n]", "", s.split("<")[0]).strip()


def _etymon_parts(a: dict) -> list[tuple[str, str, str]]:
    """{{etymon|non|:inh|gmq-pro:*ᚹᚢᛚᚠᚨᛉ}} (alias {{ety}}) → [('inh', 'gmq-pro', '*ᚹᚢᛚᚠᚨᛉ')]:
    numbered args from 2 on; ':kind' sets the relation for the targets after it."""
    out, kind = [], None
    for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int):
        v = (a[k] or "").strip()
        if v.startswith(":"):
            kind = v[1:].split("<")[0] or None
        elif ":" in v.split("<")[0] and not v.startswith("*"):
            code, term = v.split(":", 1)
            out.append((kind, code.strip(), _strip_inline(term)))
    return out


@dataclass
class Entry:
    """The etymological links of one kaikki entry (no definitions, no examples)."""
    word: str
    pos: str
    roman: str | None = None
    canon: str | None = None
    links: list = field(default_factory=list)      # [(code, term, template)] from ancestor languages
    roots: list = field(default_factory=list)      # PIE {{root}} terms
    bases: list = field(default_factory=list)      # same-language base words
    rejected: str | None = None                    # reason (borrowing; foreign source without an inherited link)
    disputed: str | None = None                    # foreign source beside an inherited link (alternative etymologies)
    form_of: list = field(default_factory=list)    # lemma words this entry is an inflected form of
    forms: list = field(default_factory=list)      # inflected forms (for lemmatizers; memory only)
    glosses: str = ""                              # first sense glosses (memory only; Hittite gloss check)


def parse_entry(d: dict, lang: str, keep_forms: bool = False) -> Entry:
    """One wiktextract entry → Entry. `lang` is its Wiktionary code."""
    anc = set(ANCESTORS.get(lang, [])) | {"ine-pro"}
    e = Entry(d.get("word") or "", d.get("pos") or "")
    for f in d.get("forms") or []:
        tags = f.get("tags") or []
        if "romanization" in tags and not e.roman:
            e.roman = f.get("form")
        elif "canonical" in tags and not e.canon:
            e.canon = f.get("form")
        elif keep_forms and f.get("form") and not set(tags) & {"table-tags", "inflection-template", "class",
                                                                "romanization"}:
            e.forms.append(f["form"])
    e.glosses = " ; ".join(g for s in (d.get("senses") or [])[:4] for g in (s.get("glosses") or [])[:1])[:300]
    for s in d.get("senses") or []:
        for fo in (s.get("form_of") or []) + (s.get("alt_of") or []):
            if fo.get("word"):
                e.form_of.append(fo["word"])
    foreign = []
    for t in d.get("etymology_templates") or []:
        name, a = t.get("name"), t.get("args") or {}
        if name in _BOR:
            e.rejected = e.rejected or f"{name}:{a.get('2')}"
            continue
        if name in ("etymon", "ety"):
            for kind, code, term in _etymon_parts(a):
                if kind in ("bor", "lbor", "slbor", "calque", "obor"):
                    e.rejected = e.rejected or f"etymon-{kind}:{code}"
                elif kind in ("inh", "der") and code and term:
                    if code in anc:
                        e.links.append((code, term, "etymon"))
                    elif code != lang:
                        foreign.append(code)
            continue
        if a.get("1") != lang:
            continue
        if name in _LINK:
            src = a.get("2")
            term = _strip_inline(a.get("3") or a.get("4") or "")
            if not src or src == "-":
                continue
            if src in anc:
                if term and term != "-":
                    e.links.append((src, term, name))
            elif src == lang:
                if term:
                    e.bases.append(term)
            else:
                foreign.append(src)
        elif name == "root":
            if a.get("2") == "ine-pro":
                e.roots += [_strip_inline(a[k]) for k in sorted((k for k in a if k.isdigit() and int(k) >= 3), key=int)
                            if _strip_inline(a[k])]
        elif name in _AFFIX:
            parts = [_strip_inline(a[k]) for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int)]
            parts = [p for p in parts if p]
            if name in ("suffix", "suf"):
                content = parts[:1]
            elif name in ("prefix", "pre"):
                content = parts[-1:]
            else:
                content = [p for p in parts if not p.startswith("-") and not p.endswith("-")]
            if len(content) == 1:
                e.bases.append(content[0])
    if foreign and not e.rejected:
        why = "foreign source: " + ",".join(sorted(set(foreign)))
        if e.links:
            e.disputed = why
        else:
            e.rejected = why
    return e


def read_dump(paths, lang: str, keep_forms: bool = False, codes=None) -> list[Entry]:
    """Entries of one language from one or more dumps (lines of other
    languages, present in the split all-languages files, are skipped)."""
    codes = set(codes or [lang])
    out = []
    for path in [paths] if isinstance(paths, (str, Path)) else paths:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                if d.get("lang_code") not in codes:
                    continue
                out.append(parse_entry(d, lang, keep_forms))
    return out


def _walk_desc(nodes, proto_code: str, proto_term: str, want: set, out: dict, borrowed: bool = False):
    for n in nodes or []:
        tags = set(n.get("raw_tags") or []) | set(n.get("tags") or [])
        b = borrowed or bool({"borrowed", "learned borrowing", "calque", "semi-learned borrowing"} & tags)
        code = n.get("lang_code")
        w = n.get("word")
        if code in want and w and not b:
            out[code].append((w.lstrip("*"), n.get("roman"), proto_code, proto_term))
        _walk_desc(n.get("descendants"), proto_code, proto_term, want, out, b)


class ProtoDB:
    """Proto-language entries (links only) and their descendants lists."""

    def __init__(self, root: Path = ROOT, codes=None, want_desc=()):
        self.entries: dict[tuple[str, str], list[Entry]] = collections.defaultdict(list)
        self.desc: dict[str, list] = collections.defaultdict(list)
        want = set(want_desc)
        for code, rel in PROTO_DUMPS.items():
            if codes is not None and code not in codes:
                continue
            with open(root / KD / rel, encoding="utf-8") as fh:
                for line in fh:
                    d = json.loads(line)
                    if d.get("lang_code") not in (None, code):
                        continue
                    e = parse_entry(d, code)
                    self.entries[(code, PieIndex.proto_key(e.word))].append(e)
                    if want and d.get("descendants"):
                        _walk_desc(d["descendants"], code, e.word, want, self.desc)

    def get(self, code: str, term: str) -> list[Entry]:
        return self.entries.get((code, PieIndex.proto_key(term)), [])


@dataclass
class Hit:
    ids: frozenset
    path: tuple            # ("non:úlfr", "gem-pro:*wulfaz", "ine-pro:*wĺ̥kʷos")
    how: str               # chain | root | pseudo | desc | lexicon | base
    steps: int
    disputed: bool = False

    @property
    def specific(self) -> bool:
        return not self.how.startswith("pseudo") and self.how != "root"


class Resolver:
    """Follows a (code, term) to PIE lexicon ids."""

    def __init__(self, idx: PieIndex, protos: ProtoDB, kinds: dict, pseudo: bool = True):
        self.idx, self.protos, self.kinds, self.pseudo = idx, protos, kinds, pseudo
        self.memo: dict = {}

    def _pie(self, term: str) -> tuple[set, str]:
        ids = self.idx.pie(term)
        if ids:
            lex = {i for i in ids if self.kinds.get(i) != "root"}
            return (lex or ids), ("lexeme" if lex else "root")
        if self.pseudo and (pid := fs.pseudo_id(term)):
            return {pid}, "pseudo"
        return set(), ""

    def resolve(self, code: str, term: str, depth: int = 0) -> Hit | None:
        key = (code, PieIndex.proto_key(term))
        if key in self.memo:
            return self.memo[key]
        self.memo[key] = None                      # cycle guard
        hit = None
        if code == "ine-pro":
            ids, kind = self._pie(term)
            if ids:
                hit = Hit(frozenset(ids), (f"ine-pro:{term}",), {"lexeme": "chain", "root": "root",
                                                               "pseudo": "pseudo"}[kind], 0)
        elif depth < 5:
            L = PROTO_NAMES.get(code)
            lex = self.idx.proto.get((L, PieIndex.proto_key(term))) if L else None
            lex_hit = Hit(frozenset(lex), (f"{code}:{term}", "lexicon-reflex"), "chain", 1) if lex else None
            sub = None
            ents = self.protos.get(code, term)
            if ents and all(e.rejected for e in ents):
                self.memo[key] = None
                return None
            for e in ents:
                if e.rejected:
                    continue
                h = self.entry_hit(e, code, depth + 1)
                if h and (sub is None or _better(h, sub)):
                    sub = h
            if sub:
                sub = Hit(sub.ids, (f"{code}:{term}",) + sub.path, sub.how, sub.steps + 1, sub.disputed)
            # the lexicon's reflex list names the lexeme directly; prefer it over a root- or pseudo-level chain
            hit = lex_hit if lex_hit and (sub is None or not sub.specific or sub.how != "chain") else sub
            if lex_hit and sub and sub.how == "chain" and sub.ids & lex_hit.ids:
                hit = Hit(sub.ids & lex_hit.ids, sub.path, "chain", sub.steps, sub.disputed)
        self.memo[key] = hit
        return hit

    def entry_hit(self, e: Entry, code: str, depth: int = 0) -> Hit | None:
        best = None
        for src, term, _ in e.links:
            h = self.resolve(src, term, depth)
            if h and (best is None or _better(h, best)):
                best = h
        if best and e.disputed and not best.disputed:
            best = Hit(best.ids, best.path, best.how, best.steps, True)
        if (best is None or not best.specific) and e.roots:
            for t in e.roots:
                ids = self.idx.pie(t, roots_only=True)
                if ids:
                    h = Hit(frozenset(ids), (f"ine-pro:{t}",), "root", 0)
                    if best is None or best.how.startswith("pseudo"):
                        best = h
                    break
        return best


_HOW_RANK = {"chain": 0, "lexicon": 1, "desc": 2, "root": 3, "base": 4, "pseudo": 5}


def _better(a: Hit, b: Hit) -> bool:
    ra, rb = _HOW_RANK.get(a.how.split("-")[0], 9), _HOW_RANK.get(b.how.split("-")[0], 9)
    return (ra, a.steps) < (rb, b.steps)


def confidence(h: Hit, agree: bool) -> str:
    if h.disputed or h.how.startswith("pseudo") or h.how in ("base",):
        return "low"
    if h.how == "root":
        return "low" if not agree else "medium"
    if agree or (h.how in ("chain", "lexicon") and h.steps <= 2):
        return "high"
    return "medium"


# ---------------------------------------------------------------- word keys per language

def _nfd_strip(s: str, keep: str = "") -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c) or c in keep)


def key_non(s: str, loose: bool = False) -> str:
    """Old Norse: lowercase; ǫ ö ø œ → ö / æ; ð/þ kept; accents kept unless loose."""
    s = unicodedata.normalize("NFC", (s or "").lower().strip("*-"))
    s = s.replace("ǫ", "ö").replace("ø", "ö").replace("œ", "æ").replace("ę", "æ").replace("ǿ", "ö")
    s = s.replace("ȩ", "æ").replace("ꝍ", "ö").replace("ǽ", "æ")
    if loose:
        s = _nfd_strip(s)
    return re.sub(r"[^a-zþðæöáéíóúýǽ]", "", unicodedata.normalize("NFC", s)) if not loose else \
        re.sub(r"[^a-zþðæö]", "", s)


def key_ang(s: str, loose: bool = False) -> str:
    """Old English: lowercase, ƿ → w, ð → þ, ġ/ċ dots off, length marks kept
    as macrons (acute = macron) unless loose."""
    s = unicodedata.normalize("NFD", (s or "").lower().strip("*-")).replace("ƿ", "w").replace("ð", "þ")
    out = []
    for c in s:
        if unicodedata.combining(c):
            if c in "̄́" and not loose:
                out.append("̄")
            continue
        out.append(c)
    s = unicodedata.normalize("NFC", "".join(out)).replace("ǣ", "ǣ")
    return re.sub(r"[^a-zþæāēīōūȳǣ]", "", s)


_GOT = dict(zip("𐌰𐌱𐌲𐌳𐌴𐌵𐌶𐌷𐌸𐌹𐌺𐌻𐌼𐌽𐌾𐌿𐍀𐍁𐍂𐍃𐍄𐍅𐍆𐍇𐍈𐍉𐍊",
                ["a", "b", "g", "d", "e", "q", "z", "h", "þ", "i", "k", "l", "m", "n", "j", "u", "p", "", "r", "s",
                 "t", "w", "f", "x", "ƕ", "o", ""]))


def key_got(s: str, loose: bool = False) -> str:
    """Gothic: Gothic script transliterated, macrons and diaeresis off, hw → ƕ."""
    s = "".join(_GOT.get(c, c) for c in (s or "").lower())
    s = _nfd_strip(s).replace("hw", "ƕ")
    return re.sub(r"[^a-zþƕ]", "", s)


def key_cu(s: str, loose: bool = False) -> str:
    """OCS (Cyrillic): lowercase, combining marks (titlo, palatalization
    hooks, accents) off, variant letters unified."""
    s = _nfd_strip((s or "").lower())
    for a, b in (("ꙑ", "ꙑ"), ("ъі", "ꙑ"), ("ы", "ꙑ"), ("ѹ", "оу"), ("ꙋ", "оу"), ("у", "оу"), ("ꙗ", "ѧ"),
                 ("ѥ", "е"), ("є", "е"), ("ꙁ", "з"), ("ѕ", "з"), ("ꙃ", "з"), ("і", "и"), ("ї", "и"), ("ѵ", "и"),
                 ("ѡ", "о"), ("ѿ", "от"), ("ꙩ", "о"), ("ꙫ", "о"), ("ꙭ", "о"), ("ꚙ", "о"), ("ꙮ", "о"),
                 ("ꙇ", "и"), ("ѣ", "ѣ"), ("ꙙ", "ѧ"), ("ѩ", "ѧ"), ("ѭ", "ѫ"), ("ꙛ", "ѫ"), ("ꙝ", "ѫ"),
                 ("ѳ", "ф"), ("ѯ", "кс"), ("ѱ", "пс"), ("ꙿ", ""), ("ⸯ", ""), ("ꙻ", ""), ("ҁ", "с")):
        s = s.replace(a, b)
    s = s.replace("оуоу", "оу")
    return re.sub(r"[^а-яꙑѣѧѫѩѭ]", "", s)


def key_xcl(s: str, loose: bool = False) -> str:
    """Classical Armenian: PROIEL's Latin transliteration and Wiktionary's
    romanization unified (ʻ ' ’ → ʿ; PROIEL r̄ → ṙ, ow → u)."""
    s = unicodedata.normalize("NFC", (s or "").lower().replace("r̄", "ṙ"))
    s = s.replace("ʻ", "ʿ").replace("'", "ʿ").replace("’", "ʿ").replace("ʼ", "ʿ").replace("ow", "u")
    return re.sub(r"[^a-zʿčšžłǰṙēəõ]", "", s)


def key_hit(s: str, loose: bool = False) -> str:
    """Hittite: lowercase, ḫ → h, š → s, length off, no hyphens or
    subscripts, geminates single (spellings vary: ḫatteššar / ḫateššar)."""
    s = (s or "").lower().replace("ḫ", "h").replace("š", "s")
    s = _nfd_strip(s)
    s = re.sub(r"[₀-₉0-9]", "", s)
    s = re.sub(r"[^a-z]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)


_HIT_ROM_END = re.compile(r"(?:zi|tari|ari|tta|mi|ši|i|aš|iš|uš|an|a|ar)$")


def hit_entry_stems(roman: str) -> list[str]:
    """kaikki Hittite citation forms (3sg. pres. or nom. sg.) → stem keys:
    pāi → pa, peššezzi → pese, attaš → at/ata, wātar → watar."""
    k = key_hit(roman)
    out = [k]
    m = _HIT_ROM_END.search(k)
    if m and len(k) - len(m[0]) >= 2:
        out.append(k[: len(k) - len(m[0])])
    if k.endswith(("as", "is", "us")) and len(k) > 3:
        out.append(k[:-1])                       # attaš → atta
    return [x for x in dict.fromkeys(out) if len(x) >= 2]


def hit_tlh_keys(lemma: str) -> list[str]:
    """TLHdig lemma (`ēd-/ad-`, `att=a-`, `ḫatt=eššar`) → keys: each stem as
    written, then without its stem vowel."""
    out = []
    for st in hit_lemma_stems(lemma):
        k = key_hit(st)
        out.append(k)
        if "=" in lemma and len(k) > 3 and k[-1] in "aiue":
            out.append(k[:-1])
    return [x for x in dict.fromkeys(out) if len(x) >= 2]


def key_xum(s: str, loose: bool = False) -> str:
    """Umbrian: lowercase, Latin-alphabet spelling; ç ř kept; macrons off."""
    s = _nfd_strip((s or "").lower(), keep="̧̌")
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"[^a-zçřš]", "", s)


def key_lv(s: str, loose: bool = False) -> str:
    """Latvian: lowercase, tone marks off (macrons, carons, cedillas kept)."""
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c) or c in "̧̄̌")
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"[^a-zāēīūčšžģķļņŗō]", "", s)


def key_sga(s: str, loose: bool = False) -> str:
    """Old Irish: lowercase, length marks kept (acute) unless loose, no
    hyphens, middle dots or punctuation."""
    s = unicodedata.normalize("NFC", (s or "").lower())
    if loose:
        s = _nfd_strip(s)
    return re.sub(r"[^a-záéíóúṡḟ]", "", s)


def key_ae(s: str, loose: bool = False) -> str:
    """Avestan transliteration (CAB / Wiktionary): lowercase, ϑ/θ → θ,
    nasal marks unified, no dots/hyphens; loose drops length."""
    s = unicodedata.normalize("NFC", (s or "").lower()).replace("ϑ", "θ").replace("t̰", "t").replace("ṱ", "t")
    s = s.replace("ɱ", "m").replace("ŋ́", "ŋ").replace("ŋᵛ", "ŋ").replace("ṇ", "n").replace("ń", "n")
    s = s.replace("ẏ", "y").replace("ii", "y").replace("uu", "v").replace("x́", "x").replace("xᵛ", "xv")
    if loose:
        s = _nfd_strip(s).replace("ə", "e").replace("ą", "a")
    return re.sub(r"[^a-zəąåāēīōūθδγšžčǰŋβšṣ]", "", s)


KEYS = {"non": key_non, "ang": key_ang, "got": key_got, "cu": key_cu, "orv": key_cu, "xcl": key_xcl, "hit": key_hit,
        "xum": key_xum, "lv": key_lv, "sga": key_sga, "ae": key_ae}


def entry_keys(e: Entry, lang: str) -> list[str]:
    """Join keys for an entry: transliterated scripts join on the
    romanization, Latin-script languages on the headword."""
    k = KEYS[lang]
    if LANGS[lang].script in ("gothic",):
        return [x for x in {k(e.word)} if x]
    if lang == "hit":
        roms = [e.roman or ""] + [f for f in e.forms if re.search(r"[a-zāēīū]", f) and "-" not in f][:1]
        return [x for r in roms if r for x in hit_entry_stems(r)]
    if LANGS[lang].script in ("armenian", "cuneiform"):
        return [x for x in {k(e.roman or "")} if x]
    if LANGS[lang].script == "cyrillic":
        return [x for x in {k(e.word), k(e.canon or "")} if x]
    return [x for x in {k(e.word), k(e.canon or "")} if x]


# ---------------------------------------------------------------- building a language's mapping table

@dataclass
class MapRec:
    key: str
    word: str
    ids: frozenset
    path: tuple
    how: str
    confidence: str
    sources: tuple
    gloss: str = ""


CONTENT_POS = {"noun", "verb", "adj", "name", "root"}


class LangMapping:
    """key → MapRec for one daughter language, plus a form → lemma-key
    lemmatizer for unlemmatized corpora."""

    def __init__(self, lang: str):
        self.lang = lang
        self.recs: dict[str, MapRec] = {}
        self.rejected: dict[str, str] = {}
        self.forms: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        self.lemma_words: set = set()
        self.pos: dict[str, set] = collections.defaultdict(set)

    def is_content(self, lemma: str) -> bool:
        """A lemma string ('a|b') is content if every part's dictionary POS
        are noun, verb, adjective or name only (unknown forms count as content)."""
        if lemma.startswith("?"):
            return True
        parts = lemma.split("|")
        known = [p for p in parts if self.pos.get(p)]
        # a homograph of a function word (ON ok 'and' / 'yoke', á 'on' / 'river') is not content
        return not known or all(self.pos[p] <= CONTENT_POS for p in known)

    def lookup(self, key: str) -> MapRec | None:
        return self.recs.get(key)


def build_lang_mapping(lang: str, lexicon: list[dict], protos: ProtoDB, root: Path = ROOT,
                       entries: list[Entry] | None = None, pseudo: bool = True,
                       idx: PieIndex | None = None, strict_homographs: bool | None = None) -> LangMapping:
    """strict_homographs (default: Hittite only): a key whose candidate
    words disagree on the etymon gets no mapping, instead of their union
    (Hittite citation forms collide once endings are stripped: pāi 'gives' /
    paizzi 'goes')."""
    if strict_homographs is None:
        strict_homographs = lang == "hit"
    spec = LANGS[lang]
    idx = idx or PieIndex(lexicon)
    kinds = {e["id"]: e.get("kind") for e in lexicon}
    res = Resolver(idx, protos, kinds, pseudo)
    K = KEYS[lang]
    if entries is None:
        dumps = [spec.dump] if isinstance(spec.dump, str) else list(spec.dump or [])
        entries = read_dump([root / KD / d for d in dumps], lang, keep_forms=True,
                            codes=spec.desc_codes or (lang,)) if dumps else []
    lm = LangMapping(lang)
    cands: dict[str, list[tuple]] = collections.defaultdict(list)   # key → (hit, source, word, gloss)
    bad: dict[str, str] = {}
    # 1. the daughter's own entries (chain)
    by_key_entries: dict[str, list[Entry]] = collections.defaultdict(list)
    for e in entries:
        keys = entry_keys(e, lang)
        for k in keys:
            by_key_entries[k].append(e)
        if e.form_of:
            for f in [e.word] + e.forms:
                for fk in {K(f), K(f, True)}:
                    for lw in e.form_of:
                        lm.forms[fk][K(lw)] += 1
            continue
        lm.lemma_words.update(keys)
        for k in keys:
            lm.pos[k].add(e.pos)
        for f in [e.word, e.canon or "", *e.forms]:
            for fk in {K(f), K(f, True)}:
                if fk:
                    for k in keys:
                        lm.forms[fk][k] += 1
        if e.rejected:
            for k in keys:
                bad[k] = e.rejected
            continue
        h = res.entry_hit(e, lang)
        if h:
            for k in keys:
                cands[k].append((Hit(h.ids, (f"{lang}:{e.word}",) + h.path, h.how, h.steps, h.disputed),
                                  "chain", e.word, e.glosses))
    # 2. descendants trees of proto-language pages
    for code in spec.desc_codes:
        for w, rom, pc, pt in protos.desc.get(code, []):
            h = res.resolve(pc, pt)
            if not h:
                continue
            for k in {K(w), K(rom or "")} if spec.script in ("latin", "avestan") else \
                    ({K(rom or "")} if spec.script in ("armenian", "cuneiform") else {K(w)}):
                if k:
                    cands[k].append((Hit(h.ids, (f"{lang}:{w}",) + h.path, "desc", h.steps + 1, h.disputed),
                                      "desc", w, ""))
    # 3. lexicon reflexes (PIE-page descendants)
    for le in lexicon:
        if le.get("kind") == "affix":
            continue
        for L in spec.lex_names:
            for r in (le.get("reflexes") or {}).get(L, []):
                if r.get("borrowed") or r.get("uncertain"):
                    continue
                forms = [r.get("form") or ""]
                if spec.script != "latin" or lang == "ae":
                    forms.append(r.get("roman") or "")
                for f in forms:
                    keys = hit_entry_stems(f) if lang == "hit" else [K(f.lstrip("*"))]
                    for k in keys:
                        if k and len(k) >= 2:
                            ids = {le["id"]} if le.get("kind") != "alt" else set(le.get("target_ids") or [le["id"]])
                            cands[k].append((Hit(frozenset(ids), (f"{lang}:{f}", f"ine-pro:*{le['form']}"),
                                                 "lexicon", 1), "lexicon", f, "; ".join(le.get("meaning") or [])))
    # combine
    for k, lst in cands.items():
        if k in bad and all(x[1] == "desc" for x in lst):
            continue                 # a borrowed homograph vetoes a descendants-tree-only link
        spec_hits = [x for x in lst if x[0].specific]
        pool = spec_hits or lst
        best = min(pool, key=lambda x: (_HOW_RANK.get(x[0].how.split("-")[0], 9), x[0].steps))
        same_how = [x for x in pool if x[0].how == best[0].how]
        if strict_homographs and len({x[0].ids for x in pool}) > 1:
            continue
        ids = frozenset().union(*(x[0].ids for x in same_how))
        srcs = tuple(sorted({x[1] for x in lst}))
        agree = len({x[1] for x in lst if x[0].ids & best[0].ids}) >= 2
        gl = " ; ".join(x[3] for x in lst if x[3])[:400]
        lm.recs[k] = MapRec(k, best[2], ids, best[0].path, best[0].how, confidence(best[0], agree), srcs, gl)
    lm.rejected = {k: v for k, v in bad.items() if k not in lm.recs}
    # 4. an entry that is a form or spelling of a mapped lemma (Arm. erkin → erkinkʿ)
    word_keys: dict[str, list] = collections.defaultdict(list)
    for e in entries:
        if not e.form_of:
            word_keys[e.word] += entry_keys(e, lang)
    for e in entries:
        if not e.form_of:
            continue
        for k in entry_keys(e, lang):
            if k in lm.recs:
                continue
            for w in e.form_of:
                hit = next((lm.recs[x] for x in word_keys.get(w, []) + [K(w)] if x in lm.recs), None)
                if hit:
                    lm.recs[k] = MapRec(k, e.word, hit.ids, (f"{lang}:{e.word}", f"form-of:{w}") + hit.path[1:],
                                        hit.how, hit.confidence, hit.sources + ("form-of",), hit.gloss)
                    break
    # 5. base-word chains (diminutives, one-base derivations), two passes
    for _ in range(2):
        for e in entries:
            if e.rejected or e.form_of:
                continue
            for k in entry_keys(e, lang):
                if k in lm.recs:
                    continue
                for b in e.bases:
                    bk = K(b.lstrip("√*"))
                    hit = lm.recs.get(bk)
                    if hit and bk != k and hit.how != "base":
                        lm.recs[k] = MapRec(k, e.word, hit.ids, (f"{lang}:{e.word}", f"base:{b}") + hit.path,
                                            "base", "low", ("base",))
                        break
    return lm


# ---------------------------------------------------------------- corpora
#
# Every loader returns formula_search.Token lists. `lemma` is the corpus's own
# lemma (lemmatized corpora) or the lemma key found by the kaikki forms table
# (unlemmatized ones; '?' + surface key when unknown). Units are named in
# Token.units; CORPORA says which unit the search uses.

PROIEL_DIR = "raw/daughters/syntacticus-proiel-torot/extract/syntacticus-treebank-data-20230428"
_P_TOKEN = re.compile(r"<token ([^>]*?)/?>")
_ATTR_H = re.compile(r'([\w:-]+)="([^"]*)"')


def load_proiel(files: list[str], corpus: str, root: Path = ROOT) -> list[Token]:
    """PROIEL/TOROT XML (research-only licence: lemmas and loci are used, no
    text is written out). Unit: sentence; locus: source + citation-part.
    Content words: common/proper nouns, adjectives, verbs."""
    toks: list[Token] = []
    for rel in files:
        text = (root / PROIEL_DIR / rel).read_text("utf-8")
        src = Path(rel).stem
        for chunk in text.split("<sentence ")[1:]:
            m = re.match(r'id="(\d+)"', chunk)
            sid = m[1] if m else str(len(toks))
            local, heads = {}, []
            for tm in _P_TOKEN.finditer(chunk):
                a = dict(_ATTR_H.findall(tm[1]))
                if "empty-token-sort" in a or not a.get("lemma") or a.get("lemma") == "?":
                    continue
                pos = a.get("part-of-speech", "")
                lemma = a["lemma"].split("#")[0]
                coarse = {"N": "noun", "A": "adj", "V": "verb"}.get(pos[:1], "other")
                morph = a.get("morphology", "") or "-" * 10
                if coarse == "verb" and len(morph) > 3 and morph[3] == "p":
                    coarse = "adj"
                local[a.get("id")] = len(toks)
                heads.append((len(toks), a.get("head-id")))
                case = {"n": "NOM", "g": "GEN", "d": "DAT", "a": "ACC", "v": "VOC", "b": "ABL", "i": "INS",
                        "l": "LOC"}.get(morph[6:7]) if len(morph) > 6 else None
                toks.append(Token(corpus, lemma, "", f"{src} {a.get('citation-part', '')}".strip(),
                                  {"sentence": f"{src}.{sid}", "verse": f"{a.get('citation-part', '')}",
                                   "book": src},
                                  pos[:1] in ("N", "A", "V"), coarse, case,
                                  {"s": "SG", "p": "PL", "d": "DU"}.get(morph[1:2]),
                                  finite=morph[3:4] in ("i", "s", "m", "o"), rel=a.get("relation")))
            for i, h in heads:
                toks[i].head = local.get(h)
    return toks


DCS_DIR = "raw/daughters/dcs-hellwig/extract/sanskrit-8aeed5a1343d0e48b64eb32af8c00e8c6eb29359/dcs/data/conllu/files"
DCS_VEDIC = ("Atharvaveda (Śaunaka)", "Atharvaveda (Paippalāda)", "Ṛgvedakhilāni")
DCS_CONTENT = {"NOUN", "VERB", "ADJ", "PROPN"}


# ---- DCS sentence locus → verse citation
#
# The DCS locus 'AVŚ, 8, 6.s48' is the 48th *sentence* of the chapter (hymn)
# AVŚ 8.6, not its verse: a DCS sentence is one text line, usually a
# half-verse. The CoNLL-U comment headers carry the verse where DCS has it:
#   `# sent_counter = 23` / `# sent_subcounter = 1`  → verse 23, its 1st line.
# About a quarter of the Atharvaveda chapters (and a few sentences in others)
# lack the counters; their sent_id is '<line id>_<k>' (k-th sentence of DCS
# text line <line id>). Line ids are consecutive within a chapter, so such a
# line is placed exactly when the numbered lines around it leave one choice
# ('bracketed'). Otherwise the verse is *inferred* by a segmentation of the
# chapter's lines into verses (line-count prior, syllable length, the hymn's
# stanza count from Whitney's translation where available): a heuristic,
# flagged as such, never to be cited as a verse number without checking.
# Statuses: counter | bracketed | inferred | unmapped.

DCS_ABBR = {"Atharvaveda (Śaunaka)": "AVŚ", "Atharvaveda (Paippalāda)": "AVP", "Ṛgvedakhilāni": "ṚVKh"}
DCS_LOCUS = re.compile(r"(AVŚ|AVP|ṚVKh),? (\d+), (\d+)\.s(\d+)")
DCS_WHITNEY = "raw/daughters/dcs-hellwig/extract/sanskrit-8aeed5a1343d0e48b64eb32af8c00e8c6eb29359/dcs/data/atharvaveda-shaunaka/translations/whitney.txt"
_DCS_SYL = re.compile(r"ai|au|[aāiīuūṛṝḷeoAĀIĪUŪṚṜḶEO]")
# −log prior of a verse of k DCS lines (counted over the numbered AVŚ/AVP chapters)
_DCS_K_COST = {1: 1.8, 2: 0.0, 3: 2.7, 4: 5.0, 5: 5.5, 6: 6.0, 7: 6.0}
# (accuracy with the counters hidden: scripts/build_av_erratum.py, '_validation' in its output)
_DCS_LAMBDA = 3.0


def _dcs_int(v: str) -> int | None:
    v = v.split("=", 1)[1].strip() if "=" in v else v.strip()
    return int(v) if v.isdigit() else None


def dcs_sentence_heads(text: str) -> tuple[str | None, list[dict]]:
    """One DCS CoNLL-U chapter file → (chapter name, its sentences in file
    order: sent_id, line id, counter, subcounter, text). Headers only."""
    chapter, out, cur_text = None, [], ""
    for line in text.splitlines():
        if line.startswith("## chapter:"):
            chapter = line.split(":", 1)[1].strip()
        elif line.startswith("# text ="):
            cur_text = line.split("=", 1)[1].strip()
        elif line.startswith("# sent_id"):
            sid = line.split("=", 1)[1].strip()
            head = sid.split("_")[0]
            out.append({"sent_id": sid, "line_id": int(head) if head.isdigit() else None,
                        "counter": None, "sub": None, "text": cur_text})
            cur_text = ""
        elif line.startswith("# sent_counter") and out:
            out[-1]["counter"] = _dcs_int(line)
        elif line.startswith("# sent_subcounter") and out:
            out[-1]["sub"] = _dcs_int(line)
    return chapter, out


def _dcs_syl(s: str) -> int:
    return len(_DCS_SYL.findall(s))


def _dcs_segment(n: int, syl: list[float], anchors: dict, n_verses: int | None,
                 present: list[bool] | None = None) -> list[tuple[int, int, int]] | None:
    """Split lines 0..n-1 into consecutive verses (each 1–7 lines), honouring
    anchors {line index: (verse, line-in-verse)}; cost = prior on the number
    of lines present in the DCS + λ·|log(verse syllables / target)|. Line ids
    absent from the chapter (`present` False) weigh nothing. Returns (verse,
    line-in-verse, lines in verse) per line, or None if no segmentation fits."""
    if n == 0:
        return []
    present = present or [True] * n
    known = sorted(s for s, p in zip(syl, present) if p and s > 0)
    fill = known[len(known) // 2] if known else 16.0
    syl = [0.0 if not p else (s if s > 0 else fill) for s, p in zip(syl, present)]
    total = sum(syl) or 1.0
    maxv = max([v for v, _ in anchors.values()] + [0])

    def run(W):
        target = total / W if W else 2 * fill
        INF = float("inf")
        V = W or n + maxv + 3
        dp = [[INF] * (n + 1) for _ in range(V + 1)]
        back = [[(0, 0)] * (n + 1) for _ in range(V + 1)]
        first = min(anchors.items())[1] if anchors else (1, 1)
        for v0 in range(min(first[0], V + 1)):      # a chapter may start mid-hymn (DCS lacks its first verses)
            dp[v0][0] = 0.0 if v0 == 0 else 40.0
        pref, npres = [0.0], [0]
        for s, p in zip(syl, present):
            pref.append(pref[-1] + s)
            npres.append(npres[-1] + p)
        for v in range(V):
            for i in range(n):
                if dp[v][i] == INF:
                    continue
                for d in range(3):                 # d verses absent from DCS before this one
                    u = v + 1 + d
                    if u > V or (d and not (i in anchors and anchors[i] == (u, 1))):
                        continue
                    for k in range(1, 8):
                        j = i + k
                        if j > n:
                            break
                        x = j - 1                  # lines i..j-2 were checked at smaller k
                        if x in anchors and anchors[x] != (u, k):
                            break
                        kp = npres[j] - npres[i]
                        c = dp[v][i] + 60.0 * d + (
                            _DCS_K_COST[kp] + _DCS_LAMBDA * abs(math.log((pref[j] - pref[i]) / target))
                            if kp else 6.0)
                        if c < dp[u][j]:
                            dp[u][j], back[u][j] = c, (i, v)
        if W:
            ends = [(dp[W][n], W)]
        else:
            ends = [(dp[v][n], v) for v in range(max(1, maxv), V + 1)]
        cost, v = min(ends)
        if cost == INF:
            return None
        out, j = [None] * n, n
        while j > 0:
            i, pv = back[v][j]
            for x in range(i, j):
                out[x] = (v, x - i + 1, j - i)
            j, v = i, pv
        return out
    res = run(n_verses) if n_verses and maxv <= n_verses <= n else None
    return res if res is not None else run(None)


def dcs_assign_verses(sents: list[dict], n_verses: int | None = None) -> list[dict]:
    """Per sentence (as from dcs_sentence_heads, same order): verse, line
    (its DCS line within the verse), lines (lines in that verse, when fixed),
    status. `n_verses`: the hymn's stanza count, if known (inference only)."""
    ids = [s["line_id"] for s in sents]
    res = [{"verse": None, "line": None, "lines": None, "status": "unmapped"} for _ in sents]
    if not sents or None in ids:
        for r, s in zip(res, sents):
            if s["counter"]:
                r.update(verse=s["counter"], line=s["sub"], status="counter")
        return res
    lo, hi = min(ids), max(ids)
    n = hi - lo + 1
    if n > 4000 or ids != sorted(ids):        # not a single run of consecutive lines: counters only
        return dcs_assign_verses([dict(s, line_id=None) for s in sents])
    anchor: dict[int, tuple[int, int]] = {}    # line index → (verse, line in verse)
    seen: dict[int, set] = collections.defaultdict(set)
    for s in sents:
        x = s["line_id"] - lo
        if s["counter"] and x not in anchor:
            seen[s["counter"]].add(x)                  # no subcounter: rank among the verse's lines
            anchor[x] = (s["counter"], s["sub"] or len(seen[s["counter"]]))
    line_of: dict[int, tuple[int, int | None, str]] = {i: (v, l, "counter") for i, (v, l) in anchor.items()}
    keys = sorted(anchor)
    for x in sorted({i - lo for i in ids} - set(anchor)):
        p = bisect.bisect_left(keys, x)
        lw = keys[p - 1] if p > 0 else None
        up = keys[p] if p < len(keys) else None
        if up is not None and up - x < anchor[up][1]:
            line_of[x] = (anchor[up][0], anchor[up][1] - (up - x), "bracketed")
        elif lw is not None and up is not None and anchor[up][0] - anchor[lw][0] <= 1:
            line_of[x] = (anchor[lw][0], anchor[lw][1] + (x - lw), "bracketed")
        elif lw is None and up is not None and anchor[up][0] == 2:
            line_of[x] = (1, None, "bracketed")
    syl = [0.0] * n
    for s in sents:
        syl[s["line_id"] - lo] += _dcs_syl(s["text"])
    seg = None
    if len(line_of) < len({i - lo for i in ids}):
        pres = [False] * n
        for i in ids:
            pres[i - lo] = True
        seg = _dcs_segment(n, syl, {i: (v, l) for i, (v, l, st) in line_of.items() if l is not None},
                           n_verses, pres)
    # verse sizes, where every line of the verse is fixed (counter/bracketed)
    fixed = {i: (v, l) for i, (v, l, st) in line_of.items() if l is not None}
    size: dict[int, int] = {}
    for i, (v, l) in fixed.items():
        if l == 1:
            k = 1
            while fixed.get(i + k, (None,))[0] == v and fixed[i + k][1] == k + 1:
                k += 1
            nxt = fixed.get(i + k)
            if (nxt and nxt[0] == v + 1 and nxt[1] == 1) or i + k == n:
                size[v] = k
    for r, s in zip(res, sents):
        x = s["line_id"] - lo
        if x in line_of:
            v, l, st = line_of[x]
            r.update(verse=v, line=l, lines=size.get(v), status=st)
        elif seg and seg[x]:
            v, l, k = seg[x]
            r.update(verse=v, line=l, lines=k, status="inferred")
    return res


def dcs_pada(sents: list[dict], res: list[dict], i: int) -> str:
    """Pāda letters for sentence i: only for a 2-line verse whose lines are
    fixed and of similar verse-line length (13–27 syllables each), line 1 →
    'ab', line 2 → 'cd'. Otherwise ''."""
    r = res[i]
    if r["status"] not in ("counter", "bracketed") or r["lines"] != 2 or r["line"] not in (1, 2):
        return ""
    by_line: dict = collections.defaultdict(int)
    for s, q in zip(sents, res):
        if q["verse"] == r["verse"] and q["status"] in ("counter", "bracketed"):
            by_line[q["line"]] += _dcs_syl(s["text"])
    a, b = by_line.get(1, 0), by_line.get(2, 0)
    if not (13 <= a <= 27 and 13 <= b <= 27 and max(a, b) / min(a, b) <= 1.4):
        return ""
    return "ab" if r["line"] == 1 else "cd"


def whitney_stanzas(root: Path = ROOT) -> dict[tuple[int, int], int]:
    """AVŚ (book, hymn) → stanza count, from the Whitney–Lanman translation
    shipped with the DCS (lines 'b.h.s text'). {} if absent."""
    fn = root / DCS_WHITNEY
    if not fn.exists():
        return {}
    out: dict = {}
    for line in fn.read_text("utf-8").splitlines():
        m = re.match(r"(\d+)\.(\d+)\.(\d+)\s", line)
        if m:
            b, h, s = map(int, m.groups())
            out[(b, h)] = max(out.get((b, h), 0), s)
    return out


def _dcs_chapter_key(chapter: str) -> tuple[str, int, int] | None:
    m = re.match(r"(AVŚ|AVP|ṚVKh), (\d+), (\d+)$", chapter or "")
    return (m[1], int(m[2]), int(m[3])) if m else None


def dcs_chapter_citations(chapter: str, sents: list[dict], stanzas: dict | None = None) -> list[dict]:
    """Per sentence of one DCS chapter: {dcs, sent_id, verse, pada, cite,
    status, line, lines}. `verse`/`cite` are '' when unmapped."""
    key = _dcs_chapter_key(chapter)
    nv = (stanzas or {}).get(key[1:]) if key and key[0] == "AVŚ" else None
    res = dcs_assign_verses(sents, nv)
    out = []
    for i, (s, r) in enumerate(zip(sents, res)):
        verse = cite = pada = ""
        if key and r["verse"]:
            verse = f"{key[0]} {key[1]}.{key[2]}.{r['verse']}"
            pada = dcs_pada(sents, res, i)
            cite = verse + pada
        out.append({"dcs": f"{chapter}.s{i + 1}", "sent_id": s["sent_id"], "verse": verse, "pada": pada,
                    "cite": cite, "status": r["status"], "line": r["line"], "lines": r["lines"]})
    return out


_DCS_CITE_CACHE: dict = {}


def dcs_citation_index(texts=DCS_VEDIC, root: Path = ROOT) -> dict[str, dict]:
    """DCS locus ('AVŚ, 8, 6.s48') → its citation record (dcs_chapter_citations)."""
    ck = (tuple(texts), str(root))
    if ck not in _DCS_CITE_CACHE:
        stanzas, idx = whitney_stanzas(root), {}
        for t in texts:
            for fn in sorted((root / DCS_DIR / t).glob("*.conllu")):
                chapter, sents = dcs_sentence_heads(fn.read_text("utf-8"))
                for rec in dcs_chapter_citations(chapter or fn.stem, sents, stanzas):
                    idx[rec["dcs"]] = rec
        _DCS_CITE_CACHE[ck] = idx
    return _DCS_CITE_CACHE[ck]


def dcs_verse_citation(locus: str, root: Path = ROOT, inferred: bool = False) -> str | None:
    """'AVŚ, 8, 6.s48' (also 'AVŚ 8, 6.s48', a trailing ' (w1/3)' window tag)
    → 'AVŚ 8.6.23' (+ pāda letters when derivable, e.g. 'AVŚ 9.1.1cd').
    None if the locus is unknown or unmapped; an inferred verse only with
    `inferred=True`."""
    m = DCS_LOCUS.search(locus)
    if not m:
        return None
    rec = dcs_citation_index(root=root).get(f"{m[1]}, {m[2]}, {m[3]}.s{m[4]}")
    if not rec or not rec["cite"] or (rec["status"] == "inferred" and not inferred):
        return None
    return rec["cite"]


def load_dcs(texts=DCS_VEDIC, corpus: str = "av", root: Path = ROOT) -> list[Token]:
    """DCS CoNLL-U (CC BY 4.0), the Vedic texts listed. Unit: DCS sentence
    (in the Atharvaveda usually a half-verse or verse); locus: chapter +
    sentence number in the chapter ('AVŚ, 8, 6.s48' — a sentence index, NOT a
    verse). units: 'sentence' (chapter|DCS sent_id), 'sent_id', 'verse' (the
    standard citation, e.g. 'AVŚ 8.6.23', '' if unmapped), 'cite' (verse +
    pāda letters when derivable), 'verse_status' (counter | bracketed |
    inferred | unmapped; see dcs_assign_verses). The `.conllu_parsed`
    duplicates are skipped."""
    toks: list[Token] = []
    stanzas = whitney_stanzas(root)
    for t in texts:
        for fn in sorted((root / DCS_DIR / t).glob("*.conllu")):
            text = fn.read_text("utf-8")
            ch0, sents = dcs_sentence_heads(text)
            cites = dcs_chapter_citations(ch0 or fn.stem, sents, stanzas)
            chapter, sent, nsent = fn.stem, None, 0
            for line in text.splitlines():
                if line.startswith("## chapter:"):
                    chapter = line.split(":", 1)[1].strip()
                elif line.startswith("# sent_id"):
                    sent = line.split("=", 1)[1].strip()
                    nsent += 1
                elif line and not line.startswith("#"):
                    c = line.split("\t")
                    if len(c) < 10 or "-" in c[0] or "." in c[0] or c[2] in ("_", ""):
                        continue
                    feats = dict(x.split("=", 1) for x in c[5].split("|") if "=" in x)
                    upos = c[3]
                    pos = {"NOUN": "noun", "PROPN": "noun", "ADJ": "adj", "VERB": "verb"}.get(upos, "other")
                    if upos == "VERB" and feats.get("VerbForm") == "Part":
                        pos = "adj"
                    ci = cites[nsent - 1] if 0 < nsent <= len(cites) else {}
                    toks.append(Token(corpus, c[2], c[1], f"{chapter}.s{nsent}",
                                      {"sentence": f"{chapter}|{sent}", "chapter": chapter, "book": t,
                                       "sent_id": sent, "verse": ci.get("verse", ""), "cite": ci.get("cite", ""),
                                       "verse_status": ci.get("status", "unmapped")},
                                      upos in DCS_CONTENT, pos, (feats.get("Case") or "").upper()[:3] or None,
                                      None, finite=feats.get("VerbForm") is None and upos == "VERB"))
    return toks


GLAUX_DIR = "raw/daughters/glaux/src/glaux-main"
GLAUX_GENRES = ("Epic poetry", "Lyric poetry", "Tragedy")


def glaux_selection(root: Path = ROOT, max_end: int = -400, genres=GLAUX_GENRES) -> list[dict]:
    """Archaic and classical poetry in GLAUx (ENDDATE ≤ −400, epic, lyric and
    tragic genres), Homer (TLG 0012) excluded: the AGDT loader has it."""
    import csv
    out = []
    with open(root / GLAUX_DIR / "metadata.txt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            try:
                end = int(r["ENDDATE"])
            except (TypeError, ValueError):
                continue
            if end <= max_end and r["GENRE_STANDARD"] in genres and not r["TLG"].startswith("0012-"):
                out.append(r)
    return out


def load_glaux(sel: list[dict] | None = None, corpus: str = "grp", root: Path = ROOT) -> list[Token]:
    """GLAUx treebank XML (NFD → NFC). Unit: verse line within a text (the
    `line` attribute); sentence as an alternative. Same tagset as AGDT."""
    sel = sel if sel is not None else glaux_selection(root)
    toks: list[Token] = []
    for r in sel:
        fn = root / GLAUX_DIR / "xml" / f"{r['TLG']}.xml"
        if not fn.exists():
            continue
        text = unicodedata.normalize("NFC", fn.read_text("utf-8"))
        name = f"{r['AUTHOR_STANDARD']} {r['TITLE_STANDARD']}"
        for si, sent in enumerate(text.split("<sentence ")[1:]):
            local, heads = {}, []
            for m in fs._HOM_W.finditer(sent):
                a = dict(fs._ATTR.findall(m[1]))
                tag = (a.get("postag") or "-" * 9).ljust(9, "-")
                if tag[0] in "u-" or not a.get("lemma"):
                    continue
                line = a.get("line") or "?"
                pos = {"n": "noun", "a": "adj", "v": "verb"}.get(tag[0], "other")
                if tag[0] == "v" and tag[4] == "p":
                    pos = "adj"
                local[a.get("id")] = len(toks)
                heads.append((len(toks), a.get("head")))
                toks.append(Token(corpus, a["lemma"], a.get("form", ""), f"{name} {line}",
                                  {"line": f"{r['TLG']}:{line}", "sentence": f"{r['TLG']}.{si}", "book": r["TLG"]},
                                  tag[0] in fs.HOM_CONTENT, pos, fs._HOM_CASE.get(tag[7]), fs._HOM_NUM.get(tag[2]),
                                  finite=tag[0] == "v" and tag[4] in "isom", rel=a.get("relation")))
            for i, h in heads:
                toks[i].head = local.get(h)
    return toks


HIT_DIR = "raw/daughters/hittite-tlhdig/extract/TLHbasisONLINE25_1_ZENODO_Beta_03"
_HIT_W = re.compile(r"<w ([^>]*)>")
_HIT_LB = re.compile(r'<lb [^>]*?txtid="([^"]*)"[^>]*?lnr="([^"]*)"')


def hit_lemma(a: dict) -> tuple[str, str] | None:
    """TLHdig word attributes → (lemma, morphology) when the analysis is
    unique: a single selected analysis (mrp0sel), or a single proposal, or
    several proposals that all share the lemma. Sumerograms and Akkadograms
    (no lowercase letter) are dropped."""
    sel = (a.get("mrp0sel") or "").split()
    props = {k[3:]: v for k, v in a.items() if re.fullmatch(r"mrp\d+", k)}
    if not props:
        return None
    nums = sorted({re.match(r"\d+", s)[0] for s in sel if re.match(r"\d+", s)})
    if len(nums) == 1 and nums[0] in props:
        chosen = [props[nums[0]]]
    elif not nums:
        chosen = list(props.values())
    else:
        chosen = [props[n] for n in nums if n in props]
    lemmas = {c.split("@")[0].strip() for c in chosen}
    if len(lemmas) != 1:
        return None
    lem = re.sub(r"^[①-⑳]\s*", "", lemmas.pop())
    if re.search(r"[A-ZḪŠ]", lem.split("=")[0]) or not re.search(r"[a-zḫšāēīū]", lem):
        return None                     # Sumerograms / Akkadograms (also as stems: LUGAL=u-)
    parts = chosen[0].split("@")
    gloss = parts[1].strip() if len(parts) > 1 else ""
    return (f"{lem}@{gloss}" if gloss else lem), (parts[2] if len(parts) > 2 else "")


def load_hittite(root: Path = ROOT, corpus: str = "hit") -> list[Token]:
    """TLHdig AOxml (CC BY 4.0), Hittite-language lines only. Unit: tablet
    line (`lb`); paragraph (between `parsep`) as the alternative. Every
    manuscript is read, so duplicates of one composition count separately."""
    toks: list[Token] = []
    for fn in sorted((root / HIT_DIR).glob("*/*.xml")):
        cth = fn.parent.name.split("_")[0]
        text = fn.read_text("utf-8", errors="replace")
        body = text.split("<body>", 1)[-1]
        cur, para = None, 0
        for piece in re.split(r"(<lb [^>]*>|<parsep[^>]*>)", body):
            if piece.startswith("<lb "):
                m = _HIT_LB.search(piece)
                lg = re.search(r'lg="([^"]*)"', piece)
                cur = (m[1], m[2]) if m and (not lg or lg[1] == "Hit") else None
                continue
            if piece.startswith("<parsep"):
                para += 1
                continue
            if not cur:
                continue
            for wm in _HIT_W.finditer(piece):
                a = dict(re.findall(r'([\w:]+)="([^"]*)"', wm[1]))
                r = hit_lemma(a)
                if not r:
                    continue
                lem, morph = r
                verbal = bool(re.match(r"\d|PTCP|INF|SUP", morph)) or "PRS" in morph or "PST" in morph \
                    or "IMP" in morph
                pos = "verb" if verbal and "PTCP" not in morph else "noun" if re.search(r"NOM|ACC|GEN|D/L|ABL|ALL|INS|STF", morph) else "other"
                content = pos in ("verb", "noun")
                toks.append(Token(corpus, lem, "", f"{cur[0]} {cur[1]}",
                                  {"line": f"{fn.stem}|{cur[1]}", "para": f"{fn.stem}|{para}", "book": cth},
                                  content, pos))
    return toks


UD_SGA = "raw/daughters/oldirish-ud"


def load_conllu_simple(files: list[Path], corpus: str, content=("NOUN", "VERB", "ADJ", "PROPN")) -> list[Token]:
    toks = []
    for fn in files:
        sent, ref = None, None
        for line in fn.read_text("utf-8").splitlines():
            if line.startswith("# sent_id"):
                sent = line.split("=", 1)[1].strip()
            elif line.startswith("# reference"):
                ref = line.split("=", 1)[1].strip()
            elif line and not line.startswith("#"):
                c = line.split("\t")
                if len(c) < 10 or "-" in c[0] or c[2] in ("_", ""):
                    continue
                pos = {"NOUN": "noun", "PROPN": "noun", "ADJ": "adj", "VERB": "verb"}.get(c[3], "other")
                toks.append(Token(corpus, c[2], "", f"{fn.parent.name.split('-')[-1]} {ref or sent}",
                                  {"sentence": f"{fn.stem}.{sent}", "book": fn.stem}, c[3] in content, pos))
    return toks


def load_oldirish_ud(root: Path = ROOT) -> list[Token]:
    return load_conllu_simple(sorted((root / UD_SGA).glob("*/*.conllu")), "sga")


# ---------------------------------------------------------------- corpus lemma → mapping

def corpus_mapping(tokens: list[Token], lm: LangMapping, lemma_keys=None, gmap: dict | None = None,
                   max_groups: int = fs.MAX_GROUPS) -> tuple[fs.Mapping, dict]:
    """formula_search.Mapping for a corpus from a LangMapping (corpus lemma →
    lexicon ids), and lemma → MapRec for the output tables. lemma_keys:
    corpus lemma → candidate keys, most specific first (default: the
    language key, then the loose key)."""
    K = KEYS[lm.lang]
    loose: dict[str, set] = collections.defaultdict(set)
    for k in lm.recs:
        loose[K(k, True)].add(k)
    lemma_keys = lemma_keys or (lambda lem: [K(lem), K(lem, True)])
    gmap = gmap or {}
    m, recs = fs.Mapping(), {}
    for lem in {t.lemma for t in tokens}:
        for i, k in enumerate(lemma_keys(lem)):
            if not k:
                continue
            hits = [lm.recs[k]] if k in lm.recs else [lm.recs[x] for x in sorted(loose.get(k, ()))] if i else []
            if not hits:
                continue
            ids = frozenset().union(*(h.ids for h in hits))
            g = frozenset(gmap.get(x, x) for x in ids)
            if len(g) > max_groups:
                m.ambiguous.add(lem)
                break
            m.lemma_groups[lem], m.lemma_lex[lem], m.lemma_tier[lem] = g, ids, hits[0].how
            recs[lem] = hits[0] if len(hits) == 1 else MapRec(k, "|".join(h.word for h in hits), ids, hits[0].path,
                                                             hits[0].how, "low", ("loose-key",))
            break
    return m, recs


# ---------------------------------------------------------------- Hittite: Kloekhorst (EDHIL) headwords
#
# The extracted text layer drops the glyphs of a private-use font: ḫ, w and
# some long or accented vowels vanish (ḫalki- → alki-, šiu- → šu-). Headwords
# and TLHdig lemmas are therefore compared on a *damaged key* (both sides with
# h/ḫ/w deleted and vowels unmarked), and a match is used only when the key is
# unique on both sides. Only the headword and the PIE line are read; nothing
# of the running text is stored.

KLOEKHORST = "raw/books/text/kloekhorst-hitt"
_KH_HEAD = re.compile(r"^\*?([^\s‘:]+(?: / [^\s‘:]+)*)\s+((?:\([^)]*\)\s*)*)‘")
_KH_PIE = re.compile(r"^\s*PIE (\*.*)$")
_HIT_VERB_END = re.compile(r"-(?:zi|i|ari|tta|tta\(ri\)|a\(ri\)|a|ttari)$")


def _kh_variants(stem: str) -> list[str]:
    """`antezzi(a)-` → ['antezzi', 'antezzia']."""
    out = [re.sub(r"\([^)]*\)", "", stem), re.sub(r"[()]", "", stem)]
    return [x for x in dict.fromkeys(out) if x]


def hit_damaged_key(s: str) -> str:
    s = _nfd_strip((s or "").lower()).replace("ḫ", "").replace("h", "").replace("w", "")
    s = s.replace("š", "s")
    s = re.sub(r"[₀-₉0-9]", "", s)
    s = re.sub(r"[^a-z]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)          # geminates and plene writing collapse


def hit_lemma_stems(lemma: str) -> list[str]:
    """TLHdig lemma `ēd-/ad-`, `ḫatt=eššar`, `eku-/aku-` → stem strings."""
    out = []
    lemma = re.sub(r"^[①-⑳]\s*", "", lemma.split("@")[0])
    for alt in lemma.split("/"):
        alt = alt.replace("=", "").strip().strip("-")
        out += _kh_variants(alt)
    return [x for x in out if x]


def kloekhorst_entries(root: Path = ROOT) -> list[dict]:
    """Headword entries of EDHIL: {'head', 'stems', 'pie', 'page'}. An entry
    starts on a line after a blank line with `headword (class) ‘gloss’`;
    its PIE reconstruction is the first indented `PIE *…` line before the
    next entry. Cross-references (`x: see y`) and cuneiform transliterations
    (several syllable hyphens) are skipped."""
    out = []
    files = sorted((root / KLOEKHORST).glob("p*.txt"))
    for fn in files:
        lines = fn.read_text("utf-8", errors="replace").splitlines()
        prev_blank = True
        for line in lines:
            m = _KH_HEAD.match(line) if prev_blank else None
            prev_blank = not line.strip()
            if m:
                head = m[1]
                parts = [p.strip() for p in head.split(" / ")]
                if any(p.count("-") > 2 for p in parts) or not re.search(r"[a-zš]", head):
                    continue
                stems = []
                for p in parts:
                    p = _HIT_VERB_END.sub("", p) if re.search(r"-(zi|i|ari|tta|ttari)$", p) else p
                    stems += _kh_variants(p.strip("-*"))
                out.append({"head": head, "stems": stems, "pie": [], "page": fn.stem})
                continue
            pm = _KH_PIE.match(line)
            if pm and out and not out[-1]["pie"] and out[-1]["page"] <= fn.stem:
                forms = re.split(r"\s*(?:,|/|~| or )\s*", pm[1])
                out[-1]["pie"] = [f.strip(" ?.;").split(" ")[0] for f in forms if f.strip().startswith("*")]
    return [e for e in out if e["pie"]]


def pie_fuzzy_key(s: str) -> str:
    """Key on which Kloekhorst's plain-text PIE (u for w, i for y, h1 for h₁,
    flattened superscripts and diacritics) meets the lexicon forms."""
    s = unicodedata.normalize("NFD", (s or "").lower().lstrip("*"))
    s = s.replace("ʷ", "w").replace("ʰ", "h").replace("₁", "1").replace("₂", "2").replace("₃", "3")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("w", "u").replace("y", "i").replace("ḱ", "k").replace("ǵ", "g")
    s = re.sub(r"\([^)]*\)", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


class FuzzyPie:
    def __init__(self, lexicon: list[dict]):
        self.idx: dict[str, set] = collections.defaultdict(set)
        self.kind = {e["id"]: e.get("kind") for e in lexicon}
        for e in lexicon:
            if e.get("kind") == "affix":
                continue
            ids = set(e.get("target_ids") or [e["id"]]) if e.get("kind") == "alt" else {e["id"]}
            for f in [e["form"], *(e.get("variants") or [])]:
                self.idx[pie_fuzzy_key(f)].update(ids)

    def lookup(self, form: str) -> tuple[set, str]:
        """Whole form first, then its leading segments (*h1ed-ri- → *h1ed-)."""
        segs = [x for x in form.lstrip("*").split("-")]
        for n in range(len(segs), 0, -1):
            k = pie_fuzzy_key("-".join(segs[:n]))
            if len(k) >= 2 and k in self.idx:
                return set(self.idx[k]), ("form" if n == len(segs) else "root-of-form")
        return set(), ""


def kloekhorst_hittite(lemmas, lexicon: list[dict], root: Path = ROOT, gmap: dict | None = None) -> dict:
    """TLHdig lemma → MapRec via EDHIL headwords (unique damaged-key match on
    both sides; the PIE line resolved by FuzzyPie)."""
    ents = kloekhorst_entries(root)
    fz = FuzzyPie(lexicon)
    by_key: dict[str, list] = collections.defaultdict(list)
    for e in ents:
        for st in e["stems"]:
            k = hit_damaged_key(st)
            if len(k) >= 3:
                by_key[k].append(e)
    lem_by_key: dict[str, set] = collections.defaultdict(set)
    for lem in lemmas:
        for st in hit_lemma_stems(lem):
            lem_by_key[hit_damaged_key(st)].add(lem)
    out = {}
    for lem in lemmas:
        for st in hit_lemma_stems(lem):
            k = hit_damaged_key(st)
            es = {id(x): x for x in by_key.get(k, [])}
            if len(k) < 3 or len(es) != 1 or len(lem_by_key[k]) != 1:
                continue
            e = next(iter(es.values()))
            ids, how = set(), ""
            for f in e["pie"]:
                ids, how = fz.lookup(f)
                if ids:
                    break
            if not ids or how != "form":
                continue          # the leading-segment fallback was wrong in 2 of 3 checked cases
            g = {(gmap or {}).get(i, i) for i in ids}
            if len(g) > fs.MAX_GROUPS:
                continue
            out[lem] = MapRec(k, e["head"], frozenset(ids), (f"hit:{lem}", f"kloekhorst:{e['page']}:{e['head']}",
                                                             f"ine-pro:{e['pie'][0]}"),
                              "kloekhorst" if how == "form" else "kloekhorst-root", "medium", ("kloekhorst",))
            break
    return out


# German glosses of TLHdig → English words that must occur in the matched
# dictionary gloss (kaikki sense or lexicon meaning). Hand-written for the
# frequent glosses; a Hittite match whose TLHdig gloss is not covered is kept
# only if it is not verbal and its key is unambiguous.
HIT_DE_EN = {
    "gehen": "go walk", "setzen": "put place set sit", "geben": "give", "trinken": "drink", "nehmen": "take",
    "zerbrechen": "break", "libieren": "libate pour offer", "fassen": "seize grab take", "kommen": "come",
    "sprechen": "speak say", "haben": "have hold", "machen": "make do", "treten": "step tread",
    "jeder": "every all whole", "ganz": "whole all", "ich": "i me", "du": "you thou", "bringen": "bring",
    "rufen": "call cry shout", "herd": "hearth", "wasser": "water", "stehen": "stand", "essen": "eat",
    "liegen": "lie", "werfen": "throw cast", "sitzen": "sit", "erde": "earth", "ordnen": "arrange order",
    "platz": "place", "anderer": "other another", "füllen": "fill", "altar": "altar", "wenig": "little few",
    "wenden": "turn", "werden": "become", "schale": "bowl", "gut": "good", "lassen": "let release leave",
    "gießen": "pour", "böse": "evil bad", "schlachten": "slaughter", "ankommen": "arrive reach",
    "sehen": "see look", "sterben": "die", "frevel": "sin offense", "verbrennen": "burn", "mensch": "man human person",
    "waschen": "wash", "laufen": "run", "mitteilen": "inform tell", "viel": "much many", "suchen": "seek search",
    "reinigen": "clean purify", "wirken": "work", "drehen": "turn", "wissen": "know", "mächtig": "powerful mighty",
    "schneiden": "cut", "teilen": "divide share", "fleisch": "flesh meat", "sein": "be", "finden": "find",
    "zerstören": "destroy", "zeit": "time", "vorderster": "first front foremost", "heben": "lift raise",
    "treiben": "drive", "schlagen": "strike beat smite kill", "getreide": "grain", "verneigen": "bow",
    "schütten": "pour", "fragen": "ask", "rein": "pure clean", "lösen": "loosen release untie", "blut": "blood",
    "kochen": "cook boil", "wünschen": "wish want", "himmel": "sky heaven", "feuer": "fire", "festmachen": "fasten",
    "stehlen": "steal", "groß": "great big large", "hand": "hand", "jener": "that", "erheben": "raise lift",
    "schicken": "send", "schlafen": "sleep", "schauen": "look", "baden": "bathe wash", "mauer": "wall",
    "früherer": "former earlier", "stechen": "stab pierce", "freund": "friend", "öffnen": "open", "binden": "bind tie",
    "wort": "word", "feindschaft": "enmity hostility", "hof": "court yard", "beten": "pray", "tanzen": "dance",
    "bitten": "ask request pray", "knie": "knee", "vertrag": "treaty", "ernte": "harvest", "lebendig": "alive living",
    "gott": "god", "feld": "field", "großvater": "grandfather", "weg": "road way path", "beißen": "bite",
    "abschneiden": "cut", "bedecken": "cover", "springen": "jump spring leap", "befehlen": "command order",
    "angenehm": "pleasant", "mischen": "mix", "anstimmen": "sing chant", "beschützen": "protect", "abwischen": "wipe",
    "welcher": "who which what", "irgendein": "any some", "er": "he that", "dieser": "this",
    "vater": "father", "mutter": "mother", "sohn": "son", "tochter": "daughter", "bruder": "brother",
    "schwester": "sister", "frau": "woman wife", "mann": "man", "pferd": "horse", "rind": "cattle ox cow",
    "schaf": "sheep", "hund": "dog", "kuh": "cow", "berg": "mountain", "fluss": "river", "baum": "tree",
    "holz": "wood", "stein": "stone", "nacht": "night", "tag": "day", "jahr": "year", "name": "name",
    "herz": "heart", "auge": "eye", "ohr": "ear", "fuß": "foot", "kopf": "head", "mund": "mouth",
    "zunge": "tongue", "zahn": "tooth", "knochen": "bone", "milch": "milk", "honig": "honey", "wein": "wine",
    "brot": "bread", "salz": "salt", "öl": "oil", "fett": "fat", "wolle": "wool", "neu": "new", "alt": "old",
    "jung": "young", "lang": "long", "breit": "wide broad", "schwer": "heavy", "weiß": "white", "schwarz": "black",
    "rot": "red", "warm": "warm hot", "kalt": "cold", "töten": "kill", "leben": "live life", "hören": "hear",
    "erkennen": "know recognize", "fürchten": "fear", "lieben": "love", "bauen": "build", "pflügen": "plough plow",
    "mahlen": "grind", "weben": "weave", "nähen": "sew", "tragen": "carry bear", "ziehen": "pull draw",
    "kämpfen": "fight", "siegen": "conquer win", "fliehen": "flee", "fallen": "fall", "wachsen": "grow",
    "zählen": "count", "schreiben": "write", "lesen": "read", "eins": "one", "zwei": "two", "drei": "three",
    "vier": "four", "unten": "below down", "oben": "above up", "hinein": "into in", "darin": "in inside",
    "vor": "before front", "hinter": "behind after", "wieder": "again back", "nicht": "not",
}


def hittite_gloss_ok(tlh_lemma: str, rec: MapRec) -> bool:
    gl = tlh_lemma.split("@", 1)[1].lower() if "@" in tlh_lemma else ""
    words = re.findall(r"[a-zäöüß]+", gl)
    en = set()
    for w in words:
        en |= set(HIT_DE_EN.get(w, "").split())
    target = set(re.findall(r"[a-z]+", (rec.gloss or "").lower()))
    if en:
        return bool(en & target)
    return False


# ---------------------------------------------------------------- unlemmatized corpora (OCR / plain text)

_WORDS = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.U)

# ---------------------------------------------------------------- mapping errata (overrides)

OVERRIDES = "data/research/formulas/mapping-overrides.json"
_OVR_CACHE: dict = {}


def load_overrides(root: Path = ROOT) -> dict:
    """{"lemma": {corpus: {lemma: (ids frozenset, row)}}, "form": {lang: {form key: lemma}}} from
    data/research/formulas/mapping-overrides.json (corrections reported in mapping-errata.md)."""
    p = Path(root) / OVERRIDES
    if p not in _OVR_CACHE:
        d = json.loads(p.read_text("utf-8")) if p.exists() else {}
        # per-language override files (one agent per language edits its own file):
        # data/research/formulas/mapping-overrides/<name>.json with the same {"lemma": [...], "form": [...]}
        d = {"lemma": list(d.get("lemma", [])), "form": list(d.get("form", []))}
        for f in sorted((Path(root) / OVERRIDES.replace(".json", "")).glob("*.json")):
            x = json.loads(f.read_text("utf-8"))
            d["lemma"] += x.get("lemma", [])
            d["form"] += x.get("form", [])
        lem: dict = collections.defaultdict(dict)
        for r in d.get("lemma", []):
            lem[r["corpus"]][r["lemma"]] = (frozenset(r["lex_id"]), r)
        form: dict = collections.defaultdict(dict)
        for r in d.get("form", []):
            form[r["lang"]][KEYS[r["lang"]](r["form"])] = r["lemma"]
        _OVR_CACHE[p] = {"lemma": dict(lem), "form": dict(form)}
    return _OVR_CACHE[p]


def apply_lemma_overrides(corpus: str, m: "fs.Mapping", gmap: dict | None = None, root: Path = ROOT,
                          overrides: dict | None = None) -> "fs.Mapping":
    """A copy of a lemma → ids Mapping with the corpus's errata applied (ids replaced, or the lemma
    unmapped when the override lists none). Tier of a corrected lemma: 'erratum'."""
    gmap = gmap or {}
    ov = (overrides or load_overrides(root))["lemma"].get(corpus, {})
    out = fs.Mapping(dict(m.lemma_groups), dict(m.lemma_tier), set(m.ambiguous), dict(m.lemma_lex))
    for lem in [k for k, v in out.lemma_lex.items() if set(v) & BLOCKED_IDS]:
        keep = frozenset(_strip_blocked(out.lemma_lex[lem]))
        if keep:
            out.lemma_lex[lem] = keep
            out.lemma_groups[lem] = frozenset(gmap.get(x, x) for x in keep)
        else:
            for d in (out.lemma_groups, out.lemma_tier, out.lemma_lex):
                d.pop(lem, None)
    for lem, (ids, _) in ov.items():
        out.ambiguous.discard(lem)
        if not ids:
            for d in (out.lemma_groups, out.lemma_tier, out.lemma_lex):
                d.pop(lem, None)
            continue
        out.lemma_lex[lem] = ids
        out.lemma_groups[lem] = frozenset(gmap.get(x, x) for x in ids)
        out.lemma_tier[lem] = "erratum"
    return out


def apply_rec_overrides(corpus: str, recs: dict, root: Path = ROOT, overrides: dict | None = None) -> dict:
    """The same for a lemma → MapRec table (what write_mapping_tables writes)."""
    ov = (overrides or load_overrides(root))["lemma"].get(corpus, {})
    out = dict(recs)
    for lem, (ids, row) in ov.items():
        if not ids:
            out.pop(lem, None)
            continue
        old = out.get(lem)
        note = row.get("erratum") or row.get("note") or "override"      # per-language rows cite a dictionary in 'note'
        out[lem] = MapRec(lem, old.word if old else lem, ids, (f"{corpus}:{lem}", "erratum:" + note),
                          "erratum", "high", ("mapping-overrides",))
    return out


# ids that the etymology resolver attaches wrongly by key collision and that no automatic mapping may
# use (an explicit override row still can): pie-lex-sh1es (a derivative of *seh₁- 'sow, impress')
# collects 'be' words (OE wesan, sindon; Goth. wisan; Latv. būt) and *h₁sónt- words (Goth. sunja,
# OE synn): mapping-errata.md, Germanic precision report
BLOCKED_IDS = {"pie-lex-sh1es"}


def _strip_blocked(ids):
    return tuple(i for i in ids if i not in BLOCKED_IDS)


def apply_table_overrides(corpus: str, table: dict, root: Path = ROOT, overrides: dict | None = None) -> dict:
    """The same for a lemma → ids tuple dict (a mapping table as read by the 8c loaders)."""
    ov = (overrides or load_overrides(root))["lemma"].get(corpus, {})
    out = {k: _strip_blocked(v) for k, v in table.items()}
    out = {k: v for k, v in out.items() if v}
    for lem, (ids, _) in ov.items():
        if ids:
            out[lem] = tuple(sorted(ids))
        else:
            out.pop(lem, None)
    return out


class FormLemmatizer:
    """Surface form → lemma keys through a LangMapping's kaikki forms table
    (inflection tables and form-of pages). Exact key first, then the loose
    key; a form with several lemmas keeps up to `max_lemmas` of them.
    Surface forms listed in the mapping overrides ('form' rows) go to their
    corrected lemma first."""

    def __init__(self, lm: LangMapping, normalize=None, max_lemmas: int = 3, fallbacks=(), form_overrides=None):
        self.lm, self.K, self.norm, self.max = lm, KEYS[lm.lang], normalize or (lambda s: s), max_lemmas
        self.fallbacks = fallbacks
        self.form_overrides = (form_overrides if form_overrides is not None
                               else load_overrides()["form"].get(lm.lang, {}))

    def __call__(self, surface: str) -> str:
        s = self.norm(surface)
        if self.form_overrides:
            o = self.form_overrides.get(self.K(s))
            if o:
                return o
        r = self._one(s)
        if r.startswith("?"):
            for f in self.fallbacks:
                for alt in f(s):
                    r2 = self._one(alt)
                    if not r2.startswith("?"):
                        return r2
        return r

    def _one(self, s: str) -> str:
        for k in (self.K(s), self.K(s, True)):
            c = self.lm.forms.get(k)
            if c and k in c:
                return k                         # the form is itself a headword
            if c:
                lem = sorted(c, key=lambda x: (-c[x], x))[: self.max]
                return "|".join(lem)
            if k in self.lm.recs or k in self.lm.lemma_words:
                return k
        return "?" + self.K(s, True)


def multi_lemma_mapping(tokens: list[Token], lm: LangMapping, gmap: dict | None = None,
                        max_groups: int = fs.MAX_GROUPS) -> tuple[fs.Mapping, dict]:
    """corpus_mapping for lemma strings 'a|b' (lemmatizer output): the union
    of the parts' mappings; '?…' (unknown form) stays unmapped."""
    gmap = gmap or {}
    m, recs = fs.Mapping(), {}
    for lem in {t.lemma for t in tokens}:
        if lem.startswith("?"):
            continue
        hits = [lm.recs[p] for p in lem.split("|") if p in lm.recs]
        if not hits:
            continue
        if len({frozenset(gmap.get(x, x) for x in h.ids) for h in hits}) > 1:
            m.ambiguous.add(lem)               # candidate lemmas with different etyma
            continue
        ids = frozenset().union(*(h.ids for h in hits))
        g = frozenset(gmap.get(x, x) for x in ids)
        if len(g) > max_groups:
            m.ambiguous.add(lem)
            continue
        m.lemma_groups[lem], m.lemma_lex[lem], m.lemma_tier[lem] = g, ids, hits[0].how
        many = "|" in lem
        recs[lem] = hits[0] if not many else MapRec(lem, "|".join(h.word for h in hits), ids, hits[0].path,
                                                    hits[0].how, "low", hits[0].sources + ("form-ambiguous",))
    return m, recs


def text_tokens(corpus: str, units, lemmatize, is_content) -> list[Token]:
    """(locus, units, line text or word list) → Tokens. These corpora have
    no POS: content = the dictionary POS of the lemma (is_content)."""
    toks = []
    for locus, u, text in units:
        for w in (_WORDS.findall(text) if isinstance(text, str) else text):
            lem = lemmatize(w)
            toks.append(Token(corpus, lem, "", locus, u, is_content(lem), "other"))
    return toks


EDDA = "raw/daughters/edda-fj1926/smundareddaeddu00jngoog_djvu.txt"


def edda_lines(root: Path = ROOT) -> list[tuple[str, dict, str]]:
    """Finnur Jónsson 1926 (PD), OCR. Verse lines between the first poem
    header and the name index; the poem is the running header (capitals),
    the stanza the 'N.' prefix. Lines with digits only, headers and lines
    with OCR debris (no letters, ≥ 30% non-letters) are dropped."""
    lines = (root / EDDA).read_text("utf-8", errors="replace").splitlines()
    out, poem, stanza, started = [], None, "0", False
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        hdr = re.match(r"^([A-ZÁÉÍÓÚÝÞÆÖ][A-ZÁÉÍÓÚÝÞÆÖÐ\- ]{3,})\.\s*\S{0,8}\s*$", s)
        if hdr:
            name = hdr[1].strip()
            if name.startswith(("NOFN", "NÖFN")):
                if started:
                    break
                continue
            if name in ("VOLUSPA", "VÖLUSPÁ"):
                started = True
            if started:
                poem = name.title()
            continue
        if not started or re.fullmatch(r"[\d\W]+", s):
            continue
        m = re.match(r"^(?:[A-ZÁÉÍÓÚÞ][a-zþð]*\.\s*kv[.,]\s*)?(\d+)\.\s+(.*)$", s)
        if m:
            stanza, s = m[1], m[2]
        letters = sum(c.isalpha() for c in s)
        if letters < 3 or letters / max(1, len(s.replace(" ", ""))) < 0.7:
            continue
        out.append((f"{poem} {stanza}", {"line": f"edda:{i}", "stanza": f"{poem}.{stanza}", "book": poem or ""}, s))
    return out


BEOWULF = "raw/daughters/oe-beowulf-gutenberg/pg9701.txt"


def beowulf_lines(root: Path = ROOT) -> list[tuple[str, dict, str]]:
    """Harrison & Sharp's Beowulf and the Finnsburh fragment (PD, Project
    Gutenberg): long lines (both half-lines), numbered from the edition's
    every-fifth-line numbers; fitt headings are skipped."""
    lines = (root / BEOWULF).read_text("utf-8", errors="replace").splitlines()
    out, n, started, poem = [], 0, False, "Beo."
    for raw in lines:
        if raw.strip().startswith("LIST OF NAMES"):
            break
        if not started:
            if "Hwæt! wē Gār-Dena" in raw:
                started = True
            else:
                continue
        s = raw.strip()
        if "FINNSBURG" in s and s.isupper():
            poem, n = "Finn.", 0
            continue
        if not s or re.match(r"^[IVXL]+\. ", s) or s.isupper():
            continue
        m = re.match(r"^(\d+)\s+", s)
        n = int(m[1]) if m else n + 1          # the edition prints every fifth line number
        s = s[m.end():] if m else s
        out.append((f"{poem} {n}", {"line": f"{poem}{n}", "book": poem}, s))
    return out


AVESTA = "raw/daughters/avesta-cab/CABLinguisticCorpus.xml"


def avesta_units(root: Path = ROOT) -> list[tuple[str, dict, list[str]]]:
    """CAB Linguistic Corpus (NC; 'without repetitions'): `ab` segments
    except the Pahlavi ones (xml:lang="pal") and headings; words end with
    '.', compound members and preverbs joined by '.' inside a word are split.
    Unit: the `ab` segment (a stanza part, usually a verse or sentence)."""
    text = (root / AVESTA).read_text("utf-8")
    out = []
    for m in re.finditer(r'<ab ([^>]*)>(.*?)</ab>', text, re.S):
        attrs = dict(re.findall(r'([\w:]+)="([^"]*)"', m[1]))
        if attrs.get("xml:lang", "av") != "av" or not attrs.get("xml:id") or attrs["xml:id"].startswith("Head"):
            continue
        body = re.sub(r"<note.*?</note>", "", m[2], flags=re.S)
        body = re.sub(r"<[^>]+>", "", body)
        body = body.replace("+", "")
        words = [w for w in re.split(r"[\s.]+", body) if re.search(r"[^\W\d_]", w)]
        aid = attrs["xml:id"]
        txt = (re.match(r"[A-Za-z]+", aid) or [aid])[0]
        out.append((aid, {"ab": aid, "book": txt}, words))
    return out


def non_clitic_variants(s: str) -> list[str]:
    """Old Norse enclitics in FJ's normalized text: hefk, munk, vilk (-k,
    -ek 'I'), þanns, svat (-s, -t), mák (ák → á)."""
    out = []
    low = s.lower()
    for suf in ("ek", "k", "s", "t", "sk", "a"):
        if low.endswith(suf) and len(low) - len(suf) >= 2:
            out.append(low[: -len(suf)])
    return out


# ---- Avestan: stem matching (no inflection tables exist)

AE_ENDINGS = sorted({"", "ō", "ə", "əm", "a", "ā", "ąm", "ą", "å", "ā̊", "ąn", "e", "ē", "ahe", "ahiiā", "āi", "ai",
                     "āt", "at", "aēibiiō", "aēibiš", "aēšu", "ånhō", "āiš", "i", "iš", "im", "ōiš", "u", "uš", "um",
                     "aoš", "ąś", "aiti", "ənti", "ata", "aiiā", "āiiā", "hiiā", "biiō", "biš", "ibiiō", "ābiiō",
                     "ābiš", "āhu", "ahu", "ōi", "əuuō", "aiiō", "š", "s", "ōm", "ąmca", "ca", "əmca", "aca",
                     "ō.ca", "ti", "nti", "aiti", "eiti", "ōit", "ā̊ŋhō", "ånhe", "ō", "ąstu", "atu", "aṇtu",
                     "ąm", "ō", "ē", "ąn", "aēca", "asca", "aēšąm", "anąm", "ānąm", "aēibīš", "ača"},
                    key=len, reverse=True)


class AvestanLemmatizer:
    """CAB surface → dictionary word: the longest dictionary stem (≥ 4
    letters, loose key) that the form starts with, followed by a known
    ending; a stem shared by several words keeps them all (≤ 3)."""

    def __init__(self, lm: LangMapping, entries_words: dict[str, str]):
        self.lm = lm
        ends = {key_ae(e, True) for e in AE_ENDINGS}
        self.ends = sorted(ends, key=len, reverse=True)
        self.stems: dict[str, set] = collections.defaultdict(set)
        for k in list(lm.recs) + list(lm.lemma_words):
            lk = key_ae(k, True)
            if len(lk) < 4:
                continue
            self.stems[lk].add(k)
            for e in self.ends:
                if e and lk.endswith(e) and len(lk) - len(e) >= 4:
                    self.stems[lk[: -len(e)]].add(k)

    def __call__(self, surface: str) -> str:
        t = key_ae(surface, True)
        if len(t) < 4:
            return "?" + t                   # short forms are mostly particles and pronouns
        for i in range(len(t), 3, -1):
            st, rest = t[:i], t[i:]
            if st in self.stems and (rest in self.ends or not rest):
                c = sorted(self.stems[st])[:3]
                return "|".join(c)
        return "?" + t


# ---- Old English poetry: Grein's Bibliothek (PD, OCR)

GREIN_DIR = "raw/daughters/oe-poetry-grein/download"
GREIN_VOLS = {"I": "bibliothekderan07greigoog_djvu.txt", "II": "bibliothekderan06greigoog_djvu.txt"}
_GREIN_THORN = ("|)", "J)", "{)", ")>", "I)", "!>", "|>", "}>", "l>")


def grein_normalize(s: str) -> str:
    """OCR repairs for Grein's typeface: þ read as |) J) {) …, ä for æ,
    v for w (Grein prints v), acute = length (handled by key_ang)."""
    for a in _GREIN_THORN:
        s = s.replace(a, "þ")
    return s.replace("ä", "æ").replace("Ä", "Æ").replace("v", "w").replace("V", "W")


def grein_lines(lemmatize, root: Path = ROOT, min_share: float = 0.6) -> list[tuple[str, dict, str]]:
    """Text volumes I (copy 07greigoog) and II (06greigoog). A line is kept
    as verse if it has ≥ 3 words and ≥ min_share of them lemmatize as Old
    English (this drops the German apparatus, page furniture and the worst
    OCR); Grein's Beowulf is skipped (the Gutenberg text has it). Locus:
    volume, OCR line, and the last poem header seen."""
    out = []
    for vol, fn in GREIN_VOLS.items():
        lines = (root / GREIN_DIR / fn).read_text("utf-8", errors="replace").splitlines()
        beo = [i for i, l in enumerate(lines) if re.search(r"\bBEO[VW]ULF\b", l)]
        beo_span = (beo[0] - 5, beo[-1] + 120) if beo else (-1, -1)
        poem = "?"
        for i, raw in enumerate(lines):
            if beo_span[0] <= i <= beo_span[1]:
                continue
            h = re.match(r"^\s*\d*\s*([A-ZÆ][A-ZÆ ,.]{3,}?)\.?\s*\d*\s*$", raw)
            if h and not re.fullmatch(r"[IVXLCYU]+\.?", h[1].strip()):
                poem = h[1].strip().title()
                continue
            s = grein_normalize(re.sub(r"^\s*\d+\.\s*", "", raw))
            ws = _WORDS.findall(s)
            if len(ws) < 3:
                continue
            lem = [lemmatize(w) for w in ws]
            if sum(not x.startswith("?") for x in lem) / len(ws) < min_share:
                continue
            out.append((f"Grein {vol} {poem} l.{i}", {"line": f"grein{vol}:{i}", "book": f"{vol}:{poem}"}, s))
    return out


# ---- Umbrian: the Iguvine Tables in Buck 1904 (PD, OCR)

BUCK = "raw/daughters/oscan-umbrian-buck1904/download/grammarofoscanum00buckuoft_djvu.txt"


def umbrian_lines(lat_forms: set, root: Path = ROOT, span=(14300, 18440)) -> list[tuple[str, dict, str]]:
    """The Iguvine Tables in Buck's text section (OCR lines 14300–18440):
    each OCR line holds the Umbrian column, then Buck's Latin translation.
    The split point is the one that leaves the most non-Latin words on the
    left and the most Latin words (LASLA surface forms) on the right; a word
    broken by a hyphen at the column end is joined to the first word of the
    next Umbrian line. Locus: table heading (IA, Via, …) and line number."""
    lines = (root / BUCK).read_text("utf-8", errors="replace").splitlines()
    out, table, ln, carry = [], "?", "0", ""
    for i in range(span[0], min(span[1], len(lines))):
        raw = lines[i].strip()
        t = re.fullmatch(r"([IV]+[AaBb]?|V[Ii]a|V[Ii]b)\.?", raw)
        if t:
            table, ln, carry = t[1].upper().replace("A", "a").replace("B", "b"), "0", ""
            continue
        if "Iguvinian" in raw or "Commentary" in raw:
            continue
        m = re.match(r"^(\d{1,2})\s+(.*)$", raw)
        if m:
            ln, raw = m[1], m[2]
        ws = re.findall(r"[^\W\d_]+-?", raw.replace("|", " ").replace("\\", " "))
        if len(ws) < 2:
            continue
        isl = [lat_key(w.rstrip("-")) in lat_forms for w in ws]
        best = max(range(len(ws) + 1), key=lambda k: (sum(not x for x in isl[:k]) + sum(isl[k:]), -k))
        left = ws[:best]
        if not left:
            continue
        if carry:
            left[0] = carry + left[0]
            carry = ""
        if left[-1].endswith("-"):
            carry = left.pop().rstrip("-")
        if left:
            out.append((f"Ig. {table} {ln}", {"line": f"ig:{i}", "book": f"Ig.{table}"}, " ".join(left)))
    return out


def lat_key(s: str) -> str:
    return fs.lat_key(s)


# ---- Latvian folk songs: quotations in an Endzelīns-era book on the dainas (OCR)

DAINAS = "raw/books/text/dainas-endzelins"


def dainas_units(root: Path = ROOT, min_chars: int = 20) -> list[tuple[str, dict, str]]:
    """The book is prose about the dainas; the songs are its «…»
    quotations, usually followed by a Barons–Visendorfs number ('B. V. 5210').
    Unit: one quotation (≥ min_chars). Hyphenated line breaks are joined.
    Locus: the B. V. number when given, else the page."""
    out = []
    for fn in sorted((root / DAINAS).glob("p*.txt")):
        text = fn.read_text("utf-8", errors="replace")
        text = re.sub(r"-\s*\n\s*", "", text).replace("\n", " ")
        for m in re.finditer(r"[«<]([^«»]{%d,400})»([^«]{0,30})" % min_chars, text):
            bv = re.search(r"B\.\s*V\.\s*(\d+)", m[2])
            loc = f"BV {bv[1]}" if bv else f"{fn.stem}"
            out.append((loc, {"song": f"{fn.stem}:{m.start()}", "book": fn.stem}, m[1]))
    return out


_LV_DIM = re.compile(r"^(.{2,}?)(?:ēntiņ|ēnīt|uliņ|ītiņ|iņ|īt|ēn|tiņ|uļ)(?:š|a|am|ai|ā|u|i|as|us|os|iem|ēm|ām|ām|s|is|e|ei|ē|ūs)?$")


def lv_diminutive_variants(s: str) -> list[str]:
    """Latvian diminutives (kalniņā, ziediņiem, māmulīte) → base headword
    candidates (kalns, zieds, māmula …)."""
    m = _LV_DIM.match(s.lower())
    if not m:
        return []
    b = m[1]
    return [b + e for e in ("s", "is", "a", "e", "š", "us", "")]



# ---------------------------------------------------------------- N-branch scoring

@dataclass
class CorpusSpec:
    name: str
    branch: str
    lang: str
    licence: str
    unit: str
    translation: bool = False      # translated from Greek (Bible, homilies): one witness together
    description: str = ""


BRANCHES = ("Indo-Iranian", "Greek", "Italic", "Germanic", "Celtic", "Balto-Slavic", "Armenian", "Anatolian")
CORE = frozenset({"Indo-Iranian", "Greek"})


@dataclass
class Witness:
    branch: str
    n: int                     # co-occurring units (after calque removal) summed over the branch's corpora
    logp: float
    corpora: dict              # corpus → co-occurrence count
    translation_only: bool = False


def branch_logp(cs: list, p: tuple, removed: dict | None = None) -> tuple[float, int, dict]:
    """A branch's one-sided log p for pair p over its testable corpora (both
    lexemes occur): exact hypergeometric when one corpus is testable, else
    Poisson on the summed co-occurrences with λ = Σ K·d/N (a stratified
    test: each corpus keeps its own base rates). `removed`: corpus →
    co-occurrences discarded as calques."""
    x, y = p
    o_tot, lam, test, per = 0, 0.0, [], {}
    for name, c in cs:
        K, d = c.single.get(x, 0), c.single.get(y, 0)
        if not K or not d:
            continue
        o = c.pair.get(p, 0) - (removed or {}).get(name, 0)
        o = max(o, 0)
        test.append((c, o, K, d))
        o_tot += o
        lam += K * d / c.n
        if o:
            per[name] = o
    if not test:
        return 0.0, 0, per
    if len(test) == 1:
        c, o, K, d = test[0]
        return fs.hypergeom_logsf(o, K, d, c.n), o, per
    return fs.poisson_logsf(o_tot, lam), o_tot, per


def score_branches(counts: dict, specs: dict, calques: dict | None = None, min_branches: int = 2,
                   alpha: float = 0.05, pairs=None, require_sig: bool = True, same_form=None) -> list[dict]:
    """counts: corpus → formula_search.Counts; specs: corpus → CorpusSpec.
    A pair is a candidate if it co-occurs in ≥ min_branches witnesses and
    p < alpha in at least one. Witnesses: branches; the branches whose
    co-occurrences all come from translation corpora (Gothic, OCS, Armenian)
    merge into one witness 'translation' (min p × their number). Score:
    Fisher's method over the witnesses' p (branches without a co-occurrence
    do not enter). calques: corpus → pair → co-occurrences to discard.
    same_form: optional predicate on pairs; True drops the pair (two
    homograph entries of one written form, e.g. *bʰendʰ- 'bind' twice: the
    'pair' is one word mapped to both)."""
    by_branch: dict[str, list] = collections.defaultdict(list)
    for name, c in counts.items():
        by_branch[specs[name].branch].append((name, c))
    if pairs is None:
        seen: dict = collections.Counter()
        for b, cs in by_branch.items():
            keys = set()
            for _, c in cs:
                keys |= c.pair.keys()
            seen.update(keys)
        pairs = [p for p, k in seen.items() if k >= min_branches]
    la = math.log(alpha)
    out = []
    for p in pairs:
        if same_form and same_form(p):
            continue
        ws = []
        for b, cs in by_branch.items():
            rem = {name: calques[name].get(p, 0) for name, _ in cs if calques and name in calques}
            lp, o, per = branch_logp(cs, p, rem)
            if o >= 1:
                tr = all(specs[nm].translation for nm in per)
                ws.append(Witness(b, o, lp, per, tr))
        trs = [w for w in ws if w.translation_only]
        wit = [w for w in ws if not w.translation_only]
        if trs:
            best = min(trs, key=lambda w: w.logp)
            wit.append(Witness("translation:" + "+".join(sorted(w.branch for w in trs)), sum(w.n for w in trs),
                               min(0.0, best.logp + math.log(len(trs))), {k: v for w in trs for k, v in w.corpora.items()},
                               True))
        if len(wit) < min_branches:
            continue
        if require_sig and min(w.logp for w in wit) >= la:
            continue
        comb = fs.fisher_logp([w.logp for w in wit])
        out.append({"pair": p, "witnesses": wit, "combined_logp": comb, "score": -comb / fs.LOG10,
                    "branches": frozenset(w.branch.split(":")[0] if not w.branch.startswith("translation")
                                          else w.branch for w in wit),
                    "real_branches": frozenset(b for w in ws for b in [w.branch]),
                    "n_witnesses": len(wit)})
    out.sort(key=lambda r: (-r["score"], r["pair"]))
    return out


def ranking_class(rec: dict) -> str:
    """a: ≥ 3 witnesses; b: 2 witnesses, not Greek + Indo-Iranian; c: exactly Greek + Indo-Iranian."""
    if rec["n_witnesses"] >= 3:
        return "a"
    return "c" if rec["branches"] == CORE else "b"


def calque_counts(units_by_corpus: dict, greek_verse_pairs: dict) -> dict:
    """corpus → pair → number of its co-occurrence units whose NT verse has
    the same pair in the Greek NT (PROIEL greek-nt). units_by_corpus:
    corpus → list of (verse, rootsets)."""
    out = {}
    for name, units in units_by_corpus.items():
        c: dict = collections.Counter()
        for verse, rs in units:
            gp = greek_verse_pairs.get(verse)
            if not gp:
                continue
            for p in fs._pairs_of(rs):
                if p in gp:
                    c[p] += 1
        out[name] = c
    return out


def verse_pairs(tokens: list[Token]) -> dict:
    """NT verse → set of lexeme pairs co-occurring in it (Greek NT)."""
    by: dict = collections.defaultdict(list)
    for t in tokens:
        by[t.units["verse"]].append(t.roots)
    return {v: fs._pairs_of(rs) for v, rs in by.items()}


def units_with_verse(tokens: list[Token], unit: str) -> list[tuple[str, list]]:
    by: dict = {}
    for t in tokens:
        u = t.units[unit]
        if u not in by:
            by[u] = (t.units.get("verse", ""), [])
        by[u][1].append(t.roots)
    return list(by.values())


def homograph_pair_test(lexicon: list[dict]):
    """Predicate: the two ids are entries with the same accent-free form."""
    form = {e["id"]: pie_key(e["form"]).strip("-") for e in lexicon}

    def same(p):
        a, b = form.get(p[0]), form.get(p[1])
        return a is not None and a == b
    return same
