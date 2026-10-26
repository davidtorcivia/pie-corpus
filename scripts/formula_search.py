#!/usr/bin/env python3
"""Formula discovery (Phase 8a), round 2: ablation over mapping, scoring,
syntax and a third witness, evaluated by 5-fold cross-validation on a
fixed evaluation set.

  uv run python -I scripts/formula_search.py ablation     # evaluation.json
  uv run python -I scripts/formula_search.py candidates   # candidates.jsonl (final method)
  uv run python -I scripts/formula_search.py all
  uv run python -I scripts/formula_search.py mapping      # round-3 mapping tables only (after new errata)

Evaluation set (built once per mapping version, then frozen for every row):
  gold    data/formulas/formulas.jsonl records attested in Vedic and Greek
          (all kinds), their pairs as in round 1
  silver  pairs West cites as a Vedic phrase and a Greek phrase in one
          paragraph (pie.formula_search.build_silver; refs only, no text)
Items are gold formulas and silver pairs, merged when they share a pair;
folds are sha1(smallest pair) mod 5. For every row, each fold's setting is
chosen on the other four folds (objective: mean recall@50/100/200), and the
held-out ranks are pooled. CIs: 2,000 bootstrap resamples of items. The
shuffled baseline reruns each fold's chosen setting on corpora whose PIE
labels are permuted across positions (5 seeds).

Round 1's outputs are kept in evaluation_round1.json / tuning_round1.json.
"""

import argparse
import collections
import math
import os
import itertools
import json
import statistics
import sys
import time
from pathlib import Path

from pie import formula_search as fs
from pie import formula_search_multi as fm
from pie import hittite_mapping as hm

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("FORMULA_SEARCH_OUT") or ROOT / "data" / "research" / "formulas")
KS = (50, 100, 200)
GOLD_KINDS = ("phrase", "lexical", "attested", "schema")
PRIMARY = ("phrase", "lexical")
SHUFFLE_SEEDS = (0, 1, 2, 3, 4)
ROUND1 = {"scorer": "llr", "map": "r1", "level": "group", "content_only": False, "rv_spec": "pada",
          "hom_spec": "line", "measure": "llr", "min_count": 3, "llr_min": 3.84}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- environment

class Env:
    def __init__(self):
        t = time.time()
        self.lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
        self.by_id = {e["id"]: e for e in self.lex}
        self.gmap = fs.group_map(self.lex)
        self.tok = {"rv": fs.load_rv(ROOT), "hom": fs.load_homer(ROOT), "lat": fs.load_latin(ROOT)}
        rv, hom, lat = self.tok["rv"], self.tok["hom"], self.tok["lat"]
        r1 = {"rv": fs.build_rv_mapping(self.lex, rv), "hom": fs.build_homer_mapping(self.lex, hom),
              "lat": fs.build_latin_mapping(self.lex, lat)}
        lang = {"rv": "sa", "hom": "grc", "lat": "la"}
        self.maps = {"r1": r1,
                     "kaikki": {c: fs.build_kaikki_mapping(lang[c], self.lex, self.tok[c], r1[c]) for c in r1},
                     "pseudo": {c: fs.build_kaikki_mapping(lang[c], self.lex, self.tok[c], r1[c], pseudo=True)
                                for c in r1}}
        self.formulas = fs.load_jsonl(ROOT / "data/formulas/formulas.jsonl")
        self.pie_idx = fs.pie_index(self.lex)
        self.extra_v = fs.kaikki_word_groups("sa", self.lex, True)
        self.extra_g = fs.kaikki_word_groups("grc", self.lex, True)
        self.cache: dict = {}
        self.applied: dict = {}
        self.shuf = (None, None)
        log(f"loaded corpora and mappings in {time.time() - t:.0f}s")

    def lemmatizer(self, mapname: str) -> fs.Lemmatizer:
        m = self.maps[mapname]
        extra = (self.extra_v, self.extra_g) if mapname != "r1" else ()
        return fs.Lemmatizer(self.tok["rv"], self.tok["hom"], m["rv"], m["hom"], self.lex, *extra)

    def project(self, p):
        a, b = self.gmap.get(p[0], p[0]), self.gmap.get(p[1], p[1])
        return None if a == b else ((a, b) if a < b else (b, a))

    # ---- counts
    def tokens(self, corpus, mapname, level, content_only, seed):
        """The corpus with roots set for this mapping (in place); a shuffled
        copy for a seed (one copy kept at a time: counts are cached instead)."""
        state = (mapname, level, content_only)
        if self.applied.get(corpus) != state:
            fs.apply_mapping(self.tok[corpus], self.maps[mapname][corpus], content_only, level)
            self.applied[corpus] = state
        if seed is None:
            return self.tok[corpus]
        key = (corpus, state, seed)
        if self.shuf[0] != key:
            self.shuf = (key, fs.shuffled(self.tok[corpus], seed + {"rv": 0, "hom": 100, "lat": 200}[corpus]))
        return self.shuf[1]

    def counts(self, corpus, mapname, level, content_only, spec, seed=None):
        key = ("cnt", corpus, mapname, level, content_only, spec, seed)
        if key not in self.cache:
            toks = self.tokens(corpus, mapname, level, content_only, seed)
            if spec == "dep":
                c = fs.count_edges(toks, fs.dep_edges(toks))
            elif spec.startswith("adj"):
                c = fs.count_edges(toks, fs.adjacency_edges(toks, "pada", int(spec[3:])))
            else:
                c = fs.corpus_counts(toks, spec)
            self.cache[key] = c
        return self.cache[key]

    def relations(self, corpus, mapname, level, content_only, link, seed=None):
        key = ("rel", corpus, mapname, level, content_only, link, seed)
        if key not in self.cache:
            toks = self.tokens(corpus, mapname, level, content_only, seed)
            edges = fs.dep_edges(toks) if link == "dep" else fs.adjacency_edges(toks, "pada", int(link[3:]))
            self.cache[key] = fs.edge_relations(toks, edges)
        return self.cache[key]

    # ---- ranking
    def rank(self, cfg: dict, seed=None) -> list[tuple]:
        """Distinct root-group pairs, best first (top 1000 cached)."""
        key = ("rank", json.dumps(cfg, sort_keys=True), seed)
        if key not in self.cache:
            full = self.rank_full(cfg, seed)
            self.cache[key] = [r["group_pair"] for r in full[:1000]]
            self.cache[("n", key)] = len(full)
        return self.cache[key]

    def n_ranked(self, cfg: dict) -> int:
        self.rank(cfg)
        return self.cache[("n", ("rank", json.dumps(cfg, sort_keys=True), None))]

    def rank_full(self, cfg: dict, seed=None) -> list[dict]:
        m, lv, co = cfg["map"], cfg["level"], cfg["content_only"]
        syn = cfg.get("syn", "none")
        rv_spec, hom_spec = cfg["rv_spec"], cfg["hom_spec"]
        if syn == "filter-linked":
            rv_spec, hom_spec = cfg["rv_link"], "dep"
        a = self.counts("rv", m, lv, co, rv_spec, seed)
        b = self.counts("hom", m, lv, co, hom_spec, seed)
        if cfg["scorer"] == "llr":
            ranking = fs.score_pairs(a, b, cfg.get("measure", "llr"), cfg["min_count"], cfg["llr_min"])
        else:
            bonus = keep = None
            if syn in ("bonus-linked", "bonus-rel", "filter-rel"):
                ra = self.relations("rv", m, lv, co, cfg["rv_link"], seed)
                rb = self.relations("hom", m, lv, co, "dep", seed)
                if syn == "bonus-linked":
                    hit = ra.keys() & rb.keys()
                else:
                    hit = {p for p in ra.keys() & rb.keys()
                           if (d := fs.dominant_relation(ra[p])) and d == fs.dominant_relation(rb[p])}
                if syn == "filter-rel":
                    keep = hit.__contains__
                else:
                    bonus = {p: cfg["syn_b"] for p in hit}
            third = None
            if cfg.get("third_mode", "none") != "none":
                third = self.counts("lat", m, lv, co, cfg["lat_spec"], seed)
            ranking = fs.score_exact([a, b], cfg["min_count"], cfg["rank_by"], cfg.get("midp", False),
                                     max_logp=cfg.get("max_logp", 0.0), third=third,
                                     third_mode=cfg.get("third_mode", "none"), bonus=bonus, keep=keep,
                                     floor=cfg.get("floor"))
        out, seen = [], set()
        for r in ranking:
            p = self.project(r["pair"])
            if p is None or p in seen:
                continue
            seen.add(p)
            out.append({**r, "group_pair": p})
        return out


