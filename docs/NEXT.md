# Next steps (handoff list, started 2026-10-29)

## Engine fix list (from the 2026-10-30 reviews; none broke an approved batch)
- **Silent cell substitution** (t3b-002, t3b-004, t038, t039): a requested cell the engine doesn't build (a dual
  oblique, a middle dual) silently becomes another (plural), with no rejection or warning. check_plan should reject,
  or realize should warn, so the planner chooses.
- gʷṓws oblique plural built on gʷéw-, not gʷów- (t035).
- Prohibitive mē is tagged closed:particle:ne (pie/realize.py, t034 review 2); pérkus "oak" is masculine, usually f.; the
  lexeme cap scales with tokens, so shortening one text can push others over (t034).
- Middle injunctive 2sg ends in -th₂e, not *-so (t035, t036: the -th₂e/-th₂er middle endings need documenting).
- péh₂tōr 'guardian' obliques identical to ph₂tḗr 'father' (t037).
- gʷʰen- 'slay' has no aorist (t037).
- Anaphoric m. NOM.SG h₁éy vs *h₁ís (t037; with the engine agent of 2026-10-30).
- h₂ew 'again' has no accent and is glossed only 'away from' (t042, t084, t034: accent-lint noise).
- A female cow triggers a false gender warning (t042).
- Brief: "How do you say …?" makes the model echo the user (t036); aorist-only words beat present synonyms in
  proverbs (t043).
- **Vocabulary round 3 (war and exchange, t040):** booty, raid, boast, threaten, weapon, sword, shield, battle,
  victory, brave, ransom, pay, weep, calf, herald; summer (sm̥h₂erós has no accent); bird/fly/iron (t3b-007).
- **Vocabulary round 4 (conversation gaps, t044 planner):** every/all (*sólh₂wos), until, before (*pr̥h₂í, *pr̥Hwós),
  because, neighbour, bread, tomorrow; a thanks/please formula beyond praise of the giver; from t050/t056/t059:
  but, only, ago and spans of time ("for three days"), yes/no, morning, count, open, cloak, summer, calf, kick,
  spill; verbs agree, refuse, persuade, obey, answer, avenge, pay; a feminine "cow" (gʷṓws is masculine only).
- The adposition pie-lex-me ('among, with') has the surface form of the enclitic 1sg ACC, so realize moves it to
  second position (ENCLITIC_PRONOUNS matches forms); no released record has it (t056 used médʰi). Match by id.
- An apposition's own `num` is silently replaced by its head's (t056).
- Numeral 'two' has no feminine oblique dual forms (t045: 4 rejects).
- gʷṓws: oblique plurals must be o-grade gʷów- (Ved. góbhis, gávām; Gk βουσί); the drills now teach gʷéwbʰos.

## Morning first
1. **Rate the TTS finals** on the finals rating page, https://claude.ai/artifact/23p85eZLQR3nawtMgUxZAf. Candidates: Kokoro + profile (bf_isabella, af_nicole, em_santa) and eSpeak → Seed-VC F0 (em_santa, em_alex, bf_isabella, af_nicole), with eSpeak as reference. Then set the winner as the `pie.speak` default and redeploy erebus `pie-tts` if Kokoro wins.
   - Seed-VC is GPL-3.0 and offline-only (~35 s/clip on CPU); a Seed-VC winner means pre-rendered demo audio, or a GPU host.
   - The earlier bake-off page (19 voices) and the Voice Lab stay up for reference.
2. **Owner decisions:**
   - THEONYM_DERIVATIVES (Helios/Sūrya) — kept for now.
   - Still-held everyday roots (remind, rise, protect, …).
   - Two t027 plural-perfect meaning changes (consolidation audit).

## Model training tests (owner, 2026-10-29)

Every arm uses the same export and the same tests:
- the chat model trains on `export/chat/train_mix.jsonl`, the translator on `export/translator/`;
- the conversational test is the reserved t010 dialogues, with English input;
- the translator test is the `translate_app` eval items;
- the benchmark is paradigm, cognate→PIE and chrF.

| Arm | Model | Where | Notes |
|---|---|---|---|
| A | Qwen ~4B instruct, LoRA | local (M3 Ultra) | fast iteration; also a base-model control |
| B | Nemotron 3.5 122B MoE instruct, LoRA | Tinker | the demo model; no base checkpoint exists |
| C | **talkie-13B** (pre-1931 English, Apache 2.0) | local LoRA | "ignorant of the modern world". Try the base model and the chat variant; the chat variant's post-training used synthetic Claude chats, so it is less purely vintage |
| D | **TypewriterLM 7.2B** (pre-1913 English, arXiv 2606.02991) | local LoRA | check the license and the released chat/instruction data |

