# LIV² transcription audit against page images

Date: 2026-10-23. Scope: 22 sampled DjVu pages (78, 89, 153, 169, 190, 191, 280, 298, 311, 328, 367, 401, 455, 481, 484, 495, 546, 568, 604, 626, 664, 674), checked against `data/lexicon/liv2.jsonl`. For each page I read the image first, then compared every record with `page.djvu` equal to that page, including stems that run onto the next page. Doubtful diacritics were checked on enlarged crops. Where a discrepancy looked systematic, I traced it back to the raw chunks (`raw/books/extract/liv2/chunk-NN.jsonl`) and to `scripts/build_liv.py` / `pie/liv.py`, then scanned the whole corpus for it.

## Summary

| | count | rate |
|---|---|---|
| Pages checked | 22 (2 have no headword: 546 is a continuation page; 495 has one headword that the build dropped) | |
| Headwords printed on those pages | 41 | |
| Records checked | 39 (41 minus 2 dropped by the build) | |
| Stem rows checked | 100 | |

**Serious errors** (wrong segment, wrong first-stem label, missed entry, wrong gloss sense):

| Category | Count | Rate |
|---|---|---|
| Missed entry (absent from liv2.jsonl) | 2 | 2/41 = 4.9 %. Both caused by the build, not the transcribers. |
| Headword segment error (root changes) | 2 | 2/41 = 4.9 %. Both on p. 674, chunk-11. |
| Spurious homograph number | 2 | 2/41 = 4.9 %. Both on p. 664, chunk-11. |
| Stem form segment error | 12 stems in 5 entries | 12/100 stems. 8 are on p. 674. |
| Wrong first-stem label | 0 | 0 % |
| Missing or extra main stem | 0 | 0 % |
| German gloss wrong | 0 | 0 % |
| English gloss mistranslates | 0 | 0 % |
| IEW reference wrong | 0 | 0 % |

**Minor errors:**

| Category | Count | Rate |
|---|---|---|
| Length mark dropped in a stem | 3 stems | 3/100 |
| Uncertain-palatal mark `ʼ` dropped (headword and stems) | 3 entries | 3/39 |
| Stem `uncertain` flag true with no `?` printed | 7 stems | 7/100 |
| Stem order different from page | 0 | 0 % |

Every serious error traces back to one of two sources: the build script (the 2 missed entries) or chunk-11, which covers pp. 659–705 (the arc and homograph errors). The other 10 chunks (01–10, two sampled pages each) had no serious errors apart from three added syllabic rings. Labels, stem order, glosses and IEW numbers were correct on every sampled page.

## Error list

