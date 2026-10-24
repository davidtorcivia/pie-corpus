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
""".split())
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
""".split())


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


def matasovic_entries(root: Path = ROOT) -> list[dict]:
    out, cur, field = [], None, None
    files = sorted((Path(root) / MATASOVIC).glob("p*.txt"))
    for fn in files:
        page = fn.stem
        for line in fn.read_text("utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            m = _MAT_HEAD.match(line)
            if m and not re.match(r"^\*[A-Z]", line):
                cur = {"head": "*" + m.group(1).strip(",.;"), "page": page, "goid": "", "w": "", "pie": "",
                       "etym": ""}
                out.append(cur)
                field = None
                continue
            if cur is None:
                continue
            lab = re.match(r"^([A-Za-z0-9 ]{1,7}):\s*(.*)$", line)
            if lab:
                L = lab.group(1).replace("0", "O").replace("l", "I").upper().replace(" ", "")
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
    if matasovic:
        add_matasovic(irish, welsh, lex, root)
    return CelticMappings(irish, welsh, parts, lex)


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
            if not e["pie"] or _MAT_LOAN.search(e["etym"]):
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
    return all(p in fw for p in lem.split("|"))


def content_of(lm: fm.LangMapping, lem: str, surface: str, lemz=None) -> bool:
    """Is a token a content word? fm.LangMapping.is_content, except: function
    words (IR_FUNCTION / CY_FUNCTION) are not content; nor are one-letter
    tokens, unknown forms of ≤ 2 letters (m., mc., K., OCR debris), and
    two-letter forms that the lemmatizer `lemz` matched only after mutation
    stripping or by skeleton."""
    lang = "cy" if lm.lang == "cy" else "sga"
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
