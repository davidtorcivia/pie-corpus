"""Reviewed source-boundary repairs, before mapping or context construction.

Coordinates in material-unit-rules.json are one-based inclusive source OCR
lines, not generated table rows. See error-verdicts-material.jsonl for review.
The frozen Celtic layer remains an input; no raw Python is imported.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "data/research/8c/stageCS/material-unit-rules.json"


@lru_cache(maxsize=1)
def reviewed_ranges():
    rows = json.loads(RULES.read_text(encoding="utf-8"))
    for name in ('material-unit-rules-w6-other.json', 'material-unit-rules-w7-other.json', 'material-unit-rules-w8-other.json', 'material-unit-rules-w9-other.json'):
        extra = RULES.with_name(name)
        if extra.exists():
            rows += json.loads(extra.read_text(encoding='utf-8'))
    # Corpus-quality batch 1: data/research/8c/corpus-quality/material-unit-rules-cq1-<area>.json
    for extra in sorted((RULES.parents[1] / 'corpus-quality').glob('material-unit-rules-cq1-*.json')):
        rows += json.loads(extra.read_text(encoding='utf-8'))
    return rows


def dainos_interleaved(lines: list[str]) -> set[int]:
    """Conservative two-column OCR exclusion, without guessing column order.

    Require repeated embedded stanza numbers followed by a capital initial,
    with at least two words on each side. Only the span between nearby anchors
    is excluded (plus three continuation lines); no whole-edition rejection.
    """
    anchors = []
    for i, line in enumerate(lines):
        for m in re.finditer(r'(?<!\w)([1-9]\d?)\s+([A-ZĄČĘĖĮŠŲŪŽ])', line):
            if len(re.findall(r'[^\W\d_]+',line[:m.start()])) >= 2 and len(re.findall(r'[^\W\d_]+',line[m.end()-1:])) >= 2:
                anchors.append(i)
                break
    out = set()
    for a,b in zip(anchors,anchors[1:]):
        if b-a <= 12:
            # A new song title/page header is a hard boundary.
            if any(re.match(r'^\s*\d{3,}\.', s) for s in lines[a+1:b]):
                continue
            out.update(range(a,min(b+4,len(lines))))
    return out


def reviewed_vuk_material(page: str, line: int) -> bool:
    return (page,line) in {('13232',153),('48084',50)}


def excluded_token_unit(corpus: str, locus: str) -> bool:
    # IcePaHC source sentence is chapter number + chapter label + title.
    return (corpus,locus) == ('icepahc','1260.jomsvikingar.nar-sag s1506')


def reviewed_byliny_text(locus: str, text: str) -> str:
    # Hilferding vol. 3 L7991: a space swallowed the medial vowel. Keep
    # the damaged form joined, then use the normal reviewed verb analysis.
    if locus == 'sbornikotdelenijarusskogojazykaislovesno92:7991':
        return text.replace('Розгор лось','Розгор$лось')
    # Corpus-quality batch 1 (w10/10): Hilferding vol. 1 L25499 line-initial
    # Кло is the interrogative Кто (т read as л; the tsar asks who could
    # raise the dead).
    if locus == 'sbornikotdelenijarusskogojazykaislovesno32:25499':
        return text.replace('«Кло ', '«Кто ', 1)
    return text


def excluded_source(corpus: str, filename: str, start: int, end: int | None = None) -> bool:
    """Exclude units wholly inside a reviewed non-primary source span."""
    end = start if end is None else end
    return any(r["corpus"] == corpus and Path(r["source"]).name == filename
               and r["start"] <= start <= end <= r["end"] for r in reviewed_ranges())


def join_restorations(text: str) -> str:
    """Internal alphabetic restorations belong to the enclosing word.

    Leave standalone brackets and editorial annotations intact.
    """
    return re.sub(r"(?<=[^\W\d_])\[([^\W\d_]+)\](?=[^\W\d_])", r"\1", text)


def reviewed_daina_quote(page: str, offset: int) -> bool:
    """Whether an extracted quotation is primary verse (wave 3 report 18)."""
    # Endzelīns p0341:1046 is a linguistic footnote, opened by a less-than
    # etymological sign and closed by a gloss quotation mark.
    return (page, offset) != ("p0341", 1046)


def repair_menota_words(words):
    """Remove reviewed editorial brackets; repair three source word boundaries.

    Preserve unreviewed readings and token coordinates. This deliberately does
    not collapse manuscript variants or infer repairs from spelling alone.
    Evidence: error-verdicts-w3-other.jsonl, reports 11,38,43–46,48,54,110.
    """
    from dataclasses import replace

    out = []
    i = 0
    while i < len(words):
        w = words[i]
        if w.doc == "AM-36-fol" and w.folio in {"8", "17", "28", "75", "117", "138"} and w.form.startswith("["):
            depth, j = 0, i
            while j < min(i + 40, len(words)):
                if words[j].folio != w.folio:
                    break
                depth += words[j].form.count("[") - words[j].form.count("]")
                j += 1
                if depth <= 0:
                    break
            phrase = " ".join(x.form for x in words[i:j])
            if depth == 0 and re.search(r"underpr|manglar|siste d|tegnet|usikkert|mellomrom", phrase):
                i = j
                continue
        if (w.doc, w.folio, w.form) == ("AM-36-fol", "15", "brygiorsverþ"):
            out.extend((replace(w, form="brygior"), replace(w, form="sverþ")))
            i += 1
            continue
        if i + 1 < len(words):
            nxt = words[i + 1]
            key = (w.doc, w.folio, w.form, nxt.form)
            joined = {
                ("AM-35-fol", "201", "ey", "dana"): "eydana",
                ("AM-63-fol", "62", "breno", "steini"): "brenosteini",
            }.get(key)
            if joined and (w.doc, w.folio, w.stanza, w.sent) == (nxt.doc, nxt.folio, nxt.stanza, nxt.sent):
                out.append(replace(w, form=joined))
                i += 2
                continue
        out.append(w)
        i += 1
    return out


_RU_WORD = re.compile(r"[а-яёѣіѳѵ]+", re.I)
_RU_NOTES = re.compile(r"^(?:примечани[ея]|комментари[ийя]|сноски|источники)\s*[.:]?$", re.I)
_RU_EDITOR = re.compile(
    r"записан[оаы]|запись\s+от|по\s+записи|собирател|сказител|"
    r"по\s+складу\s+стиха|вариант[а-я]*\s+(?:песни|былины)|"
    r"нужно\s+разум|по\s+описанию|\bдер\.|\bгуб\.|\bуезд|"
    r"\bредактор|\bиздател|\bрукопис|\bпримечани", re.I)
_RU_NOTE_START = re.compile(r"^\s*(?:\d{1,3}|[*¹²³⁴⁵⁶⁷⁸⁹]|[.)])\s*[).]\s*")
_RU_SIGNED_NOTE = re.compile(r"[—–]\s*(?:[А-Яа-яѢѣA-Z0-9]\.?){1,3}\s*[.]?\s*$")
_RU_SCHOLAR = re.compile(
    r"\b(?:рукопис|издани|издан|сборник|литератур|редакт|исслед|"
    r"вариант|предислов|примечан|собирател|сказител|правопис|"
    r"этимолог|сравнен|печат|напечат|пересказ|происхожден)|"
    r"\b(?:см|ср|стр)\.", re.I)


def _byliny_normal(text: str) -> str:
    # This is feature extraction only: the yielded source text is never changed.
    return text.lower().replace("ѣ", "е").replace("і", "и").replace("ъ", "")


def byliny_non_epic(lines: list[str]) -> dict[int, str]:
    """Conservative, edition-independent exclusions, keyed by zero-based line.

    Use OCR paragraphs and bounded windows, not reviewed coordinates. Long
    lines, punctuation, spelling or footnote calls alone cannot reject verse.
    Vowel counts are a rough rhythm proxy, not a claim to scan Russian stress.
    Blank lines bound contextual evidence; windows prevent a note contaminating
    an entire song. Explicit notes headings are handled separately on wiki pages.
    """
    out = byliny_page_material(lines)
    start = 0
    while start < len(lines):
        if not lines[start].strip():
            start += 1
            continue
        end = start + 1
        while end < len(lines) and lines[end].strip():
            end += 1
        quoted = False
        for i in range(start, end):
            line = lines[i]
            normal = _byliny_normal(line)
            if _RU_NOTES.fullmatch(normal.strip()):
                out[i] = "notes-heading"
                continue
            # Prose discussions often embed actual epic quotations. Do not
            # discard these doubtful units merely because their wrapper is prose.
            in_quote = quoted or "«" in line or "»" in line
            for char in line:
                if char == "«":
                    quoted = True
                elif char == "»":
                    quoted = False
            if in_quote:
                continue
            # At most nine physical lines, within the same OCR paragraph.
            nearby = lines[max(start, i - 4):min(end, i + 5)]
            norm = [_byliny_normal(s) for s in nearby]
            editorial = any(_RU_EDITOR.search(s) and not re.search('[«»]', s) for s in norm)
            scholarly = any(_RU_SCHOLAR.search(s) for s in norm)
            long = sum(len(_RU_WORD.findall(s)) >= 9 or len(s.strip()) >= 65 for s in norm)
            broken = sum(bool(re.search(r"[а-яё]-\s*$", s)) for s in norm)
            sentences = sum(bool(re.search(r"[а-яё][.;]\s+[а-яё]", s)) for s in norm)
            vowels = [len(re.findall(r"[аеёиоуыэюя]", s)) for s in norm]
            # Require several full-width lines AND independent prose evidence.
            if (scholarly and len(nearby) >= 3 and long >= 3 and
                    (broken >= 2 or (broken >= 1 and sentences >= 1)) and
                    sum(v > 18 for v in vowels) >= 2):
                out[i] = "wrapped-prose"
            elif _RU_EDITOR.search(normal):
                out[i] = "editorial-marker"
            elif (editorial and
                  (any(_RU_EDITOR.search(_byliny_normal(s)) and not re.search('[«»]', s)
                       for s in lines[max(start, i - 4):i + 1]) or
                   (len(line.strip()) >= 60 and long >= 2)) and
                  (broken or sentences or any(re.search(r"\b\d{2,4}\b", s) for s in norm))):
                out[i] = "editorial-paragraph"
            elif _RU_NOTE_START.search(line) and _RU_SIGNED_NOTE.search(line):
                out[i] = "signed-footnote"
            elif _RU_SIGNED_NOTE.search(line) and editorial:
                out[i] = "signed-footnote"
        start = end
    return out


def byliny_wiki_lines(rows):
    """Stop at notes on any page; retain original page/unit numbers and text."""
    page = None
    notes = False
    for pid, title, i, line in rows:
        if pid != page:
            page, notes = pid, False
        if _RU_NOTES.fullmatch(_byliny_normal(line).strip()):
            notes = True
        if not notes and not byliny_non_epic([line]):
            yield pid, title, i, line


_CELTIC_W6_NON_NAMES = {
    "welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L17016-L17028": "Dỳwawt",
    "G301041:#1:208": "Dogebhthar",
    "G301000:#1:5": "As-noí",
}


def repair_celtic_rows(rows: list[dict]) -> list[dict]:
    out = []
    welsh = "welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:"
    first, second = welsh + "L21478-L21478", welsh + "L21480-L21480"
    merged_id = welsh + "L21478-L21480"
    for original in rows:
        d = dict(original)
        uid, text = d["id"], d["text"]
        # W9-018: secure OCR confusions in the Alexander narrative;
        # Irische Texte II L14602-L14604; Kaikki sga ben (76), cen (773).
        # Leave the uncertain parent-form spellings for image-based review.
        if uid == "oldirish-irische-texte-1880-1909:irischetextemitw02winduoft:L14602-L14604":
            text = (text.replace("hen cen cheli", "ben cen cheli")
                    .replace("siur cell brathair", "siur cen brathair")
                    .replace("AlaxawiüiV", "Alaxandir"))
        # W8 Celtic: quotation-initial preterite, not a personal name.
        # CELT G301012.xml:4293; Kaikki Old Irish doicc (2825).
        if uid == "G301012:#1/#2/#52:26":
            text = text.replace("Táinic buiden", "táinic buiden")
        # W6 Celtic review: sentence/quotation-initial verbs inside flattened
        # units are not names. Normalize only these reviewed capitals before
        # the loader's medial-capital heuristic; raw text remains unchanged.
        # Source/dictionary citations: error-verdicts-w6-celtic.jsonl 100-102.
        if uid in _CELTIC_W6_NON_NAMES:
            word = _CELTIC_W6_NON_NAMES[uid]
            text = re.sub(r"(?<!\w)" + re.escape(word) + r"(?!\w)", word.lower(), text)
        # Wave-5 Celtic review: manuscript-variant footnote, not continuous
        # daughter text (error-verdicts-w5-celtic.jsonl, report 88).
        if uid == "oldirish-tbc-windisch-1905:diealtirischehel00wind:L15483-L15484":
            continue
        m = re.search(r":([^:]+):L(\d+)-L(\d+)", uid)
        if m and excluded_source("celtic", m[1] + "_djvu.txt", int(m[2]), int(m[3])):
            continue
        if "eriu_1914_7:L273-L279" in uid:
            # Source lines 273-274 are narrative, 277-279 are apparatus.
            text = text.split(":", 1)[0] + ":"
        if "revueceltique16pari:L8224-L8230" in uid:
            text = re.sub(r"^in the Bodleian manuscript:\s*", "", text)
        if uid == "G302025:#1/105:5":
            # CELT XML line 7093 itself lacks the entity's opening ampersand.
            text = text.replace("eacute;ga", "éga")
        if uid.endswith(":revueceltique10pari:L5026-L5028"):
            # The edition expands these abbreviations in parentheses. Keep
            # the letters together, without treating other parentheses as words.
            text = text.replace("atfia(datar)", "atfiadatar").replace("der(ed)", "dered")
        # W2 Celtic source repairs; exact source spans, not global OCR guesses.
        # Evidence: error-verdicts-w2-celtic.jsonl, reports 43, 47, 51.
        if uid.endswith(":revueceltique13pari:L1311-L1312"):
            continue  # numbered French comparative footnote, not primary narrative
        if uid.endswith(":zeitschriftfrc09meyeuoft:L7859-L7863"):
            text = re.sub(r"\bbrag(?:/|\s+)ait\b", "brágait", text)
        if uid.endswith(":zeitschriftfurcelti14:L22144-L22145"):
            text = text.replace("fichi(t)", "fichit")
        if d.get("source", "").startswith("celt-ucc/"):
            text = join_restorations(text)
        d["text"] = text
        if uid == second and out and out[-1]["id"] == first:
            previous = out[-1]
            if previous["text"].endswith("hir") and text.startswith("awd "):
                out[-1] = {**previous, "id": merged_id, "text": previous["text"] + text}
                continue
        out.append(d)
    # Keep dedupe references valid if either source unit was a preferred copy.
    for d in out:
        if d.get("dup_of") in (first, second) and any(x["id"] == merged_id for x in out):
            d["dup_of"] = merged_id
    return out


def reviewed_edda_lemma(line: str, form: str, lemma: str) -> str:
    """Wave-6 source/dictionary checks; preserve unrelated ewe/sea readings."""
    return {("edda:11377", "Œr", "ær"): "œrr@mad",
            ("edda:4383", "raari", "?raari"): "marr@horse"}.get((line, form, lemma), lemma)


def edda_region(line: int) -> tuple[str | None, bool]:
    """Reviewed introductory prose (one-based OCR lines) and owning poem."""
    for start, end, poem in ((5339, 5371, "Lokasenna"),
                             (12423, 12461, "Reginsmál"),
                             (15414, 15453, "Guðrúnarkviða en forna")):
        if start <= line <= end:
            return poem, True
    return None, False


def grein_apparatus(text: str) -> bool:
    # Numbered variant citations with manuscript/editor sigla, before OCR
    # normalization and lemmatization can make the quoted OE look like verse.
    return bool(re.search(r"\b\d+\)\s", text) and re.search(r"\b(?:MS|M3|Th|Grimm)\.", text))


def menota_numerals(text: str) -> str:
    """Expose normalized TEI numerals to the word loader, not their inner dots.

    Menota MLL 24v:22, 10v:12/27, 43v:26 provide explicit <num> values.
    No numeral value is inferred from surrounding legal prose.
    """
    def convert(match):
        if match[1] is None:
            return match[0]  # preserve existing word elements, including inner nums
        body = match[2]
        if '<w ' in body or '<w>' in body:
            return match[0]  # already tokenized; do not nest word elements
        value = re.search(r'\bvalue="([0-9]+)"', match[1])
        if not value:
            return match[0]
        n = value[1]
        return f'<w lemma="{n}" me:msa="xMC"><me:norm>{n}</me:norm></w>'
    return re.sub(r'<w\b[^>]*>.*?</w>|<num\b([^>]*)>(.*?)</num>', convert, text, flags=re.S)


def byliny_page_material(lines: list[str]) -> dict[int, str]:
    """Bounded page/footnote evidence, independent of source coordinates.

    A page-like window needs several full-width prose lines, word wrapping,
    and explicit critical vocabulary. Quotes and short verse remain protected.
    Numbering alone is never sufficient. OCR page numbers stop propagation.
    """
    normal = [_byliny_normal(s) for s in lines]
    out = {}
    critical = re.compile(r'\b(?:примечани|комментари|редактор|издател|рукопис|'
                          r'стихотворени|сравните|сравнивая|предислов|исследован)')
    boundary = re.compile(r'^\s*(?:\d{1,4}|[ivxlcхх]+)\s*[.]?\s*$', re.I)
    # Prefix counts keep the page pass linear in source length. This matters
    # for the many repeated full-edition loader checks in the suite.
    from bisect import bisect_left, bisect_right
    from itertools import accumulate
    word_counts = [len(_RU_WORD.findall(line)) for line in lines]
    counts = [
        [bool(line.strip()) for line in lines],
        [word_counts[j] >= 9 and len(line.strip()) >= 60 for j,line in enumerate(normal)],
        [bool(re.search(r'[а-яё]-\s*$', line)) for line in normal],
        [bool(critical.search(line)) for line in normal],
    ]
    prefix = [[0, *accumulate(values)] for values in counts]
    boundaries = [j for j,line in enumerate(lines) if boundary.fullmatch(line)]
    quoted = False
    protected = set()
    for i, line in enumerate(lines):
        if quoted or re.search('[«»„“]', line):
            protected.add(i)
        for char in line:
            if char == '«':
                quoted = True
            elif char == '»':
                quoted = False
        # Quotation state does not cross blank paragraph boundaries.
        if not line.strip():
            quoted = False
    for i, line in enumerate(lines):
        if i in protected or not line.strip():
            continue
        lo, hi = max(0, i-24), min(len(lines), i+25)
        before = bisect_left(boundaries, i)
        after = bisect_right(boundaries, i)
        if before:
            lo = max(lo, boundaries[before-1]+1)
        if after < len(boundaries):
            hi = min(hi, boundaries[after])
        size, wide, wrapped, anchors = [p[hi]-p[lo] for p in prefix]
        if (size >= 8 and wide >= 6 and wide / size >= .55 and
                wrapped >= 2 and anchors >= 2 and word_counts[i] >= 7):
            out[i] = 'critical-prose-page'
        # A compact block of independently signed editorial footnotes.
        if _RU_SIGNED_NOTE.search(line):
            nearby = lines[max(lo,i-5):min(hi,i+6)]
            if sum(bool(_RU_SIGNED_NOTE.search(s)) for s in nearby) >= 2 and any(
                _RU_NOTE_START.search(s) or _RU_EDITOR.search(_byliny_normal(s)) for s in nearby
            ):
                out[i] = 'footnote-block'
        if _RU_NOTES.fullmatch(normal[i].strip()):
            # Only the first bounded prose paragraph after an explicit heading;
            # embedded primary verse remains protected by shape and quotes.
            for j in range(i+1, min(hi,i+25)):
                if j not in protected and len(_RU_WORD.findall(lines[j])) >= 9 and critical.search(normal[j]):
                    out[j] = 'notes-section-prose'
    return out


# Harrison & Sharp, pg9701: notes/glossary identify adopted emendations.
# Coordinates refer to poem lines, not OCR numbering. No normalization-only
# accent/hyphen changes or unadopted apparatus proposals are included.
_ANG_EMENDATIONS = {
    ('Finn. 39', 'swētne'): ('hwitne', 'Finnsburh 39; Hickes transcript; Tolkien, Finn and Hengest, commentary to line 39'),
    ('Beo. 105', 'won-sǣlig'): ('won-sǣli', 'Harrison & Sharp, note to 105'),
    ('Beo. 218', 'fāmig-heals'): ('fāmi-heals', 'Harrison & Sharp, note to 218'),
    ('Beo. 281', 'bōt'): ('', 'Harrison & Sharp, glossary s.v. bōt'),
    ('Beo. 299', 'Gūð-fremmendra'): ('gōd-fremmendra', 'Harrison & Sharp, note to 299'),
    ('Beo. 367', 'glædnian'): ('glædman', 'Harrison & Sharp, note to 367'),
    ('Beo. 443', 'Gēatena'): ('Geotena', 'Harrison & Sharp, note to 443'),
    ('Beo. 499', 'Unferð'): ('Hunferð', 'Harrison & Sharp, note to 499'),
    ('Beo. 770', 'ealu-scerwen'): ('cerwen', 'Harrison & Sharp, note to 770 (second compound member)'),
    ('Beo. 1021', 'bearn'): ('brand', 'Harrison & Sharp, glossary s.v. brand'),
    ('Beo. 1279', 'dēað'): ('þeod', 'Harrison & Sharp, note to 1279'),
    ('Beo. 1364', 'hrīmge'): ('hrinde', 'Harrison & Sharp, note to 1364'),
    ('Beo. 1460', 'āter-tēarum'): ('', 'Harrison & Sharp, glossary s.v. tān (compound lemma āter-tān); Gutenberg correction'),
    ('Beo. 2210', 'wintru'): ('wintra', 'Harrison & Sharp, note to 2210'),
    ('Beo. 2247', 'fēa'): ('fec', 'Harrison & Sharp, note to 2247'),
    ('Beo. 2688', 'wundrum'): ('wundum', 'Harrison & Sharp, note to 2688'),
}


def reading_emendations(corpus: str, locus: str, text: str) -> list[dict]:
    """Verified adopted readings only; preserve the edition text and mapping."""
    if corpus != 'ang':
        return []
    return [dict(form=form, status='emended', source_reading=old, citation=cite)
            for (loc, form), (old, cite) in _ANG_EMENDATIONS.items()
            if locus.split(' (w')[0] == loc and
            re.search(r'(?<!\w)' + re.escape(form) + r'(?!\w)', text)]
