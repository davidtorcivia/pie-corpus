# 8c next design: thematic parallels and comparable pairing (proposal, not pre-registered)

Drafted 2026-10-24 after the Stage C Celtic wave, at David's request ("these larger thematic parallels are also important to think through and find … think about what and how we are pairing in texts … make them of similar ages"). Nothing here has been built or run. Once David has decided, the chosen parts go into docs/research/8c-preregistration.md before anything is built.

## What went wrong in the Celtic wave
The readers were careful. The pairing gave them little to work with.
- **The pivots were mostly late or derivative.** Of the 4,687 Celtic-pivot bundles, 2,500 (53%) have a witness after 1250. By genre: religious 1,290, annals 622, adaptation 465 (Lucan, Vergil), medical and scientific translations from Latin 454. Verse, where inherited wording is most expected, has only 131 bundles (3%).
- **The partners were mostly late Greek prose.** Of 65,483 partner slots, Greek after 300 BC has 39,552 (60%) and Greek to 300 BC 11,054 (17%, mostly prose). Homer has 359 (0.5%), the Rigveda 283 (0.4%), Hittite 39, and the Edda 3.
- **The cause is retrieval.** Partners were retrieved by shared PIE roots, scored by inverse frequency and capped per pivot, with no stratification by corpus, age or genre. The largest corpus, Galen, Plutarch and Josephus, then supplies most partners, and the commonest roots (*steh₂-*, *dʰeh₁-*, *bʰer-*) supply most of the links. Against a word-shuffle null, retrieval was no better than chance except in the far tail (build report).
- **The anchoring rule blocked one real lead.** Fínán's horse healing (docs/research/8c-addendum-finan.md) was seen and correctly not claimed: its only partners were Greek anatomy. Merseburg II, AV 4.12 and Míach's spell are all in our corpora, but no rule brought them into the same bundle.

## Principle (David, 2026-10-24): pairing is targeted, decoys are the only random part
"It's not a random blind system but we're trying to uncover parallels and not randomly sample language." Every bundle in every slab should be built by targeted pairing: comparable layers, comparable genres and the best candidates, never what the largest corpus happens to supply. Randomness and blinding remain only where they do a job: the embedded decoys measure how often readers "find" parallels that are not there, and the blind review keeps the grading honest. For that control to stay meaningful, decoys must come from the same strata and genres as the real partners, so that a decoy differs from a real bundle only in lacking the shared roots or motifs.

## Proposal 1: pair comparable texts (age and genre strata)
Absolute dates cannot be matched across branches: the Rigveda is about 1,800 years older than the earliest Old Irish saga. What can be matched is each tradition's **earliest and least derivative layer**, and **genre**.

**Archaic layer per tradition** (pivots and partners both drawn from it):

