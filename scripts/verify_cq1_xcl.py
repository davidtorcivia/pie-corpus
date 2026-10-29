"""Corpus-quality batch 1, Classical Armenian: compare the production DMHP loader against a snapshot
taken before the batch and account for every changed token.

  uv run python -I scripts/verify_cq1_xcl.py snapshot BEFORE.jsonl   (before the edits)
  uv run python -I scripts/verify_cq1_xcl.py verify BEFORE.jsonl     (after: writes the metrics/diff)

A snapshot row is [locus, surface, lemma, content, pos, cunit, DMHP lemma, DMHP POS, ids] for every
token of scripts/build_8c_stageC.dmhp_tokens with the Stage C table ids (empty for non-content).
verify asserts that no surface, coordinate, sentence key or DMHP field changed and that each lemma / content /
id change is an exact reading (cq1-readings-xcl.json), a pie.cq1_xcl rule, the name non-content rule,
the reviewed content word, or a z-cq1-xcl.json mapping row; it writes the counts per rule and every
changed token to data/research/8c/corpus-quality/error-verdicts-cq1-armenian-{metrics,token-diff}.json.
Never reads review slabs, claims or the search index.
"""
import collections
import importlib.util
import json
import sys
from pathlib import Path

from pie import arm_toch_alb_mapping as am, cq1_mapping, cq1_xcl

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/research/8c/corpus-quality"
OVR = ROOT / "data/research/formulas/mapping-overrides/z-cq1-xcl.json"


def _stage_c():
    spec = importlib.util.spec_from_file_location("cq1_xcl_stage_c", ROOT / "scripts/build_8c_stageC.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_SC = None


def rows():
    global _SC
    sc = _SC = _SC or _stage_c()
    toks, raw = sc.dmhp_tokens(ROOT), am.dmhp_tokens(ROOT)
    assert len(toks) == len(raw)
    table = sc._table("xcl", ROOT)
    return [[t.locus, t.surface, t.lemma, t.content, t.pos, t.units["cunit"], r.lemma, r.pos,
             sorted(table.get(t.lemma, ())) if t.content else []] for t, r in zip(toks, raw)]


def snapshot(path):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows():
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def classify(b, a, readings, mapping_lemmas):
    locus, surface = b[0], b[1]
    if (b[2], b[3]) == (a[2], a[3]):
        assert a[2] in mapping_lemmas, ("id change outside the mapping rows", b, a)
        return f"mapping-row:{a[2]}"
    r = readings.get((locus, surface, b[2]))
    if r and r["lemma"] == a[2]:
        return "exact-reading"
    hit = cq1_xcl.rule_for("xcl", b[2], surface, locus)
    if hit and hit[1] == a[2]:
        assert a[3] == (b[3] and not cq1_xcl.noncontent("xcl", a[2], surface, locus)), (b, a)
        return hit[0]
    if b[2] == a[2] and b[3] and not a[3] and a[2].endswith(" (name)"):
        return "name-noncontent"
    if b[2] == a[2] and a[3] and not b[3] and (locus.split(" ", 1)[0], locus.split(" ", 1)[1]) in am.DMHP_CONTENT_REVIEWED:
        return "content-reviewed"
    raise AssertionError(("unexplained change", b, a))


def verify(path):
    before = [json.loads(l) for l in open(path, encoding="utf-8")]
    after = rows()
    assert len(before) == len(after), (len(before), len(after))
    readings = {(r["locus"], r["surface"], r["old"]): r for r in cq1_mapping.reading_rows() if r["corpus"] == "xcl"}
    mapping_lemmas = {r["lemma"] for r in json.loads(OVR.read_text("utf-8"))["lemma"]}
    counts, diff = collections.Counter(), []
    for b, a in zip(before, after):
        assert [b[0], b[1], b[5], b[6], b[7]] == [a[0], a[1], a[5], a[6], a[7]], (b, a)
        if b == a:
            continue
        rule = classify(b, a, readings, mapping_lemmas)
        counts[rule] += 1
        diff.append(dict(rule=rule, locus=b[0], surface=b[1], dmhp_lemma=b[6], dmhp_pos=b[7],
                         before=dict(lemma=b[2], content=b[3], lex_id=b[8]),
                         after=dict(lemma=a[2], content=a[3], lex_id=a[8])))
    seen = {(d["locus"], d["surface"]) for d in diff if d["rule"] == "exact-reading"}
    missing = [k for k in readings if (k[0], k[1]) not in seen]
    assert not missing, ("exact readings that changed nothing", missing)
    by_rule = collections.defaultdict(collections.Counter)
    for d in diff:
        by_rule[d["rule"]][f'{d["before"]["lemma"]} -> {d["after"]["lemma"]}'] += 1
    windows = {}
    for name, rs in (("before", before), ("after", after)):
        n = collections.Counter(r[5] for r in rs if r[3])
        windows[name] = {k: (len(_SC.SB.split_windows(v, _SC.SB.MAX_WORDS)) if v > _SC.SB.MAX_WORDS else 1)
                         for k, v in n.items()}
    keys = {r[5] for r in after}
    metrics = dict(
        tokens=len(after), changed=len(diff),
        stage_c_windows=dict(
            before=sum(windows["before"].get(k, 1) for k in keys), after=sum(windows["after"].get(k, 1) for k in keys),
            sentences_with_window_count_change=sum(windows["before"].get(k, 1) != windows["after"].get(k, 1) for k in keys),
            note="content-word windows of Stage C units (build_8c_stageB.split_windows, MAX_WORDS); a changed count "
                 "re-labels that sentence's (wJ/n) window loci"),
        content_before=sum(r[3] for r in before), content_after=sum(r[3] for r in after),
        mapped_before=sum(bool(r[8]) for r in before), mapped_after=sum(bool(r[8]) for r in after),
        surface_changes=0, coordinate_changes=0, sentence_key_changes=0,
        by_rule=dict(sorted(counts.items(), key=lambda x: -x[1])),
        transitions={k: dict(v.most_common()) for k, v in sorted(by_rule.items())},
        exact_readings=len(readings),
        command="UV_CACHE_DIR=/tmp/pie-uv-cache uv run python -I scripts/verify_cq1_xcl.py verify <before.jsonl>",
    )
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "error-verdicts-cq1-armenian-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1) + "\n", "utf-8")
    (DEST / "error-verdicts-cq1-armenian-token-diff.json").write_text(
        json.dumps(diff, ensure_ascii=False, indent=0) + "\n", "utf-8")
    print(json.dumps({k: metrics[k] for k in ("tokens", "changed", "content_before", "content_after",
                                              "mapped_before", "mapped_after", "stage_c_windows")}))
    print(json.dumps(metrics["by_rule"], ensure_ascii=False))


if __name__ == "__main__":
    {"snapshot": snapshot, "verify": verify}[sys.argv[1]](sys.argv[2])
