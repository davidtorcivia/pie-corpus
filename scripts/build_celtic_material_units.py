"""Apply reviewed material repairs to the frozen Celtic layer; never overwrite it.

uv run python -I scripts/build_celtic_material_units.py --out /tmp/units.jsonl
The lead may instead request raw/daughters/celtic-stageC/units.v2.jsonl.
No code under raw/ is executed. The historical OCR builder is documented in
docs/research/celtic-stageC-units.md; this is its reviewed material-cleanup pass.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pie.material_units import repair_celtic_rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    source = ROOT / "raw/daughters/celtic-stageC/units.jsonl"
    if args.out.resolve() == source.resolve():
        ap.error("the frozen units.jsonl must not be overwritten")
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    repaired = repair_celtic_rows(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for row in repaired:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"input": len(rows), "output": len(repaired)}))


if __name__ == "__main__":
    main()
