"""Test A (knee-sleep typological control), East Asia / Finnic / Arabic half: candidate search.

Run: python -I scripts/knee_sleep_testA_east_search.py <repo-root> <out.jsonl>

Reads the downloaded corpora under raw/daughters/*-testA/ as data only and writes one JSON
row per candidate window: a knee word with a sleep/dream/death/pillow word nearby (role "knee"),
or a contrast support word (bosom, lap, arm, thigh) with a sleep word nearby (role "contrast").
Every candidate is then read and classified by hand (knee_sleep_testA_east_build.py).
Search terms are fixed here and listed in docs/research/knee-sleep/testA-east.md.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = sys.argv[1]
OUT = sys.argv[2]
RD = os.path.join(ROOT, "raw", "daughters")

# ---------------- term sets ----------------
CJK_KNEE = "膝䣛厀"
CJK_SLEEP = "寢寝眠寐臥卧睡夢夣寤"
CJK_DEATH = "死卒薨崩殂"
CJK_PILLOW = "枕"
# contrast supports (Chinese script): bosom/embrace, thigh, arm, upper arm
CJK_CONTRAST = "懷懐股肱臂"
WIN_CJK = 15

JA_KNEE = re.compile(r"膝|ひざ|ひさ(?=[のにをへ])")
JA_SLEEP = re.compile(r"寝|寐|眠|夢|臥|ね(?:ぶ|む|たる|入|いり|ぬ|たま|させ)|ねぶ|まどろ|うたたね|大殿籠|おほとのごも|御殿籠|ふし|臥し|伏し|枕")
JA_CONTRAST = re.compile(r"手枕|たまくら|手まくら|懐|ふところ|腕|かひな|かいな")
WIN_JA = 40

FI_KNEE = re.compile(r"\bpol[vw][ieae]", re.I)
FI_SLEEP = re.compile(r"\b(?:un[ieht]|unt|unen|unehe|unell|unill|unis|uin|nuk|nuku|ma[kg]a|makas|makoa|maata|maannu|lepä|lewä|lepo|lewo|kuol|kuoll)", re.I)
FI_CONTRAST = re.compile(r"\b(?:syl[ie]|syl[il]|sylih|sylis|helm[ao]|helmass|helmoih|pov[ie]|poweh|povess|powess|povell|powell)", re.I)
WIN_FI = 3  # lines each side

AR_KNEE = re.compile(r"ركب[ةت]")
AR_SLEEP = re.compile(r"نام|ينام|تنام|نوم|نائم|النوم|رقد|يرقد|راقد|رقاد|نعس|نعاس|هجع|وسن|الكرى|حلم|رؤيا|منام|وسد|توسد|اضطجع|مضطجع|مات|يموت|توفي|قبض")
AR_CONTRAST = re.compile(r"حجر[يهك]|حجرها|حجرهم|فخذ|صدر[يه]|صدرها")
WIN_AR = 12  # tokens each side

AR_DIAC = re.compile(r"[ً-ْٰـ]")


def cjk_scan(text, locate, corpus, date, rows, src):
    """text: normalized string; locate(i) -> locus string."""
    for i, ch in enumerate(text):
        role = None
        if ch in CJK_KNEE:
            role = "knee"
        elif ch in CJK_CONTRAST:
            role = "contrast"
        if not role:
            continue
        lo, hi = max(0, i - WIN_CJK), min(len(text), i + WIN_CJK + 1)
        win = text[lo:hi]
        sleep = [c for c in win if c in CJK_SLEEP]
        death = [c for c in win if c in CJK_DEATH]
        pil = CJK_PILLOW in text[max(0, i - 4):i + 5]
        if role == "knee" and not (sleep or death or pil):
            continue
        if role == "contrast":
            # contrast only when a sleep word is close (±8) or the pillow verb governs it
            # 懷 alone mostly means "thought/cherish": count it only as 懷中/懷裏/懷內/入懷/在懷/抱懷
            # or when it is pillowed on (枕 just before); 股肱 "ministers" is skipped.
            near = text[max(0, i - 6):i + 7]
            pillowed = CJK_PILLOW in text[max(0, i - 3):i]
            if ch in "懷懐" and not (pillowed or text[i + 1:i + 2] in ("中", "裏", "裡", "內", "内")
                                    or text[i - 1:i] in ("入", "在", "於", "抱")):
                continue
            if ch == "股" and "股肱" in text[max(0, i - 1):i + 2]:
                continue
            if not (any(c in CJK_SLEEP for c in near) or pillowed):
                continue
        rows.append({"corpus": corpus, "src": src, "locus": locate(i), "date": date, "role": role,
                     "word": ch, "co": "".join(sleep + death) + ("枕" if pil else ""),
                     "context": win})


def kanripo(rows):
    meta = {
        "KR1c0001": ("Shijing 毛詩", "c. 1000-600 BCE"), "KR1e0001": ("Zuozhuan 春秋左傳", "c. 4th c. BCE"),
        "KR2a0001": ("Shiji 史記", "c. 90 BCE"), "KR2a0007": ("Hanshu 漢書", "c. 111 CE"),
        "KR2a0009": ("Hou Hanshu 後漢書", "5th c. CE"), "KR2a0012": ("Sanguozhi 三國志", "late 3rd c. CE"),
        "KR2a0015": ("Jinshu 晉書 (juan 1-33 only in repo)", "648 CE"), "KR2e0001": ("Guoyu 國語", "c. 4th c. BCE"),
        "KR2e0003": ("Zhanguo ce 戰國策", "1st c. BCE compilation"), "KR3c0005": ("Hanfeizi 韓非子", "3rd c. BCE"),
        "KR5c0126": ("Zhuangzi 莊子", "4th-3rd c. BCE"), "KR5c0124": ("Liezi 列子", "c. 4th c. CE"),
        "KR4a0001": ("Chuci 楚辭", "3rd c. BCE-2nd c. CE"), "KR4h0001": ("Wenxuan 文選", "c. 530 CE"),
        "KR3l0002": ("Shishuo xinyu 世說新語", "c. 430 CE"), "KR3l0090": ("Shanhaijing 山海經", "4th c. BCE-1st c. CE"),
        "KR3l0098": ("Shiyi ji 拾遺記", "4th c. CE"), "KR3l0099": ("Soushen ji 搜神記", "c. 350 CE"),
        "KR3l0100": ("Soushen houji 搜神後記", "5th c. CE"), "KR3l0118": ("Taiping guangji 太平廣記", "978 CE (compiling earlier tales)"),
        "KR3l0123": ("Bowu zhi 博物志", "3rd c. CE"), "KR3l0125": ("Youyang zazu 酉陽雜俎", "c. 860 CE"),
        "KR4h0140": ("Quan Tangshi 全唐詩", "618-907 CE poems (compiled 1705)"),
    }
    for d in sorted(glob.glob(os.path.join(RD, "chinese-kanripo-testA", "x", "*-master"))):
        kid = os.path.basename(d).split("-")[0]
        name, date = meta[kid]
        for f in sorted(glob.glob(os.path.join(d, kid + "_*.txt"))):
            raw = open(f, encoding="utf-8").read()
            juan = re.search(r"#\+PROPERTY: JUAN (.*)", raw)
            juan = juan.group(1).strip() if juan else os.path.basename(f)
            body = raw.split("\n", 1)[1] if raw.startswith("#") else raw
            buf, pbs, pb = [], [], "?"
            for tok in re.split(r"(<pb:[^>]+>)", body):
                if tok.startswith("<pb:"):
                    pb = tok[4:-1]
                    continue
                for line in tok.split("\n"):
                    if line.startswith("#"):
                        continue
                    for c in line:
                        if c in "¶　 \t\r":
                            continue
                        buf.append(c)
                        pbs.append(pb)
            text = "".join(buf)
            cjk_scan(text, lambda i, n=name, j=juan, p=pbs: f"{n} {j} [{p[i]}]", f"chinese:{kid}", date,
                     rows, os.path.relpath(f, ROOT))


def strip_wiki(t):
    t = re.sub(r"\{\{\*\|([^}]*)\}\}", r"〈\1〉", t)
    t = re.sub(r"\{\{[^{}]*\}\}", "", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    return t


def kanbun_japan(rows):
    f = os.path.join(RD, "japanese-wikisource-testA", "zh-kanbun", "pages.jsonl")
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        title = d["title"]
        if title.startswith("古事記"):
            corpus, date = "japanese-kanbun:Kojiki", "712 CE"
        else:
            corpus, date = "japanese-kanbun:Nihon shoki", "720 CE"
        t = strip_wiki(d["text"])
        # locus: section heading (== x ==) for Kojiki, paragraph number for NS
        locs, cur, para = [], "", 0
        out = []
        for ln in t.split("\n"):
            m = re.match(r"==+\s*(.*?)\s*==+", ln)
            if m:
                cur = m.group(1)
            if ln.strip():
                para += 1
            for c in ln:
                if c in " \t":
                    continue
                out.append(c)
                locs.append(f"{title} §{cur} ¶{para}" if cur else f"{title} ¶{para}")
            out.append("\n")
            locs.append("")
        text = "".join(out)
        cjk_scan(text, lambda i, L=locs: L[i], corpus, date, rows, os.path.relpath(f, ROOT))


def yuanchao(rows):
    f = os.path.join(RD, "mongolian-zhwikisource-testA", "pages.jsonl")
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        t = strip_wiki(d["text"])
        paras = [p for p in t.split("\n") if p.strip()]
        out, locs = [], []
        for k, p in enumerate(paras, 1):
            for c in p:
                out.append(c)
                locs.append(f"{d['title']} ¶{k}")
        cjk_scan("".join(out), lambda i, L=locs: L[i], "mongolian-chinese-zongyi:Yuanchao mishi",
                 "Mongolian original c. 1228-1252; Ming Chinese summary translation c. 1370s-1380s",
                 rows, os.path.relpath(f, ROOT))


def ja_scan(text, locus, corpus, date, rows, src):
    for rx, role in ((JA_KNEE, "knee"), (JA_CONTRAST, "contrast")):
        for m in rx.finditer(text):
            i = m.start()
            win = text[max(0, i - WIN_JA): i + WIN_JA]
            sl = [x.group(0) for x in JA_SLEEP.finditer(win)]
            if role == "knee" or sl:
                rows.append({"corpus": corpus, "src": src, "locus": locus, "date": date, "role": role,
                             "word": m.group(0), "co": "|".join(sl), "context": win.replace("\n", " ")})


def manyoshu(rows):
    f = os.path.join(RD, "japanese-wikisource-testA", "ja-manyoshu", "pages.jsonl")
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        for blk in re.split(r"\[歌番号\]", d["text"])[1:]:
            num = re.search(r"(\d\d/\d{4})", blk).group(1)
            fields = dict(re.findall(r"\[(原文|訓読|仮名|題詞)\]([^\n]*)", blk))
            joined = " / ".join(fields.get(k, "") for k in ("題詞", "原文", "訓読", "仮名"))
            # scan reading + kana (knee written 膝 or 比射/比佐 in 原文 shows up as ひざ in 仮名)
            ja_scan(fields.get("訓読", "") + " ‖ " + fields.get("仮名", ""), f"MYS {num}", "japanese:Man'yoshu",
                    "c. 600-759 CE (compiled after 759)", rows, os.path.relpath(f, ROOT))
            if rows and rows[-1]["locus"] == f"MYS {num}":
                rows[-1]["full"] = joined


def genji(rows):
    f = os.path.join(RD, "japanese-wikisource-testA", "ja-genji", "pages.jsonl")
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        if not d["title"].startswith("源氏物語/"):
            continue
        paras = [p for p in strip_wiki(d["text"]).split("\n") if p.strip()]
        for k, p in enumerate(paras, 1):
            ja_scan(p, f"Genji {d['title'].split('/')[1]} ¶{k}", "japanese:Genji monogatari", "c. 1000-1010 CE",
                    rows, os.path.relpath(f, ROOT))


def ise(rows):
    f = os.path.join(RD, "japanese-wikisource-testA", "ja-ise", "ise_parse.json")
    h = json.load(open(f, encoding="utf-8"))["parse"]["text"]
    t = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>|</p>|</div>", "\n", h)))
    paras = [p for p in t.split("\n") if p.strip()]
    for k, p in enumerate(paras, 1):
        ja_scan(p, f"Ise monogatari (Gunsho ruiju text) line {k}", "japanese:Ise monogatari",
                "c. 900-950 CE", rows, os.path.relpath(f, ROOT))


def oncoj(rows):
    base = os.path.join(RD, "japanese-oncoj-testA", "x", "data-master", "psd")
    # piza (knee) L051796; contrast: tamakura 'arm-pillow' and ta 'hand/arm' + maku compounds
    for f in sorted(glob.glob(os.path.join(base, "*.psd"))):
        txt = open(f, encoding="utf-8-sig").read()
        for tr in re.split(r"\n(?=\( )", txt):
            words = re.findall(r"\((L\w+) \((?:PHON|LOG)[^ ]* ([^)]+)\)\)", tr)
            ids = re.findall(r"\(ID ([^)]+)\)", tr)
            phon = " ".join(w for _, w in words)
            if "L051796" in tr:
                rows.append({"corpus": "japanese:ONCOJ", "src": os.path.relpath(f, ROOT), "locus": ",".join(ids),
                             "date": "c. 600-759 CE", "role": "knee", "word": "piza", "co": "", "context": phon})
            elif re.search(r"\btamakura\b|\bta makura\b", phon):
                rows.append({"corpus": "japanese:ONCOJ", "src": os.path.relpath(f, ROOT), "locus": ",".join(ids),
                             "date": "c. 600-759 CE", "role": "contrast", "word": "tamakura", "co": "",
                             "context": phon})


def finnic(rows):
    files = {"pg7000.txt": ("finnic:Kalevala 1849", "1849 (folk runes collected 1820s-1840s)"),
             "pg48380.txt": ("finnic:Kalevala 1835 vol. 1", "1835"),
             "pg48381.txt": ("finnic:Kalevala 1835 vol. 2", "1835"),
             "pg7078.txt": ("finnic:Kanteletar", "1840 (folk songs collected 1820s-1830s)")}
    for fn, (corpus, date) in files.items():
        f = os.path.join(RD, "finnic-gutenberg-testA", fn)
        lines = open(f, encoding="utf-8").read().split("\n")
        head = ""
        heads = []
        for ln in lines:
            s = ln.strip()
            if re.match(r"^(.*\brunoa?\b.*|[0-9]+\.\s.*|[A-ZÄÖ][A-ZÄÖ ,.-]{3,})$", s) and len(s) < 60 and not FI_KNEE.search(s):
                head = s
            heads.append(head)
        for i, ln in enumerate(lines):
            for rx, role in ((FI_KNEE, "knee"), (FI_CONTRAST, "contrast")):
                if not rx.search(ln):
                    continue
                win = lines[max(0, i - WIN_FI): i + WIN_FI + 1]
                sl = [m.group(0) for w in win for m in FI_SLEEP.finditer(w)]
                if role == "contrast" and not sl:
                    continue
                if role == "knee" and not sl:
                    # still keep knee lines for the recall count, flagged no-cooccurrence
                    rows.append({"corpus": corpus, "src": os.path.relpath(f, ROOT), "locus": f"{heads[i]} | line {i+1}",
                                 "date": date, "role": "knee-nosleep", "word": rx.search(ln).group(0), "co": "",
                                 "context": ln.strip()})
                    continue
                rows.append({"corpus": corpus, "src": os.path.relpath(f, ROOT), "locus": f"{heads[i]} | line {i+1}",
                             "date": date, "role": role, "word": rx.search(ln).group(0), "co": "|".join(sl),
                             "context": " / ".join(w.strip() for w in win if w.strip())})


def arabic(rows):
    meta = {"0256Bukhari": ("Sahih al-Bukhari", "d. 256 AH / 870 CE"),
            "0328IbnCabdRabbih": ("al-ʿIqd al-farid (Ibn ʿAbd Rabbih)", "d. 328 AH / 940 CE"),
            "0276IbnQutaybaDinawari.CuyunAkhbar": ("ʿUyun al-akhbar (Ibn Qutayba)", "d. 276 AH / 889 CE"),
            "0276IbnQutaybaDinawari.ShicrWaShucara": ("al-Shiʿr wa-l-shuʿaraʾ (Ibn Qutayba)", "d. 276 AH / 889 CE"),
            "0255Jahiz.BayanWaTabyin": ("al-Bayan wa-l-tabyin (al-Jahiz)", "d. 255 AH / 868 CE"),
            "0255Jahiz.Hayawan": ("al-Hayawan (al-Jahiz)", "d. 255 AH / 868 CE"),
            "0168MufaddalDabbi": ("al-Mufaddaliyyat", "pre-Islamic/early Islamic poems; compiled d. 168 AH / 784 CE")}
    for f in sorted(glob.glob(os.path.join(RD, "arabic-openiti-testA", "0*"))):
        key = [k for k in meta if os.path.basename(f).startswith(k)][0]
        name, date = meta[key]
        raw = open(f, encoding="utf-8").read()
        body = raw.split("#META#Header#End#", 1)[-1]
        # OpenITI page markers close their page: a token's page is the NEXT PageV..P.. marker
        toks, locs, pending = [], [], []
        for tok in body.split():
            m = re.match(r"PageV(\d+)P(\d+)", tok)
            if m:
                page = f"vol {int(m.group(1))} p {int(m.group(2))}"
                for j in pending:
                    locs[j] = page
                pending = []
                continue
            tok = AR_DIAC.sub("", tok)
            if tok in ("###", "|", "~~", "#", "%~%") or not tok.strip("#|~%"):
                continue
            toks.append(tok)
            locs.append("end")
            pending.append(len(toks) - 1)
        for i, t in enumerate(toks):
            for rx, role in ((AR_KNEE, "knee"), (AR_CONTRAST, "contrast")):
                if not rx.search(t):
                    continue
                win = toks[max(0, i - WIN_AR): i + WIN_AR + 1]
                sl = [w for w in win if AR_SLEEP.search(w)]
                if not sl:
                    continue
                # page marker follows its page in OpenITI: the page the token is on is the next marker
                rows.append({"corpus": "arabic:" + name, "src": os.path.relpath(f, ROOT),
                             "locus": f"{name}, {locs[i]} (OpenITI page marker), token {i}", "date": date, "role": role,
                             "word": t, "co": "|".join(sl), "context": " ".join(win),
                             "licence": "OpenITI CC BY-NC-SA 4.0: research only"})


def main():
    rows = []
    kanbun_japan(rows)
    manyoshu(rows)
    oncoj(rows)
    genji(rows)
    ise(rows)
    kanripo(rows)
    yuanchao(rows)
    finnic(rows)
    arabic(rows)
    for k, r in enumerate(rows):
        r["cand"] = f"c{k:05d}"
    with open(OUT, "w", encoding="utf-8") as o:
        for r in rows:
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    c = Counter((r["corpus"].split(":")[0] + ":" + r["corpus"].split(":")[-1][:30], r["role"]) for r in rows)
    for k, v in sorted(c.items()):
        print(k, v)


if __name__ == "__main__":
    main()
