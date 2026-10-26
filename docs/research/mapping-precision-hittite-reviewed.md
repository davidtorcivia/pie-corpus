# Reviewed Hittite additions to existing etyma

2026-10-25. This review is restricted to the 200 most frequent content lemmas left unmapped by the resolved main table at the start. `fm.load_hittite()` supplies tokens; each counted token has `units["para"]`. Frequencies count token occurrences, not distinct paragraphs. Ranking is descending frequency, then lemma for ties. Main and union coverage use `hm.read_union_table(doubtful=False/True)`, including the single override resolver. No lexicon entries were created.

## Coverage

| Tier | Before tokens | After tokens | Before | After | Before types | After types |
|---|---:|---:|---:|---:|---:|---:|
| Main | 60,415 | 63,977 | 44.7393% | 47.3770% | 302 | 325 |
| Main + doubtful | 60,417 | 65,682 | 44.7407% | 48.6396% | 303 | 333 |

Denominator: 135,038 content tokens; 5,916 content lemma types. Main additions: 23; reviewed doubtful additions: 7. The pre-existing doubtful row is preserved.

## Main decisions

Notes below are review paraphrases, forms and page references, not book quotations. The lemma includes the corpus gloss. These rows are appended in the existing Hittite format to `mapping-overrides/east.json`.

| Lemma | Tokens | Existing lex_id | Evidence |
|---|---:|---|---|
| warp=@baden | 135 | pie-root-werp-turn_back_and-2 | Kloekhorst EDHIL pp. 965-966: warp-; *u̯érp-ti / *u̯r̥p-énti. The washing sense is connected through rubbing to repeated turning. LIV² p. 690 explicitly includes warapzi and war(ap)panzi. |
| šak(k)-, šek(k)-@wissen | 293 | pie-root-sekH-separate | Kloekhorst EDHIL pp. 695-696: šākk- / šakk-; *sókh₁-ei / *skh₁-énti. The semantic bridge is discrimination to knowledge; LIV² p. 524 includes sakki and sakteni under *sekH-. None of the *sekʷ- homographs is intended. |
| meḫ=ur@Zeit | 241 | pie-root-meyH-become_small | Kloekhorst EDHIL pp. 567-568: mēḫur; *méih₂-ur. EDHIL explicitly connects a finite period with diminution, rejecting the competing maturity explanation; *meyH- is the lexicon notation. |
| ar=a-@Freund | 129 | pie-root-h2er-fit | Kloekhorst EDHIL pp. 198-199: arā- is included among the derivatives of āra; *h₂or-o-. The entry connects this family with fitting and joining. |
| ar=ae-@erheben | 160 | pie-root-h3er-move | Kloekhorst EDHIL pp. 200: arai- / ari-; *h₃r-oi- / *h₃r-i-. The raising verb is distinguished from arae- on p. 199; the latter headword caused the key collision. |
| arw=ā(e)-@sich verneigen | 213 | pie-root-h2er-speak_weightily_loudly | Kloekhorst EDHIL pp. 213: aruwae-; *h₂or-u̯o-ye/o-. EDHIL relates the act of obeisance to the nominal prayer family; LIV² p. 271 identifies Greek *arwā- with this root. |
| lutt=ai-@Fenster | 155 | pie-root-lewt-see | Kloekhorst EDHIL pp. 534-535: luttāi / lutti-; *lut-oi / *lut-i-. EDHIL explicitly chooses *leut- and the visual function of the window, rather than the competing cutting etymology. |
| ḫamenk-@binden | 125 | pie-root-h2emgjh-lace_up | Kloekhorst EDHIL pp. 278-279: ḫamank- / ḫame/ink-; *h₂m-ón-ǵʰ-ei. EDHIL identifies the nasal-infixed formation with *h₂emǵʰ-; ḫamenk- is an explicit cross-reference. |
| an=iye/a-@wirken | 298 | pie-root-h3enH-onerate | Kloekhorst EDHIL pp. 179-181: aniye/a- and its imperfective anniške/a-; *h₃n-ye/o-. EDHIL retains the onus/ánas cognate family but removes the final laryngeal of the lexicon notation *h₃enH-. This is a reviewed family equation, not an endorsement of that laryngeal. |
| ann=išk-@wirken | 78 | pie-root-h3enH-onerate | Kloekhorst EDHIL pp. 179-181: aniye/a- and its imperfective anniške/a-; *h₃n-ye/o-. EDHIL retains the onus/ánas cognate family but removes the final laryngeal of the lexicon notation *h₃enH-. This is a reviewed family equation, not an endorsement of that laryngeal. |
| pešš=iye/a-@werfen | 591 | pie-root-h1es-throw | Kloekhorst EDHIL pp. 670-671: peššiye/a-; *h₁poi + *h₁s-ye/o-. The throwing lemma continues the prefixed verb, not peš(š)- on p. 669; the compound PIE line blocks the automatic root route. |
| pešš=@werfen | 105 | pie-root-h1es-throw | Kloekhorst EDHIL pp. 670-671: peššiye/a-; *h₁poi + *h₁s-ye/o-. The throwing lemma continues the prefixed verb, not peš(š)- on p. 669; the compound PIE line blocks the automatic root route. |
| išḫu=a-@schütten | 105 | pie-root-sh2ew-pour | Kloekhorst EDHIL pp. 396-398: išḫuwai- / išḫui-; *sh₂u-(o)i-. These shortened TLHdig stems belong to the pouring paradigm; root *sh₂eu-. |
| išḫ=u-@schütten | 78 | pie-root-sh2ew-pour | Kloekhorst EDHIL pp. 396-398: išḫuwai- / išḫui-; *sh₂u-(o)i-. These shortened TLHdig stems belong to the pouring paradigm; root *sh₂eu-. |
| ištamašš=@hören | 79 | pie-lex-steh3mn | Kloekhorst EDHIL pp. 411-413: ištamašš- is the s-extension of ištaman-; *stéh₃mn̥ / *sth₃mén-s. The existing nominal lexeme includes the Hittite ear reflex; this mapping is through the stated nominal base. |
| genz=u-@Schoß | 68 | pie-root-gjenh1-produce | Kloekhorst EDHIL pp. 468-469: genzu-; *ǵenh₁-su-. EDHIL explicitly derives the anatomical and figurative senses from the procreation family. |
| kur=eššar@abgeschnittener Stoff | 118 | pie-root-kwer-do | Kloekhorst EDHIL pp. 494: kurēššar; *kʷr-éh₁sh₁-r. EDHIL identifies this as a derivative of kuer-; the existing root includes carving and cutting, despite its id ending in do. |
| tani=nu-@ordnen | 133 | pie-root-dheh1-do | Kloekhorst EDHIL pp. 827-828: taninu-; *dʰoh₁-ni-neu-. EDHIL connects its base with placement; the TLHdig gloss does not express the installation sense used in the headword. |
| wašš=@bedecken | 109 | pie-root-wes-dress | Kloekhorst EDHIL pp. 1004-1006: wešš- / wašše/a-; *u̯és-to / *u̯s-yé-ti. The entry includes covering as well as clothing; the shortened key misses this headword. |
| šuwa=@füllen | 90 | pie-root-sewh3-be_become_full | Kloekhorst EDHIL pp. 794, 797: šuwe/a-; *sHu-ye/o-. EDHIL explains laryngeal metathesis from *suH- and explicitly connects the verb with šūu- and šunna-; the intended root is fullness, not pouring. |
| ling=ai-@Schwur | 87 | pie-root-h1lengjh-assert_on_oath | Kloekhorst EDHIL pp. 526-528: lingai- / linki- is listed as a derivative of li(n)k-; *h₁lenǵʰ-. The derived nominal key fails to reach the verbal entry. |
| išḫi=ul-@Vertrag | 109 | pie-root-sh2ey-bind | Kloekhorst EDHIL pp. 391-393: išḫiul- is a derivative of išḫai- / išḫi-; *sh₂-(o)i-. EDHIL treats i as a stem extension where LIV² and the existing root use *sh₂ei-; the binding family is the same, not *seh₂- satiation. |
| taganzip=a-@Erde | 63 | pie-lex-dhegjhoxm | Kloekhorst EDHIL pp. 812-813: tagānzepa- contains the earth stem of tēkan / takn-, *dʰǵʰōm + *sepa-. The existing earth lexeme supplies its nominal base; the additional element is not assigned a separate etymon. |

