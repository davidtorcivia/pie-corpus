# Tier 3 batch t096 review (herding and pasture; 40 in-world dialogues)

Reviewer brief `review-v1`. Packet: `scripts/make_review_packet.py t096 --n 20 --plants 5 --tier1 3` (28 items).
I did the blind back-translation first (`docs/audits/packets/t096-blind-translations.jsonl`, 6 items) and printed
only the `pie` field. I saved the verdicts (`docs/audits/packets/t096-verdicts.jsonl`) before I opened corpus/ or
the plans. I did not read anything under data/audits/.

- **Verdicts sha256:** `e2b708ab7a47d7532d35b8950cbd95c996579c2bf6d77dfd8e09296840a685df`
- **Score (`score_review.py`):** plant recall **5/5**, with all 5 plants named correctly. 20 real items: 0 wrong,
  1 minor. Tier 1: 0 of 3 judged wrong.
- **Gate after fixes:** PASS. 40/40 realized, reject rate 0.0, max lexeme uses 6, all_exact, 7 WARNs (all checked; see below).

## Plants caught (in the packet's own spelling)
| item | what was wrong |
|---|---|
| 8a79adf2 | *dʰéh₁yēte* is SBJV.2PL in "if they (h₁íh₂, n.pl. 'the young ones') suckle". It needs 3rd person: 3SG with a neuter plural subject, *dʰéh₁yēti* |
| 4435f278 | *ḱósyeh₂i nókʷtn̥s*: ACC.PL "nights" sits next to a fem. LOC.SG demonstrative. "This night" needs *nékʷti* |
| 34f4ac48 | *swóybʰos moy misdʰóm*: DAT/ABL.PL of reflexive swós, agreeing with nothing |
| 814937a9 | *Hrumptā́m* is a 3DU secondary form, but the subject is singular (*uksḗn*, "the bull has broken the fence") |
| 2f23c863 | *sweh₂dúh₁* is a dual or INS form. The predicate of neuter singular *h₂mélǵos* needs *sweh₂dú* |

## Blind back-translation
The 6 items (344f8ada, 9636da1d, 6d25a0d6, 5eb9f1da, 1c6073e3, cfb5c835) agree with the packet English in
substance. Where they differed, I had guessed the lexemes wrong, and the PIE itself was fine:
- I read *h₂ḱh₃ént* as "were hurt", but it is "have eaten" (h₂eḱh₃- 'eat').
- I read *stóygʰoy* as "at the fence", but it is "on the path".
- I read *h₁nédʰt* as "came out". The gloss is "come forth", so this one matched.
- *ḱéstrom* is "knife" (I had "comb").
- *léymō* is "lake" (I had "meadow").

## Real items: minors and their resolution
| item → record | finding | resolution |
|---|---|---|
| 5eb9f1da → 00025 | *wérǵomes* for "shear" is also the PRS.1PL of wérǵeti "make" | **withdrawn**: the plan uses pie-lex-wergjt-3 "to shear" |

Real items wrong: **0/20 before the fixes and 0/20 after**. Real minors: 1 before, which was withdrawn, so 0 after.

## Second pass (all 40 records against planner-brief-v4 and the in-world dialogue brief)
I aligned each record to its plan clause by clause: speaker, per-sentence English, and token features.

- **Speakers and English:** I checked every record with a script. Each has a speaker on every clause and exactly
  user + model, with the user first. Every change of speaker starts a sentence, and every sentence-initial clause
  has its `english`. The joined English equals the plan's English. All records have 4–14 clauses and 2–8 turns.
- **Nothing modern, no coinages.** The only project reconstructions are *h₂énHos* "grandmother", *pṓlHos* "foal",
  *mógʰus* "boy" and *spélom* "story", which are used as before. Every turn answers the one before.
- **Cows as female animals:** the cow slots and their pronouns are `gender: "f"` throughout. Examples: *albʰéh₂ gʷṓws*
  (00005); *gʷéws … h₁ésyeh₂ey* (00005); *kr̥snéh₂ … h₁íh₂ gʷr̥déwih₂* (00007); *gʷówes … h₁íh₂es* (00032);
  *h₂yuHn̥ḱéh₂m gʷṓm … h₁íh₂m̥* (00040). Bulls are *uksḗn* (m) and aurochs *táwros*.
