#!/usr/bin/env python3
"""Stage C-S measures, recomputed from the committed claims, verdicts and the (gitignored) keys.

Primary (docs/research/8c-preregistration.md, "Measures"): accepted claims per real bundle vs per decoy
bundle, one-sided permutation test over bundle labels (10,000 permutations, seed 0); success if r >= 2·d
and p < 0.05 (if d = 0: r > 0 and p < 0.05). Computed for (i) Celtic-pivot bundles (a claim counts only
with a contributing Celtic anchor) and (ii) all bundles. Claims of primary and follow-up readers count
together; a claim found by both (same anchor set) counts once; the pilot slabs count their official
reader only (X/H pilot readers are reported separately). A claim citing k bundles adds 1/k to each.
Secondary: the same for accepted + weak; reviewer acceptance rate of real- vs decoy-anchored claims;
confidence calibration. Exploratory (not preregistered): near-miss flags per real vs decoy bundle,
primary readers only. Search leads never enter the measures; they are tabulated separately.

    uv run python -I scripts/stagecs_measures.py --out data/research/8c/stageCS/measures.json
"""
import argparse, collections, glob, json, math, os, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ROOT / "data/audits/keys"
CS = ROOT / "data/research/8c/stageCS"
CELTIC = {"sga", "sga-gl", "mga", "cy", "ga-early"}


def review_dir(keyfile):
    b = os.path.basename(keyfile)
    if b == "8c-stageCS-claims-key.json":
        return "review"
    return "review-" + b.split("stageCS-")[1].split("-claims")[0]


def load_slabs():
    slabs = {}
    for f in glob.glob(str(KEYS / "8c-stageCS*-key.json")):
        if "claims" in f or "leads" in f:
            continue
        slabs.update(json.load(open(f))["slabs"])
    return slabs


def read_slabs():
    """Slabs with a done line from a counting reader, and the near-miss flags of primary readers."""
    read, flags = set(), collections.Counter()
    for f in glob.glob(str(CS / "claims/RS*.jsonl")):
        reader = Path(f).stem
        for line in open(f, encoding="utf-8"):
            if not line.strip():
                continue
            d = json.loads(line)
            if "done" in d and not reader.endswith(("X", "H")):
                read.add(d["slab"])
            if "near_miss" in d and not reader.endswith(("F", "X", "H")):
                for b in d["near_miss"].get("bundles", []):
                    flags[(d["slab"], b)] += 1
    return read, flags


def load_claims(slabs):
    grades = {}
    for f in glob.glob(str(CS / "review*/verdicts-*.jsonl")):
        if "-leads" in f:
            continue
        rd = os.path.basename(os.path.dirname(f))
        for line in open(f, encoding="utf-8"):
            if line.strip():
                v = json.loads(line)
                grades[(rd, v["claim"])] = v["grade"]
    claims, seen, excluded = [], set(), []
    for kf in sorted(glob.glob(str(KEYS / "8c-stageCS*claims-key.json"))):
        rd = review_dir(kf)
        for cid, info in json.load(open(kf)).items():
            if not isinstance(info, dict) or "slab" not in info:
                continue
            c = dict(info, id=f"{rd}/{cid}", grade=grades.get((rd, cid)))
            if c["reader"].endswith(("X", "H")):
                excluded.append(c)
                continue
            sig = (c["slab"], frozenset(c.get("anchors", [])))
            if sig in seen:
                c["duplicate"] = True
                excluded.append(c)
                continue
            seen.add(sig)
            kinds = {slabs[c["slab"]][b]["kind"] for b in c["bundles"] if b in slabs.get(c["slab"], {})}
            c["kind"] = "decoy" if kinds == {"decoy"} else ("mixed" if "decoy" in kinds else "real")
            c["celtic_anchor"] = any(a.split(":")[0] in CELTIC for a in c.get("anchors", []))
            claims.append(c)
    return claims, excluded


def perm_test(scores, labels, n=10000, seed=0):
    """One-sided: P(mean(real) - mean(decoy) >= observed) under label permutation."""
    real = [s for s, l in zip(scores, labels) if l]
    decoy = [s for s, l in zip(scores, labels) if not l]
    if not real or not decoy:
        return None
    obs = sum(real) / len(real) - sum(decoy) / len(decoy)
    rng = random.Random(seed)
    lab = list(labels)
    nr, total, ge = len(real), sum(scores), 0
    for _ in range(n):
        rng.shuffle(lab)
        sr = sum(s for s, l in zip(scores, lab) if l)
        if sr / nr - (total - sr) / (len(scores) - nr) >= obs - 1e-12:
            ge += 1
    return (ge + 1) / (n + 1)


def rate_ratio_ci(a, n1, c, n2):
    """Poisson rate ratio with a log-normal 95% interval (0.5 added to zero cells)."""
    a2, c2 = (a or 0.5), (c or 0.5)
    rr = (a2 / n1) / (c2 / n2)
    se = math.sqrt(1 / a2 + 1 / c2)
    return rr, rr * math.exp(-1.96 * se), rr * math.exp(1.96 * se)


