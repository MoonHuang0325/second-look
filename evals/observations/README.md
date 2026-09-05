# Two development exercises, including a strong baseline

On 2026-09-05 two independent agent contexts received the same [six synthetic conversations](../../skills/second-look/assets/demo/history.md). One received Second Look's core and references; the other received a strong ordinary review request. Neither received example answers or the 24-case evaluation keys. The two contexts inherited the host configuration; the exact model identifier and token consumption were not exposed. Both were asked to stay near 12 tool calls and 3,000 answer words. Actual time/tool consumption was not captured reliably.

The baseline request asked it to select worthwhile work, recover current goals and constraints, connect only relevant conversations, produce 1–3 complete revised deliverables, preserve source IDs, verify code and arithmetic, avoid unsupported claims, and use no personal history. This is a capable baseline, not a deliberately weak summary prompt.

| Observed output | Strong review prompt | Second Look |
| --- | --- | --- |
| Revised work | Offline search code, pilot plan, application | Offline search code, pilot plan, application |
| Research arithmetic | 800 yuan, 12 person-hours | 800 yuan, 12 person-hours |
| Application length, including headings and numeric tokens | 186 English words | 163 English words |
| Search verification reported by each run | 8 test methods + CLI smoke check passed | 2 broader test methods + CLI smoke check passed |
| Unrelated closed festival | Excluded | Excluded |
| Real-scale search performance | Not measured | Not measured |
| Saved review record | Not produced | Three records in a private synthetic-data store |

Test-method counts reflect different organization, not relative quality or coverage. The baseline was not asked to maintain a ledger; that difference is not evidence of superior reasoning. Both outputs handled the central requirements. There is no declared winner.

Read the complete [baseline answer](baseline/answer.md) and [skill answer](skill/answer.md), including their code and tests. These are actual generated artifacts, not prewritten expected answers. Execution-directory prefixes were removed and verification-log references redirected to this summary to make links and commands portable; no substantive answer was rewritten. Raw execution logs and private runtime stores are not published. The skill answer calls the application “submission-ready main-body”; the separate budget and room-access checks remain outstanding, so it is not a completed submission.

To rerun the two generated code suites from the repository root:

```sh
python3 -m unittest discover -s evals/observations/baseline -p 'test_atlas.py' -v
python3 -m unittest discover -s evals/observations/skill -p 'test_atlas.py' -v
```

These original exercise tests require a Python build with SQLite FTS5 and permission to create symlinks. They were rerun on macOS with Python 3.9 and 3.12. They are not part of the cross-platform runtime CI claim. Tests create only fictional temporary notes. Source hashes and query-without-source checks demonstrate specific behavior, not production scale or resilience against concurrent hostile filesystem changes.

This is an illustrative development comparison: one pack, one output per condition, no blinded human ratings, and incomplete resource measurements. It does **not** establish that Second Look outperforms a strong prompt, saves time, or meets real-user usefulness targets. The original [24-case protocol](../README.md) and real-user usefulness studies remain to be run. The demo pack is public development material, never a holdout benchmark.
