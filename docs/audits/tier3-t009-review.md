# Tier-3 review: t009 (long epic narratives)

Reviewer: an Indo-Europeanist reading for the project. I used handbook knowledge only (Fortson, Ringe, Beekes, Meier-Brügger, LIV-style root shapes) and did no browsing. I checked forms against the project lexicon and engine cells, and ran `pie/validate.py` for lemmatization. Every clause was then checked by hand: subject against verb person and number, and English roles against PIE case.

Verdicts: `docs/audits/packets/t009-verdicts.jsonl`.

## Counts (28 items)

| verdict | n |
|---|---|
| ok | 21 |
| minor | 2 |
| wrong | 5 |

Three items are not engine narratives: f2e468e7 (the title "The Sheep and the Horses"), 6427d501 ("What do you want?"), and d08cd265 (a line from Byrd's "The King and the God"). I judged them as reconstructions, and all three are fine.

## Recurring patterns

1. **Verb number or person does not match the subject.** Each case is a single slip inside an otherwise good text, and the text usually has the correct form elsewhere.
   - 7ec70bbc: `gʷh₂mé` is aor. 1pl, but the subject is "the troop" (3sg).
   - 1a42c10a: `liǵʰént` is 3pl, but the subject is the horse (sg).
   - 15b0e5ea: `wéwketu` is imperative 3sg, but the order goes to a 2sg addressee.
2. **Wrong case or number on a noun phrase.**
   - 52bf3c34: nom. sg `bʰréh₂tēr` follows `dwóh₁`; the dual `bʰréh₂terh₁` is needed.
   - 8024db51: dat./abl. pl. `h₁némn̥bʰos` stands for "the name" (acc. sg).
   - The engine sometimes picks the wrong cell of a correct paradigm, and the same lexeme shows the right cell a sentence later.
3. **Accusative `ḱérd` for neuter "heart".** The nominative is `ḱḗr` in the same texts, but a neuter has nom. = acc. The handbook form is *ḱḗr (or *ḱḗrd). Affected: 7ec70bbc, f8a06e93, cfac1345.
4. **Conventions I noted but did not penalize:**
   - Delabialized `wéwket` for *wekʷ- (boukólos rule).
   - Weak cases of "earth" without dʰ (`ǵʰémi`, `ǵʰméy`), where the handbook has *dʰǵʰ-ém.
   - Neuter s-stem nom. pl. `nébʰōs` (52bf3c34; expected *nébʰesh₂).
   - `gʷh₂tós` "death" rests only on Celtic (OIr bath).
   - f0ed0b58 ends with plural `sh₂ént` after a run of duals.

## View of the texts

The epic register is the strongest work in these packets. The engine handles a wide range correctly:
- dual morphology (3du `-tām`, 2du imperative `-tóm`, `-th₁es`)
- injunctive or unaugmented aorists in narrative, with subjunctive futures (`gʷémoh₂`, `méresi`, `h₁éseti`)
- optative wishes (`stundyéh₁t`, `memnih₁ént`)
- vocative accent retraction (`ḱúh₁re`, `swḗḱure`, `Hyúdʰsme`)
- impersonal weather and time verbs with no subject (`h₁regʷesyét`, `léwkt`, `h₂wést`, `h₂wérst`)

Its inherited formulae are well chosen:
- `ḱléwos ń̥dʰgʷʰitom`
- `h₁uséwōm déh₃tōr` "giver of goods"
- `dyéw ph₂ter`, `diwés dʰúgh₂ter`
- `h₁ógʷʰim gʷʰen-` with `wódr̥h₂ Hwért` / `spr̥dʰí`, a good Vṛtra/Perkʷunos dragon-slaying set
- `bʰebʰóydʰh₂e`, `dedwóye`-type perfects

The plots draw plausibly on IE motifs: the Hildebrand father–son combat (cfac1345), Achilles' withdrawal (cb62d4e7), the Divine Twins' rescue at sea (306e6a6a), and the return of Odysseus (8024db51).

The weaknesses are mechanical rather than conceptual: about one bad cell per failing text. Fixing them is a paradigm-selection or agreement-check issue in the realizer, not a lexical one. Some lexeme choices are semantically stretched but defensible:
- `HrewdH-` "weep" used for battle cries
- `gʰóstipotis` used for "lord, master" (supported by OCS gospodь)
- `ǵneh₃-` used for "meet a husband"
