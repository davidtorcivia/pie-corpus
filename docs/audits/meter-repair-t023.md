# Meter repair: t023

meter_exact before: 30/125 = 0.240 (census); after: 121/125 = 0.968. Gate: PASS (all gates true; max_lexeme_uses 6).

Edit types: particle (nu/ge add or drop), conj (-kʷe add or drop), drop (vocative/possessor/epithet/adverb removed), epithet (adjective added), vocative (added), number (none used). No split/merge edits. Epithets were added only where the adjective fits the noun, within the per-lexeme cap. Plan edit lines below are `cN [clause content]: change` (clause index 0-based). Slot head/dep indices were verified after the edits: every head/dep link in a changed plan still points at the same lexeme as before (the added-vocative renumbering bug in meter_report was avoided by shifting head/dep after each vocative insert; no misdirected index found, no fixes needed).

## Changed texts

### t023-0001 (charm)

Edits:
    c0 [VOC:worm SUBJ:closed:relative_yo OBJ:bone V:to eat MOD:big->worm]: ADD MOD:big->worm
    c2 [VOC:worm SUBJ:closed:relative_yo OBJ:blood V:to drink]: particle:None->ge
    c4 [SUBJ:fire (the element OBJ:closed:personal/2 V:to burn]: conj:None->kʷe
    c5 [SUBJ:sun OBJ:closed:personal/2 V:to be drying (transitive]: particle:None->nu
    c7 [ABL:sinew V:to come forth]: DROP ADV:h1egjhs

Verse lines changed (old -> new, syllables):

- L1: `kʷŕ̥mey h₁yós h₃ésth₁ h₁ḗdsi mr̥dʰí` (9) -> `méǵh₂ kʷŕ̥mey h₁yós h₃ésth₁ h₁ḗdsi mr̥dʰí` (11)
- L2: `kʷŕ̥mey h₁yós h₁ésh₂r̥ píph₃esi n̥ḱdʰí` (10) -> `kʷŕ̥mey-ge h₁yós h₁ésh₂r̥ píph₃esi n̥ḱdʰí` (11)
- L3: `nu péh₂wr̥ twé dʰégʷʰetu` (7) -> `nu-kʷe péh₂wr̥ twé dʰégʷʰetu` (8)
- L4: `sóh₂wl̥ twé h₂sowséyetu` (7) -> `nu sóh₂wl̥ twé h₂sowséyetu` (8)
- L5: `h₁pyéh₁t h₂éwis twé sn̥h₁wéns h₁éǵʰs h₁n̥dʰdʰí` (9) -> `h₁pyéh₁t h₂éwis twé sn̥h₁wéns h₁n̥dʰdʰí` (8)

English old: Worm, you who eat the bone, die! Worm, you who drink the blood, vanish! Then let fire burn you, let the sun dry you. Let the bird seize you. Come out of the sinew! Come out of the bone! Do not devour the sinew.

English new: Great worm, you who eat the bone, die! Worm, you who indeed drink the blood, vanish! And then let fire burn you; then let the sun dry you. Let the bird seize you. Come from the sinew! Come out of the bone! Do not devour the sinew.

### t023-0002 (charm)

Edits:
    c2 [SUBJ:blood INS:blood V:to be joining]: particle:nu->None
    c4 [SUBJ:bone V:to break (something)]: DROP MOD:closed:relative_yo->bone
    c6 [VOC:earth APPOS:mother->earth OBJ:narrowness ABL:bone V:to give (active) MOD:big->earth]: ADD MOD:big->earth
    c9 [V:to be walking]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L2: `h₃ésth₁ h₃sth₁éh₁ yungih₁tó nu h₁ésh₂r̥ h₁sh₂énh₁ yungih₁tó` (14) -> `h₃ésth₁ h₃sth₁éh₁ yungih₁tó h₁ésh₂r̥ h₁sh₂énh₁ yungih₁tó` (13)
- L4: `h₁yód h₃ésth₁ Hrumptó tód h₂ew sth₂éh₁yoyh₁t` (9) -> `h₃ésth₁ Hrumptó tód h₂ew sth₂éh₁yoyh₁t` (8)
- L5: `dʰéǵʰom méh₂ter h₂énǵʰos h₃sth₁és h₁áyso` (9) -> `méǵh₂i dʰéǵʰom méh₂ter h₂énǵʰos h₃sth₁és h₁áyso` (11)
- L6: `h₁yós ḱéyor stéh₂tu gʷm̥sḱétu-kʷe` (9) -> `h₁yós ḱéyor stéh₂tu gʷm̥sḱétu` (8)

English old: Now: bone, blood and sinew. Let bone be joined with bone. Then let blood be joined with blood. Let sinew be joined with sinew. The bone that broke, let it stand up again. Mother Earth, take the pain from the bone. Let him who lies there stand up and walk.

English new: Now: bone, blood and sinew. Let bone be joined with bone. Let blood be joined with blood. Let sinew be joined with sinew. The bone broke; let it stand up again. Great Mother Earth, take the pain from the bone. Let him who lies there stand up; let him walk.

### t023-0003 (charm)

Edits:
    c1 [VOC:blood V:to go]: DROP ADV:h1egjhs
    c2 [SUBJ:spear MOD:closed:relative_yo->spear OBJ:closed:personal/2 V:to wound]: particle:None->nu
    c4 [SUBJ:blood MOD:to be red->blood LOC:sinew V:to stand]: particle:None->ge
    c6 [OBJ:closed:anaphoric_i V:to be protecting]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `h₁ésh₂r̥ sth₂dʰí h₁ésh₂r̥ h₁éǵʰs mē gʷéh₂s` (9) -> `h₁ésh₂r̥ sth₂dʰí h₁ésh₂r̥ mē gʷéh₂s` (8)
- L2: `h₁yós ǵʰoysós twé térh₃t só Hrumpih₁tó` (10) -> `nu h₁yós ǵʰoysós twé térh₃t só Hrumpih₁tó` (11)
- L3: `h₁rudʰéh₁n̥t kréwh₂s sn̥h₁wéni sth₂éh₁yoyh₁t` (10) -> `h₁rudʰéh₁n̥t-ge kréwh₂s sn̥h₁wéni sth₂éh₁yoyh₁t` (11)
- L5: `h₁ím h₂lékse h₁éy-kʷe Hwr̥dʰyéh₁t` (7) -> `nu h₁ím h₂lékse h₁éy-kʷe Hwr̥dʰyéh₁t` (8)

English old: Blood, stand still! Blood, do not go out! The spear that wounded you, let it be broken. Let the red blood stand in the sinew. Father Sky, hear this word! Protect him, and let him become strong!

English new: Blood, stand still! Blood, do not go! Now the spear that wounded you, let it be broken. Let the red blood indeed stand in the sinew. Father Sky, hear this word! Now protect him, and let him become strong!

### t023-0004 (charm)

Edits:
    c1 [SUBJ:closed:anaphoric_i LOC:bone V:to become cold MOD:big->bone]: ADD MOD:big->bone
    c3 [SUBJ:something warm V:to flee]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L2: `h₁íd h₃sth₁í studyéh₁t gʷm̥yétu sríHgos` (9) -> `h₁íd méǵh₂i h₃sth₁í studyéh₁t gʷm̥yétu sríHgos` (11)
- L3: `gʷʰr̥nós bʰéwgtu swidyétu` (7) -> `nu gʷʰr̥nós bʰéwgtu swidyétu` (8)

English old: Fire in the bones, run into the water! Let it grow cold in the bone. Let the cold come, let what is warm flee. Let him sweat, let him drink and be satisfied. Let him not tremble.

English new: Fire in the bones, run into the water! Let it grow cold in the great bone. Let the cold come, then let what is warm flee. Let him sweat, let him drink and be satisfied. Let him not tremble.

### t023-0005 (charm)

Edits:
    c0 [VOC:heart V:to be trembling MOD:big->heart]: ADD MOD:big->heart
    c2 [VOC:narrowness ABL:heart ADV:h1egjhs V:to go]: particle:None->ge
    c4 [SUBJ:sleep IO:closed:anaphoric_i V:to step]: conj:None->kʷe
    c5 [SUBJ:tear (in the eyes)(PL) V:to dry up]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `ḱḗr mē tréms ḱḗr mē bʰéyh₂s` (6) -> `méǵh₂ ḱḗr mē tréms ḱḗr mē bʰéyh₂s` (8)
- L2: `h₂énǵʰos ḱr̥dés h₁éǵʰs gʷh₂dʰí` (7) -> `h₂énǵʰos-ge ḱr̥dés h₁éǵʰs gʷh₂dʰí` (8)
- L4: `nu gʷm̥yéh₁t swépnos h₁ésmey` (7) -> `nu-kʷe gʷm̥yéh₁t swépnos h₁ésmey` (8)
- L5: `dáḱruh₂ tr̥syéh₁t nu mudyéh₁t` (7) -> `dáḱruh₂-ge tr̥syéh₁t nu mudyéh₁t` (8)

English old: Heart, do not tremble! Heart, do not be afraid! Grief, go out of the heart. Dawn and Sun, drive the grief out of the heart. Then let sleep come to him. Let the tears dry up. Now let him become joyful.

English new: Great heart, do not tremble! Heart, do not be afraid! Grief, indeed go out of the heart. Dawn and Sun, drive the grief out of the heart. And then let sleep come to him. Let the tears indeed dry up. Now let him become joyful.

### t023-0006 (charm)

Edits:
    c2 [V:to grow (up)]: conj:kʷe->None
    c5 [SUBJ:narrowness GOAL:wolf V:to go]: conj:None->kʷe
    c6 [SUBJ:wild animal OBJ:closed:anaphoric_i V:to eat MOD:big->wild animal]: ADD MOD:big->wild animal
    c8 [VOC:sky OBJ:overpowering IO:closed:anaphoric_i V:to give]: particle:None->nu DROP APPOS:giver->sky,POSS:good->giver(PL)

Verse lines changed (old -> new, syllables):

- L1: `súHnew mē mérs gʷíh₃we h₂uksdʰí-kʷe` (9) -> `súHnew mē mérs gʷíh₃we h₂uksdʰí` (8)
- L4: `nu h₁éytu h₂énǵʰos wĺ̥kʷom` (7) -> `nu-kʷe h₁éytu h₂énǵʰos wĺ̥kʷom` (8)
- L5: `ǵʰwḗr h₁íd h₁ḗdtu gʷh₂te h₁ím dʰgʷʰh₂dʰí` (9) -> `méǵh₂s ǵʰwḗr h₁íd h₁ḗdtu gʷh₂te h₁ím dʰgʷʰh₂dʰí` (11)
- L6: `dyéw h₁uséwōm déh₃tor h₁ésmey séǵʰos dh₃dʰí` (12) -> `nu dyéw h₁ésmey séǵʰos dh₃dʰí` (8)

English old: Son, do not die! Live and grow! Your mother protects you. May Sky and Earth guard you. Then let the suffering go to the wolf. Let the wild beast eat it. Death, pass him by! Dyeus, giver of good things, give him power.

English new: Son, do not die! Live; grow! Your mother protects you. May Sky and Earth guard you. And then let the suffering go to the wolf. Let the great wild beast eat it. Death, pass him by! Now, Dyeus, give him power.

### t023-0007 (charm)

Edits:
    c1 [OBJ:livestock V:to guard]: DROP VOC:dog
    c3 [SUBJ:wild animal ADV:h2enti V:to go to]: particle:None->ge conj:None->kʷe
    c4 [SUBJ:wool V:to be becoming]: particle:None->nu
    c6 [SUBJ:sheep(PL) V:to fill oneself]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `wĺ̥kʷe wr̥h₁énm̥ mē lémbʰs ḱwón péḱu ph₂sdʰí` (12) -> `wĺ̥kʷe wr̥h₁énm̥ mē lémbʰs péḱu ph₂sdʰí` (11)
- L3: `mē h₁r̥sḱóyh₁t ǵʰwḗr h₂énti` (6) -> `mē-kʷe-ge h₁r̥sḱóyh₁t ǵʰwḗr h₂énti` (8)
- L4: `h₂wĺ̥h₁neh₂ bʰuHyóyh₁t ḱwón bʰéwdʰe` (7) -> `nu h₂wĺ̥h₁neh₂ bʰuHyóyh₁t ḱwón bʰéwdʰe` (8)
- L5: `nu h₂óweyes pl̥h₁ih₁ént` (7) -> `nu-kʷe h₂óweyes pl̥h₁ih₁ént` (8)

English old: Wolf, do not seize the lamb! Dog, guard the herd. Shepherd, lead the cattle home. Let the wild beast not come near. Let the wool grow. Dog, be awake. Now let the sheep grow full.

English new: Wolf, do not seize the lamb! Guard the herd. Shepherd, lead the cattle home. And let the wild beast indeed not come near. Then let the wool grow. Dog, be awake. And now let the sheep grow full.

### t023-0008 (charm)

Edits:
    c1 [OBJ:man V:to seize]: DROP MOD:closed:deictic_ki->man
    c2 [VOC:snake SUBJ:closed:relative_yo LOC:night V:to be creeping]: particle:None->ge
    c4 [VOC:Perkʷunos OBJ:snake INS:spear POSS:closed:personal/2->spear V:to be pushing]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `h₁ógʷʰey l̥gʰdʰí ḱóm wiHróm mē lémbʰs` (9) -> `h₁ógʷʰey l̥gʰdʰí wiHróm mē lémbʰs` (8)
- L2: `h₁ógʷʰey h₁yós kʷsépi sérpesi mē stéh₂s` (10) -> `h₁ógʷʰey-ge h₁yós kʷsépi sérpesi mē stéh₂s` (11)
- L3: `pérkʷune toy h₁ógʷʰim ǵʰoysóh₁ stunddʰí` (10) -> `nu toy pérkʷune h₁ógʷʰim ǵʰoysóh₁ stunddʰí` (11)

English old: Snake, lie down! Do not seize this man! Snake, you who creep in the night, do not rise! Perkunos, strike the snake with your spear. Snake, flee! Now let the snake go away.

English new: Snake, lie down! Do not seize the man! Snake, you who indeed creep in the night, do not rise! Now, Perkunos, strike the snake with your spear. Snake, flee! Now let the snake go away.

### t023-0009 (charm)

Edits:
    c0 [NP:sleep APPOS:brother->sleep POSS:death->brother]: particle:None->ge
    c2 [SUBJ:dog V:to be lying down MOD:good->dog]: ADD MOD:good->dog
    c6 [LOC:night V:to step]: DROP VOC:thief
    c8 [LOC:dawn V:to wake up]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `swépne gʷh₂tósyo bʰréh₂ter` (7) -> `swépne-ge gʷh₂tósyo bʰréh₂ter` (8)
- L2: `gʷm̥dʰí ḱwṓ légʰyoyh₁t h₂ówis légʰyoyh₁t` (9) -> `gʷm̥dʰí h₁wésus ḱwṓ légʰyoyh₁t h₂ówis légʰyoyh₁t` (11)
- L4: `bʰór nékʷti mē gʷéms nókʷt nos ḱéle` (9) -> `nékʷti mē gʷéms nókʷt nos ḱéle` (8)
- L5: `nu h₂usési bʰudʰih₁mé` (7) -> `nu-kʷe h₂usési bʰudʰih₁mé` (8)

English old: Sleep, brother of death, come! Let the dog lie down, let the sheep lie down, let the bird lie down. Let the household lie down. Thief, do not come in the night. Night, cover us. Then may we wake at dawn.

English new: Sleep, brother of death, indeed come! Let the good dog lie down, let the sheep lie down, let the bird lie down. Let the household lie down. Do not come in the night. Night, cover us. And then may we wake at dawn.

### t023-0010 (charm)

Edits:
    c3 [SUBJ:grease OBJ:arm V:to heal]: particle:None->nu
    c4 [VOC:cold GOAL:arm V:to go to]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L3: `smérus bʰeh₂ǵʰúm mḗdetu` (7) -> `nu smérus bʰeh₂ǵʰúm mḗdetu` (8)
- L4: `sríHgos bʰeh₂ǵʰúm h₁r̥sḱé bʰeh₂ǵʰús Hwr̥dʰyéh₁t` (10) -> `sríHgos-ge bʰeh₂ǵʰúm h₁r̥sḱé bʰeh₂ǵʰús Hwr̥dʰyéh₁t` (11)

English old: The fire burned the man's arm. Let the arm grow cold. Smear the grease on the arm. Let the grease heal the arm. Cold, go to the arm. Let the arm become strong.

English new: The fire burned the man's arm. Let the arm grow cold. Smear the grease on the arm. Now let the grease heal the arm. Cold, indeed go to the arm. Let the arm become strong.

### t023-0011 (charm)

Edits:
    c0 [VOC:fat V:to become full]: particle:None->ge
    c2 [VOC:fat V:to melt]: conj:None->kʷe
    c3 [SUBJ:water OBJ:fat ADV:h2epo V:to be carrying MOD:swift->water]: ADD MOD:swift->water
    c4 [SUBJ:cold OBJ:fat V:to seize]: particle:None->nu conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `péyh₂wr̥ mē pléh₁dʰes péyh₂wr̥ ní gʷh₂dʰí` (10) -> `péyh₂wr̥-ge mē pléh₁dʰes péyh₂wr̥ ní gʷh₂dʰí` (11)
- L2: `nu péyh₂wr̥ tinh₁dʰí` (6) -> `nu-kʷe péyh₂wr̥ tinh₁dʰí` (7)
- L3: `wódr̥ péyh₂wr̥ h₂epó bʰéretu` (9) -> `HeHḱú wódr̥ péyh₂wr̥ h₂epó bʰéretu` (11)
- L4: `sríHgos péyh₂wr̥ lémbʰtu` (6) -> `nu-kʷe sríHgos péyh₂wr̥ lémbʰtu` (8)

English old: Swelling, do not swell! Swelling, go down! Swelling, now melt! Let the water carry the swelling away. Let the cold seize the swelling. Let the wild beast devour the swelling. Let him live.

English new: Swelling, indeed do not swell! Swelling, go down! And now, swelling, melt! Let the swift water carry the swelling away. And then let the cold seize the swelling. Let the wild beast devour the swelling. Let him live.

### t023-0012 (charm)

Edits:
    c0 [SUBJ:closed:interrogative_kwi OBJ:closed:personal/2 V:to wound]: particle:None->ge
    c2 [SUBJ:spear OBJ:closed:personal/1 V:to wound]: particle:None->nu
    c6 [SUBJ:bone V:to grow]: particle:nu->None

Verse lines changed (old -> new, syllables):

- L1: `kʷís twé térh₃t kʷís toy h₃ésth₁ skélHt` (10) -> `kʷís-ge twé térh₃t kʷís toy h₃ésth₁ skélHt` (11)
- L2: `ǵʰoysós h₁mé térh₃t skélHt ǵʰoysós h₁íd` (10) -> `nu ǵʰoysós h₁mé térh₃t skélHt ǵʰoysós h₁íd` (11)
- L4: `nu h₃ésth₁ bʰuh₂yéh₁t wíHre sth₂dʰí` (9) -> `h₃ésth₁ bʰuh₂yéh₁t wíHre sth₂dʰí` (8)

English old: Who wounded you? Who split your bone? The spear wounded me. The spear split it. I heal you; I smear the grease. Then let the bone grow. Man, stand up!

English new: Who indeed wounded you? Who split your bone? Then the spear wounded me. The spear split it. I heal you; I smear the grease. Let the bone grow. Man, stand up!

### t023-0013 (charm)

Edits:
    c0 [SUBJ:closed:relative_yo OBJ:wheel POSS:sun->wheel V:to be driving]: particle:None->nu DROP VOC:dawn
    c2 [ADV:h2epo V:to go (away)]: DROP VOC:night
    c4 [SUBJ:bird V:to wake up]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `h₂éwsos h₁yéh₂ sh₂wéns kʷékʷlom h₂éǵesi h₂usdʰí` (12) -> `nu h₁yéh₂ sh₂wéns kʷékʷlom h₂éǵesi h₂usdʰí` (11)
- L2: `nókʷt h₂epó litdʰí h₂énǵʰos témHesh₁ bʰéwgtu` (12) -> `h₂epó litdʰí h₂énǵʰos témHesh₁ bʰéwgtu` (11)
- L3: `h₂éwis bʰudʰyéh₁t nu te widóyh₁t h₂éwsos` (10) -> `h₂éwis-ge bʰudʰyéh₁t nu te widóyh₁t h₂éwsos` (11)

English old: Dawn, you who drive the wheel of the sun, shine! Night, go away! Let the suffering flee with the darkness. Let the bird wake. Now, Dawn, let him see you.

English new: Now, you who drive the wheel of the sun, shine! Go away! Let the suffering flee with the darkness. Let the bird indeed wake. Now, Dawn, let him see you.

### t023-0014 (charm)

Edits:
    c2 [SUBJ:god(PL) OBJ:closed:anaphoric_i V:to cause to grow old]: particle:None->nu
    c3 [OBJ:closed:anaphoric_i V:to be looking at]: DROP VOC:sun
    c4 [SUBJ:stallion(PL) V:to be becoming]: DROP MOD:his/her/their own (refle->stallion

Verse lines changed (old -> new, syllables):

- L2: `ǵorh₂éyoyh₁ent deywṓs h₁ím sóh₂wl̥ h₁ím spéḱye` (12) -> `nu ǵorh₂éyoyh₁ent deywṓs h₁ím h₁ím spéḱye` (11)
- L3: `swṓs h₁éḱwōs bʰuHyóyh₁ent pḱúh₁ h₃pusyéh₁t` (9) -> `h₁éḱwōs bʰuHyóyh₁ent pḱúh₁ h₃pusyéh₁t` (8)

English old: Let him live a hundred years! Let death pass him by. Let the gods make him grow old. Sun, look on him. Let his horses grow. May he become rich in livestock.

English new: Let him live a hundred years! Let death pass him by. Then let the gods make him grow old. Look on him. Let the horses grow. May he become rich in livestock.

### t023-0015 (lament)

Edits:
    c3 [LOC:field V:to be lying flat]: particle:None->nu
    c5 [SUBJ:narrowness OBJ:mistress POSS:closed:personal/2->mistress V:to grasp]: conj:None->kʷe
    c7 [SUBJ:that which is heard POSS:closed:personal/2->that which is heard PRED:imperishable]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L2: `h₂éǵroy ḱéyth₂er swésōr toy HréwdHti` (10) -> `nu h₂éǵroy ḱéyth₂er swésōr toy HréwdHti` (11)
- L3: `h₁épt-ge toy h₂énǵʰos pótnih₂m` (7) -> `h₁épt-kʷe-ge toy h₂énǵʰos pótnih₂m` (8)
- L5: `nu toy ḱléwos ń̥dʰgʷʰitom` (7) -> `nu-kʷe toy ḱléwos ń̥dʰgʷʰitom` (8)

English old: Hero, you who drove cattle, you who overpowered the snake, you have died. You lie in the field. Your sister weeps. Grief indeed has seized your wife. We clothe you in a garment. Now your fame is imperishable.

English new: Hero, you who drove cattle, you who overpowered the snake, you have died. Now you lie in the field. Your sister weeps. And grief indeed has seized your wife. We clothe you in a garment. And now your fame is imperishable.

### t023-0016 (lament)

Edits:
    c2 [SUBJ:closed:personal/2 PRED:heart POSS:closed:personal/1->heart]: conj:kʷe->None
    c4 [LOC:night OBJ:closed:personal/2 V:to cry (vocally)]: particle:nu->None
    c5 [VOC:earth APPOS:mother->earth OBJ:son POSS:closed:personal/1->son V:to give (active)]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `súHnew h₁mé linékʷs h₂élom te túH-kʷe moy ḱḗr` (12) -> `súHnew h₁mé linékʷs h₂élom te túH moy ḱḗr` (11)
- L2: `kapyóh₂ toy wésmn̥ nu te nékʷti HréwdHmi` (12) -> `kapyóh₂ toy wésmn̥ nékʷti te HréwdHmi` (11)
- L3: `dʰéǵʰom méh₂ter méne suHnúm h₁áyso` (10) -> `nu dʰéǵʰom méh₂ter méne suHnúm h₁áyso` (11)

English old: Son, you left me. I nursed you, and you are my heart. I hold your garment. Now I weep for you by night. Mother Earth, take my son.

English new: Son, you left me. I nursed you; you are my heart. I hold your garment. I weep for you by night. Now, Mother Earth, take my son.

### t023-0017 (lament)

Edits:
    c2 [OBJ:sister POSS:closed:personal/2->sister V:to be protecting]: conj:None->kʷe
    c6 [V:to cry (vocally)]: conj:kʷe->None
    c7 [SUBJ:name POSS:closed:personal/2->name PRED:heard LOC:man(PL)]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L2: `nu toy h₂lékses swésorm̥` (7) -> `nu-kʷe toy h₂lékses swésorm̥` (8)
- L4: `témHesi sédyoh₂ túH mr̥wós HréwdHmi-kʷe` (12) -> `témHesi sédyoh₂ túH mr̥wós HréwdHmi` (11)
- L5: `h₁nómn̥ toy h₂nr̥sú ḱlutóm` (7) -> `h₁nómn̥-ge toy h₂nr̥sú ḱlutóm` (8)

English old: Brother, you drove the cattle and you gave me a share. Then you protected your sister. Who now gives me a share? I sit in the darkness. You are dead, and I weep. Your name is famous among men.

English new: Brother, you drove the cattle and you gave me a share. And then you protected your sister. Who now gives me a share? I sit in the darkness. You are dead; I weep. Your name is indeed famous among men.

### t023-0018 (lament)

Edits:
    c0 [VOC:father OBJ:closed:personal/1(PL) V:to pull]: particle:None->ge
    c2 [OBJ:closed:personal/1(PL) V:to be protecting]: particle:None->ge
    c5 [V:to be sitting]: particle:nu->None
    c8 [OBJ:closed:personal/1(PL) V:to lead]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `ph₂ter nos déwks h₁éḱwons-kʷe nos dédeh₃s` (10) -> `ph₂ter-ge nos déwks h₁éḱwons-kʷe nos dédeh₃s` (11)
- L2: `h₂lékses nos memn̥mé te` (7) -> `h₂lékses-ge nos memn̥mé te` (8)
- L3: `sríHgos nos lémbʰt nu sédyomes HrudHmés-kʷe` (12) -> `sríHgos nos lémbʰt sédyomes HrudHmés-kʷe` (11)
- L4: `nu nos kʷís bʰéh₂ti wédʰeti-kʷe nos` (10) -> `nu nos kʷís bʰéh₂ti nu-kʷe nos wédʰeti` (11)

English old: Father, you led us and gave us horses. You protected us; we remember you. Cold has seized us. Now we sit and cry. Who now speaks for us and leads us?

English new: Father, you indeed led us and gave us horses. You indeed protected us; we remember you. Cold has seized us. We sit and cry. Who now speaks for us and then leads us?

### t023-0019 (lament)

Edits:
    c1 [ADV:h2ew V:to step]: conj:kʷe->None
    c4 [LOC:village V:to be getting dark]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `wíHre h₂epó h₁éys h₂ew-kʷe ne gʷéms` (9) -> `wíHre h₂epó h₁éys h₂ew ne gʷéms` (8)
- L3: `nu h₁regʷesyéti ḱóymoy` (7) -> `nu-kʷe h₁regʷesyéti ḱóymoy` (8)

English old: Husband, you went away, and you did not come back. I wear your garment, and I look at your yoke. Now it is getting dark in the household. I seek you, and I remember you.

English new: Husband, you went away; you did not come back. I wear your garment, and I look at your yoke. And now it is getting dark in the household. I seek you, and I remember you.

### t023-0020 (lament)

Edits:
    c0 [VOC:king APPOS:shepherd->king POSS:man->shepherd(PL) V:to die]: particle:None->ge
    c2 [IO:closed:personal/1(PL) OBJ:reward(PL) V:to be giving]: conj:kʷe->None
    c3 [V:to be sitting ADV:h2mbhi OBJ:closed:personal/2]: particle:None->nu
    c4 [SUBJ:dawn V:to become bright]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `h₃réǵ h₂n̥rṓm póh₂imen mérs` (7) -> `h₃réǵ-ge h₂n̥rṓm póh₂imen mérs` (8)
- L2: `h₂lékses nos misdʰóns-kʷe nos dédeh₃s` (9) -> `h₂lékses nos misdʰóns nos dédeh₃s` (8)
- L3: `sédyomes te h₂m̥bʰí h₂éwsōs léwkt` (9) -> `nu te sédyomes h₂m̥bʰí nu h₂éwsōs léwkt` (11)

English old: King, shepherd of men, you have died. You guarded us and gave us rewards. We sit around you. Dawn shines, but you do not stand up. Who is our king now?

English new: King, shepherd of men, you have indeed died. You guarded us; you gave us rewards. Now we sit around you. Then Dawn shines, but you do not stand up. Who is our king now?

### t023-0021 (lament)

Edits:
    c0 [VOC:shepherd LOC:field V:to be lying flat]: particle:None->nu DROP MOD:dead->shepherd
    c2 [V:to cry (vocally)]: conj:kʷe->None
    c3 [V:to be getting dark]: particle:nu->None
    c6 [SUBJ:closed:indefinite_kwi OBJ:closed:anaphoric_i(PL) V:to guard]: conj:kʷe->None
    c7 [SUBJ:name POSS:closed:personal/2->name PRED:heard LOC:man(PL)]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `mŕ̥we póh₂imen h₂éǵroy ḱéyth₂er` (9) -> `nu póh₂imen h₂éǵroy ḱéyth₂er` (8)
- L2: `ḱwṓ toy sédyeti HréwdHti-kʷe` (9) -> `ḱwṓ toy sédyeti HréwdHti` (8)
- L3: `nu h₁regʷesyéti ne h₁édn̥ti h₂óweyes` (12) -> `h₁regʷesyéti ne h₁édn̥ti h₂óweyes` (11)
- L4: `wĺ̥kʷos h₁r̥sḱéti h₁íh₂n̥s-kʷe kʷis ne péh₂sti` (12) -> `wĺ̥kʷos h₁r̥sḱéti h₁íh₂n̥s kʷis ne péh₂sti` (11)
- L5: `h₁nómn̥ toy h₂nr̥sú ḱlutóm` (7) -> `nu toy h₁nómn̥ h₂nr̥sú ḱlutóm` (8)

English old: Dead shepherd, you lie in the field. Your dog sits and cries. Now it is getting dark; the sheep do not eat. The wolf approaches, and no one guards them. Your name is famous among men.

English new: Now, shepherd, you lie in the field. Your dog sits; it cries. It is getting dark; the sheep do not eat. The wolf approaches; no one guards them. Now your name is famous among men.

### t023-0022 (lament)

Edits:
    c6 [SUBJ:god(PL) OBJ:closed:personal/2 V:to give (active)]: particle:nu->None

Verse lines changed (old -> new, syllables):

- L4: `nu te deywṓs h₁áyn̥to h₁nómn̥ toy ḱlutóm` (12) -> `deywṓs te h₁áyn̥to h₁nómn̥ toy ḱlutóm` (11)

English old: Old father, you have died. You saw many years, and then you knew the words of the old. You led us. You sat down, and you spoke to us. Now the gods have taken you. Your name is famous.

English new: Old father, you have died. You saw many years, and then you knew the words of the old. You led us. You sat down, and you spoke to us. The gods have taken you. Your name is famous.

### t023-0023 (lament)

Edits:
    c0 [NP:son MOD:compound->son APPOS:swift->son]: particle:None->ge
    c3 [SUBJ:spear OBJ:closed:personal/2 V:to wound]: conj:kʷe->None
    c4 [SUBJ:blood MOD:to be red->blood LOC:field V:to be]: particle:None->nu conj:None->kʷe
    c5 [OBJ:closed:personal/2 V:to see]: conj:None->kʷe
    c7 [SUBJ:name PRED:heard]: DROP POSS:closed:personal/2->name

Verse lines changed (old -> new, syllables):

- L1: `h₁súḱlewes súHnew HéHḱew` (7) -> `h₁súḱlewes-ge súHnew HéHḱew` (8)
- L2: `ne ǵorh₂éyeth₂e dréms ǵʰoysós-kʷe te térh₃t` (12) -> `ne ǵorh₂éyeth₂e dréms ǵʰoysós te térh₃t` (11)
- L3: `h₁rudʰéh₁n̥t kréwh₂s h₂éǵroy h₁ésti` (9) -> `nu-kʷe h₁rudʰéh₁n̥t kréwh₂s h₂éǵroy h₁ésti` (11)
- L4: `nu te ne widéh₁yomes` (7) -> `nu-kʷe te ne widéh₁yomes` (8)
- L5: `gʷh₂tós te sléh₂gʷt h₁nómn̥ toy ḱlutóm` (9) -> `gʷh₂tós te sléh₂gʷt h₁nómn̥ ḱlutóm` (8)

English old: Son of good fame, swift one, you did not grow old. You ran, and the spear wounded you in the field. Your blood is red on the field. Now we do not see you. Death seized you. Your name is famous.

English new: Son of good fame, swift one, you indeed did not grow old. You ran; the spear wounded you in the field. And your blood is now red on the field. And now we do not see you. Death seized you. The name is famous.

### t023-0024 (lament)

Edits:
    c0 [VOC:guest GOAL:closed:personal/1(PL) V:to step]: particle:None->ge
    c2 [VOC:guest PRED:closed:interrogative_kwi SUBJ:one who begets POSS:closed:personal/2->one who begets]: particle:None->nu
    c3 [ADV:kudhe SUBJ:mother POSS:closed:personal/2->mother V:to be]: particle:None->ge
    c5 [OBJ:water IO:closed:personal/2 V:to give MOD:swift->water]: ADD MOD:swift->water
    c7 [VOC:earth OBJ:guest V:to give (active)]: particle:nu->None

Verse lines changed (old -> new, syllables):

- L1: `gʰóstey n̥smé gʷéms mérs-kʷe` (7) -> `gʰóstey-ge n̥smé gʷéms mérs-kʷe` (8)
- L2: `kʷís toy gʰóstey ǵénh₁tōr` (7) -> `nu toy kʷís gʰóstey ǵénh₁tōr` (8)
- L3: `méh₂tēr toy kúdʰe h₁ésti` (7) -> `méh₂tēr-ge toy kúdʰe h₁ésti` (8)
- L4: `sríHgos te h₁épt dh₃mé toy wódr̥` (9) -> `sríHgos te h₁épt dh₃mé toy HeHḱú wódr̥` (11)
- L5: `h₁íd te ne mḗdet nu dʰéǵʰom gʰóstim h₁áyso` (12) -> `h₁íd te ne mḗdet dʰéǵʰom gʰóstim h₁áyso` (11)

English old: Stranger, you came to us and died. Stranger, who is your begetter? Where is your mother? Cold seized you. We gave you water, but it did not heal you. Now, Earth, take the stranger.

English new: Stranger, you indeed came to us and died. Now, stranger, who is your begetter? Where indeed is your mother? Cold seized you. We gave you swift water, but it did not heal you. Earth, take the stranger.

### t023-0025 (lament)

Edits:
    c1 [SUBJ:closed:demonstrative_so PRED:dead]: DROP VOC:stallion(DU),MOD:swift->stallion
    c4 [SUBJ:stallion(DU) OBJ:closed:anaphoric_i V:to be seeking]: conj:None->kʷe
    c5 [SUBJ:stallion(DU) V:to eat]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `h₁yós uh₃wé h₂éǵet HéHḱuh₁ h₁éḱwoh₁ só mr̥wós` (12) -> `h₁yós uh₃wé h₂éǵet só mr̥wós` (8)
- L3: `nu h₂isḱétes h₁éḱwoh₁ h₁ím` (7) -> `nu-kʷe h₂isḱétes h₁éḱwoh₁ h₁ím` (8)
- L4: `h₁éḱwoh₁ ne h₁édtes kʷékʷlos stestóh₂e` (10) -> `h₁éḱwoh₁-ge ne h₁édtes kʷékʷlos stestóh₂e` (11)

English old: He who drove you is dead, swift horses. You two stand at the yoke, and no one has yoked you. Now the horses look for him. The horses do not eat. The wheel stands still.

English new: He who drove you is dead. You two stand at the yoke, and no one has yoked you. And now the horses look for him. The horses indeed do not eat. The wheel stands still.

### t023-0026 (lament)

Edits:
    c1 [ADV:h2enti V:to be standing]: particle:None->nu
    c6 [OBJ:closed:personal/2 V:to think]: particle:None->ge
    c7 [SUBJ:that which is heard POSS:closed:personal/2->that which is heard PRED:imperishable]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L2: `h₂énti stestóh₂h₂e ne-kʷe te h₂léksom` (10) -> `nu h₂énti stestóh₂h₂e ne-kʷe te h₂léksom` (11)
- L4: `nu h₂epó h₁éymi memónh₂e-kʷe te` (10) -> `nu h₂epó h₁éymi memónh₂e-kʷe-ge te` (11)
- L5: `ḱléwos-ge toy ń̥dʰgʷʰitom` (7) -> `ḱléwos-kʷe-ge toy ń̥dʰgʷʰitom` (8)

English old: Brother, I saw you falling. I stood near, and I did not protect you. I carried you from the field. The field drank your blood. Now I go away, and I remember you. Your fame indeed is imperishable.

English new: Brother, I saw you falling. Then I stood near, and I did not protect you. I carried you from the field. The field drank your blood. Now I go away, and I indeed remember you. And your fame indeed is imperishable.

### t023-0027 (lament)

Edits:
    c0 [VOC:man ADV:kudhe ADV:h2epo V:to go]: particle:None->ge
    c1 [GOAL:earth APPOS:mother->earth ADV:ni V:to go]: particle:None->ge
    c2 [SUBJ:closed:interrogative_kwi OBJ:cattle(PL) POSS:closed:personal/2->cattle V:to be driving]: conj:None->kʷe
    c3 [SUBJ:brother-in-law POSS:closed:personal/1->brother-in-law OBJ:closed:anaphoric_i(PL) V:to be driving]: particle:None->nu conj:None->kʷe
    c7 [OBJ:that which is heard V:to be carrying MOD:good->that which is heard]: DROP MOD:imperishable->that which is heard ADD MOD:good->that which is heard

Verse lines changed (old -> new, syllables):

- L1: `wíHre kúdʰe h₂epó gʷéh₂s` (7) -> `wíHre-ge kúdʰe h₂epó gʷéh₂s` (8)
- L2: `dʰéǵʰōm méh₂term̥ ní gʷā́m` (7) -> `dʰéǵʰōm-ge méh₂term̥ ní gʷā́m` (8)
- L3: `nu toy kʷís gʷṓs h₂éǵeti` (7) -> `nu-kʷe toy kʷís gʷṓs h₂éǵeti` (8)
- L4: `méne swēḱurós h₁íns h₂éǵeti` (9) -> `nu-kʷe méne swēḱurós h₁íns h₂éǵeti` (11)
- L7: `ń̥dʰgʷʰitom ḱléwos bʰéroh₂ h₁íd ne mr̥yétor` (12) -> `h₁wésu ḱléwos bʰéroh₂ h₁íd ne mr̥yétor` (11)

English old: Hero, where did you go away to? To Mother Earth I went down. Who now drives your cattle? My brother-in-law drives them. Now who speaks your words? The king speaks them. What do you carry? I carry imperishable fame. It does not die.

English new: Hero, where indeed did you go away to? To Mother Earth I indeed went down. And who now drives your cattle? And now my brother-in-law drives them. Now who speaks your words? The king speaks them. What do you carry? I carry good fame. It does not die.

## Lines not fixed

Each is off target by 1 (or 2) and no single edit or pair of edits was found that keeps the content, the adjective-noun fit and the per-lexeme cap (most are two parallel relative or interrogative clauses of 12 syllables that need 11, or a line whose only fixes would exceed the cap on a lexeme). Left unchanged; the batch passes the gate regardless.

```
t023: 121/125 verse lines exact (0.968; gate meter_exact>=0.90 PASS); lexeme cap 6
t023-0002 (charm) For a broken bone
  L2 c1-2    13/11  -2  h₃ésth₁ h₃sth₁éh₁ yungih₁tó h₁ésh₂r̥ h₁sh₂énh₁ yungih₁tó  [2, 1, 3, 2, 2, 3]
t023-0010 (charm) For a burn
  L2 c1-2    12/11  -1  bʰeh₂ǵʰús studyéh₁t h₂linHdʰí smérum bʰeh₂ǵʰéwi  [2, 2, 3, 2, 3]
t023-0011 (charm) Against a swelling
  L2 c2       7/8  +1  nu-kʷe péyh₂wr̥ tinh₁dʰí  [2, 2, 3]
  L5 c5-6     9/8  -1  gʷr̥h₃étu ǵʰwḗr péyh₂wr̥ gʷíh₃wetu  [3, 1, 2, 3]
```

Engine notes: realize_plans now prints new WARN lines (verb-form homographs of h₂éǵeti 'drive'/'say', anaphoric_i referents); they concern unchanged clauses and do not fail the gate. Tool note: meter_report's vocative edit inserts at slot 0 without renumbering head/dep (reported by the coordinator); my edit pipeline shifted indices itself and I checked every changed plan.
