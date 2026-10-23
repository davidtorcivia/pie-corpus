#!/usr/bin/env python3
"""Phase 8b replication 2 dataset (pre-registered in docs/research/8b-preregistration-2.md).

  uv run --group research python -I scripts/build_replication2.py
  uv run --group research python -I scripts/build_replication2.py --check-greek   # transliterator check

One cognate set per NIL formation (data/lexicon/nil.jsonl, `formations[].evidence`:
strings like "ved. āśú- 'schnell'", up to four per formation), target the NIL stem
written pre-laryngeally (pie/prelaryngeal.py, unchanged). No raw/ input.

Rules (fixed before the data was built):
- formations: dropped if marked ‡, ** or ˣ, if `uncertain` (NIL's leading ?), or if
  pie.nil.stem() gives no stem (schematic or partial form). Two formations with the
  same stem are one set (inputs merged).
- evidence parsing: German glosses ('...') and parentheticals are removed; a string
  is split into language segments at each NIL language abbreviation ("aav., jav.
  garəma-" gives both languages the word; "air. dét n., mkymr. dant m." gives two
  segments). Per segment the first word after the abbreviation and any labels
  (Inf., Adv., Kompar., dial., usw., ...) is taken; later variants are ignored.
- daughter words dropped (the first run's usable() rule: no uncertain, no analogical
  reflexes): words in a string with a leading `?` (uncertain); words after NIL's
  remodelling bracket `[` (as pie.nil.branches() does: the daughter does not continue
  the transponate unchanged); oblique case forms (GSg., ASg., NPl., ...; nominatives
  NSg./NASg. are kept); names (PN, ON, GN, a capitalized word); words cited inside a
  compound ("lat. in acu-pedius", "komp."); reconstructed forms (any `*` word:
  germ., kelt., slav., iran., ital., urgerm., urslav. proto-forms; their attested
  daughters after "in" are kept as their own segments).
- languages: NIL abbreviations mapped to the language labels of the first run's
  inputs (ABBR below); attested languages only; Anatolian (incl. Palaic `pal.`) and
  Tocharian removed; Mitanni (names in cuneiform) removed. A form writing laryngeal
  notation is dropped, and a language over 2% would be dropped whole.
- normalization to the Wiktionary romanizations the model was trained on: Greek
  script transliterated (Wiktionary scheme: η ē, ω ō, υ u, χ kh, rough breathing h,
  circumflex as ^, iota subscript as i, γγ ng); Sanskrit r̥ l̥ (ring below) → ṛ ḷ
  (dot below), ṁ → ṃ; Avestan ϑ → θ; Church Slavonic ь ъ → ĭ ŭ; Armenian ʿ ‘ ' → ʻ;
  Mycenaean ₂ ₃ → 2 3. Stem hyphens and morpheme boundaries (- and . inside the word)
  are removed (kept in Mycenaean and Old Persian, whose training forms write them);
  ⟨ ⟩ and + are removed; a trailing · or , is removed.
- a word could not be normalized if it is a fragment (leading -), has optional
  letters in parentheses, or has, after normalization, an NFD character that is not
  in the model's input vocabulary (characters seen ≥ 2 times in the first run's
  primary inputs) or not seen in that language's first-run inputs. Such words are
  dropped and counted (the pre-registered >20% caveat).
- sets: at least 2 languages.
- independence, per formation: dropped if the formation's stem, its pre-laryngeal
  target or its expected nominatives (pie.nil.expected) match, up to accent and
  length, a first-run (primary or secondary) target or modern form, with or without
  its nominal ending (-os -om -s -m); or if a first-run row's lexicon entry carries a
  NIL block naming this formation (pie.nil.apply() linked them). Both are
  tightenings of "stem matches a target": they can only remove sets.
- family (bootstrap cluster): the lexicon root linked to the NIL root (its `nil`
  block), else `nil:<root as printed>`.

Writes data/research/backtest/replication2.jsonl and replication2_meta.json.
"""

from __future__ import annotations

import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie import backtest as bt  # noqa: E402
from pie import nil as pnil  # noqa: E402
from pie.prelaryngeal import convert  # noqa: E402

