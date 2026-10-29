#!/usr/bin/env python3
"""Collect the Wiktionary glosses of the daughter reflexes of every unglossed lexeme.

  uv run python -I scripts/build_reflex_glosses.py [--daughters raw/daughters]

For each lexicon entry without a dictionary gloss, each reflex (language, form) is looked up in that language's
kaikki.org dump, and the glosses of the matching entries are recorded with the PIE etyma their etymologies cite.
The dumps are gitignored (raw/), so the result is committed: data/lexicon/reflex_glosses.jsonl. It holds facts
only; the rule that promotes a derived gloss on this evidence is pie.glosses.confirm (docs/lexicon.md
"Reflex-confirmed glosses").
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "lexicon" / "reflex_glosses.jsonl"
SPLIT = "kaikki-all-20261021/split/"
# reflex language (as lexicon.jsonl names it) -> dump under raw/daughters, and the dump's own language name
DUMPS = {
    "Proto-Germanic": ("kaikki-protogermanic/kaikki.org-dictionary-ProtoGermanic.jsonl", "Proto-Germanic"),
    "Proto-Indo-Iranian": ("kaikki-protoindoiranian/kaikki.org-dictionary-ProtoIndoIranian.jsonl", "Proto-Indo-Iranian"),
    "Ancient Greek": ("kaikki-ancientgreek/kaikki.org-dictionary-AncientGreek.jsonl", "Ancient Greek"),
    "Sanskrit": ("kaikki-sanskrit/kaikki.org-dictionary-Sanskrit.jsonl", "Sanskrit"),
    "Vedic Sanskrit": ("kaikki-sanskrit/kaikki.org-dictionary-Sanskrit.jsonl", "Sanskrit"),
    "Proto-Italic": ("kaikki-protoitalic/kaikki.org-dictionary-ProtoItalic.jsonl", "Proto-Italic"),
    "Latin": ("kaikki-latin/kaikki.org-dictionary-Latin.jsonl", "Latin"),
    "Old Latin": ("kaikki-latin/kaikki.org-dictionary-Latin.jsonl", "Latin"),
    "Proto-Indo-Aryan": (SPLIT + "proto-indo-aryan.jsonl", "Proto-Indo-Aryan"),
    "Proto-Balto-Slavic": ("kaikki-protobaltoslavic/kaikki.org-dictionary-ProtoBaltoSlavic.jsonl", "Proto-Balto-Slavic"),
    "Proto-Hellenic": (SPLIT + "proto-hellenic.jsonl", "Proto-Hellenic"),
    "Proto-Celtic": ("kaikki-protoceltic/kaikki.org-dictionary-ProtoCeltic.jsonl", "Proto-Celtic"),
    "Proto-Slavic": ("kaikki-protoslavic/kaikki.org-dictionary-ProtoSlavic.jsonl", "Proto-Slavic"),
    "Lithuanian": ("kaikki-lithuanian/kaikki.org-dictionary-Lithuanian.jsonl", "Lithuanian"),
    "Proto-Iranian": ("kaikki-protoiranian/kaikki.org-dictionary-ProtoIranian.jsonl", "Proto-Iranian"),
    "Latvian": ("kaikki-latvian/kaikki.org-dictionary-Latvian.jsonl", "Latvian"),
    "Avestan": (SPLIT + "avestan.jsonl", "Avestan"),
    "Younger Avestan": (SPLIT + "avestan.jsonl", "Avestan"),
    "Old Avestan": (SPLIT + "avestan.jsonl", "Avestan"),
    "Albanian": ("kaikki-albanian/kaikki.org-dictionary-Albanian.jsonl", "Albanian"),
    "Proto-Albanian": (SPLIT + "proto-albanian.jsonl", "Proto-Albanian"),
    "Old Armenian": ("kaikki-oldarmenian/kaikki.org-dictionary-OldArmenian.jsonl", "Old Armenian"),
    "Proto-Armenian": (SPLIT + "proto-armenian.jsonl", "Proto-Armenian"),
    "Hittite": ("kaikki-hittite/kaikki.org-dictionary-Hittite.jsonl", "Hittite"),
    "Proto-Anatolian": (SPLIT + "proto-anatolian.jsonl", "Proto-Anatolian"),
    "Old Irish": ("kaikki-oldirish/kaikki.org-dictionary-OldIrish.jsonl", "Old Irish"),
    "Middle Irish": ("kaikki-middleirish/kaikki.org-dictionary-MiddleIrish.jsonl", "Middle Irish"),
    "Middle Welsh": ("kaikki-middlewelsh/kaikki.org-dictionary-MiddleWelsh.jsonl", "Middle Welsh"),
    "Welsh": (SPLIT + "welsh.jsonl", "Welsh"),
    "Proto-Brythonic": ("kaikki-protobrythonic/kaikki.org-dictionary-ProtoBrythonic.jsonl", "Proto-Brythonic"),
    "Gaulish": (SPLIT + "gaulish.jsonl", "Gaulish"),
    "Tocharian A": ("kaikki-tochariana/kaikki.org-dictionary-TocharianA.jsonl", "Tocharian A"),
    "Tocharian B": ("kaikki-tocharianb/kaikki.org-dictionary-TocharianB.jsonl", "Tocharian B"),
    "Proto-Tocharian": (SPLIT + "proto-tocharian.jsonl", "Proto-Tocharian"),
    "Proto-West Germanic": (SPLIT + "proto-west-germanic.jsonl", "Proto-West Germanic"),
    "Proto-Norse": (SPLIT + "proto-norse.jsonl", "Proto-Norse"),
    "Old Norse": ("kaikki-oldnorse/kaikki.org-dictionary-OldNorse.jsonl", "Old Norse"),
    "Old English": ("kaikki-oldenglish/kaikki.org-dictionary-OldEnglish.jsonl", "Old English"),
    "Old High German": ("kaikki-oldhighgerman/kaikki.org-dictionary-OldHighGerman.jsonl", "Old High German"),
    "Middle High German": (SPLIT + "middle-high-german.jsonl", "Middle High German"),
    "Old Saxon": ("kaikki-oldsaxon/kaikki.org-dictionary-OldSaxon.jsonl", "Old Saxon"),
    "Gothic": ("kaikki-gothic/kaikki.org-dictionary-Gothic.jsonl", "Gothic"),
    "Old Prussian": (SPLIT + "old-prussian.jsonl", "Old Prussian"),
    "Old Lithuanian": (SPLIT + "old-lithuanian.jsonl", "Old Lithuanian"),
    "Old Church Slavonic": ("kaikki-oldchurchslavonic/kaikki.org-dictionary-OldChurchSlavonic.jsonl",
                            "Old Church Slavonic"),
    "Old East Slavic": ("kaikki-oldeastslavic/kaikki.org-dictionary-OldEastSlavic.jsonl", "Old East Slavic"),
    "Old Persian": ("kaikki-oldpersian/kaikki.org-dictionary-OldPersian.jsonl", "Old Persian"),
    "Oscan": (SPLIT + "oscan.jsonl", "Oscan"),
    "Umbrian": ("kaikki-umbrian/kaikki.org-dictionary-Umbrian.jsonl", "Umbrian"),
    "Pali": (SPLIT + "pali.jsonl", "Pali"),
    "Mycenaean Greek": ("kaikki-mycenaeangreek/kaikki.org-dictionary-MycenaeanGreek.jsonl", "Mycenaean Greek"),
}
WORD = re.compile(r'"word": "((?:[^"\\]|\\.)*)", "lang": "')      # the top-level word: it precedes "lang"


def key(s: str) -> str:
    """Lookup key of a citation form: NFC, no leading * or trailing/leading hyphens, lower case."""
    return unicodedata.normalize("NFC", s.strip().lstrip("*").strip("-").lower())


def plain(s: str) -> str:
    """key() without combining marks (length, accents, Vedic svara marks): dictionary titles drop them (Latin lavo
    for lav\u014d, Lithuanian giedu for g\u00ededu). Only a prefilter; a match on it alone is flagged approximate."""
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if not unicodedata.combining(c) and c not in "\u0951\u0952")


def etyma(row: dict) -> list[str]:
    """The reconstructed forms (*x) a dump entry's etymology cites, in order."""
    out = []
    for t in row.get("etymology_templates", []):
        for v in t.get("args", {}).values():
            for m in re.findall(r"\*[^\s,;:()\[\]<>|]+", v):
                if m not in out:
                    out.append(m)
    return out[:12]


