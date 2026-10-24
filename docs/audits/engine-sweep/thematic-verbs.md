# Engine sweep: thematic presents, s-aorists, thematic aorists, the perfect and the stative

Auditor family: thematic verbs (2026-10-23). Read-only audit; no code or data touched. Scratch scripts are under the
session scratchpad with the `thematic-verbs_` prefix. All patches below were applied to a scratch copy of the module and run
against every usable spec and every Tier 3 token before they were written up. The forms and counts quoted are measured,
not predicted.

Sources: Fortson 2010 ch. 5 (§§5.11–5.57), Ringe 2006 §2.3.3 (pp. 31–34), Beekes 2011 ch. 18 (pp. 259–271),
Lundquist & Yates, Handbook vol. 3 ch. 122 §§4.2–4.4 (= L&Y), LIV² (data/lexicon/liv2.jsonl, printed pages). M&A has no
verb paradigms beyond what the others give.

**Bottom line.** This family is largely clean. The thematic endings, 1pl *-mes*, middle 2pl *-dʰwe*, the thematic optative
*-oyh₁-/-oyh₁ent*, the perfect endings and ablaut, *-wṓs*, the thematic aorist, and the root and suffix grades of
*-éye-/-yé-/-sḱé-* all check against Fortson, Ringe, L&Y and Beekes. I found **10 defects** (3 shared with other families),
and they are small:

| # | Defect | Tier 3 tokens now | Fix |
|---|---|---|---|
| 1 | 2du primary *-th₁es* ranked first; the code comment credits Ringe, but Ringe has *-tés* | 9 (2 thematic) | morph.py, 1 line |
| 2 | *dedwóye* 'fear': pl. *deduyḗr*, *deduyé* (glide rule excludes C+w+i) | 8 | morph.py, 1 line |
| 3 | middle 3sg: the CCu/CCi rule puts archaic *-o* ahead of productive *-to* (*ḱl̥niyó*, *ḱluwó*; 64 lexemes) | 5 (cross-family) | morph.py, 3 lines |
| 4 | optative 3pl *-ih₁n̥t* after accented stems; Fortson: always *-ent* | 3 | morph.py |
| 5 | s-aorist / Narten: subjunctive and *-tōd* on the lengthened grade (*wḗǵʰseti*) | 0 in family; 3 Narten-present tokens (cross-family, to confirm) | morph.py |
| 6 | s-aorist / Narten: optative sg. *-yeh₁-* (unaccented) for *-ih₁-* throughout | 0 | morph.py |
| 7 | thematic PTCP.MID lacks *h₁* when the thematic vowel is accented (*widómnos*) | 0 (313 lexemes) | morph.py, 1 line |
| 8 | 62 s-aorists unusable (*dḗyḱst*, *prḗḱst*, *ḱlḗwst*, *wḗdʰst*, …); the sub-type has 1 usable lexeme and 0 tokens | 0 (coverage) | classify.py rule |
| 9 | 35 thematic deponents unusable (*mr̥yétor* 'die', *ǵn̥h₁yétor* 'be born', *mn̥yétor* 'think', …) | 0 (coverage) | classify.py rule or 5 overrides |
| 10 | a participle of a deponent may be planned active | 0 (preventive) | realize.py check |

Measured against `conjugate(..., "wiktionary")` over all usable verb specs, with `alternatives=False`, the patches
change no cell. With `alternatives=True`, 87 cells in 11 lexemes gain or reorder secondary forms (the handbook forms merged
in as alternatives) and no primary form changes. The patches are gated to `handbook` or sit in `_handbook_verbal`, so the
Wiktionary crosscheck is unaffected. Applied together to all usable specs, they change
the first form of **28 Tier 3 tokens** (list at the end).

---

## Inventory

`lx.specs`, family verb, usable, grouped by spec shape. Tokens = all Tier 3 tokens (27 files, 2,115 records).

| Sub-type | Lexemes | Used | Tokens | Rule source |
|---|---|---|---|---|
| simple thematic + tudáti (*bʰére-*, *gʷr̥h₃é-*, *píph₃e-*, *sísde-*) | 449 | 65 | 2,035 | 1,128 shape + 74 table (all thematic) |
| *-yé-/-ye-* (*gʷm̥yé-*, *spéḱye-*, *h₁regʷesyé-*, *-éh₁ye-* statives) | 389 | 31 | 1,056 | " |
| *-éye-* causative-iteratives (*moréye-*, *sodéye-*, *woséye-*) | 279 | 37 | 605 | " |
| *-sḱé-* (*gʷm̥sḱé-*, *h₂isḱé-*, *h₁r̥sḱé-*) | 69 | 4 | 189 | " |
| thematic in *-ne-* (*kh₂né-*) | 12 | 1 | 19 | shape |
| athematic statives/factitives (*h₁rudʰéh₁-*, *néweh₂-*) | 2 | 2 | 72 | table |
| deponents, usable (*ḱéytor*, *wéstor* athematic; *sékʷetor*, *pérdetor* thematic) | 4 | 4 | 202 | table |
| deponents, unusable (`unknown:middle-only`) | 37 | 0 | 0 | — |
| thematic aorists (*widé-*, *h₁ludʰé-*, *wéwkʷe-*, *likʷé-*) | 4 | 4 | 407 | 3 table + 1 shape |
| s-aorist, usable (*wḗǵʰs-/wéǵʰs-*) | 1 | 0 | 0 | table |
| s-aorist, unusable (`ḗ…st` lemmas) | 62 | 0 | 0 | — |
| perfects (*wóyd-*, *dedórḱ-*, *ǵeǵónh₁-*, *stestóh₂-*, …) | 24 | 20 | 626 | 20 table + 4 shape |

