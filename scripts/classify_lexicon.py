#!/usr/bin/env python3
"""Layer 2: assign an inflection spec to every lexicon entry, and backtest the
shape rules against the entries that have Wiktionary tables.

  uv run python -I scripts/classify_lexicon.py

Writes data/morph/inflection_specs.jsonl (one row per entry) and
data/morph/classify_report.json (coverage and per-rule backtest accuracy).
"""

import collections
import dataclasses
import json
import sys
from pathlib import Path

from pie.classify import Classified, by_shape, spec_from_template
from pie.crosscheck import cells_for

ROOT = Path(__file__).resolve().parent.parent
# Tier 3 may only use a spec from a table, or from a shape rule whose
# backtest cell agreement reaches this threshold (docs/morphology.md).
BACKTEST_AS = {"shape:thematic-neuter-reflex": "shape:thematic-neuter"}
USABLE_THRESHOLD = 0.85
LEX = ROOT / "data" / "lexicon"
OUT = ROOT / "data" / "morph"


def compare(family, spec, para):
    """(ok, total): cells of the shape-guessed spec vs cells of the table's own
    spec (template 1), both from the engine. This isolates the shape rule's
    error from the engine's (measured separately by the crosscheck)."""
    got = spec_from_template(para["templates"][0])
    if got is None:
        return 0, 0
    tfam, tspec = got
    try:
        want = cells_for(tfam, tspec)
    except Exception:
        return 0, 0
    # an o-stem table that disagrees with its own headword (h₂ŕ̥ǵn̥tom vs table h₂r̥ǵn̥tó-) tests Wiktionary,
    # not the rule; athematic tables keep their citation-form mismatch (gʷḗn vs gʷénh₂s). Engine sweep,
    # docs/audits/engine-sweep/thematic.md "Gating".
    thematic = (tfam == "noun" and tspec.kind == "thematic") or (tfam == "adj" and tspec.m_weak is None)
    if thematic and para.get("form") and para["form"] not in want.get("NOM.SG", []):
        return 0, 0
    try:
        have = cells_for(family, spec) if family == tfam else {}
    except Exception:
        have = {}
    ok = sum(1 for k, v in want.items() if set(v) == set(have.get(k, [])))
    return ok, len(want)


def main() -> int:
    lex = [json.loads(x) for x in (LEX / "lexicon.jsonl").read_text("utf-8").splitlines()]
    # status of each displaced spec (docs/audits/alt-form-status.md); the last override line of an id wins,
    # as in pie/lexicon.py
    displaced = {}
    for x in (LEX / "overrides.jsonl").read_text("utf-8").splitlines():
        o = json.loads(x)
        if "spec" in o:
            displaced[o["id"]] = (o.get("displaced_status", "legacy"), o.get("displaced_why") or o.get("note"))
    paras = {}
    for x in (LEX / "paradigms.jsonl").read_text("utf-8").splitlines():
        p = json.loads(x)
        paras[p["lex_id"]] = p

    # Backtest: shape rules on entries that have tables, table hidden.
    bt = collections.defaultdict(lambda: collections.Counter())
    for e in lex:
        p = paras.get(e["id"])
        if not p or not p["templates"][0]["name"].startswith(("ine-decl-noun", "ine-decl-adj", "ine-conj")):
            continue
        c = by_shape(e)
        bt[c.rule]["tables"] += 1
        if c.spec is None:
            continue
        ok, total = compare(c.family, c.spec, p)
        bt[c.rule]["cells_ok"] += ok
        bt[c.rule]["cells"] += total
        bt[c.rule]["tables_exact"] += ok == total and total > 0
    accuracy = {r: (c["cells_ok"] / c["cells"] if c["cells"] else None) for r, c in bt.items()}

    # Assign: table first, else shape.
    OUT.mkdir(parents=True, exist_ok=True)
    rows, cov = [], collections.Counter()
    for e in lex:
        if e["kind"] not in ("word", "derivative"):
            continue
        p = paras.get(e["id"])
        c = None
        extra = []
        if p:
            got = spec_from_template(p["templates"][0])
            if got:
                c = Classified(got[1], "table", got[0])
            # further templates on the same page (a second accent class, ...)
            for t in p["templates"][1:]:
                g2 = spec_from_template(t)
                if g2:
                    # a second Wiktionary table: a supported alternative
                    extra.append({"family": g2[0], "spec": dataclasses.asdict(g2[1]), "status": "supported"})
        if c is None:
            c = by_shape(e)
        cov[c.rule.split(":")[0] if c.spec is None else ("table" if c.rule == "table" else "shape")] += 1
        # a rule that only changes the routing evidence inherits the backtest of the paradigm it produces
        acc = 1.0 if c.rule == "table" else accuracy.get(c.rule, accuracy.get(BACKTEST_AS.get(c.rule, "")))
        usable = c.spec is not None and acc is not None and acc >= USABLE_THRESHOLD
        if e.get("spec_checked") and (c.spec is not None or e.get("spec_override")):
            usable = True          # a spec checked by hand from the reviews (data/lexicon/overrides.jsonl)
        cov["usable"] += usable
        spec = dataclasses.asdict(c.spec) if c.spec else None
        if spec and e.get("spec_override"):            # hand fixes from reviews (data/lexicon/overrides.jsonl)
            before, spec = spec, {**spec, **e["spec_override"]}
            # the displaced spec stays indexed for the validator (pie/validate.py reads extra_specs), with its
            # status: supported (a convention alternative), legacy (recognized, a warning) or rejected (a
            # diagnosed error, reported as one). Unclassified displacements default to legacy.
            if before != spec and c.family and not any(x["spec"] == before for x in extra):
                st, why = displaced.get(e["id"], ("legacy", None))
                extra.append({"family": c.family, "spec": before, "displaced_by_override": True,
                              "status": st, "status_note": why})
        if e.get("spec_checked") and spec is None and e.get("spec_override"):
            spec = e["spec_override"]
        rows.append({"id": e["id"], "form": e["form"], "rule": c.rule, "family": c.family,
                     "spec": spec,
                     "backtest_cell_accuracy": acc, "usable": usable, "extra_specs": extra})
    with (OUT / "inflection_specs.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    report = {
        "entries": len(rows),
        "coverage": dict(cov),
        "inflectable": cov["table"] + cov["shape"],
        "usable_for_tier3": cov["usable"],
        "usable_threshold": USABLE_THRESHOLD,
        "backtest": {r: {**dict(c), "cell_accuracy": round(accuracy[r], 4) if accuracy[r] is not None else None}
                     for r, c in sorted(bt.items())},
        "by_rule": dict(collections.Counter(r["rule"] for r in rows).most_common()),
    }
    (OUT / "classify_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
