# Silent-defaults audit: person-less imperatives and gender-less kʷi- slots

Date: 2026-10-28. Scope: every Tier 3 plan file, `data/generation/plans/{b001..b004,t001..t033}.jsonl`. This covers 37 files and 2,310 plans.

Two engine defaults were found today, and this audit checks the approved batches for each:

1. **IMP without `person`.** `clause_controller` falls back to `Agreement(person or 3)`, so a person-less IMP realizes as 3rd person ("let him take"), even when "you" is meant (`tier3-t027-review.md`).
2. **`closed:indefinite_kwi` / `closed:interrogative_kwi` without `gender`.** `_closed_form` picks the m./f. cell, kʷis/kʷís, unless `gender == "n"`. So 'nothing / what' comes out as 'no one / who' (`tier3-t032-review.md`). `closed:interrogative_kwo` was checked too: its fallback is also m.

## Result

**No errors were found in either category, in any batch.** No plan was edited. No batch was re-realized. `corpus/` is unchanged, and no hashes or release approvals moved. There is nothing to re-bind.

| check | slots flagged | errors | batches with flags |
|---|---|---|---|
| IMP with no `person` | 48 | 0 | t003 (6), t006 (1), t007 (2), t015 (21), t023 (18) |
| kʷi-/kʷo- with no `gender` | 60 | 0 | t004 (8), t005 (1), t006 (10), t009 (1), t010 (1), t013 (14), t014 (1), t015 (6), t020 (2), t021 (1), t025 (3), t027 (1), t028 (2), t030 (2), t032 (6), t033 (1, list only) |

### How the slots were found

The scan read `plan.clauses[*].slots[*]`, which covers every slot. A raw-text count of `"mood": "IMP"` (2,628) and of kʷi-/kʷo- ids (667) agrees exactly with the structured walk. Each flagged slot was then judged against the record's whole English text, vocatives in earlier clauses included, and against the realized form. The scan script lives in the session scratchpad (`/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/sd/scan.py`) and is not committed.

### Batches with no flagged slots

These batches have no person-less IMP and no gender-less kʷi-/kʷo- slot:
- b001, b002, b003, b004
- t001, t002, t008, t011, t012, t016, t017, t018, t019, t022, t024, t026, t029, t031

t027 has no person-less IMP slots left, because its review set `person: 2` on all 51.

## 1. Person-less imperatives (48 slots, 0 errors)

Every flagged slot is a genuine 3rd-person command. Either its clause has an overt 3rd-person SUBJ, or the English reads "let him / let it / let the X / let there be". Where "you" appears in the clause (t023-0001, t015-0024, t015-0032), it is the object or the beneficiary, not the person addressed.

