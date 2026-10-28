# Test A (typological control): East Asia, Finnic and Arabic half

Run 2026-10-28 under `docs/research/knee-sleep-preregistration.md`, whose target relation and decision rule are applied
unchanged. The Near East half (Hebrew, Akkadian, Sumerian, Egyptian) is in `testA-neareast.md`.
Hit rows: `data/research/knee-sleep/testA-east.jsonl` (288 rows, one per candidate window read). Scripts:
`scripts/knee_sleep_testA_east_fetch.py`, `..._search.py` (writes candidate windows), and `..._build.py`, which holds the hand
classification of every candidate and refuses to run if any candidate is unclassified. All of them run with `python3 -I`.

## Result in one paragraph

**Japanese and Chinese both have explicit positives, so the pre-registered rule is met by these two traditions:**
"Explicit positives in ≥ 2 unrelated non-IE traditions → the scene is typologically ordinary". Japanese has three
independent explicit scenes. Two are royal naps on a queen's knee that turn into an assassination scene: Suinin (Kojiki
712; Nihon shoki 720, with a dream) and Ankō (Nihon shoki 720, killed in his sleep). The third is in Genji (c. 1008):
young Murasaki falls asleep leaning on Genji's knee. Chinese has one: Li Mi sleeps on Emperor Suzong's knee (Taiping
guangji 38, from the Tang *Yehou waizhuan*, 9th c.). Finnic, Arabic and the Mongolian Secret History (Chinese summary
version) have **0** positives, with recall shown. Arabic prefers the thigh (*fakhidh*) and lap (*ḥijr*) for the same
scene; Finnish uses *syli*.
Two caveats go with the result, and neither changes the rule. (1) Japanese and Chinese are unrelated languages, but the
Japanese chronicles are written in literary Chinese, and the phrase 枕X膝 "pillow on X's knee" is Chinese idiom from the
Hanshu on. The native Japanese evidence is the phonographic Man'yōshū 14.3457 (*piza maku*, implicit) and the vernacular
Genji, so the Japanese case does not rest on the kanbun phrase alone. (2) The Chinese explicit positive is late (Tang,
compiled 978). Earlier Chinese knee-pillow scenes are lying awake or dying, not sleeping.

## Corpora obtained

| Tradition | Corpus (edition) | Size | Source, licence |
|---|---|---|---|
| Old Japanese, kanbun | Kojiki (3 juan + preface), Nihon shoki (30 juan) | 299k chars | zh.wikisource; PD text, site CC BY-SA 4.0 |
| Old Japanese, verse | Man'yōshū, all 20 books (原文 + 訓読 + 仮名 fields) | 4,516 poems | ja.wikisource; PD text, site CC BY-SA |
| Old Japanese, verse | ONCOJ (lemmatized, parsed: MYS, Kojiki/NS songs, Bussokuseki, Fudoki etc.) | ~100k words | github.com/ONCOJ/data, CC BY 4.0 |
| Heian | Genji monogatari, 54 chapters (Shibuya Eiichi ed.) | 946k chars | ja.wikisource, `{{CC-BY-SA-3.0}}` |
| Heian | Ise monogatari (Gunsho ruijū text, rendered page) | 24k chars | ja.wikisource; PD |
| Classical Chinese | Kanripo: Shijing, Zuozhuan, Shiji, Hanshu, Hou Hanshu, Sanguozhi, Jinshu (**juan 1–33 only**: the repo holds no more), Guoyu, Zhanguo ce, Hanfeizi, Zhuangzi, Liezi, Chuci, Wenxuan, Shishuo xinyu, Shanhaijing, Shiyi ji, Soushen ji, Soushen houji, Taiping guangji, Bowu zhi, Youyang zazu, Quan Tangshi (23 texts, chosen before reading) | 42 MB | github.com/kanripo, "Licensed as CC BY SA 4.0" |
| Mongolian | Yuanchao mishi 元朝秘史, Ming Chinese summary translation (總譯), 15 juan | 59k chars | zh.wikisource, CC BY-SA 4.0 |
| Finnic | Kalevala 1849, Kalevala 1835 (2 vols), Kanteletar 1840 | 229k words | Project Gutenberg #7000, #48380, #48381, #7078; public domain |
| Arabic | OpenITI: Ṣaḥīḥ al-Bukhārī; Ibn ʿAbd Rabbih *al-ʿIqd al-farīd*; Ibn Qutayba *ʿUyūn al-akhbār* and *al-Shiʿr wa-l-shuʿarāʾ*; al-Jāḥiẓ *al-Bayān* and *al-Ḥayawān*; *al-Mufaḍḍaliyyāt* | 2.24M words | OpenITI GitHub, **CC BY-NC-SA 4.0: research only** |

