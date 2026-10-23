"""Forward sound-law checker (Phase 3b): approximate, warning-only.

Whole-form comparison across daughters mostly measures derivation and
analogy, so this checks *diagnostic correspondences at the word-initial
position*, where alignment is reliable:

  satem/centum    ḱ ǵ ǵʰ → Skt ś j h; Gk/Lat k/c g; PGmc h k g
  labiovelars     kʷ → Lat qu-, Gk p/t/k, PGmc hw
  Grimm           p t k → PGmc f þ h;  b d g → p t k;  bʰ dʰ gʰ → b d g
  aspirates       bʰ dʰ gʰ → Skt bh dh gh/h, Gk ph th kh, Lat f f h
  Greek s- → h-   (before a vowel)
  prothesis       #h₁C #h₂C #h₃C → Gk e- a- o-
  coloring        #h₂e → Gk/Lat a-, #h₃e → o-

Each lexeme reflex not flagged borrowed, analogical or uncertain is
checked against its PIE source. A mismatch is a warning: a bad lexicon
entry or normalization, a prefixed daughter form, or a law this checker
lacks. Daughter forms are compared through their romanization (kaikki
`roman`), lowercased and stripped of diacritics, except ś ṣ, which Sanskrit
needs.
"""

from __future__ import annotations

import collections
import json
import re
import unicodedata
from pathlib import Path

from .phon import parse

ROOT = Path(__file__).resolve().parent.parent
LANGS = {"Sanskrit": "skt", "Ancient Greek": "grc", "Latin": "lat", "Proto-Germanic": "gem"}

