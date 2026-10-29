# Meter repair: t026

meter_exact before: 0.346 (55/159); after: 0.994 (157/158). Gate PASS (all gates). Lexeme caps respected.

Method: edits found with the `scripts/meter_report.py` machinery (each realized and checked by `check_plan`), applied to `data/generation/plans/t026.jsonl`, English updated to match, re-realized with `--model claude-sonnet-5-5 --prompt-id tier3-planner-v4`. `corpus/` not hand-edited; `pie/` and tools unchanged. Particle edits (nu/-ge) leave the English unchanged except where it carried the particle ("indeed" for -ge, "now/then" for nu): removed when the particle was dropped. A -kʷe added at the start of a sentence appears as "And". Merged/split sentences change only line boundaries.

**Not fixed:** `t026-0027` line 1 ("Who is she, the young one who comes from the sky?") stays at 9 syllables (target 8): the only exact fixes add an epithet whose lexeme is already at the batch cap (every slice adjective is at 7 uses) or are not meaning-preserving.

Head/dep index check: for every changed plan the (slot, head/dep target) links were compared with the original plan; only intended drops/additions differ, none retargeted. No vocative edit was used, so the reported vocative-index bug did not affect this batch. No fixes were needed.


## Changed lines (plan id, edits, old/new PIE of the whole text, old/new English)


### t026-0015
- edits: c3 particle None->nu; c6 conj -kʷe kʷe->None; c9 particle None->nu; c10 particle None->nu; c10 conj -kʷe None->kʷe
- old PIE: h₂éwsos léwka déywi diwés dʰúgh₂ter. n̥sméy léwks sḱih₃wós-kʷe twéd bʰéwgt. wiHrṓs twé kʷḱént mudént-kʷe. túH h₂yuHénih₂ túH-kʷe ń̥dʰgʷʰiteh₂. túH kʷspés swésōr téwe bʰéh₂os h₃kʷbʰós lewbʰóm. ḱéywa n̥sméy h₁wésu ḱléwos dh₃dʰí. n̥sméy ń̥dʰgʷʰitom ḱléwos h₁áydʰi.
- new PIE: h₂éwsos léwka déywi diwés dʰúgh₂ter. n̥sméy léwks sḱih₃wós-kʷe twéd bʰéwgt. nu wiHrṓs twé kʷḱént mudént-kʷe. túH h₂yuHénih₂ túH ń̥dʰgʷʰiteh₂. túH kʷspés swésōr téwe bʰéh₂os h₃kʷbʰós lewbʰóm. nu ḱéywa n̥sméy h₁wésu ḱléwos dh₃dʰí. nu-kʷe n̥sméy ń̥dʰgʷʰitom ḱléwos h₁áydʰi.
- old English: Dawn, bright goddess, Daughter of Sky! You shone for us, and darkness fled from you. Men caught sight of you and became glad. You are young, and you are imperishable. You are the sister of the night. Your radiance is dear to the eyes. Give us good fame, dear one! Give us imperishable fame!
- new English: Dawn, bright goddess, Daughter of Sky! You shone for us, and darkness fled from you. Men caught sight of you and became glad. You are young, you are imperishable. You are the sister of the night. Your radiance is dear to the eyes. Give us good fame, dear one! And give us imperishable fame!

### t026-0016
- edits: c6 particle None->nu
- old PIE: h₂éwsos ḱéywa pótni gʷṓs h₁éǵʰs wédʰesi. lewkéh₂m wéstim woséyeth₂er. h₂éweyes sth₂ént h₁yód gʷm̥yési. n̥sméy h₂éh₂usom dédeh₃si. poh₂imnéy h₂wĺ̥h₁neh₂m dédeh₃si. n̥sméy suHnúns moysóns-kʷe h₁opéye. pótni n̥sméy ń̥dʰgʷʰitom ḱléwos duh₃dʰí.
- new PIE: h₂éwsos ḱéywa pótni gʷṓs h₁éǵʰs wédʰesi. lewkéh₂m wéstim woséyeth₂er. h₂éweyes sth₂ént h₁yód gʷm̥yési. n̥sméy h₂éh₂usom dédeh₃si. poh₂imnéy h₂wĺ̥h₁neh₂m dédeh₃si. nu n̥sméy suHnúns moysóns-kʷe h₁opéye. pótni n̥sméy ń̥dʰgʷʰitom ḱléwos duh₃dʰí.
- old English: Dawn, dear mistress, you lead out the cattle. You clothe yourself in bright clothing. The birds rise when you come. You give us gold. You give wool to the shepherd. Give us sons and rams! Give us imperishable fame, mistress!
- new English: Dawn, dear mistress, you lead out the cattle. You clothe yourself in bright clothing. The birds rise when you come. You give us gold. You give wool to the shepherd. Give us sons and rams! Give us imperishable fame, mistress!

