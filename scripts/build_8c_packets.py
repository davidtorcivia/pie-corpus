#!/usr/bin/env python3
"""Phase 8c (reader-agent parallel discovery): seeds, packets, reader
assignment and the blinding key, as pre-registered in
docs/research/8c-preregistration.md (Design 1-4).

  uv run python -I scripts/build_8c_packets.py [--cache PATH]

1. Seeds. Each theme is an English concept list (THEMES, frozen here). A
   lexicon entry (any kind but affix) is a seed when one of its gloss senses
   contains a concept as whole words (plural/past/-ing forms of the last
   word allowed; senses with an exclusion phrase are skipped). Its seed root
   is its root_id (else its own id). Written to data/research/8c/seeds.json
   with the gloss sense that matched.
2. Passages. Per corpus the round-3 counting unit (RV pada, Homer line, DCS
   sentence, ...); a passage is that unit with one unit of context either
   side, inside the same text (hymn, book, poem, tablet). The count of
   distinct seed roots is taken on the core unit (content words, round-3
   lemma -> PIE mapping collapsed to root groups); a passage qualifies with
   >= 2. Per branch and theme: exact repeats (same corpus, same content
   lemmas: Hittite duplicates, RV refrains) are kept once; a branch with < 5
   qualifying passages is omitted; else the top 30 by count (ties in seeded
   random order) and 6 random others, never two passages whose cores are
   adjacent units. Passage order within a block is shuffled (seeded).
3. Packets. 16 real (one theme, all its branches) and 8 decoys: each decoy
   copies the branch set of a real packet (one drawn from each consecutive
   pair of real packets sorted by size, so sizes match) and fills each
   branch with the block of a different theme (all themes distinct within
   the packet, no block used by two decoys). Ids P-xxxx are random.
4. Readers: 8 x 3 packets, one decoy and two real each (16/8 forces this
   for "no reader all-real or all-decoy"), and no reader sees the same
   block twice (a decoy block whose theme is one of the reader's real
   packets).

Gothic, OCS and Armenian Bible texts (PROIEL/TOROT) are not loaded. Nothing
under raw/ is executed; files are read as text. Daughter text is written
only into the packets; each passage carries its corpus licence, and NC/ND
or unchecked sources are flagged research_only.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import pickle
import random
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "research" / "8c"
KEY = ROOT / "data" / "audits" / "keys" / "8c-key.json"
KEY_CHECK = ROOT / "data" / "audits" / "keys" / "8c-build-check.json"
MAPPING_DIR = ROOT / "data" / "research" / "formulas" / "mapping"
SEED = 0
HEADER = "Passages from several Indo-European traditions"
TOP, EXTRA, MIN_Q, MIN_ROOTS = 30, 6, 5, 2
N_DECOYS, N_READERS, PER_READER = 8, 8, 3

# ---------------------------------------------------------------- themes (frozen concept lists)
# (number, name, concepts, exclusions); a concept is one word or a phrase.

THEMES = [
    (1, "slaying a serpent or monster",
     ["serpent", "snake", "dragon", "worm", "monster", "slay", "slew", "slain", "kill", "smite", "smote", "strike",
      "struck", "overcome", "conquer", "hero", "club", "mace", "cudgel", "poison", "venom", "coil"], []),
    (2, "cattle raid and recovery",
     ["cattle", "cow", "kine", "ox", "oxen", "bull", "steer", "heifer", "calf", "herd", "livestock", "steal",
      "stole", "stolen", "thief", "theft", "rob", "robber", "booty", "plunder", "spoil", "raid", "rustle",
      "enclosure", "stall", "pen", "rescue", "recover", "drive away"], ["drive away evil"]),
    (3, "funeral and the road of the dead",
     ["die", "dying", "dead", "death", "corpse", "grave", "bury", "burial", "tomb", "funeral", "pyre", "mourn",
      "lament", "weep", "wept", "wail", "soul", "ghost", "shade", "underworld", "ancestor", "forefather", "bone",
      "ashes", "road", "path", "ferry", "perish", "decease"], []),
    (4, "oath and its breaking",
     ["oath", "swear", "swore", "sworn", "perjury", "pledge", "promise", "vow", "faith", "trust", "truth",
      "true", "deceive", "deceit", "deception", "betray", "treachery", "false", "falsehood", "treaty",
      "covenant", "witness", "guarantee", "curse", "guilt", "guilty", "punish", "punishment", "avenge",
      "vengeance"], ["true to life"]),
    (5, "kindling and praising fire",
     ["fire", "flame", "burn", "burnt", "kindle", "blaze", "glow", "smoke", "ember", "coal", "spark", "hearth",
      "altar", "firewood", "fuel", "sacrifice", "offering", "oblation", "worship", "praise", "invoke", "priest",
      "ghee", "melted butter", "butter"], []),
    (6, "the horse and the chariot",
     ["horse", "mare", "stallion", "foal", "steed", "colt", "chariot", "charioteer", "wagon", "cart", "wheel",
      "axle", "nave", "yoke", "harness", "rein", "bridle", "whip", "hoof", "ride", "rode", "rider", "drive",
      "drove", "driven", "driver", "team", "race", "gallop"], ["drive away"]),
    (7, "Sky and Earth as parents",
     ["sky", "heaven", "heavens", "firmament", "earth", "ground", "soil", "land", "world", "father", "mother",
      "parent", "parents", "beget", "begot", "begotten", "give birth", "bear children", "offspring", "progeny",
      "broad", "wide", "vast"], []),
    (8, "the dawn",
     ["dawn", "morning", "daybreak", "day", "daylight", "light", "shine", "shone", "bright", "brightness",
      "gleam", "glitter", "glimmer", "red", "reddish", "ruddy", "awake", "wake", "awaken", "early", "east",
      "sunrise"], ["not heavy", "in weight", "light weight"]),
    (9, "the sun's course",
     ["sun", "sunlight", "sunshine", "sunset", "eye", "wheel", "course", "path", "road", "travel", "traverse",
      "journey", "wander", "cross", "rise", "rose", "risen", "ascend", "descend", "revolve", "circle",
      "west", "east", "heat"], ["of course", "cross-reference"]),
    (10, "healing and binding charms",
     ["heal", "healer", "healing", "cure", "physician", "medicine", "remedy", "herb", "plant", "illness",
      "sickness", "disease", "sick", "ill", "wound", "injury", "pain", "fever", "blood", "joint", "limb",
      "sinew", "marrow", "bind", "bound", "tie", "fetter", "charm", "spell", "magic", "sorcery", "whole",
      "healthy"], []),
    (11, "the poet and his craft",
     ["poet", "poem", "poetry", "song", "sing", "sang", "sung", "singer", "hymn", "chant", "praise", "word",
      "speech", "speak", "voice", "verse", "craft", "weave", "wove", "woven", "fashion", "carpenter",
      "thought", "think", "mind", "inspiration", "seer", "wise", "wisdom", "fame", "famous", "glory",
      "renown", "hear", "heard"], []),
    (12, "gift and counter-gift",
     ["give", "gave", "given", "gift", "bestow", "grant", "receive", "share", "portion", "lot",
      "wealth", "riches", "goods", "treasure", "reward", "pay", "payment", "price", "exchange", "return",
      "repay", "generous", "bounty", "distribute", "allot"], ["give birth", "given birth", "give up", "give advice", "give a sign", "pay attention",
      "return home"]),
    (13, "guest and host",
     ["guest", "host", "stranger", "foreigner", "friend", "friendship", "house", "home", "household",
      "dwelling", "hall", "door", "welcome", "hospitality", "lodge", "entertain", "shelter", "master of the house",
      "hearth"], []),
    (14, "battle and the warrior's fury",
     ["battle", "war", "fight", "fought", "warrior", "army", "troop", "enemy", "foe", "spear", "sword",
      "shield", "bow", "arrow", "helmet", "weapon", "fury", "furious", "rage", "anger", "angry", "wrath",
      "frenzy", "courage", "brave", "might", "mighty", "strength", "valour", "victory", "attack", "slaughter"],
     ["bow down", "to bow", "bow the head"]),
    (15, "drinking and feasting",
     ["drink", "drank", "drunk", "intoxicate", "intoxicated", "intoxicating", "mead", "wine", "beer", "ale",
      "milk", "honey", "cup", "bowl", "vessel", "pour", "poured", "feast", "banquet", "eat", "ate", "eaten",
      "food", "meal", "meat", "sate", "satiate", "satiated", "thirst", "hunger", "sweet"], []),
    (16, "rain, storm and thunder",
     ["rain", "storm", "thunder", "lightning", "thunderbolt", "cloud", "wind", "hail", "snow", "flood",
      "shower", "drizzle", "roar", "roaring", "blow", "blew", "gust", "tempest", "wet", "moisten"],
     ["blow of", "a blow", "wind around", "to wind", "bend"]),
]

_GW = re.compile(r"[a-z]+")


def gloss_words(s: str) -> list[str]:
    return _GW.findall(s.lower())


def word_matches(tok: str, w: str) -> bool:
    """Whole-word match allowing -s/-es/-ed/-d/-ing (and -e → -ing, -y → -ies)."""
    if tok == w:
        return True
    if tok in (w + "s", w + "es", w + "ed", w + "ing"):
        return True
    if w.endswith("e") and tok in (w + "d", w[:-1] + "ing"):
        return True
    return w.endswith("y") and tok in (w[:-1] + "ies", w[:-1] + "ied")


def phrase_in(toks: list[str], phrase: str) -> bool:
    pw = gloss_words(phrase)
    n = len(pw)
    for i in range(len(toks) - n + 1):
        if toks[i:i + n - 1] == pw[:-1] and word_matches(toks[i + n - 1], pw[-1]):
            return True
    return False


def group_of(e: dict) -> str:
    return e.get("root_id") or e["id"]


def match_seeds(lexicon: list[dict], themes=THEMES) -> dict:
    """theme number → {"name", "concepts", "seeds": [{id, form, root, gloss, concept}], "roots": [...]}."""
    out = {}
    for num, name, concepts, excl in themes:
        seeds = []
        for e in lexicon:
            if e.get("kind") == "affix":
                continue
            hit = None
            for sense in e.get("meaning") or []:
                toks = gloss_words(sense)
                low = " ".join(toks)
                if any(" ".join(gloss_words(x)) in low for x in excl):
                    continue
                c = next((c for c in concepts if phrase_in(toks, c)), None)
                if c:
                    hit = (sense, c)
                    break
            if hit:
                seeds.append({"id": e["id"], "form": e.get("form", ""), "root": group_of(e), "gloss": hit[0],
                              "concept": hit[1]})
        seeds.sort(key=lambda s: s["id"])
        out[num] = {"name": name, "concepts": list(concepts), "exclusions": list(excl), "seeds": seeds,
                    "roots": sorted({s["root"] for s in seeds})}
    return out


# ---------------------------------------------------------------- corpora

BRANCHES = ("Indo-Iranian", "Greek", "Germanic", "Anatolian", "Italic", "Baltic", "Celtic")
CORPORA = {   # corpus → (branch, label, default licence, research_only)
    "rv": ("Indo-Iranian", "Rigveda (VedaWeb, Zurich annotation surface forms)",
           "CC BY 4.0 (VedaWeb Zurich annotation; the NC text layers are not used)", False),
    "av": ("Indo-Iranian", "Atharvaveda Śaunaka/Paippalāda (DCS)", "CC BY 4.0 (DCS)", False),
    "ae": ("Indo-Iranian", "Avesta (CAB Linguistic Corpus)", "CC BY-NC-SA 4.0 (CAB): non-commercial", True),
    "hom": ("Greek", "Homer (Perseus AGDT)", "CC BY-SA 3.0 (Perseus AGDT)", False),
    "grp": ("Greek", "Greek poetry to 400 BC (GLAUx)", None, None),
    "non": ("Germanic", "Poetic Edda (Finnur Jónsson 1926, OCR)", "Public domain", False),
    "ang": ("Germanic", "Old English poetry (Beowulf, Gutenberg; Grein 1857-58, OCR)", "Public domain", False),
    "hit": ("Anatolian", "Hittite (TLHdig)", "CC BY 4.0 (TLHdig)", False),
    "lat": ("Italic", "Latin (LASLA: Plautus, Lucretius, Catullus, Cato)", "LASLA: non-commercial", True),
    "xum": ("Italic", "Umbrian, Iguvine Tables (Buck 1904, OCR)", "Public domain (Buck 1904)", False),
    "lv": ("Baltic", "Latvian dainas (quotations in a book on the dainas, OCR)",
           "Folk-song quotations from an OCR'd book; copyright of the edition not checked", True),
    "sga": ("Celtic", "Old Irish glosses (UD)", None, None),
}
GLAUX_FREE = ("CC BY 4.0", "CC BY-SA 4.0")


@dataclass
class Unit:
    corpus: str
    key: str
    locus: str
    book: str
    text: str
    words: list = field(default_factory=list)    # content words: (form, lemma, lex ids tuple)
    groups: frozenset = frozenset()
    licence: str = ""
    research_only: bool = False
    pid: str = ""


def _units_from_tokens(corpus, toks, unit, book_of, surfaces, mapping, licence_of):
    """Tokens → ordered Units. mapping: lemma → lex ids; gmap applied by caller via `groups`."""
    order, by = [], {}
    for t, s in zip(toks, surfaces):
        k = t.units[unit]
        u = by.get(k)
        if u is None:
            lic, ro = licence_of(t)
            u = by[k] = Unit(corpus, k, t.locus, book_of(t), "", [], frozenset(), lic, ro)
            u._forms = []
            order.append(u)
        u._forms.append(s)
        if t.content:
            u.words.append((s, t.lemma, tuple(sorted(mapping.get(t.lemma, ())))))
    for u in order:
        u.text = " ".join(x for x in u._forms if x)
        del u._forms
    return order


def _default_licence(corpus):
    _, _, lic, ro = CORPORA[corpus]
    return lambda t: (lic, ro)


def _table(corpus: str) -> dict:
    """A round-3 mapping table, with the mapping errata applied (idempotent on regenerated tables)."""
    from pie import formula_search_multi as fm
    out = {}
    for line in (MAPPING_DIR / f"{corpus}.jsonl").read_text("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["lemma"]] = tuple(r["lex_id"])
    return fm.apply_table_overrides(corpus, out)


def _sga_surfaces(files) -> tuple[list[str], dict]:
    """Forms in load_conllu_simple's token order, and sentence key → '# text'."""
    forms, texts = [], {}
    for fn in files:
        sent = None
        for line in fn.read_text("utf-8").splitlines():
            if line.startswith("# sent_id"):
                sent = line.split("=", 1)[1].strip()
            elif line.startswith("# text") and "=" in line:
                texts[f"{fn.stem}.{sent}"] = line.split("=", 1)[1].strip()
            elif line and not line.startswith("#"):
                c = line.split("\t")
                if len(c) < 10 or "-" in c[0] or c[2] in ("_", ""):
                    continue
                forms.append(c[1])
    return forms, texts


