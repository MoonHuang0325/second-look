#!/usr/bin/env python3
"""Offline UTF-8 .txt search. Python 3.9+; SQLite FTS5 required."""
import argparse
import os
from pathlib import Path
import sqlite3
import sys
import tempfile


def check_fts5():
    with sqlite3.connect(':memory:') as con:
        try:
            con.execute('CREATE VIRTUAL TABLE probe USING fts5(text)')
        except sqlite3.OperationalError as exc:
            raise ValueError('SQLite FTS5 is unavailable in this Python installation.') from exc


def build(folder, index):
    check_fts5()
    root = Path(folder).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('The explicitly selected source must be a directory.')
    supplied = Path(index).expanduser().absolute()
    if supplied.is_symlink():
        raise ValueError('The index must not be a symlink.')
    target = supplied.resolve()
    if target == root or root in target.parents:
        raise ValueError('Choose an index outside the source folder.')
    if not target.parent.is_dir():
        raise ValueError('The index parent directory must already exist.')
    # Never replace an unrelated existing file.
    if target.exists():
        old = sqlite3.connect(target.as_uri() + '?mode=ro', uri=True)
        try:
            if old.execute('SELECT version FROM atlas_meta').fetchone() != (1,):
                raise ValueError('Existing file is not a supported Atlas index.')
        finally:
            old.close()
    fd, temporary = tempfile.mkstemp(prefix='.atlas-', suffix='.sqlite', dir=target.parent)
    os.close(fd)
    con = None
    count = 0
    skipped = 0
    try:
        con = sqlite3.connect(temporary)
        con.execute('CREATE TABLE atlas_meta(version INTEGER NOT NULL)')
        con.execute('INSERT INTO atlas_meta VALUES (1)')
        con.execute("CREATE VIRTUAL TABLE notes USING fts5(path UNINDEXED, body, tokenize='unicode61')")

        def walk_error(error):
            raise error

        for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
            kept = []
            for name in sorted(dirs):
                if (Path(directory) / name).is_symlink():
                    skipped += 1
                else:
                    kept.append(name)
            dirs[:] = kept
            for name in sorted(files):
                source = Path(directory) / name
                if source.is_symlink():
                    skipped += 1
                    continue
                if source.suffix.lower() != '.txt' or not source.is_file():
                    continue
                # Recheck containment; skip all symlinks, even ones within root.
                resolved = source.resolve(strict=True)
                if root not in resolved.parents:
                    raise ValueError('Source escaped selected folder: ' + str(source))
                flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                descriptor = os.open(source, flags)
                with os.fdopen(descriptor, 'r', encoding='utf-8') as stream:
                    body = stream.read()
                con.execute('INSERT INTO notes(path, body) VALUES (?, ?)',
                            (source.relative_to(root).as_posix(), body))
                count += 1
        con.commit()
        con.close()
        con = None
        os.replace(temporary, target)
    finally:
        if con is not None:
            con.close()
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Indexed {} notes; skipped {} symlinks.'.format(count, skipped))


def quoted(text):
    return '"' + text.replace('"', '""') + '"'


def query(index, text, all_words=False, limit=20):
    check_fts5()
    if not text.strip():
        raise ValueError('Search text must not be empty.')
    if limit < 1 or limit > 1000:
        raise ValueError('Limit must be between 1 and 1000.')
    target = Path(index).expanduser().resolve(strict=True)
    con = sqlite3.connect(target.as_uri() + '?mode=ro', uri=True)
    try:
        if con.execute('SELECT version FROM atlas_meta').fetchone() != (1,):
            raise ValueError('Unsupported Atlas index.')
        expression = (' AND '.join(quoted(word) for word in text.split())
                      if all_words else quoted(text))
        rows = con.execute(
            "SELECT path, snippet(notes, 1, '[', ']', ' … ', 24) "
            "FROM notes WHERE notes MATCH ? ORDER BY bm25(notes), path LIMIT ?",
            (expression, limit)).fetchall()
        for path, excerpt in rows:
            print(path)
            print('  ' + excerpt.replace('\n', ' '))
        print('{} result(s).'.format(len(rows)))
        return rows
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    b = commands.add_parser('build', help='Rebuild an index from an explicitly selected folder')
    b.add_argument('--folder', required=True)
    b.add_argument('--index', required=True)
    q = commands.add_parser('query', help='Find a word or token phrase using only the index')
    q.add_argument('--index', required=True)
    q.add_argument('text')
    q.add_argument('--all-words', action='store_true', help='Require every whitespace-separated term')
    q.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    try:
        if args.command == 'build':
            build(args.folder, args.index)
        else:
            query(args.index, args.text, args.all_words, args.limit)
    except (OSError, UnicodeError, ValueError, sqlite3.Error) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
