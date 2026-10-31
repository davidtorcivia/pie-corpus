# Lexicon gaps, round 3: war, conversation, the horrors wave, kinship (2026-10-31)

The coordinator's list had three groups: war and exchange, the conversation gaps the t044–t059 planners hit, and the vocabulary of an upcoming wave about raids, famine, plague, feud and death. During the round the t045, t053, t062, t064, t065 and t070 planners added more: worth, debt, lend, too/also, instead, the in-laws, bride, wedding, always, already, like/as, the household and hunting words, wealth, heir, promise, each, ordinals, autumn, month and the weather.

I worked down the ladder of the two earlier rounds (`lexicon-gaps-dialogue-2026-10-30.md`, `lexicon-gaps-core-2026-10-30.md`) and stopped at the first rung that held:

1. An existing entry, fixed in `overrides.jsonl` (gloss, form, pos or a hand-checked spec), then the lexicon is rebuilt.
2. A project reconstruction: one formation in at least 2 branches.
3. A Tier 3b neologism.

Archaic comes first (owner, 2026-10-30). Most concepts already had an inherited word whose gloss lacked the English keyword ('plundering, loot' for booty, 'to cry (vocally)' for weep, 'cattle' for cow). Where there is no word, the concept now gets an **idiom**, an inherited way of saying it, or a stated **paraphrase**. Both live in the new `data/lexicon/idioms.json`, and lexq prints them (Part 2).

Sources, read in `raw/books/text/`: M&A = Mallory & Adams 2006, LIV², Kroonen 2013, Derksen 2008 (Slavic), Matasović 2009, de Vaan 2008, Beekes 2010, EWAia, West 2007, Fortson 2010, and the Handbook of Comparative and Historical IE Linguistics (Klein, Joseph & Fritz 2017). Every override `note` names its source and locator. No book text is quoted.

## Result: words (rungs 1–3)

