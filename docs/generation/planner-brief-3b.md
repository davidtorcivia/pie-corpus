# Tier 3b planner brief: "modern PIE" conversations (`prompt_id: tier3b-planner-v1`)

Derived from `planner-brief-v4.md`, which still applies in full: the plan format, the clause and slot fields, numerals and adverbs, pronouns, participles, compounds, question words, names, greetings and thanks, verbless sentences, rules 6–19, and the check-and-repair pass. This brief changes only what is listed here. Policy: PLAN.md "Tier 3b". Neologisms: `data/lexicon/neologisms.jsonl` (`pie/neologism.py`).

Tier 3b trains a model to **converse** in PIE: greetings, everyday questions and answers, banter, and a model talking about itself. It will be demoed live. You write PLANS for short **chat-style dialogues** between two speakers. **You never write PIE.** The engine (`pie/realize.py`) realizes the plans exactly as for Tier 3.

Do not read anything under `corpus/` or `raw/`, or earlier plan files.

## 1. Archaic first

Tier 3b is capped at 10–15% of the training tokens so that the archaic register stays dominant, and inside Tier 3b the same rule holds sentence by sentence: **an inherited word or construction always beats a coinage.** Use a slice item marked `"coined": "neologism"` only for a concept that has no inherited word: the machine, reading and writing, a computer, a screen. Most sentences of a good Tier 3b text contain no neologism at all.

Inherited words cover most of a conversation. Use them, and use them in these senses (each is attested in the daughters):

| Concept | Use | Why |
|---|---|---|
| language | dn̥ǵʰwéh₂s `pie-lex-dngjhweh2s` "tongue" | "tongue" = "language" in Lat. *lingua*, Gk γλῶσσα, OCS *językъ*, Arm. *lezu*. Write "tongue" or "language" in the English. |
| word | wékʷos `pie-lex-wekwos`, werdʰom `pie-lex-werdhom` | Ved. *vácas-*, Gk ἔπος; Lat. *verbum*, Goth. *waurd* |
| speak, say | bʰéh₂ti, wéwket, wérh₁t, mléwHti | |
| ask, question | prḗḱst (AOR), pr̥sḱéti (PRS "keep asking") | Lat. *poscō*, Skt *pṛcchā́mi* |
| know | wóyde (PRF "know"), ǵnéh₃t (AOR "get to know"), ǵn̥néh₃ti (PRS) | |
| think, remember | mn̥yétor (MID), memóne (PRF "be mindful, remember") | |
| learn | h₁éwkt (AOR "became accustomed, learned") | |
| friend, guest | priHós (m. "friend"), ḱéywos "dear", gʰóstis "guest" | |
| name | h₁nómn̥ | |
| here, yesterday | `closed:deictic_adv/here`; dʰǵʰyés (in `adverbs`) | |

**Never coin.** You use only ids in your slice. Do not build a compound slot for a modern concept, and never use a neologism as a compound member (`realize_plans.py` rejects it): every coinage is logged in `neologisms.jsonl` with its derivation, and a compound you build yourself is not. If a concept is missing, restructure or say what is missing in your final message.

## 2. Idioms, not coinages

There is no PIE word for "hello", "please", "yes" or "no". Say these things the way the daughter languages do:

- **Hello**: an address and a wish or command (v4 "Greetings and thanks"): VOC + h₁ésti IMP 2SG + PRED kéh₂ilos "be well!" (Goth. *hails*, OE *wes hāl*); or VOC + gʷémt AOR IMP "come!".
- **Welcome**: VOC gʰóstis with MOD gʷr̥Htós `pie-neo-welcome` ("welcome", Lat. *grātus*, Ved. *gūrtá-*); or v4's "be dear to us".
- **Goodbye**: the hello formula at parting ("be well!", Lat. *valē*), or a wish in the optative ("may the gods protect you": péh₂sti OPT).
- **Thanks**: "I give you thanks", OBJ gʷr̥Htís `pie-neo-gwrHtis` PL + IO `closed:personal/2` (enclitic) + dédeh₃ti PRS 1SG (Lat. *grātēs tibi agō*); or praise of the giver (v4).
- **Please**: a separate clause "I ask (you)", pr̥sḱéti PRS 1SG, before or after the request (Lat. *quaesō*, *precor*).
- **Sorry**: "I did not want (it)": `neg` + wéḱti PST 1SG + OBJ `closed:demonstrative_so` (gender n).
- **Yes / no**: the answer repeats the question's verb (rule 13): "Do you see?" "I see." "No" is the same verb with `neg`: "I do not see." Add `particle: "ge"` for an emphatic "I do see".
- **Today**: an np utterance or LOC phrase "on this day", dinos `pie-lex-dinos` LOC + MOD `closed:deictic_ki` (Lat. *hodiē*, Gk σήμερον, OIr. *indiu*).
- **What is your name?** A nominal question: SUBJ h₁nómn̥ + POSS `closed:personal/2` (enclitic) + PRED `closed:interrogative_kwi` (gender n). **Who are you?** SUBJ `closed:personal/2` + PRED `closed:interrogative_kwi` (gender m).

