"""Phase 8b backtest: data, encoding, matched controls and metrics (no torch).

The model (scripts/run_backtest.py) maps a pre-Hittite cognate set to its
PIE target written the pre-laryngeal way (pie/prelaryngeal.py). This module
holds everything that must be testable without the model:

- `segments()`: the target as phoneme-sized units: a base character plus its
  combining marks and modifier letters (ḗ, dʰ, gʷʰ, r̥̄). The model predicts
  one unit per step, so every position is one decision.
- `effect_slots()`: maps the gold effects (NFC character offsets) onto unit
  indices. A loss effect points at the unit after the lost laryngeal, or at
  the end-of-word slot `len(segments)`.
- `stratum()`: the matching key for a slot. Exact strata (`exact`) are the
  same unit (base, length, accent) in the same word position (initial,
  medial, final, end); class strata (`class`) keep only vowel/consonant,
  length, accent and position. A control is a slot with no effect.
- `matched_contrast()`: stratified difference effect − control of a per-slot
  metric, with a cluster bootstrap over root families, overall and per
  effect kind.
- `FreqBaseline`: unigram and bigram unit models from training targets,
  giving the same per-slot metrics from target statistics alone.
- `hittite_slots()`: coarse alignment of a Hittite form to the target, to
  ask whether ḫ sits on slots the model flagged.
"""

from __future__ import annotations

import json
import math
import random
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

EOS = "</w>"
VOWELS = set("aeiouə")
MACRON, ACUTE, RING = "̄", "́", "̥"
KINDS = ("color", "length", "schwa", "loss")


# ---------------------------------------------------------------- data

def load(path: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text("utf-8").splitlines() if l.strip()]


def family(row: dict) -> str:
    """Bootstrap cluster: the root family, or the entry itself when it has no root."""
    return row.get("root_id") or row["id"]


def _attaches(ch: str) -> bool:
    return unicodedata.category(ch) in ("Mn", "Lm")


def segments(text: str) -> list[str]:
    """Units: a base character with its combining marks and modifier letters (each unit NFC)."""
    out: list[str] = []
    for ch in unicodedata.normalize("NFD", text):
        if out and _attaches(ch):
            out[-1] += ch
        else:
            out.append(ch)
    return [unicodedata.normalize("NFC", u) for u in out]


def _nfd(u: str) -> str:
    return unicodedata.normalize("NFD", u)


def offset_to_slot(text: str, offset: int) -> int:
    """Map a character offset in the (NFC) target to its unit index; len(text) → end slot."""
    k = -1
    for i, ch in enumerate(text):
        if not (_attaches(unicodedata.normalize("NFD", ch)[0]) and k >= 0):
            k += 1
        if i == offset:
            return k
    if offset == len(text):
        return k + 1
    raise ValueError(f"offset {offset} out of range for {text!r}")


def effect_slots(row: dict) -> dict[int, set[str]]:
    """slot index → set of effect kinds at that slot."""
    out: dict[int, set[str]] = defaultdict(set)
    for e in row["effects"]:
        out[offset_to_slot(row["target"], e["offset"])].add(e["kind"])
    return dict(out)


def is_vowel(unit: str) -> bool:
    d = _nfd(unit)
    return d[0] in VOWELS or RING in d


def position(i: int, n: int) -> str:
    if i >= n:
        return "end"
    return "initial" if i == 0 else "final" if i == n - 1 else "medial"


def stratum(units: list[str], i: int, level: str = "exact") -> tuple:
    """Matching key for slot i. `exact`: same unit and word position. `class`: vowel/consonant,
    length, accent and word position only."""
    pos = position(i, len(units))
    if i >= len(units):
        return (EOS, pos)
    u = units[i]
    if level == "exact":
        return (u, pos)
    d = _nfd(u)
    return ("V" if is_vowel(u) else "C", MACRON in d, ACUTE in d and is_vowel(u), pos)


# ---------------------------------------------------------------- input encoding

def language_order(rows: list[dict]) -> list[str]:
    """Fixed language order: by number of training sets, then name."""
    c = Counter(l for r in rows for l in r["inputs"])
    return sorted(c, key=lambda l: (-c[l], l))


