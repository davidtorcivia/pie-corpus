# Tier-3 review: packet t017 (28 items)

Reviewer: skeptical-Indo-Europeanist pass. Handbook knowledge only (Fortson, Ringe, Beekes, LIV-style conventions from memory); no browsing. I checked suspect forms against `data/lexicon/lexicon.jsonl` and engine cells (`Lexicon.cells`).

## Counts
- ok: 12
- minor: 7
- wrong: 9

## Recurring patterns

**1. Engine bug: oblique stems of amphikinetic nouns (wrong).** The weak stem zero-grades or drops material that should stay:
- `h₂éḱmō` gives `h₂ḱn-` (h₂ḱn̥sú, h₂ḱnéh₁) for *h₂ḱmn-: items 2fe3f033, 23613e85.
- `tétḱō` gives `tḱn-` (tḱnéy) for *tetḱn-: item c995f4ce.
- `swésōr` gives `susr-` (susréy) for *swesr-: item 377ebef1.

These are cell-level errors in `pie-lex-h2ekjmox`, `pie-lex-tetkjox` and `pie-lex-swesoxr`, so every text that uses an oblique case of these nouns will carry them. Fix them in the paradigm class, not per text.

**2. Wrong cell picked (wrong).** The cell exists but is the wrong one for the English:
- gen. `gʷréws` used as the object: 4ffb3b4c.
- 1pl mid. `sékʷomedʰh₂` for a 3sg subject: b06c9ba6.
- impv. 3pl `dukéntu` for a 2sg command: 57bb2538.
- acc. `h₂éǵrom` for 'in the field': e644fd93.
- the possessive `swéh₂s` agrees with the possessor (fem. gen.) instead of the dat. noun: 57b9ba42.

These look like planner/realizer slot-filling errors (case, person or agreement taken from the wrong node). Look at the realizer's feature propagation.

**3. Lost labiovelar in *perkʷ- (minor).** `pérkunos/pérkune` (687a430f, db365954) don't match the lexicon headword `pérkʷunos`. The oak lexeme `pérkus` has plain k in its strong cells but kʷ in its weak cells (`pr̥kʷéws`), giving `pérkum` in 2517f1bf and 0433ed1f.

**4. Smaller points (minor).**
- `sddʰí` (377ebef1, 23613e85) is a doubtful root-aorist imperative of *sed-.
- The twins speak in 1pl inside an otherwise dual text (b06c9ba6).
- The gen. of `h₃mígʰleh₂` has lost its accent (2fe3f033).
- `h₁áyto` (secondary ending) sits in a gnomic present (c995f4ce).

**5. Scholarly texts.**
- 4295dc6a and b30aa641 are Schleicher's 1868 fable in his pre-laryngeal notation (b30aa641 also has a stray space in `wiwidwant- swas`).
- 0c559c86 is a 'King and the God' line with `gʷah₂t`, against the corpus's `gʷéh₂t`.

All three are faithful, but they mix notation systems into the corpus. Label them as historical or keep them out of handbook-PIE training data.

## What the engine does well
The subjunctive in 'if' and 'whoever' clauses is used correctly (Hrunépetor, stunédeti, HréwdHeti, wérǵesi, méreti as future). So are perfects (dedórḱh₂e, dedwóye, tetl̥h₂dʰí), duals (yemHóh₁ … stéygʰetām, dwóh₁ h₁éḱwoh₁ HéHḱuh₁ h₁sih₁tā́m), and athematic optatives (gʷʰn̥yéh₁t, h₁dyéh₁t, pl̥nh₁ih₁tó). Inherited formulae (ḱléwos ń̥dʰgʷʰitom, gʷʰént h₁ógʷʰim, déh₃tor h₁uséwōm, ḱludʰí) are well placed. Outside the patterns above the texts are idiomatic and grammatical. The serious problems are mechanical and fixable at source.