| Page | Headword | Field | Record says | Page says | Severity |
|---|---|---|---|---|---|
| 191 | ?*g⁽ʷ⁾eRĝʰ- 'klagen' IEW 350-1 | entry | absent | entry with 2 Präsens stems | Serious (missed). Correct in chunk-03; dropped by `build_liv.py` because `headword()` returns None for capital placeholders (R). |
| 495 | *preK- 'sich fürchten' IEW 820 | entry | absent | entry with Präsens *pr̥K-sk̑é- | Serious (missed). Correct in chunk-08; dropped for the same reason (K). |
| 664 | *u̯edʰh₁- | headword / homograph | `1.*u̯edʰh₁-`, homograph 1 | `*u̯edʰh₁-¹`: the ¹ is a footnote marker, and there is no 2.*u̯edʰh₁- | Serious (homograph) |
| 664 | *u̯eĝ- | headword / homograph | `1.*u̯eĝ-`, homograph 1 | `*u̯eĝ-¹` (footnote marker) | Serious (homograph) |
| 674 | ?1.*u̯ei̯k- | headword / root | `?1.*u̯eik-` → root `weik-` | ?1.*u̯ei̯k- (root weyk-) | Serious (segment) |
| 674 | ?1.*u̯ei̯k- | stems 1–4 | ?*ui-u̯éik/uik-; *ui-né/n-k-; ?*u̯oik-éi̯e-; ?*u̯e-u̯óik/uik- | ?*u̯i-u̯éi̯k/u̯ik-; *u̯i-né/n-k-; ?*u̯oi̯k-éi̯e-; ?*u̯e-u̯ói̯k/u̯ik- | Serious (segment, 4 stems) |
| 674 | 2.*u̯ei̯k- | headword / root | `2.*u̯eik-` → root `weik-` | 2.*u̯ei̯k- (root weyk-) | Serious (segment) |
| 674 | 2.*u̯ei̯k- | stems 1–4 | *u̯éik-/uik-; *ui-né/n-k-; *uik-é-; ?*u̯e-u̯óik/uik- | *u̯éi̯k-/u̯ik-; *u̯i-né/n-k-; *u̯ik-é-; ?*u̯e-u̯ói̯k/u̯ik- | Serious (segment, 4 stems) |
| 664 | *u̯eĝ- | Perfekt | ?*u̯e-u̯óĝ/uĝ- | ?*u̯e-u̯óĝ/u̯ĝ- (arc printed under the zero-grade u) | Serious by definition (segment). Low impact: the record has the linguistically expected form. |
| 190 | *gem- | Aorist, Perfekt | *gém-/gm̥-; ?*ge-góm/gm̥- | *gém-/gm-; ?*ge-góm/gm- (no ring) | Serious by definition (the transcriber added a segment). Low impact. |
| 455 | *nek̑- | Aorist 2 | ?*né-n̥k̑-e- | ?*né-nk̑-e- (no ring) | Serious by definition (segment added). Low impact. |
| 153 | *dʰeu̯H- | Präsens 1 | *dʰéu̯H-/dʰéu̯H- | *dʰḗu̯H-/dʰéu̯H- | Minor (length) |
| 664 | *u̯edʰh₁- | Präsens | *u̯édʰh₁-/u̯édʰh₁- | *u̯ḗdʰh₁-/u̯édʰh₁- | Minor (length) |
| 664 | *u̯edʰh₁- | Iterativ | *u̯ódʰh₁-i̯e- | *u̯ṓdʰh₁-i̯e- | Minor (length) |
| 280 | ?*h₂ĝʼer- | headword, both stems | ?*h₂ĝer-; *h₂ĝér-/h₂ĝr-; *h₂ĝr-éi̯e- | ĝ with the `ʼ` uncertain-series mark throughout | Minor (the root is unchanged; record still uncertain via `uncertain_chars`) |
| 280 | *h₂leĝʼ- | headword, both stems | *h₂leĝ-; *h₂léĝ-e-; *h₂lēĝ/h₂léĝ-s- | ĝʼ throughout | Minor (same) |
| 484 | *peu̯ĝ⁽ʼ⁾- | headword, Präsens | *peu̯ĝ-; *pu-né/n-ĝ- | *peu̯ĝ⁽ʼ⁾-; ?*pu-né/n-ĝ⁽ʼ⁾- | Minor (same) |
| 153 | *dʰeu̯H- | Präsens 1 flag | uncertain: true | no `?` | Minor (flag) |
| 280 | ?*h₂ĝʼer- | Aorist flag | uncertain: true | no `?` | Minor (flag) |
| 280 | *h₂leĝʼ- | s-Aorist flag | uncertain: true | no `?` | Minor (flag) |
| 298 | ?*h₂u̯et- | Präsens flag | uncertain: true | no `?` | Minor (flag) |
| 401 | ?*las- | Präsens flag | uncertain: true | no `?` | Minor (flag) |
| 481 | *pesd- | Präsens 2 flag | uncertain: true | no `?` (the `?` belongs to the Greek reflex) | Minor (flag) |
| 604 | *steu̯- | Präsens 2 flag | uncertain: true | no `?` | Minor (flag) |

Not counted as errors:
- In chunks 05–07, footnote superscripts are kept in `headword_printed` (e.g. `*k̑en-¹`). `normalize` strips them, so this is cosmetic.
- `meaning_de` uses mixed quoting styles: '…', ‘…’ and none.
- The record-level `uncertain` field is sometimes true without a printed `?`, because `build_liv.py` ORs in `uncertain_chars` and the `ʼ`/`⁽ʷ⁾` series. That is intended behaviour, but it means the field does not mean "LIV marks it ?".

