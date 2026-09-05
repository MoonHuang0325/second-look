# First result / 第一次得到成果

Choose the section matching what you want now. You do not need to configure a review mode inside the skill.

## Try without personal data / 不提供私人对话，先试一次

Install with [the platform guide](installation.md), start a new host session, and ask:

```text
$second-look Try the bundled synthetic demo. Deliver the usable results without reading my personal history.
```

In Claude Code, replace `$second-look` with `/second-look`. 中文可说：“用自带的合成案例演示一次，直接交付成果，不读取我的私人历史。”

The agent should load the bundled start request and six-conversation history pack. It should reconstruct the relevant goals and deliver work with source IDs. If it only lists opportunities, ask it to complete the selected work. Sample answers are for comparison after your own run, not an answer to paste in first.

Without installation, give a file-capable agent the repository's `skills/second-look/SKILL.md` and its linked references, then the bundled demo `START.md` and `history.md`. This is a manual instruction fallback, not proof of native skill invocation. In a text-only chat, provide the relevant file contents yourself.

If you prefer visible local demo files, from the extracted source run:

```sh
python3 skills/second-look/scripts/second_look.py demo --output ../second-look-demo
```

This creates a **new** folder with `START.md` and `history.md`. Existing paths are refused. It does not call a model, search an account, create a database, or produce an answer. Give those files to your agent with the skill enabled.

## Use your own work / 回到自己的工作

> 这个项目准备重新开始。请找相关历史，检查旧想法现在还成立吗，直接给我适合现在的方案。

Or ask for broad discovery:

> 以前有没有被我放下、但现在值得继续的事情？请找出来并尝试解决。

Expect a short statement of actual accessible sources, followed by 1–3 results or a clear explanation of why no supported improvement was found. Check sources and uncertain assumptions before adopting the result.

If history access is absent, attach one relevant transcript or export. The skill cannot add missing account APIs. Do not buy an API service for the bundled helper; it only performs local data handling.

## Repeat use / 第二次使用

Tell it “这件事已经结束” or “以后别再推荐这个主题” when that is your preference. You can undo the exclusion later. With storage, unchanged reviewed goals can be skipped. Without storage, keep the exported ledger and provide it next time; there is no promised cross-chat memory without it.

## If something goes wrong / 卡住时

| What you see | Next step |
| --- | --- |
| Skill not recognized | Start a new host session; check the correct platform directory in the install guide. |
| No history tools | Use supplied text or an export. Report the host/version and missing capability, not raw history. |
| Only opportunities, no revised work | Ask for a complete result for the selected goal; report the behavior if it repeats. |
| Missing attachments or old truncated messages | Supply the relevant original material or accept a narrower, explicitly uncertain result. |
| Same recommendation every time | Check that the same private ledger is available and the goal was recorded after delivery. |
| Sample command created files but no answer | File preparation is not model execution. Give the files to your agent. |

[Report an installation problem](https://github.com/MoonHuang0325/second-look/issues/new/choose). The sample exercise demonstrates supplied-text handling; it does not establish whole-account discovery or real-user effectiveness.
