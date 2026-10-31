# Tier 3 batch t105 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on song and the poet's craft (an old singer teaching a boy the words,
which song to sing, a praise-song paid for with a cow or a cup, a stingy patron blamed in song, the fame a song
gives, a song for the gods, words that must be said exactly, a forgotten line), `tier3-dialogue-inworld-v1`.
Reviewer: a calibrated agent review following docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t105 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items from the `pie` field only, done before any English was printed:
   `docs/audits/packets/t105-blind-translations.jsonl`.
3. Every packet item was read word by word (person, number and case checked against each sentence, including the
   short turns). Doubtful forms were checked with `Lexicon.cells()` and the full glosses (`Lexicon.meaning`).
   The verdicts were written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t105-verdicts.jsonl`, sha256
   `ef392ce985e5de70ab145c4b082807d9f5f00a7eeebecfb5e3e40c4a00143f14`.
4. Ran `resolve_review_items.py t105`, then `score_review.py t105`.
5. Second pass: all 40 plans and records were read in full against planner-brief-v4 and the top part of the
   in-world dialogue brief. Every clause was dumped with its speaker, its sentence English, its slot glosses and
   features, and the realized sentence (the realizer does not enforce speakers or per-sentence English for Tier 3).
   After the fixes, a script checked all 40 plans and found no failures. It checked that there are two speakers with
   the user first, that every sentence-initial clause has English and no other clause does, that the speaker changes
   only at a new sentence, that the joined sentence English equals the plan English, and that each plan has 4–14
   clauses and 2–8 turns.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor (as scored) | 1/20 (withdrawn below) |

Plants caught (in the packet's spelling):
- dʰugh₂térn̥s: ACC.PL "daughters" used for the address "Daughter, my voice is old". The vocative dʰúgh₂ter is
  needed, and the record has it.
- káproh₁: NOM/ACC.DU (or INS.SG) in "the tale of the goat and the serpent". The genitive is needed; the record has
  káprosyo h₁égʷʰis-kʷe. h₁égʷʰis is a valid GEN.SG of h₁ógʷʰis (beside h₁égʷʰeys), as the engine's cells show.
- gʷm̥tóm: IMP.2DU "come (you two)" said to one wife. The 2SG gʷm̥dʰí is needed, and the record has it.
- léykʷm̥: AOR.1SG in the grandmother's short answer "You left out nothing". The 2SG léykʷs is needed.
- pedés: GEN/ABL.SG "of the foot" in "at your feet" (h₁épi). The LOC.PL pedsú is needed, as in the record.

**Real minor and its outcome:**

| item → record | finding | outcome |
|---|---|---|
| f070bfa0 → 00005 | mért (AOR) in the general statement "Fame does not die" | **withdrawn**: the lexeme mért has only aorist forms, so the gnomic aorist is the rule (v4 rule 8). The same holds for mért in 00013 and ḱn̥sént in 00016 (ḱens- has no present). |

**Packet: real wrong 0/20 and real minor 0/20 after the withdrawal, before and after the fixes.**

## Blind back-translation agreement

All six were translated before any English was seen. Four agree in substance. The two partial misses are
misreadings of single words, and neither points to an error in the PIE:

| item | divergence |
|---|---|
| e54d92f6 | The quoted line h₂éwey moy péh₂ura h₂éwey téḱnōy séngʷʰe was not understood: the reviewer read péh₂ura as a form of "fire", but it is the VOC.F "little" ("Bird, little bird, sing for my child!"). The rest agrees. |
| 9b7df160 | Agrees. h₁yód … wérh₁oh₂ was read as "a word that I say", not "if I say". |
| 6b64069d | Agrees except for kh₃téws h₂éti gʷémt, read as "went beyond the border". It means "came back from the battle". |
| be3e209d | dʰh₁tléh₂i ("at the assembly") was read as "with a gift". h₁áyso ("take!", MID IMP of h₁ay-) was read as "bronze". The rest agrees. |
| d709fd13 | Agrees. |
| cb782237 | méne ("my", GEN.1SG) was read as "first". The rest agrees. |

## Second pass: all 40 records

**Grammar.** No wrong forms were found in the 40 records. These were checked one by one:
- **Short answers and their `case`:** 0002 (ACC ×2), 0004 (NOM exclamation), 0006 (DAT), 0009 (NOM, answering "what
  is my reward?"), 0012 (ACC), 0016 (DAT), 0021 (LOC), 0024 (GEN), 0029 (ACC), 0030 (NOM), 0032 (ACC) and 0038 (NOM)
  all fit their questions.
- **Cows:** every gʷṓws slot is `gender: f`. These are 0003 (gʷṓm, h₁íh₂, h₁uséwih₂, dwóyh₁ gʷówh₁e), 0012
  (tísrn̥s gʷṓs), 0020, 0022 and 0027.
- **h₂élyos** has a gender everywhere it is used. It is h₂élyons m in 0019, a MOD in 0029, and h₂élyod n in 0029
  and 0039.
- **Predicate adjectives with dropped subjects** agree with the speaker or addressee: m in 0001, 0003, 0005, 0014
  and 0036; f in 0030 (mudréh₂, said to and by a sister).
- **Athematic obliques** are correct: kh₂n̥méni, kh₂n̥mń̥su, h₁éh₃si, ph₂wéni, h₁n̥gʷnéyey, h₃rēǵés, pedsú, nékʷts,
  gʷnéh₂ey, kh₃téwi/kh₃téws, h₂uséy/h₂usés, uksnés, m̥lités and pótn̥yeh₂s.
- **Enclitics** stand in second position or after the first constituent, including the stacked moy toy in 0014
  and 0010.

**Modern or coined words.** There are none. The only `coined: project` tokens are h₂énHos "grandmother", spélom
"tale" and mógʰus "boy", which v4 "Project reconstructions" allows.

**Senses (checked against the full glosses).** These words were checked and are all in their glosses: h₂éwh₂os for
"uncle" (0006: "maternal grandfather; maternal uncle"); wiHrós for "hero/warrior/husband"; wédʰeti for "bring";
kéh₂ilos for "whole"; tentlom for "loom"; bʰoydʰéh₂ for "oath"; wetsós for "calf"; tewtéh₂ for "people";
memóne for "remember"; péh₂uros for "few"; léh₁t for "allow"; h₁wogʷʰéyeti for "promise"; and smey- for "laugh".
h₁yód for "because" (0027) is the lexicon idiom for "because". The causative-shaped sokʷéyeti is glossed "to say".

**Sing, say and hear verbs; 'hymn' and 'tale' nouns.** All the rotated verbs say what their English says:
- sing: gʷéHyeti, séngʷʰeti ("sing, recite") and kh₂néti ("sing, chant");
- say: wéwket, mléwHti, sékʷt, wérh₁t ("say"), bʰéh₂ti and h₂roh₁dʰéyeti ("speak"), sokʷéyeti and weryeti;
- hear: ḱléwt, ḱlush₁yéti and h₂wéyst ("hear"), ḱléwseti ("listen"), ḱlowséyeti ("heed"), and h₂ḱh₂owsyéti
  ("hear well", for "the god hears everything").

h₁erkʷós is always "hymn/song of praise", kéh₂nmn̥ "song", and spélom "tale".

**Paraphrases.** All are faithful:
- the poet is "a man who knows many hymns" (h₂nḗr h₁yós polh₁úns h₁erkʷóns ǵn̥néh₃ti, 0026);
- a line is "words" (wékʷesh₂, 0008 and 0031);
- blame is "bad words about me" (h₂egʰéh₂ wékʷesh₂ méǵʰye h₂m̥bʰí, 0012);
- "exactly" is "straight" (h₃reǵtéh₂ h₁nómn̥h₂, a MOD on "the names", 0029).

**Speakers and English.** Every record has exactly two speakers, user first, and English on every sentence-initial
clause. Each turn answers the one before. 0002 addresses the singer with the feminine compound h₁súḱlewes. Nothing
in the dialogue contradicts this, so it was left as it is. One English problem was found:

| record | finding | fix |
|---|---|---|
| 00031 | "I too forgot **once**": "once" has no slot (rule 14) | minor; English "I too forgot." |

**Second pass: real wrong 0/40 before and after; real minor 1/40 before, 0/40 after.**

## Requests: 18 → 10

Before the fixes, 18 dialogues had the user asking the speaker to do something (sing, tell, teach, recite,
praise, set a name). They were 0001, 0002, 0003, 0006, 0009, 0010, 0014, 0015, 0017, 0019, 0022, 0024, 0028, 0029,
0032, 0037, 0038 and 0039. The lead counted about 20, which also takes in the borderline 0018 and 0040. Eight were
turned into exchanges where the user tells something or asks about something. Each change replaces or drops a single
clause, so the token count stays clear of the theme-cap boundary: the cap is round(0.015 × tokens), and h₁erkʷós,
wékʷos and kéh₂nmn̥ are each at 22.

| record | before | after |
|---|---|---|
| 0001 | "Grandfather, teach me: I shall sing the hymn of the gods." / "Say the words to me!" | "Grandfather, I shall sing the hymn of the gods." / "Which are the words?" (kʷéh₂ wékʷesh₂?), answered by the model's quoted first words |
| 0006 | "Then teach me: I shall sing the hymn with you." | "Then I too shall sing the hymn with you." (… tébʰye ḱóm éti gʷéHyōh₂) |
| 0010 | "Shall I sit at your feet too?" | "I too shall sit at your feet." (statement) |
| 0014 | "I know nothing new. Teach me." | "I know nothing new." The model's "Now you are wise" now answers it directly. |
| 0015 | "Lament for my husband. He died in the battle." | "My husband died in the battle." (wiHrós moy kh₃téwi mért); the singer then offers to set his name in the song |
| 0022 | "Now say me the hymn, all of it." | "Now do you know the hymn, all of it?" (… wóydth₂e?), and the boy answers by reciting it |
| 0029 | "Then show me the names, old shepherd." | "Then I shall learn the names, old shepherd." (h₁éwkoh₂) |
| 0032 | "… a holy hymn. Then say it. May it rain!" | "Then say it." dropped |

After the fixes, 10 dialogues have a request: 0002, 0003, 0009, 0017, 0019, 0024, 0028, 0037, 0038 and 0039. These
are the batch's own scenarios: the feast song, the paid praise, the lullaby, the commissioned horse-song, the work
song, the patron's praise, the tale against the wolves, the naming song, and the host's song. The borderline 0018
("what words shall I speak at the oath?") and 0040 ("give them to your sons") bring the count to 12 at most.

## Formulas

The counter says 19 records. By eye, **16 records use a formula in its sense** (20 uses): 0001 (Father Sky),
0002 (slew the serpent; swift horses), 0003 (imperishable fame), 0008 (good fame, as a predicate), 0009, 0022 and
0027 (Dawn, daughter of Sky), 0010 and 0035 (famous name, as a predicate), 0013 and 0026 (great fame), 0014 and 0036
(giver of good things), 0029 (Father Sky; Mother Earth), 0030 (swift horses, as a predicate), and 0038 (famous name;
set a name for a newborn). None is forced into its turn. The counter's false hits are:
- 0019: "swift" is a predicate on a pronoun, not the phrase;
- 0028: name and dʰeh₁- are in different sentences;
- 0015: "set his name in the song" is not name-giving, so it is a fine sentence but not the formula;
- 'good fame' in 0003, 0013, 0026 and 0036: the words only co-occur.

The re-run still counts 19.

## Gate

After the fixes, re-realized with `realize_plans.py data/generation/plans/t105.jsonl --batch t105 --model
claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`:

| measure | value |
|---|---|
| plans / realized / exact_pass | 40 / 40 / 40 |
| reject_rate | 0.0 |
| tokens | 1459 |
| max_lexeme_uses | 7 (cap 7) |
| theme_core_uses | ≤ 22 (cap 22) |
| roots_per_sentence | 3.5 |
| distinct lexemes / roots | 242 / 140 |
| formula_uses (counter) | 19 |
| gate | **PASS** |

There is one warning, unchanged. In 0005, h₂éǵet "drove" is one letter from h₂éǵt "said", and the English
correctly means "drove".

## Engine or brief gaps

There are no engine gaps. One brief observation: the formula counter (`_formula_uses`) counts lexeme
co-occurrence, so it overcounts by about 3 records here, as in earlier batches.
