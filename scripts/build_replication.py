#!/usr/bin/env python3
"""Phase 8b replication dataset (pre-registered in docs/research/8b-preregistration.md).

  uv run --group research python -I scripts/build_replication.py \\
      raw/daughters/kaikki-sanskrit/kaikki.org-dictionary-Sanskrit.jsonl \\
      raw/daughters/kaikki-ancientgreek/kaikki.org-dictionary-AncientGreek.jsonl \\
      raw/daughters/kaikki-latin/kaikki.org-dictionary-Latin.jsonl

Fresh cognate sets from the kaikki.org (wiktextract) Sanskrit, Ancient Greek and
Latin dictionaries: every entry whose etymology links it to a word-level PIE
etymon is grouped under that etymon, and a group with reflexes in at least two
languages is a cognate set. The dumps are untrusted data: they are only parsed
as JSON, never executed.

Rules (fixed before the data was built):
- links: {{inh}}, {{inh+}}, {{der}}, {{der+}} with source ine-pro, and {{etymon}}
  terms `ine-pro:...` under :inh / :der. Not borrowings, not uncertain links
  (uder, <unc>), not cognate mentions. Entries with an affix or compound
  template, or linked to two different word-level PIE terms, are not reflexes of
  one word and are dropped. Terms ending in `-` (roots, stems) or starting with
  `-` (suffixes) are not word-level etyma; they only help find the root family.
- forms: Sanskrit and Greek romanizations, Latin canonical (macron) forms. Greek
  romanizations lose the breve (U+0306), which kaikki headwords write on every
  short dichronon and the first run's inputs almost never do. Macrons and
  accents stay: they are the signal.
- contamination, as in scripts/build_backtest.py: attested languages only;
  forms writing laryngeal notation are dropped and a language over 2% would be
  dropped whole; no Anatolian or Tocharian (none in these dumps).
- target: pie/prelaryngeal.py on the lexicon's canonical form of the etymon.
- fresh at root-family level: a set is dropped if its etymon, or any root its
  entries link to, resolves to a lexicon entry whose family (root_id, else id)
  occurs in data/research/backtest/primary.jsonl or secondary.jsonl, if its
  target or etymon key equals a first-run one, or if it shares a (language,
  form) pair with a first-run input. Etyma the lexicon does not know get a
  `kaikki:` pseudo family (their own key) as root_id.

Writes data/research/backtest/replication.jsonl and replication_meta.json.
"""

from __future__ import annotations

import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie import backtest as bt  # noqa: E402
from pie.formula_search import PieIndex, pie_key  # noqa: E402
from pie.lexicon import parse_form  # noqa: E402
from pie.prelaryngeal import convert  # noqa: E402

LANG = {"sa": "Sanskrit", "grc": "Ancient Greek", "la": "Latin"}
LAR = re.compile(r"h[₁₂₃ₓ]|ʔ|ə[₁₂₃]")
CONTAMINATION_RATE = 0.02
LINK = ("inh", "inh+", "der", "der+")
AFFIX = ("af", "affix", "suffix", "prefix", "confix", "com", "compound", "suf", "pre", "con", "blend")
SKIP_POS = {"root", "suffix", "prefix", "affix", "infix", "interfix", "circumfix", "character", "romanization",
            "abbrev", "symbol"}
BREVE = "̆"


def _strip(s: str) -> str:
    return re.sub(r"<[^<>]*>", "", s or "").strip()


def _etymon_term(v: str) -> str | None:
    """`ine-pro:*h₁ey-<id:go>` → `*h₁ey-`; `ine-pro:<alt:*dʰyeh₂-><ety:...>` → `*dʰyeh₂-`."""
    v = v[len("ine-pro:"):]
    m = re.match(r"<alt:([^<>]*)>", v)
    if m:
        return m.group(1).strip()
    t = v
    while True:
        u = re.sub(r"<[^<>]*>", "", t)
        if u == t:
            break
        t = u
    return t.strip() or None


def entry_links(d: dict, lang: str) -> dict | None:
    """Word-level PIE links and root links of one wiktextract entry."""
    words, roots, affix, unc = [], [], False, False
    for t in d.get("etymology_templates") or []:
        name, a = t.get("name"), t.get("args") or {}
        if name in AFFIX:
            affix = True
            continue
        if a.get("1") != lang:
            continue
        if name in LINK and a.get("2") == "ine-pro":
            raw = a.get("3") or a.get("4") or ""
            if "<unc" in raw or a.get("unc"):
                unc = True
                continue
            term = _strip(raw)
            if term and term != "-":
                words.append(term)
        elif name == "root" and a.get("2") == "ine-pro":
            roots += [_strip(a[k]) for k in sorted((k for k in a if k.isdigit() and int(k) >= 3), key=int) if _strip(a[k])]
        elif name == "etymon":
            rel = None
            for k in sorted((k for k in a if k.isdigit() and int(k) >= 2), key=int):
                v = a[k]
                if v.startswith(":"):
                    rel = v
                    continue
                if not v.startswith("ine-pro:"):
                    continue
                term = _etymon_term(v)
                if not term:
                    continue
                if rel is None:
                    continue
                if rel.startswith(":af") or rel.startswith(":com") or rel.startswith(":suf") or rel.startswith(":pre"):
                    affix = True
                    continue
                if "unc" in rel or "<unc" in v or rel.startswith(":uder"):
                    unc = True
                    continue
                if rel.split("<")[0] in (":inh", ":der"):
                    words.append(term)
    root_like = [w for w in words if w.endswith("-")]
    words = [w for w in words if not w.endswith("-") and not w.startswith("-")]
    roots += root_like
    if not words and not roots:
        return None
    return {"words": words, "roots": roots, "affix": affix, "uncertain": unc}


