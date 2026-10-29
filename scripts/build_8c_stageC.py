#!/usr/bin/env python3
"""Phase 8c Stage C (the Celtic and new-traditions run): corpora, retrieval, bundles, embedded
decoys, reader slabs and the blinding key, as pre-registered in docs/research/8c-preregistration.md
("Stage C"), built with the Stage B machinery (scripts/build_8c_stageB.py, imported).

  uv run python -I scripts/build_8c_stageC.py [--cache-dir DIR] [--refreeze] [--procs N]

One command rebuilds everything from the corpora and the current mapping tables. --cache-dir keeps a
pickle per loader group (reused when present; delete it after a mapping change). params.json is
frozen on the first run and read by later runs; --refreeze recomputes it (allowed only while no
Stage C slab has been read).

1. Pivots, in the pre-registered reading order: the Celtic text layer
   raw/daughters/celtic-stageC/units.jsonl (units with dup_of are skipped, as text and as context):
   Old Irish glosses (Wb, Sg), Old Irish, Middle Irish, Middle/Old Welsh, Early Modern Irish; then
   Menota and IcePaHC (Old Norse), ReA (OHG, Old Saxon), Vuk, byliny, Lithuanian dainos, DMHP
   (Classical Armenian), Tocharian A, Old Albanian. Unit: the layer's unit (verse line, prose
   sentence, gloss), the corpus sentence or stanza (Menota stanza where the document has one),
   ReA verse (else the document, windowed), the edition line (Vuk, byliny, dainos, Tocharian A),
   DMHP sentence (split at ։ and the printed section numbers), Albanian paragraph. A unit with more
   than MAX_WORDS content words is cut into windows (Stage B rule).
2. Mapping, through the public API only: Celtic `celtic_mapping.build_mappings` + the lemmatizers
   with use_skeleton=False + `lemmatize_words` + `content_of` + `read_table` (celt, cy, sga-glosses;
   tagged gloss tokens by their own lemma); Germanic `germanic_new_mapping.read_table` on the corpus
   lemmas; Balto-Slavic `bsl_mapping.lemmatizer` / `corpus_words` / `read_table`; Armenian DMHP
   lemmas via `arm_toch_alb_mapping.DmhpLemma`, Tocharian A and Albanian via `build_xto` /
   `build_sqo` + `xto_tokens` / `sqo_tokens`, their tables through `fm.apply_table_overrides`.
   Names are not mapped (kept as content words, lemma marked '(name)'): bsl_mapping.is_name,
   capitalised non-initial Celtic words and tagged PROPN glosses, DMHP N+Top/N+Ant (not content).
3. Partners: every corpus held (Stage B's loaders, minus its 99 UD Old Irish units, which the Celtic
   layer's glosses replace) + the Stage C corpora + DCS Mahābhārata and Rāmāyaṇa + GLAUx texts after
   300 BC with a stated licence (Septuagint excluded: translation literature). Retrieval, idf over
   all indexed units, word matching, top-k, floor (FLOOR_Q quantile of Stage C pivots' best-partner
   scores, frozen in params.json with a word-shuffle null), bundles, merge, decoys and slab packing
   are Stage B's (imported), run from the Stage C pivots only.
4. Each passage carries 'licence' (text) and 'licence_tag' (consent-train, research, nc, nd, pd,
   cc-by, cc-by-sa, gpl, unchecked); research_only = research / nc / nd / unchecked. Each slab
   lists its tags. Slabs with text: data/research/8c/stageC/slabs/ (gitignored); loci only:
   slabs-loci/. Key: data/audits/keys/8c-stageC-key.json (gitignored).

Nothing under raw/ is executed or imported; raw files are read as text or JSON.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import math
import multiprocessing as mp
import pickle
import random
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
# a private instance of the Stage B module: install() below extends its corpus registry and order, which
# must not leak into another importer of build_8c_stageB (its tests)
_SB_NAME = "build_8c_stageB__stageC"
SB = sys.modules.get(_SB_NAME)
if SB is None:
    _spec = importlib.util.spec_from_file_location(_SB_NAME, ROOT / "scripts" / "build_8c_stageB.py")
    SB = importlib.util.module_from_spec(_spec)
    sys.modules[_SB_NAME] = SB
    _spec.loader.exec_module(SB)
B = SB.B

OUT = ROOT / "data" / "research" / "8c" / "stageC"
KEY = ROOT / "data" / "audits" / "keys" / "8c-stageC-key.json"
CELTIC_LAYER = "raw/daughters/celtic-stageC/units.jsonl"
SEED = 0
FLOOR_Q = SB.FLOOR_Q
DECOY_SHARE = SB.DECOY_SHARE
LOW_MAPPED = 0.30              # pre-registered: units < 30% mapped stay pivots (partners via mapped words)
SEED_TAG = "8c-stageC"
HEADER = "Comparison bundles (Stage C): Celtic and newly added traditions with partners from all branches"
FORMAT_NOTE = (SB.FORMAT_NOTE + " Every passage carries 'licence' and 'licence_tag': consent-train (CELT, used with "
               "consent for research and training; never redistributed), research (research only), nc "
               "(non-commercial), nd (no derivatives), pd (public domain), cc-by, cc-by-sa, gpl, unchecked. "
               "Lemmas marked '(name)' are proper names and are not mapped.")

# ---------------------------------------------------------------- corpora (Stage B's + Stage C's)

BRANCHES = ("Indo-Iranian", "Greek", "Germanic", "Anatolian", "Italic", "Baltic", "Celtic", "Slavic", "Armenian",
            "Tocharian", "Albanian")
CELTIC = ("sga-gl", "sga", "mga", "cy", "ga-early")
NEW = ("menota", "icepahc", "rea-goh", "rea-osx", "vuk", "byliny", "dainos", "ccmh", "xcl", "xto", "sqo")
PIVOTS_ALL = CELTIC + NEW
STAGEB = ("rv", "av", "ae", "hom", "grc", "non", "ang", "hit", "lat", "xum", "lv", "orv")
EXTRA = ("sa-ep", "grc-late")
ORDER_ALL = PIVOTS_ALL + STAGEB + EXTRA
NEW_CORPORA = {   # corpus → (branch, label, licence, research_only); per-unit licences override
    "sga-gl": ("Celtic", "Old Irish glosses (Würzburg, Doyle; St Gall, UD DipSGG)", None, None),
    "sga": ("Celtic", "Old Irish (CELT; Irish editions and journals, OCR)", None, None),
    "mga": ("Celtic", "Middle Irish (CELT; Irish editions and journals, OCR)", None, None),
    "cy": ("Celtic", "Middle Welsh (Skene; Evans and Rhŷs & Evans editions; journals, OCR)", None, None),
    "ga-early": ("Celtic", "Early Modern Irish (CELT; Irish editions and journals, OCR)", None, None),
    "menota": ("Germanic", "Old Norse, West Norse documents (Menota)", "CC BY-SA 4.0 (Menota)", False),
    "icepahc": ("Germanic", "Old Icelandic, IcePaHC texts to 1400", "CC BY 4.0 (IcePaHC)", False),
    "rea-goh": ("Germanic", "Old High German (Referenzkorpus Altdeutsch)", "CC BY-NC-SA 3.0 (ReA): non-commercial",
                True),
    "rea-osx": ("Germanic", "Old Saxon (Referenzkorpus Altdeutsch)", "CC BY-NC-SA 3.0 (ReA): non-commercial", True),
    "vuk": ("Slavic", "Serbian epic and lyric songs (Vuk Karadžić, sr.wikisource)",
            "CC BY-SA 4.0 (sr.wikisource transcription; text public domain)", False),
    "byliny": ("Slavic", "Russian byliny (Kirsha Danilov, Rybnikov, Hilferding, Kireevsky)", None, None),
    "dainos": ("Baltic", "Lithuanian dainos (Rhesa, Nesselmann, Schleicher, Leskien-Brugmann, Bartsch, Juškevič; OCR)",
               "Public domain", False),
    "ccmh": ("Slavic", "Old Church Slavonic (CCMH)", "CC BY 4.0 (Corpus Cyrillo-Methodianum Helsingiense)", False),
    "xcl": ("Armenian", "Classical Armenian, 5th-century authors (DMHP)", "CC BY 4.0 (DMHP)", False),
    "xto": ("Tocharian", "Tocharian A (TITUS 2.0, Sieg & Siegling)", "CC BY-NC-SA 4.0 (TITUS 2.0): non-commercial",
            True),
    "sqo": ("Albanian", "Old Albanian, Buzuku 1555 and Bogdani 1685 (TITUS 2.0)",
            "CC BY-NC-SA 4.0 (TITUS 2.0): non-commercial", True),
    "sa-ep": ("Indo-Iranian", "Epic Sanskrit, Mahābhārata and Rāmāyaṇa (DCS)", "CC BY 4.0 (DCS)", False),
    "grc-late": ("Greek", "Greek after 300 BC (GLAUx; texts with a stated licence)", None, None),
}
CELTIC_LICENCE = {
    "consent-train": ("CELT (UCC), used with consent for research and training; never redistributed", False),
    "research": ("research only (CELT files G400001-G400058 with the OUP notice; Ériu, ZCP, Revue celtique: US-PD)",
                 True),
    "nc": ("CC BY-NC-SA (St Gall glosses, UD DipSGG; CELT CC BY-NC-SA files; NLS scans of Meyer): non-commercial", True),
    "pd": ("public domain edition", False),
    "cc-by": ("CC BY 4.0 (Würzburg glosses, Doyle)", False),
}
RESEARCH_TAGS = frozenset({"research", "nc", "nd", "unchecked"})
WELSH_DIPLOMATIC = frozenset({"welsh-redbook-mabinogion-rhys-evans-1887", "welsh-white-book-mabinogion-evans-1907",
                              "welsh-redbook-bruts-rhys-evans-1890", "welsh-redbook-poetry-evans-1911",
                              "welsh-book-of-taliesin-evans-1910", "welsh-black-book-carmarthen-evans-1906",
                              "welsh-book-of-aneirin-evans-1908"})
DCS_EPIC = ("Mahābhārata", "Rāmāyaṇa")
GLAUX_LATE_EXCLUDE_TLG = ("0012-", "0527-")       # Homer (AGDT has it); Septuagint (translation literature)
GLAUX_NO_LICENCE = ("NA", "OpenEdition Books License", "")
GLAUX_LATE_RULE = ("GLAUx texts with ENDDATE > -300 and a stated open licence (SOURCE_LICENSE not 'NA' / "
                   "'OpenEdition Books License'), every genre; Homer and the Septuagint (TLG 0527, translation "
                   "literature) excluded; NC/ND texts carried with research_only")
DCS_EPIC_RULE = ("DCS Mahābhārata and Rāmāyaṇa (CC BY 4.0), DCS sentence; lemma mapping: the round-3 'av' table "
                 "(same DCS lemma convention), else the live kaikki Sanskrit mapping, with the 'av' lemma errata")


SB_ORDER_B = SB.ORDER          # Stage B's own corpus order (its loader returns these)


def install() -> None:
    """Stage C corpora and branches into the imported Stage B module (Index, render and slab packing
    read its CORPORA / BRANCHES / ORDER)."""
    for c, v in NEW_CORPORA.items():
        SB.CORPORA[c] = v
    SB.BRANCHES = BRANCHES
    SB.ORDER = ORDER_ALL


install()


def licence_tag(lic: str) -> str:
    s = lic or ""
    if s in CELTIC_LICENCE or s in ("nd", "gpl", "unchecked", "cc-by-sa"):
        return s
    if "BY-NC" in s or "non-commercial" in s:       # not "the NC text layers are not used" (VedaWeb)
        return "nc"
    if "BY-ND" in s or "-ND " in s or s.endswith("-ND"):
        return "nd"
    if "BY-SA" in s or "BY SA" in s:
        return "cc-by-sa"
    if "CC BY" in s or "CC-BY" in s:
        return "cc-by"
    if "ublic domain" in s:
        return "pd"
    if "GNU" in s:
        return "gpl"
    return "unchecked"


def lic_pair(lic: str) -> tuple[str, bool]:
    return lic, licence_tag(lic) in RESEARCH_TAGS


def _tok(corpus, lemma, surface, locus, unit, book, content, lic, extra=None):
    from pie import formula_search as fs
    u = {"cunit": unit, "book": book, "lic": lic}
    if extra:
        u.update(extra)
    return fs.Token(corpus, lemma, surface, locus, u, content, "other")


def _units(corpus, toks, mapping, text_of=None, window=True) -> list:
    """Tokens (with units cunit / book / lic) → Stage B Units."""
    lic = lambda t: lic_pair(t.units["lic"])
    return SB.units_from_tokens(corpus, toks, "cunit", lambda t: t.units["book"], [t.surface for t in toks], mapping,
                                lic, text_of=text_of, window=window)


def _name_lemma(lem: str) -> str:
    return f"{lem} (name)"


# ---------------------------------------------------------------- Celtic

def celtic_rows(root: Path = ROOT, max_date: int | None = None, notes: dict | None = None) -> list[dict]:
    """The Celtic layer's units with dup_of null, in file order; with max_date, Early Modern Irish units
    whose witness year (annal year, else date_from) is later are left out."""
    out = []
    with open(Path(root) / CELTIC_LAYER, encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            if d.get("dup_of"):
                if notes is not None:
                    notes["celtic_dup_units_skipped"] = notes.get("celtic_dup_units_skipped", 0) + 1
                continue
            if max_date is not None and d["lang"] == "ga-early" and (d.get("year") or d["date_from"]) > max_date:
                if notes is not None:
                    notes["celtic_late_units_skipped"] = notes.get("celtic_late_units_skipped", 0) + 1
                continue
            out.append(d)
    from pie.material_units import repair_celtic_rows
    return repair_celtic_rows(out)


def celtic_corpus(d: dict) -> str:
    if d["kind"] == "gloss":
        return "sga-gl"
    return {"sga": "sga", "mga": "mga", "ga-early": "ga-early", "wlm": "cy", "owl": "cy"}[d["lang"]]


def celtic_book(d: dict) -> str:
    src = d["source"]
    if d["kind"] == "gloss":
        m = re.search(r"(\d+[a-d])", d.get("ref") or d["id"].split(":")[1])
        return f"{d['id'].split(':')[0]}:{m.group(1) if m else d['id'].split(':')[1]}"
    if src.startswith("celt-ucc/"):
        return d["id"].split(":")[0]
    return f"{src}|{d.get('title') or ''}"


def gloss_unit_key(d: dict) -> str:
    """The cm.GlossTok unit of a gloss unit id: wb:1a:1 → 'Wb 1a1', sg:2b3:21 → 'sg 21'."""
    p = d["id"].split(":")
    return f"Wb {p[1]}{p[2]}" if p[0] == "wb" else f"sg {p[-1]}"


def celtic_meta(d: dict) -> dict:
    return {"lang": d["lang"], "date_from": d["date_from"], "date_to": d["date_to"],
            "date_ms_only": bool(d.get("date_ms_only")), "genre": d["genre"], "licence": d["licence"],
            "source": d["source"].split("/")[0], "kind": d["kind"]}


def load_celtic(root: Path, lex: list, max_date=None, log=print) -> tuple[dict, dict, dict]:
    """Celtic Units per corpus, unit metadata by unit id, notes."""
    from pie import celtic_mapping as cm
    notes: dict = {}
    maps = cm.build_mappings(root, lexicon=lex)
    log("celtic mappings built")
    ilz = cm.irish_lemmatizer(maps, use_skeleton=False)
    wlz = {dip: cm.welsh_lemmatizer(maps, dip, use_skeleton=False) for dip in (False, True)}
    tables = {t: cm.read_table(t, root) for t in ("celt", "sga-glosses", "cy")}
    table_of = {"sga-gl": "sga-glosses", "sga": "celt", "mga": "celt", "ga-early": "celt", "cy": "cy"}
    gl: dict = collections.defaultdict(list)
    for t in cm.gloss_tokens(root):
        gl[t.unit].append(t)
    rows = celtic_rows(root, max_date, notes)
    toks: dict = collections.defaultdict(list)
    meta, texts = {}, collections.defaultdict(dict)
    research_mismatch = 0
    seen_gloss = set()
    for d in rows:
        c = celtic_corpus(d)
        book, locus, uid = celtic_book(d), d["id"], d["id"]
        lic = d["licence"]
        src = d["source"].split("/")
        if src[0] == "celt-ucc" and len(src) > 1:
            lic = cm.celt_licence(src[1])
            research_mismatch += lic != d["licence"]
        meta[uid] = celtic_meta({**d, "licence": lic})
        texts[c][uid] = d["text"]
        if c == "sga-gl" and gloss_unit_key(d) in gl:
            key = gloss_unit_key(d)
            assert key not in seen_gloss, f"gloss unit key {key} joins two units"
            seen_gloss.add(key)
            gts = gl[key]
            # untagged tokens: the lemmatizer over the gloss's word sequence (context rules), never word by word
            ctx = cm.lemmatize_words(ilz, [t.form for t in gts])
            for t, clem in zip(gts, ctx):
                if t.lemma:
                    content = t.upos in cm.CONTENT_UPOS
                    lem = _name_lemma(t.lemma) if t.upos == "PROPN" else t.lemma
                else:
                    lem = clem
                    content = cm.content_of(maps.irish, lem, t.form, ilz)
                toks[c].append(_tok(c, lem, t.form, locus, uid, book, content, lic))
            continue
        welsh = c == "cy"
        lz = wlz[src[0] in WELSH_DIPLOMATIC] if welsh else ilz
        lm = maps.welsh if welsh else maps.irish
        ws = (cm.welsh_words if welsh else cm.irish_words)(d["text"])
        for i, (w, lem) in enumerate(zip(ws, cm.lemmatize_words(lz, ws))):
            content = cm.content_of(lm, lem, w, lz)
            if content and i > 0 and w[:1].isupper() and lem not in cm.CQ2_DEITY_LEMMAS:
                lem = _name_lemma(lem)      # cq2: Dia 'God' keeps its lemma (theonyms keep their roots)
            toks[c].append(_tok(c, lem, w, locus, uid, book, content, lic))
    notes["celt_research_tag_mismatch"] = research_mismatch
    notes["gloss_units_joined_to_tagged_tokens"] = len(seen_gloss)
    out = {}
    for c in CELTIC:
        tab = tables[table_of[c]]
        out[c] = _units(c, toks[c], tab, text_of=texts[c])
        for u in out[c]:
            u.tag = u.licence
            u.licence, u.research_only = CELTIC_LICENCE[u.tag]
    lv = collections.Counter(ilz.level.values())
    notes["irish_lemmatizer_levels_by_type"] = dict(lv)
    return out, meta, notes


# ---------------------------------------------------------------- Germanic (Menota, IcePaHC, ReA)

def menota_tokens(root: Path) -> list:
    """gm.load_menota's tokens (the one Menota loader: form table, reviewed repairs, numeral guard), with
    Stage C units: stanza for verse documents, else sentence; book = document."""
    from pie import germanic_new_mapping as gm
    lic = SB.CORPORA["menota"][2]
    def unit(t):
        d, s = t.units["doc"], t.units.get("stanza")
        return f"{d}.st{s[len(d) + 1:]}" if s else t.units["sentence"]
    return [_tok("menota", t.lemma, t.surface, t.locus, unit(t), t.units["doc"], t.content, lic)
            for t in gm.load_menota(Path(root))]


def icepahc_tokens(root: Path) -> list:
    """gm.load_icepahc's tokens with the word form kept (checked against it)."""
    from pie import germanic_new_mapping as gm
    lic = SB.CORPORA["icepahc"][2]
    return [_tok("icepahc", t.lemma, t.surface, t.locus, t.units["sentence"],
                 t.units["text"], t.content, lic)
            for t in gm.load_icepahc(root, include_surface=True)]


