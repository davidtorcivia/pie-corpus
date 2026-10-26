"""Old Norse (Menota, IcePaHC), Old High German and Old Saxon (ReA) lemma → PIE
tables for Phase 8c Stage C.

All four corpora carry their own lemmas, so the tables are keyed by the
corpus lemma string the loaders below yield (Token.lemma):

  menota   Menota TEI-P5, West Norse documents (catalogue language isl, nor,
           non; the Old Swedish and Old Danish texts are left out). Lemmatized
           documents: the `lemma` attribute (entities decoded). Unlemmatized
           ones (Codex Wormianus, the Hauksbók Vǫluspá, the c. 1700 Heimskringla
           copies, law codes): the normalized or diplomatic form looked up in
           a form → lemma table built from the lemmatized documents (only
           forms whose top lemma has at least two thirds of the votes).
           CC BY-SA 4.0.
  icepahc  IcePaHC 2024.03 `.tagged` files (word, tag, lemma); the lemmas are
           Modern Icelandic spellings (maður, vetur, búa). CC BY 4.0.
  rea-goh  Referenzkorpus Altdeutsch 1.2 (relANNIS), tokens with lang goh.
  rea-osx  the same, lang osx. ReA is CC BY-NC-SA 3.0: research use only.
           A lemma annotated with alternatives (`abawesan¦…¦wesan¦sin`) is
           given as the de-duplicated alternatives joined with '|'.

Lemma → PIE: formula_search_multi's chain / desc / lexicon / form-of / base
steps over the kaikki Old Norse, Old High German and Old Saxon dumps and the
Proto-Germanic, Proto-West-Germanic and Proto-Norse dumps, plus

  later-is   an Old Norse headword without a mapping takes the Proto-Germanic
             (or PIE) chain of a Modern Icelandic entry that names it as its
             source ({{inh|is|non|X}});
  is-bridge  an IcePaHC lemma goes to the Old Norse word its Icelandic kaikki
             entry inherits from, then to that word's mapping; failing that,
             to Modern → Old Norse spelling variants (maður → maðr, -ast →
             -ask, ft → pt, vo → vá) that name exactly one mapped headword;
  loose      a lemma whose exact key is unknown takes the accent-free key
             only when every headword under that key has the same root groups.

Nothing under raw/ is executed or imported; files are read as text, XML-ish
text, TSV or JSON. Tables hold dictionary headwords, corpus lemmas and ids,
never corpus text.
"""

from __future__ import annotations

import collections
import gzip
import html
import json
import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path

from . import formula_search as fs
from . import formula_search_multi as fm
from .formula_search import Token

ROOT = fs.ROOT
KD = fm.KD
MAPPING_DIR = "data/research/formulas/mapping"
OVERRIDE_FILE = "data/research/formulas/mapping-overrides/germanic-new.json"
MENOTA = "raw/daughters/oldnorse-menota"
ICEPAHC = "raw/daughters/oldnorse-icepahc/extract/icepahc-v2024.03/tagged"
REA = "raw/daughters/ohg-oldsaxon-rea/extract/corpora"
KAIKKI_ALL = "raw/daughters/kaikki-all-20261021/raw-wiktextract-data.jsonl.gz"

CORPORA = {
    "menota": {"lang": "non", "name": "Menota (Old Norse, West Norse documents)",
               "licence": "CC BY-SA 4.0 (Menota); mapping sources kaikki/Wiktionary CC BY-SA 4.0",
               "research_only": False},
    "icepahc": {"lang": "is", "name": "IcePaHC 2024.03 (Old Icelandic part and later)",
                "licence": "CC BY 4.0 (IcePaHC); mapping sources kaikki/Wiktionary CC BY-SA 4.0",
                "research_only": False},
    "rea-goh": {"lang": "goh", "name": "Referenzkorpus Altdeutsch 1.2, Old High German",
                "licence": "CC BY-NC-SA 3.0 (ReA): NC, research only; mapping sources kaikki/Wiktionary CC BY-SA 4.0",
                "research_only": True},
    "rea-osx": {"lang": "osx", "name": "Referenzkorpus Altdeutsch 1.2, Old Saxon",
                "licence": "CC BY-NC-SA 3.0 (ReA): NC, research only; mapping sources kaikki/Wiktionary CC BY-SA 4.0",
                "research_only": True},
}

# ---------------------------------------------------------------- keys and registry (additive)
#
# Form rows in the override files must not use these language codes:
# load_overrides keys every form row with KEYS[lang] and may run without
# this module imported. These corpora are lemmatized and need no form rows.


def key_wgm(s: str, loose: bool = False) -> str:
    """Old High German / Old Saxon: lowercase, đ → ð, ƀ → b, ƿ → w; length
    marks kept unless loose. Loose also folds the spelling variants of
    the editions and dictionaries: ð/th/þ → d, c/q(u) → k, uu → w, v → f,
    ph → pf, double consonants single."""
    s = unicodedata.normalize("NFC", (s or "").lower().strip("*-"))
    s = s.replace("đ", "ð").replace("ƀ", "b").replace("ƿ", "w").replace("ȥ", "z")
    if not loose:
        return re.sub(r"[^a-zþðæāēīōūâêîôûáéíóúœ]", "", s)
    s = fm._nfd_strip(s).replace("æ", "ae").replace("œ", "oe")
    s = re.sub(r"[^a-zþð]", "", s)
    s = s.replace("th", "d").replace("þ", "d").replace("ð", "d")
    s = s.replace("qu", "kw").replace("q", "k").replace("ck", "k").replace("c", "k")
    s = s.replace("uu", "w").replace("v", "f").replace("ph", "pf")
    return re.sub(r"(.)\1+", r"\1", s)


fm.KEYS.setdefault("goh", key_wgm)
fm.KEYS.setdefault("osx", key_wgm)
fm.KEYS.setdefault("is", fm.key_non)
for _c, _anc in (("goh", ["gmw-pro", "gem-pro"]), ("osx", ["gmw-pro", "gem-pro"]),
                 ("is", ["non", "gmq-pro", "gem-pro"])):
    fm.ANCESTORS.setdefault(_c, _anc)
fm.LANGS.setdefault("goh", fm.LangSpec("goh", "Old High German",
                                       "kaikki-oldhighgerman/kaikki.org-dictionary-OldHighGerman.jsonl",
                                       ("Old High German",), desc_codes=("goh",)))
fm.LANGS.setdefault("osx", fm.LangSpec("osx", "Old Saxon", "kaikki-oldsaxon/kaikki.org-dictionary-OldSaxon.jsonl",
                                       ("Old Saxon",), desc_codes=("osx",)))
fm.LANGS.setdefault("is", fm.LangSpec("is", "Icelandic", None, ("Icelandic",), desc_codes=("is",)))

# ---------------------------------------------------------------- Menota

