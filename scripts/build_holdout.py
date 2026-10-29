#!/usr/bin/env python3
"""Select the benchmark hold-out: write data/export/protected_roots.json and data/export/held_roots.json
(read by pie.holdout; pie.export.eval_root is the one predicate make_slice, export and the tests use).

  uv run python -I scripts/build_holdout.py            # write both files and print the comparison
  uv run python -I scripts/build_holdout.py --dry-run  # print only

Protected set (never held out), derived from the data; each family keeps its reasons:
  formula-menu     the lexemes of data/generation/formula_menu.json
  formula          the words of data/formulas/formulas.jsonl, mapped to lexemes as
                   scripts/build_formula_menu.py maps them (validator index, found words, no near-misses, the initial
                   laryngeal the books omit), and the verified tokens of corpus/tier1/formulas.jsonl
  tier2-secure     Tier 2 tokens with secure_level exact or root (corpus/tier2)
  core-noun, core-verb, conversation
                   make_slice's CORE_NOUNS and CONVERSATION ids, and its CORE_VERBS keywords resolved
                   as make_slice resolves them (usable verb, whole-word gloss hit, trusted gloss)
  numeral          every lexicon entry with pos "num"
  swadesh:kin|body|nature
                   usable nouns with a trusted gloss one of whose sense segments is a Swadesh-type
                   concept word (SWADESH below: the one hand-written list; the lexemes are found from
                   the glosses)
A lexeme without a root_id belongs to no family and cannot be held out; it is counted, not listed.

Hold-out (selection, deterministic):
  universe  every root family of the lexicon (Lexicon.load(): the root_ids of its entries)
  pool      universe − protected − families used anywhere in Tier 3/3b records (admitted or not),
            non-eval Tier 2 records, Tier 2 and Tier 3 plans, and planner slices, so no record
            already trained (or planned under the old hold-out) touches a held family
  strata    (task-bearing: the family has an inflection or cognate task) × (branches with an
            inherited reflex: 0, 1-2, 3-4, 5+) × (root_type verbal / nominal), so the new set matches
            the old one's difficulty mix
  quota     N = round(SHARE × |universe|), split over the strata in the proportions of the old
            hash draw (sha256(root_id) < SHARE over the universe), largest remainder
  ranking   inside each stratum, ascending sha256(root_id)[:8] (pie.holdout.hash_rank)
Re-running after the corpus grows selects a different set; the files are frozen on purpose. Do
not re-run to "refresh" them: benchmark scores across hold-outs are not comparable.
"""

import argparse
import collections
import datetime
import importlib.util
import json
import random
import re
import statistics
import sys
from pathlib import Path

from pie.export import cognate_tasks, inflection_tasks, train_root_ids, _load
from pie.holdout import HELD_PATH, PROTECTED_PATH, hash_rank
from pie.realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent
SHARE = 0.10
SWADESH = {
    "kin": ["father", "mother", "daughter", "son", "brother", "sister", "husband", "wife", "widow",
            "grandfather", "grandmother", "grandson", "granddaughter", "nephew", "niece", "uncle", "aunt",
            "father-in-law", "mother-in-law", "son-in-law", "daughter-in-law", "brother-in-law",
            "sister-in-law", "husband's brother", "husband's sister", "child", "orphan"],
    "body": ["head", "eye", "ear", "nose", "mouth", "tooth", "tongue", "lip", "hair", "hand", "foot", "leg",
             "knee", "arm", "elbow", "shoulder", "finger", "nail", "fingernail", "neck", "back", "breast",
             "heart", "liver", "kidney", "belly", "navel", "guts", "bowels", "blood", "bone", "marrow", "skin",
             "flesh", "meat", "fat", "horn", "tail", "feather", "wing", "eyebrow", "brow", "jaw", "chin",
             "cheek", "thigh", "heel", "lung", "bile", "milk", "egg"],
    "nature": ["sun", "moon", "star", "sky", "cloud", "fog", "rain", "snow", "ice", "wind", "thunder",
               "lightning", "water", "river", "lake", "sea", "salt", "stone", "rock", "sand", "dust", "earth",
               "ground", "mountain", "fire", "smoke", "ash", "ashes", "night", "day", "dawn", "year", "winter",
               "summer", "spring", "tree", "wood", "forest", "leaf", "root", "bark", "seed", "grass", "fruit",
               "flower", "animal", "fish", "bird", "dog", "louse", "snake", "worm", "wolf", "bear"],
}
SECURE_LEVELS = ("exact", "root")


