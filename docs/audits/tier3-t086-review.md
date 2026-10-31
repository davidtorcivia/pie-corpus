# Tier 3 review: t086 (Horrors wave, feud and blood-price)

Reviewer: calibrated reviewer (claude-opus-5-5), brief `review-v1`, 2026-10-31.
Packet: 28 items (20 real, 5 planted, 3 Tier 1), `docs/audits/packets/t086-packet.jsonl`.
Verdicts file: `docs/audits/packets/t086-verdicts.jsonl`, sha256
`934c0bb95da5b425c7aa7e028484576842217ef22393d572693ec4cd799ba763`. I saved it before opening corpus/ or the plans.

## Calibration (score_review.py)

| | |
|---|---|
| Plant recall | **4/5** (all 4 named) |
| Real items judged wrong | 1/20 (0.05; upper 0.062) |
| Real items judged minor | 0/20 |
| Tier 1 judged wrong | 0/3 |

Plants caught: 8173d202 (ph₂teres VOC.PL as subject), 26d2ded4 (h₁áyn̥to 3PL with singular kʷis), 36e46337
(bʰugyéh₁s OPT.2SG with a 3PL subject), c4e8ba5c (kʷoynéh₂h₁ INS for the ACC object, caught as minor).
Plant missed: f8291dc2, `mḗmsh₂` for `mḗms` 'flesh', the object of neuter sweh₂dú. I read past it.

## Blind back-translation (6 items, PIE only)

`docs/audits/packets/t086-blind-translations.jsonl`. Five of the six agree with the English in substance (26d2ded4,
5385c829, 2dee8886, 7157b7ca, 82062981). The differences come from my own uncertainty, not from errors:
- ḱlḗm I read as 'I declare'. It is ḱlew- AOR.1SG 'I have heard', which matches the English.
- pyéh₂t I read as 'insulted'. The lexicon gloss is 'strike'.
- In d575e975 I read h₃épnos correctly as 'wealth, goods'.

None of the six items was seen in English beforehand.

## Packet verdicts on real items

- **wrong, 93c7395a = t3-t086-00009** "Ten horses and a hundred sheep." This is a fragment answer to *kʷíd déh₃esi?*
  'what will you give?', but it was realized in the nominative (déḱm̥ h₁éḱwōs ḱm̥tóm-kʷe h₂óweyes). It needs the
  accusative of the object it answers. **Fix:** in the plan, `"case": "ACC"` on the np clause, giving
  déḱm̥ h₁éḱwons ḱm̥tóm-kʷe h₂ówins.
- **minor, Tier 1 befe5ed8** (Byrd, King and God): h₃réḱs, where Byrd prints h₃rḗǵs. This is a notation or
  normalization matter. Not a plan error; no fix.

## Second pass: all 40 records against planner-brief-v4 and the Horrors section

**Fixed at the source (plan edits, then re-realized):**
1. **t086-0009 (wrong):** the np answer was nominative. Fixed as above.
2. **t086-0002 (minor):** "He will ask a hundred cows as blood-price" was realized with the instrumental
   kʷoynéh₂h₁ (the 'as blood-price' work-around). PIE has no clear instrumental of role 'as X', so the PIE did not
   say what the English says.
   - First attempt: APPOS. It failed: the APPOS took its head's number (kʷoynā́s ACC.PL). With kʷoynéh₂ as OBJ and
     the cows as APPOS, it gave gʷṓm SG even with `num: PL` set (see engine notes below).
   - Final: two clauses. *ḱm̥tóm gʷṓs préḱseti. tód kʷoynéh₂.* "He will ask a hundred cows. That is the blood-price."