### t026-0017
- edits: c1 drop OBJ kjexr; c1 add OBJ kjexr; c2 drop MOD HeHkjus; c2 particle None->nu; c5 drop SUBJ closed:relative_yo
- old PIE: sóh₂wl̥ diwés h₃ókʷ h₁yód h₂n̥rṓm ḱérdh₂ wóydth₂e. h₁yód HeHḱúns h₁éḱwons yéwgs h₁yód dʰewséh₂ gʷʰr̥néwsi. h₁yód snígʷʰm̥ tinéh₁si h₁yód dʰoHnéh₂m pékʷesi. n̥sméy h₂ew l̥h₂pdʰí n̥sméy léwkm̥ h₁áydʰi.
- new PIE: sóh₂wl̥ diwés h₃ókʷ h₁yód h₂n̥rṓm ḱḗr wóydth₂e. nu h₁yód h₁éḱwons yéwgs h₁yód dʰewséh₂ gʷʰr̥néwsi. h₁yód snígʷʰm̥ tinéh₁si dʰoHnéh₂m pékʷesi. n̥sméy h₂ew l̥h₂pdʰí n̥sméy léwkm̥ h₁áydʰi.
- old English: Sun, eye of Sky! You who know the hearts of men, you who yoke the swift horses, you who warm the animals, you who melt the snow, you who ripen the grain, shine for us again, give us light!
- new English: Sun, eye of Sky! You who know the heart of men, you who yoke the horses, you who warm the animals, you who melt the snow, ripen the grain, shine for us again, give us light!

### t026-0018
- edits: c1 particle None->nu; c1 conj -kʷe None->kʷe; c3 drop SUBJ kwekwlos; c3 add SUBJ closed:anaphoric_i; c4 particle None->nu; c4 conj -kʷe None->kʷe; c6 particle None->nu; c7 drop POSS soh2wl
- old PIE: sh₂wéns kʷékʷlos dyéwi yéh₂ti. HeHḱéwes h₁éḱwōs h₁ím dukénti. wóyḱons lowkéyeti kʷékʷlos mē Hrumpih₁tó. HeHḱéwes h₁éḱwōs mē sth₂éh₁yoyh₁ent. dyéwmn̥-ge h₂énti h₁r̥sḱéti. bʰéh₂os Hróth₂oy sédyeti. sh₂wéns-ge léwkos n̥sméy priHóm h₁syéh₁t.
- new PIE: sh₂wéns kʷékʷlos dyéwi yéh₂ti. nu-kʷe HeHḱéwes h₁éḱwōs h₁ím dukénti. wóyḱons lowkéyeti h₁éy mē Hrumpih₁tó. nu-kʷe HeHḱéwes h₁éḱwōs mē sth₂éh₁yoyh₁ent. dyéwmn̥-ge h₂énti h₁r̥sḱéti. nu bʰéh₂os Hróth₂oy sédyeti. léwkos-ge n̥sméy priHóm h₁syéh₁t.
- old English: The wheel of the sun goes in the sky. Swift horses draw it. It lights up the settlements. May the wheel not break! May the swift horses not stand still! Splendor goes in front of it. Radiance sits in the chariot. May the light of the sun, indeed, be dear to us.
- new English: The wheel of the sun goes in the sky. And swift horses draw it. It lights up the settlements. May it not break! And may the swift horses not stand still! Splendor goes in front of it. Radiance sits in the chariot. May the light, indeed, be dear to us.

### t026-0019
- edits: c4 particle None->nu; c5 drop POSS deywos; c6 particle None->nu
- old PIE: dyéw ph₂ter h₁uséwōm déh₃tor. h₁yós h₂uséy ḱlutóm h₁nómn̥ dʰéh₁s. h₁yós n̥sméy lewbʰéh₂m léwkm̥ dʰéh₁s. túH n̥sméy upér tetónth₂e túH deywṓm h₃rḗǵs. n̥smé ḱludʰí wékʷesh₂ nos ḱludʰí. dʰewséh₂ nos péh₂wr̥-kʷe h₂lékse.
- new PIE: dyéw ph₂ter h₁uséwōm déh₃tor. h₁yós h₂uséy ḱlutóm h₁nómn̥ dʰéh₁s. h₁yós n̥sméy lewbʰéh₂m léwkm̥ dʰéh₁s. nu túH n̥sméy upér tetónth₂e túH h₃rḗǵs. nu n̥smé ḱludʰí wékʷesh₂ nos ḱludʰí. dʰewséh₂ nos péh₂wr̥-kʷe h₂lékse.
- old English: Father Sky, giver of good things! You who set a famous name for Dawn, you who made dear light for us: you have stretched out above us. You are the king of the gods. Hear us, hear our words! Protect our animals and our fire!
- new English: Father Sky, giver of good things! You who set a famous name for Dawn, you who made dear light for us: you have stretched out above us. You are the king. Hear us, hear our words! Protect our animals and our fire!

### t026-0020
- edits: c1 particle None->nu; c4 particle None->nu; c4 conj -kʷe None->kʷe; c5 particle None->nu
- old PIE: dyéw dʰéǵʰōm-kʷe méǵh₂ih₂ méh₂tēr. deywṓs usméd ǵn̥h₁yónto. yú pl̥th₂enóh₁ yú-kʷe dʰubʰróh₁. wérsenn̥s h₂egʷnóns-kʷe h₂életes. pérkʷus h₁entér stestóh₂e. ǵénh₁torh₁e n̥smé ḱlutóm. suHnúns nos ḱwónn̥s-kʷe ph₂stóm.
- new PIE: dyéw dʰéǵʰōm-kʷe méǵh₂ih₂ méh₂tēr. nu deywṓs usméd ǵn̥h₁yónto. yú pl̥th₂enóh₁ yú-kʷe dʰubʰróh₁. nu-kʷe wérsenn̥s h₂egʷnóns-kʷe h₂életes. nu pérkʷus h₁entér stestóh₂e. ǵénh₁torh₁e n̥smé ḱlutóm. suHnúns nos ḱwónn̥s-kʷe ph₂stóm.
- old English: Sky and Earth, the great mother! The gods were born from you. You are wide, and you are deep. You nourish the male animals and the lambs. Between you stands the oak. Hear us, parents! Protect our sons and our dogs!
- new English: Sky and Earth, the great mother! The gods were born from you. You are wide, and you are deep. And you nourish the male animals and the lambs. Between you stands the oak. Hear us, parents! Protect our sons and our dogs!