def form_of(d: dict, lang: str) -> str | None:
    if lang in ("sa", "grc"):
        r = next((f.get("form") for f in d.get("forms") or [] if "romanization" in (f.get("tags") or [])), None)
        if not r:
            for h in d.get("head_templates") or []:
                r = (h.get("args") or {}).get("tr") or None
                if r:
                    break
        if r and lang == "grc":
            r = unicodedata.normalize("NFC", unicodedata.normalize("NFD", r).replace(BREVE, ""))
        return r
    c = next((f.get("form") for f in d.get("forms") or [] if "canonical" in (f.get("tags") or [])), None)
    if not c:
        for h in d.get("head_templates") or []:
            a = h.get("args") or {}
            c = _strip(a.get("head") or "") or None
            if c:
                break
    return c or d.get("word")


def is_form_page(d: dict) -> bool:
    for h in d.get("head_templates") or []:
        if any(isinstance(v, str) and v.endswith(" form") for v in (h.get("args") or {}).values()):
            return True
    ss = d.get("senses") or []
    return bool(ss) and all(s.get("form_of") or s.get("alt_of") for s in ss)


def read_dump(path: str, lang: str, stats: collections.Counter) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if "ine-pro" not in line:
                continue
            d = json.loads(line)
            if d.get("lang_code") not in (None, lang):
                continue
            links = entry_links(d, lang)
            if not links:
                continue
            stats[f"{lang}:entries_with_pie_link"] += 1
            pos = d.get("pos")
            if pos in SKIP_POS or is_form_page(d):
                stats[f"{lang}:skip_pos_or_form_page"] += 1
                continue
            out.append({"lang": lang, "word": d.get("word"), "pos": pos, "form": form_of(d, lang), **links})
    return out


