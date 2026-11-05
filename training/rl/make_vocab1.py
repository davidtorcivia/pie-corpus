"""Vocabulary pilot (2026-11-04): teach EN->PIE words the gap SFT left never right, by exposure in many sentences.

Gap SFT 1 showed one exposure per word at LR 1e-5 does not teach a rare word (154 of 206 never-right EN->PIE words
stayed never right on their own training prompt). Here each word gets about ten: sentences built as plans with the
word's lexeme pinned in a slot and realized by the engine (pie.realize; never Transfer, which may pick another lemma
for the sense), in several cases, numbers, tenses and persons, beside partner words the model knows, in both
directions; plus the bare vocabulary prompt. Held-out sentences (other frames) are never trained: they are the
validation set and the test.

Words: data/sft1-check (sft1's pass rates on the prompts it trained on, the training reward, 4 samples): EN->PIE
vocabulary prompts with mean 0, whose taught lemma (make_sft1.reference: the corpus's most used of the accepted
lemmas) is a noun, verb or adjective and builds enough sentences. A seeded CONTROL set of such words gets nothing,
to tell exposure from drift.

    uv run python -I training/rl/make_vocab1.py [--out /Users/david/AI/pie-runs/rl/data/vocab1] [--words 110]
Writes train.jsonl, valid.jsonl (held-out sentences, EN->PIE), test.jsonl (the same with lex_id), control.jsonl
and words.jsonl (bare prompts of the trained and control words, for passrate), manifest.json.
"""
import argparse
import collections
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CHECK = Path("/Users/david/AI/pie-runs/rl/data/sft1-check")
SEED = 20261105
REPLAY = 0.25
SYSTEM = ("You are a speaker of Proto-Indo-European. You think in it and answer in it. A teacher is testing how well "
          "you know your own language. Answer exactly, in the form asked. Write it in the project's handbook convention.")
EN_PIE = ["Translate this into Proto-Indo-European: {}", "Render this in reconstructed Proto-Indo-European: {}",
          "Put this into Proto-Indo-European, please.\n\n{}", "How do you say this in your language? {}"]
PIE_EN = ["Translate from PIE: \"{}\"", "What does this mean in English? {}", "Translate this into English: {}"]

MAN, WOMAN, HOUSE, HORSE, SHEEP = "pie-lex-wiHros", "pie-lex-gwexn", "pie-lex-doxm", "pie-lex-h1ekjwos", "pie-lex-h2owis"
FATHER, MOTHER, OLD, GREAT = "pie-lex-ph2texr", "pie-lex-meh2texr", "pie-lex-senos", "pie-lex-megjh2s"
SEE, CARRY, I_, WE = "pie-lex-spekjyeti", "pie-lex-bhereti", "closed:personal/1", "closed:personal/1"
IRREG_PAST = {"see": "saw", "carry": "carried"}


def V(lid, tense="PRS", mood="IND", person=None, num=None):
    v = {"tense": tense, "mood": mood, "voice": "ACT", "person": person}
    if num:
        v["num"] = num
    return {"lex_id": lid, "role": "V", "verb": v}


def N(lid, role, num="SG", **kw):
    return {"lex_id": lid, "role": role, "num": num, **kw}


def plural(n):
    w = n.split()
    last = w[-1]
    if last in ("man", "woman"):
        last = last[:-2] + "en"
    elif last.endswith(("s", "x", "z", "ch", "sh")):
        last += "es"
    elif last.endswith("y") and last[-2:-1] not in "aeiou":
        last = last[:-1] + "ies"
    else:
        last += "s"
    return " ".join(w[:-1] + [last])


def third(v):
    h, *t = v.split()
    if h.endswith(("s", "x", "z", "ch", "sh", "o")):
        h += "es"
    elif h.endswith("y") and h[-2:-1] not in "aeiou":
        h = h[:-1] + "ies"
    else:
        h += "s"
    return " ".join([h] + t)


def past(v):
    from pie.translator.transfer import IRREGULAR
    rev = {b: a for a, b in IRREGULAR.items()}
    h, *t = v.split()
    if h in rev:
        h = rev[h]
    elif h.endswith("e"):
        h += "d"
    elif h.endswith("y") and h[-2:-1] not in "aeiou":
        h = h[:-1] + "ied"
    else:
        h += "ed"
    return " ".join([h] + t)


