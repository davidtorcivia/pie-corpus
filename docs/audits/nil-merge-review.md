# NIL merge review (adversarial)

Scope: `pie/nil.py` (`stem()`, `citation()`, `apply()`, `_new_lexeme()`) and what it wrote to
`data/lexicon/lexicon.jsonl`. There are two populations:

- **(a)** 159 existing derivatives that had no gloss and took NIL's (`meaning_source: "nil"`, source ≠ nil).
- **(b)** 192 new lexemes (`source: "nil"`). The classifier marked 121 of them usable: thematic-adj 64, thematic 21, s-stem-neuter 14, tor-agent 11, men-neuter 11. The other 71 are unusable: eh₂ 26, -tér- 17, thematic-neuter 12, i/u 10, other 6.

Method: I drew seeded random samples (seed 20261023): 40 from (b) (32 usable, 8 unusable) and 20 from (a). For each item I rendered NOM/ACC/GEN/LOC.SG and NOM.PL with `Lexicon.cells()`. After that I made a lighter pass over **all** 192 + 159 entries, looking for systematic faults. Judgments rest on handbook knowledge (Fortson, Ringe, Beekes, Mallory & Adams, LIV²/NIL conventions). I browsed nothing.

Grades:
- **ok**: form, gloss, gender and paradigm are all fine.
- **minor**: a notation or metadata problem, a gloss that over-specifies, or a near-duplicate; harmless in text.
- **wrong**: the word will reach text with the wrong part of speech, paradigm or meaning, or as a duplicate.

## Counts

| | ok | minor | wrong |
|---|---|---|---|
| (b) sample, 40 items | 18 | 13 | **9** |
| (b) of which usable (32) | 12 | 11 | **9** |
| (a) sample, 20 items | 12 | 8 | 0 |
| (a) full scan, 159 items | — | ~14 formation mismatches with a tolerable gloss; ~30 adjective glosses on noun-class entries | **13** gloss belongs to a different word |
| (b) full scan, 121 usable | — | — | **about a quarter** wrong: noun→adj 11 (+2 mixed), comparatives 5, duplicates 10, notation 2 (h₂éh₂usos is counted in two of these) |

All 9 wrong items in the (b) sample are usable, so they would reach text. The (a) random sample happened to miss every wrong match, but the full scan finds 13. In the scan, "formation mismatch" means NIL describes a different derivation of the same root and the gloss still fits; "different word" means the gloss is now wrong for the existing entry.

## (b) sample: new lexemes

