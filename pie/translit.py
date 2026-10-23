"""Reversible transliteration between canonical PIE notation and ASCII.

The canonical form (the `pie` field) is NFC Unicode over a closed inventory;
the ASCII form (`pie_ascii`) is for tokenizers. Both directions are strict:
anything outside the inventory raises TranslitError instead of passing
through, so a string that converts cleanly is also notation-valid. Repairs of
foreign notations belong in pie.notation, not here.

The mapping is specified in docs/notation.md; keep the two in sync.
"""

from __future__ import annotations

import unicodedata

__all__ = [
    "TranslitError",
    "to_ascii",
    "to_unicode",
    "is_canonical",
    "PASSTHROUGH",
    "ESCAPED",
]


class TranslitError(ValueError):
    def __init__(self, msg: str, text: str, pos: int):
        self.msg, self.text, self.pos = msg, text, pos
        lo = max(0, pos - 8)
        super().__init__(f"{msg} at {pos}: …{text[lo:pos]}⟦{text[pos:pos + 1]}⟧{text[pos + 1:pos + 9]}…")


# Combining marks, in the order NFD leaves them (ring below has ccc 220, so it
# sorts before macron and acute, which share ccc 230 and keep input order).
RING = "\u0325"
MACRON = "\u0304"
ACUTE = "\u0301"

ASP = "\u02b0"  # ʰ
LAB = "\u02b7"  # ʷ
SUBSCRIPT = {"\u2081": "1", "\u2082": "2", "\u2083": "3"}
SUBSCRIPT_INV = {v: k for k, v in SUBSCRIPT.items()}

VOWELS = set("aeiou")
RESONANTS = set("rlmn")  # may carry RING (syllabic)
PLAIN = set("ptszwy") | RESONANTS  # consonants with no modifiers besides RING
ASPIRABLE = set("bdg")
VELARS = set("kg")

# Characters that pass through unchanged in both directions.
PASSTHROUGH = set(" -*=.,;?!()[]\"")
# Literal characters that the ASCII form uses as markup; they are written
# with a backslash escape there. `w` is escaped only after a plain velar.
ESCAPED = set(":/_'\\")


def _marks_ascii(marks: str) -> str | None:
    """ASCII suffix for a vowel's or syllabic's marks, or None if invalid."""
    return {"": "", MACRON: ":", ACUTE: "/", MACRON + ACUTE: ":/"}.get(marks)


def _nfd_with_origins(text: str) -> tuple[str, list[int]]:
    """NFD of text, plus the index in text that each NFD code point came from."""
    chars: list[str] = []
    origin: list[int] = []
    for idx, c in enumerate(text):
        for d in unicodedata.normalize("NFD", c):
            chars.append(d)
            origin.append(idx)
    # Canonical reordering: stable-sort each run of combining marks by class.
    i = 0
    while i < len(chars):
        if unicodedata.combining(chars[i]):
            j = i
            while j < len(chars) and unicodedata.combining(chars[j]):
                j += 1
            run = sorted(range(i, j), key=lambda k: unicodedata.combining(chars[k]))
            chars[i:j] = [chars[k] for k in run]
            origin[i:j] = [origin[k] for k in run]
            i = j
        else:
            i += 1
    return "".join(chars), origin


def to_ascii(text: str) -> str:
    """Canonical Unicode → ASCII. Accepts any normalization form."""
    s, origin = _nfd_with_origins(text)
    assert s == unicodedata.normalize("NFD", text)
    try:
        return _to_ascii(s)
    except TranslitError as e:
        pos = origin[e.pos] if e.pos < len(origin) else len(text)
        raise TranslitError(e.msg, text, pos) from None


