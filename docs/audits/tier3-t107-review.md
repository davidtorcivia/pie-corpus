# Tier 3 batch t107 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on servants, bondsmen and masters (a captive set to work, orders, a
servant asking to be freed, a debtor who must serve, kind and cruel masters, two servants at night, a herd left in
trust, a runaway brought back), `tier3-dialogue-inworld-v1`. Reviewer: calibrated agent review following
docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t107 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items from the `pie` field only, before any English was printed:
   `docs/audits/packets/t107-blind-translations.jsonl`.
3. Every packet item was checked word by word (person, number, case, gender) against `Lexicon.cells()` and the
   closed class. The verdicts were saved before corpus/ or the plans were opened:
   `docs/audits/packets/t107-verdicts.jsonl`, sha256
   `76b2adb9aadba278728fd24d46163cab7a9d1f3bf5931f3c0eda732541bd26a3`.
4. `resolve_review_items.py t107`, then `score_review.py t107`. data/audits/ was not opened.
5. Second pass: all 40 records and plans read in full, clause by clause with each token's features and full gloss,
   against planner-brief-v4 and the in-world dialogue brief (top part; Horrors limits).

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **4/5** (4 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong (as scored) | 1/20 (withdrawn below: 0/20) |
| real items judged minor | 0/20 |

Plants caught (packet spelling):
- h₂éwis: GEN/ABL.SG of h₂ówis for the object "a hundred sheep" (ACC.PL h₂ówins);
- dʰúgh₂teres: VOC/NOM.PL (initial accent) for the object of "lead my daughters" (ACC.PL dʰugh₂térn̥s);
- h₁sté: 2PL "you are" in "Are there wolves in the mountains?" (3PL h₁sénti);
- h₂mélǵowos: SBJV.1DU in "Who will milk my cows?" (3SG h₂mélǵeti).

Missed plant, found after scoring: e61a0bac "Then sit down at the loom", **téntleh₂** h₁épi. téntleh₂ is the
NOM/ACC.PL of the neuter téntlom; the object of h₁épi "at" needs LOC.SG téntloy (`Lexicon.cells('pie-lex-tentlom')`).
I found it by checking the cells again after the advisor's prompt, when the corpus was already open. It does not
change the scored 4/5, and the verdicts file and its sha256 are unchanged. Lesson: I looked up only the forms I
already doubted. The brief asks for every word's case to be checked, short turns included.

**Withdrawn wrong.** bf0983e2 (t3-t107-00019): I marked "You are small" (túH péh₂ureh₂) as a wrong feminine, since
the cup-breaker calls the other speaker "brother". The plan sets `gender: "f"` on both the pronoun and the
adjective on purpose: the cup-breaker is a little sister. The PIE is correct, but its English didn't show the
gender. Fixed in the English and PIE by adding a vocative (below).

**Real wrong: 0/20 after re-checking (1/20 as scored); real minor: 0/20.**

## Blind back-translation agreement

Six items (one of them, a4419643, turned out to be a plant). My readings agree in substance with the record
English on all six. The differences were my own misreadings, not faults in the records:
- a4419643: I read h₁áyso as "I beg". It is the MID imperative of h₁ay- "take" ("Take me").
- 00989798: I didn't know h₂isḱóm. It is PST.1SG of h₂isḱéti "seek" ("I searched for it").
- 99518f11: I took gʷr̥h₂unés as "heavy work" and gʷéwbʰis as "blows". They are ABL.SG of gʷréh₂wō "quern" and
  INS.PL of gʷṓws "cattle".
- e9564d0e: I read súHnew "son!" (VOC) as "aloud".
- 272852e2: I read kʷéh₂set and spéḱyom as present/imperative. They are PST ("when your son was coughing, I
  watched him").
- ff97b931: I took wédʰēti as "lead". The record uses the homograph wédʰeti-2 "bind", which is correct.

## Second pass: all 40 records

Checked on every record: two speakers, user first, a new speaker starts a new sentence, per-sentence English
present and joined to the full English. Every turn answers the one before it. Nothing is modern or coined
(sékʷetor "serve" is the lexicon's own idiom). Within the Horrors limits there is no gore and no sexual
violence.

The batch shows the harsh world honestly and in-world:
- a servant's son is a servant (00020);
- old servants "sit by the door and die" (00017);
- a captive is beaten at the quern and dogs are set on runaways (00007, 00009);
- captive women are to be struck if they are slow (00021);
- a free labourer is threatened if he speaks in the assembly (00037);
- a servant has no name (00038);
- the chief's answer that "a servant does not become free again" (00032).

Freedom is granted only in ways the society allows: a servant freed for saving a son, a nurse freed by the boy
she raised, release at a master's death, a debt worked off, a ransom. There are no abolitionist speeches.

Checklist results:
- **Pronouns:** all 14 WARNs are not real. Eleven are demonstratives whose antecedent is a fact, or is further
  back: tód "it/that" (0003, 0006, 0020, 0022, 0023, 0026, 0035), só = the chief (0001), tóm = the home (0007),
  tóns = the ransom horses and sheep (0014), tóm = the man for sale (0024). One is the impersonal "it has dawned" beside a
  VOC (0002). Two are homograph notes: h₂éǵete and h₂éǵonti mean "drive", which is what the English says (0002,
  0025).
- **Senses** (full glosses): h₁suménēs "kindly/merciful" (0005, 0006, 0017, 0040) is the brief's "kindly". The
  nurse is ǵŕ̥h₂enti gʷḗn "old woman" (0034). The beatings use kelh₂- "strike", gʷʰn̥sḱé- "strike", téwk- "push,
  strike" and stuned- "push, hit", all in their glosses. kʷéh₂se- "cough" (0026) and mā́dsos "food, mush" (0031,
  0036) match their glosses. "Must" and "can" are rephrased as subjunctives. h₂ḱh₂owsyéti "hear well" and h₁áyso
  "take" (MID) are correct, and uksḗn "ox" is allowed by brief rule 10.
- **Fearing with the ablative:** ǵʰóstōd (0005), dʰh₁sbʰós … twéd (0027), h₂éǵtreh₂s (0040). All correct.
- **Cows as female:** gʷṓws has `gender: f` with feminine pronouns in 0002, 0003, 0004, 0008 and 0022
  (h₁íh₂n̥s, tā́s, h₁óyneh₂ gʷṓws). Generic "cattle" is m in 0007 and 0013, which is fine.
- **h₂élyos:** h₂élyeh₂s dʰǵʰmés (0011, 0040), h₂élyeh₂m dʰéǵʰōm (0025), h₂élyons "other men" (0025).
- **Female servants:** kaptéh₂es, gʷr̥déwih₂es and ml̥déwih₂es with a dropped subject (0021), h₁léwdʰereh₂ (0034),
  túH … ḱéyweh₂ and lewbʰéh₂ (0026, 0034). A mother who calls herself h₃órbʰos (0020) is acceptable: it is a
  noun, and there is no feminine in the lexicon.
- **Short answers:** the `case` is right in all 12: ACC for objects and goals (0008, 0010, 0014, 0023, 0024,
  0025, 0037, 0039), LOC (0009), NOM for a subject (0021), VOC (0038), and NOM for the echoed predicate (0034).
- **Athematic obliques:** déms, dʰǵʰmés, ph₂trés, h₂uséy, pḱéwey, gʷr̥h₂unés, ǵʰyémi, pérunsu, déh₂nus all agree
  with the cells.
- **Enclitics:** all are in Wackernagel position or after the first word of their clause.

### Fixes (plans, data/generation/plans/t107.jsonl)

| record | issue | grade | fix |
|---|---|---|---|
| t3-t107-00019 | túH péh₂ureh₂ is feminine (the speaker is a little sister), but the English "You are small" doesn't show it | minor (clarity) | Added VOC swésor to the clause: "You are small, sister, and my back is hard." |
| t3-t107-00023 | léykʷs "you left behind, abandoned" was glossed as "you lost" | minor (stretched sense) | English: "you abandoned the chief's oxen" |
| t3-t107-00040 | h₁yód "if, when" was rendered "because" | minor (English says more than the PIE) | English: "He fled when he grew afraid of your whip." |

Left as they are (acceptable):
- PST wédʰom and h₂éǵom for "have brought / have driven". Neither verb has an aorist, so rule 8 applies.
- h₂lékseti "guard" for "keep" an oath (0023).
- wóydth₂e (0001) is the handbook's underlying 2SG perfect.
- Fem. h₁yéh₂es/tā́s "those (women) who weep" in 0025, for women being carried off; the English is neutral.

Second-pass counts over 40 records: before, 0 wrong and 3 minor; after, 0 wrong and 0 minor.

## Re-realization and gate

`realize_plans.py data/generation/plans/t107.jsonl --batch t107 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`: the gate is **PASS**. 40/40 realized and exact, reject rate 0.0, max lexeme uses
8, 14 warnings (all checked above, none real), 1647 tokens.

## Engine / brief findings

None. The missed plant was the reviewer's miss, not an engine or brief fault.

## Release-rule inputs (for the lead)

- Plant recall 4/5 (rule ≥ 4/5: met).
- Real wrong after fixes: 0/20 (rule ≤ 2/20: met).
- Gate: PASS.
