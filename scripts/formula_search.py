#!/usr/bin/env python3
"""Formula discovery (Phase 8a): run the cross-corpus co-occurrence search.

  uv run python -I scripts/formula_search.py tune       # half A only
  uv run python -I scripts/formula_search.py evaluate   # frozen settings, half B once

`tune` maps both corpora, scores every setting in the grid, picks the
best on half A of the known formulas and freezes it in
data/research/formulas/tuning.json. It never computes a half-B number.
`evaluate` reads the frozen settings and writes, under
data/research/formulas/:
  evaluation.json      coverage, recall@k on half B (and A), the shuffled
                       baseline, and a per-formula decomposition
  candidates.jsonl     top 200 pairs not among the known formulas, with
                       example loci (verse/line and the lemma pair) and
                       the syntactic relation in each corpus
"""

import argparse
import collections
import itertools
import json
import statistics
import sys
import time
from pathlib import Path

from pie import formula_search as fs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "research" / "formulas"
KS = (50, 100, 200)
PRIMARY = ("phrase", "lexical")
EXTENDED = ("phrase", "lexical", "attested", "schema")
GRID = {
    "specs": [(r, h) for r in ("pada", "stanza", "win3", "win5") for h in ("line", "sentence", "win3", "win5")],
    "measure": ["llr", "pmi", "npmi"],
    "min_count": [1, 2, 3, 5],
    "content_only": [True, False],
    "llr_min": [3.84, 10.83],
    "max_share": [1.0, 0.02],
}
DEFAULT = {"rv_spec": "pada", "hom_spec": "line", "measure": "llr", "min_count": 3, "content_only": True,
           "llr_min": 10.83, "max_share": 1.0}
SHUFFLE_SEEDS = (0, 1, 2, 3, 4)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def setup():
    t = time.time()
    lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
    rv, hom = fs.load_rv(ROOT), fs.load_homer(ROOT)
    rvm, homm = fs.build_rv_mapping(lex, rv), fs.build_homer_mapping(lex, hom)
    formulas = fs.load_jsonl(ROOT / "data/formulas/formulas.jsonl")
    lem = fs.Lemmatizer(rv, hom, rvm, homm, lex)
    idx = fs.pie_index(lex)
    gold = {"primary": fs.gold_set(formulas, lem, idx, PRIMARY), "extended": fs.gold_set(formulas, lem, idx, EXTENDED)}
    gold["known"] = fs.known_pairs(formulas, lem, idx)
    log(f"loaded {len(rv)} RV / {len(hom)} Homer tokens in {time.time() - t:.0f}s")
    return lex, rv, hom, rvm, homm, gold


def counts_for(rv, hom, rvm, homm, content_only, specs, cache):
    for t, m in ((rv, rvm), (hom, homm)):
        fs.apply_mapping(t, m, content_only)
    for r, h in specs:
        for toks, spec in ((rv, r), (hom, h)):
            key = (toks[0].corpus, spec, content_only)
            if key not in cache:
                cache[key] = fs.corpus_counts(toks, spec)
    return cache


def rank(cache, cfg):
    a = cache[("rv", cfg["rv_spec"], cfg["content_only"])]
    b = cache[("hom", cfg["hom_spec"], cfg["content_only"])]
    return fs.score_pairs(a, b, cfg["measure"], cfg["min_count"], cfg["llr_min"], cfg["max_share"])


def half(gold, h):
    return [g for g in gold if g["half"] == h]


def objective(rec):
    return statistics.mean(rec[f"recall@{k}"] or 0 for k in KS)


