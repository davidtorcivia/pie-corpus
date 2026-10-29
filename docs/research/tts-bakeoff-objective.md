# TTS bake-off: objective (machine) estimates

Status: computed 2026-10-29 over the 634 clips of `tts/bakeoff/manifest.json` (see `tts-bakeoff.md`). These are
**machine estimates**, made from a phone recognizer and from acoustic measures. They are meant to be set beside the
owner's ear ratings, and they do not replace them. Nobody has listened to produce these numbers. Where the recognizer
cannot hear a distinction, the acoustic measure decides, and the tables say which one did (`basis` per clip in
`tts/bakeoff/objective.json`).

## Headline

- **Top 3 (estimated):** `bf_isabella` 3.87, `af_nicole` 3.84, `em_santa` 3.60. The two leaders are within
  noise of each other. A leave-one-word-out check (15 reruns, each dropping one word) keeps `af_nicole` and
  `bf_isabella` in the top 3 every time and `em_santa` in 12 of 15. The runs-up, `pm_alex`, `pm_santa` and
  `af_heart`, each got in once.
- **eSpeak** is the reference for the acoustic measures: its [χ] frication is 130 ms and its accent F0 peak is right
  in 24 of 24 clips. Its **recognizer-based** numbers cannot be compared with Kokoro's, because the recognizer is out
  of its domain on formant synthesis (see Caveats). Its estimated score, 2.66, is mostly that failure.
- **Clear objective findings,** robust to the scoring choices:
  1. The `palatal` dorsal spelling ([ɟ c]) is an affricate in every Kokoro voice. 56 of the 57 Kokoro clips are graded
     wrong: the recognizer hears [dʒ]/[tʃ] in 48 of them and another sibilant in 6. The release noise is 25–75 ms,
     against 0–25 ms for [ɡ k]. The `fronted` ([ɡʲ kʲ]) and `plain`
     ([ɡ k]) spellings avoid it.
  2. Word-initial h₂ is a dorsal fricative only in `af_nicole` and `bm_lewis` (100–120 ms of frication for [x] and [ʁ]).
     `em_santa` and `bf_isabella` manage it in one word or one spelling. Every other voice gives at most a faint [h]
     (0–40 ms).
  3. Kokoro's accent (pitch patch) lands on the accented syllable in most clips. The voices' mean lead is 0.4–3.3
     semitones over the highest other syllable; `ff_siwis`, `im_nicola` and the Hindi voices are weakest.

## Per voice

The score formula is stated, not tuned:

> **score = 1 + 4 × (0.3 × (1 − min(PER_broad, 1)) + 0.7 × mean over the 8 classes of the best-spelling hit rate)**

Here the hit rate is (correct + 0.5 × near) / graded clips. "Best spelling" means the voice's best variant of that
sound, which is what its recommended profile would send. PER is the mean over the voice's distinct audio clips. The
class columns show the hit rate at the best spelling, with that spelling in brackets. Accent is graded over every
polysyllabic clip (n = 31 per Kokoro voice, 24 for eSpeak).

