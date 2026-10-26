"""Celtic lemma → PIE tables for Phase 8c Stage C (pie/celtic_mapping.py).

Writes data/research/formulas/mapping/{celt,sga-glosses,cy}.jsonl (format of
the round-3 tables: corpus, lang, lemma, word, lex_id, path, how, confidence,
sources) and data/research/formulas/celtic-coverage.json (content-token
coverage per source and period). With --sample N --seed S it also writes the
token-weighted precision sample to the given path (lemma, tokens, row).

Each table holds (a) every mapped headword key of the language (so the table
serves any Irish / Welsh text through the same lemmatizer) and (b) every
lemma string the lemmatizer produced on the corpora ('a|b' unions included).
The mapping overrides (data/research/formulas/mapping-overrides/celtic.json)
are applied as for the other tables.

    uv run python scripts/build_celtic_mapping.py [--sample-dir DIR --seed 7]
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pie import celtic_mapping as cm  # noqa: E402
from pie import formula_search as fs  # noqa: E402
from pie import formula_search_multi as fm  # noqa: E402

MAPPING_DIR = ROOT / "data/research/formulas/mapping"
COVERAGE = ROOT / "data/research/formulas/celtic-coverage.json"
PRECEDENCE_LOG = ROOT / "data/research/formulas/celtic-precision/systematic-rules-log.json"
KD = ROOT / "raw/daughters"

# Irish OCR editions (round 4): path globs under raw/daughters
IRISH_OCR = {
    "felire-stokes-1905": "oldirish-felire-oengusso-stokes-1905/*_djvu.txt",
    "tbc-windisch-1905": "oldirish-tbc-windisch-1905/*_djvu.txt",
    "irische-texte": "oldirish-irische-texte-1880-1909/*_djvu.txt",
    "ancient-laws": "oldirish-ancient-laws-ireland-1865-1901/*_djvu.txt",
    "meyer-editions": "oldirish-meyer-editions-1892-1919/*_djvu.txt",
    "saltair-stokes-1883": "middleirish-saltair-na-rann-stokes-1883/*_djvu.txt",
    "tripartite-stokes-1887": "oldirish-tripartite-life-stokes-1887/*_djvu.txt",
    "lismore-stokes-1890": "middleirish-lismore-lives-stokes-1890/*_djvu.txt",
    "eriu-1904-1928": "celtic-journal-eriu-1904-1928/*_djvu.txt",
    "zcp-1897-1926": "celtic-journal-zcp-1897-1926/*_djvu.txt",
    "archiv-celt-lex": "celtic-archiv-celt-lexikographie-1898-1907/*_djvu.txt",
}
# Welsh editions: (glob, diplomatic OCR repair)
WELSH_OCR = {
    "skene-four-ancient-books-v2": ("welsh-skene-four-ancient-books/fourancientbooks02skenuoft_djvu.txt", False),
    "myvyrian-1870": ("welsh-myvyrian-archaiology-1870/*_djvu.txt", False),
    "gododin-gutenberg": ("welsh-gododin-gutenberg-9842/pg9842.txt", False),
    "ancient-laws-owen-1841": ("welsh-ancient-laws-owen-1841/*_djvu.txt", False),
    "redbook-mabinogion-1887": ("welsh-redbook-mabinogion-rhys-evans-1887/*_djvu.txt", True),
    "white-book-1907": ("welsh-white-book-mabinogion-evans-1907/*_djvu.txt", True),
    "redbook-bruts-1890": ("welsh-redbook-bruts-rhys-evans-1890/*_djvu.txt", True),
    "redbook-poetry-1911": ("welsh-redbook-poetry-evans-1911/*_djvu.txt", True),
    "book-of-taliesin-1910": ("welsh-book-of-taliesin-evans-1910/*_djvu.txt", True),
    "black-book-1906": ("welsh-black-book-carmarthen-evans-1906/*_djvu.txt", True),
    "book-of-aneirin-1908": ("welsh-book-of-aneirin-evans-1908/*_djvu.txt", True),
}

# line-level language vote for the OCR editions (coverage only; the Stage C
# builder does its own separation). Function words, not the lemmatizer, decide.
IR_FUNC = set("""in ind int inna na a ocus acus ⁊ is ro ra do di de dia fo for co cona la le i isin isind
 ní nír nach ar iar ria oc ac ag os ós .i. ba bá robo ina conid dano didiu tra immorro sin so se sain sund
 hi hí é é a an ón uad uaid leis dó dí dóib dun dúinn frit fri ri re mo do ar far bar nach nad ce cia cid
 ol amal cach cech gach nech ním dó lais leo lat aca acu ann and ann sin sein""".split())
CY_FUNC = set("""y yr ar a ac o i yn e ef hi wy wynt eu ei oed oedd mi ti ni na ny nyt nid pan gan can yg ym
 hyt dros rac wedy gwedy heb ae am val mal megys hwnn hwnnw hon hynny hyny honno yno yna sef neu no nac
 pob pawb dy vy fy yw ydiw ydoed oll yssyd sydd ual hyd tra""".split())
FOREIGN = set("""the and of to that which with his he was were is be by from this as it on at an are not
 for or but they her him their had have has been also see read text ms mss note notes line lines page
 der die das und ist nicht mit von zu den dem des ein eine sich auf auch wie aus im zum zur bei nach
 le la les et des que est une un du dans pour qui par sur pas au aux ce il
 ad cum quod non est sed ut enim autem vel quia sunt eius per ab ex qui quae""".split())


def foreign_share(words):
    return sum(w.lower() in FOREIGN for w in words) / max(1, len(words))


def ocr_lines(paths, func, min_words=4, max_foreign=0.05, min_func=0.12):
    """(edition line number, words) for lines that vote Irish/Welsh."""
    for p in paths:
        for i, line in enumerate(p.read_text("utf-8", errors="replace").splitlines()):
            ws = cm.irish_words(line)
            if len(ws) < min_words:
                continue
            low = [w.lower() for w in ws]
            if foreign_share(ws) > max_foreign:
                continue
            if sum(w in func for w in low) / len(low) < min_func:
                continue
            yield f"{p.name}:{i + 1}", ws


# ---------------------------------------------------------------- mapping a lemma string

class TableMapper:
    """Lemma string ('a', 'a|b', '?x', or a gloss lemma) → MapRec through a
    merged LangMapping; parts that disagree on root groups → None."""

    def __init__(self, lm: fm.LangMapping, gmap: dict, corpus: str, overrides: dict | None = None):
        self.lm, self.gmap, self.corpus, self.K = lm, gmap, corpus, fm.KEYS[lm.lang]
        # lemma overrides apply to the parts of a union too ('fír|fer' sees the corrected fír)
        overrides = overrides if overrides is not None else fm.load_overrides(ROOT)
        self.ov = overrides["lemma"].get(corpus, {})
        self.recs = cm.apply_base_overrides(lm.recs, corpus, overrides)
        self.loose = collections.defaultdict(set)
        for k in self.recs:
            self.loose[self.K(k, True)].add(k)
        self.memo = {}

    def part(self, p: str):
        if p in self.ov:
            ids, row = self.ov[p]
            if not ids:
                return None
            return fm.MapRec(p, p, ids, (f"{self.corpus}:{p}", "erratum:" + (row.get("note") or "")), "erratum",
                             "high", ("mapping-overrides",))
        if any(k in self.lm.recs and k not in self.recs for k in (p, self.K(p))):
            return None  # a reviewed base removal must not fall back to a loose homograph
        r = self.recs.get(p) or self.recs.get(self.K(p))
        if r:
            return r
        ks = self.loose.get(self.K(p, True), set())
        if len(ks) == 1:
            return self.recs[next(iter(ks))]
        if ks:
            g = {frozenset(self.gmap.get(x, x) for x in self.recs[k].ids) for k in ks}
            if len(g) == 1:
                return self.recs[sorted(ks)[0]]
        return None

    def __call__(self, lem: str):
        if lem in self.memo:
            return self.memo[lem]
        out = None
        if lem and not lem.startswith("?"):
            parts = lem.split("|")
            hits = [self.part(p) for p in parts]
            # every candidate that is a dictionary headword must be mapped, and all must agree: a form that
            # may also be an unmapped word (MW benn 'cart' / soft-mutated penn 'head') stays unmapped; an
            # unmapped candidate that is only an inflected form, or an article fusion (ymab = y + mab), is ignored
            blocking = [p for p, h in zip(parts, hits) if h is None and p in self.lm.lemma_words
                        and not (p[:1] == "y" and (p[1:] in parts or p[2:] in parts))]
            hits = [h for h in hits if h]
            if hits and not blocking:
                gs = {frozenset(self.gmap.get(x, x) for x in h.ids) for h in hits}
                ids = frozenset().union(*(h.ids for h in hits))
                g = frozenset(self.gmap.get(x, x) for x in ids)
                if len(gs) == 1 and len(g) <= fs.MAX_GROUPS:
                    h = hits[0]
                    if len(parts) == 1 and (h.key == lem):
                        out = h
                    else:
                        out = fm.MapRec(lem, "|".join(x.word for x in hits), ids, h.path, h.how,
                                        h.confidence if len(parts) == 1 else "low",
                                        h.sources + (("form-ambiguous",) if len(parts) > 1 else ()), h.gloss)
        self.memo[lem] = out
        return out


# ---------------------------------------------------------------- corpora

def celt_tokens(lemz, path=KD / "celt-ucc/units.jsonl"):
    """CELT units → (unit id, period, genre, source, surface, lemma, position)."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            ws = cm.irish_words(d["text"])
            # context rules (cm.CONTEXT_FORMS: tig after a preposition / article → tech 'house')
            for i, (w, lem) in enumerate(zip(ws, cm.lemmatize_words(lemz, ws))):
                yield d["id"], d["lang"], d["genre"], d["source"], w, lem, i


