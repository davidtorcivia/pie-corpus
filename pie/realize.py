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
                "neg": false | true | "ne" | "mē",  # true: ne before the verb (mē with IMP, OPT and 1st-person
                                                   # SBJV 'let me not'); "ne"/"mē" pick it ("ne" + 1sg SBJV:
                                                   # 'I shall not …', Hom. οὐδὲ ἴδωμαι)
                "particle": null | "nu" | "ge" | "yod",  # nu "now, then"; -ge emphatic (enclitic); h₁yód "if, when"
                "break": false,                    # this clause starts a new sentence
                "question": false,                 # this clause's sentence ends in "?"
                "type": "verbal" | "nominal" | "np",  # see Clause types below; default verbal
                "case": "NOM",                     # np utterances only: the case of the NP (VOC for addresses)
                "slots": [
      {"lex_id": "pie-lex-…" | "closed:personal/1" | …,
       "role": "SUBJ|OBJ|IO|INS|LOC|ABL|POSS|VOC|PRED|GOAL|MOD|APPOS|NP|ADV|V",
       "num": "SG|DU|PL",                          # nominals; MOD and V take it from their head/subject, APPOS when unset
       "head": null | <slot index>,                # MOD (adjective, demonstrative, POSS), APPOS → its noun
       "before": false,                            # APPOS: stand before the head instead of after it
       "enclitic": false,                          # pronoun slots: the enclitic form (moy, toy, …)
       "gender": null | "m|f|n",                   # pronoun slots used on their own (tod "it", kʷíd "what")
       "and": false,                               # -kʷe "and" after this word (X Y-kʷe = X and Y)
       "dep": null | <slot index>,                 # a participle's own object; or a GOAL/LOC/ABL/INS/IO noun governed
                                                   # by an ADV adposition, placed before it (tóns próti 'toward them');
                                                   # or the ABL standard of a comparative / POSS of a superlative
       "degree": null | "CMP" | "SUP",             # adjective slots: comparative *-yos-, superlative *-isto- (below)
       "verb": {"tense": "PRS|PST|AOR|PRF", "mood": "IND|IMP|SBJV|OPT", "voice": "ACT|MID",
                "person": null | 1 | 2 | 3,       # person and number default to the subject's (3SG without one);
                "num": null | "SG|DU|PL"}}]}]}    # set them for pro-drop ("let us go": person 1, num PL, no SUBJ)

`check_plan` lists every problem; `realize` assumes a checked plan. `plan_warnings` lists likely problems that
do not block realization (a 3rd-person pronoun with no referent of its gender and number nearby).
All three compute each grammatical fact once (David's review: they used to disagree): agreement through
`clause_controller` / `group_agreement` (subjects, vocative addressees, predicate adjectives, pro-drop,
numerals, coordination), cells through `Lexicon.admissible_cells` (also used by pie.export). Coordinated
singulars: two take the dual, more the plural; a dual controller takes a plural verb only where the dual
cell does not exist. Several same-role slots without "and" are one referent named twice (dyḗws ph₂tḗr) unless
the verb's explicit number reads them as several ('Father, Mother, give!' 2DU); APPOS says it unambiguously.
Tests run plans through tests/helpers.produce (check_plan, then realize).

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
  It takes its head's case. Its number is its own when the slot (or a numeral MOD on it) sets one ('the
  blood-price, a hundred cows': kʷoynéh₂m ḱm̥tóm gʷṓs, SG head, PL apposition; apposition agrees in case, not
  necessarily in number: Lat. Athenae, urbs; Gk Θῆβαι, πόλις), else its head's. A noun keeps its own gender, an
  adjective (used as a noun) takes the head's gender unless the slot gives one. It may carry its own MOD/POSS/APPOS. It stands after its head's
  phrase; "before": true puts it before. Any nominal slot (SUBJ, OBJ, VOC, PRED, POSS, NP, APPOS …) can head
  an APPOS; a MOD cannot. Unlike MOD it is a separate phrase (Ringe 2017 §3.3.2: nouns in apposition are
  separate NPs), so an adjective there reads 'the immortal ones', not 'immortal'.

Degrees of comparison (pie.degree; docs/morphology-comparison-and-comitative.md). "degree": "CMP" | "SUP" on an
  adjective slot (MOD, PRED, APPOS, or a noun role with a gender) builds the primary comparative or superlative on
  the adjective's root: swéh₂dus → swéh₂dyōs 'sweeter', swéh₂distos 'sweetest' (Fortson §6.78, §6.81; Beekes §14.4;
  Handbook ch. 122: Ved. svā́dīyas-, svā́diṣṭha-, Gk ἡδίων, ἥδιστος). Comparative: common-gender s-stem, nom. -yōs, acc.
  -yosm̥, gen. -isés …, neuter -yos; superlative: thematic -istos/-isteh₂/-istom. Only primary adjectives take them
  (-u-, -ro-, -mo-, root-accented thematic, zero-grade *-ó-, root adjectives like méǵh₂s); check_plan rejects the
  rest with the reason (-tó- participles, -yo- relational adjectives, compounds …). The token's lex_id is
  "degree:<CMP|SUP>:<lex_id>", its gloss "sweet.CMP", and it carries degree_status: "nuclear-IE" (comparative: not in
  Anatolian or Tocharian) or "late-IE" (superlative: built later on the comparative's *-is-; Italic and Celtic
  have *-is-m̥mo- instead, Ringe 2006 §2.4.2(iii)). The standard of comparison ('than the wolf') is an ABL slot with "dep": <the comparative slot>,
  placed before it (the ablative of comparison: Ringe 2006 §2.3.1; Old Iranian, Handbook ch. 35 §5.4, Av. aniiō
  θβāt̰ 'other than you');
  a superlative's 'of the horses' is a POSS slot with "dep": <the superlative slot> (partitive genitive).
Personal pronouns under an adposition. A closed:personal/1|2|refl slot may be the dep of an ADV adposition in any
  role of ADPOSITION_ROLES. The 1st/2nd-person pronouns have no instrumental or locative (Ringe 2006 p. 57): as
  the dep of an adposition, INS ('with me': ḱóm) and LOC ('among us') are realized in the dative, méǵʰye ḱóm,
  n̥sméy médʰi, and the token says case_fallback "ins->dat" / "loc->dat" (PRONOUN_ADPOSITION_CASE). Elsewhere a
  pronoun INS or LOC is a plan error; a pronoun governed by an adposition is never enclitic.
Interrogative and correlative adverbs. closed:interrogative_adv/why|when|where|how|how_many (kʷíd, kʷóm, kúdʰe,
  kʷíh₁, kʷóti) and closed:correlative_adv/so_many|as_many (tóti, h₁yóti) are indeclinable (closed_class.json, with
  their refs): role ADV; the three quantifiers also MOD with a head, which takes the plural. Interrogatives front
  like the interrogative pronouns ('where did the horse go?' = kúdʰe h₁éḱwos …).
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
  a noun lex_id: thematic (-o-) or i-/u-stem noun, its stem as is (Gk khrūsó-thronos, Ved. bāhú-ojas-); h₂nḗr 'man'
      in its zero grade h₂nr̥- (Ved. nṛ-máṇas-, Av. Nərəmanah-; compound.ZERO_GRADE_FIRST), unaccented.
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
  déms-; except h₂nḗr, compound.ZERO_GRADE_FIRST), verbal governing compounds (*ḱlewos-dʰeh₁-, vr̥tra-hán-), Caland -i-, nested compounds.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .compound import CompoundError, resolve as resolve_compound
from . import degree as _degree
from .morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj, decline_participle

ROOT = Path(__file__).resolve().parent.parent
ACCENT_MANIFEST = ROOT / "data/morph/accent_unresolved.json"


@lru_cache(maxsize=1)
def accent_manifest() -> dict:
    """data/morph/accent_unresolved.json, the one source of accent status (docs/STATUS.md "Known limitations").
    Three categories stay apart: unresolved_lexical_accent (missing information: the headword has no accent),
    representation_exceptions (forms the notation and the initial vocative accent leave unmarked, ph₂ter) and
    the genuinely unaccented clitics (not listed there). Adds two derived sets: "unresolved_ids" and
    "exception_cells" ((lex_id, gender, cell, form) tuples)."""
    m = json.loads(ACCENT_MANIFEST.read_text("utf-8"))
    m["unresolved_ids"] = frozenset(i for f in m["unresolved_lexical_accent"]["by_family"].values() for i in f["ids"])
    m["exception_cells"] = frozenset((c["lex_id"], c["gender"], c["cell"], c["form"])
                                     for c in m["representation_exceptions"]["cells"])
    return m


