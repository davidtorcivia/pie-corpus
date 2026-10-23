"""NIL (Wodtko, Irslinger & Schneider 2008): noun formations, read from page images.

`build_records()` turns the transcription chunks (raw/books/extract/nil/,
local) into facts-only records for data/lexicon/nil.jsonl: the root, and per
formation the stem as printed, a normalized stem, gender, marker, the first
daughter words and an English gloss composed from what they agree on.

`apply()` (called by pie.lexicon.build) links each NIL root to a lexicon root
(the LIV² page both sides carry first, else the form with gloss agreement),
then each formation to a derivative of that root whose form is the formation's
expected nominative (length kept, accent ignored, same stem class). A matched
lexeme gets a `nil` block, and if it has no dictionary gloss it takes NIL's
(`meaning_source: "nil"`). Formations marked ‡, ** (pre-forms) or ˣ are never
used as PIE glosses.

NIL's starred forms are transponates, not reconstructions, and NIL prints no
meanings: every gloss here was composed from the daughters (NIL's introduction,
raw/books/text/nil/p0011-p0023, §§ 5-10). A new lexeme built from a formation attested in fewer than two
branches (counting only daughters outside NIL's `[` remodelling bracket) is
flagged `nil-single-branch`.
"""

from __future__ import annotations

import collections
import json
import re
import unicodedata
from pathlib import Path

from .liv import _depal, _gloss_sim, _plain, headword
from .notation import normalize
from .translit import is_canonical

ROOT = Path(__file__).resolve().parent.parent
FIRST_PAGE, LAST_PAGE, CHUNK = 78, 807, 30
NFC = lambda s: unicodedata.normalize("NFC", s)       # noqa: E731
NFD = lambda s: unicodedata.normalize("NFD", s)       # noqa: E731
NO_GLOSS_MARKERS = ("‡", "**", "ˣ")

# NIL's language abbreviations → branch (the same branches as scripts/make_slice.py BRANCHES)
_BRANCH_ABBR = {
    "Indo-Iranian": "ved ai aav jav av apers mpers npers iran khot sogd osset pašto šughni skr pal Mitanni",
    "Greek": "gr myk dor ion att aiol boiot arkad",
    "Italic": "lat alat spätlat osk umbr pälign marrucin falisk ital venet",
    "Celtic": "air mir ir kelt gall keltib hispano-kelt mkymr akymr nkymr kymr bret mbret abret akorn mkorn "
              "abrit Ogam lusit",
    "Germanic": "germ urgerm got an ae ahd as mhd mnd mnl afr norw langobard bair",
    "Balto-Slavic": "lit alit lett apr balt aksl ksl slav urslav russ aruss russ.ksl serb.ksl poln tschech "
                    "atschech čech ačech sloven bulg serb ukr",
    "Armenian": "arm", "Albanian": "alb",
    "Anatolian": "heth aheth hluv kluv luv lyk lyd",
    "Tocharian": "toch",
}
BRANCH_OF = {a: b for b, s in _BRANCH_ABBR.items() for a in s.split()}


def chunk_range(name: str) -> tuple[int, int]:
    n = int(name.split("-")[1])
    if n == 0:
        return 270, 299                      # the pilot
    lo = FIRST_PAGE + CHUNK * (n - 1)
    return lo, min(LAST_PAGE, lo + CHUNK - 1)


def stem(printed: str | None) -> str | None:
    """'?*ĝnoh₃-tér-' → 'ǵneh₃tér' normalized; None for schematic or partial forms.

    NIL writes the colouring next to the laryngeal (h₂áu̯g-, -ah₂-, ĝnoh₃-); the lexicon writes
    h₂e / eh₂ / eh₃. NIL's cover symbols (R = r or l) and a syllabic sonorant before a vowel
    (a transcription slip: *oi̯bʰ-r̥ó-) give None.
    """
    if not printed:
        return None
    s = printed.split(">")[-1].strip()                 # '**h₁éd-u̯-on- > *h₁éd-u̯on-': the later form
    s = re.sub(r"^[?‡ˣ\[\s*]+|[\]\s]+$", "", s).replace("(-)", "")
    if s.startswith("-") or "/" in s or "´" in s or re.search(r"\([^)]*\)", s):
        return None                                   # suffix-only, alternants or optional parts
    if re.search(r"[A-GI-Z]", s):
        return None                                   # R (r/l), K, T, V…: a cover symbol, not a segment
    # h₃-colouring only inside a morpheme: *ĝnoh₃-tér- is ǵneh₃tḗr, but *kor-i̯o-h₃ōn- keeps its o
    t = normalize(s, "liv2").text
    t = "".join(NFC(re.sub("óh₃", "éh₃", re.sub("oh₃", "eh₃", NFC(seg)))) for seg in t.split("-"))
    t = re.sub("h₂á|áh₂", lambda m: m[0].replace("á", "é"), t)
    t = NFC(re.sub("h₂a|ah₂", lambda m: m[0].replace("a", "e"), t))
    if re.search(r"[rlmn]̥́?(?=[aeiou])", NFD(t)):
        return None                                   # r̥ before a vowel is r (or a misread)
    return t if t and is_canonical(t) else None


