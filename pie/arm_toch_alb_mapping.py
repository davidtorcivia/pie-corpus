"""Armenian (PROIEL + DMHP), Tocharian A and Old Albanian lemma → PIE tables (Phase 8c, Stage C).

  * **Classical Armenian.** One table, `xcl`, serves both lemmatized corpora:
    PROIEL's Armenian NT (lemmas in PROIEL's Latin transliteration) and the
    Digital Matenagirk Hayots corpus (DMHP: 5th-c. authors, automatic lemmas in
    Armenian script). DMHP lemmas are transliterated into PROIEL's convention
    (`dmhp_lemma`: ու → ow, ռ → r̄, aspirates with ʻ, PROIEL's capitalised
    lemma where one exists: տէր → Tēr), so a PROIEL row and the same DMHP
    lemma share one row and one override. Sources: the kaikki Old Armenian
    chain (formula_search_multi.build_lang_mapping) and Martirosyan's
    *Etymological Dictionary of the Armenian Inherited Lexicon*
    (`martirosyan_entries`: headword → file page, PIE forms of the ETYM
    section, borrowing statements), used as (i) a veto for words it calls
    Iranian (or other) loans, (ii) a tie-breaker for lexicon-reflex hits that
    disagree with the kaikki chain, and (iii) a last source for unmapped
    headwords whose ETYM section states one PIE etymon.
  * **Tocharian A** (`xto`): TITUS 2.0 Sieg & Siegling (NC). Tokens are the
    `<orig>` transliteration, normalised (`toch_norm`: capital Fremdzeichen
    and virama marks, restorations, line-break hyphens). Lemmatizer: the kaikki
    Tocharian A forms tables and headwords, then cautious suffix stripping
    (secondary-case and plural endings) to a unique table form. Mapping: the
    kaikki chain (Proto-Tocharian through the lexicon's reflex lists; the
    Proto-Tocharian pages of the all-languages dump), the lexicon's Tocharian
    A reflexes, and the Tocharian B cognate's chain (`cog` links of either
    dump; Adams' *Dictionary of Tocharian B* is used for checking only).
  * **Old Albanian** (`sqo`): TITUS 2.0 Buzuku 1555, Bogdani 1685, Bardhi
    (Blanchus) 1635 (NC). Each orthography is normalised to modern spelling
    (`alb_norm`), then compared on a Gheg/Tosk-neutral skeleton
    (`alb_skeleton`) with the kaikki Albanian forms tables; a skeleton with
    more than one candidate lemma stays unmapped. Mapping: the kaikki chain
    (Proto-Albanian through the lexicon's reflex lists and the dump's
    Proto-Albanian pages) and the lexicon's Albanian reflexes. No Albanian
    etymological dictionary is local (Orel, Demiraj): kaikki only. Loans
    (Latin, Romance, Greek, Slavic, Turkish) are rejected by the generic
    resolver (`bor`/`der` from a language outside the ancestry).

Nothing under raw/ is executed or imported; dumps and texts are read as JSON
or text. Tables hold dictionary headwords, lemma keys and ids, never text.
"""

from __future__ import annotations

import collections
import glob
import gzip
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from . import formula_search as fs
from . import formula_search_multi as fm

ROOT = fs.ROOT
KD = Path(fm.KD)
MAPPING_DIR = "data/research/formulas/mapping"
ALL_DUMP = "kaikki-all-20261021/raw-wiktextract-data.jsonl.gz"

LICENCES = {
    "proiel": "CC BY-NC-SA 4.0 (PROIEL, Syntacticus release 20230428; research only)",
    "dmhp": "CC BY 4.0 (DMHP, Zenodo 10.5281/zenodo.14841249)",
    "titus-xto": "CC BY-NC-SA 4.0 (TITUS 2.0 Tocharian A; research only)",
    "titus-sqo": "CC BY-NC-SA 4.0 (TITUS 2.0 Old Albanian; research only)",
    "kaikki": "CC BY-SA 4.0 / GFDL (Wiktionary via kaikki.org)",
    "lexicon": "project lexicon (data/lexicon)",
    "martirosyan": "Martirosyan 2010, EDAIL (in copyright; cited for research, no text reproduced)",
    "adams": "Adams 2013, Dictionary of Tocharian B (in copyright; cited for research, no text reproduced)",
    "override": "hand correction (data/research/formulas/mapping-overrides/arm-toch-alb.json)",
}

# ---------------------------------------------------------------- registries (additive)

fm.PROTO_NAMES.setdefault("sqj-pro", "Proto-Albanian")
fm.PROTO_NAMES.setdefault("ine-toc-pro", "Proto-Tocharian")
fm.ANCESTORS.setdefault("sqj-pro", [])
fm.ANCESTORS.setdefault("ine-toc-pro", [])
fm.ANCESTORS.setdefault("xto", ["ine-toc-pro"])
fm.ANCESTORS.setdefault("txb", ["ine-toc-pro"])
fm.ANCESTORS.setdefault("sq", ["sqj-pro"])


# ================================================================ Classical Armenian

ARM = {"ա": "a", "բ": "b", "գ": "g", "դ": "d", "ե": "e", "զ": "z", "է": "ē", "ը": "ə", "թ": "tʻ", "ժ": "ž",
       "ի": "i", "լ": "l", "խ": "x", "ծ": "c", "կ": "k", "հ": "h", "ձ": "j", "ղ": "ł", "ճ": "č", "մ": "m",
       "յ": "y", "ն": "n", "շ": "š", "ո": "o", "չ": "čʻ", "պ": "p", "ջ": "ǰ", "ռ": "r̄", "ս": "s", "վ": "v",
       "տ": "t", "ր": "r", "ց": "cʻ", "ւ": "w", "փ": "pʻ", "ք": "kʻ", "օ": "ō", "ֆ": "f", "և": "ew"}


def arm_translit(s: str) -> str:
    """Armenian script → PROIEL's transliteration (Hübschmann–Meillet with ʻ, r̄, ow);
    lowercased, other characters dropped except spaces and hyphens."""
    out = []
    for c in unicodedata.normalize("NFC", (s or "").lower()):
        if c in ARM:
            out.append(ARM[c])
        elif c in " -":
            out.append(c)
    return "".join(out).strip()


def key_xcl(s: str, loose: bool = False) -> str:
    """formula_search_multi.key_xcl (PROIEL r̄ → ṙ, ow → u, every aspiration mark → ʿ), plus
    Martirosyan's spellings (‘ for ʻ, ɫ for ł) and ō kept (the generic key drops it, so that ōr
    'day' would collide with r)."""
    s = unicodedata.normalize("NFC", (s or "").lower().replace("r̄", "ṙ"))
    s = s.replace("‘", "ʿ").replace("ɫ", "ł").replace("ŕ", "ṙ")
    s = s.replace("ʻ", "ʿ").replace("'", "ʿ").replace("’", "ʿ").replace("ʼ", "ʿ").replace("ow", "u")
    return re.sub(r"[^a-zʿčšžłǰṙēəõō]", "", s)


DMHP_DIR = "armenian-dmhp-matenagirk/src/mh_zenodo_20250208"
_DMHP_W = re.compile(r'<w id="([^"]*)">\s*\n(.*?)\n</w>', re.S)
DMHP_CONTENT = {"N+Com", "A", "V"}
DMHP_NAMES = {"N+Top", "N+Ant"}


