# Engine sweep: thematic (o-stem) nouns and adjectives

Auditor family: masculine and neuter o-stems (root-accented vs oxytone, vocative), thematic adjectives in three genders (feminine *-eh₂*), *-tó-/-nó-* verbal adjectives, *-yo-* adjectives, thematic compound second members. Engine code: `pie/morph.py` `_THEMATIC`, `_THEMATIC_NEUTER`, `_thematic`, `AdjSpec.genders`; `pie/realize.py` `Lexicon.cells`; `pie/compound.py`; `pie/phon.py` `delabialize`. Corpus: `corpus/tier3/*.jsonl` (42,017 tokens; **4,630 tokens** belong to this family: 3,545 noun, 1,085 adjective, over 266 lexemes).

Scratch scripts: `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/thematic_*.py`.

## Ranked defects (by corpus tokens affected)

"Defect" means the engine's primary (handbook) form is wrong by the books, or the paradigm is internally inconsistent. Convention questions (the books disagree with each other, and the project already picked a side) are listed separately below and are not counted.

| # | Defect | Tokens | Fix type |
|---|---|---|---|
| 1 | Boukólos delabialization before unaccented *u* rewrites the headword *pérkʷunos* as *pérkunos* in every cell | 49 | code (`morph.py`/`phon.py`), gated by convention |
| 2 | Vocative plural (and dual) not accent-retracted, though VOC.SG is (*deywṓs* for Ved. *dévās*) | 42 (40 PL, 2 DU) | code (`morph.py`) |
| 3 | *Hroth₂ós* 'chariot' is oxytone; handbook and Vedic are root-accented *Hróth₂os* | 21 | override |
| 4 | *dʰubʰrós* 'deep': Wiktionary table arg drops the root aspirate, so every cell is *dʰubr-* | 16 | override |
| 5 | Mixed-accent and mixed-ablaut paradigms: `Lexicon.cells` prepends the lemma to NOM/ACC/VOC.SG of a table noun whose table stem differs from it (silver, washbasin, lifetime) | 14 inconsistent (13 forms change) | code (`realize.py`, `compound.py`) + 3 overrides |
| 6 | Unaccented thematic stems in the corpus (legacy batches pilot, pilot2, b001, b002) | 66 | regenerate; overrides for 2 |
| 7 | Neuter s-stems misrouted to the thematic masculine (*ḱéh₂dos* 'hatred', *sterḱos* 'dung', plus 8 unused ones) | 7 | overrides |
| 8 | *súHros* 'sour': table oxytone vs root-accented headword (books disagree) | 4 | override |
| 9 | Neuter dual primary *-oy* instead of *-oyh₁* | 4 | code (`morph.py`) |
| 10 | Adjectives and pronominals classified as plain masculine nouns (*mr̥wós*, *h₁rudʰyos*, *h₂élyos*, ...): no feminine/neuter agreement | 2 attested mis-agreements | overrides (pos) |
| 11 | Pronouns usable as thematic nouns, duplicating closed classes (*Hyós*, *kʷos*, *h₁énos*) | 0 | blocklist |
| 12 | Numerals *dwóh₁*, *bʰóh₁* declined as full thematic adjectives (singular/plural cells, f. dual *dwéh₂h₁*) | 0 | blocklist / note |
| 13 | Feminine thematic-adjective dual *-eh₂h₁* (books: *-eh₂ih₁*) and vocative *-eh₂* (books: *-a*) | 0 in this family | eh₂-family fix |

Coverage finding (no wrong forms, large reach): **282 neuter o-stems (`shape:thematic-neuter`) are unusable** only because the backtest scores them 0.81 < 0.85, and every failing table is one of the inconsistent Wiktionary tables of item 5. See "Gating" below.

Totals: **13 defects**, 225 corpus tokens with a wrong or inconsistent primary form (66 of them legacy unaccented tokens).

## Inventory

1,424 usable lexemes of the family (from `inflection_specs.jsonl`, `usable: true`):

| Sub-type | Rule | Count | Accent |
|---|---|---|---|
| masculine o-stem noun | `shape:thematic` | 1,144 | 583 oxytone, 265 barytone, 352 **unaccented** (1 f, 1 f unaccented by lexicon gender) |
| masculine o-stem noun | `table` | 58 | (incl. f. *snusós*, *bʰeh₂ǵos*) |
| neuter o-stem noun | `table` | 16 | 6 oxytone, 7 barytone, 3 unaccented |
| thematic adjective | `shape:thematic-adj` | 111 | |
| thematic adjective | `table` | 95 | adjectives overall: 171 oxytone, 26 barytone, 9 unaccented |
| (unusable) neuter o-stem | `shape:thematic-neuter`, `-reflex` | 282 | 160 accented |

Adjective suffix classes (by stem ending): *-tó-* 77, *-to-* 3, *-ro-* 39, *-nó-* 12 / *-no-* 6, *-wo-* 13, *-yo-* 12, *-lo-* 5, *-mo-* 4, other 34. Compounds in the corpus: 28 tokens, 10 compounds (6 with a thematic second member).

## Sub-type checks against the books

### Masculine o-stems: endings

Engine handbook primaries: NOM *-os*, VOC *-e*, ACC *-om*, GEN *-osyo*, ABL *-ōd*, DAT *-ōy*, LOC *-oy*, INS *-oh₁*; DU *-oh₁*; PL NOM *-ōs*, ACC *-ons*, GEN *-ōm*, DAT/ABL *-oybʰos*, LOC *-oysu*, INS *-ōys*.

