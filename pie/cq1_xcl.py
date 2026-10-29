"""Corpus-quality batch 1, area 'xcl' (Classical Armenian, DMHP): general rules with exception lists.

Evidence and per-report verdicts: data/research/8c/corpus-quality/error-verdicts-cq1-armenian.jsonl;
whole-corpus token counts per rule: error-verdicts-cq1-armenian-metrics.json (scripts/verify_cq1_xcl.py).
Called through pie.cq1_mapping (contextual lemma at token construction; non-content decision in
pie.formula_search.Token). One-off corrections are exact DMHP word ids in
data/research/formulas/cq1-readings-xcl.json; lemma-level mapping rows in
mapping-overrides/z-cq1-xcl.json.

Each rule names the incoming DMHP lemma(s) it corrects, the surfaces (letters only: punctuation,
accent and question marks stripped) and the exceptions: actual DMHP word coordinates (text id, word
id) whose context was read and which keep their lemma. Unlisted lemmas and surfaces are left alone.
Original surfaces, positions and source POS are never changed.
"""
from __future__ import annotations

import re

_NON_LETTER = re.compile(r"[^Ա-Ֆա-և]")
_WORD_ID = re.compile(r"word id (\d+)\)\s*$")


def norm(surface: str) -> str:
    """The Armenian letters of a surface (punctuation, ՛ ՜ ՞ and editorial marks dropped)."""
    return _NON_LETTER.sub("", surface)


def coord(locus: str) -> tuple[str, int] | None:
    """(DMHP text id, word id) of a loader locus 'MH_1_2_13_Lazar_Parp ed. page ... (word id N)'."""
    m = _WORD_ID.search(locus)
    return (locus.split(" ", 1)[0], int(m[1])) if m else None


LAZ, MOV, AGA = "MH_1_2_13_Lazar_Parp", "MH_1_2_12_Movses_Khor", "MH_1_2_11_Agathangelos"
FAU, YEG, EZN, GRE = "MH_1_1_04_Faustos", "MH_1_1_06_Yeghishe", "MH_1_1_05_Eznik", "MH_1_1_01_Gregor_Lus"
MAN = "MH_1_1_10_Mandakuni"