D = ROOT / "data/research/backtest"
LAR = re.compile(r"h[₁₂₃ₓ]|ʔ|ə[₁₂₃]")
CONTAMINATION_RATE = 0.02
NFC = lambda s: unicodedata.normalize("NFC", s)       # noqa: E731
NFD = lambda s: unicodedata.normalize("NFD", s)       # noqa: E731

ABBR = {
    # Indo-Iranian
    "ved": "Sanskrit", "ai": "Sanskrit", "aav": "Avestan", "jav": "Avestan", "av": "Avestan",
    "apers": "Old Persian", "mpers": "Middle Persian", "npers": "Persian", "khot": "Khotanese",
    "sogd": "Sogdian", "osset": "Ossetian", "pašto": "Pashto", "šughni": "Shughni", "waxi": "Wakhi",
    # Greek
    "gr": "Ancient Greek", "myk": "Mycenaean Greek", "dor": "Doric Greek", "att": "Attic Greek",
    "ion": "Ionic Greek", "aiol": "Aeolic Greek", "boiot": "Boeotian Greek", "arkad": "Arcadocypriot Greek",
    "maked": "Ancient Macedonian",
    # Italic
    "lat": "Latin", "alat": "Old Latin", "spätlat": "Latin", "osk": "Oscan", "umbr": "Umbrian",
    "pälign": "Paelignian", "marrucin": "Marrucinian", "falisk": "Faliscan", "venet": "Venetic",
    # Celtic
    "air": "Old Irish", "mir": "Middle Irish", "ir": "Irish", "mkymr": "Middle Welsh", "akymr": "Old Welsh",
    "kymr": "Welsh", "nkymr": "Welsh", "mbret": "Middle Breton", "abret": "Old Breton", "bret": "Breton",
    "akorn": "Old Cornish", "mkorn": "Middle Cornish", "gall": "Gaulish", "keltib": "Celtiberian",
    "hispano-kelt": "Hispano-Celtic", "lusit": "Lusitanian", "Ogam": "Primitive Irish", "abrit": "Brittonic",
    # Germanic
    "got": "Gothic", "an": "Old Norse", "ae": "Old English", "ahd": "Old High German", "as": "Old Saxon",
    "mhd": "Middle High German", "afr": "Old Frisian", "mnd": "Middle Low German", "mnl": "Middle Dutch",
    "norw": "Norwegian", "langobard": "Lombardic", "bair": "Bavarian",
    # Balto-Slavic
    "lit": "Lithuanian", "alit": "Old Lithuanian", "lett": "Latvian", "apr": "Old Prussian", "kur": "Curonian",
    "aksl": "Old Church Slavonic", "ksl": "Church Slavonic", "russ.ksl": "Church Slavonic",
    "russ.-ksl": "Church Slavonic", "serb.ksl": "Church Slavonic", "aruss": "Old East Slavic",
    "russ": "Russian", "skr": "Serbo-Croatian", "serb": "Serbo-Croatian", "poln": "Polish", "apoln": "Old Polish",
    "tschech": "Czech", "čech": "Czech", "atschech": "Old Czech", "ačech": "Old Czech", "sloven": "Slovene",
    "bulg": "Bulgarian", "ukr": "Ukrainian",
    # others
    "arm": "Old Armenian", "alb": "Albanian", "thrak": "Thracian", "phryg": "Phrygian", "aphryg": "Phrygian",
    "nphryg": "Phrygian", "illyr": "Illyrian", "messap": "Messapic",
    # rarer abbreviations
    "korn": "Cornish", "aschwed": "Old Swedish", "schwed": "Swedish", "dän": "Danish", "nisl": "Icelandic",
    "me": "Middle English", "engl": "English", "nhd": "German", "ndl": "Dutch", "krimgot": "Crimean Gothic",
    "kypr": "Arcadocypriot Greek", "lesb": "Aeolic Greek", "kret": "Cretan Greek", "hom": "Epic Greek",
    "ep": "Epic Greek", "parth": "Parthian", "chwaresm": "Khwarezmian", "iron": "Iron Ossetian",
    "dig": "Digor Ossetian", "obersorb": "Upper Sorbian", "mbulg": "Bulgarian", "nir": "Irish", "mkym": "Middle Welsh",
    "alett": "Latvian", "let": "Latvian", "geg": "Gheg Albanian", "vl": "Vulgar Latin", "pkt": "Prakrit",
    "sabin": "Sabine", "volsk": "Volscian", "lepont": "Lepontic",
}
EXCLUDED = {  # abbreviation → why
    **{a: "anatolian" for a in "heth aheth jheth hluv kluv luv lyk lyd pal".split()},
    "toch": "tocharian",
    **{a: "proto" for a in ("germ urgerm kelt slav urslav iran balt ital idg uridg wgerm westgerm frühgerm urnord "
                            "urkelt urbrit inselkelt altiran ostmitteliran").split()},
    "Mitanni": "mitanni", "elam": "non-ie", "hurrit.-akkad": "non-ie",
}
BARE = {"pašto", "Ogam", "Mitanni"}           # abbreviations NIL writes without a dot
CASE = re.compile(r"^(?:[GADILV]|Abl|DAbl|GDAbl|DAbl|Instr|Lok|Akk|Dat|Gen|NA|AN|NAV)(?:Sg|Pl|Du)\.?$")
NAME = {"PN", "PNn", "ON", "ONn", "GN", "GNn", "FlN", "VN", "Stammesname", "Name", "Titel"}
HYPHEN_KEPT = {"Mycenaean Greek", "Old Persian"}
IRANIAN = {"Avestan", "Old Persian", "Middle Persian", "Persian", "Khotanese", "Sogdian", "Ossetian", "Pashto",
           "Shughni", "Wakhi"}

