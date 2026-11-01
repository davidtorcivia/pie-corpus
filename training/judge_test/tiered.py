"""Combine a screen and a confirm verdict file: an item is wrong only if the screen flagged it and the confirmer
agreed (the RL judge's tier 3, docs/research/rl-mac.md). Unparsed confirmations keep the screen's verdict.

    python tiered.py SCREEN.json CONFIRM.json OUT.json
"""
import json
import sys

screen, confirm, out = sys.argv[1:4]
h = {x["id"]: x for x in json.load(open(screen))}
s = {x["id"]: x for x in json.load(open(confirm)) if x["verdict"] in ("ok", "wrong")}
rows = [{**h[i], **({k: s[i][k] for k in ("verdict", "word", "reason")} if i in s else {})} for i in h]
json.dump(rows, open(out, "w"), ensure_ascii=False, indent=0)
