#!/usr/bin/env python3
"""Select the benchmark hold-out: write data/export/protected_roots.json and data/export/held_roots.json
(read by pie.holdout; pie.export.eval_root is the one predicate make_slice, export and the tests use).

  uv run python -I scripts/build_holdout.py            # write both files and print the comparison
  uv run python -I scripts/build_holdout.py --dry-run  # print only

Protected set (never held out), derived from the data; each family keeps its reasons:
  formula-menu     the lexemes of data/generation/formula_menu.json
  formula          the words of data/formulas/formulas.jsonl, mapped to lexemes as
                   scripts/build_formula_menu.py maps them (validator index, found words, no near-misses, the initial
                   laryngeal the books omit), and the verified tokens of corpus/tier1/formulas.jsonl
  tier2-secure     Tier 2 tokens with secure_level exact or root (corpus/tier2)
  core-noun, core-verb, conversation
                   make_slice's CORE_NOUNS and CONVERSATION ids, and its CORE_VERBS keywords resolved
                   as make_slice resolves them (usable verb, whole-word gloss hit, trusted gloss)
  numeral          every lexicon entry with pos "num"
  swadesh:kin|body|nature
                   usable nouns with a trusted gloss one of whose sense segments is a Swadesh-type
                   concept word (SWADESH below; the lexemes are found from the glosses)
  swadesh-207, leipzig-jakarta, conversation-core
                   every lexicon entry (lexeme or root, any part of speech) with a trusted gloss one of
                   whose sense segments is a concept word of CONCEPTS below: the full Swadesh-207 list,
                   the Leipzig-Jakarta 100-item list (Tadmor et al. 2010) and a conversational core (help,
                   ask, thank, teach, want, morning, …, plus the everyday families the owner named on
                   2026-10-29). A concept is "word/variant/…"; "to" and articles are stripped from the gloss
                   segments, so "to become afraid" matches "fear/be afraid/become afraid/be terrified"; a list noun that
                   is also an English verb (NOUN_ONLY: wind, stick, bark, …) matches only a noun sense
                   (not "to wind, turn"); a phrasal verb gloss also matches its verb ("to swell up": swell).
                   The hand-written part is only the concept words; the families are
                   found from the glosses.
A lexeme without a root_id belongs to no family and cannot be held out; it is counted, not listed.

Hold-out (selection, deterministic):
  universe  every root family of the lexicon (Lexicon.load(): the root_ids of its entries)
  pool      universe − protected − families used anywhere in Tier 1 records (eval, excluded anyway),
            Tier 3/3b records (admitted or not), Tier 3b coinages (data/lexicon/neologisms.jsonl),
            non-eval Tier 2 records, Tier 2 and Tier 3 plans, and planner slices, so no record
            already trained (or planned under the old hold-out) touches a held family
  strata    (task-bearing: the family has an inflection or cognate task) × (branches with an
            inherited reflex: 0, 1-2, 3-4, 5+) × (root_type verbal / nominal), so the new set matches
            the old one's difficulty mix
  quota     N = round(SHARE × |universe|), split over the strata in the proportions of the old
            hash draw (sha256(root_id) < SHARE over the universe), largest remainder
  ranking   inside each stratum, ascending sha256(root_id)[:8] (pie.holdout.hash_rank)
  shortfall a stratum whose pool is smaller than its quota is taken whole and the rest is filled from the
            same task-bearing × root_type strata with fewer branches, nearest first (recorded in
            held_roots.json "shortfall"). Since the 2026-10-29 protection only (tasks, 5+ branches,
            verbal) falls short: its well-attested verbs are nearly all everyday words.
Re-running after the corpus grows selects a different set; the files are frozen on purpose. Do
not re-run to "refresh" them: benchmark scores across hold-outs are not comparable. (Redrawn
2026-10-29 with the Swadesh-207 / Leipzig-Jakarta / conversational-core protection, before any
model was trained, so no score was lost; the strata quota still comes from the original hash draw.)
"""

import argparse
import collections
import datetime
import importlib.util
import json
import random
import re
import statistics
import sys
from pathlib import Path

