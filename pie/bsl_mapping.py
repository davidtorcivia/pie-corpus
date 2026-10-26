"""Balto-Slavic lemmatizers and lemma → PIE tables for the round-4 corpora (Phase 8c, Stage C).

Corpora (all unlemmatized):
  vuk      Vuk Karadžić, Srpske narodne pjesme (sr.wikisource; Serbian Cyrillic, ijekavian, Vuk's orthography)
  byliny   Kirsha Danilov / Rybnikov pt. I / Hilferding (ru.wikisource) and the archive.org OCR of
           Hilferding 1896-1900, Kireevsky 1860-74, Rybnikov 1861-67 (pre-reform orthography)
  dainos   Lithuanian dainos: Rhesa, Nesselmann, Schleicher, Leskien-Brugmann, Bartsch, Juškevič (OCR,
           19th-c. Prussian-Lithuanian and Polish-style spellings, facing German in several editions)
  ccmh     the CCMH Old Church Slavonic source corpus (7-bit transliteration; Marianus, Zographensis,
           Assemanianus, Savvina kniga, Suprasliensis)

This module gives
  * registry entries (setdefault: nothing in formula_search_multi changes) and word keys for
    Serbo-Croatian (`key_sh`: Cyrillic → Gaj Latin, tone marks off), Russian (`key_ru`: stress off,
    ё → е, pre-reform ѣ і ѳ ѵ and final ъ normalised) and Lithuanian (`key_lt`: tone marks off,
    ą č ę ė į š ų ū ž kept; the loose key drops these too);
  * the language mappings: kaikki entries resolved through formula_search_multi's chain / desc /
    lexicon / form-of / base steps, with three Balto-Slavic additions:
      - Russian chains through Old East Slavic (ru → orv → sla-pro) by loading the orv dump as an
        intermediate stage;
      - loan vetoes at the proto level: a Proto-Slavic / Proto-Balto-Slavic / Proto-Baltic page that
        names a non-ancestral source (fm 'disputed': *rajь < Iranian beside *reh₁ís), a page whose
        etymology text says borrowed / loan / semantic loan from Iranian, Scythian, Turkic, Germanic,
        Gothic …, and the explicit LOAN_PROTO list (Derksen's loan verdicts, *bogъ first) are rejected,
        so every daughter word inherited from them stays unmapped;
      - daughter entries with an alternative foreign etymology ('disputed') or an etymology text that
        calls the etymology unknown are rejected as in the Celtic tables;
    and Derksen's Slavic and Balto-Slavic dictionaries (`derksen_slavic_entries`,
    `derksen_baltic_entries`: headword, daughter forms, PIE line, loan statement, printed page) as a
    cross-check and as a last source for Lithuanian headwords (facts only: headword ↔ PIE id);
  * lemmatizers: surface → lemma key string ('a|b' for several candidates, '?' + loose key when
    unknown) through the kaikki form tables, with edition-specific spelling normalisation tried in
    order after the form as written (Vuk's jotation and elisions, ijekavian long endings; pre-reform
    and dialect Russian endings; Old Lithuanian sz/cz/ż/w spellings, OCR accent debris, diminutives,
    preverbs; CCMH transliteration → Cyrillic and the TOROT (form, lemma) pairs for OCS);
  * corpus readers (`vuk_units`, `byliny_units`, `dainos_units`, `ccmh_units`) that yield
    (locus, units, text) like formula_search_multi.dainas_units, with the line filters stated there.

A suppletive form (Ru. шёл → идти, люди → человек; SCr. išao → ići, ljudi → čovjek) never inherits
its lemma's etymology (SUPPLETIVE patterns plus a first-letter check on form-table links).

Nothing under raw/ is executed or imported; dumps and texts are read as JSON or text.
Outputs hold dictionary headwords, lemma keys and ids, never corpus text.
"""

from __future__ import annotations

import collections
import gzip
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import formula_search as fs
from . import formula_search_multi as fm

ROOT = fs.ROOT
KD = fm.KD
SPLIT = "kaikki-all-20261021/split"
ALL_DUMP = "kaikki-all-20261021/raw-wiktextract-data.jsonl.gz"
SPLIT_FILES = {"sh": "serbo-croatian-trimmed.jsonl", "ru": "russian-trimmed.jsonl"}

# ---------------------------------------------------------------- keys

_SR_LAT = dict(zip("абвгдђежзијклљмнњопрстћуфхцчџш",
                   ["a", "b", "v", "g", "d", "đ", "e", "ž", "z", "i", "j", "k", "l", "lj", "m", "n", "nj", "o",
                    "p", "r", "s", "t", "ć", "u", "f", "h", "c", "č", "dž", "š"]))
_KEEP_SH = {"c": "̌́", "s": "̌", "z": "̌"}


def key_sh(s: str, loose: bool = False) -> str:
    """Serbo-Croatian: Cyrillic → Gaj Latin, lowercase, tone and length marks off (č ć š ž đ kept).
    loose: also đ → dž (ć and č stay apart: Vuk's ћу 'I will' is not чу 'hear')."""
    s = unicodedata.normalize("NFD", (s or "").lower().strip("*-"))
    s = unicodedata.normalize("NFD", "".join(_SR_LAT.get(c, c) for c in s))
    out, base = [], ""
    for c in s:
        if unicodedata.combining(c):
            if c in _KEEP_SH.get(base, ""):
                out.append(c)
            continue
        base = c
        out.append(c)
    s = unicodedata.normalize("NFC", "".join(out))
    if loose:
        s = s.replace("đ", "dž")
    return re.sub(r"[^a-zčćšžđ]", "", s)


_RU_OLD = {"ѣ": "е", "і": "и", "ї": "и", "ѳ": "ф", "ѵ": "и", "ё": "е", "ѐ": "е", "ѝ": "и", "є": "е"}


def key_ru(s: str, loose: bool = False) -> str:
    """Russian: lowercase, stress marks off, ё → е, pre-reform ѣ і ѳ ѵ → е и ф и, word-final ъ off.
    loose: also й → и and ъ, ь off."""
    s = (s or "").lower().strip("*-")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c) or c == "̆")
    s = unicodedata.normalize("NFC", s)
    s = "".join(_RU_OLD.get(c, c) for c in s)
    s = re.sub(r"[^а-яй]", "", s.replace("ё", "е"))
    s = s[:-1] if s.endswith("ъ") and len(s) > 1 else s
    if loose:
        s = s.replace("й", "и").replace("ъ", "").replace("ь", "")
    return s


def key_lt(s: str, loose: bool = False) -> str:
    """Lithuanian: lowercase, tone marks (acute, grave, tilde) off; ą č ę ė į š ų ū ž y kept.
    loose: every diacritic off (OCR that lost ogoneks and dots)."""
    s = unicodedata.normalize("NFD", (s or "").lower().strip("*-"))
    out, base = [], ""
    for c in s:
        if unicodedata.combining(c):
            if loose:
                continue
            if c == "̨" or c == "̌" or (c == "̄" and base == "u") or (c == "̇" and base == "e"):
                out.append(c)
            continue
        base = c
        out.append(c)
    s = unicodedata.normalize("NFC", "".join(out))
    return re.sub(r"[^a-ząčęėįšųūž]", "", s)


# ---------------------------------------------------------------- registry (additive)

fm.ANCESTORS.setdefault("sh", ["cu", "sla-pro", "ine-bsl-pro"])       # cu: Church Slavonicisms (see _intra_family)
fm.ANCESTORS.setdefault("ru", ["orv", "cu", "sla-pro", "ine-bsl-pro"])
fm.ANCESTORS.setdefault("lt", ["bat-pro", "ine-bsl-pro"])
fm.LANGS.setdefault("sh", fm.LangSpec("sh", "Serbo-Croatian", f"{SPLIT}/{SPLIT_FILES['sh']}", ("Serbo-Croatian",),
                                      desc_codes=("sh", "sr", "hr", "bs")))
fm.LANGS.setdefault("ru", fm.LangSpec("ru", "Russian", f"{SPLIT}/{SPLIT_FILES['ru']}", ("Russian",),
                                      script="cyrillic", desc_codes=("ru",)))
fm.LANGS.setdefault("lt", fm.LangSpec("lt", "Lithuanian", "kaikki-lithuanian/kaikki.org-dictionary-Lithuanian.jsonl",
                                      ("Lithuanian", "Old Lithuanian"), desc_codes=("lt", "olt")))
fm.KEYS.setdefault("sh", key_sh)
fm.KEYS.setdefault("ru", key_ru)
fm.KEYS.setdefault("lt", key_lt)

ORV_DUMP = "kaikki-oldeastslavic/kaikki.org-dictionary-OldEastSlavic.jsonl"


def ensure_split(lang: str, root: Path = ROOT) -> Path:
    """The trimmed per-language cut of the kaikki all-languages dump (word, pos, forms, etymology,
    senses' glosses/form_of/tags, loan categories), written next to the other split files when
    missing. The dump is read as gzip JSON lines; nothing in it is executed."""
    root = Path(root)
    p = root / KD / SPLIT / SPLIT_FILES[lang]
    if p.exists():
        return p
    keep = ("word", "pos", "lang", "lang_code", "forms", "etymology_number", "etymology_templates",
            "etymology_text", "head_templates")
    cat_re = re.compile(r"borrowed|derived from|inherited from|learned|calque|semantic loan|unknown etymology", re.I)
    tag = f'"lang_code": "{lang}"'
    tmp = p.with_suffix(".part")
    with gzip.open(root / KD / ALL_DUMP, "rt", encoding="utf-8") as f, open(tmp, "w", encoding="utf-8") as out:
        for line in f:
            if tag not in line:
                continue
            d = json.loads(line)
            if d.get("lang_code") != lang:
                continue
            r = {k: d[k] for k in keep if k in d}
            r["senses"] = [{k: s[k] for k in ("glosses", "form_of", "alt_of", "tags") if k in s}
                           for s in d.get("senses") or []]
            r["categories"] = [c for c in d.get("categories") or [] if cat_re.search(c)]
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.rename(p)
    return p


# ---------------------------------------------------------------- loan vetoes

# Proto-forms whose daughters are loans (or whose etymology is unknown) per Derksen, given with the
# printed page; matched on PieIndex.proto_key. A daughter word inherited from them stays unmapped.
LOAN_PROTO = {
    "sla-pro": {
        "bogъ": "Derksen EDSIL p. 49 (*bogъ): usually considered a borrowing from Iranian; no Winter's law",
        "bogatъ": "Derksen EDSIL p. 49 (*bogatъ, from *bogъ, an Iranian loan)",
        "ubogъ": "Derksen EDSIL p. 49 (*bogъ family, an Iranian loan)",
        "nebogъ": "Derksen EDSIL p. 49 (*bogъ family, an Iranian loan)",
        "božьjь": "Derksen EDSIL p. 49 (*bogъ family, an Iranian loan)",
        "rajь": "kaikki *rajь: probably borrowed from Iranian (*raHíš)",
        "toporъ": "kaikki *toporъ: borrowed from Iranian (Old Persian *tapara-)",
        "sobaka": "kaikki *sobaka: borrowed from Middle Iranian *sabā́ka-",
        "kъnędzь": "kaikki *kъnędzь: from Proto-Germanic *kuningaz",
        "xlěbъ": "kaikki *xlěbъ: borrowed from Gothic hlaifs",
        "šelmъ": "kaikki *šelmъ: borrowed from Proto-West Germanic *helm",
        "pьsъ": "kaikki *pьsъ: etymology unknown",
    },
}

_LOAN_TEXT = re.compile(
    r"(?<!not )(?<!no )(?:borrow\w*|loan\w*|semantic loan|calque\w*)\b[^.;]{0,60}?\b(?:from|of)\b[^.;]{0,40}?"
    r"(?:iranian|scythian|sarmatian|alanian|persian|avestan|indo-iranian|turkic|turkish|tatar|mongol\w*|"
    r"germanic|gothic|norse|german|latin|greek|romance|finnic|uralic|hungarian|chuvash|bulgar|khazar)", re.I)
