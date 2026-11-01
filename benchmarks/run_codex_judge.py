"""The benchmark's GPT judge: GPT-6.1 Sol at high effort through Codex, grading judge packets
(benchmarks/judge_packets.py) by benchmarks/judge_brief.md, with a shell so it can run the engine tool
(training/judge_test/pie-tool). It may write only in the round's directory.

    python3 -I benchmarks/run_codex_judge.py ROUND [--packets 000,001] [--jobs 3]
"""
import argparse
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path("/Users/david/AI/pie-runs/bench/judge")


def run(d: Path, n: str) -> dict:
    out = d / f"verdicts-gpt-{n}.json"
    if out.exists():
        return {"packet": n, "status": "exists"}
    msg = (f"Follow the grading brief in {HERE / 'judge_brief.md'} exactly (read it first). "
           f"Packet: {d / f'packet-{n}.json'}. Output file: {out}.")
    t = time.time()
    p = subprocess.run(["codex", "exec", "--json", "--skip-git-repo-check", "-m", "gpt-6.1-sol",
                        "-c", "model_reasoning_effort=high", "-s", "workspace-write", "-C", str(d),
                        "--add-dir", "/tmp/pie-uv-cache", "--add-dir", str(HERE.parent / ".cache"), msg],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=3600)
    usage = next((json.loads(x).get("usage") for x in reversed(p.stdout.splitlines())
                  if x.startswith("{") and '"turn.completed"' in x), {})
    return {"packet": n, "status": "ok" if out.exists() else "no_output", "s": round(time.time() - t), "usage": usage,
            "exit": p.returncode, "stderr": p.stderr[-300:] if p.returncode else ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("--packets")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    d = OUT / a.round
    ns = a.packets.split(",") if a.packets else sorted(p.stem.split("-")[1] for p in d.glob("packet-*.json"))
    with ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(lambda n: run(d, n), ns):
            with open(d / "gpt-runs.jsonl", "a") as f:
                f.write(json.dumps(r) + "\n")
            print(r, flush=True)


if __name__ == "__main__":
    main()
