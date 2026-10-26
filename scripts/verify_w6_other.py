"""Wave 6 whole-corpus token snapshots; writes only /private/tmp by default."""
import importlib.util
import gzip
import json
import sys
import itertools
import difflib
from pathlib import Path
from pie import formula_search as fs, formula_search_multi as fm, bsl_mapping as bm

ROOT = Path(__file__).resolve().parents[1]


def stageb():
    spec = importlib.util.spec_from_file_location('w6_stageb', ROOT/'scripts/build_8c_stageB.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def late_greek():
    """Reconstruct the pre-wave6 loader by disabling only this worker's hooks."""
    from pie import w6_other_mapping as w6
    spec=importlib.util.spec_from_file_location('w6_stagec',ROOT/'scripts/build_8c_stageC.py')
    sc=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sc;spec.loader.exec_module(sc)
    sel=sc.glaux_late_selection(ROOT)
    original=(w6.annotated_name,w6.reviewed_lemma)
    for label in ('before','after'):
        if label=='before':
            w6.annotated_name=lambda *a:False
            w6.reviewed_lemma=lambda c,l,s,p:l
        try:
            p=Path('/private/tmp/w6-other')/label/'grc-late.jsonl'
            n=0
            with p.open('w') as out:
                for row in sel:
                    ts,_=sc.SB.load_glaux_b([row],ROOT)
                    for t in ts:
                        out.write(json.dumps([t.locus,t.surface,t.lemma,t.content,t.pos],ensure_ascii=False)+'\n');n+=1
            print(label,'grc-late',n,flush=True)
        finally:
            w6.annotated_name,w6.reviewed_lemma=original


def snapshot(label):
    out = Path('/private/tmp/w6-other') / label
    out.mkdir(parents=True, exist_ok=True)
    sb = stageb()
    def save(c, rows):
        with (out/f'{c}.jsonl').open('w') as f:
            n=0
            for row in rows:
                f.write(json.dumps(row,ensure_ascii=False)+'\n'); n+=1
        print(c,n,flush=True)
    def tokens(ts):
        return ([t.locus,t.surface,t.lemma,t.content,t.pos] for t in ts)
    save('grc',tokens(sb.load_glaux_b(sb.glaux_selection_b())[0]))
    save('hom',tokens(fs.load_homer()))
    save('orv',tokens(sb.load_torot_b(sb.ORV_TEXTS)[0]))
    save('lat',tokens(fs.load_latin()))
    save('av',tokens(fm.load_dcs()))
    save('sa-ep',tokens(fm.load_dcs(texts=('Mahābhārata','Rāmāyaṇa'),corpus='sa-ep')))
    maps=bm.build_mappings(langs=('sh','ru','lt'))
    bm.add_derksen_lt(maps.lt,bm.derksen_index(),fm.FuzzyPie(maps.lexicon))
    for c in ('vuk','byliny','dainos'):
        lz=bm.lemmatizer(c,maps)
        lm={'vuk':maps.sh,'byliny':maps.ru,'dainos':maps.lt}[c]
        def rows():
            for loc,u,text in bm.UNITS[c]():
                for i,w in enumerate(bm.corpus_words(c,text)):
                    lem=lz(w)
                    content=lm.is_content(lem) and not (lem.startswith('?') and len(lem)<3)
                    if content and bm.is_name(c,w,i): lem+=' (name)'
                    t=fs.Token(c,lem,w,loc,u,content,'noun')
                    yield [loc,w,t.lemma,t.content,t.pos]
        save(c,rows())


def compare():
    """Ordered whole-corpus comparisons; no corpus or slab regeneration."""
    base=Path('/private/tmp/w6-other')
    totals={}
    changes=[]
    from pie.material_units import reviewed_ranges, dainos_interleaved, reviewed_vuk_material
    allowed = set()
    import re
    for r in reviewed_ranges():
        if r['corpus'] not in {'byliny','dainos'}:continue
        stem=Path(r['source']).stem.replace('_djvu','')
        if r['corpus']=='dainos':stem=re.sub('[^A-Za-z0-9]+','-',stem).strip('-')
        allowed.update((r['corpus'],f'{stem}:{n}') for n in range(r['start'],r['end']+1))
    p=ROOT/bm.KD/'lithuanian-juskevic-dainos-1880-1883/Lietuviškos svotbinės dainos, 1883_djvu.txt'
    allowed.update(('dainos',f'Lietuvi-kos-svotbin-s-dainos-1883:{i+1}') for i in dainos_interleaved(p.read_text().splitlines()))
    def read(p):
        with p.open() as f:
            yield from (json.loads(l) for l in f)
    for p in sorted((base/'before').glob('*.jsonl')):
        c=p.stem
        a,b=read(p),read(base/'after'/p.name)
        nold=nnew=changed=removed=added=0
        if c not in {'vuk','byliny','dainos'}:
            for old,new in itertools.zip_longest(a,b):
                assert old is not None and new is not None
                nold+=1; nnew+=1
                if old!=new:
                    changed+=1; changes.append(dict(corpus=c,before=old,after=new))
        else:
            ga=((loc,list(rows)) for loc,rows in itertools.groupby(a,key=lambda r:r[0]))
            gb=iter((loc,list(rows)) for loc,rows in itertools.groupby(b,key=lambda r:r[0]))
            current=next(gb,None)
            for loc,old in ga:
                nold+=len(old)
                if current is None or current[0]!=loc:
                    if c=='vuk':
                        page,n=loc.removeprefix('Vuk ').split(':')
                        assert reviewed_vuk_material(page,int(n)),loc
                    else:
                        assert (c,loc) in allowed,(c,loc)
                    removed+=len(old)
                    changes.append(dict(corpus=c,locus=loc,removed_tokens=len(old)))
                    continue
                new=current[1];nnew+=len(new);current=next(gb,None)
                if old==new:continue
                matcher=difflib.SequenceMatcher(a=[tuple(r) for r in old],b=[tuple(r) for r in new],autojunk=False)
                for op,i,j,k,l in matcher.get_opcodes():
                    if op=='equal':continue
                    changed+=min(j-i,l-k);removed+=max(0,(j-i)-(l-k));added+=max(0,(l-k)-(j-i))
                    changes.append(dict(corpus=c,locus=loc,before=old[i:j],after=new[k:l]))
            assert current is None, (c,current[0])
        totals[c]=dict(before_tokens=nold,after_tokens=nnew,changed_tokens=changed,removed_tokens=removed,added_tokens=added)
    dest=ROOT/'data/research/8c/stageCS'
    with gzip.open(dest/'error-verdicts-w6-other-token-diff.jsonl.gz', 'wt', encoding='utf-8') as f:  # ~66 MB uncompressed
        f.write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in changes))
    (dest/'error-verdicts-w6-other-metrics.json').write_text(json.dumps(totals,indent=2)+'\n')
    from collections import Counter
    counts=Counter()
    for r in changes:
        c=r['corpus']
        if c not in {'byliny','vuk','dainos'}:
            a,b=r['before'],r['after']
            if b[4]=='name':counts[c+': source/dictionary names']+=1
            elif b[2]=='εἶδον@see':counts[c+': suppletive see']+=1
            elif b[2]=='εἴρω@speak':counts[c+': suppletive speak']+=1
            elif b[2]=='поити@go':counts[c+': source homonym go']+=1
            elif c=='hom' and a[0]!=b[0]:counts[c+': locus repair']+=1
        if c=='byliny' and 'before' in r:
            for b in r['after']:
                if '$' in b[1]:counts['byliny: restored dollar words (includes one reviewed space repair)']+=1
                elif b[1]=='очушкахъ':counts['byliny: diminutive eyes']+=1
        if c=='dainos' and 'removed_tokens' in r:
            kind='reviewed editorial' if r['locus'] in {'litauischevolksl00leskuoft:266','lietvikosdjnos00iugoog:32055','Lietuvi-kos-svotbin-s-dainos-1883:923'} else 'interleaved columns'
            counts[f'dainos: {kind} tokens excluded']+=r['removed_tokens']
            counts[f'dainos: {kind} units excluded']+=1
    (dest/'error-verdicts-w6-other-rule-counts.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(json.dumps(totals,indent=2))


def table_diff():
    from pie import mapping as mp
    edits=json.loads((ROOT/'data/research/formulas/mapping-overrides/w6-other.json').read_text())
    corpora=sorted({r['corpus'] for r in edits['lemma']})
    original=mp.override_files
    try:
        mp.override_files=lambda root:[p for p in original(root) if p.name!='w6-other.json']
        mp._OVR_CACHE.clear()
        before={c:mp.resolve_table(c) for c in corpora}
    finally:
        mp.override_files=original
        mp._OVR_CACHE.clear()
    changes={}
    out=Path('/private/tmp/w6-other/resolved');out.mkdir(exist_ok=True)
    for c in corpora:
        after=mp.resolve_table(c)
        dif=[]
        for k in before[c].keys()|after.keys():
            a=sorted(before[c][k].ids) if k in before[c] else []
            b=sorted(after[k].ids) if k in after else []
            if a!=b:dif.append(dict(lemma=k,before=a,after=b))
        assert {r['lemma'] for r in dif}<={r['lemma'] for r in edits['lemma'] if r['corpus']==c}
        changes[c]=sorted(dif,key=lambda r:r['lemma'])
        (out/f'{c}.jsonl').write_text(''.join(json.dumps(dict(lemma=k,lex_id=sorted(v.ids)),ensure_ascii=False)+'\n' for k,v in sorted(after.items())))
    (ROOT/'data/research/8c/stageCS/error-verdicts-w6-other-table-diff.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
    print('Only declared override rows changed:',sum(map(len,changes.values())))


if __name__=='__main__':
    if sys.argv[1]=='compare':compare();table_diff()
    elif sys.argv[1]=='late':late_greek()
    else:snapshot(sys.argv[1])
