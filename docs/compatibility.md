# Compatibility / 兼容矩阵

Status date: 2026-09-05. “Tested” below means a specific observed check, not an entire ecosystem certification. All file-format fixtures are synthetic structural samples. Live end-to-end user efficacy is not established.

| Surface/capability | Status | Evidence or limitation |
| --- | --- | --- |
| Python helpers on macOS, Python 3.9.6 and 3.12.14 | Tested | 44 automated parser, ledger, CLI, packaging and installation tests in temporary directories, including demo extraction and upgrade rollback. |
| Skills CLI 1.5.23 project copy install | Tested mechanically on macOS | The published CLI entry was run with local v0.2.0 source and explicit Codex + Claude Code targets in a temporary project, telemetry disabled. Both folders received the core and demo. This does not test live host routing or the npm wrapper itself. |
| Generated demo code | Tested on macOS Python 3.9.6 and 3.12.14 | Both independent outputs were rerun: 8 baseline test methods and 2 skill test methods passed; test counts are not comparative quality scores. [Exercise limits](../evals/observations/README.md). |
| Standard skill/package structure | Tested locally | Frontmatter/resource checks and archive integrity tests. Native host acceptance is a separate check. |
| OpenAI plugin manifest | Tested locally | Bundled plugin schema validator; no marketplace approval implied. |
| ChatGPT mapping JSON | Limited support | Synthetic active branch, ambiguous leaves, malformed graph, duplicate import and attachment tests. |
| Claude chat_messages JSON | Limited support | Synthetic text/content and missing-attachment tests; no real-account export certification. |
| Codex session JSONL | Limited support | Synthetic response-message/event fallback; execution traces marked partial. |
| Claude Code session JSONL | Limited support | Synthetic parent branches/sidechain handling; interleaved/missing parents are flagged. |
| Markdown/TXT | Tested format behavior | Explicit roles, Chinese labels, fenced code and unstructured text fixtures. Original completeness stays unknown. |
| Codex native task history | Adapter guidance; unverified end-to-end | Host tools may expose task listing and turn reading. No personal account was scanned during development. |
| ChatGPT native history + plugin UI | Unverified | Requires actual exposed history tools and a supported plugin/skill installation surface. |
| Claude chat/Cowork search + skill upload | Unverified | Requires account availability and live installation/history tests. |
| Claude Code live skill invocation | Unverified | Installer is tested, but live host routing and history discovery require a session test. |
| Python helpers on GitHub-hosted Ubuntu, macOS and Windows; Python 3.9 and 3.12 | Tested in CI | The v0.1.0 release passed the 40-test suite, structural validation and package build in all six combinations on 2026-09-05. v0.2.0 adds four tests; its current checks are visible in [Actions](https://github.com/MoonHuang0325/second-look/actions/workflows/check.yml). [Run evidence](https://github.com/MoonHuang0325/second-look/actions/runs/33956459051). This does not establish live host integration. |
| Other operating systems / Python versions | Unverified | No compatibility claim beyond the observed combinations above. |
| Human usefulness / two-week reuse | Not run | See the evaluation protocol; no adoption statistics are available. |

“格式测试通过”不等于“所有真实导出均支持”，“安装器通过”不等于“已在该产品中完整运行”。贡献者可以通过提交环境版本、无敏感数据的复现步骤与结果，逐项提升矩阵状态。

## Verification checklist per host

1. Install/uninstall without affecting existing user configuration.
2. Trigger a broad review and a focused review; check ordinary continuation does not trigger scanning.
3. Verify listing/search/fetch behavior and record actual coverage/completeness.
4. Deliver one independently checkable artifact with observed provenance.
5. Repeat the run; confirm exclusions, changed-source handling and persistence or explicit fallback.
6. Test unavailable history and missing attachments without fabricated access.

Record which steps passed. Do not upgrade a whole platform to “tested” after a manifest check alone.
