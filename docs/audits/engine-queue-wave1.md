# Engine and brief queue from the Tier 3 wave-1 reviews (2026-10-28)

These are fixed centrally after wave 1, before wave 2 starts. Each item names the review that found it.

- **PRF 2du/3du cells missing**: a dual request silently becomes plural, with no warning or reject (t024 00010; t023 66dc51f8). Either reject the plan or mark the token, as the existing dual-fallback flag does.
- **Middle 2sg secondary ending**: the engine gives *-th₂e*; the handbooks give \*-th₂es (Skt -thās) (t024). Check against Fortson and Ringe.
- **Per-lexeme cap too tight** at about 700 tokens per batch (cap 6). It forces unnatural substitutions (t029: pigs and "the herd" standing in for cattle) and short texts (16–19 words). Waiting on the t029 reviewer's verdict.
- **Conversation gaps**: question words, names, greetings (agent in progress); "here" (project reconstructions / deictic_ki).
- **Slice keyword gaps**: fox, fly, nest, beak and hunger were not offered (t028).
- **The PIE text doesn't mark who is speaking**, so dialogue reads as a run of lines (t024 review).
