"""Formula discovery (Phase 8a): cognate pairs that co-occur in both the
Rigveda and Homer more than chance predicts.

Pipeline:

  1. Corpus tokens → PIE lexemes. Rigveda: the VedaWeb Zurich annotation
     (CC BY 4.0) only, i.e. surface, Grassmann lemma, lemma class and
     Leipzig morphology; the NC text layers are never read. Homer: the
     Perseus AGDT treebank (LSJ lemmas, postags, dependency heads). A corpus
     lemma maps to lexicon entries through their reflexes, in tiers; the
     first tier that yields anything wins:
        direct    lexicon reflex key == corpus lemma key
        roots     Skt 3sg presents (cetáyati) reduced to a root (√cit-) and
                  checked against the corpus's root lemmas
        surface   lexicon reflex == an inflected corpus surface form whose
                  lemma is known (κλῦτε → κλύω)
        bridge    Proto-Indo-Iranian / -Indo-Aryan (→ Vedic) and
                  Proto-Hellenic (→ Greek) reflexes, transduced by a few
                  rules and accepted only if the result is a corpus lemma
     Each entry collapses to its `root_id` (one level; else its own id), so
     derivatives of one root count together.
  2. Co-occurrence per corpus, in units (RV pāda or stanza, Homer line) or
     in ±k-word windows. Dunning's log-likelihood ratio (G²) and PMI over
     the 2×2 table. A candidate pair must pass in both corpora; it is
     ranked by the weaker corpus's score.
  3. Evaluation against data/formulas/formulas.jsonl, split into halves by
     sha1(formula_id); tuning sees half A only.

The method can only see *etymological* pairs: a formula renewed with
non-cognate words (devá- / θεός) is invisible to it.
"""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import math
import random
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .other_mapping import contextual_lemma, homer_lemma, latin_lemma

ROOT = Path(__file__).resolve().parent.parent
RV_TEI = "raw/daughters/rigveda-vedaweb/extract/vedaweb-data-main/rigveda/TEI"
HOMER = "raw/daughters/homer-perseus-agdt"
HOMER_WORKS = {"tlg001": "Il.", "tlg002": "Od."}

SKT_LANGS = ("Sanskrit", "Vedic Sanskrit")
SKT_BRIDGE = ("Proto-Indo-Aryan", "Proto-Indo-Iranian")
GRC_LANGS = ("Ancient Greek", "Epic Greek", "Homeric Greek", "Ionic Greek", "Attic Greek", "Attic–Ionic Greek",
             "Epic, Ionic Greek")
GRC_BRIDGE = ("Proto-Hellenic",)
RV_CONTENT = {"nominal stem", "root"}
HOM_CONTENT = set("nva")          # AGDT postag[0]: noun, verb, adjective
RV_TIERS = ("direct", "roots", "surface", "bridge")
HOM_TIERS = ("direct", "unaccented", "surface", "bridge")
MAX_GROUPS = 3                    # a lemma mapping to more root groups than this is dropped as ambiguous


# ---------------------------------------------------------------- normalization

_ACC = "́̀"
_SKT_VOWELS = set("aeiou")


def skt_key(s: str) -> str:
    """Comparison key for Sanskrit in ISO 15919 or IAST: accents off vowels
    only (ś keeps its acute), r̥ l̥ → ṛ ḷ, ṁ → ṃ, no √ - * digits ⁱ."""
    out: list[str] = []
    base = ""
    syllabic = False
    for ch in unicodedata.normalize("NFD", s.lower()):
        if unicodedata.combining(ch):
            if ch in _ACC and (base in _SKT_VOWELS or syllabic):
                continue
            if ch in "̥̣" and base in "rl":
                syllabic = True
                ch = "̣"
            elif ch == "̇" and base == "m":
                ch = "̣"
            out.append(ch)
            continue
        base, syllabic = ch, False
        out.append(ch)
    s = unicodedata.normalize("NFC", "".join(out))
    return re.sub(r"[√*ⁱ0-9\s\-()]", "", s)


def skt_lemma_keys(lemma: str) -> list[str]:
    """`√īḍ- ~ īḷ-` → ['īḍ', 'īḷ'];  `√as- 1` → ['as']."""
    return [k for k in (skt_key(p) for p in lemma.split("~")) if k]


_GRC_LEN = "̄̆"
_GRC_MARKS = "́̀͂̓̔̈ͅ"


def grc_key(s: str, accents: bool = True) -> str:
    """Comparison key for Greek: macrons and breves off (the lexicon writes
    them), grave → acute, ς → σ; with accents=False also accents,
    breathings, diaeresis and iota subscript off."""
    out = []
    for ch in unicodedata.normalize("NFD", s.lower()):
        if ch in _GRC_LEN:
            continue
        if ch == "̀":
            ch = "́"
        if not accents and ch in _GRC_MARKS:
            continue
        out.append(ch)
    s = unicodedata.normalize("NFC", "".join(out)).replace("ς", "σ")
    return re.sub(r"[0-9*\-\s'’ʼ᾽()]", "", s)


_ROM = {"α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "ē", "θ": "th", "ι": "i", "κ": "k",
        "λ": "l", "μ": "m", "ν": "n", "ξ": "ks", "ο": "o", "π": "p", "ρ": "r", "σ": "s", "τ": "t", "υ": "u",
        "φ": "ph", "χ": "kh", "ψ": "ps", "ω": "ō", "ϝ": ""}


def grc_roman(s: str) -> str:
    """Unaccented Latin transliteration of a Greek word (γγ → ng), used to
    compare Proto-Hellenic reconstructions with Homeric lemmas."""
    k = grc_key(s, accents=False).replace("γγ", "νγ").replace("γκ", "νκ").replace("γχ", "νχ")
    return "".join(_ROM.get(c, c) for c in k)


def pie_key(s: str) -> str:
    """PIE comparison key: no accents (ḱ ǵ keep theirs), vowel length,
    hyphens or asterisks."""
    out: list[str] = []
    base, syllabic = "", False
    for ch in unicodedata.normalize("NFD", s.lower()):
        if unicodedata.combining(ch):
            if ch == "̄" or (ch in _ACC and (base in "aeiouy" or syllabic)):
                continue
            syllabic = syllabic or ch == "̥"
            out.append(ch)
            continue
        base, syllabic = ch, False
        out.append(ch)
    return re.sub(r"[*\-\s()]", "", unicodedata.normalize("NFC", "".join(out)))


# ---------------------------------------------------------------- Sanskrit verb root table

_PRES_ENDINGS = ("āyati", "āyate", "ayati", "ayate", "ṇoti", "ṇute", "noti", "nute", "ṇāti", "nāti", "ṇīte", "nīte",
                 "yati", "yate", "ati", "ate", "anti", "ante", "ti", "te", "mi", "si", "ṣi", "e")
_REDUP = {"d": "d", "b": "b", "p": "p", "t": "t", "j": "jghk", "c": "kc", "s": "s", "ś": "ś", "m": "m", "n": "n",
          "y": "y", "v": "v", "r": "r", "h": "h", "g": "g", "k": "k", "bh": "b"}


def _ungunate(stem: str) -> list[str]:
    out = [stem]
    for a, b in (("ar", "ṛ"), ("ra", "ṛ"), ("e", "i"), ("o", "u"), ("ay", "i"), ("av", "u"), ("ā", "a")):
        i = stem.rfind(a)
        if i >= 0:
            out.append(stem[:i] + b + stem[i + len(a):])
    return out


def _unreduplicate(stem: str) -> list[str]:
    if len(stem) >= 4 and stem[1] in "aiuā" and stem[0] in _REDUP and stem[2] in _REDUP[stem[0]] + stem[0]:
        return [stem[2:]]
    return []


def skt_root_candidates(key: str) -> list[str]:
    """Candidate roots for a Sanskrit verb form key, most specific first:
    cetayati → … cit;  dadhāti → dhā;  juhoti → hu;  śṛṇoti → śṛ."""
    out: list[str] = []
    for e in _PRES_ENDINGS:
        if key.endswith(e) and len(key) > len(e) + 1:
            stem = key[: -len(e)]
            for s in [stem] + _unreduplicate(stem):
                out += _ungunate(s)
            break
    seen: set[str] = set()
    return [c for c in out if len(c) >= 2 and not (c in seen or seen.add(c))]


# ---------------------------------------------------------------- proto-language bridges

_PII_RULES = [("ȷ́ʰ", "h"), ("ȷ́", "j"), ("ǰʰ", "h"), ("ǰ", "j"), ("ć", "ś"),
              ("č", "c"), ("š", "ṣ"), ("ž", ""), ("ẓʰ", "h"), ("ʰ", "h"), ("w", "v"),
              ("l̥", "r̥"), ("ˢ", ""), ("ᶻ", ""), ("⁠", ""), ("ȷ", "j")]
_V = "aeiouāīūṛ"


def pii_to_skt(form: str) -> list[str]:
    """Candidate Vedic keys for a Proto-Indo-Iranian / -Indo-Aryan form:
    *Háćwas → aśvas, aśva;  *ǰʰan- → han;  *dʰar- → dhar, dhṛ;  *pHtā́ → pitā, pitar.
    Laryngeals: VH → long vowel, CHC → CiC, otherwise lost."""
    s = unicodedata.normalize("NFD", form.strip().lstrip("*"))
    if " " in s or "~" in s or "," in s:
        return []
    for a, b in _PII_RULES:
        s = s.replace(a, b)
    k = skt_key(s.replace("H", "ʔ"))
    longv = {"a": "ā", "i": "ī", "u": "ū"}
    k = re.sub(r"([aiu])ʔ", lambda m: longv[m[1]], k)
    k = re.sub(rf"(?<=[^{_V}ʔ])ʔ(?=[^{_V}ʔ])", "i", k).replace("ʔ", "")
    return _skt_stem_variants(k) if k else []


def _skt_stem_variants(k: str, verbal: bool = True) -> list[str]:
    """A Sanskrit key and its plausible citation stems, most literal first;
    verbal=True adds root candidates."""
    out = [k]
    for end, reps in (("as", ["a"]), ("am", ["a"]), ("is", ["i"]), ("iṣ", ["i"]), ("us", ["u"]), ("uṣ", ["u"]),
                      ("ās", ["ā"]), ("ā", ["ar", ""]), ("ṛ", ["ar"]), ("ay", ["i"]), ("s", [""])):
        if k.endswith(end) and len(k) > len(end) + 1:
            out += [k[: -len(end)] + r for r in reps]
            break
    if verbal:
        out += skt_root_candidates(k) + _ungunate(k)[1:]
    return list(dict.fromkeys(out))


