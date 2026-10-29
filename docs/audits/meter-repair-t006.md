# Meter repair: t006

meter_exact before: 0.396 (38/96); after: 1.000 (96/96). Gate: PASS (all gates, `realize_plans.py --model claude-sonnet-5-5 --prompt-id tier3-planner-v4`). Lines changed: 58; every verse line is now 8 or 11 syllables; none left unfixed. No `head`/`dep` indices were disturbed (checked: the only slot insertions at index 0 were in clauses with no head/dep links). Only the listed lines' PIE differ between the old and new corpus (checked by line-by-line comparison of the realized text).


## Notes

- The plan English of t006 plans is not aligned sentence-for-line (PIE sentences with break:true can sit inside one English sentence), so every English edit was a substring replacement.
- t006-0008 L3: `Do not leave us!` became `Do not leave!` (the object pronoun was dropped), the only way found to reach 11 without losing the relative clause; the lead may prefer a different fix.
- t006-0034 L1: `Gods and goddess, hear us!` (singular vocative) is awkward but exact; t006-0002 L1 loses "with a stone".


## Changed lines

| plan | L | old PIE (syl) | old English | new PIE (syl) | new English | edit |
|---|---|---|---|---|---|---|
| t006-0002 | 1 | gʰrómosyo déywe h₁yós h₁ógʷʰim h₂ḱm̥néh₁ kélh₂s (12) | God of thunder, you who struck the serpent with a stone | nu gʰrómosyo déywe h₁yós h₁ógʷʰim kélh₂s (11) | Now, God of thunder, you who struck the serpent | drop slot (pro-drop / omitted modifier) [c0 4]; add particle nu [c0] |
| t006-0002 | 2 | h₁yós wédōr wr̥sméns sélǵs h₁yós gʷṓs spérs (9) | you who released the waters from the height | nu-kʷe h₁yós wédōr wr̥sméns sélǵs h₁yós gʷṓs spérs (11) | and now you who released the waters from the height | add particle nu [c1]; join to previous clause with -kʷe 'and' [c1] |
| t006-0002 | 4 | móri toy pedsú trémti (7) | At your feet the sea trembles | móri-kʷe toy pedsú trémti (8) | And at your feet the sea trembles | join to previous clause with -kʷe 'and' [c4] |
| t006-0002 | 6 | h₂éǵrons nos mē torséyes (7) | Do not make our fields dry | h₂éǵrons-kʷe nos mē torséyes (8) | And do not make our fields dry | join to previous clause with -kʷe 'and' [c6] |
| t006-0002 | 7 | ń̥dʰgʷʰitom toy ḱléwos gʷíh₃weti (9) | Your imperishable fame lives | ń̥dʰgʷʰitom-kʷe-ge toy ḱléwos gʷíh₃weti (11) | And your imperishable fame indeed lives | add particle -ge [c7]; join to previous clause with -kʷe 'and' [c7] |
| t006-0002 | 8 | nu nos n̥bʰrósyo déh₃tor ḱludʰí (9) | Now, giver of rain | n̥bʰrósyo nos déh₃tor ḱludʰí (8) | Giver of rain | drop particle nu [c8] |
| t006-0002 | 9 | gʷṓs nos h₁wésu-kʷe ḱléwos dh₃dʰí (9) | Give us cattle and good fame | nu-kʷe nos gʷṓs h₁wésu-kʷe ḱléwos dh₃dʰí (11) | And now give us cattle and good fame | add particle nu [c9]; join to previous clause with -kʷe 'and' [c9] |
| t006-0006 | 2 | wédōr wr̥sméns pró ih₂yéh₁t h₂égōr pleh₁téh₂ h₁syéh₁t (12) | go forth from the height | wédōr wr̥sméns ih₂yéh₁t h₂égōr pleh₁téh₂ h₁syéh₁t (11) | go from the height | drop adverb [c2 s2] |
| t006-0006 | 3 | gʷówes mē tr̥syóyh₁ent tóy-kʷe mē ḱm̥h₂ih₁ént (12) | , and may they not grow tired | gʷówes mē tr̥syóyh₁ent tóy mē ḱm̥h₂ih₁ént (11) | , may they not grow tired | drop clause conjunction -kʷe [c5] |
| t006-0006 | 6 | sréwmn̥ pleh₁tóm h₁syéh₁t h₂óweyes téh₂ píph₃oyh₁ent (12) | May the sheep drink them | sréwmn̥ pleh₁tóm h₁syéh₁t h₂ówih₁ téh₂ píph₃oyh₁tām (11) | May the two sheep drink them | change number [c10 s0 DU] |
| t006-0008 | 2 | méǵh₂s h₁ési n̥bʰróm nos bʰére (9) | You are great. | nu-kʷe méǵh₂s h₁ési n̥bʰróm nos bʰére (11) | And now you are great. | add particle nu [c1]; join to previous clause with -kʷe 'and' [c1] |
| t006-0008 | 3 | h₁ógʷʰim gʷʰn̥dʰí h₁yós wédōr Hwért mē nos linékʷs (12) | Do not leave us! | h₁ógʷʰim gʷʰn̥dʰí h₁yós wédōr Hwért mē linékʷs (11) | Do not leave! | drop slot (pro-drop / omitted modifier) [c5 0] |
| t006-0008 | 4 | wékʷos moy ḱléwse h₂ówins nos ph₂sdʰí (10) | Protect our sheep! | wékʷos moy ḱléwse h₂ówins-kʷe nos ph₂sdʰí (11) | And protect our sheep! | join to previous clause with -kʷe 'and' [c7] |
| t006-0008 | 5 | wĺ̥kʷos tā́s mē h₁édih₁t gʷówes nos gʷíh₃woyh₁ent (12) | May our cattle live | wĺ̥kʷos tā́s mē h₁édih₁t gʷówes gʷíh₃woyh₁ent (11) | May the cattle live | drop possessor [c9 s1] |
| t006-0008 | 6 | Hrugʰís-kʷe nos sph₁rós h₁syéh₁t (7) | and may our rye be thriving | Hrugʰís-kʷe-ge nos sph₁rós h₁syéh₁t (8) | and may our rye indeed be thriving | add particle -ge [c10] |
| t006-0008 | 7 | nu toy médʰu déh₃omes (7) | Then we shall give you mead. | nu-kʷe toy médʰu déh₃omes (8) | And then we shall give you mead. | join to previous clause with -kʷe 'and' [c11] |
| t006-0010 | 1 | h₂ékʷeh₂es h₁yéh₂es wr̥sméns pró gʷh₂té (10) | Waters, you who went forth from the height | nu h₂ékʷeh₂es h₁yéh₂es wr̥sméns pró gʷh₂té (11) | Now, waters, you who went forth from the height | add particle nu [c0] |
| t006-0010 | 3 | déh₂nuh₂ pl̥nh₁té déh₂n̥wōm méh₂teres h₁sté (12) | the mothers of the rivers | déh₂nuh₂ pl̥nh₁té déh₂n̥wōm méh₂tēr h₁sté (11) | the mother of the rivers | change number [c4 s0 SG] |
| t006-0015 | 1 | dyéw nos ph₂ter ḱludʰí h₁yós n̥bʰróm dédeh₃si (12) | Father Sky, hear us! | nu nos dyéw ḱludʰí h₁yós n̥bʰróm dédeh₃si (11) | Now, Sky, hear us! | add particle nu [c0]; drop vocative [c0 s1] |
| t006-0015 | 3 | dʰéǵʰom nos méh₂ter ḱléwse (7) | Mother Earth, listen to us! | dʰéǵʰom-kʷe nos méh₂ter ḱléwse (8) | And Mother Earth, listen to us! | join to previous clause with -kʷe 'and' [c3] |
| t006-0015 | 5 | h₁wésu nos ḱléwos dh₃dʰí (7) | Give us good fame. | h₁wésu-kʷe nos ḱléwos dh₃dʰí (8) | And give us good fame. | join to previous clause with -kʷe 'and' [c6] |
| t006-0015 | 6 | méh₂ter nos Hrugʰím h₂wĺ̥h₁neh₂m-kʷe duh₃dʰí (10) | Mother, give us rye and wool. | nu nos méh₂ter Hrugʰím h₂wĺ̥h₁neh₂m-kʷe duh₃dʰí (11) | Now, mother, give us rye and wool. | add particle nu [c7] |
| t006-0016 | 5 | méǵh₂s deywós dyḗm tn̥néwt (7) | The great god stretched out the sky | nu méǵh₂s deywós dyḗm tn̥néwt (8) | Then the great god stretched out the sky | add particle nu [c4] |
| t006-0016 | 6 | tā́m-kʷe Hn̥dʰí logʰéyet (7) | and laid her below | nu-kʷe tā́m Hn̥dʰí logʰéyet (8) | and then laid her below | add particle nu [c5] |
| t006-0016 | 7 | téh₂-kʷe móri séh₁t bʰéh₂os-kʷe kʷért (9) | , and made light | téh₂-kʷe móri séh₁t bʰéh₂os kʷért (8) | ; he made light | drop clause conjunction -kʷe [c7] |
| t006-0016 | 8 | kʷósmey deywṓy médʰu déh₃omes (9) | To which god shall we give mead? | nu-kʷe kʷósmey deywṓy médʰu déh₃omes (11) | And now to which god shall we give mead? | add particle nu [c8]; join to previous clause with -kʷe 'and' [c8] |
| t006-0017 | 5 | gʷówes-kʷe h₂éǵrom h₁yénti (7) | and the cattle go to the field | nu-kʷe gʷówes h₂éǵrom h₁yénti (8) | and now the cattle go to the field | add particle nu [c5] |
| t006-0017 | 7 | h₂éboles-kʷe pékʷonti (7) | and the apples ripen | h₂éboles-kʷe-ge pékʷonti (8) | and the apples indeed ripen | add particle -ge [c8] |
| t006-0017 | 8 | nu tóh₁ stóygʰoh₁ h₁éyomes (7) | Let us go by this path. | nu-kʷe tóh₁ stóygʰoh₁ h₁éyomes (8) | And let us go by this path. | join to previous clause with -kʷe 'and' [c9] |
| t006-0019 | 1 | h₂éwsos nos diwés dʰúgh₂ter lukdʰí (10) | Dawn, daughter of Sky, shine for us! | nu nos h₂éwsos diwés dʰúgh₂ter lukdʰí (11) | Now, Dawn, daughter of Sky, shine for us! | add particle nu [c0] |
| t006-0019 | 3 | h₁yéh₂ nos h₂ew bʰowdʰéyesi (7) | you who awaken us again | h₁yéh₂-kʷe nos h₂ew bʰowdʰéyesi (8) | and you who awaken us again | join to previous clause with -kʷe 'and' [c2] |
| t006-0019 | 4 | h₁yéh₂ gʷṓs h₂éǵrom wédʰesi (7) | you who lead the cattle to the field | h₁yéh₂-kʷe gʷṓs h₂éǵrom wédʰesi (8) | and you who lead the cattle to the field | join to previous clause with -kʷe 'and' [c3] |
| t006-0019 | 5 | h₁yéh₂ upér h₂ew h₁rudʰéh₁si (7) | you who are red above again | h₁yéh₂-kʷe upér h₂ew h₁rudʰéh₁si (8) | and you who are red above again | join to previous clause with -kʷe 'and' [c4] |
| t006-0019 | 6 | bʰéh₂os toy h₁wésu h₁ésti (7) | Your light is good. | bʰéh₂os-kʷe toy h₁wésu h₁ésti (8) | And your light is good. | join to previous clause with -kʷe 'and' [c5] |
| t006-0021 | 1 | méh₂ter toy h₂éǵrom h₂érh₃yomes (9) | we plough your field | méh₂ter h₂éǵrom h₂érh₃yomes (8) | we plough the field | drop possessor [c0 s2] |
| t006-0021 | 2 | h₁uséwih₂ nos h₁sdʰí Hrugʰís-kʷe bʰuh₂yéh₁t (10) | Be good to us | h₁uséwih₂-kʷe nos h₁sdʰí Hrugʰís-kʷe bʰuh₂yéh₁t (11) | And be good to us | join to previous clause with -kʷe 'and' [c1] |
| t006-0021 | 3 | séh₁mn̥-kʷe h₂éboles-kʷe bʰuh₂ih₁ént (10) | and the seed and the apples | nu-kʷe séh₁mn̥ h₂éboles-kʷe bʰuh₂ih₁ént (11) | and now the seed and the apples | add particle nu [c3] |
| t006-0021 | 4 | wĺ̥kʷos nos mē gʷm̥yóyh₁t (6) | May the wolf not come to us. | nu-kʷe nos wĺ̥kʷos mē gʷm̥yóyh₁t (8) | And now may the wolf not come to us. | add particle nu [c4]; join to previous clause with -kʷe 'and' [c4] |
| t006-0021 | 6 | méh₂ter toy médʰu dédeh₃omes (9) | We shall give you mead, Mother. | nu-kʷe toy méh₂ter médʰu dédeh₃omes (11) | And now we shall give you mead, Mother. | add particle nu [c7]; join to previous clause with -kʷe 'and' [c7] |
| t006-0025 | 4 | h₂égōr h₂éboln̥s-kʷe pékʷesi (9) | You ripen the berries and the apples. | nu-kʷe h₂égōr h₂éboln̥s-kʷe pékʷesi (11) | And now you ripen the berries and the apples. | add particle nu [c3]; join to previous clause with -kʷe 'and' [c3] |
| t006-0026 | 1 | HéHḱuh₁ nos yémHoh₁ gʷm̥tóm h₁yóh₁ nos mréys spr̥tóm (12) | Swift twins, come to us! | nu nos yémHoh₁ gʷm̥tóm h₁yóh₁ nos mréys spr̥tóm (11) | Now, twins, come to us! | add particle nu [c0]; drop epithet/numeral [c0 s1] |
| t006-0026 | 3 | h₁yóh₁ kʷékʷlom duktés h₁yóh₁ h₁éḱwons dm̥h₂tóm (10) | you who draw the wheel | h₁yóh₁-kʷe kʷékʷlom duktés h₁yóh₁ h₁éḱwons dm̥h₂tóm (11) | and you who draw the wheel | join to previous clause with -kʷe 'and' [c3] |
| t006-0026 | 4 | yémHoh₁ nos ḱlutóm h₁éḱwons nos ph₂stóm (10) | Protect our horses. | yémHoh₁ nos ḱlutóm h₁éḱwons-kʷe nos ph₂stóm (11) | And protect our horses. | join to previous clause with -kʷe 'and' [c6] |
| t006-0026 | 6 | h₁uséwōm nos déh₃torh₁e h₁éḱwons h₁opéyetom (13) | Givers of good things, give us horses! | nu nos déh₃torh₁e h₁éḱwons h₁opéyetom (11) | Now, givers, give us horses! | add particle nu [c8]; drop possessor [c8 s1] |
| t006-0029 | 4 | móri yéseti dyḗws tósyo ph₂tḗr h₁ésti (12) | The sea boils. Sky is his father. | nu móri yéseti dyḗws ph₂tḗr h₁ésti (11) | Now the sea boils. Sky is the father. | add particle nu [c3]; drop possessor [c4 s1] |
| t006-0029 | 5 | HeHḱéwes h₁éḱwōs tóm bʰéronti (9) | Swift horses carry him. | nu-kʷe HeHḱéwes h₁éḱwōs tóm bʰéronti (11) | And now swift horses carry him. | add particle nu [c5]; join to previous clause with -kʷe 'and' [c5] |
| t006-0029 | 6 | só h₁ógʷʰim kélh₂eti wédōr-kʷe térkh₂eti (12) | , and he will let the waters go | só h₁ógʷʰim kélh₂eti wédōr térkh₂eti (11) | ; he will let the waters go | drop clause conjunction -kʷe [c7] |
| t006-0029 | 7 | só nos n̥bʰróm bʰéroyh₁t (6) | May he give us rain! | nu-kʷe nos só n̥bʰróm bʰéroyh₁t (8) | And now may he give us rain! | add particle nu [c8]; join to previous clause with -kʷe 'and' [c8] |
| t006-0031 | 1 | h₁ń̥gʷney h₁yós wédn̥su ǵeǵónh₁th₂e (10) | Agni, you who are born in the waters | nu h₁ń̥gʷney h₁yós wédn̥su ǵeǵónh₁th₂e (11) | Now, Agni, you who are born in the waters | add particle nu [c0] |
| t006-0031 | 2 | h₁yós h₁rudʰéh₁si h₁yós nos ḱóm tḱéysi (9) | you who are red | nu-kʷe h₁yós h₁rudʰéh₁si h₁yós nos ḱóm tḱéysi (11) | and now you who are red | add particle nu [c1]; join to previous clause with -kʷe 'and' [c1] |
| t006-0031 | 3 | wódr̥ gʷʰr̥néwsi mḗms-kʷe pékʷesi (10) | You heat the water | nu wódr̥ gʷʰr̥néwsi mḗms-kʷe pékʷesi (11) | Now you heat the water | add particle nu [c3] |
| t006-0031 | 4 | bʰéh₂os toy témHesi léwkt h₁ń̥gʷney nos ḱóm sddʰí (12) | your light shines | bʰéh₂os témHesi léwkt h₁ń̥gʷney nos ḱóm sddʰí (11) | the light shines | drop possessor [c5 s2] |
| t006-0034 | 1 | déywōs nos déywih₂es-kʷe ḱluté (9) | Gods and goddesses, hear us! | déywōs nos déywih₂-kʷe ḱluté (8) | Gods and goddess, hear us! | change number [c0 s1 SG] |
| t006-0034 | 2 | h₁yóy dyéwi tḱité h₁yóy wr̥smń̥su sédyete (12) | You who dwell in the sky, you who sit | dyéwi tḱité h₁yóy wr̥smń̥su sédyete (11) | You dwell in the sky, you who sit | drop slot (pro-drop / omitted modifier) [c1 0] |
| t006-0034 | 6 | HeHḱúns nos h₁éḱwons duh₃té (7) | Give us swift horses! | HeHḱúns-kʷe nos h₁éḱwons duh₃té (8) | And give us swift horses! | join to previous clause with -kʷe 'and' [c7] |
| t006-0038 | 1 | h₂éḱmon nos péh₂wr̥ dh₃dʰí (7) | Stone, give us fire! | nu nos h₂éḱmon péh₂wr̥ dh₃dʰí (8) | Now, stone, give us fire! | add particle nu [c0] |
| t006-0038 | 2 | tód h₁n̥dóm h₁ésti tósmōd h₁éǵʰs ml̥h₃dʰí (10) | Come out of it! | tód h₁n̥dóm h₁ésti tósmōd-kʷe h₁éǵʰs ml̥h₃dʰí (11) | And come out of it! | join to previous clause with -kʷe 'and' [c2] |
| t006-0038 | 3 | úd dʰégʷʰe gʷʰr̥nudʰí nos (7) | Heat us! | úd dʰégʷʰe gʷʰr̥nudʰí-kʷe nos (8) | And heat us! | join to previous clause with -kʷe 'and' [c4] |
