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

from pie.compound import CompoundError, resolve as resolve_compound
from pie.glosses import branch
from pie.phon import has_accent, parse
from pie.realize import Lexicon, accent_manifest

ROOT = Path(__file__).resolve().parent.parent
CORE_VERBS = ["be", "see", "carry", "give", "speak", "say", "go", "come", "know", "eat", "drink", "hear",
              "sit", "stand", "lead", "drive", "kill", "slay", "live", "fear", "seek", "protect", "milk",
              "plough", "walk", "arrive", "seize", "burn", "lie", "put", "become", "split", "cover",
              # t033: no 'sing' in the slice (planners wrote mléwH- 'speak') and 'love' only as stérg- 'protect~'
              "sing", "love"]
# always offered when usable, so a concept is never carried by a thin synonym (b001 review Q2)
CORE_NOUNS = ["pie-lex-h2owis", "pie-lex-h1ngwnis", "pie-lex-peh2wr", "pie-lex-h1ekjwos", "pie-lex-gwoxws",
              "pie-lex-kjwox", "pie-lex-wlkwos", "pie-lex-dyexws", "pie-lex-ph2texr", "pie-lex-meh2texr",
              "pie-lex-dhugh2texr", "pie-lex-bhreh2texr", "pie-lex-swesoxr", "pie-lex-h2egjros", "pie-lex-wodr",
              "pie-lex-nokwts", "pie-lex-gjhwexr", "pie-lex-soh2wl", "pie-lex-swos", "pie-lex-wekwos",
              "pie-lex-deywos", "pie-lex-mert", "pie-lex-spert", "pie-lex-kjexr", "pie-lex-h2wlh1neh2",
              "pie-lex-h1lewdheros", "pie-lex-Hroth2os", "pie-lex-suHnus", "pie-lex-h2werst", "pie-lex-gjhutos",
              "pie-lex-h2nexr", "pie-lex-wiHros", "pie-lex-ghostis", "pie-lex-h1sntyos", "pie-lex-kjeywos", "pie-lex-lewbhos",
              "pie-lex-h1weh2yos", "pie-lex-steh2yeti", "pie-lex-perkwunos", "pie-lex-h3rexgjs",
              "pie-lex-bhoydheh2", "pie-lex-HrewdHti", "pie-lex-poh2imexn", "pie-lex-yugom", "pie-lex-yewgt-2",
              "pie-lex-Hyeh1kt", "pie-lex-dremt", "pie-lex-went", "pie-lex-bhewgt-3", "pie-lex-misdhos",
              "pie-lex-potnih2", "pie-lex-kwseps", "pie-lex-kjoymos-2", "pie-lex-neh2us", "pie-lex-polh1us"]
# always offered when usable, for conversation (t024 found no 'which of two', no names, no greetings): kʷóteros, the
# greeting words of planner-brief-v4 ("Greetings and thanks") and the members of its ready-made personal names
CONVERSATION = ["pie-lex-kwoteros", "pie-lex-priHos", "pie-lex-keh2ilos", "pie-lex-h1wesus", "pie-lex-gwemt",
                "pie-lex-deh3t", "pie-lex-gwrneHti", "pie-lex-deh3toxr", "pie-lex-kjlewos", "pie-lex-menos",
                "pie-lex-h1sntyos", "pie-lex-gjenh1os-2",
                # t036 (2026-10-30): everyday words a slice's size cap had squeezed out: woman, young, other,
                # second, fight (n. and v.), choose
                "pie-lex-gwexn", "pie-lex-h2yuHnkjos", "pie-lex-h2elyos", "pie-lex-h1eteros", "pie-lex-keh3tus",
                "pie-lex-wiketi", "pie-lex-welh1t-2"]
