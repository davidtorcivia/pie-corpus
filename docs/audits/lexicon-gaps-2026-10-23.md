# Lexicon gaps from planner and Tier 2 reports (2026-10-23)

Planners reported meanings they could not express. For each one I looked for the best-supported PIE etymon: the lexicon's reflexes, LIV², NIL, and the handbooks (M&A = Mallory & Adams 2006, Beekes, Fortson, Ringe, Watkins 1995, West 2007).

All fixes are in `data/lexicon/overrides.jsonl` (26 lines, with branch and book evidence in each `note`). There is one new entry in `data/lexicon/supplement.jsonl` (kúHlos). Every new or changed spec has `spec_checked: true`. I checked the main cells by hand after the rebuild:

- **Nouns:** NOM, ACC, GEN and LOC SG; NOM and ACC PL. NOM.SG equals the headword in every case.
- **Verbs:** PRS or AOR 3SG/3PL, IMP.2SG, and PTCP.

After the rebuild, the 27 touched entries all have an accented headword. 25 are inflecting lexemes and are usable. The other 2, ḱóm and h₁éǵʰs, are indeclinable adverbs, which make_slice offers as ADV. Four test plans that use the new words pass `check_plan` and realize. `uv run pytest -q` reports **2163 passed**.

The gloss tag is the first fragment of `meaning`, i.e. what the interlinear shows. It is listed in the table.

## Added or fixed

