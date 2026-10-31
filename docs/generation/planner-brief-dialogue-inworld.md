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

## Humor (batch t084, owner 2026-10-30)

A batch of in-world humor, in character. Laugh the way the oldest daughter traditions laugh, and build every joke
from the situation and the words, never from a pun (a sound-joke can't survive the engine):
- **Flyting and boasting** (Norse *Lokasenna*, Irish satire, Homeric taunts): two speakers trade insults and boasts;
  the boaster is outdone. Genre `challenge` (a dialogue genre) with speakers.
- **Trickster tales** (the fox, the clever youngest son, a thief outwitted): genre `tale` or `fable`, short, with a
  turn at the end.
- **The comic household:** the guest who eats everything, the lazy son, the drunk at the feast, the boastful
  warrior who fears a mouse, the old man who outwits the young, a quarrel between husband and wife that ends in
  laughter. Genre `dialogue` with speakers.
- **Gentle mockery of the respectable** (the Vedic frog hymn mocks priests as croaking frogs; the gambler's lament
  mocks the gambler): genre `praise` or `hymn` turned comic.
- **Earthy jokes are in-world** (*perd-* 'fart', greed, drink), never crude for its own sake.
- **Funny riddles:** genre `riddle`, an absurd description whose answer is plain.
Mix: about half dialogues with speakers (§4 of brief-3b format), half short tales and comic verse. Every joke must
still be grammatical and say exactly what its English says (v4 rule 14); the English should read as funny on its
own. The `model` speaker, where there is one, is a person of the PIE world who jokes and can be the butt of a joke.

**Finding a word:** your slice is the suggested vocabulary; for anything else run `uv run python -I scripts/lexq.py
<english word>` (v4 rule 6). Look a word up before you write around it.

## Horrors (wave t085–t088, owner 2026-10-30)

"It was a rough world and we should not hide the horrors of it." A wave about what the people of this world feared
and suffered, told the way they would tell it: plainly, by people who lived it, without modern judgment and
without relish. The daughter traditions are frank about it, and so are these texts:
- **Raid and captivity:** the cattle-raid seen from the raided side; the men killed at the fence; women and children
  carried off to serve strangers; a captive's lament far from home; ransom refused (Iliad 1 and 24, the Táin, the
  Rigveda's prayers against the raider).
- **Feud and blood-price:** a kinsman slain, the duty of vengeance, the price of a man paid or refused, a feud that
  eats two families; the oath-breaker's end.
- **Hunger and plague:** the hungry winter, the herds dying of sickness, a famine when the old are left to the
  cold, a charm against a pestilence (the daughters' charms against worms and fevers are models), a child who does not
  wake.
- **Death unprotected:** a man drowned at the ford, a child taken by wolves, a woman dead in childbirth, the dead
  left unburied for the dogs and birds (the epic's worst fate), the burning of a hall with the people inside.
- **The gods' cruelty and the dark rites:** the god who takes, the dead who come back hungry, a sacrifice that costs
  a life (myth and ritual as told, not endorsed or condemned).
- **Curses:** the curse laid on a slayer or an oath-breaker (genre `curse` if the export knows it, else `charm`).

Mix per batch: about half two-speaker dialogues (§4 of brief-3b format: survivors talking, a widow and her son, a
captive and a stranger, a judge and a slayer's kin), half laments, tales, charms and curses. Tone: grief, fear,
anger, endurance; the horror is in the facts said plainly, never in gore for its own sake. No sexual violence is
depicted (captivity may be named; nothing more). Nothing modern; no coinages. Every text must still be grammatical
and say exactly what its English says (v4 rule 14). Run lexq for the hard words (captive, famine, plague, corpse,
mourn, curse, avenge, blood-price): the lexicon round of 2026-10-31 added words and idioms for them.