# ---------------------------------------------------------------- lexical rules
# (rule, incoming lemmas, surfaces (a set, or a regex on the letters), reviewed lemma, exceptions)
LEXICAL = [
    # ayr 'man' (*h₂nḗr): obl. pl. arancʻ, instr. aramb(-n), with y-/z-; DMHP gives ariwn 'blood'
    # (blood is arean, areamb, areancʻ). Kaikki Old Armenian այր; w10 r17, r55, w11 r1.
    ("ayr-oblique", {"ariwn", "yar", "zarm", "arawnd"},
     {"արանց", "արանցն", "արանցդ", "արամբ", "արամբն", "յարանց", "յարանցն", "զարամբ"}, "ayr", set()),
    # yarean 'they arose' (yar̄nem aor. 3pl), not i + arean 'from blood'; the one blood context kept.
    ("yarean-arose", {"ariwn"}, {"յարեան", "Յարեան"}, "yar̄nem", {(YEG, 85663)}),
    # tam 'give' (*deh₃-): impv. tur / towkʻ, aor. pass. towaw, pres. 2sg tas. DMHP gives towr 'gift',
    # tawn 'feast', tasn 'ten'. w10 r22, r33, r57, r110, w11 r6.
    ("tam-give", {"towr"}, {"տուր", "Տուր"}, "tam", set()),
    ("tam-give", {"tawn"}, {"տուաւ", "Տուաւ", "տուք", "Տուք", "տուքա"}, "tam", set()),
    ("tam-give", {"tasn"}, {"տաս"}, "tam", set()),
    ("tawt-heat", {"tawn"}, {"տաւթ", "տաւթոյն"}, "tawtʻ", set()),
    # towičʻ 'giver' (agent noun of tam), DMHP tiw 'day' (formula scan item 11).
    ("towich-giver", {"tiw", "tiow", "towir"}, {"տուիչ", "տուիչն", "զտուիչ", "զտուիչն"}, "towičʻ", set()),
    # giwł 'village', obl. gełǰ- (geawł / gełǰ): DMHP geł 'beauty' (*wel- see). w10 r89, r106, w11 r9;
    # reviewed lemma as the earlier Faustos word 61990 decision (geł@village, unmapped).
    ("village", {"geł", "gełł"}, {"գեղջ", "գեղջէ", "գեղջէն", "գեղջն", "զգեղջն"}, "geł@village", set()),
    ("village", {"gełik", "gełł", "gełowk"}, {"գեղջկաց", "զգեղջկաց", "գեղջկաւքն", "գեղջուկք", "զգեղջուկ"},
     "gełǰowk", set()),
    # erē 'wild animal': not erekʻ 'three' (երեք) or em 'be'. w10 r83, r96.
    ("ere-animal", {"erekʻ", "em"}, {"երէ", "զերէ", "էրէ"}, "erē", set()),
    # gan 'they come' (gam pres. 3pl); gan 'beating' (*gʷʰen-) kept where the context is beating
    # (gan ǝmpel / gan harkanel / gan braw-kʻ). w10 r103, formula scan item 10.
    ("gan-come", {"gan"}, {"գան"}, "gam",
     {(GRE, 54442), (EZN, 9280), (EZN, 9293), (EZN, 20908), (EZN, 21313), (YEG, 6075), (YEG, 23423), (YEG, 36870),
      (MAN, 34007), (AGA, 425), (AGA, 8484), (LAZ, 25016)}),
    # gini 'wine' (*wóyh₁nom), goyn 'colour' (obl. gunoy, gunov): DMHP gin 'price'. w10 r39.
    ("gini-wine", {"gin"}, {"գինի", "Գինի", "գինւոյ", "գինւոյն", "գինւով", "գինոյն", "գինով", "գինւոջ"},
     "gini", set()),
    ("goyn-colour", {"gin"}, {"գունով", "գունոյ"}, "goyn", set()),
    # goyn 'colour' (Iranian loan): DMHP gom 'exist'. Eznik's i Goyn 'the Existent' and the unclear
    # Eznik 30084 keep gom. w10 r31 (w9 r89 fixed one Faustos token).
    ("goyn-colour", {"gom"}, {"գոյն", "Գոյն"}, "goyn", {(EZN, 827), (EZN, 30084)}),
    # elicʻ 'filled' (lnowm aor. 3sg); kept: elkʻ 'exit, rising' (gen. pl. elicʻ: əst elicʻ 'east',
    # yet elicʻ 'after the departure', elicʻ ew mticʻ) and elanem subj. 1sg 'I shall go out'. w10 r28.
    ("elic-filled", {"elkʻ"}, {"ելից"}, "lnowm",
     {(FAU, 34931), (FAU, 42332), (FAU, 42351), (YEG, 30129), (AGA, 4081), (AGA, 30201), (MOV, 17667),
      (MOV, 40804), (MOV, 49839), (MOV, 64564), (MOV, 67465), (MOV, 77895), (LAZ, 13982), (LAZ, 22715)}),
    # i mti 'in mind' (mit, loc. sg.), DMHP mtanem 'enter'; Yeghishe 34671 is mti 'I entered'. w10 r21.
    ("mti-mind", {"mtanem"}, {"մտի"}, "mit", {(YEG, 34671)}),
    # ałē 'come now!' (exhortative particle), DMHP ał 'salt'. w10 r24.
    ("ale-particle", {"ał"}, {"աղէ", "Աղէ"}, "ałē", set()),
    # cpʻan(kʻ) 'surge' (gen. pl. cpʻanacʻ), cpʻowmn; DMHP cownr 'knee'. w10 r3.
    ("cpan-surge", {"cownr"}, {"ծփանաց", "ծփանացն"}, "cpʻan", set()),
    ("cpan-surge", {"cownr"}, {"զծփումն"}, "cpʻowmn", set()),
    # ost 'branch' (gen. pl. ostocʻ), DMHP otn 'foot'. w10 r23.
    ("ost-branch", {"otn"}, re.compile(r"^ոստոց"), "ost", set()),
    # kanon 'canon', DMHP kin 'woman'. w10 r26.
    ("kanon", {"kin"}, re.compile(r"^կանոն"), "kanon", set()),
    # zroycʻ 'story, account', DMHP or 'which' and unanalysed stems. w10 r19.
    ("zroyc-story", {"or", "rowr", "orkʻ", "zrowr", "zrowrankʻ"},
     re.compile(r"^(զրոյց(ն|ս|սն|ք|քն)?|զրուցաց(ն|ս)?)$"), "zroycʻ", set()),
    # orear 'men, people' (Kaikki որեար), DMHP or 'which' / em 'be'. w10 r19 obs. 3-5.
    ("orear-men", {"or", "em", "orem"}, re.compile(r"^որեար"), "orear", set()),
    # cʻrowem 'scatter' (pres. 3sg cʻrē), DMHP ēr 'was'. w10 r30.
    ("crowem-scatter", {"ēr"}, {"ցրէ"}, "cʻrowem", set()),
    # erknem 'be in labour' (impf. 3sg erknēr), DMHP erknčʻim 'fear'. w10 r59 obs.
    ("erknem-labour", {"erknčʻim"}, {"երկնէր", "Երկնէր"}, "erknem", set()),
    # yownarēn 'in Greek', DMHP ownayn 'empty'. w10 r70.
    ("yownaren-greek", {"ownayn"}, {"յունարէն", "Յունարէն"}, "yownarēn", set()),
    # haraw 'south', DMHP harkanem 'strike'; kept: aor. pass. haraw 'was struck' (zahi haraw, dew haraw).
    ("haraw-south", {"harkanem"}, {"հարաւ"}, "haraw",
     {(FAU, 27326), (FAU, 59693), (YEG, 27866), (YEG, 27985), (YEG, 30542), (YEG, 34943), (YEG, 47165),
      (AGA, 19874)}),
    # jowkn 'fish' (instr. pl. jkambkʻ), DMHP jkowk / jkowmn. w10 r84.
    ("jowkn-fish", {"jkowk", "jkowmn"}, re.compile(r"^ձկամբ"), "jowkn", set()),
    # dram 'coin' (Greek loan), DMHP dar / dowr̄n 'door'. w10 r97 obs.
    ("dram-coin", {"dar", "dowr̄n"}, {"դրամ", "զդրամ", "ցդրամ"}, "dram", set()),
    # ericʻ 'of three' (erekʻ gen. pl.), DMHP er. w10 r99.
    ("eric-three", {"er"}, {"երից"}, "erekʻ", set()),
    # amis 'month' (*meh₁n̥s-), DMHP am 'year' or unanalysed. w10 r95, w11 r21.
    ("amis-month", {"am", "ssis", "amssis"}, {"ամիս", "ամիսն", "ամիսս"}, "amis", set()),
    # baniw(kʻ) instr. of ban 'word', DMHP bnaw 'altogether'. w11 r29.
    ("ban-word", {"bnaw", "bnawm"}, re.compile(r"^բանիւ(ն|ք|քն|քս)?$"), "ban", set()),
    # y-ariwn 'into blood', DMHP yarm. w11 r33.
    ("yariwn-blood", {"yarm"}, {"յարիւն"}, "ariwn", set()),
    # šat 'much', DMHP šta. w10 r109.
    ("shat-much", {"šta"}, {"շատ"}, "šat", set()),
    # erǰanik 'blessed', DMHP erkayn 'long'. w10 r113.
    ("erjanik", {"erkayn"}, re.compile(r"^երջանիկ"), "erǰanik", set()),
    # lcʻowcʻanem 'fill' (causative of lnowm), DMHP lowcʻanem 'light'. w10 r44 (w9 mapping row). The agent
    # noun lcʻowcʻičʻ is left to its reviewed reading (w7, Yeghishe word 71033).
    ("lcowcanem-fill", {"lowcʻanem"}, re.compile(r"^լց(?!ուցիչ)"), "lcʻowcʻanem", set()),
    # akanǰ 'ear(s)' (Martirosyan EDAIL: old dual of unkn), DMHP ownkn. w10 r121.
    ("akanj-ear", {"ownkn", "awnkn", "owkand", "awdnam"}, re.compile(r"^[զյ]?ականջ"), "akanǰ", set()),
]