# entities of the Menota entity list that occur in lemma and normalized-form
# attributes (the rest are standard HTML entities)
MENOTA_ENTITIES = {
    "oogon": "ǫ", "Oogon": "Ǫ", "oogonacute": "ǫ́", "Oogonacute": "Ǫ́", "aeligacute": "ǽ", "AEligacute": "Ǽ",
    "oslashacute": "ǿ", "Oslashacute": "Ǿ", "oelig": "œ", "OElig": "Œ", "oeligacute": "œ́", "eogon": "ę",
    "Eogon": "Ę", "eogonacute": "ę́", "slong": "s", "slongdes": "s", "rrot": "r", "rscapdot": "r",
    "dstrok": "đ", "Dstrok": "Đ", "zstrok": "z", "ezh": "z", "inodot": "i", "jnodot": "j", "jnodotenl": "j",
    "jacute": "í", "vacute": "ú", "ydot": "y", "fins": "f", "Fins": "F", "vins": "v", "vinsdot": "v",
    "ocurl": "ǫ", "Ocurl": "Ǫ", "oogoncurl": "ǫ", "oslashcurl": "ø", "acurl": "a", "ecurl": "e", "ucurl": "u",
    "avlig": "au", "AVlig": "Au", "avligacute": "au", "aylig": "ey", "aalig": "á", "aaligacute": "á",
    "aaligdblac": "á", "adblac": "á", "aolig": "ǫ", "aoligacute": "ǫ́", "drotvlig": "dv", "gethlig": "gð",
    "et": "ok", "etslash": "ok", "etfin": "ok", "combacute": "\u0301", "drot": "d", "drotenl": "d",
}
# entity suffixes for letter variants (small capitals, enlarged and uncial forms, descenders,
# insular and rotunda forms, dots): the entity stands for its base letter
_ENT_VARIANT = re.compile(r"^([A-Za-z])(?:nodot)?(?:scap|enl|unc|uncdes|uncclose|des|rdes|lrleg|rot|ins|dot|"
                          r"run|uslst|slst|close|loop|curl)+(?:dot|rdes|des)?$")
# Unicode letter variants of the diplomatic level → their base letters
MENOTA_CHARS = str.maketrans({"ſ": "s", "ꝼ": "f", "Ꝼ": "F", "ꝛ": "r", "ꝩ": "v", "Ꝩ": "V", "ı": "i", "ȷ": "j",
                              "ꞇ": "t", "ꝺ": "d", "ʀ": "r", "ẏ": "y", "ꜳ": "á", "ꜵ": "ǫ", "ɴ": "n", "ɢ": "g",
                              "ꜱ": "s", "ᴍ": "m", "ꜹ": "au", "ŋ": "ng", "\u2060": "", "ʜ": "h", "ʟ": "l", "ᴋ": "k"})
_ENT = re.compile(r"&([A-Za-z][A-Za-z0-9]*);")


def menota_decode(s: str) -> str:
    """Menota entity text → Unicode (&oogon; → ǫ, &aeligacute; → ǽ, &eth; → ð,
    &nscap; → n, &slong; and ſ → s); unknown entities (abbreviation and
    punctuation signs) are dropped."""
    def one(m):
        n = m.group(1)
        if n in MENOTA_ENTITIES:
            return MENOTA_ENTITIES[n]
        u = html.unescape(m.group(0))
        if u != m.group(0):
            return u
        v = _ENT_VARIANT.match(n)
        return v.group(1) if v else ""
    return unicodedata.normalize("NFC", _ENT.sub(one, s or "").translate(MENOTA_CHARS))


MENOTA_CONTENT = {"NC": "noun", "NP": "noun", "AJ": "adj", "VB": "verb"}
WEST_NORSE = ("isl", "nor", "non")
_M_TOKEN = re.compile(r"<w\b([^>]*)>(.*?)</w>|<pc\b[^>]*>(.*?)</pc>|<(pb|lb|lg|l|s|p|div)\b([^>]*?)/?>|</(lg|l|s|p)>",
                      re.S)
_M_ATTR = re.compile(r'([\w:.-]+)="([^"]*)"')
_M_LEVEL = {lv: re.compile(rf"<me:{lv}>(.*?)</me:{lv}>", re.S) for lv in ("norm", "dipl", "facs")}
_TAGS = re.compile(r"<[^>]+>")


def menota_catalogue(root: Path = ROOT) -> dict:
    return {d["documentId"]: d for d in
            json.loads((Path(root) / MENOTA / "catalogue-list.json").read_text("utf-8"))["documents"]}


@dataclass
class MenotaWord:
    doc: str
    lemma: str | None      # decoded lemma attribute (None if absent)
    msa: str               # word-class code (NC, VB, …) or ''
    form: str              # normalized form if given, else diplomatic (decoded, tags off)
    folio: str
    line: str
    stanza: str | None
    sent: int


def _level(body: str, lv: str) -> str:
    m = _M_LEVEL[lv].search(body)
    if not m:
        return ""
    return menota_decode(_TAGS.sub("", m.group(1))).strip()


def reviewed_menota_lemma(lemma: str | None, msa: str, form: str,
                          doc: str = "", previous: str = "") -> str | None:
    """Keep reviewed names and homonyms separate using source annotation.

    Evidence and loci: stageCS/error-verdicts-other.jsonl. Do not infer a
    name from capitalization alone, or replace a common-word homonym.
    """
    names = {"einarr", "helga", "helgi", "bera", "yngvarr", "haraldr", "oddr", "bjǫrn"}
    if lemma in names and msa.startswith("xNP"):
        return lemma + " (name)"
    if lemma == "þverá" and form == "Þverá" and doc == "AM-132-fol-Droplaugarsona-saga":
        return lemma + " (name)"
    if lemma == "máni" and doc == "AM-113-b-fol" and previous == "Þorkels":
        return lemma + " (name)"
    if lemma == "egg" and msa.startswith("xNC") and "gF" in msa.split():
        return "egg@edge"
    if lemma == "nema" and msa.startswith("xVB"):
        return "nema@take"
    if lemma == "vár" and msa.startswith("xNC"):
        return "vár@spring"
    if lemma == "niðr" and msa.startswith("xNC"):
        return "niðr@kinsman"
    return lemma


def menota_words(path: Path, doc: str) -> list[MenotaWord]:
    """The <w> elements of one Menota file in text order, with folio/line
    (pb/lb), stanza (lg n) and a sentence counter (a full stop, colon,
    question or exclamation mark in a <pc>, or an <s>/<p> boundary)."""
    t = path.read_text("utf-8")
    # Comments can contain apparent XML tags; remove them before tokenization,
    # not with the generic tag stripper (which stops at an internal '>').
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    i = t.find("<text")
    t = t[i:] if i >= 0 else t
    out, folio, line, stanza, sent = [], "", "", None, 0
    for m in _M_TOKEN.finditer(t):
        if m.group(1) is not None:
            a = dict(_M_ATTR.findall(m.group(1)))
            body = m.group(2)
            lem = menota_decode(a["lemma"]) if "lemma" in a else None
            msa = a.get("me:msa", "")
            form = _level(body, "norm") or _level(body, "dipl")
            lem = reviewed_menota_lemma(lem, msa, form, doc, out[-1].form if out else "")
            out.append(MenotaWord(doc, lem, msa[1:3] if msa.startswith("x") else "", form, folio, line, stanza, sent))
        elif m.group(3) is not None:
            p = menota_decode(_TAGS.sub("", m.group(3)))
            if re.search(r"[.:!?]", p):
                sent += 1
        elif m.group(4):
            a = dict(_M_ATTR.findall(m.group(5) or ""))
            tag = m.group(4)
            if tag == "pb":
                folio = a.get("n", folio)
            elif tag == "lb":
                line = a.get("n", line)
            elif tag == "lg":
                stanza = a.get("n") or stanza
            elif tag in ("s", "p", "div"):
                sent += 1
        elif m.group(6) in ("s", "p"):
            sent += 1
        elif m.group(6) == "lg":
            stanza = None
    return out


def menota_form_key(s: str) -> str:
    return fm.key_non(s, True)


