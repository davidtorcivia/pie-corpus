"""Tier 3b neologisms ("modern PIE"): coinages from attested roots and productive suffixes, built by the engine.

Policy: PLAN.md "Tier 3b" and the neologisms.jsonl schema. File: data/lexicon/neologisms.jsonl, one coinage per
line with PLAN's fields (neo_id, pie, english, derivation, model, rationale) plus pos, gender, gloss and the
derived `inflection` (the inflection_specs.jsonl schema). The design mirrors the project reconstructions
(pie.realize.load_project_reconstructions, docs/lexicon-project-reconstructions.md) with one difference:
project reconstructions are allowed in Tier 3 and so sit in the default Lexicon; neologisms are Tier 3b only,
so they are never in Lexicon.load(). A Tier 3b caller asks for them explicitly:

  with_neologisms(lx) -> Lexicon     a NEW Lexicon: the base one plus the neologisms (the cached
                                     Lexicon.load() is never mutated, so Tier 1-3 code never sees them)
  load_neologisms(lx) -> (entries, specs)   the one loader (with_neologisms and index_neologisms use it)
  index_neologisms(ix)               adds them to a validator index (pie.validate), like index_project

Every entry carries coined "neologism", so Lexicon.coined, the realizer's token flag (token_cell),
pie.realize.plan_coined and pie.export read the flag with no code of their own.

Three models (PLAN: compound | calque | derivative), each derived by engine code, never written by hand:
  derivative  root (a lexicon `root` entry) in a stated ablaut grade + a productive suffix (a lexicon `affix`
              entry), with the accent on the root or the suffix. derive_form() joins them (zero grade by
              pie.classify.zero_grade, the lexicon build's own function); the spec is pie.classify.by_shape
              of the headword, the classifier that gives the Wiktionary derivatives their specs. Calibrated on
              attested derivatives (tests/test_neologisms.py).
  compound    a pie.compound.resolve compound ({first, second, type}); the headword is its NOM.SG cell and
              the spec by_shape of the headword, accepted only when it declines to exactly Compound.cells()
              (so the compound engine stays the authority).
  calque      a modern sense on an existing lexeme (Lat. legō 'gather' > 'read'): the base's form and spec,
              under a new neo id so its tokens are flagged. The form is the base's own.
The stored `pie` and `inflection` must equal what the engine derives (checked on every load).

Invariants (checked on load): ids are pie-neo-<ascii>, never in lexicon.jsonl; every derivation id exists
(roots `kind: root`, suffixes `kind: affix`, members/bases are usable lexemes); no root of a held-out
benchmark family (pie.export.eval_root); a derivative or compound may not reproduce an existing lexicon form
(that is a calque of the existing word); exactly one accent; a usable, non-eh₂ spec.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from .classify import by_shape, zero_grade
from .morph import AdjSpec, NounSpec, decline, decline_adj
from .phon import parse, render

ROOT = Path(__file__).resolve().parent.parent
NEOLOGISMS = ROOT / "data/lexicon/neologisms.jsonl"
MODELS = ("compound", "calque", "derivative")
GRADES = ("e", "o", "zero")
POS_FAMILY = {"noun": "noun", "adj": "adj", "verb": "verb"}
# by_shape rules a neologism may not take: eh₂-stems are blocked systemically (backtest threshold;
# docs/lexicon-project-reconstructions.md "Existing but not offered")
BLOCKED_RULES = ("shape:eh2",)


class NeologismError(ValueError):
    """A coinage the engine cannot derive, or one that breaks the policy; the message names the row."""


# --- derivatives -------------------------------------------------------------------------------------------

def _accent_first_vowel(segs: list) -> list:
    i = next((k for k, x in enumerate(segs) if x.kind == "V" or (x.kind == "R" and x.syl)), None)
    if i is None:
        raise NeologismError(f"no vowel to accent in {render(segs)!r}")
    return [replace(x, acc=(k == i)) for k, x in enumerate(segs)]


def root_grade(root_form: str, grade: str) -> str:
    """The root in the e-, o- or zero grade, unaccented. e: as cited; o: the root's e → o; zero: the e deleted and
    its neighbours re-syllabified (pie.classify.zero_grade: gʷʰen- → gʷʰn̥-, ḱlew- → ḱlu-, kʷer- → kʷr̥-)."""
    segs = [replace(x, acc=False) for x in parse(root_form.strip("-"))]
    i = next((k for k, x in enumerate(segs) if x.kind == "V" and x.base == "e" and not x.long), None)
    if grade == "e":
        return render(segs)
    if i is None:
        raise NeologismError(f"root {root_form!r} has no e to put in the {grade} grade")
    if grade == "o":
        return render(segs[:i] + [replace(segs[i], base="o")] + segs[i + 1:])
    if grade == "zero":
        z = zero_grade(render(segs[:i] + [replace(segs[i], acc=True)] + segs[i + 1:]))
        if z is None:
            raise NeologismError(f"root {root_form!r} has no zero grade")
        return z
    raise NeologismError(f"grade must be one of {GRADES}, not {grade!r}")


def derive_form(root_form: str, grade: str, suffix_form: str, accent: str) -> str:
    """Headword of root (in `grade`) + suffix, accented on the root's vowel or the suffix's first vowel.
    kʷer- e + -trom, root → kʷértrom; preḱ- e + -nós, suffix → preḱnós; men- o + -éyeti, suffix → monéyeti."""
    root = parse(root_grade(root_form, grade))
    suf = [replace(x, acc=False) for x in parse(suffix_form.strip("-"))]
    if not suf:
        raise NeologismError(f"empty suffix {suffix_form!r}")
    if grade == "zero" and (suf[0].kind == "V" or (root and root[-1].syl and suf[0].vocalic)):
        # a vowel-initial suffix would need the root resonant re-syllabified across the junction
        raise NeologismError("a zero-grade root before a vowel-initial suffix is not built")
    if accent == "root":
        if grade == "zero":
            raise NeologismError("a zero-grade root carries no accent: use accent 'suffix'")
        root = _accent_first_vowel(root)
    elif accent == "suffix":
        suf = _accent_first_vowel(suf)
    else:
        raise NeologismError(f"accent must be 'root' or 'suffix', not {accent!r}")
    return render(root) + render(suf)


def _classify(form: str, pos: str, gender: str | None, where: str) -> dict:
    c = by_shape({"form": form, "pos": pos, "gender": gender})
    if c.spec is None or c.family != POS_FAMILY.get(pos) or not c.rule.startswith("shape:") or c.rule in BLOCKED_RULES:
        raise NeologismError(f"{where}: {form!r} ({pos}) has no usable engine spec (rule {c.rule})")
    return {"rule": c.rule, "family": c.family, "spec": asdict(c.spec)}


# --- the three models ----------------------------------------------------------------------------------------

def _head_cell(spec: dict, family: str) -> list[str]:
    from .morph import VerbSpec, conjugate
    if family == "noun":
        return decline(NounSpec(**spec), "handbook").get("NOM.SG", [])
    if family == "adj":
        return decline_adj(AdjSpec(**spec), "handbook")["m"].get("NOM.SG", [])
    return conjugate(VerbSpec(**spec), "handbook").get("PRS.3SG", []) or \
        conjugate(VerbSpec(**spec), "handbook").get("AOR.3SG", [])


def _derive(row: dict, lx) -> tuple[str, dict, str | None, str | None]:
    """(form, inflection, root_id, gender) of one row, from its derivation."""
    nid, model, d = row["neo_id"], row["model"], row["derivation"]
    where = f"{nid}"
    if model == "derivative":
        (root_id,), (suf_id,) = d["roots"], d["suffixes"]
        root, suf = lx.entries.get(root_id), lx.entries.get(suf_id)
        if not root or root.get("kind") != "root":
            raise NeologismError(f"{where}: {root_id!r} is not a lexicon root")
        if not suf or suf.get("kind") != "affix":
            raise NeologismError(f"{where}: {suf_id!r} is not a lexicon affix")
        form = derive_form(root["form"], d["grade"], suf["form"], d["accent"])
        inf = _classify(form, row["pos"], row.get("gender"), where)
        gender = inf["spec"].get("gender") if inf["family"] == "noun" else None
        return form, inf, root_id, gender
    if model == "compound":
        from .compound import CompoundError, resolve
        try:
            cmp = resolve(d["compound"], lx)
        except CompoundError as e:
            raise NeologismError(f"{where}: {e}") from None
        g = cmp.head_gender if cmp.ctype == "determinative" else None
        cells = cmp.cells(None if g else "m")
        form = cells["NOM.SG"][0]
        pos = "noun" if cmp.ctype == "determinative" else "adj"
        if row["pos"] != pos:
            raise NeologismError(f"{where}: a {cmp.ctype} is a {pos}, the row says {row['pos']}")
        inf = _classify(form, pos, g, where)
        # the classifier's spec must decline to exactly the compound engine's cells
        if pos == "noun":
            same = decline(NounSpec(**inf["spec"]), "handbook") == cells
        else:
            mine = decline_adj(AdjSpec(**inf["spec"]), "handbook")
            same = all(mine[x] == cmp.cells(x) for x in ("m", "f", "n"))
        if not same:
            raise NeologismError(f"{where}: by_shape({form!r}) does not decline like the compound engine's cells")
        root_id = next((lx.entries.get(i, {}).get("root_id") for i in (cmp.second, cmp.first)
                        if lx.entries.get(i, {}).get("root_id")), None)
        return form, inf, root_id, g
    if model == "calque":
        base = d["base"]
        e, r = lx.entries.get(base), lx.specs.get(base)
        if not e or not r or lx.inadmissible(base):
            raise NeologismError(f"{where}: calque base {base!r} is not a usable lexeme"
                                 + (f" ({lx.inadmissible(base)})" if e and lx.inadmissible(base) else ""))
        inf = {"rule": r["rule"], "family": r["family"], "spec": r["spec"]}
        return e["form"], inf, e.get("root_id"), (lx.gender(base) if r["family"] == "noun" else None)
    raise NeologismError(f"{where}: model must be one of {MODELS}, not {model!r}")


def _derivation_roots(row: dict, lx) -> list[str]:
    """The root ids a derivation must list (PLAN: 'roots + suffixes, each by root_id'): a derivative's root, or
    the root families of a compound's members / a calque's base (a neologism member contributes its own)."""
    d, model = row["derivation"], row["model"]
    if model == "derivative":
        return list(d["roots"])
    ids = [d["compound"]["first"], d["compound"]["second"]] if model == "compound" else [d["base"]]
    out = []
    for i in ids:
        e = lx.entries.get(i, {})
        rs = e["neologism"]["derivation"]["roots"] if e.get("neologism") else [e.get("root_id")]
        out += [r for r in rs if r and r not in out]
    return out


def entry(row: dict, lx) -> tuple[dict, dict]:
    """(lexicon entry, inflection spec record) of one row, derived and checked against `lx`."""
    from .export import eval_root
    nid = row.get("neo_id", "")
    if not nid.startswith("pie-neo-"):
        raise NeologismError(f"{nid!r}: a neologism id is pie-neo-<ascii>")
    if nid in lx.entries:
        raise NeologismError(f"{nid}: id already in the lexicon")
    if row.get("model") not in MODELS:
        raise NeologismError(f"{nid}: model must be one of {MODELS}")
    form, inf, root_id, gender = _derive(row, lx)
    roots = _derivation_roots(row, lx)
    d = row["derivation"]
    if sorted(d.get("roots", [])) != sorted(roots):
        raise NeologismError(f"{nid}: derivation must list the roots {roots}")
    for i in d.get("roots", []):
        if lx.entries.get(i, {}).get("kind") != "root":
            raise NeologismError(f"{nid}: {i!r} is not a lexicon root")
        if eval_root(i):
            raise NeologismError(f"{nid}: root family {i} is held out for the benchmark")
    for i in d.get("suffixes", []):
        if lx.entries.get(i, {}).get("kind") != "affix":
            raise NeologismError(f"{nid}: {i!r} is not a lexicon affix")
    if row["model"] != "calque":
        clash = [i for i, e in lx.entries.items() if e.get("form") == form]
        if clash:
            raise NeologismError(f"{nid}: {form} already exists ({clash[0]}): make it a calque of that word")
    if sum(x.acc for x in parse(form)) != 1:
        raise NeologismError(f"{nid}: {form} needs exactly one accent")
    if form not in _head_cell(inf["spec"], inf["family"]) and row["model"] != "calque":
        raise NeologismError(f"{nid}: headword {form} is not the spec's citation cell")
    if row.get("pie") != form:
        raise NeologismError(f"{nid}: pie {row.get('pie')!r} is not the engine's form {form!r}")
    want = {"rule": f"neologism:{row['model']}:{inf['rule']}", "family": inf["family"], "spec": inf["spec"],
            "usable": True, "backtest_cell_accuracy": None, "extra_specs": []}
    if row.get("inflection") is not None and row["inflection"] != want:
        raise NeologismError(f"{nid}: stored inflection differs from the engine's ({want})")
    e = {"id": nid, "kind": "neologism", "form": form, "form_ascii": None, "variants": [], "stems": [],
         "pos": row["pos"], "meaning": [row["gloss"]], "meaning_source": "neologism", "uncertain": [],
         "source": "neologism", "coined": "neologism", "confidence": "neologism", "normalized": [],
         "gender": gender, "etymon_parts": [], "root_id": root_id, "reflexes": {},
         "neologism": {k: row[k] for k in ("english", "derivation", "model", "rationale")}}
    return e, {"id": nid, "form": form, **want}


def read_rows(path: Path = NEOLOGISMS) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip()]


def load_neologisms(lx=None, path: Path = NEOLOGISMS) -> tuple[dict, dict]:
    """(entries, specs) of the neologisms, derived row by row against the base lexicon (a compound may use an
    earlier row). The one loader: with_neologisms and index_neologisms use it."""
    from .realize import Lexicon
    lx = lx or Lexicon.load()
    work = Lexicon(dict(lx.entries), dict(lx.specs), lx.closed, lx.derived, lx.blocked)
    entries, specs = {}, {}
    for row in read_rows(path):
        e, r = entry(row, work)
        work.entries[e["id"]], work.specs[e["id"]] = e, r
        entries[e["id"]], specs[e["id"]] = e, r
    return entries, specs


_WITH: dict = {}


def with_neologisms(lx=None, path: Path = NEOLOGISMS):
    """A new Lexicon: `lx` (default Lexicon.load()) plus the neologisms. Tier 3b only (make_slice --tier3b,
    realize_plans for t3b- batches); the base Lexicon is not changed."""
    from .realize import Lexicon
    lx = lx or Lexicon.load()
    k = (id(lx), str(path), path.stat().st_mtime_ns if path.exists() else None)
    if k not in _WITH:
        entries, specs = load_neologisms(lx, path)
        _WITH[k] = (lx, Lexicon({**lx.entries, **entries}, {**lx.specs, **specs}, lx.closed, lx.derived,
                                lx.blocked))
    return _WITH[k][1]


def neologism_ids(lx) -> list[str]:
    return [i for i, e in lx.entries.items() if e.get("coined") == "neologism"]


def index_neologisms(ix, path: Path = NEOLOGISMS) -> list[str]:
    """Add the neologisms to a validator index, for Tier 3b texts (scripts/realize_plans.py on a t3b- batch,
    scripts/validate_text.py --neologisms). load_index never does this: the Tier 1-3 validator lexicon never
    includes neologisms (PLAN.md). Their analyses carry source engine:neologism:<model>:<shape>."""
    from .validate import Analysis, key
    entries, specs = load_neologisms(path=path)
    for i, e in entries.items():
        if i in ix.lex and ix.lex[i].get("source") != "neologism":
            raise ValueError(f"neologism id already in the index: {i}")
        ix.lex[i] = e
    for i, r in specs.items():
        ix.specs[i] = r
        ix._add_spec(r)
    for i, e in entries.items():
        ix._add(e["form"], Analysis(i, e.get("root_id"), "LEMMA", "neologism-lexicon", status="primary"))
        ix.lemma_forms[key(e["form"], "generic-H")].append(i)
    return sorted(entries)


def fill(path: Path = NEOLOGISMS) -> int:
    """Write each row's engine-derived `pie` and `inflection` (rows are authored with the derivation only).
    `uv run python -I -m pie.neologism --fill`; a plain run checks the file and prints the table."""
    from .realize import Lexicon
    lx = Lexicon.load()
    work = Lexicon(dict(lx.entries), dict(lx.specs), lx.closed, lx.derived, lx.blocked)
    out = []
    for row in read_rows(path):
        row = {**row, "pie": None, "inflection": None}
        form, inf, _, _ = _derive(row, work)
        row["pie"] = form
        row["pos"] = row.get("pos") or inf["family"]          # a calque takes its base's part of speech
        row["inflection"] = {"rule": f"neologism:{row['model']}:{inf['rule']}", "family": inf["family"],
                             "spec": inf["spec"], "usable": True, "backtest_cell_accuracy": None, "extra_specs": []}
        e, r = entry(row, work)
        work.entries[e["id"]], work.specs[e["id"]] = e, r
        out.append(row)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), "utf-8")
    return len(out)


if __name__ == "__main__":
    import sys
    if "--fill" in sys.argv:
        print(f"filled {fill()} rows")
    ents, _ = load_neologisms()
    for i, e in ents.items():
        print(f"{i:28} {e['form']:22} {e['pos']:5} {e['neologism']['model']:10} {e['meaning'][0]}")
    print(len(ents), "neologisms")
