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
from pie.tier2_secure import SecureChecker, plan_compound_ids
from pie.translit import to_ascii
from pie.validate import index_plan_compounds, load_index, validate_text

ROOT = Path(__file__).resolve().parent.parent


def branches(refs: list[dict]) -> int:
    fam = {"Vedic": "II", "Sanskrit": "II", "Avestan": "II", "Old Persian": "II", "Greek": "Gk", "Homeric Greek": "Gk",
           "Latin": "It", "Umbrian": "It", "Old Irish": "Ce", "Welsh": "Ce", "Old Norse": "Gm", "Gothic": "Gm",
           "Old English": "Gm", "Old High German": "Gm", "Hittite": "An", "Luwian": "An", "Lithuanian": "BS",
           "Old Church Slavonic": "BS", "Armenian": "Arm", "Tocharian": "To",
           "Latvian": "BS", "Old Prussian": "BS", "Russian": "BS", "Old Russian": "BS", "Czech": "BS", "Polish": "BS",
           "Middle Irish": "Ce", "Gaulish": "Ce", "Celtiberian": "Ce", "Old Welsh": "Ce", "Middle Welsh": "Ce",
           "Old Saxon": "Gm", "Old Frisian": "Gm", "Middle High German": "Gm", "Old Icelandic": "Gm",
           "Pali": "II", "Middle Persian": "II", "Old Avestan": "II", "Young Avestan": "II", "Sanskrit (Epic)": "II",
           "Mycenaean Greek": "Gk", "Oscan": "It", "Faliscan": "It", "Palaic": "An", "Lycian": "An",
           "Tocharian A": "To", "Tocharian B": "To", "Albanian": "Alb", "Phrygian": "Phr", "Messapic": "Mes"}
    return len({fam.get(r.get("lang", ""), r.get("lang", "")) for r in refs})


def secure_check(lid: str, refs: list[dict], checker) -> dict:
    """Which branches of the cited *parallel* refs contain a reflex of the lexeme: exact (the lexeme
    itself), root (only its root or a sibling formation), with the evidence path per branch. The rules
    (mapping tables, whole-word reflex equality, compounds member by member) are in pie/tier2_secure.py."""
    return checker.check(lid, refs)


def checks_for(p: dict, checker) -> dict:
    """secure_checks of a plan: every claimed lexeme, plus every compound slot whose compound or one of
    whose members is claimed (a compound is exact only if both members are exact in the same word)."""
    claimed = list(p.get("secure", []))
    for cid, first, second in plan_compound_ids(p["plan"]):
        if cid not in claimed and ({first, second} & set(claimed)):
            claimed.append(cid)
    return {lid: secure_check(lid, p.get("cognate_refs", []), checker) for lid in claimed}


def plan_sha(p: dict) -> str:
    import hashlib
    key = {k: p.get(k) for k in ("plan", "cognate_refs", "secure")}
    return hashlib.sha256(json.dumps(key, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def main() -> int:
    path = Path(sys.argv[1])
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    lx, ix = Lexicon.load(), load_index()
    checker = SecureChecker.from_disk(lx.entries)
    out, rejects = [], []
    vp = ROOT / "data" / "tier2" / "review_verdicts.json"
    raw_review = json.loads(vp.read_text("utf-8"))["verdicts"] if vp.exists() else {}

    def verdict(p):
        """The review's verdict while the plan is the one reviewed; 'stale' once it was revised."""
        v = raw_review.get(p.get("proj_id"))
        if not v:
            return None
        if isinstance(v, str):
            return v
        return v["verdict"] if v.get("plan_sha") == plan_sha(p) else "stale"
    seen_parallels = {}
    for line in path.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        errs = check_plan(p["plan"], lx)
        if branches(p.get("cognate_refs", [])) < 2:
            errs.append("cognate_refs must cite at least two branches")
        rv = raw_review.get(p.get("proj_id"))
        if (rv.get("verdict") if isinstance(rv, dict) else rv) == "reject":   # a rejected parallel stays out
            errs.append("rejected by the adversarial review (docs/audits/tier2-review.md)")
        # one line per parallel: the same set of cited loci is the same parallel (review: duplication)
        par = tuple(sorted(x.get("locus", "") for x in p.get("cognate_refs", []) if x.get("role", "parallel") == "parallel"))
        if not errs and par in seen_parallels:
            errs.append(f"duplicate parallel of {seen_parallels[par]}")
        if errs:
            rejects.append({"proj_id": p.get("proj_id"), "errors": errs})
            continue
        seen_parallels[par] = p.get("proj_id")
        r = realize(p["plan"], lx)
        index_plan_compounds(ix, p["plan"])     # compounds are open-ended: indexed per plan
        v = validate_text(r["pie"], ix)
        # 'secure' is the planner's claim; keep only lexemes whose reflexes really stand in the cited
        # parallel passages of >= 2 branches (tier2 review: secure_share was unreliable)
        checks = checks_for(p, checker)
        secure = {lid for lid, c in checks.items() if c["level"] == "exact"}
        root_level = {lid for lid, c in checks.items() if c["level"] == "root"}
        toks = []
        for w, t in zip(r["words"], v["tokens"]):
            toks.append({"form": w["form"], "lex_id": w["lex_id"],
                         "root_id": lx.entries.get(w["lex_id"], {}).get("root_id"), "features": w["features"],
                         "verified": w["lex_id"] in secure and t.tier == "exact",
                         "secure_level": "exact" if w["lex_id"] in secure else "root" if w["lex_id"] in root_level else None,
                         "interpolated": w["lex_id"] not in secure})
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
            "branches": branches([x for x in p["cognate_refs"] if x.get("role", "parallel") == "parallel"]),
            "secure_checks": checks, "claimed_secure": sorted(p.get("secure", [])), "notes": p.get("notes", ""),
            "review": verdict(p),
            # evaluation grade: judged sound by the review and with >= 1 lexeme exactly attested in 2 branches
            "eval_grade": verdict(p) == "sound" and any(c["level"] == "exact" for c in checks.values()),
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
                      "mean_branches": round(sum(x["branches"] for x in out) / max(1, len(out)), 2),
                      "eval_grade": sum(1 for x in out if x["eval_grade"])}))
    for r in rejects[:8]:
        print("  REJECT", r["proj_id"], r["errors"][:3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
