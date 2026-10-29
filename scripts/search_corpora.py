#!/usr/bin/env python3
"""Search every unit exposed by the 8c Stage C/C-S loaders, including excluded layers.

Build (local corpus text; never commit or redistribute the index/cache):
  uv run python -I scripts/search_corpora.py --build --cache-dir data/research/8c/search-index/cache
Search (repeat --root for AND; an exact lexicon ID or group-map value):
  uv run python -I scripts/search_corpora.py --root pie-lex-gjonu --root pie-root-swep-sleep --near 8
  uv run python -I scripts/search_corpora.py --root pie-lex-dngjhweh2s --root pie-lex-kjmtom --branch Celtic --count
  uv run python -I scripts/search_corpora.py --root "kaikki:glogʰs" --root pie-lex-dekjm --branch Greek --count
  uv run python -I scripts/search_corpora.py --lemma tengae --context 1 --json
  uv run python -I scripts/search_corpora.py --form 'γλῶσσ' --branch Greek --count

--near N means max minus min content-word position <= N on distinct words in
one loader unit (adjacent words have distance 1). Unmapped content words count.
--lemma is exact/case-sensitive; --form is a case-sensitive Python regex on
content-word forms, not running text. Repeated lemma/root filters are AND;
repeated corpus/branch filters are OR. Context is neighbouring loader units in
the same corpus/book; it does not widen root co-occurrence. --count ignores
--limit and emits only the total. JSON output is JSONL. Layer flags describe
eligibility, not evidence of inheritance. Mappings are automatic and fallible.
The loaders' own deduplication, corpus exclusions and windowing still apply.
Rebuild with a fresh cache directory after changing source data or mappings.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sqlite3
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie.corpus_index import CorpusIndex, build_index

DEFAULT = ROOT / "data/research/8c/search-index/corpora.sqlite"


def build(path, cache_dir):
    # Trusted project code only. In particular never load a pickle under raw/.
    if cache_dir is not None and Path(cache_dir).resolve().is_relative_to(ROOT / "raw"):
        raise ValueError("cache directory must not be under raw/")
    spec = importlib.util.spec_from_file_location("build_8c_stageCS_search", ROOT / "scripts/build_8c_stageCS.py")
    stage = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = stage
    spec.loader.exec_module(stage)
    log = lambda *a: print(*a, file=sys.stderr, flush=True)
    units, by_id, meta, _ = stage.C.load_all(ROOT, cache_dir, include_ccmh=True, log=log)
    classes, thin = stage.prepare(units, by_id, meta, cache_dir, log)
    classifier = stage.Classifier(ROOT, meta)
    from pie.formula_search import group_map, load_jsonl
    from pie import compound_members as cmem
    from pie.material_units import same_work
    groups = group_map(load_jsonl(ROOT / "data/lexicon/lexicon.jsonl"))
    # corpus-quality batch 2: compound members (pie/compound_members.py), resolved against the loaders'
    # own lemma ids of each language; DCS verse citations (the sentence index in the locus is no verse)
    pairs = {}
    for corpus, rows in units.items():
        lang = cmem.CORPUS_LANG.get(corpus)
        if lang:
            pairs.setdefault(lang, []).extend((l, ids) for unit in rows for _, l, ids in unit.words)
    lemma_ids = {lang: cmem.lemma_id_table(lang, ps) for lang, ps in pairs.items()}
    cites = dcs_citations(stage.C.DCS_EPIC)

    def word(corpus, f, l, ids):
        w = dict(form=f, lemma=l, root_ids=list(ids), root_groups=sorted({groups.get(r, r) for r in ids}))
        lang = cmem.CORPUS_LANG.get(corpus)
        m = sorted(cmem.members(corpus, l, lemma_ids[lang]) - set(ids)) if lang in lemma_ids else []
        if m:
            w["member_ids"] = m
            w["member_groups"] = sorted({groups.get(r, r) for r in m} - set(w["root_groups"]))
        return w

    def records():
        for corpus, rows in units.items():
            for ordinal, unit in enumerate(rows):
                metadata = meta.get(unit.key.split("~w")[0], {}) if corpus in stage.C.CELTIC else {}
                greek = classifier.glaux.get(str(unit.book), {}) if corpus in ("grc", "grc-late") else {}
                mask = classes[corpus][ordinal]
                extra = {}
                cite = cites.get((corpus, unit.key.split("~w")[0]))
                if cite:
                    extra["cite"], extra["cite_status"] = cite
                work = same_work(corpus, unit.key)
                if work:
                    extra["work"] = work
                yield dict(corpus=corpus, branch=stage.SB.CORPORA[corpus][0],
                           key=unit.key, locus=unit.locus, book=str(unit.book), ordinal=ordinal,
                           emendations=unit.emendations, **extra,
                           text=unit.text, words=[word(corpus, f, l, ids) for f, l, ids in unit.words],
                           root_ids=sorted({r for _, _, ids in unit.words for r in ids}),
                           root_groups=sorted(unit.groups), licence_tag=unit.tag,
                           licence=unit.licence, research_only=unit.research_only,
                           date_from=metadata.get("date_from", greek.get("STARTDATE")),
                           date_to=metadata.get("date_to", greek.get("ENDDATE")),
                           genre=metadata.get("genre", greek.get("GENRE_STANDARD")),
                           class_mask=mask, main_class_mask=classifier(corpus, unit),
                           layer_status="included" if mask else "excluded", thin_corpus=corpus in thin)
    return build_index(path, records())


def dcs_citations(epic_texts) -> dict:
    """(corpus, DCS unit key 'chapter|sent_id') -> (verse citation, status) for av and sa-ep: the token-level
    citation of pie.formula_search_multi.dcs_assign_verses ('AVŚ 3.16.3cd'; status counter | bracketed |
    inferred). A DCS locus 'AVŚ, 3, 16.s6' is a sentence index, not a stanza (Tier 2 round-3 drafter)."""
    from pie import formula_search_multi as fm
    out = {}
    for corpus, texts in (("av", fm.DCS_VEDIC), ("sa-ep", epic_texts)):
        for t in fm.load_dcs(texts=texts, corpus=corpus, root=ROOT):
            if t.units.get("cite") and t.units.get("verse_status") != "unmapped":
                out.setdefault((corpus, t.units["sentence"]), (t.units["cite"], t.units["verse_status"]))
    return out


def reading_flags(record):
    return "".join(f" [emended {a['form']}; source: {a['source_reading'] or 'unspecified'}]"
                   for a in record.get("emendations", []))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true", help="build index only; no packets, tiers or export")
    ap.add_argument("--index", type=Path, default=DEFAULT)
    ap.add_argument("--cache-dir", type=Path, help="trusted loader pickle cache (use a fresh directory after mapping changes)")
    ap.add_argument("--root", action="append", default=[], metavar="ID_OR_GROUP")
    ap.add_argument("--near", type=int)
    ap.add_argument("--lemma", action="append", default=[])
    ap.add_argument("--form", metavar="REGEX")
    for name in ("corpus", "branch", "not-corpus"):
        ap.add_argument("--" + name, action="append", default=[])
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--context", type=int, default=0)
    output = ap.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="JSONL with complete word and layer metadata")
    output.add_argument("--text", action="store_true", help="text with loci (default)")
    ap.add_argument("--count", action="store_true", help="print total hit count only, ignoring limit/context")
    args = ap.parse_args(argv)
    try:
        if args.build:
            start = time.perf_counter()
            count = build(args.index, args.cache_dir)
            print(json.dumps(dict(units=count, seconds=round(time.perf_counter()-start, 3), bytes=args.index.stat().st_size)))
            return 0
        index = CorpusIndex(args.index)
        try:
            hits = index.search(roots=args.root, near=args.near, lemmas=args.lemma, form=args.form,
                                corpora=args.corpus, branches=args.branch, not_corpora=args.not_corpus,
                                limit=None if args.count else args.limit, context=0 if args.count else args.context)
            if args.count:
                print(sum(1 for _ in hits))
            else:
                for hit in hits:
                    if args.json:
                        print(json.dumps(hit, ensure_ascii=False))
                    else:
                        cite = f" [{hit['cite']}]" if hit.get("cite") else ""
                        print(f"{hit['corpus']} | {hit['locus']}{cite} | {hit['layer_status']} | {hit['licence_tag']}: {hit['text']}{reading_flags(hit)}")
                        for neighbour in hit.get("context", []):
                            print(f"  {neighbour['locus']}: {neighbour['text']}{reading_flags(neighbour)}")
        finally:
            index.close()
    except (ValueError, re.error, sqlite3.Error, OSError) as exc:
        ap.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
