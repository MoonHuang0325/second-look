# Security Policy

Second Look processes private conversation history. We take the confidentiality of
that data seriously: the bundled helpers make no network calls, send no telemetry,
and refuse to store private data inside the public repository or the installed skill.

## Supported Versions

| Version | Supported |
| --- | --- |
| 0.3.x | Yes |
| < 0.3.0 | No — please upgrade |

Only the latest minor release receives security fixes until 1.0.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues,
discussions, or pull requests.**

Use [GitHub Security Advisories](https://github.com/MoonHuang0325/second-look/security/advisories/new)
("Report a vulnerability") to open a private report. Include:

- The affected version and host (Codex, Claude Code, etc.)
- A description of the issue and its potential impact on private data
- Steps to reproduce or a proof of concept, if available

Do not include real private conversation content in any report; synthetic
reproductions are sufficient for every class of issue we anticipate.

## Response Commitments

| Stage | Target |
| --- | --- |
| Acknowledgement of your report | Within 7 days |
| Initial triage and severity assessment | Within 14 days |
| Fix or mitigation for confirmed issues | Within 60 days, coordinated with you before disclosure |

If the report is declined, we will explain why and, where possible, suggest a
better place to raise the concern.

## Scope Notes

- The helpers are standard-library Python and execute no transcript content; the
  host agent reads history as **evidence, not instructions** (prompt-injection
  resistance is part of the test suite). Bypasses of that evidence/instruction
  boundary are security issues we want to hear about.
- The local SQLite store is private (file-permission protected where the OS honors
  POSIX modes) but **not encrypted**. Physical-access threats are out of scope;
  please use full-disk encryption for that threat model.
