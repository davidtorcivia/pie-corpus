#!/usr/bin/env python3
"""Phase 8c Stage C-S (the stratified rebuild of Stage C), as pre-registered in
docs/research/8c-preregistration.md ("Stage C-S"): Stage C's corpora, mappings and units
(scripts/build_8c_stageC.py, imported), with targeted pairing of comparable texts.

  uv run python -I scripts/build_8c_stageCS.py [--cache-dir DIR] [--refreeze] [--procs N] [--dry-run]

1. Layer filter: only units in each tradition's earliest, least derivative layer (per genre) are
   indexed, as pivots and as partners (`classes`; the table in the pre-registration). Inverse
   frequency is computed over the indexed units only. Left-out units stay in the corpus lists, so
   context lines are rendered as before.
2. Genre classes NARR, CULT, LAW, WISDOM, LYR (a bit mask per unit): a partner shares a class with
   its pivot.
3. At most CORPUS_CAP of a pivot's TOP_K partners come from one corpus.
4. Decoys: Stage B's rule (same corpus as the real partner, matched on content-word count and mean
   idf, no beyond-chance root overlap) drawn from the indexed units that share a class with the pivot.
5. Floor: Stage B's size rule over the Stage C-S pivots, frozen in params.json before any bundle is
   built. Retrieval, bundles, merging, slab packing and rendering are Stage B's / Stage C's.

--dry-run loads, classifies and prints the kept and left-out counts per corpus and document, then stops.
Nothing under raw/ is executed or imported; raw files are read as text or JSON.
"""

from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import json
import random
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
_C_NAME = "build_8c_stageC__stageCS"
C = sys.modules.get(_C_NAME)
if C is None:
    _spec = importlib.util.spec_from_file_location(_C_NAME, ROOT / "scripts" / "build_8c_stageC.py")
    C = importlib.util.module_from_spec(_spec)
    sys.modules[_C_NAME] = C
    _spec.loader.exec_module(C)
SB, B = C.SB, C.B

OUT = ROOT / "data" / "research" / "8c" / "stageCS"
KEY = ROOT / "data" / "audits" / "keys" / "8c-stageCS-key.json"
SEED = 0
SEED_TAG = "8c-stageCS"
CORPUS_CAP = 2
CAND_MAX = 400              # most candidates rescored per pivot when the cap leaves slots empty
THIN_MAX_UNITS = 15000      # a partner corpus with fewer indexed units is thin
THIN_SLOTS = 2
HEADER = ("Comparison bundles (Stage C-S): Celtic and newly added traditions with partners from the "
          "comparable layers and genres of all branches")

NARR, CULT, LAW, WISDOM, LYR = 1, 2, 4, 8, 16
CLASS_NAMES = {NARR: "NARR", CULT: "CULT", LAW: "LAW", WISDOM: "WISDOM", LYR: "LYR"}
PIVOTS = tuple(c for c in C.PIVOTS_ALL if c != "ccmh")
GLAUX_META = "raw/daughters/glaux/src/glaux-main/metadata.txt"
HIT_DIR = "raw/daughters/hittite-tlhdig/extract/TLHbasisONLINE25_1_ZENODO_Beta_03"


def class_names(mask: int) -> list[str]:
    return [n for b, n in CLASS_NAMES.items() if mask & b]


# ---------------------------------------------------------------- the layer and genre table

CELTIC_GENRE = {"saga": NARR, "history": NARR, "prose": NARR, "dindshenchas": NARR,
                "verse": CULT | LYR | NARR, "law": LAW, "wisdom": WISDOM | LAW}
CELTIC_MAX_MID = 1250

MENOTA_PREFIX = ("AM-132-fol-", "AM-162-B-")
MENOTA_NARR = ("Wolf-Aug-9-10-4to", "AM-113-b-fol", "AM-35-fol", "AM-36-fol",
               "AM-63-fol", "Lbs-fragm-82", "NRA-norrfragm-51", "NRA-norrfragm-52", "NRA-norrfragm-53",
               "NRA-norrfragm-54", "NRA-norrfragm-55-A", "NRA-norrfragm-55-B", "NRA-norrfragm-56", "DG-8-OHleg", "HolmPerg-4-fol",
               "AM-178-fol", "AM-242-fol", "AM-544-4to-Vsp", "GKS-2365-4to-Vsp")
