# Knee-sleep Tests B and C: is the *swep- word the marked choice? (2026-10-28)

Runs Tests B and C of `docs/research/knee-sleep-preregistration.md` with its definitions and decision rules
unchanged. Where a rule did not fit the data, the problem is recorded below and a documented supplement
is reported next to the registered result, never in place of it. The preregistration names
`docs/research/knee-sleep-results.md` as the place for all three results; this file holds B and C only,
as asked, and the combined file is still to be written.

Scripts (`python -I`, read-only on `raw/` and the index):
- `scripts/research/knee_sleep/testB_hittite.py`: TLHdig parse, classification, tables, Fisher.
- `scripts/research/knee_sleep/testC_greek.py`: Greek index scan, base rates, knee windows, Fisher.
- `scripts/research/knee_sleep/fisher.py`: exact one-sided Fisher test (the env has no scipy; self-checked).

Data: `data/research/knee-sleep/testB-hittite.jsonl` (44 read paragraphs), `testC-greek.jsonl` (13 read knee
units), the hand verdicts `testB-vetting.jsonl`, `testB-paragraph-notes.jsonl`, `testC-vetting.jsonl`, and
the full count dumps `testB-summary.json`, `testC-summary.json`.

## Results by decision rule

| Test | Registered result | p (one-sided Fisher) | What the rule gives |
|---|---|---|---|
| B, knee | *šupp-* 1/13 paragraphs, *šeš-* 1/216 | 0.11 | Not significant. Counts tiny: **descriptive only.** |
| B, dream (*tešḫa-*, *zašḫai-*, MÁŠ.GI₆) | 4/13 vs 5/216 | 0.0007 | **Significant**, but every swep hit is *tešḫa-*, which also means "sleep" (see the caveat) |
| B, knee or dream (the rule as worded) | 4/13 vs 6/216 | 0.0011 | **Significant**, same caveat. Small counts (4 hits, 3 compositions): the result is reported, but it is close to the descriptive-only clause |
| C, unit as registered | 0 knee units with a sleep word in target relation | – (no positives) | **Not testable**: the recall check fails (Il. 22.500 and AP 7.170 are split across verse-line units) |
| C, ±2-line window (supplement) | 2 positives; *swep- 1 of 3 lexeme tokens vs base 53% | 0.90 (A), 0.80 (B) | No excess. 2 items: **descriptive only.** |

The preregistration gives no number for "tiny". Here a cell with fewer than about 5 hits in the smaller group is
treated as tiny: knee (1 vs 1) and Greek (2 positives) are descriptive only. The dream rows (4–5 hits among 13
*šupp-* paragraphs, from 3–4 compositions) are on that boundary; the p-values are reported, but they rest on
three or four texts.

My reading: Hittite does not make *šupp-* the marked verb in knee contexts. Knee hits are one per verb,
and only one of them (KUB 36.89) is in the target relation. *šupp-* does co-occur strongly with *tešḫa-*, but
that is a sleep verb taking a sleep/dream noun ("sleeps a sleep"), not a knee or dream scene, and *zašḫai-*
"dream" never occurs with either verb. In Greek, the two knee-supported sleep scenes use κοιμάω+ὕπνος
(AP 7.170) and ἰαύω (Hymn to Demeter). That is no more *swep- than ordinary Greek sleep vocabulary, which is
already about half ὕπνος.

## Test B: Hittite (TLHdig)

**Data.** 23,937 AOxml files; 153 are second copies of a docID (for example a copy under
`CTH 999_XML_TLH/TLH/`) and were skipped, which leaves 92,183 paragraphs. The unit is the paragraph, the stretch
of one tablet between `<parsep/>`/`<parsep_dbl/>`. TLHdig's `<clb>` clause marks appear in only a minority of
files, so clauses could not be used. Sleep paragraphs have a median of 20 words (max 351: KBo 4.2+ and KUB
14.10+ paragraphs run over a column).

