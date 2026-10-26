# Stage B Greek-routing erratum — 2026-10-25

Stage B was completed and unblinded on 2026-10-23. Its historical result remains on record: 35 accepted claims, primary ratio 2.14 and p = 0.018 under the recorded analysis. This is a post-hoc mapping-impact audit, not a rebuilt experiment, re-review, or corrected significance analysis.

The [ENG-02 handoff](../audits/handoff-2026-10-24.md) identifies the defect: broad Greek used the `grc` override population, which lacks the reviewed decisions stored under `grp`. The correction keeps the corpus and etymological-link language `grc` but routes overrides through `grp`. Homer (`hom`) already has its own reviewed route and is unaffected by this routing change.

## Method and scope

Following [the impact checker](../../scripts/check_8c_greek_routing.py) (repository path `scripts/check_8c_greek_routing.py`), two independent fresh Python processes called `load_greek_b`, with no mapped-unit pickle/cache loaded. The old process changed only the `grp` override call back to `grc`; the corrected process used the current loader. Both used the shipped Greek link extract as an input, not a cache of mapped units. Commands used `uv run python -I`; `UV_CACHE_DIR` pointed to a new temporary directory. Only Greek units were loaded. This isolates the routing intervention using current loader inputs; it is not a reconstruction of every code/data version used in the original run.

Each process assigned stable passage IDs and emitted root-group sets and per-word lexeme/root IDs to temporary snapshots. Assertions checked identical unit counts, order, passage IDs, surface forms, lemmas, text/provenance hashes and licences. “Root set” means the union of IDs after `formula_search.group_map`; “word mapping” means the actual assigned lexeme/root IDs before grouping. A lexeme-to-root correction can therefore change a word annotation without changing the passage root set.

All Greek bundle-member IDs resolved uniquely in the fresh load. All 50 `data/research/8c/stageB/slabs-loci/*.json` files were joined to the **unblinded Stage B** bundle key. Every pivot and shown partner set matched the key (decoy replacements, not discarded real partners). Counts below cover bundle members, not surrounding context lines or hypothetical newly retrieved passages. Accepted claims were joined to the Stage B claims key; all cited bundle/slab references resolved. `accepted.jsonl` contains 35 unique claims and exactly equals the union of `accepted-1.jsonl` and `accepted-2.jsonl` after sorting by claim ID.

For each accepted claim, every Greek entry in its structured `words` list was checked: broad-Greek entries were matched by cited passage, lemma and surface form; the two combined entries in B133 were split into their component lemmas. Homer entries are unchanged by construction because the intervention never changes `hom`. This does not audit every word in supporting passages or independently reassess the prose etymological argument.

**Citation discrepancy:** B115 assigns ἄκουσας / ἀκούω to Pindarus, *Isthmia* 6.42. In the freshly loaded text it occurs at **6.43**, the adjacent line. Checking that occurrence gives `pie-lex-h2kjh2owsyeti` in both modes. The other four listed Greek words match 6.42. The original claim file is preserved.

## Bundle impact

| Population | Total | Changed root sets | Changed word annotations |
|---|---:|---:|---:|
| Broad-Greek loaded passages | 282,885 | 143,224 | 144,835 |
| Distinct broad-Greek bundle-member passages | 10,755 | 7,121 | 7,240 |
| Historical real bundles | 8,188 | 4,551 | 4,609 |
| Historical decoy bundles | 2,048 | 1,134 | 1,147 |
| All historical bundles | 10,236 | 5,685 | 5,756 |

Thus **55.54%** of historical bundles contain at least one Greek member whose root set changes (55.58% of real and 55.37% of decoy bundles). The corpus-wide counts exactly reproduce the `grc` counts in [the earlier impact report](8c-greek-routing-impact-2026-10-25.json); its Stage C bundle counts are not substituted for Stage B counts.

## All 35 accepted claims

“Changed?” concerns a Greek word explicitly listed in `words`, not any other word in its bundle. The last column counts cited historical bundles containing a root-set change anywhere among their Greek members. “No Greek words” means none in that structured list, not necessarily no Greek material elsewhere in the slab.

| Claim | Any cited Greek word mapping changed? | Cited bundles with changed Greek roots / all cited |
|---|---|---:|
| B001 | **Yes** | 2/3 |
| B005 | No | 2/4 |
| B012 | No | 1/3 |
| B018 | No Greek words | 1/2 |
| B021 | No | 0/3 |
| B028 | No | 3/4 |
| B037 | No | 1/2 |
| B053 | No | 0/2 |
| B060 | No Greek words | 2/2 |
| B063 | No | 2/3 |
| B064 | No | 0/1 |
| B076 | No | 1/1 |
| B077 | **Yes** | 2/2 |
| B082 | No | 0/2 |
| B087 | **Yes** | 0/3 |
| B089 | No | 2/5 |
| B090 | No Greek words | 2/2 |
| B092 | No | 1/1 |
| B095 | No | 1/1 |
| B097 | No | 2/2 |
| B098 | No | 2/3 |
| B099 | No | 1/1 |
| B105 | No Greek words | 3/3 |
| B109 | No | 3/3 |
| B110 | No Greek words | 1/7 |
| B112 | No | 1/2 |
| B113 | No | 1/2 |
| B115 | No (6.43 checked; see citation note) | 2/2 |
| B117 | No Greek words | 2/2 |
| B119 | No | 4/4 |
| B129 | No | 0/1 |
| B133 | **Yes** | 3/3 |
| B136 | No | 2/2 |
| B145 | No | 0/1 |
| B148 | **Yes** | 3/3 |

**Five claims change; 24 have Greek words with no mapping change; six list no Greek words.** The five changed claims represent three lemma-level corrections:

| Claim(s) | Cited occurrence | Old mapping IDs | Corrected mapping IDs |
|---|---|---|---|
| B001 | ἕσσαν / ἕννυμι, Hymni Homerici *In Venerem* 6 [0013-006:6] | `pie-root-wes-dress`, `pie-root-wes-graze`, `pie-root-wes-sell` | `pie-root-wes-dress` |
| B077 | βροτοῖς / βροτός, Plato *Respublica* 2.380.379e s1 (w2/2) | `pie-lex-mrtos`, `pie-lex-smrtos` | `pie-lex-mrtos` |
| B087, B148 | υἱεῖς / υἱός, Demosthenes *Contra Macartatum* 74 s1 (w1/2) | `pie-lex-suHnus` | `pie-root-sewH-bear` |
| B133 | ὑεῖ / υἱός, Plato *Theages* 122d s6 | `pie-lex-suHnus` | `pie-root-sewH-bear` |

The first two remove extra candidate IDs while retaining the claimed dress/mortal mapping. The last replaces the “son” lexeme annotation by its root-level mapping; both group to `pie-root-sewH-bear`. This explains why B087 has a changed cited word but no cited bundle with a changed root set. These are annotation descriptions, not fresh acceptance judgments.

The raw-flesh claims B037 and B136 cite ὠμῶν with lemma **ὠμός**, whose mapping does not change; B063 and B076 cite Homer, whose route does not change. The shoulder correction for **ὦμος** therefore does not change the specific Greek words listed by those four accepted claims. B001’s clothing verb does change as listed above; B115’s listed hearing/word vocabulary does not, with the line correction noted. No new novelty or philological validation is inferred from these checks.

## What changes, and what remains historical

A fresh annotation of these same passages would change the mappings and root sets quantified here. A fresh retrieval could change IDF weights, eligible pairs, scores, selected partners, merged bundles, decoys and slab composition; none of those downstream changes was computed. In particular, 5,685 affected bundles does **not** mean 5,685 invalid bundles or lost claims, and an unchanged cited word does not establish unchanged retrieval of that claim.

The historical slabs, keys, claims, grades, novelty classifications and score file remain unchanged. Keeping those inputs fixed keeps the recorded score fixed; the historical ratio/p-value is not a result for corrected-route retrieval. No revised accepted-claim count, effect size, p-value, or claim that the primary criterion would still pass is warranted by this audit. Any rebuild/rereading or re-review would need a separately labelled follow-up that acknowledges prior unblinding. No Tier 2/Tier 3 corpus or export regeneration was performed, and no Stage C-S slabs or key were opened.

## Input fingerprints and replay

SHA-256 fingerprints below identify the audited files. For a collection, the digest is SHA-256 of the concatenation, in sorted relative-path order, of `relative_path + "\0" + file_sha256 + "\n"`. The mapped snapshots are temporary; the self-contained scripts below reproduce them and the detailed bundle/claim joins in `/tmp`. Run the two modes in separate processes, then the comparison, from the project root. Adjust only the workspace path if replaying elsewhere. The comparison output includes every affected bundle's changed member passage IDs.

| Input | SHA-256 |
|---|---|
| `scripts/build_8c_stageB.py` | `54f1655d5f39e3b8bd1f253503e77e2aa25a0390d81fdc8249aa060f610fb547` |
| `scripts/build_8c_packets.py` | `546c5968588a79159e95bc16495739e9159358fca051fd032e523342286dcf7d` |
| `scripts/check_8c_greek_routing.py` | `3b28a26e1c4b848cc68b6311444c019c62f4a2beb06a8fc6f0c9eccdad773166` |
| `pie/formula_search.py` | `be62985ad3b640312ab259577e0118daa7efceacae4d31839ae966b886aded19` |
| `pie/formula_search_multi.py` | `bdfd58332453e76c871358c516b337eeb2e24185f0df0174218ed16c98135e6e` |
| `pie/mapping.py` | `f08a6ac370d2c70ed9364c1b3d170386a8190700d3f59c5d4b38229de1d6d8ce` |
| `data/lexicon/lexicon.jsonl` | `63d44dceac01956cf19262ae2a555bad668c3fcdaffadff1bc14f07da1972969` |
| `data/research/formulas/kaikki_links/grc.jsonl` | `498732cc56b831c539667584bf6654ce59f57f85baf78218db59219f9da10449` |
| `data/research/formulas/mapping-overrides/greek.json` | `2c3e6ef6405e8c992c4d3476fdfa28b7db16e3c001d3fded09ace7f2b58cd1b2` |
| `data/audits/keys/8c-stageB-key.json` | `f26a93fc81525a945690ddcdeb2707b5403f2480a472e2cf73c9249d990ac764` |
| `data/audits/keys/8c-stageB-claims-key.json` | `2aed3ea3a0eb908c23d3f4134b35728417ade2f9e8640903d6c029abb270de24` |
| `data/research/8c/stageB/results.json` | `36bdd24bd6f5807110f8b452f80e24253d16a1a1bd867d0a0b14bf62d3757c7a` |
| `data/research/8c/stageB/slabs-loci/*.json` (collection) | `f1b82495c259f8f8da3562449335c79bfc9fb751c3766e82df0589421f26ffc0` |
| `data/research/8c/stageB/review/accepted*.jsonl` (collection) | `161bc5957655d5593d48e325b4c22a0d950f132fcf42eb043ad934805dcb029b` |

<details>
<summary>Replay scripts (no corpus or export writes)</summary>

Save as `/tmp/stageb-routing.py`:

```python
import sys, json, importlib.util, hashlib
from pathlib import Path
R=Path('/Users/david/AI/PIE')
spec=importlib.util.spec_from_file_location('stageb', R/'scripts/build_8c_stageB.py')
S=importlib.util.module_from_spec(spec); sys.modules[spec.name]=S; spec.loader.exec_module(S)
from pie import formula_search as fs, formula_search_multi as fm
mode=sys.argv[1]
if mode=='old':
    original=fm.apply_lemma_overrides
    def old_route(population,*a,**k): return original('grc' if population=='grp' else population,*a,**k)
    fm.apply_lemma_overrides=old_route
lex=fs.load_jsonl(R/'data/lexicon/lexicon.jsonl'); groups=fs.group_map(lex)
units,_=S.load_greek_b(R,lex,groups); S.B.assign_pids({'grc':units})
with open('/tmp/stageb-'+mode+'.jsonl','w') as f:
    for u in units:
        provenance=hashlib.sha256(json.dumps([u.pid,u.key,u.locus,u.book,u.text,u.licence,u.research_only,[(s,l) for s,l,_ in u.words]],ensure_ascii=False).encode()).hexdigest()
        f.write(json.dumps({'pid':u.pid,'roots':sorted({groups.get(x,x) for _,_,ids in u.words for x in ids}), 'words':[(s,l,sorted(ids)) for s,l,ids in u.words], 'provenance':provenance},ensure_ascii=False)+'\n')
print(mode,len(units))
```

Save as `/tmp/stageb-compare.py`:

```python
import json,itertools,collections,unicodedata
from pathlib import Path
R=Path('/Users/david/AI/PIE'); D=R/'data/research/8c/stageB'
claims=[json.loads(l) for l in (D/'review/accepted.jsonl').read_text().splitlines()]
parts=[json.loads(l) for f in sorted((D/'review').glob('accepted-*.jsonl')) for l in f.read_text().splitlines()]
assert sorted(parts,key=lambda x:x['claim'])==sorted(claims,key=lambda x:x['claim']) and len(claims)==35
need={w['passage'] for c in claims for w in c['words'] if w['passage'].startswith('grc:')}
need.add('grc:Pindarus Isthmia 6.43')
changed=set(); ann=set(); passages={}; total=0; loaded=set()
with open('/tmp/stageb-old.jsonl') as a,open('/tmp/stageb-corrected.jsonl') as b:
 for x,y in itertools.zip_longest(a,b):
  assert x and y
  x,y=json.loads(x),json.loads(y); assert x['pid']==y['pid'] and x['provenance']==y['provenance']
  p=x['pid']; assert p not in loaded; loaded.add(p); total+=1
  if x['roots']!=y['roots']:changed.add(p)
  if x['words']!=y['words']:ann.add(p)
  if p in need:passages[p]=(x,y)
key=json.loads((R/'data/audits/keys/8c-stageB-key.json').read_text())['slabs']
ck=json.loads((R/'data/audits/keys/8c-stageB-claims-key.json').read_text())
bs={}; rows=[]; members=set()
for f in sorted((D/'slabs-loci').glob('*.json')):
 s=json.loads(f.read_text()); affected=[]; counts=collections.Counter()
 for b in s['bundles']:
  k=key[s['slab']][b['bundle']]; assert k['pivot']==b['pivot']
  expected=k.get('decoy_partners') if k['kind']=='decoy' else [p['id'] for p in k['real_partners']]
  assert set(expected)==set(b['partners'])
  m={b['pivot'],*b['partners']}; members|=m; delta=sorted(m&changed)
  bs[b['bundle']]={'slab':s['slab'],'kind':k['kind'],'changed':delta,'annotations':sorted(m&ann)}
  counts[k['kind']]+=1
  if delta: affected.append(b['bundle']);counts[k['kind']+'_changed']+=1
 rows.append({'slab':s['slab'],**counts,'affected':affected})
assert {m for m in members if m.startswith('grc:')} <= loaded
assert set(bs) == {b for slab in key.values() for b in slab}
cr=[]
for c in claims:
 checks=[]
 for w in c['words']:
  if not w['passage'].startswith('grc:'):continue
  lookup = 'grc:Pindarus Isthmia 6.43' if c['claim']=='B115' and w['lemma']=='ἀκούω' else w['passage']
  pair=passages.get(lookup); assert pair,w
  for lemma in w['lemma'].split(', '):
   matches=[(i,s,l,ids) for i,(s,l,ids) in enumerate(pair[0]['words']) if unicodedata.normalize('NFC',l)==unicodedata.normalize('NFC',lemma)]
   assert matches, (c['claim'],w)
   for i,s,l,ids in matches:
    assert s in w['form'], (c['claim'],w,s)
    new=pair[1]['words'][i][2];checks.append({'passage':w['passage'],'form':s,'lemma':l,'old':ids,'new':new})
 bundles=ck[c['claim']]['bundles'];assert all(b in bs and bs[b]['slab']==ck[c['claim']]['slab'] for b in bundles)
 cr.append({'claim':c['claim'],'greek_words':sum(w['passage'].startswith(('grc:','hom:')) for w in c['words']), 'checks':checks,'changed':[w for w in checks if w['old']!=w['new']], 'bundles':bundles,'affected_bundles':[b for b in bundles if bs[b]['changed']]})
r={'total_units':total,'roots_changed':len(changed),'annotations_changed':len(ann),'member_greek':len([m for m in members if m.startswith('grc:')]),'member_roots_changed':len(members&changed),'member_annotations_changed':len(members&ann),'slabs':rows,'bundles':bs,'claims':cr}
Path('/tmp/stageb-impact.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print({k:v for k,v in r.items() if k not in ('slabs','bundles','claims')})
print('bundle totals',collections.Counter(x['kind'] for x in bs.values()),'affected',collections.Counter(x['kind'] for x in bs.values() if x['changed']))
for c in cr: print(c['claim'], 'changes',c['changed'],'bundles',len(c['affected_bundles']),len(c['bundles']))
```

```sh
UV_CACHE_DIR=/tmp/pie-uv-stageb uv run python -I /tmp/stageb-routing.py old
UV_CACHE_DIR=/tmp/pie-uv-stageb uv run python -I /tmp/stageb-routing.py corrected
UV_CACHE_DIR=/tmp/pie-uv-stageb uv run python -I /tmp/stageb-compare.py
```

</details>

## Affected bundle IDs, by historical slab

