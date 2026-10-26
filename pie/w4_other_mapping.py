"""Wave 4 source-verified corrections; evidence in error-verdicts-w4-other.jsonl."""


def reviewed_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    if corpus in {'grc', 'grp', 'grc-late', 'hom'}:
        if lemma in {'Ἀντιγόνη', 'Πειρίθοος', 'Ἱππίας', 'Λυκόφρων', 'Εὐρύλοχος'}:
            return lemma + ' (name)'
        if (locus, surface, lemma) == ('Thucydides Historiae 1.26.4 s1', 'κατάξοντες', 'κατάγνυμι'):
            return 'κατάγω'
    if corpus == 'lat' and (locus, surface, lemma) == ('LucrDRN1 1.1064', 'uolare', 'uolo'):
        return 'uolo@fly'
    if corpus == 'orv':
        if lemma == 'пльсковъ':
            return 'пльсковъ (name)'
        if (locus, surface, lemma) == ('lav 77.15', 'блудъ', 'блудъ'):
            return 'блудъ (name)'
    if corpus == 'vuk' and (locus, surface) == ('Vuk 21685:776', 'жели'):
        return 'željeti'
    if corpus == 'byliny' and surface.lower() in {
        'розгор$лось', 'розгор$лоси', 'розгор$лосе', 'розгор$лося',
        'разгор$лось', 'разгор$лоси', 'разгор$лосе', 'разгор$лося',
    }:
        return 'разгореться'
    if corpus == 'byliny' and (locus, surface) == ('10945725bsb:4924', 'веЪхъ'):
        # Qualified quantifier: unqualified весь also denotes a village.
        return 'весь@all'
    if corpus in {'av', 'sa-ep'}:
        if (locus, lemma) == ('MBh, 13, 3.s24', 'vasiṣṭha'):
            return 'Vasiṣṭha (name)'
        if (locus, surface, lemma) == ('MBh, 1, 93.s59', 'ādyaiḥ', 'ādya'):
            return 'ādya@first'
        if lemma == 'akṣa' and (locus, surface) in {
            ('AVP, 10, 6.s30', 'akṣaḥ'), ('MBh, 7, 57.s152', 'akṣaḥ'),
            ('MBh, 9, 44.s212', 'akṣāḥ'),
        }:
            return 'akṣi'
    if corpus == 'xcl':
        fixes = {
            ('MH_1_1_04_Faustos', '60413', 'gind'): 'Gind (name)',
            ('MH_1_1_04_Faustos', '60750', 'gind'): 'Gind (name)',
            ('MH_1_1_06_Yeghishe', '88650', 'hown'): 'hunǰkʻ',
            ('MH_1_1_06_Yeghishe', '88658', 'kesak'): 'keam',
            ('MH_1_1_06_Yeghishe', '88648', 'vayr'): 'varkʻ@cultivation',
            ('MH_1_1_04_Faustos', '51764', 'ownim'): 'yoyn (name)',
            ('MH_1_2_12_Movses_Khor', '30497', 'ownim'): 'yoyn (name)',
        }
        for (work, word, old), new in fixes.items():
            if locus.startswith(work + ' ') and f'(word id {word})' in locus and lemma == old:
                return new
    return lemma
