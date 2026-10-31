# Tier 3 batch t064 review (review-v1, 2026-10-31)

Batch: 40 in-world two-speaker dialogues about daily household work (milking, grinding, weaving, fetching water,
mending, the evening fire). Prompt `tier3-dialogue-inworld-v1`, model `claude-opus-5-5`.
Reviewer: calibrated reviewer (Claude Opus 5.5), following docs/generation/reviewer-brief.md.

## Procedure

1. Re-realized once at the start so the records carry today's two engine fixes (a "?" when any clause of a sentence
   has `question`; check_plan rejects 'two' in an oblique case). Gate PASS, 40/40 exact.
2. Packet: `make_review_packet.py t064 --n 20 --plants 5 --tier1 3`. That gave 28 items: 20 real, 5 planted, 3 Tier 1.
3. Blind back-translation of 6 items from the `pie` field only: `docs/audits/packets/t064-blind-translations.jsonl`.
4. Verdicts saved before opening corpus/ or plans: `docs/audits/packets/t064-verdicts.jsonl`,
   sha256 `dd2ce6d97a43789194eeb09d43d27387ed2e2acace048f7f1299fb3607fdc7df`.
5. `resolve_review_items.py t064`, then `score_review.py t064`.
6. Second pass: all 40 records read in full against planner-brief-v4 and the top part of
   planner-brief-dialogue-inworld (not the Humor or Horrors sections).

## Calibration

| | |
|---|---|
| Plant recall | **5/5** (all 5 caught and named) |
| Tier 1 judged wrong | 0/3 |
| Real items wrong | **0/20** |
| Real items minor | 1/20 |

Plants caught:
- `6ec64f8b`: IMP.3PL ḱl̥nwéntu for a 2SG "listen".
- `bbea0356`: SBJV.1PL h₁épomes with a 3SG bear as subject.
- `aaf362b4`: DAT/LOC.SG h₁n̥gʷléy used as the subject "embers".
- `36053ead`: NOM ḱwṓ after ḱóm, which needs the instrumental.
- `c9a9825f`: LOC.PL swópniyoysu against "a dream" (flagged minor).

## Blind back-translation agreement

All 6 items (f24a6aee, c9a9825f, f66d0074, 5bd2f6de, dd4ee9c4, 7d9b8db6) agree with their English in substance.
The differences were vocabulary I could not place without the lexicon:
- h₁ólom 'awl';
- Hrésgtis 'weaving' and h₁uséwih₂ 'good';
- péh₂uros 'the little one';
- stéh₂dʰh₁om 'herd';
- h₁opéye 'hand (me)'.

Two places where I read a different grammatical sense:
- I first took h₂wĺ̥h₁neh₂m ǵʰóstoy h₁áyso as "give the wool to the guest", but the word is ǵʰ- 'hand', not gʰ- 'guest'.
- I took somHós as "weak".

## Packet findings

**Wrong (real items):** none.

**Minor:**
- `7d9b8db6` (t3-t064-00012): somHós for "alone". When I checked afterwards, the lexicon gloss is
  "same, alike; alone", so the sense is attested in the lexicon. No fix was made.
- `904831b8` (Tier 1, Byrd 2013 King and God): ǵn̥h₁yetōd where the version I remember has ǵn̥h₁yetu. Both are
  3SG imperatives. This is a Tier 1 source question, not a t064 one.

`f1b168a3`: wédʰe "bind" was checked and is correct. It is the homograph pie-lex-wedheti-2 'to bind, join'.

## Second pass (all 40 records)

All 40 have exactly two speakers, the user first, and both speakers belong to the PIE world: kin, herders,
in-laws, a smith mentioned in passing. I found:
- no modern or coined content;
- no tool or practice outside that world (skin churn, quern, loom with warp threads, ard, wheel and wagon,
  net fishing, smoking and salting meat);
- no turn that fails to answer the one before it.

These checks all passed:
- Verbs of fearing take the ablative: wĺ̥kʷōd, nékʷts, ph₂wéns, méd, h₁ésmōd.
- Duals are used for oxen, arms, feet, eyes and the ewe with her lamb, with plural forms in the oblique cases.
- Athematic obliques are correct: h₂ḱméni and h₂ḱm̥néh₁, h₂l̥h₁wénh₁, wédn̥h₁, bʰr̥h₁wéni, mémsh₁, sh₂léh₁, déms,
  ph₂wéns, ḱunéh₁ ḱóm.