| plan · clause | record | form | English | verdict |
|---|---|---|---|---|
| t003-0004 c9 | t3-t003-00004 | h₁opéyetu | let the master give him a gift | ok, SUBJ master |
| t003-0007 c3 | t3-t003-00007 | h₁opéyetu | let the father-in-law give the bride-price again | ok, SUBJ |
| t003-0007 c8 | t3-t003-00007 | dédeh₃tu | let the daughter-in-law give him water | ok, SUBJ |
| t003-0011 c3 | t3-t003-00011 | bʰéretu | let the master of the dog bring wine | ok, SUBJ |
| t003-0011 c7 | t3-t003-00011 | dédeh₃tu | let him give a ram to its master | ok, law-code 3sg |
| t003-0023 c7 | t3-t003-00023 | h₁éstu | Let the house be yours | ok, SUBJ house |
| t006-0040 c3 | t3-t006-00040 | stundéntu (3PL) | let the waters hit him | ok, SUBJ waters PL |
| t007-0005 c7 | t3-t007-00005 | déh₃tu | Whoever is able, let him give | ok, SUBJ só |
| t007-0007 c3 | t3-t007-00007 | wérǵtu | Whoever lives, let him do the work | ok, SUBJ só |
| t015-0006 c5 | t3-t015-00006 | h₁éstu | Let there be a bond between the two houses | ok, SUBJ |
| t015-0006 c7 | t3-t015-00006 | mē Hrunépt | Let no one break the pledge | ok, SUBJ kʷis |
| t015-0020 c9 | t3-t015-00020 | h₁éstu | Let it be this one's | ok, SUBJ h₁íh₂ |
| t015-0020 c10 | t3-t015-00020 | gʷíh₃wetu | and let it live | ok, SUBJ h₁íh₂ |
| t015-0021 c4 | t3-t015-00021 | dédeh₃tu | let him give two dogs | ok, ruling on a stranger |
| t015-0021 c6 | t3-t015-00021 | h₁opéyetu | let him give a dog | ok, ruling on a brother |
| t015-0024 c5 | t3-t015-00024 | dédeh₃tu | Let him give you barley | ok, "you" is the IO |
| t015-0024 c6 | t3-t015-00024 | démetu | and let him build a hedge | ok |
| t015-0025 c2 | t3-t015-00025 | dédeh₃tu | let him give three ploughs | ok, SUBJ só |
| t015-0025 c4 | t3-t015-00025 | bʰéretu | let him bring six carts | ok, SUBJ só |
| t015-0025 c6 | t3-t015-00025 | démetu | let him build five houses | ok, SUBJ só |
| t015-0025 c8 | t3-t015-00025 | déh₃tu | let him give a hundred cattle | ok, SUBJ só |
| t015-0025 c10 | t3-t015-00025 | déh₃utu | let him give a thousand cattle | ok, SUBJ só |
| t015-0026 c4 | t3-t015-00026 | h₁opéyetu | let him give him a boat | ok, SUBJ só |
| t015-0026 c7 | t3-t015-00026 | mē kʷid déh₃ut | let him not give anything | ok; kʷid already `gender: n` |
| t015-0029 c3 | t3-t015-00029 | h₁éstu | Let there be peace for us | ok, SUBJ peace |
| t015-0029 c6 | t3-t015-00029 | lémbʰtu | let death seize him | ok, SUBJ death |
| t015-0030 c6 | t3-t015-00030 | mē moréyet | Let no one kill his own brother | ok, SUBJ kʷis |
| t015-0032 c2 | t3-t015-00032 | ḱéletu | Let the earth cover the slain | ok, SUBJ earth |
| t015-0032 c3 | t3-t015-00032 | h₁éstu | let peace be a shelter for you | ok, SUBJ peace; "you" is the IO |
| t015-0032 c4 | t3-t015-00032 | légʰtu | Let the fight lie down | ok, SUBJ fight |
| t023-0001 c4 | t3-t023-00001 | dʰégʷʰetu | let fire burn you | ok, SUBJ fire; "you" is the OBJ |
| t023-0001 c5 | t3-t023-00001 | h₂sowséyetu | let the sun dry you | ok, SUBJ sun |
| t023-0002 c8 | t3-t023-00002 | stéh₂tu | Let him who lies there stand up | ok, 3rd person (the patient) |
| t023-0002 c9 | t3-t023-00002 | gʷm̥sḱétu | and walk | ok, same subject |
| t023-0004 c2 | t3-t023-00004 | gʷm̥yétu | Let the cold come | ok, SUBJ |
| t023-0004 c3 | t3-t023-00004 | bʰéwgtu | let what is warm flee | ok, SUBJ |
| t023-0004 c4 | t3-t023-00004 | swidyétu | Let him sweat | ok, 3rd person (the patient) |
| t023-0004 c5 | t3-t023-00004 | péh₃tu | let him drink | ok |
| t023-0004 c6 | t3-t023-00004 | térptu | and be satisfied | ok |
| t023-0006 c5 | t3-t023-00006 | h₁éytu | let the suffering go to the wolf | ok, SUBJ |
| t023-0006 c6 | t3-t023-00006 | h₁ḗdtu | Let the wild beast eat it | ok, SUBJ |
| t023-0008 c6 | t3-t023-00008 | léyttu | Now let the snake go away | ok, SUBJ snake (the English is 3rd person here) |
| t023-0010 c3 | t3-t023-00010 | mḗdetu | Let the grease heal the arm | ok, SUBJ |
| t023-0011 c3 | t3-t023-00011 | bʰéretu | Let the water carry the swelling away | ok, SUBJ |
| t023-0011 c4 | t3-t023-00011 | lémbʰtu | Let the cold seize the swelling | ok, SUBJ |
| t023-0011 c5 | t3-t023-00011 | gʷr̥h₃étu | Let the wild beast devour the swelling | ok, SUBJ |
| t023-0011 c6 | t3-t023-00011 | gʷíh₃wetu | Let him live | ok, 3rd person (the patient) |
| t023-0013 c3 | t3-t023-00013 | bʰéwgtu | Let the suffering flee with the darkness | ok, SUBJ |

