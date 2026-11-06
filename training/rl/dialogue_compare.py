"""Compare two checkpoints on dialogue with Claude Opus, independent of the RL reward (which is judged by Haiku).

v1 scores a dialogue reply by chrF to one reference reply, on 16 items from about ten distinct turns; a greedy
model that changes at all flips whole replies, so v1's dialogue numbers swing by points on a few turns. This judges
the replies themselves on a larger set: the v1 dialogue items plus the stage 8 validation dialogue rows (never
trained on).

    python -I training/rl/dialogue_compare.py build OUT.jsonl
    (generate OUT.jsonl with each checkpoint: training/rl/eval_ckpt.py --prompts OUT.jsonl --out GEN_X.jsonl)
    uv run python -I training/rl/dialogue_compare.py judge GEN_A.jsonl GEN_B.jsonl --names rl6b rl8 -o RESULT.json

judge: per item, (1) a pairwise verdict, the two replies shown in an order fixed by a hash of the item id, as
"better: A / B / tie"; (2) each reply on its own under judge.DIALOGUE (ok / wrong), both with Opus. Prints wins,
losses, ties and ok rates by mode.
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "training/rl"))
OPUS = "claude-opus-5-5"

PAIR = """You compare two replies in a conversation in Proto-Indo-European (PIE), from a reconstructed-PIE language project. The speaker is a person living in the PIE world. You get the `turn` being answered (English or PIE, with the task's instructions), two candidate replies `A` and `B`, the project grammar engine's `analysis` of every word of each (lemma, English gloss, grammatical cell, all readings, or UNKNOWN), and a `reference` reply that is one good answer, not the only one.

Decide which reply is the better answer from an in-world speaker: it answers what was asked or said, makes sense, stays in the world (no modern things, no talk about the language), follows the task's format, and is grammatical (each form fits its role, checked against the analysis). Closeness to the reference's wording does not matter; a different good answer is as good as the reference. Spelling conventions (laryngeals h₁ h₂ h₃, accents, ḱ/kʷ) are the project's own. Say "tie" when neither is clearly better (both good, both bad in comparable ways, or the same).

Answer with only a JSON object: {"better": "A" or "B" or "tie", "reason": one short sentence}."""


def build(out: Path) -> None:
    rows = [json.loads(x) for x in (ROOT / "training/gen_prompts_v1.jsonl").read_text("utf-8").splitlines() if x.strip()]
    items = [r for r in rows if "dialogue" in r["kind"]]
    for x in Path("/Users/david/AI/pie-runs/rl/data/rl8/valid.jsonl").read_text("utf-8").splitlines():
        r = json.loads(x)
        if "dialogue" not in r["type"]:
            continue
        ans = json.loads(r["answer"])
        items.append({"kind": r["type"].split("|", 1)[1].replace("|", "/"), "id": "valid-" + r["source_id"] + "-" + r["type"].split("|")[-1],
                      "source_id": r["source_id"], "prompt": [{"role": "system", "content": r["system"]}, {"role": "user", "content": r["prompt"]}],
                      "reference": ans["refs"][0]})
    out.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), "utf-8")
    print(len(items), "dialogue items ->", out)


def judge(fa: Path, fb: Path, names: list[str], out: Path, workers: int) -> None:
    import judge as J
    from judge import analysis, call, client, parse, PRICE, DIALOGUE
    from pie.realize import Lexicon
    from pie.translator.analyze import Analyzer
    an, lx, c = Analyzer.load(), Lexicon.load(), client()
    A = {r["id"]: r for r in map(json.loads, fa.read_text("utf-8").splitlines())}
    B = {r["id"]: r for r in map(json.loads, fb.read_text("utf-8").splitlines())}
    ids = [i for i in A if i in B]

    def pie_of(reply: str) -> str:
        return reply.split("English:")[0].strip()

    def one(i):
        a, b = A[i], B[i]
        turn = a["user"] if "user" in a else ""
        flip = int(hashlib.sha1(i.encode()).hexdigest(), 16) % 2 == 1
        first, second = (b, a) if flip else (a, b)
        item = {"turn": turn, "A": first["output"], "B": second["output"],
                "analysis_A": analysis(an, lx, pie_of(first["output"]))[0], "analysis_B": analysis(an, lx, pie_of(second["output"]))[0],
                "reference": a.get("reference", "")}
        body = json.dumps(item, ensure_ascii=False, indent=1)
        r = c.messages.create(model=OPUS, max_tokens=16000, system=PAIR, output_config={"effort": "high"},
                              messages=[{"role": "user", "content": body}])
        v = parse("".join(x.text for x in r.content if x.type == "text"))
        better = v.get("better", "unparsed")
        winner = {"A": names[1] if flip else names[0], "B": names[0] if flip else names[1]}.get(better, better)
        usd = (r.usage.input_tokens * PRICE[OPUS][0] + r.usage.output_tokens * PRICE[OPUS][1]) / 1e6
        solo = {}
        for name, g in ((names[0], a), (names[1], b)):
            rows, senses, _ = analysis(an, lx, pie_of(g["output"]))
            s = call(c, {"turn": turn, "reply": g["output"], "analysis": rows, "senses": senses, "reference": a.get("reference", "")},
                     model=OPUS, system=DIALOGUE)
            solo[name] = s["verdict"]; usd += s["usd"]
        return {"id": i, "kind": a["kind"], "winner": winner, "reason": v.get("reason", ""), "solo": solo, "usd": usd,
                names[0]: a["output"], names[1]: b["output"]}

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(one, ids))
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), "utf-8")
    def tally(rs):
        w = {n: sum(r["winner"] == n for r in rs) for n in names}
        ok = {n: sum(r["solo"][n] == "ok" for r in rs) for n in names}
        return f"n={len(rs)}  wins {names[0]} {w[names[0]]} / {names[1]} {w[names[1]]} / tie {sum(r['winner'] == 'tie' for r in rs)}" \
               f"  ok {names[0]} {ok[names[0]]} / {names[1]} {ok[names[1]]}"
    print("all     ", tally(res))
    for k in sorted({r["kind"] for r in res}):
        print(f"{k:28s}", tally([r for r in res if r["kind"] == k]))
    print(f"cost ${sum(r['usd'] for r in res):.2f} -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "judge"]); ap.add_argument("files", nargs="+")
    ap.add_argument("--names", nargs=2, default=["A", "B"]); ap.add_argument("-o", "--out")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if a.mode == "build":
        build(Path(a.files[0]))
    else:
        judge(Path(a.files[0]), Path(a.files[1]), a.names, Path(a.out), a.workers)