def measure(bundles, slabs, claims, grades_ok, celtic_only=False):
    score = collections.Counter()
    for c in claims:
        if c["grade"] not in grades_ok or (celtic_only and not c["celtic_anchor"]):
            continue
        for b in c["bundles"]:
            score[(c["slab"], b)] += 1 / len(c["bundles"])
    keys = sorted(bundles)
    sc = [score[k] for k in keys]
    lab = [slabs[s][b]["kind"] == "real" for s, b in keys]
    nr, nd = sum(lab), len(lab) - sum(lab)
    sr = sum(x for x, l in zip(sc, lab) if l)
    sd = sum(x for x, l in zip(sc, lab) if not l)
    r, d = sr / nr if nr else 0, sd / nd if nd else 0
    p = perm_test(sc, lab)
    success = (r >= 2 * d and p is not None and p < 0.05) if d else (r > 0 and p is not None and p < 0.05)
    rr = rate_ratio_ci(sr, nr, sd, nd)
    return {"real_bundles": nr, "decoy_bundles": nd, "real_weight": round(sr, 3), "decoy_weight": round(sd, 3),
            "r": r, "d": d, "rate_ratio": rr[0], "rr_95ci": [rr[1], rr[2]], "perm_p": p, "success": success}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    slabs = load_slabs()
    read, flags = read_slabs()
    read &= set(slabs)
    bundles = {(s, b) for s in read for b in slabs[s]}
    celtic = {(s, b) for s, b in bundles if slabs[s][b].get("pivot_group") == "celtic"}
    claims, excluded = load_claims(slabs)
    claims = [c for c in claims if c["slab"] in read]
    out = {"slabs_read": len(read),
           "bundles_read": dict(collections.Counter(slabs[s][b]["kind"] for s, b in bundles)),
           "celtic_bundles_read": dict(collections.Counter(slabs[s][b]["kind"] for s, b in celtic)),
           "claims_counted": len(claims),
           "claims_by_kind_grade": {f"{k}/{g}": n for (k, g), n in
                                    sorted(collections.Counter((c["kind"], c["grade"]) for c in claims).items())},
           "excluded_claims": [{"id": c["id"], "reader": c["reader"], "why": "duplicate" if c.get("duplicate") else "pilot reader"} for c in excluded],
           "ungraded": [c["id"] for c in claims if c["grade"] is None]}
    out["primary_ii_all"] = measure(bundles, slabs, claims, {"accepted"})
    out["primary_i_celtic"] = measure(celtic, slabs, claims, {"accepted"}, celtic_only=True)
    out["secondary_ii_accepted_weak"] = measure(bundles, slabs, claims, {"accepted", "weak"})
    out["secondary_i_accepted_weak"] = measure(celtic, slabs, claims, {"accepted", "weak"}, celtic_only=True)
    acc = collections.defaultdict(collections.Counter)
    for c in claims:
        acc[c["kind"]][c["grade"]] += 1
    out["acceptance_by_kind"] = {k: dict(v) for k, v in acc.items()}
    cal = collections.defaultdict(collections.Counter)
    for c in claims:
        cal[c.get("confidence")][c["grade"]] += 1
    out["confidence_calibration"] = {k: dict(v) for k, v in cal.items()}
    out["accepted_claims"] = [{k: c.get(k) for k in ("id", "reader", "slab", "bundles", "kind", "confidence", "recalled", "anchors")}
                              for c in claims if c["grade"] == "accepted"]
    # exploratory: near-miss flags by bundle kind (primary readers only; the pilot readers had no near-miss
    # line type, so their slabs are left out of the denominator)
    pilot = set()
    for r in ("RS001", "RS002", "RS003", "RS009"):
        for line in open(CS / f"claims/{r}.jsonl", encoding="utf-8"):
            if line.strip() and "done" in json.loads(line):
                pilot.add(json.loads(line)["slab"])
    nm_bundles = {(s, b) for s, b in bundles if s not in pilot}
    nm = {"real": 0, "decoy": 0}
    for (s, b), n in flags.items():
        if (s, b) in nm_bundles:
            nm[slabs[s][b]["kind"]] += 1
    nb = dict(collections.Counter(slabs[s][b]["kind"] for s, b in nm_bundles))
    rr = rate_ratio_ci(nm["real"], nb["real"], nm["decoy"], nb["decoy"])
    keys = sorted(nm_bundles)
    out["exploratory_near_miss"] = {"slabs": len(read - pilot), "bundles": nb,
                                    "flagged_real": nm["real"], "flagged_decoy": nm["decoy"],
                                    "share_real": nm["real"] / nb["real"], "share_decoy": nm["decoy"] / nb["decoy"],
                                    "rate_ratio": rr[0], "rr_95ci": [rr[1], rr[2]],
                                    "perm_p": perm_test([1 if flags[k] else 0 for k in keys],
                                                        [slabs[s][b]["kind"] == "real" for s, b in keys])}
    # search leads: separate track
    lead_grades = collections.Counter()
    accepted_leads = []
    for f in glob.glob(str(CS / "review*-leads/verdicts-*.jsonl")):
        rd = os.path.basename(os.path.dirname(f)).replace("-leads", "")
        key = json.load(open(KEYS / f"8c-stageCS-{rd.replace('review-', '')}-leads-key.json")) \
            if (KEYS / f"8c-stageCS-{rd.replace('review-', '')}-leads-key.json").exists() else {}
        for line in open(f, encoding="utf-8"):
            if line.strip():
                v = json.loads(line)
                lead_grades[v["grade"]] += 1
                if v["grade"] == "accepted":
                    k = key.get(v["lead"], {})
                    accepted_leads.append({"review": rd, "lead": v["lead"], "reader": k.get("reader"),
                                           "recalled": k.get("recalled"), "known": v.get("known")})
    out["search_leads"] = {"grades": dict(lead_grades), "accepted": accepted_leads}
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