| concept | rung | lex_id | form | gloss now (keyword first where it matters) | evidence | rejected, and why |
|---|---|---|---|---|---|---|
| booty, spoils | 1 (gloss) | pie-lex-Hrowpos | Hrowpós m. | plunder, booty, spoils; pillage, loot | Kroonen s.v. *rauba- 'loot' (OE rēaf 'spoil, booty', OHG roub) < *Hroup-ó-; Indo-Iranian *Hrawpás | M&A *soru 'booty': no entry |
| boast | 1 (gloss) | pie-lex-h1eh1ughos | h₁éh₁ugʰos n. | vow, solemn utterance, prayer; boast, vaunt | LIV² *h₁eu̯gʷʰ- (Ved. óhate, Gk εὔχομαι 'boast, pray', Lat. voveō); s-stem Gk εὖχος, Ved. óhas- | 'boast' is the Greek sense |
| threaten | 1 (gloss) | pie-lex-tergweti | térgʷeti | to threaten, menace, scold | LIV² *tergʷ- (Skt tarjati 'threatens'); Indic present | — |
| shield | 1 (form: accent, gender) | pie-lex-skeytos | skéytos m. | shield | M&A §15.4 *skeits; Matasović *sketo- < *skeyto-; Derksen *ščitъ m. o (b), OPr. scaytan. AP (b) continues root stress (Derksen, Introduction 2.2.3.2) | skuHtóm (Latin only); skélHtus (Germanic only) |
| battle | 1 (gloss) | pie-lex-keh3tus | kéh₃tus | fight, battle | M&A §17.5 *katu- (OIr. cath 'battle') | Hyudʰyéti (derived gloss; 'fight' is covered) |
| victory | 1 (gloss) | pie-lex-segjhos-2 | séǵʰos n. | victory; might, overpowering | M&A §17.5 (Skt sáhas- 'victory', NHG Sieg, OIr. seg) | séǵʰtōr (NIL gloss, unoffered) |
| brave | 1 (spec, hand-checked) | pie-lex-dhrsus | dʰr̥sús adj. | bold, courageous, daring, brave | M&A §17.5 *dʰers-; Gk θρασύς, Skt dhṛṣú-, Lith. drąsùs. u-adjective spec on the polh₁ús pattern | — |
| pay | 1 (gloss) | pie-lex-kwinewti | kʷinéwti | to pay (a price or penalty), atone | LIV² 3.*kʷei̯- (Gk τίνω); M&A §17.4. Greek-only formation | — |
| repay | 1 (form: accent) | pie-lex-gheldheti | gʰéldʰeti | to pay, repay, requite | LIV² *gʰeldʰ- *gʰéldʰ-e- (Go. -gildan, OCS žlědǫ); Germanic and Slavic, maybe a loan | — |
| avenge | 1 (gloss) | pie-lex-kweyeti | kʷéyeti | to punish, exact a penalty; MID: to avenge oneself | LIV² *kʷéi̯-e- (Ved. cáyate); Beekes s.v. ποινή | — |
| ransom, revenge, blood-price | 1 (gloss) | pie-lex-kwoyneh2 | kʷoynéh₂ f. | payment, compensation, blood-price; ransom, penalty; punishment, vengeance | Beekes s.v. ποινή 'ransom, fine, penalty, vengeance' (Il.); M&A §17.4 | — |
| weep, wail, lament, mourn | 1 (gloss) | pie-lex-HrewdHti | HréwdHti | to weep, wail, lament; to cry (vocally) | LIV² *reu̯dH- (Ved. róditi, OAv. urudən, OLith. raudmi) | **Rung 2 does not apply:** the athematic present is already this entry. ǵʰréh₁deti (Germanic only), HrowdHeh₂yeti (unaccented) |
| calf | 1 (gloss) | pie-lex-wetsos | wetsós adj. | of a year; yearling, calf (as a noun) | EWAia s.v. vatsá- 'calf'; M&A §18.6 | wetelos (Lat. vitulus): no accent |
| summer | 1 (gloss) | pie-lex-semeh2 | sémeh₂ f. | summer; season, year | M&A §18.6 *sem- 'summer'; Kroonen s.v. *sumara- (Skt sámā). Indic-only formation | sm̥h₂eros: no source gives an accent, so it stays unoffered |
| every, all | 1 (gloss) | pie-lex-solh2wos | solh₂wós | whole, entire; all, every | M&A §11.7 *sólwos (Skt sárva- 'all') | See Notes: the spec is a noun |
| also, too | 1 (gloss) | pie-lex-eti-2 | éti adv. | beyond, over; still, also, too; and | de Vaan s.v. et (*h₁eti 'still, also'; Gk ἔτι) | — |
| neighbour | 1 (gloss) + idiom | pie-lex-woykjos-2 | woyḱós | settler, dweller, villager | EWAia s.v. veśá- 'settler'; 'neighbour' is Skt prátiveśa- | — |
| obey | 1 (gloss) | pie-lex-kjlowseyeti | ḱlowséyeti | to listen to, heed, obey | LIV² *ḱleu̯s- (Ved. śróṣan 'they obey', Lith. klausýti 'obey') | — |
| persuade | 1 (gloss) | pie-lex-bhoydheyeti | bʰoydʰéyeti | to make trust; to persuade, prevail upon | LIV² *bʰei̯dʰ- (causative: Go. baidjan, OCS běditi 'compel'; Gk ἔπεισα 'persuaded') | — |
| kick | 1 (gloss) | pie-lex-sprneHti | spr̥néHti | to kick, kick away; to spurn | LIV² *spʰerH- '(mit dem Fuß) stoßen'; nasal present in Lat. spernō and OE spornan | spr̥Héti (Indo-Iranian thematic) |
| spill | 1 (gloss) | pie-lex-gjhewt-2 | ǵʰéwt | to pour, pour out; to shed, spill | LIV² *ǵʰeu̯- | skondéyeti (Indic) |
| cow (f.) | 1 (gloss) + idiom | pie-lex-gwoxws | gʷṓws | cattle; cow, ox, bull | M&A §9.2 *gʷṓus 'cow'. A cow is the slot with `"gender": "f"` (realizer `_slot_gender`): albʰéh₂ gʷṓws | The lexicon gender stays m: 300 realized uses |
| worth | 1 (gloss) | pie-lex-h2elgwheti | h₂élgʷʰeti | to be worth, cost; to deserve | EWAia s.v. ARH (Ved. árhati); M&A §17.3 | — |
| value, price | 1 (gloss) | pie-lex-h2elgwhos | h₂elgʷʰós | value, price, worth | M&A §17.3 (Skt arghá-) | — |
| debt | 1 (form: accent) | pie-lex-dhlghos | dʰl̥gʰós m. | debt | Derksen *dьlgъ m. o (c) 'debt'. AP (c) → oxytone, as for gʷoldʰós. M&A §17.4. **This reverses the vocab-push decision.** | — |
| captive, prisoner | 1 (gloss) | pie-lex-kaptos | kaptós adj. | seized, held; captive, prisoner (as a noun) | M&A §17.5 *kaptos 'captive' (Lat. captus, OIr. cacht, PGmc *haftaz) | — |
| plague, pestilence | 1 (form: stem → noun) | pie-lex-moro | móros m. | death, doom; plague, pestilence | M&A §11.7 *móros (Lith. mãras, OCS morъ 'plague', Gk μόρος); Derksen *morъ | — |
| corpse, the dead | 1 (gloss) | pie-lex-nekjus | néḱus adj. | dead; mortal; corpse, the dead (as a noun) | M&A §11.7 (Gk νέκυς 'corpse', Av. nasu-) | nh₂wis (Germanic 'corpse'): unusable |
| murder | 1 (gloss) | pie-lex-gwhonos-2 | gʷʰónos m. | killing, slaughter; murder | M&A §17.5 (Gk φόνος 'murder') | — |
| slayer | 1 (gloss) | pie-lex-gwhentoxr | gʷʰéntōr m. | one who strikes, kills; slayer, killer | EWAia s.v. HAN (hantár- 'slayer') | gʷʰónō (Germanic only) |
| carry off | 1 (gloss) + idiom | pie-lex-h1rh1pyeti | h₁r̥h₁pyéti | to seize, snatch; to carry off | M&A §17.2 (Lat. rapiō 'carry off, plunder'); LIV² *(h₁)rep- | — |
| abandon, expose | 1 (gloss) | pie-lex-leykwt | léykʷt | to leave; to leave behind, abandon | LIV² *lei̯kʷ- (Gk ἔλιπον, Lat. līquī) | méldʰt 'desist from, abandon' stays |
| weapon, sword | 1 (gloss) + idiom | pie-lex-kjstrom | ḱéstrom n. | knife, cutting tool; blade, cutting weapon | EWAia (śástra- 'knife, sword'); M&A §15.4 | No PIE 'weapon' or 'sword' |
| husband's brother's wife | 1 (spec, hand-checked) | pie-lex-h1yenh2texr | h₁yénh₂tēr f. | husband's brother's wife, sister-in-law | M&A §12.3 (6 branches). Spec on méh₂tēr | — |
| husband's sister | 1 (form: accent; spec) | pie-lex-gjlh2oxws | ǵl̥h₂ṓws f. | husband's sister, sister-in-law | M&A §12.3 (Lat. glōs, OCS zъlъva, Gk γάλως, Arm. tal). Accent projected onto -ōw- (the root is in zero grade). Spec on gʷṓws | Gk γάλοως and Lat. glōris continue other obliques |
| mother-in-law | 1 (spec, hand-checked) | pie-lex-swekjruh2 | sweḱrúh₂ f. | mother-in-law (husband's mother) | de Vaan s.v. socer (*suekruh₂-: Skt śvaśrū́-, OCS svekry); 8 branches | — |
| bride | 1 (gloss) | pie-lex-snusos | snusós f. | daughter-in-law, son's wife; bride | M&A §12.3 (Gk νυός, Ru. snokhá 'son's wife; bride') | wédʰuh₂ (Indo-Iranian, uH-stem) |
| spin | 1 (form: stem → verb) | pie-lex-sneh1 | snéh₁ti | to spin (thread) | LIV² *sneh₁- athematic present (Gk νῆ, Lat. nēre) | sneh₁yeti: unaccented |
| loom | 1 (gloss) | pie-lex-tentlom | téntlom n. | warp (of a web), stretched threads; loom | EWAia s.v. TAN (tántra- 'warp') | No PIE 'loom' |
| back, again | 1 (pos) | pie-lex-h2eti | h₂éti adv. | back, again; away, from | de Vaan s.v. at (*h₂et(i) 'back, away'). **It was filed as a thematic-present verb.** Now indeclinable | — |
| wealth | 1 (gloss) | pie-lex-h3epnos | h₃épnos n. | wealth, goods, possessions | M&A §17.3 *h₂ó/ép(e)n- (Skt ápnas-, Lat. opulentus) | — |
| promise | 1 (gloss) | pie-lex-h1wogwheyeti | h₁wogʷʰéyeti | to vow, promise | LIV² *h₁eu̯gʷʰ- iterative (Lat. voveō) | — |
| heir | 1 (gloss) | pie-lex-h3orbhos | h₃órbʰos m. | orphan; heir; servant | M&A §12.2 (*h₂/₃orbʰos 'orphan, heir'; OIr. orb 'heir') | — |
| autumn | 1 (gloss) | pie-lex-sh1esox | sh₁ésō | harvest time, autumn | M&A §18.6 *h₁es-en- (5 groups) | — |
| curse | 3 (derivative) | pie-neo-curse | ḱépeti | to curse | LIV² *ḱep- present *ḱép-e- (Ved. śápati). Vedic only, so a coinage | Hitt. kappilalli-: another formation |
| bird, fly, wound, slaughter, flee, burn, tear, before, but, father-/brother-in-law, ordinals | already covered | h₂éwis, péth₂eti, térh₃t, gʷʰónos, bʰéwgt, h₁éwseti, h₁réypeti, préy/pró, de, swéḱuros, dayh₂wḗr, pr̥h₂wós … | — | lexq already finds them | — | — |