def _hit_w_text(inner: str) -> str:
    s = re.sub(r"<d>(.*?)</d>", r"{\1}", inner)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def _hit_lines(fm, root: Path):
    """Every Hittite-language line in load_hittite's order: key → (locus, book, text), and the
    surface of each lemmatized word in loader token order."""
    lines, surfaces = {}, []
    for fn in sorted((root / fm.HIT_DIR).glob("*/*.xml")):
        text = fn.read_text("utf-8", errors="replace")
        body = text.split("<body>", 1)[-1]
        cur = None
        for piece in re.split(r"(<lb [^>]*>|<parsep[^>]*>)", body):
            if piece.startswith("<lb "):
                m = fm._HIT_LB.search(piece)
                lg = re.search(r'lg="([^"]*)"', piece)
                cur = (m[1], m[2]) if m and (not lg or lg[1] == "Hit") else None
                if cur:
                    key = f"{fn.stem}|{cur[1]}"
                    lines.setdefault(key, [f"{cur[0]} {cur[1]}", fn.stem, []])
                continue
            if piece.startswith("<parsep") or not cur:
                continue
            key = f"{fn.stem}|{cur[1]}"
            for wm in fm._HIT_W.finditer(piece):         # the loader's own word pattern
                attrs = wm[1]
                end = piece.find("</w>", wm.end())
                inner = "" if attrs.endswith("/") or end < 0 else piece[wm.end():end]
                a = dict(re.findall(r'([\w:]+)="([^"]*)"', attrs))
                disp = _hit_w_text(inner)
                if disp:
                    lines[key][2].append(disp)
                if fm.hit_lemma(a):
                    surfaces.append(disp)
    return lines, surfaces