| id | form · pos/gender | gloss | paradigm (nom/gen sg) | grade | note |
|---|---|---|---|---|---|
| bhegnos | bʰegnós adj | broken | -ós/-ósyo, f -éh₂ | ok | Ved. bhagná- |
| bhesmn | bʰésmn̥ n | ash | bʰésmn̥ / bʰsméns | ok | proterokinetic men-stem, fine |
| bhortos | bʰórtos m | load, cargo | ok | ok | φόρτος |
| dhebhros | dʰebʰrós adj | little, scanty | ok | ok | |
| dhiHtos | dʰiHtós adj | perceived, thought | ok | ok | |
| dhobhos | dʰóbʰos m | deception; deceiver | ok | minor | all evidence is `[` (an Indic-internal formation) |
| gjheymentos | ǵʰeymentós m | winter | ok | minor | NIL marks it `?`; Indic only (hemantá-) |
| gjnoh3tos | ǵnoh₃tós adj | known | ok | minor | `oh₃` colouring not normalized (=ǵneh₃tós); near-duplicate of ǵn̥h₃tós |
| gweh2toxr | gʷéh₂tōr m | one who steps/mounts | gʷéh₂tōr / gʷh₂trés | minor | attested only in ἐπιβήτωρ |
| gwowsth2os | gʷowsth₂ós **adj** | cow-stall | adj with f -éh₂ | **wrong** | a noun (Ved. goṣṭhá- m./n.) |
| h1lngwhros-2 | h₁l̥ngʷʰrós adj | light, quick | ok | **wrong** | duplicate of existing `pie-lex-h1lngwhros` (misspelled h₁ln̥gʷʰrós) |
| h1werHwos | h₁wérHwos n | free space, room | -os / -esos | ok | *-u̯es- s-stem |
| h1wesyos | h₁wésyos **noun n** | better (comparative) | neuter s-stem -yesos | **wrong** | comparative adjective: m nom *-yōs, weak *-is- |
| h2eh2usos | h₂éh₂usos **adj** | gold | adj, f h₂éh₂useh₂ | **wrong** | a noun (Lat. aurum n.); duplicate of `h2eh2usom`; root linked to h₂wes- 'dwell' |
| h2enh1ros | h₂énh₁ros m | wind | ok | minor | NIL `R` (r/l) silently became r; Ved. ánila- has l |
| h2owyos | h₂ówyos adj | of sheep | ok | ok | |
| h2regjntos | h₂reǵn̥tós adj | silvery; silver | ok | ok | |
| h2worsos | h₂worsós **adj** | rain, downpour | adj | **wrong** | a noun (Hitt. warsa- c., Ved. varṣá- n.) |
| leykwmn | léykʷmn̥ n | remainder | léykʷmn̥ / likʷméns | minor | `[`-only: λεῖμμα alone |
| maxdsos | mā́dsos **adj** | food, mush | adj | **wrong** | a noun (Gmc *mōsa- n.) |
| medros | medrós **adj** | joy | adj | **wrong** | NIL says "Subst."; root linked to med- 'measure' instead of med- 'become sated' |
| mertos | mértos m | mortal, human | ok | minor | same Vedic evidence as existing `mortos` (mórtos) |
| meykjmn | méyḱmn̥ n | mixture | ok | minor | `[`-only (μεῖγμα) |
| roth2os | roth₂ós m | chariot, wagon | ok | ok | |
| segjhyos | séǵʰyos **noun n** | stronger | neuter s-stem | **wrong** | comparative, as for h1wesyos |
| segtos | segtós adj | attached | ok | ok | |
| sewHmn | séwHmn̥ n | begetting, birth | ok | minor | `[`, lexicographic Sanskrit only |
| steh2toxr | stéh₂tōr m | one who stands (charioteer) | ok | minor | gloss over-specifies the Vedic meaning |
| swekjuros-2 | swéḱuros m | father-in-law | ok | **wrong** | duplicate of `swekjuros`; root linked to *wer- 'burn' (bad "/" split) |
| tenh2uh2os | ténh₂uh₂os adj | bodily, one's own | ok | minor | root linked to stenh₂- 'thunder' |
| torsos | tórsos m | thirst | ok | ok | |
| yewgtos | yewgtós adj | yoked | ok | ok | |
| dh3texr | dh₃tḗr m | giver | (unusable) | ok | |
| dhebhtis | dʰébʰtis f | harm | (unusable) | ok | |
| h2erh3texr | h₂erh₃tḗr m | ploughman | (unusable) | ok | |
| h2worseh2 | h₂worséh₂ f | rainy season | (unusable) | ok | |
| h3okwteriyom | h₃okʷtériyom n | gifts on first sight | (unusable) | minor | Greek only, gloss over-specified |
| mldhrom | ml̥dʰróm n | hostility | (unusable) | minor | root linked to meldʰ- 'pray'; `R` |
| pekwtexr | pekʷtḗr m | cook | (unusable) | ok | |
| priHtexr | priHtḗr m | friend | (unusable) | ok | |

Paradigms: the thematic, thematic-adj, men-neuter and -tér- cells render correctly. The s-stem, -i̯es- and *-tor* faults are listed under P2 and P13.

## (a) sample: existing derivatives glossed by NIL