The coinage is Tier 3b only and flagged `coined: "neologism"`. idioms.json names it only under `tier3b_ids`, which lexq prints only with `--tier3b`. Tier 3 planners never see it.

## Result: idioms and paraphrases (Part 2)

`data/lexicon/idioms.json` has 54 entries: 31 idioms and 23 paraphrases. Each gives the English keys, the PIE way of saying it, the ids, how to build the plan slots, and a source. These are the inherited idioms:

- **From rounds 1–2.**
  - answer = próti + mléwHti
  - open = h₂epó + Hwért
  - tomorrow = h₂éyeri
  - today = deictic ḱi- + LOC dínos
  - thank = praise the giver (gʷr̥néHti, gʷr̥Htós)
- **yes / no.** Repeat the question's verb, or put ne on it (brief rule 13).
- **because.** A clause with the particle h₁yód (Fortson §7.27: subordinators are case forms of pronouns, Lat. quod, Hitt. kuit).
- **for three days (spans of time).** The accusative of extent: the time noun goes in a GOAL slot with a numeral MOD, so "slept three nights" gives tísrn̥s nókʷtn̥s. Source: Handbook, Indic and Greek syntax chapters. Checked: check_plan passes it with no warning.
- **raid.** h₂éǵeti + gʷṓws (pl.) 'drive off the cattle' (West ch. 12; OIr. táin < *to-ag-no-, M&A §17.5).
- **carry off.** h₂éǵeti or h₁r̥h₁pyéti + kaptós.
- **ransom.** kʷinéwti + kʷoynéh₂.
- **avenge, feud.** kʷéyeti MID; the blood-price is kʷoynéh₂.
- **a feminine cow.** gʷṓws with slot gender f.
- **calf.** wetsós as a noun.
- **girl.** h₂yuHn̥ḱós f.
- **wedding, marry.** wédʰeti + snusós 'lead home the bride' (M&A §12.2).
- **neighbour.** woyḱós.
- **agree.** 'Of one mind': PRED compound sm̥ + ménos. Checked: wéy sm̥méneses. today (wĺ̥kʷos ḱósmi dinóy h₁éyti) and because (wĺ̥kʷos h₁éyti h₁yód kénketi) also pass check_plan and realize.
- **every, all.** solh₂wós as a noun.
- **only.** somHós 'alone' or h₁óynos.
- **also.** éti.
- **but.** de or h₂éti.
- **again, give back.** h₂éti + déh₃t.
- **always.** h₂óyu in the accusative of extent.
- **soon.** moḱs.
- **famine, starve.** gʷoldʰós; mért + INS gʷoldʰós.
- **ghost, the dead.** néḱus / mr̥tós as nouns.
- **Smaller cases.** ewe, burn a house, abandon/expose, mourn/scream.

