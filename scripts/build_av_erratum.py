#!/usr/bin/env python3
"""Erratum for Atharvaveda loci cited by DCS sentence index.

  uv run python -I scripts/build_av_erratum.py   →  data/research/8c/av-loci-erratum.json

The DCS loader (pie.formula_search_multi.load_dcs) labels an AV unit
'AVŚ, 8, 6.s48': the 48th DCS *sentence* (≈ half-verse) of hymn 8.6, not its
verse. Packets, claims, reviews and reports then wrote 'AVŚ 8.6.48' for what
is AVŚ 8.6.23ab. This script lists every such sentence locus that appears in
the project's research outputs with its verse citation
(fm.dcs_citation_index), and every verse-style AV citation in those files that
is (or may be) a sentence index read as a verse.

Sentence-locus forms recognised: 'AVŚ, 8, 6.s48', 'AVŚ 8, 6.s48', 'AVŚ, 4, 12 s5',
'AVŚ 4,12 s1', 'AVŚ 7.102 s2', 'AVP 5.21 s1', with continuations in the same
string ('s4, s6', 's2-s4', 's3 (…) and s4', '; also AVŚ 12,3 s16, 18,1 s119').

Statuses (see fm.dcs_assign_verses): counter = DCS sent_counter (exact);
bracketed = no counter, but the numbered lines around it leave one verse
(exact); inferred = heuristic segmentation (accuracy measured below by hiding
the counters of the numbered chapters), for the cited ones checked by hand
where noted (checked: whitney | literature); unmapped = no verse.
Corpus text is not written out; only loci.
"""
from __future__ import annotations

import collections
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie import formula_search_multi as fm  # noqa: E402

OUT = ROOT / "data/research/8c/av-loci-erratum.json"
SCAN = ["data/research/8c/**/*", "docs/research/8c-*.md", "docs/research/8a-*.md",
        "data/research/formulas/eval-r3/**/*", "data/tier2/plans/*.jsonl", "corpus/tier2/*.jsonl",
        "docs/audits/tier2-review*.md", "data/research/literature/**/*", "docs/research/literature-review.md"]
BULK = ("data/research/8c/packets/", "data/research/8c/packets-loci/", "data/research/8c/stageB/slabs/",
        "data/research/8c/stageB/slabs-loci/")

_HEAD = re.compile(r"(AVŚ|AVP|ṚVKh)(?:,? ?(\d+), ?(\d+)[. ]s(\d+)\b|,? (\d+)\.(\d+) s(\d+)\b)")
_CONT = re.compile(r"(?:\s*(?:[,;+(]|and|also)\s*)+(?:(\d+)[,.] ?(\d+) s(\d+)\b|s(\d+)(?:\s*[-–]\s*s(\d+))?\b)"
                   r"|\s*[-–]\s*s(\d+)\b"
                   r"|\s*\([^)]{0,40}\)(?=\s*(?:[,;+]|and)\s*s\d)")
_BARE = re.compile(r"(?<![\d.,] )(?<![\d.,])\b(\d+), ?(\d+) s(\d+)\b")
_VERSE = re.compile(r"\b(AVŚ|AVP|AV)\.? ?(\d+)\.(\d+)\.(\d+)([a-e]*)")

# cited 'inferred' loci checked by hand, 2026-10-23: "whitney" = read against the
# Whitney–Lanman translation of the mapped stanza (…/atharvaveda-shaunaka/translations/
# whitney.txt); "literature" = the eval-r3 record that cites the DCS sentence also gives
# the handbook verse, and the two agree
_W = ["AVŚ, 1, 34.s13", "AVŚ, 11, 10.s18", "AVŚ, 11, 2.s44", "AVŚ, 12, 1.s9", "AVŚ, 12, 1.s10", "AVŚ, 12, 1.s11",
      "AVŚ, 16, 8.s2", "AVŚ, 17, 1.s115", "AVŚ, 17, 1.s116", "AVŚ, 17, 1.s117", "AVŚ, 3, 12.s10", "AVŚ, 3, 12.s11",
      "AVŚ, 3, 12.s12", "AVŚ, 3, 23.s13", "AVŚ, 3, 23.s14", "AVŚ, 3, 4.s10", "AVŚ, 3, 4.s11", "AVŚ, 3, 4.s12",
      "AVŚ, 4, 20.s16", "AVŚ, 4, 20.s17", "AVŚ, 4, 20.s18", "AVŚ, 4, 22.s13", "AVŚ, 4, 22.s14", "AVŚ, 4, 22.s15",
      "AVŚ, 4, 3.s6", "AVŚ, 4, 3.s7", "AVŚ, 4, 3.s8", "AVŚ, 5, 8.s14", "AVŚ, 6, 2.s1", "AVŚ, 6, 2.s2",
      "AVŚ, 6, 96.s2", "AVŚ, 6, 96.s3", "AVŚ, 8, 7.s39"]
