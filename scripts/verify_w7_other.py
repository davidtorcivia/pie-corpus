"""Wave7 other/material verification; all regenerated tables stay in /private/tmp.

Run after taking pre-edit token snapshots (see docs/research/w7-other-fixes.txt).
Never constructs or reads Stage C-S slabs, claims, or corpus/export records.
"""
from pathlib import Path
import importlib.util
import json
import sys
from pie import formula_search as fs, formula_search_multi as fm, mapping as mp
from pie import material_units as mu, bsl_mapping as bm, w7_other_mapping as w7

ROOT = Path(__file__).resolve().parents[1]
TMP = Path('/private/tmp/w7-other')
DEST = ROOT / 'data/research/8c/stageCS'


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'build_8c_{name}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def verify():
    sb, sc = module('stageB'), module('stageC')
    loaders = {
        'grc': lambda: sb.load_glaux_b([r for r in sb.glaux_selection_b() if r['AUTHOR_STANDARD'] in
                                      ('Herodotus', 'Hesiodus', 'Thucydides', 'Euripides')])[0],
        'hom': fs.load_homer,
        'lat': fs.load_latin,
        'orv': lambda: sb.load_torot_b(['spi','lav'])[0],
        'av': fm.load_dcs,
        'sa-ep': lambda: fm.load_dcs(texts=('Mahābhārata','Rāmāyaṇa'),corpus='sa-ep'),
        'xcl': lambda: sc.dmhp_tokens(ROOT),
    }
    metrics, changes = {}, []
    for c, loader in loaders.items():
        after = [[t.locus,t.surface,t.lemma,t.content,t.pos] for t in loader()]
        before = [json.loads(l) for l in (TMP/f'{c}-before.jsonl').open()]
        assert len(before) == len(after), c
        n = 0
        for a,b in zip(before,after):
            if a == b:
                continue
            assert a[:2] == b[:2] and a[4] == b[4], (c,a,b)
            assert w7.reviewed_lemma(c,a[2],a[1],a[0]) == b[2] != a[2], (c,a,b)
            if a[3] != b[3]:
                assert b[2].endswith(' (name)') and b[3] is False, (c,a,b)
            n += 1
            changes.append(dict(corpus=c,before=a,after=b))
        metrics[c] = dict(tokens=len(after),changed=n)
        print(c,metrics[c],flush=True)
    (DEST/'error-verdicts-w7-other-token-diff.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')

    # Material comparisons use real unit loaders with only this batch disabled.
    original = mu.reviewed_ranges
    extra = json.loads((DEST/'material-unit-rules-w7-other.json').read_text())
    all_rules = original()
    mu.reviewed_ranges = lambda: [r for r in all_rules if r not in extra]
    try:
        before_by = list(bm.byliny_units())
        before_ce = sc.celtic_rows(ROOT,None,{})
    finally:
        mu.reviewed_ranges = original
    after_by = list(bm.byliny_units())
    after_ce = sc.celtic_rows(ROOT,None,{})
    for c,a,b,key in [('byliny',before_by,after_by,lambda r:r[0]),
                       ('celtic',before_ce,after_ce,lambda r:r['id'])]:
        aa,bb = {key(r):r for r in a},{key(r):r for r in b}
        removed = sorted(aa.keys()-bb.keys())
        assert not bb.keys()-aa.keys()
        assert all(aa[k] == bb[k] for k in bb)
        expected = (['pesnisobrannyepnrybnikovymch3narod26:34987'] if c=='byliny' else [
            'oldirish-meyer-editions-1892-1919:berdielteste00meyeuoft:L6500-L6500',
            'celtic-journal-eriu-1904-1928:eriu_1912_6:L7994-L7995',
            'celtic-journal-eriu-1904-1928:eriu_1912_6:L7995-L7995',
            'celtic-journal-revue-celtique-1870-1928:revueceltique13pari:L22538-L22539'])
        assert removed == sorted(expected),(c,removed)
        metrics[c+'-material'] = dict(before=len(a),after=len(b),removed=removed,retained_changes=0)
        print(c+'-material',metrics[c+'-material'],flush=True)

    edits=json.loads((ROOT/'data/research/formulas/mapping-overrides/w7-other.json').read_text())
    corpora=sorted({r['corpus'] for r in edits['lemma']})
    original_files=mp.override_files
    try:
        mp.override_files=lambda root:[p for p in original_files(root) if p.name!='w7-other.json']
        mp._OVR_CACHE.clear()
        before={c:mp.resolve_table(c) for c in corpora}
    finally:
        mp.override_files=original_files
        mp._OVR_CACHE.clear()
    table_diff={}
    (TMP/'resolved').mkdir(exist_ok=True)
    for c in corpora:
        after=mp.resolve_table(c)
        diff=[]
        for k in before[c].keys()|after.keys():
            a=sorted(before[c][k].ids) if k in before[c] else []
            b=sorted(after[k].ids) if k in after else []
            if a!=b:diff.append(dict(lemma=k,before=a,after=b))
        assert {r['lemma'] for r in diff}<={r['lemma'] for r in edits['lemma'] if r['corpus']==c}
        table_diff[c]=sorted(diff,key=lambda r:r['lemma'])
        (TMP/'resolved'/f'{c}.jsonl').write_text(''.join(json.dumps(dict(lemma=k,lex_id=sorted(v.ids)),ensure_ascii=False)+'\n' for k,v in sorted(after.items())))
    (DEST/'error-verdicts-w7-other-table-diff.json').write_text(json.dumps(table_diff,ensure_ascii=False,indent=2)+'\n')
    (DEST/'error-verdicts-w7-other-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    print('All changed tokens, units and table rows are declared.',flush=True)


if __name__ == '__main__':
    verify()
