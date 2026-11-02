"""Build a PIE speaker file for VocalTractLab from a base speaker.

  python make_speaker.py JD3-PIE.speaker                         # male, classic VTL (pip engine)
  python make_speaker.py W02-PIE.speaker --base W02.speaker      # female, VTL 2.4
  python make_speaker.py M01-PIE.speaker --base M01.speaker      # male, VTL 2.4

Works with both speaker formats (classic "Geometric glottis" and VTL 2.4 "Geometric glottis 2025").
Added on top of the base speaker, then tuned on its own anatomy:

  tb-palatal-closure(a|i|u)       palatal stop [c ɟ]: the palatal fricative, tongue body raised until it
                                  closes ahead of the velar closure
  ll-rounded(a|i|u)               lip rounding [ʷ]: protruded lips, opening 0.3–0.6 cm², no tongue contact
  tt-alveolar-approximant(a|i|u)  [ɹ] for syllabic r̩: alveolar fricative with the tip lowered until the
                                  opening is 0.25–0.45 cm² (no friction)
  glottis "murmur"                breathy voice [ʱ] that keeps vibrating
  glottis "voiceless-uvular"      wide, non-vibrating glottis for χ
  glottis "voiceless-unaspirated" half-open glottis for plain p t k c (short-lag voicing)
  glottis "aspirate"              open, non-vibrating glottis for h (breath noise through the vowel's tract)
"""
import argparse, re, sys
import numpy as np

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("out", nargs="?", default="JD3-PIE.speaker")
ap.add_argument("--base", help="base speaker (default: JD3 from vocaltractlab-cython)")
ap.add_argument("--murmur-mix", type=float, default=0.5,
                help="murmur fold opening: 0 = modal, 1 = voiced-fricative (default halfway)")
ap.add_argument("--murmur-db", type=float, default=-5.0,
                help="level of a held murmured vowel re modal (dB); sets the murmur chink area")
ap.add_argument("--aspiration-db", type=float, default=0.0,
                help="aspiration strength (dB, max 0) for murmur/aspirate; classic glottis only")
a = ap.parse_args()

if a.base is None:
    import vocaltractlab_cython as _v
    a.base = _v.DEFAULT_SPEAKER_PATH
spk = open(a.base, encoding="utf-8").read()
vt = re.search(r"<vocal_tract_model>.*?</vocal_tract_model>", spk, re.S).group(0)


def block(name, text=None):
    m = re.search(r'( *)<shape name="%s">.*?</shape>\n' % re.escape(name), text or vt, re.S)
    if not m: sys.exit("shape not found: " + name)
    return m.group(0)


def params(b):
    return dict(re.findall(r'<param name="([^"]+)" value="([^"]+)"/>', b))


def render(name, p, indent="      "):
    rows = [f'{indent}<shape name="{name}">']
    rows += [f'{indent}  <param name="{k}" value="{float(x):.4f}"/>' for k, x in p.items()]
    return "\n".join(rows + [f"{indent}</shape>\n"])


# ---- vocal tract additions (initial guesses; tuned below on the actual anatomy)
new = []
u = params(block("u"))
for ctx in ("a", "i", "u"):
    p = params(block(f"tb-palatal-fricative({ctx})")); p["TBY"] = str(float(p["TBY"]) + 0.8)
    new.append(render(f"tb-palatal-closure({ctx})", p))
    r = params(block(ctx))
    r["LP"], r["LD"] = u["LP"], "0.55"
    r["JA"] = params(block(f"ll-labial-closure({ctx})"))["JA"]
    new.append(render(f"ll-rounded({ctx})", r))
    q = params(block(f"tt-alveolar-fricative({ctx})")); q["TTY"] = str(float(q["TTY"]) - 0.35)
    new.append(render(f"tt-alveolar-approximant({ctx})", q))
anchor = block("tb-uvular-fricative(u)")
spk = spk.replace(anchor, anchor + "".join(new), 1)

# ---- glottis additions, in whichever geometric model is selected
model = re.search(r'<glottis_model type="(Geometric glottis(?: 2025)?)" selected="1">.*?</glottis_model>', spk, re.S)
if not model: sys.exit("no selected geometric glottis model in the base speaker")
geo, gtype = model.group(0), model.group(1)
ctrl = re.search(r"<control_params>(.*?)</control_params>", geo, re.S).group(1)
if gtype == "Geometric glottis":            # classic: name="XB" ...
    key = {"XB": "XB", "XT": "XT", "CA": "CA", "RA": "RA", "AS": "AS"}
    idx = {n: n for n in key.values()}
    def setp(b, k, x):
        return re.sub(r'(<control_param name="%s" value=")[^"]+' % k, r"\g<1>%.6f" % x, b)
else:                                       # VTL 2.4: index + abbr
    key = {"XB": "x_bottom", "XT": "x_top", "CA": "chink_area", "RA": "rel_amp"}
    idx = {abbr: ix for ix, abbr in re.findall(r'<param index="(\d+)" name="[^"]*" abbr="([^"]+)"', ctrl)}
    def setp(b, k, x):
        return re.sub(r'(<control_param index="%s" value=")[^"]+' % k, r"\g<1>%.6f" % x, b)