def ph_to_grc(form: str) -> list[str]:
    """Candidate romanized Homeric keys for a Proto-Hellenic form:
    *kléwos → kleos;  *pʰérō → pherō;  *íkkʷos → ippos;  *Dzéus → zeus;
    *mā́tēr → mētēr (Ionic ā → ē) or mātēr."""
    s = unicodedata.normalize("NFD", form.strip().lstrip("*").lower())
    if " " in s or "~" in s:
        return []
    out_chars, base = [], ""
    for ch in s:
        if unicodedata.combining(ch):
            if ch in "\u0301\u0300\u0342\u0306\u034f\u030c" or (ch == "\u0304" and base in "iu"):
                continue
        else:
            base = ch
        out_chars.append(ch)
    s = unicodedata.normalize("NFC", "".join(out_chars)).replace("-", "").replace("ʰ", "h")
    s = s.replace("kkʷ", "pp").replace("dz", "z")
    s = re.sub(r"kʷh(?=[eiēī])", "th", s)
    s = re.sub(r"kʷ(?=[eiēī])", "t", s)
    s = re.sub(r"gʷ(?=[eē])", "d", s)
    s = s.replace("kʷh", "ph").replace("kʷ", "p").replace("gʷ", "b")
    s = s.replace("w", "").replace("ə", "a")
    s = re.sub(r"^h", "", s)
    s = re.sub(r"(?<=[aeiouāēō])[hy](?=[aeiouāēō])", "", s)
    s = re.sub(r"ky|ty", "ss", s).replace("dy", "z").replace("gy", "z").replace("ly", "ll")
    out = [s]
    if "ā" in s:
        out += [s.replace("ā", "ē"), s.replace("ā", "a")]
    return [o for o in dict.fromkeys(out) if len(o) >= 3]


# ---------------------------------------------------------------- corpora

@dataclass
class Token:
    corpus: str          # "rv" | "hom"
    lemma: str
    surface: str
    locus: str           # "RV 1.1.1a" | "Il. 1.1"
    units: dict          # unit name → unit id: pada/stanza/hymn (rv), line/sentence/book (hom)
    content: bool
    pos: str             # coarse: noun, verb, adj, other
    case: str | None = None
    number: str | None = None
    finite: bool = False
    head: int | None = None   # global index of the dependency head (hom)
    rel: str | None = None
    roots: frozenset = frozenset()

    def __post_init__(self):
        from .w6_other_mapping import annotated_name
        if annotated_name(self.corpus, self.lemma, self.pos):
            from .name_mapping import name_lemma
            self.lemma = name_lemma(self.corpus, self.lemma)
            self.content = not self.lemma.endswith(' (name)')
            self.pos = 'noun' if self.content else 'name'
        self.lemma = contextual_lemma(self.corpus, self.lemma, self.surface, self.locus)
        if self.corpus == 'vuk' and self.lemma == 'more@sea':
            self.content, self.pos = True, 'noun'
        if self.lemma.endswith(('@conjunction','@preposition','@interrogative')):
            self.content, self.pos = False, 'other'
        if self.corpus in {'menota', 'icepahc', 'grc', 'grp', 'grc-late', 'hom',
                           'av', 'sa-ep', 'orv', 'lat'} and self.lemma.endswith(' (name)'):
            self.content = False
        if self.corpus == "xcl" and self.lemma == "34@numeral":
            self.content, self.pos = False, "other"


_RV_ID = re.compile(r'xml:id="b(\d+)_h(\d+)_(\d+)_zur_([a-z])_\d+"')
_RV_F = re.compile(r'<f name="(surface|gra_lemma|gra_gramm|case|number|person|non-finite|tense)">\s*'
                   r'<(?:string|symbol)[^>]*?(?:value="([^"]*)")?\s*/?>([^<]*)')


def parse_rv_block(block: str) -> dict | None:
    """One Zurich `<fs type="zurich_info">` block → fields (no text layers)."""
    m = _RV_ID.search(block)
    if not m:
        return None
    f = {k: (v or t).strip() for k, v, t in _RV_F.findall(block)}
    return {"book": int(m[1]), "hymn": int(m[2]), "stanza": int(m[3]), "pada": m[4], **f}


def load_rv(root: Path = ROOT) -> list[Token]:
    toks = []
    for fn in sorted((root / RV_TEI).glob("rv_book_*.tei")):
        text = fn.read_text("utf-8")
        for block in text.split('<fs type="zurich_info"')[1:]:
            b = parse_rv_block('<fs type="zurich_info"' + block.split("</l>")[0])
            if not b or not b.get("gra_lemma"):
                continue
            cls = b.get("gra_gramm", "")
            st = f"{b['book']}.{b['hymn']}.{b['stanza']}"
            pos = ("verb" if cls == "root" and not b.get("case") else
                   "noun" if cls in ("nominal stem", "root") else "other")
            toks.append(Token("rv", b["gra_lemma"], b.get("surface", ""), f"RV {st}{b['pada']}",
                              {"pada": f"{st}{b['pada']}", "stanza": st, "hymn": f"{b['book']}.{b['hymn']}"},
                              cls in RV_CONTENT, pos, b.get("case"), b.get("number"),
                              finite=bool(b.get("person"))))
    return toks


_HOM_W = re.compile(r"<word ([^>]*)/>")
_ATTR = re.compile(r'(\w+)="([^"]*)"')
_HOM_CASE = {"n": "NOM", "g": "GEN", "d": "DAT", "a": "ACC", "v": "VOC"}
_HOM_NUM = {"s": "SG", "p": "PL", "d": "DU"}


def load_homer(root: Path = ROOT) -> list[Token]:
    toks: list[Token] = []
    for fn in sorted((root / HOMER).glob("tlg0012.*.tb.xml")):
        text = fn.read_text("utf-8")
        for si, sent in enumerate(text.split("<sentence ")[1:]):
            local: dict[str, int] = {}
            heads: list[tuple[int, str]] = []
            last_cite = None
            for m in _HOM_W.finditer(sent):
                a = dict(_ATTR.findall(m[1]))
                tag = (a.get("postag") or "-" * 9).ljust(9, "-")
                if tag[0] == "u" or not a.get("lemma"):
                    continue
                cite = a.get("cite") or last_cite
                last_cite = cite
                if not cite:
                    continue
                work, line = cite.rsplit(":", 2)[-2:]
                # AGDT sentence 2187720 has a truncated cite on its final
                # seven words; the sentence subdoc ends at Odyssey 8.586.
                if work == 'tlg0012.tlg002' and line == '8' and sent.startswith('subdoc="8.585-8.586" id="2187720"'):
                    line = '8.586'
                work = HOMER_WORKS.get(work.split(".")[-1], work)
                book = line.split(".")[0]
                pos = {"n": "noun", "a": "adj", "v": "verb"}.get(tag[0], "other")
                finite = tag[0] == "v" and tag[4] in "isom"
                if tag[0] == "v" and tag[4] == "p":
                    pos = "adj"      # participles agree like adjectives
                local[a.get("id", "")] = len(toks)
                heads.append((len(toks), a.get("head", "")))
                toks.append(Token("hom", homer_lemma(a["lemma"], a.get("form", "")), a.get("form", ""), f"{work} {line}",
                                  {"line": f"{work} {line}", "sentence": f"{fn.stem[:15]}.{si}",
                                   "book": f"{work} {book}"},
                                  tag[0] in HOM_CONTENT, pos, _HOM_CASE.get(tag[7]), _HOM_NUM.get(tag[2]),
                                  finite=finite, rel=a.get("relation")))
            for i, h in heads:
                toks[i].head = local.get(h)
    return toks


# ---------------------------------------------------------------- lexicon → corpus lemma mapping

def group_of(e: dict) -> str:
    return e.get("root_id") or e["id"]


@dataclass
class Mapping:
    lemma_groups: dict[str, frozenset] = field(default_factory=dict)   # corpus lemma → root groups
    lemma_tier: dict[str, str] = field(default_factory=dict)
    ambiguous: set = field(default_factory=set)
    lemma_lex: dict[str, frozenset] = field(default_factory=dict)      # corpus lemma → lexicon entry ids


def group_map(lexicon: list[dict]) -> dict[str, str]:
    return {e["id"]: group_of(e) for e in lexicon}


def _reflex_forms(e: dict, langs, roman: bool) -> list[str]:
    out = []
    for L in langs:
        for r in (e.get("reflexes") or {}).get(L, []):
            if r.get("borrowed") or r.get("uncertain"):
                continue
            f = (r.get("roman") if roman else None) or r.get("form")
            if f and not f.startswith("-"):
                out.append(f)
    return out


def _finish(cands: dict[str, dict[str, set]], lemmas: dict[str, list[str]], gmap: dict[str, str]) -> Mapping:
    """cands: tier → lemma-key → entry ids, in priority order; lemmas: corpus
    lemma → its keys; gmap: entry id → root group."""
    m = Mapping()
    for lemma, keys in lemmas.items():
        for tier in cands:
            ids = set().union(*(cands[tier].get(k, set()) for k in keys)) if keys else set()
            if ids:
                g = {gmap.get(i, i) for i in ids}
                if len(g) > MAX_GROUPS:
                    m.ambiguous.add(lemma)
                else:
                    m.lemma_groups[lemma] = frozenset(g)
                    m.lemma_lex[lemma] = frozenset(ids)
                    m.lemma_tier[lemma] = tier
                break
    return m


_SKT_CONS_START = re.compile(r"^[^aeiouāīūṛ]")


def skt_privative(key: str) -> list[str]:
    """Base candidates for a Vedic privative: akṣita → kṣita, kṣi;
    amṛta → mṛta, mṛ;  anāgas → āgas."""
    if key.startswith("an") and len(key) > 4 and not _SKT_CONS_START.match(key[2:]):
        r = key[2:]
    elif key.startswith("a") and len(key) > 3 and _SKT_CONS_START.match(key[1:]):
        r = key[1:]
    else:
        return []
    out = [r]
    for end in ("ita", "ta", "na", "iti", "ti"):
        if r.endswith(end) and len(r) > len(end) + 1:
            out += _ungunate(r[: -len(end)])
    return list(dict.fromkeys(out))