Each ID below has at least one shown Greek member with a changed root-group set. IDs not listed are unchanged under that test. Counts include both kinds; the key supplies kind and the replay output supplies changed member IDs.

<details>
<summary>Complete inventory: 5,685 affected bundles across 50 slabs</summary>

**S-07c3** — real 69/150; decoy 26/38.

`B-02c6b`, `B-03306`, `B-04ca5`, `B-05111`, `B-08831`, `B-0c5b6`, `B-0fd27`, `B-1587b`, `B-16961`, `B-1c3ca`, `B-1c98e`, `B-1d8be`, `B-1dff2`, `B-22ba3`, `B-29f3a`, `B-2c46d`, `B-2ea50`, `B-33354`, `B-3ce9e`, `B-3e23f`, `B-41c89`, `B-426f8`, `B-428ec`, `B-43c44`, `B-58c75`, `B-5908d`, `B-5a452`, `B-5d2c9`, `B-60749`, `B-6096f`, `B-6338f`, `B-65343`, `B-65784`, `B-65c8d`, `B-6b502`, `B-6f406`, `B-704e3`, `B-71544`, `B-75e40`, `B-7ecd1`, `B-84cf1`, `B-85186`, `B-870e6`, `B-882b1`, `B-8cfdf`, `B-8d39b`, `B-8d555`, `B-8dd49`, `B-8e20a`, `B-93451`, `B-9ae00`, `B-9aef7`, `B-9b16b`, `B-9d4ac`, `B-9febb`, `B-a066a`, `B-a0d61`, `B-a281a`, `B-a284c`, `B-a533b`, `B-a6741`, `B-aa9c6`, `B-aefbf`, `B-b44a2`, `B-b661c`, `B-b77b9`, `B-b95a6`, `B-bbabd`, `B-bd75d`, `B-c1a76`, `B-c37b5`, `B-c9fda`, `B-ca897`, `B-cc401`, `B-cf56e`, `B-cfb26`, `B-d2c32`, `B-d4783`, `B-d5604`, `B-d6f8a`, `B-de601`, `B-de728`, `B-e1674`, `B-e2373`, `B-e3349`, `B-e8ef4`, `B-e9d8d`, `B-ea1fa`, `B-ebdeb`, `B-f6587`, `B-fa772`, `B-fce0f`, `B-fd262`, `B-fd440`, `B-ffc88`

**S-0863** — real 67/139; decoy 19/35.

`B-03264`, `B-0471e`, `B-0590e`, `B-068c2`, `B-10702`, `B-13a6e`, `B-15ed5`, `B-17038`, `B-19592`, `B-205be`, `B-22a28`, `B-2c28b`, `B-2ce1b`, `B-31f96`, `B-32b8b`, `B-32e09`, `B-33c2e`, `B-343a4`, `B-3d948`, `B-3f91b`, `B-441a2`, `B-4a8a0`, `B-4bca8`, `B-4bd25`, `B-4c4a9`, `B-4ec04`, `B-50642`, `B-510aa`, `B-59ef2`, `B-5ecf0`, `B-6254a`, `B-640c2`, `B-645ba`, `B-67805`, `B-6cec8`, `B-6d7e8`, `B-6dee2`, `B-72549`, `B-75508`, `B-7b79e`, `B-7bb5a`, `B-7d026`, `B-7ec81`, `B-802ea`, `B-848a6`, `B-87c1e`, `B-8a7d9`, `B-8b3ed`, `B-8be24`, `B-91287`, `B-94d05`, `B-95336`, `B-9566b`, `B-95c52`, `B-96ece`, `B-97f05`, `B-99a0f`, `B-9d8d0`, `B-a8f31`, `B-aa338`, `B-af177`, `B-b6133`, `B-b640f`, `B-b7385`, `B-bae35`, `B-c54f5`, `B-cb01e`, `B-d3dc6`, `B-d640f`, `B-da8a1`, `B-db19f`, `B-dc85a`, `B-dcb1f`, `B-dff89`, `B-e0451`, `B-e056b`, `B-e0605`, `B-e25c8`, `B-e7db5`, `B-ea322`, `B-ea4a8`, `B-f0918`, `B-f0d69`, `B-f0f71`, `B-f879d`, `B-fe571`

**S-0e1c** — real 24/218; decoy 11/54.

`B-0640d`, `B-0b4fb`, `B-1436f`, `B-1437b`, `B-1f326`, `B-21e55`, `B-2f0a0`, `B-411a6`, `B-54fb3`, `B-5a02d`, `B-5c1a9`, `B-631ee`, `B-670d6`, `B-6bb34`, `B-7129b`, `B-72e10`, `B-7aa33`, `B-7cafe`, `B-7d39d`, `B-87e82`, `B-88f99`, `B-8bc81`, `B-96ad8`, `B-b8884`, `B-c8a27`, `B-c9319`, `B-cf851`, `B-d96de`, `B-dde6a`, `B-ded4e`, `B-e075f`, `B-eb02e`, `B-ebdc9`, `B-f469e`, `B-f9329`

**S-11ba** — real 123/218; decoy 32/55.

`B-02603`, `B-04d62`, `B-05871`, `B-08199`, `B-09008`, `B-09333`, `B-0f330`, `B-0fef8`, `B-11648`, `B-122c2`, `B-175f0`, `B-1ab65`, `B-1bf02`, `B-1ec99`, `B-1f543`, `B-213e0`, `B-261d5`, `B-2ad3e`, `B-2c502`, `B-2c68a`, `B-2d783`, `B-2e43a`, `B-2e6c3`, `B-33442`, `B-353f3`, `B-365a0`, `B-36ebf`, `B-37338`, `B-383f9`, `B-3bcde`, `B-3c81a`, `B-40baa`, `B-4261e`, `B-448dd`, `B-46c17`, `B-49f4f`, `B-4c555`, `B-53b0b`, `B-540f7`, `B-55afb`, `B-5620d`, `B-57464`, `B-58897`, `B-58efb`, `B-5a61f`, `B-5b861`, `B-5b917`, `B-5bba2`, `B-5e4ef`, `B-5eb58`, `B-5ec7f`, `B-5efda`, `B-5f70c`, `B-603ca`, `B-60d00`, `B-61f4b`, `B-63272`, `B-64596`, `B-64fbf`, `B-65d44`, `B-664d3`, `B-685d2`, `B-6975a`, `B-6bc08`, `B-7024f`, `B-7160b`, `B-773fa`, `B-78149`, `B-79263`, `B-7b3c2`, `B-7ddd8`, `B-7de34`, `B-7e1d1`, `B-7fc98`, `B-7ff4e`, `B-85d14`, `B-875c9`, `B-88cfa`, `B-89940`, `B-8f301`, `B-8f65d`, `B-92a76`, `B-930cb`, `B-93c85`, `B-9762c`, `B-98327`, `B-9b4e6`, `B-9d367`, `B-9e178`, `B-a0059`, `B-a0213`, `B-a0e6d`, `B-a1d77`, `B-a31b5`, `B-a3edb`, `B-a4335`, `B-a5e96`, `B-a6f2e`, `B-a9619`, `B-ab196`, `B-ab3c0`, `B-abd56`, `B-ac0f8`, `B-ae8d8`, `B-b1e82`, `B-b236c`, `B-b57b4`, `B-b6394`, `B-b6a93`, `B-b7fea`, `B-b844c`, `B-bbf61`, `B-bca99`, `B-be910`, `B-befb2`, `B-c3e35`, `B-c8a2b`, `B-c948f`, `B-c9df3`, `B-cab70`, `B-cc08a`, `B-cc7ed`, `B-ccffe`, `B-cd0e2`, `B-ce108`, `B-d0664`, `B-d0685`, `B-d18ee`, `B-d1ee6`, `B-d2558`, `B-d30c7`, `B-d4aa8`, `B-d550d`, `B-d6059`, `B-dd085`, `B-de5f6`, `B-e1b39`, `B-e2232`, `B-e253d`, `B-e2eb1`, `B-e5a7d`, `B-e6302`, `B-e8190`, `B-e86f9`, `B-e87fd`, `B-ea53b`, `B-ec033`, `B-ee7cc`, `B-eef19`, `B-f0493`, `B-f0d7c`, `B-f36ab`, `B-f53f8`, `B-f89f2`, `B-f9791`

**S-1b86** — real 17/133; decoy 2/33.

`B-00b72`, `B-0866d`, `B-0f7e6`, `B-17760`, `B-26169`, `B-43d3d`, `B-5235c`, `B-68866`, `B-68dd7`, `B-87515`, `B-a7214`, `B-acc3a`, `B-b05bd`, `B-ba565`, `B-c6289`, `B-dc35a`, `B-e3700`, `B-f4477`, `B-fb4bc`

**S-26f8** — real 103/199; decoy 28/50.

`B-00e35`, `B-051fd`, `B-055f9`, `B-0578e`, `B-078f2`, `B-08904`, `B-095da`, `B-0b69a`, `B-0cc50`, `B-0d32a`, `B-0e7ba`, `B-0ecbc`, `B-0f440`, `B-105b5`, `B-10ae8`, `B-1189d`, `B-132bb`, `B-132ee`, `B-13602`, `B-15065`, `B-16dc5`, `B-189c5`, `B-1e9d3`, `B-2028b`, `B-21518`, `B-24bad`, `B-25f9e`, `B-27076`, `B-280ea`, `B-2a32a`, `B-2be2c`, `B-2da6a`, `B-2f5e1`, `B-32dbe`, `B-346f8`, `B-371be`, `B-39912`, `B-3bb3a`, `B-3ff9c`, `B-421f8`, `B-43717`, `B-47a03`, `B-4d24d`, `B-4df40`, `B-4ed71`, `B-51fb8`, `B-5489f`, `B-57a82`, `B-589e4`, `B-59d9a`, `B-5b349`, `B-5be56`, `B-61487`, `B-66c36`, `B-670cf`, `B-681d7`, `B-68899`, `B-6af32`, `B-6bcbd`, `B-6cc45`, `B-6e714`, `B-6f647`, `B-708fd`, `B-70bae`, `B-780d0`, `B-79c8f`, `B-7e1f8`, `B-80b64`, `B-83ac1`, `B-8459b`, `B-846d6`, `B-8472d`, `B-8476d`, `B-85840`, `B-88238`, `B-88bdd`, `B-897f0`, `B-8b292`, `B-8cf86`, `B-8e380`, `B-9156d`, `B-935b1`, `B-93db0`, `B-942bd`, `B-9fc07`, `B-a12e4`, `B-a3b66`, `B-a44d9`, `B-a8461`, `B-a8b68`, `B-a9df4`, `B-ab968`, `B-ace48`, `B-b202f`, `B-b208f`, `B-b36cb`, `B-b7357`, `B-bbe9c`, `B-bcbec`, `B-c01f6`, `B-c10da`, `B-c146c`, `B-c9b6b`, `B-ce52d`, `B-ce603`, `B-cf649`, `B-d0b5b`, `B-d1992`, `B-d5fc8`, `B-da58e`, `B-db66b`, `B-dc52a`, `B-de003`, `B-e0ce4`, `B-e14b1`, `B-e4855`, `B-e641d`, `B-e6aaf`, `B-ea7b7`, `B-ebbbf`, `B-ece4a`, `B-eeb59`, `B-f0885`, `B-f25cf`, `B-f4e54`, `B-f7822`, `B-f94af`, `B-fdcb1`, `B-fe27d`, `B-fefcf`, `B-ffa48`

**S-27bb** — real 139/171; decoy 36/43.

`B-01030`, `B-014d3`, `B-01a80`, `B-02219`, `B-02449`, `B-02c4f`, `B-05283`, `B-072fc`, `B-07511`, `B-0857e`, `B-09d33`, `B-0a710`, `B-0b2a8`, `B-0bb86`, `B-11459`, `B-12447`, `B-141c4`, `B-143c5`, `B-158ae`, `B-1695c`, `B-17a9c`, `B-19f65`, `B-1ccb7`, `B-221a1`, `B-227c3`, `B-2351a`, `B-24ca1`, `B-2733b`, `B-2770c`, `B-281d1`, `B-2b2c9`, `B-2bf02`, `B-2c981`, `B-31130`, `B-31136`, `B-33788`, `B-39d3a`, `B-3aad4`, `B-3c25a`, `B-3e506`, `B-40acc`, `B-4116c`, `B-413eb`, `B-414b2`, `B-42246`, `B-42378`, `B-44ce5`, `B-4940d`, `B-4a636`, `B-4a8e2`, `B-4afcd`, `B-4b802`, `B-4cf8c`, `B-4ed81`, `B-4fc2a`, `B-507c9`, `B-52aff`, `B-566c0`, `B-596a2`, `B-59bee`, `B-5afe1`, `B-5b160`, `B-5b1bf`, `B-5c349`, `B-5ce0b`, `B-5dad5`, `B-60981`, `B-641c1`, `B-64c8e`, `B-66390`, `B-69b9a`, `B-6ca7c`, `B-73fc0`, `B-74cdc`, `B-762d1`, `B-764ef`, `B-79088`, `B-7b9dc`, `B-7d0a5`, `B-80267`, `B-80363`, `B-804ed`, `B-8071e`, `B-80f23`, `B-821df`, `B-84f45`, `B-8a4ab`, `B-8a972`, `B-8afe2`, `B-8b300`, `B-8d58a`, `B-8de0a`, `B-8e63b`, `B-8f47e`, `B-8ff57`, `B-91082`, `B-924fb`, `B-94047`, `B-94ee5`, `B-96ddf`, `B-98296`, `B-98bfb`, `B-9b9d0`, `B-9d625`, `B-9d69c`, `B-9e7e4`, `B-a1835`, `B-a54eb`, `B-a6a37`, `B-a9537`, `B-abe0c`, `B-ac0a5`, `B-acadf`, `B-ad3c1`, `B-ad8c0`, `B-adf06`, `B-ae01b`, `B-ae034`, `B-af264`, `B-b0feb`, `B-b16a3`, `B-b2361`, `B-b27b2`, `B-b3171`, `B-b8674`, `B-b9fbd`, `B-b9fd5`, `B-bcb0f`, `B-bd4c0`, `B-bd597`, `B-bd5f5`, `B-bdef8`, `B-beff9`, `B-bf409`, `B-c15d6`, `B-c5de6`, `B-c760a`, `B-c8b48`, `B-cb559`, `B-ccbd1`, `B-cfe2b`, `B-d0f8a`, `B-d21c9`, `B-d3b63`, `B-d423c`, `B-d50ba`, `B-d7bda`, `B-d7dab`, `B-d94bf`, `B-dac4c`, `B-db934`, `B-dbfdf`, `B-dcc48`, `B-de13f`, `B-e1267`, `B-e2e20`, `B-e3cf5`, `B-e63de`, `B-e71f1`, `B-e81fd`, `B-e84f9`, `B-e8c56`, `B-eaaed`, `B-ead2f`, `B-ec2e4`, `B-eccbd`, `B-edff0`, `B-ef6a6`, `B-f0288`, `B-f4803`, `B-f4c4f`, `B-f57a8`, `B-f6f2f`, `B-fce4d`, `B-fd8c8`

**S-2b67** — real 69/128; decoy 16/33.

`B-00792`, `B-01329`, `B-05841`, `B-061d1`, `B-078c6`, `B-08996`, `B-0b8d1`, `B-10923`, `B-10d8d`, `B-15398`, `B-1a45b`, `B-1c610`, `B-1c6e4`, `B-1fad6`, `B-20c5a`, `B-23146`, `B-25abd`, `B-29df2`, `B-2a80f`, `B-2b8f1`, `B-2ec27`, `B-35b6c`, `B-3aac8`, `B-3f070`, `B-42962`, `B-493be`, `B-4fc9e`, `B-50b85`, `B-56a10`, `B-5b21d`, `B-62cac`, `B-66b69`, `B-67f6f`, `B-6e3ed`, `B-717a6`, `B-725e0`, `B-732a3`, `B-7459e`, `B-760d8`, `B-768af`, `B-7a691`, `B-7c167`, `B-7deec`, `B-80f6a`, `B-84ff9`, `B-8c0ed`, `B-8c1f4`, `B-96491`, `B-9a230`, `B-9f489`, `B-9ff9d`, `B-a011f`, `B-a175b`, `B-a7429`, `B-aac06`, `B-ab23a`, `B-afcc8`, `B-afe17`, `B-b089c`, `B-b315f`, `B-b6b6f`, `B-b6ec6`, `B-c5c37`, `B-cc0ce`, `B-cf480`, `B-d1480`, `B-d181e`, `B-d7a56`, `B-d8136`, `B-d9030`, `B-db8b9`, `B-dcde4`, `B-e0004`, `B-e0f7a`, `B-ea568`, `B-eb3a3`, `B-ec23e`, `B-ec64e`, `B-eed3b`, `B-f1553`, `B-f3689`, `B-f4d42`, `B-f4e36`, `B-f6eec`, `B-f78b0`

**S-2bd6** — real 70/199; decoy 22/50.

