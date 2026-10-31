#!/usr/bin/env python3
"""Ask the lexicon for a word: the planners' query tool beside their slice (owner, 2026-10-30).

The slice says "these words fit this batch"; lexq answers "what is the word for X?" over every word a planner may
use: the same pool and eligibility as scripts/make_slice.py (usable, unblocked, accented, glossed; the everyday
and inherited lists), with the same entry format (make_slice.slice_item), so a word found here is used exactly
like a slice word.

    uv run python -I scripts/lexq.py fear summer "be silent"      # English → candidates, best first
    uv run python -I scripts/lexq.py --id pie-lex-bhebhoyh2e      # one word in full: its cells (an id
                                                                  # planners may not use: an error + the one to use)
    uv run python -I scripts/lexq.py --tier3b money               # Tier 3b batches also see the neologisms

Matching, per term: a lexeme whose gloss sense is headed by the term (lemmatized: 'to be giving' answers 'give'),
then any gloss containing the term as a word. Ranked by sense order, corpus use and attestation. Adverbs and
adpositions (indeclinable, role ADV) and the closed-class ids are searched too. One JSON object per line.

Idioms (data/lexicon/idioms.json): a concept with no single word ('answer', 'tomorrow', 'yes', 'for three days',
'raid') has an inherited idiom or a stated paraphrase. Every query prints the matching entries after the words, as
{"idiom": …, "kind", "ids", "how", "source"}; the ids are ordinary planner words (coinages only with --tier3b).
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


def singular(w: str) -> str:
    """A plural -s dropped (tears → tear, cows → cow; not 'grass', 'us')."""
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def gloss_words(s: str) -> set[str]:
    """A gloss's words with their singulars, so 'ash' finds kónHis 'ashes, dust' (-es dropped too; t100 could not
    find 'ash'). Only the gloss side: the query is matched as written."""
    out = set()
    for w in words(s):
        out |= {w, singular(w)} | ({w[:-2]} if len(w) > 4 and w.endswith("es") else set())
    return out


def search(term: str, lx, ids: list[str], uses, n: int) -> list[dict]:
    """The candidates for a term; a plural with no hit of its own is looked up in the singular ('tears' →
    dáḱru 'tear': NEXT.md round 5)."""
    out = _search(term, lx, ids, uses, n)
    t = term.lower().strip()
    sg = " ".join(singular(w) for w in t.split())
    return out or (_search(sg, lx, ids, uses, n) if sg != t else out)


def _search(term: str, lx, ids: list[str], uses, n: int) -> list[dict]:
    t = term.lower().strip()
    tw = words(t)
    scored = []
    for i in ids:
        gl, _ = lx.meaning(i)
        gl = (ms.VALENCY.get(i, {}).get("gloss") or gl or "").lower()
        senses = [re.sub(r"^(to |be )+", "", x.strip()) for x in re.split(r"[;,]", gl) if x.strip()]
        rank = next((k for k, x in enumerate(senses)
                     if x == t or (t not in FUNCTION_WORDS and (x.split(" ")[0] == t or (
                         x.split(" ")[0].isalpha() and t in gloss_words(x.split(" ")[0]))))), None)
        if rank is None and (t in FUNCTION_WORDS or not (tw and tw <= gloss_words(gl))):
            continue
        # 'one' itself before 'one who begets'; 'ash' is 'ashes'
        exact = rank is not None and (senses[rank] == t or " " not in senses[rank])
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


IDIOMS = ROOT / "data" / "lexicon" / "idioms.json"


def idioms(term: str, tier3b: bool = False) -> list[dict]:
    """The idiom entries for a query: its English phrase, or every content word of the query, is in an entry's
    `english` list (a plural -s is dropped). Coinage ids (`tier3b_ids`) only for Tier 3b."""
    norm = singular
    t = term.lower().strip()
    tw = {norm(w) for w in words(t)} - FUNCTION_WORDS
    out = []
    for e in json.loads(IDIOMS.read_text("utf-8"))["idioms"]:
        keys = [k.lower() for k in e["english"]]
        if t in keys or (tw and any(tw <= {norm(w) for w in words(k)} for k in keys)):
            hit = {"idiom": e["idiom"], "kind": e["kind"], "for": e["english"], "ids": e["ids"], "how": e["how"],
                   "source": e["source"]}
            if tier3b and e.get("tier3b_ids"):
                hit["tier3b_ids"] = e["tier3b_ids"]
            out.append(hit)
    return out


def full(i: str, lx) -> dict:
    item = ms.slice_item(lx, i)
    fam = lx.specs[i]["family"]
    if fam == "adj":
        item["cells"] = {g: lx.admissible_cells(i, g) for g in ("m", "f", "n")}
    else:
        item["cells"] = lx.admissible_cells(i)
    return item


def _skeleton(s: str) -> str:
    """An id or form reduced to what a planner keeps when typing it: no accents, no 'j'/'x' diacritic letters
    (ǵ → gj, ō → ox), no -2 homograph suffix (pie-lex-gjhlh2dhros and pie-lex-ghlh2dhros meet)."""
    import unicodedata
    s = re.sub(r"-\d+$", "", s.removeprefix("pie-lex-").removeprefix("pie-proj-"))
    s = unicodedata.normalize("NFD", s)
    return re.sub(r"[̀-ͯjx]", "", s)


def lookup_id(i: str, lx, ids: list[str]) -> dict:
    """`--id`: an offered word in full; anything else an error line that names the id to use instead. A planner
    who typed the id from a form (pie-lex-sleh2gwt for the aorist pie-lex-sleh2gwt-2, pie-lex-gjhlh2dhros for
    pie-lex-ghlh2dhros) was shown a bare entry with no cells, and check_plan then rejected it (t096)."""
    if i in ids:
        return full(i, lx)
    sk = _skeleton(i)
    same = [j for j in ids if _skeleton(j) == sk]
    if i in lx.specs:
        r = lx.specs[i]
        why = ("blocklisted" if i in lx.blocked else
               f"no usable spec (rule {r.get('rule')})" if not r.get("usable") else
               "not offered to planners (no gloss, no accent, NIL-held or an evaluation holdout)")
        return {"lex_id": i, "form": lx.entries[i]["form"], "error": f"not a planner word: {why}", "use": same}
    if i.startswith("closed:"):
        return {"lex_id": i, "error": "not an inflectable lexeme (closed ids: data/morph/closed_class.json)"}
    return {"lex_id": i, "error": "unknown id", "use": same}


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
    ids = pool(lx, a.tier3b) if a.id or a.terms else []
    for i in a.id:
        print(json.dumps(lookup_id(i, lx, ids), ensure_ascii=False))
    if a.terms:
        uses = corpus_uses()
        for t in a.terms:
            hits = search(t, lx, ids, uses, a.n)
            ims = idioms(t, a.tier3b)
            print(json.dumps({"query": t, "results": len(hits), "idioms": len(ims)}, ensure_ascii=False))
            for h in hits + ims:
                print(json.dumps(h, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