_GRC_VOWEL_START = re.compile(r"^[αεηιουω]")


def grc_privative(key: str) -> list[str]:
    """Base candidates (unaccented keys) for a Greek privative:
    αφθιτοσ → φθιτοσ, φθιω;  αμβροτοσ → βροτοσ;  ανωνυμοσ → ωνυμοσ."""
    if key.startswith("αν") and len(key) > 4 and _GRC_VOWEL_START.match(key[2:]):
        r = key[2:]
    elif key.startswith("α") and len(key) > 4 and not _GRC_VOWEL_START.match(key[1:]):
        r = key[1:]
        if r.startswith("μβ"):
            r = r[1:]
    else:
        return []
    out = [r]
    for end, new in (("ιτοσ", "ιω"), ("τοσ", "ω"), ("τοσ", "μι"), ("οσ", "ω")):
        if r.endswith(end) and len(r) > len(end) + 1:
            out.append(r[: -len(end)] + new)
    return list(dict.fromkeys(out))


def _add_privatives(m: Mapping, lemmas: dict[str, list[str]], bases) -> None:
    """Tier 'privative': an unmapped lemma that is a- / an- + a mapped base
    takes the base's groups (ákṣita- → √kṣi-, ἄφθιτος → φθίω)."""
    by_key: dict[str, set] = collections.defaultdict(set)
    by_key_lex: dict[str, set] = collections.defaultdict(set)
    for lem, g in m.lemma_groups.items():
        for k in lemmas.get(lem, []):
            by_key[k] |= g
            by_key_lex[k] |= m.lemma_lex.get(lem, g)
    for lem, keys in lemmas.items():
        if lem in m.lemma_groups or lem in m.ambiguous:
            continue
        for k in keys:
            b = next((b for b in bases(k) if b in by_key), None)
            if b:
                m.lemma_groups[lem] = frozenset(by_key[b])
                m.lemma_lex[lem] = frozenset(by_key_lex[b])
                m.lemma_tier[lem] = "privative"
                break


def _surface_index(tokens: list[Token], key) -> dict[str, collections.Counter]:
    idx: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for t in tokens:
        k = key(t.surface)
        if k:
            idx[k][t.lemma] += 1
    return idx


def _majority(c: collections.Counter, min_len_key: str, share: float = 0.6) -> str | None:
    if len(min_len_key) < 4 or not c:
        return None
    lemma, n = c.most_common(1)[0]
    return lemma if n / sum(c.values()) >= share else None


def build_rv_mapping(lexicon: list[dict], tokens: list[Token]) -> Mapping:
    lemmas = {t.lemma: skt_lemma_keys(t.lemma) for t in tokens}
    all_keys = {k for ks in lemmas.values() for k in ks}
    root_keys = {k for lem, ks in lemmas.items() if lem.startswith("√") for k in ks}
    surf = _surface_index(tokens, skt_key)
    cands = {t: collections.defaultdict(set) for t in RV_TIERS}
    for e in lexicon:
        g = e["id"]
        for f in _reflex_forms(e, SKT_LANGS, roman=True):
            k = skt_key(f)
            cands["direct"][k].add(g)
            for c in _skt_stem_variants(k, verbal=False)[1:]:
                if c in all_keys and len(c) >= 3:
                    cands["roots"][c].add(g)      # nominal citation variant: pitṛ → pitar
                    break
            for c in skt_root_candidates(k):
                if c in root_keys:
                    cands["roots"][c].add(g)
                    break
            if (lem := _majority(surf.get(k, collections.Counter()), k)):
                for lk in skt_lemma_keys(lem):
                    cands["surface"][lk].add(g)
        for f in _reflex_forms(e, SKT_BRIDGE, roman=False):
            for c in pii_to_skt(f):
                if c in all_keys and len(c) >= 3:
                    cands["bridge"][c].add(g)
                    break
    m = _finish(cands, lemmas, group_map(lexicon))
    _add_privatives(m, lemmas, skt_privative)
    return m


def build_homer_mapping(lexicon: list[dict], tokens: list[Token]) -> Mapping:
    lemmas = {t.lemma: [grc_key(t.lemma), "~" + grc_key(t.lemma, accents=False)] for t in tokens}
    roman = collections.defaultdict(set)
    for lem in lemmas:
        roman[grc_roman(lem)].add(lem)
    surf = _surface_index(tokens, grc_key)
    cands = {t: collections.defaultdict(set) for t in HOM_TIERS}
    for e in lexicon:
        g = e["id"]
        for f in _reflex_forms(e, GRC_LANGS, roman=False):
            cands["direct"][grc_key(f)].add(g)
            cands["unaccented"]["~" + grc_key(f, accents=False)].add(g)
            k = grc_key(f)
            if (lem := _majority(surf.get(k, collections.Counter()), k)):
                cands["surface"][grc_key(lem)].add(g)
        for f in _reflex_forms(e, GRC_BRIDGE, roman=False):
            for c in ph_to_grc(f):
                if c in roman and len(roman[c]) <= 3:      # πατήρ / πάτηρ / πατηρ: one word
                    for lem in roman[c]:
                        cands["bridge"][grc_key(lem)].add(g)
                    break
    m = _finish(cands, lemmas, group_map(lexicon))
    _add_privatives(m, {lem: [grc_key(lem, accents=False)] for lem in lemmas}, grc_privative)
    return m


# ---------------------------------------------------------------- kaikki (wiktextract) etymology links

KAIKKI = {"sa": "raw/daughters/kaikki-sanskrit/kaikki.org-dictionary-Sanskrit.jsonl",
          "grc": "raw/daughters/kaikki-ancientgreek/kaikki.org-dictionary-AncientGreek.jsonl",
          "la": "raw/daughters/kaikki-latin/kaikki.org-dictionary-Latin.jsonl"}
# intermediate proto-languages whose reflex lists in our lexicon can carry a link
KAIKKI_PROTO = {"sa": {"iir-pro": "Proto-Indo-Iranian", "inc-pro": "Proto-Indo-Aryan"},
                "grc": {"grk-pro": "Proto-Hellenic"},
                "la": {"itc-pro": "Proto-Italic"}}
_LINK_TEMPLATES = ("inh", "inh+", "der", "der+", "uder", "bor", "lbor")
_AFFIX_TEMPLATES = ("af", "affix", "suffix", "prefix", "confix")
KAIKKI_TIERS = ("kaikki", "kaikki-proto", "kaikki-root", "kaikki-chain")


def _inline_strip(s: str) -> str:
    """`सम्-<alt:सं-><t:altogether>` → `सम्-`."""
    return re.sub(r"<[^>]*>", "", s or "").strip()


def _numbered(a: dict, start: int) -> list[str]:
    out = []
    for k in sorted((k for k in a if k.isdigit() and int(k) >= start), key=int):
        v = _inline_strip(a[k])
        if v:
            out.append(v)
    return out


def kaikki_entry_links(d: dict, lang: str) -> dict | None:
    """The etymological links of one wiktextract entry (pure; no lexicon):
      pie       PIE terms from inh/der/bor templates (most specific first)
      pie_root  PIE roots from {{root|<lang>|ine-pro|...}}
      proto     (code, term) from intermediate proto-languages (iir-pro, grk-pro, ...)
      bases     same-language words it is derived from ({{root|sa|sa|√...}},
                {{der|grc|grc|...}}, an affix template with exactly one non-affix part)
    Returns None if there is none of these."""
    pie, pie_root, proto, bases = [], [], [], []
    protos = KAIKKI_PROTO.get(lang, {})
    for t in d.get("etymology_templates") or []:
        name, a = t.get("name"), t.get("args") or {}
        if a.get("1") != lang:
            continue
        if name in _LINK_TEMPLATES:
            term = _inline_strip(a.get("3") or a.get("4") or "")
            src = a.get("2")
            if not term or term == "-":
                continue
            if src == "ine-pro":
                pie.append(term)
            elif src in protos:
                proto.append((src, term))
            elif src == lang and name in ("der", "inh"):
                bases.append(term)
        elif name == "root":
            terms = _numbered(a, 3)
            if a.get("2") == "ine-pro":
                pie_root += terms
            elif a.get("2") == lang:
                bases += terms
        elif name in _AFFIX_TEMPLATES:
            parts = _numbered(a, 2)
            if name == "suffix":
                content = parts[:1]
            elif name == "prefix":
                content = parts[-1:]
            else:
                content = [p for p in parts if not p.startswith("-") and not p.endswith("-")]
            if len(content) == 1:
                bases.append(content[0])
    if not (pie or pie_root or proto or bases):
        return None
    roman = next((f.get("form") for f in d.get("forms") or [] if "romanization" in (f.get("tags") or [])), None)
    if not roman:
        for h in d.get("head_templates") or []:
            roman = (h.get("args") or {}).get("tr") or None
            if roman:
                break
    return {"word": d.get("word"), "roman": roman, "pos": d.get("pos"), "pie": pie, "pie_root": pie_root,
            "proto": proto, "bases": bases}


