# TTS bake-off: Kokoro voices × respellings of the hard sounds

Status: rendered, waiting for the owner's ratings (2026-10-29). Scope set by the owner: Kokoro only, all voices with the pitch patch, eSpeak (tone) as
the reference row. Piper was dropped ("it's terrible"). A parallel experiment re-voices eSpeak with voice conversion
(`tts/vc/`, separate agent); both feed one rating page.

## Manifest schema (`tts/bakeoff/manifest.json`, schema `pie-tts-bakeoff/1`)

Published early so that `tts/vc/manifest.json` can use the same fields. The rating page reads any number of
manifests with this schema and merges them on `words[].id` and `variants[].id`.

```jsonc
{
  "schema": "pie-tts-bakeoff/1",
  "source": "kokoro",                     // short name of this manifest ("kokoro", "vc")
  "generated": "2026-10-29",
  "audio_base": "audio/",                 // published path prefix of this manifest's audio on the rating page
  "targets": [                            // the hard sounds, in page order
    {"id": "h2", "label": "h₂ = χ", "note": "voiceless uvular fricative",
     "variants": [{"id": "chi", "label": "[χ]", "doc": "converter default"}, {"id": "x", "label": "[x]"}, ...]}
  ],
  "words": [                              // one target sound per word
    {"id": "h2ewsos", "pie": "h₂éwsos", "gloss": "dawn", "target": "h2"}
  ],
  "systems": [                            // the columns
    {"id": "kokoro-hf_alpha", "label": "Kokoro hf_alpha", "family": "kokoro", "language": "hi",
     "licence": "Apache-2.0", "reference": false}
  ],
  "clips": [
    {"id": "h2ewsos__x__kokoro-hf_alpha",  // {word}__{variant}__{system}; ASCII [a-z0-9_-] only
     "word": "h2ewsos", "variant": "x", "system": "kokoro-hf_alpha",
     "audio": "h2ewsos__x__kokoro-hf_alpha.mp4",   // per-clip file name (local; AAC in .mp4)
     "sprite": {"file": "kokoro-hf_alpha.mp4", "start": 12.4, "duration": 0.83},  // what the page plays: a slice
                                         // of one file per system under audio_base (seconds); optional, else "audio"
     "ipa": "xáw.sos",                   // the respelled converter IPA that was rendered
     "engine_input": "xáwsos",           // exactly what the engine received
     "same_as": null,                    // clip id with identical engine input for this system (no audio of its own)
     "duration_s": 0.92,
     "qc": {"ok": true, "flags": []}}    // automatic checks (silence, truncation, clipping)
  ]
}
```

Word ids (ASCII slugs): `h2ewsos h2owis` (χ), `h2egjeti gjenh1tor kjlewos` (ǵ/ḱ), `bhreh2ter dhugh2ter gwhenti`
(breathy stops), `kwetwores` (kʷ), `h3esth1` (h₃), `wlkwos kmtom` (syllabic), `ph2ter` (vocalized laryngeal),
`dyews` (accent), `h1esti` (h₁).

Variant ids per target: h2 `chi x voiced-uvular h`; dorsal `palatal fronted plain`; murmur `breathy aspirated plain`;
kw `labialized cluster`; h3 `gw-labialized gw-cluster rw-cluster`; syllabic `syllabic schwa`; ph2ter and dyews
`default`; h1 `h glottal-stop`.

A rating is stored at `ratings/{clip id}` as `{score: 1-5, note: string}`.

**Sprites.** An artifact version holds at most 511 files, so the page plays clips as slices of one AAC file per
system (`scripts/tts_bakeoff.py sprites`: the clips back to back, 0.5 s apart; afconvert compensates the codec
priming, measured lag 0 ms; the page still starts 50 ms early). A second source should do the same, or keep its
single-clip count low enough that the total stays under 511.

For a second source (the VC experiment): set `"source": "vc"` and `"audio_base": "vc/audio/"`, and give system ids a
prefix of their own (e.g. `espeak-vc-knnvc-hf_alpha`, label `eSpeak→VC kNN-VC/hf_alpha`). Reuse the word and
variant ids above so clips land on the same rows. An extra field `"audio_dir"` (repo path of the clip files, default
`tts/vc/audio`) tells `scripts/tts_bakeoff.py page-files` where to find them. Fields the page does not know are ignored.

## What was rendered

- **Grid:** 15 words, one target sound each, in every spelling of that sound (39 word × spelling rows). The other
  sounds of a word use the base spelling: the converter default, except that Kokoro gets h₂ as [x] outside the h₂
  rows. That follows the owner's χ test ([x] beat [χ] in every voice). eSpeak keeps [χ], because its pie table has
  no [x]. The ǵ/ḱ spellings are conventions (`dorsals` = palatal, `fronted`, `plain`); the rest are `pie.speak.PROFILES`.