# Everyday words every slice offers (2026-10-30: the t036/t039/t042 planners reported day, evening, road, wind, ice,
# summer … missing, though usable: the size cap had squeezed them out). Hand-checked, one lexeme per concept: the
# body, kin, the herd, food and fire, the sky and the seasons, the commonest verbs.
EVERYDAY = [
    "pie-lex-dinos", "pie-lex-nokwts", "pie-lex-wekwsperos", "pie-lex-stoyghos", "pie-lex-h2enh1mos-2",
    "pie-lex-h2werst", "pie-lex-snoygwhos", "pie-lex-h1yegos", "pie-lex-smh2eros", "pie-lex-yoh1r",
    "pie-lex-prexkjst", "pie-lex-h1edti", "pie-lex-peh3t", "pie-lex-swepnos", "pie-lex-doxm", "pie-lex-peh2wr",
    "pie-lex-wodr", "pie-lex-maxdsos", "pie-lex-mexms", "pie-lex-h2egjros", "pie-lex-doru", "pie-lex-h2ekjmox",
    "pie-lex-deh2nu", "pie-lex-soh2wl", "pie-lex-lowksneh2", "pie-lex-h2stexr", "pie-lex-dhegjhoxm",
    "pie-lex-gwoxws", "pie-lex-h2ewis", "pie-lex-kjerh2sox", "pie-lex-gjhostos", "pie-lex-poxds", "pie-lex-h3okws",
    "pie-lex-h2oxws", "pie-lex-h1oh3s", "pie-lex-kjexr", "pie-lex-h1nomn", "pie-lex-wekwos", "pie-lex-keh2nmn",
    "pie-lex-deywos", "pie-lex-h3rexgjs", "pie-lex-ghostis", "pie-lex-bhreh2texr", "pie-lex-swesoxr",
    "pie-lex-suHnus", "pie-lex-dhugh2texr", "pie-lex-ph2texr", "pie-lex-meh2texr", "pie-lex-potnih2",
    "pie-lex-gwexn", "pie-lex-wiHros", "pie-lex-gjerh2onts", "pie-lex-h2yuHnkjos", "pie-lex-h1wesus",
    "pie-lex-megjh2s", "pie-lex-dhebhus", "pie-lex-newos", "pie-lex-sriHgos", "pie-lex-gwmyeti", "pie-lex-h1eyti",
    "pie-lex-widet", "pie-lex-kjlewt", "pie-lex-woyde", "pie-lex-deh3t", "pie-lex-wewket", "pie-lex-bheh2ti",
    "pie-lex-sedyeti", "pie-lex-sth2eh1yeti", "pie-lex-kjeytor", "pie-lex-gwih3weti", "pie-lex-mert",
    "pie-lex-lubhyeti", "pie-lex-bhebhoyh2e", "pie-lex-h2melgjti"
]
# Tier 3b (--tier3b): inherited words the planner brief and the t3b-001 review point to in place of a coinage
# (archaic first): mówdos 'joy' and swéh₂dos 'pleasure' (not géh₂dʰos), néwos 'new' (not h₂énteros 'other' beside
# 'answer'). mówdos is NIL single-branch (Ved. móda-; P9 keeps those out of Tier 3 slices); Tier 3b offers it
# (lead, 2026-10-29), as the inherited word beats a coinage. The review's h₁éwHt 'help' is not listed here; its root
# family pie-root-h1ewH-help is no longer held out (hold-out redrawn 2026-10-29, protected as conversational core),
# so whether to offer it is open. werdʰom has no resolved accent.
# 2026-10-30 (t3b-003/006 planners found no 'want', 'dream', 'grief', 'grandfather' in their slices: usable words
# the keyword match missed): wéḱti 'wish, want' (Hitt. wekzi, Ved. váṣṭi, Gk ἑκών), súpniyom 'dream' (OCS sŭnije,
# Toch. B sänmetse), ḱéh₂dos 'care, grief' (Gk κῆδος, Oscan cadeis), h₂énǵʰos 'anxiety, distress' (PIIr. *Hánȷ́ʰas,
# Lat. angor), h₂éwh₂os 'grandfather' (Hitt. ḫuḫḫa-, Arm. haw); cognates from their lexicon reflexes
# 2026-10-30 dialogue gaps (docs/audits/lexicon-gaps-dialogue-2026-10-30.md; evidence in overrides.jsonl and
# project_reconstructions.jsonl): anger, hunger, milk, play, weave, cup, pot, knife, feast, sad, story, grandmother
TIER3B_INHERITED = ["pie-lex-mowdos", "pie-lex-sweh2dos", "pie-lex-newos", "pie-lex-wekjti", "pie-lex-supniyom",
                    "pie-lex-kjeh2dos", "pie-lex-h2engjhos", "pie-lex-h2ewh2os",
                    "pie-lex-ghremeti", "pie-lex-ghromeyeti", "pie-lex-kenketi", "pie-lex-gwoldhos",
                    "pie-lex-h2melgjos", "pie-lex-loygeti", "pie-lex-teksti", "pie-lex-peh3tlom", "pie-lex-kweros",
                    "pie-lex-kjstrom", "pie-lex-dh2pnom", "pie-lex-lugjros", "pie-proj-spelom", "pie-proj-h2enHos",
                    # 2026-10-30 core gaps (docs/audits/lexicon-gaps-core-2026-10-30.md; evidence in overrides.jsonl):
                    # Swadesh-207, Leipzig-Jakarta and conversational-core concepts, and the t036 council words
                    # (ice h₁yégos, wood dóru and soil dʰéǵʰōm are in EVERYDAY)
                    "pie-lex-mortos", "pie-lex-tekjnom", "pie-lex-peh2uros", "pie-lex-h1orseh2", "pie-lex-skelos",
                    "pie-lex-lowbhos", "pie-lex-h2endhos", "pie-lex-ghreh1mn", "pie-lex-uderos", "pie-lex-gjhorneh2",
                    "pie-lex-skjeh3ih2", "pie-lex-kapros", "pie-lex-h2eghos-2", "pie-lex-puHyeti", "pie-lex-h3regjtos",
                    "pie-lex-ghlh2dhros", "pie-lex-kjubhros", "pie-lex-mudros", "pie-lex-mewdeti", "pie-lex-wregeti",
                    "pie-lex-steygheti", "pie-lex-teryeti", "pie-lex-goleti", "pie-lex-kweh2se", "pie-lex-h3edeti",
                    "pie-lex-bhereti", "pie-lex-deykjeti", "pie-lex-th2keh1yeti", "pie-lex-h3eh3ode-2",
                    "pie-lex-kjekjomh2e", "pie-lex-kjeHst", "pie-lex-h1egos", "pie-lex-gwrHtos", "pie-lex-h2reh1dheti",
                    "pie-lex-dhh1tleh2", "pie-lex-gjnh3ros", "pie-lex-poykjos-2",
                    # 2026-10-31 round 3 (docs/audits/lexicon-gaps-round3-2026-10-31.md; evidence in overrides.jsonl):
                    # war and exchange, conversation (t044-t070 planners), the horrors wave, kinship
                    "pie-lex-Hrowpos", "pie-lex-h1eh1ughos", "pie-lex-tergweti", "pie-lex-skeytos", "pie-lex-keh3tus",
                    "pie-lex-segjhos-2", "pie-lex-dhrsus", "pie-lex-kwinewti", "pie-lex-kweyeti", "pie-lex-kwoyneh2",
                    "pie-lex-gheldheti", "pie-lex-HrewdHti", "pie-lex-wetsos", "pie-lex-semeh2", "pie-lex-solh2wos",
                    "pie-lex-woykjos-2", "pie-lex-kjlowseyeti", "pie-lex-bhoydheyeti", "pie-lex-sprneHti",
                    "pie-lex-gjhewt-2", "pie-lex-h2elgwheti", "pie-lex-h2elgwhos", "pie-lex-dhlghos", "pie-lex-kaptos",
                    "pie-lex-moro", "pie-lex-nekjus", "pie-lex-gwhonos-2", "pie-lex-gwhentoxr", "pie-lex-h1rh1pyeti",
                    "pie-lex-leykwt", "pie-lex-h1yenh2texr", "pie-lex-gjlh2oxws", "pie-lex-swekjruh2", "pie-lex-snusos",
                    "pie-lex-sneh1", "pie-lex-tentlom",
                    "pie-lex-h3epnos", "pie-lex-h1wogwheyeti", "pie-lex-h3orbhos", "pie-lex-sh1esox",
                    # 2026-10-31 round 5 (docs/audits/lexicon-gaps-round5-2026-10-31.md; evidence in overrides.jsonl):
                    # the t073-t094 planners' gaps
                    "pie-lex-h1enih3kwo", "pie-lex-sh2kros", "pie-lex-ish1ros", "pie-lex-h2oyu", "pie-lex-gjenh1eseh2",
                    "pie-lex-gwhedhyeti", "pie-lex-ghostipotis", "pie-lex-mexdeti", "pie-lex-dakjru",
                    "pie-lex-bholgjhis", "pie-lex-h2ekjs", "pie-lex-bhrgjyeti", "pie-lex-h1yagjeti", "pie-lex-mexh1ns",
                    "pie-lex-gwerdus", "pie-lex-dekjsiwos", "pie-lex-uksexn"]
