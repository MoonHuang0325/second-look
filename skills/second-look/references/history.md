# History adapters

Discover tools actually exposed by the host. Never manufacture an API or use browser scraping/private endpoints. If native tools work, do not ask for an export first. Installation does not grant account permissions.

| Environment | Preferred path | Limits |
| --- | --- | --- |
| Codex desktop | Exposed task listing/search/read tools, e.g. `list_threads`, `list_archived_threads`, `read_thread`; paginate within budget. | Summaries/truncated outputs are not full transcripts. Follow cursors where available. Listing may not be exhaustive. |
| ChatGPT | Exposed history search/list/read tools. | Installation alone does not grant enumeration. Memory is a discovery clue, not proof of a full conversation. |
| Claude chat/Cowork | Exposed conversation search/fetch tools; vary topic and time when supported. | Search may be project-restricted or snippet-only. Hits are not the whole account. |
| Codex CLI / Claude Code | Permitted local transcript files. | Do not scan the whole home folder. Candidate roots: `$CODEX_HOME/sessions`, `archived_sessions` (default `~/.codex`), `~/.claude/projects`. Existence does not establish readable/complete history. |
| Any host | Supplied Markdown/TXT, supported ChatGPT/Claude JSON or local JSONL, current visible context. | Ask for files/current context only after capability discovery fails. Work with useful visible evidence meanwhile. |

For local roots use `capabilities --local` to report candidate directory existence without reading transcripts. In an authorized broad review, inspect filenames/index metadata first and pass selected supported files to `import`; do not ingest every session to satisfy a 100-record scan. Local roots can contain unrelated work, auxiliary agents, or changing sessions. Exclude auxiliary logs unless necessary evidence; defer files that change during import.

## Native tools

1. Discover within the candidate ceiling, diversifying recent/important/older material if possible. Count unique records. Persist cursors when available.
2. Shortlist from summaries; fetch relevant messages through the latest corrections for selected goals. Check artifacts needed to evaluate the old answer.
3. Preserve source, stable conversation/message IDs, timestamps, project/scope, locators, and completeness. Use only observed or verified app-link formats.
4. Summary-only evidence requires further reading, a narrowed claim, or skipping. Never invent quotations, attachments, or timestamps.

Native observations can be saved in the helper's normalized corpus (see `runtime.md`). Structural validation cannot prove a claimed tool observation is real.

## File shapes

- ChatGPT: conversations with `mapping`; follow parent pointers to `current_node`. Without an active node, preserve leaf branches separately and label ambiguity. Invalid pointers/cycles are errors, not permission to concatenate the graph.
- Claude export: `uuid`, `name`, `chat_messages` with message `uuid`, `sender`, text/content and timestamps. Attachments remain explicit missing evidence.
- Codex JSONL: `session_meta` and `response_item` messages; use `event_msg` user/agent messages only if response messages are absent. Tool/media omissions are flagged.
- Claude Code JSONL: user/assistant events with `sessionId`, `uuid`, `parentUuid`, `message`. Preserve divergent leaf paths; exclude/report sidechains. Tool blocks are not executed.
- Markdown/TXT: standalone `User:`, `Assistant:`, `Human:`, `用户：`, `助手：` or role headings. Respect fenced code. Otherwise retain raw text as `unknown` role; never assume it contains only user facts. Completeness is unknown.

JSON copies preserve native identity. Plain text has no native ID, so its absolute path identifies it. Format support is tested with synthetic structural fixtures; real variants need sanitized samples before being claimed supported.
