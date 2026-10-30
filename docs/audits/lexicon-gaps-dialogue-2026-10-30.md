# Lexicon gaps for the dialogue planners and the translator (2026-10-30)

The t3b dialogue planners and the English → PIE translator had no usable word for 15 everyday concepts: anger/angry, story/tale, bread, milk (noun), hunger/hungry, grandmother, forest, play, weave/weaver, cloth, cup, pot, knife, feast, sad. For each one I worked down the ladder and stopped at the first rung that held:

1. An existing lexicon entry. Its gloss or spec is fixed in `data/lexicon/overrides.jsonl`, and the lexicon is rebuilt.
2. A project reconstruction in `data/lexicon/project_reconstructions.jsonl`: one formation in at least 2 branches, with handbook citations.
3. A Tier 3b neologism in `data/lexicon/neologisms.jsonl`, derived by the engine.

Sources: M&A = Mallory & Adams 2006, plus Kroonen 2013, de Vaan 2008, Matasović 2009, Beekes 2010, Derksen 2008, Martirosyan 2010, Kloekhorst 2008, LIV², EWAia, Cheung 2007 and Fortson 2010. Each was read in `raw/books/text/`, and each override `note` names its source.

## Result

| concept | rung | lex_id | form | gloss (tag first) | evidence | rejected, and why |
|---|---|---|---|---|---|---|
| anger / angry | 1 (gloss) | pie-lex-ghremeti | gʰrémeti | to be angry, rage; to roar, rumble | LIV² *gʰrem-: present *gʰrém-e-, YAv. gramant- 'wütend'. Cheung s.v. *gram 'to thunder, roar; to anger' (YAv. gram- 'ergrimmen', Sogd. 'get angry'). Gk χρεμετίζω 'neigh'. Participle gʰrémonts 'raging, angry' = YAv. gramant- | ḱéh₂dos 'care, grief; hatred': Go. hatis also means 'wrath', but the word is already 'grief'. *bʰorgʷos 'angry' (M&A §20.6): Martirosyan rejects Arm. bark 'angry' as a cognate, which leaves OIr. borb and Latv. bargs. piḱtós: Baltic only. gʰrm̥tós (Av. graṇta- 'angry'): Avestan only |
| anger (to make angry) | 1 (gloss) | pie-lex-ghromeyeti | gʰroméyeti | to anger, make angry, provoke | Kroonen s.v. *gramjan- < *gʰrom-eie- (Go. gramjan, ON gremja, OE gremian, OHG gremmen). LIV² Kaus. ?*gʰrom-éi̯e- | — |
| story / tale | 2 | pie-proj-spelom | spélom n. | story, tale, legend | Same formation in PGmc *spellą 'story, tale, legend' (Go. spill, OE spell; Kroonen *spel(H)-o-) and Arm. aṙaspel 'myth, tale, fable' (Martirosyan: aṙ- + *spel-, the same structure with OHG bī-spel). Root level only: Alb. fjalë 'word; tale', Gk ἀπειλή (doubtful). M&A §21.2. Sound law: 1 check (PGmc s-). The accent is projected (as in wérǵom). Kroonen lists the Armenian word at root level only, and the Gmc -ll- is not explained (laryngeal?) | A calque of wékʷos 'word' as Gk ἔπος: not needed, because rung 2 holds |
| bread | 3 (calque) | pie-neo-bread | dʰoHnéh₂ | bread | Base dʰoHnéh₂ 'grain' (usable table). Model: Lith. dúona 'bread' from the same word. M&A §10.3: the word means grain prepared as food, not grain in the field (also NPers. dāna, Skt. dhānā́s, Toch. B tāno) | No PIE word for bread. bʰéh₃gos (Phryg. βεκός 'bread', Hdt. 2.2): one branch, and Fortson §20.9 flags the link with *bʰeh₃g- 'bake'. Lat. pānis: no etymology (de Vaan). OIr. bairgen < *bʰars- 'barley': a bound stem |
| milk (noun) | 1 (gloss) | pie-lex-h2melgjos | h₂mélǵos n. | milk | Matasović s.v. *melgos- 'milk' (OIr. melg, a glossary word; PIE *h₂melǵ-). Nouns of the root mean 'milk' in Germanic (*meluk-, a root noun: Kroonen), Celtic (*mlixto-), Slavic and Tocharian (M&A §16.3) | **This reverses the 2026-10-23 skip ("single branch").** h₂mélǵos is the only inherited candidate with an engine shape. *ǵlákt (Gk γάλα, Lat. lac) is irregular and has no entry. dʰédʰh₁i 'curds' (Skt. dádhi, OPr. dadan 'milk') has no spec (i/n heteroclite). So the gloss is given and the single branch is stated |
| hunger | 1 (gloss) | pie-lex-gwoldhos | gʷoldʰós m. | hunger | LIV² *gʷeldʰ- note: OCS gladъ, Ru. gólod 'hunger' < *gʷoldʰ-o-. Derksen s.v. *gȏldъ m. o (c) 'hunger'. The oxytone fits Slavic AP (c). The formation is Slavic only; the root is also Indo-Aryan (Skt. gṛ́dhyati 'be greedy') | kn̥krós (PGmc *hungru-): Kroonen gives a ru-stem *kn̥k-ru-, not the thematic headword, and the engine has no ru-stem |
| hungry (to be hungry) | 1 (gloss) | pie-lex-kenketi | kénketi | to be hungry, feel hunger | M&A §16.1 *kenk- 'hunger' (Gk κέγκει 'is hungry'). Kroonen s.v. *hungru- (κέγκει < *kenk-e-; Lith. keñkras 'emaciated'). "I am hungry" is kénkoh₂. No adjective reconstructs, so the translator's ("hungry", adj) stays None | LIV² *kenk- is 'hang', another root |
| grandmother | 2 | pie-proj-h2enHos | h₂énHos f. | grandmother | Same thematic formation in Hitt. ḫanna- (c., a-stem) 'grandmother' (Kloekhorst *h₂enHo-) and Arm. han, o-stem, 'grandmother' (Martirosyan). Root level: Lat. anus 'old woman', OHG ana, OPr. ane, Lith. anýta, Gk ἀννίς. M&A §12.3. Sound law: 2 checks (Gk, Lat. a- from *h₂e). Notes: the -H- is Kloekhorst's (Martirosyan writes plain *h₂en-); gender f and the accent are projected | M&A's *h₂euh₂iha- (Lat. avia, Alb., Gk), the feminine of h₂éwh₂os: it has no lexicon entry, and the eh₂/ih₂ shapes are blocked for coinages. Rung 2 holds first |
| forest | 3 (calque) | pie-neo-forest | dóru | forest, wood (trees standing together) | Base dóru 'tree' (usable). Model: OIr. fid 'tree; wood; forest' and PGmc *widu- 'tree; wood' (Kroonen, Matasović), E wood | **Rung 1 does not hold.** pie-lex-h1widhh1us *(h₁)widʰ-u- 'tree, wood; forest' (Gmc, Celtic: Kroonen, Matasović) is the inherited word. It is now glossed by override, but no source gives an accent and the engine has no spec for the unaccented u-stem. So it stays out of the pool, like debt, grey and yew (test_forest_stays_unoffered_without_an_accent). Rung 2 may not duplicate an existing word |
| play | 1 (gloss) | pie-lex-loygeti | lóygeti | to play, frolic, leap about | Kroonen s.v. *laikan- < *lóig-e- (ON leika 'to play', OE lācan 'to play', Go. laikan 'jump for joy'). The 'play' sense is Germanic only; Lith. láigyti 'run about' is another stem | leyd-: Lat. lūdō and Gk λίζω both mean 'play' (M&A *loid-), but each continues a different present. Wiktionary's léloydti is a Latin-only reconstruction; lidyéti rests only on λίζω (Hesych.). I preferred one formation that Kroonen reconstructs with a clear 'play' sense |
| weave | 1 (gloss) | pie-lex-teksti | téksti | to weave, plait | LIV² 2.*tek- 'weben, flechten': a frozen desiderative root present *teks-/tks- (Hitt. takkeszi / takšanzi; Lat. texō 'weave'; MHG dehsen). 3 branches; athematic, as in Hittite | webʰnyeti 'to weave' (Gk ὑφαίνω, Alb. vej; reflex-confirmed) has no accent (P10). wébʰeti is Germanic only |
| weaver | 3 (derivative) | pie-neo-tektoxr | téktōr m. | weaver | tek- (e-grade, root accent) + -tōr. Model: Lat. textor 'weaver' to texō, Gk ὑφάντης. Engine cells: gen. tktrés, pl. téktores | — |
| cloth | 3 (derivative) | pie-neo-tekmn | tékmn̥ n. | cloth, woven fabric | tek- + -mn̥ 'what is woven' (as wésmn̥ 'garment'). Model: Gk ὕφασμα 'woven fabric' (Od.), Lat. textum. Gen. tkméns | wébʰos (Gk ὕφος): Beekes calls ὕφος a late back-formation. *peh₂nos (Lat. pannus, Go. fana): de Vaan suspects loanwords. *los- 'rags' (M&A): no entry, and the meaning varies. wésmn̥ is 'garment', not cloth |
| cup | 1 (gloss) | pie-lex-peh3tlom | péh₃tlom n. | drinking vessel, cup | M&A §15.1 *poh₃tlom 'drinking vessel' (Lat. pōculum 'cup', Skt. pā́tra-). The word was already usable with the reflex-confirmed gloss "drinking vessel"; it only lacked the keyword | gewlos 'vessel, bowl': Germanic only and unaccented |
| pot | 1 (gloss) | pie-lex-kweros | kʷéros m. | kettle, cooking pot, cauldron | Kroonen s.v. *hwera- 'kettle' < *kʷer-o-. The root noun 'cooking vessel' is in 4 branches: Skt. carú- (*kʷer-u-), OIr. coire, W pair (*kʷor-io-), OCS črěnъ. The thematic formation itself is Germanic only | kʷr̥yos (PCelt. *kʷaryos): unaccented. The 2026-10-28 "pot: no cognate set" covered *h₂/₃ukʷ- only |
| knife | 1 (form + gloss) | pie-lex-kjstrom | ḱéstrom n. | knife, cutting tool | de Vaan s.v. castrō: PIE *ḱs-tro- 'knife'; Skt. śástra- n. 'knife, dagger' < *ḱe/os-tro-; Alb. thadër 'double-sided axe'; Lat. castrāre < *kastrom. EWAia s.v. ŚAS: śástra- 'Messer, Schwert' (root-accented; śastrá- 'Anrufung' is another word). **The headword changes grade:** the full grade and root accent come from Skt. śástra-, as in the instrument nouns h₂érh₃trom and ḱléwtrom (precedent: yókʷr̥ → yḗkʷr̥). Wiktionary's ḱstrom (Latin's zero grade, with no vowel to accent) stays a variant, and the id leaves accent_unresolved.json | *h₂n̥sis (Lat. ēnsis, Skt. así-): de Vaan and EWAia doubt the equation. kelHtrom (Lat. culter): Latin only and unaccented. *wēben: Germanic and Tocharian only, and no entry |
| feast | 1 (gloss) | pie-lex-dh2pnom | dh₂pnóm n. | feast, sacrificial meal | M&A §16.1 *dapnom 'sacrificial meal' (Lat. daps, ON tafn, Gk δαπάνη, Arm. tawn 'feast'). Martirosyan s.v. tawn: Lat. damnum and OIc. tafn both continue *dap-no-; Arm. *dh₂p-ni- | déh₂ps (Lat. daps): no spec |
| sad | 1 (pos + gloss) | pie-lex-lugjros | luǵrós adj. | sad, mournful, wretched | Beekes s.v. λευγαλέος: λυγρός 'wretched, unhappy, sore, baneful' (Il.); Lat. lūgeō 'to be sad' is semantically closest. M&A §21.3 *leug- (Lat. lūgeō 'mourn', Gk λευγαλέος 'sad', Toch. B lakle 'suffering'). The -ró- formation is Greek only. Beekes and LIV² write a plain velar; the Wiktionary headword's ǵ is kept | ḱéh₂dos, h₂énǵʰos: nouns that are already usable ('grief', 'distress'); no adjective formation |