- **Fearing takes the ablative:** *wĺ̥kʷōd*, *h₁ésmōd ne bʰebʰóyh₂h₂e*, *ǵʰwērbʰós dedwóyh₂e*,
  *ḱr̥h₂nóybʰos bʰebʰóyh₂h₂e*, *ph₂wéns trésonti*, *h₂ékʷeh₂s tréseti*.
- **h₂élyos as a gendered adjective:** *h₂élyosyo ḱóymosyo* (m, 00017); *h₂élyās* f.pl. for the other sheep and
  cows (00013, 00032).
- **Predicate gender:** I found no nominal clause with a dropped subject. Explicit pronoun subjects agree:
  *h₁éy dweh₂rós*, *h₁íh₂ kéh₂ileh₂*, *pótni … túH ḱéyweh₂*. The neuter plural predicate *méǵyosh₂ h₁ést* with
  *stéh₂dʰh₁eh₂* (00032) is the inherited neuter-plural-with-singular-verb rule.
- **Short answers:**
  - ACC where the question asks for the object: *septḿ̥ gʷṓs uksénm̥-kʷe*, *déḱm̥ gʷṓs tríns-kʷe uksénn̥s*,
    *h₁rudʰróm pṓlHom*, *kʷétesrn̥s h₂ówins*, *dweh₂róm bʰérǵʰom*.
  - LOC: *méǵh₂i h₂ḱméni*.
  - NOM where the subject is asked for: *déḱm̥ gʷówes uksḗn-kʷe*, *h₁néwn̥ h₂óweyes …*, *somHós?*.
- **Athematic obliques** I checked against `Lexicon.cells()`: *pr̥wéni*, *bʰr̥h₁wéni/-wéns*, *ph₂wéni/-wéns*,
  *h₂ḱméni*, *h₂ḱmn̥sú*, *kl̥Héni*, *gʷéwi/gʷéws*, *h₃rēǵés*, *wédn̥h₁*, *h₁uHdʰénbʰos*, *sh₂imń̥bʰis*.
  *bʰólǵʰis* ABL.SG (00010) is a listed variant of the i-stem ablative.
- **Verb senses** I checked against the full glosses:
  - *HrewdH-* "howl, roar, bellow (of animals)"; *nes-* "return home unharmed".
  - *ḱubʰrós* "pure, clean"; *pleh₁dʰ-* "swell"; *móros* "plague".
  - *h₂m̥bʰí* "in exchange for"; *h₂éyeri* "tomorrow" (idiom); *éti* "still, also, too".
  - *h₁yaǵ-* "offer (to a god)"; *wodʰéyeti* "lead" (reflex-confirmed); *h₂eḱh₃-* "eat".
- **Pronoun WARNs (5):** all are right. The antecedent is two or more clauses back, but it is unambiguous by gender
  and number: the cow (00019, 00040), the bull (00022), the bulls (00033), the young ones (00035). The 2
  h₂éǵet/h₂éǵt near-collision WARNs (00015 "drove", 00034 "said") are both used in the right sense.

### Fixes made (plans, then re-realized)
| record | finding | fix |
|---|---|---|
| 00002 | "*Near* the village the grass has dried up" had only LOC *ḱóymoy* ("in the village") | added ADV *h₁épi* with dep → *ḱóymoy h₁épi* |
| 00033 | "Lead her *behind the bulls*": the PIE has no word for "behind the bulls" (rule 14) | English → "Lead her: she will follow them." |
| 00039 | *swóm moy misdʰóm*: the reflexive swós refers to the subject, the master ("your own wage"), but the English is "my wage" | dropped the swós slot → *misdʰóm moy dh₃dʰí* |

### Notes left as they are (minor, not changed)
- 00013, 00034: *solh₂wéh₂i sémeh₂i / nékʷti* "every summer / night" is singular "whole, all". It reads as
  "every", like Lat. omnis.
- 00021: *nu h₂wérst* is an aorist translated "Now it is raining!" (inceptive).
- 00004, 00005: the imperfect *bʰér-* is used for "carried / have brought". bʰer- has no aorist.

## Engine or brief findings
None. The minors were all in the plans.
