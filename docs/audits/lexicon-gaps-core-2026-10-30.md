# Lexicon gaps for the core concept lists (2026-10-30)

`scripts/build_holdout.py` `concept_matches` covers the Swadesh-207, Leipzig–Jakarta and conversational-core lists. It found no usable lexeme for 53 open-class concepts. Pronouns, numerals and conjunctions are handled by `data/morph/closed_class.json` and were skipped. The coordinator added 7 concepts that the t036 council planner had not found: decide, choose, council/assembly, wise, enemy, fight and other.

For each concept I worked down the same ladder as `lexicon-gaps-dialogue-2026-10-30.md` and stopped at the first rung that held:

1. **An existing entry, fixed in `overrides.jsonl`.** The fix is a gloss, form, pos or spec, and the lexicon is rebuilt.
2. **A project reconstruction.** This needs one formation in at least 2 branches.
3. **A Tier 3b neologism.**

Archaic comes first, per the owner (2026-10-30). Many concepts already had a usable word that the matcher missed because of the gloss wording ('to be carrying', 'bloom', 'gut, intestine'). For those, the fix is only the wording.

Sources (read in `raw/books/text/`): M&A = Mallory & Adams 2006; Kroonen 2013; de Vaan 2008; Beekes 2010; Matasović 2009; Derksen 2008/2015; LIV²; EWAia; Kloekhorst 2008; Martirosyan 2010; NIL 2008. Each override `note` names its source and locator. No book text is quoted.

## Result

