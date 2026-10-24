# Mapping precision: Greek (hom, grp)

Brief: docs/research/mapping-precision-brief.md. Corpora: **hom** (Homer, AGDT; mapped live by pie/formula_search.py) and **grp** (GLAUx archaic/classical poetry, table data/research/formulas/mapping/grp.jsonl). Dictionary: Beekes, *Etymological Dictionary of Greek* (EDG, raw/books/text/beekes-edg/). Overrides: data/research/formulas/mapping-overrides/greek.json. No code, lexicon or shared file was changed.

## Result

Precision = correct / mapped types in a 100-type sample, with types drawn by token frequency (content words, AGDT/GLAUx postag n/v/a).

| corpus | sample | state | mapped (n) | strict | root-level |
|---|---|---|---|---|---|
| hom | seed 0 | before | 66 | **75.8%** (50) | 86.4% (57) |
| hom | seed 1 | after round 1 | 71 | **78.9%** (56) | 91.5% (65) |
| grp | seed 0 | before | 62 | **80.6%** (50) | 90.3% (56) |
| grp | seed 1 | after round 1 | 68 | **91.2%** (62) | 97.1% (66) |

Two definitions are used:
- **Strict** counts a type as correct only if every id it carries names the etymon Beekes gives.
- **Root-level** also counts **partial** types: the root is right, but a homonymous wrong root is also attached, a better lexeme exists, or one member of a compound is missing.

Seed 0 re-judged under the same overrides scores hom 56/60 (93.3%) and grp 62/62 (100%). That figure is in-sample, because the fixes were partly found in that sample, so it is an upper bound. The seed-1 figures are the out-of-sample measurement.

Round 2 then fixed most of the errors that the seed-1 sample turned up (see below). The seed-1 numbers do not include round 2.

Token coverage of content words falls slightly, because unmapping false etymologies outweighs the compounds that were added:
- hom: 70.1% before, 65.4% after round 1, 64.5% after round 2.
- grp: 69.4% before, 65.9% after round 1, 64.9% after round 2.

Unmapped-but-mappable types in the samples: hom 7 → 7, grp 11 → 12. These are mostly compounds whose members are mapped (μεγάθυμος, ἐπώνυμος, εὐνομία) and derivatives (πυρή, νευρά).

**Overrides: 860 lemma rows.**
- By corpus: hom 345, grp 515.
- By kind: 625 remaps or additions, 235 unmaps.
- Round 1 has 608 rows and is the measured state. It includes 149 coverage rows for prefixed verbs whose simplex is mapped, such as πάρειμι (grp 470 tokens), εἰσοράω, ἀφικνέομαι, μεθίημι and ἐξέρχομαι.
- Round 2 has 252 rows, written after the seed-1 measurement and not measured.

Every row has a `note` that cites Beekes EDG by page (or s.v. where the OCR page could not be located), plus an `erratum` line. `apply_rec_overrides` needs the `erratum` key.

## Method

1. **Dump.** I rebuilt the hom mapping the way scripts/formula_search.py does: `build_kaikki_mapping(pseudo=True)` over `build_homer_mapping`, with overrides applied. For grp I read the table and applied `apply_table_overrides`. Token frequencies come from the loaded corpora. The scratch scripts, all prefixed `greek_`, stay in the session scratchpad.
2. **Sampling.** Lemmas are sorted, then drawn with weighted sampling without replacement: key = u^(1/n), u from `random.Random(seed)`, top 100. Sampling does not depend on the mapping, so seed 0 and seed 1 are independent draws of the same population.
3. **Judging.** Each type is checked against the EDG entry, whose verdict tag (IE / IE? / PG / LW / ?) survives the OCR.
   - Correct: the mapped etymon is Beekes's own (IE), or the one his IE? tag names.
   - Wrong: Beekes says PG, LW, unknown or "no convincing etymology", or names a different root.
   - Lexicon entries whose `root_id` is wrong are judged at lexeme level and not counted against the mapping. Examples: ναῦς → *sneh₂- 'swim', πατήρ → *peh₂- 'protect', θεός → *dʰeh₁- 'do', κεφαλή → *gʰebʰ- 'give', ὁδός → *sed- 'sit'. They are listed under "What remains".
4. **Fixes.** I checked the 300 most frequent mapped lemmas of each corpus; they overlap heavily, so each Greek lemma was reviewed once. A correction to a lemma is extended to its transparent derivatives and prefixed forms (e.g. τλάω, τάλας, τλήμων, τόλμα, τολμάω). Rows are emitted only where the lemma string occurs in that corpus. A correction is not written when the current mapping already has the right root group. Every lex_id was validated against lexicon.jsonl.

## Main error types (before)

1. **Homonym fan-out**, the largest class. A kaikki chain says "from PIE *X-", and every lexicon root spelled X- is attached. Examples:
   - ἕπομαι → *sekʷ- 'follow' / 'say' / 'see'
   - λέγω, λόγος → *leǵ- 'gather' / 'drip'
   - τρέπω → 'turn' / 'tread'; τλάω, τάλας, τόλμα → *telh₂- 'bear' / 'ground'
   - δαμάζω → 'tame' / 'build'; χαίρω, χάρις → *ǵʰer- / *gʰer- 'rub'
   - τιμή → three *kʷey-; κράτος → *kret- 'strong' / 'shake'; φημί, φάος → *bʰeh₂- 'speak' / 'shine'
   - εὐώδης → three *h₁es- roots

   After round 2, fan-out lemmas still carry 1.0% (hom) and 1.1% (grp) of content tokens. They were 2.1% and 2.2% after round 1.
