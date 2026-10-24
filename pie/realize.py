"""Tier 3 realizer: a structured plan → PIE text, deterministically.

The LLM writes plans (English + lexemes + roles + verb features). It never
writes PIE. This module does everything that would otherwise let free-form
"Claude-PIE" back in: case from role, agreement from the head, verb person
and number from the subject, word order, clitic placement. Each form is the
engine's primary handbook form.

Plan (one sentence):
  {"english": "...",
   "clauses": [{"order": "SOV" | "VSO",           # VSO = verb-initial (narrative/emphasis)
                "conj": null | "kʷe" | "wē",       # "and" / "or" joining this clause to the previous one
                "neg": false,                      # ne before the verb (mē with imperative)
                "particle": null | "nu" | "ge" | "yod",  # nu "now, then"; -ge emphatic (enclitic); h₁yód "if, when"
                "break": false,                    # this clause starts a new sentence
                "question": false,                 # this clause's sentence ends in "?"
                "type": "verbal" | "nominal" | "np",  # see Clause types below; default verbal
                "case": "NOM",                     # np utterances only: the case of the NP (VOC for addresses)
                "slots": [
      {"lex_id": "pie-lex-…" | "closed:personal/1" | …,
       "role": "SUBJ|OBJ|IO|INS|LOC|ABL|POSS|VOC|PRED|GOAL|MOD|APPOS|NP|ADV|V",
       "num": "SG|DU|PL",                          # nominals; MOD, APPOS and V take it from their head/subject
       "head": null | <slot index>,                # MOD (adjective, demonstrative, POSS), APPOS → its noun
       "before": false,                            # APPOS: stand before the head instead of after it
       "enclitic": false,                          # pronoun slots: the enclitic form (moy, toy, …)
       "gender": null | "m|f|n",                   # pronoun slots used on their own (tod "it", kʷíd "what")
       "and": false,                               # -kʷe "and" after this word (X Y-kʷe = X and Y)
       "verb": {"tense": "PRS|PST|AOR|PRF", "mood": "IND|IMP|SBJV|OPT", "voice": "ACT|MID",
                "person": null | 1 | 2 | 3,       # person and number default to the subject's (3SG without one);
                "num": null | "SG|DU|PL"}}]}]}    # set them for pro-drop ("let us go": person 1, num PL, no SUBJ)

`check_plan` lists every problem; `realize` assumes a checked plan. `plan_warnings` lists likely problems that
do not block realization (a 3rd-person pronoun with no referent of its gender and number nearby).

Clause types. A clause has "type": "verbal" (the default, above: exactly one V slot), "nominal" or "np".
The realizer never inserts a copula: a clause without a V slot is realized without one.
  nominal  a verbless (nominal) sentence: SUBJ + PRED, no V slot. PRED is a noun or adjective in the
           nominative; an adjective agrees with the subject in gender and number (as with h₁ésti); a noun
           keeps its own gender and number. The subject must be overt (Fortson §8.17: in nominal sentences an
           overt pronoun subject is generally required, OPers. adam navama 'I (am) the ninth'). Other roles
           (VOC, IO, INS, LOC, ABL, ADV, POSS, MOD, APPOS) are allowed; OBJ and GOAL are not (no verb governs
           them). Order: topic first, predicate last (Lehmann 1974 §2.1.4, §4.3.1.a: Hitt. attaš aššuš 'the
           father (is) good', Ved. tváṃ váruṇa 'you (are) Varuṇa', OPers. adam Dārayavauš 'I (am) Darius'),
           i.e. SUBJ … PRED; "order": "VSO" puts the predicate first. "neg" puts ne directly before the
           predicate (Hitt. lē idāluš, Lehmann §4.3.1.a ex. 43). nu, ge, yod, conj, break, question as usual.
           Use it for generic, timeless statements, identifications and descriptions in the present (Vedic,
           Avestan, Old Persian, Hittite nominal sentences; Keydana 2018 §8: the copula is optional, omitted
           especially in the present). Use a verbal clause with h₁ésti for tense or mood (a past or a wish:
           Hittite cannot drop the copula in the past, Lehmann §2.1.4 after Friedrich), for emphasis
           (Lehmann §4.3.1.a: the verb may be added for emphasis, RV 4.30.1 … asti), and for existence
           ('there is a king').
  np       a bare noun phrase as a whole utterance: a title, an exclamation, an address, an epithet line
           in a catalogue ('sweet mead' = sweh₂dú médʰu). One or more slots with role "NP" (coordinated with
           "and") plus their MOD, POSS, APPOS (and participle deps); no V, SUBJ, OBJ or other clause roles,
           no neg. "case": "NOM" (default) | "VOC" (addresses) | any other case name; the NP slots and
           everything that agrees with them take it.
Apposition. A slot with role "APPOS" and "head": k is a noun phrase in apposition to slot k ('the horses,
  immortal ones', 'Dyēus, the father'; West 2007 p. 307: a god's name with honorific epithets in apposition).
  It takes its head's case and number; a noun keeps its own gender, an adjective (used as a noun) takes the
  head's gender unless the slot gives one. It may carry its own MOD/POSS/APPOS. It stands after its head's
  phrase; "before": true puts it before. Any nominal slot (SUBJ, OBJ, VOC, PRED, POSS, NP, APPOS …) can head
  an APPOS; a MOD cannot. Unlike MOD it is a separate phrase (Ringe 2017 §3.3.2: nouns in apposition are
  separate NPs), so an adjective there reads 'the immortal ones', not 'immortal'.

Compounds (pie/compound.py). A slot may hold a compound built from two lexemes:
  {"lex_id": "compound", "compound": {"first": F, "second": S, "type": "bahuvrihi" | "determinative"},
   "role": ..., "head": k, "gender": ...}
  bahuvrihi       a possessive adjective 'having (a) F S' (Fortson §6.82, Beekes 13.1.4, L&Y §122.2.6): MOD with a
                  head, PRED, or (with a gender) a noun role, exactly like an adjective. Default type.
  determinative   a noun 'F S' with S's gender and declension (Ved. rāja-putrá-, kr̥ṣṇa-śakuní-; L&Y §122.2.6,
                  Beekes viś-páti-): any noun role, not MOD.
F (first member):
  closed:prefix/h1su  *h₁su- 'good'     (Fortson §6.86, Ringe 2.4.1; Ved. su-, Gk εὐ-)      unaccented
  closed:prefix/dus   *dus- 'bad, ill'  (Ringe 2.4.1; Gk δυσ-, Ved. dus-)                   unaccented
  closed:prefix/n     privative *ń̥- 'un-, -less' (Fortson §7.25)                            accented
  closed:prefix/sm    *sm̥- 'one, same' (Fortson §7.18: Gk ἀ-δελφός)                         unaccented
  closed:numerals/2|3|4  *dwi- *tri- *kʷetru- (Fortson §7.18; L&Y)                            unaccented
  (pie-lex-h1su / pie-lex-dus / pie-lex-n are accepted for the prefixes; prefixes make bahuvrihis only)
  an adjective lex_id: thematic stem in -o- (néwo-), keeps its accent; u-stem in -u- (h₁wesu-; HeHḱu-, the
      lexicon's 'swift', i.e. *h₁ōḱu-), unaccented (L&Y's dominant Vedic pattern; West ch. 10 cites 1M-accented
      vásu-śravas-). Caland -ro- adjectives are rejected: their compound form is -i- (Fortson §6.87, Ringe
      2.4.2: h₂r̥ǵrós → h₂r̥ǵi-), which the engine does not build (Ved. ugrá-bāhu- keeps -ro-; the books differ).
  a noun lex_id: thematic (-o-) or i-/u-stem noun, its stem as is (Gk khrūsó-thronos, Ved. bāhú-ojas-).
S (second member, a noun lex_id):
  bahuvrihi: an s-stem neuter → the -es- adjective, common gender (Beekes 13.1.2: Gk εὐμενής, Ved. sumánas-;
      Gk εὐκλεής, Ved. suśrávas-, Illyr. Ves-cleves): m./f. nom. sg. *-ēs, acc. *-esm̥, gen. *-esos,
      n. *-es (pl. *-ēs or *-esh₂); h₁suḱléwēs, dusménēs, h₁wesuḱléwēs.
      A thematic noun → a thematic adjective -os/-eh₂/-om: h₁suh₁éḱwos (Ved. suáśva-, Gk εὔιππος; West ch. 4).
      Other stems are rejected: the books give no general rule (Fortson §6.83 on the o-grade of eu-pátōr).
  determinative: any usable noun; its paradigm is kept and the first member put in front.
Accent (bahuvrihi): the Basic Accentuation Principle (Kiparsky & Halle; L&Y §122.3.1–3.2): the leftmost
  inherently accented member wins and the other loses its accent; with no accent, the leftmost syllable.
  Unaccented h₁su-/dus-/numerals/u-stems → the second member's accent (Ved. suśrávas-, sumánas-, suáśva-,
  āśu-héṣas-): h₁suḱléwēs, dusménēs, HeHḱuh₁éḱwos. Accented privative or thematic stem → first-member
  accent, as L&Y reconstruct *pró-ḱlewes- and *h₂ugró-bʰeh₂ǵʰu- (Gk recessive klutó-toksos; Ringe's
  *ń̥gʷʰdʰsitos): ń̥h₁eḱwos, néwoh₁eḱwos. The suffix-accented s-stem (*-ḱlewḗs: Clackson *dus-m(e)n-és-, the
  productive Gk -ḗs, which L&Y call an innovation) and, for the privative, the second-member accent
  (lexical n̥mr̥tós, Ved. amṛ́ta-) are kept as alternative forms, so texts that write them validate.
Accent (determinative): the head keeps its accent and the first member loses its own (newodʰéǵʰōm).
The privative keeps its syllabic n̥ before a laryngeal (Beekes p. 84: Gk νήγρετος < *n̥-h₁gr-etos) and is n̥n- before a
  true vowel or i/u (L&Y *n̥(n)udro-), rejected before a syllabic r̥ l̥ m̥ n̥; dus- takes any onset; h₁su-, sm̥- and
  the numerals before a vocalic onset are rejected (no book gives the junction). Forms are written solid (h₁suḱléwēs).
The word's lex_id is "compound:<type>:<first>+<second>"; its gloss "good+fame". The validator indexes a plan's
  compounds with pie.validate.index_plan_compounds (same cells), called by realize_plans.py and build_tier2.py. Not supported: root-noun,
  r/n/i/u/eh₂-stem second members in bahuvrihis (*-pod-, eu-pátōr), consonant-stem first members (wiḱ-,
  déms-), verbal governing compounds (*ḱlewos-dʰeh₁-, vr̥tra-hán-), Caland -i-, nested compounds.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .compound import CompoundError, resolve as resolve_compound
from .morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj, decline_participle

ROOT = Path(__file__).resolve().parent.parent

# PRED: predicate nominal or adjective (nominative; an adjective agrees with the subject).
# Interrogative phrases are fronted. A prohibitive (neg + IMP) is mē + injunctive.
ROLE_CASE = {"SUBJ": "NOM", "PRED": "NOM", "OBJ": "ACC", "GOAL": "ACC", "IO": "DAT", "INS": "INS",
             "LOC": "LOC", "ABL": "ABL", "POSS": "GEN", "VOC": "VOC"}
NOMINAL_ROLES = set(ROLE_CASE) | {"MOD", "APPOS", "NP"}
ROLES = NOMINAL_ROLES | {"ADV", "V"}
CLAUSE_TYPES = ("verbal", "nominal", "np")
CASES = ("NOM", "VOC", "ACC", "GEN", "DAT", "INS", "LOC", "ABL")
# an np utterance holds only its NP slots and what attaches to them
NP_ROLES = {"NP", "MOD", "POSS", "APPOS"}
# Wackernagel enclitics: placed after the first word of the clause
ENCLITIC_PRONOUNS = {"moy", "toy", "me", "te", "nos", "wos", "soy", "se", "noh₃", "woh₃"}


@dataclass
class Word:
    form: str
    lex_id: str
    gloss: str
    features: str
    slot: int | None = None
    clitic: bool = False


@dataclass
class Lexicon:
    entries: dict
    specs: dict
    closed: dict
    derived: dict = field(default_factory=dict)     # approximate glosses (pie/glosses.py)
    blocked: dict = field(default_factory=dict)     # lex_id → reason (data/generation/blocklist.jsonl)
    _cache: dict = field(default_factory=dict)

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> "Lexicon":
        lex = {}
        for x in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines():
            e = json.loads(x)
            lex[e["id"]] = e
        specs = {}
        for x in (ROOT / "data/morph/inflection_specs.jsonl").read_text("utf-8").splitlines():
            r = json.loads(x)
            specs[r["id"]] = r
        closed = json.loads((ROOT / "data/morph/closed_class.json").read_text("utf-8"))
        blocked = {}
        bp = ROOT / "data/generation/blocklist.jsonl"
        if bp.exists():
            for x in bp.read_text("utf-8").splitlines():
                d = json.loads(x)
                blocked[d["lex_id"]] = d["reason"]
        derived = {}
        p = ROOT / "data/lexicon/derived_glosses.jsonl"
        if p.exists():
            for x in p.read_text("utf-8").splitlines():
                d = json.loads(x)
                derived[d["id"]] = d["gloss"]
        return cls(lex, specs, closed, derived, blocked)

    def gloss(self, lex_id: str) -> str:
        if lex_id.startswith("closed:"):
            return lex_id.split(":", 1)[1]
        m = self.entries[lex_id]["meaning"]
        if not m and lex_id in self.derived:      # "to bend [-tus: action noun]" → bend.ACTN
            g = self.derived[lex_id].split("[")[0].split(",")[0].strip()
            return g.removeprefix("to ").replace(" ", ".") + "~"
        g = (m[0] if m else self.entries[lex_id]["form"]).split(",")[0].split(";")[0].strip()
        return g.removeprefix("to ").replace(" ", ".")

    def meaning(self, lex_id: str) -> tuple[str | None, str]:
        """(gloss, source): Wiktionary gloss, or the approximate derived one."""
        m = self.entries[lex_id]["meaning"]
        if m:
            # first senses joined: ḱléwos is "that which is heard; fame", and "fame" is what a planner needs
            return "; ".join(dict.fromkeys(x.strip() for x in m[:3] if x.strip())), \
                self.entries[lex_id].get("meaning_source", "wiktionary")
        return self.derived.get(lex_id), "derived"

    def gender(self, lex_id: str) -> str:
        """Lexicon gender first: spec gender defaults to m for athematic table
        stems, which would make dʰugh₂tḗr "daughter" take masculine adjectives."""
        e = self.entries.get(lex_id, {})
        g = e.get("gender")
        if g not in ("m", "f", "n") and e.get("form", "").endswith(("ih₂", "íh₂", "eh₂", "éh₂")):
            g = "f"                          # devī and eh₂ nouns: h₃rḗǵnih₂, néptih₂
        if g not in ("m", "f", "n"):
            g = ((self.specs.get(lex_id) or {}).get("spec") or {}).get("gender")
        return g if g in ("m", "f", "n") else "m"

    def participle_cells(self, lex_id: str, voice: str, gender: str) -> dict:
        """Case forms of a verb's participle, agreeing in gender.

        Active: nt-stems. Thematic (bʰéront-) has no ablaut and gen. -os
        (bʰérontos, Ved. bháratas); athematic ablauts (h₁sónt-/h₁sn̥t-, gen.
        h₁sn̥tés, Ved. satás). Feminine in -ih₂ (bʰérontih₂, h₁sn̥tíh₂).
        Middle: the -mh₁no- adjective. The perfect participle is not supported.
        """
        k = ("PTCP", lex_id, voice, gender)
        if k in self._cache:
            return self._cache[k]
        vc = self.cells(lex_id)
        forms = vc.get("PTCP.MID" if voice == "MID" else "PTCP.ACT") or []
        thematic = bool((self.specs[lex_id].get("spec") or {}).get("strong", "").endswith(("e", "é")))
        try:
            c = decline_participle(forms[0] if forms else "", voice, gender, thematic)
        except KeyError:
            raise KeyError(f"{lex_id}: no {voice} participle the engine can decline")
        self._cache[k] = c
        return c

    def cells(self, lex_id: str, gender: str | None = None) -> dict:
        k = (lex_id, gender)
        if k not in self._cache:
            r = self.specs[lex_id]
            sp, fam = r["spec"], r["family"]
            if fam == "noun":
                c = decline(NounSpec(**sp), "handbook")
                # the headword is the attested citation form (gʷḗn, not the table's gʷénh₂s)
                lemma = self.entries[lex_id]["form"]
                # not for o-stems: their headword is stem + -s/-m, so a mismatch is a table error (h₂ŕ̥ǵn̥tom vs
                # table h₂r̥ǵn̥tó-), fixed by a spec override, never by mixing two stems (engine sweep, thematic.md 5)
                if not lemma.endswith("-") and lemma not in c.get("NOM.SG", []) and r.get("rule") == "table" \
                        and NounSpec(**sp).kind != "thematic":
                    c = {**c, "NOM.SG": [lemma] + c.get("NOM.SG", [])}
                    if self.gender(lex_id) == "n":     # neuter: accusative and vocative = nominative (ḱḗr, not ḱérd)
                        c["ACC.SG"] = [lemma] + c.get("ACC.SG", [])
                        c["VOC.SG"] = [lemma] + c.get("VOC.SG", [])
            elif fam == "adj":
                c = decline_adj(AdjSpec(**sp), "handbook")[gender or "m"]
            else:
                c = conjugate(VerbSpec(**sp), "handbook")
            self._cache[k] = c
        return self._cache[k]


def _unaccent(form: str) -> str:
    import unicodedata
    d = unicodedata.normalize("NFD", form)
    return unicodedata.normalize("NFC", d.replace("\u0301", ""))


def _closed_form(lx: Lexicon, lex_id: str, feat: str, gender: str) -> str | None:
    """closed:personal/1, closed:demonstrative_so, closed:anaphoric_i, closed:deictic_ki, closed:deictic_eno,
    closed:relative_yo, closed:interrogative_kwo, ..."""
    path = lex_id.split(":", 1)[1].split("/")
    node = lx.closed
    for p in path:
        node = node.get(p, {})
    if path[0] in ("demonstrative_so", "anaphoric_i", "deictic_ki", "deictic_eno", "relative_yo", "interrogative_kwo"):
        node = node.get(gender if gender in node else "m", {})
    if path[0] in ("interrogative_kwi", "indefinite_kwi"):
        if path[0] == "indefinite_kwi":
            # the indefinite is the unaccented (enclitic) interrogative: ne kʷis 'no one', h₁yód kʷis 'if anyone'
            node = lx.closed.get("interrogative_kwi", {})
            sub = node.get("n" if gender == "n" else "mf", {})
            f = sub.get(feat)
            return _unaccent(f[0]) if f else None
        node = node.get("n" if gender == "n" else "mf", {})
    if path[0] == "numerals":
        if isinstance(node, list):                      # indeclinable 5-10: closed:numerals/indeclinable/7
            return node[0]
        node = node.get(gender) or node.get("fn" if gender in ("f", "n") else "m") or node.get("m", {})
        if feat.endswith(".SG") or feat.endswith(".DU"):  # 2 is dual, 3 and 4 plural: number follows the numeral
            feat = feat.rsplit(".", 1)[0] + (".DU" if path[1] == "2" else ".PL")
    forms = node.get(feat) if isinstance(node, dict) else None
    if not forms and path[0] == "personal" and isinstance(node, dict):
        forms = node.get(feat + ".ENCL")      # no book prints a stressed 1st/2nd pl. genitive (Ringe: "???")
    return forms[0] if forms else None


def _closed_feat(lx: Lexicon, lex_id: str, feat: str) -> str:
    """The feature actually realized: a personal-pronoun cell that falls back to the enclitic says so
    (engine sweep, closed-class-compounds.md R3)."""
    if lex_id.startswith("closed:personal/") and not feat.endswith(".ENCL"):
        node = lx.closed["personal"].get(lex_id.split("/")[1], {})
        if feat not in node and feat + ".ENCL" in node:
            return feat + ".ENCL"
    return feat


def _person_number(slot: dict, lx: Lexicon) -> tuple[int, str]:
    lid = slot["lex_id"]
    if lid.startswith("closed:personal/") and lid.split("/")[1] in ("1", "2"):
        return int(lid.split("/")[1]), slot.get("num", "SG")
    # a neuter plural subject takes a singular verb (Gk τὰ ζῷα τρέχει, Av., Hitt.): the old collective
    if slot.get("num") == "PL" and _slot_gender(slot, lx) == "n":
        return 3, "SG"
    return 3, slot.get("num", "SG")


def _verb_feature(v: dict, person: int, num: str) -> str:
    mood, tense, voice = v.get("mood", "IND"), v.get("tense", "PRS"), v.get("voice", "ACT")
    pn = f"{v.get('person') or person}{v.get('num') or num}"   # pro-drop: the verb may carry person and number
    base = {"IND": tense, "IMP": "IMP", "SBJV": "SBJV", "OPT": "OPT"}[mood]
    return ("MID." if voice == "MID" else "") + f"{base}.{pn}"


_VALENCY: dict | None = None


def _valency(lex_id: str) -> str | None:
    """'tr' / 'intr' from data/generation/verb_valency.json (verbs whose gloss misleads planners)."""
    global _VALENCY
    if _VALENCY is None:
        p = ROOT / "data" / "generation" / "verb_valency.json"
        _VALENCY = json.loads(p.read_text("utf-8")) if p.exists() else {}
    v = _VALENCY.get(lex_id)
    return v.get("valency") if isinstance(v, dict) else None


def check_plan(plan: dict, lx: Lexicon | None = None) -> list[str]:
    """Every problem with a plan, or [] if it can be realized."""
    lx = lx or Lexicon.load()
    errs = []
    if not plan.get("english"):
        errs.append("missing english")
    for ci, cl in enumerate(plan.get("clauses", [])):
        slots = cl.get("slots", [])
        verbs = [s for s in slots if s.get("role") == "V"]
        ctype = cl.get("type", "verbal")
        if ctype not in CLAUSE_TYPES:
            errs.append(f"clause {ci}: unknown clause type {ctype!r} (verbal, nominal or np)")
            continue
        if ctype == "verbal" and len(verbs) != 1:
            errs.append(f"clause {ci}: needs exactly one V slot, has {len(verbs)} (a verbless sentence is "
                        f"\"type\": \"nominal\"; a bare noun phrase is \"type\": \"np\")")
        errs += _check_clause_type(ci, cl, ctype, slots, verbs)
        # (a relative pronoun may be the subject: "you who split the vault" is fine)
        if len(verbs) == 1 and (verbs[0].get("verb") or {}).get("person") == 2 and any(
                s.get("role") == "SUBJ" and not s.get("lex_id", "").startswith("closed:") for s in slots):
            errs.append(f"clause {ci}: a 2nd-person verb takes no noun subject: address the god or person "
                        f"with a VOC slot (h₂éwsos 'Dawn!', not SUBJ h₂éwsōs)")
        # an explicit person/number on the verb is for pro-drop; with an explicit subject it must
        # agree with it (David's review: SUBJ gʷówes PL + verb num SG gave 'gʷówes trémt')
        subjs = [s for s in slots if s.get("role") == "SUBJ"]
        # a relative or interrogative subject takes its person from the antecedent or addressee
        # ("you who split the vault": h₁yós … 2SG), so only other subjects are checked
        if len(verbs) == 1 and len(subjs) == 1 and not subjs[0].get("lex_id", "").startswith(
                ("closed:relative_yo", "closed:interrogative_")):
            v = verbs[0].get("verb") or {}
            sj = dict(subjs[0])
            sj_i = slots.index(subjs[0])
            for m in slots:
                if m.get("role") == "MOD" and m.get("head") == sj_i and m.get("lex_id", "").startswith("closed:numerals/"):
                    n = m["lex_id"].split("/")[1]
                    sj["num"] = {"2": "DU", "3": "PL", "4": "PL"}.get(n, sj.get("num"))
            try:
                ep, en = _person_number(sj, lx)
            except Exception:
                ep, en = None, None
            if ep is not None:
                if v.get("person") and int(v["person"]) != ep:
                    errs.append(f"clause {ci}: the verb's person {v['person']} contradicts its subject (person {ep}); "
                                f"drop the verb's person or the subject")
                # a dual subject may take a plural verb where the dual cell is not reconstructible
                # (middle and perfect duals: the plural stands in, as for dual obliques)
                if v.get("num") and v["num"] != en and not (en == "DU" and v["num"] == "PL"):
                    errs.append(f"clause {ci}: the verb's number {v['num']} contradicts its subject ({en}"
                                f"{', a neuter plural takes a singular verb' if en == 'SG' and sj.get('num') == 'PL' else ''}); "
                                f"drop the verb's num, or fix the subject's num")
        # a 2nd-person verb addressed to a vocative agrees with it in number ("waters, flow!" is PL)
        vocs = [s for s in slots if s.get("role") == "VOC" and not s.get("and")]
        if len(verbs) == 1 and len(vocs) == 1 and not subjs:
            v = verbs[0].get("verb") or {}
            if str(v.get("person")) == "2" and v.get("num") and vocs[0].get("num", "SG") != v["num"]:
                errs.append(f"clause {ci}: the 2nd-person verb's number {v['num']} contradicts the addressee "
                            f"(VOC {vocs[0].get('num', 'SG')})")
        for si, s in enumerate(slots):
            where = f"clause {ci} slot {si}"
            lid, role = s.get("lex_id", ""), s.get("role")
            if role not in ROLES:
                errs.append(f"{where}: unknown role {role!r}")
                continue
            if role == "APPOS":
                e = _check_appos(s, si, slots, where)
                if e:
                    errs.append(e)
                    continue
            if lid.startswith("closed:"):
                continue
            if lid == "compound":
                errs += _check_compound(s, slots, where, lx)
                continue
            if role == "ADV":
                if lx.entries.get(lid, {}).get("pos") not in ("adv", "particle", "conj", "prep", "postp"):
                    errs.append(f"{where}: ADV needs an indeclinable (adv/particle) lexeme, {lid} is not one")
                continue
            if lid not in lx.specs:
                errs.append(f"{where}: unknown or non-inflectable lex_id {lid!r}")
                continue
            r = lx.specs[lid]
            if lid in lx.blocked:
                errs.append(f"{where}: {lid} is blocked from generation: {lx.blocked[lid]}")
                continue
            if not r.get("usable"):
                errs.append(f"{where}: {lid} has no usable spec (rule {r['rule']})")
                continue
            fam = r["family"]
            ptcp = s.get("participle")
            if ptcp is not None:
                if role != "MOD" or fam != "verb":
                    errs.append(f"{where}: a participle is a MOD slot holding a verb")
                elif ptcp.get("voice", "ACT") not in ("ACT", "MID"):
                    errs.append(f"{where}: participle voice must be ACT or MID")
                elif lx.entries[lid]["form"].endswith(("tor", "toy")) and ptcp.get("voice", "ACT") != "MID":
                    # engine sweep, thematic-verbs.md defect 10
                    errs.append(f"{where}: {lid} is middle-only (deponent): its participle is middle (voice MID)")
            if s.get("dep") is not None:
                d = s["dep"]
                if not (isinstance(d, int) and 0 <= d < len(slots) and slots[d].get("participle")):
                    errs.append(f"{where}: dep must point at a participle slot")
            if role == "V" and fam != "verb":
                errs.append(f"{where}: V slot needs a verb, {lid} is a {fam}")
            if role == "V" and fam == "verb" and lx.entries[lid]["form"].endswith(("tor", "toy")) \
                    and s.get("verb", {}).get("voice") != "MID":
                errs.append(f"{where}: {lid} is middle-only (deponent): voice must be MID")
            if role == "V" and fam == "verb" and cl.get("neg") and s.get("verb", {}).get("mood") == "IMP" \
                    and not any(k.startswith(("PST.", "AOR.")) for k in lx.cells(lid)):
                errs.append(f"{where}: a prohibitive (neg + IMP) needs a present or aorist stem for the "
                            f"injunctive; {lid} is a perfect")
            if role == "V" and fam == "verb" and _valency(lid) == "tr" and s.get("verb", {}).get("voice") != "MID" \
                    and not any(x.get("role") == "OBJ" for x in slots):
                errs.append(f"{where}: {lid} is transitive: active needs an OBJ; a patient subject "
                            f"('the wheel broke', 'dress yourself') takes voice MID")
            if role != "V" and fam == "verb" and ptcp is None:
                errs.append(f"{where}: role {role} needs a nominal, {lid} is a verb")
            if role == "MOD":
                h = s.get("head")
                if h is None or not (0 <= h < len(slots)) or slots[h].get("role") in ("V", "MOD", "ADV"):
                    errs.append(f"{where}: MOD needs a nominal head slot")
            if fam == "adj" and role not in ("MOD", "PRED", "APPOS") and not s.get("gender"):
                errs.append(f"{where}: an adjective used as a noun ('the Swift One') needs a gender "
                            f"(m, f or n) for whom it names")
            if role == "MOD" and fam not in ("adj",) and not lid.startswith("closed:") and ptcp is None:
                errs.append(f"{where}: MOD needs an adjective, {lid} is a {fam}")
        if not errs:
            try:
                ws = realize_clause(cl, lx)
            except KeyError as e:
                errs.append(f"clause {ci}: form not generated: {e}")
            else:
                errs += _doubled_enclitics(ci, ws)
    return errs


def _doubled_enclitics(ci: int, words: list[Word]) -> list[str]:
    """Two enclitic personal pronouns of the same person and number in different cases ('nos nos', POSS moy +
    IO moy) stand side by side in the Wackernagel slot (t019, t020 reviews). Counts what the realizer
    produces, including the GEN.PL fallback to the enclitic. The same cell twice (one possessive enclitic
    for two conjuncts) is merged by realize_clause and is fine."""
    groups: dict = {}
    for w in words:
        if w.lex_id.startswith("closed:personal/") and w.features.endswith(".ENCL"):
            groups.setdefault((w.lex_id, w.features.split(".")[1]), []).append(w)
    errs = []
    for (lid, num), ws in groups.items():
        feats = list(dict.fromkeys(w.features for w in ws))
        if len(feats) > 1:
            who = lid.split("/")[1]
            errs.append(f"clause {ci}: two enclitic {who}{num} pronouns in one clause "
                        f"({', '.join(f'{w.form} {w.features}' for w in ws)}): use one (an IO 'to me' already "
                        f"says whose; drop the POSS), or a stressed form (\"enclitic\": false)")
    return errs


# 3rd-person pronouns whose gender and number come from an antecedent, not from a head
ANAPHORS = ("closed:demonstrative_so", "closed:anaphoric_i", "closed:deictic_ki", "closed:deictic_eno")
# pronouns that introduce a referent an anaphor can take up ('whoever …, to him'; 'who …? he …')
REFERENT_PRONOUNS = ("closed:relative_yo", "closed:indefinite_kwi", "closed:interrogative_kwi", "closed:interrogative_kwo")
_NUMERAL_NUM = {"2": "DU", "3": "PL", "4": "PL", "indeclinable": "PL"}


def _referents(cl: dict, lx: Lexicon, anaphors: bool = True) -> set[tuple[str, str]]:
    """(gender, number) of every referent a clause names: a noun, an adjective or bahuvrihi used as a noun with
    a gender, a relative, indefinite or interrogative pronoun ('whoever gives …, his name'), an anaphor on
    its own (it carries its referent on to the next clauses: 'he … he'; not counted with anaphors=False), and a group of conjoined nouns (two singulars dual, else
    plural; masculine if any member is). A numeral MOD fixes its head's number, as in realize_clause."""
    slots = cl.get("slots", [])
    out, group = set(), {}
    for i, s in enumerate(slots):
        lid, role = s.get("lex_id", ""), s.get("role")
        if role in ("V", "ADV", "MOD") or s.get("participle") is not None:
            continue
        if lid.startswith("closed:"):
            if not lid.startswith(ANAPHORS + REFERENT_PRONOUNS) or (lid.startswith(ANAPHORS) and not anaphors):
                continue
            g = s.get("gender") if s.get("gender") in ("m", "f", "n") else "m"
        else:
            try:
                fam = _family(s, lx)
            except KeyError:
                continue
            if fam == "verb" or (fam == "adj" and not s.get("gender")):
                continue
            g = _slot_gender(s, lx)
        num = s.get("num", "SG")
        for m in slots:
            if m.get("role") == "MOD" and m.get("head") == i and m.get("lex_id", "").startswith("closed:numerals/"):
                num = _NUMERAL_NUM.get(m["lex_id"].split("/")[1], num)
        out.add((g, num))
        if role != "APPOS":
            group.setdefault((role, s.get("head")), []).append((g, num, bool(s.get("and"))))
    for ms in group.values():
        if len(ms) > 1 and any(a for _, _, a in ms):
            gs = {g for g, _, _ in ms}
            g = "m" if "m" in gs else gs.pop() if len(gs) == 1 else "m"
            out.add((g, "DU" if len(ms) == 2 and all(n == "SG" for _, n, _ in ms) else "PL"))
    return out