| Cell | Engine | Fortson | Ringe | Beekes | L&Y (Handbook v3 ch. 122) | M&A |
|---|---|---|---|---|---|---|
| GEN.SG | -osyo | -osi̯o (§6.48; -os Anatolian) | -osyo (p. 48) | -os, -osio (§13.2.9) | -os, -osyo, -oso | -os (Tab. 4.5) |
| ABL.SG | -ōd | -ōd/-ōt < *-o-(h₂)ad (§6.49) | -ead | -ōd | -ōd, *-oh₁ad | -ōd |
| DAT.SG | -ōy | -ōi (§6.47) | -oey | -ōi | -ōi | -ōi |
| LOC.SG | -oy, -ey | -oi, -ei (§6.47) | -ey | -oi | -oi | -oi |
| INS.SG | -oh₁ | -oh₁ (§6.47) | -oh₁ | -oh₁ | -oh₁ | -oh₁ |
| NOM.DU | -oh₁ | -oh₁ (§6.50) | -oh₁ | | -oh₁e → -oh₁ | |
| NOM.PL | -ōs | -ōs (§6.52) | -oes | -ōs | -ōs | -ōs |
| ACC.PL | -ons | -ons, -ōns (§6.55) | -ons | -ons | -oms / -ons | -ons |
| GEN.PL | -ōm | **-oHom** (§6.56) | **-ooHom** | -om | **-oh₁/₃om** | -om |
| DAT/ABL.PL | -oybʰos | -o-bʰ(y)os, -oi-bʰ- in IIr (§6.57) | -o(y)mos | -omus | -o-bʰos; -oi- "less likely at PIE stage" | -oibʰ(y)os / -omus |
| LOC.PL | -oysu | -oisu (§6.57) | -oysu | -oisu | | -oisu |
| INS.PL | -ōys | -ōis (§6.57) | -ōys | -ōis | -ōis | -ōis |

Right: everything in the singular, the dual, NOM/ACC/LOC/INS.PL. Accent of oxytones stays on the thematic vowel's replacement (*deywṓy*, *deywṓs*, Ved. *devā́ya*, *devā́s*): right. Neuter NOM.PL *-éh₂* takes the accent of an oxytone (*yugéh₂*; Ringe p. 48–49 *yugéh₂*, Ved. *yugā́*): right.

Convention notes (not defects, see last section): GEN.PL and DAT/ABL.PL. Also, the `morph.py` header attributes the contracted *-ōs/-ōy/-ōd* and gen. pl. *-ōm* to "Fortson/Ringe/Byrd". That is wrong for Ringe, who prints the uncontracted *-oes, -oey, -ead* (the "wiktionary" convention), and for the gen. pl.: neither Fortson (*-oHom*) nor Ringe (*-ooHom*) prints *-ōm*. Fix the docstring.

### Vocative (defect 2)

Fortson §6.47: VOC.SG accent retraction (Ved. *vī́ra*, Gk *ádelphe*); engine does this (`wl̥kʷós`-type → *wĺ̥kʷe*, *deywós* → *déywe*). Ringe p. 48 prints the oxytone vocative unretracted (*nisdé*); the engine keeps that as the alternative. Fine.

Fortson §6.52: the vocative **plural** also had retraction, judging by Ved. *dévās* (voc. pl. of *devá-*). The engine's VOC.PL is the NOM.PL, so it prints *deywṓs* for exactly the form Fortson cites. L&Y (§2.1.1) state that the VOC.PL was identical to the NOM.PL; that is a statement about endings and says nothing about accent. Since the handbook convention already follows Fortson for VOC.SG on the same Vedic evidence (initial accent of every Vedic vocative), VOC.PL should follow. The dual is an extrapolation: Fortson states it only for the plural, but the Vedic rule is number-independent.

Corpus: 40 VOC.PL + 2 VOC.DU tokens of non-initially-accented stems (*deywṓs* 26, *wiHrṓs* 3, *Hyudʰsmṓs* 2, *yemHṓs* 2, *sprongʰṓs* 2, *yemHóh₁* 2, ...). Root-accented stems are unaffected.

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ def _thematic(spec: NounSpec, conv: str) -> Cells:
     if conv == "handbook" and spec.gender != "n" and has_accent(stem):
         # vocative accent on the first syllable (Ved. vŕ̥ka, Gk ἄδελφε): wĺ̥kʷe, moysé → móyse
         out["VOC.SG"] = _uniq([render(_initial_accent(base + _p("e")))] + out["VOC.SG"])
+        # the plural and dual vocative retract too (Fortson §6.52: Ved. voc. pl. dévās vs nom. devā́s);
+        # the unretracted nominative form stays as the alternative
+        for feat in ("VOC.PL", "VOC.DU"):
+            hb = _THEMATIC["handbook"][feat][0]
+            out[feat] = _uniq([render(_initial_accent(base + _p(hb)))] + out[feat])
     return out
