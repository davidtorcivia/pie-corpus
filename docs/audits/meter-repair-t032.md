# Meter repair: t032

meter_exact before: 0.306 (49/160); after: 1.000 (157/157). Gate PASS (all gates). Lexeme caps respected.

Method: edits found with the `scripts/meter_report.py` machinery (each realized and checked by `check_plan`), applied to `data/generation/plans/t032.jsonl`, English updated to match, re-realized with `--model claude-sonnet-5-5 --prompt-id tier3-planner-v4`. `corpus/` not hand-edited; `pie/` and tools unchanged. Particle edits (nu/-ge) leave the English unchanged except where it carried the particle ("indeed" for -ge, "now/then" for nu): removed when the particle was dropped. A -kʷe added at the start of a sentence appears as "And". Merged/split sentences change only line boundaries.

Head/dep index check: for every changed plan the (slot, head/dep target) links were compared with the original plan; only intended drops/additions differ, none retargeted. No vocative edit was used, so the reported vocative-index bug did not affect this batch. No fixes were needed.


## Changed lines (plan id, edits, old/new PIE of the whole text, old/new English)


### t032-0001
- edits: c3 conj -kʷe kʷe->None; c4 particle None->nu; c6 particle nu->None; c7 add MOD kjeywos
- old PIE: nu gʷówes ḱóymom gʷm̥té. poh₂imḗn usmé wédʰeti. nu wih₁rós énu sékʷetor. h₁regʷesyéti mē h₃slidʰté mē-kʷe kʷis n̥ḱyéh₁t. pótnih₂ gʷṓs dʰwóri h₂mélǵti. lewkós h₂éydʰos sédesi dʰégʷʰeti.
- new PIE: nu gʷówes swóm ḱóymom gʷm̥té. poh₂imḗn usmé wédʰeti. nu wih₁rós énu sékʷetor. h₁regʷesyéti mē h₃slidʰté mē kʷis n̥ḱyéh₁t. nu pótnih₂ gʷṓs dʰwóri h₂mélǵti. nu lewkós h₂éydʰos sédesi dʰégʷʰeti.
- old English: Worm, go out of the bone, go out of the blood! Do not devour the blood, do not suck the sore. The worm is dead, and the sore is gone. Now let it grow strong, and let the blood be in it. May the god protect you, and may Dawn guard you.
- new English: Worm, go out of the bone, go out of the blood! Do not devour the blood, do not suck the sore. The worm is dead, and the sore is gone. Let it grow strong, and let the dear blood be in it. May the god protect you, and may Dawn guard you.

### t032-0002
- edits: c1 conj -kʷe kʷe->None; c2 add MOD kjeywos; c2 particle nu->None; c3 particle None->nu; c4 add MOD lewbhos; c4 particle nu->None; c5 particle nu->None; c7 add MOD kjeywos
- old PIE: h₁éḱwos h₂éǵroy ḱéyo ne-kʷe h₁ḗdt. wiHrós h₁ím widét h₃ésth₁ Hrumptó. h₃ésth₁ h₃roǵéyet h₁íd-kʷe ḱélet. dʰoHnéh₂m bʰéret h₁ésmey-kʷe h₁íh₂m̥ dédeh₃t. nu h₁éḱwos sth₂éh₁yet h₁ḗdt-kʷe.
- new PIE: h₁éḱwos h₂éǵroy ḱéyo ne-kʷe h₁ḗdt. wiHrós h₁ím widét h₃ésth₁ Hrumptó. h₃ésth₁ h₃roǵéyet h₁íd-kʷe ḱélet. dʰoHnéh₂m bʰéret h₁ésmey-kʷe h₁íh₂m̥ dédeh₃t. nu h₁éḱwos sth₂éh₁yet h₁ḗdt-kʷe.
- old English: The god went out, and the horse's bone broke. Then three times he spoke the word. Mother Earth, join bone with bone! Now join blood with blood! Then the bone grew strong, and the blood was joined. May this man's bone grow strong.
- new English: The god went out, the horse's bone broke. Three times he spoke the dear word. Mother Earth, join bone with bone! Join dear blood with blood! The bone grew strong, and the blood was joined. May this man's dear bone grow strong.

### t032-0003
- edits: c3 drop POSS soh2wl; c4 merge (break True->False); c5 particle None->nu; c7 particle None->nu
- old PIE: h₂wést bʰréh₂ter-kʷe ne gʷm̥sḱési. h₂éǵrom spéḱyoh₂ twé ne kʷéḱm̥. téwe h₁éḱwōs h₁ludʰónt túH-kʷe ne h₁ludʰés. nu kʷís méǵʰye bʰéh₂eti? méne h₃kʷṓm bʰéh₂os h₁és twé memónh₂e.
- new PIE: h₂wést bʰréh₂ter-kʷe ne gʷm̥sḱési. h₂éǵrom spéḱyoh₂ twé ne kʷéḱm̥. téwe h₁éḱwōs h₁ludʰónt túH-kʷe ne h₁ludʰés. nu-kʷe kʷís méǵʰye bʰéh₂eti? nu méne h₃kʷṓm bʰéh₂os h₁és twé memónh₂e.
- old English: Blood, stand still, and do not go out! I lay a cord around the sore. May the eye of the sun look upon it. May the sun dry the blood. The door is shut, the blood stays within. Thrice I speak the word to you.
- new English: Blood, stand still, and do not go out! I lay a cord around the sore. May the eye look upon it. May the sun dry the blood. The door is shut, the blood stays within. Thrice I speak the word to you.

