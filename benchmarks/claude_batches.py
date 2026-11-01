"""Claude contestants (the pie-bench subagent, benchmarks/README.md): build each batch's prompt, and file the
answers from each run transcript's own submit_answers calls (the inbox copy is a backup) into
benchmarks/results/claude-<model>-<effort>/answers.jsonl, with the blindness audit of each run's transcript.

    python3 -I benchmarks/claude_batches.py prompt BATCH            # the prompt text for one batch
    python3 -I benchmarks/claude_batches.py collect RUN TRANSCRIPT... # RUN = claude-haiku-low; audit + file answers

A run is accepted only if its transcript's tool calls are submit_answers (and the hand-back) alone, and it
answered every item of the batch.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {"mcp__pie_bench__get_batch", "mcp__pie_bench__submit_answers", "SubagentHandback", "StructuredOutput"}


def items():
    return {x["id"]: x for x in map(json.loads, (HERE / "items.jsonl").read_text("utf-8").splitlines())}


def batches():
    return {b["batch"]: b for b in json.loads((HERE / "batches.json").read_text())}


def prompt(batch: str, run: str) -> str:
    it, b = items(), batches()[batch]
    body = [{"id": i, **({"system": it[i]["system"]} if it[i]["system"] else {}), "instruction": it[i]["instruction"]}
            for i in b["items"]]
    return f"Batch {run}--{batch}. Items:\n{json.dumps(body, ensure_ascii=False, indent=1)}"


def audit(transcript: Path) -> tuple[list[str], dict, dict]:
    """(tool calls, usage, answers): the answers are read from the transcript's own submit_answers calls, so a
    contestant that garbles the batch id when submitting (Haiku high did, twice) is still filed correctly."""
    calls, usage, answers = [], {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0}, {}
    seen = set()
    for line in transcript.read_text("utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = e.get("message")
        if not isinstance(m, dict):
            continue
        for blk in m.get("content") or []:
            if isinstance(blk, dict) and blk.get("type") == "tool_use" and blk.get("id") not in seen:
                seen.add(blk.get("id"))
                calls.append(blk["name"])
                if blk["name"].endswith("submit_answers"):
                    for x in (blk.get("input") or {}).get("answers") or []:
                        answers.setdefault(str(x.get("id")), str(x.get("answer", "")))
        u, mid = m.get("usage"), m.get("id")
        if u and mid not in seen:              # one usage per API message (a message is logged once per block)
            seen.add(mid)
            for k, src in (("input", "input_tokens"), ("cache_creation", "cache_creation_input_tokens"),
                           ("cache_read", "cache_read_input_tokens"), ("output", "output_tokens")):
                usage[k] += u.get(src) or 0
    return calls, usage, answers


def collect(run: str, transcripts: list[str]):
    out = HERE / "results" / run
    out.mkdir(parents=True, exist_ok=True)
    have = set()
    if (out / "runs.jsonl").exists():
        have = {r["batch"] for r in map(json.loads, (out / "runs.jsonl").read_text("utf-8").splitlines()) if r["status"] == "ok"}
    bs = batches()
    for t in map(Path, transcripts):
        text = t.read_text("utf-8")
        batch = next((b for b in bs if f"{run}--{b}" in text), None)
        if not batch or batch in have:
            continue
        calls, usage, ans = audit(t)
        want = bs[batch]["items"]
        bad = [c for c in calls if c not in ALLOWED]
        status = "tool_call" if bad else "ok" if all(i in ans for i in want) else "partial"
        with open(out / "runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"batch": batch, "status": status, "calls": calls, "usage": usage,
                                "n": sum(i in ans for i in want), "transcript": str(t)}) + "\n")
        if status == "ok":
            with open(out / "answers.jsonl", "a", encoding="utf-8") as f:
                for i in want:
                    f.write(json.dumps({"id": i, "batch": batch, "answer": ans[i]}, ensure_ascii=False) + "\n")
            have.add(batch)
        print(f"{run} {batch}: {status} calls={calls} usage={usage}")


if __name__ == "__main__":
    if sys.argv[1] == "prompt":
        print(prompt(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "run"))
    else:
        collect(sys.argv[2], sys.argv[3:])
