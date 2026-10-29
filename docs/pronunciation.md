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
- Alternative `dorsals="plain"`: [k ɡ ɡʱ], the palatovelars merged with the plain velars. This is a speech choice, not a claim about PIE. Kokoro's only training language with c ɟ labels is Hindi, where they stand for च ज [tʃ dʒ], so [ɟ c] come out as affricates (docs/research/tts-bakeoff.md).
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

**X-SAMPA** (`to_xsampa`) maps: χ `X`, ħ `X\`, ɣ `G`, ʕ `?\`, ʔ `?`, c `c`, ɟ `J\`, q `q`, ɢ `G\`, ə `@`, ɐ `6`, ɵ `8`, ʷ `_w`, ʲ `'`, ʱ `_t` (breathy voice), ː `:`, syllabic `=`, high tone `_H` (after length: `e:_H`), ˈ `"`, ‖ `||`. Kirshenbaum and eSpeak `[[…]]` phoneme names are voice-specific in eSpeak-NG and are not generated here. The eSpeak mapping for the PIE voice is in `tts/espeak/mapping.json` (§11).

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

## 11. Speech

Code: `pie/speak.py` (API), `scripts/speak.py` (CLI), `scripts/speech_pack.py` (listening pack), `tts/espeak/` (eSpeak voice), `tts/kokoro/vocab.json` (Kokoro's symbol set). The research behind the choices is `docs/research/tts-options.md`. Nobody has judged the audio by ear yet; listen to the pack (§11.4) before the demo.

### 11.1 Backends

| Backend | Engine | Accent | Character |
|---|---|---|---|
| `espeak` | eSpeak-NG 1.52.0, custom `pie` phoneme table (Hindi base + Arabic ħ ʕ + level tones) | `tone=True`: voice `pie/pie-tone`, high level tone (`5`) on the accented syllable, low (`1`) elsewhere; `tone="stress"`/`False`: voice `pie/pie`, `'` stress | Robotic, segmentally right: χ ɣ ʔ ħ ʕ c ɟ, murmured stops, syllabic resonants, length |
| `kokoro` | Kokoro-82M v1.0, local PyTorch | `pitch=True` (default with `tone=True`): the predicted F0 is flattened to 0.92 × median and raised to 1.3 × median on the accented vowel (and its ː); `pitch=False` ("raw"): ˈ before the accented syllable | Natural; Hindi voices `hf_alpha` (default), `hf_beta`, `hm_omega`, `hm_psi` |
| `kokoro-remote` | Kokoro-FastAPI server, `POST /dev/generate_from_phonemes` | ˈ only (no F0 access on the server) | Same model; any server voice (Hindi, English `af_*`/`bm_*`, Italian `im_nicola`, …) |
| `kokoro-erebus` | The `kokoro` backend itself, run as the `pie-tts` service on erebus (§11.6), `POST /speak_ipa` | Same as `kokoro` (`pitch=True` F0 patch, or ˈ) | Same output as local `kokoro`, with no local PyTorch env needed; the voices pinned in the deployed revision |

**Respelling profiles.** `speak(…, profile=…)` (CLI `--profile`) respells the converter IPA before any backend sees it, with whole-phone replacements in one pass, longest first (`pie.ipa.respell`). Examples: `h2-velar` says h₂ as [x], `h1-glottal-stop` says h₁ as [ʔ], `murmur-aspirated` writes ʰ, and `syllabic-schwa` writes əC. The full list is `pie.speak.PROFILES`. Because the profile is applied first, the eSpeak round trip checks the respelled IPA, which is what was actually sent. `pie.speak.engine_input` returns the exact engine input without synthesizing. The bake-off of voices × profiles is docs/research/tts-bakeoff.md.

**Round trip (espeak).** eSpeak does not reject an unknown phoneme code: it silently drops the rest of the word (`[[H'eKw0s]]` is read as ħˈe). Every rendering is therefore read back with `espeak-ng --ipa` on the exact string sent and compared with the converter's IPA. The comparison ignores dots, stress and tone, reads eSpeak's ʰ after a voiced stop as ʱ, kw as kʷ, and a doubled r̩ l̩ m̩ n̩ ɐ ɵ as one (eSpeak prints a tone-bearing or long one twice). A mismatch raises `RoundTripError`, or with `strict=False` (`--no-strict`) prints a WARNING on stderr and warns. A second failure mode is also guarded: `[[…]]` input longer than about 750 characters is cut mid-word into a new clause that eSpeak reads as English text, so input goes to eSpeak in pieces of at most 400 characters.

**Kokoro input.** Kokoro's vocab lacks ʱ ʷ ̩ ħ ʕ ɢ ɵ and the acute, and `KModel` drops unknown symbols silently. The converter IPA goes through one substitution map (`pie.speak.KOKORO_SUBST`) and every resulting symbol is checked against `tts/kokoro/vocab.json` (`UnsupportedPhone` otherwise):

| Converter | Kokoro |
|---|---|
| ʷʱ → ʱʷ, then ʱ | ʰ (Kokoro's Hindi voices learned breathy stops as ʰ) |
| ʷ | w (kʷ → kw) |
| ħ, ʕ (pharyngeal preset) | χ, ɣ |
| C̩ (r̩ l̩ m̩ n̩) | əC; the accent goes on ə |
| ɢ (uvular dorsals), ɵ (colored vocalized h₃) | ɡ, o |
| acute | F0 mask (`pitch=True`) or ˈ |
| ‖, \| | end of chunk (`.`, synthesized separately, 0.3 s apart), `,` |

### 11.2 Setup

1. **eSpeak-NG** (Homebrew, required for `espeak`): `brew install espeak-ng` (1.52.0). Then build the PIE voice: `sh tts/espeak/build.sh`. It checks the installed version, clones the eSpeak-NG source at tag 1.52.0 (commit `4870adfa25b1a32b4361592f1be8a40337c58d6c`, needed for the phoneme sources, which Homebrew does not ship) into the gitignored `tts/espeak/build/`, copies the installed data there, adds `ph_pie` and the two voices, compiles with `--compile-phonemes` (must report 0 errors) and runs a smoke test. The system install is only read. `pie.speak` uses `tts/espeak/build/data` (override: `PIE_ESPEAK_DATA`).
2. **Kokoro, local** (optional). `kokoro` 0.9.4 and `misaki` 0.9.4 require Python < 3.13, and the main env is 3.14, so the `kokoro` dependency group (exact pins: kokoro 0.9.4, misaki[en] 0.9.4, torch 2.15.0, transformers 5.21.0, huggingface-hub 2.3.0, numpy 2.5.4, loguru 0.7.3) goes into a separate env:
   ```sh
   UV_PROJECT_ENVIRONMENT=.venv-kokoro uv sync --python 3.12 --group kokoro --no-default-groups
   UV_PROJECT_ENVIRONMENT=.venv-kokoro uv run --no-sync python -I scripts/speak.py --backend kokoro -o x.wav "deywós"
   ```
   The weights are not in git. On first use `pie.speak` downloads them from Hugging Face, pinned to revision `f3ff3571791e39611d31c381e3a41a3af07b4987` of `hexgrad/Kokoro-82M` (Apache-2.0), into the gitignored `tts/cache/hf/` (override: `PIE_KOKORO_CACHE`), and verifies each sha256:

   | File (`https://huggingface.co/hexgrad/Kokoro-82M/resolve/f3ff3571791e39611d31c381e3a41a3af07b4987/<file>`) | Bytes | sha256 |
   |---|---|---|
   | `config.json` | 2,351 | `5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f` |
   | `kokoro-v1_0.pth` | 327,212,226 | `496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4` |
   | `voices/hf_alpha.pt` | 523,425 | `06906fe05746d13a79c5c01e21fd7233b05027221a933c9ada650f5aafc8f044` |
   | `voices/hf_beta.pt` | 523,420 | `63c0a1a6272e98d43f4511bba40e30dd9c8ceaf5f39af869509b9f51a71c503e` |
   | `voices/hm_omega.pt` | 523,425 | `b55f02a8e8483fffe0afa566e7d22ed8013acf47ad4f6bbee2795a840155703e` |
   | `voices/hm_psi.pt` | 523,351 | `2f0f055cea4f1083f4ef127ece48d71606347f6557dbb961c0ca5740a2da485b` |

   The other pinned voices (Hindi, Spanish, Brazilian Portuguese, French, Italian and the English voices chosen in the bake-off) and their sha256 are listed in `pie.speak.KOKORO_FILES`. `tts/kokoro/vocab.json` is the `vocab` of that `config.json`.
3. **Kokoro, remote** (optional): a Kokoro-FastAPI server. With `PIE_KOKORO_URL` set (e.g. `http://localhost:8880` through `ssh -N -L 8880:localhost:8880 erebus`), requests go there over HTTP. Otherwise they go through `ssh $PIE_KOKORO_SSH curl …` (default host `erebus`, port `PIE_KOKORO_PORT`, default 8880). Treat the server as production: the backend only posts to the TTS endpoint.

### 11.3 Usage

```python
from pie.speak import speak, speak_ipa
speak("h₂ówis h₁éḱwōs-kʷe", backend="espeak", out_wav="ovis.wav", convention="default", tone=True)
speak("ǵʰimḗ", backend="kokoro", out_wav="g.wav", voice="hm_omega", pitch=True)
speak_ipa("ʔés.ti", backend="kokoro-remote", out_wav="e.wav", voice="hf_alpha")   # IPA in
```

`speak` returns a `SpeechResult` with the IPA, the exact engine input and (espeak) the read-back. CLI: `uv run python -I scripts/speak.py [-o out.wav] [--backend B] [--voice V] [--tone tone|stress|none] [--convention P] [--ascii|--ipa] [--no-strict] [--no-pitch] [--play] [TEXT…]`. With no text it reads stdin, one utterance per line, joined by ‖. `--play` plays the wav with `afplay` (macOS). Exit status: 1 on a speech error (including a round-trip mismatch), 2 on bad input.

### 11.4 Listening pack

`scripts/speech_pack.py` renders a fixed set to `tts/samples/`: the wavs are gitignored, and `tts/samples/manifest.json` (committed) lists every clip with phrase id, source record, PIE, English, IPA, system, voice, exact engine input and wav path. The set has the openings of Schleicher's fable and "The King and the God" (Byrd 2013, three lines each), three Tier 3 hymn lines (b003, from its last approved release; no batch containing hymns is eligible at the moment) and the 11 minimal pairs of tts-options.md §2.4. It uses nine systems: eSpeak stress and tone, local Kokoro raw and pitch-patched, Kokoro-remote with `hf_alpha`, `hm_omega`, `bm_george` and `im_nicola`, and Piper `hi_IN-rohan-medium` (through the researcher's temporary venv; skipped when that is gone). Run it in the Kokoro env to get every system (`--systems` picks a subset).

### 11.5 Known limits

- **Hindi accent.** Both main engines speak through Hindi: eSpeak's `hi` base and Kokoro's Hindi voices give dental or retroflex-coloured t d and Hindi vowel colours. The eSpeak r is the base1 alveolar trill (`R`) rather than Hindi's tap. With the non-Hindi Kokoro voices, χ c ɟ and murmur were never trained.
- **kʷ is k+w** in every engine (eSpeak has no labialized stops, Kokoro and Piper no ʷ), and ɡʷʱ is ɡʱ+w.
- **Kokoro substitutions** (§11.1 table): no ħ ʕ (said χ ɣ), syllabic resonants as ə + resonant, ʱ as ʰ. The accent is an imposed F0 contour on `kokoro` and `kokoro-erebus` and plain ˈ stress on `kokoro-remote`.
- **eSpeak conventions.** All three presets and the `fronted`, `colored`, `voiceless` and `generic` options are supported. `fronted` kʲ ɡʲ ɡʲʱ are said as the palatals c ɟ ɟʱ (§3.1: the same articulation). `dorsals="uvular"` (ɢ: no eSpeak table has a voiced uvular stop) and `vocalized="syllabic"` (χ̩ etc.) raise `UnsupportedPhone`.
- **eSpeak stress.** In stress mode a word without an accent spoken alone still gets eSpeak's default stress. The tone voice's pitch range is narrow (about 80 → 98 Hz at default settings).
- **Licences.** The eSpeak data is GPL-3.0 (the audio is not covered). Kokoro is Apache-2.0. Piper's code is GPL-3.0; the licence of the `hi_IN-rohan` data (IIT Madras IndicTTS) is unverified, so confirm it before any public use of Piper clips.

### 11.6 Deployment on erebus

The pitch-patched `kokoro` backend runs as a Docker service, `pie-tts`, on the home server erebus. It exists so the demo can use the F0 accent without the local Python 3.12 Kokoro env. The files are in `tts/erebus/`:

- `server.py`: a standard-library HTTP server. Each request goes through `pie.speak.speak` or `speak_ipa` with `backend="kokoro"`, so the server renders exactly what a local run renders. One lock serializes synthesis, because the pitch patch swaps a method on the shared model.
- `Dockerfile`:
  - base `python:3.12.13-slim-bookworm`, pinned by digest;
  - `torch==2.15.0+cpu` from the PyTorch CPU index;
  - `requirements.txt`, the exact freeze of `.venv-kokoro`;
  - the weights, fetched at build time by `pie.speak.kokoro_file` (the pinned revision and sha256 of §11.2) and baked into the image. At runtime the server runs with `HF_HUB_OFFLINE=1`.
- `deploy.sh`: run from the Mac. It stages the needed files from the committed HEAD with `git archive`:
  - `pie/{__init__,translit,phon,meter,ipa,speak}.py`;
  - `tts/espeak/mapping.json`, which `pie.speak` reads at import;
  - `tts/kokoro/vocab.json`;
  - the three `tts/erebus/` files.

  It then copies them to `~/pie-tts/` on erebus, builds `pie-tts:<git rev>` and `pie-tts:latest` there, starts the container and waits for `/health`.

**Footprint.** The deployment uses only the image `pie-tts:*`, the container `pie-tts` and the directory `~/pie-tts/` (the build context, about 200 KB). The existing `kokoro-tts` container (Kokoro-FastAPI on XPU, port 8880) and every other service are separate and untouched.

**Container settings:**
- `-p 127.0.0.1:8881:8881`: the port is bound to localhost on erebus only;
- `--restart unless-stopped`;
- `--cpus 6 --memory 6g --memory-swap 6g --pids-limit 256`;
- a read-only root filesystem with a 256 MB `/tmp` tmpfs;
- `--cap-drop ALL --security-opt no-new-privileges`, running as a non-root user;
- logs capped at 3 × 10 MB.

**Measured on 2026-10-28:**
- image 1.93 GB;
- about 2.1 GiB RAM, idle and while rendering;
- about 590% CPU (the 6-CPU cap) while rendering;
- about 0.4 × real time: 351 characters of PIE gave 35 s of audio in 14 s.

**API** (JSON in; `audio/wav` out, 16-bit mono 24 kHz):

| Endpoint | Body | Notes |
|---|---|---|
| `GET /health` | | `{"status": "ok", "revision", "voices", "torch", "threads", ...}` once the model and voices are loaded |
| `POST /speak` | `{"text": PIE, "voice": "hf_alpha", "pitch": true, "convention": "default", "tone": true, "speed": 0.9, "seed": null}` | Only `text` is required. `convention` is a key of `pie.ipa.CONVENTIONS`; `tone` is `true`, `false` or `"stress"` |
| `POST /speak_ipa` | `{"ipa": converter IPA, "voice", "pitch", "tone", "speed", "seed"}` | Used by the `kokoro-erebus` backend |

- **Limits:** `text` or `ipa` of at most 2,000 characters (413 above that) and a request body of at most 16 KB. `speed` must be in [0.5, 2.0].
- **Errors:** an unknown voice or convention, an out-of-vocab phone (`"type": "UnsupportedPhone"`), or a ‖ chunk over 510 phonemes gives 400 with `{"error", "type"}`.
- **Response headers:** a wav response carries `X-PIE-IPA`, `X-PIE-Engine-Input` and `X-PIE-Voice` (percent-encoded UTF-8).
- **Seed:** the Kokoro decoder adds random excitation noise, so two unseeded renders of the same input differ slightly. Two local runs give r ≈ 0.996-0.997 and identical length. `seed` fixes that noise, and with the same seed the service and a local CPU run agree to float drift.

**Commands** (from the Mac, in the repo):

```sh
sh tts/erebus/deploy.sh            # (re)deploy HEAD: stage, build on erebus, replace the pie-tts container
sh tts/erebus/deploy.sh status     # docker ps line, docker stats, /health
sh tts/erebus/deploy.sh logs 200   # last 200 log lines (one per request; request bodies are never logged)
sh tts/erebus/deploy.sh stop       # docker stop pie-tts   (stays stopped until started)
sh tts/erebus/deploy.sh start      # docker start pie-tts
sh tts/erebus/deploy.sh remove     # docker rm -f pie-tts; docker rmi the pie-tts images; rm -rf ~/pie-tts

ssh -N -L 8881:localhost:8881 erebus     # tunnel; then:
curl -s localhost:8881/health
curl -s -X POST localhost:8881/speak -H 'Content-Type: application/json' \
     -d '{"text": "h₂ówis h₁éḱwōs-kʷe", "voice": "hf_alpha", "pitch": true}' -o ovis.wav
uv run python -I scripts/speak.py --backend kokoro-erebus -o x.wav "deywós"   # no Kokoro env needed
```

On erebus itself: `docker logs -f pie-tts`, `docker stop pie-tts` and `docker start pie-tts`. Manual removal is `docker rm -f pie-tts; docker rmi pie-tts:latest pie-tts:<rev>; rm -rf ~/pie-tts`.

The client backend `kokoro-erebus` posts to `PIE_KOKORO_PITCH_URL` (default `http://localhost:8881`). `tests/test_speak.py::test_kokoro_erebus_renders` skips when `/health` does not answer within 2 s.

**Verification (2026-10-28, deployed revision c7d80e2).** Three pack lines (schleicher-1, king-1 and hymn-1) were sent through the tunnel to `/speak` as PIE text.
- The returned IPA and engine input equal the manifest's.
- Every sample count equals the local pack wav's.
- Unseeded, service vs pack gives r = 0.9956-0.9976, the same range as a local rerun vs pack (r = 0.9956-0.9975).
- With seed 1234 on both sides, service vs local gives r = 0.99996-1.00000 (max |Δ| ≤ 0.023 of full scale).
- F0 of `ɟʱi.méː` (Praat, as in tts-options.md §2.3) is the same track to the Hz on both sides: 171-204 Hz on ɟʱi, rising to a 271 Hz peak on méː. The earlier local measurement was 172-205 Hz, then 254-271 Hz.
