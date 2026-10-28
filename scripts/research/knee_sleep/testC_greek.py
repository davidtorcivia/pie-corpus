#!/usr/bin/env python3
"""Test C (knee-sleep pre-registration): Greek *swep- (ὕπνος/ὑπνόω) share in knee+sleep units
against its base rate among all sleep units. Reads the prebuilt search index
data/research/8c/search-index/corpora.sqlite (corpora hom / grc / grc-late) read-only.

Unit = one index unit (Homer: one verse line; GLAUx corpora: one verse line for verse, one
sentence for prose, i.e. loci with " sN"). The pre-registered rule is "a sleep word within the
unit". Because verse units are single lines, a second, documented pass also uses a window of
+-WINDOW neighbouring units in the same book for verse-line units (prose sentences stay +-0).

Lexemes (registered, simplex; lemma-spelling variants of the same lexeme folded in):
  swep: ὕπνος (+ mis-lemma ὕπνον), ὑπνόω (+ epic ὑπνώω, and ὑπνάω, the lemma Homeric ὑπνώοντας gets)
  other: εὕδω, καθεύδω, κοιμάω (+ κοιμάομαι/κοιμώομαι), ἰαύω, δαρθάνω
Compounds (καταδαρθάνω, κατακοιμάω, συγκαθεύδω, ...) count only in the 'compounds'
sensitivity, mapped to their simplex. ὑπνώσσω and other *swep- derivatives are not counted.

Lemmatization gap handled here: in the GLAUx corpora (grc, grc-late) elided tokens
(γούνατ’, εὕδοντ’, κοιμᾶσθ’ ...) are missing from the unit's word list, so they have no lemma.
Elided tokens are matched by the spelling patterns ELIDED below.

Outputs: --cands JSONL of every knee unit (or window) with a sleep word, for reading;
--summary JSON with base rates and the audit of unlemmatized stem matches.
"""
import argparse, collections, json, os, re, sqlite3, sys, unicodedata, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fisher import fisher_greater, odds_ratio  # noqa: E402,F401

LEX = {
    'ὕπνος': 'ὕπνος', 'ὕπνον': 'ὕπνος', 'ὑπνόω': 'ὑπνόω', 'ὑπνώω': 'ὑπνόω', 'ὑπνάω': 'ὑπνόω',
    'εὕδω': 'εὕδω', 'καθεύδω': 'καθεύδω', 'κοιμάω': 'κοιμάω', 'κοιμάομαι': 'κοιμάω',
    'κοιμώομαι': 'κοιμάω', 'ἰαύω': 'ἰαύω', 'δαρθάνω': 'δαρθάνω',
}
SWEP = {'ὕπνος', 'ὑπνόω'}
COMPOUNDS = {  # sensitivity only
    'καταδαρθάνω': 'δαρθάνω', 'παραδαρθάνω': 'δαρθάνω', 'συγκαταδαρθάνω': 'δαρθάνω',
    'ἀποδαρθάνω': 'δαρθάνω', 'ἐγκαταδαρθάνω': 'δαρθάνω', 'ἐπικαταδαρθάνω': 'δαρθάνω',
    'κατακοιμάω': 'κοιμάω', 'προκοιμάω': 'κοιμάω', 'ἐγκοιμάω': 'κοιμάω', 'ἐκκοιμάω': 'κοιμάω',
    'παρακοιμάω': 'κοιμάω', 'συγκοιμάομαι': 'κοιμάω', 'ἀποκοιμάομαι': 'κοιμάω',
    'ἐγκοιμάομαι': 'κοιμάω', 'ἐπικοιμάομαι': 'κοιμάω', 'παρακοιμάομαι': 'κοιμάω',
    'περικοιμάομαι': 'κοιμάω', 'ἐγκατακοιμάομαι': 'κοιμάω', 'ἐπικατακοιμάομαι': 'κοιμάω',
    'παρακαθεύδω': 'καθεύδω', 'προκαθεύδω': 'καθεύδω', 'συγκαθεύδω': 'καθεύδω',
    'σύν-καθεύδω': 'καθεύδω', 'ἀποκαθεύδω': 'καθεύδω', 'ἐγκαθεύδω': 'καθεύδω',
    'ἐκκαθεύδω': 'καθεύδω', 'ἐπικαθεύδω': 'καθεύδω', 'ὑπερκαθεύδω': 'καθεύδω',
    'συνεύδω': 'εὕδω', 'ἐνεύδω': 'εὕδω',
}
KNEE = {'γόνυ', 'γόνυϊ'}
LEXEMES = ['ὕπνος', 'ὑπνόω', 'εὕδω', 'καθεύδω', 'κοιμάω', 'ἰαύω', 'δαρθάνω']
LAYERS = {'hom': 'Homer', 'grc': 'archaic-classical', 'grc-late': 'later'}
ELISION = '’̓ʼ\''

