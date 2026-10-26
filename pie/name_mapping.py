"""One gate for source-tagged names that are themselves inherited lexemes.

Use the corpus's production ids, then the secure checker's exact/formation
semantics. Never infer inheritance from a component, spelling, or capitalization.
Explicit contextual name repairs remain authoritative (already suffixed lemmas).
"""
from functools import lru_cache
from types import SimpleNamespace

from . import mapping as mp

# These are personal-name homographs, not personified inherited nouns.
# Keys use the production language normalizer; only source-tagged names hit them.
PERSONAL_HOMOGRAPHS = {
    'grc': {
        'πάτροκλος': "Πάτροκλος is compound; the reviewed override lists πατήρ and κλέος as members, not whole-word matches.",
        'εὐρύκλεια': "Εὐρύκλεια is compound; the reviewed override lists εὐρύς and κλέος as members, not whole-word matches.",
        'κλεάνωρ': "Κλεάνωρ is compound; Kaikki's direct *ḱléwos link supplies only the first member.",
        'ζήνων': "Ζήνων is a derivative personal name, not Ζεύς itself; its direct *dyḗws link loses the name suffix.",
        'ἀρκαδία': "Ἀρκαδία is a derived place name, not the inherited word for bear; its *h₂ŕ̥tḱos link is a base.",
        'στέντωρ': "Στέντωρ is an agent-name formation in -τωρ; *(s)tenh₂- is its derivational base.",
        'λύκος': "Source-tagged Lycus (personal/place name), not the inherited common noun λύκος 'wolf'; wave-6 homograph review.",
    },
    'non': {
        'oddr': "Personal name Oddr; not the common noun 'point' (reviewed_menota_lemma, earlier source review).",
        'hallr': "Personal name Hallr; the common noun 'slope' is a different sense (wave-6 Menota review).",
        'ulfr': "Personal name Úlfr/Ulfr; not the common noun 'wolf' (wave-6 Menota review).",
        'úlfr': "Personal name Úlfr (accented spelling); not the common noun 'wolf' (wave-6 Menota review).",
        'finnr': "Personal name Finnr; not an inherited common-word lexeme (wave-6 Menota review).",
        'oddur': "IcePaHC spelling of the reviewed personal name Oddr, not 'point'.",
        'hallur': "IcePaHC spelling of the reviewed personal name Hallr, not 'slope'.",
        'úlfur': "IcePaHC spelling of the reviewed personal name Úlfr, not 'wolf'.",
        'steinarr': "Steinarr is compound: the automatic path reaches only *warjaz 'defender'; Kaikki non s.v. Steinarr.",
        'ívarr': "Ívarr is compound: the automatic path reaches only *īwaz 'yew'; Kaikki non s.v. Ívarr.",
        'ívar': "IcePaHC Ívar maps through the Ívarr compound's yew component.",
        'ögmundr': "Ǫgmundr is compound: the path reaches only *agjō; Kaikki non s.v. Ǫgmundr.",
        'danmǫrk': "Place name Danmǫrk is compound; *daniz is only its first component; Kaikki non s.v. Danmǫrk.",
        'danmörk': "IcePaHC spelling of Danmǫrk, whose mapping is only a compound component.",
        'einar': "IcePaHC Einarr maps only to *ainaz 'one'; the personal name is compound (earlier Menota name review).",
        'gestr': "Personal name Gestr at Menota AM-132-fol-Finnboga-saga 100r:15; not the common noun 'guest'.",
        'gestur': "IcePaHC spelling of the personal name Gestr; not the common noun 'guest'.",
        'brandr': "Personal name Brandr at Menota AM-132-fol-Finnboga-saga 112v:29; not the common noun 'brand'.",
        'brandur': "IcePaHC spelling of the personal name Brandr; not the common noun 'brand'.",
        'hrafn': "Personal name Hrafn at Menota AM-132-fol-Egils-saga 70v:27; not the common noun 'raven'.",
        'finna': "IcePaHC's name-tagged Finnr is mislemmatized as the verb finna 'find' (wave-6 review).",
    },
}

POPULATION = {'grc': 'grp', 'grc-late': 'grp', 'sa-ep': 'av'}
LANGUAGE = {'hom': 'grc', 'grp': 'grc', 'lat': 'la', 'av': 'sa',
            'menota': 'non', 'icepahc': 'non', 'orv': 'orv'}
LANG_LABEL = {'grc': 'Ancient Greek', 'la': 'Latin', 'sa': 'Sanskrit',
              'non': 'Old Norse', 'orv': 'Old East Slavic'}


@lru_cache(maxsize=1)
def _lexicon():
    from .formula_search import load_jsonl
    return load_jsonl(mp.ROOT / 'data/lexicon/lexicon.jsonl')


@lru_cache(maxsize=None)
def _live_mapping(lang):
    """Production live resolver over dictionary/reflex vocabulary, without Tokens.

    This avoids loader recursion and amortizes dictionary resolution across names.
    No surface-majority inference is used to establish a bare lemma's identity.
    """
    from . import formula_search as fs
    lex = _lexicon()
    links = fs.load_kaikki_links(lang)
    words = {r['word'] for r in links} | {r['roman'] for r in links if r.get('roman')}
    labels = {'grc': fs.GRC_LANGS, 'la': fs.LAT_LANGS, 'sa': fs.SKT_LANGS}[lang]
    for e in lex:
        words.update(fs._reflex_forms(e, labels, roman=lang == 'sa'))
    ts = [SimpleNamespace(lemma=w, surface=w, content=True) for w in sorted(words)]
    back = (fs.build_homer_mapping(lex, ts) if lang == 'grc' else
            fs.build_latin_mapping(lex, ts) if lang == 'la' else None)
    return fs.build_kaikki_mapping(lang, lex, ts, back, links=links, pseudo=True)


