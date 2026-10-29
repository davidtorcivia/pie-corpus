# Meter repair: b002

Date: 2026-10-28. Re-realized with the batch's own model and prompt id: `claude-sonnet-5-5`, `tier3-planner-v3`. `data/generation/batches/b002.json` does not record these, so they were taken from the stored records' `generator` fields. The engine version is `24689ea`; the stored records had `3329964`.

## Result

| | lines | exact | meter_exact | gate |
|---|---|---|---|---|
| before (stored records, current syllabifier; census) | 32 | 6 | 0.188 | would FAIL |
| after | 30 | 29 | **0.967** | **PASS** (every gate) |

The line count fell by 2 because two two-sentence praise texts (0224, 0246) were merged into one line each. The other batch numbers are unchanged:
- max lexeme uses 6 (cap 6);
- 185 distinct lexemes, 136 roots;
- 0 rejects, all exact;
- dup_across_batches 1, as before;
- 32 warnings, as before;
- formula_uses 0, as before.

**Diff check.** `corpus/tier3/b002.jsonl` was compared before and after, record by record:
- exactly the 23 records listed below changed `pie`, `english` or plan;
- no other record changed its PIE or English;
- every record's `generator.engine_version` changed from `3329964` to `24689ea`, and its `meter` field was recomputed.

## Changed lines (23 plans)

Syllable counts are per verse line (sentence), before → after. The English was updated for every edit:
- nu is rendered "now";
- a dropped -kʷe becomes "; ";
- a merge joins the two English sentences;
- a dropped vocative is removed from the English.

