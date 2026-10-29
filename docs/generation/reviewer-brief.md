# Tier 3 batch review brief (`review-v1`, 2026-10-28)

This brief is how each Tier 3 batch is reviewed before release. It writes down the procedure used for
t020–t023 (see docs/audits/tier3-t023-review.md for a finished example). There is no human expert, so every
reviewer is measured against errors planted in the packet. Approval (data/generation/releases/<batch>.json)
is set by the lead after reading the review; a reviewer never approves a batch.

## Steps

1. **Packet:** `uv run python -I scripts/make_review_packet.py <batch> --n 20 --plants 5 --tier1 3`.
   This writes `docs/audits/packets/<batch>-packet.jsonl` (opaque ids; pie, english, genre). The key is in
   `data/audits/`, and **the reviewer must never read anything under data/audits/**.
2. **Blind back-translation** (a separate agent, or done first, before you look at any English):
   - Pick 6 real-looking items and translate their PIE into English, seeing only the `pie` field.
   - Print nothing else: no `english` field, no format check that echoes whole lines.
   - Write `docs/audits/packets/<batch>-blind-translations.jsonl`: `{"item", "english", "uncertain": [...]}`.
   - If an item's English was seen by accident, say so in `uncertain`, as the t023 reviewer did.
3. **Review** every packet item:
   - Write `docs/audits/packets/<batch>-verdicts.jsonl`: `{"item", "verdict": "ok|minor|wrong", "issue"}`.
   - **wrong** = ungrammatical, or the meaning changes: agreement, case, person or number, a malformed key
     verb, or PIE and English that say different things.
   - **minor** = ablaut, accent, notation, or a stretched sense.
   - Check doubtful forms against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`,
     `pie.realize.Lexicon(...).cells()` and `.participle_cells()`.
   - Work from handbook knowledge (Fortson, Beekes, Ringe, LIV², Mallory–Adams); don't quote book text.
   **Write and save the verdicts file before you open `corpus/tier3/` or the plans.** Matching packet items
   to records reveals which items are planted, so plant recall counts only if the verdicts already exist.
   Record the file's sha256 in the report, then look the items up for fixing (t030 review).
4. **Score:** `uv run python -I scripts/score_review.py <batch>`, which writes `data/audits/<batch>-calibration.json`.
   The reviewer may run this script but must not open its key.
5. **Report:** write `docs/audits/tier3-<batch>-review.md` with counts, each wrong item with its fix, the minor
   items, the blind-translation agreement, and whether any finding is an engine gap.
6. **Fix at the source** (the review→fix loop):
   - Plan errors: edit `data/generation/plans/<batch>.jsonl`, then re-realize with the batch's own command.
   - Engine or brief errors: report them; the lead fixes them centrally.
   - Never edit `corpus/tier3/*.jsonl` by hand.

## Release rule (applied by the lead)

Approve when all three hold:
- plant recall is ≥ 4/5;
- real items judged wrong are ≤ 2/20 after the fixes;
- the gate is PASS.

Otherwise the batch stays pending, with the reasons recorded. Approval calls
`pie.batch_release.release_metadata(root, batch, status="approved", evidence=[...], rationale=...)`.
