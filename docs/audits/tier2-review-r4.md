# Tier 2 (back-projection) adversarial review, round 4

Reviewer: an independent "skeptical Indo-Europeanist" subagent, 2026-10-24.

Scope: 25 lines.
- 11 new branch-pair lines (`bp-*`).
- 11 lines converted from a copula workaround to the new verbless clause types (`"type": "nominal"`, `"np"`, role `APPOS`). They are: dawn-sun-009, -011, -017, -019; epic-diction-003, -004; fame-015; poetics-gifts-007; sky-father-002, -009, -011.
- 3 converted lines that round 2 had rejected: fame-012, sky-father-010, poetics-gifts-002. These have no built record, so I realized them with `pie.realize.realize`. All three plans pass `check_plan`.

Sources:
- I read the plans in `data/tier2/plans/` and the built records in `corpus/tier2/`, including pie, gloss, secure_checks and notes.
- Every locus that has a local corpus was checked there (`python3 -I`, read-only).
- Machine-readable verdicts are in `data/tier2/review-r4.jsonl`.

Caveat: as in rounds 2 and 3, this review was not plant-calibrated.

## 0. Rules as applied

The verdict scale is round 2's (`tier2-review-r2.md`), unchanged:
- **sound:** the head is shared in two branches in the same formation, and the line is not generic.
- **weak:** a real parallel that is overclaimed. Typical causes are a head shared only at root level, a frame larger than the core, a generic pair, a support ref leaking into the output, or a contradicted engine form.
- **reject:** one of:
  - the only shared items are periphery, or only root-level material with non-cognate heads;
  - a commonplace with no scholarly claim of inheritance;
  - a misconstrual.

Three rules were stated once and applied the same way to every line:

1. **The head rule for verbless lines.** The head is the noun in the NP slot (np clauses) or the predicate noun (nominal clauses).
   - If that noun is interpolated (no cognate in a parallel ref), the APPOS or POSS phrase must itself be a secure head plus dependent. Otherwise the line has only periphery and is rejected.
   - poetics-gifts-007 passes: 'gods' is interpolated, but 'givers of goods' is shared in three branches.
   - dawn-sun-017 and sky-father-009 fail: the NP head is interpolated and the APPOS head is root-level only.
2. **Formation against root level.** A difference of tense or aspect category counts as root-level: imperfect against aorist subjunctive against participle (bp-east-001). Different present-stem types of the same compound lexeme, all in the present, count as formation-level with a caveat (bp-ii-ita-001: reduplicated against thematized *ḱred-dʰh₁-).
3. **Late and derivative witnesses** can carry wording but not an independent branch when they are probably derived. Macrobius is not counted as Italic for dawn-sun-017, and Lucretius' Greek topos not for sky-father-002. When the line also stands without such a witness, it is only a caveat. Flagged witnesses:
   - Vuk (19th c.; the naming is a baptism)
   - Eznik (5th-c. Christian polemic)
   - Rhesa's dainos (19th c.)
   - the Slovo (authenticity disputed)
   - MBh 3.158 (post-Vedic)
   - Crist 636 (Christian)
   - Æcerbot (Christianized charm, not local)
   - Wb. 18c11 (a gloss on Galatians)
   - Plautus (adapted from Greek comedy)
   - Lucretius and Catullus 64 (Greek models)
   - Macrobius (5th c. CE)

## 1. Verdicts