def read_kaikki(path: Path, lang: str) -> list[dict]:
    """Stream a wiktextract JSONL dump (never executed, only parsed) and
    keep the entries with etymological links."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if '"etymology_templates"' not in line:
                continue
            r = kaikki_entry_links(json.loads(line), lang)
            if r:
                out.append(r)
    return out


def load_kaikki_links(lang: str, root: Path = ROOT, cache_dir: Path | None = None) -> list[dict]:
    """read_kaikki with a JSONL cache (the cache holds only words, romanizations
    and linked etymon strings)."""
    cache_dir = cache_dir or root / "data/research/formulas/kaikki_links"
    cache = cache_dir / f"{lang}.jsonl"
    if cache.exists():
        return load_jsonl(cache)
    recs = read_kaikki(root / KAIKKI[lang], lang)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), "utf-8")
    return recs


def _pie_term_keys(term: str) -> list[tuple[str, str]]:
    """(exact canonical form, accentless key) pairs for a PIE term as
    Wiktionary writes it (*(h₁)wiḱ-wo-s, *ḱléw-), via the lexicon's own
    parser and pie.notation."""
    from .lexicon import parse_form
    raw = term.strip()
    p = parse_form(raw if raw.startswith("*") else "*" + raw)
    if p.lemma is None:
        return [("", pie_key(raw))]
    return [(f, pie_key(f)) for f in [p.lemma, *p.variants]]


class PieIndex:
    """Lexicon lookup for linked PIE terms (exact canonical form first, then
    the accent/length-free key) and for intermediate proto-forms through the
    lexicon's reflex lists (Proto-Indo-Iranian *ćráwas → *ḱléwos)."""

    def __init__(self, lexicon: list[dict]):
        self.exact: dict[str, set] = collections.defaultdict(set)
        self.loose: dict[str, set] = collections.defaultdict(set)
        self.proto: dict[tuple[str, str], set] = collections.defaultdict(set)
        self.kind = {e["id"]: e.get("kind") for e in lexicon}
        for e in lexicon:
            if e.get("kind") == "affix":
                continue
            ids = set(e.get("target_ids") or []) if e.get("kind") == "alt" and e.get("target_ids") else {e["id"]}
            for f in [e["form"], *(e.get("variants") or [])]:
                self.exact[f].update(ids)
                self.loose[pie_key(f)].update(ids)
            for L, rs in (e.get("reflexes") or {}).items():
                if not L.startswith("Proto-"):
                    continue
                for r in rs:
                    if r.get("form") and not r.get("borrowed"):
                        self.proto[(L, self.proto_key(r["form"]))].update(ids)

    @staticmethod
    def proto_key(s: str) -> str:
        s = unicodedata.normalize("NFD", s.strip().lstrip("*").lower())
        s = "".join(c for c in s if c not in "́̀͂̄̆")
        return re.sub(r"[\s\-()⁠]", "", unicodedata.normalize("NFC", s))

    def pie(self, term: str, roots_only: bool = False) -> set:
        keys = _pie_term_keys(term)
        for table, i in ((self.exact, 0), (self.loose, 1)):
            for k in keys:
                ids = table.get(k[i])
                if ids:
                    if roots_only:
                        ids = {x for x in ids if self.kind.get(x) == "root"} or ids
                    return set(ids)
        return set()

    def via_proto(self, lang: str, code: str, term: str) -> set:
        L = KAIKKI_PROTO.get(lang, {}).get(code)
        return set(self.proto.get((L, self.proto_key(term)), ())) if L else set()


def pseudo_id(term: str) -> str | None:
    """Id for a linked PIE etymon that our lexicon lacks: 'kaikki:' + its
    accent-free key, so Sanskrit and Greek entries linking the same
    reconstruction page meet. Its root group is itself."""
    k = _pie_term_keys(term)[0][1]
    return f"kaikki:{k}" if len(k) >= 3 else None


def resolve_kaikki(links: list[dict], idx: PieIndex, lang: str, word_key,
                   pseudo: bool = False) -> dict[str, tuple[str, set]]:
    """kaikki word key → (tier, lexicon entry ids). Homograph entries of one
    word are unioned within the best tier. Tiers, most specific first:
    kaikki (a PIE etymon in our lexicon), kaikki-proto (an intermediate
    proto-form listed as a reflex of a lexicon entry), kaikki-root (the
    {{root}} template), kaikki-chain (derived from a same-language word that
    is itself linked; two passes), and with pseudo=True kaikki-pseudo (a PIE
    etymon not in our lexicon, see pseudo_id)."""
    rank = {t: i for i, t in enumerate(KAIKKI_TIERS + ("kaikki-pseudo",))}
    best: dict[str, tuple[str, set]] = {}

    def put(k, tier, ids):
        if not ids or not k:
            return
        cur = best.get(k)
        if cur is None or rank[tier] < rank[cur[0]]:
            best[k] = (tier, set(ids))
        elif cur[0] == tier:
            cur[1].update(ids)

    for r in links:
        k = word_key(r["word"])
        ids = next((x for x in (idx.pie(t) for t in r["pie"]) if x), set())
        if ids:
            put(k, "kaikki", ids)
            continue
        ids = next((x for x in (idx.via_proto(lang, c, t) for c, t in r["proto"]) if x), set())
        if ids:
            put(k, "kaikki-proto", ids)
            continue
        ids = next((x for x in (idx.pie(t, roots_only=True) for t in r["pie_root"]) if x), set())
        if ids:
            put(k, "kaikki-root", ids)
            continue
        if pseudo and r["pie"] and (pid := pseudo_id(r["pie"][0])):
            put(k, "kaikki-pseudo", {pid})
    for _ in range(2):
        for r in links:
            k = word_key(r["word"])
            if k in best and best[k][0] not in ("kaikki-chain", "kaikki-pseudo"):
                continue
            for b in r["bases"]:
                hit = best.get(word_key(b.lstrip("√")))
                if hit and word_key(b.lstrip("√")) != k:
                    put(k, "kaikki-chain", hit[1])
                    break
    return best


def _deva_key(s: str) -> str:
    """Devanagari word key: no svara accents, no √, no spaces."""
    return re.sub(r"[॒॑᳚√\s\-]", "", unicodedata.normalize("NFC", s or ""))


def lat_key(s: str) -> str:
    """Latin key: lowercase, no macrons/breves/accents, v → u, j → i, no digits."""
    s = "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.replace("v", "u").replace("j", "i"))


def kaikki_corpus_mapping(links: list[dict], resolved: dict, lang: str, corpus_lemmas, gmap: dict) -> Mapping:
    """Corpus lemma → lexicon entries through kaikki words. Sanskrit joins on
    the romanization (skt_key; a verb's present also yields root candidates),
    Greek on the polytonic headword (grc_key), Latin on lat_key."""
    wk = word_key_for(lang)
    by_corpus_key: dict[str, dict[str, set]] = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in links:
        hit = resolved.get(wk(r["word"]))
        if not hit:
            continue
        tier, ids = hit
        if lang == "sa":
            if not r.get("roman"):
                continue
            k = skt_key(r["roman"])
            keys = [k] + (skt_root_candidates(k)[:3] if r.get("pos") == "verb" else [])
        elif lang == "grc":
            keys = [grc_key(r["word"])]
        else:
            keys = [lat_key(r["word"])]
        for k in keys:
            if k:
                by_corpus_key[k][tier].update(ids)
    cands = {t: collections.defaultdict(set) for t in KAIKKI_TIERS + ("kaikki-pseudo",)}
    for k, tiers in by_corpus_key.items():
        for t, ids in tiers.items():
            cands[t][k] |= ids
    return _finish(cands, corpus_lemmas, gmap)


def word_key_for(lang: str):
    return {"sa": _deva_key, "grc": grc_key, "la": lat_key}[lang]


def merge_mappings(primary: Mapping, backoff: Mapping) -> Mapping:
    """primary where it has the lemma, else backoff (tiers keep their names)."""
    m = Mapping(dict(backoff.lemma_groups), dict(backoff.lemma_tier), set(backoff.ambiguous),
                dict(backoff.lemma_lex))
    for lem, g in primary.lemma_groups.items():
        m.lemma_groups[lem] = g
        m.lemma_lex[lem] = primary.lemma_lex[lem]
        m.lemma_tier[lem] = primary.lemma_tier[lem]
        m.ambiguous.discard(lem)
    return m


def rv_corpus_lemmas(tokens: list[Token]) -> dict[str, list[str]]:
    return {t.lemma: skt_lemma_keys(t.lemma) for t in tokens}


def homer_corpus_lemmas(tokens: list[Token]) -> dict[str, list[str]]:
    return {t.lemma: [grc_key(t.lemma)] for t in tokens}


def latin_corpus_lemmas(tokens: list[Token]) -> dict[str, list[str]]:
    return {t.lemma: [lat_key(t.lemma)] for t in tokens}


def build_kaikki_mapping(lang: str, lexicon: list[dict], tokens: list[Token], backoff: Mapping | None,
                         root: Path = ROOT, links: list[dict] | None = None, pseudo: bool = False) -> Mapping:
    links = links if links is not None else load_kaikki_links(lang, root)
    resolved = resolve_kaikki(links, PieIndex(lexicon), lang, word_key_for(lang), pseudo)
    lemmas = {"sa": rv_corpus_lemmas, "grc": homer_corpus_lemmas, "la": latin_corpus_lemmas}[lang](tokens)
    m = kaikki_corpus_mapping(links, resolved, lang, lemmas, group_map(lexicon))
    if lang == "grc":      # unaccented fallback for lemma spellings that differ only in accent
        lem2 = {lem: ["~" + grc_key(lem, accents=False)] for lem in lemmas if lem not in m.lemma_groups}
        cands = {t: collections.defaultdict(set) for t in KAIKKI_TIERS + ("kaikki-pseudo",)}
        for r in links:
            hit = resolved.get(grc_key(r["word"]))
            if hit:
                cands[hit[0]]["~" + grc_key(r["word"], accents=False)] |= hit[1]
        m2 = _finish(cands, lem2, group_map(lexicon))
        m = merge_mappings(m, m2)
    # pseudo links (etyma missing from the lexicon) rank below the backoff mapping
    main, extra = Mapping(), Mapping()
    for lem, t in m.lemma_tier.items():
        tgt = extra if t == "kaikki-pseudo" else main
        tgt.lemma_groups[lem], tgt.lemma_lex[lem], tgt.lemma_tier[lem] = m.lemma_groups[lem], m.lemma_lex[lem], t
    main.ambiguous = set(m.ambiguous)
    out = merge_mappings(main, backoff) if backoff else main
    return _fill(out, extra)


def _fill(m: Mapping, extra: Mapping) -> Mapping:
    """m plus extra's lemmas that m lacks."""
    for lem, g in extra.lemma_groups.items():
        if lem not in m.lemma_groups:
            m.lemma_groups[lem], m.lemma_lex[lem], m.lemma_tier[lem] = g, extra.lemma_lex[lem], extra.lemma_tier[lem]
            m.ambiguous.discard(lem)
    return m


# ---------------------------------------------------------------- Latin (LASLA, CC BY-NC-SA: research use only)