def is_name(surface: str, pos: int) -> bool:
    return pos > 0 and surface[:1].isupper()


is_function_lemma = cm.is_function_lemma
content_of = cm.content_of


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--no-ocr", action="store_true", help="skip the Irish/Welsh OCR editions (faster)")
    a = ap.parse_args(argv)
    t0 = time.time()
    maps = cm.build_mappings(ROOT)
    lex = maps.lexicon
    gmap = fs.group_map(lex)
    ov = fm.load_overrides(ROOT)
    print(f"mappings: irish {len(maps.irish.recs)} keys, welsh {len(maps.welsh.recs)} keys ({time.time() - t0:.0f}s)")
    ilz = cm.irish_lemmatizer(maps)
    cov = {}
    counts = {"celt": collections.Counter(), "sga-glosses": collections.Counter(), "cy": collections.Counter()}
    lemma_strings = {"celt": set(), "sga-glosses": set(), "cy": set()}
    mappers = {"celt": TableMapper(maps.irish, gmap, "celt"), "sga-glosses": TableMapper(maps.irish, gmap, "sga-glosses"),
               "cy": TableMapper(maps.welsh, gmap, "cy")}
    ovr = {c: ov["lemma"].get(c, {}) for c in mappers}

    def mapped(c, lem):
        if is_function_lemma(mappers[c].lm, lem):
            return False
        if lem in ovr[c]:
            return bool(ovr[c][lem][0])
        r = mappers[c](lem)
        return bool(r and fm._strip_blocked(r.ids))

    def tally(c, key, lem, surface, pos, extra=(), lemz=None):
        if not content_of(mappers[c].lm, lem, surface, lemz):
            return
        m = mapped(c, lem)
        nm = is_name(surface, pos)
        for k in (key,) + tuple(extra):
            d = cov.setdefault(c, {}).setdefault(k, collections.Counter())
            d["content"] += 1
            d["content_mapped"] += m
            if not nm:
                d["content_no_names"] += 1
                d["content_no_names_mapped"] += m
        counts[c][(surface.lower(), lem)] += 1

    # CELT
    lvl = collections.Counter()
    lic_of = collections.defaultdict(set)          # CELT lemma string → licence tags of the sources attesting it
    for uid, period, genre, src, w, lem, i in celt_tokens(ilz):
        lemma_strings["celt"].add(lem)
        lic = cm.celt_licence(src)
        lic_of[lem].add(lic)
        tally("celt", f"period:{period}", lem, w, i, (f"genre:{genre}", f"licence:{lic}", "all"), ilz)
    for s, l in ilz.level.items():
        lvl[l] += 1
    cov["celt-lemmatizer-levels-by-type"] = dict(lvl)
    print(f"celt done ({time.time() - t0:.0f}s)")
    # glosses: tagged tokens by their lemma, untagged by the lemmatizer
    for t in cm.gloss_tokens(ROOT):
        if t.lemma:
            lem = t.lemma
            if t.upos not in cm.CONTENT_UPOS:
                continue
            key = f"{t.source}-tagged"
        else:
            lem = ilz(t.form)
            key = f"{t.source}-untagged"
        lemma_strings["sga-glosses"].add(lem)
        if t.lemma:
            d = cov.setdefault("sga-glosses", {})
            m = mapped("sga-glosses", lem)
            for k in (key, "all", "tagged"):
                x = d.setdefault(k, collections.Counter())
                x["content"] += 1
                x["content_mapped"] += m
                if t.upos != "PROPN":
                    x["content_no_names"] += 1
                    x["content_no_names_mapped"] += m
            counts["sga-glosses"][("=" + lem, lem)] += 1
        else:
            tally("sga-glosses", key, lem, t.form, 1, ("all",), ilz)
    print(f"glosses done ({time.time() - t0:.0f}s)")
    if not a.no_ocr:
        for ed, pat in IRISH_OCR.items():
            paths = sorted(KD.glob(pat))
            for loc, ws in ocr_lines(paths, IR_FUNC):
                for i, (w, lem) in enumerate(zip(ws, cm.lemmatize_words(ilz, ws))):
                    lemma_strings["celt"].add(lem)
                    if not content_of(maps.irish, lem, w, ilz):
                        continue
                    m = mapped("celt", lem)
                    d = cov.setdefault("irish-ocr", {}).setdefault(ed, collections.Counter())
                    d["content"] += 1
                    d["content_mapped"] += m
                    if not is_name(w, i):
                        d["content_no_names"] += 1
                        d["content_no_names_mapped"] += m
        print(f"irish ocr done ({time.time() - t0:.0f}s)")
    lzs = {False: cm.welsh_lemmatizer(maps, False), True: cm.welsh_lemmatizer(maps, True)}
    for ed, (pat, dipl) in WELSH_OCR.items():
        paths = sorted(KD.glob(pat))
        lz = lzs[dipl]
        for loc, ws in ocr_lines(paths, CY_FUNC):
            for i, w in enumerate(ws):
                lem = lz(w)
                lemma_strings["cy"].add(lem)
                tally("cy", ed, lem, w, i, ("diplomatic" if dipl else "print-normalised", "all"), lz)
    print(f"welsh done ({time.time() - t0:.0f}s)")
    # tables
    for c, lm in (("celt", maps.irish), ("sga-glosses", maps.irish), ("cy", maps.welsh)):
        recs = {}
        for k in lm.recs:
            r = mappers[c](k)
            if r:
                recs[k] = r
        for lem in lemma_strings[c]:
            r = mappers[c](lem)
            if r:
                recs[lem] = r
        # no rows for function words (articles, prepositions, conjunctions, copula: cm.IR_FUNCTION /
        # CY_FUNCTION): they are not content words
        recs = {k: r for k, r in recs.items() if not is_function_lemma(lm, k)}
        recs = fm.apply_rec_overrides(c, recs, root=ROOT)
        rows = []
        for lem in sorted(recs):
            r = recs[lem]
            ids = fm._strip_blocked(sorted(r.ids))
            if not ids:
                continue
            lang = r.path[0].split(":", 1)[0] if r.path and ":" in r.path[0] else lm.lang
            row = {"corpus": c, "lang": lang, "lemma": lem, "word": r.word, "lex_id": list(ids),
                   "path": list(r.path), "how": r.how, "confidence": r.confidence, "sources": list(r.sources)}
            if c == "celt":
                # licence tags of the CELT sources in which this lemma string occurs ([] = dictionary headword or
                # OCR-edition form only): 'research' (G400001–G400058, OUP notice) / 'consent-train'
                row["celt_licence"] = sorted(lic_of.get(lem, ()))
            rows.append(row)
        (MAPPING_DIR / f"{c}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
        print(f"{c}: {len(rows)} rows")
    out = {}
    for c, d in cov.items():
        if not isinstance(d, dict) or not all(isinstance(v, collections.Counter) for v in d.values()):
            out[c] = d
            continue
        out[c] = {}
        for k, x in sorted(d.items()):
            out[c][k] = dict(x)
            out[c][k]["share"] = round(x["content_mapped"] / max(1, x["content"]), 4)
            out[c][k]["share_no_names"] = round(x["content_no_names_mapped"] / max(1, x["content_no_names"]), 4)
    COVERAGE.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", "utf-8")
    # rows changed by the systematic rules (Matasović precedence, its chain propagation, preverb-only drops,
    # the do·ucai / do·uccai stem split): headword keys and ids only
    PRECEDENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
    PRECEDENCE_LOG.write_text(json.dumps(maps.precedence, ensure_ascii=False, indent=1, sort_keys=True) + "\n", "utf-8")
    if a.sample_dir:
        a.sample_dir.mkdir(parents=True, exist_ok=True)
        for c in counts:
            table = {}
            for line in (MAPPING_DIR / f"{c}.jsonl").read_text("utf-8").splitlines():
                r = json.loads(line)
                table[r["lemma"]] = r
            # a type is what the corpus looks up: the surface form (lowercased) for unlemmatized text,
            # the corpus lemma ('=' + lemma) for the tagged gloss tokens; weighted by its content tokens
            types = sorted(t for t in counts[c] if mapped(c, t[1]))
            w = [counts[c][t] for t in types]
            rng = random.Random(a.seed)
            got, seen = [], set()
            while len(got) < min(a.n, len(types)):
                x = rng.choices(types, w)[0]
                if x in seen:
                    continue
                seen.add(x)
                ovrow = ovr[c].get(x[1])
                got.append({"type": x[0], "lemma": x[1], "tokens": counts[c][x],
                            "row": table.get(x[1]) or {"override": ovrow[1] if ovrow else None}})
            tot = sum(counts[c].values())
            print(f"  {c}: content types {len(counts[c])}, mapped types {len(types)}")
            (a.sample_dir / f"celtmap-sample-{c}-seed{a.seed}.jsonl").write_text(
                "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in got), "utf-8")
            print(f"sample {c}: {len(got)} of {len(types)} mapped types ({tot} content tokens)")
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