def encode_inputs(inputs: dict[str, list[str]], order: list[str], max_forms: int = 2,
                  max_len: int = 120, rng: random.Random | None = None) -> list[tuple[str, str]]:
    """One sequence per set: for each language in the fixed order, a tag token then the NFD
    characters of up to `max_forms` forms, each form closed by a separator. Returns
    (symbol, language) pairs; tags are '<lang>' symbols. With `rng`, forms are sampled."""
    rank = {l: i for i, l in enumerate(order)}
    seq: list[tuple[str, str]] = []
    for lang in sorted(inputs, key=lambda l: (rank.get(l, len(rank)), l)):
        forms = list(inputs[lang])
        if rng is not None and len(forms) > max_forms:
            forms = rng.sample(forms, max_forms)
        piece = [("<lang>", lang)]
        for f in forms[:max_forms]:
            piece += [(ch, lang) for ch in unicodedata.normalize("NFD", f)] + [("<sep>", lang)]
        if len(seq) + len(piece) > max_len:
            break
        seq += piece
    return seq


def shuffle_inputs(rows: list[dict], seed: int = 0) -> list[dict]:
    """Baseline (a): daughter forms permuted across sets, targets kept."""
    rng = random.Random(seed)
    perm = list(range(len(rows)))
    rng.shuffle(perm)
    return [{**r, "inputs": rows[j]["inputs"]} for r, j in zip(rows, perm)]


# ---------------------------------------------------------------- per-slot metrics

def entropy(p: list[float]) -> float:
    return -sum(x * math.log(x) for x in p if x > 0)


@dataclass
class Word:
    """One evaluated target: its units and per-slot metrics (len(units)+1 slots incl. end)."""
    id: str
    family: str
    units: list[str]
    effects: dict[int, set[str]]
    metrics: dict[str, list[float]] = field(default_factory=dict)


def slot_metrics(dists: list[dict[str, float]], gold: list[str]) -> dict[str, list[float]]:
    """Per-slot error (argmax ≠ gold), entropy (nats) and surprisal (−log p gold) from
    teacher-forced distributions, one per slot (units then end)."""
    err, ent, sur = [], [], []
    for p, g in zip(dists, gold, strict=True):
        best = max(p, key=p.get)
        err.append(float(best != g))
        ent.append(entropy(list(p.values())))
        sur.append(-math.log(max(p.get(g, 0.0), 1e-12)))
    return {"error": err, "entropy": ent, "surprisal": sur}


class FreqBaseline:
    """Baseline (b): per-slot metrics from target unit frequencies alone (train targets).
    `order=1` is a unigram model; `order=2` conditions on the previous unit (BOS at start)."""

    def __init__(self, targets: list[str], order: int = 2, alpha: float = 0.1):
        self.order, self.alpha = order, alpha
        self.vocab = sorted({u for t in targets for u in segments(t)} | {EOS})
        self.uni: Counter = Counter()
        self.bi: dict[str, Counter] = defaultdict(Counter)
        for t in targets:
            us = segments(t) + [EOS]
            prev = "<s>"
            for u in us:
                self.uni[u] += 1
                self.bi[prev][u] += 1
                prev = u

    def dist(self, prev: str) -> dict[str, float]:
        V = len(self.vocab)
        n = sum(self.uni.values())
        uni = {u: (self.uni[u] + self.alpha) / (n + self.alpha * V) for u in self.vocab}
        if self.order == 1:
            return uni
        c = self.bi.get(prev, Counter())
        m = sum(c.values())
        lam = m / (m + 5.0)                 # Witten-Bell-like interpolation with the unigram
        return {u: lam * c[u] / max(m, 1) + (1 - lam) * uni[u] for u in self.vocab}

    def word_metrics(self, target: str) -> dict[str, list[float]]:
        us = segments(target) + [EOS]
        prevs = ["<s>"] + us[:-1]
        return slot_metrics([self.dist(p) for p in prevs], us)


# ---------------------------------------------------------------- matched contrast

