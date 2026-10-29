# Pronunciation

This file is the convention sheet for speaking the corpus. It gives each segment and feature of the canonical notation (`docs/notation.md`) a phonetic value, the scholarly basis for that value, and the main alternative views. Code: `pie/ipa.py` (the converter) and `scripts/to_ipa.py` (the CLI). Keep this file and the code in sync.

The pipeline: the model writes PIE in canonical notation, `pie.ipa.to_ipa` turns it into IPA deterministically, and a TTS engine speaks the IPA.

**Status of the result.** Nobody heard PIE. Every value below is a reconstruction of articulation from comparative evidence, and for the laryngeals and the dorsals the handbooks disagree. The default is a single consistent choice for a demo voice. It is not a claim that PIE sounded like this. Where opinion is split, a documented alternative can be selected (§9).

Sources are listed in `data/research/literature/bibliography.json` under these keys: Fortson = `fortson2010`, Beekes = `beekes2011`, Clackson = `clackson2007`, Ringe = `ringe2017`, Mallory–Adams = `mallory-adams2006`, Byrd = `byrd2018`, Kimball = `kimball2017`. The findings used here are lit-0073 to lit-0081 in `findings.jsonl`. Locators: Fortson and Mallory–Adams by section (§), Beekes, Clackson and Ringe by section and page, and Byrd's Handbook chapter (`byrd2018`, Handbook vol. 3 ch. 121) by section.

## 1. Summary of the default convention

