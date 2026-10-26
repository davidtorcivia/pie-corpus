"""Reviewed non-Irish stem/sense distinctions, before lemma-level mapping.

Sources and individual verdicts: data/research/8c/stageCS/error-verdicts-other.jsonl.
Qualified lemmas have explicit reviewed mapping rows; a homonym is not
silently assigned the etymology of another member of its paradigm.
"""


def homer_lemma(lemma: str, form: str) -> str:
    # AGDT assigns Od. 5.490 alpha-u-oi and the cries to one lemma.
    # Beekes EDG p. 175, auo 1 versus auo 2.
    if lemma == "αὔω" and form == "αὔοι":
        return "αὔω@kindle"
    # The -iont- participle belongs to eimi 'go', not eimi 'be'.
    if lemma == "ἔπειμι" and form.startswith("ἐπιόν"):
        return "ἔπειμι@go"
    return lemma


def latin_lemma(lemma: str, form: str, identifiers: list[str]) -> str:
    # LASLA's persistent lexical identifiers distinguish its merged headwords.
    # Lucr. 6.1258 (ede-re vitam); 2.511 (or-is sapori).
    if lemma == "edo" and "lilaLemma:100577" in identifiers:
        return "edo@give"
    if lemma == "os" and "lilaLemma:115327" in identifiers:
        return "os@mouth"
    return lemma


def dcs_lemma(lemma: str, form: str) -> str:
    # Kaikki Sanskrit s.v. pash (see) versus drsh; DCS MBh 7.142.s55.
    if lemma == "dṛś" and form.startswith("paśy"):
        return "paś@see"
    return lemma


def hittite_selection(attributes: dict, tablet: str, line: str) -> dict:
    # TLHdig KUB 36.89: the speech addresses the god in the second person.
    # Select an existing analysis; do not rewrite the source or other tokens.
    selection = {
        ("KUB 36.89", "Rs. 57′", "ešta"): ("2a", "eš-@sein@"),
        ("KUB 36.89", "Rs. 58′", "arai"): ("2b", "ar=ae-@erheben@"),
    }.get((tablet, line, attributes.get("trans")))
    if selection and attributes.get("mrp2", "").startswith(selection[1]):
        return {**attributes, "mrp0sel": selection[0]}
    return attributes


def contextual_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    """Narrow source-locus corrections where annotation cannot separate senses.

    Applied at token construction so mapping and packet loaders agree. These
    are actual source-token loci, not the sometimes earlier unit-start labels
    in reader reports. Unlisted contexts retain their original lemma.
    """
    from .w4_other_mapping import reviewed_lemma
    lemma = reviewed_lemma(corpus, lemma, surface, locus)
    from .w5_other_mapping import reviewed_lemma as w5_reviewed_lemma
    lemma = w5_reviewed_lemma(corpus, lemma, surface, locus)
    from .w6_other_mapping import reviewed_lemma as w6_reviewed_lemma
    lemma = w6_reviewed_lemma(corpus, lemma, surface, locus)
    from .w7_other_mapping import reviewed_lemma as w7_reviewed_lemma
    lemma = w7_reviewed_lemma(corpus, lemma, surface, locus)
    # Wave 2: source and dictionary checks are recorded in
    # error-verdicts-w2-other.jsonl. Keep homographs outside these contexts.
    if corpus in {"grc", "grp", "grc-late"}:
        if lemma == "ὁράω" and surface in {"εἶδε", "εἶδον"}:
            return "εἶδον@see"
        # Source-locus corrections independently checked in wave 3.
        fixes = {
            ("Hesiodus Opera et dies 563", "ἐνείκῃ", "φέρω"): "φέρω@aorist",
            ("Thucydides Historiae 2.92.1 s1", "κελεύσματος", "κέλευθος"): "κέλευσμα",
            ("Euripides Ion 1403", "λιποῦσα", "λιπάω"): "λείπω",
            ("Herodotus Historiae 2.39.2 s1", "καταρησάμενοι", "καταλέγω"): "καταράομαι",
            ("Herodotus Historiae 2.126.1 s3", "δέεσθαι", "δέω"): "δέω@need",
        }
        if (locus, surface, lemma) in fixes:
            return fixes[locus, surface, lemma]
        if lemma == "λέγω" and surface == "εἶπε":
            return "εἶπον@say"
        if locus == "Thucydides Historiae 1.1.1 s1" and surface == "ᾖσαν" and lemma == "ἔρχομαι":
            return "εἰμί"
        if locus == "Thucydides Historiae 4.75.2 s1" and surface == "Κάλητα":
            return "Κάλης (name)"
    if corpus == "orv" and lemma == "поити" and surface == "поидоша":
        return "поити@go"
    if corpus == "vuk" and locus == "Vuk 22093:40" and surface == "секу":
        return "seka"
    if corpus == "vuk" and locus == "Vuk 33208:10" and surface == "мрклој":
        return "mrkli"
    if corpus == "byliny" and locus == "pesnisobrannyepvkireevskimch2pes74:203" and surface == "стБну":
        return "стена"
    if corpus == "lv" and locus == "p0216" and surface == "vilka":
        return "vilkt"
    if corpus == "menota":
        if locus == "AM-35-fol 201:" and surface == "eydana":
            return "Eydanir (name)"
        if locus == "AM-63-fol 62:" and surface == "brenosteini":
            return "brennisteinn"
        fixes = {
            ("AM-63-fol 326:", "mól", "mál"): "mala",
            ("AM-36-fol 473:29", "mǫðr", "móðr"): "móðir",
            ("AM-36-fol 427:29", "heila", "heill"): "heili",
            ("AM-242-fol 24:10", "vín", "vinr"): "vín",
        }
        if (locus, surface, lemma) in fixes:
            return fixes[locus, surface, lemma]
        if surface == "þa(+K)" and lemma == "þak" and locus.startswith("AM-36-fol "):
            return "þá"
    if corpus == "xcl":
        fixes = {
            ("MH_1_2_12_Movses_Khor", "18372", "or"): "ors",
            ("MH_1_1_04_Faustos", "28360", "mayr"): "Mari (name)",
            ("MH_1_1_04_Faustos", "13418", "bambir"): "Bambišn (name)",
            ("MH_1_1_04_Faustos", "13422", "tiranam"): "Tiran (name)",
        }
        for (work, word, old), new in fixes.items():
            if work + " " in locus and f"(word id {word})" in locus and lemma == old:
                return new
        if "MH_1_1_06_Yeghishe " in locus and "(word id 9391)" in locus and lemma == "haw":
            return "haw@ancestor"
        if "MH_1_1_04_Faustos " in locus:
            if "(word id 61988)" in locus and lemma == "hazat":
                return "Haband (name)"
            if "(word id 61990)" in locus and lemma == "geł":
                return "geł@village"
    if corpus == "ang" and locus == "Grein I A Za R I A S l.10871" and lemma == "sniwan|snīwan":
        return "snīw@noun"
    if corpus == "cy" and "whitebookofmabin00evan:L17235-L17250" in locus and surface == "kae" and lemma == "cae":
        return "cau@close"
    if corpus == "hom" and locus == "Il. 5.176" and surface == "ἔλυσεν" and lemma == "ἐλύω":
        return "λύω"
    if corpus == "sa-ep" and locus == "MBh, 9, 7.s28" and surface == "droṇasya" and lemma == "droṇa":
        return "Droṇa (name)"
    if corpus == "av" and lemma == "vid" and surface in {"veda", "vidma"}:
        return "vid@perfect"
    return lemma
