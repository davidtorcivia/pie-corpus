#!/usr/bin/env python3
"""Score a calibrated review against its key (see scripts/make_review_packet.py).

  uv run python -I scripts/score_review.py t001

Reads docs/audits/packets/<batch>-verdicts.jsonl, one line per item:
{"item": "...", "verdict": "ok|minor|wrong", "issue": "..."}. Reports:
- plant recall: planted items judged minor or wrong (and how many of those
  name the planted word);
- Tier 1 lines judged wrong (scholarly reconstructions; a high rate means
  the reviewer is over-strict, or that the line uses another school's forms);
- the wrong and minor rates on the real items, with the observed wrong rate
  corrected for the plant miss rate (wrong_rate / recall) as an upper bound.
Writes data/audits/<batch>-calibration.json.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    b = sys.argv[1]
    key = json.loads((ROOT / "data/audits/keys" / f"{b}-key.json").read_text("utf-8"))
    ver = {json.loads(x)["item"]: json.loads(x) for x in
           (ROOT / "docs/audits/packets" / f"{b}-verdicts.jsonl").read_text("utf-8").splitlines() if x.strip()}
    missing = [k for k in key if k not in ver]
    plants = [k for k, v in key.items() if v["kind"] == "plant" and k in ver]
    caught = [k for k in plants if ver[k]["verdict"] in ("minor", "wrong")]
    named = [k for k in caught if key[k]["corruption"]["replaced_by"] in (ver[k].get("issue") or "")]
    t1 = [k for k, v in key.items() if v["kind"] == "tier1" and k in ver]
    real = [k for k, v in key.items() if v["kind"] == "real" and k in ver]
    wrong = sum(1 for k in real if ver[k]["verdict"] == "wrong")
    minor = sum(1 for k in real if ver[k]["verdict"] == "minor")
    recall = len(caught) / len(plants) if plants else None
    out = {"batch": b, "items": len(key), "unjudged": len(missing),
           "plant_recall": round(recall, 3) if recall is not None else None,
           "plants": len(plants), "plants_caught": len(caught), "plants_named": len(named),
           "tier1_judged_wrong": sum(1 for k in t1 if ver[k]["verdict"] == "wrong"), "tier1": len(t1),
           "real": len(real), "real_wrong": wrong, "real_minor": minor,
           "real_wrong_rate": round(wrong / len(real), 3) if real else None,
           "real_wrong_rate_upper": round(min(1.0, wrong / len(real) / recall), 3) if real and recall else None}
    (ROOT / "data/audits").mkdir(exist_ok=True)
    (ROOT / "data/audits" / f"{b}-calibration.json").write_text(json.dumps(out, indent=1) + "\n", "utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