```

Test (tests/test_morph.py):

```python
def test_thematic_vocative_plural_retracts():
    c = decline(NounSpec("deywó"), "handbook")
    assert c["VOC.PL"][0] == "déywōs" and "deywṓs" in c["VOC.PL"]     # Fortson §6.52, Ved. dévās
    assert c["VOC.DU"][0] == "déywoh₁"
    assert decline(NounSpec("wĺ̥kʷo"), "handbook")["VOC.PL"][0] == "wĺ̥kʷōs"   # already initial
    assert decline(NounSpec("yugó", gender="n"), "handbook")["VOC.PL"][0] == "yugéh₂"  # neuter = nominative
```

The same retraction applies to the athematic and eh₂ VOC.PL; that belongs to those families, and the integrator may want one helper.

### Neuter o-stems (defect 9)

Right: NOM/ACC/VOC.SG *-om*; NOM.PL *-eh₂* with the accent of an oxytone (Fortson §6.54; Ringe p. 49 *wérǵeh₂*, *yugéh₂*; Beekes §13.2.9 *-h₂*); the oblique cases as the masculine.

Wrong order: NOM/ACC/VOC.DU primary *-oy*, alternative *-oyh₁*. Fortson §6.50 gives *-o-ih₁* (Ved. *yugé*, OCS *izě*); L&Y §2.1.1 give *-o-ih₁*; Ringe p. 48 *-oy(h₁)*; M&A give neuter 'two' as *dwoih₁*. The handbook primary should be *-oyh₁*. Corpus: 4 tokens (*déh₃roy* 2, *déh₃noy* 1, *h₁rowdʰóy* 1).

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
 _THEMATIC_NEUTER = {
     "NOM.SG": ["om"], "VOC.SG": ["om"], "ACC.SG": ["om"],
-    "NOM.DU": ["oy", "oyh₁"], "VOC.DU": ["oy", "oyh₁"], "ACC.DU": ["oy", "oyh₁"],
+    # *-o-ih₁ (Fortson §6.50, L&Y ch. 122 §2.1.1; Ringe -oy(h₁)); bare -oy kept as the alternative
+    "NOM.DU": ["oyh₁", "oy"], "VOC.DU": ["oyh₁", "oy"], "ACC.DU": ["oyh₁", "oy"],
     "NOM.PL": ["eh₂"], "VOC.PL": ["eh₂"], "ACC.PL": ["eh₂"],
 }
```

If the crosscheck needs Wiktionary's own order for the "wiktionary" run, gate it: `_THEMATIC_NEUTER` is shared by both conventions, so either split it per convention or reorder only when `conv == "handbook"`. Test:

```python
def test_thematic_neuter_dual_is_oyh1():
    assert decline(NounSpec("yugó", gender="n"), "handbook")["NOM.DU"][0] == "yugóyh₁"   # Fortson §6.50
```

### Accent classes and per-lexeme spot-check

I checked the 266 lexemes that occur in the corpus by hand (stem, accent, gender, reflexes) and ran four automatic checks over all 1,424: (a) table-arg vs headword, (b) engine form vs naive stem+ending (to catch phonological rewrites), (c) daughter evidence for neuter gender (PGmc *-ą*, PItal./PCelt. *-om*, PIIr. *-am*, Lat. *-um*, Gk *-ον*), (d) e-grade root-accented CéC-os nouns (the s-stem shape). Gender, root grade and accent are right for the high-frequency stems: *h₁éḱwos*, *deywós*, *wĺ̥kʷos* (Ved. *vŕ̥ka-*), *wiHrós* (Ved. *vīrá-*), *h₂éǵros* (Ringe p. 48), *kʷékʷlos* (see note), *ḱlutós*, *swós*, *moysós*, *yemHós*, *ǵʰoysós*, *snusós* (f., Fortson §6.44; lexicon gender f drives agreement). Check (c) found one doubtful item (*ksurós*, Gk *ξυρόν*; unused).

**Defect 3, *Hroth₂ós* 'chariot' (21 tokens).** M&A reconstruct root-accented *róth₂os* (ch. on the wheeled vehicle). Ved. *rátha-* is root-accented, and the project's own override note cites *rátha-*. Wiktionary's adjective table *Hroth₂ó* is the agentive *tomós* type ('runner'), but the lexeme is glossed and used as the noun. Fortson §6.72 describes substantivization with accent retraction (*kr̥ṣṇá-* → *kŕ̥ṣṇa-*). Handbooks vs Wiktionary disagree; for the noun sense, follow the handbook.

```json
{"id": "pie-lex-Hroth2os", "meaning": ["chariot, wheeled vehicle (lit. 'runner')"], "spec": {"m_strong": "Hróth₂o"}, "spec_checked": true, "note": "Ved. rátha- (root accent), M&A *róth₂os; Wiktionary's oxytone Hroth₂ó- is the agentive adjective 'running' (Fortson §6.72: the substantive retracts the accent). Engine sweep, thematic.md defect 3; keeps the earlier NIL re-review R5 note: Av. raθa-, Lat. rota, OIr. roth"}
```

(This line replaces the existing `pie-lex-Hroth2os` line in overrides.jsonl, keeping its meaning.)

**Defect 4, *dʰubʰrós* 'deep' (16 tokens: *dʰubróm* 9, *dʰubróy* 3, ...).** The Wiktionary template arg is `dʰubró`, so every cell lacks the aspirate. The headword, the root (*dʰewbʰ-*; Lith. *dubùs*, Goth. *diups*) and the shape rule all give *dʰubʰró-*. Only this one table is wrong.

