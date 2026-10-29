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
