"""Build the Classical Armenian (PROIEL + DMHP), Tocharian A and Old Albanian lemma → PIE tables
(Phase 8c, Stage C) and measure their coverage.

  uv run python scripts/build_arm_toch_alb_mapping.py [--only xcl,xto,sqo] [--sample-dir DIR --seed 7]

Writes data/research/formulas/mapping/{xcl,xto,sqo}.jsonl (xcl: PROIEL and DMHP lemmas in one table;
the round-3 script scripts/formula_search.py rewrites xcl.jsonl with PROIEL rows only, so rerun this
script after it) and data/research/formulas/arm-toch-alb-coverage.json. With --sample-dir, a
token-weighted sample of mapped content types per corpus (without replacement: repeated weighted
draws, repeats rejected) for the precision check. Nothing under raw/ is executed; no corpus text is
written (tables hold lemmas, dictionary headwords and ids; samples hold lemmas and counts).
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

from pie import arm_toch_alb_mapping as am  # noqa: E402
from pie import formula_search as fs  # noqa: E402
from pie import formula_search_multi as fm  # noqa: E402

MAPPING_DIR = ROOT / "data/research/formulas/mapping"
COVERAGE = ROOT / "data/research/formulas/arm-toch-alb-coverage.json"


def write_rows(corpus: str, rows: list[dict]):
    (MAPPING_DIR / f"{corpus}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")


def tally(counts: collections.Counter, table: dict) -> dict:
    tot = sum(counts.values())
    mapped = sum(n for t, n in counts.items() if t in table)
    return {"content_tokens": tot, "content_tokens_mapped": mapped, "share": round(mapped / max(1, tot), 4),
            "content_types": len(counts), "content_types_mapped": sum(1 for t in counts if t in table)}


def sample(counts: collections.Counter, table: dict, rows: dict, n: int, seed: int) -> list[dict]:
    """Types are table lemmas (lemmatized corpora) or (surface, lemma) pairs (unlemmatized ones)."""
    lem = (lambda t: t[1]) if counts and isinstance(next(iter(counts)), tuple) else (lambda t: t)
    types = sorted(t for t in counts if lem(t) in table)
    w = [counts[t] for t in types]
    rng = random.Random(seed)
    got, seen = [], set()
    while len(got) < min(n, len(types)):
        x = rng.choices(types, w)[0]
        if x in seen:
            continue
        seen.add(x)
        got.append({"type": x[0] if isinstance(x, tuple) else x, "lemma": lem(x), "tokens": counts[x],
                    "lex_id": list(table[lem(x)]), "row": rows.get(lem(x))})
    return got


def build_xcl(lex, gmap, out: dict, samples: dict):
    t0 = time.time()
    b = am.build_xcl(lex)
    proiel_all = am.proiel_lemmas()
    conv = am.DmhpLemma(proiel_all)
    dt = am.dmhp_tokens()
    dmhp: dict = collections.defaultdict(collections.Counter)
    dm_content, dm_names = collections.Counter(), collections.Counter()
    dm_by_text: dict = collections.defaultdict(collections.Counter)
    for t in dt:
        s = conv(t.lemma)
        dmhp[s][t.lemma] += 1
        if t.content:
            dm_content[s] += 1
            dm_by_text[t.text][s] += 1
        elif t.name:
            dm_names[s] += 1
    rows = am.xcl_rows(b, proiel_all, dmhp, gmap)
    write_rows("xcl", rows)
    table = fm.apply_table_overrides("xcl", {r["lemma"]: tuple(r["lex_id"]) for r in rows})
    pc = collections.Counter(t.lemma for t in fm.load_proiel(["proiel/armenian-nt.xml"], "xcl") if t.content)
    out["xcl"] = {"rows": len(rows), "changed_by_rule": dict(collections.Counter(b.changed.values())),
                  "dmhp": tally(dm_content, table), "dmhp_names": tally(dm_names, table), "proiel": tally(pc, table),
                  "dmhp_by_text": {k: tally(v, table) for k, v in sorted(dm_by_text.items())}}
    samples["xcl-dmhp"] = (dm_content, table, {r["lemma"]: r for r in rows})
    samples["xcl-proiel"] = (pc, table, {r["lemma"]: r for r in rows})
    print(f"xcl: {len(rows)} rows; DMHP {out['xcl']['dmhp']['share']:.3f}, PROIEL {out['xcl']['proiel']['share']:.3f} "
          f"({time.time() - t0:.0f}s)")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="xcl,xto,sqo")
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--all-dump", type=Path, default=None,
                    help="extract of the kaikki all-languages dump (lines of sqj-pro / ine-toc-pro), else read the .gz")
    a = ap.parse_args(argv)
    lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
    gmap = fs.group_map(lex)
    only = set(a.only.split(","))
    out = json.loads(COVERAGE.read_text("utf-8")) if COVERAGE.exists() else {}
    samples: dict = {}
    if "xcl" in only:
        build_xcl(lex, gmap, out, samples)
    if "xto" in only:
        am.build_xto_tables(lex, gmap, out, samples, ROOT, a.all_dump, write_rows)
    if "sqo" in only and hasattr(am, "build_sqo_tables"):
        am.build_sqo_tables(lex, gmap, out, samples, ROOT, a.all_dump, write_rows)
    COVERAGE.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", "utf-8")
    if a.sample_dir:
        a.sample_dir.mkdir(parents=True, exist_ok=True)
        for c, (counts, table, rows) in samples.items():
            got = sample(counts, table, rows, a.n, a.seed)
            p = a.sample_dir / f"mapata-sample-{c}-seed{a.seed}.jsonl"
            p.write_text("".join(json.dumps(g, ensure_ascii=False) + "\n" for g in got), "utf-8")
            print(f"sample {c}: {len(got)} → {p}")


if __name__ == "__main__":
    main()
