# Mapping precision: Germanic (ang, non, got)

Corpora: `ang` (Beowulf, Gutenberg, plus Grein's Bibliothek I–II, OCR), `non` (Poetic Edda, Finnur Jónsson 1926, OCR) and `got` (Gothic Bible, PROIEL). Tables: `data/research/formulas/mapping/{ang,non,got}.jsonl`. Corrections: `data/research/formulas/mapping-overrides/germanic.json`, with **239 lemma rows** (146 remaps, 93 unmaps; ang 101, non 77, got 61) and **19 form rows** (ang 16, non 3). Main dictionary: Kroonen 2013, *Etymological Dictionary of Proto-Germanic* (`raw/books/text/kroonen-pgmc/`), cited in each note by headword and scan page. De Vaan is cited once (Lat. *taceo*).

## Method

1. **Token counts.** I rebuilt the three corpora with the project loaders (`load_proiel`, `edda_lines`, `beowulf_lines` + `grein_lines`, `FormLemmatizer`, `text_tokens`), imported read-only from a scratch script. The rebuilt lemma → ids mapping matches the three tables exactly: 3714, 1928 and 1819 lemmas, 0 id differences. For the unlemmatized corpora I also collected surface forms per lemma. Without them the OCR and homograph errors cannot be seen.
2. **Sample.** For each corpus, 100 content-lemma types drawn with token-frequency weights: Efraimidis–Spirakis keys `random.Random(seed).random() ** (1/count)` over the sorted lemma list, seed 0 before the overrides and seed 1 after. Unmapped types are included, so the sample also measures coverage gaps.
3. **Verdicts.** **C** = every id is a correct etymon of the lemma as it occurs in the corpus (lexeme or root level). **P** = the right root plus a wrong extra id (usually a homonymous root), or the right root with the wrong formation. **W** = no correct id. Unmapped types are **U** (mappable) or **N** (name, borrowing, no secure etymology, function word, OCR junk). Strict precision is C / mapped. Lenient precision is (C+P) / mapped.
4. **Fixes.** I reviewed the 300 most frequent mapped lemmas of each corpus (900 in total), checking doubtful ones against Kroonen. I then scanned all three tables for ids already known to be wrong and for sets of homonymous roots, and added mappings for frequent unmapped lemmas with secure etymologies.
5. **Re-measure.** I recomputed the mapping through the real override path (`apply_rec_overrides` / `apply_lemma_overrides`; form rows go through `FormLemmatizer`) and drew the seed-1 sample from the corrected corpus. Each seed-1 item was judged twice: under the old table ids and under the new ones. This gives a paired before/after on the same items. Seed 0 is an independent "before" sample.

## Results

| corpus | seed 0, before: strict (lenient), n mapped | seed 1, same items, old ids | seed 1, new ids | seed-1 items touched by an override |
|---|---|---|---|---|
| got | 82.0% (90.2%), n=61 | 82.2% (90.4%), n=73 | **89.0% (93.2%)**, n=73 | 6 |
| non | 82.4% (92.2%), n=51 | 81.2% (87.5%), n=48 | **85.7% (91.8%)**, n=49 | 4 |
| ang | 81.8% (84.1%), n=44 | 65.8% (76.3%), n=38 | **80.5% (85.4%)**, n=41 | 10 |

The samples are small (38–73 mapped items), so a 95% interval is about ±10 points. The paired seed-1 comparison is the reliable one.

After the seed-1 verdicts I added 19 more fixes for errors that sample exposed (e.g. Go. *qainon*, *swers*, *dails*; ON *smiðr*, *blása*; OE *bān*, *bit*). The "new" column does not include them.

Seed-1 N items by type:
- got: 22 (5 names, 2 borrowings, 15 with no secure etymology).
- non: 44 (17 edition titles, abbreviations and OCR junk; 8 names; 12 real words the form lemmatizer missed; 7 with no secure etymology).
- ang: 56 (42 OCR fragments, apparatus or German text; 3 names; 11 with no secure etymology).

So the coverage gap in ON and OE is mostly a corpus problem, not an etymology problem.

Coverage (content tokens with a mapping) falls slightly, because junk and homographs are unmapped and OCR'd function words leave the content set:
- got: 73.7% → 73.1%
- non: 52.2% → 51.5%
- ang: 44.2% → 42.4%

## Main error types (and what was done)

1. **`pie-lex-sh1es` for 'be'.** In the lexicon this id is *sh₁-es-*, the s-stem of *seh₁-* 'sow'. Its variant field is `h₁es-`, so every chain ending in `ine-pro:*h₁es-` resolves to it. That hits the copula: Go. *wisan*, *sunja*; ON *vera*, *vesa*; OE *wesan*, *sindon*, *sīe*, *synn*.
   - I remapped them to `pie-lex-h1esti` / `pie-root-h1es-be`, plus `pie-lex-h2weseti` for the *wes-* stems (Kroonen *wesan- 1, p0622).
   - 'Harvest' words (Go. *asans*, OE *esne*) now go to `pie-root-sh1es-harvest`.
   - The bug is in the lexicon or resolver, so **it affects every branch**, not only Germanic.
2. **Homonymous root sets.** One Wiktionary root string expands to every lexicon root of that form: *sekʷ-* follow/say/see, *leyt-* go/touch, *lewbʰ-* cut off/desire, *nem-*, *sel-*, *h₂el-*, *h₂welh₁-*, *wes-*, *meh₂d-*, *dʰeh₁-*/*dʰeh₁y-*, and others. 67 rows now drop the homonymous or extra ids and keep the single correct root.
3. **Lemmatization and homographs in the unlemmatized corpora.** A surface form is matched to a dictionary headword of the same spelling:
   - ON *var* 'was' → 'slime'; *átti* 'owned' → 'eighth'; *bað* 'bade' → 'bath'; *lá* 'lay' → 'shore'; *verðr* 'becomes' → 'worth'; *man* 'shall' → 'household'; *sék* 'I see' → 'one'.
   - OE *is* 'is' → 'ice'; *bær* 'bore' → 'bare'; *gefylled* 'filled' → 'fell'; unmarked *god* ('God') merged with *gōd*.

   Fixed by remapping the lemma or by a form row.
4. **Grein OCR.** ð is printed as d, so *wid* 'with', *ford* 'forth', *da* 'then' and *dan* 'then' were mapped as 'wide', 'ford', 'doe' and 'dough'. These now go to the function word through form rows. Other damage:
   - Accent marks rendered as `^` or digits, and æ rendered as `&`, split words into fragments (*fe*, *sce*, *ta*, *tan*, *ter*, *fde* < *H&fde*, *hl* < *hl&ford*, *bit* < *bit)encan*). These are unmapped, or sent to `?`-forms (the code's own marker for unknown forms).
   - German preface and apparatus text and the Google Books notice pass the 60% line filter (*am*, *der*, *it*, *Cot.*). Unmapped.
5. **Etymologies Kroonen rejects or calls unknown:**
   - **Unknown:** *hlaifs*, *aba*, *skalks*, *wairþs*, *fraiw*, *sverð*, *hugr*/*hyge*, *gamall*, *lítill*, *hrafn*, *bān*/*bein*, *eiðr*.
   - **Wrong root:** *manags*/*margr*/*menigu* (*monogʰ-o-*, not *meǵh₂-*), *briggan* (not *ḱóm*), *munþs* (*mn̥t-o-*, not *mént*), *triggws* (*dreuH-u-*, not *drew-* 'run'), *lustus* (*lh₂s-*, not 'louse'), *hairto*/*hjarta* (heart, not *ḱerh₂-*), *leik* (*leig-* 'likeness', not 'bind'), *þegja* (*tHk-eh₁-*, = Lat. *tacēre*), *harðr* (*kret-*).
6. **Borrowings and names** mapped through look-alikes: OE *engel* (Lat. *angelus*), *weall* (Lat. *vallum*), *calend*; ethnonyms *Dene*, *Gēatas*, ON *Húna*; FJ's abbreviations *g.*, *v.*. Unmapped.
7. **Coverage.** 28 frequent ambiguous or unmapped lemmas are now mapped where the corpus forms settle the etymon. Examples:
   - OE *wæs*/*was* (*wesan|bēon*, about 440 tokens), *wealdend*, *willan|wil*, *dōn|dyde*, *eorðan* (via a form row).
   - ON *mun*/*munt*/*munk* (243 tokens), *skal*, *væri*, *varð*, *veit*, *vill*, *goðum*.
   - Go. *ga-hausjan*, *frawaurhts*, *þiudangardi*, *gudja*, *laistjan*, *garaihtei*.

## What remains

- **Loader fixes (code, out of scope here).** The overrides are a patch over these:
  - Grein: read `&` as æ; treat `^`/digit accent marks inside words as length marks instead of word breaks; restore ſ→s and þ→b/f confusions; drop the German Vorwort/apparatus and the Google boilerplate before the 60% filter.
  - Edda: FJ's Icelandic notes (*Skýringar*) and prose links are in the corpus (modern *og*, *að*, *hún*, *það*). Three form rows (*og*, *þótt*, *et*) and some unmaps only patch the worst of it.
- **Lexicon metadata (fix in `data/lexicon/lexicon.jsonl`, not by override):**
  - `pie-lex-sh1es` should not carry the variant `h₁es-`.
  - `pie-lex-kjerh2` (horn/head *ḱerh₂-*) has parent *ḱer-* 'grow'.
  - `pie-lex-steyh2` has parent *steh₂-*.
  - `pie-root-twek-physical_appearance` attracts *þwahan-* 'wash'.
- **Pseudo ids** (`kaikki:…`) cannot be written in the brief's override format, so doubtful ones stay, e.g. *handus*/*hǫnd* → `kaikki:ḱomt` (Kroonen: *ḱont-u-* from *hinþan-*).
- **Long tail.** Rare words still have dubious chains (ON *dýrr*, *dúnn*, *elda*; OE *lēoþ*, *geōmor*, *tȳdran*), and homographs remain whose lemma covers two etyma: OE *fāh* 'hostile/decorated', ON *vega* 'weigh/fight', Go. *weihs* (now 'holy' only).
- **Format note for the other groups.** The brief's row format omits `erratum`, but `apply_rec_overrides` reads `row["erratum"]` and raises `KeyError` without it. Every row here carries both `erratum` and `note`.
- **Tables not regenerated.** I did not run `scripts/formula_search.py mapping`: it rewrites every corpus's table. The recompute described above is the verification. The tables pick up these rows at the next regeneration, and the 8c loaders already read them through `apply_table_overrides`.