def load_units(root: Path = ROOT, log=print) -> dict[str, list[Unit]]:
    """All corpora as ordered Units with content words mapped to lexicon ids (round-3 mapping)."""
    from pie import formula_search as fs
    from pie import formula_search_multi as fm

    lex = fs.load_jsonl(root / "data/lexicon/lexicon.jsonl")
    gmap = fs.group_map(lex)
    out: dict[str, list[Unit]] = {}

    # rv, hom, lat: round-2/3 mapping (kaikki links with pseudo ids, round-1 rules as backoff), as in Env
    rv, hom, lat = fs.load_rv(root), fs.load_homer(root), fs.load_latin(root)
    maps = {}
    for c, toks, lang, r1 in (("rv", rv, "sa", fs.build_rv_mapping), ("hom", hom, "grc", fs.build_homer_mapping),
                              ("lat", lat, "la", fs.build_latin_mapping)):
        m = fs.build_kaikki_mapping(lang, lex, toks, r1(lex, toks), root=root, pseudo=True)
        m = fm.apply_lemma_overrides(c, m, gmap, root=root)      # mapping errata
        maps[c] = {k: tuple(v) for k, v in m.lemma_lex.items()}
    out["rv"] = _units_from_tokens("rv", rv, "pada", lambda t: t.units["hymn"], [t.surface for t in rv], maps["rv"],
                                   _default_licence("rv"))
    out["hom"] = _units_from_tokens("hom", hom, "line", lambda t: t.units["book"], [t.surface for t in hom],
                                    maps["hom"], _default_licence("hom"))
    out["lat"] = _units_from_tokens("lat", lat, "line", lambda t: t.units["book"], [t.surface for t in lat],
                                    maps["lat"], _default_licence("lat"))
    log("rv/hom/lat loaded")

    # lemmatized corpora with round-3 tables
    av = fm.load_dcs(texts=fm.DCS_VEDIC[:2], root=root)          # the two Atharvaveda recensions only
    out["av"] = _units_from_tokens("av", av, "sentence", lambda t: t.units["chapter"], [t.surface for t in av],
                                   _table("av"), _default_licence("av"))
    sel = fm.glaux_selection(root)
    glic = {r["TLG"]: r["SOURCE_LICENSE"] for r in sel}
    grp = [t for t in fm.load_glaux(sel, root=root) if not t.units["line"].endswith(":?")]
    out["grp"] = _units_from_tokens(
        "grp", grp, "line", lambda t: t.units["book"], [t.surface for t in grp], _table("grp"),
        lambda t: (f"GLAUx; source text licence: {glic.get(t.units['book'], '?')}",
                   glic.get(t.units["book"]) not in GLAUX_FREE))
    sga_files = sorted((root / fm.UD_SGA).glob("*/*.conllu"))
    sga = fm.load_conllu_simple(sga_files, "sga")
    forms, texts = _sga_surfaces(sga_files)
    assert len(forms) == len(sga)
    sga_lic = lambda t: (("CC BY-NC-SA 4.0 (UD Old_Irish-DipSGG): non-commercial", True) if "dipsgg" in t.units["book"]
                         else ("CC BY-SA 4.0 (UD Old_Irish-DipWBG)", False))
    out["sga"] = _units_from_tokens("sga", sga, "sentence", lambda t: t.units["book"], forms, _table("sga"), sga_lic)
    for u in out["sga"]:
        u.text = texts.get(u.key, u.text)
    hit = fm.load_hittite(root)
    hlines, hsurf = _hit_lines(fm, root)
    assert len(hsurf) == len(hit)
    hu = {u.key: u for u in _units_from_tokens("hit", hit, "line", lambda t: t.units["line"].split("|")[0], hsurf,
                                               _table("hit"), _default_licence("hit"))}
    out["hit"] = []
    lic, ro = CORPORA["hit"][2], CORPORA["hit"][3]
    for k, (locus, book, ws) in hlines.items():      # every Hittite line, lemmatized or not, in document order
        u = hu.get(k) or Unit("hit", k, locus, book, "", [], frozenset(), lic, ro)
        u.text = " ".join(ws)
        out["hit"].append(u)
    log("av/grp/sga/hit loaded")

    # unlemmatized corpora: the round-3 lemmatizers, then the round-3 tables
    idx = fs.PieIndex(lex)
    langs = ("non", "ang", "lv", "xum", "ae")
    protos = fm.ProtoDB(root=root, want_desc=[c for L in langs for c in fm.LANGS[L].desc_codes])
    lm = {L: fm.build_lang_mapping(L, lex, protos, root=root, idx=idx) for L in langs}
    ang_lemz = fm.FormLemmatizer(lm["ang"])
    lat_forms = {fs.lat_key(t.surface) for t in lat}
    sources = {
        "non": (fm.edda_lines(root), fm.FormLemmatizer(lm["non"], fallbacks=(fm.non_clitic_variants,)), "line"),
        "ang": (fm.beowulf_lines(root) + fm.grein_lines(lambda w: ang_lemz(fm.grein_normalize(w)), root), ang_lemz,
                "line"),
        "lv": (fm.dainas_units(root), fm.FormLemmatizer(lm["lv"], fallbacks=(fm.lv_diminutive_variants,)), "song"),
        "xum": (fm.umbrian_lines(lat_forms, root), fm.FormLemmatizer(lm["xum"]), "line"),
        "ae": (fm.avesta_units(root), fm.AvestanLemmatizer(lm["ae"], {}), "ab"),
    }
    for c, (units, lemz, unit) in sources.items():
        toks = fm.text_tokens(c, units, lemz, lm[c].is_content)
        surf = [w for _, _, text in units for w in (fm._WORDS.findall(text) if isinstance(text, str) else text)]
        assert len(surf) == len(toks)
        table = _table(c)
        _, recs = fm.multi_lemma_mapping(toks, lm[c], gmap)
        recs = fm.apply_rec_overrides(c, recs)
        same = {k: tuple(sorted(v.ids)) for k, v in recs.items()} == {k: tuple(sorted(v)) for k, v in table.items()}
        log(f"{c}: lemmatizer mapping {'matches' if same else 'DIFFERS FROM'} the round-3 table")
        out[c] = _units_from_tokens(c, toks, unit, lambda t: t.units["book"], surf, table, _default_licence(c))
        texts = {u[unit]: (text if isinstance(text, str) else " ".join(text)) for _, u, text in units}
        for u in out[c]:
            u.text = texts.get(u.key, u.text)
    log("non/ang/lv/xum/ae loaded")

    by_id = {e["id"]: e for e in lex}
    for c, us in out.items():
        for u in us:
            u.groups = frozenset(gmap.get(x, x) for _, _, ids in u.words for x in ids)
    assign_pids(out)
    return out, by_id


