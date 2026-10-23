#!/usr/bin/env python3
"""Formula discovery (Phase 8a), round 2: ablation over mapping, scoring,
syntax and a third witness, evaluated by 5-fold cross-validation on a
fixed evaluation set.

  uv run python -I scripts/formula_search.py ablation     # evaluation.json
  uv run python -I scripts/formula_search.py candidates   # candidates.jsonl (final method)
  uv run python -I scripts/formula_search.py all

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
                                     third=third, third_mode=cfg.get("third_mode", "none"), bonus=bonus, keep=keep,
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
                    rank_by=["fisher", "max"], midp=[False, True], floor=[None, -10.0], content_only=[False, True])
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
         "min_count": 1, "rank_by": "fisher", "midp": False, "floor": None, "content_only": False}
    return [("exact", f"+ exact per-corpus tests (hypergeometric / Poisson) combined by Fisher; map={mapname}",
             exact_grid(mapname, levels), d)]


def syntax_rows(b: dict) -> list[tuple]:
    """Variants on top of a fixed exact setting family b (specs and levels
    from the exact row's choice; the other knobs re-tuned)."""
    base = {k: b[k] for k in ("scorer", "map", "level", "rv_spec", "hom_spec")}
    knobs = dict(min_count=[1, 2], rank_by=["fisher", "max"], floor=[None, -10.0], content_only=[False, True])
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
    base = {k: v for k, v in b.items() if k not in ("min_count", "rank_by", "floor", "content_only")}
    knobs = dict(min_count=[1, 2], rank_by=["fisher", "max"], floor=[None, -10.0], content_only=[False, True])
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
                                              "gold_items": r[k]["gold_items"], "primary_items": r[k]["primary_items"]}
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["ablation", "candidates", "all"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    load_spot_checks()
    env = Env()
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