Not in this family: the 22 *-st* lemmas *térst, h₂wérst, nést, mérst, ǵéwst, h₂wékst …*. They are **root aorists of
s-final roots** (LIV² p. 440 prints *mérs-/mr̥s-* as Aorist; likewise *ters-*, *nes-*, *ǵews-*), and full grade sg. / zero
grade pl. is right for them. They belong to the root-aorist audit (272 tokens).

Features used (thematic presents, all sub-types; measured): PST.3SG 945, PRS.3SG 685, IMP.2SG 412, PST.3PL 207,
PRS.1SG 154, PRS.2SG 154, SBJV.3SG 140, MID.* 128, PRS.3PL 117, OPT.3SG 91, INJ.2SG 87. Perfects: PRF.3SG 271, PRF.1SG 95, PRF.2SG 71,
PRF.3PL 64, IMP 42, OPT 32, SBJV 17. Thematic aorists: AOR.3SG 273, AOR.3PL 36, SBJV 23, OPT 25.

---

## 1. Thematic presents

**Right.**
- Theme vowel *o* before 1st-person endings and the 3pl, *e* elsewhere, fixed accent, no ablaut (Fortson §5.28–5.29;
  Beekes p. 261).
- Primary endings *-oh₂ -esi -eti -omes -ete -onti* and secondary *-om -es -et -ome -ete -ont* (Fortson §5.28 table, Ringe
  p. 31). 1pl *-mes* is first, with *-mos* (Ringe) kept as the alternative: L&Y §4.2.5 give *-me-* with the final open,
  and Beekes p. 259 has *-mes*. This convention is right.
- Duals: secondary *-etom -etām* (Ringe p. 31 *-tóm -tā́m*; Beekes p. 271 *-teh₂m*). Imperative: bare stem, *-etu*, *-ontu*, 2pl
  *-ete*, *-etōd* (Fortson §5.54; L&Y §4.2.4.1). Thematic aorist imperatives match these too.
- Middle: *-oh₂er -eth₂er -etor -omesdʰh₂ -edʰwe -ontor*, secondary *-oh₂e -eth₂e -eto -omedʰh₂ -edʰwe -onto*. This follows
  L&Y §4.2.7 for *-h₂er*, *-th₂er*, *-tor* and *-(me)sdʰh₂*. Middle 2pl *-dʰwe* is right as the handbook primary: Fortson
  §5.16, L&Y §4.2.7 and Beekes p. 268 all have it, and Ringe's *-dʰh₂wé* (p. 31) is kept as the alternative.
- Subjunctive: long vowel *-ōh₂ -ēsi -ēti … -ōnti* (Fortson §5.55; L&Y §4.2.4.2).
- Optative: *-oyh₁-* in every person, 3pl *-oyh₁ent* (Fortson §5.57; L&Y §4.2.4.3).
- Participles: *-onts*, *-omh₁nos* (L&Y §4.4.1).
- Stem grades of every sub-type match the handbooks:
  - simple thematic: full grade, root accent (Fortson §5.30)
  - tudáti: zero grade, accented thematic vowel (§5.31)
  - *-yé-*: zero grade + accented suffix, or root accent (§5.32; L&Y §4.3.1)
  - *-sḱé-*: zero grade (§5.34)
  - *-éye-*: o-grade + *-éye-* (§5.35)
  - reduplicated *i*-presents *píph₃e-*, *sísde-* (§5.36; Ringe p. 34 *sísdeti*)

**Defect 1. 2du primary *-th₁es* (convention, misattributed).** `_handbook_verbal` puts *-th₁es* first in PRS.2DU and
SBJV.2DU, with the comment "(Ved. -thas vs -tas; Ringe)". But Ringe p. 31 gives *-tés* for **both** 2du and 3du. Fortson's
§5.28 table has *-e-to-*, and L&Y §4.2.5 reconstruct only *-to-* and say the primary dual is unclear. Only Beekes
p. 271 has *-tHe/os*, and he marks the *-th₁-* as tentative, on the model of his 2pl. Beekes's 2pl *-th₁e* / *-eth₁e* (pp. 259–260)
is **not** followed by the engine, so the current convention is internally inconsistent. Fix: put *-tes* first and keep
*-th₁es* as the alternative.

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ -499,4 +499,5 @@ def _handbook_verbal(spec: VerbSpec, out: Cells) -> Cells:
-    # primary 2du *-th₁es, distinct from 3du *-tes (Ved. -thas vs -tas; Ringe)
+    # primary 2du *-tes = 3du (Ringe p. 31; Fortson, L&Y give no distinct form); Beekes p. 271's tentative
+    # *-th₁es (Ved. -thas) is kept as an alternative
     for k in ("PRS.2DU", "SBJV.2DU"):
         if k in out:
