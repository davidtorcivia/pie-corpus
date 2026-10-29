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

# Narrowed exemption (David, 2026-10-28): an exact-match name keeps its lemma
# and roots only when it names a deity or a personified natural/abstract power.
# Every other exact match (heroes, mortals, places, rivers-as-geography, titles)
# gets "(name)" like any non-exact name. Keys use the production language
# normalizer; one line per entry: the power named, and the source of the fact.
# Census and borderline decisions: docs/research/8c-theonym-narrowing.md.
THEONYMS = {
    'grc': {
        'ζεύς': "Zeus, the Sky-father (*dyḗws); handbook (West 2007 ch. 4), project lexicon pie-lex-dyexws.",
        'δεύς': "Δεύς, dialectal (Aeolic/Boeotian) form of Zeus; same Sky-father lexeme (pie-lex-dyexws).",
        'βορέας': "Boreas, the North Wind as god (Hesiod Th. 379); a personified wind.",
        'εὖρος': "Euros, the East Wind as power (Il. 2.145, Od. 5.295 wind catalogue).",
        'ἀΐδης': "Hades, god of the dead (Il. 15.188); David's example, keep.",
        'ἀΐδας': "Doric/lyric spelling of Hades, god of the dead.",
        'ἁίδας': "Doric spelling of Hades, god of the dead.",
        'ἔρεβος': "Erebos, personified primeval Darkness (Hesiod Th. 123); David's example, keep.",
        'ἥβη': "Hebe, goddess and personified Youth (Il. 4.2; Hesiod Th. 922).",
        'ἠώς': "Eos, the Dawn goddess (*h₂éwsōs); handbook (West 2007 ch. 5), pie-lex-h2ewsoxs.",
        'ὥρα': "the Hours (Ὧραι), goddesses of the seasons (Il. 5.749; Hesiod Th. 901).",
        'φόβος': "Phobos, personified Fear, companion of Ares (Il. 4.440, 13.299).",
        'νύξ': "Nyx, personified Night (Il. 14.259; Hesiod Th. 123).",
        'χθών': "Chthon, personified Earth as primeval power; pie-lex-dhegjhoxm.",
        'ἥλιος': "Helios, the Sun god (*sóh₂wl̥); pie-lex-soh2wl.",
        'μήνη': "Mene/Selene, the Moon as goddess (H. Herm. 99-100); pie-lex-mexh1ns.",
        'μήν': "Men, the Anatolian Moon god (Strabo 12.3.31); pie-lex-mexh1ns.",
        'δίκη': "Dike, goddess and personified Justice (Hesiod Th. 902, Op. 256).",
        'λήθη': "Lethe, personified Oblivion (Hesiod Th. 227) and the mythic river of the dead.",
        'μνημοσύνη': "Mnemosyne, Titaness and personified Memory (Hesiod Th. 54, 135).",
        'ὕπνος': "Hypnos, personified Sleep (Il. 14.231; Hesiod Th. 212); pie-lex-supnos.",
        'ἕσπερος': "Hesperos, the Evening Star as god (Il. 22.318); pie-lex-wekwsperos.",
        'τέρμων': "Greek rendering of the Roman boundary god Terminus (Plut. Num. 16; Dion. Hal. 2.74).",
        'κόρος': "Koros, personified Satiety, son of Hybris (Hdt. 8.77 oracle; Pind. O. 13.10).",
    },
    'la': {
        'iuppiter': "Jupiter, the Sky-father (*dyḗws ph₂tḗr); pie-lex-dyexws.",
        'diespiter': "Diespiter, archaic name of Jupiter as Sky-father; pie-lex-dyexws.",
        'uenus': "Venus, goddess (Roman pantheon).",
        'ceres': "Ceres, goddess of grain (Roman pantheon).",
        'neptunus': "Neptune, god of the sea (Roman pantheon).",
        'diana': "Diana, goddess (Roman pantheon; from *dyew- 'bright sky').",
        'minerua': "Minerva, goddess (Roman pantheon).",
        'flora': "Flora, goddess of flowering (Varro LL 5.74).",
        'fortuna': "Fortuna, goddess and personified Fortune.",
        'fors': "Fors (Fors Fortuna), personified Chance as goddess.",
        'uirtus': "Virtus, deified Valour with a Roman temple (Cic. Leg. 2.28).",
        'spes': "Spes, deified Hope with a Roman temple (Cic. Leg. 2.28).",
        'somnus': "Somnus, personified Sleep (Verg. A. 5.838).",
        'nox': "Nox, personified Night (Verg. A. 5.721).",
        'sol': "Sol, the Sun god (*sóh₂wl̥); pie-lex-soh2wl; batch-6 regression case.",
        'luna': "Luna, the Moon goddess (Varro LL 5.74); pie-lex-lowksneh2.",
        'aurora': "Aurora, the Dawn goddess (*h₂éwsōs); pie-lex-h2ewsoxs.",
        'hesperus': "Hesperus, the Evening Star personified (Catul. 62.20).",
        'uesper': "Vesper, the Evening Star personified (Catul. 62.1).",
        'auster': "Auster, the South Wind as power.",
        'terminus': "Terminus, god of boundaries (Ov. F. 2.639).",
        'manes': "Manes, the deified spirits of the dead (Di Manes).",
        'liber': "Liber, god of wine and fertility (Roman pantheon); source-tagged as a name.",
    },
    'sa': {
        'div': "Dyaus, the Sky-father (*dyḗws); RV dyaúṣ pitā́; pie-lex-dyexws.",
        'dyaus': "Dyaus, the Sky-father, if lemmatized in the nominative.",
        'uṣas': "Uṣas, the Dawn goddess (*h₂éwsōs); pie-lex-h2ewsoxs.",
        'agni': "Agni, god of Fire (*h₁n̥gʷnis); pie-lex-h1ngwnis.",
        'vāta': "Vāta, the Wind god (*h₂weh₁n̥ts).",
        'vāyu': "Vāyu, the Wind god (RV 1.2).",
        'sūrya': "Sūrya, the Sun god (*sóh₂wl̥).",
        'pṛthivī': "Pṛthivī, Earth as goddess (*pl̥th₂éwih₂); RV dyā́vāpṛthivī́.",
        'soma': "Soma, the deified sacred drink (RV book 9).",
        'mitra': "Mitra, god of the covenant (RV 3.59).",
        'bhaga': "Bhaga, god of the portion (RV 7.41).",
        'yama': "Yama, god of the dead (RV 10.14).",
        'parjanya': "Parjanya, god of Thunder and rain (RV 5.83).",
        'rātri': "Rātrī, personified Night (RV 10.127).",
    },
    'non': {
        'þórr': "Þórr, the Thunder god (*(s)tenh₂-); batch-6 regression case, pie-lex-stenh2.",
        'þór': "Spelling of Þórr, the Thunder god.",
        'höðr': "Hǫðr, the god (Gylfaginning 28); name means 'battle'.",
        'baldr': "Baldr, the god (Gylfaginning 22).",
        'týr': "Týr, the god (*deywós); not present as a bare lemma in batch 6.",
        'hel': "Hel, goddess and realm of the dead (Gylfaginning 34).",
        'áss': "Áss, 'god', one of the Æsir (*h₂énsus).",
        'guð': "Guð, God (Christian); pie-lex-gjhutos.",
        'drottinn': "Drottinn, 'the Lord' as the name of God in the IcePaHC religious texts.",
        'andi': "Andi, the Holy Spirit (heilagr andi) in the IcePaHC religious texts.",
        'jörð': "Jǫrð, personified Earth, mother of Þórr (Gylfaginning 9); pie-lex-h1erteh2.",
        'sól': "Sól, personified Sun (Gylfaginning 11); pie-lex-soh2wl.",
        'máni': "Máni, personified Moon (Gylfaginning 11); pie-lex-mexh1ns.",
        'dagr': "Dagr, personified Day (Gylfaginning 10); batch-6 regression case.",
        'dagur': "IcePaHC spelling of Dagr, personified Day.",
        'nótt': "Nótt, personified Night (Gylfaginning 10).",
        'óðr': "Óðr, the god, Freyja's husband (Gylfaginning 35); wave-9 reviewed divine exemption (AM-242-fol 55:4).",
    },
    'orv': {
        'дивъ': "Div, the mythic divine being of the Slovo o polku Igoreve (*deywós).",
        'стрибогъ': "Stribog, god of the winds (Primary Chronicle pantheon of 980).",
    },
}

