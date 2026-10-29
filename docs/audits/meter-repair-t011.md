# Meter repair: t011

meter_exact before: 46/152 = 0.303 (census); after: 144/152 = 0.947. Gate: PASS (all gates true; max_lexeme_uses 6).

Edit types: particle (nu/ge add or drop), conj (-kʷe add or drop), drop (vocative/possessor/epithet/adverb removed), epithet (adjective added), vocative (added), number (none used). No split/merge edits. Epithets were added only where the adjective fits the noun, within the per-lexeme cap. Plan edit lines below are `cN [clause content]: change` (clause index 0-based). Slot head/dep indices were verified after the edits: every head/dep link in a changed plan still points at the same lexeme as before (the added-vocative renumbering bug in meter_report was avoided by shifting head/dep after each vocative insert; no misdirected index found, no fixes needed).

## Changed texts

### t011-0001 (hymn)

Edits:
    c0 [VOC:Perkʷunos OBJ:word POSS:closed:personal/1->word(PL) V:to hear]: DROP MOD:big->striker,VOC:striker
    c2 [SUBJ:closed:relative_yo OBJ:snake V:to be striking down MOD:big->snake]: ADD MOD:big->snake
    c7 [SUBJ:water(PL) ADV:pro-2 GOAL:sea V:to go]: conj:None->kʷe
    c8 [V:to rain LOC:field(PL) POSS:closed:personal/1->field(PL) VOC:Perkʷunos]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `pérkʷune nos méǵh₂ gʷʰóne wékʷos ḱludʰí` (12) -> `pérkʷune nos wékʷos ḱludʰí` (8)
- L2: `h₁yós stonh₂éyesi h₁yós h₁ógʷʰim gʷʰéns` (9) -> `h₁yós stonh₂éyesi h₁yós méǵh₂m̥ h₁ógʷʰim gʷʰéns` (11)
- L5: `nu wédōr móri pró gʷéh₂t` (7) -> `nu-kʷe wédōr móri pró gʷéh₂t` (8)
- L6: `nu nos pérkʷune h₂éǵroysu h₂wr̥sdʰí` (10) -> `nu-kʷe nos pérkʷune h₂éǵroysu h₂wr̥sdʰí` (11)

English old: Perkʷunos, great striker, hear our word! You who thunder, you who slew the serpent; you who set the waters free, famous are you. The serpent lay among the waters; you struck him, and then the waters went forth to the sea. Now rain on our fields, Perkʷunos.

English new: Perkʷunos, hear our word! You who thunder, you who slew the great serpent; you who set the waters free, famous are you. The serpent lay among the waters; you struck him, and then the waters went forth to the sea. And now rain on our fields, Perkʷunos.

### t011-0002 (hymn)

Edits:
    c0 [VOC:Perkʷunos MOD:swift->striker VOC:striker V:to hear MOD:good->Perkʷunos]: ADD MOD:good->Perkʷunos
    c7 [SUBJ:grain V:to grow]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L1: `pérkʷune HéHḱew gʷʰóne ḱludʰí` (9) -> `h₁wésew pérkʷune HéHḱew gʷʰóne ḱludʰí` (11)
- L4: `dʰéǵʰōm térst túH h₂wérs wédos péh₃t dʰoHnéh₂-kʷe bʰwéh₂t` (12) -> `dʰéǵʰōm térst túH h₂wérs wédos péh₃t dʰoHnéh₂ bʰwéh₂t` (11)

English old: Perkʷunos, swift striker, hear! You thunder, you give water to the earth; you fill the fields with water. The earth grew dry, you rained, she drank the water, and the grain grew. Fill our fields with water, Perkʷunos.

English new: Good Perkʷunos, swift striker, hear! You thunder, you give water to the earth; you fill the fields with water. The earth grew dry, you rained, she drank the water; the grain grew. Fill our fields with water, Perkʷunos.

### t011-0003 (hymn)

Edits:
    c0 [VOC:Perkʷunos VOC:striker V:to step]: DROP MOD:big->striker
    c2 [SUBJ:cattle(PL) V:to tremble in fear]: particle:None->nu
    c6 [VOC:striker OBJ:closed:personal/1(PL) V:to strike]: DROP VOC:Perkʷunos ADD VOC:striker

Verse lines changed (old -> new, syllables):

- L1: `pérkʷune méǵh₂ gʷʰóne gʷéms h₂énh₁mos-kʷe h₂wḗh₁t` (13) -> `pérkʷune gʷʰóne gʷéms h₂énh₁mos-kʷe h₂wḗh₁t` (11)
- L2: `gʷówes trésont stonh₂éyes wĺ̥kʷom téwks` (10) -> `nu gʷówes trésont stonh₂éyes wĺ̥kʷom téwks` (11)
- L3: `h₂wérst pérkʷune nos mē gʷʰn̥sḱés wĺ̥kʷom gʷʰn̥sḱé` (12) -> `h₂wérst gʷʰóne nos mē gʷʰn̥sḱés wĺ̥kʷom gʷʰn̥sḱé` (11)

English old: Perkʷunos, great striker, you came, and the wind blew. The cattle trembled; you thundered, you struck the wolf. It rained. Do not strike us, Perkʷunos; strike the wolf.

English new: Perkʷunos, striker, you came, and the wind blew. Then the cattle trembled; you thundered, you struck the wolf. It rained. Do not strike us, striker; strike the wolf.

### t011-0004 (hymn)