def accent_status(lex_id: str | None) -> str:
    """"unresolved" for a lexeme whose accent the sources leave open (missing information, not an unaccented
    word); "resolved" otherwise (closed-class ids and unknown ids included)."""
    return "unresolved" if lex_id in accent_manifest()["unresolved_ids"] else "resolved"

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
    gender: str | None = None       # the resolved gender of a nominal (an adjective's is its head's)
    voice: str | None = None        # ACT | MID for verbs and participles
    num_fallback: str | None = None  # du->pl when the controller's dual cell is unavailable
    coined: str | None = None       # "project" for a project reconstruction (Lexicon.coined)
    degree_status: str | None = None  # a comparative "nuclear-IE" / superlative "late-IE" (pie.degree.STATUS)
    case_fallback: str | None = None  # "ins->dat" / "loc->dat": a 1st/2nd-person pronoun under an adposition


PROJECT_RECONSTRUCTIONS = ROOT / "data/lexicon/project_reconstructions.jsonl"


def load_project_reconstructions(path: Path = PROJECT_RECONSTRUCTIONS) -> tuple[dict, dict]:
    """(entries, specs) of the project reconstructions (PLAN.md "Project reconstructions",
    docs/lexicon-project-reconstructions.md). Each line is a lexicon entry with source "project" and
    coined "project", plus an "inflection" record in the inflection_specs.jsonl schema; it is split here
    into the entry and its spec. The one loader: Lexicon.load and pie.validate.index_project read it."""
    entries, specs = {}, {}
    if not path.exists():
        return entries, specs
    for x in path.read_text("utf-8").splitlines():
        if not x.strip():
            continue
        e = json.loads(x)
        if e.get("source") != "project" or e.get("coined") != "project":
            raise ValueError(f"{e.get('id')}: a project reconstruction needs source and coined 'project'")
        inf = e.pop("inflection", None)
        entries[e["id"]] = e
        if inf:
            specs[e["id"]] = {"id": e["id"], "form": e["form"], **inf}
    return entries, specs


def plan_coined(plan: dict, lx: "Lexicon") -> list[str]:
    """The project-reconstruction lexemes a plan uses (slots and compound members), in order."""
    out = []
    for cl in plan.get("clauses", []):
        for s in cl.get("slots", []):
            c = s.get("compound") if s.get("lex_id") == "compound" and isinstance(s.get("compound"), dict) else {}
            for i in (s.get("lex_id"), c.get("first"), c.get("second")):
                if isinstance(i, str) and lx.coined(i) and i not in out:
                    out.append(i)
    return out


@dataclass
class Lexicon:
    entries: dict
    specs: dict
    closed: dict
    derived: dict = field(default_factory=dict)     # approximate glosses (pie/glosses.py)
    blocked: dict = field(default_factory=dict)     # lex_id → reason (data/generation/blocklist.jsonl)
    _cache: dict = field(default_factory=dict)

    def __post_init__(self):
        from .research_scope import research_entry, mapping_scope, RESEARCH_ONLY
        if any(research_entry({**e, "id": i}) for i, e in self.entries.items()) or any(
            mapping_scope((i,), r.get("scope")) == RESEARCH_ONLY for i, r in self.specs.items()
        ):
            raise ValueError("research_only entries/specs cannot enter the production Lexicon")

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
        # project reconstructions (PLAN.md): flagged coined, Tier 3/3b only; never in the default validator index
        p_lex, p_specs = load_project_reconstructions()
        if p_lex.keys() & lex.keys():
            raise ValueError(f"project reconstruction id already in lexicon.jsonl: {sorted(p_lex.keys() & lex.keys())}")
        lex.update(p_lex)
        specs.update(p_specs)
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
        # reflex-confirmed glosses (pie.glosses.confirm; docs/lexicon.md): a lexeme without a dictionary gloss
        # whose own reflexes in >= 2 branches agree gets that gloss, tagged meaning_source "reflex-confirmed"
        p = ROOT / "data/lexicon/confirmed_glosses.jsonl"
        if p.exists():
            for x in p.read_text("utf-8").splitlines():
                d = json.loads(x)
                e = lex.get(d["id"])
                if e is not None and not e["meaning"]:
                    lex[d["id"]] = {**e, "meaning": [d["gloss"]], "meaning_source": "reflex-confirmed"}
        return cls(lex, specs, closed, derived, blocked)

    def accent_status(self, lex_id: str) -> str:
        """"resolved" | "unresolved" (module accent_status: data/morph/accent_unresolved.json)."""
        return accent_status(lex_id)

    def coined(self, lex_id: str | None) -> str | None:
        """"project" when the lexeme, or a member of a compound, is a project reconstruction
        (data/lexicon/project_reconstructions.jsonl); None otherwise. The one source of the token flag."""
        from .compound import member_ids
        for i in [lex_id or "", *member_ids(lex_id or "")]:
            c = self.entries.get(i, {}).get("coined")
            if c:
                return c
        return None

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

    # --- admissible cells: the one place that says which cells of a lexeme a text may use ------------------
    # check_plan (through realize_clause), pie.export.inflection_tasks and pie.export.token_variants all read
    # these, so a cell the planner may not ask for is never offered as an exercise or an alternative.
    # Restrictions in the data today: blocked lexemes (data/generation/blocklist.jsonl) and unusable specs
    # have no cells; middle-only (deponent) verbs, lemma in -tor/-toy (Fortson §5.6, L&Y §4.3.1), have only
    # middle cells; an adjective's cells are those of one gender; a noun has its own gender only; a cell the
    # engine does not build (the 2du/3du middle and perfect, dual obliques) is absent. The lexicon has no
    # active-only, singulare/plurale tantum or per-cell defectivity markers yet; such a marker belongs here.

    def inadmissible(self, lex_id: str) -> str | None:
        """Why no cell of the lexeme may be used (blocked, unknown, unusable), or None."""
        if lex_id in self.blocked:
            return f"{lex_id} is blocked from generation: {self.blocked[lex_id]}"
        r = self.specs.get(lex_id)
        if r is None:
            return f"unknown or non-inflectable lex_id {lex_id!r}"
        if not r.get("usable"):
            return f"{lex_id} has no usable spec (rule {r['rule']})"
        return None

    def middle_only(self, lex_id: str) -> bool:
        """A deponent (media tantum): the lemma is a middle form (mn̥yétor, ḱéytor; engine sweep defect 10)."""
        return (self.specs.get(lex_id) or {}).get("family") == "verb" and \
            self.entries.get(lex_id, {}).get("form", "").endswith(("tor", "toy"))

    def voices(self, lex_id: str) -> tuple[str, ...]:
        """The voices a verb may take: ('MID',) for a deponent; otherwise those the engine builds cells for."""
        if self.inadmissible(lex_id) or self.specs[lex_id]["family"] != "verb":
            return ()
        if self.middle_only(lex_id):
            return ("MID",)
        c = self.cells(lex_id)
        return tuple(v for v in ("ACT", "MID") if any(cell_voice(k) == v for k in c))

    def admissible_cells(self, lex_id: str, gender: str | None = None) -> dict:
        """feature → forms for the cells a plan may use. An adjective needs its gender (masculine was a silent
        default: neuter sweh₂dú got masculine sweh₂dús as an 'acceptable' alternative); a noun asked for a
        gender other than its own has none."""
        k = ("ADM", lex_id, gender)
        if k in self._cache:
            return self._cache[k]
        out: dict = {}
        if not self.inadmissible(lex_id):
            fam = self.specs[lex_id]["family"]
            if fam == "adj":
                if gender not in ("m", "f", "n"):
                    raise ValueError(f"{lex_id}: an adjective's cells need a gender (m, f or n)")
                out = self.cells(lex_id, gender)
            elif fam == "noun":
                out = self.cells(lex_id) if gender in (None, self.gender(lex_id)) else {}
            else:
                voices = self.voices(lex_id)
                out = {f: v for f, v in self.cells(lex_id).items() if cell_voice(f) in voices}
        self._cache[k] = out
        return out

    def degree_cells(self, lex_id: str, degree: str, gender: str) -> dict:
        """An adjective's comparative (CMP) or superlative (SUP) cells in one gender (pie.degree; the realizer, the
        validator and pie.export read them here). {} for a lexeme that may not be used; DegreeError for one whose
        degree the engine cannot build."""
        if self.inadmissible(lex_id):
            return {}
        return _degree.cells(lex_id, degree, gender, self)

    def admissible_participle_cells(self, lex_id: str, voice: str, gender: str) -> dict:
        """A participle's case forms, or {} for a voice the verb may not take (a deponent's is middle)."""
        if voice not in self.voices(lex_id):
            return {}
        return self.participle_cells(lex_id, voice, gender)


