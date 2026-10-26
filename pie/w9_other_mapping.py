"""Word-coordinate readings independently reviewed in the wave 9 ledger."""
import json
from pathlib import Path

ROWS = json.loads((Path(__file__).resolve().parents[1] /
                   'data/research/formulas/w9-other-readings.json').read_text())
READINGS = {(r['corpus'], r['locus'], r['surface'], r['old']): r['lemma']
            for r in ROWS}
NONCONTENT = {(r['corpus'], r['locus'], r['surface'], r['lemma'])
              for r in ROWS if r['lemma'].endswith((' (name)', '@numeral'))}


def reviewed_lemma(corpus, lemma, surface, locus):
    return READINGS.get((corpus, locus, surface, lemma), lemma)


def noncontent(corpus, lemma, surface, locus):
    return (corpus, locus, surface, lemma) in NONCONTENT
