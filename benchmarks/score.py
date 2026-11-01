"""Score benchmark contestants (benchmarks/README.md): inflection and paradigm by the key, strict and lenient; the
judged segments (EN→PIE, PIE→EN, dialogue) from the judges' verdict files once they exist.

    uv run python -I benchmarks/score.py [CONTESTANT ...]   # default: every benchmarks/results/*/answers.jsonl

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
JUDGES = 2                    # an item counts once both judges (Opus, GPT) have graded it

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


ALIAS = {"INST": "INS", "INSTR": "INS", "INSTRUMENTAL": "INS", "NOMINATIVE": "NOM", "ACCUSATIVE": "ACC",
         "GENITIVE": "GEN", "DATIVE": "DAT", "ABLATIVE": "ABL", "LOCATIVE": "LOC", "VOCATIVE": "VOC",
         "SINGULAR": "SG", "PLURAL": "PL", "DUAL": "DU", "MASC": "M", "FEM": "F", "NEUT": "N", "MASCULINE": "M",
         "FEMININE": "F", "NEUTER": "N", "PRESENT": "PRS", "AORIST": "AOR", "PERFECT": "PRF", "IMPERFECT": "IMPF",
         "IMPERATIVE": "IMP", "SUBJUNCTIVE": "SBJV", "OPTATIVE": "OPT", "MIDDLE": "MID", "MEDIOPASSIVE": "MID",
         "ACTIVE": "ACT", "INDICATIVE": "IND", "PAST": "PST", "FUTURE": "FUT", "FIRST": "1", "SECOND": "2",
         "THIRD": "3", "1ST": "1", "2ND": "2", "3RD": "3"}
LABEL_WORD = re.compile(r"(NOM|VOC|ACC|GEN|ABL|DAT|LOC|INS|SG|DU|PL|M|F|N|[123](SG|DU|PL)?|[123](ST|ND|RD)|PRS|AOR|PRF|"
                        r"IMPF|PST|MID|ACT|IMP|SBJV|OPT|FUT|PTCP|PERF|PRES|IND|INJ)")
BLOCK = {"PRES": "PRS", "PERF": "PRF"}


def label(raw: str) -> str:
    parts = [BLOCK.get(ALIAS.get(p, p), ALIAS.get(p, p)) for p in re.split(r"[.\s]+", raw.upper()) if p]
    out = []
    for p in parts:                                   # "1 SG" or "1ST SG" -> 1SG
        if out and re.fullmatch(r"SG|DU|PL", p) and re.fullmatch(r"[123](ST|ND|RD)?", out[-1]):
            out[-1] = out[-1][0] + p
        else:
            out.append(p)
    return ".".join(out)


CASES = {"NOM", "VOC", "ACC", "GEN", "ABL", "DAT", "LOC", "INS"}
NUMS = {"SG", "DU", "PL"}
GENDERS = {"M", "F", "N"}
BLOCKS = {"PRS", "AOR", "PRF", "IMPF", "PST", "MID", "ACT", "IMP", "SBJV", "OPT", "FUT", "IND", "INJ"}


def _word(t: str) -> str:
    w = t.strip(".()[]").upper()
    return BLOCK.get(ALIAS.get(w, w), ALIAS.get(w, w))


def grid_rows(text: str) -> str:
    """A markdown grid ("| Case | Singular | Dual | Plural |" then "| Nominative | x | y | z |") as one line per
    cell, "Nominative Singular x", which the scanner reads like any other row."""
    lines, header, out, slash = text.splitlines(), None, [], None
    for line in lines:
        parts = [x.strip() for x in line.split("/")]
        if len(parts) > 1 and all(ALIAS.get(x.upper(), x.upper()) in ("SG", "DU", "PL") for x in parts):
            slash = parts                              # "Singular / dual / plural", then "Nominative: x / y / z"
            continue
        if slash and ":" in line and len(line.split(":", 1)[1].split("/")) == len(slash):
            lab, forms = line.split(":", 1)
            out += [f"{lab} {n} {f.strip()}" for n, f in zip(slash, forms.split("/"))]
            continue
        if line.count("|") < 2 and not line.strip().startswith("|"):     # a grid row, with or without edge pipes
            header = None
            out.append(line)
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cols if c):
            continue
        if header is None:
            header = cols
            continue
        for h, c in zip(header[1:], cols[1:]):
            for form in re.split(r"\s*[/,~]\s*|\s+or\s+", c)[:1]:
                out.append(f"{cols[0]} {h} {form}")
    return "\n".join(out)


def cells(text: str) -> dict:
    """A paradigm answer's cells, whatever its layout: rows ("NOM.SG: x", "nom.sg. *x", "- **Masc. nom. sg.**: x",
    "1sg x"), inline lists under a header ("Singular: nom. x; acc. y"), and shared rows ("nom/acc sg x"). A
    scanner: grammatical words (case, number, gender, person, tense block; "/" joins alternatives) build a label,
    the next other word is its form; a number, gender or block given alone is a header that carries on."""
    out = {}
    text = grid_rows(text)
    ctx = {"num": None, "gender": None, "block": []}
    cases, persons, num, gender, block, lead, lead_g, lead_b = [], [], None, None, [], False, False, False
    text = text.replace("*", " ").replace("•", " ")
    for t in re.findall(r"[^\s;,:|=–]+", text):
        subs = [_word(x) for x in re.split(r"[/.]", t) if x.strip(".()")]
        if subs and all(x in CASES or x in NUMS or x in GENDERS or x in BLOCKS or re.fullmatch(r"[123](SG|DU|PL)?|[123](ST|ND|RD)", x)
                        for x in subs):
            for x in subs:
                if x in CASES:
                    cases.append(x)
                elif x in NUMS:
                    if not cases and not persons:
                        lead = True               # a number before any case: a header, if a form follows later
                    if persons and re.fullmatch(r"[123](ST|ND|RD)?", persons[-1]):
                        persons[-1] = persons[-1][0] + x
                    else:
                        num = x
                elif x in GENDERS:
                    lead_g = lead_g or not cases and not persons
                    gender = x
                elif x in BLOCKS:
                    lead_b = lead_b or not cases and not persons
                    if x not in ("ACT", "IND"):     # the key writes the active indicative unmarked
                        block.append(x)
                else:
                    persons.append(x)
            continue
        if not any(c.isalpha() for c in t):
            continue
        form = t.strip(",;.")
        if cases or persons:
            n, g, bl = num or ctx["num"], gender or ctx["gender"], block or ctx["block"]
            for c in cases:
                out.setdefault(".".join([*([g] if g else []), *bl, c, *([n] if n else [])]), form)
            for pr in persons:                     # "du 1 x" / "Dual: 1 x": a bare person takes the number
                pr = pr + n if re.fullmatch(r"[123]", pr) and n else pr
                out.setdefault(".".join([*bl, pr]), form)
        else:                                          # a header ("Singular", "Masculine", "Present") then prose
            pass
        if num:                                    # a number carries on to the rows after it
            ctx["num"] = num
        if gender and (lead_g or not cases and not persons):
            ctx["gender"] = gender
        if block and (lead_b or not cases and not persons):
            ctx["block"] = block
        cases, persons, num, gender, block, lead, lead_g, lead_b = [], [], None, None, [], False, False, False
    return out


def lookup(got: dict, cell: str, ref: dict) -> str:
    """The answer's form for a reference cell: the same label, or a label the cell ends with when no other
    reference cell does (a verb block's '1SG' for 'PRS.1SG', an adjective's 'NOM.SG' when one gender was asked)."""
    if cell in got:
        return got[cell]
    for lab, form in got.items():                     # the answer's label is shorter: '1SG' for 'PRS.1SG'
        if cell.endswith("." + lab) and sum(c.endswith("." + lab) or c == lab for c in ref) == 1:
            return form
    for lab, form in got.items():                     # or longer: 'N.NOM.SG' for 'NOM.SG' in a one-gender table
        if lab.endswith("." + cell) and sum(lab.endswith("." + c) for c in ref) == 1:
            return form
    return ""


def score_item(k: dict, answer: str) -> dict:
    if k["segment"] == "inflection":
        a = answer.strip().split("\n")[0]
        return {"strict": float(strict(a) == strict(k["reference"])), "lenient": float(lenient(a) == lenient(k["reference"]))}
    if k["segment"] == "paradigm":
        ref = {label(c): f for c, f in (r.split(": ", 1) for r in k["reference"].splitlines() if ": " in r)}
        got = cells(answer)
        return {"strict": sum(strict(lookup(got, c, ref)) == strict(v) for c, v in ref.items()) / len(ref),
                "lenient": sum(lenient(lookup(got, c, ref)) == lenient(v) for c, v in ref.items()) / len(ref)}
    return {}


_AN = None


def notation_ok(text: str) -> bool:
    """Strict notation for a PIE answer: every word is a form the project's engine knows, exactly or but for an
    accent (pie.translator.analyze), so a mainstream spelling the project writes differently fails strict only."""
    global _AN
    if _AN is None:
        sys.path.insert(0, str(HERE.parent))
        from pie.translator.analyze import Analyzer
        _AN = Analyzer.load()
    ws = [p for w in text.split() for p in w.strip(".,;:?!\"“”'()«»").split("-") if p]
    return bool(ws) and all(_AN.word(w)[1] in ("exact", "unaccented") for w in ws)


def judged(contestant: str, key: dict, answers: dict) -> dict:
    """Per item: the mean of the judges' scores (results/<c>/judge-<judge>.jsonl), lenient; strict also needs the
    PIE in the project's notation (notation_ok) where the answer is PIE (EN→PIE, dialogue)."""
    sys.path.insert(0, str(HERE))
    from judge_packets import part
    out = {}
    for f in sorted((HERE / "results" / contestant).glob("judge-*.jsonl")):
        for r in map(json.loads, f.read_text("utf-8").splitlines()):
            out.setdefault(r["id"], []).append(r)
    res = {}
    for i, rs in out.items():
        m = sum(r["score"] for r in rs) / len(rs)
        pie = key[i]["segment"] != "pie_en"
        ok = notation_ok(part(key[i]["kind"], answers.get(i, ""))) if pie else True
        res[i] = {"strict": m * ok, "lenient": m, "judges": len(rs), "notation_ok": ok}
    return res


def score(contestant: str) -> dict:
    key = {x["id"]: x for x in map(json.loads, (HERE / "key.jsonl").read_text("utf-8").splitlines())}
    ans = {}
    for r in map(json.loads, (HERE / "results" / contestant / "answers.jsonl").read_text("utf-8").splitlines()):
        ans.setdefault(r["id"], r["answer"])
    jd = judged(contestant, key, ans)
    items = {}
    for i, k in key.items():
        if k["segment"] in JUDGED:
            if i in jd and jd[i]["judges"] >= JUDGES:
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
    summary = [{k: v for k, v in json.loads(p.read_text("utf-8")).items() if k != "items"}     # every contestant
               for p in sorted((HERE / "results").glob("*/scores.json"))]
    (HERE / "results" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