# ---------------------------------------------------------------- evaluation sets

def build_eval(env: Env, mapname: str) -> dict:
    lem = env.lemmatizer(mapname)
    gold = fs.gold_set(env.formulas, lem, env.pie_idx, GOLD_KINDS)
    silver, mentions = fs.build_silver(fs.west_passages(ROOT), lem.vedic, lem.greek)
    items = fs.eval_items(gold, silver)
    kinds = {g["formula_id"]: g["kind"] for g in gold}
    for it in items:
        it["primary"] = any(kinds[f] in PRIMARY for f in it["gold"])
    gold_pairs = {tuple(p) for g in gold for p in g["pairs"]}
    return {"map": mapname, "items": items, "gold": gold, "silver": silver, "mentions": mentions,
            "lemmatizer": lem, "summary": {
                "n_items": len(items), "n_gold_formulas": len(gold),
                "n_gold_primary_formulas": sum(kinds[g["formula_id"]] in PRIMARY for g in gold),
                "n_gold_pairs": len(gold_pairs), "n_silver_pairs": len(silver),
                "n_silver_pairs_not_in_gold": len(set(silver) - gold_pairs),
                "n_items_with_silver_only": sum(1 for it in items if not it["gold"]),
                "n_items_primary": sum(it["primary"] for it in items),
                "items_per_fold": dict(sorted(collections.Counter(it["fold"] for it in items).items()))}}


# ---------------------------------------------------------------- grids (one per ablation row)

def grid(base: dict, **axes) -> list[dict]:
    keys = list(axes)
    return [{**base, **dict(zip(keys, vals))} for vals in itertools.product(*(axes[k] for k in keys))]


ALPHA_EACH = round(math.log(0.05), 6)     # 'significant in each corpus' (p < 0.05) option
SPECS = [("pada", "line"), ("stanza", "sentence"), ("pada", "sentence"), ("win3", "win3")]


def llr_grid(mapname, level="group"):
    base = {"scorer": "llr", "map": mapname, "level": level, "measure": "llr"}
    out = []
    for (r, h) in SPECS:
        out += grid({**base, "rv_spec": r, "hom_spec": h}, min_count=[1, 2, 3], llr_min=[3.84, 10.83],
                    content_only=[False, True])
    return out


def exact_grid(mapname, levels=("group",), **extra):
    base = {"scorer": "exact", "map": mapname}
    out = []
    for (r, h) in SPECS:
        out += grid({**base, "rv_spec": r, "hom_spec": h, **extra}, level=list(levels), min_count=[1, 2],
                    rank_by=["fisher", "max"], midp=[False, True], floor=[None, -10.0], content_only=[False, True],
                    max_logp=[0.0, ALPHA_EACH])
    return out


def rows(best_exact: dict | None = None, best_syntax: dict | None = None) -> list[tuple]:
    """(name, description, settings grid, default) per ablation row."""
    r1d = dict(ROUND1)
    rws = [
        ("r1_frozen", "round-1 method and frozen setting (old mapping; LLR ≥ 3.84 and ≥ 3 co-occurrences in each corpus)",
         [r1d], r1d),
        ("r1_tuned", "round-1 method (old mapping, LLR), setting tuned by CV", llr_grid("r1"), r1d),
        ("map_kaikki", "+ kaikki etymology links (lexicon etyma only), LLR", llr_grid("kaikki"), {**r1d, "map": "kaikki"}),
        ("map_kaikki_pseudo", "+ kaikki links incl. etyma missing from the lexicon, LLR", llr_grid("pseudo"),
         {**r1d, "map": "pseudo"}),
        ("map_lexeme", "kaikki+pseudo, counted at lexeme level (evaluated on root groups), LLR",
         llr_grid("pseudo", "lexeme"), {**r1d, "map": "pseudo", "level": "lexeme"}),
    ]
    return rws


def exact_rows(mapname: str, levels) -> list[tuple]:
    d = {"scorer": "exact", "map": mapname, "level": levels[0], "rv_spec": "pada", "hom_spec": "line",
         "min_count": 1, "rank_by": "fisher", "midp": False, "floor": None, "content_only": False, "max_logp": 0.0}
    return [("exact", f"+ exact per-corpus tests (hypergeometric / Poisson) combined by Fisher; map={mapname}",
             exact_grid(mapname, levels), d)]


def syntax_rows(b: dict) -> list[tuple]:
    """Variants on top of a fixed exact setting family b (specs and levels
    from the exact row's choice; the other knobs re-tuned)."""
    base = {k: b[k] for k in ("scorer", "map", "level", "rv_spec", "hom_spec")}
    knobs = dict(min_count=[1, 2], rank_by=["fisher", "max"], floor=[None, -10.0], content_only=[False, True],
                 max_logp=[0.0, ALPHA_EACH])
    return [
        ("syn_filter_linked", "count only syntactically linked co-occurrences (Homer head–dependent; RV adjacency in the pāda)",
         grid({**base, "syn": "filter-linked", "midp": True}, rv_link=["adj1", "adj2"], **knobs), None),
        ("syn_bonus_linked", "bonus (10^b) for pairs linked at least once in both corpora",
         grid({**base, "syn": "bonus-linked", "midp": True}, rv_link=["adj1", "adj2"], syn_b=[1.0, 3.0, 10.0], **knobs), None),
        ("syn_bonus_rel", "bonus (10^b) for the same dominant relation type in both (adj+noun, verb+obj, verb+subj, noun+gen)",
         grid({**base, "syn": "bonus-rel", "midp": True}, rv_link=["adj1", "adj2"], syn_b=[1.0, 3.0, 10.0], **knobs), None),
        ("syn_filter_rel", "keep only pairs with the same dominant relation type in both",
         grid({**base, "syn": "filter-rel", "midp": True}, rv_link=["adj1", "adj2"], **knobs), None),
    ]


def latin_rows(b: dict) -> list[tuple]:
    base = {k: v for k, v in b.items() if k not in ("min_count", "rank_by", "floor", "content_only", "max_logp")}
    knobs = dict(min_count=[1, 2], rank_by=["fisher", "max"], floor=[None, -10.0], content_only=[False, True],
                 max_logp=[0.0, ALPHA_EACH])
    return [(f"latin_{m}", f"+ early Latin (LASLA) as {m}",
             grid({**base, "third_mode": m}, lat_spec=["line", "sentence"], **knobs), None)
            for m in ("tiebreak", "fisher3", "fisher3pos", "require")]


