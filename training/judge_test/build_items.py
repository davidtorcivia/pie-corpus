"""Judge test set: 60 items from approved Tier 3 dialogue batches (t089-t109), English + PIE. 24 left as they are,
12 with one inflection planted (make_review_packet.corrupt), 12 with one noun or verb swapped for another lexeme in
the same cell (a meaning error that still parses), 12 with the negation removed. Writes items.jsonl (what judges
see) and key.json (kept out of the judges' reach)."""
import json
import random
import sys
from pathlib import Path

ROOT = Path("/Users/david/AI/PIE")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from make_review_packet import corrupt  # noqa: E402
from pie.realize import Lexicon  # noqa: E402

OUT = Path(__file__).resolve().parent
rng = random.Random(20261031)
lx = Lexicon.load()
recs = []
for b in range(89, 110):
    p = ROOT / f"corpus/tier3/t{b:03d}.jsonl"
    recs += [json.loads(x) for x in p.read_text("utf-8").splitlines() if x.strip()]
recs = [r for r in recs if 15 <= len(r["pie"].split()) <= 45]
rng.shuffle(recs)


def swap(rec):
    toks = [t for t in rec["tokens"] if t["lex_id"] in lx.specs and t.get("features")
            and lx.specs[t["lex_id"]]["family"] in ("noun", "verb")]
    rng.shuffle(toks)
    pool = {f: [l for l, s in lx.specs.items() if s.get("usable") and s["family"] == f and lx.entries[l]["meaning"]]
            for f in ("noun", "verb")}
    for t in toks:
        fam = lx.specs[t["lex_id"]]["family"]
        feat = t["features"] if isinstance(t["features"], str) else t["features"][0]
        for _ in range(30):
            other = rng.choice(pool[fam])
            if other == t["lex_id"]:
                continue
            try:
                cells = lx.cells(other)
            except Exception:
                continue
            if fam == "noun" and lx.entries[other].get("gender") != lx.entries[t["lex_id"]].get("gender"):
                continue
            if cells.get(feat):
                new = cells[feat][0]
                words = rec["pie"].split()
                hit = next((j for j, w in enumerate(words) if w.strip(".,?!\"").split("-")[0] == t["form"]), None)
                if hit is None:
                    break
                words[hit] = words[hit].replace(t["form"], new, 1)
                return {**rec, "pie": " ".join(words)}, {"token": t["form"], "replaced_by": new,
                                                         "meaning": lx.entries[t["lex_id"]]["meaning"][:60],
                                                         "new_meaning": lx.entries[other]["meaning"][:60]}
    return None


def unnegate(rec):
    words = rec["pie"].split()
    hits = [j for j, w in enumerate(words) if w.strip(".,?!\"").lower() in ("né", "ne", "mḗ", "mē")]
    if not hits:
        return None
    j = rng.choice(hits)
    tail = words[j][len(words[j].rstrip(".,?!\"")):]
    del words[j]
    if tail and j > 0:
        words[j - 1] += tail
    return {**rec, "pie": " ".join(words)}, {"removed": "negation", "position": j}


plan = ["ok"] * 24 + ["inflection"] * 12 + ["lexeme"] * 12 + ["negation"] * 12
rng.shuffle(plan)
items, key, used = [], {}, set()
for kind in plan:
    for r in recs:
        if r["id"] in used:
            continue
        if kind == "ok":
            got = (r, {})
        elif kind == "inflection":
            got = corrupt(r, lx, rng)
        elif kind == "lexeme":
            got = swap(r)
        else:
            got = unnegate(r)
        if got:
            used.add(r["id"])
            iid = f"J{len(items) + 1:02d}"
            items.append({"id": iid, "english": r["english"], "pie": got[0]["pie"]})
            key[iid] = {"kind": kind, "record": r["id"], **got[1]}
            break
(OUT / "items.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), "utf-8")
(OUT / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), "utf-8")
(OUT / "held_records.json").write_text(json.dumps(sorted(used)), "utf-8")
print(len(items), {k: sum(v["kind"] == k for v in key.values()) for k in ("ok", "inflection", "lexeme", "negation")})
