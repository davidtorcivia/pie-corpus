# In-world dialogue brief: archaic conversation (`prompt_id: tier3-dialogue-inworld-v1`)

For Tier 3 batches whose genre is dialogue (council, teaching, weather, travel, …). Owner, 2026-10-30: "keep future
batches in world": a PIE speaker brought to the present should be able to follow the model. These dialogues are
the conversation data, written entirely in the archaic register.

`planner-brief-v4.md` applies in full: the plan format, the rules, meter (dialogue genres are not metered), the
check-and-repair pass. From `planner-brief-3b.md` take **only** these parts, as written there:
- §2 "Requests" (How do you say …? / Tell me … / What is …?), with the topics of your schedule entry, not §2's list;
- §3 "Idioms, not coinages", **except** the two coined options: thanks is praise of the giver or "you are dear to
  me" (ḱéywos), never gʷr̥Htís; welcome is "be dear to us" or VOC gʰóstis + MOD priHós, never gʷr̥Htós;
- §4 "Format: speakers and turns": a `speaker` on every clause (`user`, `model`), exactly two speakers, the user
  first, a new speaker always starts a new sentence, per-sentence `english` on every sentence-initial clause,
  4–14 clauses and 2–8 turns, short turns.

What is different from Tier 3b:
1. **Both speakers belong to the PIE world.** `model` is a man or woman of a household: herds, hearth, kin, gods,
   the seasons. `user` is another person of that world: a guest, a neighbour, a child, an elder, a traveller, a
   young herdsman learning. Neither speaker mentions or knows anything modern.
2. **No coinages.** Your slice has no neologisms; use only inherited words and the closed-class ids. If a concept
   has no word, restructure, or name what is missing in your final message.
3. **Conversation, not narration.** Turns answer each other: questions and answers, requests and replies,
   greetings, advice, teasing, a short story told on request. The model speaks as itself (1st person), addresses
   the user (VOC, 2nd person), and asks things back.
4. **Varied openings.** Vary the forms of address and the verbs of saying across the batch (3b §6); no one
   greeting opens more than a quarter of the dialogues.

Run with Tier 3 commands (no `--tier3b`): the records go to `corpus/tier3/<batch>.jsonl`. Final message ≤150 words
as v4 asks, plus the share of dialogues with a request and anything you could not express.
