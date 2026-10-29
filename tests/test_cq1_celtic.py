"""Corpus-quality batch 1, Celtic: general homograph rules (with their exceptions), reviewed
contexts, table decisions and the exact-coordinate name readings.

Evidence: data/research/8c/corpus-quality/error-verdicts-cq1-celtic.jsonl."""
import pytest

from pie import celtic_mapping as cm
from pie import formula_search as fs
from pie import formula_search_multi as fm


def lz(form, baseline, lang="sga"):
    key = fm.key_sga(cm._ir_clean(form)) if lang == "sga" else cm.key_cy(cm.welsh_norm(form, True))
    if lang == "sga":
        return cm.CelticLemmatizer(fm.LangMapping("sga"), cm.irish_demutate, cm.irish_skeleton,
                                   form_overrides={key: baseline}, use_skeleton=False)
    return cm.CelticLemmatizer(fm.LangMapping("cy"), cm.welsh_demutate, cm.welsh_skeleton,
                               norm=lambda w: cm.welsh_norm(w, True), form_overrides={key: baseline},
                               use_skeleton=False)


GENERAL = [
    # día: preposition + possessive / relative by default; day, god, foreign by context
    (['slógh', 'día', 'ndóinib'], 1, 'día', 'do'),
    (['cidh', 'día', 'tá'], 1, 'día', 'do'),
    (['Día', 'nderṅta-su'], 0, 'día', 'do'),
    (['Día', 'lim', 'fri', 'cach', 'sním'], 0, 'día', 'día@god'),
    (['Día', 'ocus', 'Chíaran'], 0, 'día', 'día@god'),
    (['slógh', 'día', 'ar'], 1, 'día', 'do'),                     # the God exception is unit-initial only
    (['dia', 'Sathairn'], 0, 'día|dia', 'día@day'),
    (['go', 'dia', 'bratha'], 1, 'día|dia', 'día@day'),
    (['dot-icfa', 'cech', 'día'], 2, 'día', 'día@day'),
    (['cach', 'dia', 'chéile'], 1, 'día|dia', 'día|dia'),          # each to the other: not day
    (['cach', 'dia', 't-tighibh'], 1, 'día|dia', 'día|dia'),       # each to their houses
    (['cach', 'día', 'thig'], 1, 'día', 'do'),
    (['Dia', 'nime'], 0, 'día|dia', 'día@god'),
    (['DÍA', 'MÁR', 'mo'], 0, 'día', 'día@god'),
    (['in', 'dia', 'mor', 'Apaill'], 1, 'día|dia', 'día@god'),
    (['dia', 'maoín', 'nó', 'dia', 'mór', 'maithęs'], 3, 'día|dia', 'día|dia'),  # of his great goods
    (['in', 'hoc', 'die'], 2, 'día', 'die@foreign'),
    (['in', 'die', 'Sancti', 'Martini'], 1, 'día', 'die@foreign'),
    (['Die', 'Söhne', 'des'], 0, 'día', 'die@foreign'),
    (['ar', 'Día'], 1, 'día', 'día@god'),   # medial capital: cq2 Dia 'God' rule (was: the name rule decides)
    # gona: co + possessive, but the verbal noun after the article / possessive / do, or before nó
    (['ri', 'gona', 'ferann'], 1, 'goin|gonaid|guin', 'co'),
    (['bruth', 'na', 'gona'], 2, 'goin|gonaid|guin', 'goin|gonaid|guin'),
    (['ar', 'eiccill', 'a', 'gona'], 3, 'goin|gonaid|guin', 'goin|gonaid|guin'),
    (["d'iarraidh", 'gona', 'nó', 'gabhala'], 1, 'goin|gonaid|guin', 'goin|gonaid|guin'),
    # gonadh: 'so that'; 'was wounded' after ro / do / coro
    (['Gonadh', 'uime', 'sin'], 0, 'goin', 'conid'),
    (['dib', 'gonid', 'de-sin'], 1, 'nigh', 'conid'),
    (['ro', 'gonadh', 'in', 'rí'], 1, 'goin', 'goin'),
    (['do', 'gonadh', 'é'], 1, 'goin', 'goin'),
    (['coro', 'gonad', 'Fiachra'], 1, 'gónad', 'gónad'),
    # asna: as + plural article before a plural noun; the rib after a possessive / tria / dá
    (['dotiagat', 'asna', 'foclaib', 'sin'], 1, 'easna', 'as'),
    (['techt', 'asna', 'h-inadaibh'], 1, 'easna', 'as'),
    (['tebiu', 'asna', 'di', 'berlaibh'], 1, 'easna', 'as'),
    (['brúis', 'trí', 'asna', 'isin'], 2, 'easna', 'easna'),
    (['slicht', 'a', 'asna', 'tria'], 2, 'easna', 'easna'),
    (['gor', 'bhris', 'asna'], 2, 'easna', 'easna'),
    # gráin: horror, but the grain before a cereal / after na
    (['ba', 'mór', 'a', 'gráin', 'a', 'eagla'], 3, 'grán|gráin', 'gráin@fear'),
    (['ro', 'gab', 'grain', 'ecla'], 2, 'grán|gráin', 'gráin@fear'),
    (['ochtmad', 'grain', 'eorna'], 1, 'grán|gráin', 'grán|gráin'),
    (['ithe', 'an', 'ghráin', 'ghlais'], 2, 'gráin', 'gráin'),
    (['anois', 'na', 'grain', 'is'], 2, 'grán|gráin', 'grán|gráin'),
    # Dál + people is a tribal name; dál Temra 'assembly of Tara' and plain dál stay
    (['i', 'n-Dál', 'Araidhe'], 1, 'dáilid', 'dál (name)'),
    (['co', 'nDal', 'nAraide'], 1, 'dáilid', 'dál (name)'),
    (['Dal', 'Riada'], 0, 'dál', 'dál (name)'),
    (['gur', 'éirgedar', 'dál', 'Cais'], 2, 'dál', 'dál (name)'),
    (['dáile', 'dál', 'Temra'], 1, 'dál', 'dál'),
    (['doíne', 'dál'], 1, 'dál', 'dál'),
    # risin: ri / re + article; eitir: between, or étir 'possible'
    (['dorad', 'taobh', 'risin', 'ccrín'], 2, 'rísín', 'fri'),
    (['iomcháineadh', 'eitir', 'Mhuirghil'], 1, 'eitigh', 'eter'),
    (['ní', 'h-eitir', 'a', 'riomh'], 1, 'eitigh', 'étir@possible'),
    (['ba', 'héitir', 'lais'], 1, 'eitigh', 'étir@possible'),
    # airc: plundered after ro / cur, otherwise need / ark; never the piglet
    (['co', 'ro', 'airc', 'Cluain'], 2, 'arc|airc|árc', 'orcaid'),
    (['cur', 'airc', 'an', 'tir'], 1, 'arc|airc|árc', 'orcaid'),
    (['isin', 'airc', 'isin', 'éiccen'], 1, 'arc|airc|árc', 'airc@need'),
    # galaib: gal 'valour, combat', not fichid
    (['ar', 'galaib', 'óenḟir'], 1, 'fichid', 'gal'),
]


