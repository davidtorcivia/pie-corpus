# Notation

This file specifies canonical PIE notation, its ASCII transliteration, and every rule used to normalize other notations into it. Code: `pie/translit.py` (the mapping) and `pie/notation.py` (the normalizer). Keep this file and the code in sync, and when a rule is added, add its row here in the same commit.

## 1. Canonical form (`pie` field)

Late PIE, Wiktionary/LIV conventions, **NFC**, over a **closed inventory**. `translit.to_ascii` raises on anything outside it, so "converts cleanly" means "notation-valid".

### Consonants

| Unicode | ASCII | | Unicode | ASCII | | Unicode | ASCII |
|---|---|---|---|---|---|---|---|
| p | `p` | | ḱ | `k'` | | kʷ | `kw` |
| b | `b` | | ǵ | `g'` | | gʷ | `gw` |
| bʰ | `bh` | | ǵʰ | `g'h` | | gʷʰ | `gwh` |
| t | `t` | | k | `k` | | h₁ h₂ h₃ | `h1 h2 h3` |
| d | `d` | | g | `g` | | H (generic laryngeal) | `H` |
| dʰ | `dh` | | gʰ | `gh` | | s, z | `s`, `z` |
| m n r l | `m n r l` | | w y (glides) | `w y` | | | |

- Palatals use the combining acute (U+0301) on k/g. ʰ is U+02B0, ʷ is U+02B7, and the subscripts are U+2081–2083.
- **`z`** is admitted. Wiktionary writes it for the voiced allophone of /s/ (*nizdós*), and it is attested notation, not an error.
- Voiceless aspirates (kʰ tʰ pʰ), palatal labiovelars (ḱʷ), and any modifier on other consonants are **rejected**.

### Nuclei and marks

- Vowels: a e i o u. They take an optional **macron** (U+0304, length) and an optional **acute** (U+0301, accent).
- Syllabic resonants: r̥ l̥ m̥ n̥, written with a **ring below** (U+0325). They take the same optional macron and acute.
- **Mark order** (in NFD): ring below → macron → acute. NFD puts the ring below first by itself (ccc 220), but macron and acute share ccc 230 and keep their input order. So e+acute+macron is a *different string* from ḗ, and it is rejected. The normalizer rule `G-MARK-ORDER` repairs it.
- Precomposed letters (ḗ U+1E17, ṓ U+1E53, ŕ U+0155, ĺ U+013A, ḿ U+1E3F, ń U+0144) appear wherever NFC produces them. Use `is_canonical()` to test a stored field.

### Other characters

- **Passthrough** (identical in both forms): space, `-` (morpheme/clitic boundary), `*`, `=`, `.`, `,`, `;`, `?`, `!`, `(`, `)`, `[`, `]`, `"`.
- **Escaped literals** (bare in Unicode, backslash-escaped in ASCII): `:` → `\:`, `/` → `\/`, `_` → `\_`, `'` → `\'`, `\` → `\\`. These characters are markup in the ASCII form, so a literal one is always escaped.
- Everything else is **rejected**: capitals other than `H`, tabs and newlines, `…`, typographic quotes, dashes, digits outside laryngeals, and foreign letters (ə þ v j c q x f). Clean them up with the normalizer first.
- No uppercase except `H`. PIE text is stored lowercase, and sentence-initial capitals are lowered by `G-CASE`.

## 2. ASCII form (`pie_ascii` field)

The mapping is in the table above. Mark suffixes follow the base letter in a fixed order: `_` (syllabic), then `:` (length), then `/` (accent). For example, ŕ̥ = `r_/`, ḗ = `e:/`, ŕ̥̄ = `r_:/`. The decoder rejects other orders (`e/:`).

Disambiguation rules (the decoder is greedy, left to right):

1. **`h` + `1|2|3` is a laryngeal. Any other `h` is aspiration**, and is allowed only after b, d, g, g', gw. So:
   - gʰ+h₁ = `ghh1`, ǵ+h₁ = `g'h1` (not ǵʰ + "1"), gʷ+h₁ = `gwh1`, gʷʰ+h₁ = `gwhh1`
   - a bare `h`, and `th`, `kh`, `k'h`, `kwh`, `sh` are errors.
