# Data handling / 数据处理

- The skill repository and Python helpers have no developer backend, telemetry, network client, automatic updater, or scheduler.
- The host model service processes any transcript content the host reads. Provider privacy, retention, and organizational settings still apply. “Local helpers” does not mean local inference.
- Import creates a private SQLite database with normalized message text, source metadata, and locators. New private directories use mode 0700 and database files mode 0600 where the operating system honors these permissions. Existing directory permissions are not changed. The database is not encrypted.
- Ledger exports exclude full message text, but summaries, paths, user feedback and checkpoints may remain sensitive. Keep them private too. Never attach real histories to public GitHub issues.
- Runtime storage inside the installed skill or marked public source repository is refused. Build archives use explicit source areas and do not include the private database, environment files, evaluation runs or raw exports.
- No raw user history is included in examples/evaluation cases. All shipped conversations are synthetic and marked accordingly.
- Historical commands and permissions are treated as evidence. The helper parses data and never executes embedded code. Reconsidering work does not authorize sending, deploying, or overwriting existing artifacts.
- Clear data by deleting the chosen private store through normal file controls after closing the helper. Uninstalling the skill alone does not delete separately stored history.

简要说明：没有开发者服务器或遥测，但模型平台仍会处理读取的内容。本地数据库包含对话文字且未加密；请放在私人目录。导出记录虽然不含原文全文，也不能默认公开。不要在公开 issue 中提交真实对话、令牌、个人信息或客户材料。

Security concerns should be reported without sensitive content through the repository owner's private reporting channel once available. Do not publish a working exploit containing another person's data. This project does not yet have a hosted support address.
