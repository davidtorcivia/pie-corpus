#!/usr/bin/env python3
"""Phase 8c Stage B (the discovery run): corpora, retrieval, bundles,
embedded decoys, reader slabs and the blinding key, as pre-registered in
docs/research/8c-preregistration.md ("Stage B", "Reader capacity and search").

  uv run python -I scripts/build_8c_stageB.py [--cache PATH]

1. Corpora (Stage A's loaders and passage format, scripts/build_8c_packets.py,
   with the mapping errata of data/research/formulas/mapping-overrides.json):
   Rigveda (pada), Atharvaveda Śaunaka + Paippalāda (DCS sentence), Avesta
   (CAB ab), Homer (line), GLAUx poetry and prose with ENDDATE <= -300
   (verse line, else sentence; Homer excluded, AGDT has it), Poetic Edda and
   Old English poetry (line), Hittite (TLHdig line, all texts), Latin LASLA
   (line/paragraph), Umbrian (line), Latvian dainas (song), Old Irish (UD
   glosses, sentence), early Old Russian from TOROT (sentence; ORV_TEXTS).
   Bible translations are not loaded. A unit with more than MAX_WORDS content
   words is cut into consecutive windows of near-equal size (a "line window"),
   so long prose sentences do not outscore verse by length alone.
2. Retrieval. Every unit with mapped roots is a pivot (exact repeats of an
   earlier unit, same corpus and content lemmas, are left out). Root weight:
   idf = ln(N / df), df = number of units (all corpora) containing the root
   group. A partner is a unit of another branch sharing >= 2 root groups by
   a word-to-word matching (each word and root counted once, so one
   ambiguously mapped word is not two roots), at least one outside the
   N_COMMON most frequent; score = sum of the matched groups' idf. Kept: the
   TOP_K best partners per pivot scoring >= the floor frozen in params.json
   (FLOOR_RULE, with a word-shuffle null comparison).
3. Bundles: pivot + kept partners. Merge rule: in order of best partner
   score, a bundle whose pivot and at least one partner already sit in a kept
   bundle is merged into it (new units added best first, up to MERGE_CAP
   passages); otherwise it is kept as a new bundle.
4. Slabs: bundles in document order of their pivots, grouped by pivot corpus
   section (Rigveda maṇḍala, AV kāṇḍa, Homer book, GLAUx work, Hittite
   tablet file, ...), packed greedily: a new section starts a new slab once the
   slab holds SLAB_TARGET tokens; a section is split when the slab would
   exceed SLAB_MAX. Passages are rendered once per slab (bundles list ids);
   sizes are those of the slab as shown (decoys included).
   Tokens are estimated as characters / 3.5.
5. Embedded decoys (drawn before packing): in document order of the pivots,
   one bundle in every consecutive block of 1/DECOY_SHARE (seeded random), so
   every slab holds about DECOY_SHARE decoys, has every non-pivot passage replaced by a unit of the same corpus matched
   on content-word count and mean root idf that shares no root group outside
   the N_COMMON most frequent with the pivot and at most one in all (chance
   level: below the retrieval criterion). Key: data/audits/keys/8c-stageB-key.json.

Ids S-xxxx (slabs) and B-xxxxx (bundles) are random. Slabs with daughter text
go to data/research/8c/stageB/slabs/ (gitignored); slabs-loci/ holds the same
structure with loci only. Nothing under raw/ is executed.
"""

from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import json
import math
import multiprocessing as mp
import pickle
import random
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_8c_packets", ROOT / "scripts" / "build_8c_packets.py")
B = sys.modules.get("build_8c_packets")
if B is None:
    B = importlib.util.module_from_spec(_spec)
    sys.modules["build_8c_packets"] = B
    _spec.loader.exec_module(B)

OUT = ROOT / "data" / "research" / "8c" / "stageB"
KEY = ROOT / "data" / "audits" / "keys" / "8c-stageB-key.json"
SEED = 0
MAX_WORDS = 16
TOP_K = 6
N_COMMON = 50
MIN_SHARED = 2
MERGE_CAP = 12
DECOY_SHARE = 0.2
SLAB_TARGET, SLAB_MAX, SLAB_FLUSH_AT_CORPUS = 600_000, 700_000, 350_000
CHARS_PER_TOKEN = 3.5
READER_OVERHEAD = 1.3
BUDGET = 60_000_000
HEADER = "Comparison bundles: passages from several Indo-European traditions"
FORMAT_NOTE = ("A slab holds comparison bundles. Each bundle names one pivot passage and partner passages from other "
               "branches (ids into 'passages'). A passage is a verse line, stanza, sentence or a window of a long "
               "sentence (role 'passage') with one unit of context on either side where the text has one. For every "
               "content word: its form, its corpus lemma, and the PIE lexicon etymon it maps to (id, reconstructed "
               "form, the lexicon's gloss; 'unmapped' if none). Mappings are automatic and can be wrong. Cite passages "
               "by their 'id' and claims by bundle. Passages marked research_only come from sources whose licence "
               "forbids commercial use or has not been checked.")

BRANCHES = B.BRANCHES + ("Slavic",)
ORV_TEXTS = ("spi", "lav", "pvl-hyp", "kiev-hyp", "suz-lav", "nov-sin", "rusprav", "ust-vlad", "birchbark", "mst",
             "mstislav-col", "ostromir-col", "nov-marg", "novgorod-jaroslav", "nevsky-treaty", "riga-goth",
             "rig-smol1281", "varlaam", "nov-list")
ORV_RULE = ("TOROT texts in Old Russian (language 'orv') composed before c. 1300 and original East Slavic writing: the "
            "Igor Tale, the chronicles (Primary, Kiev, Suzdal, First Novgorod), Russkaja pravda, the Statute of "
            "Vladimir, birchbark letters, colophons, charters and treaties to 1281. Left out: Church Slavonic ('chu') "
            "texts, the Uspenskij sbornik (largely translated hagiography), and everything later (Zadonshchina, "
            "Smolensk charter 1386, Pskov, Afanasij Nikitin, Domostroj, Avvakum, letters).")
CORPORA = dict(B.CORPORA)
del CORPORA["grp"]
CORPORA["grc"] = ("Greek", "Greek poetry and prose to 300 BC (GLAUx)", None, None)
CORPORA["orv"] = ("Slavic", "Early Old Russian (TOROT)", "CC BY-NC-SA 4.0 (TOROT): non-commercial", True)
ORDER = ("rv", "av", "ae", "hom", "grc", "non", "ang", "hit", "lat", "xum", "lv", "sga", "orv")
GLAUX_MAX_END = -300
EDDA_NOTES = re.compile(r"^Sk[ýy]r[íi]ngar")


