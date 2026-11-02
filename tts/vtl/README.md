# PIE → VocalTractLab (v10)

This tool compiles PIE IPA straight into a VocalTractLab gestural score. It bypasses VTL's German-only
phoneme converter, then synthesizes the score, patches what VTL can't make, and writes exact phone
timings next to every render.

**New in v10:** phrase ends keep their pitch. The decay is unchanged, but F0 no longer sags or dives into it.
A final m n l hums for at most ~100 ms and then trails off in breath (details under "Changes in v10").

**New in v9:** `--phrase-end` (on by default): before every pause of 0.2 s or more, a word's last voiced sound trails off
over 100–250 ms instead of stopping dead. It runs on the new timelines, where words inside a phrase join directly
(details under "Changes in v9"). `--no-phrase-end` gives v8's ends.

**New in v8:** `--final-h murmur`, which renders word-final H as a voiced, breathy, falling vowel tail instead of a
voiceless h (details under "Changes in v8"). The default (`--final-h noise`) renders exactly as v7.

**New in v7** (details under "Changes in v7"):
- The hymn at `--accent-range 4.0` (≈ eSpeak, +3.1 st) next to 4.6 (+3.5 st), both voices, for the ElevenLabs A/B
- Word-final H no longer lets VTL's own voicing through when it is short (the middle túH)
- h coloured by u/o/w is 5 dB louder (o: 3.3 dB), so dark h is as loud as the others; colour unchanged
- JD3: murmur −3 dB and a 25 ms spill (the i after ɡʷʱ: −7.5 → −6.4 dB)
- The `--declination 2,-3.5` renders are gone; the default 1.5,−2.5 stays

**New in v6** (details under "Changes in v6"):
- Vowels after ʱ are no longer swallowed: a murmur that keeps its level, a shorter capped spill, and modal voicing protected on both sides
- Oral gestures lead the score by 30 ms, so stop releases land on the JSON boundary (they were ~30 ms late)
- Per-vowel QC gate (level and voicing), a slope-corrected accent measure, and QC for ElevenLabs output
- A QC tracker bug fixed (0.2% clock drift: up to 60 ms late at the end of a 30 s clip)
- h at −14 dB with a 40 ms final fade

v5 added female and male voices, syllabic r̩/l̩, the darker h, `--lax-short`, the trill hack, and batch mode.
The timeline mode and the timing JSON are unchanged: the JD3 hymn JSON is still identical to v4, phone for phone.

## Voices

