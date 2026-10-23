#!/usr/bin/env python3
"""Phase 8a confirmatory evaluation: score the frozen formula-search rankings
on the pre-registered eval-r3 set (docs/research/8a-eval-set.md, "Pre-registered
protocol"). Run once; nothing here selects or tunes anything.

  uv run python -I scripts/score_eval_r3.py generate RANKINGS.json   # build rankings (~3 min)
  uv run python -I scripts/score_eval_r3.py score RANKINGS.json      # confirmatory-r3.json + tables

Rankings (all with their saved settings, nothing changed):
  R2    round 2's final setting (final_setting.json) on RV + Homer: Env.rank_full, the full
        list of distinct root-group pairs.
  R3-a/b/c  round 3's all-corpora ranking (r3_rank(ALL_R3), the rows of run_round3) split by
        fm.ranking_class, deduplicated by root group with homograph twins folded exactly as in
        write_candidates_r3 (that loop is copied here as fold_twins, without the top-100 cap).
The rankings are indexed by root-group pair, so an item's rank is the minimum rank over its
`pairs_root`. The shuffled baselines are the same code on corpora whose PIE labels are
permuted across tokens (seeds 0-4).
"""

import collections
import hashlib
import importlib.util
import itertools
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pie import formula_search as fs  # noqa: E402

EVAL = ROOT / "data/research/formulas/eval-r3/formulas-eval.jsonl"
EVAL_SHA256 = "1f4668366af9f5c6c2d127f6c7e395c88bc4b2be9c56aa996d4625b71fba2e0f"   # 8a-eval-set.md
FORMULAS = ROOT / "data/research/formulas"
OUT_JSON = FORMULAS / "confirmatory-r3.json"
KS = (50, 100, 200)
SEEDS = (0, 1, 2, 3, 4)
II, GK = "Indo-Iranian", "Greek"
CORE = frozenset({II, GK})
# the eight branches with a corpus in round 3 (pie.formula_search_multi.BRANCHES)
COVERED = frozenset({"Indo-Iranian", "Greek", "Italic", "Germanic", "Celtic", "Balto-Slavic", "Armenian", "Anatolian"})
# eval-set corpus names (phrase_corpora_confirmed) → branch
CORPUS_BRANCH = {"rv": II, "av": II, "avesta": II, "homer": GK, "glaux": GK, "latin": "Italic",
                 "edda": "Germanic", "oe": "Germanic", "hittite": "Anatolian"}
# ranking → eligibility rule: "two" = phrase_branches contains both X and Y; "min3" = ≥ 3 covered
# branches; "other_pair" = contains some covered branch pair other than Greek + Indo-Iranian
RANKINGS = {"R2": ("two", CORE), "R3-c": ("two", CORE), "R3-a": ("min3", None), "R3-b": ("other_pair", None)}
SUBSETS = ("all", "held_out_core", "corpus_confirmed", "uncontested")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- pure scoring helpers (tested)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_rule(branches, rule: str, pair=None) -> bool:
    b = set(branches) & COVERED
    if rule == "two":
        return set(pair) <= b
    if rule == "min3":
        return len(b) >= 3
    if rule == "other_pair":
        return any(frozenset(c) != CORE for c in itertools.combinations(sorted(b), 2))
    raise ValueError(rule)


def eligible(item: dict, ranking: str, field: str = "phrase_branches") -> bool:
    rule, pair = RANKINGS[ranking]
    return branch_rule(item.get(field) or [], rule, pair)


def confirmed_branches(item: dict) -> set:
    out = set()
    for c in item.get("phrase_corpora_confirmed") or []:
        if c not in CORPUS_BRANCH:
            raise KeyError(f"unknown corpus {c!r} in {item['item_id']}")
        out.add(CORPUS_BRANCH[c])
    return out & set(item.get("phrase_branches") or [])


def in_subset(item: dict, subset: str, ranking: str) -> bool:
    if subset == "all":
        return True
    if subset == "held_out_core":
        return item.get("held_out_core") is True
    if subset == "uncontested":
        return item.get("verdict") == "accepted"
    if subset == "corpus_confirmed":
        rule, pair = RANKINGS[ranking]
        return branch_rule(confirmed_branches(item), rule, pair)
    raise ValueError(subset)