def assign_pids(units: dict[str, list[Unit]]) -> None:
    """Stable passage id 'corpus:locus'; the unit key is appended where a locus repeats."""
    for c, us in units.items():
        n = collections.Counter(u.locus for u in us)
        for u in us:
            u.pid = f"{c}:{u.locus}" if n[u.locus] == 1 else f"{c}:{u.locus} [{u.key}]"


# ---------------------------------------------------------------- selection

def neighbours(us: list[Unit], i: int) -> tuple[Unit | None, Unit | None]:
    prev = us[i - 1] if i > 0 and us[i - 1].book == us[i].book else None
    nxt = us[i + 1] if i + 1 < len(us) and us[i + 1].book == us[i].book else None
    return prev, nxt


def qualifying(units: dict[str, list[Unit]], corpora, roots: set, min_roots: int = MIN_ROOTS) -> list[tuple]:
    """(score, corpus, index) of core units with ≥ min_roots distinct seed roots; exact repeats
    (same corpus and content lemmas) kept once, first in document order."""
    out, seen = [], set()
    for c in corpora:
        for i, u in enumerate(units.get(c, [])):
            s = len(u.groups & roots)
            if s < min_roots:
                continue
            dup = (c, tuple(lem for _, lem, _ in u.words))
            if dup in seen:
                continue
            seen.add(dup)
            out.append((s, c, i))
    return out