LATIN = "raw/daughters/latin-lasla/conllup"
LAT_CONTENT = {"NOUN", "VERB", "ADJ"}
_LAT_CASE = {"Nom": "NOM", "Gen": "GEN", "Dat": "DAT", "Acc": "ACC", "Voc": "VOC", "Abl": "ABL", "Loc": "LOC"}
_LAT_NUM = {"Sing": "SG", "Plur": "PL"}


def load_latin(root: Path = ROOT) -> list[Token]:
    """LASLA CoNLL-U+: lemma, UPOS, FEATS, citation (verse or paragraph).
    No dependency heads in this release. Units: line (verse/paragraph),
    sentence, work (segment for windows). Surface forms are kept in memory
    only; nothing Latin is written out except lemmas and loci."""
    toks: list[Token] = []
    for fn in sorted((root / LATIN).glob("*.conllup")):
        work = fn.stem.split("_")[-1]
        sent = None
        for line in fn.read_text("utf-8").splitlines():
            if line.startswith("# sent_id"):
                sent = line.split("=", 1)[1].strip()
                continue
            if not line or line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 10 or "-" in c[0] or not c[2] or c[2] == "_":
                continue
            misc = dict(x.split("=", 1) for x in c[9].split("|") if "=" in x)
            cite = misc.get("CitationHierarchy", "").replace("Liber_", "").replace("Versus_", "") \
                .replace("Capitulum_", "").replace("Paragraphus_", "").replace(",", ".")
            feats = dict(x.split("=", 1) for x in c[5].split("|") if "=" in x)
            upos = c[3]
            pos = {"NOUN": "noun", "PROPN": "name", "ADJ": "adj", "VERB": "verb"}.get(upos, "other")
            if upos == "VERB" and feats.get("VerbForm") == "Part":
                pos = "adj"
            lemma = re.sub(r"\d+$", "", c[2])
            lemma = latin_lemma(lemma, c[1], c[10:])
            toks.append(Token("lat", lemma, c[1], f"{work} {cite}",
                              {"line": f"{work} {cite}", "sentence": f"{work}.{sent}", "book": work},
                              upos in LAT_CONTENT, pos, _LAT_CASE.get(feats.get("Case", "").split(",")[0]),
                              _LAT_NUM.get(feats.get("Number", "")), finite=feats.get("VerbForm") == "Fin"))
    return toks


LAT_LANGS = ("Latin", "Old Latin")
LAT_BRIDGE = ("Proto-Italic",)


def build_latin_mapping(lexicon: list[dict], tokens: list[Token]) -> Mapping:
    """Lexicon reflexes (Latin, Old Latin) by lat_key, then the lemma of a
    surface form equal to a reflex."""
    lemmas = latin_corpus_lemmas(tokens)
    surf = _surface_index(tokens, lat_key)
    cands = {t: collections.defaultdict(set) for t in ("direct", "surface")}
    for e in lexicon:
        for f in _reflex_forms(e, LAT_LANGS, roman=False):
            k = lat_key(f)
            cands["direct"][k].add(e["id"])
            if (lem := _majority(surf.get(k, collections.Counter()), k)):
                cands["surface"][lat_key(lem)].add(e["id"])
    return _finish(cands, lemmas, group_map(lexicon))


def apply_mapping(tokens: list[Token], m: Mapping, content_only: bool = True, level: str = "group") -> None:
    """Set each token's counting units: root groups (level='group') or
    lexicon entry ids (level='lexeme')."""
    src = m.lemma_groups if level == "group" else m.lemma_lex
    for t in tokens:
        t.roots = src.get(t.lemma, frozenset()) if (t.content or not content_only) else frozenset()


def coverage(tokens: list[Token], m: Mapping) -> dict:
    tiers = collections.Counter()
    for t in tokens:
        tiers[m.lemma_tier.get(t.lemma, "unmapped")] += 1
    content = [t for t in tokens if t.content]
    cm = sum(1 for t in content if t.lemma in m.lemma_groups)
    am = sum(1 for t in tokens if t.lemma in m.lemma_groups)
    lem = {t.lemma for t in tokens}
    return {"tokens": len(tokens), "tokens_mapped": am, "share": round(am / len(tokens), 4),
            "content_tokens": len(content), "content_mapped": cm, "content_share": round(cm / len(content), 4),
            "lemmas": len(lem), "lemmas_mapped": len(lem & set(m.lemma_groups)),
            "lemmas_ambiguous_dropped": len(m.ambiguous), "tokens_by_tier": dict(tiers),
            "root_groups": len({g for gs in m.lemma_groups.values() for g in gs})}


# ---------------------------------------------------------------- counting and scoring

@dataclass
class Counts:
    n: int                                   # units, or token pairs for windows
    single: collections.Counter
    pair: collections.Counter
    kind: str = "units"                      # "units" (presence per unit) or "pairs" (token pairs)


def _pairs_of(rootsets: list[frozenset]) -> set[tuple[str, str]]:
    """Unordered root pairs drawn from two different tokens of one unit."""
    out = set()
    nz = [r for r in rootsets if r]
    for a, b in itertools.combinations(nz, 2):
        for x in a:
            for y in b:
                if x != y:
                    out.add((x, y) if x < y else (y, x))
    return out


def count_units(units: list[list[frozenset]]) -> Counts:
    single, pair = collections.Counter(), collections.Counter()
    for u in units:
        single.update(set().union(*u) if u else set())
        pair.update(_pairs_of(u))
    return Counts(len(units), single, pair)


def count_windows(segments: list[list[frozenset]], k: int) -> Counts:
    """Token pairs at distance ≤ k inside a segment (hymn / book). n is the
    number of such token pairs; single[x] the pairs with x on either side."""
    n = 0
    single, pair = collections.Counter(), collections.Counter()
    for seg in segments:
        L = len(seg)
        n += sum(min(k, L - 1 - i) for i in range(L))
        for i, r in enumerate(seg):
            if not r:
                continue
            nb = min(k, L - 1 - i) + min(k, i)
            for x in r:
                single[x] += nb
            for j in range(i + 1, min(L, i + k + 1)):
                s = seg[j]
                if s:
                    for x in r:
                        for y in s:
                            if x != y:
                                pair[(x, y) if x < y else (y, x)] += 1
    return Counts(n, single, pair, "pairs")


def llr(o11: int, c1: int, c2: int, n: int) -> float:
    """Signed Dunning G² for the 2×2 table; negative when o11 < expected."""
    o = (o11, c1 - o11, c2 - o11, n - c1 - c2 + o11)
    e = (c1 * c2 / n, c1 * (n - c2) / n, (n - c1) * c2 / n, (n - c1) * (n - c2) / n)
    g = 2 * sum(a * math.log(a / b) for a, b in zip(o, e) if a > 0 and b > 0)
    return g if o11 >= e[0] else -g


def pmi(o11: int, c1: int, c2: int, n: int) -> float:
    return math.log2(o11 * n / (c1 * c2)) if o11 else float("-inf")


def npmi(o11: int, c1: int, c2: int, n: int) -> float:
    if not o11:
        return -1.0
    p = o11 / n
    return pmi(o11, c1, c2, n) / -math.log2(p) if p < 1 else 1.0


MEASURES = {"llr": llr, "pmi": pmi, "npmi": npmi}


def score_pairs(a: Counts, b: Counts, measure: str = "llr", min_count: int = 3, llr_min: float = 10.83,
                max_share: float = 1.0) -> list[dict]:
    """Pairs significant in both corpora, best first by the weaker score.
    max_share drops roots present in more than that share of units."""
    f = MEASURES[measure]
    out = []
    for p in a.pair.keys() & b.pair.keys():
        oa, ob = a.pair[p], b.pair[p]
        if oa < min_count or ob < min_count:
            continue
        x, y = p
        if max(a.single[x], a.single[y]) > max_share * a.n or max(b.single[x], b.single[y]) > max_share * b.n:
            continue
        ga, gb = llr(oa, a.single[x], a.single[y], a.n), llr(ob, b.single[x], b.single[y], b.n)
        if ga < llr_min or gb < llr_min:
            continue
        sa, sb = f(oa, a.single[x], a.single[y], a.n), f(ob, b.single[x], b.single[y], b.n)
        out.append({"pair": p, "score": min(sa, sb), "rv": {"n": oa, "llr": ga, measure: sa},
                    "hom": {"n": ob, "llr": gb, measure: sb}})
    out.sort(key=lambda r: (-r["score"], r["pair"]))
    return out


# ---------------------------------------------------------------- exact per-corpus tests (round 2)

def _lchoose(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _logsumexp(xs: list[float]) -> float:
    if not xs:
        return float("-inf")
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs)) if m > float("-inf") else m


def _log_tail(o: int, lo: int, hi: int, mean: float, lpmf, midp: bool) -> float:
    """log P(X ≥ o) (midp: P(X > o) + ½P(X = o)) for a discrete X on
    [lo, hi] with log-pmf lpmf; sums the short side of the distribution."""
    if o <= lo and not midp:
        return 0.0
    if o > hi:
        return float("-inf")
    if o > mean:
        terms, i = [], o
        while i <= hi:
            t = lpmf(i)
            if i == o and midp:
                t -= math.log(2)
            terms.append(t)
            if len(terms) > 3 and t < terms[0] - 40:
                break
            i += 1
        return min(0.0, _logsumexp(terms))
    below = [lpmf(i) for i in range(lo, o)]
    if midp:
        below.append(lpmf(o) - math.log(2))
    s = math.exp(_logsumexp(below)) if below else 0.0
    return math.log(max(1.0 - s, 1e-300))


def hypergeom_logsf(o: int, K: int, d: int, N: int, midp: bool = False) -> float:
    """log P(X ≥ o), X ~ Hypergeometric(N units, K containing x, d containing y):
    the chance that x and y share ≥ o units if y's units were drawn at random."""
    lo, hi = max(0, d + K - N), min(K, d)
    base = _lchoose(N, d)
    return _log_tail(o, lo, hi, K * d / N, lambda i: _lchoose(K, i) + _lchoose(N - K, d - i) - base, midp)