### t032-0004
- edits: c0 add MOD lewbhos; c4 particle None->nu; c5 add MOD lewbhos; c5 particle ge->None; c6 particle None->nu; c7 particle None->nu
- old PIE: wíh₁re HeHḱéwes h₁éḱwōs dʰwóri stesth₂ḗr. tr̥ménti h₂eǵós-kʷe séngʷt. téwe ǵʰoysós séngʷt téwe Hróth₂os Hrumptó. nu kʷís h₁íns yéwgeti? nu kʷís Hróth₂om h₂éǵēti? wíh₁re l̥gʰdʰí téwe h₁nómn̥ méǵh₂.
- new PIE: wíh₁re HeHḱéwes h₁éḱwōs dʰwóri stesth₂ḗr. nu tr̥ménti h₂eǵós-kʷe séngʷt. téwe ǵʰoysós séngʷt téwe Hróth₂os Hrumptó. kʷís h₁íns yéwgeti kʷís Hróth₂om h₂éǵēti? nu wíh₁re l̥gʰdʰí téwe h₁nómn̥ méǵh₂.
- old English: What burns in the heart, let that grow cold! Water, come to the man and to his bones! Now let him lie down and sweat. May the fire indeed go away. Night shall carry it away. Dawn shines, and he lives.
- new English: What burns in the dear heart, let that grow cold! Water, come to the man and to his bones! Now let him lie down and sweat. May the dear fire go away. Night shall carry it away. Dawn shines, and he lives.

### t032-0005
- edits: merged two negated clauses into one coordinated GOAL (sheep and shepherd) + particle nu; added epithet pie-lex-HeHkjus (swift) on h2engwhis
- old PIE: sérpont h₂éngʷʰey lóyseh₂i l̥gʰdʰí. h₂ówins mē h₁r̥sḱés poh₂iménm̥ mē h₁r̥sḱés. nu ḱwṓ bʰéwdʰeti twé kʷéḱt. h₂epó sérpe nu bʰudʰménm̥ ní h₁idʰí. wih₁rós kʷis ǵʰwḗr-kʷe mē n̥ḱyéh₁t.
- new PIE: sérpont HéHḱew h₂éngʷʰey lóyseh₂i l̥gʰdʰí. nu h₂ówins poh₂iménm̥-kʷe mē h₁r̥sḱés. nu ḱwṓ bʰéwdʰeti nu twé kʷéḱt. h₂epó sérpe nu bʰudʰménm̥ ní h₁idʰí. wih₁rós kʷis ǵʰwḗr-kʷe mē n̥ḱyéh₁t.
- old English: Snake, creeping in the furrow, lie down! Do not go to the sheep, do not go to the shepherd. Now the dog is awake, he sees you. Creep away, now go down to the bottom. May no one be lost, man and beast alike.
- new English: Swift snake, creeping in the furrow, lie down! Do not go to the sheep or the shepherd. Now the dog is awake, he sees you. Creep away, now go down to the bottom. May no one be lost, man and beast alike.

### t032-0006
- edits: c0 add MOD lewbhos; c1 particle None->nu; c2 conj -kʷe None->kʷe; c3 particle None->nu; c4 add MOD lewbhos; c5 particle None->nu
- old PIE: wĺ̥kʷe poh₂imnés h₂ówins mē h₁éps. poh₂imḗn ḱwṓ-kʷe h₁íh₂n̥s h₂léksetes. nu ǵʰwḗrn̥s h₂epó h₁idʰí. pérkʷune h₂ówins ph₂sdʰí. wĺ̥kʷos dʰurés h₂éǵrōd-kʷe bʰugyéh₁t. ḱwṓ bʰéwdʰeti wĺ̥kʷos-kʷe mē h₁r̥yéh₁t.
- new PIE: wĺ̥kʷe poh₂imnés lewbʰā́s h₂ówins mē h₁éps. nu poh₂imḗn ḱwṓ-kʷe h₁íh₂n̥s h₂léksetes. nu-kʷe ǵʰwḗrn̥s h₂epó h₁idʰí. nu pérkʷune h₂ówins ph₂sdʰí. wĺ̥kʷos lewbʰéh₂s dʰurés h₂éǵrōd-kʷe bʰugyéh₁t. nu ḱwṓ bʰéwdʰeti wĺ̥kʷos-kʷe mē h₁r̥yéh₁t.
- old English: Wolf, do not seize the shepherd's sheep! The shepherd and the dog protect them. Now go away to the wild beasts. Perkunos, guard the sheep, and let the wolf flee from the door and the field. The dog is awake, and let the wolf not come.
- new English: Wolf, do not seize the shepherd's dear sheep! The shepherd and the dog protect them. And now go away to the wild beasts. Perkunos, guard the sheep, and let the wolf flee from the dear door and the field. The dog is awake, and let the wolf not come.