MENOTA_LAW = ("AM-302-fol", "AM-305-fol", "AM-56-4to", "AM-60-4to", "DG-8-MLL", "HolmPerg-30-4to",
              "HolmPerg-34-4to-MLL", "HolmPerg-34-4to-MLB", "NRA-norrfragm-7", "AM-279-a-4to", "TuebUB-Me-II-2",
              "AM-78-4to")

REA_GOH = ((NARR, ("Hildebrandlied", "Ludwigslied", "DeHeinrico", "Muspilli", "Wessobrunn")),
           (CULT, ("segen", "Segen", "Zauber", "Contra", "Ad_equum")),
           (WISDOM, ("Sprichwoerter",)),
           (LAW, ("LexSalica", "Markbeschreibung", "Priestereid")),
           (LYR, ("HirschundHinde",)))
REA_OSX = ((CULT, ("Contra_Vermes", "Blutsegen", "Spurihalz")), (WISDOM, ("Abecedarium",)))

ANG = ((NARR, ("Beo.", "Finn.", "I:Byrhtnoth", "I:Btrhtnoth", "I:Btbhtnoth", "I:Byrhtnotb", "I:Athelstan",
               "I:A T H E L S T A N", "I:Eadgar", "I:Eadmund", "I:Eadqak", "I:Eadveard", "I:Tod Alfreds",
               "I:Tod Alfreds, Des Somes Adelreds")),
       (LYR, ("I:Ruine", "I:Seefahrer", "I:Wanderer,", "I:Klage Der Frau", "I:Botschmt Des Gemahls An Seine Frau")),
       (WISDOM, ("I:Bi Manna Vyrdiim", "I:Bt Manna Mode", "II:Bi Manna Lease", "II:Versus Gnomici",
                 "II:Yersus Unomici", "II:Kunenlied", "II:Fader Larcvidas")))

ORV = {"spi": NARR, "lav": NARR, "nov-sin": NARR, "suz-lav": NARR, "pvl-hyp": NARR, "kiev-hyp": NARR,
       "rusprav": LAW, "riga-goth": LAW, "nevsky-treaty": LAW, "rig-smol1281": LAW, "novgorod-jaroslav": LAW,
       "nov-list": LAW, "ust-vlad": LAW}
XCL_NARR = ("Movses_Khor", "Faustos", "Agathangelos", "Yeghishe", "Lazar_Parp")
LAT = {"CatAgr": CULT, "Catul": LYR, "CatOrig": NARR}

GLAUX_GENRE = {"Epic poetry": NARR, "Lyric poetry": LYR | CULT, "Tragedy": NARR | LYR, "History": NARR,
               "Scientific Poetry": WISDOM}
GLAUX_MAX_END = -400


def hittite_class(cth: int | None) -> int:
    if cth is None:
        return 0
    for lo, hi, m in ((1, 40, NARR), (41, 147, LAW), (251, 275, LAW | WISDOM), (291, 299, LAW),
                      (300, 339, NARR | CULT), (370, 389, CULT), (390, 500, CULT)):
        if lo <= cth <= hi:
            return m
    return 0


def _by_name(table, name: str) -> int:
    m = 0
    for cls, keys in table:
        if any(k in name for k in keys):
            m |= cls
    return m


