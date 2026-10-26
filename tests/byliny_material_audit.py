"""Read-only detector audit. Run with uv run python -I tests/byliny_material_audit.py.

Batch 1 is calibration; entire batch-2 spans (not adjacent individual lines)
are held out. Negatives are manually checked epic/lyric verse from a seeded
sample of the OLD candidate population, never selected by the new detector.
No raw code is imported. Output goes to /private/tmp, never corpus or slabs.
"""
import json
import random
from collections import Counter
from pathlib import Path

from pie.bsl_mapping import BYLINY_OCR, KD, ROOT, _plaintext_songs, _verse_like
from pie.material_units import byliny_non_epic, byliny_wiki_lines

# Seed 82026, 20 old candidates per OCR edition; ambiguous/OCR debris and prose
# were rejected by inspection before scoring. Alternating accepted samples split
# calibration/held-out negatives. Coordinates are one-based physical OCR lines.
NEGATIVES = {
    'sbornikotdelenijarusskogojazykaislovesno32': [39955,1850,20899,16069,22898,14865,13453,41284,37398,12745,21818,34479,35460,28099],
    'sbornikotdelenijarusskogojazykaislovesno92': [3698,12182,1519,12941,9928,4888],
    'pesnisobrannyepvkireevskimch2vyp57': [9776,3400],
    'pesnisobrannyepvkireevskimch3vyp36': [20736,13337],
    'pesnisobrannyepvkireevskimch2pes74': [2197,4857],
    '10945725bsb': [1191],
    'pesnisobrannyepvkireevskimvyp1pesn13': [21047,13659,23348],
    'pesnisobrannyepvkireevskimch3vyp51': [3713],
    'pesnisobrannyepvkireevskimch2pesni36': [5633,1731],
    'pesnisobrannyepnrybnikovymch3narod26': [27242,11748,17440,8875],
    'pesnisobrannyepnrybnikovymch2narod72': [12075,19574],
    'pesnisobrannyepnrybnikovymch1narod12': [7816,22721,26450,11004,29703,16012],
}
# Seed 82028, ten raw wiki candidates per edition, manually read; two template
# fields in Rybnikov are not verse and are omitted. These are an additional
# validation sample, not used to select thresholds.
WIKI_NEGATIVES = {
    ('426094',91), ('425083',19), ('426147',2), ('426307',34), ('426229',106),
    ('425717',119), ('426063',87), ('425465',52), ('426237',24), ('425719',81),
    ('391421',148), ('390435',75), ('391100',178), ('390400',80),
    ('390534',199), ('390731',152), ('391421',189), ('390461',47),
    ('226091',13), ('226091',49), ('226086',137), ('226086',75), ('226086',151),
    ('226086',36), ('226091',156), ('226091',7), ('226091',120), ('226091',54),
}


def audit():
    counts = Counter()
    removed = []
    rules = json.loads((ROOT/'data/research/8c/stageCS/material-unit-rules.json').read_text())
    scores = {'calibration': Counter(), 'held_out': Counter()}
    missed = []
    neg_index = 0
    for edition, files in BYLINY_OCR.items():
        paths = [ROOT/KD/edition/f for f in files] if files else sorted((ROOT/KD/edition).glob('*_djvu.txt'))
        for path in paths:
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
            excluded = byliny_non_epic(lines)
            stem = path.stem.removesuffix('_djvu')
            rs = [r for r in rules if r['corpus']=='byliny' and Path(r['source']).name==path.name]
            for i, line in enumerate(lines):
                if not _verse_like(line):
                    continue
                old = any(r['start'] <= i+1 <= r['end'] for r in rs)
                counts[edition + ':candidates'] += 1
                counts[edition + ':pipeline_removed'] += old or i in excluded
                if i in excluded:
                    counts[edition + ':removed'] += 1
                    counts[edition + ':new'] += not old
                    removed.append({'edition': edition, 'locus': f'{stem}:{i+1}',
                                    'first_words': ' '.join(line.split()[:3]), 'reason': excluded[i]})
                elif old:
                    counts[edition + ':reviewed_backstop'] += 1
                for r in rs:
                    if r['start'] <= i+1 <= r['end']:
                        split = 'held_out' if 'w2' in r['report'] else 'calibration'
                        scores[split]['tp' if i in excluded else 'fn'] += 1
                        if i not in excluded:
                            missed.append(f'{split}:{stem}:{i+1}')
            for line_no in NEGATIVES.get(stem, []):
                assert _verse_like(lines[line_no-1])
                split = 'held_out' if neg_index % 2 else 'calibration'
                neg_index += 1
                scores[split]['fp' if line_no-1 in excluded else 'tn'] += 1
    wiki = list(_plaintext_songs(ROOT/KD/'russian-byliny-wikisource/texts-plaintext.txt'))
    kept = {(pid,i) for pid,title,i,line in byliny_wiki_lines(wiki)}
    for pid,title,i,line in wiki:
        edition = ('Kirsha Danilov (wiki)' if 'Киршею' in title else
                   'Rybnikov (wiki)' if 'Рыбниковым' in title else 'Hilferding (wiki)')
        counts[edition+':candidates'] += 1
        if (pid,i) not in kept:
            counts[edition+':removed'] += 1
            counts[edition+':pipeline_removed'] += 1
            counts[edition+':new'] += (pid,i) not in {('425083',129),('425083',130)}
            removed.append({'edition': edition, 'locus': f'ruws {pid}:{i}',
                            'first_words': ' '.join(line.split()[:3]), 'reason': 'wiki-editorial'})
        if (pid,i) in {('425083',129),('425083',130)}:
            scores['held_out']['fn' if (pid,i) in kept else 'tp'] += 1
        if (pid,i) in WIKI_NEGATIVES:
            scores['held_out']['tn' if (pid,i) in kept else 'fp'] += 1
    result = {'counts': dict(sorted(counts.items())), 'scores': {}, 'missed_reviewed': missed,
              'spot_check_seed': 82027, 'spot_check': random.Random(82027).sample(removed,30)}
    for split,c in scores.items():
        result['scores'][split] = {**dict(c), 'precision': c['tp']/(c['tp']+c['fp']),
                                   'recall': c['tp']/(c['tp']+c['fn'])}
    return result


if __name__ == '__main__':
    result = audit()
    path = Path('/private/tmp/byliny-material-audit.json')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(path)
    print(json.dumps({k:v for k,v in result.items() if k!='spot_check'}, ensure_ascii=False, indent=2))
