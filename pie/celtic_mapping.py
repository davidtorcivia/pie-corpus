"""Celtic lemmatizers and lemma → PIE tables (Phase 8c, Stage C).

Irish (Old, Middle, Early Modern) and Welsh (Old, Middle, print-normalised)
text is unlemmatized apart from the Old Irish glosses. This module gives

  * tokenizers that keep the hyphens and middle dots the editions use to mark
    mutations, clitics and preverbs (`irish_words`, `welsh_words`);
  * mutation stripping (`irish_demutate`, `welsh_demutate`) and orthographic
    keys (`irish_skeleton`, `welsh_skeleton`) for Middle Irish / Middle Welsh
    spellings of Old Irish / dictionary headwords;
  * the language mappings: kaikki Old Irish, Middle Irish and Irish
    (Old Welsh, Middle Welsh and Welsh) entries resolved through
    formula_search_multi's chain / desc / lexicon / form-of / base steps,
    plus two daughter-aware steps the generic builder lacks:
      chain-<lang>   a later-language entry whose only etymology is "from Old
                     Irish X" (Middle Welsh / Old Welsh X) takes X's mapping;
      later-<lang>   an Old Irish (Old/Middle Welsh) headword without an
                     etymology takes the proto-language chain of a Middle or
                     Modern Irish (Welsh) entry that cites it as its source;
    and Matasović's EDPC headwords (`matasovic_entries`) as a last source;
  * `CelticLemmatizer`: surface → lemma key(s) through kaikki forms tables
    and the glosses' (form, lemma) pairs; exact key first, then the
    accent-free key, then mutation-stripped variants, then the orthographic
    skeleton (unique answers only). Preverb compounds and infixed pronouns
    are not analysed: a form not in a table stays unknown ('?' + key).

Nothing under raw/ is executed or imported; dumps are read as JSON or text.
Outputs hold dictionary headwords, lemma keys and ids, never corpus text.
"""

from __future__ import annotations

import collections
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import formula_search as fs
from . import formula_search_multi as fm
from . import mapping as mp

ROOT = fs.ROOT
KD = fm.KD
SPLIT = "kaikki-all-20261021/split"

# ---------------------------------------------------------------- language registry (additive)
#
# formula_search_multi knows Old Irish only. The Celtic daughters are added to
# its registries here (setdefault: nothing existing is changed). Form rows in
# the override files must still use lang 'sga' (load_overrides keys every form
# row with KEYS[lang], and may run without this module imported).

IRISH = ("sga", "mga", "ga", "gd")
WELSH = ("owl", "wlm", "cy")


def key_cy(s: str, loose: bool = False) -> str:
    """Welsh: lowercase, circumflex/acute kept unless loose, no punctuation."""
    s = unicodedata.normalize("NFC", (s or "").lower())
    if loose:
        s = fm._nfd_strip(s)
    return re.sub(r"[^a-zâêîôûŵŷáéíóúýàèìòùẁỳäëïöüẅÿ]", "", s)


for _c, _anc in (("mga", ["sga", "pgl", "cel-pro"]), ("ga", ["mga", "sga", "pgl", "cel-pro"]),
                 ("gd", ["mga", "sga", "pgl", "cel-pro"]), ("owl", ["cel-bry-pro", "cel-pro"]),
                 ("wlm", ["owl", "cel-bry-pro", "cel-pro"]), ("cy", ["wlm", "owl", "cel-bry-pro", "cel-pro"])):
    fm.ANCESTORS.setdefault(_c, _anc)
for _c in ("mga", "ga", "gd"):
    fm.KEYS.setdefault(_c, fm.key_sga)
for _c in WELSH:
    fm.KEYS.setdefault(_c, key_cy)
fm.PROTO_NAMES.setdefault("cel-bry-pro", "Proto-Brythonic")
fm.LANGS.setdefault("mga", fm.LangSpec("mga", "Middle Irish", "kaikki-middleirish/kaikki.org-dictionary-MiddleIrish.jsonl",
                                       ("Middle Irish",), desc_codes=("mga",)))
fm.LANGS.setdefault("ga", fm.LangSpec("ga", "Irish", f"{SPLIT}/irish.jsonl", ("Irish",), desc_codes=("ga",)))
fm.LANGS.setdefault("gd", fm.LangSpec("gd", "Scottish Gaelic", f"{SPLIT}/scottish-gaelic.jsonl",
                                      ("Scottish Gaelic",), desc_codes=("gd",)))
fm.LANGS.setdefault("owl", fm.LangSpec("owl", "Old Welsh", f"{SPLIT}/old-welsh.jsonl", ("Old Welsh",), desc_codes=("owl",)))
fm.LANGS.setdefault("wlm", fm.LangSpec("wlm", "Middle Welsh", "kaikki-middlewelsh/kaikki.org-dictionary-MiddleWelsh.jsonl",
                                       ("Middle Welsh",), desc_codes=("wlm",)))
fm.LANGS.setdefault("cy", fm.LangSpec("cy", "Welsh", f"{SPLIT}/welsh.jsonl", ("Welsh",), desc_codes=("cy",)))

# ---------------------------------------------------------------- tokenizing

_IR_TOKEN = re.compile(r"[^\W\d_]+(?:[-·’'][^\W\d_]+)*", re.U)


def irish_words(text: str) -> list[str]:
    """Word tokens with their internal hyphens / middle dots (a m-Murbulg,
    h-Iarthar, do-rat, duit-siu); punctuation, digits and the Tironian
    sign are dropped."""
    return _IR_TOKEN.findall(unicodedata.normalize("NFC", text or ""))


welsh_words = irish_words

# ---------------------------------------------------------------- Irish mutations and spelling

_V = "aeiouáéíóúāēīōūàèìòùęǽæ"
# emphatic and demonstrative enclitics written with a hyphen (duit-siu, bliadain-sin, é-side)
IR_ENCLITICS = {"si", "siu", "sium", "sea", "se", "sa", "so", "sin", "son", "sem", "sam", "som", "ni", "ne", "nai",
                "nni", "sni", "sib", "sium", "side", "sidhe", "ide", "idhe", "seo", "sean", "siu", "sui", "sun",
                "sí", "sé", "so", "sa", "hí", "hé"}
# a hyphenated first part that is a mutation sign (n-/m-/h-/t- prothesis, eclipsis written apart)
IR_MUT_PREFIX = {"h", "n", "m", "t", "b", "d", "g", "c", "p", "f", "bh", "mb", "nd", "ng", "bp", "dt", "gc", "nn", "ṅ"}
# elided proclitics written with an apostrophe (d'écc = do éc, m'athair, t'ainm, b'é)
IR_ELIDED = ("d", "m", "t", "b", "dh", "th")


def _ir_clean(s: str) -> str:
    s = unicodedata.normalize("NFC", (s or "").lower().replace("’", "").replace("'", ""))
    # e caudata: CELT and the editions use ę for e / é (fęin, tighęrna, inghęn); ǽ æ for ae
    s = s.replace("ę", "e").replace("ǽ", "ae").replace("æ", "ae").replace("ꝫ", "")
    # macron length marks of some editions → acute
    for a, b in (("ā", "á"), ("ē", "é"), ("ī", "í"), ("ō", "ó"), ("ū", "ú")):
        s = s.replace(a, b)
    return s


def irish_demutate(surface: str, normalized: str | None = None) -> list[str]:
    """Candidates for the radical form of an Irish surface form, most likely
    first; the form as written is NOT included. Only clusters that cannot
    begin a radical word (eclipsis mb- nd- ng- bp- dt- gc- bhf-, ts-, the
    written lenitions ḟ ṡ bh mh dh gh fh sh ch th ph) and h-/n-/t- before a
    vowel are stripped; the hyphen, when the edition writes one, decides."""
    raw = unicodedata.normalize("NFC", surface or "").replace("’", "'")
    out: list[str] = []
    m = re.match(r"^([A-Za-z]{1,2})'(.+)$", raw)
    if m and m.group(1).lower() in IR_ELIDED:
        raw = m.group(2)
        out.append(_ir_clean(raw))
    s = _ir_clean(raw)

    def add(x):
        x = x.strip("-·")
        if x and x != s and x not in out:
            out.append(x)
    parts = re.split(r"[-·]", s)
    if len(parts) > 1:
        if parts[0] in IR_MUT_PREFIX:
            add("-".join(parts[1:]))
        if parts[-1] in IR_ENCLITICS:
            add("-".join(parts[:-1]))
            if parts[0] in IR_MUT_PREFIX and len(parts) > 2:
                add("-".join(parts[1:-1]))
    for base in [s] + list(out):
        b = base.replace("-", "").replace("·", "")
        if b.startswith("bhf"):
            add(b[2:])                     # bhf- → f-
        for pre, rad in (("mb", "b"), ("nd", "d"), ("ng", "g"), ("bp", "p"), ("dt", "t"), ("gc", "c"),
                         ("ts", "s")):
            if b.startswith(pre) and len(b) > 3:
                add(rad + b[2:])
        if b[:1] == "ḟ":
            add("f" + b[1:])
        if b[:1] == "ṡ":
            add("s" + b[1:])
        if len(b) > 3 and b[1:2] == "h" and b[0] in "bcdfgmpst":
            add(b[0] + b[2:])              # bh mh dh gh fh sh ch th ph → radical
        if len(b) > 2 and b[0] in "hnt" and b[1] in _V:
            # h- prothesis is safe; n-/t- before a vowel only when the edition marked it (capital or hyphen)
            if b[0] == "h" or (len(raw) > 1 and raw[1].isupper()) or "-" in s[:2]:
                add(b[1:])
    return out


def irish_skeleton(s: str) -> str:
    """Orthographic key on which Middle and Early Modern Irish spellings meet
    Old Irish headwords: no length marks, ae/oe/ao/aoi → ai, ea → e, io → i,
    written lenition of b d g m f s dropped (bh → b …), doubled consonants
    single, post-vocalic c t p → g d b, final -th → -d."""
    s = fm._nfd_strip(_ir_clean(s)).replace("-", "").replace("·", "")
    s = s.replace("ḟ", "f").replace("ṡ", "s")
    s = re.sub(r"[^a-z]", "", s)
    s = s.replace("aoi", "ai").replace("ao", "ai").replace("ae", "ai").replace("oe", "ai")
    s = s.replace("ea", "e").replace("io", "i")
    s = re.sub(r"([bdgmfs])h", r"\1", s)
    s = re.sub(r"(?<=.)nd", "n", s)                # Middle Irish nd / nn (cind = cinn), mb / mm
    s = re.sub(r"(?<=.)mb", "m", s)
    s = re.sub(r"([bcdfglmnprst])\1+", r"\1", s)
    s = re.sub(r"(?<=[aeiou])c(?!h)", "g", s)
    s = re.sub(r"(?<=[aeiou])t(?!h)", "d", s)
    s = re.sub(r"(?<=[aeiou])p(?!h)", "b", s)
    s = re.sub(r"th$", "d", s)
    return s


