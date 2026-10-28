# Knee-supported sleep: pre-registered tests (2026-10-28)

The owner's research packet (through round 49; kept unpublished in `raw/knee-sleep-packets/`) proposes an
inherited PIE association **KNEE[SUPPORT]–SLEEP/DREAM**. Its core anchors are Hittite KUB 36.89 rev. 56′–59′
(*genu-* + *šuppariyant-*, \*swep-) and Greek AP 7.170 (ἐπὶ γούνων … ὕπνον). It leaves one question open:
was the pairing inherited, or put together separately in each tradition from inherited words? The tests
below are fixed before any of them is run. Stage C-S's blind lead (Norse ~ Hittite knee-sleep,
`data/research/8c/leads.jsonl`) is the same question.

## Target relation (from the packet, unchanged)

A knee or knees (or a word for lap that is the knee word) support the participant who sleeps, dreams, is
described as asleep, or dies as sleep. The sleeper may lie on someone else's knees or their own. Kneeling,
trembling knees, knee wounds, and knees and sleep in separate events are not the target. A translation's
"lap" counts only when the source word is identified.

## Test A: typological control (non-Indo-European traditions)

**Question.** Is knee-supported sleep a scene that unrelated traditions also produce? If so, the Hittite–Greek
match carries little genealogical weight on its own.

**Corpora (fixed):** Hebrew Bible; Akkadian and Sumerian literary and ritual texts (open ORACC projects,
ETCSL); Middle Egyptian literature (TLA or an equivalent open corpus); Old and Middle Japanese (Kojiki,
Nihon shoki, Man'yōshū, Heian tales); Classical Chinese (open pre-modern texts); Finnic (Kalevala,
Kanteletar); Classical Arabic poetry and adab (open corpora); and, if openly available, Old Turkic or Mongolian.
Each corpus is searched by its own knee/lap word(s) and sleep/death word(s). Every hit is read in context
and classified by the target relation's rules.

**Already known before registration** (so not counted as finds): Judges 16:19 (Delilah makes Samson sleep
on her knees, Hebrew *birkeyha*); 2 Kings 4:20 (the Shunammite's son sits on his mother's knees until noon
and dies); Akkadian *birku* "knee, lap". Japanese *hizamakura* "knee-pillow" is a known later term; whether
it is attested in the early texts is part of the test.

**Decision rule.** Explicit positives in **≥ 2 unrelated non-IE traditions** (counting Hebrew and Akkadian as
one Semitic tradition) → the scene is typologically ordinary. The inheritance proposal then needs a marked
lexical choice (Tests B, C), not the scene alone. **0 positives** in the searched corpora, with recall shown on
a known item → the scene is rarer than expected, which strengthens the proposal. Exactly 1 → reported as is.

## Test B: Hittite lexical choice

**Question.** Hittite has two sleep verbs: *šeš-* (\*ses-) and *šupp-/šuppariya-* (\*swep-). Is the \*swep- verb
the marked choice in knee or dream contexts?

**Data:** TLHdig (`raw/daughters/hittite-tlhdig/`, CC BY 4.0), all tablets. Count clauses or paragraphs with
each sleep verb, and of those, how many have (i) *genu-* in the same paragraph and (ii) a dream word
(*tešḫa-*, *zašḫai-*). Every knee co-occurrence is read.

**Decision rule.** One-sided Fisher test, p < 0.05, that *šupp-* co-occurs with knees or dream more often than
*šeš-* does. With tiny counts the result is descriptive, and it says so. Lemmatization is automatic: forms are
also matched by a spelling list, and misses found by reading are reported.

## Test C: Greek lexical choice

**Question.** In Greek scenes of knee-supported sleep, is ὕπνος/ὑπνόω (\*swep-) used more than its base rate
in sleep clauses, against εὕδω, κοιμάομαι, καθεύδω, ἰαύω?

**Data:** the project's Greek corpora (Homer, archaic–classical, later Greek). Every γόνυ unit with a sleep word
within the unit is read and classified. The base rate is the share of each sleep lexeme across all sleep
clauses in the same corpora.

**Decision rule** as in Test B.

## Reporting

All three results are reported whatever they are, with the hits read, in
`docs/research/knee-sleep-results.md`. Each test is recorded as done or not done. Tests B and C use automatic
lemmas, so their recall is checked on known passages: KUB 36.89 for Hittite, AP 7.170 if it is in the corpora,
and Il. 9.455/9.488 for knee-setting.
