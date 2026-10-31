# Tier 3 review: t076 (dealing with other peoples, 40 in-world dialogues)

Reviewer brief `review-v1` (docs/generation/reviewer-brief.md). Reviewer: claude-opus-5-5, 2026-10-31.
Release approval not set (lead's decision). Nothing committed.

## Procedure

1. Packet: `scripts/make_review_packet.py t076 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items, done first from the `pie` field only (no English printed):
   `docs/audits/packets/t076-blind-translations.jsonl`.
3. Verdicts: `docs/audits/packets/t076-verdicts.jsonl`, saved before corpus/ or the plans were opened.
   **sha256 `e90a191b58b4637af97e20df416765f952f1f30c0d611abc7bc7ca70c4ef20f2`**.
4. `resolve_review_items.py t076`, then `score_review.py t076`.
5. Second pass: all 40 records read in full against planner-brief-v4 and planner-brief-dialogue-inworld (top part),
   with every doubtful sense checked against its full gloss (`Lexicon.meaning`).

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **4/5 (0.80)**, all 4 caught plants named correctly |
| Tier 1 judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor | 2/20 |

Plants caught:
- 270bd66b: `kóryos stéh₂dʰh₁oybʰos h₂egʰṓd`: abl. h₂egʰṓd as the predicate adjective. The record has nom. h₂egʰós.
- 7cad0112: `ph₂tḗr … méh₂tēr-kʷe gʷíh₃weti`: 3sg verb with two conjoined subjects. The answer and the record have
  3du gʷíh₃wetes.
- c4439d1b: `h₂élbʰit pékʷētes`: a 3du verb with the singular "barley" as subject. The record has pékʷēti.
- 2e939831: `sékʷedʰwe`: 2pl middle imperative to one addressee. The record has 2sg sékʷeso.

Plant missed. I noticed it while reading t3-t076-00035 in the second pass, after scoring; I did not diff the packet.
c935b490 has `h₂wĺ̥h₁neh₂h₁ ǵʰéyomn̥s téksm̥`, acc. pl. "winters", where the record has loc. sg. ǵʰyémi ("in the
winter"). I read it as an accusative of duration ("over winters"). The lesson: a time expression that fits two
case readings should be checked against the English, not just against grammar.

## Real items: wrong before and after

- **Judged in the packet: 0 wrong.**
- **True real wrong: 1/20 before, 0/20 after.** The second pass found one error in a packet item that I had
  passed: 0d6beec4 = t3-t076-00017, last line `h₁íh₂ ǵn̥néh₃si?` "Do you know them?". The antecedent is the
  oaths, h₁óytons, which are masculine. The neuter plural h₁íh₂ cannot refer to them. In my blind translation I
  read it as "Do you know this?". **Fix:** anaphoric gender n → m, giving `h₁íns ǵn̥néh₃si?`.

Minor (packet):
- d5d7edfd = t3-t076-00004: dual suHnúh₁ with 3pl middle nésōntor, beside 3du ménētes. The deponent nes- has no
  3du middle cell (the engine builds none), so the plural is forced. **Engine gap**, left as is.
- f5fb1622 = t3-t076-00007: withdrawn. I had read "I have come from the far sea … I have not seen it" as a
  contradiction, but the record shows that the trader says both "I came from the far sea" and "Have you seen the
  sea?", and the host answers "I have not seen it". The text is coherent. The packet has no speaker labels.

## Second pass (all 40 records)

**Wrong (outside the packet):**
- t3-t076-00018: "the blood-price: a hundred cows" came out as `kʷoynéh₂m ḱm̥tóm gʷṓm`, with acc. **sg.** gʷṓm
  ("a hundred cow"). The plan had `num: "PL"` on the APPOS slot, but the realizer gave the apposition its head's
  number (sg. kʷoynéh₂), and the check did not reject the mismatch (see engine findings). **Fix:** split into
  "Our chief has sent you the blood-price. It is a hundred cows." (nominal clause `h₁íh₂ ḱm̥tóm gʷówes`).

**Minor (English and alignment), fixed in the plan:**
- t3-t076-00012: the per-sentence English split "You are dear to me. But" | "I long for …". Now "You are dear to
  me." | "But I long for the tongue of my mother."
- t3-t076-00024: the plan English and per-sentence English were doubled ("We say this: Be whole! Be beloved to us!
  Be whole! Be beloved to us!", and "When a guest goes away, what do you say?" twice). Now "We say this:" and
  "We say the same." each stand alone.
- t3-t076-00032: "I know this cup! Sit down, child. You are my child now." was doubled in the same way, now fixed.
  "the eyes of an old friend": the PIE has no "old" (ḱéywos "dear, intimate"), so it now reads "a dear friend".
- t3-t076-00017: "were … once our foes?": "once" has no slot, so it is dropped.
- t3-t076-00018: "let the slayer never come": the PIE is mē, "not", so it now reads "not come".

**Checked and clean:**
- *In-world.* There is no money, writing or state anywhere. Trade is barter and value: h₂élgʷʰeti "be worth",
  h₂elgʷʰós, médos "measure", kʷréyh₂- "exchange", pérh₂- "sell", kʷrinéh₂- "buy" for cows. Payment is
  kʷoynéh₂ "blood-price, ransom" (Gk ποινή), kʷey- MID "avenge", gʰeldʰ- "pay". The one project reconstruction,
  spélom "story" (0034), is allowed in Tier 3 (planner-brief-v4, 2026-10-28). Both speakers are of the PIE world
  in every dialogue: envoys, chiefs, hostages, captives, traders, herdsmen and kin. Every turn answers the one
  before it. Where a dialogue ends on a question (0027, 0009), it is a question asked back, which the brief allows.
- *Writing around missing words.* The PIE says what the English says:
  - "envoy" is "my lord says / sent me with words": mléwHti, sélǵt + wékʷesbʰis.
  - "hostage" is bʰoydʰéh₂ "pledge", a predicate accusative, "I give you my son as a pledge" (0004, 0001).
  - "understand" is "know" (woyd-), as in "I hear your words but do not know them" (0003).
  - "treaty" is kʷyéh₁tis, "peace between the peoples" (0001, 0013).
  - "oath" (0020) is bʰoydʰéh₂, whose full gloss is "pledge, oath, swear; contract".
- *Oaths and guest-friendship.*
  - Oaths: swearing by the gods and by Father Sky in the instrumental (deywṓys, ph₂tréh₁ diwéh₁); an oath with a
    curse on the deceiver (0002); a boundary stone under Sky (0028).
  - Guest-friendship: "my house is your house", sitting at the host's fire, gifts exchanged (0002, 0015, 0032, 0040).
  - Greetings: "be whole" kéh₂ilos h₁sdʰí and "be dear to us". No gʷr̥Htís or gʷr̥Htós is used.
- *Fearing.* Verbs of fearing take the ablative: dʰubʰrṓd wédn̥s and h₁ésmōd-ge with bʰebʰoyh₂- (0034).
  dedwóyth₂e (0020) has no object.
- *Senses, checked against full glosses.* These looked stretched, but each is correct:
  - pérun-/pérwr̥ "rock; mountain"
  - h₂éwh₂os "maternal grandfather; maternal uncle" (an "uncle" in 0031)
  - ǵneh₃- MID "get to know, meet"
  - gʷéru "spit; spear"
  - h₂éǵros "field, pasturage"
  - wid- AOR "see, find"
  - h₂énti "near"
  - wiHrós "warrior"
  - h₁áy- MID "take"
  - h₁ewk- "learn"
  - méne- + acc. "wait for"
- *Pronouns.* All pronouns track their referents, with the 0017 exception above. The realizer's 20
  anaphoric/deictic warnings were each checked against the earlier clauses; every one has an antecedent. The one
  homograph warning (0034, h₂éǵeti "drives", not "says") is correct as "drives". h₁íh₂ (n. pl.)
  for herds, words and garments; h₁ím for a masculine oath (0001) and for salt (sḗh₂l, m.); h₁íh₂m̥ for peace.
- *Athematic obliques* are right: déh₂newi, wédni/wédn̥s, kl̥Héni/kl̥Hnés, h₂ḱméni, ǵʰyémi, bʰr̥h₁wéns, ḱr̥h₂séni,
  gʷéwbʰis, h₂éwibʰos, neh₂ubʰós (ABL with a comparative).
- *Enclitics* stand in Wackernagel position. Pronouns after ḱóm take the dative (méǵʰye, tébʰye, n̥sméy ḱóm), which
  is the documented case fallback.

## Blind-translation agreement

All 6 agree in substance. Two of the "uncertain" notes I wrote were real problems:
- 270bd66b: the h₂egʰṓd plant, which I flagged.
- 0d6beec4: I translated "Do you know this?", which led to the pronoun-gender fix above.

The f5fb1622 "contradiction" came from the missing speaker labels, not from the text.

## Re-realization and gate

`realize_plans.py data/generation/plans/t076.jsonl --batch t076 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1` gave 40/40 realized, 40 exact passes and a 0% reject rate. **Gate: PASS**
(max_lexeme_uses 8, distinct lexemes 324, 3 formula uses). The plan file from before the review is kept as a
scratch copy outside the repo.

## Engine findings (report only)

1. **APPOS number silently overridden.** `_check_appos` (pie/realize.py) compares the APPOS slot's `num` only with
   an *explicit* head number. With an unset (sg.) head, `num: "PL"` passes the check, and the slot is then realized
   in the head's number: "kʷoynéh₂m ḱm̥tóm gʷṓm" (0018). Either reject it, or let a numeral apposition keep its own
   number ("the price: a hundred cows" is natural in the daughters).
2. **No 3du middle** (and no 3du perfect): a dual subject of a deponent such as nes- must take the 3pl (0004).
   This is already known; it is listed here because it produced a packet minor.
