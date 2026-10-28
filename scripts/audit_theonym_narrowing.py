"""Before/after census for the theonym-allowlist narrowing of exact-match names.

uv run python -I scripts/audit_theonym_narrowing.py before DIR [corpus ...]
uv run python -I scripts/audit_theonym_narrowing.py after DIR [corpus ...]
uv run python -I scripts/audit_theonym_narrowing.py report DIR OUT.json

'before' replays the batch-6 gate (exact match only, no allowlist) and records
every source-tagged lemma that gate kept bare. 'after' runs production code.
Only lemmas, individual forms and loci are reported; no running text.
"""
import collections
import gzip
import importlib.util
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('w6_theonyms_audit', ROOT / 'scripts/audit_w6_theonyms.py')
w6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w6)

from pie import formula_search as fs  # noqa: E402
from pie import name_mapping as nm  # noqa: E402


def main():
    mode, directory = sys.argv[1:3]
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if mode == 'report':
        return report(directory, Path(sys.argv[3]))
    selected = set(sys.argv[3:])
    kept = collections.defaultdict(collections.Counter)
    if mode == 'before':
        # Batch-6 behaviour: exact production match alone keeps a name.
        nm.theonym_allowed = lambda corpus, lemma: True
    original = nm.name_lemma

    def recording(corpus, lemma):
        out = original(corpus, lemma)
        if not out.endswith(' (name)'):
            kept[corpus][out] += 1
        return out
    nm.name_lemma = recording
    lex = fs.load_jsonl(ROOT / 'data/lexicon/lexicon.jsonl')
    for c, loader in w6.corpora():
        if selected and c not in selected:
            continue
        path = directory / f'{mode}-{c}.jsonl.gz'
        if path.exists():
            continue
        kept.clear()
        ts = loader()
        m = w6.mapping(c, ts, lex)
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            for t in ts:
                f.write(json.dumps([t.lemma, t.content, t.pos,
                                    sorted(m.get(t.lemma, ())) if t.content else [],
                                    t.locus, t.surface], ensure_ascii=False) + '\n')
        (directory / f'{mode}-{c}-kept.json').write_text(
            json.dumps({k: dict(v.most_common()) for k, v in kept.items()}, ensure_ascii=False, indent=1))
        print(mode, c, len(ts), 'kept lemmas', sum(len(v) for v in kept.values()), flush=True)


def report(directory, out):
    result = {'seed': 6026, 'corpora': {}}
    for c, _ in w6.corpora():
        b, a = directory / f'before-{c}.jsonl.gz', directory / f'after-{c}.jsonl.gz'
        if not (b.exists() and a.exists()):
            continue
        lost, regained, changed, n = [], [], 0, 0
        lost_freq, kept_freq = collections.Counter(), collections.Counter()
        before_kept = json.loads((directory / f'before-{c}-kept.json').read_text())
        census = sorted({l for v in before_kept.values() for l in v})
        with gzip.open(b, 'rt', encoding='utf-8') as fb, gzip.open(a, 'rt', encoding='utf-8') as fa:
            for i, (lb, la) in enumerate(zip(fb, fa)):
                old, new = json.loads(lb), json.loads(la)
                assert old[4:] == new[4:], (c, i, 'alignment changed')
                n += 1
                if old[:4] != new[:4]:
                    changed += 1
                row = {'index': i, 'lemma': old[0], 'form': old[5], 'locus': old[4],
                       'before': old[:4], 'after': new[:4]}
                if old[3] and not new[3]:
                    lost.append(row)
                    lost_freq[old[0]] += 1
                elif not old[3] and new[3]:
                    regained.append(row)
                elif old[3] and old[0] in census and old[:4] == new[:4]:
                    kept_freq[old[0]] += 1
            assert fb.read() == fa.read() == '', (c, 'token count changed')
        allowed = {l for l in census if nm.theonym_allowed(c, l)}
        result['corpora'][c] = {
            'tokens': n, 'changed_tokens': changed,
            'census_exact_name_lemmas': len(census),
            'census_allowlisted': sorted(allowed), 'census_now_qualified': sorted(set(census) - allowed),
            'lost_roots_tokens': len(lost), 'lost_roots_lemma_counts': dict(lost_freq.most_common()),
            'regained_tokens': len(regained),
            'deity_tokens_lost_roots': sum(v for k, v in lost_freq.items() if k in allowed),
            'kept_census_lemma_token_counts': dict(kept_freq.most_common()),
            'lost_roots_sample_30': random.Random(6026).sample(lost, min(30, len(lost))),
        }
        print(c, n, 'lost', len(lost), 'regained', len(regained), flush=True)
    agg = collections.Counter()
    for c, v in result['corpora'].items():
        if c != 'grp':
            agg.update(v['lost_roots_lemma_counts'])
    result['aggregate_excluding_overlapping_grp'] = {
        'lost_roots_tokens': sum(agg.values()), 'top_40_lost_lemmas': agg.most_common(40)}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