def menota_reviewed_tokens(root: Path = ROOT) -> dict:
    """Source-coordinate sense repairs, applied after form-table inference.

    Each row cites its source and dictionary in the wave-2 Norse ledger.
    Keeping these out of the voting table prevents a local sense decision
    from changing the analysis of the same surface form elsewhere.
    """
    path = Path(root) / "data/research/formulas/menota-reviewed-w2.json"
    if not path.exists():
        return {}
    return {(r["doc"], r["folio"], r["line"], r["form"]): r
            for r in json.loads(path.read_text("utf-8"))}


def reviewed_menota_token(w: MenotaWord, lemma: str, msa: str, rules: dict) -> tuple[str, str]:
    names = {"án", "hróðný", "gunnarr", "eyvindr", "kári", "freyr", "bjarni", "bróðir",
             "haraldr", "mímir", "yngvi"}
    if msa == "NP" and lemma.lower() in names:
        return lemma + " (name)", msa
    row = rules.get((w.doc, w.folio, w.line, w.form))
    if row and lemma == row["given_lemma"]:
        return row["lemma"], row["tag"]
    return lemma, msa


def menota_documents(root: Path = ROOT, languages=WEST_NORSE) -> list[tuple[str, dict]]:
    cat = menota_catalogue(root)
    return [(d, cat[d]) for d in sorted(cat) if cat[d].get("language") in languages]


def load_menota(root: Path = ROOT, languages=WEST_NORSE, min_share: float = 2 / 3, min_votes: int = 3) -> list[Token]:
    """Menota West Norse tokens (content: NC, NP, AJ, VB). Units: sentence,
    stanza (verse documents), folio, doc. Lemma: the corpus lemma; in a
    document without lemmas, the form-table lemma of its normalized or
    diplomatic form (a form key seen at least `min_votes` times in the
    lemmatized documents, its top lemma holding `min_share` of the votes;
    otherwise '?' + form key). Surface forms remain in memory for reviewed
    token-level sense corrections; mapping tables contain no running text."""
    root = Path(root)
    reviewed = menota_reviewed_tokens(root)
    docs = menota_documents(root, languages)
    words = {d: menota_words(root / MENOTA / "xml" / f"{d}.xml", d) for d, _ in docs}
    votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for ws in words.values():
        for w in ws:
            if w.lemma and w.form:
                votes[menota_form_key(w.form)][(w.lemma, w.msa)] += 1
    table = {}
    for k, c in votes.items():
        (lem, msa), n = c.most_common(1)[0]
        if n >= min_votes and n >= min_share * sum(c.values()) and len(k) >= 2:
            table[k] = (lem, msa)
    toks: list[Token] = []
    for d, meta in docs:
        lemmatized = any(w.lemma for w in words[d])
        for w in words[d]:
            lem, msa, src = w.lemma, w.msa, "corpus"
            if not lemmatized:
                k = menota_form_key(w.form)
                if not k:
                    continue
                lem, msa = table.get(k, ("?" + k, ""))
                src = "form-table" if not lem.startswith("?") else "unknown"
            elif not lem:
                continue
            corrected, tag = reviewed_menota_token(w, lem, msa, reviewed)
            if (corrected, tag) != (lem, msa):
                lem, msa, src = corrected, tag, "reviewed"
            if msa == "FW" or lem in ("Latin.expression", "unass.", "?"):
                continue
            pos = MENOTA_CONTENT.get(msa, "other")
            content = msa in MENOTA_CONTENT or (src == "unknown")
            u = {"sentence": f"{d}.{w.sent}", "folio": f"{d}.{w.folio}", "doc": d, "lemma_source": src, "tag": msa}
            if w.stanza:
                u["stanza"] = f"{d}.{w.stanza}"
            toks.append(Token("menota", lem, w.form, f"{d} {w.folio}:{w.line}".strip(), u, content, pos))
    return toks

# ---------------------------------------------------------------- IcePaHC

ICE_CONTENT = re.compile(r"^(N|NS|NPR|NPRS|ADJ|ADJR|ADJS|VB\w*|VAN|VAG|BE\w*|HV\w*|MD\w*|RD\w*|DO\w*)(-[NADG])?$")


def icepahc_files(root: Path = ROOT, max_year: int | None = 1400) -> list[Path]:
    fs_ = sorted((Path(root) / ICEPAHC).glob("*.tagged"))
    return [f for f in fs_ if max_year is None or int(f.name[:4]) <= max_year]


def load_icepahc(root: Path = ROOT, max_year: int | None = 1400) -> list[Token]:
    """IcePaHC .tagged (word, tag, lemma; blank line = sentence). Content:
    nouns, proper nouns, adjectives, all verbs (VB, BE, HV, MD, RD, DO and
    the participles VAN/VAG), as for PROIEL's V. Units: sentence, text.
    Files dated after max_year are skipped (None: all)."""
    toks = []
    for f in icepahc_files(root, max_year):
        stem = f.name[: -len(".tagged")]
        s = 0
        for line in f.read_text("utf-8").splitlines():
            if not line.strip():
                s += 1
                continue
            p = line.split("\t")
            if len(p) != 3:
                continue
            w, tag, lem = p
            if not re.search(r"\w", lem) or tag in (".", ",", '"', "FW"):
                continue
            tag1 = tag.split("+")[-1] if tag.startswith(("Q+", "ONE+")) else tag
            content = bool(ICE_CONTENT.match(tag1))
            pos = "verb" if re.match(r"^(VB|VA|BE|HV|MD|RD|DO)", tag1) else "adj" if tag1.startswith("ADJ") else \
                "noun" if tag1.startswith("N") else "other"
            toks.append(Token("icepahc", lem, "", f"{stem} s{s + 1}", {"sentence": f"{stem}.{s}", "text": stem,
                                                                       "tag": tag1}, content, pos))
    return toks

# ---------------------------------------------------------------- ReA (relANNIS)

REA_LANG = {"rea-goh": {"goh", "ohg"}, "rea-osx": {"osx", "oxs"}}
REA_CONTENT = {"NA": "noun", "NE": "noun", "VV": "verb", "VA": "verb", "VM": "verb", "ADJ": "adj", "ADJA": "adj",
               "ADJD": "adj", "ADJN": "adj", "ADJO": "adj", "ADJS": "adj"}
_REA_WANT = {"lemma", "posLemma", "lang", "translation", "verse", "document", "clause", "line"}


def rea_lemma(lemma: str) -> str:
    """'abawesan¦abasin¦wesan¦sin' → 'abawesan|abasin|wesan|sin' (alternatives,
    de-duplicated in order); a single lemma is returned as written."""
    parts = []
    for p in re.split(r"[¦,]", lemma or ""):
        p = p.strip()
        if p and p not in parts:
            parts.append(p)
    return "|".join(parts)


def rea_is_content(pos_lemma: str) -> bool:
    parts = [p for p in (pos_lemma or "").split("¦") if p]
    return bool(parts) and all(p in REA_CONTENT for p in parts)