# ---------------------------------------------------------------- proper names
# (rule, regex on the letters, reviewed name lemma, incoming lemmas (None: any not already a name),
#  exceptions). Every stem was read in all its corpus contexts (verdict ledger).
NAMES = [
    ("name-greeks", re.compile(r"^([զցյ]?[Յյ]ունաց(ն)?|զՅունաւք)$"), "yoyn (name)",
     {"ownim", "own", "yoyn", "yown"}, set()),
    ("name-aryans", re.compile(r"^([զյ]?Արեաց(ն|ս)?|Արեաւք|[զյ]?Արիս(ի)?)$"), "ari (name)",
     {"ariwn", "yar̄nem", "aris"}, set()),
    # Arikʻ 'Aryans' vs. arikʻ 'arise!' (yar̄nem aor. impv. 2pl): the imperatives are kept.
    ("name-aryans", re.compile(r"^Արիք$"), "ari (name)", {"yar̄nem"},
     {(FAU, 59682), (FAU, 59700), (YEG, 94044), (YEG, 94066), (YEG, 94088), (YEG, 94096), (YEG, 94104),
      (YEG, 94115)}),
    ("name-mar", re.compile(r"^զ?Մար$"), "Mar (name)", {"mayr", "mar"}, set()),
    ("name-medes", re.compile(r"^(Մարք|Մարաւք|զ?Մարաց(ն)?)$"), "Markʻ (name)", {"mayr", "mar̄n", "mar"}, set()),
    ("name-medes", re.compile(r"^Մեդաց$"), "Medkʻ (name)", {"mekʻ"}, set()),
    ("name-uti", re.compile(r"^[զյ]?Ուտի(ոյ|ա)?$"), "Owti (name)", None, set()),
    ("name-asia", re.compile(r"^[զյ]?Ասի(ա|այ|ալ|ոյ)$"), "Asia (name)", None, set()),
    ("name-garni", re.compile(r"^զ?Գառնի(ն)?$"), "Gar̄ni (name)", {"gar̄n", "zgar̄n"}, set()),
    ("name-ormizd", re.compile(r"^[զյց]?Որմի?զդ(ի|ն|է)?$"), "Ormizd (name)", None, set()),
    ("name-hark", re.compile(r"^զ?Հարք$"), "Harkʻ (name)", {"hayr", "hark"}, {(GRE, 17587)}),
    ("name-aram", re.compile(r"^[զց]?Արամ(ի|այ)?$"), "Aram (name)", {"ar̄nem", "aram", "cʻar̄am", "aramay"}, set()),
    ("name-astlik", re.compile(r"^Աստղիկ$"), "Astłik (name)", {"astłik"}, set()),
    ("name-anush", re.compile(r"^յԱնուշն$"), "Anowš (name)", {"anown"}, set()),
    ("name-azhdahak", re.compile(r"^[զյ]?Աժդահակ(այ|դ)?$"), "Aždahak (name)", None, set()),
    ("name-tigran", re.compile(r"^զ?Տիգրան(այ|ն|ալ)?$"), "Tigran (name)", None, set()),
    ("name-eruand", re.compile(r"^զ?Երուանդ(այ)?$"), "Eruand (name)", None, set()),
    ("name-eruand", re.compile(r"^Երուանդեան(ս|ք)?$"), "Eruandean (name)", None, set()),
    ("name-kura", re.compile(r"^[զց]?Կուր$"), "Kowr (name)", {"kowr", "kowrkʻ"}, set()),
    ("name-trelk", re.compile(r"^Թռեղք$"), "Tʻr̄ełkʻ (name)", None, set()),
    ("name-mashtots", re.compile(r"^զ?Մաշտոց(ի|իւ|է)$"), "Maštocʻ (name)", None, set()),
    ("name-makuran", re.compile(r"^զՄակուրան$"), "Makowran (name)", None, set()),
    ("name-zarewand", re.compile(r"^Զարեւանդ(այ)?$"), "Zarewand (name)", None, set()),
    ("name-samuel", re.compile(r"^զ?Սամուէլ(ի|այ|ն)?$"), "Samowēl (name)", None, set()),
    ("name-karen", re.compile(r"^զ?Կարէն(ն)?$"), "Karēn (name)", {"karem", "kari"}, set()),
    ("name-koshm", re.compile(r"^Կոշմ(այ)?$"), "Košm (name)", {"košem", "košm"}, set()),
    ("name-halys", re.compile(r"^զԱլիս$"), "Alis (name)", {"ali"}, set()),
]

