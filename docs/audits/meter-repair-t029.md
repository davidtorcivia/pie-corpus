# Meter repair: t029

meter_exact before: 0.275 (14/51); after: 1.000 (42/42). Gate PASS (all gates). Lexeme caps respected.

Method: edits found with the `scripts/meter_report.py` machinery (each realized and checked by `check_plan`), applied to `data/generation/plans/t029.jsonl`, English updated to match, re-realized with `--model claude-sonnet-5-5 --prompt-id tier3-planner-v4`. `corpus/` not hand-edited; `pie/` and tools unchanged. Particle edits (nu/-ge) leave the English unchanged except where it carried the particle ("indeed" for -ge, "now/then" for nu): removed when the particle was dropped. A -kʷe added at the start of a sentence appears as "And". Merged/split sentences change only line boundaries.

Head/dep index check: for every changed plan the (slot, head/dep target) links were compared with the original plan; only intended drops/additions differ, none retargeted. No vocative edit was used, so the reported vocative-index bug did not affect this batch. No fixes were needed.
Note: t029 has fewer verse lines afterwards (51 to 42) because short lines were merged into neighbours.

## Changed lines (plan id, edits, old/new PIE of the whole text, old/new English)


### t029-0015
- edits: c0 drop MOD closed:numerals/2; c1 merge (break True->False); c2 particle None->nu; c6 add MOD kjeywos; c6 particle None->nu; c6 conj -kʷe None->kʷe
- old PIE: dwóh₁ h₁éḱwoh₁ yugté. h₂erh₃wóm h₂érh₃yete. h₁éḱwōs yugóm dukté wíHre ḱm̥h₂dʰí. dʰéǵʰōm déretor dʰéǵʰom méh₂ter h₃pusdʰí. misdʰós h₁wésus.
- new PIE: h₁éḱwoh₁ yugté h₂erh₃wóm h₂érh₃yete. nu h₁éḱwōs yugóm dukté wíHre ḱm̥h₂dʰí. dʰéǵʰōm déretor dʰéǵʰom méh₂ter h₃pusdʰí. nu-kʷe ḱéywos misdʰós h₁wésus.
- old English: Yoke the two horses! Plough the arable land! Pull the yoke, horses, toil, man, toil! The earth is split, Mother Earth, grow rich! The wage is good.
- new English: Yoke the horses! Plough the arable land! Pull the yoke, horses, toil, man, toil! The earth is split, Mother Earth, grow rich! And the dear wage is good.

### t029-0016
- edits: c2 drop SUBJ gwexn; c4 drop POSS gwexn; c5 merge (break True->False); c6 merge (break True->False)
- old PIE: h₂wĺ̥h₁neh₂m uh₁inHdʰí tónom tn̥nudʰí. gʷḗn h₂wĺ̥h₁neh₂m uh₁inéHti tónom tn̥néwti. gʷnéh₂s wókʷm̥ ḱléwsete. kʷíd gʷḗn tḗtḱt? tónom tḗtḱt.
- new PIE: h₂wĺ̥h₁neh₂m uh₁inHdʰí tónom tn̥nudʰí. h₂wĺ̥h₁neh₂m uh₁inéHti tónom tn̥néwti. wókʷm̥ ḱléwsete kʷíd gʷḗn tḗtḱt tónom tḗtḱt.
- old English: Twist the wool, stretch the string! The woman twists the wool, stretches the string. Listen to the woman's voice! What did the woman make? She made a string.
- new English: Twist the wool, stretch the string! She twists the wool, stretches the string. Listen to the voice! What did the woman make? She made a string.

### t029-0017
- edits: c2 particle None->nu; c4 particle None->nu
- old PIE: wíHrōs dukté wíHrōs stundté. kʷékʷlos wéndʰetor kʷékʷlos pró h₁éyti. ḱḗr stuh₂róm mē sth₂éh₁yete.
- new PIE: wíHrōs dukté wíHrōs stundté. nu kʷékʷlos wéndʰetor kʷékʷlos pró h₁éyti. nu ḱḗr stuh₂róm mē sth₂éh₁yete.
- old English: Pull, men, push, men! The wheel turns, the wagon goes forward. The heart is strong, do not stand still!
- new English: Pull, men, push, men! The wheel turns, the wagon goes forward. The heart is strong, do not stand still!

