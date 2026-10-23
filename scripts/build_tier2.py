#!/usr/bin/env python3
"""Tier 2 (back-projection): realize projection plans into corpus/tier2/<cluster>.jsonl.

  uv run python -I scripts/build_tier2.py data/tier2/plans/<cluster>.jsonl

A projection plan is a Tier 3 plan (pie/realize.py schema) plus the evidence:
  {"proj_id": "<cluster>-001", "cluster": "dragon-slaying", "theme": [...],
   "plan": {"english": ..., "clauses": [...]},
   "cognate_refs": [{"lang": "Vedic", "locus": "RV 1.32.1", "words": ["áhann", "áhim"],
                     "lemmas": ["han-", "áhi-"]}, ...],
   "secure": ["pie-lex-gwhenti", "pie-lex-h1ogwhis"],   # lexemes with cognates in >= 2 branches in cognate_refs
   "notes": "what is interpolated and why"}
The PIE comes from the engine, never from the planner. A token is `verified`
when its lexeme is in `secure` (attested in at least two branches of the cited
passages) and the validator matches it exactly; everything else is interpolated.
Daughter text is cited by locus and the parallel words only, never quoted at
length (several source corpora are NC-licensed).
"""

import json
import subprocess
import sys
from pathlib import Path

from pie.meter import measure
from pie.realize import Lexicon, check_plan, realize
from pie.translit import to_ascii
from pie.validate import load_index, validate_text

ROOT = Path(__file__).resolve().parent.parent


def branches(refs: list[dict]) -> int:
    fam = {"Vedic": "II", "Sanskrit": "II", "Avestan": "II", "Old Persian": "II", "Greek": "Gk", "Homeric Greek": "Gk",
           "Latin": "It", "Umbrian": "It", "Old Irish": "Ce", "Welsh": "Ce", "Old Norse": "Gm", "Gothic": "Gm",
           "Old English": "Gm", "Old High German": "Gm", "Hittite": "An", "Luwian": "An", "Lithuanian": "BS",
           "Old Church Slavonic": "BS", "Armenian": "Arm", "Tocharian": "To"}
    return len({fam.get(r.get("lang", ""), r.get("lang", "")) for r in refs})


def main() -> int:
    path = Path(sys.argv[1])
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    lx, ix = Lexicon.load(), load_index()
    out, rejects = [], []
    for line in path.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        errs = check_plan(p["plan"], lx)
        if branches(p.get("cognate_refs", [])) < 2:
            errs.append("cognate_refs must cite at least two branches")
        if errs:
            rejects.append({"proj_id": p.get("proj_id"), "errors": errs})
            continue
        r = realize(p["plan"], lx)
        v = validate_text(r["pie"], ix)
        secure = set(p.get("secure", []))
        toks = []
        for w, t in zip(r["words"], v["tokens"]):
            toks.append({"form": w["form"], "lex_id": w["lex_id"],
                         "root_id": lx.entries.get(w["lex_id"], {}).get("root_id"), "features": w["features"],
                         "verified": w["lex_id"] in secure and t.tier == "exact",
                         "interpolated": w["lex_id"] not in secure and not w["lex_id"].startswith("closed:")})
        n_sec = sum(1 for t in toks if t["verified"])
        out.append({
            "id": f"t2-{p['proj_id']}", "tier": 2, "provenance": "back_projection", "citation": None,
            "work_id": f"tier2-{p['cluster']}", "work_group_id": "tier2", "line_no": None,
            "pie": r["pie"], "pie_ascii": to_ascii(r["pie"]), "source_form": None, "tokens": toks,
            "gloss": r["gloss"], "english": r["english"], "genre": "back-projection", "theme": p.get("theme", []),
            "syllables": measure(r["pie"])["syllables"], "meter": None, "formulas": [],
            "cognate_refs": p["cognate_refs"], "alt_reconstructions": [],
            "validator": {k: v[k] for k in ("status", "coverage", "tiers", "misses")},
            "generator": {"engine_version": sha, "plan": p["plan"], "cluster": p["cluster"]},
            "neologism": False, "secure_share": round(n_sec / max(1, len(toks)), 3),
            "branches": branches(p["cognate_refs"]), "notes": p.get("notes", ""),
        })
    d = ROOT / "corpus" / "tier2"
    d.mkdir(parents=True, exist_ok=True)
    cluster = path.stem
    (d / f"{cluster}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
    (ROOT / "data" / "tier2" / "rejects").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "tier2" / "rejects" / f"{cluster}.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rejects), "utf-8")
    print(json.dumps({"cluster": cluster, "lines": len(out), "rejected": len(rejects),
                      "mean_secure_share": round(sum(x["secure_share"] for x in out) / max(1, len(out)), 3),
                      "mean_branches": round(sum(x["branches"] for x in out) / max(1, len(out)), 2)}))
    for r in rejects[:8]:
        print("  REJECT", r["proj_id"], r["errors"][:3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
