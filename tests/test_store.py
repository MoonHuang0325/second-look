import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/second-look/scripts"))
from secondlook.history import plain, validate_record
from secondlook.store import Store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = Store(self.root / "private")
        self.record = plain("User: Need 45 minutes\nAssistant: Here is a 60 minute plan", self.root / "input.md")[0]
        self.store.ingest([self.record])
        self.keys = [self.record["key"]]

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def review(self, model=None, context=""):
        return self.store.review("workshop", self.keys, "supported_improvement", "Fixed duration", ["input.md:1"], "reply:1", model, context)

    def test_idempotent_import_and_content_update(self):
        self.assertEqual(self.store.ingest([self.record])["unchanged"], 1)
        metadata = copy.deepcopy(self.record)
        metadata["updated_at"] = "2026-09-06T00:00:00Z"
        self.assertEqual(self.store.ingest([metadata])["unchanged"], 1)
        updated = copy.deepcopy(self.record)
        updated["messages"][0]["text"] = "Now 30 minutes"
        self.assertEqual(self.store.ingest([updated])["updated"], 1)

    def test_review_repeat_and_new_goal(self):
        self.review("model-a")
        self.assertFalse(self.store.eligible("workshop", self.keys, "model-a")["eligible"])
        self.assertTrue(self.store.eligible("another-goal", self.keys, "model-a")["eligible"])
        self.assertTrue(self.store.eligible("workshop", self.keys, "model-b")["eligible"])
        self.assertFalse(self.store.eligible("workshop", self.keys, None)["eligible"])

    def test_unknown_model_not_invented_change(self):
        self.review()
        self.assertFalse(self.store.eligible("workshop", self.keys, "model-b")["eligible"])

    def test_new_context_content_and_explicit_retry(self):
        self.review()
        self.assertTrue(self.store.eligible("workshop", self.keys, context="new budget")["eligible"])
        self.assertTrue(self.store.eligible("workshop", self.keys, retry=True)["eligible"])
        updated = copy.deepcopy(self.record)
        updated["messages"][0]["text"] += " Updated."
        self.store.ingest([updated])
        self.assertTrue(self.store.eligible("workshop", self.keys)["eligible"])

    def test_exclude_include_and_retry(self):
        self.store.feedback("workshop", "goal", "exclude")
        self.assertFalse(self.store.eligible("workshop", self.keys)["eligible"])
        self.assertTrue(self.store.eligible("workshop", self.keys, retry=True)["eligible"])
        self.store.feedback("workshop", "goal", "include")
        self.assertTrue(self.store.eligible("workshop", self.keys)["eligible"])
        self.store.feedback(self.keys[0], "source", "closed")
        self.assertEqual(self.store.candidates()["returned"], 0)
        self.assertEqual(self.store.candidates(include_excluded=True)["returned"], 1)

    def test_inspection_is_not_completion(self):
        self.store.inspect(self.keys)
        self.assertEqual(self.store.candidates()["returned"], 0)
        self.assertTrue(self.store.eligible("workshop", self.keys)["eligible"])
        self.assertEqual(self.store.candidates(include_inspected=True)["returned"], 1)

    def test_changed_sources_reenter_discovery(self):
        self.store.inspect(self.keys)
        updated = copy.deepcopy(self.record)
        updated["messages"][0]["text"] = "New constraint"
        self.store.ingest([updated])
        self.assertEqual(self.store.candidates()["returned"], 1)

    def test_pending_run_and_resumption(self):
        run = self.store.run(checkpoint={"next_step": "verify"})
        self.assertEqual(self.store.run(run["id"])["checkpoint"]["next_step"], "verify")
        self.assertTrue(self.store.eligible("workshop", self.keys)["eligible"])
        self.assertEqual(self.store.run(run["id"], finish=True)["status"], "complete")
        with self.assertRaises(ValueError):
            self.store.run(run["id"], checkpoint={})

    def test_ledger_portability_without_raw_transcripts(self):
        self.review()
        self.store.inspect(self.keys)
        ledger = self.store.ledger()
        self.assertNotIn("Need 45 minutes", str(ledger))
        other = Store(self.root / "other")
        try:
            other.ingest([self.record])
            other.restore(ledger)
            self.assertFalse(other.eligible("workshop", self.keys)["eligible"])
            self.assertEqual(other.candidates()["returned"], 0)
        finally:
            other.close()

    def test_invalid_restore_rolls_back(self):
        self.review()
        ledger = self.store.ledger()
        ledger["feedback"] = [{"scope": "invalid", "target": "x", "value": "include"}]
        other = Store(self.root / "other")
        try:
            with self.assertRaises(ValueError):
                other.restore(ledger)
            self.assertEqual(other.ledger()["reviews"], [])
        finally:
            other.close()

    def test_branch_refresh_retires_old_leaves(self):
        newer = copy.deepcopy(self.record)
        newer["branch"] = "leaf-2"
        stats = self.store.ingest([newer])
        self.assertEqual(stats["retired_branches"], 1)
        self.assertEqual(self.store.candidates()["returned"], 1)

    def test_conflicting_duplicates_are_atomic(self):
        before = self.store.read(self.keys[0])
        conflict = copy.deepcopy(self.record)
        conflict["messages"][0]["text"] = "Conflicting source"
        with self.assertRaises(ValueError):
            self.store.ingest([self.record, conflict])
        self.assertEqual(self.store.read(self.keys[0]), before)

    def test_review_requires_evidence_and_delivered_result(self):
        for evidence, artifact in (([], "reply:1"), (["input.md:1"], "")):
            with self.assertRaises(ValueError):
                self.store.review("workshop", self.keys, "supported_improvement", "change", evidence, artifact)

    def test_public_and_skill_data_locations_rejected(self):
        repo = Path(__file__).resolve().parents[1]
        for path in (repo / "private", repo / "skills/second-look/data"):
            with self.assertRaises(ValueError):
                Store(path)

    def test_discovery_interleaves_old_and_recent(self):
        records = []
        for i in range(12):
            r = plain("User: An unresolved task", self.root / (str(i) + ".txt"))[0]
            r["updated_at"] = "2026-01-%02d" % (i + 1)
            records.append(r)
        self.store.ingest(records)
        candidates = self.store.candidates(limit=3)["candidates"]
        self.assertEqual(candidates[0]["updated_at"], "2026-01-12")
        self.assertNotEqual(candidates[2]["key"], candidates[1]["key"])
        self.assertEqual(self.store.candidates(query="UNRESOLVED")["returned"], 12)


if __name__ == "__main__":
    unittest.main()