@dataclass
class ArmTok:
    text: str          # DMHP text id (file stem)
    locus: str         # DMHP word id (edition page, PDF page, word number)
    lemma: str         # DMHP lemma (column 4, Armenian script)
    pos: str           # DMHP POS (parts joined by '@': proclitic + host)

    @property
    def parts(self) -> list[str]:
        return self.pos.split("@")

    @property
    def content(self) -> bool:
        return any(p in DMHP_CONTENT for p in self.parts)

    @property
    def name(self) -> bool:
        return any(p in DMHP_NAMES for p in self.parts) and not self.content


def dmhp_tokens(root: Path = ROOT) -> list[ArmTok]:
    """DMHP `.vert` tokens (form, normalized form, lemma, lemma variant, POS). Digits, punctuation-only
    tokens and the 20 malformed `(var.` lines are skipped."""
    out = []
    for p in sorted(glob.glob(str(Path(root) / KD / DMHP_DIR / "*.vert"))):
        text = Path(p).name.split("_HYE")[0]
        for m in _DMHP_W.finditer(Path(p).read_text("utf-8")):
            cols = m[2].split("\t")
            if len(cols) < 5:
                continue
            lem = cols[3].strip()
            if not lem or not re.search(r"[Ա-և]", cols[0]):
                continue
            out.append(ArmTok(text, m[1], lem, cols[4].strip()))
    return out


PROIEL_XCL = "raw/daughters/syntacticus-proiel-torot/extract/syntacticus-treebank-data-20230428/proiel/armenian-nt.xml"


def proiel_lemmas(root: Path = ROOT) -> collections.Counter:
    t = (Path(root) / PROIEL_XCL).read_text("utf-8")
    return collections.Counter(m.split("#")[0] for m in re.findall(r'lemma="([^"]*)"', t))


class DmhpLemma:
    """DMHP lemma (Armenian script) → the xcl table's lemma string: PROIEL's lemma when one has the
    same key (case and ow/u spelling ignored), else the lowercase PROIEL-style transliteration."""

    def __init__(self, proiel: collections.abc.Iterable):
        by_key: dict[str, set] = collections.defaultdict(set)
        for lem in proiel:
            by_key[key_xcl(lem)].add(lem)
        self.by_key = {k: sorted(v, key=lambda x: (x != x.lower(), x))[0] for k, v in by_key.items()}

    def __call__(self, lemma: str) -> str:
        lemma = re.sub(r"\s*\(.*$", "", lemma).strip()
        t = arm_translit(lemma)
        return self.by_key.get(key_xcl(t), t)


# ---------------------------------------------------------------- Martirosyan (EDAIL) entries
#
# The text layer (raw/books/text/martirosyan-arm/pNNNN.txt; file page = printed page + 14) has a
# three-line running head (blank, headword, page number in either order), then entries: a head
# paragraph ("aṙnem, 1sg.aor ar-ar-i, … ‘to make; to create’ (Bible+)."), optional ●DIAL /
# ●SEMANTICS sections and an ●ETYM section. An entry is anchored on its first ● marker after the
# previous ●ETYM; its headwords are the head-paragraph lines between the two that start with a word
# followed by a grammatical marker (stem class, case form, aorist, gloss, attestation). Only
# headwords, file pages and the ETYM section's PIE forms / borrowing statements are kept in memory;
# nothing is written out but headword keys and page numbers.

MARTIROSYAN = "raw/books/text/martirosyan-arm"
_M_HEAD = re.compile(r"^\*?([a-zčšžɫłǰṙēəō][a-zčšžɫłǰṙēəōʻ‘\-]*?)\d?(?:\s*\([^)]{0,60}\))?(?=,|\s*:|\s+‘|\s+\(|\s+[a-z]+-stem|\s+or\s)")
_M_STRONG = re.compile(r"(?:-stem|GDSg|GDPl|NPl|AblSg|ISg|1sg\.|3sg\.|aor\.|imper\.|\(Bible|\+\)|‘[^’]{1,60}’)")
_M_PIE = re.compile(r"\*[A-Za-z0-9₀-₉ʰʷĝǵḱk̂ĝʰəh̥̯̥̄́̀ʔ\-()/]+")
M_LOAN = re.compile(r"\b(?:borrowed|loan-?word|a loan\b|an? (?:Iranian|Parthian|Middle Persian|MPers\.|Syriac|Greek|"
                    r"Aramaic|Semitic|Urartian|Caucasian|Kartvelian|Georgian) loan|from Iran\.|from Iranian|"
                    r"from Parthian|from MPers\.|of Iranian origin)", re.I)
M_NOETYM = re.compile(r"^●ETYM (?:No (?:acceptable |convincing |reliable )?etymolog|No etymological attempt|"
                      r"Etymology (?:is )?(?:unknown|uncertain)|Unknown|Of unknown origin)", re.I)


@dataclass
class MEntry:
    heads: list            # headword keys (key_xcl)
    page: int              # file page of the head paragraph
    etym_page: int         # file page of the ETYM marker
    etym: str = field(default="", repr=False)     # ETYM section text (memory only)
    line: int = -1         # index of the ETYM line in the concatenated text

    @property
    def printed(self) -> int:
        return self.page - 14

    @property
    def pie_forms(self) -> list[str]:
        return [f.rstrip(",.;:") for f in _M_PIE.findall(self.etym)]

    @property
    def no_etymology(self) -> bool:
        return bool(M_NOETYM.match(self.etym))

    def loan_statement(self, chars: int = 400) -> str | None:
        """A borrowing statement in the first `chars` characters of the ETYM section, or None."""
        m = M_LOAN.search(self.etym[:chars])
        return m[0] if m else None


def _m_lines(root: Path):
    for p in sorted(glob.glob(str(Path(root) / MARTIROSYAN / "p*.txt"))):
        n = int(Path(p).stem[1:])
        lines = Path(p).read_text("utf-8").split("\n")
        head = 0
        while head < min(4, len(lines)) and (not lines[head].strip() or re.fullmatch(r"\s*\d+\s*", lines[head])
                                             or (head and len(lines[head].split()) == 1 and head < 3)):
            head += 1
        for ln in lines[head:]:
            yield n, ln


def martirosyan_entries(root: Path = ROOT) -> list[MEntry]:
    lines = list(_m_lines(root))
    out, last_etym, i = [], -1, 0
    while i < len(lines):
        n, ln = lines[i]
        if ln.startswith("●"):
            # first marker of a new entry: headwords in the window (last_etym, i)
            heads, page = [], n
            for j in range(last_etym + 1, i):
                pj, lj = lines[j]
                m = _M_HEAD.match(lj)
                if m and _M_STRONG.search(lj[len(m[0]):len(m[0]) + 160] + " " + (lines[j + 1][1] if j + 1 < i else "")[:80]):
                    k = key_xcl(m[1])
                    if len(k) >= 2 and k not in heads:
                        if not heads:
                            page = pj
                        heads.append(k)
            # sections up to and including ETYM
            k = i
            while k < len(lines) and not lines[k][1].startswith("●ETYM"):
                k += 1
                if k < len(lines) and k > i and lines[k][1].startswith("●") and not lines[k][1].startswith(("●DIAL", "●SEM", "●ETYM")):
                    break
            if k >= len(lines):
                break
            e_start = k
            k += 1
            while k < len(lines) and not lines[k][1].startswith("●") and not (
                    _M_HEAD.match(lines[k][1]) and _M_STRONG.search(lines[k][1][:200]) and k > e_start + 2
                    and lines[k][1][:1].islower() and _looks_like_new_head(lines, k)):
                k += 1
            etym = " ".join(l for _, l in lines[e_start:k])
            out.append(MEntry(heads, page, lines[e_start][0], etym, e_start))
            last_etym = e_start
            i = e_start + 1
            continue
        i += 1
    return out