ADVERB_POS = ("adv", "prep", "postp")
NIL_ADMIT = {"pie-lex-bhagos", "pie-lex-bhngjhulos", "pie-lex-bhrtos", "pie-lex-gwowsth2os", "pie-lex-kjh3tos",
             "pie-lex-medtos", "pie-lex-priHtos", "pie-lex-h2rgjipyos", "pie-lex-kjolHtos", "pie-lex-rotos",
             # tail: Gk οὐρά and OIr. err, two branches (Beekes s.v. οὐρά; NIL no. 247): core gaps 2026-10-30
             "pie-lex-h1orseh2"}
NIL_GLOSS_HELD = {"pie-lex-h2gjtos", "pie-lex-priHnos", "pie-lex-h2ewgos", "pie-lex-wersos", "pie-lex-kjltos",
                  "pie-lex-h2egjtoxr", "pie-lex-segjhtoxr"}
# dictionary glosses and the hand-checked ones (overrides, supplement: docs/audits/lexicon-gaps-*.md; project
# reconstructions, glossed from their handbook cognates: docs/lexicon-project-reconstructions.md)
TRUSTED_GLOSS = {"wiktionary", "override", "supplement", "project", "reflex-confirmed"}
# derived glosses are kept only for transparent, productive suffixes (b002 review R1);
# other derived-gloss lexemes need reflexes in at least two branches
TRANSPARENT_SUFFIXES = {"-tōr", "-tḗr", "-éyeti", "-trom", "-tlom", "-tis", "-tus", "-néh₂ti", "-néwti", "-eti"}
VALENCY = json.loads((Path(__file__).resolve().parent.parent / "data/generation/verb_valency.json").read_text("utf-8"))