### t029-0018
- edits: c0 add MOD kjeywos; c4 add MOD kjeywos; c5 particle None->nu
- old PIE: h₂ólut yése péh₂wr̥ dʰégʷʰeti. gʰostéyey h₂ólut pékʷete. gʰóstis srobʰéyeti ḱḗr-kʷe méwdt. ḱéywe ph₃dʰí sh₂dʰí-kʷe.
- new PIE: ḱéywom h₂ólut yése péh₂wr̥ dʰégʷʰeti. gʰostéyey h₂ólut pékʷete. gʰóstis srobʰéyeti ḱéywom-kʷe ḱḗr méwdt. nu ḱéywe ph₃dʰí sh₂dʰí-kʷe.
- old English: Boil, beer, boil, the fire burns. Cook the beer for the guest! The guest sips, and the heart became joyful. Dear one, drink, and be sated!
- new English: Boil, dear beer, boil, the fire burns. Cook the beer for the guest! The guest sips, and the dear heart became joyful. Dear one, drink, and be sated!

### t029-0019
- edits: c0 particle None->nu; c2 add MOD kjeywos
- old PIE: dʰh₂bʰre h₁ólom gʷʰr̥nudʰí. h₁ólom ph₂wéni h₃roǵéye. péh₂wr̥ dʰégʷʰeti dʰh₂bʰre stunddʰí. h₁ólos h₁wésus dʰh₂bʰrósyo ḱléwos méǵh₂.
- new PIE: nu dʰh₂bʰre h₁ólom gʷʰr̥nudʰí. h₁ólom ph₂wéni h₃roǵéye. ḱéywom péh₂wr̥ dʰégʷʰeti dʰh₂bʰre stunddʰí. h₁ólos h₁wésus dʰh₂bʰrósyo ḱléwos méǵh₂.
- old English: Smith, heat the awl! Straighten the awl in the fire! The fire is burning, strike, smith, strike! The awl is good, the smith's fame is great.
- new English: Smith, heat the awl! Straighten the awl in the fire! The dear fire is burning, strike, smith, strike! The awl is good, the smith's fame is great.

### t029-0020
- edits: c5 add MOD kjeywos; c5 merge (break True->False)
- old PIE: gʷówes sth₂éh₁yete gʷḗn h₂mélǵti. gʷówes dedh₃té wr̥h₁ḗn srobʰéyeti. mē bʰih₂té. gʷḗn muddʰí.
- new PIE: gʷówes sth₂éh₁yete gʷḗn h₂mélǵti. gʷówes dedh₃té wr̥h₁ḗn srobʰéyeti. mē bʰih₂té ḱéywa gʷḗn muddʰí.
- old English: Stand, cattle, stand, the woman milks. Give, cattle, give, the lamb sips. Do not be afraid! Be joyful, woman!
- new English: Stand, cattle, stand, the woman milks. Give, cattle, give, the lamb sips. Do not be afraid! Be joyful, dear woman!

### t029-0021
- edits: c2 add MOD h1wesus; c3 particle None->nu
- old PIE: dṓm démete dṓm h₂réydʰete. bʰréh₂teres dukté. dṓm stestóh₂e h₂éHsh₂-kʷe dʰégʷʰeti. bʰréh₂teres twóm misdʰóm h₁áydʰwe.
- new PIE: dṓm démete dṓm h₂réydʰete. h₁wésewes bʰréh₂teres dukté. nu dṓm stestóh₂e h₂éHsh₂-kʷe dʰégʷʰeti. bʰréh₂teres twóm misdʰóm h₁áydʰwe.
- old English: Build the house, build it, put the house in order! Brothers, pull! The house stands, and the hearth burns. Brothers, take your wage!
- new English: Build the house, build it, put the house in order! Good brothers, pull! The house stands, and the hearth burns. Brothers, take your wage!

