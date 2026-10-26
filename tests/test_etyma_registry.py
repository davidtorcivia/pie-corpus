"""Research isolation; synthetic fixtures, no raw corpora."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from pie import etyma, mapping as mp
from pie.research_scope import RESEARCH_ONLY
from pie.tier2_secure import SecureChecker, build_population, _path_decided

RID = 'research-etymon-test-1'
ROOT = 'pie-root-test'
LID = 'pie-lex-test'
ENTRIES = {
    ROOT: {'id': ROOT, 'kind': 'root', 'form': 'test-'},
    LID: {'id': LID, 'root_id': ROOT, 'form': 'test', 'reflexes': {'Hittite': [{'form': 'test'}]}},
}


def entry(**kw):
    return {'id': RID, 'kind': 'root', 'form': 'téstH-', 'source_forms': ['*téstH-'],
            'sense': 'test', 'sources': [{'source': 'EDHIL', 'page': 1,
                                        'text_file': 'raw/books/text/kloekhorst-hitt/p0009.txt'}],
            'uncertainty': [], 'scope': RESEARCH_ONLY, **kw}


def row(ids=None, **kw):
    return {'corpus': 'hit', 'lang': 'hit', 'lemma': 'test', 'word': 'test',
            'lex_id': ids if ids is not None else [RID], 'path': ['hit:test', 'proto:*test'], **kw}


def override(kind, ids=None, scope=None):
    r = {'lex_id': ids if ids is not None else [RID]}
    if scope:
        r['scope'] = scope
    if kind == 'lemma':
        return mp.as_overrides({'hit': {'test': (r['lex_id'], r)}})
    ov = mp.as_overrides({})
    if kind == 'key':
        ov['key'] = {'hit': {'test': mp.decision(r)}}
    else:
        ov['proto'] = {('proto', mp.proto_key('*test')): mp.decision(r)}
    return ov


def test_registry_strict_schema_and_lossless_forms(tmp_path):
    e = entry(homograph=2)
    p = tmp_path / etyma.REGISTRY
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(e) + '\n')
    assert etyma.load_registry(tmp_path)[RID] == e
    for change in ({'scope': 'production'}, {'form': 'ḫet-'}, {'form': 'te\u0301stH-'},
                   {'source_forms': ['*test- ?']}, {'mystery': 1}, {'homograph': 0},
                   {'cross_link': {'root_id': ROOT, 'note': ''}}):
        with pytest.raises(ValueError):
            etyma.validate({**e, **change})
    p.write_text((json.dumps(e) + '\n') * 2)
    with pytest.raises(ValueError, match='duplicate'):
        etyma.load_registry(tmp_path)


def test_adapter_opt_in_cross_link_does_not_merge():
    from pie.formula_search import group_map
    e = entry(cross_link={'root_id': ROOT, 'note': 'Reviewed source equation.'})
    before = copy.deepcopy(ENTRIES)
    assert RID not in group_map(list(ENTRIES.values()))
    groups = etyma.research_group_map(list(ENTRIES.values()), {RID: e})
    assert groups[RID] == RID and groups[LID] == ROOT and ENTRIES == before
    e['cross_link']['root_id'] = 'pie-root-missing'
    with pytest.raises(ValueError, match='existing'):
        etyma.research_group_map(list(ENTRIES.values()), {RID: e})


def test_doubtful_forms_are_preserved_only_with_explicit_qualification():
    doubtful = entry(source_forms=['*test- ??'], uncertainty=['Mechanical reconstruction.'])
    etyma.validate(doubtful)
    assert etyma.research_group_map(list(ENTRIES.values()), {RID: doubtful})[RID] == RID
    for notes in ([], ['   ']):
        with pytest.raises(ValueError, match='uncertainty'):
            etyma.validate({**doubtful, 'uncertainty': notes})
    with pytest.raises(ValueError, match='control glyphs'):
        etyma.validate({**doubtful, 'source_forms': ['*te\x03st-']})


@pytest.mark.parametrize('kind', ['auto', 'lemma', 'key', 'proto', 'added', 'explicit', 'mixed'])
def test_scope_and_secure_fallbacks(kind):
    rows = [row([LID])]
    ov = {}
    if kind == 'auto':
        rows = [row()]
    elif kind == 'explicit':
        rows = [row([ROOT], scope=RESEARCH_ONLY)]
    elif kind == 'mixed':
        ov = override('lemma', [RID, ROOT])
    else:
        ov = override('lemma' if kind == 'added' else kind)
        if kind == 'added':
            rows = []
    resolved = mp.resolve_rows('hit', rows, ov)['test']
    assert resolved.scope == RESEARCH_ONLY
    assert all(d.scope == RESEARCH_ONLY for d in resolved.decisions)
    pop = build_population({'hit': rows}, ov)
    # Other tables and the production lexicon both offer exactly the forbidden evidence.
    rec = (frozenset({LID}), ('dict:hit', 'hit:test', 'proto:*test'), 'dict:hit', False)
    ch = SecureChecker.from_population(ENTRIES, pop, lambda: ({'hit': {'test': [rec]}},))
    for lid in (RID, ROOT, LID):
        assert ch.match(lid, 'hit', 'Hittite', 'test', True) is None
        assert ch.check(lid, [{'lang': 'Hittite', 'lemmas': ['test'], 'words': ['test']}])['evidence'] == {}
    assert not pop.tables['hit']


@pytest.mark.parametrize('kind', ['lemma', 'key', 'proto'])
def test_decisions_are_final_and_explicit_scope_survives(kind):
    ov = override(kind, [ROOT], RESEARCH_ONLY)
    assert mp.resolve_rows('hit', [row()], ov)['test'].scope == RESEARCH_ONLY
    ov = override(kind, [])
    assert mp.resolve_rows('hit', [row()], ov) == {}


def test_form_override_and_compound_cannot_restore_research(monkeypatch):
    ov = override('lemma')
    ov['form'] = {'hit': {'testing': 'test'}}
    entries = copy.deepcopy(ENTRIES)
    entries[LID]['reflexes']['Hittite'].append({'form': 'st'})
    ch = SecureChecker.from_population(entries, build_population({'hit': [row()]}, ov))
    assert ch.match(LID, 'hit', 'Hittite', 'testing', False) is None
    import pie.tier2_secure as ts
    monkeypatch.setitem(ts.PREFIX_REFLEXES, 'fixture', {'hit': ['te']})
    cid = 'compound:bahuvrihi:fixture+' + LID
    refs = [{'lang': 'Hittite', 'lemmas': ['test']}]
    assert SecureChecker(entries).check_compound(cid, refs)['evidence']
    assert ch.check_compound(cid, refs)['evidence'] == {}
    assert ch._match_key(LID, 'hit', 'Hittite', 'test', 'test') is None


def test_proto_decision_blocks_external_table_and_direct_table_blocks_reflex():
    rec = (frozenset({LID}), ('dict:hit', 'hit:test', 'proto:*test'), 'dict', False)
    assert _path_decided('hit', rec, override('proto', [ROOT], RESEARCH_ONLY)) is None
    research = (frozenset({RID}), ('hit:test',), 'fixture', False)
    ch = SecureChecker(ENTRIES, {'hit': {'test': [research]}})
    assert ch.match(LID, 'hit', 'Hittite', 'test', True) is None


def test_unknown_override_keys_still_raise(tmp_path):
    p = tmp_path / mp.OVERRIDES
    p.parent.mkdir(parents=True)
    p.write_text('{"research": []}')
    with pytest.raises(ValueError, match='unknown override keys'):
        mp.load_overrides(tmp_path)


def test_production_rejects_injected_research_and_holdouts():
    from pie.realize import Lexicon
    from pie.export import cognate_tasks, eval_root, record_tasks
    for e in (entry(), {'id': LID, 'scope': RESEARCH_ONLY}):
        with pytest.raises(ValueError, match='research_only'):
            Lexicon({e['id']: e}, {}, {})
        with pytest.raises(ValueError, match='research_only'):
            cognate_tasks(SimpleNamespace(entries={e['id']: e}))
    with pytest.raises(ValueError, match='research_only'):
        eval_root(RID)
    for r in ({'scope': RESEARCH_ONLY}, {'tokens': [{'lex_id': RID}]}):
        with pytest.raises(ValueError, match='research_only'):
            record_tasks(r)


def test_shipped_batch_and_proposals_are_separate():
    registry = etyma.load_registry()
    assert 'research-etymon-meih2ur-time' in registry
    assert 'research-etymon-h2let-call' not in registry  # promoted; old id retired
    lex = [json.loads(s) for s in (etyma.ROOT / 'data/lexicon/lexicon.jsonl').read_text().splitlines()]
    groups = etyma.research_group_map(lex, registry)
    assert not registry.keys() & {e['id'] for e in lex}
    # Identical spellings can denote different homographs; isolation is by id/scope.
    for line in (etyma.ROOT / 'data/research/formulas/etyma-hittite-proposals.jsonl').read_text().splitlines():
        r = json.loads(line)
        assert r['scope'] == RESEARCH_ONLY and set(r['lex_id']) <= registry.keys()
        assert all(groups[i] == i for i in r['lex_id'])
    assert 'etyma-hittite-proposals' not in mp.table_corpora()


def test_hittite_audit_is_complete_and_candidates_require_independent_sources():
    from pie.realize import Lexicon
    data = etyma.ROOT / 'data/research/formulas'
    def rows(name):
        return [json.loads(s) for s in (data / name).read_text().splitlines()]
    registry = etyma.load_registry()
    candidates = rows('lexicon-candidates-hittite.jsonl')
    inventory = rows('hittite-etyma-inventory.jsonl')
    audit = rows('hittite-top500-etyma-audit.jsonl')
    ids = {c['id'] for c in candidates}
    assert ids.isdisjoint(registry)
    assert len(ids) == len(candidates)
    assert {r['id'] for r in inventory} == ids | registry.keys()
    assert len({r['id'] for r in inventory}) == len(inventory)
    assert [r['rank'] for r in audit] == list(range(1, 501))
    assert len({r['lemma'] for r in audit}) == 500
    assert sum(r['tokens'] for r in audit) == 51554
    referenced = {i for r in audit for i in r['review_ids']}
    assert referenced == ids | registry.keys()
    for item in inventory:
        assert item['classification'] == ('lexicon-candidate' if item['id'] in ids else 'registry-only')
        assert item['lemma_ranks']
        assert all(item['id'] in audit[r - 1]['review_ids'] for r in item['lemma_ranks'])
    for c in candidates:
        assert c['scope'] == RESEARCH_ONLY and c['status'] == 'lexicon-candidate'
        assert c['proposed_kind'] in {'root', 'noun', 'adj', 'other'}
        assert c['agreement'] and c['form'] and c['sense']
        sources = {s['source'] for s in c['sources']}
        assert 'EDHIL' in sources and len(sources) >= 2
        assert all(type(s['page']) is int and s['page'] > 0 and
                   s['text_file'].startswith('raw/books/text/') for s in c['sources'])
        with pytest.raises(ValueError, match='research_only'):
            Lexicon({c['id']: c}, {}, {})


def test_production_never_reads_registry(monkeypatch):
    from pie.realize import Lexicon
    from pie.export import cognate_tasks
    original = Path.open
    def guarded(path, *a, **kw):
        assert 'etyma' not in path.name, 'production attempted to read registry'
        return original(path, *a, **kw)
    monkeypatch.setattr(Path, 'open', guarded)
    Lexicon.load.cache_clear()
    lx = Lexicon.load()
    assert not any(i.startswith('research-etymon-') for i in lx.entries)
    assert not any(t['source_id'].startswith('research-etymon-') for t in cognate_tasks(lx))
    # Builders must not acquire registry dependencies, including indirect ones.
    import ast
    seen = set()
    def check(path):
        if path in seen or not path.exists():
            return
        seen.add(path)
        text = path.read_text()
        assert 'etyma.jsonl' not in text and 'load_registry' not in text
        for n in ast.walk(ast.parse(text)):
            if isinstance(n, ast.ImportFrom) and n.module:
                name = n.module.removeprefix('pie.')
                if n.level or n.module.startswith('pie.'):
                    check(etyma.ROOT / 'pie' / (name.replace('.', '/') + '.py'))
    for name in ('scripts/build_lexicon.py', 'scripts/classify_lexicon.py', 'pie/liv.py',
                 'pie/realize.py', 'pie/export.py', 'pie/generate.py'):
        check(etyma.ROOT / name)


def test_external_proto_only_research_blocks_reflex_and_compound_routes():
    ov = override('proto', [ROOT], RESEARCH_ONLY)
    pop = build_population({}, ov)
    rec = (frozenset({LID}), ('dict:hit', 'hit:test', 'proto:*test'), 'dict', False)
    ch = SecureChecker.from_population(ENTRIES, pop, lambda: ({'hit': {'test': [rec]}},))
    assert ch.match(LID, 'hit', 'Hittite', 'test', True) is None
    assert ch.match(ROOT, 'hit', 'Hittite', 'test', True) is None


def test_explicit_research_entry_cannot_be_secure_even_with_production_id():
    entries = {**ENTRIES, LID: {**ENTRIES[LID], 'scope': RESEARCH_ONLY}}
    rec = (frozenset({LID}), ('hit:test',), 'fixture', False)
    ch = SecureChecker(entries, {'hit': {'test': [rec]}})
    assert ch.match(LID, 'hit', 'Hittite', 'test', True) is None
    assert ch.match(ROOT, 'hit', 'Hittite', 'test', True) is None


def test_external_proto_scope_blocks_compound_on_first_lookup(monkeypatch):
    import pie.tier2_secure as ts
    entries = copy.deepcopy(ENTRIES)
    entries[LID]['reflexes']['Hittite'].append({'form': 'st'})
    monkeypatch.setitem(ts.PREFIX_REFLEXES, 'fixture', {'hit': ['te']})
    pop = build_population({}, override('proto', [ROOT], RESEARCH_ONLY))
    rec = (frozenset({LID}), ('dict:hit', 'hit:test', 'proto:*test'), 'dict', False)
    ch = SecureChecker.from_population(entries, pop, lambda: ({'hit': {'test': [rec]}},))
    assert ch.check_compound('compound:bahuvrihi:fixture+' + LID,
                            [{'lang': 'Hittite', 'lemmas': ['test']}])['evidence'] == {}


def test_scope_cannot_be_downgraded_and_unknown_scope_raises():
    assert mp.decision({'lex_id': [RID], 'scope': 'production'}).scope == RESEARCH_ONLY
    with pytest.raises(ValueError, match='unknown mapping scope'):
        mp.resolve_rows('hit', [row(scope='reseach_only')], {})
    from pie.tier2_secure import override_row
    resolved, decided = override_row(row(), {})
    assert not decided and resolved['scope'] == RESEARCH_ONLY


def test_reviewed_production_replacement_wins_over_research_automatic_routes():
    ov = override('lemma', [LID])
    assert mp.resolve_rows('hit', [row()], ov)['test'].scope == 'production'
    pop = build_population({'hit': [row()]}, ov)
    rec = (frozenset({RID}), ('dict:hit', 'hit:test'), 'dict', False)
    ch = SecureChecker.from_population(ENTRIES, pop, lambda: ({'hit': {'test': [rec]}},))
    assert ch.match(LID, 'hit', 'Hittite', 'test', True)['level'] == 'exact'
    assert ch._match_key(LID, 'hit', 'Hittite', 'test', 'test')['level'] == 'exact'
