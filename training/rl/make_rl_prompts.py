"""The engine-checkable RL prompt set (stage 1 of RL, no judge): inflection and paradigm drills of training-split
lexemes, on cells and tables the SFT export did not drill, in the export's own prompt format (task_chat /
paradigm_chat). Ablauting lexemes get more of both, since ablaut is the gap (docs/research/training-runs.md).

    uv run python -I training/rl/make_rl_prompts.py [--out DIR] [--n 4000] [--valid 64]

Held out, so RL never trains on what is scored: every lexeme with an eval task (export/eval_tasks.jsonl), and every
lexeme of the frozen prompt sets training/gen_prompts_v1.jsonl and gen_prompts_drills_v2.jsonl. Each item carries
its acceptable answers (the cell's admissible forms; a table's rows) for training/rl/reward_engine.py.
Writes DIR/train.jsonl and DIR/valid.jsonl (mlx-lm-lora GRPO format: system, prompt, answer, type) and
DIR/manifest.json.
"""
import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pie import export_chat as ec  # noqa: E402
from pie.export import GENDER_TAG  # noqa: E402
from pie.realize import Lexicon  # noqa: E402

NEW_CELLS = {False: 4, True: 10}        # unseen cells per lexeme, by ablauting
SEED = 20261101
TR_MAX_WORDS = 35        # EN→PIE prompts: up to 35 English words, as the judge test's items (15–45) and the demo's input


def held_lexemes() -> set[str]:
    held = {json.loads(x)["source_id"] for x in (ROOT / "export/eval_tasks.jsonl").read_text("utf-8").splitlines()}
    for p in ("training/gen_prompts_v1.jsonl", "training/gen_prompts_drills_v2.jsonl"):
        held |= {json.loads(x).get("source_id") for x in (ROOT / p).read_text("utf-8").splitlines()}
    return held - {None}


def ablauting(lx, lid: str) -> bool:
    sp = lx.specs[lid]["spec"]
    return bool(sp.get("weak") or sp.get("m_weak"))


def all_cells(lx, lid: str) -> dict[str, list[str]]:
    if lx.specs[lid]["family"] == "adj":
        return {f"{GENDER_TAG[g]}.{f}": v for g in "mfn" for f, v in lx.admissible_cells(lid, g).items()}
    return lx.admissible_cells(lid)


def item(chat: dict, kind: str, answers, lid: str, abl: bool) -> dict:
    sysm, user = chat["messages"][0]["content"], chat["messages"][1]["content"]
    return {"system": sysm, "prompt": user, "answer": json.dumps(answers, ensure_ascii=False), "type": kind,
            "source_id": lid, "ablauting": abl}