def strip(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)).lower()

# spelling patterns for elided tokens without a lemma (accent-stripped, lower case)
ELIDED = [
    ('knee', re.compile(r'^(?:γουνατ|γουναθ|γονατ|γονυ)$')),
    ('ὕπνος', re.compile(r'^υπν(?:ον|ος|ου|ω|ε)?$')),
    ('ὑπνόω', re.compile(r'^υπνω(?:σ|ντ|οντ|ουσ)\w*$')),
    ('καθεύδω', re.compile(r'^(?:καθευδ|καθηυδ|εκαθευδ)\w*$')),
    ('εὕδω', re.compile(r'^(?:ευδ(?:ετ|οντ|ονθ|οιτ|ουσ|ειν|ε|ω|ησθ|ησ)|ηυδ(?:ον|ε))$')),
    ('κοιμάω', re.compile(r'^(?:κοιμ(?:α|η|ω)\w*|εκοιμ(?:α|η|ω)\w*|κεκοιμ\w*)$')),
    ('ἰαύω', re.compile(r'^ιαυ(?:ονθ|οντ|ειν|εσκ|ε|ει|ομεν)\w*$')),
    ('δαρθάνω', re.compile(r'^(?:δαρθ|εδαρθ|δραθ|εδραθ)\w*$')),
]
AUDIT_STEM = {
    'swep': re.compile(r'^υπν'),
    'knee': re.compile(r'^(?:γονυ|γουνατ|γουναθ|γονατ|γουνασ)'),
    'other': re.compile(r'^(?:ευδ(?!αιμ|ηλ|οκ|οξ|ημ|ι|ωρ|ικ|ρομ|αμ|μητ|ειελ|ενδρ)|ηυδ(?!α)|καθευδ|καθηυδ|εκαθευδ|κοιμ|εκοιμ|κεκοιμ|ιαυ|δαρθ|εδαρθ|δραθ|εδραθ)'),
}
TOKEN = re.compile(r'([^\W\d_]+)([' + ELISION + r']?)', re.U)

def is_sentence(locus):
    return bool(re.search(r' s\d+', locus))