-            out[k] = _uniq([re.sub("t([eé])s$", lambda m: "th₁" + m[1] + "s", f) for f in out[k]] + out[k])
+            out[k] = _uniq(out[k] + [re.sub("t([eé])s$", lambda m: "th₁" + m[1] + "s", f) for f in out[k]])
```
Test: `conjugate(VerbSpec("bʰére"))["PRS.2DU"] == ["bʰéretes", "bʰéreth₁es"]`, and for `VerbSpec("h₁és", "h₁s")` it is
`["h₁stés", "h₁sth₁és"]`. Impact: 9 tokens. In this family, *h₂éǵeth₁es* and *h₂életh₁es* (PRS.2DU). In the athematic
family, *h₁sth₁és* ×4, *dʰedʰh₁th₁és*, *dukth₁és* and *péh₂seth₁es* (SBJV.2DU).

**Defect 7. PTCP.MID without *h₁* when the thematic vowel is accented.** `_handbook_verbal` turns *-omnos* into
*-omh₁nos* with `f.replace("omnos", …)`. That misses *-ómnos*, so 313 usable lexemes keep *-ómnos* first: all tudáti,
*-yé-*, *-sḱé-* stems and the thematic aorists (*widómnos*, *gʷr̥h₃ómnos*, *gʷm̥yómnos*). L&Y §4.4.1 has thematic
*-o-mh₁no-*. Corpus: 0 tokens, because no plan used one of these as a middle participle.
```diff
@@ -497,2 +497,2 @@
     if spec.thematic and "PTCP.MID" in out:
-        out["PTCP.MID"] = _uniq([f.replace("omnos", "omh₁nos") for f in out["PTCP.MID"]] + out["PTCP.MID"])
+        out["PTCP.MID"] = _uniq([re.sub("([oó])mnos$", r"\1mh₁nos", f) for f in out["PTCP.MID"]] + out["PTCP.MID"])
```
Test: `VerbSpec("widé", None, "pf")` → PTCP.MID[0] `widómh₁nos`; `VerbSpec("gʷr̥h₃é")` → `gʷr̥h₃ómh₁nos`;
`VerbSpec("bʰére")` stays `bʰéromh₁nos`.

**Spec spot-check (all 1,206 thematic-present, thematic-aorist and stative/deponent lexemes scanned).**
- Every table lemma reproduces as its own PRS.3SG (or MID.PRS.3SG). The only mismatch is *gʷuHéti* → *guHéti*, which is
  the deliberate boukólos rule.
- 115 shape-rule stems carry no accent because their Wiktionary lemmas have none (*h₂emse-*, *teh₂ye-*, *gʰlinde-*,
  *spenh₁ne-*, …). They are used by 8 tokens. Low priority: a default-accent rule would be guesswork, so I propose none.
- *ǵʰlíe-* (hiatus, 2 tokens) comes from the lemma *ǵʰlíeti*. Left as is.
- *pr̥sḱéti* (table, 0 tokens) drops the root *ḱ* that Fortson §5.34 writes (*pr̥k̑-sk̑é-*). Optional override
  `{"id": "pie-lex-prskjeti", "spec": {"strong": "pr̥ḱsḱé", "weak": null, "kind": "impf"}, "spec_checked": true,
  "note": "Fortson §5.34 *pr̥k̑-sk̑é- (Ved. pr̥ccháti, Lat. poscit); the table drops the root ḱ (engine sweep)"}`.
- *wéryeti* is rendered *wérh₁yeti*. The *h₁* comes from the spec (LIV *u̯erh₁-*); Ringe p. 34 prints *wérye-ti*. Both
  are defensible.
- CRHV syllabification (*ǵíǵn̥h₁eti*, perfect *ǵeǵn̥h₁ḗr*) follows LIV² and Wiktionary; Gk γίγνομαι would favour
  *ǵíǵnh₁e-*. This is a notation convention, not a defect.

**Convention flag (no fix proposed): athematic statives.** *h₁rudʰéh₁ti* 'be red' has 50 tokens (PST.3SG 23, PRS.3SG 15),
and the factitive *néweh₂ti* has 1. Both are athematic in the table.
- Fortson §5.37 writes the stative *-eh₁-* and factitive *-eh₂-* as "probably also followed by *-i̯e/o-*" (Lat. rubēre,
  renovāre).
- L&Y §4.3.1 write *-eh₁-ye/o-* and, outside Anatolian, *-eh₂-ye/o-*. But they also cite Hitt. marš-e-zzi as athematic
  *-eh₁-*, which is what Wiktionary follows.
- So this is not clear-cut. If David wants the Fortson/L&Y form, the override is
  `{"id": "pie-lex-h1rudheh1ti", "spec": {"strong": "h₁rudʰéh₁ye", "weak": null, "kind": "impf"}, "spec_checked": true}`,
  which gives *h₁rudʰéh₁yeti*, matching the corpus's other statives *sth₂éh₁yeti* and *widéh₁yeti*. The same pattern applies
  to *néweh₂ti* → *néweh₂ye-*. Either way, *h₁rudʰéh₁ti* also gets defect 4.
- Beekes p. 260 reconstructs a thematic 3pl *-o*. Fortson, Ringe and L&Y have *-onti*, so the engine is right to follow
  them.

## 2. Deponents (media tantum) and the middle

**Right.**
- *ḱéytor* is athematic and acrostatic (strong = weak *ḱéy-*): *ḱéyh₂er*, *ḱéytor | ḱéyor*, 3pl *ḱéyn̥tor | ḱéyror*,
  *ḱéym̥h₁nos*. L&Y §4.2.3 and §4.3.1 give *ḱéy-or*/*-ro* as archaic and *-tor* as productive; Fortson §5.16 has *ḱei̯-o*.
- *wéstor* matches Ringe p. 34 (*wés-tor*) and L&Y (*wés-(t)or*).
- *sékʷetor* matches L&Y §4.2.3. Its MID.IMP.2SG *sékʷeso* matches Lat. sequere.
- `check_plan` forces voice MID on any V slot whose lemma ends in *-tor/-toy*. All 202 deponent tokens are MID.*.

**Defect 9. 35 thematic deponents are unusable.** `by_shape` returns `unknown:middle-only` for every *-tor* lemma. The
group includes the three media tantum that L&Y §4.3.1 and Ringe p. 34 cite by name:
- *mr̥yétor* 'dies' (LIV² p. 439 *mr̥-i̯é-*)
- *ǵn̥h₁yétor* 'is born' (LIV² p. 163)
- *mn̥yétor* 'thinks' (Fortson §5.32 *mn̥-i̯é-*; LIV² p. 435)

It also includes *nésetor* (LIV² p. 454 *nés-e-*) and *wértetor* (LIV² p. 691 *u̯ért-e-* "Med."). These are the only
glossed ones; the other 30 have no gloss.

The thematic ones are ordinary thematic stems with middle endings: stripping *-tor* gives the spec. I backtested this
against the two thematic deponents that have tables, *sékʷetor* and *pérdetor*: 148/148 cells. *séwHtor* and
*h₁éh₁ugʰtor* are athematic and stay unusable. Fix (classify.py, with a BACKTEST that has tables):
```diff
--- a/pie/classify.py
+++ b/pie/classify.py
@@ -142,4 +142,6 @@ def by_shape(e: dict) -> Classified:
     if is_verb:
+        if f.endswith(("etor", "étor")):     # thematic media tantum: *mr̥-yé-tor, *sékʷ-e-tor (L&Y §4.2.3, §4.3.1)
+            return Classified(VerbSpec(_strip(f, "tor")), "shape:thematic-middle", "verb")
         if f.endswith(("tor", "toy")):
             return Classified(None, "unknown:middle-only", "verb")
```
Test: `by_shape({"form": "mr̥yétor", "pos": "verb", "kind": "word"}).spec == VerbSpec("mr̥yé")`, and the MID.PRS.3SG of
that spec renders `mr̥yétor` (= lemma).

If the integrator prefers data only, these 5 override lines do the same for the glossed deponents:
```json
{"id": "pie-lex-mryetor", "spec": {"strong": "mr̥yé", "weak": null, "kind": "impf"}, "spec_checked": true, "note": "media tantum *mr̥-yé-tor 'dies' (L&Y Handbook ch. 122 §4.3.1; LIV² p. 439 *mr̥-i̯é-: Ved. mriyáte, Lat. morior); was unknown:middle-only (engine sweep, thematic-verbs)"}
{"id": "pie-lex-gjnh1yetor", "spec": {"strong": "ǵn̥h₁yé", "weak": null, "kind": "impf"}, "spec_checked": true, "note": "media tantum *ǵn̥h₁-yé-tor 'is born' (Ringe 2006 p. 34; L&Y §4.3.1: OIr. gainithir; LIV² p. 163); was unknown:middle-only (engine sweep, thematic-verbs)"}
{"id": "pie-lex-mnyetor", "spec": {"strong": "mn̥yé", "weak": null, "kind": "impf"}, "spec_checked": true, "note": "media tantum *mn̥-yé-tor 'thinks' (L&Y §4.2.3, §4.3.1; Fortson §5.32 *mn̥-i̯é-: Ved. mányate, Gk μαίνεται); was unknown:middle-only (engine sweep, thematic-verbs)"}
{"id": "pie-lex-nesetor", "spec": {"strong": "nése", "weak": null, "kind": "impf"}, "spec_checked": true, "note": "thematic middle *nés-e-tor 'returns home' (LIV² p. 454 *nés-e-: Ved. násate, Gk νέομαι); was unknown:middle-only (engine sweep, thematic-verbs)"}
{"id": "pie-lex-wertetor", "spec": {"strong": "wérte", "weak": null, "kind": "impf"}, "spec_checked": true, "note": "thematic middle *u̯ért-e-tor 'turns' (LIV² p. 691 *u̯ért-e- Med.: Ved. vártate, Lat. vertor); was unknown:middle-only (engine sweep, thematic-verbs)"}
```

**Defect 10. Deponent participles are not voice-checked** (preventive; all current deponent participles are MID).
```diff
--- a/pie/realize.py
+++ b/pie/realize.py
@@ -325,3 +325,6 @@ def check_plan(plan: dict, lx: Lexicon | None = None) -> list[str]:
                 elif ptcp.get("voice", "ACT") not in ("ACT", "MID"):
                     errs.append(f"{where}: participle voice must be ACT or MID")