def rea_editions(root: Path) -> dict:
    """(subcorpus, document, first token) → the edition form of that token (relANNIS default_layer)."""
    from pie import germanic_new_mapping as gm
    base = Path(root) / gm.REA
    out = {}
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        docs = {}
        for line in (d / "corpus.annis").read_text("utf-8").splitlines():
            p = line.split("\t")
            if len(p) > 2 and p[2] == "DOCUMENT":
                docs[p[0]] = p[1]
        nodes = {}
        with open(d / "node.annis", encoding="utf-8") as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) > 9 and p[3] == "default_layer":
                    nodes[p[0]] = (p[2], int(p[8]))
        sub = d.name.replace("DDD-AD-", "")
        with open(d / "node_annotation.annis", encoding="utf-8") as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) > 3 and p[2] == "edition" and p[0] in nodes:
                    cref, start = nodes[p[0]]
                    out[(sub, docs.get(cref, cref), start)] = p[3]
    return out


def rea_tokens(corpus: str, rows: list, eds: dict) -> list:
    """gm.load_rea(corpus, rows) with the edition form of each lemma span (checked against it)."""
    from pie import germanic_new_mapping as gm
    want = gm.REA_LANG[corpus]
    lic = SB.CORPORA[corpus][2]
    toks = []
    for r in rows:
        if r["lang"] not in want:
            continue
        lem = gm.rea_lemma(r["lemma"])
        if not lem or lem in ("-", "_"):
            continue
        doc = f"{r['sub']}/{r['doc']}"
        unit = f"{doc}.{r['verse']}" if r["verse"] else doc
        locus = f"{r['sub']} {r['doc']}" + (f" v{r['verse']}" if r["verse"] else "")
        toks.append(_tok(corpus, lem, eds.get((r["sub"], r["doc"], r["start"]), ""), locus, unit, doc,
                         gm.rea_is_content(r["posLemma"]), lic))
    ref = gm.load_rea(corpus, rows=rows)
    assert [(t.lemma, t.content) for t in ref] == [(t.lemma, t.content) for t in toks], f"{corpus} differs"
    return toks