# ---------------------------------------------------------------- units

def split_windows(n: int, max_words: int | None = None) -> list[int]:
    """Sizes of near-equal consecutive windows of ≤ max_words (one window if n ≤ max_words)."""
    max_words = max_words or MAX_WORDS
    k = max(1, math.ceil(n / max_words))
    base, extra = divmod(n, k)
    return [base + (1 if j < extra else 0) for j in range(k)]


def units_from_tokens(corpus, toks, unit, book_of, surfaces, mapping, licence_of, text_of=None,
                      max_words: int | None = None, window: bool = True) -> list:
    """Tokens → ordered Units (as build_8c_packets._units_from_tokens), cutting a unit with more than
    max_words content words into windows: key 'k~wJ', locus 'locus (wJ/n)', text = the window's forms."""
    max_words = max_words or MAX_WORDS
    order, by = [], {}
    for t, s in zip(toks, surfaces):
        k = t.units[unit]
        if k not in by:
            by[k] = []
            order.append(k)
        by[k].append((t, s))
    out = []
    text_of = text_of or {}
    for k in order:
        items = by[k]
        t0 = items[0][0]
        from pie.material_units import excluded_token_unit
        if excluded_token_unit(corpus, t0.locus):
            continue
        lic, ro = licence_of(t0)
        cpos = [i for i, (t, _) in enumerate(items) if t.content]
        sizes = split_windows(len(cpos), max_words) if window and len(cpos) > max_words else [len(cpos)]
        start, ci = 0, 0
        for j, sz in enumerate(sizes):
            ci += sz
            end = cpos[ci] if j < len(sizes) - 1 else len(items)
            part = items[start:end]
            words = [(s, t.lemma, tuple(sorted(mapping.get(t.lemma, ())))) for t, s in part if t.content]
            if len(sizes) == 1:
                key, locus = k, t0.locus
                text = text_of.get(k) or " ".join(x for _, x in part if x)
            else:
                key, locus = f"{k}~w{j + 1}", f"{t0.locus} (w{j + 1}/{len(sizes)})"
                text = " ".join(x for _, x in part if x)
            out.append(B.Unit(corpus, key, locus, book_of(t0), text, words, frozenset(), lic, ro))
            start = end
    return out


def _cite(a: dict) -> str:
    """GLAUx prose citation from the div_* attributes: values in order, dropping a value that is a
    prefix of the next (Plato's perseus section and Stephanus page before '2a')."""
    vals = [v for k, v in a.items() if k.startswith("div_") and v]
    out = [v for i, v in enumerate(vals) if not (i + 1 < len(vals) and vals[i + 1].startswith(v))]
    return ".".join(out) or "?"