```json
{"id": "pie-lex-dhubhros", "spec": {"m_strong": "dʰubʰró"}, "spec_checked": true, "note": "Wiktionary's table arg dʰubró drops the root aspirate of *dʰewbʰ- (headword dʰubʰrós; PGmc *dubraz, Lith. dubùs): engine sweep, thematic.md defect 4"}
```

**Defect 8, *súHros* 'sour' (4 tokens).** The headword is root-accented and the table oxytone. The Balto-Slavic acute root (*sū́ˀras*, Lith. *sū́ras*) agrees with the headword. Low confidence; I propose the headword.

```json
{"id": "pie-lex-suHros", "spec": {"m_strong": "súHro"}, "note": "table arg suHró disagrees with the headword súHros; PBS *sū́ˀras has root stress: engine sweep, thematic.md defect 8 (low confidence)"}
```

**Note, *kʷékʷlos* 'wheel' (182 tokens, not changed).** M&A write neuter oxytone *kʷekʷlóm* (Ved. *cakrá-* n.). Fortson §6.63 gives the stem *kʷe-kʷl-o-* without gender or accent. Wiktionary has masculine root-accented *kʷékʷlos* (Gk *κύκλος* m.). Books disagree. Keep Wiktionary unless the integrator wants M&A.

### Defect 5: lemma prepended to a table paradigm (mixed paradigms)

`Lexicon.cells` (realize.py, the `rule == "table"` branch) puts the headword first in NOM.SG (and ACC/VOC.SG for neuters) whenever it is not among the engine's NOM.SG forms. The patch is meant for athematic citation forms (*gʷḗn* vs the table's *gʷénh₂s*). For a thematic stem, though, the headword is by construction stem + *-s/-m*, so any difference is a table/headword inconsistency, and the patch turns it into a paradigm with two stems:

| Lexeme | Headword (NOM/ACC/VOC) | Oblique from table | Corpus |
|---|---|---|---|
| silver | *h₂ŕ̥ǵn̥tom* | *h₂r̥ǵn̥tósyo* | ACC 11 + NOM 2 *h₂ŕ̥ǵn̥tom*, GEN 1 *h₂r̥ǵn̥tósyo* |
| washbasin | *lówh₃trom* (2nd table) | *léwh₃trosyo* (1st table) | ACC 1 |
| lifetime | *sh₂éytlom* | *sh₂eytlosyo* (unaccented) | NOM 1 + ACC 5 |

`compound.py` `_determinative` repeats the patch for heads.

Silver: Beekes (§ on metals, p. 63) cites Skt. *rajatám*, Adams (Toch. B *ñkante*) reconstructs oxytone *h₂r̥nǵ-tóm* "as in Sanskrit *rajatám*". So the table's oxytone wins. M&A write *h₂erĝ-n̥t-om* without accent. Washbasin: keep the headword's o-grade (Wiktionary has both tables; Lat. *lavābrum*). Lifetime: the table simply lacks the accent.

```diff
--- a/pie/realize.py
+++ b/pie/realize.py
@@ def cells(self, lex_id: str, gender: str | None = None) -> dict:
             if fam == "noun":
-                c = decline(NounSpec(**sp), "handbook")
+                ns = NounSpec(**sp)
+                c = decline(ns, "handbook")
                 # the headword is the attested citation form (gʷḗn, not the table's gʷénh₂s)
                 lemma = self.entries[lex_id]["form"]
-                if not lemma.endswith("-") and lemma not in c.get("NOM.SG", []) and r.get("rule") == "table":
+                # not for o-stems: their headword is stem + -s/-m, so a mismatch is a table error
+                # (h₂ŕ̥ǵn̥tom vs table h₂r̥ǵn̥tó-), fixed by a spec override, never by mixing two stems
+                if not lemma.endswith("-") and lemma not in c.get("NOM.SG", []) and r.get("rule") == "table" \
+                        and ns.kind != "thematic":
```

and the same `kind != "thematic"` condition in `compound.py` `_determinative` (on `NounSpec(**r["spec"]).kind`). Overrides:

```json
{"id": "pie-lex-h2rgjntom", "spec": {"strong": "h₂r̥ǵn̥tó"}, "spec_checked": true, "note": "oxytone as Wiktionary's table and Skt. rajatám (Beekes, metals; Adams Toch. B ñkante *h₂r̥nǵtóm); the root-accented headword had been mixed into NOM/ACC only: engine sweep, thematic.md defect 5"}
{"id": "pie-lex-lowh3trom", "spec": {"strong": "lówh₃tro"}, "spec_checked": true, "note": "headword's o-grade (Wiktionary's second table; Lat. lavābrum); the first table léwh₃tro- had been mixed into the oblique: engine sweep, thematic.md defect 5"}
{"id": "pie-lex-sh2eytlom", "spec": {"strong": "sh₂éytlo"}, "spec_checked": true, "note": "Wiktionary's table arg lacks the accent of the headword sh₂éytlom: engine sweep, thematic.md defect 5"}
```

Tests:

```python
def test_thematic_table_paradigm_has_one_stem():
    lx = Lexicon.load()
    c = lx.cells("pie-lex-h2rgjntom")
    assert c["NOM.SG"][0] == "h₂r̥ǵn̥tóm" and c["GEN.SG"][0] == "h₂r̥ǵn̥tósyo"
    c = lx.cells("pie-lex-lowh3trom")
    assert c["NOM.SG"][0] == "lówh₃trom" and c["GEN.SG"][0] == "lówh₃trosyo"
    assert lx.cells("pie-lex-sh2eytlom")["GEN.SG"][0] == "sh₂éytlosyo"

def test_athematic_headword_still_prepended():
    assert Lexicon.load().cells("pie-lex-gwexn")["NOM.SG"][0] == "gʷḗn"    # athematic table, headword kept
```

### Defect 1: boukólos before unaccented *u* (*pérkʷunos*)

`morph.render` always calls `phon.delabialize`, which uses Wiktionary's scope: after consonantal *w*, before consonantal *w*, and before **unaccented syllabic *u***. The last clause turns the headword *pérkʷunos* into *pérkunos* (NOM 32, VOC *pérkune* 14, ACC 2, DAT 1 = 49 tokens), and *gʷutós*, *gʷʰutós*, *gʷuHnós*, *gʷuHtHós*, *pekʷwós* into *g-/k-* forms (unused). The corpus spells the storm god differently from his own headword.

Books: Fortson §3.39 states the rule as a labiovelar next to *u* (either side). Byrd (Handbook v3 ch. 121, rule Λ) writes it as */kʷ/ → [−round] / u__*, after *u* only. Beekes (p. 87) gives the Greek *boukólos* type as *k* after *u*. M&A write *perkʷunos* (7 times). So no book applies the rule before *u* in a reconstruction, and the Wiktionary headword itself keeps *kʷ*. Recommendation: the handbook convention keeps the labiovelar before syllabic *u* and puts the delabialized form second. The Wiktionary convention keeps its full scope, which the crosscheck depends on (*ḱm̥tógus* table).

```diff
--- a/pie/phon.py
+++ b/pie/phon.py
-def delabialize(segs: list[Seg]) -> list[Seg]:
+def delabialize(segs: list[Seg], before_u: bool = True) -> list[Seg]:
     """Boukólos rule as Wiktionary's module applies it: ...
-    kept after u (lúkʷos) and before accented ú (pr̥kʷúmos). Applied to whole forms."""
+    kept after u (lúkʷos) and before accented ú (pr̥kʷúmos). Applied to whole forms.
+    before_u=False drops the before-syllabic-u clause (handbook: M&A *perkʷunos)."""
     out = list(segs)
     for i, x in enumerate(out):
         if x.base in _LABIOVELAR:
             prev_w = i > 0 and out[i - 1].base == "w" and not out[i - 1].syl
             nxt = out[i + 1] if i + 1 < len(out) else None
-            next_w = nxt is not None and nxt.base == "w" and (not nxt.syl or not nxt.acc)
+            next_w = nxt is not None and nxt.base == "w" and (not nxt.syl or (before_u and not nxt.acc))
--- a/pie/morph.py
+++ b/pie/morph.py
@@ def _thematic(spec: NounSpec, conv: str) -> Cells:
-            forms.append(render(base + es))
+            segs = base + es
+            if conv == "handbook":     # labiovelar kept before syllabic u (M&A *perkʷunos); Wiktionary's form second
+                forms += [_render(delabialize(segs, before_u=False)), render(segs)]
+            else:
+                forms.append(render(segs))
         out[feat] = _uniq(forms)
```

(The VOC.SG line in `_thematic` uses `render` too and needs the same treatment.) A shared `render(segs, conv)` would carry this to the other families, which the integrator may prefer. Test:

```python
def test_handbook_keeps_labiovelar_before_u():
    c = decline(NounSpec("pérkʷuno"), "handbook")
    assert c["NOM.SG"][0] == "pérkʷunos" and "pérkunos" in c["NOM.SG"]
    assert decline(NounSpec("pérkʷuno"), "wiktionary", alternatives=False)["NOM.SG"] == ["pérkunos"]
```

### Thematic adjectives: three genders

`AdjSpec.genders` derives f. *-eh₂* by replacing the thematic vowel and keeping its accent (*néwos/néweh₂/néwom*; *ḱlutós/ḱlutéh₂/ḱlutóm*). That matches L&Y §2.1.3 (Ved. *návas, návā, navam*; Gk *né(w)os, né(w)ā, né(w)on*), Ringe 2.3.5 (feminine suffix *-h₂-* for o-stems) and Fortson §6.70. Masculine and neuter oblique cells are identical, as in Ringe. *-yo-* adjectives also take *-yeh₂* (*diwyéh₂*, Ved. *divyā́*): right. Feminine o-stem nouns (*snusós*) take feminine adjective agreement through `Lexicon.gender`: right (L&Y §2.1.3 on Gk *hodós* f.).

*-tó-* and *-nó-* adjectives are oxytone with a zero-grade root where Wiktionary has one (Fortson §5.61, §6.77; L&Y §3 on *-nó-* as inherently accented). The full-grade ones (*h₃reǵtós*, *kaptós*, *pleh₁tós*, *pokʷtós*, *sedtós*, ...) are Wiktionary headwords, not engine errors. Root-final voiced stop before *-t-* is written unassimilated (*yugtós*, Fortson §3.36 *yuk-tó-*). That is a project notation convention: the validator equates the two.

*-yo-* adjectives are written *-yo-* after a heavy syllable (*médʰyos*). Fortson §6.74 notes Sievers' *-iyo-*. Notation convention (the meter syllabifier has a Sievers flag), not a paradigm defect.