def branches(reflexes: dict) -> set[str]:
    out = set()
    for lang, xs in reflexes.items():
        if not any(not (x.get("borrowed") or x.get("analogical")) for x in xs):
            continue
        out.add(branch(lang))         # one branch table (pie.glosses.BRANCHES)
    return out


CLOSED_NUMERALS = {
    "closed:numerals/2": "two (MOD with a head; the noun takes the dual)",
    "closed:numerals/3": "three (MOD with a head; the noun takes the plural)",
    "closed:numerals/4": "four (MOD with a head; plural)",
    **{f"closed:numerals/indeclinable/{n}": w + " (MOD with a head; indeclinable)"
       for n, w in (("5", "five"), ("6", "six"), ("7", "seven"), ("8", "eight"), ("9", "nine"), ("10", "ten"),
                    ("100", "a hundred"), ("1000", "a thousand"))},
}
CLOSED = {
    "closed:personal/1": "I / we (num SG|PL); enclitic forms with \"enclitic\": true",
    "closed:personal/2": "you (num SG|PL); enclitic forms with \"enclitic\": true",
    "closed:demonstrative_so": "that (one), the (MOD with head, or as a pronoun: he/she/it)",
    "closed:anaphoric_i": "he/she/it, the one just mentioned (anaphoric h₁éy, h₁íh₂, h₁íd; pronoun or MOD)",
    "closed:deictic_ki": "this (here), near the speaker (ḱós; MOD with head, or as a pronoun: this one)",
    "closed:deictic_eno": "that (yonder), far from the speaker (h₁énos; MOD with head, or as a pronoun)",
    "closed:relative_yo": "who/which (relative)",
    "closed:interrogative_kwo": "who? which? (m/f/n by head)",
    "closed:interrogative_kwi": "who? what? (kʷís, kʷíd)",
    "closed:indefinite_kwi": "anyone, anything; with neg 'no one, nothing' (enclitic kʷis, kʷid)",
    "closed:interrogative_adv/why": "why? (kʷíd; ADV, fronted)",
    "closed:interrogative_adv/when": "when? (kʷóm; ADV, fronted)",
    "closed:interrogative_adv/where": "where? (kúdʰe; ADV, fronted)",
    "closed:interrogative_adv/how": "how? (kʷíh₁; ADV, fronted)",
    "closed:interrogative_adv/how_many": "how many? (kʷóti; MOD with a head, which takes the plural, or ADV; fronted)",
    "closed:correlative_adv/so_many": "so many (tóti; MOD with a head, plural, or ADV; answers 'how many?')",
    "closed:correlative_adv/as_many": "as many (as) (h₁yóti; MOD with a head, plural, or ADV; relative of tóti)",
    "closed:deictic_adv/here": "here (h₁idʰé; ADV, not fronted; 'there' is the adverb h₂én)",
    "compound": ("compound adjective (bahuvrihi) 'having (a) F S' or noun (determinative): {\"lex_id\": \"compound\", "
                 "\"compound\": {\"first\": F, \"second\": S, \"type\": \"bahuvrihi\"|\"determinative\"}}; F = "
                 "closed:prefix/h1su 'good', closed:prefix/dus 'bad', closed:prefix/n 'un-, -less', closed:prefix/sm "
                 "'one, same', closed:numerals/2|3|4, or a thematic/u-stem adjective or a noun; S = a noun with "
                 "compound_second: true (h1su + ḱléwos = h₁suḱléwēs 'of good fame')"),
}