def main(paths: list[str]) -> int:
    lex = bt.load(ROOT / "data/lexicon/lexicon.jsonl")
    byid = {e["id"]: e for e in lex}
    idx = PieIndex(lex)
    D = ROOT / "data/research/backtest"
    first = bt.load(D / "primary.jsonl") + bt.load(D / "secondary.jsonl")
    first_ids = {r["id"] for r in first}
    first_fams = {bt.family(r) for r in first}
    first_targets = {r["target"] for r in first}
    first_keys = {pie_key(r["modern"]) for r in first}
    first_forms = {(l, f) for r in first for l, fs in r["inputs"].items() for f in fs}

    def fam_of(eid: str) -> str:
        e = byid.get(eid) or {}
        return e.get("root_id") or eid

    stats: collections.Counter = collections.Counter()
    entries = []
    for p in paths:
        lang = next(c for c, n in (("sa", "Sanskrit"), ("grc", "AncientGreek"), ("la", "Latin")) if n in Path(p).name)
        entries += read_dump(p, lang, stats)

    # one word-level etymon per entry
    groups: dict[str, dict] = {}
    for e in entries:
        if e["affix"]:
            stats[f"{e['lang']}:drop_affix_or_compound"] += 1
            continue
        if not e["words"]:
            stats[f"{e['lang']}:drop_root_only"] += 1
            continue
        parsed = []
        for w in dict.fromkeys(e["words"]):
            p = parse_form(w if w.startswith("*") else "*" + w)
            parsed.append(p.lemma)
        lemmas = [x for x in dict.fromkeys(parsed) if x]
        if len({pie_key(x) for x in lemmas}) > 1:
            stats[f"{e['lang']}:drop_two_word_etyma"] += 1
            continue
        if not lemmas:
            stats[f"{e['lang']}:drop_etymon_unparsable"] += 1
            continue
        if not e["form"]:
            stats[f"{e['lang']}:drop_no_romanization"] += 1
            continue
        lemma = lemmas[0]
        g = groups.setdefault(lemma, {"terms": set(), "forms": collections.defaultdict(list), "roots": set(),
                                      "words": collections.defaultdict(list)})
        g["terms"].update(e["words"])
        g["roots"].update(e["roots"])
        f = unicodedata.normalize("NFC", e["form"].strip())
        L = LANG[e["lang"]]
        if f not in g["forms"][L]:
            g["forms"][L].append(f)
            g["words"][L].append(e["word"])

    # contamination scan per language (rate), then per form
    tot, bad = collections.Counter(), collections.Counter()
    for g in groups.values():
        for L, fs in g["forms"].items():
            for f in fs:
                tot[L] += 1
                bad[L] += bool(LAR.search(f))
    contaminated = sorted(L for L in tot if bad[L] / tot[L] > CONTAMINATION_RATE)

    rows, reasons = [], collections.Counter()
    fam_source = collections.Counter()
    for lemma, g in sorted(groups.items()):
        inputs = {}
        for L, fs in sorted(g["forms"].items()):
            if L in contaminated:
                continue
            keep = [f for f in fs if not LAR.search(f)]
            if keep:
                inputs[L] = keep
        if len(inputs) < 2:
            reasons["fewer_than_2_languages"] += 1
            continue
        try:
            target, effects = convert(lemma)
        except ValueError:
            reasons["transducer_failed"] += 1
            continue
        # families: the etymon itself, then any linked root
        hits = set()
        for t in g["terms"]:
            hits |= idx.pie(t)
        root_hits = set()
        for t in g["roots"]:
            root_hits |= idx.pie(t, roots_only=True)
        fams = {fam_of(x) for x in hits | root_hits}
        if (hits | root_hits) & first_ids or fams & first_fams:
            reasons["root_family_in_first_run"] += 1
            continue
        if target in first_targets or pie_key(lemma) in first_keys:
            reasons["etymon_in_first_run"] += 1
            continue
        if any((L, f) in first_forms for L, fs in inputs.items() for f in fs):
            reasons["shares_input_form_with_first_run"] += 1
            continue
        if hits:
            ids = sorted(hits)
            fam = sorted({fam_of(x) for x in hits})[0]
            fam_source["lexicon_entry"] += 1
            rid = ids[0]
        elif root_hits:
            fam = sorted({fam_of(x) for x in root_hits})[0]
            fam_source["lexicon_root"] += 1
            rid = f"kaikki:{pie_key(lemma)}"
        else:
            fam = f"kaikki:{pie_key(lemma)}"
            fam_source["pseudo"] += 1
            rid = fam
        rows.append({"id": rid if rid.startswith("kaikki:") else rid, "root_id": fam, "split": "replication",
                     "inputs": inputs, "target": target,
                     "effects": [{"kind": x.kind, "laryngeal": x.laryngeal, "offset": x.offset} for x in effects],
                     "modern": lemma, "hittite": None, "kaikki_terms": sorted(g["terms"]),
                     "kaikki_words": {L: g["words"][L] for L in inputs}})
    # ids unique
    seen = collections.Counter(r["id"] for r in rows)
    for r in rows:
        if seen[r["id"]] > 1:
            r["id"] = f"{r['id']}|{r['modern']}"

    # power check from the data alone (no model): exact strata, 3-family rule
    words = [bt.Word(r["id"], bt.family(r), bt.segments(r["target"]), bt.effect_slots(r)) for r in rows]
    matched = bt.match(words, "exact")
    with_ctl = [x for x in matched if x["controls"]]
    per_kind = {k: {"effect_slots": sum(k in x["kinds"] for x in matched),
                    "matched": sum(k in x["kinds"] for x in with_ctl),
                    "matched_families": len({words[x["word"]].family for x in with_ctl if k in x["kinds"]})}
                for k in bt.KINDS}
    train_units = {u for r in bt.load(D / "primary.jsonl") for u in bt.segments(r["target"])}
    oov = collections.Counter(u for w in words for u in w.units if u not in train_units)
    meta = {
        "built_from": [Path(p).name for p in paths],
        "rules": __doc__.split("Rules (fixed before the data was built):")[1].split("Writes")[0].strip(),
        "extraction": dict(sorted(stats.items())),
        "groups_before_filters": len(groups),
        "dropped": dict(reasons),
        "contaminated_languages": contaminated,
        "laryngeal_notation_rate": {L: bad[L] / tot[L] for L in tot},
        "sets": len(rows),
        "sets_with_effect": sum(1 for r in rows if r["effects"]),
        "families": len({bt.family(r) for r in rows}),
        "family_source": dict(fam_source),
        "by_language": dict(collections.Counter(L for r in rows for L in r["inputs"])),
        "languages_per_set": dict(collections.Counter(len(r["inputs"]) for r in rows)),
        "effect_slots": len(matched),
        "effect_slots_exact_matched": len(with_ctl),
        "matched_families": len({words[x["word"]].family for x in with_ctl}),
        "per_kind": per_kind,
        "min_slots_rule": 150,
        "powered": len(with_ctl) >= 150,
        "target_units_outside_training_vocab": dict(oov),
    }
    (D / "replication.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    (D / "replication_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps({k: v for k, v in meta.items() if k != "rules"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
