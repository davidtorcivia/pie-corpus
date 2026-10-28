#!/usr/bin/env python3
"""Test B (knee-sleep pre-registration): Hittite *swep- vs *ses- sleep verbs in TLHdig.

Run with `python -I`. Reads raw/daughters/hittite-tlhdig/extract (never executes anything there).
Unit = paragraph: the stretch of one tablet between <parsep/>/<parsep_dbl/> markers
(TLHdig's <clb> clause marks are too sparse to use as clauses).

Each <w> is classified from its candidate analyses (mrpN = lemma@gloss@form...) and the
selection mrp0sel. Status per category:
  sel   the selected analysis belongs to the category
  only  no selection, every candidate analysis belongs to the category
  amb   no selection, some but not all candidates belong to it
  spell no analyses at all, the transliteration matches the spelling list
  rej   a selection exists and picks something else (not counted)
Counted ("auto") = sel | only | spell. amb words are listed for reading but not counted.
Then a hand-vetting file (VETTING below) overrides individual tokens after reading.

Outputs (paths given on the command line):
  --cands  JSONL of every paragraph with a sleep word plus a knee or dream word, or with any
           *swep- candidate (auto or amb), with the paragraph text, for reading
  --summary JSON of counts and Fisher tests
"""
import argparse, collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fisher import fisher_greater, odds_ratio  # noqa: E402

W = re.compile(r'<w\b([^>]*)>(.*?)</w>', re.S)
TOK = re.compile(r'<lb\b([^>]*)/?>|<parsep(?:_dbl)?\b[^>]*/?>|<w\b([^>]*)>(.*?)</w>', re.S)
ATT = re.compile(r'(\w+)="([^"]*)"')
TAG = re.compile(r'<[^>]*>')
PREFIX = re.compile(r'^[\u2460-\u24ff\u2776-\u2793\s]+')  # circled ambiguity markers like "②Ⓐ "

def base(lemma):
    return PREFIX.sub('', lemma).strip()

# --- lemma inventories (lemma base, gloss substring) -------------------------------------
SES = {'šēš-/šaš-', 'šiš=k-', 'šiškeš=k-', 'šišk='}
SES_CAUS = {'šaš=nu-', 'šašša=nu-', 'šašnuš=k-', 'šaššanuš=k-', 'šašanuš=k-'}
SWEP = {'šupp=', 'šupp=a-', 'šup=', 'šupp=ar', 'šupp=iye/a-', 'šuppar=iye/a-', 'šuppar=iya-',
        'šupparu=ant-'}
KNEE = {'gen=u-', 'gan=u-', 'kinu-', 'genušš=a/i-'}
KNEE_CLOTH = {'ginuw=a-'}
DREAM = {'tešḫ=a-', 'tiešḫ=a-', 'zašḫ=ai-', 'tešḫan=iye/a-', 'tešḫanišk='}
DREAM_LOGO = {'Ù-TUM', 'Ù-TI', 'MA.MÚ', 'Ù˽NUN'}   # Akkadogram/Sumerogram "dream"
SLEEP_GLOSS = re.compile(r'schlaf|Schlaf|schläf')

def in_cat(cat, lemma, gloss):
    b = base(lemma)
    if cat == 'ses':
        return b in SES and 'schlafen' in gloss
    if cat == 'swep':
        return b in SWEP and bool(SLEEP_GLOSS.search(gloss))
    if cat == 'knee':
        return b in KNEE and gloss.startswith('Knie')
    if cat == 'kneecloth':
        return b in KNEE_CLOTH
    if cat == 'dream':
        return b in DREAM
    if cat == 'zashai':
        return b == 'zašḫ=ai-'
    if cat == 'tesha':
        return b in DREAM and b != 'zašḫ=ai-'
    if cat == 'dreamlogo':
        # Ù with a Hittite complement or a 'Schlaf' selection is the logogram of tešḫa-;
        # bare Ù is mostly Akkadian u "and", so bare Ù counts only when selected as Schlaf.
        return b in DREAM_LOGO or (b in {'Ù', 'Ù='} and 'chlaf' in gloss)
    return False

