"""Corpus-quality batch 2: the measured exception table for capitalised Greek lemmas.

  UV_CACHE_DIR=/tmp/pie-uv-cache uv run python -I scripts/cq2_greek_capitals.py INDEX.sqlite

Reads a search index built before batch 2 (read-only; the cq1 index, corpora.pre-cq2.sqlite) and the
Kaikki Ancient Greek dump (parsed, never executed), and writes
data/research/formulas/cq2-greek-capitalised.json. The rule itself is pie/cq2_other.py
(greek_capitalised); this script only freezes the measured list it needs:

  common: capitalised lemmas (grc, grc-late, hom content words with ids) whose lowercase-initial
          lemma (accents kept) is at least RATIO times as frequent in the same corpora and which are not
          a capitalised Kaikki headword: sentence-initial or title capitals of common words (Λόγος,
          Πόλις, Ἀγαθός, Εἰμί). They keep the common lemma.
Every other capitalised lemma with a lower-case letter is a name (through pie.name_mapping.name_lemma,
which keeps the THEONYMS deities); function words and verbs are rules in pie/cq2_other.py.
"""
import collections
import json
import sqlite3
import sys
import unicodedata
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KAIKKI = ROOT / "raw/daughters/kaikki-ancientgreek/kaikki.org-dictionary-AncientGreek.jsonl"
OUT = ROOT / "data/research/formulas/cq2-greek-capitalised.json"
CORPORA = ("grc", "grc-late", "hom")
RATIO = 100


def nfc(s):
    return unicodedata.normalize("NFC", s)


def lower_initial(s):
    s = unicodedata.normalize("NFD", s)
    return nfc(s[:1].lower() + s[1:])


def main(index):
    db = sqlite3.connect(f"file:{index}?mode=ro", uri=True)
    q = ",".join("?" * len(CORPORA))
    lemma_units = collections.Counter()
    for v, n in db.execute("select t.value,count(*) from terms t join postings p on p.term=t.id join units u "
                           f"on u.id=p.unit where t.kind='lemma' and u.corpus in ({q}) group by t.id", CORPORA):
        lemma_units[nfc(v)] = n
    caps = collections.Counter()
    for (p,) in db.execute(f"select payload from units where corpus in ({q})", CORPORA):
        for w in json.loads(zlib.decompress(p))["words"]:
            lem = nfc(w["lemma"])
            if lem[:1].isupper() and any(c.islower() for c in lem) and w["root_ids"] and not lem.endswith("(name)"):
                caps[lem] += 1
    heads = set()
    with open(KAIKKI, encoding="utf-8") as fh:
        for line in fh:
            w = nfc(json.loads(line).get("word") or "")
            if w[:1].isupper():
                heads.add(w)
    common = sorted(l for l, n in caps.items() if l not in heads and lemma_units.get(lower_initial(l), 0) >= RATIO * n)
    OUT.write_text(json.dumps({
        "_doc": "pie/cq2_other.py greek_capitalised: capitalised lemmas that keep their common (lower-case) "
                "lemma; written by scripts/cq2_greek_capitals.py from the pre-batch-2 index "
                f"(lowercase lemma units >= {RATIO} x capitalised tokens, not a capitalised Kaikki headword).",
        "measured_on": {"corpora": list(CORPORA), "capitalised_lemma_types": len(caps),
                        "capitalised_tokens": sum(caps.values()),
                        "common_types": len(common), "common_tokens": sum(caps[l] for l in common)},
        "common": common}, ensure_ascii=False, indent=0) + "\n", "utf-8")
    print(len(caps), sum(caps.values()), len(common), sum(caps[l] for l in common))


if __name__ == "__main__":
    main(sys.argv[1])