from pie.export import cognate_tasks, inflection_tasks, train_root_ids, _load
from pie.holdout import HELD_PATH, PROTECTED_PATH, hash_rank
from pie.realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent
SHARE = 0.10
SWADESH = {
    "kin": ["father", "mother", "daughter", "son", "brother", "sister", "husband", "wife", "widow",
            "grandfather", "grandmother", "grandson", "granddaughter", "nephew", "niece", "uncle", "aunt",
            "father-in-law", "mother-in-law", "son-in-law", "daughter-in-law", "brother-in-law",
            "sister-in-law", "husband's brother", "husband's sister", "child", "orphan"],
    "body": ["head", "eye", "ear", "nose", "mouth", "tooth", "tongue", "lip", "hair", "hand", "foot", "leg",
             "knee", "arm", "elbow", "shoulder", "finger", "nail", "fingernail", "neck", "back", "breast",
             "heart", "liver", "kidney", "belly", "navel", "guts", "bowels", "blood", "bone", "marrow", "skin",
             "flesh", "meat", "fat", "horn", "tail", "feather", "wing", "eyebrow", "brow", "jaw", "chin",
             "cheek", "thigh", "heel", "lung", "bile", "milk", "egg"],
    "nature": ["sun", "moon", "star", "sky", "cloud", "fog", "rain", "snow", "ice", "wind", "thunder",
               "lightning", "water", "river", "lake", "sea", "salt", "stone", "rock", "sand", "dust", "earth",
               "ground", "mountain", "fire", "smoke", "ash", "ashes", "night", "day", "dawn", "year", "winter",
               "summer", "spring", "tree", "wood", "forest", "leaf", "root", "bark", "seed", "grass", "fruit",
               "flower", "animal", "fish", "bird", "dog", "louse", "snake", "worm", "wolf", "bear"],
}
# Concept lists matched against every trusted gloss (any part of speech). "a/b/c": gloss variants of one concept.
CONCEPTS = {
    # Swadesh 207 (the Wiktionary appendix order); pronouns and function words are usually rootless (counted only)
    "swadesh-207": [
        "I", "you", "he/she/it", "we", "they", "this", "that", "here", "there", "who", "what", "where", "when",
        "how", "not", "all", "many", "some", "few", "other", "one", "two", "three", "four", "five",
        "big/great/large", "long", "wide/broad", "thick", "heavy", "small/little/become small", "short", "narrow", "thin",
        "woman", "man", "human being/person", "child", "wife", "husband", "mother", "father", "animal", "fish",
        "bird", "dog", "louse", "snake/serpent", "worm", "tree", "forest", "stick", "fruit", "seed", "leaf",
        "root", "bark", "flower", "grass", "rope", "skin", "meat/flesh", "blood", "bone", "fat/grease", "egg",
        "horn", "tail", "feather", "hair", "head", "ear", "eye", "nose", "mouth", "tooth", "tongue",
        "fingernail/nail", "foot", "leg", "knee", "hand", "wing", "belly", "guts/bowels/entrails", "neck",
        "back", "breast", "heart", "liver", "drink", "eat", "bite", "suck", "spit", "vomit", "blow",
        "breathe/breath", "laugh", "see", "hear", "know", "think", "smell", "fear/be afraid/become afraid/be terrified",
        "sleep", "live", "die", "kill", "fight", "hunt", "hit/strike/beat", "cut", "split", "stab/pierce",
        "scratch", "dig", "swim", "fly", "walk", "come", "lie/lie down", "sit/sit down", "stand", "turn",
        "fall", "give", "hold", "squeeze/press", "rub", "wash", "wipe", "pull/draw", "push", "throw", "tie/bind",
        "sew", "count", "say", "sing", "play", "float", "flow", "freeze/be cold", "swell", "sun", "moon",
        "star", "water", "rain", "river", "lake", "sea", "salt", "stone", "sand", "dust", "earth", "cloud",
        "fog/mist", "sky", "wind", "snow", "ice", "smoke", "fire", "ash/ashes", "burn", "road/path/way",
        "mountain", "red", "green", "yellow", "white", "black", "night", "day", "year", "warm/be warm/hot",
        "cold", "full", "new", "old", "good", "bad/evil", "rotten/rot", "dirty", "straight", "round", "sharp",
        "dull/blunt", "smooth", "wet", "dry", "correct/right", "near", "far", "right", "left", "at", "in",
        "with", "and", "if", "because", "name"],
    # Leipzig-Jakarta 100 (Tadmor, Haspelmath & Taylor 2010)
    "leipzig-jakarta": [
        "fire", "nose", "go", "water", "mouth", "tongue", "blood", "bone", "you", "root", "come", "breast",
        "rain", "I", "name", "louse", "wing", "flesh/meat", "arm/hand", "fly", "night", "ear", "neck", "far",
        "do/make", "house", "stone/rock", "bitter", "say", "tooth", "hair", "big/great/large", "one", "who",
        "he/she/it", "hit/beat/strike", "leg/foot", "horn", "this", "fish", "yesterday", "drink", "black",
        "navel", "stand", "bite", "back", "wind", "smoke", "what", "child", "egg", "give", "new", "burn",
        "not", "good", "know", "knee", "sand", "laugh", "hear", "soil", "leaf", "red", "liver", "hide",
        "skin", "suck", "carry", "ant", "heavy", "take", "old", "eat", "thigh", "thick", "long", "blow",
        "wood", "run", "fall", "eye", "ash/ashes", "tail", "dog", "cry/weep", "tie/bind", "see", "sweet",
        "rope", "shade/shadow", "bird", "salt", "small/little", "wide/broad", "star", "in", "hard",
        "crush/grind"],
    # what a conversational model needs beyond the lists (owner 2026-10-29: "help is a major critical word and
    # should not be held out"); the last row: the everyday families of the 2026-10-28 hold-out the owner named
    "conversation-core": [
        "help/assist", "ask/request", "answer", "thank", "teach", "learn", "want/wish/desire", "love",
        "like", "call", "name", "know/recognize", "remember", "forget", "wait", "stay/remain", "leave",
        "return/come back/return home", "open", "close/shut", "buy", "sell/be for sale", "work", "play", "laugh", "weep/cry",
        "dream", "morning", "evening", "today", "tomorrow",
        "take/fetch", "summer", "goat", "swear", "measure", "hate", "cover", "bury", "beard", "rejoice",
        "be ashamed", "lack", "be tired",
        # everyday words left in the hold-out by the lists above (review of the redraw, 2026-10-29)
        "lose", "show", "grow", "put/place/lay", "steal", "trust", "touch", "clean", "lick", "chew", "cough",
        "sick/ill/be ill/be sick/become sick", "silent/be silent", "soft", "pretty/beautiful", "tall/high",
        "share/divide", "exchange/trade", "take care of/care for", "happy/glad/be glad/joyful", "lift/raise/pick up",
        "lip", "understand", "wake/wake up/awaken",
        # the vocabulary push's requested everyday words (docs/audits/vocab-push.md), kept trainable
        "roof", "bed", "beech", "owe", "suckle", "sweat", "wash", "wipe", "hornet", "fortress/stronghold",
        "womb", "elk", "grief/hatred/care"],
    # the 2026-10-29 review pass is closed: adding concepts later changes the held set (a redraw, see the docstring)
}
# concept words that are nouns on the lists but also English verbs: matched only where the gloss gives them as nouns
# (not "to wind, turn", "to stick, adhere")
NOUN_ONLY = {"wind", "stick", "skin", "bark", "rock", "stone", "smoke", "dust", "salt", "fish", "right", "left",
             "back", "root", "sand", "soil", "house", "shade", "shadow", "ash", "ashes", "wood", "flesh", "rope", "leaf",
             "seed", "flower"}
