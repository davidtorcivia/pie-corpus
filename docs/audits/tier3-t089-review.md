# Tier 3 batch t089 review (review-v1): the feast and drink

Reviewer: calibrated reviewer (Claude Opus 5.5), 2026-10-31. Brief: docs/generation/reviewer-brief.md.
Batch: 40 in-world two-speaker dialogues (`tier3-dialogue-inworld-v1`): the host's welcome, shares of meat, the
mead-cup, a singer praised, too much drink, a feast for the gods.

## Procedure

1. Packet: `scripts/make_review_packet.py t089 --n 20 --plants 5 --tier1 3` → 28 items (20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items from the `pie` field only, written before any English was printed:
   `docs/audits/packets/t089-blind-translations.jsonl`.
3. Verdicts written and saved before opening corpus/ or the plans:
   `docs/audits/packets/t089-verdicts.jsonl`, **sha256 `41b3ffd0ef7a45352f0432d291194a853c6cc11a087d1813975b2480941cab5b`**
   (resolve_review_items.py printed the same hash). data/audits/ was not read.
4. `resolve_review_items.py t089`, then `score_review.py t089`.
5. Second pass: all 40 records read in full against planner-brief-v4.md and planner-brief-dialogue-inworld.md
   (top part), with every plan slot, token feature and full gloss (dump script in the session scratchpad).

## Calibration

| | |
|---|---|
| plant recall | **5/5** (all 5 named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong (before fixes) | **0/20** |
| real items minor (before fixes) | 1/20 |
| real items wrong / minor after fixes | 0/20, 0/20 |

The plants, each caught as **wrong** (packet spelling):
- 8af6fa59: *píph₃ete* is 2pl; "you drank" said to one child needs 2sg *píph₃es*.
- 5e975918: *h₂usbʰís* is instrumental plural; "we honour Dawn" needs acc.sg *h₂éwsosm̥*.
- ef8e7a80: *kʷéroybʰos* is dat./abl. plural; "in the pot" needs loc.sg *kʷéroy*.
- 4ab150c5: *uḱtés* is the 2/3 dual of wéḱti; "he wants the pig" needs 3sg *wéḱti*.
- c0741f03: *h₁usuyéh₂s* is fem. gen./abl.sg; "may the gods give you good things" needs neut.pl acc *h₁wésuh₂*.

Real-item minor (9fe2ac74 = t3-t089-00005): *swéh₂es-kʷe gʷénh₂es* "and their wives". The reflexive possessive sits
inside the subject and points back to the previous clause's subject. Early IE *swo-* can be used this loosely, but the
plain genitive is unambiguous. **Fixed**: POSS `closed:anaphoric_i` m PL → *h₁éysōm-kʷe gʷénh₂es*.

## Blind back-translation (6 items)

All 6 agree in substance with the English. The detail errors were mine, not errors in the PIE:
- eae7975e: I read *h₁áyso* as a genitive "of bronze". It is MID.IMP.2SG of h₁ay- "take!".
- f6e1069e: I gave *ḱéyth₂er* to the wrong speaker. It is 2sg "you lie".
- 26b43922: I read *súHnew moy* as "for my son". It is a vocative.
- 108edfd3: I read *gʷḗn* as "when". It is the vocative "woman".

## Second pass (all 40 records)

**Wrong: none.** Nothing modern and no coinage. *wéyh₁ō* "wine" (t3-t089-00026) is an inherited lexicon word. The only
project words are pie-proj h₂énHos "grandmother" and spélom "story", which v4 allows in Tier 3, as earlier reviews ruled.
Every turn answers the one before.

Checks made:
- **Format:** every plan has exactly two speakers, `user` first, a break at every change of speaker, per-sentence
  English that joins to the plan's English, 4–14 clauses and 2–8 turns (checked by script). No opening greeting is
  used more than 5/40 times.
- **Pronouns:** the three realizer WARNs are fine. t089-0004 *ḱód* "why do you say this?" and t089-0011 *tód* "you
  said that last year too" point to the speech just made (neuter). t089-0038 *téh₂* "them" covers *mḗms* and
  *h₂élbʰit*, both neuter. The other anaphors agree with their antecedents: *h₁ím* for kʷéros, wéyh₁ō, tworḱós and
  ḱérh₂sō (all m); *h₁íns* for h₁erkʷóns; *h₁íh₂* for skélesh₂ and péh₃tleh₂.
- **Verb senses** checked against full glosses: h₁opéyeti "make reach; give", h₁ayt MID "take", bʰágt "receive as a
  share", moréyeti "kill", sodéyeti "seat" (a true causative, used as one), srobʰéyeti "sip", ḱlowséyeti "listen to",
  bʰoréyeti "carry around", wodʰéyeti "lead", h₁ept "seize" for "take it", stunédti "hit", h₁éh₁ugʰos "vow; boast".
  All are used in a sense their gloss gives. h₁yód "for/because" is the sanctioned idiom (idioms.json).
- **Fearing + ablative:** the batch has no verb of fearing.
- **Formulas** (11 records hit the menu): *h₁ógʷʰim gʷʰen-*, *ḱléwos ń̥dʰgʷʰitom*, *h₁uséwōm déh₃tōr*, *ph₂tḗr dyḗws*
  (00009, 00012), *dʰéǵʰōm méh₂tēr*, *h₁nómn̥ dʰeh₁-*, *méǵh₂ ḱléwos* (00032, 00033), *h₁wésu ḱléwos* and *HeHḱúbʰis
  h₁éḱwōys* (00037), and *h₂éwsosm̥ diwés dʰugh₂térm̥*. All are used in their sense. Some menu hits are accidental
  (see the tooling note).
- **Predicate gender with a dropped subject:** pl̥h₁nóm n (cup), dʰr̥sús m (son), dl̥h₁gʰós m (road), ph₃tós m,
  ḱéyweh₂ f (to the mistress), ǵn̥h₃réh₂ f (to the girl, via túH f), h₁suménēs f (to the daughter). All correct.
- **Short answers:** NOM for subjects (00001, 00020), ABL (00008, 00034), ACC (00010, 00021, 00022, 00028, 00031,
  00035, 00036), LOC *dʰǵʰémi* (00026), INS *priHṓys moy HeHḱúbʰis-kʷe h₁éḱwōys* (00037). All correct.
- **Athematic obliques:** ph₂wéni, dʰǵʰémi, déh₂newi, h₂Hséh₂i / h₂éHsh₂m̥, ḱr̥h₂séni / ḱr̥h₂snés / ḱérh₂sonm̥,
  neh₂wés, diwés, dyḗm, ḱwn̥bʰís / ḱwn̥bʰós, gʷéwōm, h₁widʰwéh₂ey, bʰréh₂tr̥s, gʰóstipoteys, ǵr̥h₂n̥téy, h₂n̥rṓm, sédesi,
  and the acrostatic wédn̥h₁. All correct.
- **Enclitics:** all in second position (*gʰóstipoteys nos pótnih₂*, *suHnús toy moy mā́dsom*, *ǵérh₂ont nos dyḗws
  dh₂pnóm*). The stressed *méne* is used where the plan wants it non-enclitic.
- **Duals:** *dwóh₁ ḱr̥h₂nóh₁ … gʷh₂tā́m* (3du verb), *dwóyh₁ skélesih₁*, and *mḗms h₂élbʰit-kʷe … h₁stés* (two
  subjects, 3du). All correct.

Minor findings, fixed in data/generation/plans/t089.jsonl:
- t089-0001 *tréyes-kʷe swṓs suHnéwes* "his three sons": the reflexive sits inside an NP coordinated with its possessor
  (the same pattern as 0005). Changed to POSS anaphoric m → *h₁ésyo suHnéwes*.
- t089-0005: see the real-item minor above.
- t089-0010 English "the master **himself** poured them": "himself" has no slot. The English now omits it (rule 14).
- t089-0008 English "come back … and sing for us **again**": the single h₂éti is already "back". "again" removed.

Left as is (defensible): PST (imperfect) for single past events where the lexeme has no aorist (pl̥néh₁m̥,
gʷr̥h₃óm/ét, ḱélom); gnomic AOR for h₁áyto and h₂wérst where the verb is aorist-only (v4 rule 8); *yúH dʰr̥séwes*
(00018), plural because the user said "we killed".

## Re-realization and gate

`realize_plans.py data/generation/plans/t089.jsonl --batch t089 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`: 40/40 realized, 40 exact, reject_rate 0.0, max_lexeme_uses 7 (cap 7; the fixes take two
uses off pie-lex-swos and add none to a capped word), formula_uses 11, warnings 3 (the same three, all fine).
**Gate: PASS.**

## Engine / tooling notes (report only)

- `_formula_uses` (scripts/realize_plans.py) counts a record when every lexeme of a menu entry occurs anywhere in it.
  Several hits are accidental: 00013 "Father Sky" (a vocative ph₂ter and a separate dyḗws), 00008 and 00033 "good
  fame" (h₁wésus describes something else), 00037 "great fame" (méǵh₂ goes with the vow). The count of records with a
  formula stays 11, but the counter would credit a batch with formulas it does not use. It should require the
  formula's lexemes to be in one phrase (a head and its MOD/POSS).
- A relative pronoun that is not the subject is not fronted. t089-0040 clause 3, "the seat that the lord gives you",
  comes out as *gʰóstipotis toy h₁yód h₁opéyeti*, with the object relative *h₁yód* in the middle of its clause. Since
  *h₁yód* is also the subordinator "if, when, because", the clause can be read as "the lord, when he gives you …". This
  is the batch's only non-subject relative. The others (0007, 0013, 0018, 0031, 0035) are subjects, so SOV order puts
  them first anyway. The realizer should front `closed:relative_yo` whatever its role, as it fronts kʷís/kʷíd. The plan
  was left unchanged.
- No engine morphology errors found.

Release rule inputs for the lead: recall 5/5, real wrong 0/20 after fixes, gate PASS. Approval not set by the
reviewer; nothing committed.