### t026-0021
- edits: c0 particle None->nu; c5 conj -kʷe None->kʷe; c6 drop POSS lewks; c6 particle None->nu; c7 drop MOD lewbhos; c7 particle None->nu; c8 particle None->nu
- old PIE: léwks pr̥h₂wéh₂ léwks-ge ḱéyweh₂. léwks méǵh₂m̥ sḱih₃wóm gléwbʰeti. léwks deywṓm h₃ókʷ wiHrṓs lowkóy gʷíh₃wonti. tóy-ge sḱih₃wóy tr̥ménti. ǵʰleymós bʰéh₂os-kʷe lukés suHnúh₁. lewbʰóm bʰéh₂os n̥smé mē linkʷyéh₁t. dyéwmn̥ nos ḱléytreh₂m h₁ludʰóyh₁t.
- new PIE: nu léwks pr̥h₂wéh₂ léwks-ge ḱéyweh₂. léwks méǵh₂m̥ sḱih₃wóm gléwbʰeti. léwks deywṓm h₃ókʷ wiHrṓs lowkóy gʷíh₃wonti. tóy-kʷe-ge sḱih₃wóy tr̥ménti. nu ǵʰleymós bʰéh₂os-kʷe suHnúh₁. nu bʰéh₂os n̥smé mē linkʷyéh₁t. nu nos dyéwmn̥ ḱléytreh₂m h₁ludʰóyh₁t.
- old English: Light is first. Light, indeed, is dear. Light splits the great darkness. Light is the eye of the gods. In the light men live. In the darkness, indeed, they tremble. Brightness and radiance are the sons of light. May the dear radiance not leave us! May splendor come to our shelter!
- new English: Light is first. Light, indeed, is dear. Light splits the great darkness. Light is the eye of the gods. In the light men live. And in the darkness, indeed, they tremble. Brightness and radiance are the sons. May the radiance not leave us! May splendor come to our shelter!

### t026-0022
- edits: c2 merge (break True->False); c3 split (break False->True); c6 conj -kʷe None->kʷe; c8 particle None->nu; c8 conj -kʷe None->kʷe
- old PIE: nókʷt h₂éwsōs-kʷe méǵh₂ih₂h₁ swésorh₁e. kʷsép léyts pótni-kʷe h₁íh₂m̥ sékʷeth₂er. h₁rudʰéh₁si h₂éweyes-kʷe sth₂ént. kʷsép-ge sḱih₃wóm bʰéresi. pótni lewbʰéh₂m léwkm̥ bʰéresi. swésorh₁e n̥smé kʷsépi ph₂stóm.
- new PIE: nókʷt h₂éwsōs-kʷe méǵh₂ih₂h₁ swésorh₁e kʷsép léyts. pótni-kʷe h₁íh₂m̥ sékʷeth₂er. h₁rudʰéh₁si h₂éweyes-kʷe sth₂ént. kʷsép-kʷe-ge sḱih₃wóm bʰéresi. léwbʰa pótni lewbʰéh₂m léwkm̥ bʰéresi. nu-kʷe swésorh₁e n̥smé kʷsépi ph₂stóm.
- old English: Night and Dawn, great sisters! Night, you go away, and you, mistress, follow her. You glow red, and the birds rise. Night, indeed, you bring darkness. Mistress, you bring dear light. Protect us, sisters, in the night!
- new English: Night and Dawn, great sisters! Night, you go away, and you, mistress, follow her. You glow red, and the birds rise. And, Night, indeed, you bring darkness. Dear mistress, you bring dear light. And protect us, sisters, in the night!

### t026-0023
- edits: c0 particle None->nu; c2 conj -kʷe kʷe->None; c3 particle None->nu; c3 conj -kʷe None->kʷe; c4 particle None->nu; c6 conj -kʷe kʷe->None
- old PIE: h₂uséy h₁wésuh₂ wékʷesh₂ bʰéh₂omes. h₁íh₂ gʷm̥yéti h₂éweyes-kʷe sth₂ént. h₁ésyeh₂ey déh₃nom dédeh₃omes. h₁ésyeh₂s wókʷm̥ ḱléwsōmes. h₂réweti poh₂imḗn-kʷe dʰewséh₂ h₂éǵeti. bʰebʰudʰmé léwkm̥ dedr̥ḱmé mudmé-kʷe.
- new PIE: nu h₂uséy h₁wésuh₂ wékʷesh₂ bʰéh₂omes. h₁íh₂ gʷm̥yéti h₂éweyes sth₂ént. nu-kʷe h₁ésyeh₂ey déh₃nom dédeh₃omes. nu h₁ésyeh₂s wókʷm̥ ḱléwsōmes. h₂réweti poh₂imḗn dʰewséh₂ h₂éǵeti. bʰebʰudʰmé léwkm̥ dedr̥ḱmé mudmé-kʷe.
- old English: Let us speak good words to Dawn. She is coming, and the birds rise. Let us give her a gift. Let us listen to her voice. She glows, and the shepherd drives the animals. We are alert. We have seen the light, and we became glad.
- new English: Let us speak good words to Dawn. She is coming, the birds rise. And let us give her a gift. Let us listen to her voice. She glows, the shepherd drives the animals. We are alert. We have seen the light, and we became glad.