def rea_tokens(root: Path = ROOT, subcorpora=None) -> list[dict]:
    """Token dicts {sub, doc, lemma, posLemma, lang, translation, verse} for
    every lemma span of the ReA relANNIS export (node.annis spans joined to
    node_annotation.annis by document and token range)."""
    base = Path(root) / REA
    out = []
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        if subcorpora and d.name not in subcorpora:
            continue
        spans, docs = {}, {}
        for line in (d / "corpus.annis").read_text("utf-8").splitlines():
            p = line.split("\t")
            if len(p) > 2 and p[2] == "DOCUMENT":
                docs[p[0]] = p[1]
        with open(d / "node.annis", encoding="utf-8") as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) > 9 and p[3] == "default_ns":
                    spans[p[0]] = (p[2], int(p[8]), int(p[9]))
        tok: dict = collections.defaultdict(dict)
        verses: dict = collections.defaultdict(list)
        with open(d / "node_annotation.annis", encoding="utf-8") as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) < 4 or p[2] not in _REA_WANT or p[0] not in spans:
                    continue
                sp = spans[p[0]]
                if p[2] in ("verse", "line"):
                    verses[sp[0]].append((sp[1], sp[2], p[3]))
                elif p[2] in ("lemma", "posLemma", "lang", "translation"):
                    tok[sp][p[2]] = p[3]
        for k in verses:
            verses[k].sort()
        for sp in sorted(tok, key=lambda x: (x[0], x[1])):
            t = tok[sp]
            if "lemma" not in t:
                continue
            vs = verses.get(sp[0], [])
            v = next((x[2] for x in vs if x[0] <= sp[1] <= x[1]), None)
            out.append({"sub": d.name.replace("DDD-AD-", ""), "doc": docs.get(sp[0], sp[0]), "lemma": t["lemma"],
                        "posLemma": t.get("posLemma", ""), "lang": t.get("lang", ""),
                        "translation": t.get("translation", ""), "verse": v, "start": sp[1]})
    return out


def load_rea(corpus: str, root: Path = ROOT, rows: list[dict] | None = None) -> list[Token]:
    """corpus 'rea-goh' or 'rea-osx': ReA tokens of that language (mixed
    codes such as osx-goh and gmh/Latin tokens are left out). Content:
    posLemma NA, NE, VV, VA, VM, ADJ* (every alternative). Units: verse
    (where the edition numbers verses), doc."""
    want = REA_LANG[corpus]
    toks = []
    for r in rows if rows is not None else rea_tokens(root):
        if r["lang"] not in want:
            continue
        lem = rea_lemma(r["lemma"])
        if not lem or lem in ("-", "_"):
            continue
        u = {"doc": f"{r['sub']}/{r['doc']}", "gloss": r["translation"], "tag": r["posLemma"]}
        if r["verse"]:
            u["verse"] = f"{r['sub']}/{r['doc']}.{r['verse']}"
        first = r["posLemma"].split("¦")[0] if r["posLemma"] else ""
        toks.append(Token(corpus, lem, "", f"{r['sub']} {r['doc']}" + (f" v{r['verse']}" if r["verse"] else ""),
                          u, rea_is_content(r["posLemma"]), REA_CONTENT.get(first, "other")))
    return toks

# ---------------------------------------------------------------- entries cut from the all-languages dump
#
# The Icelandic entries and the Proto-West-Germanic and Proto-Norse pages are
# not in a per-language dump (the split proto-west-germanic.jsonl holds 72
# gmw-pro pages and 4,138 gem-pro lines), so they are streamed from the
# all-languages dump (≈1 min), or read from a cache directory of cut files.

CUT_CODES = ("is", "gmw-pro", "gmq-pro")


def kaikki_cut(root: Path = ROOT, codes=CUT_CODES, cache: Path | None = None) -> dict[str, list[str]]:
    """{code: raw JSON lines} of the entries whose top-level lang_code is in
    `codes`. With `cache`, files mapgmc-<code>.jsonl there are read if present
    and written if not."""
    out: dict[str, list[str]] = {c: [] for c in codes}
    cache = Path(cache) if cache else None
    if cache and all((cache / f"mapgmc-{c}.jsonl").exists() for c in codes):
        for c in codes:
            out[c] = (cache / f"mapgmc-{c}.jsonl").read_text("utf-8").splitlines()
        return out
    pre = {f'"lang_code": "{c}"': c for c in codes}
    with gzip.open(Path(root) / KAIKKI_ALL, "rt", encoding="utf-8") as fh:
        for line in fh:
            for k, c in pre.items():
                if k in line:
                    if json.loads(line).get("lang_code") == c:
                        out[c].append(line.rstrip("\n"))
                    break
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        for c in codes:
            (cache / f"mapgmc-{c}.jsonl").write_text("".join(x + "\n" for x in out[c]), "utf-8")
    return out


def _is_affix(term: str) -> bool:
    t = term.lstrip("*")
    return t.startswith("-") or t.endswith("-")


def proto_bases(d: dict, code: str) -> list[str]:
    """Same-language base of a proto-language derivative: the one non-affix
    part of an {{af}}/{{suffix}} template or of an {{etymon|…|:af|…}}
    (*hailagaz ← *hailaz + *-gaz). parse_entry misses parts written '*-gaz'."""
    out = []
    for t in d.get("etymology_templates") or []:
        name, a = t.get("name"), t.get("args") or {}
        parts = []
        if name in ("af", "affix", "suffix", "suf", "compound", "com") and a.get("1") == code:
            parts = [fm._strip_inline(a[k]) for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int)]
        elif name in ("etymon", "ety"):
            kind = None
            for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int):
                v = (a[k] or "").strip()
                if v.startswith(":"):
                    kind = v[1:].split("<")[0]
                elif kind in ("af", "affix", "suf", "compound") and v.startswith("*"):
                    parts.append(fm._strip_inline(v))
        parts = [x for x in parts if x]
        content = [x for x in parts if not _is_affix(x)]
        if len(content) == 1 and len(parts) >= 2 and content[0] not in out:
            out.append(content[0])
    return out


def add_proto(protos: fm.ProtoDB, code: str, lines, want=()):
    """Proto-language pages (raw JSON lines) into a ProtoDB, as its own reader
    does, with proto_bases added to each entry's bases."""
    want = set(want)
    for line in lines:
        d = json.loads(line)
        if d.get("lang_code") not in (None, code):
            continue
        e = fm.parse_entry(d, code)
        e.bases = [b for b in e.bases if not _is_affix(b)]
        for b in proto_bases(d, code):
            if b not in e.bases:
                e.bases.append(b)
        protos.entries[(code, fs.PieIndex.proto_key(e.word))].append(e)
        if want and d.get("descendants"):
            fm._walk_desc(d["descendants"], code, e.word, want, protos.desc)


_AFFIX_POS = {"prefix", "suffix", "affix", "interfix", "infix", "circumfix"}


class BaseResolver(fm.Resolver):
    """fm.Resolver plus
      * a proto-language derivative's base: a PGmc page with no etymon of
        its own but an affix template (*hailagaz ← *hailaz) takes its
        base's chain (how 'base', so confidence low);
      * no chain through an affix page (*ga-, *-ī): a word is not mapped to
        the etymon of its prefix or suffix;
      * proto-level corrections ('proto' rows of the override file
        germanic-new.json: a PGmc / PWGmc term → corrected ids, or none),
        which reach every daughter word whose chain passes the term."""

    def __init__(self, idx, protos, kinds, pseudo: bool = True, fixes: dict | None = None):
        super().__init__(idx, protos, kinds, pseudo)
        self.fixes = fixes or {}

    def resolve(self, code: str, term: str, depth: int = 0):
        key = (code, fs.PieIndex.proto_key(term))
        if key in self.fixes:
            ids, note = self.fixes[key]
            return fm.Hit(frozenset(ids), (f"{code}:{term}", "erratum:" + note), "chain", 1) if ids else None
        if code != "ine-pro":
            t = (term or "").lstrip("*")
            ents = self.protos.get(code, term)
            if t.startswith("-") or (ents and all(e.pos in _AFFIX_POS for e in ents)):
                return None
        return super().resolve(code, term, depth)

    def entry_hit(self, e: fm.Entry, code: str, depth: int = 0):
        h = super().entry_hit(e, code, depth)
        if (h is None or not h.specific) and e.bases and code in fm.PROTO_DUMPS and depth < 5:
            for b in e.bases:
                hb = self.resolve(code, b, depth + 1)
                if hb and hb.specific:
                    return fm.Hit(hb.ids, (f"base:{b}",) + hb.path, "base", hb.steps + 1, hb.disputed)
        return h


