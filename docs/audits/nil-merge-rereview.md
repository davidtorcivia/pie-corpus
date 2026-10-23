# NIL merge re-review (after the P1–P11 fixes)

Scope: the rebuilt `data/lexicon/lexicon.jsonl` and `data/morph/inflection_specs.jsonl` after
commits 9ef375f (fixes in `pie/nil.py`, `pie/liv.py`) and c503d70 (rebuild). There are two populations:

- **(a)** 159 existing derivatives glossed by NIL (`meaning_source: "nil"`, source ≠ nil).
- **(b)** 135 new lexemes (`source: "nil"`):
  - 89 are flagged `nil-single-branch`, 22 `nil-single-branch` + `nil-uncertain`, 2 `nil-uncertain` alone, and 1 `nil-notation` + `nil-single-branch`.
  - **21** carry no `nil-*` flag. **13** of those 21 are usable, so they would reach text once the hold in `scripts/make_slice.py` is lifted.

Method:
- **(b)**: all 21 unflagged entries. The population is smaller than 30, so the whole of it is graded. Three of them were in the first review (gʷowsth₂ós, mā́dsos, roth₂ós); they are graded again here as fixed items.
- **(a)**: 25 entries drawn with seed 424242 from the 140 that were not in the first review's (a) sample. The draw hit tr̥bom, which is on the first review's wrong list, so I swapped it for h₂énh₁mos-2 (seed 7) and re-check tr̥bom below.
- For each item I rendered NOM/ACC/GEN/LOC.SG, NOM/INS.PL and DAT.SG/GEN.PL (adjectives in m, f and n) with `Lexicon.cells()`, and read the `nil` block's daughter evidence.
- Full scans over all 294 NIL-sourced entries checked:
  - noun/adjective confusion
  - comparatives
  - duplicates, both stem-key and initial-laryngeal-insensitive
  - root homographs
  - h₃, R, palatal and syllabic notation
- Judgments rest on handbook knowledge only (Fortson, Ringe, Beekes, Mallory & Adams, LIV²/NIL conventions). I browsed nothing.
- Grades follow the first review: **ok**, **minor** (metadata, an over-specified gloss, or a near-duplicate harmless in text), **wrong** (reaches text with the wrong part of speech, paradigm or meaning, or as a duplicate).

## Counts

| | ok | minor | wrong |
|---|---|---|---|
| (b) all 21 unflagged | 12 | 7 | **2** |
| (b) of which usable (13) | 9 | 2 | **2** (roth₂ós duplicate, sédtōr paradigm) |
| (a) sample, 25 | 19 | 5 | **1** (h₂ǵtós) |
| (a) full scan, 159 | — | ~10 (mixed noun/adj glosses, wrong twin, accent) | **5** (h₂ǵtós, priHnós, h₂éwgos, wersós, ḱl̥tós\*) |
| First review's wrong items, re-checked | 9/9 (b) and 13/13 (a) **fixed** | | |

\* ḱl̥tós carries the right gloss for its form, but it sits on the wrong root twin (see R6). Its effect in text is minor; I count it with the wrong items because its metadata is wrong.

For comparison, the first review found about 25% of the usable new lexemes wrong and 13 wrong (a) glosses. Now 2 of 13 usable (b) are wrong, and both have simple remedies. (a) has 5 bad glosses, against 13 wrong plus ~30 adjective-on-noun before.

## (b): all 21 unflagged new lexemes

