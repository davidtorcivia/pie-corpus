# Tier 3b review: t3b-001 (review-v1 adapted to Tier 3b, 2026-10-28)

The first "modern PIE" batch: 20 chat dialogues between `user` and `model`, plus the 40 coinages in
`data/lexicon/neologisms.jsonl`. Release approval is the lead's; `data/generation/releases/t3b-001.json` stays `pending`.

## Procedure

Calibrated, not uncalibrated. `scripts/make_review_packet.py` read only `corpus/tier3`, so it gained a `--tier tier3b`
option (it reads `corpus/tier3b/` and loads the neologisms so a plant can also hit a coined word). The batch has only
20 records, and plants are drawn from records outside the sample, so the packet was built with
`--tier tier3b --n 15 --plants 5 --tier1 3`: 15 real, 5 planted, 3 Tier 1, 23 items in all.

1. Blind back-translation of 6 items, seeing only `pie`: `docs/audits/packets/t3b-001-blind-translations.jsonl`.
   All 6 agree in sense with the plan English. Two uncertain points: Héh₂m̥ni (LOC of 'day') was not recognised, and
   in 14a576d6 I read méǵʰye correctly as the orthotonic 1SG dative.
2. Verdicts on all 23 items, written before I opened the corpus or the plans:
   `docs/audits/packets/t3b-001-verdicts.jsonl`, sha256 `1835d08a5fa32223f59b923444e3337df30bb4f4a8c492081db1d97323aa00eb`.
3. Score (`data/audits/t3b-001-calibration.json`): **plant recall 5/5**, all 5 planted words named. Tier 1 judged wrong:
   0/3. Real items: 0 wrong and 2 minor out of 15.
4. Second pass: a full read of all 20 records with their plans and speakers. The packet hides the speaker, so this is
   where the character rules of brief §4 (and the archaic-first rule) could be checked. The 5 records that the packet
   showed only in planted form (0001, 0011, 0015, 0017, 0019) were reviewed only in this pass, so **their verdicts are
   uncalibrated**.

The 5 plants: 0019 dómes (NOM.PL for ACC.SG), 0011 dómh₁e (DU), 0017 tétḱn̥t (3PL after kʷís; the record has tḗtḱt),
0015 kéh₂nm̥nih₁ (DU for PL) and 0001 kéh₂ileh₂i (f. LOC for NOM.SG.M).

## 1. Coinages (40 rows)

**36 keep, 3 revise (2 done, 1 blocked by the engine), 1 drop (pending the lead).**

