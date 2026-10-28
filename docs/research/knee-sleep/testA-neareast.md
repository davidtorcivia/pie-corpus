# Test A, Near East half: knee-supported sleep in non-IE traditions (2026-10-28)

This runs the typological control registered in `docs/research/knee-sleep-preregistration.md`. Its target
relation, corpora and decision rule were followed as written. The East Asian, Finnic and Arabic half is
reported separately (`testA-east*`). Every hit is in `data/research/knee-sleep/testA-neareast.jsonl`:
65 rows, one per read hit (overlapping windows of the same passage merged), with words, classification and reason.
Candidate extraction: `python3 -I scripts/knee_sleep_testA_neareast.py {hebrew|oracc|etcsl|tla} raw/daughters OUT`.

## Corpora obtained

| Tradition | Corpus | Size searched | Licence |
|---|---|---|---|
| Hebrew (Semitic) | OSHB morphhb, WLC + Strong's lemmas (commit 3d15126) | 23,213 verses, whole Hebrew Bible | CC BY 4.0 / PD |
| Akkadian (Semitic) + Sumerian | ORACC JSON: epsd2 literary/earlylit/praxis, etcsri, ckst, blms, cams/gkab, cmawro (+Maqlû), asbp, saao (SAA 1-21) | 9,152 readable texts | CC BY-SA per project pages (files say CC0); epsd2/literary NC |
| Sumerian | ETCSL revised ed. (Oxford LLDS 2518), transliterations + translations | 394 compositions | CC BY-NC-SA 3.0 |
| Egyptian | TLA Earlier Egyptian v18 "premium" (HF), Late Egyptian v19 "premium" as a supplement | 12,773 + 3,606 sentences | CC BY-SA 4.0 |

Provenance and hashes are in `raw/MANIFEST.md` under "Knee-sleep Test A, Near East half".

## Search terms (each corpus's own lemmas)