These are paraphrases, each with its reason in the file: ago, refuse, instead, until, already, like/as, drown, grave, curse (Tier 3), weapon/sword/arrow, iron, herald, lend/borrow, rich/poor, inherit, bread, forest, hay/straw, hunter, month, storm/lightning/hail, lazy, and churn/bucket/spindle/shore/cave/bee/deer/store/cloak.

**lexq.** `scripts/lexq.py` now prints `{"idiom": …}` lines after the words on every query. The header gains an `"idioms"` count. A query matches an entry by its exact phrase, or when every content word of the query (with a plural -s dropped) is in one of the entry's keys. **Brief.** planner-brief-v4 rule 6 now has one more sentence: lexq prints idioms; build the phrase from `ids` as `how` says; a paraphrase means there is no word.

## Remaining gaps, and why

- **Engine shapes, rung-2 candidates.** None of these reaches the pool.
  - *méh₁n̥s 'moon, month' (Gk μήν, Lat. mēnsis, Skt mā́s) has no lexicon entry and no engine shape.
  - meldʰn- 'lightning' is a bare n-stem.
  - bʰey- 'bee' is a bare root noun. M&A's North-Western *bʰikʷó- has no entry.
  - h₁élh₁ēn 'deer' is an n-stem the engine cannot inflect. ḱerh₂wos 'the horned one' is accent-unresolved.