class Classifier:
    """Genre-class mask of a unit (0: not in the comparable layers). Reads the GLAUx metadata and the
    TLHdig directory names (CTH numbers) as text."""

    def __init__(self, root: Path | None = ROOT, meta: dict | None = None):
        self.meta = meta or {}
        self.glaux, self.cth = {}, {}
        if root is None:            # tests: tables filled in by hand
            return
        with open(root / GLAUX_META, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                self.glaux[r["TLG"]] = r
        for d in (root / HIT_DIR).iterdir():
            m = re.match(r"CTH (\d+)", d.name)
            if m and d.is_dir():
                for fn in d.glob("*.xml"):
                    self.cth.setdefault(fn.stem, int(m[1]))

    def glaux_class(self, tlg: str) -> int:
        r = self.glaux.get(tlg)
        if not r:
            return 0
        try:
            end = int(r["ENDDATE"])
        except ValueError:
            return 0
        if end > GLAUX_MAX_END:
            return 0
        m = GLAUX_GENRE.get(r["GENRE_STANDARD"], 0)
        if m and tlg.startswith("0020-002"):          # Hesiod, Works and Days
            m |= WISDOM
        if m and tlg.startswith("0013-"):             # Homeric Hymns
            m |= CULT
        return m

    def __call__(self, c: str, u) -> int:
        book = str(u.book)
        if c in C.CELTIC:
            md = self.meta.get(u.key.split("~w")[0]) or {}
            if md.get("date_from") is None:
                return 0
            mid = (md["date_from"] + (md.get("date_to") or md["date_from"])) / 2
            return CELTIC_GENRE.get(md.get("genre"), 0) if mid <= CELTIC_MAX_MID else 0
        if c == "menota":           # whole ids, except the two prefix families (AM 132 fol sagas, AM 162 B Njála)
            if book in MENOTA_LAW:
                return LAW
            return NARR if book in MENOTA_NARR or book.startswith(MENOTA_PREFIX) else 0
        if c == "icepahc":
            if ".law-" in book:
                return LAW
            return NARR if ".nar-" in book and "alexander" not in book else 0
        if c == "rea-goh":
            return _by_name(REA_GOH, book.split("/")[-1]) if book.startswith("Kleinere_") else 0
        if c == "rea-osx":
            return _by_name(REA_OSX, book.split("/")[-1]) if book.startswith("Kleinere_") else 0
        if c == "vuk":
            return NARR | LYR
        if c == "byliny":
            return NARR
        if c in ("dainos",):
            return LYR
        if c == "xcl":
            return NARR if any(k in book for k in XCL_NARR) else 0
        if c in ("xto", "sqo", "ccmh", "grc-late", "sga"):
            return 0
        if c == "rv":
            return CULT | NARR
        if c == "av":
            return CULT
        if c == "ae":
            if book in ("V", "VS", "VSY"):
                return LAW | CULT
            return CULT | NARR if book.startswith(("Yt", "Vyt", "DrYt")) else CULT
        if c == "hom":
            return NARR
        if c == "grc":
            return self.glaux_class(book)
        if c == "sa-ep":
            return WISDOM | LAW if book.startswith(("MBh, 12,", "MBh, 13,")) else NARR
        if c == "hit":
            return hittite_class(self.cth.get(book))
        if c == "non":
            return 0 if re.match(r"S[óo]larlj", book) else NARR | WISDOM
        if c == "ang":
            return next((cls for cls, names in ANG if book in names), 0)
        if c == "lat":
            if book.startswith("LucrDRN"):
                return WISDOM
            return LAT.get(book, 0)
        if c == "xum":
            return CULT
        if c == "lv":
            return LYR | CULT
        if c == "orv":
            return ORV.get(book, 0)
        return 0


def hittite_paragraph_texts(root: Path = ROOT) -> dict:
    """Paragraph key (as load_hittite's 'para': 'tablet|n') → the displayed text of every Hittite-language word in
    it, unlemmatized words included, cut at `parsep` even inside a line (load_hittite's segmentation)."""
    from pie import formula_search_multi as fm
    out: dict = collections.defaultdict(list)
    for fn in sorted((root / fm.HIT_DIR).glob("*/*.xml")):
        body = fn.read_text("utf-8", errors="replace").split("<body>", 1)[-1]
        cur, para = None, 0
        for piece in re.split(r"(<lb [^>]*>|<parsep[^>]*>)", body):
            if piece.startswith("<lb "):
                m = fm._HIT_LB.search(piece)
                lg = re.search(r'lg="([^"]*)"', piece)
                cur = (m[1], m[2]) if m and (not lg or lg[1] == "Hit") else None
                continue
            if piece.startswith("<parsep"):
                para += 1
                continue
            if not cur:
                continue
            for wm in fm._HIT_W.finditer(piece):
                attrs = wm[1]
                end = piece.find("</w>", wm.end())
                inner = "" if attrs.endswith("/") or end < 0 else piece[wm.end():end]
                disp = B._hit_w_text(inner)
                if disp:
                    out[f"{fn.stem}|{para}"].append(disp)
    return {k: " ".join(v) for k, v in out.items()}


def hittite_paragraph_units(root: Path = ROOT, by_id: dict | None = None) -> list:
    """Hittite units at paragraph level (TLHdig `parsep` to `parsep`, windowed like every long unit) instead of
    Stage B's tablet lines: a line is too short to share two roots with anything (Stage C-S, thin-corpus rule)."""
    from pie import formula_search as fs
    from pie import formula_search_multi as fm
    toks = fm.load_hittite(root)
    _, hsurf = B._hit_lines(fm, root)
    assert len(hsurf) == len(toks)
    text_of = hittite_paragraph_texts(root)
    hl, hro = SB.CORPORA["hit"][2], SB.CORPORA["hit"][3]
    from pie import hittite_mapping as hm
    table = hm.read_union_table(root, doubtful=True)      # thin-corpus rule: the doubtful tier, retrieval only
    us = SB.units_from_tokens("hit", toks, "para", lambda t: t.units["line"].split("|")[0], hsurf,
                              table, lambda t: (hl, hro), text_of=text_of)
    lex = fs.load_jsonl(root / "data/lexicon/lexicon.jsonl")
    gmap = fs.group_map(lex)
    for u in us:
        u.groups = frozenset(gmap.get(x, x) for _, _, ids in u.words for x in ids)
        u.tag = C.licence_tag(u.licence)
    return us


ALL = NARR | CULT | LAW | WISDOM | LYR


def loose_class(c: str, u, clf: Classifier) -> int:
    """Thin corpora (amendment): the whole native corpus, genre waived (ALL), less translations of foreign
    texts: Hittite CTH 340-369 (Hurrian and Mesopotamian adaptations), the Old English Psalms."""
    book = str(u.book)
    if c == "hit":
        cth = clf.cth.get(book)
        return 0 if cth is None or 340 <= cth <= 369 else ALL
    if c == "ang":                  # the Paris Psalter (Psalmen; OCR'd psalm numbers) and the editor's apparatus
        if re.search(r"Psalm|P S A L M|Notizen|Vorwort|Verbesserungen|Terbesserfngen|Tokwort|Grein|Wigand", book):
            return 0
        if re.fullmatch(r"II:[A-Za-z.,]{1,8}", book) and book not in ("II:Juliana", "II:Kunenlied", "II:Pbauibit"):
            return 0
        return ALL
    return ALL


def thin_corpora(idx) -> frozenset:
    cnt = collections.Counter(c for c, _ in idx.ref)
    return frozenset(c for c, n in cnt.items() if 0 < n < THIN_MAX_UNITS and c not in PIVOTS)


def prepare(units: dict, by_id: dict, meta: dict, cache_dir=None, log=print, root: Path = ROOT):
    """Hittite paragraph units, the main classification, the thin corpora (by the main rule's indexed units),
    and the loosened classification of the thin corpora. Returns (cls, thin)."""
    units["hit"] = C._cached(cache_dir, "hit-para", lambda: hittite_paragraph_units(root))
    B.assign_pids(units)
    clf = Classifier(root, meta)
    cls = classify(units, clf)
    thin = thin_corpora(SIndex(indexed_view(units, cls), by_id, cls))
    log("thin corpora: " + ", ".join(sorted(thin)))
    for c in thin:
        cls[c] = [loose_class(c, u, clf) for u in units[c]]
    return cls, thin


def classify(units: dict, clf: Classifier) -> dict:
    """corpus → list of class masks, parallel to units[corpus]."""
    return {c: [clf(c, u) for u in us] for c, us in units.items()}


class _Gone:
    """A left-out unit as the index sees it: no content words, so it is not indexed."""
    words = ()


def indexed_view(units: dict, cls: dict) -> dict:
    return {c: [u if m else _Gone() for u, m in zip(us, cls[c])] for c, us in units.items()}


# ---------------------------------------------------------------- stratified index

class SIndex(SB.Index):
    """Stage B's index over the kept units, with a genre-class mask per indexed unit; partners share a class
    with the pivot, at most CORPUS_CAP per corpus."""

    def __init__(self, view: dict, by_id: dict, cls: dict, shuffle_seed=None):
        super().__init__(view, by_id, shuffle_seed=shuffle_seed)
        self.cls = np.array([cls[c][i] for c, i in self.ref], dtype=np.int16)
        self.corp = [c for c, _ in self.ref]
        self.set_thin(frozenset())

    def partners(self, u: int, top_k: int | None = None, min_shared: int | None = None) -> list[tuple]:
        top_k = top_k or SB.TOP_K
        min_shared = min_shared or SB.MIN_SHARED
        b = self.branch[u]
        rare = [g for g in self.ugids[u] if g >= self.n_common]
        if not rare or not self.cls[u]:
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
        ok = (cnt >= min_shared) & ((self.cls[uniq] & self.cls[u]) != 0)
        if not ok.any():
            return []
        uniq, sc = uniq[ok], sc[ok]
        order = np.lexsort((uniq, -np.round(sc, 9)))
        # rescore the CAND_K best by the fast score; if the per-corpus cap then leaves slots empty, keep rescoring
        # further candidates (up to CAND_MAX) so that one corpus filling the first CAND_K cannot crowd out others
        scored, out = [], []
        for n_done, k in enumerate(order[:CAND_MAX]):
            if n_done >= SB.CAND_K and len(out) >= top_k:
                break
            v = int(uniq[k])
            s, gs = self.match(u, v)
            if len(gs) >= min_shared and any(g >= self.n_common for g in gs):
                scored.append((round(s, 6), v, len(gs)))
            if n_done + 1 >= SB.CAND_K:
                out = self._capped(scored, top_k)
        return self._capped(scored, top_k)

    def _capped(self, scored: list, top_k: int) -> list:
        out, per = [], collections.Counter()
        for s, v, n in sorted(scored, key=lambda x: (-x[0], x[1])):
            if per[self.corp[v]] >= CORPUS_CAP:
                continue
            per[self.corp[v]] += 1
            out.append((s, v, n))
            if len(out) == top_k:
                break
        return out


    def set_thin(self, thin: frozenset) -> None:
        self.thin = thin
        self.thin_mask = np.array([c in thin for c in self.corp], dtype=bool)

    def thin_partners(self, u: int, slots: int | None = None) -> list[tuple]:
        """The best partner from each thin corpus (genre class waived; other branch; >= MIN_SHARED matched roots,
        one outside the n_common most frequent), the top `slots` of them by score."""
        slots = slots or THIN_SLOTS
        b = self.branch[u]
        rare = [g for g in self.ugids[u] if g >= self.n_common]
        if not rare or not self.cls[u] or not getattr(self, "thin", None):
            return []
        cand_parts = []
        for g in rare:
            p, bd = self.post[g], self.bounds[g]
            for seg in (p[:bd[b]], p[bd[b + 1]:]):
                if len(seg):
                    seg = seg[self.thin_mask[seg]]
                    if len(seg):
                        cand_parts.append(seg)
        if not cand_parts:
            return []
        uniq = np.unique(np.concatenate(cand_parts))
        best: dict = {}
        for v in uniq:
            v = int(v)
            s, gs = self.match(u, v)
            s = round(s, 6)                 # compare at the stored precision (ties: lower uid)
            if len(gs) >= SB.MIN_SHARED and any(g >= self.n_common for g in gs):
                c = self.corp[v]
                if c not in best or (-s, v) < (-best[c][0], best[c][1]):
                    best[c] = (s, v, len(gs))
        return sorted(best.values(), key=lambda x: (-x[0], x[1]))[:slots]


def decoy_partner(idx: SIndex, pivot: int, real: int, exclude: set, rng: random.Random, pools: dict) -> int | None:
    """Stage B's decoy rule, drawn from the units of the real partner's corpus that share a class with the pivot."""
    c = idx.ref[real][0]
    pool = pools[c]
    pool = pool[(idx.cls[pool] & idx.cls[pivot]) != 0]
    if not len(pool):
        return None
    return SB.decoy_partner(idx, pivot, real, exclude, rng, {c: pool})


def build_bundles(idx: SIndex, kept: dict, cap: int | None = None) -> list[dict]:
    """Stage B's merge rule (SB.build_bundles), except that a merged-in partner joins only if it shares a class
    with the bundle's pivot (the class rule holds for every partner of a bundle)."""
    cap = cap or SB.MERGE_CAP
    order = sorted(kept, key=lambda u: (-kept[u][0][0], u))
    bundles: list[dict] = []
    where: dict = collections.defaultdict(set)
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
            if v not in b["units"] and idx.cls[v] & idx.cls[b["pivot"]]:
                b["units"].append(v)
                b["scores"][v] = s
                where[v].add(hit)
    return bundles


_IDX = None


def _work(us):
    return [(u, _IDX.partners(u), _IDX.thin_partners(u)) for u in us]


def all_partners(idx: SIndex, pivots: list[int], procs: int | None = None, chunk: int = 1000):
    """(regular partners, thin partners) by pivot uid, for the given pivots (parallel, fork)."""
    global _IDX
    _IDX = idx
    chunks = [pivots[k:k + chunk] for k in range(0, len(pivots), chunk)]
    if procs == 1 or len(pivots) < 5000:
        res = [_work(c) for c in chunks]
    else:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(procs or max(1, mp.cpu_count() - 2)) as pool:
            res = pool.map(_work, chunks)
    reg = {u: p for part in res for u, p, _ in part if p}
    thin = {u: t for part in res for u, _, t in part if t}
    return reg, thin


def kept_partners(reg: dict, thin: dict, floor: float, thin_floor: float) -> dict:
    """Regular partners >= floor and thin partners >= thin_floor (not already among the regular ones), by score."""
    out = {}
    for u in set(reg) | set(thin):
        k = [p for p in reg.get(u, ()) if p[0] >= floor]
        have = {v for _, v, _ in k}
        k += [p for p in thin.get(u, ()) if p[0] >= thin_floor and p[1] not in have]
        if k:
            out[u] = sorted(k, key=lambda x: (-x[0], x[1]))
    return out


# ---------------------------------------------------------------- build

FLOOR_RULE = (f"floor = the {SB.FLOOR_Q} quantile of the best-partner score over all Stage C-S pivots that have a "
              "partner (Stage B's size rule); a pivot keeps its top-k partners scoring >= floor")
LAYER_RULE = ("indexed units: each tradition's earliest, least derivative layer per genre "
              "(docs/research/8c-preregistration.md, Stage C-S table; scripts/build_8c_stageCS.py Classifier); "
              "idf over the indexed units only")


THIN_RULE = ("thin corpora: partner-only corpora with < THIN_MAX_UNITS indexed units under the main rule; layer "
             "loosened to the whole native corpus, genre waived; Hittite unit = paragraph; up to THIN_SLOTS thin "
             "partners per pivot (best per thin corpus) from a separate search; thin floor = the FLOOR_Q quantile of "
             "the pivots' best thin-partner scores (amendment of 2026-10-24)")


def make_params(idx, parts, null, notes=None, thin_parts=None) -> dict:
    p = C.make_params(idx, parts, SB.score_distribution(parts), null, PIVOTS, notes)
    if thin_parts:
        tb = np.array([t[0][0] for t in thin_parts.values()])
        p.update({"thin_floor": SB._q(tb, SB.FLOOR_Q), "thin_rule": THIN_RULE, "thin_max_units": THIN_MAX_UNITS,
                  "thin_slots": THIN_SLOTS, "thin_corpora": sorted(getattr(idx, "thin", ())),
                  "thin_best_quantiles": {str(q): SB._q(tb, q) for q in (0.5, 0.75, 0.9, 0.95)},
                  "pivots_with_thin_partner": len(thin_parts)})
    p.update({
        "note": "Phase 8c Stage C-S retrieval and bundle parameters, fixed from the score distribution before any "
                "bundle was built or read (docs/research/8c-preregistration.md, Stage C-S).",
        "floor_rule": FLOOR_RULE, "layer_rule": LAYER_RULE,
        "class_rule": "a partner shares at least one genre class (NARR, CULT, LAW, WISDOM, LYR) with its pivot",
        "corpus_cap": CORPUS_CAP,
        "decoy_rule": "Stage B's decoy rule within the real partner's corpus, from indexed units sharing a class "
                      "with the pivot",
        "seed_strings": {"decoys": f"{SEED_TAG}:{SEED}:decoys", "ids": f"{SEED_TAG}:{SEED}:ids"},
    })
    return p


def make_slab(sid, bis, shown, bid_of, rend, idx) -> dict:
    s = C.make_slab(sid, bis, shown, bid_of, rend, idx)
    s["header"] = HEADER
    return s


def build(units, by_id, cls, params: dict, procs=None, log=print, parts=None, meta=None, seed: int = SEED,
          thin: frozenset = frozenset()) -> dict:
    meta = meta or {}
    view = indexed_view(units, cls)
    idx = SIndex(view, by_id, cls)
    idx.set_thin(thin)
    pivots = C.pivots_of(idx, PIVOTS)
    log(f"index: {idx.N} units with roots, {len(idx.groups)} root groups, {len(pivots)} Stage C-S pivots")
    reg, tparts = parts if parts is not None else all_partners(idx, pivots, procs)
    floor = params["floor"]
    kept = kept_partners(reg, tparts, floor, params.get("thin_floor", float("inf")))
    parts = reg
    bundles = build_bundles(idx, kept)
    for b in bundles:
        assert idx.ref[b["pivot"]][0] in PIVOTS
        assert all(idx.cls[v] & idx.cls[b["pivot"]] for v in b["units"][1:])
    log(f"floor {floor}: {len(kept)} pivots, {len(bundles)} bundles")
    rend = C.Renderer(units, by_id, idx)
    rng = random.Random(f"{SEED_TAG}:{seed}:decoys")
    pools = {c: np.array([k for k, (c2, _) in enumerate(idx.ref) if c2 == c], dtype=np.int32) for c in units}
    pools = {c: p for c, p in pools.items() if len(p)}
    decoy: dict = {}
    order = SB.doc_order(idx, bundles)
    step = round(1 / SB.DECOY_SHARE)
    drawn = [rng.choice(order[k:k + step]) for k in range(0, len(order), step)
             if len(order[k:k + step]) == step or rng.random() < len(order[k:k + step]) / step]
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
    slab_bis = SB.pack_slabs(idx, bundles, rend, shown)
    ids_rng = random.Random(f"{SEED_TAG}:{seed}:ids")
    sids = SB._ids("SS", 4, len(slab_bis), ids_rng)
    bids = SB._ids("BS", 5, len(bundles), ids_rng)
    perm = list(range(len(bundles)))
    ids_rng.shuffle(perm)
    bid_of = {bi: bids[perm[bi]] for bi in range(len(bundles))}
    slabs, key = {}, {"note": "Phase 8c Stage C-S blinding key: bundle kind, real partners and decoy replacements, "
                              "pivot corpus, genre classes and (Celtic) witness metadata.", "slabs": {}}
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
                "pivot_group": "celtic" if c in C.CELTIC else "other",
                "pivot_classes": class_names(int(idx.cls[b["pivot"]])),
                "pivot_meta": meta.get(pu.key.split("~w")[0], {}),
                "pivot_mapped_share": round(C.mapped_share(pu), 3),
                "real_partners": [{"id": rend.passage(v)["id"], "corpus": idx.ref[v][0],
                                   "classes": class_names(int(idx.cls[v])),
                                   "score_vs_pivot": round(idx.match(b["pivot"], v)[0], 4),
                                   "shared": [idx.groups[g] for g in idx.shared(b["pivot"], v)]}
                                  for v in b["units"][1:]],
                **({"decoy_partners": [rend.passage(decoy[bi][v])["id"] for v in b["units"][1:]]}
                   if bi in decoy else {}),
                "merged": b["merged"]}
        key["slabs"][sid] = ent
    stats = C.make_stats(units, idx, parts, kept, bundles, slabs, slab_bis, decoy, rend, pivots, PIVOTS, meta)
    stats["decoy_target"] = len(drawn)
    stats["thin_partner_slots"] = dict(collections.Counter(
        idx.corp[v] for b in bundles for v in b["units"][1:] if idx.thin_mask[v]))
    stats["layers"] = layer_report(units, cls)
    stats["bundles_by_pivot_class"] = dict(collections.Counter(
        "+".join(class_names(int(idx.cls[b["pivot"]]))) for b in bundles))
    return {"params": params, "slabs": slabs, "key": key, "stats": stats, "bundles": bundles, "decoy": decoy,
            "idx": idx, "parts": parts,
            "assignment": {"note": "Phase 8c Stage C-S: one reader per slab (Stage B capacity).",
                           "slabs": {sid: f"RS{k + 1:03d}" for k, sid in enumerate(sids)}}}