### t026-0024
- edits: c3 particle None->nu; c6 conj -kʷe kʷe->None
- old PIE: h₁yód dyéw ph₂ter h₂wérs dʰoHnéh₂ bʰwéh₂t. polh₁éwes gʷówes wódr̥ ph₃ént. ǵʰwḗres tr̥syónti h₂éǵroy nos h₂wr̥sdʰí. wódr̥ h₁ludʰóyh₁t dʰoHnéh₂-kʷe h₂uksyéh₁t.
- new PIE: h₁yód dyéw ph₂ter h₂wérs dʰoHnéh₂ bʰwéh₂t. polh₁éwes gʷówes wódr̥ ph₃ént. nu ǵʰwḗres tr̥syónti h₂éǵroy nos h₂wr̥sdʰí. wódr̥ h₁ludʰóyh₁t dʰoHnéh₂ h₂uksyéh₁t.
- old English: Father Sky, when you rain, the grain grows. The many cattle drink the water. The beasts are thirsty. Rain on our field! May the water come, and may the grain grow up!
- new English: Father Sky, when you rain, the grain grows. The many cattle drink the water. The beasts are thirsty. Rain on our field! May the water come, may the grain grow up!

### t026-0025
- edits: c1 conj -kʷe kʷe->None; c2 particle None->nu; c4 particle None->nu; c6 conj -kʷe None->kʷe
- old PIE: h₂éwsōs pr̥h₂wéh₂ sóh₂wl̥-kʷe h₁íh₂m̥ sékʷetor. h₁íh₂ pró yéh₂ti h₁íd-kʷe énu h₁éyti. h₁íh₂ h₂réweti h₁íd-kʷe n̥sméy priHóm. h₁yód h₁r̥sḱétes sth₂mé-ge.
- new PIE: h₂éwsōs pr̥h₂wéh₂ sóh₂wl̥ h₁íh₂m̥ sékʷetor. nu h₁íh₂ pró yéh₂ti h₁íd-kʷe énu h₁éyti. nu h₁íh₂ h₂réweti h₁íd-kʷe n̥sméy priHóm. h₁yód-kʷe h₁r̥sḱétes sth₂mé-ge.
- old English: Dawn is first, and the sun follows her. She goes before, and it comes after. She glows, and it is dear to us. We, indeed, rise when they come.
- new English: Dawn is first, the sun follows her. She goes before, and it comes after. She glows, and it is dear to us. And when they come, we, indeed, rise.

### t026-0026
- edits: c0 particle None->nu; c2 particle None->nu; c5 merge (break True->False); c6 split (break False->True); c7 particle None->nu
- old PIE: wósr̥ gʷegʷóme gʷʰért-kʷe. snígʷʰs tinéh₁ti wódr̥ drémt. gʷénh₂es péyh₂tu pékʷonti. wĺ̥kʷōs n̥ḱént h₂éweyes nisdóns démonti. lewkóm n̥sméy priHóm h₁syéh₁s. téwe léwkesi gʷíh₃woyh₁me.
- new PIE: nu wósr̥ gʷegʷóme gʷʰért-kʷe. nu snígʷʰs tinéh₁ti wódr̥ drémt. gʷénh₂es péyh₂tu pékʷonti wĺ̥kʷōs n̥ḱént. h₂éweyes nisdóns démonti. nu lewkóm n̥sméy priHóm h₁syéh₁s. téwe léwkesi gʷíh₃woyh₁me.
- old English: Spring has come, and it became warm. The snow melts, the water runs. The women cook the nourishing food. The wolves vanish. The birds build nests. Bright one, may you be dear to us. May we live in your light!
- new English: Spring has come, and it became warm. The snow melts, the water runs. The women cook the nourishing food. The wolves vanish. The birds build nests. Bright one, may you be dear to us. May we live in your light!

### t026-0027
- edits: c1 particle None->nu; c2 particle None->nu; c5 conj -kʷe kʷe->None; c6 particle None->nu; c7 drop MOD prh2wos; c7 particle None->nu
- old PIE: h₂yuHénih₂ kʷís diwés gʷm̥yéti? h₁íh₂ h₂éwsōs ḱéyweh₂ déywih₂. kúdʰe h₁éyti kúdʰe-kʷe stestóh₂e? h₁íh₂ h₁éyti h₂óweyes-kʷe h₁íh₂m̥ sékʷontor. pr̥h₂wós kʷís h₁íh₂m̥ widét? pr̥h₂wós poh₂imḗn h₁íh₂m̥ widét. ḱéyweh₂ déywih₂ n̥sméy lukyéh₁t.
- new PIE: h₂yuHénih₂ kʷís diwés gʷm̥yéti? nu h₁íh₂ h₂éwsōs ḱéyweh₂ déywih₂. nu kúdʰe h₁éyti kúdʰe-kʷe stestóh₂e? h₁íh₂ h₁éyti h₂óweyes h₁íh₂m̥ sékʷontor. nu pr̥h₂wós kʷís h₁íh₂m̥ widét? nu poh₂imḗn h₁íh₂m̥ widét. ḱéyweh₂ déywih₂ n̥sméy lukyéh₁t.
- old English: Who is she, the young one who comes from the sky? She is Dawn, the dear goddess. Where does she go, and where does she stand? She goes, and the sheep follow her. Who was first to see her? The shepherd was first to see her. May the dear goddess shine for us!
- new English: Who is she, the young one who comes from the sky? She is Dawn, the dear goddess. Where does she go, and where does she stand? She goes, the sheep follow her. Who was first to see her? The shepherd saw her. May the dear goddess shine for us!

