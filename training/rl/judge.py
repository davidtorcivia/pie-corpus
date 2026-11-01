"""The Claude meaning judge: one place for its brief, the engine analysis it reads, and the API call, shared by the
RL reward (training/rl/reward_rl.py) and the judge test (training/judge_test/api_judge.py).

Tiered (docs/research/judge-test-2026-10-31.md, round 3; owner 2026-11-01): Haiku 5.5 high screens one rollout per
call; a second Haiku high call re-checks only what the first flagged, and the item is wrong only if both say so.
Only rollouts the local checks cannot decide ever reach it (reward_rl.py).

Key: ANTHROPIC_API_KEY or ~/.config/anthropic/api_key; the org-level key needs ~/.config/anthropic/workspace_id.
"""
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CFG = Path.home() / ".config/anthropic"
MODEL, EFFORT = "claude-haiku-5-5", "high"
WORKERS = 6                   # the org's concurrent-request limit: 16 returned 429s (2026-11-01)
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

PIE_EN = """You are judging an English translation of Proto-Indo-European (PIE) from a reconstructed-PIE language project. You get the `pie`, the engine's `analysis` of every PIE word (lemma, English gloss, grammatical cell, all readings) with `senses`, a `reference` translation that is one good rendering, not the only one, and the candidate `english`.

Mark it **ok** if the English says what the PIE says: the same events and participants, who does what to whom, tense or mood (a PST/AOR form is past, an IMP a command, SBJV/OPT a wish or possibility), number and person, and negation, checked against the analysis. Free wording, word order, an English idiom ("there was a king" for "a king was") and a looser but faithful rendering are ok. Mark it **wrong** if it changes or drops any of those, adds content the PIE doesn't have, leaves PIE untranslated, or adds commentary.

Answer with only a JSON object: {"verdict": "ok" or "wrong", "word": the PIE word mistranslated or null, "reason": one short sentence}."""

DIALOGUE = """You are judging a reply in a conversation in Proto-Indo-European (PIE), from a reconstructed-PIE language project. The speaker is a person living in the PIE world. You get the `turn` the speaker answers (in English or PIE), the speaker's `reply` in PIE, the engine's `analysis` of every word of the reply (lemma, English gloss, grammatical cell, all readings) with `senses`, and a `reference` reply that is one good answer, not the only one.

Mark the reply **ok** if it is in PIE, a sensible, in-world answer to the turn (it answers what was asked or said, and doesn't contradict the turn), and grammatical: every form fits its role (case, number, person, tense and mood, agreement), checked against the analysis. Mark it **wrong** if it is not PIE (English, or commentary about the language), off-topic or nonsense, has a grammatical error or a word that isn't a real form, uses the wrong meaning of a word, or brings in modern things or talk about "Proto-Indo-European" as a reconstruction. A short reply is fine if it answers. Repeating the turn, or restating its question as a statement, is not an answer: mark it wrong. A question in reply is wrong unless the turn invites one. Spelling conventions (laryngeals h₁ h₂ h₃, accents, ḱ/kʷ) are the project's own; don't count notation as an error.

The analysis may miss a reading (an indeclinable, a rare form): don't mark a word wrong only because the analysis lacks the reading the sentence needs, if the form is plausibly that word.

This project's grammar (inherited rules, not errors):
- A neuter plural subject takes a singular verb (the old collective).
- Verbs of fearing take the ablative of what is feared.
- The project writes no augment, so a form the engine calls PST also serves as the injunctive: mḗ + injunctive is a prohibition ("do not go").
- The middle can change a verb's meaning (h₁áyt 'give', middle 'take, receive'); senses give it.

Answer with only a JSON object: {"verdict": "ok" or "wrong", "word": the PIE word at fault or null, "reason": one short sentence}."""

PUNCT = ".,;:?!\"“”'()"


def words(pie: str) -> list[str]:
    return [p for w in pie.split() for p in w.strip(PUNCT).split("-") if p]


def analysis(an, lx, pie: str) -> tuple[list[str], dict, list[tuple[str, str]]]:
    """(rows, senses, statuses): each word's readings grouped by lexeme (all of them: a homograph like ḱóymos
    'village' beside the adjective's gender readings is never cut off), every sense of each lemma that has more
    than one, and each word's lookup status (exact, unaccented, typed, close, unknown)."""
    rows, senses, status = [], {}, []
    for p in words(pie):
        res, how = an.word(p)
        status.append((p, how))
        groups = {}
        for a in res:
            groups.setdefault((a.lex_id, a.lemma, a.english), []).append(a.features)
        text = " | ".join(f"{lem} '{en}' {'/'.join(f for f in fs if f)}".rstrip() for (_, lem, en), fs in groups.items())
        rows.append(f"{p}: " + (text if res else "UNKNOWN") + ("" if how == "exact" or not res else f" ({how})"))
        for lid, lem, _ in groups:
            m = lx.entries.get(lid, {}).get("meaning")
            if m and len(m) + sum(";" in x for x in m) > 1:
                senses.setdefault(lem, "; ".join(m))
    return rows, senses, status