def norm(p) -> tuple:
    a, b = p
    return (a, b) if a < b else (b, a)


def rank_index(groups: list) -> dict:
    """root-group pair → 1-based rank (first occurrence)."""
    idx = {}
    for i, gp in enumerate(groups, 1):
        idx.setdefault(norm(gp), i)
    return idx


def item_rank(item: dict, idx: dict):
    """Minimum rank over the item's pairs_root; None if none is ranked."""
    rs = [idx[norm(p)] for p in item.get("pairs_root") or [] if len(set(p)) == 2 and norm(p) in idx]
    return min(rs) if rs else None


def fold_twins(rows, project, twins):
    """Copy of the selection loop in scripts/formula_search.py write_candidates_r3, without its
    top_n cap: distinct root-group pairs best first; a pair whose per-corpus co-occurrence
    counts equal an already kept pair's and that is its homograph twin is folded into the kept
    pair's alternatives instead of getting a rank of its own."""
    seen, sig, top, alts = set(), {}, [], collections.defaultdict(list)
    for r in rows:
        gp = project(r["pair"])
        if gp is None or gp in seen:
            continue
        seen.add(gp)
        key = tuple(sorted((c, n) for w in r["witnesses"] for c, n in w.corpora.items()))
        twin = next((k for k in sig.get(key, []) if twins(k[0], r["pair"])), None)
        if twin:
            alts[twin[1]].append(gp)
            continue
        sig.setdefault(key, []).append((r["pair"], gp))
        top.append((r, gp))
    return top, alts


def recall_block(ranks: list) -> dict:
    rec = fs.recall_at(ranks, KS)
    ci = fs.bootstrap_ci(ranks, KS)
    return {f"recall@{k}": (None if rec[f"recall@{k}"] is None else round(rec[f"recall@{k}"], 3)) for k in KS} | \
        {"ci95": ci, "n": len(ranks), "hits": {f"@{k}": sum(1 for r in ranks if r and r <= k) for k in KS}}


# ---------------------------------------------------------------- generate (runs the frozen code)

