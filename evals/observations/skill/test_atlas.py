import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import atlas_search as atlas


class AtlasTests(unittest.TestCase):
    def test_acceptance_and_edges(self):
        with tempfile.TemporaryDirectory(prefix='atlas-fictional-') as temporary:
            base = Path(temporary)
            root = base / 'fictional-notes'
            root.mkdir()
            (root / 'nested').mkdir()
            (root / 'nested' / 'client.txt').write_text('Remember the client feedback from Tuesday.', encoding='utf-8')
            (root / 'unrelated.txt').write_text('Garden soil and lavender.', encoding='utf-8')
            (root / 'separated.txt').write_text('The client sent useful feedback.', encoding='utf-8')
            (root / 'ignored.md').write_text('client feedback', encoding='utf-8')
            outside = base / 'outside'
            outside.mkdir()
            (outside / 'secret.txt').write_text('client feedback OUTSIDE', encoding='utf-8')
            (root / 'linked.txt').symlink_to(outside / 'secret.txt')
            (root / 'linked-dir').symlink_to(outside, target_is_directory=True)
            before = {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
            index = base / 'atlas.sqlite'
            self.assertEqual(atlas.build(root, index)['indexed_files'], 3)
            hits = atlas.search(index, 'client feedback', 20)
            self.assertEqual([x['path'] for x in hits], ['nested/client.txt'])
            self.assertIn('[client feedback]', hits[0]['matching_text'])
            self.assertEqual(len(atlas.search(index, 'client', 20)), 2)
            self.assertEqual(atlas.search(index, 'OUTSIDE', 20), [])
            self.assertEqual(atlas.search(index, '" OR client', 20), [])
            after = {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
            self.assertEqual(before, after)
            with self.assertRaises(ValueError):
                atlas.build(root, root / 'bad.sqlite')
            with self.assertRaises(ValueError):
                atlas.search(index, '   ', 20)
            # The query must work while the entire original folder is absent.
            moved = base / 'temporarily-moved'
            root.rename(moved)
            self.assertEqual(atlas.search(index, 'client feedback', 20), hits)
            moved.rename(root)
            (root / 'bad.txt').write_bytes(b'\xff')
            with self.assertRaises(UnicodeDecodeError):
                atlas.build(root, index)
            self.assertEqual(atlas.search(index, 'client feedback', 20), hits)
            (root / 'bad.txt').unlink()
            (root / 'nested' / 'client.txt').unlink()
            atlas.build(root, index)
            self.assertEqual(atlas.search(index, 'client feedback', 20), [])
            unrelated = base / 'unrelated.sqlite'
            unrelated.write_bytes(b'not a database')
            with self.assertRaises(sqlite3.DatabaseError):
                atlas.build(root, unrelated)
            self.assertEqual(unrelated.read_bytes(), b'not a database')

    def test_fts5_unavailable_message(self):
        class MissingFTS:
            def execute(self, _):
                raise sqlite3.OperationalError('no such module: fts5')
        with self.assertRaisesRegex(RuntimeError, 'FTS5 is unavailable'):
            atlas.check_fts5(MissingFTS())


if __name__ == '__main__':
    unittest.main(verbosity=2)