_L = ["AVŚ, 1, 1.s2", "AVŚ, 1, 32.s1", "AVŚ, 4, 12.s1", "AVŚ, 4, 12.s4", "AVŚ, 4, 12.s5", "AVŚ, 4, 12.s7",
      "AVŚ, 4, 12.s8", "AVŚ, 4, 12.s10", "AVŚ, 4, 12.s11", "AVŚ, 4, 12.s17", "AVŚ, 6, 63.s8", "AVŚ, 6, 75.s6",
      "AVŚ, 7, 70.s1", "AVŚ, 10, 10.s72"]
CHECKED = {**{k: "whitney" for k in _W}, **{k: "literature" for k in _L}}

# human-readable documents corrected in place (task: docs cite the s-index as a verse)
DOC_FIXES = [
    {"file": "docs/research/8c-results.md", "was": "AVŚ 8.6.48", "now": "AVŚ 8.6.23ab", "dcs": "AVŚ, 8, 6.s48"},
    {"file": "docs/research/8c-results.md", "was": "AVŚ 11.10.18", "now": "AVŚ 11.10.8", "dcs": "AVŚ, 11, 10.s18"},
    {"file": "docs/research/8c-results.md", "was": "AVŚ 9.1.2", "now": "AVŚ 9.1.1cd", "dcs": "AVŚ, 9, 1.s2"},
    {"file": "docs/research/8c-novelty.md", "was": "AVŚ 12.2.29", "now": "AVŚ 12.2.15ab", "dcs": "AVŚ, 12, 2.s29"},
    {"file": "docs/research/8c-novelty.md", "was": "AVŚ 8.6.48", "now": "AVŚ 8.6.23ab", "dcs": "AVŚ, 8, 6.s48"},
    {"file": "docs/research/8c-novelty.md", "was": "AVŚ 13.1.47", "now": "AVŚ 13.1.24ab", "dcs": "AVŚ, 13, 1.s47"},
    {"file": "docs/research/8c-novelty.md", "was": "AVŚ 4.21.14", "now": "AVŚ 4.21.7cd", "dcs": "AVŚ, 4, 21.s14"},
    {"file": "docs/research/8c-novelty.md", "was": "AVP 19.14.24", "now": "AVP 19.14.12cd", "dcs": "AVP, 19, 14.s24"},
    {"file": "docs/research/literature-review.md", "was": "s29 is 8.3.16a", "now": "s29 is 8.3.15ab", "dcs": "AVŚ, 8, 3.s29"},
    {"file": "docs/research/literature-review.md", "was": "AV 8.3.8b", "now": "AV 8.3.7cd", "dcs": "AVŚ, 8, 3.s14"},
    {"file": "docs/research/literature-review.md", "was": "AV 4.21.7b", "now": "AV 4.21.7cd", "dcs": "AVŚ, 4, 21.s14"},
    {"file": "docs/research/literature-review.md", "was": "AV 8.4.2b", "now": "AV 8.4.2cd", "dcs": "AVŚ, 8, 4.s4"},
]


def scan_files() -> list[Path]:
    seen = set()
    for pat in SCAN:
        for p in sorted(ROOT.glob(pat)):
            if p.is_file() and p not in seen and p.name != OUT.name:
                seen.add(p)
    return sorted(seen)


def sentence_loci(text: str) -> list[str]:
    """All DCS sentence loci in a string, normalised to 'AVŚ, b, h.sN'."""
    out = []
    for m in _HEAD.finditer(text):
        t = m[1]
        b, h, n = (m[2], m[3], m[4]) if m[2] else (m[5], m[6], m[7])
        out.append(f"{t}, {int(b)}, {int(h)}.s{int(n)}")
        pos = m.end()
        last = int(n)
        while True:
            c = _CONT.match(text, pos)
            if not c or c.end() == pos:
                break
            pos = c.end()
            if c[1]:
                b, h, last = c[1], c[2], int(c[3])
                out.append(f"{t}, {int(b)}, {int(h)}.s{last}")
            elif c[4] or c[6]:
                lo = int(c[4]) if c[4] else last + 1
                hi = int(c[5] or c[6] or lo)
                out.extend(f"{t}, {int(b)}, {int(h)}.s{k}" for k in range(lo, min(hi, lo + 40) + 1))
                last = hi
    # bare 'b,h sN' after a head in the same string ('(also 9,10 s23)'): the preceding head's text
    heads = [(m.start(), m[1]) for m in _HEAD.finditer(text)]
    for m in _BARE.finditer(text):
        prev = [t for p, t in heads if p < m.start()]
        if prev:
            out.append(f"{prev[-1]}, {int(m[1])}, {int(m[2])}.s{int(m[3])}")
    return list(dict.fromkeys(out))


