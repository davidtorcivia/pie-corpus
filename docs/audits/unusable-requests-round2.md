# Wave-1 planner requests, round 2: existing, unusable, unoffered, neologism

Date: 2026-10-28. Companion to `docs/lexicon-project-reconstructions.md` ("Round 2").

For each word the wave-1 planners could not say, this file records:

- an existing lexeme, if there is one;
- why `scripts/make_slice.py` does not offer it;
- the fix.

"Offered" uses make_slice's pool rule: the lexeme has a usable spec, is not blocklisted, passes `planner_accent_ok`, is not in an `eval_root` family, and has a dictionary gloss. A derived gloss is offered only with `--derived`, and only for a transparent suffix or reflexes in 2+ branches. Causes are taken from `Lexicon.load()` on this commit.

**Scope.** Fixing unusable causes belongs to the engine agent (separate worktree). This file does not edit `lexicon.jsonl`, `inflection_specs.jsonl` or `overrides.jsonl`.

## 1. The requests

| Request | Status | Lexeme(s) | Cause / action |
|---|---|---|---|
| judge | **none** | — | Tier 3b neologism (§3) |
| witness | exists, **unusable** | `pie-lex-widtres` *widtrés* "viewer, witness" | `unknown:noun-shape`, no reflexes. Engine: give a spec (Gk ἵστωρ points to a *-tor-* agent noun *wid-tor-*) or keep it out; else neologism (§3) |
| owe | exists, **unoffered** | `pie-lex-dhlgheti` *dʰl̥gʰéti* (thematic present, usable spec) | Derived gloss only ("to owe" [-eti]); offered with `--derived`, keyword `owe`. Celtic only (OIr. *dligid*). A gloss override would make it default |
| debt | exists, **unusable** | `pie-lex-dhlghos` *dʰl̥gʰos* | Accent unresolved and derived gloss. Reflexes in Germanic and Balto-Slavic (Go. *dulgs*, OCS *dlъgъ*). Engine: accent plus gloss override "debt" |
| sell | exists, **usable, offered** | `pie-lex-perh2t-2` *pérh₂t* "to sell" (root aorist) | Keyword **`sell`**. Also `pie-lex-prneh2ti` *pr̥néh₂ti* (Gk πέρνημι; derived gloss, `--derived`) |
| swear (verb) | exists, **unoffered** | `pie-lex-h3mneh3ti` *h₃m̥néh₃ti* (Gk ὄμνυμι), `pie-lex-h3emh3ti` *h₃émh₃ti* (Indic) | Both have usable specs but only the derived root gloss "to grab, … touch" [-ti]. Each is single-branch with a non-transparent suffix, so they are never offered, even with `--derived`. Fix: gloss override "to swear (an oath)" on *h₃m̥néh₃ti*. The root *h₂wert-* "swear" is held out (`eval_root`) |
| oath (noun) | exists, **usable, offered** | `pie-lex-bhoydheh2` *bʰoydʰéh₂* (core noun), `pie-lex-h1oytos` *h₁óytos* | Keyword **`oath`** |
| sick / illness | **added** `pie-proj-swerghos` *swérgʰos* "illness" | Also exists: `pie-lex-ligos` *ligós*, `pie-lex-loygos`, `pie-lex-ligeh2` (*leyg-* "illness") | *ligós* has a derived gloss and Albanian and Greek reflexes, so it is offered with `--derived`, keyword `illness`. *ligeh₂-* is `unknown`. No adjective "sick" (§3) |
| spring (season) | exists, **usable, offered** | `pie-lex-wosr` *wósr̥* "spring (season)" | Keyword **`spring`**. It also matches *bʰréh₁wr̥* "well, spring" and *ként* "spring forth", so planners should check the gloss |
| grave / burial | root **held out** | `pie-root-dhembh-bury` *dʰembʰ-* "bury" | `eval_root`: the family is reserved for the cognate benchmark, so nothing from it can be offered. Neologism from another root (§3) |
| long | exists, **usable, offered** | `pie-lex-dlh1ghos` *dl̥h₁gʰós*, `pie-lex-dweh2ros` *dweh₂rós* "long, far" | Keyword **`long`**. `pie-lex-dlonghos` is accent-blocked |
| wait | **none** | `pie-lex-meneti` *méneti* "to stay, remain" | Derived gloss; offered with `--derived`, keyword `stay`/`remain`. Gk μένω also means "wait for", so a gloss override "to stay, wait (for)" is the cheapest fix. Hitt. *tuḫḫušiya-* "wait, look on calmly" is single-branch (LIV *th₂us-*). See §3 |
| mounted (on horseback) | **added** `pie-proj-reydheti` *réydʰeti* "to ride" | — | "Mounted" is the participle *réydʰonts* "riding". No adjective reconstructs (§3) |
| beak | **none** | — | Round 1 rejected it (every "beak" word is one-branch). Neologism (§3) |
| sing | exists, **usable, offered** | `pie-lex-kh2neti` *kh₂néti* "to sing, chant" | Keyword **`sing`**. Also `pie-lex-gweHyeti` *gʷéHyeti* (Balto-Slavic and Indo-Iranian; derived gloss "to sing" [-yeti]; offered with `--derived`). The roots *h₂weyd-* and *kan-* have no lexemes (the engine agent's item) |
| love (verb) | exists, **usable, offered** | `pie-lex-wenHt` *wénHt* "to grow fond of, come to love" (aorist only) | Keyword **`love`**. "Dear": `pie-lex-lewbhos` (core), `pie-lex-priHos`, and the new `pie-proj-keh2ros`. Present stems of *wenh₁-* exist only with derived glosses (*wn̥h₁sḱéti*, *wn̥h₁néwti*; `--derived`) |
| thank / praise of a giver | praise exists, **usable, offered** | `pie-lex-gwrneHti` *gʷr̥néHti* "to praise, extol (in song)" (conversation list); `pie-lex-h1erkwos` *h₁erkʷós* "song of praise" | Keyword **`praise`**. "Thank": no cognate set (§3) |
| here | exists, **closed class** | `pie-lex-kje` *ḱe* (particle, indeclinable) | Round 1: never offered as an adverb, because its POS is particle and it is enclitic. See §3 for the candidate *h₁idʰé* |
| grey | **added** `pie-proj-kjasnos` *ḱásnos* | Also exists: `pie-lex-polHwos` *polHwos* (*pelH-wo-*: PGmc *falwaz*, Lith. *pal̃vas*, OCS *plavъ*), `pie-lex-polHnos`, `pie-lex-plHkos` | *polHwos* has no accent (the `accent` gate) and a derived gloss. It is the better-attested "grey/fallow" and deserves an override (accent plus gloss "grey, pale"). *ǵʰreh₁-wo-* (PGmc *grēwa-*) is Germanic only (Kroonen) |
| man / human (*mon-*, *manu-*) | exists, **unusable** | `pie-lex-mon` *mon-* (bare stem, `unknown`); `pie-lex-gjhmox` *ǵʰmṓ* "human" (Lat. *homō*, Lith. *žmuõ*, Germanic) | *mon-* has no paradigm. *ǵʰmṓ* is `shape:n-stem-hk` (systemic). Usable now: `pie-lex-mortos` *mórtos* "mortal, man" (keyword **`mortal`**), `pie-lex-dhgjhemyos` *dʰǵʰémyos* "earthly; human being" (keyword **`human`**), *wiHrós*, *h₂nḗr*. For "race of men", *mórtos* or *dʰǵʰémyos* works today. A project *mánus* was rejected (Kroonen: PGmc *mann-* is not from *mon-u-*) |

## 2. Everyday words found existing but unusable or unoffered

These turned up while searching for missing everyday words. Each exists in `lexicon.jsonl`, so no project entry was made.

### Usable, but unglossed or derived-gloss only

A gloss override would put each in the default pool.

| Word | Lexeme | Note |
|---|---|---|
| roof | `pie-lex-stegos` *stégos* | s-stem, usable; gloss "to cover" [-os]. Gk τέγος, OIr. *teg*. Override: "roof, house" |
| bed | `pie-lex-leghos` *légʰos* | s-stem, usable; Gk λέχος "bed". Override: "bed, couch" |
| suckle | `pie-lex-dheh1yeti` *dʰéh₁yeti* | 4 branches |
| hatred, grief | `pie-lex-kjeh2dos` *ḱéh₂dos* | Gk κῆδος "care, mourning", PGmc *hatiz* "hatred" |
| sweat (noun) | `pie-lex-sweydos` *swéydos* | — |
| sweep, wipe | `pie-lex-wrseti` *wr̥séti* | Lat. *verrō* "sweep" (de Vaan) |
| wash | `pie-lex-lewh3eti` *léwh₃eti* | — |
| lick | `pie-lex-leygjheti` *léyǵʰeti* | — |
| hate | `pie-lex-h3odeyeti` *h₃odéyeti* | Derived (-éyeti) |
| hornet | `pie-lex-kjrh2sexr` *ḱr̥h₂sḗr* | Usable; glossed "the one with horns, i.e. antennae", so keyword `hornet` misses it. Override: "hornet" |

### Usable, offered, under a keyword planners may not try

- `pie-lex-yeseti` *yéseti* "to be boiling": keyword **`boiling`** ("boil" does not match).
- `pie-lex-h2endhos` *h₂éndʰos* "bloom": keyword **`bloom`** (for "flower").
- `pie-lex-gjombhos` *ǵómbʰos* "tooth": keyword **`tooth`**. The classic *h₃dónts* (`pie-lex-h3donts`) is `unknown:noun-shape`.
- `pie-lex-ghostipotis` *gʰóstipotis* "lord, master": the "host" of Lat. *hospes*, keyword **`lord`**.
- `pie-lex-h3enHos` *h₃énHos* "load; burden": keywords **`load`**, **`burden`**.

### Unusable

The cause is in parentheses.

- **Animals:** ant `pie-lex-morwis` (hk-iu-stem); elk `pie-lex-h1olkjis` (pk-iu-stem, no gloss); red deer `pie-lex-h1elh1exn` (noun-shape, no gloss); squirrel `pie-lex-werwer` (bare stem); louse `pie-lex-lewH`, bee `pie-lex-bhey`, nit `pie-lex-nid` (bare stems, from round 1); wasp `pie-lex-wobhseh2` (eh₂); flea `pie-lex-plusis` and kin (noun-shape/devī/eh₂); pig `pie-lex-suHs` (noun-shape; the bare stem `pie-lex-suH` is usable).
- **Plants:** moss `pie-lex-mewsom`, `pie-lex-musom` (accent, derived gloss, Germanic only); yew `pie-lex-h1eyHwos` (accent); beech `pie-lex-bheh2gjos` (accent); elm `pie-lex-h1elem` (noun-shape); alder `pie-lex-h2elis`, `pie-lex-wern` (bare stems); leaf `pie-lex-bholyom` (accent, eval-held root *bʰleh₃-*).
- **Body:** fist `pie-lex-pnkwstis` (noun-shape); womb `pie-lex-gwelbhus`; elbow `pie-lex-Heh3leneh2` (eh₂, eval-held root); skin `pie-lex-skewHtis` (pk-iu-stem).
- **Weather, time:** month `pie-lex-mexh1ns` (noun-shape, eval-held root); hail `pie-lex-gjhreh3d` (bare stem).
- **Household, food:** salt `pie-lex-sexh2l` (noun-shape; *sélos* is usable); sieve `pie-lex-kreydhrom` (accent); floor `pie-lex-pleh2ro` (bare stem); axle `pie-lex-h2ekjs` (bare stem).
- **Other:** cough `pie-lex-kweh2stox` (noun-shape, eval-held root); town `pie-lex-tpolHis` (pk-iu-stem, derived gloss); wise `pie-lex-widris` (noun-shape); rotten `pie-lex-pewHlos` (accent, derived gloss).

**Systemic causes.** Most of these come from four shape classes, already flagged in round 1:

- `shape:eh2`: 391 specs, below the backtest threshold;
- `shape:pk-iu-stem` / `hk-iu-stem`: 273;
- `n-stem`: 59;
- `devi`: 47.

The other common cause is `unknown:noun-shape` (826). In spot checks, hand-written specs for these shapes realize correctly: round 2's acrostatic i-stem and u-stem entries give the expected cells, and so do the lexicon's `table` specs, such as *bʰardʰéh₂*. That suggests the backtest threshold, not the paradigm code, is what blocks them. This is not a validation of the paradigms.

## 3. Tier 3b neologism candidates (no cognate set; not created here)

These are suggested derivations from attested roots and productive suffixes. The neologism lexicon is a later step.

| Concept | Suggested formation | Basis |
|---|---|---|
| judge | *h₂yewos-déyḱs* "law-pointer", a compound root noun | Lat. *iūdex* < *ious-dik-*; *h₂yewos* "law, ritual right" (Lat. *iūs*, Av. *yaoš*); *deyḱ-* "show" (lexicon `pie-lex-dexykjst`). Alternative: agent noun *déyḱtōr* (-tōr) |
| witness | *wéydtōr* (> *wéystōr*) "one who knows/saw", an agent noun | Gk ἵστωρ "witness, judge" < *wid-tor-*; only if `pie-lex-widtres` stays unusable |
| wait | gloss *méneti* "to stay, wait (for)" | Gk μένω "stay; wait for" (`pie-lex-meneti`); no new form is needed |
| mounted, on horseback | participle *réydʰonts* "riding"; or bahuvrīhi *h₁eḱwo-sedós* "horse-sitting" | `pie-proj-reydheti`; *sed-* "sit" with the root-noun or *-ó-* agent type (Skt *-sád-*) |
| beak | instrument noun in *-trom* to *Hreh₃d-* "gnaw": *Hréh₃dtrom* (Lat. *rōstrum* type) | The lexicon has `pie-lex-Hreh3dtrom` (unusable). Repairing it is better than coining |
| thank, thanks | *gʷr̥néHti* "praise" plus the dative of the giver; noun *gʷérHtis* "praise, thanks" (-ti- action noun) | Skt *gūrtí-* "praise", Lith. *girti* "praise". OIr. *buide* "thanks" is Celtic only (Matasović s.v. *bodo-*) |
| grave, burial | *ḱéymn̥* "resting place, lying place" (*ḱey-* "lie" plus *-mn̥*) | *dʰembʰ-* is held out. Gk κεῖμαι "lie (dead)"; Gk σῆμα "grave-mound" is another model |
| sick, ill (adjective) | *swr̥gʰós* "ill" (*-ó-* adjective) or participle *swérgʰonts* "being ill" | `pie-proj-swerghos`; LIV *su̯ergʰ-* |
| here (adverb) | *h₁idʰé* "here" (closed class, for its owner) | M&A *h₁idʰa*: Skt *ihá*, Av. *iδa*, Gk ἰθα-γενής "native" (compound only). Not added: the closed-class lists belong to the engine |
| hope | *wélpos* or *welpís* "hope" | Gk ἐλπίς, ἔλπομαι; Lat. *volup*. Verbally Greek only (LIV) |
| shame, guilt | *h₂éǵos* n. "offence, guilt" | Gk ἄγος, Skt *ā́gas-*; the Sanskrit long *ā* is irregular, so it is a neologism candidate, not a project entry |
