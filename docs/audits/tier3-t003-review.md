# Tier-3 review: packet t003

The packet has 28 items: 7 law codes, 9 dialogues, 9 genealogies and 3 fables. The per-item verdicts are in `docs/audits/packets/t003-verdicts.jsonl`.

The review used handbook knowledge only: Fortson, Ringe, Beekes, LIV-style root shapes and the comparative evidence as I know it. I did no browsing. I checked forms against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json` and engine `Lexicon.cells()`, and ran `validate_text` on every item. The validator passes every engine item: each surface form exists somewhere in its paradigm. All four wrong-slot errors below are therefore invisible to it.

## Counts

| verdict | n |
|---|---|
| ok | 5 (154e2226, a6df661a, 0960dac9, f4c70be6, 7dcf382a) |
| minor | 16 |
| wrong | 7 (6d5fa6fc, 7421739f, 80279bc4, f7fe89bb, 66dd4483, 7eb244b6, ba92cd8f) |

## Wrong: the right paradigm, the wrong cell

Four of the engine items pick a real form from the wrong slot of the paradigm:

- **Vocative for locative.** In 80279bc4, *gʰórdʰe* appears where the locative *gʰórdʰoy* belongs.
- **Ablative for accusative.** In 66dd4483, the object of 'strike' is *swēḱurṓd* where *swēḱuróm* belongs.
- **Instrumental plural for nominative.** In ba92cd8f, the subject is *mr̥wṓys* where *mr̥wós* belongs.
- **2pl for 3sg.** In 7eb244b6, *h₁sté* appears where *h₁ésti* belongs.

A fifth item, 6d5fa6fc, has a person error: 'let us swim' comes out as 3sg *snéh₂eti* where a 1pl form belongs.

ba92cd8f also has a neuter antecedent resumed by masculine *tóns*, an indicative *sléh₂gʷontor* in a 'let them take' clause, and *ḱóymom* 'the kin' standing for 'one of the kin'.

## Wrong: texts that are not engine output

Two items are not engine output.

- **f7fe89bb** is Schleicher's 1868 fable verbatim. I identified it from handbook knowledge.
- **7421739f** is a hybrid of the modern Lehmann–Zgusta and Byrd versions of the same fable. It mixes notations: *h₁ékʷoybʰyos* next to *h₁éḱwoms* in the same line, *agʰnutor* with no laryngeal, and *wewked*.

Both are marked wrong because their forms are impossible under the corpus's laryngealist conventions. They are not engine failures. Keep them only if they are tagged as historical texts.

The third fable, 2ded085f (*kʷíd wēlh₁si*), is fine apart from the missing accent. Its Narten long grade is defensible.

## Recurring minor defects

Most of these are lexicon or paradigm problems, so they will recur across the whole corpus:

- **Aspiration lost in 'seize'.** The engine writes *gʰrébh₂t-* for *gʰrébʰh₂-* (b2192d80, ded62b2d, a97bae6a).
- **Labiovelar lost in 'say'.** The engine writes *wéwket* for *wéwkʷet* (bddf88eb, d82ad50e; also 3633c1b0).
- **Laryngeal dropped in the weak cases of 'daughter'.** The engine writes *dʰugtréy* for *dʰugh₂tréy* (07b67578, 18a0f9f3).
- **Ablaut errors in fixed-grade nouns.** 'King' loses its lengthened ē in the oblique cases and vocative: *h₃réǵey* and *h₃réǵ* (07b67578, 3633c1b0). 'Earth' loses its dʰ in the locative: *ǵʰémi* (ba92cd8f).
- **Vocatives.** *pótnih₂* is used as a vocative where *pótni* belongs (9ab83960). *ph₂tér* is end-accented where the vocative should be accented on the first syllable (d82ad50e).
- **Dual not carried through.** A dual subject or referent gets plural verbs or endings (3633c1b0, 7569b6fa, b2192d80).
- **Masculine names for daughters.** *ym̥tós* (703eeef0) and *solh₂wós* (2bb06cab) are masculine o-stems, while the same texts resume the women with feminine *tā́m*.
- **Other one-offs:**
  - Instrumental plural endings disagree: *kʷetwr̥bʰí* with *gʷéwbʰis* (ffda9f85).
  - The stem of 'nimble' varies: *h₁léngʰus* with *h₁ln̥gʷʰéws* (2bb06cab).
  - The neuter s-stem plural is *wékʷōs* (55994501).
  - The accent of *dédh₃tām* is on the wrong syllable (187bb91d).
  - Yoking puts the wheel in the accusative where a locative belongs (7569b6fa).
  - *gʰóstipotis* 'host' is used for the owner of a dog (ded62b2d).

## The texts as legal prose

The law codes are the strongest genre here. They consistently follow a casuistic pattern that is plausible for Hittite and Vedic:

- a relative protasis, *h₁yós …*, with a subjunctive verb;
- or a conditional protasis, *h₁yód …*, with a subjunctive in *-ē-*;
- then an apodosis introduced by *nu* (a Hittite-flavoured link), with a 3rd-person imperative;
- prohibitions with *mē* + injunctive, and wishes in the optative.

Possession is expressed with a dative relative, *h₁yósmōy h₁éseti* 'to whom there is'. Aorist and present subjunctives are used correctly, and dual verbs agree where the subject is dual (*bʰéh₂etes*, *kʷéyetām*).

Items a97bae6a (the thief), 0960dac9 (the horse sale) and f4c70be6 (the boundary) read like genuine archaic law. The weaknesses are repetitive syntax and the few wrong-slot case errors.

## The texts as dialogue

Vocatives are mostly correct and well placed: *wíHre*, *swéḱure*, *snúse*, *ǵḿ̥re*, *gʰósti*, *bʰréh₂ter*, *dʰúgh₂ter*. The exceptions are *pótnih₂*, *ph₂tér* and *h₃réǵ*. Person and pronoun use is generally right, with good use of the perfect for states (*dedwóyh₂e*, *stestóh₂e*, *wóydth₂e*) and the middle for 'take' and 'dress oneself'.

The prose is choppy: every utterance is a single short clause, and speaker changes are left unmarked after the first *nu X wérh₁t*. That is acceptable as a style for a training corpus, but monotonous. The genealogies reuse formulas well (*ḱléwos ń̥dʰgʷʰitom*, *h₁nómn̥ dʰeh₁-*, *déh₃tōr h₁uséwōm*, *wedʰ-* 'take a wife'). Their names, built from adjectives, often ignore gender.