@pytest.mark.parametrize('words,index,baseline,target', GENERAL)
def test_irish_general_rules_and_exceptions(words, index, baseline, target):
    z = lz(words[index], baseline)
    assert z(words[index]) == baseline
    assert cm.lemmatize_words(z, words)[index] == target


REVIEWED = [
    (['cutiMmmus', 'fri', 'a', 'muá', 'ocus', 'is', 'áil'], 3, 'mua', 'ben'),
    (['ocus', 'is', 'áil', 'lin', 'ni'], 3, 'lín', 'la'),
    (['Bôi', 'lin', 'argdide', 'assa'], 1, 'lín', 'lín@net'),
    (['mocoU', 'ind', 'lin-sin'], 2, 'lín', 'lín@net'),
    (['Airc-siu', 'do', 'Emain', 'aridisi'], 0, 'arc|airc|árc', 'téit@secondary'),
    (['co', 'n-dírgiud', 'crette', 'fora', 'rind'], 2, 'creitid', 'crett@body'),
    (['Chulaind', 'foídis', 'in', 'aidchi', 'sin'], 1, 'foídid', 'foid'),
    (['Foidis', 'Uathach', 'la', 'Coin'], 0, 'foídid', 'foid'),
    (['ro', 'mben', 'a', 'lumain'], 1, 'ben', 'benaid'),
    (['trebar', 'dos', 'beir', 'mod'], 1, 'gus|dos', 'do'),
    (['Clu', 'i', 'che', "n-aímin"], 0, 'clú', 'cluiche'),
    (['cusna', 'cluib', 'teintidib'], 1, 'clú', 'cló'),
    (['brassaib', 'r', 'ends', 'Co'], 2, '?ends', 'ends@editorial'),
]


@pytest.mark.parametrize('words,index,baseline,target', REVIEWED)
def test_reviewed_contexts_keep_homographs_elsewhere(words, index, baseline, target):
    form = words[index]
    z = lz(form, baseline)
    assert cm.lemmatize_words(z, words)[index] == target
    # cq2: dos outside the verb contexts is the noun dos@bush (gus|dos had united it with gus 'vigour')
    expected = 'dos@bush' if baseline == 'gus|dos' else baseline
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == expected


