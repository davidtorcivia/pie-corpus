"""Independently reviewed wave-5 Celtic homographs and source boundaries."""
import pytest
from pie import celtic_mapping as cm
from pie import formula_search_multi as fm
from pie.material_units import repair_celtic_rows

@pytest.mark.parametrize("words,index,baseline,target", [(['tardad', 'gráin', 'na'], 1, 'grán|gráin', 'gráin@fear'),
 (['m-buí', 'h-Eriu', 'h-i'], 1, 'ériu', 'ériu (name)'),
 (['claideb', 'fata', 'sithlaí'], 1, 'práta', 'fota'),
 (['a', 'aigid', 'forro'], 1, 'aigid', 'agad@face'),
 (['ro', 'féch', 'úadha'], 1, 'fichid', 'fégaid'),
 (['torcaib', 'idna', 'catha'], 0, 'torc', 'túargabim@raise'),
 (['a', 'nocht', 'febh'], 1, 'nocht', 'innocht'),
 (['ngabail', 'rigi', 'dó'], 1, 'rigid', 'ríge'),
 (['sechnón', 'in', 'maigi', 'dochuaid'], 2, 'maígh', 'mag'),
 (['maicc', "in'athar"], 1, 'inathar', 'athair'),
 (['acht', 'gé', 'ro', 'loitis'], 1, 'gé|guidid', 'gé@although'),
 (['Fichi', 'rlg'], 0, 'fichid', 'fiche'),
 (['ceiledh', 'gái', 'fair'], 1, 'gae', 'gáu'),
 (['ba', 'bee', 'id'], 1, 'bé', 'bec'),
 (['thigi', 'file', 'isind'], 1, 'file|fil', 'fil'),
 (['isind', 'lis'], 1, 'ligh|lingid', 'les'),
 (['n-anmond', 'oss', 'aird'], 1, 'oss', 'ós'),
 (['iad', 'sen', 'robo'], 1, 'sen', 'sin'),
 (['Ge', 'bo', 'flaitli'], 0, 'guidid|gé', 'gé@although'),
 (['Gé', 'romgonais'], 0, 'gé|guidid', 'gé@although'),
 (['talmain', 'gona', 'thorthaibh'], 1, 'goin|gonaid|guin', 'cona'),
 (['faitsine', 'dhun', 'forfindam'], 1, 'dún', 'do'),
 (['ra', 'airg', 'dún', 'sobairchi'], 1, 'téit|arg', 'orcaid'),
 (['dech', 'caclia', 'gäese'], 1, '?caclia', 'cach'),
 (['trebaire', 'decli', 'áilclie'], 1, '?decli', 'dech'),
 (['imba', 'fir'], 1, 'fer', 'fír'),
 (['na', 'tessed', 'isan', 'cath'], 1, 'teichid', 'téit@secondary'),
 (['dáig', 'alta', 'in', 'mac'], 1, 'alt', 'ailid'),
 (['fo', 'dáigh', 'meic', 'dé'], 1, 'dáigh', 'dáig@because'),
 (['mar', 'bhas', 'maith'], 1, 'bás', 'bí')])
def test_context_preserves_other_homographs(words,index,baseline,target):
    form=words[index]
    z=cm.CelticLemmatizer(fm.LangMapping("sga"), cm.irish_demutate, cm.irish_skeleton,
        form_overrides={fm.key_sga(cm._ir_clean(form)):baseline}, use_skeleton=False)
    assert cm.lemmatize_words(z,words)[index]==target
    assert z(form)==baseline
    # corpus-quality batch 1 made these readings general rules (pie.celtic_mapping._cq1_irish_rule;
    # error-verdicts-cq1-celtic.jsonl): outside the old reviewed context they now give the rule's lemma.
    cq1_general = {'airc': 'airc@need', 'gráin': 'gráin@fear', 'gona': 'co',
                   'Fichi': 'fiche'}   # cq2: fichi is the numeral everywhere (error-verdicts-cq2.jsonl)
    assert cm.lemmatize_words(z, ['unrelated', form, 'unrelated'])[1] == cq1_general.get(form, baseline)


def test_welsh_until_not_birth():
    z=cm.CelticLemmatizer(fm.LangMapping("cy"), cm.welsh_demutate, cm.welsh_skeleton,
                         form_overrides={"eny":"geny"}, use_skeleton=False)
    assert cm.lemmatize_words(z,["eny","trei"])[0]=="yny"
    assert cm.lemmatize_words(z,["eny","unrelated"])[0]=="geny"
    assert not cm.content_of(z.lm,"yny","eny",z)


def test_name_marker_once_with_stage_c_loader_policy():
    z=cm.CelticLemmatizer(fm.LangMapping("sga"),cm.irish_demutate,cm.irish_skeleton,
                         form_overrides={"cáilte":"cáilte"},use_skeleton=False)
    assert cm.lemmatize_words(z,["Cáilte"])[0]=="caílte (name)"
    lemma=cm.lemmatize_words(z,["ar","Cáilte"])[1]
    assert lemma + " (name)" == "caílte (name)"


@pytest.mark.parametrize("uid", [
    "celtic-journal-revue-celtique-1870-1928:revueceltique08pari:L663-L669",
    "celtic-journal-revue-celtique-1870-1928:revueceltique13pari:L4237-L4237",
    "oldirish-tbc-windisch-1905:diealtirischehel00wind:L15483-L15484",
])
def test_apparatus_exclusion_is_source_specific(uid):
    rejected={"id":uid,"text":"apparatus"}
    retained={"id":"other:unrelated:"+uid.rsplit(":",1)[1],"text":"primary"}
    assert repair_celtic_rows([rejected,retained])==[retained]


def test_rejected_root_reports_remain_and_uncertain_stems_unmapped():
    table=cm.read_table("celt")
    assert table["cró"] == ("pie-root-krewH-pile",)
    assert cm.read_table("cy")["hydyr"] == ("pie-lex-sh1itros",)
    for lemma in ("agad@face","túargabim@raise","téit@secondary"):
        assert not table.get(lemma)
