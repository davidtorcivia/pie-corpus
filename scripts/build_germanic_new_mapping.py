"""Stage C Germanic lemma → PIE tables (pie/germanic_new_mapping.py).

Writes data/research/formulas/mapping/{menota,icepahc,rea-goh,rea-osx}.jsonl
(the round-3 table format plus `licence` and `research_only`; one row per
mapped corpus lemma string, as the loaders of germanic_new_mapping yield it)
and data/research/formulas/germanic-new-coverage.json (content-token
coverage per corpus, per source document for Menota, and for the IcePaHC
files after 1400). The overrides in
data/research/formulas/mapping-overrides/germanic-new.json are applied
('proto' rows while resolving, 'lemma' rows on the lemma strings).

With --sample-dir DIR --seed S it also writes DIR/mapgmc-sample-<S>.json: per
corpus, 100 mapped content types drawn with token-frequency weights
(Efraimidis–Spirakis keys u ** (1 / count), u from sha256("S:lemma"), so a
redraw after corrections keeps the items whose mapping survives).

    uv run python scripts/build_germanic_new_mapping.py [--cache DIR] [--sample-dir DIR --seed 7]

--cache DIR keeps the Icelandic / Proto-West-Germanic / Proto-Norse entries
cut from the all-languages kaikki dump (else they are streamed, ≈1 min).
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pie import germanic_new_mapping as gm  # noqa: E402

COVERAGE = ROOT / "data/research/formulas/germanic-new-coverage.json"


def sample_key(seed: int, lemma: str, n: int) -> float:
    h = hashlib.sha256(f"{seed}:{lemma}".encode()).digest()
    u = (int.from_bytes(h[:8], "big") + 1) / (2 ** 64 + 2)
    return u ** (1 / n)


def coverage(toks, recs) -> dict:
    cont = [t for t in toks if t.content]
    lem = collections.Counter(t.lemma for t in cont)
    mapped = {l for l in lem if l in recs}
    n_m = sum(lem[l] for l in mapped)
    conf = collections.Counter(recs[t.lemma].confidence for t in cont if t.lemma in recs)
    lexeme = sum(1 for t in cont if t.lemma in recs and any(not x.startswith("pie-root-") for x in recs[t.lemma].ids))
    return {"tokens": len(toks), "content_tokens": len(cont), "content_tokens_mapped": n_m,
            "content_token_share": round(n_m / max(1, len(cont)), 4), "content_types": len(lem),
            "content_types_mapped": len(mapped), "type_share": round(len(mapped) / max(1, len(lem)), 4),
            "mapped_tokens_by_confidence": dict(conf),
            "mapped_tokens_lexeme_level_share": round(lexeme / max(1, n_m), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path)
    ap.add_argument("--sample-dir", type=Path)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    t0 = time.time()
    maps = gm.build_mappings(ROOT, cache=a.cache)
    print(f"mappings: non {len(maps.non.recs)}, goh {len(maps.goh.recs)}, osx {len(maps.osx.recs)} keys "
          f"({time.time() - t0:.0f}s)", flush=True)
    rea = gm.rea_tokens(ROOT)
    toks = {"menota": gm.load_menota(ROOT), "icepahc": gm.load_icepahc(ROOT, max_year=None),
            "rea-goh": gm.load_rea("rea-goh", ROOT, rows=rea), "rea-osx": gm.load_rea("rea-osx", ROOT, rows=rea)}
    cov, samples = {}, {}
    for c, ts in toks.items():
        recs, steps = gm.corpus_recs(maps, c, [t.lemma for t in ts], root=ROOT, names=gm.name_lemmas(ts))
        p = gm.write_table(c, recs, ROOT)
        print(f"{c}: {len(recs)} lemma rows -> {p.relative_to(ROOT)}", flush=True)
        if c == "icepahc":
            early = [t for t in ts if int(t.units["text"][:4]) <= 1400]
            cov[c] = coverage(early, recs)
            cov[c]["note"] = "files dated <= 1400 (the Old Icelandic part); 'all_years' covers 1150-2008"
            cov[c]["all_years"] = coverage(ts, recs)
        else:
            cov[c] = coverage(ts, recs)
        if c == "menota":
            by_src = collections.defaultdict(list)
            for t in ts:
                by_src[t.units["lemma_source"] if t.units["lemma_source"] == "corpus" else "form-table"].append(t)
            cov[c]["by_lemma_source"] = {k: coverage(v, recs) for k, v in by_src.items()}
        base = early if c == "icepahc" else ts
        cov[c]["steps_by_mapped_tokens"] = dict(collections.Counter(
            (steps.get(t.lemma) or "") for t in base if t.content and t.lemma in recs).most_common(15))
        cov[c]["licence"] = gm.CORPORA[c]["licence"]
        if a.sample_dir:
            sel = [t for t in ts if t.content] if c != "icepahc" else \
                [t for t in ts if t.content and int(t.units["text"][:4]) <= 1400]
            cnt = collections.Counter(t.lemma for t in sel if t.lemma in recs)
            gl = collections.defaultdict(collections.Counter)
            for t in sel:
                if t.lemma in cnt and t.units.get("gloss"):
                    gl[t.lemma][t.units["gloss"]] += 1
            keys = sorted(cnt, key=lambda l: -sample_key(a.seed, l, cnt[l]))[:100]
            samples[c] = [{"lemma": l, "tokens": cnt[l], "gloss": [g for g, _ in gl[l].most_common(2)],
                           "row": gm.table_rows(c, {l: recs[l]})[0]} for l in keys]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"coverage -> {COVERAGE.relative_to(ROOT)}")
    for c, v in cov.items():
        print(f"  {c}: {v['content_tokens_mapped']}/{v['content_tokens']} content tokens mapped "
              f"({100 * v['content_token_share']:.1f}%), {v['content_types_mapped']} types")
    if a.sample_dir:
        a.sample_dir.mkdir(parents=True, exist_ok=True)
        out = a.sample_dir / f"mapgmc-sample-{a.seed}.json"
        out.write_text(json.dumps(samples, ensure_ascii=False, indent=1) + "\n", "utf-8")
        print(f"sample -> {out}")
    print(f"done ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