+                elif lx.entries[lid]["form"].endswith(("tor", "toy")) and ptcp.get("voice", "ACT") != "MID":
+                    errs.append(f"{where}: {lid} is middle-only (deponent): its participle is middle (voice MID)")
```
Test: a MOD participle slot on `pie-lex-kjeytor` with voice ACT is rejected; with voice MID it passes.

**Defect 3 (cross-family; middle 3sg/3pl).** The CCu/CCi glide rule in `_handbook_verbal` puts every rewritten form in
front of the cell. As a result, the archaic t-less form outranks the productive one: MID.AOR.3SG of *ḱléwt* is
*ḱluwó | ḱlutó*, and MID.PST.3SG of *ḱl̥néyti* is *ḱl̥niyó | ḱl̥nitó*. Sixty-four lexemes are affected (measured). L&Y §4.2.7 call *-o*
the unproductive relic and *-to* the productive ending, and the engine's own tables list *-tó* first. Fix: rewrite in
place, so the order is kept.
```diff
@@ -509,6 +509,5 @@
         if bad != good:
             for k, forms in out.items():
-                new = [good + f[len(bad):] for f in forms if f.startswith(bad)]
-                if new:
-                    out[k] = _uniq(new + forms)
+                if any(f.startswith(bad) for f in forms):
+                    out[k] = _uniq([good + f[len(bad):] if f.startswith(bad) else f for f in forms] + forms)
```
Test: `VerbSpec("ḱléw", "ḱlu", "pf")`: MID.AOR.3SG == `["ḱlutó", "ḱluwó", "ḱl̥wó"]`, while AOR.3PL[0] stays `ḱluwént`
and PTCP.ACT[0] stays `ḱluwónts`. Impact: 5 tokens (*ḱl̥niyó* ×4, *ḱluwó* ×1).

**Cross-family note, not counted.** 'To die' is realized only through the active root aorist *mért*: 139 tokens (AOR 101,
SBJV 22, OPT 12, IMP 4). The handbooks make the present deponent (*mr̥-yé-tor*, L&Y §4.3.1). For the aorist, LIV² p. 439
lists middle reflexes (Ved. ámr̥ta, Arm. med. meṙaw) beside active ones (Hitt. merta, OCS umrětъ), so the evidence is
mixed and it is the root-aorist auditor's call. Its AOR.3PL *m̥rént* (20 tokens) has a word-initial syllabic *m̥* before
*r* + vowel, which looks like a phon.py syllabification issue (*#mrV*, cf. *mréǵʰu-*). I am flagging that to the
root-aorist and phon auditors.

## 3. s-aorist

**Right.**
- *wḗǵʰs-* (table): lengthened grade in the active indicative singular, *wḗǵʰst*, *wḗǵʰsm̥*. This matches Ringe p. 34
  (*wḗǵʰ-s-t*, *dḗyḱ-s-t*), L&Y §4.3.2 (*wḗǵʰ-s-t*) and Beekes p. 263.
- 3pl *wéǵʰsn̥t* has zero-grade *-n̥t* after the accented stem (L&Y §4.2.5: s-aorists take *-n̥t*).
- Middle on the full grade, *wéǵʰsto* (Fortson §5.47: full grade in the middle).

**Handbooks disagree on the plural.** Beekes p. 264 has the lengthened grade in the **whole** indicative active (Ved.
ávākṣma, OCS věsomъ). Fortson §5.47 cites the same plurals but suggests the ablaut may originally have been of the
Narten type (lengthened sg. / full grade elsewhere). Wiktionary and the engine have *wéǵʰsme*. I recommend keeping it: the handbook convention follows
Fortson where Beekes and Fortson split.

**Defect 5. Subjunctive and future imperative on the lengthened grade.** The engine gives *wḗǵʰseti*, *wḗǵʰstōd*. Fortson
§5.55 says aorist subjunctives use the full grade of the aorist stem, and Beekes §18.3.1c has the lengthened grade in the
indicative only. Expected *wéǵʰseti*. The patch also covers Narten presents: Beekes p. 264 and §18.7 make the lengthened
grade an indicative-only (static-inflection) feature, but no book under raw/ prints a Narten subjunctive. The 3 affected
tokens are athematic (*h₂wḗh₁eti*, *h₂wḗh₁oh₂*, *tḗtḱomes* → *h₂wéh₁-*, *tétḱ-*) and are left for the athematic auditor to
confirm.

**Defect 6. Optative of lengthened-grade stems.** The engine gives *wéǵʰsyeh₁t*: full-grade *-yeh₁-* with no accent, on
an accented stem. Fortson §5.57: where the root is accented (Narten), the suffix is zero-grade *-ih₁-* throughout. Expected
*wéǵʰsih₁t*.

**Defect 4. Optative 3pl *-n̥t*.** `on()` turns *-ih₁ént* into *-ih₁n̥t* after any accented stem. Fortson §5.57 says the
optative 3pl was always *-ent*, never *-n̥t*, even unaccented. The Wiktionary module writes *-n̥t*, so the patch keeps that
for the `wiktionary` convention only. Tier 3 has 3 tokens: *h₁rudʰéh₁ih₁n̥t* (this family), *bʰúHih₁n̥t* and *dédh₃ih₁n̥t*
(athematic). I left the singular of *bʰúH-* alone (*bʰúHyeh₁t*): Ved. bhūyā́t has the accented full-grade suffix, so the
zero-grade-throughout rule is restricted to stems with a lengthened grade.

Patch for defects 4–6 (`wk` is `conv == "wiktionary"` in `_phase_b`):
```diff
@@ -587,13 +587,20 @@ def _phase_b(spec: VerbSpec, conv: str) -> Cells:
     def on(stem, e: str) -> str:
-        if has_accent(stem) and e in ("ih₁ént", "ónts"):
-            e = {"ih₁ént": "ih₁n̥t", "ónts": "n̥ts"}[e]   # accented stem: zero-grade -n̥t (bʰúHih₁n̥t, h₁édn̥ts)
+        # accented stem: participle -n̥ts (h₁édn̥ts); optative 3pl -n̥t only in the Wiktionary module
+        # (handbook: always *-ent, Fortson §5.57)
+        if has_accent(stem) and (e == "ónts" or (e == "ih₁ént" and wk)):
+            e = {"ih₁ént": "ih₁n̥t", "ónts": "n̥ts"}[e]
         return render(fix(join(stem, _p(e))))
 
     # subjunctive stem: the strong stem, e-grade in the perfect (wóyd- → wéyd-)
     sbjv = [replace(x, base="e") if (spec.kind == "stat" and x.kind == "V" and x.base == "o" and x.acc) else x
             for x in strong]
+    # lengthened-grade strong stem (s-aorist wḗǵʰs-, Narten smḗy-): the lengthened grade is indicative-only, so the
+    # subjunctive and -tōd take the full grade (Fortson §5.55, Beekes §18.3.1c) and the optative is -ih₁- throughout
+    # (Fortson §5.57)
+    lengthened = not wk and any(x.long and x.acc and x.kind == "V" for x in strong) and has_accent(weak)
+    if lengthened:
+        sbjv = weak
     out.update(_slots("SBJV", _SH_SBJV, lambda e: on(sbjv, e)))
-    out.update({k: v for k, v in _slots("OPT", [*_ATH_OPT_SG, *_ATH_OPT_PL], lambda e: on(weak, e)).items()})
+    opt = ["ih₁m̥", "ih₁s", "ih₁t", *_ATH_OPT_PL] if lengthened else [*_ATH_OPT_SG, *_ATH_OPT_PL]
+    out.update({k: v for k, v in _slots("OPT", opt, lambda e: on(weak, e)).items()})
@@ -603,2 +610,2 @@
     if conv == "handbook":
-        out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = [on(strong, "tōd")]
+        out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = [on(sbjv if lengthened else strong, "tōd")]
```
Tests:
- `VerbSpec("wḗǵʰs", "wéǵʰs", "pf")`: AOR.3SG[0] `wḗǵʰst` (unchanged), SBJV.3SG[0] `wéǵʰseti`, MID.SBJV.3SG[0]
  `wéǵʰsetor`, OPT.3SG[0] `wéǵʰsih₁t`, OPT.3PL[0] `wéǵʰsih₁ent`, IMP.FUT.3SG `wéǵʰstōd`.
- `VerbSpec("bʰúH", "bʰúH", "pf")`: OPT.3SG[0] stays `bʰúHyeh₁t`, OPT.3PL[0] `bʰúHih₁ent`; under the `wiktionary`
  convention OPT.3PL[0] stays `bʰúHih₁n̥t`.
- IMP.3SG *wḗǵʰstu* is left alone: no handbook prints an s-aorist imperative.

**Defect 8. The s-aorist is effectively missing (coverage).** Only *wḗǵʰst* is usable, and it has 0 tokens. There are
62 more *ḗ…st* lemmas:
- *dḗyḱst* 'pointed out' (Ringe p. 34) and *prḗḱst* 'asked' fall to `shape:root-aorist`, and `zero_grade()` fails on the
  long vowel.
- The other 60 are LIV derivatives with no pos, so `by_shape` sends them to `unknown:noun-shape`. They include *ḱlḗwst*
  'heard', *wḗdʰst* 'led' (Fortson §5.47 OCS věsomŭ), *stḗygʰst*, *wḗydst*, *plḗh₁st*, *h₃rḗǵst*.

The rule below reproduces Wiktionary's own template (args 1 = lengthened, 2 = full grade). It backtests 58/58 cells against
the one table, *wḗǵʰst*. That is thin evidence, so a spot review of the derived glosses before planners see them is
advisable.
```diff
--- a/pie/classify.py
+++ b/pie/classify.py
@@ -141,2 +141,7 @@ def by_shape(e: dict) -> Classified:
     is_verb = pos == "verb" or (pos is None and f.endswith(("ti", "tor", "toy")))
 