| meaning | lex_id | form | spec summary | evidence | status |
|---|---|---|---|---|---|
| peace | pie-lex-kwyeh1tis | kʷyéh₁tis | proterokinetic ti-stem f: -tis, gen. kʷih₁téys, pl. kʷyéh₁teyes (checked) | OPers. šiyāti-, Av. šāiti-; Lat. quiēs (t-stem); M&A ch. 21 *kʷih₁- 'rest, quiet'; LIV² p. 393 | added. Tag "rest": calm repose, not treaty-peace (gloss says so) |
| elder / old man | pie-lex-gjerh2onts | ǵérh₂onts | table amphikinetic nt-adj (unchanged) | Gk γέρων, Ved. járant-, Arm. cer; M&A ch. 12 *ǵerh₂-ont- 'old man'; Beekes | gloss fixed: "old, aged; as noun (m.): old man, elder" |
| oath (swear) | pie-lex-h1oytos | h₁óytos | thematic m | OIr. óeth, Goth. aiþs (Celtic, Germanic); M&A ch. 17 | added (pos noun, m). No two-branch verb 'swear' (h₁lenǵʰ- 'swear' is Hittite only) |
| lie / deceive | pie-lex-dhrewght | dʰréwgʰt | root aorist (unchanged) | LIV² p. 157; Ved. druh-, Av. druj-, OHG triogan | gloss "to deceive, lie to" |
| lie / deceive (present) | pie-lex-dhrughyeti | dʰrugʰyéti | thematic yé-present | LIV² p. 157 *dʰrugʰ-i̯é- (Ved. drúhyati); root also Germanic | gloss added |
| a lie | pie-lex-dhrowghos | dʰrówgʰos | table thematic m | Av. draoga-, OPers. drauga-; OHG gitroc | gloss "lie, deceit, falsehood" |
| worm | pie-lex-kwrmis | kʷŕ̥mis | i-stem m like h₁n̥gʷnís: gen. kʷr̥méys, pl. kʷŕ̥meyes (checked) | Ved. kŕ̥mi-, Lith. kirmìs, OIr. cruim, OCS črьvь, Alb. krimb; M&A ch. 9 | added (was unusable, gloss list was garbled) |
| praise | pie-lex-gwrneHti | gʷr̥néHti | nasal present, 3pl. gʷr̥nHénti | LIV² p. 210 *gʷr̥-né/n-H- (Ved. gṛṇā́ti); root also Baltic (Lith. girti) | gloss added |
| song of praise | pie-lex-h1erkwos | h₁erkʷós | table thematic m | Ved. arká-, Arm. erg, Toch. B yarke; M&A ch. 21 | gloss fixed (was a parse fragment "something that does or is subject to:") |
| call | pie-lex-gjhuHeyeti | ǵʰuHéyeti | thematic éye-present | LIV² p. 180 *ǵʰuH-éi̯e- (Ved. hváyati, Av. zbaiieiti); root also OCS zъvati | gloss added. kelh₁- not used: LIV² has it as 'entice, deceive' |
| sing | pie-lex-kh2neti | kh₂néti | thematic present | Lat. canō, OIr. canaid; LIV² p. 342 *kan- (*kán-e-) | gloss added. LIV writes the stem *kán-e-; the lexicon follows Wiktionary keh₂n- |
| milk (verb) | pie-lex-h2melgjti | h₂mélǵti | table root present (unchanged) | Gk ἀμέλγω, Lat. mulgeō, OE melcan, Lith. mélžti; LIV² p. 279; Beekes | gloss "to milk" (the old gloss "to be milking" missed the keyword) |
| smile | pie-lex-smexyti | smḗyti | Narten root present: 3pl. sméyn̥ti, ipv. sméydʰi, ptcp. sméyn̥ts (checked) | LIV² p. 568; Ved. smáyate, Latv. smiêt, OCS smьjati sę; Gk μειδιάω | added (was unusable) |
| thunder | pie-lex-stonh2eyeti | stonh₂éyeti | thematic éye-present | LIV² p. 597 *(s)tonh₂-éi̯e- (Ved. stanáyati, Lat. tonāre) | gloss added (intransitive) |
| spread | pie-lex-strneh3ti | str̥néh₃ti | nasal present, weak stem str̥nh₃- (checked) | LIV² p. 599; Ved. stṛṇā́ti, Gk στόρνυμι, Lat. sternō | gloss and spec fixed: the table's weak stem str̥nh₃é- gave 3pl. str̥nh₃énti and ipv. str̥nh₃édʰi |
| gape | pie-lex-gjhh2ieh2yeti | ǵʰh₂iéh₂yeti | thematic present | Lat. hiāre, Lith. žióti, OCS zijati; M&A ch. 21 *ǵʰ(h₁)iy-eh₂- | gloss added. M&A write h₁ where the lexicon has h₂ |
| adorn | pie-lex-pinekjti | pinéḱti | nasal present, 3pl. pinḱénti | LIV² p. 465 *pi-né/n-ḱ- (Ved. piṃśáti, Lat. pingō, Toch. pik-); M&A ch. 20; NIL | gloss added |
| back | pie-lex-kuHlos (supplement) | kúHlos | thematic m | OIr. cúl, Lat. cūlus, Ved. kū́la-; M&A ch. 11 | added. Only Celtic means 'back' proper. No root link (*kewH- 'be bent' is not in the lexicon) |
| sow | pie-lex-seh1yeti | séh₁yeti | thematic ye-present | LIV² p. 517 *séh₁-i̯e- (Goth. saian, Lith. sė́ti, OCS sějati) | gloss added |
| hearth | pie-lex-h2eHsh2 | h₂éHsh₂ | proterokinetic h₂-stem f like gʷénh₂/gʷnéh₂s: gen. h₂Hséh₂s, asigmatic nom. (checked) | Hitt. ḫašša-, Lat. āra, Osc. aasaí; M&A ch. 13; Beekes | added (was unusable). M&A write an eh₂-stem; the lemma is an h₂-stem. This was a deliberate choice, explained in the note |
| smith | pie-lex-dhh2bhros | dʰh₂bʰrós | thematic m | Lat. faber, Arm. darbin 'smith'; M&A ch. 17 *dʰabʰros 'craftsman' | added. Tag "craftsman" |
| friend | pie-lex-priHos | priHós | table thematic adj (unchanged) | NIL p. 568 *priH-ó-: Ved. priyá- 'dear; m. friend', Av. friia-; MW rhydd, Goth. freis 'free' | gloss "dear, beloved, one's own; as noun (m.): friend" |
| truth / true | pie-lex-h1sonts | h₁sónts | athematic nt-adjective (as the participle engine): gen. h₁sn̥tés, f. h₁sn̥tíh₂, n. h₁sónt (checked) | Hitt. asānt- 'true', Gmc *sanþaz 'true' (OE sōþ), Ved. sánt-; M&A ch. 20 *h₁sónt- 'real, true'; NIL; Ringe ch. 4 | changed from kind form to word, pos adj. Gloss "real, true; n. as noun: the truth". LOC.SG h₁sn̥ti is unaccented, the same as the engine's participle |
| beast | pie-lex-gjhwexr | ǵʰwḗr | lengthened grade throughout, accented oblique endings (like h₃rḗǵs): gen. ǵʰwērés, pl. ǵʰwḗres (checked) | Gk θήρ (θηρός), Lith. žvėrìs, OCS zvěrь, Lat. fera; M&A ch. 9 | added (the er-stem rule gave zero-grade ǵʰwr̥-; unusable before) |
| treat / heal | pie-lex-mexdeti | mḗdeti | thematic present (unchanged) | Lat. medērī, Av. vīmad- 'physician' (Watkins 1995 ch. 58; M&A ch. 11); this stem Gk μέδομαι, Gmc *metaną; LIV² p. 423 | gloss "to heal, treat (the sick); take measures for, attend to". LIV has a Narten present; the lexicon stem is thematic |
| together | pie-lex-kjom | ḱóm | indeclinable (ADV) | Lat. cum/com-, OIr. com-, Gmc *ga-, Lith. sù; M&A ch. 18 | gloss "with, together (with); beside, near" |
| out | pie-lex-h1egjhs | h₁éǵʰs | indeclinable (ADV) | Gk ἐξ, Lat. ex, OIr. ess-, OCS iz; M&A ch. 18 | gloss "out, out of, from". Not *nis, which is Indo-Iranian only |

