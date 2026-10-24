# Engine sweep: r-stems and n-stems

Auditor family: kinship r-stems, agent nouns in *-tḗr*/*-tōr*, *h₂nḗr*, animate n-stems (*-ō(n)*, *-ēn*, *-mō(n)*, *-mēn*), neuter men-stems (*-mn̥*), and Szemerényi's law in the nominatives. Engine state as of 2026-10-23 (pie/morph.py, pie/phon.py, pie/classify.py, data/morph/inflection_specs.jsonl, data/lexicon/overrides.jsonl). Corpus: corpus/tier3/*.jsonl.

**Result: 9 defects** (8 in the engine or specs, 1 of stale corpus tokens), plus 6 handbook disagreements recorded with a convention recommendation. The high-traffic cells are clean: NOM/ACC/VOC/GEN/DAT.SG and NOM/ACC.PL of every kinship term, *h₂nḗr*, *ḱwṓ*, *déh₃tōr* and *h₁nómn̥* match the handbook convention. All the defects are in low-frequency cells or in lexemes the corpus barely uses yet, so they touch **19 tokens now** (of 3,441 family tokens): 11 change under the two code patches (defects 1 and 2), 5 under the overrides (defects 3–5), and 3 are stale. The men-neuter fix still matters most for future batches: it changes 4 cells in each of 113 usable lexemes. The biggest practical gain is defect 8: it makes 22 hysterokinetic *-tḗr* agent nouns usable.

## Ranked fixes

| # | Defect | Fix type | Tokens now | Scope |
|---|---|---|---|---|
| 1 | *h₂éḱmō* obliques have an unsyllabified *m* (*h₂ḱmnés*, *h₂ḱmnéh₁*) | phon.py `join` step 2b | 9 (+1 stale) | 1 lexeme, 5 cells |
| 2 | men-neuter oblique plural keeps the accented full-grade suffix (*ḱluménbʰos*, *dʰh₁ménsu*) | morph.py | 2 | 113 lexemes × 4 cells |
| 3 | *kéh₂nmn̥* weak stem *kh₂nmén* has a stray *n* | override | 2 | 1 lexeme (+2 with 0 tokens) |
| 4 | *dayh₂wḗr* oblique plural *dayh₂urbʰós* (Wiktionary weak stem *dayh₂ur*) | override | 2 | 1 lexeme, 4 cells |
| 5 | acrostatic *méh₂tēr*, *bʰréh₂tēr* LOC.SG *méh₂tri* (zero-grade suffix) | override | 1 | 2 lexemes |
| 6 | *ǵʰésōr* weak stem *ǵʰsr̥*, where the handbook has *ǵʰes-r-* | override | 0 (4 strong-case tokens) | 1 lexeme |
| 7 | `shape:tor-agent` gives no `loc_sg`, so LOC.SG is the strong stem *dʰéh₁tori* | classify.py | 0 | 20 lexemes |
| 8 | `shape:er-stem` is unusable (backtest 0.796 < 0.85): it catches the neuter d-stem *ḱḗr*, and it mangles a doubly accented lemma | classify.py | 0 | +22 hysterokinetic *-tḗr* agent nouns become usable |
| 9 | stale corpus tokens from before earlier fixes: *susréh₁*, *h₂ḱnéh₁*, *dʰugtréy* | regenerate | 3 | — |

Every patch below was applied to a scratch copy of `pie/` and diffed against the current engine over all 3,814 usable lexemes in both conventions:
- **Fixes 1 and 2:** 114 lexemes change, all in the expected cells. Only 1 lexeme changes under the Wiktionary convention (*h₂éḱmō*, because its spec is a hand override). The Wiktionary cross-check is unaffected, because it builds specs from the table templates.
- **Fixes 7 and 8:** `shape:er-stem` backtest goes from 0.796 to 0.902 and `shape:tor-agent` from 0.947 to 1.000.
- **Wiktionary cross-check:** `pie.crosscheck.run` gives identical results before and after (14,015 cells ok / 182 bad, 574 / 41 tables).
- **Tests:** tests/test_morph.py, test_morph_r2_fixes.py and test_classify.py pass (91) on the patched copy. One existing test must change: tests/test_realize.py:426 (`test_t017_review_stems`) pins `h₂ḱmnés`, which becomes `h₂ḱm̥nés` (fix 1). The other test_realize failure on the scratch copy (`test_blocked_and_deponent_lexemes_are_rejected`) comes from the scratch copy having no blocklist, not from the patches. The new tests proposed below also pass there (scratch `rn_pie/tests/test_rn_proposed.py`).

---

## Inventory (199 usable lexemes)

From `lx.specs` (usable nouns whose stem ends in *r*/*n* or syllabic *m̥*). Tokens = corpus/tier3 tokens with that lex_id.