Pipeline issues visible on sampled pages. These are not transcription errors, but they change phonemes or keys:
- **p. 367, `k(u̯)` → `kw`.** LIV prints a superscript ⁽ᵘ̯⁾ (optional labialization). The transcribers wrote `k(u̯)`, which `pie/liv.py` does not recognize (it only handles `⁽ᵘ̯⁾`), so `*k⁽ᵘ̯⁾lei̯k̑-` becomes root `kwleyḱ-`, a k+w cluster instead of `kʷ`. The same happens in 23 headwords corpus-wide. In one of them, `*mei̯g(u̯)ʰ-`, the optional element is dropped instead, giving `meygʰ-`.
- **p. 401, root collision.** `*leĝ-` 'sammeln' and `?*leĝ(ʼ)-` 'tröpfeln' both get root `leǵ-` with homograph null, so the two cannot be told apart by root. There are 7 such collisions corpus-wide (`leyǵ-`, `reyǵ-`, `weh₂ǵ-`, `gʷʰer-`, `kʷeyt-`, `tergʷ-`).

## Corpus-wide checks of the systematic patterns

- **Placeholder drop.** 25 real entries are transcribed in the chunks but missing from liv2.jsonl because the headword contains R, K, T or N (a 26th hit is an "entfällt" cross-reference). Their glosses, stems and IEW numbers are usable.
- **Spurious `1.` (chunk-11 only).** 43 records on pp. 659–705 have homograph 1 and no sibling with the same root. I verified 6 on the images (pp. 659 *tu̯enk-, *tu̯er-; 662 *u̯ebʰ-, *u̯ed-; 664 ×2): each time, the ¹ is a footnote marker. Genuine homographs in the range (1./2.*u̯ei̯k-, 1./2./3.*u̯eis-, and so on) do have siblings. One case needs a manual check: `1.*u̯eh₂ĝ-` (p. 668), whose sibling `*u̯eh₂ĝ⁽ʼ⁾-` has homograph null.
- **Missing arc on i̯ (chunk-11 only).** 13 headwords on pp. 669–704 write `ei` for `ei̯`, which produces wrong roots: weid-, weig-, weih₁-, weiḱ-, weik- ×2, weip-, weis- ×3, wleikʷ-, wreiḱ-, wreit-. A crude regex also finds about 36 stems on pp. ≥ 655 with arc-less glides.
- **Dropped macron (all chunks).** 15 stems have two identical halves of the form X/X (e.g. `*déi̯h₂-/déi̯h₂-` on p. 112, `*u̯élh₁-/u̯élh₁-` on p. 682). LIV always prints these as *CḗC-/CéC-. Two were confirmed on the images.

## Verdict

**Roots, aspects and glosses are reliable enough to use outside chunk-11.**
- On the 20 sampled pages from chunks 01–10, every root segment, laryngeal index, velar series, first-stem label, stem order, German gloss, English gloss and IEW reference matched the page.
- Outside chunk-11, the only form-level slips were three added syllabic rings (pp. 190, 455), one dropped length mark (p. 153), three dropped `ʼ` marks (pp. 280, 484), and over-set stem flags.
- The first-stem label was correct in all 39 records, so aspect assignment can be trusted.

Three issues need fixing before the inventory and keys can be trusted:

1. **Re-transcribe chunk-11 (pp. 659–705, ~91 entries).** It has two independent systematic faults: footnote ¹ read as homograph `1.`, and i̯/u̯ arcs dropped, which corrupts root keys (weik- for weyk-). As a stopgap, a script can (a) clear homograph 1 on pages ≥ 659 when there is no sibling with homograph ≥ 2, and (b) add U+032F to i/u next to a vowel in that chunk. Re-reading 47 pages is cheaper and safer than proving the regex right.
2. **Stop dropping placeholder headwords in `build_liv.py`.** Keep the 25 entries with a null or placeholder root and a flag. They carry valid glosses and stems.
3. **Scripted fixes for the other patterns:**
   - Map transcribed `(u̯)` after a velar to `⁽ʷ⁾` before normalizing (23 roots).
   - Disambiguate the 7 root collisions, e.g. by homograph or by a variant suffix.
   - Mark the 15 identical-halves stems as dropped macrons (first half → ḗ, after a quick image check).

The stem `uncertain` flag is unreliable in both directions: 7/100 stems are flagged with no `?` printed. Do not use it for weighting until the flags are re-derived from a `?` in the form string.
