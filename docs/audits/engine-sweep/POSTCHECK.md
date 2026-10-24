# Engine sweep: post-integration check of the re-realized corpus

Checked 2026-10-24 against INTEGRATION.md and STATUS.md "Conventions (engine sweep)". Before = `git show 7337a3b~1:corpus/tier3/<batch>.jsonl` (27 batches, 2,115 records). After = the working-tree corpus/tier3 (commit 32673c4; 0dd44f1 touched only rejects). Nothing outside this file was modified. Scratch scripts are `postcheck-*` in the session scratchpad.

**Verdict.** The re-realization did what INTEGRATION.md says. Once 21 classifier misses were mapped by hand, **no form change is unexplained**. My token-level count of morphology changes matches the integrator's `impact.json` entry by entry except 21 small entries, a net +6, all explained (table A). The sample shows no regression. All 60 sampled forms are right per the stated convention; 3 carry a flag (#1, #37, #42). Outside the sample, two problems that touch the corpus came up, each with a proposed fix (section 6): **déh₂news** (4 tokens) contradicts the very source its override cites, and the **boukólos decision stops at the thematic and eh₂ declensions** (*pérkus*, *ḱm̥tógus*: 19 tokens). Every engine-rule decision keeps its old form as a cell. The three override-based decisions keep it only in `extra_specs`, as INTEGRATION.md documents, and the validator recognizes all of them.

## 1. Method

- Tokens were aligned per record id with `difflib` on (lex_id, features), with a second pass on lex_id alone to catch relabels. 42,017 tokens before, 42,015 after (13 inserted, 15 deleted).
- The changes were attributed by stage. The same records were re-realized with three engine trees extracted with `git archive`:
  - base = 7337a3b~1;
  - sweep = 7337a3b;
  - current = 32673c4.
- The stages compared are:
  - **stale**: the stored old text vs the old plan at base;
  - **plan**: the old plan vs the current plan, both at base;
  - **sweep**: the current plan at base vs at sweep;
  - **post**: the current plan at sweep vs at current.
- The current engine reproduces the stored corpus exactly: 0 of 2,115 records differ.
- Validator: all 2,115 records `pass` before and after. No record lost coverage, and the tiers are 42,015/42,015 `exact`.

## 2. Counts by fix

Form changes: **1,274 tokens in 754 records.** Of these:
- 1,060 changed at the sweep stage: 1,040 from morphology and 20 from realize.py R4/R5. Five of these also changed at another stage: 3 at the plan stage, 2 at the stale stage;
- 173 are pre-sweep staleness only;
- 37 come from plan edits only;
- 4 come from the post-sweep engine (764386f) only.

These add up: 1,060 + 173 + 37 + 4 = 1,274.

Besides the form changes: 121 tokens were relabelled, 13 were inserted and 15 deleted.

### A. Sweep-stage morphology vs INTEGRATION.md's table

| INTEGRATION row | INTEGRATION | this check | difference explained by |
|---|---|---|---|
| overrides + smaller engine fixes | 230 | 232 | see the breakdown below; +1 *h₁rudʰyom*, +1 *dʰubʰnóm* (agreement cascades), +1 *tn̥nwn̥tíh₂* (participle cell, not in the cell dump), +1 *h₂ḱm̥néh₁* (the 2 stale+sweep tokens fall here) |
| *h₁ed-* Narten (decision) | 121 | 124 | +2 INJ.2SG *h₁ḗds*, +1 INJ.3SG, +1 PTCP *h₁édn̥tes* (cells impact.py did not dump); −1 PST.3DU moved into a plan-edited slot |
| heteroclite collective *-ōr* | 99 | 99 | exact |
| 'I' *h₁eǵóh₂* (decision) | 82 | 82 | exact |
| *ḱéyor* t-less middle (decision) | 79 | 79 | exact |
| u-adjective suffix accent (decision) | 67 | 65 | the 2 *gʷr̥h₂úh₁* INS.SG tokens are counted here under INS.SG |
| vocative pl./du. retraction (decision) | 64 | 56 | −3 *dʰúgh₂teres* and −1 *HéHḱewih₂es* (slots changed by R5 or plan edits); the VOC.DU dual forms are counted under the dual row; 4 R5 relabels keep their form |
| consonant-stem dual *-h₁e* (decision) | 62 | 68 | +3 PTCP.NOM.DU *-nth₁e* (participle cells), +3 VOC.DU |
| 'ten' *déḱm̥* (decision) | 55 | 55 | exact |
| *pérkʷunos* (decision) | 49 | 49 | exact |
| *dédeh₃ti* mobile (decision) | 37 | 36 | −1 PRS.2PL slot plan-edited to 2SG; +1 stale+sweep |
| devī acc. *-ih₂m* (decision) | 21 | 22 | |
| i/u INS.SG | 20 | 21 | +2 *gʷr̥h₂úh₁*, which INTEGRATION.md counts under u-adjectives; −1 *gʷrúh₁*, whose slot was plan-edited (it is in the plan+sweep row) |
| pronoun tables, *tísrn̥s* | 19 | 19 | exact |
| eh₂ vocative *-a* (decision) | 17 | 17 | exact |
| 2du *-tes* (decision) | 9 | 9 | exact |
| thematic neuter dual *-oyh₁* | 3 | 4 | +1 *h₁rowdʰóyh₁* (an adjective agreeing with a neuter) |
| plan-added or plan-edited slot with a sweep form (*gʷrúh₁*, *h₁édtām*, *tóh₁*) | – | 3 | not in impact.json, which used the old plans |
| **total** | **1,034** | **1,040** | entry-level comparison with `integ/impact.json`: 21 entries differ, net +6, all listed above |