# expected word-initial reflexes: PIE initial segment base → {lang: (law, allowed initial strings)}
EXPECT = {
    "p": {"skt": ("labial", ["p", "ph"]), "grc": ("labial", ["p"]), "lat": ("labial", ["p"]), "gem": ("grimm", ["f"])},
    "t": {"skt": ("dental", ["t", "th"]), "grc": ("dental", ["t"]), "lat": ("dental", ["t"]), "gem": ("grimm", ["þ", "th", "d"])},
    "k'": {"skt": ("satem", ["ś", "s"]), "grc": ("centum", ["k", "c"]), "lat": ("centum", ["c", "k"]), "gem": ("grimm", ["h"])},
    "k": {"skt": ("velar", ["k", "c", "kh"]), "grc": ("velar", ["k", "c"]), "lat": ("velar", ["c", "k"]), "gem": ("grimm", ["h"])},
    "kw": {"skt": ("labiovelar", ["k", "c"]), "grc": ("labiovelar", ["p", "t", "k"]), "lat": ("labiovelar", ["qu", "c"]),
           "gem": ("grimm", ["hw", "h"])},
    "b": {"skt": ("labial", ["b"]), "grc": ("labial", ["b"]), "lat": ("labial", ["b"]), "gem": ("grimm", ["p"])},
    "d": {"skt": ("dental", ["d"]), "grc": ("dental", ["d"]), "lat": ("dental", ["d", "l"]), "gem": ("grimm", ["t"])},
    "g'": {"skt": ("satem", ["j"]), "grc": ("centum", ["g"]), "lat": ("centum", ["g", "n"]), "gem": ("grimm", ["k"])},
    "g": {"skt": ("velar", ["g", "j"]), "grc": ("velar", ["g"]), "lat": ("velar", ["g"]), "gem": ("grimm", ["k"])},
    "gw": {"skt": ("labiovelar", ["g", "j"]), "grc": ("labiovelar", ["b", "d", "g"]), "lat": ("labiovelar", ["v", "u", "gu"]),
           "gem": ("grimm", ["kw", "k", "q"])},
    "bh": {"skt": ("aspirate", ["bh"]), "grc": ("aspirate", ["ph", "p"]), "lat": ("aspirate", ["f"]), "gem": ("grimm", ["b"])},
    "dh": {"skt": ("aspirate", ["dh", "d"]), "grc": ("aspirate", ["th", "t"]), "lat": ("aspirate", ["f"]), "gem": ("grimm", ["d"])},
    "g'h": {"skt": ("satem", ["h"]), "grc": ("aspirate", ["kh", "ch", "k"]), "lat": ("aspirate", ["h", "f", "g"]),
            "gem": ("grimm", ["g"])},
    "gh": {"skt": ("aspirate", ["gh", "h"]), "grc": ("aspirate", ["kh", "ch", "k"]), "lat": ("aspirate", ["h", "f", "g"]),
           "gem": ("grimm", ["g"])},
    "gwh": {"skt": ("aspirate", ["gh", "h"]), "grc": ("aspirate", ["ph", "th", "kh", "ch", "p", "t", "k"]),
            "lat": ("aspirate", ["f", "v", "u", "gu", "n"]), "gem": ("grimm", ["g", "b", "w"])},
    "m": {c: ("resonant", ["m"]) for c in ("skt", "grc", "lat", "gem")},
    "n": {c: ("resonant", ["n"]) for c in ("skt", "grc", "lat", "gem")},
    "l": {"skt": ("resonant", ["l", "r"]), "grc": ("resonant", ["l"]), "lat": ("resonant", ["l"]),
          "gem": ("resonant", ["l"])},
    "r": {c: ("resonant", ["r"]) for c in ("skt", "grc", "lat", "gem")},
    "w": {"skt": ("resonant", ["v", "u"]), "grc": ("resonant", ["w", "h", "a", "e", "o", "i", "u", "ē", "ō"]),
          "lat": ("resonant", ["v", "u"]), "gem": ("resonant", ["w", "u"])},
    "s": {"grc": ("greek-s-h", ["h", "s", ""]), "lat": ("sibilant", ["s"]), "gem": ("sibilant", ["s"]),
          "skt": ("sibilant", ["s", "ṣ", "ś"])},
}
PROTHESIS = {"h1": "e", "h2": "a", "h3": "o"}
ASPIRATES = {"bh", "dh", "gh", "g'h", "gwh"}
DEASPIRATED = {"skt": {"bh": ["b"], "dh": ["d"], "gh": ["g", "j"], "g'h": ["j"], "gwh": ["g", "j"]},
               "grc": {"bh": ["p"], "dh": ["t"], "gh": ["k", "c"], "g'h": ["k", "c"], "gwh": ["p", "t", "k"]}}
STOPS = {"p", "t", "k", "k'", "kw", "b", "d", "g", "g'", "gw", "bh", "dh", "gh", "g'h", "gwh"}
# Daughter prefixes (augment, preverbs, privative): a form that starts with one
# and fails the check is skipped, not counted: its initial is not the root's.
PREFIXES = {"grc": ("e", "ē", "eu", "a", "an", "en", "ek", "ex", "epi", "apo", "kata", "syn", "pro", "para", "dys"),
            "skt": ("a", "ā", "ud", "pra", "ni", "sam", "vi", "abhi", "upa", "anu", "pari", "su", "dus"),
            "lat": ("con", "com", "co", "re", "ex", "e", "in", "im", "per", "ad", "ab", "de", "dis", "di", "prae",
                    "pro", "sub"),
            "gem": ("ga", "bi", "uz", "fra", "and", "un", "ana", "ai")}


def _roman(r: dict, lang: str) -> str | None:
    s = r.get("roman") or r.get("form")
    if not s or s.startswith("-"):
        return None
    s = s.lstrip("*").lower()
    keep = {"ś", "ṣ", "þ"}
    out = []
    for ch in unicodedata.normalize("NFC", s):
        if ch in keep:
            out.append(ch)
            continue
        base = unicodedata.normalize("NFD", ch)[0]
        out.append(base)
    s = "".join(out)
    if lang == "grc" and s.startswith("rh"):
        s = "r" + s[2:]
    if lang == "lat" and s.startswith("j"):
        s = "i" + s[1:]
    if lang == "gem":
        s = s.replace("ƕ", "hw")
    return s


