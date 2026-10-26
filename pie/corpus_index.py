"""Local SQLite search of loader units, including units outside Stage C-S layers.

Payloads are compressed JSON; inverted postings index roots/groups, lemmas and
content-word forms. No source module or pickle is needed to query the index.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sqlite3
import tempfile
import zlib


def _pack(record):
    return zlib.compress(json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode(), 1)


def _unpack(blob):
    record = json.loads(zlib.decompress(blob))
    from .material_units import reading_emendations
    annotations = reading_emendations(record.get("corpus", ""), record.get("locus", ""), record.get("text", ""))
    if annotations:
        record["emendations"] = annotations
    return record


def build_index(path: Path, records) -> int:
    """Atomically replace an index from dictionaries; retain every supplied unit."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".sqlite", delete=False) as f:
        temporary = Path(f.name)
    db = sqlite3.connect(temporary)
    try:
        db.executescript("""
            PRAGMA journal_mode=OFF;
            CREATE TABLE units(id INTEGER PRIMARY KEY, corpus TEXT, branch TEXT,
                               book TEXT, ordinal INTEGER, payload BLOB);
            CREATE TABLE terms(id INTEGER PRIMARY KEY, kind TEXT, value TEXT,
                               UNIQUE(kind, value));
            CREATE TABLE postings(term INTEGER, unit INTEGER,
                                  PRIMARY KEY(term, unit)) WITHOUT ROWID;
            CREATE INDEX neighbours ON units(corpus, book, ordinal);
            CREATE INDEX corpora ON units(corpus);
            CREATE INDEX branches ON units(branch);
            PRAGMA user_version=1;
        """)
        terms = {}
        count = 0
        for count, record in enumerate(records, 1):
            db.execute("INSERT INTO units VALUES(?,?,?,?,?,?)", (
                count, record["corpus"], record["branch"], record["book"],
                record["ordinal"], _pack(record)))
            keys = set()
            for word in record["words"]:
                keys.add(("lemma", word["lemma"]))
                keys.add(("form", word["form"]))
                keys.update(("root", r) for r in word["root_ids"] + word["root_groups"])
            ids = []
            for key in sorted(keys):
                if key not in terms:
                    terms[key] = len(terms) + 1
                    db.execute("INSERT INTO terms VALUES(?,?,?)", (terms[key], *key))
                ids.append((terms[key], count))
            db.executemany("INSERT INTO postings VALUES(?,?)", ids)
        db.commit()
        db.execute("ANALYZE")
        db.close()
        temporary.replace(path)
        return count
    finally:
        db.close()
        temporary.unlink(missing_ok=True)


def roots_near(words, roots, distance):
    """All requested roots on distinct words, max(position)-min(position) <= N.

    Unmapped content words count; function words do not. Matching is within one
    loader unit/window, never across neighbouring units.
    """
    choices = [[i for i, w in enumerate(words)
                if root in w["root_ids"] or root in w["root_groups"]] for root in roots]
    if any(not c for c in choices):
        return False
    choices.sort(key=len)

    def match(k, used):
        if k == len(choices):
            return True
        for pos in choices[k]:
            if pos not in used:
                new = used | {pos}
                if max(new) - min(new) <= distance and match(k + 1, new):
                    return True
        return False

    return match(0, set())


class CorpusIndex:
    def __init__(self, path):
        self.db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
        if self.db.execute("PRAGMA user_version").fetchone()[0] != 1:
            self.close()
            raise ValueError("Unsupported index version; rebuild the index")

    def close(self):
        self.db.close()

    def search(self, *, roots=(), lemmas=(), form=None, corpora=(), branches=(),
               not_corpora=(), near=None, limit=20, context=0):
        """Yield ordered records. Repeated roots/lemmas AND; corpus/branch lists OR.

        Form is a case-sensitive Python regex searched on content-word forms.
        None limit yields all matches. Context stays within corpus and book.
        """
        if near is not None and (near < 0 or len(roots) < 2):
            raise ValueError("--near requires at least two --root arguments and N >= 0")
        if context < 0 or (limit is not None and limit < 0):
            raise ValueError("limit and context must be nonnegative")
        conditions, args = [], []
        for kind, value in [("root", r) for r in roots] + [("lemma", l) for l in lemmas]:
            conditions.append("u.id IN (SELECT p.unit FROM postings p JOIN terms t ON t.id=p.term WHERE t.kind=? AND t.value=?)")
            args.extend((kind, value))
        if form is not None:
            regex = re.compile(form)
            self.db.create_function("matches", 1, lambda s: bool(regex.search(s)))
            conditions.append("u.id IN (SELECT p.unit FROM terms t JOIN postings p ON p.term=t.id WHERE t.kind='form' AND matches(t.value))")
        for column, values, negate in (("corpus", corpora, False), ("branch", branches, False),
                                        ("corpus", not_corpora, True)):
            if values:
                conditions.append(f"u.{column} {'NOT IN' if negate else 'IN'} ({','.join('?' for _ in values)})")
                args.extend(values)
        sql = "SELECT u.payload FROM units u"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY u.id"
        found = 0
        if limit == 0:
            return
        for (payload,) in self.db.execute(sql, args):
            record = _unpack(payload)
            if near is not None and not roots_near(record["words"], roots, near):
                continue
            if context:
                neighbours = []
                for comparison, order in (("<", "DESC"), (">", "ASC")):
                    neighbours.extend(_unpack(row[0]) for row in self.db.execute(
                        f"SELECT payload FROM units WHERE corpus=? AND book=? AND ordinal {comparison} ? ORDER BY ordinal {order} LIMIT ?",
                        (record["corpus"], record["book"], record["ordinal"], context)))
                record["context"] = sorted(neighbours, key=lambda r: r["ordinal"])
            yield record
            found += 1
            if limit is not None and found >= limit:
                break
