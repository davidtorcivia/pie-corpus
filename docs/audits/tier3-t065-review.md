# Tier 3 batch t065 review (review-v1, 2026-10-31)

Batch: 40 in-world two-speaker dialogues about possessions, lending and dividing (`tier3-dialogue-inworld-v1`).
Reviewer: claude-opus-5-5 (calibrated reviewer). Procedure: docs/generation/reviewer-brief.md.

## Procedure
- Re-realized the batch once at the start so the records carry today's two engine fixes ("?" on any clause with
  `question`; check_plan rejects 'two' in an oblique case). Gate PASS, 40/40 exact. That run printed the plan
  warnings (plan ids only); nothing from corpus/ or the plans was read before the verdicts.
- Packet: `make_review_packet.py t065 --n 20 --plants 5 --tier1 3` → 28 items.
- Blind back-translation of 6 items from the `pie` field only (before any English was printed):
  `docs/audits/packets/t065-blind-translations.jsonl`.
- Verdicts saved first: `docs/audits/packets/t065-verdicts.jsonl`,
  sha256 `be1efb48c7a8e4de4e647376be80404c94f3eb25786e3b019dcf8c1ed92b2807`. Then resolve_review_items.py, then score_review.py.
  data/audits/ was never opened.

## Calibration (score_review.py)
| | |
|---|---|
| plant recall | **5/5** (all named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | **0/20** |
| real items minor | 4/20 |

The 5 wrong verdicts were all on plants: 5fbe4d20 (INS.PL usmń̥bʰis for ACC 'three garments'), e9cb63b4 (stégesh₂ PL
for 'the roof'), fef1d68b (an untranslated PIE clause), 35247fe4 (GEN.PL ḱéywōm as the predicate), 1e393fe9 (ACC pótim
as the subject).

Real minors, as scored:
- 19a9794d / t3-t065-00033: réh₁t- for 'find'. **Withdrawn**: lexq gives the gloss "to meet, find".
- b125ab71 / t3-t065-00025: yéh₁ni 'at the harvest'. **Withdrawn**: yóh₁r̥ is glossed "year; growing season or harvest season".
- c872187b / t3-t065-00031: gʰrómos 'thunder'. **Withdrawn**: glossed "a roar, rumble; thunder".
- 393817b0 / t3-t065-00027: in "linékʷti … ne gʷm̥yéti" the dropped subject reads as the giver (the previous
  subject), but the English means the guest. **Fixed** (below).

I flagged the first three from the short gloss in the token line (first sense only). The full lexicon glosses support them.

## Blind back-translation agreement
6 items. The blind readings agree with the English on content for all 6. They differ in a few places:
- 32f5afb1: I read h₁áyoh₂ 'give back?'. The English is 'give'. The lexeme is give (active), so the English is right.
- 8381d486: I took the speaker of "He is swifter, and I bigger" for the other brother. Pro-drop leaves this open; it is not an error.
- b2004ae5: I read h₁émesi as 'I take'. It is SBJV.2SG 'you shall take'. My misreading.
- c872187b: I could not read 'spéh₁istom' ('the fattest', superlative of 'thriving'). It is a stretched sense, but it fits.
- 1e393fe9 (a plant): I could not parse the final clause. This was the planted ACC pótim.
None of the six English texts was seen before the blind file was written.

## Second pass: all 40 records
I read every record sentence by sentence (speaker, per-sentence English, token glosses) against planner-brief-v4
and the in-world dialogue brief (top part).

Nothing modern or coined. 'Wage' (misdʰh₁ós, records 15 and 16) is the inherited word and is paid in livestock, never in coin.
Lending and borrowing are written as "give me … / he did not bring him back to my house / he owes", and the
English says the same. Every "again" is h₂ew, whose lexicon sense is "away from, off; again", and the English says "again" each time.
Verbs of fearing take the ablative (bʰr̥bʰós bʰebʰóyh₂h₂e; gʰrómōd trésont). No 'two' appears in an oblique case.
The causatives (moréyeti 'kill', h₂sowséye 'dry (tr.)', h₁opéyeti 'make reach; give') carry glosses that give the sense used.

### Wrong (1, fixed)
- **t065-0011** (t3-t065-00011): the per-sentence English "You shall receive one, son," left out the clause
  *swésores-kʷe toy h₁wédmn̥ bʰágonti*, so the PIE said more than the English and the next turn ("What is a dowry?")
  answered nothing. **Fix:** English → "You shall receive one, son, and your sisters shall receive a dowry."

### Minor (4, fixed)
- **t065-0001**: "My own ox": *own* has no word in the PIE (no swos). English → "My ox died in the winter."
- **t065-0021**: "Will the fence be strong?" was answered by "Then I shall come at dawn with my sons." and only then by "It
  will stand against the wolves." **Fix:** the two sentences swapped and *nu* dropped. Now: "It will stand against the wolves. I shall
  come at dawn with my sons."
- **t065-0024**: "My spear was the first." was a nominal sentence, but the copula may be left out only in the present. **Fix:** it is now a verbal clause
  with h₁ésti PST: ǵʰoysós moy pr̥h₂wós h₁ést.
- **t065-0027**: as above. **Fix:** SUBJ gʰóstis added: "But the guest goes away, and he does not come again."
  → gʰóstis linékʷti h₂ew-kʷe ne gʷm̥yéti.

### Noted, not changed
- h₁wédmn̥ is glossed 'bride price' but rendered 'dowry' (0011). The English defines it as livestock going with the daughter.
  Daughter usage is split (Homeric ἕδνα is used both ways; OCS věno means dowry), so I left it.
- stégos 'roof' stands for 'house' (0013, 0025), and pérwr̥/péruni 'rock' for 'mountain' (0021, 0034). These are stretched senses with daughter support (Gk στέγος 'house').
- The token gloss line prints only a lexeme's first sense (h₂ew = 'away.from' where the English says 'again'; h₂éwh₂os
  = 'maternal.grandfather' where the English says 'uncle', the lexicon's second sense). This is a display limitation, not
  an error in the text. Engine/export note for the lead: a reviewer working from that line flags false minors, as I did three times above.

## After fixes
Re-realized with `scripts/realize_plans.py data/generation/plans/t065.jsonl --batch t065 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`: 40/40 realized and exact, reject_rate 0.0, max_lexeme_uses 7, 317 lexemes,
174 roots, **gate PASS**. The 7 remaining checker warnings (0012, 0016, 0017×2, 0019, 0023, 0031) were each checked and are false positives.

Real items wrong: 0/20 in the packet before and after. Second pass: 1 wrong and 4 minor, all fixed.
Violations: none. Engine gaps: none found. The only engine/export note is the first-sense-only gloss display.
Release approval was not set.