### t032-0007
- edits: c0 particle None->nu; c2 add MOD lewbhos
- old PIE: nókʷts gʷémt wiḱpótis-kʷe légʰt. bʰór wiḱpóteys dʰwórm̥ mē gʷm̥yés. téwe h₃ókʷih₁ mē widóyh₁tām. nu bʰór téwe dóws ḱr̥mh₂yéh₁t. ḱwṓ bʰéwdʰeti deywós-kʷe ḱóymom péh₂sti. h₁yós gʷṓs stéh₂yeti só mr̥yéh₁t.
- new PIE: nu nókʷts gʷémt wiḱpótis-kʷe légʰt. bʰór wiḱpóteys lewbʰéh₂m dʰwórm̥ mē gʷm̥yés. téwe h₃ókʷih₁ mē widóyh₁tām. nu bʰór téwe dóws ḱr̥mh₂yéh₁t. ḱwṓ bʰéwdʰeti deywós-kʷe ḱóymom péh₂sti. h₁yós gʷṓs stéh₂yeti só mr̥yéh₁t.
- old English: Night has come, and the master has lain down. Thief, do not come to the master's door! Let your eyes not see. Now, thief, let your arm go slack. The dog is awake, and the god guards the home. Whoever steals the cattle, let him die.
- new English: Night has come, and the master has lain down. Thief, do not come to the master's dear door! Let your eyes not see. Now, thief, let your arm go slack. The dog is awake, and the god guards the home. Whoever steals the cattle, let him die.

### t032-0008
- edits: c0 particle None->nu; c2 add MOD h1wesus; c2 particle nu->None; c4 add MOD h1wesus; c6 conj -kʷe None->kʷe; c7 particle None->nu
- old PIE: súHnew kʷsépi mē tréses. téwe méh₂tēr h₂énti h₁ésti. nu deywós h₂énti h₁ésti. twé h₂lékseti ḱwṓ-kʷe bʰéwdʰeti. h₁wésu súpniyom twé h₁r̥sḱóyh₁t. nu kʷséps bʰéwgt h₂ew-kʷe h₂wést.
- new PIE: nu súHnew kʷsépi mē tréses. téwe méh₂tēr h₂énti h₁ésti. h₁wésus deywós h₂énti h₁ésti. twé h₂lékseti h₁wésus-kʷe ḱwṓ bʰéwdʰeti. h₁wésu súpniyom twé h₁r̥sḱóyh₁t. nu-kʷe kʷséps bʰéwgt nu-kʷe h₂ew h₂wést.
- old English: Son, do not tremble in the night! Your mother is near. Now the god is near. He protects you, and the dog is awake. May a good dream come to you. Now night flees, and it dawns again.
- new English: Son, do not tremble in the night! Your mother is near. The good god is near. He protects you, and the good dog is awake. May a good dream come to you. And now night flees, and it dawns again.

### t032-0009
- edits: c2 particle None->nu; c4 particle None->nu; c5 add MOD h1wesus
- old PIE: dyéw ph₂ter dʰoHnéh₂i h₂wr̥syéh₁t. dʰéǵʰom méh₂ter h₁íh₂m̥ bʰére. gʷṓs yugté lóyseh₂m-kʷe h₂érh₃yōmes. dʰoHnéh₂ lóyseh₂i h₃pusyéh₁t. sóh₂wl̥ h₁íh₂m̥ pékʷoyh₁t. h₂óweyes sph₁réh₂es h₁sih₁ént. h₃épos r̥h₁dʰyéh₁t yugóm-kʷe mē Hrumpih₁tó.
- new PIE: dyéw ph₂ter dʰoHnéh₂i h₂wr̥syéh₁t. dʰéǵʰom méh₂ter h₁íh₂m̥ bʰére. nu gʷṓs yugté lóyseh₂m-kʷe h₂érh₃yōmes. nu dʰoHnéh₂ lóyseh₂i h₃pusyéh₁t. h₁wésu sóh₂wl̥ h₁íh₂m̥ pékʷoyh₁t. h₂óweyes sph₁réh₂es h₁sih₁ént. h₃épos r̥h₁dʰyéh₁t yugóm-kʷe mē Hrumpih₁tó.
- old English: Father Dyeus, let it rain on the grain! Mother Earth, bear it. Yoke the cattle, and let us plough the furrow. May the grain increase in the furrow. May the sun ripen it. May the sheep be fat. May the work succeed, and may the yoke not break.
- new English: Father Dyeus, let it rain on the grain! Mother Earth, bear it. Yoke the cattle, and let us plough the furrow. May the grain increase in the furrow. May the good sun ripen it. May the sheep be fat. May the work succeed, and may the yoke not break.

### t032-0010
- edits: c0 add MOD swos; c5 conj -kʷe kʷe->None; c6 particle None->nu; c7 particle None->nu
- old PIE: nu gʷówes ḱóymom gʷm̥té. poh₂imḗn usmé wédʰeti. nu wih₁rós énu sékʷetor. h₁regʷesyéti mē h₃slidʰté mē-kʷe kʷis n̥ḱyéh₁t. pótnih₂ gʷṓs dʰwóri h₂mélǵti. lewkós h₂éydʰos sédesi dʰégʷʰeti.
- new PIE: nu gʷówes swóm ḱóymom gʷm̥té. poh₂imḗn usmé wédʰeti. nu wih₁rós énu sékʷetor. h₁regʷesyéti mē h₃slidʰté mē kʷis n̥ḱyéh₁t. nu pótnih₂ gʷṓs dʰwóri h₂mélǵti. nu lewkós h₂éydʰos sédesi dʰégʷʰeti.
- old English: Now, cattle, come home to the village! The shepherd leads you. Now the man follows along. It is getting dark. Do not slip away, and let no one be lost. At the door the mistress milks the cattle. In the dwelling the bright blaze burns.
- new English: Now, cattle, come home to your own village! The shepherd leads you. Now the man follows along. It is getting dark. Do not slip away, let no one be lost. At the door the mistress milks the cattle. In the dwelling the bright blaze burns.