def select_block(cands: list[tuple], rng: random.Random, top: int = TOP, extra: int = EXTRA,
                 min_q: int = MIN_Q) -> list[tuple] | None:
    """Top `top` by score (ties in random order) plus `extra` random others, no two with adjacent
    cores; None if fewer than min_q candidates."""
    if len(cands) < min_q:
        return None
    keyed = [(-s, rng.random(), (s, c, i)) for s, c, i in cands]
    keyed.sort()
    taken: set = set()

    def free(c, i):
        return not ({(c, i - 1), (c, i), (c, i + 1)} & taken)

    chosen = []
    rest = []
    for _, _, (s, c, i) in keyed:
        if len(chosen) < top and free(c, i):
            chosen.append((s, c, i))
            taken.add((c, i))
        else:
            rest.append((s, c, i))
    rest.sort(key=lambda x: (x[1], x[2]))
    rng.shuffle(rest)
    for s, c, i in rest:
        if len(chosen) >= top + extra:
            break
        if free(c, i):
            chosen.append((s, c, i))
            taken.add((c, i))
    return chosen


# ---------------------------------------------------------------- packet rendering

def _etymon(ids, by_id, qualification=None):
    if not ids:
        return "unmapped"
    out = []
    for x in ids:
        e = by_id.get(x)
        if e is None:      # pseudo id: an etymon the lexicon lacks
            out.append({"id": x, "form": x.split(":", 1)[-1], "gloss": "(not in the lexicon)"})
            continue
        gloss = "; ".join(e.get("meaning") or [])
        rid = e.get("root_id")
        d = {"id": x, "form": e.get("form", "")}
        if rid and rid != x:
            d["root"] = rid
            if not gloss and rid in by_id:
                gloss = "root: " + "; ".join(by_id[rid].get("meaning") or [])
        d["gloss"] = gloss
        out.append(d)
    if qualification is not None:
        for e in out:
            e["qualification"] = dict(qualification)
    return out


