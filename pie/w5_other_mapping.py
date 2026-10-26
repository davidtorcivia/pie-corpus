"""Source-verified wave 5 distinctions; evidence: error-verdicts-w5-other.jsonl."""


def reviewed_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    if corpus in {'grc', 'grp', 'grc-late', 'hom'}:
        if lemma in {'Ὄσσα', 'Οἰδίπους', 'Σαλαμίς', 'Ἄργος', 'Εὐβοεύς'}:
            return lemma + ' (name)'
        if (locus, lemma) == ('Thucydides Historiae 1.20.2 s1', 'Θεσσαλός'):
            return 'Θεσσαλός (name)'
        if lemma == 'ἔρχομαι' and surface == 'ἰέναι':
            return 'εἶμι'
    if corpus in {'av', 'sa-ep'}:
        fixes = {
            ('AVŚ, 12, 3.s63', 'navaṃ', 'nava'): 'nava@new',
            ('AVŚ, 18, 1.s39', 'uvāsa', 'vas'): 'vas@dawn',
            ('MBh, 12, 335.s75', 'naṣṭān', 'naś'): 'naś@perish',
            ('MBh, 9, 35.s59', 'lubdhābhyām', 'lubh'): 'lubh@desire',
            ('AVŚ, 8, 9.s26', 'tvam', 'tva'): '-tva@abstract',
        }
        return fixes.get((locus, surface, lemma), lemma)
    if corpus == 'byliny':
        if surface.lower() == 'соколей' and locus in {
            'ruws 389866:67', 'sbornikotdelenijarusskogojazykaislovesno32:11002'
        }:
            return 'сокол'
        if (locus, surface) == ('ruws 426143:11', 'темя'):
            return 'тот@demonstrative'
        if (locus, surface) == ('pesnisobrannyepnrybnikovymch2narod72:34618', 'Жена'):
            return 'жена'
    if corpus == 'vuk' and (locus, surface) == ('Vuk 36523:2', 'Тавна'):
        return 'tavan@dark'
    if corpus == 'lv' and (locus, surface) == ('BV 28993', 'ābolā'):
        return 'ābols@clover'
    if corpus == 'orv' and lemma == 'стугна':
        return 'стугна (name)'
    if corpus == 'xcl':
        fixes = {
            ('MH_1_2_11_Agathangelos', '33389', 'tawn'): 'tam',
            ('MH_1_2_13_Lazar_Parp', '3068', 'tawn'): 'tam',
            ('MH_1_2_11_Agathangelos', '33397', 'owsowcʻanem'): 'ows',
            ('MH_1_2_11_Agathangelos', '19138', 'bar̄nam'): 'barj',
            ('MH_1_2_12_Movses_Khor', '67734', 'asim'): 'Asia (name)',
        }
        for (work, word, old), new in fixes.items():
            if locus.startswith(work + ' ') and f'(word id {word})' in locus and lemma == old:
                return new
        if surface.rstrip('։.,') == 'Մաշտոց' and lemma == 'mašt':
            return 'Maštocʻ (name)'
        # All-uppercase Armenian alphabetic chapter numerals with a terminal
        # full stop; only the independently reviewed chapter heading here.
        if locus.startswith('MH_1_2_12_Movses_Khor ') and '(word id 67732)' in locus and surface == 'ԼԴ.':
            return '34@numeral'
    return lemma
