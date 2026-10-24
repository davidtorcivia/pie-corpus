#!/usr/bin/env python3
"""The resolved word → PIE mapping population (pie.mapping.iter_resolved), for mapping-precision audits.

  uv run python -I scripts/mapping_population.py                       # counts per corpus and status
  uv run python -I scripts/mapping_population.py --corpus hit --sample 100 --seed 7 [--weights counts.json]

This is the population the Tier 2 secure checker reads (pie.tier2_secure.load_population): the tables in
data/research/formulas/mapping/ with every reviewed override applied, the lemmas only an override maps
included (status 'added'), removed lemmas left out, uncertain rows flagged. --weights takes a JSON
{lemma: token count} for a frequency-weighted sample (weighted sampling without replacement); without
it the sample is uniform. Sampled rows are printed as JSON lines.
"""

import argparse
import collections
import json
import random
import sys

from pie import mapping as mp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", action="append")
    ap.add_argument("--sample", type=int)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--weights")
    a = ap.parse_args()
    rows = list(mp.iter_resolved(corpora=set(a.corpus) if a.corpus else None))
    if not a.sample:
        c = collections.Counter((x.corpus, x.status) for x in rows)
        unc = collections.Counter(x.corpus for x in rows if x.uncertain)
        for corpus in sorted({x.corpus for x in rows}):
            st = {s: n for (cc, s), n in sorted(c.items()) if cc == corpus}
            print(json.dumps({"corpus": corpus, "resolved": sum(st.values()), **st, "uncertain": unc[corpus]}))
        return 0
    rng = random.Random(a.seed)
    if a.weights:
        w = json.loads(open(a.weights, encoding="utf-8").read())
        pool = [(x, float(w.get(x.lemma, 0))) for x in rows if w.get(x.lemma, 0) > 0]
        keyed = sorted(pool, key=lambda p: rng.random() ** (1.0 / p[1]), reverse=True)    # Efraimidis-Spirakis
        pick = [x for x, _ in keyed[: a.sample]]
    else:
        pick = rng.sample(rows, min(a.sample, len(rows)))
    for x in pick:
        print(json.dumps({"corpus": x.corpus, "lemma": x.lemma, "word": x.word, "lex_id": sorted(x.ids),
                          "status": x.status, "how": x.how, "formation": x.formation, "uncertain": x.uncertain,
                          "path": list(x.path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