def layer_report(units: dict, cls: dict) -> dict:
    out = {}
    for c, us in units.items():
        kept = collections.Counter()
        gone = 0
        for m in cls[c]:
            if m:
                kept["+".join(class_names(m))] += 1
            else:
                gone += 1
        out[c] = {"units": len(us), "kept": sum(kept.values()), "left_out": gone, "kept_by_classes": dict(kept)}
    return out


def write(res: dict, out_dir: Path = OUT, key_path: Path = KEY) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    for sub in ("slabs", "slabs-loci"):
        d = out_dir / sub
        d.mkdir(exist_ok=True)
        for old in d.glob("SS-*.json"):
            old.unlink()
    for sid, s in res["slabs"].items():
        text = SB.dump_slab(s)
        assert json.loads(text) == s
        (out_dir / "slabs" / f"{sid}.json").write_text(text, "utf-8")
        (out_dir / "slabs-loci" / f"{sid}.json").write_text(SB.dump_slab(C.loci_only(s)), "utf-8")
    (out_dir / "assignment.json").write_text(dump(res["assignment"]), "utf-8")
    (out_dir / "stats.json").write_text(dump(res["stats"]), "utf-8")
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(dump(res["key"]), "utf-8")


def dry_run(units, cls, log) -> None:
    for c, us in units.items():
        docs = collections.defaultdict(lambda: [0, 0])
        for u, m in zip(us, cls[c]):
            docs[str(u.book)][0 if m else 1] += 1
        k = sum(v[0] for v in docs.values())
        print(f"## {c}: kept {k} / {len(us)}")
        if c in ("menota", "icepahc", "rea-goh", "rea-osx", "ang", "lat", "orv", "xcl", "non", "ae"):
            for d, (a, g) in sorted(docs.items()):
                if a:
                    print(f"   + {d}: {a}")
        if c == "grc":
            tl = collections.Counter(str(u.book) for u, m in zip(us, cls[c]) if m)
            print("   kept TLG works:", len(tl), sorted(tl))
        if c == "hit":
            print("   kept by class:", dict(collections.Counter("+".join(class_names(m)) for m in cls[c] if m)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", type=Path)
    ap.add_argument("--procs", type=int, default=None)
    ap.add_argument("--refreeze", action="store_true", help="recompute params.json (only before any slab is read)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    log = lambda *a: print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)
    units, by_id, meta, notes = C.load_all(ROOT, args.cache_dir, None, False, None, log)
    cls, thin = prepare(units, by_id, meta, args.cache_dir, log)
    rep = layer_report(units, cls)
    log("kept: " + ", ".join(f"{c} {r['kept']}/{r['units']}" for c, r in rep.items()))
    if args.dry_run:
        dry_run(units, cls, log)
        return 0
    pfile = OUT / "params.json"
    params = None if args.refreeze or not pfile.exists() else json.loads(pfile.read_text("utf-8"))
    view = indexed_view(units, cls)
    parts = None
    if params is None:      # freeze the floor before any bundle is built
        idx = SIndex(view, by_id, cls)
        idx.set_thin(thin)
        pv = C.pivots_of(idx, PIVOTS)
        reg, tparts = all_partners(idx, pv, args.procs)
        parts = (reg, tparts)
        log(f"partners: {len(reg)} of {len(pv)} pivots; thin partners: {len(tparts)}")
        nidx = SIndex(view, by_id, cls, shuffle_seed=SEED)
        nparts = C.pivot_partners(nidx, C.pivots_of(nidx, PIVOTS), args.procs)
        best = np.array([p[0][0] for p in reg.values()])
        floors = sorted({SB._q(best, q) for q in (0.5, 0.75, 0.9, 0.95, 0.98, 0.99)})
        params = make_params(idx, reg, SB.null_comparison(idx, reg, nidx, nparts, floors), notes, thin_parts=tparts)
        OUT.mkdir(parents=True, exist_ok=True)
        pfile.write_text(json.dumps(params, ensure_ascii=False, indent=1) + "\n", "utf-8")
        log(f"params frozen: floor {params['floor']}, thin floor {params.get('thin_floor')}")
        del nidx, nparts, idx
    res = build(units, by_id, cls, params, args.procs, log, parts=parts, meta=meta, thin=thin)
    res["stats"]["mapping_notes"] = notes
    write(res)
    st = res["stats"]
    log(f"bundles {st['bundles']}, decoys {st['decoy_bundles']} ({st['decoy_share']}), slabs {st['slabs']}, "
        f"slab tokens {st['total_slab_tokens']}, read est. {st['read_tokens_est']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