def cell_voice(feat: str) -> str:
    """ACT or MID: the voice of a verb cell ('MID.PRS.3SG', 'PTCP.MID'; anything else is active)."""
    return "MID" if feat.startswith(("MID.", "PTCP.MID")) else "ACT"


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
    if isinstance(node, list):        # indeclinables: closed:numerals/indeclinable/7, closed:interrogative_adv/why
        return node[0]
    if path[0] == "numerals":
        node = node.get(gender) or node.get("fn" if gender in ("f", "n") else "m") or node.get("m", {})
        if feat.endswith(".SG") or feat.endswith(".DU"):  # 2 is dual, 3 and 4 plural: number follows the numeral
            feat = feat.rsplit(".", 1)[0] + (".DU" if path[1] == "2" else ".PL")
    forms = node.get(feat) if isinstance(node, dict) else None
    if not forms and path[0] == "personal" and isinstance(node, dict):
        forms = node.get(feat + ".ENCL")      # no book prints a stressed 1st/2nd pl. genitive (Ringe: "???")
    return forms[0] if forms else None


# indeclinable closed adverbs (closed_class.json interrogative_adv, correlative_adv): role ADV; the quantifiers
# also MOD with a head, which they put in the plural like a numeral ('how many horses': kʷóti h₁éḱwōs, Lat. quot)
CLOSED_ADVERBS = ("interrogative_adv", "correlative_adv", "deictic_adv")   # deictic_adv: 'here' h₁idʰé
CLOSED_QUANTIFIERS = ("closed:interrogative_adv/how_many", "closed:correlative_adv/so_many",
                      "closed:correlative_adv/as_many")


def closed_adverb_ids(lx: Lexicon) -> list[str]:
    """closed:interrogative_adv/why, … : every indeclinable closed adverb id (make_slice offers them)."""
    return [f"closed:{sec}/{k}" for sec in CLOSED_ADVERBS for k in lx.closed.get(sec, {}) if not k.startswith("_")]


def _check_closed(s: dict, slots: list, where: str, lx: Lexicon) -> list[str]:
    """A closed id must exist; an indeclinable closed adverb is an ADV (a quantifier also a MOD with a head)."""
    lid = s.get("lex_id", "")
    path = lid.split(":", 1)[1].split("/")
    if path[0] not in CLOSED_ADVERBS:
        return []
    if not isinstance(lx.closed.get(path[0], {}).get(path[1] if len(path) > 1 else "_"), list):
        return [f"{where}: unknown closed id {lid} (the slice's closed list names them)"]
    role = s.get("role")
    if role == "MOD" and lid in CLOSED_QUANTIFIERS:
        h = s.get("head")
        if not (isinstance(h, int) and 0 <= h < len(slots)) or slots[h].get("role") in ("V", "MOD", "ADV"):
            return [f"{where}: MOD needs a nominal head slot"]
        return []
    if role == "ADV":
        return []
    return [f"{where}: {lid} is an indeclinable adverb: role ADV"
            + (" (or MOD with a head: 'how many horses')" if lid in CLOSED_QUANTIFIERS else "")]


def _closed_feat(lx: Lexicon, lex_id: str, feat: str) -> str:
    """The feature actually realized: a personal-pronoun cell that falls back to the enclitic says so
    (engine sweep, closed-class-compounds.md R3)."""
    if lex_id.startswith("closed:personal/") and not feat.endswith(".ENCL"):
        node = lx.closed["personal"].get(lex_id.split("/")[1], {})
        if feat not in node and feat + ".ENCL" in node:
            return feat + ".ENCL"
    return feat


# --- agreement: computed once, used by check_plan, realize_clause and plan_warnings --------------------------
# (David's review: the checker, the realizer and the warnings each had their own rules, so they disagreed:
# check_plan dropped the vocative conjunct marked "and" and knew only the numerals 2-4.)

@dataclass(frozen=True)
class Agreement:
    """What a verb, a predicate adjective or an anaphor agrees with: a noun phrase or a group of them."""
    person: int
    num: str            # the phrase's number (a predicate adjective takes it)
    gender: str | None  # None for a pro-drop subject (the verb names no gender)
    verb_num: str       # what a finite verb takes: neuter plurals are collectives and take SG
    alt: tuple = ()     # other numbers the slots allow when their referents cannot be counted from the plan
    alt_gender: str | None = None   # the group's gender under an alternative reading

    def verb_nums(self) -> set[str]:
        return {self.verb_num, *self.alt}

    def resolve(self, num: str | None) -> "Agreement":
        """The reading an explicit verb number picks (one of alt); otherwise the default reading."""
        if num and num in self.alt and num != self.verb_num:
            return Agreement(self.person, num, self.alt_gender or self.gender, num)
        return self


def numeral_number(lex_id: str) -> str | None:
    """The number a numeral gives the noun it counts: 1 SG, 2 DU, 3 and up PL (closed:numerals/2,
    closed:numerals/indeclinable/7), and the quantifiers kʷóti, tóti, h₁yóti PL; None for anything else."""
    if lex_id in CLOSED_QUANTIFIERS:
        return "PL"
    if not lex_id.startswith("closed:numerals/"):
        return None
    try:
        n = int(lex_id.rsplit("/", 1)[1])
    except ValueError:
        return None
    return "SG" if n == 1 else "DU" if n == 2 else "PL"


def slot_number(slots: list, i: int) -> str:
    """A nominal slot's number: a numeral MOD on it decides (t016 review: 'two dogs' with num unset came out
    singular), else its num, else SG."""
    for m in slots:
        if m.get("role") == "MOD" and m.get("head") == i:
            n = numeral_number(m.get("lex_id", ""))
            if n:
                return n
    return slots[i].get("num") or "SG"


def coordination_groups(slots: list) -> dict:
    """(role, head) → slot indices; a group with more than one member and an "and" on any of them is a
    coordination (X Y-kʷe). realize_clause moves the -kʷe to the last member; the group is the same."""
    groups: dict = {}
    for i, s in enumerate(slots):
        if s.get("role") not in ("V", "MOD", "ADV"):
            groups.setdefault((s.get("role"), s.get("head")), []).append(i)
    return groups


def role_group(slots: list, role: str) -> tuple[list[int], bool]:
    """The clause-level slots of a role (head None) and whether they are coordinated (more than one, with an
    "and" on any member)."""
    ix = coordination_groups(slots).get((role, None), [])
    return ix, len(ix) > 1 and any(slots[i].get("and") for i in ix)


def phrase_agreement(slots: list, i: int, lx: Lexicon) -> Agreement:
    s = slots[i]
    lid = s.get("lex_id", "")
    num = slot_number(slots, i)
    person = int(lid.split("/")[1]) if lid.startswith("closed:personal/") and lid.split("/")[1] in ("1", "2") else 3
    g = _slot_gender(s, lx)
    # a neuter plural subject takes a singular verb (Gk τὰ ζῷα τρέχει, Av., Hitt.): the old collective
    return Agreement(person, num, g, "SG" if person == 3 and num == "PL" and g == "n" else num)


def group_agreement(slots: list, idxs: list[int], lx: Lexicon, coordinated: bool = True) -> Agreement:
    """A noun phrase (one index) or a group of same-role slots.

    Coordinated (X Y-kʷe; Fortson §8.16): two singulars dual, else plural; 1st person over 2nd over 3rd;
    masculine if any member is or the genders differ; neuter plurals together stay collective (Il. 2.468
    phúlla kaì ánthea gígnetai). Each slot counts as a referent; with three or more singular slots two of
    them may be one referent named twice (dyḗws ph₂tḗr dʰéǵʰōm méh₂tēr-kʷe: two addressees), so the dual is
    an alternative reading an explicit verb number may pick.
    Not coordinated (several slots, no "and"): one referent named twice by default (dyḗws ph₂tḗr 'Father
    Sky'); an asyndetic pair or list (ph₂ter, méh₂ter 'Father, Mother') is the alternative reading."""
    parts = [phrase_agreement(slots, i, lx) for i in idxs]
    if len(parts) == 1:
        return parts[0]
    gs = {p.gender for p in parts}
    g = gs.pop() if len(gs) == 1 else "m"
    person = min(p.person for p in parts)
    all_sg = all(p.num == "SG" for p in parts)
    if not coordinated:
        alt = (("DU",) + (("PL",) if len(parts) > 2 else ())) if all_sg else ("PL",)
        first = parts[0]
        return Agreement(first.person, first.num, first.gender, first.verb_num,
                         tuple(n for n in alt if n != first.verb_num), g)
    if all(p.person == 3 and p.num == "PL" and p.gender == "n" for p in parts):
        return Agreement(3, "PL", "n", "SG")
    num = "DU" if len(parts) == 2 and all_sg else "PL"
    return Agreement(person, num, g, num, ("DU",) if len(parts) > 2 and all_sg else (), g)