def _compound_second(lex_id: str, lx) -> bool:
    try:
        resolve_compound({"first": "closed:prefix/dus", "second": lex_id, "type": "bahuvrihi"}, lx)
        return True
    except CompoundError:
        return False


def slice_adverbs(lx, attested, n: int = 40) -> list[dict]:
    """The slice's adverbs and adpositions (role ADV): the n best attested, leaving out a word a closed adverb id
    already offers (kúdʰe, kʷíh₁, kʷóti, tóti: closed:interrogative_adv/…, so one word has one id)."""
    from pie.realize import _closed_form, closed_adverb_ids
    closed_forms = {_closed_form(lx, c, "ADV", None) for c in closed_adverb_ids(lx)}
    advs = sorted((i for i, e in lx.entries.items() if e.get("pos") in ADVERB_POS and e["meaning"]
                   and i not in lx.blocked and not e["form"].startswith("-") and e["form"] not in closed_forms),
                  key=lambda i: -attested(i))[:n]
    return [{"lex_id": i, "form": lx.entries[i]["form"], "gloss": lx.meaning(i)[0][:60]} for i in advs]


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


# a keyword also matches these gloss words. Wiktionary glosses some concepts under another English word, so
# 'cow' missed gʷṓws, glossed 'cattle', and the t029 herding slice's theme core lost its main animal (t029 review)
KEYWORD_SYNONYMS = {
    "cow": ["cattle", "ox", "bull"], "cattle": ["cow", "ox", "bull"], "ox": ["bull", "cattle"], "bull": ["ox"],
    "sheep": ["ewe", "ram", "lamb"], "ewe": ["sheep"], "ram": ["sheep"], "pig": ["swine", "piglet", "boar"],
    "swine": ["pig"], "horse": ["mare", "stallion", "steed"], "mare": ["horse"], "dog": ["hound"],
    "hound": ["dog"], "man": ["husband", "hero"], "woman": ["wife"], "wife": ["woman"], "house": ["home", "dwelling"],
    "home": ["house"], "road": ["path", "way"], "path": ["road", "way"], "fire": ["flame"], "sky": ["heaven"],
    "god": ["deity"], "king": ["ruler", "lord"], "child": ["son", "daughter"], "hungry": ["hunger"],
    "hunger": ["hungry"], "thirst": ["thirsty"], "thirsty": ["thirst"],
}