Breakdown of the 232 tokens in "overrides + smaller engine fixes":
- *déh₂nu* 26;
- *néh₂us* 23;
- *Hróth₂os* 21;
- E1 glide rule 20 (*dedwiyḗr* 8, *ḱl̥nitó* 4, *ḱl̥nwénti* 4, …);
- *bʰuH-* 18;
- *dʰubʰrós* 16;
- *h₂r̥ǵn̥tóm* 13;
- r-n D1 phon.join 12 (*h₂ḱm̥nés*, *kh₂n̥mén-*);
- *h₂wr̥s-* 11;
- *HeHḱús* 10;
- *yḗkʷr̥* 9;
- *dinós* 7;
- *h₃mígʰleh₂* 6;
- *gʷḗn* voc. 5;
- s-root F3 *médos* 4;
- feminine D6 *dn̥ǵʰwéh₂m* 3;
- *h₃ókʷ* 3;
- *wékʷsperoy* 3;
- E3 3;
- E2 2;
- *dayh₂wr̥bʰós* 2;
- *wn̥-* 2;
- r-n D2 *-mń̥su* 2;
- 1 each: *stérḱos*, *h₁rudʰyom*, *ǵʰórneh₂m*, *dʰubʰnóm*, *méh₂teri*, *tétḱn̥t*, *Hrugʰím*, *dʰǵʰuHbʰós*, *h₂yuHn̥téh₂i*, E4 *dʰédʰh₁n̥ti*, *h₃rḗǵi*.

### B. realize.py (sweep stage)

| fix | tokens |
|---|---|
| R3 `GEN.PL` → `GEN.PL.ENCL` (label only) | 67 (INTEGRATION.md: 68; one slot was plan-edited) |
| R5 conjoined vocative pair, 2nd member nominative (Fortson §8.11) | 16 relabels, 12 with a new form (*dʰéǵʰōm* 4, *méh₂tēr* 3, *pótnih₂*, *bʰṓr*, *bʰérǵʰus*, *h₁n̥gʷnís*, *HeHḱéwih₂es*) |
| R4 conjoined-subject group agreement | 8 (*trésetes*, *h₁rudʰéh₁tes*, *ḱélontor*, *h₂uksént*, *bʰebʰih₂ḗr*, *pléh₁dʰoyh₁tām*, *h₁pih₁tā́m*, *kʷḱih₁wé*) |

### C. Changes INTEGRATION.md does not cover (legitimate, but listed as required)

1. **Pre-sweep staleness: 173 tokens in 154 records.** That is exactly INTEGRATION.md's "154 already stale". The base engine already produced the new form. The records carry older engine stamps: aef57c3 59, f348874 53, 28ea46c 23, 4c9d86e 7, 04599cb 5, 40b5072 4, 93233ae 3. The pilot and pilot2 batches account for 53 of the 154 records. The forms:
   - *HéHḱus* → *HeHḱús* paradigm: 117;
   - *h₃réǵs* → *h₃rēǵés* GEN.SG: 17, plus 1 DAT.SG;
   - i-stem VOC.SG *gʰósti* → *gʰóstey*: 6, plus 4 for *gʰóstipotey* and 1 for *h₁ń̥gʷney*;
   - SBJV.1PL *-omos* → *-omes*: 10;
   - prohibitive *ne* → *mē*: 2;
   - *suHnúes* → *suHnéwes*: 2, and *súHnu* → *súHnew*: 2;
   - *ǵʰméy* → *dʰǵʰméy*: 2, and *ǵʰémi* → *dʰǵʰémi*: 2;
   - 1 each:
     - *kʷ(ó)smead* → *kʷ(ó)smōd* (×2: indefinite and interrogative ABL.SG);
     - *h₃énHōs* → *h₃énHesh₂*;
     - *dʰugtréy* → *dʰugh₂tréy*;
     - *h₂éryeti* → *h₂érh₃yeti*;
     - *susréh₁* → *swesréh₁*;
     - *ḱl̥wént* → *ḱluwént*;
     - *HéHḱuh₂* → *HeHḱúh₂*.

   None of these is a sweep change. All of them were already in the base engine.
