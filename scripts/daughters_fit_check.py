# Fit check for raw/daughters corpora: share of lexicon reflex forms (per language) matching a corpus lemma/form.
# Usage: python3 -I scripts/daughters_fit_check.py data/lexicon/lexicon.jsonl raw/daughters
import sys, os, re, json, glob, unicodedata as ud, collections
LEX, RAW = sys.argv[1], sys.argv[2]
def nfd(s): return ud.normalize('NFD', s)
def nfc(s): return ud.normalize('NFC', s)
def strip_marks(s, marks):
    return nfc(''.join(c for c in nfd(s) if c not in marks))
ACC = {'́', '̀', '͂', '̂'}
LEN = {'̄', '̆'}

def lex_forms(langs, use_roman=True):
    out = collections.defaultdict(set)   # norm-form -> set(lexeme ids)
    nref = 0; ids = set()
    for line in open(LEX, encoding='utf-8'):
        d = json.loads(line)
        for L in langs:
            for r in (d.get('reflexes') or {}).get(L, []):
                f = (r.get('roman') if use_roman and r.get('roman') else r.get('form')) or ''
                nref += 1
                out[f].add(d['id']); ids.add(d['id'])
    return out, nref, ids

def score(name, langs, corpus_counter, norm_lex, norm_corp, use_roman=True):
    lf, nref, ids = lex_forms(langs, use_roman)
    cmap = collections.defaultdict(int)
    for k, v in corpus_counter.items():
        for kk in norm_corp(k):
            if kk: cmap[kk] += v
    matched_forms = 0; matched_ids = set(); total_forms = 0
    lexkeys = {}
    for f, s in lf.items():
        total_forms += 1
        nf = norm_lex(f)
        if nf and nf in cmap:
            matched_forms += 1; matched_ids |= s; lexkeys[nf] = s
    tok = sum(corpus_counter.values())
    covered = sum(v for k, v in corpus_counter.items() if any(kk in lexkeys for kk in norm_corp(k)))
    print(f"{name}: reflex forms {total_forms}, matched {matched_forms} ({100*matched_forms/max(1,total_forms):.0f}%); "
          f"lexemes with reflexes {len(ids)}, matched {len(matched_ids)} ({100*len(matched_ids)/max(1,len(ids)):.0f}%); "
          f"corpus tokens {tok}, covered {100*covered/max(1,tok):.0f}%")

# ---- Rigveda (VedaWeb Zurich lemmas)
def skt(s):
    s = nfd(s).replace('r̥', 'ṛ').replace('l̥', 'ḷ').replace('R̥', 'Ṛ')
    s = re.sub(r'([aeiouṛḷAEIOU\u0304\u0325])[\u0301\u0300]', r'\1', nfd(s))  # accents on vowels only (keep ś)
    s = nfc(s)
    s = re.sub(r'[√*ⁱ0-9\s]', '', s).strip('-').replace('ṁ', 'ṃ').lower()
    return s
rv = collections.Counter()
for fn in glob.glob(RAW + '/rigveda-vedaweb/extract/*/rigveda/TEI/rv_book_*.tei'):
    t = open(fn, encoding='utf-8').read()
    for m in re.finditer(r'<f name="gra_lemma">\s*<string[^>]*>([^<]*)</string>', t):
        rv[m.group(1)] += 1
score('Rigveda', ['Sanskrit', 'Vedic Sanskrit'], rv, skt, lambda k: [skt(p) for p in k.split('~')])

# ---- Homer (AGDT lemmas)
def grk(s):
    s = strip_marks(s, LEN)
    return re.sub(r'[0-9*\-\s]', '', s).lower()
def grk_noacc(s):
    return strip_marks(grk(s), ACC | {'̓', '̔', '̈', 'ͅ'})
hom = collections.Counter()
for fn in glob.glob(RAW + '/homer-perseus-agdt/*.tb.xml'):
    for m in re.finditer(r'<word [^>]*lemma="([^"]*)"[^>]*postag="([^"]*)"', open(fn, encoding='utf-8').read()):
        if not m.group(2).startswith('u'): hom[m.group(1)] += 1
score('Homer (accented)', ['Ancient Greek'], hom, grk, lambda k: [grk(k)], use_roman=False)
score('Homer (unaccented)', ['Ancient Greek'], hom, grk_noacc, lambda k: [grk_noacc(k)], use_roman=False)

