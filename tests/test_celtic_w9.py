"""Wave-9 Celtic homographs: reviewed contexts and unaffected controls."""
import pytest
from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows


@pytest.mark.parametrize('words,index,baseline,target', [
    (['tar', 'leth', 'in', 'maigi', 'arna'], 3, 'maígh', 'mag'),
    (['in', 'muintear', 'na', 'comaltadha'], 1, 'múin', 'muinter@household'),
    (['suidiu', 'ní', 'tallat', 'a', 'ligiu'], 4, 'lige', 'lige@lying'),
    (['in', 'lín', 'bíte', 'i', 'seasam'], 1, 'lín', 'lín@number'),
    (['in', 'lín', 'tallat', 'i', 'suidiu'], 1, 'lín', 'lín@number'),
    (['ro', 'lín', 'na', 'fántu'], 1, 'lín', 'línaid@fill'),
    (['ro', 'lín', 'na', 'glenntu'], 1, 'lín', 'línaid@fill'),
    (['ro', 'lín', 'in', 't-óclach'], 1, 'lín', 'línaid@fill'),
    (['ro', 'lín', 'iat'], 1, 'lín', 'línaid@fill'),
    (['l', 'lín', 'fri', 'h-aige'], 1, 'lín', 'lín@net'),
    (['l', 'lín', 'fria', 'h-íascach'], 1, 'lín', 'lín@net'),
    (['l', 'lín', 'éisc'], 1, 'lín', 'lín@net'),
])
def test_irish_contexts_preserve_homographs(words, index, baseline, target):
    form = words[index]
    z = cm.CelticLemmatizer(fm.LangMapping('sga'), cm.irish_demutate,
        cm.irish_skeleton, form_overrides={fm.key_sga(cm._ir_clean(form)): baseline},
        use_skeleton=False)
    assert cm.lemmatize_words(z, words)[index] == target
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == baseline
    assert z(form) == baseline


def test_welsh_fabric_not_digging():
    z = cm.CelticLemmatizer(fm.LangMapping('cy'), cm.welsh_demutate,
        cm.welsh_skeleton, form_overrides={'bali': 'palu'}, use_skeleton=False)
    assert cm.lemmatize_words(z, ['o', 'bali', 'llathreit'])[1] == 'pali@brocade'
    assert cm.lemmatize_words(z, ['o', 'bali', 'unrelated'])[1] == 'palu'
    assert cm.lemmatize_words(z, ['unrelated', 'bali', 'llathreit'])[1] == 'palu'


def test_secure_ocr_repairs_are_local_and_idempotent():
    uid = 'oldirish-irische-texte-1880-1909:irischetextemitw02winduoft:L14602-L14604'
    text = 'hen cen cheli siur cell brathair mdihre AlaxawiüiV'
    rows = [{'id': uid, 'text': text}, {'id': 'unrelated', 'text': text}]
    got = repair_celtic_rows(rows)
    assert got[0]['text'] == 'ben cen cheli siur cen brathair mdihre Alaxandir'
    assert got[1] == rows[1]
    assert rows[0]['text'] == text
    assert repair_celtic_rows(got) == got


def test_reviewed_senses_and_retained_etymologies():
    table = cm.read_table('celt')
    assert table['lige@lying'] == ('pie-root-legh-lie',)
    assert table['lín@number'] == ('pie-root-leyH-pour',)
    assert table['línaid@fill'] == ('pie-root-leyH-pour',)
    assert not table.get('lín@net')
    assert not table.get('muinter@household')
    assert not cm.read_table('cy').get('pali@brocade')
    assert cm.read_table('cy')['gwystyl'] == ('pie-lex-gheydhlos',)
