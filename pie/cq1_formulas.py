"""Corpus-quality batch 1, formula witness scan: homographs decided by form or corpus.

Evidence: data/research/8c/corpus-quality/error-verdicts-cq1-formulas.jsonl. Called through
pie.cq1_mapping (contextual lemma at token construction). Unlisted contexts keep their lemma.

- Greek ἰός: 'arrow' (< *(H)isu-, cf. Ved. íṣu-) and 'poison, rust' (< *wisós) share the lemma.
  The plural is 'arrow' only (LSJ s.v. ἰός A, B), so plural forms become ἰός@arrow; the singular
  stays ambiguous and keeps its automatic mapping. Homer has 'arrow' only (an override row).
- Epic Sanskrit kṣam: in the Mahābhārata selection every form of DCS kṣam is the verb 'forbear,
  endure' (kṣantum, kṣamasva, kṣānta-), not the Vedic noun kṣam- 'earth' (*dʰéǵʰōm), which the
  epic replaces with kṣmā / kṣamā. The verb has no lexicon etymon; it becomes kṣam@forbear
  (unmapped). Vedic (av) keeps kṣam: AVŚ kṣami is 'on the earth'.
"""

# LSJ s.v. ἰός: plural ἰοί (also the heteroclite ἰά is 'arrows' in Homer); never 'poison'.
GREEK_ARROW_PLURAL = frozenset({"ἰοί", "ἰῶν", "ἰοῖς", "ἰοῖσι", "ἰοῖσιν", "ἰούς", "ἰοὺς", "ἰά", "ἰοὶ"})


def contextual_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    if corpus in {"grc", "grp", "grc-late"} and lemma == "ἰός" and surface.strip(".,;·:") in GREEK_ARROW_PLURAL:
        return "ἰός@arrow"
    if corpus == "sa-ep" and lemma == "kṣam":
        return "kṣam@forbear"
    return lemma


def noncontent(corpus: str, lemma: str, surface: str, locus: str) -> bool:
    return False