def keyword_hit(lx: Lexicon, lex_id: str, words) -> bool:
    """A keyword, or one of its KEYWORD_SYNONYMS, is a whole word of one of the lexeme's glosses (every sense, not
    only the first three that the slice shows)."""
    want = {w.lower() for w in words} | {x for w in words for x in KEYWORD_SYNONYMS.get(w.lower(), [])}
    senses = list(lx.entries[lex_id].get("meaning") or []) or [lx.meaning(lex_id)[0] or ""]
    g = " " + re.sub(r"[^a-z]+", " ", " ; ".join(senses).lower()) + " "
    return any(f" {w} " in g for w in want)


def planner_accent_ok(lx: Lexicon, lex_id: str) -> bool:
    """Keep P10, but let a resolved primary paradigm supply a missing headword accent.

    Absence from the unresolved manifest alone is not positive accent evidence.
    Inspect primary cells only; alternatives may include rejected source specs.
    """
    try:
        if has_accent(parse(lx.entries[lex_id]["form"].strip("-"))):
            return True
        if lx.accent_status(lex_id) == "unresolved":
            return False
        exceptions = accent_manifest()["exception_cells"]
        accented = False
        for gender in (["m", "f", "n"] if lx.specs[lex_id]["family"] == "adj" else [None]):
            cells = lx.cells(lex_id, gender)
            if not cells:
                return False
            for cell, forms in cells.items():
                if not forms:
                    return False
                count = sum(s.acc for s in parse(forms[0]))
                if count == 1:
                    accented = True
                elif count != 0 or (lex_id, gender, cell, forms[0]) not in exceptions:
                    return False
        return accented
    except ValueError:
        return False


def attested_in(lx: Lexicon, i: str) -> int:
    """Daughter languages with a reflex (of the lexeme, or else its root): prefer well-attested words."""
    e = lx.entries[i]
    n = len(e.get("reflexes", {}))
    return n or len(lx.entries.get(e.get("root_id") or "", {}).get("reflexes", {}))


def slice_item(lx: Lexicon, i: str) -> dict:
    """A lexeme as planners see it, in a slice or from scripts/lexq.py: form, gloss (the valency gloss where one
    misleads), family, gender, features, attestation and every flag."""
    e, r = lx.entries[i], lx.specs[i]
    gl, src = lx.meaning(i)
    item = {"lex_id": i, "form": e["form"], "gloss": (VALENCY.get(i, {}).get("gloss") or gl)[:90],
            "family": r["family"]}
    if i in VALENCY:
        item["valency"] = VALENCY[i]["valency"]
    if src == "derived":
        item["gloss_approximate"] = True   # root meaning + suffix function, not a dictionary gloss
    elif src == "reflex-confirmed":
        item["gloss_source"] = src         # the daughters' agreed gloss (pie.glosses.confirm): reviewed apart
    if lx.coined(i):
        item["coined"] = lx.coined(i)      # a project reconstruction (PLAN.md): Tier 3/3b only, flagged
    if r["family"] == "noun":
        item["gender"] = lx.gender(i)
        if _compound_second(i, lx) and lx.coined(i) != "neologism":   # no compound on a coinage
            item["compound_second"] = True     # s-stem neuter or thematic: a bahuvrihi second member
    item["attested_in"] = attested_in(lx, i)
    if r["family"] == "verb":
        feats = verb_features(lx.cells(i))
        if e["form"].endswith(("tor", "toy")):     # deponent: middle only
            feats = [f for f in feats if f.endswith("MID")]
            item["deponent"] = True
        item["features"] = feats
    return item


