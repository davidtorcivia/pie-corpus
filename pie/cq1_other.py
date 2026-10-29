"""Corpus-quality batch 1, area 'other': general rules with exception lists.

Evidence: data/research/8c/corpus-quality/error-verdicts-cq1-other*.jsonl. Called through
pie.cq1_mapping (contextual lemma at token construction; non-content decision in
pie.formula_search.Token). Unlisted contexts keep their lemma.

Rules (token counts measured on the production loaders, error-verdicts-cq1-other-metrics.json):
  - ang (Grein OCR): a surface with no vowel letter (cn, hl, dm, td ...) is an OCR fragment whose
    long vowels were lost; the lemmatizer's consonant-skeleton guess (cn -> cwēn) is not a reading.
    It becomes the unknown lemma '?<surface>' (still a content slot, never mapped). Exceptions:
    guesses that are already non-content (ANG_NONCONTENT_EXCEPTIONS), so no slot is added.
  - grc / grp / grc-late (GLAUx automatic lemmas): a δεξ- middle form (participle, infinitive,
    finite middle) lemmatised δείκνυμι is δέχομαι 'receive' (*deḱ-). Ionic active δέξω / δέξαι /
    δέξας / δέξειν 'show' (Herodotus) are not middle forms and keep δείκνυμι.
  - hom: Πολίτης (capitalised AGDT lemma) is the personal name Polites (Il. 2.791, 13.533,
    15.339, 24.250, Od. 10.224), never the common noun πολίτης.
  - byliny: the lemmatizer files every form of старуха 'old woman' under старик 'old man'; a
    старух- surface lemmatised старик is старуха (same *sth₂ró- mapping, a reviewed lemma row).
  - vuk: смела (lemma smeo 'bold') and смеће (lemma smeće 'rubbish' | smeti 'dare') are forms of
    smesti 'confuse, drop, lose' in every occurrence (Vuk 1546:113, 28059:72, 23725:174; 23664:69,
    29609:21, 47944:3).
"""
import re
import unicodedata

_ANG_VOWEL = re.compile(r"[aeiouyæœøǣǽāēīōūȳáéíóúý]", re.I)
_DEX_MIDDLE = re.compile(r"^δεξ.*(αμεν|ομεν|ασθ|εσθ|ατο|αντο|οιτο|οιντο|αιτο|αιντ|αιθ|αιατ|οιατ|ωμεθ|ονται|εται|ηται|ησθε)")
GREEK = {"grc", "grp", "grc-late"}
# Grein lemmas that the dictionary POS already makes non-content (st, nd -> end, bm -> bēgen, sn):
# an unknown '?x' lemma would turn them into content slots, so they are left alone.
ANG_NONCONTENT_EXCEPTIONS = {"st", "end", "bēgen", "sn"}
VUK_FORMS = {("smeo", "смела"): "smesti", ("smeće|smeti", "смеће"): "smesti"}


def _plain_greek(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return unicodedata.normalize("NFC", "".join(c for c in s if not unicodedata.combining(c)))


def contextual_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    if corpus == "ang" and len(surface) > 1 and not lemma.startswith("?") and lemma not in ANG_NONCONTENT_EXCEPTIONS \
            and not _ANG_VOWEL.search(unicodedata.normalize("NFC", surface)) and re.fullmatch(r"\w+", surface):
        return "?" + surface.lower()
    if corpus in GREEK and lemma == "δείκνυμι" and _DEX_MIDDLE.search(_plain_greek(surface)):
        return "δέχομαι"
    if corpus == "hom" and lemma == "Πολίτης":
        return "Πολίτης (name)"
    if corpus == "byliny" and lemma == "старик" and surface.lower().startswith("старух"):
        return "старуха"
    if corpus == "vuk":
        return VUK_FORMS.get((lemma, surface), lemma)
    return lemma


def noncontent(corpus: str, lemma: str, surface: str, locus: str) -> bool:
    return False