def _base(seg) -> str:
    return seg.ascii().replace("/", "").replace(":", "")


def _checks(segs, lang: str):
    """Yield (law, allowed initials) for a PIE form's first segment(s)."""
    if not segs:
        return
    first = _base(segs[0])
    second = _base(segs[1]) if len(segs) > 1 else ""
    if first in STOPS and second in STOPS:
        return  # initial stop clusters (dʰǵʰ-, tḱ-): beyond an initial check
    if first == "s" and second in STOPS | {"m", "n", "l", "r", "w"}:
        # s-mobile: the daughter may show the s or the following consonant's reflex
        rest = list(_checks(segs[1:], lang))
        allowed = {"s", "ṣ", "ś", "ch", "kṣ"} | {a for _, al in rest for a in al}
        yield ("s-mobile", sorted(allowed))
        return
    # laryngeal + consonant: Greek prothesis; other daughters start with the consonant
    if first in PROTHESIS and len(segs) > 1 and segs[1].kind in ("C", "R") and not segs[1].syl:
        if lang == "grc":
            yield ("prothesis", [PROTHESIS[first]])
        return
    if first in ("h2", "h3") and len(segs) > 1 and segs[1].kind == "V" and segs[1].base == "e":
        if lang in ("grc", "lat"):
            yield ("coloring", ["a"] if first == "h2" else ["o"])
        return
    if first in ASPIRATES and lang in DEASPIRATED and any(_base(x) in ASPIRATES for x in segs[1:]):
        # Grassmann's law: the first of two aspirates loses aspiration (bʰendʰ- → Skt bandh-)
        yield ("grassmann", DEASPIRATED[lang][first] + EXPECT[first][lang][1])
        return
    if first in EXPECT and lang in EXPECT[first]:
        law, allowed = EXPECT[first][lang]
        if first == "s" and lang == "grc" and not (len(segs) > 1 and segs[1].kind == "V"):
            return  # s + consonant stays s- in Greek; only check s + vowel
        yield (law, allowed)


def check_entry(e: dict):
    """Yield (lang, law, ok, pie_form, daughter_form) for one lexicon entry."""
    try:
        segs = parse(e["form"].strip("-"))
    except ValueError:
        return
    for lang_name, code in LANGS.items():
        for r in e.get("reflexes", {}).get(lang_name, []):
            if r.get("borrowed") or r.get("analogical") or r.get("uncertain"):
                continue
            d = _roman(r, code)
            if not d:
                continue
            for law, allowed in _checks(segs, code):
                ok = any(d.startswith(a) for a in allowed)
                if not ok and d.startswith(PREFIXES.get(code, ())) and law not in ("prothesis", "coloring"):
                    continue  # prefixed daughter form: its initial is not the root's
                yield code, law, ok, e["form"], r.get("roman") or r.get("form")


def run(root: Path = ROOT) -> dict:
    lex = [json.loads(x) for x in (root / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()]
    stats = collections.defaultdict(collections.Counter)
    warnings = []
    for e in lex:
        for code, law, ok, pie, d in check_entry(e):
            stats[(law, code)]["ok" if ok else "mismatch"] += 1
            if not ok:
                warnings.append({"lex_id": e["id"], "pie": pie, "lang": code, "law": law, "daughter": d})
    table = {f"{law}|{code}": {**dict(c), "rate": round(c["mismatch"] / (c["ok"] + c["mismatch"]), 3)}
             for (law, code), c in sorted(stats.items())}
    return {"by_law": table, "warnings": warnings,
            "total": {"checks": sum(c["ok"] + c["mismatch"] for c in stats.values()),
                      "mismatch": sum(c["mismatch"] for c in stats.values())}}
