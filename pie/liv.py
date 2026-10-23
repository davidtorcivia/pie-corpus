"""Merge LIV² root entries (transcribed from page images) into the lexicon.

Input: raw/books/extract/liv2/chunk-NN.jsonl (one entry per line; see
docs/generation/liv2-brief.md). The transcription is checked against the
PDF's OCR text: the OCR garbles roots but keeps German glosses and IEW
numbers, so an entry whose gloss or IEW number is missing from its page's
OCR is flagged (a transcription slip or an invented entry) and never merged
silently.

Merge policy (decided before the data arrived):
- a LIV root that matches a Wiktionary root (normalized form, accent-
  insensitive; homographs disambiguated by meaning) gets `liv` (page,
  German and English gloss, IEW, stem types) and the aspect of LIV's primary
  stem: the first row of the main block (Präsens → impf, Aorist → pf,
  Perfekt → stat);
- a LIV-only root becomes a new root entry with `source: liv2` and its page;
- Neubildungen (post-PIE formations) never enter the PIE stem inventory.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path

from .notation import normalize
from .translit import is_canonical

ROOT = Path(__file__).resolve().parent.parent
DJVU_TO_PDF = 1          # DjVu page n = PDF page n + 1 (verified on *bʰeh₃g-: d0074 = p0075)
ASPECT = {"Präsens": "impf", "Aorist": "pf", "Perfekt": "stat"}


# DjVu page range each transcription chunk owns (one extra page may be read to
# finish an entry). Entries outside a chunk's range are dropped: one agent's
# append once landed in another chunk's file (chunk-05 lines in chunk-10).
CHUNK_RANGES = {f"chunk-{i:02d}": (lo, hi) for i, (lo, hi) in enumerate(
    [(69, 127), (128, 186), (187, 245), (246, 304), (305, 363), (364, 422), (423, 481), (482, 540),
     (541, 599), (600, 658), (659, 712)], start=1)}


def load_chunks(root: Path = ROOT) -> list[dict]:
    out = []
    for f in sorted((root / "raw/books/extract/liv2").glob("chunk-*.jsonl")):
        lo, hi = CHUNK_RANGES.get(f.stem, (0, 10 ** 6))
        for line in f.read_text("utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if "headword_printed" in d and lo <= int(d.get("djvu_page") or -1) <= hi:
                    d["_chunk"] = f.stem
                    out.append(d)
    return out


PLACEHOLDERS = {"R": ["r", "l", "m", "n"], "K": ["ḱ", "k", "kʷ"], "T": ["t", "d"], "N": ["n", "m"]}


def expand_placeholders(s: str, cap: int = 24) -> list[str]:
    """'bʰRek̂-' → ['bʰrek̂-', 'bʰlek̂-', …]; [] if a capital is not a known placeholder."""
    out = [""]
    for ch in s:
        if ch in PLACEHOLDERS:
            out = [o + x for o in out for x in PLACEHOLDERS[ch]][:cap]
        elif re.match(r"[A-GI-Z]", ch):
            return []
        else:
            out = [o + ch for o in out]
    return out


def headword_alternatives(printed: str) -> list[str]:
    """All canonical forms a placeholder headword stands for (for matching)."""
    s = re.sub(r"^\??\(?\d*\.?\)?\s*\*?", "", printed.strip().lstrip("?")).strip()
    if not re.search(r"[A-GI-Z]", s):
        return []
    out = []
    for a in expand_placeholders(s.replace("(u̯)", "⁽ᵘ̯⁾").replace("(ʼ)", "⁽ʼ⁾")):
        f, _, _ = headword(a)
        if f and f not in out:
            out.append(f)
    return out


def headword(printed: str) -> tuple[str | None, int | None, bool]:
    """'1.*bʰeh₂-' → (canonical 'bʰeh₂-', homograph 1, uncertain)."""
    s = printed.strip()
    unc = s.startswith("?")
    s = s.lstrip("?").strip()
    m = re.match(r"^\(?(\d+)\.\)?\s*", s)
    hom = int(m[1]) if m else None
    s = s[m.end():] if m else s
    s = s.lstrip("*").strip()
    # transcribers sometimes wrote the raised optional elements on the line: k(u̯) = k⁽ᵘ̯⁾, ĝ(ʼ) = ĝ⁽ʼ⁾
    s = re.sub(r"([kgĝk̑ḱǵ]\u0311?ʰ?)\(u\u032f\)", r"\1⁽ᵘ̯⁾", s).replace("(ʼ)", "⁽ʼ⁾")
    # LIV's capital placeholders (R a resonant, K a tectal of unknown series, T a dental,
    # N a nasal) are expanded: the first expansion is the form, and the root is uncertain
    if re.search(r"[A-GI-Z]", s):
        alts = expand_placeholders(s)
        if not alts:
            return None, hom, unc
        s, unc = alts[0], True
    # LIV's uncertain series: g⁽ᵘ̯⁾ = g or gʷ (optional labialization); ĝ⁽ʼ⁾ = uncertain
    # palatal (the palatal is kept as primary). Both mark the root uncertain.
    if "⁽ᵘ̯⁾" in s or "⁽ʼ⁾" in s or re.search("[ĝk̑g̑ḱǵ]\u0311?[ʼ']", s):
        unc = True
        s = s.replace("⁽ᵘ̯⁾", "⁽ʷ⁾").replace("⁽ʼ⁾", "")
        s = re.sub("([ĝk̑g̑ḱǵ]\u0311?)[ʼ']", r"\1", s)   # bare ʼ after a palatal: the same uncertain series
    # optional elements (⁽ʰ⁾, (s)) expand to variants, as in the Wiktionary builder; the full form wins
    from .lexicon import _expand_optional
    for v in _expand_optional(normalize(s, "liv2").text)[0]:
        if is_canonical(v):
            return v, hom, unc
    return None, hom, unc


def _plain(f: str) -> str:
    """The form without accents. U+0301 is also the palatal mark of ḱ/ǵ (k/g + U+0301 in NFD),
    which is kept: ḱel- and kel- are different roots."""
    d = unicodedata.normalize("NFD", f)
    return unicodedata.normalize("NFC", re.sub("(?<![kg])́", "", d))


def _depal(f: str) -> str:
    """The form without accents and palatal marks (ḱel- = kel-): the sources disagree on the
    series of some roots (LIV *teh₂ĝ⁽ʼ⁾- = Wiktionary teh₂g- 'touch'), so a match on this key is
    accepted only when the glosses agree too."""
    d = unicodedata.normalize("NFD", f)
    return unicodedata.normalize("NFC", d.replace("́", ""))


def ocr_check(e: dict, root: Path = ROOT) -> dict:
    """Does the page's OCR text contain the transcribed German gloss and IEW number?"""
    pdf_page = int(e["djvu_page"]) + DJVU_TO_PDF
    texts = []
    for p in (pdf_page - 1, pdf_page, pdf_page + 1):
        f = root / f"raw/books/text/liv2/p{p:04d}.txt"
        if f.exists():
            texts.append(f.read_text("utf-8"))
    t = " ".join(texts)
    gloss = (e.get("meaning_de") or "").strip("'‘’ ")
    words = [w for w in re.findall(r"\w{3,}", gloss)]
    gloss_ok = (not words) or sum(w in t for w in words) >= max(1, len(words) // 2)
    iew_ok = True
    if e.get("iew") and re.search(r"\d", e["iew"]):     # "IEW –": no IEW entry, nothing to check
        num = re.findall(r"\d+", e["iew"])
        squeezed = t
        while re.search(r"(\d) (\d)", squeezed):     # the OCR spaces digits out: "IEW 1 1 5"
            squeezed = re.sub(r"(\d) (\d)", r"\1\2", squeezed)
        iew_ok = bool(num) and num[0] in squeezed
    return {"gloss_in_ocr": gloss_ok, "iew_in_ocr": iew_ok}


def _gloss_sim(a: str, b: str) -> float:
    """Word overlap of two English glosses (stopwords and 'to' ignored)."""
    stop = {"to", "the", "a", "be", "of", "and", "or", "in", "up", "out", "make"}
    wa = {w for w in re.findall(r"[a-z]+", a) if w not in stop}
    wb = {w for w in re.findall(r"[a-z]+", b) if w not in stop}
    return len(wa & wb) / max(1, min(len(wa), len(wb))) if wa and wb else 0.0


def merge(lexicon: list[dict], entries: list[dict]) -> tuple[list[dict], dict]:
    """→ (new root entries to add, report). Matched roots are updated in place."""
    from .validate import key as vkey
    roots = [e for e in lexicon if e["kind"] == "root"]
    by_plain: dict[str, list[dict]] = {}
    by_generic: dict[str, list[dict]] = {}
    for r in roots:
        for f in [r["form"], *r.get("variants", [])]:
            by_plain.setdefault(_plain(f), []).append(r)
            by_generic.setdefault(vkey(f, "generic-H"), []).append(r)
    new, report = [], {"entries": len(entries), "matched": 0, "new": 0, "unparsed": [], "ocr_flags": [],
                       "ambiguous": []}
    seen = set()
    for e in entries:
        key = (e.get("headword_printed"), e.get("meaning_de"))
        if key in seen:      # overlap pages: the same entry from two chunks
            continue
        seen.add(key)
        if e.get("see") or (not e.get("stems") and ("entfällt" in json.dumps(e, ensure_ascii=False)
                                                    or not e.get("meaning_de"))):
            report.setdefault("cross_references", []).append(e.get("headword_printed"))
            continue         # "entfällt, s. …": a redirect, not a root
        form, hom, unc = headword(e.get("headword_printed", ""))
        chk = ocr_check(e)
        if not (chk["gloss_in_ocr"] and chk["iew_in_ocr"]):
            report["ocr_flags"].append({"headword": e["headword_printed"], "page": e["djvu_page"], **chk})
        if not form:
            report["unparsed"].append(e.get("headword_printed"))
            continue
        stems = [s for s in e.get("stems", []) if s.get("label")]
        aspect = ASPECT.get(stems[0]["label"]) if stems else None
        liv = {"page_djvu": e["djvu_page"], "printed_page": e.get("printed_page"), "headword": e["headword_printed"],
               "homograph": hom, "uncertain": unc, "meaning_de": e.get("meaning_de"),
               "meaning_en": e.get("meaning_en"), "iew": e.get("iew"),
               "stems": [{"label": s["label"], "form": s.get("form_printed"), "uncertain": s.get("uncertain", False)}
                         for s in stems],
               "neubildungen": e.get("neubildungen", []), "ocr_check": chk}
        cands = by_plain.get(_plain(form), [])
        if not cands:
            # same root written with a different laryngeal index or coloring
            # (LIV bʰeyH- ~ Wiktionary bʰeyh₂-): accept only if the glosses agree too
            en = (e.get("meaning_en") or "").lower()
            g = [r for r in by_generic.get(vkey(form, "generic-H"), [])
                 if r["meaning"] and _gloss_sim(en, r["meaning"][0].lower()) >= 0.35]
            if g:
                cands = g
                liv_match = "generic-H+gloss"
            else:
                liv_match = None
        else:
            liv_match = "form"
        if len(cands) > 1:   # homographs: pick by meaning similarity
            en = (e.get("meaning_en") or "").lower()
            scored = sorted(cands, key=lambda r: -difflib.SequenceMatcher(
                None, en, (r["meaning"][0] if r["meaning"] else "").lower()).ratio())
            if en and scored:
                cands = scored[:1]
            else:
                report["ambiguous"].append(e["headword_printed"])
                cands = cands[:1]
        if cands:
            r = cands[0]
            liv["match"] = liv_match
            r.setdefault("liv", []).append(liv)
            if aspect and (r.get("root_type_source") != "head-template" or not r.get("aspect")):
                r["aspect"], r["root_type"], r["root_type_source"] = aspect, "verbal", "liv2"
            report["matched"] += 1
        else:
            new.append({"form": form, "liv": liv, "aspect": aspect, "meaning": [e.get("meaning_en") or ""],
                        "meaning_de": e.get("meaning_de")})
            report["new"] += 1
    return new, report


_ROOT_AORIST = re.compile(r"^\*([^/?]+?)-?/([^/]+?)-$")


def _aorist_lexemes(entries: dict, targets: list, reg, dump_label: str) -> int:
    """A root aorist lexeme (3sg *bʰéydt, weak stem from LIV) for every certain LIV root
    aorist (*bʰéi̯d-/bʰid-) whose root has no aorist lexeme yet. Sigmatic and reduplicated
    aorists are left out (the engine does not build them)."""
    from .lexicon import slug
    from .translit import to_ascii
    has_aor = {e.get("root_id") for e in entries.values() if e["kind"] != "root" and e.get("aspect") == "pf"}
    aor_forms = {}
    for e in entries.values():
        if e["kind"] != "root" and e.get("aspect") == "pf":
            aor_forms.setdefault(_plain(e["form"]), []).append(e)
    n = 0
    for x, rid in targets:
        if rid in has_aor:
            continue
        st = next((s for s in x.get("stems", []) if (s.get("label") or "").startswith("Aorist")
                   and not s.get("uncertain")), None)
        m = _ROOT_AORIST.match((st or {}).get("form") or "")
        if not m:
            continue
        strong, weak = (normalize(h, "liv2").text for h in m.groups())
        if re.match("h[₁₂₃]|H", strong) and not re.match("h[₁₂₃]|H", weak):
            weak = re.match("h[₁₂₃]|H", strong)[0] + weak        # LIV *h₃péu̯s-/pus-: the weak stem keeps h₃
        form = strong + "t"
        en0 = (x.get("meaning_en") or "").strip("'‘’ ").lower()
        if any(max((_gloss_sim(en0, mm.lower()) for mm in d["meaning"]), default=0) > 0
               for d in aor_forms.get(_plain(form), [])):
            continue                                              # Wiktionary already has this aorist (péh₃t 'drink')
        if not (is_canonical(form) and is_canonical(weak)) or re.search(r"[-()⁽⁾]", strong + weak):
            continue
        en = (x.get("meaning_en") or "").strip("'‘’ ")
        lid = reg.get(f"liv2-aorist|{x['headword_printed']}|{x.get('meaning_de')}", f"pie-lex-{slug(form)}")
        entries[lid] = {
            "id": lid, "kind": "word", "form": form, "form_ascii": to_ascii(form), "variants": [], "stems": [],
            "pos": "verb", "meaning": [en] if en else [], "uncertain": [], "source": "liv2",
            "source_ref": {"dump": dump_label, "page": x["page"], "stem": st["form"]},
            "confidence": "entry", "normalized": [], "aspect": "pf", "aorist_weak": weak, "etymon_parts": [],
            "reflexes": {}, "parents": [rid], "root_link_source": "liv2", "root_id": rid}
        has_aor.add(rid)
        n += 1
    return n


def apply(entries: dict[str, dict], liv_records: list[dict], reg, dump_label: str = "LIV² (Rix et al. 2001)") -> dict:
    """Apply data/lexicon/liv2.jsonl to the lexicon being built (pie.lexicon.build).

    Matched roots get `liv` (a list: homograph pages can match one root) and,
    unless Wiktionary marked the aspect itself, the aspect of LIV's primary
    stem. LIV-only roots become new root entries whose ids come from the
    (frozen) registry, under the key "liv2|<headword>|<German gloss>".
    """
    from .lexicon import gloss_tag, slug
    from .translit import to_ascii
    from .validate import key as vkey
    roots = [e for e in entries.values() if e["kind"] == "root"]
    by_plain, by_generic, by_depal = {}, {}, {}
    for r in roots:
        for f in [r["form"], *r.get("variants", [])]:
            by_plain.setdefault(_plain(f), []).append(r)
            by_generic.setdefault(vkey(f, "generic-H"), []).append(r)
            by_depal.setdefault(_depal(f), []).append(r)
    rep = {"matched_form": 0, "matched_generic": 0, "new": 0}
    targets = []                      # (LIV record, root id) for the aorist lexemes below

    def sim(en, r):                   # gloss overlap against all of a root's senses
        return max((_gloss_sim(en.lower(), m.lower()) for m in r["meaning"]), default=0.0)

    # 1. score every (LIV record, form-matched root) pair: an exact main-form match outranks a
    #    variant match, then gloss overlap; 2. assign one-to-one, best pairs first, so two LIV
    #    homographs never share one Wiktionary root (1./2.*h₂eĝ- 'drive'/'say'; *dʰeh₁- 'put'
    #    must not land on dʰeh₁y- 'suckle' through a variant spelling)
    pairs = []
    for n, x in enumerate(liv_records):
        en = (x.get("meaning_en") or "").strip("'‘’ ")
        forms = [x["root"], *x.get("root_alternatives", [])]
        best = {}
        for f in forms:
            exact_group = by_plain.get(_plain(f), [])
            # the same root with the other tectal series (palatal vs plain velar): a candidate only
            # when the glosses agree (LIV *teh₂ĝ⁽ʼ⁾- = teh₂g- 'touch', but *kleh₁- 'call' ≠ ḱleh₁- 'hot')
            depal = [r for r in by_depal.get(_depal(f), []) if r not in exact_group and sim(en, r) > 0]
            for group, tier in ((exact_group, "exact"), (depal, "depal")):
                verbal = [r for r in group if not r["meaning"] or any(m.startswith("to ") for m in r["meaning"])]
                for r in group:
                    # LIV is a dictionary of verbs: a root glossed only as a thing (h₂eǵ- 'goat') is no candidate
                    # when a verbal root of the same form exists (bʰenǵʰ- 'thick', the only one, still is)
                    if verbal and r not in verbal:
                        continue
                    if tier == "exact":
                        score = (1.0 if _plain(r["form"]) == _plain(x["root"]) else 0.5) + sim(en, r)
                    else:
                        score = 0.25 + sim(en, r)
                    best[r["id"]] = max(best.get(r["id"], 0.0), score)
        pairs.extend((score, n, rid_) for rid_, score in best.items())
    assigned, used = {}, set()
    for score, n, rid_ in sorted(pairs, key=lambda t: -t[0]):
        if n not in assigned and rid_ not in used:
            assigned[n], used_ = rid_, used.add(rid_)
    for n, x in enumerate(liv_records):
        en = (x.get("meaning_en") or "").strip("'‘’ ")
        stems = [s for s in x.get("stems", []) if s.get("label")]
        aspect = ASPECT.get(stems[0]["label"]) if stems else None
        liv = {k: x[k] for k in ("headword_printed", "homograph", "uncertain", "meaning_de", "meaning_en", "iew",
                                  "stems", "neubildungen", "page", "ocr_check")}
        forms = [x["root"], *x.get("root_alternatives", [])]
        cands = [entries[assigned[n]]] if n in assigned else []
        how = "form"
        if not cands:
            how = "generic-H+gloss"
            cands = [r for f in forms for r in by_generic.get(vkey(f, "generic-H"), [])
                     if r["id"] not in used and r["meaning"] and sim(en, r) >= 0.35][:1]
            if cands:
                used.add(cands[0]["id"])
        if cands:
            r = cands[0]
            r.setdefault("liv", []).append({**liv, "match": how})
            if aspect and r.get("root_type_source") != "head-template":
                r["aspect"], r["root_type"], r["root_type_source"] = aspect, "verbal", "liv2"
            rep["matched_form" if how == "form" else "matched_generic"] += 1
            targets.append((x, r["id"]))
            continue
        rid = reg.get(f"liv2|{x['headword_printed']}|{x.get('meaning_de')}",
                      f"pie-root-{slug(x['root'])}-{gloss_tag(en)}")
        entries[rid] = {
            "id": rid, "kind": "root", "form": x["root"], "form_ascii": to_ascii(x["root"]),
            "variants": x.get("root_alternatives", [])[1:],
            "stems": [], "pos": "root", "meaning": [en] if en else [], "meaning_de": x.get("meaning_de"),
            "uncertain": ["liv2-uncertain"] if x.get("uncertain") else [], "source": "liv2",
            "source_ref": {"dump": dump_label, "page": x["page"], "iew": x.get("iew")},
            "confidence": "entry", "normalized": [], "root_type": "verbal", "root_type_source": "liv2",
            "aspect": aspect, "etymon_parts": [], "reflexes": {}, "root_id": rid, "liv": [{**liv, "match": "new"}],
            "has_verb_derivative": False}
        rep["new"] += 1
        targets.append((x, rid))
    rep["aorists"] = _aorist_lexemes(entries, targets, reg, dump_label)
    # A LIV-only root may be a Wiktionary root reconstructed differently (dʰeHbʰ- ~ dʰh₂ebʰ-)
    # or a root LIV deliberately keeps apart (drew- vs dreh₂-). Never merge automatically:
    # link candidates with the same consonant skeleton and a similar gloss.
    def skeleton(f):
        return re.sub(r"[aeiouāēīōū]|H|y|w", "", vkey(f.rstrip("-"), "generic-H"))
    by_skel = {}
    for r in roots:
        by_skel.setdefault(skeleton(r["form"]), []).append(r)
    rep["possible_aliases"] = 0
    for e in entries.values():
        if e.get("source") == "liv2" and e["kind"] == "root":
            al = [r["id"] for r in by_skel.get(skeleton(e["form"]), [])
                  if r["meaning"] and e["meaning"] and _gloss_sim(e["meaning"][0].lower(), r["meaning"][0].lower()) >= 0.34]
            if al:
                e["possible_alias_of"] = al
                rep["possible_aliases"] += 1
    return rep
