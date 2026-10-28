"""Test A (knee-sleep typological control), East Asia/Finnic/Arabic: fetch open corpora.

Usage: python -I scripts/knee_sleep_testA_east_fetch.py wikisource <lang> <outdir> <prefix> [<prefix> ...]
       python -I scripts/knee_sleep_testA_east_fetch.py url <outfile> <url>

Wikisource mode lists every main-namespace page whose title starts with each prefix and saves
its current wikitext with revision id to <outdir>/pages.jsonl. No personal data in requests.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = "pie-corpus-research-fetch/1.0 (non-commercial research)"


def get(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(url)


def ws_titles(api, prefix):
    titles, cont = [], {}
    while True:
        p = {"action": "query", "list": "allpages", "apprefix": prefix, "apnamespace": 0,
             "aplimit": 500, "format": "json"}
        p.update(cont)
        d = json.loads(get(api, p))
        titles += [x["title"] for x in d["query"]["allpages"]]
        if "continue" not in d:
            return titles
        cont = {"apcontinue": d["continue"]["apcontinue"]}


def ws_fetch(lang, outdir, prefixes):
    api = f"https://{lang}.wikisource.org/w/api.php"
    os.makedirs(outdir, exist_ok=True)
    titles = []
    for pre in prefixes:
        titles += [t for t in ws_titles(api, pre) if t not in titles]
    print(len(titles), "titles", file=sys.stderr)
    with open(os.path.join(outdir, "pages.jsonl"), "w", encoding="utf-8") as out:
        for i in range(0, len(titles), 40):
            batch = titles[i:i + 40]
            d = json.loads(get(api, {"action": "query", "prop": "revisions", "rvprop": "content|ids|timestamp",
                                     "rvslots": "main", "titles": "|".join(batch), "format": "json",
                                     "formatversion": 2}))
            for pg in d["query"]["pages"]:
                if "revisions" not in pg:
                    continue
                rv = pg["revisions"][0]
                out.write(json.dumps({"title": pg["title"], "revid": rv["revid"], "timestamp": rv["timestamp"],
                                      "text": rv["slots"]["main"]["content"]}, ensure_ascii=False) + "\n")
            time.sleep(0.5)


def main():
    mode = sys.argv[1]
    if mode == "wikisource":
        ws_fetch(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif mode == "url":
        os.makedirs(os.path.dirname(sys.argv[2]), exist_ok=True)
        with open(sys.argv[2], "wb") as f:
            f.write(get(sys.argv[3]))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