Before training C and D:
- Measure tokens per word on our PIE (Unicode and ASCII), as was done for Qwen3-4B (5.1 / 4.6). An old-text tokenizer may split PIE characters into bytes.
- Confirm that the weights and license allow fine-tuning and a public demo.
- Check whether Tinker supports C or D as a base model; otherwise train them locally.

Judge "a living language you can converse with", not a talking dictionary: use the conversational eval plus a human read of multi-turn exchanges.

## Corpus and tooling (queued 2026-10-29)
- **More conversational corpus.** The owner wants a living language you can converse with, so plan more multi-turn dialogue batches in Tier 3 (wave 2, t034–t083, is still parked) and Tier 3b.
- **Slice gaps for Tier 3b:** bread, milk, hungry, angry, story, tomorrow, and the verbs pr̥sḱéti "ask/please" and wéḱti "wish". The brief's please/sorry idioms need them.
- **`realize_plans.py` should reject held-out root families** (`eval_root`) in plans. Today a held-out root can enter training unnoticed (t3b-001 0019 used h₁éwHt).
- **Glosses for the translator app** use internal labels (`personal/2-ACC.SG.ENCL`, `demonstrative_so-ACC.SG`). Map them to readable English glosses.
- **Compound engine:** a determinative prefix compound such as h₂énti- "counter-" for the "answer" coinage (h₂entiwékʷos).
- **t3b-001** predates the v2 rules (per-sentence English, the coined-sentence gate). Re-plan it under v2 if it is ever re-realized.
- **From the t3b-002 review:**
  - closed:demonstrative_so has no DAT/INS/GEN dual (the dual falls back to the plural).
  - The `words_per_sentence` metric equals `words_per_record`, which is a bug.
  - Two 'give' aorists (déh₃t, déh₃ut) both enter the chat data; pick one.
  - The 6-use cap blocks natural fixes for everyday words in Tier 3b.
  - Brief-3b §3 "Welcome, guest" idiom puts the model in a house, contradicting §5's "no home". Restrict it to the user's lines.

## Hold-out (redrawn 2026-10-29: 5f2239c, 1a2cb6a)
- 821 families are protected now (Swadesh-207, Leipzig–Jakarta, a conversational core); 81 core families that were held before are trainable (help, drink, hear, sit, water, day, think, …).
- **Owner's call:** some families are still held but arguably everyday: mneh₂- 'remind', h₃neh₂- 'enjoy', h₁rey- 'rise', prep- 'appear', ḱenk- 'hang', treH- 'protect', h₂ens- 'give birth', melkʷ- 'fall silent'. Protecting them needs another redraw (cheap until scores exist).
- Offer `pie-lex-h1ewHt` 'help' in Tier 3b slices (`TIER3B_INHERITED`) now that it is trainable.
- wait, thank, answer, today and tomorrow have no trusted gloss in the lexicon, so the concept list can't protect them. They need glosses or coinages.

## From corpus-quality batch 2 (done: 9297a88 … 068ee42)
- **Decided for the owner, reversible:** `THEONYM_DERIVATIVES` keeps Ἥλιος and Sūrya, both sun gods, as content with the sun root, now that ἥλιος counts as a derivative. Delete it in `pie/name_mapping.py` to undo.
- **Tier 2 lines to re-review after the cq2 mapping changes:** dawn-sun-016 and dawn-sun-009 (exact → root), epic-diction-013 (exact → root), death-otherworld-012 and -004 (root → exact). Rebuild `corpus/tier2` first.
- **Open:** Welsh nant is still keyed to *nem- through an unverified route. Clitics stay non-content; a clitic-aware scan would need a function-word layer in the index.
- **Old index copies:** `corpora.pre-cq2.sqlite` and the corrupt `corpora.cq2-decd105.sqlite`, plus the old caches under data/research/8c/search-index/. Delete them to free space.

## State at end of session (2026-10-29)
- **Corpus:** 35 Tier 3 batches approved after consolidation (t022 and t025 excluded: lexeme caps), Tier 3b t3b-001 and t3b-002 approved; final export b8498a5.
- **Engine:** usable lexemes 4,917; meter exact gate ≥ 0.90 in verse genres; hold-out protects 835 core families.
- **Parked by the owner (not started):** Tier 3 wave 2 (t034–t083), more Tier 3b batches, the translation-app shell, further discovery rounds (D1/D2 failed their controls: docs/research/discovery-r2-results.md).
- **Disk clean-up when convenient:** old search indexes and caches under data/research/8c/search-index/; tts/vc venvs and caches; tts/cache/hf.