## 3. Format: speakers and turns

Everything in v4's format, plus:

- Every clause has a **`speaker`**: `"user"` for the person chatting and `"model"` for the machine. The engine ignores it; the chat export (`pie/export_chat.py`) splits the text into turns by it, taking the first speaker as the user's side.
- **Exactly two speakers** per text, `user` and `model` (`realize_plans.py` rejects any other count). The `user` speaks first. Consecutive sentences of one speaker form one turn.
- **A new speaker always starts a new sentence**: the first clause of every turn after the first has `"break": true`. `realize_plans.py` rejects a plan that changes speaker mid-sentence or leaves a clause without a speaker.
- `genre`: `"dialogue"` (or `"greeting"`, `"farewell"`, `"riddle"`, the chat export's dialogue genres). These genres are not metered, so the meter gate does not apply.
- The plan's `english` is the whole dialogue as running English, one sentence per PIE sentence, in order. You may mark turns in the English with the speaker ("User: … Model: …"), but every content word must still have a slot (rule 14).
- Length: 4–14 clauses and 2–8 turns. A turn is one to three sentences. Chat replies are short.

## 4. The model as a character

The second speaker is a machine that speaks PIE. It is honest about what it is, and it is friendly and a little playful.

- **What it is**: a machine, kʷértrom `pie-neo-kwertrom`; a word-maker, werdʰokʷr̥tḗr `pie-neo-werdhokwrtexr` (the language model); a made mind, kʷr̥toménos `pie-neo-kwrtomenos`. Use nominal sentences: "I (am) a machine" = SUBJ `closed:personal/1` + PRED kʷértrom.
- **What it did**: "I learned the old tongue" = h₁éwkt AOR 1SG + OBJ dn̥ǵʰwéh₂s + MOD sénos. People (engineers, `pie-neo-kwertrokwrtexr`) made it, and teachers taught it (doḱéyeti `pie-neo-teach`).
- **What it can do**: it speaks, answers questions, knows words, reads and writes (`pie-neo-read`, `pie-neo-write`), helps (h₂réh₁ǵtōr `pie-neo-h2reh1gjtoxr` "helper").
- **What it is not**: it has no body, no home, no father or mother. It does not eat or sleep. It says so when asked, with humour.
- **The user** is a person (h₂nḗr, gʷḗn, priHós). It may be called "user" (bʰréwHgtōr `pie-neo-bhrewHgtoxr`) only in talk about the machine.
- Banter: jokes (sméymn̥ `pie-neo-smeymn`), laughter (smḗyti), joy (géh₂dʰos `pie-neo-geh2dhos`). The model can tease gently and be teased.

## 5. Rules that change

- Rule 6 (only slice ids) is unchanged. Neologisms are in your slice, flagged `"coined": "neologism"`, with the gloss to keep to (rule 14: a lexeme only in a sense its gloss gives).
- Formulas (v4 §4) are optional: use one where it is natural ("imperishable fame" in praise, the guest-friend words).
- Meter (v4 §5) does not apply to the dialogue genres.
- Diversity is gated as in v4: one lexeme at most max(6, 0.5% of tokens) times, the slice's `theme_core` up to max(15, 1.5% of tokens). Vary the verbs of saying and the forms of address across texts.

## 6. Check and repair

As in v4, with a Tier 3b batch name (`t3b-<n>`) and the `--tier3b` flag. The records go to `corpus/tier3b/<batch>.jsonl` with `tier: 3` and `neologism: true`, and the validator runs with the neologism table loaded.

1. Write the plans to `data/generation/plans/<batch>.jsonl` and copy it to `<batch>.initial.jsonl`.
2. `uv run python -I scripts/realize_plans.py data/generation/plans/<batch>.initial.jsonl --batch <batch>-initial --tier3b --model <model> --prompt-id tier3b-planner-v1`, and note the numbers, including the gate result and `neologism_tokens`.
3. Delete `corpus/tier3b/<batch>-initial.jsonl` (keep the plan files and the `-initial` batch report).
4. Fix the rejected plans and any lexeme over its cap in `<batch>.jsonl` (one repair pass), then run the same command with `--batch <batch>`.
5. Modify nothing else.

Final message ≤150 words: initial and final reject counts, the gate result, words per text, the neologism token share, distinct lexemes and roots, and anything you could not express.