def build(n: int, n_valid: int) -> tuple[list[dict], list[dict], dict]:
    lx = Lexicon.load()
    held = held_lexemes()
    drilled = {}
    for x in (ROOT / "export/train_tasks.jsonl").read_text("utf-8").splitlines():
        t = json.loads(x)
        if t["task"] == "inflect":
            drilled.setdefault(t["source_id"], set()).add(t["input"].rsplit(" ", 1)[1])
    lexemes = sorted(set(drilled) - held)
    inflect, paradigm = [], []
    for lid in lexemes:
        abl = ablauting(lx, lid)
        cells = all_cells(lx, lid)
        new = sorted(c for c in cells if c not in drilled[lid] and cells[c])
        lemma = lx.entries[lid]["form"]
        for c in random.Random(f"rl|{SEED}|{lid}").sample(new, min(NEW_CELLS[abl], len(new))):
            t = {"task": "inflect", "input": f"{lemma} {c}", "output": cells[c][0], "source_id": lid}
            inflect.append(item(ec.task_chat(t, None), "inflect", list(dict.fromkeys(cells[c])), lid, abl))
        fam = lx.specs[lid]["family"]
        blocks = [None]
        if fam == "adj":
            blocks = list("mfn") if abl else [None]
        elif fam == "verb" and abl:
            have = {ec._verb_block(c) for c in lx.admissible_cells(lid)}
            blocks = [b for b in ec.ABLAUT_BLOCKS if b in have] or [None]
        for b in blocks:
            p = ec.paradigm_task(lx, lid, b)
            if p:
                chat = ec.paradigm_chat(p, {}, extra=b is not None)
                rows = dict(r.split(": ", 1) for r in p["output"].split("\n"))
                paradigm.append(item(chat, "paradigm", rows, lid, abl))
    # dedupe paradigms that resolved to the same table (a block a verb lacks falls back to its default)
    seen, uniq = set(), []
    for x in paradigm:
        k = (x["source_id"], x["answer"])
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    paradigm = uniq
    rng = random.Random(SEED)
    pool = inflect + paradigm
    rng.shuffle(pool)
    # valid: whole lexemes, so no valid lexeme is trained on
    vlex = set(rng.sample(sorted({x["source_id"] for x in pool}), max(1, n_valid // 4)))
    valid = [x for x in pool if x["source_id"] in vlex][:n_valid]
    train = [x for x in pool if x["source_id"] not in vlex]
    # paradigms are long answers: about a third of the prompts, ablauting ones first in line
    want_p = min(len([x for x in train if x["type"] == "paradigm"]), n // 3)
    ps = sorted((x for x in train if x["type"] == "paradigm"), key=lambda x: not x["ablauting"])[:want_p]
    infl = [x for x in train if x["type"] == "inflect"][: n - want_p]
    train = ps + infl
    rng.shuffle(train)
    man = {"seed": SEED, "lexemes": len(lexemes), "held_lexemes": len(held), "train": len(train), "valid": len(valid),
           "by_kind": dict(Counter(f"{x['type']}:{'abl' if x['ablauting'] else 'non'}" for x in train)),
           "valid_lexemes": sorted(vlex)}
    return train, valid, man


def stem(lx, lid: str) -> str:
    sp = lx.specs[lid]
    return f"{sp['family']}:{sp['rule'].split(':')[-1]}" + (":abl" if ablauting(lx, lid) else "")


def number(cell: str) -> str:
    return next((n for n in ("DU", "PL", "SG") if n in cell.split(".")), "other")


def build_v2(n_infl: int, n_par: int, n_tr: int) -> tuple[list[dict], list[dict], dict]:
    """Stage 1b candidates (docs/research/rl-mac.md, next round): every training lexeme at its natural share, not
    ablauting first; 2 undrilled cells + 1 cell the SFT export drilled (an anchor, so known endings are rehearsed)
    per lexeme, and a dual cell for half the nominals (stage 1 taught the consonant-stem dual -h₁e only on
    ablauting stems, and the model spread it to thematic and eh₂ stems); paradigms of every family; and EN→PIE
    translation of training-split records, judged (reward_rl.py). Types carry the stratum. Candidates are then
    filtered by e3's own pass rate (training/rl/passrate.py), so the final set is chosen there."""
    lx = Lexicon.load()
    held = held_lexemes()
    drilled, tr = {}, []
    held_rec = held | {json.loads(x)["source_id"] for x in (ROOT / "export/eval_dialogues.jsonl").read_text("utf-8").splitlines()
                       if x.strip() and json.loads(x).get("source_id")}
    for x in (ROOT / "export/train_tasks.jsonl").read_text("utf-8").splitlines():
        t = json.loads(x)
        if t["task"] == "inflect":
            drilled.setdefault(t["source_id"], set()).add(t["input"].rsplit(" ", 1)[1])
        elif (t["task"] == "translate_en_pie" and t["source_id"] not in held_rec
              and len(t["input"].split()) <= TR_MAX_WORDS + 3):
            tr.append(t)
    rng = random.Random(SEED + 1)
    lexemes = sorted(set(drilled) - held)
    # valid: whole lexemes, a few per stratum, so every stem class is watched during the run
    by_stem = {}
    for lid in lexemes:
        by_stem.setdefault(stem(lx, lid), []).append(lid)
    vlex = set()
    for st, ls in sorted(by_stem.items()):
        if len(ls) >= 8:
            vlex |= set(rng.sample(sorted(ls), 2 if len(ls) < 200 else 3))
    inflect, paradigm = [], []
    for lid in lexemes:
        abl, st = ablauting(lx, lid), stem(lx, lid)
        cells = {c: v for c, v in all_cells(lx, lid).items() if v}
        lemma = lx.entries[lid]["form"]
        r = random.Random(f"rl2|{SEED}|{lid}")
        new = sorted(c for c in cells if c not in drilled[lid])
        old = sorted(c for c in cells if c in drilled[lid])
        pick = r.sample(new, min(2, len(new))) + r.sample(old, min(1, len(old)))
        duals = sorted(c for c in cells if number(c) == "DU" and c not in pick)
        if duals and lx.specs[lid]["family"] != "verb" and r.random() < 0.5:
            pick.append(r.choice(duals))
        for c in pick:
            t = {"task": "inflect", "input": f"{lemma} {c}", "output": cells[c][0], "source_id": lid}
            x = item(ec.task_chat(t, None), f"inflect|{st}|{number(c)}", list(dict.fromkeys(cells[c])), lid, abl)
            inflect.append(x)
        fam = lx.specs[lid]["family"]
        blocks = [None]
        if fam == "adj":
            blocks = list("mfn")
        elif fam == "verb" and abl:
            have = {ec._verb_block(c) for c in lx.admissible_cells(lid)}
            blocks = [b for b in ec.ABLAUT_BLOCKS if b in have] or [None]
        seen = set()
        for b in blocks:
            p = ec.paradigm_task(lx, lid, b)
            if p and p["output"] not in seen:
                seen.add(p["output"])
                rows = dict(x.split(": ", 1) for x in p["output"].split("\n"))
                paradigm.append(item(ec.paradigm_chat(p, {}, extra=b is not None), f"paradigm|{st}", rows, lid, abl))
    trans = []
    for t in tr:
        chat = ec.task_chat(t, None)
        english = chat["messages"][1]["content"]
        eng = __import__("re").sub(r"^\[style: [^\]]*\] ", "", t["input"])
        if len(eng.split()) > TR_MAX_WORDS:
            continue
        refs = list(dict.fromkeys([t["output"], *t.get("acceptable", [])]))
        x = item(chat, "translate_en_pie", {"english": eng, "refs": refs}, t["source_id"], False)
        trans.append(x)
    vrec = set(rng.sample(sorted({x["source_id"] for x in trans}), 24))
    valid = [x for x in inflect + paradigm if x["source_id"] in vlex] + [x for x in trans if x["source_id"] in vrec]
    for x in valid:
        x["type"] = "v." + x["type"]
    pools = {"inflect": [x for x in inflect if x["source_id"] not in vlex],
             "paradigm": [x for x in paradigm if x["source_id"] not in vlex],
             "translate": [x for x in trans if x["source_id"] not in vrec]}
    cand = []
    for k, want in (("inflect", n_infl), ("paradigm", n_par), ("translate", n_tr)):
        rng.shuffle(pools[k])
        cand += pools[k][:want]
    # valid: up to 4 drills per valid lexeme, all 24 translations
    vr = random.Random(SEED + 2)
    vd = {}
    for x in valid:
        vd.setdefault(x["source_id"], []).append(x)
    valid = [y for k in sorted(vd) for y in (vr.sample(vd[k], min(4, len(vd[k]))) if not vd[k][0]["type"].startswith("v.translate") else vd[k])]
    vr.shuffle(valid)
    man = {"seed": SEED, "mix": "v2", "lexemes": len(lexemes), "held_lexemes": len(held), "candidates": len(cand),
           "valid": len(valid), "valid_lexemes": sorted(vlex), "valid_records": sorted(vrec),
           "by_kind": dict(Counter(x["type"].split("|")[0] for x in cand)),
           "by_stratum": dict(Counter(x["type"] for x in cand).most_common()),
           "valid_by_stratum": dict(Counter(x["type"] for x in valid).most_common())}
    return cand, valid, man


VOCAB_EN_PIE = ["What is your word for '{x}'? Answer with the word alone.",
                "How do you say '{x}' in your language? Give just the word.",
                "Give the word for '{x}', in its dictionary form."]
VOCAB_PIE_EN = ["What does *{w} mean? Answer in English, in a few words.",
                "Say in English what *{w} means.",
                "*{w}: what is that in English? A few words."]


def senses(meanings: list[str]) -> list[str]:
    """A lexicon entry's meanings as short English phrases: 'to give (active); MID: to take, receive' ->
    ['to give', 'to take', 'receive']."""
    out = []
    for m in meanings:
        for x in re.split(r"[,;]", re.sub(r"\([^)]*\)|\b[A-Z]{2,}:\s*", " ", m)):
            x = " ".join(x.lower().split()).strip(" .")
            if x and len(x.split()) <= 4 and x not in out:
                out.append(x)
    return out


def build_v3(vlex: set, vrec: set, n_vocab: int, n_pie_en: int) -> tuple[list[dict], list[dict]]:
    """Stage 1b's added kinds (owner, 2026-11-01: vocabulary drills and PIE→EN, for the PIE→EN gap):
    vocab_en_pie (an English meaning -> the word; any lemma the lexicon lists for that meaning counts),
    vocab_pie_en (a word -> its meaning; judged unless it is one of the senses), and translate_pie_en of
    training-split records (judged unless it is a reference). Training lexemes and records only; the valid
    split's lexemes and records give the valid items."""
    lx = Lexicon.load()
    held = held_lexemes()
    rng = random.Random(SEED + 3)
    by_sense = {}
    lex = []
    for lid, e in lx.entries.items():
        if e.get("kind") == "root" or not e.get("meaning") or e["form"].endswith("-") or lid in held:
            continue
        if lid in lx.specs and lx.inadmissible(lid) and lx.specs[lid]["family"] is not None:
            continue
        ss = senses(e["meaning"])
        if not ss:
            continue
        lex.append((lid, e["form"], ss))
        for x in ss:
            by_sense.setdefault(x, set()).add(e["form"])
    vocab, valid = [], []
    for lid, form, ss in sorted(lex):
        r = random.Random(f"vocab|{SEED}|{lid}")
        sense = ss[0]
        tpl = r.randrange(3)
        sysm = ec.system(f"vocab|{lid}", ec.TEACHER[r.randrange(len(ec.TEACHER))])
        a = item({"messages": [{"role": "system", "content": sysm},
                               {"role": "user", "content": VOCAB_EN_PIE[tpl].format(x=sense)}]},
                 "vocab_en_pie", {"sense": sense, "lemmas": sorted(by_sense[sense])}, lid, False)
        b = item({"messages": [{"role": "system", "content": sysm},
                               {"role": "user", "content": VOCAB_PIE_EN[tpl].format(w=form)}]},
                 "vocab_pie_en", {"word": form, "senses": ss}, lid, False)
        (valid if lid in vlex else vocab).extend([a, b])
    rng.shuffle(vocab)
    en, pe = [x for x in vocab if x["type"] == "vocab_en_pie"], [x for x in vocab if x["type"] == "vocab_pie_en"]
    cand = en[:n_vocab // 2] + pe[:n_vocab // 2]
    held_rec = held | {json.loads(x)["source_id"] for x in (ROOT / "export/eval_dialogues.jsonl").read_text("utf-8").splitlines()
                       if x.strip() and json.loads(x).get("source_id")}
    pie_en = []
    for x in (ROOT / "export/train_tasks.jsonl").read_text("utf-8").splitlines():
        t = json.loads(x)
        if t["task"] != "translate_pie_en" or t["source_id"] in held_rec or len(t["output"].split()) > TR_MAX_WORDS:
            continue
        refs = list(dict.fromkeys([t["output"], *t.get("acceptable", [])]))
        it = item(ec.task_chat(t, None), "translate_pie_en", {"pie": t["input"], "refs": refs}, t["source_id"], False)
        (valid if t["source_id"] in vrec else pie_en).append(it)
    rng.shuffle(pie_en)
    cand += pie_en[:n_pie_en]
    vr = random.Random(SEED + 4)
    valid = vr.sample([x for x in valid if x["type"].startswith("vocab")], min(16, sum(x["type"].startswith("vocab") for x in valid))) \
        + [x for x in valid if x["type"] == "translate_pie_en"][:16]
    for x in valid:
        x["type"] = "v." + x["type"]
    return cand, valid


def build_dialogue(n: int, n_valid: int = 16) -> tuple[list[dict], list[dict]]:
    """Dialogue (owner, 2026-11-01): a conversation's first exchange from the chat export's training dialogues
    (en_dialogue in modes en_pie and mixed, pie_dialogue), the rollout being the speaker's reply, judged
    (reward_rl.py). Held-out records excluded; n_valid whole records kept for the valid split."""
    held = held_lexemes() | {json.loads(x)["source_id"] for x in (ROOT / "export/eval_dialogues.jsonl").read_text("utf-8").splitlines()
                             if x.strip() and json.loads(x).get("source_id")}
    rows = []
    for x in (ROOT / "export/chat/train.jsonl").read_text("utf-8").splitlines():
        r = json.loads(x)
        m = r["meta"]
        if m["task"] not in ("en_dialogue", "pie_dialogue") or m.get("mode") == "en_pie_gloss" or m["source_id"] in held:
            continue
        msgs = r["messages"]
        if len(msgs) < 3 or msgs[1]["role"] != "user" or msgs[2]["role"] != "assistant":
            continue
        rows.append(item({"messages": msgs[:2]}, f"dialogue|{m['task']}|{m.get('mode', 'pie')}",
                         {"turn": msgs[1]["content"], "refs": [msgs[2]["content"]]}, m["source_id"], False))
    rng = random.Random(SEED + 5)
    rng.shuffle(rows)
    vrec = set(rng.sample(sorted({x["source_id"] for x in rows}), n_valid))
    valid = [x for x in rows if x["source_id"] in vrec][:n_valid]
    for x in valid:
        x["type"] = "v." + x["type"]
    seen, cand = set(), []
    for x in rows:                                   # one exchange per record
        if x["source_id"] not in vrec and x["source_id"] not in seen:
            seen.add(x["source_id"])
            cand.append(x)
    return cand[:n], valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", default="v1", choices=["v1", "v2", "v3", "dialogue"])
    ap.add_argument("--out", default="/Users/david/AI/pie-runs/rl/data/engine_drills")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--valid", type=int, default=64)
    a = ap.parse_args()
    if a.mix == "dialogue":           # appended to a v2+v3 data dir (passrate.py resumes)
        out = Path(a.out)
        man = json.loads((out / "manifest.json").read_text())
        if "dialogue" in man.get("mix", ""):
            sys.exit("dialogue already added")
        cand, valid = build_dialogue(1500)
        with open(out / "candidates.jsonl", "a", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in cand)
        with open(out / "valid.jsonl", "a", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in valid)
        man["mix"] += "+dialogue"
        man["dialogue"] = {"candidates": dict(Counter(x["type"] for x in cand)), "valid": len(valid)}
        (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
        print(json.dumps(man["dialogue"]))
        return
    if a.mix == "v3":                 # v2's candidates plus the added kinds, appended (passrate.py resumes)
        out = Path(a.out)
        man = json.loads((out / "manifest.json").read_text())
        if "v3" in man.get("mix", ""):
            sys.exit("v3 kinds already added")
        cand, valid = build_v3(set(man["valid_lexemes"]), set(man["valid_records"]), 2400, 1500)
        with open(out / "candidates.jsonl", "a", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in cand)
        with open(out / "valid.jsonl", "a", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in valid)
        man["mix"] = "v2+v3"
        man["v3"] = {"candidates": dict(Counter(x["type"] for x in cand)), "valid": dict(Counter(x["type"] for x in valid))}
        (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
        print(json.dumps(man["v3"]))
        return
    if a.mix == "v2":                 # candidates for passrate.py, which writes the final train.jsonl
        cand, valid, man = build_v2(3000, 1200, 2400)
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        for name, rows in (("candidates", cand), ("valid", valid), ("test", valid[:8])):
            (out / f"{name}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
        (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
        print(json.dumps({k: v for k, v in man.items() if k not in ("valid_lexemes", "valid_records", "by_stratum")}))
        return
    train, valid, man = build(a.n, a.valid)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("train", train), ("valid", valid), ("test", valid[:8])):
        (out / f"{name}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
    (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
    print(json.dumps({k: v for k, v in man.items() if k != "valid_lexemes"}))


if __name__ == "__main__":
    main()
