"""Test A (typological control), Near East half: candidate extraction.

Pre-registration: docs/research/knee-sleep-preregistration.md (binding).
Reads untrusted downloads under raw/daughters/ and never executes them; run with `python3 -I`.

Usage:
  python3 -I scripts/knee_sleep_testA_neareast.py hebrew  RAW_ROOT OUT.jsonl
  python3 -I scripts/knee_sleep_testA_neareast.py oracc   RAW_ROOT OUT.jsonl
  python3 -I scripts/knee_sleep_testA_neareast.py etcsl   RAW_ROOT OUT.jsonl
  python3 -I scripts/knee_sleep_testA_neareast.py tla     RAW_ROOT OUT.jsonl

Each output row is one candidate window: a knee word (or a contrast support word: bosom, lap, arms,
embrace) co-occurring with a sleep / dream / lying-down / death word inside the fixed window. Every
candidate is then read by hand and classified (positive / contrast / not-target) in
data/research/knee-sleep/testA-neareast.jsonl.

Windows (fixed before the run):
  Hebrew: same verse (primary) or adjacent verse +-1 (secondary).
  Cuneiform (ORACC, ETCSL): same line +-2 lines.
  Egyptian (TLA HF 'premium'): same sentence only (rows are context-free, shuffled sentences).
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- Hebrew (OSHB, Strong's numbers)
HEB_KNEE = {"1290": "berek knee", "1291": "berek (Aram.) knee", "755": "arkubbah (Aram.) knee"}
HEB_CONTRAST = {"2436": "heq bosom", "2684": "hosen bosom/lap", "2220": "zeroa arm", "2263": "habaq embrace"}
HEB_SLEEP = {
    "3462": "yashen sleep (v.)", "3463": "yashen asleep", "8142": "shenah sleep", "8139": "shenah (Aram.)",
    "8153": "shenat sleep", "5123": "num slumber", "8572": "tenumah slumber", "8639": "tardemah deep sleep",
    "7290": "radam sleep deeply", "7901": "shakab lie down", "2472": "halom dream", "2492": "halam dream",
    "2493": "helem (Aram.) dream", "4191": "mut die", "4194": "mawet death", "4193": "mot (Aram.) death",
    "1478": "gawa expire",
}


def heb_lemmas(attr):
    """'c/5921 a' -> ['5921'];  'b/2436' -> ['2436']; 'l' -> []"""
    out = []
    for part in attr.split("/"):
        m = re.match(r"\s*(\d+)", part)
        if m:
            out.append(m.group(1))
    return out


def run_hebrew(raw, out):
    wlc = os.path.join(raw, "hebrew-oshb-morphhb/extract/wlc")
    ns = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
    verses = []  # (osisID, [(lemmas, text)])
    for f in sorted(glob.glob(os.path.join(wlc, "*.xml"))):
        if f.endswith("VerseMap.xml"):
            continue
        root = ET.parse(f).getroot()
        for v in root.iter(ns + "verse"):
            ws = [(heb_lemmas(w.get("lemma", "")), "".join(w.itertext())) for w in v.iter(ns + "w")]
            verses.append((v.get("osisID"), ws))
    rows = []
    n_knee = 0
    for i, (vid, ws) in enumerate(verses):
        support = [(l, t) for ls, t in ws for l in ls if l in HEB_KNEE or l in HEB_CONTRAST]
        if not support:
            continue
        if any(l in HEB_KNEE for l, _ in support):
            n_knee += 1
        for off, window in ((0, "same verse"), (-1, "prev verse"), (1, "next verse")):
            j = i + off
            if j < 0 or j >= len(verses) or verses[j][0].split(".")[0] != vid.split(".")[0]:
                continue
            sl = [(l, t) for ls, t in verses[j][1] for l in ls if l in HEB_SLEEP]
            if sl:
                rows.append({
                    "corpus": "OSHB", "locus": vid, "window": window, "sleep_locus": verses[j][0],
                    "support": [(l, HEB_KNEE.get(l) or HEB_CONTRAST.get(l), t) for l, t in support],
                    "sleep": [(l, HEB_SLEEP[l], t) for l, t in sl],
                    "kind": "knee" if any(l in HEB_KNEE for l, _ in support) else "contrast",
                })
    write(out, rows)
    print(f"hebrew: {len(verses)} verses, {n_knee} verses with a knee word, {len(rows)} candidate windows")


# ---------------------------------------------------------------- ORACC (cf = citation form)
# ORACC lemmas are matched by (cf, gw): one cf covers homonyms (Sumerian u = 'and', 'sleep', 'grass'...).
AKK_KNEE = {("birku", "knee"), ("burku", "knee"), ("kimṣu", "shin"), ("kinṣu", "shin")}
AKK_CONTRAST = {("utlu", "lap"), ("sūnu", "loin"), ("kirimmu", "(crook of) arm"), ("edēru", "embrace"),
                ("haṣānu", "hug"), ("ḫaṣānu", "hug")}
AKK_SLEEP = {("ṣalālu", "lie (down)"), ("ṣallu", "sleeping"), ("šittu", "sleep"), ("ṣallūtu", "sleep"),
             ("šuttu", "dream"), ("nâlu", "lie down"), ("nâlu", "lie down (to sleep)"), ("nīlu", "lying down"),
             ("nēlu", "lying down"), ("utūlu", "lying down"), ("utulu", "lying down"), ("itūlu", "lie down"),
             ("mâtu", "die"), ("muātu", "die"), ("mūtu", "death"), ("mītu", "dead"), ("mītu", "dead man"),
             ("mītu", "dead person"), ("mētu", "dead"), ("mītūtu", "(state of) death"),
             ("naparqudu", "lying back"), ("naparqudu", "lie on one's back"), ("rabāṣu", "lie down"),
             ("diglu", "vision")}
SUX_KNEE = {("dub", "knee"), ("zeb", "knee")}
SUX_CONTRAST = {("ur", "root"), ("gu la", "embrace")}  # ePSD2 files ur2 'lap' under ur[root]
SUX_SLEEP = {("u", "sleep"), ("u ku", "sleep"), ("usag", "sleep"), ("uri", "sleep?"), ("mamud", "dream"),
             ("mašŋik", "vision"), ("nud", "lie"), ("usala nud", "lie down"), ("uš", "die"), ("namuš", "death"),
             ("an.eše e", "die"), ("šed", "lie")}


def oracc_lines(path):
    d = json.load(open(path, encoding="utf-8"))
    lic = d.get("license")
    lines = []  # [label, [(lang, cf, gw, form)]]
    cur = None

    def walk(n):
        nonlocal cur
        if isinstance(n, dict):
            if n.get("node") == "d" and n.get("type") == "line-start":
                cur = [n.get("label", n.get("n", "?")), []]
                lines.append(cur)
            elif n.get("node") == "l":
                f = n.get("f", {})
                if cur is None:
                    cur = ["?", []]
                    lines.append(cur)
                cur[1].append((f.get("lang", ""), f.get("cf"), f.get("gw"), f.get("form", "")))
            for c in n.get("cdl", []):
                walk(c)

    walk(d)
    return d.get("textid"), d.get("project"), lic, lines


def classify_word(lang, cf, gw):
    if cf is None:
        return None
    key = (cf, gw)
    if lang.startswith("akk"):
        sets = (AKK_KNEE, AKK_CONTRAST, AKK_SLEEP)
    elif lang.startswith("sux"):
        sets = (SUX_KNEE, SUX_CONTRAST, SUX_SLEEP)
    else:
        return None
    for name, st in zip(("knee", "contrast", "sleep"), sets):
        if key in st:
            return name
    return None


def run_oracc(raw, out):
    base = os.path.join(raw, "akkadian-sumerian-oracc/extract")
    rows, seen, ntext, nknee = [], set(), 0, 0
    for f in sorted(glob.glob(os.path.join(base, "**/corpusjson/*.json"), recursive=True)):
        try:
            tid, proj, lic, lines = oracc_lines(f)
        except Exception as e:  # malformed file: report, skip
            print("skip", f, e, file=sys.stderr)
            continue
        ntext += 1
        tagged = [[(w, classify_word(w[0], w[1], w[2])) for w in ws] for _, ws in lines]
        for i, tl in enumerate(tagged):
            sup = [w for w, c in tl if c in ("knee", "contrast")]
            if not sup:
                continue
            if any(c == "knee" for _, c in tl):
                nknee += 1
            lo, hi = max(0, i - 2), min(len(lines), i + 3)
            sl = [(lines[j][0], w) for j in range(lo, hi) for w, c in tagged[j] if c == "sleep"]
            if not sl:
                continue
            key = (tid, lines[i][0])
            if key in seen:  # umbrella and sub-project can both hold a text
                continue
            seen.add(key)
            rows.append({
                "corpus": "ORACC/" + str(proj), "text": tid, "line": lines[i][0], "license": lic,
                "support": [(w[1], w[2], w[3]) for w in sup],
                "sleep": [(lab, w[1], w[2], w[3]) for lab, w in sl],
                "kind": "knee" if any(c == "knee" for _, c in tl) else "contrast",
                "context": [(lines[j][0], " ".join(w[3] for w in lines[j][1])) for j in range(lo, hi)],
            })
    write(out, rows)
    print(f"oracc: {ntext} text files, {nknee} lines with a knee lemma, {len(rows)} candidate windows")


# ---------------------------------------------------------------- ETCSL (lemma attribute)
ETCSL_KNEE = {"dub3"}
ETCSL_CONTRAST = {"ur2", "gu2 la2"}
ETCSL_SLEEP = {"u3", "u3-sa2", "u3 ku4", "nu2", "ce21", "uc2", "ug7", "ug5", "nam-uc2", "ma-mu2",
               "ma-mu2-da"}


def run_etcsl(raw, out):
    base = os.path.join(raw, "sumerian-etcsl-ota2518/extract/etcsl")
    rows, nknee = [], 0
    for f in sorted(glob.glob(os.path.join(base, "transliterations/c.*.xml"))):
        txt = open(f, encoding="latin-1").read()
        # line-level: <l n="..." id="..."> ... </l>
        lines = re.findall(r'<l\b[^>]*\bn="([^"]*)"[^>]*>(.*?)</l>', txt, re.S)
        tagged = []
        for n, body in lines:
            ws = []
            for m in re.finditer(r'<w\b([^>]*)>(.*?)</w>', body, re.S):
                a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
                form = re.sub(r"<[^>]+>", "", m.group(2))
                ws.append((a.get("lemma"), a.get("label"), a.get("form", form)))
            tagged.append((n, ws))
        for i, (n, ws) in enumerate(tagged):
            sup = [w for w in ws if w[0] in ETCSL_KNEE or w[0] in ETCSL_CONTRAST]
            if not sup:
                continue
            if any(w[0] in ETCSL_KNEE for w in sup):
                nknee += 1
            lo, hi = max(0, i - 2), min(len(tagged), i + 3)
            sl = [(tagged[j][0], w) for j in range(lo, hi) for w in tagged[j][1] if w[0] in ETCSL_SLEEP]
            if not sl:
                continue
            rows.append({
                "corpus": "ETCSL", "text": os.path.basename(f)[:-4], "line": n,
                "support": sup, "sleep": sl,
                "kind": "knee" if any(w[0] in ETCSL_KNEE for w in sup) else "contrast",
                "context": [(tagged[j][0], " ".join(w[2] for w in tagged[j][1])) for j in range(lo, hi)],
            })
    write(out, rows)
    print(f"etcsl: {nknee} lines with dub3 'knee', {len(rows)} candidate windows")


# ---------------------------------------------------------------- TLA (lemma id|form, German translation)
EG_KNEE = re.compile(r"^(pd|pꜣḏ|pd\.wꞽ|mꜣs\.t|mꜣs)$")  # TLA files "knee" as pꜣḏ (59460)
EG_CONTRAST = re.compile(r"^(qni̯|qnꞽ|qnj|ḥpt|ḥpꞽ|rmn|ḥpṯ|mnꜥ\.t|ꞽnq)$")
EG_SLEEP = re.compile(r"^(qdd|qd|sḏr|nmꜥ|nmꜥi̯|rsw\.t|rs\.wt|mwt|mt|mni̯|wrd|sḏr\.t)$")
DE_KNEE = re.compile(r"Knie|Schoß|Schoss", re.I)
DE_CONTRAST = re.compile(r"Busen|Brust|umarm|Arme[mn]?\b|Armen", re.I)
DE_SLEEP = re.compile(r"schlaf|schläf|Traum|träum|sterb|starb|gestorben|\btot|Tod|\bliegt|\bliegen|ruht", re.I)


def run_tla(raw, out):
    rows, nknee = [], 0
    for sub in ("egyptian-tla-earlier-v18", "egyptian-tla-late-v19"):
        for i, line in enumerate(open(os.path.join(raw, sub, "train.jsonl"), encoding="utf-8")):
            r = json.loads(line)
            lem = [x.split("|", 1) for x in r.get("lemmatization", "").split() if "|" in x]
            forms = [l[1] for l in lem]
            tr = r.get("translation", "")
            k = [x for x in forms if EG_KNEE.match(x)] or DE_KNEE.findall(tr)
            c = [x for x in forms if EG_CONTRAST.match(x)] + DE_CONTRAST.findall(tr)
            s = [x for x in forms if EG_SLEEP.match(x)] + DE_SLEEP.findall(tr)
            if k:
                nknee += 1
            if (k or c) and s:
                rows.append({
                    "corpus": "TLA/" + sub, "row": i, "date": [r.get("dateNotBefore"), r.get("dateNotAfter")],
                    "knee": k, "contrast": c, "sleep": s, "kind": "knee" if k else "contrast",
                    "transliteration": r.get("transliteration"), "lemmatization": r.get("lemmatization"),
                    "translation": tr,
                })
    write(out, rows)
    print(f"tla: {nknee} sentences with a knee lemma or 'Knie/Schoß', {len(rows)} candidate sentences")


def write(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    cmd, raw, out = sys.argv[1:4]
    {"hebrew": run_hebrew, "oracc": run_oracc, "etcsl": run_etcsl, "tla": run_tla}[cmd](raw, out)