def effect_entries(words: list[Word]) -> list[tuple[int, int, str]]:
    """(word index, slot, kind) for every gold effect; one slot may carry several kinds."""
    return [(wi, s, k) for wi, w in enumerate(words) for s, ks in sorted(w.effects.items()) for k in sorted(ks)]


MIN_CONTROL_FAMILIES = 3


def control_pools(words: list[Word], level: str, min_families: int = MIN_CONTROL_FAMILIES) -> dict[tuple, list[tuple[int, int]]]:
    """Non-effect slots by stratum. A stratum whose controls come from fewer than
    `min_families` root families is dropped: one stray control (kā́ps for medial ā́, átta for
    initial á) would otherwise stand in for dozens of effect slots."""
    pools: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
    for wi, w in enumerate(words):
        for s in range(len(w.units) + 1):
            if s not in w.effects:
                pools[stratum(w.units, s, level)].append((wi, s))
    return {k: v for k, v in pools.items() if len({words[wi].family for wi, _ in v}) >= min_families}


def match(words: list[Word], level: str = "exact", min_families: int = MIN_CONTROL_FAMILIES) -> list[dict]:
    """For each effect slot (any kind), its matched controls: same-word controls of the same
    stratum when there are any, else all controls of that stratum across words."""
    pools = control_pools(words, level, min_families)
    out = []
    for wi, w in enumerate(words):
        for s, kinds in sorted(w.effects.items()):
            key = stratum(w.units, s, level)
            pool = pools.get(key, [])
            same = [c for c in pool if c[0] == wi]
            ctl, where = (same, "word") if same else ([c for c in pool if c[0] != wi], "corpus")
            out.append({"word": wi, "slot": s, "kinds": sorted(kinds), "stratum": key,
                        "controls": ctl, "where": where if ctl else "none"})
    return out


def _value(words, wi, s, metric):
    return words[wi].metrics[metric][s]


def matched_contrast(words: list[Word], metric: str, level: str = "exact", kind: str | None = None,
                     n_boot: int = 2000, seed: int = 0, same_word_only: bool = False,
                     min_families: int = MIN_CONTROL_FAMILIES) -> dict:
    """Stratified contrast Σ_s w_s (mean_effect_s − mean_control_s), w_s ∝ effect slots in the
    stratum, over strata that have controls. Each effect slot is compared with the mean of
    its own matched controls (same word when possible), so the estimate is the mean of
    per-effect differences. CI: percentile cluster bootstrap over root families."""
    matched = match(words, level, min_families)
    m = [x for x in matched if x["controls"] and (kind is None or kind in x["kinds"])]
    if same_word_only:
        m = [x for x in m if x["where"] == "word"]
    all_eff = [x for x in matched if kind is None or kind in x["kinds"]]
    if not m:
        return {"n_effect": len(all_eff), "n_matched": 0, "diff": None, "ci": None}
    rows = []
    for x in m:
        e = _value(words, x["word"], x["slot"], metric)
        c = sum(_value(words, wi, s, metric) for wi, s in x["controls"]) / len(x["controls"])
        rows.append((words[x["word"]].family, e, c))
    def est(rs):
        return (sum(r[1] for r in rs) / len(rs), sum(r[2] for r in rs) / len(rs))
    me, mc = est(rows)
    by_fam: dict[str, list] = defaultdict(list)
    for r in rows:
        by_fam[r[0]].append(r)
    fams = sorted(by_fam)
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        rs = [r for f in rng.choices(fams, k=len(fams)) for r in by_fam[f]]
        a, b = est(rs)
        boots.append(a - b)
    boots.sort()
    lo, hi = boots[int(0.025 * n_boot)], boots[min(n_boot - 1, int(0.975 * n_boot))]
    p = 2 * min(sum(b <= 0 for b in boots), sum(b >= 0 for b in boots)) / n_boot
    return {"n_effect": len(all_eff), "n_matched": len(rows), "n_families": len(fams),
            "n_same_word": sum(x["where"] == "word" for x in m),
            "effect_mean": me, "control_mean": mc, "diff": me - mc, "ci": [lo, hi], "p_boot": min(1.0, p)}