SECURE_LEVELS = ("exact", "root")


def _make_slice():
    spec = importlib.util.spec_from_file_location("make_slice", ROOT / "scripts" / "make_slice.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _segments(gloss: str) -> set[str]:
    out = set()
    for s in re.split(r"[;,()]", (gloss or "").lower()):
        s = re.sub(r"^\s*(a|an|the|one's|to)\s+", "", s.strip()).strip(" .")
        if s:
            out.add(s)
    return out


def protected(lx, ms) -> tuple[dict[str, list[str]], dict]:
    """root_id → sorted reasons; and the lexemes behind each reason (for the file)."""
    reasons: dict[str, set[str]] = collections.defaultdict(set)
    rootless = collections.Counter()
    lexemes: dict[str, set[str]] = collections.defaultdict(set)

    def add(lid, why):
        e = lx.entries.get(lid)
        if e is None:
            return
        lexemes[why].add(lid)
        rid = e.get("root_id")
        if rid:
            reasons[rid].add(why)
        else:
            rootless[why] += 1

    menu = json.loads((ROOT / "data/generation/formula_menu.json").read_text("utf-8"))
    for m in menu:
        for x in m["lexemes"]:
            add(x["lex_id"], "formula-menu")
    from pie.formulas import load as load_formulas
    from pie.validate import load_index, validate_text
    ix = load_index()               # most of this script's run time (about a minute)
    formula_words = [w for f in load_formulas() if f.get("pie")
                     for w in re.split(r"[\s,]+|…|\.\.\.", f["pie"]) if w.strip("-") and not w.endswith("-")]
    for w in dict.fromkeys(formula_words):
        # as build_formula_menu maps them: a found word (no near-misses), retrying the initial laryngeal the books omit
        tries = [w] + ([lar + w for lar in ("h₁", "h₂", "h₃")] if re.match("[aeiouáéíóúāēīōū]", w) else [])
        for cand in tries:
            t = validate_text(cand.replace("-", ""), ix)["tokens"]
            if t and t[0].found and t[0].analyses and (t[0].analyses[0].lex_id or "").startswith("pie-"):
                add(t[0].analyses[0].lex_id, "formula")
                break
    for r in _load("corpus/tier1/formulas.jsonl", ROOT):
        for t in r.get("tokens") or []:
            if t.get("verified") and t.get("lex_id"):
                add(t["lex_id"], "formula")
    for r in _load("corpus/tier2/*.jsonl", ROOT):
        for t in r.get("tokens") or []:
            if t.get("secure_level") in SECURE_LEVELS and t.get("lex_id"):
                add(t["lex_id"], "tier2-secure")
    for lid in ms.CORE_NOUNS:
        add(lid, "core-noun")
    for lid in ms.CONVERSATION:
        add(lid, "conversation")

    def hits(i, words):
        g = " " + re.sub(r"[^a-z]+", " ", (lx.meaning(i)[0] or "").lower()) + " "
        return any(f" {w} " in g for w in words)

    usable = [i for i, r in lx.specs.items() if r.get("usable") and i not in lx.blocked and lx.entries[i]["meaning"]]
    for i in usable:
        if lx.specs[i]["family"] == "verb" and hits(i, ms.CORE_VERBS) and lx.meaning(i)[1] in ms.TRUSTED_GLOSS:
            add(i, "core-verb")
    for i, e in lx.entries.items():
        if e.get("pos") == "num":
            add(i, "numeral")
    for i in usable:
        if lx.specs[i]["family"] != "noun" or lx.meaning(i)[1] not in ms.TRUSTED_GLOSS:
            continue
        segs = _segments(lx.meaning(i)[0])
        for kind, words in SWADESH.items():
            if segs & set(words):
                add(i, f"swadesh:{kind}")
    matched = concept_matches(lx, ms)
    for name, by_concept in matched.items():
        for ids in by_concept.values():
            for i in ids:
                add(i, name)
    families = {name: {c: sorted({lx.entries[i].get("root_id") for i in ids if lx.entries[i].get("root_id")})
                       for c, ids in sorted(by_concept.items())} for name, by_concept in matched.items()}
    return ({rid: sorted(w) for rid, w in sorted(reasons.items())},
            {"rootless_lexemes_by_reason": dict(sorted(rootless.items())),
             "lexemes_by_reason": {k: len(v) for k, v in sorted(lexemes.items())},
             "concept_families": families})


def concept_matches(lx, ms) -> dict[str, dict[str, list[str]]]:
    """CONCEPTS list → concept → the lexicon entries (lexemes and roots, any part of speech) with a trusted gloss
    one of whose sense segments is one of the concept's variants."""
    segs, nominal = {}, {}
    for i, e in lx.entries.items():
        if i in lx.blocked and not i.startswith("pie-root-"):
            continue
        gloss, src = lx.meaning(i)
        if gloss and src in ms.TRUSTED_GLOSS:
            segs[i] = _segments(gloss)
            nominal[i] = segs[i] - _verbal_segments(gloss)
    out = {}
    for name, concepts in CONCEPTS.items():
        out[name] = {}
        for c in concepts:
            variants = {v.strip().lower() for v in c.split("/")}
            noun_only = variants & NOUN_ONLY
            out[name][c] = sorted(i for i, ss in segs.items()
                                  if (_bare(ss) & (variants - noun_only)) or (nominal[i] & noun_only))
    return out


def _bare(segs: set[str]) -> set[str]:
    """The segments and, for a phrasal verb gloss, its verb ("swell up", "wipe off", "close something" → swell, …)."""
    return segs | {re.sub(r"(\s+(up|down|off|out|away|something|oneself))+$", "", s) for s in segs}


def _verbal_segments(gloss: str) -> set[str]:
    """The sense segments (as _segments spells them) of the ';'-parts of a gloss that are verbs ("to wind, turn")."""
    return set().union(*(_segments(part) for part in (gloss or "").lower().split(";")
                         if re.match(r"\s*to\s", part)))


def excluded(lx) -> dict[str, set[str]]:
    """Families already used (or planned) for training, by source."""
    out = {}
    tier2 = _load("corpus/tier2/*.jsonl", ROOT)
    out["tier1"] = train_root_ids(_load("corpus/tier1/*.jsonl", ROOT), lx)   # eval, but no held family there either
    out["tier2-train"] = train_root_ids([r for r in tier2 if not r.get("eval_grade")], lx)
    out["tier3"] = train_root_ids(_load("corpus/tier3/*.jsonl", ROOT) + _load("corpus/tier3b/*.jsonl", ROOT), lx)
    lid_re = re.compile(r'"lex_id": *"(pie-[^"]+)"')
    for name, pats in (("plans", ["data/generation/plans/*.jsonl", "data/tier2/plans/*.jsonl"]),
                       ("slices", ["data/generation/slices/*.json"])):
        s = set()
        for pat in pats:
            for f in ROOT.glob(pat):
                for lid in lid_re.findall(f.read_text("utf-8")):
                    e = lx.entries.get(lid)
                    if e and e.get("root_id"):
                        s.add(e["root_id"])
                    elif lid.startswith("pie-root-"):
                        s.add(lid)
        out[name] = s
    # Tier 3b coinages (data/lexicon/neologisms.jsonl): pie.neologism refuses a held root in a derivation
    s = set()
    for lid in re.findall(r'"(pie-(?:root|lex)-[^"]+)"', (ROOT / "data/lexicon/neologisms.jsonl").read_text("utf-8")):
        e = lx.entries.get(lid)
        if e and e.get("root_id"):
            s.add(e["root_id"])
        elif lid.startswith("pie-root-"):
            s.add(lid)
    out["neologisms"] = s
    return out


def family_stats(lx, ms) -> dict[str, dict]:
    members = collections.defaultdict(list)
    for i, e in lx.entries.items():
        if e.get("root_id"):
            members[e["root_id"]].append(i)
    tasks = collections.Counter()
    noun_verb = collections.defaultdict(collections.Counter)
    for t in inflection_tasks(lx, random.Random(0)) + cognate_tasks(lx):
        if t.get("coined") or not t.get("root_id"):
            continue
        tasks[t["root_id"]] += 1
        fam = (lx.specs.get(t["source_id"]) or {}).get("family") or lx.entries[t["source_id"]].get("pos") or "other"
        noun_verb[t["root_id"]][fam] += 1
    out = {}
    for rid, ids in members.items():
        refl = collections.defaultdict(list)
        for i in ids:
            for lang, xs in (lx.entries[i].get("reflexes") or {}).items():
                refl[lang] += xs
        good = {lang for lang, xs in refl.items() if any(not (x.get("borrowed") or x.get("analogical")) for x in xs)}
        root_e = lx.entries.get(rid) or {}
        out[rid] = {"reflex_langs": len(good), "branches": len(ms.branches(refl)),
                    "root_type": root_e.get("root_type") or "none", "tasks": tasks[rid],
                    "task_families": dict(noun_verb[rid])}
    return out


def branch_bin(n: int) -> str:
    return "0" if n == 0 else "1-2" if n <= 2 else "3-4" if n <= 4 else "5+"


BRANCH_BINS = ["branches:0", "branches:1-2", "branches:3-4", "branches:5+"]


def stratum(s: dict) -> tuple[str, str, str]:
    return ("tasks" if s["tasks"] else "no-tasks", "branches:" + branch_bin(s["branches"]), s["root_type"])


def select(universe, pool, stats) -> tuple[list[str], dict]:
    old = [r for r in universe if hash_rank(r) < SHARE]
    n = round(SHARE * len(universe))
    by = collections.Counter(stratum(stats[r]) for r in old)
    raw = {k: n * v / len(old) for k, v in by.items()}
    quota = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - quota[k]), str(k)))[: n - sum(quota.values())]:
        quota[k] += 1
    def ranked(k):
        return sorted((r for r in pool if stratum(stats[r]) == k and r not in held), key=lambda r: (hash_rank(r), r))
    held, shortfall, filled = [], {}, collections.Counter()
    for k in sorted(quota, key=str):
        held += ranked(k)[: quota[k]]
    for k in sorted(quota, key=str):
        got = sum(1 for r in held if stratum(stats[r]) == k)
        if got >= quota[k]:
            continue
        # the stratum is exhausted (its well-attested families are protected or used): fill the rest from the same
        # task-bearing × root_type strata with fewer branches, nearest first; never across tasks or verbal/nominal
        shortfall["/".join(k)] = quota[k] - got
        need = quota[k] - got
        lower = BRANCH_BINS[: BRANCH_BINS.index(k[1])][::-1]
        for b in lower:
            take = ranked((k[0], b, k[2]))[:need]
            held += take
            filled["/".join((k[0], b, k[2]))] += len(take)
            need -= len(take)
            if not need:
                break
        if need:
            raise SystemExit(f"stratum {k}: pool short by {need} even with the lower branch bins")
    return sorted(held), {"n": n, "quota": {"/".join(k): v for k, v in sorted(quota.items())},
                          "shortfall": shortfall, "shortfall_filled_from": dict(sorted(filled.items()))}


