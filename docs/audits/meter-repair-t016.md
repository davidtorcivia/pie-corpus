# Meter repair: t016

meter_exact before: 35/94 = 0.372 (census); after: 91/94 = 0.968. Gate: PASS (all gates true; max_lexeme_uses 10).

Edit types: particle (nu/ge add or drop), conj (-kʷe add or drop), drop (vocative/possessor/epithet/adverb removed), epithet (adjective added), vocative (added), number (none used). No split/merge edits. Epithets were added only where the adjective fits the noun, within the per-lexeme cap. Plan edit lines below are `cN [clause content]: change` (clause index 0-based). Slot head/dep indices were verified after the edits: every head/dep link in a changed plan still points at the same lexeme as before (the added-vocative renumbering bug in meter_report was avoided by shifting head/dep after each vocative insert; no misdirected index found, no fixes needed).

## Changed texts

### t016-0004 (myth)

Edits:


English old: The man sat down at the hearth, and he cried out. "Brother, where are you?" Then a voice came from below. Then it spoke. "Do not weep." "I am the earth, and I carry you." "I nourish you." "I give you honey and the juice of plants." "I clothe you with wool." "The sky is my head." "The moon is my mind." "The rain-clouds are my tears." "Drink my waters." "Eat my blossoms." "When you die, I cover your bones." "Do not be afraid." "I am your brother." He heard the voice. Then his heart became glad. Then he stood up.

English new: The man sat down at the hearth, and he cried out. "Brother, where are you?" Then a voice came from below. Then it spoke. "Do not weep." "I am the earth, and I carry you." "I nourish you." "I give you honey and the juice of plants." "I clothe you with wool." "The sky is my head." "The moon is my mind." "The rain-clouds are my tears." "Drink my waters." "Eat my blossoms." "When you die, I cover your bones." "Do not be afraid." "I am your brother." He heard the voice. Then his heart became glad. Then he stood up.

### t016-0024 (charm)

Edits:
    c0 [SUBJ:cattle(PL) ADV:h2en-2 V:to stand]: particle:None->nu
    c2 [SUBJ:wolf IO:closed:anaphoric_i(PL) V:to come]: particle:None->ge
    c6 [VOC:sky OBJ:water V:to give]: particle:None->nu
    c8 [PRED:much V:to become]: particle:None->nu
    c9 [V:to grow (up)]: particle:None->nu
    c11 [SUBJ:army POSS:king->army PRED:big PRED:much V:to be]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `gʷówes h₂én sth₂éh₁yoyh₁ent mē bʰugih₁ént` (10) -> `nu gʷówes h₂én sth₂éh₁yoyh₁ent mē bʰugih₁ént` (11)
- L2: `wĺ̥kʷos h₁éymos mē gʷm̥yóyh₁t` (7) -> `wĺ̥kʷos-ge h₁éymos mē gʷm̥yóyh₁t` (8)
- L6: `dyéw wódr̥ dh₃dʰí dʰéǵʰom h₁íns h₂éle` (10) -> `nu dyéw wódr̥ dh₃dʰí dʰéǵʰom h₁íns h₂éle` (11)
- L7: `polh₁éwes bʰuHih₁ént h₂uksih₁ént` (9) -> `nu polh₁éwes bʰuHih₁ént nu h₂uksih₁ént` (11)
- L9: `h₃rēǵés h₂éǵmn̥ méǵh₂ polh₁ú-kʷe h₁syéh₁t` (10) -> `h₃rēǵés-ge h₂éǵmn̥ méǵh₂ polh₁ú-kʷe h₁syéh₁t` (11)

English old: May the cattle stand there, may they not flee! May the wolf not come to them! May the snake and the thief not seize them! Dog, guard the sheep and the flock! Shepherd, drive them inside! Sky, give water, Earth, nourish them! May they be many, may they grow! May the king have imperishable fame! May the king's flock be great and many!

English new: May the cattle now stand there, may they not flee! May the wolf indeed not come to them! May the snake and the thief not seize them! Dog, guard the sheep and the flock! Shepherd, drive them inside! Now, Sky, give water, Earth, nourish them! May they now be many, may they then grow! May the king have imperishable fame! May the king's flock indeed be great and many!