`B-00ecc`, `B-0571f`, `B-07344`, `B-083fb`, `B-09674`, `B-0dc38`, `B-12f83`, `B-1378d`, `B-1d30d`, `B-26db8`, `B-26f87`, `B-2de3a`, `B-2dfc7`, `B-2ecee`, `B-3287a`, `B-3311a`, `B-3615d`, `B-379e8`, `B-3a98c`, `B-420c2`, `B-437d9`, `B-48bf9`, `B-4ccd5`, `B-4f677`, `B-50c42`, `B-58fb2`, `B-5a7b9`, `B-5cad3`, `B-5dd47`, `B-5f14b`, `B-61c10`, `B-62a21`, `B-63b82`, `B-6737c`, `B-67f6e`, `B-6acdc`, `B-6f301`, `B-72fd2`, `B-73243`, `B-750c7`, `B-7812e`, `B-7b364`, `B-7ce50`, `B-80726`, `B-80e10`, `B-84dc5`, `B-85aff`, `B-87efd`, `B-8bb07`, `B-8e7b7`, `B-90749`, `B-922aa`, `B-92a82`, `B-95526`, `B-95a79`, `B-97eaa`, `B-99ee9`, `B-9ad3c`, `B-9afbf`, `B-a043d`, `B-a1a3d`, `B-a8dd2`, `B-abb68`, `B-ae6a5`, `B-af6c1`, `B-b1caf`, `B-b2113`, `B-b9ff1`, `B-bd81f`, `B-bea76`, `B-bebe6`, `B-c0379`, `B-c1c37`, `B-c2d32`, `B-c2fff`, `B-c3868`, `B-c8790`, `B-cd6b3`, `B-cf00f`, `B-cf96b`, `B-d12f3`, `B-da645`, `B-db0a8`, `B-dcac0`, `B-e41d4`, `B-e4a64`, `B-ed827`, `B-efdab`, `B-f238c`, `B-f34c8`, `B-f4ead`, `B-f88d7`

**S-2f31** — real 113/185; decoy 31/46.

`B-03dd6`, `B-0771c`, `B-08ba8`, `B-09e00`, `B-0ab2e`, `B-0abb8`, `B-0dcdb`, `B-0e21f`, `B-10038`, `B-10b52`, `B-11774`, `B-137f9`, `B-13bad`, `B-17bd7`, `B-1b96b`, `B-1e0b6`, `B-229ab`, `B-26335`, `B-27f1f`, `B-2f46c`, `B-330e8`, `B-34a53`, `B-36dbd`, `B-37510`, `B-38d83`, `B-3a423`, `B-3ea8e`, `B-3f0b1`, `B-3f114`, `B-3fcd4`, `B-40f23`, `B-4174c`, `B-41e1f`, `B-428e1`, `B-44b73`, `B-44c0b`, `B-46453`, `B-4d61a`, `B-4f8fd`, `B-4feec`, `B-564b6`, `B-572c1`, `B-5733b`, `B-5a2b0`, `B-5a805`, `B-5c065`, `B-5c870`, `B-5dac3`, `B-5f76f`, `B-5fb3b`, `B-6100a`, `B-61134`, `B-62ee2`, `B-6338d`, `B-65578`, `B-6593d`, `B-6717d`, `B-679fd`, `B-6952c`, `B-6a563`, `B-6cd44`, `B-6e640`, `B-6ed0e`, `B-6ed13`, `B-70c08`, `B-718ac`, `B-71db6`, `B-73fe7`, `B-767cc`, `B-79f20`, `B-7c2ee`, `B-7cc7a`, `B-82334`, `B-83aee`, `B-849fd`, `B-84c50`, `B-860ce`, `B-87ef2`, `B-884b6`, `B-8d978`, `B-90477`, `B-92bf5`, `B-94c77`, `B-97df1`, `B-9a6ab`, `B-9c397`, `B-9db84`, `B-9e626`, `B-a037e`, `B-a121c`, `B-a1ba6`, `B-a1dd0`, `B-a24e3`, `B-a5a01`, `B-a7846`, `B-a8767`, `B-a9ece`, `B-ab466`, `B-ab9da`, `B-acae8`, `B-ad4c5`, `B-af457`, `B-afd56`, `B-b3a4e`, `B-b4ed3`, `B-b5bca`, `B-b7806`, `B-b84c3`, `B-b962f`, `B-bc0c4`, `B-bc2ef`, `B-bf0c7`, `B-bf753`, `B-c4a00`, `B-caf3c`, `B-cd56c`, `B-d233b`, `B-d67e6`, `B-d7ba4`, `B-d81c8`, `B-d8c16`, `B-d92b9`, `B-dadde`, `B-db06c`, `B-dc554`, `B-df197`, `B-e0771`, `B-e1514`, `B-e74a7`, `B-e823a`, `B-e9cac`, `B-ea8da`, `B-ebb1b`, `B-ebca6`, `B-ec051`, `B-ec16d`, `B-eee3d`, `B-f049d`, `B-f0816`, `B-f4dfa`, `B-f7832`, `B-fa8ab`, `B-fca26`, `B-fff53`

**S-406b** — real 103/173; decoy 32/43.

`B-02321`, `B-0c415`, `B-10801`, `B-124f3`, `B-13856`, `B-157ce`, `B-15c7c`, `B-16868`, `B-168b9`, `B-1d0c6`, `B-1e54d`, `B-21d9c`, `B-23305`, `B-2b005`, `B-2ba7b`, `B-2e0f8`, `B-2e39f`, `B-3138c`, `B-3280a`, `B-32daf`, `B-335b1`, `B-33e7d`, `B-344ea`, `B-36087`, `B-363db`, `B-38904`, `B-39037`, `B-3a932`, `B-3bae0`, `B-3c233`, `B-400ee`, `B-403db`, `B-41c41`, `B-44cd4`, `B-45026`, `B-45dd1`, `B-4715c`, `B-47b7f`, `B-4828f`, `B-48f57`, `B-4b490`, `B-4d894`, `B-4f92a`, `B-5309b`, `B-5341a`, `B-534b0`, `B-54f95`, `B-5a51a`, `B-5a5db`, `B-5b8ad`, `B-5e050`, `B-618bf`, `B-624f0`, `B-640a5`, `B-650cd`, `B-6b940`, `B-6c681`, `B-6dcb2`, `B-70d40`, `B-71016`, `B-735c5`, `B-73c62`, `B-73c82`, `B-73c8e`, `B-741d8`, `B-7d5a9`, `B-7d738`, `B-801bc`, `B-8275a`, `B-82ac2`, `B-83d5c`, `B-854c6`, `B-860b5`, `B-86dad`, `B-878e9`, `B-87ab2`, `B-889cc`, `B-897c2`, `B-8b0df`, `B-8c110`, `B-8c528`, `B-8d1e7`, `B-93b90`, `B-95032`, `B-96cf8`, `B-96f94`, `B-9ad6c`, `B-9b64b`, `B-9c4ae`, `B-9d4e5`, `B-a2dc8`, `B-a3e85`, `B-a57bf`, `B-a8ca1`, `B-a91a7`, `B-aa6d8`, `B-afa22`, `B-b2abc`, `B-b4394`, `B-b71b6`, `B-b9ecc`, `B-ba568`, `B-bb50c`, `B-bffc8`, `B-c42ef`, `B-c6895`, `B-c8596`, `B-c8f6e`, `B-cc774`, `B-cd6ed`, `B-ceb11`, `B-d0011`, `B-d406a`, `B-d63fc`, `B-d81ad`, `B-d8b02`, `B-d8efb`, `B-dd4de`, `B-e36df`, `B-e447a`, `B-e564f`, `B-e6883`, `B-e7cd9`, `B-e8267`, `B-e9cef`, `B-ea268`, `B-ee42f`, `B-ee6e8`, `B-ef7dd`, `B-f1c7e`, `B-f36a9`, `B-f91bd`, `B-f9bde`, `B-f9e33`, `B-fc3d7`

**S-42da** — real 50/156; decoy 14/39.

`B-07b4a`, `B-0fdc2`, `B-101d3`, `B-1a812`, `B-211ec`, `B-22bed`, `B-24490`, `B-2471f`, `B-252ea`, `B-254cd`, `B-30ebc`, `B-33348`, `B-38426`, `B-3afc4`, `B-3fe44`, `B-449f5`, `B-49c25`, `B-51f20`, `B-527c5`, `B-54ce8`, `B-5c387`, `B-65668`, `B-66e5f`, `B-69ab9`, `B-6c065`, `B-70bed`, `B-7c5eb`, `B-86af7`, `B-89351`, `B-8d454`, `B-8fd45`, `B-90abb`, `B-9187a`, `B-9a3a3`, `B-9ae51`, `B-9b19f`, `B-9fd4f`, `B-a4f1b`, `B-a5ee0`, `B-ae255`, `B-ae853`, `B-b16c4`, `B-b2a27`, `B-b4541`, `B-b6d9e`, `B-c1596`, `B-c8b15`, `B-cdc61`, `B-d0868`, `B-d2afa`, `B-d3f50`, `B-da8f4`, `B-dab4b`, `B-e2996`, `B-e414d`, `B-e4c57`, `B-eab5d`, `B-ed71e`, `B-f1833`, `B-f4211`, `B-f76c9`, `B-f7b0f`, `B-f9c8d`, `B-ffdec`

**S-43be** — real 121/168; decoy 30/42.

`B-00b3b`, `B-01ebf`, `B-04b00`, `B-04c24`, `B-05951`, `B-06105`, `B-0823f`, `B-092c7`, `B-0c22d`, `B-0f217`, `B-134f2`, `B-135c9`, `B-14d16`, `B-17879`, `B-186bd`, `B-1a132`, `B-1b936`, `B-1c36c`, `B-1d01d`, `B-1e70f`, `B-1ef69`, `B-1fdda`, `B-20b25`, `B-244e5`, `B-2a09c`, `B-2af22`, `B-2bbc1`, `B-2ce03`, `B-2e045`, `B-2ec63`, `B-2f521`, `B-31ce1`, `B-32d09`, `B-3304b`, `B-37988`, `B-3a33d`, `B-3be14`, `B-3e416`, `B-40101`, `B-423b3`, `B-428fe`, `B-443d6`, `B-44edc`, `B-451c6`, `B-45385`, `B-47b02`, `B-483be`, `B-4881d`, `B-4aa62`, `B-4ab51`, `B-4afd0`, `B-4b4fc`, `B-4bbcc`, `B-4c8d8`, `B-4d0f1`, `B-4f57d`, `B-52bd6`, `B-56862`, `B-57f97`, `B-5934b`, `B-5946a`, `B-5c0dd`, `B-5e0bc`, `B-5e9ca`, `B-64327`, `B-64339`, `B-6694c`, `B-66ce2`, `B-66e04`, `B-684e0`, `B-6d2da`, `B-6eea0`, `B-70aff`, `B-710cc`, `B-71de6`, `B-747e2`, `B-74a7e`, `B-754d0`, `B-75e06`, `B-790ad`, `B-79135`, `B-795f6`, `B-7978c`, `B-7c576`, `B-7ee2e`, `B-7ef13`, `B-80e3c`, `B-815ff`, `B-8241f`, `B-83b29`, `B-83f31`, `B-8528e`, `B-86c72`, `B-8ea44`, `B-8f4ae`, `B-904a9`, `B-92f5f`, `B-939f6`, `B-93de6`, `B-966e8`, `B-98f89`, `B-99a45`, `B-99f64`, `B-9cf8d`, `B-9e044`, `B-9ee7c`, `B-a20b4`, `B-a2c07`, `B-a3053`, `B-a4187`, `B-a9804`, `B-acf1f`, `B-b0cb9`, `B-b21ef`, `B-b32da`, `B-b9a07`, `B-c1031`, `B-c25fb`, `B-c4a8d`, `B-c682c`, `B-cb167`, `B-cce53`, `B-cd8cd`, `B-ceea9`, `B-cfd49`, `B-d0096`, `B-d10e0`, `B-d175e`, `B-d3b5f`, `B-d5804`, `B-d8905`, `B-d92d6`, `B-dfc11`, `B-e129e`, `B-e36fe`, `B-e5a69`, `B-e70a1`, `B-e7c75`, `B-e7f21`, `B-e9728`, `B-ebf58`, `B-f0125`, `B-f16eb`, `B-f324b`, `B-f716e`, `B-fa2b7`, `B-fa521`, `B-fb3e9`, `B-fb83f`, `B-fd402`, `B-ffb54`

**S-4b1f** — real 90/170; decoy 18/42.

`B-02905`, `B-02c96`, `B-0411d`, `B-055e6`, `B-07506`, `B-078f5`, `B-0949e`, `B-095aa`, `B-0eef1`, `B-10b18`, `B-12144`, `B-22138`, `B-28838`, `B-2a4ed`, `B-2dda5`, `B-32d26`, `B-34eb0`, `B-357bb`, `B-36a3a`, `B-3b497`, `B-3bee3`, `B-3c916`, `B-3e205`, `B-3e8e7`, `B-3f66e`, `B-3fb48`, `B-40b3e`, `B-4b462`, `B-4d781`, `B-53a7c`, `B-54694`, `B-55b57`, `B-5658b`, `B-57d03`, `B-59905`, `B-5a924`, `B-5ad62`, `B-5e402`, `B-5e73b`, `B-66f32`, `B-6efad`, `B-70976`, `B-71d80`, `B-71f97`, `B-727b1`, `B-7711a`, `B-78959`, `B-7c0c2`, `B-7da40`, `B-84fde`, `B-8688e`, `B-8833d`, `B-88ad4`, `B-8e64a`, `B-90ae5`, `B-91dff`, `B-93c99`, `B-94f0d`, `B-9a25f`, `B-9b1bb`, `B-9c445`, `B-9e887`, `B-a3682`, `B-a5c67`, `B-a78ef`, `B-acf1e`, `B-ad8f3`, `B-aff17`, `B-b332c`, `B-b4f03`, `B-b6265`, `B-b72b4`, `B-b7f4c`, `B-b8f00`, `B-b92ab`, `B-bbfb4`, `B-be253`, `B-be72b`, `B-beb0d`, `B-bebd6`, `B-bfb6e`, `B-c3e3d`, `B-c8478`, `B-ca3ad`, `B-caafb`, `B-ce0bf`, `B-ceb56`, `B-d6a3c`, `B-d6f94`, `B-d7a33`, `B-da7f8`, `B-dbb65`, `B-dc09e`, `B-e0825`, `B-e0f3f`, `B-e60fb`, `B-e63f8`, `B-ea9be`, `B-ebad9`, `B-ef47b`, `B-f103b`, `B-f1ca3`, `B-f3940`, `B-f4572`, `B-f4cd6`, `B-fb87e`, `B-fe248`, `B-ff4a8`

**S-50ea** — real 80/162; decoy 19/40.

`B-004b0`, `B-00d31`, `B-017c4`, `B-06328`, `B-0cdb4`, `B-0cf04`, `B-0db7c`, `B-0f52c`, `B-11389`, `B-14243`, `B-173cc`, `B-1bbf7`, `B-1c9dd`, `B-1f620`, `B-208f2`, `B-20e04`, `B-210d3`, `B-24ee5`, `B-27862`, `B-280bf`, `B-2abfc`, `B-2bdb0`, `B-2cf5d`, `B-2d24b`, `B-2f2e0`, `B-32936`, `B-35f6f`, `B-38f88`, `B-39476`, `B-3f3ec`, `B-3fb97`, `B-40de2`, `B-4731b`, `B-4798f`, `B-4aaa5`, `B-4b6e4`, `B-4c430`, `B-502a3`, `B-51aaa`, `B-51d38`, `B-520a8`, `B-52cee`, `B-54096`, `B-5737d`, `B-5a40a`, `B-60fc5`, `B-61fd3`, `B-6577a`, `B-68252`, `B-69ba4`, `B-6abe7`, `B-6e77c`, `B-6e8ba`, `B-70267`, `B-743a2`, `B-771d6`, `B-7870e`, `B-78ee0`, `B-79011`, `B-7f29a`, `B-81bba`, `B-849e9`, `B-850d8`, `B-89108`, `B-8d17c`, `B-8e01f`, `B-909e5`, `B-91aa0`, `B-93297`, `B-975ca`, `B-985bf`, `B-99856`, `B-9e9a6`, `B-a0c02`, `B-a2f95`, `B-a35ba`, `B-a4b5c`, `B-a983c`, `B-abb70`, `B-b3fbb`, `B-b40ac`, `B-b511a`, `B-b6420`, `B-beeec`, `B-c533e`, `B-dd9c4`, `B-dfc0a`, `B-e011b`, `B-e0808`, `B-e60ac`, `B-ead88`, `B-eb502`, `B-ec5cf`, `B-eedba`, `B-ef37b`, `B-f7331`, `B-f8fb0`, `B-f95f0`, `B-fd099`

**S-5af2** — real 66/126; decoy 18/30.

