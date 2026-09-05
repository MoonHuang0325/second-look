# Second Look v0.1.0 — prototype

Second Look revisits accessible conversation history to discover worthwhile unresolved questions and deliver improved answers or usable work. It supports both knowledge work and developer workflows, with no default background reminders or extra model API service.

## Included

- Portable Agent Skill, standard skill ZIP and OpenAI plugin packaging.
- Capability-aware native history guidance and loss-aware local transcript importers.
- Private, transactional corpus and review ledger with duplicate suppression, explicit feedback, changed-source handling and resumable runs.
- English/Chinese documentation and complete synthetic workshop and code-fix demonstrations.
- 24 synthetic behavioral cases, separated into development/holdout sets, plus paired-trial preparation and human-rating tools.

## Validation and limits

40 local automated tests pass on macOS with Python 3.9.6 and 3.12.14. Skill and plugin structure validation passes. Archives are reproducible and installed helpers run without third-party packages.

These checks do not establish model efficacy, real-user adoption or every host's live compatibility. Paired model experiments, live ChatGPT/Claude installation/history checks and the two-week user pilot remain pending. See the compatibility matrix and evaluation protocol before making broader claims.

This release is a prototype, not a production-efficacy claim. No private user histories are included; all examples and evaluation cases are synthetic. Helpers have no telemetry or network client, but the host model service processes content it reads, and the local database is not encrypted.

中文：首个可安装原型，包含通用 skill、历史解析、私人复盘记录、双语说明和 24 组合成评测案例。40 项本地自动化测试通过；真实用户效果和部分平台端到端验证尚未完成。默认不启用后台提醒，也不声称能读取所有平台的全账号历史。
