# Engine sweep: i-stems and u-stems

Auditor family: i- and u-stem nouns (acrostatic, proterokinetic, suffix-accented "hysterokinetic") and u/i-stem adjectives with their *-wih₂/-yih₂* feminines. Engine state: `pie/morph.py` as of 2026-10-23 (handbook convention, primary form = first in cell). Scratch files: `scratchpad/iu_*` (inventory, cell dumps, checks, patched copy `iu_repo/`, impact join).

## 0. Summary

**16 defects** (11 spec, 4 code, 1 lexicon routing), plus 6 places where the handbooks disagree with each other, each needing a convention decision. Corpus impact is counted over tier-3 tokens with the lexeme + feature whose primary form would change. The family has 2,351 tokens over 59 lexemes in `corpus/tier3/` (of 42,017).

| # | Defect | Kind | Tokens | Certainty |
|---|---|---|---|---|
| 1 | u-adjectives barytone (*pléth₂us, gʷréh₂us, swéh₂dus…*) where Vedic+Greek and L&Y have suffix accent + zero-grade root | spec (8 lexemes) | ~65 | handbooks disagree, see §6 |
| 2 | u-stem LOC.SG has no lengthened-grade *-ḗw* at all | code | 43 (+6 néh₂us) | Beekes vs Ringe, see §2 |
| 3 | i-stem (PK/HK) LOC.SG primary *-éy*, not *-ḗy* (the acrostatic type already gets *-ēy* first) | code | 34 | Ringe p. 20 + Beekes agree |
| 4 | *déh₂nu*: weak stem = strong minus accent (*deh₂n̥wés*, unaccented full-grade root) | spec | 26 | clear |
| 5 | i/u INS.SG built on the full-grade suffix (*mn̥téyh₁, dréwh₁, gʷréwh₁*) | code | 25 (+2 péḱu) | all handbooks agree |
| 6 | *néh₂us* 'ship' given a zero-grade root (*nh₂éws*) and u-stem *-um* | spec (hand override) | 23 | clear |
| 7 | *suHnús* weak stem *-ów-* throughout (*suHnówey*) | spec | 18 | L&Y/Fortson/Ringe vs Wiktionary/Beekes |
| 8 | *HeHḱús* weak/fem with zero-grade root *HHḱ-* (Ved. *āśáv-*, Gk *ὠκέ(w)-*) | spec (hand override) | 13 | clear |
| 9 | *swéh₂dus* weak *suh₂déw* zero-grade root (Ved. *svādáv-*, Gk *ἡδέ(w)-*) | spec | 0 obliques (direct cases under #1) | clear |
| 10 | *péḱu* override weak *péḱew*: *péḱewh₁, péḱewbʰos* | spec (hand override) | 2 | clear |
| 11 | *Hrugʰís*, *bʰeh₂ǵʰús*: NOM.SG from the oxytone lemma, all other cells from a root-accented table stem | spec | 1 | clear |
| 12 | *h₁léngʰus*: *gʷʰ* only in m_weak (*h₁ln̥gʷʰéws* vs fem *h₁ln̥gʰéwih₂*) | spec (Wiktionary args) | 1 | clear |
| 13 | *pérkus*: strong *pérku* (plain k) vs weak *pr̥kʷéw* (NOM.PL *pérkewes*) | spec | 0 | clear |
| 14 | *ḱm̥tógʷus*: weak/fem stems carry two accents (*ḱm̥tógʷóws*; 79 cells) | spec (Wiktionary args) | 0 | clear |
| 15 | neuter dual: *móryih₁* (i-stem), *ml̥dúyh₁ / polh₁úyh₁* (oxytone u) | code | 0 | clear |
| 16 | open lexeme *pie-lex-treyes* 'three' usable, with singular cells and unaccented *trēy, treys* | lexicon | 0 | clear (closed class covers '3') |

Top 3 by corpus impact: #1, then #2 + #3 (the locative, 77 tokens together), then #5 and #4 (about 26 each). #5 is the most secure: Fortson, Ringe and Beekes all agree on it, and the fix is one line. The code fixes (§7) are three independent hunks, all gated to the handbook convention, so the Wiktionary crosscheck is unaffected. With them applied, test_morph, test_morph_r2_fixes, test_realize, test_validate, test_backtest and test_classify pass (152 tests, run in the scratch copy).

**Stale corpus (not a live defect):** 121 of the 136 *HeHḱus* tokens are root-accented (*HéHḱus, HéHḱewes, HéHḱuns, HéHḱuh₁*). They predate the t021 override, and the engine now gives *HeHḱús*. They only need regenerating. No other family lexeme has stale forms.

## 1. Inventory

The usable lexemes are those whose strong stem ends in syllabic *-i/-u* (for adjectives, the 4-argument specs). There are 72, from `scratchpad/iu_inv.py`:

| Sub-type | Lexemes (corpus tokens) |
|---|---|
| acrostatic i-stem nouns | h₂ówis 234, h₁ógʷʰis 150, pótis 95, gʰóstipotis 64, wiḱpótis 53, h₂óḱris 6 |
| proterokinetic i-stem nouns (-ti- abstracts and others) | gʰóstis 167, mértis 60, h₁léwdʰis 47, h₂éngʷʰis 43, h₂éwis 28, kʷyéh₁tis 12, méntis 9, Hrugʰís 8, ǵénh₁tis 5, ḱlównis 4, wéh₁itis 4, déh₃tis 3, wéstis 1, déh₂itis 1, kʷŕ̥mis 1; plus bʰértis, dʰéh₁tis, dʰgʷʰéytis, gʷémtis, gʷʰéntis, h₁éytis, h₁órǵʰis, stéh₂tis, téntis (0) |
| proterokinetic u-stem nouns (-tu- and others) | kéh₃tus 51, néh₂us 44, pérkus 22, pértus 17, ǵéwstus 8, bʰeh₂ǵʰús 7, bʰébʰrus 4, smérus 3 |
| suffix-accented ("hysterokinetic", accent_class null) | suHnús 173, h₁n̥gʷnís 168 |
| amphikinetic | déh₂nu (n.) 98, ǵénus 1 |
| neuters i/u (PK) | móri 112, gʷéru 48, dóru 32, médʰu 31, h₂éḱru 15, dáḱru 6, gʷétu 5, ǵónu 2, péyh₂tu 2, h₂óyu 0 |
| acrostatic neuter | péḱu 13 |
| u-adjectives | h₁wésus 167, HeHḱús 136, polh₁ús 48, gʷréh₂us 27, swéh₂dus 19, néḱus 18, h₁wérHus 16, bʰérǵʰus 15, pléth₂us 13, h₁léngʰus 9, ml̥dús 7, ḱm̥tógʷus 6, mréǵʰus 4, bʰénǵʰus 4, h₂énǵʰus 3, tégus 2; dléwkus, ténh₂us 0 |
| i-stem numeral | tréyes (open lexeme, 0; corpus uses `closed:numerals/3`, 50) |

Not audited: 273 unusable shape-rule lexemes (`shape:pk-iu-stem` 228, backtest 84.7%; `shape:hk-iu-stem` 47, backtest 45.3%). They never reach the corpus. The code fixes in §7 apply to them automatically. The *pk-iu-stem* rule zeroes the root even when the root cannot ablaut (it is the source of defect #6).

Genders are right in effect: the -ti- abstracts carry spec gender *m*, but `Lexicon.gender` takes the lexicon's *f* first.

Mechanical scans over every cell of all 72 (`iu_check.py`, `iu_scan.py`) checked three things: the number of accents per form, accented *ú/í* in hiatus, and the NOM.SG vs ACC.SG accent position. They also compared consonant skeletons, strong vs weak and m vs f. These scans found #11–#16. No weak stem drops a consonant.

## 2. Proterokinetic i-stems (*méntis* type) and u-stems (*ǵéwstus* type)

Reference paradigms: Ringe 2006 §2.3.4(iii), p. 47 (thought f., taste m., sea n., tree n.), and Beekes 2011 §13.2.6a, p. 203 (PD u-stem, with "the PD i-stems are completely parallel"). Fortson 2010 §§6.10, 6.22 and 6.42.

**Right:** NOM *méntis*, ACC *méntim*, GEN *mn̥téys*, DAT *mn̥téyey*, NOM.DU *méntih₁*, NOM.PL *ménteyes*, ACC.PL *méntins*, GEN.PL *mn̥téyōm* (Ringe *-oHom*; handbook *-ōm* is the project convention, Fortson §6.16), obliques *mn̥tíbʰos/mn̥tímos/mn̥tísu* on the accented zero-grade suffix (Ringe; the existing `_zero_grade_iu`). The same holds for the u-stem *ǵéwstus, ǵustéws, ǵustéwey, ǵéwstewes, ǵéwstuns, ǵustúsu*. Gender, Szemerényi and the ACC.PL *-ns* are fine.

**Wrong:**

- **#5 INS.SG.** The engine gives *mn̥téyh₁, ǵustéwh₁, kh₃téwh₁, gʷréwh₁* as primary. All three handbooks have the zero-grade suffix with bare *-h₁*: Ringe pp. 47 and 49 *mn̥tíh₁, ǵustúh₁, mríh₁, drúh₁, tn̥h₂úh₁*; Fortson §6.10 (Ved. *matī́* < *-i-h₁*, *-u-h₁*); Beekes §13.2.2, p. 187 (ins. *-h₁* "as found in the i- and u-stems") and §13.2.6a *-u-h₁*. Wiktionary's own tables agree (*h₁ln̥gʷʰúh₁*); only the engine's handbook branch differs, because it builds INS.SG from `obl` (the plain weak stem) while the oblique plural uses `obl_pl`. Fix: patch A (§7).
- **#3 LOC.SG, i-stems.** The engine gives *mn̥téy / mn̥tḗy*. Ringe p. 20 (§2.2.4, Stang's law) says the i-stem locative */-ey-i/* surfaced as *-ēy*; his table prints *mn̥téy (-ēy)*. Beekes §13.2.2 p. 187 and §13.2.6a reconstruct the endingless lengthened grade (Ved. *agnā́*, Gk *πόληι*). The engine already puts *-ēy* first for the acrostatic type (*h₂éwēy*), so the PK and HK order is also internally inconsistent. Fix: patch B, which makes *-ḗy* primary with *-éy* kept as an alternative.
- **#2 LOC.SG, u-stems.** The engine gives *ǵustéwi / ǵustéw*, with no *-ēw* form at all. Beekes §13.2.6a gives *-ēu* (Ved. *sūnáu*, Goth. *sunau*), and Beekes p. 187 notes the endingless locative has "full or lengthened grade" (*-ēn, -ēu*). Ringe p. 47 prints *ǵustéw(i), dréw(i)*. **Disagreement:** I propose *-ḗw* primary, for symmetry with *-ḗy* and because the brief lists it as a form of this family, with Ringe's *-éwi, -éw* kept as alternatives. The minimum fix is to add *-ḗw* as an alternative (patch B without the reordering).
- Vocative: see §8 (a disagreement, not a defect).

## 3. Acrostatic i-stems (*h₂ówis*, *pótis*)

Ringe pp. 46–47 (sheep, f.): *h₂ówis, voc. h₂ówi, acc. h₂ówim, ins. h₂éwih₁, dat. h₂éwyey, gen. h₂éwis* (later *-yos*), du. *h₂ówih₁e*, pl. *h₂óweyes, h₂ówins, h₂éwibʰi, h₂éwimos, h₂éwyoHom, h₂éwisu*. Fortson §6.21.

**Right:** every cell except the vocative order matches Ringe (with the *-ōm, -bʰos, -bʰis* conventions). GEN.SG adds *h₂éweys* (Beekes, L&Y §2.1.1). *pótis, wiḱpótis, gʰóstipotis* have no weak stem and get the full-grade *-ey-* forms first (*póteys, póteyey*: Ved. *-pates, -pataye*). That is a sound choice. The patches leave this type unchanged (tested: *h₂éwih₁*, *h₂éwēy*).

## 4. Suffix-accented i/u-stems (*h₁n̥gʷnís*, *suHnús*)

**Right:** *h₁n̥gʷnís, -ním, GEN h₁n̥gʷnéys* (Ved. *agnés*; L&Y §2.1.1 *-ey-s*), *DAT h₁n̥gʷnéyey, NOM.PL h₁n̥gʷnéyes*, obliques *h₁n̥gʷníbʰos*.

**Wrong:**

- INS.SG and LOC.SG as in §2 (*h₁n̥gʷnéyh₁ → h₁n̥gʷníh₁*, *h₁n̥gʷnéy → h₁n̥gʷnḗy*).
- **#7 suHnús weak *suHnów-*.** This is Wiktionary's argument and Beekes's genitive (Beekes Exercise 32b p. 193, and §13.2.6a gen. *-ou-s*). But Beekes has *-eu-* in the dative, locative and plural, and Ringe (*ǵustéws, ǵustéwey*), Fortson §6.42 (gen. *-eu-s*) and L&Y §2.1.1 (Ved. *sūnó-s*, Goth. *sunau-s*, OCS *synu* < *-ew-s*) all use *-éw-*. The engine has a single weak stem, so it cannot split the ablaut by case. I recommend the majority *suHnéw-*: *suHnéws, suHnéwey, suHnḗw, suHnéwōm*. This affects 18 tokens (DAT 12, GEN 3, LOC 2, GEN.PL 1).

## 5. Neuters

**Right:** *móri, dóru, médʰu, ǵónu*: NOM/ACC = bare stem; GEN *mréys, dréws*; DAT *mréyey, dréwey*; NOM.PL *mórih₂, dóruh₂*; obliques *mríbʰos, drúsu*; NOM.DU *dórwih₁* (Ringe p. 47). The PK analysis with o-grade direct cases follows Ringe p. 45 (*móri, mréy-; dóru, dréw-; ǵónu, ǵnéw-*) and Fortson §6.27 (*dr-éu-s*), and is right.

**Wrong:**

- INS.SG and LOC.SG as in §2 (*mréyh₁ → mríh₁*, *dréwi → drḗw*).
- **#15 dual.** The engine gives *móryih₁*. Ringe p. 47 has *mórīh₁ (?)*, and Fortson §6.13 *h₃ekʷih₁* 'both eyes' (OCS *oči*), i.e. *i + ih₁ → ih₁*. Oxytone u-neuters come out as *ml̥dúyh₁, polh₁úyh₁, HeHḱúyh₁*: the junction keeps the accented *ú* syllabic and turns the ending's *i* into a glide. The correct form is *-wíh₁*, as in Fortson §6.13's own example, Ved. *urv-ī́*. Fix: patch C. Corpus impact is 0, but the error spreads to every oxytone u-adjective if #1 is adopted.
- **#4 déh₂nu** (98 tokens, 26 affected). The spec is "amphikinetic" with weak *deh₂nu*, which is just the strong stem with the accent removed (Wiktionary's argument 2). It yields *deh₂n̥wés, deh₂n̥wéy, deh₂n̥wṓm*: a full-grade root without accent, which no ablaut class allows. It does not match any u-stem paradigm in Fortson §§6.21–6.22 or Ringe pp. 44–45. Ved. *dā́nu-* has fixed root accent, so the acrostatic type fits, like Fortson §6.21 *dóru* (gen. *déru-s*). The *-h₂n̥w-* syllabification itself is regular under right-to-left syllabification; it disappears once the oblique suffix is in the full grade. Proposed override: §9.
- **#10 péḱu** (hand override, weak *péḱew*). It yields INS *péḱewh₁* and obliques *péḱewbʰos*: a full-grade suffix before consonant endings, under root accent. That matches no type: acrostatic keeps the zero-grade suffix (Ringe *h₂éwibʰi*), and proterokinetic moves the accent. Wiktionary's table is proterokinetic *pḱéw-*, and Fortson's *pk̑u-i̯ent-* (OAv. *fšuiiąs*, Fortson §11.19) attests the zero-grade root. Recommend reverting to Wiktionary (*pḱéws, pḱúh₁, pḱúbʰos*). The alternative is weak null, acrostatic (*péḱews/péḱus, péḱuh₁, péḱubʰos*).

## 6. u-adjectives (masc./neut.) and the -wih₂ feminine

Ringe §2.3.5, pp. 49–50 ('thin', u-stem, proterokinetic): m. *ténh₂us, voc. ténh₂u, acc. ténh₂um, ins. tn̥h₂úh₁, dat. tn̥h₂éwey, gen. tn̥h₂éws, loc. tn̥h₂éw(i)*; du. *ténh₂uh₁*; pl. *ténh₂ewes, ténh₂uns, tn̥h₂úbʰi, tn̥h₂úmos, tn̥h₂éwoHom, tn̥h₂úsu*. Fem. *tn̥h₂éwih₂, voc. tn̥h₂éwi, acc. -ih₂m̥, gen. tn̥h₂uyéh₂s*… pl. *tn̥h₂éwih₂es, -ih₂n̥s, tn̥h₂uyéh₂bʰi*. Neut. *ténh₂u*, du. *ténh₂uih₁*, pl. *ténh₂uh₂*.

**Right:** apart from INS.SG and LOC.SG (§2), the masculine and neuter match Ringe cell for cell. The feminine matches Ringe in every cell (vocative with retracted accent, by convention; Ringe's form is the alternative). ml̥dús and polh₁ús (oxytone) decline correctly, including NOM.PL *ml̥déwes*.

**#1 Accent class (disagreement; ~65 tokens).** The spec copies Wiktionary's first, root-accented table (*pléth₂us, gen. pl̥th₂éws*). That table matches Ringe's model and Fortson §6.29 (*krétus*, *kr̥téus*). Lundquist & Yates (Handbook vol. 3, ch. 122 §2.5 and §3.2) argue explicitly from Vedic + Greek for a zero-grade root with fixed suffix accent: *gʷr̥h₂-éw-* (Ved. *gurú-*, Gk *βαρύς*), *pl̥th₂-ú-* (*pr̥thú-*, *πλατύς*), *h₁ōḱ-ú-* (*āśú-*, *ὠκύς*), *sweh₂d-ú-* (*svādú-*, *ἡδύς*), *urú-/εὐρύς*. Mallory & Adams write *pl̥th₂us* and *swehadús*. Wiktionary's own pages carry the oxytone variant as a second table for 9 of these lexemes (`extra_specs`, accent_class "hysterokinetic"). The project has already sided with the oxytone forms for *HeHḱús* (t021 review), and the brief cites *pl̥th₂ús*. **Recommendation:** follow L&Y wherever Vedic and Greek agree on suffix accent, by promoting the extra spec to primary: gʷr̥h₂ús, h₁wr̥Hús, pl̥th₂ús, sweh₂dús, h₁ln̥gʷʰús (Ved. *raghú-*, Gk *ἐλαχύς*), mr̥ǵʰús (Gk *βραχύς*), dlukús (Gk *γλυκύς*), bʰn̥ǵʰús (Ved. *bahú-*, Gk *παχύς*). tn̥h₂ús (Ved. *tanú-*) gets the same treatment, but it is Ringe's own model word, so I flag it. Keep root accent for h₁wésus (Ved. *vásu-*), néḱus (Gk *νέκυς*), bʰérǵʰus, tégus and h₂énǵʰus (no Vedic+Greek pair). Only the direct cases change. The obliques are identical (*pl̥th₂éws*).

**#8 HeHḱús** override: weak *HHḱéw-* and fem *HHḱéwih₂* have a zero-grade root. The daughters show a long root vowel in every case (Ved. *āśáv-*, Gk *ὠκέος*; L&Y *h₁ōḱ-éw-*). This should be *HeHḱéw-*. It also fixes the accentless vocative *HHḱewi* that `_initial_accent` returns for an *HHC-* onset. **#9** is the same issue in *sweh₂dús* (weak *suh₂déw* → *sweh₂déw*; L&Y *sweh₂d-éw-*).

**Feminine (disagreement, not changed):** the engine, Ringe and Wiktionary have *-éwih₂ / -uyéh₂*. L&Y §3.2 have *-w-íh₂* with accent on the feminine suffix (Ved. *pr̥thvī́, svādvī́, urvī́*; Gk *Plataiaí*). Following L&Y here would need a fourth stem shape for every adjective. I recommend keeping Ringe.

**#12 h₁léngʰus:** Wiktionary's template arguments mix *gʷʰ* (arg 2) and *gʰ* (args 3–4). The root is *h₁lengʷʰ-* (Ved. *raghú-*, Gk *ἐλαχύς*, Lat. *levis*). `delabialize` already writes *gʰ* before *u* (as with *ḱm̥tógus*), so all four stems should carry *gʷʰ*. **#14 ḱm̥tógʷus** 'having 100 cows': Wiktionary's args *ḱm̥tógʷów, ḱm̥tógʷówih₂* have two acutes. As a bahuvrihi it keeps the first member's accent (Ved. *śatá-gu-*): *ḱm̥tógʷow-*.

## 7. Code fixes (pie/morph.py)

The three hunks are independent; each changes only `conv == "handbook"`. They were checked with `patch --dry-run` against the current file.

**Patch A — INS.SG on the zero-grade suffix (#5).**

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ -247,6 +247,11 @@
         out["DAT.SG"] = _uniq([render(_add(full, "ey"))] + out["DAT.SG"])
 
     out["INS.SG"] = [w("éh₁", "h₁", obl)]
+    if hb and obl_pl is not weak:
+        # i/u-stem instrumental *-i-h₁/*-u-h₁ on the accented zero-grade suffix: Fortson §6.10 (Ved. matī́),
+        # Ringe 2006 pp. 47, 49 (mn̥tíh₁, ǵustúh₁, mríh₁, drúh₁, tn̥h₂úh₁), Beekes §13.2.6a (*-u-h₁).
+        # The full-grade form (mn̥téyh₁) follows as an alternative.
+        out["INS.SG"] = _uniq([render(_add(obl_pl, "h₁"))] + out["INS.SG"])
     out["LOC.SG"] = _locative(spec, strong, weak, hb)
```

(`obl_pl is not weak` holds exactly when `_zero_grade_iu` fired, i.e. a true i/u-stem whose weak stem has an accented *-éy/-éw/-óy/-ów*. Acrostatic *h₂éwi-* and root nouns like *gʷṓws* are untouched.)

**Patch B — LOC.SG *-ḗy* first, and *-ḗw* added for u-stems (#2, #3).**

```diff
@@ -251,3 +256,3 @@
     if hb:   # prefer the -i (or i-stem -ēy) locative to the endingless one (which looks like the nominative)
-        out["LOC.SG"] = sorted(out["LOC.SG"], key=lambda f: not f.endswith(("i", "í", "y")))
+        out["LOC.SG"] = sorted(out["LOC.SG"], key=lambda f: not f.endswith(("i", "í", "y", "ḗw", "ṓw")))
@@ -370,8 +382,16 @@ def _locative(...)
         if len(s) >= 2 and s[-1].base == "y" and not s[-1].syl and s[-2].base == "e" and s[-2].acc:
             out.append(render(lengthen_last_vowel(s)))  # -éy → -ḗy (bʰr̥tḗy)
+            if hb and strong[-1].syl and strong[-1].base == "y":
+                # *-ey-i > *-ēy (Ringe 2006 p. 20, Stang's law; Beekes §13.2.6a; Ved. agnā́): -ḗy first
+                out[-2:] = out[-2:][::-1]
         else:
             out.append(render(_add(s, "i")))
+            if hb and strong[-1].syl and strong[-1].base == "w" and len(s) >= 2 and s[-1].base == "w" \
+                    and not s[-1].syl and s[-2].base in ("e", "o") and s[-2].acc:
+                # u-stem endingless locative in the lengthened grade *-ēw (Beekes §13.2.6a; Ved. sūnáu,
+                # Goth. sunau), parallel to i-stem *-ēy; Ringe's -éw(i) follow as alternatives
+                out.insert(len(out) - 2, render(lengthen_last_vowel(s)))
     return _uniq(out)
```

The guard on `strong[-1].syl` restricts the change to true i/u-stems. Diphthongal root nouns (*gʷṓws*, *dyḗws*) and other *-éy/-éw* weak stems keep their current locatives. If the convention call goes Ringe's way for u-stems, drop the `"ḗw", "ṓw"` from the sort key: *-éwi* then stays primary and *-ḗw* becomes an alternative. **Dependency:** on its own, patch B turns *suHnów-* into a primary LOC *suHnṓw* (2 tokens), a form no handbook prints. It becomes *suHnḗw* only together with the suHnús override (#7, §9), so take both or neither for that lexeme.

**Patch C — neuter dual of i/u-stems (#15).**

```diff
@@ -255,6 +267,13 @@
         e_grade_s = len(weak) > 1 and weak[-1].base == "s" and weak[-2].base == "e"
         du = [render(_add(weak if (e_grade_s and spec.weak) else strong, "ih₁"))]
+        if hb and strong[-1].syl and strong[-1].base in ("y", "w"):
+            if strong[-1].base == "y":
+                # i-stem: -i-ih₁ → -ih₁ (Fortson §6.13 *h₃ekʷih₁ 'both eyes'; Ringe p. 47 mórīh₁ (?))
+                du = [render(_add(strong[:-1], "ih₁" if not strong[-1].acc else "íh₁"))]
+            elif strong[-1].acc:
+                # accented -ú + ih₁ → -wíh₁ (Ved. urvī́, Fortson §6.13), not -úyh₁
+                du = [render(_add(strong[:-1] + [Seg("w", "R")], "íh₁"))]
     else:
```

The hunk headers above are abbreviated; the exact unified diff of all three hunks (checked with `patch --dry-run -p1`) is in Appendix A.

**Tests to add** (e.g. `tests/test_morph_iu_stems.py`). All three fail on the current engine and pass with the patches:

```python
from pie.morph import AdjSpec, NounSpec, decline, decline_adj

def cell(spec, feat):
    return decline(spec, "handbook")[feat]

def test_iu_instrumental_on_zero_grade_suffix():      # Ringe pp. 47, 49; Fortson §6.10; Beekes §13.2.6a
    assert cell(NounSpec("ménti", "mn̥téy", "proterokinetic", "f"), "INS.SG")[0] == "mn̥tíh₁"
    assert cell(NounSpec("ǵéwstu", "ǵustéw", "proterokinetic", "m"), "INS.SG")[0] == "ǵustúh₁"
    assert cell(NounSpec("dóru", "dréw", "proterokinetic", "n"), "INS.SG")[0] == "drúh₁"
    assert cell(NounSpec("móri", "mréy", "proterokinetic", "n"), "INS.SG")[0] == "mríh₁"
    assert cell(NounSpec("h₁n̥gʷní", "h₁n̥gʷnéy"), "INS.SG")[0] == "h₁n̥gʷníh₁"
    assert cell(NounSpec("h₂ówi", "h₂éwi", "acrostatic", "f"), "INS.SG") == ["h₂éwih₁"]
    assert "mn̥téyh₁" in cell(NounSpec("ménti", "mn̥téy", "proterokinetic", "f"), "INS.SG")
    adj = decline_adj(AdjSpec("ténh₂u", "tn̥h₂éw", "tn̥h₂éwih₂", "tn̥h₂uyéh₂", "proterokinetic"))
    assert adj["m"]["INS.SG"][0] == adj["n"]["INS.SG"][0] == "tn̥h₂úh₁"
    assert adj["f"]["INS.SG"][0] == "tn̥h₂uyéh₂h₁"

def test_iu_locative_lengthened_grade():              # Ringe p. 20; Beekes §13.2.6a
    assert cell(NounSpec("ménti", "mn̥téy", "proterokinetic", "f"), "LOC.SG") == ["mn̥tḗy", "mn̥téy"]
    assert cell(NounSpec("ǵéwstu", "ǵustéw", "proterokinetic", "m"), "LOC.SG") == ["ǵustḗw", "ǵustéwi", "ǵustéw"]
    assert cell(NounSpec("h₂ówi", "h₂éwi", "acrostatic", "f"), "LOC.SG")[0] == "h₂éwēy"
    assert cell(NounSpec("pód", "ped", "acrostatic", "m", nom_sg="pṓds", loc_sg=["péd"]), "LOC.SG")[0] == "pédi"
    assert decline(NounSpec("ǵéwstu", "ǵustéw", "proterokinetic", "m"), "wiktionary", False)["LOC.SG"] == \
        ["ǵustéw", "ǵustéwi"]

def test_iu_neuter_dual():
    assert cell(NounSpec("dóru", "dréw", "proterokinetic", "n"), "NOM.DU")[0] == "dórwih₁"
    assert cell(NounSpec("móri", "mréy", "proterokinetic", "n"), "NOM.DU")[0] == "mórih₁"
    adj = decline_adj(AdjSpec("ml̥dú", "ml̥déw", "ml̥déwih₂", "ml̥duyéh₂", "proterokinetic"))
    assert adj["n"]["NOM.DU"][0] == "ml̥dwíh₁"
```

## 8. Handbook disagreements (convention notes, no change proposed)

- **Vocative of i/u-stems.** The engine's primary is the full-grade suffix (*h₂ówey, méntey, súHnew, h₁ń̥gʷney*; 160+ tokens). That follows Beekes §13.2.2 p. 186 ("characterized by the e-grade of the suffix"; Ved. *ágne, sū́no*, Goth. *sunau*). Ringe pp. 46–47, 49 (*h₂ówi, ménti, ǵéwstu, ténh₂u*) and Fortson §6.7 (Gk *póli*) give the bare stem, which the engine keeps as the alternative. This is defensible; keep it.
- **GEN.PL** *-ōm* (Fortson §6.16) vs Ringe *-oHom* and Beekes *-om*: project convention.
- **INS/DAT/ABL.PL** *-bʰis/-bʰos* vs Ringe *-bʰi, -mos*: project convention (not specific to this family).
- **u-stem LOC.SG** *-ḗw* (Beekes) vs *-éw(i)* (Ringe), and **suHnús** *-ów-* (Beekes gen., Wiktionary) vs *-éw-* (Ringe, Fortson, L&Y): §§2, 4.
- **u-adjective accent** (Ringe/Fortson root accent vs L&Y/M&A suffix accent) and **feminine** *-éwih₂* vs *-w-íh₂*: §6.
- L&Y §3.2 doubt that the *-ti-* abstracts were ever proterokinetic (Ved. *jūtí-* has fixed suffix accent). Ringe p. 45 and Fortson §6.22 are explicit that they were, so keep the current analysis.

## 9. Proposed overrides (data/lexicon/overrides.jsonl)

Specs merge into the derived spec (`{**spec, **override}`; `null` clears a field). An id that already has a line must be **edited, not duplicated**: a later line replaces the earlier `spec_override` entirely. This applies to pekju (line 15), neh2us (line 12) and HeHkjus (line 70). The token counts are the cells whose primary form changes once the code patches are applied.

**Validator index.** An override replaces the derived spec, so the forms it displaces (*pléth₂us…*, *suHnóws*, *HHḱéw-*, *nh₂éw-*) leave the primary spec. `pie/validate.py` (line 129) also indexes `extra_specs`, so the integrator can keep any displaced spec there. For the nine oxytone adjectives, Wiktionary's root-accented table and its oxytone table simply swap places. Tier 1 risk is nil: the only family forms in corpus/tier1 are *súHnus/súHnum* (Byrd, King and God; direct cases, untouched by #7), and none of the affected stems occur in raw/tier1-*.

Defects (no convention call needed):

```json
{"id": "pie-lex-deh2nu", "spec": {"weak": null, "accent_class": "acrostatic", "loc_sg": ["déh₂new"]}, "spec_checked": true, "note": "Ved. dā́nu- has fixed root accent: acrostatic like dóru (Fortson §6.21, gen. *déru-s); the Wiktionary weak arg is the strong stem minus its accent (deh₂n̥wés: unaccented full-grade root). Gives déh₂news/déh₂nus, déh₂newey, loc. déh₂newi, déh₂nubʰos (engine sweep i-u-stems #4)"}
{"id": "pie-lex-neh2us", "meaning": ["boat, ship"], "gender": "f", "spec": {"strong": "néh₂w", "weak": "neh₂w", "accent_class": null, "gender": "f"}, "spec_checked": true, "note": "mobile root noun with full-grade root throughout: Ved. naús, nā́vam, gen. nāvás, loc. nāví, pl. nā́vas, naubhís; Gk ναῦς νῆα νηός; Lat. nāvis (Beekes p. 192 *neh₂-u-bʰi). Gives néh₂us, néh₂wm̥, neh₂wés, néh₂wi, néh₂wes, néh₂wn̥s, neh₂ubʰós; replaces the zero-grade nh₂éw- (engine sweep i-u-stems #6)"}
{"id": "pie-lex-HeHkjus", "spec": {"m_strong": "HeHḱú", "m_weak": "HeHḱéw", "f_strong": "HeHḱéwih₂", "f_weak": "HeHḱuyéh₂", "accent_class": "proterokinetic"}, "spec_checked": true, "note": "oxytone 'swift' (Ved. āśú-, Gk ὠκύς, Lat. ōcior): nom. HeHḱús, not root-accented HéHḱus (t021 review); oblique and feminine keep the full-grade root as in Ved. āśáv-, Gk ὠκέος (L&Y Handbook ch. 122 §3.2 *h₁ōḱ-éw-) (engine sweep i-u-stems #8)"}
{"id": "pie-lex-pekju", "gender": "n", "meaning": ["livestock, cattle (collective)"], "spec": {"strong": "péḱu", "weak": "pḱéw", "accent_class": "proterokinetic", "gender": "n"}, "spec_checked": true, "note": "Ved. páśu n., Lat. pecu, Goth. faihu: neuter u-stem, proterokinetic as in Wiktionary (zero-grade root also in OAv. fšuiiant-, Fortson *pk̑u-i̯ent-); the earlier weak péḱew gave péḱewh₁, péḱewbʰos (engine sweep i-u-stems #10)"}
{"id": "pie-lex-bheh2gjhus", "spec": {"strong": "bʰeh₂ǵʰú"}, "note": "oxytone like its lemma (Ved. bāhú-, bāhúm, bāhóḥ); the table's strong stem bʰéh₂ǵʰu gave acc. bʰéh₂ǵʰum beside nom. bʰeh₂ǵʰús (engine sweep i-u-stems #11)"}
{"id": "pie-lex-Hrughis", "spec": {"strong": "Hrugʰí", "accent_class": null}, "note": "lemma Hrugʰís (PBS *rugís, PGmc *rugiz); the table's strong Hréwgʰi gave acc. Hréwgʰim beside nom. Hrugʰís (engine sweep i-u-stems #11)"}
{"id": "pie-lex-perkus", "spec": {"strong": "pérkʷu"}, "note": "labiovelar throughout as in the weak stem pr̥kʷéw (Lat. quercus < *perkʷu-); written pérkus before u by delabialization; nom. pl. pérkʷewes, not pérkewes (engine sweep i-u-stems #13)"}
{"id": "pie-lex-kjmtogwus", "spec": {"m_weak": "ḱm̥tógʷow", "f_strong": "ḱm̥tógʷowih₂", "f_weak": "ḱm̥tógʷuyeh₂"}, "note": "bahuvrihi keeps the first member's accent (Ved. śatá-gu-); Wiktionary's args carry two accents (ḱm̥tógʷóws) (engine sweep i-u-stems #14)"}
```

#12 h₁léngʰus: if the §6 recommendation is adopted, the h₁léngʰus line in the next block covers it. Otherwise use `{"id": "pie-lex-h1lenghus", "spec": {"m_strong": "h₁léngʷʰu", "f_strong": "h₁ln̥gʷʰéwih₂", "f_weak": "h₁ln̥gʷʰuyéh₂"}}`.

Convention-dependent: these follow L&Y for u-adjectives (§6, #1, #9) and the majority *-éw-* for suHnús (#7). Each line is the Wiktionary extra spec or the L&Y stem:

```json
{"id": "pie-lex-gwreh2us", "spec": {"m_strong": "gʷr̥h₂ú"}, "note": "Ved. gurú-, Gk βαρύς: zero-grade root, suffix accent (L&Y Handbook ch. 122 §2.5 *gʷr̥h₂-éw-; Wiktionary's second table)"}
{"id": "pie-lex-h1werHus", "spec": {"m_strong": "h₁wr̥Hú"}, "note": "Ved. urú-, Gk εὐρύς (L&Y §2.5, §3.2; Wiktionary's second table)"}
{"id": "pie-lex-pleth2us", "spec": {"m_strong": "pl̥th₂ú"}, "note": "Ved. pr̥thú-, Gk πλατύς (L&Y §3.2 *pl̥th₂-ú-; M&A *pl̥th₂us; Wiktionary's second table)"}
{"id": "pie-lex-sweh2dus", "spec": {"m_strong": "sweh₂dú", "m_weak": "sweh₂déw", "f_strong": "sweh₂déwih₂", "f_weak": "sweh₂duyéh₂"}, "note": "Ved. svādú-, svādáv-, Gk ἡδύς, ἡδέ(w)-: full-grade root, suffix accent (L&Y §3.2 *sweh₂d-ú-, *sweh₂d-éw-; M&A *swehadús)"}
{"id": "pie-lex-h1lenghus", "spec": {"m_strong": "h₁ln̥gʷʰú", "m_weak": "h₁ln̥gʷʰéw", "f_strong": "h₁ln̥gʷʰéwih₂", "f_weak": "h₁ln̥gʷʰuyéh₂"}, "note": "Ved. raghú-/laghú-, Gk ἐλαχύς, Lat. levis: labiovelar in every stem (Wiktionary's args mix gʰ/gʷʰ), suffix accent (Wiktionary's second table)"}
{"id": "pie-lex-mregjhus", "spec": {"m_strong": "mr̥ǵʰú"}, "note": "Gk βραχύς, Av. mərəzu- (Wiktionary's second table)"}
{"id": "pie-lex-dlewkus", "spec": {"m_strong": "dlukú"}, "note": "Gk γλυκύς (Wiktionary's second table)"}
{"id": "pie-lex-bhengjhus", "spec": {"m_strong": "bʰn̥ǵʰú"}, "note": "Ved. bahú-, Gk παχύς"}
{"id": "pie-lex-tenh2us", "spec": {"m_strong": "tn̥h₂ú"}, "note": "Ved. tanú- (Wiktionary's second table); Ringe 2006 p. 49 models root-accented ténh₂us, so optional"}
{"id": "pie-lex-suHnus", "spec": {"weak": "suHnéw"}, "note": "gen. *-ew-s (L&Y Handbook ch. 122 §2.1.1: Ved. sūnós, Goth. sunaus, OCS synu; Fortson §6.42; Ringe ǵustéws), dat. *-ew-ey (Ved. sūnáve; Beekes §13.2.6a), loc. *-ēw; Wiktionary/Beekes gen. *-ow-s kept only by this choice"}
```

## 10. Lexicon routing

**#16 pie-lex-treyes** is marked usable as an open adjective. Its singular cells are meaningless for '3', and several are unaccented (*trēy, treys, tisri*). The corpus uses `closed:numerals/3`, which matches Ringe p. 52 (*tréyes, tríns, tribʰí, trimós, tr̥yóHom, trisú; tríh₂*). Proposed: add the id to data/generation/blocklist.jsonl (reason "numeral 3 is closed-class: closed:numerals/3"), so a planner cannot pick the open lexeme.

## 11. Minor, no fix proposed

- NOM.PL alternatives *suHnúes, HeHḱúes, ml̥dúes, tríes* (accented *ú/í* before a vowel) come from the Wiktionary convention merged as alternatives. They are never primary, and the validator index tolerates them.
- `_initial_accent` returns an accentless form for *HHC-* onsets (VOC.SG f. *HHḱewi*). The #8 override removes the only case in this family.
- After right-to-left syllabification, *déh₂n̥wih₁* (NOM.DU) and similar *-h₂n̥w-* forms are regular. They remain after #4, in the dual and GEN.PL (*déh₂n̥wōm*).

## Appendix A. Exact diff (patches A+B+C)

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ -247,14 +247,26 @@
         out["DAT.SG"] = _uniq([render(_add(full, "ey"))] + out["DAT.SG"])
 
     out["INS.SG"] = [w("éh₁", "h₁", obl)]
+    if hb and obl_pl is not weak:
+        # i/u-stem instrumental *-i-h₁/*-u-h₁ on the accented zero-grade suffix: Fortson §6.10 (Ved. matī́),
+        # Ringe 2006 pp. 47, 49 (mn̥tíh₁, ǵustúh₁, mríh₁, drúh₁, tn̥h₂úh₁), Beekes §13.2.6a (*-u-h₁).
+        # The full-grade form (mn̥téyh₁) follows as an alternative.
+        out["INS.SG"] = _uniq([render(_add(obl_pl, "h₁"))] + out["INS.SG"])
     out["LOC.SG"] = _locative(spec, strong, weak, hb)
     if hb:   # prefer the -i (or i-stem -ēy) locative to the endingless one (which looks like the nominative)
-        out["LOC.SG"] = sorted(out["LOC.SG"], key=lambda f: not f.endswith(("i", "í", "y")))
+        out["LOC.SG"] = sorted(out["LOC.SG"], key=lambda f: not f.endswith(("i", "í", "y", "ḗw", "ṓw")))
     # --- dual
     if neuter:
         # s-stem neuters take the e-grade (weak) suffix: déḱos → déḱesih₁; others the strong stem
         e_grade_s = len(weak) > 1 and weak[-1].base == "s" and weak[-2].base == "e"
         du = [render(_add(weak if (e_grade_s and spec.weak) else strong, "ih₁"))]
+        if hb and strong[-1].syl and strong[-1].base in ("y", "w"):
+            if strong[-1].base == "y":
+                # i-stem: -i-ih₁ → -ih₁ (Fortson §6.13 *h₃ekʷih₁ 'both eyes'; Ringe p. 47 mórīh₁ (?))
+                du = [render(_add(strong[:-1], "ih₁" if not strong[-1].acc else "íh₁"))]
+            elif strong[-1].acc:
+                # accented -ú + ih₁ → -wíh₁ (Ved. urvī́, Fortson §6.13), not -úyh₁
+                du = [render(_add(strong[:-1] + [Seg("w", "R")], "íh₁"))]
     else:
         du = [render(_add(strong, "h₁")), render(_add(strong, "h₁e"))]
     out["NOM.DU"] = out["VOC.DU"] = out["ACC.DU"] = du
@@ -370,8 +382,15 @@
             continue
         if len(s) >= 2 and s[-1].base == "y" and not s[-1].syl and s[-2].base == "e" and s[-2].acc:
             out.append(render(lengthen_last_vowel(s)))  # -éy → -ḗy (bʰr̥tḗy)
+            if hb and strong[-1].syl and strong[-1].base == "y":   # *-ey-i > *-ēy (Ringe 2006 p. 20, Stang's law; Beekes §13.2.6a; Ved. agnā́): -ḗy first
+                out[-2:] = out[-2:][::-1]
         else:
             out.append(render(_add(s, "i")))
+            if hb and strong[-1].syl and strong[-1].base == "w" and len(s) >= 2 and s[-1].base == "w" \
+                    and not s[-1].syl and s[-2].base in ("e", "o") and s[-2].acc:
+                # u-stem endingless locative in the lengthened grade *-ēw (Beekes §13.2.6a; Ved. sūnáu,
+                # Goth. sunau), parallel to i-stem *-ēy; Ringe's -éw(i) follow as alternatives
+                out.insert(len(out) - 2, render(lengthen_last_vowel(s)))
     return _uniq(out)
```
