"""RL stage 1b reward (mlx-lm-lora --reward-functions-file): engine drills as in stage 1, plus EN→PIE translation
judged in tiers, so only rollouts the local checks cannot decide reach the Claude judge (owner, 2026-11-01).

Translation (type translate_en_pie; answer {"english", "refs"}), designed against reward hacking:
1. Local zero: an empty answer, more than one line (commentary), more words than 2 x the longest reference + 3
   (padding), or any word the engine does not know or knows only as a near spelling (unknown, "close"), which is
   also how an English word or an invented form fails.
2. Local one: the answer is one of the references (NFC, punctuation and case aside).
3. The rest: training/rl/judge.py (Haiku high screens; a second Haiku high call re-checks its flags; wrong only if
   both say so). ok = 1, times 0.95 for each word matched only without its accent or as a typed spelling (the
   project's notation counts); wrong = 0; no verdict (API failure, unparsed twice) = 0.5, which gives a group of
   them no advantage.
Every judgment is logged to PIE_RL_JUDGE_LOG (default RUN/judge.jsonl) for auditing what was rewarded.

PIE→EN (translate_pie_en; answer {"pie", "refs"}), added 2026-11-01: local zero for more than one line, padding,
or PIE left in the English; local one for a reference; else the judge, with the rollout as the English side.
Vocabulary (owner, 2026-11-01): vocab_en_pie (answer {"sense", "lemmas"}) is scored locally, 1 for any lemma the
lexicon gives that meaning, 0.5 without its accent, 0 for anything but one word; vocab_pie_en (answer {"word",
"senses"}) is 1 for one of the senses, 0 for more than 8 words or PIE in it, else the judge.

Dialogue (type "dialogue|<task>|<mode>"; answer {"turn", "refs"}), added 2026-11-01: local zero for an echo of the
turn, commentary, modern talk, padding or an unknown word; local one for the reference; else the judge's dialogue
brief (judge.DIALOGUE; validated against Opus on 150 benchmark replies: 85% agreement).

Types carry the stratum for the dashboard: "inflect|<stem>|<number>", "paradigm|<family>|<abl>", and a "v." prefix
on the valid split, so validation is reported per stratum (training/rl/make_rl_prompts.py --mix v2).
"""
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import reward_engine as re_  # noqa: E402
from reward_engine import register_reward_function  # noqa: E402

_JUDGE = None


def judge():
    global _JUDGE
    if _JUDGE is None:
        from judge import Judge
        _JUDGE = Judge(os.environ.get("PIE_RL_JUDGE_LOG"))
    return _JUDGE


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s).lower()
    return " ".join(w.strip(".,;:?!\"“”'()") for w in s.split())


def local(completion: str, answer: dict, an) -> tuple[float | None, int]:
    """(reward or None if the judge must decide, number of inexact words)."""
    from judge import words
    text = re_._clean(completion)
    lines = [x for x in text.splitlines() if x.strip()]
    if len(lines) != 1:
        return 0.0, 0
    text = lines[0].strip()
    if _norm(text) in {_norm(r) for r in answer["refs"]}:
        return 1.0, 0
    ws = words(text)
    if not ws or len(ws) > 2 * max(len(r.split()) for r in answer["refs"]) + 3:
        return 0.0, 0
    inexact = 0
    for w in ws:
        res, how = an.word(w)
        if not res or how == "close":
            return 0.0, 0
        inexact += how != "exact"
    return None, inexact


PIE_CHARS = re.compile(r"[₁₂₃ʰʷḱǵ]|[a-z]*h[123]")


