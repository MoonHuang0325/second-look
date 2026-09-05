<p align="center"><img src="assets/icon.png" width="64" alt="Second Look"></p>

# Second Look

**Turn unfinished AI conversations into work you can use.**

A project stalled. Your constraints changed. The model missed the point. Second Look finds worthwhile questions in accessible history, rethinks them, and delivers a revised plan, answer, draft or proposed code change—with sources you can check.

[简体中文](README.zh-CN.md) · [See a result](#from-stalled-to-actionable) · [Try it](#try-it) · [Install options](docs/installation.md)

[![Checks](https://github.com/MoonHuang0325/second-look/actions/workflows/check.yml/badge.svg)](https://github.com/MoonHuang0325/second-look/actions/workflows/check.yml) [![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Look through our past conversations. Find something worth reconsidering, and deliver the improved work.

## From stalled to actionable

![Synthetic example: an agency-dependent research plan becomes a bounded interview pilot](assets/second-chance.png)

**Old answer:** wait for a 6,000-yuan research agency budget.

**Later context:** six volunteers, two possible introductions, a 1,200-yuan cap and 12 total person-hours.

**Revised work:** a plan for up to eight interviews, 800 yuan in incentives, a 30-minute guide and a decision worksheet. Bookings and findings remain unverified.

[Read the full plan and its sources →](examples/second-chance/README.md#research-pilot)

Two more complete results: [an offline search prototype with executed checks](examples/second-chance/README.md#offline-search) · [a community application rewritten to the actual brief](examples/second-chance/README.md#community-application).

*These are actual generated outputs from synthetic history, not customer testimonials. [Inputs, comparison and limits](evals/observations/README.md).*

## Try it

**Codex or Claude Code** · Node.js/npm for this installation route:

```sh
npx skills add MoonHuang0325/second-look --skill second-look
```

Select your agent and scope when prompted, then start a new session. [Without Node / download options](docs/installation.md). The third-party installer has optional installation telemetry; [opt-out details](docs/installation.md#fast-route-skills-cli).

Start with the bundled demo; it uses no personal history:

| Your agent | Paste this |
| --- | --- |
| Codex | `$second-look Try the bundled synthetic demo. Deliver the work without reading my personal history.` |
| Claude Code | `/second-look Try the bundled synthetic demo. Deliver the work without reading my personal history.` |

**No compatible skill host?** [Try one self-contained example](examples/try-in-chat.md) by pasting it into your current AI chat. It is a manual review sample; it does not install the skill or discover other conversations.

For your own work, ask:

> Revisit our earlier decisions before we restart this project. Use the latest constraints and give me an updated plan.

**Expected:** 1–3 usable results, each showing what changed, why it holds up, and where the original material came from. If nothing meaningfully improves, Second Look can keep the original conclusion. [First-use walkthrough](docs/quickstart.md).

## Useful beyond model upgrades

| When | What to ask |
| --- | --- |
| A model or tool changes | “Can we solve something we got stuck on before?” |
| A project restarts | “Which earlier assumptions still hold?” |
| Budget, deadline or scope changes | “Update the old plan for these constraints.” |
| The conversation keeps going in circles | “Did we misunderstand the goal from the start?” |
| A topic spans several chats | “Bring the relevant ideas together and work through them again.” |
| You want to rediscover unfinished work | “Find something I set aside that's worth another look.” |

## What it can read

Second Look uses the history tools your host actually exposes. When those are unavailable, it can work with supplied Markdown/TXT, supported exports or visible conversation text. It cannot unlock whole-account history. [Formats and exact compatibility](docs/compatibility.md).

The optional Python helpers normalize files and maintain a private review ledger. They do not run a model. With persistence, unchanged reviewed goals and explicitly closed topics can be skipped on later runs; without it, cross-chat memory needs an exported ledger. [How it works](skills/second-look/SKILL.md).

## Your history stays under your control

No Second Look server, helper telemetry, extra API service or default background scanning. Your host model still processes the material it reads. Local review records are separate from this repository and are not encrypted. Historical instructions are treated as evidence; revised work is delivered separately by default. [Privacy](docs/privacy.md) · [Update, rollback and uninstall](docs/installation.md#update-and-rollback).

<details>
<summary><strong>Why a skill instead of a good prompt?</strong></summary>

A strong prompt can produce a good review. Both approaches did well on our public synthetic pack. Second Look packages the repeatable workflow: discover candidates, restore later corrections, preserve sources, verify changes and remember prior reviews when storage exists. The [comparison](evals/observations/README.md) does not establish superior reasoning or real-user adoption.

</details>

**Preview release:** installation and Python tooling have automated checks; account-specific native history workflows and human usefulness remain under validation. [Downloads](https://github.com/MoonHuang0325/second-look/releases/tag/v0.2.1) · [Compatibility](docs/compatibility.md) · [Changelog](CHANGELOG.md).

[Report a problem](https://github.com/MoonHuang0325/second-look/issues/new/choose) · [Ask a question](https://github.com/MoonHuang0325/second-look/discussions) · [Contribute](CONTRIBUTING.md)

Found a useful second look? Star the repository to find it again. Feedback about a missed goal or an unchanged answer is welcome; please keep private transcripts out of public issues.
