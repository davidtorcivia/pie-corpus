"""Tier 2 secure check: does a cited daughter word continue a given PIE lexeme?

Used by scripts/build_tier2.py. For one lexeme and the cited `cognate_refs` of a
projection plan, each *parallel* ref is tested word by word (its `lemmas` and its
`words`) and gets a level:

  exact  the word reaches the lexeme itself
  root   it reaches only the lexeme's root, or a sibling formation of the same root
  none   neither

Two kinds of evidence, best level wins:

(a) Mapping tables: daughter word → lexicon ids, from the Phase 8a pipeline
    (pie/formula_search_multi.py, docs/research/8a-round3.md):
    - the round-3 corpus tables, data/research/formulas/mapping/<corpus>.jsonl;
    - the round-2 kaikki Sanskrit / Greek / Latin links,
      data/research/formulas/kaikki_links/<lang>.jsonl, resolved with
      pie.formula_search.resolve_kaikki;
    - the round-3 dictionary mapping (build_lang_mapping over the kaikki dumps)
      for the languages it covers, because the corpus tables only hold words that
      occur in their corpora (Hitt. ēšḫar, OIr. gonaid are missing from them).
    A word the table reaches only through a derivation (base chain, privative,
    kaikki-chain) is a different formation: root level.
(b) The lexicon's reflex lists (and the Indo-Iranian / Hellenic proto-forms bridged
    to Vedic / Greek keys): whole-word equality of the normalized forms. A cited
    lemma must equal a reflex (the reflex's declared ending may be stripped, since
    citation conventions differ: Hitt. kuenzi / kuen-); a cited inflected word is
    compared stem to stem, after stripping one ending from the declared list of
    its language (ENDINGS) on both sides. Never a prefix match. Reflexes marked
    uncertain or borrowed are skipped. Forms the tables map to the lexeme count as
    reflexes too ("table form").

Compounds ("compound:<type>:<first>+<second>"): a cited word counts for a branch
when it begins with a reflex of the first member (closed prefixes: PREFIX_REFLEXES)
and its remainder matches the second member as above; the compound is exact in a
branch only if both members are exact in that same word. Each member's branches
are recorded under "members".
"""

from __future__ import annotations

import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAPPING_DIR = ROOT / "data" / "research" / "formulas" / "mapping"

# ---------------------------------------------------------------- languages

# ref language → mapping code (None: lexicon reflexes only)
LANG_CODE = {
    "Vedic": "sa", "Sanskrit": "sa", "Sanskrit (Epic)": "sa",
    "Greek": "grc", "Homeric Greek": "grc",
    "Latin": "la", "Umbrian": "xum", "Oscan": "xum",
    "Avestan": "ae", "Old Avestan": "ae", "Young Avestan": "ae",
    "Hittite": "hit", "Old Irish": "sga", "Middle Irish": "sga",
    "Old Norse": "non", "Old Icelandic": "non", "Old English": "ang", "Gothic": "got",
    "Old Church Slavonic": "cu", "Old Russian": "cu", "Latvian": "lv", "Armenian": "xcl", "Old Armenian": "xcl",
}
# corpus table → code
CORPUS_CODE = {"av": "sa", "grp": "grc", "xum": "xum", "ae": "ae", "hit": "hit", "sga": "sga", "non": "non",
               "ang": "ang", "got": "got", "cu": "cu", "lv": "lv", "xcl": "xcl"}
