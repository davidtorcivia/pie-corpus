# Tier-3 review: t011 (hymns, prayers, charms)

Reviewer: an Indo-Europeanist reading for the project. I used handbook knowledge only (Fortson, Ringe, Beekes, Meier-Brügger, LIV-style root shapes) and did no browsing. I checked forms against the project lexicon and engine cells, and ran `pie/validate.py` for lemmatization. Every clause was then checked by hand: subject against verb, English roles against PIE case, and relative-pronoun gender against its referent.

Verdicts: `docs/audits/packets/t011-verdicts.jsonl`.

## Counts (28 items)

| verdict | n |
|---|---|
| ok | 15 |
| minor | 9 |
| wrong | 4 |

Three items are versions of Schleicher's fable, not engine hymns, and I judged them as reconstructions:
- b747a1a0 is in older, pre-laryngeal notation and is fine.
- ebafd1f5 and 1059b4c4 are both minor, because they are internally inconsistent in notation, laryngeals and verb number.

## Recurring patterns

1. **An oblique plural used for a nominative or vocative.** These are the most serious errors.
   - 61c861af: the address "Gods, ..." uses dat./abl. pl. `deywóybʰos`.
   - 57556ec6: "Dawn will come" uses dat./abl. pl. `h₂usbʰós` as the subject.
   - 7a288fcb: `stóygʰoh₁` (ins. sg or dual) stands for "the way" (acc. sg).
   - 8e79a2dc (minor): acc. pl. `dʰéǵʰomn̥s` stands for "the earth".
2. **Verb person does not match the subject.** da3b7fb6 has "light came" with 2sg `h₁ludʰés`. In a 2sg hymn this is easy to produce: the engine keeps the addressee's person on a clause with a new 3sg subject.
3. **Neuter plural subjects take plural verbs, against the corpus's own convention.** In 1dc8b06f, ad4ad658 and 41ce2964, `wódr̥h₂` takes a 3pl verb. 2e8047e7 correctly has the singular (`wódr̥h₂ mē n̥ḱyéh₁t`).
4. **Neuter addressees are inflected as if masculine.** Fire is handled correctly (`péh₂wr̥ h₁yód ...`, 1dc8b06f). Elsewhere:
   - 1a191d9f: the Sun gets masc. relative `h₁yós`.
   - 41ce2964: the Sea gets masc. predicate `méǵh₂s`.
   - 656f205d: "Poison" gets an `-e` vocative (`wíse`).
   - 57556ec6: "Heart" gets vocative `ḱérd`, which is also the non-standard nom./acc. noted in t009.
5. **Laryngeal and spelling issues.**
   - bb35df7d: `h₂éryomes` lacks the h₃ of *h₂erh₃- "plough".
   - The two Schleicher versions drop or vary laryngeals (`agʰnutór`, `h₂wlnéh₂m` / `h₂wlh₂néh₂`).

These I noted but did not penalize:
- *mē* with the optative in negative wishes (751f68e0, 2e8047e7). The Greek type supports it, though the prohibitive proper takes the injunctive (853a245c, 656f205d).
- An overt god as subject of "rain" (a56c0b09 `túH ... h₂wérs`), which is fine in address.
- Impersonal `h₂ur̥syéh₁t` in 2e8047e7, which is correctly subjectless.

## View of the texts

The hymnic idiom is good and recognizably Vedic and Homeric:
- vocative openings with accent retraction (`pérkune`, `léwkeh₂ h₂éwsos`, `dyéw ph₂ter`)
- anaphoric relative predications (`h₁yós ... -si, h₁yós ... -si`, `h₁yéh₂ ...`), the *yó* "you who" style, applied consistently in 2sg
- aorist "you came, you slew" praise followed by imperative or optative petitions (`ḱludʰí`, `dh₃dʰí`, `h₁áydʰi`, `ph₂sdʰí`, `h₂ur̥sdʰí`)

It uses real inherited collocations:
- `h₁uséwōm déh₃tōr`
- Dawn as daughter of Sky
- Perkʷunos freeing the waters (`wódr̥h₂ spérs`)
- `ḱléwos ń̥dʰgʷʰitom`
- `dyéwmn̥` (Ved. dyumná-)
- perfects such as `dedwóye`, `dedórḱe`, `ǵeǵn̥h₁é`, `tetl̥h₂dʰí` (Hom. τέτλαθι)

The charms (656f205d, 57556ec6, 853a245c) have the right compact imperative shape.

These short texts carry more errors per word than the epics, because each one is dense with addressee-person shifts and neuter divine names. The fixes needed in the realizer:
- carry gender agreement from the addressee noun through relatives and predicates
- re-check verb person when a 3rd-person subject appears inside a 2sg hymn
- enforce the neuter-plural-singular-verb rule
