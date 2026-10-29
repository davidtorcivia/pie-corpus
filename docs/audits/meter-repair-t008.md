# Meter repair: t008

- meter_exact before: 78/267 = 0.292 (census, 2026-10-28). After: 269/269 = 1.000.
- Batch gate after re-realization: **PASS** (all gates: reject_rate<=0.10, max_lexeme_uses<=9, theme_core_uses<=27, roots_per_sentence>=0.35, duplicates<=2%, all_exact, meter_exact>=0.90); rejects 0.0; max lexeme uses 9; warnings 12.
- Re-realized with the batch's own model and prompt-id (tier3-planner-v4); plan file `data/generation/plans/t008.jsonl`, corpus `corpus/tier3/t008.jsonl`, report `data/generation/batches/t008.json`.
- Lines unfixed: none.
- Edit vocabulary: particle nu/-ge on or off, -kʷe joined or dropped, sentence split/merge (a "sentence break" change), epithet added or dropped, possessor/vocative/adverb/numeral dropped, number change, copula dropped in a nominal clause, `and` mark moved. English was updated for every edit.
- Head/dep audit: every changed plan was checked; each `head`/`dep` still points at the intended slot. The tool's "add a vocative" edit and my own helper inserted the vocative at slot 0 without renumbering; the affected clauses (t020-0015 c1; t008-0002, -0006, -0010) were corrected and re-checked by comparing every unchanged slot's head target with the pre-repair plan (0 differences) and listing every new epithet with its head noun.
- Texts not edited by me whose `pie`/`tokens` or `syllables` fields differ from the pre-repair corpus changed only because the engine/syllabifier moved between the census run and this re-realization (other agents' commits); no plan of theirs was touched.
- Old/new PIE lines below are the verse lines that changed (several old lines can map to several new ones after a split or merge); "-" means no counterpart.

### t008-0001 (wedding) The Bride Led Home

Edits (clause indices as in the plan): c0 drop potis:IO; c1 sentence break: None -> True; c1 drop kwekwlos:OBJ; c2 conj: None -> kʷe; c2 drop demonstrative_so:POSS; c3 sentence break: None -> True; c3 drop demonstrative_so:POSS; c4 drop demonstrative_so:POSS; c5 conj: kʷe -> None; c5 sentence break: None -> True; c6 conj: None -> kʷe; c7 conj: None -> kʷe; c8 conj: kʷe -> None; c8 sentence break: None -> True; c10 particle: None -> nu; c11 conj: None -> kʷe; c11 add newos:MOD; c13 conj: None -> kʷe; c14 add bheh2nos:MOD; c15 conj: None -> kʷe; c16 particle: None -> ge; c16 drop dhugh2texr:SUBJ; c17 conj: kʷe -> None; c17 sentence break: None -> True; c18 sentence break: True -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| ph₂tḗr póteyey swéh₂m dʰugh₂térm̥ dʰǵʰyés h₁opéyet pótis-kʷe h₁wédmn̥ kʷetwórn̥s h₁éḱwons kʷékʷlom-kʷe h₁áyt (28) / tósyeh₂s méh₂tēr tā́m néweh₂h₁ h₂wĺ̥h₁neh₂h₁ woséyet tósyeh₂s-kʷe swésōr pḱténm̥ tósyeh₂s ḱr̥h₂séni dʰéh₁t (25) / nu pótis tā́m tósyeh₂s dʰh₁méns wédʰet dwóh₁-kʷe tósyeh₂s bʰréh₂terh₁e énu stéygʰetām (22) / nu póteys gʰórdʰom h₁ludʰónt (7) / pótis tā́m h₁n̥gʷním trís péri wédʰet dayh₂wḗr-kʷe tā́m h₁n̥gʷnéy sodéyet (19) / dayh₂wéres tā́m spéḱyont tóy-kʷe dʰm̥bʰént (10) / nu pótis wérh₁t (5) / h₁eǵóh₂ dyḗws h₁ésmi túH dʰéǵʰōm h₁ési (10) / nu gʷréh₂wonm̥ stéygʰet (6) / h₁ń̥gʷney tā́m pótnih₂m ph₂sdʰí (7) / suHnéwes dʰugh₂téres-kʷe tósyeh₂ey ǵeǵn̥h₁ih₁ént pótih₁-kʷe gʷíh₃woyh₁t (20) / mértis tā́m mē h₂eh₂n̥ḱyéh₁t (7) | ph₂tḗr swéh₂m dʰugh₂térm̥ dʰǵʰyés h₁opéyet (11) / pótis-kʷe h₁wédmn̥ kʷetwórn̥s h₁éḱwons h₁áyt (11) / méh₂tēr-kʷe tā́m néweh₂h₁ h₂wĺ̥h₁neh₂h₁ woséyet (11) / swésōr-kʷe pḱténm̥ tósyeh₂s ḱr̥h₂séni dʰéh₁t (11) / nu pótis tā́m dʰh₁méns wédʰet (8) / dwóh₁ tósyeh₂s bʰréh₂terh₁e énu stéygʰetām (11) / nu-kʷe póteys gʰórdʰom h₁ludʰónt (8) / pótis-kʷe tā́m h₁n̥gʷním trís péri wédʰet (11) / dayh₂wḗr tā́m h₁n̥gʷnéy sodéyet (8) / dayh₂wéres tā́m spéḱyont nu-kʷe tóy dʰm̥bʰént (11) / nu-kʷe néwos pótis wérh₁t (8) / h₁eǵóh₂ dyḗws h₁ésmi túH-kʷe dʰéǵʰōm h₁ési (11) / nu bʰeh₂nóm gʷréh₂wonm̥ stéygʰet (8) / h₁ń̥gʷney-kʷe tā́m pótnih₂m ph₂sdʰí (8) / suHnéwes-ge tósyeh₂ey ǵeǵn̥h₁ih₁ént (11) / pótih₁ gʷíh₃woyh₁t mértis tā́m mē h₂eh₂n̥ḱyéh₁t (11) |

| old English | new English |
|---|---|
| Yesterday the father gave his own daughter to the husband, and the husband gave the bride price: four horses and a wagon. Her mother clothed her in new wool, and her sister placed a comb on her head. Then the husband led her from her house, and her two brothers walked after. Then they arrived at the husband's fence. Three times the husband led her around the Fire, and the husband's brother seated her by the Fire. The husband's brothers were looking at her, and they became astonished. Then the husband spoke: 'I am Sky; you are Earth.' Then she climbed onto the millstone. Fire, guard this wife! May sons and daughters be born to her, and may she live with the husband. May death not reach her. | Yesterday the father gave his own daughter. And the husband gave the bride price: four horses. And the mother clothed her in new wool. And the sister placed a comb on her head. Then the husband led her from the house. Her two brothers walked after. And then they arrived at the husband's fence. And three times the husband led her around the Fire. The husband's brother seated her by the Fire. The husband's brothers were looking at her, and then they became astonished. And then the new husband spoke: 'I am Sky, and you are Earth.' Then she climbed onto the shiny millstone. And, Fire, guard this wife! May sons indeed be born to her. May she live with the husband, may death not reach her. |

### t008-0002 (wedding) Go to Your Husband's House

Edits (clause indices as in the plan): c0 particle: None -> nu; c1 particle: None -> nu; c1 add dhugh2texr:VOC; c2 drop personal/2:POSS; c3 sentence break: None -> True; c4 drop h2ewsoxs:LOC; c5 conj: kʷe -> None; c9 particle: None -> nu; c9 conj: None -> kʷe; c10 particle: None -> nu; c11 particle: None -> ge; c12 drop h2yewHox:VOC; c13 conj: None -> kʷe; c13 sentence break: True -> None; c14 particle: None -> nu; c14 sentence break: None -> True

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| dʰúgh₂ter toy póteys dʰéh₁mn̥ gʷh₂dʰí (10) / pótnih₂ h₂én h₁syéh₁s (4) / téwe te póteys méh₂tēr swésōr-kʷe wn̥Hih₁tā́m dayh₂wéres-kʷe te wn̥Hih₁ént (21) / h₂usési sth₂dʰí wódr̥-kʷe bʰére péh₂wr̥-kʷe h₂réydʰe (15) | nu toy dʰúgh₂ter póteys dʰéh₁mn̥ gʷh₂dʰí (11) / nu dʰúgh₂ter pótnih₂ h₂én h₁syéh₁s (8) / póteys te méh₂tēr swésōr-kʷe wn̥Hih₁tā́m (11) / dayh₂wéres-kʷe te wn̥Hih₁ént (8) / sth₂dʰí wódr̥ bʰére péh₂wr̥-kʷe h₂réydʰe (11) |
| póteys wérǵom h₁ukdʰí (6) / dayh₂wr̥bʰós mē dedwiyéh₁s (7) / pótis toy wiHrós h₁ésti (7) / h₂yúHeni mē tréms (5) / suHnówōm toy suHnúns widóyh₁s deywṓs-kʷe te ph₂sih₁ént (15) | nu-kʷe póteys wérǵom h₁ukdʰí (8) / nu dayh₂wr̥bʰós mē dedwiyéh₁s (8) / pótis-ge toy wiHrós h₁ésti (8) / mē tréms suHnówōm-kʷe toy suHnúns widóyh₁s (11) / nu-kʷe te deywṓs ph₂sih₁ént (8) |

| old English | new English |
|---|---|
| Daughter, go to your husband's house! May you be mistress there. May your husband's mother and sister come to love you, and may the husband's brothers come to love you. Stand up at dawn, carry water, and make the fire ready. | Daughter, now go to your husband's house! Daughter, now may you be mistress there. May the husband's mother and sister come to love you. And may the husband's brothers come to love you. Stand up, carry water, and make the fire ready. |
| Learn the husband's work! May you not be afraid of the husband's brothers. Your husband is a hero. Young one, do not tremble! May you see the sons of your sons, and may the gods guard you. | And now learn the husband's work! Now may you not be afraid of the husband's brothers. Your husband is indeed a hero. Do not tremble, and may you see the sons of your sons. And now may the gods guard you. |

### t008-0003 (wedding) The Wedding Wagon

Edits (clause indices as in the plan): c0 drop h2yewHox:MOD; c1 sentence break: None -> True; c2 drop newos:MOD; c4 particle: None -> nu; c4 sentence break: None -> True; c6 sentence break: None -> True; c8 particle: None -> ge; c10 conj: kʷe -> None; c11 conj: None -> kʷe; c14 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₂yéwHō pótis kʷékʷlōy dwóh₁ HeHḱúh₁ h₁éḱwoh₁ yunégt h₂yuHn̥yéh₂s-kʷe dʰéh₁mn̥ h₁élh₂t (21) / néweh₂m h₂wĺ̥h₁neh₂m wésm̥h₁neh₂ séh₂ dʰéyǵʰesi sth₂éh₁yet (13) / tósyeh₂s bʰréh₂tēr tā́m h₁éǵʰs wédʰet tā́m-kʷe kʷékʷloy sodéyet (15) / nu pótis tóh₁ h₂epó h₂éǵet dayh₂wéres-kʷe tā́m sékʷonto (16) / stóygʰos h₁itós h₁ést tóy-kʷe ne h₃slidʰént (10) / h₂éwis gʰórdʰoy sédt séh₂-kʷe séh₂gyet (9) / póteys swésōr tā́m ph₂wéni h₁áyto (10) | pótis kʷékʷlōy dwóh₁ HeHḱúh₁ h₁éḱwoh₁ yunégt (11) / h₂yuHn̥yéh₂s-kʷe dʰéh₁mn̥ h₁élh₂t (8) / h₂wĺ̥h₁neh₂m wésm̥h₁neh₂ séh₂ dʰéyǵʰesi sth₂éh₁yet (11) / tósyeh₂s bʰréh₂tēr tā́m h₁éǵʰs wédʰet (8) / nu-kʷe tā́m kʷékʷloy sodéyet (8) / nu pótis tóh₁ h₂epó h₂éǵet (8) / dayh₂wéres-kʷe tā́m sékʷonto (8) / stóygʰos h₁itós h₁ést tóy-kʷe-ge ne h₃slidʰént (11) / h₂éwis gʰórdʰoy sédt séh₂ séh₂gyet (8) / póteys-kʷe swésōr tā́m ph₂wéni h₁áyto (11) |
| dayh₂wéres pórḱom pékʷont (7) | dayh₂wéres-kʷe pórḱom pékʷont (8) |

| old English | new English |
|---|---|
| The young husband joined two swift horses to the wagon and drove to the young woman's house. She, wearing new wool, was standing by the wall. Her brother led her out and seated her on the wagon. Then the husband drove them away, and the husband's brothers followed her. The road was passable, and they did not go astray. A bird sat down on the fence, and it gave a sign. The husband's sister received her at the fire. | The husband joined two swift horses to the wagon. And he drove to the young woman's house. She, wearing wool, was standing by the wall. Her brother led her out. And then he seated her on the wagon. Then the husband drove them away. And the husband's brothers followed her. The road was passable, and indeed they did not go astray. A bird sat down on the fence, it gave a sign. And the husband's sister received her at the fire. |
| The husband's brothers cooked a piglet. | And the husband's brothers cooked a piglet. |

### t008-0004 (wedding) Blessing of the Couple

Edits (clause indices as in the plan): c0 particle: None -> nu; c1 potnih2:VOC 'and' mark True -> False; c2 add bheh2nos:MOD; c6 conj: kʷe -> None; c7 drop demonstrative_so:MOD; c10 particle: None -> nu; c10 conj: None -> kʷe; c12 particle: None -> nu; c14 sentence break: True -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁ń̥gʷney nos h₁uséwōm déh₃tor ḱludʰí (10) / pótey pótnih₂-kʷe wí mē gʷh₂tóm (9) / h₂usú mudih₁tóm (5) | nu nos h₁ń̥gʷney h₁uséwōm déh₃tor ḱludʰí (11) / pótey pótni wí mē gʷh₂tóm (8) / bʰeh₂néh₂su h₂usú mudih₁tóm (8) |
| pótni tóm sékʷeso gʷr̥h₂wéni-kʷe wr̥ǵyé (12) / tód dʰéh₁mn̥ déh₃n̥bʰis pl̥nh₁ih₁tó (9) | pótni tóm sékʷeso gʷr̥h₂wéni wr̥ǵyé (11) / dʰéh₁mn̥ déh₃n̥bʰis pl̥nh₁ih₁tó (8) |
| péḱesh₁ h₃pusih₁tóm (6) / gʷowsth₂ós pl̥h₁yéh₁t yóh₁r̥-kʷe dʰedʰugʰyéh₁t (10) / wĺ̥kʷōs mē dʰgʷʰh₂ih₁ént (5) / mértim mē widóyh₁tom (6) | nu-kʷe péḱesh₁ h₃pusih₁tóm (8) / gʷowsth₂ós pl̥h₁yéh₁t nu-kʷe yóh₁r̥ dʰedʰugʰyéh₁t (11) / wĺ̥kʷōs mē dʰgʷʰh₂ih₁ént mértim mē widóyh₁tom (11) |

| old English | new English |
|---|---|
| Fire, giver of good things, hear us! Husband and wife, do not go apart! May you two become joyful at the dawns. | Now, Fire, giver of good things, hear us! Husband, wife, do not go apart! May you two become joyful at the shiny dawns. |
| Wife, follow him, and work at the millstone! May this house be filled with gifts. | Wife, follow him, work at the millstone! May the house be filled with gifts. |
| May you two increase in wealth. May the cow-stall become full, and may the harvest season be productive. May the wolves not come near! May you two not see death. | And now may you two increase in wealth. May the cow-stall become full, and now may the harvest season be productive. May the wolves not come near, may you two not see death. |

### t008-0005 (wedding) The Bride Price

Edits (clause indices as in the plan): c1 sentence break: True -> None; c1 drop h2yewHox:MOD; c3 conj: None -> kʷe; c4 drop numerals/2:MOD; c4 drop wedhmn:OBJ; c5 particle: None -> ge; c6 particle: None -> nu; c6 conj: None -> kʷe; c8 particle: nu -> None; c9 drop h2epo:ADV; c11 particle: None -> nu; c11 sentence break: None -> True

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| ph₂tḗr wérh₁t (4) / kʷíd moy h₂yéwHon wíHre dédeh₃si (9) | ph₂tḗr wérh₁t kʷíd moy wíHre dédeh₃si (11) |
| nu wérh₁t h₂yéwHō wiHrós (7) / déḱm̥ gʷṓs dwóh₁ HeHḱúh₁ h₁éḱwoh₁ wédʰmn̥-kʷe dédeh₃mi (14) / déh₃ōr toy mh₂ḱréh₂ h₁ésti (7) / h₂éh₂usom wéǵʰesi (6) | nu-kʷe wérh₁t h₂yéwHō wiHrós (8) / déḱm̥ gʷṓs HeHḱúh₁-kʷe h₁éḱwoh₁ dédeh₃mi (11) / déh₃ōr-ge toy mh₂ḱréh₂ h₁ésti (8) / nu-kʷe h₂éh₂usom wéǵʰesi (8) |
| nu moy dʰugh₂térm̥ sl̥h₂gʷdʰí tā́m-kʷe h₂epó wédʰe (14) / nu wiHrós tā́m h₂epó wédʰet séh₂-kʷe tósyo pótnih₂ bʰúHt (15) | dʰugh₂térm̥ moy sl̥h₂gʷdʰí tā́m-kʷe wédʰe (11) / nu wiHrós tā́m h₂epó wédʰet (8) / nu-kʷe séh₂ tósyo pótnih₂ bʰúHt (8) |

| old English | new English |
|---|---|
| The father spoke: 'Young man, what do you give me? My daughter knows work.' Then the young man spoke: 'I give ten cows and two swift horses as the bride price.' 'Your gifts are meager. Are you conveying gold?' 'I am conveying gold and fat.' 'Then take my daughter, and lead her away!' Then the man led her away, and she became his wife. | The father spoke: 'Man, what do you give me? My daughter knows work.' And then the young man spoke: 'I give ten cows and two swift horses.' 'Your gifts are indeed meager. And then are you conveying gold?' 'I am conveying gold and fat.' 'Take my daughter, and lead her!' Then the man led her away. And then she became his wife. |

### t008-0006 (wedding) The Mother to the Bride

Edits (clause indices as in the plan): c0 particle: None -> nu; c1 particle: None -> nu; c1 add newos:MOD; c4 particle: None -> nu; c4 conj: None -> kʷe; c4 sentence break: True -> None; c5 particle: None -> nu; c5 conj: None -> kʷe; c6 sentence break: None -> True; c9 sentence break: None -> True; c10 particle: None -> nu; c11 particle: None -> ge; c11 drop dhugh2texr:SUBJ; c11 drop dyexws:POSS

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| dʰúgh₂ter toy méh₂term̥ linékʷsi (10) / swóh₁ pótih₁ gʷh₂dʰí (5) | nu toy dʰúgh₂ter méh₂term̥ linékʷsi (11) / nu swóh₁ néwoh₁ pótih₁ gʷh₂dʰí (8) |
| dʰúgh₂ter h₂uHsó (5) / stóygʰōd mē bʰéyh₂s (4) / stóygʰos toy h₁itós h₁syéh₁t dayh₂wéres-kʷe te dukih₁ént (14) / h₂wĺ̥h₁neh₂m wéso h₁yéh₂m toy déh₃m̥ memn̥dʰí-kʷe me meménoh₂-kʷe te (18) / h₂éwsōs toy diwés dʰugh₂tḗr h₂usyéh₁t ḱḗr-kʷe toy mudyéh₁t (15) | dʰúgh₂ter h₂uHsó nu-kʷe stóygʰōd mē bʰéyh₂s (11) / nu-kʷe toy stóygʰos h₁itós h₁syéh₁t (8) / dayh₂wéres-kʷe te dukih₁ént (8) / h₂wĺ̥h₁neh₂m wéso h₁yéh₂m toy déh₃m̥ (8) / memn̥dʰí-kʷe me nu-kʷe te meménoh₂ (11) / h₂éwsōs-ge toy h₂usyéh₁t ḱḗr-kʷe toy mudyéh₁t (11) |

| old English | new English |
|---|---|
| Daughter, you are leaving your mother. Go with your own husband! | Now, daughter, you are leaving your mother. Now go with your own new husband! |
| Daughter, put on footwear! Do not be afraid of the road! May the road be passable for you, and may the husband's brothers lead you. Wear the wool which I gave you, and remember me, and I shall remember you! May Dawn, the daughter of Sky, become bright for you, and may your heart become joyful. | Daughter, put on footwear, and now do not be afraid of the road! And now may the road be passable for you. And may the husband's brothers lead you. Wear the wool which I gave you. And remember me, and now I shall remember you! May Dawn indeed become bright for you, and may your heart become joyful. |

### t008-0007 (wedding) The Wedding of the Sun's Daughter

Edits (clause indices as in the plan): c1 particle: nu -> None; c1 drop diwyos:MOD; c4 conj: None -> kʷe; c4 drop demonstrative_so:POSS; c5 particle: None -> nu; c5 sentence break: None -> True; c7 drop diwyos:MOD; c9 particle: None -> nu; c11 particle: None -> nu; c11 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu diwyós deywós sh₂wéns gʰórdʰom gʷémt tā́m-kʷe h₂isḱét (14) | deywós sh₂wéns gʰórdʰom gʷémt tā́m-kʷe h₂isḱét (11) |
| tósyeh₂s Hróth₂os sh₂wéns kʷékʷlos h₁ést dwóh₁-kʷe HeHḱúh₁ h₁éḱwoh₁ tā́m wéǵʰetām (19) / h₂éwsōs pró stéygʰet diwyṓs-kʷe deywṓs tā́m spéḱyont (13) / lówksneh₂ tā́m sékʷeto móri-kʷe léwkt (10) | Hróth₂os-kʷe sh₂wéns kʷékʷlos h₁ést (8) / nu-kʷe dwóh₁ HeHḱúh₁ h₁éḱwoh₁ tā́m wéǵʰetām (11) / h₂éwsōs pró stéygʰet deywṓs-kʷe tā́m spéḱyont (11) / lówksneh₂ tā́m sékʷeto nu-kʷe móri léwkt (11) |
| déywōs tā́m h₂léksete (6) | nu-kʷe déywōs tā́m h₂léksete (8) |

| old English | new English |
|---|---|
| Then a heavenly god arrived at the fence of the Sun, and he was seeking her. | A god arrived at the fence of the Sun, and he was seeking her. |
| Her chariot was the wheel of the sun, and two swift horses were conveying her. Dawn was walking ahead, and the heavenly gods were looking at her. The Moon followed her, and the sea became bright. | And the chariot was the wheel of the sun. And then two swift horses were conveying her. Dawn was walking ahead, and the gods were looking at her. The Moon followed her, and then the sea became bright. |
| Gods, protect her! | And now, gods, protect her! |

### t008-0008 (wedding) The Wife Enters the House

Edits (clause indices as in the plan): c0 add newos:MOD; c2 conj: kʷe -> None; c3 particle: None -> nu; c3 conj: None -> kʷe; c4 particle: None -> ge; c4 conj: None -> kʷe; c6 particle: None -> nu; c6 conj: None -> kʷe; c6 sentence break: True -> None; c8 conj: kʷe -> None; c9 add h1wesus:MOD; c10 particle: None -> nu; c10 conj: None -> kʷe; c12 sentence break: None -> True

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| pótni dʰéh₁mn̥ wiḱdʰí (6) / sélpos dʰéyǵʰesi h₂linHdʰí h₁n̥gʷnéy-kʷe sddʰí (12) / h₂ówins h₂wĺ̥h₁neh₂m-kʷe h₁n̥dó bʰére (9) / póteys ḱunés mē bʰéyh₂s (6) / wódr̥ yéseti (5) / pórḱom pékʷe (4) / dayh₂wéres h₂énti stesth₂ḗr spéḱyonti-kʷe te (12) / tóybʰos déh₃ōr duh₃dʰí (6) / tód toy péh₂wr̥ dʰégʷʰoyh₁t (6) / suHnús toy wiHrós ǵeǵn̥h₁yéh₁t tósyo-kʷe h₁nómn̥ ḱlutóm h₁syéh₁t (16) | pótni néwom dʰéh₁mn̥ wiḱdʰí (8) / sélpos dʰéyǵʰesi h₂linHdʰí h₁n̥gʷnéy sddʰí (11) / nu-kʷe h₂ówins h₂wĺ̥h₁neh₂m-kʷe h₁n̥dó bʰére (11) / póteys-kʷe-ge ḱunés mē bʰéyh₂s (8) / wódr̥ yéseti nu-kʷe pórḱom pékʷe (11) / dayh₂wéres h₂énti stesth₂ḗr spéḱyonti te (11) / tóybʰos h₁wésuh₂ déh₃ōr duh₃dʰí (8) / nu-kʷe toy tód péh₂wr̥ dʰégʷʰoyh₁t (8) / suHnús toy wiHrós ǵeǵn̥h₁yéh₁t (8) / tósyo-kʷe h₁nómn̥ ḱlutóm h₁syéh₁t (8) |

| old English | new English |
|---|---|
| Wife, enter the house! Smear fat on the wall, and sit down by the Fire! Carry the sheep and the wool inside. Do not be afraid of the husband's dog! The water is boiling. Cook the piglet! The husband's brothers are standing near, and they are looking at you. Give them gifts! May this fire burn for you. May a son be born to you, a hero, and may his name be famous. | Wife, enter the new house! Smear fat on the wall, sit down by the Fire! And now carry the sheep and the wool inside. And indeed do not be afraid of the husband's dog! The water is boiling, and now cook the piglet! The husband's brothers are standing near, they are looking at you. Give them good gifts! And now may this fire burn for you. May a son be born to you, a hero. And may his name be famous. |

### t008-0009 (lament) Lament for a Hero

Edits (clause indices as in the plan): c4 conj: None -> kʷe; c6 conj: kʷe -> None; c8 particle: None -> nu; c12 conj: None -> kʷe; c13 drop demonstrative_so:MOD

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| HeHḱéwes toy h₁éḱwōs Hróth₂oy stesth₂ḗr (10) / h₁léwdʰeros h₁és h₁égʷʰis-kʷe ne bʰéyh₂s (9) / h₁ógʷʰim gʷʰéns gʷṓs-kʷe swóm gʷowsth₂óm h₁élh₂s (10) | HeHḱéwes-kʷe toy h₁éḱwōs Hróth₂oy stesth₂ḗr (11) / h₁léwdʰeros h₁és h₁égʷʰis ne bʰéyh₂s (8) / h₁ógʷʰim gʷʰéns nu-kʷe gʷṓs swóm gʷowsth₂óm h₁élh₂s (11) |
| nu te h₁n̥gʷním bʰéromes (7) / h₁ń̥gʷney tóm wiHróm deywóns wéǵʰe (9) | nu-kʷe te h₁n̥gʷním bʰéromes (8) / h₁ń̥gʷney wiHróm deywóns wéǵʰe (8) |

| old English | new English |
|---|---|
| Your swift horses are standing by the chariot. You were free, and you did not grow afraid of the serpent. You slew the serpent, and you drove the cattle to your own cow-stall. | And your swift horses are standing by the chariot. You were free, you did not grow afraid of the serpent. You slew the serpent, and then you drove the cattle to your own cow-stall. |
| Now we carry you to the Fire. Fire, convey this hero to the gods! | And now we carry you to the Fire. Fire, convey the hero to the gods! |

### t008-0010 (lament) The Lord Is Gone

Edits (clause indices as in the plan): c2 particle: nu -> None; c2 add wikjpotis:VOC; c3 drop h2wlh1neh2:OBJ; c5 particle: nu -> None; c8 conj: None -> kʷe; c9 particle: None -> ge; c10 particle: None -> nu; c12 conj: kʷe -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu nos kʷís h₂lékseti (6) / h₂éh₂usom nos h₂wĺ̥h₁neh₂m-kʷe dédeh₃s h₂éǵrons-kʷe nos péh₂s (14) / nu h₃mígʰleh₂es sóh₂wl̥ ḱélonti (9) | kʷís nos wíḱpotey h₂lékseti (8) / h₂éh₂usom nos dédeh₃s h₂éǵrons-kʷe nos péh₂s (11) / h₃mígʰleh₂es sóh₂wl̥ ḱélonti (8) |
| h₂énǵʰos nos ḱr̥dsú h₁ésti (7) / swépnos nos ne gʷm̥yéti (7) / dʰéyǵʰesi toy sísdomes (7) / memn̥mé te ḱléwos-kʷe toy méǵh₂ h₁ésti (12) | h₂énǵʰos-kʷe nos ḱr̥dsú h₁ésti (8) / swépnos-ge nos ne gʷm̥yéti (8) / nu toy dʰéyǵʰesi sísdomes (8) / memn̥mé te ḱléwos toy méǵh₂ h₁ésti (11) |

| old English | new English |
|---|---|
| Who now protects us? You used to give us gold and wool, and you guarded our fields. Now clouds cover the sun. | Lord, who protects us? You used to give us gold, and you guarded our fields. Clouds cover the sun. |
| Grief is in our hearts. Sleep does not come to us. We are sitting down by your wall. We remember you, and your fame is great. | And grief is in our hearts. Sleep indeed does not come to us. Now we are sitting down by your wall. We remember you, your fame is great. |

### t008-0011 (lament) The Widow's Lament

Edits (clause indices as in the plan): c1 sentence break: True -> None; c1 drop dheh1mn:POSS; c1 drop personal/2:POSS; c3 conj: kʷe -> None; c4 drop personal/2:POSS; c5 particle: nu -> None; c7 drop personal/2:POSS; c9 sentence break: True -> None; c11 conj: None -> kʷe; c13 conj: None -> kʷe; c13 sentence break: True -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| pótey me linékʷs (5) / dʰh₁méns toy péh₂wr̥ ne dʰégʷʰeti (9) / téwe te ḱwṓ h₂isḱéti h₁eǵóh₂-kʷe trésoh₂ (12) / suHnéwes toy h₂yéwHones h₁sénti (9) / nu kʷís tóns wédʰeti kʷís-kʷe h₂érh₃yēti (12) / h₂óḱets toy dʰéyǵʰesi légʰyeti (9) / kʷíh₁ séngʷs (2) / h₂ówins ph₂sónts túH tr̥méni séngʷs (9) | pótey me linékʷs péh₂wr̥ ne dʰégʷʰeti (11) / téwe te ḱwṓ h₂isḱéti h₁eǵóh₂ trésoh₂ (11) / suHnéwes h₂yéwHones h₁sénti (8) / kʷís tóns wédʰeti kʷís-kʷe h₂érh₃yēti (11) / h₂óḱets dʰéyǵʰesi légʰyeti (8) / kʷíh₁ séngʷs h₂ówins ph₂sónts túH tr̥méni séngʷs (11) |
| wiHrṓs toy h₁wésu ḱléwos ḱluwih₁ént (10) / h₂ew mē snéwbʰōh₂ (4) / pótey te memónh₂e (6) | wiHrṓs-kʷe toy h₁wésu ḱléwos ḱluwih₁ént (11) / h₂ew mē snéwbʰōh₂ pótey-kʷe te memónh₂e (11) |

| old English | new English |
|---|---|
| Husband, you left me. The fire of your house does not burn. Your dog is seeking you, and I tremble in fear. Your sons are young. Who now leads them, and who will plough? Your harrow lies by the wall. | Husband, you left me, the fire does not burn. Your dog is seeking you, I tremble in fear. The sons are young. Who leads them, and who will plough? The harrow lies by the wall. |
| May men hear your good fame. I shall not marry again. Husband, I remember you. | And may men hear your good fame. I shall not marry again, and, husband, I remember you. |

### t008-0012 (lament) You Who Gave Us Horses

Edits (clause indices as in the plan): c3 drop personal/1:POSS; c4 conj: None -> kʷe; c7 drop personal/2:POSS; c8 conj: None -> kʷe; c10 particle: nu -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁yós wĺ̥kʷons gʷʰéns h₁yós nos térmn̥ péh₂s (9) / nu te supnós kapyéti (7) | h₁yós wĺ̥kʷons gʷʰéns h₁yós térmn̥ péh₂s (8) / nu-kʷe te supnós kapyéti (8) |
| bʰréh₂teres toy twé péri stesth₂ḗr (9) / swésores toy ḱr̥h₂séni sédyonti (10) / Hróth₂os toy sth₂éh₁yeti nu kʷís tóm h₂éǵeti (12) | bʰréh₂teres twé péri stesth₂ḗr (8) / swésores-kʷe toy ḱr̥h₂séni sédyonti (11) / Hróth₂os toy sth₂éh₁yeti kʷís tóm h₂éǵeti (11) |

| old English | new English |
|---|---|
| You who slew the wolves, you who guarded our boundary! Now sleep grasps you. | You who slew the wolves, you who guarded the boundary! And now sleep grasps you. |
| Your brothers stand around you. The sisters sit at your head. Your chariot stands: who now drives it? | The brothers stand around you. And the sisters sit at your head. Your chariot stands: who drives it? |

### t008-0013 (lament) The Mother's Lament

Edits (clause indices as in the plan): c0 particle: None -> nu; c2 conj: kʷe -> None; c4 particle: None -> ge; c8 conj: kʷe -> None; c10 particle: None -> nu; c10 conj: None -> kʷe; c10 sentence break: True -> None; c11 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| súHnew moy kúdʰe h₁ési (7) / ní ḱéyth₂er kʷséps-kʷe te ḱéleti (9) / h₂énts toy stéwdt h₂yéwHō-kʷe h₁és (7) | nu moy súHnew kúdʰe h₁ési (8) / ní ḱéyth₂er kʷséps te ḱéleti (8) / h₂énts toy stéwdt h₂yéwHō-kʷe-ge h₁és (8) |
| upó bʰuHyés wiHrós-kʷe ne bʰúHs (9) / kʷís te h₁épt (3) / mértis te kʷsépi h₁épt (6) / dʰéǵʰom méh₂ter tóm ph₂sdʰí (7) | upó bʰuHyés wiHrós ne bʰúHs (8) / kʷís te h₁épt nu-kʷe te mértis kʷsépi h₁épt (11) / dʰéǵʰom-kʷe méh₂ter tóm ph₂sdʰí (8) |

| old English | new English |
|---|---|
| My son, where are you? You are lying down, and the night covers you. Your forehead has grown cold, and you were young. | Now, my son, where are you? You are lying down, the night covers you. Your forehead has grown cold, and you were indeed young. |
| You were growing up, and you did not become a man. | You were growing up, you did not become a man. |
| Death seized you in the night. Mother Earth, guard him! | And then death seized you in the night. And, Mother Earth, guard him! |

### t008-0014 (lament) Go to the Fathers

Edits (clause indices as in the plan): c4 conj: kʷe -> None; c6 conj: kʷe -> None; c10 drop numerals/2:MOD; c11 conj: kʷe -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| tósyo ḱḗr stéwdt tósyo-kʷe ḱwṓ ḱóm légʰyeti (12) / tóm tl̥néh₂omes tóm-kʷe ní logʰéyōmes (12) | tósyo ḱḗr stéwdt tósyo ḱwṓ ḱóm légʰyeti (11) / tóm tl̥néh₂omes tóm ní logʰéyōmes (11) |
| dwóh₁ ḱwónh₁e dʰgʷʰh₂dʰí ph₂téres-kʷe te h₁áyih₁ro (13) | ḱwónh₁e dʰgʷʰh₂dʰí ph₂téres te h₁áyih₁ro (11) |

| old English | new English |
|---|---|
| His heart has grown cold, and his dog lies down close by. Let us lift him, and let us lay him down. | His heart has grown cold, his dog lies down close by. Let us lift him, let us lay him down. |
| Pass by the two dogs, and may the fathers receive you. | Pass by the two dogs, may the fathers receive you. |

### t008-0015 (lament) The Burning of the Lord

Edits (clause indices as in the plan): c1 conj: kʷe -> None; c2 particle: None -> nu; c2 conj: None -> kʷe; c2 add diwyos:MOD; c4 particle: None -> nu; c4 add diwyos:MOD; c5 drop demonstrative_so:POSS; c5 drop h2enti:ADV; c6 sentence break: True -> None; c7 particle: nu -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| wiḱpótis kʷsépi mért h₂éweyes-kʷe litént (12) / lówksneh₂ ne léwkt (4) | wiḱpótis kʷsépi mért h₂éweyes litént (11) / nu-kʷe diwyéh₂ lówksneh₂ ne léwkt (8) |
| péh₂wr̥ tóm h₁éwset (5) / tósyo tr̥mn̥tíh₂ pótnih₂ h₂énti sédt (10) / tósyo ḱwṓ ne h₁ḗdt (5) / nu wiHrṓs tósyo wérǵeh₂ h₁érkʷont (9) | nu diwyóm péh₂wr̥ tóm h₁éwset (8) / tr̥mn̥tíh₂ pótnih₂ sédt tósyo ḱwṓ ne h₁ḗdt (11) / wiHrṓs tósyo wérǵeh₂ h₁érkʷont (8) |

| old English | new English |
|---|---|
| The lord died in the night, and the birds went away. The moon did not become bright. | The lord died in the night, the birds went away. And then the heavenly moon did not become bright. |
| The fire burned him. His wife sat down near, trembling. His dog did not eat. Then the men praised his works. | Then the heavenly fire burned him. The wife sat down, trembling, his dog did not eat. The men praised his works. |

### t008-0016 (lament) The Father's Lament

Edits (clause indices as in the plan): c1 particle: None -> ge; c2 particle: None -> nu; c2 conj: None -> kʷe; c4 conj: kʷe -> None; c6 sentence break: True -> None; c7 particle: None -> nu; c7 conj: None -> kʷe; c8 particle: None -> ge; c8 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| HeHḱúm Hróth₂om térmn̥ upér h₂éǵes (10) / wĺ̥kʷos médʰyeh₂i kʷsépi sérpet (9) / wĺ̥kʷom próti gʷéh₂s wĺ̥kʷos-kʷe te moréyet (12) / ḱḗr toy skérdʰet (4) / nu toy méh₂tēr ne h₁ḗdti (7) / wódr̥ ne píph₃eti (6) / h₁eǵóh₂ te ph₂tḗr h₁n̥gʷním bʰéroh₂ (9) | HeHḱúm-ge Hróth₂om térmn̥ upér h₂éǵes (11) / nu-kʷe wĺ̥kʷos médʰyeh₂i kʷsépi sérpet (11) / wĺ̥kʷom próti gʷéh₂s wĺ̥kʷos te moréyet (11) / ḱḗr toy skérdʰet nu toy méh₂tēr ne h₁ḗdti (11) / nu-kʷe wódr̥ ne píph₃eti (8) / h₁eǵóh₂-kʷe-ge te ph₂tḗr h₁n̥gʷním bʰéroh₂ (11) |

| old English | new English |
|---|---|
| You drove the swift chariot over the boundary. A wolf was creeping in the middle of the night. You went against the wolf, and the wolf killed you. Your heart was pierced. Now your mother does not eat. She does not drink water. I, the father, carry you to the Fire. | You indeed drove the swift chariot over the boundary. And then a wolf was creeping in the middle of the night. You went against the wolf, the wolf killed you. Your heart was pierced, now your mother does not eat. And then she does not drink water. And I, the father, indeed carry you to the Fire. |

### t008-0017 (lament) The Praiser Mourns His Lord

Edits (clause indices as in the plan): c1 particle: None -> nu; c1 conj: None -> kʷe; c2 conj: None -> kʷe; c5 particle: nu -> None; c9 conj: None -> kʷe; c10 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| lelóykʷe h₂éh₂usosyo déh₃tōr (9) / lelóykʷe h₁éḱwōm h₁esh₂ós (7) / wíḱpotey nos sóh₂wl̥ h₁és ní séngʷs nu kʷséps gʷémt (12) | nu-kʷe lelóykʷe h₂éh₂usosyo déh₃tōr (11) / lelóykʷe-kʷe h₁éḱwōm h₁esh₂ós (8) / wíḱpotey nos sóh₂wl̥ h₁és ní séngʷs kʷséps gʷémt (11) |
| néwom toy kéh₂nmn̥ tḗtḱmi (7) / tód te deywóns bʰéreti (7) | néwom-kʷe toy kéh₂nmn̥ tḗtḱmi (8) / tód-kʷe te deywóns bʰéreti (8) |

| old English | new English |
|---|---|
| Gone is the great lord; gone is the giver of gold; gone is the master of the horses. Lord, you were our sun; you sank down; now the night has come. | Gone is the great lord; and now gone is the giver of gold; and gone is the master of the horses. Lord, you were our sun; you sank down; the night has come. |
| I am fashioning a new song for you. It carries you to the gods. | And I am fashioning a new song for you. And it carries you to the gods. |

### t008-0018 (lament) The Sister's Lament

Edits (clause indices as in the plan): c1 conj: None -> kʷe; c2 conj: None -> kʷe; c4 conj: kʷe -> None; c5 particle: None -> nu; c5 conj: None -> kʷe; c7 particle: None -> nu; c9 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| déḱm̥ márkons térmn̥ upér h₁élh₂s (10) / nu te wiHrṓs kʷsépi gʷʰnént (7) / h₁ésh₂r̥ toy h₂éǵroy térst ḱwónes-kʷe tód liǵʰént (12) / h₂éḱruh₂ nos méh₂tr̥s séngʷt (6) / swésōr nos ne bʰéh₂ti h₂isḱóh₂-kʷe te (10) | déḱm̥-kʷe márkons térmn̥ upér h₁élh₂s (11) / nu-kʷe te wiHrṓs kʷsépi gʷʰnént (8) / h₁ésh₂r̥ toy h₂éǵroy térst ḱwónes tód liǵʰént (11) / nu-kʷe nos h₂éḱruh₂ méh₂tr̥s séngʷt (8) / swésōr nos ne bʰéh₂ti nu-kʷe te h₂isḱóh₂ (11) |
| h₁wésu toy ḱléwos ń̥dʰgʷʰitom h₁ésti (10) | h₁wésu-kʷe toy ḱléwos ń̥dʰgʷʰitom h₁ésti (11) |

| old English | new English |
|---|---|
| You drove ten horses over the boundary. Then men struck you down in the night. Your blood dried on the field, and the dogs licked it. Tears fell from our mother. Our sister does not speak, and I am seeking you. | And you drove ten horses over the boundary. And then men struck you down in the night. Your blood dried on the field, the dogs licked it. And then tears fell from our mother. Our sister does not speak, and now I am seeking you. |
| Your good fame is imperishable. | And your good fame is imperishable. |

### t008-0027 (praise) The Giver of Good Things

Edits (clause indices as in the plan): c2 particle: None -> nu; c2 drop HeHkjus:MOD; c3 particle: None -> ge; c3 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁yód h₂éwsōs h₂wést déḱm̥ moy HeHḱúns h₁éḱwons déh₃t (12) / oḱtṓw gʷṓs péruti h₁opéyet (9) | h₁yód h₂éwsōs h₂wést nu moy déḱm̥ h₁éḱwons déh₃t (11) / oḱtṓw-kʷe-ge gʷṓs péruti h₁opéyet (11) |

| old English | new English |
|---|---|
| When Dawn became bright, he gave me ten swift horses. Last year he gave eight cows. | When Dawn became bright, then he gave me ten horses. And last year he indeed gave eight cows. |

### t008-0028 (praise) Who Gave These Horses?

Edits (clause indices as in the plan): c0 drop demonstrative_so:MOD; c2 drop numerals/3:MOD; c5 conj: kʷe -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| kʷís moy tóns kʷetwórn̥s h₁éḱwons déh₃t (9) | kʷís moy kʷetwórn̥s h₁éḱwons déh₃t (8) |
| tríns kʷékʷlons h₁opéyet h₂éh₂usoh₁ pl̥nh₁n̥tó (12) / tóns stóygʰoy ǵʰḗm wiHrṓs-kʷe me kʷḱént (9) | kʷékʷlons h₁opéyet h₂éh₂usoh₁ pl̥nh₁n̥tó (11) / tóns stóygʰoy ǵʰḗm wiHrṓs me kʷḱént (8) |

| old English | new English |
|---|---|
| Who gave me these four horses? | Who gave me four horses? |
| He gave three wagons; they were filled with gold. I drove them on along the road, and the men caught sight of me. | He gave wagons; they were filled with gold. I drove them on along the road, the men caught sight of me. |

### t008-0029 (praise) The Lord Heard My Song

Edits (clause indices as in the plan): c2 particle: None -> ge; c4 particle: None -> nu; c4 conj: None -> kʷe; c5 particle: None -> nu; c5 conj: None -> kʷe; c9 particle: None -> ge; c9 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| kéh₂nmn̥ moy dʰǵʰyés ḱléwt tósyo-kʷe ḱḗr méwdt (10) | kéh₂nmn̥ moy dʰǵʰyés ḱléwt tósyo-kʷe-ge ḱḗr méwdt (11) |
| tóybʰos gʷowsth₂óm démet (6) / h₁eǵóh₂ wékʷesōm wéydtōr h₁ésmi (9) | nu-kʷe tóybʰos gʷowsth₂óm démet (8) / nu-kʷe h₁eǵóh₂ wékʷesōm wéydtōr h₁ésmi (11) |
| tósyo ḱléwos ń̥dʰgʷʰitom h₁ésti (9) | tósyo-kʷe-ge ḱléwos ń̥dʰgʷʰitom h₁ésti (11) |

| old English | new English |
|---|---|
| Yesterday he heard my song, and his heart became joyful. | Yesterday he heard my song, and his heart indeed became joyful. |
| He built a cow-stall for them. I am one who knows the words. | And then he built a cow-stall for them. And now I am one who knows the words. |
| His fame is imperishable. | And his fame is indeed imperishable. |

### t008-0030 (praise) Two Chariots

Edits (clause indices as in the plan): c0 particle: None -> nu; c0 drop keh2nmn:OBJ; c2 drop pro-2:ADV; c3 particle: None -> nu; c3 conj: None -> kʷe; c7 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| wíḱpotey h₁uséwōm déh₃tor kéh₂nmn̥ ḱludʰí (12) | nu wíḱpotey h₁uséwōm déh₃tor ḱludʰí (11) |
| sélpos moy h₂usú pró dʰédʰeh₁si (9) / h₁léwdʰerōs te wiHrṓs ǵn̥nh₃énti (9) | sélpos moy h₂usú dʰédʰeh₁si (8) / nu-kʷe te h₁léwdʰerōs wiHrṓs ǵn̥nh₃énti (11) |
| mértis te mē h₂eh₂n̥ḱyéh₁t (7) | mértis-kʷe te mē h₂eh₂n̥ḱyéh₁t (8) |

| old English | new English |
|---|---|
| Lord, giver of good things, hear the song! | Now, lord, giver of good things, hear! |
| You put fat before me at the dawns. The free men know you. | You put fat for me at the dawns. And then the free men know you. |
| May death not reach you! | And may death not reach you! |

### t008-0031 (praise) New Words at the Lord's Fire

Edits (clause indices as in the plan): c2 particle: nu -> None; c3 conj: None -> kʷe; c4 particle: None -> nu; c7 particle: None -> nu; c8 particle: None -> nu; c8 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| nu ph₂wéni sédyonts só ḱléwset (9) / nu só stéh₂t ǵnéh₃t-kʷe me (6) | ph₂wéni sédyonts só ḱléwset (8) / nu-kʷe só stéh₂t nu-kʷe me ǵnéh₃t (8) |
| tóns swóm gʷowsth₂óm h₁élh₂m̥ ḱḗr-kʷe moy méwdt (10) / wiḱpóteys ḱléwos ń̥dʰgʷʰitom h₁syéh₁t (9) | tóns swóm gʷowsth₂óm h₁élh₂m̥ nu-kʷe moy ḱḗr méwdt (11) / nu-kʷe wiḱpóteys ḱléwos ń̥dʰgʷʰitom h₁syéh₁t (11) |

| old English | new English |
|---|---|
| Then he, sitting at the fire, was listening. Then he stood up, and he recognized me. | He, sitting at the fire, was listening. And then he stood up, and then he recognized me. |
| I drove them to my own cow-stall, and my heart became joyful. May the lord's fame be imperishable! | I drove them to my own cow-stall, and then my heart became joyful. And now may the lord's fame be imperishable! |

### t008-0032 (praise) The Praiser of the Lord

Edits (clause indices as in the plan): c0 particle: None -> nu; c0 drop personal/1:SUBJ; c2 conj: kʷe -> None; c4 conj: kʷe -> None; c5 conj: None -> kʷe; c6 conj: None -> kʷe; c8 conj: kʷe -> None; c9 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁eǵóh₂ wiḱpóteys stéwtōr h₁ésmi (9) / wĺ̥kʷons térh₂ut térmn̥-kʷe péh₂sti (9) / só memógʰe wĺ̥kʷōs-kʷe tósmōd dedwiyḗr (12) / pénkʷe moy h₁éḱwons h₂wĺ̥h₁neh₂m-kʷe déh₃ut (10) / wiHrṓs moy kéh₂nmn̥ kʷsépi ḱl̥nwénti (10) / só ḱlutós bʰúHt ḱlutós-kʷe bʰúHm̥ (9) / díwyōs déywōs tóm ph₂sté (7) | nu wiḱpóteys stéwtōr h₁ésti (8) / wĺ̥kʷons térh₂ut térmn̥ péh₂sti (8) / só memógʰe wĺ̥kʷōs tósmōd dedwiyḗr (11) / pénkʷe-kʷe moy h₁éḱwons h₂wĺ̥h₁neh₂m-kʷe déh₃ut (11) / wiHrṓs-kʷe moy kéh₂nmn̥ kʷsépi ḱl̥nwénti (11) / só ḱlutós bʰúHt ḱlutós bʰúHm̥ (8) / díwyōs-kʷe déywōs tóm ph₂sté (8) |

| old English | new English |
|---|---|
| I am the praiser of the lord. He overcame the wolves, and he guards the boundary. He has power, and the wolves are afraid of him. He gave me five horses and wool. Men listen to my song in the night. He became famous, and I became famous. Heavenly gods, guard him! | Now I am the praiser of the lord. He overcame the wolves, he guards the boundary. He has power, the wolves are afraid of him. And he gave me five horses and wool. And men listen to my song in the night. He became famous, I became famous. And, heavenly gods, guard him! |

### t008-0033 (praise) Whom Shall I Praise?

Edits (clause indices as in the plan): c0 particle: None -> nu; c0 type: None -> nominal; c0 drop h1esti:V; c2 conj: kʷe -> None; c5 particle: None -> ge; c6 conj: None -> kʷe

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| wiḱpótis ḱlutósyo ph₂trés suHnús h₁ésti (12) / só kʷsépi bʰéwdʰeti h₂ówins-kʷe h₂lékseti (12) | nu wiḱpótis ḱlutósyo ph₂trés suHnús (11) / só kʷsépi bʰéwdʰeti h₂ówins h₂lékseti (11) |
| kʷím moy wékʷesbʰis h₁érkʷōh₂ (7) / méǵh₂m̥ wiḱpótim h₁érkʷōh₂ (7) | kʷím-ge moy wékʷesbʰis h₁érkʷōh₂ (8) / méǵh₂m̥-kʷe wiḱpótim h₁érkʷōh₂ (8) |

| old English | new English |
|---|---|
| The lord is the son of a famous father. He is awake in the night, and he protects the sheep. | Now the lord is the son of a famous father. He is awake in the night, he protects the sheep. |
| Whom shall I praise with my words? I shall praise the great lord. | Whom indeed shall I praise with my words? And I shall praise the great lord. |

### t008-0034 (praise) The Chariot Gift

Edits (clause indices as in the plan): c0 add diwyos:MOD; c0 drop numerals/4:MOD; c3 particle: None -> nu; c3 conj: None -> kʷe; c5 conj: kʷe -> None; c7 drop demonstrative_so:MOD; c8 drop demonstrative_so:OBJ

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| wiḱpótis Hróth₂ōy kʷetwórn̥s h₁éḱwons yunégt (12) | wiḱpótis Hróth₂ōy diwyóns h₁éḱwons yunégt (11) |
| HeHḱéwes ḱwónes tóm sékʷontor (9) / wiHrṓs me spéḱyonti h₁eǵóh₂-kʷe tetórph₂e (12) / tóy wérh₁yonti kʷís toy tóm Hróth₂om déh₃ut (12) / wiḱpótis moy h₁uséwōm déh₃tōr tóm déh₃ut (12) | nu-kʷe HeHḱéwes ḱwónes tóm sékʷontor (11) / wiHrṓs me spéḱyonti h₁eǵóh₂ tetórph₂e (11) / tóy wérh₁yonti kʷís toy Hróth₂om déh₃ut (11) / wiḱpótis moy h₁uséwōm déh₃tōr déh₃ut (11) |

| old English | new English |
|---|---|
| The lord joined four horses to a chariot. | The lord joined heavenly horses to a chariot. |
| The swift dogs follow it. The men are looking at me, and I am satisfied. They are saying, 'Who gave you this chariot?' The lord, the giver of good things, gave it to me. | And then the swift dogs follow it. The men are looking at me, I am satisfied. They are saying, 'Who gave you the chariot?' The lord, the giver of good things, gave to me. |

### t008-0035 (praise) Giver of Horses, Giver of Cows

Edits (clause indices as in the plan): c0 particle: None -> nu; c0 type: None -> nominal; c0 drop h1esti:V; c1 conj: None -> kʷe; c2 particle: None -> nu; c2 conj: None -> kʷe; c7 particle: None -> nu

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| wiḱpótis h₁éḱwōm déh₃tōr h₁ésti (9) / só gʷéwōm déh₃tōr h₁ésti (7) / só h₂éh₂usosyo déh₃tōr h₁ésti (9) | nu wiḱpótis h₁éḱwōm déh₃tōr (8) / só-kʷe gʷéwōm déh₃tōr h₁ésti (8) / nu-kʷe só h₂éh₂usosyo déh₃tōr h₁ésti (11) |
| ḱḗr moy tetórpe gʷowsth₂ós-kʷe moy pléh₁t (10) | ḱḗr moy tetórpe nu-kʷe moy gʷowsth₂ós pléh₁t (11) |

| old English | new English |
|---|---|
| The lord is a giver of horses; he is a giver of cows; he is a giver of gold. | Now the lord is a giver of horses; and he is a giver of cows; and then he is a giver of gold. |
| My heart is satisfied, and my cow-stall has become full. | My heart is satisfied, and then my cow-stall has become full. |

### t008-0036 (praise) Cattle Die

Edits (clause indices as in the plan): c3 particle: None -> nu; c3 conj: None -> kʷe; c5 particle: None -> nu; c5 conj: None -> kʷe; c7 drop personal/1:POSS

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| h₁éyti wétesh₂ m̥rént gʷówes (9) / m̥rént bʰréh₂teres néḱt h₂éh₂usom (9) / h₁wésu ḱléwos ne mért wékʷesu moy h₁ési (12) | h₁éyti wétesh₂ nu-kʷe m̥rént gʷówes (11) / m̥rént bʰréh₂teres nu-kʷe néḱt h₂éh₂usom (11) / h₁wésu ḱléwos ne mért wékʷesu h₁ési (11) |

| old English | new English |
|---|---|
| Years go, cattle die; brothers die, gold vanishes; good fame does not die: you are in my words. | Years go, and now cattle die; brothers die, and now gold vanishes; good fame does not die: you are in the words. |

### t008-0037 (praise) The Lord's Hospitality

Edits (clause indices as in the plan): c1 conj: None -> kʷe; c3 particle: None -> nu; c5 conj: kʷe -> None; c6 drop numerals/2:MOD; c7 conj: None -> kʷe; c9 conj: kʷe -> None

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| pokʷtóm moy sélpos pró dʰéh₁t (7) / nu pórḱom h₂éḱh₃m̥ wódr̥-kʷe péh₃m̥ (10) / h₁eǵóh₂ térpm̥ swépnos-kʷe moy gʷémt (9) / dwóh₁ moy gʷréh₂wonh₁e h₂óḱetm̥-kʷe h₁opéyet (12) / tósyo dʰéh₁mn̥ déh₃n̥bʰis pl̥nh₁ih₁tó (10) / gʷíh₃woyh₁t só péḱesh₁-kʷe h₃pusyéh₁t (9) | pokʷtóm-kʷe moy sélpos pró dʰéh₁t (8) / nu pórḱom h₂éḱh₃m̥ nu-kʷe wódr̥ péh₃m̥ (11) / h₁eǵóh₂ térpm̥ swépnos moy gʷémt (8) / gʷréh₂wonh₁e moy h₂óḱetm̥-kʷe h₁opéyet (11) / tósyo-kʷe dʰéh₁mn̥ déh₃n̥bʰis pl̥nh₁ih₁tó (11) / gʷíh₃woyh₁t só péḱesh₁ h₃pusyéh₁t (8) |

| old English | new English |
|---|---|
| He put cooked butter before me. Then I ate up the piglet, and I drank water. I became satisfied, and sleep came to me. | And he put cooked butter before me. Then I ate up the piglet, and then I drank water. I became satisfied, sleep came to me. |
| May his house be filled with gifts! May he live, and may he increase in wealth! | And may his house be filled with gifts! May he live, may he increase in wealth! |

### t008-0038 (praise) The Two Brothers' Gifts

Edits (clause indices as in the plan): c0 drop numerals/2:MOD; c1 kwekwlos:OBJ 'and' mark True -> False; c2 conj: None -> kʷe; c3 particle: None -> ge; c5 particle: None -> nu; c5 conj: None -> kʷe; c6 particle: None -> ge

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| dwóh₁ moy bʰréh₂terh₁e déh₃ōr duh₃tā́m (9) / déḱm̥ h₁éḱwons kʷetwórn̥s-kʷe kʷékʷlons h₁áytām (12) / h₁éḱwōs HeHḱéwes h₁sénti (7) / kʷékʷlōs h₂wĺ̥h₁neh₂m wéǵʰonti (7) | bʰréh₂terh₁e moy déh₃ōr duh₃tā́m (8) / déḱm̥ h₁éḱwons kʷetwórn̥s kʷékʷlons h₁áytām (11) / h₁éḱwōs-kʷe HeHḱéwes h₁sénti (8) / kʷékʷlōs-ge h₂wĺ̥h₁neh₂m wéǵʰonti (8) |
| bʰóh₁ tóysōm-kʷe swésorn̥s h₁érkʷoh₂ (9) / tóysōm ḱléwos tetn̥yéh₁t (7) | nu-kʷe bʰóh₁ tóysōm-kʷe swésorn̥s h₁érkʷoh₂ (11) / tóysōm-ge ḱléwos tetn̥yéh₁t (8) |

| old English | new English |
|---|---|
| The two brothers gave me gifts: they gave ten horses and four wagons. The horses are swift. The wagons carry wool. | The two brothers gave me gifts: they gave ten horses, four wagons. And the horses are swift. The wagons indeed carry wool. |
| I praise both of them and their sisters. May their fame be stretched out! | And now I praise both of them and their sisters. May their fame indeed be stretched out! |

### t008-0039 (praise) Song, Go to the Lord

Edits (clause indices as in the plan): c1 particle: None -> nu; c2 conj: None -> kʷe; c6 sentence break: True -> None; c6 drop personal/2:POSS

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| kéh₂nmn̥ moy sth₂dʰí h₁esh₂óm-kʷe gʷh₂dʰí (10) / tósmey h₂usési wr̥h₁dʰí (7) | kéh₂nmn̥ moy sth₂dʰí nu-kʷe h₁esh₂óm gʷh₂dʰí (11) / tósmey-kʷe h₂usési wr̥h₁dʰí (8) |
| só ne tr̥syéti (5) / h₁nómn̥ toy ḱlutóm h₁ésti (7) | só ne tr̥syéti h₁nómn̥ ḱlutóm h₁ésti (11) |

| old English | new English |
|---|---|
| My song, stand up, and go to the master. Speak to him at dawn: 'Your praiser is praising you. | My song, stand up, and now go to the master. And speak to him at dawn: 'Your praiser is praising you. |
| He is not thirsty. Your name is famous.' Do not grow tired on the road to the master! | He is not thirsty, the name is famous.' Do not grow tired on the road to the master! |

### t008-0040 (praise) Wealth from the Gods

Edits (clause indices as in the plan): c0 particle: None -> nu; c1 particle: None -> nu; c1 conj: None -> kʷe; c2 gwowsth2os:OBJ 'and' mark True -> False

| old PIE (syllables) | new PIE (syllables) |
|---|---|
| deywṓs wiḱpóteyey péḱos duh₃ént (10) / só moy tód dédeh₃ti (6) / tríns h₁éḱwons h₁néwn̥ gʷṓs gʷowsth₂óm-kʷe h₁opéyet (12) | nu deywṓs wiḱpóteyey péḱos duh₃ént (11) / nu-kʷe moy só tód dédeh₃ti (8) / tríns h₁éḱwons h₁néwn̥ gʷṓs gʷowsth₂óm h₁opéyet (11) |

| old English | new English |
|---|---|
| The gods gave wealth to the lord. He gives it to me. He gave three horses, nine cows and a cow-stall. | Then the gods gave wealth to the lord. And then he gives it to me. He gave three horses, nine cows, a cow-stall. |