def load_germanic(root: Path, log=print) -> tuple[dict, dict]:
    from pie import germanic_new_mapping as gm
    out, notes = {}, {}
    rows = gm.rea_tokens(root)
    eds = rea_editions(root)
    for c, toks in (("menota", menota_tokens(root)), ("icepahc", icepahc_tokens(root)),
                    ("rea-goh", rea_tokens("rea-goh", rows, eds)), ("rea-osx", rea_tokens("rea-osx", rows, eds))):
        out[c] = _units(c, toks, gm.read_table(c, root))
        notes[f"{c}_tokens_without_surface"] = sum(1 for t in toks if not t.surface)
        log(f"{c}: {len(out[c])} units")
    return out, notes


# ---------------------------------------------------------------- Balto-Slavic (Vuk, byliny, dainos, CCMH)

def load_bsl(root: Path, lex: list, include_ccmh: bool = False, log=print) -> tuple[dict, dict]:
    from pie import bsl_mapping as bm
    from pie import formula_search_multi as fm
    maps = bm.build_mappings(root, lexicon=lex)
    # the dainos table was built with Derksen's EDBIL headwords added (scripts/build_bsl_mapping.py)
    bm.add_derksen_lt(maps.lt, bm.derksen_index(root), fm.FuzzyPie(maps.lexicon))
    ocs = bm.ocs_mapping(maps, root) if include_ccmh else None
    lms = {"vuk": maps.sh, "byliny": maps.ru, "dainos": maps.lt, "ccmh": ocs}
    out, notes = {}, {}
    for c in ("vuk", "byliny", "dainos") + (("ccmh",) if include_ccmh else ()):
        lz, lm = bm.lemmatizer(c, maps, ocs), lms[c]
        toks, texts = [], {}
        rows = list(bm.UNITS[c](root))
        lowercase = bm.lowercase_surfaces(c, rows)      # cq2: sentence-initial capitals are not names
        for locus, u, text in rows:
            lic = SB.CORPORA[c][2] or bm.SOURCES[c].get(u["source"], "unchecked")
            book = u.get("song") or u.get("page_file") or u.get("codex") or u["source"]
            ws = bm.corpus_words(c, text)
            texts[u["line"]] = " ".join(ws) if c == "ccmh" else text.strip()
            names = bm.name_flags(c, text, ws, lowercase)
            for i, w in enumerate(ws):
                lem = lz(w)
                content = lm.is_content(lem) and not (lem.startswith("?") and len(lem) < 3)
                if content and names[i]:
                    lem = _name_lemma(lem)
                toks.append(_tok(c, lem, w, locus, u["line"], book, content, lic))
        out[c] = _units(c, toks, bm.read_table(c, root), text_of=texts)
        log(f"{c}: {len(out[c])} units")
    return out, notes


