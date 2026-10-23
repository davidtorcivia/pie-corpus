#!/usr/bin/env python3
"""Build a lexicon slice for a Tier 3 planning batch: usable, glossed lexemes
chosen by gloss keywords for the genre/theme, plus a core of common verbs,
with the features each lexeme actually has.

  uv run python -I scripts/make_slice.py fable --keywords sheep horse wolf dog cow wool field --size 220
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

from pie.realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent
CORE_VERBS = ["be", "see", "carry", "give", "speak", "say", "go", "come", "know", "eat", "drink", "hear",
              "sit", "stand", "lead", "drive", "kill", "slay", "live", "fear", "seek", "protect", "milk",
              "plough", "walk", "arrive", "seize", "burn", "lie", "put", "become", "split", "cover"]
CLOSED = {
    "closed:personal/1": "I / we (num SG|PL); enclitic forms with \"enclitic\": true",
    "closed:personal/2": "you (num SG|PL); enclitic forms with \"enclitic\": true",
    "closed:demonstrative_so": "this/that, the (MOD with head, or as a pronoun: he/she/it)",
    "closed:relative_yo": "who/which (relative)",
    "closed:interrogative_kwo": "who? which? (m/f/n by head)",
    "closed:interrogative_kwi": "who? what? (kʷís, kʷíd)",
}


def verb_features(cells: dict) -> list[str]:
    feats = set()
    for k in cells:
        parts = k.split(".")
        voice = "MID" if parts[0] == "MID" else "ACT"
        if parts[0] == "MID":
            parts = parts[1:]
        if parts[0] in ("PRS", "PST", "AOR", "PRF"):
            feats.add(f"IND {parts[0]} {voice}")
        elif parts[0] in ("IMP", "SBJV", "OPT"):
            feats.add(f"{parts[0]} {voice}")
    return sorted(feats)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--size", type=int, default=220)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    lx = Lexicon.load()
    rng = random.Random(args.seed)
    pool = [i for i, r in lx.specs.items() if r.get("usable") and lx.entries[i]["meaning"]]

    def hits(i, words):
        g = " " + re.sub(r"[^a-z]+", " ", lx.entries[i]["meaning"][0].lower()) + " "
        return any(f" {w} " in g for w in words)

    chosen = [i for i in pool if hits(i, args.keywords)]
    chosen += [i for i in pool if lx.specs[i]["family"] == "verb" and hits(i, CORE_VERBS) and i not in chosen]
    rest = [i for i in pool if i not in chosen]
    rng.shuffle(rest)
    chosen += rest[: max(0, args.size - len(chosen))]
    items = []
    for i in chosen[: max(args.size, len(chosen))]:
        e, r = lx.entries[i], lx.specs[i]
        item = {"lex_id": i, "form": e["form"], "gloss": e["meaning"][0][:80], "family": r["family"]}
        if r["family"] == "noun":
            item["gender"] = lx.gender(i)
        if r["family"] == "verb":
            item["features"] = verb_features(lx.cells(i))
        items.append(item)
    out = ROOT / "data" / "generation" / "slices" / f"{args.name}.json"
    out.write_text(json.dumps({"name": args.name, "keywords": args.keywords, "closed": CLOSED, "lexemes": items},
                              ensure_ascii=False, indent=1) + "\n", "utf-8")
    fam = {}
    for it in items:
        fam[it["family"]] = fam.get(it["family"], 0) + 1
    print(f"{out}: {len(items)} lexemes {fam}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