def plan_warnings(plan: dict, lx: Lexicon | None = None) -> list[str]:
    """Likely problems that do not stop realization (printed by realize_plans.py, never a reject).

    A 3rd-person pronoun (so/séh₂/tód, h₁ís/h₁íh₂/h₁íd, the deictics) used on its own, i.e. not a MOD or
    APPOS of a noun, whose gender and number match no referent (_referents: a noun, a noun-used adjective with a
    gender, a relative or indefinite pronoun, a conjoined group, an anaphor of an earlier clause) in its own
    clause or the two before it: a likely wrong antecedent gender (t016-t021 reviews: fem. h₁íh₂ for masc.
    dyḗws, fem. h₁íh₂m̥ for the neuter silver). A neuter 'that' for a whole event, a referent named further
    back, and a sense agreement ('the flock … they') also warn: check the English. With no referent at all in
    the window (a one-sentence plan's 'he') there is nothing to compare, so no warning."""
    lx = lx or Lexicon.load()
    clauses = plan.get("clauses", [])
    refs = [_referents(cl, lx) for cl in clauses]
    out = []
    for ci, cl in enumerate(clauses):
        # an anaphor in an earlier clause carries its referent on; one in the same clause does not ('he saw him')
        near = set().union(*refs[max(0, ci - 2):ci], _referents(cl, lx, anaphors=False))
        for si, s in enumerate(cl.get("slots", [])):
            if not s.get("lex_id", "").startswith(ANAPHORS) or s.get("role") in ("MOD", "APPOS"):
                continue
            g, n = s.get("gender") if s.get("gender") in ("m", "f", "n") else "m", s.get("num", "SG")
            if near and (g, n) not in near:     # nothing named nearby: the referent is outside the plan
                out.append(f"clause {ci} slot {si}: {s['lex_id'].split(':')[1]} {s.get('role')} {g} {n} matches no "
                           f"referent of that gender and number in this clause or the two before: check its antecedent")
    return out