EXEMPT_SUBJECTS = ("closed:relative_yo", "closed:interrogative_")


def clause_controller(cl: dict, lx: Lexicon) -> tuple[Agreement, str]:
    """What the clause's finite verb and predicate adjective agree with, and its source:
      'SUBJ'  the subject, or the subjects as a group (group_agreement);
      'VOC'   no subject and a 2nd-person verb: the addressee(s) ("waters, flow!" 2PL; "Sky and Earth, hear!" 2DU);
      'verb'  pro-drop: the verb's own person and number (3SG by default; "let us go": 1PL).
    An explicit verb number picks one of the group's alternative readings (Agreement.resolve). A relative or
    interrogative subject takes its person from the antecedent or addressee ("you who split the vault":
    h₁yós … 2SG): see EXEMPT_SUBJECTS."""
    slots = cl.get("slots", [])
    v = next((s.get("verb") or {} for s in slots if s.get("role") == "V"), {})
    subj, co = role_group(slots, "SUBJ")
    if subj:
        return group_agreement(slots, subj, lx, co).resolve(v.get("num")), "SUBJ"
    voc, co = role_group(slots, "VOC")
    if voc and str(v.get("person")) == "2":
        a = group_agreement(slots, voc, lx, co)
        # an addressed neuter plural is not a collective: "waters, flow!" is 2PL
        return Agreement(2, a.num, a.gender, a.num, tuple(n for n in a.alt if n != a.num), a.alt_gender
                         ).resolve(v.get("num")), "VOC"
    num = v.get("num") or "SG"
    return Agreement(int(v.get("person") or 3), num, None, num), "verb"


def _exempt(cl: dict, kind: str) -> bool:
    """A relative or interrogative subject: the verb's own person and number stand."""
    return kind == "SUBJ" and any(cl["slots"][i].get("lex_id", "").startswith(EXEMPT_SUBJECTS)
                                  for i in role_group(cl["slots"], "SUBJ")[0])


def verb_person_number(cl: dict, v: dict, lx: Lexicon) -> tuple[int, str]:
    """The finite verb's person and number (before the dual-to-plural fallback of finite_cell). An overt
    controller decides (check_plan rejects a verb person/num that contradicts it); with pro-drop or an exempt
    subject the verb's own person and num stand."""
    a, kind = clause_controller(cl, lx)
    if kind == "verb" or _exempt(cl, kind):
        return int(v.get("person") or a.person), v.get("num") or a.verb_num
    return int(v.get("person") or a.person), a.verb_num


def finite_cell(lx: Lexicon, lid: str, v: dict, person: int, num: str, prohibitive: bool) -> str:
    """The verb cell realized for person and number: mē + injunctive (augmentless secondary form) for a
    prohibitive; where no dual cell exists (the 2du/3du middle and perfect, Ringe 2006 pp. 31-32) the plural
    stands in (check_plan rejects the 2du/3du perfect: _check_perfect_dual; the middle keeps the flagged fallback).
    Raises KeyError if the cell is not admissible."""
    mood, tense, voice = v.get("mood", "IND"), v.get("tense", "PRS"), v.get("voice", "ACT")
    base = {"IND": tense, "IMP": "IMP", "SBJV": "SBJV", "OPT": "OPT"}[mood]
    mid = "MID." if voice == "MID" else ""
    feat = f"{mid}{base}.{person}{num}"
    cells = lx.admissible_cells(lid)
    if prohibitive:
        feat = next((f"{mid}{t}.{person}{num}" for t in ("PST", "AOR") if f"{mid}{t}.{person}{num}" in cells), feat)
    if feat not in cells and feat.endswith("DU") and feat[:-2] + "PL" in cells:
        feat = feat[:-2] + "PL"
    if feat not in cells:
        raise KeyError(f"{lid} {feat}")
    return feat


def _check_agreement(ci: int, cl: dict, slots: list, verbs: list, lx: Lexicon) -> list[str]:
    """An explicit person/number on the verb is for pro-drop; with an overt subject or addressee it must
    agree with it (David's review: SUBJ gʷówes PL + verb num SG gave 'gʷówes trémt'; 'waters, flow!' is PL;
    'Sky and Earth, hear!' is DU). A dual controller may take a plural verb only where the dual cell does not
    exist."""
    if len(verbs) != 1:
        return []
    v = verbs[0].get("verb") or {}
    try:
        a, kind = clause_controller(cl, lx)
    except Exception:
        return []
    if kind == "verb" or _exempt(cl, kind):
        return []
    errs = []
    if kind == "SUBJ" and v.get("person") and int(v["person"]) != a.person:
        errs.append(f"clause {ci}: the verb's person {v['person']} contradicts its subject (person {a.person}); "
                    f"drop the verb's person or the subject")
    if v.get("num") and v["num"] not in a.verb_nums():
        ok = False
        if "DU" in a.verb_nums() and v["num"] == "PL":
            try:
                prohibitive = bool(cl.get("neg")) and v.get("mood") == "IMP"
                ok = finite_cell(lx, verbs[0]["lex_id"], v, int(v.get("person") or a.person), "DU",
                                 prohibitive).endswith("PL")
            except Exception:
                ok = True       # no such verb cell at all: reported by the realization check
        if not ok and kind == "SUBJ":
            collective = a.verb_num == "SG" and a.num == "PL"
            errs.append(f"clause {ci}: the verb's number {v['num']} contradicts its subject ({a.verb_num}"
                        f"{', a neuter plural takes a singular verb' if collective else ''}"
                        f"{', and the dual cell exists' if a.verb_num == 'DU' and v['num'] == 'PL' else ''}); "
                        f"drop the verb's num, or fix the subject's num")
        elif not ok:
            errs.append(f"clause {ci}: the 2nd-person verb's number {v['num']} contradicts the addressee "
                        f"(VOC {a.num}{', two addressees take the dual' if a.num == 'DU' else ''})")
    return errs


def _check_two_oblique(ci: int, cl: dict, lx: Lexicon) -> list[str]:
    """'two' in an oblique case: the numeral has its dual oblique (dwóbʰih₁, dwóyh₁s), but the counted noun's dual
    oblique is not reconstructible and the plural stands in (realize_clause), so the pair disagreed in number
    (t059 review: dwóbʰih₁ with an instrumental plural, three dialogues). Rejected, so the planner puts the pair
    in the NOM/ACC (dual), names the two, or drops the numeral."""
    try:
        words = realize_clause(cl, lx)
    except (KeyError, ValueError, IndexError, TypeError):
        return []                     # a malformed clause: its own errors are reported by the other checks
    return [f"clause {ci}: 'two' ({w.form}, {w.features}) in an oblique case: its noun's dual oblique does not "
            f"exist and the plural stands in, so the pair disagrees; put the pair in the NOM/ACC, name the two, or "
            f"drop the numeral" for w in words
            if w.lex_id.startswith("closed:numerals/2") and w.features.split(".")[0] not in ("NOM", "ACC", "VOC")]


def _check_perfect_dual(ci: int, cl: dict, verbs: list, lx: Lexicon) -> list[str]:
    """The perfect has no 2nd or 3rd dual: Ringe 2006 p. 32 ('the dual endings are not reconstructable because
    Greek and Indo-Iranian disagree'). Fortson §5.51 prints none either. The realizer would put the plural in
    their place (finite_cell's du→pl), so a dual pair addressed or described with a perfect came out plural in
    an otherwise dual clause (t023 66dc51f8, t024 00010). Rejected, whether the dual comes from the verb's
    num, a dual subject or two coordinated singulars, so the planner picks a present or aorist. (The middle
    2du/3du are no better reconstructed, Ringe p. 31, but no tense avoids them; they keep the flagged
    fallback.)"""
    if len(verbs) != 1:
        return []
    v = verbs[0].get("verb") or {}
    if v.get("tense") != "PRF" or v.get("mood", "IND") != "IND":
        return []
    try:
        person, num = verb_person_number(cl, v, lx)
    except Exception:
        return []
    if num != "DU" or person == 1:
        return []
    return [f"clause {ci}: the perfect has no {person}du (Ringe 2006 p. 32: not reconstructible, Greek and "
            f"Indo-Iranian disagree), and a plural would stand in for the dual; use a present or aorist verb for "
            f"a dual subject or addressee (h₁r̥tóm, sth₂éh₁yetes)"]


NEG_VALUES = (False, True, None, "ne", "mē")


