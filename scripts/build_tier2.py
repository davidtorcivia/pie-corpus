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


def _norm(w: str) -> str:
    """Daughter word or lemma → comparison key: lowercase, no accents/breathings/length, no hyphens or asterisks."""
    import unicodedata
    d = unicodedata.normalize("NFD", (w or "").lower().strip("*-√ "))
    return "".join(c for c in d if not unicodedata.combining(c)).replace("-", "")


LEX_LANG = {"II": ("Sanskrit", "Vedic", "Avestan", "Persian", "Indo-Aryan", "Iranian", "Pali"),
            "Gk": ("Greek", "Hellenic", "Mycenaean"), "It": ("Latin", "Italic", "Oscan", "Umbrian"),
            "Ce": ("Irish", "Welsh", "Celtic", "Gaulish", "Breton"),
            "Gm": ("Germanic", "Gothic", "Norse", "English", "German", "Saxon", "Icelandic"),
            "BS": ("Slavic", "Slavonic", "Lithuanian", "Latvian", "Prussian", "Russian", "Baltic"),
            "An": ("Hittite", "Luwian", "Anatolian", "Palaic", "Lycian"), "Arm": ("Armenian",),
            "To": ("Tocharian",), "Alb": ("Albanian",)}


def _branch_of(lang: str) -> str:
    return next((b for b, keys in LEX_LANG.items() if any(k in lang for k in keys)), lang)


def secure_check(lid: str, refs: list[dict], lx) -> dict:
    """Which branches of the cited *parallel* refs actually contain a reflex of the lexeme
    (exact: the lexeme's own reflexes; root: only its root's reflexes). A word matches a reflex
    when one normalized key is a prefix of the other (stems vs inflected words), length >= 3."""
    from pie.formula_search import grc_key, grc_roman, ph_to_grc, pii_to_skt, skt_key

    def keys(entry):
        out = {}
        for lang, xs in (entry or {}).get("reflexes", {}).items():
            for x in xs:
                fs = [x.get("form"), x.get("roman")]
                # the PIE pages often stop at the intermediate proto-language: bridge to the daughter
                if lang in ("Proto-Indo-Iranian", "Proto-Indo-Aryan"):
                    fs += pii_to_skt(x.get("form") or "")
                if lang == "Proto-Hellenic":
                    fs += ph_to_grc(x.get("form") or "")
                for f in fs:
                    k = _norm(f)
                    if len(k) >= 3:
                        out.setdefault(_branch_of(lang), set()).add(k)
        return out

    def ref_keys(r):
        ws = r.get("words", []) + r.get("lemmas", [])
        out = {_norm(w) for w in ws}
        b = _branch_of(r.get("lang", ""))
        if b == "Gk":
            out |= {_norm(grc_roman(grc_key(w, accents=False))) for w in ws}
        if b == "II":
            out |= {_norm(skt_key(w)) for w in ws}
        return {k for k in out if len(k) >= 3}
    e = lx.entries.get(lid, {})
    own, root = keys(e), keys(lx.entries.get(e.get("root_id") or "", {}))
    exact, rootlvl = set(), set()
    for r in refs:
        if r.get("role", "parallel") != "parallel":
            continue
        b = _branch_of(r.get("lang", ""))
        cands = ref_keys(r)
        hit = lambda ks: any(c.startswith(k[:max(3, len(k) - 2)]) or k.startswith(c[:max(3, len(c) - 2)])
                             for c in cands for k in ks)
        if hit(own.get(b, set())):
            exact.add(b)
        elif hit(root.get(b, set())):
            rootlvl.add(b)
    return {"exact_branches": sorted(exact), "root_branches": sorted(rootlvl),
            "level": "exact" if len(exact) >= 2 else "root" if len(exact | rootlvl) >= 2 else "none"}


def main() -> int:
    path = Path(sys.argv[1])
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    lx, ix = Lexicon.load(), load_index()
    out, rejects = [], []
    vp = ROOT / "data" / "tier2" / "review_verdicts.json"
    review = json.loads(vp.read_text("utf-8"))["verdicts"] if vp.exists() else {}
    seen_parallels = {}
    for line in path.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        errs = check_plan(p["plan"], lx)
        if branches(p.get("cognate_refs", [])) < 2:
            errs.append("cognate_refs must cite at least two branches")
        if review.get(p.get("proj_id")) == "reject":
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
        checks = {lid: secure_check(lid, p.get("cognate_refs", []), lx) for lid in p.get("secure", [])}
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
            "review": review.get(p.get("proj_id")),
            # evaluation grade: judged sound by the review and with >= 1 lexeme exactly attested in 2 branches
            "eval_grade": review.get(p.get("proj_id")) == "sound" and any(c["level"] == "exact" for c in checks.values()),
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