## Doubtful decisions

These decisions live in `data/research/formulas/hit-reviewed-doubtful.json`. `hm.doubtful_table` applies them only to content lemmas absent from the main table and without any override decision, including removals. Output retains `how=kloekhorst-doubtful`, `confidence=low`, EDHIL pages and reviewer notes.

| Lemma | Tokens | Existing lex_id | Evidence |
|---|---:|---|---|
| palw=ā(e)-@anstimmen | 601 | pie-root-bhleh1-bleat | Kloekhorst EDHIL p. 623: the vocal sense selects the crying/bleating root, not the blowing homograph; palwāt(t)alla- is explicitly included as a derivative. PIE line marked doubtful. |
| palwatall=a-@Anstimmer | 457 | pie-root-bhleh1-bleat | Kloekhorst EDHIL p. 623: the vocal sense selects the crying/bleating root, not the blowing homograph; palwāt(t)alla- is explicitly included as a derivative. PIE line marked doubtful. |
| palwattall=a-@Anstimmer | 92 | pie-root-bhleh1-bleat | Kloekhorst EDHIL p. 623: the vocal sense selects the crying/bleating root, not the blowing homograph; palwāt(t)alla- is explicitly included as a derivative. PIE line marked doubtful. |
| ḫurt=ai-@Fluch | 65 | pie-root-h2wert-swear | Kloekhorst EDHIL pp. 372-373: ḫurtāi- is explicitly derived from the cursing verb; the proposed Old Prussian swearing cognate identifies *h₂wert-. PIE line marked doubtful. |
| arun=a-@Meer | 73 | pie-root-h3er-move | Kloekhorst EDHIL p. 212: the proposed connection passes through aru- and the elevation of water, with a Sanskrit parallel. PIE line marked doubtful. |
| punušš=@fragen | 207 | pie-root-pnewH-regain_consciousness | Kloekhorst EDHIL pp. 681-682: tentative desiderative connection with cognition; LIV² p. 489 explicitly includes punuszi and punussanzi. Retain EDHIL double doubt despite the LIV assignment. |
| šuḫḫ=a-@schütten | 208 | pie-root-sh2ew-pour | Kloekhorst EDHIL pp. 773-774 (compare pp. 396-398): the pouring paradigm is connected with išḫuwai- through laryngeal metathesis, *sh₂u- / *suh₂-. Retain the question mark on the PIE line. |