DICT_CODES = ("non", "ang", "got", "sga", "cu", "lv", "xcl", "hit", "xum", "ae")
# ref language → lexicon reflex language names (besides the exact name)
LEX_NAMES = {
    "sa": ("Sanskrit", "Vedic Sanskrit"), "grc": ("Ancient Greek", "Epic Greek", "Homeric Greek", "Ionic Greek",
                                                  "Attic Greek", "Mycenaean Greek"),
    "ae": ("Avestan", "Old Avestan", "Younger Avestan"), "non": ("Old Norse", "Old Icelandic", "Old West Norse"),
    "cu": ("Old Church Slavonic", "Old East Slavic", "Old Russian"), "xcl": ("Old Armenian",),
    "hit": ("Hittite",), "sga": ("Old Irish",), "ang": ("Old English",), "got": ("Gothic",), "lv": ("Latvian",),
    "la": ("Latin", "Old Latin"), "xum": ("Umbrian",),
}
EXTRA_LEX_NAMES = {"Welsh": ("Welsh", "Middle Welsh", "Old Welsh"), "Luwian": ("Luwian", "Cuneiform Luwian",
                   "Hieroglyphic Luwian"), "Lithuanian": ("Lithuanian",), "Old High German": ("Old High German",)}
BRIDGES = {"sa": ("Proto-Indo-Iranian", "Proto-Indo-Aryan"), "grc": ("Proto-Hellenic",)}
# near-identical proto-forms compared as written (accents, ˀ and asterisks off): PBSl. *duktḗ = Lith. duktė,
# PItal. *sōl = Lat. sōl
LIGHT_BRIDGES = {"Lithuanian": ("Proto-Balto-Slavic", "Proto-Baltic"), "Latvian": ("Proto-Balto-Slavic", "Proto-Baltic"),
                 "Latin": ("Proto-Italic",), "Umbrian": ("Proto-Italic",), "Oscan": ("Proto-Italic",)}
# preverbs a cited Greek / Vedic word may carry before the reflex (πρόσφατος: -φατος = *gʷʰn̥tós), key space
PREVERBS = {"grc": ["pros", "pro", "kata", "kat", "apo", "ap", "epi", "ep", "ana", "en", "ek", "ex", "para",
                    "peri", "upo", "uper", "sun", "dia", "meta", "amphi", "anti"],
            "sa": ["prati", "pari", "abhi", "adhi", "anu", "apa", "ava", "upa", "pra", "sam", "nis", "nir", "ud",
                   "ut", "ni", "vi", "ā"]}

BRANCH = {"II": ("Sanskrit", "Vedic", "Avestan", "Persian", "Indo-Aryan", "Iranian", "Pali"),
          "Gk": ("Greek", "Hellenic", "Mycenaean"), "It": ("Latin", "Italic", "Oscan", "Umbrian"),
          "Ce": ("Irish", "Welsh", "Celtic", "Gaulish", "Breton"),
          "Gm": ("Germanic", "Gothic", "Norse", "English", "German", "Saxon", "Icelandic"),
          "BS": ("Slavic", "Slavonic", "Lithuanian", "Latvian", "Prussian", "Russian", "Baltic"),
          "An": ("Hittite", "Luwian", "Anatolian", "Palaic", "Lycian"), "Arm": ("Armenian",),
          "To": ("Tocharian",), "Alb": ("Albanian",)}


def branch_of(lang: str) -> str:
    return next((b for b, keys in BRANCH.items() if any(k in lang for k in keys)), lang)


# ---------------------------------------------------------------- keys