### t032-0011
- edits: c2 particle None->nu; c4 particle None->nu; c7 particle None->nu
- old PIE: nu dyéw ph₂ter h₂wr̥syéh₁t h₂wr̥syéh₁t. pérkʷune pérkʷum stunddʰí. nu wódr̥ diwés ní h₁ludʰét. dʰéǵʰōm tr̥syéti péh₃tu pléh₁tu-kʷe. dʰoHnéh₂ h₂wékseti ḱód dóh₃r̥ méǵh₂.
- new PIE: nu dyéw ph₂ter h₂wr̥syéh₁t h₂wr̥syéh₁t. nu pérkʷune pérkʷum stunddʰí. nu wódr̥ diwés ní h₁ludʰét. nu dʰéǵʰōm tr̥syéti péh₃tu pléh₁tu-kʷe. nu dʰoHnéh₂ h₂wékseti ḱód dóh₃r̥ méǵh₂.
- old English: Now, Father Dyeus, may it rain, may it rain! Perkunos, strike the oak. Now the water comes down from the sky. The earth is thirsty; let her drink and be full. Then the grain will grow, great is this gift.
- new English: Now, Father Dyeus, may it rain, may it rain! Perkunos, strike the oak. Now the water comes down from the sky. The earth is thirsty; let her drink and be full. Then the grain will grow, great is this gift.

### t032-0012
- edits: c0 add MOD polh1us; c3 particle None->nu; c6 conj -kʷe None->kʷe; c7 particle None->nu
- old PIE: péh₂wr̥ wórmons h₂wĺ̥h₁neh₂i h₁éwse. kʷŕ̥mins h₁éwse h₂ōwyéh₂ h₁éwse. h₂wĺ̥h₁neh₂m mē h₁éwses sédos mē h₁éwses. h₂éwis h₂wĺ̥h₁na lewkéh₂ bʰuHdʰí. nu wih₁rós h₁íh₂m̥ m̥dʰúh₁ h₂linéHti. wórmōs h₁ésmi méronti.
- new PIE: polh₁ú péh₂wr̥ wórmons h₂wĺ̥h₁neh₂i h₁éwse. kʷŕ̥mins h₁éwse h₂ōwyéh₂ h₁éwse. nu h₂wĺ̥h₁neh₂m mē h₁éwses sédos mē h₁éwses. h₂éwis h₂wĺ̥h₁na lewkéh₂ bʰuHdʰí. nu-kʷe wih₁rós h₁íh₂m̥ m̥dʰúh₁ h₂linéHti. nu wórmōs h₁ésmi méronti.
- old English: Fire, burn the grubs in the wool! Burn the worms, burn the eggs. Do not burn the wool, do not burn the dwelling. Be bright, wool of the sheep. Now the man smears it with honey. The grubs shall die in it.
- new English: Much fire, burn the grubs in the wool! Burn the worms, burn the eggs. Do not burn the wool, do not burn the dwelling. Be bright, wool of the sheep. And now the man smears it with honey. The grubs shall die in it.

### t032-0013
- edits: c0 drop POSS closed:personal/2; c0 particle None->nu; c3 drop POSS closed:anaphoric_i; c3 particle None->nu; c4 drop POSS closed:personal/2; c4 particle None->nu
- old PIE: sh₂imónm̥ téwe ḱérdi péri logʰéyoh₂. téwe ḱḗr h₁mé pró h₁r̥sḱétu. téwe ménos h₁mé sékʷoyh₁to. pérkʷus h₁ésyo wr̥h₂déh₁ stestóh₂e. téwe wénh₁os sh₂imnéh₁ stestóh₂tu. sh₂imṓ kʷsépi mē Hrumpih₁tó.
- new PIE: nu sh₂imónm̥ ḱérdi péri logʰéyoh₂. téwe ḱḗr h₁mé pró h₁r̥sḱétu. téwe ménos h₁mé sékʷoyh₁to. nu pérkʷus wr̥h₂déh₁ stestóh₂e. nu wénh₁os sh₂imnéh₁ stestóh₂tu. sh₂imṓ kʷsépi mē Hrumpih₁tó.
- old English: I lay a cord around your heart. Let your heart come forward to me, let your mind follow me. The oak stands by its root. Let your love stand firm by the cord, and may the cord not break in the night.
- new English: I lay a cord around the heart. Let your heart come forward to me, let your mind follow me. The oak stands by the root. Let love stand firm by the cord, and may the cord not break in the night.