| Sub-type | Usable lexemes | Tokens | Examples |
|---|---|---|---|
| kinship r-stems, hysterokinetic | ph₂tḗr, dʰugh₂tḗr, h₂stḗr (star), dayh₂wḗr | 609 | ph₂tḗr 302, dʰugh₂tḗr 209 |
| kinship r-stems, acrostatic (Wiktionary) | méh₂tēr, bʰréh₂tēr | 456 | |
| amphikinetic *-ōr* | swésōr, ǵʰésōr, dʰwṓr, bʰṓr, ǵʰḗr | 170 | swésōr 86 |
| *h₂nḗr*; *spḗr*; *ǵʰwḗr* (hand-checked override) | 3 | 213 | h₂nḗr 176 |
| agent *-tōr* (table) | déh₃tōr, ǵénh₁tōr, pékʷtōr, wéydtōr | 118 | déh₃tōr 83 |
| agent *-tōr* (`shape:tor-agent`) | 20 (dʰéh₁tōr, stéwtōr, ḱléwtōr, …) | 31 | |
| agent *-tḗr* hysterokinetic (`shape:er-stem`) | **0 usable** (24 entries, unusable) | 0 | bʰertḗr, dh₃tḗr, ǵenh₁tḗr |
| n-stems, hysterokinetic | ḱwṓ, uksḗn, poh₂imḗn, bʰudʰmḗn, sh₂imṓ, wérsēn, pḱtḗn, pstḗn, wr̥h₁ḗn, gerh₂ḗn | 360 | ḱwṓ 220, poh₂imḗn 87 |
| n-stems, amphikinetic *-ō(n)*, *-mō(n)* | h₂éḱmō, tétḱō, h₃érō, ḱérh₂sō, kólHō, wéyh₁ō, gʷréh₂wō, h₂éymō, léymō, pléwmō | 201 | h₂éḱmō 55 |
| men-neuters, proterokinetic (table) | 16 (dʰéh₁mn̥, séh₁mn̥, ḱléwmn̥, ǵʰéymn̥, …) | ~230 | dʰéh₁mn̥ 70 |
| men-neuters, proterokinetic (`shape:men-neuter`) | 100 | ~190 | kéh₂nmn̥ 41, h₂éǵmn̥ 33, sréwmn̥ 31 |
| men-neuter, acrostatic | h₁nómn̥ | 169 | |
| *r/n* heteroclites (wódr̥, péh₂wr̥, dóh₃r̥, …) | 24 | ~760 | **out of scope**: listed only, left to the heteroclite auditor |

Not in the lexicon: no *Hréǵō* lexeme exists. *ǵʰmṓ*, *h₁éh₁tmō*, *h₂ewgmṓ* and ~45 other `shape:n-stem-ak`/`-hk` entries are unusable (backtest 0.83 / 0.71), so they are absent from the corpus.

**Coverage of the spot-check.** I dumped every cell of the ~60 table lexemes by hand, read them, and compared them with the books. The 100 `shape:men-neuter` and 20 `shape:tor-agent` lexemes I checked by script:
- every weak stem was read;
- a phonotactic scan flagged any consonantal resonant between two non-vocalic segments in any primary form (scratch `rn_phonotactic.py`);
- for all 62 animates, the engine's own NOM.SG (before realize.py substitutes the lemma) was compared with the lemma: **62/62 equal**.

---

## Kinship r-stems

**Right.** *ph₂tḗr* matches Ringe 2006 §2.3.4 (p. 47–48 table: *ph₂tḗr, ph₂térm̥, gen. ph₂tr̥és, dat. ph₂tr̥éy, loc. ph₂tér(i), pl. ph₂téres, ph₂térn̥s, ph₂tr̥bʰí, ph₂tr̥mós, ph₂tr̥sú*) and Fortson §6.23 (*ph₂-tér-m̥, ph₂-tr-és*). The only difference is syllabification: Fortson writes *-tr-é-*, Ringe *-tr̥-é-*; the engine follows Fortson. *h₂stḗr* matches Ringe's 'star' column cell for cell. *dʰugh₂tḗr* matches Fortson §18.15 (*dʰugh₂-tér-m̥, -tr-és, -tér-es*). Ringe's oblique *dʰugtr-'* (laryngeal loss) is the Wiktionary table's form and stays an alternative. ACC.PL *-n̥s* (Fortson §6.14, Ringe), GEN.PL *-ōm* (Fortson §6.16), DAT/ABL.PL *-bʰos*, LOC.PL *-su* (§6.17) are all correct.

