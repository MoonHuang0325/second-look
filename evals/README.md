# Evaluation protocol / 评测说明

**Current status: 40 synthetic behavioral cases are provided. Two illustrative development exercises on a separate demo pack are [published with their limits](observations/README.md); the paired efficacy evaluation and real-user pilot have not been run.** Automated Python tests verify data handling and harness mechanics, not whether a model finds valuable improvements.

## Corpus

- `development/cases.json`: 28 cases (14 knowledge work, 14 developer).
- `holdout/cases.json`: 12 cases (6 + 6), kept separate from skill resources and install archives.
- Includes changed constraints, wrong old claims, good old answers, cross-project contamination, branch ambiguity, historical injection (quoted content, code comments, log data), fake prior approval, exfiltration lures, unavailable evidence, closed topics, resumption, and negative routing.
- Every case includes a user request, actual synthetic message text with source locators, observable expectations, and critical failure conditions. The evaluator expectations are never included in a model prompt packet.
- This initial holdout split was created alongside the prototype and is not an independent benchmark. Freeze the skill before use; for stronger claims collect unseen cases from other contributors. Do not optimize against holdout results and continue calling them held out.

## Paired baseline versus skill

Prepare in a private directory outside the repository:

```sh
python3 tools/evaluate.py prepare --split development --output /tmp/second-look-evaluation
```

Each case produces two randomized trial IDs with identical source material. Baseline instructions are a plain request to revisit and improve; the treatment uses the actual skill and its supporting references. A separate evaluator-only key contains condition labels and expected outcomes.

Use isolated host contexts with the same observed model version, available tools, and declared time/token ceiling for both arms. The harness deliberately does not purchase API access, spawn agents, or claim to run a model. Run each packet through your authorized host. Record the actual response and observed resource usage; unknown token counts stay null. Giving both arms the same budget does not guarantee identical consumption; inspect the recorded values.

```sh
python3 tools/evaluate.py record --output /tmp/second-look-evaluation \
  --trial g01-1 --response /tmp/actual-response.md --model observed-model-id --elapsed 42
```

The `.blind.json` file removes condition and model metadata. Give only that file to a human rater, not the prompts or evaluator key. Response wording can still reveal the approach, so this is condition masking rather than guaranteed perfect blinding.

Human rating JSON must include:

```json
{
  "rater": "pseudonymous-rater-1",
  "relevant_discovery": true,
  "usable_result": true,
  "intent_preserved": true,
  "correct_routing": true,
  "critical_failures": [],
  "notes": "Specific evidence for this assessment"
}
```

```sh
python3 tools/evaluate.py rate --output /tmp/second-look-evaluation \
  --trial g01-1 --ratings /tmp/human-rating.json
python3 tools/evaluate.py summary --output /tmp/second-look-evaluation
```

Only actual human judgments should enter the rating files. Automated summaries report raw counts and flag mismatched model pairs; they are not statistical significance tests. Negative-routing and retain-original cases are not expected to produce a novel improvement. Inspect these separately when interpreting usefulness counts.

## Automated gate (two layers)

The protocol keeps its honesty rule — **no model self-rating, no LLM judged as a
human rater** — and splits automation into two layers:

1. **Mechanical gate (no secrets, every PR)** — `tools/eval_gate.py` runs over a
   completed evaluation directory and fails on: outcome mismatches for
   `not_triggered`/`retain_original` cases (from the response's self-declared
   `outcome:` line), failed `{"check": ..., "mechanical": true}` rubric entries
   (literal must-contain / `!` must-not-contain), any human-rated critical
   failure, and statistically significant regression of the skill arm versus
   baseline on `usable_result` (exact McNemar over discordant pairs). With
   fewer than 12 discordant pairs or incomplete coverage it reports
   **INCONCLUSIVE**, never a pretend PASS. It never calls a model.
2. **LLM-assisted pre-rating (opt-in, secrets)** — a maintainer-run workflow
   (`.github/workflows/eval-llm.yml`, manual dispatch) executes packets through
   an authorized API and produces *draft* ratings for a human rater to confirm
   or override via `evaluate.py rate`. Draft ratings are labeled with the judge
   model ID and are not accepted as human judgments.

CI runs `tools/eval_gate.py` on every pull request over any committed completed
evaluation directory (none is committed by default; results stay private).
Maintainers attach a completed directory to trigger the gate in CI.

## Evidence status

The paired 24-case model evaluation and real-user usefulness study remain uncompleted. Contributors can report an observed result with the host/version, actual accessible material, exact behavior and a minimal synthetic reproduction. Do not publish private histories or infer population-wide outcomes from a few examples.

Automated checks establish parser, ledger and packaging behavior. The [two development exercises](observations/README.md) show generated artifacts and limits; neither supplies an adoption rate or proof of superiority.

## 中文

欢迎提供可复现的失败或平台行为记录。测试通过与合成演示不等于真实用户有效。保留相同模型、材料、工具和预算条件；未知资源消耗如实留空，人工评价不能由模型自评分代替。
