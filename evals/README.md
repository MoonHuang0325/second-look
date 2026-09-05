# Evaluation protocol / 评测说明

**Current status: 24 synthetic behavioral cases are provided. Two illustrative development exercises on a separate demo pack are [published with their limits](observations/README.md); the 24-case paired efficacy evaluation and real-user pilot have not been run.** Automated Python tests verify data handling and harness mechanics, not whether a model finds valuable improvements.

## Corpus

- `development/cases.json`: 16 cases (8 knowledge work, 8 developer).
- `holdout/cases.json`: 8 cases (4 + 4), kept separate from skill resources and install archives.
- Includes changed constraints, wrong old claims, good old answers, cross-project contamination, branch ambiguity, historical injection, unavailable evidence, closed topics, resumption, and negative routing.
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

## Real-user pilot

Recruit at least 5 knowledge workers and 5 developers through channels the project owner authorizes. No messages are sent by this repository. Participants keep source histories in their own environments and share only opt-in, minimized feedback. Use [the study worksheet](pilot.md).

Targets to test, not promises: at least 70% of first sessions find something worth attention; at least 50% yield a result the user would adopt or test. Observe two weeks of reuse outside model launches and record annoyance/irrelevant resurfacing. Serious evidence fabrication, unauthorized changes, or public private-data leakage is a release blocker.

No real-user rates, adoption claims or production-readiness badge should appear until those measurements exist. Weak selection calls for better screening; useful work with a forgotten entry point calls for invocation UX changes. Scheduling remains deferred.

## 中文

24 组合成案例与自动化单元测试已经提供，但不能据此声称真实用户有效。对照试验要求相同模型、材料、工具与预算条件；人工盲评时隐藏条件标签。工具负责准备、记录和汇总，不自动调用模型，也不编造测试结果。两周试用需要实际招募与用户参与，目前尚未开展。