| id | form | NIL formation | gloss | grade | note |
|---|---|---|---|---|---|
| bhertrom | bʰértrom | *bʰer-tro- n | means of carrying; bier | ok | |
| bhewdhtis | bʰéwdʰtis | *bʰeu̯dʰ-ti- | "to watch, heed" | minor | gloss copied from an OCS infinitive; should be a noun ("heeding") |
| dhureh2 | dʰuréh₂ | *dʰur-ah₂- f | door | ok | |
| gwh2tos | gʷh₂tós | *gʷh₂-to- | death (gone away) | minor | parenthetical; adjective gloss on a noun-class entry |
| gwoh2mos | gʷoh₂mós | *gʷoh₂-mó- m | step, altar | ok | |
| h2ekju | h₂eḱu- | *h₂ak̂-u- | sharp; needle | ok | |
| h2weksos | h₂wéksos | *h₂u̯eks-**o**- m | growth | minor | NIL has an o-stem; the entry is the s-stem vákṣas |
| h3nobhis | h₃nóbʰis | *h₃nobʰ-i- f | navel, hub; kin | ok | |
| kjlewtrom | ḱléwtrom | *k̂léu̯-tro- n | ear, hearing | ok | |
| kjubhros | ḱubʰrós | *k̂ubʰ-ró- | shining, pure | minor | adjective glossed, but the entry is classified as a thematic **noun** (no feminine) |
| kjwoytos | ḱwoytós | *k̂u̯ói̯t-o- m | light | minor | NIL accents the root (a noun); the entry accents the suffix |
| loypos | loypos | *lói̯p-o- m | ointment, glue | ok | |
| moldos | moldos | *mold-o- | soft, young | minor | adjective on a noun-class, unaccented entry |
| pedtus | pedtus | *ped-tu- | falling | ok | (the root homograph problem predates NIL) |
| steh2tleh2 | steh₂tleh₂ | *stah₂-tlah₂- | heel | ok | |
| stlneh2 | stl̥neh₂ | *stl̥-n-ah₂- | pillar | ok | |
| stoleh2 | stoléh₂ | *stol-áh₂- f | equipment; post, stem | minor | merges Greek "garment" with Germanic "post" |
| terseh2 | terseh₂ | *ters-ah₂- f | earth, land | ok | |
| trebeh2 | trebeh₂ | *trēb- f (root noun) | house | minor | NIL has a root noun; the entry is an eh₂-stem |
| yewgter | yewgtér- | *i̯eu̯g-tér- m | harnesser | ok | |

**(a) full scan: the gloss now belongs to a different word (13).** Each is a formation mismatch made possible by accent-, length- and ending-insensitive matching, or by a wrong root:
- bʰéydʰos-2: NIL's adjective *bʰeydʰó- (fīdus) glossed onto the s-stem foedus. The real match is `bheydhos`.
- bʰídis: root noun bhíd- 'cleft', glossed onto Gmc *bitiz 'bite'.
- dʰeh₁nos and dʰeh₁tus: *dʰeh₁- 'put' glossed onto fēnus and fētus, which come from dʰeh₁(y)- 'suckle'.
- dʰoyǵʰiHon-: 'rampart' glossed onto Gmc *daigijǭ.
- h₁ésus: 'good' glossed onto the PIIr *Hásu- 'life' entry, while a new h₁ésus-2 'life' was also created.
- h₃okʷéh₂: ὠπή (*h₃ōkʷ-) glossed onto ὀπή.
- léypos: Gmc *leiba- 'life' glossed onto répas.
- nogʷnós: *nōgʷno- 'leather' glossed onto the 'naked' entry.
- stéh₂mō: an Umbrian o-stem glossed onto Lith. stuomuõ.
- tr̥bom: trabs 'beam' glossed onto *þurpą 'village'.
- wedrom: *u̯ēdro- 'bucket' glossed onto vitrum.
- yugos: yúj- 'ally' glossed onto Hitt. iugaš.

**Tolerable mismatches (~14):** bʰéh₂os, bʰérǵʰō, bʰudʰo-, ǵenh₁eseh₂ (γένος→γενεά), h₂eǵós, h₂ēpeh₂, h₂wéksos, pēdó-, púḱis, sédos, swéh₂dos, swópr̥, trebeh₂, h₁lengʷʰtos.

