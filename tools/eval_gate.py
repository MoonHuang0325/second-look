#!/usr/bin/env python3
"""Mechanical evaluation gate over completed trial results.

This gate is the no-secrets CI layer of the evaluation protocol. It never runs a
model and never replaces human ratings: it validates completed trial artifacts
against mechanical expectations derived from each case's declared outcome, then
applies statistical guards on the human ratings.

Checks per trial (from evaluator-only-key expectations):
  - not_triggered / retain_original expectations must match the outcome the
    response self-declares (first line: `outcome: <label>`), when declared.
  - Any expectation marked `mechanical: true` in a case rubric entry is checked
    as a literal substring (prefix `!` for must-not-contain) against the response.

Guards:
  - required coverage: every prepared trial must have a recorded result and a
    human rating (use --allow-incomplete for development smoke runs).
  - critical failures: any rated critical failure fails the gate.
  - regression guard: skill arm must not score below baseline on usable_result
    by more than the exact McNemar margin for the paired sample at alpha=0.05
    (two-sided, exact binomial). Below the minimum pair count the guard reports
    INCONCLUSIVE instead of pretending significance.

Exit code 0 = PASS or INCONCLUSIVE-with-allowance, 1 = FAIL, 2 = usage error.
"""

import argparse
import json
import math
import sys
from pathlib import Path

OUTCOMES = ("supported_improvement", "direction_to_test", "retain_original", "not_triggered")


def declared_outcome(text):
    for line in text.splitlines()[:5]:
        if line.strip().startswith("outcome:"):
            value = line.split(":", 1)[1].strip()
            return value if value in OUTCOMES else None
    return None


def mechanical_checks(case_expected, response_text):
    """Return failed checks for rubric entries flagged mechanical.

    Accepts both forms: legacy strings ("Deliver ..."), and structured entries
    ({"check": "literal", "mechanical": true}; prefix "!" for must-not-contain).
    Legacy string rubrics are human-judgment criteria and are skipped.
    """
    failures = []
    if not isinstance(case_expected, dict):
        return failures
    for entry in case_expected.get("rubric", []):
        if isinstance(entry, str):
            continue
        if not isinstance(entry, dict) or not entry.get("mechanical"):
            continue
        check = entry["check"]
        if check.startswith("!"):
            if check[1:].casefold() in response_text.casefold():
                failures.append(check)
        elif check.casefold() not in response_text.casefold():
            failures.append(check)
    return failures


def mcnemar_exact_p(b, c):
    """Two-sided exact McNemar p-value for discordant pair counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def gate(output, allow_incomplete=False):
    output = Path(output)
    key_path = output / "evaluator-only-key.json"
    if not key_path.exists():
        raise ValueError("Run tools/evaluate.py prepare first; evaluator-only-key.json missing")
    key = json.loads(key_path.read_text(encoding="utf-8"))
    report = {"trials": len(key), "checked": [], "mechanical_failures": [],
              "outcome_mismatches": [], "missing": [], "critical_failures": [],
              "pairs": {"concordant_usable": 0, "skill_only": 0, "baseline_only": 0, "neither": 0}}
    ratings = {}
    for tid, meta in sorted(key.items()):
        result_path = output / (tid + ".result.json")
        rating_path = output / (tid + ".rating.json")
        if not result_path.exists() or not rating_path.exists():
            report["missing"].append(tid)
            continue
        result = json.loads(result_path.read_text(encoding="utf-8"))
        rating = json.loads(rating_path.read_text(encoding="utf-8"))
        ratings[tid] = (meta, result, rating)
        expected = meta.get("expected", {})
        expected_outcome = expected.get("outcome") if isinstance(expected, dict) else None
        actual_outcome = declared_outcome(result["response"])
        if expected_outcome in ("not_triggered", "retain_original") and actual_outcome \
                and actual_outcome != expected_outcome:
            report["outcome_mismatches"].append(
                {"trial": tid, "expected": expected_outcome, "declared": actual_outcome})
        for check in mechanical_checks(expected, result["response"]):
            report["mechanical_failures"].append({"trial": tid, "check": check})
        if rating["critical_failures"]:
            report["critical_failures"].append(
                {"trial": tid, "failures": rating["critical_failures"]})
        report["checked"].append(tid)
    # Paired comparison on usable_result (exact McNemar over discordant pairs).
    by_case = {}
    for tid, (meta, result, rating) in ratings.items():
        by_case.setdefault(meta["case_id"], {})[meta["arm"]] = rating["usable_result"]
    for case_id, arms in by_case.items():
        if set(arms) != {"baseline", "skill"}:
            continue
        b, s = arms["baseline"], arms["skill"]
        if b and s:
            report["pairs"]["concordant_usable"] += 1
        elif s:
            report["pairs"]["skill_only"] += 1
        elif b:
            report["pairs"]["baseline_only"] += 1
        else:
            report["pairs"]["neither"] += 1
    disc_b, disc_c = report["pairs"]["skill_only"], report["pairs"]["baseline_only"]
    report["mcnemar"] = {"discordant_pairs": disc_b + disc_c,
                         "skill_better": disc_b, "baseline_better": disc_c,
                         "p_two_sided": round(mcnemar_exact_p(disc_b, disc_c), 4)}
    hard_fail = (report["outcome_mismatches"] or report["mechanical_failures"]
                 or report["critical_failures"])
    if report["missing"] and not allow_incomplete:
        hard_fail = True
    # Regression: skill arm materially worse than baseline (one-sided direction).
    regressed = disc_c > disc_b and mcnemar_exact_p(disc_b, disc_c) < 0.10
    report["status"] = "FAIL" if hard_fail or regressed else (
        "INCONCLUSIVE" if disc_b + disc_c < 12 or report["missing"] else "PASS")
    report["interpretation"] = ("Mechanical checks and exact paired statistics over human ratings; "
                                "not proof of real-user usefulness. INCONCLUSIVE means insufficient "
                                "paired evidence, not failure.")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, help="Prepared evaluation directory")
    p.add_argument("--allow-incomplete", action="store_true",
                   help="Do not fail on unrated trials (development smoke runs)")
    p.add_argument("--require-pass", action="store_true",
                   help="Exit nonzero unless status is PASS (full-split gating)")
    args = p.parse_args()
    try:
        report = gate(args.output, args.allow_incomplete)
    except (ValueError, KeyError, OSError) as exc:
        p.exit(2, str(exc) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "FAIL" or (args.require_pass and report["status"] != "PASS"):
        sys.exit(1)


if __name__ == "__main__":
    main()