# ---------------------------------------------------------------- Greek transliteration

GRC = {"β": "b", "γ": "g", "δ": "d", "ζ": "z", "θ": "th", "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ξ": "x",
       "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "φ": "ph", "χ": "kh", "ψ": "ps", "ϝ": "w", "ϙ": "q",
       "ϲ": "s", "ϳ": "j"}
GRC_V = {"α": "a", "ε": "e", "η": "e", "ι": "i", "ο": "o", "υ": "u", "ω": "o"}
PSILI, DASIA, ACUTE, GRAVE, CIRC = "\u0313", "\u0314", "\u0301", "\u0300", "\u0342"
YPOG, DIAER, MACRON, BREVE, CIRCUMFLEX = "\u0345", "\u0308", "\u0304", "\u0306", "\u0302"


def is_greek(s: str) -> bool:
    return any("\u0370" <= c <= "\u03ff" or "\u1f00" <= c <= "\u1fff" for c in s)


def greek_translit(word: str) -> str:
    """Greek script → Wiktionary-style romanization (ἧκα → hêka, ὠκύς → ōkús, ᾠδή → ōidḗ)."""
    units = []                                       # [base, marks]
    for ch in NFD(word.lower()):
        if unicodedata.combining(ch) and units:
            units[-1][1].append(ch)
        else:
            units.append([ch, []])
    out, h_at_start = [], False
    for i, (b, marks) in enumerate(units):
        nxt = units[i + 1][0] if i + 1 < len(units) else ""
        if b == "γ" and nxt in ("γ", "κ", "ξ", "χ"):
            out.append("n")
            continue
        if b in GRC:
            prev = units[i - 1][0] if i else ""
            out.append("rh" if b == "ρ" and (DASIA in marks or prev == "ρ") else GRC[b])
            continue
        if b not in GRC_V:
            out.append(b + "".join(m for m in marks if m not in (PSILI, DASIA, BREVE)))
            continue
        if DASIA in marks:
            h_at_start = True                        # rough breathing only stands word-initially
        long = b in "ηω" or MACRON in marks or YPOG in marks
        acc = CIRCUMFLEX if CIRC in marks else ACUTE if ACUTE in marks else GRAVE if GRAVE in marks else ""
        r = GRC_V[b] + (DIAER if DIAER in marks else "")
        if YPOG in marks:                            # the accent goes on the iota: ῄ → ēí, ῷ → ōî
            r += MACRON + "i" + acc
        elif acc == CIRCUMFLEX:
            r += CIRCUMFLEX                          # circumflex replaces the macron: ê ô â
        else:
            r += (MACRON if long else "") + acc
        out.append(NFC(r))
    s = "".join(out)
    return NFC(("h" if h_at_start else "") + s)