- **Systems:** eSpeak `pie/pie-tone` (strict round trip on every clip), plus 19 Kokoro-82M v1.0 voices, all local
  PyTorch with the pitch patch, speed 0.9 and seed 0. The voices: Hindi `hf_alpha hf_beta hm_omega hm_psi`; Spanish
  `ef_dora em_alex em_santa`; Brazilian Portuguese `pf_dora pm_alex pm_santa`; French `ff_siwis`; Italian
  `if_sara im_nicola`; English `af_heart af_nicole bf_emma bf_isabella bm_lewis bm_george`. These are all the
  Kokoro voices in those languages, plus the English voices picked by the screen below. erebus was not used for
  rendering. It runs the same code, and its container is out of bounds beyond the pie-tts endpoint.
- **Dedupe:** a clip whose exact engine input equals another clip's for the same voice is not rendered again
  (`same_as`). For Kokoro, 7 of 39 rows collapse, because the vocab has no ʱ ʷ ̩: aspirated = breathy, kw = kʷ,
  ɣw = ɣʷ, and əl/əm = l̩/m̩. For eSpeak, 5 rows collapse (fronted = palatal, because the table writes kʲ as c;
  kw = kʷ; ɣw = ɣʷ), and 8 are refused up front: [x], [ʁ] and [ʰ] are not in the pie table. The page then shows the
  word's default eSpeak clip on those rows, marked as such.
- **Count:** 634 audio clips: Kokoro 32 per voice × 19 = 608, plus eSpeak 26. Published as 20 AAC sprites, one per
  system (5.5 MB). The per-clip .mp4 and .wav files stay local.

## Coverage (objective, before listening)

The **Kokoro input** column shows what `pie.speak`'s front end sends for each symbol. "Native" means the symbol is in
the shared 114-symbol vocab and goes through unchanged. The **label** columns count the sent form in each training
language's phoneme labels, produced the way Kokoro's training labels were: misaki's `EspeakG2P` (espeak-ng plus
misaki's mapping) over that language's UDHR text, about 1,500 words each (NLTK `udhr`). For English, the source is
misaki's own gold and silver lexicons (about 190,000 entries). A count of 0 means the voices of that language
probably never heard the symbol. A symbol in the vocab is only a valid id, not a trained sound.

| symbol | Kokoro input | eSpeak pie | en-gb labels | en-us labels | es labels | fr-fr labels | hi labels | it labels | pt-br labels |
|---|---|---|---|---|---|---|---|---|---|
| χ | native | yes | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| x | native | no | 0 | 0 | 40 | 0 | 0 | 0 | 46 |
| ʁ | native | no | 0 | 0 | 0 | 487 | 0 | 0 | 0 |
| h | native | yes | 10547 | 9594 | 0 | 0 | 70 | 0 | 0 |
| ʔ | native | yes | 0 | 440 | 0 | 0 | 0 | 0 | 0 |
| ħ | sent as χ | yes | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ɣ | native | yes | 0 | 0 | 43 | 0 | 5 | 0 | 0 |
| c | native | yes | 0 | 0 | 0 | 0 | 42 | 0 | 0 |
| ɟ | native | yes | 0 | 0 | 0 | 0 | 40 | 0 | 0 |
| kʲ | native | as c | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ɡʲ | native | as ɟ | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| k | native | yes | 72392 | 66468 | 277 | 267 | 215 | 222 | 230 |
| ɡ | native | yes | 17529 | 16668 | 5 | 31 | 46 | 41 | 113 |
| bʱ | sent as bʰ | yes | 0 | 0 | 0 | 0 | 39 | 0 | 0 |
| dʱ | sent as dʰ | yes | 0 | 0 | 0 | 0 | 35 | 0 | 0 |
| ɡʱ | sent as ɡʰ | yes | 0 | 0 | 0 | 0 | 13 | 0 | 0 |
| ɟʱ | sent as ɟʰ | yes | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| kʷ | sent as kw | yes | 2619 | 2357 | 15 | 0 | 0 | 28 | 13 |
| ɡʷ | sent as ɡw | yes | 356 | 293 | 0 | 0 | 0 | 18 | 18 |
| r̩ | sent as ər | yes | 0 | 0 | 0 | 0 | 6 | 0 | 0 |
| l̩ | sent as əl | yes | 8564 | 11482 | 0 | 7 | 6 | 0 | 0 |
| m̩ | sent as əm | yes | 7851 | 8544 | 0 | 10 | 14 | 0 | 6 |
| n̩ | sent as ən | yes | 15787 | 24174 | 0 | 2 | 18 | 0 | 7 |
| ə | native | yes | 116020 | 140660 | 0 | 235 | 191 | 0 | 95 |
| ː | native | yes | 70530 | 0 | 2 | 2 | 622 | 153 | 23 |