def _strip(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


_LAT2CYR = [("šč", "щ"), ("ch", "х"), ("št", "щ"), ("ja", "ꙗ"), ("ju", "ю"), ("a", "а"), ("b", "б"), ("v", "в"),
            ("g", "г"), ("d", "д"), ("e", "е"), ("ě", "ѣ"), ("ž", "ж"), ("z", "з"), ("i", "и"), ("j", "и"),
            ("k", "к"), ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"), ("r", "р"), ("s", "с"),
            ("t", "т"), ("u", "оу"), ("f", "ф"), ("x", "х"), ("c", "ц"), ("č", "ч"), ("š", "ш"), ("ъ", "ъ"),
            ("y", "ꙑ"), ("ь", "ь"), ("ę", "ѧ"), ("ǫ", "ѫ")]


def _cu_latin(s: str) -> str:
    """Scholarly Latin transliteration of OCS / Old Russian → Cyrillic (iskati → искати)."""
    s = unicodedata.normalize("NFC", s.lower())
    out, i = [], 0
    while i < len(s):
        for a, b in _LAT2CYR:
            if s.startswith(a, i):
                out.append(b)
                i += len(a)
                break
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def key(code: str | None, s: str) -> str:
    """Comparison key of a daughter word in one language. Keys keep vowel length
    where the script or transliteration writes it (Greek η/ω, Vedic ā)."""
    from . import formula_search as fs
    from . import formula_search_multi as fm
    s = (s or "").strip().strip("*-√").strip()
    if code == "sa":
        return fs.skt_key(s)
    if code == "grc":
        return fs.grc_roman(s)
    if code == "la":
        return fs.lat_key(s)
    if code == "xum":
        return fm.key_xum(s.replace("v", "u").replace("V", "u"))
    if code == "cu":
        if re.search(r"[a-zěščžęǫ]", s.lower()) and not re.search(r"[а-яѣѧѫ]", s.lower()):
            s = _cu_latin(s)
        return fm.key_cu(s)
    if code == "hit":
        return fm.key_hit(s)
    if code in fm.KEYS:
        return fm.KEYS[code](s)
    s = _strip(s.lower()).replace("ḫ", "h")
    return re.sub(r"[^a-zþðæ]", "", s)


def table_key(code: str, s: str) -> str:
    """Key used to join with the mapping tables (Greek in Greek script, accent-free)."""
    from . import formula_search as fs
    if code == "grc":
        return fs.grc_key(s or "", accents=False)
    return key(code, s)


# declared endings per language, in key space (stripped once, from the end, leaving >= 3 letters)
ENDINGS = {
    "sa": ["ebhyaḥ", "ebhiḥ", "ābhyām", "ābhiḥ", "ibhiḥ", "ubhiḥ", "ānām", "īnām", "ūnām", "asya", "āyāḥ",
           "āyām", "āyai", "eṣu", "iṣu", "uṣu", "āsu", "aiḥ", "āni", "ena", "āya", "āt", "aḥ", "am", "āḥ", "ān",
           "ām", "au", "ayaḥ", "avaḥ", "iḥ", "uḥ", "im", "um", "īḥ", "ī", "ā", "e", "ḥ", "m", "s",
           # verbal, thematic and middle only (śáye, śáyate, śayadhve → śay-). No bare -ti/-ta/-tu/-si/-mi:
           # they collide with nominal suffixes (ákṣiti- vs ákṣita-)
           "adhve", "ante", "anti", "antu", "ate", "ati", "atu", "ase", "asi", "āmi", "āmahe", "ethe",
           "dhve", "mahe"],
    "grc": ["oisi", "ēisi", "ēphi", "oio", "ois", "ous", "ēos", "eos", "eus", "ais", "ēsi", "essi", "si", "os",
            "on", "ou", "oi", "ōn", "ōs", "ō", "as", "an", "ai", "ēs", "ēn", "ē", "es", "ei", "ea", "is", "in",
            "us", "un", "a", "e", "i", "s",
            # verbal, middle and thematic only (κεῖμαι, κεῖσαι, κεῖται → kei-); no bare -mi/-si/-ti/-to
            "ntai", "metha", "sthe", "mai", "sai", "tai", "nto", "eis", "omen", "ete", "ousi", "ein"],
    "la": ["ibus", "orum", "arum", "ium", "ius", "um", "us", "is", "os", "as", "es", "em", "am", "im", "ae",
           "ui", "o", "a", "e", "i", "u", "s", "m"],
    "xum": ["om", "um", "es", "er", "o", "u", "e", "i", "a", "f", "s", "m"],
    "hit": ["anza", "anta", "anzi", "ant", "an", "as", "is", "us", "es", "ar", "za", "zi", "ti", "ta", "ni",
            "a", "i", "e", "u", "s"],
    "sga": ["aib", "ib", "ae", "e", "a", "i", "u"],
    "non": ["anna", "inn", "ar", "ir", "ur", "um", "an", "a", "i", "u", "r", "s"],
    "ang": ["ena", "um", "as", "an", "es", "a", "e", "u", "o"],
    "got": ["ans", "ins", "ons", "os", "is", "us", "ai", "au", "a", "s"],
    "cu": ["оу", "омь", "ами", "ахъ", "ъ", "ь", "а", "ѧ", "ꙑ", "и", "е", "ѣ", "о", "ѫ", "ти"],
    "lv": ["ām", "iem", "ēm", "as", "is", "us", "es", "ai", "a", "e", "i", "u", "s", "š"],
    "xcl": ["ov", "aw", "ac", "ic", "s", "k", "n", "d", "i", "u", "a"],
    None: ["as", "is", "us", "ys", "ai", "ui", "a", "e", "i", "o", "u", "s", "ė", "ą", "ų"],
}


def _ae_endings():
    from .formula_search_multi import AE_ENDINGS, key_ae
    return sorted({key_ae(e) for e in AE_ENDINGS if e and "." not in e}, key=len, reverse=True)


def stems(code: str | None, k: str) -> set[str]:
    """k and k minus one declared ending (>= 3 letters left)."""
    ends = _ae_endings() if code == "ae" else ENDINGS.get(code, ENDINGS[None])
    out = {k}
    for e in ends:
        if e and k.endswith(e) and len(k) - len(e) >= 3:
            out.add(k[: -len(e)])
    return out


# closed first members of compounds: daughter prefixes in key space (pie/compound.py PREFIXES;
# Fortson §6.86, §7.25, Ringe 2.4.1: Ved. su-, dus-, a(n)-; Gk εὐ-, δυσ-, ἀ(ν)-; Av. hu-; OIr. so-/su-)
PREFIX_REFLEXES = {
    "closed:prefix/h1su": {"sa": ["su", "sv", "sū"], "ae": ["hu", "hv", "hao", "huu"], "grc": ["eu"],
                           "sga": ["so", "su"], "cu": ["съ"]},
    "closed:prefix/dus": {"sa": ["dus", "duṣ", "dur", "duḥ", "duś", "dū"], "ae": ["duš", "duž"], "grc": ["dus"],
                          "sga": ["do", "du"]},
    "closed:prefix/n": {"sa": ["an", "a"], "ae": ["an", "a"], "grc": ["an", "a"], "la": ["in", "im", "i"],
                        "ang": ["un"], "got": ["un"], "non": ["ó", "u"], "sga": ["an", "in", "é", "am"]},
    "closed:prefix/sm": {"sa": ["sa"], "grc": ["a", "o"]},
    "closed:numerals/2": {"sa": ["dvi"], "grc": ["di"], "la": ["bi"], "ang": ["twi"]},
    "closed:numerals/3": {"sa": ["tri"], "grc": ["tri"], "la": ["tri"]},
    "closed:numerals/4": {"sa": ["catur", "catuṣ"], "grc": ["tetra"], "la": ["quadru"]},
}
PREFIX_ALIASES = {"pie-lex-h1su": "closed:prefix/h1su", "pie-lex-dus": "closed:prefix/dus",
                  "pie-lex-n": "closed:prefix/n"}

DERIVED_MARKS = ("base:", "r2-tier:kaikki-chain", "r2-tier:privative", "kaikki-chain", "privative")


# ---------------------------------------------------------------- tables

def _rec(ids, path, source, derived=False):
    return (frozenset(ids), tuple(path), source, bool(derived))


def load_corpus_tables(codes=None) -> dict:
    """data/research/formulas/mapping/*.jsonl → {code: {key: [rec]}}."""
    from .formula_search_multi import hit_tlh_keys
    out: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    for corpus, code in CORPUS_CODE.items():
        if codes is not None and code not in codes:
            continue
        p = MAPPING_DIR / f"{corpus}.jsonl"
        if not p.exists():
            continue
        for line in p.read_text("utf-8").splitlines():
            r = json.loads(line)
            derived = r.get("how") in ("base", "root") or any(
                str(x).startswith(DERIVED_MARKS) for x in r.get("path", []))
            rec = _rec(r["lex_id"], [f"table:{corpus}"] + list(r.get("path", [])), f"table:{corpus}", derived)
            keys = set()
            for part in str(r.get("lemma", "")).split("|"):
                if code == "hit":
                    keys |= set(hit_tlh_keys(part.split("@")[0]))
                else:
                    keys.add(table_key(code, part))
            for part in re.split(r"\s*[|~]\s*", str(r.get("word", ""))):    # RV lemmas: "gáv- ~ gó-"
                keys.add(table_key(code, part))
            for k in keys:
                if k:
                    out[code][k].append(rec)
    return out


def load_kaikki_tables(entries: dict, codes=("sa", "grc", "la")) -> dict:
    """Round-2 kaikki links (cached in data/research/formulas/kaikki_links) → {code: {key: [rec]}}."""
    from . import formula_search as fs
    lex = list(entries.values())
    idx = fs.PieIndex(lex)
    out: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    for code in codes:
        links = fs.load_kaikki_links(code)
        resolved = fs.resolve_kaikki(links, idx, code, fs.word_key_for(code), pseudo=False)
        wk = fs.word_key_for(code)
        for r in links:
            hit = resolved.get(wk(r["word"]))
            if not hit:
                continue
            tier, ids = hit
            rec = _rec(ids, [f"kaikki-{code}:{r['word']}", f"r2-tier:{tier}"], f"kaikki:{code}",
                       tier in ("kaikki-chain", "kaikki-root"))
            if code == "sa":
                if not r.get("roman"):
                    continue
                k = fs.skt_key(r["roman"])
                keys = [k] + (fs.skt_root_candidates(k)[:3] if r.get("pos") == "verb" else [])
            else:
                keys = [table_key(code, r["word"])]
            for k in keys:
                if k:
                    out[code][k].append(rec)
    return out


def load_dict_tables(entries: dict, codes=DICT_CODES) -> dict:
    """Round-3 dictionary mappings (build_lang_mapping over the kaikki dumps in raw/daughters)."""
    from . import formula_search as fs
    from . import formula_search_multi as fm
    lex = list(entries.values())
    out: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    codes = [c for c in codes if c in fm.LANGS]
    if not codes:
        return out
    try:
        want = [c for L in codes for c in fm.LANGS[L].desc_codes]
        protos = fm.ProtoDB(want_desc=want)
    except FileNotFoundError:
        return out
    idx = fs.PieIndex(lex)
    for code in codes:
        try:
            lm = fm.build_lang_mapping(code, lex, protos, idx=idx)
        except FileNotFoundError:
            continue
        for k, r in lm.recs.items():
            derived = r.how in ("base", "root")
            out[code][k].append(_rec(r.ids, (f"dict:{code}",) + tuple(r.path), f"dict:{code}", derived))
    return out


# ---------------------------------------------------------------- the checker

class SecureChecker:
    """entries: lexicon id → entry; tables: {code: {key: [rec]}} (rec = (ids, path, source, derived)).
    `loader(code) → {key: [rec]}` fills a language's table on first use."""

    def __init__(self, entries: dict, tables: dict | None = None, loader=None):
        self.entries = entries
        self.tables = {c: dict(t) for c, t in (tables or {}).items()}
        self.loader = loader
        self._rev: dict = {}
        self._memo: dict = {}
        self._siblings: dict = collections.defaultdict(set)
        for i, e in entries.items():
            if e.get("root_id"):
                self._siblings[e["root_id"]].add(i)

    @classmethod
    def from_disk(cls, entries: dict, dictionaries: bool = True) -> "SecureChecker":
        corpus = load_corpus_tables()
        cache: dict = {}

        def loader(code):
            if not cache:
                cache.update({"kaikki": load_kaikki_tables(entries)})
                cache["dict"] = load_dict_tables(entries) if dictionaries else {}
            merged = collections.defaultdict(list)
            for src in (corpus, cache["kaikki"], cache["dict"]):
                for k, recs in src.get(code, {}).items():
                    merged[k] += recs
            return merged
        return cls(entries, {}, loader)

    def table(self, code: str | None) -> dict:
        if code is None:
            return {}
        if code not in self.tables:
            self.tables[code] = self.loader(code) if self.loader else {}
        return self.tables[code]

    # -- levels
    def level_of(self, lid: str, ids) -> str | None:
        ids = set(ids)
        if lid in ids:
            return "exact"
        rid = (self.entries.get(lid) or {}).get("root_id")
        if rid and (rid in ids or ids & self._siblings.get(rid, set())):
            return "root"
        return None

    def _reflex_keys(self, lid: str, code: str | None, lang: str) -> list[tuple[str, str]]:
        """(key, label) of the lexeme's own reflexes in this language: lexicon lists, bridged
        proto-forms (Vedic, Greek), and the forms the tables map to it."""
        k = (lid, code, lang)
        if k not in self._memo:
            self._memo[k] = [(rk, lab, stems(code, rk)) for rk, lab in self._reflex_keys_raw(lid, code, lang)]
        return self._memo[k]

    def _reflex_keys_raw(self, lid: str, code: str | None, lang: str) -> list[tuple[str, str]]:
        from . import formula_search as fs
        e = self.entries.get(lid) or {}
        names = set(LEX_NAMES.get(code, ())) | set(EXTRA_LEX_NAMES.get(lang, ())) | {lang}
        out = []
        for L, rs in (e.get("reflexes") or {}).items():
            for r in rs:
                if r.get("borrowed") or r.get("uncertain"):
                    continue
                if L in names:
                    f = r.get("form") or ""
                    if code not in ("grc", "cu") and r.get("roman") and (code in ("sa", "hit", "ae", "xcl", "got")
                                                                        or not re.search(r"[a-zA-Z]", f)):
                        f = r["roman"]          # transliterate non-Latin scripts (Luw. 𒉺𒋫𒀀𒀸 → patās)
                    if f and not f.startswith("-"):
                        out.append((key(code, f), f"lexicon:{L}:{f}"))
                elif L in LIGHT_BRIDGES.get(lang, ()):
                    for f in re.split(r"\s*[~,]\s*", r.get("form") or ""):
                        if f and not f.startswith("-"):
                            out.append((key(code, f.replace("ˀ", "")), f"lexicon-bridge:{L}:{f}"))
                elif L in BRIDGES.get(code, ()):
                    f = r.get("form") or ""
                    cands = fs.pii_to_skt(f) if code == "sa" else fs.ph_to_grc(f)
                    out += [(c, f"lexicon-bridge:{L}:{f}") for c in cands[:2]]
        out += [(k, f"table-form:{k}") for k in self._table_forms(lid, code)]
        return [(k, lab) for k, lab in out if k and len(k) >= 2]

    def _table_forms(self, lid: str, code: str | None) -> set[str]:
        """Keys (comparison space) of words the tables map to lid without a derivation."""
        if code is None:
            return set()
        if code not in self._rev:
            rev = collections.defaultdict(set)
            for k, recs in self.table(code).items():
                for ids, path, src, derived in recs:
                    if derived:
                        continue
                    w = next((p.split(":", 1)[1] for p in path if p.startswith(f"{code}:")
                              or p.startswith(f"kaikki-{code}:")), None)
                    ck = key(code, w) if (w and code == "grc") else (k if code != "grc" else None)
                    for i in ids:
                        if ck:
                            rev[i].add(ck)
            self._rev[code] = rev
        return self._rev[code].get(lid, set())

    def _table_hits(self, code: str | None, s: str, lemma: bool) -> list:
        from .formula_search_multi import hit_entry_stems
        t = self.table(code)
        if not t:
            return []
        ks = {table_key(code, s)}
        if code == "sa":
            from .formula_search import skt_lemma_keys
            ks |= set(skt_lemma_keys(s.replace("/", "~")))
            ks |= {k[:-2] + "ṛ" for k in ks if k.endswith("ar") and len(k) > 4}   # duhitár- = duhitṛ
        if code == "hit":
            ks |= set(hit_entry_stems(s.strip("-")))
        return [r for k in ks if k for r in t.get(k, [])]

    def match(self, lid: str, code: str | None, lang: str, s: str, lemma: bool) -> dict | None:
        """Best evidence that cited string s continues lid, or None."""
        best = None

        def put(level, via, path):
            nonlocal best
            rank = {"exact": 2, "root": 1}
            if best is None or rank[level] > rank[best["level"]]:
                best = {"level": level, "cited": s, "via": via, "path": list(path)}
        # (a) mapping tables
        for ids, path, src, derived in self._table_hits(code, s, lemma):
            lv = self.level_of(lid, ids)
            if lv:
                put("root" if derived else lv, src, path)
        # (b) whole-word equality with the reflexes (and with the root's / siblings' reflexes: root level)
        k = key(code, s)
        if k and len(k) >= 2:
            mine = stems(code, k) if not lemma else {k}
            for rk, lab, rst in self._reflex_keys(lid, code, lang):
                if mine & rst:
                    put("exact", "reflex", [lab])
                    break
            if (best is None or best["level"] != "exact") and code in PREVERBS:
                for pv in PREVERBS[code]:
                    if k.startswith(pv) and len(k) - len(pv) >= 3:
                        rest = stems(code, k[len(pv):])
                        hit = next((lab for rk, lab, rst in self._reflex_keys(lid, code, lang) if rest & rst), None)
                        if hit:
                            put("exact", "reflex", [f"preverb:{pv}", hit])
                            break
            if best is None or best["level"] != "exact":
                rid = (self.entries.get(lid) or {}).get("root_id")
                for other in ([rid] if rid else []) + sorted(self._siblings.get(rid, set()) - {lid}):
                    hit = next((lab for rk, lab, rst in self._reflex_keys(other, code, lang)
                                if not lab.startswith("table-form") and mine & rst), None)
                    if hit:
                        put("root", "reflex", [f"{other}", hit])
                        break
        return best

    def _cited(self, r: dict):
        for w in r.get("lemmas", []) or []:
            for part in re.split(r"\s*~\s*", w):
                yield part, True
        for w in r.get("words", []) or []:
            for part in str(w).split():
                yield part, False

    def check(self, lid: str, refs: list[dict]) -> dict:
        if lid.startswith("compound:"):
            return self.check_compound(lid, refs)
        exact, rootlvl, ev = set(), set(), {}
        for r in refs:
            if r.get("role", "parallel") != "parallel":
                continue
            lang = r.get("lang", "")
            b, code = branch_of(lang), LANG_CODE.get(lang)
            for s, is_lemma in self._cited(r):
                m = self.match(lid, code, lang, s, is_lemma)
                if not m:
                    continue
                if m["level"] == "exact":
                    exact.add(b)
                    if ev.get(b, {}).get("level") != "exact":
                        ev[b] = {**m, "locus": r.get("locus"), "lang": lang}
                elif b not in ev:
                    rootlvl.add(b)
                    ev[b] = {**m, "locus": r.get("locus"), "lang": lang}
        rootlvl -= exact
        return {"exact_branches": sorted(exact), "root_branches": sorted(rootlvl),
                "level": "exact" if len(exact) >= 2 else "root" if len(exact | rootlvl) >= 2 else "none",
                "evidence": {b: ev[b] for b in sorted(ev)}}

    # -- compounds
    @staticmethod
    def compound_members(cid: str) -> tuple[str, str]:
        body = cid.split(":", 2)[2]            # "<first>+<second>" (the first member may contain ':')
        first, second = body.rsplit("+", 1)
        return PREFIX_ALIASES.get(first, first), second

    def _first_prefixes(self, first: str, code: str | None, lang: str) -> list[tuple[str, str]]:
        if first in PREFIX_REFLEXES:
            return [(p, f"prefix:{first}:{p}") for p in PREFIX_REFLEXES[first].get(code, [])]
        out = []
        for rk, lab, rst in self._reflex_keys(first, code, lang):
            for st in rst:
                if len(st) >= 3:
                    out.append((st, lab))
        return out

    def check_compound(self, cid: str, refs: list[dict]) -> dict:
        first, second = self.compound_members(cid)
        lv = {"exact": 2, "root": 1}
        per = {"first": collections.defaultdict(int), "second": collections.defaultdict(int)}
        comp, ev = {}, {}
        for r in refs:
            if r.get("role", "parallel") != "parallel":
                continue
            lang = r.get("lang", "")
            b, code = branch_of(lang), LANG_CODE.get(lang)
            for s, is_lemma in self._cited(r):
                k = key(code, s)
                for pref, plab in sorted(self._first_prefixes(first, code, lang), key=lambda x: -len(x[0])):
                    if not (k.startswith(pref) and len(k) - len(pref) >= 2):
                        continue
                    l1 = 2                    # a closed prefix or the first member's own reflex
                    rest = k[len(pref):]
                    m2 = self._match_key(second, code, lang, rest, s)
                    # the whole word mapped to the second member through its base (εὔιππος → ἵππος)
                    for ids, path, src, derived in self._table_hits(code, s, is_lemma):
                        lvl = self.level_of(second, ids)
                        if lvl and (m2 is None or lv[lvl] > lv[m2["level"]]):
                            m2 = {"level": lvl, "cited": s, "via": src, "path": list(path)}
                    if not m2:
                        continue
                    l2 = lv[m2["level"]]
                    per["first"][b] = max(per["first"][b], l1)
                    per["second"][b] = max(per["second"][b], l2)
                    both = min(l1, l2)
                    if both > comp.get(b, 0):
                        comp[b] = both
                        ev[b] = {"level": "exact" if both == 2 else "root", "cited": s, "locus": r.get("locus"),
                                 "lang": lang, "first": plab, "second": {k2: m2[k2] for k2 in ("level", "via", "path")}}
                    break
        exact = {b for b, x in comp.items() if x == 2}
        rootlvl = {b for b, x in comp.items() if x == 1}

        def side(d):
            return {"exact_branches": sorted(b for b, x in d.items() if x == 2),
                    "root_branches": sorted(b for b, x in d.items() if x == 1)}
        return {"exact_branches": sorted(exact), "root_branches": sorted(rootlvl),
                "level": "exact" if len(exact) >= 2 else "root" if len(exact | rootlvl) >= 2 else "none",
                "evidence": {b: ev[b] for b in sorted(ev)},
                "members": {first: side(per["first"]), second: side(per["second"])}}

    def _match_key(self, lid: str, code: str | None, lang: str, rest: str, cited: str) -> dict | None:
        """A compound's remainder (already in key space) against the second member."""
        t = self.table(code)
        best = None
        for st in stems(code, rest):
            tk = st
            if code == "grc":          # tables are keyed in Greek script: compare through the table forms
                tk = None
            for ids, path, src, derived in (t.get(tk, []) if tk else []):
                lvl = self.level_of(lid, ids)
                if lvl and not derived:
                    if best is None or lvl == "exact":
                        best = {"level": lvl, "cited": cited, "via": src, "path": list(path)}
        if best and best["level"] == "exact":
            return best
        mine = stems(code, rest)
        for rk, lab, rst in self._reflex_keys(lid, code, lang):
            if mine & rst:
                return {"level": "exact", "cited": cited, "via": "reflex", "path": [lab]}
        return best


def plan_compound_ids(plan: dict) -> list[tuple[str, str, str]]:
    """(compound lex_id, first, second) for every compound slot of a plan."""
    out = []
    for cl in plan.get("clauses", []):
        for s in cl.get("slots", []):
            if s.get("lex_id") == "compound" and s.get("compound"):
                c = s["compound"]
                first = PREFIX_ALIASES.get(c.get("first"), c.get("first"))
                cid = f"compound:{c.get('type', 'bahuvrihi')}:{first}+{c.get('second')}"
                out.append((cid, first, c.get("second")))
    return out