- **No accent.**
  - sm̥h₂eros 'summer': sémeh₂ is used instead.
  - h₂ew 'away; again': h₂éti now covers it.
  - wetelos 'calf', poros 'shore', strowom 'straw', skeytos's siblings skoytom and gʰeldʰom.
- **Single-branch or unusable.**
  - loykʷéh₂ 'loan' (NIL, single branch).
  - l̥h₁dós 'lazy' (Germanic, noun spec only).
  - sḱóh₁yno- 'hay' (bare stem).
  - snéh₁trom 'spindle' (Greek only, not verified).
  - speḱus 'cave' (Latin only).
  - kʷískʷe 'each' (Fortson §7.27): the engine has no -kʷe generalizer on pronouns.
- **No PIE word exists.** These stay paraphrases: until, ago, already, instead (an adposition with a genitive object, which the engine lacks), lend, rich, iron, weapon, sword, grave, herald and hunter.

## What changed

- **`data/lexicon/overrides.jsonl`.**
  - 44 ids: 42 new rows, plus ḱéstrom and dʰl̥gʰos merged into their existing rows with the notes joined by " | ".
  - **Rebuild.** First the scratch-copy rebuild was checked byte-identical to the working tree. After the overrides, `lexicon.jsonl` changes in exactly these 44 ids.
  - `inflection_specs.jsonl` changes in 10 rows:
    - dʰl̥gʰós, skéytos, gʰéldʰeti: now accented
    - móros, snéh₁ti: stem → word
    - dʰr̥sús, h₁yénh₂tēr, ǵl̥h₂ṓws, sweḱrúh₂: hand-checked specs, unusable before
    - h₂éti: verb → indeclinable
  - **None of the 10 occurs in corpus/, plans, batches, releases or slices** (grep), so no realized text changes.
  - `confirmed_glosses.jsonl` loses h₁r̥h₁pyéti and solh₂wós, which now have overrides.
- **`data/morph/accent_unresolved.json`.** dʰl̥gʰos, skeytos and gʰeldʰeti are removed (noun/thematic 314 → 312 lexemes, verb/thematic-present 115 → 114; 20,621 → 20,507 cells).
- **`data/lexicon/neologisms.jsonl` (45 → 46).** pie-neo-curse ḱépeti, filled by `pie.neologism --fill`.
- **New: `data/lexicon/idioms.json`.**
- **Reachability.**
  - 40 ids added to `scripts/make_slice.py` TIER3B_INHERITED. All of them pass `offered()`.
  - The pool goes from 1,414 (round 1) to 1,436 offered.
- **Translator.** `pie/translator/lexmap.py` OVERRIDES gets 53 English → lexeme keys. "The brave man repays the debt." → dʰr̥sús wiHrós dʰl̥gʰóm gʰéldʰeti.
- **Docs and tools.** `scripts/lexq.py` (idioms), `docs/generation/planner-brief-v4.md` (rule 6).