## 2. Gender-less kʷi- / kʷo- slots (60 slots, 0 errors)

### `interrogative_kwi` and `indefinite_kwi` (47 slots)

All 47 slots stand for a person: "who", "who of you", "someone", "anyone", "no one", or "no sheep / no horse" as an adjectival MOD. So animate kʷís/kʷis is correct for each of them. The "who" items do not need a separate row each:
- **interrogative "who" (36):** t004-0002, 0008, 0015, 0018, 0020, 0022, 0030, 0036; t006-0003 c1, 0016 c0–c3, 0018 c1 and c6, 0033, 0037; t013-0001 c12 and c17, 0002, 0004, 0007, 0010 c3, 0011, 0012 c0 and c1, 0016, 0040.
- **indefinite:**

| plan · clause | record | form | English | verdict |
|---|---|---|---|---|
| t013-0010 c4 | t3-t013-00010 | ne kʷis bʰéh₂ti | No one speaks | ok |
| t013-0013 c4 | t3-t013-00013 | ne kʷis me sékʷetor | no one follows me | ok |
| t013-0017 c1 | t3-t013-00017 | ne kʷosmōd bʰéwgm̥ | I did not flee from anyone | ok |
| t014-0013 c10 | t3-t014-00013 | h₂ówis kʷis ne | No sheep is missing | ok, MOD of f. h₂ówis (m./f. kʷis) |
| t015-0006 c7 | t3-t015-00006 | kʷis mē Hrunépt | Let no one break the pledge | ok |
| t015-0007 c4 | t3-t015-00007 | kʷis … ne déh₃weti | No one will give him fire | ok |
| t015-0013 c7 | t3-t015-00013 | h₁ím-kʷe kʷis ne sepelyét | no one honored him | ok |
| t015-0017 c7 | t3-t015-00017 | kʷis … mē sepelyóyh₁t | may no one honor his name | ok |
| t015-0026 c2 | t3-t015-00026 | h₁yód kʷis | If anyone takes the boat | ok |
| t015-0030 c6 | t3-t015-00030 | kʷis … mē moréyet | Let no one kill his own brother | ok |
| t027-0006 c0 | t3-t027-00006 | h₂nḗr kʷis | A man stole … | ok, 'some man', MOD of h₂nḗr |
| t028-0028 c2 | t3-t028-00028 | h₁éḱwos-kʷe kʷis … ne | no horse draws it | ok, MOD of m. h₁éḱwos |
| t032-0005 c7 | t3-t032-00005 | kʷis … mē n̥ḱyéh₁t | May no one be lost, man and beast | ok |
| t032-0010 c5 | t3-t032-00010 | mē-kʷe kʷis n̥ḱyéh₁t | let no one be lost | ok |
| t032-0017 c0 | t3-t032-00017 | h₁yód kʷesyo h₃ésth₁ | When someone's bone breaks | ok |
| t032-0023 c5 | t3-t032-00023 | h₁yód kʷis | If anyone heals a man | ok |
| t032-0029 c4 | t3-t032-00029 | h₁ím kʷis sléh₂gʷt | Someone has seized him | ok |
| t032-0031 c1 | t3-t032-00031 | kʷis … ne sísdeti | No one sits down in his seat | ok |

Every 'nothing / something / anything / what' in these batches already carries `gender: n` and realizes as kʷid / kʷíd. Examples:
- t013-0001 kʷíd dʰédʰeh₁omes
- t014-0022 ne kʷid kʷḱént
- t015-0026 mē kʷid déh₃ut
- t020-0028 kʷid … mē h₁ést
- t021-0003 kʷid ne tetólh₂e
- t021-0023 kʷid ne dédeh₃ti
- t021-0027 ne kʷid bʰéronti
- t032-0015 and t032-0022, fixed by the t032 review