# ---------------------------------------------------------------- cross-validation

def objective(ranks) -> float:
    r = fs.recall_at(ranks, KS)
    return statistics.mean(r[f"recall@{k}"] or 0 for k in KS)


def cv(env: Env, ev: dict, settings: list[dict], default: dict | None) -> dict:
    items = ev["items"]
    all_ranks = []
    for cfg in settings:
        all_ranks.append(_ranks(env.rank(cfg), items))
    dist = [0 if default is None else sum(cfg.get(k) != default.get(k) for k in set(cfg) | set(default))
            for cfg in settings]
    pooled: list = [None] * len(items)
    chosen = []
    for f in range(5):
        train = [i for i, it in enumerate(items) if it["fold"] != f]
        test = [i for i, it in enumerate(items) if it["fold"] == f]
        best = min(range(len(settings)),
                   key=lambda s: (-objective([all_ranks[s][i] for i in train]), dist[s], s))
        chosen.append(best)
        for i in test:
            pooled[i] = all_ranks[best][i]
    full_best = min(range(len(settings)), key=lambda s: (-objective(all_ranks[s]), dist[s], s))
    return {"pooled": pooled, "chosen": chosen, "full_best": full_best, "settings": settings, "all_ranks": all_ranks}


def _ranks(ranking, items):
    rank = {}
    for i, gp in enumerate(ranking, 1):
        rank.setdefault(gp, i)
    return [min((rank[tuple(p)] for p in it["pairs"] if tuple(p) in rank), default=None) for it in items]


def shuffled_recall(env: Env, ev: dict, res: dict) -> dict:
    items = ev["items"]
    per_seed = []
    for seed in SHUFFLE_SEEDS:
        pooled = [None] * len(items)
        for f, s in enumerate(res["chosen"]):
            ranks = _ranks(env.rank(res["settings"][s], seed), items)
            for i, it in enumerate(items):
                if it["fold"] == f:
                    pooled[i] = ranks[i]
        per_seed.append(fs.recall_at(pooled, KS))
    return {f"recall@{k}": round(statistics.mean(r[f"recall@{k}"] for r in per_seed), 3) for k in KS} | \
        {"max_over_seeds": {f"recall@{k}": round(max(r[f"recall@{k}"] for r in per_seed), 3) for k in KS}}


def summarize(env: Env, ev: dict, res: dict, shuffle: bool = True) -> dict:
    items = ev["items"]
    pooled = res["pooled"]
    prim = [r for r, it in zip(pooled, items) if it["primary"]]
    gold_only = [r for r, it in zip(pooled, items) if it["gold"]]
    out = {"n_items": len(items),
           "recall": {k: round(v, 3) for k, v in fs.recall_at(pooled, KS).items()},
           "ci95": fs.bootstrap_ci(pooled, KS),
           "gold_items": {"n": len(gold_only), **{k: round(v, 3) for k, v in fs.recall_at(gold_only, KS).items()}},
           "primary_items": {"n": len(prim), **{k: round(v, 3) for k, v in fs.recall_at(prim, KS).items()}},
           "chosen_per_fold": [res["settings"][s] for s in res["chosen"]],
           "folds_agree": len(set(res["chosen"])) == 1,
           "full_data_best": res["settings"][res["full_best"]],
           "n_settings": len(res["settings"]),
           "n_ranked_pairs_full_best": env.n_ranked(res["settings"][res["full_best"]])}
    if shuffle:
        out["shuffled"] = shuffled_recall(env, ev, res)
    return out


def run_ablation(env: Env) -> dict:
    evs = {"E2": build_eval(env, "pseudo"), "E1": build_eval(env, "r1")}
    for k, ev in evs.items():
        log(f"eval set {k}: {ev['summary']}")
    table = []
    results = {}

    def do(name, desc, settings, default):
        row = {"row": name, "description": desc}
        for k, ev in evs.items():
            res = cv(env, ev, settings, default)
            results[(name, k)] = res
            row[k] = summarize(env, ev, res)
            log(f"{name:20s} {k}: {row[k]['recall']} ci={row[k]['ci95']} shuf={row[k]['shuffled']} "
                f"n_set={len(settings)}")
        table.append(row)

    for name, desc, settings, default in rows():
        do(name, desc, settings, default)
    # exact scoring on the better mapping (by E2 pooled objective among the mapping rows)
    map_rows = ["map_kaikki", "map_kaikki_pseudo", "map_lexeme"]
    best_map_row = max(map_rows, key=lambda r: (objective(results[(r, "E2")]["pooled"]), -map_rows.index(r)))
    mapname = "kaikki" if best_map_row == "map_kaikki" else "pseudo"
    for name, desc, settings, default in exact_rows(mapname, ("group", "lexeme")):
        do(name, desc, settings, default)
    # control: the same exact scoring on the round-1 mapping (separates mapping from scoring)
    ctrl = exact_rows("r1", ("group", "lexeme"))[0]
    do("control_exact_r1map", "control: exact scoring on the round-1 mapping (not part of the cumulative chain)",
       ctrl[2], ctrl[3])
    b = results[("exact", "E2")]["settings"][results[("exact", "E2")]["full_best"]]
    for name, desc, settings, default in syntax_rows(b):
        do(name, desc, settings, default)
    syn_names = [r for r in ("exact", "syn_filter_linked", "syn_bonus_linked", "syn_bonus_rel", "syn_filter_rel")]
    best_syn = max(syn_names, key=lambda r: (objective(results[(r, "E2")]["pooled"]), -syn_names.index(r)))
    bs = results[(best_syn, "E2")]["settings"][results[(best_syn, "E2")]["full_best"]]
    for name, desc, settings, default in latin_rows(bs):
        do(name, desc, settings, default)
    all_names = [r["row"] for r in table]
    chain = [r for r in all_names[all_names.index("exact"):] if not r.startswith("control")]
    final_row = max(chain,
                    key=lambda r: (objective(results[(r, "E2")]["pooled"]), -all_names.index(r)))
    final = results[(final_row, "E2")]
    fcfg = final["settings"][final["full_best"]]
    strict = {**fcfg, "max_logp": ALPHA_EACH}
    do("final_each_p05", "diagnostic: the final setting, but each corpus must give p < 0.05 (fixed, not tuned)",
       [strict], strict)
    for row in table:
        for k in evs:
            fr, rr = results[(final_row, k)]["pooled"], results[(row["row"], k)]["pooled"]
            row[k]["final_minus_row"] = {f"recall@{kk}": fs.paired_bootstrap_diff(fr, rr, kk) for kk in KS}
    return {"evs": evs, "table": table, "results": results, "final_row": final_row,
            "final_cfg": final["settings"][final["full_best"]], "best_map_row": best_map_row, "best_syn_row": best_syn}


# ---------------------------------------------------------------- outputs

def describe(env: Env, x: str) -> dict:
    e = env.by_id.get(x)
    if e:
        return {"id": x, "pie": e["form"], "meaning": (e.get("meaning") or [None])[0]}
    return {"id": x, "pie": x.split(":", 1)[-1] if x.startswith("kaikki:") else None,
            "meaning": None, "note": "etymon linked by Wiktionary, not in our lexicon" if x.startswith("kaikki:") else None}