`B-00ae5`, `B-0140f`, `B-01430`, `B-019ec`, `B-028ce`, `B-04b9b`, `B-0bfac`, `B-0ce94`, `B-0d0fa`, `B-0e368`, `B-11b45`, `B-1d43b`, `B-1f4e8`, `B-22256`, `B-26c3b`, `B-2938a`, `B-2de7f`, `B-30f91`, `B-380b4`, `B-3a25e`, `B-3b00d`, `B-3bf39`, `B-3c469`, `B-3d574`, `B-43ac5`, `B-43e33`, `B-456d2`, `B-46ce7`, `B-48077`, `B-4b68b`, `B-5183b`, `B-54652`, `B-5498f`, `B-639ed`, `B-64daa`, `B-69a0f`, `B-6bc0e`, `B-6c377`, `B-6e3a7`, `B-6ecd8`, `B-6ff34`, `B-702c9`, `B-71f13`, `B-735c2`, `B-75cb4`, `B-79069`, `B-7d105`, `B-7dcac`, `B-8d35e`, `B-8e545`, `B-92000`, `B-93e7c`, `B-944b7`, `B-98441`, `B-99c61`, `B-9e861`, `B-a6935`, `B-af6a8`, `B-afe3c`, `B-b6abd`, `B-b8a07`, `B-bcf8c`, `B-bd03c`, `B-befe2`, `B-c01e3`, `B-c453d`, `B-c6a0b`, `B-cbdb6`, `B-cc103`, `B-cd357`, `B-cfcdd`, `B-d5f2c`, `B-d887f`, `B-e1708`, `B-e1b69`, `B-e1d3a`, `B-e460e`, `B-ea2d3`, `B-f85c3`, `B-f864a`, `B-fad6a`, `B-fb4fa`, `B-fccab`, `B-ffd5e`

**S-60d7** — real 72/156; decoy 20/39.

`B-01308`, `B-014a6`, `B-02d5e`, `B-03440`, `B-04aad`, `B-050b5`, `B-057cd`, `B-09351`, `B-09e6e`, `B-169bc`, `B-1c35c`, `B-25b8a`, `B-275fd`, `B-2bff1`, `B-2c789`, `B-2eed2`, `B-34e15`, `B-37bc7`, `B-3aeb1`, `B-3c2a6`, `B-48a6c`, `B-4b235`, `B-4eb43`, `B-53aa2`, `B-53f53`, `B-588f9`, `B-5baf6`, `B-6006b`, `B-623ae`, `B-62f6c`, `B-681d5`, `B-6a096`, `B-6b58b`, `B-6db86`, `B-6e9c1`, `B-7189b`, `B-7381c`, `B-742e0`, `B-75161`, `B-75f51`, `B-79574`, `B-818c4`, `B-8204a`, `B-85515`, `B-86290`, `B-8705d`, `B-8eee3`, `B-8f928`, `B-90706`, `B-90b82`, `B-90ef9`, `B-93607`, `B-93a5d`, `B-93aef`, `B-94cf5`, `B-9d42c`, `B-a3534`, `B-a5108`, `B-a53d7`, `B-b28d3`, `B-b2f5c`, `B-b4e8c`, `B-b6363`, `B-b6eea`, `B-b8c2d`, `B-b8e1c`, `B-ba1a2`, `B-bb454`, `B-bcbb1`, `B-be187`, `B-c7da3`, `B-ce2c1`, `B-d2d7a`, `B-d2eb1`, `B-d3a4f`, `B-d48d0`, `B-dd83e`, `B-de554`, `B-dfc4e`, `B-e2390`, `B-e360c`, `B-e3df1`, `B-e45db`, `B-e7593`, `B-eb694`, `B-ec309`, `B-f4177`, `B-f42b1`, `B-f43d3`, `B-f537b`, `B-f9ada`, `B-fbfdb`

**S-653b** — real 105/134; decoy 28/34.

`B-03917`, `B-039e7`, `B-0499d`, `B-0660d`, `B-07213`, `B-0a611`, `B-0b73b`, `B-0bab4`, `B-0dd63`, `B-0e5d6`, `B-0eb38`, `B-0edba`, `B-0f158`, `B-0f5a1`, `B-1324a`, `B-142c3`, `B-15012`, `B-178af`, `B-1d092`, `B-1ecc1`, `B-21679`, `B-22cc6`, `B-23b53`, `B-2493a`, `B-259e5`, `B-26b88`, `B-2877d`, `B-2a6db`, `B-2a70f`, `B-2c5f6`, `B-2e215`, `B-2f4f4`, `B-2fb99`, `B-3041f`, `B-31de2`, `B-33292`, `B-3380a`, `B-33835`, `B-33bdb`, `B-33c77`, `B-35faa`, `B-3e1c4`, `B-400d1`, `B-41150`, `B-437f3`, `B-47717`, `B-4a6b6`, `B-4dec9`, `B-5236a`, `B-53589`, `B-558d8`, `B-5641e`, `B-590d9`, `B-59cd2`, `B-5b01c`, `B-5bd12`, `B-5f056`, `B-60159`, `B-616fb`, `B-644d5`, `B-6598c`, `B-69724`, `B-69926`, `B-69bff`, `B-6b5f7`, `B-6bb83`, `B-6d57a`, `B-744ec`, `B-74b2e`, `B-7502a`, `B-759c1`, `B-78f54`, `B-79d64`, `B-8243a`, `B-8275d`, `B-85d03`, `B-87600`, `B-8c263`, `B-8c930`, `B-8d7ac`, `B-94cc4`, `B-96ab6`, `B-96af4`, `B-97cb9`, `B-9a593`, `B-a04a5`, `B-a19fb`, `B-a56bb`, `B-a7bbd`, `B-a8697`, `B-aaef3`, `B-b0778`, `B-b1973`, `B-b360e`, `B-b3df5`, `B-b501e`, `B-b83cd`, `B-bbd35`, `B-be00e`, `B-bf0c5`, `B-c0dc7`, `B-c14aa`, `B-c19fa`, `B-c1a67`, `B-c5953`, `B-c7157`, `B-c853e`, `B-c935f`, `B-cced1`, `B-d2aab`, `B-da5e7`, `B-da659`, `B-dc5ae`, `B-ddf48`, `B-de6c4`, `B-de837`, `B-dfe8c`, `B-e0b8d`, `B-e0c05`, `B-e2989`, `B-e4bff`, `B-e5126`, `B-e877c`, `B-e8c15`, `B-ea1a7`, `B-eb750`, `B-ebdd0`, `B-ec602`, `B-f099d`, `B-f19bb`, `B-fb9e8`, `B-fd4e4`, `B-fe953`

**S-65fb** — real 79/152; decoy 15/38.

`B-03b2c`, `B-062b7`, `B-07b60`, `B-08937`, `B-08955`, `B-09873`, `B-0b524`, `B-0dd56`, `B-0e0d7`, `B-105fc`, `B-136b3`, `B-181a4`, `B-1c9b4`, `B-1fada`, `B-20459`, `B-2286d`, `B-23719`, `B-23a0d`, `B-24481`, `B-29466`, `B-29a51`, `B-31ae5`, `B-3444b`, `B-35a02`, `B-3944a`, `B-4311c`, `B-43db1`, `B-44a45`, `B-46e66`, `B-47412`, `B-489bf`, `B-4d7fb`, `B-50006`, `B-52334`, `B-52c93`, `B-5768d`, `B-5ab38`, `B-5dd8d`, `B-60ab7`, `B-625a9`, `B-66702`, `B-686d0`, `B-6a342`, `B-706d2`, `B-74f05`, `B-7838c`, `B-7d2e1`, `B-80e06`, `B-81027`, `B-831fc`, `B-83cc1`, `B-84c75`, `B-85619`, `B-85f40`, `B-88f22`, `B-8af8d`, `B-8b3e5`, `B-8c38c`, `B-8e9fb`, `B-8fe18`, `B-93c26`, `B-93f95`, `B-971e4`, `B-97896`, `B-98ef5`, `B-9cc74`, `B-9d708`, `B-9dc36`, `B-a1fbd`, `B-a3662`, `B-a4a0d`, `B-a6693`, `B-b433c`, `B-bb04a`, `B-c020d`, `B-c1076`, `B-c3fd6`, `B-caa53`, `B-cc0c7`, `B-ccf4c`, `B-cf0ad`, `B-cfc9c`, `B-d1414`, `B-d281c`, `B-d40d4`, `B-d5537`, `B-da06c`, `B-db99c`, `B-dca06`, `B-e2497`, `B-e7fed`, `B-eacf3`, `B-eb077`, `B-f5d84`

**S-660f** — real 135/158; decoy 35/41.

`B-0031b`, `B-091c6`, `B-09ed3`, `B-0b2e3`, `B-0da50`, `B-0dbe6`, `B-0e906`, `B-0f8e7`, `B-0faa0`, `B-11115`, `B-11f6f`, `B-17e27`, `B-17f35`, `B-18e84`, `B-191bc`, `B-19b54`, `B-1bd5e`, `B-1cd95`, `B-1d334`, `B-1ed53`, `B-20dac`, `B-223a3`, `B-23db2`, `B-24b4e`, `B-2adfc`, `B-2bab2`, `B-2bfa7`, `B-2ccd4`, `B-2edb7`, `B-33494`, `B-3589a`, `B-35c28`, `B-36298`, `B-36688`, `B-37567`, `B-3941a`, `B-3d308`, `B-3f57a`, `B-40369`, `B-40800`, `B-40ac1`, `B-415ae`, `B-426eb`, `B-42d11`, `B-47306`, `B-49458`, `B-49872`, `B-4b06e`, `B-4f599`, `B-4ff4a`, `B-51b44`, `B-52ad1`, `B-55b14`, `B-56a36`, `B-57831`, `B-5846e`, `B-5851d`, `B-59356`, `B-5cf0e`, `B-5fc42`, `B-61024`, `B-62ac7`, `B-62cf0`, `B-63b9c`, `B-65eda`, `B-6615d`, `B-663aa`, `B-68b13`, `B-69599`, `B-6ae99`, `B-6b759`, `B-6b886`, `B-6d724`, `B-6df84`, `B-6f6fd`, `B-730d9`, `B-75f58`, `B-76310`, `B-7734e`, `B-78d69`, `B-7aa92`, `B-7bfbe`, `B-7c59b`, `B-7ced7`, `B-80401`, `B-815fb`, `B-82784`, `B-8518b`, `B-89068`, `B-89c5a`, `B-8a16d`, `B-8ab06`, `B-8b57c`, `B-8b9ee`, `B-8cecf`, `B-8f434`, `B-94d10`, `B-97eb7`, `B-9a21e`, `B-9f79c`, `B-a3db5`, `B-a4a89`, `B-a67a7`, `B-a6e90`, `B-a722a`, `B-a7350`, `B-a8c14`, `B-a9413`, `B-aa35d`, `B-aac39`, `B-ac6b3`, `B-ad9c1`, `B-b0dfa`, `B-b14b2`, `B-b29ec`, `B-b5699`, `B-b58db`, `B-b6a5a`, `B-b9250`, `B-ba59c`, `B-ba732`, `B-baf35`, `B-bd7d5`, `B-bea8a`, `B-c09ca`, `B-c1d14`, `B-c2633`, `B-c3dc5`, `B-c5ac4`, `B-c7378`, `B-c8280`, `B-cadb6`, `B-cde26`, `B-ce713`, `B-cfc33`, `B-d0aba`, `B-d1766`, `B-d468f`, `B-d4ea3`, `B-d6268`, `B-d63bc`, `B-d6778`, `B-daa70`, `B-dbb26`, `B-dc73c`, `B-dca62`, `B-dcddb`, `B-dd23b`, `B-dff98`, `B-e0c80`, `B-e1375`, `B-e243b`, `B-e47b9`, `B-e6fe6`, `B-e8ddb`, `B-e9277`, `B-e9f79`, `B-eb4c2`, `B-ef6cd`, `B-ef9c8`, `B-f1383`, `B-f2908`, `B-f2a20`, `B-f306e`, `B-f43c8`, `B-f5938`, `B-f90bf`, `B-f9472`, `B-fa673`, `B-fd966`

**S-674f** — real 83/138; decoy 18/34.

`B-00b89`, `B-05dcb`, `B-066dc`, `B-082e9`, `B-0aecf`, `B-0b298`, `B-11bc4`, `B-1278c`, `B-183e4`, `B-19ce2`, `B-1ad88`, `B-1c79d`, `B-1f9ee`, `B-2063e`, `B-21f77`, `B-27d79`, `B-2a9cd`, `B-2b30e`, `B-2e559`, `B-3069a`, `B-30c20`, `B-3103b`, `B-34b60`, `B-351eb`, `B-35201`, `B-39b8d`, `B-418f7`, `B-41c4f`, `B-4b49a`, `B-4cbcb`, `B-51a0c`, `B-521b5`, `B-522c7`, `B-55753`, `B-55817`, `B-59869`, `B-5d7a1`, `B-5e1b2`, `B-5f089`, `B-654b4`, `B-69066`, `B-69b6d`, `B-72557`, `B-776f8`, `B-787f1`, `B-83a9f`, `B-84426`, `B-85315`, `B-874c7`, `B-889a2`, `B-8b82b`, `B-9442f`, `B-97c73`, `B-9a083`, `B-9c04b`, `B-9cf5b`, `B-9ea4b`, `B-9f451`, `B-a14e4`, `B-a3b9e`, `B-a63d6`, `B-a65d0`, `B-ab1e5`, `B-ae7fd`, `B-affea`, `B-b145b`, `B-b1bd9`, `B-b2748`, `B-bbec6`, `B-bc254`, `B-be615`, `B-bf0f2`, `B-c1ac7`, `B-c8c8a`, `B-cd937`, `B-d1f23`, `B-d5b06`, `B-d5fae`, `B-d8ea2`, `B-da846`, `B-dcd92`, `B-e0a39`, `B-e14bc`, `B-e282f`, `B-e5be8`, `B-e6832`, `B-e6a33`, `B-e967a`, `B-ea095`, `B-ea187`, `B-ea2d1`, `B-ec042`, `B-ecf0c`, `B-ed330`, `B-ed4d7`, `B-ee9da`, `B-eea7f`, `B-efd12`, `B-fbcb1`, `B-fe8c6`, `B-ff0d1`

**S-6a6d** — real 76/201; decoy 19/50.

`B-0181f`, `B-019e5`, `B-02b42`, `B-067b8`, `B-0e426`, `B-0f019`, `B-1288c`, `B-161d5`, `B-161f4`, `B-1650d`, `B-16779`, `B-16bf8`, `B-19e68`, `B-1add3`, `B-1ee03`, `B-1efcf`, `B-1fd4a`, `B-20646`, `B-210c6`, `B-2439f`, `B-31294`, `B-349ed`, `B-3870e`, `B-3c053`, `B-3c3f1`, `B-3d568`, `B-3dc82`, `B-3f56e`, `B-419b6`, `B-44cb6`, `B-47cdf`, `B-480e7`, `B-48592`, `B-4df43`, `B-538a7`, `B-554e9`, `B-5634d`, `B-57cf1`, `B-59e19`, `B-5af7f`, `B-5b0f2`, `B-5b7d1`, `B-5b83b`, `B-5d9a0`, `B-60a42`, `B-637b0`, `B-68faa`, `B-6b847`, `B-6dd80`, `B-6e384`, `B-6f13f`, `B-76a91`, `B-78f32`, `B-7b41d`, `B-80dd8`, `B-8200e`, `B-828b4`, `B-85425`, `B-866cf`, `B-8e8d8`, `B-922c6`, `B-944f8`, `B-95a49`, `B-985d3`, `B-9ad5f`, `B-9b051`, `B-9b6ed`, `B-9edb9`, `B-a2e24`, `B-a5526`, `B-a7b0b`, `B-aa704`, `B-aa8e1`, `B-acca3`, `B-ad2f9`, `B-aecf7`, `B-b00cb`, `B-b5a73`, `B-b5d1c`, `B-b677f`, `B-bea04`, `B-c0442`, `B-c1483`, `B-c3fa3`, `B-cfa39`, `B-d2b68`, `B-d56e2`, `B-d7db6`, `B-dbcd1`, `B-dcc50`, `B-dda0c`, `B-e3436`, `B-ec26f`, `B-f86ad`, `B-fcee1`

**S-6f0b** — real 130/160; decoy 32/40.

`B-000b9`, `B-000c8`, `B-00c59`, `B-0144d`, `B-01cac`, `B-083d8`, `B-0926f`, `B-092fc`, `B-0b2d4`, `B-0e123`, `B-1013e`, `B-10481`, `B-111e7`, `B-11e31`, `B-1560d`, `B-15aa0`, `B-15f85`, `B-17814`, `B-1da66`, `B-1f220`, `B-20e54`, `B-21f16`, `B-2399f`, `B-26b4b`, `B-26bf9`, `B-270f3`, `B-27879`, `B-27c67`, `B-29ba1`, `B-2a81d`, `B-2c239`, `B-2e4f7`, `B-2f77a`, `B-2f9f2`, `B-3092b`, `B-3374b`, `B-338af`, `B-367d3`, `B-3706f`, `B-38d91`, `B-3be05`, `B-3cad6`, `B-40382`, `B-417e0`, `B-4333b`, `B-448e0`, `B-4546b`, `B-45ba3`, `B-45f35`, `B-467d3`, `B-473d5`, `B-49b11`, `B-4a9af`, `B-4d384`, `B-4f042`, `B-506e7`, `B-51ff4`, `B-52e31`, `B-53018`, `B-5399e`, `B-554b1`, `B-562e4`, `B-5936a`, `B-59535`, `B-5992b`, `B-59ce3`, `B-5deb6`, `B-5e472`, `B-5ebe4`, `B-5f86f`, `B-5fae7`, `B-611c9`, `B-63804`, `B-638af`, `B-64028`, `B-6570f`, `B-6646f`, `B-664a1`, `B-664dc`, `B-67598`, `B-68cda`, `B-6bb04`, `B-6ea14`, `B-71e15`, `B-7281a`, `B-75e77`, `B-77af7`, `B-77f13`, `B-7bf21`, `B-7ce92`, `B-81025`, `B-82f8a`, `B-855f9`, `B-86125`, `B-8656c`, `B-87a5b`, `B-8a8a5`, `B-8c757`, `B-8d0fa`, `B-8f685`, `B-8fd02`, `B-94aec`, `B-94c97`, `B-95596`, `B-98761`, `B-9927f`, `B-9ab0c`, `B-9d85b`, `B-a09e6`, `B-a0fa1`, `B-a39bf`, `B-a3c2f`, `B-a7037`, `B-aacb4`, `B-ab32f`, `B-ae63d`, `B-aee48`, `B-aee52`, `B-b0f15`, `B-b1640`, `B-b1757`, `B-b2034`, `B-b81fa`, `B-ba149`, `B-bb56d`, `B-bc46d`, `B-bf95e`, `B-c01a6`, `B-c1f55`, `B-c6440`, `B-c6c10`, `B-c8e68`, `B-ca4da`, `B-ca672`, `B-caff5`, `B-cb9d7`, `B-cc03c`, `B-cc0dd`, `B-cfcda`, `B-d0693`, `B-d0d47`, `B-d3089`, `B-d4946`, `B-d543b`, `B-d6d04`, `B-dc0af`, `B-dcfa0`, `B-ddc97`, `B-e3328`, `B-e41d7`, `B-e7aed`, `B-e88ec`, `B-ee6fd`, `B-ef423`, `B-f3fb5`, `B-f54f5`, `B-f56ca`, `B-f6295`, `B-f69f1`, `B-f875f`, `B-f9474`, `B-fc0cc`