## Complete frozen top-200 disposition

“No supported headword” below means no sense-matched headword or documented derivative connection was established in this review; it does not claim that the lemma is absent from the entire book. Incidental damaged-key matches are not etymological evidence. A mechanical form without an existing sense-matched etymon remains unmapped.

| Rank | Lemma | Tokens | Disposition / reason |
|---:|---|---:|---|
| 1 | parš=@zerbrechen | 2878 | EDHIL p. 642 marks *bʰr̥s- doubtful; existing *bʰers- concerns a tip/top, not breaking. |
| 2 | mem=a-@sprechen | 2235 | EDHIL pp. 573-575: alternative doubly doubtful reconstructions do not identify one existing speech etymon. |
| 3 | iye/a-@machen | 1588 | EDHIL p. 381: doubtful *HH-ye/o-; matching laryngeal skeletons concern heat, not making. |
| 4 | ḫumant-@jeder; ganz | 1212 | EDHIL p. 361: doubtful *h₂u-went-; no supported existing totality etymon. |
| 5 | ḫalz=ai-@rufen | 1085 | EDHIL pp. 276-278: *h₂lt-; no existing root/lexeme established for the calling family. |
| 6 | palw=ā(e)-@anstimmen | 601 | Doubtful addition only; see evidence above. |
| 7 | mem=išk-@sprechen | 592 | Imperfective of mēma-; same unresolved alternatives, EDHIL pp. 573-575. |
| 8 | pešš=iye/a-@werfen | 591 | Main addition; see evidence above. |
| 9 | ḫand=ā(e)-@ordnen | 548 | EDHIL pp. 289-291 explicitly rejects derivation from ḫant-; no known cognate for its proposed nominal base. |
| 10 | ištanan=a-@Altar | 501 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 413. |
| 11 | irḫ=ā(e)-@die Runde machen | 494 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 12 | waḫ=nu-@wenden | 467 | EDHIL pp. 993-995: doubtful turning family; existing *weyH- is withering, not turning. |
| 13 | ḫuppa=r-@Schale | 458 | Damaged key collides with EDHIL p. 295 business-family headword; vessel sense does not justify that mapping. |
| 14 | palwatall=a-@Anstimmer | 457 | Doubtful addition only; see evidence above. |
| 15 | ni=@(Orakelterminus) | 419 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 16 | kit=a-@Vortragspriester(?) | 415 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 17 | idal=u-@böse | 413 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 420. |
| 18 | ḫuek-/ḫuk-@schlachten/beschwören | 405 | EDHIL pp. 347-349 separates slaughter and incantation homographs; the corpus lemma merges them, and one etymology is doubtful. No mixed-tier union. |
| 19 | ḫuwaš=i-@Kultstele | 373 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 20 | ân-@warmes Brot | 362 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 21 | wašt=ul-@Frevel | 354 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 931, 985. |
| 22 | e=šša-@machen | 329 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 388. |
| 23 | ḫuitt=iye/a-@ziehen | 325 | EDHIL pp. 350-352 requires *h₂ueTH- and leaves the cognate decision open; replacing it by *h₂uet- is not a notation-only correction. |
| 24 | ḫatr=ā(e)-@mitteilen | 307 | EDHIL pp. 335-336 connects writing with piercing. Existing *h₂et- entries have incompatible senses; the prior automatic h₂etō stub is not sufficient semantic evidence. |
| 25 | šuppiy=aḫḫ-@heilig machen | 303 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 789. |
| 26 | an=iye/a-@wirken | 298 | Main addition; see evidence above. |
| 27 | šak(k)-, šek(k)-@wissen | 293 | Main addition; see evidence above. |
| 28 | takarm=u-@(Brot oder Gebäck) | 287 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 29 | aḫrušḫ=i-@Räucherschale | 281 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 30 | šupp=a-@Fleisch | 262 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 31 | tarn=a-@Halbmaß | 253 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 32 | šarr=a-@teilen | 252 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 730, 727. |
| 33 | wem=iye/a-@finden | 246 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 998. |
| 34 | šaramma-@Brotration(?) | 244 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 35 | ḫuprušḫ=i(t)-@Räucheraltar(?) | 244 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 36 | kurš=a-@Vlies | 243 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 37 | ḫarš=i-@Vorratsgefäß | 242 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 38 | meḫ=ur@Zeit | 241 | Main addition; see evidence above. |
| 39 | keld=i-@Wohlbefinden | 240 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 40 | ḫap=iya-@(Kultfunktionär) | 232 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 41 | taw=al-@(kultisches Getränk) | 230 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 42 | anaḫ=i(t)-@Kostprobe (einer Opfergabe) | 227 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 43 | marnu=a-@(Biersorte) | 220 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 44 | ḫalk=i-@Getreide | 214 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 274. |
| 45 | arw=ā(e)-@sich verneigen | 213 | Main addition; see evidence above. |
| 46 | kuš=@ungünstig | 210 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 47 | šuḫḫ=a-@schütten | 208 | Doubtful addition only; see evidence above. |
| 48 | punušš=@fragen | 207 | Doubtful addition only; see evidence above. |
| 49 | šupp=i-@kultisch rein | 207 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 789. |
| 50 | išḫaruḫ=@(Opfergefäß) | 200 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 51 | alḫuitr=a-@(Priesterin) | 194 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 52 | wag=eššar@(Brot oder Gebäck) | 190 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 53 | galgaltur=i-@Tamburin(?) | 183 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 54 | parašnau=aš@Mann des Niederhockens | 183 | Derived crouching expression; the nominal base remains ambiguous (EDHIL p. 645). |
| 55 | danna=š-@(Speise) | 182 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 56 | ḫalzi=ya-@rufen | 179 | EDHIL pp. 276-278: *h₂lt-; no existing root/lexeme established for the calling family. |
| 57 | parš=iye/a-@zerbrechen | 173 | EDHIL p. 642 marks *bʰr̥s- doubtful; existing *bʰers- concerns a tip/top, not breaking. |
| 58 | za=nu-@kochen | 172 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 59 | wēḫ-/waḫḫ-@sich drehen | 169 | EDHIL pp. 993-995: *uéih₂-o is doubtful and the existing *weyH- has an incompatible sense. |
| 60 | tur=iye/a-@festmachen | 167 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 61 | ḫalzi=ša-@rufen | 166 | EDHIL pp. 276-278: *h₂lt-; no existing root/lexeme established for the calling family. |
| 62 | aš=eššar@Versammlung | 164 | EDHIL p. 219 offers two analyses of the base; do not select between existing being and sitting roots on the assembly gloss alone. |
| 63 | paršn=ā(e)-@sich niederhocken | 162 | EDHIL p. 645 leaves heel versus feline nominal bases unresolved; *pers- sprinkle is not this etymon. |
| 64 | ar=ae-@erheben | 160 | Main addition; see evidence above. |
| 65 | upp=a-@(her)schicken | 157 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 921. |
| 66 | ḫarš=i-@Brotlaib | 157 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 67 | lutt=ai-@Fenster | 155 | Main addition; see evidence above. |
| 68 | šuw=aye/a-@(an)schauen | 154 | EDHIL pp. 795-796: doubtful spying etymology; no existing sense-matched root established. |
| 69 | šar=nink-@kompensieren | 153 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 736. |
| 70 | tarpal=a/i-@Schärpe(?) | 152 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 71 | gip=eššar@Elle | 151 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 479. |
| 72 | idur=i-@(Brot oder Gebäck) | 144 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 73 | karp=i-@Zorn | 144 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 74 | ḫalliyar=i-@(Kultsänger) | 144 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 75 | ḫila=mmar@Torbau | 144 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 76 | ḫalug=a-@Botschaft | 143 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 77 | ḫarzaz=u(t)-@(Brot oder Gebäck?) | 141 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 78 | ku=tt-@Mauer | 140 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 498. |
| 79 | imm=iye/a-@mischen | 138 | EDHIL pp. 385-386 rejects the exchange etymology and distinguishes the holding sense of *yem-; no secure sense-matched existing root. |
| 80 | karuil=i-@früherer | 138 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 81 | nai-/neya-@(sich) drehen | 137 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 598. |
| 82 | tuḫḫu=eššar@(feste Reinigungssubstanz) | 137 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 83 | walḫ=i-@walḫi-Bier | 137 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 84 | parku=i-@rein | 136 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 637. |
| 85 | ḫattal=u-@Riegel | 136 | Doubtful EDHIL proposal; no single existing etymon with defensible sense correspondence established. EDHIL p(p). 332. |
| 86 | warp=@baden | 135 | Main addition; see evidence above. |
| 87 | tani=nu-@ordnen | 133 | Main addition; see evidence above. |
| 88 | pank=u-@viel | 131 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 89 | ar=a-@Freund | 129 | Main addition; see evidence above. |
| 90 | parš=iya-@zerbrechen | 128 | EDHIL p. 642 marks *bʰr̥s- doubtful; existing *bʰers- concerns a tip/top, not breaking. |
| 91 | kalmu=š-@Lituus (Krummstab des Königs) | 126 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 431. |
| 92 | memi=an-@Wort | 125 | EDHIL p. 575: speech-family alternatives; existing *mey- homographs have incompatible senses. |
| 93 | ḫamenk-@binden | 125 | Main addition; see evidence above. |
| 94 | ḫeš(š)-/ḫaš(š)-@öffnen | 125 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 321. |
| 95 | paršull=i-@Brocken | 124 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 96 | ḫil=a-@Hof | 124 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 97 | labarn=a-@(Königstitel) | 123 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 98 | tuḫur=ai-@(Brot oder Gebäck) | 123 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 99 | kuru=r@Feindschaft | 122 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 496. |
| 100 | tapišan=a-@(Gefäß) | 121 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 101 | ḫamin=a-@Kämmerer | 121 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 102 | parku=nu-@reinigen | 119 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 103 | kur=eššar@abgeschnittener Stoff | 118 | Main addition; see evidence above. |
| 104 | mug=ā(e)-@beten | 118 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 105 | zankil=atar@Bestrafung | 117 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 106 | app=a-@fertig sein | 116 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 107 | arku=ā(e)-@bitten | 116 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 108 | irḫu=i(t)-@Korb | 111 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 109 | kapp=i-@(Behälter) | 111 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 110 | išḫi=ul-@Vertrag | 109 | Main addition; see evidence above. |
| 111 | wašš=@bedecken | 109 | Main addition; see evidence above. |
| 112 | zuḫr=i-@(Gras) | 109 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 113 | mulat=i-@(Brot oder Gebäck) | 108 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 114 | zintuḫ=i-@(Funktionärin) | 108 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 115 | ḫalku=eššar@Ernte | 108 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 116 | šeppi=t-@(Getreideart) | 107 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 117 | išḫu=a-@schütten | 105 | Main addition; see evidence above. |
| 118 | ni=nink-@heben | 105 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 119 | pešš=@werfen | 105 | Main addition; see evidence above. |
| 120 | taparwaš=u-@(Brot oder Gebäck) | 103 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 121 | papr=atar@Unsauberkeit | 101 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 122 | ḫalliyar=a-@(Kultsänger) | 100 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 123 | zil=a-@Entscheidung | 99 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 124 | i=šša-@machen | 98 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 388. |
| 125 | muk=eššar@Anrufung | 98 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 126 | palš=a-@Weg | 98 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 621. |
| 127 | gimr=a/i-@Feld | 96 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 476. |
| 128 | paršiy=anna-@zerbrechen | 95 | EDHIL p. 642 marks *bʰr̥s- doubtful; existing *bʰers- concerns a tip/top, not breaking. |
| 129 | laḫann=i-@(Flasche oder Krug aus Gold oder Silber) | 94 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 130 | ašš=ul-@Güte | 93 | EDHIL pp. 223-224: doubtful good-family reconstruction; no justification for equating it with the sitting root despite the matching skeleton. |
| 131 | ey=an-@Eibe(?) | 92 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 132 | palwattall=a-@Anstimmer | 92 | Doubtful addition only; see evidence above. |
| 133 | watarn=aḫḫ-@befehlen | 92 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 988. |
| 134 | ši=@(Orakelterminus) | 92 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 135 | kišr=i-@(Wollgegenstand) | 91 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 136 | ḫaršiyall=i-@Vorratsgefäß | 91 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 137 | mani=aḫḫ-@zuteilen | 90 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 553. |
| 138 | parn=a-@Haus | 90 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 666. |
| 139 | šuwa=@füllen | 90 | Main addition; see evidence above. |
| 140 | šane=zzi-@angenehm | 89 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 141 | kankat=i-@(Art Brei) | 88 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 142 | ling=ai-@Schwur | 87 | Main addition; see evidence above. |
| 143 | purpur=a/i-@Klumpen | 86 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 144 | watku=@springen | 86 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 989. |
| 145 | ḫanišš=a-@Schöpfgefäß | 84 | EDHIL pp. 286-287 rejects an inherited water-drawing analysis of this vessel name. |
| 146 | ḫalentuw=a-@Palast | 83 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 147 | kapun=u-@(Flächenmaß) | 81 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 148 | luzz=i-@Fronarbeit | 81 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 536. |
| 149 | utn=e-@Land | 81 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 933. |
| 150 | ḫaštap=i-@(Orakelvogel) | 81 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 151 | išpantuzi=aššar@Libationsgefäß | 80 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 152 | tarkumm=iye/a-@verkünden | 80 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 153 | šupp=a-@kultisch rein | 80 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 789. |
| 154 | arkam=i-@(Art Harfe oder Leier) | 79 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 155 | ištamašš=@hören | 79 | Main addition; see evidence above. |
| 156 | tupp=a-@Truhe | 79 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 157 | ḫal=i-@(Brot oder Gebäck) | 79 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 158 | ḫappin=a-@offene Flamme | 79 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 159 | ann=išk-@wirken | 78 | Main addition; see evidence above. |
| 160 | išḫ=u-@schütten | 78 | Main addition; see evidence above. |
| 161 | kururiy=aḫḫ-@als Feind behandeln | 77 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 162 | ḫeu-@Regen | 77 | Doubtful EDHIL proposal; no single existing etymon with defensible sense correspondence established. EDHIL p(p). 340. |
| 163 | ki=nu-@öffnen | 76 | EDHIL pp. 477-478: doubtful aspirated dorsal; *ǵeyH- without aspiration is not an acceptable normalization. |
| 164 | maršanašš=i-@(Orakelvogel) | 76 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 165 | a=a-@warm sein | 75 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 166 | ambašš=i(t)-@Brandopfer | 75 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 167 | išiy=aḫḫ-@ankündigen | 75 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 168 | pank=u-@Volk | 75 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 169 | arun=a-@Meer | 73 | Doubtful addition only; see evidence above. |
| 170 | tul=iya-@Versammlung | 73 | Doubtful EDHIL proposal; no single existing etymon with defensible sense correspondence established. EDHIL p(p). 897. |
| 171 | karimme@Tempel | 72 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 172 | takš=ul-@Frieden | 72 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 815. |
| 173 | ḫeku=r-@Fels | 71 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 174 | ariyaš=eššar@Orakel | 70 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 175 | nakk=i-@wichtig | 70 | Sense-matched EDHIL headword has no PIE reconstruction; no existing etymon established. EDHIL p(p). 593. |
| 176 | uzi=a-@Fleisch(?); Fleischopfer(?) | 70 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 177 | katti=ši | 69 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 178 | part=awar@Flügel | 69 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 646. |
| 179 | wašk=u-@Verfehlung | 69 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 180 | ašš=iye/a-@gut sein | 68 | EDHIL pp. 223-225: good-family derivative, not a justified match to sitting. |
| 181 | genz=u-@Schoß | 68 | Main addition; see evidence above. |
| 182 | innaraw=atar@Rüstigkeit | 68 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 183 | išḫaḫr=u-@Tränenstrom | 68 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 184 | wakš=ur@(Maßeinheit) | 67 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 185 | ḫalent=u-@Palast | 67 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 186 | ḫallir=i-@(Kultsänger) | 67 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 187 | ḫatr=išk-@mitteilen | 67 | Same writing/piercing family, EDHIL pp. 335-336; no defensible existing etymon with matching sense. |
| 188 | ḫulugann=i-@Kutsche | 67 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 189 | šarnikz=il-@Kompensation | 66 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 190 | šen=a-@Figur | 66 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 191 | panka=u-@Volk | 65 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 192 | piḫaššašš=a/i-@zum Blitz gehörig | 65 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 193 | tapriy=a-@tapri(t)-Funktionär | 65 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 194 | wapp=u-@Ufer | 65 | EDHIL reconstruction does not establish an existing etymon with matching form and sense. EDHIL p(p). 958. |
| 195 | ḫurt=ai-@Fluch | 65 | Doubtful addition only; see evidence above. |
| 196 | aš=@(übrig) bleiben | 64 | Doubtful EDHIL proposal; no single existing etymon with defensible sense correspondence established. EDHIL p(p). 214. |
| 197 | išḫam=išk-@singen | 64 | EDHIL pp. 393-394 requires the extended singing root *sh₂em-; mapping directly to binding would erase that root extension. |
| 198 | maršaštarr=(i)-@Entweihung | 64 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 199 | araḫzen=a-@umliegend | 63 | No supported headword/derivative connection to an existing etymon; incidental key matches rejected. |
| 200 | taganzip=a-@Erde | 63 | Main addition; see evidence above. |