def _check_neg(ci: int, cl: dict, ctype: str, verbs: list) -> list[str]:
    """`neg`: true picks the particle (ne; mē with IMP, OPT and the 1st-person SBJV); "ne" and "mē" choose it.
    "ne" + 1st-person SBJV is a negated statement of will or the future ('I shall not …'): Hom. οὐδὲ ἴδωμαι
    'nor shall I see' (Il. 1.262), the prospective subjunctive negated with οὐ, against hortatory μή 'let me
    not'; Ved. ná + subjunctive likewise (t027, t028 reviews)."""
    n = cl.get("neg")
    if n not in NEG_VALUES:
        return [f"clause {ci}: neg must be true, false, \"ne\" or \"mē\", not {n!r}"]
    if not isinstance(n, str):
        return []
    mood = ((verbs[0].get("verb") or {}).get("mood", "IND") if len(verbs) == 1 else None)
    if n == "ne" and mood in ("IMP", "OPT"):
        return [f"clause {ci}: neg \"ne\" cannot go with {mood}: a prohibition is mē + injunctive (neg + IMP), "
                f"a negative wish mē + optative"]
    if n == "mē" and (ctype != "verbal" or mood == "IND"):
        return [f"clause {ci}: neg \"mē\" negates a command, wish or exhortation (IMP, OPT, SBJV); a statement "
                f"takes ne (neg: true)"]
    return []


def _check_imp_person(ci: int, cl: dict, verbs: list) -> list[str]:
    """An imperative with no person and no subject is 3rd person ('let him go'). With a VOC in the clause it is
    almost always a command to the addressee (t027 review: 12 of the 14 wrong items, h₁ógʷʰey h₁nédʰtu 'Serpent,
    let him come forth'). So the planner must say which one it means. A person-less IMP with no VOC stays
    3rd person: the approved records have 56 such commands with no VOC ('whoever has a dog, let him feed it')."""
    if len(verbs) != 1:
        return []
    v = verbs[0].get("verb") or {}
    slots = cl.get("slots", [])
    if v.get("mood") != "IMP" or v.get("person") or any(s.get("role") == "SUBJ" for s in slots) \
            or not any(s.get("role") == "VOC" for s in slots):
        return []
    return [f"clause {ci}: an imperative beside a VOC needs a person: 2 to command the addressee ('Serpent, come "
            f"forth!'), or 3 for 'let him …'; without one it would be 3rd person"]


# the cases an adposition governs, by the role of its dependent: 'toward X' GOAL (acc.), 'in X' LOC, 'from X' ABL,
# 'with X' INS, 'for X' IO (dat.)
ADPOSITION_ROLES = {"GOAL": "ACC", "LOC": "LOC", "ABL": "ABL", "INS": "INS", "IO": "DAT"}


def _check_adposition_dep(s: dict, head: dict, where: str, lx: Lexicon) -> list[str]:
    """A noun phrase governed by an adverb/adposition: {"role": "GOAL", "dep": <ADV slot>} 'toward them' (t033 review:
    próti took no object, and the planner left the "them" out). In PIE these were adverbs construed with a case
    form, postposed in Anatolian and Vedic (Fortson §8.8: Hitt. šuḫḫi šēr "on the roof", Ved. jánām̐ ánu "among men"); the
    dependent stands directly before its adposition and takes the case of its role. The head must be a lexicon
    adverb or adposition, not a closed interrogative or quantifier."""
    hid = head.get("lex_id", "")
    if hid.startswith("closed:") or lx.entries.get(hid, {}).get("pos") not in ("adv", "prep", "postp"):
        return [f"{where}: dep points at ADV {hid}, which is not an adverb or adposition that can govern a noun"]
    if s.get("role") not in ADPOSITION_ROLES:
        return [f"{where}: a noun governed by an adposition takes one of the roles "
                f"{', '.join(f'{r} ({c})' for r, c in ADPOSITION_ROLES.items())}, not {s.get('role')}"]
    return []


# --- personal pronouns under an adposition, and the cases they lack ---------------------------------------------
# The 1st/2nd-person and reflexive pronouns have no instrumental or locative: Ringe 2006 §2.3.6(iii) p. 57 prints
# four singular cases and '???' for the stressed plural oblique; Fortson §7.2 reconstructs little beyond the stems;
# only Beekes §15.3.1 offers a singular loc./ins. *h₁mói, *tói, which he calls unclear and which is the shape of
# his dative-genitive clitic. The daughters' instrumentals (Ved. máyā, OCS mъnojǫ, Lith. manimì) are each built
# anew. Governed by an adposition ('with me', 'among us') the pronoun takes the dative: the case a pronoun takes
# after 'with' in Greek (σύν + dat.), Gothic (miþ + dat., miþ sis; miþ is the cognate of médʰi, Kroonen s.v. *medi)
# and Old Irish (co + dat., the cognate of ḱóm); only Latin has the ablative (mē-cum, mē(d) < *h₁med: de Vaan s.v.
# com-, me). The token says so (case_fallback "ins->dat" / "loc->dat"). The evidence and the rejected alternatives
# are in docs/morphology-comparison-and-comitative.md.
PRONOUN_FALLBACK_CASES = ("INS", "LOC")
PRONOUN_ADPOSITION_CASE = "DAT"


def _governed_by_adposition(s: dict, slots: list) -> bool:
    d = s.get("dep")
    return isinstance(d, int) and 0 <= d < len(slots) and slots[d].get("role") == "ADV"


def pronoun_fallback(lx: Lexicon, s: dict, slots: list, case: str, num: str) -> str | None:
    """The case a personal pronoun takes instead of one it lacks: PRONOUN_ADPOSITION_CASE for an instrumental or
    locative governed by an adposition; None if the pronoun has the case or no fallback applies."""
    lid = s.get("lex_id", "")
    if not lid.startswith("closed:personal/") or s.get("enclitic"):
        return None
    if _closed_form(lx, lid, f"{case}.{num}", "m") is not None:
        return None
    if case in PRONOUN_FALLBACK_CASES and _governed_by_adposition(s, slots):
        return PRONOUN_ADPOSITION_CASE
    return None


def _check_personal_case(s: dict, si: int, slots: list, where: str, lx: Lexicon) -> list[str]:
    """A 1st/2nd-person or reflexive pronoun in a case it has no form for is a plan error with the reason (it used
    to surface as 'form not generated'); under an adposition the instrumental and locative fall back (above)."""
    lid, role = s.get("lex_id", ""), s.get("role")
    if not lid.startswith("closed:personal/") or role not in ROLE_CASE:
        return []
    if s.get("enclitic") and _governed_by_adposition(s, slots):
        return [f"{where}: a pronoun governed by an adposition is the stressed form (no enclitic): an enclitic "
                f"moves to the second position of the clause, away from its adposition"]
    case = ROLE_CASE[role]
    num = slot_number(slots, si)
    if num == "DU" and case not in ("NOM", "ACC", "VOC"):
        num = "PL"                    # dual obliques: the plural stands in (realize_clause)
    feat = f"{case}.{num}" + (".ENCL" if s.get("enclitic") else "")
    if _closed_form(lx, lid, feat, "m") is not None:
        return []
    fb = pronoun_fallback(lx, s, slots, case, num)
    if fb and _closed_form(lx, lid, f"{fb}.{num}", "m") is not None:
        return []
    who = {"1": "1st-person", "2": "2nd-person", "refl": "reflexive"}.get(lid.split("/")[1], "personal")
    hint = {"INS": " For 'with me / with you' put the pronoun under an adposition: ADV ḱóm (pie-lex-kjom) and the "
                   "pronoun as its dep with role INS ('méǵʰye ḱóm'); for 'by me' (agent or means) rephrase.",
            "LOC": " For 'in / among us' put the pronoun under an adposition (ADV h₁én, médʰi …) as its dep with role "
                   "LOC."}.get(case, "")
    return [f"{where}: the {who} pronoun has no {feat} form (Ringe 2006 p. 57: only the nominative, accusative, "
            f"genitive and dative are reconstructable in the singular, and the plural oblique only as an enclitic; "
            f"closed_class.json adds the ablative méd/twéd).{hint}"]


# --- degrees of comparison (pie.degree) ---------------------------------------------------------------------------
def _check_degree(s: dict, where: str, lx: Lexicon) -> list[str]:
    """"degree": "CMP" | "SUP" on an adjective slot: the engine must be able to build it from the root."""
    d = s.get("degree")
    lid = s.get("lex_id", "")
    if d not in _degree.DEGREES:
        return [f"{where}: degree must be one of {', '.join(_degree.DEGREES)}, not {d!r}"]
    if lid.startswith("closed:") or lid == "compound" or s.get("participle") is not None:
        return [f"{where}: a degree (comparative, superlative) is built on an adjective lexeme, not on "
                f"{'a participle' if s.get('participle') is not None else lid}"]
    if lx.inadmissible(lid):
        return []                     # reported once by check_plan's own lexeme check
    try:
        _degree.base(lid, lx)
    except _degree.DegreeError as e:
        return [f"{where}: {e}"]
    return []