def write_evaluation(env: Env, ab: dict) -> None:
    evs = ab["evs"]
    ev = evs["E2"]
    cov = {m: {c: fs.coverage(env.tok[c], env.maps[m][c]) for c in ("rv", "hom", "lat")} for m in env.maps}
    silver_list = [{"pair": [describe(env, p[0])["pie"] or p[0], describe(env, p[1])["pie"] or p[1]], "ids": list(p),
                    "refs": refs, "in_gold": any(tuple(p) == tuple(q) for g in ev["gold"] for q in g["pairs"])}
                   for p, refs in sorted(ev["silver"].items())]
    final_res = ab["results"][(ab["final_row"], "E2")]
    items_out = [{"item_id": it["item_id"], "fold": it["fold"], "gold": it["gold"], "silver": it["silver"],
                  "primary": it["primary"],
                  "pairs": [[describe(env, x)["pie"] or x for x in p] for p in it["pairs"]],
                  "rank_heldout_final": r}
                 for it, r in zip(ev["items"], final_res["pooled"])]
    table_compact = [{"row": r["row"], **{k: {"recall": r[k]["recall"], "ci95": r[k]["ci95"],
                                              "shuffled": {kk: r[k]["shuffled"][kk] for kk in ("recall@50", "recall@100", "recall@200")},
                                              "gold_items": r[k]["gold_items"], "primary_items": r[k]["primary_items"],
                                              "final_minus_row": r[k]["final_minus_row"]}
                                          for k in ("E2", "E1")}} for r in ab["table"]]
    doc = {
        "round": 2,
        "date": time.strftime("%Y-%m-%d"),
        "protocol": ["Items: gold formulas (formulas.jsonl, kinds phrase/lexical/attested/schema with Vedic and "
                     "Greek attestations) and silver pairs (West, phrase-level co-citation), merged when they share "
                     "a PIE pair; recall@k = share of items with any pair ranked ≤ k among distinct root-group pairs.",
                     "5-fold CV by item (sha1 of its smallest pair): each fold's setting is chosen on the other four "
                     "folds; held-out ranks are pooled. CI: 2,000 bootstrap resamples of items (percentile).",
                     "E2 = evaluation set lemmatized with the round-2 mapping (frozen for all rows); E1 = the same "
                     "construction with the round-1 mapping. Both are reported for every row.",
                     "shuffled = mean over 5 seeds of the same per-fold settings run on corpora whose PIE labels are "
                     "permuted across token positions (unit structure kept)."],
        "eval_sets": {k: v["summary"] for k, v in evs.items()},
        "silver": {"definition": "a West paragraph cites two Vedic words for PIE groups x and y within 60 characters "
                                 "and two Greek words for x and y within 60 characters, the two phrases within 400 "
                                 "characters; words lemmatized through the corpus surface forms and the mapping",
                   "watkins": "0 pairs: the Watkins PDF text layer has no Greek script and Vedic without diacritics; "
                              "Watkins pages are used only for the mention flag on candidates",
                   "pairs_E2": silver_list,
                   "spot_check": SPOT_CHECK},
        "coverage": cov,
        "mapping_spot_check": MAPPING_SPOT_CHECK,
        "ablation": table_compact,
        "ablation_detail": ab["table"],
        "selection": {"best_mapping_row": ab["best_map_row"], "best_syntax_row": ab["best_syn_row"],
                      "final_row": ab["final_row"], "final_setting": ab["final_cfg"]},
        "items_E2": items_out,
        "round1": "evaluation_round1.json and tuning_round1.json hold the round-1 outputs",
    }
    (OUT / "evaluation.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")


SPOT_CHECK = {}            # filled from data/research/formulas/spot_checks.json if present
MAPPING_SPOT_CHECK = {}


def load_spot_checks():
    p = OUT / "spot_checks.json"
    if p.exists():
        d = json.loads(p.read_text("utf-8"))
        SPOT_CHECK.update(d.get("silver", {}))
        MAPPING_SPOT_CHECK.update(d.get("mapping", {}))


def mention_index(env: Env, ev: dict) -> dict:
    """pair → refs: West paragraphs (silver phrase-level, or any co-citation)
    and Watkins pages (co-citation of ASCII Vedic words) naming both."""
    stop = set()
    try:
        stop = {w.strip().lower() for w in open("/usr/share/dict/words", encoding="utf-8")}
    except OSError:
        pass
    m = env.maps["pseudo"]
    av = fs.ascii_lookup([(t.surface, m["rv"].lemma_groups[t.lemma]) for t in env.tok["rv"] if t.lemma in m["rv"].lemma_groups], stop)
    ag = fs.ascii_lookup([(fs.grc_roman(t.surface), m["hom"].lemma_groups[t.lemma]) for t in env.tok["hom"]
                          if t.lemma in m["hom"].lemma_groups], stop)
    _, wk = fs.build_silver(fs.watkins_passages(ROOT), lambda w: frozenset(), lambda w: frozenset(), av, ag)
    return {"silver": ev["silver"], "west": ev["mentions"], "watkins": wk}


def write_candidates(env: Env, cfg: dict, ev: dict, top_n: int = 200) -> list[dict]:
    known = fs.known_pairs(env.formulas, ev["lemmatizer"], env.pie_idx)
    ranking = [r for r in env.rank_full(cfg) if r["group_pair"] not in known]
    top = ranking[:top_n]
    mentions = mention_index(env, ev)
    m, lv, co = cfg["map"], cfg["level"], cfg["content_only"]
    toks = {c: env.tokens(c, m, lv, co, None) for c in ("rv", "hom", "lat")}
    want = {r["pair"] for r in top}
    ex = {"rv": fs.instances(toks["rv"], cfg["rv_spec"], want),
          "hom": fs.instances(toks["hom"], cfg["hom_spec"], want),
          "lat": fs.instances(toks["lat"], "line", want, limit=4)}
    link = cfg.get("rv_link", "adj1")
    rel_rv = env.relations("rv", m, lv, co, link)
    rel_hom = env.relations("hom", m, lv, co, "dep")
    out = []
    for i, r in enumerate(top, 1):
        p, gp = r["pair"], r["group_pair"]
        dr, dh = fs.dominant_relation(rel_rv.get(p)), fs.dominant_relation(rel_hom.get(p))

        def refs(d):
            return d.get(gp, [])[:5]
        lat_ex = [{"locus": e["locus"], "lemmas": e["lemmas"]} for e in ex["lat"][p]["examples"]]
        rec = {"rank": i, "pair": [describe(env, p[0]), describe(env, p[1])],
               "groups": [describe(env, g)["pie"] or g for g in gp] if lv == "lexeme" else None,
               "score_neglog10p": round(r["score"], 2),
               "rv": {"n": r["n"][0], "neglog10p": round(-r["logp"][0] / fs.LOG10, 2)},
               "hom": {"n": r["n"][1], "neglog10p": round(-r["logp"][1] / fs.LOG10, 2)},
               "lat": ({"n": r["third"]["n"], "neglog10p": round(-r["third"]["logp"] / fs.LOG10, 2)}
                       if r.get("third") else None),
               "significant_in_both": max(r["logp"]) < ALPHA_EACH,
               "relation": {"rv_linked": dict(rel_rv.get(p, {})), "hom_dependency": dict(rel_hom.get(p, {})),
                            "rv_dominant": dr, "hom_dominant": dh, "same_in_both": bool(dr and dr == dh)},
               "rv_examples": ex["rv"][p]["examples"], "hom_examples": ex["hom"][p]["examples"],
               "lat_examples": lat_ex,
               "west_watkins": {"silver_phrase_parallel": refs(mentions["silver"]),
                                "west_co_mention": refs(mentions["west"]),
                                "watkins_co_mention": refs(mentions["watkins"]),
                                "mentioned": bool(mentions["silver"].get(gp) or mentions["west"].get(gp)
                                                  or mentions["watkins"].get(gp))},
               "status": "unreviewed"}
        out.append(rec)
    with (OUT / "candidates.jsonl").open("w", encoding="utf-8") as fh:
        for rec in out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return out