# ---- Latin (LASLA)
def lat(s):
    s = strip_marks(s, LEN | ACC).lower().replace('v', 'u').replace('j', 'i')
    return re.sub(r'[0-9*\-\s]', '', s)
la = collections.Counter()
for fn in glob.glob(RAW + '/latin-lasla/conllup/*.conllup'):
    for line in open(fn, encoding='utf-8'):
        p = line.split('\t')
        if len(p) > 3 and p[0].isdigit() and p[3] != 'PUNCT': la[p[2]] += 1
score('Latin (LASLA early)', ['Latin'], la, lat, lambda k: [lat(k)])

# ---- Hittite (TLHdig mrp lemmas)
def hit(s):
    s = re.sub(r'[ᴀ-ᶿ⁰-₟\U00012000-\U0001254F]', '', s)  # modifier/superscript letters, cuneiform
    s = re.sub(r'[=\-*\s0-9]', '', s).lower()
    return s
ht = collections.Counter()
mre = re.compile(r'mrp\d+="[①-⑳]?\s*([^@"]*)@')
for root, _, fs in os.walk(RAW + '/hittite-tlhdig/extract'):
    for f in fs:
        if f.endswith('.xml'):
            t = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
            for wm in re.finditer(r'<w\b([^>]*)>', t):
                lem = set(mre.findall(wm.group(1)))
                for l in lem: ht[l] += 1
def hit_variants(k):
    out = []
    for p in k.split('/'):
        out.append(hit(re.sub(r'\(([^)]*)\)', r'\1', p)))
        out.append(hit(re.sub(r'\([^)]*\)', '', p)))
    return out
def hit_lex(f):
    # syllabic transliteration e-ep-zi -> eepzi is inflected; only stems like 'ardu-' can match
    return hit(f)
score('Hittite (TLHdig lemma candidates)', ['Hittite'], ht, hit_lex, hit_variants)

# ---- Avesta (surface forms, CAB)
def av(s):
    s = s.replace('^', '').replace('ⁱ', 'i').replace('ᵛ', 'v').replace('ϑ', 'θ')
    s = s.replace('aō', 'ao').replace('aē', 'ae')
    return re.sub(r'[+*\-\s.]', '', s).lower()
avc = collections.Counter()
t = open(RAW + '/avesta-cab/CABLinguisticCorpus.xml', encoding='utf-8').read()
for a in re.findall(r'<ab\b[^>]*>(.*?)</ab>', t, re.S):
    for w in re.split(r'[\s.]+', re.sub('<[^>]+>', '', a)):
        if w: avc[w] += 1
score('Avesta (surface forms)', ['Avestan', 'Younger Avestan', 'Old Avestan'], avc, av, lambda k: [av(k)])

# ---- Old Irish UD
def sga(s): return re.sub(r'[*\-\s0-9]', '', s).lower()
oi = collections.Counter()
for fn in glob.glob(RAW + '/oldirish-ud/*/*.conllu'):
    for line in open(fn, encoding='utf-8'):
        p = line.split('\t')
        if len(p) > 3 and p[0].isdigit() and p[3] != 'PUNCT': oi[p[2]] += 1
score('Old Irish (UD lemmas)', ['Old Irish'], oi, sga, lambda k: [sga(k)])

# ---- Old Norse (FJ 1926 surface)
def non(s):
    s = s.lower().replace('ǫ', 'ö').replace('ø', 'ö').replace('ǿ', 'ǿ')
    return re.sub(r'[*\-\s0-9.,;:!?()]', '', s)
on = collections.Counter(w for w in re.findall(r"[^\W\d_]+", open(RAW + '/edda-fj1926/smundareddaeddu00jngoog_djvu.txt', encoding='utf-8').read()))
score('Edda FJ1926 (surface)', ['Old Norse'], on, non, lambda k: [non(k)])

# ---- Old English (Beowulf surface)
def ang(s): return re.sub(r'[*\-\s0-9]', '', strip_marks(s.lower(), LEN | ACC))
oe = collections.Counter(w for w in re.findall(r"[^\W\d_]+", open(RAW + '/oe-beowulf-gutenberg/pg9701.txt', encoding='utf-8').read()))
score('Beowulf H&S (surface, incl. glossary)', ['Old English'], oe, ang, lambda k: [ang(k)])
