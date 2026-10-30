#!/usr/bin/env python3
"""Replace one lexeme with another in every Tier 3 plan that uses it, re-realize those batches, and report each
batch's gate and meter before and after.

    uv run python -I scripts/swap_lexeme.py pie-lex-deh3ut pie-lex-deh3t [--dry-run]

Every slot whose lex_id is OLD becomes NEW, with its role, features and head unchanged; nothing else in the plan
moves. A batch is realized with the model and prompt id its records already carry (generator) and the current
commit as engine version. Realization resets the batch's release to pending (pie.batch_release); a batch that was
approved and still passes its gate is re-approved here with the swap's audit note added to its evidence, because
the swap is mechanical: the same plans with one lexeme exchanged. A batch whose gate no longer passes stays pending.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie.batch_release import corpus_dir, release_metadata  # noqa: E402


def batches_using(lex: str) -> list[str]:
    return sorted(p.stem for p in (ROOT / "data/generation/plans").glob("*.jsonl")
                  if not p.stem.endswith(".initial") and f'"{lex}"' in p.read_text("utf-8")
                  and (ROOT / corpus_dir(p.stem) / f"{p.stem}.jsonl").exists())


def gate(batch: str) -> dict:
    d = json.loads((ROOT / f"data/generation/batches/{batch}.json").read_text("utf-8"))
    return {"gate": d.get("gate"), "meter_exact": d.get("meter_exact"), "realized": d.get("realized"),
            "plans": d.get("plans")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("old"), ap.add_argument("new")
    ap.add_argument("--note", required=True, help="the audit note added to a re-approved batch's evidence")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rerun", nargs="*", default=[],
                    help="batches whose plans are already swapped: re-realize and re-approve only")
    a = ap.parse_args()
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    report = {}
    for b in batches_using(a.old) + a.rerun:
        plans = ROOT / f"data/generation/plans/{b}.jsonl"
        rec = json.loads((ROOT / corpus_dir(b) / f"{b}.jsonl").read_text("utf-8").splitlines()[0])["generator"]
        rel_path = ROOT / f"data/generation/releases/{b}.json"
        # the committed release: a failed earlier run has already reset the working copy to pending
        git = subprocess.run(["git", "show", f"HEAD:data/generation/releases/{b}.json"], capture_output=True,
                             text=True, cwd=ROOT)
        release = json.loads(git.stdout) if git.returncode == 0 else {}
        before = gate(b)
        n = plans.read_text("utf-8").count(f'"{a.old}"')
        report[b] = {"slots": n, "before": before, "was": release.get("review", {}).get("status")}
        if a.dry_run:
            continue
        if b not in a.rerun:
            plans.write_text(plans.read_text("utf-8").replace(f'"{a.old}"', f'"{a.new}"'), "utf-8")
        cmd = [sys.executable, "-I", "scripts/realize_plans.py", str(plans.relative_to(ROOT)), "--batch", b,
               "--model", rec["model"], "--prompt-id", rec["prompt_id"], "--engine-version", head]
        if b.startswith("t3b-"):
            cmd.append("--tier3b")
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
            report[b]["error"] = r.returncode
            continue
        after = gate(b)
        report[b]["after"] = after
        if report[b]["was"] == "approved" and after["gate"] == "PASS" and after["realized"] == before["realized"]:
            rv = release["review"]
            rel_path.write_text(json.dumps(release_metadata(
                ROOT, b, status="approved", evidence=[*rv.get("evidence", []), a.note],
                rationale=rv.get("rationale", "") + f" Re-approved after the mechanical {a.old} -> {a.new} swap "
                                                     f"({a.note})."), ensure_ascii=False) + "\n", "utf-8")
            report[b]["now"] = "approved"
        else:
            report[b]["now"] = "pending"
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