def _looks_like_new_head(lines, k) -> bool:
    """A strong head line followed (before any other ●ETYM) by a ● marker: the next entry starts here."""
    for j in range(k + 1, min(k + 400, len(lines))):
        if lines[j][1].startswith("●"):
            return True
    return False


class MIndex:
    """headword key → Martirosyan entries. Lookup: the detected headwords first; else any line that
    starts with the word followed by ',', ':', '(' or a gloss, taken to the next ETYM section
    (within 150 lines)."""

    def __init__(self, entries: list[MEntry], root: Path = ROOT):
        self.entries = entries
        self.by_key: dict[str, list[MEntry]] = collections.defaultdict(list)
        for e in entries:
            for h in e.heads:
                self.by_key[h].append(e)
        self.starts: dict[str, list[int]] = collections.defaultdict(list)
        for i, (_, ln) in enumerate(_m_lines(root)):
            m = re.match(r"^\*?([a-zčšžɫłǰṙēəō][a-zčšžɫłǰṙēəōʻ‘\-]*?)\d?(?=,|\s*:|\s+‘|\s+\()", ln)
            if m:
                self.starts[key_xcl(m[1])].append(i)
        self.lines = [e.line for e in entries]

    def get(self, lemma: str) -> list[MEntry]:
        for k in dict.fromkeys((key_xcl(lemma), key_xcl(lemma).removesuffix("kʿ"))):
            if self.by_key.get(k):
                return self.by_key[k]
        import bisect
        out = []
        for k in dict.fromkeys((key_xcl(lemma), key_xcl(lemma).removesuffix("kʿ"))):
            for i in self.starts.get(k, []):
                j = bisect.bisect_right(self.lines, i)
                if j < len(self.entries) and self.entries[j].line - i <= 150 and self.entries[j] not in out:
                    out.append(self.entries[j])
            if out:
                break
        return out


# ---------------------------------------------------------------- shared: kaikki reading with hedges and hints

_HEDGE = re.compile(r"^\s*(?:The origin (?:is|in|of the word is) (?:uncertain|unknown|unclear|obscure|disputed)|"
                    r"(?:Of )?(?:uncertain|unknown|unclear|obscure|disputed) (?:origin|etymology)|Uncertain\b|"
                    r"Unclear\b|Unknown\b|Origin (?:is )?(?:uncertain|unknown)|Etymology (?:uncertain|unknown)|"
                    r"[^.]{0,80}\bleaves? the origin(?: of the word)? open|[^.]{0,80}\b(?:does not|do not) record an "
                    r"acceptable etymology|[^.]{0,60}\bconsider the origin of the word unknown|"
                    r"[^.]{0,160}\bof (?:uncertain|unknown|unclear|obscure)(?: further)? origin|"
                    r"[^.]{0,120}\b(?:root|origin|etymology)[^.]{0,40}\b(?:are|is) disputed|"
                    r"[^.]{0,80}\bdetails are uncertain|(?:Probably |Perhaps )?(?:of )?onomatopoeic origin|"
                    r"Disputed\b|Most probably (?:derived )?from a substrate)", re.I)


@dataclass
class KEntry:
    entry: fm.Entry
    hedged: bool                  # the etymology text opens with "uncertain / unknown / left open"
    hints: dict                   # PIE term key → gloss words from the template (id=, t=, 5=)


def _gloss_words(s: str) -> set:
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower())
            if w not in {"the", "and", "with", "from", "for", "into", "something", "someone", "one", "make", "become"}}


def read_kaikki(paths, lang: str, codes=None, keep_forms: bool = True) -> list[KEntry]:
    codes = set(codes or [lang])
    out = []
    for path in [paths] if isinstance(paths, (str, Path)) else paths:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                if d.get("lang_code") not in codes:
                    continue
                e = fm.parse_entry(d, lang, keep_forms)
                hints = {}
                for t in d.get("etymology_templates") or []:
                    a = t.get("args") or {}
                    if t.get("name") in ("root", "inh", "der", "inh+", "der+") and a.get("2") == "ine-pro":
                        words = _gloss_words(" ".join(str(a.get(k) or "") for k in ("id", "t", "gloss", "5")))
                        for k in ("3", "4"):
                            if a.get(k) and words:
                                hints[fs.PieIndex.proto_key(fm._strip_inline(a[k]))] = words
                out.append(KEntry(e, bool(_HEDGE.match(d.get("etymology_text") or "")), hints))
    return out


def _homograph_roots(ids, lexd: dict) -> bool:
    """Two or more root entries of one written form (*h₂er- 'fit' / 'take' / 'speak loudly')."""
    roots = [lexd[i] for i in ids if i in lexd and lexd[i].get("kind") == "root"]
    return len(roots) == len(ids) >= 2 and len({fs.PieIndex.proto_key(r["form"]) for r in roots}) == 1


def disambiguate_roots(ids, hint_words: set, lexd: dict) -> frozenset | None:
    """The one homograph root whose id slug or meaning shares a word with the hint (template gloss,
    the word's own gloss, the dictionary's gloss of the etymon); None if not exactly one."""
    keep = [i for i in ids if hint_words & (_gloss_words(i.split("-", 3)[-1].replace("_", " ")) |
                                            _gloss_words(" ".join(lexd[i].get("meaning") or [])))]
    return frozenset(keep) if len(keep) == 1 else None