What the table explains:

- **χ is in no training language.** That is why [x] or [ʁ] beat it in every voice. [x] occurs only in es (the jota)
  and pt-br, where it is the rhotic of *carro*, *rato*. [ʁ] occurs only in fr. A Spanish voice is the natural home
  for [x].
- **ǵ fails because c and ɟ are Hindi affricates in Kokoro.** The only language with c/ɟ labels is Hindi, and there
  espeak-ng writes च ज as c ɟ: misaki gives चाय → `cˈaːj` and जल → `ɟˈʌl`. So every voice says ɟ as [dʒ]
  ("ha-je-tee"). eSpeak's pie table says a true palatal stop, which is why it alone gets near "ge". kʲ/ɡʲ are in the
  vocab, but ʲ is in no language's labels (misaki strips it from English), so [ɡʲ] is an untrained combination. Plain
  [ɡ k] are trained everywhere.
- **Murmur:** bʰ dʰ ɡʰ occur only in Hindi labels, where they are the breathy stops. Elsewhere ʰ after a voiced stop
  is untrained.
- **ʔ is trained only in en-us** (misaki's glottal stop), and h is barely present outside English and Hindi.
- **Syllabic resonants** are sent as əC in every voice, which matches English's ᵊl/ən-style labels.

eSpeak (reference) can say everything the converter emits except [x], [ʁ] and written [ʰ]. Its fronted velars are
said as the palatals.

## English voice screen

To pick English voices for [x], all 28 English voices (plus the other languages, for comparison) rendered
`xá.wis`, `á.xa`, `χá.wis` and `á.χa` (three seeds, median). The script measured frication: 10 ms frames that are
unvoiced (autocorrelation below 0.45), energetic and high in zero-crossing rate. The intervocalic `á.xa` is the clean
measure; the `xá.wis` numbers also include the final [s]. Best on `á.xa` (ms): af_nicole 150, bf_emma 130,
bf_isabella 130, bm_lewis 130, am_santa 120 (grade D−, left out), bm_fable 100. The pinned bm_george measured
**0 ms** for [x] in every probe. af_heart (60 ms) was added because it is Kokoro's top-graded voice.

## Automatic checks of the rendered clips

- **Basic QC** (silence, clipping, under 45 ms per phone, speech duration outside 0.65–1.6× the median of the same
  row across voices): 0 of 634 clips flagged. Durations range from 0.80× (ff_siwis, h₂ rows) to 1.44×
  (bm_george, which is slow overall). Kokoro dropped no whole syllable anywhere.
- **The word-initial voiceless fricative is the clear automatic failure.** Onset frication in the h₂ rows (ms
  before voicing, `h2ewsos`/`h2owis`): eSpeak [χ] 130/130 and [h] 70/70. In Kokoro, [χ] gets 0 ms in 17 of 19 voices,
  and [x] gets 0 ms in 13 voices. Measurable [x] only in af_nicole 110/30, bm_lewis 60/40, bf_emma 20/10,
  bf_isabella 0/70 and em_santa 30/0. In every other voice the h₂ onset is close to a bare vowel. Listening has to
  decide whether the weak onsets still read as [x], but the measurement says most voices drop it word-initially.

## Licences

- Kokoro-82M weights and voices: Apache-2.0. VOICES.md marks `ff_siwis` as trained on SIWIS data (CC BY).
- eSpeak-NG: GPL-3.0 engine and data; the audio output is not covered.
- No non-commercial voice is in the set (Piper's CC-BY-NC voices were the concern, and Piper is out).

## Files

- Clips: `tts/bakeoff/audio/` (gitignored; `.wav` + `.mp4`). Manifest: `tts/bakeoff/manifest.json` (committed).
- Rating page: `tts/bakeoff/rating-page/index.html`. It fetches `manifests/kokoro.json` and, if published,
  `manifests/vc.json`, and stores ratings in the artifact `db` (in memory only, with a notice, when `db` is
  unavailable). `scripts/tts_bakeoff.py page-files` writes `rating-page/files.txt` (published path ← source) and
  `files-1.json`, the Artifact `files` map: the manifest and 20 sprites, 6.1 MB with the page, one publish.
- Rebuild: `scripts/tts_bakeoff.py render` (also builds the sprites), `qc`, `sprites`, `coverage --texts <udhr dir>`,
  `page-files` (Kokoro env).