# --- spelling lists for words with no analyses (TLHdig trans: k for g, u for w) -----------
ENC = r'(?:ma|ia|a|kan|šan|ašta|pat|za|ua|uar|mu|ta|ši|šmaš|at|aš|an)*'
SPELL = {
    'ses': re.compile(r'^(?:šeš(?:zi|mi|anzi|un|uanzi|uaš|uar|ta|tu|teni|ten|er|ir|ki\w*)|šešš(?:un|er|ir)'
                      r'|šiške\w*|šiški\w*|šišk\w*|šašanzi|šašueni|šašanna)' + ENC + '$'),
    'swep': re.compile(r'^(?:šupt(?:ari|at|a|ati|enua)|šuppar(?:i|ia|u)\w*|šupparu\w*'
                       r'|šuppant\w*|šupuanzi)' + ENC + '$'),
    'knee': re.compile(r'^(?:kenu(?:a|aš|az|aza|it|š|šš\w*)?|genu\w*|kanu(?:t)?|GENU\w*|BIRK\w*|BI-IR-KI\w*)'
                       + ENC + '$'),
    'dream': re.compile(r'^(?:tešḫ(?!ap|uli|alli)\w*|tiešḫ\w*|zašḫ(?!apun)\w*)$'),
    'zashai': re.compile(r'^zašḫ(?!apun)\w*$'),
    'tesha': re.compile(r'^(?:tešḫ(?!ap|uli|alli)\w*|tiešḫ\w*)$'),
    'dreamlogo': re.compile(r'(?:MÁŠ\.GI|Ù-TUM|Ù-TI|MA\.MÚ|^Ù(?:it|an|uš|aš|az|i|ituamu)$)'),
}
FOREIGN = {'AKK', 'HURR', 'HAT', 'SUM', 'LUW', 'PAL', 'HURR?', 'AKK?'}
LOGO_COMPLEMENT = re.compile(r'^(?:A-NA |IŠ-TU |ŠA |I-NA )?Ù(?:-TUM|-TI|it|an|uš|aš|az|i|ituamu|za)\w*$')

def cat_logo(tr):
    """Ù with a Hittite phonetic complement, or Ù-TUM/Ù-TI, MA.MÚ, MÁŠ.GI₆: logograms for dream/sleep."""
    return bool(LOGO_COMPLEMENT.match(tr) or re.match(r'^(?:\S+ )?(?:MA\.MÚ|MÁŠ\.GI)', tr))

CATS = ['ses', 'swep', 'knee', 'kneecloth', 'dream', 'tesha', 'zashai', 'dreamlogo']
# duplicate manuscripts of one composition among the read paragraphs: dup -> principal
DUPS = {'KBo 19.111': 'KBo 19.109a', 'KUB 14.10+': 'KBo 55.25+', 'KUB 14.8': 'KBo 55.25+',
        'KBo 6.26': 'KBo 25.85+', 'KUB 29.34+': 'KBo 25.85+', 'KUB 26.31+': 'KUB 13.4'}

def analyses(at):
    out = {}
    for k, v in at.items():
        m = re.fullmatch(r'mrp(\d+)', k)
        if m and m.group(1) != '0' and '@' in v:
            p = v.split('@')
            out[m.group(1)] = (p[0].strip(), p[1].strip() if len(p) > 1 else '')
    return out

def classify(at):
    an = analyses(at)
    raw_sel = at.get('mrp0sel', '').strip()
    sel = re.findall(r'\d+', raw_sel)
    tr = at.get('trans', '')
    res = {}
    if raw_sel in FOREIGN:  # word tagged as Akkadian/Hurrian/Hattic/Sumerian/Luwian etc.
        if tr.startswith(('Ù-TUM', 'Ù-TI', 'MA.MÚ')):
            res['dreamlogo'] = 'spell'
        return res
    if cat_logo(tr):
        res['dreamlogo'] = 'spell'
    for cat in CATS:
        if cat in res:
            continue
        hit = [n for n, (lem, gl) in an.items() if in_cat(cat, lem, gl)]
        if not an:
            if cat in SPELL and SPELL[cat].search(tr):
                res[cat] = 'spell'
            continue
        if not hit:
            continue
        if sel:
            res[cat] = 'sel' if set(sel) & set(hit) else 'rej'
        else:
            res[cat] = 'only' if len(hit) == len(an) else 'amb'
    return res

COUNTED = {'sel', 'only', 'spell'}

def paragraphs(path):
    s = open(path, encoding='utf-8').read()
    doc = re.search(r'<docID>(.*?)</docID>', s)
    doc = doc.group(1) if doc else os.path.basename(path)
    cur, lnr, pi = [], '', 0
    for m in TOK.finditer(s):
        if m.group(0).startswith('<lb'):
            lnr = dict(ATT.findall(m.group(1))).get('lnr', '')
        elif m.group(0).startswith('<parsep'):
            if cur:
                yield doc, pi, cur
            cur, pi = [], pi + 1
        else:
            at = dict(ATT.findall(m.group(2)))
            disp = TAG.sub('', m.group(3)).strip()
            if not disp:
                continue
            cur.append({'lnr': lnr, 'trans': at.get('trans', ''), 'disp': disp, 'cls': classify(at),
                        'an': analyses(at), 'sel': at.get('mrp0sel', '').strip()})
    if cur:
        yield doc, pi, cur