def _check_clause_type(ci: int, cl: dict, ctype: str, slots: list, verbs: list) -> list[str]:
    """Clause-level rules of nominal clauses and np utterances (and NP slots elsewhere)."""
    errs = []
    if ctype != "np" and any(s.get("role") == "NP" for s in slots):
        errs.append(f"clause {ci}: role NP belongs to an np utterance (\"type\": \"np\")")
    if ctype != "np" and cl.get("case") is not None:
        errs.append(f"clause {ci}: \"case\" is for np utterances only; a {ctype} clause takes case from roles")
    if ctype == "verbal":
        return errs
    if verbs:
        errs.append(f"clause {ci}: a {ctype} clause has no V slot (the realizer never adds a copula; for "
                    f"tense, mood, emphasis or existence use a verbal clause with h₁ésti)")
    top = [s for s in slots if s.get("dep") is None]
    if ctype == "nominal":
        if not any(s.get("role") == "SUBJ" for s in top):
            errs.append(f"clause {ci}: a nominal clause needs an overt SUBJ (no verb ending marks the person: "
                        f"OPers. adam navama 'I (am) the ninth')")
        if not any(s.get("role") == "PRED" for s in top):
            errs.append(f"clause {ci}: a nominal clause needs a PRED (a noun or adjective)")
        for si, s in enumerate(slots):
            if s.get("role") in ("OBJ", "GOAL") and s.get("dep") is None:
                errs.append(f"clause {ci} slot {si}: role {s['role']} needs a verb; a nominal clause has none")
        if cl.get("order") not in (None, "SOV", "VSO"):
            errs.append(f"clause {ci}: order must be SOV (predicate last) or VSO (predicate first)")
    if ctype == "np":
        if cl.get("case", "NOM") not in CASES:
            errs.append(f"clause {ci}: unknown case {cl.get('case')!r} (one of {', '.join(CASES)})")
        if not any(s.get("role") == "NP" for s in slots):
            errs.append(f"clause {ci}: an np utterance needs a slot with role NP (the head noun)")
        for si, s in enumerate(slots):
            if s.get("role") not in NP_ROLES and s.get("dep") is None:
                errs.append(f"clause {ci} slot {si}: an np utterance holds only NP, MOD, POSS and APPOS slots "
                            f"(and participle deps), not {s.get('role')}; a sentence with a predicate is "
                            f"\"type\": \"nominal\"")
            if s.get("role") == "POSS" and s.get("head") is None:
                errs.append(f"clause {ci} slot {si}: in an np utterance a POSS needs a head")
        if cl.get("neg"):
            errs.append(f"clause {ci}: an np utterance cannot be negated (ne negates a predicate: use a "
                        f"nominal clause)")
    return errs