### t032-0014
- edits: c0 particle None->nu; c1 particle None->nu; c2 particle None->nu; c4 conj -kʷe kʷe->None; c5 particle None->nu; c6 particle None->nu
- old PIE: pérkʷunos wih₁rṓm ḱérdh₂ dedórḱe. h₁yós gʰóstim dʰrugʰyéti só n̥ḱyéh₁t. bʰoydʰéh₂ sth₂éh₁yetu h₁íh₂-kʷe méǵh₂ih₂. h₁yós bʰoydʰéh₂m péh₂sti só gʷíh₃wēti. deywṓs bʰoydʰéh₂s wékʷos ḱluwént. gʰóstim sédos h₁n̥dó wédʰe.
- new PIE: nu pérkʷunos wih₁rṓm ḱérdh₂ dedórḱe. nu h₁yós gʰóstim dʰrugʰyéti nu só n̥ḱyéh₁t. bʰoydʰéh₂ sth₂éh₁yetu h₁íh₂ méǵh₂ih₂. nu h₁yós bʰoydʰéh₂m péh₂sti nu só gʷíh₃wēti. deywṓs bʰoydʰéh₂s wékʷos ḱluwént. gʰóstim sédos h₁n̥dó wédʰe.
- old English: Perkunos has seen the hearts of men. Whoever deceives the guest, let him vanish. Let the oath stand; it is great. He who guards the pledge shall live. The gods have heard the word of the oath. Lead the guest into the dwelling.
- new English: Perkunos has seen the hearts of men. Whoever deceives the guest, let him vanish. Let the oath stand; it is great. He who guards the pledge shall live. The gods have heard the word of the oath. Lead the guest into the dwelling.

### t032-0028
- edits: c0 add MOD swos; c0 particle None->nu; c1 particle None->nu; c2 drop POSS closed:personal/2; c3 particle None->nu; c7 drop MOD kjlutos; c7 particle None->nu; c8 particle None->nu
- old PIE: súHnew ḱóymōd dʰǵʰyés léyts. ne h₁ludʰés téwe-kʷe ph₂tḗr twé h₂isḱéti. ǵʰoysós twé h₂éǵroy h₃wáth₂t. téwe h₁ésh₂r̥ dʰéǵʰōm h₁éyti. nu téwe h₃ésth₁h₂ h₂én ḱéyor. kʷís téwe Hróth₂om h₂éǵēti? ḱlutóm téwe h₁nómn̥ mē mr̥yéh₁t. twé kʷsépi trís HréwdHmi.
- new PIE: nu súHnew swṓd ḱóymōd dʰǵʰyés léyts. nu ne h₁ludʰés ph₂tḗr-kʷe twé h₂isḱéti. nu ǵʰoysós twé h₂éǵroy h₃wáth₂t. téwe h₁ésh₂r̥ dʰéǵʰōm h₁éyti. nu téwe h₃ésth₁h₂ h₂én ḱéyor. kʷís téwe Hróth₂om h₂éǵēti? nu téwe h₁nómn̥ mē mr̥yéh₁t. nu twé kʷsépi trís HréwdHmi.
- old English: Yesterday, son, you went away from the home. You did not arrive, and your father seeks you. The spear wounded you in the field. Your blood goes into the earth, and now your bones lie there. Who shall drive your chariot? May your famous name not die. Thrice I cry out for you in the night.
- new English: Yesterday, son, you went away from your own home. You did not arrive, and the father seeks you. The spear wounded you in the field. Your blood goes into the earth, and now your bones lie there. Who shall drive your chariot? May your name not die. Thrice I cry out for you in the night.

### t032-0029
- edits: c0 particle None->nu; c1 particle None->nu; c3 conj -kʷe kʷe->None; c4 particle None->nu; c6 drop POSS closed:personal/1; c6 particle None->nu
- old PIE: h₂éḱruh₂ méne h₃kʷsú h₁ésti. méne suHnús lelóykʷe. wĺ̥kʷos h₁ím ne h₁épt ǵʰoysós-kʷe h₁ím ne térh₃t. h₁ím kʷis sléh₂gʷt h₁ím-kʷe wéydsoh₂. h₂énǵʰos méne gudóm gʷr̥h₃éti. kʷís méǵʰye h₁ím h₁opéyēti?
- new PIE: nu h₂éḱruh₂ méne h₃kʷsú h₁ésti. nu méne suHnús lelóykʷe. wĺ̥kʷos h₁ím ne h₁épt ǵʰoysós h₁ím ne térh₃t. nu kʷis h₁ím sléh₂gʷt h₁ím-kʷe wéydsoh₂. nu h₂énǵʰos gudóm gʷr̥h₃éti. kʷís méǵʰye h₁ím h₁opéyēti?
- old English: Tears are in my eyes. My son is gone. The wolf did not seize him, and the spear did not wound him. Someone has seized him, and I long to see him. Grief eats my entrails. Who will give him to me?
- new English: Tears are in my eyes. My son is gone. The wolf did not seize him, the spear did not wound him. Someone has seized him, and I long to see him. Grief eats the entrails. Who will give him to me?