def icelandic_entries(lines) -> list[fm.Entry]:
    out = []
    for line in lines:
        d = json.loads(line)
        if d.get("lang_code") == "is":
            out.append(fm.parse_entry(d, "is", keep_forms=False))
    return out

# ---------------------------------------------------------------- Modern Icelandic → Old Norse spelling


def modern_to_old_variants(lemma: str) -> list[str]:
    """Candidate Old Norse spellings of a Modern Icelandic lemma, most
    likely first (maður → maðr; konungur → konungr; andast → andask;
    eftir → eptir; svo → svá; -legur → -ligr). The lemma itself is not
    included."""
    s = unicodedata.normalize("NFC", (lemma or "").lower())
    out: list[str] = []

    def add(x):
        if x and x != s and x not in out:
            out.append(x)

    base = [s]
    if re.search(r"[^aeiouáéíóúýæö]ur$", s):
        base.append(s[:-2] + "r")
    if s.endswith("ast"):
        base.append(s[:-3] + "ask")
        base.append(s[:-3] + "azk")
    for b in list(base):
        if b.endswith("legur") or b.endswith("legr"):
            base.append(re.sub(r"leg(u)?r$", "ligr", b))
        if b.endswith("lega"):
            base.append(b[:-4] + "liga")
    for b in base:
        add(b)
        v = b
        v = re.sub(r"ft", "pt", v)
        v = re.sub(r"^(s?)vo", r"\1vá", v)
        v = v.replace("kv", "hv") if v.startswith("kv") else v
        add(v)
        if v.endswith("ð") and len(v) > 3:
            add(v[:-1] + "t")
        if "je" in v:
            add(v.replace("je", "é"))
    return [x for x in out if x != s]

# ---------------------------------------------------------------- Kroonen 2013 (headwords and reflex lists)
#
# Kroonen, Etymological Dictionary of Proto-Germanic (raw/books/text/kroonen-pgmc,
# OCR). Only facts are used: which Old High German, Old Saxon and Old Norse
# words an entry lists under which Proto-Germanic headword. The headword is
# then matched to a kaikki Proto-Germanic page (stem key, unique match) and
# that page's chain gives the PIE id. OCR damage (6 for ó, ii for ú, / for l)
# is repaired on both the reflex words and the headword before matching.

KROONEN = "raw/books/text/kroonen-pgmc"
_KR_HEAD = re.compile(r"^\*([^\s]+)\s+((?:[a-z]+\.\s*)+)['‘]", re.M)
_KR_TAG = {"OHG": "goh", "OS": "osx", "ON": "non"}
_KR_REFLEX = re.compile(r"(?:^|[\s,(])(OHG|OS|ON)\s+((?:[^\s,;:=']+(?:,\s+)?)+?)\s+(?:[a-z]{1,4}\.|'|\()")
_KR_END = re.compile(r"=+>|:+>|⇒|\((?:IE|EUR|GM|NWIE|EUR/IE|IE\?|GM\?|DRV|NIE|WGM)[^)]*\)")


def kroonen_ocr(s: str) -> str:
    """Undo the frequent OCR substitutions of the scan text: 6 → o, 0 → o,
    ii → u, / → l, 1 → l; parentheses and brackets dropped."""
    s = (s or "").replace("6", "o").replace("0", "o").replace("ii", "u").replace("/", "l").replace("1", "l")
    return re.sub(r"[()\[\]{}<>!?.·]", "", s)


def kroonen_entries(root: Path = ROOT) -> list[dict]:
    """[{head, page, reflexes: {lang: [words]}}] for every headword line."""
    files = sorted((Path(root) / KROONEN).glob("p*.txt"))
    out = []
    for f in files:
        t = f.read_text("utf-8")
        ms = list(_KR_HEAD.finditer(t))
        for i, m in enumerate(ms):
            seg = t[m.start(): ms[i + 1].start() if i + 1 < len(ms) else len(t)]
            e = _KR_END.search(seg)
            seg = seg[: e.start()] if e else seg[:600]
            seg = seg.replace("-\n", "").replace("\n", " ")
            refl: dict[str, list] = collections.defaultdict(list)
            for rm in _KR_REFLEX.finditer(seg):
                for w in re.split(r",\s+", rm.group(2)):
                    w = kroonen_ocr(w.strip()).strip("-")
                    if len(w) >= 2 and w not in refl[_KR_TAG[rm.group(1)]]:
                        refl[_KR_TAG[rm.group(1)]].append(w)
            out.append({"head": kroonen_ocr(m.group(1)).strip("-"), "page": f.stem, "reflexes": dict(refl)})
    return out


def pgmc_stem_key(s: str) -> str:
    """*waldaną / waldan- → 'waldan'; *nabją / nabja- → 'nabj'; *huzdą → 'huzd'."""
    s = fm._nfd_strip((s or "").lower().lstrip("*").rstrip("-"))
    s = re.sub(r"[^a-zþðƀ]", "", s).replace("ƀ", "b")
    s = re.sub(r"z$", "", s)
    return re.sub(r"[aeiou]$", "", s)


def kroonen_bridge(root: Path, protos: fm.ProtoDB, res: fm.Resolver, langs=("goh", "osx", "non")) -> dict:
    """{lang: {loose key: (word, headword, page, Hit)}} for reflex words whose
    Kroonen headword matches exactly one resolvable kaikki PGmc page.
    A loose key listed under entries with different etyma is dropped."""
    pages: dict[str, set] = collections.defaultdict(set)
    for (code, k), es in protos.entries.items():
        if code == "gem-pro":
            for e in es:
                pages[pgmc_stem_key(e.word)].add(e.word)
    out = {L: {} for L in langs}
    bad = {L: set() for L in langs}
    for ent in kroonen_entries(root):
        cands = pages.get(pgmc_stem_key(ent["head"])) or set()
        if len(cands) != 1:
            continue
        w = next(iter(cands))
        h = res.resolve("gem-pro", "*" + w)
        if not h or not h.specific:
            continue
        for L in langs:
            for word in ent["reflexes"].get(L, []):
                k = loose_key(L)(word)
                if len(k) < 3:
                    continue
                if k in out[L] and out[L][k][3].ids != h.ids:
                    bad[L].add(k)
                out[L].setdefault(k, (word, w, ent["page"], h))
    for L in langs:
        for k in bad[L]:
            out[L].pop(k, None)
    return out


# ---------------------------------------------------------------- building the mappings


def _later_is(lm_non: fm.LangMapping, ice: list[fm.Entry], res: fm.Resolver) -> dict:
    """later-is rows for unmapped Old Norse headwords, and the Icelandic
    headword → Old Norse source words index used by the IcePaHC bridge."""
    K = fm.key_non
    cand: dict[str, list] = collections.defaultdict(list)
    bridge: dict[str, list] = collections.defaultdict(list)
    for e in ice:
        if e.form_of:
            continue
        srcs = [t for c, t, _ in e.links if c == "non"]
        for t in srcs:
            if K(e.word) and K(t) and K(t) not in bridge[K(e.word)]:
                bridge[K(e.word)].append(K(t))
        if e.rejected or len(srcs) != 1:
            continue
        k = K(srcs[0])
        if not k or k in lm_non.recs or k in lm_non.rejected:
            continue
        h = res.entry_hit(e, "is")          # proto links only (the non link does not resolve)
        if h and h.specific:
            cand[k].append((e.word, srcs[0], h))
    for k, lst in cand.items():
        if len({x[2].ids for x in lst}) > 1:
            continue
        w, src, h = lst[0]
        lm_non.recs[k] = fm.MapRec(k, src, h.ids, (f"non:{src}", f"is:{w}") + h.path, "later-is",
                                   "medium" if h.how == "chain" else "low", ("later-entry",))
    return dict(bridge)


