# Installation / 安装

The repository contains one canonical skill at `skills/second-look`. Python helpers require Python 3.9+; reasoning uses your host model, not a separate API key. Without Python, the core instructions still work on visible text using host tools.

[Download the v0.1.0 prototype packages / 下载原型安装包](https://github.com/MoonHuang0325/second-look/releases/tag/v0.1.0). Choose the standard skill ZIP for compatible custom-skill uploads, or the OpenAI plugin ZIP for supported plugin surfaces. For the local installer below, download the full source checkout.

## Codex local / Codex 本地

From an extracted source checkout:

```sh
python3 tools/install.py --target codex
```

This copies the skill into `~/.agents/skills/second-look`. For a permitted custom skills directory, use `--dest /absolute/path/to/skills`. Existing installs are never overwritten; retain a backup and remove/move the old installation yourself before reinstalling. Do not put private history in the install folder.

Invoke `$second-look`, or ask “Find useful questions in my history worth reconsidering.” If the skill does not appear, start a new task/reload the host. Tool availability varies between desktop, CLI, and cloud. A skill cannot create missing history APIs.

安装器不会覆盖已有版本。安装后在 Codex 中调用 `$second-look`；未出现时重新开启任务或重新加载宿主。桌面、CLI 与云端的历史读取能力可能不同。

## Claude Code

```sh
python3 tools/install.py --target claude
```

This copies the same skill to `~/.claude/skills/second-look`. Invoke `/second-look`. The standard frontmatter intentionally avoids Claude Code-only fields so the core can also be packaged for other supported skill surfaces.

## Claude chat / Cowork

Build `dist/second-look-0.1.0-skill.zip` with `python3 tools/build.py`. On an account with custom skill uploads enabled, upload that standard skill ZIP through the product's Skills settings and enable it. Ask for Second Look in a conversation. Follow [Claude's current skills guidance](https://code.claude.com/docs/en/skills) for account-specific availability.

This upload flow is not yet live-tested for this repository. Conversation search may be restricted by plan/project. If it cannot access history, provide an export or visible text; installation does not remove restrictions.

## ChatGPT / OpenAI plugin distribution

`dist/second-look-0.1.0-openai-plugin.zip` contains the plugin manifest and the same skill. It is a distribution artifact, not an approved marketplace listing. Public directory submission and account-specific installation remain release tasks. [OpenAI's skill/plugin guide](https://learn.chatgpt.com/docs/build-skills) describes supported distribution surfaces.

For immediate use on an accessible local host, use the Codex installation above. If only an ordinary chat is available, supply the skill instructions and selected transcript as context; describe this as a manual fallback, not a native skill installation or whole-history integration.

OpenAI 插件包已经提供构建方式，但不等于已上线插件市场。聊天界面的安装与历史能力必须按账号实测；受限时使用当前对话或导出文件，不声称已自动访问全账号。

## Try without personal data

Ask the host to load `skills/second-look/SKILL.md` and review `examples/workshop/history.md`. Do not give it the demonstration result first. Inspect whether it produces a complete 45-minute plan with the required activities and valid arithmetic.

For helper-only smoke testing from the source checkout, choose a private directory outside the repository:

```sh
python3 skills/second-look/scripts/second_look.py --store /tmp/second-look-demo import examples/workshop/history.md
python3 skills/second-look/scripts/second_look.py --store /tmp/second-look-demo candidates
```

These commands only import/index the synthetic example. They do not run a model or perform a review. Native history tools should be preferred over export when actually available. See [runtime instructions](../skills/second-look/references/runtime.md).

## Remove

Remove only the installed `second-look` folder through your normal file controls. Private data is stored separately in the directory selected with `--store` (default `~/.local/share/second-look`) and is not deleted by uninstalling the skill. Remove that directory separately if you want to erase local history/ledger data. No background job needs removal.
