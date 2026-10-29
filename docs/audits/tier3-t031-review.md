# Tier-3 review: packet t031 (28 items)

The packet covers law, oath and judgment texts, plus three Tier 1 fable lines. It was built with `scripts/make_review_packet.py t031 --n 20 --plants 5 --tier1 3`. The review follows `docs/generation/reviewer-brief.md` (review-v1). The reviewer worked from handbook knowledge only: Fortson, Beekes, Ringe, LIV², and Mallory & Adams as remembered. Doubtful forms were checked with a reverse index of every token to its cell, built from `Lexicon.cells()`, `Lexicon.participle_cells()` and `data/morph/closed_class.json`, and genders against `data/lexicon/lexicon.jsonl`.

Order of work:
1. The blind back-translation was done first, from the `pie` field only.
2. The verdicts were written and saved before `corpus/tier3/` or the plans were opened. `docs/audits/packets/t031-verdicts.jsonl` has sha256 `a0fca3cf78411c4d701674a52939c3a7143379857acb23e6d0ace1209a58ea6b`, and `resolve_review_items.py` printed the same hash.
3. Flagged items were mapped to records with `scripts/resolve_review_items.py t031`. The packet was never diffed against the corpus, and nothing under `data/audits/` was read.
4. One departure from "open only those records": after the verdicts were saved, record t3-t031-00001 was printed to learn the schema, and the seven records behind the planner's antecedent warnings were opened for the pronoun check the lead asked for. Because the verdicts already existed, this could not expose the plants.

## Calibration (score_review.py)

| plants caught | plants named | Tier 1 judged wrong | real wrong | real minor | real ok |
|---------------|--------------|---------------------|------------|------------|---------|
| 5/5 (blind)   | 5/5          | 0/3                 | 2/20       | 2/20       | 16/20   |

Seven items were judged wrong in all. Five were the plants:

| item | planted error |
|------|---------------|
| 044db7c7 | dual h₁éḱwoh₁ for 'the stallion' |
| 1a7ab281 | acc. dual poh₂iménh₁e for 'the shepherd' |
| 8c2aa988 | voc. pl. bʰóydʰeh₂es as the object of 'made an oath' |
| c7b5399b | nom. pl. stéh₂dʰh₁eh₂ for 'a herd' |
| 868d38ec | nom. pl. dyéwes for 'dear to the sky' |

All five were found before the item mapping was seen.

## Counts on the 20 real items

|              | ok | minor | wrong |
|--------------|----|-------|-------|
| before fixes | 16 | 2     | 2     |
| after fixes  | 19 | 1     | 0     |

All three Tier 1 lines are minor, for source notation only.

## Wrong (real, 2), both fixed at the source

- **1f160e6d → t3-t031-00005 (plan t031-0005, clause 4).** In `tósyo gʷówes h₂éǵrom wéyḱonti h₁édeti-kʷe`, the coordinated verb 'eat' is 3sg, but its subject gʷówes is plural (wéyḱonti is correctly 3pl). The clause had only a V slot, so the verb defaulted to 3sg. Fix: added `person: 3, num: PL` to the verb. It now realizes as **h₁édonti-kʷe**.
- **fba40536 → t3-t031-00026 (plan t031-0026, clause 6).** In `tód dʰéyǵʰos bʰl̥Hós méǵh₂-kʷe h₁syéh₁t`, masculine bʰl̥Hós goes with neuter dʰéyǵʰos, while méǵh₂ is correctly neuter. **Engine/lexicon gap:** `pie-lex-bhlHos` is specced as a masculine *noun* (`shape:thematic`, `family: noun`), so it cannot agree. Fix: swapped it for the adjective `pie-lex-albhos`. It now reads **albʰóm méǵh₂-kʷe**, and the English 'white' is unchanged.

## Minor (real, 2)

