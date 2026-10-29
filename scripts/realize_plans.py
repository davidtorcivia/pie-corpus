#!/usr/bin/env python3
"""Check, realize and validate a batch of Tier 3 plans.

  uv run python -I scripts/realize_plans.py data/generation/plans/pilot-fable.jsonl --batch pilot-fable

Plans that fail the checker go to data/generation/rejects/<batch>.jsonl with
their errors. Realized records go to corpus/tier3/<batch>.jsonl, or for a Tier 3b batch (named t3b-<n>,
--tier3b) to corpus/tier3b/<batch>.jsonl with neologism: true, the neologisms loaded into the lexicon and the
validator index (pie/neologism.py), and every clause naming its speaker (docs/generation/planner-brief-3b.md). Warnings (pie.realize.plan_warnings)
are printed as WARN lines and counted in the summary; they never reject a plan.
Gate FAIL returns exit status 1, retaining candidates and reports. Every run
creates pending release metadata; PASS alone does not authorize training export.
"""

import argparse
import collections
import json
import sys
from pathlib import Path

from pie.batch_release import corpus_dir, release_metadata
from pie.meter import measure, record_meter, summary as meter_numbers
from pie.realize import Lexicon, check_plan, plan_warnings, realize, token_cell
from pie.translit import to_ascii
from pie.compound import member_ids
from pie.neologism import coined_sentences, index_neologisms, tier3b_plan_errors, with_neologisms
from pie.validate import all_exact, index_plan_compounds, index_project, load_index, validate_text

ROOT = Path(__file__).resolve().parent.parent
CAP_EXEMPT = {"pie-lex-h1esti"}          # "to be"
# Tier 3b: at most a quarter of the PIE sentences may contain a neologism (t3b-001 review: the pilot had 48/95)
COINED_SENTENCE_MAX = 0.25


def _meter_summary(records: list[dict]) -> dict | None:
    """The original meter_fit report (lines within ±1 of 8 or 11), kept in this shape for older readers."""
    m = [r["meter"] for r in records if r.get("meter")]
    if not m:
        return None
    lines = sum(len(x["line_syllables"]) for x in m)
    return {"lines": lines, "fit": sum(x["fit"] for x in m), "share": round(sum(x["fit"] for x in m) / max(1, lines), 3)}


def _meter_fields(records: list[dict]) -> dict:
    """meter_near (±1, the same number as meter_fit), meter_exact (exactly a target length: the gated number)
    and meter_cadence (the Vedic close of exact lines, information only), over verse lines of metered genres."""
    s = meter_numbers([r["meter"] for r in records if r.get("meter")])
    if s is None:
        return {"meter_near": None, "meter_exact": None, "meter_cadence": None}
    return {"meter_near": {"lines": s["lines"], "near": s["near"], "share": s["near_share"]},
            "meter_exact": {"lines": s["lines"], "exact": s["exact"], "share": s["exact_share"]},
            "meter_cadence": s["cadence"]}


def _formula_uses(records: list[dict]) -> int:
    """Records that use every lexeme of some formula-menu entry."""
    p = ROOT / "data" / "generation" / "formula_menu.json"
    menu = [set(x["lex_id"] for x in m["lexemes"]) for m in json.loads(p.read_text("utf-8"))] if p.exists() else []
    return sum(1 for r in records if any(f <= {t["lex_id"] for t in r["tokens"]} for f in menu))


def lexeme_cap(n_sentences: int, n_tokens: int = 0) -> int:
    """Max uses of one lexeme per batch: 6, or 2% of the records, or 0.5% of the tokens
    (long connected texts have many tokens per record), whichever is largest."""
    return max(6, round(0.02 * n_sentences), round(0.005 * n_tokens))


METER_EXACT_MIN = 0.90          # gate: share of verse lines with exactly 8 or 11 (12 if declared) syllables


def _meter(pie: str, genre: str | None, declared: int | None = None) -> dict | None:
    """Verse genres (pie.meter.METERED_GENRES): syllables per line (a line = a sentence), how many are within
    ±1 of a target (`fit`) and exactly a target (`exact`), and each line's cadence (pie.meter.record_meter)."""
    return record_meter(pie, genre, declared)


def theme_cap(n_sentences: int, n_tokens: int = 0) -> int:
    """Max uses of a slice's declared theme-core lexeme (a hymn to Dawn says "Dawn"): 15, 6% of the
    records, or 1.5% of the tokens."""
    return max(15, round(0.06 * n_sentences), round(0.015 * n_tokens))