The feminine dual and vocative come from the eh₂ declension (defect 13). L&Y ch. 122 (numerals) give f. 'two' *d(u)weh₂-ih₁*, and the Greek chapter of Handbook v1 derives Myc. *-a-e* from PIE *-eh₂-ih₁*. The engine has *-eh₂h₁*. Fortson §6.70 gives the eh₂ vocative as *-a* with retracted accent (Ringe *dʰoHn[á]*). The engine has the nominative *-eh₂* with retraction. No corpus token of this family hits either (adjective NOM/ACC.DU tokens are all masculine or neuter), so I leave the patch to the eh₂ auditor.

**Defect 10, adjectives and pronominals as masculine nouns.** Lexemes without `pos` default to the thematic-noun rule, so these adjective lexemes cannot agree in gender: *mr̥wós* 'dead', *h₁rudʰyos* 'red', *wēdos* 'wet', *ḱuh₁rós* 'strong', *ḱéywos* 'dear' (Ved. *śéva-* adj.), *dʰegʷʰrós* 'burning', *dʰr̥ǵʰtós* 'firm', *sḿ̥teros* 'one of two' (Gk *ἕτερος*), *h₂élyos* 'other'. Most corpus uses are substantival masculine, which is fine. Two mis-agreements are attested: *méh₂tēr mr̥wós h₁ésti* ('mother is dead', should be *mr̥wéh₂*) and *gʷʰéros ... h₁rudʰyos* (neuter subject). Fix: overrides with `"pos": "adj"` (the shape rule then builds an `AdjSpec`), e.g.

```json
{"id": "pie-lex-mrwos", "pos": "adj", "note": "adjective 'dead' (Ved. mṛtá-type o-stem adj.), was a masculine noun and could not agree with méh₂tēr: engine sweep, thematic.md defect 10"}
{"id": "pie-lex-kjeywos", "pos": "adj", "note": "Ved. śéva- adj. 'dear'; substantival use stays masculine: engine sweep, thematic.md defect 10"}
```

(and the same for *h₁rudʰyos*, *wēdos*, *ḱuh₁rós*, *dʰegʷʰrós*, *dʰr̥ǵʰtós*, *sḿ̥teros*). *h₂élyos* is a pronominal adjective (Fortson §7.14: Lat. *aliud*, Gk *ἄλλο*), so its neuter and some oblique cells take pronominal endings (*-od*, NOM.PL *-oy*, DAT.SG *-osmōy*). No book prints its paradigm. A closed-class entry modelled on `demonstrative_so` would be the clean fix (the corpus has 2 DAT.SG *h₂élyōy* that would become *h₂élyosmōy*). Note only.

### Compounds (thematic second members)

Six of the corpus compounds have a thematic second member: determinatives *wesowiHrós*, *neh₂uwiHrós* (VOC *néh₂uwiHre*), *h₂r̥tḱogʷʰonóm*, *wl̥kʷogʷʰonóm*; bahuvrihis *h₁suh₁éḱwos*, *HeHḱuh₁éḱwos*. Right:
- Determinative heads keep their accent behind a deaccented first member (Ved. *rāja-putrá-*).
- Agentive *-gʷʰonós* is of the *tomós* type, frequent as a final member (Fortson §6.59).
- The bahuvrihi inflects as a thematic adjective with f. *-eh₂*.
- The compound vocative retracts to the first syllable of the whole word, consistent with the simplex.

Accent of su-/dus- bahuvrihis on the second member: consistent with Vedic *su-vī́ra-*. I found no defect; the compound auditor owns the BAP logic.

### Defect 6: unaccented stems in the corpus (66 tokens)

352 masculine thematic nouns, 3 neuters and 9 adjectives have no accent. `make_slice` now gates on an accented headword, but 66 tokens from pilot (8), pilot2 (4), b001 (33) and b002 (15) predate the gate: *werdʰom* 9, *dinos* 7, *sh₂éytlom* 6 (table, defect 5), *srowmos* 6, *ḱerh₂wos* 6, *h₁eh₂nos* 6, *wēdos* 4, *ǵʰleystos* 4, *h₂eysos* 4, *h₁rudʰyos* 3, *wekʷsperos* 3, *deynos* 2, *gurnos* 2, *ǵʰeh₁ros* 1, *waylos* 1, *gewlos* 1, *sterḱos* 1. Fix: regenerate or drop those records. Where the daughters give the accent, an override makes the lexeme usable again:

```json
{"id": "pie-lex-dinos", "spec": {"strong": "dinó"}, "note": "oxytone: Ved. diná-, PIIr *dinám (as given in the lexicon's reflexes); headword unaccented: engine sweep, thematic.md defect 6"}
{"id": "pie-lex-wekwsperos", "spec": {"strong": "wékʷspero"}, "note": "root accent: Gk ἕσπερος, PBS *wékeras; headword unaccented: engine sweep, thematic.md defect 6"}
```

With a shape spec, `spec.strong` sets every cell. The planner gate still reads the headword, so these stay out of slices unless `make_slice.accented` also accepts an accented spec.

### Defect 7: neuter s-stems routed to the thematic masculine