def _line(u: Unit, role: str, by_id) -> dict:
    return {"role": role, "locus": u.locus, "text": u.text,
            "words": [{"form": f, "lemma": lem,
                       "etymon": _etymon(ids, by_id, getattr(u, "qualifications", {}).get(lem))}
                      for f, lem, ids in u.words]}


def render_passage(units, c: str, i: int, by_id) -> dict:
    us = units[c]
    u = us[i]
    prev, nxt = neighbours(us, i)
    lines = ([_line(prev, "context before", by_id)] if prev else []) + [_line(u, "passage", by_id)] + \
            ([_line(nxt, "context after", by_id)] if nxt else [])
    return {"id": u.pid, "corpus": CORPORA[c][1], "locus": u.locus, "licence": u.licence,
            "research_only": u.research_only, "lines": lines}


FORMAT_NOTE = ("Each block holds passages from one branch. A passage is a verse line, stanza or sentence (role "
               "'passage') with one unit of context on either side where the text has one. For every content word: "
               "its form, its corpus lemma, and the PIE lexicon etymon it maps to (id, reconstructed form, the "
               "lexicon's gloss; 'unmapped' if none). Mappings are automatic and can be wrong. Cite passages by "
               "their 'id'. Passages marked research_only come from sources whose licence forbids commercial use "
               "or has not been checked.")


def make_packet(pid: str, blocks: dict, units, by_id) -> dict:
    """blocks: branch → list of (score, corpus, index), already in display order."""
    out_blocks = []
    for b in BRANCHES:
        if b not in blocks:
            continue
        out_blocks.append({"branch": b, "passages": [render_passage(units, c, i, by_id) for _, c, i in blocks[b]]})
    ids = [p["id"] for bl in out_blocks for p in bl["passages"]]
    assert len(ids) == len(set(ids))
    return {"packet": pid, "header": HEADER, "format": FORMAT_NOTE,
            "branches": [bl["branch"] for bl in out_blocks], "passage_ids": ids, "blocks": out_blocks}


# ---------------------------------------------------------------- decoys, ids, readers

