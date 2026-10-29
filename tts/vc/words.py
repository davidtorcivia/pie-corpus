"""Hard-word set (ids as in tts/bakeoff/manifest.json where the word is shared) for the eSpeak + voice-conversion viability test (docs/research/tts-voice-conversion.md)."""

# (id, PIE text, target sound(s) under test)
WORDS = [
    ("h2ewsos", "h₂éwsos", "χ"),
    ("h2owis", "h₂ówis", "χ"),
    ("h2egjeti", "h₂éǵeti", "χ + palatal ǵ"),
    ("gjenh1tor", "ǵénh₁tor", "palatal ǵ"),
    ("kjlewos", "ḱléwos", "palatal ḱ"),
    ("bhreh2ter", "bʰréh₂tēr", "breathy bʰ"),
    ("dhugh2ter", "dʰugh₂tḗr", "breathy dʰ"),
    ("gwhenti", "gʷʰénti", "breathy labiovelar gʷʰ"),
    ("kwetwores", "kʷetwóres", "labiovelar kʷ"),
    ("h3esth1", "h₃ésth₁", "h₃ (ʕʷ) + final h₁"),
    ("wlkwos", "wĺ̥kʷos", "syllabic l̥ + kʷ"),
    ("kmtom", "ḱm̥tóm", "ḱ + syllabic m̥"),
    ("ph2ter", "ph₂tḗr", "h₂ between stops"),
    ("dyews", "dyḗws", "long ē + accent"),
    ("h1esti", "h₁ésti", "h₁ (ʔ)"),
    ("ghime", "ǵʰimḗ", "breathy ǵʰ + final accent (F0 peak check, ɟʱi.méː)"),
    # two sentences of corpus record t3-t026-00015 ("Dawn, Daughter of Sky"), corpus/tier3/t026.jsonl
    ("hymn-1", "h₂éwsos léwka déywi diwés dʰúgh₂ter.", "hymn line (t3-t026-00015 s1)"),
    ("hymn-2", "n̥sméy léwks sḱih₃wós-kʷe twéd bʰéwgt.", "hymn line (t3-t026-00015 s2)"),
]

TIMBRES = ["hm_omega", "ef_dora", "em_alex"]

# Fair-comparison round (owner's request): the bake-off's top-3 Kokoro voices, each with its recommended profile
# (docs/research/tts-bakeoff-objective.md "Top 3 voices and recommended profiles"), on 4 hard words + the 2 lines.
TIMBRES2 = ["bf_isabella", "af_nicole", "em_santa"]
VOICE_PROFILE = {"bf_isabella": ("h2-velar", "fronted"), "af_nicole": ("h2-velar", "fronted"),
                 "em_santa": ("h2-voiced-uvular", "plain")}
SUBSET = ["h2ewsos", "h2egjeti", "kjlewos", "bhreh2ter", "hymn-1", "hymn-2"]


def selection(default_voices):
    """(voices, item ids) for a converter run: VC_VOICES / VC_ITEMS (comma lists) override the defaults."""
    import os
    v = os.environ.get("VC_VOICES")
    i = os.environ.get("VC_ITEMS")
    return (v.split(",") if v else list(default_voices)), (set(i.split(",")) if i else None)