_GLOSS_DROP = re.compile(r",?\s*\b(?:in compounds?|compound(?: first| second)? member|compound)\b", re.I)


def clean_gloss(g: str | None) -> str | None:
    """A composed NIL gloss → a PIE gloss, or None. Drops glosses with '?', parentheticals
    ('(in compounds)', '(infinitive)', '(oak in Greek)'), and senses that are verbs ('to give':
    an infinitive among the daughters, not a meaning of the noun)."""
    if not g or "?" in g:
        return None
    g = re.sub(r"\s*\([^)]*\)", "", g)
    g = _GLOSS_DROP.sub("", g)
    senses = [s.strip(" ,") for s in g.split(";")]
    senses = [s for s in senses if s and not s.lower().startswith("to ") and "infinitive" not in s.lower()]
    g = "; ".join(senses).strip(" ,;")
    return g or None


def branches(evidence: list) -> set[str]:
    """Branches of the daughters NIL cites, leaving out those in its remodelling bracket `[`
    (the daughter does not continue the transponate unchanged)."""
    out = set()
    for s in evidence:
        s = s if isinstance(s, str) else s.get("form", "")
        if s.lstrip("? ").startswith("["):
            continue
        m = re.match(r"[?\s]*([^\s,]+?)\.?[\s,]", s)
        b = BRANCH_OF.get(m[1]) if m else None
        if b:
            out.add(b)
    return out


_GENDER = re.compile(r"(?<![\w.])(m|f|n|c)\.(?=[\s,)/;]|$)")


def ev_gender(evidence: list) -> str | None:
    """What the daughters say a formation is: a gender ('m', 'f', 'n'; Hittite c. counts as m),
    'noun' (nouns whose gender is not cited), 'adj', 'mixed' (as many nouns as adjectives), or
    None without evidence.

    Per daughter, only its headword part counts (before its gloss and before 'Subst.':
    mádhya- 'mittlerer', Subst. n. 'Mitte' is an adjective). A daughter with no gender mark is
    a noun if its German gloss is capitalized (ved. bhūmá- 'Erde'), or a Latin neuter in -um,
    else an adjective. Daughters in NIL's remodelling bracket count only when no other is cited."""
    ev = [s if isinstance(s, str) else s.get("form", "") for s in evidence]
    ev = [s for s in ev if s.strip() and not s.lstrip("? ").startswith(("Subst", "HG"))]
    plain = [s for s in ev if not s.lstrip("? ").startswith("[")]
    ev = plain or ev
    if not ev:
        return None
    genders, nouns, adj = [], 0, 0
    for s in ev:
        cut = re.search(r"['‘’\"]|Subst\.", s)
        head, sep, rest = (s[:cut.start()], cut[0], s[cut.end():]) if cut else (s, "", "")
        gs = ["m" if m[1] == "c" else m[1] for m in _GENDER.finditer(head)]
        if gs:
            genders.append(gs[0])
        elif re.match(r"[?\[\s]*lat\.\s+\S+um\b", head) and "-um" not in head:
            genders.append("n")                           # lat. fermentum, aurum
        elif sep == "Subst.":
            continue                                      # an adjective also used as a noun: no vote
        elif re.match(r"\W*(?:[A-ZÄÖÜ]|eine?\s)", rest):   # 'Erde', 'ein Orakelvogel'
            nouns += 1
        else:
            adj += 1
    nounish = len(genders) + nouns
    if nounish == 0:
        return "adj"
    if adj > nounish:
        return "adj"
    if adj == nounish:
        return "mixed"
    return collections.Counter(genders).most_common(1)[0][0] if genders else "noun"