**Not obtained or not done:**
- *Kitāb al-Aghānī*: not found under its author folder in the OpenITI `0375AH` repo listing.
- Mutanabbī's *Dīwān*: the raw file returned 404.
- The Mongolian original: only the Chinese summary translation is on wikisource, and the interlinear version was not
  available. A translation's knee or lap counts only when the source word is identified, so any hit there could not
  have counted anyway.
- Old Turkic: not attempted.
- Other Heian texts (Makura no sōshi, Konjaku): not searched.

## Search terms (fixed in the search script)

- **Chinese script** (Kojiki, Nihon shoki, Kanripo, Secret History): knee 膝 and its variants **䣛** and 厀. A hit is a
  candidate when, within ±15 characters, it has a sleep or dream word (寢寝眠寐臥卧睡夢夣寤) or a death word (死卒薨崩殂),
  or 枕 within ±4. Contrasts: 股 (thigh), 肱/臂 (arm), and 懷 only as 懷中/在懷/入懷/抱懷 (bosom), each with a sleep word
  within ±6 or governed by 枕.
- **Japanese kana texts** (MYS 訓読/仮名, Genji, Ise): 膝, ひざ, ひさ+particle. Sleep words: 寝, 寐, 眠, 夢, 臥, ね-forms,
  まどろ, うたたね, 大殿籠, ふし, 枕, within ±40 characters. Contrasts: 手枕/たまくら, 懐, 腕/かひな.
- **ONCOJ**: lemma L051796 *piza* "knee" (every token read). Contrast: *ta makura* "arm-pillow".
- **Finnish**: `pol[vw][ieae]-` (covers the old *w* spelling), with a sleep or death word within ±3 lines (*uni*, *uin-*,
  *nukku-*, *maka-/maata/makoa*, *lepä-*, *kuol-*). Knee lines without such a word were also checked at ±8 lines.
  Contrasts: *syli*, *helma*, *povi*.
- **Arabic** (diacritics stripped): knee ركبة/ركبت-. Contrasts: حجر+suffix (lap), فخذ (thigh), صدر+suffix (chest).
  Each needs within ±12 tokens a word from نام/نوم/نائم, رقد/راقد, نعس, هجع, وسن, الكرى, حلم/رؤيا/منام, وسد/توسد, اضطجع,
  or مات/توفي/قبض.

## Recall checks (run before reading)

| Corpus | Known knee passage | Found? |
|---|---|---|
| Kojiki / Nihon shoki | Suinin: the emperor sleeps on Saho-hime's knee (枕其后之御膝 / 枕皇后膝而晝寢) | yes (Kojiki 中卷 §垂仁天皇; NS 卷6 ¶10) |
| Man'yōshū (wikisource) and ONCOJ | MYS 5.810, Tabito's zither "on the knee of one who knows my voice" (比等能比射乃倍) | yes, in both. Both editions return the same 4 *piza* poems (3.379, 5.810, 7.1328, 14.3457) |
| Chinese (Kanripo) | Shiji 7, at the Xiang Yu camp gate: 無不膝行而前 | yes. Shishuo xinyu, Wang Dao pillows on Zhou Yi's knee: **missed by 膝 alone**, because Kanripo spells it 䣛 (U+48DB). After 䣛 and 厀 were added, found (c00148). Without the variant, 28 knee tokens would have been lost |
| Secret History (Chinese) | §244 Hö'elün lays her breasts on her knees (出兩乳置膝上) | yes (2 knee tokens in the whole text, neither with sleep) |
| Kalevala 1849 / 1835 | Runo 1: the bird nests on Ilmatar's (1835: Väinämöinen's) knee (*polvea*, *polwelle*) | yes, both spellings |
| Kanteletar | no independently known knee passage | not shown. The regex returns 50 knee lines; *syli* recall is shown (I.1 "Kreivin sylissä istunut") |
| Bukhārī | ʿUmar kneels: فبرك عمر على ركبتيه | yes (3 places). Contrast recall: ʿĀʾisha's necklace hadith, head on her thigh (فخذي … قد نام), also found |
| Genji / Ise | no independently known knee passage | Genji not shown in advance (it has 4 膝 and 4 ひざ in all). Ise has no knee word at all |