### t026-0028
- edits: c2 conj -kʷe kʷe->None; c4 conj -kʷe kʷe->None; c6 drop POSS closed:personal/1; c7 particle None->nu; c7 conj -kʷe None->kʷe; c9 conj -kʷe None->kʷe
- old PIE: príHa déywi n̥smé gʷm̥dʰí. n̥sméy lukdʰí sḱih₃wós-kʷe bʰugyéh₁t. léwkm̥ kʷḱih₁mé mē-kʷe m̥rih₁mé. n̥sméy h₂óyu h₁wésu-kʷe ḱléwos h₁áydʰi. ḱóymos nos dyuménh₁ lewkós h₁syéh₁t. bʰórm̥ wĺ̥kʷom-kʷe n̥sméd ǵʰidʰí. péh₂wr̥ nos ḱléytreh₂i dʰégʷʰoyh₁t. ḱḗr-ge nos lowkóy mudyéh₁t.
- new PIE: príHa déywi n̥smé gʷm̥dʰí. n̥sméy lukdʰí sḱih₃wós bʰugyéh₁t. léwkm̥ kʷḱih₁mé mē m̥rih₁mé. n̥sméy h₂óyu h₁wésu-kʷe ḱléwos h₁áydʰi. ḱóymos dyuménh₁ lewkós h₁syéh₁t. nu-kʷe bʰórm̥ wĺ̥kʷom-kʷe n̥sméd ǵʰidʰí. péh₂wr̥ nos ḱléytreh₂i dʰégʷʰoyh₁t. ḱḗr-kʷe-ge nos lowkóy mudyéh₁t.
- old English: Dear goddess, come to us! Shine for us, and may the darkness flee. May we see the light, and may we not die. Give us a long life and good fame. May our household be bright with splendor! Drive the thief and the wolf away from us. May our fire burn in the shelter. May our heart, indeed, be glad in the light.
- new English: Dear goddess, come to us! Shine for us, may the darkness flee. May we see the light, may we not die. Give us a long life and good fame. May the household be bright with splendor! And drive the thief and the wolf away from us. May our fire burn in the shelter. And may our heart, indeed, be glad in the light.

### t026-0029
- edits: c0 drop MOD swos; c1 conj -kʷe None->kʷe; c2 particle None->nu; c4 particle None->nu; c6 drop POSS closed:personal/1; c6 particle None->nu
- old PIE: h₂éwsos swā́s h₂ówins pl̥th₂enóm h₂éǵrom wédʰoh₂. h₁íh₂n̥s-ge wĺ̥kʷōd h₂lékse. wĺ̥kʷos h₁íh₂n̥s mē gʷm̥yéh₁t. méne h₂óweyes pl̥h₁éwih₂es h₁sih₁ént. h₂óyu gʷíh₃woyh₁ent mē-kʷe m̥rih₁ént. méne priHós ḱwṓ h₁ím kʷḱyéh₁t mē kʷis lelikʷyéh₁t. léwbʰa déywi tébʰye h₂wĺ̥h₁neh₂m dédeh₃oh₂.
- new PIE: h₂éwsos h₂ówins pl̥th₂enóm h₂éǵrom wédʰoh₂. h₁íh₂n̥s-kʷe-ge wĺ̥kʷōd h₂lékse. nu wĺ̥kʷos h₁íh₂n̥s mē gʷm̥yéh₁t. méne h₂óweyes pl̥h₁éwih₂es h₁sih₁ént. nu h₂óyu gʷíh₃woyh₁ent mē-kʷe m̥rih₁ént. nu priHós ḱwṓ h₁ím kʷḱyéh₁t mē kʷis lelikʷyéh₁t. léwbʰa déywi tébʰye h₂wĺ̥h₁neh₂m dédeh₃oh₂.
- old English: Dawn, I lead my own sheep to the wide field. Protect them, indeed, from the wolf! May the wolf not come to them! May my sheep be many. May they live a long time, and may they not die. May my dear dog see the wolf. May none be missing. I shall give you wool, dear goddess.
- new English: Dawn, I lead the sheep to the wide field. And protect them, indeed, from the wolf! May the wolf not come to them! May my sheep be many. May they live a long time, and may they not die. May the dear dog see the wolf. May none be missing. I shall give you wool, dear goddess.

### t026-0030
- edits: c2 conj -kʷe kʷe->None; c5 drop POSS closed:personal/1; c5 particle None->nu; c8 conj -kʷe kʷe->None
- old PIE: sóh₂wl̥ méne ḱóymōd h₁éymi. méǵʰye pró ih₂dʰí h₁mé-kʷe spéḱye. wĺ̥kʷos bʰṓr-kʷe h₁mé mē h₁pih₁tā́m. méne ǵónwih₁ mē tr̥mih₁tā́m. méne tpḗrsneh₂ mē h₃slidʰyéh₁t mē bʰebʰih₂yéh₁m̥. ḱóymom h₁r̥yéh₁m̥ solh₂wós-kʷe bʰuHyéh₁m̥.
- new PIE: sóh₂wl̥ méne ḱóymōd h₁éymi. méǵʰye pró ih₂dʰí h₁mé spéḱye. wĺ̥kʷos bʰṓr-kʷe h₁mé mē h₁pih₁tā́m. méne ǵónwih₁ mē tr̥mih₁tā́m. nu tpḗrsneh₂ mē h₃slidʰyéh₁t mē bʰebʰih₂yéh₁m̥. ḱóymom h₁r̥yéh₁m̥ solh₂wós bʰuHyéh₁m̥.
- old English: Sun, I am going away from my village. Go before me, and look upon me! May the wolf and the thief not seize me! May my knees not tremble. May my heel not slip. May I not be afraid. May I arrive at home, and may I be whole.
- new English: Sun, I am going away from my village. Go before me, look upon me! May the wolf and the thief not seize me! May my knees not tremble. May the heel not slip. May I not be afraid. May I arrive at home, may I be whole.

