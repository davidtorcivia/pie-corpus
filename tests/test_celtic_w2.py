"""Wave-2 Celtic regressions with contrastive contexts and source repair boundaries."""
import pytest

from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows


def lz(lang='sga'):
    forms = {'hlechta': '?hlechta', 'fóirithin': 'fóir', 'tliúath': '?tliuath',
             'cléib': 'clé', 'coin': 'cú', 'mben': 'ben', 'tóchta': 'tongaid',
             'bíad': 'bíad', 'comla': 'adcomla|conlá', 'nyf': 'nyf'}
    return cm.CelticLemmatizer(
        fm.LangMapping(lang), cm.irish_demutate, cm.irish_skeleton,
        form_overrides={fm.KEYS[lang](k): v for k, v in forms.items()}, use_skeleton=False)


@pytest.mark.parametrize('words,index,target', [
    (['trian', 'hlechta'], 1, 'mlicht'),
    (['furtacht', 'fóirithin', 'orum'], 1, 'foirithin@help'),
    (['toing', 'mo', 'tliúath', 'or'], 2, 'túath'),
    (['for-fholumh', 'a', 'cléib', 'co'], 2, 'clíab'),
    (['Erne', 'coin', 'hingenaib'], 1, 'cona'),
    (['co', 'mben', 'dí'], 1, 'benaid'),
    (['dechmaid', 'in', 'tóchta', 'co'], 2, 'tócht@piece'),
    (['no', 'bíad', 'a', 'chend'], 1, 'bí'),
    (['dorsaide', 'in', 'comla', 'la'], 2, 'comla'),
])
def test_reviewed_context_and_cache_isolation(words, index, target):
    lemz = lz()
    original = lemz(words[index])
    assert cm.lemmatize_words(lemz, words)[index] == target
    assert lemz(words[index]) == original
    # Removing the preceding lexical condition must preserve the baseline.
    assert cm.lemmatize_words(lemz, words[index:])[0] == original


def test_conditional_requires_head_phrase_not_arbitrary_possessive():
    lemz = lz()
    assert cm.lemmatize_words(lemz, ['no', 'bíad', 'a', 'maic'])[1] == 'bíad'
    assert cm.lemmatize_words(lemz, ['no', 'bíad', 'a'])[1] == 'bíad'


def test_welsh_negative_clitic_does_not_replace_snow_noun():
    lemz = lz('cy')
    for verb in ['rygelwy', 'rygelOy']:
        assert cm.lemmatize_words(lemz, ['nyf', verb])[0] == 'ny'
        assert not cm.content_of(lemz.lm, 'ny', 'nyf', lemz)
    assert cm.lemmatize_words(lemz, ['nyf', 'gwyn'])[0] == 'nyf'
    assert cm.lemmatize_words(lz(), ['nyf', 'rygelwy'])[0] == 'nyf'


def row(uid, text):
    return {'id': uid, 'text': text, 'source': 'edition/example', 'dup_of': None}


def test_material_repairs_are_scoped_idempotent_and_do_not_mutate_input():
    rows = [row('x:zeitschriftfrc09meyeuoft:L7859-L7863', 'a brag/ait in chon'),
            row('x:zeitschriftfurcelti14:L22144-L22145', 'fichi(t) seoit'),
            row('x:revueceltique13pari:L1311-L1312', 'Comparez'),
            row('unrelated', 'brag/ait fichi(t) Comparez')]
    repaired = repair_celtic_rows(rows)
    assert [r['text'] for r in repaired] == ['a brágait in chon', 'fichit seoit',
                                           'brag/ait fichi(t) Comparez']
    assert repair_celtic_rows(repaired) == repaired
    assert rows[0]['text'] == 'a brag/ait in chon'


def test_new_nominal_senses_have_reviewed_mapping_blocks():
    overrides = fm.load_overrides(cm.ROOT)
    for corpus in ['celt', 'sga-glosses']:
        for lemma in ['foirithin@help', 'tócht@piece']:
            assert not overrides['lemma'][corpus][lemma][0]
