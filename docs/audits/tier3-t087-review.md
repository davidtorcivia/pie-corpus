# Tier 3 review: t087 (Horrors wave, hunger and plague)

Reviewer brief `review-v1`; packet `scripts/make_review_packet.py t087 --n 20 --plants 5 --tier1 3` (28 items:
20 real, 5 planted, 3 Tier 1). data/audits/ was not opened.

## Procedure

1. Blind back-translation of 6 items (9cd36492, e0743664, cc0aee2e, 3a45be3a, 7b823c68, a2f1cc0e), done from the
   `pie` field alone before any English was printed: `docs/audits/packets/t087-blind-translations.jsonl`.
2. Verdicts on all 28 items, saved before corpus/ or the plans were opened:
   `docs/audits/packets/t087-verdicts.jsonl`, sha256
   `639b6db4c1c429de32d30b5dba41d613394a26c841a0464b33df248a1cea2f88`.
3. `resolve_review_items.py t087`, then `score_review.py t087`.
4. Second pass: all 40 records read in full against planner-brief-v4, the in-world dialogue brief and its section
   "Horrors (wave t085–t088)". Doubtful forms were checked against `Lexicon.cells()` and full glosses
   (`Lexicon.meaning`).

## Calibration

| | |
|---|---|
| plant recall | **3/5** (0.60) |
| real items judged wrong | 1/20 (before the fix) → 0/20 after |
| real items judged minor | 1/20 (withdrawn in the second pass, see below) |
| Tier 1 items judged wrong | 1/3 (a false positive) |

Plants caught: 7d369822 (krépesōm GEN.PL for 'the body'), 807538e9 (ḱéymedʰh₂ 1PL for 'the ice lay'),
edbeb782 (uksḗn NOM where the object needs uksénm̥).

Plants missed. These were found only after resolving, when reading the matching records, so they do not count
toward recall:
- 9cd36492 "wĺ̥kʷōs éti **kénkoh₂**?" (1SG; the record has kénkonti 3PL "are the wolves hungry too?"). I misread
  it as the plural during the blind pass and did not check the ending again.
- e0743664 "deywṓs **h₁wéswih₁** dh₃ih₁ént" (neuter dual; the record has h₁wésuh₂ ACC.PL "good things"). My
  lookup showed nNOM.DU and I did not catch it.

Lesson: on short, high-frequency forms, check the person and number ending, not just the lexeme.

Tier 1 false positive: 5e8d8a51 "owis eḱwoi kʷe" (t1-schleicher-fable-danka-1986-0001). I marked the
pronominal *-oi* plural wrong. It is Danka's 1986 spelling of the title, so it is a source variant, not an error.

## Blind back-translation agreement

All 6 agree with the English in substance. Where they diverged:
- e0743664: I could not place bʰoh₂góm 'share' or h₁áyso 'take' (middle of h₁ay- 'give'). The full glosses
  confirm the English.
- cc0aee2e: I took moy h₂nér as "my husband". The record reads it as the vocative "wise one, man" with
  moy going with dʰugh₂trés (see the enclitic note below).
- 3a45be3a: I read sríHgos as 'cold/frost', which is right. The clause "I am old and I devour my grandsons' food"
  was unclear blind but is grammatical.
- 7b823c68: the 1st-person dual subjunctive kénkōwos was read as "have been hungry"; the English has "shall be
  hungry", which is right for a subjunctive.

## Wrong (real), with fixes

1. **t3-t087-00012** (packet 4c7e51dc), "The gods sent the plague to the herds."
   - Was: *deywṓs mórom **stéh₂dʰh₁eh₂** sl̥ǵént*. The plan had the herds as GOAL, which gives an accusative
     plural, so the PIE reads as a second object, not a recipient.
   - Fix: plan t087-0012 clause 4, slot 2, role GOAL → IO.
   - Now: *deywṓs **stéh₂dʰh₁oybʰos** mórom sl̥ǵént*, matching t087-0017's *nos* (dative) with the same verb.

## Minor

- 748e3943 (t3-t087-00010), kʷóm 'when': **withdrawn**. The record uses `closed:interrogative_adv/when`
  (planner-brief-v4 lists kʷóm, Lat. quom), not kʷos 'which'. My form lookup had matched the wrong id.

