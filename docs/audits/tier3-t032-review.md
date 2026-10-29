# Tier-3 review: packet t032 (28 items)

The batch has 40 texts: 14 charms, 13 healing narratives and 13 laments. A Sonnet planner wrote them (`tier3-planner-v4`). The packet held 20 real items, 5 plants and 3 Tier 1 fable lines (`--n 20 --plants 5 --tier1 3`).

The reviewer worked from handbook knowledge only (Fortson, Beekes, Ringe, LIV², Mallory & Adams, as remembered). Every packet token was checked against a reverse index of all admissible cells, built from `Lexicon.cells()`, `participle_cells()` and `closed_class.json`. Files:
- verdicts: `docs/audits/packets/t032-verdicts.jsonl`;
- blind translations: `docs/audits/packets/t032-blind-translations.jsonl`.

The grades follow the t021, t023 and t030 calibration:
- **wrong**: ungrammatical, or the meaning changes;
- **minor**: ablaut, accent, notation, or a stretched sense.

## Procedure and independence

The reviewer followed `reviewer-brief.md` (review-v1, 2026-10-28) in this order:
1. Built the packet.
2. Built the token→cell index. It prints lexicon glosses, not packet English.
3. Did the blind translation of 6 items, printing only their `pie` field.
4. Read the packet English and judged all 28 items.
5. **Saved the verdicts file** (sha256 `dc3476318ec60a53dbceb9778df9100c597babacfe2f809ab9064c5678dd6436`, which `resolve_review_items.py` also prints).
6. Only then ran `score_review.py`, ran `resolve_review_items.py`, and opened the plans and `corpus/tier3/t032.jsonl`.

The packet was never diffed against the corpus, and nothing under `data/audits/` was opened. **Plant recall is therefore blind: 5/5.**

## Counts

| set | ok | minor | wrong |
|-----|----|-------|-------|
| packet, all 28 | 16 | 7 | 5 |
| real items (20), before fixes | 16 | 4 | 0 |
| real items (20), after fixes | 19 | 1 | 0 |

The scorer reports:
- plant recall 5/5 (5 named);
- real wrong 0/20;
- no Tier 1 line judged wrong.

After the fixes, `realize_plans.py` gives:
- gate **PASS**, with 40/40 exact;
- max_lexeme_uses 6 against a cap of 6;
- meter_fit 154/160 (0.963), unchanged;
- 8 warnings, down from 10.

Outside the packet sample, two further real items are **wrong** and are now fixed (see below). One of them is the source record of a plant.

## Wrong

### Plants (5, all caught)

- **70236aa4**: `dyubʰós dóh₃r̥ h₁áydʰi` uses the dat./abl. *plural* of dyḗws for 'Give Dyeus a gift'. It needs dat. sg. diwéy.
- **0dcaf625**: `h₁yós gʰóstis dʰrugʰyéti` has a nominative gʰóstis, so it means 'the guest who deceives'. It needs acc. gʰóstim.
- **399341e0**: `péruti h₂uksté` uses a 2pl aorist for one brother. It needs 2sg h₂wéks.
- **7ebed750**: `bʰéh₂os sn̥gʷtā́m` puts a 3du aorist with a singular subject. It needs séngʷt.
- **b4da52de**: `pérkʷunos pérkʷum stunddʰí` puts the addressee of an imperative in the nominative. It needs vocative pérkʷune.

### Real, found through the plant item (1, fixed)

- **t032-0022**: this is the source of 70236aa4. The verdict on 70236aa4 also flagged `mē moy kʷim déh₃s`, which survives in the real record. Animate kʷim means 'do not give me *anyone*', but the English is 'Give me nothing'. The plan's `closed:indefinite_kwi` slot had no gender, so the realizer fell back to the m./f. form. **Fix:** `"gender": "n"`, which gives **kʷid**.

### Real, outside the packet (1, fixed)

