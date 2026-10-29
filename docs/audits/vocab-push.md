# Vocabulary push (2026-10-29)

Branch `worktree-agent-a9632948d6f6181bb`. This work follows `docs/audits/unusable-lexemes-census.md` and `docs/audits/unusable-requests-round2.md`. Tests: `tests/test_vocab_push.py`.

## Counts

| | before | after |
|---|---|---|
| usable specs (`classify_report.json`) | 4,885 | 4,917 |
| offered by `make_slice` by default (census "ok") | 1,206 | 1,325 |
| extra offered with `--derived` | 1,148 | 1,072 |
| no-accent (pool P10) | 795 | 725 |

The "before" column was measured on this branch's base (f12b60e) with the census script and the current `make_slice` pool. The census document's own figures (1,131 ok, 4,885 usable) come from an earlier commit.

Where the gain comes from:

- **Shape rules:** +31 usable (devī).
- **Checked overrides:** 19 glosses, one accent (beech) and one paradigm (tooth).
- **Reflex-confirmed glosses:** 123.
- **Accents from reflexes:** 69.

## Requested words

| word | lexeme | now | how |
|---|---|---|---|
| roof | *stégos* | offered | gloss "roof, house" (Beekes s.v. στέγος; Matasović *\*tegos-*; M&A ch. 13) |
| bed | *légʰos* | offered | gloss "bed, couch; lair" (Beekes s.v. λέχεται; M&A *\*légʰes-*) |
| tooth | *h₃dónts* | offered | checked hysterokinetic spec h₃dónt-/h₃dn̥t- (Beekes 2011 p. 197; Ved. *dán, dántam, datás*) |
| swear | *h₃m̥néh₃ti* | offered | gloss "to swear (an oath)" (Beekes s.v. ὄμνυμι; Ved. *ámīti*). Greek and Indic only |
| owe | *dʰl̥gʰéti* | offered | gloss "to owe, be entitled to" (Matasović *\*dlig-o-*). Celtic only |
| wait | *méneti* | offered | gloss "to stay, remain; to wait (for)" (Beekes s.v. μένω) |
| hornet | *ḱr̥h₂sḗr* | offered | gloss "hornet" (de Vaan s.v. *crābrō*; Kroonen *\*hurnuta-*) |
| suckle, sweat, wash, lick | *dʰéh₁yeti, swéydos, léwh₃eti, léyǵʰeti* | offered | dictionary glosses (Beekes, de Vaan, Kroonen, LIV²) |
| sweep/wipe, grief/hatred | *wr̥séti, ḱéh₂dos* | offered | the branches split the sense; glosses follow de Vaan and Beekes's PIE glosses |
| fortress/town, womb, elk | *tpólHis, gʷélbʰus, h₁ólḱis* | offered | Beekes s.v. πόλις, δελφύς; Kroonen *\*algi-*, Derksen *\*olsь* |
| beech | *bʰeh₂ǵós* | offered | M&A ch. 10 print *\*bʰeh₂ǵós*; Gk φηγός is oxytone; feminine |
| debt | *dʰl̥gʰos* | glossed, **not offered** | no source prints an accent, and there is no Vedic or Greek cognate |
| grey | *polHwos* | glossed, **not offered** | as for debt (Kroonen *\*falwa-*, Derksen *\*polvъ*: unaccented) |
| yew, sieve | *h₁eyHwos, kreydʰrom* | **not offered** | as for debt |
| man | *ǵʰmṓ* | **not fixed** | Fortson §6.30 prints amphikinetic *\*dʰǵʰémō(n)*, gen. *\*dʰǵʰm̥nés*: another lemma with root accent. The Klein et al. handbook prints the oxytone *\*ǵʰm̥mṓ* (our headword) with no paradigm. The sources disagree on the accent, so no spec. *mon-* is a Germanic-only bare stem |
| witness | *widtrés* | **not fixed** | the literature prints *\*u̯id-tor-* (Beekes s.v. ἵστωρ; Fortson §12.28 *\*u̯idtōr*), unaccented, Greek only. Neither source supports *widtrés* |
| pig, fist, flea, elm, red deer, ant, wise | | **not fixed** | no handbook paradigm (súHs, plúsis, h₁élem, h₁élh₁ēn, widris). Fist is M&A's oxytone *\*pn̥kʷstí-*, which no shape rule takes. Ant: the hk-iu rule is unusable |
| rotten, beak, illness | *pewHlos, Hreh₃dtrom, ligós* | **not fixed** | *pewHlos* is a Baltic noun 'mouldered wood'; 'rotten' is zero-grade *\*puH-lo-*. *rōstrum* is Latin only. *ligós* mixes Gk ὀλίγος 'few' with Lith. *ligà* 'illness' |
| month, leaf, elbow, cough | | held out | `eval_root` families: not offerable by policy |