def poisson_logsf(o: int, lam: float, midp: bool = False) -> float:
    """log P(X ≥ o), X ~ Poisson(lam)."""
    if lam <= 0:
        return 0.0 if o <= 0 else float("-inf")
    hi = max(o, int(lam + 40 * math.sqrt(lam) + 50))
    return _log_tail(o, 0, hi, lam, lambda i: i * math.log(lam) - lam - math.lgamma(i + 1), midp)


def fisher_logp(logps: list[float]) -> float:
    """Fisher's method: log of the combined p-value of independent tests,
    X = −2 Σ ln p ~ χ²(2k); sf(X) = e^{−X/2} Σ_{j<k} (X/2)^j / j!."""
    k = len(logps)
    if not k:
        return 0.0
    h = -sum(logps)                       # X/2
    if h <= 0:
        return 0.0
    terms = [j * math.log(h) - math.lgamma(j + 1) for j in range(k)]
    return min(0.0, -h + _logsumexp(terms))


def pair_logp(c: Counts, p: tuple, midp: bool = False) -> float:
    """One corpus's exact one-sided log p for pair p: hypergeometric on unit
    presence, Poisson (λ = s_x s_y / 2n) on token-pair counts (windows, edges)."""
    x, y = p
    o = c.pair.get(p, 0)
    if c.kind == "pairs":
        return poisson_logsf(o, c.single[x] * c.single[y] / (2 * c.n), midp)
    return hypergeom_logsf(o, c.single[x], c.single[y], c.n, midp)


LOG10 = math.log(10)


def score_exact(corpora: list[Counts], min_count: int = 1, rank_by: str = "fisher", midp: bool = False,
                max_logp: float = 0.0, third: Counts | None = None, third_mode: str = "none",
                bonus: dict | None = None, keep=None, floor: float | None = None) -> list[dict]:
    """Pairs co-occurring ≥ min_count times in every corpus of `corpora`,
    ranked by Fisher's combined p (rank_by='fisher') or by the weaker
    corpus's p ('max'). max_logp: each corpus's log p must be ≤ this.
    third (a third corpus, e.g. Latin) per third_mode:
      none       ignored
      fisher3    a third Fisher term wherever both lexemes occur in it
                 (absent co-occurrence → p = 1, which costs the pair)
      fisher3pos a third term only where the pair co-occurs there
      require    the pair must co-occur there (filter), score unchanged
      tiebreak   ranking by the two-corpus score in 0.5-log10 bins, then
                 by the third corpus's p
    bonus: pair → log10 units subtracted from the score (syntax bonus);
    keep: optional predicate on pairs (syntax filter); floor: clip each
    corpus's log10 p at this value before combining (truncated Fisher, so
    one corpus's huge count cannot carry a pair alone)."""
    a = corpora[0]
    common = set(a.pair)
    for c in corpora[1:]:
        common &= c.pair.keys()
    out = []
    for p in common:
        if any(c.pair[p] < min_count for c in corpora) or (keep and not keep(p)):
            continue
        lps = [pair_logp(c, p, midp) for c in corpora]
        if max(lps) > max_logp:
            continue
        if floor is not None:
            lps = [max(lp, floor * LOG10) for lp in lps]
        rec = {"pair": p, "logp": lps, "n": [c.pair[p] for c in corpora]}
        third_lp = None
        if third is not None and third_mode != "none":
            x, y = p
            testable = third.single.get(x, 0) > 0 and third.single.get(y, 0) > 0
            o3 = third.pair.get(p, 0)
            if third_mode == "require" and o3 < 1:
                continue
            if testable:
                third_lp = pair_logp(third, p, midp)
                if floor is not None:
                    third_lp = max(third_lp, floor * LOG10)
                rec["third"] = {"n": o3, "logp": third_lp}
        if third_mode == "fisher3" and third_lp is not None:
            comb = fisher_logp(lps + [third_lp])
        elif third_mode == "fisher3pos" and third_lp is not None and rec["third"]["n"] >= 1:
            comb = fisher_logp(lps + [third_lp])
        else:
            comb = fisher_logp(lps)
        s = comb if rank_by == "fisher" else max(lps)
        if bonus:
            s -= bonus.get(p, 0.0) * LOG10
        rec["combined_logp"] = comb
        rec["score"] = -s / LOG10                      # higher is better: −log10 p
        rec["_tb"] = -(third_lp if third_lp is not None else 0.0)
        out.append(rec)
    if third_mode == "tiebreak":
        out.sort(key=lambda r: (-math.floor(r["score"] * 2), -r["_tb"], -r["score"], r["pair"]))
    else:
        out.sort(key=lambda r: (-r["score"], r["pair"]))
    return out


# ---------------------------------------------------------------- syntactic links (round 2)

def count_edges(tokens: list[Token], edges: list[tuple[int, int]]) -> Counts:
    """Counts over token pairs that are linked (dependency edges, or
    adjacency): n = number of links, single[x] = links with x on either end."""
    single, pair = collections.Counter(), collections.Counter()
    n = 0
    for i, j in edges:
        n += 1
        a, b = tokens[i].roots, tokens[j].roots
        for x in a:
            single[x] += 1
        for y in b:
            single[y] += 1
        for x in a:
            for y in b:
                if x != y:
                    pair[(x, y) if x < y else (y, x)] += 1
    return Counts(n, single, pair, "pairs")


def dep_edges(tokens: list[Token]) -> list[tuple[int, int]]:
    """Direct head–dependent links (Homer treebank)."""
    return [(i, t.head) for i, t in enumerate(tokens) if t.head is not None and t.head != i]


def adjacency_edges(tokens: list[Token], unit: str = "pada", k: int = 1, content_only: bool = True) -> list[tuple[int, int]]:
    """Token pairs at most k apart inside one unit (the RV proxy for syntax;
    with content_only, distance counts content words only, so a particle
    in between does not break adjacency)."""
    out = []
    by_unit: dict[str, list[int]] = collections.defaultdict(list)
    for i, t in enumerate(tokens):
        if t.content or not content_only:
            by_unit[t.units[unit]].append(i)
    for idx in by_unit.values():
        for a in range(len(idx)):
            for b in range(a + 1, min(len(idx), a + k + 1)):
                out.append((idx[a], idx[b]))
    return out


REL_MAP = {"verb+acc": "verb+obj", "verb+nom": "verb+subj", "gen+nom": "noun+gen", "agree": "adj+noun"}


def link_relation(a: Token, b: Token, a_idx: int, b_idx: int) -> str:
    """Relation type of two linked tokens, in one vocabulary for both corpora:
    adj+noun, verb+obj, verb+subj, noun+gen, other. Homer uses the treebank
    label of the dependent where the two are head and dependent; otherwise
    (and in the RV) morphology decides (relation())."""
    dep, head = (a, b) if a.head == b_idx else (b, a) if b.head == a_idx else (None, None)
    if dep is not None and dep.rel:
        r = dep.rel.split("_")[0]
        if r == "OBJ":
            return "verb+obj"
        if r == "SBJ":
            return "verb+subj"
        if r == "ATR":
            if dep.case == "GEN" and dep.pos == "noun":
                return "noun+gen"
            if dep.pos == "adj" or (dep.case and dep.case == head.case):
                return "adj+noun"
    return REL_MAP.get(relation(a, b), "other")


def edge_relations(tokens: list[Token], edges: list[tuple[int, int]]) -> dict:
    """pair → Counter of link_relation over its linked co-occurrences."""
    out: dict = collections.defaultdict(collections.Counter)
    for i, j in edges:
        a, b = tokens[i], tokens[j]
        if not a.roots or not b.roots:
            continue
        rel = None
        for x in a.roots:
            for y in b.roots:
                if x != y:
                    rel = rel or link_relation(a, b, i, j)
                    out[(x, y) if x < y else (y, x)][rel] += 1
    return out


def dominant_relation(c: collections.Counter | None) -> str | None:
    if not c:
        return None
    c = {k: v for k, v in c.items() if k != "other"}
    return max(sorted(c), key=c.get) if c else None


# ---------------------------------------------------------------- units

def rootsets_by(tokens: list[Token], unit: str) -> list[list[frozenset]]:
    groups: dict[str, list[frozenset]] = {}
    for t in tokens:
        groups.setdefault(t.units[unit], []).append(t.roots)
    return list(groups.values())


def corpus_counts(tokens: list[Token], spec: str) -> Counts:
    """spec: a unit name ('pada', 'stanza', 'line', 'sentence') or
    'win<k>' for ±k-word windows inside hymns (RV) / books (Homer)."""
    if spec.startswith("win"):
        seg = "hymn" if tokens[0].corpus == "rv" else "book"
        return count_windows(rootsets_by(tokens, seg), int(spec[3:]))
    return count_units(rootsets_by(tokens, spec))


def shuffled(tokens: list[Token], seed: int = 0) -> list[Token]:
    """Same unit structure, root sets permuted across all positions."""
    rs = [t.roots for t in tokens]
    random.Random(seed).shuffle(rs)
    out = []
    for t, r in zip(tokens, rs):
        c = Token(**{**t.__dict__})
        c.roots = r
        out.append(c)
    return out


# ---------------------------------------------------------------- evaluation set

VEDIC_ATT = re.compile(r"^(Vedic|Sanskrit|Rigvedic)")
GREEK_ATT = re.compile(r"^(Greek|Homeric|Epic Greek)")


def split_half(formula_id: str) -> str:
    return "A" if hashlib.sha1(formula_id.encode("utf-8")).digest()[0] % 2 == 0 else "B"


def _att_words(text: str) -> list[str]:
    text = re.sub(r"\.\s*\.\s*\.|…|\(.*?\)", " ", text)
    return [w for w in re.split(r"[\s|,;:.!?\"“”·]+", text) if w and not w.startswith("-")]


def _skt_variants(w: str) -> list[str]:
    k = skt_key(w)
    out = [k]
    if k.endswith("ḥ"):
        out += [k[:-1] + "s", k[:-1] + "r", k[:-1]]
    if k.endswith("ṃ"):
        out.append(k[:-1] + "m")
    if k.endswith("o"):
        out.append(k[:-1] + "as")
    if k.endswith(("s", "r")):
        out.append(k[:-1] + "ḥ")
    if k.endswith("m"):
        out.append(k[:-1] + "ṃ")
    return out