def load_vetting(path):
    """JSONL of {doc, lnr, trans, cat, verdict: 'yes'|'no', note}. Overrides auto status."""
    v = {}
    if path and os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            if line.strip():
                r = json.loads(line)
                v[(r['doc'], r['lnr'], r['trans'], r['cat'])] = r['verdict'] == 'yes'
    return v

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='raw/daughters/hittite-tlhdig/extract')
    ap.add_argument('--vetting', default='data/research/knee-sleep/testB-vetting.jsonl')
    ap.add_argument('--cands')
    ap.add_argument('--summary')
    ap.add_argument('--rows', help='JSONL, one row per read paragraph')
    ap.add_argument('--notes', default='data/research/knee-sleep/testB-paragraph-notes.jsonl')
    a = ap.parse_args()
    vet = load_vetting(a.vetting)
    files = sorted(glob.glob(a.root + '/**/*.xml', recursive=True), key=lambda f: ('CTH 999' in f, f))
    tok_status = collections.Counter()
    n_par = 0
    rows = []  # per paragraph flags
    plen = []  # word counts of sleep paragraphs
    cands = []
    seen_ids, skipped = set(), []
    for f in files:
        # TLHdig ships some tablets twice (e.g. a copy under CTH 999_XML_TLH/TLH/); keep one per docID
        m = re.search(r'<docID>(.*?)</docID>', open(f, encoding='utf-8').read(4000))
        did = m.group(1) if m else f
        if did in seen_ids:
            skipped.append(f)
            continue
        seen_ids.add(did)
        cth = os.path.basename(os.path.dirname(f)).split('_')[0]
        for doc, pi, ws in paragraphs(f):
            n_par += 1
            flags = collections.defaultdict(set)  # cat -> statuses present
            for w in ws:
                for cat, st in w['cls'].items():
                    key = (doc, w['lnr'], w['trans'], cat)
                    if key in vet:
                        st = 'vet-yes' if vet[key] else 'vet-no'
                    w['cls'][cat] = st
                    tok_status[(cat, st)] += 1
                    flags[cat].add(st)
            got = {c: bool(flags[c] & (COUNTED | {'vet-yes'})) for c in CATS}
            amb = {c: bool(flags[c] & {'amb'}) for c in CATS}
            rows.append((doc, pi, got, amb))
            if got['ses'] or got['swep']:
                plen.append(len(ws))
            sleepish = got['ses'] or got['swep'] or amb['swep'] or amb['ses']
            other = any(got[c] or amb[c] for c in ('knee', 'kneecloth', 'dream', 'dreamlogo'))
            if (sleepish and other) or got['swep'] or amb['swep'] or 'vet-no' in flags['swep']:
                cands.append({'doc': doc, 'cth': cth, 'par': pi,
                              'lines': f"{ws[0]['lnr']}–{ws[-1]['lnr']}",
                              'flags': {c: sorted(flags[c]) for c in CATS if flags[c]},
                              'hits': [{'lnr': w['lnr'], 'trans': w['trans'], 'disp': w['disp'], 'cls': w['cls'],
                                        'an': {k: f'{l}@{g}' for k, (l, g) in w['an'].items()
                                               if any(in_cat(c, l, g) for c in CATS)}, 'sel': w['sel']}
                                       for w in ws if w['cls']],
                              'text': ' '.join(('|' + w['lnr'] + '| ' if i == 0 or ws[i - 1]['lnr'] != w['lnr'] else '')
                                               + w['disp'] for i, w in enumerate(ws))})
    # --- tables
    def table(feature, variant='main'):
        t = collections.Counter()
        for doc, pi, got, amb in rows:
            if variant == 'dedup' and doc in DUPS:
                continue
            s, w = got['ses'], got['swep']
            if variant == 'ses_amb':
                s = s or amb['ses']
            grp = 'both' if s and w else 'swep' if w else 'ses' if s else None
            if grp:
                t[(grp, feature(got))] += 1
        return t
    feats = {
        'knee': lambda g: g['knee'],
        'dream_strict': lambda g: g['dream'],
        'dream_broad': lambda g: g['dream'] or g['dreamlogo'],
        'knee_or_dream_strict': lambda g: g['knee'] or g['dream'],
        'knee_or_dream_broad': lambda g: g['knee'] or g['dream'] or g['dreamlogo'],
        'kneecloth': lambda g: g['kneecloth'],
        'tesha_only': lambda g: g['tesha'],
        'zashai_only': lambda g: g['zashai'],
    }
    plen.sort()
    out = {'tablets': len(files), 'tablets_skipped_duplicate_docID': len(skipped), 'paragraphs': n_par,
           'sleep_paragraph_words': {'n': len(plen), 'median': plen[len(plen) // 2], 'max': plen[-1]},
           'token_status': {f'{c}:{s}': n for (c, s), n in sorted(tok_status.items())}, 'tables': {}}
    for name, fn, variant in [(n, f, v) for v in ('main', 'dedup', 'ses_amb') for n, f in feats.items()]:
        if variant != 'main' and name not in ('knee', 'dream_strict', 'knee_or_dream_strict', 'knee_or_dream_broad'):
            continue
        name = name if variant == 'main' else f'{name}__{variant}'
        t = table(fn, variant)
        rec = {g: {'with': t[(g, True)], 'without': t[(g, False)]} for g in ('swep', 'ses', 'both')}
        # Fisher on exclusive groups; and with 'both' paragraphs counted in each group
        a_, b_ = rec['swep']['with'], rec['swep']['without']
        c_, d_ = rec['ses']['with'], rec['ses']['without']
        rec['fisher_exclusive'] = {'p_one_sided': fisher_greater(a_, b_, c_, d_), 'or': odds_ratio(a_, b_, c_, d_)}
        A, B = a_ + rec['both']['with'], b_ + rec['both']['without']
        C, D = c_ + rec['both']['with'], d_ + rec['both']['without']
        rec['fisher_both_in_each'] = {'p_one_sided': fisher_greater(A, B, C, D), 'or': odds_ratio(A, B, C, D),
                                      'table': [[A, B], [C, D]]}
        out['tables'][name] = rec
    if a.rows:
        notes = {}
        if os.path.exists(a.notes):
            for line in open(a.notes, encoding='utf-8'):
                if line.strip():
                    r = json.loads(line); notes[(r['doc'], r.get('lines'))] = r
        vnotes = {}
        if a.vetting and os.path.exists(a.vetting):
            for line in open(a.vetting, encoding='utf-8'):
                if line.strip():
                    r = json.loads(line); vnotes[(r['doc'], r['lnr'], r['trans'], r['cat'])] = r
        good = COUNTED | {'vet-yes'}
        with open(a.rows, 'w', encoding='utf-8') as fh:
            for c in cands:
                fl = {k: set(v) for k, v in c['flags'].items()}
                sleep = bool((fl.get('ses', set()) | fl.get('swep', set())) & good)
                other = any(fl.get(k, set()) & (good | {'amb'}) for k in ('knee', 'kneecloth', 'dream', 'dreamlogo'))
                swep_read = bool(fl.get('swep', set()) & (good | {'vet-no'}))
                swep_amb_ctx = bool(fl.get('swep', set()) & {'amb'}) and other
                if not ((sleep and other) or swep_read or swep_amb_ctx):
                    continue
                n = notes.get((c['doc'], c['lines'])) or notes.get((c['doc'], None), {})
                if not n:
                    amb_only = [h['disp'] for h in c['hits'] if 'amb' in h['cls'].values()]
                    n = {'note': 'read; ambiguous words not counted (šupp- here = šuppi- "pure" / šuppa "meat"; bare Ù = '
                                 'Akkadian u "and"): ' + ', '.join(amb_only[:8])} if amb_only else {}
                row = {'doc': c['doc'], 'cth': c['cth'], 'lines': c['lines'],
                       'groups': {'swep': bool(fl.get('swep', set()) & good), 'ses': bool(fl.get('ses', set()) & good)},
                       'features': {k: bool(fl.get(k, set()) & good) for k in ('knee', 'tesha', 'zashai', 'dreamlogo', 'kneecloth')},
                       'words': [{'lnr': h['lnr'], 'form': h['disp'], 'status': h['cls'], 'analyses': h['an'], 'sel': h['sel'],
                                  'vetting': [vnotes[k]['note'] for k in ((c['doc'], h['lnr'], h['trans'], cat) for cat in h['cls'])
                                              if k in vnotes]}
                                 for h in c['hits'] if set(h['cls']) & {'ses', 'swep', 'knee', 'kneecloth', 'tesha', 'zashai', 'dreamlogo'}
                                 and set(h['cls'].values()) - {'rej'}],
                       'target_relation': n.get('target', 'not-target' if (sleep and other) else 'n/a (no knee/dream word)'),
                       'note': n.get('note', ''), 'text': c['text'][:1500]}
                fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    if a.summary:
        json.dump(out, open(a.summary, 'w'), ensure_ascii=False, indent=1, default=str)
    if a.cands:
        with open(a.cands, 'w', encoding='utf-8') as fh:
            for c in cands:
                fh.write(json.dumps(c, ensure_ascii=False) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))

if __name__ == '__main__':
    main()