def test_unrelated_homographs_keep_their_lemma():
    # foídis 'sends' (Foídis Medb cét fer), lín 'number', dos 'bush', mben elsewhere
    assert cm.lemmatize_words(lz('Foídis', 'foídid'), ['Foídis', 'Medb', 'cét', 'fer'])[0] == 'foídid'
    assert cm.lemmatize_words(lz('dos', 'gus|dos'), ['in', 'dos', 'dídin'])[1] == 'dos@bush'   # cq2 (was gus|dos)
    assert cm.lemmatize_words(lz('lin', 'lín'), ['in', 'lin', 'sin'])[1] == 'lín'
    assert cm.lemmatize_words(lz('rí-sin', 'rí'), ['in', 'rí-sin'])[1] == 'rí'


def test_welsh_goreu_best_only_after_yn_or_pwy():
    z = lz('oreu', 'goreu|gwneuthur', 'cy')
    assert cm.lemmatize_words(z, ['ỳn', 'oreu', 'a', 'allom'])[1] == 'goreu'
    assert cm.lemmatize_words(z, ['pwy', 'oreu', 'onadunt'])[1] == 'goreu'
    assert cm.lemmatize_words(z, ['y', 'waew', 'a', 'oreu', 'yn', 'deuhanner'])[3] == 'goreu|gwneuthur'


def test_content_status():
    lm = fm.LangMapping('sga')
    for lem, surface in (('do', 'día'), ('co', 'gona'), ('conid', 'gonadh'), ('as', 'asna'), ('fri', 'risin'),
                         ('eter', 'eitir'), ('la', 'lin'), ('die@foreign', 'die'), ('ends@editorial', 'ends')):
        assert not cm.content_of(lm, lem, surface), lem
    for lem, surface in (('día@day', 'día'), ('día@god', 'dia'), ('gráin@fear', 'gráin'), ('gal', 'galaib'),
                         ('dál (name)', 'n-Dál'), ('étir@possible', 'h-eitir'), ('crett@body', 'crette')):
        assert cm.content_of(lm, lem, surface), lem


def test_table_decisions():
    celt = cm.read_table('celt')
    assert celt['día@day'] == ('pie-lex-dyexws',)
    assert celt['día@god'] == ('pie-lex-deywos',)
    assert set(celt['día']) == {'pie-lex-deywos', 'pie-lex-dyexws'}       # bare día keeps the noun union
    for lem in ('meinic', 'menic', 'múin', 'múin|múineadh', 'crett@body', 'étir@possible', 'airc@need',
                'gráin@fear', 'lín@net', 'téit@secondary', 'gal', 'cluiche'):
        assert not celt.get(lem), lem
    assert not cm.read_table('sga-glosses').get('meinic')
    assert not cm.read_table('cy').get('goreu')
    # retained (reports rejected / unclear): EDPC supports these
    assert celt['tús'] == ('pie-root-weyd-see',)            # *to-wissu- < *weyd- (EDPC p0402)
    assert celt['tarla'] == ('pie-lex-lh1yeti',)            # *la-yo- < *leh₁- (EDPC p0248)
    assert celt['bad|baid'] == ('pie-lex-gwh2yeti',)        # *ba-yo- 'die' < 'go' (EDPC p0132)
    assert celt['mag'] == ('pie-lex-megjh2s',)              # EDPC p0267 '(?)': disputed, left
    assert celt['foid'] == ('pie-lex-h2woseti',)
    assert celt['orcaid'] == ('pie-root-h3erg-perish',)
    assert celt['cló'] == ('pie-lex-kleh2wos',)


def test_quotation_verbs_are_not_names_at_their_coordinates():
    t = fs.Token('mga', 'asbeir (name)', 'Asbert',
                 'oldirish-irische-texte-1880-1909:irischetextemitw01winduoft:L5723-L5723', {}, True, 'other')
    assert t.lemma == 'asbeir' and t.content
    t = fs.Token('sga', 'asbeir (name)', 'Asbert', 'G301012:#1/#2/#1:69', {}, True, 'other')
    assert t.lemma == 'asbeir'
    # Epir 'Epirus' (a place) keeps the name reading
    t = fs.Token('mga', 'asbeir (name)', 'Epir', 'G305001:#1/17:12', {}, True, 'other')
    assert t.lemma == 'asbeir (name)'
    # the same surface at an unreviewed coordinate is untouched
    t = fs.Token('mga', 'asbeir (name)', 'Asbert', 'unrelated:L1-L1', {}, True, 'other')
    assert t.lemma == 'asbeir (name)'