- **Hebrew** (Strong's, checked against verses that contain them). Knee: בֶּרֶךְ 1290, Aram. 1291, אַרְכֻבָּה 755.
  Contrast supports: חֵיק 2436 "bosom", חֹצֶן 2684, זְרוֹעַ 2220 "arm", חָבַק 2263 "embrace". Sleep/death:
  יָשֵׁן 3462/3463, שֵׁנָה 8142/8139/8153, נוּם 5123, תְּנוּמָה 8572, תַּרְדֵּמָה 8639, רָדַם 7290, שָׁכַב 7901, חֲלוֹם/חָלַם 2472/2492/2493,
  מוּת 4191, מָוֶת 4194/4193, גָּוַע 1478.
- **Akkadian** (ORACC cf[gw]). Knee: birku, burku [knee]; kimṣu/kinṣu [shin]. Contrast: utlu [lap], sūnu [loin = lap],
  kirimmu [(crook of) arm], edēru [embrace], ḫaṣānu [hug]. Sleep/death: ṣalālu [lie (down)], ṣallu [sleeping], šittu
  [sleep], ṣallūtu, šuttu [dream], nâlu, nīlu, nēlu, utūlu, itūlu [lie down], diglu [vision], mâtu/muātu [die],
  mūtu, mītu, mētu, mītūtu, naparqudu, rabāṣu [lie down]. Matching is on (cf, gw), because one cf covers homonyms.
- **Sumerian** (ORACC cf[gw]; ETCSL lemma). Knee: du₁₀ (dub[knee], ETCSL dub3), zeb[knee]. Contrast: ur₂ "lap" (ePSD2
  files it under ur[root], so every ur hit was read), gu₂ la₂ "embrace". Sleep/death: u₃ [sleep], u₃ ku₄, u₃-sa₂,
  usag, mamud [dream], mašŋik [vision], nu₂ [lie], šed₇/ce21 [lie], uš₂/ug₇ [die], nam-uš₂ [death], an.eše e.
- **Egyptian** (TLA lemma forms + German translation as a second net). Knee: mꜣs.t, pd/pꜣḏ (TLA files the knee
  word, written *pd*, under lemma 59460 *pꜣḏ*; the first run missed that form, and it was added and rerun with no new
  candidate); German Knie, Schoß. Contrast:
  qni̯/qnꞽ "embrace, bosom", ḥpt, rmn "arm", mnꜥ.t "nurse"; German umarm-, Arme. Sleep/death: sḏr, qdd, nmꜥ, mwt, mt;
  German schlaf-, Traum, sterb-, tot/Tod, liegt, ruht.

**Windows**, fixed before the run: Hebrew same verse (primary) or adjacent verse; cuneiform same line ±2 lines;
Egyptian same sentence only, because the TLA rows are shuffled single sentences with no context. Knee lines
outside a window were also read when they fell in a sleep context (the Šulgi N lullaby) or were among the few
Egyptian knee hits.

## Recall check

Both registered Hebrew items were found by the script in the same verse, before any reading:

- **Judg 16:19**: וַתְּיַשְּׁנֵהוּ עַל־בִּרְכֶּיהָ (1290 + 3462), with שְׁנָתוֹ in 16:20.
- **2 Kgs 4:20**: וַיֵּשֶׁב עַל־בִּרְכֶּיהָ ... וַיָּמֹת (1290 + 4191); 4:31 then speaks of the death as לֹא הֵקִיץ "has not woken".

Both are positives under the target relation. As registered, they are **not counted as new finds**. There is no
known item with which to test recall in Akkadian, Sumerian or Egyptian. The Akkadian "birku = knee, lap" entry is lexical,
not a passage.

## Positives

| Tradition | Locus | Words | Status |
|---|---|---|---|
| Hebrew | Judg 16:19 | *wattəyaššənēhû ʿal-birkeyhā* | known (recall), not counted |
| Hebrew | 2 Kgs 4:20 | *wayyēšeb ʿal-birkeyhā ... wayyāmōt* | known (recall), not counted |
| **Sumerian** | **Gilgameš and Ḫuwawa A, ETCSL 1.8.1.5 l. 91** (= ePSD2 Q000365 l. 91) | *du₁₀-ub ama ugu-ŋu₁₀ {d}nin-sumun₂-ka u₃-sa₂ dug₄-ga-gin₇* | **new find** |

The Sumerian passage: Gilgameš has been asleep on the mountain ("how long will you sleep?", ll. 70-81) and, on
waking, swears: am I to be again "as if sleeping on the knee of my own mother Ninsumun"? ETCSL's translation
says "lap", but the source word is du₁₀ "knee" (ETCSL lemma dub3 "knee"), so it meets the rule that a
translated "lap" counts only when the source word is identified. The scene is a simile, but it is explicit: a sleeper (a
child) supported by the mother's knee. Nothing in the target relation excludes similes; this is noted in case
the owner wants to weigh it lower.

No Akkadian positive and no Egyptian positive were found.

**Borderline, not counted:** Gudea Cylinders (ETCSL 2.1.7 l. 906) *u₃ dub₃ ŋar-ra*: lions and dragons
"lying asleep, knees bent". It is a sleeper on its own knees, but in the crouch/kneel idiom (dub₃ ŋar) and of animals.
The rule excludes kneeling, so it is not-target.

## Near-contrasts (sleep, lying or death on a support that is not the knee)

| Tradition | Locus | Support | What |
|---|---|---|---|
| Hebrew | 1 Kgs 3:20 | חֵיק bosom | dead child laid in a bosom while the mother is asleep |
| Hebrew | 1 Kgs 17:19 | חֵיק bosom | dead son taken from the widow's bosom (the Elijah twin of 2 Kgs 4:20, which uses knees) |
| Hebrew | 1 Kgs 1:2 | חֵיק bosom | Abishag to lie in the old king's bosom |
| Hebrew | 2 Sam 12:3 | חֵיק bosom | the pet lamb lies in his bosom |
| Hebrew | Mic 7:5 | חֵיק bosom | "she who lies in your bosom" |
| Hebrew | Lam 2:12 | חֵיק bosom | children faint "like the slain" and pour out their soul into their mothers' bosom (found by reading every ḥêq verse; the window missed it) |
| Sumerian | Šulgi N (lullaby) 2.4.2.14 ll. 33-34 | ur₂ lap; a₂ arms | wife to lie in his warm lap, son in his outstretched arms |
| Sumerian | Lament for Urim 2.2.2 l. 228 | ur₂ lap | little ones lying in their mothers' laps carried off by water |
| Sumerian | Inana's Descent 1.4.1 ll. 390-391 | ur₂ lap | wives/children who lie in men's laps |
| Sumerian | Old man and young girl, Q002335 l. 40 | ur₂ lap | "like a little child may he lie in your lap" |
| Sumerian | BT 7 + N 3323 + N 3326 (P278368) r iv' 3'-6' | ur₂ lap | "in the holy lap of Enlil ... may sweet sleep enter" (fragmentary) |
| Sumerian | Enki and Ninḫursaĝa 1.1.1 ll. 126N, 180, 182; proverb P414096 o 6 | ur₂ lap | sexual lying in the lap |
| Akkadian | SAA 2, 6 ll. 428-429 | sūnu (ÚR) lap | curse: wives made to lie in the enemy's lap |

Near-misses of form that are not-target: Maqlû IV 26-27 and CMAwR 7.2/8.3 (an *effigy* laid in a corpse's lap,
*ina sūn mīti*); the Udug-hul compendium STT 2, 173 (a figurine laid in the patient's lap at night); Udug-hul TIM 9, 62
(demons take the wife from the man's lap, ur₂, and the son from his knee, du₁₀); Šulgi N l. 38 (the son is to grow
up "on his good knee"); Westcar (Ruddedet sits with her head on her knees, mꜣs.t, in grief; no sleep); Job 3:12-13
(knees at birth, grave-sleep counterfactual); Dan 10:9-10 (deep sleep face down, then raised onto the knees).

**Which support do these traditions prefer?** In Hebrew, lying, sleeping or dying *in the bosom* (ḥêq: 6) outnumbers
the knee (2, both registered). The Hebrew knee is otherwise the place of birth, adoption and nursing: Gen 30:3,
48:12, 50:23 and Isa 66:12 (dandled on the knees). The bosom is where a nurse carries a child (Num 11:12, Ruth 4:16, Isa 40:11). The same scene, a mother's dead son, appears with knees in the Elisha story and with the bosom in the
Elijah story. In Sumerian the lap/arms (ur₂, a₂: 7 contrasts) is the normal place to lie; the knee (du₁₀) is where a
child is nursed and grows (Šulgi N l. 38, Udug-hul), and it carries sleep in exactly one passage, the
Gilgameš simile. Akkadian shows no knee-sleep, and only one lap-lying passage (sexual). Egyptian, in this small sample,
shows the knee/lap (mꜣs.t, qnꞽ) only for grief postures and a nursing child, never with sleep.

## Counts

| Corpus | Knee-word units | Candidate windows | Rows read | Positive (known / new) | Contrast | Not-target |
|---|---|---|---|---|---|---|
| OSHB Hebrew | 27 verses (+ every ḥêq/ḥōṣen verse read) | 30 | 23 | 2 / 0 | 6 | 15 |
| ORACC Akkadian (+bilingual) | 304 knee-lemma lines (Akk.+Sum.) | 47 (Akk.+Sum.) | 11 | 0 / 0 | 1 | 10 |
| Sumerian (ETCSL + ePSD2, deduplicated by composition) | 79 du₁₀ lines in ETCSL | 28 ETCSL + ORACC Sum. | 25 | 0 / 1 | 7 | 17 |
| TLA Egyptian (Earlier + Late supplement) | 21 sentences | 3 | 6 | 0 / 0 | 0 | 6 |

## What the pre-registered decision rule implies

The rule counts "explicit positives in ≥ 2 unrelated non-IE traditions (counting Hebrew and Akkadian as one
Semitic tradition)", and it says the registered items are "not counted as finds". The wording points to the strict
reading. Its third branch, "0 positives in the searched corpora, with recall shown on a known item", can only be
reached if the registered items are left out of the count: recall *requires* finding Judg 16:19, so under the inclusive
reading 0 would be impossible. Both readings are still given, because the inclusive one is the alternative the owner
may prefer, and the test is not redesigned:

- **Strict reading (registered items excluded):** new positives in the Near East half come from **one tradition, Sumerian**
  (Gilgameš and Ḫuwawa A 91). Semitic has 0 new and Egyptian has 0. For this half that is "exactly 1 → reported as is". The
  "0 positives" branch, which would strengthen the proposal, does not apply.
- **Inclusive reading (registered items count as positives for their tradition):** Semitic (Judg 16:19, 2 Kgs 4:20) +
  Sumerian = **2 unrelated non-IE traditions**. The rule's first branch then applies: the scene is typologically
  ordinary, and the inheritance proposal needs a marked lexical choice (Tests B, C), not the scene alone.

The final Test A verdict also depends on the East half. One new positive there, in any tradition, gives ≥ 2
under either reading. On the substance: the scene is attested outside Indo-European in two unrelated families
(Semitic and Sumerian), in both cases as a child or a man on a woman's knees. **For Semitic:** positive, but
only through the registered Hebrew items; nothing new in Hebrew; nothing in the open Akkadian corpora. **For Egyptian:** 0, from
a small corpus, so this is weak evidence of absence, not evidence of rarity.

## Gaps and problems (recorded, not fixed)

- **Akkadian narrative literature is largely missing.** The open ORACC projects are letters, treaties, rituals,
  scholarship and bilinguals. The Standard Babylonian Gilgameš, Atra-ḫasīs and Enūma eliš are not among them. eBL was
  checked briefly; no open bulk download was found, so it was dropped. Lead for the owner, not verified here and
  not counted: in SB Gilgameš tablet IV, standard translations have Gilgameš sit with his chin on his knees before
  sleep falls on him. If the Akkadian uses *birku*, it would be an Akkadian (self-supported) positive.
- **Egyptian coverage is thin.** The TLA HF sets are "premium" subsets (intact sentences only, about 16k), shuffled,
  with no text IDs, so there are no loci and no cross-sentence window. Loci given in the JSONL (Shipwrecked
  Sailor, Westcar) are the reader's identifications. The full TLA web corpus sits behind a bot-check page and was not used.
- **Licences conflict in ORACC:** the files say CC0, the project pages say CC BY-SA (and NC for ETCSL-derived
  epsd2/literary). The stricter reading is recorded in the manifest.
- 30 ORACC corpusjson files are empty (0 bytes) and were skipped.
- ETCSL and ePSD2/literary are the same compositions. Hits were merged by composition, so each passage is counted once.
- The rule's treatment of registered items in the ≥ 2 count is ambiguous (see above). It needs an owner decision, not a
  silent choice.
