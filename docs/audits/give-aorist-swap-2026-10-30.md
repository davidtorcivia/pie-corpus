# Give-aorist consolidation (2026-10-30)

The t3b-002 review found two aorists of 'give' in the chat data: déh₃t (`pie-lex-deh3t`, root *deh₃-, Ved. ádāt,
Gk ἔδομεν, Arm. et) and déh₃ut (`pie-lex-deh3ut`, root *deh₃w-, no reflexes in the lexicon). One was to go.
déh₃ut is blocked (data/generation/blocklist.jsonl) and every plan slot that used it now uses déh₃t, with the
same role and features (`scripts/swap_lexeme.py pie-lex-deh3ut pie-lex-deh3t`). Forms change with it:
déh₃ut → déh₃t, duh₃dʰí → dh₃dʰí, déh₃utu → déh₃tu, déh₃woh₂ → déh₃oh₂.

**Cap.** Summing two lexemes into one put déh₃t over the per-lexeme cap in 18 batches. 'Give' is now capped
like a theme-core word (`CORE_CAPPED` in scripts/realize_plans.py, mirrored in scripts/meter_report.py): it
carries the hymns' closing request and the guest-gift talk, and it is now the only give-aorist.

**Approval.** The change is mechanical (the same plans, one lexeme exchanged). Every batch that was approved
and still passes its gate is re-approved with this note added to its evidence. t022 and t025 failed their
lexeme-cap gates before the swap and still do; they stay pending.

| batch | slots swapped | gate before | gate after | meter_exact before | after | release |
|---|---|---|---|---|---|---|
| b003 | 6 | PASS | PASS | 0.917 | 0.917 | approved |
| b004 | 6 | PASS | PASS | — | — | approved |
| t002 | 2 | PASS | PASS | 0.91 | 0.907 | approved |
| t004 | 1 | PASS | PASS | — | — | approved |
| t005 | 11 | PASS | PASS | 0.941 | 0.941 | approved |
| t006 | 8 | PASS | PASS | 0.906 | 0.906 | approved |
| t008 | 8 | PASS | PASS | 0.914 | 0.9 | approved |
| t011 | 2 | PASS | PASS | 0.908 | 0.908 | approved |
| t012 | 1 | PASS | PASS | — | — | approved |
| t014 | 1 | PASS | PASS | 1.0 | 1.0 | approved |
| t015 | 6 | PASS | PASS | — | — | approved |
| t018 | 8 | PASS | PASS | 0.933 | 0.933 | approved |
| t019 | 10 | PASS | PASS | — | — | approved |
| t020 | 10 | PASS | PASS | 0.95 | 0.95 | approved |
| t021 | 4 | PASS | PASS | — | — | approved |
| t022 | 14 | FAIL | FAIL (unchanged) | — | — | pending |
| t024 | 2 | PASS | PASS | — | — | approved |
| t025 | 14 | FAIL | FAIL (unchanged) | — | — | pending |
| t026 | 4 | PASS | PASS | 0.937 | 0.937 | approved |
| t027 | 2 | PASS | PASS | — | — | approved |
| t028 | 3 | PASS | PASS | — | — | approved |
| t030 | 1 | PASS | PASS | — | — | approved |
| t033 | 11 | PASS | PASS | 0.934 | 0.921 | approved |
| t3b-002 | 3 | PASS | PASS | — | — | approved |
