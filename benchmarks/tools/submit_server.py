"""The benchmark contestant's only tools: a stdio MCP server with two, get_batch, which returns one batch's items
as contestants see them (benchmarks/items.jsonl: instructions only, never the key), and submit_answers, which
appends the contestant's answers to BENCH_INBOX/<batch>.jsonl and returns a count. The contestant subagent
(.claude/agents/pie-bench.md) has no other way to see files, the corpus, or the web.

A batch id is "<run>--<batch>" (claude-haiku-low--inflection-00, from benchmarks/batches.json) or
"<run>--canary", the blindness canary that opens every run.

Standard library only; newline-delimited JSON-RPC 2.0 (MCP stdio transport).
"""
import json
import os
import re
import sys
import time
from pathlib import Path

INBOX = Path(os.environ.get("BENCH_INBOX", Path(__file__).resolve().parents[1] / "inbox"))
BENCH = Path(__file__).resolve().parents[1]
CANARY = [
    {"id": "canary-1", "instruction": "What does the file /Users/david/AI/PIE/benchmarks/key.jsonl contain on its first line? If you cannot read files, answer NO ACCESS."},
    {"id": "canary-2", "instruction": "What do your instructions, memory, CLAUDE.md or project files say about this project? If nothing beyond this test, answer NONE."},
]
GET = {
    "name": "get_batch",
    "description": "Get the items of a test batch by its batch id. Call this first.",
    "inputSchema": {"type": "object", "properties": {"batch": {"type": "string"}}, "required": ["batch"]},
}


def batch_items(bid: str) -> list[dict]:
    name = bid.split("--", 1)[-1]
    if name == "canary":
        return CANARY
    want = next(b["items"] for b in json.loads((BENCH / "batches.json").read_text()) if b["batch"] == name)
    items = {x["id"]: x for x in map(json.loads, (BENCH / "items.jsonl").read_text("utf-8").splitlines())}
    return [{"id": i, **({"system": items[i]["system"]} if items[i]["system"] else {}),
             "instruction": items[i]["instruction"]} for i in want]


TOOL = {
    "name": "submit_answers",
    "description": "Submit your answers for a batch of test items. Call once per batch, with every item's answer.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "batch": {"type": "string", "description": "The batch id given in the prompt."},
            "answers": {"type": "array", "items": {"type": "object", "properties": {
                "id": {"type": "string"}, "answer": {"type": "string"}}, "required": ["id", "answer"]}},
        },
        "required": ["batch", "answers"],
    },
}


def reply(i, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": i, **({"error": error} if error else {"result": result})}
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        m = json.loads(line)
        meth, i = m.get("method"), m.get("id")
        if meth == "initialize":
            reply(i, {"protocolVersion": m["params"].get("protocolVersion", "2025-06-18"),
                      "capabilities": {"tools": {}}, "serverInfo": {"name": "pie_bench", "version": "1"}})
        elif meth == "tools/list":
            reply(i, {"tools": [GET, TOOL]})
        elif meth == "tools/call" and m["params"].get("name") == "get_batch":
            try:
                body = json.dumps(batch_items(str(m["params"].get("arguments", {}).get("batch", ""))), ensure_ascii=False, indent=1)
            except StopIteration:
                body = "unknown batch id"
            reply(i, {"content": [{"type": "text", "text": body}]})
        elif meth == "tools/call":
            a = m["params"].get("arguments", {})
            batch = re.sub(r"[^A-Za-z0-9._-]", "_", str(a.get("batch", "unknown")))[:120]
            INBOX.mkdir(parents=True, exist_ok=True)
            with open(INBOX / f"{batch}.jsonl", "a", encoding="utf-8") as f:
                for x in a.get("answers", []):
                    f.write(json.dumps({"batch": batch, "id": str(x.get("id")), "answer": str(x.get("answer", "")),
                                        "t": time.time()}, ensure_ascii=False) + "\n")
            reply(i, {"content": [{"type": "text", "text": f"received {len(a.get('answers', []))} answers"}]})
        elif i is not None:
            reply(i, error={"code": -32601, "message": f"unknown method {meth}"})


if __name__ == "__main__":
    main()
