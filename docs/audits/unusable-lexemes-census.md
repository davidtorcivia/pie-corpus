# Unusable-lexeme census (2026-10-28)

This census covers every word and derivative in `data/morph/inflection_specs.jsonl` (6,748 rows). Each row is put in one bucket: the first reason, in pool order, that `scripts/make_slice.py` would not offer it to a planner by default. The order is usable spec, blocklist, P10 accent gate, eval holdout root, NIL hold, gloss. "ok" means the row is offered. It was built on branch `worktree-agent-ac6cd6df8f3267bab` after the engine-queue-wave1 fixes. Regenerate the buckets with `scripts/census_unusable.py`.

**Usable specs:** 4,215 before this work and 4,885 after it. The gains are:
- eh₂ backtest gate: +391;
- ox, salt and fox overrides: +3;
- pk-iu-stem rule, where an o-grade root is acrostatic (Fortson §6.21, §6.27): +226 (backtest 84.7% → 89.3%);
- n-stem-ak rule, consonantal root resonant before -n̥: +50 (backtest 82.6% → 85.3%).

**Offered by default ("ok"):** about 1,071 before (now minus the 57 rows unusable at base) and 1,131 after. With `--derived`, a further 2,324 rows are offered, up from 1,983 before.

## Buckets

| bucket | lexemes | with a dictionary gloss | kind of fix |
|---|---|---|---|
| derived gloss only (needs --derived) | 2324 | 0 | gloss data: a dictionary gloss, or the slice built with `--derived` |
| ok | 1131 | 1131 | none needed |
| unknown:noun-shape | 823 | 94 | per word: no shape rule; 783 are unglossed tree derivatives with no part of speech |
| bound-stem (form with a hyphen) | 797 | 113 | not words (roots, stems, suffixes); a citation form would make some usable |
| no-accent (pool P10) | 795 | 76 | per word: an accent from a source (accent manifest category 1) |
| eval-holdout root | 323 | 113 | policy: held out for the cognate/inflection benchmark (pie.export.eval_root) |
| no gloss | 162 | 0 | per word: a gloss |
| NIL hold | 118 | 118 | policy: NIL re-review (docs/audits/nil-merge-rereview.md) |
| indeclinable | 84 | 84 | used as ADV when the part of speech is adv/particle |
| backtest-fail:shape:hk-iu-stem | 47 | 14 | engine: shape rule below 85% or no rule |
| backtest-fail:shape:devi | 47 | 7 | engine: shape rule below 85% or no rule |
| unknown:athematic-no-ablaut | 44 | 1 | engine: shape rule below 85% or no rule |
| blocklist | 32 | 15 | policy: data/generation/blocklist.jsonl |
| backtest-fail:shape:n-stem-hk | 9 | 2 | engine: shape rule below 85% or no rule |
| unknown | 4 | 2 | engine: shape rule below 85% or no rule |
| unknown:adj-shape | 3 | 3 | engine: shape rule below 85% or no rule |
| unknown:verb-shape | 2 | 2 | engine: shape rule below 85% or no rule |
| unknown:middle-only | 2 | 0 | engine: shape rule below 85% or no rule |
| shape:er-stem | 1 | 0 | engine: shape rule below 85% or no rule |

## What was fixed at the source

