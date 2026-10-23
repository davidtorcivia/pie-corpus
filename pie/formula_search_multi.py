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
        "clq", "calque", "pcal", "sl", "psm", "translit")
_AFFIX = ("af", "affix", "suffix", "prefix", "confix", "suf", "pre")


def _strip_inline(s: str) -> str:
    """`*ḱom-o-<id:x>` → `*ḱom-o-`; stray brackets of nested etymon syntax off."""
    s = re.sub(r"<[^>]*>", "", s or "")
    return re.sub(r"[<>\[\]'\n]", "", s.split("<")[0]).strip()


def _etymon_parts(a: dict) -> tuple[str | None, str | None, str | None]:
    """{{etymon|non|:inh|gmq-pro:*ᚹᚢᛚᚠᚨᛉ}} → ('inh', 'gmq-pro', '*ᚹᚢᛚᚠᚨᛉ')."""
    kind = (a.get("2") or "").lstrip(":").split("<")[0] or None
    tgt = _strip_inline(a.get("3") or "")
    if ":" in tgt and not tgt.startswith("*"):
        code, term = tgt.split(":", 1)
        return kind, code, term
    return kind, None, None


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
    rejected: str | None = None                    # reason (borrowing, foreign source)
    form_of: list = field(default_factory=list)    # lemma words this entry is an inflected form of
    forms: list = field(default_factory=list)      # inflected forms (for lemmatizers; memory only)


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
        if name == "etymon":
            kind, code, term = _etymon_parts(a)
            if kind in ("bor", "lbor", "slbor", "calque"):
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
        e.rejected = "foreign source: " + ",".join(sorted(set(foreign)))
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
    how: str               # chain | chain-proto-lexicon | root | pseudo | desc | lexicon | base
    steps: int

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
                sub = Hit(sub.ids, (f"{code}:{term}",) + sub.path, sub.how, sub.steps + 1)
            # the lexicon's reflex list names the lexeme directly; prefer it over a root- or pseudo-level chain
            hit = lex_hit if lex_hit and (sub is None or not sub.specific or sub.how != "chain") else sub
            if lex_hit and sub and sub.how == "chain" and sub.ids & lex_hit.ids:
                hit = Hit(sub.ids & lex_hit.ids, sub.path, "chain", sub.steps)
        self.memo[key] = hit
        return hit

    def entry_hit(self, e: Entry, code: str, depth: int = 0) -> Hit | None:
        best = None
        for src, term, _ in e.links:
            h = self.resolve(src, term, depth)
            if h and (best is None or _better(h, best)):
                best = h
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
    if h.how.startswith("pseudo") or h.how in ("base",):
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
    """Hittite: lowercase, ḫ → h, no hyphens, subscripts or determinatives,
    final citation -aš/-a- endings left in place (lemmas are stems in TLHdig)."""
    s = (s or "").lower().replace("ḫ", "h").replace("š", "s")
    s = _nfd_strip(s)
    s = re.sub(r"[₀-₉0-9]", "", s)
    return re.sub(r"[^a-z]", "", s)


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


KEYS = {"non": key_non, "ang": key_ang, "got": key_got, "cu": key_cu, "xcl": key_xcl, "hit": key_hit,
        "xum": key_xum, "lv": key_lv, "sga": key_sga, "ae": key_ae}


def entry_keys(e: Entry, lang: str) -> list[str]:
    """Join keys for an entry: transliterated scripts join on the
    romanization, Latin-script languages on the headword."""
    k = KEYS[lang]
    if LANGS[lang].script in ("gothic",):
        return [x for x in {k(e.word)} if x]
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


class LangMapping:
    """key → MapRec for one daughter language, plus a form → lemma-key
    lemmatizer for unlemmatized corpora."""

    def __init__(self, lang: str):
        self.lang = lang
        self.recs: dict[str, MapRec] = {}
        self.rejected: dict[str, str] = {}
        self.forms: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        self.lemma_words: set = set()

    def lookup(self, key: str) -> MapRec | None:
        return self.recs.get(key)


def build_lang_mapping(lang: str, lexicon: list[dict], protos: ProtoDB, root: Path = ROOT,
                       entries: list[Entry] | None = None, pseudo: bool = True,
                       idx: PieIndex | None = None) -> LangMapping:
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
    cands: dict[str, list[tuple[Hit, str, str]]] = collections.defaultdict(list)   # key → (hit, source, word)
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
                cands[k].append((Hit(h.ids, (f"{lang}:{e.word}",) + h.path, h.how, h.steps), "chain", e.word))
    # 2. descendants trees of proto-language pages
    for code in spec.desc_codes:
        for w, rom, pc, pt in protos.desc.get(code, []):
            h = res.resolve(pc, pt)
            if not h:
                continue
            for k in {K(w), K(rom or "")} if spec.script in ("latin", "avestan") else \
                    ({K(rom or "")} if spec.script in ("armenian", "cuneiform") else {K(w)}):
                if k:
                    cands[k].append((Hit(h.ids, (f"{lang}:{w}",) + h.path, "desc", h.steps + 1), "desc", w))
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
                    k = K(f.lstrip("*"))
                    if k and len(k) >= 2:
                        ids = {le["id"]} if le.get("kind") != "alt" else set(le.get("target_ids") or [le["id"]])
                        cands[k].append((Hit(frozenset(ids), (f"{lang}:{f}", f"ine-pro:{le['form']}"),
                                             "lexicon", 1), "lexicon", f))
    # combine
    for k, lst in cands.items():
        if k in bad and all(src != "lexicon" for _, src, _ in lst):
            continue
        spec_hits = [x for x in lst if x[0].specific]
        pool = spec_hits or lst
        best = min(pool, key=lambda x: (_HOW_RANK.get(x[0].how.split("-")[0], 9), x[0].steps))
        same_how = [x for x in pool if x[0].how == best[0].how]
        ids = frozenset().union(*(x[0].ids for x in same_how))
        srcs = tuple(sorted({x[1] for x in lst}))
        agree = len({x[1] for x in lst if x[0].ids & best[0].ids}) >= 2
        lm.recs[k] = MapRec(k, best[2], ids, best[0].path, best[0].how, confidence(best[0], agree), srcs)
    lm.rejected = {k: v for k, v in bad.items() if k not in lm.recs}
    # 4. base-word chains (diminutives, one-base derivations), two passes
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


def load_dcs(texts=DCS_VEDIC, corpus: str = "av", root: Path = ROOT) -> list[Token]:
    """DCS CoNLL-U (CC BY 4.0), the Vedic texts listed. Unit: DCS sentence
    (in the Atharvaveda usually a half-verse or verse); locus: chapter +
    sentence number in the chapter. The `.conllu_parsed` duplicates are skipped."""
    toks: list[Token] = []
    for t in texts:
        for fn in sorted((root / DCS_DIR / t).glob("*.conllu")):
            chapter, sent, nsent = fn.stem, None, 0
            for line in fn.read_text("utf-8").splitlines():
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
                    toks.append(Token(corpus, c[2], "", f"{chapter}.s{nsent}",
                                      {"sentence": f"{chapter}|{sent}", "chapter": chapter, "book": t},
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
                toks.append(Token(corpus, a["lemma"], "", f"{name} {line}",
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
    lem = lemmas.pop()
    if not re.search(r"[a-zḫšāēīū]", lem):
        return None
    parts = chosen[0].split("@")
    return lem, (parts[2] if len(parts) > 2 else "")


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