| voice | score | PER broad | PER strict | ins/clip | χ (h₂) | ǵ/ḱ | breathy | kʷ | h₃ | syllabic | h₁ | accent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eSpeak (ref.) | 2.66 | 0.52 | 0.53 | 0.2 | 1.00 (chi) | 0.33 (palatal) | 0.00 (breathy) | 0.00 (labialized) | 0.00 (gw-labialized) | 0.25 (syllabic) | 0.50 (h) | 1.00 |
| bf_isabella | 3.87 | 0.38 | 0.47 | 0.8 | 0.50 (x) | 0.83 (fronted) | 0.67 (breathy) | 1.00 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 1.00 (h) | 0.82 |
| af_nicole | 3.84 | 0.33 | 0.42 | 0.1 | 1.00 (x) | 0.50 (fronted) | 0.50 (breathy) | 1.00 (labialized) | 0.50 (gw-labialized) | 0.50 (syllabic) | 1.00 (h) | 0.82 |
| em_santa | 3.60 | 0.50 | 0.59 | 0.7 | 0.75 (voiced-uvular) | 0.67 (plain) | 0.83 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 1.00 (h) | 0.71 |
| pm_alex | 3.53 | 0.49 | 0.55 | 0.8 | 0.25 (h) | 0.67 (fronted) | 1.00 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 1.00 (h) | 0.82 |
| af_heart | 3.51 | 0.48 | 0.55 | 0.7 | 0.25 (h) | 0.67 (fronted) | 0.50 (breathy) | 1.00 (labialized) | 0.50 (rw-cluster) | 0.75 (syllabic) | 1.00 (h) | 0.71 |
| pm_santa | 3.49 | 0.48 | 0.56 | 0.6 | 0.50 (h) | 0.50 (fronted) | 0.83 (breathy) | 1.00 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 0.50 (h) | 0.75 |
| bm_lewis | 3.42 | 0.47 | 0.59 | 0.6 | 1.00 (x) | 0.50 (fronted) | 0.83 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.50 (syllabic) | 0.50 (h) | 0.74 |
| if_sara | 3.33 | 0.44 | 0.47 | 0.7 | 0.00 (chi) | 0.67 (fronted) | 0.67 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 1.00 (h) | 0.65 |
| bf_emma | 3.31 | 0.51 | 0.61 | 1.0 | 0.25 (x) | 0.67 (fronted) | 0.67 (breathy) | 1.00 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 0.50 (h) | 0.57 |
| em_alex | 3.30 | 0.45 | 0.52 | 0.6 | 0.50 (voiced-uvular) | 0.67 (fronted) | 0.50 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 0.50 (h) | 0.78 |
| pf_dora | 3.27 | 0.51 | 0.57 | 0.8 | 0.25 (voiced-uvular) | 0.83 (fronted) | 0.67 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.75 (syllabic) | 0.50 (h) | 0.82 |
| bm_george | 3.23 | 0.54 | 0.65 | 1.0 | 0.00 (chi) | 0.50 (plain) | 0.50 (breathy) | 0.50 (labialized) | 0.50 (rw-cluster) | 1.00 (syllabic) | 1.00 (h) | 0.81 |
| hf_beta | 3.06 | 0.53 | 0.56 | 0.8 | 0.00 (chi) | 0.67 (fronted) | 0.50 (breathy) | 0.50 (labialized) | 0.50 (rw-cluster) | 0.50 (syllabic) | 1.00 (h) | 0.58 |
| im_nicola | 3.04 | 0.46 | 0.50 | 0.7 | 0.00 (chi) | 0.50 (plain) | 0.50 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 1.00 (syllabic) | 0.50 (h) | 0.48 |
| ef_dora | 2.96 | 0.50 | 0.55 | 0.7 | 0.00 (chi) | 0.67 (fronted) | 0.50 (breathy) | 0.50 (labialized) | 0.50 (gw-labialized) | 0.50 (syllabic) | 0.50 (h) | 0.72 |
| ff_siwis | 2.75 | 0.56 | 0.59 | 0.8 | 0.00 (chi) | 0.83 (fronted) | 0.50 (breathy) | 0.00 (labialized) | 0.00 (gw-labialized) | 0.75 (syllabic) | 1.00 (h) | 0.40 |
| hm_psi | 2.65 | 0.57 | 0.62 | 1.1 | 0.25 (h) | 0.50 (fronted) | 0.50 (breathy) | 0.50 (labialized) | 0.00 (gw-labialized) | 0.50 (syllabic) | 0.50 (h) | 0.48 |
| hm_omega | 2.57 | 0.61 | 0.65 | 1.1 | 0.00 (chi) | 0.50 (fronted) | 0.67 (breathy) | 0.00 (labialized) | 0.50 (gw-labialized) | 0.50 (syllabic) | 0.50 (h) | 0.47 |
| hf_alpha | 2.52 | 0.67 | 0.71 | 1.6 | 0.00 (chi) | 0.50 (fronted) | 0.50 (breathy) | 0.00 (labialized) | 0.50 (gw-labialized) | 0.50 (syllabic) | 0.50 (h) | 0.71 |

"ins/clip" counts recognized phones with no counterpart in the target. In the Hindi voices it is mostly a vowel
before the word (`ɐ h…`, `a h…`, `i ɡ…`). Kokoro's Hindi voices seem to open a word that starts with a laryngeal or a
cluster with a short vowel. Listening should confirm that.

### Acoustic measures per voice

