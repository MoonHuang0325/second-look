#!/usr/bin/env python3
"""Local UTF-8 .txt word/phrase search. Python 3.9+, SQLite FTS5 required."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile


def check_fts5(conn):
    try:
        conn.execute('CREATE VIRTUAL TABLE temp.fts_probe USING fts5(text)')
        conn.execute('DROP TABLE temp.fts_probe')
    except sqlite3.OperationalError as exc:
        raise RuntimeError('SQLite FTS5 is unavailable in this Python installation.') from exc


def inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def build(folder, index):
    root = Path(folder).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Folder must be a directory.')
    raw_index = Path(index).expanduser()
    if raw_index.is_symlink():
        raise ValueError('Index must not be a symlink.')
    destination = raw_index.resolve()
    if inside(destination, root):
        raise ValueError('Keep the index outside the source folder.')
    if not destination.parent.is_dir():
        raise ValueError('The index parent directory must already exist.')
    # Reject unrelated databases/files before replacing an existing index.
    if destination.exists():
        with sqlite3.connect(destination.as_uri() + '?mode=ro', uri=True) as old:
            marker = old.execute('SELECT format FROM atlas_metadata').fetchone()
            if marker != ('atlas-search-v1',):
                raise ValueError('Existing file is not an Atlas index.')
    fd, filename = tempfile.mkstemp(prefix='.atlas-build-', suffix='.sqlite', dir=destination.parent)
    os.close(fd)
    staging = Path(filename)
    count = 0
    conn = None
    try:
        conn = sqlite3.connect(staging)
        check_fts5(conn)
        conn.execute('CREATE TABLE atlas_metadata(format TEXT, root TEXT)')
        conn.execute('INSERT INTO atlas_metadata VALUES (?, ?)', ('atlas-search-v1', str(root)))
        conn.execute('CREATE VIRTUAL TABLE notes USING fts5(path UNINDEXED, body, tokenize="unicode61")')
        for parent, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(parent) / d).is_symlink())
            for name in sorted(names):
                path = Path(parent) / name
                if path.suffix.lower() != '.txt' or path.is_symlink() or not path.is_file():
                    continue
                if not inside(path.resolve(strict=True), root):
                    continue
                # Files are opened only for reading. Any decoding/read error aborts the rebuild.
                body = path.read_text(encoding='utf-8')
                conn.execute('INSERT INTO notes(path, body) VALUES (?, ?)', (path.relative_to(root).as_posix(), body))
                count += 1
        conn.commit()
        conn.close()
        conn = None
        os.replace(staging, destination)
    finally:
        if conn is not None:
            conn.close()
        staging.unlink(missing_ok=True)
    return {'indexed_files': count, 'index': str(destination)}


def search(index, phrase, limit):
    if not phrase.strip():
        raise ValueError('Enter a nonempty word or phrase.')
    if limit < 1 or limit > 1000:
        raise ValueError('Limit must be between 1 and 1000.')
    path = Path(index).expanduser().resolve(strict=True)
    # Quote the entire argument as an FTS phrase; operators are treated as text.
    query = '"' + phrase.replace('"', '""') + '"'
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as conn:
        check_fts5(conn)
        rows = conn.execute(
            "SELECT path, snippet(notes, 1, '[', ']', ' … ', 30) FROM notes "
            'WHERE notes MATCH ? ORDER BY bm25(notes), path LIMIT ?', (query, limit)
        ).fetchall()
    return [{'path': row[0], 'matching_text': row[1]} for row in rows]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    rebuild = sub.add_parser('index', help='Rebuild a local index from a selected folder')
    rebuild.add_argument('folder')
    rebuild.add_argument('index')
    query = sub.add_parser('query', help='Find an indexed word or phrase without reading source files')
    query.add_argument('index')
    query.add_argument('phrase')
    query.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    try:
        result = build(args.folder, args.index) if args.command == 'index' else search(args.index, args.phrase, args.limit)
    except (OSError, UnicodeError, ValueError, RuntimeError, sqlite3.Error) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