# ================================================================ round 3: every branch

R3_OUT = OUT
MAPPING_DIR = OUT / "mapping"
R3_SEEDS = (0, 1, 2)
TOROT_OCS = ["proiel/marianus.xml", "torot/zogr.xml", "torot/supr.xml", "torot/psal-sin.xml", "torot/vit-const.xml",
             "torot/vit-meth.xml", "torot/kiev-mis.xml", "torot/chrabr.xml", "torot/euch.xml"]

SPECS3 = {
    "rv": fm.CorpusSpec("rv", "Indo-Iranian", "sa", "CC BY 4.0 (VedaWeb Zurich annotation)", "pada",
                        description="Rigveda, VedaWeb (round-2 corpus and mapping)"),
    "av": fm.CorpusSpec("av", "Indo-Iranian", "sa", "CC BY 4.0 (DCS)", "sentence",
                        description="DCS: Atharvaveda Śaunaka + Paippalāda, Ṛgvedakhilāni"),
    "ae": fm.CorpusSpec("ae", "Indo-Iranian", "ae", "NC (CAB)", "ab", description="Avesta, CAB Linguistic Corpus"),
    "hom": fm.CorpusSpec("hom", "Greek", "grc", "CC BY-SA 3.0 (Perseus AGDT)", "line",
                         description="Iliad + Odyssey, AGDT (round-2 corpus and mapping)"),
    "grp": fm.CorpusSpec("grp", "Greek", "grc", "GLAUx: CC BY / CC BY-SA, NC/NA texts research-only", "line",
                         description="GLAUx archaic/classical poetry (Hesiod, Hymns, lyric, tragedy)"),
    "lat": fm.CorpusSpec("lat", "Italic", "la", "NC (LASLA)", "line", description="Plautus, Lucretius, Catullus, Cato"),
    "xum": fm.CorpusSpec("xum", "Italic", "xum", "PD (Buck 1904)", "line", description="Iguvine Tables (Buck OCR)"),
    "non": fm.CorpusSpec("non", "Germanic", "non", "PD (FJ 1926)", "line", description="Poetic Edda, FJ 1926 OCR"),
    "ang": fm.CorpusSpec("ang", "Germanic", "ang", "PD", "line", description="Beowulf (Gutenberg) + Grein's Bibliothek I–II (OCR)"),
    "got": fm.CorpusSpec("got", "Germanic", "got", "NC (PROIEL)", "sentence", translation=True,
                         description="Gothic Bible, PROIEL"),
    "sga": fm.CorpusSpec("sga", "Celtic", "sga", "CC BY-SA / NC (UD)", "sentence", description="UD Old Irish glosses"),
    "cu": fm.CorpusSpec("cu", "Balto-Slavic", "cu", "NC (PROIEL/TOROT)", "sentence", translation=True,
                        description="Old Church Slavonic: Marianus, Zographensis, Suprasliensis, Psalterium Sinaiticum, …"),
    "lv": fm.CorpusSpec("lv", "Balto-Slavic", "lv", "OCR of a book on the dainas (quotations only)", "song",
                        description="Latvian dainas quoted in raw/books/text/dainas-endzelins"),
    "xcl": fm.CorpusSpec("xcl", "Armenian", "xcl", "NC (PROIEL)", "sentence", translation=True,
                         description="Classical Armenian NT, PROIEL"),
    "hit": fm.CorpusSpec("hit", "Anatolian", "hit", "CC BY 4.0 (TLHdig)", "line", description="TLHdig Hittite, tablet lines"),
}


