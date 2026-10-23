# Tier 3 planner brief, v4: connected texts (`prompt_id: tier3-planner-v4`)

You write PLANS for whole PIE TEXTS: stories, hymns, prayers, law codes, dialogues. Each text is a connected passage, as long as it needs to be (typically 10–30 clauses), with its own characters, topic and line of thought. **You never write PIE.** A plan is English plus lexeme ids, roles and features; a deterministic engine (`pie/realize.py`; read its docstring for the full schema) produces the PIE.

The goal is **sophisticated, accurate prose**: texts that read like the oldest Indo-European literature (the Rigveda, Homer, the Hittite laws, the Avesta), not like a list of grammar-book sentences. Accuracy comes first: every plan must say exactly what its English says.

Do not read anything under `corpus/` or `raw/`, or earlier plan files.

## Format
One JSON object per line, one line per TEXT:
`{"plan_id": "<batch>-0001", "genre": "...", "theme": ["..."], "title": "short English title", "plan": {"english": "the whole text in English", "clauses": [...]}}`

Clause fields: `order` ("SOV" default, or "VSO" verb-initial), `conj` ("kʷe" = "and", "wē" = "or", joining this clause to the previous one), `neg` (ne; with IMP or OPT it is mē: "do not!", "may it not …"), `particle` ("nu" = "now, then", clause-initial; "ge" = emphatic "indeed", enclitic; "yod" = h₁yód "if, when", opening a subordinate clause, e.g. the condition of a law), `break` (this clause starts a new sentence), `question` (its sentence ends with "?").
Slot fields: `lex_id`, `role` (SUBJ OBJ IO INS LOC ABL POSS VOC PRED GOAL MOD ADV V), `num` (SG DU PL), `head` (MOD and POSS: index of the noun slot it modifies), `enclitic` (pronoun slots), `gender` (pronoun slots used on their own), `and` (-kʷe after this word: "X Y-and" = "X and Y"), `participle` and `dep` (below).
Verb slot: `{"lex_id": ..., "role": "V", "verb": {"tense": "PRS|PST|AOR|PRF", "mood": "IND|IMP|SBJV|OPT", "voice": "ACT|MID", "person": 1|2|3, "num": "SG|PL"}}`.

**Participles (new).** A MOD slot may hold a verb with `"participle": {"voice": "ACT"}` (or "MID"): it agrees with its head noun. A slot with `"dep": <index of the participle slot>` is the participle's own argument (its object, instrument, …) and takes the case of its own role. Example, "the man carrying the load saw the horses":
`[{"lex_id": "<man>", "role": "SUBJ"}, {"lex_id": "<carry>", "role": "MOD", "head": 0, "participle": {"voice": "ACT"}}, {"lex_id": "<load>", "role": "OBJ", "dep": 1}, {"lex_id": "<horse>", "role": "OBJ", "num": "PL"}, {"lex_id": "<see>", "role": "V", ...}]`. Use participles for background action, the way Vedic and Homeric narrative does ("having seized the cattle, he drove them home" → a participle + a main verb). The perfect participle is not available.