2. **764386f plan, blocklist and engine edits.**
   - 37 plan-stage form changes: stressed pronouns replacing doubled enclitics (*toy* → *téwe* 5, *te* → *twé* 2, *moy* → *méne* 2, *nos* → *n̥smé*), number fixes for addressees and subjects (IMP.2DU/2PL → 2SG 10, INJ.2DU → 2SG 2, *trémt* → *tr̥mént*, *h₂ówim* → *h₂ówins*, *stunédtu* → *stundéntu*), and antecedent gender fixes (*tóm* → *tód*, *tā́m* → *tóm*, *h₁íns* → *h₁íd*, …);
   - 3 tokens with a plan edit plus a sweep form;
   - 4 post-stage tokens: *dʰegʷʰróm* 3 and *mr̥wéh₂* 1, from the five noun-used adjectives now `pos: adj`;
   - 13 insertions and 15 deletions:
     - blocked *ǵʰéyos* replaced by *h₁éḱwos* in 10 pilot/pilot2 records;
     - the *kʷetwóres* lexeme replaced by `closed:numerals/4` in 2 records;
     - t3-t020-00039 gained a subject *h₁íh₂*, with its *-kʷe* moving to it.
3. **Relabels: 121 in total.** R3 accounts for 67, R5 for 16, and R4 together with the plan edits for 38. Of the R4/plan relabels, 8 are R4 and 30 are plan edits, including GEN.SG.ENCL → GEN.SG 7 and ACC.SG.ENCL → ACC.SG 2.

The current checker rejects 82 old plans: the 31 known rejects plus 51 that 764386f fixed in the plans. By message:
- "adjective used as a noun needs a gender": 42;
- blocked *ǵʰéyos*: 10;
- 2nd-person number contradicts the addressee: 12;
- verb number contradicts its subject: 7;
- doubled enclitic: 9;
- blocked *kʷetwóres*: 2.

No rejection is of an unexpected type.

## 3. Unexplained changes