def gshape(src_names, new_name, changes):
    for s in src_names:
        m = re.search(r'( *)<shape name="%s">.*?</shape>\n' % re.escape(s), geo, re.S)
        if m: break
    else:
        sys.exit(f"none of {src_names} in the glottis model")
    b = m.group(0).replace(f'name="{s}"', f'name="{new_name}"')
    for k, x in changes.items():
        if k in key and key[k] in idx:
            b = setp(b, idx[key[k]], x)
    return b


def vals(s, keys):
    return dict(zip(keys, (float(x) for x in s.split(","))))


def gvals(name):
    """Current XB/XT/CA/RA of one of the speaker's own glottis shapes."""
    b = re.search(r'( *)<shape name="%s">.*?</shape>\n' % re.escape(name), geo, re.S).group(0)
    if gtype == "Geometric glottis":
        get = lambda k: float(re.search(r'<control_param name="%s" value="([^"]+)"' % k, b).group(1))
    else:
        get = lambda k: float(re.search(r'<control_param index="%s" value="([^"]+)"' % idx[key[k]], b).group(1))
    return {k: get(k) for k in ("XB", "XT", "CA", "RA")}


# PIE glottis settings, defined relative to this speaker's own reference shapes so they carry over
# between glottis models with different scales (JD3: modal XB 0.010, voiceless-plosive 0.10;
# W02 2025 model: modal 0.052, voiceless-plosive 0.23).
modal, vfric = gvals("modal"), gvals("voiced-fricative")
vlfric, vlplos = gvals("voiceless-fricative"), gvals("voiceless-plosive")
mur = {"XB": modal["XB"] + a.murmur_mix * (vfric["XB"] - modal["XB"]),
       "XT": modal["XT"] + a.murmur_mix * (vfric["XT"] - modal["XT"]),
       "CA": min(0.25, max(6 * modal["CA"], 0.15)), "RA": 1.0}
uvu = {"XB": 1.6 * vlfric["XB"], "XT": 1.6 * vlfric["XT"]}
una = {"XB": 0.5 * vlplos["XB"], "XT": 0.5 * vlplos["XT"], "RA": 0.0}   # no vibration, but not pressed (−1)
asp = {"XB": vlfric["XB"], "XT": vlfric["XT"], "CA": 0.15, "RA": 0.0}
if gtype == "Geometric glottis":
    mur["AS"] = asp["AS"] = min(a.aspiration_db, 0.0)
add = (gshape(["breathy", "modal"], "murmur", mur)
       + gshape(["voiceless-fricative"], "voiceless-uvular", uvu)
       + gshape(["voiceless-plosive"], "voiceless-unaspirated", una)
       + gshape(["h"], "aspirate", asp))
glot_report = "  glottis: " + "  ".join(f"{n} XB {d['XB']:.3f}" for n, d in
                                       (("murmur", mur), ("uvular", uvu), ("unaspirated", una), ("aspirate", asp)))
last = list(re.finditer(r'( *)<shape name="[^"]+">.*?</shape>\n', geo, re.S))[-1].group(0)
spk = spk.replace(geo, geo.replace(last, last + add, 1), 1)
open(a.out, "w", encoding="utf-8").write(spk)


# ---- tune the added vocal-tract shapes on this anatomy
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import vtlengine
eng = vtlengine.open_engine(a.out)
order = list(params(block("a")).keys())
text = open(a.out, encoding="utf-8").read()


def put(name, vec):
    global text
    old = re.search(r'( *)<shape name="%s">.*?</shape>\n' % re.escape(name), text, re.S).group(0)
    text = text.replace(old, render(name, dict(zip(order, vec))), 1)