def _ice_own(ice: list[fm.Entry], res: fm.Resolver) -> dict:
    """Icelandic headword key → Hit from its own proto-language links (used
    only when the Old Norse bridge gives nothing)."""
    out: dict[str, list] = collections.defaultdict(list)
    for e in ice:
        if e.form_of or e.rejected:
            continue
        h = res.entry_hit(e, "is")
        if h and h.specific:
            out[fm.key_non(e.word)].append((e.word, h))
    return {k: v for k, v in out.items() if len({x[1].ids for x in v}) == 1}


def _drop_affix_recs(lm: fm.LangMapping, entries: list[fm.Entry]):
    """No mapping for an affix headword (gi-, -ung) or through one: a base
    chain that ends in a prefix entry (githuld → gi-) is dropped."""
    K = fm.KEYS[lm.lang]
    affix = {k for e in entries if e.pos in _AFFIX_POS or _is_affix(e.word) for k in fm.entry_keys(e, lm.lang)}
    for k in list(lm.recs):
        r = lm.recs[k]
        bad = k in affix
        for x in r.path[1:]:
            if x.startswith(f"{lm.lang}:") and (_is_affix(x.split(":", 1)[1]) or K(x.split(":", 1)[1]) in affix):
                bad = True
            elif x.startswith("base:") and K(x[5:]) in affix:
                bad = True
        if bad:
            del lm.recs[k]


def _block_fixed(lm: fm.LangMapping, entries: list[fm.Entry], fixes: dict):
    """A headword whose own etymology chain names a proto term that a
    'proto' row unmaps (vetr ← *wintruz) gets no mapping from another source
    either (the descendants tree of *wihtiz lists a homograph vetr)."""
    dead = {k for k, (ids, _) in fixes.items() if not ids}
    for e in entries:
        if e.form_of or not e.links:
            continue
        keys = {(c, fs.PieIndex.proto_key(t)) for c, t, _ in e.links}
        if keys & dead and not any(c == "ine-pro" for c, _, _ in e.links):
            for k in fm.entry_keys(e, lm.lang):
                r = lm.recs.get(k)
                if r and not any(fs.PieIndex.proto_key(x.split(":", 1)[1]) in {t for _, t in keys & dead}
                                 for x in r.path if ":" in x):
                    del lm.recs[k]
                    lm.rejected[k] = "proto erratum"


def proto_fixes(root: Path = ROOT) -> dict:
    """{(code, proto key): (ids, note)} from the 'proto' rows of
    data/research/formulas/mapping-overrides/germanic-new.json."""
    p = Path(root) / OVERRIDE_FILE
    if not p.exists():
        return {}
    out = {}
    for r in json.loads(p.read_text("utf-8")).get("proto", []):
        out[(r["code"], fs.PieIndex.proto_key(r["term"]))] = (tuple(r["lex_id"]), r.get("note", "override"))
    return out


@dataclass
class GermanicMappings:
    non: fm.LangMapping
    goh: fm.LangMapping
    osx: fm.LangMapping
    ice_bridge: dict          # Icelandic headword key → [Old Norse keys]
    ice_own: dict             # Icelandic headword key → [(word, Hit)]
    kroonen: dict             # lang → loose key → (reflex word, PGmc page word, Kroonen page, Hit)
    lexicon: list
    gmap: dict