def postprocess(lm: fm.LangMapping, kents: list[KEntry], lexd: dict, lang: str, extra_hints=None,
                mixed: bool = False) -> dict:
    """Systematic fixes on a built LangMapping, in place. Returns {key: reason} of dropped or changed keys:
      hedged      every etymological entry of the key opens with "origin uncertain / unknown / left open"
                  (the chain, the lexicon reflex lists and the descendants trees are then all dropped)
      borrowed    every entry of the key is a borrowing (bor / der from outside the ancestry): its
                  lexicon-reflex or descendants-tree link is dropped too
      homograph   ids are homograph roots: kept only if one is singled out by the template gloss, the
                  word's gloss or `extra_hints` (key → words); else dropped
      root-gloss-mismatch  a single root id whose meaning shares no word with the gloss the kaikki template
                  gives for the etymon (Alb. lut 'pray' ← *lew- 'to sound', not the lexicon's *lew- 'dirt')
      mixed-homograph  (mixed=True, for unlemmatized corpora, where a surface form cannot be assigned to one
                  of two homograph entries) the key has an inherited entry and a borrowed or hedged one
                  (Alb. regj 'tan' / regj 'king' < Lat. rēgem)
    """
    K = fm.KEYS[lang]
    by_key: dict[str, list[KEntry]] = collections.defaultdict(list)
    for ke in kents:
        for k in fm.entry_keys(ke.entry, lang):
            by_key[k].append(ke)
    changed = {}
    for k in list(lm.recs):
        r = lm.recs[k]
        ents = by_key.get(k, [])
        # every entry of the key (alternative-form and form-of pages included) must be hedged or borrowed
        if ents and r.path[1:2] and not r.path[1].startswith("form-of:"):
            if all(x.hedged or x.entry.rejected for x in ents) and any(x.hedged for x in ents):
                del lm.recs[k]
                changed[k] = "hedged"
                continue
            if all(x.entry.rejected for x in ents) and r.how in ("lexicon", "desc"):
                del lm.recs[k]
                changed[k] = "borrowed"
                continue
        if mixed and ents and r.path[1:2] and not r.path[1].startswith("form-of:"):
            ety = [x for x in ents if not x.entry.form_of and (x.entry.links or x.entry.roots or x.entry.rejected or x.hedged)]
            if any(x.hedged or x.entry.rejected for x in ety) and any(not (x.hedged or x.entry.rejected) for x in ety):
                del lm.recs[k]
                changed[k] = "mixed-homograph"
                continue
        if all(lexd.get(i, {}).get("kind") == "root" for i in r.ids) and len(r.ids) == 1:
            words = set()
            for x in ents:
                for v in x.hints.values():
                    words |= v
            i = next(iter(r.ids))
            if words and not words & (_gloss_words(i.split("-", 3)[-1].replace("_", " ")) |
                                      _gloss_words(" ".join(lexd[i].get("meaning") or []))):
                del lm.recs[k]
                changed[k] = "root-gloss-mismatch"
                continue
        if _homograph_roots(r.ids, lexd):
            words = set()
            for x in ents:
                for v in x.hints.values():
                    words |= v
                words |= _gloss_words(x.entry.glosses)
            words |= set((extra_hints or {}).get(k, ()))
            keep = disambiguate_roots(r.ids, words, lexd)
            if keep:
                lm.recs[k] = fm.MapRec(k, r.word, keep, r.path, r.how, r.confidence, r.sources + ("homograph-gloss",), r.gloss)
                changed[k] = "homograph-resolved"
            else:
                del lm.recs[k]
                changed[k] = "homograph"
    # form-of and base-word records copied from a dropped key go with it
    dropped = {k for k, v in changed.items() if v != "homograph-resolved"}
    for k in list(lm.recs):
        for step in lm.recs[k].path[1:2]:
            if step.startswith(("form-of:", "base:")) and K(step.split(":", 1)[1].lstrip("√*")) in dropped:
                del lm.recs[k]
                changed[k] = "via-" + changed[K(step.split(":", 1)[1].lstrip("√*"))]
    return changed


# ---------------------------------------------------------------- the xcl table (PROIEL + DMHP)

class _Key:
    """Temporarily replace formula_search_multi's key function for one language."""

    def __init__(self, lang, fn):
        self.lang, self.fn = lang, fn

    def __enter__(self):
        self.old = fm.KEYS.get(self.lang)
        fm.KEYS[self.lang] = self.fn

    def __exit__(self, *a):
        fm.KEYS[self.lang] = self.old


@dataclass
class XclBuild:
    lm: fm.LangMapping
    changed: dict
    mindex: "MIndex"
    kents: list


def m_hints(mindex: "MIndex", key: str) -> set:
    """Gloss words of the PIE etymon(s) Martirosyan's ETYM section opens with ("From PIE *h2er- ‘to fix,
    put together’")."""
    out = set()
    for e in mindex.by_key.get(key, []):
        for g in re.findall(r"\*[^\s‘]+\s+‘([^’]{1,60})’", e.etym[:300]):
            out |= _gloss_words(g)
    return out


def build_xcl(lexicon: list[dict], root: Path = ROOT, idx=None) -> XclBuild:
    idx = idx or fs.PieIndex(lexicon)
    lexd = {e["id"]: e for e in lexicon}
    spec = fm.LANGS["xcl"]
    kents = read_kaikki(Path(root) / KD / spec.dump, "xcl")
    mindex = MIndex(martirosyan_entries(root), root)
    with _Key("xcl", key_xcl):
        protos = fm.ProtoDB(root, codes={"hyx-pro"}, want_desc=["xcl"])
        lm = fm.build_lang_mapping("xcl", lexicon, protos, root=root, entries=[k.entry for k in kents], idx=idx)
        hints = {k: m_hints(mindex, k) for k in lm.recs if _homograph_roots(lm.recs[k].ids, lexd)}
        changed = postprocess(lm, kents, lexd, "xcl", hints)
    return XclBuild(lm, changed, mindex, kents)


def xcl_lemma_keys(lem: str) -> list[str]:
    """Candidate keys of a corpus lemma: the key, the loose key, then the singular of a plurale tantum
    or plural lemma (DMHP mardik → mard, erkinkʻ → erkin) for the table lookup."""
    k = key_xcl(lem)
    out = [k, key_xcl(lem, True)]
    for suf in ("ikʿ", "kʿ", "ik"):
        if k.endswith(suf) and len(k) - len(suf) >= 2:
            out.append(k[: -len(suf)])
    return list(dict.fromkeys(out))


def xcl_rows(b: XclBuild, proiel: collections.Counter, dmhp: dict, gmap: dict) -> list[dict]:
    """Table rows for every PROIEL lemma and every DMHP lemma (as its table string) that maps.
    dmhp: table string → Counter of DMHP (Armenian-script) lemmas."""
    with _Key("xcl", key_xcl):
        lemmas = set(proiel) | set(dmhp)
        toks = [fs.Token("xcl", l, "", "", {}, True, "other") for l in sorted(lemmas)]
        m, recs = fm.corpus_mapping(toks, b.lm, lemma_keys=xcl_lemma_keys, gmap=gmap)
    rows = []
    for lem in sorted(recs):
        r = recs[lem]
        ids = fm._strip_blocked(sorted(r.ids))
        if not ids:
            continue
        lic = {}
        if lem in proiel:
            lic["proiel"] = LICENCES["proiel"]
        if lem in dmhp:
            lic["dmhp"] = LICENCES["dmhp"]
        lic["kaikki"] = LICENCES["kaikki"]
        if r.how == "lexicon" or "lexicon" in r.sources:
            lic["lexicon"] = LICENCES["lexicon"]
        if "homograph-gloss" in r.sources:
            lic["martirosyan"] = LICENCES["martirosyan"]
        row = {"corpus": "xcl", "lang": "xcl", "lemma": lem, "word": r.word, "lex_id": list(ids), "path": list(r.path),
               "how": r.how, "confidence": r.confidence, "sources": list(r.sources),
               "corpora": [c for c, d in (("proiel", proiel), ("dmhp", dmhp)) if lem in d], "licence": lic}
        if lem in dmhp:
            row["dmhp_lemmas"] = sorted(dmhp[lem])
        rows.append(row)
    return rows


# ================================================================ kaikki all-languages dump: proto pages

def all_dump_lines(codes: set, root: Path = ROOT, extract: Path | None = None) -> dict[str, list[dict]]:
    """Entries of the given lang_codes from the all-languages dump (3 GB .gz, scanned once, ≈1–2 min),
    or from an extract made earlier (a directory of <code>.jsonl files)."""
    out: dict[str, list[dict]] = {c: [] for c in codes}
    if extract:
        for c in codes:
            p = Path(extract) / f"{c}.jsonl"
            if p.exists():
                out[c] = [json.loads(l) for l in p.read_text("utf-8").splitlines() if l.strip()]
        return out
    pat = re.compile(r'"lang_code": "(' + "|".join(re.escape(c) for c in sorted(codes)) + r')"')
    with gzip.open(Path(root) / KD / ALL_DUMP, "rt", encoding="utf-8") as fh:
        for line in fh:
            if pat.search(line):
                d = json.loads(line)
                if d.get("lang_code") in codes:
                    out[d["lang_code"]].append(d)
    return out


