"""Wave5 source regressions and homonym controls; no book running text."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from pie import mapping as mp, formula_search_multi as fm
from pie.formula_search import Token
from pie.germanic_new_mapping import menota_words
from pie.material_units import byliny_page_material, repair_celtic_rows


@pytest.mark.parametrize('c,old,form,loc,new', [
    ('grc','ἔρχομαι','ἰέναι','Herodotus Historiae 9.66.2 s1','εἶμι'),
    ('grc','Θεσσαλός','Θεσσαλὸς','Thucydides Historiae 1.20.2 s1','Θεσσαλός (name)'),
    ('av','nava','navaṃ','AVŚ, 12, 3.s63','nava@new'),
    ('av','vas','uvāsa','AVŚ, 18, 1.s39','vas@dawn'),
    ('sa-ep','naś','naṣṭān','MBh, 12, 335.s75','naś@perish'),
    ('sa-ep','lubh','lubdhābhyām','MBh, 9, 35.s59','lubh@desire'),
    ('av','tva','tvam','AVŚ, 8, 9.s26','-tva@abstract'),
    ('byliny','колея|коля','соколей','ruws 389866:67','сокол'),
    ('byliny','темя','темя','ruws 426143:11','тот@demonstrative'),
    ('vuk','?tavna','Тавна','Vuk 36523:2','tavan@dark'),
    ('lv','ābols','ābolā','BV 28993','ābols@clover'),
    ('xcl','tawn','տուաւ','MH_1_2_11_Agathangelos ed. page 1484 (word id 33389)','tam'),
    ('xcl','owsowcʻanem','ուսոց','MH_1_2_11_Agathangelos ed. page 1484 (word id 33397)','ows'),
    ('xcl','bar̄nam','բարձի','MH_1_2_11_Agathangelos ed. page 1402 (word id 19138)','barj'),
    ('xcl','asim','Ասիոյ','MH_1_2_12_Movses_Khor ed. page 2158 (word id 67734)','Asia (name)'),
    ('xcl','ənd','ԼԴ.','MH_1_2_12_Movses_Khor ed. page 2158 (word id 67732)','34@numeral'),
])
def test_reviewed_tokens_preserve_surface(c,old,form,loc,new):
    t=Token(c,old,form,loc,{},True,'noun')
    assert (t.lemma,t.surface)==(new,form)
    if form!='ἰέναι':
        assert Token(c,old,form,'unreviewed',{},True,'noun').lemma==old


def test_resolved_tables_do_not_leak_senses():
    t=mp.resolve_table('av')
    assert t['nava'].ids=={'pie-lex-h1newn'}
    assert t['nava@new'].ids=={'pie-lex-newos'}
    assert t['lubh@desire'].ids=={'pie-root-lewbh-desire'}
    assert 'pie-root-h2nekj-reach' not in t['naś@perish'].ids
    assert 'tva' in t and '-tva@abstract' not in t
    assert 'φᾶρος' not in mp.resolve_table('grp')
    assert 'ḫatt=a-@stechen' not in mp.resolve_table('hit')
    assert mp.resolve_table('xum')['pequo'].ids=={'pie-lex-pekju'}


def test_avestan_reviewed_forms_and_unrelated_short_stems():
    lm=SimpleNamespace(recs={'pasu':None,'vīra':None},lemma_words={})
    lem=fm.AvestanLemmatizer(lm,{})
    assert [lem(x) for x in ['pasə̄uš','vīrə̄ṇg','pasubiia','vīraēibiia']]==['pasu','vīra','pasu','vīra']
    assert lem('pasca').startswith('?')
    assert lem('vī').startswith('?')


def test_menota_numerals_are_retained_without_phantom_sentence_breaks(tmp_path):
    p=tmp_path/'fixture.xml'
    p.write_text('<text><pb n="1r"/><lb n="2"/><w lemma="vera" me:msa="xVB"><me:norm>er</me:norm></w>'
                 '<num value="3"><me:dipl><pc>.</pc>iii<pc>.</pc></me:dipl><me:norm>3</me:norm></num>'
                 '<lb n="3"/><w lemma="nátt" me:msa="xNC"><me:norm>nǽtr</me:norm></w></text>')
    ws=menota_words(p,'fixture')
    assert [w.form for w in ws]==['er','3','nǽtr']
    assert len({w.sent for w in ws})==1
    assert ws[1].msa=='MC' and ws[1].line=='2'


def test_celtic_apparatus_ranges_leave_primary_neighbours():
    for book,start,end in [('revueceltique08pari',663,671),('revueceltique13pari',4237,4237)]:
        assert repair_celtic_rows([{'id':f'edition:{book}:L{start}-L{end}','text':'fixture'}])==[]
        assert repair_celtic_rows([{'id':f'edition:{book}:L{start-1}-L{start-1}','text':'fixture'}])


def test_page_detector_needs_independent_editorial_evidence():
    verse=['1. Едет молодец во чисто поле','Он услышал песню удалую','Он сказал: «Примечания»']
    assert not byliny_page_material(verse)
    assert byliny_page_material(['1) Иное чтение. — Р.', '2) Другое чтение. — Р.'])


def test_old_russian_name_veto_survives_cyrillic_only_key():
    lm=fm.LangMapping('orv')
    for name in ['пльсковъ','стугна']:
        lm.recs[fm.KEYS['orv'](name)] = fm.MapRec(name,name,frozenset({'kaikki:example'}),(), 'fixture','high',())
    ts=[Token('orv','пльсковъ','пльскове','nov-sin',{},True,'noun'),
        Token('orv','стугна','стугну','suz-lav',{},True,'noun')]
    auto,_=fm.corpus_mapping(ts,lm)
    assert auto.lemma_lex  # old dictionary normalization can erase '(name)'
    fixed=fm.apply_table_overrides('orv',auto.lemma_lex)
    assert not any(fixed.get(t.lemma) for t in ts)


def test_armenian_chapter_numeral_is_context_only():
    t=Token('xcl','ənd','ԼԴ.','MH_1_2_12_Movses_Khor ed. page 2158 (word id 67732)',{},True,'noun')
    assert not t.content and t.surface=='ԼԴ.'


def test_greek_name_veto_overrides_live_fuzzy_mapping():
    for corpus in ['grp','hom']:
        names=['Ὄσσα','Οἰδίπους','Σαλαμίς','Ἄργος','Εὐβοεύς','Θεσσαλός']
        automatic={name+' (name)':('pie-lex-wokwyeh2',) for name in names}
        resolved=fm.apply_table_overrides(corpus,automatic)
        assert not any(resolved.get(name+' (name)') for name in names)