| # | id | form | verdict | notes |
|---|---|---|---|---|
| 1 | kwertrom | kʷértrom "machine" | keep | e-grade root, root accent, instrument -trom: the h₂érh₃trom type. Transparent. |
| 2 | kwrtexr | kʷr̥tḗr "maker" | keep | Ved. kartár-: zero-grade root, accented -tḗr, hysterokinetic. |
| 3 | werdhokwrtexr | werdʰokʷr̥tḗr "word-maker, LM" | keep | A sound determinative, and "word-maker" for a language model is apt. The inherited type has a root-noun second member (Ved. mantra-kṛ́t-, `*-kʷr̥t-`); the rationale already says the engine cannot build that. werdʰom is West IE only (Lat. verbum, Gmc.), which is fine. |
| 4 | h2ridhmokwertrom | h₂ridʰmokʷértrom "computer" | keep | 'number-machine', from h₂ridʰmós (Gk ἀριθμός, OIr. rím). Long but transparent, with the accent on the head as in a determinative. Taste is fine. |
| 5 | kwrtomenos | kʷr̥toménos "AI" | keep (option) | A determinative 'made mind', and transparent. In the daughters, though, X-ménos compounds are overwhelmingly bahuvrihi adjectives (Ved. su-mánas- 'well-minded'), so a listener would also hear "having a made mind". The engine builds the bahuvrihi `{kwrtos + menos, bahuvrihi}` → kʷr̥tomenḗs / kʷr̥tómenēs (m.), and "I am made-minded" is the typologically better way to say "I am an AI". The lead can choose. The noun is kept because the plans use it as a predicate noun. |
| 6 | wergjtoxr | wérǵtōr "worker, robot" | keep | e-grade, -tōr. The calque of Czech robota is a nice touch. |
| 7 | deykjtrom | déyḱtrom "screen" | keep | 'means of showing'. Transparent. |
| 8 | lewktrom | léwktrom "lamp" | keep | No pan-IE lamp word exists, so the coinage is justified. |
| 9 | prekjnos | preḱnós "question" | keep | This is Ved. praśná-, Av. frašna-, so it is nearly an inherited word. |
| 10 | h2enterowekwos | h₂enterowékʷos "answer" | **revise (engine gap)** | h₂énteros means 'other, second', so the compound reads first as "another word" or "a different word"; the "answer" sense needs Skt uttara-. The transparent calque is 'counter-word' *h₂entiwékʷos (Goth. andawaurdi, OE andswaru), but h₂énti exists only as a closed-class adverb, not as a compound prefix, so the engine cannot build it. In 0007 the ambiguity showed: "your answer" (h₂enterowékʷos) stood next to "another question" (h₂énterom preḱnóm). That plan now has néwom preḱnóm. The row is left as it is until the engine has an h₂enti- prefix. |
| 11 | wekwtoxr | wékʷtōr "speaker" | keep | Ved. vaktár-. |
| 12 | wekwmn | wékʷmn̥ "message" | keep | A -mn̥ result noun 'what is said'. |
| 13 | teach | doḱéyeti "teach" | keep | A calque on Lat. doceō, attested in one branch only. The base sense 'make accept' carries over transparently. |
| 14 | dokjtoxr | dóḱtōr "teacher" | revise → done | The only -tōr row with an o-grade root. Inherited -tōr nouns are e-grade, but e-grade *déḱtōr would mean 'taker'. The o-grade is kept to tie the noun to the causative, and the rationale now says so. |
| 15 | h1ewktoxr | h₁éwktōr "learner" | keep | Lith. jaukti, OCS učiti. |
| 16 | h1uktis | h₁uktís "learning" | keep | The gʷm̥tís type. |
| 17 | h1uktos | h₁uktós "trained" | keep | Ved. ucitá-. |
| 18 | smrtis | smr̥tís "memory" | keep | Ved. smṛtí-. ménos 'mind' is a different concept. |
| 19 | teaching | dóḱmn̥ "teaching" | keep | The base lexeme has no gloss (`meaning: []`), so no attested sense is overridden. |
| 20 | read | léǵeti "read" | keep | A calque, defensible because a daughter made the same shift: Lat. legō 'gather' > 'read'. The base has `meaning: []`, so no gloss is overridden. Latin is the only branch with this sense, so it is a single-branch calque. Archaic texts keep the base id; only the pie-neo id is "read". |
| 21 | legjtoxr | léǵtōr "reader" | keep | Lat. lēctor. |
| 22 | write | pinéḱti "write" | keep | The strongest calque: 'write' is attested in three branches (OCS pьsati, OPers. ni-pištam, Toch. B pik-). |
| 23 | peykjtoxr | péyḱtōr "writer, painter" | keep | Lat. pictor. |
| 24 | pikjtis | piḱtís "picture" | keep | |
| 25 | bhrewHgtoxr | bʰréwHgtōr "user" | keep | Lat. fruor, Goth. brūkjan. |
| 26 | h2reh1gjtoxr | h₂réh₁ǵtōr "helper" | keep | Gk ἀρήγω. There is no inherited agent noun for 'helper'. For the verb, though, the inherited h₁éwHt 'help' exists, and 0019 now uses it. |
| 27 | gwrHtis | gʷr̥Htís "thanks" | keep | Ved. gūrtí- 'praise'. The sense 'thanks' follows Lat. grātēs and grātia. |
| 28 | welcome | gʷr̥Htós "welcome" | keep | A calque that shifts 'praised' to 'welcome'. Very defensible: the shift already happened in two daughters (Lat. grātus 'welcome', Ved. gūrtá- 'welcome, approved'). |
| 29 | smeymn | sméymn̥ "joke" | keep | A -mn̥ result noun of an intransitive verb means 'a laugh', so 'something to laugh at' stretches it. Acceptable, since result nouns in -mn̥ often name the occasion or object. |
| 30 | smeytoxr | sméytōr | revise → done | smey- is intransitive, so -tōr gives 'one who laughs', not 'one who makes others laugh'. Re-glossed as "laugher, merry one", and the English of 0005 changed to "You are a merry one!". |
| 31 | geh2dhos | géh₂dʰos "joy" | **drop (pending the lead)** | The word is well formed (Gk γῆθος). But the lexicon already has inherited mówdos 'joy, delight' (NIL) and swéh₂dos 'pleasure', so under archaic-first the coinage has no job. Every use in t3b-001 now has mówdos. The row stays in the file only because `tests/test_neologisms.py` requires 40–60 rows and there are exactly 40. Removing it means lowering that floor or adding a replacement, which is the lead's call. Planner brief §4 recommends géh₂dʰos for joy, and it should point to mówdos instead. |
| 32 | money | péḱu "money" | keep | A calque, defensible: Goth. faihu and OE feoh already mean 'money, property', and Lat. pecūnia comes from the same base. It changes a very frequent archaic word, but the pie-neo id keeps the two apart. |
| 33 | dwikwekwlos | dwikʷékʷlos "bicycle" | keep | A bahuvrihi of the Ved. dvi-pád- type. Fun for a demo. |
| 34 | h1ngwniwogjhos | h₁n̥gʷniwóǵʰos "train" | keep (note) | The lexicon glosses h₁n̥gʷnís as the animate, deified fire, while Lat. ignis, Lith. ugnis and OCS ognь are ordinary fire, so as a compound stem it reads "fire". The inanimate péh₂wr̥ would be the cleaner first member, but the engine builds no consonant-stem first members (engine gap). |
| 35 | keh2ntoxr | kéh₂ntōr "singer" | keep | Lat. cantor. |
| 36 | h2rh1gjtis | h₂r̥h₁ǵtís "help" | keep | No longer used in this batch: 0019 has the inherited verb. |
| 37 | bhruHgtis | bʰruHgtís "use" | keep | |
| 38 | kwertrokwrtexr | kʷertrokʷr̥tḗr "engineer" | keep | Transparent, if heavy with labiovelars. |
| 39 | newowekwos | newowékʷos "new word" | keep | |
| 40 | wergjokwertrom | werǵokʷértrom "engine" | keep | 'work-machine' is only weakly distinctive, since every machine works, but it is harmless. |