class R3:
    """Round-3 corpora, mappings and counts (round-2 Env for RV, Homer, LASLA and the eval set)."""

    def __init__(self, env: Env):
        t = time.time()
        self.env = env
        lex = env.lex
        self.gmap = env.gmap
        self.tok: dict = {"rv": env.tok["rv"], "hom": env.tok["hom"], "lat": env.tok["lat"]}
        # mapping errata (data/research/formulas/mapping-overrides.json) on copies: round 2's Env is unchanged
        self.maps: dict = {c: fm.apply_lemma_overrides(c, env.maps["pseudo"][c], env.gmap) for c in ("rv", "hom", "lat")}
        self.recs: dict = {}
        idx = fs.PieIndex(lex)
        want = [c for L in fm.LANGS.values() for c in L.desc_codes]
        protos = fm.ProtoDB(want_desc=want)
        self.lm = {}
        for L in ("non", "ang", "got", "sga", "cu", "lv", "xcl", "hit", "xum", "ae"):
            self.lm[L] = fm.build_lang_mapping(L, lex, protos, idx=idx)
            log(f"mapping {L}: {len(self.lm[L].recs)} keys")
        # lemmatized corpora
        self.tok["got"] = fm.load_proiel(["proiel/gothic-nt.xml"], "got")
        self.tok["xcl"] = fm.load_proiel(["proiel/armenian-nt.xml"], "xcl")
        self.tok["cu"] = fm.load_proiel(TOROT_OCS, "cu")
        self.tok["sga"] = fm.load_oldirish_ud()
        self.tok["hit"] = fm.load_hittite()
        self.tok["av"] = fm.load_dcs()
        self.glaux_sel = fm.glaux_selection()
        self.tok["grp"] = fm.load_glaux(self.glaux_sel)
        for c in ("got", "xcl", "cu", "sga"):
            self.maps[c], self.recs[c] = fm.corpus_mapping(self.tok[c], self.lm[c], gmap=self.gmap)
        self._hittite()
        self._sanskrit()
        self._greek()
        # unlemmatized corpora
        self._text("non", fm.edda_lines(), fm.FormLemmatizer(self.lm["non"], fallbacks=(fm.non_clitic_variants,)))
        ang_lemz = fm.FormLemmatizer(self.lm["ang"])
        self._text("ang", fm.beowulf_lines() + fm.grein_lines(lambda w: ang_lemz(fm.grein_normalize(w))), ang_lemz)
        self._text("lv", fm.dainas_units(), fm.FormLemmatizer(self.lm["lv"], fallbacks=(fm.lv_diminutive_variants,)))
        lat_forms = {fs.lat_key(t.surface) for t in self.tok["lat"]}
        self._text("xum", fm.umbrian_lines(lat_forms), fm.FormLemmatizer(self.lm["xum"]))
        self._text("ae", fm.avesta_units(), fm.AvestanLemmatizer(self.lm["ae"], {}))
        for c in self.recs:
            self.recs[c] = fm.apply_rec_overrides(c, self.recs[c])
            self.maps[c] = fm.apply_lemma_overrides(c, self.maps[c], self.gmap)
        # Greek NT for the calque check
        gnt = fm.load_proiel(["proiel/greek-nt.xml"], "gnt")
        gm = fs.build_kaikki_mapping("grc", lex, gnt, fs.build_homer_mapping(lex, gnt), pseudo=True)
        fs.apply_mapping(gnt, gm, True, "lexeme")
        self.gnt_pairs = fm.verse_pairs(gnt)
        self.applied = None
        self.same_form = fm.homograph_pair_test(lex)
        form = {e["id"]: fs.pie_key(e["form"]).strip("-") for e in lex}
        # two pairs are homograph twins if each lexeme is the same entry or an entry of the same written form
        # (with identical per-corpus counts) or the two pairs share a lexeme: one word mapped to two entries
        self.homograph_twins = lambda p, q: bool(set(p) & set(q)) or all(
            a == b or (form.get(a) and form.get(a) == form.get(b))
            for a, b in zip(sorted(p, key=lambda x: form.get(x, x)), sorted(q, key=lambda x: form.get(x, x))))
        log(f"round 3 corpora and mappings in {time.time() - t:.0f}s: " +
            ", ".join(f"{c} {len(v)}" for c, v in self.tok.items()))

    def _text(self, c, units, lemz):
        lm = self.lm[SPECS3[c].lang]
        self.tok[c] = fm.text_tokens(c, units, lemz, lm.is_content)
        self.maps[c], self.recs[c] = fm.multi_lemma_mapping(self.tok[c], lm, self.gmap)

    def _hittite(self):
        """kaikki + lexicon (gloss-checked) first, EDHIL headwords as the second source (hm.hittite_table)."""
        final, self.hit_cov = hm.hittite_table(self.tok["hit"], self.lm["hit"], self.env.lex, self.gmap)
        mm = fs.Mapping()
        for l, r in final.items():
            mm.lemma_lex[l] = r.ids
            mm.lemma_groups[l] = frozenset(self.gmap.get(x, x) for x in r.ids)
            mm.lemma_tier[l] = r.how
        self.maps["hit"], self.recs["hit"] = mm, final
        log(f"hittite coverage {self.hit_cov}")

    def _sanskrit(self):
        """DCS lemmas: the RV mapping by accent-free lemma key, then the
        round-2 kaikki Sanskrit links (with root candidates for verbs)."""
        toks, lex = self.tok["av"], self.env.lex
        rvm = self.maps["rv"]
        bykey: dict = {}
        for lem in rvm.lemma_lex:
            for k in fs.skt_lemma_keys(lem):
                bykey.setdefault(k, (lem, rvm.lemma_lex[lem], rvm.lemma_tier.get(lem)))
        km = fs.build_kaikki_mapping("sa", lex, toks, None, pseudo=True)
        m = fs.Mapping()
        recs = {}
        for lem in {t.lemma for t in toks}:
            hit = next((bykey[k] for k in fs.skt_lemma_keys(lem) if k in bykey), None)
            if hit:
                m.lemma_lex[lem], m.lemma_tier[lem] = hit[1], "rv-lemma"
                recs[lem] = fm.MapRec(lem, hit[0], hit[1], (f"sa:{lem}", f"rv-lemma:{hit[0]}", f"r2-tier:{hit[2]}"),
                                      "rv-lemma", "high" if hit[2] in ("kaikki", "direct", "kaikki-proto") else "medium",
                                      ("round2-rv",))
            elif lem in km.lemma_lex:
                m.lemma_lex[lem], m.lemma_tier[lem] = km.lemma_lex[lem], km.lemma_tier[lem]
                recs[lem] = fm.MapRec(lem, lem, km.lemma_lex[lem], (f"sa:{lem}", f"kaikki-sa:{km.lemma_tier[lem]}"),
                                      km.lemma_tier[lem], "low" if km.lemma_tier[lem] == "kaikki-pseudo" else "medium",
                                      ("round2-kaikki-sa",))
            if lem in m.lemma_lex:
                m.lemma_groups[lem] = frozenset(self.gmap.get(x, x) for x in m.lemma_lex[lem])
        self.maps["av"], self.recs["av"] = m, recs

    def _greek(self):
        """GLAUx lemmas: the round-2 kaikki Greek mapping with the round-1 rules as backoff."""
        toks, lex = self.tok["grp"], self.env.lex
        m = fs.build_kaikki_mapping("grc", lex, toks, fs.build_homer_mapping(lex, toks), pseudo=True)
        self.maps["grp"] = m
        self.recs["grp"] = {l: fm.MapRec(l, l, m.lemma_lex[l], (f"grc:{l}", f"r2-tier:{m.lemma_tier[l]}"),
                                         m.lemma_tier[l], "low" if m.lemma_tier[l] == "kaikki-pseudo" else "medium",
                                         ("round2-grc",)) for l in m.lemma_lex}

    # ---- counting
    def apply(self, level="lexeme"):
        if self.applied == level:
            return
        for c, toks in self.tok.items():
            fs.apply_mapping(toks, self.maps[c], True, level)
        self.applied = level

    def counts(self, corpora, level="lexeme", seed=None) -> dict:
        self.apply(level)
        out = {}
        for c in corpora:
            toks = self.tok[c] if seed is None else fs.shuffled(self.tok[c], seed + 7 * list(SPECS3).index(c))
            out[c] = fs.count_units(fs.rootsets_by(toks, SPECS3[c].unit))
        return out

    def calques(self, level="lexeme", seed=None) -> dict:
        self.apply(level)
        ub = {}
        for c in ("got", "xcl", "cu"):
            toks = self.tok[c] if seed is None else fs.shuffled(self.tok[c], seed + 7 * list(SPECS3).index(c))
            ub[c] = fm.units_with_verse(toks, SPECS3[c].unit)
        return fm.calque_counts(ub, self.gnt_pairs if seed is None else {})

    def project(self, p):
        return self.env.project(p)


def r3_rank(r3: R3, corpora, level="lexeme", seed=None, require_sig=True, core_only=False,
            branch_filter=None, drop_homographs=True) -> list[dict]:
    cnt = r3.counts(corpora, level, seed)
    cal = r3.calques(level, seed) if any(c in corpora for c in ("got", "xcl", "cu")) else None
    rows = fm.score_branches(cnt, SPECS3, cal, require_sig=require_sig,
                             same_form=r3.same_form if drop_homographs else None)
    if branch_filter:
        rows = [r for r in rows if branch_filter(r)]
    if core_only:     # re-score Greek + Indo-Iranian pairs on those two witnesses only
        out = []
        for r in rows:
            w = [x for x in r["witnesses"] if x.branch in fm.CORE]
            if len(w) == 2:
                comb = fs.fisher_logp([x.logp for x in w])
                out.append({**r, "combined_logp": comb, "score": -comb / fs.LOG10})
        out.sort(key=lambda r: (-r["score"], r["pair"]))
        rows = out
    return rows


def _group_rank(r3: R3, rows: list[dict]) -> list:
    out, seen = [], set()
    for r in rows:
        gp = r3.project(r["pair"])
        if gp is None or gp in seen:
            continue
        seen.add(gp)
        out.append(gp)
    return out


def has_core(r):
    return fm.CORE <= {w.branch for w in r["witnesses"]}


ALL_R3 = list(SPECS3)
CORE_CORPORA = ["rv", "hom"]