| voice | h₂ frication ms, [χ] / [x] / [ʁ] / [h] (mean of 2 words) | ǵ/ḱ release noise ms, palatal / fronted / plain (mean of 3) | murmur ΔH1–H2 dB / ΔHNR dB, breathy − plain (mean of 3) | accent: mean F0 lead, st | dyews F0 rise, st |
|---|---|---|---|---|---|
| eSpeak (ref.) | 130 / – / – / 82 | 30 / 30 / 8 | 1.5 / −1.5 | 3.0 | 0.7 |
| bf_isabella | 8 / 55 / 48 / 75 | 52 / 30 / 10 | 0.6 / −5.1 | 1.6 | 2.1 |
| af_nicole | 75 / 118 / 112 / 112 | 62 / 45 / 22 | (−19.5) / −0.3 | 1.5 | (16.0) |
| em_santa | 40 / 25 / 88 / 72 | 47 / 15 / 2 | 6.6 / −7.4 | 1.7 | 2.7 |
| pm_alex | 10 / 18 / 18 / 32 | 58 / 15 / 22 | 3.8 / −3.9 | 1.7 | 3.1 |
| af_heart | 5 / 8 / 0 / 38 | 52 / 37 / 25 | 1.5 / −1.6 | 1.9 | 0.3 |
| pm_santa | 8 / 20 / 10 / 60 | 65 / 18 / 22 | 2.3 / 3.9 | 1.7 | 2.7 |
| bm_lewis | 75 / 108 / 122 / 100 | 52 / 33 / 10 | 6.2 / −1.3 | 3.3 | 4.0 |
| if_sara | 0 / 2 / 0 / 2 | 28 / 18 / 2 | −1.0 / 0.6 | 1.2 | 0.6 |
| bf_emma | 2 / 28 / 22 / 48 | 60 / 32 / 25 | 4.5 / 2.0 | 0.9 | 1.6 |
| em_alex | 15 / 25 / 38 / 38 | 50 / 13 / 0 | −3.2 / 0.3 | 1.7 | 2.7 |
| pf_dora | 10 / 10 / 22 / 10 | 53 / 12 / 3 | 6.9 / 0.2 | 1.6 | 2.0 |
| bm_george | 10 / 8 / 10 / 12 | 25 / 15 / 2 | 0.7 / −1.0 | 1.6 | 5.8 |
| hf_beta | 0 / 0 / 0 / 0 | 10 / 8 / 2 | 1.1 / 1.1 | 1.0 | 0.4 |
| im_nicola | 8 / 10 / 12 / 8 | 18 / 0 / 0 | −2.6 / 0.9 | 0.7 | 1.1 |
| ef_dora | 2 / 15 / 12 / 12 | 40 / 13 / 2 | 3.1 / −1.5 | 1.3 | 2.2 |
| ff_siwis | 0 / 8 / 2 / 10 | 37 / 12 / 2 | −3.3 / −4.2 | 0.4 | 0.1 |
| hm_psi | 0 / 5 / 0 / 18 | 17 / 0 / 0 | −3.3 / −0.1 | 0.8 | 0.4 |
| hm_omega | 0 / 2 / 8 / 2 | 20 / 2 / 0 | −1.6 / −0.9 | 0.9 | 0.6 |
| hf_alpha | 0 / 2 / 5 / 0 | 48 / 37 / 8 | 5.3 / −8.0 | 1.2 | 2.4 |

Values in brackets are measurement failures. `af_nicole` says the breathy stops voiceless ([p t k] with 75–115 ms of
aspiration), so there is no modal-voice H1–H2 to compare. Its `dyews` F0 track has an octave jump. The h₂ numbers
agree with the onset-frication figures in `tts-bakeoff.md`, which were measured the same way: unvoiced by Praat's
autocorrelation pitch (threshold 0.45), above −40 dB.

## Per sound class: best voice and best spelling

The best spelling is the mean hit rate of that spelling over the 19 Kokoro voices. The best voices are those with the
highest best-spelling hit; ties are broken by the mean over all spellings.

