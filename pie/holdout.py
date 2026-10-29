"""The benchmark hold-out: root families kept out of training so the cognate→PIE and inflection tasks
test unseen families (pie.export.eval_root, the one predicate every caller uses).

Two generated files, written by scripts/build_holdout.py (its docstring documents the selection):

  data/export/protected_roots.json  root families that must never be held out (formula vocabulary,
                                     Tier 2 secure lexemes, make_slice's core lists, Swadesh-type
                                     kin terms, numerals, body parts and natural-world nouns, and the
                                     Swadesh-207, Leipzig-Jakarta and conversational-core concepts),
                                     each with its reasons
  data/export/held_roots.json       the held-out families, frozen at selection time

The hold-out is a frozen list, not a hash predicate: until 2026-10-28 a 10% sha256 hash of root_id
decided it, which held out core formula vocabulary (dʰugh₂tḗr, so "Daughter of Sky" could not
appear in training texts). The hash now only ranks families inside the eligible pool. A family
outside the frozen list (one added to the lexicon later) is not held out. Benchmark scores from
before and after the swap are not comparable (docs/STATUS.md "Known limitations"). Redrawn
2026-10-29 so that core everyday families (help, drink, hear, water, day, …) are trainable, before
any model was trained.
"""

from __future__ import annotations

import functools
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTECTED_PATH = ROOT / "data" / "export" / "protected_roots.json"
HELD_PATH = ROOT / "data" / "export" / "held_roots.json"


def hash_rank(root_id: str) -> float:
    """The deterministic rank of a family inside the eligible pool (the old predicate's hash)."""
    return int(hashlib.sha256(root_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


@functools.lru_cache(maxsize=None)
def protected_roots() -> frozenset[str]:
    if not PROTECTED_PATH.exists():     # a hold-out without its protected set is a broken state
        raise FileNotFoundError(f"{PROTECTED_PATH} missing: run scripts/build_holdout.py")
    return frozenset(json.loads(PROTECTED_PATH.read_text("utf-8"))["roots"])


@functools.lru_cache(maxsize=None)
def held_roots() -> frozenset[str]:
    d = json.loads(HELD_PATH.read_text("utf-8"))
    held = frozenset(d["held"])
    clash = held & protected_roots()
    if clash:
        raise ValueError(f"protected root family in the hold-out: {sorted(clash)[:3]}")
    return held