## Verification

Regenerated with `UV_CACHE_DIR=/tmp/pie-uv-cache uv run python -I scripts/formula_search.py mapping --corpus hit` after checking `--help`. SHA-256 comparison of every mapping JSONL before/after: only `hit.jsonl` and `hit-doubtful.jsonl` changed. The temporary cache path avoids a sandbox restriction on the default uv cache.

Tests cover reviewed evidence preservation, unknown fields, stale IDs, duplicate decisions, missing/invalid pages, content filtering, precedence of main rows and overrides, and persisted tier separation.

Final stable-input full suite: `UV_CACHE_DIR=/tmp/pie-uv-cache uv run pytest -q` — **2,512 passed** in 364.54 seconds. The targeted Hittite/override/resolution run also passed all 42 tests. All pre-existing main and doubtful decisions retain their IDs; the differences are exactly the 23 main and seven doubtful additions listed above.


## 2026-10-25 — independent blind formation check

The independent blind check graded 60 main-tier rows: 51 correct, 7 partial,
2 wrong. Strict precision: **51/60 = 85.0% [73.9, 91.9]**; lenient precision:
**58/60 = 96.7% [88.6, 99.1]**. The doubtful tier was **8/8 faithful**.
These are pre-fix results, not a new evaluation of the repaired tables.

