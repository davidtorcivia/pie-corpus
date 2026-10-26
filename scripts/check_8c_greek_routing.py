#!/usr/bin/env python3
"""ENG-02 impact: fresh processes, no loader caches, text-free temporary snapshots.

Run: uv run python -I scripts/check_8c_greek_routing.py
Only the historical Stage C loci files are inspected; no keys or Stage C-S slabs.
The old mode changes only grp override routing back to grc. Shipped link extracts
are inputs, not cached mapped units. Neither mode reads stagec/stagecs caches.
"""

import argparse
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def snapshot(corpus, mode, output):
    spec = importlib.util.spec_from_file_location("eng02_C", ROOT / "scripts/build_8c_stageC.py")
    C = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = C
    spec.loader.exec_module(C)
    from pie import formula_search as fs
    from pie import formula_search_multi as fm

    if mode == "old":
        original = fm.apply_lemma_overrides

        def old_route(population, *args, **kwargs):
            return original("grc" if population == "grp" else population, *args, **kwargs)

        fm.apply_lemma_overrides = old_route
    lex = fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")
    groups = fs.group_map(lex)
    loader = C.SB.load_greek_b if corpus == "grc" else C.load_greek_late
    units, _ = loader(ROOT, lex, groups)
    C.B.assign_pids({corpus: units})
    with output.open("w") as fh:
        for u in units:
            roots = sorted({groups.get(x, x) for _, _, ids in u.words for x in ids})
            annotation = digest([sorted(ids) for _, _, ids in u.words])
            provenance = digest([u.corpus, u.key, u.locus, u.book, u.text, u.licence,
                                 u.research_only, [(s, lemma) for s, lemma, _ in u.words]])
            fh.write(json.dumps([u.pid, roots, annotation, provenance]) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--worker", choices=["grc", "grc-late"])
    ap.add_argument("--mode", choices=["old", "corrected"])
    ap.add_argument("--snapshot", type=Path)
    args = ap.parse_args()
    if args.worker:
        snapshot(args.worker, args.mode, args.snapshot)
        return
    report = {"cache_policy": "fresh subprocess per corpus/mode; loader caches disabled", "corpora": {}}
    changed_roots, changed_annotations = set(), set()
    with tempfile.TemporaryDirectory(prefix="pie-eng02-") as tmp:
        for corpus in ("grc", "grc-late"):
            paths = [Path(tmp) / f"{corpus}-{mode}.jsonl" for mode in ("old", "corrected")]
            for mode, path in zip(("old", "corrected"), paths):
                print(f"Loading {corpus}: {mode} (fresh process)", file=sys.stderr, flush=True)
                subprocess.run(["uv", "run", "python", "-I", str(Path(__file__).resolve()),
                                "--worker", corpus, "--mode", mode, "--snapshot", str(path)],
                               cwd=ROOT, check=True)
            counts = {"units": 0, "root_sets_changed": 0, "mapping_annotations_changed": 0}
            with paths[0].open() as old, paths[1].open() as corrected:
                for a, b in itertools.zip_longest(old, corrected):
                    assert a is not None and b is not None, "Unit count changed"
                    a, b = json.loads(a), json.loads(b)
                    assert a[0] == b[0] and a[3] == b[3], "Identity or provenance changed"
                    counts["units"] += 1
                    if a[1] != b[1]:
                        counts["root_sets_changed"] += 1
                        changed_roots.add(a[0])
                    if a[2] != b[2]:
                        counts["mapping_annotations_changed"] += 1
                        changed_annotations.add(a[0])
            report["corpora"][corpus] = counts
    bundles = {}
    loci_files = sorted((ROOT / "data/research/8c/stageC/slabs-loci").glob("*.json"))
    for path in loci_files:
        for b in json.loads(path.read_text())["bundles"]:
            bundles[b["bundle"]] = {b["pivot"], *b["partners"]}
    members = set().union(*bundles.values()) if bundles else set()
    report["historical_stageC"] = {
        "loci_files": len(loci_files), "bundles": len(bundles),
        "member_passages_with_changed_roots": len(members & changed_roots),
        "member_passages_with_changed_annotations": len(members & changed_annotations),
        "bundles_with_changed_roots": sum(bool(p & changed_roots) for p in bundles.values()),
        "bundles_with_changed_annotations": sum(bool(p & changed_annotations) for p in bundles.values()),
    }
    inputs = [ROOT / p for p in ("scripts/build_8c_stageB.py", "scripts/build_8c_stageC.py",
              "scripts/check_8c_greek_routing.py", "data/lexicon/lexicon.jsonl",
              "data/research/formulas/kaikki_links/grc.jsonl",
              "data/research/formulas/mapping-overrides/greek.json")]
    report["sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