def make_decoys(real_blocks: dict, rng: random.Random, n: int = N_DECOYS) -> list[dict]:
    """real_blocks: theme → {branch → block}. Each decoy: branch → theme, copying the branch set of a
    template real packet (one per consecutive pair of real packets sorted by size), all themes
    distinct within the decoy, no (branch, theme) block used twice."""
    size = lambda t: (len(real_blocks[t]), sum(len(v) for v in real_blocks[t].values()), t)
    ordered = sorted(real_blocks, key=size)
    step = len(ordered) / n
    templates = [ordered[int(k * step) + rng.randrange(max(1, int((k + 1) * step) - int(k * step)))]
                 for k in range(n)]
    used: set = set()
    decoys = []
    for tmpl in templates:
        branches = [b for b in BRANCHES if b in real_blocks[tmpl]]
        for _ in range(1000):
            order = branches[:]
            rng.shuffle(order)
            got = _fill_decoy(order, real_blocks, used, rng)
            if got:
                break
        else:
            raise RuntimeError("no decoy assignment")
        used |= {(b, t) for b, t in got.items()}
        decoys.append({"template": tmpl, "themes": {b: got[b] for b in BRANCHES if b in got}})
    return decoys


def _fill_decoy(order, real_blocks, used, rng, chosen=None):
    chosen = chosen or {}
    if len(chosen) == len(order):
        return dict(chosen)
    b = order[len(chosen)]
    opts = sorted(t for t in real_blocks if b in real_blocks[t] and (b, t) not in used and t not in chosen.values())
    rng.shuffle(opts)
    for t in opts:
        chosen[b] = t
        r = _fill_decoy(order, real_blocks, used, rng, chosen)
        if r:
            return r
        del chosen[b]
    return None


def packet_ids(n: int, rng: random.Random) -> list[str]:
    ids: list[str] = []
    while len(ids) < n:
        x = f"P-{rng.randrange(16 ** 4):04x}"
        if x not in ids:
            ids.append(x)
    return ids


def assign_readers(kinds: dict, themes_of: dict, rng: random.Random, n_readers: int = N_READERS,
                   per: int = PER_READER) -> list[list[str]]:
    """kinds: id → 'real'|'decoy'; themes_of: id → set of themes. Each reader gets ≥ 1 of each kind
    (here: one decoy, two real) and no two packets of a reader share a theme."""
    real = sorted(i for i, k in kinds.items() if k == "real")
    dec = sorted(i for i, k in kinds.items() if k == "decoy")
    assert len(real) + len(dec) == n_readers * per and len(dec) == n_readers
    for _ in range(10000):
        rng.shuffle(dec)
        rng.shuffle(real)
        readers = [[d] for d in dec]
        if _fill_readers(readers, real[:], themes_of, per, rng):
            for r in readers:
                rng.shuffle(r)
            rng.shuffle(readers)
            return readers
    raise RuntimeError("no reader assignment")


def _fill_readers(readers, pool, themes_of, per, rng):
    slot = next((r for r in readers if len(r) < per), None)
    if slot is None:
        return True
    opts = [p for p in pool if all(not (themes_of[p] & themes_of[q]) for q in slot)]
    rng.shuffle(opts)
    for p in opts:
        slot.append(p)
        pool.remove(p)
        if _fill_readers(readers, pool, themes_of, per, rng):
            return True
        pool.append(p)
        slot.pop()
    return False


# ---------------------------------------------------------------- build

def build(units, by_id, lexicon, seed: int = SEED, themes=THEMES) -> dict:
    """Everything except writing: seeds, blocks, packets, key, assignment, stats."""
    seeds = match_seeds(lexicon, themes)
    real_blocks: dict = {}
    qual_counts: dict = {}
    for num, *_ in themes:
        roots = set(seeds[num]["roots"])
        real_blocks[num] = {}
        for b in BRANCHES:
            cs = [c for c in CORPORA if CORPORA[c][0] == b]
            cands = qualifying(units, cs, roots)
            qual_counts[(num, b)] = len(cands)
            rng = random.Random(f"8c:{seed}:block:{num}:{b}")
            blk = select_block(cands, rng)
            if blk:
                rng.shuffle(blk)
                real_blocks[num][b] = blk
    rng = random.Random(f"8c:{seed}:packets")
    decoys = make_decoys(real_blocks, rng)
    ids = packet_ids(len(themes) + len(decoys), rng)
    specs = [("real", num, real_blocks[num], {num}) for num, *_ in themes] + \
            [("decoy", d["themes"], {b: real_blocks[t][b] for b, t in d["themes"].items()}, set(d["themes"].values()))
             for d in decoys]
    rng.shuffle(specs)
    packets, key, kinds, themes_of = {}, {}, {}, {}
    for pid, (kind, th, blocks, tset) in zip(ids, specs):
        packets[pid] = make_packet(pid, blocks, units, by_id)
        kinds[pid], themes_of[pid] = kind, tset
        names = {n: nm for n, nm, *_ in themes}
        key[pid] = ({"kind": "real", "theme": th, "theme_name": names[th]} if kind == "real" else
                    {"kind": "decoy", "themes": {b: t for b, t in th.items()},
                     "theme_names": {b: names[t] for b, t in th.items()}})
    readers = assign_readers(kinds, themes_of, rng)
    order = [p for r in readers for p in r]
    assignment = {"order": order,
                  "readers": [{"reader": f"R{k + 1}", "packets": r} for k, r in enumerate(readers)]}
    stats = {"packets": {pid: {"branches": len(p["blocks"]),
                               "passages": len(p["passage_ids"]),
                               "per_branch": {bl["branch"]: len(bl["passages"]) for bl in p["blocks"]}}
                         for pid, p in sorted(packets.items())},
             "themes": {num: {"seeds": len(seeds[num]["seeds"]), "seed_roots": len(seeds[num]["roots"])}
                        for num, *_ in themes},
             "qualifying": {num: {b: qual_counts[(num, b)] for b in BRANCHES} for num, *_ in themes}}
    return {"seeds": seeds, "packets": packets, "key": key, "assignment": assignment, "stats": stats,
            "kinds": kinds}


