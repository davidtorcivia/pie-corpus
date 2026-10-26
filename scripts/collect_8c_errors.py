#!/usr/bin/env python3
"""Collect unverified reader error reports without loading text-bearing slabs.

Usage: uv run python -I scripts/collect_8c_errors.py CLAIMS_DIR ... --output FILE
Without --readers, Stage C-S input defaults to the finished pilot readers.
Use --readers RS004 RS005 or --readers 'RS00[4-8]' to select another wave;
--exclude accepts the same reader-ID globs and takes precedence. Quote globs
to prevent shell expansion. RS002H is always excluded before opening files.
Output retains the reader-brief envelope, adds corpus/source/provenance, and
merges reports by corpus + given lemma (or form). Unidentified notes remain
separate instead of collapsing all unknown words into one error. Harvesting is
heuristic: quotes are evidence for review, never verified mapping corrections.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
KINDS = {'mapping', 'lemma', 'ocr', 'unit', 'name'}
FIELDS = ('passage', 'form', 'given_lemma', 'given_etymon', 'kind',
          'correct_reading', 'evidence')
PILOT = re.compile(r'RS(?:001[^.]*|002|002X|003[^.]*|009[^.]*)\.(?:jsonl|progress)$')
WORD = r"[\w\u0300-\u036f*ḱǵʰ₁₂₃-]+"
SIGNALS = {
    'ocr': r'\bOCR\b.{0,35}(?:misread|error|junk|uncertain)|(?:misread|mismapped|uncertain).{0,35}\bOCR\b',
    'lemma': r'wrong lemma|mislemmati[sz]|lemma.{0,20}(?:wrong|incorrect)|\bmisread(?:ing)?\b|\b' + WORD + r'\s*=\s*[^;]{1,80},?\s+not\b',
    'mapping': r'mis[- ]?map|(?:wrong|missing|erroneous|spurious|uncertain).{0,25}mapping|mapping.{0,35}(?:wrong|junk|incorrect|not evidence)|not (?:a secure cognate|<)|spurious matches',
    'unit': r'unit.{0,25}(?:cut|split|boundary).{0,20}wrong|wrong.{0,20}unit (?:cut|boundary)|unit cut in the wrong place',
    'name': r'name (?:taken|mapped|treated|misread) as (?:a )?word',
}
LANGUAGES = {'Irish': ('sga', 'mga', 'ga'), 'Welsh': ('wlm', 'cy'),
             'ON': ('menota', 'non'), 'Norse': ('menota', 'non')}


def allowed(path: Path, readers: list[str] | None = None,
            exclude: list[str] = ()) -> bool:
    """Filter names before opening; never inspect the unfinished pilot reader."""
    if path.suffix not in {'.jsonl', '.progress'} or path.name.startswith('RS002H.'):
        return False
    if any(fnmatchcase(path.stem, pattern) for pattern in exclude):
        return False
    if readers is not None:
        return any(fnmatchcase(path.stem, pattern) for pattern in readers)
    return 'stageCS' not in path.parts or bool(PILOT.fullmatch(path.name))


def load_loci(dirs: list[Path]) -> tuple[dict, dict]:
    passages, bundles = {}, {}
    for directory in dirs:
        for path in sorted(directory.glob('*.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            passages.update((p['id'], p) for p in data.get('passages', []))
            for b in data.get('bundles', []):
                bundles[b['bundle']] = [b['pivot'], *b.get('partners', [])]
    return passages, bundles


def normalize(record: dict, passages: dict, source: str, origin: dict) -> dict:
    supplied = record['error']
    error = {key: supplied.get(key, '') or '' for key in FIELDS}
    if error['kind'] not in KINDS:
        raise ValueError(f"Invalid error kind {error['kind']!r} at {origin}")
    passage = passages.get(error['passage'], {})
    corpus = passage.get('corpus') or supplied.get('corpus', '')
    if not corpus and ':' in error['passage']:
        corpus = error['passage'].split(':', 1)[0]
    # Only an exact form match, in the target passage, can supply word metadata.
    words = list(passage.get('words', []))
    for line in passage.get('lines', []):
        if line.get('role') == 'passage':
            words.extend(line.get('words', []))
    matches = [w for w in words if isinstance(w, dict) and w.get('form') == error['form']]
    if len(matches) == 1:
        for target, key in [('given_lemma', 'lemma'), ('given_etymon', 'etymon')]:
            if not error[target]:
                error[target] = matches[0].get(key, '') or ''
    error['corpus'] = corpus
    if 'note_fragment' in supplied:
        error['note_fragment'] = supplied['note_fragment']
    return {'reader': record.get('reader', ''), 'slab': record.get('slab', ''),
            'source': source, 'error': error, 'provenance': [origin]}


def harvest(note: str, reader: str, slab: str, passages: dict, bundles: dict,
            origin: dict) -> list[dict]:
    results = []
    # Do not split abbreviations (Ir., e.g., etc.) or passage identifiers.
    recent_bundles = []
    for fragment in re.split(r';|\n|(?<=[.!?])\s+(?=[A-Z][a-z]|B[CS]-)', note):
        fragment = fragment.strip()
        # A quoted/new lead in a semicolon list cannot inherit the prior lead's locus.
        if not re.match(r'(?:[a-z]|Irish\b|Welsh\b)', fragment):
            recent_bundles = []
        mentioned = re.findall(r'B[CS]-[0-9a-f]+', fragment)
        if mentioned:
            recent_bundles = mentioned
        kinds = [k for k, pattern in SIGNALS.items() if re.search(pattern, fragment, re.I)]
        if re.search(r'\bnot inherited\b', fragment) and not re.search(r'wrong|misread|mis.?map', fragment, re.I):
            kinds = [k for k in kinds if k != 'lemma']
        if not kinds:
            continue
        # Negated reports are not positive evidence of an error.
        if re.search(r'\bno (?:wrong lemmas?|mapping errors?|OCR errors?|misreadings?)\b', fragment, re.I):
            continue
        form = ''
        patterns = [
            rf'\b({WORD})\s*=\s*{WORD}.{{0,60}}\bnot\b',
            rf'(?:mis[- ]mapping of\s+(?:ON\s+)?|wrong lemma\s+["`\']?|misread(?:ing)?\s+(?:Irish\s+|Welsh\s+)?["`\']?)({WORD})',
            rf'({WORD})\s+is not (?:<|a secure cognate)',
            rf'automatic\s+({WORD}(?:/{WORD})?)\s+mapping',
            rf'spurious matches include Irish\s+({WORD})',
        ]
        for pattern in patterns:
            match = re.search(pattern, fragment, re.I)
            if match:
                form = match[1]
                break
        pids = [pid for pid in passages if pid in fragment]
        # Bundle references narrow candidates but never imply every partner is wrong.
        candidates = set()
        for bid in recent_bundles:
            candidates.update(bundles.get(bid, []))
        if not pids and candidates:
            for language, prefixes in LANGUAGES.items():
                if re.search(r'\b' + language + r'\b', fragment):
                    selected = [p for p in candidates if p.split(':')[0] in prefixes]
                    if len(selected) == 1:
                        pids = selected
                        break
        # Without an exact locus, don't invent one or infer a lemma from prose.
        for pid in pids or ['']:
            for kind in kinds:
                # Capture a short literal excerpt centered on the diagnostic signal.
                signal = re.search(SIGNALS[kind], fragment, re.I)
                start = max(0, signal.start() - 100)
                quote = fragment[start:start + 280]
                error = {'passage': pid, 'form': form, 'kind': kind,
                         'evidence': quote, 'note_fragment': quote}
                results.append(normalize({'reader': reader, 'slab': slab, 'error': error},
                                         passages, 'harvested-note', origin))
    return results


def deduplicate(reports: list[dict]) -> list[dict]:
    def key(value):
        return unicodedata.normalize('NFC', value).strip().casefold()
    merged = {}
    aliases = {}
    # Prefer explicit reports, retaining each additional observation as evidence.
    for report in sorted(reports, key=lambda r: r['source'] != 'structured-error'):
        e = report['error']
        word = e['given_lemma'] or e['form']
        identity = (key(e['corpus']), key(word))
        if not word or not e['corpus']:
            identity += (e['passage'], key(e.get('note_fragment', e['evidence'])))
        word_aliases = [(key(e['corpus']), key(w)) for w in (e['given_lemma'], e['form'])
                        if w and e['corpus']]
        identity = next((aliases[a] for a in word_aliases if a in aliases), identity)
        for alias in word_aliases:
            aliases[alias] = identity
        if identity not in merged:
            merged[identity] = report
            report['kinds'] = [e['kind']]
            report['observations'] = []
        else:
            kept = merged[identity]
            if e['kind'] not in kept['kinds']:
                kept['kinds'].append(e['kind'])
            kept['observations'].append({'reader': report['reader'], 'slab': report['slab'],
                                         'source': report['source'], 'error': e})
            for origin in report['provenance']:
                if origin not in kept['provenance']:
                    kept['provenance'].append(origin)
    return list(merged.values())


def collect(claims_dirs: list[Path], loci_dirs: list[Path],
            readers: list[str] | None = None, exclude: list[str] = ()) -> list[dict]:
    passages, bundles = load_loci(loci_dirs)
    reports = []
    paths = sorted({p for d in claims_dirs for p in d.iterdir()
                    if p.is_file() and allowed(p, readers, exclude)})
    metadata = {}
    for path in paths:
        if path.suffix != '.jsonl':
            continue
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError as exc:
                raise ValueError(f'{path}:{number}: invalid JSON') from exc
            reader = record.get('reader', path.stem)
            slab = record.get('slab', '')
            metadata[path.with_suffix('.progress')] = (reader, slab)
            origin = {'file': str(path), 'line': number}
            if 'error' in record:
                reports.append(normalize(record, passages, 'structured-error', origin))
            if record.get('done') is True:
                reports.extend(harvest(record.get('note', ''), reader, slab, passages, bundles, origin))
    for path in paths:
        if path.suffix == '.progress':
            reader, slab = metadata.get(path, (path.stem, ''))
            for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                reports.extend(harvest(line, reader, slab, passages, bundles,
                                       {'file': str(path), 'line': number}))
    return deduplicate(reports)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('claims_dirs', type=Path, nargs='+')
    parser.add_argument('--output', '-o', required=True, type=Path)
    parser.add_argument('--readers', nargs='+', metavar='ID_OR_GLOB',
                        help='Select reader filename stems (overrides the pilot default)')
    parser.add_argument('--exclude', nargs='+', default=[], metavar='ID_OR_GLOB',
                        help='Exclude reader filename stems, even if selected')
    parser.add_argument('--loci-dirs', nargs='+', type=Path, default=[
        ROOT / 'data/research/8c/stageC/slabs-loci',
        ROOT / 'data/research/8c/stageCS/slabs-loci'])
    args = parser.parse_args()
    reports = collect(args.claims_dirs, args.loci_dirs, args.readers, args.exclude)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in reports), encoding='utf-8')
    print(f'{len(reports)} deduplicated reports')
    print('By kind (reports may have multiple kinds):', json.dumps(dict(sorted(Counter(
        k for r in reports for k in r['kinds']).items())), ensure_ascii=False))
    print('By corpus:', json.dumps(dict(sorted(Counter(
        r['error']['corpus'] or 'unknown' for r in reports).items())), ensure_ascii=False))


if __name__ == '__main__':
    main()
