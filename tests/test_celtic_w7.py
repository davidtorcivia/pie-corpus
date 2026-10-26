"""Wave-7 source-verified Celtic contexts; preserve unrelated homographs."""
import pytest
from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows


@pytest.mark.parametrize('words,index,baseline,target', [
    (['bláth', 'ḟind', 'ina'], 1, 'find', 'find@white'),
    (['imma-ricfa', 'élúd', 'dó'], 1, 'asluí', 'élúd@escape'),
    (['in', 't-áes', 'cumachta'], 1, 'dotét', 'áes'),
    (['in', 't-áes', 'trebaire'], 1, 'dotét', 'áes'),
    (['do', 'thenid', 'sinnaig'], 1, '?thenid', 'tene'),
    (['esca', 'usci', 'aer'], 1, '?usci', 'uisce'),
    (['Id', 'adaig', 'muir'], 1, 'adaig', 'adaig@night'),
    (['bid', 'lir', 'bomand', 'ega'], 1, 'ler|lear', 'il'),
    (['bit', 'lir', 'bomand', 'ega'], 1, 'ler|lear', 'il'),
    (['adaig', 'muir', 'tir'], 1, 'muir|múr', 'muir'),
    (['usci', 'aer', 'Id'], 1, 'aer|áer', 'aer@air'),
    (['sær-chlanna', 'h-Erind'], 1, 'érind', 'ériu (name)'),
    (['dær-tuathaib', 'h-Erind'], 1, 'érind', 'ériu (name)'),
    (['co', 'hAine', 'co', 'hAirigi'], 1, 'áine', 'áine (name)'),
    (['riut', 'gus', 'aniu'], 1, 'gus', 'co'),
    (['fhleid', 'gusa', 'm-bertha'], 1, 'gus', 'co'),
    (['ocus', 'lotar', 'i', 'm-breith'], 1, 'loit', 'luid'),
    (['bris', 'a', 'craide', 'ina', 'cliab'], 2, '?craide', 'cride'),
    (['in', 't-shlegh', 'ina', 'h-ucht'], 1, '?tshlegh', 'sleg'),
    (['ni', 'rus', 'leic'], 1, 'ros|rús', 'ro'),
    (['h-ucht', 'cor', 'bris'], 1, 'foceird|cor|coir', 'co'),
    (['ó', 'aill', 'do', 'aill'], 1, 'aile|áill', 'aill'),
    (['do', 'aill', 'ocom'], 1, 'aile|áill', 'aill'),
])
def test_reviewed_context(words, index, baseline, target):
    form = words[index]
    z = cm.CelticLemmatizer(fm.LangMapping('sga'), cm.irish_demutate,
        cm.irish_skeleton, form_overrides={fm.key_sga(cm._ir_clean(form)): baseline},
        use_skeleton=False)
    assert cm.lemmatize_words(z, words)[index] == target
    assert z(form) == baseline
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == baseline
    if target in {'co', 'ro'}:
        assert not cm.content_of(z.lm, target, form, z)


@pytest.mark.parametrize('uid', [
    'oldirish-meyer-editions-1892-1919:berdielteste00meyeuoft:L6500-L6500',
    'celtic-journal-eriu-1904-1928:eriu_1912_6:L7994-L7995',
    'celtic-journal-revue-celtique-1870-1928:revueceltique13pari:L22538-L22539',
])
def test_reviewed_material_exclusions_are_exact(uid):
    rows = [{'id': uid, 'text': 'apparatus'},
            {'id': uid.split(':')[0] + ':unrelated:L1-L1', 'text': 'apparatus'}]
    assert repair_celtic_rows(rows) == rows[1:]
    assert repair_celtic_rows(repair_celtic_rows(rows)) == rows[1:]


def test_sense_overrides_and_retained_derivations():
    ov = fm.load_overrides()['lemma']['celt']
    assert not ov['élúd@escape'][0]
    assert not ov['aer@air'][0]
    table = cm.read_table('celt')
    assert table['tús'] == ('pie-root-weyd-see',)
    assert table['mag'] == ('pie-lex-megjh2s',)
    assert table['luid'] == ('pie-lex-h1ludhet',)