`classify.by_shape` sends a *-os* noun to the s-stem neuter only with gender n, an *-es-* stem, or a Sanskrit *-as* / Greek *-εα* reflex. Greek neuters in *-ος* (gen. *-εος*), Latin neuters in *-us, -eris/-oris* and Avestan *-ah-* neuters slip through as masculine o-stems (ACC *-om*, NOM.PL *-ōs*). In the corpus: *ḱéh₂dos* 'hatred' (6 NOM.SG; Gk *κῆδος* n., Goth. *hatis* n.) and *sterḱos* 'dung' (1; Lat. *stercus, -oris* n.). Unused but usable, with an s-stem reflex in the lexicon: *dʰérsos* (Gk *θάρσος*), *gʷélHos* (Gk *βέλος*), *h₃néydos* (Gk *ὄνειδος*), *stégos* (Gk *στέγος*), *wébʰos* (Gk *ὕφος*), *h₁éyǵʰos* (Av. *aēzah-*), *kénh₂os* (PIIr *čánHas*), *témpos* (PItal. *tempos*, Lat. *tempus, -oris*). Overrides in the existing s-stem spec format (`shape:s-stem-neuter`: strong = headword, weak = stem + *es*, acrostatic, n):

```json
{"id": "pie-lex-kjeh2dos", "gender": "n", "spec": {"strong": "ḱéh₂dos", "weak": "ḱéh₂des", "accent_class": "acrostatic", "gender": "n"}, "spec_checked": true, "note": "neuter s-stem: Gk κῆδος, -εος n., Goth. hatis n.; was a thematic masculine: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-sterkjos", "gender": "n", "spec": {"strong": "sterḱos", "weak": "sterḱes", "accent_class": "acrostatic", "gender": "n"}, "note": "neuter s-stem: Lat. stercus, -oris n.; headword unaccented, so it stays out of slices: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-dhersos", "gender": "n", "note": "neuter s-stem: Gk θάρσος n. (by_shape then routes it to shape:s-stem-neuter): engine sweep, thematic.md defect 7"}
{"id": "pie-lex-gwelHos", "gender": "n", "note": "neuter s-stem: Gk βέλος n.: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-h3neydos", "gender": "n", "note": "neuter s-stem: Gk ὄνειδος n.: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-stegos", "gender": "n", "note": "neuter s-stem: Gk στέγος n.: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-webhos", "gender": "n", "note": "neuter s-stem: Gk ὕφος n.: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-h1eygjhos", "gender": "n", "note": "neuter s-stem: Av. aēzah- n.: engine sweep, thematic.md defect 7"}
{"id": "pie-lex-kenh2os", "gender": "n", "note": "neuter s-stem: PIIr *čánHas (Ved. cánas- n.): engine sweep, thematic.md defect 7"}
{"id": "pie-lex-tempos", "gender": "n", "note": "neuter s-stem: Lat. tempus, -oris n.: engine sweep, thematic.md defect 7"}
```

(`gender: n` alone suffices for a shape lexeme, because `by_shape` routes *-os* + g = n to the s-stem rule.) The general heuristic, root-accented e-grade CéC-os = s-stem, is not safe: *séntos* 'path' (Goth. *sinþs* m.) and *h₁yégos* (deliberately m.) are thematic. So I propose only the reflex-backed overrides, plus a classifier check that Greek *-ος* reflexes of a barytone e-grade lemma raise a review flag. Test:

```python
def test_kjeh2dos_is_s_stem():
    c = Lexicon.load().cells("pie-lex-kjeh2dos")
    assert c["ACC.SG"][0] == "ḱéh₂dos" and c["GEN.SG"][0].startswith("ḱéh₂des")
```

### Defects 11–12: pronouns and numerals declined as nominal o-stems

*Hyós* (relative), *kʷos* (interrogative) and *h₁énos* (distal) are usable as `shape:thematic` masculine nouns, because `spec_from_template` skips `ine-decl-pron`. Their nominal endings are wrong for pronouns (NOM.PL *-ōs* for *-oy*, DAT.SG *-ōy* for *-osmōy*; Fortson §7.9–12), and the closed classes already have them (`relative_yo`, `interrogative_kwo`, `deictic_eno`). 0 corpus tokens. Blocklist lines (data/generation/blocklist.jsonl):

```json
{"lex_id": "pie-lex-Hyos", "reason": "relative pronoun declined as a thematic noun (nominal NOM.PL -ōs, DAT.SG -ōy); use closed:relative_yo (engine sweep, thematic.md defect 11)"}
{"lex_id": "pie-lex-kwos", "reason": "interrogative pronoun declined as a thematic noun; use closed:interrogative_kwo (engine sweep, thematic.md defect 11)"}
{"lex_id": "pie-lex-h1enos", "reason": "distal pronoun declined as a thematic noun; use closed:deictic_eno (engine sweep, thematic.md defect 11)"}
```

*dwóh₁* 'two' and *bʰóh₁* 'both' have a one-arg adjective table, so they get full singular and plural cells (*dwós*, *dwósyo*, *dwṓs*) and a feminine dual *dwéh₂h₁*. L&Y ch. 122 give f. *d(u)weh₂-ih₁* and n. *dwo-ih₁*. The 2 corpus tokens (*bʰóh₁* NOM/ACC.DU m.) are right. Block *dwóh₁* (duplicate of `closed:numerals/2`). For *bʰóh₁*, either add a closed-class dual-only entry or leave it, since realize only asks for DU cells of a numeral.

