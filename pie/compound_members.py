"""Compound members: the lexicon ids a compound's members reach, for search (corpus-quality batch 2).

The word mapping keys a compound to one lexeme (εὔιππος -> *h₁éḱwos, ἀνδροφόνος -> *gʷʰen-) or to none
(πολυώνυμος, suáśva-), and the prefixes *h₁su-, *n̥-, *dus- had no postings at all, so compound-only
formulas ('good horses', 'man-slaying', 'many-named') returned no compound hits (formula witness scan
item 42). This module finds a compound's members and gives each member the ids that the production
mapping gives the member word itself:

  - members from the headword's Wiktionary etymology template ({{af}} / {{affix}} / {{compound}} /
    {{prefix}} / {{confix}} of the word's own language, two or more parts; suffix parts such as -ος,
    -ής, -ῐς are dropped): Kaikki Ancient Greek, Sanskrit and Latin dumps (template_members);
  - else a split at a closed first member (SPLIT_PREFIXES: su- / εὐ- 'good', dus- / δυσ- 'bad',
    puru- / πολυ- 'much', sāmi- / ἡμι- 'half'), when the remainder is itself a mapped corpus lemma
    (suáśva- = su- + áśva-, puruṇā́man- = puru- + nā́man-). The privative a(n)- / ἀ(ν)- is never split
    off by form (ἄνεμος, ἀγαθός); it counts only where a template names it;
  - a closed prefix member takes the reviewed lexicon id (PREFIXES: *n̥-, *h₁su-, *dus-, *pélh₁u-,
    *sēmi-); any other member takes the production ids of the same-language corpus lemma it equals
    (the `lemma_ids` the caller passes: lemma key -> ids, built from the loaders' own words), so a member
    is mapped exactly as the word is when it stands alone.

Members are a search layer only. They never replace or join a word's lexeme ids and are never evidence
in the Tier 2 secure check (pie/tier2_secure.py has its own compound rule). The search index stores them
as separate word fields (member_ids, member_groups; scripts/search_corpora.py) and posts them as root
terms: a compound unit is found by its members, and a pair scan can count a compound hit (one word keyed
in both slots) apart from a pair of words.

Languages: Sanskrit (rv, av, sa-ep), Ancient Greek (hom, grc, grc-late) and Latin (lat), the corpora
whose mapping is built from the Kaikki dumps. Latin has no closed prefixes here (in- 'not' and in- 'in'
are one spelling).
"""
from __future__ import annotations

import collections
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data/research/formulas/compound_members"
TEMPLATES = ("af", "affix", "compound", "prefix", "confix")
CORPUS_LANG = {"rv": "sa", "av": "sa", "sa-ep": "sa", "hom": "grc", "grc": "grc", "grc-late": "grc", "lat": "la"}
_N, _SU, _DUS, _POLY, _SEMI = "pie-lex-n", "pie-lex-h1su", "pie-lex-dus", "pie-lex-pelh1u", "pie-lex-sexmi"
_TWO, _THREE, _FOUR = "pie-lex-dwoh1", "pie-lex-treyes", "pie-lex-kwetwores"
# closed prefixes, keyed by key(lang, member) (Sanskrit: the Kaikki romanization's key)
PREFIXES = {
    "grc": {"α": _N, "αν": _N, "ευ": _SU, "εϋ": _SU, "δυσ": _DUS, "πολυ": _POLY, "ημι": _SEMI,
            "τρι": _THREE, "τετρα": _FOUR},
    "sa": {"a": _N, "an": _N, "su": _SU, "dus": _DUS, "dur": _DUS, "duṣ": _DUS, "duḥ": _DUS, "duś": _DUS,
           "puru": _POLY, "sāmi": _SEMI, "dvi": _TWO, "tri": _THREE, "catur": _FOUR, "catuṣ": _FOUR},
    "la": {},
}
# first members split off by form (never the privative), with the shortest remainder allowed; Sanskrit
# keys after skt_key (dvipád- = dvi- + pád-, cátuṣpad- = catuṣ- + pád-)
SPLIT_PREFIXES = {"grc": {"ευ": 4, "δυσ": 4, "πολυ": 4, "ημι": 4},
                  "sa": {"su": 4, "dus": 4, "dur": 4, "duṣ": 4, "duś": 4, "puru": 4, "sāmi": 4, "dvi": 3, "tri": 3,
                         "catuṣ": 3, "catur": 3},
                  "la": {}}
