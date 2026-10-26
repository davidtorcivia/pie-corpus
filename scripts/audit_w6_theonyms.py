"""Snapshot/compare complete affected corpora, without building corpus artifacts.

uv run python -I scripts/audit_w6_theonyms.py before /tmp/w6-theonyms
uv run python -I scripts/audit_w6_theonyms.py after /tmp/w6-theonyms
Only lemmas, individual forms and loci are reported; no running text.
"""
import collections
import gzip
import importlib.util
import json
from pathlib import Path
import random
import sys

from pie import formula_search as fs, formula_search_multi as fm
from pie import germanic_new_mapping as gm

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('theonyms_stage_c', ROOT / 'scripts/build_8c_stageC.py')
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)
sb = sc.SB


def corpora():
    yield 'hom', fs.load_homer
    yield 'lat', fs.load_latin
    yield 'av', lambda: fm.load_dcs(texts=fm.DCS_VEDIC[:2])
    yield 'sa-ep', lambda: fm.load_dcs(texts=sc.DCS_EPIC, corpus='sa-ep')
    yield 'grc', lambda: sb.load_glaux_b(sb.glaux_selection_b())[0]
    yield 'grc-late', lambda: sb.load_glaux_b(sc.glaux_late_selection(ROOT))[0]
    yield 'grp', fm.load_glaux
    yield 'orv', lambda: sb.load_torot_b(sb.ORV_TEXTS)[0]
    yield 'menota', gm.load_menota
    yield 'icepahc', gm.load_icepahc


def mapping(c, ts, lex):
    if c in {'hom', 'lat', 'grc', 'grc-late', 'grp', 'sa-ep'}:
        lang = 'la' if c == 'lat' else 'sa' if c == 'sa-ep' else 'grc'
        back = (fs.build_latin_mapping(lex, ts) if c == 'lat' else
                fs.build_homer_mapping(lex, ts) if lang == 'grc' else None)
        pop = 'grp' if c in {'grc', 'grc-late'} else 'av' if c == 'sa-ep' else c
        result = sb.live(pop, lang, ts, back, lex, fs.group_map(lex))
        if c == 'sa-ep':
            result.update(sb.B._table('av'))
        return result
    if c == 'orv':
        from pie.name_mapping import orv_mapping
        return orv_mapping(ts)[0]
    return sb.B._table(c)


def main():
    mode, directory = sys.argv[1:3]
    selected = set(sys.argv[3:])
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if mode == 'before':
        # Reproduce pre-fix behavior for repeatable baseline snapshots.
        from pie import name_mapping as nm
        nm.name_lemma = lambda corpus, lemma: lemma if lemma.endswith(' (name)') else lemma + ' (name)'
        def before_post_init(t):
            # Exact pre-fix Token hook, with Latin's old PROPN-to-noun tag.
            from pie.w6_other_mapping import annotated_name
            if t.corpus == 'lat' and t.pos == 'name':
                t.pos = 'noun'
            if annotated_name(t.corpus, t.lemma, t.pos):
                if not t.lemma.endswith(' (name)'):
                    t.lemma += ' (name)'
                t.content, t.pos = False, 'name'
            t.lemma = fs.contextual_lemma(t.corpus, t.lemma, t.surface, t.locus)
            if t.corpus == 'vuk' and t.lemma == 'more@sea':
                t.content, t.pos = True, 'noun'
            if t.lemma.endswith(('@conjunction', '@preposition', '@interrogative')):
                t.content, t.pos = False, 'other'
            if t.corpus == 'xcl' and t.lemma == '34@numeral':
                t.content, t.pos = False, 'other'
        fs.Token.__post_init__ = before_post_init
    lex = fs.load_jsonl(ROOT / 'data/lexicon/lexicon.jsonl')
    report = {'seed': 6026, 'scope': 'All tokens of all ten affected production loader populations; grp is the earlier poetry selection and overlaps grc.', 'corpora': {}}
    if mode == 'after' and selected:
        report = json.loads((directory / 'diff.json').read_text())
    for c, loader in corpora():
        if selected and c not in selected:
            continue
        if mode == 'before' and (directory / (c + '.jsonl.gz')).exists():
            continue
        ts = loader()
        mp = mapping(c, ts, lex)
        path = directory / (c + '.jsonl.gz')
        def row(t):
            return [t.lemma, t.content, t.pos, sorted(mp.get(t.lemma, ())) if t.content else [], t.locus, t.surface]
        if mode == 'before':
            with gzip.open(path, 'wt', encoding='utf-8') as f:
                for t in ts:
                    f.write(json.dumps(row(t), ensure_ascii=False) + '\n')
            print(c, len(ts), 'snapshotted', flush=True)
            continue
        regained, lost, changed = [], [], 0
        categories = collections.Counter()
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            for i, t in enumerate(ts):
                old = json.loads(next(f))
                new = row(t)
                assert old[4:] == new[4:], (c, i, 'alignment changed')
                if old[:4] != new[:4]:
                    changed += 1
                    categories['lemma'] += old[0] != new[0]
                    categories['content'] += old[1] != new[1]
                    categories['pos'] += old[2] != new[2]
                    categories['roots'] += old[3] != new[3]
                    if old[3] and not new[3]:
                        lost.append({'index': i, 'lemma': t.lemma, 'form': t.surface, 'locus': t.locus,
                                     'before': old[:4], 'after': new[:4]})
                    if not old[3] and new[3]:
                        regained.append({'index': i, 'lemma': t.lemma, 'form': t.surface, 'locus': t.locus,
                                         'before': old[:4], 'after': new[:4]})
            assert not f.read(), (c, 'token count changed')
        freq = collections.Counter(r['lemma'] for r in regained)
        report['corpora'][c] = {'tokens': len(ts), 'changed_tokens': changed, 'regained_tokens': len(regained),
                                'change_categories': dict(categories), 'lost_roots_tokens': len(lost),
                                'lost_roots_sample_30': random.Random(6026).sample(lost, min(30, len(lost))),
                                'regained_lemma_counts': dict(freq.most_common()),
                                'top_40': freq.most_common(40),
                                'sample_30': random.Random(6026).sample(regained, min(30, len(regained)))}
        print(c, len(ts), 'changed', changed, 'regained', len(regained), flush=True)
    if mode == 'after':
        (directory / 'diff.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