- **t032-0015**: `ne kʷim h₁ḗdt` means 'he ate no one', where the English is 'He ate nothing'. This is the same missing-gender slot. **Fix:** `"gender": "n"`, which gives **ne kʷid h₁ḗdt**.

The other texts outside the packet were read through, and no further wrong item was found.

## Minor (real items)

- **7af1b125 (t032-0004)**: in `wódr̥ h₂nérm̥ swéh₂-kʷe h₃ésth₁h₂ gʷm̥dʰí`, the reflexive swo- points to the man, but the subject is the addressed water. **Fixed** to the anaphoric genitive: `h₁ésyo-kʷe h₃ésth₁h₂` 'and to his bones'. The English 'his own' became 'his'. Now ok.
- **2d036a96 (t032-0033)**: `h₁yód wĺ̥kʷos h₁ért h₁ím úd ǵʰéyt` has a null main-clause subject right after the wolf, so the line reads as 'the wolf drove him out'. The English means the dog drove the wolf out. The dog and wolf nouns are both at the cap of 6, and a pronoun cannot settle it, because both animals are masculine. **Fixed** with the noun from line 1: `ḱéywos h₁ím úd ǵʰéyt` 'the dear one drove it out', where line 1 already says `méne ḱéywos h₁ést`. The English changes to match. Now ok.
- **53d24214 (t032-0034)**: gʰósteyes 'guests, strangers' was rendered as 'enemies'. That is the Latin *hostis* development, not the PIE sense. **Fixed** in the English: 'The strangers arrived'. bʰoréyont, the iterative 'carry around', for 'carried off' is acceptable. Now ok.
- **db5b7ec5 (t032-0025)**: gʷā́m writes the Stang outcome of the 1sg root aorist. This is the same notation point as in t021, t023 and t030. It is engine-wide and was not changed.
- **Tier 1 lines.** Each follows its source faithfully, but its notation clashes with the corpus:
  - 195851d6 (Lühr 2008): h₂wlh₂néh₂, unmarked syllabic m, parenthesised (H) and (h₁);
  - 74d67fea (Schleicher 1868): no laryngeals, a-vocalism;
  - 2d7ad28b (Hirt 1939): ḱeḱruwos, owis, augmented ebʰuget.

The release file's record, plan and gate-report hashes were refreshed by the last re-realize, and its review status is still `pending`.

## Pronoun warnings (10)

All ten warnings were checked against the full text.

**Two were ambiguous and are fixed:**
- **t032-0002**, clause 5. In `nu h₁éy stéh₂t` 'then he stood up', h₁éy can be the god, who is the subject of the line before, or the horse, which appears only as the genitive in h₁éḱwosyo. The horse noun is at the cap. **Fix:** the clause is dropped. The line is now `nu h₃ésth₁ Hwérdʰt h₁ésh₂r̥-kʷe yungtó` 'Then the bone grew strong, and the blood was joined'. It is 8 syllables, so meter_fit is unchanged.
- **t032-0018**, clause 12. In `h₁ésmey h₁íd déh₃t` 'she gave it to him', the neuter h₁íd sits nearer to péh₂wr̥ 'fire', which 'vanished from him' in clause 7, than to wódr̥ 'water' in clause 1. The warning pointed at the IO slot; the real problem is the OBJ. The water noun is at the cap. **Fix:** `h₁ésmey médʰu déh₃t` 'She gave him mead'. médʰu is now at 6.

**Eight are unambiguous and were left:**
- 0015: h₁íh₂ is the wife, the only feminine referent.
- 0017: tóm … h₁yós wóyde is a correlative, a false positive.
- 0020: h₁ésmey is the horse, since the man is the subject.
- 0025: h₁ím is the guest.
- 0026: h₁íns is the horses.
- 0034: ḱód is 'this' for the whole event.
- 0040: h₁íns is the horses.
- 0018: the remaining IO h₁ésmey is the son.

One ambiguity that matters, t032-0033, raised **no** warning, because the wolf and the dog have the same gender (see Minor above).

## Charm meter claim (meter_fit 0.963)

