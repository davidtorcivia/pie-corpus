"""Tier 3 realizer: a structured plan → PIE text, deterministically.

The LLM writes plans (English + lexemes + roles + verb features). It never
writes PIE. This module does everything that would otherwise let free-form
"Claude-PIE" back in: case from role, agreement from the head, verb person
and number from the subject, word order, clitic placement. Each form is the
engine's primary handbook form.

Plan (one sentence):
  {"english": "...",
   "clauses": [{"order": "SOV" | "VSO",           # VSO = verb-initial (narrative/emphasis)
                "conj": null | "kʷe",              # "and" joining this clause to the previous one
                "neg": false,                      # ne before the verb (mē with imperative)
                "particle": null | "nu",           # sentence particle, clause-initial
                "slots": [
      {"lex_id": "pie-lex-…" | "closed:personal/1" | …,
       "role": "SUBJ|OBJ|IO|INS|LOC|ABL|POSS|VOC|PRED|GOAL|MOD|ADV|V",
       "num": "SG|DU|PL",                          # nominals; MOD and V take it from their head/subject
       "head": null | <slot index>,                # MOD (adjective, demonstrative, POSS) → its noun
       "enclitic": false,                          # pronoun slots: the enclitic form (moy, toy, …)
       "verb": {"tense": "PRS|PST|AOR|PRF", "mood": "IND|IMP|SBJV|OPT", "voice": "ACT|MID",
                "person": null | 1 | 2 | 3}}]}]}   # person defaults to the subject's (3 for nouns)

`check_plan` lists every problem; `realize` assumes a checked plan.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj

ROOT = Path(__file__).resolve().parent.parent

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
        return cls(lex, specs, closed)

    def gloss(self, lex_id: str) -> str:
        if lex_id.startswith("closed:"):
            return lex_id.split(":", 1)[1]
        m = self.entries[lex_id]["meaning"]
        g = (m[0] if m else self.entries[lex_id]["form"]).split(",")[0].split(";")[0].strip()
        return g.removeprefix("to ").replace(" ", ".")

    def gender(self, lex_id: str) -> str:
        """Lexicon gender first: spec gender defaults to m for athematic table
        stems, which would make dʰugh₂tḗr "daughter" take masculine adjectives."""
        g = self.entries.get(lex_id, {}).get("gender")
        if g not in ("m", "f", "n"):
            g = ((self.specs.get(lex_id) or {}).get("spec") or {}).get("gender")
        return g if g in ("m", "f", "n") else "m"

    def cells(self, lex_id: str, gender: str | None = None) -> dict:
        k = (lex_id, gender)
        if k not in self._cache:
            r = self.specs[lex_id]
            sp, fam = r["spec"], r["family"]
            if fam == "noun":
                c = decline(NounSpec(**sp), "handbook")
            elif fam == "adj":
                c = decline_adj(AdjSpec(**sp), "handbook")[gender or "m"]
            else:
                c = conjugate(VerbSpec(**sp), "handbook")
            self._cache[k] = c
        return self._cache[k]


def _closed_form(lx: Lexicon, lex_id: str, feat: str, gender: str) -> str | None:
    """closed:personal/1, closed:demonstrative_so, closed:relative_yo, closed:interrogative_kwo, ..."""
    path = lex_id.split(":", 1)[1].split("/")
    node = lx.closed
    for p in path:
        node = node.get(p, {})
    if path[0] in ("demonstrative_so", "relative_yo", "interrogative_kwo"):
        node = node.get(gender if gender in node else "m", {})
    if path[0] == "interrogative_kwi":
        node = node.get("n" if gender == "n" else "mf", {})
    forms = node.get(feat) if isinstance(node, dict) else None
    return forms[0] if forms else None


def _person_number(slot: dict, lx: Lexicon) -> tuple[int, str]:
    lid = slot["lex_id"]
    if lid.startswith("closed:personal/") and lid.split("/")[1] in ("1", "2"):
        return int(lid.split("/")[1]), slot.get("num", "SG")
    return 3, slot.get("num", "SG")


def _verb_feature(v: dict, person: int, num: str) -> str:
    mood, tense, voice = v.get("mood", "IND"), v.get("tense", "PRS"), v.get("voice", "ACT")
    pn = f"{v.get('person') or person}{num}"
    base = {"IND": tense, "IMP": "IMP", "SBJV": "SBJV", "OPT": "OPT"}[mood]
    return ("MID." if voice == "MID" else "") + f"{base}.{pn}"


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
        for si, s in enumerate(slots):
            where = f"clause {ci} slot {si}"
            lid, role = s.get("lex_id", ""), s.get("role")
            if role not in ROLES:
                errs.append(f"{where}: unknown role {role!r}")
                continue
            if lid.startswith("closed:"):
                continue
            if lid not in lx.specs:
                errs.append(f"{where}: unknown or non-inflectable lex_id {lid!r}")
                continue
            r = lx.specs[lid]
            if not r.get("usable"):
                errs.append(f"{where}: {lid} has no usable spec (rule {r['rule']})")
                continue
            fam = r["family"]
            if role == "V" and fam != "verb":
                errs.append(f"{where}: V slot needs a verb, {lid} is a {fam}")
            if role != "V" and fam == "verb":
                errs.append(f"{where}: role {role} needs a nominal, {lid} is a verb")
            if role == "MOD":
                h = s.get("head")
                if h is None or not (0 <= h < len(slots)) or slots[h].get("role") in ("V", "MOD", "ADV"):
                    errs.append(f"{where}: MOD needs a nominal head slot")
            if role == "MOD" and fam not in ("adj",) and not lid.startswith("closed:"):
                errs.append(f"{where}: MOD needs an adjective, {lid} is a {fam}")
        if not errs:
            try:
                realize_clause(cl, lx)
            except KeyError as e:
                errs.append(f"clause {ci}: form not generated: {e}")
    return errs


def realize_clause(cl: dict, lx: Lexicon) -> list[Word]:
    slots = cl["slots"]
    subj = next((s for s in slots if s["role"] == "SUBJ"), None)
    person, num = _person_number(subj, lx) if subj else (3, "SG")
    words: dict[int, Word] = {}
    for i, s in enumerate(slots):
        lid, role = s["lex_id"], s["role"]
        if role == "V":
            v = s.get("verb", {})
            feat = _verb_feature(v, person, num)
            form = lx.cells(lid)[feat][0]
        elif role == "ADV":
            feat, form = "ADV", (lx.entries[lid]["form"] if not lid.startswith("closed:") else lid.split(":")[-1])
        else:
            head = slots[s["head"]] if role == "MOD" else s
            case = ROLE_CASE[head["role"]]
            n = head.get("num", "SG")
            g = lx.gender(head["lex_id"]) if not head["lex_id"].startswith("closed:") else "m"
            feat = f"{case}.{n}" + (".ENCL" if s.get("enclitic") else "")
            if lid.startswith("closed:"):
                form = _closed_form(lx, lid, feat, g)
                if form is None:
                    raise KeyError(f"{lid} {feat}")
            elif lx.specs[lid]["family"] == "adj":
                form = lx.cells(lid, g)[feat][0]
            else:
                form = lx.cells(lid)[feat][0]
        words[i] = Word(form, lid, lx.gloss(lid), feat, i, clitic=form in ENCLITIC_PRONOUNS)

    # order: each MOD/POSS directly before its head; then SOV or verb-initial
    def phrase(i: int) -> list[int]:
        mods = [j for j, s in enumerate(slots) if s["role"] in ("MOD", "POSS") and s.get("head") == i]
        return mods + [i]

    order_roles = ["VOC", "SUBJ", "IO", "OBJ", "GOAL", "INS", "LOC", "ABL", "PRED", "ADV"]
    heads = [i for i, s in enumerate(slots) if s["role"] not in ("V", "MOD") and not
             (s["role"] == "POSS" and s.get("head") is not None)]
    heads.sort(key=lambda i: order_roles.index(slots[i]["role"]) if slots[i]["role"] in order_roles else 99)
    seq = [j for h in heads for j in phrase(h)]
    vi = next(i for i, s in enumerate(slots) if s["role"] == "V")
    neg = Word("mē" if slots[vi].get("verb", {}).get("mood") == "IMP" else "ne", "closed:particle:ne",
               "NEG", "PARTICLE") if cl.get("neg") else None
    vseq = ([neg] if neg else []) + [words[vi]]
    out = [words[i] for i in seq if not words[i].clitic]
    out = vseq + out if cl.get("order") == "VSO" else out + vseq
    if cl.get("particle"):
        out.insert(0, Word(cl["particle"], f"closed:particle:{cl['particle']}", cl["particle"].upper(), "PARTICLE"))
    # Wackernagel: enclitics after the first word, "and" (-kʷe) on the first word
    clitics = [words[i] for i in seq if words[i].clitic]
    out[1:1] = clitics
    if cl.get("conj") == "kʷe":
        out.insert(1, Word("-kʷe", "closed:particle:-kʷe", "and", "PARTICLE", clitic=True))
    return out


def realize(plan: dict, lx: Lexicon | None = None) -> dict:
    lx = lx or Lexicon.load()
    words: list[Word] = []
    for cl in plan["clauses"]:
        words += realize_clause(cl, lx)
    text, gloss = [], []
    for w in words:
        if w.form.startswith("-") and text:
            text[-1] += w.form
            gloss[-1] += "=" + w.gloss
        else:
            text.append(w.form)
            gloss.append(f"{w.gloss}-{w.features}" if w.features not in ("PARTICLE", "ADV") else w.gloss)
    return {"pie": " ".join(text) + ".", "gloss": " ".join(gloss), "english": plan["english"],
            "words": [w.__dict__ for w in words]}