| plan | genre | old PIE / English | syl | new PIE / English | syl | edit |
|---|---|---|---|---|---|---|
| b002-0221 | praise | ḱludʰí nos h₃rḗǵni h₂lékse-kʷe nos.<br>O queen, hear us, and protect us! | 9 | ḱludʰí nos h₃rḗǵni h₂lékse nos.<br>O queen, hear us; protect us! | 8 | drop -kʷe |
| b002-0223 | praise | pótey h₂r̥ǵrós h₁ési dédeh₃si-kʷe nos sh₁esóm.<br>O master, you are shining, and you give us the harvest. | 13 | h₂r̥ǵrós h₁ési dédeh₃si-kʷe nos sh₁esóm.<br>You are shining, and you give us the harvest. | 11 | drop vocative potis |
| b002-0224 | praise | stéwtor séngʷʰe. ḱléwsōmes.<br>O praiser, recite! We shall listen. | 4/3 | stéwtor séngʷʰe ḱléwsōmes-kʷe.<br>O praiser, recite, and we shall listen. | 8 | merge; add -kʷe |
| b002-0225 | praise | dʰugʰyéh₁t h₂éǵros gʷunuyéh₁t-kʷe h₂éǵmn̥.<br>May the field be productive, and may the flock grow. | 10 | nu dʰugʰyéh₁t h₂éǵros gʷunuyéh₁t-kʷe h₂éǵmn̥.<br>Now may the field be productive, and may the flock grow. | 11 | add nu (c0) |
| b002-0228 | praise | séngʷʰomes toy ḱléwsesi-kʷe nos.<br>We recite for you, and you listen to us. | 9 | séngʷʰomes toy ḱléwsesi nos.<br>We recite for you; you listen to us. | 8 | drop -kʷe |
| b002-0229 | praise | dʰéwgʰsi h₂r̥ǵrós-kʷe h₁ési.<br>You are productive, and you are shining. | 7 | nu dʰéwgʰsi h₂r̥ǵrós-kʷe h₁ési.<br>Now you are productive, and you are shining. | 8 | add nu (c0) |
| b002-0230 | praise | péh₂wr̥ ǵʰléyde gʷʰr̥nudʰí-kʷe nos.<br>Shine, O fire, and warm us! | 9 | péh₂wr̥ ǵʰléyde gʷʰr̥nudʰí nos.<br>Shine, O fire; warm us! | 8 | drop -kʷe |
| b002-0231 | praise | mē nos moréyoyh₁t gʷʰéros.<br>May the heat not kill us! | 7 | nu nos mē moréyoyh₁t gʷʰéros.<br>Now may the heat not kill us! | 8 | add nu (c0) |
| b002-0232 | praise | h₂léksoyh₁t nos dʰwṓr ph₂syéh₁t-kʷe nos h₁n̥gʷnís.<br>May the door protect us, and may the fire guard us. | 10 | nu nos h₂léksoyh₁t dʰwṓr ph₂syéh₁t-kʷe nos h₁n̥gʷnís.<br>Now may the door protect us, and may the fire guard us. | 11 | add nu (c0) |
| b002-0233 | praise | dedórḱth₂e nos ǵn̥néh₃si-kʷe nos.<br>You see us, and you recognize us. | 9 | dedórḱth₂e nos ǵn̥néh₃si nos.<br>You see us; you recognize us. | 8 | drop -kʷe |
| b002-0234 | praise | pótey gʷm̥yé sddʰí-kʷe.<br>Come, O master, and sit down! | 6 | nu pótey gʷm̥yé nu-kʷe sddʰí.<br>Now come, O master, and now sit down! | 8 | add nu (c0); add nu (c1) |
| b002-0235 | praise | stéwtor sth₂dʰí séngʷʰe-kʷe.<br>Stand up, O praiser, and recite! | 7 | nu stéwtor sth₂dʰí séngʷʰe-kʷe.<br>Now stand up, O praiser, and recite! | 8 | add nu (c0) |
| b002-0236 | praise | h₃rḗǵnih₂ ǵʰléydeti dedr̥ḱmé-kʷe tā́m.<br>The queen shines, and we see her. | 10 | nu h₃rḗǵnih₂ ǵʰléydeti dedr̥ḱmé-kʷe tā́m.<br>Now the queen shines, and we see her. | 11 | add nu (c0) |
| b002-0237 | praise | ǵʰléydesi h₁rudʰéh₁si-kʷe.<br>You shine, and you are red. | 7 | nu ǵʰléydesi h₁rudʰéh₁si-kʷe.<br>Now you shine, and you are red. | 8 | add nu (c0) |
| b002-0238 | praise | h₂ówis moysós-kʷe tetr̥pih₁tā́m.<br>May the sheep and the ram be satisfied. | 9 | nu h₂óweyes moysós-kʷe tetr̥pih₁ént.<br>Now may the sheep and the ram be satisfied. | 11 | add nu (c0); number h2owis SG→PL |
| b002-0239 | praise | h₁éh₁ugʰos toy dedh₃més ḱl̥néwsi-kʷe tód.<br>We give you a vow, and you listen to it. | 12 | h₁éh₁ugʰos toy dedh₃més ḱl̥néwsi tód.<br>We give you a vow; you listen to it. | 11 | drop -kʷe |
| b002-0240 | praise | memn̥mé te ǵn̥nh₃més-kʷe te.<br>We are mindful of you, and we recognize you. | 9 | memn̥mé te ǵn̥nh₃més te.<br>We are mindful of you; we recognize you. | 8 | drop -kʷe |
| b002-0241 | praise | wérh₁yōmes dédeh₃omes-kʷe.<br>Let us speak, and let us give. | 9 | wérh₁yōmes dédeh₃omes.<br>Let us speak; let us give. | 8 | drop -kʷe |
| b002-0242 | praise | dedr̥ḱih₁mé te ḱluyéh₁s-kʷe nos.<br>May we see you, and may you hear us. | 9 | dedr̥ḱih₁mé te ḱluyéh₁s nos.<br>May we see you; may you hear us. | 8 | drop -kʷe |
| b002-0244 | praise | wóydth₂e dedórḱth₂e-kʷe.<br>You know, and you see. | 6 | nu wóydth₂e nu-kʷe dedórḱth₂e.<br>Now you know, and now you see. | 8 | add nu (c0); add nu (c1) |
| b002-0246 | praise | ḱludʰí nos. h₁r̥sḱé nos.<br>Hear us! Come to us! | 3/3 | nu nos ḱludʰí h₁r̥sḱé-kʷe nos.<br>Now hear us, and come to us! | 8 | merge; add -kʷe; add nu (c0) |
| b002-0247 | praise | tetr̥pih₁mé mē-kʷe gʷl̥dʰyóyh₁me.<br>May we be satisfied, and may we not be hungry. | 9 | tetr̥pih₁mé mē gʷl̥dʰyóyh₁me.<br>May we be satisfied; may we not be hungry. | 8 | drop -kʷe |
| b002-0248 | praise | tl̥néh₂si nos bʰéresi-kʷe nos.<br>You lift us up, and you carry us. | 9 | tl̥néh₂si nos bʰéresi nos.<br>You lift us up; you carry us. | 8 | drop -kʷe |

Notes:
- **b002-0223:** the only exact edit drops the vocative "O master". The English drops it too.
- **b002-0238:** "sheep" (h₂ówis) is now plural (h₂óweyes, with a plural verb). This is the only edit to land the line: one particle gives 10 syllables, and the plural adds the 11th. English "sheep" reads as both singular and plural, so the English stays the same apart from "Now".
- **nu on a second clause:** b002-0234 and b002-0244 have nu on both clauses (the second written nu-kʷe, as elsewhere in the corpus: t002, t020). The English reads "and now".

## Not fixed (1 line)

- **b002-0250** "h₂r̥ǵróm dedr̥ḱih₁mé" ("May we see the shining one!"), 6 syllables, target 8.
  - A particle gives 7.
  - The only epithet that reaches 8 or 11 is pie-lex-megjyoxs "greater". It is already at the lexeme cap (6), and it does not suit the line.
  - The clause has a 1pl optative verb, so it cannot take a vocative.
  - Left as it is.