Reviewed overrides remove laḫ=u- (EDHIL pp. 512–513: *loh₂u-ei, rejecting
*leuh₃-) and tarna- (pp. 846–847: *trK-no-h₁/₃-, rejecting *terh₂-; compare
LIV² p. 635). No wash/crossing root is substituted. The lexicon's
*terḱh₂- release root differs from EDHIL's reconstruction; tarna- remains
unmapped. The te-/tar- row now covers **only te-**, *dheh₁-ti; the suppletive
*ter- component has no matching speech-root id (pp. 857–858, 870–871).

The source route now distinguishes complete formations from root identity.
Marked causatives, imperfectives and secondary presents cannot inherit an
incompatible base lexeme. The same check covers dictionary chains and lexicon
reflexes; reviewed overrides were corrected as well. A differing formation
uses existing root ancestors and retains its reconstruction/formation note.
Whole-form ambiguity and gloss gates still apply before root fallback.
Matching base formations, including middle *ḱei-to(r), remain lexemes.
The protection, sleep and filling families now use roots; fullness explicitly
uses *sewh₃-, never the misleading bear-family parent of *su-ne-H-ti.

Only the Hittite builder was run. Main rows: 334 → 331; doubtful rows: 8 → 8
(byte-identical). Hash comparisons of all mapping tables found only
`hit.jsonl` changed. No Tier 2/Tier 3 corpus or export regeneration.