**S-73d4** — real 139/197; decoy 26/49.

`B-02038`, `B-03e65`, `B-060b6`, `B-08537`, `B-0a063`, `B-0cda5`, `B-0d571`, `B-0d7f0`, `B-0ee9c`, `B-10693`, `B-10945`, `B-10a38`, `B-12c38`, `B-1afc3`, `B-1c087`, `B-1c996`, `B-1d45c`, `B-1fbf1`, `B-22aa1`, `B-293a0`, `B-29861`, `B-2bf87`, `B-2cf47`, `B-2d8d5`, `B-2f433`, `B-2f45d`, `B-30e64`, `B-334f7`, `B-335a3`, `B-3498e`, `B-353b0`, `B-373d2`, `B-39575`, `B-3de3d`, `B-3f952`, `B-41ab8`, `B-43a80`, `B-4469f`, `B-44b32`, `B-44b80`, `B-45a6b`, `B-4992b`, `B-4a6d4`, `B-4ad58`, `B-4b906`, `B-4ce71`, `B-4d13e`, `B-4dc8e`, `B-4f284`, `B-4fc6f`, `B-57797`, `B-5b29f`, `B-5dd5e`, `B-63d01`, `B-6659c`, `B-66c39`, `B-66c6c`, `B-67881`, `B-68437`, `B-6b11e`, `B-7395a`, `B-76296`, `B-776ea`, `B-77e52`, `B-7b58e`, `B-7c33b`, `B-7dfbd`, `B-7ef1e`, `B-7f77b`, `B-7fd6e`, `B-800c3`, `B-8119a`, `B-811e3`, `B-81ad5`, `B-82129`, `B-829e5`, `B-8350b`, `B-848dc`, `B-85b15`, `B-874e4`, `B-87ab7`, `B-89281`, `B-8c8fd`, `B-8d5a2`, `B-90a82`, `B-9376c`, `B-93e5f`, `B-94337`, `B-955b6`, `B-99150`, `B-992af`, `B-9d74c`, `B-9d9a3`, `B-9e0c4`, `B-9e12d`, `B-9ec7b`, `B-a0d0b`, `B-a11c6`, `B-a37cc`, `B-a4cf2`, `B-a6e50`, `B-a7da6`, `B-a89ec`, `B-a97af`, `B-aa307`, `B-aa376`, `B-aa956`, `B-ab437`, `B-ab984`, `B-ad29d`, `B-ad96f`, `B-b0fc3`, `B-b33f8`, `B-b5e50`, `B-b651e`, `B-b6db0`, `B-b8a27`, `B-b918c`, `B-bba20`, `B-bf591`, `B-bf634`, `B-bffd0`, `B-c35ef`, `B-c3643`, `B-c4416`, `B-c4b26`, `B-c51f1`, `B-c5c5b`, `B-c6643`, `B-c69a0`, `B-c6fc2`, `B-c7e94`, `B-cad30`, `B-ce065`, `B-cf0a5`, `B-cf45a`, `B-cf652`, `B-cf9b3`, `B-d356e`, `B-d3683`, `B-d38c1`, `B-d6a4d`, `B-d7621`, `B-d8322`, `B-df83f`, `B-df8d1`, `B-e0b00`, `B-e18e1`, `B-e4934`, `B-e7451`, `B-eaeea`, `B-ec231`, `B-ec556`, `B-ec749`, `B-ef5e1`, `B-f447b`, `B-f4e66`, `B-f5544`, `B-f778a`, `B-f85e5`, `B-f9a7c`, `B-fb78c`, `B-feb24`, `B-ff602`, `B-ffe7e`

**S-7c00** — real 72/124; decoy 19/31.

`B-092a6`, `B-0eead`, `B-16b79`, `B-1c494`, `B-1f88f`, `B-23b22`, `B-2905c`, `B-29a74`, `B-2dd11`, `B-32c78`, `B-343b5`, `B-34bfd`, `B-36f7b`, `B-375a6`, `B-3989b`, `B-412c0`, `B-46a7d`, `B-5039b`, `B-50c5f`, `B-511ad`, `B-54fb5`, `B-56641`, `B-56add`, `B-58c7b`, `B-5e347`, `B-66dac`, `B-6892b`, `B-6f333`, `B-6f995`, `B-70f8a`, `B-74b2d`, `B-75f92`, `B-78224`, `B-7baa2`, `B-7fe29`, `B-804b3`, `B-8286f`, `B-838ad`, `B-83b6f`, `B-84cef`, `B-84cf5`, `B-85624`, `B-86de1`, `B-8bb8d`, `B-8d11b`, `B-8e331`, `B-945f6`, `B-99d37`, `B-9b454`, `B-9edd1`, `B-9f143`, `B-9f285`, `B-a022d`, `B-a4739`, `B-aa69d`, `B-ac6b4`, `B-adc5a`, `B-ade83`, `B-b2732`, `B-b33d2`, `B-b3d22`, `B-b4d5b`, `B-b83e2`, `B-b8cc7`, `B-ba033`, `B-c41a7`, `B-c4f88`, `B-c59d4`, `B-c5c19`, `B-c82f6`, `B-c87b9`, `B-c8cd4`, `B-cc998`, `B-d0f74`, `B-d2806`, `B-d318f`, `B-d67e1`, `B-d9249`, `B-dfd76`, `B-e0ec6`, `B-e1822`, `B-e43cc`, `B-e7fd0`, `B-e86ec`, `B-ea9ff`, `B-ee66a`, `B-ef09e`, `B-f1dba`, `B-f5d65`, `B-fcda4`, `B-ff416`

**S-80a2** — real 56/125; decoy 13/32.

`B-00c3d`, `B-010b0`, `B-0264e`, `B-09395`, `B-0b139`, `B-0bc86`, `B-0e341`, `B-12ab9`, `B-2101f`, `B-2628c`, `B-27ec3`, `B-2d11b`, `B-2e130`, `B-2ec67`, `B-34b24`, `B-35e38`, `B-3811c`, `B-383b2`, `B-3870d`, `B-427d2`, `B-4e683`, `B-4e7b6`, `B-56193`, `B-5a98e`, `B-6a35c`, `B-6d19a`, `B-6de38`, `B-7637e`, `B-76fb0`, `B-8ecde`, `B-90766`, `B-91603`, `B-99366`, `B-a00b2`, `B-a0a84`, `B-aa16b`, `B-ae53b`, `B-b129b`, `B-b1e4c`, `B-b1fb3`, `B-b9aea`, `B-bc1e0`, `B-be721`, `B-bfce4`, `B-c075a`, `B-c216c`, `B-c743a`, `B-c8a9f`, `B-cd37d`, `B-d02de`, `B-d1170`, `B-d2217`, `B-d5a92`, `B-d6985`, `B-d6c0b`, `B-df426`, `B-dfb77`, `B-e328a`, `B-e51ab`, `B-e6537`, `B-e6e14`, `B-ea091`, `B-eba0b`, `B-ef5bf`, `B-efcb1`, `B-f01c1`, `B-f08da`, `B-fda09`, `B-fe64d`

**S-8304** — real 121/164; decoy 31/40.

`B-00732`, `B-01b71`, `B-0222d`, `B-04803`, `B-05282`, `B-07b7e`, `B-09d47`, `B-0cd0a`, `B-0daeb`, `B-0feca`, `B-11997`, `B-11e3c`, `B-159af`, `B-16e4a`, `B-18717`, `B-18c7f`, `B-1bc05`, `B-1bea8`, `B-1bf5e`, `B-1dec7`, `B-1e9cb`, `B-2181d`, `B-22ce0`, `B-22f3e`, `B-270be`, `B-2c7b2`, `B-2cedc`, `B-2dc11`, `B-2fa69`, `B-31436`, `B-34d25`, `B-38e71`, `B-3a77c`, `B-3ab9a`, `B-3e582`, `B-3faa9`, `B-40b80`, `B-44aca`, `B-45e00`, `B-474b0`, `B-47ed9`, `B-485c8`, `B-48716`, `B-4c3ea`, `B-4c575`, `B-4cfc9`, `B-4e27c`, `B-4f21a`, `B-4facd`, `B-520a5`, `B-563a3`, `B-572d7`, `B-58bc3`, `B-5d00e`, `B-5d78e`, `B-5d7d5`, `B-5fafb`, `B-6370f`, `B-64b4c`, `B-65d58`, `B-672f1`, `B-6a4db`, `B-6a910`, `B-70274`, `B-70ca8`, `B-71206`, `B-71e6f`, `B-732e1`, `B-7539c`, `B-75db9`, `B-76914`, `B-7863c`, `B-80017`, `B-80153`, `B-80b8a`, `B-82119`, `B-84536`, `B-859c3`, `B-861c2`, `B-867da`, `B-87377`, `B-87784`, `B-8799d`, `B-87d0c`, `B-88687`, `B-8aa07`, `B-8c061`, `B-8c6e2`, `B-8c9f2`, `B-8ec33`, `B-8f830`, `B-90928`, `B-9508c`, `B-95d3e`, `B-9859e`, `B-9aa91`, `B-9c48f`, `B-9f54c`, `B-a1030`, `B-a18d6`, `B-a1d4c`, `B-a3528`, `B-a4523`, `B-a4b3b`, `B-a6035`, `B-a7498`, `B-a8f89`, `B-ac495`, `B-ac550`, `B-acbd9`, `B-aea77`, `B-aec20`, `B-af548`, `B-b082d`, `B-b33c7`, `B-b36b9`, `B-b3f39`, `B-b8b6e`, `B-be099`, `B-c3368`, `B-c5181`, `B-c6859`, `B-ca27a`, `B-ca44d`, `B-ccf44`, `B-cecea`, `B-d28ca`, `B-d32b4`, `B-d431d`, `B-d568d`, `B-d6466`, `B-d9802`, `B-e0573`, `B-e0cb9`, `B-e4454`, `B-e4d5a`, `B-e54e9`, `B-e8801`, `B-ecc44`, `B-ee6a9`, `B-ef259`, `B-ef5f3`, `B-f1b29`, `B-f3307`, `B-f674c`, `B-f7032`, `B-f790a`, `B-fa2c5`, `B-fa55a`, `B-fac1a`, `B-fb958`, `B-fe3e8`

**S-8334** — real 8/127; decoy 3/33.

`B-31238`, `B-3dcd2`, `B-4fbbf`, `B-76fd4`, `B-8b9cf`, `B-928ca`, `B-b2d1b`, `B-b71d2`, `B-dc4b3`, `B-e83a7`, `B-fb115`

**S-8534** — real 132/182; decoy 32/44.

`B-02814`, `B-050a1`, `B-05a19`, `B-0a6bd`, `B-0ddd1`, `B-0ec37`, `B-0f532`, `B-10cd5`, `B-1618c`, `B-17cf0`, `B-18d59`, `B-1b46e`, `B-1bc60`, `B-1ce3b`, `B-1f394`, `B-209eb`, `B-252f3`, `B-25740`, `B-26d15`, `B-2b560`, `B-2c469`, `B-30258`, `B-30af3`, `B-313dc`, `B-322e9`, `B-32ec8`, `B-3760b`, `B-37b53`, `B-382d2`, `B-3c53f`, `B-3df50`, `B-3e5a2`, `B-3ecc1`, `B-4145e`, `B-423c8`, `B-424f3`, `B-427f4`, `B-44de0`, `B-46b72`, `B-47757`, `B-48b65`, `B-498ff`, `B-4a02c`, `B-4b0af`, `B-4d0d1`, `B-4df73`, `B-532b1`, `B-54b34`, `B-5521a`, `B-553db`, `B-57706`, `B-5a556`, `B-5a71f`, `B-5c03b`, `B-5c905`, `B-5f5af`, `B-60f01`, `B-615d0`, `B-62ec6`, `B-67718`, `B-68564`, `B-6c51e`, `B-6d211`, `B-6e9be`, `B-6efdb`, `B-7005c`, `B-703cc`, `B-71f21`, `B-73b60`, `B-7437c`, `B-7acf0`, `B-7ad7c`, `B-7b6ab`, `B-7cdd2`, `B-7cfe7`, `B-7e9a1`, `B-80325`, `B-8060e`, `B-81e6b`, `B-83109`, `B-85776`, `B-86d72`, `B-8ab92`, `B-8b32c`, `B-8bd0f`, `B-8daf7`, `B-8e9da`, `B-8ee22`, `B-912ea`, `B-91e12`, `B-92df8`, `B-935e5`, `B-954ee`, `B-96033`, `B-96862`, `B-977d9`, `B-97e44`, `B-98290`, `B-98f5d`, `B-99c24`, `B-9a1b2`, `B-9ba74`, `B-9ddcd`, `B-a1ed3`, `B-a4585`, `B-a6697`, `B-a70fd`, `B-a8a9c`, `B-a8b35`, `B-a9734`, `B-aac13`, `B-aad3c`, `B-abefd`, `B-ac72b`, `B-ae579`, `B-aedf3`, `B-afa03`, `B-b17d3`, `B-b2dab`, `B-b3384`, `B-b38cd`, `B-b45f9`, `B-b7ddf`, `B-ba15d`, `B-bb4ff`, `B-bdbfc`, `B-bddab`, `B-c0987`, `B-c136b`, `B-c1748`, `B-c7e90`, `B-c84b4`, `B-c8cb7`, `B-cf502`, `B-d2b91`, `B-d41a4`, `B-d4bc6`, `B-d8ea6`, `B-dc27a`, `B-dc629`, `B-dc6ef`, `B-df107`, `B-df363`, `B-e0180`, `B-e3ec5`, `B-e5710`, `B-e71a7`, `B-e7df2`, `B-e81d1`, `B-e9384`, `B-ea147`, `B-ea8ec`, `B-ec2d5`, `B-ec55b`, `B-ec617`, `B-ec6b2`, `B-ecd7c`, `B-f0993`, `B-f50b8`, `B-f87d1`, `B-fb094`, `B-fd82e`, `B-fe58e`, `B-ffcf4`

**S-8714** — real 117/214; decoy 24/54.

`B-00526`, `B-014c7`, `B-047b2`, `B-0a905`, `B-0b660`, `B-0e60c`, `B-12da1`, `B-14c16`, `B-17f2f`, `B-18aa7`, `B-1aa15`, `B-1bc5f`, `B-1d2c8`, `B-1db11`, `B-1fdc4`, `B-2635f`, `B-2673a`, `B-2a735`, `B-2b691`, `B-2ff2d`, `B-31361`, `B-3362a`, `B-33733`, `B-34f39`, `B-3645b`, `B-37632`, `B-395e7`, `B-40466`, `B-44b93`, `B-45e6f`, `B-4604d`, `B-46862`, `B-47bb6`, `B-495ff`, `B-49657`, `B-49670`, `B-4ab03`, `B-50d12`, `B-5364e`, `B-5509e`, `B-56181`, `B-58ce0`, `B-5b3b0`, `B-5e667`, `B-5f25c`, `B-5f9df`, `B-610b3`, `B-63818`, `B-64e03`, `B-6a29f`, `B-6d51e`, `B-70dc0`, `B-717ef`, `B-74753`, `B-76361`, `B-77baf`, `B-7ac30`, `B-7b2a5`, `B-7c49a`, `B-7f307`, `B-7ffee`, `B-82d37`, `B-83dce`, `B-83f43`, `B-87c9b`, `B-89672`, `B-8a214`, `B-8c7f1`, `B-90129`, `B-904b8`, `B-9069a`, `B-91905`, `B-92f38`, `B-93e81`, `B-9614c`, `B-967b4`, `B-98ae8`, `B-9b75c`, `B-9b9ed`, `B-9dabb`, `B-a052f`, `B-a3c98`, `B-a759c`, `B-a76f1`, `B-a8716`, `B-a9036`, `B-ac289`, `B-acc05`, `B-ad45f`, `B-afb13`, `B-b1032`, `B-b48d6`, `B-b50d8`, `B-b7045`, `B-b760b`, `B-b8949`, `B-ba2fe`, `B-ba64e`, `B-bb145`, `B-be8b0`, `B-c0246`, `B-c0571`, `B-c1185`, `B-c4ad7`, `B-c58ee`, `B-c7758`, `B-c7baa`, `B-c83b4`, `B-c8e87`, `B-ca563`, `B-ccb71`, `B-ccc30`, `B-d0528`, `B-d32f6`, `B-d474d`, `B-d5778`, `B-d60b7`, `B-d8191`, `B-d8d4a`, `B-d9347`, `B-d9f36`, `B-db09e`, `B-df6c7`, `B-e1351`, `B-e16be`, `B-e30f9`, `B-e6525`, `B-e686b`, `B-e8023`, `B-e85a7`, `B-e96c2`, `B-ead2d`, `B-eb5dc`, `B-ecf4e`, `B-ed29d`, `B-f3842`, `B-f90e2`, `B-fbb3b`, `B-fc049`, `B-fc8e5`, `B-fc91f`