# Function words (articles, prepositions and their conjugated and article-fused forms, conjunctions,
# particles, pronouns, the copula and the substantive verb). They are not content words: the
# lemmatizer still answers for them, but coverage and the Stage C content-word share leave them out.
# Accent-free keys, Old to Early Modern spellings.
IR_FUNCTION = set("""
ic icc acht act éis eis ēis baoi baoí bui bhaoi bhí bhi arin arind fén bus dáig beidh biaidh
a á ab abhus ac aca acu aga ag agus aici aige aigi ailiu air airi airiu aithle amal amail
amhail an ann and annsin andsin annsein ar ara arna ass asa asin as at ata atá athá atait ataat
ba bá bad bah bái bai baí bat batar be beith beth bi bí bid bo boi boí bói bu
bud buí cach cech cecha gach gacha cia cid cidh cinnas cindas co cu con cona conad conadh conid coro
cosin cosna gusan gusin gusna go gu da dá dar de dhe di dí diar dib díb dibh do dó
doib dóib don dond dun dúin dúinn dúib dúibh duit dhuit dom domh dam damh dhamh dín dind do-sin dano
danó didiu didu é e ea ed eadh ead eat edh eisi eisidhe fa fá fair faire fan far fein
féin fen fodéin fadéin fesin fessin fil fail feil fo for fora forro forsin forsan forsna fri fria
frisin frisna friu fris ga gan gen gin ha he hé hi hí hu i í ia iar iarna iarom
íarom iaram iaramh íaramh iarsin iat iatt id ille im imm imma immon imon imo ime in ina inna ind
int inn isin isind isan isna isnaib is iss ís it la las lasin lasna lais leis le lea leo
léo lesin lim lium linn lib lat leat leam lem ma mad mani manip mar mur mo m mu mé
me mi mise misi mhé na ná nach nacha nad nách nar nár ne né ní ni nir nír nis
nocha noco nocon nogo nó no nu ó o oc ocus occa oca oco ocá ol ón ond onda ra
re ré ri ria ría rem remi ro ros robo roba robai robói rop rob rodbo sa sae sin sind
sinn siat sib sibh se sé si sí sidhe side so sodain son sond sund sunn sunna tall tar tara
tarsin tra trá tre tría tria triana uad uadh uaid uaidh uadha uaithi uaidhib uas úas uile uili uli ule
ura úadaib úaib dan dhó dhi dhíbh dhóibh ainn uainn uaim uaimh liom liomsa leisin chuca chuige chuice cuca cuci
cuice uime uimpe uimpi impe impi uimme
íad iad íat
""".split())    # íad / iad 'they, them' (3pl pronoun; independent check: 235 CELT tokens lemmatized to íadaid 'closes')
# tano / tanaw: preposition tan + 3sg; wc: OCR of English "we" in the facing translation (Owen laws)
CY_FUNCTION = set("""
uc me tra anno rwyf wyf oeddwn ydwyf
a ac ach ae af ai am amdanaw ar arnaw arnei arnunt atat attaw attei attunt y yr yn ym
yg yng o oc odyna oe oed oedd oedynt oet oes oez o6 ouet ef efo e ei eu i
idaw idi udunt ydaw ydiw ydyw ydynt ydyn yw ynt ys yssyd ysydd sydd mae mai ny nyt nid na
nas nat nac neu no nor neut nyd pan gan can gant kan kant yrwng rwng wrth wrthaw gyt gyd
hyt hyd hyny hynny hwnn hwnnw hon honno hono hyn hynn yna yno yma dy vy fy uy y6 mi
ti ni chwi wy wynt wyntwy ynteu hi hwy hwyntwy efe ual val mal megys mor mwy pei pe kyn
cyn kyt cyt tra tros dros rac rhag wedy gwedy wedi gwedi heb hep is uch uwch yngkylch dan adan
namyn onyt onid oni yny ynny ynn ryw rw ry yd yt ydd bu bo bot bod bydd bei byddai
bydei bit bwyf oll holl pob pawb pa pwy py pyt beth yo ydau a6 yssit ysit ydys oedit oedyt

tano tanaw wc""".split())


def is_function_word(surface: str, lang: str = "sga") -> bool:
    """Function words by surface (lowercase, length marks kept so that bó
    'cow' and bo 'was', rí 'king' and ri 'to' stay apart; a hyphenated
    mutation sign or enclitic is stripped first): IR_FUNCTION / CY_FUNCTION."""
    if lang == "sga":
        if fm.key_sga(_ir_clean(surface)) in IR_FUNCTION:
            return True
        return ("-" in surface or "'" in surface) and any(fm.key_sga(x) in IR_FUNCTION for x in irish_demutate(surface))
    return key_cy(welsh_norm(surface)) in CY_FUNCTION


# ---------------------------------------------------------------- Welsh mutations and spelling

_WV = "aeiouwyâêîôûŵŷ"


def welsh_norm(s: str, diplomatic: bool = False) -> str:
    """Lowercase NFC, k → c. diplomatic=True also repairs the OCR of the
    diplomatic editions (Evans, Rhŷs & Evans): insular w read as O / 6 inside
    a word, long r read as z / 2."""
    s = unicodedata.normalize("NFC", s or "")
    if diplomatic:
        s = re.sub(r"(?<=[a-z])[O6]", "w", s)
        s = re.sub(r"(?<=[a-zA-Z])[z2]|[z2](?=[a-z])", "r", s)
    return s.lower().replace("k", "c").replace("’", "").replace("'", "")


def welsh_demutate(surface: str, normalized: str | None = None) -> list[str]:
    """Radical candidates for a Welsh form (soft, nasal, aspirate mutation,
    h-prothesis), the form itself not included. Middle Welsh writes the soft
    mutation of b/m as u/v/f and of d as d, so f/u/v- give b- and m-."""
    s = (normalized if normalized is not None else welsh_norm(surface)).replace("-", "")
    out: list[str] = []

    def add(x):
        if x and x != s and x not in out:
            out.append(x)
    if s.startswith("ngh"):
        add("c" + s[3:])
    elif s.startswith("mh"):
        add("p" + s[2:])
    elif s.startswith("nh"):
        add("t" + s[2:])
    elif s.startswith("ng"):
        add("g" + s[2:])
    if s.startswith("ph"):
        add("p" + s[2:])
    if s.startswith("th"):
        add("t" + s[2:])
    if s.startswith("ch"):
        add("c" + s[2:])
    if s.startswith("dd"):
        add("d" + s[2:])
    if s[:1] in "fuv" and len(s) > 2 and not s.startswith("ff"):
        add("b" + s[1:])
        add("m" + s[1:])
    if s[:1] == "b":
        add("p" + s[1:])
    if s[:1] == "d" and not s.startswith("dd"):
        add("t" + s[1:])
    if s[:1] == "g" and not s.startswith("ng"):
        add("c" + s[1:])
    if s[:1] == "l" and not s.startswith("ll"):
        add("ll" + s[1:])
    if s[:1] == "r" and not s.startswith("rh"):
        add("rh" + s[1:])
    if s[:1] == "m":
        add("b" + s[1:])
    if s[:1] == "n" and not s.startswith("ng"):
        add("d" + s[1:])
    if s[:1] == "h" and s[1:2] in _WV:
        add(s[1:])
    if s[:1] in _WV:
        add("g" + s)                       # soft mutation of g- is its loss
    return out


def welsh_skeleton(s: str) -> str:
    """Key on which Middle Welsh spellings meet the dictionaries: no accents,
    k → c, v / u before a vowel → f, dd → d, doubled letters single, final
    t c p → d g b (MW tat, tec = tad, teg), i/y and w/u kept apart."""
    s = fm._nfd_strip(welsh_norm(s)).replace("-", "")
    s = re.sub(r"[^a-z]", "", s)
    s = s.replace("v", "f")
    s = re.sub(r"(?<=[aeioy])u(?=[aeioy])", "f", s)
    s = s.replace("dd", "d")
    s = re.sub(r"([bcdfglmnprst])\1+", r"\1", s)
    s = re.sub(r"(?<=[aeiouwy])t$", "d", s)
    s = re.sub(r"(?<=[aeiouwy])c$", "g", s)
    s = re.sub(r"(?<=[aeiouwy])p$", "b", s)
    return s


# ---------------------------------------------------------------- gloss corpora (lemmatized Old Irish)

WURZBURG = "raw/daughters/oldirish-wurzburg-doyle/glosses.json"
UD_FULL = "raw/daughters/oldirish-ud-full-20261023"
CRITMITB = "raw/daughters/middleirish-ud-critmitb-dev/mga_critmitb-ud-test.conllu"
UPOS = {"NOUN": "noun", "PROPN": "name", "ADJ": "adj", "VERB": "verb", "AUX": "verb-aux", "ADV": "adv",
        "ADP": "prep", "PRON": "pron", "DET": "det", "PART": "particle", "SCONJ": "conj", "CCONJ": "conj",
        "NUM": "num", "INTJ": "intj"}
CONTENT_UPOS = ("NOUN", "VERB", "ADJ", "PROPN")


@dataclass
class GlossTok:
    source: str        # wb | sg | wb-ud | mga-ud
    unit: str          # gloss / sentence id
    form: str
    lemma: str         # '' for untagged Würzburg tokens
    upos: str          # '' when untagged; '<Latin>' etc. for Latin


def wurzburg_tokens(root: Path = ROOT) -> list[GlossTok]:
    """Würzburg glosses (Doyle, CC BY 4.0): every Irish token; tagged ones
    carry UD POS and lemma, the rest (about 60%) only their form. Latin and
    Greek tokens are dropped: those tagged as such, and in untagged glosses
    any word that occurs as a tagged Latin token anywhere in the corpus (the
    untagged text marks Latin only by italics, not always), plus editorial
    sigla (sup., rl.)."""
    data = json.loads((Path(root) / WURZBURG).read_text("utf-8"))
    latin = {"sup", "rl", "et", "est", "per", "in", "non", "deo", "dei", "hic", "híc", "id", "ut", "quia", "cum", "ad",
             "eius", "sed", "uel", "uel", "autem", "enim", "ergo", "quod", "qui", "quae", "ab", "de", "ex", "pro"} - {"in"}
    for ep in data:
        for fo in ep["folios"]:
            for gl in fo["glosses"]:
                for form, pos, lem, _ in gl.get("glossTokens") or []:
                    if pos.startswith("<Latin") or pos == "<Greek>":
                        latin.add(form.lower())
    latin.discard("in")
    latin.discard("a")
    out = []
    for ep in data:
        for fo in ep["folios"]:
            for gl in fo["glosses"]:
                unit = f"Wb {fo['folio'].replace('f. ', '')}{gl['glossNo']}"
                toks = gl.get("glossTokens")
                if toks:
                    for form, pos, lem, _ in toks:
                        if (pos.startswith("<") and pos != "<unknown>") or pos == "PUNCT":
                            continue
                        if pos == "<unknown>":
                            for w in irish_words(form):
                                if w.lower() not in latin:
                                    out.append(GlossTok("wb", unit, w, "", ""))
                        else:
                            out.append(GlossTok("wb", unit, form, lem, pos))
                else:
                    text = re.sub(r"<em>.*?</em>", " ", gl.get("glossText") or "")
                    text = re.sub(r"<[^>]+>", " ", text)
                    for w in irish_words(text):
                        if w.lower() not in latin:
                            out.append(GlossTok("wb", unit, w, "", ""))
    return out


def conllu_tokens(path: Path, source: str) -> list[GlossTok]:
    out, sent = [], None
    for line in Path(path).read_text("utf-8").splitlines():
        if line.startswith("# sent_id"):
            sent = line.split("=", 1)[-1].strip()
        elif line and not line.startswith("#"):
            c = line.split("\t")
            if len(c) < 10 or "-" in c[0] or c[3] in ("PUNCT", "X", "SYM"):
                continue
            out.append(GlossTok(source, f"{source} {sent}", c[1], c[2] if c[2] not in ("_",) else "", c[3]))
    return out


def gloss_tokens(root: Path = ROOT) -> list[GlossTok]:
    """The sga-glosses corpus: Würzburg (Doyle JSON; the UD DipWBG files are
    a subset of the same glosses and are not added) and St Gall (UD DipSGG,
    incomplete + test)."""
    root = Path(root)
    toks = wurzburg_tokens(root)
    for f in ("DipSGG/incomplete.conllu", "DipSGG/sga_dipsgg-ud-test.conllu"):
        toks += conllu_tokens(root / UD_FULL / f, "sg")
    return toks


def gloss_pairs(root: Path = ROOT) -> list[tuple[str, str, str]]:
    """(form, lemma, UPOS) from every lemmatized Old/Middle Irish token (Wb,
    Sg, DipWBG, CritMITB) for the forms table."""
    root = Path(root)
    toks = [t for t in gloss_tokens(root) if t.lemma]
    for f in ("DipWBG/incomplete.conllu", "DipWBG/sga_dipwbg-ud-test.conllu"):
        toks += [t for t in conllu_tokens(root / UD_FULL / f, "wb-ud") if t.lemma]
    toks += [t for t in conllu_tokens(root / CRITMITB, "mga-ud") if t.lemma]
    return [(t.form, t.lemma, t.upos) for t in toks]