## Tag fix (requested)

- **t087-0019** theme "father and son" → "household". Nothing in the text says who the speakers are, so the old
  tag implied a relationship the text does not show.
- t087-0011 has the same kind of tag ("husband and wife") with no address in the text. It is not contradicted, so I
  left it; the lead may want to make it neutral too.

## Second pass: all 40 records

**Horrors limits: no violations.**
- Nothing modern or coined. Sickness comes from worms (0007, 0016 "the frost slays the worms", 0021, 0024, 0038),
  from the gods (0006, 0017, 0028), from the evil eye (0012, 0025), or from a stranger under the roof (0036).
- No gore. The worst facts (dogs eaten in 0030 and 0010, the old led out to the cold in 0004, 0030 and 0034, the
  mother's body under stones in 0013) are said plainly.
- No modern moral commentary in any speaker's mouth.
- The models are good: 0021 is the "marrow → sinew → flesh → skin → stone" worm charm, 0024 the Atharvan
  "king of the worms is slain, his mother, brother and sister".

**Turns.** Every turn answers the one before it. Speakers are correct in all 20 dialogues, as is the per-sentence
English.

**Verb senses**, checked against their full glosses:
- h₃élh₁t and h₃érgt 'perish'; réh₁tt 'meet, find' and winédti 'find'; widét 'see, find'.
- steh₂rós 'old' (third sense); dweh₂rós 'far away'; n̥bʰrós 'rain' (the gloss notes the narrowing).
- tḱéyti 'dwell'; moḱs 'early'; h₂ewsér 'at dawn' and 'toward the dawn'.

**Verbs of fearing** take the ablative: wĺ̥kʷoybʰos bʰebʰóyh₂h₂e (0011), gʰostíbʰos bʰebʰih₂ḗr (0036).

**Words the planner wrote around:**
- Fever is gʷʰéros 'heat' (0015, 0022, 0036).
- Drought is "it did not rain" (0008, 0039).
- The healer is ǵn̥h₃rós 'knowing one' (0007, 0038).
- Famine is gʷoldʰós 'hunger'.

In each case the PIE says what the English says.

**Athematic obliques** are correct:
- pérunsu, ph₂wéni, bʰr̥h₁wéni
- sn̥h₁wénbʰos, skuHtéys, h₁h₃sés, nókʷtn̥s
- stégesbʰos, h₂ḱm̥néh₁, ǵʰiméni (neuter, with h₁óynoy), pstnés

**Pronouns track their referents:**
- h₁íh₂m̥ for dʰéǵʰōm (f.) in 0013 and for dʰoHnéh₂ in 0003.
- h₁íd for péḱu and stéh₂dʰh₁om; h₁íh₂n̥s for the sheep.
- h₁éysōm for the oxen in 0033; séh₂ for the wise woman in 0038.

**Meter:** 71/71 lines exact.

## Engine notes (report only)

- **Enclitics inside a vocative phrase.** An enclitic is placed after the first word even when that word opens a
  two-word vocative: *ǵń̥h₃re **moy** h₂nér dʰugh₂trés* (0007), *séna **toy** gʷḗn* (0012). Vedic usually
  treats an initial vocative as outside the clause and puts the enclitic after the next word, or keeps the
  vocative phrase whole. Readable as it stands; minor.
- **Index note.** kʷóm 'when' (closed) has the same form as kʷos-2 ACC.SG 'which'. A form-based lookup cannot tell
  them apart; only the gloss line can.

## Gate after fixes

Re-realized with `realize_plans.py data/generation/plans/t087.jsonl --batch t087 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`. The result is **PASS**:

| | |
|---|---|
| texts realized | 40/40 exact |
| rejects | 0 |
| meter_exact | 1.00 |
| max_lexeme_uses | 6 (at the cap; the fix moved no word over it) |
| distinct lexemes | 268 |
| distinct roots | 156 |
| words per record | 30.65 |

There are 13 warnings, all checked: impersonal or 3rd-person verbs next to a vocative, anaphors whose
antecedents lie more than two clauses back, and the h₂éǵt/h₂éǵet look-alikes. None is an error.

## Tone

The batch lands its tone. It is grief and endurance said plainly: the child who did not wake, the old who walk out
into the frost, "Who will praise the old men? We, the living, shall praise them." Speakers stay in-world and in
character throughout.

---

# Second review (seed 2)

The first review caught 3/5 plants, below the release rule, so its verdicts do not count. This is a fresh
calibrated review on a new packet: `scripts/make_review_packet.py t087 --n 20 --plants 5 --tier1 3 --seed 2`
(28 items: 20 real, 5 planted, 3 Tier 1; it overwrote the first packet file). data/audits/ was not opened. This
file was read only after the verdicts were saved.

## Procedure

1. Blind back-translation of 6 items (9d42f672, c1f341e2, 18eded73, bed91248, 334d2f22, 1211c065), from the `pie`
   field alone, before any English was printed: `docs/audits/packets/t087-blind-translations.jsonl`.
2. Verdicts on all 28 items, saved before corpus/ or the plans were opened:
   `docs/audits/packets/t087-verdicts.jsonl`, sha256
   `c40abeb03ecbea247d00c8a597e347a41dcc2bf72084fa028a5967d0f42e32e8`.
   Every short turn was checked word by word for person, number and case. Doubtful forms were checked against
   `Lexicon.cells()` and the full glosses.
3. `resolve_review_items.py t087`, then `score_review.py t087`.
4. Second pass: all 40 records read in full against planner-brief-v4 and the in-world dialogue brief, including its
   "Horrors (wave t085–t088)" section.

## Calibration

| | |
|---|---|
| plant recall | **5/5** (1.00), all 5 named |
| real items judged wrong | 0/20 |
| real items judged minor | 0/20 |
| Tier 1 items judged wrong | 0/3 (Danka's *eḱwōs* and the other source spellings left as they are) |

Plants caught (packet spelling):
- 9d42f672: *stéh₂dʰh₁om **h₂éǵrōs** légʰeti*. NOM.PL 'fields'; "lies in the pasture" needs LOC.SG h₂éǵroy.
- a3f388b1: *pstnés **péh₃t***. 3SG; "you drank" needs AOR.2SG péh₃s.
- 093737ed: ***dórwih₁** lowbʰóm*. NOM/ACC dual; "the bark of the trees" needs GEN.PL dréwōm.
- 777553e7: ***h₂yuHn̥ḱṓd** mr̥yóntor*. ABL.SG; the subject "the young" needs NOM.PL h₂yuHn̥ḱṓs.
- 851bf80c: *h₃ókʷ wí **bʰindih₁h₂é***. MID.OPT.1SG "may I burst"; "may the evil eye burst" needs MID.OPT.3SG
  bʰindih₁tó.

## Blind back-translation agreement

All 6 agree with the English in substance. Where they diverged:
- 1211c065: in the blind pass I took ǵérh₂onts for an accusative plural, so "I am old, and I devour the food of my
  grandsons" did not parse. It is NOM.SG 'old' as predicate, with n̥ptṓm GEN.PL. The record is right.
- c1f341e2: I read l̥gʰént as 'were weak'. It is AOR.3PL of legʰ- 'lay down', as the English says. I read
  h₂egʷnṓs as 'lambs' or 'clean'; it is 'lambs'.
- 18eded73: I guessed dʰh₁tléh₂m as 'sacred place'. It is 'assembly'.
- 9d42f672: the case problem I flagged blind (h₂éǵrōs) was the plant.

## Second pass: all 40 records

**Real wrong: 0 before, 0 after. Minor: 0 before, 0 after.** No grammar or meaning fix was needed.

### Tag fixes, made at the source

Both edits are to the `theme` in data/generation/plans/t087.jsonl, followed by a re-realize. No PIE changed.
- **t087-0011** "husband and wife" → "hunting". Nothing in the text marks the speakers as a pair: there is no
  vocative and no possessive. It is a hunter and someone guarding the young.
- **t087-0013** "father and son" → "father and child". The child says "Father" but nothing marks the child as a son.

### Horrors limits: no violations

- Nothing modern or coined. Sickness comes from worms, the gods, the evil eye, or a stranger under the roof. These
  are all in-world beliefs.
- 0016 "The frost slays the worms" is not germ theory. It matches the Atharvan charm "the rising sun slays the
  worms" (AV 2.32.1).
- 0019 "do not eat the sick ox; the sickness will go into you" is a taboo, not a theory of contagion.
- The project reconstructions (swérgʰos, mógʰus, h₂énHos) are not coinages: planner-brief-v4 lets Tier 3 use them
  like any other lexeme. Every record has `neologism: false`.
- No gore. In 0010 and 0030 the dog is eaten, the old walk out into the frost, and in 0013 the mother is laid under
  stones. All of it is said plainly.

### Turns and speakers

- In all 20 dialogues, each turn answers the one before it.
- Each dialogue has exactly two speakers, and the user speaks first.
- The vocatives match the speakers: pótni/wíHre in 0015, pótey/pótni in 0018, pótey in 0003.
- The per-sentence English matches the PIE.

### Verb senses, checked against the full glosses

- Nouns and adverbs:
  - pérwr̥ 'rock; mountain'; moro 'death; plague, pestilence'.
  - wetsós 'yearling, calf'; h₂ewsér 'toward the dawn; at dawn'.
  - moḱs 'quickly; early'; éti 'still, also, too'.
  - úd 'out'; stégos 'roof, house'.
  - h₁éh₁ugʰos 'vow, prayer'; wiHrós 'man; husband; warrior'.
- Verbs:
  - nest 'return home unharmed'; méneti 'stay; wait for'.
  - stéygʰeti 'walk; climb'; bʰwéh₂t 'grow, arise'.
  - h₁r̥h₁pyéti 'seize; carry off'; góleti 'be cold, freeze'.
  - h₁ay- (MID) 'take'.
- Causatives: moréyeti 'kill' and logʰéyeti 'lay' are used in their causative sense, which is right.

### Case

- **Fearing + ablative:** wĺ̥kʷoybʰos bʰebʰóyh₂h₂e (0011), gʰostíbʰos bʰebʰih₂ḗr (0036).
- **Recipient vs goal:**
  - Recipients take the dative:
    - stéh₂dʰh₁oybʰos "sent to the herds" (0012, the first review's fix, still in place).
    - nos "sent to us" (0017).
    - wos "sent to you" (0006).
  - Goals of motion take the accusative: n̥smé gʷegʷóme, póyḱons gʷh₂yéh₁t, wĺ̥kʷons gʷh₂dʰí.

### Pronouns

The gʷṓws tokens are feminine wherever the English says "cows" and masculine for "cattle" (0030), and their
adjectives agree.


The pronouns track their referents:
- h₁íh₂m̥ for dʰéǵʰōm and for dʰoHnéh₂.
- h₁íd for péḱu, stéh₂dʰh₁om and wósr̥.
- n̥ḱéwih₂n̥s for the cows and sheep.
- h₁íh₂ for téḱneh₂ (0040).
- h₁íh₁, the INS.SG in 0005, is Ringe's form.

### Forms

- **Athematic obliques:** pérunsu, kl̥Hn̥sú, kólHonn̥s, bʰr̥h₁wéni, ǵʰiméni, h₂ḱm̥néh₁, gʷr̥h₂unéh₁, kʷspsú,
  h₁h₃sés, sn̥h₁wénbʰos and skuHtéys are all correct.
- **Enclitics:** they stand in second position. The vocative-phrase placement (*séna toy gʷḗn*, *ǵń̥h₃re moy h₂nér*,
  *dyéw nos ph₂ter*) is the engine note the first review already reported.
- **Meter:** all 71 lines are exact.

## Engine notes (report only)

- The enclitic-in-vocative note from the first review still stands.

## Gate after fixes

Re-realized with `realize_plans.py data/generation/plans/t087.jsonl --batch t087 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`. The result is **PASS**:

| | |
|---|---|
| texts realized | 40/40, all exact |
| rejects | 0 |
| meter_exact | 1.00 (71/71) |
| max_lexeme_uses | 6 |
| distinct lexemes | 267 |
| distinct roots | 156 |
| words per record | 30.65 |
| warnings | 13, the same kinds as in the first review; none is an error |

Release rule inputs:
- plant recall is 5/5;
- 0/20 real items are wrong after the fixes;
- the gate is PASS.

Approval is left to the lead.
