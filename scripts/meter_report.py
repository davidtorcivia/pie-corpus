#!/usr/bin/env python3
"""List every verse line of a batch with its syllable count, target, gap and the syllable-cheap edits.

  uv run python -I scripts/meter_report.py <batch>                 # data/generation/plans/<batch>.jsonl
  uv run python -I scripts/meter_report.py path/to/plans.jsonl     # any plan file (e.g. <batch>.initial.jsonl)
  options: --misses (only lines off target) --edits N (per line, default 8) --json
  uv run python -I scripts/meter_report.py --census                # every stored batch, from corpus records

Read-only: it realizes the plans in memory (check_plan, realize) and writes nothing, so a planner can run it
on the plan file before the final realize_plans.py run. A verse line is a sentence of a plan whose genre is in
pie.meter.METERED_GENRES (the plan's clauses from one "break": true to the next), exactly as realize_plans.py
scores it. The target is the nearest of 8 and 11 (and 12 if the plan record declares "meter": 12); the gap is
target − count (+ = add syllables).

Every edit is measured, not estimated: the tool applies it to a copy of the plan, realizes it, recounts the
line and keeps only edits check_plan accepts. Edits: particle nu / -ge on or off, clause conjunction -kʷe on or
off, a nominal slot's number (SG/DU/PL), dropping an epithet, adverb, possessor or vocative (with its
dependents), adding a slice adjective as an epithet (MOD) or a vocative, splitting a sentence at a clause or
merging it with the next. Edits that add a word or change number or meaning say so: the plan's English must
be updated to match. Engine alternative forms of the same cell with a different count are listed as "alt"
(information: a plan cannot select them). Word order never changes a count (counts are per word).
"""

from __future__ import annotations

import argparse
import copy
import json
import runpy
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pie.export import token_variants  # noqa: E402
from pie.meter import METERED_GENRES, line_syllables, measure, nearest_target, targets_for, verse_lines  # noqa: E402
from pie.realize import Lexicon, check_plan, realize, token_cell  # noqa: E402

NOMINAL_ROLES = {"SUBJ", "OBJ", "IO", "INS", "LOC", "ABL", "POSS", "VOC", "GOAL", "NP", "APPOS", "PRED"}
DROPPABLE = {"MOD": "epithet", "APPOS": "apposition", "ADV": "adverb", "POSS": "possessor", "VOC": "vocative"}
GATE = runpy.run_path(str(ROOT / "scripts" / "realize_plans.py"))     # lexeme_cap, METER_EXACT_MIN


def groups(plan: dict) -> list[list[int]]:
    """Clause indices of each sentence: a clause with "break": true starts a new one (pie.realize.realize)."""
    out: list[list[int]] = []
    for ci, cl in enumerate(plan["clauses"]):
        if not out or (ci and cl.get("break")):
            out.append([])
        out[-1].append(ci)
    return out


def counts(plan: dict, lx: Lexicon) -> list[int] | None:
    try:
        return [measure(x)["syllables"] for x in verse_lines(realize(plan, lx)["pie"])]
    except Exception:            # an edited plan the realizer cannot take: not an edit
        return None


def _drop(slots: list[dict], k: int) -> list[dict]:
    """Slots without slot k and everything that depends on it (head/dep chains), indices renumbered."""
    gone = {k}
    changed = True
    while changed:
        changed = False
        for i, s in enumerate(slots):
            if i not in gone and (s.get("head") in gone or s.get("dep") in gone):
                gone.add(i)
                changed = True
    new = {old: n for n, old in enumerate(i for i in range(len(slots)) if i not in gone)}
    out = []
    for i, s in enumerate(slots):
        if i in gone:
            continue
        s = dict(s)
        for key in ("head", "dep"):
            if isinstance(s.get(key), int):
                s[key] = new[s[key]]
        out.append(s)
    return out