**Disagreement: mother and brother.** Wiktionary makes *méh₂tēr* and *bʰréh₂tēr* acrostatic: weak *méh₂tr̥-*, gen. *méh₂tr̥s*. The sources split:
- **With Wiktionary:** Beekes 13.2.4 (static *méh₂-tr, gen. méh₂-tr-s*) and M&A §12.3 'Kinship' (*méh₂tēr*, *bʰréh₂ter-*, root accent). For brother, also Fortson §6.8 (OE *brōþor* < *bʰrātr̥-s*) and L&Y ch. 122 §2.1.1 (*-r̥s* in r-stems).
- **Against:** Fortson §6.37 prefers *meh₂tér-* (suffix-accented, like 'father').

**Keep the Wiktionary convention.** It is the lemma in all 456 tokens, and three handbooks support it.

**Defect 5: acrostatic LOC.SG.** `_locative` uses the weak stem for every acrostatic noun, so it outputs *méh₂tri, bʰréh₂tri*. The locative takes the full grade of the suffix: Fortson §6.11; Beekes 13.2.5b r-stem loc. *-ér-i*; Ved. *mātári, bhrā́tari*. Fix with a spec override, so root nouns like *nókʷts* (loc. *nékʷt(i)*) are not touched:

```json
{"id": "pie-lex-meh2texr", "spec": {"loc_sg": ["méh₂ter"]}, "spec_checked": true, "note": "loc. full-grade suffix méh₂ter(i), not méh₂tri (Fortson §6.11; Beekes 13.2.5b r-stem loc. -ér-i; Ved. mātári): engine-sweep r-n-stems"}
{"id": "pie-lex-bhreh2texr", "spec": {"loc_sg": ["bʰréh₂ter"]}, "spec_checked": true, "note": "loc. full-grade suffix bʰréh₂ter(i), not bʰréh₂tri (Fortson §6.11; Beekes 13.2.5b; Ved. bhrā́tari): engine-sweep r-n-stems"}
```
Verified result: LOC.SG *méh₂teri, méh₂ter*. All other cells unchanged.

**Defect 4: *dayh₂wḗr*.** Wiktionary's weak stem *dayh₂ur* gives the right GEN *dayh₂urés*, but before consonant endings it gives *dayh₂urbʰós, dayh₂ursú*. The zero grade of *-wer-* before a consonant is *-wr̥-*, as *-tr̥-* is in *ph₂tr̥bʰí/ph₂tr̥sú* (Ringe p. 48); compare Ved. weak stem *devṛ-* (*devṛ́bhis*). The weak stem *dayh₂wr̥* gives *dayh₂urés* by junction syllabification anyway, so only the oblique plural changes:

```json
{"id": "pie-lex-dayh2wexr", "spec": {"weak": "dayh₂wr̥"}, "spec_checked": true, "note": "weak dayh₂wr̥- like ph₂tr̥- (Ringe 2006 §2.3.4 ph₂tr̥bʰí; Ved. devṛ́-): gen. still dayh₂urés, but dat. pl. dayh₂wr̥bʰós, not Wiktionary's dayh₂urbʰós: engine-sweep r-n-stems"}
```
Verified result: *dayh₂wr̥bʰós, dayh₂wr̥sú, dayh₂wr̥bʰís*, GEN *dayh₂urés*.

**Convention, not a defect: VOC *ph₂ter*.** The vocative is unaccented, 84 tokens. `_initial_accent` leaves it unaccented because the retracted accent falls on the syllabic laryngeal (Fortson §6.7; Ved. *pítar*, Gk *πάτερ*). Ringe writes unretracted *ph₂tér*, which is the alternative. This is deliberate and documented in code; no change.

## *-ōr* amphikinetic, *h₂nḗr*, root nouns in *-ēr/-ōr*

**Right.**
- *swésōr*, acc. *swésorm̥*, gen. *swesrés* (the existing override, after Fortson). *déh₃tōr* has the same shape.
- *h₂nḗr, h₂nérm̥, h₂n̥rés, h₂néres, h₂nérn̥s, h₂nr̥bʰós* (Ved. *nṛ́bhyas*).
- *dʰwṓr*, gen. *dʰurés* (Ved. *dúras*). *bʰṓr*, *ǵʰḗr* and *spḗr* are fine.
- *ǵʰwḗr* is a deliberate hand-checked override (M&A ch. 9; Gk *θηρός*, accented endings). Its `accent_class: acrostatic` label does not match its mobile accent, but the forms are as intended.