# ---------------------------------------------------------------- Matasović, EDPC (Proto-Celtic headwords)
#
# OCR text (raw/books/text/matasovic-pcelt/pNNNN.txt). Field labels as OCR'd:
# "GOlD:/GOID:" (Goidelic), "W:", "PIE:". Headword lines start with '*'.
# Only headword, the Goidelic/Welsh forms and the PIE line are read; the OCR
# loses length marks and garbles laryngeals (*bhehz- = *bʰeh₂-).

MATASOVIC = "raw/books/text/matasovic-pcelt"
_MAT_HEAD = re.compile(r"^\*([^\s'‘]+)")
_MAT_LOAN = re.compile(r"loan|borrow|Lehn|non-IE|substrat", re.I)


def _mat_is_loan(etym: str) -> bool:
    """A loan / substrate remark about the Celtic word itself, not about a neighbour borrowing it
    (*rūnā: 'the Germanic words … could be early loanwords from Celtic')."""
    return any(not re.match(r"[a-z]*\s+(?:from|in(?:to)?)\s+(?:Celtic|Gaul|Goidelic|Irish|Brit|Welsh|PCelt)",
                            etym[m.end():m.end() + 40], re.I)
               for m in _MAT_LOAN.finditer(etym))


_MAT_LABEL = re.compile(r"^([A-Za-z0-9 ]{1,7}):\s*(.*)$")
_MAT_FIELDS = {"GOID", "GOIDE", "W", "PIE", "ETYM", "BRET", "CO", "GAUL", "COGN", "REF", "SEE", "CELTIB", "LEP",
               "PICT", "OIR", "MIR"}
_MAT_OPENERS = {"GOID", "GOIDE", "W", "PIE", "BRET", "CO", "GAUL", "CELTIB", "LEP"}


def _mat_is_head(lines: list[str], i: int) -> bool:
    """A '*' line opens an entry only when it carries a category tag ('[Noun]', '[Vb]') or one of the
    next three lines is one or a form/PIE field label (*bowd-ro- / 'dirty' / [Adj]): in the ETYM text OCR often breaks a line before a starred
    form (p0265 *luxtu-: '... deriving these Celtic words from PIE / *lewg- 'break' / is not convincing'),
    which used to start a bogus entry and cut the real one's ETYM short."""
    if "[" in lines[i]:
        return True
    for nxt in lines[i + 1:i + 4]:
        if nxt.startswith("*"):
            return False
        if nxt.startswith("["):
            return True
        lab = _MAT_LABEL.match(nxt)
        if lab and lab.group(1).replace("0", "O").replace("l", "I").upper().replace(" ", "") in _MAT_OPENERS:
            return True
    return False


