"""Independent regression examples for the wave7 other/material decisions."""
from pathlib import Path
import json
import pytest
from pie.formula_search import Token
from pie import mapping as mp
from pie.material_units import excluded_source, byliny_non_epic, repair_celtic_rows

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('corpus,locus,form,old,new', [
    ('grc','Herodotus Historiae 3.64.5 s1','ἐπειρόμενος','ἐπιλέγω','ἐπείρομαι'),
    ('grc','Euripides Bacchae 492','δεῖ','δέω','δέω@need'),
    ('grc','Herodotus Historiae 4.199.2 s1','ἐκπέποται','ἐκπίπτω','ἐκπίνω'),
    ('grc','Herodotus Historiae 3.60.4 s1','νηὸς','ναῦς','ναός@temple'),
    ('grc','Herodotus Historiae 3.60.4 s1','νηῶν','ναῦς','ναός@temple'),
    ('hom','Il. 3.174','λιποῦσα','λιπάω','λείπω'),
    ('orv','lav 66.1','доити','доити','доити@go'),
    ('av','AVŚ, 18, 1.s77','kṣām','kṣā','kṣam@earth'),
    ('sa-ep','Rām, Bā, 72.s53','tūrya','tṛ','tūrya'),
    ('xcl','MH_1_1_04_Faustos ed. page 338 - PDF page 62 (word id 24984)','յայրումն','ayr','ayrowmn'),
    ('xcl','MH_1_1_04_Faustos ed. page 338 - PDF page 62 (word id 24990)','հունձք','hown','hownjkʻ'),
    ('xcl','MH_1_1_04_Faustos ed. page 289 - PDF page 13 (word id 4838)','սիւնհոդոսին','siwdopown','siwnhodos'),
    ('xcl','MH_1_2_12_Movses_Khor ed. page 1867 - PDF page 125 (word id 18394)','բդեշխի','bčem','bdeašx'),
    ('xcl','MH_1_1_06_Yeghishe ed. page 1002 - PDF page 482 (word id 71033)','լցուցիչն','lowcʻanem','lcʻowcʻičʻ'),
    ('xcl','MH_1_2_12_Movses_Khor ed. page 2195 - PDF page 452 (word id 82371)','յորդաբուղխ','ordaxowtʻiwn','yordabowłx'),
])
def test_context_and_surface_are_preserved(corpus,locus,form,old,new):
    t=Token(corpus,old,form,locus,{},True,'verb')
    assert (t.lemma,t.surface,t.content)==(new,form,True)
    assert Token(corpus,old,form,'unreviewed',{},True,'verb').lemma==old


@pytest.mark.parametrize('corpus,locus,form,old', [
    ('lat','LucrDRN3 3.1025',"Ancu'",'ancus'),
    ('grc','Hesiodus Fragmenta 136.3','Κοίρανον','Κοίρανος'),
    ('grc','Thucydides Historiae 2.29.3 s1','Θρᾳκῶν','Θρᾷξ'),
    ('grc','Herodotus Historiae 1.98.3 s2','Μήδων','Μῆδος'),
    ('sa-ep','MBh, 1, 100.s2','satyavatī','satyavatī'),
    ('xcl','MH_1_1_04_Faustos ed. page 368 - PDF page 92 (word id 37133)','Արեաց','ariwn'),
    ('xcl','MH_1_2_12_Movses_Khor ed. page 2056 - PDF page 314 (word id 47211)','Ձիրաւ,','jir'),
    ('xcl','MH_1_1_04_Faustos ed. page 289 - PDF page 13 (word id 4840)','Նիկիա,','nikem'),
    ('xcl','MH_1_2_12_Movses_Khor ed. page 1867 - PDF page 125 (word id 18401)','Դարեհի','darem'),
    ('xcl','MH_1_2_12_Movses_Khor ed. page 1867 - PDF page 125 (word id 18391)','Միհրդատայ','mirdahar'),
    ('xcl','MH_1_2_12_Movses_Khor ed. page 1867 - PDF page 125 (word id 18400)','Միհրդատայ,','mirdahar'),
])
def test_names_stay_in_context_but_not_content(corpus,locus,form,old):
    t=Token(corpus,old,form,locus,{},True,'noun')
    assert t.lemma.endswith(' (name)') and not t.content
    assert t.surface==form
    # cq1 (corpus-quality batch 1) turned the Armenian Areacʻ 'Aryans' reading into a general rule
    # (pie.cq1_xcl name-aryans); other unreviewed forms keep their content status.
    from pie.cq1_xcl import rule_for
    assert Token(corpus,old,form,'unreviewed',{},True,'noun').content or rule_for(corpus,old,form,'unreviewed')


def test_mapping_homographs_and_uncertain_etymologies():
    for c,l,expected in [
        ('grp','πλέω',{'pie-root-plew-fly'}),
        ('hom','λείπω',{'pie-root-leykw-leave'}),
        ('orv','слава',{'pie-root-kjlew-hear'}),
        ('orv','доити@go',{'pie-root-h1ey-go'}),
        ('av','kṣam@earth',{'pie-lex-dhegjhoxm'}),
        ('xcl','lcʻowcʻičʻ',{'pie-root-pleh1-fill'}),
        ('grp','ναός@temple',set()),('grp','δέω@need',set()),
        ('av','tūrya',set()),('xcl','hownjkʻ',set()),
    ]:
        assert set(mp.decide(c,l,{'bad-auto-id'})[0])==expected
    # A sense-specific fix must not globally remove the genuine ship/milk/man readings.
    for c,l in [('grp','ναῦς'),('orv','доити'),('xcl','ayr')]:
        assert not any(r['lemma']==l and r['corpus']==c for r in json.loads(
            (ROOT/'data/research/formulas/mapping-overrides/w7-other.json').read_text())['lemma'])


def test_reviewed_material_boundaries_and_detector_miss():
    rules=json.loads((ROOT/'data/research/8c/stageCS/material-unit-rules-w7-other.json').read_text())
    for r in rules:
        fn=Path(r['source']).name
        assert excluded_source(r['corpus'],fn,r['start'],r['end'])
        assert not excluded_source(r['corpus'],fn,r['start']-1,r['end'])
    r=rules[-1]
    lines=(ROOT/r['source']).read_text().splitlines()
    assert r['start']-1 not in byliny_non_epic(lines)
    assert lines[r['start']-1].startswith('ПЕРЕЧЕНЬ')
    source=ROOT/'raw/daughters/celtic-stageC/units.jsonl'
    ids={'oldirish-meyer-editions-1892-1919:berdielteste00meyeuoft:L6500-L6500',
         'celtic-journal-eriu-1904-1928:eriu_1912_6:L7994-L7995',
         'celtic-journal-revue-celtique-1870-1928:revueceltique13pari:L22538-L22539'}
    selected=[r for line in source.open() if (r:=json.loads(line))['id'] in ids]
    assert len(selected)==3
    assert repair_celtic_rows(selected)==[]