def _make_slice():
    spec = importlib.util.spec_from_file_location("make_slice", ROOT / "scripts" / "make_slice.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _segments(gloss: str) -> set[str]:
    out = set()
    for s in re.split(r"[;,()]", (gloss or "").lower()):
        s = re.sub(r"^\s*(a|an|the|one's|to)\s+", "", s.strip()).strip(" .")
        if s:
            out.add(s)
    return out


def protected(lx, ms) -> tuple[dict[str, list[str]], dict]:
    """root_id → sorted reasons; and the lexemes behind each reason (for the file)."""
    reasons: dict[str, set[str]] = collections.defaultdict(set)
    rootless = collections.Counter()
    lexemes: dict[str, set[str]] = collections.defaultdict(set)

    def add(lid, why):
        e = lx.entries.get(lid)
        if e is None:
            return
        lexemes[why].add(lid)
        rid = e.get("root_id")
        if rid:
            reasons[rid].add(why)
        else:
            rootless[why] += 1

    menu = json.loads((ROOT / "data/generation/formula_menu.json").read_text("utf-8"))
    for m in menu:
        for x in m["lexemes"]:
            add(x["lex_id"], "formula-menu")
    from pie.formulas import load as load_formulas
    from pie.validate import load_index, validate_text
    ix = load_index()               # most of this script's run time (about a minute)
    formula_words = [w for f in load_formulas() if f.get("pie")
                     for w in re.split(r"[\s,]+|…|\.\.\.", f["pie"]) if w.strip("-") and not w.endswith("-")]
    for w in dict.fromkeys(formula_words):
        # as build_formula_menu maps them: a found word (no near-misses), retrying the initial laryngeal the books omit
        tries = [w] + ([lar + w for lar in ("h₁", "h₂", "h₃")] if re.match("[aeiouáéíóúāēīōū]", w) else [])
        for cand in tries:
            t = validate_text(cand.replace("-", ""), ix)["tokens"]
            if t and t[0].found and t[0].analyses and (t[0].analyses[0].lex_id or "").startswith("pie-"):
                add(t[0].analyses[0].lex_id, "formula")
                break
    for r in _load("corpus/tier1/formulas.jsonl", ROOT):
        for t in r.get("tokens") or []:
            if t.get("verified") and t.get("lex_id"):
                add(t["lex_id"], "formula")
    for r in _load("corpus/tier2/*.jsonl", ROOT):
        for t in r.get("tokens") or []:
            if t.get("secure_level") in SECURE_LEVELS and t.get("lex_id"):
                add(t["lex_id"], "tier2-secure")
    for lid in ms.CORE_NOUNS:
        add(lid, "core-noun")
    for lid in ms.CONVERSATION:
        add(lid, "conversation")

    def hits(i, words):
        g = " " + re.sub(r"[^a-z]+", " ", (lx.meaning(i)[0] or "").lower()) + " "
        return any(f" {w} " in g for w in words)

    usable = [i for i, r in lx.specs.items() if r.get("usable") and i not in lx.blocked and lx.entries[i]["meaning"]]
    for i in usable:
        if lx.specs[i]["family"] == "verb" and hits(i, ms.CORE_VERBS) and lx.meaning(i)[1] in ms.TRUSTED_GLOSS:
            add(i, "core-verb")
    for i, e in lx.entries.items():
        if e.get("pos") == "num":
            add(i, "numeral")
    for i in usable:
        if lx.specs[i]["family"] != "noun" or lx.meaning(i)[1] not in ms.TRUSTED_GLOSS:
            continue
        segs = _segments(lx.meaning(i)[0])
        for kind, words in SWADESH.items():
            if segs & set(words):
                add(i, f"swadesh:{kind}")
    return ({rid: sorted(w) for rid, w in sorted(reasons.items())},
            {"rootless_lexemes_by_reason": dict(sorted(rootless.items())),
             "lexemes_by_reason": {k: len(v) for k, v in sorted(lexemes.items())}})


def excluded(lx) -> dict[str, set[str]]:
    """Families already used (or planned) for training, by source."""
    out = {}
    tier2 = _load("corpus/tier2/*.jsonl", ROOT)
    out["tier2-train"] = train_root_ids([r for r in tier2 if not r.get("eval_grade")], lx)
    out["tier3"] = train_root_ids(_load("corpus/tier3/*.jsonl", ROOT) + _load("corpus/tier3b/*.jsonl", ROOT), lx)
    lid_re = re.compile(r'"lex_id": *"(pie-[^"]+)"')
    for name, pats in (("plans", ["data/generation/plans/*.jsonl", "data/tier2/plans/*.jsonl"]),
                       ("slices", ["data/generation/slices/*.json"])):
        s = set()
        for pat in pats:
            for f in ROOT.glob(pat):
                for lid in lid_re.findall(f.read_text("utf-8")):
                    e = lx.entries.get(lid)
                    if e and e.get("root_id"):
                        s.add(e["root_id"])
                    elif lid.startswith("pie-root-"):
                        s.add(lid)
        out[name] = s
    return out


def family_stats(lx, ms) -> dict[str, dict]:
    members = collections.defaultdict(list)
    for i, e in lx.entries.items():
        if e.get("root_id"):
            members[e["root_id"]].append(i)
    tasks = collections.Counter()
    noun_verb = collections.defaultdict(collections.Counter)
    for t in inflection_tasks(lx, random.Random(0)) + cognate_tasks(lx):
        if t.get("coined") or not t.get("root_id"):
            continue
        tasks[t["root_id"]] += 1
        fam = (lx.specs.get(t["source_id"]) or {}).get("family") or lx.entries[t["source_id"]].get("pos") or "other"
        noun_verb[t["root_id"]][fam] += 1
    out = {}
    for rid, ids in members.items():
        refl = collections.defaultdict(list)
        for i in ids:
            for lang, xs in (lx.entries[i].get("reflexes") or {}).items():
                refl[lang] += xs
        good = {lang for lang, xs in refl.items() if any(not (x.get("borrowed") or x.get("analogical")) for x in xs)}
        root_e = lx.entries.get(rid) or {}
        out[rid] = {"reflex_langs": len(good), "branches": len(ms.branches(refl)),
                    "root_type": root_e.get("root_type") or "none", "tasks": tasks[rid],
                    "task_families": dict(noun_verb[rid])}
    return out


def branch_bin(n: int) -> str:
    return "0" if n == 0 else "1-2" if n <= 2 else "3-4" if n <= 4 else "5+"


def stratum(s: dict) -> tuple[str, str, str]:
    return ("tasks" if s["tasks"] else "no-tasks", "branches:" + branch_bin(s["branches"]), s["root_type"])


def select(universe, pool, stats) -> tuple[list[str], dict]:
    old = [r for r in universe if hash_rank(r) < SHARE]
    n = round(SHARE * len(universe))
    by = collections.Counter(stratum(stats[r]) for r in old)
    raw = {k: n * v / len(old) for k, v in by.items()}
    quota = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - quota[k]), str(k)))[: n - sum(quota.values())]:
        quota[k] += 1
    held = []
    for k in sorted(quota, key=str):
        cands = sorted((r for r in pool if stratum(stats[r]) == k), key=lambda r: (hash_rank(r), r))
        if len(cands) < quota[k]:
            raise SystemExit(f"stratum {k}: pool {len(cands)} < quota {quota[k]}")
        held += cands[: quota[k]]
    return sorted(held), {"n": n, "quota": {"/".join(k): v for k, v in sorted(quota.items())}}