The all-row pass also rejects kara/ep(p)- (EDHIL pp. 442–443):
*ghrobh₁-ei / *ghrbh₁-enti differs from both the mapped aorist and its
*h₂-root; no preferred *h₁-root exists in the lexicon.

A shared plural *-enti is insufficient to equate hi- and mi-formations;
comparison uses the lexeme’s canonical form and variants, not a shared
plural stem. Thus gulš- retains only its root (EDHIL pp. 492–493).

### Complete row change inventory

79 changed main-table rows: 58 id changes (including three removals), 21 formation-note changes only. No additions.

| Lemma | Before | After |
|---|---|---|
| akku=išk-@trinken | pie-lex-h1egwhti, pie-lex-h1exgwhti | pie-root-h1egwh-drink |
| anš=iye/a-@abwischen | pie-lex-h2omh1sey | pie-root-h2meh1-mow |
| anš=išk-@abwischen | pie-lex-h2omh1sey | pie-root-h2meh1-mow |
| app=išk-@fassen | pie-lex-h1epti | pie-root-h1ep-grab |
| arr=iye/a-@waschen | pie-root-h1erH-wash | same ids; formation note added |
| arr=išk-@waschen | pie-root-h1erH-wash | same ids; formation note added |
| arš=iya-2@fließen | pie-lex-h1ersti | pie-root-h1ers-flow |
| arš=iya-@fließen | pie-lex-h1ersti | pie-root-h1ers-flow |
| arš=nu-@fließen lassen | pie-lex-h1ersti | pie-root-h1ers-flow |
| gulš-@ritzen | pie-lex-kwelsti | pie-root-kwels-pull |
| išk=iye/a-@bestreichen | pie-root-segj-anoint | same ids; formation note added |
| išpar=anna-@hin-/ausbreiten | pie-lex-sporey | pie-root-sper-scatter |
| išpar=nu-@ausbreiten | pie-lex-sporey | pie-root-sper-scatter |
| išparr=e/a-@hin-/ausbreiten | pie-lex-sporey | pie-root-sper-scatter |
| išparr=iešk-@hin-/ausbreiten | pie-lex-sporey | pie-root-sper-scatter |
| kara/ep(p)-@fressen | pie-lex-ghrebh2t | unmapped |
| karp=iye/a-@heben | pie-lex-kerpt | pie-root-kerp-cut_off |
| karš=iye/a-@abschneiden | pie-lex-kerst, pie-lex-kerst-2 | pie-root-kers-cut |
| kiš=ā(e)-@kämmen | pie-lex-kesti | pie-root-kes-scrape |
| kur=išk-@schneiden | pie-root-kwer-do | same ids; formation note added |
| laḫ=u-@gießen | pie-lex-loh3wey | unmapped |
| link=išk-@schwören | pie-root-h1lengjh-assert_on_oath | same ids; formation note added |
| luk=eš-@allmählich hell werden | pie-lex-lewkt | pie-root-lewk-bright |
| lukk=išk-@anzünden | pie-lex-lewkt | pie-root-lewk-bright |
| mall=iye/a-@mahlen | pie-root-melh2-grind | same ids; formation note added |
| mall=išk-@mahlen | pie-root-melh2-grind | same ids; formation note added |
| mar=nu-@verschwinden lassen | pie-lex-mert | pie-root-mer-die |
| mau(š)-/mu-@fallen | pie-lex-myowh1ti | pie-root-myewh1-move |
| mer=nu-@verschwinden lassen | pie-lex-mert | pie-root-mer-die |
| naḫ=išk-@fürchten | pie-root-neh2-become_afraid | same ids; formation note added |
| papparš=išk-@(be)spritzen | pie-root-pers-sprinkle | same ids; formation note added |
| paḫš=@beschützen | pie-lex-peh2sti | pie-root-peh2-protect |
| paḫḫaš=@beschützen | pie-lex-peh2sti | pie-root-peh2-protect |
| paḫḫaš=nu-@beschützen | pie-lex-peh2sti | pie-root-peh2-protect |
| tarku=išk-@tanzen | pie-lex-terkwti | pie-root-terkw-turn |
| tarn=a-@lassen | pie-lex-trneh2ti | unmapped |
| taru=išk-@tanzen | pie-lex-terkwti | pie-root-terkw-turn |
| taruḫḫ=išk-@mächtig sein | pie-lex-terh2uti | pie-root-terh2-cross_over |
| te-/tar-@sprechen | pie-lex-dheh1t | pie-root-dheh1-do |
| tekkušš=iye/a-@zeigen | pie-root-dekws-show | same ids; formation note added |
| tekušš=iye/a-@zeigen | pie-root-dekws-show | same ids; formation note added |
| tepaw=aḫḫ-@gering machen | pie-root-dhebh-make_small | same ids; formation note added |
| tepaw=eš-@wenig werden | pie-lex-dhebhus | pie-root-dhebh-make_small |
| unuw=ā(e)-@schmücken | pie-lex-h3unewti | pie-root-h3ew-put_clothes_or |
| walaḫḫ=anna-@schlagen | pie-lex-welh3ti | pie-root-welh3-hit |
| walaḫḫ=išk-@schlagen | pie-lex-welh3ti | pie-root-welh3-hit |
| walḫ=anna-@schlagen | pie-lex-welh3ti | pie-root-welh3-hit |
| walḫ=išk-@schlagen | pie-lex-welh3ti | pie-root-welh3-hit |
| warr=ā(e)-@zu Hilfe kommen | pie-lex-h1orei | pie-root-h1er-arrive |
| warš=iya-@erfrischen | pie-lex-wersto | pie-root-wers-rise |
| warš=iye/a-@(ab)ernten | pie-root-wers-wipe | same ids; formation note added |
| warš=iye/a-@erfrischen | pie-lex-wersto | pie-root-wers-rise |
| wed=ā(e)-@(her)bringen | pie-root-wedh-lead | same ids; formation note added |
| wek=išk-@wünschen | pie-root-wekj-wish | same ids; formation note added |
| wer=iye/a-@rufen | pie-lex-weryeti | pie-root-werh1-speak |
| zinn=a-@beendigen | pie-lex-tineh1ti | pie-root-teyh1-get_hot |
| šanḫ-@suchen | pie-lex-senh2t | pie-root-senh2-obtain |
| šanḫ-@suchen/reinigen | pie-lex-senh2t | pie-root-senh2-obtain |
| šanḫ=išk-@suchen/reinigen | pie-lex-senh2t | pie-root-senh2-obtain |
| šaš=nu-@zum Schlafen veranlassen | pie-lex-sesti | pie-root-ses-rest |
| šašša=nu-@zum Schlafen veranlassen | pie-lex-sesti | pie-root-ses-rest |
| šunn=a-@füllen | pie-lex-suneHti | pie-root-sewh3-be_become_full |
| šunn=iye/a-@füllen | pie-lex-suneHti | pie-root-sewh3-be_become_full |
| šunn=išk-@füllen | pie-lex-suneHti | pie-root-sewh3-be_become_full |
| šup=@schlafen | pie-lex-swept | pie-root-swep-sleep |
| šupp=@schlafen | pie-lex-swept | pie-root-swep-sleep |
| šupp=a-@schlafen | pie-lex-swept | pie-root-swep-sleep |
| šuppar=iya-@schlafen | pie-root-swep-sleep | same ids; formation note added |
| šuppar=iye/a-@schlafen | pie-root-swep-sleep | same ids; formation note added |
| ḫan=iye/a-@schöpfen | pie-root-h2en-draw | same ids; formation note added |
| ḫan=išk-@schöpfen | pie-root-h2en-draw | same ids; formation note added |
| ḫappin=aḫḫ-@reich werden | pie-lex-h3epeno | pie-root-h3ep-work |
| ḫark=@umkommen | pie-lex-h3ergt | pie-root-h3erg-perish |
| ḫark=iya-@umkommen | pie-root-h3erg-perish | same ids; formation note added |
| ḫat=eš-@trocken werden | pie-lex-h2odey | pie-root-h2ed-dry |
| ḫat=nu-@zum Vertrocknen bringen | pie-lex-h2odey | pie-root-h2ed-dry |
| ḫatt=anna-@stechen | pie-lex-h2etox | pie-root-h2et-but |
| ḫuišš=@leben | pie-lex-h2westi | pie-root-h2wes-dwell |
| ḫuš=nu-@leben lassen | pie-root-h2wes-dwell | same ids; formation note added |

Validation: `uv run pytest -q tests/test_hittite_mapping.py`: **26 passed**;
`uv run pytest -q`: **2,578 passed** (378.93 seconds). Commands used
`UV_CACHE_DIR=/private/tmp/pie-uv-cache` because the default cache was sandbox-inaccessible.
The final all-row formation check found no remaining mismatches; post-suite
hashes again confirmed that only `hit.jsonl` changed among mapping tables.