def add_proto(protos: fm.ProtoDB, code: str, dicts: list[dict], want=()):
    """Proto-language pages (dicts from all_dump_lines) into a ProtoDB, with their descendants trees."""
    want = set(want)
    for d in dicts:
        e = fm.parse_entry(d, code)
        protos.entries[(code, fs.PieIndex.proto_key(e.word))].append(e)
        if want and d.get("descendants"):
            fm._walk_desc(d["descendants"], code, e.word, want, protos.desc)


def _cognate_fill(lm: fm.LangMapping, other: fm.LangMapping, pairs, K, label: str, glosses=None,
                  skip=()) -> int:
    """Keys of `lm` without a mapping take the mapping of a sister-language cognate (kaikki `cog`
    templates in either dump): Tocharian A ← Tocharian B. Only cognates whose own mapping is a chain,
    lexicon or descendants link (not a base word or a pseudo id) and, when `glosses` (lang → key → gloss
    words) is given, whose glosses share a word (A ke 'chance' is not B kaiyye 'cattle'); one per key."""
    n = 0
    for k, ow in pairs:
        if k in lm.recs or not k or k in skip:
            continue
        if glosses is not None and not (glosses[0].get(k, set()) & glosses[1].get(ow, set())):
            continue
        r = other.recs.get(ow)
        if r and r.how in ("chain", "lexicon", "desc", "root"):
            lm.recs[k] = fm.MapRec(k, k, r.ids, (f"{lm.lang}:{k}", f"{label}:{r.word}") + r.path[1:], r.how,
                                   "low" if r.how == "root" else "medium", r.sources + (label,), r.gloss)
            n += 1
    return n


# ================================================================ Tocharian A

def key_toch(s: str, loose: bool = False) -> str:
    """Tocharian (kaikki headwords, TITUS normalised text): lowercase, no hyphens or brackets; loose drops
    vowel length and the ä/a distinction."""
    s = unicodedata.normalize("NFC", (s or "").lower())
    if loose:
        s = fm._nfd_strip(s, keep="̣̂́̇̃").replace("ä", "a")
        s = unicodedata.normalize("NFC", s)
    return re.sub(r"[^a-zäāēīōūṣśṃñṅṭḍṇḷṛḥ]", "", s)


for _c in ("xto", "txb"):
    fm.KEYS.setdefault(_c, key_toch)
fm.LANGS.setdefault("xto", fm.LangSpec("xto", "Tocharian A", "kaikki-tochariana/kaikki.org-dictionary-TocharianA.jsonl",
                                       ("Tocharian A",), desc_codes=("xto",)))
fm.LANGS.setdefault("txb", fm.LangSpec("txb", "Tocharian B", "kaikki-tocharianb/kaikki.org-dictionary-TocharianB.jsonl",
                                       ("Tocharian B",), desc_codes=("txb",)))

TOCH_A = "titus2-tocharian/src/tocharian-ba1d8343a68f6653fa71af24b2562bd4b6cddba5/drafts/tocha/output.xml"


def toch_norm(w: str) -> str | None:
    """One TITUS Tocharian A token (Sieg–Siegling transliteration) → normalised word, or None for
    fragments. Capitals mark the Fremdzeichen (consonant + ä): KA, TA → kä, tä; a capital consonant
    before \\ (virama) or another consonant is the bare consonant; restorations ( ) and [ ] are kept,
    lacunae (_ . / * +) make the token a fragment; digits are verse numbers."""
    w = re.sub(r"\d+", "", w)
    if not w or re.search(r"[_./*+?~^!]", w):
        return None
    w = w.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("\\", "")
    w = w.replace("Ä", "ä").replace("A", "ä").replace("ù", "u").replace("ì", "i")
    w = unicodedata.normalize("NFC", w.lower()).strip("-:;|,")
    if not w or not re.fullmatch(r"[a-zäāēīōūṣśṃñṅṭḍṇḷṛḥʰ̥]+", w):
        return None
    return w


@dataclass
class TochLine:
    ms: str          # manuscript (TITUS div n)
    part: str        # leaf side
    line: str
    words: list      # normalised words (None for fragments)


def toch_lines(root: Path = ROOT) -> list[TochLine]:
    """TITUS Tocharian A `<orig>` lines; German notes and `<foreign>` spans dropped; a word broken at
    the line end ('-') is joined with the first word of the next line of the same leaf side."""
    t = (Path(root) / KD / TOCH_A).read_text("utf-8")
    body = t[t.find("<body"):]
    out: list[TochLine] = []
    ms = part = ""
    for m in re.finditer(r'<div n="([^"]*)"[^>]*type="(manuscript|part)"|<lb n="([^"]*)"\s*/>\s*<choice>\s*<orig>(.*?)</orig>', body, re.S):
        if m[2] == "manuscript":
            ms, part = m[1], ""
            continue
        if m[2] == "part":
            part = m[1]
            continue
        raw = re.sub(r"<foreign[^>]*>.*?</foreign>", " ", m[4], flags=re.S)
        raw = re.sub(r"<[^>]+>", " ", raw).replace("TOCHARIAN//", " ").replace("|RECORD:", " ")
        toks = raw.split()
        if out and out[-1].ms == ms and out[-1].part == part and out[-1].words and out[-1].words[-1] is not None \
                and out[-1].words[-1].endswith("-") and toks:
            first = toch_norm(toks[0])
            prev = out[-1].words[-1].rstrip("-")
            out[-1].words[-1] = (prev + first) if first else None
            toks = toks[1:]
        words = []
        for x in toks:
            if x.endswith("-") and toch_norm(x[:-1]):
                words.append(toch_norm(x[:-1]) + "-")
            else:
                words.append(toch_norm(x))
        out.append(TochLine(ms, part, m[3], words))
    for ln in out:
        ln.words = [w.rstrip("-") if w else w for w in ln.words]
    return out


# secondary-case and plural endings of Tocharian A nouns (added to the oblique) and common verb endings
TOCH_NOUN_END = ("aśśäl", "śśäl", "yo", "ā", "ac", "äṣ", "aṣ", "aṃ", "äṃ", "ṃ", "is", "es", "ṣi", "i", "s", "ñ", "äñ", "aśśi", "śśi")
TOCH_VERB_END = ("äṣ", "äñc", "äñcäṃ", "ñc", "ñcäṃ", "äṃ", "tär", "ntär", "träṃ", "mäṃ", "at", "āt", "ā", "āṣ", "äl", "ālune",
                 "lune", "nt", "ntu", "ṣt", "t", "m", "ṣ", "u", "o", "e")
TOCH_VERB_END = TOCH_VERB_END + ("tsi", "äntsi", "ntsi", "ālyi", "lyi", "l", "ṃ", "ñ", "s", "c", "ac", "tra", "nträ", "imār", "māṃ")
CONTENT_POS = fm.CONTENT_POS