| class | best Kokoro voice(s) (hit) | best spelling (Kokoro mean hit per spelling) | eSpeak |
|---|---|---|---|
| χ (h₂) | af_nicole, bm_lewis (1.00) | **none is good**: voiced-uvular 0.21 ≈ h 0.20 ≈ x 0.17 > chi 0.07 | 1.00 |
| ǵ/ḱ | bf_isabella, pf_dora, ff_siwis (0.83) | **fronted 0.60** > plain 0.51 ≫ palatal 0.01 | 0.33 |
| breathy | pm_alex (1.00) | breathy = aspirated 0.62 (same input) > plain 0.49 | 0.00 (recognizer fails) |
| kʷ | af_nicole, bf_isabella, pm_santa, af_heart, bf_emma (1.00) | labialized = cluster 0.55 (same input) | 0.00 (recognizer fails) |
| h₃ | bm_lewis, pm_alex, hm_omega (0.50) | gw-labialized = gw-cluster 0.37 (same input) > rw-cluster 0.16 | 0.00 (recognizer fails) |
| syllabic | im_nicola, bm_george (1.00) | syllabic = schwa 0.68 (same input) | 0.25 |
| h₁ | af_nicole, bf_isabella, if_sara, af_heart, pm_alex, em_santa, hf_beta, bm_george (1.00) | **h 0.74** > glottal-stop 0.47 | 0.50 |
| accent | af_nicole, bf_isabella (0.82) | n/a | 1.00 |
| (H̥ → ə, not scored) | 12 voices at 1.00 | n/a | 0.50 |

For Kokoro, `breathy`/`aspirated`, `labialized`/`cluster`, `gw-labialized`/`gw-cluster` and `syllabic`/`schwa` send the
**identical** engine input (`same_as` in the manifest; Kokoro's vocab has no ʱ ʷ ̩). The equal rates are by
construction, not a finding. Among the h₂ spellings, the differences between x, ʁ and h are a few clips across 19
voices: only `chi` is clearly worse. A voice that can make the fricative at all does so for [x] and [ʁ] alike
(af_nicole, bm_lewis), and `em_santa` does it only for [ʁ].

## Top 3 voices and recommended profiles

The recommendation is the best spelling per class for that voice; ties go to the converter default. The dorsal
spellings are `pie.ipa` conventions, not `pie.speak.PROFILES` entries. Everything else is a `PROFILES` name.
`default` means no respelling.

| voice | h₂ | ǵ/ḱ | breathy | kʷ | h₃ | syllabic | h₁ | combined |
|---|---|---|---|---|---|---|---|---|
| **bf_isabella** | h2-velar | convention dorsals=fronted | default | default | default | default | default | `h2-velar` + dorsals=fronted |
| **af_nicole** | h2-velar | convention dorsals=fronted (= plain, tie) | default | default | default | default | default | `h2-velar` + dorsals=fronted |
| **em_santa** | h2-voiced-uvular | convention dorsals=plain | default | default | default | default | default | `h2-voiced-uvular` + dorsals=plain |
| pm_alex (4th) | h2-h (all weak) | convention dorsals=fronted | default | default | default | default | default | `h2-h` + dorsals=fronted |
| af_heart (5th) | h2-h (all weak) | convention dorsals=fronted | default | default | h3-voiced-uvular-w | default | default | `h2-h` + `h3-voiced-uvular-w` + dorsals=fronted |

Notes on the profiles:

- `default` for breathy, kʷ, h₃ and syllabic is the same input as `murmur-aspirated`, `labiovelar-cluster`,
  `h3-unrounded-w` and `syllabic-schwa` in Kokoro. `murmur-plain` was never better than the default in any voice.
- `af_nicole`'s fronted and plain dorsals tie at 0.50 (plain velars in every word), so its pick is a tie-break. For
  `em_santa`, plain beat fronted in one word (`h2egjeti`).
- `h1-glottal-stop` is never recommended. The recognizer hears a stop ([d t b v]) under it in 18 of 19 voices. None
  of them shows a measurable release burst, so they count as near (a possible glottal onset). Only the ear can tell
  [ʔ] from a weak [d]. Kokoro has [ʔ] in its vocab, but it was trained only in en-us.

## Method

**Recognizer.** `facebook/wav2vec2-xlsr-53-espeak-cv-ft` @ `2c733782`, Apache-2.0. It is reused from the VC experiment
(`tts/vc/recognize.py`, weights in `tts/vc/cache/hf`, gitignored). Decoding is greedy CTC over the model's own
`vocab.json`. Each recognized token keeps its 20 ms frame times, which place the acoustic windows.

**Target.** Each clip is scored against its word's converter IPA in the default convention (`words[].ipa` in the
manifest), not against the respelled clip IPA. So a `plain` dorsal clip is still scored against [ɟ], and Kokoro's
base [x] for h₂ outside the h₂ rows is scored against [χ].