| speaker file | voice | engine | hymn QC (accent / h median / flags) | hard test QC |
|---|---|---|---|---|
| `JD3-PIE.speaker` | male (VTL's JD3, the v1–v4 voice) | pip `vocaltractlab-cython` | +3.54 st / 0.52 / 1 short ə (at 4.0: **pass**, +3.08) | +3.33 st / 0.56 / 2 short ə |
| `W02-PIE.speaker` | **female** (VTL 2.4 W02) | VTL 2.4 API | +3.54 st / 0.33 / **pass** (at 4.0: **pass**, +3.06) | +3.33 st / 0.45 / 1 short ə |
| `M01-PIE.speaker` | male, alternate (VTL 2.4 M01) | VTL 2.4 API | +3.55 st / 0.53 / 1 vowel at −8.2 dB | not rendered |

Every nucleus in every render has tracked voicing. "Short ə" means an interconsonantal schwa of 57–68 ms
with 30–35 ms of voicing, against the 40 ms gate: dh₃dʰí, ǵénh₁tor, ph₂tḗr (see Known limits).

The baseline pitch defaults to each speaker's rest F0 minus 3 st:
- JD3 and M01 ≈ 101 Hz
- W02 ≈ 185 Hz

`--pitch` overrides this.

The VTL 2.4 voices use the 2025 glottis model, which the pip package can't load. `vtlengine.py` picks
the engine from the speaker file, so the commands are the same for every voice.

### Setup

```
pip install vocaltractlab-cython numpy scipy
```

- **Windows:** copy `API/VocalTractLabApi.dll`, `msvcp140.dll`, `vcruntime140.dll` and `vcruntime140_1.dll`
  from `VTL2.4.zip` next to `vtlengine.py`. The DLL path is untested here (built and tested on Linux).
- **Linux/macOS:** run `./build_vtl24.sh VTL2.4.zip`, which builds `libvtl24.so`/`.dylib` from the zip's
  sources (needs g++). A Linux x86-64 build is included in `linux/`.
- **Elsewhere:** set `VTL24_LIB=/path/to/lib` to point at the library.

`make_speaker.py OUT --base BASE` rebuilds a PIE voice from any VTL speaker in either format. Every shape it
adds is tuned on that voice's own anatomy, and its glottis settings are scaled from the voice's own
modal and voiceless shapes. The two models use very different scales: modal fold gap 0.0515 for W02 vs 0.0102 for JD3.

| added shape | JD3 | W02 / M01 |
|---|---|---|
| palatal closure (c) | tongue body raised +0.5 cm | velar closure slid 3 mm forward (2.4 can't close from the fricative) |
| lip rounding (ʷ) | lip opening 0.3–0.6 cm² | same |
| alveolar approximant (r̩) | tip lowered to 0.35 cm² | same |
| murmur, voiceless-uvular, -unaspirated, aspirate | relative to JD3's shapes | relative to W02/M01's shapes |

**Timing compensation** (measured on the hard test, both engines):

| lag | measured | compensation (default) | flag |
|---|---|---|---|
| stop release vs score | ~30 ms late | oral and velic tiers lead by 30 ms → releases at 0 to +8 ms | `--oral-advance` |
| voicing onset after a voiceless sound | pip ~30 ms, 2.4 ~40 ms | onsets lead by 30 / 40 ms, eating into the voiceless sound (which keeps ≥ 40% of itself) | `--glottis-advance` |
| voicing offset before a voiceless sound | small; 2.4 slightly late | openings lead by 0 / 20 ms, never into a vowel's 55 ms of modal voicing | `--abduct-advance` |

In v5 the 2.4 advance moved the whole glottal tier, openings included, which stacked with the glottal
lead before voiceless sounds and ate short vowels. Now only the onsets move.

## Run

```
python pie_vtl.py --timeline dawn-hymn-cadence.json out --speaker W02-PIE.speaker   # one clip
python pie_vtl.py hymn.txt out                                                     # text mode
python qc.py out                                                                   # QC report for out.wav + out.json
```

### Batch (the assembly line)

```
python pie_vtl.py --batch clips/ --speakers JD3-PIE.speaker,W02-PIE.speaker \
       --out-dir renders --vary-pitch 2 --vary-accent 0.4 --seed 0
```

- **Input:** `--batch` takes a folder of timeline JSONs, or a `.txt` list of their paths.
- **Engines:** VTL starts once per speaker.
- **Output:** every clip gets `CLIP__SPEAKER.wav/.json/.TextGrid/.tsv/.ges`.
- **Manifest:** `manifest.jsonl` gets one line per clip, with the seed, the pitch and accent actually used, the render time, and the full QC record.
- **Seeds:** each clip's seed is `sha1(clip|speaker|--seed)`. It drives the noise in the χ/h patches and
  the variation draw. Reruns are bit-identical, and so is any speaker order (checked with md5).
- **Variation:** `--vary-pitch 2` draws a baseline shift in ±2 st per clip, and `--vary-accent 0.4` draws ±0.4 st on `--accent-range`.
- **Example:** `batch_example/` holds 3 hard-test lines × 2 voices (accent 4.0 ± 0.2, `--final-h murmur`),
  at about 10 s of render time per clip. 3 of the 6 pass:
  - hard1 in W02 fails on the short ə of ph₂tḗr (30 ms voiced);
  - hard5 measures +2.1/+2.2 st, under the 2.5 gate. Its 4 words have mostly phrase-final accents, which are now held level,
    so a one-line clip reads lower; the full clips read +2.9–3.1.
  - At an accent base of 4.0, `--qc-min-lift 2.0` is a fairer gate for single lines.

### QC gate (`qc.py`, run on every batch clip)

| check | measure | pass |
|---|---|---|
| accent lift | accented minus unaccented nuclei, st, with each line's offset and slope regressed out | ≥ 2.5 st (`--qc-min-lift`) |
| voiced | share of nuclei with any tracked F0 | ≥ 0.97 |
| **vowel level** | each nucleus vs the clip's median vowel (middle 60% of the nucleus) | ≥ −8 dB (syllabic m̩ n̩: −12 dB) |
| **vowel voicing** | tracked F0 inside each nucleus (34 ms analysis span, so edges aren't under-read) | ≥ 40 ms, or 70% of a nucleus shorter than 57 ms (`--qc-min-voiced-ms`) |
| χ | 2–8 kHz energy share, ±20 ms at each χ | every token 0.30–0.80 |
| h | same, at each h | median 0.25–0.60 |

Also reported, not gated: `accent_lift_raw_st` (the plain difference, biased on short clips where
the unaccented vowels sit early or late in the line), and `h_level_db` (each h re the median vowel),
for comparing what ElevenLabs keeps. `--vowels` prints the per-nucleus table.

The tracker is YIN with a 0.20 threshold. The vowel gates catch the v5 problem: the v5 hymn fails them on 9 nuclei (W02) and 7 (JD3).

#### QC on the ElevenLabs output
ElevenLabs runs as an API step on your machine with your key. Its output goes through the same gate:

```
python qc.py eleven/clip.wav --timing renders/clip.json --ref renders/clip.wav       # one clip
python qc.py --manifest renders/manifest.jsonl --dir eleven/ --out manifest_eleven.jsonl   # a batch
```

`--ref` aligns the file to the VTL render first (energy envelope cross-correlation, ±300 ms, 5 ms steps;
a test file delayed by 37 ms read back as 35 ms). Batch mode matches files by name (`CLIP__SPEAKER.wav`).
Any wav works: 16/24/32-bit or float, mono or stereo, any rate. Convert mp3 with ffmpeg first.

## Changes in v10

### Phrase ends without the pitch dive
In v9, VTL's F0 sagged as the lungs stepped down: téwe −3.6 st, lewbʰóm −6.2 st (JD3). ElevenLabs then turned
that sag into creak. There were three causes, each now fixed:

| v9 cause | v10 |
|---|---|
| the extra 2 st `--pe-fall` at line ends | off (`PE_FALL` 0); the timeline's line-final fall (2 st) stays |
| the accent fall of an accented word ran into its phrase-end tail | **Caesura:** from 80 ms before the last nucleus, the target holds level at the F0 VTL actually has at the nucleus onset. **Line end:** the target follows the contour, but never more than 3 st below that (`PE_LINE_FALL`). A phrase-final accent now reaches its peak 40 ms earlier, so the rise is done by the vowel onset |
| lower lung pressure lowers F0 | the target is raised by `PE_F0_COMP` st per dB of pressure drop (calibrated: 0.04 for both engines, 40 ms early for VTL's F0 lag); floor 3 st under the nucleus (`--pe-floor`) |

**Final m n l.** In v9 the hum lasted 200+ ms. Its level barely follows lung pressure, so it stayed loud and low until the folds parted.
- **Hum:** the folds now open 100 ms into the m with a 15 ms time constant (`--pe-hum 0.12`), so the hum lasts 90–110 ms.
- **Breath:** vowel-coloured breath then carries the rest of the decay (`--pe-breath -16` dB: 30 ms swell, then hold 70/30 ms, then a fade over 90/60 ms at line/caesura). This is a patch like the h patch, and `--pe-breath -99` turns it off.
- **No hum blip:** the glottis stays open 80 ms past the decay, and the lips and velum are held 50 ms past it. Without this, the folds closed again on leftover pressure and a −14 dB hum came back.

Vowel tails end exactly as in v9. Measured from the last nucleus to word end + 120 ms (JD3 / W02 / M01, hymn):

| | v9 | **v10** |
|---|---|---|
| caesura F0 span, max (limit 1.0 st) | 4.1 / 3.9 / 3.9 | **0.9 / 0.8 / 0.9** |
| line-end F0 span, max (limit 3.0 st) | 6.2 / 6.0 / 6.0 | **1.2 / 1.4 / 1.2** |
| F0 floor re the nucleus, min (limit −3.9 st = 0.8×) | −6.1 / −5.9 / −5.9 | **−1.1 / −0.9 / −1.0** |
| shortest decay, caesura / line end (limits 80 / 120 ms) | JD3 95 / 155 | **JD3 90 / 145, W02 105 / 155, M01 162 / 175** |
| final m hum (lewbʰóm, ń̥dʰgʷʰitom) | 215 ms | **95–100 ms** |

Line 5 in JD3: téwe 3.6 → 0.5 st and lewbʰóm 6.2 → 1.2 st. Elsewhere, n̥sméy 4.1 → 0.9 and dh₃dʰí 3.0 → 1.2.

Hard test, all three voices: caesura spans ≤ 0.8 st and line ends ≤ 2.6 st. The worst line end is the murmured final túH:
its tail has its own 4 st nominal fall, now capped at 3. Floors are ≥ −2.4 st; decays are ≥ 92 / 147 ms.

All values for every word and voice are in `phrase-ends-v10.md`. Words ending in s, χ or a stop are listed but stay outside the
limits; h₂yuHénih₂ (−χ) spans 1.3–1.9 st, as in v8.

**QC** now also reports `span_st` and `floor_st` for every phrase end and gates voiced endings: ≤ 1 st at caesuras, ≤ 3 st at line ends, floor ≥ −3.9 st.
The v9 hymn fails this gate on 6 words; v10 passes it in all three voices, on the hymn and the hard test. Run it on the ElevenLabs output
(`qc.py eleven.wav --timing ... --ref ... --final-h murmur`) to see whether ElevenLabs still adds the dive.

Timing JSON: identical to v9.

## Changes in v9

### `--phrase-end`
This applies to the last segment of a word followed by a pause of 0.2 s or more (line end: 0.5 s or more; caesura: less),
when that segment is voiced: a vowel, a glide, m n r l, or a murmured final H. Words ending in s, χ or a stop are left alone.
Their friction or release already carries the end.

| part | what it does |
|---|---|
| level path | Output level follows `PE_PATH`. Line end: 0 dB at end − 70 ms, −10 dB at end − 40 ms, −30 dB at end + 90 ms, −45 dB at end + 120 ms. Caesura: −60 / −35 / +55 / +75 ms. |
| lungs | A 10 ms staircase that tracks that path (pressure dB = output dB / `PE_K`, calibrated: 3 for pip, 5 for VTL 2.4, whose folds stop abruptly at low pressure), then off with a soft 30 ms release. This replaces the step. |
| glottis | Modal until the −10 dB point (minus the glottal lag), then murmur, then the h shape: the voice ends in air. |
| F0 | A further 2 st fall over the decay at line ends (`--pe-fall`); none at caesuras. |
| tract | Held: the vowel shape, and m n l closures and velum, last until the decay ends. A phrase-final r is an open [ɹ] the voice trails on, not a tap (the tap's closure cut the tail at 42 ms; `--pe-tap` keeps it). |
| timing | The decay runs up to 120 ms (line) / 75 ms (caesura) into the pause, always leaving ≥ 80 ms of silence. Word `end`s and the timing JSON are unchanged (identical to v8 on the same timeline). |

Decay from −10 to −30 dB under the last nucleus's peak, measured with your `vtl_ends.py` (qc.py reproduces it to the ms).
Hymn, accent 4.0, `--final-h murmur`:

| | JD3 v8 → **v9** | W02 v8 → **v9** | M01 **v9** |
|---|---|---|---|
| caesura (déywi, sḱih₃wós-kʷe, twé, téwe, n̥sméy, ń̥dʰgʷʰitom) | 20–25 → **95–142 ms** | 7–10 → **130–167 ms** | **147–180 ms** |
| line end (dʰúgh₂ter, mudént-kʷe, lewbʰóm, dh₃dʰí) | 22–42 → **155–212 ms** | 7–80 → **190–205 ms** | **205–249 ms** |
| end of hymn (h₁áydʰi) | 15 → **224 ms** | 7 → **207 ms** | **234 ms** |

On the hard test, voiced endings are 95–120 ms (JD3) / 132–142 ms (W02) at caesuras, and 157–212 / 192–252 ms at line ends, final túH included.
Every phrase end passes the new QC gate (≥ 120 ms at line ends, ≥ 80 ms at caesuras) in all three voices. The
lowest is ń̥dʰgʷʰitom at a caesura in JD3: 95 ms.

Endings the flag leaves alone: s/χ-final words are unchanged (95–182 ms). Stop-final words still end on their release
(bʰéwgt 35–62, h₁r̥sḱét 25–32, Hwr̥dʰyéh₁t 90–97 ms). Those aren't voice decays, and the gate skips them.

### Words that join (`pause_after` 0.0)
A 0.0 gap now inserts nothing between the words. There is no pause gesture, no lung release, and no glottal closure.
Checked on the scores of all four renders: no lung-off gesture and no glottal "stop" gesture anywhere outside a real pause.
Voicing breaks only where a sound needs it: voiceless consonants, and the closure of a voiced stop, which goes as
quiet across a word join as inside a word (déywi after léwka: −14.9 dB vs −16.0 dB for word-internal voiced stops).

Found while checking this, and fixed: since v8, a murmured final H began with a 20 ms neutral (zero) lung gesture.
The vowel's pressure ended 20 ms early, and the H's started only at its label.

### New timelines
`dawn-hymn-cadence.json` and `hardtest-cadence.json` are your new versions (v1 kept as `*-v1.json`). The middle túH now gets
82 ms of murmured tail (was 53 ms in a 177 ms word), and sḱih₃wós parses as sciɣ.wós.

QC: `qc.py` reports `phrase_ends` (decay per pause, with `voiced_end`) and gates voiced endings. Use `--no-phrase-end` to
report without gating, for example on files rendered without it.

## Changes in v8

### `--final-h murmur`
Neural converters delete a short voiceless noise before a pause. With this flag, a word-final H after a
nucleus (túH) becomes the vowel carrying on into breathy voice, with the breath patch on top:

| part | what it does | flag (default) |
|---|---|---|
| duration | target 90 ms, and only slightly elastic, so the vowel gives up the time first; word boundaries stay where the timeline puts them | `--final-h-dur 0.090` |
| oral | the vowel's tract shape is held through the H | |
| glottis | murmur (the ʱ shape), opening to the h glottis over the last half; starts one glottal lag (30/40 ms) early | `--final-h-open 0.5` |
| lungs | pressure decays to 50% across the tail (the abrupt cut before a short gap is skipped) | `--final-h-lung 0.5` |
| F0 | falls 4 st nominal across it, 40 ms early for VTL's F0 lag | `--final-h-fall 4` |
| breath | vowel-coloured patch noise, 6 dB under a plain h (with the u boost); swells in over the first 40%, fades over the last 30%; VTL's own voice is not ducked | `--final-h-noise -6` |

Measured on the hymn at `--accent-range 4.0` (re the u before it):

| túH | duration | first half | second half | voiced (QC) |
|---|---|---|---|---|
| JD3 line 4a / 4b / 5 | 93 / 53 / 93 ms | −2.2 / −2.2 / −2.6 dB | −9.7 / −4.9 / −10.2 dB, share 0.12–0.16 | 95 / 55 / 70 ms |
| W02 line 4a / 4b / 5 | 93 / 53 / 93 ms | −4.0 / −2.9 / −4.2 dB | −12.2 / −7.2 / −11.7 dB, share 0.13–0.18 | 40 / 55 / 50 ms |

JD3's first tail stays periodic to the end, with F0 falling 135 → 112 Hz (−3.2 st). W02's voice also continues to the end,
falling 249 → 209 Hz (checked with `--no-patch`). Its breath layer masks the tracker over the last ~40 ms, hence 40–50 ms "voiced".

- **The middle túH** stays at 53 ms. Its word is only 177 ms in the timeline, and taking more would leave the u at under 50 ms. Lengthen the word in the timeline for a full tail.
- **Timing JSON:** same format and word boundaries. In the three túH words the u→h boundary moves 9–15 ms earlier; nothing else changes.
- **QC:** with `--final-h murmur` (in `qc.py` and batch), word-final H are left out of the h-share gate and listed under `final_h`
  with duration, voiced ms, level and share.

## Changes in v7

### Accent A/B
`renders/dawn-hymn-{male-JD3,female-W02}-acc4.0` and `-acc4.6`. Measured lift: JD3 +3.08 / +3.54 st, W02 +3.06 / +3.54 st
(eSpeak +3.06–3.09). The timing JSON is the same for both (and still identical to v4).

### The middle túH (line 4, 44 ms)
That H is squeezed to 44 ms by the timeline. The 40 ms end fade multiplied the duck envelope too, so over
most of the interval VTL's own lagging voicing of the u was barely ducked. Over the whole interval it was
low-frequency voicing: 2–8 kHz share 0.12. Now the duck covers the whole interval, only the patch noise fades,
and the fade is capped at half the H. The lung release wasn't the cause: it drops only 20 ms before a short word gap and doesn't touch the patch.
Whole-interval share: JD3 0.12 → **0.56**, W02 0.34 → 0.50.

### Dark h level
`--h-round-boost 5`: an h coloured by u or w gets +5 dB, and by o +3.3 dB. Between two vowels the boost follows the colour crossfade.
The colour (VTL's transfer function of the vowel) is unchanged. A-weighted, the u-coloured h of the hard
test sat at about −10.5 dB re the vowels against about −6 dB for the others. With +5 dB they read −3.5 to −6.4 (suHnús −6.4, túH −5.6,
Hwr̥ −3.5) vs −4.4 to −7.6 for the rest. Hymn JD3 túH ×3 RMS: −13.7/−9.0/−13.4 → −9.7/−9.3/−9.6 dB re the median vowel.

### JD3's i after ɡʷʱ
Both of your suggestions help JD3 a little. Whole-vowel level re the median vowel, ń̥dʰgʷʰiteh₂ / ń̥dʰgʷʰitom:

| JD3 hymn | i | i |
|---|---|---|
| v6 | −7.5 | −7.5 |
| `--murmur-db -3` | −6.5 | −6.8 |
| `--breathy-release 0.025` | −7.2 | −7.2 |
| both (**v7 default for JD3**) | **−6.4** | **−6.7** |

Most of the rest isn't the murmur. In single-word tests, ń̩dʱ.ɡʷʱi, ń̩d.ɡʷi and ń̩dʱ.ɡʱi come out within 0.3 dB of each other.
Swapping the murmur for modal voice *and* removing the rounding carry-over together gains 1.8 dB. Two things are in the way:
- **The velar release:** i after ɡ is 1.7 dB weaker than after d.
- **i itself:** in this voice it is about 5 dB under o.

Releasing tongue-body closures 15 ms earlier (`--tb-release 0.045`) gains another 0.4 dB, but makes velar
releases land 15 ms before their label, so it stays off. JD3 now uses `make_speaker.py --murmur-db -3` (chink 0.061) and a 25 ms spill.
W02 is unchanged.

## Changes in v6

### Vowels after ʱ
Your diagnosis was right on all three counts:
- **The murmur was too leaky.** Its chink area (posterior glottal gap) was 0.15–0.25 cm². A held murmured
  vowel came out 16.6 dB below modal on W02 and ~10 dB on JD3. It did keep vibrating in isolation (voiced
  0.82–1.0). `make_speaker.py` now sets the chink area by bisection so a held murmured [aː] sits
  `--murmur-db -5` below modal. Results: W02 0.030 (modal 0.010), M01 0.040, JD3 0.084 (modal 0.050).
- **The spill was too long and stacked.** It is now `--breathy-release 0.040`, capped at a third of the next segment.
  It counts against the 55 ms of modal voicing a nucleus keeps, so the glottal lead before a following
  voiceless sound (70 ms before χ in bʰéh₂os) shrinks to fit.
- **The 2.4 advance stacked.** It is now onset-only (Timing compensation, above).

Vowels right after ʱ vs all other vowels, on the corrected tracker:

| render | after ʱ (n=9): level / voiced share | other vowels |
|---|---|---|
| v5 hymn JD3 | −10.1 dB / 0.65 | +0.1 dB / 0.86 |
| v5 hymn W02 | −9.4 dB / 0.62 | +0.3 dB / 0.83 |
| **v6 hymn JD3** | **−3.6 dB / 0.82** | +0.2 dB / 0.91 |
| **v6 hymn W02** | **−4.0 dB / 0.90** | +0.2 dB / 0.94 |
| v6 hymn M01 | −5.0 dB / 0.85 | 0.0 dB / 0.89 |
| v6 hard test JD3 | −2.9 dB / 0.82 | +0.3 dB / 0.88 |
| v6 hard test W02 | −4.1 dB / 0.91 | 0.0 dB / 0.90 |

The worst v5 cases are all fixed:

| vowel | v5 JD3 | v5 W02 | v6 JD3 | v6 W02 |
|---|---|---|---|---|
| i of ń̥dʰgʷʰiteh₂ | −18 dB, 55/132 ms voiced | −17 dB, 50/132 ms | −6 dB, 85/132 ms | −6 dB, 105/132 ms |
| a of bʰéh₂os | | −15 dB, 30/120 ms | pass | pass |
| o of h₃kʷbʰós | | −15 dB | pass | pass |

The remaining 3–4 dB is the murmur itself (−5 dB over at most 40 ms). For less, rebuild with
`make_speaker.py --murmur-db -3`, or use `--breathy-release 0.025`.

### Stop releases on the label
Both engines released stops ~30 ms after the score time. That put the first 30 ms of every post-stop
vowel inside its closure, against the JSON labels. The oral and velic tiers now lead by 30 ms.
The median release now lands at −6 to +8 ms of the JSON boundary (was +27 to +38).
On the hard test, W02's mean voicing inside vowels went from 0.83 to 0.92, and its worst vowel from −18.6 dB to −7.9 dB.

### QC tracker drift
`qc.py` stepped 220 samples per "5 ms" frame (4.99 ms), so its frames ran up to 60 ms late by the end of a
30 s clip. That under-read voicing late in clips, and it under-read accent lift. The same bug was in the old `pitch.py`.
Corrected numbers:
- the v5 hymn's accent lift was +3.7 (JD3) / +3.6 (W02) st, not 3.45 / 3.3;
- eSpeak's reference lift is +3.06–3.09 on the hymn and +3.08–3.20 on the hard test, not 3.4.

VTL therefore overshoots eSpeak by about 0.5 st at `--accent-range 4.6`. I left that in, since
ElevenLabs flattened v3's accent by about 0.6 st. To match eSpeak exactly before ElevenLabs, use `--accent-range 4.0`.

### h for ElevenLabs
`--h-level -14` (was −18) and `--h-fade 0.040` (was 70 ms). On the hymn, h now sits a median −13.3 dB (JD3) / −13.6 dB (W02)
below the median vowel, about 4 dB louder than v5. Spectral shares are unchanged (JD3 median 0.45, W02 0.31).
The three túH tokens on JD3: 0.64/0.12/0.39 share at −13.1/−9.4/−13.3 dB (v5: 0.54/0.02/0.31 at −18.9/−9.3/−18.1).
Whether ElevenLabs keeps them is your test; `h_level_db` in its QC output shows how much survives.

### Hard test
`renders/hardtest-*.wav` cover both voices.
- All 35 words parse. The syllabics r̥ l̥ m̥ n̥ (accented and final) are voiced nuclei.
- χ shares are 0.43–0.72 (all in range), and h medians 0.51 (JD3) / 0.44 (W02).

## Changes in v5

### Syllabic r̩ l̩ (and accented ŕ̩)
`r̩ l̩ r̥ l̥` were consonants with no vowel. Now:
- Both the syllabic stroke (U+0329) and the ring (U+0325) on r/l/m/n make them nuclei.
- They carry a schwa (ə), with the tongue tip held as [ɹ] or [l] over it.
- They get n̩ timing and take the acute accent.

In `syl.txt` (tr̩.sjóχ, hl̩χ.dʱí, ŕ̩.tkos, tŕ̥.sjoχ, ml̥.dú) every syllabic nucleus is voiced and
115–137 ms long. Accented ŕ̩ sits 4.3–4.8 st above the unaccented vowel after it, in both voices. The JSON `kind` is `Rs`/`Ls`.

### h: darker
Two routes were tried:
- **VTL-native first:** an open, non-vibrating glottis (`--h-mode vtl`). It gives almost no breath noise in either engine (2–8 kHz share ≈ 0.00–0.02), so the patch stays the default.
- **Patch, reworked:** the noise is now filtered by **VTL's own transfer function for the neighbouring vowel** instead of an LPC fit to the audio. This means:
  - it works at female F0, where LPC failed;
  - there is no treble boost on JD3 (`--h-tilt 0`) and a light one on 2.4 voices (2 dB/oct, because their transfer functions are darker);
  - there is a light F1 cut below 500 Hz and a rolloff above 7 kHz;
  - `--h-level -18` dB, `--h-duck 0.8` (v6: −14 dB);
  - word-final H fades out over 70 ms (v6: 40 ms; v7: noise only, at most half the H).

A glide next to h (h₁w-) now colours it, which fixed h₁wésu.

| h token | wiHrṓs | túH | h₂yuHénih₂ | túH | túH | h₁wésu | h₁áydʰi | median |
|---|---|---|---|---|---|---|---|---|
| v4 (JD3) | 0.71 | 0.82 | 0.80 | 0.29 | 0.84 | 0.79 | 0.48 | 0.79 |
| **v5 JD3** | 0.40 | 0.54 | 0.78 | 0.02 | 0.31 | 0.48 | 0.19 | **0.40** |
| **v5 W02** | 0.62 | 0.25 | 0.53 | 0.29 | 0.21 | 0.29 | 0.30 | **0.29** |

The share barely moves with level, because it's a spectral ratio. If the h still reads too bright,
use `--h-tilt -2`. If it reads too loud, use `--h-level -22`.

### `--lax-short`
Short e i o u use VTL's lax shapes [ɛ ɪ ɔ ʊ]. Long vowels and a stay tense. The A/B renders are
`*-lax.wav`. QC on the lax renders:
- JD3 lift 3.47, 67 of 68 voiced (one short o in bʰéh₂os goes faint);
- W02 lift 3.35, 66 of 68 voiced.

### Trill (`--trill N`, experimental; default 1 = tap)
VTL can't trill on its own. A real trill is aerodynamic: the airflow pulls the tongue tip back onto the
ridge about 25 times a second. VTL's tongue is target-driven instead, and the following was measured on the tube area:
- After the first contact, the tip only reaches VTL's 0.15 cm² constriction floor.
- Re-closure targets of any depth, including one 1 cm past the stop closure, never re-close within a 40–65 ms cycle.

`--trill N` therefore works like the χ/h patches:
- **VTL's part:** it makes the first contact itself (a real tap with real formant transitions), then holds an open [ɹ]-like tip.
- **The patch's part:** it brings each of the N contacts down to −20 dB below the following vowel, at 40 ms spacing (25 Hz). A contact VTL already made is left as it is.

The r becomes N × 40 ms long, and in timeline mode the rest of the word gives up that time. The measured
envelope through rr in a.ra and wih.róːs shows three regular 15–20 dB dips in both voices. QC still passes on the full hymn.

This is a tap-train, not a physical trill: the formants don't flutter the way a real trill's do. Judge it by ear:
- Listen to `trill-demo-*.wav`: a.ra and wih.róːs as a tap, then with `--trill 3`.
- Compare the hymn renders `*-trill3.wav`.

### Declination through ElevenLabs
(Retracted in v7: corrected measurements show ElevenLabs keeps declination, −4.9 → −5.0 st. The default 1.5,−2.5 stays.)

## How each sound is built

| PIE | gestures |
|---|---|
| p t k c | closure + **voiceless-unaspirated** glottis (short-lag voicing) |
| b d ɡ | closure + voiced-plosive glottis |
| bʱ dʱ ɡʷʱ | voiced closure → **murmur** glottis (−5 dB) ≤ 40 ms / ⅓ into the next segment, brief F0 dip |
| c | **tb-palatal-closure** |
| kʷ ɡʷʱ ɣʷ | + **ll-rounded** lips into the release |
| χ | uvular fricative + wide glottis, then the **frication patch** |
| ɣʷ | voiced uvular fricative + rounding + light noise layer |
| h | glottal opening, then the **aspiration patch** |
| s | alveolar fricative |
| m n n̩ | closure + velum; n̩ long; velum shuts early before obstruents |
| r̩ l̩ | schwa nucleus + [ɹ]/[l] tongue tip, accentable |
| r | alveolar tap [ɾ]; with `--trill N`, first contact + patched contacts |
| w j | vowel-tier [u] (+ rounding) / [i] glides |

## Pitch, timing, frication

These are unchanged from v4. The settings are:
- **Accent:** `--accent-range 4.6`. This is a nominal value: VTL's lag delivers about 0.77× of it (≈ +3.5 st measured; eSpeak +3.1).
- **Contour:** `--declination 1.5,-2.5`, `--final-fall 2`, `--accent-rise 0.12`, `--accent-fall 0.15`, `--breathy-dip 2`.
- **χ patch:** `--chi-level -9` and `--gamma-level -20`.
- **Timing:** in timeline mode the wav is exactly last `end` + `pause_after` long.

## Known limits

- **Short interconsonantal ə.** A 57–68 ms schwa between stops (ph₂tḗr, ǵénh₁tor, dh₃dʰí) gets 30–35 ms of
  voicing, and the 40 ms gate flags it.
  - That is about what an unaspirated release (VOT ~15–20 ms) plus the closing gesture leaves.
  - Retuning the glottis timing didn't move it.
  - Lengthen those schwas in the timeline, or gate with `--qc-min-voiced-ms 30` if you accept them.
- **The kʷspés / nu-kʷe /e/ from v5** is fixed in W02 and JD3. It came from the QC drift plus the stacked advance.
- **M01:** the i of ń̥dʰgʷʰiteh₂ sits at −8.2 dB, just over the gate.
- **Vowel qualities** come from each speaker's German shapes.
- **Breathiness is subtle.** VTL only partly devoices.

## Files

| file | what |
|---|---|
| `pie_vtl.py` | the compiler (single clips and `--batch`) |
| `vtlengine.py` | pip / VTL 2.4 engine interface |
| `make_speaker.py` | builds a PIE voice from any VTL speaker |
| `qc.py` | QC gate (also standalone) |
| `build_vtl24.sh`, `linux/libvtl24.so` | VTL 2.4 library for Linux/macOS |
| `JD3-PIE`, `W02-PIE`, `M01-PIE.speaker` | the three voices; `W02.speaker` and `M01.speaker` are the stock bases |
| `renders/hardtest-*-v10.wav/.json/.TextGrid` | v10: the hard-sound test in JD3, W02 and M01, at accent 4.0, `--final-h murmur` |
| `renders/dawn-hymn-*-v10.wav/.json/.TextGrid` | v10: the hymn in JD3, W02 and M01, same settings (new timeline) |
| `phrase-ends-v10.md` | F0 span, floor and decay of every phrase end, every voice |
| `hardtest-cadence.json`, `hard_lines/` | the hard-test timeline, and the same split into 9 one-line clips for batch |
| `batch_example/` | 3 hard-test lines × 2 voices: clips, renders and `manifest.jsonl` |
| `pitch.py`, `hmeasure.py` | older single-purpose checks (superseded by `qc.py`) |
