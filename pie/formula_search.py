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
                work = HOMER_WORKS.get(work.split(".")[-1], work)
                book = line.split(".")[0]
                pos = {"n": "noun", "a": "adj", "v": "verb"}.get(tag[0], "other")
                finite = tag[0] == "v" and tag[4] in "isom"
                if tag[0] == "v" and tag[4] == "p":
                    pos = "adj"      # participles agree like adjectives
                local[a.get("id", "")] = len(toks)
                heads.append((len(toks), a.get("head", "")))
                toks.append(Token("hom", a["lemma"], a.get("form", ""), f"{work} {line}",
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


def _finish(cands: dict[str, dict[str, set]], lemmas: dict[str, list[str]]) -> Mapping:
    """cands: tier → lemma-key → groups, in priority order; lemmas: corpus
    lemma → its keys."""
    m = Mapping()
    for lemma, keys in lemmas.items():
        for tier in cands:
            g = set().union(*(cands[tier].get(k, set()) for k in keys)) if keys else set()
            if g:
                if len(g) > MAX_GROUPS:
                    m.ambiguous.add(lemma)
                else:
                    m.lemma_groups[lemma] = frozenset(g)
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
    for lem, g in m.lemma_groups.items():
        for k in lemmas.get(lem, []):
            by_key[k] |= g
    for lem, keys in lemmas.items():
        if lem in m.lemma_groups or lem in m.ambiguous:
            continue
        for k in keys:
            hit = next((by_key[b] for b in bases(k) if b in by_key), None)
            if hit:
                m.lemma_groups[lem] = frozenset(hit)
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
        g = group_of(e)
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
    m = _finish(cands, lemmas)
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
        g = group_of(e)
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
    m = _finish(cands, lemmas)
    _add_privatives(m, {lem: [grc_key(lem, accents=False)] for lem in lemmas}, grc_privative)
    return m


def apply_mapping(tokens: list[Token], m: Mapping, content_only: bool = True) -> None:
    for t in tokens:
        t.roots = m.lemma_groups.get(t.lemma, frozenset()) if (t.content or not content_only) else frozenset()


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
    return Counts(n, single, pair)


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

    def __init__(self, rv: list[Token], hom: list[Token], rvm: Mapping, homm: Mapping, lexicon: list[dict]):
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
            g = self.rv_lem.get(k) or self.skt_lex.get(k)
            if g and len(g) <= MAX_GROUPS:
                return frozenset(g)
        return frozenset()

    def greek(self, w: str) -> frozenset:
        k = grc_key(w, accents=False)
        if k in self.hom_surf:
            lem = self.hom_surf[k].most_common(1)[0][0]
            if lem in self.homm.lemma_groups:
                return self.homm.lemma_groups[lem]
        g = self.hom_lem.get(k) or self.grc_lex.get(k)
        return frozenset(g) if g and len(g) <= MAX_GROUPS else frozenset()


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