# ---------------------------------------------------------------- Armenian (DMHP), Tocharian A, Old Albanian

_DMHP_W = re.compile(r'<w id="([^"]*)">\s*\n(.*?)\n</w>', re.S)


def dmhp_tokens(root: Path) -> list:
    """DMHP words with form and sentence: the tokens of am.dmhp_tokens (checked against it), a sentence
    ending at a word ending in ։ or : and at the printed section numbers (digit tokens)."""
    import glob
    from pie import arm_toch_alb_mapping as am
    conv = am.DmhpLemma(am.proiel_lemmas(root))
    lic = SB.CORPORA["xcl"][2]
    toks, ref = [], []
    for p in sorted(glob.glob(str(Path(root) / am.KD / am.DMHP_DIR / "*.vert"))):
        text = Path(p).name.split("_HYE")[0]
        s = 0
        for m in _DMHP_W.finditer(Path(p).read_text("utf-8")):
            cols = m[2].split("\t")
            if len(cols) < 5:
                continue
            form = cols[0].strip()
            if re.fullmatch(r"\d+", form):
                s += 1
                continue
            lem = cols[3].strip()
            if not lem or not re.search(r"[Ա-և]", cols[0]):
                continue
            at = am.ArmTok(text, m[1], lem, cols[4].strip())
            ref.append(lem)
            toks.append(_tok("xcl", conv(lem), form, f"{text} {m[1]}", f"{text}.s{s}", text, at.content, lic))
            if form.endswith(("։", ":")):
                s += 1
    assert ref == [t.lemma for t in am.dmhp_tokens(root)], "DMHP tokens differ from am.dmhp_tokens"
    return toks


