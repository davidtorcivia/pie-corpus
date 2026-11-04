"""Add lexicon hints (pie.translator.hints) to a generation prompt set, for the engine-in-the-loop mode: each prompt
whose answer is PIE from English (EN→PIE, English-turn dialogue) gets one line naming the project's word for each
English content word, after the user's message. The rows keep their ids and kinds and record the hints given.

    uv run --group translator python -I training/engine_prompts.py IN.jsonl OUT.jsonl
Then training/rl/eval_ckpt.py --prompts OUT.jsonl --constrain (constrained decoding for the PIE answers).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pie.translator.hints import hint_line, hints  # noqa: E402

HINT_KINDS = {"translate_en_pie", "translate_app/en_pie", "en_dialogue/en_pie", "en_dialogue/en_pie_gloss",
              "en_dialogue/mixed"}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    rows = [json.loads(x) for x in Path(src).read_text("utf-8").splitlines() if x.strip()]
    n = 0
    for r in rows:
        if r.get("kind") not in HINT_KINDS:
            continue
        msgs = r["prompt"]
        i = max(j for j, m in enumerate(msgs) if m["role"] == "user")
        hs = hints(msgs[i]["content"])
        line = hint_line(hs)
        r["hints"] = hs
        if line:
            msgs[i] = {**msgs[i], "content": msgs[i]["content"].rstrip() + "\n\n(" + line + ")"}
            n += 1
    Path(dst).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    print(f"{n} of {len(rows)} prompts hinted -> {dst}")


if __name__ == "__main__":
    main()