_UNKNOWN_TEXT = re.compile(r"^\s*(?:unknown|uncertain|unclear|obscure|of (?:unknown|uncertain|unclear|obscure) "
                           r"origin)|etymology (?:is )?(?:unknown|uncertain|unclear|obscure)", re.I)


def proto_vetoes(root: Path = ROOT) -> dict[tuple[str, str], str]:
    """(proto code, proto_key) → reason, for Proto-Slavic, Proto-Balto-Slavic and Proto-Baltic pages
    whose etymology text says loan / borrowed from a non-ancestral language, or unknown etymology,
    plus LOAN_PROTO."""
    out = {}
    for code in ("sla-pro", "ine-bsl-pro", "bat-pro"):
        with open(Path(root) / KD / fm.PROTO_DUMPS[code], encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                if d.get("lang_code") not in (None, code):
                    continue
                t = d.get("etymology_text") or ""
                k = fs.PieIndex.proto_key(d.get("word") or "")
                if _LOAN_TEXT.search(t):
                    out.setdefault((code, k), "loan per etymology text")
                elif _UNKNOWN_TEXT.search(t):
                    out.setdefault((code, k), "etymology unknown per etymology text")
                for tm in d.get("etymology_templates") or []:
                    a = tm.get("args") or {}
                    if tm.get("name") == "sl" and a.get("1") == code and a.get("2") not in fm.ANCESTORS.get(code, []):
                        out.setdefault((code, k), f"semantic loan from {a.get('2')}")
    for code, rows in LOAN_PROTO.items():
        for w, why in rows.items():
            out[(code, fs.PieIndex.proto_key(w))] = why
    return out


OVERRIDE_FILE = "data/research/formulas/mapping-overrides/balto-slavic-new.json"


def key_rows(root: Path = ROOT) -> list[dict]:
    """The 'key' rows of the override file: {"lang", "key", "lex_id", "note"} — a daughter headword
    (sh, ru, lt, cu) whose mapping the dictionaries correct or reject; the correction also reaches
    every word mapped through it (base-word chains, preverb compounds, form-of entries)."""
    p = Path(root) / OVERRIDE_FILE
    return json.loads(p.read_text("utf-8")).get("key", []) if p.exists() else []


def apply_key_rows(lm: fm.LangMapping, rows: list[dict]) -> int:
    K = fm.KEYS[lm.lang]
    n = 0
    for row in rows:
        if row["lang"] != lm.lang:
            continue
        k = K(row["key"])
        ids = frozenset(row["lex_id"])
        pre = (f"{lm.lang}:", "base:", "form-of:")     # daughter-level path elements only (not sla-pro:*pasti)
        targets = [k] + [x for x, r in lm.recs.items() if x != k and any(
            p.startswith(pre) and K(p.split(":", 1)[1].split("§")[0]) == k for p in r.path[1:])]
        for x in targets:
            old = lm.recs.get(x)
            if not ids:
                if old or x == k:
                    lm.recs.pop(x, None)
                    lm.rejected[x] = "override: " + row.get("note", "")[:80]
                    n += 1
            else:
                lm.recs[x] = fm.MapRec(x, old.word if old else row["key"], ids,
                                       (f"{lm.lang}:{x}", "erratum:" + row.get("note", "")[:60]) +
                                       (tuple(old.path[1:]) if old and x != k else ()),
                                       "erratum", "high", ("mapping-overrides",))
                if x == k:
                    lm.pos[k].add(row.get("pos", "noun") if not lm.pos.get(k) else next(iter(lm.pos[k])))
                n += 1
    return n


def proto_rows(root: Path = ROOT) -> list[dict]:
    """The 'proto' rows of the Balto-Slavic override file: {"code", "term", "lex_id", "note"} — a
    Proto-Slavic / Proto-Balto-Slavic / Proto-Baltic page whose etymology the dictionaries correct
    (lex_id: the right lexicon ids) or reject (lex_id []: unclear etymology or loan). They act on
    every daughter word that inherits from the page (fm.load_overrides ignores this key)."""
    p = Path(root) / OVERRIDE_FILE
    return json.loads(p.read_text("utf-8")).get("proto", []) if p.exists() else []


def harden_protos(protos: fm.ProtoDB, vetoes: dict) -> int:
    """Reject proto entries with a foreign source beside the inherited link ('disputed') and the
    vetoed ones. Returns the number of entries rejected."""
    n = 0
    for (code, k), ents in protos.entries.items():
        for e in ents:
            if e.rejected:
                continue
            if (code, k) in vetoes:
                e.rejected, n = vetoes[(code, k)], n + 1
            elif e.disputed and code in ("sla-pro", "ine-bsl-pro", "bat-pro"):
                e.rejected, n = "foreign source beside inherited link: " + e.disputed, n + 1
    return n


# ---------------------------------------------------------------- daughter entries

def _main_word(form: str, head: str) -> str:
    """'ìšao sam' → 'ìšao', 'бу́ду идти́' → 'идти́', 'sagledao se' → 'sagledao': the word of a multiword
    table form with the longest common prefix with the headword (accent-free)."""
    ws = form.split()
    if len(ws) == 1:
        return form
    h = _nfd_plain(head)
    def lcp(w):
        w, n = _nfd_plain(w), 0
        while n < min(len(w), len(h)) and w[n] == h[n]:
            n += 1
        return n
    best = max(ws, key=lcp)
    return best if lcp(best) >= 1 else ""


def _nfd_plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def _affix_bases(d: dict, lang: str, keep_ids: bool = False) -> list[str]:
    """Same-language base words that fm.parse_entry misses: {{ety|x|:af|*junъ|*-akъ}} (etymon
    templates of kind 'af') and affix templates whose parts carry the proto asterisk (*reťi + *-ь).
    Only a formation with exactly one non-affix part gives a base. keep_ids (proto pages): the
    part's sense id or gloss is kept after '§' (*reťi§say), for BslResolver to pick the homograph."""
    out = []
    for t in d.get("etymology_templates") or []:
        name, a = t.get("name"), t.get("args") or {}
        if a.get("1") != lang:
            continue
        if name in ("etymon", "ety") and str(a.get("2", "")).startswith(":af"):
            parts = [str(a[k]) for k in sorted((k for k in a if k.isdigit() and int(k) >= 3), key=int)]
        elif name in ("affix", "af", "suffix", "suf", "prefix", "pre", "compound", "com", "confix"):
            parts = [str(a[k]) for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int)]
        else:
            continue
        ids = [(re.search(r"<(?:id|t):([^>]*)>", p) or [None, ""])[1] for p in parts]
        parts = [re.sub(r"<[^>]*>", "", p).split("<")[0].strip() for p in parts]
        ids = [i for p, i in zip(parts, ids) if p and p != "-"]
        parts = [p for p in parts if p and p != "-"]
        bare = [p.lstrip("*") for p in parts]
        if name in ("suffix", "suf"):
            content = parts[:1]
        elif name in ("prefix", "pre"):
            content = parts[-1:]
        else:
            content = [p for p, b in zip(parts, bare) if not b.startswith("-") and not b.endswith("-")]
        if len(content) == 1 and not content[0].lstrip("*").startswith("-"):
            b = content[0].split("#")[0]
            gid = ids[parts.index(content[0])] if keep_ids else ""
            out.append(b + (f"§{gid.split(',')[0].split(';')[0].strip()}" if gid else ""))
    return out


