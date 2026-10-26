"""Wave-3 lexical disambiguation: positive contexts and homograph boundaries."""
import pytest

from pie import celtic_mapping as cm
from pie import formula_search_multi as fm


@pytest.mark.parametrize('words,index,baseline,target', [
    (['rogenair', 'annocht'], 1, 'nocht', 'innocht'),
    (['Ro', 'sir', 'immoro'], 1, 'sír', 'síraid'),
    (['IN', 't-ochtur', 'ar', 'xx', 'oclach'], 1, '?tochtur', 'ochtar'),
    (['ná', 'bíad', 'commus'], 1, 'bíad', 'bí'),
    (['tairces', 'do', 'ṡétaib', 'dó'], 2, 'sét', 'sét@treasure'),
    (['dia', 'imshnímaib', 'móra'], 1, '?imshnimaib', 'imshním'),
    (['bodéin', 'asa', 'h-aithli'], 2, 'adlen', 'aithle@afterwards'),
    (['ingen', 'do', 'légud', 'úad'], 2, 'legaid', 'léicid'),
])
def test_context_correction_preserves_homograph_and_cache(words, index, baseline, target):
    form = words[index]
    z = cm.CelticLemmatizer(
        fm.LangMapping('sga'), cm.irish_demutate, cm.irish_skeleton,
        form_overrides={fm.key_sga(form): baseline}, use_skeleton=False)
    assert z(form) == baseline
    assert cm.lemmatize_words(z, words)[index] == target
    assert z(form) == baseline
    assert cm.lemmatize_words(z, words[index:])[0] == baseline
    if index + 1 < len(words):
        assert cm.lemmatize_words(z, words[:index + 1])[index] == baseline


def test_temporal_expression_is_not_lexical_smearing_evidence():
    lm = fm.LangMapping('sga')
    assert cm.is_function_lemma(lm, 'aithle@afterwards')
    assert not cm.content_of(lm, 'aithle@afterwards', 'h-aithli')
    assert not cm.is_function_lemma(lm, 'adlen')


def test_unverified_sense_derivations_are_explicitly_unmapped():
    ov = fm.load_overrides(cm.ROOT)
    for corpus in ('celt', 'sga-glosses'):
        for lemma in ('síraid', 'ochtar', 'sét@treasure', 'imshním', 'aithle@afterwards'):
            assert not ov['lemma'][corpus][lemma][0]
    # The rejected reader proposal must not overwrite the inherited do/make root.
    assert cm.read_table('celt')['dogní'] == ('pie-root-gjenh1-produce',)