## Shape rules (backtest cell agreement)

| rule | before | after | usable |
|---|---|---|---|
| devī | 60.5% (46/76) | **86.8%** (66/76) | yes (+31 lexemes) |
| n-stem-hk | 71.0% | 76.3% | no |
| hk-iu-stem | 45.3% (on 5 tables) | 57.9% (on 3) | no |

- **devī:** an accented o-grade or lengthened-grade root keeps the root accent throughout (Ved. *pátnī*, gen. *pátnyāḥ*; *rā́jñī*, *rā́jñyāḥ*; fixed accent as in Fortson §6.21's acrostatic class) and the grade the Wiktionary tables write (*pótn̥yeh₂-*). Vedic cannot tell *\*o* from *\*e*, and §6.21's o/e ablaut is not applied. Before this fix, `zero_grade()` deleted the only root vowel (*pótnih₂ → ptnyéh₂*).
  - The e-grade branch alone scores 28/38: néptih₂'s table keeps *nept-*.
  - Unaccented devī headwords now get no spec (15 lexemes): their oblique accent would be a guess.
  - *síh₂* 'she' is a pronoun, not a devī noun.
- **n-stem-hk:** the locative now takes accented *-én(i)* (Fortson §6.11). The rest of the miss is lexical (sh₂imṓ's weak stem is sh₂in̥).
- **hk-iu:** the tables of Hrugʰís and bʰeh₂ǵʰús are written on root-accented headwords and are now skipped, as is done for eh₂. The suHnús and suHyús tables have an o-grade weak stem (Beekes's *\*-ou-s*), which the rule does not produce. No threshold was changed.

## Derived-gloss-only lexemes

`pie.glosses.confirm` gives a lexeme the gloss that its own reflexes agree on in two or more branches (docs/lexicon.md "Reflex-confirmed glosses"). This adds 123 lexemes: 72 by the head rule and 51 by consensus. They are offered by default and tagged `gloss_source: reflex-confirmed` in slices.

Of the 2,341 usable lexemes that still have only a derived gloss:

- 1,340 have linked reflexes in one branch only;
- 151 have linked reflexes in none;
- 553 have no reflex record;
- 256 have reflexes in two or more branches that do not agree.

## Accent-missing lexemes

`pie/accent_reflex.py` supplied 69 accents (rule in docs/morphology.md "Accent from a Vedic or Greek reflex").

Of the 725 that remain, most have no Ancient Greek or Vedic reflex in our data. The rest are excluded for one of these reasons:

- their shape class is not accent-faithful (athematic stems, table specs);
- the reflex fails the Greek recessive or law-of-limitation test;
- the reflex has a different syllable count;
- the reflex is Classical Sanskrit with no accent.

## Guards

- **Wiktionary cross-check:** 14,015/14,197 before and after.
- **Re-realization:** all 39 Tier 3 batches were re-realized read-only, with the current engine, against the stored records.
  - **Already different at the base, before this work (29 plans).**
    - 24 records: the Narten imperative *h₁éddʰi → h₁ddʰí* (docs/morphology.md, Phase B).
    - 4 plans now rejected by the dual-perfect checker rule: t010-0012, t027-0016, t027-0022, t027-0025.
    - 1 plan now rejected by the adjective-as-noun gender rule: b002-0250.
    - 1 record, t031-0015: *h₂r̥ǵrós → h₂r̥ǵróm* (neuter agreement with fire).
  - **Changed by this work:** one record. t3-pilot-00008 (fable-009) changes *ǵʰeh₁ros → ǵʰéh₁ros* (Gk χῆρος). This supplies a missing accent, i.e. it fixes an error.
  - **Interlinear gloss line:** 82 stored records would change if re-realized. For example, *sing~ → sing* (the derived-gloss marker goes), *hatred~ → care* (ḱéh₂dos), and *love~ → loveliness* (wénh₁os). Their PIE does not change.
  - **Not rewritten:** no stored record was rewritten here. Re-realizing with `realize_plans.py` resets each touched batch's release to pending. Before this work, an earlier partial re-realization of 16 batches had also clobbered generator provenance (engine_version and prompt_id); it was reverted.
