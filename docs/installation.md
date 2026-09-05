# Installation / 安装

One canonical core supports compatible Agent Skills hosts. Python helpers require Python 3.9+ and no additional API service. Without Python, a host can still review visible text. A skill cannot grant missing history access.

## Fast route: Skills CLI

With Node.js/npm available:

```sh
npx skills add MoonHuang0325/second-look --skill second-look
```

Select your installed agent and project/personal scope when prompted (the CLI may select noninteractive defaults in an agent environment). For an explicit project install:

```sh
npx skills add MoonHuang0325/second-look --skill second-look -a codex claude-code --copy
```

This uses the third-party [Skills CLI](https://github.com/vercel-labs/skills), not a service supplied by Second Look. Its optional installation telemetry can be disabled with `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1`; see [the CLI documentation](https://www.skills.sh/docs/cli). The project itself has no telemetry. Directory visibility and rankings are not guaranteed by this command.

## Download and Python route

Download a source archive from the [v0.2.0 preview release](https://github.com/MoonHuang0325/second-look/releases/tag/v0.2.0), extract it, and run from its folder:

```sh
python3 tools/install.py --target codex
# Or, for Claude Code:
python3 tools/install.py --target claude
```

Targets are `~/.agents/skills/second-look` and `~/.claude/skills/second-look`. `--dest /absolute/path/to/skills` selects another permitted skills directory. The installer never replaces an existing install unless `--upgrade` is supplied.

Start a new host session. In Codex invoke `$second-look`; in Claude Code invoke `/second-look`. Try the [bundled synthetic demo](quickstart.md) before personal history. See [OpenAI's current skills guide](https://learn.chatgpt.com/docs/build-skills) and [Claude Code's skill guide](https://code.claude.com/docs/en/skills) for host-specific discovery and settings.

## Update and rollback

For installs made with this repository's Python installer, download the newer source, then:

```sh
python3 tools/install.py --target codex --upgrade
# Or:
python3 tools/install.py --target claude --upgrade
```

The old folder is moved into a unique backup under `~/.agents/second-look-backups` or `~/.claude/second-look-backups`, outside the active skills directory. The installer prints its exact location. User-added files remain in that backup; review and reapply customizations separately. Private review records are not modified. A failed final installation move restores the previous folder.

To roll back, close active agent sessions, move the new `second-look` folder aside, and move the printed backup folder back to the original `second-look` location. Start a new session. Keep the backup until satisfied.

For symlink installs or installs managed by another tool, update with that original tool. This Python installer refuses to replace a symlink. Never store private histories inside the skill folder.

中文：升级需要明确加上 `--upgrade`，旧版本自动备份，私人复盘记录不变。回退时把备份移回原位置即可；使用其他安装器创建的链接，请用原安装器升级。

## Claude chat / Cowork and OpenAI plugin surfaces

The release includes a standard `second-look-0.2.0-skill.zip` and `second-look-0.2.0-openai-plugin.zip`, generated from the same core. Use the standard ZIP only on a product/account that exposes compatible custom-skill uploads. The plugin ZIP is a distribution artifact, not a marketplace approval or promise of ChatGPT chat installation.

These account-specific native upload, routing and whole-history flows remain unverified for this release. Do not assume Claude Code installation also installs Claude chat, or that a Codex folder exposes all ChatGPT conversations. [Exact compatibility](compatibility.md).

If native installation is unavailable, supply the [core instructions](../skills/second-look/SKILL.md) and a selected transcript as visible context. This is a manual fallback, not a native installation. The model should state the material it can actually read.

## Remove

Remove the installed `second-look` folder through your normal file controls or original installer. Separately stored private data (default `~/.local/share/second-look`, or your `--store` directory) and backups remain until you delete them explicitly. No background job needs removal.
