import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/second-look/scripts"))
from secondlook.history import ImportFailure, load, plain, validate_record


def gpt():
    return {"id": "gpt-1", "title": "Workshop", "current_node": "b", "mapping": {
        "root": {"parent": None, "message": None},
        "a": {"parent": "root", "message": {"author": {"role": "user"}, "content": {"content_type": "text", "parts": ["Plan a workshop."]}}},
        "b": {"parent": "a", "message": {"author": {"role": "assistant"}, "content": {"content_type": "text", "parts": ["45 minutes."]}}},
        "c": {"parent": "a", "message": {"author": {"role": "assistant"}, "content": {"content_type": "text", "parts": ["60 minutes."]}}}}}


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_active_branch_only(self):
        r = load(self.write("a.json", [gpt()]))
        self.assertEqual(len(r), 1)
        self.assertEqual([m["text"] for m in r[0]["messages"]], ["Plan a workshop.", "45 minutes."])

    def test_ambiguous_branches_never_merge(self):
        data = gpt()
        del data["current_node"]
        records = load(self.write("a.json", [data]))
        self.assertEqual(len(records), 2)
        self.assertNotEqual(records[0]["key"], records[1]["key"])
        for r in records:
            self.assertIn("active_branch_unknown", r["warnings"])
            self.assertEqual(len(r["messages"]), 2)

    def test_native_identity_survives_file_copy(self):
        a = load(self.write("a.json", [gpt()]))[0]
        b = load(self.write("b.json", [gpt()]))[0]
        self.assertEqual((a["key"], a["fingerprint"]), (b["key"], b["fingerprint"]))
        self.assertNotEqual(a["locator"], b["locator"])

    def test_missing_active_node_rejected(self):
        data = gpt()
        data["current_node"] = "absent"
        with self.assertRaises(ImportFailure):
            load(self.write("a.json", data))

    def test_missing_parent_and_cycle_rejected(self):
        for parent in ("absent", "b"):
            data = gpt()
            data["mapping"]["a"]["parent"] = parent
            with self.subTest(parent=parent), self.assertRaises(ImportFailure):
                load(self.write("a.json", data))

    def test_multimodal_omission_is_visible(self):
        data = gpt()
        data["mapping"]["a"]["message"]["content"] = {"content_type": "multimodal_text", "parts": ["See image", {"content_type": "image_asset_pointer", "asset_pointer": "private"}]}
        r = load(self.write("a.json", data))[0]
        self.assertEqual(r["messages"][0]["text"], "See image")
        self.assertIn("attachment_or_nontext_omitted", r["warnings"])

    def test_claude_export_content_not_duplicated(self):
        data = [{"uuid": "c1", "name": "Plan", "chat_messages": [
            {"uuid": "m1", "sender": "human", "text": "Same text", "content": [{"type": "text", "text": "Same text"}], "attachments": [{"name": "missing.pdf"}]}]}]
        r = load(self.write("c.json", data))[0]
        self.assertEqual(r["messages"][0]["text"], "Same text")
        self.assertEqual(r["messages"][0]["role"], "user")
        self.assertTrue(r["warnings"])

    def test_text_roles_and_fences(self):
        records = plain("# User\nPlease check\n```text\nAssistant: inside code\n```\n# Assistant\nOK\n用户：预算改变了", self.root / "a.md")
        self.assertEqual([m["role"] for m in records[0]["messages"]], ["user", "assistant", "user"])
        self.assertIn("Assistant: inside code", records[0]["messages"][0]["text"])
        self.assertEqual(records[0]["messages"][2]["text"], "预算改变了")

    def test_unstructured_text_is_unknown(self):
        r = plain("A decision note, not role-tagged.", self.root / "a.txt")[0]
        self.assertEqual(r["messages"][0]["role"], "unknown")
        self.assertEqual(r["completeness"], "unknown")

    def jsonl(self, rows):
        path = self.root / "session.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        return path

    def test_codex_duplicate_events_not_repeated(self):
        rows = [{"type": "session_meta", "payload": {"id": "s1"}},
                {"type": "event_msg", "payload": {"type": "user_message", "message": "Question"}},
                {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Question"}]}},
                {"type": "response_item", "payload": {"type": "function_call", "arguments": "DO NOT EXECUTE"}}]
        r = load(self.jsonl(rows))[0]
        self.assertEqual(len(r["messages"]), 1)
        self.assertEqual(r["completeness"], "partial")
        self.assertIn("tool_or_reasoning_events_omitted", r["warnings"])

    def test_codex_event_only_fallback(self):
        r = load(self.jsonl([{"type": "event_msg", "payload": {"type": "agent_message", "message": "Answer"}}]))[0]
        self.assertEqual(r["messages"][0]["text"], "Answer")

    def test_claude_code_branches_and_sidechain(self):
        def event(mid, parent, text, side=False):
            return {"type": "user", "sessionId": "s1", "uuid": mid, "parentUuid": parent, "isSidechain": side,
                    "message": {"role": "user", "content": text}}
        records = load(self.jsonl([event("a", None, "Root"), event("b", "a", "Branch B"), event("c", "a", "Branch C"), event("d", None, "Secret auxiliary", True)]))
        self.assertEqual(len(records), 2)
        self.assertTrue(all(len(r["messages"]) == 2 for r in records))
        self.assertTrue(all("sidechain_excluded" in r["warnings"] for r in records))

    def test_invalid_and_large_files(self):
        path = self.write("unknown.json", {"password": "not a chat"})
        with self.assertRaises(ImportFailure):
            load(path)
        with self.assertRaises(ImportFailure):
            load(path, 2)

    def test_normalized_corpus_roundtrip(self):
        record = load(self.write("a.json", gpt()))[0]
        record["key"] = "tampered"
        r = load(self.write("normalized.json", {"kind": "second-look-corpus", "schema_version": 1, "conversations": [record]}))[0]
        self.assertNotEqual(r["key"], "tampered")
        bad = copy.deepcopy(r)
        bad["messages"][1]["id"] = bad["messages"][0]["id"]
        with self.assertRaises(ImportFailure):
            validate_record(bad)


if __name__ == "__main__":
    unittest.main()
