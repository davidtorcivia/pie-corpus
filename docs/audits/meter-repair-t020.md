# Meter repair: t020

- meter_exact before: 18/60 = 0.300 (census, 2026-10-28). After: 60/60 = 1.000.
- Batch gate after re-realization: **PASS** (all gates: reject_rate<=0.10, max_lexeme_uses<=11, theme_core_uses<=33, roots_per_sentence>=0.35, duplicates<=2%, all_exact, meter_exact>=0.90); rejects 0.0; max lexeme uses 11; warnings 44.
- Re-realized with the batch's own model and prompt-id (tier3-planner-v4); plan file `data/generation/plans/t020.jsonl`, corpus `corpus/tier3/t020.jsonl`, report `data/generation/batches/t020.json`.
- Lines unfixed: none.
- Edit vocabulary: particle nu/-ge on or off, -kʷe joined or dropped, sentence split/merge (a "sentence break" change), epithet added or dropped, possessor/vocative/adverb/numeral dropped, number change, copula dropped in a nominal clause, `and` mark moved. English was updated for every edit.
- Head/dep audit: every changed plan was checked; each `head`/`dep` still points at the intended slot. The tool's "add a vocative" edit and my own helper inserted the vocative at slot 0 without renumbering; the affected clauses (t020-0015 c1; t008-0002, -0006, -0010) were corrected and re-checked by comparing every unchanged slot's head target with the pre-repair plan (0 differences) and listing every new epithet with its head noun.
- Texts not edited by me whose `pie`/`tokens` or `syllables` fields differ from the pre-repair corpus changed only because the engine/syllabifier moved between the census run and this re-realization (other agents' commits); no plan of theirs was touched.
- Old/new PIE lines below are the verse lines that changed (several old lines can map to several new ones after a split or merge); "-" means no counterpart.

### t020-0003 (prayer) A Prayer to Sky and Earth for the Newborn

Edits (clause indices as in the plan): c0 particle: nu -> None; c0 add lewbhos:MOD; c1 add lewbhos:MOD; c4 add HeHkjus:MOD; c5 particle: nu -> None; c7 add lewbhos:MOD; c9 add h1wesus:MOD

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu nos dyéw ph₂ter ḱléwse (7) / dʰéǵʰom méh₂ter ḱóm ǵónh₁om h₂lékse (9) | dyéw nos léwbʰe ph₂ter ḱléwse (8) / dʰéǵʰom léwbʰa méh₂ter ḱóm ǵónh₁om h₂lékse (11) |
| sh₂wéns kʷékʷle h₁ésmey ǵʰleynós h₁sdʰí (9) / nu nos ḱóymoy h₂uksyéh₁t Hwr̥dʰyéh₁t-kʷe (9) / HeHḱéwes h₁éḱwōs h₁ésmey h₁sih₁ént (9) | sh₂wéns HéHḱew kʷékʷle h₁ésmey ǵʰleynós h₁sdʰí (11) / ḱóymoy nos h₂uksyéh₁t Hwr̥dʰyéh₁t-kʷe (8) / HeHḱéwes lewbʰṓs h₁éḱwōs h₁ésmey h₁sih₁ént (11) |
| mórtōs h₁ésyo h₁nómn̥ ḱluwih₁ént (9) | mórtōs h₁ésyo h₁wésu h₁nómn̥ ḱluwih₁ént (11) |

| old English | new English |
|---|---|
| Now, Father Sky, hear us! Mother Earth, protect this offspring! | Dear Father Sky, hear us! Dear Mother Earth, protect this offspring! |
| Wheel of the sun, be bright for him! Now may he grow up in our household, and may he be strong! May swift horses be his! | Swift wheel of the sun, be bright for him! May he grow up in our household, and may he be strong! May dear swift horses be his! |
| May men hear his name! | May men hear his good name! |

### t020-0006 (charm) A Charm to Guard the Newborn

Edits (clause indices as in the plan): c3 drop kjwox:VOC; c5 particle: None -> nu; c6 drop h2epo:ADV; c7 particle: None -> nu; c9 add gjerh2onts:MOD; c10 conj: None -> kʷe; c12 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| ḱwón h₁ím ph₂sdʰí ḱwón h₁ésmi l̥gʰdʰí (9) / h₁yód wĺ̥kʷos h₁ludʰḗti ḱwṓ h₁ím gʷʰn̥yéh₁t (10) / wĺ̥kʷe h₂epó bʰugdʰí h₁ń̥gʷney kʷsépi dʰégʷʰe (12) | ḱwón h₁ím ph₂sdʰí h₁ésmi l̥gʰdʰí (8) / h₁yód wĺ̥kʷos h₁ludʰḗti nu ḱwṓ h₁ím gʷʰn̥yéh₁t (11) / wĺ̥kʷe bʰugdʰí nu h₁ń̥gʷney kʷsépi dʰégʷʰe (11) |
| wĺ̥kʷos h₁ím mē widóyh₁t (6) / nu dʰéǵʰom h₁ím tetl̥h₂dʰí (7) | ǵérh₂onts wĺ̥kʷos h₁ím mē widóyh₁t (8) / nu-kʷe dʰéǵʰom h₁ím tetl̥h₂dʰí (8) |
| nu sóh₂wl̥ h₁ím gʷʰr̥nudʰí (7) | nu-kʷe sóh₂wl̥ h₁ím gʷʰr̥nudʰí (8) |

| old English | new English |
|---|---|
| Dog, guard him, dog, lie down by him! If the wolf comes, may the dog kill him! Wolf, flee away, Fire, burn in the night! | Dog, guard him, lie down by him! If the wolf comes, then may the dog kill him! Wolf, flee; now, Fire, burn in the night! |
| May the wolf not see him! Now, Earth, hold him up! | May the old wolf not see him! And now, Earth, hold him up! |
| Now, Sun, warm him! | And now, Sun, warm him! |

### t020-0015 (wedding) A Song for the Wedding

Edits (clause indices as in the plan): c0 add swos:MOD; c1 add potnih2:VOC; c3 conj: None -> kʷe; c4 h1ekjwos:SUBJ number PL -> DU; c5 conj: None -> kʷe; c7 particle: None -> ge; c8 add lewbhos:MOD; c10 conj: None -> kʷe; c11 conj: None -> kʷe; c12 conj: None -> kʷe; c14 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu pótni dʰéh₁mn̥ wiḱdʰí (7) / téwe swéḱurōy h₁uséwih₂ h₁sdʰí (9) | nu pótni swóm dʰéh₁mn̥ wiḱdʰí (8) / pótni téwe swéḱurōy h₁uséwih₂ h₁sdʰí (11) |
| péh₂wr̥-ge toy ǵʰleynóm h₁syéh₁t (7) / téwe h₁éḱwōs HeHḱéwes h₁sih₁ént (9) / nu toy h₃éngʷn̥ polh₁ú h₁syéh₁t (7) | péh₂wr̥-kʷe-ge toy ǵʰleynóm h₁syéh₁t (8) / téwe h₁éḱwoh₁ HeHḱúh₁ h₁sih₁tā́m (8) / nu-kʷe toy h₃éngʷn̥ polh₁ú h₁syéh₁t (8) |
| téwe séh₁mn̥ polh₁ú h₁syéh₁t (7) / déḱm̥ suHnúns h₂éloyh₁s (6) | téwe-ge séh₁mn̥ polh₁ú h₁syéh₁t (8) / déḱm̥ lewbʰóns suHnúns h₂éloyh₁s (8) |
| sénoh₁-ge ḱóm bʰuHih₁tóm (7) / nu wos sóh₂wl̥ ḱóm spéḱye (7) / h₂éwsos wos diwés dʰúgh₂ter lukdʰí (10) | sénoh₁-kʷe-ge ḱóm bʰuHih₁tóm (8) / nu-kʷe wos sóh₂wl̥ ḱóm spéḱye (8) / h₂éwsos-kʷe wos diwés dʰúgh₂ter lukdʰí (11) |
| nu tóybʰos h₁wésuh₂ dh₃dʰí (7) | nu-kʷe tóybʰos h₁wésuh₂ dh₃dʰí (8) |

| old English | new English |
|---|---|
| Now enter the dwelling, mistress! Be good to your father-in-law! | Now enter your own dwelling, mistress! Mistress, be good to your father-in-law! |
| May the fire indeed be bright for you! May your horses be swift! Now may there be much butter for you! | And may the fire indeed be bright for you! May your two horses be swift! And now may there be much butter for you! |
| May your seed be many! May you nourish ten sons! | May your seed indeed be many! May you nourish ten dear sons! |
| May you two indeed grow old together! Now, Sun, look upon you together! Dawn, daughter of Sky, shine for you! | And may you two indeed grow old together! And now, Sun, look upon you together! And Dawn, daughter of Sky, shine for you! |
| Now give them good things! | And now give them good things! |

### t020-0034 (lament) The Widow's Lament

Edits (clause indices as in the plan): c0 particle: None -> ge; c4 conj: None -> kʷe; c6 particle: ge -> None; c8 particle: None -> ge; c10 add lewbhos:MOD; c11 conj: None -> kʷe; c14 conj: kʷe -> None; c15 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| pótey h₂epó lelóykʷth₂e (7) | pótey-ge h₂epó lelóykʷth₂e (8) |
| nu h₁widʰéwh₂ h₁ésmi méne ḱḗr stéwdt (10) / h₁n̥gʷnís dʰégʷʰeti h₁ésmi-ge ne sédyesi (12) / téwe sth₂dʰlóm spéḱyoh₂ kúdʰe h₁ési (10) / stóygʰom spéḱyoh₂ wíHre h₂ew gʷm̥dʰí (9) / téwe ǵónh₁ōs HrudHénti (7) / ḱwṓ te h₂isḱéti pékʷom toy ne-kʷe h₁ḗdsi (12) / nu te dʰéǵʰōm ḱéleti (7) | nu h₁widʰéwh₂ h₁ésmi méne-kʷe ḱḗr stéwdt (11) / h₁n̥gʷnís dʰégʷʰeti h₁ésmi ne sédyesi (11) / téwe sth₂dʰlóm spéḱyoh₂ kúdʰe-ge h₁ési (11) / stóygʰom spéḱyoh₂ léwbʰe wíHre h₂ew gʷm̥dʰí (11) / téwe-kʷe ǵónh₁ōs HrudHénti (8) / ḱwṓ te h₂isḱéti pékʷom toy ne h₁ḗdsi (11) / nu-kʷe te dʰéǵʰōm ḱéleti (8) |

| old English | new English |
|---|---|
| Husband, you are gone away! | Husband, you are indeed gone away! |
| Now I am a widow, my heart has grown cold! | Now I am a widow, and my heart has grown cold! |
| I look at your place; where are you? I look at the road, come back, husband! Your offspring cry out. The dog looks for you; I cooked for you, and you do not eat! Now the earth covers you. | I look at your place; where indeed are you? I look at the road, come back, dear husband! And your offspring cry out. The dog looks for you; I cooked for you, you do not eat! And now the earth covers you. |

### t020-0035 (lament) The Sons' Lament

Edits (clause indices as in the plan): c2 conj: None -> kʷe; c4 particle: None -> ge; c4 wekwos:SUBJ number SG -> PL; c5 conj: None -> kʷe; c6 conj: None -> kʷe; c8 conj: None -> kʷe; c10 particle: None -> nu

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu nos kʷís pró wédʰēti (7) | nu-kʷe nos kʷís pró wédʰēti (8) |
| téwe nos wékʷos h₂éwsu h₁ésti (9) / téwe nos h₁nómn̥ dn̥ǵʰwéh₂i h₁ésti (10) / nu h₂éwsōs léwkt ne-kʷe bʰéwdʰs (7) / mórtoysu-ge méǵh₂s h₁és (7) | téwe-ge nos wékʷesh₂ h₂éwsu h₁ésti (11) / téwe-kʷe nos h₁nómn̥ dn̥ǵʰwéh₂i h₁ésti (11) / nu-kʷe h₂éwsōs léwkt ne-kʷe bʰéwdʰs (8) / mórtoysu-kʷe-ge méǵh₂s h₁és (8) |
| h₂éḱmonm̥ te upér stoh₂éyomes (10) | nu te h₂éḱmonm̥ upér stoh₂éyomes (11) |

| old English | new English |
|---|---|
| Now who indeed will lead us forward? | And now who indeed will lead us forward? |
| Your word is in our ears. Your name is on our tongue. Now dawn grows bright, and you do not wake. You indeed were great among men. | Your words are indeed in our ears. And your name is on our tongue. And now dawn grows bright, and you do not wake. And you indeed were great among men. |
| We set up a stone above you. | Now we set up a stone above you. |

### t020-0040 (prayer) A Prayer for the Dead Father

Edits (clause indices as in the plan): c0 drop ph2texr:VOC; c1 conj: None -> kʷe; c5 particle: None -> nu; c6 drop meh2texr:VOC; c8 conj: None -> kʷe; c9 conj: None -> kʷe; c10 drop anaphoric_i:POSS; c11 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| ph₂ter stóygʰoh₁ h₁idʰí ph₂trṓm stóygʰoh₁ h₁idʰí (12) | stóygʰoh₁ h₁idʰí ph₂trṓm-kʷe stóygʰoh₁ h₁idʰí (11) |
| sóh₂wl̥ h₁ím spéḱye dʰéǵʰom méh₂ter h₁ím h₁áyso (12) / ph₂tr̥bʰís sdyéh₁t ǵʰutóm médʰu ph₃yéh₁t (10) / h₁ésyo h₁nómn̥ mē mr̥yéh₁t (7) / h₁ésyo ḱléwos ń̥dʰgʷʰitom h₁syéh₁t h₁ím memn̥mé (12) | nu sóh₂wl̥ h₁ím spéḱye dʰéǵʰom h₁ím h₁áyso (11) / ph₂tr̥bʰís sdyéh₁t ǵʰutóm-kʷe médʰu ph₃yéh₁t (11) / h₁ésyo-kʷe h₁nómn̥ mē mr̥yéh₁t (8) / ḱléwos ń̥dʰgʷʰitom h₁syéh₁t h₁ím-kʷe memn̥mé (11) |

| old English | new English |
|---|---|
| Go, father, by the path, go by the path of the fathers! | Go by the path, and go by the path of the fathers! |
| Sun, look upon him, Mother Earth, receive him! May he sit with the fathers, may he drink the libated mead! May his name not die! May his fame be imperishable, we remember him. | Now, Sun, look upon him, Earth, receive him! May he sit with the fathers, and may he drink the libated mead! And may his name not die! May fame be imperishable, and we remember him. |

