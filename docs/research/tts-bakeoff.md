# TTS bake-off: Kokoro voices × respellings of the hard sounds

Status: in progress (2026-10-29). Scope set by the owner: Kokoro only, all voices with the pitch patch, eSpeak (tone) as
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
     "audio": "h2ewsos__x__kokoro-hf_alpha.mp4",   // file name under audio_base (AAC in .mp4)
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