def _check_appos(s: dict, si: int, slots: list, where: str) -> str | None:
    h = s.get("head")
    if not (isinstance(h, int) and 0 <= h < len(slots)) or h == si:
        return f"{where}: APPOS needs a head slot (the noun phrase it stands in apposition to)"
    if slots[h].get("role") in ("V", "ADV", "MOD"):
        return f"{where}: APPOS needs a nominal head, slot {h} is a {slots[h].get('role')}"
    seen, k = {si}, h
    while slots[k].get("role") == "APPOS":         # a chain of appositions must end in a nominal
        if k in seen or not isinstance(slots[k].get("head"), int) or not 0 <= slots[k]["head"] < len(slots):
            return f"{where}: APPOS head chain is circular or broken"
        seen.add(k)
        k = slots[k]["head"]
    if s.get("participle") is not None:
        return f"{where}: a participle is a MOD, not an APPOS"
    n, hn = s.get("num"), _chain_num(slots, h)
    if n and hn and n != hn:
        return f"{where}: an APPOS takes its head's number ({hn}), not {n}"
    return None


def _chain_num(slots: list, i: int) -> str | None:
    """The explicit number of slot i, following APPOS heads (None if unset)."""
    seen = set()
    while i not in seen and 0 <= i < len(slots):
        seen.add(i)
        s = slots[i]
        if s.get("role") == "APPOS" and not s.get("num") and isinstance(s.get("head"), int):
            i = s["head"]
            continue
        return s.get("num")
    return None


