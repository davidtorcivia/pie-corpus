# Meter repair: t014

- meter_exact before: 23/71 = 0.324 (census, 2026-10-28). After: 67/67 = 1.000.
- Batch gate after re-realization: **PASS** (all gates: reject_rate<=0.10, max_lexeme_uses<=7, theme_core_uses<=22, roots_per_sentence>=0.35, duplicates<=2%, all_exact, meter_exact>=0.90); rejects 0.0; max lexeme uses 7; warnings 34.
- Re-realized with the batch's own model and prompt-id (tier3-planner-v4); plan file `data/generation/plans/t014.jsonl`, corpus `corpus/tier3/t014.jsonl`, report `data/generation/batches/t014.json`.
- Lines unfixed: none.
- Edit vocabulary: particle nu/-ge on or off, -kʷe joined or dropped, sentence split/merge (a "sentence break" change), epithet added or dropped, possessor/vocative/adverb/numeral dropped, number change, copula dropped in a nominal clause, `and` mark moved. English was updated for every edit.
- Head/dep audit: every changed plan was checked; each `head`/`dep` still points at the intended slot. The tool's "add a vocative" edit and my own helper inserted the vocative at slot 0 without renumbering; the affected clauses (t020-0015 c1; t008-0002, -0006, -0010) were corrected and re-checked by comparing every unchanged slot's head target with the pre-repair plan (0 differences) and listing every new epithet with its head noun.
- Texts not edited by me whose `pie`/`tokens` or `syllables` fields differ from the pre-repair corpus changed only because the engine/syllabifier moved between the census run and this re-realization (other agents' commits); no plan of theirs was touched.
- Old/new PIE lines below are the verse lines that changed (several old lines can map to several new ones after a split or merge); "-" means no counterpart.

### t014-0017 (work song) Ploughman's Song

Edits (clause indices as in the plan): c0 particle: None -> nu; c0 add HeHkjus:MOD; c1 add h2egjryos:MOD; c3 sentence break: True -> None; c5 sentence break: True -> None; c6 conj: kʷe -> None; c8 particle: None -> nu; c8 conj: None -> kʷe; c8 sentence break: True -> None; c10 particle: None -> nu; c11 particle: None -> nu; c11 conj: None -> kʷe; c11 add mudros:MOD

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| gʷówes dukté (4) / h₂érh₃trom dukté (5) / yugóm bʰérete (5) / lóyseh₂m h₃roǵéyete (6) / mē h₃slidʰté (3) / gʷʰrensós dʰégʷʰeti swidyómes-kʷe (9) / h₂nḗr wos sékʷetor (5) / séh₁mn̥ séh₁yoh₂ (4) | nu HéHḱewes gʷówes dukté (8) / h₂éǵr̥yom h₂érh₃trom dukté (8) / yugóm bʰérete lóyseh₂m h₃roǵéyete (11) / mē h₃slidʰté gʷʰrensós dʰégʷʰeti swidyómes (11) / h₂nḗr wos sékʷetor nu-kʷe séh₁mn̥ séh₁yoh₂ (11) |
| sóh₂wl̥ séh₁mn̥ gʷʰr̥nuyéh₁t (7) / gʷówes dukté (4) | nu sóh₂wl̥ séh₁mn̥ gʷʰr̥nuyéh₁t (8) / nu-kʷe múdrōs gʷówes dukté (8) |

| old English | new English |
|---|---|
| Pull, cattle! Pull the plough! Bear the yoke! Make the furrow straight! Do not go astray! The heat burns, and we sweat. The man follows you. I sow the seed. | Now pull, swift cattle! Pull the field plough! Bear the yoke, make the furrow straight! Do not go astray; the heat burns, we sweat. The man follows you, and now I sow the seed. |
| May the sun warm the seed! Pull, cattle! | Now may the sun warm the seed! And now pull, cheerful cattle! |

### t014-0018 (work song) Harvest Song

Edits (clause indices as in the plan): c0 particle: None -> nu; c1 conj: None -> kʷe; c1 add sth2ros:MOD; c4 conj: kʷe -> None; c5 conj: None -> kʷe; c6 add h1rowdhos:MOD; c8 sentence break: True -> None; c9 add mudros:MOD; c10 sentence break: True -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₂éḱesh₂ skinédomes (7) / bʰórom wéǵʰōmes (5) | nu h₂éḱesh₂ skinédomes (8) / sth₂róm-kʷe bʰórom wéǵʰōmes (8) |
| gʷʰrensós dʰégʷʰeti puHrós-kʷe h₂sowsós h₁ésti (12) / h₂éboles h₁rowdʰṓs h₁sénti (7) / h₂éboln̥s wósh₂r̥-kʷe h₂éḱh₃omes (9) / h₁erkʷóm bʰéh₂omes (5) / léwbʰe médʰu píph₃e (6) / swésor ǵr̥h₂nóm gʷr̥h₃é (6) / méwdomes (3) | gʷʰrensós dʰégʷʰeti puHrós h₂sowsós h₁ésti (11) / h₂éboles-kʷe h₁rowdʰṓs h₁sénti (8) / h₁rowdʰóns h₂éboln̥s wósh₂r̥-kʷe h₂éḱh₃omes (11) / h₁erkʷóm bʰéh₂omes léwbʰe médʰu píph₃e (11) / múdra swésor ǵr̥h₂nóm gʷr̥h₃é méwdomes (11) |

| old English | new English |
|---|---|
| Let us cut the ears of grain! Let us transport the load! | Now let us cut the ears of grain! And let us transport the steady load! |
| The heat burns, and the wheat is dry. The apples are red. Let us eat up the apples and the garlic! Let us speak a hymn of praise! Drink mead, dear one! Eat grain, sister! Let us be joyful! | The heat burns, the wheat is dry. And the apples are red. Let us eat up the red apples and the garlic! Let us speak a hymn of praise, drink mead, dear one! Eat grain, cheerful sister, let us be joyful! |

### t014-0033 (prayer) Prayer to Father Sky for Rain

Edits (clause indices as in the plan): c2 conj: None -> kʷe; c6 particle: None -> nu; c12 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| dʰéǵʰōm méh₂tēr tr̥syéti (7) | dʰéǵʰōm-kʷe méh₂tēr tr̥syéti (8) |
| h₁yós méǵh₂m̥ n̥bʰróm bʰéyds h₂éǵroy h₂wr̥sdʰí (10) | h₁yós méǵh₂m̥ n̥bʰróm bʰéyds nu h₂éǵroy h₂wr̥sdʰí (11) |
| h₂éboles h₁rudʰéh₁ih₁ent (7) | h₂éboles-kʷe h₁rudʰéh₁ih₁ent (8) |

| old English | new English |
|---|---|
| Mother Earth is thirsty. | And Mother Earth is thirsty. |
| You who split the great rain-cloud, rain on the field! | You who split the great rain-cloud, now rain on the field! |
| May the apples be red! | And may the apples be red! |

### t014-0034 (prayer) Prayer to Mother Earth over the Seed

Edits (clause indices as in the plan): c1 conj: None -> kʷe; c8 add sth2ros:MOD; c10 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu toy séh₁mn̥ séh₁yomes (7) | nu-kʷe toy séh₁mn̥ séh₁yomes (8) |
| puHrósyo h₂éḱesh₂ polh₁úh₂ h₁syéh₁t (9) / wósh₂r̥ bʰuHyóyh₁t h₃ósdos wr̥h₂dés bʰuHyóyh₁t (10) | puHrósyo sth₂réh₂ h₂éḱesh₂ polh₁úh₂ h₁syéh₁t (11) / wósh₂r̥ bʰuHyóyh₁t h₃ósdos-kʷe wr̥h₂dés bʰuHyóyh₁t (11) |

| old English | new English |
|---|---|
| Now we sow the seed for you. | And now we sow the seed for you. |
| May the ears of wheat be many! May the garlic grow, may the branch grow from the root! | May the firm ears of wheat be many! May the garlic grow, and may the branch grow from the root! |

### t014-0035 (prayer) Prayer to the Sun over the Ripening Grain

Edits (clause indices as in the plan): c0 add h1rowdhos:MOD; c1 conj: None -> kʷe; c2 particle: None -> nu; c3 add lewbhos:MOD; c5 conj: None -> kʷe; c6 add sth2ros:MOD

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| sh₂wéns kʷékʷle h₂éǵrom gʷʰr̥nudʰí (9) / polh₁úh₂ puHrósyo h₂éḱesh₂ pékʷe (10) / kʷékʷle h₂élbʰit mē h₁éwsoyh₁s (7) / kʷékʷle méǵh₂s h₁ési h₁ím spéḱye (9) / puHrṓy gʷʰrensóm h₁opéye (7) / ń̥dʰgʷʰitom nos ḱléwos h₁opéye (9) | sh₂wéns h₁rówdʰe kʷékʷle h₂éǵrom gʷʰr̥nudʰí (11) / polh₁úh₂-kʷe puHrósyo h₂éḱesh₂ pékʷe (11) / nu kʷékʷle h₂élbʰit mē h₁éwsoyh₁s (8) / léwbʰe kʷékʷle méǵh₂s h₁ési h₁ím spéḱye (11) / puHrṓy-kʷe gʷʰrensóm h₁opéye (8) / ń̥dʰgʷʰitom nos sth₂róm ḱléwos h₁opéye (11) |

| old English | new English |
|---|---|
| Wheel of the sun, warm the field! Ripen the many ears of wheat! Wheel, may you not burn the barley! Wheel, you are great, look upon it. Give heat to the wheat. Give us imperishable fame. | Red wheel of the sun, warm the field! And ripen the many ears of wheat! Now, wheel, may you not burn the barley! Dear wheel, you are great, look upon it. And give heat to the wheat. Give us firm, imperishable fame. |

### t014-0036 (prayer) Prayer for the Herd at Night

Edits (clause indices as in the plan): c0 add gjnh3ros:MOD; c3 conj: kʷe -> None; c4 conj: None -> kʷe; c7 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| déywōs gʷṓs h₂ówins-kʷe h₂léksete (9) | ǵń̥h₃rōs déywōs gʷṓs h₂ówins-kʷe h₂léksete (11) |
| gʷíh₃woyh₁ent polh₁éwes-kʷe h₁sih₁ént (9) / h₂ŕ̥tḱos tóns kʷsépi mē h₁pyéh₁t (7) | gʷíh₃woyh₁ent polh₁éwes h₁sih₁ént (8) / h₂ŕ̥tḱos-kʷe tóns kʷsépi mē h₁pyéh₁t (8) |
| h₂éwsosm̥-ge widóyh₁ent (7) | h₂éwsosm̥-kʷe-ge widóyh₁ent (8) |

| old English | new English |
|---|---|
| Gods, guard the cattle and the sheep! | Knowing gods, guard the cattle and the sheep! |
| May they live and be many. May the bear not seize them in the night. | May they live, may they be many. And may the bear not seize them in the night. |
| May they indeed see Dawn! | And may they indeed see Dawn! |

### t014-0037 (charm) Charm against the Wolf

Edits (clause indices as in the plan): c3 add kjoymos:MOD; c5 particle: None -> ge; c6 particle: None -> nu; c8 particle: None -> nu; c9 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| gʰórtom mē gʷéms gʷowsth₂óm-wē mē gʷéms (9) / dedórḱh₂e te ne me dedórḱth₂e (9) / sh₂itós h₁sdʰí sélos ih₂dʰí (7) / h₁éy h₁régʷos h₂epó bʰugyéh₁t (7) | ḱóymom gʰórtom mē gʷéms gʷowsth₂óm-wē mē gʷéms (11) / dedórḱh₂e-ge te nu me ne dedórḱth₂e (11) / sh₂itós h₁sdʰí nu sélos ih₂dʰí (8) / h₁éy-kʷe h₁régʷos h₂epó bʰugyéh₁t (8) |

| old English | new English |
|---|---|
| Do not come to the enclosure or to the cow-stall. I have seen you; you do not see me. | Do not come to the homely enclosure or to the cow-stall. I have seen you indeed; now you do not see me. |
| Go to the marsh. May he flee away into the darkness! | Now go to the marsh. And may he flee away into the darkness! |

### t014-0038 (prayer) Thanks at the Harvest

Edits (clause indices as in the plan): c2 conj: None -> kʷe; c4 add pikjtos:MOD; c6 add h2sowsos:MOD; c7 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁rowdʰóns toy h₂éboln̥s h₁opéyomes (10) | h₁rowdʰóns-kʷe toy h₂éboln̥s h₁opéyomes (11) |
| dóh₃r̥ h₁áyso gʷérHtores h₁smés (9) / ǵénh₁mn̥ nos wésni h₁opéye (9) / méǵh₂s-ge h₁wésus-kʷe h₁syéh₁s (7) | piḱtóm dóh₃r̥ h₁áyso gʷérHtores h₁smés (11) / h₂sowsóm nos ǵénh₁mn̥ wésni h₁opéye (11) / méǵh₂s-kʷe-ge h₁wésus-kʷe h₁syéh₁s (8) |

| old English | new English |
|---|---|
| We give honey and the poured mead, we give you red apples. | We give honey and the poured mead, and we give you red apples. |
| Receive the gift, we are praisers. Give us seed in spring. May you indeed be great and good! | Receive the adorned gift, we are praisers. Give us dry seed in spring. And may you indeed be great and good! |

### t014-0039 (prayer) Prayer to Fire at the Hearth

Edits (clause indices as in the plan): c0 particle: None -> nu; c1 conj: None -> kʷe; c1 sentence break: None -> True; c1 add h2sowsos:MOD; c3 conj: None -> kʷe; c7 particle: None -> nu

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁ń̥gʷney déywe dóh₃r̥ h₁éddʰi h₃ósdons h₁éddʰi lukdʰí (14) / h₂éHsh₂m̥ h₂lékse tóns ph₂sdʰí (7) | nu h₁ń̥gʷney déywe dóh₃r̥ h₁ddʰí (8) / h₂sowsóns-kʷe h₃ósdons h₁ddʰí lukdʰí (8) / h₂éHsh₂m̥-kʷe h₂lékse tóns ph₂sdʰí (8) |
| deywóybʰos lewbʰós h₁ési (7) | nu deywóybʰos lewbʰós h₁ési (8) |

| old English | new English |
|---|---|
| Fire, god, eat the gift, eat the branches, be bright! Guard the hearth, guard them! | Now, fire, god, eat the gift! And eat the dry branches, be bright! And guard the hearth, guard them! |
| You are dear to the gods! | Now you are dear to the gods! |

### t014-0040 (prayer) Dawn at the Cow-stall

Edits (clause indices as in the plan): c4 conj: kʷe -> None; c6 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| gʷíh₃woyh₁ent polh₁éwes-kʷe h₁sih₁ént (9) / widóyh₁ent te sóh₂wl̥ te sékʷetor (10) | gʷíh₃woyh₁ent polh₁éwes h₁sih₁ént (8) / widóyh₁ent te sóh₂wl̥-kʷe te sékʷetor (11) |

| old English | new English |
|---|---|
| May they live and be many. May they see you, behind you the sun follows. | May they live, may they be many. May they see you, and behind you the sun follows. |

