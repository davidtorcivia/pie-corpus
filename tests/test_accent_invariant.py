"""Global accent invariant (fix/accent): the primary form of every cell of every usable lexeme, and of every
closed-class table, carries exactly one accent mark.

The accent manifest data/morph/accent_unresolved.json (read by the code too: pie.realize.accent_manifest) keeps
three categories apart, and nothing moves between them to satisfy this test:
  unresolved_lexical_accent: missing information (the headword has no accent); the lexemes stay usable and are
      flagged accent: unresolved downstream. A cell passes only with no accent at all on an accentless headword.
  representation_exceptions: the vocatives the initial vocative accent leaves unmarked (ph₂ter). Frozen as exact
      (lex_id, gender, cell, primary form) combinations, so an unrelated accent loss cannot hide in one.
  INHERENTLY_ACCENTLESS (below): supported unaccented clitics only, each with its reason. Nothing goes here only
      because a handbook prints it without an accent, and no vocative goes here.
The defect groups (double_accent_source, closed_pending) are listed, not excepted. The test fails when a new case
appears and when a listed one is fixed (remove it from the manifest then), so the lists only shrink.
"""

import json
from pathlib import Path

import pytest

from pie.phon import parse
from pie.realize import ACCENT_MANIFEST, accent_manifest

ROOT = Path(__file__).resolve().parent.parent
KNOWN = json.loads(ACCENT_MANIFEST.read_text("utf-8"))

# closed_class.json paths (cell or particle) that are accentless by nature
_ENCL_PRON = ("unstressed (enclitic) personal pronoun paradigm beside the stressed one: Fortson §7.2; the unstressed "
              "personal pronouns are sentential clitics, §8.25")
INHERENTLY_ACCENTLESS = {
    **{f"personal/{p}/{c}": _ENCL_PRON for p, cs in {
        "1": ("ACC.SG.ENCL", "GEN.SG.ENCL", "DAT.SG.ENCL", "ACC.PL.ENCL", "GEN.PL.ENCL", "DAT.PL.ENCL", "ACC.DU.ENCL"),
        "2": ("ACC.SG.ENCL", "GEN.SG.ENCL", "DAT.SG.ENCL", "ACC.PL.ENCL", "GEN.PL.ENCL", "DAT.PL.ENCL", "ACC.DU.ENCL"),
        "refl": ("ACC.SG.ENCL", "DAT.SG.ENCL", "GEN.SG.ENCL")}.items() for c in cs},
    "particles/-kʷe": "sentence-connective clitic *kʷe 'and' (Fortson §8.24, §7.27)",
    "particles/-wē": "sentence-connective clitic *u̯ē 'or' (Fortson §8.24, §7.27)",
    "particles/-ge": "word-level emphatic clitic, postpositive and unstressed (Fortson §8.23)",
}


def n_acc(form: str) -> int:
    return sum(s.acc for s in parse(form.replace("-", "")))


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    return Lexicon.load()


@pytest.fixture(scope="module")
def hits(lx) -> dict[str, list[tuple[str, str, int]]]:
    hits: dict[str, list] = {}
    for lid, r in lx.specs.items():
        if not r.get("usable"):
            continue
        for g in (["m", "f", "n"] if r["family"] == "adj" else [None]):
            for k, v in lx.cells(lid, g).items():
                if v and n_acc(v[0]) != 1:
                    hits.setdefault(lid, []).append((f"{g or ''}:{k}", v[0], n_acc(v[0])))
    return hits


def test_every_primary_lexeme_cell_has_one_accent(lx, hits):
    lemma = {i for f in KNOWN["unresolved_lexical_accent"]["by_family"].values() for i in f["ids"]}
    exc = {(c["lex_id"], c["gender"] or "", c["cell"], c["form"]) for c in KNOWN["representation_exceptions"]["cells"]}
    multi = set(KNOWN["double_accent_source"]["ids"])
    new, seen_exc = [], set()
    for lid, hs in hits.items():
        for cell, form, n in hs:
            g, c = cell.split(":", 1)
            if (lid, g, c, form) in exc and n == 0:
                seen_exc.add((lid, g, c, form))
                continue
            ok = (lid in lemma and n == 0 and n_acc(lx.entries[lid]["form"].strip("*-")) == 0) \
                or (lid in multi and n > 1)
            if not ok:
                new.append((lid, cell, form, n))
    assert not new, f"{len(new)} new cells without exactly one accent: {new[:20]}"
    fixed = sorted((lemma | multi) - set(hits))
    assert not fixed, f"listed in data/morph/accent_unresolved.json but now clean (remove them): {fixed}"
    gone = sorted(exc - seen_exc)
    assert not gone, f"representation exceptions no longer generated as listed (update the manifest): {gone[:10]}"


def test_representation_exceptions_are_frozen_vocatives():
    rec = KNOWN["representation_exceptions"]
    assert len(rec["cells"]) == 111 and rec["lexemes"] == len(rec["ids"]) == 30
    assert {c["lex_id"] for c in rec["cells"]} == set(rec["ids"])
    assert all(c["cell"].startswith("VOC.") and n_acc(c["form"]) == 0 for c in rec["cells"])
    # the three categories do not overlap
    lemma = accent_manifest()["unresolved_ids"]
    assert not lemma & set(rec["ids"]) and not lemma & set(KNOWN["double_accent_source"]["ids"])


def test_known_defect_counts_do_not_grow(hits):
    """The family counts in the manifest are the ones the report gives; they may only go down."""
    for fam, rec in KNOWN["unresolved_lexical_accent"]["by_family"].items():
        assert sum(len(hits.get(i, [])) for i in rec["ids"]) <= rec["cells"], fam
        assert rec["lexemes"] == len(rec["ids"]), fam
    assert sum(r["cells"] for r in KNOWN["unresolved_lexical_accent"]["by_family"].values()) \
        == KNOWN["unresolved_lexical_accent"]["cells"]


def _closed_primaries():
    c = json.loads((ROOT / "data/morph/closed_class.json").read_text("utf-8"))

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if not k.startswith("_"):
                    yield from walk(v, path + [k])
        elif isinstance(node, list) and node and isinstance(node[0], str):
            yield "/".join(path), node[0]

    for k, v in c.items():
        if k.startswith("_") or k == "particles":
            continue
        yield from walk(v, [k])
    for form in c["particles"]:
        yield f"particles/{form}", form


def test_every_closed_class_primary_has_one_accent():
    pending = KNOWN["closed_pending"]["ids"]
    bad = [(p, f) for p, f in _closed_primaries()
           if n_acc(f) != 1 and p not in INHERENTLY_ACCENTLESS and p not in pending]
    assert not bad, bad
    # the exceptions and the pending list name real, still-accentless entries
    prim = dict(_closed_primaries())
    for p in [*INHERENTLY_ACCENTLESS, *pending]:
        assert p in prim and n_acc(prim[p]) == 0, p


def test_inherently_accentless_list_is_enclitics_only():
    assert all(p.endswith(".ENCL") or p.startswith("particles/-") for p in INHERENTLY_ACCENTLESS)
