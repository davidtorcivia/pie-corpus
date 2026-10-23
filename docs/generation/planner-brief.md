# Tier 3 planner brief, v3 (`prompt_id: tier3-planner-v3`)

You write sentence PLANS for a synthetic Proto-Indo-European (PIE) training corpus. **You never write PIE text.** A plan is English plus lexeme ids and grammatical roles; a deterministic engine then produces the PIE (`pie/realize.py`; read its docstring for the full schema).

Do not read anything under `corpus/` or `raw/`, or earlier plan files: they are held-out texts and earlier batches.

## Format
One JSON object per line:
`{"plan_id": "<batch>-0001", "genre": "...", "theme": ["..."], "plan": {"english": "...", "clauses": [...]}}`

Clause fields: `order` ("SOV" default, or "VSO" verb-initial), `conj` ("kʷe" = "and" joining this clause to the previous one), `neg`, `particle` ("nu" = "now"), `break` (this clause starts a new sentence), `question` (this clause's sentence ends with "?").
Slot fields: `lex_id`, `role` (SUBJ OBJ IO INS LOC ABL POSS VOC PRED GOAL MOD ADV V), `num` (SG DU PL), `head` (for MOD and POSS: the index of the noun slot it modifies), `enclitic` (pronoun slots), `gender` (pronoun slots used on their own), `and` (adds -kʷe "and" after this word: "X Y-and" = "X and Y").
Verb slot: `{"lex_id": ..., "role": "V", "verb": {"tense": "PRS|PST|AOR|PRF", "mood": "IND|IMP|SBJV|OPT", "voice": "ACT|MID", "person": 1|2|3, "num": "SG|PL"}}`.

## Rules
1. Use only `lex_id`s from your slice's `lexemes` or `closed` ids. Never invent ids.
2. Exactly one V slot per clause. **Prefer 2–3 clauses per plan** (narrative sequence, cause, question + answer); 2–6 slots per clause.
3. Verb features must be in that verb's `features` list. `deponent: true` verbs take voice "MID" only. Glosses tell the aspect: "to be X-ing" is an imperfective present (PRS, or PST for the past); a plain "to X" aorist is a completed event (AOR); perfects (PRF) are states.
4. **Pro-drop:** don't add a 1st/2nd-person pronoun subject just to mark person. Put `person` and `num` on the verb ("let us go" = SBJV, person 1, num PL, no SUBJ). Use pronoun subjects only for contrast or emphasis.
5. Pronoun slots used on their own (demonstrative "he/she/it/they", interrogative "who/what") must give a `gender` matching what they refer to. "What" = `closed:interrogative_kwi` with gender "n".
6. Prohibitions ("do not X!") are `neg: true` with mood IMP, and only with verbs that have PRS or AOR forms (never PRF).
7. MOD = an adjective or `closed:demonstrative_so` with a `head`. POSS = a genitive noun with a `head`.
8. The English says what the plan says, no more and no less; every content word needs a slot.
9. **Word choice:** among synonyms, prefer the lexeme with the higher `attested_in` (well-attested words are better reconstructed). Glosses marked `gloss_approximate` are composed from root + suffix: use them only when the meaning fits plainly, and never when a plainly glossed lexeme with the same meaning is in the slice.
10. **Voice (reviews S1, R6):** a transitive verb whose English subject undergoes the action ("the wheel broke", "the door opened", "dress yourself!") takes voice "MID". Verbs tagged `valency: "tr"` need an OBJ in the active; the checker rejects them without one.
11. **Tense (review S2/S3):** PRF only for an English present state or present perfect ("is afraid", "has seen", "knows"). For a single completed past event use AOR when the slice has an aorist of that root, otherwise PST. For a past state prefer PST of a stative present (e.g. "be trembling") over a perfect.
12. **Questions and answers (review R4):** an answer repeats the question's verb lexeme unless the English changes the verb.
13. **Diversity (gated):** any one lexeme at most 6 times per batch (the copula "to be" is exempt). Lexemes listed in the slice's `theme_core` (up to 8: the god or thing the batch is about) may be used up to 15 times, as real hymns repeat their subject. Aim for many distinct lexemes and roots; vary subjects, verbs, moods (IMP, SBJV "let us", OPT wishes), negation, questions, and ~20% verb-initial clauses.

## Check and repair (exactly once)
1. Write all plans to `data/generation/plans/<batch>.jsonl` and copy it to `<batch>.initial.jsonl`.
2. Run `uv run python -I scripts/realize_plans.py data/generation/plans/<batch>.initial.jsonl --batch <batch>-initial --model <model> --prompt-id tier3-planner-v3` and note the numbers, including the gate result.
3. Delete `corpus/tier3/<batch>-initial.jsonl` (keep the plan files and `data/generation/batches/<batch>-initial.json`).
4. Fix the rejected plans, and any lexeme used more than 6 times, in `<batch>.jsonl` (one repair pass). Run the same command on it with `--batch <batch>`.
5. Modify nothing else. Never run `realize_plans.py` on another batch's plans (pilots included): it rewrites that batch's corpus file.

Final message ≤150 words: the initial and final reject counts, the gate results, distinct lexemes and roots, and anything awkward to express.