## What changed

- **Overrides (13 rows).** There are gloss overrides for gʰrémeti, gʰroméyeti, kénketi, gʷoldʰós, h₂mélǵos, lóygeti, téksti, péh₃tlom, kʷéros, dh₂pnóm and h₁widʰh₁us. ḱstrom also gets a form override, to ḱéstrom, and luǵrós gets `pos: adj`. Then I rebuilt with `build_lexicon.py`, `classify_lexicon.py` and `build_glosses.py`. The rebuild was first run on a scratch copy and checked byte-identical to HEAD before the overrides went in. After it, `inflection_specs.jsonl` changes in exactly two rows:
  - ḱstrom → ḱéstrom (thematic neuter)
  - luǵrós (thematic noun → thematic adjective)

  `lexicon.jsonl` changes in exactly the 13 overridden ids. Neither spec-changed id occurs in corpus/ or data/generation/, so no realized text changes. pie-lex-kjstrom left `accent_unresolved.json`; the noun/shape:thematic-neuter group went from 130 lexemes / 2470 cells to 129 / 2451.
- **Project reconstructions (round 3):** pie-proj-spelom and pie-proj-h2enHos.
- **Neologisms (39 → 43):** pie-neo-tektoxr, pie-neo-tekmn, pie-neo-bread and pie-neo-forest, filled by `pie.neologism --fill`. The first 39 rows are unchanged.
- **Reachability.** The 12 rung-1 words and 2 rung-2 words are added to `scripts/make_slice.py` TIER3B_INHERITED. Every new gloss carries its concept word for `keyword_hit`. I also added English → lexeme entries in `pie/translator/lexmap.py` OVERRIDES: rage, anger (verb), hunger (noun and verb), milk, play, weave, cup, pot, kettle, knife, feast, sad, story, tale and grandmother. The translator's `Lexicon.load()` has no neologisms, so bread, forest, weaver and cloth reach only the Tier 3b planners. The translator's map cache rebuilds by itself: its key hashes lexicon.jsonl, inflection_specs.jsonl and project_reconstructions.jsonl (pie/translator/analyze.py `_INPUTS`).
- **Pool.** Offered by default goes from 1,378 to 1,391; usable specs go from 4,931 to 4,933.