# ---------------------------------------------------------------- evidence parsing

def _abbr(tok: str) -> str | None:
    t = tok.rstrip(",;:")
    if t in BARE:
        return t
    if not t.endswith("."):
        return None
    a = t[:-1]
    return a if a in ABBR or a in EXCLUDED else None


def parse_evidence(s: str) -> list[dict]:
    """One evidence string → segments {langs, word, drop} (drop: why the word is unusable)."""
    s = s.replace("’", "'").replace("‘", "'")
    lead = re.match(r"[\s?\[]*", s)[0]
    uncertain = "?" in lead
    bracket = "[" in lead
    s = s[len(lead):]
    s = re.sub(r"'[^']*'?", " §G ", s)              # German glosses
    s = re.sub(r"(?:(?<=\s)|^)\([^()]*\)(?=[\s,;]|$)", " ", s)   # parentheticals standing alone: (Pl.), (ageg.)
    segs: list[dict] = []
    cur = None
    for tok in s.split():
        if tok.startswith("["):
            bracket = True
            tok = tok[1:]
            if not tok:
                continue
        if "]" in tok:
            tok = tok.replace("]", "")
        a = _abbr(tok)
        if a:
            if cur is not None and cur["word"] is None and not cur["after_gloss"] and not cur["labels"]:
                cur["langs"].append(a)               # "aav., jav. garəma-" / "as., ae. bū"
            else:
                cur = {"langs": [a], "word": None, "labels": [], "flags": set(), "after_gloss": False,
                       "bracket": bracket, "uncertain": uncertain}
                segs.append(cur)
            continue
        if cur is None:
            continue
        if tok == "§G":
            cur["after_gloss"] = True
            continue
        if tok in ("und", "u.", "oder"):
            continue
        t = tok.rstrip(",;:")
        if t in NAME or t.rstrip(".") in NAME:
            cur["flags"].add("name")
            continue
        if cur["word"] is not None or cur["after_gloss"]:
            continue
        if CASE.match(t) and not re.match(r"^NA?Sg\.?$|^NSg\.?$", t):
            cur["flags"].add("oblique")
            cur["labels"].append(t)
            continue
        if t in ("in", "komp.", "Komp.", "z.B.", "vgl."):
            cur["flags"].add("compound" if t != "vgl." else "cf")
            cur["labels"].append(t)
            continue
        if t.endswith(".") and not t.startswith("*") and (t[:-1].isalpha() or "." in t[:-1]) and len(t) <= 9 \
                and not is_greek(t):
            cur["labels"].append(t)                   # Inf., Adv., Kompar., dial., usw., Subst., m., ...
            continue
        if t in ("PPP", "PPA", "Ptz", "VG"):
            cur["labels"].append(t)
            continue
        cur["word"] = t
    out = []
    for c in segs:
        drop = None
        w = c["word"]
        if c["uncertain"]:
            drop = "uncertain"
        elif c["bracket"]:
            drop = "remodelled"
        elif w is None:
            drop = "no_word"
        elif w.startswith("*") or "*" in w:
            drop = "reconstructed"
        elif "name" in c["flags"]:
            drop = "name"
        elif "compound" in c["flags"]:
            drop = "compound"
        elif "oblique" in c["flags"]:
            drop = "oblique_case"
        elif "cf" in c["flags"]:
            drop = "cf"
        for a in c["langs"]:
            out.append({"abbr": a, "word": w, "drop": drop})
    return out


# ---------------------------------------------------------------- normalization

