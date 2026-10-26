#!/usr/bin/env python3
"""Reproduce wave5 pairs in a temporary index; never writes corpora or slabs.

uv run python -I scripts/verify_w5_other.py
uv run python -I scripts/collocates_8c.py --db /private/tmp/fix5-pairs.sqlite \
  --target pie-lex-pekju,pie-lex-pekju-2 --pair pie-lex-wiHros --window 4
"""
import importlib.util
import json
from pathlib import Path

from pie import formula_search as fs, formula_search_multi as fm, mapping as mp
from pie.corpus_index import build_index

ROOT = Path(__file__).resolve().parents[1]


def pairs(path=Path('/private/tmp/fix5-pairs.sqlite')):
    spec = importlib.util.spec_from_file_location('stagec_w5_check', ROOT/'scripts/build_8c_stageC.py')
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    lex = fs.load_jsonl(ROOT/'data/lexicon/lexicon.jsonl')
    protos = fm.ProtoDB(root=ROOT, want_desc=['ae','xum'])
    records, hits = [], {}
    for corpus in ('ae','xum'):
        lm = fm.build_lang_mapping(corpus,lex,protos,root=ROOT)
        if corpus == 'ae':
            lem = fm.AvestanLemmatizer(lm,{})
            units = fm.avesta_units(ROOT)
            key = 'ab'
        else:
            lem = fm.FormLemmatizer(lm)
            units = fm.umbrian_lines({fs.lat_key(t.surface) for t in fs.load_latin(ROOT)},ROOT)
            key = 'line'
        tokens = fm.text_tokens(corpus,units,lem,lm.is_content)
        mapping = {k:tuple(v.ids) for k,v in mp.resolve_table(corpus).items()}
        surfaces = [w for _,_,text in units for w in (fm._WORDS.findall(text) if isinstance(text,str) else text)]
        actual = sc.SB.units_from_tokens(corpus,tokens,key,lambda t:t.units['book'],surfaces,mapping,
                                        lambda t:('source; temporary verification only',True))
        hits[corpus] = []
        for i,u in enumerate(actual):
            words = [dict(form=f,lemma=l,root_ids=list(ids),root_groups=[]) for f,l,ids in u.words]
            records.append(dict(corpus=corpus,branch='Italic' if corpus=='xum' else 'Indo-Iranian',
                                book=u.book,ordinal=i,locus=u.locus,text=u.text,words=words))
            cattle = [j for j,w in enumerate(words) if 'pie-lex-pekju' in w['root_ids']]
            men = [j for j,w in enumerate(words) if 'pie-lex-wiHros' in w['root_ids']]
            if any(abs(a-b)<=4 for a in cattle for b in men):
                hits[corpus].append(u.locus)
    return dict(index=str(path),units=build_index(path,records),pair_loci=hits)


def table_diff():
    """Regenerate resolved snapshots into tmp; assert only declared rows change."""
    edits=json.loads((ROOT/'data/research/formulas/mapping-overrides/w5-other.json').read_text())
    corpora=sorted({r['corpus'] for r in edits['lemma']})
    original=mp.override_files
    try:
        mp.override_files=lambda root:[p for p in original(root) if p.name!='w5-other.json']
        mp._OVR_CACHE.clear()
        before={c:mp.resolve_table(c) for c in corpora}
    finally:
        mp.override_files=original
        mp._OVR_CACHE.clear()
    changes={}
    out=Path('/private/tmp/fix5-resolved-tables')
    out.mkdir(exist_ok=True)
    for c in corpora:
        after=mp.resolve_table(c)
        dif=[]
        for key in before[c].keys()|after.keys():
            a=sorted(before[c][key].ids) if key in before[c] else []
            b=sorted(after[key].ids) if key in after else []
            if a!=b:
                dif.append(dict(lemma=key,before=a,after=b))
        assert {r['lemma'] for r in dif}<={r['lemma'] for r in edits['lemma'] if r['corpus']==c}
        changes[c]=sorted(dif,key=lambda d:d['lemma'])
        (out/f'{c}.jsonl').write_text(''.join(json.dumps(dict(lemma=k,lex_id=sorted(v.ids)),ensure_ascii=False)+'\n' for k,v in sorted(after.items())))
    return changes


if __name__ == "__main__":
    print(json.dumps(dict(pairs=pairs(),table_diff=table_diff()),ensure_ascii=False,indent=2))