def client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY") or (CFG / "api_key").read_text().strip()
    ws = CFG / "workspace_id"
    headers = {"anthropic-workspace-id": ws.read_text().strip()} if ws.exists() else None
    return anthropic.Anthropic(api_key=key, default_headers=headers, max_retries=8)


def parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    try:
        v = json.loads(m[0]) if m else {}
    except json.JSONDecodeError:     # an unescaped quote in the reason: the verdict and word are still readable
        v = {k: (x[1] if x else None) for k, x in
             (("verdict", re.search(r'"verdict"\s*:\s*"(ok|wrong)"', text)), ("word", re.search(r'"word"\s*:\s*"([^"]*)"', text)))}
        v = {**v, "reason": text[:200]} if v["verdict"] else {}
    return v


def call(c, item: dict, model: str = MODEL, effort: str = EFFORT, system: str = SYSTEM) -> dict:
    """One judgment of {english, pie, analysis, senses} (or a dialogue's {turn, reply, analysis, senses,
    reference} with system=DIALOGUE): verdict ok / wrong / unparsed, with usage."""
    body = json.dumps({k: item[k] for k in ("english", "pie", "turn", "reply", "analysis", "senses", "reference")
                       if k in item}, ensure_ascii=False, indent=1)
    t = time.time()
    r = c.messages.create(model=model, max_tokens=16000, system=system, output_config={"effort": effort},
                          messages=[{"role": "user", "content": body}])
    v = parse("".join(b.text for b in r.content if b.type == "text"))
    pi, po = PRICE[model]
    return {"verdict": v.get("verdict", "unparsed"), "word": v.get("word"), "reason": v.get("reason", ""),
            "in": r.usage.input_tokens, "out": r.usage.output_tokens,
            "usd": (r.usage.input_tokens * pi + r.usage.output_tokens * po) / 1e6, "s": round(time.time() - t, 1)}


class Judge:
    """Tiered judging with a cache (identical english + pie is judged once per run) and a log of every call,
    for auditing what the policy was rewarded for."""

    def __init__(self, log: str | None = None):
        from pie.realize import Lexicon
        from pie.translator.analyze import Analyzer
        self.an, self.lx, self.c = Analyzer.load(), Lexicon.load(), client()
        self.cache: dict[tuple[str, str], dict] = {}
        self.log = open(log, "a", encoding="utf-8") if log else None
        self.lock = threading.Lock()
        self.spent = 0.0

    def _one(self, english: str, pie: str, dialogue: tuple | None = None) -> dict:
        """A translation pair (english, pie); with dialogue=(turn, reference) a dialogue reply `pie`; with
        dialogue=("pie_en", reference) a candidate English translation `english` of `pie`."""
        key = (english, pie, dialogue)
        if key in self.cache:
            return self.cache[key]
        rows, senses, _ = analysis(self.an, self.lx, pie)
        if dialogue and dialogue[0] == "pie_en":
            item = {"pie": pie, "analysis": rows, "senses": senses, "reference": dialogue[1], "english": english}
            sysm = PIE_EN
        elif dialogue:
            item = {"turn": dialogue[0], "reply": pie, "analysis": rows, "senses": senses, "reference": dialogue[1]}
            sysm = DIALOGUE
        else:
            item, sysm = {"english": english, "pie": pie, "analysis": rows, "senses": senses}, SYSTEM
        out = {"english": english, "pie": pie, **({"turn": dialogue[0]} if dialogue else {}), "t": time.time()}
        try:
            v = call(self.c, item, system=sysm)
            out["screen"] = v
            verdict = v["verdict"]
            if verdict != "ok":                       # flagged or unparsed: a second look decides
                v2 = call(self.c, item, system=sysm)
                out["confirm"] = v2
                verdict = "wrong" if v2["verdict"] != "ok" and verdict == "wrong" else \
                          "ok" if v2["verdict"] == "ok" else v2["verdict"]
            out["verdict"] = verdict
        except Exception as e:                        # the API failed: no verdict (reward_rl gives a neutral score)
            out["verdict"], out["error"] = "error", repr(e)[:300]
        usd = sum(out.get(k, {}).get("usd", 0) for k in ("screen", "confirm"))
        with self.lock:
            self.spent += usd
            if out["verdict"] != "error":
                self.cache[key] = out
            if self.log:
                self.log.write(json.dumps(out, ensure_ascii=False) + "\n")
                self.log.flush()
        return out

    def many(self, pairs: list[tuple]) -> list[dict]:
        """Judge (english, pie) pairs, or (english, pie, (turn, reference)) dialogue replies, in parallel."""
        uniq = list(dict.fromkeys(pairs))
        with ThreadPoolExecutor(WORKERS) as ex:
            got = dict(zip(uniq, ex.map(lambda p: self._one(*p), uniq)))
        return [got[p] for p in pairs]