3. **t086-0022 (minor):** ǵorh₂éyonto 'they grew old'. The gloss of ǵorh₂éyeti is causative only ('to cause to grow
   old, mature'), so by the causative rule it should not be used for the plain sense. Replaced by a coordinated
   predicate: *gʷénh₂es h₁widʰéwh₂es séneh₂es-kʷe bʰuHént* "The women became widows and grew old" (sénos PRED,
   gender f, num PL; the feminine is correct).

**Checked and correct:**
- **kʷéyeti** is middle wherever it means 'take vengeance': kʷéyeso, kʷéyōh₂er, kʷéyoh₂e, kʷéyōntor. It is active
  only for the gods' 'punish' in 0029 (kʷéyontu), which matches the active gloss.
- **kʷoynéh₂ 'devoured'** (0007, 0023, 0033, 0034): it stands for 'vengeance', and the full gloss includes
  "punishment, vengeance".
- **h₂éwh₂os** is used for both "mother's father" and "mother's brother" (0006, 0007). The gloss covers both senses.
- **ḱóymos** is used as the adjective 'kin' in 0037: "household dogs", and "kinsman" as a noun. This is supported.
- **h₃nóbʰis** is feminine; swéh₂ey in 0021 agrees with it.
- **Laws** (0027–0031) follow the form 'whoever / if …, let him …': h₁yós/h₁yód + subjunctive, then an
  imperative in -tu or mē + injunctive. h₁yód 'because' in 0028 is the sanctioned idiom.
- **Curses** (0037–0040, 0016 clause 6) are all optatives; mē is used with wishes. The 39 curse has the correct
  bʰugih₁ént.
- **No courts or states:** the elder or the assembly decides (dʰh₁tléh₂ 'assembly' in 0006 and 0026; h₂réh₁dʰ- in
  0026 and 0029). The judge is always ǵérh₂ont 'elder'. Witness and accept/refuse are expressed with h₁ayt- MID
  'take' and ne.
- **Predicate adjectives and pronouns:** luǵréh₂ in 0036 is feminine. somHós is masculine and matches the speakers:
  the old man in 0007 and the planned male speaker in 0034. Pronouns track slayer, slain and kin throughout.
- **Meter:** all 56 metered lines are exact (8 and 11 syllables).
- **Athematic obliques** are correct: gʷʰn̥trés, n̥ḱéws, h₁widʰwéh₂ey, déms, nókʷtn̥s.
- **Enclitics** sit in Wackernagel position.
- **Turns:** every dialogue turn answers the one before; speakers and per-sentence English are correct.

**Left as minor (no fix):**
- 0019 ǵʰéwt and 0017 ḱluwént are gnomic aorists rendered with an English present.
- Some English 'but' / 'and' has no particle in the PIE (0012, 0018, 0026).

**Horrors limits:**
- No sexual violence.
- No gore beyond plain facts ("his blood poured out among the cups", "your blood lies on my hands").
- No modern moral commentary. The closest are the proverbial lines *kʷoynéh₂ kruh₂sés h₁wésyōs* "a price is better
  than blood" (0019) and *ḱéh₂dos ne wósn̥* "grief is not a trade" (0031). Both are in-world, said by an elder and
  a law.
- No coinages.

**Violations:** none.

## Real wrong/minor counts

| | wrong | minor |
|---|---|---|
| Packet, before fixes | 1/20 | 0/20 |
| Packet, after fixes | 0/20 | 0/20 |
| Full batch, before | 1 (0009) | 2 fixed (0002, 0022) plus a few stylistic ones |
| Full batch, after | 0 | stylistic only |

## Gate after re-realization

PASS: 40/40 exact, reject 0.0, max_lexeme_uses 8 (≤8), tokens 1506, meter_exact 56/56, duplicates 0.
accent_defect_tokens = 2, the same as before my edits.

## Engine / brief notes (report only)

- An APPOS slot always takes its head's number and ignores an explicit `num` (a hundred cows in apposition to
  SG kʷoynéh₂ came out gʷṓm). Plural apposition to a singular head ('the price, a hundred cows') cannot be
  expressed.
- A fragment (np) answer defaults to NOM. The planner brief could say that an answer takes the case of the
  constituent it answers ("case": "ACC").
- The lexicon has no plain intransitive 'grow old' (only causative ǵorh₂éyeti).

## Tone

The batch lands its tone. It covers grief, duty and the cost of the feud, told plainly and in-world: the widow
refusing sheep, the grandfather alone at the door, the feud that "devoured two houses".