## What makes a good text
1. **Continuity.** Keep characters and topics across clauses; refer back with pronouns (`closed:demonstrative_so` with the right `gender`, or pro-drop: the verb's person and number alone) rather than repeating nouns every clause. Open new sentences with `particle: "nu"` ("then") to move a story forward; join closely linked clauses with `conj: "kʷe"`.
2. **Variety of syntax.** Mix main clauses with relative clauses (`closed:relative_yo` + correlative `closed:demonstrative_so`), participial phrases, questions and answers, commands (IMP), wishes (OPT: "may X …"), exhortations (SBJV 1st plural: "let us …"), negation and prohibition (neg + IMP = "do not!"). About 20% of clauses verb-initial (VSO) for emphasis or in narrative sequence.
3. **Genre voice.** Hymn: invocation (VOC), praise of the god's deeds (AOR, PST), and a closing request (IMP or OPT). Prayer/charm: imperatives and optatives, repetition. Law: "whoever does X, let him pay Y" (relative clause + SBJV/OPT/IMP), lists of cases. Myth/epic: narrative past (AOR for single events, PST for background), participles, speeches. Dialogue: turns with questions, answers that repeat the question's verb, vocatives.
4. **Inherited phrasing.** Your slice has a `formulas` list: inherited phrases reconstructed from matching daughter-language wording (each has its lexemes and a note on how to build it, e.g. ḱléwos + MOD ń̥dʰgʷʰitos = "imperishable fame"). Use at least one formula in every text where it fits naturally (hymns, epic, praise: almost always). Don't force them into laws or dialogues where they would be odd.
5. **Meter (hymns, prayers, charms).** Old Indo-European verse is counted in syllables: lines of 8 (Vedic gāyatrī) or 11 (triṣṭubh). Aim each sentence of a hymn, prayer or charm at 8 or 11 syllables. After the initial run, `corpus/tier3/<batch>-initial.jsonl` is deleted, but `data/generation/batches/<batch>-initial.json` reports `meter_fit` (the share of lines within ±1 of 8 or 11): improve it in the repair pass by adding or dropping a word, never by changing the meaning.

## Rules (all still apply)
6. Use only `lex_id`s from your slice's `lexemes` or `closed` ids. Never invent ids.
7. Exactly one V slot per clause; 2–7 slots per clause.
8. Verb features must be in that verb's `features` list. Proverbs and general truths ("a guest is holy", "fire burns") use the present; a verb that has only aorist forms takes the gnomic aorist (AOR, IND), never a subjunctive. `deponent: true` verbs take voice "MID" only. Aspect: PRS/PST = ongoing or habitual, AOR = a completed single event, PRF = a present state ("knows", "is afraid", "has seen"). For a single past event use AOR when the slice has an aorist of the root, otherwise PST.
9. **Pro-drop:** no 1st/2nd-person pronoun subject just to mark person; put `person`/`num` on the verb. Pronoun subjects only for contrast or emphasis.
10. Pronoun slots used on their own must give a `gender` matching their referent. "What" = `closed:interrogative_kwi`, gender "n".
11. Prohibitions are `neg: true` + mood IMP, with verbs that have PRS or AOR forms (never PRF).
12. **Voice:** a transitive verb whose English subject undergoes the action ("the wheel broke", "dress yourself") takes "MID". Verbs tagged `valency: "tr"` need an OBJ in the active.
13. **Questions and answers:** an answer repeats the question's verb lexeme unless the English changes the verb.
14. **The English says what the plan says**, no more and no less; every content word needs a slot. Write the English as good, plain prose (it is the translation readers will see).
15. **Word choice:** prefer the lexeme with the higher `attested_in`. `gloss_approximate` lexemes only when the meaning fits plainly and no plainly glossed synonym is in the slice. `gloss_source: "nil"` glosses come from a dictionary of nominal formations and are reliable.
16. **Diversity (gated):** any one lexeme at most max(6, 0.5% of the batch's tokens) times; `theme_core` lexemes (the god or thing the batch is about) up to max(15, 1.5% of tokens). The copula is exempt.

## Check and repair (exactly once)
1. Write all plans to `data/generation/plans/<batch>.jsonl` and copy it to `<batch>.initial.jsonl`.
2. Run `uv run python -I scripts/realize_plans.py data/generation/plans/<batch>.initial.jsonl --batch <batch>-initial --model <model> --prompt-id tier3-planner-v4` and note the numbers, including the gate result, `meter_fit`, `formula_uses` and `words_per_record`.
3. Delete `corpus/tier3/<batch>-initial.jsonl` (keep the plan files and `data/generation/batches/<batch>-initial.json`).
4. Fix the rejected plans, any lexeme over its cap, and hymn lines far from 8/11 syllables, in `<batch>.jsonl` (one repair pass). Run the same command with `--batch <batch>`.
5. Modify nothing else. Never run `realize_plans.py` on another batch's plans.

Final message ≤150 words: the initial and final reject counts, gate results, words per text, meter_fit, formula_uses, distinct lexemes and roots, and anything you could not express.
