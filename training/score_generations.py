"""Score a run's per-epoch generations (training/train_lora.py writes them) on the Mac, where the PIE tools live.

    uv run python -I training/score_generations.py RUN_DIR/generations-e1.jsonl [...]     # writes scores-e1.json

Per item, by kind:
- chrF (character 6-gram F-score, beta 2) of the output's PIE against the reference's PIE: every kind whose
  reference is PIE (translations to PIE, dialogue replies, continuations, inflection, paradigms, cognates);
- exact match: inflect and cognates_to_pie;
- recognized: the share of the output's PIE words the reverse form index knows (pie.translator.analyze, exact or
  unaccented match), i.e. real forms the engine can build, a grammaticality check the loss can't give;
- modern: the output mentions something the persona must not (machine, computer, AI, ...);
- cells: for a paradigm, the share of the reference's cells the output gives exactly;
- by stem class (prompts that carry a source_id, as training/gen_prompts_v1.jsonl's do): inflect exact and
  paradigm cells per class, the class being the lexicon spec's rule (thematic, n-stem, root aorist, ...), and
  ablauting vs not (the spec has a weak stem).
cognates_to_pie is never in the training mix (a speaker doesn't know the daughter languages), so it is scored
under "untrained" and kept out of the summary. The summary is per kind and overall; scores-eN.json sits next to
the generations, and the dashboard shows it.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pie.translator.analyze import Analyzer  # noqa: E402

MODERN = re.compile(r"\b(machine|computer|artificial|AI|language model|program|robot|internet|phone|assistant)\b", re.I)
ENGLISH_OUT = ("translate_pie_en", "translate_app/pie_en", "gloss")


def pie_part(text: str) -> str:
    """The PIE of an output: after 'PIE:' when present, before 'English:' / 'Gloss:' / 'Notes:'."""
    t = text.split("PIE:", 1)[-1]
    return re.split(r"\n?(English|Gloss|Notes):", t)[0].strip()


def chrf(hyp: str, ref: str, n: int = 6, beta: float = 2.0) -> float:
    hyp, ref = re.sub(r"\s+", " ", hyp.strip()), re.sub(r"\s+", " ", ref.strip())
    if not hyp or not ref:
        return 0.0
    ps, rs = [], []
    for k in range(1, n + 1):
        h = Counter(hyp[i:i + k] for i in range(len(hyp) - k + 1))
        r = Counter(ref[i:i + k] for i in range(len(ref) - k + 1))
        m = sum((h & r).values())
        if h:
            ps.append(m / sum(h.values()))
        if r:
            rs.append(m / sum(r.values()))
    p, r = (sum(ps) / len(ps) if ps else 0), (sum(rs) / len(rs) if rs else 0)
    return 0.0 if p + r == 0 else round(100 * (1 + beta**2) * p * r / (beta**2 * p + r), 1)


UNTRAINED = ("cognates_to_pie",)


def cells(text: str) -> dict:
    return dict(m.groups() for m in re.finditer(r"([A-Z][A-Z0-9.]+):\s*(\S+)", text))


def stem_class(lx, lid: str | None) -> tuple[str, bool] | None:
    s = lx.specs.get(lid) if lid else None
    if not s:
        return None
    sp = s["spec"]
    rule = s["rule"].split(":", 1)[-1]
    if rule in ("table", "project", "noun-shape", "verb-shape", "adj-shape"):
        rule = f"{s['family']}-{sp.get('accent_class') or 'table'}"
    return rule, bool(sp.get("weak") or sp.get("m_weak"))


def score(path: Path) -> dict:
    from pie.realize import Lexicon
    an = Analyzer.load()
    lx = Lexicon.load()
    by_class = defaultdict(lambda: defaultdict(list))
    rows = [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip()]
    per = defaultdict(lambda: defaultdict(list))
    items = []
    for g in rows:
        k, out, ref = g["kind"], g["output"], g["reference"]
        s = {"kind": k, "id": g.get("id")}
        if k not in ENGLISH_OUT:
            o, r = pie_part(out), pie_part(ref)
            s["chrf"] = chrf(o, r)
            words = [w for w in re.findall(r"[^\s.,;:!?\"“”()]+", o) if not re.fullmatch(r"[A-Za-z]+", w)]
            if words:
                s["recognized"] = round(sum(an.word(w)[1] in ("exact", "unaccented") for w in words) / len(words), 3)
            if k in ("inflect", "cognates_to_pie"):
                s["exact"] = float(o.strip(" *.") == r.strip(" *."))
            if k == "paradigm":
                rc, oc = cells(ref), cells(out)
                if rc:
                    s["cells"] = round(sum(oc.get(c) == f for c, f in rc.items()) / len(rc), 3)
            sc = stem_class(lx, g.get("source_id"))
            if sc and k in ("inflect", "paradigm"):
                m = "exact" if k == "inflect" else "cells"
                if m in s:
                    for cls in (f"{k}:{sc[0]}", f"{k}:{'ablauting' if sc[1] else 'non-ablauting'}"):
                        by_class[cls][m].append(s[m])
        else:
            s["chrf"] = chrf(out.split("Gloss:")[0], ref.split("Gloss:")[0])
        s["modern"] = bool(MODERN.search(out))
        items.append(s)
        for m in ("chrf", "recognized", "exact", "modern", "cells"):
            if m in s:
                per[k][m].append(float(s[m]))
                if k not in UNTRAINED:
                    per["ALL"][m].append(float(s[m]))
    mean = lambda xs: round(sum(xs) / len(xs), 3) if xs else None
    by_kind = {k: {m: mean(v) for m, v in d.items()} | {"n": len(d["chrf"])} for k, d in per.items()}
    allk = by_kind["ALL"]
    summary = {"chrF": allk.get("chrf"), "recognized": allk.get("recognized"), "exact": allk.get("exact"),
               "paradigm_cells": allk.get("cells"), "modern": allk.get("modern")}
    classes = {c: {m: mean(v) for m, v in d.items()} | {"n": sum(len(v) for v in d.values())}
               for c, d in sorted(by_class.items())}
    return {"summary": summary, "by_kind": by_kind, "by_class": classes,
            "untrained": {k: by_kind[k] for k in UNTRAINED if k in by_kind}, "items": items}


def main():
    for p in sys.argv[1:]:
        p = Path(p)
        res = score(p)
        out = p.with_name(p.name.replace("generations-", "scores-").replace(".jsonl", ".json"))
        out.write_text(json.dumps(res, ensure_ascii=False, indent=1), "utf-8")
        print(p.parent.name, p.stem, json.dumps(res["summary"]))


if __name__ == "__main__":
    main()
