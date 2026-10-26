"""Wave 7 contextual readings; evidence in error-verdicts-w7-other.jsonl.

Keys are actual loader word coordinates, not review-window start labels.
Unreviewed homonyms and original surface strings are preserved.
"""

GREEK = {
    ('Herodotus Historiae 3.64.5 s1', 'ἐπειρόμενος', 'ἐπιλέγω'): 'ἐπείρομαι',
    ('Hesiodus Fragmenta 136.3', 'Κοίρανον', 'Κοίρανος'): 'Κοίρανος (name)',
    ('Euripides Bacchae 492', 'δεῖ', 'δέω'): 'δέω@need',
    ('Herodotus Historiae 4.199.2 s1', 'ἐκπέποται', 'ἐκπίπτω'): 'ἐκπίνω',
    ('Thucydides Historiae 2.29.3 s1', 'Θρᾳκῶν', 'Θρᾷξ'): 'Θρᾷξ (name)',
    ('Herodotus Historiae 3.60.4 s1', 'νηὸς', 'ναῦς'): 'ναός@temple',
    ('Herodotus Historiae 3.60.4 s1', 'νηῶν', 'ναῦς'): 'ναός@temple',
    ('Herodotus Historiae 1.98.3 s2', 'Μήδων', 'Μῆδος'): 'Μῆδος (name)',
    ('Il. 3.174', 'λιποῦσα', 'λιπάω'): 'λείπω',
}

# Text id, exact word id, surface, incoming lemma -> reviewed lemma.
ARMENIAN = {
    ('MH_1_1_04_Faustos', 37133, 'Արեաց', 'ariwn'): 'ari (name)',
    ('MH_1_1_04_Faustos', 24984, 'յայրումն', 'ayr'): 'ayrowmn',
    ('MH_1_1_04_Faustos', 24990, 'հունձք', 'hown'): 'hownjkʻ',
    ('MH_1_2_12_Movses_Khor', 47211, 'Ձիրաւ,', 'jir'): 'Jiraw (name)',
    ('MH_1_1_04_Faustos', 4840, 'Նիկիա,', 'nikem'): 'Nikia (name)',
    ('MH_1_1_04_Faustos', 4838, 'սիւնհոդոսին', 'siwdopown'): 'siwnhodos',
    ('MH_1_2_12_Movses_Khor', 18401, 'Դարեհի', 'darem'): 'Dareh (name)',
    ('MH_1_2_12_Movses_Khor', 18391, 'Միհրդատայ', 'mirdahar'): 'Mihrdat (name)',
    ('MH_1_2_12_Movses_Khor', 18400, 'Միհրդատայ,', 'mirdahar'): 'Mihrdat (name)',
    ('MH_1_2_12_Movses_Khor', 18394, 'բդեշխի', 'bčem'): 'bdeašx',
    ('MH_1_1_06_Yeghishe', 71033, 'լցուցիչն', 'lowcʻanem'): 'lcʻowcʻičʻ',
    ('MH_1_2_12_Movses_Khor', 82371, 'յորդաբուղխ', 'ordaxowtʻiwn'): 'yordabowłx',
}


def armenian_name(lemma, surface, locus):
    """Exclude precisely the reviewed names, retaining their context tokens."""
    return any(new == lemma and form == surface and locus.startswith(text + ' ed.')
               and locus.endswith(f'(word id {word_id})')
               for (text, word_id, form, old), new in ARMENIAN.items()
               if new.endswith(' (name)'))


def reviewed_lemma(corpus, lemma, surface, locus):
    if corpus == 'lat' and (locus, surface, lemma) == ('LucrDRN3 3.1025', "Ancu'", 'ancus'):
        return 'Ancus (name)'
    if corpus in {'grc', 'grp', 'grc-late', 'hom'}:
        return GREEK.get((locus, surface, lemma), lemma)
    if corpus in {'av', 'sa-ep'}:
        return {
            ('AVŚ, 18, 1.s77', 'kṣām', 'kṣā'): 'kṣam@earth',
            ('Rām, Bā, 72.s53', 'tūrya', 'tṛ'): 'tūrya',
            ('MBh, 1, 100.s2', 'satyavatī', 'satyavatī'): 'satyavatī (name)',
        }.get((locus, surface, lemma), lemma)
    if corpus == 'orv' and (locus, surface, lemma) == ('lav 66.1', 'доити', 'доити'):
        return 'доити@go'
    if corpus == 'xcl' and '(word id ' in locus:
        text = locus.split(' ed.')[0]
        word_id = locus.rsplit('(word id ', 1)[1].split(')', 1)[0]
        if word_id.isdigit():
            return ARMENIAN.get((text, int(word_id), surface, lemma), lemma)
    return lemma
