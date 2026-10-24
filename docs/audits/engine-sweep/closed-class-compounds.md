# Engine sweep: closed class and compounds

Scope: `data/morph/closed_class.json` (personal pronouns and enclitics, *so/seh₂/tod*, anaphoric *h₁e-/h₁i-*, deictics *ḱo-* and *h₁eno-*, relative *h₁yo-*, *kʷi-/kʷo-*, numerals 2–4 declined and 5–1000 indeclinable, particles); the lexicon's numeral lexemes (*h₁óynos*, *sḗm*, *dwóh₁*, *tréyes*, *kʷetwóres*); `pie/compound.py`; and the agreement and clitic rules in `pie/realize.py` that use these words.

Method: I compared every closed-class cell (first form = handbook convention) with Ringe 2017 §2.3.6 (book pp. 52–57 = `raw/books/text/ringe/p0063–p0068`), Fortson 2010 §§7.1–7.29 and §§8.11, 8.16, 8.24–8.27, Beekes 2011 §15.2.1 (pp. 228–229), and Lundquist & Yates (Handbook ch. 122, §§2.2.2–2.3.1, §3.1). I checked the tables mechanically for internal consistency: masc. = neut. in the obliques, dat. pl. = abl. pl., an accent on every stressed form. All 1,299 usable noun heads that a compound accepts went through the determinative builder, and the vocalic-onset heads through the bahuvrihi builder. All 12,867 clauses of `corpus/tier3/*.jsonl` (2,115 records, 13,442 closed-class tokens, 28 compound tokens) were re-realized from their stored plans with the current engine and with the patched engine. The patched engine is in my scratch copy. Its full `tests/test_realize.py` and `tests/test_validate.py` pass, as do the 8 new tests below; all 8 fail on the current engine. The corpus counts below are tokens in the corpus as it stands.

**Result: 20 defects** (6 in the closed-class data, 3 in the lexicon numerals, 9 in realize.py, 2 in compound.py), plus notes where the handbooks disagree or a convention is in play. With all fixes applied, 203 of the 12,867 clauses change.

## Ranked fixes