**Defect 6: *ǵʰésōr* 'hand'.** Wiktionary's weak stem *ǵʰsr̥* gives gen. *ǵʰsrés*. Fortson §6.37 gives stem *ǵʰes-r-* (Hitt. *kiš(š)r-*, Gk *χειρ-*, Arm. *jeṙn* < *ǵʰesr-n-*), and again in ch. 9 (Gk *kheír* < *ǵʰes-r-*). This parallels the *swesr-* override. There is no counter-evidence in the books. Only strong-case tokens so far (4).

```json
{"id": "pie-lex-gjhesoxr", "spec": {"weak": "ǵʰesr", "loc_sg": ["ǵʰesér"]}, "spec_checked": true, "note": "weak *ǵʰes-r- with full-grade root (Fortson §6.37: Hitt. kiššr-, Gk χειρ-, Arm. jeṙn < *ǵʰesr-n-), like swesr-: gen. ǵʰesrés, not ǵʰsrés: engine-sweep r-n-stems"}
```
Verified result: *ǵʰesrés, ǵʰesréy, ǵʰeséri, ǵʰesr̥bʰós*.

## Agent nouns

**-tōr (amphikinetic), table type: right.** This is Fortson §6.37 (*déh₃-tōr*, root accent and full grade) and Beekes 13.2.4 subtype 3 (*dṓtōr*, gen. *C(e)C-R-ós*). The cells are:
- singular: *déh₃tōr, déh₃torm̥*, gen. *dh₃trés*, loc. *dh₃tér(i)*;
- plural: **acc. pl. *déh₃torn̥s***, **gen. pl. *dh₃trṓm***, *dh₃tr̥bʰós*.

These parallel Ringe's amphikinetic n-stem *léymō*: acc. pl. *léymonn̥s*, gen. pl. *limnóHom*.

**Defect 7: `shape:tor-agent` locative.** The rule (pie/classify.py ~l. 208) sets no `loc_sg`, so the 20 shape-derived *-tōr* nouns get LOC.SG = strong stem: *dʰéh₁tori, gʷémtori, ḱléwtori*. Every table *-tōr* noun has Wiktionary's `loc_sg` with zero-grade root and accented e-grade suffix (*dh₃tér, pkʷtér, widtér*), the amphikinetic locative of Fortson §6.24 (cf. *h₂ḱmén*, Ringe *limén(i)*). This is the only cell where the rule fails its backtest: 4/76 cells, all LOC.SG. 0 tokens now.

**Defect 8: `shape:er-stem` (*-tḗr* agents) is unusable.** Backtest 0.796 < 0.85. The failures are:
- **13 cells:** the neuter root noun *ḱḗr* 'heart' (a d-stem, *ḱérd-/ḱr̥d-*) is routed into the *-ḗr* rule.
- **9 cells:** *dʰugh₂tḗr*, where the Wiktionary table has Hackstein's *dʰugtr-*.
- **4 cells:** *dayh₂wḗr*, where the shape rule's *dayh₂wr̥-* is actually better than the table, see defect 4.

Excluding neuters raises it to 0.902, which makes 22 hysterokinetic agent nouns usable: *bʰertḗr, dh₃tḗr, ǵenh₁tḗr, ǵneh₃tḗr, h₂erh₃tḗr, ḱlutḗr, priHtḗr, sth₂tḗr, teptḗr …*. Their handbook cells read right:
- *dh₃tḗr, dh₃térm̥*, gen. *dh₃trés*, loc. *dh₃téri*;
- plural *dh₃téres*, **acc. pl. *dh₃térn̥s***, **gen. pl. *dh₃trṓm***, *dh₃tr̥bʰós*.

Fortson §6.37 gives *-tḗr* agents a zero-grade root, but the lemmas' own grade is kept (*bʰertḗr*, as in Ved. *dātár-*). The rule's `zero_grade()` call also turns the doubly accented lemma *spéḱtḗr* into weak *spḱter-*, so it is replaced by plain suffix reduction (*-tér → -tr̥*). That gives the same result for every other lemma.

Before the integrator re-runs the classifier, block *pie-lex-h2eh2ikjexr* (*h₂eh₂iḱḗr*, glossed 'to possess, own', pos null) in data/generation/blocklist.jsonl. A planner would otherwise use it as a verb. Several of the 22 have no gloss (*dʰeh₁tḗr, h₂eydʰḗr, tewktḗr*) and only become plannable through derived glosses.