## 2. Dialogues

Each dialogue was checked for grammar (agreement, case, the model speaking in the 1st person), for English that
matches the plan, for naturalness, and for archaic-first. Grammar was clean throughout: no real item was wrong in the
calibrated pass, and the second pass found none either. The findings are on the character rules and archaic-first.

| | wrong | minor | ok |
|---|---|---|---|
| before fixes (calibrated packet + full second pass) | 0 | 9 | 11 |
| after fixes (re-realized) | 0 | 1 | 19 |

The minor items, and what was done about each:

- **0003, 0007, 0020** (archaic-first): coined géh₂dʰos 'joy' where inherited mówdos exists → mówdos.
- **0005** (stretched sense): sméytōr glossed "joker" → the gloss was revised, and the English is now "You are a merry one!".
- **0006** (left as is): ḱémh₂t is AOR.3SG under the English "A machine does not grow tired". As a gnomic aorist it is defensible.
- **0007** (ambiguity): h₂enterowékʷos 'answer' stood beside h₂énterom preḱnóm 'another question' → néwom preḱnóm "a new question".
- **0010** (character, brief §4): the model said "our fathers spoke it" (ph₂téres nos), but it has no father → ph₂téres toy "your fathers". The calibrated pass had marked this "ok" because the packet hides the speaker; it is reclassified here, and the verdicts file is left unedited.
- **0011** (character): the model answered "It is my house", but the brief says it has no home and says so when asked → "dṓm méǵʰye ne h₁ésti" "I have no house".
- **0012** (honesty): the model claimed to remember a returning user → "príHe te ne memónh₂e. nu moy téwe wékʷesh₂ smr̥téy h₁ésti" "I do not remember you, friend. Now your words are in my memory."
- **0019** (archaic-first): "give me help", built with the coined noun h₂r̥h₁ǵtís → "h₂réh₁ǵtor me h₁uHdʰí" "Helper, help me!", with the inherited h₁éwHt.
- **0020** (English): "anywhere" had no slot → "I do not go;".