@lru_cache(maxsize=1)
def _orv_dictionaries():
    from . import formula_search as fs, formula_search_multi as fm
    lex = _lexicon()
    db = fm.ProtoDB(want_desc=[c for lang in ('orv', 'cu') for c in fm.LANGS[lang].desc_codes])
    idx = fs.PieIndex(lex)
    return tuple(fm.build_lang_mapping(lang, lex, db, idx=idx) for lang in ('orv', 'cu'))


def orv_mapping(tokens):
    """Stage B's Old Russian dictionary with Church Slavonic backoff."""
    from . import formula_search as fs, formula_search_multi as fm
    gmap = fs.group_map(_lexicon())
    primary, backoff = [fm.corpus_mapping(tokens, lm, gmap=gmap) for lm in _orv_dictionaries()]
    ids = {**backoff[0].lemma_lex, **primary[0].lemma_lex}
    return fm.apply_table_overrides('orv', ids), {**backoff[1], **primary[1]}


@lru_cache(maxsize=None)
def _resources(population):
    from . import tier2_secure as secure
    lang = LANGUAGE[population]
    ov = mp.load_overrides()
    # A corpus decision must not be replaced by another corpus's homograph.
    local = {**ov, 'decisions': {population: ov['decisions'].get(population, {})},
             'lemma': {population: ov['lemma'].get(population, {})}}
    rows = mp.read_table(population)
    if population == 'orv':
        dictionaries = _orv_dictionaries()
        words = {r.word for lm in dictionaries for r in lm.recs.values()}
        _, recs = orv_mapping([SimpleNamespace(lemma=w) for w in words])
        rows = [dict(corpus='orv', lang='orv', lemma=w, word=r.word, lex_id=list(r.ids),
                     path=list(r.path), how=r.how, confidence=r.confidence) for w, r in recs.items()]
    # IcePaHC's table is tagged modern 'is', but its historical tokens use
    # the checker's Old Norse formation rules. Keep the corpus decisions local.
    checker_rows = [{**r, 'lang': 'non'} for r in rows] if population == 'icepahc' else rows
    pop = secure.build_population({population: checker_rows}, local, added=False)
    entries = {e['id']: e for e in _lexicon()}
    ch = secure.SecureChecker.from_population(
        entries, pop, lambda: (secure.load_kaikki_tables(entries, (lang,)),)
        if lang in {'grc', 'la', 'sa'} else ())
    resolved = mp.resolve_rows(population, rows, local)
    return lang, local, resolved, ch


@lru_cache(maxsize=None)
def exact_name_ids(corpus, lemma):
    """Exact production lexeme ids of an unqualified source-tagged name."""
    from . import formula_search as fs
    from . import tier2_secure as secure
    population = POPULATION.get(corpus, corpus)
    if population not in LANGUAGE or lemma.endswith(' (name)'):
        return frozenset()
    lang, ov, resolved, checker = _resources(population)
    if mp._keyer(lang)(lemma) in PERSONAL_HOMOGRAPHS.get(lang, {}):
        return frozenset()
    if population == 'orv':
        ids = orv_mapping([SimpleNamespace(lemma=lemma)])[0].get(lemma, frozenset())
    elif population in {'hom', 'grp', 'lat'} or corpus == 'sa-ep':
        m = _live_mapping(lang)
        # Production lemma key normalizations; preserve corpus-specific decisions.
        wk = fs.word_key_for(lang)
        ids = m.lemma_lex.get(lemma)
        if ids is None:
            ids = _live_keys(lang).get(wk(lemma), frozenset())
        ids, _ = mp.decide(population, lemma, ids, ov)
        if corpus == 'sa-ep' and lemma in resolved:
            ids = resolved[lemma].ids
    else:
        r = resolved.get(lemma)
        # These routes explicitly strip a productive component; the secure
        # checker historically accepts some prefix paths as exact. Names must
        # be the whole lexeme, so do not admit those component-only routes.
        component = r and (r.how in {'base', 'root', 'prefix', 'compound'} or
                           any(p.startswith(('prefix:', 'base:', 'compound:', 'privative:')) for p in r.path))
        ids = r.ids if r and not component else frozenset()
    return frozenset(i for i in ids if i.startswith('pie-lex-') and
                     (hit := checker.match(i, secure.code_of(population, lang), LANG_LABEL[lang], lemma, True)) and
                     hit['level'] == 'exact' and
                     not any(p.startswith(('preverb:', 'prefix:', 'base:', 'compound:', 'privative:'))
                             for p in hit['path']))


@lru_cache(maxsize=None)
def _live_keys(lang):
    from .formula_search import word_key_for
    wk = word_key_for(lang)
    return {wk(k): v for k, v in _live_mapping(lang).lemma_lex.items()}


def name_lemma(corpus, lemma):
    """Preserve exact inherited words; qualify all other annotated names."""
    if lemma.endswith(' (name)') or exact_name_ids(corpus, lemma):
        return lemma
    return lemma + ' (name)'
