# Tier 3 review: t079 (in-world dialogues, youths learning a craft or duty)

Reviewer: calibrated reviewer (review-v1), 2026-10-31. Brief: docs/generation/reviewer-brief.md.
Packet: `make_review_packet.py t079 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).

## Procedure
1. Blind back-translation of 6 items done first, from the `pie` field only:
   `docs/audits/packets/t079-blind-translations.jsonl`.
2. Verdicts were written before corpus/ or the plans were opened:
   `docs/audits/packets/t079-verdicts.jsonl`,
   sha256 `fe25021b0d89b9f6944b6a83d8d6722cec64932ef25c321af56a3117a41020b1`.
3. `resolve_review_items.py t079`, then `score_review.py t079`.
4. Second pass: all 40 records read in full against planner-brief-v4 and the in-world dialogue brief (top part).

## Calibration (score_review.py)
| measure | value |
|---|---|
| plant recall | **4/5 (0.8)**, 4 named |
| Tier 1 judged wrong | 0/3 |
| real wrong (before fixes) | 1/20 (0.05; upper 0.062) |
| real minor (before fixes) | 2/20 |
| real wrong (after fixes) | **0/20** |
| real minor (after fixes) | 0/20 (one withdrawn, one fixed) |

Plants caught (the planted item ids are hidden; the resolver gives no record): an ACC.SG adjective agreeing with a
nominative feminine noun (sénom gʷḗn), a 2du imperative to one addressee (gʷéHyetom), a LOC.PL used for an object
(h₁némn̥su), a GEN.PL used for an object (stéh₂dʰh₁ōm). One plant was missed.

## Blind back-translation
The 6 blind items (dialogues on weaving, the missing lamb, the star over the village, the hearth fire, the foal,
swimming) matched the plan English in every clause, apart from small things: "if" read where the English has
"for/because" (h₁yód, which is the project's idiom for "because"), "grandfathers" read for h₂énHōs, which is a
project word for "grandmothers", and the closing line of the swimming item ("Will you tell the boys?") was not
recovered (mogʰúbʰos was read as an adverb). No item was seen early.

## Packet findings (real items)
- **wrong → fixed** · t3-t079-00036 (017cf2e0) · the bride says ḱéywos wos h₁ésoh₂ "I will be dear to you" twice with
  a masculine predicate. A predicate adjective with a dropped 1sg subject defaults to masculine. Fix: `gender: "f"` on
  the PRED slot (clauses 7, 9), which now gives ḱéyweh₂.
- **minor → fixed** · t3-t079-00025 (d18834e5) · "The fire is a god; he warms the house" realized as one run-on
  sentence, h₁n̥gʷnís deywós dṓm gʷʰr̥néwti ("the god Fire warms the house"). The nominal clause and the verbal
  clause had no `break`. Fix: split them, giving h₁n̥gʷnís deywós. dṓm gʷʰr̥néwti.
- **minor → withdrawn** · t3-t079-00010 (4e278cc6) · tóh₁ (ACC.DU) and then tóybʰos (DAT.PL) for the two oxen. The
  plan has `num: "DU"` on both. The dative dual cannot be reconstructed, so the plural form is the expected engine
  output (planner-brief-v4 rule 17).

## Second pass: all 40 records
None of the remaining dialogues has a modern idea, a coinage, or a turn that fails to answer the previous one. The
written-around words are handled honestly. Hammer and anvil become "strike the bronze on the stone" (00004). The
needle is a bone with a sharp point pushed through the cloth (00021). The bridle is the mane (00003). Dyeing is
peyḱ- "colour, mark with colour" with red flowers boiled in the pot (00006). "Teach me" is ḱeHs- + IMP plus a
how-question (00002, 00007). Every verb of fearing takes the ablative: wĺ̥kʷōd, h₁éḱwoybʰos, gʰrómōd, nékʷts,
h₁ésmōd, tósmōd, bʰr̥bʰós. The craft verbs are used in their real senses: téks- weave, tetḱ- carpentry, sneh₁- spin,
siHw- sew, h₂erh₃- plough, h₂melǵ- milk, demh₂- tame, tinéh₁- melt, térd- bore, topéye- heat. The athematic oblique
forms all check against cells(): ǵʰesrés, ǵʰesréh₁, h₂ḱm̥néh₁, ph₂wéni, nékʷti, kʷsépi, déh₂newi, pr̥kʷéws,
pr̥kʷéwi, ḱunés, gʷéwey, gʷéwōm, h₃rēǵbʰós, dʰh₁sbʰós, kl̥Hn̥sú, h₂str̥sú.

Fixed in the plan (`data/generation/plans/t079.jsonl`):
- **wrong** · 00028: "yoke the two horses to the chariot". A two-horse chariot team is a post-PIE practice
  (Sintashta horizon), not part of the PIE world. Hróth₂os is glossed "chariot, wheeled vehicle", so the English now
  says "cart", and the title is "The Horse Team".
- **wrong** · 00017 and 00023: solh₂wós "all" with `gender: "f"` (for the sheep) came out as masculine solh₂wóns and
  solh₂wṓs (engine gap, below). Fixed as "I saw them in the field" (h₁íh₂n̥s) and "The sheep are here" (h₂óweyes).
- **wrong** · 00016, 00017, 00021, 00030, 00032, 00033, 00039, 00040: a statement and a question with no `break`
  between them came out as one PIE question, so the statement was read as a question. Examples: h₁íd siHwyóm h₁íd
  h₁wésu? ("have I sewn it, is it good?"); h₁íh₂m̥ térdm̥ h₃okʷéh₂ méǵh₂ih₂?. Each is now split into two sentences,
  with the per-sentence English split to match.
- **minor** · 00009, 00014, 00021, 00023, 00028 (two places), 00029, 00034: the same missing `break` between two
  statements (only the punctuation and the sentence alignment are affected). Split.
- **minor** · 00024: solh₂wós "everyone" had `gender: "n"` (now m; the form is unchanged). The answer "We say this"
  used h₂eǵ- AOR where the question has sekʷ- SBJV; it now repeats the question's verb: ḱód sékʷomes "We shall say
  this" (rule 13).
- **minor** · 00021: "For whom will you sew first?" had no slot for "first"; the English is now "For whom will you
  sew?".

Minors left as they are (aspect or sense, meaning intact):
- 00007 ǵʰumé (AOR 1pl) and 00019 h₁áyn̥to (MID AOR 3pl) describe a habitual rite with the aorist (gnomic); 00038
  pl̥h₁tó likewise.
- 00004 dʰinéǵʰmi "I shape (a knife)": dʰeyǵʰ- is properly "knead, form (clay)", a stretch for metalwork, but within
  its gloss "to form, shape".
- 00023 "The lambs are small; they will be afraid of it" is realized as one clause ("the small lambs will fear it").

Gate after the fixes: **PASS** (40/40 realized, reject 0, max lexeme uses 8 ≤ 8, all_exact, distinct lexemes 375).

## Engine, lexicon and brief notes (report only)
1. **solh₂wós has no feminine or neuter.** `pie-lex-solh2wos` has `pos: null`, so its spec is a noun: a slot with
   `gender: "f"` or `"n"` gets the masculine cells under an f/n tag (solh₂wóns ACC.PL/f). The lexq idiom tells
   planners to use it "as its own slot with a gender", which produces this error for any f/n referent. Either give it
   an adjective spec (solh₂wéh₂, solh₂wéh₂ns) or have the checker reject a gender other than m.
2. **Predicate adjective with pro-drop.** With a dropped 1st/2nd-person subject the PRED takes the masculine unless
   the plan sets `gender` on the PRED (t079-0036). A brief line ("a female speaker's predicate adjective needs
   `gender: "f"`"), or a checker warning when the speaker is addressed with a feminine VOC, would prevent it.
3. **No `break` between a statement and a question.** The engine runs two sentences together and the trailing "?"
   turns the statement into a question. 17 instances in this batch. The engine could warn when a sentence-initial
   clause's `english` has more than one sentence but the clauses after it have no `break`.
4. **Role inversion (brief).** In 7 of the 40 dialogues (00003, 00006, 00012, 00016, 00017, 00020, 00032) `model` is
   the child or learner and `user` is the elder who teaches. The in-world brief says `model` is "a man or woman of a
   household" and `user` is the child or young learner. The user-first rule means this cannot be fixed by swapping
   labels. It is left as it is and flagged for the lead: the planner brief could say explicitly that the learner
   speaks as `user`.
5. h₁ógʷʰis GEN.SG has h₁égʷʰis as its primary form, beside h₁égʷʰeys (00031, 00035). h₁égʷʰeys (Ved. -eḥ) would
   read better as the primary form.

Not committed. Release approval not set.