| Notation | Default IPA | Main alternative(s) |
|---|---|---|
| p b t d | [p b t d] | glottalic: [p pʼ t tʼ] for *p *b *t *d (§3.3) |
| bʰ dʰ gʰ | [bʱ dʱ ɡʱ] | plain voiced (glottalic theory) |
| ḱ ǵ ǵʰ | [c ɟ ɟʱ] | fronted velars [kʲ ɡʲ ɡʲʱ]; plain velars [k ɡ ɡʱ] (uvular hypothesis) |
| k g gʰ | [k ɡ ɡʱ] | uvulars [q ɢ ɢʱ] (uvular hypothesis) |
| kʷ gʷ gʷʰ | [kʷ ɡʷ ɡʷʱ] | — |
| s, z | [s], [z] | — |
| m n r l | [m n r l] | — |
| y w | [j w] | — |
| r̥ l̥ m̥ n̥ | [r̩ l̩ m̩ n̩] | — |
| i u | [i u] | — |
| h₁ | [h] | [ʔ] |
| h₂ | [χ] | [ħ]; [x] |
| h₃ | [ɣʷ] | [ʕʷ]; voiceless [χʷ] |
| H (generic) | as h₁: [h] | — |
| vocalized laryngeal (CHC, CH#) | [ə] | colored [ə ɐ ɵ]; epenthetic [əχ]; syllabic [χ̩] |
| **e next to h₂ / h₃** | **[a] / [o]** (laryngeal coloring, on by default) | uncolored [e] |
| e o a, ē ō ā ī ū | [e o a], [eː oː aː iː uː] | Beekes: [æ ʌ] for *e *o |
| accent (acute) | high tone on the nucleus: [é] | stress [ˈ]; unmarked |
| syllable boundary | `.`, Vedic rule V.CV, VC.CV | onset maximization within legal onsets |

Examples (default, high tone):

| PIE | IPA |
|---|---|
| h₂ówis h₁éḱwōs-kʷe | χó.wis héc.woːs.kʷe |
| ph₂tḗr | pə.téːr |
| dʰugh₂tḗr | dʱu.ɡə.téːr |
| diwés | di.wés |
| ḱléwos ń̥dʰgʷʰitom | clé.wos ń̩dʱ.ɡʷʱi.tom |
| gʷʰénti | ɡʷʱén.ti |
| h₂éǵeti | χá.ɟe.ti |
| h₃ésth₁ | ɣʷós.tə |

## 2. Laryngeals

### 2.1 Consonantal values

The handbooks agree that the laryngeals were obstruents, probably fricatives, articulated far back in the mouth. Hittite and Luvian ḫ reflects h₂ and (word-initially) h₃. Beyond that, the values are disputed.

- **h₁ = [h]** (default). Byrd §3.3: /h/ or /ʔ/ is the most common reconstruction, and many prefer /h/. Fortson §3.21: a widespread view is plain h or a glottal stop. Alternatives: [ʔ] is favored by Beekes (p. 119 table, §11.8 p. 147: possibly a glottal stop, since h₁ does not color *e) and, as the current tendency, by Clackson (§2.5 p. 57). Ringe (§2.2.1 p. 9) commits only to "an obstruent".
- **h₂ = [χ]**, a voiceless uvular fricative (default). Byrd §3.3, following Weiss, takes h₂ and h₃ to have been originally uvular, and Anatolian ḫ likely uvular. Alternatives: a pharyngeal [ħ] (Fortson §3.21; Beekes p. 119, §11.8 p. 147); a velar [x] (Ringe §2.2.4 p. 14 renders *h₂éwis roughly as *[xáwis]); Clackson (p. 57) leaves it as a velar or pharyngeal back fricative. Mallory–Adams (§3.3) list x/xʷ or χ/χʷ as possible values.
- **h₃ = [ɣʷ]**, a voiced labialized uvular fricative (default). Its voicing is supported by *pi-ph₃-e- > Ved. píbati, Lat. bibit, OIr. ibid, where h₃ voiced the preceding *p (Byrd §3.3). Fortson §3.21 has a voiced pharyngeal, Clackson p. 57 a voiced back fricative perhaps with lip-rounding, and Kimball (Handbook vol. 1 ch. 20 §7) a voiced fricative in Proto-Anatolian. The rounding is inferred from the o-coloring (Ringe p. 9; Beekes p. 147). Alternatives: [ʕʷ] (Beekes, Byrd's /ʕ(w)/); voiceless [χʷ] (the h₂-like series of Mallory–Adams §3.3).
- **H (generic laryngeal) = the value of h₁**, so [h] by default. H is written where the color is unknown, and h₁ is the laryngeal with no coloring effect, so it is the neutral choice. H does not color vowels (§2.3).

### 2.2 Vocalized laryngeals

A laryngeal is a syllable nucleus exactly where `pie/meter.py` says it is (`meter.word_nuclei`). That means between consonants (CHC) and word-finally after a consonant (CH#), but not word-initially (#HC), not after another laryngeal, and not after a diphthong in -y. The rule and its Vedic and Greek basis are in the meter module's docstring and in `docs/audits/meter-census.md`.

- **Default: the vocalized laryngeal is pronounced [ə]**, a short mid central vowel that replaces the consonant: ph₂tḗr [pə.téːr], ǵénh₁tor [ɟé.nə.tor], méǵh₂ [mé.ɟə]. This is the traditional *schwa indogermanicum* (Fortson §3.29 "schwa primum"; Beekes §11.8.1 p. 148, older notation *ə₁). The daughter reflexes are Gk e/a/o by laryngeal (the triple reflex), Indo-Iranian i, and a elsewhere (Fortson §3.17; Beekes §11.8 p. 146; Clackson §2.5 pp. 58–59, table 2.13).
- **Why not keep the consonant?** Byrd (§3.3, §5.3) holds that true vocalization *h̥ was unlikely. On his view a prop vowel stood next to the laryngeal (written p(ə)h₂tḗr), and in PIE itself only #CHC developed it; the rest is branch-specific. Ringe (§2.2.4 p. 15) treats the laryngeals as never syllabic. Fortson §3.17 says the prop vowel arose before or after the laryngeal. A rendering [pəχ.téːr] would close the first syllable and make it heavy, but `meter.weights` and the Vedic meter (pi-tā́, light) count it as light. The default therefore keeps the syllable light by pronouncing the nucleus as [ə] alone.
- Alternatives (all keep the same syllable count):
  - `vocalized="colored"`: h₁ [ə], h₂ [ɐ], h₃ [ɵ], H [ə]. This follows the Greek triple reflex (ἄνεμος, θυγάτηρ, ἄροτρον).
  - `vocalized="syllabic"`: the laryngeal itself is the nucleus, e.g. [pχ̩.téːr]. This is literally what meter.py models. It is hard for most TTS engines.
  - Epenthetic [əχ] (Byrd's prop vowel plus consonant) is documented here but not implemented, because it contradicts the meter weights.
- A vocalized laryngeal is never accented and never long.

### 2.3 Laryngeal coloring (on by default)

**By default the converter colors a short e next to h₂ to [a] and next to h₃ to [o]**: h₂éǵeti [χá.ɟe.ti], bʰéh₂ti [bʱáχ.ti], h₃ésth₁ [ɣʷós.tə]. The notation writes e, following Wiktionary/LIV, because coloring is predictable. In late PIE the colored vowel was what was pronounced: Ringe (§2.2.4 p. 14) gives *[xáwis] and says that next to h₂, *e was pronounced [a]. Beekes (§11.8 p. 147) explains the o-coloring by the rounding of h₃. This is the single largest surface effect in the converter. In the corpus, about 13,000 h₂ stand against about 650 written short a (plus about 660 ā), so most [a] in the output comes from coloring. Preset `uncolored` turns it off.

- Coloring is applied only to **short e**, directly next to the laryngeal (before or after it). If e stands between h₂ and h₃, the preceding laryngeal decides.
- Long ē is not colored (Eichner's law), and o is not changed.
- h₁ and H do not color.
- Coloring keeps the accent: h₂é → [χá].

## 3. Stops

### 3.1 Dorsals

The notation has three series: ḱ ǵ ǵʰ, k g gʰ and kʷ gʷ gʷʰ. Three series must be reconstructed, because Luvian, Albanian and Armenian keep them apart (Byrd §3.1; Fortson §3.9; Ringe p. 7; Clackson §2.4 pp. 51–53). Mallory–Adams (§3.2) call this a topic of major argument. Beekes (§11.3.3 pp. 124–126) discusses plain velars as possible allophones but takes the third series to be phonologized in PIE.

- **Default: palatovelars are palatal stops [c ɟ ɟʱ].** Fortson §3.5 calls them true palatals, like k and g farther forward (as in *Tokyo*, *argue*), and Beekes §11.3.2 p. 122 has the tongue raised toward the palate. The single symbols [c ɟ] are easier for TTS than a diacritic.
- Alternative `dorsals="fronted"`: [kʲ ɡʲ ɡʲʱ], the same articulation written as a fronted velar.
- Alternative `dorsals="uvular"` (the uvular hypothesis): the written palatovelars are plain velars [k ɡ ɡʱ] and the written plain velars are uvulars [q ɢ ɢʱ]. Ringe (§2.2.1 p. 7 and n. 2) finds true palatal stops most unlikely and takes the other two series as postvelar. Clackson (§2.4) reports Huld's version (ḱ velar, k uvular), and Mallory–Adams (§3.2) mention k, q, qʷ.
- **Labiovelars = [kʷ ɡʷ ɡʷʱ]**, single segments, velars with lip-rounding, not velar + w (Fortson §3.5; Ringe p. 7; Clackson §2.4 p. 49; Beekes p. 122). Sanskrit and Lithuanian keep them apart from *ku̯. The notation writes a plain velar + w as `k\w` in ASCII, which the converter renders [kw]. Boukólos delabialization is applied in the morphology engine (`phon.boukolos`), not here.

### 3.2 Voiced aspirates

**bʰ dʰ gʰ (and ǵʰ gʷʰ) = breathy-voiced (murmured) stops [bʱ dʱ ɡʱ]** (Byrd §3.1; Fortson §3.6; Ringe p. 8: "probably breathy-voiced"; Clackson §2.3 pp. 45–48). Sanskrit bh dh gh continue this type directly. *b is rare (Fortson §3.10–3.11; Ringe p. 8; Mallory–Adams §3.4), but it is written and is rendered [b].

### 3.3 The glottalic alternative (documented, not implemented)

Under the glottalic theory (Gamkrelidze–Ivanov, Hopper), the traditional plain voiced stops *b d g were ejectives or glottalized, and the voiced aspirates were plain voiced. Beekes (§11.3.6 pp. 128–129) accepts a version of it, in which the traditional voiced stops were pre-glottalized, and cites Lachmann's and Winter's laws. He still writes b d g bʰ for convenience. Byrd (§3.1) rejects it, and Fortson (§3.10–3.11) and Ringe (p. 8) find it rejected or unproven. Clackson (§2.3) calls the debate largely a non-argument and suggests that *d may have been "stiff" or creaky-voiced. `docs/notation.md` excludes glottalic notation, so the converter has no glottalic preset.

## 4. Fricatives and resonants

- **s = [s]; z = [z].** z is the voiced allophone of s before voiced obstruents (*nizdós*) (Byrd §3.2, §5.1; Fortson §3.12, §3.34; Clackson §2.2 p. 36). Ringe (p. 20) is unsure whether the assimilation is PIE. The converter renders z only where the notation writes it and does not voice s itself (§8).
- **m n r l = [m n r l].** r is given as an alveolar trill [r]. The handbooks do not fix the r-type, and [ɾ] is equally possible. The converter does not assimilate n to a following velar (no [ŋ]).
- **y w = [j w]**, and **i u = [i u]**. These are one phoneme each, with the vocalic and consonantal values as allophones (Byrd §1.1, §2; Ringe §2.2.2 p. 9; Clackson §2.2 pp. 35–36; Beekes §11.5 pp. 138–140; Mallory–Adams §4.1). The converter does not re-derive which value applies. It uses the notation's spelling as fixed by `phon.join`.
- **Syllabic resonants r̥ l̥ m̥ n̥ = [r̩ l̩ m̩ n̩]**, like the final syllables of English *bottle*, *bottom*, *button* (Fortson §3.14). Long r̥̄ = [r̩ː].
- **Diphthongs** are vowel + glide, with the glide in the coda: ey [ej], ow [ow], ḗw [éːw]. An accent falls on the vowel: éy [éj].
- **Sievers' and Lindeman's laws are not applied.** Prevocalic y/w after a heavy syllable stay [j w] (dyḗws is one syllable). This matches meter.py's default (`sievers=False`). Byrd (§5.4) keeps the two laws apart, Fortson (§3.43–3.44) reports Schindler's merger of them, and Beekes (§11.5) sees no compelling reason to date Lindeman's law to PIE.

## 5. Vowels

- **Short a e o i u = [a e o i u]; long ā ē ō ī ū = [aː eː oː iː uː].** Length is phonemic and is marked with [ː]. Fortson (§3.26–3.27) reconstructs five short vowels and long *ē *ā *ō, with *ī *ū uncertain. Underlying *a is rare (Ringe §2.2.3 pp. 10–11; Fortson §4.8, §4.17; Clackson p. 36), and most surface [a] comes from h₂e (§2.3).
- Quality: mid vowels are given as [e o], the plain cardinal values. Beekes (§11.6.2 pp. 141–143) has no *a and suggests that *e *o were phonetically [æ ʌ]. That is not implemented.
- A vocalized laryngeal is [ə] (§2.2). It is the only vowel outside the notation.

## 6. Accent

- **PIE had a pitch accent, rendered as a high tone on the accented syllable's nucleus.** Fortson §3.30–3.32 calls it standardly agreed that the accent was a pitch accent, the accented syllable higher in pitch, and mobile. Ringe (§2.2 p. 7, §2.2.5 p. 21) says high pitch, and Byrd §4.4 a mobile high-pitch accent "similar to modern Swedish". Beekes (§11.9.3 p. 155) identifies the Vedic *udātta* as a high tone and the PIE accent as tone-raising. Clackson (§3.4 pp. 76–78) reserves judgement for PIE itself, although Greek and Vedic had pitch accents.
- **IPA convention (`tone=True`, default):** the IPA high-tone diacritic, a combining acute (U+0301), on the nucleus: [é], [éː], [ĺ̩], [í]. On a diphthong it goes on the vowel ([éj]). One mark per accented word; unaccented words (clitics such as -kʷe, enclitic forms) carry none. The converter does not model the Vedic *svarita* or the Greek circumflex (a fall on long vowels). A long accented vowel is simply high.
- **Plain-stress fallback (`tone="stress"`):** for engines without tone, [ˈ] goes before the accented syllable instead: ph₂tḗr [pə.ˈteːr]. The two marks are never combined.
- `tone=False`: no accent marks.

## 7. Syllabification

Nuclei come from `pie/meter.py` (`meter.word_nuclei`): vowels, syllabic resonants as written, and vocalized laryngeals (§2.2). The converter imports this function and does not fork it, so every word has exactly as many IPA syllables as `meter.word_syllables` counts. The tests check this over every tier 1 word and a sample of 3,000 tier 2/3 words.

Boundaries ("." in IPA) follow the rule `meter.weights` uses for Vedic syllable weight:
- one consonant between nuclei begins the next syllable: h₂ówis [χó.wis];
- in a cluster, the first consonant closes the syllable and the rest begin the next: h₁éḱwōs [héc.woːs], kʷetwóres [kʷet.wó.res];
- a word-initial cluster is the first onset (h₂stḗr [χstéːr]), and a word-final one the last coda.

So a syllable is heavy (long nucleus or a coda) exactly when `meter.weights` says it is (tested). A clitic joined by a hyphen counts as part of its host, as in meter: h₁éḱwōs-kʷe [héc.woːs.kʷe]. A word with no nucleus is rendered as its bare consonants, with no syllable.

Alternative (not implemented): Byrd 2015 and Byrd §4.1–4.2 give a moraic analysis in which every coda consonant is a mora, with a maximal CCVCC template and extrasyllabic word-edge consonants. An onset-maximizing split (V.CCV where CC is a legal word-initial onset) would move some boundaries, but it would not change counts.

## 8. What is not modelled

- **Sandhi.** Words are converted one at a time. No external sandhi, assimilation across word boundaries, or resyllabification across words takes place. (`meter.weights` treats a line as one stream for weight, but the IPA keeps word boundaries.)
- **Assimilations inside a word.** These are not modelled: s → z before voiced stops, unless written; voicing or devoicing in clusters (e.g. *-gʷʰt-*); Bartholomae's law; nasal place assimilation; the *-tst-* insertion in dental clusters. The notation writes underlying forms (`pie/phon.py` docstring), and so does the IPA.
- **Prosody above the word.** Sentence intonation, emphasis, enclitic accent shifts and phrasal downstep are not modelled. Punctuation becomes a pause only: `. ? ! …` → ‖ (major group), `, ; :` → | (minor group). Quotes, brackets, `*` and `=` are dropped. Use `breaks=False` to drop the pauses too.
- **Laryngeal loss and compensatory lengthening** (eh₂ → ā and the like) are post-PIE and are not applied. eh₂ is [aχ], not [aː]. Forms the notation already writes contracted (-ām) are rendered as written.
- **Sievers/Lindeman variants, the Vedic svarita, the Greek circumflex** (§4, §6).

## 9. API and conventions

```python
from pie.ipa import to_ipa, to_xsampa, syllables, Convention, CONVENTIONS

to_ipa(text, *, convention="default", tone=True, ascii=False, breaks=True) -> str
#   tone: True (high tone, acute) | "stress" (ˈ) | False;  ascii=True reads pie_ascii
syllables(word, *, convention="default", tone=True, ascii=False) -> list[str]
to_xsampa(ipa) -> str          # X-SAMPA for engines that want ASCII phoneme codes
```

Named presets (`CONVENTIONS`):

| Preset | h₁ h₂ h₃ (H) | Dorsals | Vocalized | Coloring |
|---|---|---|---|---|
| `default` | h χ ɣʷ (h) | c ɟ ɟʱ | ə | on |
| `pharyngeal` | ʔ ħ ʕʷ (ʔ) (Beekes, Fortson type) | c ɟ ɟʱ | ə | on |
| `uncolored` | h χ ɣʷ (h) | c ɟ ɟʱ | ə | off |

Any combination can be built with `Convention(laryngeals="fricative"|"pharyngeal"|"voiceless", generic=None|"<ipa>", dorsals="palatal"|"fronted"|"uvular", vocalized="schwa"|"colored"|"syllabic", coloring=True|False)`.

**X-SAMPA** (`to_xsampa`) maps: χ `X`, ħ `X\`, ɣ `G`, ʕ `?\`, ʔ `?`, c `c`, ɟ `J\`, q `q`, ɢ `G\`, ə `@`, ɐ `6`, ɵ `8`, ʷ `_w`, ʲ `'`, ʱ `_t` (breathy voice), ː `:`, syllabic `=`, high tone `_H` (after length: `e:_H`), ˈ `"`, ‖ `||`. Kirshenbaum and eSpeak `[[…]]` phoneme names are voice-specific in eSpeak-NG and are not generated here. They are left to the TTS integration.

**CLI** (`scripts/to_ipa.py`):
- `convert [--ascii] [--xsampa] [--tone tone|stress|none] [--convention P] TEXT…` reads stdin when no text is given.
- `batch IN.jsonl OUT.jsonl [--field pie] [--xsampa]` writes a new file with an `ipa` field. It refuses to overwrite the input, or any existing file without `--force`.
- `stats PATH…` reports failures, the symbol inventory and the unusual phones.

## 10. Corpus check (2026-10-28, default convention)

`stats corpus/tier1 corpus/tier2 corpus/tier3`: 2,757 records, 53,957 whitespace tokens, **0 failures**. The IPA uses 32 distinct code points and 42 distinct phones (segments with their modifiers, tone ignored). The most frequent phones outside plain Latin `p b t d k ɡ s z h m n r l j w a e i o u` are:

| Phone | Count | | Phone | Count |
|---|---|---|---|---|
| χ | 11,449 | | eː | 2,825 |
| kʷ | 6,883 | | bʱ | 2,767 |
| c | 4,822 | | oː | 2,585 |
| dʱ | 4,199 | | ɡʷ | 2,362 |
| ə | 2,944 | | ɟ | 2,235 |

They are followed by ɣʷ 2,180, n̩ 2,092, r̩ 1,970, m̩ 1,783, l̩ 1,265, ɟʱ 1,202, ɡʱ 1,045 and ɡʷʱ 918. The high-tone acute (U+0301) and the syllabic mark (U+0329) are the two combining marks. Under `pharyngeal`, [h] becomes [ʔ], χ becomes ħ and ɣʷ becomes ʕʷ, with the same counts.