def describe(name, fams, stats) -> dict:
    xs = [stats[r] for r in fams]

    def dist(key, bins):
        c = collections.Counter()
        for x in xs:
            v = x[key]
            c[next(lab for lab, lo, hi in bins if lo <= v <= hi)] += 1
        return {lab: c[lab] for lab, _, _ in bins}
    tf = collections.Counter()
    for x in xs:
        tf.update(x["task_families"])
    return {"set": name, "families": len(xs),
            "reflex_langs": {"median": statistics.median(x["reflex_langs"] for x in xs) if xs else 0,
                             "mean": round(statistics.mean(x["reflex_langs"] for x in xs), 2) if xs else 0,
                             "bins": dist("reflex_langs", [("0", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5),
                                                           ("6-10", 6, 10), ("11+", 11, 10 ** 6)])},
            "branches": {"mean": round(statistics.mean(x["branches"] for x in xs), 2) if xs else 0,
                         "bins": dist("branches", [("0", 0, 0), ("1", 1, 1), ("2", 2, 2), ("3-4", 3, 4),
                                                   ("5+", 5, 99)])},
            "root_type": dict(collections.Counter(x["root_type"] for x in xs)),
            "task_bearing": sum(1 for x in xs if x["tasks"]),
            "tasks": sum(x["tasks"] for x in xs),
            "tasks_by_lexeme_family": dict(tf.most_common())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ms, lx = _make_slice(), Lexicon.load()
    prot, prot_meta = protected(lx, ms)
    exc = excluded(lx)
    universe = sorted({e["root_id"] for e in lx.entries.values() if e.get("root_id")})
    stats = family_stats(lx, ms)
    used = set().union(*exc.values())
    pool = [r for r in universe if r not in prot and r not in used]
    held, sel = select(universe, pool, stats)
    old = [r for r in universe if hash_rank(r) < SHARE]
    seen_train = exc["tier2-train"] | exc["tier3"]
    report = {"old_hash": describe("old hash draw", old, stats),
              "old_effective": describe("old effective (hash, unseen in training)",
                                        [r for r in old if r not in seen_train], stats),
              "new": describe("new", held, stats),
              "old_protected": sorted(r for r in old if r in prot)}
    if HELD_PATH.exists():      # the frozen set this run replaces (for the before/after comparison)
        prev = json.loads(HELD_PATH.read_text("utf-8"))
        report["previous"] = describe(f"previous frozen set ({prev.get('generated')})",
                                      [r for r in prev["held"] if r in stats], stats)
        report["previous_now_protected"] = {r: prot[r] for r in prev["held"] if r in prot}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"universe {len(universe)}, protected {len(prot)}, used {len(used & set(universe))}, pool {len(pool)}, "
          f"held {len(held)}; old∩new {len(set(old) & set(held))}")
    if args.dry_run:
        return 0
    today = datetime.date.today().isoformat()
    PROTECTED_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROTECTED_PATH.write_text(json.dumps({
        "generated": today, "by": "scripts/build_holdout.py", "swadesh_concepts": SWADESH, "concepts": CONCEPTS,
        **prot_meta, "families": len(prot), "roots": prot}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    HELD_PATH.write_text(json.dumps({
        "generated": today, "by": "scripts/build_holdout.py", "share": SHARE, "universe": len(universe),
        "protected": len(prot), "excluded_used": {k: len(v & set(universe)) for k, v in exc.items()},
        "pool": len(pool), **sel, "ranking": "ascending int(sha256(root_id)[:8], 16) / 0xFFFFFFFF within stratum",
        "comparison": {k: v for k, v in report.items() if k not in ("old_protected", "previous_now_protected")},
        "previous_now_protected": sorted(report.get("previous_now_protected", {})),
        "old_protected_count": len(report["old_protected"]),
        "held": held}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"wrote {PROTECTED_PATH} and {HELD_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
