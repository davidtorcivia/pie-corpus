"""Test A (knee-sleep typological control), East Asia / Finnic / Arabic: apply the hand classification.

Run: python -I scripts/knee_sleep_testA_east_search.py <root> <cands.jsonl>
     python -I scripts/knee_sleep_testA_east_build.py <cands.jsonl> data/research/knee-sleep/testA-east.jsonl

Every candidate window written by the search script was read in context (wider context was pulled
from the raw file where the window was not enough). The decisions below are keyed by candidate id;
the script refuses to run if any candidate is unclassified, so a changed search forces a re-read.

classification: positive | contrast | not-target
explicit (positives only): true = knee supports a participant who is narrated as asleep / dreaming /
dying as sleep (the pre-registered "explicit positive"); false = knee-pillowing or lying on the knee
with no sleep word, or sleep only proposed. Only explicit positives enter the decision rule.
"""
import json
import sys
from collections import OrderedDict

P, C, N = "positive", "contrast", "not-target"

# (classification, explicit, tags, reason)
CLS = {
    # ---- Japanese kanbun (Kojiki 712, Nihon shoki 720) ----
    "c00000": (N, None, [], "monkey asleep; a man grabs its arm: arm is not a support"),
    "c00001": (N, None, ["death"], "fallen corpses lie pillowed on arms (place-name aetiology 頬枕田): death, not sleep; arm"),
    "c00002": (P, True, ["dream", "knee-pillow", "sovereign"], "Suinin 5: the emperor sleeps by day pillowed on the empress's knee (枕皇后膝而晝寢), wakes and tells his dream (朕今日夢矣)"),
    "c00003": (P, True, ["dream", "knee-pillow", "sovereign", "same-episode"], "same Suinin episode, Saho-hime's confession: 天皇枕妾膝而寢之 ... 故今日夢; one scene with c00002"),
    "c00004": (N, None, ["knee-pillow", "awake"], "Nintoku 40: Hayabusawake lies (以臥) pillowed on the princess's knee but is talking: awake"),
    "c00005": (P, True, ["knee-pillow", "sovereign", "death-in-sleep"], "Yuryaku前紀 (Anko 3): Anko lies drunk asleep by day pillowed on the empress's knee (枕皇后膝。晝醉眠臥) and is stabbed in his deep sleep (伺其熟睡而刺殺之). The Kojiki parallel (下卷) has 坐神牀而晝寢 with no knee"),
    "c00006": (P, True, ["knee-pillow", "sovereign"], "Kojiki Suinin: the emperor, unaware of the plot, sleeps pillowed on the empress's knee (枕其后之御膝。爲御寢坐也); she cannot stab him and her tears wake him"),
    # ---- Man'yoshu (wikisource 訓読/仮名) and ONCOJ ----
    "c00013": (N, None, ["kneeling"], "MYS 3.379 膝折り伏して 'bending the knees and prostrating' in worship: kneeling"),
    "c00014": (N, None, ["kneeling", "dup"], "MYS 3.379 kana line of c00013"),
    "c00085": (N, None, ["kneeling", "dup"], "MYS 3.379 in ONCOJ (piza wori pusite): kneeling"),
    "c00023": (N, None, ["knee-pillow", "dream-frame", "borderline"], "MYS 5.810 (Tabito, 729): a zither that turned into a maiden in a dream (此琴夢化娘子) asks when it may pillow on the knee of one who knows its voice (人の膝の上我が枕かむ). The knee-pillow is the zither's wish; the dreamer is not the one on the knee and no one sleeps on it"),
    "c00024": (N, None, ["dup"], "MYS 5.810 kana line of c00023"),
    "c00088": (N, None, ["dup"], "MYS 5.810 in ONCOJ (piza no pe wa ga makuraka mu)"),
    "c00029": (N, None, ["object-on-knee"], "MYS 7.1328 膝に伏す玉の小琴 'the jewelled zither that lies on the knee': an instrument, not a sleeper"),
    "c00030": (N, None, ["dup"], "MYS 7.1328 kana line"),
    "c00091": (N, None, ["dup"], "MYS 7.1328 in ONCOJ"),
    "c00054": (P, False, ["knee-pillow", "lover", "phonographic"], "MYS 14.3457 (Azuma-uta): 大和女の膝まくごとに 'each time you pillow on the knee of a Yamato woman, do not forget me'. 原文 比射麻久 is phonographic, i.e. native Old Japanese, not a Sinitic phrase. Pillow verb maku = lie/sleep with, but no sleep word"),
    "c00055": (P, False, ["dup"], "MYS 14.3457 kana line of c00054"),
    "c00079": (P, False, ["dup", "phonographic"], "MYS 14.3457 in ONCOJ: yamato mye no piza maku (PHON)"),
    # ---- Genji (c. 1000-1010) ----
    "c00095": (P, False, ["knee-pillow", "invitation"], "Wakamurasaki: the child says she is sleepy; Genji: この膝の上に大殿籠もれよ 'sleep on my knee'. Sleep proposed, not narrated"),
    "c00097": (P, True, ["lean-on-knee", "child"], "Momiji no ga: young Murasaki leans against Genji's knee and falls asleep (御膝に寄りかかりて、寝入りたまひぬれば)"),
    "c00114": (N, None, ["child-on-knee", "awake"], "Suma: (the boy) set on his knee (膝に据ゑたまへる): no sleep"),
    "c00115": (N, None, ["kneeling"], "Fuji no uraba: 膝をつきて奏す 'kneels and reports'; 寝 is 寝殿 'main hall'"),
    "c00098": (C, None, ["arm-pillow"], "Tokonatsu: the lady lies with her arm as pillow (かひなを枕にて), lounging; arm, not knee"),
    "c00104": (C, None, ["arm-pillow", "sleep"], "Agemaki: Naka no kimi dozing, 腕を枕にて寝たまへる 'sleeping with her arm as pillow'"),
    "c00108": (C, None, ["arm-pillow"], "Ukifune: the girl, arm as pillow (腕を枕にて), gazes at the fire: awake"),
    "c00110": (C, None, ["arm-pillow", "lover"], "Aoi: 新手枕 'the new arm-pillow' (first night with Murasaki), the lover's sleep support"),
    "c00106": (N, None, [], "Yadorigi: lady lies prone, holds out her arm: not a support"),
    "c00116": (N, None, ["bosom"], "Wakana jo: 賤しき懐のうちにも 'within my humble bosom' (= care, upbringing), with dream talk; not a sleep support"),
    # ---- Chinese (Kanripo) knee ----
    "c00123": (N, None, ["kneeling"], "Shiji 86 (Jing Ke): the crown prince 膝行 'moves on his knees'; 死 belongs to Tian Guang's suicide"),
    "c00125": (N, None, [], "Hanshu 23 commentary: 髕 punishment removes the knee bone; 死刑 nearby"),
    "c00128": (N, None, ["death-on-knee", "knee-pillow"], "Hanshu 88 (Meng Xi): Meng falsely claimed his master Tian died pillowed on his knee (且死時枕喜膝) and passed the Yi to him alone. Dying on the knee, no sleep framing (2 Kgs 4:20 type)"),
    "c00129": (N, None, [], "Hou Hanshu 76: 坐必端膝 'sits with knees straight' (decorum); 死 elsewhere"),
    "c00131": (N, None, [], "Hou Hanshu 104 commentary: 撫膝而泣 'strike knees and weep'; 土崩 'collapse'"),
    "c00133": (P, False, ["knee-pillow", "lying"], "Sanguozhi 16 (Su Ze): Dong Zhao once lay pillowed on Su Ze's knee (枕則膝臥); Su pushed him off: 'my knee is no flatterer's pillow'. Lying, no sleep word"),
    "c00134": (P, False, ["dup"], "Sanguozhi 16, same sentence as c00133"),
    "c00135": (N, None, ["wound"], "Sanguozhi 17: an arrow strikes Zhang He's right knee and he dies: knee wound"),
    "c00136": (N, None, ["own-knees", "borderline"], "Sanguozhi 24 commentary (Weishi chunqiu): Gao Rou so diligent he 擁膝抱文書而寢 'slept clasping his knees and hugging his documents': sitting asleep, knees clasped rather than a support"),
    "c00137": (N, None, [], "Sanguozhi 29: a horse bites Cao Pi's knee; deaths nearby"),
    "c00138": (N, None, ["dup"], "Sanguozhi: same passage text as c00137, repeated in a later juan file"),
    "c00139": (N, None, ["knee-pillow", "dream-content"], "Jinshu 1 (Sima Yi): he dreamed the Son of Heaven pillowed on his knee (夢天子枕其膝). The pillowing figure is dreamed, not the dreamer; no sleeper on the knee"),
    "c00140": (N, None, ["death-on-knee", "knee-pillow"], "Jinshu 31 (Empress Yang Yan): on her deathbed she pillows on the emperor's knee (臨終枕帝膝) and speaks; c00141 she dies on his knee. Death on the knee, no sleep framing"),
    "c00141": (N, None, ["death-on-knee"], "Jinshu 31: 崩于明光殿，絶于帝膝 'expired on the emperor's knee'"),
    "c00143": (N, None, ["dup", "death-on-knee"], "Jinshu file 033 repeats juan 31 text (repo duplicate of c00140)"),
    "c00144": (N, None, ["dup", "death-on-knee"], "repo duplicate of c00141"),
    "c00142": (N, None, ["knee-pillow", "dream-content"], "Jinshu 32 (Empress Li): she often dreamed two dragons pillowed on her knees (數夢兩龍枕膝) and sun and moon entered her bosom: omen dream, the pillowers are dragons"),
    "c00145": (N, None, ["dup", "dream-content"], "repo duplicate of c00142"),
    "c00148": (N, None, ["knee-pillow", "awake", "recall"], "Shishuo xinyu: Wang Dao pillows on Zhou Yi's knee (枕周伯仁膝, spelled 䣛) and points at his belly, joking: awake. Recall item for the 䣛 variant"),
    "c00154": (P, True, ["knee-pillow", "sovereign"], "Taiping guangji 38 (Li Mi, from 鄴侯外傳): Li Mi asks as his only reward to sleep once pillowed on the Son of Heaven's knee (但枕天子膝睡一覺)"),
    "c00155": (P, True, ["knee-pillow", "sovereign", "same-episode"], "same story, fulfilled: Li Mi falls asleep (寐); Suzong lifts his head onto his knee (捧泌首置於膝), and after a long while he wakes (良久方覺): 'the Son of Heaven's knee has been pillowed'"),
    "c00156": (N, None, [], "TPGJ 66: sleeping day and night, a seal-mark appears on both knees: no support"),
    "c00162": (N, None, ["apron"], "TPGJ 161: 蔽膝 'knee-cover, apron' hidden under a mat"),
    "c00163": (N, None, ["apron", "dup"], "TPGJ 161 same apron"),
    "c00166": (N, None, ["own-knees", "borderline"], "TPGJ 238: a creature sits with knees bound, back to a pillar, head bowed asleep: sitting, not on a knee"),
    "c00167": (N, None, [], "TPGJ 268: torture list (tiles under the knees); 臥 on thorns"),
    "c00174": (N, None, ["wound"], "TPGJ 279: sores on the knee, feet drop off, he dies; a dream omen"),
    "c00175": (N, None, [], "TPGJ 290: 促膝密坐 'sit knee to knee'; 廢寢 'forgo sleep'"),
    "c00177": (N, None, ["apron"], "TPGJ 314: 蔽膝 apron; 卒 'soldier'"),
    "c00178": (N, None, [], "TPGJ 318: sword laid across the knees; 以死拒之"),
    "c00179": (N, None, [], "TPGJ 327: before sleeping, something taps his knee"),
    "c00182": (N, None, ["child-on-knee", "ghost"], "TPGJ 355: a dead son returns and sits on his mother's knee, talking: awake"),
    "c00183": (N, None, [], "TPGJ 480 (= Youyang zazu 4): buried knees turn into people after 120 years"),
    "c00184": (N, None, [], "Bowu zhi 10: soak in cold water to the knee"),
    "c00185": (N, None, ["dup"], "Youyang zazu 4: same as c00183"),
    "c00186": (N, None, [], "Youyang zazu: woman sits knee to knee (接膝而坐); the scholar lies drunk elsewhere"),
    "c00191": (N, None, ["child-on-knee"], "Du Fu, Qiang cun: 嬌兒不離膝 'my child won't leave my knee'; 寐 is in the preceding poem's line"),
    "c00193": (N, None, [], "QTS 234: 'my brother sleeps soundly, then stretches his knees'"),
    "c00195": (N, None, [], "QTS 277: old man's knees above his chin; 臥 to scare birds"),
    "c00197": (N, None, ["kneeling"], "QTS 369: a monk's knees have worn marks in his niche"),
    "c00199": (N, None, [], "Bai Juyi: quilt wraps both knees while he naps: no knee support"),
    "c00202": (N, None, ["object-on-knee"], "QTS 450: a zither on the knee; 死 elsewhere"),
    "c00206": (N, None, [], "QTS 492: 容膝 'room for the knees' (tiny dwelling)"),
    "c00208": (N, None, ["object"], "QTS 583: 金夾膝 'gold knee-clasp', a bed object; dream"),
    "c00210": (N, None, ["apron"], "QTS 683: 蔽膝 apron"),
    "c00216": (N, None, ["death-on-knee", "knee-pillow"], "QTS 801 (Yang girl of Yuexi, prose note): 即以首枕其膝而逝 'laid her head on his knee and passed away'. Death on the knee, no sleep framing"),
    "c00217": (N, None, [], "QTS 828 note: 不皴膝 'never chafed his knees' (always sat, never lay)"),
    "c00219": (N, None, ["kneeling"], "Zhuangzi 11: Guangchengzi lies facing south; the Yellow Emperor approaches on his knees (膝行)"),
    # ---- Chinese contrasts ----
    "c00118": (C, None, ["thigh", "death", "mourning"], "Zuozhuan (公知其無罪也，枕之股而哭之): the lord pillows the dead man on his thigh and weeps: mourning rite, thigh"),
    "c00119": (C, None, ["thigh", "death", "mourning"], "Zuozhuan Xiang 25: Yanzi pillows the corpse on his thigh and weeps (枕尸股而哭)"),
    "c00120": (C, None, ["thigh", "death", "mourning"], "Zuozhuan: 衣其尸，枕之股而哭之 over a corpse"),
    "c00121": (C, None, ["thigh", "death", "mourning"], "Zuozhuan Xiang 30: Zichan pillows the dead Boyou on his thigh and weeps"),
    "c00122": (C, None, ["thigh", "sleep", "sovereign"], "Shiji (Chu King Ling story): King Ling, starving, sleeps pillowed on the thigh of the attendant (王因枕其股而臥), who slips away leaving a clod"),
    "c00146": (C, None, ["thigh", "sleep", "sovereign"], "Guoyu, Wu yu: same story, explicit: 王枕其股以寢於地。王寐，疇枕王以墣而去之"),
    "c00132": (C, None, ["thigh", "death", "mourning"], "Sanguozhi 4 commentary: Sima Fu pillows the dead emperor on his thigh and weeps"),
    "c00168": (C, None, ["thigh", "death", "mourning"], "TPGJ 274: Cui lifts the dead girl's head onto his thigh, weeps, prays; she revives"),
    "c00196": (C, None, ["thigh", "death", "mourning", "dup"], "QTS 368 note: same story as c00168"),
    "c00190": (C, None, ["thigh", "sleep"], "QTS 172 (Li Bai): 我醉横眠枕其股 'drunk, I sprawl asleep pillowed on his thigh'"),
    "c00153": (C, None, ["arm", "lover"], "Soushen ji 19: a woman (really a giant turtle) lies pillowed on his arm (枕臂而臥)"),
    "c00189": (C, None, ["arm", "sleep"], "QTS 23: 寢臂幽夢長 'sleeping on an arm, a long dark dream'"),
    "c00198": (C, None, ["arm", "sleep", "dup"], "QTS 382: same line as c00189"),
    "c00200": (C, None, ["arm", "sleep", "own"], "QTS 439 (Bai Juyi): 中宵枕臂眠 'at midnight sleeps pillowed on his arm'"),
    "c00201": (C, None, ["arm", "sleep", "own"], "QTS 448: 枕臂火爐前 napping"),
    "c00204": (C, None, ["arm", "sleep", "own"], "QTS 460: 擁袍枕臂醉眠"),
    "c00211": (C, None, ["arm", "sleep", "lover"], "QTS 683: 鴛鴦枕臂眠 lovers' arm-pillow"),
    "c00203": (C, None, ["arm", "sleep", "own"], "QTS 458: 曲肱一覺醉中眠 (Analects allusion)"),
    "c00205": (C, None, ["arm", "own"], "QTS 467: 醉後曲肱林下卧"),
    "c00207": (C, None, ["arm", "own"], "QTS 518: 寒牀但枕肱"),
    "c00130": (N, None, [], "Hou Hanshu 83: 肱臥 in the portrait story; obscure, not a support scene"),
    "c00124": (N, None, ["sexual"], "Shiji 118: the heir grabs the queen's thigh asking to lie with her"),
    "c00126": (N, None, ["sexual", "dup"], "Hanshu 44: same story"),
    "c00127": (N, None, ["bosom", "dream-content"], "Hanshu 84 commentary: dream of the moon entering the bosom (omen)"),
    "c00147": (N, None, [], "Zhanguo ce 3 (Su Qin): stabs his own thigh to stay awake"),
    "c00149": (N, None, ["bosom", "dream-content"], "Soushen ji 10: Lady Wu dreams the moon entered her bosom"),
    "c00150": (N, None, ["bosom", "dream-content", "dup"], "Soushen ji 10: same"),
    "c00151": (N, None, ["bosom", "dream-content", "dup"], "Soushen ji 10: same"),
    "c00152": (N, None, [], "Soushen ji 16: gold pillow kept in his bosom"),
    "c00157": (N, None, [], "TPGJ 75: takes a gourd from his bosom"),
    "c00158": (N, None, [], "TPGJ 85: takes tiles from his bosom"),
    "c00159": (N, None, [], "TPGJ 88: dreams a tiger bites his arm"),
    "c00160": (N, None, [], "TPGJ 112: 劉肱 a personal name"),
    "c00161": (N, None, ["bosom", "dream-content"], "TPGJ 137: Dong Zhongshu dreamed a dragon entered his bosom"),
    "c00164": (N, None, [], "TPGJ 162: dream, banner pierces thigh"),
    "c00165": (N, None, [], "TPGJ 202: 錦半臂 a garment"),
    "c00169": (N, None, [], "TPGJ 278: dream of a 半臂 garment"),
    "c00170": (N, None, ["dup"], "TPGJ 278: same"),
    "c00171": (N, None, ["dup"], "TPGJ 278: same"),
    "c00172": (N, None, ["dup"], "TPGJ 278: same"),
    "c00173": (N, None, ["dup"], "TPGJ 278: same (股肱 'limbs')"),
    "c00176": (N, None, [], "TPGJ 300: marks on his arm after waking"),
    "c00180": (N, None, [], "TPGJ 340: tiger eyes tied to arms; household asleep"),
    "c00181": (N, None, [], "TPGJ 351: 股慄 'thighs trembling' after a dream"),
    "c00187": (N, None, [], "Wenxuan 25: 股肱守 'trusted governor'; 高臥"),
    "c00188": (N, None, [], "Wenxuan 30: 撫枕懷百慮 'strokes the pillow, full of cares'"),
    "c00192": (N, None, [], "QTS 233 title: 伏枕書懷 'writing my feelings, bedridden'"),
    "c00194": (N, None, [], "QTS 261: 攘臂 'bares his arm' on waking"),
    "c00209": (N, None, [], "QTS 681: 折臂翁 'old man with broken arm'; dream"),
    "c00212": (N, None, ["death"], "QTS 708: corpses still hold bows on their arms"),
    "c00213": (N, None, [], "QTS 727: 蔣肱 a name"),
    "c00214": (N, None, ["dup"], "QTS 727: same name"),
    "c00215": (N, None, [], "QTS 793: 病枕欹 / 懷君 'think of you'"),
    "c00218": (N, None, [], "QTS 897: sandalwood marks on the arm after a love tryst"),
    # ---- Finnic ----
    "c00240": (N, None, ["polvi=lifetime"], "Kalevala 7: puhki polveni 'all my life' (polvi 'generation'); uin 'I swam'"),
    "c00305": (N, None, ["polvi=lifetime", "dup"], "Kalevala 1835: same formula"),
    "c00276": (N, None, ["kneeling"], "Kalevala 41: boys on their knees on the ground listening; all the listeners fall asleep (separate)"),
    "c00317": (N, None, [], "Kalevala 1835: beard down to the knees; maata 'earth'"),
    "c00256": (N, None, ["helma"], "Kalevala 20: the maiden asleep, honey-grass in her skirt-lap (helmassansa): not a support"),
    "c00257": (N, None, ["syli"], "Kalevala 22: mother dead with a sheaf in her arms (kupo sylihin)"),
    "c00261": (N, None, [], "Kalevala 30: syli = fathom of spear-shaft"),
    "c00268": (N, None, ["syli", "dup"], "Kalevala 36: same formula as c00257"),
    "c00320": (N, None, ["helma"], "Kalevala 1835: shirt-hems sweep the sand; maata 'ground'"),
    "c00321": (N, None, ["syli"], "Kalevala 1835: maidens left unembraced, embraced ones un-lain-with (sylityt makoamatta): sexual, no support"),
    "c00322": (N, None, ["syli", "dup"], "same lines"),
    "c00354": (N, None, [], "Kalevala 1835: sylen = fathom; kuolemahan"),
    "c00362": (N, None, [], "Kanteletar table of contents"),
    "c00366": (C, None, ["syli", "sleep"], "Kanteletar I.1 (Kreivin sylissä istunut): the girl sat in the count's lap/arms (kreivinsä sylissä) and then slept beside him (nukkui kreivin vierehen); syli, not polvi"),
    "c00368": (N, None, ["povi"], "Kanteletar: povi 'breast' burning with grief; sleep elsewhere"),
    "c00379": (N, None, ["syli", "dup"], "Kanteletar: = Kalevala 22 formula"),
    "c00389": (N, None, ["povi"], "Kanteletar: love-charm, breast on fire, no sleep at night"),
    "c00395": (C, None, ["syli", "death-as-sleep"], "Kanteletar (Tuuti lasta tuonelahan): lull the child into the boards' embrace (lautojen sylihin), to sleep under the turf (alla nurmen nukkumahan): death as sleep in the coffin's syli"),
    "c00404": (N, None, ["syli"], "Kanteletar: syntynyt sylin pitävi 'the born are held in arms'"),
    "c00406": (N, None, ["helma"], "Kanteletar: Katri's skirt jingles; the village cannot sleep"),
    "c00407": (N, None, ["helma", "dup"], "same lines"),
    # ---- Arabic (OpenITI, research only) ----
    "c00421": (N, None, [], "fa-khadhalahu 'deserted him' (not fakhidh)"),
    "c00422": (N, None, [], "fakhidh = leaning on the thigh when spearing"),
    "c00423": (N, None, [], "fakhidh = clan subdivision"),
    "c00424": (N, None, ["chest", "object"], "al-Jahiz: a book always on his chest when he lay down"),
    "c00425": (N, None, [], "animal teats; hilma 'nipple'"),
    "c00426": (N, None, [], "poetry: sadr 'breast' + hilm 'forbearance'"),
    "c00427": (C, None, ["thigh", "sleep"], "Bukhari, Tayammum: the Prophet asleep with his head on ʿAʾisha's thigh (واضع رأسه على فخذي قد نام)"),
    "c00434": (C, None, ["thigh", "sleep", "dup"], "Bukhari: same hadith, another chapter"),
    "c00435": (C, None, ["thigh", "sleep", "dup"], "Bukhari: same hadith: فنام ... على فخذي"),
    "c00440": (C, None, ["thigh", "sleep", "dup"], "Bukhari: same hadith, another chapter"),
    "c00441": (C, None, ["lap", "sleep"], "Bukhari: the Prophet laid his head in ʿAʾisha's lap asleep (ثنى رأسه في حجري راقدا)"),
    "c00430": (C, None, ["lap", "chest", "death"], "Bukhari, Wasaya: ʿAʾisha: I had him propped on my chest, or she said my lap (صدري أو قالت حجري), he slumped in my lap and I did not notice he had died"),
    "c00431": (C, None, ["lap", "death", "dup"], "same hadith as c00430"),
    "c00439": (C, None, ["chest", "death", "dup"], "Bukhari, Maghazi: same death report (مسندته إلى صدري ... فمات)"),
    "c00438": (C, None, ["thigh", "death"], "Bukhari, Maghazi: at his death 'his head on ʿAʾisha's thigh' (ورأسه على فخذ عائشة)"),
    "c00428": (N, None, ["kneeling"], "Bukhari: he set down his knee so Safiyya could step on it to mount"),
    "c00429": (N, None, [], "rakibtu 'I rode'"),
    "c00442": (N, None, ["dup"], "rakibtu 'I rode' (same hadith)"),
    "c00432": (N, None, [], "rakibat 'she rode', then fell and died"),
    "c00437": (N, None, ["wound"], "ʿAmir's own sword hits his knee and he dies"),
    "c00443": (N, None, ["wound", "dup"], "same hadith"),
    "c00433": (N, None, [], "dream: the sword's blade (sadr) broke"),
    "c00436": (N, None, ["dup"], "same dream"),
    "c00444": (N, None, ["dup"], "same dream"),
    "c00445": (N, None, [], "ʿUyun: Sulayk asleep; a man crouches on his chest (attack)"),
    "c00446": (N, None, [], "ʿUyun: woman lying down wakes with a man on her chest (attack)"),
    "c00447": (N, None, [], "fa-khadhalahu 'deserted him'"),
    "c00448": (N, None, [], "ʿUyun: description of a woman: kneecaps (رضاف ركبتيها) when she lies on her back"),
    "c00449": (N, None, [], "fa-khudh 'so take'"),
    "c00450": (N, None, [], "fa-khudhīhā 'take it'"),
    "c00451": (N, None, ["dup"], "ʿIqd: the Sulayk story (attack on the chest)"),
    "c00452": (N, None, ["dup"], "fa-khudhīhā 'take it'"),
    "c00453": (N, None, ["dup"], "ʿIqd: same description as c00448"),
    "c00454": (N, None, [], "fa-khudh 'take'"),
    "c00455": (N, None, ["dup"], "fa-khadhalahu"),
    "c00456": (N, None, [], "sat on his chest, he died: attack"),
    "c00457": (N, None, ["dup"], "same"),
    "c00458": (N, None, [], "salamat sadrihi 'goodwill'; sleep returns"),
    "c00459": (N, None, ["lap"], "ʿIqd: al-Rashid was raised in her lap (rubbiya fi hijriha) = upbringing"),
    "c00460": (N, None, ["wound"], "spear touches the inside of my thigh"),
    "c00461": (N, None, [], "sadr = first hemistich of a verse"),
    "c00462": (N, None, [], "rakibat 'she rode'"),
    "c00463": (N, None, [], "rukkibat 'were set'"),
    "c00464": (N, None, [], "description of breasts"),
    "c00465": (N, None, [], "zoology: breasts on the chest; animals sleep with eyes open"),
    "c00466": (N, None, [], "rakibtanī 'you rode me' (donkey in a dream)"),
    "c00467": (N, None, [], "rakibtuhu 'I rode it'"),
}