### t026-0031
- edits: c0 particle None->nu; c1 particle None->nu; c4 particle None->nu; c6 particle None->nu; c8 conj -kʷe None->kʷe
- old PIE: dyéw ph₂ter tébʰye moysóm dedh₃més. h₁ím h₁áyso n̥sméy-kʷe wódr̥ duh₃dʰí. tébʰye h₂wĺ̥h₁neh₂m h₂éh₂usom-kʷe bʰérōmes. tr̥syómes dʰewséh₂-kʷe nos tr̥syéti. h₂éǵroysu nos h₂wr̥sdʰí dʰoHnéh₂ h₂uksyéh₁t. dʰewséh₂-ge nos mē mr̥yéh₁t.
- new PIE: nu dyéw ph₂ter tébʰye moysóm dedh₃més. nu h₁ím h₁áyso n̥sméy-kʷe wódr̥ duh₃dʰí. tébʰye h₂wĺ̥h₁neh₂m h₂éh₂usom-kʷe bʰérōmes. nu tr̥syómes dʰewséh₂-kʷe nos tr̥syéti. nu nos h₂éǵroysu h₂wr̥sdʰí dʰoHnéh₂ h₂uksyéh₁t. dʰewséh₂-kʷe-ge nos mē mr̥yéh₁t.
- old English: Father Sky, we give you a ram. Take it, and give us water! We shall bring you wool and gold. We are thirsty, and our animals are thirsty. Rain on our fields, and may the grain grow up! May our animals, indeed, not die.
- new English: Father Sky, we give you a ram. Take it, and give us water! We shall bring you wool and gold. We are thirsty, and our animals are thirsty. Rain on our fields, and may the grain grow up! And may our animals, indeed, not die.

### t026-0032
- edits: c0 drop MOD lewbhos; c0 particle None->nu; c2 particle None->nu; c3 particle None->nu; c5 particle None->nu; c7 particle None->nu
- old PIE: léwbʰa pótni méne suHnús ḱéyor gʷʰért-kʷe. méne suHnúm memn̥dʰí. h₁ím spéḱye h₁ím-kʷe h₂lékse. méne suHnús sth₂yéh₁t mē-kʷe mr̥yéh₁t. wódr̥ ph₃yéh₁t h₁édih₁t-kʷe. pótni tébʰye h₂egʷnóm déh₃oh₂.
- new PIE: nu pótni méne suHnús ḱéyor gʷʰért-kʷe. nu méne suHnúm memn̥dʰí. nu h₁ím spéḱye h₁ím-kʷe h₂lékse. nu méne suHnús sth₂yéh₁t mē-kʷe mr̥yéh₁t. nu wódr̥ ph₃yéh₁t h₁édih₁t-kʷe. pótni tébʰye h₂egʷnóm déh₃oh₂.
- old English: Dear mistress, my son lies, and has become warm. Remember my son! Look upon him and guard him! May my son stand up, and may he not die. May he drink water, and may he eat. I shall give you a lamb, mistress.
- new English: Mistress, my son lies, and has become warm. Remember my son! Look upon him and guard him! May my son stand up, and may he not die. May he drink water, and may he eat. I shall give you a lamb, mistress.

### t026-0033
- edits: c2 particle None->nu; c3 particle None->nu; c6 drop POSS closed:personal/1; c7 particle None->nu
- old PIE: léwkm̥ dedr̥ḱmé mudmé-kʷe. léwka n̥sméy bʰéh₂os h₁áys. tébʰye déh₃nom dedh₃més. n̥smé h₂ew gʷm̥dʰí tetr̥pmé. h₁wésuh₂ nos wékʷesh₂ ḱlutéh₂ h₁syéh₁t. n̥sméy priHós h₁sdʰí n̥smé mē linékʷs.
- new PIE: léwkm̥ dedr̥ḱmé mudmé-kʷe. nu léwka n̥sméy bʰéh₂os h₁áys. nu tébʰye déh₃nom dedh₃més. n̥smé h₂ew gʷm̥dʰí tetr̥pmé. h₁wésuh₂ wékʷesh₂ ḱlutéh₂ h₁syéh₁t. nu n̥sméy priHós h₁sdʰí n̥smé mē linékʷs.
- old English: We have seen the light, and we became glad. Bright one, you gave us light. We give you a gift. Come to us again. We are satisfied. May our good words be heard! Be dear to us, do not leave us!
- new English: We have seen the light, and we became glad. Bright one, you gave us light. We give you a gift. Come to us again. We are satisfied. May the good words be heard! Be dear to us, do not leave us!