def records(text: str, path: Path) -> list[str]:
    """JSONL → one string per record; otherwise per paragraph."""
    if path.suffix in (".jsonl", ".progress"):
        return text.splitlines()
    return text.split("\n\n")


def validate(stanzas) -> dict:
    """Hide the counters of the fully numbered chapters and re-infer: share of
    sentences whose verse comes out right (with the hymn's stanza count: Whitney
    for AVŚ, the DCS maximum for AVP; and with 70 % of the counters kept)."""
    out = {}
    for t in fm.DCS_VEDIC[:2]:
        st = collections.Counter()
        for fn in sorted((fm.ROOT / fm.DCS_DIR / t).glob("*.conllu")):
            ch, s = fm.dcs_sentence_heads(fn.read_text("utf-8"))
            if not s or not all(x["counter"] for x in s):
                continue
            truth = [x["counter"] for x in s]
            key = fm._dcs_chapter_key(ch)
            nv = stanzas.get(key[1:]) if key[0] == "AVŚ" else max(truth)
            r = fm.dcs_assign_verses([dict(x, counter=None, sub=None) for x in s], nv)
            st["none_n"] += len(s)
            st["none_ok"] += sum(y["verse"] == v for y, v in zip(r, truth))
            rnd = random.Random(ch)
            s2 = [dict(x) if rnd.random() < 0.7 else dict(x, counter=None, sub=None) for x in s]
            r2 = fm.dcs_assign_verses(s2, nv)
            for x, y, v in zip(s2, r2, truth):
                if not x["counter"]:
                    st[f"{y['status']}_n"] += 1
                    st[f"{y['status']}_ok"] += y["verse"] == v
        ab = fm.DCS_ABBR[t]
        out[ab] = {
            "no_counters_inferred": f"{st['none_ok']}/{st['none_n']} = {st['none_ok'] / max(1, st['none_n']):.3f}",
            "30pct_hidden_bracketed": f"{st['bracketed_ok']}/{st['bracketed_n']}",
            "30pct_hidden_inferred": f"{st['inferred_ok']}/{st['inferred_n']}",
        }
    return out


