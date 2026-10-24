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
    kaikki-chain) is a different formation: root level. The corpus tables are
    read as pie.mapping resolves them (pie.mapping.iter_resolved: the same
    population the mapping-precision measurement samples), so override rows
    add, remove and remap lemmas; a row marked "formation": "derivative"
    (Ved. sū́rya-, mahā́nt-) is root level, one marked "uncertain" no evidence.
    Wiktionary/kaikki etymologies link a derivative to its base's page (mahát
    "from *méǵh₂s") and alternative-form pages to their target (*suHyús →
    *suHnús), so a kaikki link alone does not show the same formation.
(b) The lexicon's reflex lists (and the Indo-Iranian / Hellenic proto-forms bridged
    to Vedic / Greek keys): whole-word equality of the normalized forms. A cited
    lemma must equal a reflex (the reflex's declared ending may be stripped, since
    citation conventions differ: Hitt. kuenzi / kuen-); a cited inflected word is
    compared stem to stem, after stripping one ending from the declared list of
    its language (ENDINGS) on both sides. Never a prefix match. Reflexes marked
    uncertain or borrowed are skipped. Forms the tables map to the lexeme count as
    reflexes too ("table form").
Reviewed decisions win over every route. The override rows of all corpora of a language (rv and av for
Vedic, hom and grp for Greek, ...) decide a cited lemma with the same key, and an inflected word through its
stem when its ref cites that lemma: no route (table, kaikki link, dictionary chain, lexicon reflex, table
form, preverb or compound remainder, sibling reflex) may then give a lexeme more than the decision allows
(Gov): nothing for one the decision removed or that lies outside the family it lists (Latv. pūrs 'dowry
chest' is not *péh₂wr̥; Ved. gír- 'praise' is not *gʷerh₃- 'swallow' through giráti), at most its own level
for one it removed in favour of a root (υἱός: *suHnús only root level). A ref may give senses
({"senses": {word: gloss}}): a decision whose sense does not overlap does not apply. Reviewed 'form' rows
send a cited surface form to its lemma first.
Either way 'exact' means the same formation: an agent / kin noun in *-tor-/*-tér-
whose cited daughter word shows the other type (Vedic accent, Greek / Latin suffix
grade: dātā́ and δωτῆρες against *déh₃tōr) is root level (formation_clash).

Compounds ("compound:<type>:<first>+<second>"): a cited word counts for a branch
when it begins with a reflex of the first member (closed prefixes: PREFIX_REFLEXES)
and its remainder matches the second member as above; the compound is exact in a
branch only if both members are exact in that same word. Each member's branches
are recorded under "members".
"""

from __future__ import annotations

import collections
import re
import unicodedata
from pathlib import Path

from . import mapping as mp

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


# ---------------------------------------------------------------- formation: agent nouns

# The two PIE agent-noun types are different formations (Tichy 1995; Lindeman): root-accented *-tor-
# (o-grade suffix: *déh₃tōr, *ǵénh₁tōr) and suffix-accented *-tér- (e-grade: *ǵenh₁tḗr, *ph₂tḗr).
# Vedic keeps the accent (dā́tā vásu 'giving goods' ~ dātā́ vásūnām 'giver of goods'), Greek and Latin
# the suffix grade (δώτωρ, -τορ- ~ δωτήρ, -τῆρ-; Lat. -tor). Avestan, Germanic etc. show neither:
# a word there is not checked. Keys drop accents, so the cited string is read as written.
_ACUTE, _SYLLABIC = "́", ("̥", "̣")


def _units(s: str) -> list[tuple[str, str]]:
    """NFD string → [(base letter, its combining marks)]."""
    out: list = []
    for ch in unicodedata.normalize("NFD", s):
        if unicodedata.combining(ch) and out:
            out[-1] = (out[-1][0], out[-1][1] + ch)
        else:
            out.append((ch, ""))
    return out


def _accented(b: str, m: str) -> bool:
    """An acute on a vowel or a syllabic resonant (not ś, ǵ, ḱ)."""
    return _ACUTE in m and (b in "aeiou" or (b in "rlmn" and any(x in m for x in _SYLLABIC)))


def agent_type_pie(form: str) -> str | None:
    """'root' (*-tor-, root accent) or 'suffix' (*-tér-, suffix accent) for an agent / kin noun in
    *-tor/-ter; None for anything else and for the mixed type (*méh₂tēr: root accent, e-grade)."""
    u = _units((form or "").strip("*- ").lower())
    if len(u) < 4 or u[-1][0] != "r" or u[-2][0] not in "oe" or u[-3][0] != "t":
        return None
    suffix_acc = _ACUTE in u[-2][1]
    root_acc = any(_accented(b, m) for b, m in u[:-3])
    if suffix_acc and u[-2][0] == "e":
        return "suffix"
    if root_acc and not suffix_acc and u[-2][0] == "o":
        return "root"
    return None


def agent_type_cited(code: str | None, s: str) -> str | None:
    """The agent-noun type a cited daughter word shows, or None when it shows none."""
    s = (s or "").strip().strip("*-√").strip().lower()
    if code == "sa":
        u = _units(s)
        ts = [i for i in range(len(u) - 1) if u[i][0] == "t" and u[i + 1][0] in "aru"]
        acc = [i for i, (b, m) in enumerate(u) if _accented(b, m)]
        if not ts or not acc:
            return None                 # unaccented (DCS, epic): no evidence either way
        return "suffix" if acc[0] > ts[-1] else "root"
    if code in ("grc", "la"):
        k = _strip(s).replace("ς", "σ") if code == "grc" else _strip(s)
        m = list(re.finditer(r"τ([ηεωο])ρ" if code == "grc" else r"t([eo])r", k))
        if m:
            return "suffix" if m[-1].group(1) in "ηεe" else "root"
    return None


# ---------------------------------------------------------------- tables

def _rec(ids, path, source, derived=False):
    return (frozenset(ids), tuple(path), source, bool(derived))


# corpora whose mapping is built live (no table in mapping/): their override rows still decide
LIVE_CORPUS_CODE = {"rv": "sa", "hom": "grc", "lat": "la", "orv": "cu"}
# table row languages that the checker reads under another code (Middle Irish rows of a CELT table: sga)
LANG_ALIAS = {"mga": "sga", "orv": "cu"}
CHECK_CODES = frozenset(c for c in LANG_CODE.values() if c)


def code_of(corpus: str, lang: str | None = None) -> str | None:
    """The checker's language code for a corpus (or a row of it in language `lang`); None: not read."""
    c = CORPUS_CODE.get(corpus) or LIVE_CORPUS_CODE.get(corpus)
    if c:
        return c
    c = LANG_ALIAS.get(lang, lang)
    return c if c in CHECK_CODES else None


def load_lemma_overrides() -> dict:
    """The mapping errata, {corpus: {lemma: (ids, row)}}: data/research/formulas/mapping-overrides.json and
    the per-language files in mapping-overrides/ (pie.mapping.load_overrides)."""
    return mp.load_overrides(ROOT)["lemma"]


def override_row(r: dict, overrides: dict) -> tuple[dict | None, bool]:
    """A mapping-table row with its corpus's lemma erratum applied → (row or None if unmapped, overridden?).
    An override row with "formation": "derivative" says the lemma continues a derivative of the listed
    lexeme (Ved. mahā́nt- for *méǵh₂s): the row then counts as a derivation, root level.
    (Kept for callers; the checker itself resolves through pie.mapping.)"""
    hit = overrides.get(r.get("corpus"), {}).get(r.get("lemma"))
    if not hit:
        return r, False
    ids, orow = hit
    if not ids:
        return None, True
    note = orow.get("erratum") or orow.get("note") or "override"
    path = [p for p in r.get("path", [])[:1]] + ["erratum:" + note]
    return {**r, "lex_id": sorted(ids), "path": path, "how": "erratum",
            "formation": orow.get("formation")}, True


def _parts(code: str, lemma: str) -> list[str]:
    """A decided lemma's citation parts: '~' variants ('gír- ~ gīr-'); Hittite: before '@'. A lemmatizer
    group 'a|b' (an ambiguous corpus form) has none: its decision is about that table row only, not about
    the lemmas a and b wherever else they are cited."""
    if "|" in str(lemma or ""):
        return []
    out = []
    for part in re.split(r"\s*~\s*", str(lemma or "")):
        part = part.split("@")[0] if code == "hit" else part
        if part.strip():
            out.append(part)
    return out


def row_keys(code: str, r: dict) -> set[str]:
    from .formula_search_multi import hit_tlh_keys
    keys = set()
    for part in str(r.get("lemma", "")).split("|"):
        if code == "hit":
            keys |= set(hit_tlh_keys(part.split("@")[0]))
        else:
            keys.add(table_key(code, part))
    for part in re.split(r"\s*[|~]\s*", str(r.get("word", ""))):    # RV lemmas: "gáv- ~ gó-"
        keys.add(table_key(code, part))
    return {k for k in keys if k}


def decision_keys(code: str, lemma: str, word: str | None = None) -> set[str]:
    """Table-space keys of a decided lemma (and of its table row's word): '~' variants split, a group
    'a|b' none (see _parts)."""
    from .formula_search_multi import hit_tlh_keys
    keys = set()
    for part in _parts(code, lemma) + (_parts(code, word) if word and _parts(code, lemma) else []):
        if code == "hit":
            keys |= set(hit_tlh_keys(part))
        keys.add(table_key(code, part))
    return {k for k in keys if k}


_TONES = {"\u0300", "\u0301", "\u0302", "\u0342", "\u0313", "\u0314", "\u0344"}


def _tone_form(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower().replace("ς", "σ"))
                   if c.isalpha() or c in _TONES)


def tone_clash(a: str, b: str) -> bool:
    """Both written with accents or breathings, and these differ: two words, whatever their keys."""
    fa, fb = _tone_form(a), _tone_form(b)
    return bool(_TONES & set(fa)) and bool(_TONES & set(fb)) and fa != fb


class Population:
    """What the checker reads from the mapping tables: pie.mapping.iter_resolved (the same population the
    mapping-precision measurement samples), its table recs, and the reviewed decisions per language."""

    def __init__(self):
        self.resolved: list = []                                  # pie.mapping.Resolved, in load order
        self.tables: dict = collections.defaultdict(lambda: collections.defaultdict(list))
        self.corrected: dict = collections.defaultdict(set)       # code → table keys of decided lemmas
        self.decided: dict = collections.defaultdict(list)        # code → [(corpus, lemma, word, decisions)]
        self.auto: dict = collections.defaultdict(lambda: collections.defaultdict(set))  # code → key → auto ids
        self.forms: dict = {}                                     # code → {form key: lemma}
        self.overrides: dict | None = None                        # pie.mapping.load_overrides() shape


def build_population(rows_by_corpus: dict, overrides: dict | None, codes=None, added: bool = True) -> Population:
    """rows_by_corpus: {corpus: [raw table rows]}; corpora with override rows but no table are added
    (their decided lemmas only) when `added`."""
    ov = mp.as_overrides(overrides or {})
    pop = Population()
    corpora = list(rows_by_corpus) + ([c for c in ov["decisions"] if c not in rows_by_corpus] if added else [])
    for corpus in corpora:
        rows = rows_by_corpus.get(corpus, [])
        lang = mp.corpus_lang(corpus, rows)
        row_of = {r["lemma"]: r for r in rows}
        for x in mp.resolve_rows(corpus, rows, ov).values():
            code = code_of(corpus, x.lang)
            if code is None or (codes is not None and code not in codes):
                continue
            pop.resolved.append(x)
            if x.uncertain:
                continue                      # an uncertain equation is never secure evidence
            r = row_of.get(x.lemma, {})
            derived = x.how in ("base", "root") or x.derivative or any(
                str(p).startswith(DERIVED_MARKS) for p in x.path)
            rec = _rec(x.ids, [f"table:{corpus}"] + list(x.path), f"table:{corpus}", derived)
            for k in row_keys(code, {"lemma": x.lemma, "word": r.get("word", x.word)}):
                pop.tables[code][k].append(rec)
        # proto-page and headword decisions decide the table words mapped through them, like lemma rows
        # (ON fara through gem-pro *faraną: no route may then restore the link the page decision dropped)
        path_decided = {}
        if ov.get("proto") or ov.get("key"):
            for r in rows:
                if r["lemma"] in ov["decisions"].get(corpus, {}):
                    continue
                rl = r.get("lang") or lang
                pd = mp.path_decision([f"{rl}:{r['lemma']}", *r.get("path", ())], rl, ov)
                if pd:
                    path_decided[r["lemma"]] = [pd]
        for lem, ds in [*ov["decisions"].get(corpus, {}).items(), *path_decided.items()]:
            r = row_of.get(lem, {})
            code = code_of(corpus, r.get("lang") or lang)
            if code is None or (codes is not None and code not in codes):
                continue
            keys = decision_keys(code, lem, r.get("word"))
            pop.corrected[code] |= keys
            pop.decided[code].append((corpus, lem, r.get("word"), tuple(ds)))
            for k in keys:
                pop.auto[code][k] |= set(mp.strip_blocked(r.get("lex_id", ())))
    # headword decisions ('key' rows: a daughter headword and the words mapped through it)
    for lang, rows in ov.get("key", {}).items():
        code = code_of("", lang)
        if code is None or (codes is not None and code not in codes):
            continue
        for k, d in rows.items():
            keys = decision_keys(code, k)
            pop.corrected[code] |= keys
            pop.decided[code].append((f"key:{lang}", k, None, (d,)))
    for lang, fo in ov.get("form", {}).items():
        code = LANG_ALIAS.get(lang, lang)
        pop.forms.setdefault(code, {}).update(fo)
    pop.overrides = ov
    return pop


def table_from_rows(rows, overrides: dict | None = None) -> tuple[dict, dict]:
    """(corpus, row) pairs of the mapping tables → ({code: {key: [rec]}}, {code: keys of decided lemmas}),
    resolved by pie.mapping (override rows whose lemma the rows lack are added). The decided keys are
    dropped from the round-2 kaikki and dictionary tables when they are merged, so a corrected lemma is
    not re-admitted through another source (υἱός, mahát)."""
    by: dict = collections.defaultdict(list)
    for corpus, r in rows:
        by[corpus].append(r)
    pop = build_population(dict(by), overrides or {})
    return pop.tables, pop.corrected


def load_population(codes=None, overrides: dict | None = None, root: Path = ROOT) -> Population:
    """data/research/formulas/mapping/*.jsonl with every override applied (pie.mapping.iter_resolved)."""
    ov = mp.as_overrides(overrides, root)
    rows = {c: mp.read_table(c, root) for c in mp.table_corpora(root)}
    return build_population(rows, ov, codes)


def load_corpus_tables(codes=None, overrides: dict | None = None) -> tuple[dict, dict]:
    """data/research/formulas/mapping/*.jsonl, errata applied → ({code: {key: [rec]}}, corrected keys)."""
    pop = load_population(codes, overrides)
    return pop.tables, pop.corrected


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


def _path_decided(code: str, rec, overrides: dict | None):
    """An automatic rec with the proto-page or headword decision its path runs through applied (None:
    removed)."""
    ids, p, s, d = rec
    pd = mp.path_decision(p[1:], code, overrides) if overrides else None
    if pd is None:
        return rec
    if not pd.ids or pd.uncertain:
        return None
    return (pd.ids, tuple(p) + ("erratum:" + pd.note,), s, d or pd.derivative)


def merge_tables(code: str, corpus: dict, others, corrected: dict, dropped: dict | None = None,
                 overrides: dict | None = None) -> dict:
    """One language's table: the corpus rows, then the automatic links of the other sources (BLOCKED_IDS
    removed, proto-page and headword decisions of `overrides` applied: pie.mapping.path_decision),
    except for keys of a decided lemma (a reviewed decision wins over the automatic links). `dropped`
    collects the ids so dropped, per key."""
    merged = collections.defaultdict(list)
    for src in (corpus, *others):
        for k, recs in src.get(code, {}).items():
            if src is not corpus:
                recs = [(frozenset(mp.strip_blocked(ids)), p, s, d) for ids, p, s, d in recs]
                recs = [x for x in (_path_decided(code, r, overrides) for r in recs if r[0]) if x]
                if k in corrected.get(code, ()):
                    if dropped is not None:
                        for x in recs:
                            dropped[k] |= x[0]
                    continue
            merged[k] += recs
    return merged


LEVEL_RANK = {None: 0, "root": 1, "exact": 2}


class Gov:
    """The reviewed decisions (pie.mapping.Decision) that apply to one cited word of a language, and what
    they leave to the other routes. Every route's level for a lexeme is capped by `cap`:
      - lexemes marked uncertain: no route may give more than the decision itself does (nothing);
      - a lexeme the decision lists: exact (root for a "derivative" decision);
      - a lexeme under a root the decision lists: exact (the decision picked the root, e.g. between
        homograph roots: Ved. bhā 'shine', not 'speak'; a lexicon reflex list may show the lexeme itself),
        unless the decision only demoted it, i.e. every automatic id it removed lies in the family it kept
        (υἱός: *suHnús → the root *sewH-, because υἱός is *suH-iu-): then root;
      - a sibling of a listed lexeme: root; anything else: none (no route restores an equation the
        review contradicts)."""

    def __init__(self, checker: "SecureChecker", decided: list, auto: set):
        self.ch = checker
        self.decided = decided                       # [(corpus, lemma, Decision)]
        certain = [d for _, _, d in decided if not d.uncertain]
        self.allowed = frozenset().union(*(d.ids for d in certain)) if certain else frozenset()
        self.derivative = frozenset().union(*(d.ids for d in certain if d.derivative)) if certain else frozenset()
        unc = [d.ids for _, _, d in decided if d.uncertain]
        self.uncertain = (frozenset().union(*unc) if unc else frozenset()) - self.allowed
        self.removed = frozenset(auto) - self.allowed
        self.demoted = bool(self.removed) and all(checker.level_of(i, self.allowed) for i in self.removed)
        self.path = [f"override:{c}:{lem}" for c, lem, _ in decided[:3]]

    def own(self, lid: str) -> str | None:
        """The level the decisions themselves give lid."""
        best = None
        for _, _, d in self.decided:
            if d.uncertain or not d.ids:
                continue
            lv = self.ch.level_of(lid, d.ids)
            if lv and d.derivative:
                lv = "root"
            if LEVEL_RANK[lv] > LEVEL_RANK[best]:
                best = lv
        return best

    def cap(self, lid: str) -> str | None:
        own = self.own(lid)
        if lid in self.uncertain or lid in self.allowed or (lid in self.removed and self.demoted):
            return own
        rid = (self.ch.entries.get(lid) or {}).get("root_id")
        if own == "root" and rid in self.allowed and rid not in self.derivative:
            return "exact"
        return own

    def limit(self, lid: str, level: str | None) -> str | None:
        c = self.cap(lid)
        return level if LEVEL_RANK[level] <= LEVEL_RANK[c] else c


# ---------------------------------------------------------------- the checker

class SecureChecker:
    """entries: lexicon id → entry; tables: {code: {key: [rec]}} (rec = (ids, path, source, derived)).
    `loader(code) → {key: [rec]}` fills a language's table on first use. `population` (a Population)
    carries the reviewed decisions: with it, every route is capped by them (Gov); without it (fixtures),
    the tables alone decide."""

    def __init__(self, entries: dict, tables: dict | None = None, loader=None, population: Population | None = None):
        self.entries = entries
        self.tables = {c: dict(t) for c, t in (tables or {}).items()}
        self.loader = loader
        self.population = population
        self.dropped: dict = collections.defaultdict(lambda: collections.defaultdict(set))
        self._rev: dict = {}
        self._memo: dict = {}
        self._gov_idx: dict = {}
        self._siblings: dict = collections.defaultdict(set)
        for i, e in entries.items():
            if e.get("root_id"):
                self._siblings[e["root_id"]].add(i)

    @classmethod
    def from_population(cls, entries: dict, pop: Population, others_loader=None) -> "SecureChecker":
        """A checker over a Population; others_loader() → (kaikki tables, dictionary tables) on first use."""
        cache: dict = {}
        ch = cls(entries, {}, None, pop)

        def loader(code):
            if not cache:
                cache["others"] = tuple(others_loader()) if others_loader else ()
            # no key-level drop of the other sources: the decisions cap them word by word (Gov), where a
            # drop by key would also hit an accent homograph (ὠμός under ὦμος)
            return merge_tables(code, pop.tables, cache["others"], {}, ch.dropped[code], pop.overrides)
        ch.loader = loader
        return ch

    @classmethod
    def from_disk(cls, entries: dict, dictionaries: bool = True, overrides: dict | None = None) -> "SecureChecker":
        pop = load_population(overrides=overrides)
        return cls.from_population(entries, pop, lambda: (load_kaikki_tables(entries),
                                                          load_dict_tables(entries) if dictionaries else {}))

    def table(self, code: str | None) -> dict:
        if code is None:
            return {}
        if code not in self.tables:
            self.tables[code] = self.loader(code) if self.loader else {}
        return self.tables[code]

    # -- reviewed decisions
    def _gov_index(self, code: str) -> dict:
        """{"eq": {table key: [entry]}, "full": {comparison key: [entry]}, "stem": {comparison stem: [entry]}},
        entry = (corpus, lemma, decisions, table keys, citation parts)."""
        if code not in self._gov_idx:
            eq, full, st = (collections.defaultdict(list) for _ in range(3))
            for corpus, lem, word, ds in (self.population.decided.get(code, []) if self.population else []):
                parts = tuple(_parts(code, lem) + (_parts(code, word) if word and _parts(code, lem) else []))
                e = (corpus, lem, ds, frozenset(decision_keys(code, lem, word)), parts)
                for k in e[3]:
                    eq[k].append(e)
                # comparison space: the table keys themselves, except Greek (tables in Greek script)
                cks = {key(code, p) for p in parts} if code == "grc" else e[3]
                for ck in cks:
                    if ck and len(ck) >= 2:
                        full[ck].append(e)
                        for x in stems(code, ck):
                            st[x].append(e)
            self._gov_idx[code] = {"eq": eq, "full": full, "stem": st}
        return self._gov_idx[code]

    def _eq_entries(self, code: str, s: str, keys=()) -> dict:
        """Decided lemmas that cited lemma s is: same table key, and no clash of accent or breathing when
        both are written with them (Gk ὦμος 'shoulder' is not ὠμός 'raw', though both key ωμοσ)."""
        idx = self._gov_index(code)
        out = {}
        for x in {y for y in self._hit_keys(code, s) if y} | set(keys):
            for e in idx["eq"].get(x, ()):
                if not e[4] or any(not tone_clash(s, p) for p in e[4]):
                    out[(e[0], e[1])] = e
        return out

    def governing(self, code: str | None, s: str | None = None, lemma: bool = True, sense: str | None = None,
                  k: str | None = None, context: set | None = None, eq: set | None = None) -> Gov | None:
        """The decisions that apply to cited s. A lemma: the decided lemmas it is (_eq_entries; `eq`: table
        keys of a word with no citation string). An inflected word, or with k a remainder already in
        comparison-key space: when its ref cites lemmas (`context`, see SecureChecker.context), a decided
        lemma among them that it shares a stem with (the relation the reflex route uses); otherwise a
        decided lemma whose whole key it is plus one declared ending. A homograph stem elsewhere in the
        language does not decide it (πρόσ-φατος is not φάτις, giráti cited for √gṝ- is not gír-).
        None when no decision applies."""
        if code is None or not self.population or not self.population.decided.get(code):
            return None
        idx = self._gov_index(code)
        hit = {}
        if s is not None:
            hit.update(self._eq_entries(code, s))
        for x in eq or ():
            for e in idx["eq"].get(x, ()):
                hit[(e[0], e[1])] = e
        ck = k if k is not None else (key(code, s) if (s is not None and not lemma) else None)
        if ck:
            for x in stems(code, ck):
                for e in (idx["full"].get(x, ()) if context is None else ()):
                    hit[(e[0], e[1])] = e
                for e in (idx["stem"].get(x, ()) if context else ()):
                    if (e[0], e[1]) in context:
                        hit[(e[0], e[1])] = e
        if not hit:
            return None
        decided = [(c, lem, d) for (c, lem), e in sorted(hit.items()) for d in e[2]
                   if sense is None or mp.senses_overlap(d.sense, sense)]
        if not decided:
            return None
        auto: set = set()
        keys = set()
        for e in hit.values():
            keys |= e[3]
        tab = self.table(code)
        for x in keys:
            auto |= self.population.auto.get(code, {}).get(x, set())
            auto |= self.dropped.get(code, {}).get(x, set())
            for ids, path, src, derived in tab.get(x, ()):
                if not any(str(p).startswith("erratum:") for p in path):
                    auto |= ids
        return Gov(self, decided, auto)

    def form_lemma(self, code: str | None, s: str) -> str | None:
        """The lemma a reviewed 'form' row sends a cited surface form to ('?…': an unknown fragment)."""
        fo = (self.population.forms.get(code) if self.population and code else None)
        if not fo:
            return None
        from .formula_search_multi import KEYS
        kf = KEYS.get(code)
        return fo.get(kf(s)) if kf else fo.get(s.lower())

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
        """Keys (comparison space) of words the tables map to lid without a derivation (and, for a word a
        reviewed decision governs, only where the decision leaves lid exact)."""
        if code is None:
            return set()
        if code not in self._rev:
            rev = collections.defaultdict(set)
            for k, recs in self.table(code).items():
                gov = None
                for ids, path, src, derived in recs:
                    if derived:
                        continue
                    w = next((p.split(":", 1)[1] for p in path if p.startswith(f"{code}:")
                              or p.startswith(f"kaikki-{code}:")), None)
                    ck = key(code, w) if (w and code == "grc") else (k if code != "grc" else None)
                    if not ck:
                        continue
                    if gov is None:
                        tw = next((p.split(":", 1)[1] for p in path if p.startswith(f"{code}:")), None)
                        gov = (self.governing(code, tw) if tw else self.governing(code, eq={k})) or False
                    for i in ids:
                        if not gov or gov.cap(i) == "exact":
                            rev[i].add(ck)
            self._rev[code] = rev
        return self._rev[code].get(lid, set())

    def _hit_keys(self, code: str | None, s: str) -> set[str]:
        from .formula_search_multi import hit_entry_stems
        ks = {table_key(code, s)}
        if code == "sa":
            from .formula_search import skt_lemma_keys
            ks |= set(skt_lemma_keys(s.replace("/", "~")))
            ks |= {k[:-2] + "ṛ" for k in ks if k.endswith("ar") and len(k) > 4}   # duhitár- = duhitṛ
        if code == "hit":
            ks |= set(hit_entry_stems(s.strip("-")))
        return ks

    def _table_hits(self, code: str | None, s: str, lemma: bool) -> list:
        t = self.table(code)
        if not t:
            return []
        return [r for k in self._hit_keys(code, s) if k for r in t.get(k, [])]

    def formation_clash(self, lid: str, code: str | None, s: str) -> str | None:
        """Why cited s, though it reaches lid, is another formation of it (None: no evidence of that).
        Only the agent-noun type is read off the word itself; derivatives come marked from the tables."""
        want = agent_type_pie((self.entries.get(lid) or {}).get("form", ""))
        got = agent_type_cited(code, s) if want else None
        if want and got and got != want:
            return f"formation:agent-noun:{got}-accented≠{want}-accented"
        return None

    def match(self, lid: str, code: str | None, lang: str, s: str, lemma: bool, sense: str | None = None,
              context: set | None = None) -> dict | None:
        """Best evidence that cited string s continues lid, or None. 'exact' needs the same formation:
        a word that reaches lid but shows another formation of it is root level. A reviewed decision
        (pie.mapping) that applies to s caps every route (Gov); a reviewed 'form' row first sends an
        inflected word to its lemma. context: table keys of the lemmas cited with an inflected word
        (None: any decided lemma whose stem it shares)."""
        cited = s
        if not lemma:
            fl = self.form_lemma(code, s)
            if fl:
                if fl.startswith("?"):
                    return None
                s, lemma = fl, True
        best = None
        clash = self.formation_clash(lid, code, cited)
        gov = self.governing(code, s, lemma, sense, context=context)

        def put(level, via, path, g=None):
            nonlocal best
            path = list(path)
            for gv in (gov, g):
                if gv is not None:
                    lv = gv.limit(lid, level)
                    if lv != level:
                        path += gv.path + [f"override-cap:{lv}"]
                    level = lv
            if level is None:
                return
            if level == "exact" and clash:
                level, path = "root", path + [clash]
            if best is None or LEVEL_RANK[level] > LEVEL_RANK[best["level"]]:
                best = {"level": level, "cited": cited, "via": via, "path": path}
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
                            put("exact", "reflex", [f"preverb:{pv}", hit],
                                self.governing(code, k=k[len(pv):]))
                            break
            if best is None or best["level"] != "exact":
                rid = (self.entries.get(lid) or {}).get("root_id")
                for other in ([rid] if rid else []) + sorted(self._siblings.get(rid, set()) - {lid}):
                    hit = next((lab for rk, lab, rst in self._reflex_keys(other, code, lang)
                                if not lab.startswith("table-form") and mine & rst), None)
                    if hit:
                        put("root", "reflex", [f"{other}", hit])
                        break
        # (c) the decision itself (an inflected word it governs through its stem, an override-only lemma)
        if gov is not None and (lv := gov.own(lid)):
            put(lv, "override", gov.path + [f"erratum:{d.note}" for _, _, d in gov.decided[:1]])
        return best

    def context(self, code: str | None, r: dict) -> set | None:
        """The decided lemmas, (corpus, lemma), that a ref's cited lemmas are (None when it cites none)."""
        lem = [p for w in r.get("lemmas", []) or [] for p in re.split(r"\s*~\s*", w)]
        if not (lem and code and self.population and self.population.decided.get(code)):
            return None
        return {x for p in lem for x in self._eq_entries(code, p)}

    def _cited(self, r: dict):
        senses = r.get("senses") or {}
        for w in r.get("lemmas", []) or []:
            for part in re.split(r"\s*~\s*", w):
                yield part, True, senses.get(w) or senses.get(part)
        for w in r.get("words", []) or []:
            for part in str(w).split():
                yield part, False, senses.get(w) or senses.get(part)

    def check(self, lid: str, refs: list[dict]) -> dict:
        if lid.startswith("compound:"):
            return self.check_compound(lid, refs)
        exact, rootlvl, ev = set(), set(), {}
        want = agent_type_pie((self.entries.get(lid) or {}).get("form", ""))
        shown = collections.defaultdict(set)        # branch → agent-noun types its matched words show
        for r in refs:
            if r.get("role", "parallel") != "parallel":
                continue
            lang = r.get("lang", "")
            b, code = branch_of(lang), LANG_CODE.get(lang)
            ctx = self.context(code, r)
            for s, is_lemma, sense in self._cited(r):
                m = self.match(lid, code, lang, s, is_lemma, sense, ctx)
                if not m:
                    continue
                if want and (t := agent_type_cited(code, s)) and (m["level"] == "exact" or any(
                        str(p).startswith("formation:agent-noun") for p in m["path"])):
                    shown[b].add(t)         # words that reach lid itself (not a sibling such as jánitrī-)
                if m["level"] == "exact":
                    exact.add(b)
                    if ev.get(b, {}).get("level") != "exact":
                        ev[b] = {**m, "locus": r.get("locus"), "lang": lang}
                elif b not in ev:
                    rootlvl.add(b)
                    ev[b] = {**m, "locus": r.get("locus"), "lang": lang}
        # a branch whose accent- or grade-marking words all show the other agent-noun type is that type:
        # Av. dātārō (no accent) beside Ved. dātā́ in the same cited cell is not evidence for *déh₃tōr
        for b in sorted(exact):
            if shown.get(b) and want not in shown[b]:
                exact.discard(b)
                rootlvl.add(b)
                ev[b] = {**ev[b], "level": "root", "path": list(ev[b]["path"]) + [
                    f"formation:agent-noun:branch shows {'/'.join(sorted(shown[b]))}-accented only"]}
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
            ctx = self.context(code, r)
            for s, is_lemma, sense in self._cited(r):
                k = key(code, s)
                whole = self.governing(code, s, is_lemma, sense, context=ctx)
                for pref, plab in sorted(self._first_prefixes(first, code, lang), key=lambda x: -len(x[0])):
                    if not (k.startswith(pref) and len(k) - len(pref) >= 2):
                        continue
                    l1 = 2                    # a closed prefix or the first member's own reflex
                    rest = k[len(pref):]
                    m2 = self._match_key(second, code, lang, rest, s)
                    # the whole word mapped to the second member through its base (εὔιππος → ἵππος)
                    for ids, path, src, derived in self._table_hits(code, s, is_lemma):
                        lvl = self.level_of(second, ids)
                        if lvl and whole is not None:
                            lvl = whole.limit(second, lvl)
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

    def _match_key(self, lid: str, code: str | None, lang: str, rest: str, cited: str,
                   context: set | None = None) -> dict | None:
        """A compound's remainder (already in key space) against the second member, capped by the
        decisions that govern the remainder."""
        gov = self.governing(code, k=rest, context=context)

        def capped(m):
            if m is None or gov is None:
                return m
            lv = gov.limit(lid, m["level"])
            return None if lv is None else {**m, "level": lv}
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
        best = capped(best)
        if best and best["level"] == "exact":
            return best
        mine = stems(code, rest)
        for rk, lab, rst in self._reflex_keys(lid, code, lang):
            if mine & rst:
                m = capped({"level": "exact", "cited": cited, "via": "reflex", "path": [lab]})
                if m and (best is None or LEVEL_RANK[m["level"]] > LEVEL_RANK[best["level"]]):
                    return m
                break
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