### t026-0034
- edits: c0 add MOD kjlutos; c1 particle None->nu; c3 particle None->nu; c5 particle None->nu
- old PIE: h₂yúHeni pótni ǵʰwḗrm̥ h₂isḱóh₂. h₁mé wédʰe h₁mé-kʷe spéḱye. méǵʰye h₁ím woydéye mē-kʷe bʰugyéh₁t. méne h₃ókʷih₁ h₁ím kʷḱih₁tā́m. h₁ím h₁pyéh₁m̥ tébʰye-kʷe déh₃nom dédeh₃oh₂.
- new PIE: h₂yúHeni ḱlúta pótni ǵʰwḗrm̥ h₂isḱóh₂. nu h₁mé wédʰe h₁mé-kʷe spéḱye. nu méǵʰye h₁ím woydéye mē-kʷe bʰugyéh₁t. nu méne h₃ókʷih₁ h₁ím kʷḱih₁tā́m. h₁ím h₁pyéh₁m̥ tébʰye-kʷe déh₃nom dédeh₃oh₂.
- old English: Young mistress, I am seeking a wild beast. Lead me and look upon me! Show it to me, and may it not flee. May my eyes catch sight of it. May I seize it, and I shall give you a gift.
- new English: Young, famous mistress, I am seeking a wild beast. Lead me and look upon me! Show it to me, and may it not flee. May my eyes catch sight of it. May I seize it, and I shall give you a gift.

### t026-0035
- edits: c2 conj -kʷe None->kʷe; c4 particle None->nu
- old PIE: dyéw ḱludʰí sóh₂wl̥ widéh₁ye. méǵh₂ih₂m-ge bʰoydʰéh₂m dʰéh₁m̥. h₁yód ḱéywom dʰréwgʰoh₂ dyḗws me moréyoyh₁t. h₁yód h₁ím mē dʰréwgʰoh₂ gʷíh₃woyh₁m̥.
- new PIE: dyéw ḱludʰí sóh₂wl̥ widéh₁ye. méǵh₂ih₂m-kʷe-ge bʰoydʰéh₂m dʰéh₁m̥. h₁yód ḱéywom dʰréwgʰoh₂ nu me dyḗws moréyoyh₁t. h₁yód h₁ím mē dʰréwgʰoh₂ gʷíh₃woyh₁m̥.
- old English: Sky, hear! Sun, see! I have indeed made a great pledge. If I deceive a friend, may Sky kill me. If I do not deceive him, may I live.
- new English: Sky, hear! Sun, see! And I have indeed made a great pledge. If I deceive a friend, may Sky kill me. If I do not deceive him, may I live.

### t026-0036
- edits: c2 particle None->nu; c5 particle None->nu; c7 add MOD lewbhos
- old PIE: sóh₂wl̥ kóryom h₁imés n̥sméy pró ih₂dʰí. n̥smé h₂lékse gʰóstins-kʷe unih₁mé. polh₁éwes gʰósteyes n̥sméd bʰugih₁ént. n̥smé gʰostíbʰos spr̥dʰí. n̥sméy polh₁úns misdʰóns h₁áydʰi. péh₂wr̥ h₁rih₁mé mē-kʷe m̥rih₁mé.
- new PIE: sóh₂wl̥ kóryom h₁imés n̥sméy pró ih₂dʰí. nu n̥smé h₂lékse gʰóstins-kʷe unih₁mé. polh₁éwes gʰósteyes n̥sméd bʰugih₁ént. nu n̥smé gʰostíbʰos spr̥dʰí. n̥sméy polh₁úns misdʰóns h₁áydʰi. lewbʰóm péh₂wr̥ h₁rih₁mé mē-kʷe m̥rih₁mé.
- old English: Sun, we are going to war: go before us! Guard us, and may we overpower the enemies. May the many enemies flee from us. Rescue us from the enemies! Give us many prizes! May we arrive at the fire, and may we not die.
- new English: Sun, we are going to war: go before us! Guard us, and may we overpower the enemies. May the many enemies flee from us. Rescue us from the enemies! Give us many prizes! May we arrive at the dear fire, and may we not die.

### t026-0037
- edits: c0 add MOD swos; c0 particle None->nu; c3 particle None->nu; c4 particle None->nu; c5 particle None->nu; c6 particle None->nu; c8 particle None->nu; c8 conj -kʷe None->kʷe
- old PIE: h₂éwsos méǵʰye suHnúm h₁opéye. h₁éy Hwr̥dʰyéh₁t h₂óyu-kʷe gʷíh₃woyh₁t. h₁éy wiHrós h₁syéh₁t h₁éy h₁léwdʰeros h₁syéh₁t. h₁ésyo h₁nómn̥ ḱlutóm h₁syéh₁t. péyh₂tu h₁édih₁t sh₂yéh₁t-kʷe. tébʰye h₂egʷnóm h₂wĺ̥h₁neh₂m-kʷe déh₃oh₂.
- new PIE: nu h₂éwsos méǵʰye swóm suHnúm h₁opéye. h₁éy Hwr̥dʰyéh₁t h₂óyu-kʷe gʷíh₃woyh₁t. nu h₁éy wiHrós h₁syéh₁t nu h₁éy h₁léwdʰeros h₁syéh₁t. nu h₁ésyo h₁nómn̥ ḱlutóm h₁syéh₁t. nu péyh₂tu h₁édih₁t sh₂yéh₁t-kʷe. nu-kʷe tébʰye h₂egʷnóm h₂wĺ̥h₁neh₂m-kʷe déh₃oh₂.
- old English: Dawn, give me a son! May he become strong, and may he live a long time. May he be a hero. May he be free. May his name be famous. May he eat nourishing food, and may he be sated. I shall give you a lamb and wool.
- new English: Dawn, give me a son of my own! May he become strong, and may he live a long time. May he be a hero. May he be free. May his name be famous. May he eat nourishing food, and may he be sated. And I shall give you a lamb and wool.

