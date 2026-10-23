"""Write a laryngealist form the way pre-laryngeal handbooks did (Brugmann).

Phase 8b's backtest trains on the evidence as it stood before the
laryngeal theory, so its PIE targets must look like Brugmann's, not like
forms with the laryngeals simply deleted. The laryngeals' effects stay
visible as long vowels, a-/o-coloring and schwa, which is exactly what
Saussure found suspicious:

  coloring    h₂e eh₂ → a,  h₃e eh₃ → o         (h₂eǵ- → aǵ-)
  length      VH before C or # → V̄              (dʰeh₁- → dʰē-, steh₂- → stā-, bʰuH- → bʰū-)
              R̥H → R̥̄                           (ǵr̥h₂nóm → ǵr̥̄nóm)
  schwa       CHC, CH# → CəC                     (ph₂tḗr → pətḗr, dʰugh₂tḗr → dʰugətḗr)
  loss        #H, HV → ∅                         (h₁ésti → ésti, h₂ówis → ówis)

`convert()` returns the string and the list of effects, each with its
output character offset: the gold positions the backtest scores against.
The output is a research representation, not canonical PIE (ə is outside
the inventory).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .phon import Seg, parse, render

LAR = {"h1", "h2", "h3", "H"}
COLOR = {"h2": "a", "h3": "o"}


@dataclass
class Effect:
    kind: str          # color | length | schwa | loss
    laryngeal: str     # h1 h2 h3 H
    offset: int        # character offset in the output string (for loss: where it was)


def convert(form: str) -> tuple[str, list[Effect]]:
    segs = parse(form.strip("-"))
    effects: list[tuple[str, str, int]] = []   # (kind, laryngeal, segment index in `out`)
    # 1. coloring: e next to h₂/h₃
    segs = list(segs)
    colored = set()
    for i, s in enumerate(segs):
        if s.kind == "V" and s.base == "e" and not s.syl:
            for j in (i - 1, i + 1):
                if 0 <= j < len(segs) and segs[j].base in COLOR:
                    segs[i] = replace(s, base=COLOR[segs[j].base])
                    colored.add((i, segs[j].base))
                    break
    # 2. laryngeals: length, schwa, loss
    out: list = []
    color_at = {}
    for i, s in enumerate(segs):
        if s.base not in LAR:
            if any(ci == i for ci, _ in colored):
                color_at[len(out)] = next(lb for ci, lb in colored if ci == i)
            out.append(s)
            continue
        prev = out[-1] if out else None
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        next_vowel = nxt is not None and (nxt.kind == "V" and not nxt.syl)
        if isinstance(prev, Seg) and (prev.kind == "V" or prev.syl) and not next_vowel:
            out[-1] = replace(prev, long=True)
            effects.append(("length", s.base, len(out) - 1))
        elif prev is None or next_vowel:
            effects.append(("loss", s.base, len(out)))
        else:
            out.append("ə")
            effects.append(("schwa", s.base, len(out) - 1))
    for k, lb in color_at.items():
        effects.append(("color", lb, k))
    # render, tracking each segment's character offset
    text, offsets = "", []
    for x in out:
        offsets.append(len(text))
        text += x if isinstance(x, str) else render([x])
    offsets.append(len(text))
    return text, sorted((Effect(k, lb, offsets[i]) for k, lb, i in effects), key=lambda e: e.offset)
