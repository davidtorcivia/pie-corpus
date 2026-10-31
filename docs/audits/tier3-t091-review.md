# Tier 3 review: t091 (gods and rites explained, 40 in-world dialogues)

Reviewer brief `review-v1` (docs/generation/reviewer-brief.md). Packet: `make_review_packet.py t091 --n 20 --plants 5 --tier1 3`
(28 items: 20 real, 5 planted, 3 Tier 1). data/audits/ was not opened.

## Order of work and integrity

1. Packet made; only the `pie` field printed. Six items back-translated blind
   (docs/audits/packets/t091-blind-translations.jsonl) before any English was seen.
2. Packet English read; forms checked against `Lexicon.cells()` (a reverse form index built from the engine),
   `Lexicon.meaning()` and `scripts/lexq.py`.
3. Verdicts saved before corpus/ or plans were opened:
   docs/audits/packets/t091-verdicts.jsonl,
   **sha256 `8b90ecc0e8d664e179e66b2f1687a5ea43cf0ac77e37fd73454e4572a5329d1a`** (resolve_review_items.py confirmed this hash).
4. `resolve_review_items.py t091`, then `score_review.py t091`.

## Calibration

| | |
|---|---|
| plant recall | **5/5** (all named) |
| real items judged wrong | **0/20** |
| real items judged minor | 3/20 |
| Tier 1 judged wrong | 0/3 |

The five plants I caught, in the packet's spelling:
- 7a602097 **ḱlutā́m**: aorist 3DU for "Have you heard my name in songs?" (the corpus has 2SG ḱléws).
- cce0b186 **wikḗte**: SBJV 2PL for the oath "I will not fight against you" (corpus: 1SG wikṓh₂).
- da76e300 **kénkoh₂**: 1SG with the subject wĺ̥kʷōs, "the wolves are hungry too" (corpus: kénkonti).
- 4105cf31 **dh₃dʰí**: 2SG among 2PL imperatives addressed to the group (corpus: dh₃té).
- e089d861 **kʷéḱetes**: SBJV 2DU/3DU for "Will I see the wind?" (corpus: kʷéḱoh₂).

Four of the five sat in short question-and-answer turns, as the brief warns.

## Blind back-translation

All six agree with the English in substance (c33764bd, 801efc95, ac022b09, e089d861, b3a4435a fully; 7a602097 up to
the plant). Small differences: I read `pérunsu` as "rocks" (gloss: "rock; mountain"), `h₂éwins` as "birds" (correct)
and `kʷíd` as "what" where the English has "why" (both senses exist). In 7a602097 I could not read `ḱlutā́m` as "you
heard": that was the plant.

## Real items: minor (packet)