def r3_configs():
    """Fixed (not tuned) configurations for the sanity measurement."""
    return {
        "r2_final": None,   # round-2 final setting, its own code path
        "r3_rv_hom_only": dict(corpora=CORE_CORPORA, require_sig=True),
        # diagnostics (descriptive, nothing is selected on them): which added core corpus moves the ranks
        "diag_rv_hom_grp": dict(corpora=["rv", "hom", "grp"], require_sig=True),
        "diag_rv_av_hom": dict(corpora=["rv", "av", "hom"], require_sig=True),
        "diag_rv_ae_hom": dict(corpora=["rv", "ae", "hom"], require_sig=True),
        "r3_core_corpora_core_score": dict(corpora=["rv", "av", "ae", "hom", "grp"], require_sig=True, core_only=True),
        "r3_all_core_pairs": dict(corpora=ALL_R3, require_sig=True, branch_filter=has_core),
        "r3_all_core_score_only": dict(corpora=ALL_R3, require_sig=True, branch_filter=has_core, core_only=True),
        "r3_all_pairs": dict(corpora=ALL_R3, require_sig=True),
    }


def run_round3(env: Env) -> int:
    MAPPING_DIR.mkdir(parents=True, exist_ok=True)
    r3 = R3(env)
    write_mapping_tables(r3)
    ev = build_eval(env, "pseudo")
    items = ev["items"]
    final_cfg = json.loads((OUT / "final_setting.json").read_text("utf-8"))["setting"]
    res = {}
    rankings = {}
    for name, cfg in r3_configs().items():
        t = time.time()
        if cfg is None:
            g = env.rank(final_cfg)
            rows = None
        else:
            rows = r3_rank(r3, **cfg)
            g = _group_rank(r3, rows)
        rankings[name] = rows
        ranks = _ranks(g, items)
        res[name] = {"recall": fs.recall_at(ranks, KS), "ci95": fs.bootstrap_ci(ranks, KS), "ranks": ranks,
                     "n_ranked": len(g)}
        log(f"{name}: {res[name]['recall']} n={len(g)} {time.time() - t:.0f}s")
    for name in res:
        res[name]["minus_r2"] = {f"recall@{k}": fs.paired_bootstrap_diff(res[name]["ranks"], res["r2_final"]["ranks"], k)
                                 for k in KS}
    # regression: the N-branch code on rv + hom without the significance filter = round 2's ranking
    reg = r3_rank(r3, CORE_CORPORA, require_sig=False, drop_homographs=False)
    g_reg, g_r2 = _group_rank(r3, reg)[:200], env.rank(final_cfg)[:200]
    regression = {"top200_identical": g_reg == g_r2, "top200_overlap": len(set(g_reg) & set(g_r2))}
    log(f"regression vs round 2: {regression}")
    # third-branch witnesses of the evaluation items (all-corpora rows)
    allrows = rankings["r3_all_pairs"]
    by_gp: dict = {}
    for r in allrows:
        gp = r3.project(r["pair"])
        if gp and gp not in by_gp:
            by_gp[gp] = r
    third = []
    g_all = {gp: i for i, gp in enumerate(_group_rank(r3, allrows), 1)}
    for it in items:
        rs = [by_gp[tuple(p)] for p in it["pairs"] if tuple(p) in by_gp]
        extra = sorted({w.branch for r in rs for w in r["witnesses"] if w.branch not in fm.CORE})
        third.append({"item_id": it["item_id"], "pairs": [[describe(env, x)["pie"] or x for x in p] for p in it["pairs"]],
                      "third_branch_witnesses": extra,
                      "rank_all_pairs": min((g_all[tuple(p)] for p in it["pairs"] if tuple(p) in g_all), default=None)})
    # shuffled baseline per ranking class
    real = {cl: [r for r in allrows if fm.ranking_class(r) == cl] for cl in "abc"}
    cut = {cl: (real[cl][99]["score"] if len(real[cl]) >= 100 else (real[cl][-1]["score"] if real[cl] else None))
           for cl in "abc"}
    shuf = {cl: [] for cl in "abc"}
    shuf_items = []
    for seed in R3_SEEDS:
        rows = r3_rank(r3, ALL_R3, seed=seed)
        for cl in "abc":
            sc = [r for r in rows if fm.ranking_class(r) == cl]
            shuf[cl].append({"n_pairs": len(sc), "n_above_real_top100_cutoff":
                             sum(1 for r in sc if cut[cl] is not None and r["score"] >= cut[cl])})
        core = [r for r in rows if has_core(r)]
        shuf_items.append(fs.recall_at(_ranks(_group_rank(r3, core), items), KS))
        log(f"shuffle seed {seed}: " + str({cl: shuf[cl][-1] for cl in "abc"}))
    top_stats = {}
    for cl in "abc":
        t100 = real[cl][:100]
        top_stats[cl] = {"n": len(t100),
                         "with_2plus_witnesses_p05": sum(sum(w.logp < math.log(0.05) for w in r["witnesses"]) >= 2 for r in t100),
                         "with_translation_witness": sum(any(w.translation_only for w in r["witnesses"]) for r in t100),
                         "weakest_witness_p_ge_0.5": sum(max(w.logp for w in r["witnesses"]) >= math.log(0.5) for r in t100)}
    baseline = {"top100_witness_stats": top_stats, "per_class": {cl: {"real_n_pairs": len(real[cl]), "real_top100_cutoff_neglog10p": cut[cl],
                                   "shuffled": shuf[cl]} for cl in "abc"},
                "items_recall_r3_all_core_pairs_shuffled": {
                    f"recall@{k}": round(statistics.mean(x[f"recall@{k}"] for x in shuf_items), 3) for k in KS}}
    cands = write_candidates_r3(r3, real)
    write_round3_json(r3, res, regression, third, baseline, cands, items)
    return 0


def write_mapping_tables(r3: R3):
    """data/research/formulas/mapping/<corpus>.jsonl: one row per mapped
    corpus lemma (dictionary word, corpus lemma or lemma key, lexicon ids,
    path, confidence, how, sources). No corpus text."""
    for c, recs in r3.recs.items():
        rows = []
        for lem in sorted(recs):
            r = recs[lem]
            rows.append({"corpus": c, "lang": SPECS3[c].lang, "lemma": lem, "word": r.word, "lex_id": sorted(r.ids),
                         "path": list(r.path), "how": r.how, "confidence": r.confidence, "sources": list(r.sources)})
        (MAPPING_DIR / f"{c}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")


def write_hittite_table() -> dict:
    """Rewrite data/research/formulas/mapping/hit.jsonl alone (the R3 route for Hittite without building
    the other corpora): TLHdig tokens, the kaikki Hittite LangMapping, hm.hittite_table, the mapping
    errata. Returns the coverage notes."""
    lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
    gmap = fs.group_map(lex)
    lm = fm.build_lang_mapping("hit", lex, fm.ProtoDB(want_desc=fm.LANGS["hit"].desc_codes), idx=fs.PieIndex(lex))
    toks = fm.load_hittite()
    final, cov = hm.hittite_table(toks, lm, lex, gmap)
    final = fm.apply_rec_overrides("hit", final)
    MAPPING_DIR.mkdir(parents=True, exist_ok=True)
    (MAPPING_DIR / "hit.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n"
                                                   for x in hm.table_rows(final)), "utf-8")
    log(f"hit.jsonl: {len(final)} rows; coverage {cov}")
    st: dict = {}
    dt = hm.doubtful_table(toks, lex, gmap, final, stats=st)
    (ROOT / hm.DOUBTFUL_TABLE).write_text("".join(json.dumps({**x, "note": hm.doubtful_note(x)}, ensure_ascii=False) + "\n"
                                                  for x in hm.table_rows(dt)), "utf-8")
    log(f"hit-doubtful.jsonl (retrieval only): {len(dt)} rows; {st}")
    return cov


