"""Corpus-quality batch 2 (cq2): general rules with exception lists, outside Celtic and Slavic.

Evidence: data/research/8c/corpus-quality/error-verdicts-cq2.jsonl; report
docs/research/8c-corpus-quality-batch2.md. Called through pie.cq1_mapping (contextual lemma at token
construction; non-content decision in pie.formula_search.Token). Unlisted contexts keep their lemma.

Rules:
  - Greek (grc, grp, grc-late, hom), capitalised lemmas (greek_capitalised). The treebanks' lemma keeps
    the capital of a proper noun or adjective (Μακεδών, Θεσσαλός, Ἀρκάς, Κύκλωψ), and the automatic
    mapping then reached the common-word homograph (Ἀρκάς -> ἄρκτος 'bear'). A capitalised lemma with a
    lower-case letter is a name, decided by pie.name_mapping.name_lemma: the THEONYMS deities and
    personified powers keep their lemma and ids (Ζεύς, Ἠώς, Ἥλιος), every other name becomes
    '<lemma> (name)', non-content. Exceptions, which keep the common lower-case lemma:
      * function words written with a capital (GREEK_FUNCTION_CAPITALS: Καί, Περι, Κατά, Τοί ...):
        lower-cased and non-content; pronominal adjectives, quantifiers and ordinals
        (GREEK_ADJECTIVE_CAPITALS: Πᾶς, Ἄλλος, Μέγας, Τρίτος): lower-cased, content as their POS says;
      * verbs (citation ending -ω unaccented, -μαι, -μι): lower-cased (Φαίνω, Εἰμί, Δείκνυμι);
      * the measured list data/research/formulas/cq2-greek-capitalised.json ("common"): the
        lower-case lemma is at least 100 times as frequent and the capitalised form is no Kaikki
        headword (sentence-initial and title capitals: Λόγος, Πόλις, Ἀγαθός).
    An all-capital lemma (Α, Ε, Η, ΔΕ, ΓΕ: letter labels and inscriptions in capitals) is non-content.
  - GLAUx Ἀοῦς lemmatised Ἀών (Pind. O. 2.83, Bacchyl. 17.42): Ἀών 'Aon' has the genitive Ἀόνος;
    Ἀοῦς is the Doric genitive of Ἀώς = Ἠώς 'Dawn' (LSJ s.v. ἠώς), so the lemma is Ἠώς.
  - Armenian գան: lead decision (batch 2) to follow the cq1 rule gan -> gam everywhere; the two
    wave-8/9 readings gam@present (Movses 82268, Yeghishe 20801) become gam, whose reviewed row is
    *weh₂(dʰ)- 'go' (arm-toch-alb.json, Martirosyan EDAIL 196), the etymology the w8 reviewer gave the
    present; gam@present was unmapped.
  - Welsh neint 'streams, valleys' (pl. of nant, GPC s.v. nant) lemmatised deint 'teeth' (pl. of dant):
    surface neint -> nant. All 10 tokens of the cq2 index read: blaen neint, adar ... neint (Skene,
    Red Book poetry); none after a nasal-mutation trigger (fy, yn), which would make it 'my teeth'.
"""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEK = frozenset({"grc", "grp", "grc-late", "hom"})
CAPITALS_TABLE = ROOT / "data/research/formulas/cq2-greek-capitalised.json"

# capitalised function words found among the capitalised content lemmas of the cq1 index (particles,
# prepositions, conjunctions, article and pronoun forms, numerals): lower-cased and non-content
GREEK_FUNCTION_CAPITALS = frozenset("""
Καί Τοί Τώς Πρός Τέ Τε Οὐ Οὔ Τῆ Τῆς Τής Ἐγώ Ὅς Τί Ἐν Ἀνά Ἀπό Πέρα Μά Ἐντός Εἶ Ταχέως Νώ Περι Περ Κατά
Ὦς Ὡς Τοτέ Τότε Τό Τός Τάς Μή Ἄν Ἐπί Εὖ Ἅλις Ἄλις Ἆλις Οἱ Ἀλλά Μετά Σύν Παρά Πῶς Εἰς Νῦν Ἄγαν Πρό
Ἅπαξ Ἁπάξ Ἅς Ἐκ Ἄφνω Πλήν Νή Νῆ Ὦ Ὥ Τίς Ἑπτά Τρίς Τρεῖς Ἕξ Τέσσαρες Δύο Πέντε Μία Εἷς Ἑκατόν Ἄμφω
""".split())
# capitalised pronominal adjectives, quantifiers and ordinals: lower-cased, content as their POS says
GREEK_ADJECTIVE_CAPITALS = frozenset("""
Τόσος Αὑτός Πολλός Ὅσος Ἆλλος Πλεῖστος Ἕτερος Ἄλλος Πᾶς Ὅμοιος Ἀμφότερος Ἀμφοτερός Ποιός Ἕκαστος
Ἑκάτερος Αὐτός Ἕβδομος Πέμπτος Ἕκτος Τρίτος Πρότερος Ὕστερος Μόνος Ἴσος Ἶσος Πολύς Μέγας
""".split())
_VERB_ENDINGS = ("ω", "μαι", "μι")


@lru_cache(maxsize=1)
def _common_capitals() -> frozenset:
    if not CAPITALS_TABLE.exists():
        return frozenset()
    return frozenset(json.loads(CAPITALS_TABLE.read_text("utf-8"))["common"])


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def lower_initial(s: str) -> str:
    d = unicodedata.normalize("NFD", s)
    return _nfc(d[:1].lower() + d[1:])


def _upper_initial(s: str) -> str:
    d = unicodedata.normalize("NFD", s)
    return _nfc(d[:1].upper() + d[1:])


def all_capitals(lemma: str) -> bool:
    letters = [c for c in lemma if c.isalpha()]
    return bool(letters) and not any(c.islower() for c in letters)


def greek_capitalised(corpus: str, lemma: str) -> str:
    """The batch-2 decision for a capitalised Greek lemma (see the module docstring)."""
    lem = _nfc(lemma)
    if lem in GREEK_FUNCTION_CAPITALS or lem in GREEK_ADJECTIVE_CAPITALS:
        return lower_initial(lem)
    plain = "".join(c for c in unicodedata.normalize("NFD", lem) if not unicodedata.combining(c))
    if plain.endswith(_VERB_ENDINGS) and not lem.endswith("ώ"):
        return lower_initial(lem)
    if lem in _common_capitals():
        return lower_initial(lem)
    from .name_mapping import name_lemma
    return name_lemma(corpus, lemma)


def contextual_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    if corpus in GREEK:
        if lemma == "Ἀών" and surface.strip(".,;·:’'") == "Ἀοῦς":
            lemma = "Ἠώς"
        if (lemma[:1].isupper() and not lemma.endswith(" (name)") and "@" not in lemma
                and not all_capitals(lemma)):
            return greek_capitalised(corpus, lemma)
        return lemma
    if corpus == "xcl" and lemma == "gam@present":
        return "gam"
    if corpus == "cy" and lemma == "deint" and surface.strip(".,;:!?'’").lower() == "neint":
        return "nant"
    return lemma


def noncontent(corpus: str, lemma: str, surface: str, locus: str) -> bool:
    if corpus in GREEK:
        if all_capitals(lemma) and not lemma.endswith(" (name)"):
            return True
        # a capitalised function word, lower-cased by contextual_lemma (always a function word)
        if lemma[:1].islower() and surface[:1].isupper() and _upper_initial(lemma) in GREEK_FUNCTION_CAPITALS:
            return True
    return False