| id | form · pos/gender | gloss | paradigm | grade | note |
|---|---|---|---|---|---|
| bhagos | bʰágos m | allotter; god | -os/-osyo | ok | bhága-, baga-, bogъ. NIL's `? *bʰāg-ó-` 'share' was wrongly swallowed into it as a "duplicate" (length ignored, R5) |
| bhngjhulos | bʰn̥ǵʰulós adj | thick, ample | m/f -éh₂/n -óm | ok | bahulá- |
| bhrtos | bʰr̥tós adj | carried, brought | ok | ok | bhr̥tá-, fūrtum |
| dhh1sos | dʰh₁sóm n | sacred object; deity | (unusable) | minor | the gender is a 2:1 vote of Luwian/Lycian n. over `?`θεός m.; 'deity' blends in θεός; near-duplicate of dʰéh₁s 'god' |
| gjnoh3tlom | ǵnéh₃tlom n | means of knowing, mark | (unusable) | ok | h₃ normalized; only the id slug keeps `noh3` |
| gwowsth2os | gʷowsth₂ós **m** | cow-stall | ok | ok | first-review wrong, now a noun |
| h1ekjweh2 | h₁éḱweh₂ f | mare | (unusable) | ok | áśvā, equa, ešva |
| h2ekjyeh2 | h₂eḱyéh₂ f | edge | (unusable) | ok | |
| h2enh1teh2 | h₂énh₁teh₂ f | breathing, sigh | (unusable) | minor | the Germanic and Albanian daughters are NIL-`?`, so only OIr. osnad (a compound) is firm |
| h2erh3dhlom | h₂érh₃dʰlom n | plough | (unusable) | minor | all four daughters are Slavic. `skr.` (Serbo-Croatian) was counted as Indo-Iranian (R4), so it escaped `nil-single-branch` |
| h2oxgjis | h₂ōǵís m | race, contest | (unusable) | minor | Celtic and Tocharian daughters are `?`; only Indo-Iranian is firm |
| h2rgjipyos | h₂r̥ǵipyós m | eagle | ok | ok | r̥jipyá-; Arm. arcui is `?` in NIL but a standard comparison |
| kjh3tos | ḱh₃tós adj | sharpened, sharp; shrewd | ok | ok | śitá-, catus |
| kjolHtos | ḱolHtós adj | cold | ok | ok | šáltas. The Avestan daughter is `?`, so strictly one firm branch |
| maxdsos | mā́dsos **m** | food, mush | ok | minor | now a noun, but the m comes from a Counter tie won by `? mbret. meus m.` (Breton has no neuter). The firm Gmc *mōsa- is **n.** Only Germanic is firm |
| medtos | medtós adj | full, sated; drunk | ok | ok | mattá-, μεστός; root med- 'sate' now correct |
| priHtos | priHtós adj | pleased, beloved | ok | ok | prītá-, frīta-, fríðr |
| roth2os | roth₂ós m | chariot, wagon | ok | **wrong** | duplicate of the usable Wiktionary `Hroth₂ós` (the same *(H)rot-h₂-ó-, glossed 'running; something that runs (wheels, chariots)'). It sits under the unmerged twin root LIV `ret-` / Wiktionary `Hreth₂-`. `_nkey` keeps the initial H, so the duplicate check misses it. It is also in `CORE_NOUNS` in make_slice.py |
| rotos | rótos m | wheel | ok | minor | a legitimate formation (roth, rãtas, *raþą), but Wiktionary's Hroth₂ós cites the same Baltic reflexes |
| sedtoxr | sédtōr m | one who sits | GEN **sdtrés**, DAT sdtréy, GEN.PL sdtrṓm | **wrong** | P11 is unfixed: a root-accented *-tor* agent gets the hysterokinetic zero-grade weak stem. Ved. sáttar- keeps the root and its accent (gen. type dā́tuḥ < *-tr̥s) |
| torseh2 | torséh₂ f | thirst; drying kiln | (unusable) | minor | the gloss joins Skt 'thirst' to OHG darra 'kiln' |

What the 13 usable entries render as:
- Thematic nouns and adjectives are correct: m -os/-om/-osyo/-oy, -ōs/-oes; f -éh₂; n -óm.
- Accents are right.
- ḱ, ǵ and kʷ, gʷ are intact.
- None has an `oh₃`, R or syllabic-before-vowel spelling.

## (a): sample of 25 NIL glosses on existing derivatives