2. **Wiktionary etymologies that Beekes rejects or calls Pre-Greek or unknown.** Examples: αἷμα, ἀγαθός, ἄνθρωπος, ἄναξ, μάχομαι, φίλος (*bʰílos, explicitly "must be abandoned"), καλός, κακός, χρόνος, καιρός, νῆσος ('swimmer', "should be abandoned"), αἱρέω, νόος, ποταμός, καλύπτω (PG), ὕβρις, σῶμα, φώς 'man'. Also κῦδος and χρή: Beekes gives *keud- and *ǵʰreh₁- for these, but the lexicon lacks those roots, so the lemmas are unmapped rather than left on the wrong *skewh₁- / *gʰreh₁- 'grow'.
3. **Homograph and accent confusion.**
   - AGDT δύω 'enter, sink' was mapped to *dwóh₁ 'two' (the numeral is δύο); 172 tokens with καταδύω.
   - ὦμος 'shoulder' was mapped to ὠμός 'raw'.
   - κήρ 'death' was mapped to κῆρ 'heart'.
   - κοινός was mapped to *sḱóh₁yno- 'shine' on the surface tier; it is *kom-yo- (EDG p. 731).
4. **Suffix pseudo-ids.** θάνατος and ἀθάνατος were mapped to kaikki:etos. They are now *dʰenh₂- (EDG p. 533f., LIV²).
5. **Half-mapped compounds.** ἀδελφός was mapped to *h₁n̥- 'in'; it is now *sm̥- + *gʷelbʰu-. Πάτροκλος and Εὐρύκλεια had only one member mapped.
6. **Proper names** with folk etymologies: Ὀδυσσεύς → *h₃ed- (PG), Ἥρα → *weh₁- 'true' (PG), Ἑλένη.

## What remains

- **Fan-out tail.** These have no Beekes verdict located yet: οἴομαι, ἐπιτέλλω/τέλλω, ἐφέπω/ἀμφιέπω (*sekʷ- vs *sep-), βλάπτω/βλάβη, ζητέω, τάσσω, τόπος, ἀθρόος, ὀδύνη/ὠδίς, ἵμερος, φᾶρος, φάρμακον, ἀρά/ἀριστερός, μέλος, ὥρα, κυλίνδω, κύκνος, Ἐρινύς, θέμις, ἐθίζω.
- **Kept but unverified or doubtful.**
  - παρθένος → *pstḗn 'breast' (direct reflex in the lexicon; Beekes not located)
  - ἕκαστος → *kʷ- (Beekes: inner-Greek ἑκὰς τις)
  - ἐρίγδουπος → *stewp-; λακίς → *leh₂-
  - pseudo-ids such as κρείων, μυρίος, ὕμνος, ὄλβος, βάρβαρος
  - ὅρκος, χορός, στέφανος, πλοῦτος, δόλος
  - αὐτός → *h₂ew 'away' (partial)
- **Two groups, one etymon.** In ἀμείβω and μιμνῄσκω the lexeme's root_id differs from the root entry. This is a lexicon issue.
- **Lexicon root_id errors** (listed in Method 3). They should be fixed in the lexicon, not by overrides.
- **Roots the lexicon lacks, so the lemmas stay unmapped:**
  - *keud- (κῦδος)
  - *ǵʰreh₁- (χρή, χρῆμα, χρηστός)
  - *h₂wedʰ- (ἆθλος)
  - the root of δύω 'put on' (Skt. upa-du-)
  - *peyH- 'be fat' (πίων; the lexicon only has 'sing')
- **Coverage.** Many frequent unmapped types are compound epithets and names (μεγάθυμος, περικαλλής, Ἀτρείδης) or Pre-Greek (μέγαρον, γαῖα, χαλκός, θάλασσα). Bahuvrihi compounds could be mapped member by member.
- **Caveats.**
  - One judge (this agent) did all the judging.
  - EDG pages are taken from the OCR page markers, or estimated as 2·file−48 where a marker is missing, so they may be off by one.
  - A few notes cite s.v. without a page.

## Sample judgments (wrong and partial)

- **Seed 0, before.**
  - hom wrong: εὐώδης, καταδύω, μῦθος, ἐρίγδουπος, κακός, ἐκπέρθω, αἱρέω, κυδάλιμος, Ἥρα.
  - hom partial: αὐτός, Εὐρύκλεια, δαμάζω, ἐπιτρέπω, ἰσόθεος, ἕλιξ, δῖος.
  - grp wrong: ἀγαθός, κοινός, χρηστός, χρόνος, ἀδελφός, κισσός.
  - grp partial: βροτός, ἕπομαι, ἔοικα, τόλμα, χάρις, εὐλογέω.
- **Seed 1, after round 1.**
  - hom wrong: ἐρίγδουπος, ὀχθέω, φίλος, νίκη, ῥίπτω, πίων.
  - hom partial: οἷος, ἰαύω, κραταιός, ἱδρόω, κλισμός, Τελαμών, Εὐπείθης, ὀρθόκραιρος, τανυήκης.
  - grp wrong: λακίς, νεβρός.
  - grp partial: ἐθίζω, εἰλύω, εὐδαίμων, ὄψ.
  - Round 2 fixed φίλος, νίκη, ῥίπτω, ὀχθέω, πίων, νεβρός, ἰαύω, κραταιός, ἱδρόω, κλισμός, Τελαμών and εἰλύω.