| item / record | issue | action |
|---|---|---|
| c33764bd / t3-t091-00019 | `péruti mr̥yéto` (PST middle) for the single event "he died last year"; rule 8 wants the aorist `mért`. | **Fixed in the plan** (clause 8 → `pie-lex-mert` AOR, now `péruti mért`). `pie-lex-mert` was at the cap, so I freed a use in 0004: its "She does not die" had a gnomic aorist `ne mért`, now `ne mr̥yétor` (PRS MID), the same as 0014, 0025 and 0034. The first try at this fix FAILed the gate (mert 9/8) and was reverted. |
| 610c3291 / t3-t091-00026 | `dh₃ént` / `dh₃mé` (aorist of `deh3t`) for "what do your people give / we give" (habitual). | Not fixed: moving both to the present `dédeh₃ti` took it to 10 uses (over the cap of 8). Left as a gnomic aorist, which is defensible. |
| f553830f / t3-t091-00037 | The answer `dh₃mé` (aorist) to the present question `dedh₃més`; `mē` in the conditional "if we give nothing" (the engine's rule-11 mē for neg + 1st-person SBJV); goal `tóns` with no adposition beside `n̥smé próti`. | **Fixed in the plan:** clause 1 → `dédeh₃ti` PRS 1PL (`dedh₃més`); clause 5 `neg: "ne"` (now `h₁yód kʷid ne h₁opéyōmes`); clause 3 GOAL + ADV `próti` (`tóns próti wédʰomes`). |

## Second pass: all 40 records

Each record was read sentence by sentence (speaker, per-sentence English, the PIE, and each token's lexeme and cell)
against planner-brief-v4 and the in-world dialogue brief.

- **In-world and from inside:** nothing modern and no coinages. `spélom` 'story' and `h₂énHos` 'grandmother' are
  `pie-proj` project reconstructions, which v4 allows. The stranger's-gods dialogues (0008, 0018, 0040) compare the two
  peoples' rites without judging either ("Then he is the same god"; "The roads are different, but the fathers are the
  same"). The dark rites (0038, the hungry dead father) are told plainly.
- **Speakers:** the user speaks first everywhere, there are two speakers, and a new speaker always starts a new
  sentence. Where the model asks a question back, the next turn answers it. Every turn answers its question.
- **Theonyms:** `dyḗws` (sky god, sometimes "Sky"), `pérkʷunos`, `h₂éwsōs`, `bʰágos` ('allotter; god'), `nébʰtus`
  ('water deity', glossed "the water god") and `déh₂nu`, each in a sense its gloss gives. Gods and the dead get
  masculine pronouns (Fire, the Wind, Bhagos), Dawn, Earth and the Moon feminine ones, the Sun neuter `h₁íd`.
- **Formulas (16 counted by `_formula_uses`):** 14 are true uses in the right sense: Father Sky (00001, 00022), slew
  the serpent (00003), Dawn daughter of Sky (00004, 00036), set a name (00008, "we gave him another name"), swift
  horses (00012, 00015, 00023), great fame and imperishable fame (00014), wheel of the sun (00015), Mother Earth
  (00016, 00032), giver of good things (00024), good fame (00028). Two are lexical coincidences: 00019 "set a name"
  (`dʰéh₁t` 'set the cup' plus `h₁nómn̥` with `wéwket`) and 00040 "Father Sky" (`dyḗm` plus `ph₂térn̥s` 'the
  fathers'). **Metric issue, report only:** the counter matches lexeme sets anywhere in the record, not phrases.
- **The 11 referent WARNs:** all resolve. 0012 c6, 0027 c4: `ḱód` points forward to a quotation. 0017 c6/c9: Fire.
  0019 c6: the dead. 0023 c7, 0037 c8: the gods. 0027 c8, 0028 c6: `tód` = the fact or the act. 0038 c6: the dead
  father. 0038 c9: dual neuter `tóy` = the milk and the fat.
- **The 4 `h₂éǵeti` homograph WARNs** (0011, 0012, 0015, 0017): all mean 'drive' (rain-clouds, horses, the sun, evil
  things away).
- **Verb senses** checked against the full glosses: `ǵʰuHéyeti` 'call upon (a god)' for praying, `mḗdeti` 'heal',
  `h₁áyt` MID 'receive', `h₁opéyeti` 'make reach; give', `nes-` 'return home unharmed', `h₂éwh₂os` 'maternal
  grandfather; maternal uncle' ("Uncle", 0030), `perwr-2` 'rock; mountain', `némos` 'place of sacrifice', `ḱubʰrós`
  'shining, beautiful'. All fit.
- **Fearing + ablative:** `tósmōd bʰebʰóyh₂th₂e` (0003) and `wĺ̥kʷoybʰos` ABL (0022) are right.
- **Predicate adjectives with dropped subjects:** `dʰr̥sús` m. (0014), `h₂yuHn̥ḱéh₂` f. for Dawn (0004),
  `h₂yuHn̥ḱṓs` pl. (0034), `h₁uséwih₂` f. in "Be good" (0023; the planner set `gender: "f"`, a daughter speaking). All
  consistent.
- **Short answers:** "Herds, horses and wealth" (0024) is an np with ACC, answering "what do they give?"; "And the
  other twin?" stays NOM. Both right.
- **Athematic obliques** (`h₂Hséh₂s/-i`, `h₂ḱméni`, `pr̥wéni`, `péruni/pérunsu`, `kh₂n̥mń̥su`, `dn̥ǵʰwéh₂m`, `h₂n̥réy`,
  `h₂nr̥bʰós`, `méh₂tr̥h₁`, `sh₂wéns/-éy`, `wédn̥s/wédni`, `m̥dʰéws`, `dʰǵʰméy`, `pr̥kʷúsu`, `drúsu`) and the enclitic
  chains (`ǵʰóstom toy moy ǵʰóstoy`, `kʷíd toy wíḱpotey …`) are all in order.
- **Mechanical checks** over all 40 plans: the per-sentence `english` joins to the plan's English exactly; the user
  speaks first; there is no speaker change without `break`; there are exactly two speakers.
- **Remaining stretched choices (minor, left):** 0024 "Do you know a song of praise?" has no slot for "of praise"
  (rule 14). gnomic aorists of aorist-only 'pour' verbs (`ǵʰwént`, `ǵʰumé`,
  `ǵʰudmé`, `sikʷmé`) for habitual English, which rule 8 allows. 0001 `upér` 'above' for "from above". 0013 `kʷíh₂`
  (neuter plural) "what are the stars?". 0028 `wos` (plural) "may they give you", meaning the couple.

No real item was wrong, before or after the fixes.

## Fixes and gate

- Plan edits in data/generation/plans/t091.jsonl: t091-0037 (3 changes), t091-0019 (aorist `mért`), and t091-0004
  (`ne mr̥yétor`, which frees the cap for 0019). A backup of the plan before
  the review is in the reviewer's scratchpad.
- The batch was re-realized with `realize_plans.py data/generation/plans/t091.jsonl --batch t091 --model claude-opus-5-5
  --prompt-id tier3-dialogue-inworld-v1`. 40/40 realized, 40 exact, reject_rate 0. max_lexeme_uses 8 ≤ 8,
  formula_uses 16, warnings 15. **Gate PASS.**
- The 0026 fix (`dh₃ént`/`dh₃mé` → present `dédeh₃ti`) was tried and reverted: it took `pie-lex-dedeh3ti` to 10/8 and
  the gate FAILed. 0026 stays a minor (gnomic aorist). **Engine/brief note for the lead:** with a cap of 8 in a 40-text batch, a correct aspect fix can be
  blocked by the cap. It may help to exempt the high-frequency core verbs ('give', 'die') the way the copula is exempt.

## Release-rule inputs (for the lead; approval not set)

- Plant recall: 5/5.
- Real items judged wrong after the fixes: 0/20. Minor: 3 before, 1 after (0026).
- Gate: PASS.
