# Meter repair: b003

Date: 2026-10-28. Re-realized with the batch's own model and prompt id: `claude-sonnet-5-5`, `tier3-planner-v3`. `data/generation/batches/b003.json` does not record these, so they were taken from the stored records' `generator` fields. The engine version is `763cfb8`, HEAD at the time of the run. The stored records had `3329964`.

## Result

| | lines | exact | meter_exact | gate |
|---|---|---|---|---|
| before (stored records, current syllabifier; census) | 218 | 30 | 0.138 | would FAIL |
| after | 206 | 192 | **0.932** | **PASS** (every gate) |

Other numbers:
- max lexeme uses: 6 → 7 (cap 7). Now at 7: deywos, h2ewsoxs, lewkos, albhos, krsnos, h1rudhros.
- tokens: 1339 → 1378.
- unchanged: distinct lexemes 238, roots 147, 0 rejects, all exact, 0 duplicates, warnings 16.
- formula_uses: 4 → 4. A trial run that also repaired 0002 dropped this to 3, so 0002 was reverted (see below).

**Diff check.** `corpus/tier3/b003.jsonl` was compared before and after, record by record:
- exactly the 155 records listed below changed `pie`, `english` or plan;
- every other record has identical PIE and English;
- every record's `generator.engine_version` changed, and its `meter` field was recomputed.

## Edit types used

- **drop -kʷe** (asyndeton). The English ", and" becomes "; ".
- **add nu** (clause-initial "now"; "then" in past narrative).
  - Two clauses both with nu are rendered "Now …, and now …".
  - nu on a clause that has -kʷe is written nu-kʷe, as elsewhere in the corpus.
- **add -ge** ("indeed"): only in 0027.
- **split / merge** at a clause boundary. The English sentences are split or joined to match.
- **drop copula h₁ésti** (custom edit, not in `meter_report.py`): the clause becomes `"type": "nominal"`, a verbless nominal sentence.
  - The English keeps "is", because English needs the copula and the engine never adds one (brief).
  - Used in 0018, 0024, 0033, 0036, 0038, 0043, 0044, 0068 and 0027 (L2).
- **add vocative** (custom: the tool only proposes vocatives already in the plan), each added to the English:
  - 0111 h₂éwsos "Dawn";
  - 0120 déywe "O god";
  - 0158 h₂épos "Limb".