def normalize_word(word: str, lang: str) -> tuple[str | None, str | None]:
    """→ (normalized form, None) or (None, reason it could not be normalized)."""
    w = word.replace("⟨", "").replace("⟩", "").replace("+", "").replace("†", "")
    w = w.rstrip(",;:·")
    w = re.sub(r"^\(-\)", "", w)                     # ai. (-)nibha-
    w = re.sub("[¹²³⁴⁵]", "", w)                    # NIL's homograph numbers: bhā́ma-¹
    if not w:
        return None, "empty"
    if w.startswith("-"):
        return None, "fragment"
    if "(" in w or ")" in w or "/" in w:
        return None, "optional_letters"
    if is_greek(w) and lang not in IRANIAN:      # Avestan, Sogdian ... write θ δ β γ themselves
        w = greek_translit(w)
    d = NFD(w)
    if lang == "Sanskrit":
        d = d.replace("̥", "̣").replace("ṁ", "ṃ")
        d = NFD(NFC(d).replace("ṁ", "ṃ"))
    elif lang == "Avestan":
        d = d.replace("ϑ", "θ")
    elif lang in ("Old Church Slavonic", "Church Slavonic", "Old East Slavic"):
        d = d.replace("ь", "ĭ").replace("ъ", "ŭ")
        d = NFD(d)
    elif lang == "Old Armenian":
        d = d.replace("ʿ", "ʻ").replace("'", "ʻ")
    elif lang == "Mycenaean Greek":
        d = d.replace("₂", "2").replace("₃", "3")
    w = NFC(d)
    if lang in HYPHEN_KEPT:
        w = w.rstrip("-")
    else:
        w = w.replace("-", "")
        w = w.replace(".", "")
    if not w:
        return None, "empty"
    if w[0].isupper():
        return None, "capitalized"
    return w, None


