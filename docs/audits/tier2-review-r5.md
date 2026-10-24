# Tier 2 (back-projection) adversarial review, round 5

Reviewer: an independent "skeptical Indo-Europeanist" subagent, 2026-10-24.

## Scope

The scope is every plan whose review verdict is missing or stale. I found these by comparing `plan_sha()` (loaded from `scripts/build_tier2.py`) for each line in `data/tier2/plans/*.jsonl` with the `plan_sha` stored in `data/tier2/review_verdicts.json`.
- No line lacks a verdict.
- Eight lines are stale, all of them weak in round 4 and revised since: bp-gk-ita-001, bp-ii-gmc-001, bp-ii-ita-003, dawn-sun-009, dawn-sun-011, poetics-gifts-007, sky-father-002 and sky-father-011.

That is exactly the expected set; there are no others.

## Method

- Each plan was realized with `pie.realize.realize` after `check_plan`; all pass.
- I re-ran the builder's secure check (`checks_for` with `SecureChecker`) without writing any output.
- Every cited locus that has a local corpus was re-checked (`python3 -I`, read-only).

Machine-readable verdicts are in `data/tier2/review-r5.jsonl`.

Standards: the verdict scale and the three rules of round 4 (`tier2-review-r4.md` §0), unchanged.

Caveat: as before, this review was not plant-calibrated.

## 1. Verdicts

| id | PIE now | r4 | r5 | did the fix resolve r4? |
|---|---|---|---|---|
| bp-gk-ita-001 | diwéy ph₂tréy | weak | **sound** | Yes. The verb from the support ref is gone; the dative NP is exact in Gk and Umbr. |
| bp-ii-gmc-001 | priHóm h₁nómn̥ | weak | **sound** | Yes. Cut to the NP, as r4 proposed. Caveat: in OE the sense is 'cognomen'. |
| bp-ii-ita-003 | n̥mr̥tóns deywóns | weak | weak | Only the frame. Lat. immortalis is a new formation, the pair is near-universal, and the Plautus is adapted from Greek. |
| dawn-sun-009 | méǵh₂ sóh₂wl̥ | weak | weak (reject edge) | Only the case and the stale note. No member is exact in both branches, and the pair is generic. |
| dawn-sun-011 | sóh₂wl̥ spéḱm̥ | weak | weak (reject edge) | Only the case and the stale note. Both heads are formation- or root-level. |
| poetics-gifts-007 | h₁uséwōm dh₃téres | weak | **sound** | Yes. The agent noun is now suffix-accented and 'gods' is dropped. There are caveats on root ablaut. |
| sky-father-002 | dyḗws moy ph₂tḗr pl̥th₂éwih₂-kʷe moy méh₂tēr | weak | weak | The uncited 'our' leak is fixed. The rest of r4 stands, including P6. |
| sky-father-011 | dyḗws ph₂tḗr ǵenh₁tḗr | weak | weak | Two of three. The stitched genitive and the accent are fixed; Catullus is still the only second branch. |

**Totals: 3 sound, 5 weak, 0 reject.** Three lines go up (weak to sound). None goes down.

## 2. Findings

1. **The fixes split into two kinds.**
   - **Substantive fixes.** In three lines the revision removed exactly what round 4 objected to, and each line now meets the head rule with exact or formation-level heads in two branches.
     - bp-gk-ita-001: the causative from Lat. voveō (support only) is gone.
     - bp-ii-gmc-001: the stitched verb and 'begot' are gone.
     - poetics-gifts-007: the root-accented déh₃tores and the interpolated θεοί are gone.
   - **Mechanical fixes.** In four lines the revision corrected the case, the frame or a stale note, but the round-4 verdict rested on facts a plan cannot change:
     - formation-level heads (dawn-009, dawn-011);
     - a renewed Latin formation (bp-ii-ita-003);
     - a derivative only witness (sky-011).

     These stay weak. Their notes now say so honestly.
2. **The builder's round-4 false positives are fixed.**
   - mahát, sū́rya- and svar now carry `erratum:` tags in the evidence path. The builder gives mahát and sū́rya- level root, and *sóh₂wl̥ gets level none in dawn-009 and -011.
   - The builder's levels now agree with round 4's reading.
   - **One false negative remains.** pie-lex-dh3texr (poetics-007) gets level none:
     - Av. dātar- routes to *déh₃tōr;
     - Gk δωτήρ and Ved. dātár- reach no suffix-accented id.

     The head is in fact shared, as the same agent-noun formation, in all three branches.
   - pie-lex-gjenh1texr (sky-011) gets root for Lat. genitor, also a false negative of the same kind.