**Adjective glosses on noun-class entries:** 42 glossed (a) entries are classified `shape:thematic` (noun) and have no pos. About 30 of them are adjectives NIL prints without a gender: ḱwitrós, mudrós, piḱrós, suptós, srutós, steh₂rós, sth₂rós, sl̥prós, likʷtós, …. They will be inflected as masculine nouns with no feminine.

## Systematic problems and fixes

**P1. Root linking picks homographs and strips palatals (≈26 of the 192 new lexemes sit under the wrong root).** This also feeds (a) wrong matches and (b) duplicates.

What happens:
- `_plain()` (pie/liv.py) deletes every U+0301. That accent is also the diacritic of ḱ/ǵ, so ḱel- = kel- = skel-'s variant kel-.
- With several candidates, `apply()` breaks the tie by `_gloss_sim`. Its stopword list contains "be", so the sim is 0 and the first candidate wins.
- A single candidate is accepted with no check at all.

Results:

| NIL root | linked to | should be |
|---|---|---|
| *h₁es- | sh₁es- 'harvest' | h₁es- |
| *dʰeh₁- | dʰeh₁y- 'suckle' | dheh1-do, which exists |
| *k̂el-, *k̂elH- | skel-, skelH- | |
| *tenh₂- | stenh₂- 'thunder' | |
| *h₂u̯es- 'dawn' | h₂wes- 'dwell' | |
| *med- 'sate' | med- 'measure' | |
| *meldʰ- 'abandon' | 'pray' | |
| *smer- 'fat' | 'remember' | |
| 1.*pei̯g- 'paint' | 'inactive' | |
| *bʰes- 'rub' | 'chew' | |
| 1.*u̯ers- 'male' | 'wipe' | |
| *mis-dʰh₁-ó- | mey- | |

There is a further bug in `build_records()`: it splits `*su̯ek̂ur̥/u̯er-` on "/", so "u̯er-" becomes a root and is matched to *wer- 'burn'.

Fix:
```python
# apply(): prefer the LIV² page, which both sides carry
def _liv_page(x):  # NIL 'LIV 136f.' -> 136
    m = re.search(r"LIV\s*(\d+)", x.get("liv_ref") or ""); return int(m[1]) if m else None
p = _liv_page(x)
if p and cands:
    by_page = [r for r in cands if any(abs(int(re.sub(r"\D", "", l["page"]["printed"]) or 0) - p) <= 2
                                       for l in r.get("liv", []))]
    cands = by_page or cands
# exact form beats variant-only (s-mobile) matches; never accept a 0-similarity pick
exact = [r for r in cands if _plain(r["form"]) in {_plain(f) for f in forms}]
cands = exact or cands
if not p and (len(cands) > 1 or _gloss_sim(en, liv_en(cands[0])) < 0.2):
    continue                                        # leave the formation unmerged
```
```python
# liv._plain: strip accents only on vowels/syllabics, keep ḱ ǵ
return NFC(re.sub(r"(?<=[aeiouAEIOŪ̥])́", "", NFD(f)))
# build_records: split alternatives on ',' and on '/' only before a new starred form
for part in re.split(r"\s*,\s*|\s*/\s*(?=[?*])", e["root_printed"]):
```

**P2. Genderless o-stems all become adjectives (11 clear nouns, all usable).** The nouns: bʰérmentos (fermentum n.), bʰuh₂mós, dʰh₁sós (θεός m.), gʷowsth₂ós, h₂éh₂usos, h₂worsós, mā́dsos, medrós, móystos (c.), n̥bʰós, wr̥sn̥bʰh₂ós. Two more mix noun and adjective: h₃okʷós, dʰǵʰémyos. The evidence strings carry the gender.