| id | form · class | gloss | grade | note |
|---|---|---|---|---|
| bheh2os | bʰéh₂os n s-stem | light, radiance | ok | bhā́s-, iubar; now the s-stem formation (it was a mismatch in the first review) |
| bhoydos | bʰóydos (thematic, no pos) | breaking, biting | minor | NIL has an oxytone agent adjective (*bʰoi̯d-ó-, Gmc -beitr 'biting'); the entry is root-accented, and the participle gloss sits on a noun |
| dhigjhtos | dʰiǵʰtós adj | smeared, formed | ok | fictus, digdhá- |
| dnkjmos | dn̥ḱmós m | bite | ok | δαγμός |
| dnkjtos | dn̥ḱtós adj | bitten | ok | daṣṭá- |
| gjonh1eh2 | ǵonh₁éh₂ f | begetting, offspring | ok | γονή (unusable) |
| h1lewdhis-2 | h₁lewdʰis m | people | minor | the gloss went onto the unaccented tree-path twin of the glossed h₁léwdʰis 'people'. The twin predates NIL and is unusable |
| h2erh3tis | h₂érh₃tis f | ploughing; ploughland | ok | (unusable) |
| h2gjtos | h₂ǵtós **noun m** | driven, led | **wrong** | `pos: noun, gender: m` was set by `_attach` from "mkymr. amaeth m." and "gall. amb-actus 'Dienstmann'", which are substantivized compound members. The simplex is the participle (ἐπακτός, āctus) and should be an adjective (R1) |
| h3nobheh2 | h₃nobʰeh₂ f | hub; navel | ok | (unusable) |
| kjlowsos | ḱlowsos m | hearing | ok | sluxъ; unaccented, so out of slices anyway |
| leypom | leypóm n | life, body | ok | Gmc *lība-. This was the first review's léypos problem, now on the right entry |
| mregjhyoxs | mréǵʰyōs | shorter | ok | comparative, unusable |
| nigwtexr | nigʷtḗr m | washer, washing vessel | ok | (unusable) |
| pekwmn | pékʷmn̥ n | pastry, cake | ok | πέμμα; proterokinetic pkʷméns |
| pikjros | piḱrós adj | pointed, bitter; variegated | minor | NIL marks it `?`; the gloss blends Greek 'bitter' with Slavic 'speckled' |
| pikjtos | piḱtós adj | adorned, decorated | ok | piṣṭá- |
| sedos | sédos n s-stem | seat, dwelling | ok | sádas-, ἕδος |
| selpos | sélpos n s-stem | fat, oil, butter | ok | ἔλπος, Toch. ṣälyp, gjalpë |
| sogjhos | sóǵʰos adj | holding; mighty | minor | NIL is oxytone (*soĝʰ-ó-); the entry is root-accented, and its reflex ὄχος is better *woǵʰos |
| stlto | stl̥to- | foolish | ok | stultus (unusable) |
| stoh2mos | stóh₂mos m | stature, size | ok | stúomas |
| tentus | téntus m | thread, string | ok | tántu- (unusable) |
| widris | widris | knowing, wise | ok | ἴδρις (unusable) |
| h2enh1mos-2 | h₂énh₁mos m | wind; spirit | minor | ἄνεμος, animus are right, but this is the accented twin of h₂enh₁mos 'breath'. The duplicate predates NIL; NIL's gloss makes the twin slice-eligible |

## First review's wrong items, re-checked

All are fixed.

**(b) 9/9:**
- gʷowsth₂ós is now m.
- The comparatives h₁wésyos and séǵʰyos are gone: `_shape` returns None for *-i̯es-.
- Attached to existing entries instead of created:
  - h₂éh₂usos → h₂éh₂usom
  - h₁l̥ngʷʰrós-2 → h₁ln̥gʷʰrós
- medrós and swéḱuros-2 are gone.
- h₂worsós is now m and held back by `nil-uncertain`.
- mā́dsos is now a noun, though with a doubtful m (above).

