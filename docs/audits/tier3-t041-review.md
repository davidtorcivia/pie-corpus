# Tier-3 review: batch t041 (packet of 28 items; all 40 records read)

Batch: myths of death and the otherworld, laments, genealogies. Reviewer brief `review-v1`, planner brief v4.

## Counts

| | before fixes | after fixes |
|---|---|---|
| Plant recall | 5/5 (all named) | — |
| Tier 1 judged wrong | 0/3 | — |
| Real packet items judged wrong | 0/20 | 0/20 |
| Real packet items judged minor | 8/20 | 3/20 (122accf6/0004, 4ff015bf/0017, 83225b45/0026: gnomic aorists of aorist-only verbs under an English present; §8 allows them, kept as minor for the record) |
| Real wrong, second pass over all 40 records | 3 records + 8 mislabelled genres | 0 |
| Gate | PASS (no metered texts: `meter_exact` null) | PASS, `meter_exact` 69/69 = 1.00 |

- The verdicts file `docs/audits/packets/t041-verdicts.jsonl` was saved before corpus/ or the plans were opened.
  Its sha256 is `775137fe92e1acf031ce9b403c94fa18b3bce2ef4e80bc5c1c0bdc89178eaa2c`.
- `score_review.py` returned plant_recall 1.0, real_wrong 0, real_minor 8.
- The five plants I caught were all person, number or case errors:
  - h₁ésesi 2SG with h₁eǵóh₂;
  - ménetes 2/3DU with wéy;
  - ǵʰéwete 2PL with kʷís;
  - h₁uséwōm GEN.PL as the object of 'give';
  - m̥dʰéws GEN as the object of 'drink'.

## Blind back-translation (6 items)

I translated these from the `pie` field alone, before reading any English.
- **Agree (5/6):** 83225b45, dd296cc6, 783f8e8a, 261b6a66, 52f9e1b4.
  The only uncertainties were small: ḱérh₂sones 'heads/hair', h₁áyih₁ro 'receive', gʷʰénm̥.
- **d7faf5d2:** the blind pass flagged ǵʰéwete as 2PL where the sense is 'who will pour', i.e. the plant. Otherwise it agrees.

## Wrong, second pass (fixed in the plan file)

1. **t041-0039 (anachronism).** "Bright-Mind carved the words" (wékʷesh₂ péyḱt, theme `inscription`) means writing.
   Writing has no inherited word: it is one of the 3b neologism concepts.
   - Fix: dropped the clause and its English; the theme is now `memorial stone`. Setting up the stone stays.
2. **t041-0032 (genealogy; packet item 4a2a80a6, which I judged minor in the packet and upgraded to wrong in the second pass because genealogical consistency is an explicit check).** The text said "No son was born to Wolf-Fame; his grandson ruled after him."
   - Fix: the English now says "his nephew". The PIE népōts already covers that sense (gloss: grandson; descendant; nephew).
   - The rest of the line checks: First-Fame → Swift-Mind → Wolf-Fame → (nephew) Divine-Horses → his grandson.
3. **t041-0013 (English ≠ PIE).** Clause 6 said "gather them and burn them with fire", but the burning was realized in a
   later sentence that the English labelled "wash them with milk".
   - Fix: re-split as gather + wash / burn / put under a stone / pour, with matching clause English.

## Genre labels (fixed)

The planner had filed four laments (0011, 0012, 0013, 0020) as `death-otherworld` with a theme `lament`, to stay
out of the meter gate.
- **Laments:** all four are now `lament`, and the `lament` theme tag is removed.
- **Prayers:** I applied the same test to every other text: a second-person address to a god or to the dead, with
  imperative or optative requests, is a metered genre. Three funeral liturgies fail it:
  - 0014 "Go Forth on the Old Paths" (RV 10.14.7–8 type);
  - 0015 "Words at the Grave" (RV 10.18 type: "Earth, receive this dead man… may we live and see the sun");
  - 0016 "The Feast of the Fathers" (an invocation of the Pitṛs: "come… drink… give us sons… go below").

  All three are now `prayer`.
- **Proverb:** 0021 "What Does Not Die" (Hávamál 76 type) is gnomic and is now `proverb` (not metered).
- **Kept as `death-otherworld`:** 0003 (dogs of death) and 0004 (the ferryman). Both are mostly description; their
  imperatives come inside a narrative frame.

