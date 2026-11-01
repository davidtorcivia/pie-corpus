"""Score benchmark contestants (benchmarks/README.md): inflection and paradigm by the key, strict and lenient; the
judged segments (EN→PIE, PIE→EN, dialogue) from the judges' verdict files once they exist.

    python3 -I benchmarks/score.py [CONTESTANT ...]      # default: every benchmarks/results/*/answers.jsonl

Writes results/<contestant>/scores.json and results/summary.json.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEIGHTS = {"inflection": 20, "paradigm": 15, "en_pie": 30, "pie_en": 20, "dialogue": 15}
JUDGED = ("en_pie", "pie_en", "dialogue")

ASCII = [("gwh", "gʷʰ"), ("kwh", "kʷʰ"), ("bh", "bʰ"), ("dh", "dʰ"), ("gh", "gʰ"), ("kw", "kʷ"), ("gw", "gʷ"),
         ("k'", "ḱ"), ("g'", "ǵ"), ("h1", "h₁"), ("h2", "h₂"), ("h3", "h₃"), ("ʷ", "ʷ")]
PALATAL = {"ḱ": "\0K", "ǵ": "\0G"}


def strict(s: str) -> str:
    s = unicodedata.normalize("NFC", s.strip())
    return s.strip(" *.,;:!?\"'“”").strip()


def lenient(s: str) -> str:
    """Notation forgiven, phonology kept: ASCII spellings mapped, accents and vowel length dropped, case ignored;
    the palatals ḱ ǵ (written with a combining acute) stay distinct from k g."""
    s = strict(s).lower().replace("*", "")
    for a, b in ASCII:
        s = s.replace(a, b)
    s = unicodedata.normalize("NFC", s)
    for a, b in PALATAL.items():
        s = s.replace(a, b)
    s = "".join(c for c in unicodedata.normalize("NFD", s) if c not in "́̀̄̆̂")
    s = unicodedata.normalize("NFC", s)
    for a, b in PALATAL.items():
        s = s.replace(b, a)
    return " ".join(s.split())


def cells(text: str) -> dict:
    return {m[1]: m[2] for m in re.finditer(r"([A-Z][A-Z0-9.]+)\s*:\s*\*?([^\s,;]+)", text)}


def score_item(k: dict, answer: str) -> dict:
    if k["segment"] == "inflection":
        a = answer.strip().split("\n")[0]
        return {"strict": float(strict(a) == strict(k["reference"])), "lenient": float(lenient(a) == lenient(k["reference"]))}
    if k["segment"] == "paradigm":
        ref, got = cells(k["reference"]), cells(answer)
        return {"strict": sum(strict(got.get(c, "")) == strict(v) for c, v in ref.items()) / len(ref),
                "lenient": sum(lenient(got.get(c, "")) == lenient(v) for c, v in ref.items()) / len(ref)}
    return {}


def judged(contestant: str) -> dict:
    """Mean of the judges' verdicts per item: results/<c>/judge-<judge>.jsonl rows {id, score, notation_ok}."""
    out = {}
    for f in sorted((HERE / "results" / contestant).glob("judge-*.jsonl")):
        for r in map(json.loads, f.read_text("utf-8").splitlines()):
            out.setdefault(r["id"], []).append(r)
    return {i: {"strict": sum(r["score"] * bool(r.get("notation_ok")) for r in rs) / len(rs),
                "lenient": sum(r["score"] for r in rs) / len(rs), "judges": len(rs)} for i, rs in out.items()}


def score(contestant: str) -> dict:
    key = {x["id"]: x for x in map(json.loads, (HERE / "key.jsonl").read_text("utf-8").splitlines())}
    ans = {}
    for r in map(json.loads, (HERE / "results" / contestant / "answers.jsonl").read_text("utf-8").splitlines()):
        ans.setdefault(r["id"], r["answer"])
    jd = judged(contestant)
    items = {}
    for i, k in key.items():
        if k["segment"] in JUDGED:
            if i in jd:
                items[i] = {"segment": k["segment"], **jd[i]}
        elif i in ans:
            items[i] = {"segment": k["segment"], **score_item(k, ans[i])}
    seg = {}
    for s in WEIGHTS:
        xs = [v for v in items.values() if v["segment"] == s]
        n = sum(k["segment"] == s for k in key.values())
        seg[s] = {"n": len(xs), "of": n, **({m: round(100 * sum(x[m] for x in xs) / n, 1) for m in ("strict", "lenient")}
                                            if len(xs) == n else {})}
    complete = all("strict" in v for v in seg.values())
    total = {m: round(sum(WEIGHTS[s] * seg[s][m] for s in WEIGHTS) / sum(WEIGHTS.values()), 1)
             for m in ("strict", "lenient")} if complete else None
    return {"contestant": contestant, "segments": seg, "pie_score": total, "items": items}


def main():
    names = sys.argv[1:] or sorted(p.parent.name for p in (HERE / "results").glob("*/answers.jsonl"))
    summary = []
    for c in names:
        s = score(c)
        (HERE / "results" / c / "scores.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), "utf-8")
        summary.append({k: s[k] for k in ("contestant", "segments", "pie_score")})
        print(c, json.dumps({k: (v.get("strict"), v.get("lenient"), f"{v['n']}/{v['of']}") for k, v in s["segments"].items()}),
              s["pie_score"])
    (HERE / "results" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
