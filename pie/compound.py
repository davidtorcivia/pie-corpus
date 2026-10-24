"""Nominal compounds: stem formation, inflection and accent from two lexemes.

The rules (and their sources) are stated in pie/realize.py's docstring, which
is the planner-facing schema. This module holds the machinery, shared by the
realizer (pie.realize) and the validator (pie.validate), so a compound is
generated and recognized by one function.

  resolve(c, lx) → Compound      c = {"first": ..., "second": ..., "type": ...}
  Compound.cells(gender) → Cells  bahuvrihi: m/f/n; determinative: the head's gender

`lx` is a pie.realize.Lexicon (anything with .entries, .specs, .blocked,
.gender(lex_id) and .gloss(lex_id)). Members are joined as strings, never with
phon.join: the first member is its own prosodic word, so its final resonant keeps
its syllabicity (privative n̥-h₁…, not *nh₁…).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .morph import AdjSpec, Cells, NounSpec, _bare, _initial_accent, _uniq, decline, decline_adj
from .phon import deaccent, has_accent, parse, render

TYPES = ("bahuvrihi", "determinative")

# closed first members: id → (form, inherently accented, gloss)
#   h₁su- 'good', dus- 'bad' (Fortson §6.86, Ringe 2.4.1; Ved. su-, dus-); privative *n̥- (Fortson §7.25);
#   *sm̥- 'one, same' and the numeral prefixes *dwi- *tri- *kʷetru- (Fortson §7.18; L&Y dwi-)
PREFIXES = {
    "closed:prefix/h1su": ("h₁su", False, "good"),
    "closed:prefix/dus": ("dus", False, "bad"),
    "closed:prefix/n": ("ń̥", True, "un"),
    "closed:prefix/sm": ("sm̥", False, "one"),
    "closed:numerals/2": ("dwi", False, "two"),
    "closed:numerals/3": ("tri", False, "three"),
    "closed:numerals/4": ("kʷetru", False, "four"),
}
# the lexicon's affix entries name the same prefixes
PREFIX_ALIASES = {"pie-lex-h1su": "closed:prefix/h1su", "pie-lex-dus": "closed:prefix/dus",
                  "pie-lex-n": "closed:prefix/n", "pie-lex-sm": "closed:prefix/sm",
                  # the numeral lexemes compound as *dwi- *tri- *kʷetru- (Fortson §7.18), not as dwó-
                  # (engine sweep, closed-class-compounds.md P2)
                  "pie-lex-dwoh1": "closed:numerals/2", "pie-lex-treyes": "closed:numerals/3",
                  "pie-lex-kwetwores": "closed:numerals/4"}


class CompoundError(ValueError):
    """A compound the engine cannot build; the message is for the planner."""


def _deacc(form: str) -> str:
    return render(deaccent(parse(form)))


def _vocalic_onset(form: str) -> bool:
    s = parse(form)
    return bool(s) and s[0].vocalic


def _vowel_onset(form: str) -> bool:
    """A true vowel or syllabic i/u (*n̥(n)udro-), not a syllabic liquid or nasal."""
    s = parse(form)
    return bool(s) and (s[0].kind == "V" or (s[0].syl and s[0].base in ("y", "w")))


@dataclass(frozen=True)
class Compound:
    ctype: str
    first: str               # first-member id as given (aliases normalized)
    second: str              # second-member lex_id
    first_form: str          # compositional form, accent as written in the compound
    first_accented: bool
    second_kind: str         # "s-neuter" | "thematic" | "noun" (determinative head)
    lx: object

    @property
    def lex_id(self) -> str:
        return f"compound:{self.ctype}:{self.first}+{self.second}"

    def gloss(self) -> str:
        g1 = PREFIXES[self.first][2] if self.first in PREFIXES else self.lx.gloss(self.first)
        return f"{g1}+{self.lx.gloss(self.second)}"

    @property
    def head_gender(self) -> str:
        return self.lx.gender(self.second)

    # --- stems -------------------------------------------------------------
    def _second_stem(self) -> str:
        sp = self.lx.specs[self.second]["spec"]
        return _bare(sp["weak"] if self.second_kind == "s-neuter" else sp["strong"])

    def _stems(self) -> list[str]:
        """Bahuvrihi stems, primary first. BAP: the leftmost inherent accent wins."""
        st2 = self._second_stem()
        f = self.first_form
        if self.first == "closed:prefix/n" and _vowel_onset(st2):
            f = f + "n"                                    # *n̥(n)udro- (L&Y), not *nudro-
        f_plain = _deacc(f)
        if self.first_accented:
            out = [f + _deacc(st2)]
            if self.first == "closed:prefix/n":
                out.append(f_plain + st2)                   # 2M-accented variant (lexical n̥mr̥tós, Ved. amṛ́ta-)
        else:
            out = [f_plain + st2]
        if self.second_kind == "s-neuter":
            # suffix accent *-és- (Clackson *dus-m(e)n-és-; productive Gk -ḗs): an alternative only
            segs = deaccent(parse(f_plain + _deacc(st2)))
            i = max(k for k, x in enumerate(segs) if x.kind == "V")
            segs[i] = replace(segs[i], acc=True)
            out.append(render(segs))
        if not has_accent(parse(out[0])):
            out[0] = render(_initial_accent(parse(out[0])))   # BAP default: leftmost syllable
        return _uniq(out)

    # --- cells -------------------------------------------------------------
    def cells(self, gender: str | None = None) -> Cells:
        key = ("CMP", self.lex_id, gender)
        cache = getattr(self.lx, "_cache", {})
        if key in cache:
            return cache[key]
        c = self._bahuvrihi(gender or "m") if self.ctype == "bahuvrihi" else self._determinative()
        cache[key] = c
        return c

    def _bahuvrihi(self, gender: str) -> Cells:
        out: Cells = {}
        for stem in self._stems():
            if self.second_kind == "thematic":
                c = decline_adj(AdjSpec(stem), "handbook")[gender]
            else:
                # s-stem adjective: common gender (Gk εὐκλεής m./f., Ved. sumánās m./f.); the feminine is
                # the masculine, not a devī stem. Non-ablauting -es- (Gk gen. -eos, Ved. -asas).
                g = "n" if gender == "n" else "m"
                c = decline(NounSpec(stem, stem, None, g), "handbook")
                if g == "n":   # nom.-acc. pl. *-es-h₂ (Gk -εα) beside the engine's collective -ēs
                    for k in ("NOM.PL", "ACC.PL", "VOC.PL"):
                        c[k] = _uniq(c[k] + [stem + "h₂"])
            for k, v in c.items():
                out[k] = _uniq(out.get(k, []) + v)
        return out

    def _determinative(self) -> Cells:
        """The head's paradigm with the deaccented first member in front (Ved. rāja-putrá-,
        kr̥ṣṇa-śakuní-, viś-páti-: the head keeps its accent)."""
        r = self.lx.specs[self.second]
        sp = dict(r["spec"])
        f = _deacc(self.first_form)
        for k in ("strong", "weak", "nom_sg"):
            if sp.get(k):
                sp[k] = f + _bare(sp[k])
        sp["loc_sg"] = [f + _bare(x) for x in sp.get("loc_sg") or []]
        c = decline(NounSpec(**sp), "handbook")
        lemma = self.lx.entries[self.second]["form"]
        base = decline(NounSpec(**r["spec"]), "handbook")
        if not lemma.endswith("-") and r.get("rule") == "table" and lemma not in base.get("NOM.SG", []) \
                and NounSpec(**r["spec"]).kind != "thematic":
            # as Lexicon.cells: the headword is the attested citation form (not for o-stems: thematic.md 5)
            c = {**c, "NOM.SG": [f + lemma] + c.get("NOM.SG", [])}
            if self.head_gender == "n":
                c["ACC.SG"] = [f + lemma] + c.get("ACC.SG", [])
                c["VOC.SG"] = [f + lemma] + c.get("VOC.SG", [])
        return c


_CALAND_MSG = ("first member {}: a -ro- adjective's compound form is the Caland -i- stem (Fortson §6.87, "
               "Ringe 2.4.2: h₂r̥ǵrós → h₂r̥ǵi-), which the engine does not build")


def _caland(stem: str, accented_only: bool = False) -> bool:
    """A -ro- adjective stem (C-ró-; a noun spec'd from an adjective counts only with the accented suffix)."""
    segs = parse(stem)
    return (len(segs) > 2 and segs[-2].base == "r" and not segs[-2].syl and segs[-1].base == "o"
            and not segs[-3].vocalic and (segs[-1].acc or not accented_only))


def _noun_class(r: dict) -> str:
    sp = r["spec"]
    s, w = _bare(sp["strong"]), sp.get("weak")
    if w is None and s[-1:] in ("o", "ó"):
        return "thematic"
    if sp.get("gender") == "n" and s.endswith(("os", "ós")) and w and _bare(w).endswith(("es", "és")):
        return "s-neuter"
    segs = parse(s)
    if segs and segs[-1].kind == "R" and segs[-1].syl and segs[-1].base in ("y", "w"):
        return "i/u-stem"
    return "other"


def _usable(lid: str, lx, what: str) -> dict:
    r = lx.specs.get(lid)
    if not r or not r.get("spec"):
        raise CompoundError(f"{what} {lid!r} is not an inflectable lexeme")
    if lid in getattr(lx, "blocked", {}):
        raise CompoundError(f"{what} {lid} is blocked from generation: {lx.blocked[lid]}")
    if not r.get("usable"):
        raise CompoundError(f"{what} {lid} has no usable spec (rule {r.get('rule')})")
    return r


def _first(fid: str, ctype: str, lx) -> tuple[str, bool]:
    """(compositional form, inherently accented)."""
    if fid in PREFIXES:
        if ctype != "bahuvrihi":
            raise CompoundError(f"first member {fid} is a prefix: prefix compounds are bahuvrihis "
                                f"(type 'bahuvrihi'); a negated adjective is its own lexeme (n̥mr̥tós)")
        form, acc, _ = PREFIXES[fid]
        return form, acc
    r = _usable(fid, lx, "first member")
    sp = r["spec"]
    if r["family"] == "adj":
        if sp.get("m_weak") is None:
            stem = _bare(sp["m_strong"])
            if _caland(stem):
                raise CompoundError(_CALAND_MSG.format(fid))
            return stem, has_accent(parse(stem))            # thematic -o- keeps its accent (Ved. ugrá-bāhu-)
        stem = _bare(sp["m_strong"])
        last = parse(stem)[-1]
        if last.kind == "R" and last.syl and last.base == "w":
            return _deacc(stem), False                      # u-stem -u-: yields to 2M (Ved. āśu-héṣas-)
        raise CompoundError(f"first member {fid}: only thematic (-o-) and u-stem (-u-) adjectives have a "
                            f"compositional form the engine builds")
    if r["family"] == "noun":
        k = _noun_class(r)
        if k in ("thematic", "i/u-stem"):
            stem = _bare(sp["strong"])
            if _caland(stem, accented_only=True):
                raise CompoundError(_CALAND_MSG.format(fid))
            return stem, has_accent(parse(stem))            # Gk khrūsó-thronos, Ved. bāhú-ojas-
        segs = parse(_bare(sp["strong"]))
        if len(segs) > 1 and segs[-1].kind == "R" and not segs[-1].syl and segs[-1].base in ("y", "w") \
                and not segs[-2].vocalic:
            # a root noun whose stem ends in a glide after a consonant composes in -u-/-i- like a u-stem:
            # néh₂w- 'ship' → néh₂u- (néh₂uwiHrós; engine sweep: the i-u-stems.md #6 spec néh₂w- replaced néh₂u-)
            stem = render(segs[:-1] + [replace(segs[-1], syl=True)])
            return stem, has_accent(parse(stem))
        raise CompoundError(f"first member {fid}: only thematic and i-/u-stem nouns have a compositional "
                            f"form the engine builds (consonant stems take a zero grade: Beekes 13.1.4)")
    raise CompoundError(f"first member {fid} is a {r['family']}: verbal compounds (*ḱlewos-dʰeh₁-) "
                        f"are not supported")


def resolve(c: dict, lx) -> Compound:
    """Check a compound description and return the Compound; raises CompoundError."""
    if not isinstance(c, dict):
        raise CompoundError("compound must be an object {first, second, type}")
    ctype = c.get("type", "bahuvrihi")
    if ctype not in TYPES:
        raise CompoundError(f"compound type must be one of {TYPES}, not {ctype!r}")
    fid, sid = c.get("first"), c.get("second")
    if not fid or not sid:
        raise CompoundError("compound needs a first and a second member")
    if "compound" in (fid, sid) or isinstance(fid, dict) or isinstance(sid, dict):
        raise CompoundError("nested compounds are not supported")
    fid = PREFIX_ALIASES.get(fid, fid)
    form, acc = _first(fid, ctype, lx)
    r = _usable(sid, lx, "second member")
    if r["family"] != "noun":
        raise CompoundError(f"second member {sid} is a {r['family']}: the second member must be a noun")
    k = _noun_class(r)
    if ctype == "bahuvrihi":
        if k not in ("thematic", "s-neuter"):
            raise CompoundError(f"second member {sid}: a bahuvrihi needs an s-stem neuter (ḱléwos → -ḱléwes-) "
                                f"or a thematic noun (h₁éḱwos → -h₁éḱwo-); the books give no general rule for "
                                f"other stems (Fortson §6.83 calls the o-grade of eu-pátōr unexplained)")
        kind = k
    else:
        kind = "noun"
    st2 = _bare(r["spec"]["weak"] if k == "s-neuter" and ctype == "bahuvrihi" else r["spec"]["strong"])
    if not has_accent(parse(st2)) and not has_accent(parse(lx.entries[sid]["form"])):
        raise CompoundError(f"second member {sid} has no accent marked; its compound accent is unknown")
    if fid in PREFIXES and _vocalic_onset(st2) and not form.endswith("s") and not (
            fid == "closed:prefix/n" and _vowel_onset(st2)):
        raise CompoundError(f"{fid} before a second member with a vocalic onset: the books give no junction rule")
    if fid not in PREFIXES and _vocalic_onset(st2):
        # a vowel-final stem (-o-, -u-, -i-) before a vowel or syllabic resonant gives hiatus (newo-úderos,
        # newo-n̥bʰrós): rejected as for the prefixes (engine sweep, closed-class-compounds.md P1)
        raise CompoundError(f"first member {fid} before a second member with a vocalic onset ({sid}): "
                            f"the books give no junction rule")
    return Compound(ctype, fid, sid, form, acc, kind, lx)


def member_ids(lex_id: str) -> list[str]:
    """The two member ids of a realized compound's lex_id (compound:<type>:<first>+<second>)."""
    if not lex_id.startswith("compound:"):
        return []
    return lex_id.split(":", 2)[2].rsplit("+", 1)