class SuffixLemmatizer:
    """Surface → lemma key(s) by a LangMapping's forms table (exact key, then loose key), then by
    stripping one known ending to reach (a) a table form of a noun/adjective or (b) a verb-root headword
    ('träṅk-'), keeping the result only if exactly one lemma is reached. Unknown forms: '?' + key."""

    def __init__(self, lm: fm.LangMapping, noun_end=(), verb_end=(), min_stem: int = 3, norm=None):
        self.lm, self.K = lm, fm.KEYS[lm.lang]
        self.noun_end = sorted(set(noun_end), key=len, reverse=True)
        self.verb_end = sorted(set(verb_end), key=len, reverse=True)
        self.min_stem = min_stem
        self.norm = norm or (lambda s: s)
        self.level: dict[str, str] = {}
        self.roots = {k for k, pos in lm.pos.items() if "verb" in pos}

    def _table(self, k: str) -> list[str]:
        c = self.lm.forms.get(k)
        if c:
            if k in c:
                return [k]
            return sorted(c, key=lambda x: (-c[x], x))[:3]
        if k in self.lm.recs or k in self.lm.lemma_words:
            return [k]
        return []

    def __call__(self, surface: str) -> str:
        s = self.norm(surface)
        k = self.K(s)
        if not k:
            return "?"
        for i, kk in enumerate((k, self.K(s, True))):
            got = self._table(kk) if i == 0 else [x for x in self._table(kk)]
            if got:
                self.level[k] = "table" if i == 0 else "loose"
                return "|".join(got)
        cands = set()
        for e in self.noun_end:
            if k.endswith(e) and len(k) - len(e) >= self.min_stem:
                for lem in self._table(k[: -len(e)]):
                    if self.lm.pos.get(lem, set()) & {"noun", "adj", "name"}:
                        cands.add(lem)
        if len(cands) == 1:
            self.level[k] = "noun-suffix"
            return cands.pop()
        vc = set()
        for e in self.verb_end:
            if k.endswith(e) and len(k) - len(e) >= self.min_stem:
                b = k[: -len(e)]
                for r in (b, b.rstrip("ä")):
                    if r in self.roots:
                        vc.add(r)
        if len(vc) == 1 and not cands:
            self.level[k] = "verb-suffix"
            return vc.pop()
        self.level[k] = "unknown" if not cands and not vc else "ambiguous"
        return "?" + k


@dataclass
class TochBuild:
    lm: fm.LangMapping
    txb: fm.LangMapping
    changed: dict
    lemmatizer: SuffixLemmatizer
    cognates: int