### t032-0030
- edits: c6 conj -kʷe None->kʷe; c7 particle None->nu
- old PIE: h₂wést bʰréh₂ter-kʷe ne gʷm̥sḱési. h₂éǵrom spéḱyoh₂ twé ne kʷéḱm̥. téwe h₁éḱwōs h₁ludʰónt túH-kʷe ne h₁ludʰés. nu kʷís méǵʰye bʰéh₂eti? méne h₃kʷṓm bʰéh₂os h₁és twé memónh₂e.
- new PIE: h₂wést bʰréh₂ter-kʷe ne gʷm̥sḱési. h₂éǵrom spéḱyoh₂ twé ne kʷéḱm̥. téwe h₁éḱwōs h₁ludʰónt túH-kʷe ne h₁ludʰés. nu-kʷe kʷís méǵʰye bʰéh₂eti? nu méne h₃kʷṓm bʰéh₂os h₁és twé memónh₂e.
- old English: It has dawned, brother, and you do not come. I look at the field; I did not see you. Your horses arrived, but you did not arrive. Who shall speak to me now? You were the light of my eyes. I remember you.
- new English: It has dawned, brother, and you do not come. I look at the field; I did not see you. Your horses arrived, but you did not arrive. And who shall speak to me now? You were the light of my eyes. I remember you.

### t032-0031
- edits: c1 particle None->nu; c2 drop POSS h2engjhos; c3 merge (break True->False); c4 drop POSS closed:personal/1; c4 particle None->nu; c5 particle None->nu; c6 conj -kʷe None->kʷe
- old PIE: méne wiHrós pr̥kʷéwi Hn̥dʰí ḱéyor. h₁ésyo kʷis sédesi ne sísdeti. h₂énǵʰesos wéstrom wésh₂er. nu kʷís yugóm yéwgeti? kʷís méne lóyseh₂m h₂érh₃yēti? méne sédos h₂ew wiḱdʰí. mr̥tṓs-ge ne ḱl̥nwénti. h₁wésu téwe ḱléwos h₂uksyéh₁t.
- new PIE: méne wiHrós pr̥kʷéwi Hn̥dʰí ḱéyor. nu kʷis h₁ésyo sédesi ne sísdeti. wéstrom wésh₂er nu kʷís yugóm yéwgeti? nu kʷís lóyseh₂m h₂érh₃yēti? nu méne sédos h₂ew wiḱdʰí. mr̥tṓs-kʷe-ge ne ḱl̥nwénti. h₁wésu téwe ḱléwos h₂uksyéh₁t.
- old English: My husband lies under the oak. No one sits down in his seat. I wear the garment of grief. Now who shall harness the yoke? Who shall plough my furrow? Come back into my home. The dead indeed do not listen. May your good fame grow.
- new English: My husband lies under the oak. No one sits down in his seat. I wear the garment. Now who shall harness the yoke? Who shall plough the furrow? Come back into my home. And the dead indeed do not listen. May your good fame grow.

### t032-0032
- edits: c3 particle None->nu; c3 conj -kʷe None->kʷe; c4 particle None->nu; c8 drop MOD kjlutos; c8 particle None->nu
- old PIE: h₃rḗǵs mért h₁ésyo ḱléwos méǵh₂. nu h₁ésyo ḱléwos ń̥dʰgʷʰitom h₁éseti. h₁ésyo wéyHs méǵh₂ih₂ h₁ést. wiḱpóteyes stesth₂ḗr HrudHénti-kʷe. Hróth₂os stestóh₂e h₂eǵós-kʷe ne h₁ésti. ḱlutóm h₁ésyo h₁nómn̥ méǵh₂ h₁syéh₁t.
- new PIE: h₃rḗǵs mért h₁ésyo ḱléwos méǵh₂. nu h₁ésyo ḱléwos ń̥dʰgʷʰitom h₁éseti. nu-kʷe h₁ésyo wéyHs méǵh₂ih₂ h₁ést. nu wiḱpóteyes stesth₂ḗr HrudHénti-kʷe. Hróth₂os stestóh₂e h₂eǵós-kʷe ne h₁ésti. nu h₁ésyo h₁nómn̥ méǵh₂ h₁syéh₁t.
- old English: The king has died, his fame is great. Now his fame shall be imperishable. His strength was great. The lords stand and cry out. The chariot is standing, and there is no driver. May his famous name be great.
- new English: The king has died, his fame is great. Now his fame shall be imperishable. And his strength was great. The lords stand and cry out. The chariot is standing, and there is no driver. May his name be great.

### t032-0033
- edits: c0 particle None->nu; c2 particle None->nu; c2 conj -kʷe None->kʷe; c3 conj -kʷe None->kʷe; c4 particle None->nu; c5 particle None->nu; c8 conj -kʷe None->kʷe
- old PIE: méne ḱwṓ mr̥tós méne ḱéywos h₁ést. h₁mé lóyseh₂i énu sékʷeto. h₁yód wĺ̥kʷos h₁ért ḱéywos h₁ím úd ǵʰéyt. h₁ésyo h₃ókʷih₁ lewkóyh₁ h₁stā́m. nu Hn̥dʰí h₂én légʰyeti ḱéywe l̥gʰdʰí. nu kʷís kʷsépi bʰéwdʰēti?
- new PIE: nu méne ḱwṓ mr̥tós méne ḱéywos h₁ést. nu-kʷe h₁mé lóyseh₂i énu sékʷeto. h₁yód-kʷe wĺ̥kʷos h₁ért nu ḱéywos h₁ím úd ǵʰéyt. nu h₁ésyo h₃ókʷih₁ lewkóyh₁ h₁stā́m. nu Hn̥dʰí h₂én légʰyeti ḱéywe l̥gʰdʰí. nu-kʷe kʷís kʷsépi bʰéwdʰēti?
- old English: My dog is dead, he was my dear friend. He followed me along the furrow. When the wolf arrived, the dear one drove it out. His eyes were bright. Now he lies there below, lie down, dear friend. Who shall stay awake now, in the night?
- new English: My dog is dead, he was my dear friend. And he followed me along the furrow. And when the wolf arrived, the dear one drove it out. His eyes were bright. Now he lies there below, lie down, dear friend. And who shall stay awake now, in the night?

