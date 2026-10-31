"""Engine tools for the PIE judges.

    analyze "<PIE text>"     every word: lemma, English gloss, grammatical cell (all readings), or UNKNOWN
    lexq <english word>      the lexicon's PIE words for an English word (scripts/lexq.py)
    usage <PIE word>         up to 6 corpus sentences using that word's lexeme, with their English
    cells <PIE word>         the lexeme's full paradigm, from the engine

Run: UV_CACHE_DIR=/tmp/pie-uv-cache uv run --quiet --project /Users/david/AI/PIE python -I tools.py <command> <args>
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/david/AI/PIE")
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
HELD = set(json.loads((HERE / "held_records.json").read_text()))


def analyzer():
    from pie.translator.analyze import Analyzer
    return Analyzer.load()


def analyze(text):
    an = analyzer()
    for w in text.split():
        core = w.strip(".,;:?!\"“”'()")
        parts = core.split("-")
        for p in parts:
            if not p:
                continue
            res, status = an.word(p)
            if not res:
                print(f"{p}: UNKNOWN ({status})")
            else:
                print(f"{p}: " + " | ".join(f"{a.lemma} '{a.english}' {a.features or ''} [{a.pos}]" for a in res[:4])
                      + ("" if status == "exact" else f"  ({status})"))


def lexeme(word):
    res, _ = analyzer().word(word.strip(".,?!"))
    return res[0].lex_id if res else None


def usage(word):
    lid = lexeme(word)
    if not lid:
        print("UNKNOWN word"); return
    n = 0
    for p in sorted((ROOT / "corpus").glob("tier[23]/*.jsonl")):
        for line in p.read_text("utf-8").splitlines():
            r = json.loads(line)
            if r["id"] in HELD or not any(t.get("lex_id") == lid for t in r.get("tokens", [])):
                continue
            print(f"- {r['pie']}\n  = {r.get('english', '')}")
            n += 1
            if n >= 6:
                return
    if not n:
        print("no corpus examples")


def cells(word):
    from pie.realize import Lexicon
    lid = lexeme(word)
    if not lid:
        print("UNKNOWN word"); return
    lx = Lexicon.load()
    fam = lx.specs[lid]["family"]
    gs = ("m", "f", "n") if fam == "adj" else (None,)
    for g in gs:
        cs = lx.cells(lid, g) if g else lx.cells(lid)
        print((f"[{g}] " if g else "") + "; ".join(f"{k} {v[0]}" for k, v in cs.items() if v))


if __name__ == "__main__":
    cmd, arg = sys.argv[1], " ".join(sys.argv[2:])
    if cmd == "lexq":
        subprocess.run([sys.executable, "-I", str(ROOT / "scripts/lexq.py"), *sys.argv[2:]], cwd=ROOT)
    else:
        {"analyze": analyze, "usage": usage, "cells": cells}[cmd](arg)