# preverbs and prepositional first members: a preverb + verb (ἐκχέω, prajā́-, uestibulum) is not a compound
# formula, and adding the preverb's adverb to every prefixed verb would key half the Greek verbs twice.
# Keys as key(lang, member); such a member counts for nothing.
PREVERBS = {
    "grc": frozenset("""εκ εξ εν εμ εγ ενι εισ εσ παρα παρ παρε συν συμ συγ συλ συσ συ απο απ αφ επι επ εφ κατα
κατ καθ δια δι ανα αμφι αντι αντ ανθ προ προσ περι υπο υπ υφ υπερ μετα μετ μεθ""".split()),
    "sa": frozenset("""pra vi sam saṃ ā ud ut abhi ni pari upa ava anu adhi apa api prati nis nir niṣ niḥ antar ati
pari parā""".split()),
    "la": frozenset("""ad ab abs a con com co de dis di ex e in im il ir per prae pro re red sub sus trans tra ob
inter intro circum super ante post se""".split()),
}
# combining forms whose base word the member key cannot show (stem allomorphs): member key -> lemma key
COMBINING = {"grc": {"ανδρο": "ανηρ", "ανδρ": "ανηρ", "ανδρει": "ανηρ", "ονυμα": "ονομα"}, "sa": {}, "la": {}}
# lexicon parts of speech whose ids a member does not contribute (adverbs and preverbs, particles,
# pronouns, determiners, conjunctions): the member then counts for nothing
FUNCTION_POS = frozenset({"adv", "particle", "pron", "det", "conj"})


def key(lang: str, s: str) -> str:
    """The comparison key of a corpus lemma or member: Greek grc_key without accents or breathings,
    Sanskrit skt_key (ṇ -> n, as after r / ṣ / puru-), Latin lat_key; no hyphens."""
    from . import formula_search as fs
    s = re.sub(r"<[^>]*>", "", s or "").strip().split("@")[0]
    if lang == "grc":
        return fs.grc_key(s, accents=False)
    if lang == "sa":
        return fs.skt_key(s).replace("ṇ", "n")
    return fs.lat_key(s)


def _is_suffix(part: str) -> bool:
    p = re.sub(r"<[^>]*>", "", part or "").strip()
    return p.startswith("-") and not p.endswith("-")


def template_members(d: dict, lang: str) -> list[list[str]]:
    """The member lists of one wiktextract entry's compound templates (pure)."""
    out = []
    for t in d.get("etymology_templates") or []:
        a = t.get("args") or {}
        if t.get("name") not in TEMPLATES or a.get("1") != lang:
            continue
        parts = [a[k] for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int) if a[k].strip()]
        parts = [re.sub(r"<[^>]*>", "", p).strip() for p in parts if not _is_suffix(p)]
        if len([p for p in parts if p]) >= 2:
            out.append([p for p in parts if p])
    return out


def _roman(d: dict) -> str | None:
    """The entry's romanization, as pie.formula_search.kaikki_entry_links reads it."""
    roman = next((f.get("form") for f in d.get("forms") or [] if "romanization" in (f.get("tags") or [])), None)
    if not roman:
        for h in d.get("head_templates") or []:
            roman = (h.get("args") or {}).get("tr") or None
            if roman:
                break
    return roman


def read_members(path: Path, lang: str) -> tuple[list[dict], dict]:
    """Stream a wiktextract dump (parsed, never executed): (compound records {word, roman, members},
    Devanagari word -> romanization for every Sanskrit entry that has one)."""
    from .formula_search import _deva_key
    out, roman_of = [], {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if lang == "sa" and '"romanization"' in line or '"etymology_templates"' in line:
                d = json.loads(line)
            else:
                continue
            r = _roman(d) if lang == "sa" else None
            if r:
                roman_of.setdefault(_deva_key(d.get("word")), r)
            ms = template_members(d, lang)
            if ms:
                out.append({"word": d.get("word"), "roman": r, "members": ms})
    return out, roman_of


def load_members(lang: str, root: Path = ROOT) -> tuple[list[dict], dict]:
    """read_members with a JSON cache (headwords, romanizations and member strings only)."""
    from .formula_search import KAIKKI
    cache = CACHE / f"{lang}.json"
    if cache.exists():
        d = json.loads(cache.read_text("utf-8"))
        return d["compounds"], d["roman"]
    recs, roman = read_members(Path(root) / KAIKKI[lang], lang)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"_doc": "pie/compound_members.py cache: Kaikki compound templates (headword, "
                                         "romanization, member strings) and, for Sanskrit, Devanagari -> "
                                         "romanization; regenerate by deleting this file.",
                                 "compounds": recs, "roman": roman}, ensure_ascii=False) + "\n", "utf-8")
    return recs, roman