Fix in `citation()` (pass `fm["evidence"]`):
```python
_G = re.compile(r"(?<![\w.])(m|f|n|c)\.(?=[\s,)/]|$)")
def _ev_gender(ev):
    gs = [("m" if m[1] == "c" else m[1]) for s in ev for m in _G.finditer(s if isinstance(s, str) else s.get("form", ""))]
    return max(set(gs), key=gs.count) if gs else None
...
if re.search(r"[oó]$", stem):
    g = g or _ev_gender(evidence)
    if g is None:
        if any("Subst." in s for s in evidence): return None   # noun of unknown gender: don't guess
        return stem + "s", "adj", None
```
The same `_ev_gender`/adj test should set `pos` on (a) hits that have none:

```python
# apply(), when glossing a hit
if not hit.get("pos"):
    s = _shape(fm["stem"], fm.get("gender"), fm["evidence"])
    if s:
        hit["pos"], hit["pos_source"] = s[1], "nil"
```
This addresses the ~30 adjective glosses on noun-class entries.

**P3. Comparatives in -i̯es- become neuter s-stem nouns (5, all usable).** The five are bʰéwh₂yos, h₁wésyos, préyHyos, séǵʰyos, sényos, glossed "greater / better / dearer / stronger / older". They render as neuters (séǵʰyesos …).

Fix: put this before the s-stem branch in `citation()`:
```python
if re.search(r"y[eé]s$", stem):          # *-i̯es-/-i̯os- comparative
    return None                           # until a comparative family exists (cf. pedyōs: also unusable)
    # later: return stem[:-2] + "ōs", "adj", None   (m nom *-yōs, n *-yos, weak *-is-)
```

**P4. Duplicates (≈14; 10 of them usable).**
- Key collisions: bʰosós-2, dʰh₁tós-2, gʷih₃rós-2, gʷoyh₃ós-2, ḱl̥tós-3 (=ḱl̥tós-2, Lith. šil̃tas), swéḱuros-2, ténh₂mn̥-2.
- Spelling variants: h₁l̥ngʷʰrós-2 (existing h₁ln̥gʷʰrós), dóh₃tōr (existing déh₃tōr), h₂éh₂usos (existing h₂éh₂usom), neptíHs (néptih₂), sweḱrúHs (sweḱrúh₂), mértos (mórtos), gʷénh₂s (gʷḗn).
- Not a duplicate: tr̥séh₂-2 (the existing tr̥séh₂ is Umbr. turse < *tres-).

Cause: `_new_lexeme()` checks only `kids` of the (often wrong) root, and keys are sensitive to h₃-colouring and H vs h₂.

Fix: check the global `words` index under a normalized key, and attach the `nil` block to the hit instead of creating an entry:
```python
def _nkey(f):  # colour- and laryngeal-insensitive
    f = re.sub("oh₃", "eh₃", re.sub("óh₃", "éh₃", f))
    f = re.sub(r"([iu])H", r"\1h₂", f)
    return _key(f)
hit = words_by_stem.get(_nkey(re.sub(r"(s|m|om|os)$", "", form)))   # index words by stem (form minus -s/-m/-os/-om)
if hit: hit.setdefault("nil", []).append(...); return 0
```
`apply()` has to build `words_by_stem` (the same strip applied to every word/derivative form) and pass it through. That is what catches h₂éh₂usos ~ h₂éh₂usom.

**P5. NIL h₃ colouring not normalized (10).** The affected stems are ǵnoh₃tḗr, ǵnoh₃tós, ǵnóh₃tlom, dóh₃tōr, yóh₃smn̥, yóh₃sneh₂, yoh₃stḗr, and h₃okʷ- ×3. `stem()` normalizes only `h₂a/ah₂`. NIL writes the e-grade of *deh₃-, *ĝneh₃-, *i̯eh₃s- as `-oh₃-`, exactly as it writes `-ah₂-`.

Fix in `stem()`: `t = re.sub("óh₃", "éh₃", re.sub("oh₃", "eh₃", t))`. Leave root-initial `h₃o` alone, because the lexicon itself writes the o-grade h₃ókʷs and h₃okʷéh₂; rely on `_nkey` for matching.

