# Contributing

Contribute improvements supported by a concrete failure or user need. Keep the main skill concise and portable. Do not add a permanent rule for every isolated example.

## Before a change

- Explain the user-facing failure and expected result.
- For a new transcript format, include a minimal **synthetic** or fully sanitized fixture with provenance/consent for any real-derived structure. Preserve branch and attachment semantics.
- Never submit personal chat exports, customer data, credentials, private evaluation runs, or actual account locators.
- Use development cases while tuning. Holdout cases are for a frozen skill/version; once used to tune, they are no longer held out for that experiment.

## Checks

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate.py
python3 tools/build.py
```

For skill behavior changes, compare the baseline and skill on the same evidence/model/tool budget using `tools/evaluate.py`. Report known limitations and negative results. Format validation alone does not establish usefulness.

For a platform compatibility claim, record host/version, installation route, history scope, exact tested behaviors, and any fallback. Follow `docs/compatibility.md`; don't upgrade unrelated rows.

Changes should preserve natural language invocation, no default background interruptions, result-first delivery, source provenance, meaningful validation, and user control over exclusions. Avoid hard-coded vendor tool names in the generic core.

## 中文

欢迎提交真实使用中发现的问题、经过脱敏的格式样本、平台安装验证和有依据的改进。请先描述具体失败，再提出修改；不要提交真实对话、客户资料、账号凭证或私人评测文件。保留测试集不能一边用于调参，一边声称仍是独立评测。贡献按项目 MIT 许可证发布。