def _cog_pairs(kents_a, kents_b, Ka, Kb, a_code: str, b_code: str, root: Path, dump_a: str, dump_b: str):
    """(A key, B key) pairs from `cog` templates: A entries citing a B cognate and B entries citing an A one."""
    pairs = []
    for path, me, other, K1, K2, flip in ((dump_a, a_code, b_code, Ka, Kb, False), (dump_b, b_code, a_code, Kb, Ka, True)):
        with open(Path(root) / KD / path, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                for t in d.get("etymology_templates") or []:
                    a = t.get("args") or {}
                    if t.get("name") == "cog" and a.get("1") == other and a.get("2"):
                        x, y = K1(d.get("word") or ""), K2(a["2"])
                        pairs.append((y, x) if flip else (x, y))
    return pairs


def build_xto(lexicon: list[dict], root: Path = ROOT, idx=None, extract=None) -> TochBuild:
    idx = idx or fs.PieIndex(lexicon)
    lexd = {e["id"]: e for e in lexicon}
    protos = fm.ProtoDB(root, codes=set(), want_desc=())
    dumps = all_dump_lines({"ine-toc-pro"}, root, extract)
    add_proto(protos, "ine-toc-pro", dumps["ine-toc-pro"], want=("xto", "txb"))
    out = {}
    for lang in ("txb", "xto"):
        kents = read_kaikki(Path(root) / KD / fm.LANGS[lang].dump, lang)
        lm = fm.build_lang_mapping(lang, lexicon, protos, root=root, entries=[k.entry for k in kents], idx=idx,
                                   strict_homographs=True)
        ch = postprocess(lm, kents, lexd, lang, mixed=True)
        out[lang] = (lm, ch, kents)
    a, b = out["xto"][0], out["txb"][0]
    pairs = _cog_pairs(out["xto"][2], out["txb"][2], key_toch, key_toch, "xto", "txb", root,
                       fm.LANGS["xto"].dump, fm.LANGS["txb"].dump)
    gl = []
    for lang in ("xto", "txb"):
        g: dict[str, set] = collections.defaultdict(set)
        for ke in out[lang][2]:
            for k in fm.entry_keys(ke.entry, lang):
                g[k] |= _gloss_words(ke.entry.glosses)
        gl.append(g)
    # only A words without an etymology of their own take the B cognate's: keys dropped as homographs,
    # hedged or borrowed (by build_lang_mapping's strict homograph rule or by postprocess) are not refilled
    own = {k for ke in out["xto"][2] if ke.entry.links or ke.entry.roots or ke.entry.rejected or ke.hedged
           for k in fm.entry_keys(ke.entry, "xto")}
    n = _cognate_fill(a, b, pairs, key_toch, "cognate-txb", gl, skip=own | set(out["xto"][1]))
    lz = SuffixLemmatizer(a, TOCH_NOUN_END, TOCH_VERB_END)
    return TochBuild(a, b, out["xto"][1], lz, n)


def xto_tokens(b: TochBuild, root: Path = ROOT, lines=None) -> list[fs.Token]:
    """Tocharian A tokens (fragments skipped): unit 'line' = manuscript.side.line, 'leaf' = manuscript.side."""
    toks = []
    for ln in lines or toch_lines(root):
        for w in ln.words:
            if not w:
                continue
            lem = b.lemmatizer(w)
            toks.append(fs.Token("xto", lem, w, f"A {ln.ms} {ln.part}{ln.line}",
                                 {"line": f"{ln.ms}.{ln.part}.{ln.line}", "leaf": f"{ln.ms}.{ln.part}"},
                                 b.lm.is_content(lem), "other"))
    return toks


def lemma_rows(corpus: str, lang: str, recs: dict, lic: dict) -> list[dict]:
    rows = []
    for lem in sorted(recs):
        r = recs[lem]
        ids = fm._strip_blocked(sorted(r.ids))
        if not ids:
            continue
        l2 = dict(lic)
        if r.how == "lexicon" or "lexicon" in r.sources:
            l2["lexicon"] = LICENCES["lexicon"]
        rows.append({"corpus": corpus, "lang": lang, "lemma": lem, "word": r.word, "lex_id": list(ids),
                     "path": list(r.path), "how": r.how, "confidence": r.confidence, "sources": list(r.sources),
                     "licence": l2})
    return rows


def build_xto_tables(lex, gmap, out: dict, samples: dict, root: Path, extract, write_rows):
    import time
    t0 = time.time()
    b = build_xto(lex, root, extract=extract)
    toks = xto_tokens(b, root)
    m, recs = fm.multi_lemma_mapping(toks, b.lm, gmap)
    rows = lemma_rows("xto", "xto", recs, {"titus-xto": LICENCES["titus-xto"], "kaikki": LICENCES["kaikki"]})
    write_rows("xto", rows)
    table = fm.apply_table_overrides("xto", {r["lemma"]: tuple(r["lex_id"]) for r in rows})
    cont = collections.Counter(t.lemma for t in toks if t.content)
    known = collections.Counter(t.lemma for t in toks if t.content and not t.lemma.startswith("?"))
    out["xto"] = {"rows": len(rows), "tokens": len(toks), "changed_by_rule": dict(collections.Counter(b.changed.values())),
                  "cognate_fills": b.cognates, "content_incl_unknown": _tally(cont, table),
                  "content_known_lemma": _tally(known, table),
                  "lemmatizer_levels_by_type": dict(collections.Counter(b.lemmatizer.level.values()))}
    surf = collections.Counter((t.surface, t.lemma) for t in toks if t.content)
    samples["xto"] = (surf, table, {r["lemma"]: r for r in rows})
    print(f"xto: {len(rows)} rows; {len(toks)} tokens; content mapped {out['xto']['content_incl_unknown']['share']:.3f} "
          f"({time.time() - t0:.0f}s)")


def _tally(counts, table) -> dict:
    tot = sum(counts.values())
    mapped = sum(n for t, n in counts.items() if t in table)
    return {"content_tokens": tot, "content_tokens_mapped": mapped, "share": round(mapped / max(1, tot), 4),
            "content_types": len(counts), "content_types_mapped": sum(1 for t in counts if t in table)}


# ================================================================ Old Albanian

def key_sq(s: str, loose: bool = False) -> str:
    """Albanian (kaikki headwords and forms, lexicon reflexes): the part before a comma, lowercased;
    a multi-word form ('kam punuar') gives no key; loose drops ë and ç/q, ll/rr doubling."""
    s = unicodedata.normalize("NFC", (s or "").split(",")[0].split(";")[0].strip().lower().strip("*-"))
    if " " in s:
        return ""
    if loose:
        s = s.replace("ë", "e").replace("ç", "c")
    return re.sub(r"[^a-zëç]", "", s)


fm.KEYS.setdefault("sq", key_sq)
fm.LANGS.setdefault("sq", fm.LangSpec("sq", "Albanian", "kaikki-albanian/kaikki.org-dictionary-Albanian.jsonl",
                                      ("Albanian", "Old Albanian", "Gheg Albanian", "Tosk Albanian"),
                                      desc_codes=("sq", "aln", "als")))

ALB_DIR = "titus2-other-ie/src/other-ie-d1d7e03b290e1f9436ca666b52518108318d9c23"
ALB_TEXTS = {"buzuku": "buzuk", "bogdani": "bogda", "bardhi": "blanc"}


def _alb_common(s: str) -> str:
    s = re.sub(r"(.)\1+", r"\1", s)                       # doubled letters (baam, ξξ handled before)
    return s


def alb_norm(w: str, text: str) -> str:
    """Old orthography → approximately modern (Gheg) spelling, per text. Buzuku 1555: ſ s/sh, ћ q/gj,
    ξ th/dh, ɣ y/u, ɛ z, ɿ r, gñ/ñ/gn nj, ch/c(a o u) k, final -eh ë. Bogdani 1685 and Bardhi 1635
    (Italian-based): sc(e i) sh, ch k (chi qi), kj q, gi+vowel gj, gn nj, ξξ th, ξ dh, λ ll, ü y, è ë.
    The skeleton (alb_skeleton) absorbs the remaining ambiguity (s/sh, th/dh, r/rr, q/gj)."""
    s = unicodedata.normalize("NFC", w.lower())
    s = s.replace("p̱", "per").replace("̱", "").replace("̅", "").replace("̷", "").replace("·", "")
    if text == "buzuku":
        s = s.replace("ſ", "s").replace("ћ", "q").replace("ξ", "th").replace("ɣ", "y").replace("ɛ", "z")
        s = s.replace("ʒ", "x").replace("Ʒ", "x").replace("ƹ", "zh").replace("ɿ", "r").replace("₡", "c")
        s = s.replace("gñ", "nj").replace("ñ", "nj").replace("gn", "nj").replace("ẽ", "ë").replace("ã", "â")
        s = s.replace("õ", "o").replace("ũ", "u").replace("ð", "dh")
        s = re.sub(r"ch", "k", s)
        s = re.sub(r"c(?=[aou]|$|[^aeiouy])", "k", s)
        s = re.sub(r"eh$", "ë", s)
        s = re.sub(r"h$", "", s)
    else:
        s = s.replace("ξξ", "th").replace("ξ", "dh").replace("λ", "ll").replace("ɛ", "z").replace("ü", "y")
        s = s.replace("ɣɣ", "y").replace("ɣ", "y")
        s = s.replace("è", "ë").replace("ò", "o").replace("ù", "u").replace("à", "a").replace("ì", "i").replace("æ", "e")
        s = re.sub(r"sci(?=[aou])", "sh", s)
        s = s.replace("sc", "sh")
        s = re.sub(r"chi(?=[aou])", "q", s)              # chiofte = qoftë; chie- = qie- (chieλ = qiell)
        s = re.sub(r"ch(?=[ei])", "q", s)
        s = s.replace("ch", "k").replace("kj", "q")
        s = re.sub(r"gi(?=[aeouë])", "gj", s)
        s = re.sub(r"gi(?=[^aeiouyëj])", "gji", s)
        s = re.sub(r"gh(?=[ie])", "gj", s)
        s = s.replace("gn", "nj")
        s = re.sub(r"c(?=[aou]|$|[^aeiouyë])", "k", s)
    return re.sub(r"[^a-zëçâêîôû]", "", s)


def alb_skeleton(s: str) -> str:
    """A Gheg/Tosk- and orthography-neutral key: sh→s, zh→z, th/dh→8, gj/q/ç→Q, nj→N, ll→L, rr→r,
    xh→x, y/u not merged; vowels ë/e and the nasal vowels unified, a final e/ë dropped, doubled letters
    single."""
    s = unicodedata.normalize("NFC", (s or "").lower())
    s = s.replace("â", "a").replace("ê", "e").replace("î", "i").replace("ô", "o").replace("û", "u")
    s = s.replace("sh", "s").replace("zh", "z").replace("xh", "x").replace("th", "8").replace("dh", "8")
    s = s.replace("gj", "Q").replace("q", "Q").replace("ç", "Q").replace("nj", "N").replace("ll", "L")
    s = s.replace("ë", "e")
    s = re.sub(r"(.)\1+", r"\1", s)
    s = re.sub(r"e$", "", s) if len(s) > 2 else s
    return re.sub(r"[^a-z8QNL]", "", s)


def gheg_variants(form: str) -> list[str]:
    """A standard (Tosk-based) form and its regular Gheg counterparts: intervocalic r ↔ n (rhotacism:
    verë / venë), ua → ue (grua / grue), participles -uar → -ue/-uem, -ur → -un/-unë."""
    out = {form}
    if re.search(r"[aeiouyë]r[aeiouyë]", form):
        out.add(re.sub(r"(?<=[aeiouyë])r(?=[aeiouyë])", "n", form))
    if "ua" in form:
        out.add(form.replace("ua", "ue"))
    if form.endswith("uar"):
        out |= {form[:-3] + "ue", form[:-3] + "uem"}
    if form.endswith("ur"):
        out |= {form[:-2] + "un", form[:-2] + "unë"}
    return sorted(out)


# Frequent Old Albanian forms (after alb_norm) that the forms tables get wrong: function words (None: left
# unmapped), Gheg forms of jam 'be' and kam 'have', and Hyj 'God' (no kaikki entry; the key hyj is the verb
# 'enter'). Checked against the texts' usage (Buzuku, Bogdani, Bardhi).
ALB_FORMS = {
    **{w: None for w in ("e", "të", "te", "en", "në", "ne", "per", "për", "qi", "më", "me", "së", "se", "hi", "i", "y",
                         "ai", "aj", "si", "endë", "ende", "endee", "edhe", "na", "por", "mos", "ata", "ato", "tue",
                         "ti", "tuu", "iy", "ju", "enbë", "mbë", "mbe", "tii", "nuke", "nukë", "tine", "atë", "një",
                         "nji", "nje", "o", "as", "em", "kus", "kush", "maa", "ma", "ender", "nder", "ndër", "enfill",
                         "pa", "paa", "nah", "atah", "ate", "tij", "saj", "u", "ky", "kjo", "ajo", "atij", "asaj",
                         "hyj", "hyji", "hyjit", "hyjn", "hj", "jezy", "iezy", "jesu", "iesu", "kristi", "kriskti",
                         "krishti", "krishtit")},
    "anste": "jam", "anstë": "jam", "anshtë": "jam", "ashtë": "jam", "qenë": "jam", "qanë": "jam", "kenë": "jam",
    "klene": "jam", "kjenë": "jam", "qane": "jam", "qene": "jam", "janë": "jam", "jane": "jam",
    "qis": "kam", "kish": "kam", "kisht": "kam", "kaa": "kam", "ka": "kam", "kanë": "kam", "kane": "kam",
    "thom": "them", "thotë": "them", "flit": "flas", "flet": "flas", "këtë": None, "ketë": None, "kete": None,
    "kenë": "jam", "kene": "jam", "gjallë": "gjallë", "qall": None, "bëhet": "bëj", "bahet": "bëj", "vërtet": None,
    "herre": "herë", "herra": "herë", "here": "herë",
}


class AlbLemmatizer:
    """Old Albanian surface → kaikki lemma key: normalise the orthography (alb_norm), take the skeleton,
    look it up among the skeletons of every kaikki form and headword (and their Gheg variants); a
    skeleton that several lemmas share stays unmapped ('?' + skeleton)."""

    def __init__(self, lm: fm.LangMapping, min_len: int = 3):
        self.lm = lm
        self.exact: dict[str, set] = collections.defaultdict(set)
        self.index: dict[str, set] = collections.defaultdict(set)
        for f, c in list(lm.forms.items()) + [(k, {k: 1}) for k in lm.lemma_words]:
            for v in gheg_variants(f):
                self.exact[v] |= set(c)
                sk = alb_skeleton(v)
                if len(sk) >= min_len:
                    self.index[sk] |= set(c)
        self.level: dict[str, str] = {}

    def __call__(self, surface: str, text: str) -> str:
        n = alb_norm(surface, text)
        sk = alb_skeleton(n)
        if n in ALB_FORMS:
            self.level[sk] = "fixed"
            return ALB_FORMS[n] or "?" + sk
        got = self.exact.get(n, set())
        if len(got) == 1:
            self.level[sk] = "exact"
            return next(iter(got))
        if not got:
            got = self.index.get(sk, set())
            if len(got) == 1:
                self.level[sk] = "skeleton"
                return next(iter(got))
        self.level[sk] = "ambiguous" if got else "unknown"
        return "?" + sk


@dataclass
class AlbUnit:
    text: str
    locus: str
    words: list


def alb_units(root: Path = ROOT) -> list[AlbUnit]:
    """Buzuku and Bogdani paragraphs (line breaks marked break="no" joined; Latin-tagged spans dropped);
    Bardhi: the Albanian <form> of each dictionary entry."""
    out = []
    for text, d in ALB_TEXTS.items():
        t = (Path(root) / KD / ALB_DIR / d / "output.xml").read_text("utf-8")
        body = t[t.find("<body"):]
        if text == "bardhi":
            for i, m in enumerate(re.finditer(r"<form>(.*?)</form>", body, re.S)):
                out.append(AlbUnit(text, f"Bardhi entry {i + 1}", fm._WORDS.findall(re.sub(r"<[^>]+>", " ", m[1]))))
            continue
        body = re.sub(r'<(\w+)[^>]*xml:lang="(?:lat|ita)[^"]*"[^>]*>.*?</\1>', " ", body, flags=re.S)
        body = re.sub(r"-?\s*<lb[^>]*break=\"no\"[^>]*/>\s*", "", body)
        for m in re.finditer(r'<p [^>]*?xml:id="([^"]*)"[^>]*>(.*?)</p>', body, re.S):
            txt = re.sub(r"<[^>]+>", " ", m[2])
            out.append(AlbUnit(text, f"{text} {m[1]}", re.findall(r"[^\W\d_]+(?:[̷̱̅][^\W\d_]*)?", txt)))
    return out


@dataclass
class AlbBuild:
    lm: fm.LangMapping
    changed: dict
    lemmatizer: AlbLemmatizer


def build_sqo(lexicon: list[dict], root: Path = ROOT, idx=None, extract=None) -> AlbBuild:
    idx = idx or fs.PieIndex(lexicon)
    lexd = {e["id"]: e for e in lexicon}
    protos = fm.ProtoDB(root, codes=set(), want_desc=())
    dumps = all_dump_lines({"sqj-pro"}, root, extract)
    add_proto(protos, "sqj-pro", dumps["sqj-pro"], want=("sq", "aln", "als"))
    kents = read_kaikki(Path(root) / KD / fm.LANGS["sq"].dump, "sq")
    lm = fm.build_lang_mapping("sq", lexicon, protos, root=root, entries=[k.entry for k in kents], idx=idx,
                               strict_homographs=True)
    ch = postprocess(lm, kents, lexd, "sq", mixed=True)
    return AlbBuild(lm, ch, AlbLemmatizer(lm))


def sqo_tokens(b: AlbBuild, root: Path = ROOT, units=None) -> list[fs.Token]:
    toks = []
    for u in units or alb_units(root):
        for w in u.words:
            lem = b.lemmatizer(w, u.text)
            toks.append(fs.Token("sqo", lem, w.lower(), u.locus, {"paragraph": u.locus, "text": u.text},
                                 b.lm.is_content(lem) and not lem.startswith("?") or (lem.startswith("?") and len(lem) > 4),
                                 "other"))
    return toks


def build_sqo_tables(lex, gmap, out: dict, samples: dict, root: Path, extract, write_rows):
    import time
    t0 = time.time()
    b = build_sqo(lex, root, extract=extract)
    toks = sqo_tokens(b, root)
    m, recs = fm.multi_lemma_mapping(toks, b.lm, gmap)
    rows = lemma_rows("sqo", "sq", recs, {"titus-sqo": LICENCES["titus-sqo"], "kaikki": LICENCES["kaikki"]})
    write_rows("sqo", rows)
    table = fm.apply_table_overrides("sqo", {r["lemma"]: tuple(r["lex_id"]) for r in rows})
    res = {"rows": len(rows), "tokens": len(toks), "changed_by_rule": dict(collections.Counter(b.changed.values())),
           "lemmatizer_levels_by_type": dict(collections.Counter(b.lemmatizer.level.values()))}
    for text in ALB_TEXTS:
        tt = [t for t in toks if t.units["text"] == text]
        res[text] = {"tokens": len(tt),
                     "content_incl_unknown": _tally(collections.Counter(t.lemma for t in tt if t.content), table),
                     "content_known_lemma": _tally(collections.Counter(t.lemma for t in tt if t.content and not t.lemma.startswith("?")), table)}
    res["all"] = {"content_incl_unknown": _tally(collections.Counter(t.lemma for t in toks if t.content), table),
                  "content_known_lemma": _tally(collections.Counter(t.lemma for t in toks if t.content and not t.lemma.startswith("?")), table)}
    out["sqo"] = res
    surf = collections.Counter((t.surface, t.lemma) for t in toks if t.content)
    samples["sqo"] = (surf, table, {r["lemma"]: r for r in rows})
    print(f"sqo: {len(rows)} rows; {len(toks)} tokens; content mapped {res['all']['content_incl_unknown']['share']:.3f} "
          f"({time.time() - t0:.0f}s)")