def _check_degree_dep(s: dict, head: dict, where: str) -> list[str]:
    """The standard of comparison ('than X') is an ABL slot whose dep is the comparative (the ablative of
    comparison: Ringe 2006 §2.3.1; Old Iranian, Handbook ch. 35 §5.4); a superlative's 'of X' is a POSS slot (partitive genitive) whose dep is the
    superlative."""
    want = {"CMP": "ABL", "SUP": "POSS"}.get(head.get("degree"))
    if s.get("role") != want:
        return [f"{where}: a slot governed by a {'comparative' if want == 'ABL' else 'superlative'} is its "
                f"{'standard (than X): role ABL' if want == 'ABL' else 'partitive genitive (of X): role POSS'}, "
                f"not {s.get('role')}"]
    return []


def _check_pred_gender(ci: int, cl: dict, slots: list, lx: Lexicon) -> list[str]:
    """A predicate adjective agrees with its controller (the subject or addressee), so a `gender` on the PRED
    slot itself is ignored. One that contradicts the controller's gender is a plan error: the gender
    belongs on the subject (t031 review: túH … h₂r̥ǵrós for the neuter fire; t029: nogʷṓs for the feminine
    sheep). With pro-drop the PRED's gender is the referent's and is used."""
    out = []
    for si, s in enumerate(slots):
        g = s.get("gender")
        if s.get("role") != "PRED" or g not in ("m", "f", "n") or s.get("lex_id", "").startswith("closed:"):
            continue
        try:
            if _family(s, lx) != "adj":
                continue
            a, kind = clause_controller(cl, lx)
        except Exception:
            continue
        if kind != "verb" and a.gender and a.gender != g:
            out.append(f"clause {ci} slot {si}: the predicate adjective agrees with its {kind.lower()} "
                       f"({a.gender}); its own gender {g} is ignored. Put the gender on the "
                       f"{'subject' if kind == 'SUBJ' else 'addressee'} slot (a pronoun has none of its own)")
    return out


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
        errs += _check_agreement(ci, cl, slots, verbs, lx)
        errs += _check_perfect_dual(ci, cl, verbs, lx)
        errs += _check_two_oblique(ci, cl, lx)
        errs += _check_neg(ci, cl, ctype, verbs)
        errs += _check_imp_person(ci, cl, verbs)
        errs += _check_pred_gender(ci, cl, slots, lx)
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
            d = s.get("dep")
            if isinstance(d, int) and 0 <= d < len(slots) and slots[d].get("role") == "ADV":
                errs += _check_adposition_dep(s, slots[d], where, lx)
            if isinstance(d, int) and 0 <= d < len(slots) and slots[d].get("degree") is not None:
                errs += _check_degree_dep(s, slots[d], where)
            if s.get("degree") is not None:
                errs += _check_degree(s, where, lx)
            errs += _check_personal_case(s, si, slots, where, lx)
            if lid.startswith("closed:"):
                errs += _check_closed(s, slots, where, lx)
                continue
            if lid == "compound":
                errs += _check_compound(s, slots, where, lx)
                continue
            if role == "ADV":
                if lx.entries.get(lid, {}).get("pos") not in ("adv", "particle", "conj", "prep", "postp"):
                    errs.append(f"{where}: ADV needs an indeclinable (adv/particle) lexeme, {lid} is not one")
                continue
            bad = lx.inadmissible(lid)
            if bad:
                errs.append(f"{where}: {bad}")
                continue
            fam = lx.specs[lid]["family"]
            ptcp = s.get("participle")
            if ptcp is not None:
                if role != "MOD" or fam != "verb":
                    errs.append(f"{where}: a participle is a MOD slot holding a verb")
                elif ptcp.get("voice", "ACT") not in ("ACT", "MID"):
                    errs.append(f"{where}: participle voice must be ACT or MID")
                elif ptcp.get("voice", "ACT") not in lx.voices(lid):
                    # engine sweep, thematic-verbs.md defect 10
                    errs.append(f"{where}: {lid} is middle-only (deponent): its participle is middle (voice MID)"
                                if lx.middle_only(lid) else f"{where}: {lid} has no {ptcp.get('voice', 'ACT')} participle")
            if s.get("dep") is not None:
                d = s["dep"]
                if not (isinstance(d, int) and 0 <= d < len(slots)
                        and (slots[d].get("participle") or slots[d].get("role") == "ADV"
                             or slots[d].get("degree") is not None)):
                    errs.append(f"{where}: dep must point at a participle slot, an adposition (ADV) slot or a "
                                f"comparative/superlative (degree) slot")
            if role == "V" and fam != "verb":
                errs.append(f"{where}: V slot needs a verb, {lid} is a {fam}")
            if role == "V" and fam == "verb" and (s.get("verb") or {}).get("voice", "ACT") not in lx.voices(lid):
                errs.append(f"{where}: {lid} is middle-only (deponent): voice must be MID" if lx.middle_only(lid)
                            else f"{where}: {lid} has no {(s.get('verb') or {}).get('voice', 'ACT')} cells")
            if role == "V" and fam == "verb" and cl.get("neg") and s.get("verb", {}).get("mood") == "IMP" \
                    and not any(k.startswith(("PST.", "AOR.")) for k in lx.cells(lid)):
                errs.append(f"{where}: a prohibitive (neg + IMP) needs a present or aorist stem for the "
                            f"injunctive; {lid} is a perfect")
            if role == "V" and fam == "verb" and _valency(lid) == "tr" and s.get("verb", {}).get("voice") != "MID" \
                    and not any(x.get("role") == "OBJ" for x in slots):
                errs.append(f"{where}: {lid} is transitive: active needs an OBJ; a patient subject "
                            f"('the wheel broke', 'dress yourself') takes voice MID")
            if role == "V" and fam == "verb" and _valency(lid) == "fear" \
                    and any(x.get("role") == "OBJ" and x.get("dep") is None for x in slots):
                errs.append(f"{where}: {lid} is a verb of fearing: what is feared takes role ABL ('fear from the "
                            f"wolf', Ved. bhī- + abl.), not OBJ")
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


def _referents(cl: dict, lx: Lexicon, anaphors: bool = True) -> set[tuple[str, str]]:
    """(gender, number) of every referent a clause names: a noun, an adjective or bahuvrihi used as a noun with
    a gender, a relative, indefinite or interrogative pronoun ('whoever gives …, his name'), an anaphor on
    its own (it carries its referent on to the next clauses: 'he … he'; not counted with anaphors=False), and a
    group of conjoined nouns (group_agreement, as for a verb). A numeral MOD fixes its head's number (slot_number)."""
    slots = cl.get("slots", [])
    out, members = set(), set()
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
        out.add((g, slot_number(slots, i)))
        if role != "APPOS":
            members.add(i)
    for ix in coordination_groups(slots).values():
        ix = [i for i in ix if i in members]
        if len(ix) > 1 and any(slots[i].get("and") for i in ix):
            a = group_agreement(slots, ix, lx)
            out.add((a.gender, a.num))
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
        out += _default_warnings(ci, cl, clauses[ci - 1] if ci else None, lx)
        out += _pred_gender_warnings(ci, cl, lx)
        out += _answer_case_warnings(ci, cl, clauses[ci - 1] if ci else None)
        out += _dual_fallback_warnings(ci, cl, lx)
    return out


QUESTION_WORDS = ("closed:interrogative_kwi", "closed:interrogative_kwo")


def _questioned_case(cl: dict | None) -> tuple[str, str] | None:
    """(role, case) of the constituent a question asks for: the slot of kʷís/kʷíd (or the head of an
    interrogative kʷó- MOD, or of kʷóti 'how many'), when its role governs a case; None if there is none."""
    if not cl or not cl.get("question"):
        return None
    slots = cl.get("slots", [])
    for s in slots:
        lid, i = s.get("lex_id", ""), None
        if lid.startswith(QUESTION_WORDS):
            i = slots.index(s)
        elif lid == "closed:interrogative_adv/how_many" and s.get("role") == "MOD":
            i = s.get("head")
        if not isinstance(i, int) or not 0 <= i < len(slots):
            continue
        seen = set()
        while slots[i].get("role") in ("MOD", "APPOS") and isinstance(slots[i].get("head"), int) and i not in seen:
            seen.add(i)
            i = slots[i]["head"]
        role = slots[i].get("role")
        if role in ROLE_CASE and slots[i].get("dep") is None:
            return role, ROLE_CASE[role]
    return None