def strata_table(words: list[Word], level: str = "exact") -> list[dict]:
    """Per-stratum effect and control counts (all non-effect slots, before the family rule)."""
    pools = control_pools(words, level, min_families=1)
    eff: Counter = Counter()
    kinds: dict[tuple, Counter] = defaultdict(Counter)
    for x in match(words, level, min_families=1):
        eff[x["stratum"]] += 1
        kinds[x["stratum"]].update(x["kinds"])
    out = []
    for k in sorted(eff, key=lambda k: -eff[k]):
        pool = pools.get(k, [])
        fams = len({words[wi].family for wi, _ in pool})
        out.append({"stratum": list(k), "effects": eff[k], "controls": len(pool), "control_families": fams,
                    "usable": fams >= MIN_CONTROL_FAMILIES, "kinds": dict(kinds[k])})
    return out


def all_contrasts(words: list[Word], metrics=("error", "entropy", "surprisal"), levels=("exact", "class"),
                  n_boot: int = 2000) -> dict:
    out = {}
    for level in levels:
        out[level] = {}
        for metric in metrics:
            if metric not in words[0].metrics:
                continue
            out[level][metric] = {"all": matched_contrast(words, metric, level, n_boot=n_boot),
                                  "same_word": matched_contrast(words, metric, level, n_boot=n_boot,
                                                                same_word_only=True)}
            for k in KINDS:
                out[level][metric][k] = matched_contrast(words, metric, level, kind=k, n_boot=n_boot)
    return out


def descriptive(words: list[Word], metric: str) -> dict:
    """Mean metric at effect slots per kind and at non-effect slots, unmatched."""
    by: dict[str, list[float]] = defaultdict(list)
    for w in words:
        for s in range(len(w.units) + 1):
            v = w.metrics[metric][s]
            ks = w.effects.get(s)
            if not ks:
                by["none"].append(v)
            else:
                by["any"].append(v)
                for k in ks:
                    by[k].append(v)
    return {k: {"n": len(v), "mean": sum(v) / len(v)} for k, v in sorted(by.items())}


# ---------------------------------------------------------------- Hittite

HIT_VOWELS = set("aeiu")


def hittite_clean(form: str) -> str | None:
    """Lower-case phonemic-ish string from a Hittite romanization: no hyphens, plene vowels
    collapsed, ḫ unified. Forms with logograms (upper case) are skipped."""
    f = unicodedata.normalize("NFD", form)
    if any(ch.isupper() for ch in f):
        return None
    f = "".join(ch for ch in f if not _attaches(ch) or ch == "̮")    # keep breve below of ḫ
    f = f.replace("ḫ", "H").replace("h", "H")
    s = "".join(ch for ch in f if ch.isalpha() or ch == "H")
    out = ""
    for ch in s:                                   # collapse doubled letters (plene, geminate)
        if not out or out[-1] != ch:
            out += ch
    return out or None


def _base(u: str) -> str:
    return _nfd(u)[0]


def align(target_units: list[str], hit: str) -> list[tuple[int | None, int | None]]:
    """Needleman-Wunsch alignment of target unit bases to Hittite characters.
    Returns (target index or None, hittite index or None) pairs."""
    a = [_base(u) for u in target_units]
    voice = {frozenset(p) for p in ("td", "kg", "pb")}

    def sub(x, y):
        if x == y:
            return 0.0
        if (x in VOWELS) and (y in HIT_VOWELS):
            return 0.4
        if x == "ə" and y == "H":
            return 0.3
        if frozenset((x, y)) in voice:
            return 0.2
        if (x not in VOWELS) and (y not in HIT_VOWELS) and y != "H":
            return 0.7
        return 1.0
    gap = 0.6
    n, m = len(a), len(hit)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        D[i][0], B[i][0] = i * gap, "u"
    for j in range(1, m + 1):
        D[0][j], B[0][j] = j * (0.3 if hit[j - 1] == "H" else gap), "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            g_h = 0.3 if hit[j - 1] == "H" else gap      # a Hittite ḫ with no target unit is cheap
            opts = [(D[i - 1][j - 1] + sub(a[i - 1], hit[j - 1]), "d"), (D[i - 1][j] + gap, "u"),
                    (D[i][j - 1] + g_h, "l")]
            D[i][j], B[i][j] = min(opts)
    i, j, path = n, m, []
    while i > 0 or j > 0:
        b = B[i][j]
        if b == "d":
            path.append((i - 1, j - 1)); i -= 1; j -= 1
        elif b == "u":
            path.append((i - 1, None)); i -= 1
        else:
            path.append((None, j - 1)); j -= 1
    return path[::-1]