**Classification.** Each `<w>` is classed from its candidate analyses and `mrp0sel`. A word counts if
(a) the selected analysis is in the class, (b) there is no selection and every candidate is in the class, or
(c) there are no analyses and the transliteration matches the spelling list. Words with a mix of candidates
and no selection ("amb") are read but not counted. Words tagged AKK/HURR/HAT/SUM/LUW are excluded from the
Hittite verb classes. Then every counted *šupp-* token and every knee/dream co-occurrence was read, and hand
verdicts override the automatic class (`testB-vetting.jsonl`).
- *šeš-*: lemmas šēš-/šaš-, šiš=k-, šiškeš=k-, šišk= (sleep gloss); spelling list for unanalysed forms.
- *šupp-* (*swep-): šupp=/šup=/šupp=a-/šupp=ar/šupp=iye/a-/šuppar=iye/a-/šuppar=iya-/šupparu=ant- with a sleep
  gloss. The annotator gives a "schlafen" candidate to most šuppa/šuppi/šuppaš forms, which are really *šuppi-*
  "pure" or *šuppa* "meat". 311 such words stayed "amb" and 250 had a non-sleep selection. All 19 automatically
  counted tokens were read; 3 were rejected and 16 kept: KUB 25.27 *šuppa* ŠE.NAGA "pure soap"; DBH 43_2.81 *šuppiyanzi*,
  purity context; KBo 36.53, an Akkadian omen.
- knee: gen=u-, gan=u-, kinu-, genušš=a/i- (gloss Knie). ginuw=a- "Knietuch" is kept apart (0 hits with sleep).
- dream: *tešḫa-* (tešḫ=a-, tiešḫ=a-, tešḫan=iye/a-, tešḫanišk=) and *zašḫai-*. "Broad" adds the logograms:
  Ù with a Hittite complement (Ù-an, Ù-aš, ...), Ù-TUM, Ù-TI, MA.MÚ.

**Counts (paragraphs; "both" = paragraphs with both verbs, kept out of the exclusive Fisher):**

| feature | *šupp-* with / without | *šeš-* with / without | both | p exclusive | p both-in-each |
|---|---|---|---|---|---|
| knee (*genu-*) | 1 / 12 | 1 / 215 | 0 / 2 | 0.11 | 0.12 |
| dream strict (*tešḫa-*, *zašḫai-*) | 4 / 9 | 5 / 211 | 0 / 2 | 0.0007 | 0.0012 |
| of which *tešḫa-* | 4 / 9 | 5 / 211 | 0 / 2 | 0.0007 | |
| of which *zašḫai-* | 0 / 13 | 0 / 216 | 0 / 2 | 1.0 | |
| dream broad (+ logograms) | 5 / 8 | 7 / 209 | 0 / 2 | 0.0002 | 0.0003 |
| **knee or dream strict (registered rule)** | 4 / 9 | 6 / 210 | 0 / 2 | **0.0011** | 0.0019 |
| knee or dream broad | 5 / 8 | 8 / 208 | 0 / 2 | 0.0003 | 0.0005 |

Sensitivities:
- Collapsing duplicate manuscripts to one per composition (Hedammu KBo 19.109a/19.111; Plague Prayer
  KBo 55.25+/KUB 14.10+/KUB 14.8; Laws KBo 25.85+/KBo 6.26/KUB 29.34+; Instructions KUB 13.4/KUB 26.31+):
  knee-or-dream strict 3/12 vs 4/208, p = 0.004; knee 1/12 vs 1/208, p = 0.11.
- Counting the 46 ambiguous *šeš-* tokens: knee-or-dream strict p = 0.0007.