- Enclitics sit in second position.
- Pronouns track their referents, including the gender of h₁íd, h₁íh₂m̥ and h₁íns.
- Craft verbs are used in their real sense: mélh₂- and gʰrendʰ- grind, teḱs- weaves, siHw- sews, h₂eydʰ- kindles,
  der- flays (gloss "tearing, skinning, flaying"), kh₂eyd- cuts.
- Questions end in "?".

Some glosses looked doubtful but are in the lexicon:
- h₂éwh₂os 'maternal grandfather / maternal uncle';
- népōts 'grandson / nephew';
- h₂éḱos 'ear of grain';
- pekʷ- 'to ripen';
- médʰu 'mead';
- kʷékʷlos 'wagon';
- dweh₂rós 'far away';
- dért 'to tear (intrans.)'.

Fixed at the source in data/generation/plans/t064.jsonl:
1. **t064-0028, clause 11**: the father called his daughter "a giver of good things" (déh₃tōr + h₁wésus GEN.PL).
   déh₃tōr is a masculine agent noun used of a woman, which brief rule 18b forbids. The line is now "You are dear to
   me" = túH moy ḱéyweh₂, a nominal clause with a feminine subject. This is the in-world brief's own thanks option
   (ḱéywos). As a side effect `formula_uses` drops from 2 to 1. The brief says not to force formulas into dialogues.
2. **Causative-shaped -éye- verbs standing in for plain verbs**, where the lexicon glosses them as the plain verb.
   A causative used for a plain verb was a past error. All three were moved to the plain verb:
   - t064-0006, clause 11, "bind them with the rope": bʰondʰéye (pie-lex-bhondheyeti) → bʰéndʰe
     (pie-lex-bhendheti), as in t064-0014.
   - t064-0008, clause 8, "lead the oxen to the stall": wodʰéye (pie-lex-wodheyeti) → dukdʰí (pie-lex-dewkti,
     'to pull, to draw; to lead'). wedʰ- is at the cap of 7, so it could not take this use.
   - t064-0016, clause 5, "tell me": sokʷéye (pie-lex-sokweyeti) → skʷdʰí (pie-lex-sekwt-3, AOR IMP), as in
     t064-0034.

   These verbs keep their causative sense and stay as they are: h₁opéye 'make reach, hand', moréye- 'kill',
   logʰéye 'lay', h₂sowséye- 'dry (tr.)'. No word went over the cap. The lead may want to review the o-grade -éye-
   entries glossed as plain verbs (bhondheyeti, wodheyeti, sokweyeti) centrally.

Counted as acceptable, not fixed:
- The present tense stands for the future in places, e.g. kénkonti for "they will be hungry", which is normal PIE
  usage.
- h₁áyto (MID.AOR) and h₁nédʰt (AOR) are gnomic aorists. h₁nédʰt has only aorist forms.

## Counts before and after the fixes

| | before | after |
|---|---|---|
| Packet real wrong | 0/20 | 0/20 |
| Packet real minor | 1/20 | 1/20 (the gloss supports it; no fix) |
| Second pass, brief violations | 4 (0028 rule 18b; causatives in 0006, 0008, 0016) | 0 |

## Gate

The final realize gives:
- 40/40 realized, all exact;
- reject_rate 0.0;
- max_lexeme_uses 7, at the cap;
- 352 distinct lexemes, 198 roots;
- gate **PASS**.

## Engine and lexicon notes (report only)

- **wéwket / wéwke** ('say'): the cells drop the labial of the spec stem wéwkʷe. This is the engine's deliberate
  boukólos delabialization next to *u* (pie/phon.py `boukolos`), and many handbooks write *wé-wk-e-t. It is not a
  defect. The only note is that Greek εἶπε keeps the labial.
- **ḱlḗm** (AOR.1SG of pie-lex-kjlewt 'hear', where one would expect ḱléwm̥): a question for the engine owners.
  Is applying a Stang's-law-type -ewm̥ → -ēm to a verb intended? The form is also a homograph of AOR.1SG of
  pie-lex-kjleyt-2 'to lean'.
- **The h₂éǵ- 'drive' / h₂eǵ- 'say' homograph warnings** (0009, 0020, 0030) were checked, and every use means
  'drive'.

Release approval is left to the lead.