- **add epithet**, each added to the English:
  - 0027 deḱsiwós "rightful" (×2);
  - 0062 dʰubʰnós "deep" (spring) and kr̥snós "black" (sparrow);
  - 0072 albʰós "white" (shine) and h₁rudʰrós "red" (team; cf. Vedic Uṣas's red cows);
  - 0075 lewkós "bright" (god).
- **drop vocative / possessor / numeral**, each removed from the English:
  - 0013 "Mother";
  - 0040 "O Waters";
  - 0065 "four".
- **rewrite (0005):** "The dawn is the daughter of the sky. She is bright." became one nominal clause, h₂éwsōs diwés dʰugh₂tḗr lewkéh₂-kʷe ("Now the dawn is the daughter of the sky, and bright"), with a coordinated predicate. It keeps the formula.
- **Partial fixes (split; one half exact):** 0014, 0067, 0077, 0100, 0101, 0181. The other half is listed under Not fixed.

## Changed lines (155 plans)

Syllable counts are per verse line (sentence), before → after.

| plan | genre | old PIE / English | syl | new PIE / English | syl | edit |
|---|---|---|---|---|---|---|
| b003-0003 | hymn | sóh₂wl̥ dʰéǵʰōm lowkéyeti lówksneh₂-kʷe kʷsépm̥ lowkéyeti.<br>The sun lights up the earth, and the moon lights up the night. | 17 | sóh₂wl̥ dʰéǵʰōm lowkéyeti. lówksneh₂ kʷsépm̥ lowkéyeti.<br>The sun lights up the earth. The moon lights up the night. | 8/8 | split; drop -kʷe |
| b003-0006 | hymn | stonh₂éyet n̥bʰrós-kʷe h₂wérst.<br>It thundered, and the rain-cloud rained. | 7 | nu stonh₂éyet n̥bʰrós-kʷe h₂wérst.<br>Then it thundered, and the rain-cloud rained. | 8 | add nu (c0) |
| b003-0007 | hymn | déh₂nu wódr̥ bʰéreti tód-kʷe píph₃omes.<br>The river carries water, and we drink it. | 12 | déh₂nu wódr̥ bʰéreti tód píph₃omes.<br>The river carries water; we drink it. | 11 | drop -kʷe |
| b003-0008 | hymn | h₂stḗr kʷsépi bʰeh₂nós h₁ésti tóm-kʷe spéḱyomes.<br>The star is shiny in the night, and we look at it. | 12 | h₂stḗr kʷsépi bʰeh₂nós h₁ésti tóm spéḱyomes.<br>The star is shiny in the night; we look at it. | 11 | drop -kʷe |
| b003-0009 | hymn | tósmey kéh₂nmn̥ gʷéHyomes só-kʷe h₂ḱh₂owsyéti.<br>We sing a song to him, and he hears well. | 12 | tósmey kéh₂nmn̥ gʷéHyomes só h₂ḱh₂owsyéti.<br>We sing a song to him; he hears well. | 11 | drop -kʷe |
| b003-0010 | hymn | h₂éwsosm̥ h₁érkʷōmes. ḱluyéh₁t nos séh₂.<br>Let us praise the dawn! May she hear us! | 6/4 | h₂éwsosm̥ h₁érkʷōmes ḱluyéh₁t-kʷe nos séh₂.<br>Let us praise the dawn, and may she hear us! | 11 | merge; add -kʷe |
| b003-0011 | hymn | péh₂wr̥ deywós h₁ésti. tód nos ǵn̥néh₃ti.<br>Fire is a god. It knows us. | 6/5 | péh₂wr̥ deywós h₁ésti tód nos ǵn̥néh₃ti.<br>Fire is a god; it knows us. | 11 | merge |
| b003-0012 | hymn | dʰéǵʰōm gʷṓs h₂életi séh₂-kʷe nos bʰéreti.<br>The earth nourishes the cattle, and she carries us. | 12 | dʰéǵʰōm gʷṓs h₂életi séh₂ nos bʰéreti.<br>The earth nourishes the cattle; she carries us. | 11 | drop -kʷe |
| b003-0013 | hymn | méh₂ter te h₁érkʷomes. h₂éwgmn̥ nos dedh₃dʰí.<br>Mother, we praise you! Give us strength! | 6/6 | h₁érkʷomes te h₂éwgmn̥-kʷe nos dedh₃dʰí.<br>We praise you, and give us strength! | 11 | merge; drop vocative meh2texr; add -kʷe |
| b003-0015 | hymn | sóh₂wl̥ nigʷtéh₂m sékʷetor séh₂-kʷe gʷm̥sḱéti.<br>The sun follows the washed one, and she is walking. | 12 | sóh₂wl̥ nigʷtéh₂m sékʷetor séh₂ gʷm̥sḱéti.<br>The sun follows the washed one; she is walking. | 11 | drop -kʷe |
| b003-0016 | hymn | kʷséps léytt h₁ludʰét-kʷe nigʷtéh₂.<br>The night went away, and the washed one arrived. | 7 | nu kʷséps léytt h₁ludʰét-kʷe nigʷtéh₂.<br>Then the night went away, and the washed one arrived. | 8 | add nu (c0) |
| b003-0017 | hymn | n̥bʰrós stonh₂éyeti dedwimé-kʷe.<br>The cloud is thundering, and we are afraid. | 10 | nu n̥bʰrós stonh₂éyeti dedwimé-kʷe.<br>Now the cloud is thundering, and we are afraid. | 11 | add nu (c0) |
| b003-0018 | hymn | dʰéh₁ses déh₃tores h₁sénti tóy-kʷe nos widéh₁yonti.<br>The gods are givers, and they see us. | 14 | dʰéh₁ses déh₃tores tóy nos widéh₁yonti.<br>The gods are givers; they see us. | 11 | drop copula h₁ésti (nominal clause); drop -kʷe |
| b003-0020 | hymn | dʰéǵʰōm tréset gʷówes-kʷe tr̥mént.<br>The earth trembled in fear, and the cattle were trembling. | 9 | dʰéǵʰōm tréset gʷówes tr̥mént.<br>The earth trembled in fear; the cattle were trembling. | 8 | drop -kʷe |
| b003-0021 | hymn | spḗr kʷsépi trémti só-kʷe dedwóye.<br>The sparrow is trembling in the night, and it is afraid. | 10 | nu spḗr kʷsépi trémti só-kʷe dedwóye.<br>Now the sparrow is trembling in the night, and it is afraid. | 11 | add nu (c0) |
| b003-0022 | hymn | só sédt stéwtōr-kʷe kéh₂nmn̥ gʷéHyet.<br>He sat down, and the praiser sang a song. | 9 | só sédt stéwtōr kéh₂nmn̥ gʷéHyet.<br>He sat down; the praiser sang a song. | 8 | drop -kʷe |
| b003-0023 | hymn | dʰéh₁s wédni stestóh₂e só-kʷe nos spéḱyeti.<br>The god stands in the water, and he looks at us. | 12 | dʰéh₁s wédni stestóh₂e só nos spéḱyeti.<br>The god stands in the water; he looks at us. | 11 | drop -kʷe |
| b003-0025 | hymn | h₁n̥gʷnís h₂éǵrom gʷr̥h₃éti. mē nos gʷr̥h₃és.<br>The fire devours the field. Do not devour us! | 7/4 | h₁n̥gʷnís h₂éǵrom gʷr̥h₃éti mē nos gʷr̥h₃és.<br>The fire devours the field; do not devour us! | 11 | merge |
| b003-0026 | hymn | stéwtor kéh₂nmn̥ gʷéHye. dʰéh₁s tód ḱléwtu.<br>Praiser, sing the song! Let the god hear it! | 6/4 | stéwtor kéh₂nmn̥ gʷéHye dʰéh₁s-kʷe tód ḱléwtu.<br>Praiser, sing the song, and let the god hear it! | 11 | merge; add -kʷe |
| b003-0027 | hymn | kʷís déh₃tōr h₁ésti? deywós déh₃tōr h₁ésti.<br>Who is the giver? The god is the giver. | 5/6 | kʷís deḱsiwós déh₃tōr h₁ésti? deywós-ge deḱsiwós déh₃tōr.<br>Who is the rightful giver? The god indeed is the rightful giver. | 8/8 | add epithet dekjsiwos; add epithet dekjsiwos; drop copula h₁ésti (nominal clause); add -ge (c1) |
| b003-0028 | hymn | péh₂wr̥ dʰégʷʰeti wédos-kʷe h₁wersóm h₁ésti.<br>Fire burns, and the water is wet. | 12 | péh₂wr̥ dʰégʷʰeti wédos h₁wersóm h₁ésti.<br>Fire burns; the water is wet. | 11 | drop -kʷe |
| b003-0029 | hymn | h₁n̥gʷním h₁érkʷōmes moldʰéyōmes-kʷe.<br>Let us praise Fire, and let us pray! | 10 | nu h₁n̥gʷním h₁érkʷōmes moldʰéyōmes-kʷe.<br>Now let us praise Fire, and let us pray! | 11 | add nu (c0) |
| b003-0030 | hymn | só h₂stérn̥s dyéwi dʰéh₁t lówksneh₂m-kʷe kʷsépi dʰéh₁t.<br>He set the stars in the sky and the moon in the night. | 12 | só h₂stérn̥s dyéwi dʰéh₁t lówksneh₂m kʷsépi dʰéh₁t.<br>He set the stars in the sky; he set the moon in the night. | 11 | drop -kʷe |
| b003-0032 | hymn | só stéwtorm̥ dedórḱe só-kʷe tóm wóyde.<br>He has seen the praiser, and he knows him. | 12 | só stéwtorm̥ dedórḱe só tóm wóyde.<br>He has seen the praiser; he knows him. | 11 | drop -kʷe |
| b003-0033 | hymn | dyéwmn̥ albʰóm h₁ésti léwkos-kʷe h₁rudʰróm h₁ésti.<br>The splendor is white, and the light is red. | 13 | dyéwmn̥ albʰóm léwkos-kʷe h₁rudʰróm h₁ésti.<br>The splendor is white, and the light is red. | 11 | drop copula h₁ésti (nominal clause) |
| b003-0035 | hymn | ph₂ter ḱléwse. kh₂nómes toy.<br>Father, listen! We are singing to you. | 4/4 | ph₂ter ḱléwse kh₂nómes toy.<br>Father, listen; we are singing to you. | 8 | merge |
| b003-0036 | hymn | só déh₃tōr h₁ésti tósmey-kʷe médʰu dedh₃més.<br>He is a giver, and we are giving him honey. | 13 | só déh₃tōr tósmey-kʷe médʰu dedh₃més.<br>He is a giver, and we are giving him honey. | 11 | drop copula h₁ésti (nominal clause) |
| b003-0037 | hymn | h₂ékʷeh₂es dʰubʰnéh₂es h₁sénti téh₂es-kʷe lowkóm bʰoréyonti.<br>The waters are deep, and they carry the light. | 17 | h₂ékʷeh₂es dʰubʰnéh₂es h₁sénti. téh₂es lowkóm bʰoréyonti.<br>The waters are deep. They carry the light. | 8/8 | split; drop -kʷe |
| b003-0038 | hymn | lówksneh₂ albʰéh₂ h₁ésti h₂stéres-kʷe bʰeh₂nṓs h₁sénti.<br>The moon is white, and the stars are shiny. | 13 | lówksneh₂ albʰéh₂ h₂stéres-kʷe bʰeh₂nṓs h₁sénti.<br>The moon is white, and the stars are shiny. | 11 | drop copula h₁ésti (nominal clause) |
| b003-0039 | hymn | só h₃rēǵéy h₁éḱwom déh₃t h₃rḗǵs-kʷe méwdt.<br>He gave a horse to the king, and the king became joyful. | 9 | só h₃rēǵéy h₁éḱwom déh₃t h₃rḗǵs méwdt.<br>He gave a horse to the king; the king became joyful. | 8 | drop -kʷe |
| b003-0040 | hymn | h₂ékʷeh₂es h₂ówins h₂élete h₂léksete-kʷe nos.<br>O Waters, you nourish the sheep, and you protect us. | 13 | nu h₂ówins h₂élete h₂léksete-kʷe nos.<br>Now you nourish the sheep, and you protect us. | 11 | drop vocative h2ekweh2; add nu (c0) |
| b003-0041 | hymn | h₂ékʷeh₂es méh₂teres h₁sté. h₁opéyete nos médʰu.<br>O Waters, you are mothers. Give us honey! | 7/7 | nu h₂ékʷeh₂es méh₂teres h₁sté. h₁opéyete-kʷe nos médʰu.<br>Now, O Waters, you are mothers. And give us honey! | 8/8 | add -kʷe; add nu (c0) |
| b003-0043 | hymn | péh₂wr̥ h₂ékʷeh₂ōm bʰréh₂tēr h₁ésti tód-kʷe lewkóm h₁ésti.<br>Fire is the brother of the waters, and it is bright. | 15 | péh₂wr̥ h₂ékʷeh₂ōm bʰréh₂tēr tód-kʷe lewkóm.<br>Fire is the brother of the waters, and it is bright. | 11 | drop copula h₁ésti (nominal clause); drop copula h₁ésti (nominal clause) |
| b003-0044 | hymn | dyḗws deywṓm ph₂tḗr h₁ésti só-kʷe nos dedórḱe.<br>Sky is the father of the gods, and he has seen us. | 13 | dyḗws deywṓm ph₂tḗr só-kʷe nos dedórḱe.<br>Sky is the father of the gods, and he has seen us. | 11 | drop copula h₁ésti (nominal clause) |
| b003-0046 | hymn | tósmey kh₂nṓmes méwdomes-kʷe.<br>Let us sing to him, and let us become joyful! | 9 | tósmey kh₂nṓmes méwdomes.<br>Let us sing to him; let us become joyful! | 8 | drop -kʷe |
| b003-0047 | hymn | tósmey médʰu h₁opéyōmes h₁édomes-kʷe.<br>Let us give honey to him, and let us eat! | 12 | tósmey médʰu h₁opéyōmes h₁édomes.<br>Let us give honey to him; let us eat! | 11 | drop -kʷe |
| b003-0048 | hymn | lówksneh₂m spéḱyōmes. séh₂ lukyéh₁t.<br>Let us look at the moon! May she become bright! | 5/3 | lówksneh₂m spéḱyōmes séh₂ lukyéh₁t.<br>Let us look at the moon; may she become bright! | 8 | merge |
| b003-0049 | hymn | h₂éwsosm̥ h₁éyomes. h₂wisyéh₁t nos séh₂.<br>Let us go to the dawn! May she hear us! | 6/4 | h₂éwsosm̥ h₁éyomes h₂wisyéh₁t-kʷe nos séh₂.<br>Let us go to the dawn, and may she hear us! | 11 | merge; add -kʷe |
| b003-0050 | hymn | stéwtōr h₂usési bʰéwdʰt só-kʷe kh₂nét.<br>The praiser woke up at dawn, and he sang. | 10 | nu stéwtōr h₂usési bʰéwdʰt só-kʷe kh₂nét.<br>Then the praiser woke up at dawn, and he sang. | 11 | add nu (c0) |
| b003-0051 | hymn | h₁ń̥gʷney h₂ówins h₂léksesi wédʰesi-kʷe nos.<br>Fire, you protect the sheep, and you lead us. | 12 | h₁ń̥gʷney h₂ówins h₂léksesi wédʰesi nos.<br>Fire, you protect the sheep; you lead us. | 11 | drop -kʷe |
| b003-0052 | hymn | h₁n̥gʷnís wédos gʷʰr̥néwti tód-kʷe pékʷomes.<br>Fire heats the water, and we cook it. | 12 | h₁n̥gʷnís wédos gʷʰr̥néwti tód pékʷomes.<br>Fire heats the water; we cook it. | 11 | drop -kʷe |
| b003-0053 | hymn | bʰh₂més só-kʷe ḱl̥néwti.<br>We speak, and he listens. | 7 | nu bʰh₂més só-kʷe ḱl̥néwti.<br>Now we speak, and he listens. | 8 | add nu (c0) |
| b003-0055 | hymn | sóh₂wl̥ sth₂dʰí lukdʰí-kʷe.<br>Sun, stand up, and become bright! | 7 | nu sóh₂wl̥ sth₂dʰí lukdʰí-kʷe.<br>Sun, now stand up, and become bright! | 8 | add nu (c0) |
| b003-0056 | hymn | Hwr̥dʰdʰí h₁ń̥gʷney dʰégʷʰe-kʷe.<br>Fire, become strong, and burn! | 7 | nu Hwr̥dʰdʰí h₁ń̥gʷney dʰégʷʰe-kʷe.<br>Fire, now become strong, and burn! | 8 | add nu (c0) |
| b003-0057 | hymn | álbʰōs médʰu ph₃té mudté-kʷe.<br>White ones, drink the honey, and become joyful! | 9 | álbʰōs médʰu ph₃té mudté.<br>White ones, drink the honey; become joyful! | 8 | drop -kʷe |
| b003-0058 | hymn | widé nos bʰéh₂na ḱludʰí-kʷe nos.<br>Shiny one, see us, and hear us! | 9 | widé nos bʰéh₂na ḱludʰí nos.<br>Shiny one, see us; hear us! | 8 | drop -kʷe |
| b003-0059 | hymn | álbʰa h₂éǵrom gʷh₂dʰí h₁ddʰí-kʷe.<br>White one, go to the field, and eat! | 8 | álbʰa h₂éǵrom gʷh₂dʰí h₁ddʰí.<br>White one, go to the field; eat! | 7 | drop -kʷe |
| b003-0060 | hymn | l̥h₂pdʰí lówksna. ǵn̥h₃ih₁mé te.<br>Moon, shine! May we know you! | 4/4 | l̥h₂pdʰí lówksna ǵn̥h₃ih₁mé te.<br>Moon, shine; may we know you! | 8 | merge |
| b003-0061 | hymn | dʰéh₁ses ne dedwiyḗr. tóy gʷegʷmḗr.<br>The gods are not afraid. They are standing steady. | 6/3 | nu dʰéh₁ses ne dedwiyḗr tóy-kʷe gʷegʷmḗr.<br>Now the gods are not afraid, and they are standing steady. | 11 | merge; add -kʷe; add nu (c0) |
| b003-0062 | hymn | bʰréh₁wr̥ bʰeh₂nóm wédos wéǵʰeti spḗr-kʷe tód píph₃eti.<br>The spring carries the shiny water, and the sparrow drinks it. | 15 | dʰubʰnóm bʰréh₁wr̥ bʰeh₂nóm wédos wéǵʰeti. kr̥snós-kʷe spḗr tód píph₃eti.<br>The deep spring carries the shiny water. And the black sparrow drinks it. | 11/8 | split; add epithet dhubhnos; add epithet krsnos |
| b003-0063 | hymn | lowkós h₂ékʷeh₂s h₁nédʰt léwkt-kʷe.<br>The light came forth from the water, and it became bright. | 7 | nu lowkós h₂ékʷeh₂s h₁nédʰt léwkt-kʷe.<br>Then the light came forth from the water, and it became bright. | 8 | add nu (c0) |
| b003-0064 | hymn | bʰuHyéh₁t léwkos. tód kʷḱih₁mé.<br>May there be light! And may we see it! | 4/3 | bʰuHyéh₁t léwkos tód-kʷe kʷḱih₁mé.<br>May there be light, and may we see it! | 8 | merge; add -kʷe |
| b003-0065 | hymn | kʷetwóres h₁éḱwōs sóh₂wl̥ bʰéronti tóy-kʷe bʰéwdʰonti.<br>The four horses carry the sun, and they are awake. | 15 | h₁éḱwōs sóh₂wl̥ bʰéronti tóy bʰéwdʰonti.<br>The horses carry the sun; they are awake. | 11 | drop epithet closed:numerals/4; drop -kʷe |
| b003-0068 | hymn | ph₂wéns ǵʰleymós lewkós h₁ésti tód-kʷe dʰégʷʰeti.<br>The shine of the fire is bright, and it burns. | 13 | ph₂wéns ǵʰleymós lewkós tód-kʷe dʰégʷʰeti.<br>The shine of the fire is bright, and it burns. | 11 | drop copula h₁ésti (nominal clause) |
| b003-0069 | hymn | dyéwmn̥ wédni h₂wékst bʰwéh₂t-kʷe.<br>Splendor grew up in the water, and it grew. | 7 | nu dyéwmn̥ wédni h₂wékst bʰwéh₂t-kʷe.<br>Then splendor grew up in the water, and it grew. | 8 | add nu (c0) |
| b003-0070 | hymn | kŕ̥sna bʰéwdʰesi. widéh₁yomes te.<br>Black one, you are awake. We see you. | 5/5 | kŕ̥sna bʰéwdʰesi widéh₁yomes-kʷe te.<br>Black one, you are awake, and we see you. | 11 | merge; add -kʷe |
| b003-0072 | hymn | séh₂ h₂éǵrom ǵʰleymóh₁ woséyeti yéwgos-kʷe h₂éǵeti.<br>She clothes the field with shine, and she drives the team. | 15 | séh₂ h₂éǵrom albʰóh₁ ǵʰleymóh₁ woséyeti. h₁rudʰróm-kʷe yéwgos h₂éǵeti.<br>She clothes the field with white shine. And she drives the red team. | 11/8 | split; add epithet albhos; add epithet h1rudhros |
| b003-0074 | hymn | wéydtōr kéh₂nmn̥ gʷéHyeti h₃rḗǵs-kʷe ḱl̥néwti.<br>The knower sings the song, and the king listens. | 12 | wéydtōr kéh₂nmn̥ gʷéHyeti h₃rḗǵs ḱl̥néwti.<br>The knower sings the song; the king listens. | 11 | drop -kʷe |
| b003-0075 | hymn | deywós h₃réǵm̥ wóyde só-kʷe tósmey médʰu h₁opéyeti.<br>The god knows the king, and he gives him honey. | 16 | lewkós deywós h₃réǵm̥ wóyde. nu-kʷe só tósmey médʰu h₁opéyeti.<br>The bright god knows the king. And now he gives him honey. | 8/11 | split; add epithet lewkos; add nu (c1) |
| b003-0077 | hymn | déh₂n̥wih₁ wódr̥ bʰéretes tóy-kʷe pléh₁dʰetes.<br>The two rivers carry water, and they swell. | 13 | déh₂n̥wih₁ wódr̥ bʰéretes. tóy-kʷe pléh₁dʰetes.<br>The two rivers carry water. And they swell. | 8/5 | split |
| b003-0078 | hymn | h₂érh₃yōmes h₂éǵrom wr̥ǵyṓmes-kʷe.<br>Let us plough the field, and let us work! | 10 | nu h₂érh₃yōmes h₂éǵrom wr̥ǵyṓmes-kʷe.<br>Now let us plough the field, and let us work! | 11 | add nu (c0) |
| b003-0079 | hymn | só nos sh₂éytlom déh₃t tóm-kʷe h₁érkʷomes.<br>He gave us a lifetime, and we praise him. | 10 | nu nos só sh₂éytlom déh₃t tóm-kʷe h₁érkʷomes.<br>Then he gave us a lifetime, and we praise him. | 11 | add nu (c0) |
| b003-0080 | hymn | méwdomes. léwkt lowkós.<br>Let us rejoice! The light became bright. | 3/3 | nu méwdomes léwkt-kʷe lowkós.<br>Now let us rejoice, and the light became bright. | 8 | merge; add -kʷe; add nu (c0) |
| b003-0082 | prayer | h₂éwgmn̥ nos duh₃dʰí bʰuh₂ih₁mé-kʷe.<br>Give us strength, and may we grow! | 9 | h₂éwgmn̥ nos duh₃dʰí bʰuh₂ih₁mé.<br>Give us strength; may we grow! | 8 | drop -kʷe |
| b003-0083 | prayer | dedh₃dʰí nos sh₂éytlom gʷíh₃woyh₁me-kʷe.<br>Give us a lifetime, and may we live! | 10 | nu nos dedh₃dʰí sh₂éytlom gʷíh₃woyh₁me-kʷe.<br>Now give us a lifetime, and may we live! | 11 | add nu (c0) |
| b003-0085 | prayer | ph₂sdʰí nos tr̥pih₁mé-kʷe.<br>Protect us, and may we be satisfied! | 7 | nu nos ph₂sdʰí tr̥pih₁mé-kʷe.<br>Now protect us, and may we be satisfied! | 8 | add nu (c0) |
| b003-0086 | prayer | n̥bʰrós h₂wr̥syéh₁t déh₂nu-kʷe pl̥h₁yéh₁t.<br>May the rain-cloud rain, and may the river become full! | 9 | n̥bʰrós h₂wr̥syéh₁t déh₂nu pl̥h₁yéh₁t.<br>May the rain-cloud rain; may the river become full! | 8 | drop -kʷe |
| b003-0087 | prayer | h₂éwsōs nos h₂usyéh₁t widóyh₁me-kʷe tā́m.<br>May the dawn become bright for us, and may we see her! | 10 | nu nos h₂éwsōs h₂usyéh₁t widóyh₁me-kʷe tā́m.<br>Now may the dawn become bright for us, and may we see her! | 11 | add nu (c0) |
| b003-0088 | prayer | dʰéh₁ses nos h₂wisté h₂léksete-kʷe nos.<br>Gods, hear us, and protect us! | 10 | nu nos dʰéh₁ses h₂wisté h₂léksete-kʷe nos.<br>Gods, now hear us, and protect us! | 11 | add nu (c0) |
| b003-0090 | prayer | mē nos gʷʰéns. h₂éwgmn̥ nos h₁áydʰi.<br>Do not strike us down! Give us strength! | 3/5 | mē nos gʷʰéns h₂éwgmn̥ nos h₁áydʰi.<br>Do not strike us down; give us strength! | 8 | merge |
| b003-0091 | prayer | mē tr̥syóyh₁me ph₃ih₁mé-kʷe wédos.<br>May we not be thirsty, and may we drink the water! | 9 | mē tr̥syóyh₁me ph₃ih₁mé wédos.<br>May we not be thirsty; may we drink the water! | 8 | drop -kʷe |
| b003-0092 | prayer | ph₂ter nos wédʰe spéḱye-kʷe nos.<br>Father, lead us, and look at us! | 9 | ph₂ter nos wédʰe spéḱye nos.<br>Father, lead us; look at us! | 8 | drop -kʷe |
| b003-0093 | prayer | h₁r̥sḱé nos h₂ḱh₂owsyé-kʷe nos.<br>Come to us, and hear us well! | 7 | nu nos h₁r̥sḱé h₂ḱh₂owsyé-kʷe nos.<br>Now come to us, and hear us well! | 8 | add nu (c0) |
| b003-0094 | prayer | Hwérdʰomes h₂éḱh₃omes-kʷe.<br>Let us become strong, and let us eat! | 7 | nu Hwérdʰomes h₂éḱh₃omes-kʷe.<br>Now let us become strong, and let us eat! | 8 | add nu (c0) |
| b003-0095 | prayer | tóybʰos bʰéh₂omes. ǵn̥h₃ih₁ént nos tóy.<br>Let us speak to them! May they know us! | 5/5 | tóybʰos bʰéh₂omes ǵn̥h₃ih₁ént-kʷe nos tóy.<br>Let us speak to them, and may they know us! | 11 | merge; add -kʷe |
| b003-0097 | prayer | sóh₂wl̥ widóyh₁me gʷíh₃woyh₁me-kʷe.<br>May we see the sun, and may we live! | 9 | sóh₂wl̥ widóyh₁me gʷíh₃woyh₁me.<br>May we see the sun; may we live! | 8 | drop -kʷe |
| b003-0099 | prayer | deḱsiwóm nos dh₃dʰí tód-kʷe h₂réydʰe.<br>Give us what is right, and arrange it! | 10 | nu nos deḱsiwóm dh₃dʰí tód-kʷe h₂réydʰe.<br>Now give us what is right, and arrange it! | 11 | add nu (c0) |
| b003-0102 | prayer | mélit suh₂dyéh₁t péh₃omes-kʷe tód.<br>May the honey become tasty, and let us drink it! | 9 | mélit suh₂dyéh₁t péh₃omes tód.<br>May the honey become tasty; let us drink it! | 8 | drop -kʷe |
| b003-0103 | prayer | wr̥ǵyṓmes mélit-kʷe h₁édomes.<br>Let us work, and let us eat the honey! | 9 | wr̥ǵyṓmes mélit h₁édomes.<br>Let us work; let us eat the honey! | 8 | drop -kʷe |
| b003-0104 | prayer | h₃rḗǵs wĺ̥kʷom tr̥h₂uyéh₁t Hwr̥dʰyéh₁t-kʷe.<br>May the king overcome the wolf, and may he be strong! | 9 | h₃rḗǵs wĺ̥kʷom tr̥h₂uyéh₁t Hwr̥dʰyéh₁t.<br>May the king overcome the wolf; may he be strong! | 8 | drop -kʷe |
| b003-0107 | prayer | wédos gʷʰr̥yéh₁t tód-kʷe píph₃ōmes.<br>May the water become warm, and let us drink it! | 9 | wédos gʷʰr̥yéh₁t tód píph₃ōmes.<br>May the water become warm; let us drink it! | 8 | drop -kʷe |
| b003-0108 | prayer | wódr̥ mē tr̥syéh₁t srobʰéyōmes-kʷe.<br>May the water not dry up, and let us sip! | 10 | nu wódr̥ mē tr̥syéh₁t srobʰéyōmes-kʷe.<br>Now may the water not dry up, and let us sip! | 11 | add nu (c0) |
| b003-0109 | prayer | déh₂newi snéh₂omes térpomes-kʷe.<br>Let us swim in the river, and let us become sated! | 10 | nu déh₂newi snéh₂omes térpomes-kʷe.<br>Now let us swim in the river, and let us become sated! | 11 | add nu (c0) |
| b003-0110 | prayer | mē bʰéyh₂s mē-kʷe tréses.<br>Do not be afraid, and do not tremble! | 6 | nu mē bʰéyh₂s nu-kʷe mē tréses.<br>Now do not be afraid, and now do not tremble! | 8 | add nu (c0); add nu (c1) |
| b003-0112 | prayer | sddʰí píph₃e-kʷe mélit.<br>Sit down, and drink the honey! | 6 | nu sddʰí nu-kʷe píph₃e mélit.<br>Now sit down, and now drink the honey! | 8 | add nu (c0); add nu (c1) |
| b003-0113 | prayer | tósmey moldʰéyōmes. só nos h₂wisyéh₁t.<br>Let us pray to him! May he hear us! | 6/4 | tósmey moldʰéyōmes só-kʷe nos h₂wisyéh₁t.<br>Let us pray to him, and may he hear us! | 11 | merge; add -kʷe |
| b003-0114 | prayer | léwkos gʷʰodʰéyōmes. dh₃yéh₁t só tód.<br>Let us ask for light! May he give it! | 6/4 | léwkos gʷʰodʰéyōmes dh₃yéh₁t-kʷe só tód.<br>Let us ask for light, and may he give it! | 11 | merge; add -kʷe |
| b003-0115 | prayer | tósmey moysóm h₁yáǵyōmes. só tr̥pyéh₁t.<br>Let us sacrifice a ram to him! May he be satisfied! | 7/3 | tósmey moysóm h₁yáǵyōmes só-kʷe tr̥pyéh₁t.<br>Let us sacrifice a ram to him, and may he be satisfied! | 11 | merge; add -kʷe |
| b003-0116 | prayer | bʰréh₂ter moysóm h₁yáǵye bʰéh₂oh₂-kʷe.<br>Brother, sacrifice the ram, and let me speak! | 9 | bʰréh₂ter moysóm h₁yáǵye bʰéh₂oh₂.<br>Brother, sacrifice the ram; let me speak! | 8 | drop -kʷe |
| b003-0117 | prayer | tl̥nh₂dʰí nos sodéye-kʷe nos.<br>Lift us up, and seat us! | 9 | tl̥nh₂dʰí nos sodéye nos.<br>Lift us up; seat us! | 8 | drop -kʷe |
| b003-0118 | prayer | h₃pusih₁mé h₂uksih₁mé-kʷe.<br>May we become rich, and may we grow! | 7 | nu h₃pusih₁mé h₂uksih₁mé-kʷe.<br>Now may we become rich, and may we grow! | 8 | add nu (c0) |
| b003-0119 | prayer | bʰérǵʰm̥ h₁ludʰṓmes sísdōmes-kʷe.<br>Let us arrive at the fortified height, and let us sit down! | 9 | bʰérǵʰm̥ h₁ludʰṓmes sísdōmes.<br>Let us arrive at the fortified height; let us sit down! | 8 | drop -kʷe |
| b003-0122 | prayer | bʰréh₂ter h₁n̥gʷním dʰh₁dʰí gʷʰéromes-kʷe.<br>Brother, set the fire, and let us become warm! | 10 | nu bʰréh₂ter h₁n̥gʷním dʰh₁dʰí gʷʰéromes-kʷe.<br>Brother, now set the fire, and let us become warm! | 11 | add nu (c0) |
| b003-0123 | prayer | swésor wédos yése píph₃ōmes-kʷe.<br>Sister, boil the water, and let us drink! | 10 | nu swésor wédos yése píph₃ōmes-kʷe.<br>Sister, now boil the water, and let us drink! | 11 | add nu (c0) |
| b003-0126 | prayer | ḱéle nos h₂lékse-kʷe nos.<br>Cover us, and protect us! | 7 | nu nos ḱéle h₂lékse-kʷe nos.<br>Now cover us, and protect us! | 8 | add nu (c0) |
| b003-0127 | prayer | mórǵm̥ h₁éyomes gʷegʷémomes-kʷe.<br>Let us go to the border, and let us stand steady! | 10 | nu mórǵm̥ h₁éyomes gʷegʷémomes-kʷe.<br>Now let us go to the border, and let us stand steady! | 11 | add nu (c0) |
| b003-0128 | prayer | yéwgos yunégomes h₁élh₂omes-kʷe.<br>Let us yoke the team, and let us drive! | 10 | nu yéwgos yunégomes h₁élh₂omes-kʷe.<br>Now let us yoke the team, and let us drive! | 11 | add nu (c0) |
| b003-0129 | prayer | h₂égōr bʰuh₂yéh₁t téh₂-kʷe h₁édih₁me.<br>May the berries grow, and may we eat them! | 9 | h₂égōr bʰuh₂yéh₁t téh₂ h₁édih₁me.<br>May the berries grow; may we eat them! | 8 | drop -kʷe |
| b003-0130 | prayer | yéwHs píph₃ōmes séh₂omes-kʷe.<br>Let us drink the broth, and let us become sated! | 9 | yéwHs píph₃ōmes séh₂omes.<br>Let us drink the broth; let us become sated! | 8 | drop -kʷe |
| b003-0131 | prayer | bʰoh₂góm nos h₁áydʰi wédʰe-kʷe nos.<br>Give us a share, and lead us! | 9 | bʰoh₂góm nos h₁áydʰi wédʰe nos.<br>Give us a share; lead us! | 8 | drop -kʷe |
| b003-0132 | prayer | dʰénwr̥ mē Hrumpih₁tó memgʰih₁mé-kʷe.<br>May the bow not break, and may we be able! | 10 | nu dʰénwr̥ mē Hrumpih₁tó memgʰih₁mé-kʷe.<br>Now may the bow not break, and may we be able! | 11 | add nu (c0) |
| b003-0133 | prayer | h₂ṓws ḱluyéh₁t h₂ḱh₂owsyóyh₁me-kʷe.<br>May the ear listen, and may we hear well! | 7 | nu h₂ṓws ḱluyéh₁t h₂ḱh₂owsyóyh₁me-kʷe.<br>Now may the ear listen, and may we hear well! | 8 | add nu (c0) |
| b003-0134 | prayer | ḱleytéh₂i sísdōmes h₂isḱṓmes-kʷe.<br>Let us sit on the slope, and let us seek! | 10 | nu ḱleytéh₂i sísdōmes h₂isḱṓmes-kʷe.<br>Now let us sit on the slope, and let us seek! | 11 | add nu (c0) |
| b003-0136 | prayer | yéwHs h₂isḱé tód-kʷe bʰoréye.<br>Seek the broth, and carry it! | 9 | yéwHs h₂isḱé tód bʰoréye.<br>Seek the broth; carry it! | 8 | drop -kʷe |
| b003-0137 | prayer | bʰéwdʰe spéḱye-kʷe nos.<br>Be awake, and look at us! | 6 | nu bʰéwdʰe nu-kʷe nos spéḱye.<br>Now be awake, and now look at us! | 8 | add nu (c0); add nu (c1) |
| b003-0138 | prayer | mē léyts h₂wisdʰí-kʷe nos.<br>Do not go away, and hear us! | 6 | nu mē léyts nu-kʷe nos h₂wisdʰí.<br>Now do not go away, and now hear us! | 8 | add nu (c0); add nu (c1) |
| b003-0139 | prayer | tetr̥pih₁mé sh₂ih₁mé-kʷe.<br>May we be satisfied, and may we become sated! | 7 | nu tetr̥pih₁mé sh₂ih₁mé-kʷe.<br>Now may we be satisfied, and may we become sated! | 8 | add nu (c0) |
| b003-0140 | prayer | stéwtor tósmey kéh₂nmn̥ h₂ǵdʰí. só tód ǵn̥h₃yéh₁t.<br>Praiser, say the song to him! May he know it! | 7/4 | stéwtor tósmey kéh₂nmn̥ h₂ǵdʰí só tód ǵn̥h₃yéh₁t.<br>Praiser, say the song to him; may he know it! | 11 | merge |
| b003-0142 | charm | h₂ōwyóm mē lémbʰs. tód sh₁dʰí.<br>Do not seize the egg! Let it go! | 4/3 | h₂ōwyóm mē lémbʰs tód-kʷe sh₁dʰí.<br>Do not seize the egg, and let it go! | 8 | merge; add -kʷe |
| b003-0143 | charm | gʷh₂dʰí bʰór h₂éǵrōd mē-kʷe dʰégʷʰh₂s.<br>Thief, go away from the field, and do not come near! | 9 | gʷh₂dʰí bʰór h₂éǵrōd mē dʰégʷʰh₂s.<br>Thief, go away from the field; do not come near! | 8 | drop -kʷe |
| b003-0144 | charm | bʰór n̥ḱdʰí ḱm̥h₂dʰí-kʷe.<br>Thief, vanish, and become tired! | 6 | nu bʰór n̥ḱdʰí nu-kʷe ḱm̥h₂dʰí.<br>Thief, now vanish, and now become tired! | 8 | add nu (c0); add nu (c1) |
| b003-0145 | charm | h₃slidʰdʰí dʰwḗse ḱéyso-kʷe.<br>Possessed one, slip and go astray, and lie flat! | 7 | nu h₃slidʰdʰí dʰwḗse ḱéyso-kʷe.<br>Possessed one, now slip and go astray, and lie flat! | 8 | add nu (c0) |
| b003-0146 | charm | bʰṓr sn̥gʷyéh₁t tr̥syéh₁t-kʷe.<br>May the thief fall down, and may he become thirsty! | 6 | nu bʰṓr sn̥gʷyéh₁t nu-kʷe tr̥syéh₁t.<br>Now may the thief fall down, and now may he become thirsty! | 8 | add nu (c0); add nu (c1) |
| b003-0147 | charm | ḱm̥h₂dʰí dʰwḗse sn̥gʷdʰí-kʷe.<br>Possessed one, become tired, and sink! | 7 | nu ḱm̥h₂dʰí dʰwḗse sn̥gʷdʰí-kʷe.<br>Possessed one, now become tired, and sink! | 8 | add nu (c0) |
| b003-0149 | charm | bʰéwdʰe ḱwón ḱléwse-kʷe.<br>Dog, be awake, and listen! | 6 | nu bʰéwdʰe ḱwón nu-kʷe ḱléwse.<br>Dog, now be awake, and now listen! | 8 | add nu (c0); add nu (c1) |
| b003-0150 | charm | wĺ̥kʷos lelóykʷe moysós-kʷe légʰt.<br>The wolf is gone, and the ram lay down. | 9 | wĺ̥kʷos lelóykʷe moysós légʰt.<br>The wolf is gone; the ram lay down. | 8 | drop -kʷe |
| b003-0152 | charm | l̥h₁dʰí h₁ólom litdʰí-kʷe.<br>Let go of the awl, and go away! | 7 | nu l̥h₁dʰí h₁ólom litdʰí-kʷe.<br>Now let go of the awl, and go away! | 8 | add nu (c0) |
| b003-0156 | charm | pl̥h₁dʰí yḗkʷr̥ sth₂dʰí-kʷe.<br>Liver, become full, and stand up! | 7 | nu pl̥h₁dʰí yḗkʷr̥ sth₂dʰí-kʷe.<br>Liver, now become full, and stand up! | 8 | add nu (c0) |
| b003-0157 | charm | h₂ṓws h₂ḱh₂owsyé ḱléwse-kʷe.<br>Ear, hear well, and listen! | 6 | nu h₂ṓws h₂ḱh₂owsyé nu-kʷe ḱléwse.<br>Ear, now hear well, and now listen! | 8 | add nu (c0); add nu (c1) |
| b003-0159 | charm | h₂épos sélpesh₁ h₂linéHmi tód-kʷe bʰuh₂yéh₁t.<br>I smear the limb with fat, and may it grow. | 12 | h₂épos sélpesh₁ h₂linéHmi tód bʰuh₂yéh₁t.<br>I smear the limb with fat; may it grow. | 11 | drop -kʷe |
| b003-0160 | charm | ǵʰórneh₂m sélpesh₁ h₂linéHmi séh₂-kʷe sh₂yéh₁t.<br>I smear the gut with fat, and may it become sated. | 12 | ǵʰórneh₂m sélpesh₁ h₂linéHmi séh₂ sh₂yéh₁t.<br>I smear the gut with fat; may it become sated. | 11 | drop -kʷe |
| b003-0161 | charm | h₂ṓws sokʷóh₁ h₂linéHmi h₂wisyéh₁t-kʷe tód.<br>I smear the ear with juice, and may it hear. | 10 | nu h₂ṓws sokʷóh₁ h₂linéHmi h₂wisyéh₁t-kʷe tód.<br>Now I smear the ear with juice, and may it hear. | 11 | add nu (c0) |
| b003-0162 | charm | dʰwḗse yékʷn̥s ǵʰidʰí mē-kʷe gʷm̥yés.<br>Possessed one, go away from the liver, and do not come! | 10 | nu dʰwḗse yékʷn̥s ǵʰidʰí mē-kʷe gʷm̥yés.<br>Possessed one, now go away from the liver, and do not come! | 11 | add nu (c0) |
| b003-0163 | charm | dʰwḗsos n̥ḱyéh₁t pl̥h₁yéh₁t-kʷe yḗkʷr̥.<br>May the possessed one vanish, and may the liver become full! | 9 | dʰwḗsos n̥ḱyéh₁t pl̥h₁yéh₁t yḗkʷr̥.<br>May the possessed one vanish; may the liver become full! | 8 | drop -kʷe |
| b003-0165 | charm | péh₂wr̥ bʰórm̥ h₁éwse n̥ḱyéh₁t-kʷe.<br>Fire, burn the thief, and may he vanish! | 9 | péh₂wr̥ bʰórm̥ h₁éwse n̥ḱyéh₁t.<br>Fire, burn the thief; may he vanish! | 8 | drop -kʷe |
| b003-0166 | charm | déh₂nu mē pléh₁dʰes ḱr̥mh₂dʰí-kʷe.<br>River, do not swell, and become slack! | 9 | déh₂nu mē pléh₁dʰes ḱr̥mh₂dʰí.<br>River, do not swell; become slack! | 8 | drop -kʷe |
| b003-0167 | charm | ń̥bʰre litdʰí lukyéh₁t-kʷe lowkós.<br>Rain-cloud, go away, and may the light become bright! | 9 | ń̥bʰre litdʰí lukyéh₁t lowkós.<br>Rain-cloud, go away; may the light become bright! | 8 | drop -kʷe |
| b003-0168 | charm | wĺ̥kʷos gʷʰnih₁tó sn̥gʷyéh₁t-kʷe.<br>May the wolf be struck down, and may he sink! | 7 | nu wĺ̥kʷos gʷʰnih₁tó sn̥gʷyéh₁t-kʷe.<br>Now may the wolf be struck down, and may he sink! | 8 | add nu (c0) |
| b003-0169 | charm | dʰwḗsos bʰindih₁tó mē-kʷe h₁r̥yéh₁t.<br>May the possessed one burst, and may he not arrive! | 9 | dʰwḗsos bʰindih₁tó mē h₁r̥yéh₁t.<br>May the possessed one burst; may he not arrive! | 8 | drop -kʷe |
| b003-0171 | charm | ḱwón moysóm bʰérǵʰm̥ h₁l̥h₂dʰí ḱéyso-kʷe.<br>Dog, drive the ram to the fortified height, and lie flat! | 10 | nu ḱwón moysóm bʰérǵʰm̥ h₁l̥h₂dʰí ḱéyso-kʷe.<br>Dog, now drive the ram to the fortified height, and lie flat! | 11 | add nu (c0) |
| b003-0172 | charm | spér mē tréms gʷíh₃we-kʷe.<br>Sparrow, do not tremble, and live! | 6 | nu spér mē tréms nu-kʷe gʷíh₃we.<br>Sparrow, now do not tremble, and now live! | 8 | add nu (c0); add nu (c1) |
| b003-0175 | charm | bʰárdʰa bʰuh₂dʰí h₂uksdʰí-kʷe.<br>Beard, grow, and become strong! | 7 | nu bʰárdʰa bʰuh₂dʰí h₂uksdʰí-kʷe.<br>Beard, now grow, and become strong! | 8 | add nu (c0) |
| b003-0177 | charm | h₂épos h₃réǵe tl̥nh₂dʰí-kʷe tód.<br>Straighten the limb, and lift it! | 9 | h₂épos h₃réǵe tl̥nh₂dʰí tód.<br>Straighten the limb; lift it! | 8 | drop -kʷe |
| b003-0178 | charm | h₂épos tn̥nudʰí tód-kʷe stoh₂éye.<br>Stretch the limb, and make it stand! | 10 | nu h₂épos tn̥nudʰí tód-kʷe stoh₂éye.<br>Now stretch the limb, and make it stand! | 11 | add nu (c0) |
| b003-0179 | charm | h₂épos mē h₁rudʰéh₁ih₁t gʷʰr̥yéh₁t-kʷe tód.<br>May the limb not be red, and may it become warm! | 10 | nu h₂épos mē h₁rudʰéh₁ih₁t gʷʰr̥yéh₁t-kʷe tód.<br>Now may the limb not be red, and may it become warm! | 11 | add nu (c0) |
| b003-0180 | charm | yékʷney kh₂nóh₂ tód-kʷe sélpesh₁ h₂linéHmi.<br>I sing to the liver, and I smear it with fat. | 12 | yékʷney kh₂nóh₂ tód sélpesh₁ h₂linéHmi.<br>I sing to the liver; I smear it with fat. | 11 | drop -kʷe |
| b003-0181 | charm | h₁regʷesyéti wĺ̥kʷos-kʷe gʷm̥yéti. ḱwón bʰéwdʰe.<br>It is getting dark, and the wolf comes. Dog, be awake! | 10/3 | nu h₁regʷesyéti wĺ̥kʷos-kʷe gʷm̥yéti. ḱwón bʰéwdʰe.<br>Now it is getting dark, and the wolf comes. Dog, be awake! | 11/3 | add nu (c0) |
| b003-0182 | charm | spḗr gʷíh₃woyh₁t Hwr̥dʰyéh₁t-kʷe.<br>May the sparrow live, and may it grow! | 6 | nu spḗr gʷíh₃woyh₁t nu-kʷe Hwr̥dʰyéh₁t.<br>Now may the sparrow live, and now may it grow! | 8 | add nu (c0); add nu (c1) |
| b003-0183 | charm | bʰuHyóyh₁t h₂ōwyóm Hwr̥dʰyéh₁t-kʷe.<br>May the egg be growing, and may it become strong! | 7 | nu bʰuHyóyh₁t h₂ōwyóm Hwr̥dʰyéh₁t-kʷe.<br>Now may the egg be growing, and may it become strong! | 8 | add nu (c0) |
| b003-0184 | charm | yéwgos stoh₂éye tód-kʷe wédʰe.<br>Make the team stand up, and lead it! | 9 | yéwgos stoh₂éye tód wédʰe.<br>Make the team stand up; lead it! | 8 | drop -kʷe |
| b003-0185 | charm | mē moréyes spérm̥ gʷíh₃wetu-kʷe.<br>Do not kill the sparrow, and let it live! | 10 | nu mē moréyes spérm̥ gʷíh₃wetu-kʷe.<br>Now do not kill the sparrow, and let it live! | 11 | add nu (c0) |
| b003-0186 | charm | bʰudʰménm̥ sn̥gʷdʰí mē-kʷe gʷm̥yés.<br>Sink to the bottom, and do not come! | 9 | bʰudʰménm̥ sn̥gʷdʰí mē gʷm̥yés.<br>Sink to the bottom; do not come! | 8 | drop -kʷe |
| b003-0187 | charm | h₂ḱh₂owsyóyh₁t ḱwṓ bʰudʰyéh₁t-kʷe.<br>May the dog hear well, and may he wake up! | 6 | nu h₂ḱh₂owsyóyh₁t ḱwṓ nu-kʷe bʰudʰyéh₁t.<br>Now may the dog hear well, and now may he wake up! | 8 | add nu (c0); add nu (c1) |
| b003-0188 | charm | dʰwḗsos h₂ōwyóm mē widóyh₁t h₃slidʰyéh₁t-kʷe.<br>May the possessed one not see the egg, and may he go astray! | 10 | nu dʰwḗsos h₂ōwyóm mē widóyh₁t h₃slidʰyéh₁t-kʷe.<br>Now may the possessed one not see the egg, and may he go astray! | 11 | add nu (c0) |
| b003-0189 | charm | sddʰí mŕ̥we mē-kʷe stéh₂s.<br>Dead one, sit down, and do not stand up! | 6 | nu sddʰí mŕ̥we nu-kʷe mē stéh₂s.<br>Dead one, now sit down, and now do not stand up! | 8 | add nu (c0); add nu (c1) |
| b003-0190 | charm | ǵʰórneh₂ mē skérdʰoyh₁t séh₂-kʷe pl̥h₁yéh₁t.<br>May the gut not be pierced, and may it be full! | 9 | ǵʰórneh₂ mē skérdʰoyh₁t séh₂ pl̥h₁yéh₁t.<br>May the gut not be pierced; may it be full! | 8 | drop -kʷe |
| b003-0005 | hymn | h₂éwsōs diwés dʰugh₂tḗr h₁ésti. séh₂ lewkéh₂ h₁ésti.<br>The dawn is the daughter of the sky. She is bright. | 9/5 | nu h₂éwsōs diwés dʰugh₂tḗr lewkéh₂-kʷe.<br>Now the dawn is the daughter of the sky, and bright. | 11 | rewrite: merge into one nominal clause with coordinated predicate (drop séh₂ and both copulas) + nu |
| b003-0014 | hymn | sh₂wéns dʰugh₂tḗr h₁éḱwons h₂éǵeti séh₂-kʷe lewkéh₂ h₁ésti.<br>The daughter of the sun drives the horses, and she is bright. | 16 | nu sh₂wéns dʰugh₂tḗr h₁éḱwons h₂éǵeti. séh₂-kʷe lewkéh₂ h₁ésti.<br>Now the daughter of the sun drives the horses. And she is bright. | 11/6 | split; add nu (c0) |
| b003-0024 | hymn | h₂éwsterom h₁rudʰróm h₁ésti kr̥snéh₂-kʷe linékʷti.<br>The east is red, and the black one is leaving. | 13 | h₂éwsterom h₁rudʰróm kr̥snéh₂-kʷe linékʷti.<br>The east is red, and the black one is leaving. | 11 | drop copula h₁ésti (nominal clause) |
| b003-0067 | hymn | h₃rḗǵs tóybʰos kh₂n̥ménh₁ bʰéh₂ti tóy-kʷe tóm ḱl̥nwénti.<br>The king speaks to them with a song, and they hear him. | 14 | h₃rḗǵs tóybʰos kh₂n̥ménh₁ bʰéh₂ti. tóy-kʷe tóm ḱl̥nwénti.<br>The king speaks to them with a song. And they hear him. | 8/6 | split |
| b003-0100 | prayer | woydéye nos deḱsiwóm ǵn̥néh₃omes-kʷe tód.<br>Show us what is right, and let us know it! | 13 | nu nos woydéye deḱsiwóm. ǵn̥néh₃omes-kʷe tód.<br>Now show us what is right! And let us know it! | 8/6 | split; add nu (c0) |
| b003-0101 | prayer | ph₂tḗr méh₂tēr-kʷe gʷíh₃woyh₁tām tetr̥pih₁ént-kʷe.<br>May the father and the mother live, and may they be satisfied! | 13 | ph₂tḗr méh₂tēr-kʷe gʷíh₃woyh₁tām. tetr̥pih₁ént-kʷe.<br>May the father and the mother live! And may they be satisfied! | 8/5 | split |
| b003-0111 | prayer | bʰudʰdʰí sth₂dʰí-kʷe.<br>Wake up, and stand up! | 5 | nu h₂éwsos bʰudʰdʰí sth₂dʰí-kʷe.<br>Dawn, now wake up, and stand up! | 8 | add vocative h2ewsoxs; add nu (c0) |
| b003-0120 | prayer | h₁ddʰí sh₂dʰí-kʷe.<br>Eat, and become sated! | 4 | nu déywe h₁ddʰí sh₂dʰí-kʷe.<br>O god, now eat, and become sated! | 7 | add vocative deywos; add nu (c0) |
| b003-0158 | charm | mē stéwds. gʷʰr̥dʰí.<br>Do not become cold! Become warm! | 2/2 | nu mē stéwds h₂épos gʷʰr̥dʰí-kʷe.<br>Limb, now do not become cold, and become warm! | 8 | merge; add vocative h2epos; add -kʷe; add nu (c0) |

## Not fixed

These lines are still off target. Every edit type the tool knows was tried, and so were combinations of up to four edits.

The slice adjectives that fit the context are now at the lexeme cap of 7: lewkos, albhos, krsnos and h1rudhros were each at 6 before the repair, and deywos and h2ewsoxs are also at 7. The adjectives still under the cap (udros "aquatic", dwoyos "twofold", swekjstos "sixth", bhosos "barefoot" and the like) would be nonsense epithets, so they were not used.

| plan | line | syl / target | why it is left |
|---|---|---|---|
| b003-0002 | "h₂éwsos diwés dʰúgh₂ter h₂usdʰí." / "h₁érkʷomes te." | 9/8, 4/8 | Unchanged. The only exact repair merges the two sentences and drops one of the vocatives h₂éwsos, diwés or dʰúgh₂ter. That breaks the formula "Dawn, daughter of Sky" (formula_uses fell from 4 to 3 in a trial run, so it was reverted). An epithet on Dawn would need lewkos or albhos, both at the cap. |
| b003-0014 | L2 "séh₂-kʷe lewkéh₂ h₁ésti." | 6/8 | Split from a 16-syllable line; L1 is now exact (11). L2 "And she is bright" has a pronoun subject and an adjective predicate, so there is nothing to hang an epithet on. nu gives 7. |
| b003-0045 | "kʷís gʷṓs h₂éǵeti?" / "h₁rudʰréh₂ gʷṓs h₂éǵeti." | 5/8, 6/8 | Unchanged. A question and its answer: merging them loses the question. Neither line reaches 8 with a particle, and there is no sensible epithet under the cap. |
| b003-0067 | L2 "tóy-kʷe tóm ḱl̥nwénti." | 6/8 | Split from 14; L1 is now exact (8). L2 "and they hear him" has only pronouns and a verb; nu gives 7. |
| b003-0077 | L2 "tóy-kʷe pléh₁dʰetes." | 5/8 | Split from 13; L1 is now exact (8). The tool's exact alternative makes "the two rivers" singular or plural while the second clause keeps a dual verb, a grammatical mismatch, so it was rejected. |
| b003-0100 | L2 "ǵn̥néh₃omes-kʷe tód." | 6/8 | Split from 13; L1 is now exact (8, with nu). L2 is a verb and a pronoun. |
| b003-0101 | L2 "tetr̥pih₁ént-kʷe." | 5/8 | Split from 13; L1 is now exact (8). L2 is a single verb. |
| b003-0105 | "mélit nos sélpos-kʷe h₁opéye gʷr̥h₃ṓmes-kʷe." | 13/11 | Unchanged. Dropping -kʷe gives 12 and a split gives 9+4. There is no possessor, vocative or epithet to drop. |
| b003-0106 | "bʰréh₂term̥ swésorm̥-kʷe h₂lékse ḱéle-kʷe tóns." | 13/11 | Unchanged, for the same reason. 11 would need the object pronoun dropped, but the English "cover them" needs it. |
| b003-0135 | "kʷís nos péh₂seti?" / "ph₂tḗr nos péh₂seti." | 5/8, 6/8 | Unchanged. A question and its answer, as 0045. |
| b003-0181 | L2 "ḱwón bʰéwdʰe." | 3/8 | L1 is now exact (nu, 11). L2 "Dog, be awake!" is 5 short. The tool's exact repair (merge, then drop the vocative "dog") loses the addressee, so it was rejected. |

That is 14 of 206 lines: 0002, 0045 and 0135 have two lines each; the rest one.
