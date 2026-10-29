"""Source regressions for wave 8 other/material review; no slab/key access."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from pie import formula_search as fs, formula_search_multi as fm, mapping as mp
from pie.material_units import excluded_source, reading_emendations
from pie.w8_other_mapping import READINGS

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('key,new', READINGS.items())
def test_reviewed_context_preserves_surface_and_other_occurrences(key, new):
    c, loc, form = key
    t = fs.Token(c, 'old', form, loc, {}, True, 'noun')
    # corpus-quality batch 2, lead decision: Armenian gan follows the cq1 rule (gam) everywhere
    new = 'gam' if new == 'gam@present' else new
    assert t.lemma == new
    assert t.surface == form
    assert t.content == (not new.endswith(' (name)'))
    assert fs.Token(c, 'old', form, 'elsewhere', {}, True, 'noun').lemma == 'old'


def test_verified_mapping_changes_and_controls():
    assert mp.resolve_table('av')['nakta'].ids == {'pie-lex-nokwts'}
    assert mp.resolve_table('byliny')['падать'].ids == {'pie-root-ped-walk'}
    assert mp.decide('xcl', 'gam@present', {'pie-root-gwem-come'})[0] == set()
    assert mp.resolve_table('xcl')['gan'].ids == {'pie-lex-gwhonis'}
    assert mp.resolve_table('hom')['ἀφύσσω'].uncertain
    assert mp.resolve_table('vuk')['vuk'].ids == {'pie-lex-wlkwos'}


def test_material_rules_are_exact_source_lines():
    rows = json.loads((ROOT/'data/research/8c/stageCS/material-unit-rules-w8-other.json').read_text())
    assert len(rows) == 15
    for r in rows:
        assert r['start'] == r['end']
        assert excluded_source('byliny', Path(r['source']).name, r['start'])
        # cq2 excludes all of Rybnikov vol. 2 from line 21980 (the editorial matter); the w8 lines there
        # are no longer single-line exclusions
        if Path(r['source']).name == 'pesnisobrannyepnrybnikovymch2narod72_djvu.txt' and r['start'] >= 21980:
            continue
        assert not excluded_source('byliny', Path(r['source']).name, r['start'] - 1, r['end'])


def test_actual_edition_readings_flagged_without_text_changes():
    rows = fm.beowulf_lines()
    flagged = [(loc, text, reading_emendations('ang', loc, text)) for loc, _, text in rows
               if reading_emendations('ang', loc, text)]
    assert len(flagged) == 16
    loc, u, text = next(r for r in rows if r[0] == 'Finn. 39')
    assert u['emendations'][0]['form'] == 'swētne'
    assert u['emendations'][0]['source_reading'] == 'hwitne'
    toks = fm.text_tokens('ang', [(loc, u, text)], lambda w: w, lambda w: True)
    assert [t.surface for t in toks if t.emendations] == ['swētne']
    assert ''.join(t.surface for t in toks)  # all surfaces retained
    # Apparatus proposals not adopted in the main text must not be flagged.
    for loc, _, text in rows:
        if loc in {'Beo. 906', 'Beo. 1043', 'Beo. 1261', 'Beo. 2447', 'Beo. 2565'}:
            assert not reading_emendations('ang', loc, text)
    assert not reading_emendations('ang', 'Finn. 38', 'swētne')
    assert not reading_emendations('non', 'Finn. 39', 'swētne')


def stage_b():
    name = 'w8_test_stage_b'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, ROOT/'scripts/build_8c_stageB.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def test_unit_renderer_and_existing_search_index_expose_emendation(tmp_path):
    from pie.corpus_index import build_index, CorpusIndex
    sb = stage_b()
    loc, u, text = next(r for r in fm.beowulf_lines() if r[0] == 'Finn. 39')
    toks = fm.text_tokens('ang', [(loc, u, text)], lambda w: w, lambda w: True)
    units = sb.units_from_tokens('ang', toks, 'line', lambda t: 'Finn.',
                                [t.surface for t in toks], {}, lambda t: ('PD', False))
    assert len(units) == 1 and 'swētne' in units[0].text
    rendered = sb.B._line(units[0], 'passage', {})
    assert rendered['emendations'][0]['source_reading'] == 'hwitne'
    record = dict(corpus='ang', branch='Germanic', book='Finn.', ordinal=0,
                  locus=loc, text=text, words=[dict(form='swētne', lemma='swēte', root_ids=[], root_groups=[])])
    path = tmp_path/'test.sqlite'
    build_index(path, [record])  # an older index has no annotation field
    idx = CorpusIndex(path)
    try:
        hit = next(idx.search(form='swētne'))
        assert hit['text'] == text
        assert hit['emendations'] == rendered['emendations']
    finally:
        idx.close()
