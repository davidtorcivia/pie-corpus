# Verbs of fearing take the ablative (2026-10-30)

Three reviews (t3b-004, t039, t042) found "fear X" planned with X as the direct object. The corpus's model for
fearing is the Vedic one: bhī- 'fear' + ablative ('fear from the wolf'), as the handbooks give it; the intransitive
verbs of fearing in the lexicon (bʰebʰóyh₂e, bʰéyh₂t, dedwóye, h₂eh₂ógʰe, tréseti, pr̥ksḱéti, tr̥ssḱéti, troméyeti)
are tagged `"valency": "fear"` in data/generation/verb_valency.json, and pie.realize.check_plan rejects an OBJ beside
them. The causatives 'scare' (troséyeti, torgʷéyeti) stay ordinary transitives.

Existing plans: 39 OBJ slots beside a verb of fearing in 14 approved batches (b002, t001, t007, t012, t013, t014,
t015, t017, t020, t021, t030, t033, t3b-002, t3b-006) became ABL, nothing else changed; the batches were
re-realized (`scripts/swap_lexeme.py --rerun …`) and, where they still pass, re-approved with this note. t042 (in
review) is fixed by its reviewer.
