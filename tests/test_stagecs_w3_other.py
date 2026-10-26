"""Wave 3 independently reviewed source corrections and negative controls."""
from dataclasses import replace
from pathlib import Path

from pie.formula_search import Token
from pie.formula_search_multi import load_overrides
from pie.germanic_new_mapping import MenotaWord, menota_words
from pie.material_units import repair_menota_words, reviewed_daina_quote
from pie.other_mapping import contextual_lemma

ROOT = Path(__file__).resolve().parents[1]


def test_contextual_lemmas_preserve_homographs_and_source_surfaces():
    cases = [
        ('grc', 'φέρω', 'ἐνείκῃ', 'Hesiodus Opera et dies 563', 'φέρω@aorist'),
        ('grc', 'κέλευθος', 'κελεύσματος', 'Thucydides Historiae 2.92.1 s1', 'κέλευσμα'),
        ('grc', 'λιπάω', 'λιποῦσα', 'Euripides Ion 1403', 'λείπω'),
        ('grc', 'καταλέγω', 'καταρησάμενοι', 'Herodotus Historiae 2.39.2 s1', 'καταράομαι'),
        ('grc', 'δέω', 'δέεσθαι', 'Herodotus Historiae 2.126.1 s3', 'δέω@need'),
        ('hom', 'ἐλύω', 'ἔλυσεν', 'Il. 5.176', 'λύω'),
        ('sa-ep', 'droṇa', 'droṇasya', 'MBh, 9, 7.s28', 'Droṇa (name)'),
        ('xcl', 'or', 'որսոց,', 'MH_1_2_12_Movses_Khor ed. page 1867 - PDF page 125 (word id 18372)', 'ors'),
        ('xcl', 'mayr', 'Մարի,', 'MH_1_1_04_Faustos ed. page 346 - PDF page 70 (word id 28360)', 'Mari (name)'),
        ('xcl', 'bambir', 'Բամբիշն', 'MH_1_1_04_Faustos ed. page 311 - PDF page 35 (word id 13418)', 'Bambišn (name)'),
        ('xcl', 'tiranam', 'Տիրանայ։', 'MH_1_1_04_Faustos ed. page 311 - PDF page 35 (word id 13422)', 'Tiran (name)'),
    ]
    for corpus, lemma, surface, locus, expected in cases:
        t = Token(corpus, lemma, surface, locus, {}, True, 'noun')
        assert (t.lemma, t.surface) == (expected, surface)
        assert contextual_lemma(corpus, lemma, surface, 'control') == lemma


def test_suppletion_does_not_change_present_or_causative():
    assert contextual_lemma('grc', 'ὁράω', 'εἶδον', 'x') == 'εἶδον@see'
    assert contextual_lemma('grc', 'ὁράω', 'ὁρᾷ', 'x') == 'ὁράω'
    for form in ('veda', 'vidma'):
        assert contextual_lemma('av', 'vid', form, 'x') == 'vid@perfect'
    assert contextual_lemma('av', 'vid', 'vedayati', 'x') == 'vid'
    ov = load_overrides(ROOT)['lemma']
    assert set(ov['av']['vid@perfect'][0]) == {'pie-root-weyd-see'}
    assert set(ov['grp']['φέρω@aorist'][0]) == {'pie-root-h1nekj-receive'}
    for lemma in ('Ἶρις', 'Περίανδρος', 'Ἕκτωρ', 'Νικίας', 'Ἀριστεύς'):
        assert not ov['grp'][lemma][0]
    assert not ov['hom']['Ἕκτωρ'][0]


def test_menota_brackets_keep_restorations_and_unreviewed_contexts(tmp_path):
    forms = ['word', '[sára]', '[sára', 'er', 'underprikka', 'der]', 'after']
    xml = '<text><pb n="8"/>' + ''.join(f'<w><me:dipl>{f}</me:dipl></w>' for f in forms) + '</text>'
    p = tmp_path / 'sample.xml'
    p.write_text(xml)
    assert [w.form for w in menota_words(p, 'AM-36-fol')] == ['word', '[sára]', 'after']
    assert [w.form for w in menota_words(p, 'control')] == forms
    nested = [MenotaWord('AM-36-fol', None, '', f, '17', '', None, 1)
              for f in ['[note', '[vinr]', 'underprikka', 'end]', 'verse']]
    assert [w.form for w in repair_menota_words(nested)] == ['verse']


def test_material_joins_do_not_mark_unlemmatized_documents_as_lemmatized():
    for doc, folio, forms, expected in [
        ('AM-35-fol', '201', ['ey', 'dana'], ['eydana']),
        ('AM-63-fol', '62', ['breno', 'steini'], ['brenosteini']),
        ('AM-36-fol', '15', ['brygiorsverþ'], ['brygior', 'sverþ']),
    ]:
        ws = [MenotaWord(doc, None, '', f, folio, '', None, 1) for f in forms]
        fixed = repair_menota_words(ws)
        assert [w.form for w in fixed] == expected
        assert all(w.lemma is None for w in fixed)
        assert repair_menota_words(fixed) == fixed
        assert [w.form for w in repair_menota_words([replace(w, folio='other') for w in ws])] == forms
    assert not reviewed_daina_quote('p0341', 1046)
    assert reviewed_daina_quote('p0341', 0)
    assert reviewed_daina_quote('p0342', 1046)
