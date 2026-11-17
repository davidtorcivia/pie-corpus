"""English → PIE by rule: parse the English (spaCy), build a plan in the planners' format (docs/generation/
planner-brief-v4.md), and let the engine realize it (pie.realize.check_plan, realize). No language model.

Each English sentence becomes one or more clauses:
- the verb: its lemma → a verb lexeme that has the needed tense (lexmap); past → AOR (else PST), present → PRS
  (else a gnomic AOR), "has seen"/"knows"-type perfects → PRF, "will" → SBJV (the subjunctive as future), "may" →
  OPT, "let us" → SBJV 1PL, a bare imperative → IMP 2SG/PL; "be" + adjective/noun in the present → a nominal
  sentence (no copula), else h₁ésti;
- roles from the dependency parse: nsubj → SUBJ (a personal pronoun is dropped and marks the verb's person and
  number), dobj → OBJ, dative/iobj → IO, prepositions → GOAL (to, into), LOC (in, at, on), ABL (from, out of), INS
  (with, by), IO (for), POSS (of); amod → MOD, poss → POSS, nummod → a numeral, this/that → deictic_ki /
  demonstrative_so, not → neg, where/why/how/when → the interrogative adverbs, an address ("Friend, …") → VOC;
- a coordinated noun takes "and" (-kʷe) on the last conjunct; a coordinated verb is a new clause with kʷe;
- "no X" / "nothing" / "nobody" / "no one" / "none" as subject, object or existential noun → the clause's neg (ne),
  the pronouns as the indefinite kʷis/kʷid (ne kʷis gʷémt 'no one came'); "no" elsewhere is noted as left out;
- "there is/are X" → X the subject of h₁ésti, which agrees with it (existence takes the verb);
- possessive "have" (the root verb with an object: "I have a horse", not the perfect's aux) → the possessor in the
  dative, the possessed the subject of h₁ésti (h₁éḱwos moy h₁ésti, Lat. mihi est equus);
- "only" on a noun → h₁óynos 'one, alone' agreeing with it (noted as a stand-in);
- a verbless noun phrase after a comma ("…, only death") → an np utterance of its own, or an address (VOC) in a
  command or 2nd-person clause ("Come, my friend!"); a plural addressee makes the 2nd-person verb plural.
Everything the rules don't cover is reported in `notes`, and a word with no lexeme stays out of the PIE and is listed
in `unknown`. check_plan's errors are reported, never hidden: the slot that causes one is dropped and the plan
retried, and the drop is noted.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path
from dataclasses import dataclass, field

from ..realize import Lexicon, _valency, check_plan, realize
from .lexmap import LexMap

PRONOUNS = {  # English personal pronoun → (person, number)
    "i": (1, "SG"), "me": (1, "SG"), "we": (1, "PL"), "us": (1, "PL"),
    "you": (2, "SG"), "he": (3, "SG"), "him": (3, "SG"), "she": (3, "SG"), "her": (3, "SG"), "it": (3, "SG"),
    "they": (3, "PL"), "them": (3, "PL"),
}
GENDER = {"he": "m", "him": "m", "his": "m", "she": "f", "her": "f", "hers": "f", "it": "n", "its": "n",
          "they": "m", "them": "m", "their": "m"}
POSSESSIVE = {"my": (1, "SG"), "our": (1, "PL"), "your": (2, "SG"), "his": (3, "SG"), "her": (3, "SG"),
              "its": (3, "SG"), "their": (3, "PL")}
WH_ADV = {"where": "closed:interrogative_adv/where", "why": "closed:interrogative_adv/why",
          "how": "closed:interrogative_adv/how", "when": "closed:interrogative_adv/when"}
NUMERALS = {"two": "closed:numerals/2", "three": "closed:numerals/3", "four": "closed:numerals/4",
            "five": "closed:numerals/indeclinable/5", "six": "closed:numerals/indeclinable/6",
            "seven": "closed:numerals/indeclinable/7", "eight": "closed:numerals/indeclinable/8",
            "nine": "closed:numerals/indeclinable/9", "ten": "closed:numerals/indeclinable/10",
            "hundred": "closed:numerals/indeclinable/100", "thousand": "closed:numerals/indeclinable/1000"}
PREP_ROLE = {"to": "GOAL", "into": "GOAL", "toward": "GOAL", "towards": "GOAL", "in": "LOC", "at": "LOC",
             "on": "LOC", "inside": "LOC", "from": "ABL", "out": "ABL", "with": "INS", "by": "INS", "for": "IO",
             "through": "INS", "along": "INS", "across": "INS",     # the path: Vedic instrumental of the way
             "of": "POSS"}
# irregular past forms spaCy's small model leaves unlemmatized when it mis-tags them
IRREGULAR = dict(x.split(":") for x in (
    "drank:drink ate:eat ran:run sang:sing saw:see went:go came:come gave:give spoke:speak knew:know took:take "
    "sat:sit stood:stand fell:fall led:lead drove:drive bore:bear slew:slay heard:hear said:say told:tell "
    "brought:bring thought:think fought:fight held:hold kept:keep slept:sleep wept:weep found:find grew:grow "
    "threw:throw flew:fly wore:wear rode:ride rose:rise shone:shine struck:strike won:win fed:feed fled:flee "
    "laid:lay lost:lose made:make met:meet sent:send sold:sell sought:seek taught:teach woke:wake bit:bite "
    "hid:hide broke:break chose:choose stole:steal swam:swim began:begin drew:draw blew:blow became:become "
    "bound:bind built:build felt:feel left:leave meant:mean spent:spend swore:swear tore:tear dug:dig "
    "wove:weave sowed:sow milked:milk ploughed:plough").split())
# Words with no lexeme of their own: the nearest English word the lexicon has (tried in order). The result is
# reported as an approximation ("truth ≈ true"), never passed off as the word itself.
SYNONYMS = {
    "truth": ["true"], "evident": ["visible", "clear"], "obvious": ["visible", "clear"], "apparent": ["visible"],
    "manifest": ["visible"], "plain": ["clear"], "liberty": ["free"], "freedom": ["free"], "happiness": ["joy"],
    "joyful": ["glad"], "justice": ["right"], "just": ["right"], "nation": ["people"], "country": ["land"],
    "consider": ["think"], "believe": ["think"], "suppose": ["think"], "seem": ["appear"], "create": ["make"],
    "endow": ["give"], "grant": ["give"], "pursue": ["seek"], "pursuit": ["seek"], "hope": ["wish"],
    "desire": ["wish"], "wicked": ["bad"], "lovely": ["beautiful", "fair", "good"],
    "large": ["big", "great"], "huge": ["great"], "tiny": ["small"], "quick": ["swift"], "rapid": ["swift"],
    "fast": ["swift"], "forest": ["wood", "tree"], "woods": ["wood", "tree"], "ocean": ["sea"], "lake": ["sea", "water"],
    "kid": ["child", "son", "boy"], "girl": ["daughter"], "boy": ["son"], "lady": ["woman"],
    "husband": ["man"], "wife": ["woman"], "ruler": ["king"], "lord": ["king", "master"], "chief": ["king"],
    "warrior": ["man", "hero"], "soldier": ["man"], "battle": ["war", "fight"], "begin": ["start"],
    "finish": ["end"], "unalienable": ["imperishable"], "inalienable": ["imperishable"], "eternal": ["imperishable"],
    "immortal": ["undying", "imperishable"], "self": ["own"], "equal": ["alike", "same"], "certain": ["true"],
    "tell": ["say", "speak"], "talk": ["speak"], "chat": ["speak"],
}
# derivational endings stripped to reach a base the lexicon has: happiness → happy, equality → equal
SUFFIXES = [("iness", "y"), ("ness", ""), ("ity", ""), ("ity", "e"), ("ment", ""), ("ation", "e"), ("ion", ""),
            ("dom", ""), ("hood", ""), ("ship", ""), ("ful", ""), ("ly", ""), ("th", "e"), ("er", ""), ("or", "")]
# English adverbs of time, place and manner the translator says with an indeclinable (Transfer.adverbs): a fixed
# list, so a gloss word that is also a preposition, a conjunction or an answer ('to', 'but', 'yes') never matches
ADVERB_WORDS = {"here", "there", "yonder", "now", "today", "yesterday", "tomorrow", "again", "also", "too", "still",
                "soon", "quickly", "early", "together", "down", "up", "away", "back", "out", "off", "twice", "thrice",
                "apart", "around", "inside", "behind", "below", "above", "afterwards", "somewhere", "upwards",
                "outward", "within"}
# modal auxiliaries with no PIE counterpart in the engine: reported, never dropped silently ('may'/'might' → OPT,
# 'will'/'shall' → SBJV)
MODALS_UNSAID = {"can", "could", "would", "should", "must", "ought"}
# subordinating conjunctions: True → the clause particle h₁yód 'if, when' (pie.realize; idioms.json: because,
# since), False → no rule (reported as left out, never silently dropped)
SUBORDINATORS = {"if": True, "when": True, "whenever": True, "because": True, "since": True,
                 "although": False, "though": False, "unless": False, "until": False, "till": False, "while": False,
                 "before": False, "after": False, "whereas": False, "once": False}
GIVE_LIKE = {"give", "say", "tell", "show", "bring", "send", "offer", "sing", "speak"}   # "to X" = IO
# negative pronouns: the indefinite kʷis/kʷid under the clause's ne ('ne kʷis gʷémt' no one came; pie.realize)
NEG_PRONOUNS = {"nothing": "n", "nobody": "m", "none": "m", "noone": "m"}
ONLY_NOTE = "'only' ≈ h₁óynos 'one, single, alone', agreeing with its noun (no PIE particle for 'only'; Lat. ūnus)"
POSSESSIVE_HAVE_NOTE = "'have' → the dative of possession: the possessor in the dative + h₁ésti 'is' (Lat. mihi est)"
NEG_DEPS = ("nsubj", "nsubjpass", "dobj", "attr", "dative", "iobj")    # the phrases whose "no" negates the clause


def _negative(tok) -> bool:
    """A subject, object or existential noun phrase that negates its clause: 'no hope', 'no man', 'nothing',
    'nobody', 'none'. ('with no horse' is not: "no" elsewhere is reported as left out.)"""
    return tok.dep_ in NEG_DEPS and (tok.text.lower() in NEG_PRONOUNS
                                     or any(c.dep_ == "det" and c.text.lower() == "no" for c in tok.children))


def _senses_of(meaning: list[str]) -> list[str]:
    """A lexicon meaning list split into its comma/semicolon senses, lower case, parentheses dropped."""
    out = []
    for m in meaning:
        for x in re.split(r"[;,]", re.sub(r"\(.*?\)", "", m)):
            x = x.strip().lower()
            if x:
                out.append(x)
    return out


def verb_lemmas(tok) -> list[str]:
    """Lemma guesses for a verb spaCy lemmatized wrongly ('shines' → 'shin'): the word re-parsed after 'they', then
    the regular English endings taken off (-s, -es, -ies, -ed, -ing, a doubled consonant, a dropped -e)."""
    w = tok.text.lower()
    out = [nlp()(f"they {w}")[1].lemma_.lower()]
    for end, add in (("ies", "y"), ("es", ""), ("s", ""), ("ied", "y"), ("ed", ""), ("ed", "e"), ("ing", ""),
                     ("ing", "e")):
        if w.endswith(end) and len(w) - len(end) >= 2:
            b = w[: -len(end)] + add
            out.append(b)
            if not add and len(b) > 2 and b[-1] == b[-2] and b[-1] not in "aeiouls":      # stopped → stop
                out.append(b[:-1])
    return list(dict.fromkeys(out))


def _comma_next_to(tok) -> bool:
    """An address is set off by a comma (or starts/ends the sentence next to one): "Come, friend!", "Friend, …"."""
    d = tok.doc
    return (tok.i > 0 and d[tok.i - 1].text == ",") or (tok.i + 1 < len(d) and d[tok.i + 1].text == ",")


NP_HEADS = ("NOUN", "PROPN", "PRON", "ADJ")    # a sentence rooted in one of these has no verb: an np utterance
MODEL = "en_core_web_lg"       # parser + full word vectors (md shares one vector across many rare words: tiger =
                                # wolf = chariot); the vectors give the nearest-word fallback; prod needs it
SIMILAR_MIN = 0.6               # cosine floor for a nearest-word stand-in by vector


@functools.lru_cache(maxsize=1)
def nlp():
    import spacy
    return spacy.load(MODEL, disable=["ner"])


@dataclass
class Result:
    english: str
    pie: str | None
    gloss: str | None
    plan: dict | None
    unknown: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    lex_ids: list[str | None] = field(default_factory=list)    # per written word, for the provenance labels


class Transfer:
    def __init__(self):
        from ..neologism import with_neologisms
        self.lx = with_neologisms(Lexicon.load())   # coinages are offered (and labelled coined); inherited words rank first
        self.map = LexMap.load(nlp())
        self.used: set[int] = set()        # token indices that became a slot (translate() reports the rest)
        self.neg_dets: set[int] = set()    # "no" determiners that became the clause's ne

    # ---------------------------------------------------------------- words
    def lookup(self, tok, families: tuple[str, ...], notes) -> tuple[str | None, str | None]:
        """(lex_id, family) for a token: its own word first, then a synonym (SYNONYMS), then a derivational base
        (SUFFIXES), in each of the families asked for. Any substitute is noted as an approximation."""
        lem, text = tok.lemma_.lower(), tok.text.lower()
        for w in dict.fromkeys([lem, text]):
            for f in families:
                cs = self.map.candidates(w, f)
                if cs:
                    return cs[0].lex_id, f
        if tok.pos_ == "PROPN":
            # a name with no lexeme of its own stays out (reported unknown): a stand-in by meaning would rename the
            # person (David ≈ smith, Achilles ≈ tendon: the vectors place a name near a surname or a body part)
            return None, None
        tries = list(SYNONYMS.get(lem, []))
        for end, add in SUFFIXES:
            if lem.endswith(end) and len(lem) - len(end) >= 3:
                tries.append(lem[: -len(end)] + add)
        for w in tries:
            for f in families + tuple(x for x in ("adj", "noun", "verb") if x not in families):
                if f == "verb" and "verb" not in families:
                    continue
                cs = self.map.candidates(w, f)
                if cs:
                    notes.append(f"'{tok.text}' ≈ '{w}' (no PIE word for '{tok.text}')")
                    return cs[0].lex_id, f
        # a time or place adverb is never a noun's stand-in ('today' ≈ 'yesterday' by the vectors): Transfer.adverbs
        w, f, sim = self.nearest(lem, families) if lem not in ADVERB_WORDS else (None, None, 0.0)
        if w:
            notes.append(f"'{tok.text}' ≈ '{w}' (no PIE word for '{tok.text}'; nearest by meaning, {sim:.2f})")
            return self.map.candidates(w, f)[0].lex_id, f
        return None, None

    def nearest(self, lemma: str, families: tuple[str, ...]) -> tuple[str | None, str | None, float]:
        """The English word with a lexeme whose vector is closest to the lemma's (cosine ≥ SIMILAR_MIN)."""
        import numpy as np
        if not hasattr(self, "_vecs"):
            vocab = nlp().vocab
            self._vecs = {}
            for f in ("noun", "adj", "verb"):
                words = [w for w, cs in self.map.by_lemma.items() if any(c.family == f for c in cs)
                         and vocab.has_vector(w)]
                m = np.array([vocab.get_vector(w) for w in words], dtype="float32")
                m /= np.linalg.norm(m, axis=1, keepdims=True) + 1e-9
                self._vecs[f] = (words, m)
        vocab = nlp().vocab
        if not vocab.has_vector(lemma):
            return None, None, 0.0
        v = vocab.get_vector(lemma).astype("float32")
        v /= np.linalg.norm(v) + 1e-9
        best = (None, None, 0.0)
        for f in families:
            words, m = self._vecs[f]
            if not words:
                continue
            sims = m @ v
            i = int(sims.argmax())
            if sims[i] > best[2] and words[i] != lemma:
                best = (words[i], f, float(sims[i]))
        return best if best[2] >= SIMILAR_MIN else (None, None, best[2])

    def noun(self, tok, notes, unknown) -> str | None:
        lid, _ = self.lookup(tok, ("noun", "adj"), notes)
        if not lid:
            unknown.append(tok.text)
            return None
        self.used.add(tok.i)
        return lid

    def adj(self, tok, unknown, notes=None) -> str | None:
        lid, _ = self.lookup(tok, ("adj",), notes if notes is not None else [])
        if not lid:
            unknown.append(tok.text)
            return None
        self.used.add(tok.i)
        return lid

    @functools.cached_property
    def adverbs(self) -> dict[str, list[dict]]:
        """English adverb → the slots that say it. The project's own choices first (idioms.json: 'again' h₂éti,
        'soon' móḱs, 'also' éti, 'tomorrow' h₂éyeri, 'today' = 'on this day', deictic_ki + dínos in the locative),
        then the indeclinable lexemes (adv, particle) whose gloss is that one word ('yesterday' dʰǵʰyés,
        'now' nu, 'down' ní), and the closed-class deictic h₁idʰé 'here'."""
        import json as _json
        out: dict[str, list[dict]] = {"here": [{"lex_id": "closed:deictic_adv/here", "role": "ADV"}],
                                      "today": [{"lex_id": "pie-lex-dinos", "role": "LOC"},
                                                {"lex_id": "closed:deictic_ki", "role": "MOD", "head": 0}]}
        ok = lambda lid: self.lx.entries.get(lid, {}).get("pos") in ("adv", "particle")
        idioms = _json.loads((Path(__file__).resolve().parents[2] / "data/lexicon/idioms.json").read_text("utf-8"))
        for it in idioms["idioms"]:
            ids = [i for i in it.get("ids") or [] if ok(i)]
            if it.get("kind") == "idiom" and ids:
                for w in it["english"]:
                    if w in ADVERB_WORDS:
                        out.setdefault(w, [{"lex_id": ids[0], "role": "ADV"}])
        best: dict[str, tuple[int, str]] = {}      # the lexeme whose gloss names the word earliest
        for lid, e in self.lx.entries.items():
            if not ok(lid) or not e.get("meaning") or e.get("kind") == "root":
                continue
            for rank, sense in enumerate(_senses_of(e["meaning"])[:4]):
                if sense in ADVERB_WORDS and sense not in out and rank < best.get(sense, (99, ""))[0]:
                    best[sense] = (rank, lid)
        for w, (_, lid) in best.items():
            out[w] = [{"lex_id": lid, "role": "ADV"}]
        return out

    def degree(self, tok, slot_i: int, slots: list, notes, unknown) -> None:
        """'bigger (than the dog)', 'the biggest', 'more beautiful': the engine's primary comparative/superlative
        (pie.degree, realize "degree"), the standard of comparison an ABL slot governed by it (the ablative of
        comparison, Ringe 2006 §2.3.1) and a superlative's 'of X' a POSS slot (partitive genitive). An adjective
        the engine builds no degree for (pie.degree.base: not a primary adjective) stays plain, with a note."""
        from .. import degree as _degree
        d = {"Cmp": "CMP", "Sup": "SUP"}.get(next(iter(tok.morph.get("Degree")), None))
        for c in tok.children:
            if c.dep_ == "advmod" and c.text.lower() in ("more", "most"):
                d = "CMP" if c.text.lower() == "more" else "SUP"
                self.used.add(c.i)
        if d is None:
            return
        lid = slots[slot_i]["lex_id"]
        try:
            _degree.base(lid, self.lx)
        except Exception as e:
            notes.append(f"'{tok.text}': no {'comparative' if d == 'CMP' else 'superlative'} of "
                         f"{self.lx.entries.get(lid, {}).get('form', lid)} in the engine ({e}); the plain adjective stands")
            return
        slots[slot_i]["degree"] = d
        for c in tok.children:
            if c.dep_ == "prep" and c.text.lower() == ("than" if d == "CMP" else "of"):
                self.used.add(c.i)
                for g in c.children:
                    if g.dep_ == "pobj":
                        i = self.np_slots(g, "ABL" if d == "CMP" else "POSS", slots, notes, unknown)
                        if i is not None:
                            slots[i]["dep"] = slot_i

    def verb(self, lemma: str, tense: str, mood: str, notes, prohibitive: bool = False) -> tuple[str | None, str]:
        """A verb lexeme with the needed cell, and the tense actually used. A prohibitive (neg + IMP) needs a present
        or aorist stem (the injunctive). A verb with no lexeme of its own tries its SYNONYMS."""
        cs = self.map.candidates(lemma, "verb")
        if not cs:
            for w in SYNONYMS.get(lemma, []):
                cs = self.map.candidates(w, "verb")
                if cs:
                    notes.append(f"'{lemma}' ≈ '{w}' (no PIE word for '{lemma}')")
                    break
        if not cs:              # the nearest verb by meaning, as lookup() does for nouns ('understand' ≈ 'know')
            w, _, sim = self.nearest(lemma, ("verb",))
            if w:
                cs = self.map.candidates(w, "verb")
                notes.append(f"'{lemma}' ≈ '{w}' (no PIE word for '{lemma}'; nearest by meaning, {sim:.2f})")
        if not cs:
            return None, tense
        want = {"IND": [tense], "IMP": ["IMP"], "SBJV": ["SBJV"], "OPT": ["OPT"]}[mood]
        prefs = {"AOR": ["AOR", "PST"], "PRS": ["PRS", "AOR"], "PRF": ["PRF", "PRS"], "PST": ["PST", "AOR"]}
        if mood == "IND":
            # a stative perfect with no present or aorist stem (wóyde 'knows', h₃eh₃óde 'hates', ḱeḱómh₂e 'is tired')
            # says the present state: its perfect is the present tense
            if tense == "PRS" and "PRF" in cs[0].tenses and not cs[0].tenses & {"PRS", "AOR"}:
                return cs[0].lex_id, "PRF"
            for t in prefs[tense]:
                for c in cs:
                    if t in c.tenses:
                        if t != tense:
                            notes.append(f"'{lemma}': no {tense} stem, used {t}")
                        return c.lex_id, t
            return None, tense
        for c in cs:
            if want[0] in c.tenses and (not prohibitive or c.tenses & {"PRS", "AOR"}):
                stem = "AOR" if "AOR" in c.tenses else "PRF" if "PRF" in c.tenses else "PRS"
                return c.lex_id, stem
        return None, tense

    # ---------------------------------------------------------------- clauses
    def np_slots(self, tok, role, slots, notes, unknown, num=None) -> int | None:
        """A noun phrase headed by tok (noun, pronoun, proper noun) → slots; returns the head slot's index."""
        low = tok.text.lower()
        self.used.add(tok.i)
        no_one = low == "one" and any(c.dep_ == "det" and c.text.lower() == "no" for c in tok.children)
        if low in NEG_PRONOUNS or no_one:        # the clause takes ne (clause(): _negative)
            slots.append({"lex_id": "closed:indefinite_kwi", "role": role, "gender": NEG_PRONOUNS.get(low, "m")})
            return len(slots) - 1
        if tok.pos_ == "PRON":
            if low in PRONOUNS:
                p, n = PRONOUNS[low]
                if p in (1, 2):
                    slots.append({"lex_id": f"closed:personal/{p}", "role": role, "num": n})
                else:
                    slots.append({"lex_id": "closed:anaphoric_i", "role": role, "num": n, "gender": GENDER.get(low, "m")})
                return len(slots) - 1
            if low in ("what", "who", "whom"):
                slots.append({"lex_id": "closed:interrogative_kwi", "role": role, "gender": "n" if low == "what" else "m"})
                return len(slots) - 1
            if low in ("this", "that"):
                slots.append({"lex_id": "closed:deictic_ki" if low == "this" else "closed:demonstrative_so",
                              "role": role, "gender": "n"})
                return len(slots) - 1
            notes.append(f"pronoun '{tok.text}' left out")
            return None
        if tok.lemma_.lower() in ("thing", "one") and any(c.dep_ == "amod" for c in tok.children):
            a = next(c for c in tok.children if c.dep_ == "amod")     # "good things": the adjective as a noun
            lid = self.adj(a, unknown)
            if not lid:
                return None
            slots.append({"lex_id": lid, "role": role, "num": "PL" if tok.morph.get("Number") == ["Plur"] else "SG",
                          "gender": "n" if tok.lemma_.lower() == "thing" else "m"})
            self.used.add(a.i)
            return len(slots) - 1
        lid = self.noun(tok, notes, unknown)
        if not lid:
            return None
        n = num or ("PL" if tok.morph.get("Number") == ["Plur"] else "SG")
        head = len(slots)
        slots.append({"lex_id": lid, "role": role, "num": n})
        if self.lx.specs.get(lid, {}).get("family") == "adj":       # an adjective as a noun: priHós 'friend',
            # 'truths' ≈ the true (things): neuter for a thing, else by the referent
            person_noun = tok.lemma_.lower() in ("friend", "woman", "girl", "wife", "man", "child", "enemy")
            slots[head]["gender"] = ("f" if tok.lemma_.lower() in ("woman", "girl", "wife") else "m") if person_noun else "n"
        for ch in tok.children:
            cl = ch.text.lower()
            if ch.dep_ == "amod" and ch.pos_ == "ADJ" and ch.text.lower() not in IRREGULAR:
                a = self.adj(ch, unknown, notes)
                if a:
                    slots.append({"lex_id": a, "role": "MOD", "head": head})
                    self.degree(ch, len(slots) - 1, slots, notes, unknown)
            elif ch.dep_ == "poss":
                if cl in POSSESSIVE:
                    p, pn = POSSESSIVE[cl]
                    if p in (1, 2):
                        slots.append({"lex_id": f"closed:personal/{p}", "role": "POSS", "num": pn, "head": head,
                                      "enclitic": True})
                    else:
                        slots.append({"lex_id": "closed:anaphoric_i", "role": "POSS", "num": pn, "head": head,
                                      "gender": GENDER.get(cl, "m")})
                else:
                    self.np_slots(ch, "POSS", slots, notes, unknown)
                    slots[-1]["head"] = head
            elif ch.dep_ == "nummod" and cl in NUMERALS:
                self.used.add(ch.i)
                slots.append({"lex_id": NUMERALS[cl], "role": "MOD", "head": head})
                slots[head]["num"] = "DU" if cl == "two" else "PL"
            elif ch.dep_ == "det" and cl in ("this", "these", "that", "those"):
                self.used.add(ch.i)
                slots.append({"lex_id": "closed:deictic_ki" if cl in ("this", "these") else "closed:demonstrative_so",
                              "role": "MOD", "head": head})
            elif ch.dep_ == "advmod" and cl == "only":
                # 'only death', 'only the king': h₁óynos 'one, alone' agreeing with the noun (Lat. ūnus)
                self.used.add(ch.i)
                slots.append({"lex_id": "pie-lex-h1oynos", "role": "MOD", "head": head})
                if ONLY_NOTE not in notes:
                    notes.append(ONLY_NOTE)
            elif ch.dep_ == "det" and cl == "another":
                # 'another girl': h₂élyos, a pronominal adjective agreeing with its noun (round 5)
                self.used.add(ch.i)
                slots.append({"lex_id": "pie-lex-h2elyos", "role": "MOD", "head": head})
            elif ch.dep_ == "prep" and ch.text.lower() == "of":
                for g in ch.children:
                    if g.dep_ == "pobj":
                        i = self.np_slots(g, "POSS", slots, notes, unknown)
                        if i is not None:
                            slots[i]["head"] = head
            elif ch.dep_ == "conj" and ch.pos_ in ("NOUN", "PROPN", "PRON"):
                if any(c.dep_ == "cc" and c.text.lower() in ("or", "nor") for c in tok.children):
                    # the engine joins nouns only with -kʷe 'and' (-wē 'or' joins clauses): 'or' would turn into 'and'
                    notes.append(f"'or {ch.text}' left out (nouns are joined only with -kʷe 'and')")
                    self.used.add(ch.i)
                    continue
                i = self.np_slots(ch, role, slots, notes, unknown)
                if i is not None:
                    slots[i]["and"] = True
            elif ch.dep_ == "appos" and ch.pos_ in ("NOUN", "PROPN") and role not in ("MOD", "APPOS"):
                # 'Dawn, daughter of the sky': a noun phrase in apposition, in its head's case (realize: APPOS)
                i = self.np_slots(ch, "APPOS", slots, notes, unknown)
                if i is not None:
                    slots[i]["head"] = head
        return head

    def clause(self, root, sent, notes, unknown, inherit: dict | None = None) -> list[dict]:
        """One verbal or nominal clause (and its coordinated verbs as kʷe clauses)."""
        slots: list[dict] = []
        cl: dict = {"slots": slots}
        self.used.add(root.i)
        kids = list(root.children)
        aux = [k for k in kids if k.dep_ in ("aux", "auxpass")]
        aux_l = [a.lemma_.lower() for a in aux]
        neg = any(k.dep_ == "neg" for k in kids)
        if any(_negative(k) for k in kids):              # 'no man came', 'there is no hope', 'I have nothing'
            neg = True
            self.neg_dets |= {c.i for k in kids if _negative(k) for c in k.children if c.text.lower() == "no"}
        lemma = root.lemma_.lower()
        tense_m = root.morph.get("Tense")
        tense = "AOR" if "Past" in tense_m or any(a.morph.get("Tense") == ["Past"] for a in aux if a.lemma_ == "do") else "PRS"
        if tense == "PRS" and root.tag_ == "VBG" and any(a.lemma_.lower() == "be" and "Past" in a.morph.get("Tense")
                                                        for a in aux):
            tense = "PST"        # 'was eating': PST, the imperfect (planner-brief-v4: AOR for single events, PST for background)
        mood = "IND"
        if "will" in aux_l or "shall" in aux_l:
            mood = "SBJV"
        elif "may" in aux_l or "might" in aux_l:
            mood = "OPT"
        elif "have" in aux_l and root.tag_ == "VBN":
            tense = "PRF"
        for a in aux:
            if a.lemma_.lower() in MODALS_UNSAID:
                notes.append(f"'{a.text}' not expressed (PIE has no modal verb for it; the plain verb stands)")
        subj = [k for k in kids if k.dep_ in ("nsubj", "nsubjpass")]
        if not subj and root.pos_ == "VERB":
            # 'What did the wolf eat?': the small parser hangs the subject on the verb as a compound
            subj = [k for k in kids if k.dep_ == "compound" and k.pos_ in ("NOUN", "PROPN") and k.i < root.i]
        # a command: the bare verb with no subject, and any 'do' the imperative's own (Do not go! Don't go!), not a
        # tensed do-support (What did … eat? Does … ?)
        if root.tag_ == "VB" and not subj and all(a.lemma_.lower() == "do" and a.tag_ not in ("VBD", "VBZ") for a in aux):
            mood = "IMP"
        person, num = 3, "SG"
        if root.lemma_ == "let":                         # "let us go" → SBJV 1PL
            xs = [k for k in kids if k.dep_ in ("ccomp", "xcomp")]
            if xs and any(c.text.lower() == "us" for c in list(xs[0].children) + kids):
                root, lemma, mood = xs[0], xs[0].lemma_.lower(), "SBJV"
                self.used.add(root.i)
                kids = [c for c in root.children if c.text.lower() != "us"]
                subj, person, num = [], 1, "PL"
        if root.dep_ == "advcl":
            # 'If you come …', 'When the sun rises …', 'Because the king was angry …': the subordinate clause takes
            # the particle h₁yód 'if, when' (pie.realize "particle": "yod"; idioms.json 'because': a clause with
            # h₁yód), not the interrogative kʷóm 'when?'. Other subordinators have no rule and are reported.
            for k in kids:
                if k.dep_ in ("mark", "advmod") and k.text.lower() in SUBORDINATORS:
                    self.used.add(k.i)
                    if SUBORDINATORS[k.text.lower()]:
                        cl["particle"] = "yod"
                    else:
                        notes.append(f"'{k.text}' left out (no PIE conjunction for it in the engine)")
            kids = [k for k in kids if not (k.dep_ in ("mark", "advmod") and k.text.lower() in SUBORDINATORS)]
        voice = "MID" if any(k.dep_ == "nsubjpass" for k in kids) else "ACT"
        # possessive 'have' ('I have a horse', 'the king had no son'): the possessor in the dative, the possessed the
        # subject of h₁ésti (h₁éḱwos moy h₁ésti, Lat. mihi est equus). The perfect's 'have' is an aux of the
        # participle (root 'seen'), never this root; 'have to go' (xcomp) keeps the verb.
        possess = (lemma == "have" and mood != "IMP" and bool(subj) and any(k.dep_ == "dobj" for k in kids)
                   and not any(k.dep_ in ("xcomp", "ccomp") for k in kids))
        if possess and POSSESSIVE_HAVE_NOTE not in notes:
            notes.append(POSSESSIVE_HAVE_NOTE)
        for s in subj:
            low = s.text.lower()
            if possess:
                self.used.add(s.i)
                if low in PRONOUNS:
                    p, n = PRONOUNS[low]
                    if p in (1, 2):
                        slots.append({"lex_id": f"closed:personal/{p}", "role": "IO", "num": n, "enclitic": True})
                    else:
                        slots.append({"lex_id": "closed:anaphoric_i", "role": "IO", "num": n,
                                      "gender": GENDER.get(low, "m")})
                else:
                    self.np_slots(s, "IO", slots, notes, unknown)
                continue
            if low in PRONOUNS:
                person, num = PRONOUNS[low]
                if person == 3:
                    num = PRONOUNS[low][1]
            else:
                self.np_slots(s, "SUBJ", slots, notes, unknown)
                conj = sum(c.dep_ == "conj" for c in s.children)
                num = "DU" if conj == 1 else "PL" if conj or s.morph.get("Number") == ["Plur"] else "SG"
        if mood == "IMP":
            person = 2
        # copula: "X is Y" / "X is good"
        copula = lemma == "be"
        attr = [k for k in kids if k.dep_ in ("attr", "acomp")]
        if copula and not attr:
            # 'Be well, my friend!': the parser makes 'well' an adverb; with 'be' it is the predicate 'healthy'
            # (lexmap OVERRIDES well → kéh₂ilos, as in the corpus's kéh₂ilos h₁sdʰí)
            attr = [k for k in kids if k.dep_ == "advmod" and k.text.lower() == "well"]
        # 'there is a king', 'there are no wolves': the noun is the subject of h₁ésti (existence takes the verb;
        # pie.realize, nominal sentences), which agrees with it
        existential = copula and attr and any(k.dep_ == "expl" for k in kids) and \
            all(a.pos_ in ("NOUN", "PROPN", "PRON") for a in attr)
        fragments = []        # '…, only death': a verbless noun phrase after a comma, an utterance of its own
        misread = []          # "…and drank water": the small model reads a past verb as the object's adjective
        for k in kids:
            d, low = k.dep_, k.text.lower()
            bad = [c for c in k.children if c.dep_ == "amod" and c.text.lower() in IRREGULAR]
            if d == "dobj" and bad:
                misread.append((bad[0], k))
            elif d == "dobj" and low == "home":            # "drive the cattle home" parsed as object 'cattle home'
                self.used.add(k.i)
                for c in k.children:
                    if c.dep_ == "compound":
                        self.np_slots(c, "OBJ", slots, notes, unknown)
                slots.append({"lex_id": "pie-lex-doxm", "role": "GOAL"})
            elif d in ("dobj",):
                self.np_slots(k, "SUBJ" if possess else "OBJ", slots, notes, unknown)
            elif d in ("dative", "iobj") and k.pos_ != "ADP":
                self.np_slots(k, "IO", slots, notes, unknown)
            elif d == "prep" or (d in ("dative", "iobj") and k.pos_ == "ADP"):
                prep = low
                role = PREP_ROLE.get(prep)
                if prep == "to" and lemma in GIVE_LIKE:
                    role = "IO"
                for g in k.children:
                    if g.dep_ == "pobj" and role:
                        self.np_slots(g, role, slots, notes, unknown)
                    elif g.dep_ == "pobj":
                        notes.append(f"'{prep} {g.text}' left out (no case rule for '{prep}')")
            elif d == "advmod" and low == "home":            # "go home", "drive the cattle home": a goal
                self.used.add(k.i)
                slots.append({"lex_id": "pie-lex-doxm", "role": "GOAL"})
            elif d == "advmod" and low in WH_ADV:
                self.used.add(k.i)
                slots.append({"lex_id": WH_ADV[low], "role": "ADV"})
            elif d in ("advmod", "npadvmod", "prt") and low in self.adverbs and not (d == "prt" and low in ("up", "down", "out", "off")):
                # 'yesterday', 'here', 'again', 'ran away' (a phrasal verb's up/down/out/off is part of the verb's
                # meaning, 'give up', 'sit down': left out and reported)
                self.used.add(k.i)
                base = len(slots)
                for x in self.adverbs[low]:
                    slots.append({**x, **({"head": base + x["head"]} if "head" in x else {})})
            elif d in ("advmod", "neg") and low == "never":
                self.used.add(k.i)
                neg = True
                notes.append("'never' → ne 'not' (no PIE word for 'never')")
            elif d == "advmod" and low not in ("not", "n't"):
                pass                                     # reported by translate() as left out
            elif d in ("npadvmod", "intj", "appos") and k.pos_ in ("NOUN", "PROPN") and _comma_next_to(k):
                self.np_slots(k, "VOC", slots, notes, unknown)
            elif d in ("npadvmod", "appos") and k.pos_ in ("NOUN", "PROPN") and k.i > root.i \
                    and k.left_edge.i > 0 and k.doc[k.left_edge.i - 1].text == ",":
                if mood == "IMP" or person == 2:         # 'Come, my friend!', 'You are drunk, dear friend': an address
                    self.np_slots(k, "VOC", slots, notes, unknown)
                else:
                    fragments.append(k)
            elif d == "conj" and k.pos_ in ("VERB", "AUX"):
                pass
        if existential:
            for a in attr:
                self.np_slots(a, "SUBJ", slots, notes, unknown)
            slots.append({"lex_id": "pie-lex-h1esti", "role": "V",
                          "verb": {"tense": "PST" if tense == "AOR" else "PRS", "mood": mood, "voice": "ACT"}})
        elif copula and attr:
            a = attr[0]
            if a.pos_ == "ADJ" or a.text.lower() == "well":
                lid = self.adj(a, unknown, notes)
                if lid:
                    slots.append({"lex_id": lid, "role": "PRED"})
                    self.degree(a, len(slots) - 1, slots, notes, unknown)
            elif a.pos_ in ("NOUN", "PROPN"):
                self.np_slots(a, "PRED", slots, notes, unknown, num="PL" if num == "PL" else "SG")
            elif a.pos_ == "PRON" and a.text.lower() in ("who", "what"):
                slots.append({"lex_id": "closed:interrogative_kwi", "role": "PRED", "gender": "n" if a.text.lower() == "what" else "m"})
            nominal = tense == "PRS" and mood == "IND" and person == 3 and any(s["role"] == "SUBJ" for s in slots)
            if nominal and not any(s["role"] == "PRED" for s in slots):
                # the predicate has no PIE word ('My name is David': a name): the subject alone, as a noun phrase
                for s_ in slots:
                    if s_["role"] == "SUBJ":
                        s_["role"] = "NP"
                cl["type"] = "np"
            elif nominal:
                cl["type"] = "nominal"
            else:
                slots.append({"lex_id": "pie-lex-h1esti", "role": "V",
                              "verb": {"tense": "PST" if tense == "AOR" else "PRS", "mood": mood, "voice": "ACT",
                                       "person": person, "num": num}})
        elif copula:                                     # "Where is my father?": existence/location
            slots.append({"lex_id": "pie-lex-h1esti", "role": "V",
                          "verb": {"tense": "PST" if tense == "AOR" else "PRS", "mood": mood, "voice": "ACT",
                                   "person": person, "num": num}})
        elif possess:                                    # h₁ésti agrees with the possessed (its subject)
            slots.append({"lex_id": "pie-lex-h1esti", "role": "V",
                          "verb": {"tense": "PST" if tense == "AOR" else "PRS", "mood": mood, "voice": "ACT"}})
        else:
            if root.text.lower() in IRREGULAR:                  # spaCy's small model leaves some ("drank")
                lemma, tense = IRREGULAR[root.text.lower()], "AOR" if mood == "IND" else tense
            elif not self.map.candidates(lemma, "verb"):
                lemma = next((w for w in verb_lemmas(root) if self.map.candidates(w, "verb")), lemma)
            if inherit:
                tense, mood = inherit["tense"], inherit["mood"]
            lid, t = self.verb(lemma, tense, mood, notes, prohibitive=neg and mood == "IMP")
            if not lid:
                unknown.append(root.text)
                return []
            v = {"tense": t, "mood": mood, "voice": voice}
            if not any(s["role"] == "SUBJ" for s in slots):
                v.update(person=person, num=num)
            if self.lx.middle_only(lid):
                v["voice"] = "MID"
            if _valency(lid) == "fear":          # 'fear the wolf' = 'fear from the wolf' (check_plan; Ved. bhī- + abl.)
                for s_ in slots:
                    if s_["role"] == "OBJ" and s_.get("dep") is None and "head" not in s_:
                        s_["role"] = "ABL"
            slots.append({"lex_id": lid, "role": "V", "verb": v})
        if neg:
            cl["neg"] = True
        out = [cl]
        for vtok, obj in misread:
            extra: list[dict] = []
            self.np_slots(obj, "OBJ", extra, notes, unknown)
            lid, t = self.verb(IRREGULAR[vtok.text.lower()], tense, mood, notes)
            if lid:
                v = {"tense": t, "mood": mood, "voice": "ACT", "person": person, "num": num}
                out.append({"conj": "kʷe", "slots": extra + [{"lex_id": lid, "role": "V", "verb": v}]})
            else:
                unknown.append(vtok.text)
        for k in kids:            # "we hold these truths to be evident", "I want to eat": the clause it governs
            if k.dep_ in ("ccomp", "xcomp", "advcl") and k.pos_ in ("VERB", "AUX"):
                sub_subj = any(x.dep_ in ("nsubj", "nsubjpass") for x in k.children)
                objs = [i for i, s_ in enumerate(slots) if s_["role"] == "OBJ" and "head" not in s_]
                preds = [x for x in k.children if x.dep_ in ("acomp", "attr") and x.pos_ == "ADJ"]
                if k.lemma_ == "be" and not sub_subj and objs and preds:
                    # "we hold these truths to be evident": a predicative adjective agreeing with the object
                    # (double accusative), not a clause of its own
                    self.used.add(k.i)
                    for p_ in preds:
                        lid = self.adj(p_, unknown, notes)
                        if lid:
                            slots.insert(len(slots) - 1, {"lex_id": lid, "role": "MOD", "head": objs[0]})
                    continue
                more = self.clause(k, sent, notes, unknown,
                                   inherit=None if sub_subj or k.lemma_ == "be" else {"tense": tense, "mood": "IND"})
                for c in more:
                    for s_ in c["slots"]:
                        if s_["role"] == "V" and not sub_subj:
                            s_["verb"]["person"], s_["verb"]["num"] = person, num
                # a subordinate clause that comes first in the English comes first in the PIE (h₁yód … , main)
                out = more + out if k.dep_ == "advcl" and k.i < root.i else out + more
        for k in kids:                                    # "…and drank": a coordinated verb, same subject
            if k.dep_ == "conj" and k.pos_ in ("VERB",):
                more = self.clause(k, sent, notes, unknown, inherit={"tense": tense, "mood": mood})
                if more:
                    more[0]["conj"] = "kʷe"
                    for s in more[0]["slots"]:
                        if s["role"] == "V" and not any(x.dep_ in ("nsubj", "nsubjpass") for x in k.children):
                            s["verb"]["person"], s["verb"]["num"] = person, num
                    out += more
        for k in fragments:              # 'There is no hope, only death': the noun phrase as an np utterance
            extra: list[dict] = []
            if self.np_slots(k, "NP", extra, notes, unknown) is not None:
                out.append({"type": "np", "slots": extra})
                notes.append(f"'{k.doc[k.left_edge.i:k.right_edge.i + 1].text}' (no verb) → a noun phrase of its own")
        return out

    def np_utterance(self, root, notes, unknown) -> list[dict]:
        """A sentence with no verb ('wolf', 'Two horses.', 'The wolf and the dog.'): a noun-phrase utterance (the
        engine's "np" clause type, planner-brief-v4 'Noun-phrase utterance'), in the nominative. A lone adjective
        ('beautiful') is the masculine adjective as a noun."""
        slots: list[dict] = []
        if root.pos_ == "ADJ":
            lid = self.adj(root, unknown, notes)
            if not lid:
                return []
            slots.append({"lex_id": lid, "role": "NP", "gender": "m"})
        elif self.np_slots(root, "NP", slots, notes, unknown) is None:
            return []
        return [{"type": "np", "slots": slots}]

    # ---------------------------------------------------------------- text
    def translate(self, english: str) -> Result:
        doc = nlp()(english)
        self.used = set()
        self.neg_dets = set()
        notes: list[str] = []
        unknown: list[str] = []
        clauses = []
        for sent in doc.sents:
            root = sent.root
            voc = None
            if root.pos_ in ("NOUN", "PROPN") and _comma_next_to(root):
                verbs = [c for c in root.children if c.pos_ in ("VERB", "AUX") and c.dep_ in ("relcl", "ccomp", "acl", "appos")]
                if verbs:
                    voc, root = root, verbs[0]
            if voc is None and root.pos_ in NP_HEADS:
                cls = self.np_utterance(root, notes, unknown)
            else:
                cls = self.clause(root, sent, notes, unknown)
            if cls and voc is not None:
                self.np_slots(voc, "VOC", cls[0]["slots"], notes, unknown)
            if not cls:
                continue
            for c in cls:                 # 'Come, young men!': a plural addressee makes the 2nd-person verb plural
                vocs = [s_ for s_ in c["slots"] if s_["role"] == "VOC" and s_.get("num") in ("DU", "PL")]
                if vocs and not any(s_["role"] == "SUBJ" for s_ in c["slots"]):
                    for s_ in c["slots"]:
                        if s_["role"] == "V" and s_["verb"].get("person") == 2:
                            s_["verb"]["num"] = vocs[0]["num"]
            cls[0]["break"] = bool(clauses)
            if sent.text.strip().endswith("?"):
                for c in cls:
                    c["question"] = True
            cls[0]["english"] = sent.text.strip()
            clauses += cls
        # every content word that became no slot is reported, never dropped silently
        skip = {"be", "do", "have", "will", "shall", "may", "let", "not", "to"}
        left = [t.text for t in doc if t.i not in self.used and t.pos_ in ("NOUN", "PROPN", "VERB", "ADJ", "ADV", "NUM")
                and t.lemma_.lower() not in skip and t.text not in unknown]
        if left:
            notes.append("left out (no rule for how it fits the sentence): " + ", ".join(left))
        stray_no = [t.head.text for t in doc if t.dep_ == "det" and t.text.lower() == "no" and t.i not in self.neg_dets]
        if stray_no:
            notes.append("'no' left out (it negates the clause only on a subject or object): "
                         + ", ".join(f"'no {w}'" for w in stray_no))
        if not clauses:
            return Result(english, None, None, None, unknown, notes, ["nothing to translate"])
        plan = {"english": english, "clauses": clauses}
        errors: list[str] = []
        for _ in range(8):
            errs = check_plan(plan, self.lx)
            if not errs:
                break
            errors += errs
            if not self._drop_for(plan, errs[0], notes):
                return Result(english, None, None, plan, unknown, notes, errs)
        else:
            return Result(english, None, None, plan, unknown, notes, errors)
        r = realize(plan, self.lx)
        ids: list[str | None] = []
        for w in r["words"]:                     # an enclitic (-kʷe) is written onto the word before it
            if not w["form"].startswith("-"):
                ids.append(w["lex_id"])
        return Result(english, r["pie"], r["gloss"], plan, unknown, notes, [], ids)

    @staticmethod
    def _drop_for(plan: dict, err: str, notes: list[str]) -> bool:
        """Drop the slot an error names (clause N slot M), so the rest still translates."""
        m = re.search(r"clause (\d+).*?slot (\d+)", err)
        if not m:
            return False
        ci, si = int(m[1]), int(m[2])
        try:
            slots = plan["clauses"][ci]["slots"]
            if slots[si]["role"] == "V":
                return False
            dropped = slots.pop(si)
        except (IndexError, KeyError):
            return False
        for s in slots:
            for k in ("head", "dep"):
                if k in s and s[k] is not None:
                    if s[k] == si:
                        s.pop(k)
                    elif s[k] > si:
                        s[k] -= 1
        notes.append(f"left out {dropped['lex_id']} ({err})")
        return True
