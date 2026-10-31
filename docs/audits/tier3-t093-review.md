# Tier 3 batch t093 review (quarrels and making peace; 40 in-world dialogues)

Reviewer brief `review-v1`. Packet: `scripts/make_review_packet.py t093 --n 20 --plants 5 --tier1 3` (28 items).
I did the blind back-translation first (`docs/audits/packets/t093-blind-translations.jsonl`, 6 items). I saved the
verdicts (`docs/audits/packets/t093-verdicts.jsonl`) before opening corpus/ or the plans.

- **Verdicts sha256:** `5fa7203bf3a498040e44107a58ef7f5805a7607870b17ef1d945fb9557db2bec`
- **Score (`score_review.py`):** plant recall **4/5** (all 4 caught plants named correctly); real items 20, of which
  0 wrong and 5 minor; Tier 1: 1 of 3 judged wrong.
- **Gate after fixes:** PASS (40/40 realized, reject 0.0, max lexeme uses 7, all_exact).

## Plants caught (in the packet's own spelling)
| item | what was wrong |
|---|---|
| 2d919497 | dʰoréyetām (IMP/PST.3DU) for "keep your dog" (needs IMP.2SG dʰoréye) |
| 9fa2927c | h₁itā́m (IMP/PST.3DU) for "Go and eat, son" (needs h₁idʰí) |
| d7f8285e | téwe sédesh₂? (NOM.PL "seats") for the echo "Your seat?" (needs sédos) |
| 8f9ad2f7 | h₂roh₁dʰéyete (2PL) for "You (dear one) spoke against me" (needs 2SG h₂roh₁dʰéyes) |

I missed one plant. It is not identified here, because the key is not read.

## Tier 1
- 15cc6250 (`t1-king-and-god-byrd-2013-0012`): *nu h₃réḱs pótnih₂ súHnum ǵeǵonh₁e* is glossed "The king's lady
  bore a son", but h₃réḱs is a nominative, not a genitive. This is the source text's own wording (Byrd 2013). It is
  reported for the Tier 1 owner and is outside this batch.

## Real items: minors and their resolution
| item → record | finding | resolution |
|---|---|---|
| 9164be4f → 00017 | *h₁yód-kʷe h₁íd mē widṓh₂*: `neg: true` on a 1SG subjunctive gives mē ("let me not find it") inside a conditional | **fixed**: `neg: "ne"` → *ne widṓh₂* |
| 36c2f3de → 00025 | *h₁íh₂n̥s* (f.) takes up "ten cows and the old spear" (ǵʰoysós m.) | **fixed**: pronoun gender m → *h₁íns* |
| b4bdcfd2 → 00031 | *h₃slidʰént* is an aorist ("slipped"), but the English had "they slip" | **fixed** in the English: "Swift, and they slipped!" |
| 1941ea53 → 00033 | *túH sénos* is masculine | **withdrawn**: the record shows the user is the husband (he calls his wife h₁súh₁eḱwa, voc. f.), so the masculine is right; *ḱéwbʰyōs* f. is used for the wife |
| 05c196f2 → 00036 | *wéy h₃nóbʰis* "we are kin" looked like a stretched sense | **withdrawn**: the full gloss is "navel, hub; kin" |

Real items wrong: **0/20 before the fixes and 0/20 after**. Real minors: 5 before, 0 after.

## Second pass (all 40 records against planner-brief-v4 and the in-world dialogue brief)
I aligned each record to its plan clause by clause (speaker, per-sentence English, token features). Results:
- **Nothing modern.** No neologisms. The only project reconstruction is *h₂énHos* "grandmother" (00018, 00020).
  It is well supported (Hitt. ḫanna-, Arm. han, OHG ana, OPr. ane), so I did not count it as a coinage. Noted for the lead.
- **Written-around concepts read correctly.** Forgive is *l̥h₁dʰí* "let them go" with the bad words as object
  (00003). Sorry is *tód ne wéḱm̥* "I did not want it" (00017, 00038). Take back a word is *h₂éti h₁áy-* (00005).
  Quarrel is *wik-* "fight", which is the lexeme's gloss.
- **Prohibitions** are mē + injunctive throughout (mē gʰrémes, mē kélh₂s, mē stunéds, mē térgʷes, mē bʰéyh₂s,
  mē dʰréwgʰs, mē légʰs). *mē pékʷōh₂?* "Should I not cook?" (00032) is a deliberative subjunctive with mē, as in
  Greek, and I accepted it.
- **Fearing takes the ablative**: twéd bʰéyh₂m̥, priHṓd ne dedwóye, wédn̥s dedwóyth₂e.
- **Short answers have the right case**: kʷóterom / sénom (ACC, 00018); déḱm̥ gʷṓs … ǵʰoysóm (ACC, 00025);
  ugʷsénm̥ kʷérom-kʷe (ACC, 00040); déh₂nus poh₂imḗn (NOM, 00030).
- **Predicate gender with a dropped subject** is right everywhere I checked: pr̥h₂wéh₂ (00030), dʰr̥ǵʰtéh₂ (00037),
  dweh₂rós (00023), luǵrós (00018).
- **Enclitics:** plan enclitic slots equal the ENCL tokens in all 40 records, so no identical enclitic was merged.
  The slot-versus-token differences are all the h₁yód particle.
- **English-only fixes:** 00024 "Lead him to me." → "Then lead him to me." (nu); 00020 "And what did you do to
  him?" → "What did you do to him?" (no -kʷe); 00025 "his goods … them" → "his wealth … it" (h₃épnos n.sg., h₁íd).
- **Notes left as they are (minor, not changed):** 00009 addresses swéḱruh₂ (mother-in-law) as "Mother". 00015
  "we two are sisters" (wé swésorh₁e) is said between sisters-in-law. woyḱós "villager" is translated "Neighbour"
  (7 uses). All three are idiomatic, and the PIE and the English agree.

## Blind back-translation agreement (6 items)
- **Close:** 56d1163d, b4bdcfd2, 2d919497.
- **Partial:** ac34fc90, 9a7567bf, 3587c55b.
- **My misreadings, not record errors:** h₁wogʷʰéyes read as "took" (it means "promised"); tr̥h₃ént read as
  "crossed" (it means "wounded"); ǵʰóstos read as "guest" (it means "hand"); h₂ḱm̥néh₁ kélh₂t read as "called a
  stone" (it means "struck with a stone").
- **No record errors surfaced.** The one record error was the planted 2d919497 dʰoréyetām, which the blind pass
  took as an imperative and the full review caught.

## Engine or brief gaps
None found in this batch. The Tier 1 nominative in Byrd's line is a source question, not an engine one.

## Fix log
Plan file `data/generation/plans/t093.jsonl` (the pre-review copy is in the session scratchpad as
`t093-plans-before-review.jsonl`). I edited plans 0017, 0020, 0024, 0025 and 0031, then re-realized with
`scripts/realize_plans.py data/generation/plans/t093.jsonl --batch t093 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`. Gate PASS. I did not set the release approval and did not commit.