## Positives

**Explicit** (the knee supports someone narrated as asleep, dreaming, or dying in sleep):

| Tradition | Locus | Date | Words | Scene |
|---|---|---|---|---|
| Japanese | Kojiki 中卷, Suinin | 712 | 枕其后之御膝。爲御寢坐 | the emperor sleeps on the empress's knee. Her dagger is raised; her tears fall on his face and wake him |
| Japanese | Nihon shoki 6, Suinin 5 | 720 | 天皇枕皇后膝而晝寢 … 朕今日夢矣 | the same story, with his dream of a snake and rain (one scene, two texts) |
| Japanese | Nihon shoki 14, Yūryaku前紀 (Ankō 3) | 720 | 枕皇后膝。晝醉眠臥 … 伺其熟睡而刺殺之 | Ankō sleeps drunk by day on the empress's knee and is stabbed in his sleep. The Kojiki parallel puts him on a "god-bed" (坐神牀而晝寢) with no knee |
| Japanese | Genji, Momiji no ga | c. 1008 | 御膝に寄りかかりて、寝入りたまひぬれば | young Murasaki falls asleep leaning on Genji's knee |
| Chinese | Taiping guangji 38, Li Mi (from 鄴侯外傳) | Tang tale, 9th c.; compiled 978 | 但枕天子膝睡一覺 … 捧泌首置於膝，良久方覺 | Li Mi asks, as his only reward, to sleep once on the Son of Heaven's knee. Later he dozes, and Suzong lifts his head onto his knee until he wakes |

**Implicit** (knee-pillow with no sleep word, or sleep only proposed; not counted for the rule):
- MYS 14.3457 (Azuma-uta, before 759): 比射麻久 *piza maku* "pillow on (a Yamato woman's) knee". Phonographic, so native
  Old Japanese.
- Genji, Wakamurasaki: この膝の上に大殿籠もれよ "sleep on my knee". An invitation; the sleep is not narrated.
- Sanguozhi 16, Su Ze (3rd c.): 枕則膝臥 "lay pillowed on Su Ze's knee", then pushed off.

**Not counted but worth weighing** (knee-pillow or death on the knee without sleep). These are recorded as not-target
under the rule:
- Death on the knee, the 2 Kgs 4:20 type: Hanshu 88 (Tian Sheng 且死時枕喜膝, 1st c. CE); Jinshu 31 (Empress Yang
  臨終枕帝膝 … 絶于帝膝, 648); Quan Tangshi 801 note (以首枕其膝而逝).
- Knee-pillow inside a dream's content: Jinshu 1 (Sima Yi dreams the emperor 枕其膝); Jinshu 32 (dragons 枕膝); MYS 5.810
  (a dream-zither wishes to lie on a knee).
- Awake knee-pillow: Nihon shoki 11 (Hayabusawake 枕皇女之膝以臥, talking); Shishuo xinyu (Wang Dao, joking).

**The term *hizamakura* 膝枕:** it occurs in none of the searched texts (Kojiki, Nihon shoki, Man'yōshū, Genji, Ise).
The scene is attested from 712 as a verb phrase (枕…膝, *piza maku*), not as the compound.

## Near-contrasts (another body part supports the sleeper or the dying)

- **Japanese:** the arm-pillow 手枕 *tamakura* is the standard lovers' sleep support. It appears in 19 Man'yōshū poems
  (wikisource and ONCOJ agree on the same 19), against 1 knee-pillow poem (14.3457). Genji has 腕/かひなを枕にて three
  times, plus 新手枕 once. So Japanese uses the arm for lovers and the knee for a sovereign's (or a child's) nap.
- **Chinese:** the thigh 股.
  - For the dead, in a mourning rite: Zuozhuan ×4 (枕之股而哭), Sanguozhi 4, Taiping guangji 274 (= Quan Tangshi 368).
  - For a sleeper: King Ling of Chu sleeps on his attendant's thigh (Shiji; Guoyu, Wu yu: 王枕其股以寢於地。王寐);
    Li Bai (Quan Tangshi 172): 醉横眠枕其股.
  - The arm, 枕臂眠 / 寢臂 / 曲肱, 8 times in Tang verse; Soushen ji 19 枕臂而臥.