def _check_compound(s: dict, slots: list, where: str, lx: Lexicon) -> list[str]:
    role = s.get("role")
    try:
        cmp = resolve_compound(s.get("compound"), lx)
    except CompoundError as e:
        return [f"{where}: {e}"]
    if role in ("V", "ADV"):
        return [f"{where}: a compound is a nominal; role {role} needs a verb or an indeclinable"]
    if s.get("participle") is not None or s.get("dep") is not None:
        return [f"{where}: a compound slot takes no participle or dep"]
    if cmp.ctype == "determinative":
        if role == "MOD":
            return [f"{where}: a determinative compound is a noun (its head's gender and declension); "
                    f"use type 'bahuvrihi' for an adjective ('having X')"]
        return []
    if role == "MOD":
        h = s.get("head")
        if h is None or not (isinstance(h, int) and 0 <= h < len(slots)) or slots[h].get("role") in ("V", "MOD", "ADV"):
            return [f"{where}: MOD needs a nominal head slot"]
    elif role not in ("PRED", "APPOS") and not s.get("gender"):
        return [f"{where}: a bahuvrihi used as a noun ('the one of good fame') needs a gender (m, f or n)"]
    return []


def _family(s: dict, lx: Lexicon) -> str:
    if s["lex_id"] == "compound":
        return "adj" if (s.get("compound") or {}).get("type", "bahuvrihi") == "bahuvrihi" else "noun"
    return lx.specs[s["lex_id"]]["family"]