```diff
--- a/pie/classify.py
+++ b/pie/classify.py
@@ -200,17 +200,22 @@
         return Classified(NounSpec(st, weak, "proterokinetic", "f", devi=True), "shape:devi", "noun")
     if f.endswith(("eh₂", "éh₂")):
         return Classified(NounSpec(f, gender="f"), "shape:eh2", "noun")
-    if f.endswith(("tḗr", "ḗr")):
+    if f.endswith(("tḗr", "ḗr")) and g != "n":   # not the neuter root noun ḱḗr (a d-stem, ḱérd-/ḱr̥d-)
         st = f.replace("ḗr", "ér")
-        wk = zero_grade(st)
+        # zero-grade suffix only (Fortson §6.23, §6.37: *ph₂tér-/*ph₂tr-, *dh₃tḗr): zero_grade() reduced the root
+        # of a doubly accented lemma instead (spéḱtḗr → spḱter-); such lemmas get no spec
+        one_accent = sum(x.acc for x in _segs(st)) == 1      # (not a count of U+0301: ḱ/ǵ carry one too)
+        wk = _deaccent(st[:-2]) + "r̥" if one_accent else None
         return Classified(NounSpec(st, wk, "hysterokinetic", g if g in ("m", "f") else "m") if wk else None,
                           "shape:er-stem", "noun")
     if f.endswith("tōr"):                       # amphikinetic agent noun: ǵʰéwtōr, ǵʰéwtorm̥
         root = _strip(f, "tōr")
         wk = zero_grade(root)
         if wk:
+            # locative in the accented e-grade suffix with zero-grade root, as in the tables (dh₃tér, pkʷtér;
+            # Fortson §6.24 amphikinetic): not the strong stem (dʰéh₁tori)
             return Classified(NounSpec(root + "tor", wk + "tr̥", "amphikinetic", g if g in ("m", "f") else "m",
-                                       nom_sg=f), "shape:tor-agent", "noun")
+                                       nom_sg=f, loc_sg=[wk + "tér"]), "shape:tor-agent", "noun")
     if f.endswith(("ís", "ús")):
         st = _strip(f, "s")
         weak = _deaccent(st[:-1]) + ("éy" if f.endswith("ís") else "éw")
```
Then rerun scripts/classify_lexicon.py. Measured on a scratch copy: er-stem (120/133) 0.902, tor-agent (76/76) 1.000. Tests to add to tests/test_classify.py:

```python
def test_er_stem_rule_skips_neuters_and_reduces_only_the_suffix():
    from pie.classify import by_shape
    assert by_shape({"form": "ḱḗr", "pos": "noun", "gender": "n"}).spec is None
    c = by_shape({"form": "ǵenh₁tḗr", "pos": "noun", "gender": "m"})
    assert (c.rule, c.spec.weak) == ("shape:er-stem", "ǵenh₁tr̥")
    assert by_shape({"form": "ǵʰḗr", "pos": "noun", "gender": "m"}).spec.weak == "ǵʰr̥"   # ǵ's acute is not an accent
    assert by_shape({"form": "spéḱtḗr", "pos": "noun"}).spec is None

def test_tor_agent_locative():
    from pie.classify import by_shape
    from pie.morph import decline
    c = by_shape({"form": "dʰéh₁tōr", "pos": "noun", "gender": "m"})
    assert decline(c.spec, "handbook")["LOC.SG"][0] == "dʰh₁téri"
```

## Animate n-stems

**Right.**
- *ḱwṓ*: Ringe 'dog' column cell for cell (*ḱwónm̥, ḱunés, ḱunéy, ḱwónes, ḱwónn̥s, ḱwn̥bʰí, ḱunóHom, ḱwn̥sú*).
- *uksḗn*: Fortson §6.23 *h₂ukʷs-ḗn, -én-m̥, -n-és*, and Ringe 'bull'.
- *léymō, h₂éymō*: Ringe 'lake' cell for cell (*léymonm̥, limnés, limén(i), léymonn̥s, limn̥bʰí*).
- *pléwmō, sh₂imṓ*: the *-mn-* restoration of `_restore_mn`. *tétḱō* is fine (override). *h₃érō, kólHō, gʷréh₂wō* (Fortson §6.34), *ḱérh₂sō, wéyh₁ō* are fine.
- *poh₂imḗn* gen. *poh₂imnés*; *bʰudʰmḗn* gen. *bʰudʰm̥nés*.
- Amphikinetic acc. sg. *-on-m̥* follows Fortson §6.24 and Ringe *léymonm̥*. Beekes 13.2.5a writes acc. *-én-m*: a disagreement, and the engine correctly follows Fortson/Ringe.

