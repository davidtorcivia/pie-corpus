"""Build the release page (index.html) and the PNG card page (cards.html) from benchmarks/results/summary.json."""
import json
from pathlib import Path

HERE = Path(__file__).parent
SUMMARY = Path("/Users/david/AI/PIE/benchmarks/results/summary.json")

NAMES = {
    "ours-nemotron35-e3-bf16": ("PIE Nemotron 120B · e3", "nemotron", "bf16"),
    "ours-nemotron35-e1-bf16": ("PIE Nemotron 120B · e1", "nemotron", "bf16"),
    "ours-nemotron35-e1": ("PIE Nemotron 120B · e1 (5-bit)", "nemotron", "5-bit"),
    "ours-nemotron35-e2": ("PIE Nemotron 120B · e2 (5-bit)", "nemotron", "5-bit"),
    "ours-merge-half": ("PIE Qwen 35B · RL merge", "qwen", "5-bit"),
    "ours-rl1-step500": ("PIE Qwen 35B · RL stage 1", "qwen", "5-bit"),
    "ours-rl3-step275": ("PIE Qwen 35B · RL stage 3", "qwen", "5-bit"),
    "ours-e3": ("PIE Qwen 35B · SFT", "qwen", "5-bit"),
}
FAMILY = {"claude-opus": "opus", "claude-sonnet": "sonnet", "claude-haiku": "haiku",
          "codex-gpt-6.1-sol": "sol", "codex-gpt-6.1-terra": "terra"}
LABEL = {"opus": "Claude Opus 5.5", "sonnet": "Claude Sonnet 5.5", "haiku": "Claude Haiku 5.5",
         "sol": "GPT-6.1 Sol", "terra": "GPT-6.1 Terra"}

runs = []
for r in json.loads(SUMMARY.read_text()):
    c = r["contestant"]
    if c in NAMES:
        name, fam, prec = NAMES[c]
        effort, ours = None, True
    else:
        base, effort = c.rsplit("-", 1)
        fam = FAMILY[base]
        name, prec, ours = f"{LABEL[fam]} · {effort}", None, False
    runs.append({"id": c, "name": name, "family": fam, "effort": effort, "ours": ours, "prec": prec,
                 "L": r["pie_score"]["lenient"], "S": r["pie_score"]["strict"],
                 "seg": {k: [v["lenient"], v["strict"], v["n"]] for k, v in r["segments"].items()}})
runs.sort(key=lambda x: -x["L"])
data = "const DATA = " + json.dumps({"runs": runs}, ensure_ascii=False) + ";\n"
charts = (HERE / "charts.js").read_text()
for src, out in (("page.src.html", "index.html"), ("cards.src.html", "cards.html")):
    html = (HERE / src).read_text().replace("/*__DATA__*/", data).replace("/*__CHARTS__*/", charts)
    (HERE / out).write_text(html)
    print("wrote", out, len(html))