def frames(fam, lid, sense):
    """(english, plan) candidates, train frames then test frames; plans that fail check_plan are dropped later."""
    out = {"train": [], "test": []}
    if fam == "noun":
        n = re.sub(r"^(a|an|the) ", "", sense)
        ns = plural(n)
        C = lambda e, slots, **kw: (e, {"english": e, "clauses": [{"slots": slots, **kw}]})
        out["train"] += [
            C(f"The {n} sees the sheep.", [N(lid, "SUBJ"), N(SHEEP, "OBJ"), V(SEE)]),
            C(f"The man sees the {n}.", [N(MAN, "SUBJ"), N(lid, "OBJ"), V(SEE)]),
            C(f"The woman carries the {ns}.", [N(WOMAN, "SUBJ"), N(lid, "OBJ", "PL"), V(CARRY)]),
            C(f"The father of the {n} sees the horse.", [N(FATHER, "SUBJ"), N(lid, "POSS", head=0), N(HORSE, "OBJ"), V(SEE)]),
            C(f"The man saw the horse in the {n}.", [N(MAN, "SUBJ"), N(HORSE, "OBJ"), N(lid, "LOC"), V(SEE, "AOR")]),
            C(f"The {ns} saw the man.", [N(lid, "SUBJ", "PL"), N(MAN, "OBJ"), V(SEE, "AOR")]),
            C(f"The woman carries the sheep with the {n}.", [N(WOMAN, "SUBJ"), N(SHEEP, "OBJ"), N(lid, "INS"), V(CARRY)]),
            C(f"The mother does not see the {n}.", [N(MOTHER, "SUBJ"), N(lid, "OBJ"), V(SEE)], neg=True),
            C(f"The old {n} sees the house.", [N(lid, "SUBJ"), {"lex_id": OLD, "role": "MOD", "head": 0}, N(HOUSE, "OBJ"), V(SEE)]),
        ]
        out["test"] += [
            C(f"The {n} carries the horse.", [N(lid, "SUBJ"), N(HORSE, "OBJ"), V(CARRY)]),
            C(f"The woman saw the {ns}.", [N(WOMAN, "SUBJ"), N(lid, "OBJ", "PL"), V(SEE, "AOR")]),
            C(f"The mother of the {ns} sees the house.", [N(MOTHER, "SUBJ"), N(lid, "POSS", "PL", head=0), N(HOUSE, "OBJ"), V(SEE)]),
        ]
    elif fam == "verb":
        v = re.sub(r"^to ", "", sense)
        C = lambda e, slots, **kw: (e, {"english": e, "clauses": [{"slots": slots, **kw}]})
        Ii = lambda num: N(I_, "SUBJ", num)
        out["train"] += [
            C(f"The man {third(v)}.", [N(MAN, "SUBJ"), V(lid)]),
            C(f"The woman {past(v)}.", [N(WOMAN, "SUBJ"), V(lid, "AOR")]),
            C(f"The woman {past(v)}.", [N(WOMAN, "SUBJ"), V(lid, "PST")]),
            C(f"We {v}.", [Ii("PL"), V(lid)]),
            C(f"I {past(v)}.", [Ii("SG"), V(lid, "AOR")]),
            C(f"I {past(v)}.", [Ii("SG"), V(lid, "PST")]),
            C(f"The men {v}.", [N(MAN, "SUBJ", "PL"), V(lid)]),
            C(f"The father does not {v}.", [N(FATHER, "SUBJ"), V(lid)], neg=True),
            C(f"{v[0].upper() + v[1:]}, mother!", [N(MOTHER, "VOC"), V(lid, mood="IMP", person=2)]),
            C(f"The man {third(v)} the sheep.", [N(MAN, "SUBJ"), N(SHEEP, "OBJ"), V(lid)]),
            C(f"The old man {third(v)}.", [N(MAN, "SUBJ"), {"lex_id": OLD, "role": "MOD", "head": 0}, V(lid)]),
        ]
        out["test"] += [
            C(f"The mother {third(v)}.", [N(MOTHER, "SUBJ"), V(lid)]),
            C(f"The horses {past(v)}.", [N(HORSE, "SUBJ", "PL"), V(lid, "AOR")]),
            C(f"The horses {past(v)}.", [N(HORSE, "SUBJ", "PL"), V(lid, "PST")]),
            C(f"The woman does not {v}.", [N(WOMAN, "SUBJ"), V(lid)], neg=True),
        ]
    elif fam == "adj":
        a = sense
        C = lambda e, slots, **kw: (e, {"english": e, "clauses": [{"slots": slots, **kw}]})
        M = lambda h: {"lex_id": lid, "role": "MOD", "head": h}
        out["train"] += [
            C(f"The {a} man sees the horse.", [N(MAN, "SUBJ"), M(0), N(HORSE, "OBJ"), V(SEE)]),
            C(f"The woman sees the {a} horse.", [N(WOMAN, "SUBJ"), N(HORSE, "OBJ"), M(1), V(SEE)]),
            C(f"The horse is {a}.", [N(HORSE, "SUBJ"), {"lex_id": lid, "role": "PRED"}], type="nominal"),
            C(f"The {a} men carry the sheep.", [N(MAN, "SUBJ", "PL"), M(0), N(SHEEP, "OBJ"), V(CARRY)]),
            C(f"The sheep are {a}.", [N(SHEEP, "SUBJ", "PL"), {"lex_id": lid, "role": "PRED"}], type="nominal"),
            C(f"The man saw the {a} house.", [N(MAN, "SUBJ"), N(HOUSE, "OBJ"), M(1), V(SEE, "AOR")]),
            C(f"The {a} woman carries the house.", [N(WOMAN, "SUBJ"), M(0), N(HOUSE, "OBJ"), V(CARRY)]),
            C(f"The father sees the {a} sheep.", [N(FATHER, "SUBJ"), N(SHEEP, "OBJ", "PL"), M(1), V(SEE)]),
        ]
        out["test"] += [
            C(f"The {a} mother sees the man.", [N(MOTHER, "SUBJ"), M(0), N(MAN, "OBJ"), V(SEE)]),
            C(f"The house is {a}.", [N(HOUSE, "SUBJ"), {"lex_id": lid, "role": "PRED"}], type="nominal"),
            C(f"The man carries the {a} horses.", [N(MAN, "SUBJ"), N(HORSE, "OBJ", "PL"), M(1), V(CARRY)]),
        ]
    return out