**S-9026** — real 106/180; decoy 24/46.

`B-02174`, `B-0444e`, `B-056dd`, `B-067ae`, `B-06a8f`, `B-0ae34`, `B-0cc05`, `B-0dc9a`, `B-0e40b`, `B-1209b`, `B-12829`, `B-13f03`, `B-163df`, `B-175a8`, `B-1be3e`, `B-1cc72`, `B-202ff`, `B-20da6`, `B-21106`, `B-29863`, `B-2a3e6`, `B-2ac36`, `B-2c2dc`, `B-31ba9`, `B-3438b`, `B-34c5e`, `B-3bef8`, `B-3d2e8`, `B-3f8a2`, `B-41316`, `B-41757`, `B-427ff`, `B-442b1`, `B-470d6`, `B-4d67b`, `B-4dc6b`, `B-4dd69`, `B-4ebcd`, `B-4fe86`, `B-50f58`, `B-520ce`, `B-53416`, `B-55b59`, `B-56344`, `B-57556`, `B-57ad9`, `B-5844a`, `B-58d2b`, `B-5a181`, `B-5bf3c`, `B-5c986`, `B-5cb74`, `B-5e190`, `B-5fb41`, `B-5ff5e`, `B-61851`, `B-62f9e`, `B-636a2`, `B-650c7`, `B-65a45`, `B-66df0`, `B-703b4`, `B-73dbe`, `B-75250`, `B-7609e`, `B-777ad`, `B-7b5e1`, `B-7c6a8`, `B-7e99e`, `B-7f983`, `B-84a94`, `B-84c79`, `B-86d15`, `B-87a05`, `B-87f04`, `B-894eb`, `B-89556`, `B-89d15`, `B-8a0b1`, `B-8b901`, `B-903e6`, `B-93de1`, `B-978f9`, `B-99355`, `B-9b8e2`, `B-9dc8c`, `B-a2de4`, `B-a5e8a`, `B-a91a8`, `B-a9345`, `B-aadc8`, `B-ac01f`, `B-acba1`, `B-b058e`, `B-b78b1`, `B-b7a2a`, `B-b8a0d`, `B-ba7df`, `B-bcc1b`, `B-be520`, `B-bec5f`, `B-c001a`, `B-c7b90`, `B-ccb22`, `B-cd0ab`, `B-cd7fc`, `B-cfb77`, `B-d20eb`, `B-d3080`, `B-d9aa4`, `B-de40e`, `B-de68f`, `B-e1e00`, `B-e1eb5`, `B-e8a7e`, `B-e9457`, `B-f06c6`, `B-f0774`, `B-f258c`, `B-f26f8`, `B-f30d6`, `B-f31ae`, `B-f35e9`, `B-f69e0`, `B-f7d67`, `B-f7efa`, `B-fa4b4`, `B-fd03a`, `B-fe66e`, `B-ff40b`

**S-96b7** — real 133/173; decoy 36/44.

`B-00c8e`, `B-018d2`, `B-06a81`, `B-070d1`, `B-0a32a`, `B-0e201`, `B-0f1be`, `B-0fa61`, `B-11500`, `B-11c36`, `B-1669f`, `B-16ce9`, `B-1702a`, `B-18222`, `B-18b15`, `B-1ae3f`, `B-1b417`, `B-22408`, `B-23831`, `B-24489`, `B-25233`, `B-29abf`, `B-2a1a1`, `B-2d5d0`, `B-2d914`, `B-2eec7`, `B-314b8`, `B-32ad6`, `B-33f6d`, `B-35d56`, `B-373a7`, `B-37581`, `B-39bbc`, `B-3a35e`, `B-3aaf8`, `B-3c7ac`, `B-3d8b7`, `B-3e078`, `B-3eff1`, `B-3fcd3`, `B-400fa`, `B-40806`, `B-43507`, `B-452be`, `B-45635`, `B-4a4a5`, `B-4c48b`, `B-4f758`, `B-51177`, `B-52fa5`, `B-564c8`, `B-56cab`, `B-58e01`, `B-591a8`, `B-5ae8e`, `B-5b711`, `B-5b7c5`, `B-5c23d`, `B-5f31c`, `B-5fe33`, `B-602fc`, `B-603c7`, `B-64b07`, `B-65b0b`, `B-65f79`, `B-66dd3`, `B-6825c`, `B-69426`, `B-6c69c`, `B-6cc90`, `B-6d6a7`, `B-6f763`, `B-6f97b`, `B-70727`, `B-70f97`, `B-72b48`, `B-7377a`, `B-742c6`, `B-765d2`, `B-773b6`, `B-78eb7`, `B-79a65`, `B-7a61f`, `B-7e39b`, `B-7e93c`, `B-850da`, `B-851a6`, `B-865ef`, `B-8708b`, `B-87d4e`, `B-8a5da`, `B-8a816`, `B-8ac46`, `B-8b074`, `B-8b18f`, `B-8b80c`, `B-8c042`, `B-8c655`, `B-8e87b`, `B-8ec2d`, `B-90b76`, `B-9116f`, `B-91170`, `B-928f6`, `B-928f8`, `B-9a211`, `B-9ba3a`, `B-9c54c`, `B-9e060`, `B-9e5c9`, `B-9f425`, `B-a1498`, `B-a22ba`, `B-a48bf`, `B-a695c`, `B-a7d96`, `B-a7f6e`, `B-aa8f3`, `B-abe54`, `B-abe85`, `B-afab9`, `B-b0abb`, `B-b669e`, `B-b7355`, `B-b7b52`, `B-b8690`, `B-bab95`, `B-baec1`, `B-bcdd5`, `B-c0dae`, `B-c2148`, `B-c248f`, `B-c38c7`, `B-c3b37`, `B-c8578`, `B-c9e04`, `B-caf31`, `B-cb56e`, `B-cc22a`, `B-d2436`, `B-d2f3c`, `B-d33f6`, `B-d713f`, `B-d89fe`, `B-d8fc7`, `B-db75f`, `B-dca02`, `B-dd58f`, `B-e008e`, `B-e33f8`, `B-e4003`, `B-e4733`, `B-e5876`, `B-e6e38`, `B-e72c1`, `B-e9892`, `B-ee950`, `B-eed15`, `B-ef995`, `B-f0dea`, `B-f408d`, `B-f4c9c`, `B-f73ce`, `B-f949c`, `B-fb152`, `B-fbb38`, `B-fc25b`, `B-fe0b9`, `B-fe778`

**S-a79c** — real 94/177; decoy 28/44.

`B-002e7`, `B-00531`, `B-00f80`, `B-02fac`, `B-0a217`, `B-0ea86`, `B-12361`, `B-1304a`, `B-14d11`, `B-164fe`, `B-17228`, `B-177fb`, `B-1f0d0`, `B-21425`, `B-25030`, `B-25efc`, `B-26e05`, `B-27384`, `B-2c06e`, `B-2ca49`, `B-2d863`, `B-2e043`, `B-2e79c`, `B-2f067`, `B-2f91c`, `B-3281f`, `B-3489f`, `B-358bb`, `B-372dd`, `B-38280`, `B-382be`, `B-3cca8`, `B-3cdf2`, `B-3d23f`, `B-4029a`, `B-40708`, `B-416b5`, `B-418de`, `B-439ca`, `B-44105`, `B-4598d`, `B-46341`, `B-46e5e`, `B-4aee2`, `B-4c2c9`, `B-53a36`, `B-592ae`, `B-5aa00`, `B-5dda9`, `B-60aee`, `B-62388`, `B-638fe`, `B-656a9`, `B-67d85`, `B-6b9e4`, `B-6bbe5`, `B-6c8a0`, `B-6c8a9`, `B-6d9ae`, `B-75a49`, `B-79350`, `B-7c503`, `B-83428`, `B-8584e`, `B-86c65`, `B-87d1d`, `B-90788`, `B-92d75`, `B-934eb`, `B-93bde`, `B-94a7d`, `B-97db7`, `B-984c6`, `B-98f8c`, `B-9bb01`, `B-a0593`, `B-a223f`, `B-a2472`, `B-a3bc6`, `B-a3d25`, `B-a3fee`, `B-a4d15`, `B-a9373`, `B-ac1ed`, `B-ad23e`, `B-b099e`, `B-b1720`, `B-bbbcf`, `B-be402`, `B-be874`, `B-bfe75`, `B-c1b0b`, `B-c4a03`, `B-c6aea`, `B-ccabf`, `B-cd06b`, `B-d04c9`, `B-d2f27`, `B-d3161`, `B-d5768`, `B-d5c00`, `B-d6052`, `B-d9f25`, `B-dcbaa`, `B-de4c7`, `B-df022`, `B-e0aed`, `B-e6b66`, `B-e9722`, `B-e9cc9`, `B-eb8f9`, `B-ed237`, `B-ee825`, `B-eeb48`, `B-f3173`, `B-f64e3`, `B-f9dd8`, `B-fa329`, `B-fc3a8`, `B-fca2d`, `B-fe68b`, `B-ffd26`

**S-af31** — real 42/222; decoy 8/55.

`B-01690`, `B-0bc1c`, `B-0e4b0`, `B-10ac5`, `B-1100c`, `B-29ff8`, `B-2c568`, `B-2d2f2`, `B-31b8c`, `B-3992b`, `B-3f184`, `B-43c55`, `B-44986`, `B-44fcf`, `B-4c28b`, `B-51cf4`, `B-5befa`, `B-5d747`, `B-60f61`, `B-64cbe`, `B-66234`, `B-6850f`, `B-6a521`, `B-6fd5b`, `B-7d380`, `B-8373c`, `B-83d6e`, `B-90db2`, `B-9d1e8`, `B-a4e4b`, `B-b5893`, `B-bba23`, `B-ce1b1`, `B-ce975`, `B-d628f`, `B-d9436`, `B-dbdf2`, `B-e149f`, `B-e4601`, `B-e5928`, `B-e6dcb`, `B-ea21a`, `B-ea6c0`, `B-ec9dd`, `B-ecb78`, `B-eddc9`, `B-ee92d`, `B-f0a45`, `B-f0c3f`, `B-fe8c3`

**S-b256** — real 123/139; decoy 29/34.

`B-00158`, `B-0049a`, `B-016b6`, `B-093d0`, `B-0a2e6`, `B-0b3eb`, `B-0c983`, `B-0cbd5`, `B-0cc08`, `B-0e316`, `B-0f75f`, `B-12fef`, `B-13890`, `B-147ff`, `B-173d5`, `B-1a63c`, `B-1d6fa`, `B-2223c`, `B-248c0`, `B-257db`, `B-26c9d`, `B-27bc5`, `B-285bf`, `B-2a2ba`, `B-2e10b`, `B-3179a`, `B-35dd8`, `B-35f82`, `B-37413`, `B-3aef0`, `B-3be02`, `B-3c40a`, `B-3e410`, `B-3e49e`, `B-4128f`, `B-41839`, `B-43c45`, `B-43f4b`, `B-44174`, `B-44549`, `B-45f26`, `B-46969`, `B-46ed2`, `B-47da0`, `B-480fa`, `B-4918e`, `B-491fd`, `B-4a570`, `B-4b2ce`, `B-4bad4`, `B-4f069`, `B-4f166`, `B-4f882`, `B-51719`, `B-521ce`, `B-53393`, `B-53d27`, `B-564f9`, `B-58b13`, `B-5c54c`, `B-5d4f8`, `B-5f121`, `B-5f669`, `B-5fba5`, `B-60756`, `B-60bda`, `B-62068`, `B-63312`, `B-6424b`, `B-6a518`, `B-6dbff`, `B-71a6a`, `B-72c3a`, `B-75c6c`, `B-76c87`, `B-78a35`, `B-7d67f`, `B-801d6`, `B-84d62`, `B-85001`, `B-85b6d`, `B-861c8`, `B-86e52`, `B-8767b`, `B-8ade2`, `B-9122b`, `B-95489`, `B-9718c`, `B-9932a`, `B-99be8`, `B-9aa86`, `B-a14a0`, `B-a6f36`, `B-a7d7c`, `B-aa911`, `B-ac859`, `B-aca9a`, `B-b008d`, `B-b0cc8`, `B-b14dd`, `B-b43fb`, `B-b791f`, `B-b9168`, `B-ba805`, `B-baa53`, `B-bbcad`, `B-bc1bd`, `B-bd927`, `B-be4c7`, `B-bec94`, `B-bf535`, `B-c52b4`, `B-c6fb0`, `B-c76ca`, `B-c9527`, `B-cc222`, `B-cd2f9`, `B-cf17c`, `B-d0720`, `B-d152c`, `B-d467a`, `B-d5a8f`, `B-d5f8b`, `B-d7137`, `B-d72cf`, `B-d7668`, `B-d8dd5`, `B-d905f`, `B-da427`, `B-da49e`, `B-db32d`, `B-db5ef`, `B-e1502`, `B-e1e7f`, `B-e229f`, `B-e59d9`, `B-ebc9c`, `B-ecd7f`, `B-ef0b7`, `B-f12b5`, `B-f2103`, `B-f37ac`, `B-f3dda`, `B-f4de5`, `B-f54ad`, `B-f6fac`, `B-f9608`, `B-faff1`, `B-fb937`, `B-fbbb3`, `B-fd0fc`, `B-fd66e`

**S-b555** — real 45/139; decoy 10/35.

`B-01ccc`, `B-064b6`, `B-0c359`, `B-0e339`, `B-12f09`, `B-19a82`, `B-1dfab`, `B-20b80`, `B-23494`, `B-24776`, `B-258e9`, `B-28e34`, `B-30283`, `B-31be3`, `B-36d30`, `B-38ce7`, `B-3a9de`, `B-3b68d`, `B-3d273`, `B-520cf`, `B-5ca30`, `B-73139`, `B-7328c`, `B-7783a`, `B-86b7c`, `B-8a86f`, `B-8b838`, `B-9092d`, `B-90ef3`, `B-90fa2`, `B-91d61`, `B-acaa0`, `B-afc87`, `B-b42da`, `B-b45b2`, `B-b4f59`, `B-b7926`, `B-bd44a`, `B-c11d3`, `B-cbf9b`, `B-cc4e8`, `B-cf8ec`, `B-d2183`, `B-d308a`, `B-d392f`, `B-d4836`, `B-da103`, `B-dbf73`, `B-e5e85`, `B-e9023`, `B-f0897`, `B-f1fd8`, `B-f38e2`, `B-f6246`, `B-fafe7`

**S-b6e5** — real 137/188; decoy 34/46.