def _answer_case_warnings(ci: int, cl: dict, prev: dict | None) -> list[str]:
    """A short answer (an np utterance) takes the case of the constituent its question asks for: 'What will he
    ask?' 'Ten horses and a hundred sheep.' answers the object, so the NPs are accusative (t086 review: déḱm̥
    h₁éḱwons ḱm̥tóm-kʷe h₂ówins). An np utterance defaults to the nominative; warn when it follows a question
    about a non-nominative constituent and sets no "case"."""
    if cl.get("type") != "np" or cl.get("case") is not None:
        return []
    q = _questioned_case(prev)
    if q is None or q[1] in ("NOM", "VOC"):
        return []
    return [f"clause {ci}: an np answer after a question about the {q[0]} is nominative by default; if it answers "
            f"that question, set \"case\": \"{q[1]}\" on the clause"]


def _dual_fallback_warnings(ci: int, cl: dict, lx: Lexicon) -> list[str]:
    """A dual subject or addressee with a middle verb gets the plural verb: the 2du/3du mediopassive endings
    are not reconstructable (Ringe 2006 p. 32: only Greek and Indo-Iranian attest them, and they disagree), so
    the engine builds no such cell and finite_cell lets the plural stand in, flagging the token num_fallback
    "du->pl" (the perfect's 2du/3du is rejected instead: _check_perfect_dual). Warns, so the planner knows the
    verb is plural (or rephrases: an active verb, or a plural subject)."""
    vi = next((i for i, s in enumerate(cl.get("slots", [])) if s.get("role") == "V"), None)
    if vi is None:
        return []
    try:
        if verb_person_number(cl, cl["slots"][vi].get("verb") or {}, lx)[1] != "DU":
            return []
        words = realize_clause(cl, lx)
    except Exception:
        return []
    return [f"clause {ci} slot {w.slot}: the 2du/3du middle is not reconstructable (Ringe 2006 p. 32), so the "
            f"dual subject takes the plural {w.form} ({w.features}, num_fallback du->pl); use an active verb if the "
            f"pair must be dual" for w in words if w.num_fallback == "du->pl"]


def _pred_gender_warnings(ci: int, cl: dict, lx: Lexicon) -> list[str]:
    """A predicate adjective whose subject is dropped and that has no `gender` of its own comes out masculine,
    which is wrong when a woman or a neuter thing is meant ('you are dear to me' to a daughter: t053, t079
    reviews). Warns, so the planner sets gender on the PRED (used with pro-drop: _check_pred_gender)."""
    out = []
    for si, s in enumerate(cl.get("slots", [])):
        if s.get("role") != "PRED" or s.get("gender") or s.get("lex_id", "").startswith("closed:"):
            continue
        try:
            if _family(s, lx) != "adj":
                continue
            a, kind = clause_controller(cl, lx)
        except Exception:
            continue
        if kind == "verb" or not a.gender:
            out.append(f"clause {ci} slot {si}: predicate adjective with a dropped subject and no gender: it comes out "
                       f"masculine; set \"gender\": \"f\" (or \"n\") on the PRED if the referent is a woman or a thing")
    return out


def _has(cl: dict | None, role: str) -> bool:
    return bool(cl) and any(s.get("role") == role for s in cl.get("slots", []))


def _addresses(cl: dict | None) -> bool:
    """The clause names an addressee: a VOC slot, or a vocative np utterance ('Sky!')."""
    return _has(cl, "VOC") or bool(cl) and cl.get("type") == "np" and cl.get("case") == "VOC"


def _default_warnings(ci: int, cl: dict, prev: dict | None, lx: Lexicon) -> list[str]:
    """Silent defaults that are usually a plan omission (engine-queue-wave1; silent-defaults audit):
      - a verb with no person, no subject, and a VOC in this clause or the one before: it is 3rd person
        ('Sky, you are great' with no person says 'he is great');
      - a verb-only clause with no person and no num after a clause whose subject is not singular: it is
        3sg, not the subject carried over (t031-0005 'the cows graze … and eats');
      - an adjective agreeing with a 1st/2nd-person pronoun that has no gender: it is masculine (t029: nogʷṓs
        for the ewe);
      - a verb form that is also a form of a verb with another root (h₂éǵt 'said' and h₂éǵet 'drove'; t030)."""
    slots = cl.get("slots", [])
    out = []
    vi = next((i for i, s in enumerate(slots) if s.get("role") == "V"), None)
    v = (slots[vi].get("verb") or {}) if vi is not None else {}
    if vi is not None and not v.get("person") and not _has(cl, "SUBJ"):
        if (_has(cl, "VOC") and v.get("mood") != "IMP") or (_addresses(prev) and not _has(cl, "VOC")):
            out.append(f"clause {ci}: the verb has no person and no subject, and a VOC is near: it is realized "
                       f"as 3rd person; set person: 2 if it addresses the VOC")
        elif not v.get("num") and not _has(cl, "VOC") and _has(prev, "SUBJ"):
            try:
                a, kind = clause_controller(prev, lx)
            except Exception:
                a, kind = None, None
            if a is not None and kind == "SUBJ" and a.verb_num != "SG":
                out.append(f"clause {ci}: a verb-only clause after a {a.verb_num} subject is realized as 3sg; "
                           f"set the verb's person and num if that subject goes on (person: 3, num: {a.verb_num})")
    try:
        ctrl, kind = clause_controller(cl, lx)
    except Exception:
        ctrl, kind = None, None
    for si, s in enumerate(slots):
        lid = s.get("lex_id", "")
        if lid.startswith("closed:personal/") and lid.split("/")[1] in ("1", "2") and not s.get("gender"):
            agrees = [j for j, m in enumerate(slots) if m.get("role") in ("MOD", "APPOS") and m.get("head") == si
                      and not m.get("lex_id", "").startswith("closed:") and not m.get("gender")
                      and (m.get("participle") is not None or _safe_family(m, lx) == "adj")]
            if s.get("role") == "SUBJ" and kind == "SUBJ" and len(role_group(slots, "SUBJ")[0]) == 1:
                agrees += [j for j, m in enumerate(slots) if m.get("role") == "PRED"
                           and not m.get("lex_id", "").startswith("closed:") and _safe_family(m, lx) == "adj"]
            if agrees:
                out.append(f"clause {ci} slot {si}: the pronoun has no gender, so the adjective agreeing with it "
                           f"(slot {agrees[0]}) is masculine; set gender on the pronoun (f for a woman or a ewe, "
                           f"n for the fire)")
    if vi is not None and _confusables().get(slots[vi].get("lex_id", "")):      # realize only when it can warn
        try:
            form = realize_clause(cl, lx)
        except Exception:
            form = None
        w = next((x for x in form or [] if x.slot == vi), None)
        for o in (_confusables().get(w.lex_id, ()) if w is not None else ()):
            # the same form (h₂éǵeti 'drives' = SBJV 'may say'), or two past forms of the same person and number
            # one letter apart (h₂éǵt AOR.3SG 'said' ~ h₂éǵet PST.3SG 'drove', the t030 slip); one letter apart
            # in other cells (h₂éǵt ~ h₂éǵe IMP.2SG) is not a likely misreading
            pn, past = w.features.rsplit(".", 1)[-1], w.features.startswith(PAST_CELLS)
            near = sorted((f, v[0]) for f, v in lx.admissible_cells(o).items()
                          if v and not f.startswith("PTCP") and (v[0] == w.form or (
                              past and f.startswith(PAST_CELLS) and f.rsplit(".", 1)[-1] == pn
                              and _one_apart(w.form, v[0]))))
            if near:
                f, form = near[0]
                same = "is also" if form == w.form else "is one letter from"
                out.append(f"clause {ci}: the verb form {w.form} ('{lx.gloss(w.lex_id)}', {w.features}) {same} "
                           f"{form} ('{lx.gloss(o)}', {o} {f}): check that the English means "
                           f"'{lx.gloss(w.lex_id)}'")
    return out


_CONFUSABLES: dict | None = None
PAST_CELLS = ("PST.", "AOR.", "INJ.", "MID.PST.", "MID.AOR.")


def _confusables() -> dict:
    """lex_id → the lex_ids it is easily confused with (data/generation/confusable_verbs.json)."""
    global _CONFUSABLES
    if _CONFUSABLES is None:
        p = ROOT / "data" / "generation" / "confusable_verbs.json"
        _CONFUSABLES = {}
        for pair in (json.loads(p.read_text("utf-8"))["pairs"] if p.exists() else []):
            a, b = pair["lex_ids"]
            _CONFUSABLES.setdefault(a, []).append(b)
            _CONFUSABLES.setdefault(b, []).append(a)
    return _CONFUSABLES