# ---------------------------------------------------------------- numerals
# Armenian letter numerals (Ա 1 ... Թ 9, Ժ 10 ... Ղ 90, Ճ 100 ... Ջ 900), printed as chapter and section
# numbers: uppercase with a period (Լ., ԿԶ., ՃԺԹ.), uppercase without a period when two or more letters
# (ԺԹ, ՅԻԱ), and in Movses' Geography lowercase list numbers (ա. ... ժ., ժա. ... խդ.). Exceptions: an
# all-caps title word (Mandakuni ՆԱ.) and Eznik Ո. (not a section number). w10 r46, r47, w11 r27.
_NUM_LETTERS = "ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋ"
_NUM_VALUE = {ch: (i % 9 + 1) * 10 ** (i // 9) for i, ch in enumerate(_NUM_LETTERS)}
_UPPER_DOT = re.compile(r"[Ա-Ֆ]{1,4}\.")
_UPPER_BARE = re.compile(r"[Ա-Ֆ]{2,4},?")
_LOWER_DOT = re.compile(r"[ա-և]{1,2}\.")
_LOWER_SINGLE = set("աբգդեզըթժ")
# printed section numbers whose letters do not form a well-ordered numeral (OCR): read, kept as numbers
_GARBLED_SECTIONS = {"ԽԼ.", "ՀԻ.", "ՑԱ.", "ԶԵ.", "ԼԳԱ.", "ՂԼԲ."}
NUMERAL_EXCEPTIONS = {(MAN, None, "ՆԱ."), (EZN, None, "Ո.")}


def numeral_value(letters: str) -> int | None:
    """Value of a well-formed letter numeral (one letter per decimal order, descending), else None."""
    up = letters.upper()
    if not up or any(c not in _NUM_VALUE for c in up):
        return None
    vals = [_NUM_VALUE[c] for c in up]
    orders = [len(str(v)) for v in vals]
    if orders != sorted(orders, reverse=True) or len(set(orders)) != len(orders):
        return None
    return sum(vals)


def numeral_lemma(surface: str, locus: str) -> str | None:
    c = coord(locus)
    text = c[0] if c else locus.split(" ", 1)[0]
    if (text, None, surface) in NUMERAL_EXCEPTIONS:
        return None
    if surface in _GARBLED_SECTIONS:
        return "section@numeral"
    if _UPPER_DOT.fullmatch(surface):
        v = numeral_value(surface[:-1])
    elif _UPPER_BARE.fullmatch(surface):
        v = numeral_value(surface.rstrip(","))
    elif text == MOV and _LOWER_DOT.fullmatch(surface):
        letters = surface[:-1]
        if len(letters) == 1 and letters not in _LOWER_SINGLE:
            return None
        if len(letters) == 2 and not (letters[0] in "ժիլխծկհձղ" and letters[1] in "աբգդեզէըթ"):
            return None
        v = numeral_value(letters)
    else:
        return None
    return f"{v}@numeral" if v else None


# ---------------------------------------------------------------- application

def rule_for(corpus: str, lemma: str, surface: str, locus: str) -> tuple[str, str] | None:
    """(rule name, reviewed lemma) for a DMHP token one of the rules corrects, else None."""
    if corpus != "xcl" or lemma.endswith((" (name)", "@numeral")):
        return None
    num = numeral_lemma(surface, locus)
    if num:
        return "numeral", num
    n, c = norm(surface), coord(locus)
    for name, olds, forms, new, exc in LEXICAL:
        if lemma in olds and (n in forms if isinstance(forms, set) else forms.search(n)) and c not in exc:
            return name, new
    for name, pat, new, olds, exc in NAMES:
        if (olds is None or lemma in olds) and pat.search(n) and c not in exc:
            return name, new
    return None


def contextual_lemma(corpus: str, lemma: str, surface: str, locus: str) -> str:
    hit = rule_for(corpus, lemma, surface, locus)
    return hit[1] if hit else lemma


def noncontent(corpus: str, lemma: str, surface: str, locus: str) -> bool:
    """Armenian names (any reviewed ' (name)' lemma: DMHP's own N+Top / N+Ant are already non-content)
    and numerals are not content words."""
    return corpus == "xcl" and lemma.endswith((" (name)", "@numeral"))