def main():
    idx = fm.dcs_citation_index()
    stanzas = fm.whitney_stanzas()
    maxc: dict = collections.defaultdict(int)
    for rec in idx.values():
        if rec["status"] == "counter" and rec["verse"]:
            ch = rec["dcs"].rsplit(".s", 1)[0]
            maxc[ch] = max(maxc[ch], int(rec["verse"].rsplit(".", 1)[1]))

    nlines: dict = {}
    for t in fm.DCS_VEDIC[:2]:
        for fn in sorted((fm.ROOT / fm.DCS_DIR / t).glob("*.conllu")):
            ch, sents = fm.dcs_sentence_heads(fn.read_text("utf-8"))
            nlines[ch] = len({x["line_id"] for x in sents})

    def chapter_check(ch: str) -> str:
        k = fm._dcs_chapter_key(ch)
        w = stanzas.get(k[1:]) if k and k[0] == "AVŚ" else None
        if ch not in maxc:                       # no DCS counters at all: every verse is inferred
            if w is None:
                return "no DCS counters and no stanza count: inferred verse unreliable"
            if w > nlines.get(ch, 0):
                return f"no DCS counters; Whitney {w} stanzas > {nlines.get(ch, 0)} DCS lines: inferred verse unreliable"
            return f"no DCS counters; inferred against Whitney's {w} stanzas"
        if not k or k[0] != "AVŚ":
            return "no stanza count (AVP: none shipped)"
        if w is None:
            return "hymn not in Whitney file"
        if maxc[ch] != w:
            return f"DCS numbers {maxc[ch]} stanzas, Whitney {w}: verse numbering may differ"
        return "ok"

    files = scan_files()
    cited: dict = collections.defaultdict(lambda: {"files": set(), "bulk": collections.Counter()})
    verse_style: dict = collections.defaultdict(lambda: {"files": set(), "same_record": set()})
    for p in files:
        try:
            text = p.read_text("utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(p.relative_to(ROOT))
        bulk = next((b for b in BULK if rel.startswith(b)), None)
        for rec_text in records(text, p):
            locs = sentence_loci(rec_text)
            for loc in locs:
                if bulk:
                    cited[loc]["bulk"][bulk] += 1
                else:
                    cited[loc]["files"].add(rel)
            if bulk:
                continue
            for m in _VERSE.finditer(rec_text):
                t = {"AV": "AVŚ"}.get(m[1], m[1])
                key = f"{m[1]} {m[2]}.{m[3]}.{m[4]}{m[5]}"
                sloc = f"{t}, {int(m[2])}, {int(m[3])}.s{int(m[4])}"
                verse_style[(key, sloc)]["files"].add(rel)
                if sloc in locs:
                    verse_style[(key, sloc)]["same_record"].add(rel)

    loci = {}
    unmapped = {}
    for loc in sorted(cited, key=lambda s: (s.split(",")[0], *map(int, re.findall(r"\d+", s)))):
        c = cited[loc]
        rec = idx.get(loc)
        ch = loc.rsplit(".s", 1)[0]
        b, h, n = re.findall(r"\d+", loc)
        entry = {"misread_as": f"{loc.split(',')[0]} {b}.{h}.{n}"}
        if rec is None:
            entry.update(status="unmapped", reason="no such DCS sentence (chapter absent or index beyond it)")
        else:
            entry.update(sent_id=rec["sent_id"], verse=rec["verse"] or None, pada=rec["pada"] or None,
                         cite=rec["cite"] or None, status=rec["status"], line_in_verse=rec["line"],
                         lines_in_verse=rec["lines"], chapter_check=chapter_check(ch))
            if rec["status"] == "inferred":
                entry["checked"] = CHECKED.get(loc)
                if not entry["checked"]:         # a heuristic verse is not a correction: keep it apart
                    entry["inferred_cite"], entry["cite"], entry["verse"] = entry["cite"], None, None
        entry["cited_in"] = sorted(c["files"])
        if c["bulk"]:
            entry["cited_in_bulk"] = dict(sorted(c["bulk"].items()))
        loci[loc] = entry
        if entry["status"] == "unmapped" or (entry["status"] == "inferred" and not entry.get("checked")
                                             and c["files"]):
            unmapped[loc] = {"status": entry["status"], "files": sorted(c["files"]) or sorted(c["bulk"])}

    vs = []
    for (key, sloc), v in sorted(verse_style.items()):
        rec = idx.get(sloc)
        cit = loci.get(sloc)
        k = fm._dcs_chapter_key(sloc.rsplit(".s", 1)[0])
        n = int(sloc.rsplit(".s", 1)[1])
        w = stanzas.get(k[1:]) if k and k[0] == "AVŚ" else None
        same = rec is not None and rec["verse"] and int(rec["verse"].rsplit(".", 1)[1]) == n
        if same and (v["same_record"] or cit is not None):
            verdict = "consistent either way (DCS sentence s{0} is verse {0})".format(n)
        elif v["same_record"]:
            verdict = "sentence index read as verse (the same record cites the DCS sentence)"
        elif w is not None and n > w:
            verdict = f"sentence index read as verse (hymn has {w} stanzas)"
        elif cit is not None:
            verdict = "probably a sentence index read as verse (the DCS sentence is cited elsewhere)"
        else:
            verdict = "verse number (no DCS sentence locus behind it; not checked here)"
        row = {"as_written": key, "files": sorted(v["files"]), "verdict": verdict}
        if verdict.startswith(("sentence", "probably")):
            row.update(dcs=sloc, status=(rec or {}).get("status", "unmapped"))
            if rec and rec["status"] == "inferred" and sloc not in CHECKED:
                row["inferred_cite"] = rec["cite"] or None
            else:
                row["cite"] = (rec or {}).get("cite") or None
        vs.append(row)

    st = collections.Counter(e["status"] for e in loci.values())
    out = {
        "_source": (
            "Erratum for AV/AVP loci written as DCS sentence indices ('AVŚ, 8, 6.s48' = 48th sentence of hymn 8.6) and "
            "read as verse numbers. Built by scripts/build_av_erratum.py from the DCS CoNLL-U headers "
            "(sent_counter/sent_subcounter; sent_id '<line>_<k>') via pie.formula_search_multi.dcs_citation_index; "
            "stanza counts from the Whitney–Lanman translation shipped with the DCS. This file is the correction for "
            "the frozen evaluation set (data/research/formulas/eval-r3/formulas-eval.jsonl) and for the committed 8c "
            "packets, claims, verdicts, accepted and novelty files, which are not rewritten. 'cite' is the citation to "
            "use; status 'inferred' is a heuristic verse (see _validation): it is in 'cite' only where 'checked' names how it was verified (whitney | literature), otherwise in 'inferred_cite' (not to be cited unchecked); pāda letters are given only for a 2-line stanza with lines of similar length (ab = first DCS line, "
            "cd = second)."),
        "_scanned": SCAN,
        "_counts": {"sentence_loci": len(loci), **dict(sorted(st.items()))},
        "_validation": validate(stanzas),
        "documents_corrected": DOC_FIXES,
        "loci": loci,
        "verse_style_mentions": vs,
        "unmapped_or_unchecked_in_reports": unmapped,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(OUT.relative_to(ROOT), out["_counts"], out["_validation"])
    print("verse-style mentions:", collections.Counter(r["verdict"].split(" (")[0] for r in vs))
    print("unmapped/unchecked cited outside bulk files:", len(unmapped))


if __name__ == "__main__":
    main()