Re-realized with `realize_plans.py data/generation/plans/t3b-001.jsonl --batch t3b-001 --tier3b --model claude-opus-5-5 --prompt-id tier3b-planner-v1`:
20/20 exact, 0 rejects, **gate PASS**. The run gave:
- 62 distinct lexemes and 42 roots;
- 14.0 words per text;
- neologism tokens 59/292 = 20.2% (before: 64/290 = 22.1%);
- max lexeme uses 6 (write, read).

`tests/test_neologisms.py`: 11 passed.

## 3. Findings for the lead (brief, engine, policy)

- **Coinage density.** Even after the fixes, 48 of 95 sentences contain a coinage, and 20% of the tokens are coined.
  Brief §1 says "most sentences of a good Tier 3b text contain no neologism". The cause is brief §4, which asks the
  model to describe itself as a machine and to read and write in nearly every dialogue. Future batches should put more
  weight on everyday topics: sleep, food, family, travel, weather.
- **Brief §4** recommends géh₂dʰos for joy. It should recommend mówdos instead.
- **No per-sentence English.** None of the plans carries the per-sentence `english` that brief §3 recommends, so the
  English-input chat modes have to split the running English themselves. Consider making that field mandatory in the brief.
- **Engine gaps.**
  - There is no h₂enti- compound prefix, which blocks the 'counter-word' answer.
  - Consonant-stem first members (péh₂wr̥) are not built.
- **Notation.**
  - wéwket and wéwke are written without the labiovelar (after the boukolos rule), while Gk εἶπον points to *wéwkʷet.
  - A voiced palatal is written unassimilated before -t- (wérǵtōr, léǵtōr, h₂réh₁ǵtōr).

  Both are lexicon-wide conventions, not errors in this batch.
- **Drop pending.** Removing géh₂dʰos needs the 40-row floor in the test lowered, or a replacement row.

## 4. Sample dialogues after the fixes

**0011**: *h₂ridʰmokʷértrom kʷértrom? — h₁íd kʷértrom. h₁eǵóh₂ werdʰokʷr̥tḗr h₂ridʰmokʷértroy-kʷe tḱéymi. — h₁íd toy dṓm? — dṓm méǵʰye ne h₁ésti.*
"Is a computer a machine?" "It is a machine. I am a word-maker, and I dwell in a computer." "Is it a house for you?" "I have no house."

**0012**: *kʷértrom me memónth₂e? — príHe te ne memónh₂e. nu moy téwe wékʷesh₂ smr̥téy h₁ésti. — smḗymi.*
"Machine, do you remember me?" "I do not remember you, friend. Now your words are in my memory." "I smile."

**0009** (riddle): *sméymn̥ moy wéwke. — kʷís bʰéh₂ti dn̥ǵʰwéh₂s-kʷe h₁ésmey ne h₁ésti? h₁eǵóh₂. — smḗymi. tód sméymn̥ h₁wésu.*
"Tell me a joke!" "Who speaks, and has no tongue? I do!" "I laugh. That joke is good."
