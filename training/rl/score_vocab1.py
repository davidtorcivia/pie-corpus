"""Vocabulary pilot score: on held-out sentences (make_vocab1.py's test.jsonl, never trained), does the answer use the
target word? A written word counts when the analyzer reads it as a form of the target lexeme (exactly or but for an
accent). Trained words and control words apart; with passrate.jsonl dirs, the bare vocabulary prompts' never /
sometimes / always counts too.

    uv run --group translator python -I training/rl/score_vocab1.py GEN.jsonl [GEN2.jsonl ...] [--pass DIR ...]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
TEST = Path("/Users/david/AI/pie-runs/rl/data/vocab1/test.jsonl")


def uses(an, text, lid):
    for w in text.split():
        hits, how = an.word(w.split("-")[0])
        if how in ("exact", "unaccented") and any(h.lex_id == lid for h in hits):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gens", nargs="*")
    ap.add_argument("--pass", dest="passes", nargs="*", default=[])
    a = ap.parse_args()
    from pie.translator.analyze import Analyzer
    an = Analyzer.load()
    test = {x["id"]: x for x in map(json.loads, TEST.read_text("utf-8").splitlines())}
    for g in a.gens:
        c = collections.Counter()
        for x in map(json.loads, Path(g).read_text("utf-8").splitlines()):
            t = test[x["id"]]
            k = "control" if t["control"] else "trained"
            c[k] += 1
            c[k + "_hit"] += uses(an, x["output"], t["lex_id"])
        print(Path(g).name, {k: f"{c[k + '_hit']}/{c[k]} = {c[k + '_hit'] / max(c[k], 1):.3f}" for k in ("trained", "control")})
    for d in a.passes:
        c = collections.Counter()
        for r in map(json.loads, (Path(d) / "passrate.jsonl").read_text("utf-8").splitlines()):
            m = sum(r["scores"]) / len(r["scores"])
            c["always" if m > 0.8 else "never" if m == 0 else "sometimes"] += 1
        print(d, dict(c))


if __name__ == "__main__":
    main()