def offered(lx: Lexicon, derived: bool = False) -> list[str]:
    """The ids a slice may offer (the pool): usable spec, not blocklisted, accent (P10), not an eval-holdout root,
    not NIL-held, and a dictionary gloss, or with derived=True an approximate derived gloss on a transparent suffix
    or on a word attested in two branches."""
    def derived_ok(i):
        suffix = lx.derived[i].split("[", 1)[-1].split(":", 1)[0].strip()
        return suffix in TRANSPARENT_SUFFIXES or len(branches(lx.entries[i].get("reflexes", {}))) >= 2

    # gates (tier3-b001/b002 reviews): an accented headword or resolved primary paradigm (P10), and a derived gloss
    # only for a transparent suffix or a word attested in two branches (R1)
    # NIL after the re-review (docs/audits/nil-merge-rereview.md): NIL glosses on existing words are
    # admitted except NIL_GLOSS_HELD; of the new NIL lexemes only the NIL_ADMIT subset judged ok.
    # Lexemes flagged nil-single-branch / nil-uncertain / nil-notation always stay out (P9).
    def nil_held(i):
        e = lx.entries[i]
        if any(u.startswith("nil-") for u in e.get("uncertain", [])):
            return True
        if e.get("source") == "nil":
            return i not in NIL_ADMIT
        return e.get("meaning_source") == "nil" and i in NIL_GLOSS_HELD

    # root families the export holds out for the cognate/inflection benchmark are never offered to
    # planners, so they stay unseen in training sentences (pie.export.eval_root)
    from pie.export import eval_root
    return [i for i, r in lx.specs.items() if r.get("usable") and i not in lx.blocked and planner_accent_ok(lx, i) and
            not eval_root(lx.entries[i].get("root_id")) and
            not nil_held(i) and
            (lx.entries[i]["meaning"] or (derived and i in lx.derived and derived_ok(i)))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--size", type=int, default=220)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--derived", action="store_true", help="include lexemes with approximate derived glosses")
    ap.add_argument("--core", nargs="*", default=[],
                    help="up to 8 theme-core lexeme ids, capped at 15 uses per batch instead of 6")
    ap.add_argument("--tier3b", action="store_true",
                    help="Tier 3b slice: also offer every neologism (data/lexicon/neologisms.jsonl), flagged coined")
    args = ap.parse_args()
    lx = Lexicon.load()
    if args.tier3b:      # a new Lexicon with the neologisms; the default one never has them (pie/neologism.py)
        from pie.neologism import with_neologisms
        lx = with_neologisms(lx)
    rng = random.Random(args.seed)
    ap_derived = args.derived

    pool = offered(lx, ap_derived)

    def attested(i):
        return attested_in(lx, i)

    def hits(i, words):
        return keyword_hit(lx, i, words)

    # keyword hits: dictionary-glossed first, then well attested; a derived-gloss
    # lexeme only if its (root, family) isn't represented yet (a root's many
    # derived presents would otherwise flood the slice)
    hits_all = sorted((i for i in pool if hits(i, args.keywords)),
                      key=lambda i: (lx.meaning(i)[1] not in TRUSTED_GLOSS, -attested(i)))
    chosen, seen_rf = [], set()
    for i in hits_all:
        rf = (lx.entries[i].get("root_id"), lx.specs[i]["family"])
        if lx.meaning(i)[1] == "derived" and rf in seen_rf:
            continue
        seen_rf.add(rf)
        chosen.append(i)
    chosen = chosen[: args.size]
    # a tree-path derivative is left out when a dictionary word of the same root and gloss is in
    # the slice (mr̥tós beside the word; b003 review): planners otherwise split one concept in two
    words_rg = {(lx.entries[i].get("root_id"), lx.meaning(i)[0]) for i in chosen if lx.entries[i]["kind"] == "word"}
    chosen = [i for i in chosen if not (lx.entries[i]["kind"] == "derivative" and
                                        (lx.entries[i].get("root_id"), lx.meaning(i)[0]) in words_rg)]
    chosen += [i for i in pool if lx.specs[i]["family"] == "verb" and hits(i, CORE_VERBS) and i not in chosen
               and lx.meaning(i)[1] in TRUSTED_GLOSS]
    chosen += [i for i in CORE_NOUNS + CONVERSATION if i in pool and i not in chosen]
    chosen += [i for i in pool if args.tier3b and lx.coined(i) == "neologism" and i not in chosen
               and i not in lx.blocked]
    # the inherited everyday words (named for Tier 3b, where they replaced coinages; since 2026-10-30 offered to every
    # slice, as the in-world Tier 3 dialogues need them most): usable, unblocked and accented; P9's NIL hold waived
    from pie.export import eval_root
    chosen += [i for i in EVERYDAY if i not in chosen and lx.specs.get(i, {}).get("usable") and i not in lx.blocked
               and planner_accent_ok(lx, i)]
    chosen += [i for i in TIER3B_INHERITED if i not in chosen and lx.specs.get(i, {}).get("usable")
               and i not in lx.blocked and planner_accent_ok(lx, i)
               and not eval_root(lx.entries[i].get("root_id"))]
    # the formula menu's words, so planners can use the inherited phrases
    menu_path = ROOT / "data" / "generation" / "formula_menu.json"
    menu = json.loads(menu_path.read_text("utf-8")) if menu_path.exists() else []
    chosen += [x["lex_id"] for m in menu for x in m["lexemes"] if x["lex_id"] in pool and x["lex_id"] not in chosen]
    # random fill: dictionary-glossed or well-attested words only (b002 review R3)
    rest = [i for i in pool if i not in chosen and (lx.meaning(i)[1] in TRUSTED_GLOSS or attested(i) >= 3)]
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
        item = slice_item(lx, i)
        items.append(item)
    out = ROOT / "data" / "generation" / "slices" / f"{args.name}.json"
    # theme core: given with --core, else the 8 best keyword hits that are nouns (the thing or god the
    # batch is about), so its cap is 15 instead of 6 (b004 review)
    auto = [i for i in hits_all if lx.specs[i]["family"] == "noun" and lx.meaning(i)[1] != "derived"]
    core = [i for i in (args.core or auto) if i in {it["lex_id"] for it in items}][:8]
    ids = {it["lex_id"] for it in items}
    formulas = [m for m in menu if all(x["lex_id"] in ids for x in m["lexemes"])]
    # adverbs and adpositions (role ADV): indeclinables have no paradigm spec, so the pool never has them
    adverbs = slice_adverbs(lx, attested)
    out.write_text(json.dumps({"name": args.name, "keywords": args.keywords,
                               "closed": {**CLOSED, **CLOSED_NUMERALS}, "adverbs": adverbs, "theme_core": core,
                               "formulas": formulas, "lexemes": items},
                              ensure_ascii=False, indent=1) + "\n", "utf-8")
    fam = {}
    for it in items:
        fam[it["family"]] = fam.get(it["family"], 0) + 1
    print(f"{out}: {len(items)} lexemes {fam}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
