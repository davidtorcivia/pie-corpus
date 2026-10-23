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
                "slots": [
      {"lex_id": "pie-lex-…" | "closed:personal/1" | …,
       "role": "SUBJ|OBJ|IO|INS|LOC|ABL|POSS|VOC|PRED|GOAL|MOD|ADV|V",
       "num": "SG|DU|PL",                          # nominals; MOD and V take it from their head/subject
       "head": null | <slot index>,                # MOD (adjective, demonstrative, POSS) → its noun
       "enclitic": false,                          # pronoun slots: the enclitic form (moy, toy, …)
       "gender": null | "m|f|n",                   # pronoun slots used on their own (tod "it", kʷíd "what")
       "and": false,                               # -kʷe "and" after this word (X Y-kʷe = X and Y)
       "verb": {"tense": "PRS|PST|AOR|PRF", "mood": "IND|IMP|SBJV|OPT", "voice": "ACT|MID",
                "person": null | 1 | 2 | 3,       # person and number default to the subject's (3SG without one);
                "num": null | "SG|DU|PL"}}]}]}    # set them for pro-drop ("let us go": person 1, num PL, no SUBJ)

`check_plan` lists every problem; `realize` assumes a checked plan.

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
NOMINAL_ROLES = set(ROLE_CASE) | {"MOD"}
ROLES = NOMINAL_ROLES | {"ADV", "V"}
# Wackernagel enclitics: placed after the first word of the clause
ENCLITIC_PRONOUNS = {"moy", "toy", "me", "te", "nos", "wos", "soy", "se"}


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
                if not lemma.endswith("-") and lemma not in c.get("NOM.SG", []) and r.get("rule") == "table":
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
        if len(verbs) != 1:
            errs.append(f"clause {ci}: needs exactly one V slot, has {len(verbs)}")
        # (a relative pronoun may be the subject: "you who split the vault" is fine)
        if len(verbs) == 1 and (verbs[0].get("verb") or {}).get("person") == 2 and any(
                s.get("role") == "SUBJ" and not s.get("lex_id", "").startswith("closed:") for s in slots):
            errs.append(f"clause {ci}: a 2nd-person verb takes no noun subject: address the god or person "
                        f"with a VOC slot (h₂éwsos 'Dawn!', not SUBJ h₂éwsōs)")
        for si, s in enumerate(slots):
            where = f"clause {ci} slot {si}"
            lid, role = s.get("lex_id", ""), s.get("role")
            if role not in ROLES:
                errs.append(f"{where}: unknown role {role!r}")
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
            if fam == "adj" and role not in ("MOD", "PRED") and not s.get("gender"):
                errs.append(f"{where}: an adjective used as a noun ('the Swift One') needs a gender "
                            f"(m, f or n) for whom it names")
            if role == "MOD" and fam not in ("adj",) and not lid.startswith("closed:") and ptcp is None:
                errs.append(f"{where}: MOD needs an adjective, {lid} is a {fam}")
        if not errs:
            try:
                realize_clause(cl, lx)
            except KeyError as e:
                errs.append(f"clause {ci}: form not generated: {e}")
    return errs


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
    elif role != "PRED" and not s.get("gender"):
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
    subj_i = next((i for i, s in enumerate(slots) if s["role"] == "SUBJ"), None)
    subj = slots[subj_i] if subj_i is not None else None
    person, num = _person_number(subj, lx) if subj else (3, "SG")
    neuter_pl = subj is not None and person == 3 and subj.get("num") == "PL" and _slot_gender(subj, lx) == "n"
    vi = next(i for i, s in enumerate(slots) if s["role"] == "V")
    v = slots[vi].get("verb", {})
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
            form = lx.cells(lid)[feat][0]
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
            case = ROLE_CASE["PRED" if role == "PRED" else head["role"]] if role != "MOD" else ROLE_CASE[head["role"]]
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
            elif s.get("participle"):
                form = lx.participle_cells(lid, s["participle"].get("voice", "ACT"), g)[feat][0]
                feat = f"PTCP.{s['participle'].get('voice', 'ACT')}.{feat}"
            elif lx.specs[lid]["family"] == "adj":
                form = lx.cells(lid, g)[feat][0]
            else:
                form = lx.cells(lid)[feat][0]
        words[i] = Word(form, lid, lx.gloss(lid), feat, i, clitic=form in ENCLITIC_PRONOUNS)

    # phrases: every MOD/POSS goes directly before its head, recursively
    def phrase(i: int) -> list[int]:
        mods = [j for j, x in enumerate(slots) if x["role"] in ("MOD", "POSS") and x.get("head") == i and j != i]
        deps = [j for j, x in enumerate(slots) if x.get("dep") == i and j != i]   # a participle's own object etc.
        return [k for j in deps + mods for k in phrase(j)] + [i]

    order_roles = ["VOC", "SUBJ", "IO", "OBJ", "GOAL", "INS", "LOC", "ABL", "PRED", "ADV"]
    tops = [i for i, x in enumerate(slots) if x["role"] not in ("V", "MOD") and x.get("dep") is None and not
            (x["role"] == "POSS" and x.get("head") is not None)]
    tops.sort(key=lambda i: order_roles.index(slots[i]["role"]) if slots[i]["role"] in order_roles else 99)
    phrases = [phrase(t) for t in tops]
    # interrogatives move to the front of the clause (with their phrase)
    q = [ph for ph in phrases if any(slots[j]["lex_id"].startswith("closed:interrogative") for j in ph)]
    phrases = q + [ph for ph in phrases if ph not in q]
    seq = [j for ph in phrases for j in ph]
    placed = sorted(seq + [vi])
    if placed != list(range(len(slots))):
        missing = sorted(set(range(len(slots))) - set(placed))
        raise KeyError(f"slots {missing} not attached to the clause (a MOD/POSS head chain is broken)")
    for i in seq:
        if slots[i]["lex_id"] == "closed:indefinite_kwi":
            words[i].clitic = True        # the indefinite is enclitic: ne kʷis gʷémt 'no one came'
    neg = Word("mē" if (prohibitive or neg_wish) else "ne", "closed:particle:ne", "NEG", "PARTICLE") \
        if cl.get("neg") else None
    vseq = ([neg] if neg else []) + [words[vi]]
    def render_phrase(ph: list[int]) -> list[Word]:
        ws = []
        for i in ph:
            if words[i].clitic:
                continue
            ws.append(words[i])
            if slots[i].get("and"):
                ws.append(Word("-kʷe", "closed:particle:-kʷe", "and", "PARTICLE", clitic=True))
        return ws

    front = [w for ph in q for w in render_phrase(ph)]           # fronted interrogative phrase(s)
    rest = [w for ph in phrases if ph not in q for w in render_phrase(ph)]
    out = front + vseq + rest if cl.get("order") == "VSO" else front + rest + vseq
    if cl.get("particle") == "nu":
        out.insert(0, Word("nu", "closed:particle:nu", "NU", "PARTICLE"))
    if cl.get("particle") == "yod":       # h₁yód 'if, when' (Ved. yád): a subordinate clause, verb-final
        out.insert(0, Word("h₁yód", "closed:relative_yo/n", "if/when", "CONJ"))
    # Wackernagel: enclitics after the first word, "and" (-kʷe) / "or" (-wē) on the first word
    clitics = [words[i] for i in seq if words[i].clitic]
    if cl.get("particle") == "ge":
        clitics.insert(0, Word("-ge", "closed:particle:-ge", "EMPH", "PARTICLE", clitic=True))
    out[1:1] = clitics
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
