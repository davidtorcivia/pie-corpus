"""Wave 6 source/dictionary decisions; see error-verdicts-w6-other.jsonl."""
from functools import lru_cache
import json
from pathlib import Path
import unicodedata


@lru_cache(maxsize=1)
def greek_dictionary_names():
    """Exact NFC dictionary name heads, never surface capitalization guesses."""
    p = Path(__file__).resolve().parents[1] / 'raw/daughters/kaikki-ancientgreek/kaikki.org-dictionary-AncientGreek.jsonl'
    if not p.exists():
        return frozenset()
    names, common = set(), set()
    with p.open(encoding='utf-8') as f:
        for line in f:
            if any(f'"pos": "{pos}"' in line for pos in ('name','noun','adj')):
                d = json.loads(line)
                head = unicodedata.normalize('NFC', d['word'])
                if d.get('pos') == 'name':
                    names.add(head)
                elif d.get('pos') in {'noun','adj'}:
                    common.add(head)
    return frozenset(names - common)


def annotated_name(corpus, lemma, pos):
    if pos == 'name' and corpus in {'orv','av','sa-ep','grc','grp','grc-late','hom','lat'}:
        return True
    # Treebanks distinguish name heads by case even when their POS is n.
    # Require independent dictionary POS; lowercase common homonyms survive.
    return (corpus in {'grc','grp','grc-late','hom'} and pos == 'noun'
            and lemma[:1].isupper() and lemma in greek_dictionary_names())


VUK = {
    ('Vuk 34511:17','секу'): 'seka',
    ('Vuk 35651:3','Селе'): 'sestra',
    ('Vuk 1598:45','нити'): 'niti@conjunction',
    ('Vuk 35114:29','Оди'): 'hoditi',
    ('Vuk 28210:5','прео'): 'preko@preposition',
    ('Vuk 23690:27','вили'): 'vila@fairy',
    ('Vuk 36524:12',"ор'е"): 'orah',
    ('Vuk 38644:1','седа'): 'sedati',
    ('Vuk 40097:65','пали'): 'paliti',
    ('Vuk 10134:200','Иву'): 'Ivo (name)',
    ('Vuk 22066:215','обали'): 'obaliti',
    ('Vuk 18822:41','Стојан'): 'Stojan (name)',
    ('Vuk 1658:283','бране'): 'braniti',
    ('Vuk 15623:1','желе'): 'žeti',
    ('Vuk 21696:563','Куче'): 'Kuči (name)',
    ('Vuk 23734:92','Вати'): 'hvatiti',
    ('Vuk 48070:3',"Јел'"): 'je-li@interrogative',
    ('Vuk 1573:727','хрче'): 'hrt',
    ('Vuk 12614:1','Осу'): 'osuti',
    ('Vuk 21701:435','сива'): 'sijevati',
    ('Vuk 21701:544','врата'): 'vrat',
    ('Vuk 23722:93','мора'): 'more@sea',
}


def reviewed_lemma(corpus, lemma, surface, locus):
    if corpus == 'vuk':
        return VUK.get((locus,surface), lemma)
    if corpus in {'grc','grp','grc-late','hom'}:
        if lemma == 'ὁράω' and surface == 'ἰδὼν':
            return 'εἶδον@see'
        if lemma == 'λέγω' and surface == 'ἐρέων':
            return 'εἴρω@speak'
    if corpus in {'av','sa-ep'}:
        if (locus,surface) in {('AVŚ, 18, 2.s106','ūrṇomi'),('MBh, 5, 22.s49','vṛtaṃ')}:
            return 'vṛ@cover'
        if (locus,surface) in {('MBh, 3, 256.s10','bhīmo'),('MBh, 5, 48.s33','jambhasya'),('MBh, 5, 47.s146','kṛṣṇena')}:
            return lemma + ' (name)'
    if corpus == 'lat':
        if locus == 'CatAgr 40.2' and lemma == 'liber': return 'liber@bark'
        if (locus,surface) == ('CatAgr 133.1','pulli'): return 'pullus@young'
        if (locus,surface) == ('CatAgr 162.1','moliti'): return 'molo'
    if corpus == 'byliny':
        if surface.lower() == 'очушкахъ': return 'око'
        if (locus,surface) == ('sbornikotdelenijarusskogojazykaislovesno32:22138','мор$'): return 'море'
        if (locus,surface) == ('sbornikotdelenijarusskogojazykaislovesno32:22138','овчиникъ'): return 'овчинник'
        if (locus,surface) == ('sbornikotdelenijarusskogojazykaislovesno92:24157','кленбва'): return 'кленовый'
    if corpus == 'dainos':
        if (locus,surface) == ('litauischevolksl00leskuoft:16851','yra'): return 'būti@present'
        if (locus,surface) == ('litauischevolksl00leskuoft:20040','praszyt'): return 'prašyti'
        if (locus,surface) == ('Lietuvi-kos-svotbin-s-dainos-1883:48920','kašes'): return 'kašė'
        if (locus,surface) == ('Lietuvi-kos-svotbin-s-dainos-1883:40495','Lankyte'): return 'lankyti'
    if corpus == 'lv':
        return {('BV 28321','bāliņš'):'brālis',('BV 28321','maliņā'):'mala',
                ('BV 28354','matiņus'):'mats',('BV 375','sētiņā'):'sēta'}.get((locus,surface),lemma)
    if corpus == 'xcl' and surface == 'Յունաց' and locus.startswith('MH_1_2_12_Movses_Khor ') and '(word id 81226)' in locus:
        return 'yoyn (name)'
    return lemma