report = []
for ctx in ("a", "i", "u"):
    velar_cl = np.where(eng.tube_area(eng.shape(f"tb-velar-closure({ctx})")) < 0.005)[0]
    velar = int(velar_cl.mean()) if len(velar_cl) else 0
    # palatal stop: a firm closure (≥10% of the tube) at the palatal place, ahead of the velar closure.
    # Method A: raise the tongue body from the palatal fricative. Method B (VTL 2.4, where fricative
    # shapes stay at the 0.15 cm² floor): slide the velar closure forward to the palatal place.
    pal_fric = eng.shape(f"tb-palatal-fricative({ctx})")
    pal_place = int(eng.tube_area(pal_fric).argmin())
    span_min = max(3, int(0.1 * len(eng.tube_area(pal_fric))))
    i_tby, i_tcx = order.index("TBY"), order.index("TCX")
    found = None
    for d in np.arange(0.2, 2.01, 0.05):                                   # method A
        p = pal_fric.copy(); p[i_tby] += d
        cl = np.where(eng.tube_area(p) < 0.005)[0]
        if len(cl) >= span_min and cl.min() > velar:
            found = ("TBY+%.2f" % d, p, cl); break
    if found is None:                                                      # method B
        vel = eng.shape(f"tb-velar-closure({ctx})"); best = None
        for d in np.arange(0.0, 2.51, 0.05):
            p = vel.copy(); p[i_tcx] += d
            cl = np.where(eng.tube_area(p) < 0.005)[0]
            if len(cl) < span_min: continue
            score = abs((cl.min() + cl.max()) / 2 - (pal_place - 2))
            if best is None or score < best[0]: best = (score, d, p, cl)
        if best: found = ("velar TCX+%.2f" % best[1], best[2], best[3])
    if found:
        method, p, cl = found
        put(f"tb-palatal-closure({ctx})", p)
        report.append(f"  tb-palatal-closure({ctx})      {method:16s} closed {cl.min()}-{cl.max()} "
                      f"(velar closure {velar}, palatal fricative {pal_place})")
    else:
        report.append(f"  tb-palatal-closure({ctx})      ⚠ no closure found")

    # approximant: lower the tip until the narrowest front opening is 0.25-0.45 cm²
    base_q = eng.shape(f"tt-alveolar-fricative({ctx})"); i_tty = order.index("TTY")
    fr = int(eng.tube_area(base_q).argmin())
    best = None
    for d in np.arange(0.0, 1.21, 0.02):
        q = base_q.copy(); q[i_tty] -= d
        m = eng.tube_area(q)[fr - 4:fr + 5].min()
        if best is None or abs(m - 0.35) < abs(best[1] - 0.35): best = (d, m, q)
    put(f"tt-alveolar-approximant({ctx})", best[2])
    report.append(f"  tt-alveolar-approximant({ctx}) TTY-{best[0]:.2f}  opening {best[1]:.2f} cm²")

    # rounding: lip opening 0.3-0.6 cm² and nothing else narrower than 0.2 cm²
    r = eng.shape(f"ll-rounded({ctx})"); i_ja, i_ld = order.index("JA"), order.index("LD")
    v = eng.shape(ctx)
    cands = []
    for wja in np.linspace(0, 1, 11):
        for ld in np.arange(0.0, 0.9, 0.05):
            rr = r.copy(); rr[i_ja] = v[i_ja] * (1 - wja) + r[i_ja] * wja; rr[i_ld] = ld
            ar = eng.tube_area(rr)
            lip, rest = ar[-3:].min(), ar[:-4].min()
            ok = 0.3 <= lip <= 0.6 and rest >= 0.2
            cands.append((not ok, abs(lip - 0.45), -wja, rr, lip, rest))
    cands.sort(key=lambda c: c[:3])
    _, _, _, rr, lip, rest = cands[0]
    put(f"ll-rounded({ctx})", rr)
    report.append(f"  ll-rounded({ctx})              lip opening {lip:.2f} cm², elsewhere ≥ {rest:.2f} cm²")

open(a.out, "w", encoding="utf-8").write(text)
eng.close()

# ---- murmur level: the chink (posterior leak) sets how much a murmured vowel loses. Found by
# bisection so a held murmured [aː] sits --murmur-db below modal (VTL 2.4 voices otherwise lose ~16 dB).
import json, os, tempfile
import pie_vtl
tmp = tempfile.mkdtemp()
words = pie_vtl.words_from_text("máː.maː")
timed, total, words = pie_vtl.build_timeline(words, 1.0)
ges = pie_vtl.compile_score(timed, total, words, pie_vtl.speaker_pitch(a.out))
nuc = next((s0, s1) for s0, s1, g in timed if g is not None and pie_vtl.is_nucleus(g))
mid = (nuc[0] + nuc[1]) / 2
body = re.search(r'<gesture_sequence type="glottal-shape-gestures"[^>]*>(.*?)</gesture_sequence>', ges, re.S).group(1)
g_mod, g_mur = os.path.join(tmp, "modal.ges"), os.path.join(tmp, "murmur.ges")
open(g_mod, "w", encoding="utf-8").write(ges)
open(g_mur, "w", encoding="utf-8").write(ges.replace(body, body.replace('value="modal"', 'value="murmur"')))
mblock = re.search(r' *<shape name="murmur">.*?</shape>\n', text, re.S).group(0)
ca_key = idx[key["CA"]]


def level(ca, ges_path):
    b = setp(mblock, ca_key, ca)
    f = os.path.join(tmp, "t.speaker")
    open(f, "w", encoding="utf-8").write(text.replace(mblock, b))
    e = vtlengine.open_engine(f); x = e.ges_to_audio(ges_path); e.close()
    x = x[int((mid - .06) * 44100):int((mid + .06) * 44100)]
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12), b


ref, _ = level(modal["CA"], g_mod)
lo, hi = modal["CA"], 0.25
for _ in range(8):
    ca = (lo + hi) / 2
    lv, b = level(ca, g_mur)
    lo, hi = (ca, hi) if lv - ref > a.murmur_db else (lo, ca)
ca = (lo + hi) / 2
lv, b = level(ca, g_mur)
text = text.replace(mblock, b)
open(a.out, "w", encoding="utf-8").write(text)
report.append(f"  murmur chink area {ca:.3f} (modal {modal['CA']:.3f}): held vowel {lv - ref:+.1f} dB re modal")
print(f"wrote {a.out}  ({gtype}, engine {vtlengine.engine_kind(a.out)})")
print(glot_report)
print("\n".join(report))
