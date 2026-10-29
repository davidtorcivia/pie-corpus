"""Derived glosses for unglossed derivatives: root meaning + suffix function.

Most usable lexemes are derivatives from Wiktionary's descendant trees,
with segmentation but no gloss. When the root is glossed and the final
suffix is a known affix entry, the gloss is composed as
"<root gloss> [<suffix>: <function>]". These glosses are APPROXIMATE: the
planner is told so, and records using them are tagged, so reviews can
measure meaning errors on derived-gloss lexemes separately.

Suffix labels below are short paraphrases of the Wiktionary affix entries'
own glosses. Unlisted suffixes fall back to the affix entry's first clause.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LABELS = {
    "-ti": "present verb", "-eti": "thematic present verb", "-yeti": "transitive present verb",
    "-yéti": "intransitive present verb", "-éyeti": "causative/iterative verb", "-sḱéti": "durative/iterative verb",
    "-éh₁yeti": "stative verb", "-néh₂ti": "nasal present verb", "-néwti": "nasal present verb",
    "-tós": "verbal adjective, 'X-ed'", "-nós": "verbal adjective, 'X-ed'", "-rós": "adjective",
    "-lós": "adjective", "-ós": "agent noun or adjective, 'X-ing'", "-os": "action/result noun, 'act of X'",
    "-éh₂": "abstract/collective noun", "-eh₂": "abstract/collective noun", "-mn̥": "result noun, 'what is X-ed'",
    "-mos": "action/result noun", "-tis": "action noun, 'act of X-ing'", "-tus": "action noun",
    "-tḗr": "agent noun, 'one who X-es'", "-tōr": "agent noun, 'one who X-es'", "-trom": "instrument, 'means of X-ing'",
    "-tlom": "instrument, 'means of X-ing'", "-dʰlom": "instrument or place", "-yos": "adjective of relation",
    "-ih₂": "feminine noun", "-ōs": "abstract noun", "-us": "adjective or noun", "-is": "noun",
    "-wōs": "perfect participle, 'having X-ed'", "-onts": "participle, 'X-ing'", "-mh₁nos": "middle participle",
    "-s": "root noun",
}


def _plain(s: str) -> str:
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if c not in ("́",))


def build(lexicon: list[dict]) -> dict[str, dict]:
    by_id = {e["id"]: e for e in lexicon}
    affixes, exact = {}, {}
    for e in lexicon:
        if e["kind"] == "affix" and e["meaning"]:
            affixes.setdefault(_plain(e["form"]), e)
            exact.setdefault(e["form"], e)
    out = {}
    for e in lexicon:
        if e["meaning"] or e["kind"] not in ("derivative", "word"):
            continue
        root = by_id.get(e.get("root_id") or "")
        seg = e.get("segmented")
        if not root or not root.get("meaning") or not seg or "-" not in seg.strip("-"):
            continue
        parts = seg.strip("-").split("-")
        found = None
        for k in range(1, len(parts)):            # longest suffix first; accents ignored
            suf = "-" + "".join(parts[k:])
            # an exact (accented) match wins: oxytone -tós is the verbal adjective, -tos the ablatival
            # adverb suffix (t016 review: 'X-ed' adjectives were glossed as adverbs)
            if suf in exact:
                if suf in ("-s", "-t") and len(parts) != 2:
                    break
                found = exact[suf]
                break
            if _plain(suf) in affixes:
                # -s / -t are root-noun / root-aorist suffixes only on root + suffix;
                # elsewhere they are the nominative or 3sg ending (Hh₃es-eno-s)
                if suf in ("-s", "-t") and len(parts) != 2:
                    break
                found = affixes[_plain(suf)]
                break
        if not found:
            continue
        label = LABELS.get(found["form"]) or LABELS.get(_plain(found["form"])) or \
            found["meaning"][0].split(".")[0].split(";")[0][:60]
        rg = root["meaning"][0].split(";")[0].strip()
        out[e["id"]] = {"gloss": f"{rg} [{found['form']}: {label}]", "root_id": root["id"],
                        "affix_id": found["id"], "source": "derived"}
    return out


def write(root: Path = ROOT) -> int:
    lex = [json.loads(x) for x in (root / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()]
    d = build(lex)
    with (root / "data/lexicon/derived_glosses.jsonl").open("w", encoding="utf-8") as f:
        for k, v in sorted(d.items()):
            f.write(json.dumps({"id": k, **v}, ensure_ascii=False) + "\n")
    return len(d)


# --- Reflex-confirmed glosses (docs/lexicon.md "Reflex-confirmed glosses") ---------------------------------------
#
# A lexeme with no dictionary gloss gets a gloss when the Wiktionary entries of its own reflexes, in at least two
# branches, say the same thing. The evidence is data/lexicon/reflex_glosses.jsonl (scripts/build_reflex_glosses.py:
# the daughters' glosses and the PIE etyma their etymologies cite). Two rules, tried in order:
#   head: a sense of the derived gloss (root meaning + suffix, above) whose content words the reflex glosses
#         repeat in >= 2 branches. The gloss is that sense, so it says no more than the derived gloss did.
#   consensus: else, a content word shared by the reflex glosses of >= 2 branches, all of the lexeme's part of
#         speech; the gloss is the shortest reflex gloss segment that contains it (Gk λούω, Lat. lavō 'wash').
# A reflex counts only if its dictionary entry is linked to this lexeme: its etymology cites the lexeme's form
# (accents and hyphens ignored) or the entry is the only one under that form. Approximate (title-only) matches
# need the etymology link.

BRANCHES = [("Indo-Iranian", r"Sanskrit|Vedic|Avestan|Persian|Pali|Prakrit|Indo-Aryan|Iranian|Hindi|Ossetian|"
             r"Pashto|Khotanese|Sogdian|Bactrian|Kurdish|Parthian|Bengali|Marathi|Punjabi|Nuristani"),
            ("Greek", r"Greek|Hellenic|Mycenaean"), ("Italic", r"Latin|Italic|Oscan|Umbrian|Faliscan"),
            ("Celtic", r"Irish|Welsh|Celtic|Gaulish|Breton|Cornish|Celtiberian|Gaelic|Manx|Brythonic"),
            ("Germanic", r"Germanic|Gothic|Norse|English|German|Saxon|Frisian|Dutch|Icelandic|Swedish|Danish"),
            ("Balto-Slavic", r"Slavic|Slavonic|Lithuanian|Latvian|Prussian|Russian|Polish|Czech|Baltic|Serbo"),
            ("Armenian", r"Armenian"), ("Albanian", r"Albanian"),
            ("Anatolian", r"Hittite|Luwian|Lycian|Palaic|Lydian|Anatolian"), ("Tocharian", r"Tocharian")]


def branch(lang: str) -> str:
    return next((b for b, pat in BRANCHES if re.search(pat, lang)), lang)


_STOP = set("""a an the of to in on at by for from with without into onto upon as or and be is are was being been
one ones someone something thing things kind sort type sorts part also esp especially etc i e eg ie which who that
this these those its it his her their your my our very much more most some any other others certain such same
make made do does doing done get got give have has having become becomes go come put take set let cause causes
used use using usually generally often state act action quality person people man men place time way manner
small large great little big good bad new old form forms name word variant variants alternative sense senses
meaning meanings literally figuratively compare see cf derived from denoting related relating pertaining""".split())


def _words(text: str) -> set[str]:
    text = re.sub(r"\([^)]*\)", " ", text.lower())
    out = set()
    for w in re.findall(r"[a-z]+", text):
        if len(w) < 3 or w in _STOP:
            continue
        out.add(_stem(w))
    return out


def _stem(w: str) -> str:
    for suf in ("ings", "ing", "ies", "ied", "es", "ed", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            if suf in ("ies", "ied"):
                w += "y"
            break
    return w.rstrip("e") if len(w) > 3 else w


def _pie_key(s: str) -> str:
    d = unicodedata.normalize("NFD", s.lstrip("*").replace("-", "").lower())
    return "".join(c for c in d if not unicodedata.combining(c))


def linked_reflexes(entry: dict, rec: dict) -> list[dict]:
    """The reflex dictionary entries linked to the lexeme (see above): [{branch, lang, form, pos, glosses}]."""
    keys = {_pie_key(f) for f in [entry["form"], *entry.get("variants", []), *entry.get("stems", [])] if f}
    out = []
    for r in rec.get("reflexes", []):
        ents = r["entries"]
        for x in ents:
            cites = any(_pie_key(y) in keys for y in x.get("etyma", []))
            alone = len(ents) == 1 and not x.get("approx")
            if cites or alone:
                out.append({"branch": branch(r["lang"]), "lang": r["lang"], "form": r["form"], "pos": x.get("pos"),
                            "glosses": x["glosses"][:3]})
    return out


_POS_OK = {"noun": {"noun", "name"}, "adj": {"adj", "noun", "participle"}, "verb": {"verb"}}


def _senses(head: str) -> list[str]:
    return [s.strip() for s in re.split(r"[;,]\s*", head) if s.strip()]


def confirm(entry: dict, family: str | None, derived: str | None, rec: dict | None) -> dict | None:
    """{"gloss", "rule", "evidence"} for a lexeme without a dictionary gloss, or None (rules above)."""
    if not rec or family not in _POS_OK:
        return None
    refl = linked_reflexes(entry, rec)
    if not refl:
        return None

    def sense_ok(s: str) -> bool:
        return s.startswith("to ") == (family == "verb")

    # head: senses of the derived gloss repeated in >= 2 branches
    if derived:
        head = derived.split(" [", 1)[0].strip()
        kept, ev = [], {}
        for s in _senses(head):
            if not sense_ok(s):
                continue
            sw = _words(s)
            if not sw:
                continue
            hits = [x for x in refl if any(sw & _words(g) for g in x["glosses"])]
            if len({x["branch"] for x in hits}) >= 2:
                kept.append(s)
                for x in hits:
                    ev.setdefault((x["lang"], x["form"]), x)
        if kept:
            return {"gloss": ", ".join(kept), "rule": "head", "evidence": _evidence(ev.values())}
    # consensus: a content word of the primary sense (the first sense of the first gloss) of reflexes in >= 2
    # branches, each of the lexeme's part of speech. A word deep in a long gloss list is not a shared meaning:
    # Gk νέμω 'deal out, ...; enjoy' and Latv. ņemt 'take; ... enjoy' do not make németi 'to enjoy'
    pos_refl = [x for x in refl if x["pos"] in _POS_OK[family]]
    pos_refl = [{**x, "glosses": [_senses(x["glosses"][0])[0]]} for x in pos_refl
                if x["glosses"] and _senses(x["glosses"][0])]
    by_word: dict[str, set[str]] = {}
    for x in pos_refl:
        for w in set().union(*(_words(g) for g in x["glosses"])):
            by_word.setdefault(w, set()).add(x["branch"])
    shared = sorted((w for w, b in by_word.items() if len(b) >= 2), key=lambda w: (-len(by_word[w]), w))
    if not shared:
        return None
    w = shared[0]
    if len(shared) > 1 and len(by_word[shared[1]]) == len(by_word[w]) and not _same_segment(w, shared[1], pos_refl):
        return None          # two unrelated words tie: the daughters do not agree on one sense
    segs = []
    for x in pos_refl:
        for g in x["glosses"]:
            for s in _senses(g):
                if w in _words(s):
                    segs.append(_clean(s))
    segs = [s for s in segs if sense_ok(s)]
    if not segs:
        return None
    gloss = min(segs, key=lambda s: (len(s), s))
    ev = [x for x in pos_refl if any(w in _words(g) for g in x["glosses"])]
    return {"gloss": gloss, "rule": "consensus", "evidence": _evidence(ev)}


def _same_segment(a: str, b: str, refl: list[dict]) -> bool:
    return any({a, b} <= _words(s) for x in refl for g in x["glosses"] for s in _senses(g))


def _clean(s: str) -> str:
    s = re.sub(r"^(a|an|the)\s+", "", s.strip().rstrip("."), flags=re.I)
    return s[:1].lower() + s[1:]


def _evidence(xs) -> list[dict]:
    return [{"lang": x["lang"], "form": x["form"], "gloss": "; ".join(x["glosses"])[:120]} for x in xs][:8]


def write_confirmed(root: Path = ROOT) -> int:
    """data/lexicon/confirmed_glosses.jsonl from lexicon.jsonl, inflection_specs.jsonl, derived_glosses.jsonl and
    reflex_glosses.jsonl. Lexemes with a dictionary gloss are skipped (theirs wins)."""
    rd = lambda p: [json.loads(x) for x in (root / p).read_text("utf-8").splitlines() if x.strip()]
    lex = {e["id"]: e for e in rd("data/lexicon/lexicon.jsonl")}
    fam = {r["id"]: r["family"] for r in rd("data/morph/inflection_specs.jsonl")}
    der = {d["id"]: d["gloss"] for d in rd("data/lexicon/derived_glosses.jsonl")}
    out = []
    for rec in rd("data/lexicon/reflex_glosses.jsonl"):
        e = lex.get(rec["id"])
        if not e or e["meaning"]:
            continue
        c = confirm(e, fam.get(e["id"]), der.get(e["id"]), rec)
        if c:
            out.append({"id": e["id"], "form": e["form"], **c})
    (root / "data/lexicon/confirmed_glosses.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
    return len(out)