def _palatal_lost(root: str | None, st: str | None) -> bool:
    """*(-)genh₁-etó- under *ĝenh₁-: the root has a palatal, the formation only a plain k/g."""
    if not root or not st:
        return False
    pal = re.compile("[ḱǵ]")
    return bool(pal.search(NFC(root))) and not pal.search(NFC(st)) and bool(re.search("[kg](?!ʷ)", NFC(st)))


def build_records(root: Path = ROOT) -> list[dict]:
    out, seen = [], set()
    for f in sorted((root / "raw/books/extract/nil").glob("chunk-*.jsonl")):
        lo, hi = chunk_range(f.stem)
        for line in f.read_text("utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if "root_printed" not in e or not lo <= int(e.get("pdf_page") or -1) <= hi + 10:
                continue
            key = (e["root_printed"], e.get("root_gloss_de"))
            if key in seen or not e.get("formations"):
                continue
            seen.add(key)
            alts = []
            # alternatives are split on ',' and on '/' only before a new starred form
            # (*su̯ek̂ur̥/u̯er- is one headword, not *su̯ek̂ur̥- and *u̯er-)
            for part in re.split(r"\s*,\s*|\s*/\s*(?=[?*])", e["root_printed"]):
                part = re.sub(r"\((ó|o)-\)", "", part).strip()
                if "´" in part or not part.strip("*?- "):
                    continue
                f_, h_, u_ = headword(part)
                if f_ and f_ not in alts:
                    alts.append(f_)
            form, hom, unc = (alts[0] if alts else None), *headword(e["root_printed"].split(",")[0])[1:]
            fms = []
            for x in e["formations"]:
                st = stem(x.get("form_printed"))
                ev = (x.get("evidence") or [])[:4]
                flags = ["palatal-lost"] if _palatal_lost(form, st) else []
                fms.append({
                    "printed": x.get("form_printed"), "stem": st,
                    "marker": x.get("marker") or ("‡" if (x.get("form_printed") or "").startswith("‡") else None),
                    "indent": x.get("indent"), "gender": x.get("gender"),
                    "gloss_en": clean_gloss(x.get("gloss_en")), "gloss_en_composed": x.get("gloss_en"),
                    "evidence": ev, "branches": sorted(branches(x.get("evidence") or [])),
                    "uncertain": bool(x.get("uncertain")), "flags": flags,
                })
            out.append({
                "root": form, "root_alternatives": alts, "homograph": hom, "uncertain": unc or bool(e.get("uncertain_chars")),
                "root_printed": e["root_printed"], "root_gloss_de": e.get("root_gloss_de"),
                "root_gloss_en": e.get("root_gloss_en"), "liv_ref": e.get("liv_ref"),
                "page": {"pdf": e.get("pdf_page"), "printed": e.get("printed_page")},
                "formations": fms,
            })
    return out


def _shape(stem: str, gender: str | None, evidence: list = ()) -> tuple[str, str, str | None] | None:
    """NIL stem + gender (+ the daughters' genders) → (nominative, pos, gender), or None."""
    g = gender if gender in ("m", "f", "n") else None
    ev = ev_gender(evidence) if evidence else None
    if g is None and ev in ("m", "f", "n"):
        g = ev
    stem = NFC(re.sub(r"([íiúu])H$", lambda m: m[1] + "h₂", stem))   # *neptíH- → neptíh₂
    if re.search(r"(?<![aeiouáéíóú])y[eéoó]s$", stem):
        # *-i̯es-/-i̯os- comparative (m nom *-yōs, n *-yos, weak *-is-): no comparative family
        # in the engine yet (pedyōs is unusable too), so no lexeme rather than a neuter s-stem
        return None
    if re.search(r"[oó]$", stem):
        if g is None:
            ev_text = " ".join(s if isinstance(s, str) else s.get("form", "") for s in evidence)
            if ev in ("noun", "mixed") or "Subst." in ev_text:
                return None                    # a noun of unknown gender, or noun and adjective: don't guess
            return stem + "s", "adj", None
        return stem + ("m" if g == "n" else "s"), "noun", g
    if stem.endswith(("eh₂", "éh₂")):                     # eh₂-stem (NIL -ah₂-, normalized in stem())
        return stem, "noun", "f"
    if stem.endswith(("ih₂", "íh₂", "uh₂", "úh₂")):         # devī type, sweḱrúh₂: no -s
        return stem, "noun", "f"
    if stem.endswith(("h₁", "h₂", "h₃", "H")):
        return None                                      # laryngeal-final root noun (gʷénh₂): no -s
    if re.search(r"[ií]$|[uú]$", stem) and g in ("m", "f"):
        return stem + "s", "noun", g
    if re.search(r"[eé]s$", stem) and g in (None, "n"):   # s-stem neuter: ǵénh₁es- → ǵénh₁os
        return re.sub(r"([eé])s$", lambda m: {"e": "o", "é": "ó"}[m[1]] + "s", stem), "noun", "n"
    if re.search(r"m[eé]n$", stem) and g == "n":
        return re.sub(r"m[eé]n$", "mn̥", stem), "noun", "n"
    if re.search(r"t[eé]r$", stem) and g in (None, "m", "f"):
        return re.sub(r"t([eé])r$", lambda m: "t" + ("ḗ" if m[1] == "é" else "ē") + "r", stem), "noun", g or "m"
    if re.search(r"t[oó]r$", stem) and g in (None, "m"):
        return stem[:-2] + "ōr", "noun", "m"
    if re.search(r"[^aeiouāēīōūáéíóúr̥l̥m̥n̥]$", stem) and g in ("m", "f"):
        return stem + "s", "noun", g                      # root noun
    return None


def citation(stem: str, gender: str | None, evidence: list = ()) -> tuple[str, str, str | None] | None:
    """NIL stem + gender → (citation form, pos, gender) for the classifier, or None.

    NIL prints stems (*ĝnoh₃-tér-, *dʰiH-ti-); the lexicon cites nominatives. An o-stem NIL
    prints without a gender takes the gender its daughters cite (θεός m.); with none it is an
    adjective, unless a daughter is cited as a substantive (Subst.), when no lexeme is made.
    """
    from .phon import has_accent, parse
    try:
        if not has_accent(parse(stem)):
            return None                       # the slice gate needs an accent; don't guess one
    except ValueError:
        return None
    c = _shape(stem, gender, evidence)
    return (NFC(c[0]), c[1], c[2]) if c else None


def _key(form: str) -> str:
    from .validate import key
    return key(form.strip("-"), "nolength")


def _length(form: str) -> str:
    """The long vowels of a form, in order (h₃ōkʷ- ≠ h₃okʷ-, u̯ēdro- ≠ wedrom)."""
    d = NFD(form)
    return "".join(d[i - 1] for i, c in enumerate(d) if c == "̄" and i)


def _nkey(form: str) -> str:
    """A colour-, laryngeal-, accent-, length- and syllabicity-insensitive key for the duplicate
    check: dóh₃tōr ~ déh₃tōr, neptíH ~ néptih₂, h₁l̥ngʷʰrós ~ h₁ln̥gʷʰrós."""
    from .validate import key
    f = NFC(re.sub("óh₃", "éh₃", re.sub("oh₃", "eh₃", NFC(form.strip("-")))))
    f = re.sub(r"([iu])H", r"\1h₂", f)
    return NFD(key(f, "generic-H")).replace("̥", "")


def _stem_key(form: str) -> str:
    """A word's key without its nominative ending: h₂éh₂usos ~ h₂éh₂usom."""
    return _nkey(re.sub(r"(os|ós|om|óm|s|m)$", "", NFC(form.strip("-"))))


_FAMILY = {"thematic": "o", "thematic-adj": "o", "thematic-neuter": "o", "thematic-neuter-reflex": "o",
           "s-stem-neuter": "s", "eh2": "eh2", "devi": "ih2", "er-stem": "r", "tor-agent": "r",
           "hk-iu-stem": "iu", "pk-iu-stem": "iu", "u-adj": "iu", "n-stem-hk": "n", "n-stem-ak": "n",
           "men-neuter": "men"}


def _family(e: dict) -> str | None:
    from .classify import by_shape
    try:
        rule = by_shape(e).rule
    except Exception:
        return None
    return _FAMILY.get(rule.split(":", 1)[-1])


def expected(fm: dict) -> list[tuple[str, str | None]]:
    """The forms an existing lexeme may cite a NIL formation by, with the stem class:
    the nominative, and the bare stem (the lexicon cites yewgtér-, h₂eḱu-)."""
    st = fm.get("stem")
    if not st:
        return []
    out = []
    c = _shape(st, fm.get("gender"), fm.get("evidence") or [])
    if c:
        out.append((NFC(c[0]), _family({"form": NFC(c[0]), "pos": c[1], "gender": c[2]})))
    if re.search(r"[oó]$", st) and fm.get("gender") not in ("m", "f", "n"):
        out += [(st + "s", "o"), (st + "m", "o")]        # a genderless o-stem: either nominative
    elif not c and re.search(r"[iuíú]$", st):
        out.append((st + "s", "iu"))                      # a genderless i/u-stem (pedtus)
    elif not c and re.search(r"(?<![aeiouáéíóú])y[eéoó]s$", st):
        out.append((st[:-2] + "ōs", None))                # comparative: *-yōs
    elif not c and re.search(r"[^aeiouāēīōūáéíóúr̥l̥m̥n̥]$", st) and not re.search(r"[eé]s$|m[eé]n$", st):
        out.append((st + "s", None))                      # root noun: only "" or "-s"
    out.append((st, None))
    return out


def _liv_page(x: dict) -> int | None:
    """The LIV² page NIL cites for the root; 'vgl. LIV 82' (cf.) names another root."""
    if re.match(r"\s*vgl\.", x.get("liv_ref") or ""):
        return None
    m = re.search(r"LIV\s*(\d+)", x.get("liv_ref") or "")
    return int(m[1]) if m else None


LIV_DJVU_OFFSET = 4          # LIV² printed page = DjVu page - 4 (all 1169 transcribed pages that print both)


def _page_distance(r: dict, p: int) -> int | None:
    ds = []
    for l in r.get("liv", []):
        pg = l.get("page") or {}
        pr = re.sub(r"\D", "", str(pg.get("printed") or ""))
        if pr:
            ds.append(abs(int(pr) - p))
        elif pg.get("djvu"):
            ds.append(abs(int(pg["djvu"]) - LIV_DJVU_OFFSET - p))
    return min(ds) if ds else None


def _root_sim(en: str, r: dict) -> float:
    senses = list(r.get("meaning") or []) + [l.get("meaning_en") or "" for l in r.get("liv", [])]
    return max((_gloss_sim(en, s.strip("'‘’ ").lower()) for s in senses), default=0.0)


def link_root(x: dict, by_plain: dict, by_depal: dict, by_generic: dict) -> tuple[dict | None, str]:
    """A NIL root → (lexicon root, how) or (None, why not).

    1. a candidate (same form, palatal-insensitive form, or laryngeal-generic form) carrying the
       LIV² page NIL cites; 2. else the same form, if exactly one candidate shares the gloss
       (a tie, or a gloss overlap under 0.2, leaves the root unlinked); 3. else a palatal- or
       laryngeal-insensitive form with gloss overlap ≥ 0.35."""
    from .validate import key as vkey
    en = (x.get("root_gloss_en") or "").lower()
    forms = x.get("root_alternatives") or ([x["root"]] if x.get("root") else [])
    uniq = lambda rs: list({r["id"]: r for r in rs}.values())      # noqa: E731
    exact = uniq(r for f in forms for r in by_plain.get(_plain(f), []))
    loose = uniq(r for f in forms for r in by_depal.get(_depal(f), []) + by_generic.get(vkey(f, "generic-H"), [])
                 if r not in exact)
    p = _liv_page(x)
    if p:
        # NIL cites the page the LIV² entry starts on ('LIV 136f.'); the LIV entry may be a page or
        # two off (a misprint, an entry starting at the foot of a page). A palatal- or
        # laryngeal-insensitive candidate needs the gloss too (2.*pei̯g- 'vex' is peyǵ-, not peyg-)
        dist = [(d, r) for r in exact + loose if (d := _page_distance(r, p)) is not None and d <= 2
                and (r in exact or _root_sim(en, r) > 0)]
        if dist:
            d, r = min(dist, key=lambda t: (t[0], _root_sim(en, t[1]) == 0, t[1] not in exact,
                                            -_root_sim(en, t[1])))
            return r, "liv-page"
    if exact:
        main = [r for r in exact if _plain(r["form"]) in {_plain(f) for f in forms}] or exact
        scored = sorted(((_root_sim(en, r), r) for r in main), key=lambda t: -t[0])
        if scored[0][0] >= 0.2 and (len(scored) == 1 or scored[1][0] < scored[0][0]):
            return scored[0][1], "form+gloss"
        return None, "ambiguous" if len(scored) > 1 else "gloss-mismatch"
    scored = sorted(((_root_sim(en, r), r) for r in loose), key=lambda t: -t[0])
    if scored and scored[0][0] >= 0.35 and (len(scored) == 1 or scored[1][0] < scored[0][0]):
        return scored[0][1], "loose-form+gloss"
    return None, "no-candidate"


def apply(entries: dict[str, dict], records: list[dict], reg=None) -> dict:
    from .validate import key as vkey
    roots = [e for e in entries.values() if e["kind"] == "root"]
    by_plain, by_depal, by_generic = {}, {}, {}
    for r in roots:
        for f in [r["form"], *r.get("variants", [])]:
            by_plain.setdefault(_plain(f), []).append(r)
            by_depal.setdefault(_depal(f), []).append(r)
            by_generic.setdefault(vkey(f, "generic-H"), []).append(r)
    words, by_stem = {}, {}
    for e in entries.values():
        if e["kind"] in ("word", "derivative"):
            words.setdefault(_key(e["form"]), []).append(e)
            by_stem.setdefault(_stem_key(e["form"]), []).append(e)
    children = {}
    for e in entries.values():
        if e["kind"] in ("word", "derivative") and e.get("root_id"):
            children.setdefault(e["root_id"], []).append(e)
    rep = collections.Counter(roots=len(records))
    for x in records:
        root, how = link_root(x, by_plain, by_depal, by_generic)
        if not root:
            # a nominal headword (*dʰéĝʰ-om-, *dʰugh₂tér-): a word cited by the headword's stem,
            # with the gloss agreeing
            en = (x.get("root_gloss_en") or "").lower()
            for f in x.get("root_alternatives") or []:
                st = f.replace("-", "")
                ws = [w for k in (_key(st), _key(st + "s"), _key(st + "m")) for w in words.get(k, [])]
                w = max(ws, key=lambda w: _root_sim(en, w), default=None)
                # the gloss agrees, or the only word of that form has no gloss to disagree with (koros)
                if w and (_root_sim(en, w) >= 0.2 or (len(ws) == 1 and not w["meaning"])):
                    root, how = entries.get(w.get("root_id") or "", w), "nominal-headword"
                    break
        if not root:
            rep[f"roots_unlinked_{how}"] += 1
            continue
        rep["roots_matched"] += 1
        rep[f"roots_by_{how}"] += 1
        root.setdefault("nil", []).append({"root_printed": x["root_printed"], "page": x["page"], "link": how})
        kids = {}
        for c in children.get(root["id"], []) + ([root] if root["kind"] != "root" else []):
            kids.setdefault(_key(c["form"]), []).append(c)
        for fm in x["formations"]:
            rep["formations"] += 1
            if not fm["stem"]:
                continue
            hit = _match(fm, kids)
            if not hit:
                rep.update(_new_lexeme(entries, kids, by_stem, root, x, fm, reg))
                continue
            rep["formations_matched"] += 1
            _attach(hit, x, fm, rep)
    return dict(rep)


def _match(fm: dict, kids: dict) -> dict | None:
    """The root's lexeme cited by the formation's expected nominative or bare stem: same letters
    (accent-insensitive), same long vowels, and not of another stem class (s-stem vs o-stem)."""
    best = None
    for form, fam in expected(fm):
        for c in kids.get(_key(form), []):
            if _length(c["form"].strip("-")) != _length(form):
                continue
            cf = _family(c) if fam else None
            if fam and cf and cf != fam:
                continue
            score = (fam is not None and cf == fam) * 2 + (NFC(c["form"].strip("-")) == form)
            if best is None or score > best[0]:
                best = (score, c)
    return best[1] if best else None


def _glossable(hit: dict, fm: dict) -> bool:
    """May NIL's gloss stand as this lexeme's gloss? Not for ‡/**/ˣ formations or flagged notation.
    (A branch-overlap test against the lexeme's reflexes was tried and dropped: NIL and Wiktionary
    often cite different daughters of the same word, h₂érh₃tis, sedti-, gʷéh₂tis.)"""
    return bool(fm.get("gloss_en")) and fm.get("marker") not in NO_GLOSS_MARKERS and not fm.get("flags")


def _attach(hit: dict, x: dict, fm: dict, rep) -> None:
    hit.setdefault("nil", []).append({**fm, "root_printed": x["root_printed"], "page": x["page"]})
    if not hit["meaning"] and _glossable(hit, fm):
        hit["meaning"], hit["meaning_source"] = [fm["gloss_en"]], "nil"
        rep["glossed"] += 1
    if hit.get("meaning_source") == "nil" and not hit.get("pos"):
        # NIL says whether the formation is a noun (and its gender) or an adjective: the lexeme's
        # paradigm must agree with the gloss it now carries (ḱubʰrós 'shining' is no noun)
        c = _shape(fm["stem"], fm.get("gender"), fm.get("evidence") or [])
        if c and _key(c[0]) == _key(hit["form"]):
            hit["pos"], hit["pos_source"] = c[1], "nil"
            if c[1] == "noun" and c[2] and not hit.get("gender"):
                hit["gender"] = c[2]
            rep["pos_set"] += 1


def _new_lexeme(entries: dict, kids: dict, by_stem: dict, root: dict, x: dict, fm: dict, reg) -> dict:
    """A NIL formation the lexicon lacks → a new derivative lexeme (citation form built from
    the stem; the classifier assigns the paradigm and decides usability as for any lexeme).
    → report counts."""
    from .lexicon import slug
    from .translit import to_ascii
    if reg is None or not fm["stem"] or not fm["gloss_en"] or fm["marker"] in NO_GLOSS_MARKERS:
        return {}
    c = citation(fm["stem"], fm.get("gender"), fm.get("evidence") or [])
    if not c:
        return {"no_citation": 1}
    form, pos, g = c
    if not is_canonical(form):
        return {"no_citation": 1}
    # the lexicon may have the word already, under another root or spelling (h₂éh₂usom,
    # déh₃tōr, swéḱuros) or in the other ablaut grade with the same meaning (mórtos ~ mértos)
    dup = by_stem.get(_stem_key(form), [])
    if not dup:
        abl = lambda f: _nkey(f).replace("o", "e")       # noqa: E731
        dup = [k for ks in kids.values() for k in ks
               if abl(k["form"]) == abl(form) and max((_gloss_sim(fm["gloss_en"].lower(), m.lower())
                                                       for m in k["meaning"]), default=0) >= 0.5]
    if dup:
        hit = dup[0]
        hit.setdefault("nil", []).append({**fm, "root_printed": x["root_printed"], "page": x["page"],
                                          "match": "duplicate"})
        return {"duplicate": 1}
    unc = []
    if fm["uncertain"]:
        unc.append("nil-uncertain")
    if len(fm.get("branches") or branches(fm.get("evidence") or [])) < 2:
        unc.append("nil-single-branch")
    if fm.get("flags"):
        unc.append("nil-notation")
    lid = reg.get(f"nil|{x['root_printed']}|{fm['printed']}", f"pie-lex-{slug(form)}")
    entries[lid] = {
        "id": lid, "kind": "derivative", "form": form, "form_ascii": to_ascii(form), "variants": [], "stems": [],
        "pos": pos, "gender": g, "meaning": [fm["gloss_en"]], "meaning_source": "nil",
        "uncertain": unc, "source": "nil",
        "source_ref": {"dump": "NIL (Wodtko, Irslinger & Schneider 2008)", "page": x["page"],
                       "printed": fm["printed"]},
        "confidence": "entry", "normalized": [], "etymon_parts": [], "reflexes": {},
        "nil": [{**fm, "root_printed": x["root_printed"], "page": x["page"]}],
        "parents": [root["id"]], "root_link_source": "nil", "root_id": root["id"] if root["kind"] == "root"
        else root.get("root_id")}
    kids.setdefault(_key(form), []).append(entries[lid])
    by_stem.setdefault(_stem_key(form), []).append(entries[lid])
    return {"new": 1, **({"new_single_branch": 1} if "nil-single-branch" in unc else {})}