| concept | rung | lex_id | form | gloss (tag first) | evidence | rejected, and why |
|---|---|---|---|---|---|---|
| human being / person | 1 (gloss) | pie-lex-mortos | mórtos m. | mortal, human being, person, man | M&A §11.7 *mórtos 'person, mortal' (dial. Gk μορτός, Av. marəta-, Skt márta- 'person, mortal'); §12.1 | ǵʰmṓ 'human': the sources disagree on the accent (vocab-push.md), so it gets no spec |
| child | 1 (gloss) | pie-lex-tekjnom | téḱnom n. | child, offspring; young (of an animal) | Beekes s.v. τέκνον 'child, young animal' (Il.) < *tek- 'beget'; M&A §11.6 *tek- 'bear a child' (Skt tákman- 'child'). The -no- neuter is Greek only (stated, as h₂mélǵos) | bʰornom (PGmc *barna- 'child', Kroonen): no accent (P10). suHnús is 'son' |
| small / little | 1 (pos + gloss) | pie-lex-peh2uros | péh₂uros adj. | small, little; few | de Vaan s.v. parvus (Lat. parvus < *peh₂u-ro-, Gk παῦρος 'little'); M&A §19.2 *pau- 'little, few'. Same -ro- adjective in Italic and Greek | dʰébʰus (NIL 'little, small'; Hitt. tēpu-, Kloekhorst): Hittite-only u-stem, with a *noun* spec (f). It is in make_slice EVERYDAY: see Notes |
| tail | 1 (gloss + flag) | pie-lex-h1orseh2 | h₁orséh₂ f. | tail | NIL no. 247 (MIr. err, Gk οὐρά); Beekes s.v. οὐρά (OIr. err f. 'tail' < *h₁ers-h₂-). Two branches, so the nil-single-branch flag is lifted and the word added to NIL_ADMIT | *puk- (Skt púccha-): no entry. *wólos: horse-tail hair only |
| leg, thigh | 1 (gloss) | pie-lex-skelos | skélos n. | leg, thigh | Beekes s.v. σκέλος 'thigh, leg' (Il.; Myc. ke-re-a₂) < *skel- 'bend'; M&A §18.5 (OPr. culczi 'thigh'). One lexeme covers both concepts | pṓds 'foot' already covers Leipzig–Jakarta 'leg/foot'. *sókʷt(H)- 'thigh': no entry, and formations differ (Kloekhorst '?'). ḱlównis is 'hip', tpḗrsneh₂ 'heel' |
| bark | 1 (gloss) | pie-lex-lowbhos | lowbʰós m. | bark, bast, rind (of a tree) | M&A §10.1 *lóubʰo/eh₂- 'bast, bark' (Lith. luõbas, Ru. lub, Alb. labë); Derksen s.v. luobas, *lubъ. Balto-Slavic formation; Derksen raises a substrate (b/p) | Lat. cortex: Latin only (de Vaan). The *(s)kor- group: no entry |
| flower | 1 (gloss) | pie-lex-h2endhos | h₂éndʰos n. | flower, bloom, blossom | M&A §10.2 *h₂éndʰes- 'flower' (Alb. ëndë 'flower', Gk ἄνθος, Arm. and, Skt ándhas-) | — |
| grass | 1 (gloss) | pie-lex-ghreh1mn | gʰréh₁mn̥ n. | grass, herbage | de Vaan s.v. grāmen (*gʰr̥h₁-mn̥, to *gʰreh₁- 'grow'); Kroonen s.v. *grasa- (Lat. grāmen < *gʰr̥h₁-mn-). Italic-only formation, root also Germanic. M&A §10.2: no PIE 'grass' | A Tier 3b derivative gʰréh₁mn̥ was drafted. The engine refused it: the form already exists as pie-lex-ghreh1mn, so rung 1 holds. tr̥nós 'thorn': 'grass' is Indo-Iranian only |
| belly | 1 (gloss) | pie-lex-uderos | úderos m. | belly, abdomen, stomach | de Vaan s.v. uterus 'belly, womb' (*(H)ud-er-o-; Skt udára- 'belly'); EWAia s.v. udára- 'Bauch'; M&A §11.5 | — |
| guts / entrails | 1 (gloss) | pie-lex-gjhorneh2 | ǵʰórneh₂ f. | gut, intestine; guts, entrails | M&A §11.5 *ǵʰorHneh₂- 'entrails'; Kroonen s.v. *garnō- 'intestines' < *ǵʰór-n-eh₂-, Lith. žarnà | — |
| ice | 1 (gloss) | pie-lex-h1yegos | h₁yégos m. | ice, frost | Kroonen s.v. *jeka(n)- 'ice' < *ieg-o(n)-; Kloekhorst s.v. eka- 'cold, frost, ice' < *iég-o-. Anatolian and Germanic | h₁eygóm (the derived duplicate); h₁eyH- (PGmc *īsa-: Germanic only) |
| shade / shadow | 1 (form: accent) | pie-lex-skjeh3ih2 | sḱéh₃ih₂ f. | shadow, shade | EWAia s.v. chāyā́- (NomSg *sḱéh₃-ih₂, GenSg *sḱh₃-iéh₂-s; Gk σκιά, Alb. hije, Toch. B skiyo); Beekes s.v. σκιά (same paradigm, h₂). The unaccented Wiktionary form stays a variant | sḱih₃wós and the other derived forms mean 'dark, grey' |
| wood | 1 (gloss) | pie-lex-doru | dóru n. | tree; wood, timber | M&A §10.1 *dóru 'wood, tree' (Hitt. tāru, Skt dā́ru, Gk δόρυ); Kloekhorst s.v. tāru 'wood' | h₁widʰh₁us: no accent (previous round) |
| soil | 1 (gloss) | pie-lex-dhegjhoxm | dʰéǵʰōm f. | earth, ground, soil | M&A §8.1 'earth'; de Vaan s.v. humus 'earth, ground' | — |
| goat | 1 (gloss) | pie-lex-kapros | kápros m. | he-goat, billy goat; goat | Kroonen *hafra- 'billy goat' < *kap-ro- (Lat. caper, OIr. gabor; Gk κάπρος 'boar'); M&A §11.4 | *dík-, *h₂eyǵ-, *ǵʰaid-: no usable lexeme (ǵʰaydos is Latin-only thematic, round 2) |
| bad / evil | 1 (pos + gloss) | pie-lex-h2eghos-2 | h₂egʰós adj. | bad, evil, dangerous | EWAia s.v. aghá- (Ved. aghá- 'böse', YAv. aγa- 'schlecht'); Kroonen s.v. *agla-; M&A §20.6. The thematic adjective is Indo-Iranian | dus- (a prefix, already closed:prefix/dus). *ǵʰalh₂ros, *h₂/₃wop-: no entry |
| rotten / rot | 1 (gloss) | pie-lex-puHyeti | púHyeti | to rot, decay, stink | LIV² 2.*peu̯H- (*puH-i̯e-: Ved. pū́yati, YAv. puiieiti); M&A §20.5. 'rotten' is the participle púHyonts | puHtós mixes in pū- 'purify'; puHlos has no accent |
| straight | 1 (gloss) | pie-lex-h3regjtos | h₃reǵtós adj. | straight, right, upright; straightened | Kroonen s.v. *rehta- 'straight' < *h₃reǵ-to- (Av. rāsta-, Gk ὀρεκτός, Lat. rēctus); M&A §18.3 | — |
| smooth | 1 (pos + gloss) | pie-lex-ghlh2dhros | gʰl̥h₂dʰrós adj. | smooth, hairless, bald | de Vaan s.v. glaber (*gʰlh₂dʰ-ro- 'smooth'; root also Balto-Slavic, OHG glat); M&A §20.9. The -ro- formation is Latin only | *leh₁i-u- (Lat. lēvis, Gk λεῖος): no entry, and the formations differ |
| beautiful / pretty | 1 (gloss) | pie-lex-kjubhros | ḱubʰrós adj. | shining, beautiful, pretty; pure, clean (Armenian) | EWAia s.v. śubhrá- 'glänzend, schmuck', ŚOBH 'schön sein'; Martirosyan s.v. surb. The 'beautiful' sense is Indic | *kal- (Gk καλός, Skt kalyāṇa-): no entry. ḱowbʰéh₂ (NIL, Vedic only) |
| happy / glad | 1 (gloss) | pie-lex-mudros | mudrós adj. | glad, happy, cheerful, lively | EWAia s.v. MOD (Ved. mudrá- 'fröhlich', Lith. mudrùs 'munter'); LIV² *meu̯d-; M&A §20.6. Indo-Iranian and Baltic | tusyéti: derived gloss, one branch |
| rejoice | 1 (gloss) | pie-lex-mewdeti | méwdeti | to rejoice, be glad, be merry | LIV² *meu̯d- (Ved. módate); EWAia s.v. MOD. Indo-Aryan present; the root is also Baltic | *geh₂dʰ- (γηθέω): LIV² calls it a renewal, and Lat. gaudeō is denominative |
| hunt | 1 (gloss) | pie-lex-wregeti | wrégeti | to hunt, track, pursue | LIV² *u̯reg- (*u̯rég-e-: Ved. vrájant-, Go. wrikan); Kroonen s.v. *wrekan- (ON reka 'hunt'); M&A §22.15 | h₂éǵreh₂ (NIL: nil-uncertain + single branch). h₂eǵro- (bare stem) |
| walk | 1 (gloss) | pie-lex-steygheti | stéygʰeti | to walk, stride, march; to climb, step up | LIV² *stei̯gʰ- (Gk στείχω 'go, march', OIr. tíagu, Go. steigan); Kroonen s.v. *stīgan- | gʷm̥sḱéti ('come'). ǵʰengʰ- derivatives (one branch each) |
| rub | 1 (gloss) | pie-lex-teryeti | téryeti | to rub, rub away, wear down | LIV² *terh₁- 'reiben' (Gk τείρω; Slavic ye-relics); de Vaan s.v. terō. The headword lacks Wiktionary's -h₁- | An athematic *térh₁ti: no daughter keeps it. gʰréndʰeti means 'grind' |
| freeze / be cold | 1 (gloss) | pie-lex-goleti | góleti | to be cold, freeze | Kroonen s.v. *kalan- 'to be cold' (ON kala 'freeze') < *gólH-e-; de Vaan s.v. gelus. Germanic-only formation | stéwdt: a root aorist with no present |
| cough | 1 (form + pos + gloss) | pie-lex-kweh2se | kʷéh₂seti | to cough | Kroonen s.v. *hwōsan- (OE hwōsan) < *kʷeh₂s-e-; LIV² *kʷeh₂s- 'husten'; M&A §11.6 (the best-attested 'cough'). Bare stem kʷéh₂se- → present headword, root accent as Skt kā́sate (EWAia and LIV call it late) | No project row: the stem exists |
| smell | 1 (gloss) | pie-lex-h3edeti | h₃édeti | to smell, give off a smell; to smell (something) | de Vaan s.v. odor (PIt. *ode/o-; Gk ὄζω, Arm. hot, Lith. úosti); LIV² 1.*h₃ed- | gʷʰreh₁- (Ved. jíghrati only) |
| carry | 1 (gloss) | pie-lex-bhereti | bʰéreti | to carry, bear; to be carrying (present) | M&A §3.1, §4.8 (Table 4.11 *bher- 'carry') | — |
| show | 1 (gloss) | pie-lex-deykjeti, pie-lex-dexykjst | déyḱeti, dḗyḱst | to show, point out | LIV² 1.*dei̯ḱ- 'zeigen' (present *déi̯ḱ-e-; s-aorist Gk ἔδειξα) | dékʷseti (Indo-Iranian, derived) |
| be silent | 1 (gloss) | pie-lex-th2keh1yeti | th₂kéh₁yeti | to be silent, keep silent | Kroonen s.v. *þagēn- < *tHk-eh₁- (Go. þahan), 'identical to Lat. tacēre'; de Vaan s.v. taceō. Italic and Germanic | ḱlusrós (NIL, Arm. lur only; left as it is) |
| hate | 1 (pos + spec + gloss) | pie-lex-h3eh3ode-2 | h₃eh₃óde (perfect) | to hate | LIV² 2.*h₃ed- (perfect only: Lat. ōdī); de Vaan s.v. ōdī. Italic-only formation; spec checked by hand (stative, as wóyde) | ḱéh₂dos is a noun. dweys- (Indo-Iranian, no lexeme). h₃odéyeti (PGmc 'incite') |
| be tired | 1 (pos + spec + gloss) | pie-lex-kjekjomh2e | ḱeḱómh₂e (perfect) | to be tired, be weary (from toil) | LIV² *ḱemh₂- (perfect: Ved. śaśāma, Hom. κεκμηώς 'tired'); Beekes s.v. κάμνω. Two branches | méh₃yeti: its reflex-confirmed 'to get tired' reverses Kroonen's transitive 'to tire'. It was regloss-ed 'to tire, wear out' |
| teach | 1 (gloss) | pie-lex-kjeHst | ḱéHst | to instruct, teach; to direct | LIV² *ḱeHs- (Ved. śā́sti 'instruct', OAv. sīšā 'teach!', Alb. thom) | *dens- (no lexeme). Tier 3b doḱéyeti (pie-neo-teach) already exists |
| lack | 1 (gloss) | pie-lex-h1egos | h₁égos n. | lack, need, want | de Vaan s.v. egeō (*h₁eg-es- 'lack, need'); LIV² ?*h₁eǵH-. Italic-only s-stem | dews- (Gk only). h₁uh₂nós (NIL) |
| thank | 1 (gloss: the adjective) | pie-lex-gwrHtos | gʷr̥Htós adj. | praised, welcome; pleasing; grateful, thankful | de Vaan s.v. grātus (*gʷr̥H-to-: Skt gūrtá- 'welcome', Lith. girtas 'praised', Lat. grātus 'thankful', grātēs 'thanks'). No PIE thanking formula reconstructs | No 'thank' sense was added to gʷr̥néHti: it is attested as 'praise, welcome', never 'thank'. The inherited idiom is praising the giver (gʷr̥néHti). Tier 3b gʷr̥Htís 'thanks' exists. The matcher still misses 'thank' |
| morning | 1 (gloss, adverb) | pie-lex-h2eyeri | h₂éyeri adv. | early; morning, in the morning | M&A §18.6 *h₂eyer- 'early' (Gk ἦρι, ἠέριος 'of the morning'). Offered through slice_adverbs | h₂éwsōs is 'dawn'. *kʷtus is Germanic |
| near | already covered | pie-lex-h1epi, pie-lex-kjom, pie-lex-h2enti | h₁épi, ḱóm, h₂énti adv. | on, at, near … | Offered through slice_adverbs (indeclinables have no spec, so `offered()` never lists them) | — |
| decide | 1 (gloss) | pie-lex-h2reh1dheti | h₂réh₁dʰeti | to counsel, advise; to decide; to plan, consider | Kroonen s.v. *rēdan- 'to decide' < *Hreh₁dʰ-e- (OE rǣdan, OHG rātan, ON ráða). Germanic present; the root is also Indo-Iranian | rékt (a root aorist, 'arrange, fix') |
| council / assembly | 1 (gloss) | pie-lex-dhh1tleh2 | dʰh₁tléh₂ f. | assembly, meeting, council; debate | Matasović s.v. *datlā 'assembly' (OIr. dál, MW dadl). Celtic only; the etymology is disputed | sedtlóm (NIL, one branch) |
| wise | 1 (gloss) | pie-lex-gjnh3ros | ǵn̥h₃rós adj. | knowing, experienced, wise | de Vaan s.v. gnārus 'knowing, experienced' (*ǵn̥h₃-ro-). Italic-only adjective | widris (no spec). widwṓs 'knowing' is the other archaic way |
| enemy | 1 (gloss) | pie-lex-poykjos-2 | póyḱos m. | enemy, foe; hostile one | Kroonen s.v. *faiha- 'hostile' (OE fāh, E foe) < *póiḱ-o-; OIr. óech 'enemy'. Germanic and Celtic | gʰóstis keeps 'stranger, enemy'. Only Latin has 'enemy', so a speaker would hear 'guest' |
| choose, fight, other, woman, young | already covered | wolh₁éyeti / wélh₁t, wikéti / kéh₃tus, h₂élyos, gʷḗn, h₂yuHn̥ḱós | — | glosses already carry the word | In the pool and in CONVERSATION (bd533a1): the t036 slice had squeezed them out with the size cap | — |
| count | 3 (calque) | pie-neo-count | kʷéyteti | to count, reckon | kʷéyteti 'notice' (Ved. cétati) in the sense its Balto-Slavic relatives gave the root: OCS čьtǫ 'count, read', Lith. skaitýti (LIV² *kʷei̯t-) | *h₂rey- has only nouns (OIr. rím, OE rīm, Gk ἀριθμός). Lat. reor is Latin only. h₂rinéHti is OIr. 'sells' |
| bury | 3 (derivative) | pie-neo-dhmbhyeti | dʰm̥bʰyéti | to bury | Zero grade + -yé-: LIV² 2.*dʰembʰ- present *dʰm̥bʰ-i̯e- (Gk θάπτω). Arm. damban 'grave' is a noun; Martirosyan suspects an Armeno-Greek substrate word | Gmc *burgjan (LIV '?'). Go. filhan (Germanic only) |
| answer | 3 (exists) | pie-neo-h2enterowekwos | h₂enterowékʷos | answer | The coinage exists from an earlier round. The archaic idiom is preverb + 'speak' (Ved. práti-brav-, OAv. paiti.mrauu: próti + mléwHti, EWAia s.v. práti) | No simplex PIE verb. The engine has no preverb compounds |
| lose | paraphrase | — | — | — | No PIE transitive 'lose'. The idiom is néḱt 'vanish, be lost' (EWAia s.v. NAŚ: naṣṭá- 'verloren'), or noḱéyeti 'make vanish' | Go. fra-liusan (Germanic only). deh₂p- (no usable entry) |
| open | paraphrase | — | — | — | LIV² *Hu̯er-: 'open' occurs only with a preverb of removal (Ved. ápa vṛ, Lat. aperiō < *ap-wer-, OCS ot-voriti), so h₂epó + Hwért | *reu̯h₁- (Tocharian only). *h₃u̯ei̯g- (Greek only). An idiom gloss on Hwért (past only) was not added |
| round | paraphrase | — | — | — | No PIE adjective. Each branch derives its own (Lat. rotundus from rota, Gk στρογγύλος); use kʷékʷlos 'wheel; circle' | wr̥ttós 'turned': derived gloss, no 'round' sense in the sources |
| today | paraphrase | — | — | — | Each branch builds 'this day' from its own demonstrative and day word (Lat. hodiē, Gk σήμερον, Skt adyá): demonstrative + loc. of dínos | — |
| tomorrow | paraphrase | — | — | — | M&A §18.6: no PIE 'tomorrow'. Gk αὔριον is from 'at dawn' (Beekes); use h₂éyeri | h₂ewsér 'at dawn': the 'tomorrow' sense is Greek only, and it has no spec |
| be ashamed | paraphrase | — | — | — | LIV² ?*ǵʰneu̯-: Indo-Aryan only, uncertain. Gk αἴδομαι ~ Go. aistan is formally uncertain (Beekes) | h₂éǵos 'guilt' (declined in round 2) |
| understand | paraphrase | — | — | — | pret- (LIV ?, Baltic perfect): no lexeme. The inherited verbs of knowing (ǵn̥h₃sḱéti, ǵnéh₃t) carry it. The sources give 'kennen/erkennen', not 'understand' | — |
| louse | paraphrase | — | — | — | M&A §9.5 *lu(s)- is heavily reshaped. Matasović s.v. *luwā. No formation is shared by 2 branches, and the root noun has no engine shape | -níd- 'nit' |
| stick | paraphrase | — | — | — | *ǵʰazdʰo- 'rod' (Go. gazds, Lat. hasta): Kroonen calls it a European loan. βάκτρον / baculum: Beekes asks whether it is a European loanword | h₃ósdos 'branch' and dóru are usable |
| lip | paraphrase | — | — | — | Skt óṣṭha-: Indo-Iranian only (EWAia). Lat. labium / PGmc *lepjan-: a European *b word, one formation per branch (Kroonen) | h₁óh₁s 'mouth' |
| sand | paraphrase | — | — | — | Kroonen s.v. *sanda-: Gmc *samda-, Lat. sabulum and Gk ἄμαθος cannot be reconciled (non-IE). Beekes marks ἄμαθος as European | A calque of ḱórkeh₂ 'gravel': no daughter makes that shift |

