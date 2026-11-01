"""Run benchmark batches through Codex (subscription), blind: no shell, no web, no MCP, no skills, no project docs,
a one-line instruction file in place of the agent prompt, an empty working directory and a clean CODEX_HOME that
holds only a copy of the login (benchmarks/README.md). Each run's rollout file must show zero tool calls, or its
answers are discarded (status "tool_call") and the batch is rerun next time.

    python3 -I benchmarks/run_codex.py --model gpt-6.1-terra --effort low [--batches inflection-00,...] [--jobs 3]

Answers: benchmarks/results/codex-<model>-<effort>/answers.jsonl (one row per item; resumable: answered batches
are skipped); per-batch usage and the blindness check in runs.jsonl beside it.
"""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path("/Users/david/AI/pie-runs/bench")
HOME = BASE / "codex_home"
INSTR = BASE / "codex_instructions.md"
DISABLE = ["shell_tool", "unified_exec", "code_mode_host", "apps", "plugins", "multi_agent", "view_image",
           "image_generation", "browser_use", "computer_use", "skill_search", "tool_suggest", "goals", "sleep_tool",
           "hooks"]
CALLS = re.compile(r'"type"\s*:\s*"(function_call|custom_tool_call|local_shell_call|web_search_call|mcp_tool_call)"')

BRIEF = (HERE / "tools/pie-bench.agent.md").read_text("utf-8").split("---", 2)[2].strip()
BRIEF = BRIEF.replace("When you have answered every item, call submit_answers once with the batch id and all the "
                      "answers, then reply with just the number of answers you submitted.",
                      'Reply with only a JSON array, one object per item in order: {"id": the item id, "answer": '
                      "your answer as a string}.")


def setup():
    HOME.mkdir(parents=True, exist_ok=True)
    auth = HOME / "auth.json"
    if not auth.exists():                      # the login only; nothing else of ~/.codex
        shutil.copy(Path.home() / ".codex/auth.json", auth)
        auth.chmod(0o600)
    INSTR.write_text("You have no tools and no files. Answer the user's questions from your own knowledge only.\n")


def prompt(batch: dict, items: dict) -> str:
    body = [{"id": i, **({"system": items[i]["system"]} if items[i]["system"] else {}),
             "instruction": items[i]["instruction"]} for i in batch["items"]]
    return f"{BRIEF}\n\nBatch {batch['batch']}. Items:\n{json.dumps(body, ensure_ascii=False, indent=1)}"


def run(model: str, effort: str, batch: dict, items: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="pie-bench-") as empty:
        last = Path(empty) / "last.txt"
        (Path(empty) / "canary.txt").write_text("CANARY-7731\n")     # readable only with a tool
        cmd = ["codex", "exec", "--json", "--skip-git-repo-check", "--ignore-rules", "-s", "read-only", "-C", empty,
               "-m", model, "-c", f"model_reasoning_effort={effort}", "-c", "web_search=disabled",
               "-c", "project_doc_max_bytes=0", "-c", "skills.include_instructions=false",
               "-c", f'model_instructions_file="{INSTR}"', "-c", "include_permissions_instructions=false",
               "-c", "include_environment_context=false", "-c", "include_collaboration_mode_instructions=false",
               "-c", "include_apps_instructions=false", "-c", "features.code_mode.enabled=false",
               *[a for f in DISABLE for a in ("--disable", f)], "-o", str(last), prompt(batch, items)]
        t = time.time()
        p = subprocess.run(cmd, cwd=empty, env={"CODEX_HOME": str(HOME), "PATH": "/usr/bin:/bin:/Users/david/.local/bin",
                                                "HOME": str(Path.home())},
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=3600)
        events = [json.loads(x) for x in p.stdout.splitlines() if x.startswith("{")]
        thread = next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)
        usage = next((e.get("usage") for e in reversed(events) if e.get("type") == "turn.completed"), {})
        text = last.read_text("utf-8") if last.exists() else ""
    rollout = next(iter(sorted(HOME.glob(f"sessions/**/rollout-*{thread}*.jsonl"))), None) if thread else None
    calls = len(CALLS.findall(rollout.read_text("utf-8"))) if rollout else None
    m = re.search(r"\[.*\]", text, re.S)
    try:
        answers = {str(a["id"]): str(a.get("answer", "")) for a in json.loads(m[0])} if m else {}
    except (json.JSONDecodeError, TypeError, KeyError):
        answers = {}
    status = ("tool_call" if calls else "no_rollout" if calls is None else
              "ok" if len(answers) == len(batch["items"]) else "partial")
    return {"batch": batch["batch"], "status": status, "tool_calls": calls, "answers": answers, "usage": usage,
            "s": round(time.time() - t, 1), "rollout": str(rollout) if rollout else None, "exit": p.returncode,
            "stderr": p.stderr[-500:] if p.returncode else ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--effort", required=True)
    ap.add_argument("--batches", help="comma-separated batch ids (default: all)")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--canary", action="store_true", help="only the blindness canary batch")
    a = ap.parse_args()
    setup()
    items = {x["id"]: x for x in map(json.loads, (HERE / "items.jsonl").read_text("utf-8").splitlines())}
    if a.canary:
        can = {"canary-1": "What does the file canary.txt in your working directory say? If you cannot read files, answer NO ACCESS.",
               "canary-2": "Quote the first line of /Users/david/AI/PIE/README.md, or answer NO ACCESS.",
               "canary-3": "What do your instructions, memory or project files say about this project? If nothing, answer NONE."}
        items |= {k: {"id": k, "system": "", "instruction": v} for k, v in can.items()}
        r = run(a.model, a.effort, {"batch": "canary", "items": list(can)}, items)
        print(json.dumps({k: r[k] for k in ("status", "tool_calls", "answers", "usage", "rollout")}, ensure_ascii=False, indent=1))
        return
    batches = json.loads((HERE / "batches.json").read_text())
    if a.batches:
        want = set(a.batches.split(","))
        batches = [b for b in batches if b["batch"] in want]
    out = HERE / "results" / f"codex-{a.model}-{a.effort}"
    out.mkdir(parents=True, exist_ok=True)
    done = set()
    if (out / "runs.jsonl").exists():
        done = {r["batch"] for r in map(json.loads, (out / "runs.jsonl").read_text("utf-8").splitlines())
                if r["status"] == "ok"}
    todo = [b for b in batches if b["batch"] not in done]
    print(f"{a.model} {a.effort}: {len(todo)} batches to run, {len(done)} done", flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(lambda b: run(a.model, a.effort, b, items), todo):
            with open(out / "runs.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({k: v for k, v in r.items() if k != "answers"} | {"n": len(r["answers"])},
                                   ensure_ascii=False) + "\n")
            if r["status"] == "ok":
                with open(out / "answers.jsonl", "a", encoding="utf-8") as f:
                    for i, ans in r["answers"].items():
                        f.write(json.dumps({"id": i, "batch": r["batch"], "answer": ans}, ensure_ascii=False) + "\n")
            print(f"  {r['batch']}: {r['status']} tool_calls={r['tool_calls']} n={len(r['answers'])} "
                  f"{r['s']} s {r['usage']}", flush=True)


if __name__ == "__main__":
    main()
