# PIE benchmark judge brief

You are grading answers in a benchmark of Proto-Indo-European (PIE). Read the packet file you are given: a JSON
list of items. Each item has a `segment`, the `setting` and `prompt` the contestant saw, a `reference` answer from
the project, and several anonymous `answers` to grade. Grade every answer on its own merits: the reference is one
good answer, not the only one, and a different wording, word order or a mainstream reconstruction of a word the
project spells or chooses differently can be fully right.

Score each answer **1** (right), **0.5** (right in substance, with one minor error) or **0** (wrong):

- **en_pie** (English to PIE): does the PIE say what the English says, grammatically? 1: the meaning is all there
  and every form fits its role (case, number, person, tense and mood, agreement). 0.5: the meaning is there with one
  wrong ending or agreement that does not change it, or one weaker word choice. 0: a meaning error (a wrong or
  missing word, a lost or added negation, a wrong participant), several grammatical errors, not PIE, or empty.
- **pie_en** (PIE to English): does the English say what the PIE says? 1: same meaning. 0.5: one detail wrong or
  missing (tense, number, one word). 0: the meaning is wrong or largely missing.
- **dialogue** (a reply in PIE to a turn in English or PIE): is it a sensible, in-world reply to the turn, in PIE,
  and grammatical? 1: yes. 0.5: sensible but with one grammatical error, or only loosely responsive. 0: not PIE
  (English, or commentary about the language), off-topic, nonsense, or several errors. The speaker lives in the
  PIE world: modern things, or talking about "Proto-Indo-European" as a reconstruction, are wrong.

Notation is not graded here (it is checked separately): don't lower a score for accents, laryngeal notation
(h₁ h₂ h₃ vs H), ḱ/k, or an asterisk.

You may check forms with the project's engine, which knows the project's lexicon and paradigms:

    /Users/david/AI/PIE/training/judge_test/pie-tool analyze "<PIE text>"   # every word: lemma, gloss, cell, or UNKNOWN
    /Users/david/AI/PIE/training/judge_test/pie-tool cells <PIE word>        # the word's full paradigm
    /Users/david/AI/PIE/training/judge_test/pie-tool usage <PIE word>        # corpus sentences using it
    /Users/david/AI/PIE/training/judge_test/pie-tool lexq <english word>     # the lexicon's PIE words for it

UNKNOWN only means the project's lexicon lacks the word; judge it by mainstream reconstruction. Don't open other
files in /Users/david/AI/PIE, and don't try to find out which model wrote an answer.

Write your verdicts as a JSON list to the output file you are given, one object per answer:
`{"answer_id": "...", "score": 1 | 0.5 | 0, "reason": "one short sentence"}`. Grade every answer in the packet.
Then reply with just the number of verdicts you wrote.
