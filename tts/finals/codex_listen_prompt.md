# Blind listening test: reconstructed Proto-Indo-European speech

You are a listener on a panel choosing the speech voice for a reconstructed Proto-Indo-European (PIE) language model. Score these clips by **listening to them**.

Do not run transcription, spectrogram, pitch-tracking or other audio-analysis software. Machine measurements are already collected separately. What is wanted from you is a listener's judgement. If you cannot hear a clip, leave its scores empty and write `could not hear` in the note. Do not guess.

## Contents

- `clips/NN_item/A.wav` … `H.wav`: 28 items × 8 systems = 224 clips, mono 16-bit WAV, loudness-matched.
  - Items 1–10 are whole short hymns of roughly 10–40 s.
  - Items 11–26 are single hard words.
  - Items 27–28 are hymn lines.
- Each letter A–H is the same speech system in every item. The letters are blind. One system may be a robotic formant synthesizer that is accurate but unnatural; the others are neural voices.
- `items.csv`: for each item, the PIE text, the **target IPA** and an English translation.
- `ratings.csv`: the score sheet to fill in. Return it with every row filled.

## Target pronunciation

The target IPA in `items.csv` is the reference. The key sounds:

| PIE | Target | Also acceptable |
|---|---|---|
| h₁ | [h] | a glottal stop or a light breath |
| h₂ | [χ] (voiceless uvular fricative, as in German *Bach* or Spanish *jota*) | [x], [ʁ]. Bad: silent, or plain [h] |
| h₃ | [ɣʷ] (voiced, rounded back fricative) | [ʁʷ], [ɣ] |
| ḱ ǵ ǵʰ | [c ɟ ɟʱ] (palatal stops) | fronted [kʲ ɡʲ], or plain [k ɡ]. Bad: affricates like English *ch* or *j* |
| bʰ dʰ gʰ | breathy-voiced stops [bʱ dʱ ɡʱ] | plain [b d ɡ] with some aspiration |
| kʷ gʷ | labialised [kʷ ɡʷ] | |
| ´ (acute) | the accented syllable has **high pitch**, the PIE pitch accent | stress-plus-pitch |
| r̥ l̥ m̥ n̥ | syllabic sonorants | |

## Scores

Score each clip from 1 to 5 on four scales:

- **accuracy**: how closely the clip matches the target IPA, given the table above. Check the hard sounds (h₂, ḱ/ǵ, the breathy stops) and whether the accented syllable is high. Missing or inserted syllables count against it.
- **clarity**: whether a listener reading the IPA could follow along and identify each word.
- **naturalness**: whether it sounds like a human voice: no robotic buzz, warbling, metallic artefacts, slurring or odd pauses.
- **overall**: which system you would choose to speak this language in a public demo. Weigh accuracy and naturalness. A clip that is natural but wrong should not score 5.

In **note**, write a few words on what you heard, for example "h₂ came out as [h]", "ǵ sounds like j in jam", "accent lands on the wrong syllable", "metallic warble at 12 s" or "best h₂ of the set".

## Return

1. The completed `ratings.csv`.
2. A short summary of no more than 300 words:
   - Rank systems A–H overall.
   - Give each one's main strength and weakness.
   - Say which consistently handles h₂ and ḱ/ǵ best.
   - Say whether any system is clearly unacceptable for a demo.