Edits:
    c0 [VOC:Perkʷunos MOD:heard->striker PRED:striker V:to be MOD:big->Perkʷunos]: ADD MOD:big->Perkʷunos
    c7 [SUBJ:closed:personal/2 V:to thunder [-éyeti: caus]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `pérkʷune ḱlutós gʷʰonós h₁ési` (9) -> `méǵh₂ pérkʷune ḱlutós gʷʰonós h₁ési` (11)
- L5: `túH stonh₂éyesi tód-kʷe dédeh₃si` (10) -> `nu túH stonh₂éyesi tód-kʷe dédeh₃si` (11)

English old: Perkʷunos, you are a famous striker. Who slew the serpent, who set the waters free? You slew the serpent, you set the waters free. Who thunders, who gives water to the earth? You thunder, and you give it. Give us imperishable fame.

English new: Great Perkʷunos, you are a famous striker. Who slew the serpent, who set the waters free? You slew the serpent, you set the waters free. Who thunders, who gives water to the earth? Now you thunder, and you give it. Give us imperishable fame.

### t011-0005 (hymn)

Edits:
    c0 [VOC:sky VOC:father PRED:giver POSS:good->giver(PL) V:to be]: particle:None->ge
    c3 [SUBJ:closed:relative_yo OBJ:word POSS:closed:personal/1->word(PL) V:to be sharp-eared]: particle:None->nu
    c4 [SUBJ:closed:relative_yo IO:god(PL) OBJ:name(PL) V:to have put]: particle:None->ge
    c6 [OBJ:good(PL) V:to give IO:closed:personal/1(PL)]: particle:nu->None

Verse lines changed (old -> new, syllables):

- L1: `dyéw ph₂ter h₁uséwōm déh₃tōr h₁ési` (10) -> `dyéw-ge ph₂ter h₁uséwōm déh₃tōr h₁ési` (11)
- L3: `h₁yós nos wékʷos h₂ḱh₂owsyési` (7) -> `nu nos h₁yós wékʷos h₂ḱh₂owsyési` (8)
- L4: `h₁yós deywóybʰos h₁nómn̥h₂ dʰéh₁s` (7) -> `h₁yós-ge deywóybʰos h₁nómn̥h₂ dʰéh₁s` (8)
- L5: `lewkós ḱlutós h₁ési nu nos h₁wésuh₂ duh₃dʰí` (12) -> `lewkós ḱlutós h₁ési h₁wésuh₂ nos duh₃dʰí` (11)

English old: Father Sky, you are the giver of good things. You who give light, you who set the stars in the night, you who hear our word well, you who gave the gods their names: bright and famous are you. Now give us good things.

English new: Father Sky, you are indeed the giver of good things. You who give light, you who set the stars in the night, you who then hear our word well, you who indeed gave the gods their names: bright and famous are you. Give us good things.

### t011-0006 (hymn)

Edits:
    c1 [ADV:uper V:to be stretching]: DROP VOC:sky
    c3 [V:to rain]: DROP VOC:sky

Verse lines changed (old -> new, syllables):

- L2: `dyéw upér tn̥néwsi dʰéǵʰom Hn̥dʰí ḱéyth₂er` (12) -> `upér tn̥néwsi dʰéǵʰom Hn̥dʰí ḱéyth₂er` (11)
- L3: `dyéw h₂wérs dʰéǵʰom wédos péh₃s h₂orkéyetom nos` (12) -> `h₂wérs dʰéǵʰom wédos péh₃s h₂orkéyetom nos` (11)

English old: Father Sky and Mother Earth, hear us, you two! Sky, you stretch above; Earth, you lie below. Sky, you rained; Earth, you drank the water. Guard us, you two.

English new: Father Sky and Mother Earth, hear us, you two! You stretch above; Earth, you lie below. You rained; Earth, you drank the water. Guard us, you two.

### t011-0007 (hymn)

Edits:
    c0 [VOC:father POSS:man->heart(PL) OBJ:heart(PL) V:to have seen]: DROP VOC:sky
    c1 [OBJ:pledge(PL) POSS:man->pledge(PL) V:to see]: particle:None->ge
    c2 [SUBJ:closed:relative_yo OBJ:pledge V:to break (something)]: particle:None->nu
    c6 [OBJ:closed:personal/1(PL) V:to strike]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `dyéw ph₂ter h₂n̥rṓm ḱérdh₂ wóydth₂e` (9) -> `ph₂ter h₂n̥rṓm ḱérdh₂ wóydth₂e` (8)
- L2: `h₂n̥rṓm bʰoydʰā́s dedórḱth₂e` (7) -> `h₂n̥rṓm-ge bʰoydʰā́s dedórḱth₂e` (8)
- L3: `h₁yós bʰoydʰéh₂m Hrunépt tóm kélh₂s mért-kʷe` (10) -> `nu h₁yós bʰoydʰéh₂m Hrunépt tóm kélh₂s mért-kʷe` (11)
- L4: `nu nos bʰoydʰéh₂m ḱléwse mē nos kl̥h₂yéh₁s` (10) -> `nu nos bʰoydʰéh₂m ḱléwse mē-ge nos kl̥h₂yéh₁s` (11)

English old: Father Sky, you know the hearts of men; you have seen the pledges of men. Whoever broke a pledge, you struck him, and he died. Hear our pledge now. May you not strike us.

English new: Father, you know the hearts of men; you have indeed seen the pledges of men. Whoever then broke a pledge, you struck him, and he died. Hear our pledge now. Indeed, may you not strike us.

### t011-0008 (hymn)

Edits:
    c0 [VOC:sky MOD:bright->sky V:to be getting dark]: particle:None->nu
    c3 [POSS:closed:personal/2->star(SG) SUBJ:star(PL) V:to shine]: particle:None->ge
    c4 [POSS:closed:personal/2->moon(SG) SUBJ:moon V:to shine]: particle:None->nu
    c6 [SUBJ:dawn POSS:closed:personal/2->daughter(SG) SUBJ:daughter ADV:h2ew V:to come]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `léwke dyéw h₁regʷesyéti` (7) -> `nu léwke dyéw h₁regʷesyéti` (8)
- L3: `téwe h₂stéres ǵʰlóh₁onti` (7) -> `téwe-ge h₂stéres ǵʰlóh₁onti` (8)
- L4: `téwe lówksneh₂ ǵʰlóh₁eti ph₂sdʰí nos` (10) -> `nu téwe lówksneh₂ ǵʰlóh₁eti ph₂sdʰí nos` (11)
- L5: `h₂éwsōs téwe dʰugh₂tḗr h₂ew gʷm̥yóyh₁t` (10) -> `h₂éwsōs-ge téwe dʰugh₂tḗr h₂ew gʷm̥yóyh₁t` (11)

English old: Bright Sky, it grows dark. The sun sank, and the stars are standing. Your stars shine, your moon shines. Protect us. May Dawn, your daughter, come again.

English new: Now, bright Sky, it grows dark. The sun sank, and the stars are standing. Your stars indeed shine, now your moon shines. Protect us. May Dawn, your daughter, indeed come again.

### t011-0009 (hymn)

Edits:
    c0 [VOC:daughter POSS:sky->daughter V:to shine]: DROP VOC:dawn,MOD:bright->dawn
    c2 [SUBJ:closed:relative_yo OBJ:earth V:to light up]: particle:None->nu
    c5 [SUBJ:star(PL) V:to vanish]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L1: `léwka h₂éwsos diwés dʰúgh₂ter ǵʰlóh₁esi` (12) -> `diwés dʰúgh₂ter ǵʰlóh₁esi` (8)
- L3: `h₁yéh₂ dʰéǵʰōm lowkéyesi` (7) -> `nu h₁yéh₂ dʰéǵʰōm lowkéyesi` (8)
- L4: `h₁yéh₂ sóh₂wl̥ wédʰesi gʷéms h₂stéres-kʷe n̥ḱént` (12) -> `h₁yéh₂ sóh₂wl̥ wédʰesi gʷéms h₂stéres n̥ḱént` (11)

English old: Bright Dawn, daughter of Sky, you shine. You who drive the night away, you who light up the earth, you who bring the sun! You came, and the stars vanished. Come again, Dawn, and bring us the sun.

English new: Daughter of Sky, you shine. You who drive the night away, you who then light up the earth, you who bring the sun! You came; the stars vanished. Come again, Dawn, and bring us the sun.

### t011-0010 (hymn)

Edits:
    c4 [SUBJ:cattle(PL) V:to stand up]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L2: `gʷṓs h₁eǵʰ wédʰesi gʷéms spḗr bʰéwdʰt gʷówes-kʷe sth₂ént` (12) -> `gʷṓs h₁eǵʰ wédʰesi gʷéms spḗr bʰéwdʰt gʷówes sth₂ént` (11)

English old: Dawn, daughter of Sky, you who are red, you lead the cattle out. You came: the sparrow woke, and the cattle stood up. The man drives them forward. Dawn, safeguard them.

English new: Dawn, daughter of Sky, you who are red, you lead the cattle out. You came: the sparrow woke; the cattle stood up. The man drives them forward. Dawn, safeguard them.

### t011-0011 (hymn)

Edits:
    c0 [VOC:dawn SUBJ:night POSS:closed:personal/2->sister(SG) PRED:sister V:to be MOD:dear->dawn]: ADD MOD:dear->dawn
    c2 [V:to stand up]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L1: `h₂éwsos kʷséps téwe swésōr h₁ésti` (9) -> `léwbʰa h₂éwsos kʷséps téwe swésōr h₁ésti` (11)
- L2: `kʷséps légʰt stéh₂s-kʷe lówksneh₂ séngʷt wiHrṓs-kʷe bʰudʰént` (12) -> `kʷséps légʰt stéh₂s lówksneh₂ séngʷt wiHrṓs-kʷe bʰudʰént` (11)

English old: Dawn, Night is your sister. Night lay down, and you stood up. The moon sank, and the men woke. Dawn, shining, you come. Give us light, Dawn.

English new: Dear Dawn, Night is your sister. Night lay down; you stood up. The moon sank, and the men woke. Dawn, shining, you come. Give us light, Dawn.

### t011-0012 (hymn)

Edits:
    c1 [SUBJ:closed:relative_yo V:to shine [-ti: present v]: particle:None->nu
    c6 [MOD:big->that which is heard OBJ:that which is heard V:to give IO:closed:personal/1(PL) VOC:dawn MOD:good->that which is heard]: ADD MOD:good->that which is heard

Verse lines changed (old -> new, syllables):

- L2: `h₁yéh₂ ḱwinétsi h₁nédʰs léwks-kʷe` (7) -> `nu h₁yéh₂ ḱwinétsi h₁nédʰs léwks-kʷe` (8)
- L4: `h₂éwsos nos méǵh₂ ḱléwos dh₃dʰí` (9) -> `h₂éwsos nos méǵh₂ h₁wésu ḱléwos dh₃dʰí` (11)

English old: Bright Dawn, you drive swift horses. You who shine, you came forth and became bright. Your two horses stood up, and the men rejoiced. Give us great fame, Dawn.

English new: Bright Dawn, you drive swift horses. You who now shine, you came forth and became bright. Your two horses stood up, and the men rejoiced. Give us great and good fame, Dawn.

### t011-0013 (hymn)

Edits:
    c0 [VOC:wheel POSS:sun->wheel MOD:bright->wheel V:to shine]: particle:None->nu
    c3 [SUBJ:closed:relative_yo OBJ:path V:to light up]: particle:None->nu
    c5 [V:to stand up]: particle:None->ge
    c7 [PRED:big V:to be VOC:wheel]: conj:None->kʷe
    c8 [POSS:closed:personal/2->shine(SG) OBJ:shine V:to give (active) IO:closed:personal/1(PL)]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `sh₂wéns léwke kʷékʷle skondéyesi` (10) -> `nu sh₂wéns léwke kʷékʷle skondéyesi` (11)
- L3: `h₁yós stóygʰom lowkéyesi` (7) -> `nu h₁yós stóygʰom lowkéyesi` (8)
- L4: `h₁yód h₂éwsōs h₁ért stéh₂s h₂stéres-kʷe n̥ḱént` (10) -> `h₁yód h₂éwsōs h₁ért stéh₂s-ge h₂stéres-kʷe n̥ḱént` (11)
- L5: `kʷékʷle-ge méǵh₂s h₁ési` (7) -> `kʷékʷle-kʷe-ge méǵh₂s h₁ési` (8)
- L6: `téwe nos dyéwmn̥ h₁áydʰi` (7) -> `nu nos téwe dyéwmn̥ h₁áydʰi` (8)

English old: Bright wheel of the Sun, you shine. You who travel the path, you who bring warmth, you who light up the way! When Dawn arrived, you stood up, and the stars vanished. Great indeed are you, wheel. Give us your splendor.

English new: Now, bright wheel of the Sun, you shine. You who travel the path, you who bring warmth, you who then light up the way! When Dawn arrived, you indeed stood up, and the stars vanished. And great indeed are you, wheel. Now give us your splendor.

### t011-0014 (hymn)

Edits:
    c0 [VOC:sun OBJ:god(PL) OBJ:man(PL) V:to be looking at]: particle:None->nu
    c1 [V:to fall down]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `sóh₂wl̥ deywóns h₂nérn̥s-kʷe spéḱyesi` (10) -> `nu sóh₂wl̥ deywóns h₂nérn̥s-kʷe spéḱyesi` (11)
- L2: `séngʷs h₁regʷesyét-kʷe stéh₂s léwks-kʷe h₁ludʰét` (10) -> `séngʷs-ge h₁regʷesyét-kʷe stéh₂s léwks-kʷe h₁ludʰét` (11)

English old: Sun, you look upon the gods and men. You sank, and it grew dark; you stood up, and light came. Sun, climbing the sky, guard us.

English new: Now, Sun, you look upon the gods and men. You indeed sank, and it grew dark; you stood up, and light came. Sun, climbing the sky, guard us.

### t011-0015 (hymn)

Edits:
    c0 [POSS:closed:personal/2->stallion(SG) MOD:swift->stallion(DU) SUBJ:stallion(DU) OBJ:closed:personal/2(SG) V:to be transporting]: particle:None->nu DROP VOC:sun
    c3 [GOAL:path V:to go]: conj:kʷe->None
    c6 [OBJ:warmth OBJ:something bright V:to make reach IO:closed:personal/1(PL)]: particle:None->nu conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `sóh₂wl̥ te téwe HeHḱúh₁ h₁éḱwoh₁ wéǵʰetes` (12) -> `nu te téwe HeHḱúh₁ h₁éḱwoh₁ wéǵʰetes` (11)
- L2: `h₁yód h₂éwsōs h₁ért sth₂éh₁yetām póntoh₁m̥-kʷe gʷéh₂s` (12) -> `h₁yód h₂éwsōs h₁ért sth₂éh₁yetām póntoh₁m̥ gʷéh₂s` (11)
- L5: `gʷʰérmn̥ nos léwkm̥-kʷe h₁opéye` (9) -> `nu-kʷe nos gʷʰérmn̥ léwkm̥-kʷe h₁opéye` (11)

English old: Sun, your two swift horses carry you. When Dawn arrived, they stood, and you went along the path, you who light up the path. Your path is bright. Give us warmth and light.

English new: Now your two swift horses carry you. When Dawn arrived, they stood; you went along the path, you who light up the path. Your path is bright. And now give us warmth and light.

### t011-0016 (hymn)

Edits:
    c1 [SUBJ:closed:relative_yo OBJ:water V:to be heating MOD:swift->water]: ADD MOD:swift->water
    c3 [SUBJ:grain V:to grow (up)]: particle:None->nu
    c6 [OBJ:closed:demonstrative_so V:to be cooking VOC:sun MOD:dear->sun]: ADD MOD:dear->sun

Verse lines changed (old -> new, syllables):

- L2: `h₁yós wódr̥ gʷʰr̥néwsi wódr̥ gʷʰért` (9) -> `h₁yós HeHḱú wódr̥ gʷʰr̥néwsi wódr̥ gʷʰért` (11)
- L3: `dʰoHnéh₂ h₂wékst wiHrṓs-kʷe sh₂ént` (7) -> `nu dʰoHnéh₂ h₂wékst wiHrṓs-kʷe sh₂ént` (8)
- L4: `tā́m mē h₁éwses sóh₂wl̥ tā́m pékʷe` (9) -> `tā́m mē h₁éwses lewbʰóm sóh₂wl̥ tā́m pékʷe` (11)

English old: Sun, you who ripen the grain, you who heat the water! The water grew warm, the grain grew up, and the men were sated. Do not burn it; ripen it, Sun.

English new: Sun, you who ripen the grain, you who heat the swift water! The water grew warm, then the grain grew up, and the men were sated. Do not burn it; ripen it, dear Sun.

### t011-0017 (hymn)

Edits:
    c0 [VOC:fire (animate PRED:guest POSS:closed:personal/1->guest(PL) V:to be]: particle:None->nu
    c1 [SUBJ:closed:relative_yo V:to burn]: particle:None->nu
    c2 [SUBJ:closed:relative_yo OBJ:closed:personal/1(PL) V:to be heating]: particle:None->nu
    c6 [OBJ:closed:personal/1(PL) V:to burn (something)]: particle:None->nu DROP VOC:fire (animate

Verse lines changed (old -> new, syllables):

- L1: `h₁ń̥gʷney nos gʰóstis h₁ési` (7) -> `nu nos h₁ń̥gʷney gʰóstis h₁ési` (8)
- L2: `h₁yós dʰégʷʰesi h₁yós nos gʷʰr̥néwsi` (9) -> `nu h₁yós dʰégʷʰesi nu nos h₁yós gʷʰr̥néwsi` (11)
- L4: `h₁ń̥gʷney nos mē h₁éwses gʷʰérmn̥ nos dedh₃dʰí` (12) -> `nu nos mē h₁éwses gʷʰérmn̥ nos dedh₃dʰí` (11)

English old: Fire, you are our guest. You who burn, you who warm us! You came to us, you sat down, and we gave you a gift. Do not burn us, Fire. Give us warmth.

English new: Now, Fire, you are our guest. You who now burn, you who then warm us! You came to us, you sat down, and we gave you a gift. Now do not burn us. Give us warmth.

### t011-0018 (hymn)

Edits:
    c0 [VOC:fire (animate MOD:to be carrying->fire (animate OBJ:gift(PL) IO:god(PL) V:to be walking]: DROP POSS:closed:personal/1->gift(PL)
    c1 [SUBJ:closed:relative_yo GOAL:god(PL) V:to go]: particle:None->nu
    c3 [SUBJ:god(PL) V:to become joyful]: particle:None->ge
    c5 [OBJ:word POSS:closed:personal/1->word(PL) IO:god(PL) V:to be transporting VOC:fire (animate]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `déh₃neh₂ nos bʰéront h₁ń̥gʷney deywóybʰos gʷm̥sḱé` (12) -> `déh₃neh₂ bʰéront h₁ń̥gʷney deywóybʰos gʷm̥sḱé` (11)
- L2: `h₁yós deywóns h₁éysi h₁ludʰés` (7) -> `nu h₁yós deywóns h₁éysi h₁ludʰés` (8)
- L3: `deywṓs-kʷe mudént déh₃neh₂ h₁áyn̥to` (10) -> `deywṓs-kʷe-ge mudént déh₃neh₂ h₁áyn̥to` (11)
- L4: `h₁ń̥gʷney nos deywóybʰos wékʷos wéǵʰe` (10) -> `nu nos h₁ń̥gʷney deywóybʰos wékʷos wéǵʰe` (11)

English old: Fire, carrying our gifts to the gods, come! You who go to the gods, you arrived, and the gods became glad. They received the gifts. Convey our word to the gods, Fire.

English new: Fire, carrying gifts to the gods, come! You who now go to the gods, you arrived, and the gods indeed became glad. They received the gifts. Now convey our word to the gods, Fire.

### t011-0019 (hymn)

Edits:
    c2 [V:to become cold]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L2: `h₁regʷesyét stéwdt-kʷe wĺ̥kʷos gʷm̥sḱét` (9) -> `h₁regʷesyét stéwdt wĺ̥kʷos gʷm̥sḱét` (8)

English old: Fire, you light up the night. It grew dark and it grew cold; a wolf came. You stood up, and the wolf went away. Fire, do not vanish; shine on.

English new: Fire, you light up the night. It grew dark; it grew cold; a wolf came. You stood up, and the wolf went away. Fire, do not vanish; shine on.

### t011-0020 (hymn)

Edits:
    c0 [VOC:fire (the element SUBJ:closed:relative_yo V:to burn]: particle:None->nu
    c2 [SUBJ:closed:relative_yo OBJ:water V:to be heating MOD:swift->water]: ADD MOD:swift->water

Verse lines changed (old -> new, syllables):

- L1: `péh₂wr̥ h₁yód dʰégʷʰesi h₁yód pékʷesi` (10) -> `nu péh₂wr̥ h₁yód dʰégʷʰesi h₁yód pékʷesi` (11)
- L2: `h₁yód wódr̥ gʷʰr̥néwsi wédōr gʷʰért` (9) -> `h₁yód HeHḱú wódr̥ gʷʰr̥néwsi wédōr gʷʰért` (11)

English old: Fire, you who burn, you who cook, you who heat the water! The waters grew warm. We ate and were sated. Warm us, Fire.

English new: Now, Fire, you who burn, you who cook, you who heat the swift water! The waters grew warm. We ate and were sated. Warm us, Fire.

### t011-0021 (hymn)

Edits:
    c0 [VOC:water(PL) VOC:mother(PL) V:to hear]: DROP POSS:closed:personal/1->mother(PL)
    c1 [SUBJ:closed:relative_yo(PL) OBJ:sheep(PL) V:to be nourishing]: particle:None->nu
    c4 [SUBJ:Perkʷunos OBJ:closed:personal/2(PL) V:to free]: particle:None->ge
    c7 [V:to protect OBJ:closed:personal/1(PL)]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L1: `h₂ékʷeh₂es nos méh₂teres ḱluté` (9) -> `h₂ékʷeh₂es méh₂teres ḱluté` (8)
- L2: `h₁yéh₂es h₂ówins h₂élete` (7) -> `nu h₁yéh₂es h₂ówins h₂élete` (8)
- L4: `pérkʷunos usmé spért pró-kʷe gʷh₂té` (10) -> `pérkʷunos-ge usmé spért pró-kʷe gʷh₂té` (11)
- L5: `mē tr̥sih₁té stérgete-kʷe nos` (9) -> `mē tr̥sih₁té stérgete nos` (8)

English old: Waters, our mothers, hear! You who nourish the sheep, you who go to the sea. The serpent enclosed you; Perkʷunos set you free, and you went forth. Do not dry up, and protect us.

English new: Waters, mothers, hear! You who now nourish the sheep, you who go to the sea. The serpent enclosed you; Perkʷunos indeed set you free, and you went forth. Do not dry up; protect us.

### t011-0022 (hymn)

Edits:
    c3 [POSS:closed:personal/2->fish(SG) SUBJ:fish(PL) V:to swim]: particle:None->nu
    c4 [VOC:sea OBJ:closed:personal/1(PL) V:to swallow]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L3: `téwe dʰǵʰúHes sn̥h₂énti` (7) -> `nu téwe dʰǵʰúHes sn̥h₂énti` (8)
- L4: `móri nos mē gʷr̥h₃és h₂orkéye nos` (10) -> `móri-ge nos mē gʷr̥h₃és h₂orkéye nos` (11)

English old: Great Sea, great are you. You who swallow the waters! The waters went to you; your fish swim. Sea, do not swallow us; guard us.

English new: Great Sea, great are you. You who swallow the waters! The waters went to you; now your fish swim. Sea, indeed do not swallow us; guard us.

### t011-0023 (hymn)

Edits:
    c0 [VOC:water(PL) ABL:closed:personal/2(PL) SUBJ:sheep(PL) V:to live]: particle:None->ge
    c1 [ABL:closed:personal/2(PL) SUBJ:man(PL) V:to live]: particle:None->nu
    c2 [ABL:closed:personal/2(PL) SUBJ:fish(PL) V:to live]: particle:None->ge
    c4 [OBJ:field(PL) V:to fill]: conj:kʷe->None
    c5 [VOC:water(PL) V:to dry up]: conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `wédōr h₂óweyes usméd gʷíh₃wonti` (10) -> `wédōr-ge h₂óweyes usméd gʷíh₃wonti` (11)
- L2: `wiHrṓs usméd gʷíh₃wonti` (7) -> `nu wiHrṓs usméd gʷíh₃wonti` (8)
- L3: `dʰǵʰúHes usméd gʷíh₃wonti` (7) -> `dʰǵʰúHes-ge usméd gʷíh₃wonti` (8)
- L4: `diwés h₂wérst h₂éǵrons-kʷe pl̥nh₁té` (9) -> `diwés h₂wérst h₂éǵrons pl̥nh₁té` (8)
- L5: `nu wédōr mē tr̥sih₁té` (7) -> `nu-kʷe wédōr mē tr̥sih₁té` (8)

English old: Waters, from you the sheep live; from you men live; from you the fish live. It rained from the sky, and you filled the fields. Now, Waters, may you not dry up.

English new: Waters, from you indeed the sheep live; from you then men live; from you indeed the fish live. It rained from the sky; you filled the fields. And now, Waters, may you not dry up.

### t011-0024 (hymn)

Edits:
    c0 [VOC:mother OBJ:man(PL) OBJ:cattle(PL) V:to be holding up]: particle:None->nu DROP VOC:earth
    c6 [V:to dry up]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `dʰéǵʰom méh₂ter h₂nérn̥s gʷṓs-kʷe tetólh₂th₂e` (12) -> `nu méh₂ter h₂nérn̥s gʷṓs-kʷe tetólh₂th₂e` (11)
- L4: `nu nos bʰére mē-kʷe térs` (7) -> `nu nos bʰére mē-kʷe-ge térs` (8)

English old: Mother Earth, you hold up men and cattle. You who are stretched out, you who are productive! You drank the water and became green. Now carry us, and do not dry up.

English new: Now, Mother, you hold up men and cattle. You who are stretched out, you who are productive! You drank the water and became green. Now carry us, and indeed do not dry up.

### t011-0025 (hymn)

Edits:
    c0 [VOC:mother POSS:closed:personal/2->field(SG) OBJ:field V:to be ploughing]: particle:None->nu DROP VOC:earth
    c1 [SUBJ:closed:relative_yo OBJ:grain V:to be creating]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `dʰéǵʰom méh₂ter téwe h₂éǵrom h₂érh₃yomes` (12) -> `nu méh₂ter téwe h₂éǵrom h₂érh₃yomes` (11)
- L2: `h₁yéh₂ dʰoHnéh₂m tḗtḱsi h₁yéh₂ gʷṓs h₂élesi` (10) -> `nu h₁yéh₂ dʰoHnéh₂m tḗtḱsi h₁yéh₂ gʷṓs h₂élesi` (11)

English old: Mother Earth, we plough your field. You who create the grain, you who feed the cattle! The grain became green, the cattle were sated. Feed us.

English new: Now, Mother, we plough your field. You who then create the grain, you who feed the cattle! The grain became green, the cattle were sated. Feed us.

### t011-0026 (hymn)

Edits:
    c0 [VOC:earth VOC:mother LOC:foot(PL) V:to be lying flat]: DROP POSS:closed:personal/1->foot(PL)
    c1 [SUBJ:closed:relative_yo V:to live]: particle:None->nu
    c6 [OBJ:closed:personal/1(PL) V:to protect]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `dʰéǵʰom nos méh₂ter pedsú ḱéyth₂er` (9) -> `dʰéǵʰom méh₂ter pedsú ḱéyth₂er` (8)
- L2: `h₁yós gʷíh₃weti h₁épi te stéygʰeti` (10) -> `nu h₁yós gʷíh₃weti h₁épi te stéygʰeti` (11)
- L4: `stérge nos mē-kʷe nos léh₁s` (7) -> `stérge-ge nos mē-kʷe nos léh₁s` (8)

English old: Mother Earth, you lie beneath our feet. Whoever lives walks on you; whoever dies comes to you. You drank the water. Love us, and do not leave us.

English new: Mother Earth, you lie beneath the feet. Whoever now lives walks on you; whoever dies comes to you. You drank the water. Indeed love us, and do not leave us.

### t011-0027 (hymn)

Edits:
    c1 [ABL:sky ABL:earth V:to be begotten]: particle:None->ge
    c4 [V:to become big/strong]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L2: `diwés dʰǵʰmés-kʷe ǵeǵn̥h₁é` (7) -> `diwés-ge dʰǵʰmés-kʷe ǵeǵn̥h₁é` (8)
- L4: `Hwr̥dʰté pró-kʷe gʷh₂té h₂léksete nos` (10) -> `nu Hwr̥dʰté pró-kʷe gʷh₂té h₂léksete nos` (11)

English old: Now, gods, hear us! You are born of Sky and Earth. You who look upon men, you who give good things! You became strong and went forth. Protect us.

English new: Now, gods, hear us! You are indeed born of Sky and Earth. You who look upon men, you who give good things! Then you became strong and went forth. Protect us.

### t011-0028 (hymn)

Edits:
    c0 [PRED:praised(PL) V:to be]: particle:None->nu DROP VOC:god(PL)
    c2 [SUBJ:closed:relative_yo(PL) IO:closed:demonstrative_so(PL) OBJ:name MOD:heard->name V:to have put]: particle:None->nu conj:None->kʷe

Verse lines changed (old -> new, syllables):

- L1: `déywōs gʷr̥Htṓs h₁sté h₁yóy gʷérHtorn̥s ḱluté` (12) -> `nu gʷr̥Htṓs h₁sté h₁yóy gʷérHtorn̥s ḱluté` (11)
- L2: `h₁yóy tóybʰos ḱlutóm h₁nómn̥ dʰh₁té` (9) -> `nu-kʷe h₁yóy tóybʰos ḱlutóm h₁nómn̥ dʰh₁té` (11)

English old: Gods, you are praised. You who heard the praisers, you who set a famous name for them, you who gave imperishable fame! Hear us too.

English new: Now you are praised. You who heard the praisers, and you who then set a famous name for them, you who gave imperishable fame! Hear us too.

### t011-0029 (hymn)

Edits:
    c1 [VOC:god(PL) SUBJ:closed:relative_yo(PL) OBJ:water(PL) GOAL:sea V:to drive on MOD:dear->god]: ADD MOD:dear->god
    c2 [SUBJ:closed:relative_yo(PL) OBJ:earth V:to be holding up]: particle:None->nu DROP VOC:god(PL)

Verse lines changed (old -> new, syllables):

- L2: `déywōs h₁yóy wédōr móri ǵʰité` (9) -> `léwbʰōs déywōs h₁yóy wédōr móri ǵʰité` (11)
- L3: `déywōs h₁yóy dʰéǵʰōm tetl̥h₂é bʰérgʰete nos` (12) -> `nu h₁yóy dʰéǵʰōm tetl̥h₂é bʰérgʰete nos` (11)

English old: Gods, you who set the wheel of the sun in the sky, gods, you who drove the waters to the sea, gods, you who hold up the earth: guard us.

English new: Gods, you who set the wheel of the sun in the sky, dear gods, you who drove the waters to the sea, you who now hold up the earth: guard us.

### t011-0030 (hymn)

Edits:
    c0 [VOC:god(PL) V:to be walking GOAL:closed:personal/1(PL)]: particle:None->ge
    c3 [IO:closed:demonstrative_so(PL) OBJ:that which is heard MOD:good->that which is heard V:to give]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L1: `déywōs n̥smé gʷm̥sḱéte` (7) -> `déywōs-ge n̥smé gʷm̥sḱéte` (8)
- L3: `tóybʰos-kʷe h₁wésu ḱléwos dh₃té` (9) -> `tóybʰos h₁wésu ḱléwos dh₃té` (8)

English old: Gods, come to us! You came to our fathers, you drank the libation, and you gave them good fame. Come now to us, and sit down.

English new: Gods, come indeed to us! You came to our fathers, you drank the libation; you gave them good fame. Come now to us, and sit down.

### t011-0031 (prayer)

Edits:
    c0 [VOC:sky VOC:father OBJ:path MOD:long->path V:to go]: particle:None->ge
    c1 [OBJ:path POSS:closed:personal/1->path(PL) V:to straighten]: conj:None->kʷe
    c3 [SUBJ:dawn OBJ:closed:personal/1(PL) V:to lead MOD:dear->dawn]: ADD MOD:dear->dawn

Verse lines changed (old -> new, syllables):

- L1: `dyéw ph₂ter dweh₂róm póntoh₁m̥ h₁imés` (10) -> `dyéw-ge ph₂ter dweh₂róm póntoh₁m̥ h₁imés` (11)
- L2: `nu nos stóygʰom h₃roǵéye` (7) -> `nu-kʷe nos stóygʰom h₃roǵéye` (8)
- L3: `mē ḱm̥h₂ih₁mé h₂éwsōs nos wédʰoyh₁t` (9) -> `mē ḱm̥h₂ih₁mé lewbʰéh₂ nos h₂éwsōs wédʰoyh₁t` (11)

English old: Father Sky, we go a long path. Now make our way straight. May we not grow tired. May Dawn lead us.

English new: Father Sky, we indeed go a long path. And now make our way straight. May we not grow tired. May dear Dawn lead us.

### t011-0032 (prayer)

Edits:
    c1 [SUBJ:grain V:to grow]: particle:None->nu
    c2 [SUBJ:sheep(PL) V:to become sated]: particle:None->nu
    c3 [SUBJ:earth V:to dry up]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L2: `dʰoHnéh₂ bʰuh₂yéh₁t h₂óweyes sh₂ih₁ént` (9) -> `nu dʰoHnéh₂ bʰuh₂yéh₁t nu h₂óweyes sh₂ih₁ént` (11)
- L3: `dʰéǵʰōm mē tr̥syéh₁t wédōr mē n̥ḱyéh₁t` (10) -> `nu dʰéǵʰōm mē tr̥syéh₁t wédōr mē n̥ḱyéh₁t` (11)

English old: Gods, may it rain on our fields. May the grain grow, may the sheep be sated. May the earth not dry up, may the waters not vanish.

English new: Gods, may it rain on our fields. May the grain now grow, may the sheep then be sated. May the earth now not dry up, may the waters not vanish.

### t011-0033 (prayer)

Edits:
    c2 [OBJ:gift(PL) IO:closed:demonstrative_so V:to make reach]: particle:None->nu
    c4 [V:to be listening OBJ:closed:personal/1(PL)]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L2: `tósmey déh₃neh₂ h₁opéyomes sédt-kʷe` (10) -> `nu tósmey déh₃neh₂ h₁opéyomes sédt-kʷe` (11)
- L3: `ḱléwse nos gʰóstim ph₂sdʰí` (7) -> `ḱléwse-ge nos gʰóstim ph₂sdʰí` (8)

English old: Father Sky, a guest has arrived. He is dear. We give him gifts, and he has sat down. Hear us, and protect the guest.

English new: Father Sky, a guest has arrived. He is dear. We now give him gifts, and he has sat down. Hear us indeed, and protect the guest.

### t011-0034 (prayer)

Edits:
    c1 [V:to live]: particle:None->nu
    c2 [V:to grow (up)]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L2: `gʷíh₃woyh₁t h₂uksyéh₁t Hwr̥dʰyéh₁t` (6) -> `nu gʷíh₃woyh₁t h₂uksyéh₁t-ge Hwr̥dʰyéh₁t` (8)

English old: Gods, a son is born to us. May he live, may he grow, may he become strong. Protect him, and give him fame.

English new: Gods, a son is born to us. May he now live, may he indeed grow, may he become strong. Protect him, and give him fame.

### t011-0035 (prayer)

Edits:
    c0 [VOC:earth VOC:mother SUBJ:closed:relative_yo OBJ:closed:personal/1(PL) V:to be carrying MOD:dear->earth]: ADD MOD:dear->earth
    c1 [POSS:closed:personal/2->name(SG) MOD:heard->name OBJ:name V:to sing [-yeti: transiti]: particle:None->nu conj:None->kʷe
    c2 [V:to be satisfied]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `dʰéǵʰom nos méh₂ter h₁yéh₂ bʰéresi` (9) -> `léwbʰa nos dʰéǵʰom méh₂ter h₁yéh₂ bʰéresi` (11)
- L2: `téwe ḱlutóm h₁nómn̥ gʷéHyomes` (9) -> `nu-kʷe téwe ḱlutóm h₁nómn̥ gʷéHyomes` (11)
- L3: `tetr̥pmé tetl̥h₂dʰí nos` (7) -> `nu tetr̥pmé tetl̥h₂dʰí nos` (8)

English old: Mother Earth, you who carry us, we sing your famous name. We are satisfied. Hold us up.

English new: Dear Mother Earth, you who carry us, and now we sing your famous name. Now we are satisfied. Hold us up.

### t011-0037 (charm)

Edits:
    c0 [VOC:snake GOAL:closed:personal/1(PL) V:to be creeping]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `h₁ógʷʰey n̥smé mē sérpes` (7) -> `nu h₁ógʷʰey n̥smé mē sérpes` (8)

English old: Serpent, do not creep to us. Perkʷunos slew you. Die! Poison, dry up!

English new: Now, serpent, do not creep to us. Perkʷunos slew you. Die! Poison, dry up!

### t011-0038 (charm)

Edits:
    c0 [VOC:wolf GOAL:sheep(PL) V:to go to]: particle:None->nu
    c1 [VOC:dog OBJ:sheep(PL) V:to protect]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `wĺ̥kʷe h₂ówins mē h₁r̥sḱés` (7) -> `nu wĺ̥kʷe h₂ówins mē h₁r̥sḱés` (8)
- L2: `ḱwón h₂ówins h₂orkéye ḱwṓ bʰéwdʰeti` (10) -> `ḱwón-ge h₂ówins h₂orkéye ḱwṓ bʰéwdʰeti` (11)

English old: Wolf, do not go to the sheep. Dog, guard the sheep. The dog is awake, and the wolf is afraid. Sky has seen you.

English new: Now, wolf, do not go to the sheep. Dog, indeed guard the sheep. The dog is awake, and the wolf is afraid. Sky has seen you.

### t011-0039 (charm)

Edits:
    c0 [VOC:warmth ABL:head ADV:h1egjh V:to go (away)]: particle:None->nu
    c3 [VOC:warmth ADV:h2epo V:to go (away)]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `gʷʰérmn̥ kapwéts h₁eǵʰ litdʰí` (7) -> `nu gʷʰérmn̥ kapwéts h₁eǵʰ litdʰí` (8)
- L3: `gʷʰérmn̥ h₂epó litdʰí káput studdʰí` (10) -> `gʷʰérmn̥-ge h₂epó litdʰí káput studdʰí` (11)

English old: Heat, go out of the head. Head, become cold. Waters, go to the head. Heat, go away; head, become cold.

English new: Now, heat, go out of the head. Head, become cold. Waters, go to the head. Heat, indeed go away; head, become cold.

## Lines not fixed

Each is off target by 1 (or 2) and no single edit or pair of edits was found that keeps the content, the adjective-noun fit and the per-lexeme cap (most are two parallel relative or interrogative clauses of 12 syllables that need 11, or a line whose only fixes would exceed the cap on a lexeme). Left unchanged; the batch passes the gate regardless.

```
t011: 144/152 verse lines exact (0.947; gate meter_exact>=0.90 PASS); lexeme cap 6
t011-0002 (hymn) Rain for the Thirsty Earth
  L2 c1-2    12/11  -1  túH stonh₂éyesi túH dʰǵʰméy wédos dédeh₃si  [1, 4, 1, 1, 2, 3]
t011-0004 (hymn) Who Slew the Serpent?
  L4 c5-6    12/11  -1  kʷós stonh₂éyeti kʷós dʰǵʰméy wédos dédeh₃ti  [1, 4, 1, 1, 2, 3]
t011-0005 (hymn) Father Sky, Giver of Good Things
  L2 c1-2    12/11  -1  h₁yós léwkm̥ dédeh₃si h₁yós h₂stérn̥s kʷsépi dʰéh₁s  [1, 2, 3, 1, 2, 2, 1]
t011-0013 (hymn) Wheel of the Sun
  L2 c1-2    12/11  -1  h₁yós póntoh₁m̥ h₁éysi h₁yós gʷʰérmn̥ bʰéresi  [1, 3, 2, 1, 2, 3]
t011-0025 (hymn) Mother Earth, We Plough Your Field
  L3 c3-5    12/11  -1  dʰoHnéh₂ ǵʰelh₃wéh₂ bʰúHt gʷówes sh₂ént h₂éle nos  [2, 3, 1, 2, 1, 2, 1]
t011-0027 (hymn) Gods Born of Sky and Earth
  L1 c0       7/8  +1  nu nos déywōs ḱléwsete  [1, 1, 2, 3]
  L3 c2-3    12/11  -1  h₁yóy h₂nérn̥s spéḱyete h₁yóy h₁wésuh₂ dedh₃té  [1, 2, 3, 1, 2, 3]
t011-0028 (hymn) Gods Who Give Fame to the Praisers
  L3 c3-4    12/11  -1  h₁yóy ń̥dʰgʷʰitom ḱléwos h₁áyte ḱl̥nuté nos  [1, 3, 2, 2, 3, 1]
```

Engine notes: realize_plans now prints new WARN lines (verb-form homographs of h₂éǵeti 'drive'/'say', anaphoric_i referents); they concern unchanged clauses and do not fail the gate. Tool note: meter_report's vocative edit inserts at slot 0 without renumbering head/dep (reported by the coordinator); my edit pipeline shifted indices itself and I checked every changed plan.
