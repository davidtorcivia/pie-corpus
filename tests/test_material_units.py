from pie.material_units import (excluded_source, grein_apparatus,
                                join_restorations, repair_celtic_rows)
from pie.formula_search_multi import EDDA, edda_lines


def test_internal_restoration_is_one_word_but_notes_are_not_joined():
    from pie.celtic_mapping import irish_words
    assert irish_words(join_restorations("Adcon[n]airc-sium derscai[g]theach")) == [
        "Adconnairc-sium", "derscaigtheach"]
    assert join_restorations("word [note] word a[123]b") == "word [note] word a[123]b"


def test_reviewed_celtic_boundaries_and_manuscript_title():
    def row(uid, text):
        return {"id": uid, "text": text, "source": "ocr", "dup_of": None}
    rows = [row("x:eriu_1910_4:L9175-L9177", "variants"),
            row("x:eriu_1914_7:L273-L279", "narrative: apparatus sicH"),
            row("x:revueceltique16pari:L8224-L8230", "in the Bodleian manuscript: quotation"),
            row("x:zeitschriftfrc03meyeuoft:L185-L185", "manuscript title")]
    fixed = repair_celtic_rows(rows)
    assert [d["text"] for d in fixed] == ["narrative:", "quotation", "manuscript title"]
    assert rows[1]["text"] == "narrative: apparatus sicH"
    assert repair_celtic_rows(fixed) == fixed


def test_welsh_split_join_keeps_metadata_and_updates_duplicate_reference():
    prefix = "welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:"
    a, b = prefix + "L21478-L21478", prefix + "L21480-L21480"
    rows = [{"id": a, "text": "prefix hir", "licence": "pd"},
            {"id": b, "text": "awd ac eli"},
            {"id": "copy", "text": "copy", "dup_of": b}]
    fixed = repair_celtic_rows(rows)
    assert fixed[0]["text"] == "prefix hirawd ac eli"
    assert fixed[0]["licence"] == "pd"
    assert fixed[1]["dup_of"] == fixed[0]["id"]
    assert repair_celtic_rows(fixed) == fixed


def test_byliny_review_ranges_do_not_remove_adjacent_verse():
    assert excluded_source("byliny", "11016812bsb_djvu.txt", 6393)
    assert not excluded_source("byliny", "11016812bsb_djvu.txt", 6397)
    assert not excluded_source("byliny", "other_djvu.txt", 6393)


def test_grein_apparatus_not_quoted_verse():
    assert grein_apparatus("439) word MS. O. word K. — 445) word Th.")
    assert not grein_apparatus("439 word word word")
    assert not grein_apparatus("439) word word word")


def test_edda_prose_does_not_inherit_previous_poem_and_commentary_stops(tmp_path):
    lines = [""] * 19656
    lines[0] = "VÖLUSPÁ."
    lines[1] = "1. verse words here"
    lines[5338] = "Lokasenna."
    lines[5355] = "prose words here"
    lines[5371] = "1. new verse words"
    lines[12422] = "Reginsmál A-B."
    lines[12461] = "A. 1. more verse words"
    lines[15413] = "Goðrúnarkviða en forna."
    lines[15453] = "1. final verse words"
    lines[16000] = "VÖLSUNGAKVIÐA EN FORNA."
    lines[16001] = "1. different poem words"
    lines[19651] = "Nokkrar  skýríngar."
    lines[19655] = "editorial words here"
    p = tmp_path / EDDA
    p.parent.mkdir(parents=True)
    p.write_text("\n".join(lines), encoding="utf-8")
    units = edda_lines(tmp_path)
    assert [u[0] for u in units] == ["Völuspá 1", "Lokasenna 1", "Reginsmál 1",
                                    "Guðrúnarkviða en forna 1", "Völsungakviða En Forna 1"]


def test_reviewed_entity_and_parenthetical_expansions_are_locus_scoped():
    rows = [
        {'id': 'G302025:#1/105:5', 'text': 'h-othar eacute;ga', 'source': 'celt-ucc/G302025'},
        {'id': 'x:revueceltique10pari:L5026-L5028',
         'text': 'atfia(datar) co der(ed)', 'source': 'ocr'},
        {'id': 'other', 'text': 'eacute;ga der(ed) (note)', 'source': 'ocr'},
    ]
    fixed = repair_celtic_rows(rows)
    assert [r['text'] for r in fixed] == ['h-othar éga', 'atfiadatar co dered', 'eacute;ga der(ed) (note)']
    assert repair_celtic_rows(fixed) == fixed
    assert rows[0]['text'] == 'h-othar eacute;ga'
