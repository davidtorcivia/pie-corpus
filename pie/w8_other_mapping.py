"""Wave 8 source-coordinate corrections; evidence in error-verdicts-w8-other.jsonl."""
READINGS = {
    ('grc', 'Herodotus Historiae 4.58.1 s1', 'ποιέων'): 'πόα',
    ('grc', 'Herodotus Historiae 4.35.3 s1', 'Ὠλὴν'): 'Ὠλήν (name)',
    ('grc', 'Herodotus Historiae 1.204.1 s1', 'Καύκασος'): 'Καύκασος (name)',
    ('xcl', 'MH_1_2_12_Movses_Khor ed. page 2193 - PDF page 450 (word id 81372)', 'Գայիանէ'): 'Gayianē (name)',
    ('xcl', 'MH_1_2_12_Movses_Khor ed. page 2195 - PDF page 452 (word id 82268)', 'գան'): 'gam@present',
    ('byliny', 'pesnisobrannyepvkireevskimch2pesni36:6739', 'пбрву'): 'первый',
    ('byliny', '10945725bsb:17578', 'Подымитесь'): 'подыматься',
    ('byliny', 'pesnisobrannyepvkireevskimch2pes74:235', 'сыру'): 'сырой',
    ('byliny', 'pesnisobrannyepvkireevskimch2vyp57:4441', 'Фзди'): 'ездить',
    ('vuk', 'Vuk 28249:332', 'Вук'): 'Vuk (name)',
    ('vuk', 'Vuk 23672:237', 'Вука'): 'Vuk (name)',
}


def reviewed_lemma(corpus, lemma, surface, locus):
    return READINGS.get((corpus, locus, surface), lemma)
