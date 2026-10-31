#!/usr/bin/env python3
"""Ask the lexicon for a word: the planners' query tool beside their slice (owner, 2026-10-30).

The slice says "these words fit this batch"; lexq answers "what is the word for X?" over every word a planner may
use: the same pool and eligibility as scripts/make_slice.py (usable, unblocked, accented, glossed; the everyday
and inherited lists), with the same entry format (make_slice.slice_item), so a word found here is used exactly
like a slice word.

    uv run python -I scripts/lexq.py fear summer "be silent"      # English → candidates, best first
    uv run python -I scripts/lexq.py --id pie-lex-bhebhoyh2e      # one word in full: its cells
    uv run python -I scripts/lexq.py --tier3b money               # Tier 3b batches also see the neologisms

Matching, per term: a lexeme whose gloss sense is headed by the term (lemmatized: 'to be giving' answers 'give'),
then any gloss containing the term as a word. Ranked by sense order, corpus use and attestation. Adverbs and
adpositions (indeclinable, role ADV) and the closed-class ids are searched too. One JSON object per line.
"""
import argparse
import collections
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie.realize import Lexicon, closed_adverb_ids  # noqa: E402

_spec = importlib.util.spec_from_file_location("make_slice", ROOT / "scripts" / "make_slice.py")
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)


def corpus_uses() -> collections.Counter:
    c = collections.Counter()
    for f in sorted((ROOT / "corpus").glob("tier*/*.jsonl")):
        for line in f.read_text("utf-8").splitlines():
            for t in json.loads(line).get("tokens") or []:
                if t.get("lex_id"):
                    c[t["lex_id"]] += 1
    return c


def pool(lx, tier3b: bool) -> list[str]:
    ids = ms.offered(lx)
    extra = ms.EVERYDAY + ms.TIER3B_INHERITED + ms.CONVERSATION
    ids += [i for i in extra if i not in ids and lx.specs.get(i, {}).get("usable") and i not in lx.blocked
            and ms.planner_accent_ok(lx, i)]
    if tier3b:
        ids += [i for i in lx.specs if lx.coined(i) == "neologism" and i not in ids and i not in lx.blocked]
    return ids


# a function word is looked up among adverbs, adpositions and closed ids, not inside content words' glosses
FUNCTION_WORDS = {"with", "in", "on", "at", "to", "from", "of", "by", "for", "and", "or", "not", "the", "a", "here",
                  "there", "now", "then", "up", "down", "out", "over", "under", "before", "after", "away"}


def words(s: str) -> set[str]:
    return set(re.findall(r"[a-z]+", s.lower()))


def search(term: str, lx, ids: list[str], uses, n: int) -> list[dict]:
    t = term.lower().strip()
    tw = words(t)
    scored = []
    for i in ids:
        gl, _ = lx.meaning(i)
        gl = (ms.VALENCY.get(i, {}).get("gloss") or gl or "").lower()
        senses = [re.sub(r"^(to |be )+", "", x.strip()) for x in re.split(r"[;,]", gl) if x.strip()]
        rank = next((k for k, x in enumerate(senses)
                     if x == t or (t not in FUNCTION_WORDS and x.split(" ")[0] == t)), None)
        if rank is None and (t in FUNCTION_WORDS or not (tw and tw <= words(gl))):
            continue
        exact = rank is not None and senses[rank] == t       # 'one' itself before 'one who begets'
        score = (0 if rank is not None else 10) + (rank or 0) - 5 * exact - min(uses[i], 400) / 100 - ms.attested_in(lx, i) / 20
        scored.append((score, i))
    scored.sort()
    out = [ms.slice_item(lx, i) | {"corpus_uses": uses[i]} for _, i in scored[:n]]
    # adverbs and adpositions (ADV), and closed-class ids, by gloss
    for e in ms.slice_adverbs(lx, lambda i: ms.attested_in(lx, i), n=10_000):
        if tw and tw <= words(e.get("gloss", "")):
            out.append({**e, "family": "adverb", "role": "ADV"})
    for cid in closed_adverb_ids(lx):
        if t in cid.lower():
            out.append({"lex_id": cid, "family": "closed adverb", "role": "ADV"})
    for sec, node in lx.closed.items():
        if not sec.startswith("_") and t in sec.replace("_", " "):
            out.append({"lex_id": f"closed:{sec}", "family": "closed", "note": "see data/morph/closed_class.json"})
    return out


def full(i: str, lx) -> dict:
    item = ms.slice_item(lx, i)
    fam = lx.specs[i]["family"]
    if fam == "adj":
        item["cells"] = {g: lx.admissible_cells(i, g) for g in ("m", "f", "n")}
    else:
        item["cells"] = lx.admissible_cells(i)
    return item


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="*")
    ap.add_argument("--id", action="append", default=[], help="show one lexeme in full (repeatable)")
    ap.add_argument("--tier3b", action="store_true", help="also offer the neologisms (Tier 3b batches only)")
    ap.add_argument("-n", type=int, default=8, help="candidates per term (default 8)")
    a = ap.parse_args()
    lx = Lexicon.load()
    if a.tier3b:
        from pie.neologism import with_neologisms
        lx = with_neologisms(lx)
    for i in a.id:
        if i not in lx.specs:
            print(json.dumps({"lex_id": i, "error": "not an inflectable lexeme (closed ids: data/morph/closed_class.json)"}))
            continue
        print(json.dumps(full(i, lx), ensure_ascii=False))
    if a.terms:
        ids, uses = pool(lx, a.tier3b), corpus_uses()
        for t in a.terms:
            hits = search(t, lx, ids, uses, a.n)
            print(json.dumps({"query": t, "results": len(hits)}, ensure_ascii=False))
            for h in hits:
                print(json.dumps(h, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