def _one_apart(a: str, b: str) -> bool:
    """Identical, or one inserted, deleted or substituted character apart (NFC): h₂éǵt ~ h₂éǵet."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    s, t = (a, b) if len(a) < len(b) else (b, a)
    return any(t[:i] + t[i + 1:] == s for i in range(len(t)))


def _safe_family(s: dict, lx: Lexicon) -> str | None:
    try:
        return _family(s, lx)
    except KeyError:
        return None


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
    # a counted noun takes the numeral's number (slot_number: 1 SG, 2 DU, 3 and up PL; t016 review: "two dogs"
    # came out singular when the plan left num unset; closed-class R7: 5-1000 too)
    for i in range(len(slots)):
        want = slot_number(slots, i)
        if want != (slots[i].get("num") or "SG") and any(
                m.get("role") == "MOD" and m.get("head") == i and numeral_number(m.get("lex_id", "")) for m in slots):
            slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
            slots[i]["num"] = want
    # an apposition takes its head's case (case_of); its number is its own when the plan (or a numeral on it)
    # sets one ('the blood-price, a hundred cows': SG head, PL apposition; t076, t086 reviews), else its head's;
    # an adjective (or pronoun) in apposition also takes its head's gender
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
            if not s.get("num"):
                s["num"] = slots[h].get("num", "SG")
            if not s.get("gender") and (s["lex_id"].startswith("closed:") or _family(s, lx) == "adj"):
                s["gender"] = _slot_gender(slots[h], lx)
            done.add(i)
        for i in range(len(slots)):
            settle(i)
    ctype = cl.get("type", "verbal")
    # -kʷe goes on the last conjunct (X Y-kʷe, Lat. senatus populusque): a mark only on an earlier
    # member of a coordinated group (same role and head) moves to the last one (t014 review)
    groups = coordination_groups(slots)
    for ix in groups.values():
        if len(ix) > 1 and any(slots[i].get("and") for i in ix) and not slots[ix[-1]].get("and"):
            slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
            for i in ix[:-1]:
                slots[i]["and"] = False
            slots[ix[-1]]["and"] = True
    pairs = {i for ix in groups.values() if len(ix) == 2 and slots[ix[-1]].get("and") for i in ix}
    # the verb's and the predicate adjective's controller: subject(s), addressee(s) or the verb itself (pro-drop);
    # the same computation check_plan makes (clause_controller)
    ctrl, ctrl_kind = clause_controller({**cl, "slots": slots}, lx)
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
    person, num = verb_person_number({**cl, "slots": slots}, v, lx) if vi is not None else (ctrl.person, ctrl.verb_num)
    neg_wish = neg_wish or (cl.get("neg") and v.get("mood") == "SBJV" and person == 1)
    # an explicit particle overrides: "ne" + 1st-person SBJV 'I shall not …', "mē" + SBJV 'let him not …'
    # (_check_neg; t027, t028 reviews)
    if cl.get("neg") == "ne":
        neg_wish = False
    elif cl.get("neg") == "mē":
        neg_wish = True
    words: dict[int, Word] = {}
    for i, s in enumerate(slots):
        lid, role = s["lex_id"], s["role"]
        if role == "V":
            # a neuter plural subject takes a singular verb even if the plan set num (t011 review): verb_person_number
            feat = finite_cell(lx, lid, v, person, num, bool(prohibitive))
            form = lx.admissible_cells(lid)[feat][0]
            if prohibitive:
                feat = feat.replace("PST", "INJ").replace("AOR", "INJ")
            words[i] = Word(form, lid, lx.gloss(lid), feat, i, voice=v.get("voice", "ACT"),
                            num_fallback="du->pl" if num == "DU" and feat.endswith("PL") else None)
            continue
        elif role == "ADV":
            feat, form = "ADV", (lx.entries[lid]["form"] if not lid.startswith("closed:")
                                 else _closed_form(lx, lid, "ADV", None) or lid.split(":")[-1])
        else:
            # agreement source: a MOD agrees with its head; a predicate adjective with the subject
            if role == "MOD":
                head = slots[s["head"]]
            elif role == "PRED" and not lid.startswith("closed:") and _family(s, lx) == "adj":
                # a predicate adjective agrees with the controller: the subject or conjoined subjects; with a
                # 2nd-person verb and no subject the addressee(s) ("Sea, you are great", t011 review); with
                # pro-drop the verb's number ("may they be many": polh₁éwes) and its own gender
                if ctrl_kind == "verb":
                    head = {**s, "num": s.get("num") or ctrl.num}
                else:
                    head = {"lex_id": "closed:controller", "role": "PRED", "num": ctrl.num, "gender": ctrl.gender}
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
            wlid, wgloss, dstatus, case_fb = lid, None, None, None
            if n == "DU" and case not in ("NOM", "ACC", "VOC") and not lid.startswith("closed:numerals"):
                # dual obliques are not reconstructible (Fortson §6.13, §6.50; Lundquist & Yates
                # §122.2.1.1; Ringe ???): the plural stands in, and the feature says so
                n = "PL"
            g = _slot_gender(head, lx)
            fb = pronoun_fallback(lx, s, slots, case, n) if lid.startswith("closed:personal/") else None
            if fb:                    # 'with me': the dative (PRONOUN_ADPOSITION_CASE), flagged on the token
                case_fb, case = f"{case.lower()}->{fb.lower()}", fb
            feat = f"{case}.{n}" + (".ENCL" if s.get("enclitic") else "")
            if lid == "compound":
                cmp = resolve_compound(s["compound"], lx)
                form = cmp.cells(g if cmp.ctype == "bahuvrihi" else None)[feat][0]
                words[i] = Word(form, cmp.lex_id, cmp.gloss(), feat, i, gender=g)
                continue
            if lid.startswith("closed:"):
                form = _closed_form(lx, lid, feat, g)
                if form is None:
                    raise KeyError(f"{lid} {feat} {g}")
                feat = _closed_feat(lx, lid, feat)
            elif s.get("participle"):
                pv = s["participle"].get("voice", "ACT")
                form = lx.admissible_participle_cells(lid, pv, g)[feat][0]
                feat = f"PTCP.{pv}.{feat}"
            elif lx.specs[lid]["family"] == "adj" and s.get("degree"):
                form = lx.degree_cells(lid, s["degree"], g)[feat][0]
                wlid, wgloss = _degree.degree_id(s["degree"], lid), f"{lx.gloss(lid)}.{_degree.GLOSS[s['degree']]}"
                dstatus = _degree.STATUS[s["degree"]]
            elif lx.specs[lid]["family"] == "adj":
                form = lx.admissible_cells(lid, g)[feat][0]
            else:
                form = lx.admissible_cells(lid)[feat][0]
        if role == "ADV":
            wlid, wgloss, dstatus, case_fb = lid, None, None, None
        words[i] = Word(form, wlid, wgloss or lx.gloss(lid), feat, i,
                        clitic=feat.endswith(".ENCL") or form in ENCLITIC_PRONOUNS,
                        gender=g if role != "ADV" else None,
                        voice=s["participle"].get("voice", "ACT") if s.get("participle") else None,
                        degree_status=dstatus, case_fallback=case_fb)

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


def token_cell(w: dict) -> dict:
    """Resolved cell metadata, number fallback and the project-reconstruction flag ("coined": "project")
    of a realized word for a corpus token. Only applicable keys are included; features continues to name
    the realized cell."""
    return {k: w[k] for k in ("gender", "voice", "num_fallback", "case_fallback", "degree_status", "coined")
            if w.get(k)}


def realize(plan: dict, lx: Lexicon | None = None) -> dict:
    lx = lx or Lexicon.load()
    text, gloss, words = [], [], []
    # a sentence is a question when any of its clauses says so: the brief sets `question` on the sentence's first
    # clause, and reading only its last dropped the "?" of 35 multi-clause questions (t045 review)
    asked = False
    for ci, cl in enumerate(plan["clauses"]):
        if ci and cl.get("break"):
            text[-1] += "?" if asked else "."
            asked = False
        asked = asked or bool(cl.get("question"))
        ws = realize_clause(cl, lx)
        words += ws
        for w in ws:
            w.coined = lx.coined(w.lex_id)
            if w.form.startswith("-") and text:
                text[-1] += w.form
                gloss[-1] += "=" + w.gloss
            else:
                text.append(w.form)
                gloss.append(f"{w.gloss}-{w.features}" if w.features not in ("PARTICLE", "ADV") else w.gloss)
    end = "?" if asked else "."
    return {"pie": " ".join(text) + end, "gloss": " ".join(gloss), "english": plan["english"],
            "words": [w.__dict__ for w in words]}
