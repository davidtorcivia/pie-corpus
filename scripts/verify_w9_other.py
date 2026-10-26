"""Compare wave9 other corrections against pre-edit snapshots; tables go to /private/tmp.

Never reads or rebuilds Stage C-S review slabs, claims or corpus/export files.
"""
import importlib.util
import json
import re
from pathlib import Path
import sys

from pie import formula_search as fs, formula_search_multi as fm, mapping as mp
from pie import material_units as mu, bsl_mapping as bm, w9_other_mapping as w9

ROOT = Path(__file__).resolve().parents[1]
TMP = Path('/private/tmp/w9-other')
DEST = ROOT/'data/research/8c/stageCS'


def module(stage):
    spec = importlib.util.spec_from_file_location('w9_'+stage, ROOT/'scripts'/f'build_8c_{stage}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def verify():
    sb, sc = module('stageB'), module('stageC')
    loaders = {
        'xcl': lambda: sc.dmhp_tokens(ROOT),
        'grc': lambda: sb.load_glaux_b([r for r in sb.glaux_selection_b()
                  if r['AUTHOR_STANDARD'] in ('Herodotus','Thucydides','Euripides','Pisander')])[0],
        'orv': lambda: sb.load_torot_b(['lav','pvl-hyp'])[0],
        'hom': fs.load_homer,
        'sa-ep': lambda: fm.load_dcs(texts=('Rāmāyaṇa',), corpus='sa-ep'),
    }
    changes, metrics = [], {}
    for c, loader in loaders.items():
        before = [json.loads(l) for l in (TMP/f'{c}-before.jsonl').open()]
        after = [[t.locus,t.surface,t.lemma,t.content,t.pos] for t in loader()]
        assert len(before) == len(after), c
        changed = []
        for a,b in zip(before,after):
            if a == b:
                continue
            assert a[:2] == b[:2] and a[4] == b[4], (c,a,b)
            assert w9.reviewed_lemma(c,a[2],a[1],a[0]) == b[2] != a[2], (c,a,b)
            if a[3] != b[3]:
                assert w9.noncontent(c,b[2],b[1],b[0]) and b[3] is False
            changed.append(dict(corpus=c,before=a,after=b))
        expected = sum(r['corpus']==c for r in w9.ROWS)
        assert len(changed) == expected, (c,len(changed),expected)
        changes += changed
        metrics[c] = dict(tokens=len(after),changed=len(changed),surface_changes=0,coordinate_changes=0)
        if c == 'xcl':
            xcl_tokens = (before, after)
        print(c,metrics[c],flush=True)
    (DEST/'error-verdicts-w9-other-token-diff.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')

    # Disable only this batch's material rules. Compare every surviving unit.
    original = mu.reviewed_ranges
    extra = json.loads((DEST/'material-unit-rules-w9-other.json').read_text())
    all_rules = original()
    for c, loader in [('byliny',bm.byliny_units),('dainos',bm.dainos_units)]:
        mu.reviewed_ranges = lambda: [r for r in all_rules if r not in extra]
        try:
            before = {r[0]:r for r in loader()}
        finally:
            mu.reviewed_ranges = original
        after = {r[0]:r for r in loader()}
        assert not after.keys()-before.keys()
        assert all(after[k] == before[k] for k in after)
        removed = sorted(before.keys()-after.keys())
        expected = []
        for r in extra:
            if r['corpus'] != c:
                continue
            stem = Path(r['source']).stem.replace('_djvu', '')
            if c == 'dainos':
                stem = re.sub(r'[^A-Za-z0-9]+', '-', stem).strip('-')
            expected.append(f"{stem}:{r['start']}")
        assert removed == sorted(expected), (c,removed,expected)
        metrics[c+'-material'] = dict(before=len(before),after=len(after),removed=removed,retained_changes=0)
        print(c+'-material',len(removed),'removed; retained changes 0',flush=True)

    edits = json.loads((ROOT/'data/research/formulas/mapping-overrides/w9-other.json').read_text())['lemma']
    corpora = sorted({r['corpus'] for r in edits})
    original_files = mp.override_files
    try:
        mp.override_files = lambda root: [p for p in original_files(root) if p.name != 'w9-other.json']
        mp._OVR_CACHE.clear()
        before = {c:mp.resolve_table(c) for c in corpora}
    finally:
        mp.override_files = original_files
        mp._OVR_CACHE.clear()
    diff = {}
    (TMP/'resolved').mkdir(exist_ok=True)
    for c in corpora:
        after = mp.resolve_table(c)
        if c == 'xcl':
            token_diff = []
            for a,b in zip(*xcl_tokens):
                ai = sorted(before[c][a[2]].ids) if a[3] and a[2] in before[c] else []
                bi = sorted(after[b[2]].ids) if b[3] and b[2] in after else []
                if a == b and ai == bi:
                    continue
                if a == b:
                    assert a[2] in {r['lemma'] for r in edits if r['corpus']==c}
                token_diff.append(dict(locus=a[0],surface=a[1],
                                       before=dict(lemma=a[2],content=a[3],lex_id=ai),
                                       after=dict(lemma=b[2],content=b[3],lex_id=bi)))
            (DEST/'error-verdicts-w9-other-xcl-token-diff.json').write_text(
                json.dumps(token_diff,ensure_ascii=False,indent=2)+'\n')
            metrics['xcl']['changed_including_mapping'] = len(token_diff)
        rows = []
        for k in before[c].keys() | after.keys():
            a = sorted(before[c][k].ids) if k in before[c] else []
            b = sorted(after[k].ids) if k in after else []
            if a != b:
                rows.append(dict(lemma=k,before=a,after=b))
        assert {r['lemma'] for r in rows} <= {r['lemma'] for r in edits if r['corpus']==c}
        diff[c] = sorted(rows,key=lambda r:r['lemma'])
        (TMP/'resolved'/f'{c}.jsonl').write_text(''.join(json.dumps(dict(lemma=k,lex_id=sorted(v.ids)),ensure_ascii=False)+'\n' for k,v in sorted(after.items())))
    (DEST/'error-verdicts-w9-other-table-diff.json').write_text(json.dumps(diff,ensure_ascii=False,indent=2)+'\n')
    (DEST/'error-verdicts-w9-other-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    print('All token, unit and resolved-table differences are declared.',flush=True)


if __name__ == '__main__':
    verify()