def describe(name, fams, stats) -> dict:
    xs = [stats[r] for r in fams]

    def dist(key, bins):
        c = collections.Counter()
        for x in xs:
            v = x[key]
            c[next(lab for lab, lo, hi in bins if lo <= v <= hi)] += 1
        return {lab: c[lab] for lab, _, _ in bins}
    tf = collections.Counter()
    for x in xs:
        tf.update(x["task_families"])
    return {"set": name, "families": len(xs),
            "reflex_langs": {"median": statistics.median(x["reflex_langs"] for x in xs) if xs else 0,
                             "mean": round(statistics.mean(x["reflex_langs"] for x in xs), 2) if xs else 0,
                             "bins": dist("reflex_langs", [("0", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5),
                                                           ("6-10", 6, 10), ("11+", 11, 10 ** 6)])},
            "branches": {"mean": round(statistics.mean(x["branches"] for x in xs), 2) if xs else 0,
                         "bins": dist("branches", [("0", 0, 0), ("1", 1, 1), ("2", 2, 2), ("3-4", 3, 4),
                                                   ("5+", 5, 99)])},
            "root_type": dict(collections.Counter(x["root_type"] for x in xs)),
            "task_bearing": sum(1 for x in xs if x["tasks"]),
            "tasks": sum(x["tasks"] for x in xs),
            "tasks_by_lexeme_family": dict(tf.most_common())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ms, lx = _make_slice(), Lexicon.load()
    prot, prot_meta = protected(lx, ms)
    exc = excluded(lx)
    universe = sorted({e["root_id"] for e in lx.entries.values() if e.get("root_id")})
    stats = family_stats(lx, ms)
    used = set().union(*exc.values())
    pool = [r for r in universe if r not in prot and r not in used]
    held, sel = select(universe, pool, stats)
    old = [r for r in universe if hash_rank(r) < SHARE]
    seen_train = exc["tier2-train"] | exc["tier3"]
    report = {"old_hash": describe("old hash draw", old, stats),
              "old_effective": describe("old effective (hash, unseen in training)",
                                        [r for r in old if r not in seen_train], stats),
              "new": describe("new", held, stats),
              "old_protected": sorted(r for r in old if r in prot)}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"universe {len(universe)}, protected {len(prot)}, used {len(used & set(universe))}, pool {len(pool)}, "
          f"held {len(held)}; old∩new {len(set(old) & set(held))}")
    if args.dry_run:
        return 0
    today = datetime.date.today().isoformat()
    PROTECTED_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROTECTED_PATH.write_text(json.dumps({
        "generated": today, "by": "scripts/build_holdout.py", "swadesh_concepts": SWADESH,
        **prot_meta, "families": len(prot), "roots": prot}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    HELD_PATH.write_text(json.dumps({
        "generated": today, "by": "scripts/build_holdout.py", "share": SHARE, "universe": len(universe),
        "protected": len(prot), "excluded_used": {k: len(v & set(universe)) for k, v in exc.items()},
        "pool": len(pool), **sel, "ranking": "ascending int(sha256(root_id)[:8], 16) / 0xFFFFFFFF within stratum",
        "comparison": {k: v for k, v in report.items() if k != "old_protected"},
        "old_protected_count": len(report["old_protected"]),
        "held": held}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"wrote {PROTECTED_PATH} and {HELD_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
