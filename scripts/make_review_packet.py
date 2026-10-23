#!/usr/bin/env python3
"""Calibrated review packets: we have no human expert, so reviewers are
measured on errors we planted.

  uv run python -I scripts/make_review_packet.py t001 --n 40 --plants 8 --tier1 4

Writes docs/audits/packets/<batch>-packet.jsonl (what the reviewer sees:
pie, english, genre; ids are opaque; no gloss, which would reveal plants) and
data/audits/keys/<batch>-key.json (which items are planted, with the
corruption, and which are Tier 1 scholarly lines). The reviewer must not
read data/audits/. A plant replaces one word of a real record with another
cell of the same lexeme's paradigm: a wrong case or number for a noun,
wrong gender agreement for an adjective, wrong person or number for a verb.
Scoring: scripts/score_review.py compares the reviewer's verdicts with the
key (recall on plants, verdicts on Tier 1 lines, wrong rate on the rest).
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

from pie.realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent


def corrupt(rec: dict, lx: Lexicon, rng: random.Random) -> tuple[dict, dict] | None:
    toks = [(i, t) for i, t in enumerate(rec["tokens"]) if t["lex_id"] in lx.specs and t.get("features")]
    rng.shuffle(toks)
    for i, t in toks:
        fam = lx.specs[t["lex_id"]]["family"]
        feat = t["features"] if isinstance(t["features"], str) else t["features"][0]
        try:
            if fam == "noun":
                cells = lx.cells(t["lex_id"])
            elif fam == "adj":
                g = rng.choice([x for x in ("m", "f", "n")])
                cells = lx.cells(t["lex_id"], g)
            else:
                cells = lx.cells(t["lex_id"])
        except Exception:
            continue
        cur = t["form"]
        if fam == "verb":
            alts = [k for k in cells if k.rsplit(".", 1)[0] == feat.rsplit(".", 1)[0] and k != feat]
        else:
            alts = [k for k in cells if k != feat]
        alts = [k for k in alts if cells[k] and cells[k][0] != cur]
        if not alts:
            continue
        k = rng.choice(alts)
        new = cells[k][0]
        words = rec["pie"].split()
        hit = next((j for j, w in enumerate(words) if w.strip(".,?!").split("-")[0] == cur), None)
        if hit is None:
            continue
        words[hit] = words[hit].replace(cur, new, 1)
        out = {**rec, "pie": " ".join(words)}
        return out, {"token": cur, "replaced_by": new, "true_feature": feat, "planted_feature": k, "family": fam}
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--plants", type=int, default=8)
    ap.add_argument("--tier1", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    lx = Lexicon.load()
    recs = [json.loads(x) for x in (ROOT / "corpus/tier3" / f"{args.batch}.jsonl").read_text("utf-8").splitlines()]
    sample = rng.sample(recs, min(args.n, len(recs)))
    items, key = [], {}
    for r in sample:
        items.append(("real", r, None))
    planted = 0
    for r in rng.sample(recs, len(recs)):
        if planted >= args.plants:
            break
        if any(r["id"] == s["id"] for s in sample):
            continue
        c = corrupt(r, lx, rng)
        if c:
            items.append(("plant", c[0], c[1]))
            planted += 1
    t1 = [json.loads(x) for f in sorted((ROOT / "corpus/tier1").glob("*.jsonl")) for x in f.read_text("utf-8").splitlines()]
    t1 = [r for r in t1 if r.get("pie") and r.get("english") and r["provenance"] == "scholarly"]
    for r in rng.sample(t1, min(args.tier1, len(t1))):
        items.append(("tier1", r, None))
    rng.shuffle(items)
    out = []
    for n, (kind, r, info) in enumerate(items):
        pid = hashlib.sha256(f"{args.batch}{args.seed}{n}".encode()).hexdigest()[:8]
        # no interlinear gloss: it describes the original words, so it would give the plants away
        out.append({"item": pid, "pie": r["pie"], "english": r.get("english"), "genre": r.get("genre")})
        key[pid] = {"kind": kind, "source_id": r["id"], "corruption": info}
    pd = ROOT / "docs" / "audits" / "packets"
    kd = ROOT / "data" / "audits" / "keys"
    pd.mkdir(parents=True, exist_ok=True)
    kd.mkdir(parents=True, exist_ok=True)
    (pd / f"{args.batch}-packet.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
    (kd / f"{args.batch}-key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{len(out)} items ({len(sample)} real, {planted} planted, {sum(1 for k in key.values() if k['kind'] == 'tier1')} "
          f"Tier 1) → {pd / (args.batch + '-packet.jsonl')}; key → {kd / (args.batch + '-key.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