class Lemmatizer:
    """Maps attestation words to root groups through the corpora's own
    surface → lemma pairs, then the corpus lemma mapping; falls back to
    lemma keys and to lexicon reflex forms."""

    def __init__(self, rv: list[Token], hom: list[Token], rvm: Mapping, homm: Mapping, lexicon: list[dict],
                 extra_v: dict | None = None, extra_g: dict | None = None):
        self.extra_v, self.extra_g = extra_v or {}, extra_g or {}
        self.rv_surf = _surface_index(rv, skt_key)
        self.hom_surf = _surface_index(hom, lambda s: grc_key(s, accents=False))
        self.rv_lem = collections.defaultdict(set)
        for lem, g in rvm.lemma_groups.items():
            for k in skt_lemma_keys(lem):
                self.rv_lem[k] |= g
        self.hom_lem = collections.defaultdict(set)
        for lem, g in homm.lemma_groups.items():
            self.hom_lem[grc_key(lem, accents=False)] |= g
        self.rvm, self.homm = rvm, homm
        self.skt_lex, self.grc_lex = collections.defaultdict(set), collections.defaultdict(set)
        for e in lexicon:
            for f in _reflex_forms(e, SKT_LANGS, roman=True):
                self.skt_lex[skt_key(f)].add(group_of(e))
            for f in _reflex_forms(e, GRC_LANGS, roman=False):
                self.grc_lex[grc_key(f, accents=False)].add(group_of(e))

    def vedic(self, w: str) -> frozenset:
        for k in _skt_variants(w):
            if k in self.rv_surf:
                lem = self.rv_surf[k].most_common(1)[0][0]
                if lem in self.rvm.lemma_groups:
                    return self.rvm.lemma_groups[lem]
        for k in _skt_variants(w):
            g = self.rv_lem.get(k) or self.skt_lex.get(k) or self.extra_v.get(k)
            if g and len(g) <= MAX_GROUPS:
                return frozenset(g)
        return frozenset()

    def greek(self, w: str) -> frozenset:
        k = grc_key(w, accents=False)
        if k in self.hom_surf:
            lem = self.hom_surf[k].most_common(1)[0][0]
            if lem in self.homm.lemma_groups:
                return self.homm.lemma_groups[lem]
        g = self.hom_lem.get(k) or self.grc_lex.get(k) or self.extra_g.get(k)
        return frozenset(g) if g and len(g) <= MAX_GROUPS else frozenset()


def kaikki_word_groups(lang: str, lexicon: list[dict], pseudo: bool = False, root: Path = ROOT) -> dict:
    """Dictionary-word key → root groups from the kaikki links, for
    lemmatizing words the books cite from outside the corpora (Sanskrit:
    skt_key of the romanization; Greek: unaccented grc_key)."""
    links = load_kaikki_links(lang, root)
    idx = PieIndex(lexicon)
    res = resolve_kaikki(links, idx, lang, word_key_for(lang), pseudo)
    gmap = group_map(lexicon)
    out: dict[str, set] = collections.defaultdict(set)
    for r in links:
        hit = res.get(word_key_for(lang)(r["word"]))
        if not hit:
            continue
        k = skt_key(r["roman"]) if lang == "sa" and r.get("roman") else grc_key(r["word"], accents=False) \
            if lang == "grc" else None
        if k:
            out[k] |= {gmap.get(i, i) for i in hit[1]}
    return dict(out)


def pie_roots(text: str | None, lex_index: list[tuple[str, frozenset]]) -> list[frozenset]:
    """Root groups named in a formula's PIE wording, one slot per word: the
    groups of the longest lexicon form (≥ 4 chars, no accents/length) that
    is a prefix of the word."""
    out: list[frozenset] = []
    if not text:
        return out
    for w in re.split(r"[\s/…,;]+|\.\.\.", text):
        if not w or re.search(r"[A-Z]", w):
            continue
        k = pie_key(w)
        for form, groups in lex_index:
            if len(form) >= 4 and k.startswith(form):
                out.append(groups)
                break
    return out


def pie_index(lexicon: list[dict]) -> list[tuple[str, frozenset]]:
    idx: dict[str, set] = collections.defaultdict(set)
    for e in lexicon:
        if e.get("kind") in ("affix",):
            continue
        idx[pie_key(e["form"])].add(group_of(e))
    return sorted(((k, frozenset(v)) for k, v in idx.items()), key=lambda kv: -len(kv[0]))


def gold_set(formulas: list[dict], lem: Lemmatizer, lex_idx, kinds=("phrase", "lexical")) -> list[dict]:
    """Evaluation formulas: of the given kinds, attested in Vedic and Greek,
    with ≥ 2 identified PIE lexemes. Gold pairs are
      - `pie_pairs`: groups of two different words of the PIE wording
        (never two readings of one word), and
      - `attested_pairs`: groups found on two different words of one Vedic
        attestation and on two different words of one Greek attestation.
    A lone PIE word plus an attested group is not a pair: in West's
    "lexical" entries that is usually one lexeme seen twice."""
    out = []
    for f in formulas:
        if f["kind"] not in kinds:
            continue
        ved = [a for a in f["attestations"] if VEDIC_ATT.match(a["lang"])]
        grk = [a for a in f["attestations"] if GREEK_ATT.match(a["lang"])]
        if not ved or not grk:
            continue
        vsets = [[lem.vedic(w) for w in _att_words(a["text"])] for a in ved]
        gsets = [[lem.greek(w) for w in _att_words(a["text"])] for a in grk]
        V = set().union(*(s for ws in vsets for s in ws))
        G = set().union(*(s for ws in gsets for s in ws))
        P = pie_roots(f.get("pie") or f.get("pie_printed"), lex_idx)
        pp = set()
        for a, b in itertools.combinations(P, 2):
            for x in a:
                for y in b:
                    if x != y and not any(x in s and y in s for s in P):
                        pp.add((x, y) if x < y else (y, x))
        ap = set().union(*(_pairs_of(ws) for ws in vsets)) & set().union(*(_pairs_of(ws) for ws in gsets))
        pairs = pp | ap
        if not pairs:
            continue
        out.append({"formula_id": f["formula_id"], "half": split_half(f["formula_id"]), "kind": f["kind"],
                    "pairs": sorted(pairs), "pie_pairs": sorted(pp), "attested_pairs": sorted(ap),
                    "pie_groups": sorted(set().union(*P)), "vedic_groups": sorted(V), "greek_groups": sorted(G)})
    return out


def known_pairs(formulas: list[dict], lem: Lemmatizer, lex_idx) -> set:
    """Every pair any known formula names, for excluding them from new
    candidates: cross-word pairs of each PIE wording (all kinds, whatever
    the attestations) plus the gold pairs of every Vedic+Greek formula."""
    out = set()
    for f in formulas:
        P = pie_roots(f.get("pie") or f.get("pie_printed"), lex_idx)
        for a, b in itertools.combinations(P, 2):
            out |= {(x, y) if x < y else (y, x) for x in a for y in b if x != y}
    kinds = {f["kind"] for f in formulas}
    for g in gold_set(formulas, lem, lex_idx, tuple(kinds)):
        out |= set(g["pairs"])
    return out


def recall(ranking: list[dict], gold: list[dict], ks=(50, 100, 200)) -> dict:
    rank = {r["pair"]: i + 1 for i, r in enumerate(ranking)}
    ranks = {g["formula_id"]: min((rank[p] for p in g["pairs"] if p in rank), default=None) for g in gold}
    n = len(gold)
    return {"n": n, **{f"recall@{k}": round(sum(1 for r in ranks.values() if r and r <= k) / n, 3) if n else None
                       for k in ks}, "ranks": ranks}


# ---------------------------------------------------------------- silver evaluation set (West / Watkins co-citations)

WEST_TEXT = "raw/books/text/west"
WATKINS_TEXT = "raw/books/text/watkins"
_WORD = re.compile(r"[^\W\d_](?:[\ẁ-ͯ’'ʼ᾽]*[\ẁ-ͯ])?")
_GREEK_CH = re.compile(r"[Ͱ-Ͽἀ-῿]")
_LATIN_CH = re.compile(r"[a-z]", re.I)
_SKT_MARKS = set("̣̥̄́̀̃̇")   # macron, dot below, acute, grave, ring, tilde, dot above
_SKT_LETTERS = set("śṣ")


def is_vedic_like(w: str) -> bool:
    """A Latin-script word with an IAST/ISO mark (ā ṛ ṣ ś ṃ ḥ ñ ṅ, or a
    written accent), as West cites Vedic. Untouched English never qualifies."""
    if _GREEK_CH.search(w) or not _LATIN_CH.search(w):
        return False
    d = unicodedata.normalize("NFD", w)
    return any(c in _SKT_MARKS for c in d) or any(c in _SKT_LETTERS for c in w)


def passage_tokens(text: str) -> list[tuple[int, str, str]]:
    """(char offset, word, script) with script 'grc', 'skt' (Vedic-like
    Latin) or 'lat' (plain Latin script)."""
    out = []
    for m in _WORD.finditer(unicodedata.normalize("NFC", text)):
        w = m[0].strip("’'ʼ᾽")
        if not w:
            continue
        script = "grc" if _GREEK_CH.search(w) else "skt" if is_vedic_like(w) else "lat"
        out.append((m.start(), w, script))
    return out


def cited_groups(text: str, vedic, greek, ascii_vedic=None, ascii_greek=None) -> list[tuple[int, str, frozenset]]:
    """(offset, 'v'|'g', groups) for each cited word that maps. ascii_* are
    optional lookups for plain-Latin words (Watkins's OCR has no diacritics
    and no Greek script)."""
    out = []
    for off, w, script in passage_tokens(text):
        g, side = frozenset(), None
        if script == "grc":
            g, side = greek(w), "g"
        elif script == "skt":
            g, side = vedic(w), "v"
        elif ascii_vedic or ascii_greek:
            if ascii_vedic and (g := ascii_vedic(w)):
                side = "v"
            elif ascii_greek and (g := ascii_greek(w)):
                side = "g"
        if g and side:
            out.append((off, side, g))
    return out