NOISE_JA = "MYS ひさ = hisa 'long time' or ひざ = -zar- negative ending / -zama: not the knee word"
NOISE_GENJI = "Genji: ひさ/ひざ inside another word (匂ひさへ, 生ひざま, ひざまづき 'kneel'), or かひな = kahinashi 'in vain': not target"


def classify(r):
    c = r["cand"]
    if c in CLS:
        return CLS[c]
    if r["corpus"] == "japanese:Man'yoshu" and r["word"] in ("ひさ", "ひざ"):
        return (N, None, ["lexical-noise"], NOISE_JA)
    if r["corpus"] == "japanese:Genji monogatari" and r["word"] in ("ひさ", "ひざ", "かひな"):
        kneel = "ひざまづ" in r["context"]
        return (N, None, ["kneeling" if kneel else "lexical-noise"], NOISE_GENJI)
    if r["word"] in ("手枕", "たまくら", "tamakura"):
        return (C, None, ["arm-pillow", "lover"], "arm-pillow 手枕 tamakura, the standard lovers' sleep support in Old Japanese verse")
    if r["corpus"] == "japanese:Man'yoshu" and r["word"] == "かひな":
        return (N, None, [], "MYS 3.420: cords hung on the arms (ritual)")
    raise SystemExit(f"unclassified candidate {c} {r['corpus']} {r['locus']} {r['word']}")