**Meter.** Before the fixes, 16 of the 65 verse lines in these 7 texts were exact. After the fixes all 69 are exact
(some lines were split or merged). I re-ran `meter_report.py` until it listed no misses, then re-read every changed
line against its English. The edits were:
- added or dropped nu, -ge and -kʷe;
- split or merged sentences;
- added an epithet, an adverb or a vocative, with the English updated to match. Examples: "sweet milk", "a new white
  garment", "Dark Death", "We, the living", "in peace", "by which our former fathers went" (RV pū́rve pitáraḥ);
- dropped a few redundant possessors (e.g. "the bed is cold").

My first meter pass broke the lexeme cap: ph₂tḗr reached 13 uses, and dʰéǵʰōm and méh₂tēr 12 each. I rebalanced the
lines, and the final max_lexeme_uses is 11, at the cap of 11.

## Other fixes made while re-realizing

- **Reflexive possession.** The anaphoric h₁ésyo was used for the subject's own, where brief §19 asks for swos. I
  converted the five places where it was ambiguous:
  - 0035 "gave his daughter to Swift-Mind": h₁ésyo could have meant Swift-Mind's daughter;
  - 0028 "the boy asked his uncle";
  - 0026 "receives the dead in his house";
  - 0039 "set up for his parent";
  - 0004 "teaches his boy".
- **Present for a habitual 'pour'.** 0009 and 0030 had used the aorist-only ǵʰéwt. They now use the present stem
  ǵʰéweti.
- **"The youngest".** 0037 had the positive h₂yuHn̥ḱéh₂, so the English now says "The young one" (the -ḱo- adjective
  has no superlative).

## Minor, left as is

- **Leftover reflexives.** About 14 more places use h₁ésyo/h₁ésyeh₂s for the subject's own (e.g. 0006 "led his
  wife", 0018 "his hands", 0023 "his father"). None is ambiguous in context. I did not convert them because swos is
  already at the cap of 11 (see engine/brief notes).
- **Gnomic aorists.** Aorist-only verbs appear under an English present: h₁áyto 'takes, receives' (0004, 0026);
  ḱéHst 'teaches'; ǵnéh₃t 'meets' and pért 'crosses' (0017). Brief §8 allows this.
- **Other packet minors:**
  - 783f8e8a (somHóh₁ 'alone') is within the gloss.
  - 261b6a66 gʷʰénm̥ is PST because gʷʰen- has no aorist, which is correct by §8.
  - In cb0e6c48, téh₂ is followed by an apposed népotn̥s; an apposed noun keeps its own gender, so this is by design.

## Sense checks (lexq words)

Every out-of-slice sense fits its gloss:
- dʰegʷʰh₂- 'pass by';
- Hyowdʰéye- 'cause to move';
- h₃meyǵʰ- 'urinate';
- tewtéh₂ 'heap';
- stéh₂dʰh₁om 'herd';
- kʷih₁tí- 'peace';
- h₁ewk- 'learn';
- peyḱ- 'carve';
- seykʷ- 'pour out'.

Causatives are used correctly: stoh₂éye-, woséye-, logʰéye-, lowkéye-.

Fearing takes the ablative: témHesos mē bʰéyh₂s, tóybʰos mē bʰéyh₂s.

The only flagged tokens are two project reconstructions (`coined: project`), which brief v4 allows: mógʰus and h₂énHos.

## Engine / brief issues (report only)

1. **swos counts against the per-lexeme cap.** A batch about lineage needs "his own" constantly, so the reflexive
   possessive hits the cap of 11. That pushes planners back to the non-reflexive h₁ésyo, against §19. The lead should
   consider exempting swos (like the copula) or giving it the theme-core cap.
2. **Name reuse across texts.** Each text is consistent on its own, but the batch is not:
   - Kindly is a mother in 0007 and a man in 0023, 0029 and 0039;
   - the serpent-slayer is Divine-Race in 0024 but First-Fame in 0032;
   - Good-Path is a dead forebear in 0029 but alive in 0030.

   The brief could ask planners to keep one bearer per name within a batch.
3. **The meter-gate dodge.** The planner gave metered texts a non-metered genre to avoid the gate. The brief (or the
   realizer) should tie the genre to form, e.g. a `lament` theme ⇒ genre `lament`, so the dodge is caught
   automatically.

## Assessment

- Plant recall is 5/5.
- Real packet wrong is 0/20, both before and after the fixes.
- The final gate PASSES:
  - reject 0;
  - max_lexeme_uses 11 (cap 11);
  - meter_exact 1.00 over 69 lines;
  - 50.2 words per record.
- Release approval is left to the lead. Nothing has been committed.