2. **`w` right after plain `k`/`g` is labialization.** A literal w after a plain velar is written `k\w`/`g\w` (*kwékʷlos* → `k\we/kwlos`). After a palatal no escape is needed: ḱw = `k'w` (*h₁éḱwos* → `h1e/k'wos`). After an aspirate no escape is needed either: gʰw = `ghw`, and gʷʰ = `gwh` is distinct. `\w` anywhere else is an error.
3. `'` right after `k`/`g` marks the palatal. `_` right after r/l/m/n marks the syllabic. `:` and `/` are valid only after a nucleus. In any other position these characters must be escaped.

Round-trip guarantees (tested in `tests/test_translit.py` over 382 listed forms plus 5,000 fuzzed strings):
- `to_unicode(to_ascii(x)) == NFC(x)` for every valid x, whether it arrives as NFC or NFD.
- `to_ascii(to_unicode(a)) == a` for every canonical ASCII string a.
- ASCII output is pure ASCII.

CLI: `uv run python -I scripts/translit.py {to-ascii|to-unicode|normalize|check} [--profile P] [TEXT…]`.

## 3. Normalization (`source_form` → `pie`)

**The principle:** normalization is notational only. It changes symbols, never the reconstruction. Schleicher's *Avis akvāsas ka* becomes *awis akwāsas ka*, a valid string in the inventory that is still an 1868-stage reconstruction. Re-reconstructing an old text in modern terms is a separate, new record (provenance `back_projection` or `synthetic`), never a normalization.

- **Generic rules** (`G-*`) apply only where the input symbol has no other reading in IE notation. They run in every profile.
- **Profile rules** (`P-*`) are correct only for sources that follow a given convention. A source opts in by naming its profile.
- `normalize()` returns the IDs of the rules that fired. Store them in the record's `notes` (`normalized: G-CASE,P-V-W`) so every mapping applied to a record can be traced.

### Rule log

