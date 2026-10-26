"""Tier 3 release policy: current passing gates AND content-bound review approval.

Candidate artifacts are retained even when ineligible. This module is the shared
admission decision for export and publication tooling; realization never approves
its own output. See docs/audits/eng-01-release-migration.md.
"""
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def release_metadata(root: Path, batch: str, *, status: str = "pending",
                     evidence: list[str] | None = None, rationale: str = "Awaiting review.") -> dict:
    """Bind a review decision to candidate records, plans, and the gate report."""
    return {
        "schema_version": 1, "batch": batch,
        "sha256": {name: sha256(root / path) for name, path in artifact_paths(batch).items()},
        "review": {"required": True, "status": status,
                   "evidence": evidence or [], "rationale": rationale},
    }


def artifact_paths(batch: str) -> dict[str, str]:
    return {"records": f"corpus/tier3/{batch}.jsonl",
            "plans": f"data/generation/plans/{batch}.jsonl",
            "gate_report": f"data/generation/batches/{batch}.json"}


def batch_eligibility(root: Path, batch: str, *, experimental: bool = False) -> dict:
    """Fail closed on absent, stale, or malformed evidence; report all reasons.

    Experimental admission changes only the decision, never the underlying facts.
    """
    reasons = []
    gate = "unknown"
    review_status = "unknown"
    paths = artifact_paths(batch)
    try:
        report = json.loads((root / paths["gate_report"]).read_text("utf-8"))
        gates = report["gates"]
        if (not isinstance(gates, dict) or not gates
                or any(type(v) is not bool for v in gates.values())
                or report["gate"] not in ("PASS", "FAIL")
                or (report["gate"] == "PASS") != all(gates.values())):
            raise ValueError("inconsistent gates")
        gate = report["gate"]
        if gate == "FAIL":
            reasons.append("gate FAIL: " + ", ".join(k for k, v in gates.items() if not v))
    except (OSError, ValueError, KeyError, TypeError):
        reasons.append("missing or malformed gate report")
    try:
        meta = json.loads((root / f"data/generation/releases/{batch}.json").read_text("utf-8"))
        review = meta["review"]
        if (meta["schema_version"] != 1 or meta["batch"] != batch
                or review["required"] is not True
                or review["status"] not in ("pending", "approved", "rejected")
                or not isinstance(review["rationale"], str) or not review["rationale"].strip()
                or not isinstance(review["evidence"], list)
                or any(not isinstance(e, str) or not e.strip() for e in review["evidence"])
                or (review["status"] == "approved" and not review["evidence"])):
            raise ValueError("invalid review")
        review_status = review["status"]
        for name, path in paths.items():
            if meta["sha256"][name] != sha256(root / path):
                reasons.append(f"stale {name} evidence")
        if review_status != "approved":
            reasons.append(f"required review {review_status}")
    except (OSError, ValueError, KeyError, TypeError):
        reasons.append("missing or malformed release metadata")
    return {"batch": batch, "gate": gate, "review": review_status,
            "eligible": not reasons, "admitted": not reasons or experimental,
            "experimental": experimental, "reasons": reasons}