def matasovic_entries(root: Path = ROOT) -> list[dict]:
    out, cur, field = [], None, None
    files = sorted((Path(root) / MATASOVIC).glob("p*.txt"))
    lines: list[tuple[str, str]] = []
    for fn in files:
        for line in fn.read_text("utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                lines.append((fn.stem, line))
    text = [x for _, x in lines]
    for i, (page, line) in enumerate(lines):
        m = _MAT_HEAD.match(line)
        if m and not re.match(r"^\*[A-Z]", line) and _mat_is_head(text, i):
            g = re.search(r"['‘]([^'’]{2,60})['’]", " ".join(text[i:i + 3]))
            cur = {"head": "*" + m.group(1).strip(",.;"), "page": page, "goid": "", "w": "", "pie": "",
                   "etym": "", "gloss": g.group(1) if g else ""}
            out.append(cur)
            field = None
            continue
        if cur is None:
            continue
        lab = _MAT_LABEL.match(line)
        if lab:
            L = lab.group(1).replace("0", "O").replace("l", "I").upper().replace(" ", "")
            if L in _MAT_FIELDS:
                field = {"GOID": "goid", "GOIDE": "goid", "W": "w", "PIE": "pie", "ETYM": "etym"}.get(L)
                if field:
                    cur[field] += " " + lab.group(2)
                continue
        if field:
            cur[field] += " " + line
    return out


def _mat_forms(text: str, prefixes: tuple) -> list[str]:
    """'OIr. bés [u m], MIr. banb, banbán' → ['bés', 'banb', 'banbán'] for the
    given language abbreviations (OCR variants 0Ir / Olr / OIr, a missing
    space after the dot)."""
    out = []
    pat = r"(?<![A-Za-z])(?:" + "|".join(prefixes) + r")(?:\.\s*|\s+)"
    for m in re.finditer(pat + r"([^\[\(;]*)", text):
        seg = re.split(pat, m.group(1))[0]
        for w in seg.split(","):
            w = w.strip().split(" ")[0].strip(".-:*'‘’")
            if w and re.fullmatch(r"[^\W\d_]+(?:-[^\W\d_]+)?", w):
                out.append(w)
    return out


GOID_PREFIX = ("OIr", "0Ir", "Olr", "OIr", "MIr", "Mlr", "EIr", "Elr", "Ir")
W_PREFIX = ("MW", "OW", "W")


def mat_pie_key(s: str) -> str:
    """Matasović OCR PIE → fm.pie_fuzzy_key space: z/, after h → laryngeal 2/1."""
    s = (s or "").strip()
    s = re.sub(r"h[z2]", "h2", s)
    s = re.sub(r"h[,1l](?=[a-z\-]|$)", "h1", s)
    s = re.sub(r"h[J3]", "h3", s)
    s = s.replace("_", "-")
    return s


# ---------------------------------------------------------------- building the mappings

# an etymology that the entry itself calls unknown or speculative is not used (round-0 sample:
# druimm "Unclear. Pokorny tentatively…", tol "Unknown…", daear "Further etymology is unknown; Morris Jones…")
_HEDGE = re.compile(r"^\s*(?:unknown|unclear|uncertain|obscure|of (?:unknown|uncertain|unclear|disputed|obscure)"
                    r" origin)|further (?:etymology|origins?)[^.]{0,40}?(?:unknown|unclear|uncertain|obscure)"
                    r"|of (?:uncertain|unknown|unclear|obscure) (?:etymology|origin|derivation)"
                    r"|not been accepted|tenuous|folk[- ]etymolog|tentatively|according to stokes|macbain"
                    r"|morris jones", re.I)


def _entries(lang: str, root: Path) -> list[fm.Entry]:
    """kaikki entries of one Celtic stage, with two rejections the generic
    parser leaves open: an entry with a source outside the language's
    ancestry (fm 'disputed': Irish uair < Latin hōra beside a PIE link) and
    an entry whose etymology text calls its own etymology unknown or
    speculative (_HEDGE)."""
    spec = fm.LANGS[lang]
    dumps = [spec.dump] if isinstance(spec.dump, str) else list(spec.dump)
    codes = set(spec.desc_codes or (lang,))
    out = []
    for path in dumps:
        with open(Path(root) / KD / path, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                if d.get("lang_code") not in codes:
                    continue
                e = fm.parse_entry(d, lang, True)
                if e.disputed and not e.rejected:
                    e.rejected = "foreign source beside inherited link: " + e.disputed
                et = d.get("etymology_text") or ""
                if not e.rejected and _HEDGE.search(et):
                    e.rejected = "etymology marked unknown/speculative"
                out.append(e)
    return out


# Suppletive paradigms: a form-table or form-of form from another stem must not inherit the lemma's
# etymology (round-0 sample: bá, bia, bís → at·tá *steh₂-; rug → beirid; do·rochair → do·tuit;
# ad·cuaid → ad·fét; Welsh goreu → da). Patterns are searched in the accent-free key of the form.
SUPPLETIVE = {
    "sga": {
        "attá": r"^(?:ro|ra|ní|ni|na|nad|nach|co|con|ma|ce|dia|ara|in|im|ar|ro)?[bfḟ]",
        "is": r"^(?:ro|ra|ní|ni|na|nad|nach|co|con|ma|ce|dia|in|ar)?b",
        "beirid": r"ruc|rug|ructh|rucs|uic|ucc|ucs|ruuc",
        "beir": r"ruc|rug|ructh|rucs|uic|ucc|ucs|ruuc",
        "dobeir": r"rat|rad|tart|tuc|tug|tuuc|ruc|rug|uic",
        "tabair": r"rat|tuc|tug",
        "téit": r"luid|lod|lot|reg|rach|dul|dol|lluid",
        "dotét": r"luid|lod|lot|reg|rach|dul|dol",
        "tét": r"luid|lod|lot|reg|rach",
        "dotuit": r"rochair|rochr|rocair|rocha|rocra|rchair|rchar|rchr",
        "tuit": r"rochair|rochr|rchair",
        "adfét": r"cuaid|cuad|chuaid|chuad|cuid",
        "adcí": r"cond|conn|acca|accae|acae|faca|facc",
        "atchí": r"cond|conn|acca|faca",
        "ithid": r"duaid|duad",
        "téigh": r"chuaid|chuadh|dul|rach|ragh|luid",
        "maith": r"^ferr|^fearr|^dech|^dag",
    },
    "cy": {
        "da": r"gor|gwell|well|gwaeth",
        "drwg": r"gwaeth|waeth|gwaethaf",
        "bot": r"^(?:ny|nyt|ni|nid|na|nat|pan|a|y|yd|yr)?(?:o|y|m|e|s|w)",
        "bod": r"^(?:ny|nyt|ni|nid|na|nat|pan|a|y|yd|yr)?(?:o|y|m|e|s|w)",
        "mynet": r"aeth|aet|euth|^el|^a$|^af|^ae",
        "mynd": r"aeth|aet|euth|^el|^a$|^af|^ae",
        "myned": r"aeth|aet|euth|^el|^a$|^af|^ae",
        "gwneuthur": r"^gor|oruc|orug|wnaeth|naeth",
        "dyuot": r"^daw|^deu|^doe|^deuth|^doeth|^del|^dau",
        "dyfod": r"^daw|^deu|^doe|^deuth|^doeth|^del|^dau",
    },
}


# Two verbs in one kaikki table: the inflection table of sga do·ucai 'understands' (*h₁ewk-, EDPC p0417
# *u-n-k-o-) also lists the forms of do·uccai 'brings' (·tuc, ·tucus, ·tuctar, ·tucsat …), the
# preterite / subjunctive stem of do·beir, causative of do·icc (kaikki sga do·uic; EDPC p0042 *ank-o-,
# *h₂neḱ-). Non-palatal ·tuc(c)- forms go to the lemma 'douccai', which takes do·icc's mapping; the
# palatal ·tuic(c)i / ·tucci forms stay with 'understand'. (lemma, form pattern on the accent-free key,
# new lemma, lemma whose mapping it takes, path note)
STEM_SPLITS = {
    "sga": [("doucai", r"^th?uc{1,2}(?=$|[aousftm])", "douccai", "doicc", "sga:douic (do·uccai 'brings')")],
}


def _stem_splits(lm: fm.LangMapping, splits: list) -> dict:
    """Move the matching forms of a lemma to a new lemma (STEM_SPLITS); returns {new lemma: [forms]}."""
    K = fm.KEYS[lm.lang]
    moved: dict[str, list] = {}
    for lem, pat, new, src, note in splits:
        rx = re.compile(pat)
        lk, nk = K(lem), K(new)
        for f in list(lm.forms):
            c = lm.forms[f]
            if lk in c and rx.search(K(f, True)):
                c[nk] += c.pop(lk)
                moved.setdefault(nk, []).append(f)
        r = lm.recs.get(K(src))
        if r and moved.get(nk):
            lm.recs[nk] = fm.MapRec(nk, new, r.ids, (f"{lm.lang}:{new}", note) + r.path, "stem-split",
                                    "medium", r.sources + ("stem-split",), r.gloss)
            lm.lemma_words.add(nk)
    return moved


def _formof_word(r: fm.MapRec) -> str | None:
    for p in r.path:
        if p.startswith("form-of:"):
            return p[len("form-of:"):]
    return None


def _suppletive(lm: fm.LangMapping, table: dict):
    """Drop form-table links and form-of mappings from another stem of a
    suppletive lemma (SUPPLETIVE)."""
    K = fm.KEYS[lm.lang]
    pats = {K(k): re.compile(v) for k, v in table.items()}
    for f in list(lm.forms):
        c = lm.forms[f]
        for lk in [x for x in c if x in pats]:
            if f != lk and pats[lk].search(K(f, True)):
                del c[lk]
        if not c:
            del lm.forms[f]
    for k in list(lm.recs):
        w = _formof_word(lm.recs[k])
        if w and K(w) in pats and k != K(w) and pats[K(w)].search(K(k, True)):
            del lm.recs[k]


def _formof_conflicts(lm: fm.LangMapping, entries: list[fm.Entry], gmap: dict, lang: str):
    """A key that the dictionary knows only as an inflected form (Middle Welsh
    bu 'was', a form of bot) keeps no mapping that came from elsewhere (bu in
    the descendants of Proto-Celtic *bāus 'cow') unless both agree."""
    K = fm.KEYS[lang]
    lemma_keys = {k for e in entries if not e.form_of for k in fm.entry_keys(e, lang)}
    grp = lambda r: frozenset(gmap.get(x, x) for x in r.ids)
    for e in entries:
        if not e.form_of:
            continue
        for k in fm.entry_keys(e, lang):
            r = lm.recs.get(k)
            if k in lemma_keys or not r or _formof_word(r):
                continue
            lem = [lm.recs.get(K(w)) for w in e.form_of]
            lem = [x for x in lem if x]
            if not lem or any(grp(x) != grp(r) for x in lem):
                del lm.recs[k]


def _via_daughter(lm: fm.LangMapping, entries: list[fm.Entry], earlier: dict, lang: str):
    """chain-<code>: an entry whose etymology names an earlier stage of the
    language (Middle Irish → Old Irish) takes that word's mapping."""
    K = fm.KEYS[lang]
    for e in entries:
        if e.rejected or e.form_of:
            continue
        keys = fm.entry_keys(e, lang)
        if all(k in lm.recs for k in keys):
            continue
        hit = None
        for code, term, _ in e.links:
            if code in earlier:
                r = earlier[code].recs.get(fm.KEYS[code](term))
                if r:
                    hit = (code, term, r)
                    break
        if not hit:
            continue
        code, term, r = hit
        for k in keys:
            if k not in lm.recs:
                lm.recs[k] = fm.MapRec(k, e.word, r.ids, (f"{lang}:{e.word}", f"{code}:{term}") + r.path[1:],
                                       f"chain-{code}", "medium" if r.confidence == "high" else "low",
                                       r.sources + (f"via-{code}",), r.gloss or e.glosses)
    lm.rejected = {k: v for k, v in lm.rejected.items() if k not in lm.recs}


def _from_later(lm: fm.LangMapping, later: list[tuple[str, list[fm.Entry], fm.Resolver]], lang: str):
    """later-<code>: an earlier-stage headword (Old Irish X) with no mapping
    takes the proto-language chain of a later entry that cites X as its
    source (Irish fírinne ← OIr. fírinne; Welsh gŵr ← MW gwr ← *wiros)."""
    K = fm.KEYS[lang]
    cand: dict[str, list] = collections.defaultdict(list)
    for code, ents, res in later:
        for e in ents:
            if e.rejected or e.form_of:
                continue
            src = [t for c, t, _ in e.links if c == lang]
            if len(src) != 1:
                continue
            k = K(src[0])
            if not k or k in lm.recs or k in lm.rejected:
                continue
            h = res.entry_hit(e, code)          # proto links only (daughter codes do not resolve)
            if h and h.specific:
                cand[k].append((code, e.word, src[0], h))
    for k, lst in cand.items():
        groups = {x[3].ids for x in lst}
        if len(groups) > 1:
            continue                            # later entries disagree
        code, w, src, h = lst[0]
        lm.recs[k] = fm.MapRec(k, src, h.ids, (f"{lang}:{src}", f"{code}:{w}") + h.path, f"later-{code}",
                               "medium" if h.how == "chain" else "low", ("later-entry",))


def _merge(lang: str, parts: list[fm.LangMapping], gmap: dict) -> fm.LangMapping:
    """One mapping for the stages of a language (Old > Middle > Modern).
    For a key mapped in several stages: a mapping inherited by a mere
    inflected form (form-of) yields to a headword's own mapping (OIr. bia
    'will be' vs Ir. bia 'food'); if the remaining stages disagree on the
    root group, the earliest stage keeps the key only when its mapping is the
    word's own etymology chain, else the key is left unmapped."""
    out = fm.LangMapping(lang)
    by_key: dict[str, list] = collections.defaultdict(list)
    for lm in parts:
        for k, r in lm.recs.items():
            by_key[k].append(r)
        for k, v in lm.rejected.items():
            out.rejected.setdefault(k, v)
        for f, c in lm.forms.items():
            out.forms[f].update(c)
        out.lemma_words |= lm.lemma_words
        for k, p in lm.pos.items():
            out.pos[k] |= p
    grp = lambda r: frozenset(gmap.get(x, x) for x in r.ids)
    for k, rs in by_key.items():
        own = [r for r in rs if not _formof_word(r)] or rs
        if len({grp(r) for r in own}) == 1:
            out.recs[k] = own[0]
        elif own[0].how in ("chain", "lexicon") and not _formof_word(own[0]):
            out.recs[k] = own[0]
    out.rejected = {k: v for k, v in out.rejected.items() if k not in out.recs}
    return out


_GLOSS_STOP = set("to the a an of and or in on with be being from for as by at into one that which this its his her "
                  "their something someone person thing make become cause up out off down".split())


def _gloss_words(text: str) -> set:
    return {w[:4] for w in re.findall(r"[a-z]+", (text or "").lower()) if w not in _GLOSS_STOP and len(w) > 2}


def _disambiguate_roots(lm: fm.LangMapping, lex: list[dict], gloss_of):
    """A mapping to two or more homograph lexicon roots of one form (*wel-
    'see' / 'turn' / 'enclose'; *h₂ey- 'vital force' / 'give' / 'day') keeps
    the root(s) whose meaning shares a word with the glosses along the
    word's path (kaikki daughter and proto-language senses); with no overlap
    all are kept."""
    form = {e["id"]: e["form"] for e in lex}
    kind = {e["id"]: e.get("kind") for e in lex}
    mean = {e["id"]: " ".join(e.get("meaning") or []) for e in lex}
    for k, r in list(lm.recs.items()):
        roots = [i for i in r.ids if kind.get(i) == "root"]
        if len(roots) < 2 or len({form[i] for i in roots}) == len(roots):
            continue
        g = _gloss_words(" ".join([r.gloss] + [gloss_of(p) for p in r.path]))
        if not g:
            continue
        score = {i: len(g & _gloss_words(mean[i])) for i in roots}
        best = max(score.values())
        if best == 0:
            continue
        keep = frozenset(i for i in r.ids if i not in roots or score[i] == best)
        if keep != r.ids:
            lm.recs[k] = fm.MapRec(r.key, r.word, keep, r.path, r.how, r.confidence, r.sources + ("gloss-disambiguated",),
                                   r.gloss)


@dataclass
class CelticMappings:
    irish: fm.LangMapping       # key_sga keys; sga > mga > ga
    welsh: fm.LangMapping       # key_cy keys; owl > wlm > cy
    parts: dict                 # per-stage LangMappings
    lexicon: list
    precedence: dict = None     # matasovic_precedence log: {lang: {key: (old ids, new ids | None, EDPC page:head)}}


def apply_base_overrides(recs: dict, corpus: str, overrides: dict) -> dict:
    """Resolve corpus decisions inherited through base paths, nearest base first.

    Use the shared resolver for decisions; an explicit decision on the derived
    key takes priority. Keep this corpus-specific because Irish tables share a
    language mapping but can have different reviewed decisions.
    """
    out = dict(recs)
    for key, rec in recs.items():
        bases = [p.split(":", 1)[1] for p in rec.path if p.startswith("base:")]
        if not bases:
            continue
        lang = rec.path[0].split(":", 1)[0] if rec.path else None
        ids, decisions = mp.decide_row(corpus, key, rec.ids, rec.path, lang, overrides)
        if not decisions:
            for base in bases:
                ids, decisions = mp.decide(corpus, base, rec.ids, overrides)
                if decisions:
                    break
        if not decisions:
            continue
        if not ids:
            out.pop(key, None)
        else:
            out[key] = fm.MapRec(key, rec.word, ids, rec.path, "erratum",
                                 "low" if any(d.uncertain for d in decisions) else "high",
                                 rec.sources + ("mapping-overrides",), rec.gloss)
    return out


def build_mappings(root: Path = ROOT, lexicon: list[dict] | None = None, matasovic: bool = True) -> CelticMappings:
    root = Path(root)
    lex = lexicon or [json.loads(l) for l in (root / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines() if l]
    idx = fs.PieIndex(lex)
    kinds = {e["id"]: e.get("kind") for e in lex}
    protos = fm.ProtoDB(root, codes={"cel-pro", "cel-bry-pro"}, want_desc=IRISH + WELSH)
    res = fm.Resolver(idx, protos, kinds, True)
    ents = {c: _entries(c, root) for c in IRISH + WELSH}
    parts = {}
    for c in IRISH + WELSH:
        parts[c] = fm.build_lang_mapping(c, lex, protos, root=root, entries=ents[c], idx=idx)
    _via_daughter(parts["mga"], ents["mga"], {"sga": parts["sga"]}, "mga")
    for c in ("ga", "gd"):
        _via_daughter(parts[c], ents[c], {"mga": parts["mga"], "sga": parts["sga"]}, c)
    _via_daughter(parts["wlm"], ents["wlm"], {"owl": parts["owl"]}, "wlm")
    _via_daughter(parts["cy"], ents["cy"], {"wlm": parts["wlm"], "owl": parts["owl"]}, "cy")
    _from_later(parts["sga"], [(c, ents[c], res) for c in ("mga", "ga", "gd")], "sga")
    _from_later(parts["mga"], [(c, ents[c], res) for c in ("ga", "gd")], "mga")
    _from_later(parts["owl"], [(c, ents[c], res) for c in ("wlm", "cy")], "owl")
    _from_later(parts["wlm"], [("cy", ents["cy"], res)], "wlm")
    gmap = fs.group_map(lex)
    for c in IRISH + WELSH:
        _formof_conflicts(parts[c], ents[c], gmap, c)
    irish = _merge("sga", [parts[c] for c in ("sga", "mga", "ga")], gmap)
    welsh = _merge("cy", [parts[c] for c in ("owl", "wlm", "cy")], gmap)
    # Scottish Gaelic only lends etymologies (later-gd); its forms and headwords are not Irish
    upos_of: dict[str, set] = collections.defaultdict(set)
    for form, lem, upos in gloss_pairs(root):
        fk, lk = fm.key_sga(form), fm.key_sga(lem)
        if not fk or not lk:
            continue
        irish.forms[fk][lk] += 1
        irish.forms[fm.key_sga(form, True)][lk] += 1
        upos_of[lk].add(UPOS.get(upos, upos.lower()))
        irish.lemma_words.add(lk)
    for lk, ps in upos_of.items():          # gloss POS only for lemmas the dictionaries do not classify
        if not irish.pos.get(lk):
            irish.pos[lk] |= ps
    _suppletive(irish, SUPPLETIVE["sga"])
    _suppletive(welsh, SUPPLETIVE["cy"])
    split_log = _stem_splits(irish, STEM_SPLITS["sga"])
    glosses: dict[str, str] = collections.defaultdict(str)
    for c in IRISH + WELSH:
        for e in ents[c]:
            if e.glosses:
                glosses[f"{c}:{e.word}"] += " " + e.glosses
    for (code, _), es in protos.entries.items():
        for e in es:
            if e.glosses:
                glosses[f"{code}:{e.word}"] += " " + e.glosses
    gloss_of = lambda p: glosses.get(p, "") or glosses.get(p.replace(":*", ":"), "") or glosses.get(
        p.split(":", 1)[0] + ":*" + p.split(":", 1)[-1], "")
    for lm in (irish, welsh):
        _disambiguate_roots(lm, lex, gloss_of)
    precedence: dict = {}
    if matasovic:
        add_matasovic(irish, welsh, lex, root)
        precedence = matasovic_precedence(irish, welsh, lex, gmap, gloss_of, root)
    precedence["preverb-only"] = {lm.lang: drop_preverb_only(lm, lex) for lm in (irish, welsh)}
    precedence["stem-split"] = split_log
    return CelticMappings(irish, welsh, parts, lex, precedence)


def add_matasovic(irish: fm.LangMapping, welsh: fm.LangMapping, lex: list[dict], root: Path = ROOT):
    """EDPC headword → its Goidelic and Welsh forms (unique accent-free key
    on both sides) → its PIE line (FuzzyPie, whole form only). Loanword
    entries and entries without a PIE line are skipped. Only keys the
    kaikki steps left unmapped get a row (how 'matasovic', confidence low)."""
    fz = fm.FuzzyPie(lex)
    mean = {e["id"]: " ".join(e.get("meaning") or []) for e in lex}
    ents = matasovic_entries(root)
    for lm, fields, prefixes, K in ((irish, "goid", GOID_PREFIX, fm.key_sga), (welsh, "w", W_PREFIX, key_cy)):
        loose: dict[str, set] = collections.defaultdict(set)
        for k in set(lm.lemma_words) | set(lm.recs):
            loose[K(k, True)].add(k)
        by_key: dict[str, list] = collections.defaultdict(list)
        for e in ents:
            if not e["pie"] or _mat_is_loan(e["etym"]):
                continue
            for w in _mat_forms(e[fields], prefixes):
                k = K(w, True)
                if len(k) >= 3:
                    by_key[k].append(e)
        for k, es in by_key.items():
            if len({id(x) for x in es}) != 1:
                continue
            words = loose.get(k, set())
            if len(words) != 1:
                continue                              # the accent-free key must name one headword
            w = next(iter(words))
            if w in lm.recs:
                continue
            e = es[0]
            pies = [p.strip(" ?.;,") for p in re.split(r"[,;]| or ", e["pie"]) if p.strip().startswith("*")]
            ids = set()
            for p in pies:
                p = mat_pie_key(p.split(" ")[0].split("'")[0].split("‘")[0])
                ids, how = fz.lookup(p)
                if ids and how == "form":
                    break
                ids = set()
            if not ids or len(ids) > 3:
                continue
            # the PIE line's own gloss ('lead', 'call') must fit the lexicon meaning of the id(s) FuzzyPie found:
            # OCR-flattened forms collide with homographs (*gel- 'call' → *gel- 'be cold')
            gm = re.search(r"['‘]([^'’]{2,40})['’]", e["pie"])
            if gm:
                gw = _gloss_words(gm.group(1))
                score = {i: len(gw & _gloss_words(mean.get(i, ""))) for i in ids}
                if gw and max(score.values()) == 0:
                    continue
                if gw:
                    ids = {i for i in ids if score[i] == max(score.values())}
            lm.recs[w] = fm.MapRec(w, w, frozenset(ids), (f"{lm.lang}:{w}", f"matasovic:{e['page']}:{e['head']}",
                                                         f"ine-pro:{pies[0] if pies else ''}"),
                                   "matasovic", "low", ("matasovic",))


# Matasović's EDPC takes precedence over the kaikki/Wiktionary chain where both speak to a headword
# (independent check, docs/research/mapping-precision-celtic-independent.md: lucht, caill, bran, aimser, cruind,
# meth, toísech, Welsh caer, daly, gof, da were Wiktionary/IEW etymologies that EDPC rejects or calls unknown).
# statements about the word's own etymology only; loan remarks are left out, since EDPC often says a
# cognate or a neighbour's word was borrowed (*drungo-: Lat. drungus 'is a loanword from' Celtic)
_MAT_REJECT = re.compile(
    r"(?:IE|PIE) etymology (?:is|remains) (?:unknown|lacking|uncertain|obscure|unclear)"
    r"|(?:its|the) etymology is (?:unknown|uncertain|obscure|unclear)|convincing (?:IE |PIE )?etymology is lacking"
    r"|no (?:convincing |plausible |certain |good |generally accepted )?(?:IE |PIE )?etymology"
    r"|is not convincing|unconvincing|appears improbable|non-IE|onomatopo|will not do|of unknown origin"
    r"|origin is unknown", re.I)
_MAT_ARROW = re.compile(r"<\s*PIE\s+(\*[^\s,;)'‘]+)")


def _mat_verdict(e: dict, fz, mean: dict):
    """One EDPC entry → ('ids', frozenset) when its PIE line (or a '< PIE *x' derivation in ETYM) resolves
    to lexicon ids (whole form or its leading segments; the PIE gloss must fit), ('reject', reason) when it
    gives no PIE etymon and its ETYM calls the etymology unknown, non-IE, onomatopoeic or a loan, else None."""
    pie = e["pie"].strip()
    if re.search(r"this (?:etymology|derivation|connection) is (?:quite |rather |very )?(?:uncertain|doubtful|dubious)"
                 r"|semantics of this derivation are (?:somewhat )?stretched", e["etym"], re.I):
        return None                            # EDPC doubts its own PIE line (*nesso-, *lugri): not decisive
    if not pie:
        m = _MAT_ARROW.search(e["etym"])
        if m:
            pie = m.group(1)
        else:
            m = _MAT_REJECT.search(e["etym"])
            return ("reject", m.group(0)) if m else None
    pies = [x.strip(" ?.;,") for x in re.split(r"[,;]| or |\+", pie) if x.strip().startswith("*")]
    for x in pies:
        ids, how = fz.lookup(mat_pie_key(x.split(" ")[0].split("'")[0].split("‘")[0]))
        if not ids or how != "form" or len(ids) > 4:
            continue                           # whole form only: *h1en-h3kw- must not resolve to *h₁én
        gm = re.search(r"['‘]([^'’]{2,40})['’]", pie)
        if gm:
            gw = _gloss_words(gm.group(1))
            score = {i: len(gw & _gloss_words(mean.get(i, ""))) for i in ids}
            if gw and max(score.values()) == 0:
                return None                    # the gloss fits no id (OCR-flattened homograph): not decisive
            if gw:
                ids = {i for i in ids if score[i] == max(score.values())}
        return ("ids", frozenset(ids))
    return None


def matasovic_precedence(irish: fm.LangMapping, welsh: fm.LangMapping, lex: list[dict], gmap: dict,
                         gloss_of=lambda p: "", root: Path = ROOT) -> dict:
    """Where an EDPC entry speaks to a mapped headword (its Goidelic / Welsh form, accent-free key naming
    exactly one mapped headword; the same join as `add_matasovic`), EDPC wins:

      * EDPC gives no PIE etymon and calls the etymology unknown, non-IE or a loan → the key is unmapped
        (lucht, caill, bran, aimser, cruind, meth; W caer, daly);
      * EDPC's PIE etymon shares no root group with the kaikki ids → EDPC's ids replace them
        (brisid/bres *bʰreyH- → *bʰres-; rann *h₂rey- → *perh₃-; toísech *wedʰ- → *weyd-);
      * EDPC's etymon is among the ids → ids that are homographs of it (same lexicon form, other root)
        are dropped (*h₂ews- 'draw water' / 'become light').

    A key with several EDPC entries is changed only when all of them agree (all reject, or all name the
    same root group). Returns {lang: {key: (old ids, new ids or None, page:head)}} for the report."""
    fz = fm.FuzzyPie(lex)
    mean = {e["id"]: " ".join(e.get("meaning") or []) for e in lex}
    form = {e["id"]: e.get("form") for e in lex}
    grp = lambda ids: frozenset(gmap.get(x, x) for x in ids)
    ents = matasovic_entries(root)
    log: dict = {}
    for lm, field, prefixes, K in ((irish, "goid", GOID_PREFIX, fm.key_sga), (welsh, "w", W_PREFIX, key_cy)):
        loose: dict[str, set] = collections.defaultdict(set)
        for k in lm.recs:
            loose[K(k, True)].add(k)
        by_key: dict[str, dict] = collections.defaultdict(dict)
        for e in ents:
            # the entry's first Goidelic / Welsh form only: later ones are often derivatives or OCR run-ons
            # from other fields (*luxsman- 'loimm, lucht'; *yalo- … 'act')
            for w in _mat_forms(e[field], prefixes)[:1]:
                k = K(w, True)
                if len(k) >= 3:
                    by_key[k][id(e)] = e
        out = log.setdefault(lm.lang, {})
        for k, es in by_key.items():
            words = loose.get(k, set())
            if len(words) != 1:
                continue
            w = next(iter(words))
            r = lm.recs[w]
            if r.how == "matasovic":
                continue
            # the EDPC headword must be the same word: its gloss shares a word with the kaikki senses
            # (OIr. athar 'of a father' is not *futro-; Welsh bod 'to be' is not *butā 'dwelling')
            kg = _gloss_words(" ".join([r.gloss or ""] + [gloss_of(p) for p in r.path]))
            if not any(kg & _gloss_words(e["gloss"]) for e in es.values()):
                continue
            vs = [(_mat_verdict(e, fz, mean), e) for e in es.values()]
            vs = [(v, e) for v, e in vs if v]
            if not vs or len(vs) != len(es):
                continue                                   # an entry without a verdict: EDPC is not decisive
            where = ";".join(f"{e['page']}:{e['head']}" for _, e in vs)
            if all(v[0] == "reject" for v, _ in vs):
                del lm.recs[w]
                lm.rejected[w] = "matasovic: " + vs[0][0][1] + f" ({where})"
                out[w] = (sorted(r.ids), None, where + " «" + vs[0][0][1] + "»")
                continue
            if any(v[0] != "ids" for v, _ in vs) or len({grp(v[1]) for v, _ in vs}) != 1:
                continue
            new = frozenset().union(*(v[1] for v, _ in vs))
            if not grp(new) & grp(r.ids):
                ids = new
            else:
                keepforms = {form.get(i) for i in r.ids if gmap.get(i, i) in grp(new)}
                ids = frozenset(i for i in r.ids if gmap.get(i, i) in grp(new) or form.get(i) not in keepforms)
            if ids != r.ids:
                lm.recs[w] = fm.MapRec(r.key, r.word, ids, r.path + (f"matasovic:{where}",), "matasovic-precedence",
                                       "low" if r.confidence == "low" else "medium", r.sources + ("matasovic",),
                                       r.gloss)
                out[w] = (sorted(r.ids), sorted(ids), where)
        # the same decision for keys that inherit the changed word's mapping along a chain
        # (Irish taoiseach ← toísech, coill ← caill; Welsh trachwant ← chwant)
        src = {}
        for w, (old, new, where) in list(out.items()):
            for p0 in {f"{c}:{w}" for c in (IRISH if lm.lang == "sga" else WELSH)}:
                src[p0] = (w, old, new, where)
        for k, r in list(lm.recs.items()):
            if k in out:
                continue
            hit = next((src[p] for p in r.path[1:] if p in src), None)
            if not hit or sorted(r.ids) != hit[1]:
                continue
            w, old, new, where = hit
            if new is None:
                del lm.recs[k]
                lm.rejected[k] = f"matasovic via {w} ({where})"
            else:
                lm.recs[k] = fm.MapRec(r.key, r.word, frozenset(new), r.path + (f"matasovic:{where}",),
                                       "matasovic-precedence", r.confidence, r.sources + ("matasovic",), r.gloss)
            out[k] = (old, new, f"via {w}")
    return log


def drop_preverb_only(lm: fm.LangMapping, lex: list[dict]) -> list[str]:
    """A content headword (noun, verb, adjective, name) whose only ids are PIE adverbs / preverbs (*de, *ḱóm,
    *h₁épi, *péri) through a prefix keeps nothing of its lexical root (Cymru → *kom- → *ḱóm, Irish íadaid →
    *h₁épi): unmapped. Returns the keys dropped."""
    adv = {e["id"] for e in lex if e.get("kind") == "word" and e.get("pos") == "adv"}
    K = fm.KEYS[lm.lang]
    proto_of = lambda r: [x for x in r.path if x.startswith(("cel-pro:", "cel-bry-pro:"))]
    # spellings of a headword that keeps its adverb etymon through a Proto-Celtic word (uasal ~ úasal)
    kept = {K(k, True) for k, r in lm.recs.items() if r.ids and r.ids <= adv and proto_of(r)
            and not proto_of(r)[0].rstrip().endswith("-")}
    dropped = []
    for k, r in list(lm.recs.items()):
        if not (r.ids and r.ids <= adv and lm.pos.get(k, set()) & {"noun", "verb", "adj", "name"}):
            continue
        if K(k, True) in kept:
            continue
        # a word derived from the adverb itself keeps it (úasal, MW uchel < *ouxselos < *upo): only a chain
        # that reaches the adverb through a bare prefix (*kom-, *exs-) or with no Proto-Celtic word at all has
        # lost the lexical root
        proto = [x for x in r.path if x.startswith(("cel-pro:", "cel-bry-pro:"))]
        if not proto or proto[0].rstrip().endswith("-"):
            del lm.recs[k]
            lm.rejected[k] = "preverb-only mapping"
            dropped.append(k)
    return dropped


# ---------------------------------------------------------------- lemmatizer

class CelticLemmatizer:
    """Surface → lemma key string (fm.FormLemmatizer conventions: 'a|b' for
    up to `max_lemmas` candidates, '?' + loose key when unknown).

    Order: the form as written (exact key, accent-free key), then each
    mutation-stripped candidate (same two keys), then the orthographic
    skeleton of all of them, used only when it names at most `max_lemmas`
    lemmas. Preverb compounds and infixed pronouns are not split."""

    def __init__(self, lm: fm.LangMapping, demutate, skeleton, norm=None, max_lemmas: int = 3,
                 form_overrides: dict | None = None, use_skeleton: bool = True):
        """use_skeleton=False drops the last, least precise level (Irish: 3 C / 5 W of the 11
        skeleton-level items in the final sample; docs/research/mapping-precision-celtic.md)."""
        self.use_skeleton = use_skeleton
        self.lm, self.K = lm, fm.KEYS[lm.lang]
        self.demutate, self.skeleton, self.norm, self.max = demutate, skeleton, norm or _ir_clean, max_lemmas
        self.form_overrides = form_overrides if form_overrides is not None else \
            fm.load_overrides()["form"].get(lm.lang, {})
        self.skel: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        heads = set(lm.lemma_words) | set(lm.recs)
        for f, c in lm.forms.items():
            sk = skeleton(f)
            if sk:
                self.skel[sk].update({x: 1 for x in c})
        for h in heads:
            sk = skeleton(h)
            if sk:
                self.skel[sk][h] += 1
        self.heads = heads
        self.cache: dict[str, str] = {}
        self.level: dict[str, str] = {}

    def _table(self, k: str) -> str | None:
        """Every lemma whose count is at least a third of the best one's, the
        headword itself included: a form that is a headword and also a
        frequent form of another lemma (MW benn 'cart' / soft mutation of
        penn 'head'; Ir. cur 'hero' / verbal noun of cuirid) gives 'a|b', which
        multi-lemma mapping leaves unmapped when the etyma differ."""
        c = self.lm.forms.get(k)
        if c:
            top = max(c.values())
            keep = sorted((x for x in c if 3 * c[x] >= top), key=lambda x: (-c[x], x != k, x))
            return "|".join(keep[: self.max])
        if k in self.heads:
            return k
        return None

    def __call__(self, surface: str) -> str:
        if surface in self.cache:
            return self.cache[surface]
        r, lvl = self._lemmatize(surface)
        self.cache[surface], self.level[surface] = r, lvl
        return r

    def _lemmatize(self, surface: str) -> tuple[str, str]:
        s = self.norm(surface)
        dm = self.demutate(surface, s)
        cands = dm if ("'" in surface or "’" in surface) and dm else [s] + dm
        if self.form_overrides:
            for c in cands:
                if self.K(c) in self.form_overrides:
                    return self.form_overrides[self.K(c)], "override"
        for i, c in enumerate(cands):
            for loose in (False, True):
                k = self.K(c, loose)
                if len(k) < 1:
                    continue
                r = self._table(k)
                if r:
                    return r, ("form" if i == 0 else "demutated") + ("-loose" if loose else "")
        for c in (cands if self.use_skeleton else ()):
            sk = self.skeleton(c)
            if len(sk) < 3:
                continue
            got = self.skel.get(sk)
            if got and len(got) <= self.max:
                return "|".join(sorted(got, key=lambda x: (-got[x], x))), "skeleton"
        return "?" + self.K(s, True), "unknown"


# Forms whose reading depends on the word before them (independent check: tig is the dat. of tech
# 'house' after a preposition or article in 415 of its 925 CELT tokens, and 'comes' (·tic of do·icc)
# mostly elsewhere). Without such a word the form keeps its ambiguous union (form override 'tech|doicc'),
# which the tables leave unmapped. key → [(preceding words, lemma)]; first match wins.
_IR_HOUSE_PREV = frozenset("""isin issin isind asin asind i hi h-i ina dia día da dá don dond din ón on ic oc is""".split())
CONTEXT_FORMS = {
    "sga": {
        "tig": [(_IR_HOUSE_PREV, "tech")],
        "thig": [(_IR_HOUSE_PREV, "tech"), (frozenset("ní ni má ma mar".split()), "doicc")],
    },
}


# Reviewed Irish homographs and names: error-verdicts-irish.jsonl supplies the
# independent source loci and dictionary citations for every IR-CS identifier.
# Rules use immediate lexical context, never passage IDs. Missing neighbours
# do not match; capitalization alone is insufficient without a reviewed name.
# (previous word sequences, following forms, corrected lemma/sense, requires capital)
IR_REVIEWED_CONTEXT = {
    'adaig': [
        (('mbai',), ('and',), 'adaig@night', False),  # IR-CS-065
    ],
    'adaigh': [
        (('an',), ('sin',), 'adaig@night', False),  # IR-CS-079, IR-CS-080
    ],
    'agaib': [
        (('cúich',), ('dingbhus',), 'ag', False),  # IR-CS-113
    ],
    'aidchi': [
        (('teora',), ('ac',), 'adaig@night', False),  # IR-CS-063
    ],
    'aide': [
        (('mo',), ('i',), 'aite', False),  # IR-CS-044
    ],
    'aingil': [
        (('bennachadur',), ('dé',), 'aingel@angel', False),  # IR-CS-117
        (('tainic',), ('do',), 'aingel@angel', False),  # IR-CS-173
    ],
    'airc': [
        (('isin',), ('ruc',), 'arc@ark', False),  # IR-CS-034
        (('isin',), ('oiret',), 'arc@ark', False),  # IR-CS-034
    ],
    'asna': [
        (('fesin',), ('srothaibh',), 'as', False),  # IR-CS-054
        (('iar',), ('losaib-sin',), 'as', False),  # IR-CS-055, IR-CS-160
    ],
    'bas': [
        (('sin',), ('chommairge',), 'is', False),  # IR-CS-031
    ],
    'ben': [
        (('badesta',), ('a',), 'benaid', False),  # IR-CS-038
    ],
    'bether': [
        (('ní',), ('co',), 'bí', False),  # IR-CS-060
    ],
    'bhai': [
        (('ro',), ('mac',), 'bí', False),  # IR-CS-016
    ],
    'bheithi': [
        (('fedh',), ('a',), 'bí', False),  # IR-CS-030
    ],
    'bhir': [
        (('do',), ('chruaidh',), 'bir', False),  # IR-CS-066
        (('don',), ('isin',), 'bir', False),  # IR-CS-068
    ],
    'bhud': [
        (('nach',), ('marbh',), 'bud', False),  # IR-CS-104
    ],
    'bhó': [
        (('gur',), ('fliuch',), 'bo', False),  # IR-CS-017, IR-CS-159
    ],
    'biadh': [
        (('nach',), ('ainm',), 'bí', False),  # IR-CS-077
    ],
    'bias': [
        (('cidh',), ('damh',), 'bí', False),  # IR-CS-058
    ],
    'boinn': [
        (('co',), ('combai',), 'boand (name)', False),  # IR-CS-151
    ],
    'brcith': [
        (('dot',), (), 'breith', False),  # IR-CS-168
    ],
    'broind': [
        (('ósa',), ('brúis',), 'brú@belly', False),  # IR-CS-157
    ],
    'bás': [
        (('ní',), ('remi',), 'bí', False),  # IR-CS-032
    ],
    'bía': [
        (('ní',), ('fáitsine',), 'bí', False),  # IR-CS-059
    ],
    'bíad': [
        (('no',), ('a chend',), 'bí', False),  # W2-044: conditional with a chend
        (('no',), ('congal',), 'bí', False),  # IR-CS-105
        (('no',), ('for',), 'bí', False),  # IR-CS-106
        (('no',), ('fora',), 'bí', False),  # IR-CS-106
    ],
    'bíd': [
        (('gacha',), (), 'bíad', False),  # IR-CS-069
    ],
    'caera': [
        (('sumha',), ('mil',), 'cáer@berry', False),  # IR-CS-048
    ],
    'cas': [
        ((), (), 'cas (name)', True),  # IR-CS-098
    ],
    'chlaid': [
        (('fâcbur a',), (), 'claideb', False),  # IR-CS-147: truncated at the unit boundary
    ],
    'chlíu': [
        (('bara',), (), 'clé', False),  # IR-CS-056
    ],
    'chomla': [
        (('in',), ('sin',), 'comla', False),  # IR-CS-123
    ],
    'chuain': [
        (('an',), ('do',), 'cúan@harbour', False),  # IR-CS-081
    ],
    'cháera': [
        (('immar',), ('tenda',), 'cáer@berry', False),  # IR-CS-049
    ],
    'collaib': [
        (('dá',), (), 'colainn', False),  # IR-CS-088
    ],
    'comla': [
        (('dorsaide in',), ('la',), 'comla', False),  # W2-065
        (('tiprait',), ('furri',), 'comla', False),  # IR-CS-124
    ],
    'cuala': [
        (('gu',), ('in',), 'rocluinethar', False),  # IR-CS-091
    ],
    'cáilte': [
        ((), (), 'caílte (name)', True),  # IR-CS-166
    ],
    'damhsa': [
        (('briathar',), ('ol',), 'do', False),  # IR-CS-052
    ],
    'deógan': [
        ((), (), 'eógan (name)', True),  # IR-CS-092
    ],
    'dfionn': [
        ((), (), 'fionn (name)', True),  # IR-CS-128
    ],
    'dhuin': [
        (('ferr',), ('a',), 'do', False),  # IR-CS-015
    ],
    'dobo': [
        ((), ('córa',), 'bo', False),  # IR-CS-089
        (('n-érinn',), ('mó',), 'bo', False),  # IR-CS-090
    ],
    'dáed': [
        ((), (), 'áed (name)', True),  # IR-CS-045
    ],
    'dána': [
        (('co',), ('dúrcraidech',), 'dána@bold', False),  # IR-CS-116
    ],
    'día': [
        (('buille',), ('ghlúin',), 'dia', False),  # IR-CS-028
    ],
    'días': [
        (('n-amus',), ('cach',), 'dias@pair', False),  # IR-CS-006
        (('acht',), ('ro',), 'dias@pair', False),  # IR-CS-007
        (('an',), ('daltadh',), 'dias@pair', False),  # IR-CS-008
    ],
    'eitir': [
        ((), ('ṡrotha',), 'eter', False),  # IR-CS-133
    ],
    'eogan': [
        ((), (), 'eógan (name)', True),  # IR-CS-094
    ],
    'eó': [
        ((), ('uma',), 'eó@pin', False),  # IR-CS-033
    ],
    'fele': [
        (('fos',), ('toa',), 'féile@modesty', False),  # IR-CS-122
    ],
    'fer': [
        (('ega',), ('or',), 'fér', False),  # IR-CS-014
    ],
    'fiacha': [
        ((), (), 'fiacha (name)', True),  # IR-CS-180
    ],
    'file': [
        (('é',), ('sund',), 'fil', False),  # IR-CS-102
        (('céin',), ('in',), 'fil', False),  # IR-CS-102
    ],
    'filed': [
        (('h-aisia',), ('araon',), 'fil', False),  # IR-CS-114
    ],
    'find': [
        (('lia',), ('lia',), 'find@white', False),  # IR-CS-083
    ],
    'fir': [
        (('as',), ('don',), 'fír', False),  # IR-CS-012
        (('deiligud',), ('gai',), 'fír', False),  # IR-CS-013
    ],
    'fáe': [
        (('chlé',), ('ri',), 'fo', False),  # IR-CS-009
    ],
    'gaet': [
        (('màthair',), ('in',), 'gonaid', False),  # IR-CS-167
    ],
    'gai': [
        (('fir',), ('and',), 'gáu', False),  # IR-CS-078
    ],
    'gairit': [
        (('bo',), ('linn',), 'gairid@short', False),  # IR-CS-111
    ],
    'ghaibh': [
        (('do',), ('coirrbreaca',), 'gae', False),  # IR-CS-041
    ],
    'gonadh': [
        (('chuir',), ('ann',), 'conid', False),  # IR-CS-129
    ],
    'grain': [
        (('gab',), ('eacla',), 'gráin@fear', False),  # IR-CS-084
    ],
    'gráin': [
        (('gabus',), ('egla',), 'gráin@fear', False),  # IR-CS-085
        (('gan',), ('ré',), 'gráin@fear', False),  # IR-CS-086
    ],
    'h-aidchi-so': [
        (('na',), ('di',), 'adaig@night', False),  # IR-CS-062
    ],
    'h-alpain': [
        ((), (), 'alba (name)', True),  # IR-CS-022
    ],
    'h-erenà': [
        ((), (), 'ériu (name)', True),  # IR-CS-131
    ],
    'h-eógan': [
        ((), (), 'eógan (name)', True),  # IR-CS-093
    ],
    'herind': [
        ((), (), 'ériu (name)', True),  # IR-CS-132
    ],
    'hingnib': [
        (('cosaib',), ('doib',), 'ingen@nail', False),  # IR-CS-042
    ],
    'husci': [
        (('fri',), ('andes',), 'uisce', False),  # IR-CS-171
    ],
    'ior': [
        (('lethchind',), ('icthchlocind',), 'for', False),  # IR-CS-146, IR-CS-176
        (('icthchlocind',), ('cnàinired',), 'for', False),  # IR-CS-146, IR-CS-176
    ],
    'iṅgni': [
        (('bertsatar',), ('na',), 'ingen@nail', False),  # IR-CS-043
    ],
    'lasan': [
        (('duibi',), ('sruth',), 'la', False),  # IR-CS-051
    ],
    'leiginn': [
        (('mac',), ('dia',), 'légend@learning', False),  # IR-CS-130
    ],
    'lind': [
        (('assu',), ('óenláech',), 'la', False),  # IR-CS-004
        (('fein',), ('gura',), 'la', False),  # IR-CS-005
    ],
    'lotair': [
        (('léo',), ('îor',), 'luid', False),  # IR-CS-169
    ],
    'lotar': [
        ((), ('na',), 'luid', False),  # IR-CS-001
    ],
    'lía': [
        (('a',), ('ro',), 'lia@stone', False),  # IR-CS-097
    ],
    'm-bíd': [
        (('m-bec',), ('sin',), 'bíad', False),  # IR-CS-067
    ],
    'maid': [
        (('ro',), ('cnómaidm',), 'maidid', False),  # IR-CS-020
    ],
    'mbo': [
        (('co',), ('marb',), 'bo', False),  # IR-CS-018
    ],
    'messi': [
        ((), ('tarlaic',), 'mé', False),  # IR-CS-027
    ],
    'messu': [
        (('ba',), ('lais-sium',), 'messu@worse', False),  # IR-CS-026
    ],
    'mina': [
        ((), ('bhedh',), 'mani', False),  # IR-CS-099
    ],
    'mun': [
        ((), ('budh',), 'mani', False),  # IR-CS-110
    ],
    'méd': [
        (('caithemh',), ('na',), 'méid', False),  # IR-CS-070
        (('ar',), ('menman',), 'méid', False),  # IR-CS-071
    ],
    'mín': [
        (('riamh',), ('bud',), 'mani', False),  # IR-CS-103
    ],
    'n-adaig': [
        (('i',), ('ríg',), 'agaid', False),  # IR-CS-064
    ],
    'n-airc': [
        (('gach',), ('gach',), 'airc@distress', False),  # IR-CS-100
    ],
    'n-alpain': [
        ((), (), 'alba (name)', True),  # IR-CS-023
    ],
    'n-domnall': [
        ((), (), 'domnall (name)', True),  # IR-CS-096
    ],
    'n-eistecht': [
        (('á',), ('adubairt',), 'éistecht@hearing', False),  # IR-CS-076
    ],
    'n-uird': [
        (('a',), ('a',), 'ord@office', False),  # IR-CS-073, IR-CS-074
    ],
    'nalpain': [
        ((), (), 'alba (name)', True),  # IR-CS-021
    ],
    'no-mbligtis': [
        (('chluined',), ('da',), 'mligid', False),  # IR-CS-149, IR-CS-175
    ],
    'nís': [
        (('úadib',), ('arlaic',), 'ní', False),  # IR-CS-019
        (('súas',), ('arlaic',), 'ní', False),  # IR-CS-019
    ],
    'nít': [
        (('aile',), ('fírlaech',), 'ní', False),  # IR-CS-047
    ],
    'oss': [
        (('lia',), ('a',), 'ós', False),  # IR-CS-119, IR-CS-162
        (('oghaim',), ('a',), 'ós', False),  # IR-CS-120, IR-CS-161
    ],
    'rena': [
        (('claidbib',), ('carpdib',), 'ria', False),  # IR-CS-024, IR-CS-155
    ],
    'rioghacht': [
        (('ar',), ('do',), 'ríge', False),  # IR-CS-057
    ],
    'shaltair': [
        (('a',), ('forsin',), 'saltair@psalter', False),  # IR-CS-087
    ],
    'smera': [
        (('fuarus',), ('imdha',), 'smér', False),  # IR-CS-029
    ],
    'suil': [
        (('sin',), ('dech',), 'suil@before', False),  # IR-CS-011
    ],
    't-art': [
        (('in',), ('amnas',), 'art', False),  # IR-CS-050
    ],
    't-ech': [
        (('in',), ('bocóidech',), 'ech', False),  # IR-CS-109
    ],
    't-echt': [
        (('in',), ('dosom',), 'écht', False),  # IR-CS-179
    ],
    'thes': [
        (('na',), (), 'tes@south', False),  # IR-CS-036
        (('lendchaime',), ('ro',), 'tes@south', False),  # IR-CS-165
    ],
    'tibridis': [
        (('cona',), ('usce',), 'dobeir@give-present', False),  # IR-CS-172
    ],
    'áed': [
        ((), (), 'áed (name)', True),  # IR-CS-046
    ],
    'áilli': [
        (('rempu',), ('do',), 'álaind', False),  # IR-CS-101
    ],
    'áith': [
        (('neimhnech',), ('uillend-glas',), 'áith@sharp', False),  # IR-CS-107
        (('claidim',), ('urnocht',), 'áith@sharp', False),  # IR-CS-108
    ],
    'ás': [
        (('scíath',), ('gúallib',), 'ós', False),  # IR-CS-040
    ],
    'éistecht': [
        (('tagra',), ('re',), 'éistecht@hearing', False),  # IR-CS-075
    ],
    'îor': [
        (('lotair',), ('muir',), 'for', False),  # IR-CS-170
    ],
    'óengus': [
        ((), (), 'óengus (name)', True),  # IR-CS-095
    ],
    'órda': [
        (('slabrad',), ('claidim',), 'órda@golden', False),  # IR-CS-072
    ],
    'úathu': [
        (('gaíthe',), ('chuccu',), 'ó', False),  # IR-CS-003
    ],
    'ḟálti': [
        (('ind',), ('sin',), 'fáilte', False),  # IR-CS-010
    ],
    'ṅdiad': [
        ((), (), 'diad (name)', True),  # IR-CS-039
    ],
    'ṅgabail': [
        (('in',), ('bífed',), 'gabul', False),  # IR-CS-002
    ],
}

# Wave-2 source and dictionary evidence: error-verdicts-w2-celtic.jsonl.
IR_REVIEWED_CONTEXT.update({
    'hlechta': [(('trian',), (), 'mlicht', False)],
    'fóirithin': [(('furtacht',), ('orum',), 'foirithin@help', False)],
    'tliúath': [(('toing mo',), ('or',), 'túath', False)],
    'cléib': [(('for-fholumh a',), ('co',), 'clíab', False)],
    'coin': [(('erne',), ('hingenaib',), 'cona', False)],
    'mben': [(('co',), ('dí',), 'benaid', False)],
    'tóchta': [(('dechmaid in',), ('co',), 'tócht@piece', False)],
})

# Wave-3 source and dictionary evidence: error-verdicts-w3-celtic.jsonl.
# Keep homographs outside these independently checked lexical contexts.
IR_REVIEWED_CONTEXT.update({
    'annocht': [(('rogenair',), (), 'innocht', False)],
    'sir': [(('ro',), ('immoro',), 'síraid', False)],
    't-ochtur': [(('in',), ('ar xx oclach',), 'ochtar', False)],
    'ṡétaib': [(('tairces do',), ('dó',), 'sét@treasure', False)],
    'imshnímaib': [(('dia',), ('móra',), 'imshním', False)],
    'h-aithli': [(('bodéin asa',), (), 'aithle@afterwards', False)],
    'légud': [(('ingen do',), ('úad',), 'léicid', False)],
})
IR_REVIEWED_CONTEXT['bíad'].append((('ná',), ('commus',), 'bí', False))


# Wave-4 source and dictionary evidence: error-verdicts-w4-celtic.jsonl.
for _form, _rules in {'daig': [(('fo',), ('tathar',), 'dáig@because', False)],
 'lind': [(('fochen',), ('do',), 'la', False)],
 'fochen': [((), ('lind do',), 'fochen@welcome', False)],
 'aodh': [(('^',), ('mend',), 'aodh (name)', True)],
 'chriad': [(('coirp',), (), 'cré@clay', False)],
 'aidche': [(('lathi',), ('and',), 'adaig@night', False)],
 'theigh': [(('ro',), ('ro folaig',), 'teichid', False)],
 'thes': [(('na rígh',), ('ar',), 'tess@south', False)],
 'airc': [(('is',), ('dúnn',), 'airc@need', False)],
 'cuan': [(('in',), ('lan do longaib',), 'cúan@harbour', False)],
 'fäid': [((), ('iter na faidib',), 'fáith', False)],
 'h-ögaib': [(('ög iter na',), ('apstal',), 'óg@virgin', False)],
 'or': [(('lem',), ('si-si',), 'ol', False)],
 'orgain': [(('do',), ('in sidiu',), 'orgain@slaying', False)],
 'ndéni': [(('co',), ('íar',), 'déne@speed', False)],
 'forecmaing': [((), ('sin scíath',), 'doecmaing', False)],
 'broind': [(('ósa',), ('coro',), 'brú@belly', False)],
 'nádaim': [(('síl',), ('do',), 'ádam (name)', True)],
 'uig': [(('don',), ('ucut',), 'og@egg', False)],
 'gé': [(('acht',), ('atá',), 'gé@although', False)],
 't-tarladar': [(('go',), ('for dhuirteach',), 'tarla@happen', False)]}.items():
    IR_REVIEWED_CONTEXT.setdefault(_form, []).extend(_rules)


# Wave-5 independent source/dictionary review: error-verdicts-w5-celtic.jsonl.
for _form, _rules in {'aigid': [(('a',), ('forro',), 'agad@face', False)],
 'airg': [(('ra',), ('dún sobairchi',), 'orcaid', False)],
 'alta': [(('dáig',), ('in mac',), 'ailid', False)],
 'bee': [(('ba',), ('id',), 'bec', False)],
 'bhas': [(('mar',), ('maith',), 'bí', False)],
 'caclia': [(('dech',), ('gäese',), 'cach', False)],
 'decli': [(('trebaire',), ('áilclie',), 'dech', False)],
 'dhun': [(('faitsine',), ('forfindam',), 'do', False)],
 'dáigh': [(('fo',), ('meic dé',), 'dáig@because', False)],
 'fata': [(('claideb',), ('sithlaí',), 'fota', False)],
 'fichi': [(('^',), ('rlg',), 'fiche', False)],
 'file': [(('thigi',), ('isind',), 'fil', False)],
 'fir': [(('imba',), (), 'fír', False)],
 'féch': [(('ro',), ('úadha',), 'fégaid', False)],
 'ge': [(('^',), ('bo flaitli',), 'gé@although', False)],
 'gona': [(('talmain',), ('thorthaibh',), 'cona', False)],
 'gráin': [(('tardad',), ('na',), 'gráin@fear', False)],
 'gái': [(('ceiledh',), ('fair',), 'gáu', False)],
 'gé': [(('acht',), ('ro loitis',), 'gé@although', False),
        (('^',), ('romgonais',), 'gé@although', False)],
 'h-eriu': [(('m-buí',), ('h-i',), 'ériu (name)', True)],
 'inathar': [(('maicc',), (), 'athair', False)],
 'lis': [(('isind',), (), 'les', False)],
 'maigi': [(('sechnón in',), ('dochuaid',), 'mag', False)],
 'nocht': [(('a',), ('febh',), 'innocht', False)],
 'oss': [(('n-anmond',), ('aird',), 'ós', False)],
 'rigi': [(('ngabail',), ('dó',), 'ríge', False)],
 'sen': [(('iad',), ('robo',), 'sin', False)],
 'tessed': [(('na',), ('isan cath',), 'téit@secondary', False)],
 'torcaib': [((), ('idna catha',), 'túargabim@raise', False)]}.items():
    IR_REVIEWED_CONTEXT.setdefault(_form, []).extend(_rules)


# Wave-6 independent source/dictionary review: error-verdicts-w6-celtic.jsonl.
# Narrow contexts preserve the milk verb, rock noun and other homographs.
for _form, _rules in {
    'crúim': [(('dá',), ('and',), 'cruim', False)],
    't-ech': [(('an',), ('gu cenn',), 'ech', False)],
    'áilli': [(('neoil',), ('aen-gela',), 'álaind', False)],
    'thúaithi': [(('rí mo',), ('do-ratusa',), 'túath', False)],
    'abhull': [((), ('fo bláth', 'abaigh'), 'aball', False)],
    'abull': [((), ('ac tuitim',), 'aball', False)],
    'oengus': [(('^',), ('find',), 'óengus (name)', True)],
    'do-ratusa': [(('thúaithi',), ('dúibsi',), 'dorat', False)],
    'toig': [(('dia',), ('indisid',), 'tech', False)],
    'días': [((), ('ban',), 'dias@pair', False)],
    'mbrec': [(('iasc',), ('for',), 'brecc', False)],
    'aengus': [(('^',), ('aainm',), 'aengus (name)', True)],
}.items():
    IR_REVIEWED_CONTEXT.setdefault(_form, []).extend(_rules)


# Wave-7 independent source/dictionary review: error-verdicts-w7-celtic.jsonl.
# Contexts keep unrelated homographs and prefixed names separate.
for _form, _rules in {
    'ḟind': [(('bláth',), ('ina',), 'find@white', False)],
    'élúd': [(('imma-ricfa',), ('dó',), 'élúd@escape', False)],
    't-áes': [(('in',), ('cumachta', 'trebaire'), 'áes', False)],
    'thenid': [(('do',), ('sinnaig',), 'tene', False)],
    'usci': [(('esca',), ('aer',), 'uisce', False)],
    'adaig': [(('id',), ('muir',), 'adaig@night', False)],
    'lir': [(('bid', 'bit'), ('bomand ega',), 'il', False)],
    'muir': [(('adaig',), ('tir',), 'muir', False)],
    'aer': [(('usci',), ('id',), 'aer@air', False)],
    'h-erind': [(('saer-chlanna', 'daer-tuathaib'), (), 'ériu (name)', True)],
    'haine': [(('co',), ('co hairigi',), 'áine (name)', True)],
    'gus': [(('riut',), ('aniu',), 'co', False)],
    'gusa': [(('fhleid',), ('m-bertha',), 'co', False)],
    'lotar': [(('ocus',), ('i m-breith',), 'luid', False)],
    'craide': [(('bris a',), ('ina cliab',), 'cride', False)],
    't-shlegh': [(('in',), ('ina h-ucht',), 'sleg', False)],
    'rus': [(('ni',), ('leic',), 'ro', False)],
    'cor': [(('h-ucht',), ('bris',), 'co', False)],
    'aill': [(('o', 'ó'), ('do aill',), 'aill', False),
             (('do',), ('ocom',), 'aill', False)],
}.items():
    IR_REVIEWED_CONTEXT.setdefault(_form, []).extend(_rules)


# Wave-8 source/dictionary evidence: error-verdicts-w8-celtic.jsonl.
# The preposition-plus-possessive forms retain the preposition's function status.
for _form, _rules in {
    'foda': [(('fothlocht fann',), ('for a lár',), 'fota', False)],
    'rena': [(('sé féin',), ('fáistine',), 'fri', False)],
    'áidchi': [(('láe nó',), ('ar in ríg',), 'adaig@night', False)],
    'ret': [(('nó',), ('buimme', 't aiti'), 'fri', False)],
}.items():
    IR_REVIEWED_CONTEXT.setdefault(_form, []).extend(_rules)


def lemmatize_words(lemz: "CelticLemmatizer", words: list[str]) -> list[str]:
    """Lemmas for a word sequence: `lemz(w)` for each word, except that a form in CONTEXT_FORMS takes the
    lemma its preceding word selects (tig after isin / i / ina / dia … → tech 'house'). Stage C should use
    this rather than calling the lemmatizer word by word."""
    rules = CONTEXT_FORMS.get(lemz.lm.lang, {})
    out = []
    normalized = [_ir_clean(w) for w in words] if lemz.lm.lang == "sga" else []
    for i, w in enumerate(words):
        lem = lemz(w)
        for prev, target in rules.get(w.lower(), ()):
            if i and words[i - 1].lower() in prev:
                lem = target
                break
        if normalized:
            for previous, following, target, capitalized in IR_REVIEWED_CONTEXT.get(normalized[i], ()):
                if capitalized and not any(c.isupper() for c in w):
                    continue
                # ^ anchors a reviewed name to unit start; later capitals
                # already receive the loader's name label.
                if previous and not any((i == 0 if p == "^" else
                                         normalized[max(0, i - len(p.split())):i] == p.split())
                                        for p in previous):
                    continue
                if following and not any(normalized[i + 1:i + 1 + len(f.split())] == f.split()
                                         for f in following):
                    continue
                lem = target
                break
        # W2-089: negative preverbal complex; the exact clitic/OCR analysis
        # of final f is not needed to exclude the snow noun here.
        # nyf also denotes snow; preserve that noun outside this reviewed context.
        if (lemz.lm.lang == "cy" and key_cy(welsh_norm(w, True)) == "nyf"
                and i + 1 < len(words)
                and key_cy(welsh_norm(words[i + 1], True)) == "rygelwy"):
            lem = "ny"
        # The Stage C loader adds a name marker to medial capitalized forms.
        # Keep the reviewed initial-name rule, but avoid a second marker here.
        if i > 0 and w[:1].isupper() and lem == "caílte (name)":
            lem = "caílte"
        # W5-036: conjunction eny/yny before the reviewed tide verb.
        if (lemz.lm.lang == "cy" and key_cy(welsh_norm(w, True)) == "eny"
                and i + 1 < len(words)
                and key_cy(welsh_norm(words[i + 1], True)) == "trei"):
            lem = "yny"
        out.append(lem)
    return out


def irish_lemmatizer(maps: CelticMappings, **kw) -> CelticLemmatizer:
    return CelticLemmatizer(maps.irish, irish_demutate, irish_skeleton, norm=_ir_clean, **kw)


def welsh_lemmatizer(maps: CelticMappings, diplomatic: bool = False, **kw) -> CelticLemmatizer:
    """diplomatic=True for the Evans / Rhŷs & Evans diplomatic editions (OCR repair, welsh_norm)."""
    return CelticLemmatizer(maps.welsh, welsh_demutate, welsh_skeleton,
                            norm=lambda w: welsh_norm(w, diplomatic), **kw)


# ---------------------------------------------------------------- content words (Stage C 30% rule)

def is_function_lemma(lm: fm.LangMapping, lem: str) -> bool:
    """A lemma string all of whose parts are function words (no table row)."""
    fw = IR_FUNCTION if lm.lang == "sga" else CY_FUNCTION
    return all(p in fw or (lm.lang == "sga" and p in {"suil@before", "ós", "eter", "mani", "aithle@afterwards", "dáig@because", "fochen@welcome", "gé@although"})
               for p in lem.split("|"))


def content_of(lm: fm.LangMapping, lem: str, surface: str, lemz=None) -> bool:
    """Is a token a content word? fm.LangMapping.is_content, except: function
    words (IR_FUNCTION / CY_FUNCTION) are not content; nor are one-letter
    tokens, unknown forms of ≤ 2 letters (m., mc., K., OCR debris), and
    two-letter forms that the lemmatizer `lemz` matched only after mutation
    stripping or by skeleton."""
    lang = "cy" if lm.lang == "cy" else "sga"
    if (lm.lang == "sga" and is_function_lemma(lm, lem)
            or lm.lang == "cy" and (lem, key_cy(surface)) in {("ny", "nyf"), ("yny", "eny")}):
        return False
    if len(surface) <= 1 or is_function_word(surface, lang):
        return False
    if lem.startswith("?") and len(lem) <= 3:
        return False
    if len(surface) == 2 and lemz is not None and lemz.level.get(surface, "form") not in ("form", "override"):
        return False
    return lm.is_content(lem)


# ---------------------------------------------------------------- CELT licence tags
#
# David (2026-10-24): the 58 CELT files G4000xx carry an Oxford University Press copyright notice and are
# research only; the other CELT files are usable for training under the consent. Taken as G400001–G400058
# (the 58 files numbered G4000xx up to the first gap; G400065–G400090 are outside the count).

# exactly the files whose TEI <availability> carries the Oxford University Press copyright notice (checked
# 2026-10-24 over all 412 headers); other files cite OUP/Clarendon only as the print edition's publisher
CELT_RESEARCH_ONLY = frozenset(f"G4000{n:02d}" for n in range(1, 59))


def celt_licence(source: str) -> str:
    """'research' for the OUP-notice CELT files, 'consent-train' for the rest."""
    return "research" if source in CELT_RESEARCH_ONLY else "consent-train"


# ---------------------------------------------------------------- reading the tables (for the Stage C builder)

MAPPING_DIR = "data/research/formulas/mapping"
TABLES = {"celt": "Irish (CELT, Irish OCR editions)", "sga-glosses": "Old Irish glosses (Wb, Sg)",
          "cy": "Welsh (OCR editions)"}


def read_table(corpus: str, root: Path = ROOT) -> dict:
    """lemma string → lexicon ids, with the mapping overrides applied."""
    out = {}
    for line in (Path(root) / MAPPING_DIR / f"{corpus}.jsonl").read_text("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["lemma"]] = tuple(r["lex_id"])
    return fm.apply_table_overrides(corpus, out, root=root)