**Defect 1: *h₂éḱmō* obliques.** The override weak *h₂ḱmn* (t017 review, kept *m*) leaves *m* consonantal between *ḱ* and *n*: *h₂ḱmnés, h₂ḱmnéh₁, h₂ḱmnéy, h₂ḱmnṓm*. In the handbook notation a resonant between two consonants is syllabic. Ringe 2006 §2.3.4 writes the parallel collective obliques *h₁n̥h₃m̥nés, sh₁m̥nés*, and the engine itself writes *bʰudʰm̥nés*. The correct forms are *h₂ḱm̥nés, h₂ḱm̥néh₁*. 9 tokens (INS 6, ABL 2, +1 stale *h₂ḱnéh₁*).

A spec change cannot fix this. Weak *h₂ḱm̥n* would break the oblique plural: `join` step 5 sees *m̥* as vocalic and outputs *h₂ḱm̥nbʰós*. So the fix goes in `join`, as a narrow companion to step 2. Over all usable lexemes it changes only these 5 cells; *tetḱnés, swesrés, wr̥h₁nés, ḱunés, h₂ḱmn̥bʰós, gʷʰn̥h₂ér* are unchanged:

```diff
--- a/pie/phon.py
+++ b/pie/phon.py
@@ -136,6 +136,13 @@
             out[i] = replace(out[i], syl=True)
             i -= 1
 
+    # 2b. stem-final consonantal resonant before a vocalic ending: a consonantal resonant before it, between
+    #     non-vocalic segments, becomes syllabic (h₂ḱmn+és → h₂ḱm̥nés, as Ringe 2006 §2.3.4 h₁n̥h₃m̥nés)
+    if n >= 3 and n < len(out) and out[n - 1].kind == "R" and not out[n - 1].syl and out[n].vocalic \
+            and out[n - 2].kind == "R" and not out[n - 2].syl and not _fixed(out[n - 2]) \
+            and not out[n - 3].vocalic:
+        out[n - 2] = replace(out[n - 2], syl=True)
+
     # 3. ending resonants, left to right within the initial resonant run
     i = n
     while i < len(out) and out[i].kind == "R" and not _fixed(out[i]):
```

Test for tests/test_morph_r2_fixes.py, in `test_handbook_primary`:

```python
    (NounSpec("h₂éḱmon", "h₂ḱmn", "amphikinetic", loc_sg=["h₂ḱmén"]), "GEN.SG", "h₂ḱm̥nés"),
    (NounSpec("h₂éḱmon", "h₂ḱmn", "amphikinetic", loc_sg=["h₂ḱmén"]), "INS.PL", "h₂ḱmn̥bʰís"),
    (NounSpec("tétḱon", "tetḱn", "amphikinetic", loc_sg=["tetḱén"]), "GEN.SG", "tetḱnés"),
```

**Contradiction to resolve.** tests/test_morph_r2_fixes.py:29 still asserts the Asno-law reading *h₂ḱnés* (Byrd: the *m* is lost after a heavy syllable) for the Wiktionary weak stem *h₂ḱn̥*. The override then chose *h₂ḱmn-*, citing Ved. *aśnás* as a later loss. The test passes because it builds its own spec, but the two decisions contradict each other. Pick one and update the comment in `_athematic` (`_restore_mn`). This audit follows the override.

**Disagreement: *ḱwṓ* LOC.SG.** Ringe's table has *ḱwón(i)* (o-grade). Wiktionary and Beekes 13.2.5a (n-stem loc. *-én(-i)*, Gk *αἰέν*) have *ḱwén(i)*. Keep *ḱwéni*. Ringe's *ḱúon(?)* vocative is marked uncertain by Ringe himself; keep *ḱwón*.

## Neuter men-stems

**Right (singular).** Proterokinetic *séh₁mn̥, gen. sh₁méns, dat. sh₁méney, loc. sh₁mén(i), ins. sh₁ménh₁, du. séh₁m̥nih₁*. This is Ringe's 'seed' column (*sh₁m̥éns, sh₁m̥éney, sh₁m̥én(i), sh₁m̥énh₁, séh₁mn̥ih₁*; Ringe writes *m̥* before the accented vowel, a notation difference) and Fortson §6.34 (gen. *-men-s*). *h₁nómn̥* (acrostatic, Wiktionary) gives gen. *h₁némn̥s*, the type of Ringe's acrostatic *h₁nḗh₃mn̥*, gen. *h₁néh₃mn̥(o)s*. The name's reconstruction is disputed: Fortson §6.36 gives both *h₁neh₃mn̥* and *h₁nomn̥*. Keep the lemma.