@lru_cache(maxsize=None)
def template_table(lang: str) -> dict:
    """compound key -> member-key lists (closed prefixes as ('id', lexicon id))."""
    from .formula_search import _deva_key
    recs, roman_of = load_members(lang)
    out: dict = collections.defaultdict(list)

    def mkey(m):
        if lang == "sa":
            r = roman_of.get(_deva_key(m.strip("-")))
            return key(lang, r) if r else None
        return key(lang, m)

    for r in recs:
        head = key(lang, r["roman"]) if lang == "sa" else key(lang, r["word"])
        if not head:
            continue
        for parts in r["members"]:
            ms = []
            for m in parts:
                k = mkey(m)
                if k in PREFIXES.get(lang, {}):
                    ms.append(("id", PREFIXES[lang][k]))
                elif k and k not in PREVERBS.get(lang, ()):
                    ms.append(("lemma", COMBINING.get(lang, {}).get(k, k), m))
            out[head].append(ms)
    return dict(out)


def _word_key(lang: str):
    from .formula_search import word_key_for
    return word_key_for(lang)


@lru_cache(maxsize=None)
def _kaikki_resolved(lang: str) -> dict:
    """pie.formula_search.resolve_kaikki over the Kaikki link cache (word key -> (tier, ids))."""
    from . import formula_search as fs
    lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
    return fs.resolve_kaikki(fs.load_kaikki_links(lang), fs.PieIndex(lex), lang, _word_key(lang))


@lru_cache(maxsize=1)
def _function_ids() -> frozenset:
    from .formula_search import load_jsonl
    return frozenset(e["id"] for e in load_jsonl(ROOT / "data/lexicon/lexicon.jsonl") if e.get("pos") in FUNCTION_POS)


def members(corpus: str, lemma: str, lemma_ids: dict) -> frozenset:
    """Member ids of a corpus lemma. lemma_ids: key(lang, lemma) -> production ids of the same-language
    corpora (scripts/search_corpora.py builds it from the loaders' words). Empty for a name, an unknown
    word, a non-compound, or a compound with fewer than two mapped members."""
    lang = CORPUS_LANG.get(corpus)
    if not lang or not lemma or lemma.endswith(" (name)") or lemma.startswith("?"):
        return frozenset()
    k = key(lang, lemma)
    if not k:
        return frozenset()

    function = _function_ids()

    resolved = _kaikki_resolved(lang)

    def ids_of(m):
        if m[0] == "id":
            return frozenset({m[1]})
        v, raw = m[1], m[2]
        if not v or v == k:
            return frozenset()
        ids = lemma_ids.get(v)
        if not ids:          # a member that is no corpus lemma: the word mapping's own Kaikki resolution
            hit = resolved.get(_word_key(lang)(raw.strip("-"))) or resolved.get(_word_key(lang)(raw))
            ids = hit[1] if hit and hit[0] != "kaikki-pseudo" else ()
        return frozenset(i for i in ids if i not in function)

    best = frozenset()
    for ms in template_table(lang).get(k, ()):
        got = [ids_of(m) for m in ms]
        if sum(1 for g in got if g) >= 2:
            best |= frozenset().union(*got)
    if best:
        return best
    for p, shortest in SPLIT_PREFIXES[lang].items():
        rest = k[len(p):]
        rest_ids = frozenset(i for i in lemma_ids.get(rest, ()) if i not in function) if k.startswith(p) else ()
        if len(rest) >= shortest and rest_ids:
            return frozenset({PREFIXES[lang][p]}) | rest_ids
    return frozenset()


def lemma_id_table(lang: str, pairs) -> dict:
    """key(lang, lemma) -> union of ids, from (lemma, ids) pairs of the same-language corpora."""
    out: dict = collections.defaultdict(set)
    for lem, ids in pairs:
        if ids and not lem.endswith(" (name)"):
            k = key(lang, lem)
            if k:
                out[k] |= set(ids)
    return {k: frozenset(v) for k, v in out.items()}
