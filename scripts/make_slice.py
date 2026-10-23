#!/usr/bin/env python3
"""Build a lexicon slice for a Tier 3 planning batch: usable, glossed lexemes
chosen by gloss keywords for the genre/theme, plus a core of common verbs,
with the features each lexeme actually has.

  uv run python -I scripts/make_slice.py fable --keywords sheep horse wolf dog cow wool field --size 220
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

from pie.phon import has_accent, parse
from pie.realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent
CORE_VERBS = ["be", "see", "carry", "give", "speak", "say", "go", "come", "know", "eat", "drink", "hear",
              "sit", "stand", "lead", "drive", "kill", "slay", "live", "fear", "seek", "protect", "milk",
              "plough", "walk", "arrive", "seize", "burn", "lie", "put", "become", "split", "cover"]
# always offered when usable, so a concept is never carried by a thin synonym (b001 review Q2)
CORE_NOUNS = ["pie-lex-h2owis", "pie-lex-h1ngwnis", "pie-lex-peh2wr", "pie-lex-h1ekjwos", "pie-lex-gwoxws",
              "pie-lex-kjwox", "pie-lex-wlkwos", "pie-lex-dyexws", "pie-lex-ph2texr", "pie-lex-meh2texr",
              "pie-lex-dhugh2texr", "pie-lex-bhreh2texr", "pie-lex-swesoxr", "pie-lex-h2egjros", "pie-lex-wodr",
              "pie-lex-nokwts", "pie-lex-gjhwexr", "pie-lex-soh2wl"]
# derived glosses are kept only for transparent, productive suffixes (b002 review R1);
# other derived-gloss lexemes need reflexes in at least two branches
TRANSPARENT_SUFFIXES = {"-tōr", "-tḗr", "-éyeti", "-trom", "-tlom", "-tis", "-tus", "-néh₂ti", "-néwti", "-eti"}
BRANCHES = [("Indo-Iranian", r"Sanskrit|Vedic|Avestan|Persian|Pali|Prakrit|Indo-Aryan|Iranian|Hindi|Ossetian|"
             r"Pashto|Khotanese|Sogdian|Bactrian|Kurdish|Parthian|Bengali|Marathi|Punjabi|Nuristani"),
            ("Greek", r"Greek|Hellenic|Mycenaean"), ("Italic", r"Latin|Italic|Oscan|Umbrian|Faliscan"),
            ("Celtic", r"Irish|Welsh|Celtic|Gaulish|Breton|Cornish|Celtiberian|Gaelic|Manx"),
            ("Germanic", r"Germanic|Gothic|Norse|English|German|Saxon|Frisian|Dutch|Icelandic|Swedish|Danish"),
            ("Balto-Slavic", r"Slavic|Slavonic|Lithuanian|Latvian|Prussian|Russian|Polish|Czech|Baltic|Serbo"),
            ("Armenian", r"Armenian"), ("Albanian", r"Albanian"),
            ("Anatolian", r"Hittite|Luwian|Lycian|Palaic|Lydian|Anatolian"), ("Tocharian", r"Tocharian")]
VALENCY = json.loads((Path(__file__).resolve().parent.parent / "data/generation/verb_valency.json").read_text("utf-8"))


def branches(reflexes: dict) -> set[str]:
    out = set()
    for lang, xs in reflexes.items():
        if not any(not (x.get("borrowed") or x.get("analogical")) for x in xs):
            continue
        out.add(next((b for b, pat in BRANCHES if re.search(pat, lang)), lang))
    return out


CLOSED = {
    "closed:personal/1": "I / we (num SG|PL); enclitic forms with \"enclitic\": true",
    "closed:personal/2": "you (num SG|PL); enclitic forms with \"enclitic\": true",
    "closed:demonstrative_so": "this/that, the (MOD with head, or as a pronoun: he/she/it)",
    "closed:relative_yo": "who/which (relative)",
    "closed:interrogative_kwo": "who? which? (m/f/n by head)",
    "closed:interrogative_kwi": "who? what? (kʷís, kʷíd)",
}


def verb_features(cells: dict) -> list[str]:
    feats = set()
    for k in cells:
        parts = k.split(".")
        voice = "MID" if parts[0] == "MID" else "ACT"
        if parts[0] == "MID":
            parts = parts[1:]
        if parts[0] in ("PRS", "PST", "AOR", "PRF"):
            feats.add(f"IND {parts[0]} {voice}")
        elif parts[0] in ("IMP", "SBJV", "OPT"):
            feats.add(f"{parts[0]} {voice}")
    return sorted(feats)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--size", type=int, default=220)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--derived", action="store_true", help="include lexemes with approximate derived glosses")
    ap.add_argument("--core", nargs="*", default=[],
                    help="up to 8 theme-core lexeme ids, capped at 15 uses per batch instead of 6")
    args = ap.parse_args()
    lx = Lexicon.load()
    rng = random.Random(args.seed)
    ap_derived = args.derived

    def derived_ok(i):
        suffix = lx.derived[i].split("[", 1)[-1].split(":", 1)[0].strip()
        return suffix in TRANSPARENT_SUFFIXES or len(branches(lx.entries[i].get("reflexes", {}))) >= 2

    def accented(i):
        try:
            return has_accent(parse(lx.entries[i]["form"].strip("-")))
        except ValueError:
            return False

    # gates (tier3-b001/b002 reviews): an accented headword (P10), and a derived gloss
    # only for a transparent suffix or a word attested in two branches (R1)
    pool = [i for i, r in lx.specs.items() if r.get("usable") and i not in lx.blocked and accented(i) and
            (lx.entries[i]["meaning"] or (ap_derived and i in lx.derived and derived_ok(i)))]

    def attested(i):
        """Daughter languages with a reflex (of the lexeme, or else its root): prefer well-attested words."""
        e = lx.entries[i]
        n = len(e.get("reflexes", {}))
        return n or len(lx.entries.get(e.get("root_id") or "", {}).get("reflexes", {}))

    def hits(i, words):
        g = " " + re.sub(r"[^a-z]+", " ", (lx.meaning(i)[0] or "").lower()) + " "
        return any(f" {w} " in g for w in words)

    # keyword hits: dictionary-glossed first, then well attested; a derived-gloss
    # lexeme only if its (root, family) isn't represented yet (a root's many
    # derived presents would otherwise flood the slice)
    hits_all = sorted((i for i in pool if hits(i, args.keywords)),
                      key=lambda i: (lx.meaning(i)[1] != "wiktionary", -attested(i)))
    chosen, seen_rf = [], set()
    for i in hits_all:
        rf = (lx.entries[i].get("root_id"), lx.specs[i]["family"])
        if lx.meaning(i)[1] == "derived" and rf in seen_rf:
            continue
        seen_rf.add(rf)
        chosen.append(i)
    chosen = chosen[: args.size]
    chosen += [i for i in pool if lx.specs[i]["family"] == "verb" and hits(i, CORE_VERBS) and i not in chosen
               and lx.meaning(i)[1] == "wiktionary"]
    chosen += [i for i in CORE_NOUNS if i in pool and i not in chosen]
    # random fill: dictionary-glossed or well-attested words only (b002 review R3)
    rest = [i for i in pool if i not in chosen and (lx.meaning(i)[1] == "wiktionary" or attested(i) >= 3)]
    rng.shuffle(rest)
    # balance the fill by family so verbs (now plentiful, with the LIV² aorists) don't crowd out
    # nouns and adjectives: about 40% nouns and 8% adjectives in the whole slice
    target = {"noun": round(0.40 * args.size), "adj": round(0.08 * args.size)}
    for fam in ("noun", "adj"):
        have = sum(1 for i in chosen if lx.specs[i]["family"] == fam)
        add = [i for i in rest if lx.specs[i]["family"] == fam][: max(0, target[fam] - have)]
        chosen += add
    rest = [i for i in rest if i not in set(chosen)]
    chosen += rest[: max(0, args.size - len(chosen))]
    items = []
    for i in chosen[: max(args.size, len(chosen))]:
        e, r = lx.entries[i], lx.specs[i]
        gl, src = lx.meaning(i)
        item = {"lex_id": i, "form": e["form"], "gloss": (VALENCY.get(i, {}).get("gloss") or gl)[:90],
                "family": r["family"]}
        if i in VALENCY:
            item["valency"] = VALENCY[i]["valency"]
        if src == "derived":
            item["gloss_approximate"] = True   # root meaning + suffix function, not a dictionary gloss
        if r["family"] == "noun":
            item["gender"] = lx.gender(i)
        item["attested_in"] = attested(i)
        if r["family"] == "verb":
            feats = verb_features(lx.cells(i))
            if e["form"].endswith(("tor", "toy")):     # deponent: middle only
                feats = [f for f in feats if f.endswith("MID")]
                item["deponent"] = True
            item["features"] = feats
        items.append(item)
    out = ROOT / "data" / "generation" / "slices" / f"{args.name}.json"
    core = [i for i in args.core if i in {it["lex_id"] for it in items}][:8]
    out.write_text(json.dumps({"name": args.name, "keywords": args.keywords, "closed": CLOSED, "theme_core": core,
                               "lexemes": items},
                              ensure_ascii=False, indent=1) + "\n", "utf-8")
    fam = {}
    for it in items:
        fam[it["family"]] = fam.get(it["family"], 0) + 1
    print(f"{out}: {len(items)} lexemes {fam}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