def glaux_selection_b(root: Path = ROOT, max_end: int = GLAUX_MAX_END) -> list[dict]:
    """Every GLAUx text with ENDDATE ≤ max_end, all genres, Homer (TLG 0012) excluded."""
    out = []
    with open(root / B_fm().GLAUX_DIR / "metadata.txt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            try:
                end = int(r["ENDDATE"])
            except (TypeError, ValueError):
                continue
            if end <= max_end and not r["TLG"].startswith("0012-"):
                out.append(r)
    return out


def load_glaux_b(sel: list[dict], root: Path = ROOT) -> tuple[list, list]:
    """GLAUx tokens (as formula_search_multi.load_glaux) with a unit per verse line where the word has a
    `line`, else per sentence; prose locus = work + div citation + sentence number in that citation."""
    from pie import formula_search as fs
    fm = B_fm()
    toks, surf = [], []
    for r in sel:
        fn = root / fm.GLAUX_DIR / "xml" / f"{r['TLG']}.xml"
        if not fn.exists():
            continue
        text = unicodedata.normalize("NFC", fn.read_text("utf-8"))
        name = f"{r['AUTHOR_STANDARD']} {r['TITLE_STANDARD']}"
        per_cite: collections.Counter = collections.Counter()
        for si, sent in enumerate(text.split("<sentence ")[1:]):
            ws = [dict(fs._ATTR.findall(m[1])) for m in fs._HOM_W.finditer(sent)]
            ws = [a for a in ws if a.get("lemma") and (a.get("postag") or "-")[0] not in "u-"]
            if not ws:
                continue
            prose = [a for a in ws if not a.get("line")]
            sloc = None
            if prose:
                c = _cite(prose[0])
                per_cite[c] += 1
                sloc = f"{name} {c} s{per_cite[c]}"
            for a in ws:
                tag = (a.get("postag") or "-" * 9).ljust(9, "-")
                line = a.get("line")
                if line:
                    unit, locus = f"{r['TLG']}:{line}", f"{name} {line}"
                else:
                    unit, locus = f"{r['TLG']}.s{si}", sloc
                pos = {"n": "noun", "a": "adj", "v": "verb"}.get(tag[0], "other")
                toks.append(fs.Token("grc", a["lemma"], a.get("form", ""), locus,
                                     {"line": unit, "book": r["TLG"]}, tag[0] in fs.HOM_CONTENT, pos))
                surf.append(a.get("form", ""))
    return toks, surf


_P_TOKEN = re.compile(r"<token ([^>]*?)/?>")
_ATTR_H = re.compile(r'([\w:-]+)="([^"]*)"')


def load_torot_b(files, root: Path = ROOT) -> tuple[list, list]:
    """TOROT XML with surface forms (punctuation from presentation-before/after kept on the form)."""
    from pie import formula_search as fs
    fm = B_fm()
    toks, surf = [], []
    for name in files:
        text = (root / fm.PROIEL_DIR / "torot" / f"{name}.xml").read_text("utf-8")
        for chunk in text.split("<sentence ")[1:]:
            m = re.match(r'id="(\d+)"', chunk)
            sid = m[1] if m else str(len(toks))
            first = None
            for tm in _P_TOKEN.finditer(chunk):
                a = dict(_ATTR_H.findall(tm[1]))
                if "empty-token-sort" in a or not a.get("form"):
                    continue
                if first is None:
                    first = f"{name} {a.get('citation-part', '')}".strip()
                pos = a.get("part-of-speech", "")
                lemma = (a.get("lemma") or "?").split("#")[0]
                if a.get('lemma') == 'поити#1':
                    lemma = 'поити@go'
                content = pos[:1] in ("N", "A", "V") and lemma != "?"
                toks.append(fs.Token("orv", lemma, a["form"], first, {"sentence": f"{name}.{sid}", "book": name},
                                     content, 'name' if pos == 'Ne' else {"N": "noun", "A": "adj", "V": "verb"}.get(pos[:1], "other")))
                surf.append((a.get("presentation-before", "") + a["form"] + a.get("presentation-after", "")).strip())
    return toks, surf


def B_fm():
    from pie import formula_search_multi as fm
    return fm


def live(population, lang, toks, backoff, lex, gmap, root=ROOT):
    """Keep the reviewed population distinct from the etymological-link language."""
    from pie import formula_search as fs
    m = fs.build_kaikki_mapping(lang, lex, toks, backoff, root=root, pseudo=True)
    m = B_fm().apply_lemma_overrides(population, m, gmap, root=root)
    return {k: tuple(v) for k, v in m.lemma_lex.items()}


def load_greek_b(root, lex, gmap):
    """GLAUx broad Greek: grc corpus/link language, grp reviewed decisions."""
    from pie import formula_search as fs
    sel = glaux_selection_b(root)
    glic = {r["TLG"]: r["SOURCE_LICENSE"] for r in sel}
    gtoks, gsurf = load_glaux_b(sel, root)
    gmapping = live("grp", "grc", gtoks, fs.build_homer_mapping(lex, gtoks), lex, gmap, root)
    units = units_from_tokens(
        "grc", gtoks, "line", lambda t: t.units["book"], gsurf, gmapping,
        lambda t: (f"GLAUx; source text licence: {glic.get(t.units['book'], '?')}",
                   glic.get(t.units["book"]) not in B.GLAUX_FREE))
    return units, len(sel)


def load_units_b(root: Path = ROOT, log=print) -> tuple[dict, dict, dict]:
    """All Stage B corpora as ordered Units with content words mapped (round-3 mapping + errata).
    Returns (units by corpus, lexicon by id, mapping coverage notes)."""
    from pie import formula_search as fs
    fm = B_fm()
    lex = fs.load_jsonl(root / "data/lexicon/lexicon.jsonl")
    gmap = fs.group_map(lex)
    out: dict = {}
    notes: dict = {}
    lic = lambda c: (lambda t, c=c: (CORPORA[c][2], CORPORA[c][3]))

    rv, hom, lat = fs.load_rv(root), fs.load_homer(root), fs.load_latin(root)
    for c, toks, lang, r1, unit, book in (("rv", rv, "sa", fs.build_rv_mapping, "pada", "hymn"),
                                          ("hom", hom, "grc", fs.build_homer_mapping, "line", "book"),
                                          ("lat", lat, "la", fs.build_latin_mapping, "line", "book")):
        mp_ = live(c, lang, toks, r1(lex, toks), lex, gmap, root)
        out[c] = units_from_tokens(c, toks, unit, lambda t, b=book: t.units[b], [t.surface for t in toks], mp_,
                                   lic(c))
    log("rv/hom/lat loaded")
    av = fm.load_dcs(texts=fm.DCS_VEDIC[:2], root=root)
    out["av"] = units_from_tokens("av", av, "sentence", lambda t: t.units["chapter"], [t.surface for t in av],
                                  B._table("av"), lic("av"))
    out["grc"], notes["glaux_texts"] = load_greek_b(root, lex, gmap)
    sga_files = sorted((root / fm.UD_SGA).glob("*/*.conllu"))
    sga = fm.load_conllu_simple(sga_files, "sga")
    forms, texts = B._sga_surfaces(sga_files)
    assert len(forms) == len(sga)
    sga_lic = lambda t: (("CC BY-NC-SA 4.0 (UD Old_Irish-DipSGG): non-commercial", True)
                         if "dipsgg" in t.units["book"] else ("CC BY-SA 4.0 (UD Old_Irish-DipWBG)", False))
    out["sga"] = units_from_tokens("sga", sga, "sentence", lambda t: t.units["book"], forms, B._table("sga"),
                                   sga_lic, text_of=texts)
    hit = fm.load_hittite(root)
    hlines, hsurf = B._hit_lines(fm, root)
    assert len(hsurf) == len(hit)
    hu = {u.key: u for u in units_from_tokens("hit", hit, "line", lambda t: t.units["line"].split("|")[0], hsurf,
                                              B._table("hit"), lic("hit"), window=False)}
    out["hit"] = []
    hl, hro = CORPORA["hit"][2], CORPORA["hit"][3]
    for k, (locus, book, ws) in hlines.items():
        u = hu.get(k) or B.Unit("hit", k, locus, book, "", [], frozenset(), hl, hro)
        u.text = " ".join(ws)
        out["hit"].append(u)
    log("av/grc/sga/hit loaded")

    idx = fs.PieIndex(lex)
    langs = ("non", "ang", "lv", "xum", "ae")
    protos = fm.ProtoDB(root=root, want_desc=[c for L in langs + ("orv", "cu") for c in fm.LANGS[L].desc_codes])
    lm = {L: fm.build_lang_mapping(L, lex, protos, root=root, idx=idx) for L in langs + ("orv", "cu")}
    ang_lemz = fm.FormLemmatizer(lm["ang"])
    lat_forms = {fs.lat_key(t.surface) for t in lat}
    sources = {
        "non": (fm.edda_lines(root), fm.FormLemmatizer(lm["non"], fallbacks=(fm.non_clitic_variants,)), "line"),
        "ang": (fm.beowulf_lines(root) + fm.grein_lines(lambda w: ang_lemz(fm.grein_normalize(w)), root), ang_lemz,
                "line"),
        "lv": (fm.dainas_units(root), fm.FormLemmatizer(lm["lv"], fallbacks=(fm.lv_diminutive_variants,)), "song"),
        "xum": (fm.umbrian_lines(lat_forms, root), fm.FormLemmatizer(lm["xum"]), "line"),
        "ae": (fm.avesta_units(root), fm.AvestanLemmatizer(lm["ae"], {}), "ab"),
    }
    for c, (units, lemz, unit) in sources.items():
        toks = fm.text_tokens(c, units, lemz, lm[c].is_content)
        surf = [w for _, _, text in units for w in (fm._WORDS.findall(text) if isinstance(text, str) else text)]
        assert len(surf) == len(toks)
        texts = {u[unit]: (text if isinstance(text, str) else " ".join(text)) for _, u, text in units}
        out[c] = units_from_tokens(c, toks, unit, lambda t: t.units["book"], surf, B._table(c), lic(c),
                                   text_of=texts)
    # Finnur Jónsson's notes (Skýringar, Icelandic prose commentary) are in the Edda OCR: not Old Norse verse
    notes["non_notes_units_dropped"] = sum(1 for u in out["non"] if EDDA_NOTES.match(u.book))
    out["non"] = [u for u in out["non"] if not EDDA_NOTES.match(u.book)]
    log("non/ang/lv/xum/ae loaded")

    otoks, osurf = load_torot_b(ORV_TEXTS, root)
    m1, _ = fm.corpus_mapping(otoks, lm["orv"], gmap=gmap)
    m2, _ = fm.corpus_mapping(otoks, lm["cu"], gmap=gmap)      # OCS dictionary as backoff (same lemma spelling)
    omap = {k: tuple(v) for k, v in m2.lemma_lex.items()}
    omap.update({k: tuple(v) for k, v in m1.lemma_lex.items()})
    omap = fm.apply_table_overrides("orv", omap, root=root)
    out["orv"] = units_from_tokens("orv", otoks, "sentence", lambda t: t.units["book"], osurf, omap, lic("orv"))
    cont = [t for t in otoks if t.content]
    notes["orv_content_token_share_mapped"] = round(sum(t.lemma in omap for t in cont) / max(1, len(cont)), 3)
    notes["orv_mapped_by_orv_dictionary"] = len(m1.lemma_lex)
    notes["orv_mapped_by_ocs_backoff"] = len(set(m2.lemma_lex) - set(m1.lemma_lex))
    log("orv loaded")

    by_id = {e["id"]: e for e in lex}
    for us in out.values():
        for u in us:
            u.groups = frozenset(gmap.get(x, x) for _, _, ids in u.words for x in ids)
    B.assign_pids(out)
    return {c: out[c] for c in ORDER}, by_id, notes


def corpus_report(units: dict) -> dict:
    """Units, word tokens (whitespace-split text) and content words per corpus."""
    out = {}
    for c, us in units.items():
        out[c] = {"label": CORPORA[c][1], "branch": CORPORA[c][0], "units": len(us),
                  "units_with_mapped_roots": sum(1 for u in us if u.groups),
                  "tokens": sum(len(u.text.split()) for u in us), "content_words": sum(len(u.words) for u in us)}
    return out


# ---------------------------------------------------------------- retrieval

CAND_K = 50        # candidates per pivot by the fast group score, re-scored word by word


def _group(x: str, by_id: dict) -> str:
    e = by_id.get(x)
    return (e.get("root_id") or x) if e else x


class Index:
    """Units with ≥ 1 root group (exact repeats of an earlier unit of the same corpus, same content lemmas,
    left out: Hittite duplicates, refrains); root df / idf; postings sorted by (branch, uid). Each content
    word is a set of root groups (an ambiguous mapping gives several), so a pair is scored on a matching of
    words: every word and every root counts once. shuffle_seed: the null model, content words' root sets
    permuted within each corpus."""

    def __init__(self, units: dict, by_id: dict, n_common: int | None = None, shuffle_seed=None):
        n_common = N_COMMON if n_common is None else n_common
        bidx = {b: k for k, b in enumerate(BRANCHES)}
        ref, wsets, seen = [], [], set()
        for c in units:
            cw = []
            for i, u in enumerate(units[c]):
                ws = [frozenset(_group(x, by_id) for x in ids) for _, _, ids in u.words]
                dup = (c, tuple(lem for _, lem, _ in u.words))
                if not any(ws) or dup in seen:
                    continue
                seen.add(dup)
                cw.append((i, ws))
            if shuffle_seed is not None:        # the same units; their words' root sets permuted
                flat = [w for _, ws in cw for w in ws]
                random.Random(f"{shuffle_seed}:{c}").shuffle(flat)
                k = 0
                for n, (i, ws) in enumerate(cw):
                    cw[n] = (i, flat[k:k + len(ws)])
                    k += len(ws)
            for i, ws in cw:
                if any(ws):
                    ref.append((c, i))
                    wsets.append([w for w in ws if w])
        self.ref = ref
        self.branch = np.array([bidx[CORPORA[c][0]] for c, _ in ref], dtype=np.int8)
        df = collections.Counter(g for ws in wsets for g in set().union(*ws))
        self.groups = sorted(df, key=lambda g: (-df[g], g))
        self.gid = {g: k for k, g in enumerate(self.groups)}
        self.N = len(ref)
        self.df = np.array([df[g] for g in self.groups], dtype=np.int64)
        self.idf = np.log(self.N / self.df)
        self.n_common = n_common
        self.uwords = [[tuple(sorted(self.gid[g] for g in w)) for w in ws] for ws in wsets]
        self.ugids = [sorted({g for w in ws for g in w}) for ws in self.uwords]
        self.nwords = np.array([len(units[c][i].words) for c, i in ref], dtype=np.int32)
        cm = np.zeros(self.N, dtype=np.uint64)
        for k, gs in enumerate(self.ugids):
            v = 0
            for g in gs:
                if g < n_common:
                    v |= 1 << g
            cm[k] = v
        self.cmask = cm
        post: list = [[] for _ in self.groups]
        for k, gs in enumerate(self.ugids):
            for g in gs:
                post[g].append(k)
        self.post, self.bounds = [], []
        nb = len(BRANCHES)
        for lst in post:
            a = np.array(lst, dtype=np.int32)
            a = a[np.lexsort((a, self.branch[a]))] if len(a) else a
            br = self.branch[a] if len(a) else np.zeros(0, dtype=np.int8)
            self.post.append(a)
            self.bounds.append(np.searchsorted(br, np.arange(nb + 1), side="left"))
        self.mean_idf = np.array([float(self.idf[gs].mean()) for gs in self.ugids])

    def match(self, u: int, v: int) -> tuple[float, list[int]]:
        """Word matching between u and v: (word u, word v, shared root) triples taken by idf, highest
        first, each word and each root used once. Returns (score, matched root gids)."""
        trip = []
        for i, wu in enumerate(self.uwords[u]):
            su = set(wu)
            for j, wv in enumerate(self.uwords[v]):
                for g in su.intersection(wv):
                    trip.append((-self.idf[g], g, i, j))
        trip.sort()
        ui, vj, gs = set(), set(), []
        for _, g, i, j in trip:
            if i in ui or j in vj or g in gs:
                continue
            ui.add(i)
            vj.add(j)
            gs.append(g)
        return float(self.idf[gs].sum()) if gs else 0.0, sorted(gs)

    def shared(self, u: int, v: int) -> list[int]:
        return self.match(u, v)[1]

    def partners(self, u: int, top_k: int | None = None, min_shared: int | None = None) -> list[tuple]:
        """Top-k (score, v, n_shared) partners of pivot u in other branches (score desc, uid asc): ≥ min_shared
        matched roots, ≥ 1 outside the n_common most frequent."""
        top_k = top_k or TOP_K
        min_shared = min_shared or MIN_SHARED
        b = self.branch[u]
        rare = [g for g in self.ugids[u] if g >= self.n_common]
        if not rare:
            return []
        parts, ws = [], []
        for g in rare:
            p, bd = self.post[g], self.bounds[g]
            for seg in (p[:bd[b]], p[bd[b + 1]:]):
                if len(seg):
                    parts.append(seg)
                    ws.append(np.full(len(seg), self.idf[g]))
        if not parts:
            return []
        cand = np.concatenate(parts)
        w = np.concatenate(ws)
        uniq, inv = np.unique(cand, return_inverse=True)
        cnt = np.bincount(inv)
        sc = np.bincount(inv, weights=w)
        m = int(self.cmask[u])
        if m:
            cm = self.cmask[uniq]
            g = 0
            while m:
                if m & 1:
                    hit = ((cm >> np.uint64(g)) & np.uint64(1)).astype(bool)
                    cnt = cnt + hit
                    sc = sc + hit * self.idf[g]
                m >>= 1
                g += 1
        ok = cnt >= min_shared
        if not ok.any():
            return []
        uniq, sc = uniq[ok], sc[ok]
        order = np.lexsort((uniq, -np.round(sc, 9)))[:CAND_K]
        out = []
        for k in order:
            v = int(uniq[k])
            s, gs = self.match(u, v)
            if len(gs) >= min_shared and any(g >= self.n_common for g in gs):
                out.append((round(s, 6), v, len(gs)))
        out.sort(key=lambda x: (-x[0], x[1]))
        return out[:top_k]


_IDX: Index | None = None


def _work(rng_):
    lo, hi = rng_
    return [(u, _IDX.partners(u)) for u in range(lo, hi)]


def all_partners(idx: Index, procs: int | None = None, chunk: int = 2000) -> dict:
    """pivot uid → top-k partner list, computed in parallel (fork)."""
    global _IDX
    _IDX = idx
    ranges = [(lo, min(idx.N, lo + chunk)) for lo in range(0, idx.N, chunk)]
    if procs == 1 or idx.N < 5000:
        res = [_work(r) for r in ranges]
    else:
        ctx = mp.get_context("fork")
        with ctx.Pool(procs or max(1, mp.cpu_count() - 2)) as pool:
            res = pool.map(_work, ranges)
    return {u: p for part in res for u, p in part if p}


# ---------------------------------------------------------------- floor (frozen in params.json)

FLOOR_Q = 0.90
FLOOR_RULE = (f"floor = the {FLOOR_Q} quantile of the best-partner score over all pivots that have a partner (a pivot "
              "keeps its top-k partners scoring >= floor). This is a size rule chosen for the pre-registered budget "
              "(30-60M tokens, 'generous by design; readers judge'), not a significance threshold: against the null "
              "model below, real best-partner scores do not exceed chance except in the far tail (null_comparison).")
NULL_RULE = ("null model: the same deduplicated units, each content word's root-group set permuted among the content "
             "words of its corpus (seed 0); the same retrieval")


def _q(a, q) -> float:
    return round(float(np.quantile(a, q)), 4) if len(a) else 0.0


def score_distribution(parts: dict) -> dict:
    best = np.array(sorted(p[0][0] for p in parts.values()))
    allp = np.array(sorted(s for p in parts.values() for s, _, _ in p))
    qs = (0.5, 0.75, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999)
    return {"pivots_with_partner": int(len(best)), "pairs_top_k": int(len(allp)),
            "best_score_quantiles": {str(q): _q(best, q) for q in qs},
            "pair_score_quantiles": {str(q): _q(allp, q) for q in qs}}


def null_comparison(idx: Index, parts: dict, nidx: Index, nparts: dict, floors) -> dict:
    """Pivots whose best partner scores >= f, real vs null, overall and per pivot corpus."""
    out = {}
    for f in floors:
        r = collections.Counter(idx.ref[u][0] for u, p in parts.items() if p[0][0] >= f)
        n = collections.Counter(nidx.ref[u][0] for u, p in nparts.items() if p[0][0] >= f)
        out[str(round(f, 4))] = {"real": sum(r.values()), "null": sum(n.values()),
                                 "per_corpus_real_null": {c: [r.get(c, 0), n.get(c, 0)] for c in ORDER}}
    return out


def make_params(idx: Index, parts: dict, dist: dict, null: dict | None = None) -> dict:
    best = np.array([p[0][0] for p in parts.values()])
    floor = _q(best, FLOOR_Q)
    return {
        "frozen": True,
        "note": "Phase 8c Stage B retrieval and bundle parameters, fixed from the score distribution before any "
                "bundle was built or read (docs/research/8c-preregistration.md, Stage B). Rebuilds read the floor "
                "from this file.",
        "seed": SEED,
        "units": {"max_content_words": MAX_WORDS, "window_rule": "a unit with more than max_content_words content "
                  "words is cut into ceil(n/max) consecutive windows of near-equal size"},
        "root_weight": "idf = ln(N / df); df = number of units (all Stage B corpora) containing the root group; "
                       "N = units with >= 1 mapped root group",
        "N_units": idx.N,
        "partner_rule": f"other branch; >= {MIN_SHARED} shared root groups, >= 1 of them outside the {N_COMMON} most "
                        "frequent root groups; score = sum of idf over shared groups",
        "top_k": TOP_K, "n_common": N_COMMON, "min_shared": MIN_SHARED,
        "floor_rule": FLOOR_RULE, "floor_quantile": FLOOR_Q, "floor": floor,
        "score_distribution": dist, "null_model": NULL_RULE, "null_comparison": null or {},
        "common_roots": [{"group": idx.groups[g], "df": int(idx.df[g])} for g in range(min(N_COMMON, len(idx.groups)))],
        "merge_rule": f"bundles in order of best partner score; a bundle whose pivot and >= 1 partner already sit in a "
                      f"kept bundle is merged into it (its other units added best first, cap {MERGE_CAP} passages); "
                      "else kept", "merge_cap": MERGE_CAP,
        "decoys": {"share": DECOY_SHARE, "rule": "bundles in document order of their pivots; one in every "
                   "consecutive block of 1/share drawn (seeded random), before slabs are packed; every "
                   "non-pivot passage replaced by a unit of the same corpus, not in the bundle, sharing no root group "
                   f"outside the {N_COMMON} most frequent with the pivot and at most one in all; matched on content-"
                   "word count (within 25%, at least +-1) and mean root idf (within 10%, widened to 20%, 40%, any)"},
        "slabs": {"target_tokens": SLAB_TARGET, "max_tokens": SLAB_MAX,
                  "flush_at_corpus_change": SLAB_FLUSH_AT_CORPUS,
                  "chars_per_token": CHARS_PER_TOKEN, "reader_overhead": READER_OVERHEAD},
        "corpora": {c: CORPORA[c][1] for c in ORDER},
        "glaux_rule": f"all GLAUx texts with ENDDATE <= {GLAUX_MAX_END}, every genre, Homer (TLG 0012) excluded",
        "orv_texts": list(ORV_TEXTS), "orv_rule": ORV_RULE,
        "old_irish": "UD Old Irish glosses only; Thesaurus Palaeohibernicus (OCR, unlemmatized, Irish interleaved "
                     "with Latin and English) is not usable without a separate extraction",
    }


# ---------------------------------------------------------------- bundles

def kept_partners(parts: dict, floor: float) -> dict:
    out = {}
    for u, ps in parts.items():
        k = [p for p in ps if p[0] >= floor]
        if k:
            out[u] = k
    return out


def build_bundles(idx: Index, kept: dict, cap: int | None = None) -> list[dict]:
    """[{pivot, units (pivot first, then by score), scores {uid: score vs pivot}, merged: n}] by the merge rule."""
    cap = cap or MERGE_CAP
    order = sorted(kept, key=lambda u: (-kept[u][0][0], u))
    bundles: list[dict] = []
    where: dict = collections.defaultdict(set)      # uid → bundle indexes containing it
    for u in order:
        ps = kept[u]
        hit = None
        for bi in sorted(where.get(u, ())):
            if any(bi in where.get(v, ()) for _, v, _ in ps):
                hit = bi
                break
        if hit is None:
            b = {"pivot": u, "units": [u] + [v for _, v, _ in ps], "scores": {v: s for s, v, _ in ps}, "merged": 0}
            bundles.append(b)
            bi = len(bundles) - 1
            for x in b["units"]:
                where[x].add(bi)
            continue
        b = bundles[hit]
        b["merged"] += 1
        for s, v, _ in ps:
            if len(b["units"]) >= cap:
                break
            if v not in b["units"]:
                b["units"].append(v)
                b["scores"][v] = s
                where[v].add(hit)
    return bundles


def bundle_shared(idx: Index, b: dict) -> list[int]:
    """Root groups the pivot shares with any partner."""
    p = b["pivot"]
    return sorted({g for v in b["units"][1:] for g in idx.shared(p, v)})


# ---------------------------------------------------------------- rendering and slabs

def render(units, c: str, i: int, by_id) -> dict:
    us = units[c]
    u = us[i]
    prev, nxt = B.neighbours(us, i)
    lines = ([B._line(prev, "context before", by_id)] if prev else []) + [B._line(u, "passage", by_id)] + \
            ([B._line(nxt, "context after", by_id)] if nxt else [])
    return {"id": u.pid, "corpus": CORPORA[c][1], "locus": u.locus, "licence": u.licence,
            "research_only": u.research_only, "lines": lines}


def section_of(c: str, u) -> str:
    if c == "rv":
        return "RV " + u.locus.split()[1].split(".")[0]
    if c == "av":
        p = u.locus.split(",")
        return f"{p[0]} {p[1].strip()}" if len(p) > 1 else u.book
    if c == "hom":
        return u.locus.split(".")[0] + "." + u.locus.split()[1].split(".")[0]
    return u.book


class Renderer:
    def __init__(self, units, by_id, idx: Index):
        self.units, self.by_id, self.idx = units, by_id, idx
        self.cache: dict = {}

    def passage(self, uid: int) -> dict:
        if uid not in self.cache:
            c, i = self.idx.ref[uid]
            p = render(self.units, c, i, self.by_id)
            self.cache[uid] = (p, len(json.dumps(p, ensure_ascii=False)) + 4)
        return self.cache[uid][0]

    def size(self, uid: int) -> int:
        self.passage(uid)
        return self.cache[uid][1]


def bundle_entry_chars(n: int) -> int:
    return 60 + 40 * n


def doc_order(idx: Index, bundles: list[dict]) -> list[int]:
    pos = {c: k for k, c in enumerate(ORDER)}
    return sorted(range(len(bundles)), key=lambda bi: (pos[idx.ref[bundles[bi]["pivot"]][0]],
                                                      idx.ref[bundles[bi]["pivot"]][1]))


def pack_slabs(idx: Index, bundles: list[dict], rend: Renderer, shown: dict) -> list[list[int]]:
    """Bundle indexes per slab: document order of pivots, sections kept together where they fit.
    shown: bundle index → the units as shown (pivot first; decoy partners in place)."""
    order = doc_order(idx, bundles)
    slabs, cur, seen, size = [], [], set(), 0
    last_sec, last_c = None, None

    def flush():
        nonlocal cur, seen, size
        if cur:
            slabs.append(cur)
        cur, seen, size = [], set(), 0

    for bi in order:
        c, i = idx.ref[bundles[bi]["pivot"]]
        sec = (c, section_of(c, rend.units[c][i]))
        if c != last_c and size / CHARS_PER_TOKEN >= SLAB_FLUSH_AT_CORPUS:
            flush()
        elif sec != last_sec and size / CHARS_PER_TOKEN >= SLAB_TARGET:
            flush()
        us = shown[bi]
        add = bundle_entry_chars(len(us)) + sum(rend.size(v) for v in set(us) - seen)
        if cur and (size + add) / CHARS_PER_TOKEN > SLAB_MAX:
            flush()
            add = bundle_entry_chars(len(us)) + sum(rend.size(v) for v in set(us))
        cur.append(bi)
        seen.update(us)
        size += add
        last_sec, last_c = sec, c
    flush()
    return slabs


def slab_size_tokens(units_lists: list[list[int]], rend: Renderer) -> float:
    seen = set()
    chars = 0
    for us in units_lists:
        chars += bundle_entry_chars(len(us))
        for v in us:
            if v not in seen:
                seen.add(v)
                chars += rend.size(v)
    return chars / CHARS_PER_TOKEN


# ---------------------------------------------------------------- decoys

def decoy_partner(idx: Index, pivot: int, real: int, exclude: set, rng: random.Random, pools: dict) -> int | None:
    """A same-corpus unit matched on content-word count and mean idf with no beyond-chance root overlap."""
    c = idx.ref[real][0]
    pool = pools[c]
    n0, m0 = int(idx.nwords[real]), float(idx.mean_idf[real])
    tol_n = max(1, round(0.25 * n0))
    pg = set(idx.ugids[pivot])
    nw = idx.nwords[pool]
    base = pool[np.abs(nw - n0) <= tol_n]
    for tol in (0.10, 0.20, 0.40, None):
        cand = base if tol is None else base[np.abs(idx.mean_idf[base] - m0) <= tol * m0]
        if not len(cand):
            continue
        for v in rng.sample(sorted(int(x) for x in cand), min(3000, len(cand))):
            v = int(v)
            if v in exclude:
                continue
            sh = pg & set(idx.ugids[v])
            if len(sh) <= 1 and all(g < idx.n_common for g in sh):
                return v
    return None


# ---------------------------------------------------------------- build

def _ids(prefix: str, width: int, n: int, rng: random.Random) -> list[str]:
    out: list = []
    seen = set()
    while len(out) < n:
        x = f"{prefix}-{rng.randrange(16 ** width):0{width}x}"
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def build(units, by_id, params: dict | None = None, procs: int | None = None, log=print, parts=None) -> dict:
    """Everything except writing. params: a frozen params.json (its floor is used) or None (computed)."""
    idx = Index(units, by_id)
    log(f"index: {idx.N} units with roots, {len(idx.groups)} root groups")
    parts = parts if parts is not None else all_partners(idx, procs)
    dist = score_distribution(parts)
    if params is None:
        params = make_params(idx, parts, dist)
    else:
        assert params["top_k"] == TOP_K and params["n_common"] == N_COMMON and params["min_shared"] == MIN_SHARED
    floor = params["floor"]
    kept = kept_partners(parts, floor)
    bundles = build_bundles(idx, kept)
    for b in bundles:
        assert any(g >= idx.n_common for g in bundle_shared(idx, b))
    log(f"floor {floor}: {len(kept)} pivots, {len(bundles)} bundles")
    rend = Renderer(units, by_id, idx)
    rng = random.Random(f"8c-stageB:{SEED}:decoys")
    pools = {c: np.array([k for k, (c2, _) in enumerate(idx.ref) if c2 == c], dtype=np.int32) for c in ORDER}
    pools = {c: p for c, p in pools.items() if len(p)}
    decoy: dict = {}
    order = doc_order(idx, bundles)
    step = round(1 / DECOY_SHARE)
    drawn = [rng.choice(order[k:k + step]) for k in range(0, len(order), step)
             if len(order[k:k + step]) == step or rng.random() < len(order[k:k + step]) / step]
    decoy_target = len(drawn)
    for bi in drawn:
        b = bundles[bi]
        excl = set(b["units"])
        rep = {}
        for v in b["units"][1:]:
            d = decoy_partner(idx, b["pivot"], v, excl, rng, pools)
            if d is None:
                break
            rep[v] = d
            excl.add(d)
        if len(rep) == len(b["units"]) - 1:
            decoy[bi] = rep
    shown = {bi: [b["pivot"]] + [decoy.get(bi, {}).get(v, v) for v in b["units"][1:]] for bi, b in enumerate(bundles)}
    slab_bis = pack_slabs(idx, bundles, rend, shown)
    ids_rng = random.Random(f"8c-stageB:{SEED}:ids")
    sids = _ids("S", 4, len(slab_bis), ids_rng)
    bids = _ids("B", 5, len(bundles), ids_rng)
    perm = list(range(len(bundles)))
    ids_rng.shuffle(perm)
    bid_of = {bi: bids[perm[bi]] for bi in range(len(bundles))}
    slabs, key = {}, {"note": "Phase 8c Stage B blinding key: bundle kind, real partners and decoy replacements.",
                      "slabs": {}}
    for sid, bis in zip(sids, slab_bis):
        slabs[sid] = make_slab(sid, bis, shown, bid_of, rend, idx)
        key["slabs"][sid] = {bid_of[bi]: {
            "kind": "decoy" if bi in decoy else "real",
            "pivot": rend.passage(bundles[bi]["pivot"])["id"],
            "real_partners": [{"id": rend.passage(v)["id"],
                               "score_vs_pivot": round(idx.match(bundles[bi]["pivot"], v)[0], 4),
                               "shared": [idx.groups[g] for g in idx.shared(bundles[bi]["pivot"], v)]}
                              for v in bundles[bi]["units"][1:]],
            **({"decoy_partners": [rend.passage(decoy[bi][v])["id"] for v in bundles[bi]["units"][1:]]}
               if bi in decoy else {}),
            "merged": bundles[bi]["merged"]} for bi in bis}
    stats = make_stats(units, idx, parts, kept, bundles, slabs, slab_bis, decoy, params, rend)
    stats["decoy_target"] = decoy_target
    return {"params": params, "slabs": slabs, "key": key, "stats": stats, "bundles": bundles, "decoy": decoy,
            "idx": idx, "parts": parts,
            "assignment": {"note": "Phase 8c Stage B: one reader per slab.",
                           "slabs": {sid: f"RB{k + 1:03d}" for k, sid in enumerate(sids)}}}


def make_slab(sid, bis, shown, bid_of, rend: Renderer, idx: Index) -> dict:
    bl, seen, passages = [], set(), []
    for bi in sorted(bis, key=lambda x: bid_of[x]):
        us = shown[bi]
        bl.append({"bundle": bid_of[bi], "pivot": rend.passage(us[0])["id"],
                   "partners": [rend.passage(v)["id"] for v in us[1:]]})
    for bi in bis:          # passages in document order of first use (pivot sections stay together)
        for v in shown[bi]:
            if v not in seen:
                seen.add(v)
                passages.append(rend.passage(v))
    return {"slab": sid, "header": HEADER, "format": FORMAT_NOTE, "bundles": bl, "passages": passages}


def loci_only(slab: dict) -> dict:
    return {**{k: v for k, v in slab.items() if k != "passages"},
            "passages": [{"id": p["id"], "corpus": p["corpus"], "locus": p["locus"], "licence": p["licence"],
                          "research_only": p["research_only"],
                          "lines": [{"role": ln["role"], "locus": ln["locus"]} for ln in p["lines"]]}
                         for p in slab["passages"]]}


def dump_slab(s: dict) -> str:
    head = {k: v for k, v in s.items() if k not in ("bundles", "passages")}
    lines = ["{"] + [f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}," for k, v in head.items()]
    for name in ("bundles", "passages"):
        lines.append(f' {json.dumps(name)}: [')
        xs = s[name]
        lines += ["  " + json.dumps(x, ensure_ascii=False) + ("," if k < len(xs) - 1 else "") for k, x in enumerate(xs)]
        lines.append(" ]" + ("," if name == "bundles" else ""))
    lines.append("}")
    return "\n".join(lines) + "\n"


def make_stats(units, idx, parts, kept, bundles, slabs, slab_bis, decoy, params, rend) -> dict:
    sizes = {sid: round(len(dump_slab(s)) / CHARS_PER_TOKEN) for sid, s in slabs.items()}
    total = sum(sizes.values())
    piv_c = collections.Counter(idx.ref[b["pivot"]][0] for b in bundles)
    part_c = collections.Counter(idx.ref[v][0] for b in bundles for v in b["units"][1:])
    units_c = collections.Counter(idx.ref[v][0] for b in bundles for v in b["units"])
    sec = {}
    for sid, bis in zip(slabs, slab_bis):
        secs = []
        for bi in bis:
            c, i = idx.ref[bundles[bi]["pivot"]]
            s = f"{c}: {section_of(c, units[c][i])}"
            if not secs or secs[-1] != s:
                secs.append(s)
        sec[sid] = {"bundles": len(bis), "decoy_share": round(sum(bi in decoy for bi in bis) / len(bis), 3),
                    "tokens": sizes[sid], "sections": secs[:3] + (["..."] if len(secs) > 3 else [])
                    + (secs[-1:] if len(secs) > 3 else [])}
    alt = {}
    best = sorted((p[0][0] for p in parts.values()), reverse=True)
    for q in (0.90, 0.95, 0.97, 0.98, 0.99):
        f = _q(np.array(best), q)
        kb = build_bundles(idx, kept_partners(parts, f))
        tok = sum(slab_size_tokens([b["units"]], rend) for b in kb)
        alt[str(q)] = {"floor": f, "bundles": len(kb), "slab_tokens_est_no_dedupe": round(tok),
                       "read_tokens_est_no_dedupe": round(tok * READER_OVERHEAD)}
    return {
        "corpora": corpus_report(units),
        "index": {"units_with_roots": idx.N, "root_groups": len(idx.groups)},
        "pivots_with_any_partner": len(parts), "pivots_above_floor": len(kept),
        "bundles": len(bundles), "bundles_merged_into": sum(1 for b in bundles if b["merged"]),
        "bundle_size": dict(sorted(collections.Counter(len(b["units"]) for b in bundles).items())),
        "decoy_bundles": len(decoy), "decoy_share": round(len(decoy) / max(1, len(bundles)), 4),
        "slabs": len(slabs), "slab_tokens": sec,
        "decoy_share_per_slab_min_max": [min(v["decoy_share"] for v in sec.values()),
                                         max(v["decoy_share"] for v in sec.values())] if sec else [],
        "slab_tokens_min_max": [min(sizes.values()), max(sizes.values())] if sizes else [],
        "total_slab_tokens": total, "read_tokens_est": round(total * READER_OVERHEAD),
        "coverage": {c: {"pivot_bundles": piv_c.get(c, 0), "partner_slots": part_c.get(c, 0),
                         "unit_slots": units_c.get(c, 0)} for c in ORDER},
        "floor_alternatives": alt,
    }


def write(res: dict, out_dir: Path = OUT, key_path: Path = KEY) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    for sub in ("slabs", "slabs-loci"):
        d = out_dir / sub
        d.mkdir(exist_ok=True)
        for old in d.glob("S-*.json"):
            old.unlink()
    for sid, s in res["slabs"].items():
        text = dump_slab(s)
        assert json.loads(text) == s
        (out_dir / "slabs" / f"{sid}.json").write_text(text, "utf-8")
        (out_dir / "slabs-loci" / f"{sid}.json").write_text(dump_slab(loci_only(s)), "utf-8")
    (out_dir / "assignment.json").write_text(dump(res["assignment"]), "utf-8")
    (out_dir / "stats.json").write_text(dump(res["stats"]), "utf-8")
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(dump(res["key"]), "utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, help="pickle of the loaded corpora (created if missing)")
    ap.add_argument("--procs", type=int, default=None)
    args = ap.parse_args()
    log = lambda *a: print(*a, file=sys.stderr, flush=True)
    if args.cache and args.cache.exists():
        units, by_id, notes = pickle.loads(args.cache.read_bytes())
    else:
        units, by_id, notes = load_units_b(ROOT, log)
        if args.cache:
            args.cache.write_bytes(pickle.dumps((units, by_id, notes)))
    log(f"notes: {notes}")
    pfile = OUT / "params.json"
    params = json.loads(pfile.read_text("utf-8")) if pfile.exists() else None
    if params is None:      # freeze the floor before any bundle is built
        idx = Index(units, by_id)
        parts = all_partners(idx, args.procs)
        nidx = Index(units, by_id, shuffle_seed=SEED)
        nparts = all_partners(nidx, args.procs)
        best = np.array([p[0][0] for p in parts.values()])
        floors = sorted({_q(best, q) for q in (0.75, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999)})
        params = make_params(idx, parts, score_distribution(parts),
                             null_comparison(idx, parts, nidx, nparts, floors))
        params["mapping_notes"] = notes
        OUT.mkdir(parents=True, exist_ok=True)
        pfile.write_text(json.dumps(params, ensure_ascii=False, indent=1) + "\n", "utf-8")
        log(f"params frozen: floor {params['floor']}")
        res = build(units, by_id, params, args.procs, log, parts=parts)
    else:
        res = build(units, by_id, params, args.procs, log)
    write(res)
    st = res["stats"]
    log(f"bundles {st['bundles']}, decoys {st['decoy_bundles']} ({st['decoy_share']}), slabs {st['slabs']}, "
        f"slab tokens {st['total_slab_tokens']}, read est. {st['read_tokens_est']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
