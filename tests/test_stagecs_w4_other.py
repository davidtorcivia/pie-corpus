"""Reviewed wave4 errors, homonym controls, and source-boundary regressions."""
from pathlib import Path

import pytest

from pie import bsl_mapping as bm, mapping as mp
from pie.formula_search import Token
from pie.material_units import excluded_source, repair_celtic_rows
from pie.w4_other_mapping import reviewed_lemma

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    ('grc', 'κατάγνυμι', 'κατάξοντες', 'Thucydides Historiae 1.26.4 s1', 'κατάγω'),
    ('lat', 'uolo', 'uolare', 'LucrDRN1 1.1064', 'uolo@fly'),
    ('orv', 'блудъ', 'блудъ', 'lav 77.15', 'блудъ (name)'),
    ('vuk', 'žeti', 'жели', 'Vuk 21685:776', 'željeti'),
    ('byliny', '?веех', 'веЪхъ', '10945725bsb:4924', 'весь@all'),
    ('sa-ep', 'vasiṣṭha', 'vasiṣṭhaḥ', 'MBh, 13, 3.s24', 'Vasiṣṭha (name)'),
    ('sa-ep', 'ādya', 'ādyaiḥ', 'MBh, 1, 93.s59', 'ādya@first'),
    ('av', 'akṣa', 'akṣaḥ', 'AVP, 10, 6.s30', 'akṣi'),
    ('sa-ep', 'akṣa', 'akṣaḥ', 'MBh, 7, 57.s152', 'akṣi'),
    ('sa-ep', 'akṣa', 'akṣāḥ', 'MBh, 9, 44.s212', 'akṣi'),
]


@pytest.mark.parametrize('corpus,lemma,surface,locus,expected', CASES)
def test_locus_corrections_reach_shared_tokens(corpus, lemma, surface, locus, expected):
    t = Token(corpus, lemma, surface, locus, {}, True, 'noun')
    assert (t.lemma, t.surface) == (expected, surface)
    assert reviewed_lemma(corpus, lemma, surface, 'unreviewed') == lemma


def test_names_preserve_common_homonyms():
    assert reviewed_lemma('hom', 'Πειρίθοος', 'Πειρίθοον', 'Il. 14.318') == 'Πειρίθοος (name)'
    assert reviewed_lemma('grc', 'Ἀντιγόνη', 'Ἀντιγόνη', 'x') == 'Ἀντιγόνη (name)'
    assert reviewed_lemma('orv', 'пльсковъ', 'пльсковѣ', 'nov-sin') == 'пльсковъ (name)'
    assert reviewed_lemma('orv', 'блудъ', 'блудъ', 'other') == 'блудъ'
    assert reviewed_lemma('grc', 'γόνος', 'γόνος', 'x') == 'γόνος'


@pytest.mark.parametrize('work,word,old,new', [
    ('MH_1_1_04_Faustos', '60413', 'gind', 'Gind (name)'),
    ('MH_1_1_04_Faustos', '60750', 'gind', 'Gind (name)'),
    ('MH_1_1_06_Yeghishe', '88650', 'hown', 'hunǰkʻ'),
    ('MH_1_1_06_Yeghishe', '88658', 'kesak', 'keam'),
    ('MH_1_1_06_Yeghishe', '88648', 'vayr', 'varkʻ@cultivation'),
    ('MH_1_1_04_Faustos', '51764', 'ownim', 'yoyn (name)'),
    ('MH_1_2_12_Movses_Khor', '30497', 'ownim', 'yoyn (name)'),
])
def test_armenian_uses_actual_word_not_sentence_start(work, word, old, new):
    locus = f'{work} ed. page 0 (word id {word})'
    assert Token('xcl', old, 'surface', locus, {}, True, 'noun').lemma == new
    assert reviewed_lemma('xcl', old, 'surface', locus.replace(word, '0')) == old


def test_ocr_yat_cannot_create_an_elk_token():
    for surface in ('розгор$лоси', 'розгор$лосе', 'разгор$лось'):
        assert bm.corpus_words('byliny', surface) == [surface]
        assert Token('byliny', '?unknown', surface, 'x', {}, True, 'verb').lemma == 'разгореться'
    assert bm.corpus_words('byliny', 'лось лоси лосе') == ['лось', 'лоси', 'лосе']
    assert bm.corpus_words('vuk', 'розгор$лоси') == bm.words('розгор$лоси')


def test_reviewed_material_boundaries():
    for filename, n in [('pesnisobrannyepvkireevskimch2vyp57_djvu.txt', 8979),
                        ('10945725bsb_djvu.txt', 24393),
                        ('pesnisobrannyepvkireevskimch3vyp51_djvu.txt', 11694)]:
        assert excluded_source('byliny', filename, n)
        assert not excluded_source('byliny', filename, n + 1)
    uid = 'oldirish-tbc-windisch-1905:diealtirischehel00wind:L24627-L24628'
    assert repair_celtic_rows([{'id': uid, 'text': 'fixture'}]) == []
    assert repair_celtic_rows([{'id': uid.replace('24627-L24628', '24632-L24633'), 'text': 'fixture'}])


def test_resolved_mappings_and_rejected_report():
    av = mp.resolve_table('av')
    assert av['prakṛti'].ids == {'pie-root-kwer-do'}
    assert av['akṣi'].ids == {'pie-lex-h3okws'}
    assert av['akṣa'].ids == {'pie-lex-h2ekjs'}  # actual axles unchanged
    for c in ('grp', 'hom'):
        t = mp.resolve_table(c)
        assert all(k not in t for k in ('κέρδος', 'κερδαίνω', 'Πειρίθοος', 'Ἀντιγόνη'))
    assert 'песок' not in mp.resolve_table('byliny')
    assert mp.resolve_table('lat')['caelum'].ids == {'pie-lex-keh2ilos'}