**None.** The automatic classifier left 21 tokens unclassified at first, and all of them belong to listed fixes:
- *h₂ḱm̥néh₁/-nés* 9 → r-n D1;
- *h₁imń̥su* and *wr̥smń̥su* → r-n D2;
- *dn̥ǵʰwéh₂m* 3 → feminine D6;
- *médos* 4 → s-root F3, since `pie-lex-medos` is now routed to the s-stem neuter shape;
- *ǵḿ̥rōs* → vocative retraction (the classifier's accent test was fooled by the acute of ǵ);
- *h₁rowdʰóyh₁* → D9;
- *dʰubʰnóm* → agreement with *ḱéh₂dos*, which the thematic D7 override made neuter;
- *dedwiyḗr* 8 → the E1 glide rule ("smaller engine fixes");
- *h₁stés*, *duktés*, *dʰedʰh₁tés* → the 2du decision.

## 4. Sample of 60 changed tokens (seed 11)

**Scheme (reproducible, `postcheck-sample.py`).**
- Strata: INTEGRATION.md's 17 rows, plus one stratum for "overrides and smaller engine fixes" and one for "realize.py R4/R5". Stale, plan and post changes are excluded.
- Allocation: 1 per stratum, the rest proportional to tokens by largest remainder, capped at the number of distinct (lex_id, features, new form) types.
- Selection: per stratum, candidates are sorted by (record id, position), shuffled with `random.Random(11)`, and the first are taken in order, skipping repeated types.

**Abbreviations.** F = Fortson 2010, R = Ringe 2006 (book pages; text file = page + 11), B = Beekes 2011, L&Y = Lundquist & Yates, Handbook vol. 3 ch. 122, M&A = Mallory & Adams. "✓conv" = right per the stated convention.

| # | stratum | record | lexeme, cell | before → after | verdict, reference |
|---|---|---|---|---|---|
| 1 | 'I' | t3-b002-00137 | personal/1 NOM.SG | h₁eǵ → **h₁eǵóh₂** | ✓conv. F §7.4 *eǵoh₂; L&Y (h₁)eǵoh₂; R éǵh₂ dissents. The final accent is an assumption (Gk ἐγώ); no book prints one |
| 2–4 | 'ten' | t3-t008-00017, t3-t013-00016, t3-t013-00003 | numerals/10 ACC.PL, NOM.PL, INS.PL | déḱm̥t → **déḱm̥** | ✓conv. F §3 list *dek̑m̥, §6.40 *dek̑m̥-t- 'decad' (the *-t* form is the derived noun); L&Y *deḱm̥. Indeclinable, so it is the same form in every case |
| 5 | 2du | t3-t020-00029 | dʰédʰeh₁ti PRS.2DU | dʰedʰh₁th₁és → **dʰedʰh₁tés** | ✓conv. R p. 31: 2du = 3du *-tés |
| 6–8 | pérkʷunos | t3-t009-00019, t3-t009-00015, t3-t019-00014 | NOM.SG, VOC.SG, ACC.SG | pérku- → **pérkʷunos, pérkʷune, pérkʷunom** | ✓conv (M&A *perkʷunos, 4 hits). F §3.39 states boukólos as a PIE rule (a labiovelar "adjacent to the vowel *u"), against this decision. See finding 6.2 for the scope gap |
| 9 | dual -h₁e | t3-t010-00001 | gʷṓws ACC.DU | gʷówh₁ → **gʷówh₁e** | ✓conv. A root noun in *-w-*, so a consonant stem; Ved. gā́vā/gā́vau has the C-stem dual. L&Y's "glide-final stems *-h₁*" cites i-stems only (kavī́, gosti) |
| 10 | dual -h₁e | t3-t009-00001 | h₂nḗr ACC.DU | h₂nérh₁ → **h₂nérh₁e** | ✓conv. R pp. 47–49 C-stems *-h₁e* (ph₂térh₁e, uksénh₁e) |
| 11 | dual -h₁e | t3-t003-00014 | bʰréh₂tēr NOM.DU | → **bʰréh₂terh₁e** | ✓conv. R p. 49 ph₂térh₁e |
| 12 | dual -h₁e | t3-t019-00017 | dʰugh₂tḗr NOM.DU | → **dʰugh₂térh₁e** | ✓conv. Same paradigm; hysterokinetic suffix accent kept |
| 13 | devī acc. | t3-t005-00007 | h₁wr̥Hús f. ACC.SG | -ih₂m̥ → **h₁wr̥Héwih₂m** | ✓conv. F §17.12 fem. acc. *-ih₂-m (Toch. -ā); F §6.70 the eh₂ analogue *-eh₂-m, not *-eh₂-m̥ (Stang). R p. 50 tn̥h₂éwih₂m̥ dissents and stays the alternative |
| 14 | devī acc. | t3-b001-00173 | pótnih₂ ACC.SG | → **pótnih₂m** | ✓conv (Ved. pátnīm) |
| 15 | dédeh₃ti | t3-b002-00239 | PRS.1PL | dédh₃mes → **dedh₃més** | ✓conv. B *dʰi-dʰh₁-mé (Gk títhemen), Ved. dadmás |
| 16 | dédeh₃ti | t3-t018-00022 | IMP.2SG | dédh₃dʰi → **dedh₃dʰí** | ✓conv. Ved. daddhí; R p. 31 *-dʰí |
| 17 | eh₂ voc. | t3-b003-00058 | bʰéh₂nos f. VOC.SG | bʰéh₂neh₂ → **bʰéh₂na** | ✓conv. F §6.70 ("retracted accentuation … ended in *-a"); R p. 49 h₂wĺ̥h₁n[a] |
| 18 | eh₂ voc. | t3-t011-00012 | léwkos f. VOC.SG | léwkeh₂ → **léwka** | ✓conv. Same rule |
| 19 | Narten | t3-t008-00016 | h₁édti PRS.3SG | h₁édti → **h₁ḗdti** | ✓conv. R p. 27 *h₁ḗd- ~ *h₁éd-; F ch. 5 (Lat. ēst) |
| 20 | Narten | t3-t016-00007 | PRS.1SG | → **h₁ḗdmi** | ✓conv. Strong lengthened grade |
| 21 | Narten | t3-t014-00006 | PST.3SG | → **h₁ḗdt** | ✓conv. Strong stem in the singular active |
| 22 | Narten | t3-t003-00013 | IMP.3SG | → **h₁ḗdtu** | ✓conv. R p. 31 *-tu* on the strong stem |
| 23 | Narten | t3-t017-00040 | OPT.3SG | h₁dyéh₁t → **h₁édih₁t** | ✓conv. R p. 30 *h₁éd-ih₁-* (zero-grade suffix after the accented stem) |
| 24 | Narten | t3-t010-00003 | PST.3PL | h₁dént → **h₁édn̥t** | ✓conv. Weak *h₁éd-* + *-n̥t* (accent fixed on the root) |
| 25 | Narten | t3-t012-00015 | PRS.2SG | → **h₁ḗdsi** | ✓conv (Lat. ēs) |
| 26 | u-adj | t3-t003-00032 | h₁léngʷʰus NOM.PL | h₁léngʰewes → **h₁ln̥gʷʰéwes** | ✓conv. Suffix accent (Ved. raghávas) and labiovelar (i-u #12) |
| 27 | u-adj | t3-t003-00034 | gʷr̥h₂ús NOM.SG | gʷréh₂us → **gʷr̥h₂ús** | ✓conv. Ved. gurú-, Gk βαρύς; the zero-grade root before the accented suffix is regular |
| 28 | u-adj | t3-t005-00004 | h₁wr̥Hús ACC.PL | h₁wérHuns → **h₁wr̥Húns** | ✓conv. Ved. urū́n |
| 29 | u-adj | t3-pilot2-00133 | pl̥th₂ús n. NOM.SG | pléth₂u → **pl̥th₂ú** | ✓conv. L&Y ch. 122: *pl̥th₂ús, *pl̥th₂wíh₂, *pl̥th₂ú |
| 30 | voc. pl. | t3-t011-00028 | deywós VOC.PL | deywṓs → **déywōs** | ✓conv. F §6.52 (Ved. dévās) |
| 31 | voc. pl. | t3-t003-00010 | wiHrós VOC.PL | → **wíHrōs** | ✓conv |
| 32 | voc. pl. | t3-t008-00032 | diwyós VOC.PL | → **díwyōs** | ✓conv |
| 33 | ḱéyor | t3-t020-00002 | MID.PST.3SG | ḱéyto → **ḱéyo** | ✓conv. F §5.16 *ḱey-o(-) (CLuw. ziyari, Ved. śáye); R p. 31 *-ó / *-t-ó |
| 34 | ḱéyor | t3-t013-00023 | MID.PRS.3SG | → **ḱéyor** | ✓conv. F §5.18 |
| 35 | ḱéyor | t3-t016-00011 | MID.PST.3PL | ḱéyn̥to → **ḱéyro** | ✓conv. F §5.18 3pl *-ro |
| 36 | ḱéyor | t3-t005-00026 | MID.PRS.3PL | → **ḱéyror** | ✓conv |
| 37, 42 | -ōr | t3-t005-00003 ×2 | wódr̥ NOM.PL, ACC.PL | wódr̥h₂ → **wédōr** | ✓conv. R p. 45 *wédōr ~ udn-´. F §6.15 *ud-ōr and §9.40 *u̯edṓr put the accent on the suffix: flag for the lead (R and Wiktionary *wédor* vs F) |
| 38 | -ōr | t3-t002-00028 | bʰréh₁wr̥ NOM.PL | → **bʰréh₁wōr** | ✓conv. The rule is extrapolated (no handbook prints this word's collective) |
| 39–40 | -ōr | t3-t008-00038, t3-t013-00001 | dóh₃r̥ NOM.PL, ACC.PL | → **déh₃ōr** | ✓conv (Wiktionary coll. *déh₃or*) |
| 41 | -ōr | t3-t011-00023 | wódr̥ VOC.PL | → **wédōr** | ✓conv. Neuter, so voc. = nom. |
| 43 | i/u INS | t3-b001-00244 | gʷétu INS.SG | gʷtéwh₁ → **gʷtúh₁** | ✓conv. R p. 48 ǵustúh₁, drúh₁; F §6.10 *-u-h₁ |
| 44 | i/u INS | t3-t005-00032 | gʷr̥h₂ús INS.SG | → **gʷr̥h₂úh₁** | ✓conv. R p. 50 tn̥h₂úh₁ |
| 45 | override | t3-t014-00032 | bʰuH- IMP.2SG | bʰúHdʰi → **bʰuHdʰí** | ✓conv. R p. 30 *bʰuh₂-* unaccented outside the singular active; R p. 31 *-dʰí |
| 46 | D10 | t3-b002-00061 | h₁rudʰyos NOM.SG | → **h₁rudʰyom** | ✓. Agrees with gʷʰéros, lexicon gender n (Gk θέρος n.) |
| 47 | override | t3-t012-00018 | h₂wers- OPT.3SG | h₂ur̥syéh₁t → **h₂wr̥syéh₁t** | ✓. Zero grade *h₂wr̥s-* (LIV *h₂u̯ers-*). Syllabification: r̥ between w and s; *-yéh₁-* in the singular |
| 48 | r-n D1 | t3-t008-00015 | kéh₂nmn̥ LOC.SG | kh₂nméni → **kh₂n̥méni** | ✓. n between h₂ and m is syllabic; R p. 48 men-neuter loc. *-mén(i)* |
| 49 | override | t3-t016-00024 | bʰuH- OPT.3PL | → **bʰuHih₁ént** | ✓conv. R p. 30 *bʰuh₂-ih₁-*; F 3pl *-ent* |
| 50 | E1 | t3-b003-00061 | dedwóye PRF.3PL | deduyḗr → **dedwiyḗr** | ✓. Sievers (F §3.43): *-iy-* after the heavy *edw-*; *w* stays consonantal |
| 51 | override | t3-pilot-00105 | dayh₂wḗr DAT.PL | dayh₂urbʰós → **dayh₂wr̥bʰós** | ✓. R p. 49 ph₂tr̥bʰí; the weak *-wr̥-* parallels *-tr̥-* |
| 52 | override | t3-t016-00026 | néh₂us ACC.SG | néh₂um → **néh₂wm̥** | ✓. Ved. nā́vam, Hom. νῆα < *nāw-m̥ (Beekes, text file p0063: *neh₂us) |
| 53 | r-n D1 | t3-t005-00021 | h₂éḱmō ABL.SG | h₂ḱmnés → **h₂ḱm̥nés** | ✓ per the override's *-mn-* stem; the right-to-left syllabification is regular. The Asno-law *h₂ḱn̥-* reading stays open (INTEGRATION.md) |
| 54 | override | t3-t018-00014 | néh₂us LOC.SG | nh₂éwi → **néh₂wi** | ✓. Non-ablauting; Ved. nāví |
| 55 | override | t3-t021-00006 | dʰubʰrós n. NOM.SG | dʰubróm → **dʰubʰróm** | ✓. Root *dʰewbʰ-* keeps its aspirate (PGmc *dubraz*) |
| 56 | pronoun | t3-pilot-00129 | kʷo- GEN.SG | kʷésyo → **kʷósyo** | ✓conv. R p. 54 tósyo; R p. 201: *kʷésyo* belongs to *kʷi-/kʷe-*, not *kʷo-* |
| 57 | pronoun | t3-t003-00002 | relative DAT.SG | h₁yósmōy → **h₁yósmey** | ✓conv. Follows R p. 54 tósmey; B ch. 15 pronoun table (p. 228) *tosmōi* dissents (Ved. tásmai) and stays the alternative |
| 58 | R4 | t3-t005-00004 | h₂wekst- AOR.3PL | h₂wékst (3sg) → **h₂uksént** | ✓. Conjoined subject → plural (F §8.16); root aorist 3pl on the zero grade, *-ént* |
| 59 | R5 | t3-t008-00004 | pótnih₂ NOM.SG | pótni (voc.) → **pótnih₂** | ✓. F §8.11: the conjunct with *-kʷe* takes the nominative (vā́yav índraś ca) |
| 60 | D9 | t3-b004-00025 | déh₃nom ACC.DU | déh₃noy → **déh₃noyh₁** | ✓conv. F §6.50 *-o-ih₁*; R p. 49 yugóy(h₁) |

**Result:** 60/60 are right per the stated convention, with flags on #1 (the accent is assumed) and #37/#42 (the accent of *wédōr*; F §9.40 *u̯edṓr*). No new form is wrong.

**Sound rules in the new forms.**
- Laryngeals are written uncoloured throughout, unchanged from before (*bʰéh₂na*, *h₂wr̥s-*).
- Szemerényi applies where expected: *méh₂tēr* and *bʰṓr* (R5 nominatives), and *h₂nḗr* (unchanged).
- Sievers/Lindeman: *dedwiyḗr* after a cluster, *ḱluwént* after a cluster (unchanged), and *-w-/-y-* after a light syllable: *ḱl̥nwénti* (Ved. śr̥ṇvánti), *tr̥h₂wént*, *wn̥yéh₁s*.
- Syllabification: *h₂ḱm̥nés*, *kh₂n̥méni*, *déh₂n̥wōm*, *h₂wr̥syéh₁t*.

None violates the stated rules.

**Targeted checks outside the sample.**
- *h₁éddʰi*: Gk ἔσθι has root accent, which fits the Narten convention; Ved. addhí accents the ending. This is consistent with the convention.
- *néh₂us*: the NOM.SG is unchanged; the VOC *néh₂u* has a syllabic final.
- *dedh₃ih₁t* OPT.3SG follows R p. 30 *dʰé-dʰh₁-ih₁-* and B §18.8.4. Gk διδοίην and Ved. dadyā́t have *-yeh₁-*, which stays an alternative.
- *déh₂news*: wrong. See 6.1.

## 5. Sample of 40 unchanged tokens (seed 11)

**Scheme (`postcheck-unch.py`).** The pool is tokens whose form and features are identical before and after. Each token is assigned to one of the eight families by its spec. Per family, 3 tokens come from lexemes that changed elsewhere and 2 from untouched lexemes, as distinct types, using `random.Random(11)` over the sorted candidates.

| family | tokens (record) | verdict |
|---|---|---|
| athematic verbs | *dh₃té* IMP.2PL (t005-00037), *kʷéḱt* AOR.3SG (t018-00002), *h₁ésti* (t015-00016), *sn̥h₂ént* PST.3PL (t018-00011), *bʰéyh₂s* AOR.2SG (t008-00009) | all right. R p. 30 *h₁és-* ~ *h₁s-*; zero-grade 3pl *-ént*; Gk δότε |
| closed class | *tóm* (t014-00015), *kʷíh₁* INS (t021-00001), *tóns* (t014-00039), *h₁yód* (t007-00012), *dwóh₁* (t016-00026) | right. R p. 54; F §19.10 *kʷih₁*; F §6.13 *d(u)u̯oh₁* |
| feminine | *h₂wĺ̥h₁neh₂* NOM, *h₂wĺ̥h₁neh₂s* GEN (t016-00016, t018-00027), *lówksneh₂* (t007-00016), *bʰoydʰéh₂m*, *dʰoHnéh₂m* ACC (t018-00028, t019-00018) | right. R p. 49 (wool, grain); F §6.70 acc. *-eh₂-m* |
| i/u-stems | *polh₁úh₂* n. pl. (t013-00014), *h₁n̥gʷnís* (t018-00006), *h₂ówins* (t010-00015), *h₁ógʷʰim* (t006-00029), *h₂éngʷʰis* (t012-00004) | right. R pp. 47–48 h₂ówis, h₂ówins; Ved. agní-, purū́ |
| r/n-stems | *h₂nḗr* (t016-00009), *bʰréh₂tēr* (t013-00021), *méh₂ter* VOC (t019-00028), *sh₂imónm̥* (t012-00001), *ǵʰwḗrn̥s* (t016-00034) | right. Szemerényi; vocative with root accent (Gk μῆτερ); amphikinetic *-mon-* acc. *-onm̥* (R p. 47 léymonm̥) |
| s/root/heteroclite | *wódr̥* ACC.SG (t005-00027), *néh₂us* (t016-00028), *gʷówes* NOM.PL (t016-00028), *sélpos* (t005-00035), *sóh₂wl̥* (t003-00025) | right. R p. 46 *wódr̥*, *sóh₂wl̥*; R p. 198 *gʷów-es*; B *neh₂us* |
| thematic | *lewbʰós* (t009-00013), *deywóns* (t002-00026), *wiHróns* (t003-00020), *ḱoph₂óh₁* INS (b001-00104), *h₁éḱwoh₁* DU (t009-00009) | right. F §6.50 dual *-o-h₁*; R p. 49 *-ons* |
| thematic verbs | *h₂éǵesi* (t016-00036), *tréset* INJ (t003-00016), *h₂lékseti* (t015-00007), *gʷm̥yét* (t014-00008), *ḱléwsoh₂* (b001-00126) | right |

**No silent regressions in the 40.** I also scanned the whole corpus for leftovers of each convention: a vocative plural/dual with a non-initial accent; a consonant-stem dual in bare *-h₁*; an eh₂ VOC.SG in *-eh₂*; a devī ACC in *-ih₂m̥*; an i/u INS.SG in *-ewh₁/-eyh₁*; a 2du in *-th₁es*; a heteroclite in *-r̥h₂*; 'I' or 'ten' in an old form. Only the forms the conventions exempt remain: i/u and thematic duals, devī *pótnih₂h₁*, and *-uw-/-iy-* after a true cluster (*ḱluwént*, *tḱiyént*, *dedwiyéh₁t*). **The one exception is boukólos (6.2).**

## 6. Findings and proposed fixes

### 6.1 *déh₂nu* GEN/ABL.SG (4 tokens): the primary contradicts the source its override cites

The override (i-u #4) makes *déh₂nu* acrostatic "like dóru (Fortson §6.21, gen. *déru-s*)". Fortson §6.27 and the word index print the acrostatic genitive as ***déru-s***: e-grade root, zero-grade suffix. Beside it stands the newer proterokinetic *dr-éu-s*. The engine instead puts *déh₂news* first, with *déh₂nus* second. The cause is the `spec.weak is None` i/u branch in `_athematic` (pie/morph.py, the `suHnú- → suHnéws` comment), which puts the full-grade *-ew-s* first for every class. Fix, keeping *déh₂news* as an alternative:

```diff
         full = strong[:-1] + [Seg("e", "V", acc=strong[-1].acc), Seg(strong[-1].base, "R")]   # suHnú- → suHnéws
-        out["GEN.SG"] = out["ABL.SG"] = _uniq([render(_add(full, "s"))] + gen)
+        # acrostatic neuter u-stem (the dóru type): gen. *déru-s, zero-grade suffix (Fortson §6.21, §6.27)
+        dóru = spec.accent_class == "acrostatic" and neuter and strong[-1].base == "w"
+        fg = [render(_add(full, "s"))]
+        out["GEN.SG"] = out["ABL.SG"] = _uniq(gen + fg if dóru else fg + gen)
```

The scope is restricted on purpose. The only other `weak: null` acrostatic i/u lexemes are the masculine *póti*, *gʰóstipoti* and *wiḱpóti*, where *-eys* first is the intended choice (Ved. *-es*, Goth. *-ais*), and the condition leaves them untouched. *déh₂nu* is the only lexeme the fix changes: GEN.SG 2 and ABL.SG 2 tokens become *déh₂nus*. Leave DAT.SG *déh₂newey* and LOC.SG *déh₂newi* alone: Fortson prints no acrostatic dative or locative, and R p. 48 has *dréw(i)*. Also correct the override note's "Gives déh₂news/déh₂nus" to give the order the fix produces.

### 6.2 boukólos decision scope: *pérkus/pérkum* 13 tokens, *ḱm̥tógus* 6 tokens

The decision keeps *kʷ* before syllabic *u* only in the handbook thematic and eh₂ declensions (`_render_kw`). Its justification (thematic.md defect 1: "no book applies the rule before *u* in a reconstruction"; M&A) applies just as well to the u-stems. M&A in fact print ***pérkʷus*** 'oak' (word list, p. 160). Yet the athematic `render` still delabializes:
- `pie-lex-perkus`: NOM *pérkus*, ACC *pérkum*, but GEN *pr̥kʷéws* and INS *pr̥kʷúh₁*. This is even though its own sweep override (#13) sets the strong stem to *pérkʷu*.
- `pie-lex-kjmtogwus` (headword *ḱm̥tógʷus*): NOM *ḱm̥tógus*.

So the corpus now has *pérkʷunos* beside *pérkus*. Two options for the lead, either of which makes the corpus consistent:
- (a) Extend the decision to the handbook athematic declension: render with `delabialize(before_u=False)` and append `_with_delabialized`, as the thematic path does. The Wiktionary convention, and with it the crosscheck's *ḱm̥tógus* table, keeps its full scope.
- (b) Revert *pérkʷunos* to *pérkunos* (Fortson §3.39 states boukólos as a PIE rule).

Fortson and M&A disagree here, so this is a convention choice. I recommend (a), because it follows the decision as recorded.

### 6.3 Flags, no change proposed

- *wédōr* accent: R p. 45 *wédōr* (and Wiktionary) vs F §9.40 *u̯edṓr*.
- *h₁eǵóh₂* accent: assumed (already flagged in STATUS).
- *h₂ḱm̥n-* vs the Asno-law *h₂ḱn̥-*: already open in INTEGRATION.md.
- *suHnús*'s weak *suHnów-* (*suHnóws*, *suHnówey*, *suHnówi*: 18 tokens, unchanged) sits against the *-éw(i)* u-stem convention. This is i-u #7, which INTEGRATION.md lists as not applied (L&Y/Fortson/Ringe *-éw-* vs Beekes/Wiktionary). It is not a regression, but it is the largest unchanged token group that the u-stem convention does not cover.

## 7. Alternatives kept (STATUS: "the other form stays an alternative")

The check (`postcheck-alts.py`, every distinct sweep change) asks whether the old form is still in `Lexicon.cells(...)` for the cell. The counts are distinct-change tokens.

| decision | lexeme checked | old form | status |
|---|---|---|---|
| eh₂ vocative *-a* | lewkos f. VOC.SG | léwkeh₂ | **cell** (all 17) |
| devī acc. *-ih₂m* | pótnih₂ ACC.SG | pótnih₂m̥ | **cell** (all 22) |
| u-stem loc. *-ḗw* | sweh₂dús LOC.SG | (added) | **cell**: sweh₂déwi, sweh₂déw, sweh₂dḗw; gʷréwi, gʷréw, gʷrḗw. The *-ḗw* alternative is missing where the weak stem has o-grade (suHnówi, suHnów), which is by design: i-u #2 restricts it to e-grade weak stems |
| u-adjective accent | gʷr̥h₂ús NOM.SG | gʷréh₂us | `extra_specs` only (all 65), documented in INTEGRATION.md "Override displacement"; validator recognizes *gʷréh₂us*, *swéh₂dus*, *pléth₂us* (exact) |
| vocative pl./du. retraction | deywós VOC.PL | deywṓs | **cell** (all 56) |
| consonant-stem dual *-h₁e* | gʷṓws NOM.DU | gʷówh₁ | **cell** (all 68) |
| *h₁ed-* Narten | h₁édti PRS.3PL | h₁dénti | `extra_specs` only (documented); validator recognizes *h₁dénti*, *h₁ddʰí* |
| *ḱéyor* | kjeytor MID.PRS.3SG | ḱéytor | **cell** (all 79) |
| *dédeh₃ti* mobile | PRS.1PL | dédh₃mes | `extra_specs` only (documented); validator recognizes *dédh₃mes* |
| 2du *-tes* | h₁ésti PRS.2DU | h₁sth₁és | **cell** (all 9) |
| 'I' | personal/1 NOM.SG | h₁eǵ | **cell**: h₁eǵóh₂, h₁eǵoh₂, eǵoh₂, h₁eǵ, éǵh₂, eǵh₂óm |
| 'ten' | numerals/10 | déḱm̥t | **cell**: déḱm̥, déḱm̥t, déḱm̥d |
| boukólos | perkwunos NOM.SG | pérkunos | **cell** (all 49) |

**No alternative is missing.** The "gone" old forms belong to defect fixes, not convention decisions, and none needs to be kept:
- E1 *ḱl̥nuwénti*;
- the table errors *dʰubróm*, *nh₂éws*, *h₂ŕ̥ǵn̥tom*, *h₃ókʷs*;
- *h₂ḱmnés* and *médos* (accentless).

One cosmetic point: my `extra_specs` check did not regenerate *h₁ed-*'s injunctive (*h₁éds*, *h₁édt*) or its participle (*h₁dóntes*), because those cells are derived outside `conjugate`. The validator, though, does recognize all three: `analyze_token` returns `exact`, with analyses under pie-lex-h1edti and pie-lex-h1edt.