def glosses(row: dict) -> list[str]:
    out = []
    for s in row.get("senses", []):
        if s.get("form_of") or s.get("alt_of") or {"form-of", "alt-of"} & set(s.get("tags", [])):
            continue
        for g in s.get("glosses", [])[:1]:
            if g not in out:
                out.append(g[:160])
    return out[:6]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daughters", type=Path, default=ROOT / "raw" / "daughters")
    args = ap.parse_args()
    lex = [json.loads(x) for x in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()]
    todo = [e for e in lex if not e["meaning"] and e["kind"] in ("word", "derivative") and e.get("reflexes")]
    need: dict[str, set[str]] = {}
    for e in todo:
        for lang, xs in e["reflexes"].items():
            if lang in DUMPS:
                for x in xs:
                    need.setdefault(DUMPS[lang][0], set()).add(key(x["form"]))
    found: dict[tuple[str, str], list[dict]] = {}
    for path, keys in sorted(need.items()):
        p = args.daughters / path
        if not p.exists():
            print(f"missing dump {p}", file=sys.stderr)
            continue
        by_plain: dict[str, set[str]] = {}
        for k in keys:
            by_plain.setdefault(plain(k), set()).add(k)
        n = 0
        with p.open(encoding="utf-8") as f:
            for line in f:
                m = WORD.search(line)
                if not m:
                    continue
                w = key(json.loads(f'"{m.group(1)}"'))
                if plain(w) not in by_plain:
                    continue
                row = json.loads(line)
                g = glosses(row)
                if not g:
                    continue
                exact = ({w} | {key(x["form"]) for x in row.get("forms", [])
                                if {"canonical", "romanization"} & set(x.get("tags", []))}) & keys
                # a citation form that differs only in length or Vedic accent marks (Latin lavō under the
                # title lavo, Sanskrit with svara marks): matched, flagged approximate
                hit = exact or by_plain[plain(w)]
                rec = {"pos": row.get("pos"), "glosses": g, "etyma": etyma(row), "lang": row.get("lang"),
                       "approx": not exact}
                for k in hit:
                    found.setdefault((path, k), []).append(rec)
                    n += 1
        print(f"{path}: {len(keys)} forms, {n} entries", file=sys.stderr)
    rows = []
    for e in todo:
        refl = []
        for lang, xs in e["reflexes"].items():
            if lang not in DUMPS:
                continue
            path, dump_lang = DUMPS[lang]
            for x in xs:
                if x.get("borrowed") or x.get("analogical"):
                    continue
                hits = [r for r in found.get((path, key(x["form"])), []) if r["lang"] == dump_lang]
                if hits:
                    refl.append({"lang": lang, "form": x["form"], "entries": [
                        {"pos": r["pos"], "glosses": r["glosses"], "etyma": r["etyma"],
                         **({"approx": True} if r["approx"] else {})} for r in hits[:4]]})
        if refl:
            rows.append({"id": e["id"], "form": e["form"], "reflexes": refl})
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    print(f"{OUT}: {len(rows)} lexemes with reflex glosses (of {len(todo)} unglossed with reflexes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
