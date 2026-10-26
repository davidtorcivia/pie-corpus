"""Synthetic examples: no source quotation or coordinate-specific detector rules."""
from pie.material_units import byliny_non_epic, byliny_wiki_lines
from pie.bsl_mapping import byliny_units, KD


def test_wrapped_prose_requires_context_and_stops_at_blank():
    prose = [
        'Этот длинный рассказ исследователь обсуждает в своей новой ра-',
        'боте о деревне, где он жил. Другие сведения еще не были запи-',
        'саны в тот год. Позднее автор привел здесь подробное объяснение.',
        'Так было дело.',
    ]
    lines = ['А и едет добрый молодец', '', *prose, '', 'А и едет добрый молодец']
    excluded = byliny_non_epic(lines)
    assert 5 in excluded
    assert 0 not in excluded and 7 not in excluded
    assert not byliny_non_epic(['Так было дело.'])


def test_primary_prose_and_verse_before_recording_note_are_retained():
    lines = ['Поехали тут сильные богатыри по широкой дорожке да по чи-',
             'стому полю. Долго ехали они, а потом вышли к большому мо-',
             'рю и решили отдохнуть. Стали они ставить свои белые шатры.',
             'Говорит тут старший богатырь.']
    assert not byliny_non_epic(lines)
    assert 0 not in byliny_non_epic([
        'Ты царю верно служишь!',
        '(Записано собирателем в деревне в 1834 году от старого солда-',
        'та.)'])


def test_orthography_dialogue_dates_and_inline_calls_do_not_suffice():
    lines = ['А и едет добрый молодец', 'А и едетъ добрый молодецъ',
             '«Ты куда идешь, добрый молодец?»', 'Ехал он во чисто поле [1]',
             'Он прожил сто лет на свете', '1. Едет он во чисто поле',
             'Он родился в 1791 году', 'Он сказал: «Записано на камне!»']
    assert not byliny_non_epic(lines)


def test_editorial_context_is_bounded_and_numbering_is_stable(tmp_path):
    folder = tmp_path / KD / 'russian-byliny-wikisource'
    folder.mkdir(parents=True)
    (folder/'texts-plaintext.txt').write_text(
        '### Song [pageid 9]\nА и едет добрый молодец\nПримечания\n'
        'Здесь объясняется запись\n### Other [pageid 10]\nОн приехал во чисто поле\n')
    # Loader requires both explicitly configured Hilferding files.
    from pie.bsl_mapping import BYLINY_OCR
    for edition, files in BYLINY_OCR.items():
        for filename in files or []:
            p = tmp_path/KD/edition/filename
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('А и едет добрый молодец\n\nЗаписано в деревне\n')
    units = list(byliny_units(tmp_path))
    assert [u[0] for u in units[:2]] == ['ruws 9:1', 'ruws 10:1']
    assert len(units) == 4
    assert all('Записано' not in u[2] for u in units)


def test_notes_generalize_to_unseen_page_and_old_spelling():
    rows = [('new','title',1,'Скакал удалый молодец'),
            ('new','title',2,'Примѣчанія.'),
            ('new','title',3,'editorial'),
            ('other','title',1,'Скакал удалый молодец')]
    assert list(byliny_wiki_lines(rows)) == [rows[0], rows[3]]


def test_markers_and_signed_footnotes():
    assert byliny_non_epic(['Записано от сказителя в деревне']) == {0:'editorial-marker'}
    assert byliny_non_epic(['1) Другое чтение. — Р.']) == {0:'signed-footnote'}
    assert not byliny_non_epic(['Он услышал песню молодецкую'])