As a cross-check, every kʷi- slot with an explicit m./f. gender in a text whose English has nothing, something or anything was read: 13 slots. Each one is a 'who' or 'no one' clause, and the 'nothing' of the same text is a separate neuter slot.

### `interrogative_kwo` (13 slots): the default does not apply

Every kʷo- slot is a MOD with a `head`, and it takes its gender from the head noun, not from the m. fallback. Neuter heads come out neuter, so these are not near-misses:

| plan · clause | form | head | English |
|---|---|---|---|
| t005-0030 c0 | kʷóm | deywóm (m) | Which god |
| t006-0016 c8 | kʷósmey | deywṓy (m) | To which god |
| t009-0003 c3 | kʷós | wiHrós (m) | Which man |
| t010-0028 c0 | kʷód | h₁éymn̥ (n) | which road |
| t020-0004 c3 | kʷód | h₁nómn̥ (n) | Which name |
| t020-0010 c2 | kʷód | h₁wédmn̥ (n) | Which bride-price |
| t021-0028 c6 | kʷód | ḱléwos (n) | Which fame |
| t025-0003 c5 | kʷód | wósn̥ (n) | What price |
| t025-0009 c4 | kʷód | h₁wédmn̥ (n) | What bride price |
| t025-0010 c8 | kʷós | poh₂imḗn (m) | Which shepherd? |
| t028-0028 c3 | kʷós | kʷékʷlos (m) | Which wheel |
| t030-0001 c0 | kʷósmōd | ḱóymōd (m) | from which village |
| t030-0005 c0 | kʷóm | h₂éǵrom (m) | To which field |

## t026 and t033: list only, nothing touched

- **t026:** no flagged slots in either check.
- **t033:** `data/generation/plans/t033.jsonl` was read as of this audit. A planner is working on it, so it may change. There are no person-less IMP slots. One indefinite slot has no gender: t033-0036 c9, `wr̥h₁énm̥ kʷis mē stéh₂yoyh₁t`, 'May no one steal the lamb'. Animate is correct there, so this is not an error.

## Gate and corpus confirmation

Nothing was re-realized, so no gate was re-run and no corpus diff exists. Two stronger checks were made instead:
- **Drift check.** Every plan of every batch from b001 to t032 was put through `check_plan` and `realize()` under the current engine (HEAD 2d25584; working-tree `pie/` as of this audit). The resulting `pie` string was compared with the record in `corpus/tier3/<batch>.jsonl`, matched by plan. Results:
  - plan mismatches: 0
  - checker rejects: 0
  - surface drift: 0 records, in all 36 batches (2,270 records)

  So every approved record still matches its plan under today's engine.
- **Recorded gates** (`data/generation/batches/<b>.json`). Every batch shows PASS except two. Both failures are pre-existing, and neither batch's release is approved:
  - **t022: FAIL.** `max_lexeme_uses` is 18, over the cap of 8. Release `pending`: "redo open".
  - **t025: FAIL.** `max_lexeme_uses` is 25, over the cap of 9, and the theme-core cap also fails. Release `pending`: "Awaiting review". A reviewer of t025 should know about this.

## Related observations (outside the two named defaults, not fixed)

- **The same fallback applies to every mood.** `Agreement(person or 3)` also covers IND, SBJV and OPT. So "Sky, you are great" with no `person` would come out as h₁ésti 'he is'. A narrow scan looked for verbs with no `person` in a clause that has a VOC and no SUBJ, and found 6. All 6 are correct 3rd person:
  - t005-0007 c6, 'He set you on your course, Dawn'
  - t018-0030 c4 and t018-0031 c6, '… cried out, "Mother!"' (a quoted vocative)
  - t021-0002 c2, 'Dear one, it is gone below'
  - t023-0013 c5, 'Dawn, let him see you'
  - t029-0032 c5, 'Father Sky, may it rain'

  A broader pass was not made: one would cover non-IMP verbs whose vocative is in an earlier clause. The engine-side fix (require `person` on verbs in addressed clauses, or infer 2nd person from a VOC) would cover this class too.
- **Provenance gap.** t024–t032 records carry `generator.engine_version: "unknown"`. This was the case before the audit.