**(a) 13/13:**
- bʰéydʰos-2 now reads 'trust, compact' (foedus).
- léypos now reads 'stain' (répas).
- tr̥bom now reads 'village, farmstead' (*þurpą).
- h₁ésus now reads 'life, existence'.
- h₃okʷéh₂ now reads 'opening, hole' (ὀπή).
- negʷnos took 'naked', not nogʷnós.
- No longer glossed at all: bʰídis (‡), dʰeh₁nos, dʰeh₁tus, dʰoyǵʰiHon-, stéh₂mō, wedrom, yugos.

**The first review's other lists:**
- *Adjective-on-noun (~30):* ḱwitrós, mudrós, piḱrós, suptós, srutós, steh₂rós, sth₂rós and likʷtós are now `pos: adj` with f -éh₂.
- *Genderless o-stem nouns:* bʰérmentom is n. and single-branch. dʰh₁sóm is n.
- *Duplicates:* all 14 are attached or absent.
- *Notation:* nothing left among the 294 forms (no non-initial `oh₃`, no R, no r̥/n̥ before a vowel). genh₁etós is flagged `nil-notation`.
- *Root homographs:* fixed for h₁es-, dʰeh₁-, ḱelH-, med-, h₂wes- 'dawn' and the swéḱuros "/" split. Still wrong: 1.*pei̯g- 'paint' (→ `peyg-` 'inactive'), *k̂el- 'warm' (→ `ḱel-` 'incline') and *mis-dʰh₁-ó- (→ `mey-` 'change', via the nominal-headword path). See R6.

## Residual systematic problems and fixes

**R1. Gender votes from compounds and personal names (h₂ǵtós, priHnós: participles inflected as m nouns).**

`ev_gender()` counts the gender of these evidence lines:
- a compound or personal name containing the formation: "jav. in PN frīnāspa- m.", "gall. -actus z.B. in amb-"
- an agent noun built on it: "mkymr. amaeth m."
- NIL-`?` daughters

Fix in `ev_gender()`:

```python
_NOVOTE = re.compile(r"\bPNn?\b|\bHG\b|\bVG\b|z\.B\.|^\W*\S+\.\s+-")   # names, compounds, '-actus'
ev = [s for s in ev if not _NOVOTE.search(s)]
firm = [s for s in ev if not s.lstrip().startswith("?")]
ev = firm or ev
```

Then make a mixed oxytone *-tó-/-nó-* stem a verbal adjective. Put this in `_shape()` before the noun-of-unknown-gender return:

```python
if g is None and ev == "mixed" and re.search(r"[tn]ó$", stem):
    return stem + "s", "adj", None
```

With both changes, h₂ǵtós and priHnós become adjectives. mā́dsos becomes n. (the firm Gmc daughter), and dʰh₁sóm stays n.

**R2. Oxytone s-stem adjectives made into neuter nouns (h₂éwgos 'strong').**

What happens:
- NIL `?*h₂au̯g-és-` is the oxytone, genderless adjective (Av. aojah- 'strong'). `_shape` turns it into a neuter s-stem.
- It matches the noun h₂éwgos (ójas- 'strength') and glosses it 'strong'.
- The right formation, *h₂áu̯g-es- 'strength, might', is attached only as a "duplicate", and the duplicate path never glosses.

Fix in `_shape()`:

```python
if re.search(r"[eé]s$", stem) and g in (None, "n"):
    if g is None and (stem.endswith("és") or ev == "adj"):
        return None                      # s-stem adjective (*-és-): no family yet
```

Then let a duplicate attachment gloss an unglossed hit of the same stem class.

**R3. NIL-`?` formations gloss (a) entries with no flag.**

`_attach` never writes `nil-*` to `uncertain`, so `nil_held()` cannot hold these back once source-based holding ends. 15 (a) glosses come from `?` formations. 8 of them are usable and accented: h₂eǵós, h₂éwgos, h₂wéksos, ḱlusrós, piḱrós, priHnós, sth₂rós and wersós ('better': one OIr. daughter, a comparative gloss on a positive adjective with f and n forms).