### t032-0034
- edits: c2 conj -kʷe None->kʷe; c3 drop POSS closed:personal/1; c3 particle None->nu; c4 drop POSS closed:personal/1; c4 particle None->nu; c5 conj -kʷe None->kʷe; c6 particle None->nu
- old PIE: gʰósteyes h₁rént h₂éydʰos-kʷe ḱóymom gʷr̥h₃ét. nu Hrowpóm h₁éǵʰs bʰoréyont. méne bʰréh₂teres kúdʰe h₁sénti? méne swésores kúdʰe h₁sénti? nu kʷís ḱóymom démēti? pérkʷune ḱód dedórḱth₂e?
- new PIE: gʰósteyes h₁rént h₂éydʰos-kʷe ḱóymom gʷr̥h₃ét. nu-kʷe Hrowpóm h₁éǵʰs bʰoréyont. nu bʰréh₂teres kúdʰe h₁sénti? nu swésores kúdʰe h₁sénti? nu-kʷe kʷís ḱóymom démēti? nu pérkʷune ḱód dedórḱth₂e?
- old English: The strangers arrived, and a blaze devoured the village. Then they carried off the plunder. Where are my brothers? Where are my sisters? Now who shall build the village? Perkunos, do you see this?
- new English: The strangers arrived, and a blaze devoured the village. And then they carried off the plunder. Where are the brothers? Where are the sisters? And now who shall build the village? Perkunos, do you see this?

### t032-0035
- edits: c0 particle None->nu; c2 particle None->nu; c3 particle None->nu; c4 drop POSS closed:personal/1; c7 conj -kʷe kʷe->None
- old PIE: bʰéh₂os séngʷt h₂ew-kʷe h₁ludʰét. dʰoHnéh₂ ní séngʷt h₂wékst-kʷe. h₁yód nos bʰéh₂os séngʷeti h₂ew ne gʷm̥sḱómes. ǵn̥h₁yómesdʰh₂ mr̥yómesdʰh₂-kʷe. ḱléwos ne mért ń̥dʰgʷʰitom ḱléwos h₁ésti.
- new PIE: nu bʰéh₂os séngʷt h₂ew-kʷe h₁ludʰét. nu dʰoHnéh₂ ní séngʷt nu-kʷe h₂wékst. h₁yód bʰéh₂os séngʷeti h₂ew ne gʷm̥sḱómes. ǵn̥h₁yómesdʰh₂ mr̥yómesdʰh₂. ḱléwos ne mért ń̥dʰgʷʰitom ḱléwos h₁ésti.
- old English: The light goes down and comes again. The grain sinks down and grows. When our light has set, we do not come again. We are born, and we die. Fame does not die, imperishable fame remains.
- new English: The light goes down and comes again. The grain sinks down and grows. When the light has set, we do not come again. We are born, we die. Fame does not die, imperishable fame remains.

### t032-0036
- edits: c0 particle None->nu; c1 particle None->nu; c4 particle None->nu; c5 particle None->nu; c6 particle None->nu; c7 particle None->nu; c8 drop POSS closed:personal/1
- old PIE: ǵʰoysós h₁mé gʰbʰéli térh₃t. méne h₁ésh₂r̥ h₁éǵʰs h₁éyti. ní ḱéyh₂er h₁regʷesyéti-kʷe. kʷŕ̥meyes méne h₃ésth₁h₂ gʷr̥h₃ṓnti. méne swesréy mluHdʰí ǵʰoysóh₁ séngʷt. mē HréwdHs méne h₁nómn̥ ḱlutóm h₁éseti.
- new PIE: nu ǵʰoysós h₁mé gʰbʰéli térh₃t. nu méne h₁ésh₂r̥ h₁éǵʰs h₁éyti. ní ḱéyh₂er h₁regʷesyéti-kʷe. nu kʷŕ̥meyes méne h₃ésth₁h₂ gʷr̥h₃ṓnti. nu méne swesréy mluHdʰí nu ǵʰoysóh₁ séngʷt. nu mē HréwdHs h₁nómn̥ ḱlutóm h₁éseti.
- old English: The spear wounded me in the head. My blood goes out. I lie down, and it is getting dark. The worms will eat my bones. Tell my sister: he fell by the spear. Do not cry out; my name shall be famous.
- new English: The spear wounded me in the head. My blood goes out. I lie down, and it is getting dark. The worms will eat my bones. Tell my sister: he fell by the spear. Do not cry out; the name shall be famous.