def analyse(rec):
    """-> (simplex lexemes, compound-sensitivity lexemes, knee forms, sleep forms, unlemmatized stem hits)"""
    lx_s, lx_c, knee, sleep, audit = set(), set(), [], [], []
    forms = {}
    for w in rec['words']:
        forms.setdefault(strip(w['form']), w['lemma'])
        l = w['lemma']
        if l in LEX:
            lx_s.add(LEX[l]); lx_c.add(LEX[l]); sleep.append((w['form'], l))
        elif l in COMPOUNDS:
            lx_c.add(COMPOUNDS[l]); sleep.append((w['form'], l))
        if l in KNEE:
            knee.append(w['form'])
    for m in TOKEN.finditer(rec['text']):
        tok, el = m.group(1), m.group(2)
        st = strip(tok)
        if st in forms:
            continue
        if el:
            for cat, rx in ELIDED:
                if rx.match(st) and not (cat == 'knee' and tok[0].isupper()):
                    if cat == 'knee':
                        knee.append(tok + el)
                    else:
                        lx_s.add(cat); lx_c.add(cat); sleep.append((tok + el, cat + ' (elided, by spelling)'))
                    break
        for fam, rx in AUDIT_STEM.items():
            if rx.match(st):
                audit.append((fam, st, bool(el)))
    return lx_s, lx_c, knee, sleep, audit

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default='data/research/8c/search-index/corpora.sqlite')
    ap.add_argument('--window', type=int, default=2)
    ap.add_argument('--read-window', type=int, default=5, help='wider window, read only (not tested)')
    ap.add_argument('--rows', help='JSONL, one row per read knee unit')
    ap.add_argument('--cands'); ap.add_argument('--summary')
    ap.add_argument('--vetting', default='data/research/knee-sleep/testC-vetting.jsonl')
    a = ap.parse_args()
    db = sqlite3.connect(f'file:{a.db}?mode=ro', uri=True)
    corp = tuple(LAYERS)
    info = {}  # id -> record summary for sleep or knee units
    base = {v: {c: collections.Counter() for c in corp} for v in ('simplex', 'compounds')}
    nsleep = {v: collections.Counter() for v in base}
    audit = collections.Counter(); audit_ex = {}
    elided_added = collections.Counter()
    for uid, corpus, book, ordinal, payload in db.execute(
            'select id,corpus,book,ordinal,payload from units where corpus in (?,?,?)', corp):
        rec = json.loads(zlib.decompress(payload))
        lx_s, lx_c, knee, sleep, au = analyse(rec)
        for fam, st, el in au:
            audit[(fam, corpus, st, el)] += 1
            audit_ex.setdefault((fam, corpus, st, el), f"{rec['locus']}")
        for f, l in sleep:
            if 'elided' in l:
                elided_added[(corpus, l.split()[0])] += 1
        for f in knee:
            if f[-1] in ELISION and corpus != 'hom':
                elided_added[(corpus, 'γόνυ')] += 1
        for l in lx_s:
            base['simplex'][corpus][l] += 1
        for l in lx_c:
            base['compounds'][corpus][l] += 1
        if lx_s: nsleep['simplex'][corpus] += 1
        if lx_c: nsleep['compounds'][corpus] += 1
        if lx_c or knee:
            info[uid] = {'id': uid, 'corpus': corpus, 'book': book, 'ordinal': ordinal, 'locus': rec['locus'],
                         'text': rec['text'], 'lx_s': sorted(lx_s), 'lx_c': sorted(lx_c), 'knee': knee,
                         'sleep': sleep, 'genre': rec.get('genre'), 'date_from': rec.get('date_from'),
                         'layer_status': rec.get('layer_status')}
    def window(u, k):
        if k == 0 or is_sentence(u['locus']):
            return [u]
        ids = [r[0] for r in db.execute('select id from units where corpus=? and book=? and ordinal between ? and ? '
                                        'order by ordinal', (u['corpus'], u['book'], u['ordinal'] - k, u['ordinal'] + k))]
        out = []
        for i in ids:
            if i in info:
                out.append(info[i])
            else:
                r = db.execute('select payload from units where id=?', (i,)).fetchone()
                rec = json.loads(zlib.decompress(r[0]))
                out.append({'id': i, 'locus': rec['locus'], 'text': rec['text'], 'lx_s': [], 'lx_c': [],
                            'knee': [], 'sleep': []})
        # do not cross a poem boundary inside one book (e.g. epigram 7.170 -> 7.267)
        poem = lambda loc: re.sub(r'[\s.]\d+[a-z]?$', '', loc)
        return [r for r in out if poem(r['locus']) == poem(u['locus'])]
    cands = []
    for u in sorted((u for u in info.values() if u['knee']), key=lambda u: u['id']):
        for k, mode in ((0, 'unit'), (a.window, 'window'), (a.read_window, 'read-window')):
            ctx = window(u, k)
            lx_s = sorted(set().union(*(set(r['lx_s']) for r in ctx)))
            lx_c = sorted(set().union(*(set(r['lx_c']) for r in ctx)))
            if lx_c:
                cands.append({'mode': mode, 'corpus': u['corpus'], 'layer': LAYERS[u['corpus']], 'knee_unit': u['id'],
                              'locus': u['locus'], 'loci': [r['locus'] for r in ctx], 'unit_ids': [r['id'] for r in ctx],
                              'knee_forms': u['knee'], 'lexemes_simplex': lx_s, 'lexemes_compounds': lx_c,
                              'sleep_forms': [(r['locus'], f, l) for r in ctx for f, l in r['sleep']],
                              'text': ' / '.join(r['text'] for r in ctx), 'genre': u['genre'],
                              'date_from': u['date_from'], 'layer_status': u['layer_status']})
    out = {'units_by_corpus': dict(db.execute('select corpus,count(*) from units where corpus in (?,?,?) group by corpus',
                                              corp).fetchall()),
           'sleep_units': {v: dict(nsleep[v]) for v in nsleep},
           'knee_units': collections.Counter(u['corpus'] for u in info.values() if u['knee']),
           'base': {v: {c: dict(base[v][c]) for c in corp} for v in base},
           'elided_added': {f'{c}:{l}': n for (c, l), n in sorted(elided_added.items())},
           'cands': collections.Counter(c['mode'] for c in cands),
           'audit_unlemmatized': [{'family': f, 'corpus': c, 'form': s, 'elided': e, 'n': n, 'example': audit_ex[(f, c, s, e)]}
                                  for (f, c, s, e), n in audit.most_common()]}
    # ---- classification (read by hand) and Fisher tests
    vet = {}
    if a.vetting and os.path.exists(a.vetting):
        for line in open(a.vetting, encoding='utf-8'):
            if line.strip():
                r = json.loads(line); vet[r['locus']] = r
    for c in cands:
        c['class'] = vet.get(c['locus'], {}).get('class', 'UNREAD')
        c['note'] = vet.get(c['locus'], {}).get('note', '')
    tot = collections.Counter()
    for cc in corp:
        tot.update(base['simplex'][cc])
    nunits = sum(nsleep['simplex'].values())
    swep_units = 0
    for uid, u in info.items():
        if set(u['lx_s']) & SWEP:
            swep_units += 1
    out['base_pooled'] = {'lexeme_units': dict(tot), 'swep_share': sum(tot[l] for l in SWEP) / sum(tot.values()),
                          'sleep_units': nunits, 'units_with_swep': swep_units}
    out['base_share_by_layer'] = {cc: {l: round(base['simplex'][cc].get(l, 0) / max(1, sum(base['simplex'][cc].values())), 3)
                                       for l in LEXEMES} for cc in corp}
    tests = {}
    for mode in ('unit', 'window'):
        for label, classes in (('positives', {'positive'}), ('positives_strict', {'positive-strict'}),
                               ('positives+near', {'positive', 'near-contrast'})):
            pos = [c for c in cands if c['mode'] == mode and c['class'] in classes]
            if label == 'positives_strict':  # drop the borderline Hymn to Demeter item
                pos = [c for c in cands if c['mode'] == mode and c['class'] == 'positive'
                       and 'Cererem' not in c['locus']]
            lx = collections.Counter(l for c in pos for l in c['lexemes_simplex'])
            a_ = sum(lx[l] for l in SWEP); b_ = sum(lx.values()) - a_
            c_ = sum(tot[l] for l in SWEP) - a_; d_ = sum(tot.values()) - sum(tot[l] for l in SWEP) - b_
            ua = sum(1 for c in pos if set(c['lexemes_simplex']) & SWEP); ub = len(pos) - ua
            uc = swep_units - ua; ud = nunits - swep_units - ub
            tests[f'{mode}:{label}'] = {
                'loci': [c['locus'] for c in pos], 'lexemes': dict(lx),
                'ruleA_lexeme_occurrences': {'table': [[a_, b_], [c_, d_]], 'p_one_sided': fisher_greater(a_, b_, c_, d_)},
                'ruleB_units_with_swep': {'table': [[ua, ub], [uc, ud]], 'p_one_sided': fisher_greater(ua, ub, uc, ud)}}
    out['tests'] = tests
    if a.rows:
        by = {}
        for c in cands:
            r = by.setdefault(c['locus'], {'locus': c['locus'], 'corpus': c['corpus'], 'layer': c['layer'],
                                           'genre': c['genre'], 'date_from': c['date_from'],
                                           'layer_status': c['layer_status'], 'found_in': [],
                                           'knee_forms': c['knee_forms'], 'class': c['class'], 'note': c['note']})
            r['found_in'].append(c['mode'])
            r['sleep_forms'] = c['sleep_forms']; r['lexemes_simplex'] = c['lexemes_simplex']
            r['lexemes_compounds'] = c['lexemes_compounds']; r['loci'] = c['loci']; r['text'] = c['text']
        with open(a.rows, 'w', encoding='utf-8') as fh:
            for r in by.values():
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    if a.cands:
        with open(a.cands, 'w', encoding='utf-8') as fh:
            for c in cands:
                fh.write(json.dumps(c, ensure_ascii=False) + '\n')
    if a.summary:
        json.dump(out, open(a.summary, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'audit_unlemmatized'}, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