def candidate_edits(plan: dict, line: int, grp: list[int], lx: Lexicon, slice_: dict) -> list[tuple[str, str, dict]]:
    """(kind, description, edited plan) for one sentence."""
    out = []

    def edit(kind, desc, fn):
        p = copy.deepcopy(plan)
        fn(p)
        out.append((kind, desc, p))

    for ci in grp:
        cl = plan["clauses"][ci]
        part = cl.get("particle")
        if part is None:
            for x in ("nu", "ge"):
                edit("particle", f"c{ci}: add particle {'nu' if x == 'nu' else '-ge'}",
                     lambda p, ci=ci, x=x: p["clauses"][ci].__setitem__("particle", x))
        elif part in ("nu", "ge"):
            edit("particle", f"c{ci}: drop particle {part}", lambda p, ci=ci: p["clauses"][ci].pop("particle"))
        if ci > 0:
            if cl.get("conj") is None:
                edit("conj", f"c{ci}: join to the previous clause with -kʷe 'and'",
                     lambda p, ci=ci: p["clauses"][ci].__setitem__("conj", "kʷe"))
            elif cl.get("conj") == "kʷe":
                edit("conj", f"c{ci}: drop clause -kʷe", lambda p, ci=ci: p["clauses"][ci].pop("conj"))
        slots = cl.get("slots", [])
        for k, s in enumerate(slots):
            lid = s.get("lex_id", "")
            if s.get("role") in NOMINAL_ROLES and s.get("head") is None and not lid.startswith("closed:") \
                    and lid != "compound":
                for num in ("SG", "DU", "PL"):
                    if num != s.get("num", "SG"):
                        edit("number", f"c{ci} slot {k} {lid} ({s['role']}): number {s.get('num', 'SG')}→{num} "
                                       f"[meaning: update the English]",
                             lambda p, ci=ci, k=k, num=num: p["clauses"][ci]["slots"][k].__setitem__("num", num))
            if s.get("role") in DROPPABLE and s.get("participle") is None:
                edit("drop", f"c{ci} slot {k}: drop {DROPPABLE[s['role']]} {lid} [update the English]",
                     lambda p, ci=ci, k=k: p["clauses"][ci].__setitem__("slots", _drop(p["clauses"][ci]["slots"], k)))
        # epithets: a slice adjective on a noun slot
        adjs = [x["lex_id"] for x in slice_.get("lexemes", []) if x.get("family") == "adj"]
        for k, s in enumerate(slots):
            lid = s.get("lex_id", "")
            if s.get("role") in NOMINAL_ROLES and lx.specs.get(lid, {}).get("family") == "noun":
                have = {t.get("lex_id") for t in slots if t.get("head") == k}
                for a in adjs:
                    if a not in have:
                        edit("epithet", f"c{ci}: add epithet {a} (MOD on slot {k} {lid}) [add it to the English]",
                             lambda p, ci=ci, k=k, a=a: p["clauses"][ci]["slots"].append(
                                 {"lex_id": a, "role": "MOD", "head": k}))
        # vocatives: an address to a clause with a 2nd-person or imperative verb and none yet
        v = next((t.get("verb") for t in slots if t.get("role") == "V"), None)
        if v and (v.get("person") == 2 or v.get("mood") == "IMP") and not any(t.get("role") == "VOC" for t in slots):
            used = {t["lex_id"] for c in plan["clauses"] for t in c.get("slots", []) if t.get("role") == "VOC"}
            core = [x for x in slice_.get("theme_core", []) if lx.specs.get(x, {}).get("family") == "noun"]
            for n in dict.fromkeys([*used, *core]):
                edit("vocative", f"c{ci}: add vocative {n} [add it to the English]",
                     lambda p, ci=ci, n=n: p["clauses"][ci]["slots"].insert(0, {"lex_id": n, "role": "VOC"}))
    for ci in grp[1:]:
        edit("split", f"split the sentence before c{ci} (break: true) [two lines]",
             lambda p, ci=ci: p["clauses"][ci].__setitem__("break", True))
    nxt = grp[-1] + 1
    if nxt < len(plan["clauses"]):
        edit("merge", f"merge with the next sentence (c{nxt}: break → false) [one line]",
             lambda p: p["clauses"][nxt].pop("break"))
    return out