- **eh₂ backtest** (scripts/classify_lexicon.py): 4 tables were written on another spelling of their own headword. They scored 0/19 and kept the rule at 78.9%. They are now skipped, as thematic tables already were.
- **pk-iu-stem** (pie/classify.py): an accented o-grade root (h₂ówis ~ h₂éwis, h₁ógʷʰis, h₂óḱris) is acrostatic with o/e ablaut (Fortson §6.21). Before a resonant + consonant it stays proterokinetic (h₁órǵʰis, ḱlównis; Fortson §6.27). The 7 tables still missed are pótis/wiḱpótis/gʰóstipotis (no ablaut), gʰóstis (full grade in the weak stem), bʰébʰrus (reduplication), ǵénus (amphikinetic) and pérkus (table kʷ against headword k).
- **n-stem-ak** (pie/classify.py): a root-final liquid or nasal is consonantal before *-n̥*, so the weak stem of h₃érō is h₃rn̥, not h₃r̥n̥ (the table's form). Still missed: the weak stem loses *m* in h₂éḱmō and pléwmō (Ved. aśnás), and tétḱō loses its reduplication.

## Engine rules still below 85% (not changed)

- `shape:devi`: 46/76 (60.5%) on 4 tables.
- `shape:hk-iu-stem`: 43/95 (45.3%) on 5 tables.
- `shape:n-stem-hk`: 27/38 (71.0%) on 2 tables.
  - devī: the 4 tables show three different patterns (déywih₂ ~ diwyéh₂, néptih₂ ~ neptyéh₂, pótnih₂ ~ pótn̥yeh₂). That is too few tables to choose a rule.
  - hk-iu: the oxytone headwords disagree with their own tables (bʰeh₂ǵʰús against table bʰéh₂ǵʰus), and suHnús has an o-grade weak stem.
  - n-stem-hk: loc. ḱwén (e-grade) and the weak stem sh₂in̥ without -m-.

## Per-word lists for data agents

### no-accent (pool P10): 795

Usable spec, headword without accent (P10 keeps it out of slices). Needs a sourced accent; add it as a form override and remove the id from data/morph/accent_unresolved.json.

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-h1edt` | *h₁édt | to (bite →) eat | shape:root-aorist |
| `pie-lex-Heh3syos` | Heh₃syos |  | shape:thematic |
| `pie-lex-Hh3esenos` | Hh₃esenos |  | shape:thematic |
| `pie-lex-Hh3oskyeh2` | Hh₃oskyeh₂ |  | shape:eh2 |
| `pie-lex-Hleymos` | Hleymos |  | shape:thematic |
| `pie-lex-Hreh3dtrom` | Hreh₃dtrom |  | shape:thematic-neuter |
| `pie-lex-HrewHtrom` | HrewHtrom |  | shape:thematic-neuter |
| `pie-lex-Hrigjeh1yeti` | Hriǵeh₁yeti |  | shape:thematic-present |
| `pie-lex-HrowdHeh2` | HrowdHeh₂ |  | shape:eh2 |
| `pie-lex-HrowdHeh2yeti` | HrowdHeh₂yeti |  | shape:thematic-present |
| `pie-lex-HruHdhlom` | HruHdʰlom |  | shape:thematic-neuter |
| `pie-lex-Hrudeh1yeti` | Hrudeh₁yeti |  | shape:thematic-present |
| `pie-lex-bakkos` | bakkos |  | shape:thematic |
| `pie-lex-bakos` | bakos |  | shape:thematic |
| `pie-lex-baktlom` | baktlom |  | shape:thematic-neuter |
| `pie-lex-baktrom` | baktrom |  | shape:thematic-neuter |
| `pie-lex-bhedheh2` | bʰedʰeh₂ |  | shape:eh2 |
| `pie-lex-bhedhrom` | bʰedʰrom |  | shape:thematic-neuter |
| `pie-lex-bhedhyeti` | bʰedʰyeti |  | shape:thematic-present |
| `pie-lex-bheh2geh2` | bʰeh₂geh₂ |  | shape:eh2 |
| `pie-lex-bheh2weh1yeti` | bʰeh₂weh₁yeti |  | shape:thematic-present |
| `pie-lex-bheh2gjos` | bʰeh₂ǵos | oak | table |
| `pie-lex-bhelh1nos` | bʰelh₁nos |  | shape:thematic |
| `pie-lex-bherHos` | bʰerHos |  | shape:thematic |
| `pie-lex-bherh1dyeh2` | bʰerh₁dyeh₂ |  | shape:eh2 |
| `pie-lex-bhernyom` | bʰernyom |  | shape:thematic-neuter |
| `pie-lex-bhersdheti` | bʰersdʰeti |  | shape:thematic-present |
| `pie-lex-bhewdhos` | bʰewdʰos | offerer | shape:thematic |
| `pie-lex-bhh2wedheti` | bʰh₂wedʰeti |  | shape:thematic-present |
| `pie-lex-bhh2weti` | bʰh₂weti |  | shape:thematic-present |
| `pie-lex-bhih2tweh2` | bʰih₂tweh₂ |  | shape:eh2 |
| `pie-lex-bhleh1dhrom` | bʰleh₁dʰrom |  | shape:thematic-neuter |
| `pie-lex-bhleh1yeti` | bʰleh₁yeti |  | shape:thematic-present |
| `pie-lex-bhlendhos` | bʰlendʰos |  | shape:thematic |
| `pie-lex-bhlendhyeti` | bʰlendʰyeti |  | shape:thematic-present |
| `pie-lex-bhlogmos` | bʰlogmos |  | shape:thematic |
| `pie-lex-bhlondhos` | bʰlondʰos |  | shape:thematic |
| `pie-lex-bhldeti` | bʰl̥deti |  | shape:thematic-present |
| `pie-lex-bhlgeh1yeti` | bʰl̥geh₁yeti |  | shape:thematic-present |
| `pie-lex-bhlgmeh2` | bʰl̥gmeh₂ | flame | shape:eh2 |
| `pie-lex-bhlndhos` | bʰl̥ndʰos |  | shape:thematic |
| `pie-lex-bhodhh2wos` | bʰodʰh₂wos |  | shape:thematic |
| `pie-lex-bhodhom` | bʰodʰom |  | shape:thematic-neuter |
| `pie-lex-bhodhos` | bʰodʰos | torment; tormenter | shape:thematic |
| `pie-lex-bhodhyom` | bʰodʰyom |  | shape:thematic-neuter |
| `pie-lex-bhogom` | bʰogom |  | shape:thematic-neuter |
| `pie-lex-bhogyos` | bʰogyos |  | shape:thematic |
| `pie-lex-bholHos` | bʰolHos |  | shape:thematic |
| `pie-lex-bholHtos` | bʰolHtos |  | shape:thematic |
| `pie-lex-bholsos` | bʰolsos |  | shape:thematic |
| `pie-lex-bholtos` | bʰoltos |  | shape:thematic |
| `pie-lex-bholyom` | bʰolyom |  | shape:thematic-neuter |
| `pie-lex-bholgjheh2yeti` | bʰolǵʰeh₂yeti |  | shape:thematic-present |
| `pie-lex-bholgjhineh2` | bʰolǵʰineh₂ |  | shape:eh2 |
| `pie-lex-bholgjhinos` | bʰolǵʰinos |  | shape:thematic |
| `pie-lex-bholgjhnos` | bʰolǵʰnos |  | shape:thematic |
| `pie-lex-bhondheh2` | bʰondʰeh₂ |  | shape:eh2 |
| `pie-lex-bhorHeti` | bʰorHeti |  | shape:thematic-present |
| `pie-lex-bhorHyeti` | bʰorHyeti |  | shape:thematic-present |
| `pie-lex-bhorideh2` | bʰorideh₂ |  | shape:eh2 |
| `pie-lex-bhorneh2` | bʰorneh₂ |  | shape:eh2 |
| `pie-lex-bhornom` | bʰornom | child; bundle | shape:thematic-neuter |
| `pie-lex-bhorsiHneh2` | bʰorsiHneh₂ |  | shape:eh2 |
| `pie-lex-bhowdhos` | bʰowdʰos |  | shape:thematic |
| `pie-lex-bhowghos` | bʰowgʰos |  | shape:thematic |
| `pie-lex-bhoydeh2` | bʰoydeh₂ | pasture | shape:eh2 |
| `pie-lex-bhregeh2` | bʰregeh₂ |  | shape:eh2 |
| `pie-lex-bhriHnos` | bʰriHnos |  | shape:thematic |
| `pie-lex-bhriHos` | bʰriHos |  | shape:thematic |
| `pie-lex-bhriHwos` | bʰriHwos |  | shape:thematic |
| `pie-lex-bhrodhos` | bʰrodʰos |  | shape:thematic |
| `pie-lex-bhruHgeti` | bʰruHgeti |  | shape:thematic-present |
| `pie-lex-bhruHgyeti` | bʰruHgyeti |  | shape:thematic-present |
| `pie-lex-bhrHeh2` | bʰr̥Heh₂ |  | shape:eh2 |
| `pie-lex-bhrHom` | bʰr̥Hom |  | shape:thematic-neuter |
| `pie-lex-bhrskos` | bʰr̥skos |  | shape:thematic |
| `pie-lex-bhrskjos` | bʰr̥sḱos |  | shape:thematic |
| `pie-lex-bhuHeh2` | bʰuHeh₂ |  | shape:eh2 |
| `pie-lex-bhuHlom` | bʰuHlom |  | shape:thematic-neuter |
| `pie-lex-bhuHrom` | bʰuHrom |  | shape:thematic-neuter |
| `pie-lex-bhuHskos` | bʰuHskos |  | shape:thematic |
| `pie-lex-bhuHtikjos` | bʰuHtiḱos |  | shape:thematic |
| `pie-lex-bhexdheh2` | bʰēdʰeh₂ | *oppressing > adversity | shape:eh2 |
| `pie-lex-bhexreh2` | bʰēreh₂ | bier, litter | shape:eh2 |
| `pie-lex-deh2lom` | deh₂lom |  | shape:thematic-neuter |
| `pie-lex-deh2mos` | deh₂mos |  | shape:thematic |
| `pie-lex-deldelh1yeti` | deldelh₁yeti |  | shape:thematic-present |
| `pie-lex-denkjeti` | denḱeti |  | shape:thematic-present |
| `pie-lex-derHgheti` | derHgʰeti |  | shape:thematic-present |
| `pie-lex-derHgheyeti` | derHgʰeyeti |  | shape:thematic-present |
| `pie-lex-derkjom` | derḱom |  | shape:thematic-neuter |
| `pie-lex-dewh2dhrom` | dewh₂dʰrom |  | shape:thematic-neuter |
| `pie-lex-dewkelos` | dewkelos |  | shape:thematic |
| `pie-lex-deynos` | deynos | day | shape:thematic |
| `pie-lex-dlonghos` | dlongʰos | long | table |
| `pie-lex-dnkjos` | dn̥ḱos | gadfly | shape:thematic |
| `pie-lex-doh1los` | doh₁los |  | shape:thematic |
| `pie-lex-dolh1os` | dolh₁os | pain? | shape:thematic |
| `pie-lex-dolh1yeh2` | dolh₁yeh₂ |  | shape:eh2 |
| `pie-lex-domh2os` | domh₂os |  | shape:thematic |
| `pie-lex-donkjos` | donḱos | stinging insect; pincers | shape:thematic |
| `pie-lex-dorHgheh2` | dorHgʰeh₂ |  | shape:eh2 |
| `pie-lex-dowh2dhlom` | dowh₂dʰlom |  | shape:thematic-neuter |
| `pie-lex-dowh2os` | dowh₂os |  | shape:thematic |
| `pie-lex-drexmyeti` | drēmyeti |  | shape:thematic-present |
| `pie-lex-drHghneti` | dr̥Hgʰneti |  | shape:thematic-present |
| `pie-lex-drbhos` | dr̥bʰos |  | shape:thematic |
| `pie-lex-drnos` | dr̥nos |  | shape:thematic |
| `pie-lex-drkjeh2` | dr̥ḱeh₂ |  | shape:eh2 |
| `pie-lex-duh2dhrom` | duh₂dʰrom |  | shape:thematic-neuter |
| `pie-lex-dweh2inos` | dweh₂inos |  | shape:thematic |
| `pie-lex-dwighom` | dwigʰom | split in two | table |
| `pie-lex-dheh1ilyos` | dʰeh₁ilyos |  | shape:thematic |
| `pie-lex-dheh1nom` | dʰeh₁nom |  | shape:thematic-neuter |
| `pie-lex-dheh1nos` | dʰeh₁nos |  | shape:thematic |
| `pie-lex-dheh1tos` | dʰeh₁tos | having given birth | shape:thematic |
| `pie-lex-dhelbheti` | dʰelbʰeti |  | shape:thematic-present |
| `pie-lex-dhelbhtom` | dʰelbʰtom |  | shape:thematic-neuter |
| `pie-lex-dhelh1om` | dʰelh₁om |  | shape:thematic-neuter |
| `pie-lex-dhelh1os` | dʰelh₁os |  | shape:thematic |
| `pie-lex-dhewpeh2` | dʰewpeh₂ |  | shape:eh2 |
| `pie-lex-dheygweti` | dʰeygʷeti |  | shape:thematic-present |
| `pie-lex-dheygwos` | dʰeygʷos |  | shape:thematic |
| `pie-lex-dhh2obhros` | dʰh₂obʰros |  | shape:thematic |
| `pie-lex-dhlbheyeti` | dʰl̥bʰeyeti |  | shape:thematic-present |
| `pie-lex-dhlghos` | dʰl̥gʰos |  | shape:thematic |
| `pie-lex-dhmbhos` | dʰm̥bʰos |  | shape:thematic |
| `pie-lex-dhnghlom` | dʰn̥gʰlom |  | shape:thematic-neuter |
| `pie-lex-dhngwlos` | dʰn̥gʷlos |  | shape:thematic |
| `pie-lex-dhogwhos` | dʰogʷʰos |  | shape:thematic |
| `pie-lex-dholbheh2` | dʰolbʰeh₂ |  | shape:eh2 |
| `pie-lex-dholbhos` | dʰolbʰos |  | shape:thematic |
| `pie-lex-dholbhtom` | dʰolbʰtom |  | shape:thematic-neuter |
| `pie-lex-dholyom` | dʰolyom |  | shape:thematic-neuter |
| `pie-lex-dhonghos` | dʰongʰos |  | shape:thematic |
| `pie-lex-dhowh2eh2` | dʰowh₂eh₂ |  | shape:eh2 |
| `pie-lex-dhowh2mos` | dʰowh₂mos |  | shape:thematic |
| `pie-lex-dhowh2nos` | dʰowh₂nos |  | shape:thematic |
| `pie-lex-dhowh2om` | dʰowh₂om |  | shape:thematic-neuter |
| `pie-lex-dhowpeh2` | dʰowpeh₂ |  | shape:eh2 |
| `pie-lex-dhowsos` | dʰowsos | breath, breathing; animal | shape:thematic |
| `pie-lex-dhoygjhyeh2` | dʰoyǵʰyeh₂ |  | shape:eh2 |
| `pie-lex-dhreh1nom` | dʰreh₁nom |  | shape:thematic-neuter |
| `pie-lex-dhreh1tos` | dʰreh₁tos |  | shape:thematic |
| `pie-lex-dhrewghos` | dʰrewgʰos |  | shape:thematic |
| `pie-lex-dhrnsskjeti` | dʰrn̥ssḱeti |  | shape:thematic-present |
| `pie-lex-dhughos` | dʰugʰos |  | shape:thematic |
| `pie-lex-dhuh2yeh2` | dʰuh₂yeh₂ |  | shape:eh2 |
| `pie-lex-dhunstom` | dʰunstom |  | shape:thematic-neuter |
| `pie-lex-dhurom` | dʰurom | gate, door | shape:thematic-neuter |
| `pie-lex-dhuskos` | dʰuskos | dark-colored | shape:thematic |
| `pie-lex-dhusos` | dʰusos |  | shape:thematic |
| `pie-lex-dhustrom` | dʰustrom |  | shape:thematic-neuter |
| `pie-lex-dhwestyeh2` | dʰwestyeh₂ |  | shape:eh2 |
| `pie-lex-dhworeh2` | dʰworeh₂ |  | shape:eh2 |
| `pie-lex-dhwoxreh2` | dʰwōreh₂ |  | shape:eh2 |
| `pie-lex-geh2widhh1os` | geh₂widʰh₁os |  | shape:thematic |
| `pie-lex-gewlos` | gewlos | vessel, bowl | shape:thematic |
| `pie-lex-gewpeh2` | gewpeh₂ |  | shape:eh2 |
| `pie-lex-glewbhmeh2` | glewbʰmeh₂ |  | shape:eh2 |
| `pie-lex-gleybhos` | gleybʰos |  | shape:thematic |
| `pie-lex-gleybhyeti` | gleybʰyeti |  | shape:thematic-present |
| `pie-lex-gnowHos` | gnowHos |  | shape:thematic |
| `pie-lex-golHos` | golHos |  | shape:thematic |
| `pie-lex-golHweh2` | golHweh₂ |  | shape:eh2 |
| `pie-lex-golHwos` | golHwos |  | shape:thematic |
| `pie-lex-gowHoros` | gowHoros |  | shape:thematic |
| `pie-lex-gownos` | gownos | furry, shaggy | shape:thematic |
| `pie-lex-gowros` | gowros | lock of hair | shape:thematic |
| `pie-lex-greh2yeti` | greh₂yeti |  | shape:thematic-present |
| `pie-lex-gupeh2` | gupeh₂ |  | shape:eh2 |
| `pie-lex-gurnos` | gurnos | back | shape:thematic |
| `pie-lex-ghebheti` | gʰebʰeti |  | shape:thematic-present |
| `pie-lex-ghedeseh2` | gʰedeseh₂ |  | shape:eh2 |
| `pie-lex-gheghugjheh2` | gʰegʰuǵʰeh₂ |  | shape:eh2 |
| `pie-lex-gheghugjhos` | gʰegʰuǵʰos |  | shape:thematic |
| `pie-lex-gheldheti` | gʰeldʰeti |  | shape:thematic-present |
| `pie-lex-gheldhom` | gʰeldʰom |  | shape:thematic-neuter |
| `pie-lex-gheydhyeti` | gʰeydʰyeti |  | shape:thematic-present |
| `pie-lex-ghh1bhleh2` | gʰh₁bʰleh₂ |  | shape:eh2 |
| `pie-lex-ghlindeti` | gʰlindeti | to shine, glint | shape:thematic-present |
| `pie-lex-ghodeh2` | gʰodeh₂ |  | shape:eh2 |
| `pie-lex-ghodom` | gʰodom |  | shape:thematic-neuter |
| `pie-lex-ghodhos` | gʰodʰos |  | shape:thematic |
| `pie-lex-ghoh1bheh2yeti` | gʰoh₁bʰeh₂yeti |  | shape:thematic-present |
| `pie-lex-ghreh1nos` | gʰreh₁nos |  | shape:thematic |
| `pie-lex-ghremnos` | gʰremnos |  | shape:thematic |
| `pie-lex-ghroh1yeti` | gʰroh₁yeti |  | shape:thematic-present |
| `pie-lex-ghrondheh2` | gʰrondʰeh₂ |  | shape:eh2 |
| `pie-lex-ghrondhilos` | gʰrondʰilos |  | shape:thematic |
| `pie-lex-ghrowgjhos` | gʰrowǵʰos |  | shape:thematic |
| `pie-lex-ghrmeh1yeti` | gʰr̥meh₁yeti |  | shape:thematic-present |
| `pie-lex-ghrmeh2` | gʰr̥meh₂ |  | shape:eh2 |
| `pie-lex-ghrmeh2-2` | gʰr̥meh₂ |  | shape:eh2 |
| `pie-lex-gwelHdhlom` | gʷelHdʰlom |  | shape:thematic-neuter |
| `pie-lex-gwelHtlom` | gʷelHtlom |  | shape:thematic-neuter |
| `pie-lex-gwerHos` | gʷerHos |  | shape:thematic |
| `pie-lex-gweyh3tom` | gʷeyh₃tom |  | shape:thematic-neuter |
| `pie-lex-gwh2yeti` | gʷh₂yeti |  | shape:thematic-present |
| `pie-lex-gwlHtrom` | gʷl̥Htrom |  | shape:thematic-neuter |
| `pie-lex-gwlh2enos` | gʷl̥h₂enos |  | shape:thematic |
| `pie-lex-gwogworh3trom` | gʷogʷorh₃trom |  | shape:thematic-neuter |
| `pie-lex-gwolHmos` | gʷolHmos |  | shape:thematic |
| `pie-lex-gworHeh2` | gʷorHeh₂ |  | shape:eh2 |
| `pie-lex-gwotyeti` | gʷotyeti |  | shape:thematic-present |
| `pie-lex-gwowHos` | gʷowHos |  | shape:thematic |
| `pie-lex-gwowos` | gʷowos |  | shape:thematic |
| `pie-lex-gwextyom` | gʷētyom |  | shape:thematic-neuter |
| `pie-lex-gwhedheh2` | gʷʰedʰeh₂ |  | shape:eh2 |
| `pie-lex-gwhedhyeh2` | gʷʰedʰyeh₂ |  | shape:eh2 |
| `pie-lex-gwhodhos` | gʷʰodʰos |  | shape:thematic |
| `pie-lex-h1eh2nos` | h₁eh₂nos | ring | shape:thematic |
| `pie-lex-h1epiplowyom` | h₁epiplowyom |  | shape:thematic-neuter |
| `pie-lex-h1erseh2yeti` | h₁erseh₂yeti |  | shape:thematic-present |
| `pie-lex-h1ersyos` | h₁ersyos |  | shape:thematic |
| `pie-lex-h1eyHwos` | h₁eyHwos |  | shape:thematic |
| `pie-lex-h1eytwom` | h₁eytwom |  | shape:thematic-neuter |
| `pie-lex-h1lengwhtos` | h₁lengʷʰtos |  | shape:thematic |
| `pie-lex-h1lewdherteh2` | h₁lewdʰerteh₂ |  | shape:eh2 |
| `pie-lex-h1lewdhertos` | h₁lewdʰertos |  | shape:thematic |
| `pie-lex-h1lh1onbhos` | h₁l̥h₁onbʰos |  | shape:thematic |
| `pie-lex-h1reh1weh2` | h₁reh₁weh₂ |  | shape:eh2 |
| `pie-lex-h1roh1trom` | h₁roh₁trom |  | shape:thematic-neuter |
| `pie-lex-h1roh1weh2` | h₁roh₁weh₂ |  | shape:eh2 |
| `pie-lex-h1roh1wos` | h₁roh₁wos |  | shape:thematic |
| `pie-lex-h1roh1yeti` | h₁roh₁yeti |  | shape:thematic-present |
| `pie-lex-h1rowdhsos` | h₁rowdʰsos |  | shape:thematic |
| `pie-lex-h1rowgos` | h₁rowgos |  | shape:thematic |
| `pie-lex-h1rudhyos` | h₁rudʰyos |  | shape:thematic-adj |
| `pie-lex-h1rh1tlom` | h₁r̥h₁tlom |  | shape:thematic-neuter |
| `pie-lex-h1uh2kos` | h₁uh₂kos |  | shape:thematic |
| `pie-lex-h1uh2nos` | h₁uh₂nos | lacking, empty | shape:thematic-adj |
| `pie-lex-h1usyeh2` | h₁usyeh₂ |  | shape:eh2 |
| `pie-lex-h1weh2nos` | h₁weh₂nos | empty, extinguished | shape:thematic-adj |
| `pie-lex-h1weh2stos` | h₁weh₂stos |  | shape:thematic |
| `pie-lex-h1weydhh1os` | h₁weydʰh₁os |  | shape:thematic |
| `pie-lex-h1yeHwos` | h₁yeHwos |  | shape:thematic |
| `pie-lex-h1exgwhryos` | h₁ēgʷʰryos |  | shape:thematic |
| `pie-lex-h2edbhereti` | h₂edbʰereti |  | shape:thematic-present |
| `pie-lex-h2eldhrom` | h₂eldʰrom |  | shape:thematic-neuter |
| `pie-lex-h2elmntom` | h₂elmn̥tom |  | shape:thematic-neuter |
| `pie-lex-h2elmos` | h₂elmos |  | shape:thematic |
| `pie-lex-h2emseti` | h₂emseti |  | shape:thematic-present |
| `pie-lex-h2emsos` | h₂emsos |  | shape:thematic |
| `pie-lex-h2enh1mos` | h₂enh₁mos | breath | table |
| `pie-lex-h2enh1slos` | h₂enh₁slos |  | shape:thematic |
| `pie-lex-h2enh1tom` | h₂enh₁tom | breath, panting | shape:thematic-neuter |
| `pie-lex-h2enh1gjhom` | h₂enh₁ǵʰom |  | shape:thematic-neuter |
| `pie-lex-h2enkos-2` | h₂enkos |  | shape:thematic |
| `pie-lex-h2enkulos` | h₂enkulos |  | shape:thematic |
| `pie-lex-h2erHmos` | h₂erHmos |  | shape:thematic |
| `pie-lex-h2ereh2ksneh2` | h₂ereh₂ksneh₂ |  | shape:eh2 |
| `pie-lex-h2erkeh2` | h₂erkeh₂ |  | shape:eh2 |
| `pie-lex-h2erkeseh2` | h₂erkeseh₂ |  | shape:eh2 |
| `pie-lex-h2euskjlteh2yeti` | h₂eusḱl̥teh₂yeti |  | shape:thematic-present |
| `pie-lex-h2ewh1eleh2` | h₂ewh₁eleh₂ |  | shape:eh2 |
| `pie-lex-h2ewseti` | h₂ewseti |  | shape:thematic-present |
| `pie-lex-h2ewsyeti` | h₂ewsyeti |  | shape:thematic-present |
| `pie-lex-h2ewyom` | h₂ewyom |  | shape:thematic-neuter |
| `pie-lex-h2eysos` | h₂eysos | request | shape:thematic |
| `pie-lex-h2ekjoneh2` | h₂eḱoneh₂ |  | shape:eh2 |
| `pie-lex-h2grtrom` | h₂gr̥trom |  | shape:thematic-neuter |
| `pie-lex-h2lewghos` | h₂lewgʰos |  | shape:thematic |
| `pie-lex-h2liHmos` | h₂liHmos |  | shape:thematic |
| `pie-lex-h2liHnos` | h₂liHnos |  | shape:thematic |
| `pie-lex-h2lowghnos` | h₂lowgʰnos |  | shape:thematic |
| `pie-lex-h2lowghos` | h₂lowgʰos |  | shape:thematic |
| `pie-lex-h2loybhom` | h₂loybʰom |  | shape:thematic-neuter |
| `pie-lex-h2meh1tom` | h₂meh₁tom |  | shape:thematic-neuter |
| `pie-lex-h2meh1tweh2` | h₂meh₁tweh₂ |  | shape:eh2 |
| `pie-lex-h2mh1eh2` | h₂mh₁eh₂ |  | shape:eh2 |
| `pie-lex-h2mh1eh2tos` | h₂mh₁eh₂tos |  | shape:thematic |
| `pie-lex-h2mh1eh2yeti` | h₂mh₁eh₂yeti |  | shape:thematic-present |
| `pie-lex-h2mh1tweh2` | h₂mh₁tweh₂ |  | shape:eh2 |
| `pie-lex-h2nkos` | h₂n̥kos |  | shape:thematic |
| `pie-lex-h2olteros` | h₂olteros |  | shape:thematic |
| `pie-lex-h2olyos` | h₂olyos |  | shape:thematic |
| `pie-lex-h2orkos` | h₂orkos |  | shape:thematic |
| `pie-lex-h2oydskeh2` | h₂oydskeh₂ |  | shape:eh2 |
| `pie-lex-h2riHmom` | h₂riHmom |  | shape:thematic-neuter |
| `pie-lex-h2rh3eh2` | h₂r̥h₃eh₂ | fertile soil | shape:eh2 |
| `pie-lex-h2uh1lyeh2` | h₂uh₁lyeh₂ |  | shape:eh2 |
| `pie-lex-h2welh1trom` | h₂welh₁trom |  | shape:thematic-neuter |
| `pie-lex-h2wleipkjeh2` | h₂wleipḱeh₂ |  | shape:eh2 |
| `pie-lex-h2wlopkjeh2` | h₂wlopḱeh₂ |  | shape:eh2 |
| `pie-lex-h2wlh1eh1yeti` | h₂wl̥h₁eh₁yeti |  | shape:thematic-present |
| `pie-lex-h2wlh1os` | h₂wl̥h₁os |  | shape:thematic |
| `pie-lex-h2woldhyeh2` | h₂woldʰyeh₂ |  | shape:eh2 |
| `pie-lex-h2wolh1kjnom` | h₂wolh₁ḱnom |  | shape:thematic-neuter |
| `pie-lex-h2wolh1kjos` | h₂wolh₁ḱos |  | shape:thematic |
| `pie-lex-h2yewdhos` | h₂yewdʰos |  | shape:thematic |
| `pie-lex-h2expeh2` | h₂ēpeh₂ |  | shape:eh2 |
| `pie-lex-h3edolos` | h₃edolos |  | shape:thematic |
| `pie-lex-h3enHostos` | h₃enHostos | loaded; burdened | shape:thematic-adj |
| `pie-lex-h3eyth1seti` | h₃eyth₁seti |  | shape:thematic-present |
| `pie-lex-h3meygjhos` | h₃meyǵʰos | urine | shape:thematic |
| `pie-lex-h3meygjhyeti` | h₃meyǵʰyeti |  | shape:thematic-present |
| `pie-lex-h3mighsom` | h₃migʰsom |  | shape:thematic-neuter |
| `pie-lex-h3mighstos` | h₃migʰstos |  | shape:thematic |
| `pie-lex-h3moygjhos` | h₃moyǵʰos | urine | shape:thematic |
| `pie-lex-h3nobheh2` | h₃nobʰeh₂ | hub; navel | shape:eh2 |
| `pie-lex-h3orbhyom` | h₃orbʰyom |  | shape:thematic-neuter |
| `pie-lex-h3rewHdhh1eti` | h₃rewHdʰh₁eti |  | shape:thematic-present |
| `pie-lex-h3rewHkyeti` | h₃rewHkyeti |  | shape:thematic-present |
| `pie-lex-h3rewHmos` | h₃rewHmos |  | shape:thematic |
| `pie-lex-h3rewHyeti` | h₃rewHyeti |  | shape:thematic-present |
| `pie-lex-h3reweti` | h₃reweti |  | shape:thematic-present |
| `pie-lex-h3rewseti` | h₃rewseti |  | shape:thematic-present |
| `pie-lex-h3reyHdhom` | h₃reyHdʰom |  | shape:thematic-neuter |
| `pie-lex-h3reyHtrom` | h₃reyHtrom |  | shape:thematic-neuter |
| `pie-lex-h3riHndos` | h₃riHndos |  | shape:thematic |
| `pie-lex-h3rinHos` | h₃rinHos |  | shape:thematic |
| `pie-lex-h3rowsos` | h₃rowsos |  | shape:thematic |
| `pie-lex-h3royHdheh2` | h₃royHdʰeh₂ |  | shape:eh2 |
| `pie-lex-h3royHeti` | h₃royHeti |  | shape:thematic-present |
| `pie-lex-h3royHkeh2` | h₃royHkeh₂ |  | shape:eh2 |
| `pie-lex-h3yebhos` | h₃yebʰos |  | shape:thematic |
| `pie-lex-kaghyos` | kagʰyos |  | shape:thematic |
| `pie-lex-kakkeh2` | kakkeh₂ |  | shape:eh2 |
| `pie-lex-keHidos` | keHidos |  | shape:thematic |
| `pie-lex-kelHtrom` | kelHtrom |  | shape:thematic-neuter |
| `pie-lex-kendos` | kendos |  | shape:thematic |
| `pie-lex-keneti` | keneti |  | shape:thematic-present |
| `pie-lex-keniHnos` | keniHnos |  | shape:thematic |
| `pie-lex-kenyeh2` | kenyeh₂ |  | shape:eh2 |
| `pie-lex-kerpos` | kerpos |  | shape:thematic |
| `pie-lex-kerssneh2` | kerssneh₂ |  | shape:eh2 |
| `pie-lex-keyh2eti` | keyh₂eti |  | shape:thematic-present |
| `pie-lex-kh2empeh2` | kh₂empeh₂ |  | shape:eh2 |
| `pie-lex-kh2empos` | kh₂empos |  | shape:thematic |
| `pie-lex-kh2emptos` | kh₂emptos |  | shape:thematic |
| `pie-lex-kh2oydeh2yeti` | kh₂oydeh₂yeti |  | shape:thematic-present |
| `pie-lex-kleh2udeti` | kleh₂udeti |  | shape:thematic-present |
| `pie-lex-kleh2uyeti` | kleh₂uyeti |  | shape:thematic-present |
| `pie-lex-kleh2weh2` | kleh₂weh₂ |  | shape:eh2 |
| `pie-lex-kleh2wos` | kleh₂wos |  | shape:thematic |
| `pie-lex-kloh2uyos` | kloh₂uyos |  | shape:thematic |
| `pie-lex-klHlom` | kl̥Hlom |  | shape:thematic-neuter |
| `pie-lex-klpos` | kl̥pos |  | shape:thematic |
| `pie-lex-kmHelos` | km̥Helos | bumblebee | shape:thematic |
| `pie-lex-knyos` | kn̥yos |  | shape:thematic |
| `pie-lex-kolHweh2` | kolHweh₂ |  | shape:eh2 |
| `pie-lex-kolh2dos` | kolh₂dos |  | shape:thematic |
| `pie-lex-kolh2geh2` | kolh₂geh₂ |  | shape:eh2 |
| `pie-lex-kolpos` | kolpos |  | shape:thematic |
| `pie-lex-komHeh2ros` | komHeh₂ros |  | shape:thematic |
| `pie-lex-komHonieh2` | komHonieh₂ |  | shape:eh2 |
| `pie-lex-komHonyos` | komHonyos |  | shape:thematic |
| `pie-lex-konos` | konos |  | shape:thematic |
| `pie-lex-koros` | koros | war; army | shape:thematic |
| `pie-lex-koryonos` | koryonos |  | shape:thematic |
| `pie-lex-koryos-2` | koryos | army, war band | shape:thematic |
| `pie-lex-kowh2eti` | kowh₂eti |  | shape:thematic-present |
| `pie-lex-kreydeh2` | kreydeh₂ |  | shape:eh2 |
| `pie-lex-kreydhrom` | kreydʰrom | sieve | shape:thematic-neuter |
| `pie-lex-kreytros` | kreytros |  | shape:thematic |
| `pie-lex-krowsos` | krowsos |  | shape:thematic |
| `pie-lex-kruseh2` | kruseh₂ |  | shape:eh2 |
| `pie-lex-ksulom` | ksulom |  | shape:thematic-neuter |
| `pie-lex-ksweybheh2yeti` | ksweybʰeh₂yeti |  | shape:thematic-present |
| `pie-lex-kuh2yos` | kuh₂yos |  | shape:thematic |
| `pie-lex-koxlom` | kōlom |  | shape:thematic-neuter |
| `pie-lex-kwelh1esyeti` | kʷelh₁esyeti |  | shape:thematic-present |
| `pie-lex-kwelh1h3onh2os` | kʷelh₁h₃onh₂os |  | shape:thematic |
| `pie-lex-kwelh1om` | kʷelh₁om |  | shape:thematic-neuter |
| `pie-lex-kweynos` | kʷeynos |  | shape:thematic |
| `pie-lex-kwih1meh2` | kʷih₁meh₂ |  | shape:eh2 |
| `pie-lex-kwilpeh2` | kʷilpeh₂ |  | shape:eh2 |
| `pie-lex-kwolpeh2` | kʷolpeh₂ | bending, turning | shape:eh2 |
| `pie-lex-kwoyh1eyeti` | kʷoyh₁eyeti |  | shape:thematic-present |
| `pie-lex-kwryos` | kʷr̥yos |  | shape:thematic |
| `pie-lex-kwyeh1tos` | kʷyeh₁tos |  | shape:thematic |
| `pie-lex-kwexreh2` | kʷēreh₂ |  | shape:eh2 |
| `pie-lex-legtos` | legtos |  | shape:thematic |
| `pie-lex-leghrom` | legʰrom |  | shape:thematic-neuter |
| `pie-lex-leghtos` | legʰtos |  | shape:thematic |
| `pie-lex-leghyeh2` | legʰyeh₂ |  | shape:eh2 |
| `pie-lex-leghyom` | legʰyom |  | shape:thematic-neuter |
| `pie-lex-leh1enos` | leh₁enos |  | shape:thematic |
| `pie-lex-leh1tos` | leh₁tos |  | shape:thematic |
| `pie-lex-leh2dheh2` | leh₂dʰeh₂ |  | shape:eh2 |
| `pie-lex-leh2dheti` | leh₂dʰeti |  | shape:thematic-present |
| `pie-lex-leh2unom` | leh₂unom |  | shape:thematic-neuter |
| `pie-lex-leh2utom` | leh₂utom |  | shape:thematic-neuter |
| `pie-lex-leh2weti` | leh₂weti |  | shape:thematic-present |
| `pie-lex-leidsktos` | leidsktos |  | shape:thematic |
| `pie-lex-lentos` | lentos |  | shape:thematic |
| `pie-lex-lestrom` | lestrom |  | shape:thematic-neuter |
| `pie-lex-leubheh2` | leubʰeh₂ |  | shape:eh2 |
| `pie-lex-lewdos` | lewdos |  | shape:thematic |
| `pie-lex-lewktos` | lewktos |  | shape:thematic |
| `pie-lex-leygjos` | leyǵos |  | shape:thematic |
| `pie-lex-leygjheh2` | leyǵʰeh₂ |  | shape:eh2 |
| `pie-lex-legjnom` | leǵnom |  | shape:thematic-neuter |
| `pie-lex-lh2belos` | lh₂belos |  | shape:thematic |
| `pie-lex-lipos` | lipos |  | shape:thematic |
| `pie-lex-lndheh2` | ln̥dʰeh₂ |  | shape:eh2 |
| `pie-lex-lndhom` | ln̥dʰom |  | shape:thematic-neuter |
| `pie-lex-lndhwyom` | ln̥dʰwyom |  | shape:thematic-neuter |
| `pie-lex-loghyom` | logʰyom |  | shape:thematic-neuter |
| `pie-lex-loh2ugos` | loh₂ugos |  | shape:thematic |
| `pie-lex-londhom` | londʰom |  | shape:thematic-neuter |
| `pie-lex-londhwos` | londʰwos |  | shape:thematic |
| `pie-lex-lowbhom` | lowbʰom |  | shape:thematic-neuter |
| `pie-lex-lowh2nom` | lowh₂nom |  | shape:thematic-neuter |
| `pie-lex-lowksneh2-2` | lowksneh₂ | moon | shape:eh2 |
| `pie-lex-lowkstrom` | lowkstrom |  | shape:thematic-neuter |
| `pie-lex-loydeh2` | loydeh₂ |  | shape:eh2 |
| `pie-lex-loypos` | loypos | ointment, glue | shape:thematic |
| `pie-lex-loystos` | loystos |  | shape:thematic |
| `pie-lex-loygjhos` | loyǵʰos |  | shape:thematic |
| `pie-lex-logjos` | loǵos |  | shape:thematic |
| `pie-lex-lubheh1yeti` | lubʰeh₁yeti |  | shape:thematic-present |
| `pie-lex-lubhom` | lubʰom |  | shape:thematic-neuter |
| `pie-lex-ludeh2yeti` | ludeh₂yeti |  | shape:thematic-present |
| `pie-lex-lukeh2` | lukeh₂ |  | shape:eh2 |
| `pie-lex-lexgyeh2` | lēgyeh₂ |  | shape:eh2 |
| `pie-lex-lh2ewnom` | l̥h₂ewnom |  | shape:thematic-neuter |
| `pie-lex-lh2ewos` | l̥h₂ewos |  | shape:thematic |
| `pie-lex-lh2utlom` | l̥h₂utlom |  | shape:thematic-neuter |
| `pie-lex-mdeh1yeti` | mdeh₁yeti |  | shape:thematic-present |
| `pie-lex-megwros` | megʷros |  | shape:thematic |
| `pie-lex-meh1reh2` | meh₁reh₂ |  | shape:eh2 |
| `pie-lex-meh2nos` | meh₂nos |  | shape:thematic |
| `pie-lex-meh2ros-2` | meh₂ros |  | shape:thematic |
| `pie-lex-melh2wom` | melh₂wom |  | shape:thematic-neuter |
| `pie-lex-memseh2` | memseh₂ |  | shape:eh2 |
| `pie-lex-mendos` | mendos |  | shape:thematic |
| `pie-lex-mendwos` | mendwos |  | shape:thematic |
| `pie-lex-mendyenos` | mendyenos |  | shape:thematic |
| `pie-lex-mendyonos` | mendyonos |  | shape:thematic |
| `pie-lex-mendyos` | mendyos |  | shape:thematic |
| `pie-lex-meneh2` | meneh₂ |  | shape:eh2 |
| `pie-lex-meteti` | meteti |  | shape:thematic-present |
| `pie-lex-metlyom` | metl̥yom |  | shape:thematic-neuter |
| `pie-lex-mewsom` | mewsom |  | shape:thematic-neuter |
| `pie-lex-mewsyeh2` | mewsyeh₂ |  | shape:eh2 |
| `pie-lex-meyeh2yeti` | meyeh₂yeti |  | shape:thematic-present |
| `pie-lex-meyth2mos` | meyth₂mos |  | shape:thematic |
| `pie-lex-mh1trom` | mh₁trom |  | shape:thematic-neuter |
| `pie-lex-mh2kjeh1yeti` | mh₂ḱeh₁yeti |  | shape:thematic-present |
| `pie-lex-miteh2` | miteh₂ |  | shape:eh2 |
| `pie-lex-mluHos` | mluHos |  | shape:thematic |
| `pie-lex-mlh2kos` | ml̥h₂kos |  | shape:thematic |
| `pie-lex-mlnos` | ml̥nos |  | shape:thematic |
| `pie-lex-mlwHeh2` | ml̥wHeh₂ |  | shape:eh2 |
| `pie-lex-moh1ros` | moh₁ros |  | shape:thematic |
| `pie-lex-moldos` | moldos | soft, young, tender | shape:thematic-adj |
| `pie-lex-molh2eti` | molh₂eti |  | shape:thematic-present |
| `pie-lex-molh2mos` | molh₂mos |  | shape:thematic |
| `pie-lex-molh2tos` | molh₂tos |  | shape:thematic |
| `pie-lex-molh3tos` | molh₃tos |  | shape:thematic |
| `pie-lex-mosgos` | mosgos |  | shape:thematic |
| `pie-lex-mowskos` | mowskos |  | shape:thematic |
| `pie-lex-moydeti` | moydeti |  | shape:thematic-present |
| `pie-lex-moyneh2` | moyneh₂ |  | shape:eh2 |
| `pie-lex-moynos` | moynos |  | shape:thematic |
| `pie-lex-moyros` | moyros |  | shape:thematic |
| `pie-lex-moyryom` | moyryom |  | shape:thematic-neuter |
| `pie-lex-moyteh2` | moyteh₂ |  | shape:eh2 |
| `pie-lex-moyth2tom` | moyth₂tom |  | shape:thematic-neuter |
| `pie-lex-mrh2seh2` | mr̥h₂seh₂ |  | shape:eh2 |
| `pie-lex-mrh2tlom` | mr̥h₂tlom |  | shape:thematic-neuter |
| `pie-lex-musom` | musom |  | shape:thematic-neuter |
| `pie-lex-musos` | musos |  | shape:thematic |
| `pie-lex-nebhelos` | nebʰelos |  | shape:thematic |
| `pie-lex-negwnos` | negʷnos | naked | shape:thematic-adj |
| `pie-lex-negwros` | negʷros |  | shape:thematic |
| `pie-lex-nemeseh2` | nemeseh₂ |  | shape:eh2 |
| `pie-lex-nogwedhos` | nogʷedʰos |  | shape:thematic |
| `pie-lex-noh2weyeti` | noh₂weyeti |  | shape:thematic-present |
| `pie-lex-nuh2eh2` | nuh₂eh₂ |  | shape:eh2 |
| `pie-lex-nh2ritos` | n̥h₂ritos |  | shape:thematic |
| `pie-lex-nskwetos` | n̥skʷetos |  | shape:thematic |
| `pie-lex-pedeh2` | pedeh₂ | footprint, track; after | shape:eh2 |
| `pie-lex-pedeti` | pedeti |  | shape:thematic-present |
| `pie-lex-pedom` | pedom | step | shape:thematic-neuter |
| `pie-lex-peh2dhlom` | peh₂dʰlom |  | shape:thematic-neuter |
| `pie-lex-peh2dhrom` | peh₂dʰrom |  | shape:thematic-neuter |
| `pie-lex-peh2ukos` | peh₂ukos |  | shape:thematic |
| `pie-lex-peh2woporh3os` | peh₂woporh₃os | providing little | shape:thematic |
| `pie-lex-peh2gjos` | peh₂ǵos |  | shape:thematic |
| `pie-lex-peh2gjsleh2` | peh₂ǵsleh₂ |  | shape:eh2 |
| `pie-lex-pelmos` | pelmos |  | shape:thematic |
| `pie-lex-perkwHnos` | perkʷHnos |  | shape:thematic |
| `pie-lex-pewHlos` | pewHlos |  | shape:thematic |
| `pie-lex-pewHlyos` | pewHlyos |  | shape:thematic |
| `pie-lex-pewkjyeh2` | pewḱyeh₂ |  | shape:eh2 |
| `pie-lex-pekjteti` | peḱteti |  | shape:thematic-present |
| `pie-lex-ph2weros` | ph₂weros |  | shape:thematic |
| `pie-lex-ph2wos` | ph₂wos |  | shape:thematic |
| `pie-lex-ph2gjeh2` | ph₂ǵeh₂ |  | shape:eh2 |
| `pie-lex-ph2kjyom` | ph₂ḱyom |  | shape:thematic-neuter |
| `pie-lex-pih3wom` | pih₃wom |  | shape:thematic-neuter |
| `pie-lex-pisenom` | pisenom |  | shape:thematic-neuter |
| `pie-lex-pistlom` | pistlom |  | shape:thematic-neuter |
| `pie-lex-pleh2geti` | pleh₂geti |  | shape:thematic-present |
| `pie-lex-pleh2gyeti` | pleh₂gyeti |  | shape:thematic-present |
| `pie-lex-pleh2kyeti` | pleh₂kyeti |  | shape:thematic-present |
| `pie-lex-pleh2ngeti` | pleh₂ngeti |  | shape:thematic-present |
| `pie-lex-pleh2nos` | pleh₂nos |  | shape:thematic |
| `pie-lex-pleh2sos` | pleh₂sos |  | shape:thematic |
| `pie-lex-pleh2trom` | pleh₂trom |  | shape:thematic-neuter |
| `pie-lex-plewksmeh2` | plewksmeh₂ |  | shape:eh2 |
| `pie-lex-plewsteh2` | plewsteh₂ |  | shape:eh2 |
| `pie-lex-plewtyom` | plewtyom |  | shape:thematic-neuter |
| `pie-lex-ploh2nos` | ploh₂nos |  | shape:thematic |
| `pie-lex-ploh2trom` | ploh₂trom |  | shape:thematic-neuter |
| `pie-lex-plokonos` | plokonos |  | shape:thematic |
| `pie-lex-plokos` | plokos |  | shape:thematic |
| `pie-lex-plowmos` | plowmos |  | shape:thematic |
| `pie-lex-plowtyom` | plowtyom |  | shape:thematic-neuter |
| `pie-lex-plokjsom` | ploḱsom |  | shape:thematic-neuter |
| `pie-lex-pludom` | pludom |  | shape:thematic-neuter |
| `pie-lex-plusos` | plusos |  | shape:thematic |
| `pie-lex-plexweh2` | plēweh₂ |  | shape:eh2 |
| `pie-lex-plh1gom` | pl̥h₁gom |  | shape:thematic-neuter |
| `pie-lex-plh2emeh2` | pl̥h₂emeh₂ | palm | shape:eh2 |
| `pie-lex-plh2trom` | pl̥h₂trom |  | shape:thematic-neuter |
| `pie-lex-plneh2` | pl̥neh₂ |  | shape:eh2 |
| `pie-lex-poh2gjeh2` | poh₂ǵeh₂ |  | shape:eh2 |
| `pie-lex-polHwos` | polHwos |  | shape:thematic |
| `pie-lex-polh2nos` | polh₂nos | flat, open | shape:thematic-adj |
| `pie-lex-polyeti` | polyeti |  | shape:thematic-present |
| `pie-lex-poplh1os` | poplh₁os |  | shape:thematic |
| `pie-lex-porh2neh2` | porh₂neh₂ |  | shape:eh2 |
| `pie-lex-porh3sos` | porh₃sos |  | shape:thematic |
| `pie-lex-poros` | poros |  | shape:thematic |
| `pie-lex-porsos` | porsos |  | shape:thematic |
| `pie-lex-pougjneh2` | pouǵneh₂ |  | shape:eh2 |
| `pie-lex-poyh2dos` | poyh₂dos |  | shape:thematic |
| `pie-lex-poyh2weh2` | poyh₂weh₂ |  | shape:eh2 |
| `pie-lex-poystom` | poystom |  | shape:thematic-neuter |
| `pie-lex-pokjsom` | poḱsom |  | shape:thematic-neuter |
| `pie-lex-preslom` | preslom |  | shape:thematic-neuter |
| `pie-lex-preswos` | preswos |  | shape:thematic |
| `pie-lex-priHyetor` | priHyetor |  | shape:thematic-middle |
| `pie-lex-priismmos` | priism̥mos |  | shape:thematic |
| `pie-lex-prowos` | prowos |  | shape:thematic |
| `pie-lex-prh2mos` | pr̥h₂mos | first | shape:thematic |
| `pie-lex-prkjeh2` | pr̥ḱeh₂ |  | shape:eh2 |
| `pie-lex-puHlos` | puHlos |  | shape:thematic |
| `pie-lex-puHlyos` | puHlyos |  | shape:thematic |
| `pie-lex-pugjneh2` | puǵneh₂ |  | shape:eh2 |
| `pie-lex-pukjteh2` | puḱteh₂ |  | shape:eh2 |
| `pie-lex-sdherbheti` | sdʰerbʰeti |  | shape:thematic-present |
| `pie-lex-sedyeh2` | sedyeh₂ |  | shape:eh2 |
| `pie-lex-seh1ros` | seh₁ros |  | shape:thematic |
| `pie-lex-seh1tos` | seh₁tos |  | shape:thematic |
| `pie-lex-seh1yos` | seh₁yos |  | shape:thematic |
| `pie-lex-seh1ytom` | seh₁ytom |  | shape:thematic-neuter |
| `pie-lex-seh2gnos` | seh₂gnos |  | shape:thematic |
| `pie-lex-sekweti` | sekʷeti |  | shape:thematic-present |
| `pie-lex-sekwtlom` | sekʷtlom |  | shape:thematic-neuter |
| `pie-lex-selh1weh2` | selh₁weh₂ |  | shape:eh2 |
| `pie-lex-serpenos` | serpenos |  | shape:thematic |
| `pie-lex-serwos` | serwos |  | shape:thematic |
| `pie-lex-serwos-2` | serwos |  | shape:thematic |
| `pie-lex-sh1itos` | sh₁itos |  | shape:thematic |
| `pie-lex-sh1itros` | sh₁itros |  | shape:thematic |
| `pie-lex-skelHyom` | skelHyom |  | shape:thematic-neuter |
| `pie-lex-skereti` | skereti |  | shape:thematic-present |
| `pie-lex-skertsneh2` | skertsneh₂ | portion | shape:eh2 |
| `pie-lex-skewHlos` | skewHlos |  | shape:thematic |
| `pie-lex-skeydros` | skeydros |  | shape:thematic |
| `pie-lex-skeyeti` | skeyeti |  | shape:thematic-present |
| `pie-lex-skeytos` | skeytos |  | shape:thematic |
| `pie-lex-skibom` | skibom |  | shape:thematic-neuter |
| `pie-lex-skidos` | skidos |  | shape:thematic |
| `pie-lex-skndsleh2` | skn̥dsleh₂ |  | shape:eh2 |
| `pie-lex-skolHyeh2` | skolHyeh₂ |  | shape:eh2 |
| `pie-lex-skolh1os` | skolh₁os |  | shape:thematic |
| `pie-lex-skongos` | skongos |  | shape:thematic |
| `pie-lex-skorbhos` | skorbʰos |  | shape:thematic |
| `pie-lex-skoros` | skoros |  | shape:thematic |
| `pie-lex-skoros-2` | skoros |  | shape:thematic |
| `pie-lex-skowh1os` | skowh₁os |  | shape:thematic |
| `pie-lex-skoytom` | skoytom |  | shape:thematic-neuter |
| `pie-lex-skreynyom` | skreynyom |  | shape:thematic-neuter |
| `pie-lex-skreywos` | skreywos |  | shape:thematic |
| `pie-lex-skrobeh2` | skrobeh₂ |  | shape:eh2 |
| `pie-lex-skrtiHneh2` | skr̥tiHneh₂ |  | shape:eh2 |
| `pie-lex-skuHtyeh2` | skuHtyeh₂ |  | shape:eh2 |
| `pie-lex-sloh1gos` | sloh₁gos |  | shape:thematic |
| `pie-lex-slh1yeti` | sl̥h₁yeti |  | shape:thematic-present |
| `pie-lex-smelseh2` | smelseh₂ |  | shape:eh2 |
| `pie-lex-smelsos` | smelsos |  | shape:thematic |
| `pie-lex-smerimneh2` | smerimneh₂ |  | shape:eh2 |
| `pie-lex-smersmeros` | smersmeros |  | shape:thematic |
| `pie-lex-smesmros` | smesmros |  | shape:thematic |
| `pie-lex-smldom` | sml̥dom |  | shape:thematic-neuter |
| `pie-lex-smldos` | sml̥dos |  | shape:thematic |
| `pie-lex-smlsbheh2mos` | sml̥sbʰeh₂mos |  | shape:thematic |
| `pie-lex-smoh1los` | smoh₁los |  | shape:thematic |
| `pie-lex-smoldom` | smoldom |  | shape:thematic-neuter |
| `pie-lex-smrturos` | smr̥turos |  | shape:thematic |
| `pie-lex-smh2eros` | sm̥h₂eros |  | shape:thematic |
| `pie-lex-sneh1yeti` | sneh₁yeti |  | shape:thematic-present |
| `pie-lex-sntskjeti` | sn̥tsḱeti |  | shape:thematic-present |
| `pie-lex-sodyeh2` | sodyeh₂ |  | shape:eh2 |
| `pie-lex-sodyom` | sodyom | seat | shape:thematic-neuter |
| `pie-lex-solh2idhos` | solh₂idʰos |  | shape:thematic |
| `pie-lex-sorwom` | sorwom |  | shape:thematic-neuter |
| `pie-lex-spenh1neti` | spenh₁neti |  | shape:thematic-present |
| `pie-lex-spergjheti` | sperǵʰeti |  | shape:thematic-present |
| `pie-lex-speykeh2` | speykeh₂ |  | shape:eh2 |
| `pie-lex-speykomnos` | speykomnos |  | shape:thematic |
| `pie-lex-speyneh2` | speyneh₂ |  | shape:eh2 |
| `pie-lex-spoHymekos` | spoHymekos |  | shape:thematic |
| `pie-lex-spoHymos` | spoHymos |  | shape:thematic |
| `pie-lex-srewedhrom` | srewedʰrom |  | shape:thematic-neuter |
| `pie-lex-srowmeh2` | srowmeh₂ |  | shape:eh2 |
| `pie-lex-srowmos` | srowmos |  | shape:thematic |
| `pie-lex-srowtos` | srowtos |  | shape:thematic |
| `pie-lex-srowyeh2` | srowyeh₂ |  | shape:eh2 |
| `pie-lex-steh2ghos` | steh₂gʰos |  | shape:thematic |
| `pie-lex-steh2mos` | steh₂mos | fixing, settled state | shape:thematic |
| `pie-lex-steh2tleh2` | steh₂tleh₂ | heel | shape:eh2 |
| `pie-lex-stengwyeti` | stengʷyeti |  | shape:thematic-present |
| `pie-lex-sterbhos` | sterbʰos |  | shape:thematic |
| `pie-lex-sth2elom` | sth₂elom |  | shape:thematic-neuter |
| `pie-lex-sth2olom` | sth₂olom |  | shape:thematic-neuter |
| `pie-lex-stigeti` | stigeti |  | shape:thematic-present |
| `pie-lex-stih2yeh2` | stih₂yeh₂ |  | shape:eh2 |
| `pie-lex-stih2yom` | stih₂yom |  | shape:thematic-neuter |
| `pie-lex-stlkos` | stl̥kos |  | shape:thematic |
| `pie-lex-stlneh2` | stl̥neh₂ | pillar, gravestone | shape:eh2 |
| `pie-lex-stogeh2` | stogeh₂ |  | shape:eh2 |
| `pie-lex-stognos` | stognos |  | shape:thematic |
| `pie-lex-storbheyeti` | storbʰeyeti |  | shape:thematic-present |
| `pie-lex-stowrHos` | stowrHos |  | shape:thematic |
| `pie-lex-stoyh2neh2` | stoyh₂neh₂ |  | shape:eh2 |
| `pie-lex-stoyh2nos` | stoyh₂nos |  | shape:thematic |
| `pie-lex-strnghos` | strn̥gʰos |  | shape:thematic |
| `pie-lex-stronghos` | strongʰos |  | shape:thematic |
| `pie-lex-strowom` | strowom |  | shape:thematic-neuter |
| `pie-lex-stupos` | stupos |  | shape:thematic |
| `pie-lex-suh2ghos` | suh₂gʰos |  | shape:thematic |
| `pie-lex-swedhh1eh2` | swedʰh₁eh₂ |  | shape:eh2 |
| `pie-lex-sweh2dros` | sweh₂dros |  | shape:thematic |
| `pie-lex-swerwos` | swerwos |  | shape:thematic |
| `pie-lex-swopnos` | swopnos | sleep, dream | shape:thematic |
| `pie-lex-sworeh2` | sworeh₂ |  | shape:eh2 |
| `pie-lex-syuHeti` | syuHeti |  | shape:thematic-present |
| `pie-lex-sgjheti` | sǵʰeti |  | shape:thematic-present |
| `pie-lex-skjeh3iros` | sḱeh₃iros |  | shape:thematic |
| `pie-lex-tegdhleh2` | tegdʰleh₂ |  | shape:eh2 |
| `pie-lex-tegnom` | tegnom |  | shape:thematic-neuter |
| `pie-lex-tegslom` | tegslom |  | shape:thematic-neuter |
| `pie-lex-teh2dheti` | teh₂dʰeti |  | shape:thematic-present |
| `pie-lex-teh2eynos` | teh₂eynos |  | shape:thematic |
| `pie-lex-teh2yeti` | teh₂yeti |  | shape:thematic-present |
| `pie-lex-telketi` | telketi |  | shape:thematic-present |
| `pie-lex-temHseh2` | temHseh₂ |  | shape:eh2 |
| `pie-lex-temh1lom` | temh₁lom |  | shape:thematic-neuter |
| `pie-lex-tenghsleh2` | tengʰsleh₂ |  | shape:eh2 |
| `pie-lex-teplos` | teplos |  | shape:thematic |
| `pie-lex-terseh2` | terseh₂ | earth, land | shape:eh2 |
| `pie-lex-tetkjeh2` | tetḱeh₂ |  | shape:eh2 |
| `pie-lex-tetkjsneh2` | tetḱsneh₂ |  | shape:eh2 |
| `pie-lex-th2esyeh2` | th₂esyeh₂ |  | shape:eh2 |
| `pie-lex-tlokwetor` | tlokʷetor |  | shape:thematic-middle |
| `pie-lex-tlkskjos` | tl̥ksḱos |  | shape:thematic |
| `pie-lex-tlkwos` | tl̥kʷos |  | shape:thematic |
| `pie-lex-tmpeh2` | tm̥peh₂ |  | shape:eh2 |
| `pie-lex-tokwos` | tokʷos |  | shape:thematic |
| `pie-lex-tolh2eseh2yeti` | tolh₂eseh₂yeti |  | shape:thematic-present |
| `pie-lex-tolh2meh2` | tolh₂meh₂ |  | shape:eh2 |
| `pie-lex-tolh2os` | tolh₂os |  | shape:thematic |
| `pie-lex-tolkeh2` | tolkeh₂ |  | shape:eh2 |
| `pie-lex-tolkos` | tolkos |  | shape:thematic |
| `pie-lex-torkwmos` | torkʷmos |  | shape:thematic |
| `pie-lex-trebeh2` | trebeh₂ | homestead, dwelling | shape:eh2 |
| `pie-lex-trebnos` | trebnos | dwelling, arrangement | shape:thematic |
| `pie-lex-treh1skjeti` | treh₁sḱeti |  | shape:thematic-present |
| `pie-lex-trewdsos` | trewdsos |  | shape:thematic |
| `pie-lex-trewdtos` | trewdtos |  | shape:thematic |
| `pie-lex-treydhlom` | treydʰlom |  | shape:thematic-neuter |
| `pie-lex-trobeh2` | trobeh₂ |  | shape:eh2 |
| `pie-lex-trbom` | tr̥bom | village, farmstead | shape:thematic-neuter |
| `pie-lex-trseh1yeti` | tr̥seh₁yeti |  | shape:thematic-present |
| `pie-lex-tuh2edheh2` | tuh₂edʰeh₂ |  | shape:eh2 |
| `pie-lex-tuh2elos` | tuh₂elos |  | shape:thematic |
| `pie-lex-tuh2sneh2` | tuh₂sneh₂ |  | shape:eh2 |
| `pie-lex-tuh2teh2` | tuh₂teh₂ |  | shape:eh2 |
| `pie-lex-tumidos` | tumidos |  | shape:thematic |
| `pie-lex-turkjsos` | turḱsos |  | shape:thematic |
| `pie-lex-tworHos` | tworHos |  | shape:thematic |
| `pie-lex-tkjilos` | tḱilos |  | shape:thematic |
| `pie-lex-udsdhh1os` | udsdʰh₁os |  | shape:thematic |
| `pie-lex-uh2dhom` | uh₂dʰom | shallow water, ford | shape:thematic-neuter |
| `pie-lex-waylos` | waylos | wolf | table |
| `pie-lex-webhnyeti` | webʰnyeti |  | shape:thematic-present |
| `pie-lex-wedrom` | wedrom |  | shape:thematic-neuter |
| `pie-lex-wedhos` | wedʰos |  | shape:thematic |
| `pie-lex-weh1iros` | weh₁iros | turned, twisted | shape:thematic |
| `pie-lex-weh1reh2` | weh₁reh₂ |  | shape:eh2 |
| `pie-lex-weh1ros` | weh₁ros | true | table |
| `pie-lex-wendheh2` | wendʰeh₂ |  | shape:eh2 |
| `pie-lex-werdhom` | werdʰom | word | table |
| `pie-lex-wereh1yeti` | wereh₁yeti |  | shape:thematic-present |
| `pie-lex-werh1idheti` | werh₁idʰeti |  | shape:thematic-present |
| `pie-lex-wertenom` | wertenom |  | shape:thematic-neuter |
| `pie-lex-wertyeti` | wertyeti |  | shape:thematic-present |
| `pie-lex-weryeh2` | weryeh₂ |  | shape:eh2 |
| `pie-lex-wergjos` | werǵos |  | shape:thematic |
| `pie-lex-wetelos` | wetelos |  | shape:thematic-neuter-reflex |
| `pie-lex-wetusos` | wetusos |  | shape:thematic |
| `pie-lex-weydoh2lom` | weydoh₂lom |  | shape:thematic-neuter |
| `pie-lex-weyh1neh2` | weyh₁neh₂ |  | shape:eh2 |
| `pie-lex-weystleh2` | weystleh₂ |  | shape:eh2 |
| `pie-lex-weykjos` | weyḱos |  | shape:thematic |
| `pie-lex-wegjhnos` | weǵʰnos |  | shape:thematic |
| `pie-lex-wegjhos` | weǵʰos |  | shape:thematic |
| `pie-lex-wih1elos` | wih₁elos |  | shape:thematic |
| `pie-lex-wiwondhos` | wiwondʰos |  | shape:thematic |
| `pie-lex-wlikwos` | wlikʷos |  | shape:thematic |
| `pie-lex-wnh1trom` | wn̥h₁trom |  | shape:thematic-neuter |
| `pie-lex-wobhyom` | wobʰyom |  | shape:thematic-neuter |
| `pie-lex-wodheh2` | wodʰeh₂ |  | shape:eh2 |
| `pie-lex-wodhos` | wodʰos |  | shape:thematic |
| `pie-lex-wodhyom` | wodʰyom |  | shape:thematic-neuter |
| `pie-lex-wogwedhos` | wogʷedʰos |  | shape:thematic |
| `pie-lex-wogwos` | wogʷos |  | shape:thematic |
| `pie-lex-wokwyeh2` | wokʷyeh₂ |  | shape:eh2 |
| `pie-lex-wolh1os` | wolh₁os |  | shape:thematic |
| `pie-lex-wolh3os` | wolh₃os |  | shape:thematic |
| `pie-lex-womh1nos` | womh₁nos |  | shape:thematic |
| `pie-lex-worbhos` | worbʰos |  | shape:thematic |
| `pie-lex-woreh2` | woreh₂ |  | shape:eh2 |
| `pie-lex-woreh2yeti` | woreh₂yeti |  | shape:thematic-present |
| `pie-lex-worgos` | worgos |  | shape:thematic |
| `pie-lex-woros` | woros |  | shape:thematic |
| `pie-lex-woryos` | woryos |  | shape:thematic |
| `pie-lex-worgjhos` | worǵʰos |  | shape:thematic |
| `pie-lex-wogjheh2` | woǵʰeh₂ |  | shape:eh2 |
| `pie-lex-wogjhlos` | woǵʰlos |  | shape:thematic |
| `pie-lex-wogjhnos` | woǵʰnos |  | shape:thematic |
| `pie-lex-wreh1gjyeti` | wreh₁ǵyeti |  | shape:thematic-present |
| `pie-lex-wreyteh1yeti` | wreyteh₁yeti |  | shape:thematic-present |
| `pie-lex-wreykjeh2` | wreyḱeh₂ |  | shape:eh2 |
| `pie-lex-wreykjos` | wreyḱos |  | shape:thematic |
| `pie-lex-writeti` | writeti |  | shape:thematic-present |
| `pie-lex-wexdos` | wēdos | wet | shape:thematic-adj |
| `pie-lex-yemHnos` | yemHnos |  | shape:thematic |
| `pie-lex-yetkos` | yetkos |  | shape:thematic |
| `pie-lex-yugos` | yugos |  | shape:thematic |
| `pie-lex-gjenh1eseh2` | ǵenh₁eseh₂ | lineage, offspring | shape:eh2 |
| `pie-lex-gjh2reh2` | ǵh₂reh₂ |  | shape:eh2 |
| `pie-lex-gjneh3meh2` | ǵneh₃meh₂ | mark; mind, judgement, opinion | shape:eh2 |
| `pie-lex-gjnh1iwos` | ǵn̥h₁iwos |  | shape:thematic |
| `pie-lex-gjnh3yom` | ǵn̥h₃yom |  | shape:thematic-neuter |
| `pie-lex-gjorh2istos` | ǵorh₂istos |  | shape:thematic |
| `pie-lex-gjorh2os` | ǵorh₂os |  | shape:thematic |
| `pie-lex-gjowsteh2` | ǵowsteh₂ |  | shape:eh2 |
| `pie-lex-gjwlHom` | ǵwl̥Hom |  | shape:thematic-neuter |
| `pie-lex-gjwolHos` | ǵwolHos |  | shape:thematic |
| `pie-lex-gjyewh1neh2` | ǵyewh₁neh₂ |  | shape:eh2 |
| `pie-lex-gjheh1ros` | ǵʰeh₁ros | derelict, forsaken | shape:thematic-adj |
| `pie-lex-gjhelh3os` | ǵʰelh₃os |  | shape:thematic |
| `pie-lex-gjhenghyeti` | ǵʰengʰyeti |  | shape:thematic-present |
| `pie-lex-gjherHnieh2` | ǵʰerHnieh₂ |  | shape:eh2 |
| `pie-lex-gjherstos` | ǵʰerstos |  | shape:thematic |
| `pie-lex-gjheydhos` | ǵʰeydʰos |  | shape:thematic |
| `pie-lex-gjhleystos` | ǵʰleystos | shine, brightness | shape:thematic |
| `pie-lex-gjhlidmnyeti` | ǵʰlidmn̥yeti | to shine, sparkle | shape:thematic-present |
| `pie-lex-gjholh3tos` | ǵʰolh₃tos |  | shape:thematic |
| `pie-lex-gjhonghos` | ǵʰongʰos |  | shape:thematic |
| `pie-lex-gjhrHeh2` | ǵʰr̥Heh₂ |  | shape:eh2 |
| `pie-lex-gjhrHos` | ǵʰr̥Hos |  | shape:thematic |
| `pie-lex-gjhuHeh2` | ǵʰuHeh₂ |  | shape:eh2 |
| `pie-lex-gjhuHeti` | ǵʰuHeti |  | shape:thematic-present |
| `pie-lex-gjhulos` | ǵʰulos |  | shape:thematic |
| `pie-lex-gjhumos` | ǵʰumos |  | shape:thematic |
| `pie-lex-gjhweriHnos` | ǵʰweriHnos |  | shape:thematic |
| `pie-lex-kjeh1strom` | ḱeh₁strom |  | shape:thematic-neuter |
| `pie-lex-kjelmos` | ḱelmos |  | shape:thematic |
| `pie-lex-kjelneh2` | ḱelneh₂ |  | shape:eh2 |
| `pie-lex-kjerh2onowos` | ḱerh₂onowos | head nodding | shape:thematic |
| `pie-lex-kjerh2srom` | ḱerh₂srom |  | shape:thematic-neuter |
| `pie-lex-kjerh2wos` | ḱerh₂wos | the horned one | shape:thematic |
| `pie-lex-kjeyros` | ḱeyros | orphaned | shape:thematic |
| `pie-lex-kjh2dos` | ḱh₂dos |  | shape:s-stem-neuter |
| `pie-lex-kjlowsos` | ḱlowsos | hearing | shape:thematic |
| `pie-lex-kjlowsteh2` | ḱlowsteh₂ |  | shape:eh2 |
| `pie-lex-kjlyeti` | ḱl̥yeti |  | shape:thematic-present |
| `pie-lex-kjordom` | ḱordom |  | shape:thematic-neuter |
| `pie-lex-kjorkeh2` | ḱorkeh₂ | pebble, gravel, small stone | shape:eh2 |
| `pie-lex-kjorwos` | ḱorwos |  | shape:thematic |
| `pie-lex-kjoyteh2` | ḱoyteh₂ |  | shape:eh2 |
| `pie-lex-kjroh2snom` | ḱroh₂snom |  | shape:thematic-neuter |
| `pie-lex-kjseh1yeti` | ḱseh₁yeti |  | shape:thematic-present |
| `pie-lex-kjsewlos` | ḱsewlos |  | shape:thematic |
| `pie-lex-kjstrom` | ḱstrom |  | shape:thematic-neuter |
| `pie-lex-kjwentos` | ḱwentos |  | shape:thematic |

### no gloss: 162

Usable spec, but no gloss at all. Needs a dictionary gloss (overrides.jsonl `meaning`).

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-bakyeh2` | bakyéh₂ |  | shape:eh2 |
| `pie-lex-bhih2tros` | bʰih₂trós |  | shape:thematic |
| `pie-lex-bhndhyom` | bʰn̥dʰyóm |  | shape:thematic-neuter |
| `pie-lex-bhodhyom-2` | bʰodʰyóm |  | shape:thematic-neuter |
| `pie-lex-bhoyh2nom` | bʰoyh₂nóm |  | shape:thematic-neuter |
| `pie-lex-bhudhyetor` | bʰudʰyétor |  | shape:thematic-middle |
| `pie-lex-bheh2meh2` | bʰéh₂meh₂ |  | shape:eh2 |
| `pie-lex-bheyh2etor` | bʰéyh₂etor |  | shape:thematic-middle |
| `pie-lex-bhuHtlom` | bʰúHtlom |  | shape:thematic-neuter |
| `pie-lex-bhrmgos` | bʰŕ̥mgos |  | shape:thematic |
| `pie-lex-bhexdhetor` | bʰḗdʰetor |  | shape:thematic-middle |
| `pie-lex-dewkdhlos` | dewkdʰlós |  | shape:thematic |
| `pie-lex-dewkdhrom` | dewkdʰróm |  | shape:thematic-neuter |
| `pie-lex-dh2pnom` | dh₂pnóm |  | shape:thematic-neuter |
| `pie-lex-dh2pnneh2` | dh₂pn̥néh₂ |  | shape:eh2 |
| `pie-lex-dh2yetor` | dh₂yétor |  | shape:thematic-middle |
| `pie-lex-dekjweh2` | déḱweh₂ |  | shape:eh2 |
| `pie-lex-dokjseh2` | dóḱseh₂ |  | shape:eh2 |
| `pie-lex-dexkjweh2` | dēḱwéh₂ |  | shape:eh2 |
| `pie-lex-dhh1dhmos` | dʰh₁dʰmós |  | shape:thematic |
| `pie-lex-dhowHtos` | dʰowHtós |  | shape:thematic |
| `pie-lex-dhroghos` | dʰrogʰós |  | shape:thematic |
| `pie-lex-dhuHnos` | dʰuHnós |  | shape:thematic |
| `pie-lex-dmpedom` | dḿ̥pedom |  | shape:thematic-neuter |
| `pie-lex-gh2newti` | gh₂néwti |  | shape:athematic-root |
| `pie-lex-gh2wyeti` | gh₂wyéti |  | shape:thematic-present |
| `pie-lex-gleyHweh2` | gleyHwéh₂ |  | shape:eh2 |
| `pie-lex-gloyHtom` | glóyHtom |  | shape:thematic-neuter |
| `pie-lex-ghostigwhowos` | gʰostigʷʰowós |  | shape:thematic |
| `pie-lex-gwrh3tlom` | gʷr̥h₃tlóm |  | shape:thematic-neuter |
| `pie-lex-gwerh3tlom` | gʷérh₃tlom |  | shape:thematic-neuter |
| `pie-lex-h1elusos` | h₁elusós |  | shape:thematic |
| `pie-lex-h1grskjetor` | h₁gr̥sḱétor |  | shape:thematic-middle |
| `pie-lex-h1geretor` | h₁géretor |  | shape:thematic-middle |
| `pie-lex-h1rebhrom` | h₁rebʰróm |  | shape:thematic-neuter |
| `pie-lex-h1rebhyom` | h₁rebʰyóm |  | shape:thematic-neuter |
| `pie-lex-h1regwti` | h₁régʷti |  | shape:athematic-root |
| `pie-lex-h1rgwntos` | h₁r̥gʷn̥tós |  | shape:thematic |
| `pie-lex-h1uHtos` | h₁uHtós |  | shape:thematic |
| `pie-lex-h1elnbhos` | h₁éln̥bʰos |  | shape:thematic |
| `pie-lex-h1erh1tlom` | h₁érh₁tlom |  | shape:thematic-neuter |
| `pie-lex-h1ewHeti` | h₁éwHeti |  | shape:thematic-present |
| `pie-lex-h1ih1ewHeti` | h₁íh₁ewHeti |  | shape:thematic-present |
| `pie-lex-h1exwst` | h₁ḗwst |  | shape:s-aorist |
| `pie-lex-h2dtos` | h₂dtós |  | shape:thematic |
| `pie-lex-h2eydhexr` | h₂eydʰḗr |  | shape:er-stem |
| `pie-lex-h2poh2orkeyeti` | h₂poh₂orkéyeti |  | shape:thematic-present |
| `pie-lex-h2poh2erketi` | h₂poh₂érketi |  | shape:thematic-present |
| `pie-lex-h2sutmeh2` | h₂sutméh₂ |  | shape:eh2 |
| `pie-lex-h2welh1nos` | h₂wélh₁nos |  | shape:thematic |
| `pie-lex-h2enh1tlom` | h₂énh₁tlom |  | shape:thematic-neuter |
| `pie-lex-h2eph3ox` | h₂éph₃ō |  | shape:n-stem-ak |
| `pie-lex-h2erdhrom` | h₂érdʰrom |  | shape:thematic-neuter |
| `pie-lex-h2erh1isox` | h₂érh₁isō |  | shape:n-stem-ak |
| `pie-lex-h2erti` | h₂érti |  | shape:athematic-root |
| `pie-lex-h3kwyetor` | h₃kʷyétor |  | shape:thematic-middle |
| `pie-lex-h3mighleh2-2` | h₃migʰleh₂ |  | shape:eh2 |
| `pie-lex-h3rewnos` | h₃réwnos |  | shape:thematic |
| `pie-lex-h3reyHdheti-2` | h₃réyHdʰeti |  | shape:thematic-present |
| `pie-lex-h3ekwsetor` | h₃ékʷsetor |  | shape:thematic-middle |
| `pie-lex-h3eplom` | h₃éplom |  | shape:thematic-neuter |
| `pie-lex-kaghnom` | kagʰnóm |  | shape:thematic-neuter |
| `pie-lex-kesrom` | kesróm |  | shape:thematic-neuter |
| `pie-lex-ksownom` | ksównom |  | shape:thematic-neuter |
| `pie-lex-kaghsos` | kágʰsos |  | shape:thematic |
| `pie-lex-keh2ntlom` | kéh₂ntlom |  | shape:thematic-neuter |
| `pie-lex-kwolpeyeti` | kʷolpéyeti |  | shape:thematic-present |
| `pie-lex-kwolpos` | kʷolpós |  | shape:thematic |
| `pie-lex-kwoywos` | kʷoywós |  | shape:thematic |
| `pie-lex-kwelpeti` | kʷélpeti |  | shape:thematic-present |
| `pie-lex-kwoyos` | kʷóyos |  | shape:thematic |
| `pie-lex-kwoyseh2` | kʷóyseh₂ |  | shape:eh2 |
| `pie-lex-lugjros` | luǵrós |  | shape:thematic |
| `pie-lex-leseti` | léseti |  | shape:thematic-present |
| `pie-lex-lewketor` | léwketor |  | shape:thematic-middle |
| `pie-lex-lewksos` | léwksos |  | shape:thematic |
| `pie-lex-lokus` | lókus |  | shape:pk-iu-stem |
| `pie-lex-londhrom` | lóndʰrom |  | shape:thematic-neuter |
| `pie-lex-lbrom` | l̥bróm |  | shape:thematic-neuter |
| `pie-lex-lbyom` | l̥byóm |  | shape:thematic-neuter |
| `pie-lex-mneh2yetor` | mnéh₂yetor |  | shape:thematic-middle |
| `pie-lex-mukyetor` | mukyétor |  | shape:thematic-middle |
| `pie-lex-meh3tus` | méh₃tus |  | shape:pk-iu-stem |
| `pie-lex-meyetor` | méyetor |  | shape:thematic-middle |
| `pie-lex-ninsetor` | ninsétor |  | shape:thematic-middle |
| `pie-lex-pelnom` | pelnóm |  | shape:thematic-neuter |
| `pie-lex-pleh3utom` | pleh₃utóm |  | shape:thematic-neuter |
| `pie-lex-plowtom` | plowtóm |  | shape:thematic-neuter |
| `pie-lex-plexnyeh2` | plēnyéh₂ |  | shape:eh2 |
| `pie-lex-plh1yetor` | pl̥h₁yétor |  | shape:thematic-middle |
| `pie-lex-pntstos` | pn̥tstós |  | shape:thematic |
| `pie-lex-prewetor` | préwetor |  | shape:thematic-middle |
| `pie-lex-prdkeh2` | pr̥dkéh₂ |  | shape:eh2 |
| `pie-lex-prh3sos` | pr̥h₃sós |  | shape:thematic |
| `pie-lex-pugjmeh2` | puǵméh₂ |  | shape:eh2 |
| `pie-lex-peh3tlom` | péh₃tlom |  | shape:thematic-neuter |
| `pie-lex-pelskjos` | pélsḱos |  | shape:thematic |
| `pie-lex-porkjonos` | pórḱonos |  | shape:thematic |
| `pie-lex-sekyom` | sekyóm |  | shape:thematic-neuter |
| `pie-lex-sewh1yeh2` | sewh₁yéh₂ |  | shape:eh2 |
| `pie-lex-skuHtom` | skuHtóm |  | shape:thematic-neuter |
| `pie-lex-slyetor` | sl̥yétor |  | shape:thematic-middle |
| `pie-lex-smrtos` | smr̥tós |  | shape:thematic |
| `pie-lex-smHtlom` | sm̥Htlóm |  | shape:thematic-neuter |
| `pie-lex-smlom` | sm̥lóm |  | shape:thematic-neuter |
| `pie-lex-sormeh2` | sorméh₂ |  | shape:eh2 |
| `pie-lex-spHoymnos` | spHóymnos |  | shape:thematic |
| `pie-lex-spenh1etor` | spénh₁etor |  | shape:thematic-middle |
| `pie-lex-spekjtlom` | spéḱtlom |  | shape:thematic-neuter |
| `pie-lex-srudhmos` | srudʰmós |  | shape:thematic |
| `pie-lex-srutom` | srutóm |  | shape:thematic-neuter |
| `pie-lex-stebhlom` | stebʰlóm |  | shape:thematic-neuter |
| `pie-lex-sth2weh2` | sth₂wéh₂ |  | shape:eh2 |
| `pie-lex-steygetor` | stéygetor |  | shape:thematic-middle |
| `pie-lex-stigheh2` | stígʰeh₂ |  | shape:eh2 |
| `pie-lex-stighom` | stígʰom |  | shape:thematic-neuter |
| `pie-lex-stighos` | stígʰos |  | shape:thematic |
| `pie-lex-sedtlom` | sédtlom |  | shape:thematic-neuter |
| `pie-lex-seknom` | séknom |  | shape:thematic-neuter |
| `pie-lex-sekskeh2` | sékskeh₂ |  | shape:eh2 |
| `pie-lex-sektleh2` | séktleh₂ |  | shape:eh2 |
| `pie-lex-tewh2tyos` | tewh₂tyós |  | shape:thematic |
| `pie-lex-tnh1yetor` | tn̥h₁yétor |  | shape:thematic-middle |
| `pie-lex-trmeh1yeti` | tr̥méh₁yeti |  | shape:thematic-present |
| `pie-lex-tweryeh2` | tweryéh₂ |  | shape:eh2 |
| `pie-lex-tyegwetor` | tyégʷetor |  | shape:thematic-middle |
| `pie-lex-teh2gslos` | téh₂gslos |  | shape:thematic |
| `pie-lex-teh2gyus` | téh₂gyus |  | shape:pk-iu-stem |
| `pie-lex-tentlom` | téntlom |  | shape:thematic-neuter |
| `pie-lex-terh1dhrom` | térh₁dʰrom |  | shape:thematic-neuter |
| `pie-lex-tersetor` | térsetor |  | shape:thematic-middle |
| `pie-lex-tekjnom` | téḱnom |  | shape:thematic-neuter |
| `pie-lex-torkwtom` | tórkʷtom |  | shape:thematic-neuter |
| `pie-lex-ukwtHom` | ukʷtHóm |  | shape:thematic-neuter |
| `pie-lex-usHnos` | usHnós |  | shape:thematic |
| `pie-lex-utsos` | utsós |  | shape:thematic |
| `pie-lex-wergjhnom` | werǵʰnóm |  | shape:thematic-neuter |
| `pie-lex-wergjhslom` | werǵʰslóm |  | shape:thematic-neuter |
| `pie-lex-wegjhyom` | weǵʰyóm |  | shape:thematic-neuter |
| `pie-lex-wegjhitlom` | weǵʰítlom |  | shape:thematic-neuter |
| `pie-lex-wigetor` | wigétor |  | shape:thematic-middle |
| `pie-lex-wokwtlom` | wokʷtlóm |  | shape:thematic-neuter |
| `pie-lex-woygeyeti` | woygéyeti |  | shape:thematic-present |
| `pie-lex-wesnnos` | wésn̥nos |  | shape:thematic |
| `pie-lex-wetrus` | wétrus |  | shape:pk-iu-stem |
| `pie-lex-woygos` | wóygos |  | shape:thematic |
| `pie-lex-woyh1meh2` | wóyh₁meh₂ |  | shape:eh2 |
| `pie-lex-wogjos` | wóǵos |  | shape:thematic |
| `pie-lex-yeh2tom` | yeh₂tóm |  | shape:thematic-neuter |
| `pie-lex-nstom` | ń̥stom |  | shape:thematic-neuter |
| `pie-lex-gjusetor` | ǵusétor |  | shape:thematic-middle |
| `pie-lex-gjhewyom` | ǵʰewyóm |  | shape:thematic-neuter |
| `pie-lex-gjhlh3enyom` | ǵʰl̥h₃enyóm |  | shape:thematic-neuter |
| `pie-lex-gjhoryom` | ǵʰóryom |  | shape:thematic-neuter |
| `pie-lex-kjleh1wom` | ḱleh₁wóm |  | shape:thematic-neuter |
| `pie-lex-kjlewetos` | ḱlewetós |  | shape:thematic |
| `pie-lex-kjlitom` | ḱlitóm |  | shape:thematic-neuter |
| `pie-lex-kjmh2yetor` | ḱm̥h₂yétor |  | shape:thematic-middle |
| `pie-lex-kjuh1ryos` | ḱuh₁ryós |  | shape:thematic |
| `pie-lex-kjweytetor` | ḱwéytetor |  | shape:thematic-middle |
| `pie-lex-kjweytoxr` | ḱwéytōr |  | shape:tor-agent |
| `pie-lex-kjenketor` | ḱénketor |  | shape:thematic-middle |

### unknown:noun-shape, glossed: 94 (of 823)

Glossed nouns with no shape rule: each needs a checked spec (overrides.jsonl `spec` + `spec_checked`, as for ox, salt and fox).

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-Hyoh1r` | Hyóh₁r̥ | year, summer | unknown:noun-shape |
| `pie-lex-Hisus` | Hísus | arrow | unknown:noun-shape |
| `pie-lex-bhengjhyoxs` | bʰénǵʰyōs | thicker | unknown:noun-shape |
| `pie-lex-bhoh2gs` | bʰóh₂gs | allotment | unknown:noun-shape |
| `pie-lex-bhexdht` | bʰḗdʰt | to press | unknown:noun-shape |
| `pie-lex-drkjh2ekjru` | dr̥ḱh₂eḱru | eye-sharp/bitter | unknown:noun-shape |
| `pie-lex-derkjs` | dérḱs | eye | unknown:noun-shape |
| `pie-lex-dhwexs` | dʰwḗs | breath; soul | unknown:noun-shape |
| `pie-lex-dhedhh1i` | dʰédʰh₁i | milk curd | unknown:noun-shape |
| `pie-lex-gerh2oxws` | gerh₂ōws | crane (bird) | unknown:noun-shape |
| `pie-lex-gloyHtn` | glóyHtn̥ | slime, glue | unknown:noun-shape |
| `pie-lex-gowr` | gówr̥ | curl | unknown:noun-shape |
| `pie-lex-ghebhl` | gʰébʰl̥ | head | unknown:noun-shape |
| `pie-lex-gwhnteys` | gʷʰn̥téys | striking, beating | unknown:noun-shape |
| `pie-lex-h1lewdhis-2` | h₁lewdʰis | people | unknown:noun-shape |
| `pie-lex-h1weydhh1us-2` | h₁weydʰh₁us | wild | unknown:noun-shape |
| `pie-lex-h1widhh1us` | h₁widʰh₁us | wood | unknown:noun-shape |
| `pie-lex-h1widhh1ewh2` | h₁widʰh₁éwh₂ | widow | unknown:noun-shape |
| `pie-lex-h1yagjtoxr` | h₁yaǵtōr | one who worships, worshipper | unknown:noun-shape |
| `pie-lex-h1yenh2texr` | h₁yénh₂tēr | husband's brother's wife, co-sister-in-law | unknown:noun-shape |
| `pie-lex-h1eh1tr` | h₁éh₁tr̥ | some internal organ | unknown:noun-shape |
| `pie-lex-h1elem` | h₁élem | mountain elm | unknown:noun-shape |
| `pie-lex-h1eytr` | h₁éytr̥ | way, course | unknown:noun-shape |
| `pie-lex-h2elks` | h₂elks | sacred place, sanctuary; idol | unknown:noun-shape |
| `pie-lex-h2emsus-2` | h₂emsus | king, lord | unknown:noun-shape |
| `pie-lex-h2ekjru-2` | h₂eḱru | tear (of the eyes) | unknown:noun-shape |
| `pie-lex-h2uksexn` | h₂uksḗn | bull | unknown:noun-shape |
| `pie-lex-h2weydr` | h₂wéydr̥ | living creature, wild animal | unknown:noun-shape |
| `pie-lex-h2wostu` | h₂wóstu | home, dwelling | unknown:noun-shape |
| `pie-lex-h2erh3wr` | h₂érh₃wr̥ | ploughed land | unknown:noun-shape |
| `pie-lex-h2ekjonts` | h₂éḱonts | javelin | unknown:noun-shape |
| `pie-lex-h3donts` | h₃dónts | tooth | unknown:noun-shape |
| `pie-lex-h3edhexs` | h₃edʰḗs | adze | unknown:noun-shape |
| `pie-lex-krets` | kréts | strength | unknown:noun-shape |
| `pie-lex-kretyoxs` | krétyōs | strong; better | unknown:noun-shape |
| `pie-lex-krewh2s` | kréwh₂s | blood | unknown:noun-shape |
| `pie-lex-kaghr` | kágʰr̥ | enclosure | unknown:noun-shape |
| `pie-lex-koyts` | kóyts | brightness | unknown:noun-shape |
| `pie-lex-minuyoxs` | minuyṓs | smaller, less | unknown:noun-shape |
| `pie-lex-minoxs` | minṓs | smaller, less | unknown:noun-shape |
| `pie-lex-mregjhyoxs` | mréǵʰyōs | shorter | unknown:noun-shape |
| `pie-lex-mexh1ns` | mḗh₁n̥s | moon | unknown:noun-shape |
| `pie-lex-newyoxs` | néwyōs | newer | unknown:noun-shape |
| `pie-lex-nekjs` | néḱs | death | unknown:noun-shape |
| `pie-lex-nogwts` | nógʷts | night | unknown:noun-shape |
| `pie-lex-nyugs` | n̥yúgs | unjoined | unknown:noun-shape |
| `pie-lex-pedtus` | pedtus | falling, going down | unknown:noun-shape |
| `pie-lex-pedyoxs` | pedyōs | worse | unknown:noun-shape |
| `pie-lex-pih2dses` | pih₂dsés | pitch, resin | unknown:noun-shape |
| `pie-lex-pnkwstis` | pn̥kʷstis | fist | unknown:noun-shape |
| `pie-lex-probhHus` | probʰHus | good, excellent | unknown:noun-shape |
| `pie-lex-preh2i` | préh₂i | before | unknown:noun-shape |
| `pie-lex-per-2` | pér | through | unknown:noun-shape |
| `pie-lex-skabhtis` | skabʰtis | digging | unknown:noun-shape |
| `pie-lex-skobhis` | skobʰis | filings, sawdust | unknown:noun-shape |
| `pie-lex-skabhmn` | skábʰmn̥ | ditch, trench | unknown:noun-shape |
| `pie-lex-smeh2r` | sméh₂r̥ | hand | unknown:noun-shape |
| `pie-lex-smokjwr` | smóḱwr̥ | beard; chin | unknown:noun-shape |
| `pie-lex-smkrt` | sm̥kŕ̥t | one time | unknown:noun-shape |
| `pie-lex-sneHtr` | snéHtr̥ | adder (type of snake) | unknown:noun-shape |
| `pie-lex-sokwh2oxy` | sokʷh₂ṓy | follower in one's retinue | unknown:noun-shape |
| `pie-lex-solh2oh3kws` | solh₂oh₃kʷs | appearing whole | unknown:noun-shape |
| `pie-lex-speh1s` | spéh₁s | prosperity | unknown:noun-shape |
| `pie-lex-sraxps` | srā́ps | turnip, rape, cabbage | unknown:noun-shape |
| `pie-lex-sterih2s` | steríh₂s | sterile cow, heifer | unknown:noun-shape |
| `pie-lex-steyghs` | stéygʰs | path | unknown:noun-shape |
| `pie-lex-swekjruh2` | sweḱrúh₂ | mother-in-law | unknown:noun-shape |
| `pie-lex-swordoworis` | swordoworis | black water | unknown:noun-shape |
| `pie-lex-swe-2` | swé | self (reflexive pronoun) | unknown:noun-shape |
| `pie-lex-swopr` | swópr̥ | sleep, dream | unknown:noun-shape |
| `pie-lex-swops` | swóps | sleep | unknown:noun-shape |
| `pie-lex-so` | só | this | unknown:noun-shape |
| `pie-lex-suHs` | súHs | sow > pig | unknown:noun-shape |
| `pie-lex-soxdus` | sōdus | plant, garden | unknown:noun-shape |
| `pie-lex-tepents` | tepents | hot | unknown:noun-shape |
| `pie-lex-trbs` | tr̥bs | beam | unknown:noun-shape |
| `pie-lex-tuh2` | túh₂ | second-person singular pronoun: you | unknown:noun-shape |
| `pie-lex-widris` | widris | knowing, wise | unknown:noun-shape |
| `pie-lex-widtres` | widtrés | viewer, witness | unknown:noun-shape |
| `pie-lex-wrmis` | wr̥mis | worm | unknown:noun-shape |
| `pie-lex-wey` | wéy | we (more than two) | unknown:noun-shape |
| `pie-lex-weyh1s` | wéyh₁s | force, strength | unknown:noun-shape |
| `pie-lex-wexs` | wēs | pasture | unknown:noun-shape |
| `pie-lex-yoh1r-2` | yóh₁r̥ | year, season | unknown:noun-shape |
| `pie-lex-yoh1r-3` | yóh₁r̥ | year, season | unknown:noun-shape |
| `pie-lex-yuHs` | yúHs | you (plural) | unknown:noun-shape |
| `pie-lex-atta` | átta | father | unknown:noun-shape |
| `pie-lex-egjh2` | éǵh₂ | I (first-person pronoun) | unknown:noun-shape |
| `pie-lex-gjlh2oxws` | ǵl̥h₂ōws | sister-in-law (husband's sister) | unknown:noun-shape |
| `pie-lex-gjhlidmn` | ǵʰlidmn̥ | shine | unknown:noun-shape |
| `pie-lex-gjhesr` | ǵʰésr̥ | hand | unknown:noun-shape |
| `pie-lex-kjlutis` | ḱlutis | hearing | unknown:noun-shape |
| `pie-lex-kjelh2m` | ḱélh₂m̥ | straw | unknown:noun-shape |
| `pie-lex-kjokwr` | ḱókʷr̥ | dung, excrement, faeces | unknown:noun-shape |

### bound-stem (form with a hyphen), glossed: 113 (of 797)

Glossed roots and stems (louse lewH-, bee bʰey-, nit -níd-). Each needs a handbook citation form before it can take a spec.

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-kwe` | -kʷe | and | indeclinable |
| `pie-lex-kwe-2` | -kʷe | generalizing particle | indeclinable |
| `pie-lex-nid` | -níd- | nit, louse egg | unknown |
| `pie-lex-we` | -we | or | indeclinable |
| `pie-lex-Heh3ley` | Heh₃ley- | bend, joint; limb, member, arm | unknown |
| `pie-lex-HrewdH` | HrewdH- | to weep | unknown |
| `pie-lex-boli` | boli- | strength | unknown |
| `pie-lex-bhendh` | bʰendʰ- | to bind, tie | unknown |
| `pie-lex-bherno` | bʰerno- | heap; child, youth | unknown |
| `pie-lex-bhey` | bʰey- | bee | unknown |
| `pie-lex-bhleh1` | bʰleh₁- | to bleat; to cry | unknown |
| `pie-lex-bholHik` | bʰolHik- | coot, waterfowl | unknown |
| `pie-lex-bhormo` | bʰormo- | basket; lap | unknown |
| `pie-lex-bhors` | bʰors- | spike, prickle | unknown |
| `pie-lex-bhugj` | bʰuǵ- | buck, he-goat | unknown |
| `pie-lex-deh2i` | deh₂i- | to share, divide | unknown |
| `pie-lex-deh2p` | deh₂p- | to sacrifice; to lose | unknown |
| `pie-lex-dyewgwlh2eno` | dyewgʷl̥h₂eno- | divine acorn | unknown |
| `pie-lex-dhembh` | dʰembʰ- | to strike, stun; to be stunned | unknown |
| `pie-lex-dhers` | dʰers- | to be bold | unknown |
| `pie-lex-dhergjh` | dʰerǵʰ- | strong, robust | unknown |
| `pie-lex-dhgwhey` | dʰgʷʰey- | to decline, perish | unknown |
| `pie-lex-dhworo` | dʰworo- | door, gate; courtyard | unknown |
| `pie-lex-gewd` | gewd- | bag, stomach | unknown |
| `pie-lex-gewl` | gewl- | vessel, cub | unknown |
| `pie-lex-gewp` | gewp- | round object, knoll; cavity | unknown |
| `pie-lex-gewt` | gewt- | pouch, sack | unknown |
| `pie-lex-gwlHeH` | gʷl̥HeH- | to drip > to collapse, be weary | unknown |
| `pie-lex-h1egjh-2` | h₁eǵʰ- | hedgehog | unknown |
| `pie-lex-h1op` | h₁op- | to desire | unknown |
| `pie-lex-h1enih3kwo` | h₁énih₃kʷo- | face | unknown |
| `pie-lex-h2eHsh2-2` | h₂eHsh₂- | hearth, fireplace | unknown |
| `pie-lex-h2eh1ter` | h₂eh₁ter- | fire | unknown |
| `pie-lex-h2en` | h₂en- | on, onto | indeclinable |
| `pie-lex-h2eygj` | h₂eyǵ- | oak | unknown |
| `pie-lex-h2egjino` | h₂eǵino- | of a goat; goat-skin | unknown |
| `pie-lex-h2egjro` | h₂eǵro- | hunt, slaughter | unknown |
| `pie-lex-h2egjh` | h₂eǵʰ- | cow | unknown |
| `pie-lex-h2ekjs` | h₂eḱs- | axle, axis | unknown |
| `pie-lex-h2ekju` | h₂eḱu- | sharp; needle | unknown |
| `pie-lex-h2ogjnyo` | h₂oǵn̥yo- | what is driven | unknown |
| `pie-lex-h2reh1dh` | h₂reh₁dʰ- | to think; to arrange | unknown |
| `pie-lex-h2rey` | h₂rey- | to count; to arrange | unknown |
| `pie-lex-h2elis` | h₂élis- | alder | unknown |
| `pie-lex-h3dont` | h₃dónt- | *biting; tooth | unknown |
| `pie-lex-h3ewes` | h₃ewes- | covering, clothing | unknown |
| `pie-lex-h3nexbho` | h₃nēbʰo- | wheel | unknown |
| `pie-lex-h3olh1eye` | h₃olh₁éye- | to bring down | unknown |
| `pie-lex-kekoh2n` | kekoh₂n- | stork | unknown |
| `pie-lex-kokjs` | koḱs- | joint | unknown |
| `pie-lex-ksnewo` | ksnéwo- | scraping | unknown |
| `pie-lex-kwsewd` | kʷsewd- | to crush into pieces, disintegrate | unknown |
| `pie-lex-lHustro` | lHustro- | dirty place | unknown |
| `pie-lex-lHuto` | lHuto- | dirt | unknown |
| `pie-lex-lewH` | lewH- | louse | unknown |
| `pie-lex-lewto` | lewto- | mud, dirt | unknown |
| `pie-lex-loykwn` | lóykʷn- | inheritance, property left; lent land | unknown |
| `pie-lex-meh1lo` | meh₁lo- | measurement, time | unknown |
| `pie-lex-meldhn` | meldʰn- | lightning | unknown |
| `pie-lex-mewHdh` | mewHdʰ- | to complain or care about something | unknown |
| `pie-lex-meyo` | meyo- | change, movement | unknown |
| `pie-lex-mon` | mon- | man, human being | unknown |
| `pie-lex-morbhh2o` | morbʰh₂o- | looking like death? | unknown |
| `pie-lex-mus` | mus- | a fly (insect) | unknown |
| `pie-lex-moro` | móro- | death, pestilence | unknown |
| `pie-lex-nih3kw` | níh₃kʷ- | looking down | unknown |
| `pie-lex-nh1dti` | n̥h₁dti- | having no eating | unknown |
| `pie-lex-peh2tro` | peh₂tro- | guarder, protector, keeper | unknown |
| `pie-lex-proh2wryh2` | próh₂wr̥yh₂- | forepart (of a ship) | unknown |
| `pie-lex-prh3o` | pr̥h₃o- | providing | unknown |
| `pie-lex-sedlo` | sedlo- | seat | unknown |
| `pie-lex-sedti` | sedti- | sitting | unknown |
| `pie-lex-skerdh` | skerdʰ- | herd | unknown |
| `pie-lex-smmo` | sm̥mo- | some, any | unknown |
| `pie-lex-soplo` | soplo- | instrument | unknown |
| `pie-lex-steh2lo` | steh₂lo- | seat, stand | unknown |
| `pie-lex-stenh2` | stenh₂- | to thunder | unknown |
| `pie-lex-steryo` | steryo- | sterile | unknown |
| `pie-lex-stlto` | stl̥to- | foolish | unknown |
| `pie-lex-strew` | strew- | to spread, strew | unknown |
| `pie-lex-stegwhe` | stégʷʰe- | thematic present | unknown |
| `pie-lex-stegwhs` | stégʷʰs- | s-aorist | unknown |
| `pie-lex-syuHdhlo` | syuHdʰlo- | awl | unknown |
| `pie-lex-tata` | tata- | dad, father | unknown |
| `pie-lex-teh2bheh1` | teh₂bʰeh₁- | to be melting | unknown |
| `pie-lex-teh2k` | teh₂k- | to melt | unknown |
| `pie-lex-teh2w` | teh₂w- | to melt | unknown |
| `pie-lex-temh1d` | temh₁d- | to split, cut off | unknown |
| `pie-lex-temp` | temp- | to stretch, exert an effort on | unknown |
| `pie-lex-tend` | tend- | to stretch, extend | unknown |
| `pie-lex-tengh` | tengʰ- | to pull | unknown |
| `pie-lex-tenh2` | tenh₂- | to stretch, extend | unknown |
| `pie-lex-tens` | tens- | to stretch | unknown |
| `pie-lex-tetkjdhlo` | tetḱdʰlo- | adze | unknown |
| `pie-lex-tewh2s` | tewh₂s- | swelling | unknown |
| `pie-lex-tuHsont` | tuHsont- | thousand | indeclinable |
| `pie-lex-tuh2bh` | tuh₂bʰ- | hump, bump | unknown |
| `pie-lex-wern` | wern- | a kind of tree, perhaps alder | unknown |
| `pie-lex-wesli` | wesli- | sellable | unknown |
| `pie-lex-weykjs` | weyḱs- | mistletoe | unknown |
| `pie-lex-wormiHk` | wormiHk- | ant | unknown |
| `pie-lex-worno` | worno- | black bird; raven; crow | unknown |
| `pie-lex-wrsu` | wr̥su- | top, summit | unknown |
| `pie-lex-yewgter` | yewgtér- | harnesser, joiner | unknown |
| `pie-lex-yeh2lo` | yéh₂lo- | zeal | unknown |
| `pie-lex-gjelu` | ǵelu- | leech | unknown |
| `pie-lex-gjneh3no` | ǵneh₃no- | known; knowledge | unknown |
| `pie-lex-gjneh3os` | ǵneh₃os- | close kinsman | unknown |
| `pie-lex-gjnubhedh` | ǵnubʰedʰ- | to bend the knee, kneel (in reverence), pray? | unknown |
| `pie-lex-gjherdh` | ǵʰerdʰ- | to enclose | unknown |
| `pie-lex-gjhewd` | ǵʰewd- | to pour | unknown |
| `pie-lex-gjhreh3d` | ǵʰreh₃d- | hail | unknown |
| `pie-lex-kjlewmnto` | ḱléwmn̥to- | fame | unknown |

### backtest-fail:shape:devi, glossed: 7 (of 47)

Glossed devī nouns: a checked spec each.

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-bheydhih2` | bʰéydʰih₂ | obedience | shape:devi |
| `pie-lex-h2weksih2` | h₂weksíh₂ | flame | shape:devi |
| `pie-lex-h2ekjih2` | h₂éḱih₂ | point, sharpness, edge | shape:devi |
| `pie-lex-seykwenih2` | seykʷénih₂ | she who pours | shape:devi |
| `pie-lex-sih2` | síh₂ | she | shape:devi |
| `pie-lex-skjeh3ih2` | sḱeh₃ih₂ | shadow, shade | shape:devi |
| `pie-lex-gjenh1trih2` | ǵénh₁trih₂ | mother | shape:devi |

### backtest-fail:shape:hk-iu-stem, glossed: 14 (of 47)

Glossed hysterokinetic i/u-stems: a checked spec each.

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-Hreh1is` | Hreh₁ís | wealth, goods | shape:hk-iu-stem |
| `pie-lex-bheh2nus` | bʰeh₂nús | ray of light | shape:hk-iu-stem |
| `pie-lex-bhndhtus` | bʰn̥dʰtús | bond, agreement, custom | shape:hk-iu-stem |
| `pie-lex-h2ewis-2` | h₂ewís | manifest, apparent, evident | shape:hk-iu-stem |
| `pie-lex-h2weh1yus` | h₂weh₁yús | wind | shape:hk-iu-stem |
| `pie-lex-h2oxgjis` | h₂ōǵís | race, contest | shape:hk-iu-stem |
| `pie-lex-kwis` | kʷís | which, what | shape:hk-iu-stem |
| `pie-lex-kwis-2` | kʷís | who, what (interrogative) | shape:hk-iu-stem |
| `pie-lex-morwis` | morwís | ant | shape:hk-iu-stem |
| `pie-lex-pedh2tis` | pedh₂tís | foot soldier | shape:hk-iu-stem |
| `pie-lex-wlHmis` | wl̥Hmís | wave | shape:hk-iu-stem |
| `pie-lex-is-2` | ís | this, he (used as the 3rd person pronoun) | shape:hk-iu-stem |
| `pie-lex-kjlustis` | ḱlustís | obedience; hearing | shape:hk-iu-stem |
| `pie-lex-kjis` | ḱís | this (here) | shape:hk-iu-stem |

### backtest-fail:shape:n-stem-hk, glossed: 2 (of 9)

Glossed hysterokinetic n-stems: a checked spec each.

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-h2ewgmox` | h₂ewgmṓ | something that grows | shape:n-stem-hk |
| `pie-lex-gjhmox` | ǵʰmṓ | human (cf. Earthling) | shape:n-stem-hk |

### unknown:athematic-no-ablaut, glossed: 1 (of 44)

Glossed athematic verbs whose stem has no e/o to ablaut (Narten ḗ, nasal infix): a checked spec each.

| id | form | gloss | rule |
|---|---|---|---|
| `pie-lex-stisteh2ti` | stísteh₂ti | to be standing up, to be getting up | unknown:athematic-no-ablaut |