def build_mappings(root: Path = ROOT, lexicon: list[dict] | None = None, cache: Path | None = None,
                   cut: dict | None = None, kroonen: bool = True) -> GermanicMappings:
    """cut: {code: lines} from kaikki_cut (read here when not given; cache as there)."""
    root = Path(root)
    lex = lexicon or [json.loads(l) for l in (root / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines() if l]
    idx = fs.PieIndex(lex)
    kinds = {e["id"]: e.get("kind") for e in lex}
    want = ("non", "goh", "osx", "is")
    cut = cut if cut is not None else kaikki_cut(root, cache=cache)
    protos = fm.ProtoDB(root, codes=set())
    add_proto(protos, "gem-pro", (root / KD / fm.PROTO_DUMPS["gem-pro"]).read_text("utf-8").splitlines(), want)
    for code in ("gmw-pro", "gmq-pro"):
        add_proto(protos, code, cut.get(code, []), want)
    fixes = proto_fixes(root)
    res = BaseResolver(idx, protos, kinds, True, fixes=fixes)

    class _Bound(BaseResolver):
        def __init__(self, idx, protos, kinds, pseudo=True):
            super().__init__(idx, protos, kinds, pseudo, fixes=fixes)

    # build_lang_mapping makes its own fm.Resolver: use BaseResolver (with the fixes) for these builds only
    lms = {}
    orig, fm.Resolver = fm.Resolver, _Bound
    try:
        for lang in ("non", "goh", "osx"):
            spec = fm.LANGS[lang]
            ents = fm.read_dump([root / KD / spec.dump], lang, keep_forms=True, codes=spec.desc_codes)
            lms[lang] = fm.build_lang_mapping(lang, lex, protos, root=root, entries=ents, idx=idx)
            _drop_affix_recs(lms[lang], ents)
            _block_fixed(lms[lang], ents, fixes)
    finally:
        fm.Resolver = orig
    non, goh, osx = lms["non"], lms["goh"], lms["osx"]
    bridge, own = {}, {}
    if cut.get("is"):
        ice = icelandic_entries(cut["is"])
        bridge = _later_is(non, ice, res)
        own = _ice_own(ice, res)
        # Icelandic descendants-tree entries (PGmc pages listing Icelandic words)
        for w, rom, pc, pt in protos.desc.get("is", []):
            h = res.resolve(pc, pt)
            if h and h.specific:
                own.setdefault(fm.key_non(w), [(w, fm.Hit(h.ids, (f"is:{w}",) + h.path, "desc", h.steps + 1,
                                                             h.disputed))])
    kr = kroonen_bridge(root, protos, res) if kroonen else {"goh": {}, "osx": {}, "non": {}}
    return GermanicMappings(non, goh, osx, bridge, own, kr, lex, fs.group_map(lex))


def _groups(ids, gmap) -> frozenset:
    return frozenset(gmap.get(x, x) for x in ids)


def skel_non(s: str) -> str:
    """Old Norse spelling skeleton: the accent-free key with j → i, w → v and
    an initial h before l, r, n dropped (Menota lemmas write segia, iorð,
    sialfr; Old Norwegian lutr, laupa for hlutr, hlaupa)."""
    k = fm.key_non(s, True).replace("j", "i").replace("w", "v")
    return k[1:] if len(k) > 2 and k[0] == "h" and k[1] in "lrn" else k


def loose_key(lang: str):
    return skel_non if lang == "non" else (lambda s: fm.KEYS[lang](s, True))


class LooseIndex:
    """Loose key (accent-free; skel_non for Old Norse) → headword keys of a
    LangMapping, used only when the headwords under the loose key agree on
    the root groups."""

    def __init__(self, lm: fm.LangMapping, gmap: dict):
        self.lm, self.gmap, self.key = lm, gmap, loose_key(lm.lang)
        self.by: dict[str, list] = collections.defaultdict(list)
        self.acc: dict[str, list] = collections.defaultdict(list)     # accent-free exact key only
        for k in lm.recs:
            self.by[self.key(k)].append(k)
            self.acc[fm._nfd_strip(k)].append(k)

    def _one(self, ks) -> fm.MapRec | None:
        if not ks or len({_groups(self.lm.recs[k].ids, self.gmap) for k in ks}) != 1:
            return None
        return self.lm.recs[sorted(ks)[0]]

    def get(self, key: str) -> fm.MapRec | None:
        return self._one(self.by.get(key))

    def get_accent(self, word: str) -> fm.MapRec | None:
        return self._one(self.acc.get(fm._nfd_strip(fm.KEYS[self.lm.lang](word))))


def _rec_for_key(lm: fm.LangMapping, loose: LooseIndex, word: str, mode: str = "loose") -> tuple[fm.MapRec | None, str]:
    """word → (MapRec, step): the exact key; then the accent-free key;
    then (mode 'loose') the loose key, only for a word that is not itself a
    dictionary headword (raun 'trial' is not hraun 'lava')."""
    K = fm.KEYS[lm.lang]
    k = K(word)
    if k and k in lm.recs:
        return lm.recs[k], "exact"
    if k and k in lm.rejected:
        return None, "rejected"
    if not k or mode == "exact":
        return None, ""
    # Old Norse spelling marks vowel length, so an accent-free match is a guess for a headword
    # (lið 'host' is not líð 'ale'); ReA's OHG/OS lemmas carry no length marks at all
    r = loose.get_accent(word) if (lm.lang != "non" or k not in lm.lemma_words) else None
    if r:
        return r, "accent"
    if mode == "loose" and k not in lm.lemma_words:
        r = loose.get(loose.key(word))
        if r:
            return r, "loose"
    return None, ""


def _ice_rec(maps: GermanicMappings, loose_non: LooseIndex, lemma: str) -> tuple[fm.MapRec | None, str]:
    """IcePaHC lemma → (MapRec, step)."""
    K = fm.key_non
    lk = K(lemma)
    srcs = maps.ice_bridge.get(lk) or []
    hits = [maps.non.recs[s] for s in srcs if s in maps.non.recs]
    own = maps.ice_own.get(lk)

    def own_rec():
        w, h = own[0]
        path = (f"is:{lemma}",) + tuple(x for x in h.path if not x.startswith("is:"))
        return fm.MapRec(lemma, w, h.ids, path, h.how, fm.confidence(h, False), ("is-own",)), "is-own"

    if hits:
        if len({_groups(h.ids, maps.gmap) for h in hits}) == 1:
            h = hits[0]
            return fm.MapRec(lemma, h.word, h.ids, (f"is:{lemma}",) + h.path, h.how, h.confidence,
                             h.sources + ("is-bridge",), h.gloss), "is-bridge"
        return None, "ambiguous"
    if srcs:                                  # the Icelandic entry names its Old Norse source: no guessing
        if any(x in maps.non.rejected for x in srcs):
            return None, "bridge-borrowed"    # ON herra < OS hērro: the Icelandic chain is the loan's
        return own_rec() if own else (None, "bridge-unmapped")
    r, step = _rec_for_key(maps.non, loose_non, lemma)
    if r:
        return fm.MapRec(lemma, r.word, r.ids, (f"is:{lemma}",) + r.path, r.how, r.confidence,
                         r.sources + ("is-same-spelling",), r.gloss), "same-" + step
    if step == "rejected":
        return None, step
    got = []
    for v in modern_to_old_variants(lemma):
        r, st = _rec_for_key(maps.non, loose_non, v)
        if r and st == "exact":
            got.append((v, r))
        if got:
            break
    if got:
        v, r = got[0]
        return fm.MapRec(lemma, r.word, r.ids, (f"is:{lemma}", f"non-spelling:{v}") + r.path, r.how,
                         "medium" if r.confidence == "high" else "low", r.sources + ("is-variant",), r.gloss), "variant"
    if own:
        return own_rec()
    cands = [lemma] + modern_to_old_variants(lemma)
    if any(fm.key_non(v) in maps.non.lemma_words for v in cands):
        return None, ""                       # a headword (andligr) is not split into prefix + base
    for v in cands:
        r, st = _strip_prefix(maps.non, loose_non, v)
        if r:
            return fm.MapRec(lemma, r.word, r.ids, (f"is:{lemma}", st) + r.path, "prefix",
                             "medium" if r.confidence == "high" else "low", r.sources + ("prefix",), r.gloss), st
    return None, ""


# verbal and nominal prefixes whose removal leaves the root (Braune–Reiffenstein,
# Ahd. Gramm. §§ 70–76; Gallée, As. Gramm.; Noreen, Aisl. Gramm. § 147 for ú-)
PREFIXES = {
    "goh": ("ingagan", "ingegin", "samant", "widar", "duruh", "after", "furi", "fora", "ubar", "umbi", "missi",
            "hina", "dana", "dara", "zuo", "nidar", "aba", "ana", "zer", "fir", "far", "fur", "for", "int", "ant",
            "mit", "uz", "ur", "ir", "ar", "er", "gi", "ga", "ge", "ka", "bi", "be", "zi", "za", "ze", "un", "ab"),
    "osx": ("forth", "aftar", "thurh", "wiðar", "widar", "ofar", "obar", "umbi", "far", "for", "fir", "and", "ant",
            "mid", "ut", "ūt", "ur", "gi", "ge", "bi", "be", "an", "te", "ti", "to", "un", "af", "a"),
    "non": ("fyrir", "yfir", "undir", "gagn", "upp", "sam", "mis", "van", "for", "tor", "út", "ú", "ó"),
}


def _strip_prefix(lm: fm.LangMapping, loose: "LooseIndex", word: str,
                  ov: dict | None = None) -> tuple[fm.MapRec | None, str]:
    """A prefixed word (gi-hōren, fir-lāzan, ú-vinr) or a hyphenated one
    (dana-magan) → the mapping of its last part, when that part has one (a
    lemma override row for the part counts: aba-wesan → wesan's row).
    Not for a dictionary headword: kaikki gives a prefixed word's {{prefix}}
    base itself, so a headword without one is not split (andligr is not
    and- + ligr)."""
    w = word.lower()
    ov = ov or {}
    if fm.KEYS[lm.lang](word) in lm.lemma_words:
        return None, ""

    def part(x):
        if x in ov:
            ids, row = ov[x]
            if not ids:
                return None
            return fm.MapRec(x, x, frozenset(ids), (f"{lm.lang}:{x}", "erratum:" + row.get("note", "")), "erratum",
                             "high", ("mapping-overrides",))
        return _rec_for_key(lm, loose, x, mode="accent")[0]

    if "-" in w:
        tail = w.rsplit("-", 1)[1]
        if len(tail) >= 3:
            r = part(tail)
            if r:
                return r, "hyphen:" + tail
    for pre in PREFIXES.get(lm.lang, ()):
        if w.startswith(pre) and len(w) - len(pre) >= 3:
            r = part(w[len(pre):])
            if r:
                return r, f"prefix:{pre}-"
    return None, ""


def _kroonen_rec(maps: GermanicMappings, lang: str, word: str) -> tuple[fm.MapRec | None, str]:
    kr = maps.kroonen.get(lang) or {}
    for w, pre in [(word, "")] + [(word[len(p):], p) for p in PREFIXES.get(lang, ()) if word.lower().startswith(p)]:
        x = kr.get(loose_key(lang)(w))
        if x and len(loose_key(lang)(w)) >= 3:
            rw, head, page, h = x
            path = (f"{lang}:{word}",) + ((f"prefix:{pre}-",) if pre else ()) + \
                (f"kroonen:{page}:*{head}-:{lang} {rw}",) + h.path
            return fm.MapRec(word, rw, h.ids, path, "kroonen", "low", ("kroonen",)), "kroonen"
    return None, ""


def map_lemma(maps: GermanicMappings, corpus: str, lemma: str, loose: dict,
              ov: dict | None = None) -> tuple[fm.MapRec | None, str]:
    """A corpus lemma string ('a|b' = alternatives) → (MapRec, step). The
    alternatives must agree on the root groups; otherwise unmapped. `ov`:
    the corpus's lemma override rows (lemma → (ids, row)), applied to each
    alternative as well as (by the caller) to the whole string."""
    lang = CORPORA[corpus]["lang"]
    ov = ov or {}
    if lemma.endswith(" (name)"):
        return None, "name-unmapped"
    if lemma.startswith("?"):
        return None, "unknown"
    parts = [p for p in lemma.split("|") if p]
    hits, steps = [], []
    for p in parts:
        if p in ov:
            ids, row = ov[p]
            if ids:
                hits.append(fm.MapRec(p, p, frozenset(ids), (f"{lang}:{p}", "erratum:" + row.get("note", "")),
                                      "erratum", "high", ("mapping-overrides",)))
                steps.append("erratum")
            continue
        if lang == "is":
            r, st = _ice_rec(maps, loose["non"], p.lower() if p[:1].isupper() else p)
        else:
            lm = getattr(maps, lang)
            r, st = _rec_for_key(lm, loose[lang], p)
            if r is None and st != "rejected":
                r, st = _strip_prefix(lm, loose[lang], p, ov)
                if r:
                    r = fm.MapRec(p, r.word, r.ids, (f"{lang}:{p}", st) + r.path, "prefix",
                                  "medium" if r.confidence == "high" else "low", r.sources + ("prefix",), r.gloss)
            if r is None and st != "rejected":
                r, st = _kroonen_rec(maps, lang, p)
        if r:
            hits.append(r)
            steps.append(st)
    if not hits:
        return None, ""
    if len({_groups(h.ids, maps.gmap) for h in hits}) > 1:
        return None, "ambiguous"
    ids = frozenset().union(*(h.ids for h in hits))
    if len(_groups(ids, maps.gmap)) > fs.MAX_GROUPS:
        return None, "too-many-groups"
    h = hits[0]
    if len(parts) > 1:
        h = fm.MapRec(lemma, "|".join(x.word for x in hits), ids, h.path, h.how, "low",
                      h.sources + ("lemma-alternatives",), h.gloss)
    elif h.key != lemma:
        h = fm.MapRec(lemma, h.word, h.ids, h.path, h.how, h.confidence, h.sources, h.gloss)
    if any(s == "loose" or s.endswith("-loose") for s in steps):
        h = fm.MapRec(h.key, h.word, h.ids, h.path, h.how, "low" if h.confidence != "high" else "medium",
                      h.sources + ("loose-key",), h.gloss)
    return h, steps[0]


NAME_TAGS = re.compile(r"^(NP|NPRS?(-[NADG])?|NE)$")


def name_lemmas(tokens) -> set:
    """Lemma strings tagged as proper names (Menota NP, IcePaHC NPR*, ReA NE)
    in at least half of their tokens."""
    n, tot = collections.Counter(), collections.Counter()
    for t in tokens:
        tot[t.lemma] += 1
        if NAME_TAGS.match(t.units.get("tag") or ""):
            n[t.lemma] += 1
    return {l for l in n if 2 * n[l] >= tot[l]}


def _name_rec(maps: GermanicMappings, lang: str, lemma: str) -> tuple[fm.MapRec | None, str]:
    """A proper name maps only through a kaikki name entry of its own
    (Haraldr, Þórr), never through a common noun of similar form (ReA Aram
    'Aram' is not aram 'poor')."""
    lm = maps.non if lang == "is" else getattr(maps, lang)
    keys = [fm.KEYS[lm.lang](lemma)]
    if lang == "is":
        keys = maps.ice_bridge.get(fm.key_non(lemma)) or keys
    for k in keys:
        r = lm.recs.get(k)
        if r and "name" in lm.pos.get(k, ()) and "form-of" not in r.sources and r.how not in ("prefix", "base"):
            return fm.MapRec(lemma, r.word, r.ids, r.path, r.how, r.confidence, r.sources + ("name",), r.gloss), "name"
    return None, "name-unmapped"


def corpus_recs(maps: GermanicMappings, corpus: str, lemmas, overrides: dict | None = None,
                root: Path = ROOT, names: set | None = None) -> tuple[dict, dict]:
    """lemma → MapRec for the corpus's lemmas (blocked ids stripped, the
    mapping overrides applied), and lemma → step. `names`: lemma strings
    that are proper names (name_lemmas), mapped only through name entries."""
    names = names or set()
    loose = {"non": LooseIndex(maps.non, maps.gmap), "goh": LooseIndex(maps.goh, maps.gmap),
             "osx": LooseIndex(maps.osx, maps.gmap)}
    ov = (overrides or fm.load_overrides(root))["lemma"].get(corpus, {})
    recs, steps = {}, {}
    for lem in sorted(set(lemmas)):
        if lem in names and lem not in ov:
            r, st = _name_rec(maps, CORPORA[corpus]["lang"], lem)
        else:
            r, st = map_lemma(maps, corpus, lem, loose, ov)
        steps[lem] = st
        if r:
            keep = fm._strip_blocked(r.ids)
            if not keep:
                continue
            if len(keep) != len(r.ids):
                r = fm.MapRec(r.key, r.word, frozenset(keep), r.path, r.how, r.confidence, r.sources, r.gloss)
            recs[lem] = r
    decided = fm.apply_rec_overrides(corpus, recs, root=root, overrides=overrides)
    # Keep the ancestry that made a proto decision govern this word. Without
    # it, reading a regenerated table loses the decision's formation cap.
    for lem, r in decided.items():
        if lem in recs and r.how == "erratum":
            path = tuple(dict.fromkeys((*recs[lem].path, *r.path[1:])))
            decided[lem] = replace(r, path=path)
    return decided, steps


def table_rows(corpus: str, recs: dict) -> list[dict]:
    meta = CORPORA[corpus]
    rows = []
    for lem in sorted(recs):
        r = recs[lem]
        rows.append({"corpus": corpus, "lang": meta["lang"], "lemma": lem, "word": r.word, "lex_id": sorted(r.ids),
                     "path": list(r.path), "how": r.how, "confidence": r.confidence, "sources": list(r.sources),
                     "licence": meta["licence"], "research_only": meta["research_only"]})
    return rows


def write_table(corpus: str, recs: dict, root: Path = ROOT) -> Path:
    p = Path(root) / MAPPING_DIR / f"{corpus}.jsonl"
    p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in table_rows(corpus, recs)), "utf-8")
    return p


def read_table(corpus: str, root: Path = ROOT) -> dict:
    """lemma string → lexicon ids, with the mapping overrides applied (for the Stage C builder)."""
    out = {}
    for line in (Path(root) / MAPPING_DIR / f"{corpus}.jsonl").read_text("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["lemma"]] = tuple(r["lex_id"])
    return fm.apply_table_overrides(corpus, out, root=root)


def load_corpus(corpus: str, root: Path = ROOT, **kw) -> list[Token]:
    if corpus == "menota":
        return load_menota(root, **kw)
    if corpus == "icepahc":
        return load_icepahc(root, **kw)
    return load_rea(corpus, root, **kw)
