# Tier 3b batch t3b-006 review (stories, songs, gods and feelings)

Reviewer: calibrated, `review-v1` brief, adapted to Tier 3b as in t3b-002. The second pass also checked planner-brief-3b v3 (§5 character, archaic-first, English-to-PIE match, turn coherence).

## Procedure

1. **Packet.** `make_review_packet.py t3b-006 --tier tier3b --n 20 --plants 5 --tier1 3` gave 28 items: 20 real, 5 planted and 3 Tier 1. I never read anything under `data/audits/`.
2. **Blind back-translation.** I translated 6 items from `pie` alone, before I saw any English: `docs/audits/packets/t3b-006-blind-translations.jsonl`.
   - The PIE of all 28 items was printed together in one listing, with no English.
   - In 5 of the 6 the sense agrees with the plan English: df19f712, 6fc90b1f, 376aa324, 87e05701 and e28db3f3.
   - In 1ca80624 I read gʷéHyeti blind as 'lives' (from gʷeyH-). The lexicon has it under geH- 'sing' (Lith. *giedóti*), so the plan's "sings" is right. This was my error, not the batch's.
   - One plant surfaced in the blind pass itself: e28db3f3, wĺ̥kʷōys (INS.PL) with a 3SG verb.
3. **Verdicts.** I judged all 28 items before opening `corpus/tier3b/` or the plans: `docs/audits/packets/t3b-006-verdicts.jsonl`, sha256 `c5a72fa3e04131bf423c364a15f3d62b156f345804259cd3d8c6fe9db64c6352`. Then I ran `resolve_review_items.py`, then `score_review.py`.
4. **Second pass.** I read all 40 records in full, sentence by sentence: speaker, PIE, per-sentence English and gloss.
   - The planted items correspond to records 0011, 0014, 0022, 0035 and 0039. I read them in their real form in this pass.

## 1. Counts

| | before fixes | after fixes |
|---|---|---|
| Plant recall | **5/5** | |
| Tier 1 items judged wrong | 0/3 | |
| Real packet items wrong | 0/20 | 0/20 |
| Real packet items minor | 1/20 | 1/20 |
| Second pass, all 40 records: wrong | 0 | 0 |
| Second pass, all 40 records: minor | 3 | 2 (one fixed) |
| §5 character violations | **0** | 0 |
| Gate | PASS | **PASS** (40/40 realized, 0 rejected, coined sentences 9/209 = 4.3%, neologism tokens 1.3%) |

Record 0033 is a real packet item (51dfc71f) that I judged ok on grammar. Its archaic-first problem turned up only in the second pass, so it is counted there and not in the packet's minor count.

The trial re-realization in §6 left no stale reject: `data/generation/rejects/t3b-006.jsonl` is empty after the final run.

**Plant recall: 5/5.**
- The scorer reports `plants_named: 0` because it matches the replacement form as an exact Unicode string, and I wrote the forms in ASCII (h1eymi, sokweyesi, deywoybhos, suHh1e, wl_kwoys).
- Each issue still names the wrong form, the feature it carries, and the right one:
  - 80d30ab5: h₁éymi, 1SG for 3SG h₁éyti.
  - 21bebe3f: sokʷéyesi, 2SG for 3SG sokʷéyeti.
  - 8ff4bb70: deywóybʰos, DAT.PL subject for NOM.PL deywṓs.
  - 934db83b: súHh₁e, NOM.DU for NOM.SG súHs.
  - e28db3f3: wĺ̥kʷōys, INS.PL for NOM.SG wĺ̥kʷos.
- All five match the real records (0011, 0035, 0014, 0039, 0022), which were realized correctly.

## 2. Wrong items

None among the 20 real packet items, and none in the 40-record second pass.

## 3. Minor items

1. **0004 (b49ea4b9 in the packet): wórmos for "ant". Not fixed.**
   - wórmos is 'worm, insect larva'. The root werm- also covers "ant or other small insect" (Lith. *var̃mas* 'insect, gnat'), so the sense is stretched but defensible.
   - The proper word is morwís 'ant' (Gk μύρμηξ, OIr. *moirb*, ON *maurr*). It is not in the slice, and when I tried it the engine rejected it: `pie-lex-morwis has no usable spec (rule shape:hk-iu-stem)`.
   - I reverted the plan to wórmos. This is an engine gap (§5 below).