Fix in `_attach()`:

```python
if hit.get("meaning_source") == "nil" and hit["meaning"] == [fm["gloss_en"]]:
    for flag, cond in (("nil-uncertain", fm.get("uncertain")),
                       ("nil-single-branch", len(fm.get("branches") or []) < 2)):
        if cond and flag not in hit.setdefault("uncertain", []):
            hit["uncertain"].append(flag)
```

Apply the single-branch part to (a) only if the gloss, rather than the word, is what we want to gate. The word itself is already attested by Wiktionary.

**R4. The branch gate counts `?` daughters and misreads `skr.`**

In NIL, `skr.` is Serbo-Croatian; Sanskrit is `ai.`/`ved.`. All 7 `skr.` lines are Slavic (rȁlo, zȇt, júha, …). `_BRANCH_ABBR` lists `skr` under Indo-Iranian.

With `?` daughters excluded, 6 of the 21 unflagged entries fall to one branch: h₂énh₁teh₂, h₂érh₃dʰlom, h₂ōǵís, h₂r̥ǵipyós, ḱolHtós, mā́dsos. The last three are usable.

Fix:

```python
# _BRANCH_ABBR: drop "skr" from "Indo-Iranian", add it to "Balto-Slavic"
# branches(): leave out NIL's uncertain daughters as well as its remodelled ones
if s.lstrip("? ").startswith("[") or s.lstrip().startswith("?"):
    continue
```

If h₂r̥ǵipyós and ḱolHtós should stay (both are handbook comparisons), whitelist them explicitly rather than loosening the rule.

**R5. The duplicate check is too loose in one direction and blind in another.**

All 33 "duplicate" attachments were listed. They fail in four ways:
- **Verbs swallow participles.** A verb cited by its stem has the same `_stem_key` as the *-tó-* adjective. Lexemes lost this way:
  - bʰágt ← *bʰag-tó- 'allotted'
  - ǵnéh₃t ← jñātá- 'known'
  - mért ← *mér-to- 'mortal'
  - ségt ← *seg-tó- 'attached'
  - bʰúHt ← bhūtá-
  - dʰéh₁t ← *dʰeh₁-tó- 'law'
  - ǵénh₁t ← *ĝénh₁-to-
- **Length and laryngeal identity are dropped:**
  - bʰágos ← bʰāgó- 'share'
  - h₁ustós ← *h₂us-tó- 'dawned' (two different roots)
- **Stem class is ignored:**
  - dénḱs (root noun) ← s-stem *dénk̂-es-
  - skábʰos (s-stem) ← o-stem 'shavings'
- **Initial-laryngeal variants are missed:** roth₂ós vs Hroth₂ós, and h₂worsós vs worsós.

Fix in `_new_lexeme()`:

```python
def _same_word(h, form, fam):
    return (h.get("pos") != "verb" and h.get("kind") != "root"
            and _length(h["form"].strip("-")) == _length(form)
            and (fam is None or _family(h) in (None, fam))
            and _lar(h["form"]) == _lar(form))          # h₁/h₂/h₃ sequence; H matches any
dup = [h for h in by_stem.get(_stem_key(form), []) + by_stem.get(_stem_key(re.sub(r"^(H|h[₁₂₃])", "", form)), [])
       if _same_word(h, form, fam)]
```

`by_stem` must also be indexed with the initial laryngeal stripped.

**R6. LIV-page root links inherit `liv.py` homograph errors.**

`link_root()` trusts the LIV page, but `liv.py` attached these by form alone:
- LIV 2.*k̑el- 'become warm' → Wiktionary `ḱel-` 'incline'. Result: NIL ḱl̥tós 'warmed, cooked; warm' glossed the 'incline' twin (Gmc *hulþaz). The real twin is `kjltos-2` under ḱleh₁- 'hot' (Lith. šil̃tas).
- LIV 1.*pei̯g- 'paint' → Wiktionary `peyg-` 'inactive'. Result: pigtós and pigtḗr are filed under 'inactive' (both held).

