"""The round-2 judge brief through the Claude API, one item per call (the shape the RL judge will have), with the
engine analysis inline and no tools. Records each call's usage and cost.

    uv run --with anthropic python -I training/judge_test/api_judge.py --model claude-haiku-5-5 --effort high \
        --out training/judge_test/verdicts3-api-haiku-high.json

Key: ANTHROPIC_API_KEY or ~/.config/anthropic/api_key; the org-level key needs ~/.config/anthropic/workspace_id.
"""
import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic

HERE = Path(__file__).resolve().parent
CFG = Path.home() / ".config/anthropic"
PRICE = {  # $ per M input, output tokens
    "claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0)}

SYSTEM = """You are judging Proto-Indo-European (PIE) text from a reconstructed-PIE language project. Each item pairs an English text with a PIE rendering. Decide whether the PIE says what the English says, grammatically.

Mark an item **wrong** if any word has the wrong meaning, the wrong inflection for its role (case, number, person, tense or mood the English doesn't call for, or a failure of agreement), if something the English says is missing or contradicted (for example a lost or added negation), or if a word isn't a real form. Otherwise mark it **ok**. Spelling conventions (laryngeals h₁ h₂ h₃, accents, ḱ/kʷ) are the project's own; don't count notation as an error. Small differences in word order or a looser but correct rendering are ok.

`analysis` is the project's grammar engine output for every word: its lemma, English gloss and grammatical cell, with all possible readings (a form can fit several cells), or UNKNOWN. Judge from the English, the PIE and this analysis. Check each word's role in the sentence against its cell: the case a noun needs for its role, the person and number a verb needs for its subject, agreement of adjectives and pronouns.

`senses` lists every meaning of a lemma when it has more than one; the analysis shows only the first, so check senses before calling a word the wrong meaning. The analysis may also miss a reading (an indeclinable, a rare form): don't mark a word wrong only because the analysis lacks the reading the sentence needs, if the form is plausibly that word.

This project's grammar (inherited rules, not errors):
- A neuter plural subject takes a singular verb (the old collective).
- Verbs of fearing take the ablative of what is feared.
- The project writes no augment, so a form the engine calls PST also serves as the injunctive: mḗ + injunctive is a prohibition ("do not go").
- The middle can change a verb's meaning (h₁áyt 'give', middle 'take, receive'); senses give it.
- A 2PL may address one person who speaks for a group.

Answer with only a JSON object: {"verdict": "ok" or "wrong", "word": the PIE word at fault or null, "reason": one short sentence}."""


def client():
    key = os.environ.get("ANTHROPIC_API_KEY") or (CFG / "api_key").read_text().strip()
    ws = CFG / "workspace_id"
    headers = {"anthropic-workspace-id": ws.read_text().strip()} if ws.exists() else None
    return anthropic.Anthropic(api_key=key, default_headers=headers, max_retries=6)


def judge(c, model, effort, item):
    body = json.dumps({k: item[k] for k in ("english", "pie", "analysis", "senses") if k in item}, ensure_ascii=False, indent=1)
    t = time.time()
    r = c.messages.create(model=model, max_tokens=16000, system=SYSTEM, output_config={"effort": effort},
                          messages=[{"role": "user", "content": body}])
    text = "".join(b.text for b in r.content if b.type == "text")
    m = re.search(r"\{.*\}", text, re.S)
    try:
        v = json.loads(m[0]) if m else {}
    except json.JSONDecodeError:     # an unescaped quote in the reason: the verdict and word are still readable
        v = {k: (x[1] if x else None) for k, x in
             (("verdict", re.search(r'"verdict"\s*:\s*"(ok|wrong)"', text)), ("word", re.search(r'"word"\s*:\s*"([^"]*)"', text)))}
        v = {**v, "reason": text[:200]} if v["verdict"] else {}
    u = r.usage
    return {"id": item["id"], "verdict": v.get("verdict", "unparsed"), "word": v.get("word"),
            "reason": v.get("reason", text[:200]), "in": u.input_tokens, "out": u.output_tokens,
            "s": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-5-5")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--items", default=str(HERE / "items_v2.jsonl"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only-flagged", help="a verdicts file: judge only the items it marked wrong (the tier-2 check)")
    a = ap.parse_args()
    items = [json.loads(x) for x in Path(a.items).read_text("utf-8").splitlines() if x.strip()]
    if a.only_flagged:
        flagged = {v["id"] for v in json.loads(Path(a.only_flagged).read_text()) if v["verdict"] != "ok"}
        items = [it for it in items if it["id"] in flagged]
    c = client()
    t = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(lambda it: judge(c, a.model, a.effort, it), items))
    Path(a.out).write_text(json.dumps(rows, ensure_ascii=False, indent=0), "utf-8")
    pi, po = PRICE[a.model]
    tin, tout = sum(r["in"] for r in rows), sum(r["out"] for r in rows)
    cost = (tin * pi + tout * po) / 1e6
    print(f"{a.model} {a.effort}: {len(rows)} items, {time.time() - t:.0f} s wall, in {tin} out {tout} tokens, "
          f"${cost:.4f} (${cost / len(rows) * 1000:.2f} per 1000 judgments), "
          f"unparsed {sum(r['verdict'] == 'unparsed' for r in rows)}")


if __name__ == "__main__":
    main()
