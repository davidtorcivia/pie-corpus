"""Source regressions and controls for wave 6 other/material corrections."""
from pathlib import Path
import importlib.util
import sys

import pytest
from pie import bsl_mapping as bm, formula_search as fs, mapping as mp
from pie.material_units import dainos_interleaved, excluded_token_unit, reviewed_byliny_text
from pie.w6_other_mapping import VUK


def test_ocr_dollar_is_internal_or_final_yat_not_a_word_boundary():
    assert bm.corpus_words('byliny','св$тъ мор$ д$в$ца') == ['св$тъ','мор$','д$в$ца']
    assert [bm.ru_norm_ocr(w) for w in bm.corpus_words('byliny','св$тъ мор$')] == ['свѣтъ','морѣ']
    assert bm.corpus_words('byliny',"царь' $ лось word$word 12") == ["царь'",'лось','word','word']
    assert bm.corpus_words('vuk','св$тъ') == ['св','тъ']


def test_split_reflexive_does_not_create_elk():
    loc='sbornikotdelenijarusskogojazykaislovesno92:7991'
    text=reviewed_byliny_text(loc,'Розгор лось')
    words=bm.corpus_words('byliny',text)
    assert words == ['Розгор$лось']
    assert fs.Token('byliny','?',words[0],loc,{},True,'noun').lemma == 'разгореться'
    assert reviewed_byliny_text('elsewhere','Розгор лось') == 'Розгор лось'


def test_two_columns_require_repeated_internal_stanza_markers():
    rows=['1 Mano sesė 4 Tavo brolis','Auga rūta, Žydi liepa','2 Mano brolis 5 Tavo sesė','Auga liepa, Žydi rūta']
    assert dainos_interleaved(rows) == set(range(4))
    assert not dainos_interleaved(['1 Mano sesė','Auga rūta','2 Tavo brolis'])
    assert not dainos_interleaved(['Mano sesė 4 Tavo brolis','Auga rūta'])
    assert not dainos_interleaved([rows[0],'123. Nauja daina',rows[2]])


@pytest.mark.parametrize('name,common',[('Λύκος','λύκος'),('Φᾶσις','φάσις'),('Πόντος','πόντος'),('Ἀντίλοχος','λόχος')])
def test_dictionary_name_pos_keeps_common_homonyms(name,common):
    t=fs.Token('grc',name,name,'fixture',{},True,'noun')
    # Theonym narrowing (docs/research/8c-theonym-narrowing.md): source-tagged
    # Πόντος is mostly the region/Black Sea, so it is a name like the others.
    # The lowercase inherited sea noun πόντος is unaffected (checked below).
    assert t.lemma == name+' (name)' and not t.content and t.pos=='name'
    t=fs.Token('grc',common,common.title(),'fixture',{},True,'noun')
    assert t.lemma==common and t.content
    # cq2 (corpus-quality batch 2): a capitalised Greek lemma outside the dictionary names is now a name
    # too (pie.cq2_other.greek_capitalised); before, it stayed content
    assert fs.Token('grc','Ἄγνωστον','Ἄγνωστον','fixture',{},True,'noun').lemma == 'Ἄγνωστον (name)'


@pytest.mark.parametrize('key,new',VUK.items())
def test_reviewed_vuk_homonyms_keep_unreviewed_occurrences(key,new):
    loc,form=key
    assert fs.Token('vuk','old',form,loc,{},True,'noun').lemma==new
    assert fs.Token('vuk','old',form,'unreviewed',{},True,'noun').lemma=='old'


def test_context_only_and_restored_sea_content():
    assert not fs.Token('vuk','nit','нити','Vuk 1598:45',{},True,'noun').content
    t=fs.Token('vuk','mora|more','мора','Vuk 23722:93',{},False,'other')
    assert t.content and t.lemma=='more@sea'


def test_reviewed_mapping_senses():
    assert mp.resolve_table('grp')['εἴρω@speak'].ids=={'pie-lex-weryeti'}
    assert 'ἰσχυρός' not in mp.resolve_table('grp')
    assert mp.resolve_table('av')['vṛ@cover'].ids=={'pie-root-h2wer-lift'}
    assert mp.resolve_table('av')['vṛ'].ids=={'pie-lex-wlnh1toy','pie-root-welh1-choose'}
    assert mp.resolve_table('vuk')['padati'].ids=={'pie-root-ped-walk'}
    assert 'tih' not in mp.resolve_table('vuk')
    assert mp.resolve_table('orv')['поити@go'].ids=={'pie-root-h1ey-go'}


def test_homer_citation_repair_preserves_words():
    ts=fs.load_homer()
    assert not any(t.locus=='Od. 8' for t in ts)
    words=[t.surface for t in ts if t.locus=='Od. 8.586']
    assert words==['γίγνεται','ὅς','κεν','ἑταῖρος','ἐὼν','πεπνυμένα','εἰδῇ']


def test_editorial_title_is_excluded_at_unit_boundary():
    assert excluded_token_unit('icepahc','1260.jomsvikingar.nar-sag s1506')
    assert not excluded_token_unit('icepahc','1260.jomsvikingar.nar-sag s1505')
    assert not excluded_token_unit('icepahc','1260.jomsvikingar.nar-sag s1507')


def test_latin_inherited_name_and_common_word_keep_content(tmp_path):
    p=tmp_path/fs.LATIN/'fixture_test.conllup'
    p.parent.mkdir(parents=True)
    p.write_text('# sent_id = fixture\n1\tLiber\tliber\tPROPN\t_\tCase=Nom\t0\troot\t_\tCitationHierarchy=1\n'
                 '2\tliber\tliber\tADJ\t_\tCase=Nom\t1\tdep\t_\tCitationHierarchy=1\n')
    name,common=fs.load_latin(tmp_path)
    assert name.lemma=='liber' and name.content  # Liber personifies the inherited adjective
    assert common.lemma=='liber' and common.content