### t026-0038
- edits: c1 drop POSS closed:personal/1; c1 particle None->nu; c2 drop POSS closed:personal/1; c2 particle None->nu; c6 particle None->nu; c6 conj -kʷe None->kʷe
- old PIE: h₁eǵóh₂ méǵh₂s ḱóymosyo h₃rḗǵs. h₂éwsos sóh₂wl̥ dyéw-kʷe méne wóyḱom ph₂sté. méne wiHrṓs h₂óyu gʷíh₃woyh₁ent. h₁éysōm h₂óweyes pl̥h₁éwih₂es h₁sih₁ént. bʰṓr méne ḱóymom mē gʷm̥yéh₁t. pl̥h₁éwih₂ dʰoHnéh₂ wóyḱoy h₁syéh₁t. méǵʰye ń̥dʰgʷʰitom ḱléwos duh₃té.
- new PIE: h₁eǵóh₂ méǵh₂s ḱóymosyo h₃rḗǵs. nu h₂éwsos sóh₂wl̥ dyéw-kʷe wóyḱom ph₂sté. nu wiHrṓs h₂óyu gʷíh₃woyh₁ent. h₁éysōm h₂óweyes pl̥h₁éwih₂es h₁sih₁ént. bʰṓr méne ḱóymom mē gʷm̥yéh₁t. pl̥h₁éwih₂ dʰoHnéh₂ wóyḱoy h₁syéh₁t. nu-kʷe méǵʰye ń̥dʰgʷʰitom ḱléwos duh₃té.
- old English: I am the great king of the village. Dawn, Sun and Sky, protect my settlement! May my men live a long time. May their sheep be many. May the thief not come to my village. May there be much grain in the settlement. Give me imperishable fame!
- new English: I am the great king of the village. Dawn, Sun and Sky, protect the settlement! May the men live a long time. May their sheep be many. May the thief not come to my village. May there be much grain in the settlement. And give me imperishable fame!

### t026-0039
- edits: c1 conj -kʷe kʷe->None; c2 particle None->nu; c5 conj -kʷe kʷe->None; c6 drop POSS closed:personal/1; c7 merge (break True->False)
- old PIE: h₁regʷesyéti kʷséps-kʷe gʷm̥yéti. sóh₂wl̥ wódr̥ Hn̥dʰí séngʷs. ph₂ter n̥smé nékʷti h₂lékse. l̥gʰih₁mé swépnos-kʷe n̥smé h₁pyéh₁t. ḱwṓ nos ḱléytreh₂m h₂léksoyh₁t. pérkʷus n̥smé ḱéloyh₁t. bʰudʰih₁mé léwkm̥-kʷe h₂ew dedr̥ḱih₁mé.
- new PIE: h₁regʷesyéti kʷséps gʷm̥yéti. nu sóh₂wl̥ wódr̥ Hn̥dʰí séngʷs. ph₂ter n̥smé nékʷti h₂lékse. l̥gʰih₁mé swépnos n̥smé h₁pyéh₁t. ḱwṓ ḱléytreh₂m h₂léksoyh₁t pérkʷus n̥smé ḱéloyh₁t. bʰudʰih₁mé léwkm̥-kʷe h₂ew dedr̥ḱih₁mé.
- old English: It is getting dark, and night is coming. Sun, you sank into the water below. Father, guard us in the night! May we lie down, and may sleep seize us. May our dog guard the shelter. May the oak cover us. May we wake, and may we see the light again.
- new English: It is getting dark, night is coming. Sun, you sank into the water below. Father, guard us in the night! May we lie down, may sleep seize us. May the dog guard the shelter. May the oak cover us. May we wake, and may we see the light again.

### t026-0040
- edits: c0 particle None->nu; c3 particle None->nu; c4 particle None->nu; c6 particle None->nu; c6 conj -kʷe None->kʷe; c8 particle None->nu
- old PIE: pl̥th₂enóm méne h₂éǵrom h₂érh₃yoh₂. dyéw h₁ésmi h₂wr̥sdʰí sóh₂wl̥ h₁ím gʷʰr̥nudʰí. dʰéǵʰom méh₂ter méǵʰye dʰoHnéh₂m dh₃dʰí. méne dʰoHnéh₂ h₂uksyéh₁t h₁édih₁m̥-kʷe. h₂éweyes h₁íh₂m̥ mē h₁édih₁ent. méne yugóm mē Hrumpih₁tó. pérkʷunos h₁mé mē stundyéh₁t.
- new PIE: nu pl̥th₂enóm méne h₂éǵrom h₂érh₃yoh₂. dyéw h₁ésmi h₂wr̥sdʰí sóh₂wl̥ h₁ím gʷʰr̥nudʰí. nu dʰéǵʰom méh₂ter méǵʰye dʰoHnéh₂m dh₃dʰí. nu méne dʰoHnéh₂ h₂uksyéh₁t h₁édih₁m̥-kʷe. nu-kʷe h₂éweyes h₁íh₂m̥ mē h₁édih₁ent. méne yugóm mē Hrumpih₁tó. nu pérkʷunos h₁mé mē stundyéh₁t.
- old English: I am ploughing my wide field. Sky, rain upon it! Sun, warm it! Mother Earth, give me grain! May my grain grow up, and may I eat. May the birds not eat it. May my yoke not break. May Perkwunos not strike me.
- new English: I am ploughing my wide field. Sky, rain upon it! Sun, warm it! Mother Earth, give me grain! May my grain grow up, and may I eat. And may the birds not eat it. May my yoke not break. May Perkwunos not strike me.

