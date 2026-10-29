"""Wave 9 source-coordinate regressions; never read review slabs or claims."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from pie import formula_search as fs, mapping as mp
from pie.w9_other_mapping import ROWS, reviewed_lemma

ROOT = Path(__file__).resolve().parents[1]
# corpus-quality batch 2, lead decision: Armenian gan follows the cq1 rule (gam) everywhere
CQ2 = {'gam@present': 'gam'}


def test_contextual_corrections_do_not_change_unreviewed_homographs():
    for r in ROWS:
        t = fs.Token(r['corpus'], r['old'], r['surface'], r['locus'], {}, True, 'noun')
        assert t.lemma == CQ2.get(r['lemma'], r['lemma']), r
        assert t.surface == r['surface']
        assert t.content == (not r['lemma'].endswith((' (name)', '@numeral')))
        assert reviewed_lemma(r['corpus'], r['old'], r['surface'], 'elsewhere') == r['old']
        assert reviewed_lemma(r['corpus'], 'unreviewed', r['surface'], r['locus']) == 'unreviewed'


def test_actual_dmhp_coordinates_and_segmentation():
    spec = importlib.util.spec_from_file_location('w9_stage_c', ROOT/'scripts/build_8c_stageC.py')
    sc = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = sc
    spec.loader.exec_module(sc)
    expected = {(r['locus'], r['surface']): r for r in ROWS if r['corpus'] == 'xcl'}
    seen = set()
    for t in sc.dmhp_tokens(ROOT):
        r = expected.get((t.locus, t.surface))
        if r:
            seen.add((t.locus, t.surface))
            assert t.lemma == CQ2.get(r['lemma'], r['lemma'])
            assert t.content == (not t.lemma.endswith((' (name)', '@numeral')))
    assert seen == expected.keys()


@pytest.mark.parametrize('corpus,lemma,ids', [
    ('xcl', 'kamkʻ', set()), ('xcl', 'lapʻem', set()),
    ('xcl', 'lcʻowcʻanem', {'pie-root-pleh1-fill'}),
    ('xcl', 'ar̄ow', {'pie-root-srew-flow'}),
    ('grp', 'ἄδυτος', set()), ('grp', 'δύσις', set()),
    ('hom', 'ἔσθω', {'pie-root-h1ed-eat'}),
    ('av', 'akṣa@eye', {'pie-lex-h3okws'}),
    ('byliny', 'волна@wave', {'pie-root-welH-roll'}),
    ('byliny', 'лисица', set()), ('vuk', 'bol@pain', set()),
])
def test_reviewed_mapping_replaces_wrong_automatic_root(corpus, lemma, ids):
    assert mp.decide(corpus, lemma, {'wrong-auto-root'})[0] == ids


def test_unreviewed_senses_and_correct_aorist_are_preserved():
    assert mp.resolve_table('xcl')['gam'].ids == {'pie-root-weh2dh-go'}
    assert mp.resolve_table('xcl')['gam@aorist'].ids == {'pie-root-gwem-come'}
    assert mp.resolve_table('byliny')['волна'].ids == {'pie-lex-h2wlh1neh2'}
    assert fs.Token('xcl', 'town', 'տան', 'unreviewed', {}, True, 'noun').lemma == 'town'
    assert fs.Token('sa-ep', 'akṣa', 'akṣaḥ', 'unreviewed', {}, True, 'noun').lemma == 'akṣa'


def test_reviewed_material_exclusions_have_exact_boundaries():
    from pie.material_units import excluded_source
    rows = json.loads((ROOT/'data/research/8c/stageCS/material-unit-rules-w9-other.json').read_text())
    assert len(rows) == 67
    for r in rows:
        assert r['start'] == r['end']
        assert excluded_source(r['corpus'], Path(r['source']).name, r['start'])
        # cq2 excludes all of Rybnikov vol. 2 from line 21980 (its editorial matter)
        if Path(r['source']).name == 'pesnisobrannyepnrybnikovymch2narod72_djvu.txt' and r['start'] >= 21980:
            continue
        assert not excluded_source(r['corpus'], Path(r['source']).name, r['start']-1, r['end'])