| Tradition | Archaic layer |
|---|---|
| Indo-Iranian | Rigveda; Atharvaveda (both recensions); Gāthās, Yasna, Yašts |
| Greek | Homer, Hesiod, Homeric Hymns, archaic lyric (GLAUx poetry to about 450 BC); not Galen, Plutarch or Josephus |
| Anatolian | Hittite myths, rituals and incantations (TLHdig, CTH by genre) |
| Germanic | Eddic poetry; Old English poetry (including the metrical charms); Merseburg charms and the other OHG/OS minor monuments; skaldic verse (where held) |
| Celtic | Old and Middle Irish saga, law, verse, glosses and charms by language date (witness ≤ 1200, or the edition's linguistic date where the manuscript is late, such as the Táin, *Cath Maige Tuired* and the law tracts); Welsh: the Gododdin, Taliesin and the Mabinogi |
| Italic | Plautus, Cato (including the charms in *De agri cultura*), Lucretius, Catullus (LASLA); Umbrian (Iguvine Tables) |
| Baltic and Slavic | Latvian dainas and Lithuanian dainos (late-attested oral tradition, kept as a separate stratum); the Igor Tale; byliny and Vuk as a late-oral stratum |
| Armenian and Tocharian | pre-translation or native material only (most of DMHP is translation literature) |

**Excluded or separate.** Translations (Bible, Latin school medicine, Lucan and Vergil adaptations), annals, devotional prose, and late Greek prose are not used as pivots or partners. Hagiography is its own stratum for the motif search only, flagged as Christian (Fínán shows it can carry older narrative types, but also medieval charm traditions).

**Genre classes**, each paired only with its own class:
- myth and saga narrative ↔ myth and epic narrative;
- charms and incantations ↔ charms and incantations;
- law and oath ↔ law and oath;
- praise and invocation ↔ praise and invocation;
- lament, funeral and gnomic or wisdom verse ↔ the same;
- glosses go with whatever genre they gloss.

**Retrieval within strata.** Retrieval works as now (shared root groups, inverse frequency), but runs only between compatible strata, with a per-corpus cap of at most a third of a pivot's partners. This stops the largest corpus from filling the bundle.

**Cost.** The archaic layers are small (Rigveda about 160k words, Homer about 200k, Edda about 40k, Old Irish saga and law perhaps 1M tokens), so a full stratified run is far smaller than Stage C. My estimate is about 20 to 40 readers.

## Proposal 2: search for thematic parallels (episodes and motifs, not wording)
Many accepted comparisons are narrative rather than verbal: the healing historiola, the cattle raid, the dragon fight, the hero's choice of short glorious life, the horse sacrifice, the king's truth and the land's fertility. A line-and-root design cannot find these.
- **Unit:** the episode: a scene of 5 to 40 lines or sentences, cut at the editions' section breaks or by a segmenter, within the archaic strata above plus the hagiographic stratum.
- **Motif record:** each episode gets a structured English record:
  - roles (healer, injured animal, hero, opponent, king, poet …);
  - actions in order (journey, injury, incantation, joining …);
  - objects and settings;
  - the motif-feature codes from a fixed vocabulary (built from the 16 Stage A themes, extended to about 200 to 300 codes, modelled on motif-index categories).

  An annotator agent writes it while seeing **one episode at a time**, with no cross-tradition material and no instruction to look for parallels, which limits recall-driven annotation.
- **Candidate pairs:** episodes in different branches that share at least 3 motif codes in the same order, at least one of them rare by inverse frequency over all episodes. Shared cognate words or names are scored as a bonus, not required.
- **Readers** get thematic dossiers: a pivot episode with its candidate episodes, given as text, not just the summaries. They judge whether the shared sequence is specific enough to be inherited.
- **Review grades for thematic claims** (separate from the wording grades):
  - **accepted:** a shared sequence of at least 3 narrative elements in the same order, at least one of them not near-universal, plus a specific detail or cognate name or wording, and no plausible derivation (translation, Christian or classical model, medieval diffusion);
  - **weak:** a shared sequence, but generic or possibly derivative;
  - **reject:** otherwise.
- **Controls:**
  - **embedded decoys:** episodes from the same genre and stratum with matched motif-code counts but no shared rare code;
  - **a non-Indo-European control corpus**, so that universal and areal motifs can be told apart. Candidates: Akkadian and Sumerian epic and incantations from ORACC (open licence), and the Finnish Kalevala and Finnic charms (public domain), which also carry the Merseburg type by borrowing. A motif that pairs as often with these as with Indo-European texts is universal or areal, not evidence of inheritance.
- **Recall risk is higher here** than for wording: famous types (Merseburg, the dragon fight) are in every handbook. Readers mark recalled claims as before. The novelty check matters more, and "known" outcomes count as recovery, not discovery.
- **Cost:**
  - annotation of the archaic and hagiographic strata, perhaps 30 to 60k episodes, at roughly 10 to 25M input tokens;
  - reading: 20 to 40 dossier readers;
  - review and novelty.

## Proposal 3: a cheap pilot first
Before either full design, a pilot on two or three themes. It sets the review rules, the decoy rate and the cost before anything is pre-registered at scale.
- **Healing:** the bone-to-bone type, with Fínán, Merseburg, AV 4.12, *Cath Maige Tuired*, the OE charms and the Finnic control.
- **Cattle raid:** Táin and the other Irish *tána*, RV Vala, Geryon, Hermes' theft.
- **One less famous theme:** for example, the hospitality test or the guest who is a god in disguise.

## Decisions for David
1. Stratified pairing (Proposal 1): yes or no; and whether hagiography and the late oral traditions get their own strata or are left out.
2. Thematic search (Proposal 2): yes or no; and whether to add a non-Indo-European control corpus (ORACC, Kalevala), which is a new acquisition.
3. Pilot first (Proposal 3): recommended.
4. Apply the stratified pairing to every slab: rebuild all of Stage C under Proposal 1, the 159 unread slabs and the Celtic pivots alike. The new build reads the Celtic pivots against new, comparable partners. It is a new pre-registered run, not a re-reading of the Celtic wave, which stays reported as it is. The 159 slabs as built are not read.