def short(ctx, word, n):
    i = ctx.find(word)
    if i < 0:
        return ctx[: 2 * n]
    return ctx[max(0, i - n): i + len(word) + n]


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
    out = []
    for r in rows:
        if r["role"] == "knee-nosleep":
            continue
        cl, ex, tags, reason = classify(r)
        n = 12 if r["corpus"].startswith(("chinese", "japanese-kanbun", "mongol")) else 25
        if r["corpus"].startswith("finnic"):
            n = 60
        if r["corpus"].startswith("arabic"):
            n = 45
        row = OrderedDict(
            id=f"testA-east-{r['cand']}", corpus=r["corpus"], locus=r["locus"], date=r["date"],
            role=r["role"], words={"support": r["word"], "sleep_death_pillow": r["co"]},
            context=short(r["context"], r["word"], n), classification=cl, reason=reason, tags=tags,
            src=r["src"])
        if cl == P:
            row["explicit"] = bool(ex)
        if "licence" in r:
            row["licence"] = r["licence"]
        out.append(row)
    with open(sys.argv[2], "w", encoding="utf-8") as o:
        for row in out:
            o.write(json.dumps(row, ensure_ascii=False) + "\n")
    from collections import Counter
    cnt = Counter((row["corpus"].split(":")[0], row["classification"], row.get("explicit")) for row in out
                  if "dup" not in row["tags"])
    for k, v in sorted(cnt.items(), key=str):
        print(k, v)
    unused = set(CLS) - {r["cand"] for r in rows}
    if unused:
        raise SystemExit(f"stale ids in CLS: {sorted(unused)}")


if __name__ == "__main__":
    main()