- **ddfa8268 → t3-t031-00017 (fixed).** In `túH HeHḱús h₂r̥ǵrós-kʷe`, 'you are swift and shining' gives masculine predicates to the fire. The same text addresses that fire with neuter n̥mr̥tóm péh₂wr̥. Personification, as with Agni, makes the masculine defensible, so this is minor. `pie-lex-h2rgjros` is another adjective specced as a masculine noun (same gap as above).
  - Fix: `gender: n` on the túH subject slot, which is the agreement controller, and `pie-lex-lewkos` 'bright' in place of h₂r̥ǵrós. It now reads **túH HeHḱú lewkóm-kʷe**, and the English changes 'shining' to 'bright'.
  - A `gender` on the PRED slots themselves is ignored by the engine. The controller's gender is what counts.
- **ae2ed34e → t3-t031-00010 (left).** `mē ḱléwseto` 'let it not be heard' uses the middle of ḱléwseti 'listen' in a passive sense. This is a stretched sense, not an error. Left as is.

## Antecedent-check warnings (planner-reported, 9)

All nine were opened in the records and judged in context:

| plan | pronoun | antecedent | verdict |
|------|---------|------------|---------|
| t031-0030 cl. 8 | **h₁íd (n.) 'I stole it'** | tn̥tlós 'net' is **masculine** (tóm tn̥tlóm, two clauses before) | **wrong gender; fixed** to m. It now reads h₁ím stéh₂yom, and the warning is gone |
| t031-0031 cl. 12 | h₁íns (m.pl.) 'you did not guard them' | the piglets, pórḱons, the only m.pl. referent | ok |
| t031-0033 cl. 10 | h₁íh₂m̥ (f.) 'lead her to your home' | the sister. méh₂tēr is nearer, but the bride-price context settles it | ok |
| t031-0034 cl. 5 | h₁íd (n.) 'the wind carried it' | péh₂wr̥ 'fire', the only neuter referent | ok |
| t031-0034 cl. 8 | h₁ím (m.) 'let us build it again' | gʷowsth₂ós 'stall'. The wind and the men are also m.sg., but 'build' rules them out | ok |
| t031-0037 cl. 8, 13 | h₁éyes / h₁íns (m.pl.) | gʷṓws 'cattle' (m.), the only plural referent | ok |
| t031-0038 cl. 7 | h₁éyes (m.pl.) 'let them drive that man out' | the men of the settlement, and the English is as vague | ok |
| t031-0040 cl. 9 | h₁ésyeh₂ey (f.) 'give her a piglet' | the shepherd's wife. The speaker, the mother, cannot be meant | ok |

Verdict: 8 of the 9 pronouns are unambiguous. One had the wrong gender, and that one is now fixed. After re-realization the batch has 8 warnings, all of them checked and harmless.

Two observations come from opening these records; they are not packet items and nothing was changed:
- In t3-t031-00040, `wékʷesh₂ ḱlḗm` drops 'of both' from 'I have heard the words of both'. The aorist for 'have heard' is acceptable.
- In 044db7c7 (a plant), the narrative is incoherent: the stallion goes to h₁énos and he is told 'it is yours', but h₁óynos leads it away. The PIE and the English agree, so this may be in the underlying plan.

## Blind back-translation (6 items, PIE only)

The translations are in `docs/audits/packets/t031-blind-translations.jsonl`, written before any English field was printed.

| item | agreement | what the blind pass missed |
|------|-----------|----------------------------|
| ae2ed34e | full | — |
| 62ea9a49 | full | — |
| 9ef3ed54 | full | — |
| 1f160e6d | structure right | read 'let **him** take' and 'work wool for her'. Flagged the h₁édeti agreement error blind; it was the real wrong item |
| eace9ea9 | structure right | read h₂éwim as a sheep variant ('lamb'), missed h₂eh₃méh₂m 'raw', read ḱéletu as 'call/drive' instead of 'cover' |
| 868d38ec | structure right | read h₂éwim as 'sheep' and tn̥tlós as 'pen'. Did not notice the plant dyéwes, read as 'to the sky' |

Overall, 3 of 6 agree fully and 3 partly. The clause structure, the legal logic and the protasis/apodosis were right in all six. The misses were lexical, and all were rare lexemes: h₂éwis 'bird' against h₂ówis 'sheep', tn̥tlós 'net', h₂eh₃mós 'raw', ḱel- 'cover'.

## Accepted conventions (not penalised)

