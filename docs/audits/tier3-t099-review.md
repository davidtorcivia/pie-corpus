# Tier 3 batch t099 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on the house and settlement (timber, posts, wattle and daub, roof and
hearth, a son building beside his father, neighbours helping, loading wagons, a new place by a river, the fence
against wolves), `tier3-dialogue-inworld-v1`. Reviewer: calibrated agent review following
docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t099 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items from the `pie` field only, before any English was printed:
   `docs/audits/packets/t099-blind-translations.jsonl`.
3. Every packet word was checked against `Lexicon.cells()` and the closed class (a reverse form index), then the
   verdicts were written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t099-verdicts.jsonl`, sha256
   `f60b0e33da74aabfea9873510585afb0b90ce6fe1447c9d45279e322080ac701`.
4. `resolve_review_items.py t099`, then `score_review.py t099`.
5. Second pass: all 40 records and plans read in full against planner-brief-v4 and the in-world dialogue brief.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor (as scored) | 1/20 (withdrawn below: 0/20) |

Plants caught (packet spelling):
- dweh₂róybʰos: DAT/ABL.PL for the predicate NOM.SG n. "Is the spring far?" (the answer has dweh₂róm);
- h₁éyesi: SBJV.2SG for "Where will we go?" (1PL);
- dʰh₁mé: AOR.1PL for "I have laid a bed for you" (1SG);
- h₁usuyéh₂bʰos: DAT/ABL.PL f. for ACC.SG n. "a good place" (h₁wésu stéh₂nom);
- h₁r̥sḱétom: IMP.2DU for "Go to the high door", said to one guest (IMP.2SG).

**Withdrawn minor.** f9788eb2 (t3-t099-00031): I marked "he hears the wolves well" as having no word for "well".
The full gloss of h₂ḱh₂owsyéti is "to be sharp-eared, to hear well", so the verb carries it. The record is correct.
**Real wrong: 0/20 before and after the fixes; real minor: 0/20.**

## Blind back-translation agreement

All six were translated before any English was seen. Agreement was substantive on all six; divergences were single
words, none pointing to an error in the PIE:

| item | divergence |
|---|---|
| 2f12c039 | spérs taken as "spared" ("you have saved", spért 'free, rescue'); téḱneh₂ read as "daughter", not "children" |
| 87180b8d | gólesi read as "do you complain?" (góleti 'be cold'); kʷért "broke" for "made" |
| 29c01c4e | none of substance ("withies" for "twigs") |
| 6378c8a9 | h₂éyeri "early" for "tomorrow" (the lexq idiom) |
| 2365731f | h₂éwh₂e read as "already" (it is VOC "uncle"); gʷr̥déwih₂es "pregnant" for "slow" |
| e7f47f54 | none |

## Second pass (all 40 records)

No modern or coined content; every dialogue has two in-world speakers, the user first, a new speaker on a new
sentence, per-sentence English on every sentence-initial clause, the joined English equal to the plan English, and
4–14 clauses in 2–8 turns (checked by script over all 40 plans). Turns answer each other; the one loose spot,
t3-t099-00028 where the model asks the rhetorical "Is the door not strong?" after proposing to carry it away, reads
as a justification and stands.

Checks asked for by the lead:
- **Deictic WARNs.** All three are fine. "I know that" (0007) and "Why do you do that?" (0027) point back to the
  previous turn (tód); "Where did you learn this?" (0021) is ḱód for the skill just shown.
- **Substitutes, read against the full glosses.** Beam → dóru 'tree; wood, timber' ("timbers", 0026); axe →
  ḱéstrom 'knife, cutting tool; blade', and the English says "blade" (0001, 0002); clay → dʰéǵʰōm 'earth, soil'
  ("earth and water", 0004); thatch → gʰréh₁mn̥ 'grass' (0020) and lowbʰós 'bark' (0021, 0038); ladder → upó +
  stéygʰeti 'climb up' (0005, 0030); camp → wóyḱos 'settlement' (0018) and stéh₂nom 'place'. Each English says what
  the substitute means. Others checked: wénh₁t-2 'set, place' for "set the door/post"; wédʰeti-2 'bind' (0020) beside
  wédʰeti 'lead' (0017); h₂epó + Hwért "open" is the lexq idiom; h₂ewsér 'in the direction of dawn' for "toward the
  dawn"; kʷékʷlos 'wheel; circle'; h₁opéyeti 'make reach; give' for "hand up".
- **Fearing** takes the ablative everywhere: h₂eḱróybʰos steh₂uróybʰos bʰebʰóyh₂e (0012), wĺ̥kʷoybʰos trésoh₂ (0022),
  ḱwn̥bʰós mē tréses (0039).
- **Formulas.** "May the gods give you good things" (0039) is built as v4 says. "I praise you" is the thanks idiom
  (0008, 0029, 0039). 0008 had "you are a good giver" (h₁wésus as MOD of déh₃tōr): fixed to the formula
  "giver of good things", POSS n. PL → túH h₁uséwōm déh₃tōr (Ved. dātā́ vásūnām), with the English to match.
- **Cows** are female wherever the English says cows: kʷétesres gʷówes, gʷówes gʷr̥déwih₂es, h₁íh₂es ish₁réh₂es
  (0033); "cattle" stays unmarked; bulls are uksḗn.
- **h₂élyos** is an adjective with a gender: h₂élyōd ḱóymōd (m), h₂élyom h₂éḱsim (m), h₂élyod dʰéh₁mn̥ (n).
- **Predicate adjectives with dropped subjects** agree with the referent: túH luǵréh₂ / ǵn̥h₃réh₂ / dʰr̥séwih₂ to women,
  h₁eǵóh₂ luǵrós (old man), h₂yuHn̥ḱós h₁ésm̥ (uncle), h₁íh₂es h₃reǵtéh₂es (posts, f.).
- **Short answers** take the case asked for: ACC "Grass and a rope", "To a new place", "Ten loads", "Seven
  wagons", "Toward the great river"; INS "With stakes and branches"; LOC "At the ford"; NOM "Ten bulls and four
  cows" (the subject of "how many will pull them?").
- **Athematic obliques** are the engine's: dʰuréy, dʰwóri, pr̥wéni, wédni, ph₂wéni, dʰh₁méns/dʰh₁méni, kl̥Héni,
  h₂ḱméni, h₂Hséh₂i, sḱénh₁, gʰr̥h₁ménh₁, drúsu, pr̥kʷéws, déh₂nus (ABL). No error found.
- **Enclitics** stand in second position (moy/toy/nos/te/me), with -kʷe on the first word of its clause or on the
  last conjunct (mē-kʷe péds, nu-kʷe kénkonti, wédn̥h₁-kʷe).

Plan fixes found in the second pass (beyond 0008 above):

| record | finding | fix |
|---|---|---|
| t3-t099-00030 | "They do not weep" (the eyes, dual) was 3PL HrudHénti after the 3DU question HrudHtés | verb `num: "DU"` → ne HrudHtés |
| t3-t099-00002 | "the oxen will pull the wagon": the PIE has h₁ím "it", no slot for "wagon" (v4 rule 14) | English → "the oxen will pull it." |
| t3-t099-00032 | "Wool is welcome to me" on gʷr̥Htós; the in-world brief bars gʷr̥Htós for "welcome" | English → "Wool is pleasing to me" (the gloss's own sense; the PIE is unchanged) |

## Engine or brief notes (report only)

- The referent WARN fires on demonstrative_so/deictic_ki n. SG pointing back to a whole previous turn ("that",
  "this"); all three here are correct uses. Low priority.
- h₂wéseti is both SBJV.3SG of h₂wést 'grow light' (0040) and PRS.3SG of h₂wéseti 'dwell' (0039); homophony, not
  an error.
- Brief/idiom tension: the in-world brief says "never gʷr̥Htós" for welcome, while data/lexicon/idioms.json offers
  gʷr̥Htós for "grateful" and "call the gift welcome". A gift that pleases is not a greeting, but the two texts should
  say the same thing.
- The batch report gives `formula_uses: 1`, but no t099 record has a non-empty `formulas` field, and 0039's "may the
  gods give you good things" (built as v4 says) is not registered as a formula. Possible counter/export mismatch.
- "Kindle the fire" (0006) on h₁éwseti 'burn' is a stretch inside the gloss's transitive sense; left as is.
- No engine gaps were found in the forms.

## Result

- Re-realized with `realize_plans.py data/generation/plans/t099.jsonl --batch t099 --model claude-opus-5-5
  --prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, 0 rejects, max lexeme uses 6, 3 WARNs (the deictics
  above). **Gate: PASS.**
- Release rule: recall 5/5 (needs ≥ 4/5), real wrong after fixes 0/20 (needs ≤ 2/20), gate PASS. All three hold;
  the approval decision is the lead's.
- Plans backup before the fixes: scratchpad `t099-plans-before-review.jsonl`. Nothing is committed.
