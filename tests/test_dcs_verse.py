"""DCS sentence locus ('AVŚ, 8, 6.s48' = 48th sentence of the hymn) → verse
citation ('AVŚ 8.6.23'). Fixtures are invented headers; the real-data checks
(skipped without the DCS dump) use loci only, no corpus text."""

import pytest

from pie import formula_search_multi as fm


def _chapter(rows):
    """rows: (sent_id, counter, subcounter, syllable-ish text) → CoNLL-U headers + one token each."""
    out = ["## chapter: AVŚ, 1, 1"]
    for sid, c, sc, text in rows:
        out.append(f"# text = {text}")
        out.append(f"# sent_id = {sid}")
        if c is not None:
            out.append(f"# sent_counter = {c}")
            out.append(f"# sent_subcounter = {'' if sc is None else sc}")
        out.append("1\tdevāḥ\tdeva\tNOUN\t_\tCase=Nom\t0\troot\t_\t_")
        out.append("")
    return "\n".join(out) + "\n"


HALF = "ta ta ta ta ta ta ta ta ta ta ta ta ta ta ta ta"      # 16 syllables, an anuṣṭubh half-verse


def test_counter_and_bracketed_lines():
    text = _chapter([
        ("100", 1, 1, HALF), ("101", 1, 2, HALF),
        ("102", 2, 1, HALF), ("103_1", None, None, "ta ta ta ta ta ta ta ta"), ("103_2", None, None, "ta ta ta ta ta ta ta ta"),
        ("104", 3, 1, HALF), ("105", 3, 2, HALF),
    ])
    ch, sents = fm.dcs_sentence_heads(text)
    assert ch == "AVŚ, 1, 1" and [s["line_id"] for s in sents] == [100, 101, 102, 103, 103, 104, 105]
    recs = fm.dcs_chapter_citations(ch, sents)
    assert [(r["dcs"], r["verse"], r["status"]) for r in recs] == [
        ("AVŚ, 1, 1.s1", "AVŚ 1.1.1", "counter"), ("AVŚ, 1, 1.s2", "AVŚ 1.1.1", "counter"),
        ("AVŚ, 1, 1.s3", "AVŚ 1.1.2", "counter"), ("AVŚ, 1, 1.s4", "AVŚ 1.1.2", "bracketed"),
        ("AVŚ, 1, 1.s5", "AVŚ 1.1.2", "bracketed"), ("AVŚ, 1, 1.s6", "AVŚ 1.1.3", "counter"),
        ("AVŚ, 1, 1.s7", "AVŚ 1.1.3", "counter")]
    assert [r["cite"] for r in recs] == ["AVŚ 1.1.1ab", "AVŚ 1.1.1cd", "AVŚ 1.1.2ab", "AVŚ 1.1.2cd",
                                         "AVŚ 1.1.2cd", "AVŚ 1.1.3ab", "AVŚ 1.1.3cd"]
    assert recs[3]["sent_id"] == "103_1"


def test_no_pada_for_unequal_or_three_line_verses_and_empty_subcounter():
    text = _chapter([
        ("10", 1, 1, HALF), ("11", 1, 2, "ta ta ta ta ta ta ta ta"),       # gāyatrī-like 16 + 8: no letters
        ("12", 2, None, HALF), ("13", 2, None, HALF), ("14", 2, None, HALF),  # no subcounter: rank in verse
    ])
    ch, sents = fm.dcs_sentence_heads(text)
    recs = fm.dcs_chapter_citations(ch, sents)
    assert [r["cite"] for r in recs] == ["AVŚ 1.1.1", "AVŚ 1.1.1", "AVŚ 1.1.2", "AVŚ 1.1.2", "AVŚ 1.1.2"]
    assert [r["line"] for r in recs] == [1, 2, 1, 2, 3]


def test_unnumbered_chapter_is_inferred_from_stanza_count():
    rows = [(f"{200 + i}_1", None, None, HALF) for i in range(6)]
    ch, sents = fm.dcs_sentence_heads(_chapter(rows))
    recs = fm.dcs_chapter_citations(ch, sents, {(1, 1): 3})
    assert [r["verse"] for r in recs] == ["AVŚ 1.1.1"] * 2 + ["AVŚ 1.1.2"] * 2 + ["AVŚ 1.1.3"] * 2
    assert {r["status"] for r in recs} == {"inferred"} and all(r["pada"] == "" for r in recs)


def test_load_dcs_exposes_verse_units(tmp_path):
    dd = tmp_path / fm.DCS_DIR / "Atharvaveda (Śaunaka)"
    dd.mkdir(parents=True)
    (dd / "x-0000-AVŚ, 1, 1-1.conllu").write_text(_chapter([("100", 1, 1, HALF), ("101", 1, 2, HALF)]), "utf-8")
    toks = fm.load_dcs(("Atharvaveda (Śaunaka)",), root=tmp_path)
    assert [t.locus for t in toks] == ["AVŚ, 1, 1.s1", "AVŚ, 1, 1.s2"]       # locus unchanged (packet ids)
    assert [(t.units["verse"], t.units["cite"], t.units["sent_id"], t.units["verse_status"]) for t in toks] == [
        ("AVŚ 1.1.1", "AVŚ 1.1.1ab", "100", "counter"), ("AVŚ 1.1.1", "AVŚ 1.1.1cd", "101", "counter")]


_REAL = (fm.ROOT / fm.DCS_DIR / "Atharvaveda (Śaunaka)").is_dir()


@pytest.mark.skipif(not _REAL, reason="DCS dump not present")
@pytest.mark.parametrize("locus,verse", [
    # the five pairs found by the literature check (docs/research/literature-review.md)
    ("AVŚ, 8, 6.s48", "AVŚ 8.6.23"), ("AVŚ, 13, 1.s47", "AVŚ 13.1.24"), ("AVŚ, 11, 10.s18", "AVŚ 11.10.8"),
    ("AVŚ, 9, 1.s2", "AVŚ 9.1.1"), ("AVŚ, 8, 3.s29", "AVŚ 8.3.15"),
    # checked against Whitney–Lanman's translation of the mapped stanza
    ("AVŚ, 4, 20.s16", "AVŚ 4.20.7"), ("AVŚ, 1, 34.s13", "AVŚ 1.34.4"), ("AVŚ, 12, 1.s11", "AVŚ 12.1.6"),
    ("AVŚ, 6, 96.s2", "AVŚ 6.96.2"), ("AVŚ, 17, 1.s116", "AVŚ 17.1.25"), ("AVŚ 8, 6.s48 (w1/2)", "AVŚ 8.6.23"),
])
def test_real_dcs_loci(locus, verse):
    cite = fm.dcs_verse_citation(locus, inferred=True)
    assert cite is not None and cite.rstrip("abcde") == verse


@pytest.mark.skipif(not _REAL, reason="DCS dump not present")
def test_real_dcs_status_and_pada():
    idx = fm.dcs_citation_index()
    assert idx["AVŚ, 8, 6.s48"]["status"] == "counter" and idx["AVŚ, 8, 6.s48"]["sent_id"] == "648035"
    assert fm.dcs_verse_citation("AVŚ, 9, 1.s2") == "AVŚ 9.1.1cd"
    assert idx["AVŚ, 11, 10.s18"]["status"] == "inferred"
    assert fm.dcs_verse_citation("AVŚ, 11, 10.s18") is None                  # inferred only on request