**P6. (a) matching is too loose (13 wrong + ~14 mismatched).** `ENDINGS` lets any stem take any of 30 endings, and `_key(..., "nolength")` drops length. So a root noun matches an -os/-is/-eh₂ entry, an o-stem matches an s-stem, and *h₃ōkʷ- matches h₃okʷ-.

Fix: build the one expected nominative and compare with length kept:
```python
exp = _shape(fm["stem"], fm.get("gender"), fm["evidence"])  # citation() without the accent gate
cand = kids.get(key(exp[0], "noaccent")) if exp else None   # keep ā/ē/ō
if cand and spec_family(cand) != family_of(exp):            # s-stem vs thematic, eh₂ vs root noun
    cand = None
```
Root nouns (consonant-final stems with no `_shape`) should match only "" or "s".

**P7. NIL notation leaking through.**
- `R` (r/l cover symbol) becomes r: h₂énh₁ros, ml̥dʰróm, téntrom.
- A palatal is lost in transcription: `*(-)genh₁-etó-` gives **genh₁etós** under *ĝenh₁-, and `*gnoh₃-dʰlo-`.
- A syllabic sonorant stands before a vowel: oybʰr̥ós.

Fixes in `stem()`:
```python
if "R" in s: return None
if re.search(r"[rlmn]̥(?=[aeiouāēīōūáéíóú])", unicodedata.normalize("NFD", t)): return None
```
In `build_records()`, if the root has `ĝ/k̂/ĝʰ` and the formation shows the plain stop in the same root slot, flag `uncertain` (or restore the palatal).

Checked and fine:
- a-colouring `h₂a/ah₂ → h₂e/eh₂` came through correctly (h₂eḱénis, gʷéh₂trom, h₂énh₁teh₂, h₂werseh₂).
- k̂/ĝ → ḱ/ǵ is right wherever the transcription has the palatal.
- Labiovelars `ʷ` are preserved (gʷowsth₂ós, h₃kʷtós, snigʷʰetós).
- Glides `i̯/u̯` normalize to y/w.

**P8. Laryngeal-final root nouns.** gʷénh₂s: the root-noun branch adds -s after h₂ (the nominative is *gʷénh₂). For neptíHs, moysíHs and sweḱrúHs the lexicon's convention is -ih₂/-uh₂ with no -s. All four are unusable today but would collide later.

Fix:
```python
stem = re.sub(r"([íiúu])H$", lambda m: m[1] + "h₂", stem)
if stem.endswith(("ih₂", "íh₂", "uh₂", "úh₂")): return stem, "noun", "f"
if stem.endswith(("h₁", "h₂", "h₃", "H")) and g: return None
```

**P9. Weak attestation is not gated (98 single-daughter, 56 usable; 19 with only `[` evidence, 13 usable; 31 NIL-`?`, 21 usable).**
- NIL's own introduction (raw/books/text/nil/p0011–p0023, §§ 5–10) is explicit on three points:
  - Its starred forms are **Transponate**, "keine Rekonstrukte, die das jeweilige Wort als schon grundsprachlich existent postulieren".
  - They "erhalten … keine Bedeutungsangaben". So every NIL gloss in our data was composed from the daughters, and none is NIL's claim about a PIE meaning.
  - NIL deliberately includes single-language words that can be transposed.