def load_protos(root: Path = ROOT, codes=("sla-pro", "ine-bsl-pro", "bat-pro"), want_desc=()) -> fm.ProtoDB:
    """fm.ProtoDB for the Balto-Slavic proto-languages, with the affix bases of `_affix_bases`
    and the section anchors of link terms cleaned."""
    p = fm.ProtoDB(root, codes=[])
    want = set(want_desc)
    for code in codes:
        with open(Path(root) / KD / fm.PROTO_DUMPS[code], encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                if d.get("lang_code") not in (None, code):
                    continue
                e = fm.parse_entry(d, code)
                extra = _affix_bases(d, code, keep_ids=True)
                plain = {b.split("§")[0] for b in extra}
                e.bases = extra + [b for b in e.bases if b not in plain]
                e.etym_no = d.get("etymology_number")
                _clean_links(e)
                p.entries[(code, fs.PieIndex.proto_key(e.word))].append(e)
                if want and d.get("descendants"):
                    tag = f"§#{e.etym_no}" if e.etym_no else ""
                    fm._walk_desc(d["descendants"], code, e.word + tag, want, p.desc)
    return p


def _clean_links(e: fm.Entry) -> fm.Entry:
    """'*lěpъ#Etymology 2' → '*lěpъ§#2' (a Wiktionary section anchor names the homograph page,
    which BslResolver honours); other anchors are dropped. A 'base' that is an affix (*-a, *-do,
    *-tъ: fm.parse_entry keeps the first part of a suffix template) is dropped."""
    e.bases = [b for b in e.bases if not re.match(r"^[*√]*-|.*-$", b.split("§")[0].strip())]
    def one(t):
        m = re.match(r"^(.*?)#Etymology[ _](\d+)", t)
        return f"{m[1].strip()}§#{m[2]}" if m else t.split("#")[0].strip()
    e.links = [(c, one(t), n) for c, t, n in e.links]
    e.bases = [b.split("#")[0].strip() if "§" not in b else b for b in e.bases]
    return e


def _sel_ok(e: fm.Entry, sel: str) -> bool:
    if sel.startswith("#"):
        return str(getattr(e, "etym_no", "") or "") == sel[1:]
    return bool(sel) and sel.lower() in (e.glosses or "").lower()


class BslResolver(fm.Resolver):
    """fm.Resolver plus proto-level derivations: a Proto-Slavic / Proto-Balto-Slavic / Proto-Baltic
    page with no PIE link of its own that is formed from another page of the same proto-language
    (*junakъ = *junъ + *-akъ; *vъzęti = *vъz- + *jęti) takes that page's chain."""

    fixed: dict = {}            # (proto code, proto_key) → (ids, note): the 'proto' rows of the override file

    def resolve(self, code: str, term: str, depth: int = 0):
        fx = self.fixed.get((code, fs.PieIndex.proto_key(term.split("§")[0])))
        if fx:
            return fm.Hit(frozenset(fx[0]), (f"{code}:{term.split('§')[0]}", "erratum:" + fx[1][:60]), "chain", 1)
        if "§" not in term:
            return super().resolve(code, term, depth)
        t, sel = term.split("§", 1)
        ents = [e for e in self.protos.get(code, t) if _sel_ok(e, sel)]
        if not ents:
            return super().resolve(code, t, depth)
        key = (code, fs.PieIndex.proto_key(t), sel)
        if key in self.memo:
            return self.memo[key]
        self.memo[key] = None
        best = None
        if depth < 5 and not all(e.rejected for e in ents):
            for e in ents:
                if e.rejected:
                    continue
                h = self.entry_hit(e, code, depth + 1)
                if h and (best is None or fm._better(h, best)):
                    best = h
            if best:
                best = fm.Hit(best.ids, (f"{code}:{t}",) + best.path, best.how, best.steps + 1, best.disputed)
            else:
                best = super().resolve(code, t, depth)
        self.memo[key] = best
        return best

    vetoes: dict = {}           # (code, proto_key) of loan / unclear proto-forms (and stage entries linking them)

    def entry_hit(self, e: fm.Entry, code: str, depth: int = 0):
        if any((c, fs.PieIndex.proto_key(t.split("§")[0])) in self.vetoes for c, t, _ in e.links):
            return None                 # a word inherited from a vetoed proto-form takes no root-template fallback
        best = super().entry_hit(e, code, depth)
        if (best is None or not best.specific) and e.bases and code in ("sla-pro", "ine-bsl-pro", "bat-pro") \
                and depth < 5:
            for b in e.bases:
                h = self.resolve(code, b, depth + 1)
                if h and (h.specific or best is None):
                    return fm.Hit(h.ids, (f"{code}-base:{b}",) + h.path, h.how, h.steps + 1, h.disputed)
        return best

_HEDGE = re.compile(r"^\s*(?:unknown|unclear|uncertain|obscure|of (?:unknown|uncertain|unclear|disputed|obscure)"
                    r" origin)|further (?:etymology|origins?) (?:is |are )?(?:unknown|unclear|uncertain|obscure)"
                    r"|etymology (?:is )?(?:unknown|unclear|uncertain|obscure)|folk[- ]etymolog", re.I)
_LOAN_CAT = re.compile(r"terms (?:borrowed|semantic loans|calqued|derived) from (?!Proto-(?:Slavic|Balto-Slavic|Baltic|"
                       r"Indo-European)|Old East Slavic|Old Church Slavonic|Church Slavonic|Old Lithuanian)", re.I)
# intra-Slavic / intra-Baltic sources whose 'derived' category is not a foreign loan
_OK_DER = re.compile(r"derived from (?:Proto-|Old East Slavic|Old Church Slavonic|Church Slavonic|Old Lithuanian|"
                     r"Russian|Serbo-Croatian|Lithuanian|Latvian)", re.I)


_SLAVIC = re.compile(r"^(?:cu|chu|orv|ru|uk|be|rue|pl|cs|sk|hsb|dsb|csb|pox|sl|sh|sr|hr|bs|bg|mk|zle|zlw|zls|"
                     r"zle-.*|zlw-.*|zls-.*|sla-.*)$")
_BALTIC = re.compile(r"^(?:lt|olt|lv|ltg|prg|sgs|xcu|xsv|bat-.*)$")
_FAMILY = {"sh": _SLAVIC, "ru": _SLAVIC, "cu": _SLAVIC, "orv": _SLAVIC, "lt": _BALTIC}


def _intra_family(d: dict, lang: str) -> dict:
    """A borrowing or derivation from a sister language of the same branch (Ru. солнце 'learned
    borrowing from Middle Russian', глава from Old Church Slavonic; Lith. from Latvian) is a
    transmission inside the branch, not a foreign loan: a template from an ancestor stage (orv, cu)
    becomes a 'der' link that the resolver follows; one from any other sister language is dropped,
    so that the word's other (inherited) links decide. Loans across branches are untouched."""
    fam = _FAMILY.get(lang)
    if not fam:
        return d
    anc = set(fm.ANCESTORS.get(lang, []))
    out = []
    changed = False
    for t in d.get("etymology_templates") or []:
        a = t.get("args") or {}
        src = a.get("2")
        if (t.get("name") in fm._BOR or t.get("name") in fm._LINK) and a.get("1") == lang and src and src != lang \
                and src not in anc and src != "ine-pro" and fam.match(src):
            changed = True
            continue
        if t.get("name") in fm._BOR and a.get("1") == lang and src in anc and fam.match(src or ""):
            t = {"name": "der", "args": dict(a)}
            changed = True
        out.append(t)
    if not changed:
        return d
    d = dict(d)
    d["etymology_templates"] = out
    return d


def read_entries(lang: str, root: Path = ROOT) -> list[fm.Entry]:
    """kaikki entries of sh / ru / lt / orv / cu with the Celtic rejections (a foreign source beside an
    inherited link; an etymology text calling the etymology unknown) and one more: a 'terms borrowed
    from <non-ancestral language>' category."""
    root = Path(root)
    if lang in SPLIT_FILES:
        paths = [ensure_split(lang, root)]
    elif lang == "orv":
        paths = [root / KD / ORV_DUMP]
    else:
        spec = fm.LANGS[lang]
        paths = [root / KD / d for d in ([spec.dump] if isinstance(spec.dump, str) else spec.dump)]
    codes = set(fm.LANGS[lang].desc_codes or (lang,)) if lang in fm.LANGS else {lang}
    out = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                w0 = (d.get("word") or "").strip()
                if d.get("lang_code") not in codes or " " in w0 or w0.endswith("."):
                    continue                     # multiword headwords ('у краткое') and abbreviations ('стр.')
                sens = d.get("senses") or []
                if sens and all({"abbreviation", "initialism", "acronym"} & set(x.get("tags") or []) for x in sens):
                    continue
                d = _intra_family(d, lang)
                e = fm.parse_entry(d, lang, True)
                if e.disputed and not e.rejected:
                    e.rejected = "foreign source beside inherited link: " + e.disputed
                if not e.rejected and _HEDGE.search(d.get("etymology_text") or ""):
                    e.rejected = "etymology marked unknown/speculative"
                if not e.rejected:
                    cats = [c.get("name", "") if isinstance(c, dict) else c for c in d.get("categories") or []]
                    bad = [c for c in cats if _LOAN_CAT.search(c) and not _OK_DER.search(c)]
                    if bad and not e.links:
                        e.rejected = "category: " + bad[0]
                if e.forms:              # multiword table forms (perfect, future, reflexive): the word
                    e.forms = [_main_word(f, e.word) for f in e.forms]  # closest to the headword, not the auxiliary
                    e.forms = [f for f in e.forms if f]
                e.bases += [b for b in _affix_bases(d, lang) if b not in e.bases]
                _clean_links(e)
                out.append(e)
    return out


# ---------------------------------------------------------------- suppletion and form-table hygiene

# lemma key regex → regex on the loose key of a form that belongs to another stem
SUPPLETIVE = {
    "sh": {r"ći$": r"š(?:a|l|av)", r"^biti$": r"^(?:je|sa|si|smo|ste|su|nisa|nis|nije)"},
    "ru": {r"(?:и|й)ти$": r"ш(?:е|л|ед|ел)", r"^быть$": r"^(?:есть|есмь|еси|суть|нет)"},
    "lt": {r"^būti$": r"^(?:es|yr|nes|nėr)"},
}


def _loose_first(K, s: str) -> str:
    k = K(s, True)
    return k[:1]


def clean_forms(lm: fm.LangMapping) -> int:
    """Drop form-table and form-of links whose form begins with another letter than its lemma
    (suppletive or derived partners listed in a headword's forms: шёл → идти, люди → человек,
    лучше → хороший, ljudi → čovjek) and the SUPPLETIVE patterns. Returns links dropped."""
    K = fm.KEYS[lm.lang]
    pats = [(re.compile(a), re.compile(b)) for a, b in SUPPLETIVE.get(lm.lang, {}).items()]
    n = 0
    heads = set(lm.lemma_words) | set(lm.recs)
    for f in list(lm.forms):
        c = lm.forms[f]
        for lk in list(c):
            if lk == f:
                continue
            bad = lk not in heads           # junk lemma keys from form-of strings ('videti and vidjeti')
            bad = bad or (bool(f) and bool(lk) and _loose_first(K, f) != _loose_first(K, lk))
            bad = bad or any(a.search(lk) and b.search(K(f, True)) for a, b in pats)
            if bad:
                del c[lk]
                n += 1
        if not c:
            del lm.forms[f]
    for k in list(lm.recs):
        w = next((p[len("form-of:"):] for p in lm.recs[k].path if p.startswith("form-of:")), None)
        if not w:
            continue
        lk = K(w)
        if (lk and _loose_first(K, k) != _loose_first(K, lk)) or any(a.search(lk) and b.search(K(k, True))
                                                                     for a, b in pats):
            del lm.recs[k]
            n += 1
    return n


def veto_loans(lm: fm.LangMapping, entries: list[fm.Entry], vetoes: dict) -> int:
    """A key whose every own entry is rejected or links to a vetoed proto-form keeps no mapping from
    another source (the lexicon's reflex lists, a descendants tree, a homograph's form-of link)."""
    by_key: dict[str, list] = collections.defaultdict(list)
    for e in entries:
        if not e.form_of:
            for k in fm.entry_keys(e, lm.lang):
                by_key[k].append(e)
    n = 0
    def vetoed(c, t):
        return (c, fs.PieIndex.proto_key(t.split("§")[0])) in vetoes
    for k, es in by_key.items():
        if k not in lm.recs:
            continue
        def loan(e):
            return e.rejected or any(vetoed(c, t) for c, t, _ in e.links)
        if all(loan(e) for e in es) and any(e.links or e.rejected for e in es):
            del lm.recs[k]
            lm.rejected[k] = "loan veto"
            n += 1
    # any mapping whose path runs through a vetoed proto-form (Ru. бог → orv богъ → *bogъ)
    for k in list(lm.recs):
        for p in lm.recs[k].path:
            c, _, t = p.partition(":")
            if t and c in ("sla-pro", "ine-bsl-pro", "bat-pro") and vetoed(c, t):
                del lm.recs[k]
                lm.rejected[k] = "loan veto (path)"
                n += 1
                break
    # one-letter keys of content words are abbreviations or OCR fragments (п., г.)
    for k in [k for k in lm.recs if len(k) < 2 and lm.pos.get(k, set()) & {"noun", "verb", "adj", "name"}]:
        del lm.recs[k]
        n += 1
    return n


PREVERBS = {
    "cu": ("въз", "вьз", "вън", "въ", "вꙑ", "до", "за", "из", "на", "надъ", "о", "объ", "об", "отъ", "от", "по", "подъ",
           "при", "прѣ", "про", "раз", "роз", "съ", "сь", "оу", "ѫ"),
    "ru": ("воз", "вос", "вз", "вс", "вы", "до", "за", "из", "ис", "на", "над", "о", "об", "обо", "от", "ото", "пере",
           "по", "под", "подо", "пре", "при", "про", "раз", "рас", "с", "со", "у", "в", "во"),
    "sh": ("do", "iz", "is", "na", "nad", "o", "ob", "od", "po", "pod", "pre", "pri", "pro", "raz", "ras", "s", "sa",
           "u", "uz", "us", "za", "z", "iza", "pod", "su"),
    "lt": ("ap", "api", "at", "ati", "iš", "nu", "pa", "par", "per", "pra", "pri", "su", "už", "į", "apsi", "atsi",
           "išsi", "nusi", "pasi", "parsi", "persi", "prasi", "prisi", "susi", "užsi", "įsi"),
}


def add_prefixed_verbs(lm: fm.LangMapping) -> int:
    """An unmapped verb headword that is a preverb + a mapped verb headword (OCS прити = при + ити,
    Ru. возговорить, SCr. pokupiti, Lith. pasakyti) takes the simple verb's mapping (how
    'preverb', confidence low): the root of a preverb compound is the root of its verb."""
    n = 0
    verbs = {k for k, p in lm.pos.items() if "verb" in p}
    for k in sorted(verbs):
        if k in lm.recs or k in lm.rejected:
            continue
        for pv in sorted(PREVERBS.get(lm.lang, ()), key=len, reverse=True):
            b = k[len(pv):]
            if k.startswith(pv) and len(b) >= 3 and b in verbs and b in lm.recs:
                r = lm.recs[b]
                if r.how in ("pseudo",) and len(b) < 4:
                    continue
                lm.recs[k] = fm.MapRec(k, k, r.ids, (f"{lm.lang}:{k}", f"preverb:{pv}-") + r.path, "preverb", "low",
                                       r.sources + ("preverb",), r.gloss)
                n += 1
                break
    return n


_STOP = set("the a an of to in on and or be is as by for with from that this one's someone something etc "
             "make cause become have".split())


def _stems(text: str) -> set:
    return {w[:5] for w in re.findall(r"[a-z]{3,}", (text or "").lower()) if w not in _STOP}


def narrow_by_gloss(lm: fm.LangMapping, entries: list[fm.Entry], gmap: dict, lexmean: dict) -> int:
    """A record whose ids fall in several root groups (homograph lexicon roots: aušra → *h₂ews-
    'dawn' + *h₂ews- 'draw water'; kelti → *kel- 'drive' + *kelH- 'rise') keeps only the ids whose
    lexicon meaning shares a word with the daughter's own glosses, when some do and some do not."""
    gl = collections.defaultdict(str)
    for e in entries:
        if not e.form_of:
            for k in fm.entry_keys(e, lm.lang):
                gl[k] += " " + (e.glosses or "")
    n = 0
    for k, r in list(lm.recs.items()):
        if len({gmap.get(x, x) for x in r.ids}) < 2:
            continue
        g = _stems(gl.get(k, "") or r.gloss)
        if not g:
            continue
        keep = frozenset(x for x in r.ids if _stems(lexmean.get(x, "")) & g)
        if keep and keep != r.ids:
            lm.recs[k] = fm.MapRec(r.key, r.word, keep, r.path, r.how, r.confidence, r.sources + ("gloss-narrowed",),
                                   r.gloss)
            n += 1
    return n


def unmap_homographs(lm: fm.LangMapping, entries: list[fm.Entry], res: fm.Resolver, gmap: dict) -> int:
    """A key that names two dictionary words of different etymology (SCr. grad 'city' / 'hail',
    pasti 'graze' / 'fall', biti 'be' / 'beat'; Ru. есть 'is' / 'eat') is left unmapped: an
    unlemmatized text cannot tell them apart. Two entries differ when their chains reach different
    root groups, or when one has an etymology that does not resolve and names another proto-form."""
    by_key: dict[str, list] = collections.defaultdict(list)
    for e in entries:
        if not e.form_of and not e.rejected and e.pos in fm.CONTENT_POS | {"pron", "num"}:
            for k in fm.entry_keys(e, lm.lang):
                by_key[k].append(e)
    n = 0
    for k, es in by_key.items():
        if k not in lm.recs or len(es) < 2:
            continue
        hits = [(e, res.entry_hit(e, lm.lang)) for e in es]
        groups = {frozenset(gmap.get(x, x) for x in h.ids) for e, h in hits if h and h.specific}
        terms = {fs.PieIndex.proto_key(t.split("§")[0]) for e, h in hits for _, t, _ in e.links[:1]}
        unresolved = [e for e, h in hits if not h and e.links]
        if len(groups) > 1 or (groups and unresolved and len(terms) > 1):
            del lm.recs[k]
            lm.rejected[k] = "homograph of different etymology"
            n += 1
    return n


# Lithuanian personal and reflexive pronoun forms (with the dainos' dialect -ės/-ę): they go to the
# pronoun, never to a verb form that shares the key (manę, manės ≠ manyti)
LT_PRONOUNS = {"aš": ("man", "manęs", "manės", "mane", "manę", "manim", "manimi", "manyje", "manie", "mani"),
               "tu": ("tau", "tavęs", "tavės", "tave", "tavę", "tavim", "tavimi", "tavyje", "tavie", "tavi"),
               "savęs": ("sau", "savęs", "savės", "save", "savę", "savim", "savimi", "savyje", "savie")}


# Serbo-Croatian present forms of *h₁es- (jesam, sam, je, su, nije …): a separate lemma key, so
# that they neither take biti's *bʰuH- nor pass as sam 'alone' / je 'her'
SH_H1ES = ("jesam", "jesi", "jest", "jeste", "jesmo", "jesu", "sam", "si", "je", "smo", "ste", "su", "nisam", "nisi",
           "nije", "nismo", "niste", "nisu", "nijesam", "nijesi", "nijesmo", "nijeste", "nijesu")
H1ES_KEY = "jesam"


def add_h1es_forms(lm: fm.LangMapping, forms) -> None:
    for f in forms:
        k = fm.KEYS[lm.lang](f)
        c = lm.forms[k]
        c[H1ES_KEY] = max([1] + [v for x, v in c.items() if x != H1ES_KEY])   # as strong as any other reading
    lm.recs[H1ES_KEY] = fm.MapRec(H1ES_KEY, "jesam", frozenset({"pie-root-h1es-be"}),
                                  (f"{lm.lang}:jesam", "suppletive:*h₁es-"), "suppletive", "high", ("suppletive",))
    lm.pos[H1ES_KEY].add("verb")
    lm.lemma_words.add(H1ES_KEY)


# sources of loans frequent enough in folk song to collide with an inherited homograph
# (SCr. beg 'bey' / beg 'flight'; Ru. лук 'onion' / лук 'bow')
HOMOGRAPH_LOAN_SRC = re.compile(r"^(?:ota|tr|trk|trk-.*|az|tt|kk|xbo|cv|fa|fa-cls|pal|ira|ira-.*|xsc|ar|hu|de|gmh|goh|"
                                r"gem|gem-pro|gmw-pro|got|non|gmq|sv|yi)$")


def veto_loan_homographs(lm: fm.LangMapping, entries: list[fm.Entry]) -> int:
    """A key that names both a borrowed word (from HOMOGRAPH_LOAN_SRC) and an inherited one is left
    unmapped: an unlemmatized text cannot tell them apart."""
    loan_keys = set()
    for e in entries:
        if e.form_of or not e.rejected:
            continue
        m = re.search(r"foreign source: ([\w,-]+)", e.rejected)
        m2 = None if m else re.match(r"(?:etymon-)?[\w+ -]+?:([\w-]+)", e.rejected)
        codes = m[1].split(",") if m else ([m2[1]] if m2 else [])
        if any(HOMOGRAPH_LOAN_SRC.match(x) for x in codes):
            loan_keys.update(fm.entry_keys(e, lm.lang))
    n = 0
    for k in loan_keys:
        if k in lm.recs:
            del lm.recs[k]
            lm.rejected[k] = "homograph of a loanword"
            n += 1
    return n


# ---------------------------------------------------------------- Lithuanian verb forms from principal parts

def _lt_parts(d: dict) -> tuple[str, str, str] | None:
    """(infinitive, 3 pres., 3 past) from a kaikki Lithuanian verb entry."""
    inf = d.get("word") or ""
    pres = past = None
    for f in d.get("forms") or []:
        t = set(f.get("tags") or [])
        if "present" in t and "third-person" in t and not pres:
            pres = f.get("form")
        elif "past" in t and "third-person" in t and not past:
            past = f.get("form")
    if not inf.endswith(("ti", "tis")) or not pres or not past:
        return None
    return key_lt(inf), key_lt(pres), key_lt(past)


def lt_verb_forms(inf: str, pres: str, past: str) -> set[str]:
    """Finite and common non-finite forms of a Lithuanian verb from its three principal parts (keys,
    tone marks off). Approximate: forms that do not occur in a text never match anything."""
    out = set()
    refl = inf.endswith("tis")
    inf = inf[:-1] if refl else inf
    st = inf[:-2]                                   # infinitive stem
    if pres.endswith("si"):
        pres = pres[:-2]
    if past.endswith("si"):
        past = past[:-2]
    # present
    if pres.endswith("ia"):
        b = pres[:-2]
        out |= {b + "iu", b + "i", b + "ia", b + "iame", b + "iate", b + "iam", b + "iat"}
    elif pres.endswith("a"):
        b = pres[:-1]
        out |= {b + "u", b + "i", b + "a", b + "ame", b + "ate", b + "am", b + "at"}
    elif pres.endswith("i"):
        b = pres[:-1]
        out |= {b + "iu", b + "i", b + "ime", b + "ite", b + "im", b + "it"}
    elif pres.endswith("o"):
        b = pres[:-1]
        out |= {b + "au", b + "ai", b + "o", b + "ome", b + "ote", b + "om", b + "ot"}
    out.add(pres)
    # past
    if past.endswith("ė"):
        b = past[:-1]
        if b.endswith("č"):
            b2 = b[:-1] + "t"
        elif b.endswith("dž"):
            b2 = b[:-2] + "d"
        else:
            b2 = b
        out |= {b + "iau" if not b.endswith(("č", "dž")) else b + "iau", b2 + "ei", b + "ė", b + "ėme", b + "ėte",
                b + "ėm", b + "ėt"}
    elif past.endswith("o"):
        b = past[:-1]
        out |= {b + "au", b + "ai", b + "o", b + "ome", b + "ote", b + "om", b + "ot"}
    out.add(past)
    # future, conditional, imperative, frequentative past, participles, gerunds
    fs_ = st
    if st.endswith(("s", "z")):
        fs_ = st[:-1]
    elif st.endswith(("š", "ž")):
        fs_ = st[:-1]
    fut = fs_ + ("š" if st.endswith(("š", "ž")) else "s")
    out |= {fut, fut + "iu", fut + "i", fut + "ime", fut + "ite", fut + "im", fut + "it"}
    out |= {st + "čiau", st + "tum", st + "tų", st + "tumėme", st + "tumėte", st + "tumei", st + "tumbim"}
    imp = st + "k" if not st.endswith(("g", "k")) else st
    out |= {imp, imp + "ite", imp + "ime", imp + "it", imp + "im", st + "ki", st + "kie"}
    out |= {st + "davo", st + "davau", st + "davai", st + "davome", st + "davote"}
    out |= {st + "tas", st + "ta", st + "ti", st + "tą", st + "tos", st + "tus", st + "damas", st + "dama",
            st + "dami", st + "damos", st + "dam", st + "tinas", st + "sias", st + "siant", st + "siąs"}
    if pres.endswith(("a", "ia", "o", "i")):
        b = pres[:-1] if not pres.endswith("ia") else pres[:-2] + "i"
        out |= {b + "nt", b + "ntis", b + "nčios", b + "ntys", b + "ntį", b + "nčią", b + "ąs", b + "ąją",
                b + "nčių", pres + "nt", pres + "ntis"}
    if past.endswith(("o", "ė")):
        b = past[:-1]
        out |= {b + "ęs", b + "usi", b + "usios", b + "usią", b + "usį", b + "iusi", b + "ęsis"}   # not -ę (manę 'me')
    if refl or True:
        out |= {f + "s" for f in list(out) if f.endswith(("u", "i", "a", "o", "ė", "e"))}
        out |= {f + "si" for f in list(out) if f.endswith(("a", "o", "ė", "e"))}
        out |= {f[:-1] + "uosi" for f in list(out) if f.endswith("u")}
        out |= {f[:-1] + "iesi" for f in list(out) if f.endswith("i")}
    out.add(inf)
    out.add(inf + "s")
    return {x for x in out if len(x) >= 2}


def add_lt_verb_forms(lm: fm.LangMapping, root: Path = ROOT) -> int:
    """Generated verb forms → their infinitive's key, unless the form is already a table form."""
    n = 0
    path = Path(root) / KD / fm.LANGS["lt"].dump
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if '"pos": "verb"' not in line:
                continue
            d = json.loads(line)
            if d.get("lang_code") != "lt" or d.get("pos") != "verb":
                continue
            p = _lt_parts(d)
            if not p:
                continue
            lk = p[0]
            if lk.endswith("tis"):
                lk = lk  # reflexive headword key kept as is
            for f in lt_verb_forms(*p):
                for fk in (f,):                     # exact keys only: a generated form never claims a loose key
                    c = lm.forms[fk]
                    if lk not in c and not c:
                        c[lk] += 1
                        n += 1
    return n


# ---------------------------------------------------------------- building the mappings

@dataclass
class BslMappings:
    sh: fm.LangMapping
    ru: fm.LangMapping
    lt: fm.LangMapping
    cu: fm.LangMapping          # kaikki OCS (key_cu keys)
    lexicon: list
    gmap: dict
    vetoes: dict
    entries: dict               # lang → list[Entry]


def _load_lexicon(root: Path) -> list[dict]:
    return [json.loads(l) for l in (Path(root) / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines() if l]


def build_mappings(root: Path = ROOT, lexicon: list[dict] | None = None, langs=("sh", "ru", "lt", "cu")) -> BslMappings:
    root = Path(root)
    lex = lexicon or _load_lexicon(root)
    idx = fs.PieIndex(lex)
    want = set()
    for c in langs:
        want |= set(fm.LANGS[c].desc_codes or (c,))
    protos = load_protos(root, want_desc=tuple(want))
    vetoes = proto_vetoes(root)
    fixed = {}
    for r in proto_rows(root):
        k = (r["code"], fs.PieIndex.proto_key(r["term"]))
        if r["lex_id"]:
            fixed[k] = (tuple(r["lex_id"]), r.get("note", ""))
            vetoes.pop(k, None)
        else:
            vetoes[k] = "override: " + r.get("note", "")
    BslResolver.fixed = fixed
    BslResolver.vetoes = vetoes
    harden_protos(protos, vetoes)
    ents, out = {}, {}
    # Old East Slavic (for Russian) and Old Church Slavonic (Church Slavonicisms in Russian and
    # Serbo-Croatian) as intermediate stages
    stages = (["orv"] if "ru" in langs else []) + (["cu"] if {"ru", "sh"} & set(langs) else [])
    for st in stages:
        es = read_entries(st, root)
        if st in langs:
            ents[st] = es
        for e in es:
            if any((c, fs.PieIndex.proto_key(t.split("§")[0])) in vetoes for c, t, _ in e.links):
                e.rejected = e.rejected or "links to a vetoed proto-form"
                vetoes[(st, fs.PieIndex.proto_key(e.word))] = "stage entry links to a vetoed proto-form"
            if not e.form_of:
                protos.entries[(st, fs.PieIndex.proto_key(e.word))].append(e)
    saved = fm.Resolver
    fm.Resolver = BslResolver                 # build_lang_mapping looks the class up at call time
    try:
        for c in langs:
            ents[c] = ents.get(c) or read_entries(c, root)
            out[c] = fm.build_lang_mapping(c, lex, protos, root=root, entries=ents[c], idx=idx)
    finally:
        fm.Resolver = saved
    gmap = fs.group_map(lex)
    kinds = {e["id"]: e.get("kind") for e in lex}
    res = BslResolver(idx, protos, kinds, True)
    for c in langs:                               # keys of words that carry an etymology (resolved or not)
        out[c].etym_keys = {k for e in ents[c] if not e.form_of and (e.links or e.roots or e.bases or e.rejected)
                            for k in fm.entry_keys(e, c)}
    lexmean = {e["id"]: " ".join(e.get("meaning") or []) if isinstance(e.get("meaning"), list) else str(e.get("meaning") or "")
               for e in lex}
    for c in langs:
        lm = out[c]
        veto_loans(lm, ents[c], vetoes)
        veto_loan_homographs(lm, ents[c])
        unmap_homographs(lm, ents[c], res, gmap)
        narrow_by_gloss(lm, ents[c], gmap, lexmean)
        add_prefixed_verbs(lm)
        for k in lm.recs:
            if len(k) <= 3 and not lm.pos.get(k):
                lm.pos[k].add("other")            # a short key known only from reflex lists is not a content word
        for k in list(lm.recs):
            r = lm.recs[k]
            keep = frozenset(fm._strip_blocked(r.ids))
            if not keep:
                del lm.recs[k]
            elif keep != r.ids:
                lm.recs[k] = fm.MapRec(r.key, r.word, keep, r.path, r.how, r.confidence, r.sources, r.gloss)
        clean_forms(lm)
        if c == "lt":
            add_lt_verb_forms(lm, root)
            for lem, forms in LT_PRONOUNS.items():
                for f in forms:
                    for fk in {key_lt(f), key_lt(f, True)}:
                        lm.forms[fk] = collections.Counter({lem: 1})
                lm.pos[lem].add("pron")
                lm.lemma_words.add(lem)
    if "sh" in out:
        add_h1es_forms(out["sh"], SH_H1ES)
    krows = key_rows(root)
    for c in langs:
        if c != "cu":                             # cu: after the TOROT merge (ocs_mapping)
            apply_key_rows(out[c], krows)
    return BslMappings(out.get("sh"), out.get("ru"), out.get("lt"), out.get("cu"), lex, gmap, vetoes, ents)


# ---------------------------------------------------------------- lemmatizer

HEAD_ONLY = "\x00"          # variant prefix: the variant counts only if it is itself a headword key
_TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*['’]?", re.U)


def words(text: str) -> list[str]:
    """Word tokens; a word-final apostrophe (Vuk's elision: ил', нит') is kept."""
    return _TOKEN.findall(text)


class BslLemmatizer:
    """Surface → lemma key string (fm.FormLemmatizer conventions: 'a|b' for up to `max_lemmas`
    candidates, '?' + loose key when unknown).

    Order: the form as written, then each spelling variant from `variants` (exact keys first,
    then loose keys). A form that is a headword and also a frequent form of another lemma gives
    'a|b' (every lemma with at least a third of the best count), which multi-lemma mapping leaves
    unmapped when the etyma differ."""

    def __init__(self, lm: fm.LangMapping, norm=None, variants=None, max_lemmas: int = 3,
                 form_overrides: dict | None = None):
        self.lm, self.K = lm, fm.KEYS[lm.lang]
        self.norm = norm or (lambda s: s)
        self.variants = variants or (lambda s: [])
        self.max = max_lemmas
        self.form_overrides = form_overrides or {}
        self.heads = set(lm.lemma_words) | set(lm.recs)
        self.cache: dict[str, str] = {}
        self.level: dict[str, str] = {}

    def _table(self, k: str) -> str | None:
        c = self.lm.forms.get(k)
        if c:
            top = max(c.values())
            keep = sorted((x for x in c if 3 * c[x] >= top), key=lambda x: (-c[x], x != k, x))
            return "|".join(keep[: self.max])
        if k in self.heads:
            return k
        return None

    def __call__(self, surface: str) -> str:
        r = self.cache.get(surface)
        if r is None:
            r, lvl = self._lemmatize(surface)
            self.cache[surface], self.level[surface] = r, lvl
        return r

    def _lemmatize(self, surface: str) -> tuple[str, str]:
        s = self.norm(surface)
        k0 = self.K(s)
        if k0 in self.form_overrides:
            return self.form_overrides[k0], "override"
        var = [v for v in self.variants(s) if v and v != s]
        head_only = {v[1:] for v in var if v.startswith(HEAD_ONLY)}
        var = [v.lstrip(HEAD_ONLY) for v in var]
        cands = (var + [s]) if s.endswith("'") else ([s] + var)      # an elided word is never its bare form first
        for loose in (False, True):
            for i, c in enumerate(cands):
                k = self.K(c, loose)
                if len(k) < 1 or (cands[i] != s and len(k) < 2):
                    continue
                if cands[i] in head_only:
                    r = k if k in self.heads and self.lm.pos.get(k, set()) & {"noun", "adj", "name"} else None
                else:
                    r = self._table(k)
                if r and len(k) <= 3 and all(len(x) > 2 * len(k) + 2 for x in r.split("|")):
                    r = None                     # a short token read as a dictionary abbreviation ('vard.', 'raj.')
                if r:
                    return r, ("form" if cands[i] == s else "variant") + ("-loose" if loose else "")
        return "?" + self.K(s, True), "unknown"


# Vuk (Serbian Cyrillic, ijekavian) ------------------------------------------------

def vuk_norm(w: str) -> str:
    return w.replace("’", "'").lower()


_VUK_END = (("ијема", "има"), ("ијем", "им"), ("ијех", "их"), ("ијем", "ом"), ("ога", "ог"), ("ому", "ом"),
            ("оме", "ом"), ("ему", "ем"), ("еме", "ем"), ("ега", "ег"))


def vuk_variants(w: str) -> list[str]:
    """Vuk's spellings → standard ijekavian: elided final vowel (ил' → или, нит' → нити), his
    jotated ђ/ћ for дј/тј (ђевојка → дјевојка, ћерати → тјерати), dropped initial х (оћу → хоћу),
    ijekavian long endings (-ијем, -ијех, -ијема) and long adjectival endings (-ога, -ому)."""
    out = []
    base = w.rstrip("'")
    if w.endswith("'"):
        out += [base + v for v in ("и", "а", "е", "о", "у")]
    cands = [base]
    if "ђ" in base or "ћ" in base:
        j = base.replace("ђе", "дје").replace("ће", "тје").replace("ђи", "дји")
        j2 = base.replace("ђ", "дј").replace("ћ", "тј")
        cands += [j, j2]
    if base[:1] in "аеиоу":
        cands.append("х" + base)
    if "је" in base and "ије" not in base:
        cands.append(re.sub(r"(?<=[бвгдзклмнпрстфхцчшжђћ])је", "ије", base, count=1))
    if "ије" in base:
        cands.append(base.replace("ије", "је", 1))
    for c in list(cands):
        for a, b in _VUK_END:
            if c.endswith(a) and len(c) > len(a) + 1:
                cands.append(c[: -len(a)] + b)
    out += cands[1:]
    return out


# Russian (pre-reform and dialect byliny spelling) --------------------------------

def ru_norm(w: str) -> str:
    return w.lower()


_RU_END = (("аго", "ого"), ("яго", "его"), ("ыя", "ые"), ("ия", "ие"), ("ова", "ого"), ("ева", "его"),
           ("ой", "ый"), ("ей", "ий"), ("ыи", "ый"), ("ии", "ий"), ("ыим", "ым"), ("ою", "ой"), ("ею", "ей"),
           ("ия", "ья"), ("ие", "ье"), ("ию", "ью"))


_RU_SHORT = (("у", "ую"), ("ю", "юю"), ("ы", "ые"), ("и", "ие"), ("а", "ая"), ("я", "яя"), ("о", "ое"), ("е", "ее"))
_RU_DIM = re.compile(r"^(.{2,}?)(?:ушк|юшк|ушек|юшек|еньк|оньк|онк|енк|ышк|ушечк|очк|ечк|ёнк|ок|ек|ик|ечек|очек)"
                     r"(?:а|и|у|е|ой|ою|ам|ами|ах|о|ом|ов|ы)?$")
_RU_PREV = ("воз", "вос", "вз", "вс", "вы", "до", "за", "из", "ис", "на", "об", "обо", "от", "ото", "пере", "по", "под",
            "подо", "при", "про", "раз", "рас", "со", "с", "у", "о", "въ", "в")


def ru_variants(w: str) -> list[str]:
    """Pre-reform and byliny spellings → modern: -аго/-яго → -ого/-его, -ыя/-ія → -ые/-ие, Kirsha's
    -ова/-ева genitives, -ой for -ый, -ія/-іе/-ію; dialect пошол → пошел; byliny contracted
    adjectives (чисту → чистую, золоты → золотые); OCR ф/б for ѣ/о and a lost final ѣ (себ → себе);
    hypocoristic diminutives (силушку → сила, дороженька → дорога); last, a stripped preverb
    (возговорит → говорит)."""
    s = key_ru(w)
    out = []
    for a, b in _RU_END:
        if s.endswith(a) and len(s) > len(a) + 1:
            out.append(s[: -len(a)] + b)
    if s.endswith("ол") and len(s) > 3:
        out.append(s[:-2] + "ел")
    for a, b in _RU_SHORT:
        if s.endswith(a) and len(s) >= 4:
            out.append(s[: -len(a)] + b)
    if "ф" in s:
        out.append(s.replace("ф", "е"))
    if "б" in s[1:]:
        out.append(s[0] + s[1:].replace("б", "о"))
    if len(s) >= 3 and s[-1] not in "аеиоуыэюяйь":
        out.append(s + "е")
    m = _RU_DIM.match(s)
    if m:
        b = m[1]
        alt = b[:-1] + {"ж": "г", "ч": "к", "ш": "х"}.get(b[-1], b[-1])
        for x in dict.fromkeys([b, alt]):
            out += [HEAD_ONLY + x + e for e in ("а", "о", "ь", "", "я", "е")]
    for p in _RU_PREV:
        if s.startswith(p) and len(s) - len(p) >= 4:
            out.append(s[len(p):])
    return out


# Lithuanian (19th-c. editions) ---------------------------------------------------

_LT_ORTH = (("sz", "š"), ("cz", "č"), ("ż", "ž"), ("ź", "ž"), ("ſ", "s"), ("ů", "uo"), ("ł", "l"), ("w", "v"),
            ("ë", "ė"), ("ẽ", "e"), ("ã", "a"), ("õ", "o"), ("ũ", "u"), ("ĩ", "i"), ("ỹ", "y"), ("ô", "o"),
            ("ê", "ė"), ("û", "ū"), ("î", "y"), ("é", "ė"))


def lt_norm(w: str) -> str:
    s = unicodedata.normalize("NFC", w.lower())
    for a, b in _LT_ORTH:
        s = s.replace(a, b)
    return s


_LT_DIM = re.compile(r"^(.{2,}?)(?:užėl|užiuk|užaič|užait|užyt|užėl|užel|už|ėl|el|ytė|yt|yč|ut|uč|aič|ait|ul|uk|iuk|"
                     r"ėn|užukėl|eliuk|ėliuk|ėlyt|užėliuk|ulyt|ulėl|užuk)"
                     r"(?:is|ė|ys|io|iui|į|iu|yje|i|ių|iams|ius|iais|iuose|ę|ės|ei|ėje|ių|ėms|es|ėmis|ėse|a|ai|ą|"
                     r"e|u|o|ui|us|ų|ams|uos|ais|ose|as|yt|ėm|ėj|iai|ia|ią|ios|ioms|iom|iomis|ioj)?$")
_LT_PREV = ("nebe", "tebe", "ne", "be", "te", "atsi", "apsi", "išsi", "nusi", "pasi", "parsi", "persi", "prasi",
            "prisi", "susi", "užsi", "įsi", "at", "ap", "iš", "nu", "pa", "par", "per", "pra", "pri", "su", "už", "į",
            "ant", "api", "isz")


def lt_variants(w: str) -> list[str]:
    """Polish-style diphthongs (aj/ej → ai/ei), dialect -a for -o (mana → mano), diminutives
    (laivužis → laivas), particles and preverbs (nesziok → nešiok, pasikėlė → kėlė)."""
    s = lt_norm(w)
    out = []
    if re.search(r"[aeu]j(?![aeiouyąęėįųū])", s):
        out.append(re.sub(r"([aeu])j(?![aeiouyąęėįųū])", r"\1i", s))
    if s.endswith("ej") and len(s) > 3:                       # Juškevič brolelej, zodelej → -iai / -ei
        out += [s[:-2] + "iai", s[:-2] + "ei", s[:-2] + "ėj"]
    if "y" in s:                                              # y for i (motynele → motinėlė)
        out.append(s.replace("y", "i"))
    if re.search(r"e(?=l|s$|$)", s):                          # e for ė in suffixes (-elė, -es)
        out.append(re.sub(r"e(?=l[eė]|s$|$)", "ė", s))
    if s.endswith("a") and len(s) > 3:
        out.append(s[:-1] + "o")
    m = _LT_DIM.match(s)
    if m and len(m[1]) >= 2:
        b = m[1]
        if len(b) >= 3:                                       # a diminutive must reach a headword itself
            out += [HEAD_ONLY + b + e for e in ("as", "is", "ys", "a", "ė", "us", "uo", "ias", "ius")]
    for p in _LT_PREV:
        if s.startswith(p) and len(s) - len(p) >= 3:
            rest = s[len(p):]
            out.append(rest)
            for q in _LT_PREV[6:]:
                if rest.startswith(q) and len(rest) - len(q) >= 3:
                    out.append(rest[len(q):])
    return out


def ru_norm_ocr(w: str) -> str:
    """OCR debris of pre-reform letters: $ and inner Ъ/Ь read for ѣ, 1 for і."""
    w = re.sub(r"(?<=[а-яѣі])[$%]|(?<=[а-яѣі])[ЪЬ](?=[а-яѣі])|(?<=[а-яѣі]{2})Ъ$", "ѣ", w)
    w = re.sub(r"(?<=[а-яА-Я])1(?=[а-яА-Я])", "і", w)
    return w.lower()


# ---------------------------------------------------------------- corpus readers
#
# Each yields (locus, units, text); text is one verse line (prose: one OCR line). Sources and line
# filters are listed per corpus in SOURCES and in the reader docstrings.

SOURCES = {
    "vuk": {"serbian-vuk-wikisource": "CC BY-SA 4.0 (sr.wikisource transcription; text public domain)"},
    "byliny": {"russian-byliny-wikisource": "CC BY-SA 4.0 (ru.wikisource transcription; text public domain)",
               "russian-hilferding-1894-archiveorg": "public domain",
               "russian-kireevsky-1860-1874-archiveorg": "public domain",
               "russian-rybnikov-1861-1867-archiveorg": "public domain"},
    "dainos": {"lithuanian-rhesa-dainos-1825-1843": "public domain",
               "lithuanian-nesselmann-1853": "public domain",
               "lithuanian-schleicher-1857": "public domain",
               "lithuanian-leskien-brugmann-1882": "public domain",
               "lithuanian-bartsch-dainubalsai-1886": "public domain",
               "lithuanian-juskevic-dainos-1880-1883": "public domain"},
    "ccmh": {"ocs-ccmh": "CC BY 4.0 (Corpus Cyrillo-Methodianum Helsingiense)"},
}
CORPUS_LANG = {"vuk": "sh", "byliny": "ru", "dainos": "lt", "ccmh": "cu"}
_CYR = re.compile(r"[А-Яа-яЁёЂђЈјЉљЊњЋћЏџѢѣІіѲѳѴѵ]")


def _plaintext_songs(path: Path):
    title, pid, i = None, None, 0
    for line in path.read_text("utf-8").splitlines():
        m = re.match(r"^### (.*?) \[pageid (\d+)", line)
        if m:
            title, pid, i = m[1], m[2], 0
            continue
        if pid and line.strip() and _CYR.search(line):
            i += 1
            yield pid, title, i, line


_VUK_APPARATUS = re.compile(r"\d|^\s*Извор|[Сс]тр\.|Караџић|издањ|штампариј|[Кк]њига (?:прва|друга|трећа|четврта|пета)|"
                            r"[A-Za-z]{3}|Просвета|уредио|тумачењем")


def vuk_song_line(line: str) -> bool:
    """Not a bibliographic or editorial line (digits after the line number and footnote marks are
    stripped; 'Извор', 'стр.', 'Караџић', 'издање', Latin words) and at most 14 words (the deseterac
    has 3-6)."""
    return not _VUK_APPARATUS.search(line) and len(line.split()) <= 14


def vuk_units(root: Path = ROOT):
    """Vuk's songs (sr.wikisource plain text, one song page per '###' header). Unit: verse line;
    units: song (page id), line. Lines without Cyrillic (wiki debris) and editorial lines
    (`vuk_song_line`) are skipped."""
    p = Path(root) / KD / "serbian-vuk-wikisource/songs-plaintext.txt"
    for pid, title, i, line in _plaintext_songs(p):
        from pie.material_units import reviewed_vuk_material
        if reviewed_vuk_material(pid, i):
            continue
        line = re.sub(r"\[\d+\]", "", re.sub(r"^\s*\d{1,5}\.?\s+", "", line))
        if not vuk_song_line(line):
            continue
        yield (f"Vuk {pid}:{i}", {"song": f"vuk:{pid}", "line": f"vuk:{pid}:{i}",
                                  "source": "serbian-vuk-wikisource"}, line)


BYLINY_OCR = {
    "russian-hilferding-1894-archiveorg": ("sbornikotdelenijarusskogojazykaislovesno32_djvu.txt",
                                           "sbornikotdelenijarusskogojazykaislovesno92_djvu.txt"),
    "russian-kireevsky-1860-1874-archiveorg": None,       # every *_djvu.txt
    "russian-rybnikov-1861-1867-archiveorg": None,
}


def _verse_like(line: str, max_words: int = 8) -> bool:
    ws = line.split()
    if not 2 <= len(ws) <= max_words or line.rstrip().endswith(("-", "—")):
        return False
    letters = [c for c in line if c.isalpha()]
    if len(letters) < 6:
        return False
    cyr = sum(1 for c in letters if _CYR.match(c))
    return cyr / len(letters) >= 0.85 and not re.search(r"\d{2,}", line)


def byliny_units(root: Path = ROOT):
    """Byliny: the ru.wikisource texts (Kirsha Danilov, Rybnikov pt. I pre-reform versions, two
    Hilferding byliny), every verse line; and the archive.org OCR of Hilferding vols. 2-3, Kireevsky
    vyp. 1, 4-10 and Rybnikov pts. 1-4, OCR lines that look like verse: 2-8 words, ≥ 85% Cyrillic
    letters, no number of two or more digits, no line-final hyphen (prose commentary, headers and
    indexes mostly fail this). Contextual prose and editorial features in
    material_units exclude non-epic material. Historical reviewed exclusions
    remain a backstop, not detector training at runtime. Doubtful units stay;
    this is not a claim that all remaining OCR is verse.
    Rybnikov pt. I is in both the wikisource and the OCR set."""
    from pie.material_units import byliny_wiki_lines, byliny_non_epic, excluded_source, reviewed_byliny_text
    root = Path(root)
    p = root / KD / "russian-byliny-wikisource/texts-plaintext.txt"
    for pid, title, i, line in byliny_wiki_lines(_plaintext_songs(p)):
        yield (f"ruws {pid}:{i}", {"song": f"ruws:{pid}", "line": f"ruws:{pid}:{i}",
                                   "source": "russian-byliny-wikisource"}, line)
    for d, files in BYLINY_OCR.items():
        paths = [root / KD / d / f for f in files] if files else sorted((root / KD / d).glob("*_djvu.txt"))
        for fp in paths:
            stem = fp.stem.replace("_djvu", "")
            lines = fp.read_text("utf-8", errors="replace").splitlines()
            excluded = byliny_non_epic(lines)
            for i, line in enumerate(lines):
                if (_verse_like(line) and i not in excluded and
                        not excluded_source("byliny", fp.name, i + 1)):
                    yield (f"{stem}:{i + 1}", {"page_file": f"{d}/{stem}", "line": f"{stem}:{i + 1}",
                                               "source": d}, reviewed_byliny_text(f'{stem}:{i + 1}', line))


LT_FUNC = set("""ir ar kad kur o ei tai ne nei su iš isz į ant po prie pri mano mana tavo tava savo sava jo jos
 aš asz tu mes jūs jus kaip kas ko kam tik dar jau bet nu pas per už uż kodėl tas ta tą tie tos ten čia czia
 nė jog nes tad dėl del lig ligi iki man tau mus jau vėl vel sau tę tę jei jeigu kaip kaipgi ogi tegu bus buvo
 yra mergužė mergelė bernelis motinėlė tėvelis brolelis sesutė jaunas jauna žirgelis""".split())
DE_FUNC = set("""und der die das ich du er sie es nicht mit von zu ein eine einen ist mein dein auf im den dem des
 wie so wo was als auch nach aus bei mir dir mich dich sich hat war wird werden noch nur am an da daß dass
 doch ja nein vor für fur über uber unter durch um bis ihr ihm ihn uns euch sein seine meine deine mutter
 vater lied lieder anmerkung vgl seite heißt bedeutet wort""".split())


def lt_line(line: str) -> bool:
    """A dainos OCR line is Lithuanian when its Lithuanian evidence (function words, words with
    Lithuanian letters or sz/cz digraphs) outweighs its German evidence (function words, ß, sch,
    umlauts in German-looking words) and it has at least two words."""
    ws = [w.lower() for w in _TOKEN.findall(line)]
    if len(ws) < 2:
        return False
    lt = de = 0
    for w in ws:
        if w in LT_FUNC or re.search(r"[ąčęėįšųūž]|sz|cz|ż", w):
            lt += 1
        if w in DE_FUNC or re.search(r"ß|sch|ſch|tz|ck|ung$|lich$|keit$|heit$", w):
            de += 1
    return lt >= 1 and lt > de


DAINOS_FILES = {
    "lithuanian-rhesa-dainos-1825-1843": ("dainos00reza_djvu.txt", "Rhesa_Dainas_1825n_djvu.txt"),
    "lithuanian-nesselmann-1853": ("littauischevolk00nessgoog_djvu.txt",),
    "lithuanian-schleicher-1857": ("litauischemrch00schl_djvu.txt",),
    "lithuanian-leskien-brugmann-1882": ("litauischevolksl00leskuoft_djvu.txt",),
    "lithuanian-bartsch-dainubalsai-1886": ("dainubalsai00tilsgoog_djvu.txt",),
    "lithuanian-juskevic-dainos-1880-1883": ("lietvikosdjnos00iugoog_djvu.txt", "litvikosdjnosur00jugoog_djvu.txt",
                                             "Lietuviškos svotbinės dainos, 1883_djvu.txt"),
}


def dainos_units(root: Path = ROOT):
    """Lithuanian dainos: every OCR line that passes `lt_line` (facing German translations, German
    notes and introductions fail it). Line-final hyphens are joined to the next line."""
    root = Path(root)
    from pie.material_units import dainos_interleaved, excluded_source
    for d, files in DAINOS_FILES.items():
        for fn in files:
            fp = root / KD / d / fn
            if not fp.exists():
                continue
            stem = re.sub(r"[^A-Za-z0-9]+", "-", fp.stem.replace("_djvu", "")).strip("-")
            lines = fp.read_text("utf-8", errors="replace").splitlines()
            # This edition's OCR is independently verified as two-column.
            # Other editions have different layouts; do not infer their layout
            # from isolated verse/page numbers in prose.
            excluded = dainos_interleaved(lines) if fn == 'Lietuviškos svotbinės dainos, 1883_djvu.txt' else set()
            carry = ""
            for i, line in enumerate(lines):
                if i in excluded or excluded_source('dainos', fn, i + 1):
                    carry = ''
                    continue
                line = carry + line
                carry = ""
                if re.search(r"\w[-⸗]\s*$", line):
                    carry = re.sub(r"[-⸗]\s*$", "", line).rsplit(" ", 1)
                    line, carry = (carry[0], carry[1]) if len(carry) == 2 else ("", carry[0])
                if lt_line(line):
                    yield (f"{stem}:{i + 1}", {"page_file": f"{d}/{stem}", "line": f"{stem}:{i + 1}",
                                               "source": d}, line)


# CCMH 7-bit transliteration → Cyrillic (Marianus table; Suprasliensis differs in u/U/Y, see CCMH_CODEX)
_CCMH_BASE = [("jE", "ѩ"), ("jO", "ѭ"), ("ju", "ю"), ("ja", "ꙗ"), ("je", "ѥ"), ("a", "а"), ("b", "б"), ("v", "в"),
              ("g", "г"), ("d", "д"), ("e", "е"), ("Z", "ж"), ("D", "ѕ"), ("z", "з"), ("i", "и"), ("I", "і"),
              ("J", "і"), ("G", "г"), ("k", "к"), ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"),
              ("r", "р"), ("s", "с"), ("t", "т"), ("f", "ф"), ("F", "ф"), ("T", "ѳ"), ("x", "х"), ("w", "ѡ"),
              ("q", "щ"), ("c", "ц"), ("C", "ч"), ("S", "ш"), ("&", "ъ"), ("$", "ь"), ("y", "ꙑ"), ("@", "ѣ"),
              ("E", "ѧ"), ("O", "ѫ"), ("X", "кс"), ("P", "пс"), ("A", "ъ"), ("j", "ј")]
CCMH_CODEX = {
    "marianus": {"u": "оу", "U": "ѵ", "Y": "у"},
    "zographensis": {"u": "оу", "U": "ѵ", "Y": "ѵ"},
    "zogr-b": {"u": "оу", "U": "ѵ", "Y": "ѵ"},
    "assemanianus": {"u": "оу", "U": "ѵ", "Y": "у"},
    "savvina": {"u": "оу", "U": "оу", "Y": "ѵ"},
    "suprasliensis": {"u": "оу", "U": "оу", "Y": "ѵ"},
}


def ccmh_word(w: str, codex: str = "marianus") -> str | None:
    """One CCMH word → Cyrillic, or None for a word under titlo ('!' first: an abbreviation) or with
    an unreadable letter ('?'). Diacritics (* ' ~ ^ ( ) \" %) and brackets are dropped; an inner '!'
    (superscript letter) keeps its letter."""
    if w.startswith("!") or "?" in w:
        return None
    w = re.sub(r"[*'~^()\"%\[\]<>=!]", "", w)
    if not w or not re.search(r"[A-Za-z&$@]", w):
        return None
    extra = CCMH_CODEX.get(codex, CCMH_CODEX["marianus"])
    out, i = [], 0
    table = [(k, v) for k, v in extra.items()] + _CCMH_BASE
    while i < len(w):
        for k, v in table:
            if w.startswith(k, i):
                out.append(v)
                i += len(k)
                break
        else:
            i += 1
    s = "".join(out).replace("ј", "")
    return s or None


CCMH_FILES = ("marianus", "zographensis", "zogr-b", "assemanianus", "savvina", "suprasliensis")


def ccmh_units(root: Path = ROOT):
    """CCMH canonical OCS codices (the two Vitae, later copies, are left out). Unit: one text line
    (gospels: one verse line; Suprasliensis: one manuscript line). Text: the 7-bit transliteration
    with {…} (superfluous material) removed; '-' + line end joins a word across lines."""
    root = Path(root) / KD / "ocs-ccmh/ccmh-src"
    for codex in CCMH_FILES:
        fp = root / f"{codex}.txt"
        if not fp.exists():
            continue
        carry = ""
        for line in fp.read_text("utf-8", errors="replace").splitlines():
            m = re.match(r"^\s*(\d{6,8})\s+(.*)$", line)
            if not m:
                continue
            lid, text = m[1], re.sub(r"\{[^}]*\}", "", m[2])
            text = carry + text
            carry = ""
            if re.search(r"[A-Za-z&$@]-\s*$", text):
                parts = re.sub(r"-\s*$", "", text).rsplit(" ", 1)
                text, carry = (parts[0], parts[1]) if len(parts) == 2 else ("", parts[0])
            yield (f"{codex} {lid}", {"codex": codex, "line": f"{codex}:{lid}", "verse": f"{codex}:{lid[:5]}",
                                      "source": "ocs-ccmh"}, text)


def ccmh_words(text: str) -> list[str]:
    return [w for w in re.split(r"[\s.:,;]+", text) if w and w not in ("-", "--", ":-", "::")]


# ---------------------------------------------------------------- OCS: TOROT pairs and the round-3 'cu' table

TOROT_OCS = fm.PROIEL_DIR, ("proiel/marianus.xml", "torot/zogr.xml", "torot/supr.xml", "torot/psal-sin.xml",
                            "torot/vit-const.xml", "torot/vit-meth.xml", "torot/kiev-mis.xml", "torot/chrabr.xml",
                            "torot/euch.xml")
_P_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')


def torot_pairs(root: Path = ROOT) -> collections.Counter:
    """(form key, lemma key, coarse POS) counts from the TOROT/PROIEL OCS treebanks (research-only
    licence; only the pairs are used, no text is written out)."""
    d, files = TOROT_OCS
    c: collections.Counter = collections.Counter()
    for rel in files:
        p = Path(root) / d / rel
        if not p.exists():
            continue
        for m in fm._P_TOKEN.finditer(p.read_text("utf-8")):
            a = dict(_P_ATTR.findall(m[1]))
            form, lem = a.get("form"), (a.get("lemma") or "").split("#")[0]
            if not form or not lem or lem == "?":
                continue
            pos = {"N": "noun", "A": "adj", "V": "verb"}.get(a.get("part-of-speech", "")[:1], "other")
            c[(fm.key_cu(form), fm.key_cu(lem), pos)] += 1
    return c


def read_round3_table(corpus: str, root: Path = ROOT) -> dict:
    """A round-3 table (lemma → ids) with every override file applied."""
    out = {}
    p = Path(root) / "data/research/formulas/mapping" / f"{corpus}.jsonl"
    for line in p.read_text("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["lemma"]] = tuple(r["lex_id"])
    return fm.apply_table_overrides(corpus, out, root=root)


_CU_H1ES = re.compile(r"^(?:н[еѣ])?(?:ес|соут|сѫт|сꙑ|сѫщ|сѫшт|сѫі|сѫ$)")


def ocs_mapping(maps: BslMappings, root: Path = ROOT) -> fm.LangMapping:
    """The kaikki OCS mapping with (a) the TOROT (form, lemma) pairs added to its form table and the
    TOROT POS to its POS sets, and (b) every TOROT lemma of the round-3 'cu' table (east.json and
    the other overrides applied) as a record that takes precedence over the kaikki record."""
    lm = maps.cu
    for (fk, lk, pos), n in torot_pairs(root).items():
        if lk in ("бꙑти", "небꙑти") and _CU_H1ES.match(fk):
            lk = "есмь"                           # suppletive *h₁es- forms of бꙑти (естъ, есмь, сѫтъ, нѣстъ)
        if fk and lk:
            lm.forms[fk][lk] += n
            lm.pos[lk].add(pos if pos != "other" else "other")
            lm.lemma_words.add(lk)
    ov = fm.load_overrides(root)["lemma"].get("cu", {})
    for lem, ids in read_round3_table("cu", root).items():
        k = fm.key_cu(lem)
        if not k or str(lm.rejected.get(k, "")).startswith("loan veto"):
            continue                              # the Balto-Slavic loan vetoes hold for CCMH (богъ, Derksen p. 49)
        how = "erratum" if lem in ov else "round3-cu"
        lm.recs[k] = fm.MapRec(k, lem, frozenset(ids), (f"cu:{lem}", "round3-table:cu"), how,
                               "high" if how == "erratum" else "medium", ("round3-cu",))
    for lem, (ids, _) in ov.items():            # unmaps of the round-3 table hold for CCMH too
        k = fm.key_cu(lem)
        if not ids and k in lm.recs:
            del lm.recs[k]
            lm.rejected[k] = "round-3 override unmap"
    lm.recs["есмь"] = fm.MapRec("есмь", "есмь", frozenset({"pie-root-h1es-be"}), ("cu:есмь", "suppletive:*h₁es-"),
                                "suppletive", "high", ("suppletive",))
    lm.pos["есмь"].add("verb")
    add_prefixed_verbs(lm)
    apply_key_rows(lm, key_rows(root))
    return lm


# ---------------------------------------------------------------- Derksen (facts only: headword, forms, PIE line, loan note)

DERKSEN_SLAVIC = "raw/books/text/derksen-slavic"
DERKSEN_BALTIC = "raw/books/text/derksen-baltic"
_DS_HEAD = re.compile(r"^\*(\S+(?: \S+){0,2}?)\s+((?:[mfn]\.|v\.|adj\.|adv\.|conj\.|prep\.|pron\.|num\.|prt\.|"
                      r"interj\.|part\.|indecl\.)[^‘']{0,40})[‘']([^’']{1,80})[’']")
# text-layer glyphs of Derksen's PIE lines (EDSIL private-use font) → standard notation
_DK_PIE = {"&": "₁", "'": "₂", "\x15": "₃", "\x14": "ʷ", "\x98": "ḱ", "\x06": "", "\x07": "o", "\x1f": "o",
           "_": "ʷ", "\"": "ʷ", "[": "", "!": "", "¥": "", "—": "", "„": "h"}


def derksen_pie(s: str) -> str:
    """Repair the damaged glyphs of a Derksen PIE line (h' → h₂, g\x14 → gʷ, \x98 → ḱ …)."""
    s = "".join(_DK_PIE.get(c, c) for c in (s or ""))
    s = re.sub(r"\bh\s*([123])", lambda m: "h" + "₁₂₃"[int(m[1]) - 1], s)
    return s.replace("hr", "h₂") if re.search(r"hr(?:[-\s]|$)", s) else s
_LOAN_NOTE = re.compile(r"(?<!not )(?<!no )(?:a |is )?(?:borrowing|borrowed|loanword|loan)\b[^.]{0,40}?"
                        r"(?:from|of)\s+(?:an?\s+)?([A-Z][a-z]+)", re.I)


def _page_no(lines: list[str]) -> str:
    for l in lines[:3]:
        if l.strip().isdigit():
            return l.strip()
    return ""


def _forms_after(text: str, tag: str) -> list[str]:
    """Words after 'Ru.', 'SCr.', 'OCS', 'Lith.' … (Latin transliteration; text-layer damage kept)."""
    out = []
    for m in re.finditer(r"(?:^|[\s;(])" + re.escape(tag) + r"\s+(?:\([^)]*\)\s*)?([^\s,;‘'(]+)", text):
        out.append(m[1])
    return out


def derksen_slavic_entries(root: Path = ROOT) -> list[dict]:
    """Derksen EDSIL entries: head (text-layer form; jers often damaged), gloss, printed page,
    daughter forms (OCS, Ru., SCr.), Lithuanian cognates, the PIE line, and a loan note if the
    entry calls the word a borrowing."""
    out, cur = [], None
    for fn in sorted((Path(root) / DERKSEN_SLAVIC).glob("p*.txt")):
        lines = fn.read_text("utf-8", errors="replace").splitlines()
        page = _page_no(lines)
        for l in lines:
            m = _DS_HEAD.match(l.strip())
            if m:
                cur = {"head": m[1], "pos": m[2].strip(), "gloss": m[3], "page": page, "file": fn.stem, "lines": []}
                out.append(cur)
                continue
            if cur is not None:
                cur["lines"].append(l)
    for e in out:
        text = "\n".join(e.pop("lines"))
        e["ocs"] = _forms_after(text, "OCS")
        e["ru"] = _forms_after(text, "Ru.")
        e["scr"] = _forms_after(text, "SCr.")
        e["lith"] = _forms_after(text, "Lith.")
        pm = re.search(r"^PIE\s*\n\s*(\*[^\n]+)", text, re.M)
        e["pie"] = pm[1].strip() if pm else ""
        lm = _LOAN_NOTE.search(text)
        e["loan"] = lm[0] if lm and not re.search(r"not (?:a |an )?(?:borrow|loan)", text[max(0, lm.start() - 30):lm.end()]) else ""
    return out


def derksen_baltic_entries(root: Path = ROOT) -> list[dict]:
    """Derksen EDBIL entries: Lithuanian headword (the line before 'LITH'), printed page, the LITH
    line, Slavic forms, the PIE line, a loan note."""
    out = []
    for fn in sorted((Path(root) / DERKSEN_BALTIC).glob("p*.txt")):
        lines = fn.read_text("utf-8", errors="replace").splitlines()
        page = _page_no(lines)
        idx = [i for i, l in enumerate(lines) if l.strip() in ("LITH", "OLITH", "OPR", "LATV")]
        heads = [i for i in idx if lines[i].strip() in ("LITH", "OLITH", "OPR") and i > 0
                 and not (i >= 2 and lines[i - 1].strip() in ("LITH", "LATV"))]
        for j, i in enumerate(heads):
            head = lines[i - 1].strip()
            if not head or " " in head.strip() and not re.match(r"^\S+ \d$", head):
                continue
            end = heads[j + 1] - 1 if j + 1 < len(heads) else len(lines)
            text = "\n".join(lines[i:end])
            pm = re.search(r"^PIE\s*\n\s*(\*[^\n]+)", text, re.M)
            lm = _LOAN_NOTE.search(text)
            out.append({"head": re.sub(r"\s+\d$", "", head), "page": page, "file": fn.stem,
                        "kind": lines[i].strip(), "lith": text.split("\n", 2)[1] if "\n" in text else "",
                        "ru": _forms_after(text, "Ru."), "scr": _forms_after(text, "SCr."),
                        "ocs": _forms_after(text, "OCS"),
                        "pie": pm[1].strip() if pm else "", "loan": lm[0] if lm else ""})
    return out


_RU_LAT = dict(zip("абвгдежзийклмнопрстуфхцчшщъыьэюя",
                   ["a", "b", "v", "g", "d", "e", "ž", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t",
                    "u", "f", "x", "c", "č", "š", "šč", "", "y", "", "e", "ju", "ja"]))


def latin_key(s: str) -> str:
    """Accent-free Latin key on which Derksen's transliterated Ru./SCr./OCS/Lith. forms meet ours."""
    s = (s or "").lower()
    if re.search(r"[а-яѣіѫѧꙑ]", s):
        s = fm.key_cu(s) if re.search(r"[ѣѫѧꙑ]", s) else key_ru(s)
        s = s.replace("оу", "у").replace("ѣ", "ě").replace("ѫ", "ǫ").replace("ѧ", "ę").replace("ꙑ", "ы")
        s = "".join(_RU_LAT.get(c, c) for c in s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("đ", "dj").replace("ł", "l")
    return re.sub(r"[^a-z]", "", s)


def derksen_index(root: Path = ROOT) -> dict[str, dict[str, list[dict]]]:
    """{'ru'|'sh'|'cu'|'lt': {latin key: [entries]}} over both dictionaries."""
    idx = {c: collections.defaultdict(list) for c in ("ru", "sh", "cu", "lt")}
    for e in derksen_slavic_entries(root):
        e["dict"] = "EDSIL"
        for c, f in (("ru", "ru"), ("sh", "scr"), ("cu", "ocs"), ("lt", "lith")):
            for w in e[f]:
                k = latin_key(w)
                if len(k) >= 2:
                    idx[c][k].append(e)
    for e in derksen_baltic_entries(root):
        e["dict"] = "EDBIL"
        k = latin_key(e["head"])
        if len(k) >= 2:
            idx["lt"][k].append(e)
        for c, f in (("ru", "ru"), ("sh", "scr"), ("cu", "ocs")):
            for w in e[f]:
                k = latin_key(w)
                if len(k) >= 2:
                    idx[c][k].append(e)
    return idx


def derksen_ids(e: dict, fz: fm.FuzzyPie) -> set:
    """Lexicon ids for an entry's PIE line (first starred form that FuzzyPie resolves as a whole form)."""
    for p in re.split(r"[,;]| or |/", derksen_pie(e.get("pie") or "")):
        p = p.strip(" ?.()")
        if not p.startswith("*"):
            continue
        ids, how = fz.lookup(p.split(" ")[0])
        if ids and how == "form" and len(ids) <= 3:
            return ids
    return set()


def add_derksen_lt(lm: fm.LangMapping, didx: dict, fz: fm.FuzzyPie, only=None) -> int:
    """EDBIL headword (unique accent-free key) → its PIE line, for Lithuanian keys the kaikki steps
    left unmapped (how 'derksen', confidence low). Entries with a loan note are skipped."""
    n = 0
    heads = collections.defaultdict(set)
    for k in set(lm.lemma_words) | set(lm.recs):
        heads[latin_key(k)].add(k)
    for lk, es in didx["lt"].items():
        es = [e for e in es if e["dict"] == "EDBIL"]
        if len({(e["head"], e["page"]) for e in es}) != 1:
            continue
        e = es[0]
        if e["loan"] or not e["pie"]:
            continue
        ks = heads.get(lk, set())
        if len(ks) != 1:
            continue
        k = next(iter(ks))
        if k in lm.recs or (only is not None and k not in only):
            continue
        ids = derksen_ids(e, fz)
        if not ids:
            continue
        lm.recs[k] = fm.MapRec(k, k, frozenset(ids), (f"lt:{k}", f"derksen-EDBIL:p{e['page']}:{e['head']}",
                                                      f"ine-pro:{e['pie'][:40]}"), "derksen", "low", ("derksen",))
        n += 1
    return n


# ---------------------------------------------------------------- tables

MAPPING_DIR = "data/research/formulas/mapping"
TABLES = {"vuk": "Vuk Karadžić, Serbian epic and lyric songs (sh)", "byliny": "Russian byliny (ru)",
          "dainos": "Lithuanian dainos (lt)", "ccmh": "CCMH Old Church Slavonic (cu)"}
MAPPING_LICENCE = {"chain": "kaikki/Wiktionary CC BY-SA 4.0", "desc": "kaikki/Wiktionary CC BY-SA 4.0",
                   "lexicon": "kaikki/Wiktionary CC BY-SA 4.0 (via the lexicon)",
                   "base": "kaikki/Wiktionary CC BY-SA 4.0", "root": "kaikki/Wiktionary CC BY-SA 4.0",
                   "derksen": "facts from Derksen 2008/2015 (Brill; headword-PIE link only)",
                   "round3-cu": "round-3 cu table (TOROT lemmas, CC BY-NC-SA research only; kaikki CC BY-SA)",
                   "erratum": "hand override (dictionary note)"}


def read_table(corpus: str, root: Path = ROOT) -> dict:
    """lemma string → lexicon ids, with the mapping overrides applied (for the Stage C builder)."""
    out = {}
    for line in (Path(root) / MAPPING_DIR / f"{corpus}.jsonl").read_text("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["lemma"]] = tuple(r["lex_id"])
    return fm.apply_table_overrides(corpus, out, root=root)


def lemmatizer(corpus: str, maps: BslMappings, lm: fm.LangMapping | None = None) -> BslLemmatizer:
    """The lemmatizer for one corpus (ccmh: pass the ocs_mapping result as lm)."""
    if corpus == "vuk":
        return BslLemmatizer(maps.sh, norm=vuk_norm, variants=vuk_variants)
    if corpus == "byliny":
        return BslLemmatizer(maps.ru, norm=ru_norm_ocr, variants=ru_variants)
    if corpus == "dainos":
        return BslLemmatizer(maps.lt, norm=lt_norm, variants=lt_variants)
    if corpus == "ccmh":
        return BslLemmatizer(lm or maps.cu)
    raise KeyError(corpus)


def corpus_words(corpus: str, text: str) -> list[str]:
    """Word tokens of one unit's text (CCMH: transliterated to Cyrillic; abbreviations under titlo
    and words with unreadable letters dropped)."""
    if corpus == "ccmh":
        return [c for c in (ccmh_word(w) for w in ccmh_words(text)) if c]
    if corpus == "byliny":
        # Preserve OCR yat ($) inside Cyrillic words, including final yat.
        # The normal ru_norm_ocr + dictionary path resolves the joined form.
        return re.findall(r"[А-Яа-яЁёѣѢіІ]+(?:\$[А-Яа-яЁёѣѢіІ]+)*\$(?:[А-Яа-яЁёѣѢіІ]+)?|" + _TOKEN.pattern, text)
    return words(text)


def is_name(corpus: str, surface: str, position: int) -> bool:
    """A capitalised word that does not begin its line (verse line, OCR line) is taken as a proper
    name (Иве, Марко, Добрыня): its lemma's etymon (iva 'willow', marka) is not the name's, so the
    Stage C builder should not map it. CCMH has no case distinction (upper case marks letters)."""
    return corpus != "ccmh" and position > 0 and surface[:1].isupper()


UNITS = {"vuk": vuk_units, "byliny": byliny_units, "dainos": dainos_units, "ccmh": ccmh_units}


VARIANT_KEY = {"sh": lambda k: k.replace("ije", "e").replace("je", "e"),
               "ru": lambda k: key_ru(k, True), "lt": lambda k: key_lt(k, True), "cu": lambda k: k}


def map_lemma(lem: str, lm: fm.LangMapping, gmap: dict, max_groups: int = fs.MAX_GROUPS) -> fm.MapRec | None:
    """A lemmatizer string → MapRec. Stricter than fm.multi_lemma_mapping: a union 'a|b' is mapped
    only if every part is mapped and all parts agree on the root groups (a part without a mapping,
    such as a loanword or a function word, leaves the union unmapped)."""
    if not lem or lem.startswith("?"):
        return None
    parts = lem.split("|")
    hits = [lm.recs.get(p) for p in parts]
    if any(h is None for h in hits):
        # an unmapped part does not block the union when it is a spelling variant of a mapped part
        # (ekavian videti beside ijekavian vidjeti), a word of the same stem (drag|draga,
        # udariti|udar: common prefix of ≥ 4 letters, and not itself a rejected loan), or a junk key
        # from a kaikki form-of string (over 20 letters)
        vk = VARIANT_KEY.get(lm.lang, lambda x: x)
        mp = [p for p, h in zip(parts, hits) if h is not None]
        if not mp:
            return None
        mapped = {vk(p) for p in mp}
        def lcp(a, b):
            n = 0
            while n < min(len(a), len(b)) and a[n] == b[n]:
                n += 1
            return n
        for p, h in zip(parts, hits):
            if h is not None or len(p) > 20 or vk(p) in mapped:
                continue
            if p in lm.rejected or p in getattr(lm, "etym_keys", ()) or not any(lcp(p, m) >= 4 for m in mp):
                return None                  # a word with an etymology of its own (vetoed or unresolved) blocks
        hits = [h for h in hits if h is not None]
    groups = {frozenset(gmap.get(x, x) for x in h.ids) for h in hits}
    if len(groups) != 1 or len(next(iter(groups))) > max_groups:
        return None
    if len(hits) == 1:
        return hits[0]
    ids = frozenset().union(*(h.ids for h in hits))
    h = hits[0]
    return fm.MapRec(lem, "|".join(x.word for x in hits), ids, h.path, h.how, "low", h.sources + ("form-ambiguous",),
                     h.gloss)