def tune(args) -> int:
    lex, rv, hom, rvm, homm, gold = setup()
    gold.pop("known")
    gA = {k: half(v, "A") for k, v in gold.items()}
    cache = {}
    for co in GRID["content_only"]:
        counts_for(rv, hom, rvm, homm, co, GRID["specs"], cache)
    rows = []
    for (r, h), meas, mc, co, lm, ms in itertools.product(GRID["specs"], GRID["measure"], GRID["min_count"],
                                                          GRID["content_only"], GRID["llr_min"], GRID["max_share"]):
        cfg = {"rv_spec": r, "hom_spec": h, "measure": meas, "min_count": mc, "content_only": co, "llr_min": lm,
               "max_share": ms}
        ranking = rank(cache, cfg)
        recs = {k: fs.recall(ranking, v) for k, v in gA.items()}
        rows.append({"settings": cfg, "n_candidates": len(ranking),
                     "A": {k: {kk: vv for kk, vv in rec.items() if kk != "ranks"} for k, rec in recs.items()},
                     "objective": round(objective(recs["primary"]) + objective(recs["extended"]), 4),
                     "distance_from_default": sum(cfg[k] != DEFAULT[k] for k in DEFAULT)})
    rows.sort(key=lambda x: (-x["objective"], x["distance_from_default"]))
    best = rows[0]
    best_rank = rank(cache, best["settings"])
    ranksA = {k: fs.recall(best_rank, v)["ranks"] for k, v in gA.items()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tuning.json").write_text(json.dumps({
        "note": "Tuned on half A of the known formulas only (sha1(formula_id) first byte even). "
                "Objective: mean recall@50/100/200 on the primary set plus the same on the extended set; "
                "ties go to the setting closest to the pre-registered default.",
        "grid": {k: v for k, v in GRID.items()}, "default": DEFAULT,
        "frozen": best["settings"], "best": best, "half_A_ranks": ranksA,
        "n_half_A": {k: len(v) for k, v in gA.items()},
        "top_settings": rows[:25], "default_row": next(r for r in rows if r["settings"] == DEFAULT),
    }, ensure_ascii=False, indent=1) + "\n", "utf-8")
    log(f"{len(rows)} settings; half A n={ {k: len(v) for k, v in gA.items()} }")
    for r in rows[:10]:
        log(f"  {r['objective']:.3f} {r['settings']} cands={r['n_candidates']} A={r['A']}")
    log(f"frozen: {best['settings']}")
    return 0


def describe(g, by_id):
    e = by_id.get(g)
    return {"id": g, "pie": e["form"] if e else None, "meaning": (e.get("meaning") or [None])[0] if e else None}


