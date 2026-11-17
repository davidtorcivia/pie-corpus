"""Greetings, thanks and the other set phrases a visitor types first ("Hello", "Thank you", "Welcome!"), for the
translator. No PIE greeting or thanks formula is reconstructible, so these are said the way the project's planner
brief says to build them from inherited words (docs/generation/planner-brief-v4.md, "Greetings and thanks"):
- a greeting is the wish "be well!", kéh₂ilos h₁sdʰí (Goth. hails, OE wes hāl);
- welcome is the address "dear guest!", príHe gʰóstey;
- thanks are praise of the giver, gʷr̥néH- 'praise' ("I praise you");
- a farewell is the same wish "be well!": the daughters part with the formula they greet with (Gk. χαῖρε for both;
  Lat. salvē / valē, both "be well"), an extension of the brief's greeting rule, noted as such.
Each rewrite is translated like any other English (the memory, then the rules) and carries a note saying what was
done. Words with no PIE counterpart at all ('please'; a bare 'yes' or 'no', which PIE says by repeating the question's
verb, idioms.json) are reported, never turned into some other word.

    rewrite("Hello, my friend!")  →  [("Be well, my friend!", "<note>")]
    rewrite("Hello, how are you?") →  [("Be well!", "<note>"), ("how are you?", None)]
"""
from __future__ import annotations

import re

GREETING_NOTE = ("'{w}' → 'be well!' (kéh₂ilos h₁sdʰí): no PIE greeting is reconstructible; the daughters greet with "
                 "a wish (Goth. hails, OE wes hāl; planner-brief-v4, Greetings and thanks)")
WELCOME_NOTE = ("'{w}' → 'dear guest!' (príHe gʰóstey): no PIE word for 'welcome'; the guest is greeted as dear "
                "(planner-brief-v4, Greetings and thanks)")
THANKS_NOTE = ("'{w}' → 'I praise you': no PIE word for thanks; thanks are praise of the giver, gʷr̥néH- "
               "(planner-brief-v4, Greetings and thanks)")
FAREWELL_NOTE = ("'{w}' → 'be well!' (kéh₂ilos h₁sdʰí): no PIE farewell is reconstructible; the daughters part "
                 "with a wish of health as they greet with one (Gk. χαῖρε, Lat. valē), so the brief's greeting is used "
                 "(planner-brief-v4, Greetings and thanks, extended to partings)")
PLEASE_NOTE = "'please' left out (no PIE word for it)"
YES_NO_NOTE = ("'{w}' has no PIE word: an answer repeats the question's verb ('yes') or puts ne before it ('no') "
               "(data/lexicon/idioms.json, yes/no)")

_GREET = r"(?:hello|hallo|hullo|hi|hey|hiya|howdy|greetings|hail|good (?:morning|day|afternoon|evening))(?: there)?"
_FAREWELL = r"(?:good-?\s?bye|bye(?:-?\s?bye)?|farewell)"
_THANKS = r"(?:thank you(?: (?:very|so) much)?|thanks(?: a lot)?|many thanks|thank you kindly)"
_END = r"[\s.!?,;:]*"


def _clause_like(rest: str) -> bool:
    """A rest that is a sentence of its own ('how are you?') rather than an address ('my friend')."""
    if rest.rstrip().endswith("?"):
        return True
    from .transfer import nlp
    return any(t.pos_ in ("VERB", "AUX") for t in nlp()(rest))


def rewrite(sentence: str) -> list[tuple[str, str | None]] | None:
    """[(english to translate, note)] for a sentence that is or starts with a set phrase, else None. An empty
    english means there is nothing to translate and the note says why."""
    s = sentence.strip()
    low = s.lower()
    m = re.fullmatch(rf"({_GREET}){_END}", low)
    if m:
        return [("Be well!", GREETING_NOTE.format(w=s.rstrip(" .!?,")))]
    # 'Hello, my friend!', 'Hi David', 'Good morning, how are you?': a comma or '!' after the greeting, or one of
    # the words that is only a greeting ('Hail fell from the sky' is not one)
    m = re.match(rf"({_GREET})(\s*[,!]\s*|\s+)(.+)$", s, flags=re.I)
    if m and (m[2].strip() or re.fullmatch(r"(?:hello|hallo|hullo|hi|hey|hiya|howdy|greetings)", m[1].lower())):
        rest = m[3].strip()
        note = GREETING_NOTE.format(w=m[1])
        if _clause_like(rest):
            return [("Be well!", note), (rest, None)]
        return [(f"Be well, {rest.rstrip(' .!?')}!", note)]
    m = re.fullmatch(rf"({_FAREWELL}){_END}", low)
    if m:
        return [("Be well!", FAREWELL_NOTE.format(w=s.rstrip(" .!?,")))]
    m = re.match(rf"({_FAREWELL})\s*[,!]\s*(.+)$", s, flags=re.I)     # 'Goodbye, my friend!'
    if m and not _clause_like(m[2]):
        return [(f"Be well, {m[2].strip().rstrip(' .!?')}!", FAREWELL_NOTE.format(w=m[1]))]
    if re.fullmatch(rf"welcome{_END}", low):            # not "you're welcome", the answer to thanks
        return [("Dear guest!", WELCOME_NOTE.format(w=s.rstrip(" .!?,")))]
    m = re.fullmatch(rf"({_THANKS})(?:,? (.+?))?{_END}", low)
    if m and (not m[2] or not _clause_like(m[2])):
        tail = s[len(m[1]):].strip(" ,.!?") if m[2] else ""
        # the address first ('My friend, I praise you.'): the parser reads a trailing one as part of the clause
        return [(f"{tail[0].upper() + tail[1:]}, I praise you." if tail else "I praise you.",
                 THANKS_NOTE.format(w=m[1]))]
    if re.fullmatch(rf"(?:yes|yeah|yep|no|nope){_END}", low):
        return [("", YES_NO_NOTE.format(w=s.rstrip(" .!?,")))]
    if re.search(r"\bplease\b", low):
        rest = re.sub(r",?\s*\bplease\b\s*,?", " ", s, flags=re.I).strip()
        rest = re.sub(r"\s+([.!?,;:])", r"\1", re.sub(r"\s+", " ", rest))
        if not re.search(r"[A-Za-z]", rest):
            return [("", PLEASE_NOTE)]
        return [(rest[0].upper() + rest[1:], PLEASE_NOTE)]
    return None
