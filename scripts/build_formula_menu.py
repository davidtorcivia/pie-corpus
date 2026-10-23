#!/usr/bin/env python3
"""Formula menu for Tier 3 planners: known formulas (data/formulas/formulas.jsonl)
whose words all map to usable lexemes, so a plan can use the inherited phrase.

  uv run python -I scripts/build_formula_menu.py

A full word maps through the validator index (ḱléwos → pie-lex-kjlewos),
trying an initial laryngeal the books omit. Core phrases are curated in CORE. Writes data/generation/formula_menu.json.
"""

import json
import re
import sys
from pathlib import Path

from pie.formulas import load
from pie.liv import _plain
from pie.realize import Lexicon
from pie.validate import key, load_index, validate_text

ROOT = Path(__file__).resolve().parent.parent


CORE = [
    ("imperishable fame", ["ḱléwos", "ń̥dʰgʷʰitos"], "ḱléwos with MOD ń̥dʰgʷʰitos (n.)",
     "Ved. śrávas ákṣitam, Gk κλέος ἄφθιτον; Watkins 1995 ch. 15, West 2007 ch. 10"),
    ("great fame", ["ḱléwos", "méǵh₂s"], "ḱléwos with MOD méǵh₂s", "Ved. máhi śrávas, Gk μέγα κλέος; Watkins 1995"),
    ("good fame", ["ḱléwos", "h₁wésus"], "ḱléwos with MOD h₁wésus", "Ved. vásu śrávas, Gk ἐῢ κλέος; West 2007"),
    ("slew the serpent", ["gʷʰénti", "h₁ógʷʰis"], "V gʷʰénti (PST) with OBJ h₁ógʷʰis",
     "Ved. áhann áhim, Gk ἔπεφνε ... ὄφιν; Watkins 1995 (the dragon-slaying formula)"),
    ("swift horses", ["h₁éḱwos", "HéHḱus"], "h₁éḱwos (PL) with MOD HéHḱus",
     "Ved. āśávo áśvāḥ, Gk ὠκέες ἵπποι; Watkins 1995"),
    ("master of the house", ["pótis", "dṓm"], "pótis with POSS dṓm (gen. déms)", "Ved. dámpati-, Gk δεσπότης; Watkins 1995"),
    ("Father Sky", ["dyḗws", "ph₂tḗr"], "VOC dyḗws + VOC ph₂tḗr (dyéw ph₂ter)", "Ved. dyàuṣ pitā́, Gk Ζεῦ πάτερ, Lat. Iuppiter; West 2007 ch. 4"),
    ("Mother Earth", ["dʰéǵʰōm", "méh₂tēr"], "dʰéǵʰōm with apposed méh₂tēr", "Ved. pṛthivī́ mātā́; West 2007 ch. 4"),
    ("Dawn, daughter of Sky", ["h₂éwsōs", "dʰugh₂tḗr", "dyḗws"], "h₂éwsōs, dʰugh₂tḗr with POSS dyḗws (gen. diwés)",
     "Ved. duhitā́ diváḥ, Gk Διὸς θυγάτηρ; West 2007 ch. 5"),
    ("famous name", ["h₁nómn̥", "ḱlutós"], "h₁nómn̥ with MOD ḱlutós (n.)", "Gk ὄνομα κλυτόν, Ved. śrútyaṃ nā́ma; Watkins 1995"),
    ("giver of good things", ["déh₃tōr", "h₁wésus"], "déh₃tōr with POSS h₁wésus (n. gen. pl.)",
     "Ved. dātā́ vásūnām, Gk δωτῆρες ἐάων; Watkins 1995"),
    ("wheel of the sun", ["kʷékʷlos", "sóh₂wl̥"], "kʷékʷlos with POSS sóh₂wl̥", "Ved. sū́ryasya cakrám; West 2007 ch. 5"),
    ("set a name", ["h₁nómn̥", "dʰéh₁t"], "V dʰéh₁t (AOR) with OBJ h₁nómn̥", "Gk ὄνομα θέσθαι, Hitt. lāman dāi-; West 2007"),
]


def main() -> int:
    lx, ix = Lexicon.load(), load_index()
    usable = {i for i, r in lx.specs.items() if r.get("usable") and i not in lx.blocked}
    roots = {}
    for e in lx.entries.values():
        if e["kind"] == "root":
            roots.setdefault(key(e["form"].strip("-"), "generic-H"), e["id"])
    kids = {}
    for i in usable:
        kids.setdefault(lx.entries[i].get("root_id"), []).append(i)

    def by_root(stem):
        rid = roots.get(key(stem.strip("-"), "generic-H"))
        if rid is None:
            return None
        cands = kids.get(rid, [])
        return max(cands, key=lambda i: len(lx.entries[i].get("reflexes", {})), default=None)

    menu = []
    for f in load():
        if f["kind"] not in ("phrase", "lexical") or not f.get("pie") or f["flags"]:
            continue
        words = [w for w in re.split(r"[\s,]+|…|\.\.\.", f["pie"]) if w.strip("-")]
        if len(words) < 2:
            continue
        ids = []
        for w in words:
            lid = None
            if not w.endswith("-"):
                # Watkins and West often omit an initial laryngeal (ógʷʰim for h₁ógʷʰim)
                tries = [w] + ([lar + w for lar in ("h₁", "h₂", "h₃")] if re.match("[aeiouáéíóúāēīōū]", w) else [])
                for cand in tries:
                    t = validate_text(cand.replace("-", ""), ix)["tokens"]
                    if t and t[0].found and t[0].analyses[0].lex_id in usable:
                        lid = t[0].analyses[0].lex_id
                        break
            # (a bare root is not mapped: root → lexeme guesses mapped *terh₂- to the noun tórmos)
            if not lid:
                break
            ids.append(lid)
        if len(ids) == len(words) and len(set(ids)) == len(ids) and \
                tuple(sorted(ids)) not in {tuple(sorted(x["lex_id"] for x in m["lexemes"])) for m in menu}:
            menu.append({"formula_id": f["formula_id"], "english": f["english"], "pie_printed": f["pie_printed"],
                         "lexemes": [{"lex_id": i, "form": lx.entries[i]["form"], "gloss": lx.meaning(i)[0][:40]}
                                     for i in ids], "source": f["source"]})
    # Core inherited phrases, curated in canonical notation (the extracted strings are too
    # irregular to map automatically). Each is verified to map onto usable lexemes.
    by_form = {}
    for i in usable:
        by_form.setdefault(lx.entries[i]["form"], i)
    done = {tuple(sorted(x["lex_id"] for x in m["lexemes"])) for m in menu}
    for english, words, how, ref in CORE:
        ids = [by_form.get(w) for w in words]
        if None in ids:
            print("  core formula skipped (word not usable):", english, [w for w, i in zip(words, ids) if not i])
            continue
        if tuple(sorted(ids)) in done:
            continue
        menu.append({"formula_id": None, "english": english, "pie_printed": None, "how": how, "ref": ref,
                     "lexemes": [{"lex_id": i, "form": lx.entries[i]["form"], "gloss": lx.meaning(i)[0][:40]}
                                 for i in ids], "source": "core"})
    out = ROOT / "data" / "generation" / "formula_menu.json"
    out.write_text(json.dumps(menu, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{len(menu)} formulas usable by planners → {out}")
    for m in menu[:12]:
        print("  ", m["english"][:40], "|", " + ".join(x["form"] for x in m["lexemes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
