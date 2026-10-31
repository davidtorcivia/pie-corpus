"""Score judge verdict files against key.json: recall on each planted error kind, false alarms on the 24 untouched
items, and whether the judge named the planted word."""
import json
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
key = json.loads((HERE / "key.json").read_text())
n = lambda s: unicodedata.normalize("NFC", (s or "").strip(".,?!\"“” ")).lower()
for f in sys.argv[1:] or sorted(str(p) for p in HERE.glob("verdicts-*.json")):
    v = {x["id"]: x for x in json.loads(Path(f).read_text())}
    row, named, fa = {}, 0, []
    for kind in ("inflection", "lexeme", "negation"):
        ids = [i for i, k in key.items() if k["kind"] == kind]
        hit = [i for i in ids if v.get(i, {}).get("verdict") == "wrong"]
        row[kind] = f"{len(hit)}/{len(ids)}"
        named += sum(1 for i in hit if kind != "negation" and n(v[i].get("word")) in (n(key[i]["replaced_by"]),)
                     or kind != "negation" and n(key[i]["replaced_by"]) in n(v[i].get("word")))
    ok = [i for i, k in key.items() if k["kind"] == "ok"]
    fa = [i for i in ok if v.get(i, {}).get("verdict") == "wrong"]
    planted = [i for i, k in key.items() if k["kind"] != "ok"]
    caught = sum(v.get(i, {}).get("verdict") == "wrong" for i in planted)
    print(f"{Path(f).stem:24} recall {caught}/{len(planted)}  " + "  ".join(f"{k} {x}" for k, x in row.items())
          + f"  named {named}/24  false alarms {len(fa)}/{len(ok)} {fa}  missing {60 - len(v)}")
