"""Balto-Slavic lemma → PIE tables for Phase 8c Stage C (pie/bsl_mapping.py).

Writes data/research/formulas/mapping/{vuk,byliny,dainos,ccmh}.jsonl (format of the round-3 tables:
corpus, lang, lemma, word, lex_id, path, how, confidence, sources; plus `tokens`, the lemma string's
content-token count in the corpus, `licence`, {source edition: licence} for the editions in which it
occurs, and `mapping_licence`, the licence of the mapping evidence) and
data/research/formulas/bsl-coverage.json (content-token coverage per corpus and source edition).
With --sample-dir DIR --seed S it also writes the token-weighted precision sample (100 mapped
(surface, lemma) types per corpus) with a judging aid (kaikki and lexicon glosses, path, Derksen
entries that list the word).

Each table holds (a) every lemma string the lemmatizer produced on the corpus that maps (unions
'a|b' included) and (b) every other mapped headword key of the language, so that the Stage C
builder can lemmatize the same editions (or others) with bsl_mapping.lemmatizer and look the result
up with bsl_mapping.read_table. The overrides (data/research/formulas/mapping-overrides/, here
balto-slavic-new.json) are applied before writing; read_table applies them again (idempotent).

    uv run python scripts/build_bsl_mapping.py [--sample-dir DIR --seed 7]
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pie import bsl_mapping as bm  # noqa: E402
from pie import formula_search as fs  # noqa: E402
from pie import formula_search_multi as fm  # noqa: E402
from pie import mapping  # noqa: E402

MAPPING_DIR = ROOT / bm.MAPPING_DIR
COVERAGE = ROOT / "data/research/formulas/bsl-coverage.json"
CORPORA = ("vuk", "byliny", "dainos", "ccmh")


class Mapper:
    """lemma string → MapRec after the overrides (lemma rows of the corpus code)."""

    def __init__(self, lm: fm.LangMapping, gmap: dict, corpus: str, ov: dict):
        self.lm, self.gmap, self.corpus = lm, gmap, corpus
        self.ov = ov["lemma"].get(corpus, {})
        self.cache: dict = {}

    def __call__(self, lem: str) -> fm.MapRec | None:
        if lem in self.cache:
            return self.cache[lem]
        if lem in self.ov:
            ids, row = self.ov[lem]
            r = None
            if ids:
                old = bm.map_lemma(lem, self.lm, self.gmap)
                r = fm.MapRec(lem, old.word if old else lem, ids, (f"{self.corpus}:{lem}", "erratum:" + row.get("note", "")),
                              "erratum", "high", ("mapping-overrides",))
        else:
            r = bm.map_lemma(lem, self.lm, self.gmap)
            if r:
                ids = frozenset(fm._strip_blocked(r.ids))
                r = fm.MapRec(r.key, r.word, ids, r.path, r.how, r.confidence, r.sources, r.gloss) if ids else None
        self.cache[lem] = r
        return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--corpora", default=",".join(CORPORA))
    a = ap.parse_args(argv)
    which = a.corpora.split(",")
    t0 = time.time()
    maps = bm.build_mappings(ROOT)
    ocs = bm.ocs_mapping(maps, ROOT)
    fz = fm.FuzzyPie(maps.lexicon)
    didx = bm.derksen_index(ROOT)
    n_dk = bm.add_derksen_lt(maps.lt, didx, fz)
    print(f"mappings built ({time.time() - t0:.0f}s); Derksen EDBIL additions: {n_dk}")
    mapping._OVR_CACHE.clear()
    ov = fm.load_overrides(ROOT)
    lms = {"vuk": maps.sh, "byliny": maps.ru, "dainos": maps.lt, "ccmh": ocs}
    cov, samples = {}, {}
    for c in which:
        lm = lms[c]
        lz = bm.lemmatizer(c, maps, ocs)
        mp = Mapper(lm, maps.gmap, c, ov)
        counts: collections.Counter = collections.Counter()       # (surface, lemma) → content tokens
        lem_tok: collections.Counter = collections.Counter()
        lem_src: dict = collections.defaultdict(set)
        d = collections.defaultdict(collections.Counter)
        for loc, u, text in bm.UNITS[c](ROOT):
            src = u["source"]
            for i, w in enumerate(bm.corpus_words(c, text)):
                lem = lz(w)
                lem_src[lem].add(src)
                d[src]["tokens"] += 1
                d["all"]["tokens"] += 1
                if not lm.is_content(lem) or (lem.startswith("?") and len(lem) < 3):
                    continue
                nm = bm.is_name(c, w, i)
                r = None if nm else mp(lem)          # names are not mapped (bm.is_name)
                for k in (src, "all"):
                    d[k]["content"] += 1
                    d[k]["content_mapped"] += bool(r)
                    d[k]["unknown"] += lem.startswith("?")
                    if not nm:
                        d[k]["content_no_names"] += 1
                        d[k]["content_no_names_mapped"] += bool(r)
                if not nm:
                    counts[(w.lower(), lem)] += 1
                lem_tok[lem] += 1
        lv = collections.Counter(lz.level.values())
        cov[c] = {k: dict(x, share=round(x["content_mapped"] / max(1, x["content"]), 4),
                          share_no_names=round(x["content_no_names_mapped"] / max(1, x["content_no_names"]), 4))
                  for k, x in sorted(d.items())}
        cov[c]["lemmatizer_levels_by_type"] = dict(lv)
        # table
        recs = {}
        for lem in lem_tok:
            r = mp(lem)
            if r:
                recs[lem] = r
        for k in lm.recs:
            if k not in recs and lm.is_content(k):
                r = mp(k)
                if r:
                    recs[k] = r
        for lem, (ids, row) in mp.ov.items():
            if ids and lem not in recs:
                recs[lem] = mp(lem)
        rows = []
        lic = bm.SOURCES[c]
        for lem in sorted(recs):
            r = recs[lem]
            how = r.how.split("-")[0] if r.how.startswith("chain-") else r.how
            rows.append({"corpus": c, "lang": bm.CORPUS_LANG[c], "lemma": lem, "word": r.word, "lex_id": sorted(r.ids),
                         "path": list(r.path), "how": r.how, "confidence": r.confidence, "sources": list(r.sources),
                         "tokens": lem_tok.get(lem, 0),
                         "licence": {s: lic[s] for s in sorted(lem_src.get(lem, ())) if s in lic},
                         "mapping_licence": bm.MAPPING_LICENCE.get(how, bm.MAPPING_LICENCE["chain"])})
        (MAPPING_DIR / f"{c}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
        print(f"{c}: {len(rows)} rows; content coverage {cov[c]['all']['share']:.3f} "
              f"(no names {cov[c]['all']['share_no_names']:.3f}) ({time.time() - t0:.0f}s)")
        if a.sample_dir:
            types = sorted(t for t in counts if mp(t[1]))
            w = [counts[t] for t in types]
            rng = random.Random(a.seed)
            got, seen = [], set()
            while len(got) < min(a.n, len(types)):
                x = rng.choices(types, w)[0]
                if x in seen:
                    continue
                seen.add(x)
                got.append(x)
            gl = collections.defaultdict(list)
            K = fm.KEYS[bm.CORPUS_LANG[c]]
            for e in maps.entries.get(bm.CORPUS_LANG[c], []):
                if not e.form_of and e.glosses:
                    gl[K(e.word)].append(f"{e.pos}: {e.glosses[:80]}")
            samples[c] = [judging_row(c, s, lem, counts[(s, lem)], mp(lem), lm, maps, didx, gl) for s, lem in got]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1, sort_keys=True) + "\n", "utf-8")
    if a.sample_dir:
        a.sample_dir.mkdir(parents=True, exist_ok=True)
        for c, rows in samples.items():
            (a.sample_dir / f"mapbsl-sample-{c}-seed{a.seed}.jsonl").write_text(
                "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
    return 0


def judging_row(c, surface, lem, n, r, lm, maps, didx, gl):
    lexg = {e["id"]: (e.get("form"), (e.get("meaning") or "")[:60]) for e in maps.lexicon if e["id"] in r.ids}
    lang = bm.CORPUS_LANG[c]
    dk = []
    for part in lem.split("|"):
        for e in didx.get(lang, {}).get(bm.latin_key(part), [])[:3]:
            dk.append(f"{e['dict']} p{e['page']} {e['head']} PIE {bm.derksen_pie(e['pie'])[:40]}"
                      + (f" LOAN: {e['loan'][:40]}" if e.get("loan") else ""))
    return {"surface": surface, "lemma": lem, "tokens": n, "lex_id": sorted(r.ids), "lexicon": lexg,
            "path": list(r.path), "how": r.how,
            "kaikki_gloss": " / ".join(g for p in lem.split("|") for g in gl.get(p, [])[:2])[:240], "derksen": dk[:4]}


if __name__ == "__main__":
    sys.exit(main())
