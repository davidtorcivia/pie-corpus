# Tier 2 brief: back-projection from parallel daughter passages (`provenance: back_projection`)

You reconstruct PIE phrases that are **actually attested** as parallel wording in two or more branches: the inherited phraseology Watkins and West study (Indra slays the serpent / Thor slays the world-serpent; κλέος ἄφθιτον / śrávas ákṣitam; Father Sky; Dawn the daughter of Sky; healing charms "bone to bone, blood to blood"). **You never write PIE.** You write a plan (the Tier 3 plan schema in pie/realize.py's docstring and docs/generation/planner-brief-v4.md), using as lexemes the PIE etyma of the daughter words, and the engine produces the PIE.

## What a projection line is
One record per parallel: the attested passages (2+ branches), and one PIE line (or two or three clauses) that is their common ancestor as closely as the evidence allows.
- **Secure elements:** lexemes whose cognates actually stand in the cited passages in at least two branches (e.g. *gʷʰen-* in RV áhann and in Avestan jaγna; *h₁ógʷʰis* in áhim and in Avestan aži-). List their lex_ids in `secure`.
- **Interpolated elements:** what the line needs grammatically but no two branches share (a particle, a pronoun, a tense choice). Keep them few, and explain them in `notes`.
- Prefer the morphology the branches agree on (tense/aspect, case, number). If they disagree, choose the reconstruction the handbooks support and say so in `notes`.

## Evidence sources (local; read with `python3 -I`, never execute anything there)
- Rigveda: raw/daughters/rigveda-vedaweb/ (TEI with lemma annotation; cite as "RV 1.32.1").
- Homer: raw/daughters/homer-perseus-agdt/ (treebank; cite "Il. 9.413").
- Avesta: raw/daughters/avesta-cab/ (cite "Y. 9.8", "Yt. 19.40").
- Poetic Edda: raw/daughters/edda-fj1926/; Old English: raw/daughters/oe-beowulf-gutenberg/; Old Irish: raw/daughters/oldirish-ud/; Hittite: raw/daughters/hittite-tlhdig/; early Latin: raw/daughters/latin-lasla/.
- Archaic and classical Greek beyond Homer: raw/daughters/glaux/ (GLAUx treebank: Hesiod, the Homeric Hymns, Pindar, Bacchylides, the tragedians, the lyric and epic fragments). `src/glaux-main/metadata.txt` maps each text id (`0020-001` = Hesiod, Theogony) to its TLG number, author, title, genre and licence; the text is `src/glaux-main/xml/<id>.xml`, one `<word form= lemma= line=>` per token. The Greek is NFD: normalize (`unicodedata.normalize("NFC", …)`) before matching. Cite "Hes. Th. 117", "Hymn. Hom. 33.1", "Pind. Pyth. 3.112".
- Atharvaveda: raw/daughters/dcs-hellwig/ (Digital Corpus of Sanskrit, CoNLL-U with lemmas; Śaunaka and Paippalāda). Cite "AVŚ 4.12.1", "AVP 4.15.1".
- Umbrian: raw/daughters/oscan-umbrian-buck1904/ (Buck 1904, OCR; cite "Tab. Ig. VIa 30").
- **Cite only loci you confirmed in a local corpus when one exists for that text.** A locus taken from West or Watkins for a text that is in a local corpus (all of the above) must be checked there, words and construal, before it goes into `cognate_refs`; "not in local corpora" is only true for texts none of these holds (Livy, Vergil, the Irish sagas, the dainos …).
- The scholarship: West 2007 (raw/books/text/west/) and Watkins 1995 (raw/books/text/watkins/) name the parallels and loci; use them to find passages, then confirm the words in the corpora where a corpus exists. data/formulas/formulas.jsonl lists the known formulas with attestations.
- **Never quote daughter text at length.** In `cognate_refs` give the locus, the parallel words only, and their lemmas.

## Format
One JSON object per line in `data/tier2/plans/<cluster>.jsonl`:
`{"proj_id": "<cluster>-001", "cluster": "<cluster>", "theme": ["<West cluster>"], "plan": {"english": "...", "clauses": [...]}, "cognate_refs": [{"lang": "Vedic", "locus": "RV 1.32.1", "words": ["áhann", "áhim"], "lemmas": ["han-", "áhi-"]}, {"lang": "Avestan", "locus": "Y. 9.8", "words": ["jaγna", "ažīm"], "lemmas": ["jan-", "aži-"]}], "secure": ["pie-lex-gwhenti", "pie-lex-h1ogwhis"], "notes": "..."}`
Language names (each maps to a branch in scripts/build_tier2.py; Vedic and Avestan are one branch, Indo-Iranian): Vedic, Avestan, Old Persian, Greek, Mycenaean Greek, Latin, Oscan, Umbrian, Old Irish, Middle Irish, Welsh, Gaulish, Old Norse, Old English, Gothic, Old High German, Old Saxon, Hittite, Luwian, Lithuanian, Latvian, Old Prussian, Old Church Slavonic, Armenian, Tocharian A/B, Albanian, Phrygian.

## Rules
- Lexemes: any usable lexeme in data/lexicon/lexicon.jsonl (check `uv run python -c "from pie.realize import Lexicon; lx=Lexicon.load(); print(lx.specs['<id>']['usable'])"`), never blocked ones (data/generation/blocklist.jsonl). Find the PIE etymon of a daughter word through the lexicon's `reflexes`.
- All of planner-brief-v4's grammatical rules apply (pro-drop marking, VOC address, voice, tense, gender of adjectives used as names, duals).
- Each line must cite at least two branches (the builder rejects otherwise). Three or more branches is better.
- Honesty over coverage: if a parallel is only semantic (no shared cognate words), it is not a back-projection; skip it.

## Lessons from the adversarial review (docs/audits/tier2-review.md)
- **`secure` is checked by the builder**, not taken on trust (pie/tier2_secure.py): a lexeme counts only if a cited word or lemma in the parallel refs of at least two branches reaches it through the Phase 8a mapping tables (data/research/formulas/mapping/, the kaikki links) or equals one of its recorded reflexes as a whole word (`secure_checks` in the output: `exact` vs `root`, with the evidence path per branch). A derivative or a sibling formation of the same root is root level. A compound counts only if one cited word carries both members. Cite the daughter word as attested *and* its dictionary lemma, so the match can be found.
- **Mark each ref's role**: `"role": "parallel"` (the passage that carries the shared wording; default) or `"role": "support"` (a passage cited for meaning or usage only). Only parallel refs count as branches.
- **The head of the formula must be secure** (the noun of a noun phrase, the verb of a clause): a line whose only secure words are its periphery is not a back-projection.
- **One line per parallel.** The builder drops a second line with the same set of parallel loci; vary the passages, not the phrasing.
- **Follow the daughters' morphology exactly**: Ved. dhehi is the reduplicated *present* imperative (dʰedʰh₁dʰí), not the aorist; if both branches have the middle (Ved. yukṣvá, Gk ζεύγνυσθε), so does the line.
- Shared root with different formations in the two branches is root-level evidence, not exact: say so in `notes`.
- Lines the review rejected are listed in data/tier2/review_verdicts.json and never reach the corpus.

## Check
Run `uv run python -I scripts/build_tier2.py data/tier2/plans/<cluster>.jsonl`; fix rejects; rerun until 0 rejects. Report lines, rejects, mean secure share, mean branches.