def main(write: bool = True, loose_daughters: bool = False, loose_formations: bool = False,
         independence: str = "full", min_families: int = bt.MIN_CONTROL_FAMILIES) -> dict:
    """The pre-registered build with the defaults. The keyword arguments only serve the exploratory
    sensitivity check (scripts/replication2_sensitivity.py), which never writes the data:
    `loose_daughters` keeps ?-marked and [-bracketed daughter words, `loose_formations` keeps
    ‡/**/ˣ and uncertain formations, `independence` is "full" (the rule above), "literal" (bare
    stem against first-run targets, up to accent and length) or "none"."""
    nil = bt.load(ROOT / "data/lexicon/nil.jsonl")
    lex = bt.load(ROOT / "data/lexicon/lexicon.jsonl")
    byid = {e["id"]: e for e in lex}
    prim = bt.load(D / "primary.jsonl")
    first = prim + bt.load(D / "secondary.jsonl")

    # model input inventory (as scripts/run_backtest.py Vocab: chars seen ≥ 2 times) and per language
    cc = collections.Counter(ch for r in prim for fs in r["inputs"].values() for f in fs for ch in NFD(f))
    vocab = {c for c, n in cc.items() if n >= 2}
    lang_chars = collections.defaultdict(set)
    for r in prim:
        for L, fs in r["inputs"].items():
            for f in fs:
                lang_chars[L].update(NFD(f))
    train_langs = collections.Counter(L for r in prim for L in r["inputs"])
    first_forms = {(L, f) for r in first for L, fs in r["inputs"].items() for f in fs}

    # independence keys
    def key(s: str) -> str:
        d = NFD(s.strip("-"))
        d = re.sub("[̀́̂̄̆͂]", "", d)
        return NFC(d)

    def keys_of(s: str) -> set[str]:
        k = key(s)
        out = {k}
        m = re.sub(r"(os|om|s|m)$", "", k)
        out.add(m)
        return out

    first_targets = {key(r["target"]) for r in first}
    first_keys = set()
    for r in first:
        first_keys |= keys_of(r["target"]) | keys_of(r["modern"])
    linked = set()          # (root_printed, printed) formations linked to a first-run row's lexicon entry
    for r in first:
        for b in (byid.get(r["id"]) or {}).get("nil") or []:
            if b.get("printed"):
                linked.add((b.get("root_printed"), b.get("printed")))
    root_link = {}
    for e in lex:
        if e["kind"] == "root":
            for b in e.get("nil") or []:
                root_link.setdefault(b["root_printed"], e["id"])

    stats = collections.Counter()
    word_drop = collections.Counter()
    norm_fail = collections.Counter()
    norm_fail_lang = collections.Counter()
    norm_tot_lang = collections.Counter()
    norm_fail_examples = collections.defaultdict(list)
    by_stem: dict[str, dict] = {}
    for rec in nil:
        for fm in rec["formations"]:
            stats["formations"] += 1
            if fm.get("marker") in ("‡", "**", "ˣ") and not loose_formations:
                stats[f"drop_marker_{fm['marker']}"] += 1
                continue
            if fm.get("uncertain") and not loose_formations:
                stats["drop_uncertain"] += 1
                continue
            if not fm.get("stem"):
                stats["drop_no_stem"] += 1
                continue
            stats["formations_kept_by_marker"] += 1
            inputs: dict[str, list[str]] = {}
            raw_words: dict[str, list[str]] = {}
            for ev in fm.get("evidence") or []:
                for seg in parse_evidence(ev):
                    a = seg["abbr"]
                    if a in EXCLUDED:
                        word_drop[f"lang_{EXCLUDED[a]}"] += 1
                        continue
                    if seg["drop"] in ("uncertain", "remodelled") and loose_daughters:
                        seg = {**seg, "drop": "reconstructed" if "*" in (seg["word"] or "*") else None}
                    if seg["drop"]:
                        word_drop[seg["drop"]] += 1
                        continue
                    L = ABBR[a]
                    norm_tot_lang[L] += 1
                    f, why = normalize_word(seg["word"], L)
                    if f is not None:
                        bad = [c for c in NFD(f) if c not in vocab or (L in lang_chars and c not in lang_chars[L])]
                        if bad:
                            f, why = None, "unseen_character"
                    if f is None:
                        norm_fail[why] += 1
                        norm_fail_lang[L] += 1
                        if len(norm_fail_examples[L]) < 8:
                            norm_fail_examples[L].append(seg["word"])
                        continue
                    if LAR.search(f):
                        word_drop["laryngeal_notation"] += 1
                        continue
                    if f not in inputs.setdefault(L, []):
                        inputs[L].append(f)
                        raw_words.setdefault(L, []).append(seg["word"])
            inputs = {L: v for L, v in inputs.items() if v}
            st = fm["stem"]
            g = by_stem.get(st)
            if g:
                stats["merged_same_stem"] += 1
                for L, fs in inputs.items():
                    for f in fs:
                        if f not in g["inputs"].setdefault(L, []):
                            g["inputs"][L].append(f)
                g["formations"].append(fm["printed"])
                g["linked"] |= (rec["root_printed"], fm["printed"]) in linked
                continue
            by_stem[st] = {"stem": st, "fm": fm, "rec": rec, "inputs": inputs, "raw": raw_words,
                           "formations": [fm["printed"]], "linked": (rec["root_printed"], fm["printed"]) in linked}

    rows, reasons = [], collections.Counter()
    for st, g in by_stem.items():
        inputs = {L: v for L, v in sorted(g["inputs"].items()) if v}
        if len(inputs) < 2:
            reasons["fewer_than_2_languages"] += 1
            continue
        try:
            target, effects = convert(st)
        except ValueError:
            reasons["transducer_failed"] += 1
            continue
        fk = keys_of(st) | keys_of(target)
        for f, _ in pnil.expected(g["fm"]):
            fk |= keys_of(f)
        if independence == "literal":
            if key(st) in first_targets:
                reasons["stem_matches_first_run_target_literal"] += 1
                continue
        elif independence == "none":
            pass
        elif g["linked"]:
            reasons["formation_linked_to_first_run_entry"] += 1
            continue
        elif fk & first_keys:
            reasons["stem_matches_first_run"] += 1
            continue
        rec = g["rec"]
        fam = root_link.get(rec["root_printed"]) or f"nil:{rec['root_printed']}"
        rows.append({"id": f"nil:{rec['root_printed']}|{g['fm']['printed']}", "root_id": fam,
                     "split": "replication2", "inputs": inputs, "target": target,
                     "effects": [{"kind": x.kind, "laryngeal": x.laryngeal, "offset": x.offset} for x in effects],
                     "modern": st, "hittite": None, "nil_formations": g["formations"],
                     "nil_root": rec["root_printed"], "nil_page": rec["page"],
                     "nil_words": {L: g["raw"].get(L, []) for L in inputs}})
    # contamination scan per language (rate) on the kept forms
    tot, bad = collections.Counter(), collections.Counter()
    for r in rows:
        for L, fs in r["inputs"].items():
            for f in fs:
                tot[L] += 1
                bad[L] += bool(LAR.search(f))
    contaminated = sorted(L for L in tot if bad[L] / tot[L] > CONTAMINATION_RATE)
    assert not contaminated, contaminated
    seen = collections.Counter(r["id"] for r in rows)
    assert max(seen.values(), default=1) == 1

    # power check from the data alone (no model): exact strata, 3-family rule
    words = [bt.Word(r["id"], bt.family(r), bt.segments(r["target"]), bt.effect_slots(r)) for r in rows]
    matched = bt.match(words, "exact", min_families)
    with_ctl = [x for x in matched if x["controls"]]
    per_kind = {k: {"effect_slots": sum(k in x["kinds"] for x in matched),
                    "matched": sum(k in x["kinds"] for x in with_ctl),
                    "matched_families": len({words[x["word"]].family for x in with_ctl if k in x["kinds"]})}
                for k in bt.KINDS}
    train_units = {u for r in prim for u in bt.segments(r["target"])}
    oov = collections.Counter(u for w in words for u in w.units if u not in train_units)
    n_words = sum(norm_tot_lang.values())
    n_fail = sum(norm_fail.values())
    meta = {
        "rules": __doc__.split("Rules (fixed before the data was built):")[1].split("Writes")[0].strip(),
        "formation_filter": dict(stats),
        "daughter_words_dropped_before_normalization": dict(word_drop),
        "words_to_normalize": n_words,
        "words_not_normalized": n_fail,
        "not_normalized_share": n_fail / n_words if n_words else None,
        "not_normalized_by_reason": dict(norm_fail),
        "not_normalized_by_language": {L: [norm_fail_lang[L], norm_tot_lang[L]]
                                        for L in sorted(norm_tot_lang, key=lambda L: -norm_tot_lang[L])},
        "not_normalized_examples": dict(norm_fail_examples),
        "caveat_over_20pct": bool(n_words and n_fail / n_words > 0.20),
        "set_filter": dict(reasons),
        "contaminated_languages": contaminated,
        "sets": len(rows),
        "sets_with_effect": sum(1 for r in rows if r["effects"]),
        "families": len({bt.family(r) for r in rows}),
        "families_lexicon_root": len({bt.family(r) for r in rows if not bt.family(r).startswith("nil:")}),
        "by_language": dict(collections.Counter(L for r in rows for L in r["inputs"]).most_common()),
        "languages_not_in_training": sorted({L for r in rows for L in r["inputs"] if train_langs[L] < 3}),
        "languages_per_set": dict(sorted(collections.Counter(len(r["inputs"]) for r in rows).items())),
        "sets_sharing_an_input_form_with_first_run": sum(
            any((L, f) in first_forms for L, fs in r["inputs"].items() for f in fs) for r in rows),
        "effect_slots": len(matched),
        "effect_slots_exact_matched": len(with_ctl),
        "matched_families": len({words[x["word"]].family for x in with_ctl}),
        "per_kind": per_kind,
        "min_slots_rule": 150,
        "powered": len(with_ctl) >= 150,
        "target_units_outside_training_vocab": dict(oov),
    }
    if not write:
        return meta
    (D / "replication2.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    (D / "replication2_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps({k: v for k, v in meta.items() if k not in ("rules", "not_normalized_examples")},
                     ensure_ascii=False, indent=1))
    return meta


def check_greek() -> float:
    """The transliterator against the lexicon's Greek reflexes that carry both script and romanization
    (breves dropped, as the first run's inputs almost never write them): share identical."""
    n = ok = 0
    for e in bt.load(ROOT / "data/lexicon/lexicon.jsonl"):
        for x in e.get("reflexes", {}).get("Ancient Greek", []):
            f, r = x.get("form"), x.get("roman")
            if f and r and is_greek(f):
                n += 1
                ok += greek_translit(f) == NFC(NFD(r).replace(BREVE, "")).lower()
    print(f"Greek transliteration: {ok}/{n} identical ({ok / n:.1%})")
    return ok / n


if __name__ == "__main__":
    if "--check-greek" in sys.argv:
        check_greek()
    else:
        main()
    sys.exit(0)