## Cells checked

| word | cells |
|---|---|
| dʰr̥sús | m. dʰr̥sús, dʰr̥súm, gen. dʰr̥séws; f. dʰr̥séwih₂, gen. dʰr̥suyéh₂s |
| sweḱrúh₂ | acc. sweḱrúh₂m̥, gen. sweḱruh₂és, pl. sweḱrúh₂es |
| ǵl̥h₂ṓws | acc. ǵl̥h₂ṓm, gen. ǵl̥h₂éws, pl. ǵl̥h₂ówes |
| h₁yénh₂tēr | acc. h₁yénh₂term̥, gen. h₁yénh₂tr̥s, pl. h₁yénh₂teres |
| skéytos, dʰl̥gʰós, móros | skéytom, skéytosyo; dʰl̥gʰósyo; mórosyo |
| snéh₁ti, gʰéldʰeti, kʷinéwti | snéh₁mi, du. sn̥h₁wós; gʰéldʰoh₂; kʷinéwmi, du. kʷinuwós |
| ḱépeti (Tier 3b) | thematic present ḱépe- |
| realized | "The brave mother-in-law spins." → dʰr̥séwih₂ sweḱrúh₂ snéh₁ti. "The white cow" (gender f) → albʰéh₂ gʷṓws |
| translator | snusós HréwdHti 'the bride weeps'; móros h₁léwdʰins moréyeti 'the plague kills the people'; gʷʰéntōr kaptóm térgʷeti 'the slayer threatens the captive' |

## Notes (reported, not changed)

- **solh₂wós 'whole, all' has a thematic NOUN spec** (pos missing), so it cannot be a MOD. That makes "all the men" impossible. Gk ὅλος/ὅλη and Skt sárva-/sárvā are adjectives.
  - t003 and t026 use it as a noun with gender f, realized solh₂wós.
  - An adjective spec would make that cell solh₂wéh₂, so it would change realized records. This needs the owner's decision.
- **h₂éti** was a usable thematic-present *verb* spec on an adverb (its -eti read as the verb ending). The fix was safe because nothing uses it. Other indeclinables ending in -eti may have the same misclassification.
- **The debt reversal.** The 2026-10-23 vocab push kept dʰl̥gʰos unresolved ("no source prints an accent"). Derksen does print AP (c), the same evidence the dialogue round accepted for gʷoldʰós. `test_unsourced_accents_stay_unresolved` was updated to match.
- **gʷṓws stays m. in the lexicon** (300 realized uses). The feminine is the slot gender. Brief rule 10 mentions gender only for pronouns, but `_slot_gender` reads it on any noun slot.
- **Unverified in the handbooks read.** These rest on the entry reflexes or on standard knowledge, not on a page read in this round: the 'always' idiom (Gk αἰεί), 'soon' (moḱs), the Ved. óhas- half of h₁éh₁ugʰos, Ved. áhuta- and Gk ἔχευα in the ǵʰéwt note, and the OIr. cacht gloss in the kaptós note. The first two are marked so in idioms.json.

## Tests

- **New.**
  - `tests/test_lexq.py`: `test_idioms_answer_concepts_without_a_word` (idioms printed, no coinage in Tier 3 ids, every id exists) and `test_round3_words_are_found` (12 concepts → the expected lexeme first).
  - `tests/test_vocab_push.py`: `test_round3_specs_and_cells` (the cells above and a realized plan).
  - `tests/test_translator.py`: `test_round3_words_reach_the_translator`.
- **Runs.**
  - test_neologisms, test_project_reconstructions, test_lexicon*, test_vocab_push, test_glosses*, test_planner_accent*, test_lexq, test_accent_invariant and test_accent_policy: **181 passed** (exit 0).
  - test_translator with `--group translator`: **22 passed** (exit 0).
  - test_realize, test_validate, test_u_adjective_alternatives, test_alt_status and test_conversation_gaps: 114 passed and 1 failed.
    - The failure was `test_closed_adverbs_are_checked`, a TypeError in `_check_two_oblique`, an engine change from another agent (b3016b1).
    - Commit c874332 fixed it while this round was running. The rerun gave test_conversation_gaps 8 passed.