3. **Engine forms against the cells.**
   - **Corrected:** ǵenh₁tḗr = janitā́, and dh₃téres has the oxytone accent of δωτῆρες and dātā́.
   - **Still open:**
     - pl̥th₂éwih₂ against Ved. pr̥thivī́ (sky-002, P6).
     - Oxytone n̥mr̥tóns against Ved. amŕ̥tān (bp-ii-ita-003).
     - The base heteroclite sóh₂wl̥, which stands in no cited cell (dawn-009, -011). sū́rya- and ἠέλιος are derivatives. Ved. svàr's zero-grade root is levelled ablaut, the same caveat accepted for Umbr. Iuve, and does not count against the line.
     - In sky-011, Lat. genitor has the agent-noun suffix but cannot show which accent type it continues, because Latin generalized -tor-.
     - Zero-grade dh₃- and proterokinetic h₁uséwōm in poetics-007. The cited cells have the full grade and root accent (δωτῆρες, dātā́, vásūnām, vohunąm; Hoffmann's *h₁wéswōm for ἑάων). Both forms are the handbook ones: NIL has *dh₃-tér-, and Greek attests the zero grade in δοτῆρες (Il. 19.44, uncited). I count them as levelling in the daughters, not as a contradicting type, so they are caveats here, unlike round 4's déh₃tores.
4. **The engine always puts MOD and POSS before the head** (systematic; no verdict changes on it). Both daughters have noun before adjective in:
   - dawn-009: svàr mahát, Ἠέλιόν … μέγαν;
   - bp-ii-ita-003: devā́n … amŕ̥tān, deos inmortalis.

   The engine prints adjective first in both. A plan has no way to ask for the postposed order except through APPOS, which changes the meaning ('the immortal ones'). This is the handbook default order (Fortson), but it overrides agreeing daughters, against the brief's "prefer what the branches agree on".
5. **Stale "not in local corpora" claims (r2 P10, fourth round running).** Both are in support refs, so no verdict changes:
   - bp-ii-gmc-001 says the OE Bede is not local. It is: `oe-bibliothek-ags-prosa`, Bibliothek der ags. Prosa IV, has "wæs his freonama Oesc", Bede 2.5.
   - sky-father-002 says Varro RR 1.1.5 is not local. It is: `latin-ogl-latin` phi0684.phi002 has "Iuppiter pater appellatur, Tellus terra mater".
6. **A better parallel for sky-father-011 is available locally.** West ch. 2 names the pitā́ janitā́ 'father begetter' pair. Its witnesses:
   - Av. Y. 44.3 ząθā ptā (CAB);
   - Eur. Ion 136 Φοῖβός μοι γενέτωρ πατήρ (glaux 0006-010; note the enclitic μοι, as in RV 1.164.33 dyaúr me pitā́ janitā́);
   - Enn. Ann. 113 Vahlen (= 108 Sk.) o pater o genitor. It is local in Vahlen. Cicero's text has genitor; most Lactantius manuscripts lack it (add. Pal.).

   None is of Dyaus. A line *ph₂tḗr ǵenh₁tḗr on these loci would be a three-branch sound candidate. As it stands, sky-011 rests on Catullus alone.
7. **Small role and construal points.**
   - bp-gk-ita-001: Cato Agr. 134.1 (Ioui only) is marked parallel. It is the only path by which the builder credits *dyḗws to Italic, because Umbr. Iuve has no table key. The fix is that key, then demote Cato to support.
   - poetics-007: Y. 65.12 is an address to the Aməṣ̌a Spəṇtas (nom. = voc. pl.).
   - sky-002: the -kʷe has no counterpart in the asyndetic RV 1.164.33.
   - bp-ii-gmc-001: in Crist 636, Grein's Sprachschatz files cende under cennan 2 'creare, facere' and freó-nama as 'cognomen'.
8. **Loci.** Every cited locus with a local corpus contains the cited words; no fabricated attestation was found. Checked:
   - VedaWeb: RV 3.2.7, 2.23.2, 4.13.3, 1.164.33, 1.89.4, 4.1.10, 1.185.6, 10.84.5, 10.123.7, 7.56.10, 10.65.15 (= 10.66.15), 3.4.11, 8.51.5.
   - AGDT: Il. 17.498, 24.287-288; Od. 13.51, 8.325, 8.335; Il. 19.44.
   - glaux: Hes. Th. 19; Hymn. Dem. 62; Eur. Ion 136.
   - CAB: Y. 65.12, 44.3.
   - Buck OCR: Tab. Ig. IIb 7, 17-18, 21-23, 24, 26, and the glossary.
   - LASLA: Cato Agr. 134.1, Orig. 4 fr. 7; Catull. 64.26-27; Lucr. 1.250-251; Plaut. Amph. 1093.
   - Grein: Crist 636 and its apparatus (manuscript reading; no note on 636).
   - Prosa-Bibliothek: OE Bede.
   - OGL: Varro RR 1.1.5.
   - Vahlen: Enn. Ann. 113.

   Not local (confirmed by search): the Æcerbot, in Grein, Sweet and Bright.
