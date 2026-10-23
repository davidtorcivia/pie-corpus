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