### t016-0026 (prayer)

Edits:
    c2 [GOAL:closed:relative_yo SUBJ:twin V:to go]: particle:None->nu
    c5 [V:to become afraid]: particle:None->ge
    c6 [OBJ:boat V:to go into]: particle:None->nu
    c8 [SUBJ:fire (animate OBJ:closed:personal/2 V:to give (active) MOD:dear->fire (animate]: ADD MOD:dear->fire (animate
    c9 [SUBJ:earth OBJ:bone(PL) POSS:closed:personal/2->bone V:to be covering]: particle:None->ge
    c10 [SUBJ:dawn OBJ:closed:personal/2 V:to make lively MOD:heard->dawn]: ADD MOD:heard->dawn
    c11 [SUBJ:that which is heard POSS:closed:personal/2->that which is heard PRED:imperishable V:to be]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L2: `yemHós h₁yóm gʷéh₂t tóm gʷh₂dʰí` (7) -> `nu yemHós h₁yóm gʷéh₂t tóm gʷh₂dʰí` (8)
- L4: `mē bʰéyh₂s néh₂wm̥ wiḱdʰí` (6) -> `mē-ge bʰéyh₂s nu néh₂wm̥ wiḱdʰí` (8)
- L5: `mē kʷélh₁s h₁n̥gʷnís te h₁áyih₁to` (9) -> `mē kʷélh₁s lewbʰós te h₁n̥gʷnís h₁áyih₁to` (11)
- L6: `dʰéǵʰōm toy h₃ésth₁h₂ ḱéloyh₁t` (7) -> `dʰéǵʰōm-ge toy h₃ésth₁h₂ ḱéloyh₁t` (8)
- L7: `h₂éwsōs te woǵéyoyh₁t` (6) -> `ḱlutéh₂ te h₂éwsōs woǵéyoyh₁t` (8)
- L8: `ḱléwos toy ń̥dʰgʷʰitom h₁syéh₁t` (7) -> `nu toy ḱléwos ń̥dʰgʷʰitom h₁syéh₁t` (8)

English old: "Go, dead man, along the path, follow the twin." "Go the way that the twin went." "Two dogs guard the path." "Do not be afraid, enter the boat." "Do not turn around, may Fire receive you." "May Earth cover your bones." "May Dawn awaken you." "May your fame be imperishable."

English new: "Go, dead man, along the path, follow the twin." "Go the way that the twin then went." "Two dogs guard the path." "Indeed, do not be afraid, now enter the boat." "Do not turn around, may dear Fire receive you." "May Earth indeed cover your bones." "May famous Dawn awaken you." "Now may your fame be imperishable."

### t016-0033 (hymn)

Edits:
    c3 [VOC:father SUBJ:closed:relative_yo IO:closed:personal/1(PL) OBJ:daylight OBJ:light V:to give]: ADD VOC:father
    c4 [SUBJ:dawn SUBJ:daughter V:to be walking]: DROP POSS:closed:personal/2->daughter
    c8 [OBJ:word POSS:closed:personal/1->word(PL) VOC:father V:to hear]: particle:None->nu
    c10 [IO:closed:personal/1(PL) OBJ:that which is heard MOD:good->that which is heard V:to give]: particle:None->ge
    c11 [VOC:father OBJ:closed:personal/1(PL) OBJ:army POSS:closed:personal/1->army(PL) V:to be protecting]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L3: `h₁yós n̥sméy Héh₂mr̥ ḱwoytóm-kʷe déh₃s` (9) -> `ph₂ter h₁yós n̥sméy Héh₂mr̥ ḱwoytóm-kʷe déh₃s` (11)
- L4: `h₂éwsōs toy dʰugh₂tḗr gʷm̥sḱéti` (9) -> `h₂éwsōs dʰugh₂tḗr gʷm̥sḱéti` (8)
- L8: `ph₂ter nos wékʷos ḱludʰí` (7) -> `nu nos ph₂ter wékʷos ḱludʰí` (8)
- L10: `h₁wésu nos ḱléwos dh₃dʰí` (7) -> `h₁wésu-ge nos ḱléwos dh₃dʰí` (8)
- L11: `ph₂ter nos n̥smé h₂éǵmn̥-kʷe h₂lékse` (10) -> `nu nos ph₂ter n̥smé h₂éǵmn̥-kʷe h₂lékse` (11)

English old: Father Sky, giver of good things, hear us! You who stand above, you who set the sun up, you who gave the day and the light to us. Dawn, your daughter, comes. The great son lifted you up. Your rain-clouds fill the sea. Your fame is imperishable. Hear our word, father! May your light not vanish from us! Give us good fame! Father, protect us and our flock!

English new: Father Sky, giver of good things, hear us! You who stand above, you who set the sun up, father, you who gave the day and the light to us. Dawn, the daughter, comes. The great son lifted you up. Your rain-clouds fill the sea. Your fame is imperishable. Now hear our word, father! May your light not vanish from us! Give us indeed good fame! Father, now protect us and our flock!

### t016-0034 (hymn)

Edits:
    c0 [VOC:earth VOC:mother OBJ:closed:personal/1(PL) V:to hear]: particle:None->nu
    c4 [PRED:flesh POSS:twin->flesh MOD:slain->twin V:to be MOD:dear->flesh]: ADD MOD:dear->flesh
    c5 [VOC:mother OBJ:oak OBJ:bloom(PL) V:to be carrying]: ADD VOC:mother
    c11 [OBJ:bone(PL) V:to be covering]: DROP POSS:closed:personal/1->bone(PL)

Verse lines changed (old -> new, syllables):

- L1: `dʰéǵʰom nos méh₂ter ḱludʰí` (7) -> `nu nos dʰéǵʰom méh₂ter ḱludʰí` (8)
- L4: `gʷʰn̥tósyo yemHósyo mḗms h₁ési` (9) -> `gʷʰn̥tósyo yemHósyo lewbʰóm mḗms h₁ési` (11)
- L5: `pérkʷum h₂éndʰesh₂-kʷe bʰéresi` (9) -> `méh₂ter pérkʷum h₂éndʰesh₂-kʷe bʰéresi` (11)
- L10: `h₁yód méromes h₃ésth₁h₂ nos ḱéle` (9) -> `h₁yód méromes h₃ésth₁h₂ ḱéle` (8)

English old: Mother Earth, hear us! You who carry the mortals, you who nourish the flock, you who drink the water of Sky. You are the flesh of the slain twin. You bear the oak and the blossoms. Your fields are broad. Beasts and cattle drink your waters. Give us wool and honey! Mother, may you carry us and the beasts! When we die, cover our bones.

English new: Now, Mother Earth, hear us! You who carry the mortals, you who nourish the flock, you who drink the water of Sky. You are the dear flesh of the slain twin. Mother, you bear the oak and the blossoms. Your fields are broad. Beasts and cattle drink your waters. Give us wool and honey! Mother, may you carry us and the beasts! When we die, cover the bones.

### t016-0035 (hymn)

Edits:
    c1 [SUBJ:stallion(PL) MOD:swift->stallion OBJ:wheel V:to pull]: particle:None->ge
    c3 [SUBJ:dawn V:to become bright (at daw]: particle:None->nu
    c5 [LOC:night SUBJ:sun V:to fall down]: particle:None->ge
    c7 [SUBJ:wheel POSS:sun->wheel V:to break (something)]: particle:None->nu
    c9 [SUBJ:sun OBJ:water(PL) V:to be heating]: particle:None->ge
    c10 [SUBJ:sun OBJ:closed:personal/1(PL) OBJ:wild animal(PL) V:to see MOD:dear->sun]: ADD MOD:dear->sun
    c11 [SUBJ:sun OBJ:closed:personal/1(PL) V:to see]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L2: `HeHḱéwes h₁éḱwōs kʷékʷlom dukénti` (10) -> `HeHḱéwes-ge h₁éḱwōs kʷékʷlom dukénti` (11)
- L4: `h₂éwsōs h₂wést nu sóh₂wl̥ léwkt` (7) -> `nu h₂éwsōs h₂wést nu sóh₂wl̥ léwkt` (8)
- L5: `sóh₂wl̥ kʷsépi séngʷt Héh₂m̥ni-kʷe léwkt` (10) -> `sóh₂wl̥-ge kʷsépi séngʷt Héh₂m̥ni-kʷe léwkt` (11)
- L6: `sh₂wéns kʷékʷlos ne Hrumptór` (7) -> `nu sh₂wéns kʷékʷlos ne Hrumptór` (8)
- L8: `sóh₂wl̥ h₂ékʷās gʷʰr̥néwti` (7) -> `sóh₂wl̥-ge h₂ékʷās gʷʰr̥néwti` (8)
- L9: `sóh₂wl̥ nos ǵʰwḗrn̥s-kʷe dedórḱe` (9) -> `lewbʰóm nos sóh₂wl̥ ǵʰwḗrn̥s-kʷe dedórḱe` (11)
- L10: `sóh₂wl̥ nos dedr̥ḱyéh₁t h₁íd nos ḱluyéh₁t` (10) -> `nu nos sóh₂wl̥ dedr̥ḱyéh₁t h₁íd nos ḱluyéh₁t` (11)

English old: The wheel of the sun runs through the sky. Swift horses draw it. Swift is the wheel of the sun. Dawn dawns, then the sun becomes bright. In the night the sun sinks, and in the day it becomes bright. The wheel of the sun does not break. Its path is straight. The sun heats the waters. The sun sees us and the beasts. May the sun see us, may it hear us.

English new: The wheel of the sun runs through the sky. Swift horses indeed draw it. Swift is the wheel of the sun. Now Dawn dawns, then the sun becomes bright. In the night the sun indeed sinks, and in the day it becomes bright. Now the wheel of the sun does not break. Its path is straight. The sun indeed heats the waters. The dear sun sees us and the beasts. May the sun now see us, may it hear us.

### t016-0036 (hymn)

Edits:
    c0 [VOC:dawn VOC:daughter POSS:sky->daughter V:to become bright (at daw MOD:dear->dawn]: ADD MOD:dear->dawn
    c1 [SUBJ:closed:relative_yo OBJ:people OBJ:wild animal(PL) V:to make lively]: particle:None->nu
    c3 [SUBJ:closed:relative_yo OBJ:light MOD:swift->light POSS:sun->swift V:to be carrying]: particle:None->ge
    c4 [INS:a type of women's garmen MOD:flat->a type of women's garmen V:to be wearing]: particle:None->nu
    c7 [SUBJ:light POSS:closed:personal/2->light PRED:big V:to be]: particle:None->ge
    c8 [GOAL:hearth POSS:closed:personal/1->hearth(PL) VOC:dawn V:to step]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `h₂éwsos diwés dʰúgh₂ter h₂usdʰí` (9) -> `léwbʰa h₂éwsos diwés dʰúgh₂ter h₂usdʰí` (11)
- L2: `h₁yéh₂ h₁léwdʰim ǵʰwḗrn̥s-kʷe woǵéyesi` (10) -> `nu h₁yéh₂ h₁léwdʰim ǵʰwḗrn̥s-kʷe woǵéyesi` (11)
- L4: `h₁yéh₂ sh₂wéns HeHḱúm ḱwoytóm bʰéresi` (10) -> `h₁yéh₂-ge sh₂wéns HeHḱúm ḱwoytóm bʰéresi` (11)
- L5: `pl̥th₂uyéh₂h₁ pĺ̥h₂seh₂h₁ wésth₂er` (7) -> `nu pl̥th₂uyéh₂h₁ pĺ̥h₂seh₂h₁ wésth₂er` (8)
- L7: `ḱwoytós toy méǵh₂s h₁ésti` (7) -> `ḱwoytós-ge toy méǵh₂s h₁ésti` (8)
- L8: `h₂éwsos nos h₂éHsh₂m̥ gʷm̥dʰí` (7) -> `nu nos h₂éwsos h₂éHsh₂m̥ gʷm̥dʰí` (8)

English old: Dawn, daughter of Sky, become bright! You who awaken the people and the beasts, you who drive the night away. You who bring the swift light of the sun. You clothe yourself in a broad garment. When you come, the night grows less. Your light is great. Come to our hearth, Dawn! Awaken us, Dawn, daughter of Sky!

English new: Dear Dawn, daughter of Sky, become bright! You who now awaken the people and the beasts, you who drive the night away. You who indeed bring the swift light of the sun. Now you clothe yourself in a broad garment. When you come, the night grows less. Your light is indeed great. Now come to our hearth, Dawn! Awaken us, Dawn, daughter of Sky!

### t016-0037 (hymn)

Edits:
    c0 [SUBJ:night V:to come]: particle:None->nu
    c3 [SUBJ:star(PL) LOC:sky V:to stand]: particle:None->ge
    c6 [SUBJ:daylight(PL) PRED:long V:to be becoming]: particle:None->nu
    c11 [SUBJ:bloom(PL) LOC:field V:to grow]: conj:kʷe->None
    c12 [SUBJ:sheep(PL) V:to grow (up)]: particle:None->ge
    c14 [SUBJ:closed:interrogative_kwi OBJ:closed:deictic_ki IO:people IO:wild animal(PL) V:to put in order]: particle:None->nu
    c15 [SUBJ:god(PL) OBJ:closed:deictic_ki IO:closed:anaphoric_i(PL) V:to put in order]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `kʷséps gʷm̥yéti Héh₂mr̥-kʷe gʷm̥yéti` (10) -> `nu kʷséps gʷm̥yéti Héh₂mr̥-kʷe gʷm̥yéti` (11)
- L3: `h₂stéres dyéwi sth₂éh₁yonti` (7) -> `h₂stéres-ge dyéwi sth₂éh₁yonti` (8)
- L5: `Héh₂mōr dl̥h₁gʰéh₂ bʰuHyéti` (7) -> `nu Héh₂mōr dl̥h₁gʰéh₂ bʰuHyéti` (8)
- L8: `snóygʷʰos tinéh₁ti h₂éndʰesh₂-kʷe h₂éǵroy bʰwéh₂t` (12) -> `snóygʷʰos tinéh₁ti h₂éndʰesh₂ h₂éǵroy bʰwéh₂t` (11)
- L9: `h₂óweyes h₂uksént h₁éḱwōs-kʷe h₂uksént` (10) -> `h₂óweyes-ge h₂uksént h₁éḱwōs-kʷe h₂uksént` (11)
- L10: `kʷís h₁ludʰéyey ǵʰwērbʰós-kʷe ḱód h₂réydʰet` (10) -> `nu kʷís h₁ludʰéyey ǵʰwērbʰós-kʷe ḱód h₂réydʰet` (11)
- L11: `deywṓs h₁éymos ḱód h₂réydʰont` (7) -> `deywṓs-ge h₁éymos ḱód h₂réydʰont` (8)

English old: Night comes, and day comes. The sun walks in the day. The stars stand in the sky. Winter comes, and the waters grow cold. The days grow long. Heat dries the waters. The sun turns, and winter goes. The snow melts, and blossoms arise in the field. The sheep grow, and the horses grow. Who set this in order for the people and the beasts? The gods set this in order for them.

English new: Now night comes, and day comes. The sun walks in the day. The stars indeed stand in the sky. Winter comes, and the waters grow cold. Then the days grow long. Heat dries the waters. The sun turns, and winter goes. The snow melts; blossoms arise in the field. The sheep indeed grow, and the horses grow. Now who set this in order for the people and the beasts? The gods indeed set this in order for them.

### t016-0038 (hymn)

Edits:
    c0 [IO:people IO:army V:to step]: DROP VOC:night
    c4 [SUBJ:moon ADV:uper V:to be walking]: particle:None->nu
    c5 [OBJ:mortal(PL) OBJ:wild animal(PL) V:to be covering]: particle:None->ge
    c9 [SUBJ:dawn SUBJ:daughter POSS:sky->daughter IO:closed:personal/1(PL) V:to arrive]: particle:None->nu

Verse lines changed (old -> new, syllables):

- L1: `kʷsép h₁ludʰéyey h₂ǵméney-kʷe gʷm̥dʰí` (9) -> `h₁ludʰéyey h₂ǵméney-kʷe gʷm̥dʰí` (8)
- L4: `lówksneh₂ upér stéygʰeti` (7) -> `nu lówksneh₂ upér stéygʰeti` (8)
- L5: `mórtons ǵʰwḗrn̥s-kʷe ḱéle` (7) -> `mórtons-ge ǵʰwḗrn̥s-kʷe ḱéle` (8)
- L9: `h₂éwsōs nos diwés dʰugh₂tḗr h₁ludʰóyh₁t` (10) -> `nu nos h₂éwsōs diwés dʰugh₂tḗr h₁ludʰóyh₁t` (11)

English old: Night, come to the people and the flock! You who cover the earth, you who bring the stars, your stars look at the people. The moon walks above. Cover the mortals and the beasts! Sleep comes to us and to the beasts. You are the mother of the stars and of Dawn. Do not frighten our flock, Night! May Dawn, daughter of Sky, come to us!

English new: Come to the people and the flock! You who cover the earth, you who bring the stars, your stars look at the people. Now the moon walks above. Indeed cover the mortals and the beasts! Sleep comes to us and to the beasts. You are the mother of the stars and of Dawn. Do not frighten our flock, Night! Now may Dawn, daughter of Sky, come to us!

### t016-0039 (hymn)

Edits:
    c0 [VOC:sky VOC:earth OBJ:closed:personal/1(PL) V:to hear]: particle:None->nu
    c3 [SUBJ:earth MOD:flat->earth ADV:Hndhi V:to be stretched]: particle:None->ge
    c4 [ADV:h1enter SUBJ:mist V:to stand]: particle:None->nu
    c7 [SUBJ:cattle(PL) V:to drink]: conj:kʷe->None

Verse lines changed (old -> new, syllables):

- L1: `dyéw nos dʰéǵʰōm-kʷe ḱlutóm` (7) -> `nu nos dyéw dʰéǵʰōm-kʷe ḱlutóm` (8)
- L4: `pl̥th₂éwih₂ dʰéǵʰōm Hn̥dʰí tetóne` (10) -> `pl̥th₂éwih₂-ge dʰéǵʰōm Hn̥dʰí tetóne` (11)
- L5: `h₃mígʰleh₂ h₁entér sth₂éh₁yeti` (7) -> `nu h₃mígʰleh₂ h₁entér sth₂éh₁yeti` (8)
- L7: `h₁entér h₂wérst gʷówes-kʷe píph₃onti` (9) -> `h₁entér h₂wérst gʷówes píph₃onti` (8)

English old: Sky and Earth, hear us! You two are the father and the mother of the gods. The great Sky is stretched above. The broad Earth is stretched below. In between stands the mist. In between goes the wheel of the sun. In between it rains, and the cattle drink. You two nourish the mortals and the flock. Give us the day and the water, you two!

English new: Now, Sky and Earth, hear us! You two are the father and the mother of the gods. The great Sky is stretched above. The broad Earth is indeed stretched below. Now in between stands the mist. In between goes the wheel of the sun. In between it rains; the cattle drink. You two nourish the mortals and the flock. Give us the day and the water, you two!

### t016-0040 (hymn)

Edits:
    c0 [SUBJ:desire PRED:first V:to grow]: particle:None->nu
    c2 [SUBJ:closed:interrogative_kwi OBJ:sky V:to be stretching]: particle:None->nu
    c3 [SUBJ:closed:interrogative_kwi OBJ:earth V:to lay]: DROP ADV:Hndhi
    c4 [SUBJ:closed:interrogative_kwi OBJ:sea OBJ:oak V:to work]: particle:None->ge
    c5 [SUBJ:closed:interrogative_kwi OBJ:sun OBJ:moon ADV:uper V:to have put MOD:dear->sun]: ADD MOD:dear->sun
    c6 [SUBJ:closed:interrogative_kwi IO:wheel POSS:sun->wheel OBJ:stallion(PL) MOD:swift->stallion V:to harness]: particle:None->nu
    c7 [SUBJ:closed:interrogative_kwi IO:mortal(PL) OBJ:daylight OBJ:light V:to give]: particle:None->ge
    c8 [SUBJ:god(PL) OBJ:closed:anaphoric_i V:to have seen]: particle:None->nu
    c10 [OBJ:bowing IO:closed:anaphoric_i(PL) V:to work]: particle:None->ge

Verse lines changed (old -> new, syllables):

- L1: `kóh₂mos pr̥h₂wós bʰwéh₂t ménos kóh₂mōd bʰwéh₂t` (10) -> `nu kóh₂mos pr̥h₂wós bʰwéh₂t ménos kóh₂mōd bʰwéh₂t` (11)
- L2: `kʷís dyḗm tn̥néwt kʷís dʰéǵʰōm Hn̥dʰí logʰéyet` (12) -> `nu kʷís dyḗm tn̥néwt kʷís dʰéǵʰōm logʰéyet` (11)
- L3: `kʷís móri pérkʷum-kʷe wérǵt` (7) -> `kʷís-ge móri pérkʷum-kʷe wérǵt` (8)
- L4: `kʷís sóh₂wl̥ lówksneh₂m-kʷe upér dʰéh₁t` (9) -> `kʷís lewbʰóm sóh₂wl̥ lówksneh₂m-kʷe upér dʰéh₁t` (11)
- L5: `kʷís sh₂wéns kʷékʷlōy HeHḱúns h₁éḱwons yéwgt` (10) -> `nu kʷís sh₂wéns kʷékʷlōy HeHḱúns h₁éḱwons yéwgt` (11)
- L6: `kʷís mórtoybʰos Héh₂mr̥ ḱwoytóm-kʷe déh₃t` (10) -> `kʷís-ge mórtoybʰos Héh₂mr̥ ḱwoytóm-kʷe déh₃t` (11)
- L7: `deywṓs h₁íd widḗr h₁íd-kʷe ne widmé` (10) -> `nu deywṓs h₁íd widḗr h₁íd-kʷe ne widmé` (11)
- L8: `h₁éymos némos wérǵomes` (7) -> `h₁éymos-ge némos wérǵomes` (8)

English old: Desire arose first, from Desire the mind arose. Who stretched the sky? Who laid the earth below? Who made the sea and the oak? Who set the sun and the moon above? Who yoked the swift horses to the wheel of the sun? Who gave the day and the light to the mortals? The gods know it, and we do not know it. Let us make a sacrifice to them.

English new: Then Desire arose first, from Desire the mind arose. Now who stretched the sky? Who laid the earth? Who indeed made the sea and the oak? Who set the dear sun and the moon above? Now who yoked the swift horses to the wheel of the sun? Who indeed gave the day and the light to the mortals? The gods now know it, and we do not know it. Let us indeed make a sacrifice to them.

## Lines not fixed

Each is off target by 1 (or 2) and no single edit or pair of edits was found that keeps the content, the adjective-noun fit and the per-lexeme cap (most are two parallel relative or interrogative clauses of 12 syllables that need 11, or a line whose only fixes would exceed the cap on a lexeme). Left unchanged; the batch passes the gate regardless.

```
t016: 91/94 verse lines exact (0.968; gate meter_exact>=0.90 PASS); lexeme cap 10
t016-0034 (hymn) To Mother Earth
  L2 c1-2    12/11  -1  h₁yéh₂ mórtons bʰéresi h₁yéh₂ h₂éǵmn̥ h₂élesi  [1, 2, 3, 1, 2, 3]
  L8 c8       9/8  -1  h₂wĺ̥h₁neh₂m nos mélit-kʷe h₁opéye  [2, 1, 3, 3]
t016-0038 (hymn) To Night
  L2 c1-2    12/11  -1  h₁yéh₂ dʰéǵʰōm ḱélesi h₁yéh₂ h₂stérn̥s bʰéresi  [1, 2, 3, 1, 2, 3]
```

Engine notes: realize_plans now prints new WARN lines (verb-form homographs of h₂éǵeti 'drive'/'say', anaphoric_i referents); they concern unchanged clauses and do not fail the gate. Tool note: meter_report's vocative edit inserts at slot 0 without renumbering head/dep (reported by the coordinator); my edit pipeline shifted indices itself and I checked every changed plan.