def _load_search_script():
    spec = importlib.util.spec_from_file_location("formula_search_script", ROOT / "scripts/formula_search.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def generate(dest: Path) -> int:
    if sha256(EVAL) != EVAL_SHA256:
        log("eval set hash mismatch; stop")
        return 2
    # guard: anything the search script would write goes to a scratch dir, not the repo
    scratch = dest.parent / "formula_search_out"
    scratch.mkdir(parents=True, exist_ok=True)
    os.environ["FORMULA_SEARCH_OUT"] = str(scratch)
    S = _load_search_script()
    assert S.OUT == scratch
    final_cfg = json.loads((FORMULAS / "final_setting.json").read_text("utf-8"))["setting"]
    t0 = time.time()
    env = S.Env()
    out = {"commit": git("rev-parse", "HEAD"),
           "git_status_search_code": git("status", "--short", "pie/formula_search.py", "pie/formula_search_multi.py",
                                         "scripts/formula_search.py", "data/research/formulas/final_setting.json"),
           "eval_sha256": sha256(EVAL), "final_setting": final_cfg, "checks": {}, "rankings": {}, "shuffled": {}}

    # ---- R2: the round-2 final setting, full ranking (real, then the 5 shuffles)
    full = env.rank_full(final_cfg)
    out["rankings"]["R2"] = [{"gp": list(r["group_pair"]), "pair": list(r["pair"]), "score": r["score"]} for r in full]
    known = fs.known_pairs(env.formulas, env.lemmatizer("pseudo"), env.pie_idx)
    saved = [json.loads(l) for l in (FORMULAS / "candidates.jsonl").read_text("utf-8").splitlines() if l.strip()]
    regen = [r for r in full if r["group_pair"] not in known][:len(saved)]
    out["checks"]["R2_reproduces_candidates_jsonl"] = {
        "n_compared": len(saved),
        "identical_pairs_and_order": [tuple(x["id"] for x in s["pair"]) for s in saved] == [tuple(r["pair"]) for r in regen],
        "identical_scores": [s["score_neglog10p"] for s in saved] == [round(r["score"], 2) for r in regen]}
    log(f"R2: {len(full)} ranked pairs, check {out['checks']['R2_reproduces_candidates_jsonl']}, {time.time() - t0:.0f}s")
    out["shuffled"]["R2"] = {}
    for seed in SEEDS:
        out["shuffled"]["R2"][str(seed)] = [list(r["group_pair"]) for r in env.rank_full(final_cfg, seed)]
        log(f"R2 shuffle {seed}: {len(out['shuffled']['R2'][str(seed)])} pairs")

    # ---- R3: all corpora, classes a/b/c (round 3's rows for its candidate lists)
    r3 = S.R3(env)
    from pie import formula_search_multi as fm
    assert COVERED == frozenset(fm.BRANCHES) and CORE == fm.CORE

    def classes(rows):
        res = {}
        for cl in "abc":
            sub = [r for r in rows if fm.ranking_class(r) == cl]
            top, alts = fold_twins(sub, r3.project, r3.homograph_twins)
            res[cl] = {"folded": top, "alts": alts, "unfolded": S._group_rank(r3, sub)}
        return res

    rows = S.r3_rank(r3, S.ALL_R3)
    real = classes(rows)
    for cl in "abc":
        top = real[cl]["folded"]
        out["rankings"][f"R3-{cl}"] = [
            {"gp": list(gp), "pair": list(r["pair"]), "score": r["score"],
             "witnesses": [{"branch": w.branch, "n": w.n, "neglog10p": round(-w.logp / fs.LOG10, 2)} for w in r["witnesses"]],
             "homograph_alternatives": [list(a) for a in real[cl]["alts"].get(gp, [])]} for r, gp in top]
        out["rankings"][f"R3-{cl}-unfolded"] = [list(gp) for gp in real[cl]["unfolded"]]
        saved = [json.loads(l) for l in (FORMULAS / f"candidates-r3-{cl}.jsonl").read_text("utf-8").splitlines() if l.strip()]
        out["checks"][f"R3-{cl}_reproduces_candidates_r3_{cl}_jsonl"] = {
            "n_compared": len(saved),
            "identical_pairs_and_order": [tuple(x["id"] for x in s["pair"]) for s in saved] ==
                                         [tuple(r["pair"]) for r, _ in top[:len(saved)]],
            "identical_scores": [s["score_neglog10p"] for s in saved] == [round(r["score"], 2) for r, _ in top[:len(saved)]]}
        log(f"R3-{cl}: {len(top)} folded / {len(real[cl]['unfolded'])} unfolded, "
            f"check {out['checks'][f'R3-{cl}_reproduces_candidates_r3_{cl}_jsonl']}")
    for cl in "abc":
        out["shuffled"][f"R3-{cl}"] = {}
    for seed in SEEDS:
        sh = classes(S.r3_rank(r3, S.ALL_R3, seed=seed))
        for cl in "abc":
            out["shuffled"][f"R3-{cl}"][str(seed)] = [list(gp) for _, gp in sh[cl]["folded"]]
        log(f"R3 shuffle {seed}: " + ", ".join(f"{cl} {len(sh[cl]['folded'])}" for cl in "abc") + f", {time.time() - t0:.0f}s")
    out["runtime_s"] = round(time.time() - t0)
    out["scratch_files_written_by_search_code"] = sorted(str(p.relative_to(scratch)) for p in scratch.rglob("*") if p.is_file())
    dest.write_text(json.dumps(out, ensure_ascii=False) + "\n", "utf-8")
    log(f"wrote {dest}")
    return 0


# ---------------------------------------------------------------- score

def load_eval() -> list[dict]:
    return [json.loads(l) for l in EVAL.read_text("utf-8").splitlines() if l.strip()]


def score(src: Path) -> int:
    if sha256(EVAL) != EVAL_SHA256:
        log("eval set hash mismatch; stop")
        return 2
    gen = json.loads(src.read_text("utf-8"))
    if not all(c["identical_pairs_and_order"] and c["identical_scores"] for c in gen["checks"].values()):
        log(f"reproduction check failed: {gen['checks']}; stop")
        return 3
    items = load_eval()
    primary = [it for it in items if it.get("primary") is True]
    secondary = [it for it in items if it.get("strength") == "lexical" and it.get("primary") is not True]
    idx = {name: rank_index([r["gp"] for r in gen["rankings"][name]]) for name in RANKINGS}
    lexpair = {name: {norm(r["gp"]): norm(r["pair"]) for r in gen["rankings"][name]} for name in RANKINGS}
    idx_unf = {f"R3-{cl}": rank_index(gen["rankings"][f"R3-{cl}-unfolded"]) for cl in "abc"}
    alt_of = {f"R3-{cl}": {norm(a): norm(r["gp"]) for r in gen["rankings"][f"R3-{cl}"] for a in r["homograph_alternatives"]}
              for cl in "abc"}
    sh_idx = {name: {s: rank_index(g) for s, g in gen["shuffled"][name].items()} for name in RANKINGS}

    res = {"protocol": "docs/research/8a-eval-set.md, Pre-registered protocol",
           "eval_sha256": {"expected": EVAL_SHA256, "found": sha256(EVAL), "match": True},
           "code_commit": gen["commit"], "search_code_git_status": gen["git_status_search_code"] or "clean",
           "final_setting_r2": gen["final_setting"], "reproduction_checks": gen["checks"],
           "level": "root group: rankings are lists of distinct root-group pairs (lexeme-level counts, deduplicated "
                    "by root group), so hits use pairs_root", "rankings": {}}
    for name in RANKINGS:
        elig = [it for it in primary if eligible(it, name)]
        ranks = {it["item_id"]: item_rank(it, idx[name]) for it in elig}
        block = {"n_ranked_pairs": len(gen["rankings"][name]), "n_eligible": len(elig), "subsets": {}, "baseline": {}}
        for sub in SUBSETS:
            its = [it for it in elig if in_subset(it, sub, name)]
            rr = [ranks[it["item_id"]] for it in its]
            block["subsets"][sub] = recall_block(rr)
            per_seed = [fs.recall_at([item_rank(it, sh_idx[name][s]) for it in its], KS) for s in sh_idx[name]]
            block["baseline"][sub] = {"n": len(its), "seeds": sorted(int(s) for s in sh_idx[name]),
                                      **{f"recall@{k}": {"mean": (round(statistics.mean(p[f"recall@{k}"] for p in per_seed), 3) if its else None),
                                                         "max": (round(max(p[f"recall@{k}"] for p in per_seed), 3) if its else None)}
                                         for k in KS}}
        # per-pair ranks of every eligible item (all its pairs_root), and lexeme-exactness of hits
        block["item_ranks"] = []
        for it in elig:
            prs = []
            for p in it.get("pairs_root") or []:
                q = norm(p) if len(set(p)) == 2 else None
                prs.append({"pair_root": list(p), "rank": idx[name].get(q) if q else None,
                            "ranked_lexeme_pair": list(lexpair[name][q]) if q in lexpair[name] else None,
                            "ranked_lexeme_pair_in_item_pairs": (lexpair[name][q] in {norm(x) for x in it.get("pairs") or []})
                            if q in lexpair[name] else None,
                            **({"rank_unfolded": idx_unf[name].get(q), "folded_into": list(alt_of[name][q]) if q in alt_of[name] else None}
                               if name in idx_unf else {})})
            block["item_ranks"].append({"item_id": it["item_id"], "label": it["label"], "held_out_core": it["held_out_core"],
                                        "verdict": it["verdict"], "corpus_confirmed": in_subset(it, "corpus_confirmed", name),
                                        "best_rank": ranks[it["item_id"]], "pairs": prs})
        hits200 = [x for x in block["item_ranks"] if x["best_rank"] and x["best_rank"] <= 200]
        block["hits_at_200_lexeme_exact"] = sum(any(p["rank"] == x["best_rank"] and p["ranked_lexeme_pair_in_item_pairs"]
                                                    for p in x["pairs"]) for x in hits200)
        block["hits_at_200"] = len(hits200)
        if name in idx_unf:
            unf = {it["item_id"]: item_rank(it, idx_unf[name]) for it in elig}
            block["folding_sensitivity"] = {
                f"@{k}": [iid for iid in ranks if bool(ranks[iid] and ranks[iid] <= k) != bool(unf[iid] and unf[iid] <= k)]
                for k in KS}
            block["unfolded_subsets"] = {sub: recall_block([unf[it["item_id"]] for it in elig if in_subset(it, sub, name)])
                                         for sub in SUBSETS}
        block["top200"] = gen["rankings"][name][:200]
        res["rankings"][name] = block

    # paired comparison R3-c vs R2 on their common eligible items
    common = [it for it in primary if eligible(it, "R2") and eligible(it, "R3-c")]
    res["paired_R3c_minus_R2"] = {}
    for sub in SUBSETS:
        its = [it for it in common if in_subset(it, sub, "R2") and in_subset(it, sub, "R3-c")]
        a = [item_rank(it, idx["R3-c"]) for it in its]
        b = [item_rank(it, idx["R2"]) for it in its]
        res["paired_R3c_minus_R2"][sub] = {"n": len(its), **{f"recall@{k}": fs.paired_bootstrap_diff(a, b, k) for k in KS}}

    # held-out core: best rank per ranking
    core = [it for it in primary if it.get("held_out_core") is True]
    res["held_out_core_items"] = [
        {"item_id": it["item_id"], "label": it["label"], "phrase_branches": it["phrase_branches"],
         **{name: (item_rank(it, idx[name]) or "not ranked") if eligible(it, name) else "not eligible" for name in RANKINGS}}
        for it in core]

    # secondary: other lexical items, eligibility by `branches` (descriptive only)
    sec = {}
    reasons = sorted({r for it in secondary for r in it.get("exclusion_reasons") or []})
    for name in RANKINGS:
        elig = [it for it in secondary if eligible(it, name, "branches")]
        rows = {"all": recall_block([item_rank(it, idx[name]) for it in elig])}
        for rs in reasons:
            its = [it for it in elig if rs in (it.get("exclusion_reasons") or [])]
            rows[rs] = recall_block([item_rank(it, idx[name]) for it in its])
        rows["n_unscoreable_no_two_root_pair"] = sum(1 for it in elig if not any(len(set(p)) == 2 for p in it.get("pairs_root") or []))
        rows["hit_items_at_200"] = [{"item_id": it["item_id"], "label": it["label"], "rank": item_rank(it, idx[name]),
                                     "exclusion_reasons": it["exclusion_reasons"]}
                                    for it in elig if (item_rank(it, idx[name]) or 10 ** 9) <= 200]
        sec[name] = rows
    res["secondary_other_lexical"] = {"n_items": len(secondary), "eligibility_field": "branches", "by_ranking": sec}
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print_tables(res)
    log(f"wrote {OUT_JSON}")
    return 0


def _fmt(b: dict, k: int) -> str:
    v = b[f"recall@{k}"]
    if v is None:
        return "n = 0"
    lo, hi = b["ci95"][f"recall@{k}"]
    return f"{v:.2f} ({lo:.2f}–{hi:.2f}), n = {b['n']}"


def print_tables(res: dict) -> None:
    for name, blk in res["rankings"].items():
        print(f"\n{name}: {blk['n_ranked_pairs']} ranked pairs, {blk['n_eligible']} eligible")
        for sub, b in blk["subsets"].items():
            bl = blk["baseline"][sub]
            print(f"  {sub:18s} " + " | ".join(_fmt(b, k) for k in KS) +
                  "   shuffled mean/max " + " ".join(f"{bl[f'recall@{k}']['mean']}/{bl[f'recall@{k}']['max']}" for k in KS))
    print("\npaired R3-c − R2")
    for sub, d in res["paired_R3c_minus_R2"].items():
        print(f"  {sub:18s} n = {d['n']} " + " ".join(f"@{k} {d[f'recall@{k}']}" for k in KS))
    print("\nheld-out core")
    for x in res["held_out_core_items"]:
        print("  " + json.dumps(x, ensure_ascii=False))
    print("\nsecondary")
    for name, rows in res["secondary_other_lexical"]["by_ranking"].items():
        for sub, b in rows.items():
            if isinstance(b, dict):
                print(f"  {name:5s} {sub:24s} " + " | ".join(_fmt(b, k) for k in KS))


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("generate", "score"):
        print(__doc__)
        return 1
    p = Path(sys.argv[2])
    return generate(p) if sys.argv[1] == "generate" else score(p)


if __name__ == "__main__":
    sys.exit(main())