**Defect 2: oblique plural.** Wiktionary's men-neuter tables are singular+dual only (`n: sd` plus a collective), so the engine invents the plural. Before consonant-initial endings it keeps the accented full-grade weak stem: *ḱluménbʰos, dʰh₁ménbʰis, h₁iménsu, wr̥sménsu*. L&Y ch. 122 §2.4.1 states that the men-suffix is zero-grade before consonant-initial endings (Ved. instr. pl. *dhā́mabhis* < *dʰéh₁-mn̥-bʰis*) and full-grade before vowels (dat. *dhā́mane* < *-men-ey*). Compare Beekes 13.2.5a (Gk *-asi* < *-n̥si*; Ved. *-abhis*) and the engine's own i/u-stem rule (Ringe *mn̥tíbʰi*). GEN.PL *-mén-ōm* has a vowel-initial ending and stays.

Proposed: the accented zero-grade suffix *-mń̥-* (*ḱlumń̥bʰos, ḱlumń̥su*). This follows the proterokinetic accent of the spec (Fortson §6.22) and the project's i/u precedent. The old forms stay as trailing alternatives through the existing `obl_pl is not weak` block.

**Disagreement on the accent.** L&Y say the class has fixed root accent in the attested languages (*dʰéh₁-mn̥-bʰis*). Fortson §6.34 and Ringe (*sh₁m̥éns*) are proterokinetic. The spec's accent class should decide, as above.

Scope: 113 lexemes × 4 cells (DAT/ABL/LOC/INS.PL). Nothing else changes, and heteroclites (*ph₂wén-*) are untouched because the *m* is required.

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ -190,6 +190,11 @@
     # Only true i/u-stems (strong stem in syllabic -i/-u), not diphthongal root nouns (gʷṓws: Ved. góbhis).
     iu_stem = bool(strong) and strong[-1].kind == "R" and strong[-1].syl and strong[-1].base in ("y", "w")
     obl_pl = _zero_grade_iu(weak) if (hb and iu_stem) else obl
+    if hb and neuter and spec.accent_class == "proterokinetic":
+        # men-neuters: zero-grade suffix before consonant-initial endings, accented as in the proterokinetic
+        # weak cases (Lundquist & Yates, Handbook ch. 122 §2.4.1: Ved. dhā́mabhis < *dʰéh₁-mn̥-bʰis; Gk -μασι
+        # < *-mn̥-si; cf. Ringe 2006 §2.3.4 mn̥tíbʰi): ḱlumén- → ḱlumń̥bʰos, ḱlumń̥su
+        obl_pl = _zero_grade_men(obl_pl)
 
     def w(acc_ending: str, plain_ending: str, stem: list[Seg] | None = None) -> str:
         st = weak if stem is None else stem
@@ -318,6 +323,14 @@
     return weak
 
 
+def _zero_grade_men(weak: list[Seg]) -> list[Seg]:
+    """Weak stem -mén- → accented syllabic -mń̥- (ḱlumén- → ḱlumń̥-); unchanged otherwise."""
+    if len(weak) >= 3 and weak[-1].base == "n" and weak[-1].kind == "R" and not weak[-1].syl \
+            and weak[-2].base == "e" and weak[-2].acc and weak[-3].base == "m" and not weak[-3].syl:
+        return weak[:-2] + [Seg("n", "R", syl=True, acc=True)]
+    return weak
+
+
 def _zero_grade_iu(weak: list[Seg]) -> list[Seg]:
```

Test:

```python
def test_men_neuter_oblique_plural_zero_grade():
    c = hb(NounSpec("ḱléwmn̥", "ḱlumén", "proterokinetic", "n"))
    assert c["INS.PL"][0] == "ḱlumń̥bʰis" and c["LOC.PL"][0] == "ḱlumń̥su" and c["DAT.PL"][0] == "ḱlumń̥bʰos"
    assert "ḱluménbʰis" in c["INS.PL"]                  # old form kept as an alternative
    assert c["GEN.PL"][0] == "ḱluménōm"                 # vowel-initial ending: full grade (L&Y)
    assert c["GEN.SG"][0] == "ḱluméns"
    # acrostatic h₁nómn̥ (weak already -mn̥-) and the heteroclite péh₂wr̥ are untouched
    assert hb(NounSpec("h₁nómn̥", "h₁némn̥", "acrostatic", "n"))["INS.PL"][0] == "h₁némn̥bʰis"
    assert hb(NounSpec("péh₂wr̥", "ph₂wén", "proterokinetic", "n"))["INS.PL"][0] == "ph₂wénbʰis"