- So a NIL formation alone is not evidence that the word existed in PIE.
- `[` is NIL's **Umbildungsklammer**: the daughter does not continue the transponate unchanged. Typical cases are Greek -μα(τ-) for *-men- and Lithuanian thematic adjectives moved into the i̯ā-class.
- A lexeme whose evidence is all `[` therefore has no daughter that continues it unchanged. Examples: léykʷmn̥, méyḱmn̥, séǵʰmn̥, yóh₃smn̥ (Greek -μα only); módos and dʰóbʰos (remodelled Indic forms).
- I did not find ‡ defined in the introduction text I searched. Many one-language formations carry no ‡ in the transcription: τονή, ὀπτήρια, βατήρ, lat. suāsor, tentor. Verify against a page image what ‡ means before relying on it (the module docstring assumes "one language only").
- Glosses built from one daughter are over-specified, for example:
  - "prolongation (of a note)", "stater (weight)", "threshold, base" (gʷm̥tḗr)
  - "gifts on first sight", "letter, writing" (péyḱmn̥ < OCS pismę)
  - "stretcher (an occupation)", "nature" (gʷómos, gʷomtéh₂ < Lith.)
  - "loan, hire" (loykʷéh₂)
- Glosses built from infinitives come out as verbs or labels: "deceiving (infinitive)", bʰéwdʰtis "to watch".

Fix in `_new_lexeme()`: require ≥2 branches and at least one non-`[` daughter; otherwise create the entry with `uncertain: ["nil-single-branch"]`, and have the slice gate exclude `nil-*` uncertain entries:
```python
BR = {"ved":"ii","ai":"ii","jav":"ii","aav":"ii","apers":"ii","iran":"ii","gr":"gk","myk":"gk","lat":"it","osk":"it","umbr":"it",
      "germ":"gm","got":"gm","an":"gm","ae":"gm","ahd":"gm","as":"gm","lit":"bs","lett":"bs","apr":"bs","aksl":"bs","russ":"bs",
      "air":"ce","mir":"ce","mkymr":"ce","gall":"ce","heth":"an","hluv":"an","lyk":"an","toch":"to","arm":"ar","alb":"al"}
def _branches(ev):
    return {BR.get(re.match(r"[?\[\s]*([a-z]+)", s).group(1)) for s in ev if not s.lstrip("? ").startswith("[")} - {None}
if len(_branches(fm["evidence"])) < 2: unc.append("nil-single-branch")
```
Glosses that mention "(Inf.)" in the evidence should be nominalized ("watching, heed"), or the formation skipped.

**P10. Gloss composition.** NIL glosses that contain "?" or a parenthetical (14) should not pass into a PIE gloss verbatim. Strip the parentheticals, and drop the gloss when it contains "?" ("sinew (?), diaphragm (?)").

**P11. Notes outside nil.py (for the classifier).**
- Root-accented *-tor* agents get a hysterokinetic weak stem: dóh₃tōr gen dh₃trés, gʷéh₂tōr gen gʷh₂trés. The Vedic dā́tar- type has gen. dā́tuḥ with root accent kept. This affects the existing déh₃tōr too.
- All eh₂-stems and all -tér- nouns are unusable, which hides most NIL eh₂ and agent formations from text (fine for now).

## Verdict

**Not yet.**

About a quarter of the 121 usable new lexemes are wrong in ways that reach text:
- 11 nouns inflected as adjectives
- 5 comparatives inflected as neuter nouns
- about 10 duplicates of existing words
- 2 notation errors

On top of that, about 26 sit under the wrong root. In (a), 13 existing words now carry another word's gloss, and about 30 adjective glosses sit on noun paradigms.

Beyond the bugs, NIL itself says its forms are transponates without meanings, not reconstructions (P9). Every NIL gloss is ours, and a single-branch NIL formation should not by itself make a PIE word.

P1, P4 and P6 are matching bugs with effects across entries. They need fixing in `nil.py`/`liv._plain`, followed by a lexicon rebuild, before any NIL-sourced gloss or lexeme goes into a Tier 3 slice.

After P1–P6 and the rebuild, a gated subset is defensible:
- -tó-/-nó-/-ró-/-ló- adjectives, men-neuters, -tor agents and m o-stems
- attested in ≥2 branches, with at least one non-`[` daughter
- not NIL-`?`
- with the root verified by LIV page

That subset is roughly 50–60 lexemes. Re-sample 30 of them before admitting them. Keep the -i̯es- comparatives and all genderless substantives out until P2 and P3 land.