| id | verdict | core | deciding fact |
|---|---|---|---|
| bp-east-001 | weak | *h₁nómn̥ dʰeh₁- + dat. | Object exact in Arm/Gk/Ved; verb root-level only (impf., -nǫ- pf., aor. subj. mid., -tá- ptc.). |
| bp-east-002 | weak | *bʰréh₂tēr bʰréh₂trey | One kin noun in a commonplace polyptoton; verb interpolated and non-cognate; Slovo and MBh are late. |
| bp-east-003 | weak | *diwés suHnús | Head exact only in Vedic (υἱός is *suH-iu-, a builder false positive; Lith. diminutive); referents differ. |
| bp-gk-gmc-001 | weak | *wékʷesh₁ wérǵoh₁-kʷe | West reconstructs it, but each member is exact in only one other branch; generic merism. |
| bp-gk-gmc-002 | **sound** | *méh₂tr̥s ǵónuh₂ | Hes. Th. 460 = Sigurðarkviða skamma 45/46; both nouns exact; specific birth idiom (West). |
| bp-gk-ita-001 | weak | *diwéy ph₂tréy | The dative NP is exact. The verb is not shared: the Umbrian vufru is an adjective, and the causative comes from a support ref (Lat. voveō). |
| bp-ii-gmc-001 | weak | *priHóm h₁nómn̥ | NP equation sound (Scheller, Schmitt). Verb stitched from a plural-object stanza; in Crist 636 cende means 'proclaimed'. |
| bp-ii-gmc-002 | **reject** | *wid- 2pl | Only 'know' is shared, in non-parallel passages (incipit against refrain); the vocative is stitched from Vǫluspá 1 and root-level. |
| bp-ii-ita-001 | **sound** | *ḱreddʰh₁té + dat. | The compound is exact in Ved/Lat/OIr, all present stems; dative construction shared. |
| bp-ii-ita-002 | weak | *deywṓm deywós | Exact in both branches, but a productive, widespread figure; the Latin is one fragmentary line quoted by Varro. |
| bp-ii-ita-003 | weak | *deywóns n̥mr̥tóns | Lat. immortalis is a new formation; verb interpolated; near-universal pair. |
| dawn-sun-009 | weak | *méǵh₂ sóh₂wl̥ | At the reject edge. Generic; both members formation-level in Greek (mahát is the nt-stem, a false positive). |
| dawn-sun-011 | weak | *sóh₂wl̥, *spéḱs | APPOS is faithful, but both heads are root- or formation-level (sū́rya-, ἠέλιος, σκοπός). |
| dawn-sun-017 | **reject** | *diwés h₃ókʷ | NP head 'Sun' interpolated; 'eye' root-level; the Latin is Macrobius. Only *diwés is shared. |
| dawn-sun-019 | **reject** | *sh₂wéns gʷówes | RV 7.36.1 has the Sun as subject releasing the cows (rays): no 'cattle of the Sun' there. |
| epic-diction-003 | **sound** | *sweh₂dú médʰu | Ved/Gk exact; OE conjecture now support only (r3 fix applied). |
| epic-diction-004 | weak | *h₁éḱwōs n̥mr̥tṓs | APPOS matches both texts; generic pair (P5), as in r3. |
| fame-012 | **reject** | *h₁nómn̥ ḱlutóm | The nominal sentence misreads Od. 19.183 (the predicate is Αἴθων); the Vedic has nā́ma adverbial. |
| fame-015 | **sound** | *h₁suḱléwēs | Compound equation; builder now credits it; np is a good choice. |
| poetics-gifts-002 | **reject** | *wékʷesōm tétḱones | The NP stands in no text (Pyth. 3.113 ἐξ ἐπέων); head root-level. |
| poetics-gifts-007 | weak | *h₁uséwōm déh₃tores | Genuine three-branch formula; the engine's root accent is contradicted by every cited cell; 'gods' interpolated. |
| sky-father-002 | weak | *dyḗws ph₂tḗr / méh₂tēr | Kin terms only outside Vedic; Lucretius is derivative; pl̥th₂éwih₂ still wrong (P6). |
| sky-father-009 | **reject** | *h₂strṓm péyḱos | NP head 'heaven' interpolated; root-level throughout; only 'stars' exact. |
| sky-father-010 | **reject** | *diwés népoth₁e | Head népōts is Vedic only; only *diwés is shared. |
| sky-father-011 | weak | *dyḗws ph₂tḗr ǵénh₁tōr | Core is real (RV 4.1.10 ~ Catull. 64.27), but 'of the gods' is stitched from RV 1.185.6; the accent contradicts Ved. janitā́. |

**Totals: 4 sound, 14 weak, 7 reject.**

The 11 bp-* lines: 2 sound, 8 weak, 1 reject. The 14 converted lines: 2 sound, 6 weak, 6 reject.

**Against earlier verdicts** (`data/tier2/review_verdicts.json`):
- **Unchanged:** dawn-009, dawn-011, epic-004, poetics-007 and sky-002 stay weak. fame-015 and epic-003 stay sound. fame-012, poetics-002 and sky-010 stay rejects.
- **Lower:**
  - dawn-017 drops from weak to reject. As a bare NP its head fails, and the Latin witness is Macrobius.
  - dawn-019 drops from weak (r1) to reject. The Vedic has no possessive relation.
  - sky-009 drops from weak (r1) to reject: it fails the head rule.
  - sky-011 drops from sound (r1) to weak: stitched genitive and accent.
- None went up.

## 2. Findings

1. **The verbless conversion is mostly faithful, but it does not fix lines that lacked a shared phrase.**
   - In 9 of the 14 converted lines, the np, nominal or APPOS shape follows what the daughters actually have. Examples:
     - apposition in dawn-011 (RV 4.13.3 tám sū́ryam … spáśam; Hymn. Dem. 62 Ἠέλιον … σκοπόν);
     - apposition in epic-004 (amṛ́tāḥ separated from áśvāḥ by the verb; ἄμβροτοι enjambed);
     - apposition in poetics-007 (θεοί, δωτῆρες ἑάων) and sky-011;
     - the nominal sentence in sky-002 (RV 1.164.33).
   - Removing the interpolated copula is an improvement everywhere.
   - But fame-012, sky-010 and poetics-002 were rejected for content (misconstrual, periphery only, a non-existent NP), and the new clause type leaves that untouched.
   - fame-012 makes it worse: its nominal predicate 'my name is famous' is not the Greek sentence. In Od. 19.183 ἐμοὶ δ' ὄνομα κλυτὸν Αἴθων, the predicate is Αἴθων and κλυτόν is attributive.
   - Two conversions build an NP the second branch does not have:
     - dawn-019: a genitive 'cattle of the Sun', where RV 7.36.1 has the Sun as subject.
     - sky-009: 'heaven, the ornament of stars', where Avestan stəhrpaēsah- qualifies the garment.
