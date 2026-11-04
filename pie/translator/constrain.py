"""Engine-constrained decoding: the language model may write only PIE words the engine knows.

At each decoding step the processor walks the model's top candidates in order and keeps the first whose text keeps
every PIE word a form of the analyzer's index (pie.translator.analyze), or a prefix of one while the word is still
being written. That is benchmarks/score.py's strict notation rule (notation_ok: a known form, exactly or but for an
accent; enclitics after a hyphen checked on their own), applied while writing instead of after: what the grammar
accepts always passes notation_ok.

Which text is PIE: every line, except a line that starts with a label other than "PIE:" (English:, Gloss:,
Notes:), which is free; the text after "PIE:" is PIE. A line still short enough to become a label is free.
The caller enables the processor only for prompts whose answer is PIE (EN→PIE, dialogue).

    from pie.translator.constrain import Grammar, Constraint
    proc = Constraint(tokenizer, Grammar.load(), prompt_len)      # mlx_lm generate_step(logits_processors=[proc])

Greedy only: the step's logits are masked to the one token chosen. If none of the top `topk` candidates fits, the
step is left unconstrained and counted (proc.fallbacks), so a result reports how often the grammar gave way.
"""
from __future__ import annotations

import bisect
import functools
import re

from .analyze import Analyzer, nfc, unaccented

# stripped from both ends of a word, as score.notation_ok and Analyzer.word do
PUNCT = set(".,;:!?\"“”'‘’()[]«»…")
LABELS = ("PIE", "English", "Gloss", "Notes", "Note", "Translation", "Literal")
_LABEL = re.compile(r"^\s*(%s)\s*:" % "|".join(LABELS))


class Grammar:
    """Word and prefix membership over the analyzer's forms, compared without accents (notation_ok's leniency)."""

    def __init__(self, forms):
        self.keys = sorted({unaccented(nfc(f)) for f in forms})
        self._set = set(self.keys)

    @classmethod
    @functools.lru_cache(maxsize=1)
    def load(cls) -> "Grammar":
        a = Analyzer.load()
        return cls(list(a.index) + list(a.loose))

    def word(self, w: str) -> bool:
        return unaccented(nfc(w)) in self._set

    def prefix(self, p: str) -> bool:
        if not p:
            return True
        p = unaccented(nfc(p))
        i = bisect.bisect_left(self.keys, p)
        return i < len(self.keys) and self.keys[i].startswith(p)

    def token(self, t: str, complete: bool) -> bool:
        """One whitespace-separated token: leading/trailing punctuation, then words joined by hyphens. While the
        token is still being written (not complete, no trailing punctuation yet) its last part need only be a
        prefix of a form."""
        i, j = 0, len(t)
        while i < j and t[i] in PUNCT:
            i += 1
        k = j
        while k > i and t[k - 1] in PUNCT:
            k -= 1
        core = t[i:k]
        if any(c in PUNCT for c in core):
            return False
        if not core:
            return True
        done = complete or k < j
        parts = core.split("-")
        if done:
            return all(self.word(p) for p in parts if p)
        return all(self.word(p) for p in parts[:-1] if p) and self.prefix(parts[-1])

    def pie_text(self, s: str, complete: bool) -> bool:
        """A run of PIE text; complete: the text ends here (end of line or answer), so its last word must be whole."""
        toks = s.split()
        if not toks:
            return True
        last_open = not complete and not s[-1].isspace()
        return (all(self.token(t, True) for t in toks[:-1])
                and self.token(toks[-1], not last_open))

    def line(self, s: str, complete: bool) -> bool:
        m = _LABEL.match(s)
        if m:
            return m[1] != "PIE" or self.pie_text(s[m.end():], complete)
        if not complete and any(lab.startswith(s.lstrip()) for lab in LABELS) and s.strip():
            return True                       # may still become a label
        return self.pie_text(s, complete)

    def text(self, s: str, complete: bool = False) -> bool:
        """An answer (or its tail from a line start): every line by line(); lines before the last are complete."""
        lines = s.split("\n")
        return all(self.line(x, True) for x in lines[:-1]) and self.line(lines[-1], complete)


class Constraint:
    """mlx_lm logits processor (tokens, logits) -> logits, for one prompt of prompt_len tokens."""

    def __init__(self, tokenizer, grammar: Grammar, prompt_len: int, topk: int = 64):
        self.tok, self.g, self.n, self.topk = tokenizer, grammar, prompt_len, topk
        self.eos = set(getattr(tokenizer, "eos_token_ids", None) or [tokenizer.eos_token_id])
        self.fallbacks = 0
        self.steps = 0

    def _ok(self, gen: list[int], prev: str, cand: int) -> bool:
        if cand in self.eos:
            return self.g.text(prev[prev.rfind("\n") + 1:], complete=True)
        new = self.tok.decode(gen + [cand])
        # a multi-byte letter (h₁, ḱ, ʷ) can take two tokens: check what is decoded so far
        new = new.rstrip("�")
        start = prev.rfind("\n") + 1
        if not new.startswith(prev[:start]):
            start = 0
        return self.g.text(new[start:], complete=False)

    def choose(self, gen: list[int], order) -> int | None:
        prev = self.tok.decode(gen).rstrip("�") if gen else ""
        for c in order[:self.topk]:
            if self._ok(gen, prev, int(c)):
                return int(c)
        return None

    def __call__(self, tokens, logits):
        import mlx.core as mx
        import numpy as np
        self.steps += 1
        gen = [int(x) for x in np.array(tokens[self.n:])] if tokens is not None and len(tokens) > self.n else []
        row = np.array(logits[0].astype(mx.float32))
        order = np.argsort(-row)
        c = self.choose(gen, order)
        if c is None:
            self.fallbacks += 1
            return logits
        mask = np.full(row.shape, -np.inf, dtype=np.float32)
        mask[c] = 0.0
        return logits + mx.array(mask)[None].astype(logits.dtype)