def local_pie_en(completion: str, answer: dict) -> float | None:
    """PIE→EN sentence: one line of English (no PIE left in it, not padded); a reference scores 1, else the judge."""
    text = re_._clean(completion)
    lines = [x for x in text.splitlines() if x.strip()]
    if len(lines) != 1:
        return 0.0
    t = lines[0].strip()
    ws = t.split()
    if not ws or len(ws) > 2 * max(len(r.split()) for r in answer["refs"]) + 5:
        return 0.0
    if sum(bool(PIE_CHARS.search(w)) for w in ws) > max(1, len(ws) // 5):   # left in PIE, or a gloss
        return 0.0
    return 1.0 if _norm(t) in {_norm(r) for r in answer["refs"]} else None


def _sense(s: str) -> str:
    s = _norm(s)
    return re.sub(r"^(to|a|an|the) ", "", s)


def local_vocab_pie_en(completion: str, answer: dict) -> float | None:
    """A word's meaning: a few English words; one of the lexicon's senses scores 1, else the judge."""
    t = re_._clean(completion).strip().split("\n")[0].strip(" .\"'")
    if not t or len(t.split()) > 8 or PIE_CHARS.search(t):
        return 0.0
    return 1.0 if _sense(t) in {_sense(x) for x in answer["senses"]} else None


def vocab_en_pie(completion: str, answer: dict) -> float:
    """The word for a meaning: one word, any lemma the lexicon lists for that meaning; without its accent half."""
    t = re_._clean(completion).strip().strip(" .*\"'")
    if not t or len(t.split()) != 1:
        return 0.0
    w = unicodedata.normalize("NFC", t.lstrip("*")).lower()
    lem = {unicodedata.normalize("NFC", x).lower() for x in answer["lemmas"]}
    if w in lem:
        return 1.0
    from pie.translator.analyze import unaccented
    return 0.5 if unaccented(w) in {unaccented(x) for x in lem} else 0.0


MODERN = re.compile(r"\b(proto-indo-european|reconstruct\w*|language model|computer|machine|internet|phone)\b", re.I)


def _toks(t: str) -> list[str]:
    return [unicodedata.normalize("NFC", w.strip(".,;:?!*'\"«»“”")).lower() for w in t.split() if w.strip(".,;:?!*'\"«»“”")]


def echoes(turn: str, reply: str) -> bool:
    """The reply is (nearly) the turn again: 90% of its words are the turn's and it is no longer than the turn
    plus one word (tuned on the benchmark against Opus's grades: catches the echoes Haiku passed, few real answers)."""
    a, b = set(_toks(turn)), _toks(reply)
    return bool(b) and sum(w in a for w in b) / len(b) >= 0.9 and len(b) <= len(_toks(turn)) + 1


def local_dialogue(completion: str, answer: dict, an) -> float | None:
    """A dialogue reply: local zero for an echo of the turn, commentary or modern talk, padding (3 x the reference
    + 5 words), or any word the engine doesn't know (English fails here); the reference scores 1; else the judge."""
    from judge import words
    t = re_._clean(completion).strip()
    if not t or echoes(answer["turn"], t) or MODERN.search(t) or re.search(r"(English|Gloss|Translation):", t):
        return 0.0
    if _norm(t) in {_norm(r) for r in answer["refs"]}:
        return 1.0
    ws = words(t)
    if not ws or len(ws) > 3 * max(len(r.split()) for r in answer["refs"]) + 5:
        return 0.0
    for w in ws:
        res, how = an.word(w)
        if not res or how == "close":
            return 0.0
    return None


def score_all(completions, answers, types) -> list[float]:
    out: list[float | None] = [None] * len(completions)
    todo = []
    for i, (c, a, t) in enumerate(zip(completions, answers, types)):
        kind = t.removeprefix("v.").split("|")[0]
        if kind == "translate_en_pie":
            ans = json.loads(a)
            r, inexact = local(c, ans, judge().an)
            if r is None:
                todo.append((i, ans["english"], re_._clean(c).strip(), inexact))
            else:
                out[i] = r
        elif kind == "translate_pie_en":
            ans = json.loads(a)
            r = local_pie_en(c, ans)
            if r is None:          # the judge's pair is (English, PIE) whichever way the translation went
                todo.append((i, re_._clean(c).strip(), ans["pie"], 0, ("pie_en", ans["refs"][0])))
            else:
                out[i] = r
        elif kind == "vocab_pie_en":
            ans = json.loads(a)
            r = local_vocab_pie_en(c, ans)
            if r is None:
                todo.append((i, re_._clean(c).strip().split("\n")[0], ans["word"], 0))
            else:
                out[i] = r
        elif kind == "dialogue":
            ans = json.loads(a)
            r = local_dialogue(c, ans, judge().an)
            if r is None:
                ref = ans["refs"][0]
                todo.append((i, "", re_._clean(c).strip(), 0, (ans["turn"], ref)))
            else:
                out[i] = r
        elif kind == "vocab_en_pie":
            out[i] = vocab_en_pie(c, json.loads(a))
        else:
            out[i] = re_.score(c, a, kind)
    if todo:
        verdicts = judge().many([(t[1], t[2], *t[4:]) for t in todo])
        for (i, _, _, inexact, *_), v in zip(todo, verdicts):
            out[i] = (0.95 ** inexact if v["verdict"] == "ok" else 0.0 if v["verdict"] == "wrong" else 0.5)
    return out


def strata(ty: str) -> list[str]:
    """The groups a prompt is reported in: its kind, kind x ablauting, and an inflection's number (the stage 1
    regression was the dual of non-ablauting stems), each with the valid split's "v." prefix."""
    v = "v." if ty.startswith("v.") else ""
    parts = ty.removeprefix("v.").split("|")
    out = [v + parts[0]]
    if len(parts) > 1:
        out.append(f"{v}{parts[0]}:{'abl' if parts[1].endswith(':abl') else 'non'}")
    if parts[0] == "inflect" and len(parts) > 2:
        out.append(f"{v}inflect:{'abl' if parts[1].endswith(':abl') else 'non'}:{parts[2]}")
    return out


@register_reward_function()
def pie_rl(prompts, completions, answer, types=None):
    types = types or ["inflect"] * len(answer)
    t = time.time()
    out = score_all(completions, answer, types)
    if os.environ.get("PIE_RL_REWARD_LOG"):          # per-stratum means for the dashboard
        by = {}
        for r, ty in zip(out, types):
            for k in strata(ty):
                by.setdefault(k, []).append(r)
        row = {"t": time.time(), "n": len(out), "judge_s": round(time.time() - t, 1),
               "judge_usd": round(_JUDGE.spent, 4) if _JUDGE else 0.0,
               **{f"reward/{k}": sum(v) / len(v) for k, v in by.items()}}
        with open(os.environ["PIE_RL_REWARD_LOG"], "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return out