2. **The np case defaults to NOM even where the daughters agree on an oblique case** (systematic; not a verdict changer). The brief says "prefer the morphology the branches agree on", and `"case"` accepts any case. Lines where every cited cell is accusative:
   - dawn-009: RV 3.2.7, object of ā́ … apr̥ṇat; Hes. Th. 19, in the accusative catalogue.
   - dawn-011: RV 4.13.3, Hymn. Dem. 62.
   - dawn-017: RV 1.72.10 acc. du.; Macrobius (not local) oculum as West quotes it.
   - sky-010: RV 1.182.1 ACC DU; Hymn. 33.1 κούρους.
   - fame-015: RV 1.91.21 and 1.49.2 suśrávasam; Od. 21.331 ἐϋκλεῖας.

   NOM is defensible as a citation form only when the daughters disagree (epic-003: Vedic genitive, Greek accusative).
3. **Stale "not in local corpora" claims (r2 P10 again).** The converted lines were edited only where the copula was, and four notes still say a text is not local when glaux has it:
   - Hes. Th. 19 (dawn-009);
   - Hymn. Dem. 62 (dawn-011);
   - Hymn. Hom. 33.1 = glaux 0013-033 (sky-010);
   - Eur. Hel. 1096 = glaux 0006-014 (sky-009).

   In each, the locus contains the cited words.
4. **Support leaks and uncited sources (P2).**
   - bp-gk-ita-001: the finite verb's o-grade causative *h₁wogʷʰéye- comes from Lat. voveō (Cato Agr. 83.1, a support ref). The plan lists `pie-lex-h1wogwheyeti` as secure although the builder returns level `none`.
   - sky-father-002: 'our' (nos) comes from AVP 5.21.1 dyauś ca naḥ pitā. The passage is local (DCS) but not in cognate_refs; the cited RV 1.164.33 has me 'my'.
5. **Stitching.**
   - bp-ii-gmc-001: the verb janata (RV 10.123.7, plural object) is joined to the singular of RV 10.84.5. In Crist 636 the subject is Job and the object Christ, so cende means 'proclaimed'; 'begot' fits neither passage.
   - bp-ii-gmc-002: the ON verb (refrain) and the ON address word (Vǫluspá 1, an accusative) come from different stanzas.
   - sky-father-011: devā́nām comes from RV 1.185.6, where jánitrī is Heaven and Earth, not Dyaus.
