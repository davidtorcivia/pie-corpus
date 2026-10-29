"""Wave-4 Irish context regressions and conservative homograph boundaries."""
import pytest
from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows


@pytest.mark.parametrize('words,index,baseline,target', [(['fo', 'daig', 'tathar'], 1, 'daig', 'dáig@because'),
 (['fochen', 'lind', 'do'], 1, 'lind', 'la'),
 (['Fochen', 'lind', 'do'], 0, '?fochen', 'fochen@welcome'),
 (['Aodh', 'mend'], 0, 'aodh', 'aodh (name)'),
 (['coirp', 'chriad'], 1, 'crenaid', 'cré@clay'),
 (['lathi', 'aidche', 'and'], 1, 'adaig', 'adaig@night'),
 (['ro', 'theigh', 'ro', 'folaig'], 1, 'téigh', 'teichid'),
 (['na', 'rígh', 'thes', 'ar'], 2, 'thés|téit|tés', 'tess@south'),
 (['is', 'airc', 'dúnn'], 1, 'arc|airc|árc', 'airc@need'),
 (['in', 'cuan', 'lan', 'do', 'longaib'], 1, 'cúan|cúán', 'cúan@harbour'),
 (['Fäid', 'iter', 'na', 'faidib'], 0, 'fid', 'fáith'),
 (['ög', 'iter', 'na', 'h-ögaib', 'apstal'], 3, 'gaibid|congaib|etargaib', 'óg@virgin'),
 (['lem', 'or', 'si-si'], 1, 'ór', 'ol'),
 (['do', 'orgain', 'in', 'sidiu'], 1, 'orgán', 'orgain@slaying'),
 (['co', 'ndēni', 'íar'], 1, 'dogní', 'déne@speed'),
 (['Forecmaing', 'sin', 'scíath'], 0, '?forecmaing', 'doecmaing'),
 (['ósa', 'broind', 'coro'], 1, '?broind', 'brú@belly'),
 (['síl', 'nÁdaim', 'do'], 1, 'fadaigh', 'ádam (name)'),
 (['don', 'uig', 'ucut'], 1, 'og', 'og@egg'),
 (['acht', 'gē', 'atá'], 1, 'gé|guidid', 'gé@although'),
 (['go', 't-tarladar', 'for', 'dhuirteach'], 1, 'adgládathar', 'tarla@happen')])
def test_reviewed_context_and_unrelated_homograph(words, index, baseline, target):
    form = words[index]
    z = cm.CelticLemmatizer(
        fm.LangMapping('sga'), cm.irish_demutate, cm.irish_skeleton,
        form_overrides={fm.key_sga(cm._ir_clean(form)): baseline}, use_skeleton=False)
    assert cm.lemmatize_words(z, words)[index] == target
    assert z(form) == baseline
    # corpus-quality batch 1 made these readings general rules (pie.celtic_mapping._cq1_irish_rule;
    # error-verdicts-cq1-celtic.jsonl): outside the old reviewed context they now give the rule's lemma.
    cq1_general = {'airc': 'airc@need', 'gráin': 'gráin@fear', 'gona': 'co'}
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == cq1_general.get(form, baseline)


def test_welcome_and_conjunctions_do_not_become_names_or_content():
    lm = fm.LangMapping('sga')
    for lemma, surface in [('fochen@welcome', 'Fochen'), ('dáig@because', 'daig'),
                           ('gé@although', 'gē'), ('la', 'lind'), ('ol', 'or')]:
        assert not cm.content_of(lm, lemma, surface)


def test_reviewed_roots_and_rejected_report():
    t = cm.read_table('celt')
    assert t['fili'] == ('pie-root-wel-see',)
    assert not t.get('gal')
    assert t['tús'] == ('pie-root-weyd-see',)
    assert t['daig'] == ('pie-lex-dhegwhis',)


def test_reported_footnote_is_excluded_by_material_review():
    uid = 'oldirish-tbc-windisch-1905:diealtirischehel00wind:L24627-L24628'
    rows = [{'id': uid, 'text': 'editorial quotation'},
            {'id': 'other:L24627-L24628', 'text': 'unrelated source'}]
    assert repair_celtic_rows(rows) == [rows[1]]


def test_initial_name_rule_leaves_existing_medial_name_handling_alone():
    z = cm.CelticLemmatizer(
        fm.LangMapping('sga'), cm.irish_demutate, cm.irish_skeleton,
        form_overrides={'aodh': 'aodh'}, use_skeleton=False)
    assert cm.lemmatize_words(z, ['Aodh', 'Mend']) == ['aodh (name)', '?mend']
    assert cm.lemmatize_words(z, ['ocus', 'Aodh', 'Mend'])[1] == 'aodh'
    assert cm.lemmatize_words(z, ['aodh', 'Mend'])[0] == 'aodh'