def build(fam, lid, sense, lx):
    from pie.realize import check_plan, realize
    res = {}
    for split, cands in frames(fam, lid, sense).items():
        seen, ok = set(), []
        for e, plan in cands:
            if e in seen:
                continue                       # an AOR frame realized: its PST twin is skipped
            try:
                if check_plan(plan, lx):
                    continue
                r = realize(plan, lx)
            except Exception:
                continue
            if not any(w.get("lex_id") == lid for w in r["words"]):
                continue
            seen.add(e)
            ok.append({"english": e, "pie": r["pie"]})
        res[split] = ok
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/Users/david/AI/pie-runs/rl/data/vocab1")
    ap.add_argument("--words", type=int, default=110)
    ap.add_argument("--control", type=int, default=50)
    a = ap.parse_args()
    from pie.realize import Lexicon
    from pie.translator.lexmap import _corpus_counts
    sys.path.insert(0, str(ROOT / "training/rl"))
    from make_sft1 import reference
    lx = Lexicon.load()
    uses = _corpus_counts()
    form_lid = {}
    for lid, e in lx.entries.items():
        form_lid.setdefault(e.get("form", "").strip("*"), lid)
    lemma_uses = {f: uses.get(lid, 0) for f, lid in form_lid.items()}

    cands = [json.loads(x) for x in (CHECK / "candidates.jsonl").read_text("utf-8").splitlines()]
    rates = {r["i"]: r["scores"] for r in map(json.loads, (CHECK / "passrate.jsonl").read_text("utf-8").splitlines())}
    stats = collections.Counter()
    pool = []
    for i, x in enumerate(cands):
        if x["type"].removeprefix("v.").split("|")[0] != "vocab_en_pie" or i not in rates or sum(rates[i]) > 0:
            continue
        sense = json.loads(x["answer"])["sense"].strip()
        if len(sense.split()) > 3 or re.search(r"[,;()/]", sense):
            stats["skip_sense"] += 1
            continue
        form = reference(x, lemma_uses)
        lid = form_lid.get(form)
        fam = (lx.entries.get(lid) or {}).get("pos")
        if fam not in ("noun", "verb", "adj"):
            stats["skip_family"] += 1
            continue
        s = build(fam, lid, sense, lx)
        if len(s["train"]) < 5 or len(s["test"]) < 2:
            stats["skip_few_sentences"] += 1
            continue
        pool.append({"i": i, "cand": x, "sense": sense, "form": form, "lex_id": lid, "family": fam, **s})
    rng = random.Random(SEED)
    rng.shuffle(pool)
    control, words = pool[:a.control], pool[a.control:a.control + a.words]
    stats["pool"] = len(pool)
    stats.update(f"family:{w['family']}" for w in words)

    def chat(user, answer, meta):
        return {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user},
                             {"role": "assistant", "content": answer}], "meta": meta}

    train, valid, test = [], [], []

    def test_row(row, w, control):          # eval_ckpt.py's prompt format, plus the word it tests
        return {"kind": "translate_en_pie", "id": f"vocab1-{len(test):04d}", "source_id": w["lex_id"],
                "prompt": row["messages"][:2], "reference": row["messages"][2]["content"], "lex_id": w["lex_id"],
                "sense": w["sense"], "control": control}
    for w in words:
        m = {"gap": "vocab1", "lex_id": w["lex_id"], "sense": w["sense"]}
        for k, s in enumerate(w["train"]):
            train.append(chat(rng.choice(EN_PIE).format(s["english"]), s["pie"], {**m, "dir": "en_pie"}))
            stats["en_pie"] += 1
            if k % 3 == 0:
                train.append(chat(rng.choice(PIE_EN).format(s["pie"]), s["english"], {**m, "dir": "pie_en"}))
                stats["pie_en"] += 1
        x = w["cand"]
        for _ in range(2):
            train.append({"messages": [{"role": "system", "content": x["system"]}, {"role": "user", "content": x["prompt"]},
                                       {"role": "assistant", "content": w["form"]}], "meta": {**m, "dir": "vocab"}})
            stats["vocab"] += 1
        for s in w["test"]:
            row = chat(EN_PIE[0].format(s["english"]), s["pie"], {**m, "dir": "test"})
            valid.append(row)
            test.append(test_row(row, w, False))
    for w in control:
        for s in w["test"]:
            test.append(test_row(chat(EN_PIE[0].format(s["english"]), s["pie"], {}), w, True))
    export = [json.loads(l) for l in (ROOT / "export/chat/train.jsonl").read_text("utf-8").splitlines()]
    n_replay = int(len(train) * REPLAY / (1 - REPLAY))
    for j in rng.sample(range(len(export)), n_replay):
        train.append({"messages": export[j]["messages"], "meta": {"gap": "replay", "task": export[j]["meta"].get("task")}})
    stats["replay"] = n_replay
    rng.shuffle(train)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    wr = lambda name, rows: (out / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    wr("train.jsonl", train)
    wr("valid.jsonl", valid)
    wr("test.jsonl", test)
    # bare prompts, passrate.py's candidate format (one dir each so passrate's outputs stay apart)
    for name, ws in (("words", words), ("control", control)):
        d = out / name
        d.mkdir(exist_ok=True)
        wr(f"{name}/candidates.jsonl", [w["cand"] for w in ws])
        (d / "manifest.json").write_text((CHECK / "manifest.json").read_text("utf-8"), "utf-8")
    wr("words.jsonl", [{k: w[k] for k in ("i", "sense", "form", "lex_id", "family")} | {"set": "train"} for w in words]
       + [{k: w[k] for k in ("i", "sense", "form", "lex_id", "family")} | {"set": "control"} for w in control])
    man = {"source": str(CHECK), "seed": SEED, "train": len(train), "valid": len(valid), "test": len(test),
           "words": len(words), "control": len(control), "stats": dict(sorted(stats.items()))}
    (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
