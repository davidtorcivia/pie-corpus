"""Clean convention alternatives must not inherit errors from displaced tables."""
import json
from pathlib import Path

import pytest

from pie.morph import AdjSpec, decline_adj
from pie.validate import FormIndex, all_exact, validate_text

ROOT = Path(__file__).resolve().parents[1]
ALTERNATIVES = [json.loads(line) for line in
                (ROOT / 'data/morph/alternative_specs.jsonl').read_text().splitlines()]


@pytest.mark.parametrize('alternative', ALTERNATIVES, ids=lambda a: a['id'])
def test_clean_root_accented_alternative(alternative):
    rows = {r['id']: r for r in map(json.loads,
            (ROOT / 'data/morph/inflection_specs.jsonl').read_text().splitlines())}
    row = rows[alternative['id']]
    clean = next(e for e in row['extra_specs']
                 if e.get('source') == 'clean-root-accented-u-adjective')
    assert clean['status'] == 'supported'
    assert not clean.get('displaced_by_override')
    assert clean['spec'] == alternative['spec']
    assert {k: v for k, v in clean['spec'].items() if k != 'm_strong'} == {
        k: v for k, v in row['spec'].items() if k != 'm_strong'}
    assert row['spec']['m_strong'].endswith('ú')
    spec = AdjSpec(**clean['spec'])
    cells = decline_adj(spec)
    assert len(cells) == 3
    assert cells['m']['ACC.SG'][0] == cells['m']['NOM.SG'][0][:-1] + 'm'
    ix = FormIndex([], [row], {})
    for gender in cells.values():
        for forms in gender.values():
            for form in forms:
                assert all_exact(validate_text(form, ix)), form


def test_clean_alternatives_do_not_endorse_displaced_errors():
    rows = [r for r in map(json.loads,
            (ROOT / 'data/morph/inflection_specs.jsonl').read_text().splitlines())
            if r['id'] in {'pie-lex-sweh2dus', 'pie-lex-h1lenghus'}]
    ix = FormIndex([], rows, {})
    assert all_exact(validate_text('swéh₂dus h₁léngʰus h₁léngʷʰewes', ix))
    for form in ('suh₂déws', 'h₁ln̥gʰéwih₂'):
        token = validate_text(form, ix)['tokens'][0]
        assert token.status == 'legacy', form
        assert token.tier == 'legacy', form
    for row in rows:
        displaced = next(e for e in row['extra_specs'] if e.get('displaced_by_override'))
        assert displaced['status'] == 'legacy'