def hittite_slots(target_units: list[str], hit: str) -> list[set[int]]:
    """For each ḫ in the cleaned Hittite form, the target slots it sits on: the aligned unit,
    or the two units around the gap where it was inserted (end slot = len(units))."""
    path = align(target_units, hit)
    out = []
    last_t = -1
    for k, (ti, hj) in enumerate(path):
        if ti is not None:
            last_t = ti
        if hj is not None and hit[hj] == "H":
            if ti is not None:
                out.append({ti})
            else:
                nxt = next((t for t, _ in path[k + 1:] if t is not None), len(target_units))
                out.append({s for s in (last_t, nxt) if s >= 0})
    return out


def stratum_breakdown(words: list[Word], metric: str, level: str = "exact", kind: str | None = None,
                      min_families: int = MIN_CONTROL_FAMILIES) -> list[dict]:
    """Per-stratum effect − control means of a metric (matched slots only), largest first."""
    by: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for x in match(words, level, min_families):
        if not x["controls"] or (kind is not None and kind not in x["kinds"]):
            continue
        e = words[x["word"]].metrics[metric][x["slot"]]
        c = sum(words[wi].metrics[metric][s] for wi, s in x["controls"]) / len(x["controls"])
        by[x["stratum"]].append((e, c))
    out = [{"stratum": list(k), "n": len(v), "effect_mean": sum(a for a, _ in v) / len(v),
            "control_mean": sum(b for _, b in v) / len(v)} for k, v in by.items()]
    for o in out:
        o["diff"] = o["effect_mean"] - o["control_mean"]
    return sorted(out, key=lambda o: -o["n"])


def decolor(unit: str) -> str:
    """The e-vowel a colored a/o would have been: same length and accent marks (ā́ → ḗ)."""
    d = _nfd(unit)
    if d[0] not in "ao":
        return unit
    return unicodedata.normalize("NFC", "e" + d[1:])


def confusions(words: list[Word], argmax: list[list[str]], kind: str, level: str = "exact",
               min_families: int = MIN_CONTROL_FAMILIES) -> dict:
    """At matched effect slots of `kind`, what the model predicted instead of the gold unit,
    against what it predicted at their matched controls (same gold unit). `argmax[w][s]` is
    the model's top unit at slot s of word w. Reports the share of decolored (e-vowel)
    predictions, the Saussure inference in its simplest form."""
    eff: Counter = Counter()
    ctl: Counter = Counter()
    n_e = n_c = dec_e = dec_c = 0
    for x in match(words, level, min_families):
        if not x["controls"] or kind not in x["kinds"]:
            continue
        g = words[x["word"]].units[x["slot"]] if x["slot"] < len(words[x["word"]].units) else EOS
        p = argmax[x["word"]][x["slot"]]
        eff[(g, p)] += 1
        n_e += 1
        dec_e += p != g and p == decolor(g) and decolor(g) != g
        w = 1.0 / len(x["controls"])
        for wi, s in x["controls"]:
            q = argmax[wi][s]
            ctl[(g, q)] += w
            n_c += w
            dec_c += w * (q != g and q == decolor(g) and decolor(g) != g)
    return {"n_effect": n_e, "decolored_share_effect": dec_e / n_e if n_e else None,
            "decolored_share_control": dec_c / n_c if n_c else None,
            "effect_top": [[g, p, n] for (g, p), n in eff.most_common(15)],
            "control_top": [[g, p, round(n, 2)] for (g, p), n in ctl.most_common(15)]}