def _to_ascii(s: str) -> str:
    text = s  # error positions are NFD offsets here; to_ascii maps them back
    out: list[str] = []
    i, n = 0, len(s)

    def marks_at(j: int) -> tuple[str, int]:
        k = j
        while k < n and unicodedata.combining(s[k]):
            k += 1
        return s[j:k], k

    while i < n:
        c = s[i]
        marks, j = marks_at(i + 1)

        if c in VOWELS:
            suf = _marks_ascii(marks)
            if suf is None:
                raise TranslitError("bad marks on vowel (expected macron before acute)", text, i)
            out.append(c + suf)
            i = j
        elif c in RESONANTS and marks:
            if not marks.startswith(RING) or _marks_ascii(marks[1:]) is None:
                raise TranslitError("bad marks on resonant", text, i)
            out.append(c + "_" + _marks_ascii(marks[1:]))
            i = j
        elif c in VELARS:
            if marks == ACUTE:
                base, palatal = c + "'", True
            elif not marks:
                base, palatal = c, False
            else:
                raise TranslitError("bad marks on velar", text, i)
            if j < n and s[j] == LAB:
                if palatal:
                    raise TranslitError("palatal cannot be labialized", text, j)
                base += "w"
                j += 1
            elif j < n and s[j] == "w" and not palatal:
                base += "\\w"  # plain velar + w, distinct from kʷ
                j += 1
                out.append(base)
                i = j
                continue
            if j < n and s[j] == ASP:
                if c == "k":
                    raise TranslitError("no voiceless aspirates in inventory", text, j)
                base += "h"
                j += 1
            out.append(base)
            i = j
        elif c in ASPIRABLE:  # b, d
            if marks:
                raise TranslitError("unexpected mark", text, i + 1)
            if j < n and s[j] == ASP:
                out.append(c + "h")
                i = j + 1
            else:
                out.append(c)
                i = j
        elif c in PLAIN:
            if marks:
                raise TranslitError("unexpected mark", text, i + 1)
            if j < n and s[j] in (ASP, LAB):
                raise TranslitError("modifier not allowed on this consonant", text, j)
            out.append(c)
            i = j
        elif c == "h":
            if marks or j >= n or s[j] not in SUBSCRIPT:
                raise TranslitError("h must be a numbered laryngeal (h₁ h₂ h₃)", text, i)
            out.append("h" + SUBSCRIPT[s[j]])
            i = j + 1
        elif c == "H":
            if marks:
                raise TranslitError("unexpected mark", text, i + 1)
            out.append("H")
            i = j
        elif c in PASSTHROUGH:
            out.append(c)
            i += 1
        elif c in ESCAPED:
            out.append("\\" + c)
            i += 1
        else:
            raise TranslitError(f"character outside inventory {c!r} (U+{ord(c):04X})", text, i)
    return "".join(out)


def to_unicode(ascii_text: str) -> str:
    """ASCII → canonical NFC Unicode. Accepts only canonical ASCII."""
    s = ascii_text
    out: list[str] = []
    i, n = 0, len(s)

    def peek(k: int) -> str:
        return s[k] if k < n else ""

    def aspiration(k: int) -> bool:
        # `h` is aspiration unless it starts a laryngeal (`h` + digit).
        return peek(k) == "h" and peek(k + 1) not in ("1", "2", "3")

    def vowel_marks(k: int) -> tuple[str, int]:
        m = ""
        if peek(k) == ":":
            m += MACRON
            k += 1
        if peek(k) == "/":
            m += ACUTE
            k += 1
        if peek(k) == ":":
            raise TranslitError("length must precede accent (e:/ not e/:)", s, k)
        return m, k

    while i < n:
        c = s[i]
        if c in VOWELS:
            m, i = vowel_marks(i + 1)
            out.append(c + m)
        elif c in RESONANTS and peek(i + 1) == "_":
            m, i = vowel_marks(i + 2)
            out.append(c + RING + m)
        elif c in VELARS:
            base, i = c, i + 1
            if peek(i) == "'":
                base += ACUTE
                i += 1
            elif peek(i) == "w":
                base += LAB
                i += 1
            elif peek(i) == "\\" and peek(i + 1) == "w":
                out.append(c + "w")
                i += 2
                continue
            if aspiration(i):
                if c == "k":
                    raise TranslitError("no voiceless aspirates in inventory", s, i)
                base += ASP
                i += 1
            out.append(base)
        elif c in ASPIRABLE:
            if aspiration(i + 1):
                out.append(c + ASP)
                i += 2
            else:
                out.append(c)
                i += 1
        elif c in PLAIN:
            if aspiration(i + 1):
                raise TranslitError("no aspirate on this consonant", s, i + 1)
            out.append(c)
            i += 1
        elif c == "h":
            d = peek(i + 1)
            if d not in SUBSCRIPT_INV:
                raise TranslitError("bare h (laryngeal needs a digit)", s, i)
            out.append("h" + SUBSCRIPT_INV[d])
            i += 2
        elif c == "H":
            out.append("H")
            i += 1
        elif c in PASSTHROUGH:
            out.append(c)
            i += 1
        elif c == "\\":
            e = peek(i + 1)
            if e not in ESCAPED:
                raise TranslitError("bad escape", s, i)
            out.append(e)
            i += 2
        else:
            raise TranslitError(f"character outside ASCII inventory {c!r}", s, i)
    return unicodedata.normalize("NFC", "".join(out))


def is_canonical(text: str) -> bool:
    """True if `text` is NFC and entirely within the canonical inventory."""
    if unicodedata.normalize("NFC", text) != text:
        return False
    try:
        to_ascii(text)
    except TranslitError:
        return False
    return True
