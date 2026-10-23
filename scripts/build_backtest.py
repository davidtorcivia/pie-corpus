#!/usr/bin/env python3
"""Phase 8b dataset: pre-Hittite cognate sets → pre-laryngeal PIE targets.

  uv run python -I scripts/build_backtest.py

Writes data/research/backtest/{primary,secondary}.jsonl and meta.json:
- inputs: attested daughter forms only (primary), or attested plus the
  notation-clean proto-languages (secondary). Anatolian and Tocharian are
  removed, and so is any language whose forms write laryngeal notation in
  more than 2% of cases (the Wiktionary proto-languages that encode the
  theory). Romanizations keep length and accent: they are the signal.
- target: the PIE form as pre-laryngeal handbooks wrote it
  (pie/prelaryngeal.py), with the laryngeal effects and their offsets as
  the gold standard, and the modern form for reference.
- hittite: Anatolian reflexes, held aside for the confirmation check only.
- split: whole root families held out (10% eval, 10% dev), by hash.
"""

import collections
import hashlib
import json
import re
import sys
from pathlib import Path

from pie.prelaryngeal import convert

ROOT = Path(__file__).resolve().parent.parent
LAR = re.compile(r"h[₁₂₃ₓ]|ʔ|ə[₁₂₃]")
EXCLUDE = re.compile(r"Hittite|Luwian|Lycian|Palaic|Lydian|Carian|Anatolian|Tocharian")
CONTAMINATION_RATE = 0.02


def split_of(root_id: str) -> str:
    h = int(hashlib.sha256((root_id or "").encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "eval" if h < 0.10 else "dev" if h < 0.20 else "train"


def usable(xs):
    return [x for x in xs if not (x.get("borrowed") or x.get("analogical") or x.get("uncertain"))]


def main() -> int:
    lex = [json.loads(l) for l in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()]
    # 1. contamination scan, per language, by rate
    tot, bad = collections.Counter(), collections.Counter()
    for e in lex:
        for lang, xs in e.get("reflexes", {}).items():
            for x in xs:
                tot[lang] += 1
                bad[lang] += bool(LAR.search((x.get("form") or "") + " " + (x.get("roman") or "")))
                if lang.startswith("Proto-") and re.search(r"(?<![A-Za-z])H|H(?![a-z])", x.get("form") or ""):
                    bad[lang] += 1
    contaminated = sorted(l for l in tot if bad[l] / tot[l] > CONTAMINATION_RATE)
    contaminated += [l for l in ("Proto-Balto-Slavic",) if l not in contaminated]   # its acute encodes the theory
    out = {"primary": [], "secondary": []}
    for e in lex:
        if e["kind"] == "affix":
            continue
        refl = e.get("reflexes", {})
        try:
            target, effects = convert(e["form"])
        except ValueError:
            continue
        hitt = {l: [x.get("roman") or x["form"] for x in usable(xs)] for l, xs in refl.items() if EXCLUDE.search(l)}
        for run, allow_proto in (("primary", False), ("secondary", True)):
            inputs = {}
            for lang, xs in sorted(refl.items()):
                if EXCLUDE.search(lang) or lang in contaminated or (lang.startswith("Proto-") and not allow_proto):
                    continue
                forms = [x.get("roman") or x["form"] for x in usable(xs)]
                if forms:
                    inputs[lang] = forms
            if len(inputs) < 2:
                continue
            out[run].append({"id": e["id"], "root_id": e.get("root_id"), "split": split_of(e.get("root_id") or e["id"]),
                             "inputs": inputs, "target": target,
                             "effects": [{"kind": x.kind, "laryngeal": x.laryngeal, "offset": x.offset} for x in effects],
                             "modern": e["form"], "hittite": hitt or None})
    d = ROOT / "data" / "research" / "backtest"
    d.mkdir(parents=True, exist_ok=True)
    meta = {"contaminated_excluded": contaminated, "excluded_branches": "Anatolian, Tocharian",
            "contamination_rate_threshold": CONTAMINATION_RATE}
    for run, rows in out.items():
        (d / f"{run}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
        c = collections.Counter(r["split"] for r in rows)
        meta[run] = {"sets": len(rows), "with_laryngeal_effect": sum(1 for r in rows if r["effects"]),
                     "by_split": dict(c), "with_hittite": sum(1 for r in rows if r["hittite"]),
                     "languages": len({l for r in rows for l in r["inputs"]})}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