The syllable counts are right: spot-checks by hand agree with `pie.meter.measure`. The claim is weak, though, because of what the metric measures.

- **The window.** `_meter` counts a line, meaning a sentence, as fitting when it is within ±1 of 8 or 11 syllables. That is any length from 7 to 12.
- **Every metered line is 6 to 12 syllables long:**

  | syllables | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
  |-----------|---|---|---|---|----|----|----|
  | lines     | 6 | 47 | 30 | 31 | 18 | 17 | 11 |

  Only the 6-syllable lines fail.
- **Exact hits are rare.** Only 47 of the 160 lines (0.29) have exactly 8 or 11 syllables: 0.32 of charm lines and 0.27 of lament lines.
- **The comparison genre.** Healing prose in the same batch, which the metric does not score, has lines of 1 to 21 syllables and would score 0.48.

So 0.963 shows that the planner keeps charm and lament sentences between 7 and 12 syllables. It is not evidence of gāyatrī or triṣṭubh meter: nothing checks cadence or quantity, and 9- and 10-syllable lines count as fits for either target. Reporting the exact-8/11 share next to the windowed share would make this visible.

## Blind back-translation

Six items were translated from the PIE alone: e08f54c7, 28d12a27, 5ee9ff8c, 74b671c5, 399341e0, 901230e1. **6/6 agree in substance** with the English. The differences:
- péruti was read as 'on the rock' (taken as locative of pérwr̥); it is 'last year' (Gk πέρυσι), the one lexical miss;
- 'kindled a fire' against 'the fire burned';
- 'seat' against 'dwelling' for sédos;
- 'know' against 'see' was resolved in favour of the English: widyéh₁t is the perfect optative of *woyd-.

The blind pass also flagged the 2pl h₂uksté in 399341e0, which turned out to be a plant.

## Engine and brief findings (for the lead; nothing in `pie/` was changed)

1. **The indefinite pronoun defaults to the animate gender.** A `closed:indefinite_kwi` slot without `gender` realizes as kʷim. That produced two real wrong items: 'nothing' came out as 'no one' in 0015 and 0022. Suggestion: have `check_plan` require an explicit gender on indefinite and interrogative slots, as it already effectively does for the interrogative.
2. **The antecedent warning tests only gender and number.** It misses same-gender ambiguity, such as wolf against dog (0033) or a nearer neuter (0018, where it flagged the wrong slot). It also fires on a correlative tóm … h₁yós (0017) and on the neuter 'this' for an event (0034). A check on the nearest earlier subject of the same gender would catch 0002, 0018 and 0033.
3. **No check on reflexive swo-.** A swo- whose referent is not the clause subject (0004) goes unflagged. So does the opposite case: in 0013, `pérkʷus h₁ésyo wr̥h₂déh₁` 'the oak by its root' uses non-reflexive h₁ésyo where the subject's own root calls for swéh₂. That item is outside the packet and minor, and was left unchanged.
4. **meter_fit's ±1 window** makes the score close to a test of line length (see above).
5. **gʷā́m notation** (Stang's law in the 1sg root aorist) recurs from batch to batch. It belongs to the engine or STATUS, not to plans.

## Assessment

The grammar is strong, and all five plants were gross single-cell errors. The two real errors share one cause: an underspecified closed-class slot. After the fixes, none of the 20 real items is wrong (0/20), and one is minor (a notation point).

The texts suit their genres:
- **Charms** use the classic types:
  - bone-to-bone and blood-to-blood (0002);
  - worm out of the bone (0001);
  - blood-stopping with a closed door and the threefold word (0003);
  - herd and thief protection;
  - the wool-grub fire charm, built on repetition (0012).
- **Healing narratives** use the healer–patient dialogue (0015, 0022) and a Merseburg-type horse cure (0020).
- **Laments** address the dead and use the formulas ḱléwos ń̥dʰgʷʰitom, ḱlutóm h₁nómn̥ and h₁wésu ḱléwos, along with the rhetorical 'who shall yoke / plough' questions.
