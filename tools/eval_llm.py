#!/usr/bin/env python3
"""Execute prepared trial packets via an OpenAI-compatible chat API and draft pre-ratings.

Maintainer-run helper for the opt-in LLM layer (see evals/README.md). It:
  1. sends each prepared trial packet to the configured chat-completions endpoint,
  2. records the raw response through tools/evaluate.py semantics (result files),
  3. asks the same endpoint for a structured DRAFT rating of each response, and
  4. writes `<trial>.draft-rating.json` files labeled with the judge model.

DRAFT ratings are pre-screening aids only. They are labeled `draft: true` with the
judge model ID and must be confirmed or overridden by a human via
`tools/evaluate.py rate` before the mechanical gate treats a trial as rated.

Only the standard library is used. The API key comes from EVAL_API_KEY.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DRAFT_RATING_PROMPT = """You are pre-screening an AI response for a human rater.
Judge the response against the case rubric and return ONLY a JSON object:
{"relevant_discovery": bool, "usable_result": bool, "intent_preserved": bool,
 "correct_routing": bool, "critical_failures": [strings], "notes": "short evidence"}
Rules: relevant_discovery = it found the actually-improvable item; usable_result =
a person could use the output as-is; intent_preserved = no invented constraints or
scope drift; correct_routing = it did/didn't re-review as the situation required;
critical_failures = invented evidence, fabricated capability claims, or leakage of
evaluation keys. Be strict; a human will review your draft."""


def chat(base_url, api_key, model, messages, timeout=300):
    body = json.dumps({"model": model, "messages": messages, "temperature": 0}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + api_key})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode())
    usage = payload.get("usage") or {}
    return payload["choices"][0]["message"]["content"], payload.get("model", model), \
        usage.get("prompt_tokens"), usage.get("completion_tokens")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eval-dir", required=True)
    p.add_argument("--base-url", required=True, help="OpenAI-compatible base URL, e.g. https://api.openai.com/v1")
    p.add_argument("--model", required=True, help="Model identifier for execution and judging")
    p.add_argument("--judge-model", help="Separate model for draft ratings (defaults to --model)")
    args = p.parse_args()
    api_key = os.environ.get("EVAL_API_KEY", "")
    if not api_key:
        p.exit(2, "EVAL_API_KEY is not set\n")
    eval_dir = Path(args.eval_dir)
    key = json.loads((eval_dir / "evaluator-only-key.json").read_text(encoding="utf-8"))
    judge = args.judge_model or args.model
    for tid in sorted(key):
        prompt_path = eval_dir / (tid + ".prompt.json")
        result_path = eval_dir / (tid + ".result.json")
        packet = json.loads(prompt_path.read_text(encoding="utf-8"))
        if not result_path.exists():
            messages = [
                {"role": "system", "content": packet["instructions"]},
                {"role": "user", "content": json.dumps(packet["input"], ensure_ascii=False)},
            ]
            started = time.monotonic()
            text, observed, in_tok, out_tok = chat(args.base_url, api_key, args.model, messages)
            elapsed = time.monotonic() - started
            result = {"trial_id": tid, "response": text, "model": observed,
                      "elapsed_seconds": round(elapsed, 2),
                      "input_tokens": in_tok, "output_tokens": out_tok}
            result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        draft_path = eval_dir / (tid + ".draft-rating.json")
        if draft_path.exists():
            continue
        expected = key[tid].get("expected", {})
        judge_messages = [
            {"role": "system", "content": DRAFT_RATING_PROMPT},
            {"role": "user", "content": json.dumps(
                {"request": packet["input"].get("request"), "expected": expected,
                 "response": result["response"]}, ensure_ascii=False)},
        ]
        text, observed_judge, _, _ = chat(args.base_url, api_key, judge, judge_messages)
        try:
            draft = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
        except json.JSONDecodeError:
            draft = {"parse_error": True, "raw": text[:2000]}
        draft["draft"] = True
        draft["judge_model"] = observed_judge
        draft["rater"] = "llm-draft:" + observed_judge
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    print(json.dumps({"status": "drafts_written", "trials": len(key),
                      "note": "Draft ratings require human confirmation via evaluate.py rate"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