**Caveat: the dream result is a *tešḫa-* collocation, not a dream scene.** TLHdig glosses *tešḫa-* as
"Schlaf". In 3 of the 4 strict *šupp-* hits, *tešḫa-* is the sleep the verb takes or is taken by:
- KBo 19.109a / 19.111 (one Hedammu text): *tešḫaš ēpta* "sleep seized him".
- KUB 4.47 Vs. 5: *tešḫan* UL *šuppariyazzi* "does not sleep a sleep".
- KUB 36.89: *tiešḫuš šuppariyanza* (CHD and the owner's packet read "dreams"; TLHdig "sleep").

KUB 4.47 Vs. 4 (*tešḫuš idalamuš uškezzi* "sees bad dreams") is the only clear swep–dream use. On the
*šeš-* side the dream sense dominates (Plague Prayer incubation *tešḫit* "in a dream", KBo 4.2+
*tešḫaniškewan*). If co-occurrence is restricted to *tešḫa-* in the dream sense, with KUB 36.89 counted as
"dreams":
- strict: *šupp-* 2/13 vs *šeš-* 4/216, p = 0.039 (dedup 0.015);
- with KUB 36.89 as "sleep": 1/13 vs 4/216, p = 0.26.

The registered rule gives p = 0.0011. That number measures mostly the figura-like pairing of *šuppariya-* with
*tešḫa-* (p = 0.0006 for *tešḫa-* in the sleep sense alone), not a marked choice of *šupp-* in dream contexts.

**Recall check: passed.** KUB 36.89 Rs. 56′–59′ is found, with all three features counted:
- knee: *ge-nu-wa-〈aš〉* (Rs. 57′), syllabic Hittite with the ending restored by the editor, not an
  Akkadogram. TLHdig selects gen=u- "Knie" D/L.PL over the ke=nu- "open" candidate. The owner's packet writes
  the form "GI-NU-WA". TLHdig has no logographic knee anywhere: 0 GENU, 0 GI-NU-, 0 BIRKU (the BI-IR-TI
  forms are *birtu* "fortress").
- dream: *ti-eš-ḫu-uš*.
- *šupp-*: *šu-up-pa-ri-ia-an-za*.

**Read knee co-occurrences (all):**
- KUB 36.89 Rs. 56′–59′ (*šupp-*): **positive**. The only target-relation item. Target-classified knee:
  *šupp-* 1/13 vs *šeš-* 0/216, p = 0.057, descriptive only.
- KUB 33.108 Vs. II (*šeš-*, Pišaiša myth): Ištar lies down to sleep (*šešuwanzi*), Pišaiša lies with her;
  later he falls at her knees (*genuwaš kattan* ... *ḫali-*) in supplication. Kneeling, a separate event:
  not target. This is also a **lemmatization miss**: *genuwaš* had no selection, so only reading counted it.

**The two "both" paragraphs** show how the verbs divide the meaning:
- KUB 20.86+ Rs. V 9′–10′: "either he sleeps (*šešzi*) with his wife or he sleeps (*šuppariyattari*)".
- KUB 52.91 (dream report): *katta šeššun* "I lay down", then *appa šuppariyanun* "I slept again", then
  *uḫḫun* "I saw".

*šeš-* is "lie down, go to bed, lie with" (many *šeš-* hits are the sexual idiom of the Laws and
Instructions), and *šupp-* is "be asleep". This matters for the "marked choice" question: the *swep- verb is
the one for the state of sleeping itself. A sleeper-on-knees description would select it on semantic grounds,
with no inherited formula needed. Both these paragraphs also undercut the dream signal: one is a dream report,
yet neither has a dream noun.

**Other reading findings and lemmatization misses:**
- Muršili's plague prayer (KBo 55.25+ / KUB 14.10+ / KUB 14.8): *šuppa šeški(š)kanzi*, "the priests shall
  sleep in purity", then someone "may see it in a dream (*tešḫit*)". The incubation formula uses *šeš-*, and
  *šuppa* here is the false friend *šuppi-* "pure". *šeškiškanzi* has no analyses (`mrp0sel="???"`) and was
  caught only by the spelling list. Likewise *še-eš-šu-un* (KUB 52.91).
- KBo 3.16+ (Narām-Sîn): *šuppiyaš* GIŠNÁ-*aš šeškeyaḫḫut* "sleep on a pure bed": again *šeš-* with *šuppi-*
  "pure".
- *zašḫai-* "dream" (63 tokens): 0 co-occurrences with either verb. MÁŠ.GI₆: 0 tokens in TLHdig. MA.MÚ:
  5 tokens, none with a sleep verb.
- Bare Ù is mostly Akkadian *u* "and" (920 ambiguous tokens). It counts as a dream logogram only when it
  has a Hittite complement or a Schlaf selection.
- The circled ambiguity prefixes (②Ⓐ …) on TLHdig lemmas have to be stripped before lemma matching. An
  earlier pass of this script missed *šuppariššan* (KBo 25.191) because of them.

**Decision rule B:**
- Knee alone: not significant (p = 0.11) and descriptive only (1 vs 1).
- Knee or dream: p = 0.0011 < 0.05, so the registered rule is formally met.
- As recorded above, the significance rests on *šupp-* + *tešḫa-* as a sleep collocation. With *zašḫai-*
  or dream-sense *tešḫa-* alone it is weak (p 0.04–0.26) or absent.

## Test C: Greek

**Data.** The project's prebuilt index `data/research/8c/search-index/corpora.sqlite`: hom (27,760 units,
Iliad and Odyssey), grc (281,664; GLAUx archaic–classical), grc-late (624,778; GLAUx later). These are the
same corpora `scripts/collocates_8c.py` and `scripts/search_corpora.py` read. Layers are the corpus labels.
grc-late contains some Hellenistic texts dated -400 (Theocritus, Callimachus), and grc includes rows with
`layer_status: excluded`. No unit is filtered on `layer_status`. **The Anthology is in the corpora** only
through author files: AP 7.170 is "Posidippus Epigrammata 7.170" (grc-late, TLG 1632-001). There is no
TLG 7000 Anthology file.