def _slot_gender(s: dict, lx: Lexicon) -> str:
    if s.get("gender") in ("m", "f", "n"):
        return s["gender"]
    if s["lex_id"] == "compound":
        c = s.get("compound") or {}
        return lx.gender(c["second"]) if c.get("type") == "determinative" and c.get("second") else "m"
    return lx.gender(s["lex_id"]) if not s["lex_id"].startswith("closed:") else "m"


def realize_clause(cl: dict, lx: Lexicon) -> list[Word]:
    slots = cl["slots"]
    # a noun counted by 2 is dual, by 3 or 4 plural (the numeral MOD fixes its head's number; t016 review:
    # "two dogs" came out singular when the plan left num unset)
    for sl in slots:
        if sl["role"] == "MOD" and sl["lex_id"].startswith("closed:numerals/") and sl.get("head") is not None:
            n = sl["lex_id"].split("/")[1]
            want = {"2": "DU", "3": "PL", "4": "PL", "indeclinable": "PL"}.get(n)   # 5-1000 too (closed-class R7)
            if want and slots[sl["head"]].get("num") != want:
                slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
                slots[sl["head"]]["num"] = want
    # an apposition takes its head's number; an adjective (or pronoun) in apposition also its gender
    if any(sl["role"] == "APPOS" for sl in slots):
        slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
        done: set[int] = set()

        def settle(i: int, chain: tuple = ()) -> None:
            s = slots[i]
            if s["role"] != "APPOS" or i in done:
                return
            h = s.get("head")
            if h is None or h in chain or not 0 <= h < len(slots):
                raise KeyError(f"APPOS slot {i}: broken head chain")
            settle(h, chain + (i,))
            s["num"] = slots[h].get("num", "SG")
            if not s.get("gender") and (s["lex_id"].startswith("closed:") or _family(s, lx) == "adj"):
                s["gender"] = _slot_gender(slots[h], lx)
            done.add(i)
        for i in range(len(slots)):
            settle(i)
    ctype = cl.get("type", "verbal")
    # -kʷe goes on the last conjunct (X Y-kʷe, Lat. senatus populusque): a mark only on an earlier
    # member of a coordinated group (same role and head) moves to the last one (t014 review)
    groups: dict = {}
    for i, sl in enumerate(slots):
        if sl["role"] not in ("V", "MOD", "ADV"):
            groups.setdefault((sl["role"], sl.get("head")), []).append(i)
    for ix in groups.values():
        if len(ix) > 1 and any(slots[i].get("and") for i in ix) and not slots[ix[-1]].get("and"):
            slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
            for i in ix[:-1]:
                slots[i]["and"] = False
            slots[ix[-1]]["and"] = True
    coord = {i for ix in groups.values() if len(ix) > 1 and any(slots[i].get("and") for i in ix) for i in ix}
    pairs = {i for ix in groups.values() if len(ix) == 2 and slots[ix[-1]].get("and") for i in ix}
    subj_i = next((i for i, s in enumerate(slots) if s["role"] == "SUBJ"), None)
    subj = slots[subj_i] if subj_i is not None else None
    person, num = _person_number(subj, lx) if subj else (3, "SG")
    neuter_pl = subj is not None and person == 3 and subj.get("num") == "PL" and _slot_gender(subj, lx) == "n"
    subjs = sorted(i for i in coord if slots[i]["role"] == "SUBJ" and slots[i].get("head") is None)
    if len(subjs) > 1:
        # conjoined subjects (X Y-kʷe) agree as a group (Fortson §8.16): two singulars dual, else plural;
        # 1st person over 2nd over 3rd (engine sweep, closed-class-compounds.md R4)
        pn = [_person_number(slots[i], lx) for i in subjs]
        person = min(p for p, _ in pn)
        if all(slots[i].get("num") == "PL" and _slot_gender(slots[i], lx) == "n" for i in subjs):
            num = "SG"      # Il. 2.468 phúlla kaì ánthea gígnetai (Fortson §8.16): neuter plurals stay collective
        else:
            num = "DU" if len(subjs) == 2 and all(slots[i].get("num", "SG") == "SG" for i in subjs) else "PL"
            neuter_pl = False
    vi = next((i for i, s in enumerate(slots) if s["role"] == "V"), None)
    if (vi is None) != (ctype != "verbal"):
        raise KeyError(f"a {ctype} clause {'needs a' if ctype == 'verbal' else 'takes no'} V slot")
    v = slots[vi].get("verb", {}) if vi is not None else {}

    def case_of(i: int, chain: tuple = ()) -> str:
        """Case from role: MOD and APPOS take their head's, NP the utterance's (np clauses)."""
        r = slots[i]["role"]
        if r in ("MOD", "APPOS"):
            h = slots[i].get("head")
            if h is None or h in chain or not 0 <= h < len(slots):
                raise KeyError(f"slot {i}: broken head chain")
            return case_of(h, chain + (i,))
        if r == "NP":
            return cl.get("case", "NOM")
        return ROLE_CASE[r]
    prohibitive = cl.get("neg") and v.get("mood") == "IMP"
    neg_wish = cl.get("neg") and v.get("mood") == "OPT"        # mē + optative: "may it not …" (Gk μή + opt.)
    # hortative subjunctive 'let us not …' takes mē as well (Gk μή + hortatory subj.)
    neg_wish = neg_wish or (cl.get("neg") and v.get("mood") == "SBJV" and int(v.get("person") or person) == 1)
    words: dict[int, Word] = {}
    for i, s in enumerate(slots):
        lid, role = s["lex_id"], s["role"]
        if role == "V":
            # a neuter plural subject takes a singular verb even if the plan set num (t011 review)
            feat = _verb_feature({**v, "num": "SG"} if neuter_pl else v, person, num)
            if prohibitive:
                # mē + injunctive (augmentless secondary form), not the imperative
                pn = feat.split(".")[-1]
                cells = lx.cells(lid)
                mid = "MID." if v.get("voice") == "MID" else ""
                feat = next((f"{mid}{t}.{pn}" for t in ("PST", "AOR") if f"{mid}{t}.{pn}" in cells), feat)
            cells = lx.cells(lid)
            if feat not in cells and feat.endswith("DU") and feat[:-2] + "PL" in cells:
                feat = feat[:-2] + "PL"       # no dual cell (e.g. the perfect): the plural stands in
            form = cells[feat][0]
            if prohibitive:
                feat = feat.replace("PST", "INJ").replace("AOR", "INJ")
        elif role == "ADV":
            feat, form = "ADV", (lx.entries[lid]["form"] if not lid.startswith("closed:") else lid.split(":")[-1])
        else:
            # agreement source: a MOD agrees with its head; a predicate adjective with the subject
            if role == "MOD":
                head = slots[s["head"]]
            elif role == "PRED" and subj and not lid.startswith("closed:") and _family(s, lx) == "adj":
                head = subj
            elif role == "PRED" and not subj and not lid.startswith("closed:") and _family(s, lx) == "adj" \
                    and any(x["role"] == "VOC" for x in slots):
                # "Sea, you are great": the dropped subject is the addressee (t011 review)
                head = {**next(x for x in slots if x["role"] == "VOC"), "role": "PRED"}
            elif role == "PRED" and not subj and not lid.startswith("closed:") and _family(s, lx) == "adj":
                # pro-drop: the predicate adjective takes the verb's number ("may they be many": polh₁éwes)
                head = {**s, "num": s.get("num") or v.get("num") or "SG"}
            else:
                head = s
            case = "NOM" if role == "PRED" else case_of(i)
            hi = i
            while slots[hi]["role"] in ("MOD", "APPOS") and slots[hi].get("head") is not None:
                hi = slots[hi]["head"]
            if case == "VOC" and hi in pairs and slots[hi].get("and"):
                case = "NOM"        # vā́yav índraś ca 'o Vayu and Indra' (Fortson §8.11; closed-class R5)
            if role == "MOD" and head["role"] == "MOD":
                raise KeyError("MOD cannot head a MOD")
            n = head.get("num", "SG")
            if n == "DU" and case not in ("NOM", "ACC", "VOC") and not lid.startswith("closed:numerals"):
                # dual obliques are not reconstructible (Fortson §6.13, §6.50; Lundquist & Yates
                # §122.2.1.1; Ringe ???): the plural stands in, and the feature says so
                n = "PL"
            g = _slot_gender(head, lx)
            feat = f"{case}.{n}" + (".ENCL" if s.get("enclitic") else "")
            if lid == "compound":
                cmp = resolve_compound(s["compound"], lx)
                form = cmp.cells(g if cmp.ctype == "bahuvrihi" else None)[feat][0]
                words[i] = Word(form, cmp.lex_id, cmp.gloss(), feat, i)
                continue
            if lid.startswith("closed:"):
                form = _closed_form(lx, lid, feat, g)
                if form is None:
                    raise KeyError(f"{lid} {feat} {g}")
                feat = _closed_feat(lx, lid, feat)
            elif s.get("participle"):
                form = lx.participle_cells(lid, s["participle"].get("voice", "ACT"), g)[feat][0]
                feat = f"PTCP.{s['participle'].get('voice', 'ACT')}.{feat}"
            elif lx.specs[lid]["family"] == "adj":
                form = lx.cells(lid, g)[feat][0]
            else:
                form = lx.cells(lid)[feat][0]
        words[i] = Word(form, lid, lx.gloss(lid), feat, i,
                        clitic=feat.endswith(".ENCL") or form in ENCLITIC_PRONOUNS)

    # phrases: every MOD/POSS goes directly before its head, recursively; an APPOS phrase follows
    # its head's phrase ('the horses, immortal ones'), or precedes it with "before"
    def phrase(i: int) -> list[int]:
        mods = [j for j, x in enumerate(slots) if x["role"] in ("MOD", "POSS") and x.get("head") == i and j != i]
        deps = [j for j, x in enumerate(slots) if x.get("dep") == i and j != i]   # a participle's own object etc.
        app = [j for j, x in enumerate(slots) if x["role"] == "APPOS" and x.get("head") == i and j != i]
        pre = [k for j in app if slots[j].get("before") for k in phrase(j)]
        post = [k for j in app if not slots[j].get("before") for k in phrase(j)]
        return pre + [k for j in deps + mods for k in phrase(j)] + [i] + post

    # a nominal sentence is topic first, predicate last (Lehmann 1974 §2.1.4, §4.3.1.a)
    order_roles = ["VOC", "SUBJ", "IO", "OBJ", "GOAL", "INS", "LOC", "ABL", "PRED", "ADV"] if ctype == "verbal" \
        else ["VOC", "SUBJ", "IO", "INS", "LOC", "ABL", "ADV", "PRED"] if ctype == "nominal" else ["NP"]
    tops = [i for i, x in enumerate(slots) if x["role"] not in ("V", "MOD", "APPOS") and x.get("dep") is None
            and not (x["role"] == "POSS" and x.get("head") is not None)]
    tops.sort(key=lambda i: order_roles.index(slots[i]["role"]) if slots[i]["role"] in order_roles else 99)
    phrases = [phrase(t) for t in tops]
    is_pred = [slots[t]["role"] == "PRED" for t in tops]
    # interrogatives move to the front of the clause (with their phrase)
    q = [ph for ph in phrases if any(slots[j]["lex_id"].startswith("closed:interrogative") for j in ph)]
    pred_phrases = [ph for ph, p in zip(phrases, is_pred) if p and ph not in q]
    phrases = q + [ph for ph in phrases if ph not in q]
    seq = [j for ph in phrases for j in ph]
    placed = sorted(seq + ([vi] if vi is not None else []))
    if placed != list(range(len(slots))):
        missing = sorted(set(range(len(slots))) - set(placed))
        raise KeyError(f"slots {missing} not attached to the clause (a MOD/POSS head chain is broken)")
    for i in seq:
        if slots[i]["lex_id"] == "closed:indefinite_kwi":
            words[i].clitic = True        # the indefinite is enclitic: ne kʷis gʷémt 'no one came'
    neg = Word("mē" if (prohibitive or neg_wish) else "ne", "closed:particle:ne", "NEG", "PARTICLE") \
        if cl.get("neg") else None
    vseq = ([neg] if neg else []) + [words[vi]] if vi is not None else []
    # -kʷe follows the first word of the conjunct it joins, a single word or a phrase
    # (Fortson §7.27, §8.24: Lat. lūcusue Diānae; Ved. ágna índraś ca; closed-class-compounds.md R1)
    and_host: dict[int, int] = {}
    for i, sl in enumerate(slots):
        if sl.get("and") and sl["role"] not in ("V", "ADV"):
            ph = [j for j in phrase(i) if not words[j].clitic]
            h = ph[0] if ph else i
            and_host[h] = and_host.get(h, 0) + 1

    def render_phrase(ph: list[int]) -> list[Word]:
        ws = []
        for i in ph:
            if words[i].clitic:
                continue
            ws.append(words[i])
            for _ in range(and_host.get(i, 0)):
                ws.append(Word("-kʷe", "closed:particle:-kʷe", "and", "PARTICLE", clitic=True))
        return ws

    front = [w for ph in q for w in render_phrase(ph)]           # fronted interrogative phrase(s)
    if ctype == "verbal":
        rest = [w for ph in phrases if ph not in q for w in render_phrase(ph)]
        out = front + vseq + rest if cl.get("order") == "VSO" else front + rest + vseq
    else:
        # no verb and no copula: the predicate (with ne before it) stands last, or first with VSO
        rest = [w for ph in phrases if ph not in q and ph not in pred_phrases for w in render_phrase(ph)]
        pseq = [w for ph in pred_phrases for w in render_phrase(ph)]
        if neg:
            pseq = [neg] + pseq if pseq else pseq
            if not pseq:                  # the predicate is a fronted interrogative: ne after it
                front = front[:1] + [neg] + front[1:]
        out = front + pseq + rest if cl.get("order") == "VSO" else front + rest + pseq
    if cl.get("particle") == "nu":
        out.insert(0, Word("nu", "closed:particle:nu", "NU", "PARTICLE"))
    if cl.get("particle") == "yod":       # h₁yód 'if, when' (Ved. yád): a subordinate clause, verb-final
        out.insert(0, Word("h₁yód", "closed:relative_yo/n", "if/when", "CONJ"))
    # Wackernagel: enclitics after the first word, "and" (-kʷe) / "or" (-wē) on the first word
    clitics = [words[i] for i in seq if words[i].clitic]
    # one possessive enclitic serves both conjuncts: h₂óweyes moy h₁éḱwōs-kʷe, not *moy moy (closed-class R8)
    clitics = [w for k, w in enumerate(clitics)
               if (w.form, w.features) not in {(x.form, x.features) for x in clitics[:k]}]
    if cl.get("particle") == "ge":
        clitics.insert(0, Word("-ge", "closed:particle:-ge", "EMPH", "PARTICLE", clitic=True))
    # after the first word and any connective clitic on it (Fortson §8.25: gʷṓs-kʷe te; closed-class R6)
    k = 1
    while k < len(out) and out[k].form in ("-kʷe", "-wē"):
        k += 1
    out[k:k] = clitics
    if cl.get("conj") in ("kʷe", "wē"):
        f = "-" + cl["conj"]
        out.insert(1, Word(f, f"closed:particle:{f}", "and" if f == "-kʷe" else "or", "PARTICLE", clitic=True))
    return out


def realize(plan: dict, lx: Lexicon | None = None) -> dict:
    lx = lx or Lexicon.load()
    text, gloss, words = [], [], []
    for ci, cl in enumerate(plan["clauses"]):
        if ci and cl.get("break"):
            text[-1] += "?" if plan["clauses"][ci - 1].get("question") else "."
        ws = realize_clause(cl, lx)
        words += ws
        for w in ws:
            if w.form.startswith("-") and text:
                text[-1] += w.form
                gloss[-1] += "=" + w.gloss
            else:
                text.append(w.form)
                gloss.append(f"{w.gloss}-{w.features}" if w.features not in ("PARTICLE", "ADV") else w.gloss)
    end = "?" if plan["clauses"][-1].get("question") else "."
    return {"pie": " ".join(text) + end, "gloss": " ".join(gloss), "english": plan["english"],
            "words": [w.__dict__ for w in words]}