def report(path: Path, misses_only: bool = False, max_edits: int = 8) -> dict:
    lx = Lexicon.load()
    plans = [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip()]
    batch = path.stem.removesuffix(".initial").removesuffix("-initial")
    sp = ROOT / "data" / "generation" / "slices" / f"{batch}.json"
    slice_ = json.loads(sp.read_text("utf-8")) if sp.exists() else {}
    # lexeme uses over the whole batch, for the cap note on added words
    uses: Counter = Counter()
    n_tokens = 0
    realized = {}
    for n, rec in enumerate(plans):
        plan = rec.get("plan", rec)
        if check_plan(plan, lx):
            continue
        r = realize(plan, lx)
        realized[n] = r
        n_tokens += len(r["words"])
        uses.update(w["lex_id"] for w in r["words"] if not w["lex_id"].startswith("closed:"))
    cap = GATE["lexeme_cap"](len(realized), n_tokens)
    out_plans = []
    total = exact = 0
    for n, rec in enumerate(plans):
        if rec.get("genre") not in METERED_GENRES:
            continue
        plan, pid = rec.get("plan", rec), rec.get("plan_id", n)
        entry = {"plan_id": pid, "genre": rec.get("genre"), "title": rec.get("title"), "lines": []}
        out_plans.append(entry)
        if n not in realized:
            entry["rejected"] = check_plan(plan, lx)[:3]
            continue
        r = realized[n]
        tg = targets_for(rec.get("meter"))
        lines, grps = verse_lines(r["pie"]), groups(plan)
        if len(lines) != len(grps):
            raise SystemExit(f"{pid}: {len(lines)} sentences but {len(grps)} clause groups")
        # engine alternatives of each word's cell, by word position in the text
        toks = [{"form": w["form"], "lex_id": w["lex_id"], "features": w["features"], **token_cell(w)}
                for w in r["words"]]
        alts = token_variants({"tier": 3, "tokens": toks}, lx) or []
        alt_by_form = {}
        for t, a in zip(toks, alts):
            for f in a[1:]:
                d = measure(f)["syllables"] - measure(t["form"])["syllables"]
                if d:
                    alt_by_form.setdefault(t["form"], []).append((f, d))
        for li, (text, grp) in enumerate(zip(lines, grps)):
            c = measure(text)["syllables"]
            target = nearest_target(c, tg)
            gap = target - c
            total += 1
            exact += c in tg
            line = {"line": li + 1, "clauses": grp, "text": text, "syllables": c, "per_word": line_syllables(text),
                    "target": target, "gap": gap, "edits": []}
            if misses_only and not gap:
                continue
            entry["lines"].append(line)
            if not gap:
                continue
            base = [measure(x)["syllables"] for x in lines]
            found = []
            for kind, desc, p in candidate_edits(plan, li, grp, lx, slice_):
                new = counts(p, lx)
                if new is None or new == base:
                    continue
                if kind == "split":
                    parts = new[li:li + 2]
                    score = sum(abs(x - nearest_target(x, tg)) for x in parts)
                    result = "+".join(map(str, parts))
                elif kind == "merge":
                    parts = [new[li]]
                    score = abs(new[li] - nearest_target(new[li], tg))
                    result = str(new[li])
                else:
                    if len(new) != len(base):
                        continue
                    score = abs(new[li] - nearest_target(new[li], tg))
                    result = str(new[li])
                if score >= abs(gap) or (kind == "merge" and score > 0):
                    continue
                if check_plan(p, lx):
                    continue
                added = Counter(w["lex_id"] for w in realize(p, lx)["words"]) - \
                    Counter(w["lex_id"] for w in r["words"])
                over = [lid for lid in added if not lid.startswith("closed:") and uses[lid] + added[lid] > cap]
                found.append({"kind": kind, "edit": desc, "result": result, "exact": score == 0,
                              **({"over_cap": over} if over else {})})
            found.sort(key=lambda e: (not e["exact"], "over_cap" in e,
                                      ["particle", "conj", "drop", "epithet", "vocative", "number", "split",
                                       "merge"].index(e["kind"])))
            line["edits"] = found[:max_edits]
            line["alt"] = [f"{w} → {f} ({d:+d})" for w in text.replace("-", " -").split()
                           for f, d in alt_by_form.get(w, []) if abs(gap - d) < abs(gap)]
    return {"batch": batch, "source": str(path), "lexeme_cap": cap, "lines": total, "exact": exact,
            "exact_share": round(exact / max(1, total), 3), "gate_min": GATE["METER_EXACT_MIN"],
            "plans": out_plans}