# Personal homographs predate THEONYMS. With the allowlist none of them can be
# kept any more, so this table is now redundant; it stays as the record of the
# reviewed batch-6/wave-6 decisions and as a second guard.
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


# Allowlisted theonyms whose word is a reviewed derivative of the lexeme (formation "derivative": the
# secure check counts it at root level) yet is the god's own name for that power, not a homograph:
# Helios / Sūrya are the -iyo- derivative of *sóh₂wl̥ (tier2-review-r6 §4, EWAia II 742). They keep their
# roots as the narrowing rule meant (docs/research/8c-theonym-narrowing.md: the exclusions are wrong
# lexemes). Corpus-quality batch 2.
THEONYM_DERIVATIVES = {'grc': {'ἥλιος': 'pie-lex-soh2wl'}, 'sa': {'sūrya': 'pie-lex-soh2wl'}}


def theonym_allowed(corpus, lemma):
    """Reviewed deity / personified-power allowlist membership (THEONYMS)."""
    lang = LANGUAGE.get(POPULATION.get(corpus, corpus))
    return bool(lang) and mp._keyer(lang)(lemma) in THEONYMS.get(lang, {})


@lru_cache(maxsize=None)
def exact_name_ids(corpus, lemma):
    """Exact production lexeme ids of an unqualified source-tagged name that
    names a reviewed deity or personified power (THEONYMS)."""
    from . import formula_search as fs
    from . import tier2_secure as secure
    population = POPULATION.get(corpus, corpus)
    if population not in LANGUAGE or lemma.endswith(' (name)'):
        return frozenset()
    if not theonym_allowed(corpus, lemma):
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
    deriv = THEONYM_DERIVATIVES.get(lang, {}).get(mp._keyer(lang)(lemma))
    return frozenset(i for i in ids if i.startswith('pie-lex-') and
                     (hit := checker.match(i, secure.code_of(population, lang), LANG_LABEL[lang], lemma, True)) and
                     (hit['level'] == 'exact' or (hit['level'] == 'root' and i == deriv)) and
                     not any(p.startswith(('preverb:', 'prefix:', 'base:', 'compound:', 'privative:'))
                             for p in hit['path']))


@lru_cache(maxsize=None)
def _live_keys(lang):
    from .formula_search import word_key_for
    wk = word_key_for(lang)
    return {wk(k): v for k, v in _live_mapping(lang).lemma_lex.items()}


def name_lemma(corpus, lemma):
    """Preserve exact inherited theonyms; qualify all other annotated names."""
    if lemma.endswith(' (name)') or exact_name_ids(corpus, lemma):
        return lemma
    return lemma + ' (name)'
