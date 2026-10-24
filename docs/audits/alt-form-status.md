# Status of alternative forms

Recorded 2026-10-24 (branch fix/altstatus). Defect (David's review): when an override replaced a lexeme's spec, `scripts/classify_lexicon.py` kept the displaced spec in `extra_specs`, and `pie/validate.py` indexed its cells like any engine cell. A diagnosed parsing error therefore validated as a clean exact match: 'fish' *dʰǵʰúHoey* (DAT.SG from Wiktionary's thematization note *dʰǵʰúH-o* read as a weak stem) came out pass, coverage 1.0, tier exact, source engine:table.

## Statuses

| Status | Meaning | Validator |
|---|---|---|
| primary | the lexeme's spec (`spec`), the closed class, the lexicon headword | exact (or a fuzzy tier) |
| supported | an alternative a handbook or the project's conventions endorse: the displaced specs the engine-sweep conventions keep as the alternative (docs/STATUS.md "Conventions (engine sweep)", docs/audits/engine-sweep/INTEGRATION.md), a second Wiktionary table, the verbatim Wiktionary table cells | exact |
| legacy | retained for recognition only, not endorsed (contested, superseded, or a spec that mixes a convention alternative with a diagnosed error) | tier `legacy`: a warning, never exact |
| rejected | a diagnosed source or parsing error (the override note or an engine-sweep audit calls the form wrong: mis-parsed, dropped segment, missing accent, wrong grade or gender) | not found: miss `known-error`, detail `known error: <note>`; the text fails |

Where the status lives: `displaced_status` and `displaced_why` on the override line in `data/lexicon/overrides.jsonl`. `classify_lexicon.py` copies them into the displaced entry of `extra_specs` (`status`, `status_note`). A displaced spec without a classification defaults to legacy. A second Wiktionary table (not displaced) is `supported`.

How the validator uses it (`pie/validate.py`):
- Every `Analysis` carries `status` and `note`. A token takes the best status among its analyses at the first tier that matches. So a cell the primary and a rejected spec share (fish NOM.SG *dʰǵʰúHs*) stays primary, and a rejected string that is also another lexeme's valid form validates as that form.
- When an override displaced a table's spec, the verbatim Wiktionary cells of that table (`wiktionary-cell`) take the displaced status. Otherwise they would let the same error back in (*gʷénh₂s*).
- A headword or variant that only a legacy or rejected spec generates takes that status: the unaccented headword *dinos* is rejected, the old headword *yókʷr̥* legacy.
- A token that matches only rejected forms is a known error unless a clitic or augment parse gives a valid analysis.
- Quality gates: `all_exact(v)` (coverage 1.0 and every token at tier `exact`) counts only primary and supported forms. `scripts/realize_plans.py` uses it for its `all_exact` gate. Tier 1 (`pie/tier1.py`) and Tier 2 (`scripts/build_tier2.py`) set `verified` from `tier == "exact"`, which a legacy match (tier `legacy`) and a known error (not found) never reach. `Lexicon.cells` (pie/realize.py) reads only the primary `spec`, so the realizer never generates a displaced form; no change there.
- `validate_text` also returns `legacy` (surfaces), `known_errors` (`surface: known error: ...`) and `accentless` (the accent lint, below).

## Classification of the 63 displaced specs

10 supported, 8 legacy, 45 rejected. Each override's note was read. The "displaced" column lists the fields where the displaced spec differs from the primary.

Notes on particular cases:
- Gender only (*déywih₂*, *h₃rḗǵnih₂*, *néptih₂*, *pótnih₂*, *wl̥kʷíh₂s*): the displaced spec had gender m. Its cells are identical to the primary's, so the rejection never applies to a form. It is listed for completeness.
- Rejected but never firing: two more lexemes have no string of their own. *h₁áyt*'s weak *h₁i-* forms (*h₁idʰí*) are valid forms of *h₁éyti* 'go', the confusion the override note describes, and they validate as 'go'. *h₃mígʰleh₂*'s unaccented forms (*h₃migʰleh₂*) are also the primary cells of the duplicate lexeme `pie-lex-h3mighleh2-2`, whose unusable shape spec is unaccented. The accent lint flags them, but they still validate exact through the duplicate (a lexicon question, left open).
- Check: every realizer cell (`Lexicon.cells`, first form, all usable lexemes, three genders for adjectives: 197,217 forms) validates without a legacy or rejected status, so the gate cannot fail on the engine's own output.
- Mixed (*swéh₂dus*, *h₁léngʰus*): the root accent is a convention alternative (i-u-stems #1), but the same displaced spec also carries a diagnosed error: zero-grade oblique *suh₂déw-* (i-u-stems #9), and the gʰ/gʷʰ mix (#12). The whole spec is therefore legacy. The root-accented nominatives (*swéh₂dus*, the headword) validate as legacy, not exact. A clean root-accented alternative would need its own spec.
- Contested, so legacy rather than rejected: *h₂ḱn̥-* (Asno's law, an open question in INTEGRATION.md), *tń̥neh₂* (no handbook has the word), acrostatic *h₃réǵ-*, *h₂yuh₁n̥téh₂*, feminine 'one' *sih₂*, *yókʷr̥*.
- LIV's prevocalic weak stems (*ul-*, *un-*, *Hur-*) and lost breves (*h₂ur̥g-*, *gul̥-*, *ul̥h₁-*): rejected. athematic-verbs.md S1 calls them "uncontroversial data fixes", and the displaced spec turns the notation into wrong strings before a consonant (*undʰí*).

| Lexeme | Headword | Status | Displaced | Why |
|---|---|---|---|---|
| `pie-lex-bhengjhus` | bʰénǵʰus | supported | m_strong bʰénǵʰu | root-accented first Wiktionary table of a u-adjective (convention i-u-stems #1) |
| `pie-lex-dedeh3ti` | dédeh₃ti | supported | weak dédh₃ | Ringe 2006 p. 28 fixed weak dédh₃-, kept as the alternative (convention D2) |
| `pie-lex-dlewkus` | dléwkus | supported | m_strong dléwku | root-accented first Wiktionary table of a u-adjective (convention i-u-stems #1) |
| `pie-lex-gwreh2us` | gʷréh₂us | supported | m_strong gʷréh₂u | root-accented first Wiktionary table of a u-adjective (convention i-u-stems #1) |
| `pie-lex-h1edti` | h₁édti | supported | strong h₁éd, weak h₁d | Wiktionary's ordinary root present h₁dénti, kept as the alternative (convention D1) |
| `pie-lex-h1werHus` | h₁wérHus | supported | m_strong h₁wérHu | root-accented first Wiktionary table of a u-adjective (convention i-u-stems #1) |
| `pie-lex-kjeytor` | ḱéytor | supported | mid_t_less False | middle -tor/-n̥tor, kept as the alternative (convention D5) |
| `pie-lex-lowh3trom` | lówh₃trom | supported | strong léwh₃tro | Wiktionary's other table, e-grade léwh₃trom (thematic.md defect 5: 'Wiktionary has both tables'; the defect was the mixing) |
| `pie-lex-mregjhus` | mréǵʰus | supported | m_strong mréǵʰu | root-accented first Wiktionary table of a u-adjective (convention i-u-stems #1) |
| `pie-lex-pleth2us` | pléth₂us | supported | m_strong pléth₂u | root-accented first Wiktionary table of a u-adjective (convention i-u-stems #1) |
| `pie-lex-h1lenghus` | h₁léngʰus | legacy | m_strong h₁léngʰu, f_strong h₁ln̥gʰéwih₂, f_weak h₁ln̥gʰuyéh₂ | mixed: the root accent is a convention alternative, but the same spec mixes gʰ/gʷʰ (i-u-stems #12) |
| `pie-lex-h2ekjmox` | h₂éḱmō | legacy | weak h₂ḱn̥ | Wiktionary weak h₂ḱn̥- (Asno's law) vs h₂ḱmn-: an open question (INTEGRATION.md 'not applied') |
| `pie-lex-h2yuHnteh2` | h₂yuHn̥téh₂ | legacy | strong h₂yuh₁n̥téh₂ | table h₂yuh₁n̥téh₂ (specific h₁) vs the lemma's H; the project follows the lemma (feminine.md D8) |
| `pie-lex-h3rexgjs` | h₃rḗǵs | legacy | weak h₃réǵ, accent_class acrostatic, loc_sg [] | acrostatic h₃rḗǵs ~ h₃réǵ-; the project follows lengthened grade throughout (t003 review, s-root-heteroclite F7) |
| `pie-lex-sexm` | sḗm | legacy | f_strong sih₂, f_weak None | feminine 'one' sih₂ without a weak stem; Fortson, Beekes, Ringe sm-ih₂ (feminine.md D11) |
| `pie-lex-sweh2dus` | swéh₂dus | legacy | m_strong swéh₂du, m_weak suh₂déw, f_strong suh₂déwih₂, f_weak suh₂duyéh₂ | mixed: the root accent swéh₂dus is a convention alternative, but the same spec's zero-grade oblique suh₂déw- is diagnosed wrong (i-u-stems #9) |
| `pie-lex-tnneh2` | tn̥néh₂ | legacy | strong tń̥neh₂ | root-accented table tń̥neh₂; no handbook has the word, the lemma's oxytone is followed (feminine.md D10) |
| `pie-lex-yokwr` | yḗkʷr̥ | legacy | strong yókʷr̥ | old headword yókʷr̥, kept as a lexicon variant; Ved. yákr̥t excludes *o (s-root-heteroclite F2) |
| `pie-lex-HeHkjus` | HéHḱus | rejected | m_strong HéHḱu, m_weak HHḱéw, f_strong HHḱéwih₂, f_weak HHḱuyéh₂ | root-accented HéHḱus and zero-grade HHḱéw- are wrong: oxytone, full-grade oblique (t021 review, i-u-stems #8) |
| `pie-lex-Hroth2os` | Hroth₂ós | rejected | m_strong Hroth₂ó | the oxytone table Hroth₂ó- is the agentive adjective 'running', not 'chariot' (thematic.md defect 3) |
| `pie-lex-Hrughis` | Hrugʰís | rejected | strong Hréwgʰi, accent_class proterokinetic | the table's strong Hréwgʰi- gave acc. Hréwgʰim beside nom. Hrugʰís (i-u-stems #11) |
| `pie-lex-Hwert` | Hwért | rejected | weak Hur | LIV's prevocalic weak Hur- mis-read as a stem for every environment (athematic-verbs S1) |
| `pie-lex-bheh2gjhus` | bʰeh₂ǵʰús | rejected | strong bʰéh₂ǵʰu | the table's strong bʰéh₂ǵʰu- gave acc. bʰéh₂ǵʰum beside nom. bʰeh₂ǵʰús (i-u-stems #11) |
| `pie-lex-bhreh2texr` | bʰréh₂tēr | rejected | loc_sg [] | loc. bʰréh₂tri is wrong: full-grade suffix bʰréh₂ter(i) (r-n-stems defect 5) |
| `pie-lex-bhuHt` | bʰúHt | rejected | weak bʰúH | accented weak stem gave bʰúHn̥t, bʰúHyeh₁t; Ringe and Vedic accent suffix and ending (athematic-verbs D4) |
| `pie-lex-dayh2wexr` | dayh₂wḗr | rejected | weak dayh₂ur | Wiktionary's weak dayh₂ur- gave dat. pl. dayh₂urbʰós, not dayh₂wr̥bʰós (r-n-stems defect 4) |
| `pie-lex-deh2nu` | déh₂nu | rejected | weak deh₂nu, accent_class amphikinetic, loc_sg [] | the Wiktionary weak arg is the strong stem minus its accent: a parsing error (i-u-stems #4) |
| `pie-lex-deywih2` | déywih₂ | rejected | gender m | spec gender m for an ih₂ noun (feminine.md housekeeping) |
| `pie-lex-dhegjhoxm` | dʰéǵʰōm | rejected | weak ǵʰm̥, gender m, loc_sg ['ǵʰém'] | the Wiktionary weak ǵʰm̥- drops the dʰ (t012 review); gender m was wrong (t014 review) |
| `pie-lex-dhgjhuHs` | dʰǵʰúHs | rejected | weak dʰǵʰúH-o, accent_class acrostatic | Wiktionary's arg 2 dʰǵʰúH-o is a thematization note mis-parsed as the weak stem (dat. dʰǵʰúHoey, gen. pl. dʰǵʰúHoōm) (s-root-heteroclite F6) |
| `pie-lex-dhubhros` | dʰubʰrós | rejected | m_strong dʰubró | the table arg dʰubró- drops the root aspirate (thematic.md defect 4) |
| `pie-lex-dhugh2texr` | dʰugh₂tḗr | rejected | weak dʰugtr̥, gender m | the table's weak stem dʰugtr̥- drops the h₂ (tier3-t003 review) |
| `pie-lex-dinos` | dinos | rejected | strong dino | unaccented headword stem (thematic.md defect 6) |
| `pie-lex-dusmenexs` | dusménēs | rejected | strong dusmenes, weak dusmenes, nom_sg dusmenēs | the table stem was unaccented, giving gen. dusmenesés (s-root-heteroclite F10) |
| `pie-lex-gjhesoxr` | ǵʰésōr | rejected | weak ǵʰsr̥, loc_sg ['ǵʰsér'] | zero-grade weak ǵʰsr̥- is wrong: ǵʰesr- (r-n-stems defect 6) |
| `pie-lex-gjhorneh2` | ǵʰórneh₂ | rejected | strong ǵʰorneh₂ | the table stem lacks the accent (feminine.md D7) |
| `pie-lex-gjhwexr` | ǵʰwḗr | rejected | strong ǵʰwér, weak ǵʰwr̥, accent_class hysterokinetic, nom_sg None, loc_sg [] | the er-stem rule's zero-grade weak ǵʰwr̥- is wrong: lengthened grade throughout (lexicon gaps 2026-10-23) |
| `pie-lex-gwelt` | gʷélt | rejected | weak gul̥ | LIV's weak gul̥- lost the labiovelar (athematic-verbs S1) |
| `pie-lex-gwexn` | gʷḗn | rejected | gender m, nom_sg None | unsourced sigmatic nom. gʷénh₂s and voc. gʷénh₂ as primary (feminine.md D4); bare gʷénh₂ stays a cell of the primary |
| `pie-lex-h1ayt` | h₁áyt | rejected | weak h₁i | weak h₁i-: a root with *a does not ablaut (tier3-t002 review) |
| `pie-lex-h2eryeti` | h₂éryeti | rejected | strong h₂érye | the Wiktionary form h₂éryeti drops the h₃ of *h₂erh₃- (t014 review) |
| `pie-lex-h2wergt-2` | h₂wérgt | rejected | weak h₂ur̥g | LIV's h₂ur̥g- with a lost breve: two adjacent nuclei (athematic-verbs S1) |
| `pie-lex-h2werst` | h₂wérst | rejected | weak h₂ur̥s | LIV's h₂ur̥s- with a lost breve: two adjacent nuclei (athematic-verbs S1) |
| `pie-lex-h3mighleh2` | h₃mígʰleh₂ | rejected | strong h₃migʰleh₂ | the table stem lacks the accent: 17/18 cells accentless (feminine.md D3) |
| `pie-lex-h3rexgjnih2` | h₃rḗǵnih₂ | rejected | gender m | spec gender m for an ih₂ noun (feminine.md housekeeping) |
| `pie-lex-keh2nmn` | kéh₂nmn̥ | rejected | weak kh₂nmén | weak kh₂nmén- lacks the syllabic n̥ (r-n-stems defect 3) |
| `pie-lex-kjmtogwus` | ḱm̥tógʷus | rejected | m_weak ḱm̥tógʷów, f_strong ḱm̥tógʷówih₂, f_weak ḱm̥tógʷuyéh₂ | Wiktionary's args carry two accents per form (feminine.md D12, i-u-stems #14) |
| `pie-lex-meh2texr` | méh₂tēr | rejected | loc_sg [] | loc. méh₂tri is wrong: full-grade suffix méh₂ter(i) (r-n-stems defect 5) |
| `pie-lex-neh2us` | néh₂us | rejected | strong néh₂u, weak n̥h₂éw, accent_class proterokinetic | the shape rule's zero-grade nh₂éw- is wrong: full-grade root throughout (i-u-stems #6) |
| `pie-lex-neptih2` | néptih₂ | rejected | gender m | spec gender m for an ih₂ noun (feminine.md housekeeping) |
| `pie-lex-perkus` | pérkus | rejected | strong pérku | delabialized strong pérku- gave nom. pl. pérkewes (i-u-stems #13) |
| `pie-lex-potnih2` | pótnih₂ | rejected | gender m | spec gender m for an ih₂ noun (feminine.md housekeeping) |
| `pie-lex-sh2eytlom` | sh₂éytlom | rejected | strong sh₂eytlo | the table arg lacks the accent of the headword (thematic.md defect 5) |
| `pie-lex-strneh3ti` | str̥néh₃ti | rejected | weak str̥nh₃é | the table's weak str̥nh₃é- gave ipv. str̥nh₃édʰi (lexicon gaps 2026-10-23) |
| `pie-lex-swesoxr` | swésōr | rejected | weak susr̥, gender m, loc_sg ['susér'] | zero-grade weak susr̥- is wrong: swesr- (t017 review) |
| `pie-lex-teh2ngsmn` | téh₂ngsmn̥ | rejected | weak th₂ngsmén | weak th₂ngsmén- lacks the syllabic n̥ (r-n-stems defect 3) |
| `pie-lex-tetkjox` | tétḱō | rejected | weak tḱn̥, loc_sg ['tḱén'] | the Wiktionary weak tḱn̥- drops the reduplication (t017 review) |
| `pie-lex-tetkjti` | tétḱti | rejected | weak ttḱ | the shape rule's weak ttḱ- deleted the root's only vowel (athematic-verbs S2) |
| `pie-lex-wekwsperos` | wekʷsperos | rejected | strong wekʷspero | unaccented headword stem (thematic.md defect 6) |
| `pie-lex-welh1t-2` | wélh₁t | rejected | weak ul̥h₁ | LIV's ul̥h₁- with a lost breve: two adjacent nuclei (athematic-verbs S1) |
| `pie-lex-welt` | wélt | rejected | weak ul | LIV's prevocalic weak ul- mis-read as a stem for every environment (athematic-verbs S1) |
| `pie-lex-went` | wént | rejected | weak un | LIV's prevocalic weak un- mis-read as a stem for every environment: undʰí (athematic-verbs S1) |
| `pie-lex-wlkwih2s` | wl̥kʷíh₂s | rejected | gender m | spec gender m for an ih₂ noun (feminine.md housekeeping) |

## Second Wiktionary tables (not displaced): supported

33 lexemes carry a further Wiktionary table in `extra_specs` (a second accent class and the like). They are supported: *Héh₂mr̥*, *bʰúHt*, *bʰudʰmḗn*, *déḱm̥t*, *dléwkus*, *dusménēs*, *gʰóstipotis*, *ǵʰéyōm*, *ǵʰéyōm*, *gʷémtis*, *gʷréh₂us*, *h₁léngʰus*, *h₁wérHus*, *h₂énǵʰus*, *h₂énts*, *h₂ṓms*, *h₃bʰrúHs*, *léymō*, *lówh₃trom*, *mréǵʰus*, *néḱus*, *pléth₂us*, *pótis*, *spéḱs*, *ténh₂us*, *wiḱpótis*, *wódr̥*, *wósh₂r̥*, *wósn̥*, *wósn̥*, *wósr̥*, *wósr̥*, *yḗkʷr̥*.


## Effect

In the index, 1,395 exact-tier strings now match only rejected forms and 179 only legacy forms, across 46 lexemes. Before this change all of them validated as exact. Another 1,459 strings are supported-only and stay exact.

Whole stored corpus (corpus/tier1, tier2, tier3: 42,874 tokens) revalidated before and after the change: **0 tokens change status**. No exact token becomes legacy or rejected, and nothing else changes. The realizer builds only from the primary `spec` (`Lexicon.cells`), and no scholarly Tier 1/Tier 2 text writes one of the displaced forms. So the defect was latent in the stored corpus. It affected validation of new text, such as an agent-written or imported line using *dʰǵʰúHoey*.

## Accent lint

`validate_text(...)["accentless"]` lists every found token written without an accent mark. The palatal acute of *ḱ, ǵ* does not count as an accent. Enclitic tokens are exempt (`-kʷe`), as are the closed-class forms closed_class.json writes unaccented (particles such as *ne*, enclitic pronouns, the indefinite *kʷis*) and the enclitic or postpositive lexicon particles in `ACCENTLESS_LEXEMES` (*gʰe, bʰo, ḱe, -kʷe, u, -we, ō*). The lint is a warning: it does not change `status` or the tier.

Stored corpus hits: Tier 3, 235 tokens; Tier 1, 84; Tier 2, 1. Morphology is not fixed here: accentless optatives are being fixed in pie/morph.py in a separate branch.
- Tier 3: vocative *ph₂ter* / *ph₂teres* 87, from the vocative retraction onto a syllable with no vowel. The adverb *h₂ew* 84, unaccented in the lexicon. Unaccented thematic headwords that predate the make_slice gate (thematic.md "Gating"), 49: *werdʰom* 9, *ḱerh₂wos* 6, *h₁eh₂nos* 6, *srowmos* 6, *ǵʰleystos* 4, *h₂eysos* 4, *wēdos* 4, *h₁rudʰyos* 3, *gurnos* 2, *deynos* 2, *ǵʰeh₁ros*, *waylos*, *gewlos* 1 each. Past *h₂emset/h₂emsom* 6 and *teh₂yet* 1. *h₁eǵʰ* 4, *gʰlindeti* 1, *ph₃te* 1, *sēmi* 1. Optative *dedh₃ih₁t* 1.
- Tier 1: source versions printed without accents (Schleicher-fable versions 67, King and God 15, formulas 2).
- Tier 2: *ph₂ter* 1.