6. **Engine and lexicon forms.**
   - **pl̥th₂éwih₂** (sky-002): still printed. Ved. pr̥thivī́ contradicts it. This is r1/r2 P6, unfixed.
   - **déh₃tores** (poetics-007) and **ǵénh₁tōr** (sky-011): root-accented agent nouns, where the cited cells are suffix-accented (δωτῆρες; Ved. dātā́ + gen., Benveniste's type; Av. dātar-; Ved. janitā́). The root-accented type is attested only in δῶτορ ἐάων (Od. 8.335), which is not cited. The note on poetics-007 says the usable lexeme is missing.
   - **wéwket** (bp-east-002, interpolated): it has no labiovelar. Gk εἶπον (π < *kʷ) contradicts that, and so does the lexicon's own reflex, Proto-Hellenic *weikʷon.
   - Minor: *n̥mr̥tós is oxytone, against Ved. amŕ̥ta- (epic-004, bp-ii-ita-003).
7. **Loci.** Every cited locus that has a local corpus contains the cited words, parallel and support refs alike, and no fabricated attestation was found. Corpora and loci checked (parallel loci; support loci are listed after):
   - DMHP: Eznik II.3 §24.
   - Vuk: 'Nahod Simeun'.
   - TOROT: Slovo 77.
   - FJ 1926: Vǫlundarkviða 23, Sigurðarkviða skamma st. 46.
   - TITUS Neckel: Sigurðarkviða st. 45, Vǫluspá 1, 27, 28, 33.
   - DCS: MBh 3.158, AVŚ 3.13.3, 1.32.1, 13.1.24, AVP 5.21.1.
   - AGDT: Od. 19.403-404, 19.183, 21.331, 8.325, 9.162, 17.533, 12.127-128, 13.51; Il. 1.504, 17.498, 24.287-288, 16.380-381, 16.866-867, 16.522, 1.9, 14.286.
   - glaux: Hes. Th. 19, 460; Hymn. Hom. 2.62, 2.117, 33.1; Pind. Pyth. 3.113, Nem. 3.4; Eur. Hel. 1096.
   - Grein: Beowulf 1100, Crist 636.
   - Gutenberg Beowulf: 1100, 1834.
   - CAB: Y. 31.22b, 65.12, Yt. 13.2-3, N. 5.2.
   - Buck: Tab. Ig. IIb 22-26.
   - LASLA: Cato Agr. 134.1, Plaut. Epid. 340, Amph. 1093, Catull. 12.6, 64.26-27, Lucr. 1.250-251.
   - Baehrens FPR: Carmen Saliare fr. 1, with its apparatus.
   - Doyle: Wb. 18c11.
   - Rhesa 1843: no. 48.
   - VedaWeb: all cited RV stanzas.
   - Support loci: Il. 5.879, 1.395; Hymn. Hom. 2.65; Hávamál 141 (FJ 1926); RV 1.103.5, 3.4.11, 1.31.1, 10.150.4, 2.23.2, 1.89.4; Y. 31.1c; YtDru7.4j; Cato Orig. (dii immortales), Agr. 83.1; Tab. Ig. IIb 17-18; Catull. 12.6.

   Three caveats:
   - Vr. 11.12 (poetics-007) was not found in CAB; Y. 65.12 suffices.
   - Macrobius and the Æcerbot are not local.
   - The Carmen Saliare reading diuom is Baehrens's; the Florentinus has diuum, and supplicate is Grotefend's correction. The note says so.

## 3. False positives of the builder's secure check

| line | cited | credited as | problem |
|---|---|---|---|
| bp-east-003 | Gk υἱός | *suHnús exact | *suH-iu-, another suffix (Beekes EDG): root level. Known before this round. |
| dawn-sun-009 | Ved. mahát | *méǵh₂s exact | The nt-stem mahā́nt-. The exact match for μέγα is Ved. máhi. Formation-level. |
| dawn-sun-011, -019 | Ved. sū́rya- | *sóh₂wl̥ exact | A -ya- derivative, not the heteroclite (svàr is the exact one). Formation-level. |
| poetics-gifts-007 | Av. dātar- | *déh₃tōr exact | Accent-blind: the cell is the suffix-accented type. |
| sky-father-011 | Ved. janitár- | *ǵénh₁tōr exact | Accent-blind, as above. |
| bp-ii-gmc-002 | ON vita | *wóyde exact | The right lexeme, but the path runs through non:vissa → *widtós (the participle adjective). The verdict is unaffected. |
| bp-east-001 | Gk θῆαι | *dʰeh₁- root | The path runs through pie-lex-dheh1ts (θής 'serf'), the wrong lexeme. The level happens to be right. |
| bp-gk-ita-001, dawn-sun-017, sky-father-011 | Lat. Iuppiter, Umbr. Iupater | *dyḗws / *ph₂tḗr exact | Evidence from a compound member. Acceptable, but it should be marked as such. |

The pattern:
- The builder equates a daughter lemma with a PIE lexeme whenever a Wiktionary or kaikki chain links them, and it cannot see suffix differences inside the same root (υἱός, mahát, sū́rya-) or accent (dātar-, janitár-).
- An `exact` on a derivative is therefore not evidence of formation identity.
- A mapping-level fix would compare the daughter stem's suffix with the lexeme's: -nu- vs -iu-, -nt- vs -s, -ya- vs -l/n.

## 4. Systematic problems

- **Kin and commonplace pairs dominate the new bp-* lines.**
  - brother to brother (bp-east-002);
  - god of gods (bp-ii-ita-002);
  - immortal gods (bp-ii-ita-003);
  - word and deed (bp-gk-gmc-001);
  - son of Sky (bp-east-003).

  The branch-pair search finds lexically exact pairs, but many are the kind of collocation that arises independently. Only bp-gk-gmc-002 and bp-ii-ita-001 are both exact and specific.
- **Late witnesses are often the only second branch.**
  - the Slovo and MBh (bp-east-002);
  - Macrobius (dawn-017);
  - Lucretius (sky-002);
  - Christian OE (bp-ii-gmc-001).

  The notes flag the date but still count the branch. The branch count (`branches`) should not include a witness the note itself calls derivative.
- **The secure check over-credits derivatives** (§3). For the verbless lines this matters more than before: an NP line has no verb to carry it, so a wrong `exact` on the NP head is the whole claim (bp-east-003, dawn-011, dawn-019).
- **Notes are not re-verified when the plan is revised** (§2.3). The same stale claim appears in four lines edited this round.
