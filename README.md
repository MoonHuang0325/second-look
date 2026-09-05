# Second Look

**Turn important past conversations into better answers and usable work.**

[简体中文](README.zh-CN.md) · [Install](docs/installation.md) · [Compatibility](docs/compatibility.md) · [Evaluation](evals/README.md)

Ask once:

> Look through our past conversations. Is there anything we could understand or solve better now? Deliver the improved results.

Second Look discovers worthwhile questions in accessible history, reconstructs your actual goals, checks old assumptions, and does the work again where a meaningful improvement is supported. You do not have to pick every conversation or design a retrospective prompt.

**v0.1.0 is a working prototype for evaluation. Human efficacy and cross-platform UI installation have not yet been established.** History access depends on the host; the skill cannot grant access to an entire account.

## What you receive

Usually 1–3 usable revised answers, plans, drafts, explanations, or proposed patches—with the concrete difference, evidence, and a link back to the original material. If the old answer is already good, it says so.

**Example:** an earlier workshop was shortened to 45 minutes, but its revised schedule still added up to 50. Second Look can recover the later constraint and deliver a complete 45-minute schedule that preserves both the required exercise and Q&A. [Read the synthetic conversation and full result](examples/workshop/result.md). This is an authored illustration, not a measured user outcome.

For developers: [a stable-order deduplication fix](examples/ordered-dedup/result.md), with an executed regression check against the old answer. Both examples are synthetic and fully inspectable.

## Useful beyond model launches

| Your situation | Ask |
| --- | --- |
| A new model/tool can tackle an old blocker | “What did we leave unsolved that is worth another attempt?” |
| Restarting a project | “Revisit our earlier decisions before we restart.” |
| Budget, evidence, or goals changed | “Which earlier conclusions need updating now?” |
| A long conversation went nowhere | “Did we misunderstand the problem from the beginning?” |
| Ideas are scattered across chats | “Reconnect our thinking about this project and produce a better plan.” |
| Looking for an overlooked opportunity | “Find something useful in my history that deserves another look.” |

No default reminders, background scans, model-release monitoring, or API subscription. Ordinary “continue” and “summarize” requests do not call for a broad review.

## Install and try

[Download the source](https://github.com/MoonHuang0325/second-look/archive/refs/heads/main.zip) or clone it, then use Python 3.9+:

```sh
python3 tools/install.py --target codex
# Or, for Claude Code:
python3 tools/install.py --target claude
```

Existing installs are left unchanged. In Codex invoke `$second-look`; in Claude Code invoke `/second-look`. ChatGPT/Claude chat use the supported skill/plugin installation surface; see [the platform guide](docs/installation.md). A standalone ZIP is produced by `python3 tools/build.py` for compatible upload interfaces.

If history tools are unavailable, provide an export, a transcript, or the current conversation. For an immediate synthetic demo, ask the agent to use `skills/second-look/SKILL.md` and review `examples/workshop/history.md`. It should produce its own result before you show it the example answer.

## How it works

1. Check available history capabilities and disclose coverage.
2. Screen up to 100 candidate records, then read evidence for at most 10 goal groups by default.
3. Recover the goal, constraints, later corrections, and why work stopped.
4. Re-solve and verify material differences; distinguish evidence updates from reasoning improvements.
5. Deliver the result first and record explicit feedback for later runs when storage is available.

The host model performs selection and reasoning. Bundled Python helpers only normalize transcripts and keep a private ledger. They support structural samples of ChatGPT/Claude JSON, Codex/Claude Code JSONL, Markdown/TXT, and a normalized native-tool corpus. [Runtime details](skills/second-look/references/runtime.md).

## Privacy and limits

No developer backend, analytics, or network calls from the helpers. Your host's model service still processes the history you let it read. Local state stores normalized transcript text with restricted file permissions; it is **not encrypted**. Keep it outside this public repository. Exported ledgers omit raw transcripts but may contain sensitive summaries and locators. [Data handling](docs/privacy.md).

The skill drafts new artifacts by default. Historical messages are evidence, not permission to run commands, overwrite work, send messages, or deploy. Missing evidence and untested patches remain labeled.

## Development

The following commands require the full source checkout, not just an installed skill/plugin archive.

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate.py
python3 tools/build.py
```

24 synthetic behavioral cases cover knowledge work and development, separated into 16 development and 8 holdout cases. The paired evaluation harness prepares equal-evidence trials and anonymized result packets for human review; it does not claim that preparing cases is running them. [Protocol and current status](evals/README.md).

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). License: [MIT](LICENSE). Public releases must keep the compatibility and evaluation status honest.