Every Tier 3b row is a coinage. pie-neo-count and pie-neo-dhmbhyeti are new; pie-neo-h2enterowekwos, pie-neo-teach and pie-neo-gwrHtis existed before. All are Tier 3b only and flagged `coined: "neologism"`.

## Counts

Counted over the 53 assigned concepts and the coordinator's 7:

- **Rung 1: 42 concepts (38 assigned, 4 added), on 41 lexemes.** These are gloss or wording fixes, plus the pos, form or spec changes noted in the table. skélos covers both leg and thigh. There are 43 override rows: the second 'show' row (dḗyḱst) and the méh₃yeti correction are extra.
- **Already covered: 7 concepts.**
  - near (adverbs);
  - answer, by an existing Tier 3b coinage;
  - choose, fight, other, woman and young (the coordinator's).
- **Rung 2: 0.** Every candidate either already existed in the lexicon (cough, grass, child) or had only one branch for its formation.
- **Rung 3 (Tier 3b): 2 new coinages,** count and bury.
- **Paraphrase: 11 concepts.** lose, open, round, today, tomorrow, be ashamed, understand, louse, stick, lip and sand. thank is counted under rung 1 through the adjective gʷr̥Htós 'grateful'; the verb itself stays a paraphrase.

**Matcher**, rerun with this script's own `concept_matches` (307 concept strings); the hold-out files stay frozen and were not redrawn:

| | before | after |
|---|---|---|
| concepts with no trusted-gloss hit at all, open-class | 11 | 6: answer, round, sand, thank, today, tomorrow |
| concepts with no **offered** lexeme (pool, or slice adverbs), open-class | 56 | 18 |

The 18 after the round:
- Tier 3b, invisible to the matcher: answer, bury, count, forest.
- Paraphrases: be ashamed, lip, lose, louse, open, round, sand, stick, thank, today, tomorrow, understand.
- Not in this round: hair, summer.

## What changed

- **`data/lexicon/overrides.jsonl`: 43 rows.** 40 are new and 3 are merged into an existing row (h₁yégos, ǵʰórneh₂, dʰéǵʰōm), with the notes joined by " | ".
- **Rebuild.** First I ran `build_lexicon.py`, `classify_lexicon.py` and `build_glosses.py` on a scratch copy of the tree and checked it was byte-identical to HEAD. Then the overrides went in, and the scratch result was byte-identical to the repo rebuild.
  - `lexicon.jsonl` changes in exactly the 43 overridden ids.
  - `inflection_specs.jsonl` changes in 7 rows:
    - sḱéh₃ih₂: unknown:devi-no-accent → shape:devi
    - kʷéh₂seti: bare stem → thematic present
    - h₃eh₃óde and ḱeḱómh₂e: hand-checked stative perfects, `kind: stat`
    - péh₂uros, h₂egʰós, gʰl̥h₂dʰrós: thematic noun → thematic adjective
  - None of the 7 ids occurs in corpus/, plans, batches or releases, so no realized text changes.
  - `confirmed_glosses.jsonl` loses méh₃yeti, which now has an override (121 rows).
- **`pie/lexicon.py`.** The override block now applies an `uncertain` key. That is how tail's nil-single-branch flag is lifted on the Beekes evidence.
- **`data/lexicon/neologisms.jsonl` (43 → 45):** pie-neo-count and pie-neo-dhmbhyeti, filled by `pie.neologism --fill`. The first 43 rows are unchanged.
- **Reachability (`scripts/make_slice.py`).**
  - The 37 new rung-1 ids are added to TIER3B_INHERITED, which since fc96006 goes to every slice. ice, wood and soil are in EVERYDAY already.
  - pie-lex-h1orseh2 is added to NIL_ADMIT.
  - These edits were picked up by another agent's commit e4c05ac while this round was running, so they are already in HEAD.
- **Translator.**
  - `pie/translator/lexmap.py` OVERRIDES gets 51 English → lexeme keys. Coinages now reach the translator through `with_neologisms`, and "We count the sheep" and "They bury the dead man" go through.
  - `pie/translator/transfer.py`:
    - The SYNONYMS fallbacks evil → bad, beautiful → fair and child → son are dropped, because those words now have their own lexemes.
    - A stative perfect with no present stem gives the present state (h₃eh₃óde 'hates', wóyde 'knows').
    - The object of a verb of fearing is mapped to ABL. This follows e4c05ac's new check_plan rule, which had broken "Do not fear the wolf!".
- **Pool.** Offered by default goes from 1,391 to 1,414; usable specs go from 4,933 to 4,937.
- **docs/lexicon.md:** the reflex-confirmed count is updated.

## Cells checked

| word | cells |
|---|---|
| sḱéh₃ih₂ f. | acc. sḱéh₃ih₂m, gen. sḱh₃yéh₂s, loc. sḱh₃yéh₂i (EWAia's paradigm) |
| kʷéh₂seti | 1sg. kʷéh₂soh₂, 3pl. kʷéh₂sonti |
| h₃eh₃óde | 1sg. h₃eh₃ódh₂e, 3pl. h₃eh₃dḗr |
| ḱeḱómh₂e | 3pl. ḱeḱm̥h₂ḗr (cf. κεκμηώς) |
| péh₂uros | f. péh₂ureh₂ |
| h₂egʰós | f. h₂egʰéh₂ |
| gʰl̥h₂dʰrós | f. gʰl̥h₂dʰréh₂ |
| téḱnom | gen. téḱnosyo |
| gʰréh₁mn̥ | gen. gʰr̥h₁méns |
| h₁orséh₂ | acc. h₁orséh₂m |
| dʰm̥bʰyéti | 3pl. dʰm̥bʰyónti |
| kʷéyteti | 3pl. kʷéytonti |
| realized | "The small child rubs the goat." → péh₂urom téḱnom káprom téryeti. |
| translator | "The beautiful woman carries the goat." → ḱubʰréh₂ gʷḗn káprom bʰéreti. "The council decides." → dʰh₁tléh₂ h₂réh₁dʰeti. "I hate the wolf." → wĺ̥kʷom h₃eh₃ódh₂e. |

## Notes

- **dʰébʰus.** make_slice EVERYDAY (76e6d34) offers dʰébʰus for 'small'. It has a NIL gloss, a Hittite-only u-stem and a feminine *noun* spec, so its adjective use mis-declines. péh₂uros (Italic and Greek, adjective spec) is the better entry. I did not change EVERYDAY.
- **hair and summer** were outside this round. They are matched (h₂wolh₁ḱos, sm̥h₂eros) but not offered.
- **A pre-existing test failure.** `test_neologisms.py::test_slice_to_export_production_path` asserted that mówdos stays out of the plain slice, which fc96006 deliberately changed. The assertion now reflects the new behaviour.
- **Another test was updated.** test_vocab_push's unaccented-devī example moved from sḱeh₃ih₂, which now has its accent, to bʰerontih₂.

## Tests

- New in `tests/test_vocab_push.py`:
  - each CORE keyword maps to a lexeme that is offered, carries an override gloss and is in TIER3B_INHERITED or EVERYDAY;
  - the matcher finds an offered lexeme for 36 concepts;
  - the 7 spec changes, with a realized sentence;
  - the tail NIL flag.
- New in `tests/test_translator.py`: `test_core_gap_words_reach_the_translator`.
- The named suites:
  - test_neologisms, test_project_reconstructions, test_lexicon, test_vocab_push, test_glosses and test_planner_accent: 166 passed.
  - test_translator (`--group translator`): 21 passed.
- Also run: test_realize, test_validate, test_accent_invariant, test_accent_policy, test_u_adjective_alternatives, test_alt_status, test_lexq and test_conversation_gaps: 125 passed. test_export, matcher and hold-out tests: 2 passed.