## Cells checked

| word | cells |
|---|---|
| ḱéstrom | ḱéstrom, gen. ḱéstrosyo, loc. ḱéstroy, pl. ḱéstreh₂ |
| luǵrós | m. luǵrós / luǵróm, f. luǵréh₂, n. luǵróm |
| gʷoldʰós | gʷoldʰóm, gʷoldʰósyo, pl. gʷoldʰṓs |
| h₂mélǵos | gen. h₂mélǵesos, pl. h₂mélǵesh₂ |
| dh₂pnóm | gen. dh₂pnósyo, pl. dh₂pnéh₂ |
| kʷéros | kʷérom, kʷérosyo |
| péh₃tlom | péh₃tlosyo |
| téksti | 3pl. tksénti (Hitt. takšanzi), ipv. tksdʰí |
| gʰrémeti | 3pl. gʰrémonti, ptcp. gʰrémonts |
| gʰroméyeti | gʰroméyonti |
| kénketi | kénkonti, ipv. kénke |
| lóygeti | lóygonti |
| spélom | gen. spélosyo, pl. spéleh₂ |
| h₂énHos f. | h₂énHom, h₂énHosyo |
| téktōr | téktorm̥, gen. tktrés |
| tékmn̥ | gen. tkméns, pl. tékmn̥h₂ |

## Tests

New tests:

- `tests/test_vocab_push.py`: a DIALOGUE keyword → lexeme test (offered, override gloss, in TIER3B_INHERITED), the knife and sad paradigms with a realized sentence, and the forest accent gate.
- `tests/test_project_reconstructions.py`: ROUND3 in the policy, realize and slice tests, plus round-3 paradigms.

Runs:

- The named suites, plus test_glosses, test_vocab_push, test_accent_invariant, test_accent_policy, test_planner_accent and test_translator: 153 passed.
- test_alt_status, test_conversation_gaps, test_engine_queue_wave1, test_engine_sweep, test_export, test_export_chat, test_realize, test_u_adjective_alternatives and test_validate, run on the scratch tree: 245 passed.