+    # s-aorist (Ringe *dḗyḱ-s-t, *wḗǵʰ-s-t; Fortson §5.47): lengthened grade in the active indicative, full grade
+    # elsewhere (Wiktionary's ine-conj-pf args wḗǵʰs / wéǵʰs). Many are LIV derivatives without pos.
+    if f.endswith("st") and "ḗ" in f and pos in (None, "verb") and e.get("aspect") in (None, "pf"):
+        st = f[:-1]
+        return Classified(VerbSpec(st, st.replace("ḗ", "é"), "pf"), "shape:s-aorist", "verb")
     if is_verb:
```
Measured effect on `by_shape` over the whole lexicon: 60 entries move from `unknown:noun-shape` and 3 from
`shape:root-aorist` (*dḗyḱst*, *prḗḱst*, *wḗǵʰst*) to `shape:s-aorist`. Nothing else changes. Example after patch 5:
*dḗyḱsm̥, dḗyḱst, déyḱsn̥t*, mid. *déyḱsto*, sbjv. *déyḱseti*. Test: `by_shape` of *dḗyḱst* (pos verb, aspect pf) is
`VerbSpec("dḗyḱs", "déyḱs", "pf")`, rule `shape:s-aorist`. Land this together with patch 5, or the new lexemes get
*dḗyḱseti*.

## 4. Thematic aorists

All right. The thematic aorist has zero grade and an accented thematic vowel: *widét*, *h₁ludʰét* (Fortson §5.48; L&Y
§4.3.2; Beekes p. 263; Ringe p. 34 *h₁ludʰéd*). The reduplicated aorist *wéwkʷet* → *wéwket* (boukólos) matches Fortson
§5.49 *u̯e-uk^w-e-* and L&Y *we-ukʷ-e-t*. Its endings are those of the thematic imperfect (Beekes p. 264). The cells check
out:
- subjunctive *widḗti* (Gk ἴδῃ)
- optative *widóyh₁t*
- imperative *widé* (Gk ἰδέ)
- participle *widónts* (Gk ἰδών)
- no augment (L&Y §4.2.1)

The only defect is the middle participle (defect 7), with 0 tokens. All 407 tokens are correct.

## 5. The perfect (stative)

**Right.**
- Reduplication *Ce-* (Fortson §5.51): *dedórḱ-*, *memón-*, *gʷegʷóm-*, *ǵeǵónh₁-*; *s*-clusters *stestóh₂-* (Ringe p. 34
  *ste-stóh₂-e*); *h₂eh₂nóḱ-* (Ringe p. 34 *h₂e-h₂nóḱ-e*); unreduplicated *wóyd-* (Fortson §5.52; Beekes p. 265).
- Accented o-grade in the singular, zero grade with accented endings in the dual and plural (Fortson §5.51; Beekes p. 265;
  L&Y §4.3.3 *me-món-e*, *me-mn-ḗr*).
- Endings *-h₂e -th₂e -e -wé -mé -é -ḗr* (Ringe p. 33; Fortson §5.52 table; L&Y §4.2.6 *-ēr* by Szemerényi from *-ers*;
  Beekes p. 265). The dual 2/3 is left empty, correctly: Ringe "???", and L&Y say it cannot be reconstructed.
- No middle cells (L&Y §4.2.3: the perfect middle is a late category).
- Optative on the weak stem *widyéh₁t* (Ved. vidyā́t), 3pl *widih₁ént* (Fortson §5.57).
- Participle *widwṓs* with *-wos-/-us-* (L&Y §4.4.1; Ringe p. 33). Spot-checked all 24 perfects; all weak stems are
  correct (*dedwi-* Gk δέδιμεν, *bʰebʰidʰ-* ἐπέπιθμεν, *lelikʷ-*, *ḱeḱlu-*, *bʰebʰih₂-*).

**Defect 2. *dedwóye* 'be afraid': plural *deduyḗr*, *deduyé*, *deduyih₁ént*.** The weak stem *dedwi-* goes through the
junction rule to *deduy-* before a vowel. Gk δείδιμεν / δειδίασι keep the *i* (*dwi-*), and the engine's own CCu/CCi fix
(Sievers/Lindeman: *ḱluwónt-*) exists for exactly this. But it excludes any stem whose second-to-last segment is a glide
(`wk[-2].base not in ("w","y")`). Only two usable specs hit the exclusion: *dedwi-* and the root aorist *kʷyu-*. Excluding
only identical pairs (*-wu-*, *-yi-*) fixes both.
```diff
@@ -505,3 +505,3 @@ def _handbook_verbal(spec: VerbSpec, out: Cells) -> Cells:
     if (not spec.thematic and len(wk) > 2 and wk[-1].base in ("w", "y") and wk[-1].syl
-            and wk[-2].kind != "V" and wk[-3].kind != "V" and wk[-2].base not in ("w", "y")):
+            and wk[-2].kind != "V" and wk[-3].kind != "V" and wk[-2].base != wk[-1].base):
```
Measured output:
- *dedwóye*: PRF.3PL `dedwiyḗr | deduyḗr`, PRF.2PL `dedwiyé`, OPT.3PL `dedwiyih₁ént`, IMP.3PL `dedwiyéntu`. PRF.1PL
  stays `dedwimé`.
- *kʷyéwt* (root aorist): AOR.3PL `kʷyuwént` (was *kʷiwént*), PTCP.ACT `kʷyuwónts`. 0 tokens; flag to the root-aorist
  auditor.

Test: `VerbSpec("dedwóy", "dedwi", "stat")` PRF.3PL[0] == `dedwiyḗr`. Impact: 8 tokens (*deduyḗr* PRF.3PL ×8), the
largest in this family.

**Open, no fix: perfect subjunctive e-grade** (*wéydeti*, *dedérḱeti*; 18 tokens). Engine and Wiktionary agree. Fortson
§5.55 says only "the strong stem", which for a perfect is the o-grade, and Gk εἰδέω supports the e-grade for 'know'. No
book under raw/ prints a perfect subjunctive paradigm, so this cannot be checked.

**Sound rules in this family (no defects).**
- Bartholomae is applied nowhere in the engine. Perfect 2sg forms are written morphophonemically (*bʰebʰówdʰth₂e*,
  *wewórtth₂e*), like Fortson's *u̯óid-th₂e*. This is a cross-family convention, not this family's defect.
- Pinault is Wiktionary-only by documented convention, so the handbook keeps the laryngeal before *y* in perfect
  optatives (*stesth₂yéh₁t*, *bʰebʰih₂yéh₁t*).
- *-ye-* after a heavy syllable is written without Sievers (*spéḱyeti*, *sédyeti*), which is how Fortson §5.32 and L&Y
  §4.3.1 spell it.
- Lindeman/Sievers after CCi/CCu is handled by the glide rule (defects 2 and 3).
- Boukólos applies as designed: *wéwkʷe-* → *wéwket*, *gʷuHé-* → *guHéti*, *lelikʷ-* + *-wé* → *lelikwé*.
- Szemerényi: 3pl *-ḗr*, participle *-wṓs*.

**Open, unverifiable: perfect imperatives** (42 tokens, 27 of them *memóne* IMP; *widdʰí* = Ved. viddhí). No handbook
gives a paradigm. The engine extrapolates the athematic rules: zero grade + *-dʰí*, and 3sg on the strong stem
(*wóydtu*).

## 6. Moods across the family (summary)

| Mood | Thematic | Athematic stems in this family (perfect, s-aorist, statives, deponents) |
|---|---|---|
| Subjunctive | long vowel *-ē-/-ō-* + primary endings ✓ (Fortson §5.55, L&Y Tab. 122.10) | strong stem + *-e/o-* ✓; lengthened-grade stems wrong (defect 5); perfect e-grade unverifiable |
| Optative | *-oyh₁-* all persons, 3pl *-oyh₁ent* ✓ | *-yéh₁-/-ih₁-* on weak stem ✓; 3pl *-n̥t* after accent (defect 4); lengthened stems (defect 6) |
| Imperative | bare stem, *-etu*, *-ete*, *-ontu*, *-etōd* ✓ | *-dʰí* on zero grade ✓ |
| Middle | *-oh₂er … -edʰwe … -ontor* ✓; PTCP *-omh₁nos* (defect 7) | ✓; *-o* order (defect 3) |

Notation: Fortson and L&Y write the thematic optative *-o-ih₁-* (disyllabic). The engine and Wiktionary write
*-oyh₁-*. Same reconstruction, different spelling; no change proposed.

## 7. Tokens whose first form changes if all morph.py patches land (measured, 28)

| Tokens | Lexeme / cell | Now → patched | Defect |
|---|---|---|---|
| 8 | dedwóye PRF.3PL | deduyḗr → dedwiyḗr | 2 |
| 4 | h₁ésti PRS.2DU | h₁sth₁és → h₁stés | 1 |
| 4 | ḱl̥néyti MID.PST.3SG | ḱl̥niyó → ḱl̥nitó | 3 |
| 1 each | h₂éǵeti, h₂életi PRS.2DU; dʰédʰeh₁ti, déwkti PRS.2DU; péh₂sti SBJV.2DU | -th₁es → -tes | 1 |
| 1 each | h₁rudʰéh₁ti, bʰúHt, dédeh₃ti OPT.3PL | -ih₁n̥t → -ih₁ent | 4 |
| 1 each | h₂wḗh₁ti SBJV.1SG/3SG; tḗtḱti SBJV.1PL | h₂wḗh₁- → h₂wéh₁-; tḗtḱ- → tétḱ- | 5 |
| 1 | ḱléwt MID.AOR.3SG | ḱluwó → ḱlutó | 3 |

The classify.py rules (defects 8 and 9) change no existing token. They add 63 s-aorist and 35 deponent lexemes for
future plans, including 'die', 'be born' and 'think' as middle presents.