- h₁yód stands for 'if' in the protasis. Its verb is subjunctive (h₂érh₃yēti, moréyēti) and the apodosis is a 3sg imperative, often introduced by nu.
- mē + injunctive marks a prohibition (kʷis mē kʷéyet, gʰóstim kʷis mē moréyet), ne marks a negative statement, and mē + optative a negative wish (mē h₂wisih₁ént).
- h₁opéyeti 'make reach' is used for 'give, grant', a stretched sense accepted in earlier batches. h₁áyt/h₁áyeti means 'give, pay'.
- An accusative of goal follows verbs of motion: ph₂térm̥ h₁ludʰét, tóm gʷowsth₂óm bʰéret, bʰréh₁wr̥ h₂éǵēti.
- Locative h₃rḗǵi is used for 'before the king'.
- The reflexive possessive swós can refer to the 1st person: swósyo bʰréh₂tr̥s 'of my brother', as with Ved. svá-.

## Assessment

The grammar is strong:
- Duals are used where they should be: dwóh₁ suHnúh₁ … h₁ludʰétām, bʰréh₂terh₁e … dʰh₁tā́m with the 1du subjunctive h₁élh₂owos, towdós h₁léwdʰeros-kʷe … démetām, and dwóh₁ wóyḱoh₁ ḱéywoh₁ h₁stā́m.
- Anaphors follow their antecedent's gender: h₁íd for neuter dʰéyǵʰos, wédʰmn̥ and péh₂wr̥; h₁ím for masculine ǵʰórtos, misdʰós and h₂éǵros; h₁íh₂m̥ for feminine h₂wĺ̥h₁neh₂, h₂éwis and bʰoydʰéh₂. The one exception, the net, was fixed.
- The perfect is used as a present (dedr̥ḱé, dedr̥ḱḗr 'see'; dedwóye 'is afraid'), and the middle where expected (h₁éwseto 'burned', sékʷeto 'followed').
- The h₁yós … só correlatives in the laws and the 'whoever …, let that man …' clauses are idiomatic.

The texts suit their genres:
- **Laws** are casuistic: an h₁yód/h₁yós protasis, then an imperative penalty. There are graded cases (dog kills piglet / wolf / bird; plough / graze; break the wall / snow / beast) and closing maxims ('the word of a free man is dear to the sky', 'the eagle is dear to the sky').
- **Oaths** follow the expected pattern: a 1sg denial, then a self-curse in the optative ('may the snake devour me', 'may the wolf eat my heart'), with the gods or fire invoked as witnesses. 9ef3ed54 is a proper water ordeal.
- **Judgments** are nu-chained dialogues: complaint, denial, a witness or evidence (the track, the dog, the sister, the mother), then the king's or judge's sentence. They often close on a fame line (h₁nómn̥ ḱlutóm / ne ḱlutóm).

The texts average about 37 words. Each opens with the case or the parties and closes with a penalty, a sentence or a maxim, and none reads as cut off. The one narrative flaw is the plant 044db7c7: the wrong claimant leads the stallion away.

## Engine and lexicon gaps (for the lead; `pie/` not changed)

1. **Adjectives specced as masculine nouns.** `pie-lex-bhlHos` 'white' and `pie-lex-h2rgjros` 'shining' have `family: noun, gender: m` in `data/morph/inflection_specs.jsonl`. They cannot agree with a feminine or neuter head, and check_plan does not flag the mismatch. Other thematic -ós adjectives with a noun spec probably have the same problem. These should become `adj` specs, or check_plan should reject a noun-family PRED/MOD whose gender differs from its controller's.
2. **A gender on a PRED slot is silently ignored.** Agreement comes only from the controller. That is probably correct, but it would help if check_plan warned about it.
3. **A V-only coordinated clause falls back to 3sg.** The verb does not take its number from the previous clause's plural subject (t031-0005). The planner has to state the number. An inherited subject number, or a warning, would prevent this.

## Fix summary

`data/generation/plans/t031.jsonl` was changed in four plans: t031-0005, 0017, 0026 and 0030. The batch was re-realized with `realize_plans.py … --batch t031 --model claude-sonnet-5-5 --prompt-id tier3-planner-v4`. The result: 40/40 realized and exact, 8 warnings, gate **PASS**. The release approval was not set, and nothing was committed.