def evaluate(args) -> int:
    tuning = json.loads((OUT / "tuning.json").read_text("utf-8"))
    cfg = tuning["frozen"]
    lex, rv, hom, rvm, homm, gold = setup()
    known = gold.pop("known")
    by_id = {e["id"]: e for e in lex}
    cache = counts_for(rv, hom, rvm, homm, cfg["content_only"], [(cfg["rv_spec"], cfg["hom_spec"])], {})
    ranking = rank(cache, cfg)
    res = {k: {h: fs.recall(ranking, half(v, h)) for h in ("A", "B")} for k, v in gold.items()}

    # shuffled baseline: root sets permuted across positions, unit structure kept
    shuf = {k: {h: [] for h in ("A", "B")} for k in gold}
    shuf_n = []
    for seed in SHUFFLE_SEEDS:
        c = {}
        srv, shom = fs.shuffled(rv, seed), fs.shuffled(hom, seed + 100)
        c[("rv", cfg["rv_spec"], cfg["content_only"])] = fs.corpus_counts(srv, cfg["rv_spec"])
        c[("hom", cfg["hom_spec"], cfg["content_only"])] = fs.corpus_counts(shom, cfg["hom_spec"])
        sr = rank(c, cfg)
        shuf_n.append(len(sr))
        for k, v in gold.items():
            for h in ("A", "B"):
                shuf[k][h].append(fs.recall(sr, half(v, h)))
    shuffled = {k: {h: {f"recall@{kk}": round(statistics.mean(r[f"recall@{kk}"] or 0 for r in rs), 3) for kk in KS}
                    for h, rs in hv.items()} for k, hv in shuf.items()}

    # per-formula decomposition (both halves)
    a = cache[("rv", cfg["rv_spec"], cfg["content_only"])]
    b = cache[("hom", cfg["hom_spec"], cfg["content_only"])]
    rank_of = {r["pair"]: i + 1 for i, r in enumerate(ranking)}
    decomp = []
    for g in gold["extended"]:
        rows = []
        for p in g["pairs"]:
            x, y = p
            row = {"pair": [describe(x, by_id)["pie"] or x, describe(y, by_id)["pie"] or y],
                   "in_rv": [a.single[x] > 0, a.single[y] > 0], "in_hom": [b.single[x] > 0, b.single[y] > 0],
                   "rv_n": a.pair[p], "hom_n": b.pair[p],
                   "rv_llr": round(fs.llr(a.pair[p], a.single[x], a.single[y], a.n), 2) if a.single[x] and a.single[y] else None,
                   "hom_llr": round(fs.llr(b.pair[p], b.single[x], b.single[y], b.n), 2) if b.single[x] and b.single[y] else None,
                   "rank": rank_of.get(p)}
            rows.append(row)
        decomp.append({"formula_id": g["formula_id"], "half": g["half"], "kind": g["kind"],
                       "primary": g["kind"] in PRIMARY, "pairs": rows})

    # candidates: top 200 not among any known formula's pairs (all kinds, both halves). Pairs passing the
    # frozen criteria come first; the list is filled to 200 with pairs positively associated (count ≥ 2) in both.
    sig = [dict(r, tier="significant") for r in ranking if r["pair"] not in known]
    seen = {r["pair"] for r in ranking}
    weak = [dict(r, tier="below_threshold") for r in fs.score_pairs(a, b, cfg["measure"], 2, 0.0, cfg["max_share"])
            if r["pair"] not in known and r["pair"] not in seen]
    top = (sig + weak)[:200]
    want = {r["pair"] for r in top}
    ex_rv = fs.instances(rv, cfg["rv_spec"], want)
    ex_hom = fs.instances(hom, cfg["hom_spec"], want)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "candidates.jsonl").open("w", encoding="utf-8") as fh:
        for i, r in enumerate(top, 1):
            p = r["pair"]
            er, eh = ex_rv[p], ex_hom[p]
            rec = {"rank": i, "tier": r["tier"], "pair": [describe(p[0], by_id), describe(p[1], by_id)],
                   "score": round(r["score"], 3), "measure": cfg["measure"],
                   "rv": {k: round(v, 3) if isinstance(v, float) else v for k, v in r["rv"].items()},
                   "hom": {k: round(v, 3) if isinstance(v, float) else v for k, v in r["hom"].items()},
                   "rv_relations": dict(er["relations"]), "hom_relations": dict(eh["relations"]),
                   "hom_dependency_linked": eh["dep_linked"],
                   "parallel_relation": fs.parallel_relation(er["relations"], eh["relations"]),
                   "rv_examples": er["examples"], "hom_examples": eh["examples"],
                   "status": "unreviewed"}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    leak = {}
    for k in ("primary", "extended"):
        a_pairs = {p for g in half(gold[k], "A") for p in g["pairs"]}
        leak[k] = sorted(g["formula_id"] for g in half(gold[k], "B") if set(g["pairs"]) & a_pairs)

    def strip(rr):
        return {k: v for k, v in rr.items() if k != "ranks"}
    (OUT / "evaluation.json").write_text(json.dumps({
        "settings": cfg,
        "coverage": {"rigveda": fs.coverage(rv, rvm), "homer": fs.coverage(hom, homm)},
        "n_candidates_significant_in_both": len(ranking),
        "recall": {k: {h: strip(rr) for h, rr in v.items()} for k, v in res.items()},
        "ranks": {k: {h: rr["ranks"] for h, rr in v.items()} for k, v in res.items()},
        "shuffled_baseline": {"seeds": list(SHUFFLE_SEEDS), "n_candidates": shuf_n, "recall_mean": shuffled},
        "eval_sets": {k: {h: len(half(v, h)) for h in ("A", "B")} for k, v in gold.items()},
        "half_B_formulas_sharing_a_gold_pair_with_half_A": leak,
        "candidates_written": {"significant": sum(r["tier"] == "significant" for r in top),
                               "below_threshold": sum(r["tier"] == "below_threshold" for r in top)},
        "decomposition": decomp,
        "notes": ["primary = kinds phrase+lexical (the acceptance set); extended adds West 'attested' and "
                  "Watkins 'schema' records with Vedic and Greek attestations.",
                  "Half A was used for tuning; half B is reported once with the frozen settings.",
                  "A formula counts as recovered at k if any of its gold pairs ranks ≤ k."],
    }, ensure_ascii=False, indent=1) + "\n", "utf-8")
    for k, v in res.items():
        for h, rr in v.items():
            log(f"{k} half {h}: {strip(rr)}   shuffled: {shuffled[k][h]}")
    log(f"candidates significant in both: {len(ranking)}; wrote {len(top)} candidates")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["tune", "evaluate"])
    args = ap.parse_args()
    return tune(args) if args.stage == "tune" else evaluate(args)


if __name__ == "__main__":
    sys.exit(main())