**Lexemes.**
- *swep-: ὕπνος (+ the mis-lemma ὕπνον) and ὑπνόω (+ ὑπνώω, and ὑπνάω, the lemma Homeric ὑπνώοντας gets).
- The rest: εὕδω, καθεύδω, κοιμάω (+ κοιμάομαι/κοιμώομαι), ἰαύω, δαρθάνω.
- Not counted: compounds (καταδαρθάνω, κατακοιμάω, συγκαθεύδω ...), which enter only a sensitivity count in
  `testC-summary.json`, and other *swep- derivatives (ὑπνώσσω 28, ὑπνώδης ...).
- Knee: lemma γόνυ.

**Lemmatization miss found: elided forms in GLAUx.** In grc and grc-late, elided tokens (γούνατ’, γόνατ’,
γούναθ’, εὕδοντ’, καθεύδουσ’, κοιμᾶσθ’, ἰαύονθ’, Ὕπν’) are missing from the unit word lists, so the lemma
index never sees them. The script matches them by spelling. That adds 51 knee tokens (grc 14, grc-late 37)
and 18 sleep tokens. Homer's index keeps its elided forms. Two other errors were seen and left: ἐφέσσεσθαι
(Il. 9.455) lemmatized as ἐπιέννυμι, and the particle γοῦν, which a naive knee search would sweep in
(4,897 tokens, excluded).

**Base rate (units containing each lexeme; a unit with two lexemes counts once for each):**

| layer | sleep units | ὕπνος | ὑπνόω | εὕδω | καθεύδω | κοιμάω | ἰαύω | δαρθάνω | *swep- share |
|---|---|---|---|---|---|---|---|---|---|
| Homer | 213 | 104 (45.4%) | 3 (1.3%) | 60 (26.2%) | 7 (3.1%) | 41 (17.9%) | 13 (5.7%) | 1 (0.4%) | 46.7% |
| archaic–classical | 988 | 486 (47.4%) | 33 (3.2%) | 74 (7.2%) | 302 (29.4%) | 124 (12.1%) | 7 (0.7%) | 0 | 50.6% |
| later | 2,452 | 1,267 (49.6%) | 122 (4.8%) | 64 (2.5%) | 535 (20.9%) | 548 (21.4%) | 20 (0.8%) | 1 (0.0%) | 54.4% |
| pooled | 3,653 | 1,857 | 158 | 198 | 844 | 713 | 40 | 2 | 52.9% |

(Per-lexeme cells can sum above the unit count, because a unit with two lexemes counts once for each.)

**The registered unit rule does not work for verse.** Homer units are single lines, and so are GLAUx verse
units; only prose units are sentences. Both recall items have the knee word on one line and the sleep word on
the next:
- Il. 22.500 has γούνασι; 22.502 ὕπνος and 22.503 εὕδεσκ’ are on later lines.
- AP 7.170 has γούνων at line 5; κοιμαθεὶς and ὕπνον are at line 6.

At the unit level there are 5 knee+sleep units, all prose and all not target (table below), so the
registered test has no positives and the recall check fails. As a documented supplement, not a redesign,
verse units were also read in a window of ±2 lines within the same poem. Prose sentences stay as single units.
A ±5 window was read as well but not tested.

**Every knee unit with a sleep word, read and classified (13):**

