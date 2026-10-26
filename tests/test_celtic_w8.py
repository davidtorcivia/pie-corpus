"""Wave-8 Celtic homographs, checked against CELT and dictionaries."""
import pytest
from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows


@pytest.mark.parametrize('words,index,baseline,target', [
    (['fothlocht', 'fann', 'foda', 'for', 'a', 'lár'], 2, 'fód', 'fota'),
    (['sé', 'féin', 'rena', 'fāistine'], 2, 'fren', 'fri'),
    (['láe', 'nó', 'áidchi', 'ar', 'in', 'ríg'], 2, 'adaig', 'adaig@night'),
    (['nó', 'ret', 'buimme'], 1, 'rét|réidid', 'fri'),
    (['nó', 'ret', "t'", 'aiti'], 1, 'rét|réidid', 'fri'),
])
def test_reviewed_homographs_preserve_other_contexts(words, index, baseline, target):
    form = words[index]
    z = cm.CelticLemmatizer(fm.LangMapping('sga'), cm.irish_demutate,
        cm.irish_skeleton, form_overrides={fm.key_sga(cm._ir_clean(form)): baseline},
        use_skeleton=False)
    assert cm.lemmatize_words(z, words)[index] == target
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == baseline
    if target == 'fri':
        assert not cm.content_of(z.lm, target, form, z)


def test_quotation_initial_verb_is_not_a_name():
    row = {'id': 'G301012:#1/#2/#52:26', 'text': 'aisnéis: Táinic buiden mór'}
    other = {**row, 'id': 'unrelated'}
    repaired = repair_celtic_rows([row, other])
    assert repaired[0]['text'] == 'aisnéis: táinic buiden mór'
    assert repaired[1] == other
    assert row['text'] == 'aisnéis: Táinic buiden mór'
    assert repair_celtic_rows(repaired) == repaired


def test_retained_beginning_etymology_and_night_sense():
    table = cm.read_table('celt')
    assert table['tús'] == ('pie-root-weyd-see',)
    assert not table.get('adaig@night')