There are 28 LIV form matches that have a homograph number and zero gloss overlap. About half look wrong outright:
- h₁reh₁- 'rest' ← 'ask'
- h₂et- 'grass' ← 'go'
- per- 'beat' ← 'make equal'
- ser- 'flow' ← 'watch over'
- tend- 'stretch' ← 'grow weary'
- wer- 'burn' ← 'ward off'
- wer- 'sense' ← 'run'

Fix in `liv.py`: when a numbered LIV headword (`\d\.\*`) form-matches a Wiktionary root with gloss overlap 0, create a new LIV root instead. Then in `link_root()`, have a `liv-page` candidate also pass `_root_sim > 0` against the Wiktionary meaning whenever it has one.

**R7. Root-accented *-tor* agents (P11, unfixed, in `pie/classify.py`).**

sédtōr renders gen. sdtrés, dat. sdtréy and gen.pl. sdtrṓm. The (a) entries h₂éǵtōr and séǵʰtōr, and the Wiktionary table déh₃tōr, show the same fault. The Vedic dā́tar- type keeps the root's full grade and accent: gen. *déh₃tr̥s, dat. *déh₃trey.

Until the classifier builds that paradigm, mark `shape:tor-agent` with a root accent unusable.

**R8. Several NIL formations matching one entry: the first one glosses.**

Examples:
- ḱwoytós (oxytone) got 'light', the gloss of the root-accented *k̂u̯ói̯t-o-; the oxytone *k̂u̯oi̯t-ó- is 'white, bright'.
- poyḱós is the same case: 'ornament' rather than 'coloured'.

Fix: in `apply()`, collect all hits per lexeme and gloss from the formation whose `expected()` form equals `NFC(hit["form"])`.

**R9. Twin entries that predate NIL.** These are minor:
- h₂énh₁mos-2 / h₂enh₁mos
- koryos-2 / kóryos
- h₁lewdʰis-2 / h₁léwdʰis

NIL glossed the tree-path twin because the headword entry has no `root_id`. The accent gate keeps the unaccented member of each pair out of slices, but both members of h₂énh₁mos are eligible. Fix: in `_attach`, if a same-`_nkey` word already has a dictionary gloss, attach the `nil` block there and leave the twin unglossed.

## Verdict

**(a) NIL glosses: yes, with exclusions.**
- 19/25 of the sample are ok and 1 is wrong. The full scan finds 5 bad glosses (down from 13, plus ~30 adjective-on-noun).
- Option 1: admit them now with an explicit blocklist: `h2gjtos`, `priHnos`, `h2ewgos`, `wersos`, `kjltos`, plus the root-accented tor-agents `h2egjtoxr` and `segjhtoxr` (R7).
- Option 2, cleaner: land R1–R3 and R6, rebuild, then admit every (a) gloss whose entry has no `nil-*` flag.

**(b) unflagged new lexemes: yes, for a named subset, not the whole flag-free set.**
- After R4, admit these 10 of the 13 usable lexemes:
  - judged ok: bʰágos, bʰn̥ǵʰulós, bʰr̥tós, gʷowsth₂ós, ḱh₃tós, medtós, priHtós
  - h₂r̥ǵipyós and ḱolHtós, whitelisted as handbook comparisons even though each rests on one firm branch
  - rótos (minor: its reflexes overlap with Hroth₂ós)
- Keep out:
  - **roth₂ós** until it is merged with Hroth₂ós (R5). Keep one entry, glossed 'chariot', and point `CORE_NOUNS` at it.
  - **sédtōr** until R7.
  - **mā́dsos**: its firm evidence is one branch, and its gender should be n.
- The 112 `nil-*`-flagged lexemes stay held, as designed.

R5 is not needed to admit anything. It only recovers about 10 good lexemes that were lost as false duplicates ('known', 'allotted', 'mortal', 'attached'), so do it before the next NIL rebuild rather than before admission.