### t029-0022
- edits: c0 add MOD lewbhos; c2 particle None->nu; c3 merge (break True->False); c4 particle None->nu; c5 particle None->nu; c5 merge (break True->False)
- old PIE: wíHrōs wódr̥ déh₂nus bʰérete. swésor wódr̥ limnés bʰére. léymō stéwdt. gʰostéyey h₂ólut dh₃dʰí. mē h₃slidʰté. wéǵʰete.
- new PIE: léwbʰōs wíHrōs wódr̥ déh₂nus bʰérete. swésor wódr̥ limnés bʰére. nu léymō stéwdt gʰostéyey h₂ólut dh₃dʰí. nu mē h₃slidʰté nu wéǵʰete.
- old English: Carry the water from the river, men! Sister, carry the water from the lake. The lake has become cold. Give beer to the guest! Do not slip! Keep carrying!
- new English: Carry the water from the river, dear men! Sister, carry the water from the lake. The lake has become cold. Give beer to the guest! Do not slip! Keep carrying!

### t029-0023
- edits: c0 particle None->nu; c3 add MOD lewbhos; c4 split (break False->True); c5 merge (break True->False)
- old PIE: kʷékʷlom pitséh₁ h₂linHdʰí. kʷékʷlom wéndʰe pī́ts dʰégʷʰeti. dʰh₂bʰrós kʷékʷlom démet kʷékʷlos h₁wésus. Hróth₂os h₁ln̥gʷʰrós.
- new PIE: nu kʷékʷlom pitséh₁ h₂linHdʰí. kʷékʷlom wéndʰe pī́ts dʰégʷʰeti. lewbʰós dʰh₂bʰrós kʷékʷlom démet. kʷékʷlos h₁wésus Hróth₂os h₁ln̥gʷʰrós.
- old English: Smear the wheel with pitch! Turn the wheel, the pitch is burning. The craftsman built the wheel, the wheel is good. The chariot is light.
- new English: Smear the wheel with pitch! Turn the wheel, the pitch is burning. The dear craftsman built the wheel, the wheel is good. The chariot is light.

### t029-0024
- edits: c0 add MOD lewbhos; c1 merge (break True->False); c2 split (break False->True); c3 merge (break True->False)
- old PIE: kólHonm̥ h₁imés. ḱwṓ pró h₁éyti sékʷomesdʰh₂-kʷe. gʷéh₂omes.
- new PIE: lewbʰóm kólHonm̥ h₁imés ḱwṓ pró h₁éyti. sékʷomesdʰh₂-kʷe gʷéh₂omes.
- old English: We go to the hill. The dog goes forward, and we follow. Let us go!
- new English: We go to the dear hill. The dog goes forward, and we follow. Let us go!

### t029-0025
- edits: c0 particle None->nu; c2 drop LOC peh2wr; c3 merge (break True->False)
- old PIE: h₂óweyes sth₂éh₁yete h₂wĺ̥h₁neh₂m skindmés. h₂wĺ̥h₁neh₂m ph₂wéni h₂sowséyete. nu yúH nogʷéh₂es.
- new PIE: nu h₂óweyes sth₂éh₁yete h₂wĺ̥h₁neh₂m skindmés. h₂wĺ̥h₁neh₂m h₂sowséyete nu yúH nogʷéh₂es.
- old English: Sheep, stand, we cut the wool. Dry the wool by the fire! Now you are naked.
- new English: Sheep, stand, we cut the wool. Dry the wool! Now you are naked.

### t029-0026
- edits: c0 particle None->nu; c1 particle None->nu; c3 particle None->nu
- old PIE: wíHrōs pérwr̥ gléwbʰete. tód gléwbʰete swidyómes. pérwr̥ Hrumptór mē h₃slidʰté.
- new PIE: nu wíHrōs pérwr̥ gléwbʰete. nu tód gléwbʰete swidyómes. nu pérwr̥ Hrumptór mē h₃slidʰté.
- old English: Split the rock, men! Split it, we sweat. The rock breaks, do not slip!
- new English: Split the rock, men! Split it, we sweat. The rock breaks, do not slip!

### t029-0027
- edits: c4 particle None->nu; c4 merge (break True->False)
- old PIE: súHnew bʰéwdʰe h₁regʷesyéti. stéh₂dʰh₁om spéḱye wókʷm̥ ḱléwse. mē légʰs.
- new PIE: súHnew bʰéwdʰe h₁regʷesyéti. stéh₂dʰh₁om spéḱye wókʷm̥ ḱléwse nu mē légʰs.
- old English: Be awake, son, be awake, it is getting dark. Look at the herd, listen to the voice! Do not lie down.
- new English: Be awake, son, be awake, it is getting dark. Look at the herd, listen to the voice! Do not lie down.