def theme_core(batch: str) -> set[str]:
    """Up to 8 lexeme ids a slice declares as its theme core (`theme_core` in the slice file)."""
    p = ROOT / "data" / "generation" / "slices" / f"{batch.removesuffix('-initial')}.json"
    core = json.loads(p.read_text("utf-8")).get("theme_core", []) if p.exists() else []
    return set(core[:8])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", type=Path)
    ap.add_argument("--batch", required=True)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--prompt-id", default="tier3-planner-v1")
    ap.add_argument("--engine-version", default="unknown", help="caller-supplied engine provenance")
    ap.add_argument("--tier3b", action="store_true", help="a Tier 3b ('modern PIE') batch: name it t3b-<n>")
    args = ap.parse_args()
    sha = args.engine_version
    tier3b = args.batch.startswith("t3b-")
    if args.tier3b != tier3b:
        ap.error("Tier 3b batches are named t3b-<n> and run with --tier3b (and only they)")
    lx, ix = Lexicon.load(), load_index()
    index_project(ix)      # Tier 3 may use project reconstructions (tokens carry coined: project)
    if tier3b:             # Tier 3b only: neologisms (coined: neologism); a Tier 3 plan using one is rejected
        lx = with_neologisms(lx)
        index_neologisms(ix)
    plans = [json.loads(x) for x in args.plans.read_text("utf-8").splitlines() if x.strip()]
    records, rejects, stats, warnings = [], [], collections.Counter(), []
    for n, p in enumerate(plans):
        plan = p.get("plan", p)
        errs = check_plan(plan, lx) + (tier3b_plan_errors(plan, lx) if tier3b else [])
        if errs:
            rejects.append({"plan_id": p.get("plan_id", n), "errors": errs, "plan": plan})
            stats["rejected"] += 1
            continue
        warnings += [(p.get("plan_id", n), w) for w in plan_warnings(plan, lx)]   # printed, never a reject
        r = realize(plan, lx)
        index_plan_compounds(ix, plan)          # compounds are open-ended: indexed per plan
        v = validate_text(r["pie"], ix)
        stats["realized"] += 1
        # primary and supported forms only: a legacy match or a known error fails the all_exact gate
        stats["exact_pass"] += all_exact(v)
        # the accent lint's categories (a report, never a gate): unaccented forms of the frozen representation
        # exceptions (voc. ph₂ter) and accent defects; unresolved-accent tokens are counted below by lexeme
        stats["accent_representation_tokens"] += len(v["accent_representation"])
        stats["accent_defect_tokens"] += len(v["accentless"])
        roots = sorted({lx.entries[i].get("root_id") for w in r["words"]
                        for i in [w["lex_id"], *member_ids(w["lex_id"])] if i in lx.entries} - {None})
        records.append({
            "id": f"t3-{args.batch}-{len(records) + 1:05d}",
            "tier": 3, "provenance": "synthetic", "citation": None,
            "work_id": args.batch, "work_group_id": None, "line_no": None,
            "pie": r["pie"], "pie_ascii": to_ascii(r["pie"]), "source_form": None,
            # gender and voice: the resolved cell (pie.export.token_variants offers alternatives of that cell only)
            "tokens": [{"form": w["form"], "lex_id": w["lex_id"],
                        "root_id": lx.entries.get(w["lex_id"], {}).get("root_id"),
                        "features": w["features"], **token_cell(w), "verified": True} for w in r["words"]],
            "gloss": r["gloss"], "english": r["english"],
            "genre": p.get("genre"), "theme": p.get("theme", []),
            "syllables": measure(r["pie"])["syllables"], "meter": _meter(r["pie"], p.get("genre"), p.get("meter")),
            "formulas": [], "cognate_refs": [], "alt_reconstructions": [],
            "validator": {k: v[k] for k in ("status", "coverage", "tiers", "misses")},
            "generator": {"model": args.model, "engine_version": sha, "prompt_id": args.prompt_id,
                          "convention": "handbook", "plan": plan},
            "neologism": tier3b, "roots": roots,
            "notes": "",
        })
    out = ROOT / corpus_dir(args.batch) / f"{args.batch}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), "utf-8")
    (ROOT / "data" / "generation" / "rejects" / f"{args.batch}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rejects), "utf-8")
    roots = {x for r in records for x in r["roots"]}
    # the copula is exempt from the per-lexeme cap; everything else is capped
    uses = collections.Counter(t["lex_id"] for r in records for t in r["tokens"]
                               if not t["lex_id"].startswith("closed:") and t["lex_id"] not in CAP_EXEMPT)
    core = theme_core(args.batch)
    core_uses = {k: v for k, v in uses.items() if k in core}
    uses = collections.Counter({k: v for k, v in uses.items() if k not in core})
    others = set()
    for f in [*(ROOT / "corpus" / "tier3").glob("*.jsonl"), *(ROOT / "corpus" / "tier3b").glob("*.jsonl")]:
        # a batch's own initial run (<batch>-initial) is a draft of the same plans, not another batch
        if f.name != out.name and not f.stem.endswith("-initial"):
            others |= {json.loads(x)["pie"] for x in f.read_text("utf-8").splitlines() if x.strip()}
    pies = [r["pie"] for r in records]
    dup_within = len(pies) - len(set(pies))
    dup_across = sum(1 for p_ in set(pies) if p_ in others)
    n = max(1, len(records))
    summary = {"plans": len(plans), **stats, "reject_rate": round(stats["rejected"] / max(1, len(plans)), 3),
               "distinct_roots": len(roots), "roots_per_sentence": round(len(roots) / n, 3),
               "distinct_lexemes": len(uses), "max_lexeme_uses": max(uses.values(), default=0),
               "most_used": uses.most_common(5), "dup_within": dup_within, "dup_across_batches": dup_across,
               "tokens": sum(len(r["tokens"]) for r in records),
               "words_per_sentence": round(sum(len(r["pie"].split()) for r in records) / n, 2),
               "words_per_record": round(sum(len(r["pie"].split()) for r in records) / n, 2),
               "meter_fit": _meter_summary(records),
               **_meter_fields(records),
               "formula_uses": _formula_uses(records), "warnings": len(warnings)}
    if tier3b:     # how much of the batch is coined vocabulary (PLAN.md caps Tier 3b at 10-15% of training tokens)
        neo = [t["lex_id"] for r in records for t in r["tokens"] if t.get("coined") == "neologism"]
        summary["neologism_tokens"] = {"tokens": len(neo), "share": round(len(neo) / max(1, summary["tokens"]), 3),
                                       "lexemes": len(set(neo))}
        # and how many sentences contain one (brief §1: most contain none; gated at COINED_SENTENCE_MAX)
        cs = [coined_sentences(r["generator"]["plan"], lx) for r in records]
        c, t = sum(x for x, _ in cs), sum(y for _, y in cs)
        summary["coined_sentences"] = {"sentences": t, "coined": c, "share": round(c / max(1, t), 3)}
    # accent: unresolved (missing information: the lexeme's headword has no accent; data/morph/accent_unresolved.json)
    unres = [(r["id"], t["lex_id"]) for r in records for t in r["tokens"] if lx.accent_status(t["lex_id"]) == "unresolved"]
    summary["accent_unresolved"] = {"tokens": len(unres), "lexemes": len({x for _, x in unres}),
                                    "records": len({x for x, _ in unres})}
    # Gates (docs/STATUS.md question 5): the batch passes only on numbers
    gates = {"reject_rate<=0.10": summary["reject_rate"] <= 0.10,
             f"max_lexeme_uses<={lexeme_cap(n, summary['tokens'])}":
                 summary["max_lexeme_uses"] <= lexeme_cap(n, summary["tokens"]),
             f"theme_core_uses<={theme_cap(n, summary['tokens'])}":
                 max(core_uses.values(), default=0) <= theme_cap(n, summary["tokens"]),
             "roots_per_sentence>=0.35": summary["roots_per_sentence"] >= 0.35,
             "duplicates<=2%": (dup_within + dup_across) <= 0.02 * n,
             "all_exact": stats["exact_pass"] == stats["realized"]}
    if tier3b:
        gates[f"coined_sentence_share<={COINED_SENTENCE_MAX:.2f}"] = \
            summary["coined_sentences"]["share"] <= COINED_SENTENCE_MAX
    if summary["meter_exact"] is not None:   # only batches with verse lines in a metered genre
        gates[f"meter_exact>={METER_EXACT_MIN:.2f}"] = summary["meter_exact"]["share"] >= METER_EXACT_MIN
    summary["gates"] = gates
    summary["gate"] = "PASS" if all(gates.values()) else "FAIL"
    (ROOT / "data" / "generation" / "batches").mkdir(exist_ok=True)
    (ROOT / "data" / "generation" / "batches" / f"{args.batch}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", "utf-8")
    # Preserve the exact input plans alongside the candidate. Every realization
    # resets review to pending, including a byte-identical rerun.
    plan_copy = ROOT / "data/generation/plans" / f"{args.batch}.jsonl"
    plan_copy.parent.mkdir(parents=True, exist_ok=True)
    if args.plans.resolve() != plan_copy.resolve():
        plan_copy.write_bytes(args.plans.read_bytes())
    releases = ROOT / "data/generation/releases"
    releases.mkdir(parents=True, exist_ok=True)
    (releases / f"{args.batch}.json").write_text(
        json.dumps(release_metadata(ROOT, args.batch), indent=1) + "\n", "utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    for r in rejects[:10]:
        print("  REJECT", r["plan_id"], r["errors"][:3])
    for pid, w in warnings:
        print("  WARN", pid, w)
    return 0 if summary["gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