def coverage_r3(r3: R3) -> dict:
    out = {}
    for c, toks in r3.tok.items():
        cont = [t for t in toks if t.content]
        m = r3.maps[c]
        lem = collections.Counter(t.lemma for t in cont)
        mapped = [l for l in lem if l in m.lemma_lex]
        conf = collections.Counter()
        recs = r3.recs.get(c, {})
        for t in cont:
            if t.lemma in m.lemma_lex:
                conf[recs[t.lemma].confidence if t.lemma in recs else "round2"] += 1
        lexeme = sum(1 for t in cont if t.lemma in m.lemma_lex and any(not x.startswith("pie-root-") for x in m.lemma_lex[t.lemma]))
        units = len({t.units[SPECS3[c].unit] for t in toks})
        out[c] = {"tokens": len(toks), "content_tokens": len(cont), "units": units,
                  "content_tokens_mapped": sum(lem[l] for l in mapped),
                  "content_token_share": round(sum(lem[l] for l in mapped) / max(1, len(cont)), 4),
                  "content_types": len(lem), "content_types_mapped": len(mapped),
                  "type_share": round(len(mapped) / max(1, len(lem)), 4),
                  "mapped_tokens_by_confidence": dict(conf),
                  "mapped_tokens_lexeme_level_share": round(lexeme / max(1, sum(lem[l] for l in mapped)), 4)}
    return out


def _loci(r3: R3, corpus: str, pairs: set, limit=3) -> dict:
    ex = fs.instances(r3.tok[corpus], SPECS3[corpus].unit, pairs, limit=limit)
    return {p: [e["locus"] for e in v["examples"]] for p, v in ex.items()}


def write_candidates_r3(r3: R3, real: dict, top_n: int = 100) -> dict:
    env = r3.env
    r3.apply("lexeme")
    known = fs.known_pairs(env.formulas, env.lemmatizer("pseudo"), env.pie_idx)
    out = {}
    for cl, rows in real.items():
        seen, sig, top, alts = set(), {}, [], collections.defaultdict(list)    # sig: counts → kept (pair, gp)
        for r in rows:
            gp = r3.project(r["pair"])
            if gp is None or gp in seen:
                continue
            seen.add(gp)
            # homograph duplicates: the same co-occurrences counted under another entry of one written form
            key = tuple(sorted((c, n) for w in r["witnesses"] for c, n in w.corpora.items()))
            twin = next((k for k in sig.get(key, []) if r3.homograph_twins(k[0], r["pair"])), None)
            if twin:
                alts[twin[1]].append(gp)
                continue
            sig.setdefault(key, []).append((r["pair"], gp))
            top.append((r, gp))
            if len(top) >= top_n:
                break
        want = {r["pair"] for r, _ in top}
        loci = {c: _loci(r3, c, want) for c in r3.tok}
        recs = []
        for i, (r, gp) in enumerate(top, 1):
            p = r["pair"]
            per = {}
            for w in r["witnesses"]:
                for c, n in w.corpora.items():
                    per[c] = {"branch": SPECS3[c].branch, "n": n, "loci": loci[c].get(p, [])[:3]}
            paths = {}
            for c in per:
                for x in p:
                    for lem, rec in r3.recs.get(c, {}).items():
                        if x in rec.ids:
                            paths.setdefault(c, {}).setdefault(x, []).append(" > ".join(rec.path))
                            if len(paths[c][x]) >= 2:
                                break
            recs.append({"rank": i, "class": cl, "pair": [describe(env, p[0]), describe(env, p[1])],
                         "groups": [describe(env, g)["pie"] or g for g in gp],
                         "score_neglog10p": round(r["score"], 2),
                         "weakest_witness_neglog10p": round(-max(w.logp for w in r["witnesses"]) / fs.LOG10, 2),
                         "n_witnesses_p05": sum(w.logp < math.log(0.05) for w in r["witnesses"]),
                         "witnesses": [{"branch": w.branch, "n": w.n, "neglog10p": round(-w.logp / fs.LOG10, 2),
                                        "translation_only": w.translation_only} for w in r["witnesses"]],
                         "per_corpus": per, "mapping_paths": paths, "in_formulas_jsonl": gp in known,
                         "homograph_alternatives": [[describe(env, g)["pie"] or g for g in a] for a in alts.get(gp, [])],
                         "status": "unreviewed"})
        out[cl] = recs
        (OUT / f"candidates-r3-{cl}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in recs),
                                                       "utf-8")
    return out


def write_round3_json(r3, res, regression, third, baseline, cands, items):
    doc = {"round": 3, "date": time.strftime("%Y-%m-%d"),
           "note": "Sanity measurement on the round-2 24-item set (not confirmatory; the set was used for tuning in "
                   "round 2). Fixed settings, no CV, CIs from 2,000 bootstrap resamples of items.",
           "corpora": {c: {**SPECS3[c].__dict__} for c in SPECS3},
           "glaux_subset": [{"tlg": r["TLG"], "author": r["AUTHOR_STANDARD"], "title": r["TITLE_STANDARD"],
                             "genre": r["GENRE_STANDARD"], "licence": r["SOURCE_LICENSE"], "tokens": r["TOKENS"]}
                            for r in r3.glaux_sel],
           "coverage": coverage_r3(r3), "hittite_coverage": r3.hit_cov,
           "sanity": {k: {kk: vv for kk, vv in v.items()} for k, v in res.items()},
           "configs": {k: (v if v is None else {kk: (vv.__name__ if callable(vv) else vv) for kk, vv in v.items()})
                       for k, v in r3_configs().items()},
           "regression_vs_round2": regression, "items_third_branch": third, "shuffled_baseline": baseline,
           "candidates": {cl: len(v) for cl, v in cands.items()}}
    (OUT / "evaluation-r3.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n", "utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["ablation", "candidates", "all", "round3", "mapping"])
    ap.add_argument("--corpus", choices=["hit"], help="mapping stage: rewrite this corpus's table only")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "mapping" and args.corpus == "hit":
        write_hittite_table()
        return 0
    load_spot_checks()
    env = Env()
    if args.stage == "round3":
        return run_round3(env)
    if args.stage == "mapping":       # rewrite the round-3 mapping tables only (e.g. after new errata)
        MAPPING_DIR.mkdir(parents=True, exist_ok=True)
        write_mapping_tables(R3(env))
        return 0
    if args.stage in ("ablation", "all"):
        ab = run_ablation(env)
        write_evaluation(env, ab)
        (OUT / "final_setting.json").write_text(json.dumps({"final_row": ab["final_row"], "setting": ab["final_cfg"]},
                                                           ensure_ascii=False, indent=1) + "\n", "utf-8")
        ev = ab["evs"]["E2"]
    else:
        ev = build_eval(env, "pseudo")
    if args.stage in ("candidates", "all"):
        cfg = json.loads((OUT / "final_setting.json").read_text("utf-8"))["setting"]
        cands = write_candidates(env, cfg, ev)
        log(f"wrote {len(cands)} candidates with {cfg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
