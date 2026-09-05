# Second Look

**Your important questions deserve another answer.**

![Second Look: rediscover, reconsider, deliver](assets/social-preview.png)

[简体中文](README.zh-CN.md) · [Try the demo](docs/quickstart.md) · [Install](docs/installation.md) · [Examples](examples/README.md) · [Compatibility](docs/compatibility.md)

[![Checks](https://github.com/MoonHuang0325/second-look/actions/workflows/check.yml/badge.svg)](https://github.com/MoonHuang0325/second-look/actions/workflows/check.yml) [![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Ask your agent:

> Look through our past conversations. Find something worth reconsidering, and deliver the improved work.

Second Look discovers worthwhile questions in **accessible** history, reconnects later corrections and constraints, and produces 1–3 usable answers, plans, drafts or proposed code changes. It shows the difference and evidence. When there is no supported improvement, it says so.

Built for people who already do meaningful work with AI: developers, creators, researchers and project owners. Useful when a project restarts, requirements change, a conversation goes in circles, or a new model/tool becomes available.

## See the work it can produce

The first-use pack contains six **synthetic conversations**. Try it before reading the example answers.

| Work that stalled | Evidence found later | Inspect the revised work |
| --- | --- | --- |
| A research pilot waiting for a 6,000-yuan agency budget | Six volunteers, two possible introductions and a smaller approved budget | [A feasible pilot plan and interview guide](examples/second-chance/README.md#research-pilot) |
| A note-search project blocked by cloud/API restrictions | The user only needs word/phrase search first | [An offline prototype and executed checks](examples/second-chance/README.md#offline-search) |
| An application written as an investor pitch | The user corrected the audience, purpose and required sections | [A complete community application](examples/second-chance/README.md#community-application) |

These demonstrate a method, not measured customer outcomes. The same pack was also tried with a strong review prompt: [read the comparison and limits](evals/observations/README.md). No claim of superiority, saved time or real-user adoption follows from these examples.

## Install and get a first result

For Codex or Claude Code with Node.js/npm available:

```sh
npx skills add MoonHuang0325/second-look --skill second-look
```

Choose your agent and installation scope in the installer. This is the third-party Skills CLI; it has optional installation telemetry. For no third-party installer, use the [download and Python route](docs/installation.md). Its details and tested scope are documented there.

Then start a new agent session and ask:

**Codex**

```text
$second-look Try the bundled synthetic demo. Deliver the work without reading my personal history.
```

**Claude Code**

```text
/second-look Try the bundled synthetic demo. Deliver the work without reading my personal history.
```

For your own work, ask “Revisit our earlier decisions before we restart this project” or “Find an overlooked opportunity in my history.” Available history depends on your host and permissions. If history tools are absent, use a transcript, export or the current conversation. [First-use walkthrough](docs/quickstart.md).

**v0.2.0 is a preview.** The Python runtime and packaging have automated checks; host-by-host personal-history discovery and human usefulness remain separate validation tasks. [Exact compatibility](docs/compatibility.md) · [Download packages](https://github.com/MoonHuang0325/second-look/releases/tag/v0.2.0).

## Why a skill?

A capable model can already do a good review with a good prompt. Second Look packages the repeatable parts: finding candidates, preserving sources and branches, distinguishing real improvements from rephrasing, and respecting what you already reviewed or closed. The Python helpers normalize files and maintain a private ledger; **they do not run a model**.

One invocation can screen up to 100 candidate records and read up to 10 goal groups by default. These are limits, not a promise of whole-account access. Repeated use can explore new material and skip unchanged reviewed goals when a ledger is available. [Method](skills/second-look/SKILL.md) · [Runtime](skills/second-look/references/runtime.md).

## Privacy and control

- No developer server, helper telemetry, default reminders or background scanning.
- Your host model service still processes what it reads. This is not all-local inference.
- Private history and review records stay outside the public repository. Local records are not encrypted.
- Historical instructions are evidence, not permission to execute them. New work is drafted separately by default.
- Sharing is opt-in: ask for a minimized share draft, review it, and decide whether to publish.

[Data details](docs/privacy.md) · [Update or uninstall](docs/installation.md#update-and-rollback).

## Help make it useful

[Report a problem](https://github.com/MoonHuang0325/second-look/issues/new/choose) · [Share feedback](https://github.com/MoonHuang0325/second-look/discussions) · [Contribute](CONTRIBUTING.md)

An install failure, a review that missed the point, or an example where nothing improved is useful feedback. Please do not upload raw private conversations. If you want to follow new cases and releases, **Star this repository**.

For maintainers: [development and evaluation](docs/development.md) · [launch action manual / 推广行动手册](https://github.com/MoonHuang0325/second-look/blob/main/docs/launch/action-manual.zh-CN.md).