def _table(corpus: str, root: Path) -> dict:
    """A Stage C table (lemma → ids) with the overrides, through the public API."""
    from pie import formula_search_multi as fm
    out = {}
    for line in (Path(root) / "data/research/formulas/mapping" / f"{corpus}.jsonl").read_text("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["lemma"]] = tuple(r["lex_id"])
    return fm.apply_table_overrides(corpus, out, root=root)


def load_east(root: Path, lex: list, extract=None, log=print) -> tuple[dict, dict]:
    from pie import arm_toch_alb_mapping as am
    out, notes = {}, {}
    out["xcl"] = _units("xcl", dmhp_tokens(root), _table("xcl", root))
    log(f"xcl: {len(out['xcl'])} units")
    tb = am.build_xto(lex, root, extract=extract)
    lic = SB.CORPORA["xto"][2]
    xt = [_tok("xto", t.lemma, t.surface, t.locus, t.units["line"], t.units["leaf"], t.content, lic)
          for t in am.xto_tokens(tb, root)]
    out["xto"] = _units("xto", xt, _table("xto", root))
    log(f"xto: {len(out['xto'])} units")
    ab = am.build_sqo(lex, root, extract=extract)
    units = am.alb_units(root)
    notes["sqo_bardhi_dictionary_entries_left_out"] = sum(1 for u in units if u.text == "bardhi")
    units = [u for u in units if u.text != "bardhi"]
    lic = SB.CORPORA["sqo"][2]
    texts = {u.locus: " ".join(u.words) for u in units}
    st = [_tok("sqo", t.lemma, t.surface, t.locus, t.units["paragraph"], t.units["text"], t.content, lic)
          for t in am.sqo_tokens(ab, root, units=units)]
    out["sqo"] = _units("sqo", st, _table("sqo", root), text_of=texts)
    log(f"sqo: {len(out['sqo'])} units")
    return out, notes


# ---------------------------------------------------------------- partner-only additions

def glaux_late_selection(root: Path = ROOT) -> list[dict]:
    import csv
    out = []
    with open(Path(root) / SB.B_fm().GLAUX_DIR / "metadata.txt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            try:
                end = int(r["ENDDATE"])
            except (TypeError, ValueError):
                continue
            if end > SB.GLAUX_MAX_END and r["SOURCE_LICENSE"] not in GLAUX_NO_LICENCE \
                    and not r["TLG"].startswith(GLAUX_LATE_EXCLUDE_TLG):
                out.append(r)
    return out


def load_greek_late(root, lex, gmap):
    """GLAUx late Greek: grc-late corpus, grc links, grp reviewed decisions."""
    from pie import formula_search as fs
    from pie import formula_search_multi as fm
    sel = glaux_late_selection(root)
    glic = {r["TLG"]: r["SOURCE_LICENSE"] for r in sel}
    gtoks, gsurf = SB.load_glaux_b(sel, root)
    m = fs.build_kaikki_mapping("grc", lex, gtoks, fs.build_homer_mapping(lex, gtoks), root=root, pseudo=True)
    m = fm.apply_lemma_overrides("grp", m, gmap, root=root)
    units = SB.units_from_tokens(
        "grc-late", gtoks, "line", lambda t: t.units["book"], gsurf, {k: tuple(v) for k, v in m.lemma_lex.items()},
        lambda t: lic_pair(f"GLAUx; source text licence: {glic.get(t.units['book'], '?')}"))
    return units, len(sel)


def load_extra(root: Path, lex: list, gmap: dict, log=print) -> tuple[dict, dict]:
    from pie import formula_search as fs
    from pie import formula_search_multi as fm
    out, notes = {}, {}
    ep = fm.load_dcs(texts=DCS_EPIC, corpus="sa-ep", root=root)
    km = fs.build_kaikki_mapping("sa", lex, ep, None, root=root, pseudo=True)
    km = fm.apply_lemma_overrides("av", km, gmap, root=root)
    emap = {k: tuple(v) for k, v in km.lemma_lex.items()}
    emap.update(B._table("av"))
    # corpus-quality batch 2: the epic's own lemma decisions (corpus "sa-ep") win over the shared 'av'
    # table; before, a sa-ep row reached the index only when an av row said the same (epic dama
    # 'self-restraint' vs AV dama 'house', epic dam 'tame')
    from pie import mapping as mp
    for lem in mp.load_overrides(root)["decisions"].get("sa-ep", {}):
        emap[lem] = tuple(sorted(mp.decide("sa-ep", lem, emap.get(lem, ()), root=root)[0]))
    lic = SB.CORPORA["sa-ep"][2]
    out["sa-ep"] = SB.units_from_tokens("sa-ep", ep, "sentence", lambda t: t.units["chapter"],
                                        [t.surface for t in ep], emap, lambda t: lic_pair(lic))
    log(f"sa-ep: {len(out['sa-ep'])} units")
    out["grc-late"], count = load_greek_late(root, lex, gmap)
    notes["glaux_late_texts"] = count
    log(f"grc-late: {len(out['grc-late'])} units from {count} texts")
    return out, notes


# ---------------------------------------------------------------- loading everything

def _cached(cache_dir, name, fn):
    if cache_dir:
        if name == "stageB" or name.startswith(("celtic-", "bsl")):
            name += "-material-v2"
        p = Path(cache_dir) / f"stagec-cache-{name}.pkl"
        if p.exists():
            return pickle.loads(p.read_bytes())
        res = fn()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(pickle.dumps(res, protocol=pickle.HIGHEST_PROTOCOL))
        return res
    return fn()


def load_all(root: Path = ROOT, cache_dir=None, max_date=None, include_ccmh=False, extract=None, log=print):
    """(units by corpus in ORDER_ALL, lexicon by id, Celtic unit metadata, notes)."""
    from pie import formula_search as fs
    lex = fs.load_jsonl(root / "data/lexicon/lexicon.jsonl")
    gmap = fs.group_map(lex)
    notes: dict = {}
    def stage_b():
        cur, SB.ORDER = SB.ORDER, SB_ORDER_B
        try:
            return SB.load_units_b(root, log)
        finally:
            SB.ORDER = cur
    b_units, by_id, b_notes = _cached(cache_dir, "stageB", stage_b)
    notes["stageB"] = b_notes
    notes["stageB_sga_units_dropped"] = len(b_units.pop("sga", []))
    tag = f"celtic-{max_date or 'all'}"
    cel, meta, n = _cached(cache_dir, tag, lambda: load_celtic(root, lex, max_date, log))
    notes["celtic"] = n
    ger, n = _cached(cache_dir, "germanic", lambda: load_germanic(root, log))
    notes["germanic"] = n
    bsl, n = _cached(cache_dir, "bsl" + ("-ccmh" if include_ccmh else ""), lambda: load_bsl(root, lex, include_ccmh, log))
    notes["bsl"] = n
    east, n = _cached(cache_dir, "east", lambda: load_east(root, lex, extract, log))
    notes["east"] = n
    ext, n = _cached(cache_dir, "extra", lambda: load_extra(root, lex, gmap, log))
    notes["extra"] = n
    units = {**b_units, **cel, **ger, **bsl, **east, **ext}
    for c in units:
        for u in units[c]:
            u.groups = frozenset(gmap.get(x, x) for _, _, ids in u.words for x in ids)
            if c not in CELTIC:
                u.tag = licence_tag(u.licence)
    B.assign_pids(units)
    return {c: units[c] for c in ORDER_ALL if c in units}, by_id, meta, notes


# ---------------------------------------------------------------- retrieval from the pivots

_IDX = None


def _work(us):
    return [(u, _IDX.partners(u)) for u in us]


def pivot_partners(idx, pivots: list[int], procs: int | None = None, chunk: int = 1000) -> dict:
    """pivot uid → Stage B top-k partner list, for the given pivots only (parallel, fork)."""
    global _IDX
    _IDX = idx
    chunks = [pivots[k:k + chunk] for k in range(0, len(pivots), chunk)]
    if procs == 1 or len(pivots) < 5000:
        res = [_work(c) for c in chunks]
    else:
        with mp.get_context("fork").Pool(procs or max(1, mp.cpu_count() - 2)) as pool:
            res = pool.map(_work, chunks)
    return {u: p for part in res for u, p in part if p}


def pivots_of(idx, pivot_corpora) -> list[int]:
    s = set(pivot_corpora)
    return [k for k, (c, _) in enumerate(idx.ref) if c in s]


FLOOR_RULE = (f"floor = the {FLOOR_Q} quantile of the best-partner score over all Stage C pivots that have a partner "
              "(Stage B's rule, applied to the Stage C pivots; a pivot keeps its top-k partners scoring >= floor). "
              "A size rule, not a significance threshold (null_comparison).")
NULL_RULE = ("null model: the same deduplicated units of every corpus, each content word's root-group set permuted "
             "among the content words of its corpus (seed 0); the same retrieval from the Stage C pivots")


def make_params(idx, parts: dict, dist: dict, null: dict | None, pivot_corpora, notes=None) -> dict:
    p = SB.make_params(idx, parts, dist, null)
    best = np.array([v[0][0] for v in parts.values()])
    for k in ("glaux_rule", "orv_texts", "orv_rule", "old_irish"):
        p.pop(k, None)
    p.update({
        "note": "Phase 8c Stage C retrieval and bundle parameters, fixed from the score distribution before any "
                "bundle was built or read (docs/research/8c-preregistration.md, Stage C). Rebuilds read the floor "
                "from this file.",
        "root_weight": "idf = ln(N / df); df = number of indexed units (all corpora, pivots and partners) containing "
                       "the root group; N = indexed units with >= 1 mapped root group",
        "floor_rule": FLOOR_RULE, "floor": SB._q(best, FLOOR_Q), "null_model": NULL_RULE,
        "pivot_corpora": [c for c in pivot_corpora if c in SB.CORPORA],
        "partner_corpora": [c for c in ORDER_ALL if c in SB.CORPORA and c in {x for x, _ in idx.ref}],
        "corpora": {c: SB.CORPORA[c][1] for c in ORDER_ALL if c in {x for x, _ in idx.ref}},
        "glaux_rule": f"Stage B: all GLAUx texts with ENDDATE <= {SB.GLAUX_MAX_END}; Stage C adds: {GLAUX_LATE_RULE}",
        "dcs_epic_rule": DCS_EPIC_RULE,
        "orv_texts": list(SB.ORV_TEXTS), "orv_rule": SB.ORV_RULE,
        "celtic_rule": "raw/daughters/celtic-stageC/units.jsonl, units with dup_of null; Celtic lemmatizers with "
                       "use_skeleton=False; tagged gloss tokens by their lemma (sga-glosses table)",
        "low_mapped_rule": f"units with < {LOW_MAPPED:.0%} of content words mapped are pivots like the others "
                           "(partners only through their mapped words)",
        "seed_strings": {"decoys": f"{SEED_TAG}:{SEED}:decoys", "ids": f"{SEED_TAG}:{SEED}:ids"},
    })
    if notes is not None:
        p["mapping_notes"] = notes
    return p


# ---------------------------------------------------------------- build

class Renderer(SB.Renderer):
    """Stage B's renderer with the passage's licence tag."""

    def passage(self, uid: int) -> dict:
        if uid not in self.cache:
            c, i = self.idx.ref[uid]
            p = SB.render(self.units, c, i, self.by_id)
            p["licence_tag"] = getattr(self.units[c][i], "tag", None) or licence_tag(p["licence"])
            self.cache[uid] = (p, len(json.dumps(p, ensure_ascii=False)) + 4)
        return self.cache[uid][0]


def make_slab(sid, bis, shown, bid_of, rend, idx) -> dict:
    s = SB.make_slab(sid, bis, shown, bid_of, rend, idx)
    s["header"], s["format"] = HEADER, FORMAT_NOTE
    tags = collections.Counter(p["licence_tag"] for p in s["passages"])
    out = {"slab": s["slab"], "header": HEADER, "format": FORMAT_NOTE, "licence_tags": dict(sorted(tags.items())),
           "research_only_passages": sum(1 for p in s["passages"] if p["research_only"]),
           "bundles": s["bundles"], "passages": s["passages"]}
    return out


def loci_only(slab: dict) -> dict:
    return {**{k: v for k, v in slab.items() if k != "passages"},
            "passages": [{"id": p["id"], "corpus": p["corpus"], "locus": p["locus"], "licence": p["licence"],
                          "licence_tag": p["licence_tag"], "research_only": p["research_only"],
                          "lines": [{"role": ln["role"], "locus": ln["locus"]} for ln in p["lines"]]}
                         for p in slab["passages"]]}


def mapped_share(u) -> float:
    return sum(1 for _, _, ids in u.words if ids) / max(1, len(u.words))


def build(units, by_id, params: dict | None = None, procs: int | None = None, log=print, parts=None,
          pivot_corpora=PIVOTS_ALL, meta: dict | None = None, seed: int = SEED) -> dict:
    """Everything except writing. params: a frozen params.json (its floor is used) or None (computed)."""
    meta = meta or {}
    idx = SB.Index(units, by_id)
    pivots = pivots_of(idx, pivot_corpora)
    log(f"index: {idx.N} units with roots, {len(idx.groups)} root groups, {len(pivots)} Stage C pivots")
    parts = parts if parts is not None else pivot_partners(idx, pivots, procs)
    dist = SB.score_distribution(parts)
    if params is None:
        params = make_params(idx, parts, dist, None, pivot_corpora)
    else:
        assert params["top_k"] == SB.TOP_K and params["n_common"] == SB.N_COMMON and \
            params["min_shared"] == SB.MIN_SHARED
    floor = params["floor"]
    kept = SB.kept_partners(parts, floor)
    bundles = SB.build_bundles(idx, kept)
    for b in bundles:
        assert any(g >= idx.n_common for g in SB.bundle_shared(idx, b))
        assert idx.ref[b["pivot"]][0] in pivot_corpora
    log(f"floor {floor}: {len(kept)} pivots, {len(bundles)} bundles")
    rend = Renderer(units, by_id, idx)
    rng = random.Random(f"{SEED_TAG}:{seed}:decoys")
    pools = {c: np.array([k for k, (c2, _) in enumerate(idx.ref) if c2 == c], dtype=np.int32) for c in units}
    pools = {c: p for c, p in pools.items() if len(p)}
    decoy: dict = {}
    order = SB.doc_order(idx, bundles)
    step = round(1 / DECOY_SHARE)
    drawn = [rng.choice(order[k:k + step]) for k in range(0, len(order), step)
             if len(order[k:k + step]) == step or rng.random() < len(order[k:k + step]) / step]
    for bi in drawn:
        b = bundles[bi]
        excl = set(b["units"])
        rep = {}
        for v in b["units"][1:]:
            d = SB.decoy_partner(idx, b["pivot"], v, excl, rng, pools)
            if d is None:
                break
            rep[v] = d
            excl.add(d)
        if len(rep) == len(b["units"]) - 1:
            decoy[bi] = rep
    shown = {bi: [b["pivot"]] + [decoy.get(bi, {}).get(v, v) for v in b["units"][1:]] for bi, b in enumerate(bundles)}
    slab_bis = SB.pack_slabs(idx, bundles, rend, shown)
    ids_rng = random.Random(f"{SEED_TAG}:{seed}:ids")
    sids = SB._ids("SC", 4, len(slab_bis), ids_rng)
    bids = SB._ids("BC", 5, len(bundles), ids_rng)
    perm = list(range(len(bundles)))
    ids_rng.shuffle(perm)
    bid_of = {bi: bids[perm[bi]] for bi in range(len(bundles))}
    slabs, key = {}, {"note": "Phase 8c Stage C blinding key: bundle kind, real partners and decoy replacements, "
                              "pivot corpus and (Celtic) witness metadata for the secondary measures.", "slabs": {}}
    for sid, bis in zip(sids, slab_bis):
        slabs[sid] = make_slab(sid, bis, shown, bid_of, rend, idx)
        ent = {}
        for bi in bis:
            b = bundles[bi]
            c, i = idx.ref[b["pivot"]]
            pu = units[c][i]
            ent[bid_of[bi]] = {
                "kind": "decoy" if bi in decoy else "real",
                "pivot": rend.passage(b["pivot"])["id"], "pivot_corpus": c,
                "pivot_group": "celtic" if c in CELTIC else "other",
                "pivot_meta": meta.get(pu.key.split("~w")[0], {}),
                "pivot_mapped_share": round(mapped_share(pu), 3),
                "real_partners": [{"id": rend.passage(v)["id"], "corpus": idx.ref[v][0],
                                   "score_vs_pivot": round(idx.match(b["pivot"], v)[0], 4),
                                   "shared": [idx.groups[g] for g in idx.shared(b["pivot"], v)]}
                                  for v in b["units"][1:]],
                **({"decoy_partners": [rend.passage(decoy[bi][v])["id"] for v in b["units"][1:]]}
                   if bi in decoy else {}),
                "merged": b["merged"]}
        key["slabs"][sid] = ent
    stats = make_stats(units, idx, parts, kept, bundles, slabs, slab_bis, decoy, rend, pivots, pivot_corpora, meta)
    stats["decoy_target"] = len(drawn)
    return {"params": params, "slabs": slabs, "key": key, "stats": stats, "bundles": bundles, "decoy": decoy,
            "idx": idx, "parts": parts,
            "assignment": {"note": "Phase 8c Stage C: one reader per slab (Stage B capacity).",
                           "slabs": {sid: f"RC{k + 1:03d}" for k, sid in enumerate(sids)}}}


# ---------------------------------------------------------------- stats

def _century(m: dict) -> str:
    mid = (m["date_from"] + m["date_to"]) // 2
    return f"{mid // 100 + 1:02d} c."


def corpus_report(units: dict, meta: dict, idx) -> dict:
    """Per corpus: units, tokens, content words, mapped share, indexed (pivot-able) units, and those
    below the 30% mapped share; Celtic also by language, period, genre and licence."""
    indexed = {(c, i) for c, i in idx.ref}
    out, celtic = {}, {k: collections.defaultdict(collections.Counter) for k in ("lang", "period", "genre", "licence")}
    for c, us in units.items():
        r = collections.Counter()
        for i, u in enumerate(us):
            nw, nm = len(u.words), sum(1 for _, _, ids in u.words if ids)
            r["units"] += 1
            r["tokens"] += len(u.text.split())
            r["content_words"] += nw
            r["content_words_mapped"] += nm
            ix = (c, i) in indexed
            r["indexed_units"] += ix
            low = ix and nm < LOW_MAPPED * nw
            r["indexed_units_below_30pct_mapped"] += low
            if c in CELTIC:
                m = meta.get(u.key.split("~w")[0])
                if not m:
                    continue
                for k, v in (("lang", m["lang"]), ("period", _century(m)), ("genre", m["genre"]),
                             ("licence", m["licence"])):
                    x = celtic[k][v]
                    x["units"] += 1
                    x["tokens"] += len(u.text.split())
                    x["content_words"] += nw
                    x["content_words_mapped"] += nm
                    x["pivots"] += ix
                    x["pivots_below_30pct_mapped"] += low
        out[c] = {"label": SB.CORPORA[c][1], "branch": SB.CORPORA[c][0], "role": "pivot" if c in PIVOTS_ALL else
                  "partner", **dict(r), "mapped_share": round(r["content_words_mapped"] / max(1, r["content_words"]), 4),
                  "licence_tags": dict(collections.Counter(getattr(u, "tag", None) or "?" for u in us))}
    cel = {k: {v: {**dict(x), "mapped_share": round(x["content_words_mapped"] / max(1, x["content_words"]), 4)}
               for v, x in sorted(d.items())} for k, d in celtic.items()}
    return {"corpora": out, "celtic": cel}


def make_stats(units, idx, parts, kept, bundles, slabs, slab_bis, decoy, rend, pivots, pivot_corpora, meta) -> dict:
    sizes = {sid: round(len(SB.dump_slab(s)) / SB.CHARS_PER_TOKEN) for sid, s in slabs.items()}
    total = sum(sizes.values())
    by_c = collections.defaultdict(collections.Counter)
    for bi, b in enumerate(bundles):
        c = idx.ref[b["pivot"]][0]
        by_c[c]["bundles"] += 1
        by_c[c]["decoys"] += bi in decoy
    groups = {g: {"bundles": sum(v["bundles"] for c, v in by_c.items() if (c in CELTIC) == (g == "celtic")),
                  "decoys": sum(v["decoys"] for c, v in by_c.items() if (c in CELTIC) == (g == "celtic"))}
              for g in ("celtic", "other")}
    part_c = collections.Counter(idx.ref[v][0] for b in bundles for v in b["units"][1:])
    sec = {}
    for sid, bis in zip(slabs, slab_bis):
        secs = []
        for bi in bis:
            c, i = idx.ref[bundles[bi]["pivot"]]
            s = f"{c}: {SB.section_of(c, units[c][i])}"
            if not secs or secs[-1] != s:
                secs.append(s)
        sec[sid] = {"bundles": len(bis), "decoy_share": round(sum(bi in decoy for bi in bis) / len(bis), 3),
                    "tokens": sizes[sid], "licence_tags": slabs[sid]["licence_tags"],
                    "sections": secs[:3] + (["..."] if len(secs) > 3 else []) + (secs[-1:] if len(secs) > 3 else [])}
    alt = {}
    best = sorted((p[0][0] for p in parts.values()), reverse=True)
    for q in (0.90, 0.95, 0.97, 0.98, 0.99):
        f = SB._q(np.array(best), q)
        kb = SB.build_bundles(idx, SB.kept_partners(parts, f))
        tok = sum(SB.slab_size_tokens([b["units"]], rend) for b in kb)
        alt[str(q)] = {"floor": f, "bundles": len(kb),
                       "celtic_pivot_bundles": sum(1 for b in kb if idx.ref[b["pivot"]][0] in CELTIC),
                       "slab_tokens_est_no_dedupe": round(tok),
                       "read_tokens_est_no_dedupe": round(tok * SB.READER_OVERHEAD)}
    lowset = {u for u in pivots if mapped_share(units[idx.ref[u][0]][idx.ref[u][1]]) < LOW_MAPPED}
    rep = corpus_report(units, meta, idx)
    return {
        **rep,
        "index": {"units_with_roots": idx.N, "root_groups": len(idx.groups), "stageC_pivots": len(pivots)},
        "pivots_below_30pct_mapped": len(lowset),
        "pivots_below_30pct_mapped_with_partner": sum(1 for u in parts if u in lowset),
        "pivots_below_30pct_mapped_in_bundles": sum(1 for b in bundles if b["pivot"] in lowset),
        "pivots_with_any_partner": len(parts), "pivots_above_floor": len(kept),
        "bundles": len(bundles), "bundles_merged_into": sum(1 for b in bundles if b["merged"]),
        "bundle_size": dict(sorted(collections.Counter(len(b["units"]) for b in bundles).items())),
        "decoy_bundles": len(decoy), "real_bundles": len(bundles) - len(decoy),
        "decoy_share": round(len(decoy) / max(1, len(bundles)), 4),
        "pivot_groups": groups,
        "bundles_by_pivot_corpus": {c: dict(by_c[c]) for c in pivot_corpora if c in by_c},
        "slabs": len(slabs), "slab_tokens": sec,
        "decoy_share_per_slab_min_max": [min(v["decoy_share"] for v in sec.values()),
                                         max(v["decoy_share"] for v in sec.values())] if sec else [],
        "slab_tokens_min_max": [min(sizes.values()), max(sizes.values())] if sizes else [],
        "total_slab_tokens": total, "read_tokens_est": round(total * SB.READER_OVERHEAD),
        "readers_at_stageB_capacity": len(slabs),
        "reader_capacity": {"target_tokens": SB.SLAB_TARGET, "max_tokens": SB.SLAB_MAX},
        "partner_slots_by_corpus": dict(sorted(part_c.items(), key=lambda x: -x[1])),
        "floor_alternatives": alt,
    }


# ---------------------------------------------------------------- writing

def write(res: dict, out_dir: Path = OUT, key_path: Path = KEY) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    for sub in ("slabs", "slabs-loci"):
        d = out_dir / sub
        d.mkdir(exist_ok=True)
        for old in d.glob("SC-*.json"):
            old.unlink()
    for sid, s in res["slabs"].items():
        text = SB.dump_slab(s)
        assert json.loads(text) == s
        (out_dir / "slabs" / f"{sid}.json").write_text(text, "utf-8")
        (out_dir / "slabs-loci" / f"{sid}.json").write_text(SB.dump_slab(loci_only(s)), "utf-8")
    (out_dir / "assignment.json").write_text(dump(res["assignment"]), "utf-8")
    (out_dir / "stats.json").write_text(dump(res["stats"]), "utf-8")
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(dump(res["key"]), "utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", type=Path, help="directory for per-loader pickles (reused when present)")
    ap.add_argument("--procs", type=int, default=None)
    ap.add_argument("--refreeze", action="store_true", help="recompute params.json (only before any slab is read)")
    ap.add_argument("--celtic-max-date", type=int, default=None,
                    help="leave out Early Modern Irish units with witness year after this (not pre-registered)")
    ap.add_argument("--include-ccmh", action="store_true", help="add CCMH OCS as pivots (Bible translations: not "
                    "pre-registered for Stage C)")
    ap.add_argument("--kaikki-extract", type=Path, default=None,
                    help="directory of kaikki all-languages extracts (sqj-pro.jsonl, ine-toc-pro.jsonl)")
    ap.add_argument("--time-sample", type=int, default=0, help="time retrieval on N pivots and stop")
    args = ap.parse_args()
    log = lambda *a: print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)
    pivot_corpora = PIVOTS_ALL if args.include_ccmh else tuple(c for c in PIVOTS_ALL if c != "ccmh")
    units, by_id, meta, notes = load_all(ROOT, args.cache_dir, args.celtic_max_date, args.include_ccmh,
                                         args.kaikki_extract, log)
    notes["celtic_max_date"] = args.celtic_max_date
    notes["include_ccmh"] = args.include_ccmh
    log("loaded: " + ", ".join(f"{c} {len(us)}" for c, us in units.items()))
    if args.time_sample:
        idx = SB.Index(units, by_id)
        pv = pivots_of(idx, pivot_corpora)
        sample = random.Random(0).sample(pv, min(args.time_sample, len(pv)))
        t0 = time.time()
        p = pivot_partners(idx, sample, args.procs)
        dt = time.time() - t0
        log(f"N {idx.N}, pivots {len(pv)}; {len(sample)} pivots in {dt:.1f}s ({len(p)} with partners); "
            f"est. full {dt * len(pv) / len(sample) / 60:.1f} min")
        return 0
    pfile = OUT / "params.json"
    params = None if args.refreeze or not pfile.exists() else json.loads(pfile.read_text("utf-8"))
    if params is None:      # freeze the floor before any bundle is built
        idx = SB.Index(units, by_id)
        pv = pivots_of(idx, pivot_corpora)
        parts = pivot_partners(idx, pv, args.procs)
        log(f"partners: {len(parts)} of {len(pv)} pivots")
        nidx = SB.Index(units, by_id, shuffle_seed=SEED)
        nparts = pivot_partners(nidx, pivots_of(nidx, pivot_corpora), args.procs)
        best = np.array([p[0][0] for p in parts.values()])
        floors = sorted({SB._q(best, q) for q in (0.75, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999)})
        params = make_params(idx, parts, SB.score_distribution(parts),
                             SB.null_comparison(idx, parts, nidx, nparts, floors), pivot_corpora, notes)
        OUT.mkdir(parents=True, exist_ok=True)
        pfile.write_text(json.dumps(params, ensure_ascii=False, indent=1) + "\n", "utf-8")
        log(f"params frozen: floor {params['floor']}")
        del nidx, nparts
        res = build(units, by_id, params, args.procs, log, parts=parts, pivot_corpora=pivot_corpora, meta=meta)
    else:
        res = build(units, by_id, params, args.procs, log, pivot_corpora=pivot_corpora, meta=meta)
    res["stats"]["mapping_notes"] = notes
    write(res)
    st = res["stats"]
    log(f"bundles {st['bundles']}, decoys {st['decoy_bundles']} ({st['decoy_share']}), slabs {st['slabs']}, "
        f"slab tokens {st['total_slab_tokens']}, read est. {st['read_tokens_est']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