```json
{"lex_id": "pie-lex-dwoh1", "reason": "duplicate of closed:numerals/2; the adjective table generates singular/plural cells and f. dual dwéh₂h₁ for *dweh₂ih₁ (L&Y ch. 122): engine sweep, thematic.md defect 12"}
```

## Gating: 282 neuter o-stems unusable for no paradigm reason

`scripts/classify_lexicon.py` backtests each shape rule against the engine cells of the table spec and gates at 0.85. `shape:thematic-neuter` scores 0.8125 (13 of 16 tables exact). The 3 failing tables are exactly silver, washbasin and lifetime: tables whose arg disagrees with their own headword (defect 5). The shape rule built from the headword is right; the table is the odd one out. `shape:thematic` (0.868) loses 10 tables the same way: ordinals and possessives (*tritós*, *penkʷtós*, *twós*, ...) that Wiktionary tables as adjectives while the shape rule, lacking `pos`, makes them nouns (0/19 cells by family mismatch). That is a part-of-speech question, not a paradigm error.

Proposed change (scripts/classify_lexicon.py `compare`): skip a table whose own NOM.SG (from its spec) does not contain the headword, since that measures Wiktionary's inconsistency, not the rule. Then compare an adjective table with a noun shape on the masculine or neuter cells. With that, `shape:thematic-neuter` reaches 13/13 and the 282 neuters become usable (160 accented; with glosses, perhaps 40–100 reach slices).

```diff
--- a/scripts/classify_lexicon.py
+++ b/scripts/classify_lexicon.py
@@ def compare(family, spec, para):
     tfam, tspec = got
     try:
         want = cells_for(tfam, tspec)
     except Exception:
         return 0, 0
+    # an o-stem table that disagrees with its own headword (h₂ŕ̥ǵn̥tom vs table h₂r̥ǵn̥tó-) tests
+    # Wiktionary, not the rule; athematic tables keep their citation-form mismatch (gʷḗn vs gʷénh₂s)
+    thematic = (tfam == "noun" and tspec.kind == "thematic") or (tfam == "adj" and tspec.m_weak is None)
+    if thematic and para.get("form") and para["form"] not in want.get("NOM.SG", []):
+        return 0, 0
```

(`cells_for` returns flat cells, adjectives with their three genders unioned, so NOM.SG holds the masculine headword.) Test: after `uv run python -I scripts/classify_lexicon.py`, `classify_report.json` has `backtest["shape:thematic-neuter"]["cell_accuracy"] == 1.0`.

## Convention questions (books disagree; not counted as defects)

1. **GEN.PL *-ōm*** (39 tokens). Fortson §6.56 argues for *-o-Hom* over the traditional *-ōm*. Ringe prints *-ooHom*, L&Y *-oh₁/₃om*, Beekes and M&A short *-om*. No book prints *-ōm* as its reconstruction, though Tier 1 authors Danka, Voyles and Lehmann write it. The handbook convention lists it deliberately and the measurement chose it; keep it, but correct the attribution in the `morph.py` header. If the convention is ever re-measured, *-oHom* is the Fortson/Ringe/L&Y form.
2. **DAT/ABL.PL *-oybʰos*** (58 tokens, all *-óybʰos/-oybʰos*). L&Y say thematic vowel + *-bʰos* (Ven. *louderobos*), with the *-oi-* stem "less likely at the PIE stage". Fortson §6.57 calls *-oi-bʰ-* an Indo-Iranian pattern; Beekes has *-omus*, Ringe *-o(y)mos*, M&A *-oibʰ(y)os/-omus*. Among Tier 1 authors, *-obʰos* (Danka, Lühr) has more support than *-oybʰ(y)os* (Byrd), and *-obʰos* is now only a Wiktionary-side alternative. Recommendation for the integrator: handbook primary *-obʰos*, then *-oybʰos*, *-omos*, *-oybʰyos*. One line in `_THEMATIC["handbook"]`, and every form stays in the cell.
3. **Oxytone vocative** (95 VOC.SG tokens of oxytones). Fortson retracts (*déywe*); Ringe does not (*nisdé*). The engine follows Fortson with Ringe as the alternative. Keep.
4. **LOC.SG *-oy*** vs Ringe *-ey*. Fortson §6.47 has *-oi* with *-ei* a variant. Keep.
5. **Uncontracted (Ringe) vs contracted (Fortson, Beekes, L&Y, M&A)** NOM.PL/DAT/ABL.SG: the contracted forms are the majority; keep. The docstring should not cite Ringe for them.
6. ***kʷékʷlos*** m. (Wiktionary, Gk *κύκλος*) vs M&A *kʷekʷlóm* n. (Ved. *cakrá-*), 182 tokens. Keep Wiktionary.

## Corpus counts used above

Counted from `corpus/tier3/*.jsonl` (27 files) by lex_id + features, with the realized forms checked. Family total 4,630 tokens; per defect: pérkʷunos 49; VOC.PL/DU of non-initial-accent stems 42; Hroth₂ós 21; dʰubʰrós 16; silver 14 (+ sh₂éytlom 6, lówh₃trom 1, whose surface forms are already the target); unaccented 66 (incl. sh₂éytlom); s-stem misroutes 7; súHros 4; neuter dual 4; mis-agreement 2; GEN.PL 39 and DAT/ABL.PL 58 (convention).