- **Arabic:** all in Bukhārī.
  - The Prophet asleep with his head on ʿĀʾisha's **thigh** (فخذي … قد نام; 4 chapters, one hadith).
  - His head in her **lap**, asleep (ثنى رأسه في حجري راقدا).
  - He died propped on her chest or lap (صدري أو قالت حجري … انخنث في حجري); or with his head on her thigh (ورأسه على
    فخذ عائشة).
  - No knee scene. In the adab texts, knee words occur only for kneeling, wounds and body descriptions.
- **Finnic:**
  - Kanteletar I.1: the girl sits in the count's *syli*, then sleeps beside him.
  - Kanteletar "Tuuti lasta tuonelahan": death as sleep in the *syli* of coffin boards (*lautojen sylihin … alla nurmen
    nukkumahan*).
  - No knee scene. *Polvi* hits are mostly "generation/lifetime" (*puhki polveni*), kneeling, or Ilmatar's knee in the
    sea.

## Counts (distinct passages; duplicate rows for the same passage are excluded)

| Tradition | Knee tokens in corpus | Candidate windows read | Explicit + | Implicit + | Death on knee | Clear contrasts |
|---|---|---|---|---|---|---|
| Japanese, kanbun (Kojiki, NS) | 14 | 7 | 3 passages (2 scenes) | 0 | 0 | 0 |
| Japanese, Man'yōshū / ONCOJ | 4 poems | 86 (incl. noise ひさ "long time") | 0 | 1 | 0 | 19 tamakura poems |
| Japanese, Genji / Ise | 8 / 0 | 25 / 0 | 1 | 1 | 0 | 4 (arm) |
| Chinese, Kanripo (23 texts) | 419 (膝 389, 䣛 28, 厀 2) | 102 | 1 scene (2 rows) | 1 | 3 | 9 thigh, 9 arm |
| Mongolian (Chinese 總譯) | 2 | 0 | 0 | 0 | 0 | 0 |
| Finnic | 184 knee lines | 21 | 0 | 0 | 0 | 2 (*syli*) |
| Arabic (OpenITI, NC) | 183 ركب[ةت] tokens (includes "rode") | 47 | 0 | 0 | 0 | 4 passages (thigh ×2, lap, chest/lap) |

## What the pre-registered rule implies

- **Japanese: positive.** There are explicit positives (712, 720, c. 1008). The phrase is native as well as Sinitic:
  the phonographic *piza maku* and the vernacular Genji both have it.
- **Chinese: positive.** One explicit positive (Tang, 9th c.), plus a long run of knee-pillow scenes from the Hanshu on:
  awake, lying, dying, or dreamed.
- **Finnic: 0, with recall shown** (Kalevala). The knee is not a sleep support here; *syli* is.
- **Arabic: 0, with recall shown** (Bukhārī). The same scene goes to the thigh or lap.
- **Mongolian: 0** in a small text, and the text is a translation.
- **Overall:** two unrelated non-IE traditions (Japanese, Chinese) give explicit positives, so by the rule as written
  **knee-supported sleep is typologically ordinary.** The inheritance proposal then has to rest on marked lexical choice
  (Tests B and C), not on the scene. This half alone meets the threshold; whatever Hebrew adds (Judges 16:19 was known
  before registration) only adds a third tradition.

The rule's word "unrelated" is ambiguous here: Japanese and Chinese are unrelated languages, but the Japanese
chronicles take part of their phrasing from Chinese literature. That is recorded, not redesigned. The Japanese scene
also shows a pattern the Chinese one lacks: a sovereign asleep on a queen's knee at the moment of a planned killing,
twice, which is close in shape to the Hittite and Greek knee-sleep-death scenes.

## Procedure notes

- Each row's `context` is a short window of the original text only. No translations were quoted.
- OpenITI rows carry `licence: research only`.
- The Jinshu repo files for juan 31 and 33 repeat the same text. The duplicates are tagged `dup` and counted once.
- The rule's "explicit" was read as "a sleep, dream or death-in-sleep word applies to the person on the knee". Rows
  that are knee-pillow only carry `explicit: false`.
