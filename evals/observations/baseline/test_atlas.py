import contextlib
import hashlib
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import atlas


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'notes'
        self.root.mkdir()
        (self.root / 'nested').mkdir()
        (self.root / 'nested' / 'incident.txt').write_text('Recent client feedback delayed delivery.', encoding='utf-8')
        (self.root / 'other.txt').write_text('Library meeting on Tuesday.', encoding='utf-8')
        (self.root / 'separated.txt').write_text('The client sent useful feedback.', encoding='utf-8')
        self.index = self.base / 'index.sqlite'

    def hashes(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*.txt') if not p.is_symlink()}

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            atlas.build(self.root, self.index)

    def search(self, text, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return atlas.query(self.index, text, **kwargs)

    def test_phrase_word_paths_and_source_integrity(self):
        before = self.hashes()
        self.build()
        result = self.search('client feedback')
        self.assertEqual([r[0] for r in result], ['nested/incident.txt'])
        self.assertIn('[client feedback]', result[0][1])
        self.assertEqual(len(self.search('client')), 2)
        self.assertEqual(len(self.search('client feedback', all_words=True)), 2)
        self.assertEqual(self.hashes(), before)

    def test_query_without_source_folder(self):
        self.build()
        self.root.rename(self.base / 'unavailable-notes')
        self.assertEqual(len(self.search('client feedback')), 1)

    def test_symlinks_are_excluded(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'secret.txt').write_text('outside secret', encoding='utf-8')
        (self.root / 'file-link.txt').symlink_to(outside / 'secret.txt')
        (self.root / 'dir-link').symlink_to(outside, target_is_directory=True)
        self.build()
        self.assertEqual(self.search('secret'), [])

    def test_rebuild_removes_deleted_note(self):
        self.build()
        (self.root / 'nested' / 'incident.txt').unlink()
        self.build()
        self.assertEqual(self.search('client feedback'), [])

    def test_failed_rebuild_preserves_index(self):
        self.build()
        before = self.index.read_bytes()
        (self.root / 'bad.txt').write_bytes(b'\xff')
        with self.assertRaises(UnicodeError):
            self.build()
        self.assertEqual(self.index.read_bytes(), before)

    def test_rejects_index_inside_sources_and_unrelated_file(self):
        with self.assertRaises(ValueError):
            atlas.build(self.root, self.root / 'index.sqlite')
        self.index.write_text('not an index', encoding='utf-8')
        with self.assertRaises(sqlite3.Error):
            self.build()
        self.assertEqual(self.index.read_text(), 'not an index')

    def test_literal_query_and_empty_guard(self):
        self.build()
        self.assertEqual(self.search('client OR feedback'), [])
        with self.assertRaises(ValueError):
            self.search('  ')

    def test_missing_fts5_is_reported(self):
        class Unavailable:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def execute(self, sql):
                raise sqlite3.OperationalError('no such module: fts5')
        with patch('atlas.sqlite3.connect', return_value=Unavailable()):
            with self.assertRaisesRegex(ValueError, 'FTS5 is unavailable'):
                atlas.check_fts5()


if __name__ == '__main__':
    unittest.main(verbosity=2)