`B-01624`, `B-029ea`, `B-0614a`, `B-09277`, `B-0a6d8`, `B-0c285`, `B-0dbe5`, `B-0f286`, `B-0fe45`, `B-1064b`, `B-16f37`, `B-18ddd`, `B-19a14`, `B-19fa0`, `B-1add5`, `B-1ddbe`, `B-1e396`, `B-1f940`, `B-21647`, `B-22c25`, `B-2372e`, `B-23a6b`, `B-26ede`, `B-285f2`, `B-2c46a`, `B-2eaf4`, `B-2ee6c`, `B-2f35c`, `B-3323a`, `B-350ff`, `B-36351`, `B-389b1`, `B-39a96`, `B-3bd28`, `B-3beea`, `B-3fc85`, `B-40367`, `B-40dbe`, `B-42511`, `B-43630`, `B-44922`, `B-46be2`, `B-48492`, `B-49e53`, `B-4b275`, `B-4d344`, `B-4ee3e`, `B-4f732`, `B-4fb0b`, `B-51a94`, `B-5243f`, `B-56960`, `B-56d51`, `B-57b89`, `B-57d6b`, `B-58b57`, `B-59117`, `B-59dd0`, `B-5b35d`, `B-5c90d`, `B-5cbfa`, `B-5ddf7`, `B-5e474`, `B-620ed`, `B-63234`, `B-6587b`, `B-66ce6`, `B-67052`, `B-69333`, `B-6ad07`, `B-6e686`, `B-6eaee`, `B-6f63a`, `B-6fcd9`, `B-72e23`, `B-76264`, `B-76ad0`, `B-77bf8`, `B-78814`, `B-790ac`, `B-7b491`, `B-7baba`, `B-7e000`, `B-7f956`, `B-805e2`, `B-8065d`, `B-819ed`, `B-81a91`, `B-81e89`, `B-82416`, `B-82617`, `B-83d81`, `B-85d28`, `B-8981e`, `B-8cc10`, `B-8da02`, `B-8ee16`, `B-92718`, `B-9445d`, `B-94de5`, `B-9505a`, `B-97c51`, `B-97d10`, `B-99324`, `B-9abfd`, `B-9cd48`, `B-9d3d4`, `B-a00a0`, `B-a10ff`, `B-a6300`, `B-a736b`, `B-a7bd3`, `B-a83dd`, `B-a88d9`, `B-a8bc6`, `B-a8ee2`, `B-aa7f3`, `B-ae079`, `B-af651`, `B-b0404`, `B-b3127`, `B-b5056`, `B-b8543`, `B-b8c23`, `B-bab82`, `B-bc6ec`, `B-bf99f`, `B-bfaa9`, `B-c0ae0`, `B-c258a`, `B-c2b5e`, `B-c3849`, `B-c426e`, `B-c5b77`, `B-c6369`, `B-c9854`, `B-ca3b1`, `B-cd6ea`, `B-cee04`, `B-cf21a`, `B-cf3ab`, `B-d025a`, `B-d2bbd`, `B-d3126`, `B-d4a55`, `B-d520d`, `B-d5561`, `B-d5dd7`, `B-d639a`, `B-d77e6`, `B-d84ff`, `B-db588`, `B-dbc9d`, `B-dc86b`, `B-e3924`, `B-e58d3`, `B-e60cc`, `B-e6e77`, `B-e7dc2`, `B-eddad`, `B-f07bd`, `B-f1f50`, `B-f5e2e`, `B-f758a`, `B-f86d3`, `B-f953b`, `B-fa774`, `B-fae5e`, `B-fb565`, `B-fbcc9`, `B-fbeee`

**S-b9f7** — real 131/150; decoy 32/37.

`B-06153`, `B-0a3f5`, `B-0a46c`, `B-0e1f1`, `B-0f7a0`, `B-1082c`, `B-13346`, `B-1a400`, `B-1acda`, `B-1af80`, `B-1b6c7`, `B-1cc7a`, `B-20625`, `B-21ca5`, `B-232aa`, `B-26016`, `B-263f6`, `B-275a1`, `B-28190`, `B-2890f`, `B-2c1c5`, `B-2dd66`, `B-333bd`, `B-376d8`, `B-37b77`, `B-37d53`, `B-39205`, `B-39ffc`, `B-3b8a3`, `B-3c0d2`, `B-3c434`, `B-3d2ff`, `B-3d538`, `B-3f87e`, `B-428a7`, `B-456cd`, `B-47a90`, `B-4ad22`, `B-4c981`, `B-4d698`, `B-4db0e`, `B-4e216`, `B-4e744`, `B-4f170`, `B-5193d`, `B-52c42`, `B-55143`, `B-559c1`, `B-55bc7`, `B-55ea5`, `B-584b7`, `B-5862d`, `B-5a97b`, `B-5b59d`, `B-5dd25`, `B-60477`, `B-60c05`, `B-62bd8`, `B-63040`, `B-66290`, `B-683c0`, `B-6913f`, `B-6df7d`, `B-6e2f5`, `B-70c28`, `B-70ee9`, `B-727b3`, `B-73bf4`, `B-74092`, `B-77f05`, `B-7cea2`, `B-7e0d2`, `B-7e715`, `B-8034f`, `B-81bd5`, `B-82433`, `B-82d24`, `B-834dd`, `B-84ab0`, `B-877f9`, `B-87b16`, `B-8876d`, `B-8948f`, `B-89777`, `B-89c34`, `B-8b123`, `B-8bc3b`, `B-8c0aa`, `B-8db5c`, `B-8de75`, `B-8ffee`, `B-901f2`, `B-9107f`, `B-92d5a`, `B-92fd1`, `B-9430e`, `B-95bf1`, `B-96893`, `B-96f75`, `B-97997`, `B-9a933`, `B-9cf3d`, `B-9e4d9`, `B-9f402`, `B-a2016`, `B-a3a81`, `B-a3e7e`, `B-a8a19`, `B-a8a94`, `B-a9da9`, `B-adefb`, `B-ae15c`, `B-b007f`, `B-b0c49`, `B-b1577`, `B-b18e0`, `B-b1ef5`, `B-b2e69`, `B-b646a`, `B-b97e9`, `B-be024`, `B-c1b08`, `B-c2f12`, `B-c3a89`, `B-c6c3b`, `B-c8c39`, `B-c9404`, `B-c9ff9`, `B-cd544`, `B-cd90a`, `B-cfde1`, `B-d041a`, `B-d086a`, `B-d1fd7`, `B-d391f`, `B-d3ec0`, `B-d3f55`, `B-d5be7`, `B-d9dac`, `B-db707`, `B-dd690`, `B-e2089`, `B-e2e99`, `B-e31f8`, `B-e4ab9`, `B-e4d7f`, `B-e55e3`, `B-e6436`, `B-e6e53`, `B-e9e24`, `B-ea923`, `B-ebabd`, `B-ee74d`, `B-efdaa`, `B-f6602`, `B-f79c9`, `B-f8df9`, `B-fb2d8`, `B-fb309`, `B-fb3a1`, `B-feab0`, `B-ff81e`, `B-ffe5c`

**S-cbb3** — real 76/192; decoy 16/48.

`B-0c101`, `B-0c953`, `B-10dac`, `B-111c2`, `B-19bc0`, `B-1f97a`, `B-21074`, `B-230e9`, `B-254a5`, `B-260cb`, `B-2953a`, `B-2aa92`, `B-3b59a`, `B-3d701`, `B-47934`, `B-4ad45`, `B-4c58f`, `B-4d5b7`, `B-4fae3`, `B-5188a`, `B-54917`, `B-55ef5`, `B-59d06`, `B-5e862`, `B-5f6aa`, `B-6843b`, `B-6a27b`, `B-6a85a`, `B-6e231`, `B-6f188`, `B-6ff80`, `B-6fffd`, `B-744d0`, `B-74bd7`, `B-7557a`, `B-78074`, `B-78e4d`, `B-7b2aa`, `B-7fb92`, `B-83a51`, `B-842e1`, `B-8531c`, `B-879be`, `B-959f7`, `B-96894`, `B-98c74`, `B-98ff4`, `B-99a80`, `B-9a8ba`, `B-9ace6`, `B-9cfdb`, `B-9ee91`, `B-9eeff`, `B-9f186`, `B-a1725`, `B-a57c3`, `B-aa38d`, `B-ac8aa`, `B-ad6c6`, `B-b268d`, `B-b8215`, `B-bdc9e`, `B-c0bf0`, `B-c383f`, `B-c7f21`, `B-c8da8`, `B-c8ff0`, `B-ca85f`, `B-cbf7e`, `B-cc1d5`, `B-cdc09`, `B-d5084`, `B-d660d`, `B-d7ebc`, `B-db5c3`, `B-dec1a`, `B-dff95`, `B-e2344`, `B-e6a7b`, `B-e8092`, `B-ed06d`, `B-f0c57`, `B-f0f99`, `B-f4521`, `B-f6011`, `B-f7ec1`, `B-f7f00`, `B-f9cb4`, `B-fa555`, `B-fa988`, `B-fb845`, `B-fd3de`

**S-cea7** — real 110/150; decoy 30/38.

`B-01410`, `B-021f6`, `B-02907`, `B-03729`, `B-07136`, `B-0b928`, `B-0dd58`, `B-100b4`, `B-10ad6`, `B-11b8f`, `B-122d9`, `B-179dd`, `B-1b102`, `B-1f8b3`, `B-20310`, `B-21b05`, `B-227bb`, `B-24268`, `B-24c39`, `B-25c7e`, `B-28834`, `B-2b9a2`, `B-2c186`, `B-2c68f`, `B-2c964`, `B-2efa9`, `B-3044e`, `B-32a0c`, `B-37e93`, `B-38115`, `B-3991c`, `B-3d2c1`, `B-3e52f`, `B-3ff5b`, `B-41ab3`, `B-433e9`, `B-47b36`, `B-4857c`, `B-4b544`, `B-4c7b4`, `B-4d385`, `B-4f8b8`, `B-509c3`, `B-50aa1`, `B-51073`, `B-52bfb`, `B-54eef`, `B-55691`, `B-5572b`, `B-55f6c`, `B-58ec9`, `B-5bac9`, `B-5d048`, `B-5da8a`, `B-63de9`, `B-648fe`, `B-66b9f`, `B-686f3`, `B-6c9a4`, `B-6efa6`, `B-72fc1`, `B-758ac`, `B-77016`, `B-79776`, `B-7a69b`, `B-7a7b7`, `B-7a956`, `B-7b2a7`, `B-7c81e`, `B-7f04d`, `B-8261d`, `B-84031`, `B-840c6`, `B-8659b`, `B-86bbf`, `B-87423`, `B-88891`, `B-8f535`, `B-8f86e`, `B-8fbbf`, `B-917de`, `B-948e9`, `B-95418`, `B-9696d`, `B-96d56`, `B-97e86`, `B-a3a9a`, `B-a4996`, `B-a5332`, `B-a6b9c`, `B-a7f88`, `B-aaada`, `B-ab77a`, `B-ab9ce`, `B-abe2a`, `B-af947`, `B-b2a3a`, `B-b30c6`, `B-b8f52`, `B-b9622`, `B-ba511`, `B-bb2d4`, `B-bb713`, `B-bb9fb`, `B-beb06`, `B-c48fd`, `B-c84de`, `B-c9e41`, `B-ca516`, `B-caa59`, `B-cb98a`, `B-cbd10`, `B-cc367`, `B-ccf25`, `B-cda43`, `B-d0a58`, `B-d3767`, `B-d37b3`, `B-d3add`, `B-d4a94`, `B-d5971`, `B-d5ed5`, `B-d99c9`, `B-daffe`, `B-dbb6f`, `B-e03e7`, `B-e08e1`, `B-e1d0a`, `B-e418c`, `B-e7fde`, `B-eaeac`, `B-ed1b4`, `B-ed9af`, `B-ed9c4`, `B-efa44`, `B-f1b1c`, `B-f345b`, `B-f3fb6`, `B-f6763`, `B-fa792`

**S-d5a1** — real 67/123; decoy 20/32.

`B-01ea3`, `B-04fb0`, `B-054ad`, `B-08cf8`, `B-0c676`, `B-0eaf7`, `B-12aa7`, `B-15d81`, `B-15fd5`, `B-1ec87`, `B-21664`, `B-21e60`, `B-25f4f`, `B-2f36f`, `B-34a98`, `B-3926f`, `B-3e4b3`, `B-40839`, `B-45177`, `B-45f10`, `B-472f4`, `B-491f2`, `B-4aa91`, `B-4d51c`, `B-4dab2`, `B-4dd13`, `B-4f64c`, `B-503d5`, `B-5280b`, `B-55758`, `B-57d8c`, `B-5f4cc`, `B-65530`, `B-6779a`, `B-6ab2a`, `B-7045f`, `B-72b2c`, `B-738b4`, `B-74d47`, `B-7c0f1`, `B-7d746`, `B-7e94a`, `B-7ed38`, `B-81103`, `B-82d3e`, `B-84a17`, `B-8686a`, `B-8826d`, `B-898af`, `B-8aae7`, `B-8c93a`, `B-90ea4`, `B-936a3`, `B-966de`, `B-9ccd4`, `B-9cfd3`, `B-a4fb4`, `B-ae12b`, `B-b0431`, `B-b200d`, `B-b3378`, `B-b37e1`, `B-bad8c`, `B-bc6df`, `B-bdafc`, `B-be09c`, `B-c189a`, `B-c49ef`, `B-c602a`, `B-c99c6`, `B-cfc6a`, `B-cfe8e`, `B-d043d`, `B-d18b2`, `B-da455`, `B-df349`, `B-e8b51`, `B-e8e39`, `B-edd22`, `B-f046c`, `B-f3547`, `B-f39e8`, `B-f3d06`, `B-f6058`, `B-f79bd`, `B-f7c49`, `B-f8bcf`

**S-d6ec** — real 91/190; decoy 23/47.

`B-0539a`, `B-09043`, `B-09220`, `B-116e4`, `B-172a5`, `B-1b910`, `B-22fec`, `B-23729`, `B-2380f`, `B-2611e`, `B-26d31`, `B-2b9c1`, `B-2c7b1`, `B-305cd`, `B-3177b`, `B-33445`, `B-33ab3`, `B-35f4b`, `B-37beb`, `B-38b0a`, `B-3e7fb`, `B-406fa`, `B-41da2`, `B-434f9`, `B-44066`, `B-4499e`, `B-44a9f`, `B-4a6da`, `B-4a732`, `B-4a809`, `B-4ab7f`, `B-4c976`, `B-4d929`, `B-4dcf2`, `B-4f6f6`, `B-5323f`, `B-56066`, `B-57842`, `B-5e29c`, `B-5e2d0`, `B-5f587`, `B-60c5d`, `B-60e0c`, `B-65b78`, `B-65bef`, `B-660db`, `B-66245`, `B-6a51b`, `B-6be52`, `B-6e109`, `B-6f1ff`, `B-77f33`, `B-790cd`, `B-7b69f`, `B-7c3f8`, `B-7e29f`, `B-813da`, `B-81a46`, `B-83c6f`, `B-857cb`, `B-87d5b`, `B-897e9`, `B-8a4dd`, `B-8b4f7`, `B-8dbcb`, `B-8fc25`, `B-91114`, `B-912c6`, `B-9185e`, `B-918f3`, `B-923b2`, `B-93076`, `B-93cb6`, `B-9567f`, `B-96703`, `B-98c31`, `B-9904d`, `B-9b874`, `B-9c785`, `B-a09f8`, `B-a11f3`, `B-a5d16`, `B-a69fb`, `B-b004a`, `B-b2b02`, `B-b2d1c`, `B-b3449`, `B-b3ff1`, `B-b41ba`, `B-b44d0`, `B-b7bf2`, `B-b8ce2`, `B-bcf8a`, `B-bd5fb`, `B-c57d0`, `B-c6fd4`, `B-c8f78`, `B-cc7e7`, `B-ccaa0`, `B-d3030`, `B-d72d8`, `B-dc5c7`, `B-dc5ca`, `B-e2006`, `B-e49e8`, `B-e57b9`, `B-e9eff`, `B-ea2ad`, `B-eb3f4`, `B-ed936`, `B-eddbe`, `B-f51d8`, `B-f679d`, `B-f7859`

**S-d83d** — real 125/169; decoy 30/43.

`B-03d3b`, `B-04be2`, `B-058cc`, `B-0b452`, `B-0bb46`, `B-0cb2d`, `B-0cf85`, `B-0d013`, `B-0d1bb`, `B-10261`, `B-11e5d`, `B-130ee`, `B-14fd1`, `B-1902e`, `B-19569`, `B-1bb2f`, `B-2117e`, `B-222de`, `B-223ee`, `B-23943`, `B-248f5`, `B-26577`, `B-29f47`, `B-2a3aa`, `B-2ae88`, `B-2b98c`, `B-2c930`, `B-2d3bb`, `B-2f031`, `B-2fd24`, `B-313d1`, `B-33f2e`, `B-34ce6`, `B-380c7`, `B-38f5d`, `B-39d4f`, `B-3c02e`, `B-3d9dd`, `B-3f71a`, `B-42288`, `B-42b2f`, `B-45ef5`, `B-47d9f`, `B-47fb3`, `B-48518`, `B-4b8e1`, `B-4bb74`, `B-4e849`, `B-4f4a1`, `B-510bb`, `B-55a20`, `B-5864d`, `B-58779`, `B-5904e`, `B-5baf7`, `B-5e079`, `B-5e78c`, `B-60a33`, `B-61375`, `B-659a2`, `B-67714`, `B-67b93`, `B-68585`, `B-69e82`, `B-69f63`, `B-6b449`, `B-6b8a5`, `B-6d4f0`, `B-6f065`, `B-7184f`, `B-71c74`, `B-73523`, `B-746f8`, `B-76a89`, `B-77baa`, `B-792ea`, `B-79a42`, `B-7a9ef`, `B-7b45a`, `B-7b96b`, `B-7bd77`, `B-7c5a3`, `B-7ed04`, `B-7f404`, `B-80518`, `B-831f6`, `B-83c68`, `B-84026`, `B-840e4`, `B-84e9b`, `B-86618`, `B-86e84`, `B-877dc`, `B-88080`, `B-891f1`, `B-8a62d`, `B-8af50`, `B-8be14`, `B-8cba3`, `B-8f94c`, `B-90af8`, `B-93122`, `B-9a0cc`, `B-9aed6`, `B-9b2bd`, `B-9caf0`, `B-9db7b`, `B-a0c79`, `B-a3d6c`, `B-a43c0`, `B-a5515`, `B-a57fc`, `B-ab473`, `B-abcfc`, `B-af1db`, `B-af92f`, `B-b2e1b`, `B-b3576`, `B-b5840`, `B-b78b4`, `B-b863f`, `B-bc8b7`, `B-bd5ef`, `B-c07b5`, `B-c0c54`, `B-c1a16`, `B-c391d`, `B-c4b44`, `B-c6509`, `B-cbd5d`, `B-cbe64`, `B-cdd89`, `B-d08b8`, `B-d3020`, `B-d3877`, `B-db385`, `B-dcffd`, `B-dd507`, `B-dd5aa`, `B-dd8e1`, `B-e1f50`, `B-e3b7a`, `B-e8025`, `B-e8b00`, `B-ec9da`, `B-eddbf`, `B-eeec9`, `B-ef8bd`, `B-f2c29`, `B-f42ec`, `B-f6943`, `B-f6be0`, `B-fc065`, `B-fd770`, `B-ffa3b`

