"""Wave-6 independently reviewed Celtic contexts and false name labels."""
import pytest
from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows


@pytest.mark.parametrize('words,index,baseline,target', [
    (['dá', 'crúim', 'and'], 1, 'crúigh', 'cruim'),
    (['an', 't-ech', 'gu', 'cenn'], 1, 'tech', 'ech'),
    (['neoil', 'áilli', 'aen-gela'], 1, 'aille', 'álaind'),
    (['rí', 'mo', 'thúaithi', 'do-ratusa'], 2, '?thuaithi', 'túath'),
    (['i', 'abhull', 'fo', 'bláth'], 1, '?abhull', 'aball'),
    (['i', 'abhull', 'abaigh'], 1, '?abhull', 'aball'),
    (['i', 'abull', 'ac', 'tuitim'], 1, '?abull', 'aball'),
    (['Oengus', 'find'], 0, 'oíngus', 'óengus (name)'),
    (['thúaithi', 'do-ratusa', 'dúibsi'], 1, '?doratusa', 'dorat'),
    (['dia', 'toig', 'indisid'], 1, 'tóg', 'tech'),
    (['i', 'días', 'ban'], 1, 'días', 'dias@pair'),
    (['iasc', 'mbrec', 'for'], 1, 'bréc', 'brecc'),
    (['Aengus', 'aainm'], 0, 'aengus', 'aengus (name)'),
])
def test_reviewed_context_and_unrelated_homograph(words, index, baseline, target):
    form = words[index]
    z = cm.CelticLemmatizer(fm.LangMapping('sga'), cm.irish_demutate,
        cm.irish_skeleton, form_overrides={fm.key_sga(cm._ir_clean(form)): baseline},
        use_skeleton=False)
    assert cm.lemmatize_words(z, words)[index] == target
    assert z(form) == baseline
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == baseline


@pytest.mark.parametrize('uid,word', [
    ('welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L17016-L17028', 'Dỳwawt'),
    ('G301041:#1:208', 'Dogebhthar'),
    ('G301000:#1:5', 'As-noí'),
])
def test_false_name_capitals_are_source_specific_and_idempotent(uid, word):
    row = {'id': uid, 'text': f'prefix {word} suffix'}
    unrelated = {'id': 'unrelated:' + uid, 'text': row['text']}
    got = repair_celtic_rows([row, unrelated])
    assert got[0]['text'] == f'prefix {word.lower()} suffix'
    assert got[1] == unrelated
    assert row['text'] == f'prefix {word} suffix'
    assert repair_celtic_rows(got) == got
    # The loader's medial-capital heuristic no longer labels this verb a name.
    assert not cm.irish_words(got[0]['text'])[1][:1].isupper()


def test_reviewed_roots_and_suppletive_give_stem():
    table = cm.read_table('celt')
    assert table['machad'] == ('pie-lex-pedom',)
    assert table['tús'] == ('pie-root-weyd-see',)
    assert table['brecc'] == ('pie-root-perkj-colored',)
    assert cm.read_table('cy')['gwneuthur'] == ('pie-lex-wergjeti',)
    # The perfective give stem must not inherit present *bher- by lemmatization.
    assert not table.get('dorat')
    assert not table.get('dias@pair')