**Symbol mapping.** Both sides are mapped to one decomposed alphabet before the Levenshtein distance:

| converter IPA | recognizer units | | recognizer token | units |
|---|---|---|---|---|
| bʱ dʱ ɡʱ | bʰ dʰ ɡʰ (the model's murmur symbols, Hindi labels) | | aʊ eɪ oʊ aɪ ɔɪ | a w, e j, o w, a j, o j |
| ɡʷʱ | ɡʰ w | | əl, l̩, n̩, ɚ | ə l, ə l, ə n, ə r |
| kʷ ɡʷ ɣʷ | k w, ɡ w, ɣ w (the vocab has no ʷ) | | X, kh/th/ph | χ, kʰ/tʰ/pʰ |
| l̩ m̩ n̩ r̩ | ə l, ə m, ə n, ə r (no m̩ in the vocab) | | iː, i5, … | length and tone digits stripped |
| acute, ː, syllable dots | removed (dots kept for syllable boundaries) | | dʒ tʃ ts | kept as single units |

**PER strict** is the Levenshtein distance over these units divided by the target length. **PER broad** also merges
vowel quality (ɛ→e, ɔ→o, ɪ ɨ→i, ʊ→u, ɑ æ→a, ɐ ʌ ɜ→ə) and rhotic type (ɾ ɹ ʁ ɻ→r), which the recognizer's
language-biased labels blur, and it is the PER used in the score. h/x/χ, ɡ/ɣ, ɟ/dʒ and voicing stay distinct.

**Target slot.** A phonetically weighted alignment of target to recognized units (similar consonants 0.6, a
vowel↔consonant substitution never cheaper than an insertion plus a deletion) finds what the recognizer heard in the
tested sound's position. That includes insertions right after it, so [d h] fills the dʰ slot. It also records vowels
inserted just before it.

**Grades** (correct = 1, near = 0.5, wrong and missing = 0):

| class | correct | near | wrong / missing |
|---|---|---|---|
| χ (h₂, 2 words) | the recognizer hears [χ x]; or it hears a fricative (incl. [f θ ʃ], which it uses for eSpeak's [χ]) and **≥ 80 ms** of voiceless frication, for any spelling but `h` | 30–80 ms of frication (≥ 80 ms in the `h` spelling, which is [h] by design); capped at near when a vowel is inserted before it | a weak [h] with < 30 ms; a stop or other consonant; a vowel onset |
| ǵ/ḱ (3 words) | [ɟ c ɡʲ kʲ], velar + [j], or [j] with a 5–25 ms burst (eSpeak's palatal stop) | a plain [ɡ k] (+ an inserted [i]); a palatal with > 45 ms of noise | [dʒ tʃ ʒ ʃ z s ts tɕ dʑ] |
| breathy (3 words) | voiced stop + [h], or [bʰ dʰ ɡʰ]; or a plain voiced stop with ΔH1–H2 ≥ +3 dB **and** ΔHNR ≤ −2 dB against the same voice's plain clip | voiced stop without murmur; voiceless aspirated stop | voiceless unaspirated stop or other consonant |
| kʷ | [k w] | [ɡ w], [k] | other |
| h₃ | dorsal fricative + [w] | dorsal fricative alone, [ɡ](+w), [h w] | other consonant / vowel onset |
| syllabic (2 words) | a central vowel (ə ʌ ɐ ɨ ɪ ɜ) or none + [l]/[m] | a full vowel + [l]/[m] | no [l]/[m] |
| h₁ | [h] | [h] after an inserted vowel; [ʔ]; a stop label with no release burst (a glottal onset); a voiceless onset ≥ 40 ms under another fricative label | a stop with a burst |
| accent | the median F0 of the accented syllable is ≥ 1 st above every other syllable | 0–1 st above | below another syllable |

**Acoustic measures.** These are computed with parselmouth (Praat) and numpy at a 5 ms hop.

- *h₂ frication:* the longest run of unvoiced frames above −40 dB (Praat AC pitch, voicing threshold 0.45) between
  speech onset and the following vowel. The power-weighted spectral centroid is also stored.
- *ǵ/ḱ release noise:* the longest run of frames whose energy is mostly above 2.5 kHz (ratio ≥ 0.3, above −35 dB)
  between the preceding and following vowel; voicing is allowed. Against the recognizer's labels, [ɡ k] gave 0–25 ms
  in most clips and [dʒ tʃ] 25–75 ms, so 30 ms is the affricate line. The measure is less clean for word-initial ḱ
  before [l], where aspiration adds to the noise.
- *Breathy voice:* the uncorrected H1–H2 and the HNR over the first 40 ms of voicing after the release, reported as
  breathy − plain for the same voice and word.
- *Accent:* syllable spans are halfway between the aligned vowel nuclei, using the median F0 per syllable. `dyews` has
  one syllable, so only its F0 rise (middle third against first third) is reported.

## Caveats: where the machine is unreliable

- **The recognizer never emits χ in an h₂ slot, never emits ʔ, and almost never emits a murmured stop symbol.** That
  confirms the earlier finding in `tts-options.md`. It hears even eSpeak's 130 ms [χ] as [h], and it hears Kokoro's
  [x] as [h] everywhere. The h₂ grades are therefore **acoustic**: frication duration. Duration and centroid do
  **not** separate [h] from [x]/[χ]; eSpeak's [h] has 82 ms and a centroid near 2.1 kHz, its [χ] 130 ms and 2.3 kHz.
  A long fricative in an [x]/[ʁ] spelling is therefore counted as correct on the strength of the spelling, and only
  the ear can tell whether it is dorsal.
- **Murmur:** the recognizer heard a voiced stop followed by [h] in 20 of the 57 distinct Kokoro breathy clips. 14 of
  them are `dhugh2ter`, where almost every voice does it. This is likely real aspiration, but it may also be breathy
  release heard as [h]. The paired H1–H2 is noisy: even eSpeak's breathy stops show only +1.5 dB. It upgraded just
  2 clips (4 rows with their `same_as` copies).
  Treat the breathy column as "is there an [h]-like release", not as a measured breathy voice.
- **h₁ as [ʔ]:** it cannot be verified, so "glottal onset" means only "the recognizer's [d]/[t] has no burst
  above 2.5 kHz". The burst detector may simply miss a weak voiced [d], so the `glottal-stop` near grades are
  generous.
- **eSpeak is out of domain for the recognizer.** It loses whole onsets (`bʱráχ.teːr` → `a x d ɨ m`, `djéːws` →
  `eɪ ʃ`) and hears [kʷ] as [k m]. eSpeak's PER and its zeros for breathy, kʷ and h₃ are recognizer failures, not
  eSpeak failures. Use eSpeak only as the acoustic reference (frication, bursts, F0).
- **Small samples.** Each class has 1–3 words, so one clip moves a hit rate by 0.17–0.5. The score differences below
  about 0.15 are within this noise. The leave-one-word-out check says the top two are stable and the third is likely;
  the order below that should not be read closely.
- **The F0 tracker** makes octave errors and catches creak. `bm_lewis`'s creaky word-final syllables inflate his accent
  leads; `af_nicole`'s `dyews` rise of 16 st is an octave jump.
- **Vowel labels** come from the recognizer's English, Romance and other training data. Broad PER merges them, but
  quality-level judgements, for example of [ə] in the syllabic rows, lean on labels such as [ɪ ʌ] that may just be
  the recognizer's habits.

## Files and rerun

- `scripts/tts_bakeoff_objective.py`: run with `tts/vc/.venv-eval/bin/python -I scripts/tts_bakeoff_objective.py
  recognize|measure|analyze --cache <dir>`. The cache holds the CTC log-probs and raw measures and lives outside the
  repo; recognition takes about 2 minutes on CPU.
- `tts/bakeoff/objective.json` (schema `pie-tts-bakeoff-objective/1`): the formula and thresholds; `voices` (PER,
  per-class hit by spelling with per-word grades, score, profile); `by_class`; `ranking`, `top3` and the
  leave-one-word-out counts; `clips` (every manifest row, with recognized phones, slot, grade, basis and raw
  measures). Rows with `same_as` carry the grades of the clip whose audio they reuse (`audio_of`). The 8 eSpeak rows
  that were refused (no audio) are left out.