| locus | found in | sleep words | class |
|---|---|---|---|
| Il. 10.90 | ±2 | ὕπνος (91) | not target: knees as the vigour formula; sleep does not settle on the eyes |
| Il. 19.72 | ±2 | ἰαύειν (71) | not target: γόνυ κάμψειν "bend the knee", rest after flight |
| **Il. 22.500** (recall) | ±2; εὕδεσκ’ at ±3 | ὕπνος (502), εὕδεσκ’ (503) | **near-contrast**: ate on his father's knees; slept in the nurse's arms (owner's packet agrees) |
| Il. 5.408 | ±5 only | ὕπνου (413) | not target |
| Od. 10.481 | ±2 | κοιμήσαντο (479) | not target: supplication at Circe's knees |
| **h.Cer. 263–264** | ±2 | ἴαυσεν (264) | **positive** (borderline): Demophon "went upon our knees and slept in our arms" (γούνων ... ἐπέβη καὶ ἐν ἀγκοίνῃσιν ἴαυσεν) |
| **AP 7.170.5–6** (Posidippus; recall) | ±2 | κοιμαθεὶς, ὕπνον (6) | **positive**: dead child on his mother's knees, "lulled, holds the deep sleep" |
| Agatharchides 55 s7 / Diodorus 3.27.2 | unit | ὕπνων | not target: the elephant cannot kneel, so it sleeps against a tree (one text, two copies) |
| Dion. Hal. 20.4.6 | unit | κοιμωμένους | not target: people killed asleep, others rolling at the killers' knees |
| **Josephus AJ 8.28** | unit | κοιμωμένης, ἐπικοιμηθεῖσα | **near-contrast**: Solomon's judgment, "took my child from my knees while I slept"; knees hold the child, the mother sleeps |
| Galen, In Hipp. Epid. I 3.1.25 | unit | ἐκοιμήθη | not target: insomnia and knee pain, separate symptoms |
| Oppian, Cyn. 3.55 | ±5 only | ὕπνον, ὑπνώει, εὕδει (50–52) | not target |

**Recall checks:**
- Il. 22.500–504: found in the ±2 window, as a near-contrast, not a positive.
- AP 7.170: in the corpora as Posidippus 7.170, found in the ±2 window, positive.
- Il. 9.455 (γούνασιν) and 9.488 (γούνεσσι): knee lemma present. Neither has a sleep word, so neither is a
  candidate.
- The Hymn to Demeter item is not in the curated packet, but the owner's v15 archive already lists it
  (category "divine_knee_arm_sleep"). It is not a new find.

**Gap the preregistration did not anticipate: two sleep lexemes in one positive.** AP 7.170 has κοιμαθεὶς
(participle) together with ὕπνον (object of ἔχει). The counting rules were fixed before the Fisher test was
looked at, and three are reported:
- A, lexeme tokens: each lexeme in the positive counts once.
- B, units: does the positive contain any *swep- word?
- C, the participle/finite sleep verb only.

**Fisher (±2 window; positives against all other sleep units, pooled layers):**

| positive set | rule A: *swep- tokens / other | p | rule B: units with *swep- / without | p |
|---|---|---|---|---|
| unit rule (registered) | 0 / 0 | not testable | 0 / 0 | not testable |
| AP 7.170 + h.Cer. | 1 / 2 | 0.90 | 1 / 1 | 0.80 |
| AP 7.170 only (h.Cer. as near-contrast) | 1 / 1 | 0.78 | 1 / 0 | 0.55 |
| positives + near-contrasts (+ Il. 22.500, Josephus) | 2 / 3 | 0.85 | 2 / 2 | 0.76 |

Rule C: the sleep verbs in the positives are κοιμάω (AP 7.170) and ἰαύω (h.Cer.), so 0 of 2 are *swep-.
Base rates of the verbs alone (ὑπνόω about 1–5%) would make this unremarkable.

**Decision rule C:** no one-sided excess of *swep- in knee-supported sleep. The registered unit-level test is
not testable (0 positives, failed recall). The supplementary window has 2 positives, which is descriptive
only. The *swep- share there (1/3 tokens; 1/2 units) is at or below the 47–54% base rate.

## What this means for the proposal

- Neither tradition shows *swep- as the marked lexical choice in knee scenes.
- Hittite has one knee-supported sleep scene. Its verb fits on semantic grounds: in the two paragraphs with
  both verbs, *šupp-* names the state of being asleep and *šeš-* lying down or lying with.
- In Greek, ὕπνος is the default sleep noun in every layer, and the oldest knee-supported sleep (h.Cer.)
  uses ἰαύω.
- The Hittite dream result is the one registered significance. It rests on *šupp-* + *tešḫa-* "sleep", is
  not about knees, and does not carry over to *zašḫai-* "dream".
- The Hittite–Greek link therefore stays a scene match (Test A's question), not a lexical one.