def census() -> list[dict]:
    """Per stored batch (corpus/tier3/*.jsonl, not re-realized): verse lines of metered genres, computed from
    each record's stored `pie` and `genre` with the current syllabifier, beside the stored per-line counts
    (the syllabifier the batch was realized with, where the record has a `meter` field)."""
    from pie.meter import record_meter, summary
    rows = []
    for f in sorted((ROOT / "corpus" / "tier3").glob("*.jsonl")):
        recs = [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
        ms = [m for r in recs if (m := record_meter(r["pie"], r.get("genre")))]
        old = [r["meter"] for r in recs if r.get("meter")]
        s = summary(ms)
        if s is None:
            rows.append({"batch": f.stem, "records": len(recs), "metered_records": 0, "lines": 0})
            continue
        old_exact = sum(n in (8, 11) for m in old for n in m["line_syllables"])
        old_lines = sum(len(m["line_syllables"]) for m in old)
        genres = Counter(r["genre"] for r in recs if r.get("genre") in METERED_GENRES)
        rows.append({"batch": f.stem, "records": len(recs), "metered_records": len(ms), "genres": dict(genres),
                     "lines": s["lines"], "exact": s["exact"], "exact_share": s["exact_share"],
                     "near_share": s["near_share"], "stored_lines": old_lines,
                     "stored_exact_share": round(old_exact / old_lines, 3) if old_lines else None,
                     "cadence": s["cadence"],
                     "gap_hist": dict(sorted(Counter(nearest_target(n) - n for m in ms
                                                     for n in m["line_syllables"]).items()))})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", nargs="?", help="batch name (data/generation/plans/<batch>.jsonl) or a plan file path")
    ap.add_argument("--census", action="store_true", help="every stored batch, from its corpus records (JSON)")
    ap.add_argument("--misses", action="store_true", help="only lines that are off target")
    ap.add_argument("--edits", type=int, default=8, help="edits listed per line")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.census:
        print(json.dumps(census(), ensure_ascii=False, indent=1))
        return 0
    if not a.batch:
        ap.error("a batch or plan file is required (or --census)")
    path = Path(a.batch)
    if not path.exists():
        path = ROOT / "data" / "generation" / "plans" / f"{a.batch}.jsonl"
    rep = report(path, a.misses, a.edits)
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    print(f"{rep['batch']}: {rep['exact']}/{rep['lines']} verse lines exact ({rep['exact_share']:.3f}; "
          f"gate meter_exact>={rep['gate_min']:.2f} {'PASS' if rep['exact_share'] >= rep['gate_min'] else 'FAIL'}); "
          f"lexeme cap {rep['lexeme_cap']}")
    print("Counts are per word: word order never changes them. [..] = what else the edit changes.")
    for e in rep["plans"]:
        if "rejected" in e:
            print(f"\n{e['plan_id']} ({e['genre']}) REJECTED by check_plan: {e['rejected']}")
            continue
        if not e["lines"]:
            continue
        print(f"\n{e['plan_id']} ({e['genre']}) {e.get('title') or ''}")
        for ln in e["lines"]:
            cl = f"c{ln['clauses'][0]}" + (f"-{ln['clauses'][-1]}" if len(ln["clauses"]) > 1 else "")
            mark = "ok" if not ln["gap"] else f"{ln['gap']:+d}"
            print(f"  L{ln['line']} {cl:7} {ln['syllables']:2}/{ln['target']} {mark:>3}  {ln['text']}  "
                  f"{ln['per_word']}")
            for ed in ln["edits"]:
                cap_note = f"  OVER CAP: {', '.join(ed['over_cap'])}" if ed.get("over_cap") else ""
                print(f"      {'=' if ed['exact'] else '~'} {ed['result']:>5}  {ed['edit']}{cap_note}")
            for alt in ln.get("alt", []):
                print(f"      alt  {alt}  (engine alternative; a plan cannot select it)")
            if ln["gap"] and not ln["edits"]:
                print("      (no single edit found: rephrase, or combine edits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