| ID | Rule | Example | Scope / risk | Added |
|---|---|---|---|---|
| G-NFC | Unicode NFC (runs first and last) | e+U+0301 → é | none | P0 |
| G-WS | trim; collapse whitespace to one space | | none | P0 |
| G-QUOTES | “ ” „ « » → `"` | | dialogue in fable versions | P0 |
| G-ELLIPSIS | … → `...` | | | P0 |
| G-LAR-DIGIT | laryngeal with ASCII/superscript digit → subscript | h2, h² → h₂ | only after h/H, and PIE text has no other digits | P0 |
| G-LAR-X | hₓ / Hₓ → H | hₓéw- → Héw- | unknown-color laryngeal, same meaning | P0 |
| G-CASE | lowercase, except a standalone `H` | H₂ówis → h₂ówis; dʰéH stays | **a blanket lower() would destroy generic laryngeals**; H + subscript is a capitalized h | P0 |
| G-PAL-CIRC | circumflex or inverted breve above on k g → acute | k̂ ĝ k̑ → ḱ ǵ | older palatal notation (Brugmann/Pokorny); caron deliberately excluded | P0 |
| G-LAB-U | ᵘ, ᵘ̯, ᵂ after k g → ʷ | kᵘ̯e → kʷe | older labiovelar notation | P0 |
| G-GLIDE | i̯ u̯ → y w | dei̯u̯os → deywos | Wiktionary writes glides as y w | P0 |
| G-RING-ABOVE | ring above on r l m n → ring below | wr̊ → wr̥ | common typo | P0 |
| G-SYL-DOT | dot below on r l m n → ring below | ṛ → r̥ | Indological convention in older IE works; PIE has no retroflexes | P0 |
| G-MARK-ORDER | acute+macron → macron+acute | é̄ → ḗ | invisible difference, distinct strings | P0 |
| G-HOMOGLYPH | Greek/Cyrillic look-alikes → Latin (Greek ο α ε ι υ; Cyrillic а е о р с у х і ј) | *mṛh₂-ό-* (Greek ό) → mr̥h₂-ó-; Cyrillic е in *ǵʰеydʰis* | found in the Wiktionary dump (3 forms); only PIE fields are normalized, so Greek cognate text is never touched | P1 |
| G-LAR-RING | ring below on a laryngeal → plain | h̥₁ → h₁ | Wiktionary marks vocalized laryngeals this way (6 forms). Syllabicity is predictable from context, and the meter module re-derives it, so dropping the mark loses no information we keep | P1 |
| P-CARET-SUP | `^w` `^h` (EPUB superscript flattened by our extractor) → ʷ ʰ | g^wōm → gʷōm | Fortson EPUB | books |
| P-HX-ASCII | ASCII `hx` → H | bherhxĝos → bʰerHǵos | Mallory & Adams | books |
| P-SPACING-RING | spacing ring ˚ after r l m n → ring below | pl˚th₂wī → pl̥th₂wī | West EPUB | books |
| P-SPACING-DIACRITICS | spacing macron/acute after the nucleus → combining | ph2te¯´r → ph₂tḗr | Ringe PDF text | books |
| P-STRIP-FOOTNOTE | superscript footnote digits on forms → removed | *bʰéh₁dʰ-e-²* | LIV² transcriptions | books |
| P-KU-LABIO | plain velar + u̯ → labiovelar (ku̯ gu̯ gʰu̯ → kʷ gʷ gʷʰ) | *neku̯-* → *nekʷ-* | **LIV² only**: LIV writes labiovelars with a superscript ᵘ̯ that transcribers sometimes put on the line. A true plain velar + w sequence would be mis-mapped; LIV writes those rarely, and palatals (ḱu̯) are excluded | books |
| P-ASP-PLAIN-H | plain h after b d g ǵ gʷ, not followed by a subscript → ʰ | bher- → bʰer-; *dhugh₂tḗr* → dʰugh₂tḗr (g+h₂ kept) | only for sources writing aspirates as `bh` and laryngeals with subscripts (Mallory–Adams style) | P0 |
| P-LAB-W-AFTER-K | plain k g + w → kʷ gʷ | kwis → kʷis | only for sources writing labiovelars as `kw`; would corrupt real k+w | P0 (defined, no profile yet) |
| P-SCHWA | ə → H | pəter → pHter | schwa indogermanicum ≈ vocalized laryngeal, color unknown; source-specific (Hirt) | P0 (defined, no profile yet) |
| P-V-W | v → w | akvāsas → akwāsas | older glide notation | P0 |
| P-J-Y | j → y | jugom → yugom | older/German glide notation | P0 |
| P-APOS-PAL | k' g' k’ → ḱ ǵ | | only for ASCII-ish sources; would corrupt quotes | P0 (defined, no profile yet) |

### Profiles

| Profile | Rules (in order) | For |
|---|---|---|
| `default`, `wiktionary` | generic only | Wiktionary, modern sources in standard notation |
| `plain-h-aspirates` | P-ASP-PLAIN-H + generic | Mallory & Adams, similar typography |
| `schleicher-1868` | P-V-W, P-J-Y + generic | Schleicher's fable |
| `fortson`, `mallory-adams`, `west`, `ringe` | per-book rules above, with laryngeal digits and *hx* resolved before plain-*h* aspiration (so *dhugh2* keeps g + h₂) | reference books (raw/books/) |

Profiles for Hirt (ə, labiovelars), Lehmann & Zgusta, and Kortlandt (glottalic stops) will be added in Phase 4, when the actual texts are in hand. The glottalic mapping (Kortlandt's notation ↔ the traditional series) is a notational correspondence, so it qualifies as normalization. Its table will be logged here.

## 4. Open notation questions

- ~~**How often the `\w` escape fires.**~~ Measured in Phase 1: on 17 of 7,261 lexicon forms. The spelling stays.
- **Wiktionary internal variants.** Phase 1 will audit the dump for forms that fail `is_canonical`: hₓ, parenthesized s-mobile `(s)`, alternative accent placements, `ʰ` look-alikes. Any new repair becomes a G- or P- rule here.
- **Dashes.** — and – are currently rejected. Decide when the first source that uses them as punctuation arrives.