def balance(packets: dict, kinds: dict) -> dict:
    out = {}
    for k in ("real", "decoy"):
        ps = [packets[p] for p in packets if kinds[p] == k]
        out[k] = {"n": len(ps), "mean_passages": round(statistics.mean(len(p["passage_ids"]) for p in ps), 2),
                  "mean_branches": round(statistics.mean(len(p["blocks"]) for p in ps), 2),
                  "passages": sorted(len(p["passage_ids"]) for p in ps),
                  "branches": sorted(len(p["blocks"]) for p in ps)}
    r, d = out["real"], out["decoy"]
    out["rel_diff_passages"] = round(abs(r["mean_passages"] - d["mean_passages"]) / r["mean_passages"], 3)
    out["rel_diff_branches"] = round(abs(r["mean_branches"] - d["mean_branches"]) / r["mean_branches"], 3)
    out["balanced"] = out["rel_diff_passages"] <= 0.10 and out["rel_diff_branches"] <= 0.10
    return out


def dump_packet(p: dict) -> str:
    """Indented header, one passage per line (compact) to keep packets readable and small."""
    head = {k: v for k, v in p.items() if k != "blocks"}
    lines = ["{"]
    for k, v in head.items():
        lines.append(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},")
    lines.append(' "blocks": [')
    for bi, bl in enumerate(p["blocks"]):
        lines.append(f'  {{"branch": {json.dumps(bl["branch"], ensure_ascii=False)}, "passages": [')
        ps = bl["passages"]
        for pi, ps_ in enumerate(ps):
            lines.append("   " + json.dumps(ps_, ensure_ascii=False) + ("," if pi < len(ps) - 1 else ""))
        lines.append("  ]}" + ("," if bi < len(p["blocks"]) - 1 else ""))
    lines.append(" ]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write(res: dict, out_dir: Path = OUT, key_path: Path = KEY, check_path: Path = KEY_CHECK) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdir = out_dir / "packets"
    pdir.mkdir(exist_ok=True)
    for old in pdir.glob("P-*.json"):
        old.unlink()
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    seeds = {"note": "Phase 8c seed lexemes per theme (frozen with the packets; see "
                     "docs/research/8c-preregistration.md). Matched gloss sense and concept per seed.",
             "themes": {str(k): v for k, v in res["seeds"].items()}}
    (out_dir / "seeds.json").write_text(dump(seeds), "utf-8")
    for pid, p in res["packets"].items():
        text = dump_packet(p)
        assert json.loads(text) == p
        (pdir / f"{pid}.json").write_text(text, "utf-8")
    (out_dir / "assignment.json").write_text(dump(res["assignment"]), "utf-8")
    st = res["stats"]
    (out_dir / "stats.json").write_text(dump({"packets": st["packets"],
                                              "themes": {str(k): v for k, v in st["themes"].items()}}), "utf-8")
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(dump(res["key"]), "utf-8")
    check = {"size_balance": balance(res["packets"], res["kinds"]),
             "qualifying_passages_by_theme_and_branch": {str(k): v for k, v in st["qualifying"].items()}}
    check_path.write_text(dump(check), "utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, help="pickle of the loaded corpora (created if missing)")
    args = ap.parse_args()
    log = lambda *a: print(*a, file=sys.stderr, flush=True)
    if args.cache and args.cache.exists():
        units, by_id = pickle.loads(args.cache.read_bytes())
    else:
        units, by_id = load_units(ROOT, log)
        if args.cache:
            args.cache.write_bytes(pickle.dumps((units, by_id)))
    lexicon = [json.loads(x) for x in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines() if x]
    for c, us in units.items():
        log(f"{c}: {len(us)} units, {sum(len(u.words) for u in us)} content words")
    res = build(units, by_id, lexicon)
    write(res)
    b = balance(res["packets"], res["kinds"])
    log(f"packets {len(res['packets'])}; size balance: rel. diff passages {b['rel_diff_passages']}, "
        f"branches {b['rel_diff_branches']}, balanced={b['balanced']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