2. **0033: archaic-first. Fixed.**
   - "Who was your teacher?" used the noun coinage dóḱtōr `pie-neo-dokjtoxr`. The verb already in the slice says the same thing.
   - New first clause: "Who taught you?", kʷís te doḱéyet? (SUBJ interrogative_kwi m, OBJ personal/2 enclitic, V pie-neo-teach PST).
   - This drops one coined lexeme from the batch (5 to 4 neologism lexemes). The model's answer, "Mother taught me songs.", now repeats the question's verb, as rule 13 expects.
3. **0035: préḱsdʰi. Not a plan fault.** The engine builds this IMP.2SG of the s-aorist prḗḱst with -dʰi on the s-stem. Imperatives of this shape are hardly attested; a reflex-backed form would be the present imperative pr̥sḱé. Reported only.

Checked and **ok**:
- h₁éy, anaphoric NOM.SG.M after Ringe, in the verbless "he is a great god" (0005).
- dwóyh₁ h₂ówih₁, fem. dual (0029).
- h₁áyto, LIV *h₁ai̯-* MID 'received' (0002).
- h₁ddʰí 'eat!' (0030).
- ḱl̥nudʰí (0031).
- h₂roh₁dʰéye 'speak' (Goth. *rōdjan*) (0004).
- wiHrṓs and deywṓs as NOM.PL in -ōs, which is the engine's thematic nominative plural (0019, 0014).

## 4. Second pass: character, coherence, archaic-first

- **§5 character: no violations.**
  - In every dialogue the model is a human speaker with a household: a brother and sons by the evening fire (0007), a sister who sings to the sheep (0009, 0033), and a mother who teaches songs and explains the sun (0010, 0011, 0033).
  - Also: a father who died last year and is seen in a dream (0024); a newborn son (0026); cattle and sheep under the gods' protection (0017); a lost cow (0019); a dog (0040); a name his father gave him (0020).
  - No line makes the model a machine or a made mind, or says it has no body, home or parents.
- **Turn coherence.** Every turn answers the one before. The "How do I say …?" items (0025, 0027) follow the brief: the user's sentence comes back as the model's own turn, plus one more line.
- **English matches the PIE** in all 40 records. The only exception is the small "And …" in 0010 and 0035, which has no slot: trivial.
- **Archaic first.**
  - 9 of 209 sentences contain a coinage. These are kéh₂ntōr 'singer', doḱéyeti 'teach', gʷŕ̥Hte 'welcome' and sméymn̥ 'joke', all brief-sanctioned.
  - The everyday concepts use the inherited words from the brief's table: dn̥ǵʰwéh₂s, wékʷos, memóne, h₁éwkm̥, mówdos, bʰoydʰéh₂, priHós/ḱéywos/gʰóstis.

## 5. Engine gaps (report only)

1. **pie-lex-morwis 'ant' has no usable inflection spec** (`shape:hk-iu-stem`). The inherited word for "ant" can't be realized, so planners fall back on wórmos.
2. **s-aorist IMP.2SG préḱsdʰi** (prḗḱst): the form is doubtful. Consider restricting that imperative cell for s-aorists, or routing it to the present imperative.
3. **The scorer's `plants_named` uses exact Unicode substring matching**, so a reviewer who writes ASCII forms scores 0 even when every plant is named. Consider matching `pie_ascii` too.

## 6. Fixes applied

- `data/generation/plans/t3b-006.jsonl`, plan t3b-006-0033, clause 0: "Who was your teacher?" became "Who taught you?" The plan-level English was updated to match.
- Re-realized with `scripts/realize_plans.py data/generation/plans/t3b-006.jsonl --batch t3b-006 --tier3b --model claude-opus-5-5 --prompt-id tier3b-planner-v3`.
  - Result: 40/40 realized, 0 rejected, gate PASS.
  - coined_sentences 9/209 (0.043); neologism_tokens 9 (0.013) from 4 lexemes; max_lexeme_uses 6.
- The trial swap to morwís in plan 0004 (one run, plan rejected) was reverted. Plan 0004 is byte-identical to the original.

Release approval is left to the lead. Against the release rule: plant recall is 5/5 (needs ≥ 4/5), 0/20 real items are wrong (needs ≤ 2/20), and the gate is PASS.