def silver_pairs_in(cited: list[tuple[int, str, frozenset]], phrase: int = 60, span: int = 400) -> set:
    """Pairs (x, y) of PIE groups for which the passage cites a Vedic phrase
    (two words ≤ `phrase` chars apart, one for x and one for y) and a Greek
    phrase likewise, the two phrases ≤ `span` chars apart."""
    def phrases(side):
        ws = [(o, g) for o, s, g in cited if s == side]
        out = collections.defaultdict(list)
        for (o1, g1), (o2, g2) in itertools.combinations(ws, 2):
            if abs(o2 - o1) > phrase:
                continue
            for x in g1:
                for y in g2:
                    if x != y and not (x in g2 and y in g1 and len(g1) == len(g2) == 1):
                        out[(x, y) if x < y else (y, x)].append((o1 + o2) / 2)
        return out
    pv, pg = phrases("v"), phrases("g")
    return {p for p in pv.keys() & pg.keys() if any(abs(a - b) <= span for a in pv[p] for b in pg[p])}


def co_mentions(cited: list[tuple[int, str, frozenset]]) -> set:
    """All group pairs cited anywhere in one passage (any side), for the
    'West/Watkins mention this pair' flag on candidates."""
    gs = [g for _, _, g in cited]
    return _pairs_of(gs)


def west_passages(root: Path = ROOT) -> list[tuple[dict, str]]:
    """(ref, paragraph text) for West's chapters (EPUB, one paragraph per
    line). Text stays in memory; only refs are stored."""
    out = []
    for fn in sorted((root / WEST_TEXT).glob("*.txt")):
        if not re.match(r"\d+_(ch\d+|introduction|elegy)", fn.stem):
            continue
        for i, para in enumerate(fn.read_text("utf-8").splitlines(), 1):
            if para.strip():
                out.append(({"book": "west", "file": fn.stem, "para": i}, para))
    return out


def watkins_passages(root: Path = ROOT) -> list[tuple[dict, str]]:
    """(ref, page text) for Watkins's PDF text layer, one PDF page each,
    the index pages excluded."""
    out = []
    for fn in sorted((root / WATKINS_TEXT).glob("p*.txt")):
        t = fn.read_text("utf-8")
        out.append(({"book": "watkins", "pdf_page": int(fn.stem[1:])}, t))
    return out


def ascii_fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def ascii_lookup(pairs, stop: set, min_len: int = 4):
    """A plain-ASCII word → groups lookup from (form, groups) pairs, keeping
    only keys of ≥ min_len that are not English words and map to one group set."""
    idx: dict[str, set] = collections.defaultdict(set)
    for form, g in pairs:
        k = ascii_fold(form)
        if len(k) >= min_len and k.isalpha() and k not in stop:
            idx[k].add(frozenset(g))
    uniq = {k: next(iter(v)) for k, v in idx.items() if len(v) == 1}
    return lambda w: uniq.get(ascii_fold(w), frozenset())


def build_silver(passages: list[tuple[dict, str]], vedic, greek, ascii_vedic=None, ascii_greek=None,
                 phrase: int = 60, span: int = 400) -> tuple[dict, dict]:
    """silver: pair → refs (phrase-level co-citations); mentions: pair → refs
    (any co-citation in one passage)."""
    silver, mentions = collections.defaultdict(list), collections.defaultdict(list)
    for ref, text in passages:
        c = cited_groups(text, vedic, greek, ascii_vedic, ascii_greek)
        if len(c) < 2:
            continue
        for p in silver_pairs_in(c, phrase, span):
            silver[p].append(ref)
        for p in co_mentions(c):
            mentions[p].append(ref)
    return dict(silver), dict(mentions)


def eval_items(gold: list[dict], silver: dict) -> list[dict]:
    """Evaluation items: each gold formula (its pair set) and each silver
    pair, merged when they share a pair (union-find), so one PIE pair never
    sits in two folds. fold = sha1 of the item's smallest pair mod 5."""
    items = [{"pairs": set(map(tuple, g["pairs"])), "gold": [g["formula_id"]], "silver": False} for g in gold]
    items += [{"pairs": {p}, "gold": [], "silver": True} for p in silver]
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owner: dict = {}
    for i, it in enumerate(items):
        for p in it["pairs"]:
            if p in owner:
                parent[find(i)] = find(owner[p])
            else:
                owner[p] = i
    merged: dict[int, dict] = {}
    for i, it in enumerate(items):
        r = merged.setdefault(find(i), {"pairs": set(), "gold": [], "silver": False})
        r["pairs"] |= it["pairs"]
        r["gold"] += it["gold"]
        r["silver"] = r["silver"] or it["silver"]
    out = []
    for r in merged.values():
        ps = sorted(r["pairs"])
        key = "|".join(ps[0])
        out.append({"item_id": key, "pairs": ps, "gold": sorted(r["gold"]), "silver": r["silver"],
                    "fold": fold_of(key)})
    return sorted(out, key=lambda r: r["item_id"])


def fold_of(key: str, k: int = 5) -> int:
    return int.from_bytes(hashlib.sha1(key.encode("utf-8")).digest()[:4], "big") % k


def item_ranks(ranking: list[dict], items: list[dict], project=None) -> list[int | None]:
    """Best rank of any of an item's pairs. `project` maps a ranked pair to
    the group pair it stands for (lexeme-level scoring); ranks then count
    distinct group pairs."""
    rank: dict = {}
    n = 0
    for r in ranking:
        p = project(r["pair"]) if project else r["pair"]
        if p is None or p in rank:
            continue
        n += 1
        rank[p] = n
    return [min((rank[p] for p in it["pairs"] if p in rank), default=None) for it in items]


def recall_at(ranks: list[int | None], ks=(50, 100, 200)) -> dict:
    n = len(ranks)
    return {f"recall@{k}": (sum(1 for r in ranks if r and r <= k) / n if n else None) for k in ks}


def bootstrap_ci(ranks: list[int | None], ks=(50, 100, 200), b: int = 2000, seed: int = 0) -> dict:
    """Percentile 95% CI for recall@k, resampling items with replacement."""
    rng = random.Random(seed)
    n = len(ranks)
    out = {}
    hits = {k: [1 if r and r <= k else 0 for r in ranks] for k in ks}
    for k in ks:
        if not n:
            out[f"recall@{k}"] = None
            continue
        h = hits[k]
        stats = sorted(sum(h[rng.randrange(n)] for _ in range(n)) / n for _ in range(b))
        out[f"recall@{k}"] = [round(stats[int(0.025 * b)], 3), round(stats[int(0.975 * b) - 1], 3)]
    return out


def paired_bootstrap_diff(ranks_a: list, ranks_b: list, k: int, b: int = 2000, seed: int = 0) -> dict:
    """recall@k(a) − recall@k(b) on the same items, with a paired percentile
    95% CI (items resampled together)."""
    n = len(ranks_a)
    if not n:
        return {"diff": None, "ci95": None}
    d = [(1 if ra and ra <= k else 0) - (1 if rb and rb <= k else 0) for ra, rb in zip(ranks_a, ranks_b)]
    rng = random.Random(seed)
    stats = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(b))
    return {"diff": round(sum(d) / n, 3), "ci95": [round(stats[int(0.025 * b)], 3), round(stats[int(0.975 * b) - 1], 3)]}


# ---------------------------------------------------------------- syntactic relation of a co-occurrence

def relation(a: Token, b: Token) -> str:
    """Coarse morphological relation of two co-occurring tokens, comparable
    across the corpora: verb+acc, verb+nom, agree (same case and number),
    gen+nom (one genitive dependent), other."""
    for v, n in ((a, b), (b, a)):
        if v.pos == "verb" and n.pos in ("noun", "adj") and n.case:
            if n.case == "ACC":
                return "verb+acc"
            if n.case == "NOM" and v.finite:
                return "verb+nom"
    if a.case and b.case and a.pos in ("noun", "adj") and b.pos in ("noun", "adj"):
        if a.case == b.case and a.number == b.number:
            return "agree"
        if "GEN" in (a.case, b.case):
            return "gen+nom"
    return "other"


def instances(tokens: list[Token], spec: str, pairs: set, limit: int = 6) -> dict:
    """For each pair: up to `limit` example (locus, lemma, lemma, relation,
    dep) and a relation tally over all co-occurrences under `spec`."""
    out = {p: {"examples": [], "relations": collections.Counter(), "dep_linked": 0} for p in pairs}
    want = {x for p in pairs for x in p}

    def visit(i: int, j: int):
        a, b = tokens[i], tokens[j]
        for x in a.roots & want:
            for y in b.roots & want:
                p = (x, y) if x < y else (y, x)
                if x == y or p not in out:
                    continue
                o = out[p]
                rel = relation(a, b)
                dep = a.head == j or b.head == i
                o["relations"][rel] += 1
                o["dep_linked"] += dep
                if len(o["examples"]) < limit:
                    loc = a.locus if a.locus == b.locus else f"{a.locus}–{b.locus.split(' ')[-1]}"
                    first, second = (a, b) if x < y else (b, a)
                    ex = {"locus": loc, "lemmas": [first.lemma, second.lemma], "pos": [first.pos, second.pos],
                          "relation": rel}
                    if a.corpus == "hom":
                        ex["dep"] = (b.rel if b.head == i else a.rel if a.head == j else None)
                    o["examples"].append(ex)

    idx = [i for i, t in enumerate(tokens) if t.roots & want]
    if spec.startswith("win"):
        k = int(spec[3:])
        seg = "hymn" if tokens[0].corpus == "rv" else "book"
        for n, i in enumerate(idx):
            for j in idx[n + 1:]:
                if j - i > k or tokens[j].units[seg] != tokens[i].units[seg]:
                    break
                visit(i, j)
    else:
        by_unit: dict[str, list[int]] = collections.defaultdict(list)
        for i in idx:
            by_unit[tokens[i].units[spec]].append(i)
        for us in by_unit.values():
            for i, j in itertools.combinations(us, 2):
                visit(i, j)
    return out


def parallel_relation(rv_rel: collections.Counter, hom_rel: collections.Counter, min_n: int = 2) -> str | None:
    """The shared dominant non-'other' relation, if each corpus has it ≥ min_n times."""
    def top(c):
        c = {k: v for k, v in c.items() if k != "other" and v >= min_n}
        return max(c, key=c.get) if c else None
    t = top(rv_rel)
    return t if t and t == top(hom_rel) else None


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text("utf-8").splitlines() if l.strip()]
