"""The benchmark contestant's only tool: a stdio MCP server with one tool, submit_answers, which appends the
contestant's answers to BENCH_INBOX/<batch>.jsonl. It reads nothing and returns nothing but a count, so a
contestant subagent (.claude/agents/pie-bench.md) has no way to see files, the corpus, or the web.

Standard library only; newline-delimited JSON-RPC 2.0 (MCP stdio transport).
"""
import json
import os
import re
import sys
import time
from pathlib import Path

INBOX = Path(os.environ.get("BENCH_INBOX", Path(__file__).resolve().parents[1] / "inbox"))
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
            reply(i, {"tools": [TOOL]})
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
