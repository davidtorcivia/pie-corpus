"""Engine reward for RL stage 1 (mlx-lm-lora --reward-functions-file): every answer is checked against the engine's
own forms, so no judge is needed.

Designed against reward hacking (the policy only ever sees this number):
- inflect: 1 only if the whole answer is one of the cell's admissible forms (an optional * and final period
  aside), else 0. Two forms, a hedge ("a or b"), or a form plus commentary score 0.
- paradigm: line by line. A line is a row ("CELL: form", one form) or it is junk. Each of the table's cells
  scores when its first row gives the engine's form; every other line (a repeated cell, a cell the table lacks,
  a row with two forms, prose) costs half a cell. Reward = (right - 0.5 * bad) / cells, floored at 0, so neither
  padding, nor second guesses, nor hedged rows pay, and the best answer is exactly the table.
- A truncated or looping answer scores what it got right: a cut-off table loses its missing cells, a looping form
  matches nothing, and the junk lines of a loop cost.
What the reward cannot see (meaning, translation, chat) is held by the KL term to the e3 model (beta in the
config), and checked outside the loop: the valid split is whole held-out lexemes, and the frozen v1 and v2
prompt sets (lexemes RL never sees) are re-scored on the checkpoints. Reward up with v2 flat is memorization.

Answers are JSON (training/rl/make_rl_prompts.py): a list of forms for inflect, {cell: form} for paradigm.
"""
import json
import os
import re
import time
import unicodedata

try:
    from mlx_lm_lora.trainer.grpo_reward_functions import register_reward_function
except ImportError:                          # the PIE env (tests/test_rl.py) has no mlx
    def register_reward_function(name=None):
        return lambda f: f

ROW = re.compile(r"\s*[-*]?\s*([A-Z][A-Z0-9.]+)\s*:\s*\*?([^\s*]+?)[.,;]?\s*")


def _clean(text: str) -> str:
    text = text.split("</think>")[-1]
    return unicodedata.normalize("NFC", text).strip()


def _form(text: str) -> str:
    return _clean(text).strip(" *.").strip()


def inflect_reward(completion: str, answer) -> float:
    forms = {unicodedata.normalize("NFC", f) for f in answer}
    return 1.0 if _form(completion) in forms else 0.0


def paradigm_reward(completion: str, answer: dict) -> float:
    ref = {c: unicodedata.normalize("NFC", f) for c, f in answer.items()}
    seen, right, bad = set(), 0, 0
    for line in _clean(completion).splitlines():
        if not line.strip():
            continue
        m = ROW.fullmatch(line)
        if not m or m[1] not in ref or m[1] in seen:
            bad += 1
            continue
        seen.add(m[1])
        right += m[2] == ref[m[1]]
    return max(0.0, (right - 0.5 * bad) / len(ref))


def score(completion: str, answer_json: str, kind: str) -> float:
    answer = json.loads(answer_json)
    return paradigm_reward(completion, answer) if kind == "paradigm" else inflect_reward(completion, answer)


@register_reward_function()
def pie_engine(prompts, completions, answer, types=None):
    types = types or ["inflect"] * len(answer)
    out = [score(c, a, t) for c, a, t in zip(completions, answer, types)]
    if os.environ.get("PIE_RL_REWARD_LOG"):          # per-kind means for the dashboard (training/rl/grpo.py)
        by = {}
        for r, t in zip(out, types):
            by.setdefault(t, []).append(r)
        row = {"t": time.time(), "n": len(out), **{f"reward/{k}": sum(v) / len(v) for k, v in by.items()}}
        with open(os.environ["PIE_RL_REWARD_LOG"], "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return out
