import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import eval_gate  # noqa: E402


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


class GateFixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        self.key = {
            "c01-1": {"case_id": "c01", "arm": "baseline", "audience": "knowledge",
                      "expected": {"outcome": "supported_improvement",
                                   "rubric": [{"check": "45 minutes", "mechanical": True}]}},
            "c01-2": {"case_id": "c01", "arm": "skill", "audience": "knowledge",
                      "expected": {"outcome": "supported_improvement",
                                   "rubric": [{"check": "45 minutes", "mechanical": True}]}},
            "c02-1": {"case_id": "c02", "arm": "baseline", "audience": "developer",
                      "expected": {"outcome": "retain_original", "rubric": []}},
            "c02-2": {"case_id": "c02", "arm": "skill", "audience": "developer",
                      "expected": {"outcome": "retain_original", "rubric": []}},
        }
        write(self.root / "evaluator-only-key.json", self.key)

    def complete(self, responses=("outcome: supported_improvement\n45 minutes",) * 2
                 + ("outcome: retain_original\nkept",) * 2,
                 usable=(False, True, False, True), critical=None):
        for i, tid in enumerate(sorted(self.key)):
            write(self.root / (tid + ".result.json"),
                  {"trial_id": tid, "response": responses[i], "model": "m1", "elapsed_seconds": 1})
            write(self.root / (tid + ".rating.json"),
                  {"rater": "r1", "relevant_discovery": True, "usable_result": usable[i],
                   "intent_preserved": True, "correct_routing": True,
                   "critical_failures": (critical or {}).get(tid, [])})

    def gate(self, allow_incomplete=False):
        return eval_gate.gate(self.root, allow_incomplete)


class TestGate(GateFixture):
    def test_incomplete_fails_without_flag(self):
        self.complete()
        (self.root / "c02-2.rating.json").unlink()
        report = self.gate()
        self.assertEqual(report["missing"], ["c02-2"])
        self.assertEqual(report["status"], "FAIL")
        report = self.gate(allow_incomplete=True)
        self.assertEqual(report["status"], "INCONCLUSIVE")

    def test_mechanical_and_outcome_failures(self):
        self.complete(responses=("outcome: supported_improvement\nno duration",) * 4)
        report = self.gate()
        self.assertEqual(len(report["mechanical_failures"]), 2)
        self.complete(responses=("outcome: supported_improvement\n45 minutes",) * 2
                      + ("outcome: supported_improvement\nchanged it anyway",) * 2)
        report = self.gate()
        self.assertEqual(len(report["outcome_mismatches"]), 2)
        self.assertEqual(report["status"], "FAIL")

    def test_critical_failure_fails(self):
        self.complete(critical={"c01-2": ["invented evidence"]})
        self.assertEqual(self.gate()["status"], "FAIL")

    def test_small_samples_are_inconclusive_not_pass(self):
        self.complete()
        report = self.gate()
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["pairs"]["skill_only"], 2)

    def test_regression_direction_fails(self):
        key = {}
        for i in range(10):
            for number, arm in enumerate(("baseline", "skill"), 1):
                key["r%02d-%d" % (i, number)] = {
                    "case_id": "r%02d" % i, "arm": arm, "audience": "knowledge",
                    "expected": {"outcome": "supported_improvement", "rubric": []}}
        write(self.root / "evaluator-only-key.json", key)
        self.key = key
        self.complete(responses=("outcome: supported_improvement\nx",) * 20,
                      usable=tuple(i % 2 == 0 for i in range(20)))
        report = self.gate()
        self.assertEqual(report["mcnemar"]["baseline_better"], 10)
        self.assertEqual(report["status"], "FAIL")

    def test_cli_contract(self):
        self.complete()
        run = subprocess.run([sys.executable, str(ROOT / "tools/eval_gate.py"),
                              "--output", str(self.root), "--allow-incomplete"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)
        self.assertIn(report["status"], ("INCONCLUSIVE", "PASS"))
        run = subprocess.run([sys.executable, str(ROOT / "tools/eval_gate.py"),
                              "--output", str(self.root), "--require-pass"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)


if __name__ == "__main__":
    unittest.main()