| # | defect | where | corpus tokens | fix |
|---|---|---|---|---|
| C1 | 1sg nom. primary *h₁eǵ* has no accent (every other stressed pronoun form has one) and matches neither book: Ringe p. 57 *éǵh₂*, Fortson §7.4 *eǵoh₂* | closed_class | **82** | primary *h₁éǵh₂* (Ringe plus the table's initial-h₁ convention, as anaphoric *h₁éy* < Ringe *éy*); old forms kept as alternatives |
| R3 | stressed 1/2 pl. gen. falls back to the enclitic *nos/wos* but is labelled `GEN.PL` (not `.ENCL`), and is moved to Wackernagel position only because its form happens to be in a string list | realize.py | **68** (label only; form unchanged) | `_closed_feat` relabels the fallback `GEN.PL.ENCL`; clitic = feature `.ENCL` |
| C2 | 'ten' primary *déḱm̥t* matches neither handbook: Fortson §7.17 *dék̑m̥*, Ringe p. 54 *déḱm̥d*; the lexicon's own pie-lex-dekjm is *déḱm̥* | closed_class | **55** | `["déḱm̥", "déḱm̥t", "déḱm̥d"]` |
| R1 | phrase-level *-kʷe* is put after the conjunct's **head** (last word): *tósyo ǵm̥rós-kʷe*, *dwóh₁ h₁éḱwoh₁-kʷe*. Fortson §7.27 and §8.24 put it after the **first word** of the conjunct, whether that is a word or a phrase (Lat. *silua alta Iouis lūcusue Diānae*) | realize.py | **29** | `and_host` = first non-clitic word of the conjunct's phrase |
| C4 | the pronoun tables break masc. = neut. in the obliques and dat. pl. = abl. pl. (the neuter and fem. abl. cells added later from Ringe got Ringe's *-mos/-soHom/-smey* first, while the masculine kept *-bʰos/-sōm*). *kʷo-* and *h₁yo-* masc. dat. sg. *-smōy* and *kʷo-* gen./loc. *kʷés-* don't follow the demonstrative, which Ringe p. 55 and L&Y §2.2.3 say they inflect like | closed_class | **17** (*h₁yósmōy* 7, *kʷésmōy* 4, *kʷésyo* (kʷo-) 4, *kʷósmey* 1, *téh₂mos* 1) | edit script below |
| R5 | conjoined vocatives: Fortson §8.11 (Ved. *vā́yav índraś ca*, Il. 3.277) puts the conjunct that carries *-kʷe* in the **nominative**; the engine gives *ph₂ter méh₂ter-kʷe*, *dyéw dʰéǵʰom-kʷe* | realize.py | **11** (in 2-member vocative pairs) | case NOM for the *-kʷe* conjunct of a 2-member VOC pair |
| R4 | conjoined subjects: the verb agrees with the **first** subject only (*h₂éwsterom móri-kʷe h₁rudʰéh₁ti*, *h₁eǵ … bʰréh₂tēr-kʷe kʷḱyéh₁m̥*). Fortson §8.16: subject and verb agree in number. Two neuter plurals stay singular (Fortson's own example, Il. 2.468 *phúlla kaì ánthea gígnetai*) | realize.py | **8** verb tokens | group agreement: 2 SG → DU, otherwise PL; lowest person; DU→PL fallback when a stem has no dual (perfect) |
| R8 | two possessive enclitics of the same form are stacked: *h₂óweyes moy moy h₁éḱwōs-kʷe* | realize.py | **3** redundant tokens (t002-00025, t002-00026, t020-00020) | drop a repeated identical clitic from the Wackernagel cluster |
| R2 | dual enclitics *noh₃*, *woh₃* are missing from `ENCLITIC_PRONOUNS`, so they stay in phrase position: *tósyo bʰréh₂tēr woh₃ lémbʰt* | realize.py | **4** (3 misplaced) | add them; clitic by feature |
| C3 | fem. 'three' acc. pl. primary *tisrn̥s* has no accent while nom. is *tísres* (Ringe p. 53 prints both without an accent and marks the accent doubtful) | closed_class | **2** | `["tísrn̥s", "tisrn̥s", "tísr̥ms"]` |
| L1 | the lexicon numeral adjectives are usable and decline as ordinary adjectives: pie-lex-dwoh1 gives sg. *dwós*, pl. *dwṓs*, f. *dwéh₂h₁*; pie-lex-kwetwores gives sg. *kʷetwṓr*, neut. pl. *kʷetwṓ* (Ringe p. 54 *kʷetwṓr*). They also bypass the numeral rule that fixes the head's number. pie-lex-treyes is already blocked for the same reason | blocklist | **2** (*kʷetwóres*, right form, but no head-number rule) | block them (lines below) |
| L2 | pie-lex-sexm *sḗm*: fem. *sih₂*, *sih₂m̥* drops the *m* (Ringe p. 52 *sémih₂*, *sémih₂m̥*; Fortson §7.16 and L&Y §2.3.1 *sm-ih₂*, Gk *mía*), and the adjective module builds a plural for 'one' | blocklist | 0 | block until hand-tabled (cells are in Ringe p. 52) |
| R6 | Wackernagel clitics are put after word 1 even when word 1 carries its own *-kʷe*: *gʷṓs te toy-kʷe* ('you and your cattle'). Fortson §8.25: sentential clitics come after the first stressed word **and any connective clitic attached to it** | realize.py | **1** | insert after word 1 and its *-kʷe/-wē* |
| R7 | indeclinable numerals (5–1000) don't fix their head's number (only 2/3/4 do): *septḿ̥ h₁éḱwos* comes out singular if the plan leaves `num` unset | realize.py | 0 (planners set PL every time; latent) | `"indeclinable": "PL"` |
| C5 | numerals 2–4 have no VOC cells (Ringe prints "n.-v."), so a numeral modifying a vocative is a KeyError | closed_class | 0 (plans rejected) | VOC = NOM |
| C6 | *kʷi-* neut. has NOM.PL *kʷíh₂* but no ACC.PL, so 'what (things)' as an object is a KeyError | closed_class | 0 | ACC.PL *kʷíh₂* |
| P1 | lexical first members (thematic *-o-*, *-u-*) before a 2nd member with a vocalic onset are accepted and give hiatus forms (*newoúderos*, *néwoimyos*, *newon̥bʰrós*: 21 heads). The same junction is rejected for the prefixes, since no book gives a junction rule | compound.py | 0 | reject, as for prefixes |
| P2 | the numeral lexeme pie-lex-dwoh1 as a first member gives accented *dwó-* (*dwóḱlewēs*), not *dwi-* (Fortson §7.18; L&Y §2.3.1). The lexicon's affix pie-lex-sm *sm̥-* is not aliased to closed:prefix/sm and fails as "not inflectable" | compound.py | 0 | aliases |
| L3 | 'one' *h₁óynos* declines as a plain thematic adjective (dat. *h₁óynōy*, gen. pl. *h₁óynōm*). Ringe p. 55 counts 'one' among the quantifiers with pronominal inflection (cf. Lat. *ūnīus*, *ūnī*) | lexicon | 0 (only NOM/ACC in the corpus, identical either way) | low; see notes |
| R9 | `-kʷe` on an enclitic-pronoun conjunct is dropped (the clitic leaves its phrase, the particle goes with it) | realize.py | 0 | not patched; planner guidance: a conjunct with *-kʷe* must be stressed |

Stale corpus forms that are not engine defects: *kʷósmead*/*kʷosmead* (2 tokens). The engine now gives *-mōd* first; regenerating fixes them.

## 1. Personal pronouns (personal/1, /2, /refl)

**Right.** 1sg acc. *h₁mé* (Ringe *m̥(m)é*), enclitic *me*, gen. *méne* (Fortson §7.4; Ringe *méme* alt.), dat. *méǵʰye* (Ringe p. 57), enclitic dat./gen. *moy* (Fortson §7.7), nom. pl. *wéy* (Fortson *u̯ei*), obl. pl. stem *n̥s-mé-* (Fortson §7.4), enclitic *nos*; nom. du. *wé*, acc. du. *n̥h₃mé*, *noh₃* (Ringe). 2sg *túH* (Fortson §7.6 *tuH*; Ringe *túh₂*), *twé*, *te*, *téwe*, *toy*, *tébʰye*; 2pl *usmé* (Fortson; Ringe/Katz *uswé* alt.), *wos*; du. *yú*, *uh₃wé*, *woh₃*. Reflexive *swé*, *se*, *séwe*, *soy*, *sébʰye* exactly as Ringe p. 57, no nominative (Fortson §7.13). Accent: every stressed form except C1 has one; every enclitic has none.

**Wrong.** C1, R2, R3 (table above). R3 detail: the stressed 1/2 pl. genitive has no form in any book (Ringe "???", Fortson §7.4 gives only the stem), so the enclitic fallback is fine, but the token should say what it is.

**Gaps (no fix):** INS/LOC of the personal pronouns and the stressed obl. pl. are not reconstructible (Ringe "???"), so plans that ask for them are rejected, which is correct. Fortson §7.8: 'my/your' were more often possessive **adjectives** (*mei̯o-/moi̯o-*, *tewo-/two-*, *swo-*); the engine has *swós* in the lexicon but realizes 'my, your' as the genitive *méne/téwe/moy/toy*. That is attested usage (Ved. *máma*, *me*), but planners could be told about *swós*.

## 2. Demonstrative *so/seh₂/tod*, anaphoric *h₁e-/h₁i-*, deictics *ḱo-*, *h₁eno-*, relative *h₁yo-*

**Right.** *só séh₂ tód*, *tóm tā́m* (Ringe *téh₂m [tā́m]*), gen. *tósyo*, fem. *tósyeh₂s/-ey/-i* (Ringe p. 54), dat. *tósmey* (Ringe; Beekes p. 228 *tosmōi* alt.), loc. *tósmi*, abl. *tósmōd* and ins. *tóh₁* (Fortson-contracted, Ringe's *tósmead*, *tónoh₁* as alternatives, a documented t001 decision), nom. pl. *tóy*, *téh₂es*, *téh₂*, acc. *tóns*, ins. *tṓys*, loc. *tóysu*, gen. *tóysōm* (Fortson §7.9 *-sōm*), du. *tóh₁ / tóy*. Anaphoric: Ringe p. 56 cell for cell, with Beekes's initial *h₁* (p. 229); fem. ins. sg. and the dual are left out, as Ringe has "???". Relative: inflects like *so/tod* with nom. *h₁yós* (Ringe p. 55; L&Y §2.2.3). *ḱo-* and *h₁eno-* are derived from *so/tod* as documented.

**Wrong.** C4. Cell by cell, from a consistency script over the tables:

- demonstrative_so, deictic_ki, deictic_eno, relative_yo, interrogative_kwo: masc. dat./abl. pl. *-oybʰos* but neut. *-oymos*; masc. gen. pl. *-oysōm* but neut. *-oysoHom*; fem. dat. pl. *-eh₂bʰos* but fem. abl. pl. *-eh₂mos*.
- relative_yo: masc. dat. sg. *h₁yósmōy* vs neut. *h₁yósmey* (demonstrative *tósmey*); masc. ins. sg. *h₁yóh₁* vs neut. *h₁yónoh₁*.
- interrogative_kwo: masc. gen. *kʷésyo* / dat. *kʷésmōy* / loc. *kʷésmi* vs neut. *kʷósyo / kʷósmey / kʷósmi*. Ringe p. 56 has the adnominal *o*-stems inflect like the relative, i.e. like *so/tod*, so *kʷósyo, kʷósmey, kʷósmi*. Ins. *kʷónoh₁* vs the demonstrative's *tóh₁* convention.
- interrogative_kwi: mf dat. *kʷésmōy*, loc. *kʷésmi* vs n *kʷósmey*, *kʷósmi*; mf/n gen./dat./abl. pl. are mixed in the same way.
- numerals 3 and 4: masc. dat. pl. *tribʰós*, *kʷetwr̥bʰós* vs abl. pl. *trimós*, *kʷetwr̥mós* (Ringe prints one d.-abl. cell); neut. and fem. *-mós* only.

Direction chosen: keep each table's existing **masculine primary**, which follows the project's handbook convention ("*-bʰ-* first", contracted *-sōm*; morph.py header; diff.jsonl rows 137, 150, 200 accepted *-bʰos* via Fortson's general ending §6.14). Give the neuter and the abl. cells the same primary, with the Ringe form as the alternative. For *kʷi-* (the i/e-stem), the singular obliques go to e-grade like its gen. *kʷésyo* (Ringe pp. 56, 117) with *-smey* like *tósmey*. This changes only 17 corpus tokens. *Disagreement:* both pronoun-specific tables, Ringe p. 55 (*tóymos*) and Beekes p. 228 (*toimus*, anaphoric *h₁eimus* p. 229), have **-m-** in the pronominal dat. pl. The *-bʰos* primary rests only on Fortson's nominal ending. If the integrator prefers the books' pronoun tables, flip every pronominal and numeral dat./abl. pl. to *-mos* first (48 tokens of *tóybʰos*, 2 of *téh₂bʰos*). The script below has one line to change for that.

**Gaps (no fix):** fem. dual of every *o*-stem pronoun is absent (Ringe "???"), so "these two women" is rejected. L&Y §2.2.2 leave the oblique root grade open between *o* and *e*.

## 3. Interrogative/indefinite *kʷi-/kʷo-*

**Right.** *kʷís kʷíd*, *kʷím*, nom. pl. *kʷéyes* (i-stem), ins. *kʷíh₁* (Fortson §19.10 *kʷih₁*), gen. *kʷésyo* (Ringe p. 117); *kʷós kʷéh₂ kʷód*. Accented interrogative and unaccented enclitic indefinite *kʷis/kʷid* (Ringe p. 57; L&Y §2.2.4); interrogative phrases are fronted (Fortson §8.20, WH-movement); the indefinite clitic goes to Wackernagel position (*ne kʷis gʷémt*). **Wrong:** C4 (above), C6.

## 4. Numerals

**Right.** 2 = dual, masc. *dwóh₁*, neut. *dwóy(h₁)* (Ringe p. 53; Fortson §7.17); 3 *tréyes tríns tríh₂*, ins. *tribʰí*, loc. *trisú*, gen. *tr̥yóHom* (as Ringe prints it); fem. *tísres* (*-sr-*, Fortson §6.71, L&Y); 4 *kʷetwóres kʷetwórn̥s kʷetwṓr*, gen. *kʷeturóHom*, fem. *kʷétesres* (Ringe p. 54); 5 *pénkʷe*, 6 *swéḱs*, 7 *septḿ̥*, 8 *oḱtṓw*, 9 *h₁néwn̥*, 100 *ḱm̥tóm* (Ringe; Fortson §7.17). Realizer: 2 makes its head dual and 3/4 make it plural (t016 fix); numeral obliques keep the dual (only 2 has oblique dual cells, unsourced: *dwóyh₁s*, *dwóbʰih₁*, 0 tokens). Compound forms *dwi- tri- kʷetru-* (Fortson §7.18). 'one' is the lexicon adjective *h₁óynos* (Fortson §7.16 *oi-no-*).

**Wrong.** C2, C3, C5, R7, L1, L2, L3. *Disagreements (no change proposed):* 4 masc. nom. pl.: Fortson §7.17 *kʷétwores*, Ringe *kʷetwóres*, L&Y unaccented. The table follows Ringe, but docs/morphology.md (line 122) says Fortson's *kʷétwores* was put first. Fix the doc or the table (1 token); I recommend keeping Ringe, whose whole paradigm the table uses. 4 neut.: L&Y *kʷetworh₂* vs Ringe *kʷetwṓr* (the table's). 2 fem.: L&Y §2.3.1 *d(u)weh₂-ih₁*, Ringe "Central dialects" *dwéh₂ih₁*; the table uses the neuter *dwóyh₁* (Ved. *dvé* is fem./neut.). Adding *dwéh₂ih₁* as a fem. alternative is optional. 1000 *ǵʰéslom*: Ringe p. 54 says the higher numerals are not securely reconstructible; leave it, already flagged in `_refs` as weaker.

## 5. Particles and realizer agreement

**Right.** *-kʷe* 'and' and *-wē* 'or' are postpositive (Fortson §7.27); clause-level *-kʷe* goes after the first word of the clause, including *ne-kʷe* and *h₁yód-kʷe*; an earlier-only mark moves to the last conjunct (X Y-kʷe, Ved. *ágna índraś ca*); *nu* (Fortson §7.28); *-ge* after the first word (Fortson §7.29); Wackernagel enclitics after the first word (§8.25); neuter plural subject with a singular verb (Fortson §8.16); *mē* + augmentless (injunctive) form in prohibitions (Fortson §7.25, Beekes §17.2 *meh₁*, Beekes §18.8.2: Skt injunctive obligatory in prohibitions). Numeral head-number fix (t016).

**Wrong.** R1, R2, R3, R4, R5, R6, R7, R8 (table). R9: not patched.

**Convention note: *mē* with OPT and hortative SBJV.** Fortson §7.25 and Beekes §17.2 give *mē* only for prohibitions (with the injunctive). Handbook ch. 97 (Albanian syntax) §5.1 reconstructs a PIE contrast of *ne* with indicatives and *mē* with modal forms (Gk μή, Arm. *mi*, Skt *mā́*). The engine's rule (mē for IMP, OPT, and 1st-person SBJV; *ne* for 2nd/3rd-person SBJV) matches neither view. Under the Handbook view, 2nd/3rd-person SBJV should take *mē* too (54 clauses: SBJV with person 2, 3 or unset). Under the Fortson/Beekes view, OPT and SBJV should take *ne* (≈142 clauses now with *mē*). I recommend the Handbook statement, applied to every non-indicative mood (one line: `neg_wish = cl.get("neg") and v.get("mood") in ("OPT", "SBJV")`), but it is a convention choice for David, so it is not in the diff.

**Relative clauses:** the relative is not fronted when a topic precedes it (37 of 507 clauses, e.g. *h₃rḗǵs h₁yód dʰéh₁t*). Fortson §8.27 says a topicalized element may precede the relative, so this is not a defect.

## 6. Compounds (pie/compound.py)

**Right.** Prefixes *h₁su-*, *dus-* (Fortson §6.86; Ringe 2.4.1), privative *n̥-* (Fortson §7.25) with *n̥n-* before a vowel (L&Y) and syllabic *n̥* kept before a laryngeal (Beekes: *n̥-h₁gr-etos*), *sm̥-* (Fortson §7.18). s-stem bahuvrihi → *-es-* adjective of common gender: m./f. *-ēs, -esm̥, -esos*, nom. pl. *-eses*; n. *-es*, pl. *-esh₂* / *-ēs* (Gk εὐκλεής, Ved. *suśrávas-*). Thematic 2nd member → *-os/-eh₂/-om*. The accent follows the BAP exactly as L&Y §3.1 state it: leftmost inherently accented member; unaccented *h₁su-*, *dus-*, numerals and *u*-stem adjectives yield to the 2nd member (Ved. *suśrávas-*, *āśu-héṣas-*); accented thematic 1st member wins (*pró-ḱlewes-*, *h₂ugró-bʰeh₂ǵʰu-*). Productive Gk suffix accent *-ḗs* is kept as an alternative. Vocative initial accent. Determinatives: all 1,299 accepted heads checked; every cell equals deaccented first member + the head's own cell (VOC aside, which takes the whole-word initial accent, Ved. *rā́japutra*). Rejections: prefix determinatives, Caland *-ro-* first members (Fortson §6.87; Ringe 2.4.2), consonant-stem first members, non-*s*/non-thematic bahuvrihi heads, unaccented heads, nested and verbal compounds. All 28 corpus compound tokens are correct.

**Wrong.** P1, P2. *Note (L&Y §3.2):* L&Y treat *-ti-* and *-u-* as underlyingly unaccented in secondary derivation. The engine applies this to *u*-stem adjectives but lets *i/u*-stem **noun** first members keep their accent (Ved. *bāhú-ojas-*, cited in realize.py). L&Y's argument would predict 2nd-member accent for *ti*-stems too. 0 corpus tokens; leave as is, mark it as a convention.

## Proposed patches

### realize.py (R1–R8)

```diff
--- a/pie/realize.py
+++ b/pie/realize.py
@@ -91,7 +91,7 @@
 NOMINAL_ROLES = set(ROLE_CASE) | {"MOD"}
 ROLES = NOMINAL_ROLES | {"ADV", "V"}
 # Wackernagel enclitics: placed after the first word of the clause
-ENCLITIC_PRONOUNS = {"moy", "toy", "me", "te", "nos", "wos", "soy", "se"}
+ENCLITIC_PRONOUNS = {"moy", "toy", "me", "te", "nos", "wos", "soy", "se", "noh₃", "woh₃"}
 
 
 @dataclass
@@ -247,6 +247,15 @@
     return forms[0] if forms else None
 
 
+def _closed_feat(lx: Lexicon, lex_id: str, feat: str) -> str:
+    """The feature actually realized: a personal-pronoun cell that falls back to the enclitic says so."""
+    if lex_id.startswith("closed:personal/") and not feat.endswith(".ENCL"):
+        node = lx.closed["personal"].get(lex_id.split("/")[1], {})
+        if feat not in node and feat + ".ENCL" in node:
+            return feat + ".ENCL"
+    return feat
+
+
 def _person_number(slot: dict, lx: Lexicon) -> tuple[int, str]:
     lid = slot["lex_id"]
     if lid.startswith("closed:personal/") and lid.split("/")[1] in ("1", "2"):
@@ -407,14 +416,39 @@
     for sl in slots:
         if sl["role"] == "MOD" and sl["lex_id"].startswith("closed:numerals/") and sl.get("head") is not None:
             n = sl["lex_id"].split("/")[1]
-            want = {"2": "DU", "3": "PL", "4": "PL"}.get(n)
+            want = {"2": "DU", "3": "PL", "4": "PL", "indeclinable": "PL"}.get(n)
             if want and slots[sl["head"]].get("num") != want:
                 slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
                 slots[sl["head"]]["num"] = want
+    # -kʷe goes on the last conjunct (X Y-kʷe, Lat. senatus populusque): a mark only on an earlier
+    # member of a coordinated group (same role and head) moves to the last one (t014 review)
+    groups: dict = {}
+    for i, sl in enumerate(slots):
+        if sl["role"] not in ("V", "MOD", "ADV"):
+            groups.setdefault((sl["role"], sl.get("head")), []).append(i)
+    for ix in groups.values():
+        if len(ix) > 1 and any(slots[i].get("and") for i in ix) and not slots[ix[-1]].get("and"):
+            slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
+            for i in ix[:-1]:
+                slots[i]["and"] = False
+            slots[ix[-1]]["and"] = True
+    coord = {i for ix in groups.values() if len(ix) > 1 and any(slots[i].get("and") for i in ix) for i in ix}
+    pairs = {i for ix in groups.values() if len(ix) == 2 and slots[ix[-1]].get("and") for i in ix}
     subj_i = next((i for i, s in enumerate(slots) if s["role"] == "SUBJ"), None)
     subj = slots[subj_i] if subj_i is not None else None
     person, num = _person_number(subj, lx) if subj else (3, "SG")
     neuter_pl = subj is not None and person == 3 and subj.get("num") == "PL" and _slot_gender(subj, lx) == "n"
+    subjs = [i for i in coord if slots[i]["role"] == "SUBJ" and slots[i].get("head") is None]
+    if len(subjs) > 1:
+        # conjoined subjects (X Y-kʷe) agree as a group (Fortson §8.16): two singulars dual, else plural;
+        # 1st person over 2nd over 3rd
+        pn = [_person_number(slots[i], lx) for i in subjs]
+        person = min(p for p, _ in pn)
+        if all(slots[i].get("num") == "PL" and _slot_gender(slots[i], lx) == "n" for i in subjs):
+            num = "SG"      # Il. 2.468 phúlla kaì ánthea gígnetai (Fortson §8.16): neuter plurals stay collective
+        else:
+            num = "DU" if len(subjs) == 2 and all(slots[i].get("num", "SG") == "SG" for i in subjs) else "PL"
+            neuter_pl = False
     vi = next(i for i, s in enumerate(slots) if s["role"] == "V")
     v = slots[vi].get("verb", {})
     prohibitive = cl.get("neg") and v.get("mood") == "IMP"
@@ -433,7 +467,10 @@
                 cells = lx.cells(lid)
                 mid = "MID." if v.get("voice") == "MID" else ""
                 feat = next((f"{mid}{t}.{pn}" for t in ("PST", "AOR") if f"{mid}{t}.{pn}" in cells), feat)
-            form = lx.cells(lid)[feat][0]
+            cells = lx.cells(lid)
+            if feat not in cells and feat.endswith("DU") and feat[:-2] + "PL" in cells:
+                feat = feat[:-2] + "PL"       # no dual cell (e.g. the perfect): the plural stands in
+            form = cells[feat][0]
             if prohibitive:
                 feat = feat.replace("PST", "INJ").replace("AOR", "INJ")
         elif role == "ADV":
@@ -454,6 +491,9 @@
             else:
                 head = s
             case = ROLE_CASE["PRED" if role == "PRED" else head["role"]] if role != "MOD" else ROLE_CASE[head["role"]]
+            hi = s["head"] if role == "MOD" else i
+            if case == "VOC" and hi in pairs and slots[hi].get("and"):
+                case = "NOM"        # vā́yav índraś ca 'o Vayu and Indra' (Fortson §8.11)
             if role == "MOD" and head["role"] == "MOD":
                 raise KeyError("MOD cannot head a MOD")
             n = head.get("num", "SG")
@@ -472,6 +512,7 @@
                 form = _closed_form(lx, lid, feat, g)
                 if form is None:
                     raise KeyError(f"{lid} {feat} {g}")
+                feat = _closed_feat(lx, lid, feat)
             elif s.get("participle"):
                 form = lx.participle_cells(lid, s["participle"].get("voice", "ACT"), g)[feat][0]
                 feat = f"PTCP.{s['participle'].get('voice', 'ACT')}.{feat}"
@@ -479,7 +520,8 @@
                 form = lx.cells(lid, g)[feat][0]
             else:
                 form = lx.cells(lid)[feat][0]
-        words[i] = Word(form, lid, lx.gloss(lid), feat, i, clitic=form in ENCLITIC_PRONOUNS)
+        words[i] = Word(form, lid, lx.gloss(lid), feat, i,
+                        clitic=feat.endswith(".ENCL") or form in ENCLITIC_PRONOUNS)
 
     # phrases: every MOD/POSS goes directly before its head, recursively
     def phrase(i: int) -> list[int]:
@@ -500,31 +542,27 @@
     if placed != list(range(len(slots))):
         missing = sorted(set(range(len(slots))) - set(placed))
         raise KeyError(f"slots {missing} not attached to the clause (a MOD/POSS head chain is broken)")
-    # -kʷe goes on the last conjunct (X Y-kʷe, Lat. senatus populusque): a mark only on an earlier
-    # member of a coordinated group (same role and head) moves to the last one (t014 review)
-    groups: dict = {}
-    for i, sl in enumerate(slots):
-        if sl["role"] not in ("V", "MOD", "ADV"):
-            groups.setdefault((sl["role"], sl.get("head")), []).append(i)
-    for ix in groups.values():
-        if len(ix) > 1 and any(slots[i].get("and") for i in ix) and not slots[ix[-1]].get("and"):
-            slots = [dict(x) for x in slots] if slots is cl["slots"] else slots
-            for i in ix[:-1]:
-                slots[i]["and"] = False
-            slots[ix[-1]]["and"] = True
     for i in seq:
         if slots[i]["lex_id"] == "closed:indefinite_kwi":
             words[i].clitic = True        # the indefinite is enclitic: ne kʷis gʷémt 'no one came'
     neg = Word("mē" if (prohibitive or neg_wish) else "ne", "closed:particle:ne", "NEG", "PARTICLE") \
         if cl.get("neg") else None
     vseq = ([neg] if neg else []) + [words[vi]]
+    # -kʷe follows the first word of the conjunct it joins, a single word or a phrase
+    # (Fortson §7.27, §8.24: Lat. lūcusue Diānae; Ved. ágna índraś ca)
+    and_host: dict[int, int] = {}
+    for i, sl in enumerate(slots):
+        if sl.get("and") and sl["role"] not in ("V", "ADV"):
+            ph = [j for j in phrase(i) if not words[j].clitic]
+            and_host[ph[0] if ph else i] = and_host.get(ph[0] if ph else i, 0) + 1
+
     def render_phrase(ph: list[int]) -> list[Word]:
         ws = []
         for i in ph:
             if words[i].clitic:
                 continue
             ws.append(words[i])
-            if slots[i].get("and"):
+            for _ in range(and_host.get(i, 0)):
                 ws.append(Word("-kʷe", "closed:particle:-kʷe", "and", "PARTICLE", clitic=True))
         return ws
 
@@ -537,9 +575,14 @@
         out.insert(0, Word("h₁yód", "closed:relative_yo/n", "if/when", "CONJ"))
     # Wackernagel: enclitics after the first word, "and" (-kʷe) / "or" (-wē) on the first word
     clitics = [words[i] for i in seq if words[i].clitic]
+    # one possessive enclitic serves both conjuncts: h₂óweyes moy h₁éḱwōs-kʷe, not *moy moy
+    clitics = [w for k, w in enumerate(clitics) if (w.form, w.features) not in {(x.form, x.features) for x in clitics[:k]}]
     if cl.get("particle") == "ge":
         clitics.insert(0, Word("-ge", "closed:particle:-ge", "EMPH", "PARTICLE", clitic=True))
-    out[1:1] = clitics
+    k = 1
+    while k < len(out) and out[k].form in ("-kʷe", "-wē"):
+        k += 1
+    out[k:k] = clitics
     if cl.get("conj") in ("kʷe", "wē"):
         f = "-" + cl["conj"]
         out.insert(1, Word(f, f"closed:particle:{f}", "and" if f == "-kʷe" else "or", "PARTICLE", clitic=True))
```

### compound.py (P1, P2)

```diff
--- a/pie/compound.py
+++ b/pie/compound.py
@@ -37,7 +37,10 @@
 }
 # the lexicon's affix entries name the same prefixes
 PREFIX_ALIASES = {"pie-lex-h1su": "closed:prefix/h1su", "pie-lex-dus": "closed:prefix/dus",
-                  "pie-lex-n": "closed:prefix/n"}
+                  "pie-lex-n": "closed:prefix/n", "pie-lex-sm": "closed:prefix/sm",
+                  # the numeral lexemes compound as *dwi- *tri- *kʷetru- (Fortson §7.18), not as dwó-
+                  "pie-lex-dwoh1": "closed:numerals/2", "pie-lex-treyes": "closed:numerals/3",
+                  "pie-lex-kwetwores": "closed:numerals/4"}
 
 
 class CompoundError(ValueError):
@@ -260,6 +263,10 @@
     if fid in PREFIXES and _vocalic_onset(st2) and not form.endswith("s") and not (
             fid == "closed:prefix/n" and _vowel_onset(st2)):
         raise CompoundError(f"{fid} before a second member with a vocalic onset: the books give no junction rule")
+    if fid not in PREFIXES and _vocalic_onset(st2):
+        # a vowel-final stem (-o-, -u-, -i-) before a vowel or syllabic resonant: newo-úderos, newo-n̥bʰrós
+        raise CompoundError(f"first member {fid} before a second member with a vocalic onset ({sid}): "
+                            f"the books give no junction rule")
     return Compound(ctype, fid, sid, form, acc, kind, lx)
 
 
```

### closed_class.json (C1–C6)

A script that applies every edit (keys and order kept; run as `python3 -I script.py data/morph/closed_class.json data/morph/closed_class.json`). For the *-mos*-first alternative in C4, swap the two forms in the `put(... "DAT.PL"/"ABL.PL" ...)` lines. Also add `_refs` entries: `personal/1/NOM.SG: "Ringe 2017 p. 57 éǵh₂ (initial h₁ by the table convention); Fortson §7.4 *eǵoh₂"`, `numerals/indeclinable/10: "Fortson §7.17 *dék̑m̥; Ringe 2017 p. 54 déḱm̥d"`, `numerals/3/f/ACC.PL: "Ringe 2017 p. 53 tisrn̥s (accent?), accented like nom. tísres"`.

```python
"""Closed-class edits proposed by docs/audits/engine-sweep/closed-class-compounds.md (run: python3 cc_closed_patch.py IN OUT)."""
import json, sys
d = json.load(open(sys.argv[1]))
def put(path, forms):
    node = d
    for p in path[:-1]: node = node[p]
    node[path[-1]] = forms
# C1 1sg nominative: accented, Ringe éǵh₂ with the table's initial h₁ (cf. anaphoric h₁éy < Ringe éy)
put(["personal","1","NOM.SG"], ["h₁éǵh₂", "h₁eǵ", "éǵh₂", "eǵoh₂", "eǵh₂óm"])
# C2 'ten': Fortson §7.17 *dék̑m̥ (= the lexicon's pie-lex-dekjm); Ringe déḱm̥d kept
put(["numerals","indeclinable","10"], ["déḱm̥", "déḱm̥t", "déḱm̥d"])
# C3 fem. 'three' acc. pl. accented like its nom. tísres
put(["numerals","3","f","ACC.PL"], ["tísrn̥s", "tisrn̥s", "tísr̥ms"])
# C4 dat. = abl. pl., masc. = neut. obliques (one primary per table)
for t, st, fst in [("demonstrative_so","t","téh₂"),("deictic_ki","ḱ","ḱéh₂"),("deictic_eno","h₁én","h₁éneh₂"),
                   ("relative_yo","h₁y","h₁yéh₂"),("interrogative_kwo","kʷ","kʷéh₂")]:
    o = st + ("o" if t == "deictic_eno" else "ó")
    for c in ("DAT.PL","ABL.PL"):
        put([t,"m",c], [o+"ybʰos", o+"ymos"]); put([t,"n",c], [o+"ybʰos", o+"ymos"])
        put([t,"f",c], [fst+"bʰos", fst+"mos"])
    put([t,"m","GEN.PL"], [o+"ysōm", o+"ysoHom"]); put([t,"n","GEN.PL"], [o+"ysōm", o+"ysoHom"])
put(["interrogative_kwi","n","DAT.PL"], ["kʷóybʰos","kʷóymos"]); put(["interrogative_kwi","n","ABL.PL"], ["kʷóybʰos","kʷóymos"])
put(["interrogative_kwi","mf","DAT.PL"], ["kʷóybʰos","kʷóymos"]); put(["interrogative_kwi","mf","ABL.PL"], ["kʷóybʰos","kʷóymos"])
put(["interrogative_kwi","n","GEN.PL"], ["kʷóysōm","kʷóysoHom"]); put(["interrogative_kwi","mf","GEN.PL"], ["kʷóysōm","kʷóysoHom"])
# dat./loc./gen./ins. sg. like the demonstrative (tósmey, tósmi, tósyo, tóh₁)
put(["relative_yo","m","DAT.SG"], ["h₁yósmey","h₁yósmōy","h₁yosméy"]); put(["relative_yo","n","DAT.SG"], ["h₁yósmey","h₁yósmōy","h₁yosméy"])
put(["relative_yo","n","INS.SG"], ["h₁yóh₁","h₁yónoh₁"]); put(["relative_yo","m","INS.SG"], ["h₁yóh₁","h₁yónoh₁"])
for g in ("m","n"):
    put(["interrogative_kwo",g,"GEN.SG"], ["kʷósyo","kʷésyo","kʷéso"])
    put(["interrogative_kwo",g,"DAT.SG"], ["kʷósmey","kʷósmōy","kʷésmōy"])
    put(["interrogative_kwo",g,"LOC.SG"], ["kʷósmi","kʷésmi"])
    put(["interrogative_kwo",g,"INS.SG"], ["kʷóh₁","kʷónoh₁"])
for g in ("mf","n"):            # i/e-stem: e-grade like gen. kʷésyo (Ringe pp. 56, 117)
    put(["interrogative_kwi",g,"DAT.SG"], ["kʷésmey","kʷésmōy","kʷósmey"])
    put(["interrogative_kwi",g,"LOC.SG"], ["kʷésmi","kʷósmi"])
put(["interrogative_kwi","n","ACC.PL"], ["kʷíh₂"])           # = NOM.PL (neuter)
for g, s in (("m","tri"),("n","tri"),("f","tisr̥")):
    for c in ("DAT.PL","ABL.PL"): put(["numerals","3",g,c], [s+"bʰós", s+"mós"])
for g, s in (("m","kʷetwr̥"),("n","kʷetwr̥"),("f","kʷetesr̥")):
    for c in ("DAT.PL","ABL.PL"): put(["numerals","4",g,c], [s+"bʰós", s+"mós"])
# C5 vocative of 2-4 = nominative (Ringe p. 53-54 'n.-v.')
for n_, g_ in (("3","m"),("3","f"),("3","n"),("4","m"),("4","f"),("4","n")):
    put(["numerals",n_,g_,"VOC.PL"], list(d["numerals"][n_][g_]["NOM.PL"]))
for g_ in ("m","fn"):
    put(["numerals","2",g_,"VOC.DU"], list(d["numerals"]["2"][g_]["NOM.DU"]))
json.dump(d, open(sys.argv[2],"w"), ensure_ascii=False, indent=2)
```

### data/generation/blocklist.jsonl (L1, L2)

```json
{"lex_id": "pie-lex-dwoh1", "reason": "the adjective lexeme declines as a thematic adjective (sg. dwós, pl. dwṓs); 'two' is a dual: use closed:numerals/2 (Ringe 2017 p. 53; engine-sweep closed-class audit)"}
{"lex_id": "pie-lex-kwetwores", "reason": "the adjective lexeme makes sg. kʷetwṓr and neut. pl. kʷetwṓ (Ringe 2017 p. 54 kʷetwṓr); use closed:numerals/4 (engine-sweep closed-class audit)"}
{"lex_id": "pie-lex-sexm", "reason": "fem. sih₂ drops the m (Ringe 2017 p. 52 sémih₂, Fortson §7.16 *sm-ih₂) and the adjective module builds a plural of 'one'; blocked until hand-tabled (engine-sweep closed-class audit)"}
```

The 2 corpus records that use pie-lex-kwetwores (t3-b003-00065, t3-t012-00022) then need closed:numerals/4.

### Tests (tests/test_realize.py)

```python
def _lx():
    from pie.realize import Lexicon
    return Lexicon.load()


def test_kwe_follows_first_word_of_a_phrasal_conjunct():
    """Fortson §8.24 (Lat. lūcusue Diānae): -kʷe after the first word of the conjunct, not its head."""
    from pie.realize import realize
    p = {"english": "The warrior and his son-in-law came.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-Hyudhsmos", "role": "SUBJ"},
        {"lex_id": "pie-lex-gjmros", "role": "SUBJ", "and": True},
        {"lex_id": "closed:demonstrative_so", "role": "POSS", "head": 1},
        {"lex_id": "pie-lex-gwemt", "role": "V", "verb": {"tense": "AOR"}}]}]}
    assert "tósyo-kʷe ǵm̥rós" in realize(p, _lx())["pie"]


def test_conjoined_subjects_agree_as_a_group():
    """Fortson §8.16: two singular subjects joined by -kʷe take a dual verb; neuter plurals stay singular."""
    from pie.realize import realize
    p = {"english": "The wolf and the snake fled.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-wlkwos", "role": "SUBJ"},
        {"lex_id": "pie-lex-h1ogwhis", "role": "SUBJ", "and": True},
        {"lex_id": "pie-lex-bhewgt-3", "role": "V", "verb": {"tense": "AOR"}}]}]}
    w = realize(p, _lx())["words"]
    assert [x["features"] for x in w if x["lex_id"] == "pie-lex-bhewgt-3"] == ["AOR.3DU"]


def test_wackernagel_clitic_after_the_first_words_own_kwe():
    """Fortson §8.25: sentential clitics follow the first word and its connective clitic (gʷṓs-kʷe te)."""
    from pie.realize import realize
    p = {"english": "I nourish you and your cattle.", "clauses": [{"slots": [
        {"lex_id": "closed:personal/2", "role": "OBJ", "enclitic": True},
        {"lex_id": "pie-lex-gwoxws", "role": "OBJ", "num": "PL", "and": True},
        {"lex_id": "pie-lex-h2eleti", "role": "V", "verb": {"person": 1, "num": "SG"}}]}]}
    assert realize(p, _lx())["pie"].startswith("gʷṓs-kʷe te ")


def test_dual_enclitics_are_wackernagel():
    from pie.realize import realize
    p = {"english": "His brother seized us two.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-bhreh2texr", "role": "SUBJ"},
        {"lex_id": "closed:demonstrative_so", "role": "POSS", "head": 0},
        {"lex_id": "closed:personal/2", "role": "OBJ", "num": "DU", "enclitic": True},
        {"lex_id": "pie-lex-lembht", "role": "V", "verb": {"tense": "AOR"}}]}]}
    assert realize(p, _lx())["pie"].split()[1] == "woh₃"


def test_conjoined_vocative_pair_puts_the_second_in_the_nominative():
    """Fortson §8.11: Ved. vā́yav índraś ca."""
    from pie.realize import realize
    p = {"english": "Father and Mother, hear!", "clauses": [{"slots": [
        {"lex_id": "pie-lex-ph2texr", "role": "VOC"},
        {"lex_id": "pie-lex-meh2texr", "role": "VOC", "and": True},
        {"lex_id": "pie-lex-kjlewt", "role": "V", "verb": {"tense": "AOR", "mood": "IMP", "person": 2, "num": "DU"}}]}]}
    assert realize(p, _lx())["pie"].startswith("ph₂ter méh₂tēr-kʷe ")


def test_indeclinable_numeral_makes_its_head_plural():
    from pie.realize import realize
    p = {"english": "Seven horses ran.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-h1ekjwos", "role": "SUBJ"},
        {"lex_id": "closed:numerals/indeclinable/7", "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-bhewgt-3", "role": "V", "verb": {"tense": "AOR"}}]}]}
    assert realize(p, _lx())["pie"] == "septḿ̥ h₁éḱwōs bʰugént."


def test_closed_class_table_consistency():
    """Masc. and neut. obliques are one form; dat. pl. = abl. pl.; stressed forms carry an accent."""
    import unicodedata
    d = _lx().closed
    for t in ("demonstrative_so", "interrogative_kwo", "interrogative_kwi", "relative_yo", "anaphoric_i",
              "deictic_ki", "deictic_eno"):
        m, n = d[t].get("m") or d[t]["mf"], d[t]["n"]
        for k in set(m) & set(n):
            if k.split(".")[0] in ("GEN", "ABL", "DAT", "LOC", "INS"):
                assert m[k][0] == n[k][0], (t, k)
        for g, c in d[t].items():
            if isinstance(c, dict) and "DAT.PL" in c:
                assert c["DAT.PL"][0] == c["ABL.PL"][0], (t, g)
    assert "́" in unicodedata.normalize("NFD", d["personal"]["1"]["NOM.SG"][0].replace("ǵ", "g"))
    assert d["numerals"]["indeclinable"]["10"][0] == "déḱm̥"         # Fortson §7.17


def test_numeral_vocative():
    from pie.realize import realize
    p = {"english": "Three brothers, come!", "clauses": [{"slots": [
        {"lex_id": "pie-lex-bhreh2texr", "role": "VOC", "num": "PL"},
        {"lex_id": "closed:numerals/3", "role": "MOD", "head": 0},
        {"lex_id": "pie-lex-gwemt", "role": "V", "verb": {"tense": "AOR", "mood": "IMP", "person": 2, "num": "PL"}}]}]}
    assert realize(p, _lx())["pie"].startswith("tréyes ")
```

## Corpus impact after all fixes

Re-realizing all 12,867 stored clauses with every patch above changes 203 of them, with no new errors. Most changed tokens: *h₁eǵ* → *h₁éǵh₂* 82, *déḱm̥t* → *déḱm̥* 54, phrase *-kʷe* moved 29, *h₁yósmōy* → *h₁yósmey* 7, *kʷésmōy* → *kʷésmey* 4, *kʷésyo* → *kʷósyo* (kʷo-) 4, vocative pairs 11 (*dʰéǵʰom* → *dʰéǵʰōm*, *méh₂ter* → *méh₂tēr*, …), conjoined-subject verbs 8, dual enclitics 3, *moy moy* 3, *tisrn̥s* → *tísrn̥s* 2. Label-only: 68 `GEN.PL` → `GEN.PL.ENCL`.