## Skipped

| meaning | candidate | why |
|---|---|---|
| enemy / foe | póyḱos (pie-lex-poykjos-2): OIr. óech, Gmc *faihaz | Two branches in Wiktionary, but no handbook covers it. gʰóstis 'guest; stranger, enemy' is already usable, but only Latin has the 'enemy' sense |
| answer | none | No PIE etymon; the daughters' words are later formations |
| weapon | none | M&A ch. 15: only a Germanic–Tocharian isogloss (*wēben); *h₂/₃isis 'sword' (Lat. ēnsis, Ved. así-) is not in the lexicon |
| wise | ǵn̥h₃rós 'knowing' | Its reflexes don't mean 'wise' (Ved. jārá- 'lover', Lat. gnārus 'knowing'). *widwṓs (perfect participle) is not in the lexicon, and the engine has no perfect participle. For 'know', wóyde, ǵn̥néh₃ti and ǵnéh₃t are already usable |
| foolish | stl̥to- | Bound stem, Latin and Germanic only. M&A has only regional words (OCS ludъ etc.) |
| fox | h₂wlōpēḱs, h₂wl̥pis | Irregular, taboo-deformed set (Gk ἀλώπηξ, Lat. volpēs, Ved. lopāśá-, Lith. lãpė). The candidate headwords are unaccented, so the slice gate drops them, and an override cannot change `form` |
| fly (insect) | mus- | M&A ch. 9 *mus- 'fly, gnat', but each branch suffixes it differently (Lat. musca, Gk μυῖα, Lith. musė). The lemma is a bound stem with no inflectable reconstruction |
| unageing | (no entry) | West 2007 ch. 2: Ved. ajára- and Gk ἀγήραος match only partly in etymology (the Greek is built on the s-stem γῆρας) |
| bread | none | No PIE word. Lith. dúona 'bread' < *dʰoHnéh₂ 'grain' |
| child | téḱnom, bʰornom, putló- | téḱnom is Greek only; bʰornom has an unaccented headword; putló- is not in the lexicon. ǵénh₁mn̥ 'offspring' is usable |
| fetter | *ped-i-, *ped-eh₂ | NIL gives a different formation in each branch (Lat. compēs, Gk πέδη, Gmc *feturō); its two-branch *(-)ped-i- is marked uncertain |
| milk (noun) | h₂mélǵos | Only OIr. melg; the Germanic *meluk- is a different formation |
| house-lord compounds | - | Out of scope |

## Limits found

- Overrides cannot change `form`. That leaves good etyma with unaccented Wiktionary headwords out of every slice, because of make_slice's accent gate. Examples are weh₁ros 'true' (Lat. vērus, OIr. fír, Gmc *wēraz), wr̥mis 'worm', gurnos 'back' and bʰornom 'child'. A `form` override in `pie/lexicon.py` would let them in.
- pie-lex-h2eti 'back, again, away' (an adverb) gets the thematic-present verb rule, because its pos is null and its form ends in -eti. I did not change it.
- **make_slice ranks override glosses below Wiktionary ones.** `lx.meaning()` now returns source `override` or `supplement` for every entry touched here, and make_slice only fully trusts `wiktionary`:
  - The CORE_VERBS path requires a Wiktionary gloss. So h₂mélǵti is still not offered automatically, even though "milk" is a core verb.
  - The random fill requires a Wiktionary gloss or at least 3 attested languages. These ten fall short: dʰréwgʰt (0), kúHlos (0), dʰrugʰyéti (1), ǵʰuHéyeti (1), dʰrówgʰos (2), kh₂néti (2), séh₁yeti (2), dʰh₂bʰrós (2), ǵʰwḗr (2), mḗdeti (2). They reach planners only through batch keywords.
  - Keyword hits sort override glosses after Wiktionary glosses, so they are cut first when `--size` is tight.

  Fix (in scripts/, not done here): count `override` as dictionary-grade in make_slice, or add the planner-reported ids to CORE_NOUNS and CORE_VERBS.
- **Two 'true' adjectives.** h₁sn̥tyós (a CORE_NOUN; Indo-Iranian only per NIL) and h₁sónts ('real, true'; three branches) will both be offered. The slice dedup does not merge them, because their glosses differ. h₁sónts is the better-supported one.