### t032-0037
- edits: c0 particle None->nu; c1 particle None->nu; c4 conj -kʷe kʷe->None; c5 particle None->nu; c7 particle None->nu
- old PIE: ne h₂wérst lóyseh₂ térst dʰoHnéh₂ ne bʰwéh₂t. ǵʰwḗres tr̥syónti tr̥syómes-kʷe. upó spéḱyomes n̥smé mē linékʷs. pérkʷune ne h₂wérseti? ḱm̥h₂mé wéyHs-kʷe nos lelóykʷe.
- new PIE: nu ne h₂wérst nu lóyseh₂ térst dʰoHnéh₂ ne bʰwéh₂t. ǵʰwḗres tr̥syónti tr̥syómes. nu upó spéḱyomes n̥smé mē linékʷs. nu pérkʷune ne h₂wérseti? ḱm̥h₂mé wéyHs-kʷe nos lelóykʷe.
- old English: It has not rained, the furrow has dried up, the grain does not grow. The wild beasts are thirsty, and we are thirsty. We look up, do not leave us. Perkunos, will it not rain? We have grown tired, and our strength is gone.
- new English: It has not rained, the furrow has dried up, the grain does not grow. The wild beasts are thirsty, we are thirsty. We look up, do not leave us. Perkunos, will it not rain? We have grown tired, and our strength is gone.

### t032-0038
- edits: c0 add MOD swos; c0 particle None->nu; c1 drop POSS closed:personal/1; c1 particle None->nu; c5 conj -kʷe None->kʷe; c7 particle None->nu
- old PIE: mr̥tós méne ph₂tḗr. n̥ḱéwih₂ méne swésōr méne sédos stéwdt. nu kʷís h₁mé péh₂seti kʷís h₁mé wédʰēti? nu kʷís h₁mé woséyēti? nu pró h₁éyoh₂ HréwdHoh₂-kʷe.
- new PIE: nu mr̥tós méne swós ph₂tḗr. nu n̥ḱéwih₂ swésōr méne sédos stéwdt. nu kʷís h₁mé péh₂seti kʷís h₁mé wédʰēti? nu-kʷe kʷís h₁mé woséyēti? nu pró h₁éyoh₂ nu-kʷe HréwdHoh₂.
- old English: Dead is my father. Dead is my sister, my seat has grown cold. Now who shall protect me, who shall lead me? Now who shall clothe me? Then I shall go forth and cry out.
- new English: Dead is my own father. Dead is the sister, my seat has grown cold. Now who shall protect me, who shall lead me? And now who shall clothe me? Then I shall go forth and cry out.

### t032-0039
- edits: c0 drop POSS closed:personal/1; c0 particle None->nu; c2 particle None->nu; c2 conj -kʷe None->kʷe; c4 particle None->nu; c6 drop POSS closed:personal/2; c6 particle None->nu; c7 particle None->nu
- old PIE: dʰéǵʰom méne bʰréh₂term̥ h₁áyso h₁ím h₂lékse. bʰréh₂ter pr̥kʷéwi Hn̥dʰí l̥gʰdʰí. pr̥kʷéws wréh₂des téwe h₃ésth₁h₂ térdonti. péruti h₂wéks nu Hn̥dʰí légʰyesi. pérkʷunos téwe h₁nómn̥ widyéh₁t. téwe h₁nómn̥ mē n̥ḱyéh₁t.
- new PIE: nu dʰéǵʰom bʰréh₂term̥ h₁áyso h₁ím h₂lékse. nu-kʷe bʰréh₂ter pr̥kʷéwi Hn̥dʰí l̥gʰdʰí. pr̥kʷéws wréh₂des téwe h₃ésth₁h₂ térdonti. nu péruti h₂wéks nu Hn̥dʰí légʰyesi. nu pérkʷunos h₁nómn̥ widyéh₁t. nu téwe h₁nómn̥ mē n̥ḱyéh₁t.
- old English: Earth, receive my brother, protect him. Lie down, brother, under the oak. The roots of the oak shall bore through your bones. Last year you grew tall, now you lie below. May Perkunos know your name. May your name not vanish.
- new English: Earth, receive the brother, protect him. And lie down, brother, under the oak. The roots of the oak shall bore through your bones. Last year you grew tall, now you lie below. May Perkunos know the name. May your name not vanish.

### t032-0040
- edits: c1 particle None->nu; c5 particle nu->None; c6 particle nu->None; c6 merge (break True->False); c7 particle None->nu
- old PIE: wíh₁re HeHḱéwes h₁éḱwōs dʰwóri stesth₂ḗr. tr̥ménti h₂eǵós-kʷe séngʷt. téwe ǵʰoysós séngʷt téwe Hróth₂os Hrumptó. nu kʷís h₁íns yéwgeti? nu kʷís Hróth₂om h₂éǵēti? wíh₁re l̥gʰdʰí téwe h₁nómn̥ méǵh₂.
- new PIE: wíh₁re HeHḱéwes h₁éḱwōs dʰwóri stesth₂ḗr. nu tr̥ménti h₂eǵós-kʷe séngʷt. téwe ǵʰoysós séngʷt téwe Hróth₂os Hrumptó. kʷís h₁íns yéwgeti kʷís Hróth₂om h₂éǵēti? nu wíh₁re l̥gʰdʰí téwe h₁nómn̥ méǵh₂.
- old English: Man, the swift horses stand at the door. They tremble, and the driver has fallen. Your spear has fallen, your chariot is broken. Now who shall yoke them? Now who shall drive the chariot? Lie down, man, your name is great.
- new English: Man, the swift horses stand at the door. They tremble, and the driver has fallen. Your spear has fallen, your chariot is broken. Who shall yoke them? Who shall drive the chariot? Lie down, man, your name is great.