**S-dbfc** — real 75/120; decoy 17/30.

`B-027be`, `B-04120`, `B-0c3c5`, `B-0c569`, `B-0c82b`, `B-12309`, `B-14e6a`, `B-1b61b`, `B-1d653`, `B-2114b`, `B-249d0`, `B-27ebf`, `B-28c9e`, `B-2c1f8`, `B-2ce02`, `B-306b7`, `B-31139`, `B-311f5`, `B-341d2`, `B-38c5f`, `B-3a0b6`, `B-3b352`, `B-4155d`, `B-42e55`, `B-44fd0`, `B-46301`, `B-4bfe5`, `B-4cf9c`, `B-4f425`, `B-52b87`, `B-541eb`, `B-5489e`, `B-56a92`, `B-61b54`, `B-63344`, `B-6442c`, `B-6948f`, `B-6a235`, `B-6ce1e`, `B-706dd`, `B-7350c`, `B-7437e`, `B-7445c`, `B-74e63`, `B-759e1`, `B-762ae`, `B-7bc67`, `B-7c45b`, `B-8169a`, `B-84af1`, `B-88dbe`, `B-8cb3c`, `B-8cd79`, `B-8e95e`, `B-916d6`, `B-91889`, `B-9336c`, `B-97401`, `B-9b8ad`, `B-9d935`, `B-a073b`, `B-a276a`, `B-a6e26`, `B-a844a`, `B-a8cbb`, `B-a985f`, `B-b6957`, `B-b890a`, `B-ba289`, `B-bcaac`, `B-bf946`, `B-c02c4`, `B-c1c12`, `B-c3c59`, `B-c7448`, `B-cf566`, `B-d78ec`, `B-d8ce5`, `B-d9a98`, `B-db4c8`, `B-dbe75`, `B-dd20a`, `B-df767`, `B-dfc25`, `B-e053a`, `B-e89a4`, `B-e9fe0`, `B-eaff5`, `B-f0ce7`, `B-f15cf`, `B-f4594`, `B-fa2e5`

**S-e31e** — real 124/190; decoy 32/47.

`B-01cff`, `B-03ea7`, `B-063f9`, `B-07fbc`, `B-08eb5`, `B-0aa01`, `B-0b9f5`, `B-0c125`, `B-0c981`, `B-0d3f8`, `B-0d65b`, `B-0da60`, `B-0f841`, `B-10049`, `B-10369`, `B-119a9`, `B-146e3`, `B-17dcd`, `B-18341`, `B-1af39`, `B-1bc52`, `B-1cd14`, `B-1d609`, `B-1d643`, `B-1d7c6`, `B-1fefa`, `B-206b9`, `B-235c9`, `B-25a0b`, `B-25ebb`, `B-25fac`, `B-26e6b`, `B-27838`, `B-2ac4e`, `B-2f3e3`, `B-31589`, `B-32663`, `B-340d1`, `B-34659`, `B-36994`, `B-38848`, `B-39b74`, `B-3c8ac`, `B-3c9fd`, `B-3d91a`, `B-3de23`, `B-3e759`, `B-413ac`, `B-413d0`, `B-42166`, `B-422be`, `B-44c2c`, `B-492af`, `B-4ad60`, `B-4ade6`, `B-521a0`, `B-542bb`, `B-54b38`, `B-58bbc`, `B-59085`, `B-59274`, `B-5a00c`, `B-5a429`, `B-5bfd0`, `B-5bfe6`, `B-5c211`, `B-5cc14`, `B-60905`, `B-61cd3`, `B-6752f`, `B-6773c`, `B-6a1c1`, `B-702a2`, `B-723f0`, `B-7371e`, `B-74ffd`, `B-7985a`, `B-79b54`, `B-7a5ea`, `B-80c32`, `B-8220d`, `B-82844`, `B-83937`, `B-85934`, `B-87484`, `B-89ea3`, `B-8c1dc`, `B-8c41b`, `B-9101d`, `B-9436c`, `B-9883e`, `B-9998a`, `B-99cb3`, `B-9a95d`, `B-9aca6`, `B-9be62`, `B-9f172`, `B-9faa5`, `B-a3709`, `B-a3e30`, `B-a3f86`, `B-a46fa`, `B-a5d79`, `B-a8138`, `B-aa99a`, `B-ab60f`, `B-abbb6`, `B-ae262`, `B-b1bdd`, `B-b2b89`, `B-b342d`, `B-b3bbf`, `B-b7666`, `B-ba3db`, `B-bdf60`, `B-bf915`, `B-c1264`, `B-c2d87`, `B-c7a66`, `B-cad33`, `B-cc1c4`, `B-cf9ec`, `B-d1e24`, `B-d2232`, `B-d2661`, `B-d2b5a`, `B-d39fe`, `B-d4123`, `B-d68e3`, `B-d6a51`, `B-d8db8`, `B-d9002`, `B-da3db`, `B-db872`, `B-dbda1`, `B-df977`, `B-dfe3f`, `B-e0345`, `B-e24e5`, `B-e2b3c`, `B-e3603`, `B-e65b3`, `B-e804d`, `B-ede5f`, `B-f136f`, `B-f13d0`, `B-f219b`, `B-f59f9`, `B-f6ad6`, `B-f76ec`, `B-f782b`, `B-f7b80`, `B-f8372`, `B-f913b`, `B-fa3e0`, `B-fdf33`

**S-e552** — real 110/139; decoy 28/34.

`B-03d4e`, `B-04d37`, `B-05188`, `B-0558b`, `B-0635d`, `B-07795`, `B-09937`, `B-0ab45`, `B-0acc5`, `B-0b314`, `B-0b5fe`, `B-0bbb7`, `B-0bc68`, `B-10532`, `B-108b6`, `B-1090d`, `B-12380`, `B-12db3`, `B-13026`, `B-15893`, `B-19940`, `B-1b0a6`, `B-1c467`, `B-1d982`, `B-1ecb8`, `B-20d22`, `B-220f0`, `B-2480a`, `B-253c2`, `B-29582`, `B-2a997`, `B-2ceb2`, `B-2d6f3`, `B-318fb`, `B-37024`, `B-3a778`, `B-3be1d`, `B-3eb39`, `B-3f5f6`, `B-42cd5`, `B-43f61`, `B-441ff`, `B-48ebf`, `B-49d05`, `B-4a7f7`, `B-4f577`, `B-51e82`, `B-5773d`, `B-59383`, `B-5e104`, `B-5ebd6`, `B-5f5ad`, `B-66b79`, `B-689d7`, `B-6970d`, `B-6a5b2`, `B-6c815`, `B-6d550`, `B-70865`, `B-73e5f`, `B-73f3b`, `B-7544d`, `B-76744`, `B-7a015`, `B-7a883`, `B-7c771`, `B-7c881`, `B-7d5aa`, `B-7e381`, `B-81864`, `B-81974`, `B-823a8`, `B-8f5a6`, `B-9028b`, `B-92c3a`, `B-97646`, `B-9b641`, `B-9cd41`, `B-a0d17`, `B-a1bb7`, `B-a45b2`, `B-a669c`, `B-a6a68`, `B-a7621`, `B-ab085`, `B-af06c`, `B-b0273`, `B-b0ac5`, `B-b147a`, `B-b1f0f`, `B-b303c`, `B-b3fcd`, `B-b75bc`, `B-b788b`, `B-b7a24`, `B-b9886`, `B-ba806`, `B-baa6a`, `B-bb1d1`, `B-c0131`, `B-c1d8e`, `B-c2a7d`, `B-c39a0`, `B-c522b`, `B-c60e6`, `B-c8762`, `B-cc552`, `B-cdb89`, `B-d15ed`, `B-d2621`, `B-d3527`, `B-d361f`, `B-d4d23`, `B-d616f`, `B-d8645`, `B-d8db6`, `B-d931f`, `B-de34b`, `B-df715`, `B-e030b`, `B-e2ee2`, `B-e4bdf`, `B-e8cff`, `B-e9c66`, `B-eb899`, `B-eca37`, `B-ece0c`, `B-ed33a`, `B-ee088`, `B-eec01`, `B-f4984`, `B-f4f16`, `B-f5272`, `B-f6395`, `B-f6d6b`, `B-fb30b`, `B-ff1a3`, `B-ffb9d`

**S-eb11** — real 126/203; decoy 35/52.

`B-002f1`, `B-02fda`, `B-03165`, `B-08769`, `B-09287`, `B-0b9f7`, `B-164ce`, `B-16a62`, `B-17b65`, `B-17dfc`, `B-1b81a`, `B-1c0d8`, `B-1ec50`, `B-1ec6d`, `B-1eed8`, `B-1f5cb`, `B-201b8`, `B-21487`, `B-27e19`, `B-2a52d`, `B-2bf75`, `B-2c741`, `B-2de5c`, `B-2e603`, `B-3008e`, `B-31ca3`, `B-33376`, `B-34162`, `B-35810`, `B-366ae`, `B-36775`, `B-36aef`, `B-36d70`, `B-3880d`, `B-3c415`, `B-3c5c7`, `B-3c9ed`, `B-3cdbc`, `B-3d84c`, `B-3e019`, `B-3f50d`, `B-41211`, `B-4326f`, `B-43594`, `B-47be7`, `B-48cfb`, `B-49f65`, `B-4d606`, `B-4df1f`, `B-50208`, `B-518d9`, `B-52117`, `B-55d12`, `B-59ec3`, `B-5b970`, `B-5ea39`, `B-5ec3d`, `B-5ffce`, `B-60d15`, `B-622e8`, `B-62593`, `B-63626`, `B-666f7`, `B-6ae32`, `B-6b875`, `B-6d43a`, `B-6dc54`, `B-716e6`, `B-7247c`, `B-79b37`, `B-7acc3`, `B-7c66f`, `B-7c8b9`, `B-7d405`, `B-80b7f`, `B-81b2f`, `B-81dab`, `B-84401`, `B-845a7`, `B-877f2`, `B-889f9`, `B-894d9`, `B-8a7cb`, `B-8b415`, `B-8c7db`, `B-8c898`, `B-8eb87`, `B-8ec3c`, `B-8f2df`, `B-9088a`, `B-911d6`, `B-93578`, `B-9393e`, `B-94e29`, `B-9537e`, `B-9a29d`, `B-9ac01`, `B-9aff9`, `B-9c74e`, `B-9c750`, `B-a04e2`, `B-a149b`, `B-a2940`, `B-a2a68`, `B-a2e57`, `B-a2f11`, `B-a7488`, `B-a9784`, `B-aa875`, `B-abfe7`, `B-ae5bb`, `B-afd74`, `B-afe88`, `B-b006f`, `B-b3f66`, `B-b4b73`, `B-b5e8c`, `B-b76bd`, `B-b90c2`, `B-bc7f7`, `B-bde31`, `B-beeff`, `B-c8364`, `B-cbb6d`, `B-cc1f3`, `B-cdc79`, `B-d04dc`, `B-d3634`, `B-d40f4`, `B-d50c5`, `B-d707a`, `B-da7de`, `B-daf0b`, `B-ddd6d`, `B-dedd6`, `B-df71d`, `B-e37e3`, `B-e3835`, `B-e43b3`, `B-e469e`, `B-e4c3a`, `B-e5016`, `B-e517c`, `B-e51cf`, `B-e661a`, `B-e89f6`, `B-e8a5a`, `B-e8de5`, `B-e8efe`, `B-ea27e`, `B-eb72a`, `B-ec9fa`, `B-ed148`, `B-ed8ca`, `B-f0196`, `B-f2c60`, `B-f4396`, `B-f693d`, `B-f7ddb`, `B-faf6e`, `B-fb04e`

**S-ee1b** — real 77/130; decoy 10/32.

`B-03a77`, `B-06707`, `B-0676a`, `B-070f5`, `B-0721c`, `B-08545`, `B-09a25`, `B-0f116`, `B-11f03`, `B-145d7`, `B-14c52`, `B-226b5`, `B-2488c`, `B-26a06`, `B-28dea`, `B-327d3`, `B-3634a`, `B-3a1df`, `B-3c3e8`, `B-40571`, `B-419a2`, `B-47fde`, `B-4d553`, `B-55582`, `B-5598f`, `B-58d34`, `B-58dd3`, `B-58f84`, `B-5beb4`, `B-5c357`, `B-5e4f2`, `B-61bbf`, `B-664f4`, `B-66fa8`, `B-677a6`, `B-74dd2`, `B-76929`, `B-786a2`, `B-7a996`, `B-7c298`, `B-7e4b5`, `B-81692`, `B-81d6d`, `B-8f4ec`, `B-9335f`, `B-95fd4`, `B-9d037`, `B-9f691`, `B-a2e0e`, `B-a510f`, `B-a5a17`, `B-a7641`, `B-aac8d`, `B-ac6fd`, `B-b4bac`, `B-b5f50`, `B-b6397`, `B-b66f1`, `B-b9cf6`, `B-b9e7e`, `B-beb90`, `B-bfd35`, `B-c49a7`, `B-c80dc`, `B-ca1cf`, `B-cec12`, `B-d0e77`, `B-d2252`, `B-d5898`, `B-d6219`, `B-d7258`, `B-d9a25`, `B-de150`, `B-de27c`, `B-df8f4`, `B-e0cee`, `B-e10c5`, `B-e37d3`, `B-e5be3`, `B-e9d9b`, `B-ed50d`, `B-f19c8`, `B-f1c95`, `B-f4b09`, `B-f6436`, `B-f859f`, `B-fdc3b`

**S-f7bf** — real 73/170; decoy 16/42.

`B-087a7`, `B-0ca51`, `B-0cfaa`, `B-0f804`, `B-0feff`, `B-10e1d`, `B-10e8c`, `B-11254`, `B-12043`, `B-122de`, `B-13318`, `B-16d74`, `B-1affb`, `B-1d307`, `B-24385`, `B-26061`, `B-29788`, `B-2d230`, `B-33533`, `B-356f3`, `B-3696f`, `B-3f408`, `B-42bb3`, `B-43e73`, `B-44a73`, `B-4793c`, `B-4831c`, `B-4c7fe`, `B-4d11b`, `B-50180`, `B-5132d`, `B-525fe`, `B-5acef`, `B-71497`, `B-727be`, `B-797e8`, `B-7b211`, `B-7e6cd`, `B-7eae8`, `B-83f29`, `B-881f3`, `B-88258`, `B-890b5`, `B-8a6c8`, `B-8b3c3`, `B-8d735`, `B-929cb`, `B-94849`, `B-94aa4`, `B-9a41f`, `B-9b009`, `B-9b854`, `B-9d65e`, `B-9ec42`, `B-a24ee`, `B-a2971`, `B-a4c92`, `B-a59d9`, `B-abf54`, `B-ad8cf`, `B-b0e61`, `B-b12bc`, `B-b1428`, `B-b45f4`, `B-b9e1f`, `B-bb084`, `B-bc911`, `B-bf1a7`, `B-bf27b`, `B-c603f`, `B-c6e98`, `B-ca1eb`, `B-cb350`, `B-cbb28`, `B-cf50f`, `B-d096c`, `B-d4061`, `B-d9267`, `B-dba4d`, `B-dc044`, `B-ddcf7`, `B-e8784`, `B-ea517`, `B-ec6fc`, `B-f39b5`, `B-f4f24`, `B-f5422`, `B-f71d5`, `B-fd11a`

**S-f885** — real 57/117; decoy 7/30.

`B-0114a`, `B-01ce1`, `B-035e1`, `B-04707`, `B-0d6e4`, `B-15a43`, `B-15a62`, `B-1d7db`, `B-1e8f7`, `B-226a3`, `B-229af`, `B-28888`, `B-2c8c6`, `B-324c5`, `B-36d75`, `B-3a019`, `B-3b69f`, `B-3bfd6`, `B-3e13a`, `B-3eccc`, `B-41987`, `B-4217b`, `B-42790`, `B-449cf`, `B-4aa57`, `B-4aeb5`, `B-4c76a`, `B-56a18`, `B-5f5da`, `B-62f8c`, `B-69f70`, `B-707b1`, `B-79b0f`, `B-7e0b1`, `B-7e59f`, `B-7f8e2`, `B-8404c`, `B-85e1b`, `B-863f5`, `B-8c3c1`, `B-8c441`, `B-95811`, `B-a5016`, `B-a7a19`, `B-ace6e`, `B-ad6d4`, `B-ae68c`, `B-b714b`, `B-b8630`, `B-be4a3`, `B-bfa74`, `B-c4a7e`, `B-cc3e9`, `B-e1866`, `B-e2df6`, `B-e2fb2`, `B-e4464`, `B-e4784`, `B-e7df6`, `B-eaa46`, `B-f4f85`, `B-fbe5e`, `B-fc571`, `B-fe570`

</details>