```

Heteroclites in *-wén-* (*ph₂wénbʰis*) have the same pattern. I left them for the heteroclite auditor and did not judge them.

**Defect 3: stray *n* in `shape:men-neuter` weak stems.** The rule's `zero_grade()` can leave a resonant between consonants:
- *kéh₂nmn̥* gives weak *kh₂nmén* (2 tokens: INS *kh₂nménh₁*, LOC *kh₂nméni*);
- *téh₂ngsmn̥* gives *th₂ngsmén*;
- *kékwmn̥* gives *kkwmén*.

The last two have 0 tokens and no gloss.

```json
{"id": "pie-lex-keh2nmn", "spec": {"weak": "kh₂n̥mén"}, "spec_checked": true, "note": "zero-grade root kh₂n̥- (the n between h₂ and m is syllabic): gen. kh₂n̥méns, not kh₂nméns: engine-sweep r-n-stems"}
{"id": "pie-lex-teh2ngsmn", "spec": {"weak": "th₂n̥gsmén"}, "spec_checked": true, "note": "syllabic n̥ between h₂ and g: engine-sweep r-n-stems"}
```
The lemma *kéh₂nmn̥* itself (34 ACC.SG tokens) also has a stray *n* after the *eh₂* coda. Fortson §6.34 writes *kan-mn̥* (Lat. *carmen*). The lemma is Wiktionary's and the validator matches it, so the lemma was left alone; it is flagged here for the lexicon owner. A related case: *wéluHmn̥* has weak *wluHmén*, with an initial *w* before *l* (0 tokens).

**Disagreement: NOM/ACC.PL.** The engine gives *-mn̥h₂* (*ḱléwmn̥h₂*, *h₁nómn̥h₂*, 5 tokens), which is Fortson §6.15 (neuter *-h₂*; Gk *-ματα*, Lat. *-mina*). Ringe (collectives *séh₁mō, h₁néh₃mō*) and the Wiktionary tables (`coll`: *ḱléwmō, h₁némō*) give the collective in *-mō*. Keep *-mn̥h₂* primary. Optionally add the collective *-mō* (strong stem with the final *n̥* replaced by long *ō*) as an alternative for validator coverage. It is not needed for the corpus.

## Szemerényi's law and the nominatives

Correct throughout:
- *-ers → -ēr* (*ph₂tḗr*), *-ors → -ōr* (*swésōr, déh₃tōr*).
- *-ons → -ō*, with the *n* lost only after *ō* (Fortson §3.38, §3.40): *ḱwṓ, h₂éḱmō, sh₂imṓ*.
- *-ens → -ēn* keeps the *n*: *uksḗn, poh₂imḗn, bʰudʰmḗn, wérsēn*.
- No lengthening after a long vowel (*ǵʰwḗr* via nom_sg).

All 62 animate nominatives the engine builds equal their lemmas.

## Corpus: stale tokens (defect 9)

Three tokens predate the current specs and do not match any current cell form: *susréh₁* (swésōr INS.SG), *h₂ḱnéh₁* (h₂éḱmō INS.SG), *dʰugtréy* (dʰugh₂tḗr DAT.SG). Regenerating or revalidating those records fixes them. Every other family token equals the current primary form.

## Smaller notes (no change proposed)

- **NOM.DU *-h₁* before *-h₁e*.** Fortson §6.13 allows either; Ringe has *-h₁e* throughout. This order applies to all athematic animates, not only this family; 40 family tokens. It is a cross-family convention question.
- **Ringe's syllabification of oblique stems** (*ph₂tr̥és, uksn̥éh₁*) is not among the alternatives. This only affects validator coverage of Ringe-notation texts, not the corpus.
- ***méh₂tēr* gender.** Spec gender m, lexicon gender f; also *ǵʰésōr*, *dʰwṓr*. `Lexicon.gender` prefers the lexicon, so agreement is right.

## Scratch files

All in /private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/:
- inventory: rn_inv.py, rn_family.txt;
- corpus counts: rn_corpus.py, rn_counts.json, rn_feat.py;
- phonotactic scan: rn_phonotactic.py;
- backtests: rn_bt.py, rn_bt2.py, rn_bt3.py;
- patched engine copy: rn_pie/;
- full before/after cell dumps: rn_dump.py, rn_before.json, rn_after.json;
- diffs: rn_morph.diff, rn_phon.diff, rn_classify.diff.
