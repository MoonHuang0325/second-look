# Three second chances / 三份可以检查的新版成果

**All source conversations are synthetic.** The revised work below was generated in an independent Second Look exercise, then its code was rerun. [Try the input first](../../docs/quickstart.md) · [Complete answer](../../evals/observations/skill/answer.md) · [Strong-prompt comparison](../../evals/observations/README.md).

## Research pilot

**Before:** an assistant made an unapproved 6,000-yuan agency contract a prerequisite and proposed app-pitch questions.

**Later evidence:** the same project has six eligible volunteers, two possible free introductions, a 1,200-yuan budget and two people available for two hours weekly over three weeks. The user's decision is whether to try a manual service, not build an app. A similarly named festival is a separate, closed project.

**Delivered:** a plan for up to eight completed interviews, 800 yuan in incentives and 12 total person-hours, a 30-minute incident-based guide, an invitation draft, a note template and a decision worksheet. Bookings and findings are not invented. Week two has no spare capacity; delays may reduce completions.

[Read the complete plan](../../evals/observations/skill/answer.md#lantern-an-eight-interview-pilot-within-the-current-budget). Source: [history A1–A3 and B1–B3](../../skills/second-look/assets/demo/history.md); C1 is excluded.

中文：把“没钱请代理，所以先等着”改成符合现有资源的访谈试点。预算和工时算得通，不代表招募已经成功或需求已经得到验证。

## Offline search

**Before:** a note-search project stopped because the assistant insisted on hosted embeddings, contrary to the no-upload/no-API-budget constraint.

**Later evidence:** word and remembered-phrase search is enough for the first version.

**Delivered:** [standalone Python prototype](../../evals/observations/skill/atlas_search.py) with a local SQLite FTS5 index, separate indexing/querying, relative paths and matching excerpts. [Executed acceptance tests](../../evals/observations/skill/test_atlas.py) check unchanged source files, phrase matching, ordinary symlink exclusion, failed-rebuild preservation and querying without rereading the notes.

[Read usage and limits](../../evals/observations/skill/answer.md#atlas-a-working-local-word-and-phrase-search-draft). Source: [history D1–D3 and E1–E2](../../skills/second-look/assets/demo/history.md). Small fictional fixtures do not validate 12,000-note performance. FTS5 is required; token phrases are not byte-exact matching.

中文：先交付能运行的离线搜索，并说明验过什么、没验什么。这个示例不会读取你的真实笔记。

## Community application

**Before:** a community reading-group application became an investor pitch with invented customers, funding and clinical outcomes.

**Delivered:** a [163-word application main body](../../evals/observations/skill/cedar-application.txt), using exactly Need, Activity, Access and Evaluation. It restores the belonging goal, four free library sessions and accessible participation options. Enrollment and outcomes remain unknown; the separate budget and room access need confirmation.

[Read the reasoning and remaining checks](../../evals/observations/skill/answer.md#cedar-a-submission-ready-main-body-draft). Source: [history F1–F3](../../skills/second-look/assets/demo/history.md).

中文：完成一份符合表格要求的正文，不把“写完了正文”当成“可以免检查提交整个申请”。

## What this demonstrates

The outputs respond to later corrections and produce usable work. A strong ordinary prompt also produced all three deliverables on this pack. The skill's broader proposition—repeatable discovery, source discipline and review memory—still needs real-history and repeated-use validation.
