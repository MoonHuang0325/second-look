"""Loss-aware transcript normalization. No network calls or command execution."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


class ImportFailure(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def stamp(value):
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, timezone.utc).isoformat()
        except (OverflowError, ValueError, OSError):
            return None
    return str(value) if value else None


def text_content(content):
    """Return visible text plus omission flags; never stringify tool payloads as prose."""
    if isinstance(content, str):
        return content, []
    if content is None:
        return "", []
    if isinstance(content, list):
        values = [text_content(item) for item in content]
        return "\n".join(t for t, _ in values if t), sorted(set(w for _, ws in values for w in ws))
    if not isinstance(content, dict):
        return "", ["unsupported_content"]
    kind = content.get("type", content.get("content_type", ""))
    if kind in ("text", "input_text", "output_text"):
        if isinstance(content.get("text"), str):
            return content["text"], []
        if isinstance(content.get("parts"), list):
            return text_content(content["parts"])
    if kind == "multimodal_text":
        return text_content(content.get("parts", []))
    if kind in ("tool_use", "tool_result", "function_call", "function_call_output", "tool_reference"):
        return "", ["tool_evidence_omitted"]
    if kind in ("thinking", "redacted_thinking", "reasoning"):
        return "", ["reasoning_omitted"]
    return "", ["attachment_or_nontext_omitted"]


def make_message(mid, role, content, when, locator, extra=None):
    text, warnings = text_content(content)
    warnings.extend(extra or [])
    role = {"human": "user", "用户": "user", "助手": "assistant"}.get(role, role)
    if role not in ("user", "assistant", "system", "developer", "tool", "unknown"):
        role = "unknown"
        warnings.append("unknown_role")
    return {"id": str(mid), "role": role, "text": text, "timestamp": stamp(when),
            "locator": locator, "warnings": sorted(set(warnings))}


def record(source, cid, title, messages, locator, branch="main", warnings=None,
           created=None, updated=None, project=None, completeness="text_only"):
    warnings = sorted(set((warnings or []) + [w for m in messages for w in m["warnings"]]))
    result = {"source": source, "id": str(cid), "branch": str(branch), "title": str(title or "Untitled"),
              "created_at": stamp(created), "updated_at": stamp(updated), "project": project,
              "locator": locator, "completeness": completeness, "warnings": warnings, "messages": messages}
    return validate_record(result)


def validate_record(item):
    if not isinstance(item, dict):
        raise ImportFailure("Normalized conversation must be an object")
    for name in ("source", "id", "branch", "title", "locator", "completeness"):
        if not isinstance(item.get(name), str) or not item[name]:
            raise ImportFailure("Missing/invalid conversation field: " + name)
    if item["completeness"] not in ("complete", "text_only", "partial", "summary_only", "unknown"):
        raise ImportFailure("Invalid completeness")
    if not isinstance(item.get("messages"), list) or not item["messages"]:
        raise ImportFailure("Conversation has no messages")
    ids = set()
    for m in item["messages"]:
        if not isinstance(m, dict) or not isinstance(m.get("text"), str):
            raise ImportFailure("Invalid normalized message")
        if not isinstance(m.get("id"), str) or not m["id"] or m["id"] in ids:
            raise ImportFailure("Missing or duplicate message ID")
        ids.add(m["id"])
        if m.get("role") not in ("user", "assistant", "system", "developer", "tool", "unknown"):
            raise ImportFailure("Invalid message role")
        if not isinstance(m.get("locator"), str) or not m["locator"]:
            raise ImportFailure("Missing message locator")
        if not isinstance(m.get("warnings", []), list):
            raise ImportFailure("Invalid message warnings")
    item = dict(item)
    item["warnings"] = sorted(set(item.get("warnings", [])))
    item["key"] = digest([item["source"], item["id"], item["branch"]])[:32]
    # Location changes don't create new content. Evidence/constraints/omission changes do.
    material = {k: v for k, v in item.items() if k not in ("locator", "key", "fingerprint", "created_at", "updated_at")}
    material["messages"] = [{k: v for k, v in m.items() if k != "locator"} for m in item["messages"]]
    item["fingerprint"] = digest(material)
    return item


def graph_paths(nodes, target=None):
    """Follow parents; reject corruption even in an unselected branch."""
    if not nodes:
        raise ImportFailure("Empty message graph")
    parents = {key: node.get("parent") for key, node in nodes.items()}
    for key, parent in parents.items():
        if parent is not None and parent not in nodes:
            raise ImportFailure("Missing graph parent for " + key)
    resolved = set()
    for key in nodes:
        trail = set()
        cursor = key
        while cursor is not None and cursor not in resolved:
            if cursor in trail:
                raise ImportFailure("Cycle in conversation graph")
            trail.add(cursor)
            cursor = parents[cursor]
        resolved.update(trail)
    if target is not None and target not in nodes:
        raise ImportFailure("Active branch points to a missing node")
    leaves = [target] if target is not None else sorted(set(nodes) - set(parents.values()))
    paths = []
    for leaf in leaves:
        path, cursor = [], leaf
        while cursor is not None:
            path.append(cursor)
            cursor = parents[cursor]
        paths.append((leaf, list(reversed(path))))
    return paths


def chatgpt(data, path):
    nodes = data["mapping"]
    if not isinstance(nodes, dict) or any(not isinstance(n, dict) for n in nodes.values()):
        raise ImportFailure("Invalid ChatGPT mapping")
    cid = data.get("id") or data.get("conversation_id") or digest(str(path))[:24]
    active = data.get("current_node")
    records = []
    for leaf, keys in graph_paths(nodes, active):
        messages, warnings = [], []
        if active is None:
            warnings.append("active_branch_unknown")
        for key in keys:
            m = nodes[key].get("message")
            if not m:
                continue
            extra = ["attachment_or_nontext_omitted"] if m.get("metadata", {}).get("attachments") else []
            messages.append(make_message(key, m.get("author", {}).get("role", "unknown"),
                                         m.get("content"), m.get("create_time"),
                                         str(path) + "#mapping/" + key, extra))
        if messages:
            records.append(record("chatgpt", cid, data.get("title"), messages, str(path),
                                  "active" if active else leaf, warnings, data.get("create_time"),
                                  data.get("update_time")))
    if not records:
        raise ImportFailure("ChatGPT graph contains no readable messages")
    return records


def claude_export(data, path):
    cid = data.get("uuid") or data.get("id") or digest(str(path))[:24]
    messages = []
    for i, m in enumerate(data["chat_messages"]):
        if not isinstance(m, dict):
            raise ImportFailure("Invalid Claude message")
        extra = ["attachment_or_nontext_omitted"] if m.get("attachments") or m.get("files") else []
        content = m.get("content") or m.get("text", "")
        messages.append(make_message(m.get("uuid", str(i)), m.get("sender", "unknown"), content,
                                     m.get("created_at"), str(path) + "#chat_messages/" + str(i), extra))
    return [record("claude", cid, data.get("name"), messages, str(path), created=data.get("created_at"),
                   updated=data.get("updated_at"))]


def codex_log(rows, path):
    meta = next((r.get("payload", {}) for _, r in rows if r.get("type") == "session_meta"), {})
    cid = meta.get("id") or digest(str(path))[:24]
    messages, events, warnings = [], [], []
    for line, r in rows:
        payload = r.get("payload", {})
        if not isinstance(payload, dict):
            warnings.append("unsupported_event")
            continue
        if r.get("type") == "response_item":
            if payload.get("type") == "message":
                messages.append(make_message(payload.get("id", str(line)), payload.get("role", "unknown"),
                                             payload.get("content"), r.get("timestamp"), str(path) + ":" + str(line)))
            else:
                warnings.append("tool_or_reasoning_events_omitted")
        elif r.get("type") == "event_msg" and payload.get("type") in ("user_message", "agent_message"):
            events.append(make_message(str(line), "user" if payload["type"] == "user_message" else "assistant",
                                       payload.get("message", ""), r.get("timestamp"), str(path) + ":" + str(line)))
    messages = messages or events
    warnings.append("execution_log_text_only")
    return [record("codex", cid, path.stem, messages, str(path), warnings=warnings,
                   created=meta.get("timestamp"), updated=messages[-1]["timestamp"] if messages else None,
                   project=meta.get("cwd"), completeness="partial")]


def claude_log(rows, path):
    nodes, warnings, session_ids = {}, [], set()
    for line, r in rows:
        if r.get("isSidechain"):
            warnings.append("sidechain_excluded")
            continue
        if r.get("type") not in ("user", "assistant") or not isinstance(r.get("message"), dict):
            continue
        mid = str(r.get("uuid", line))
        if mid in nodes:
            raise ImportFailure("Duplicate Claude Code event ID")
        if r.get("sessionId"):
            session_ids.add(r["sessionId"])
        m = r["message"]
        nodes[mid] = {"parent": r.get("parentUuid"), "message": make_message(
            mid, m.get("role", r["type"]), m.get("content"), r.get("timestamp"), str(path) + ":" + str(line))}
    if len(session_ids) > 1:
        raise ImportFailure("Multiple session IDs in one Claude Code log")
    # Interleaved progress records can be parents. Cut only missing links and expose that loss.
    for node in nodes.values():
        if node["parent"] is not None and node["parent"] not in nodes:
            node["parent"] = None
            warnings.append("parent_context_missing")
    cid = next(iter(session_ids), digest(str(path))[:24])
    paths = graph_paths(nodes)
    result = []
    for leaf, keys in paths:
        messages = [nodes[k]["message"] for k in keys]
        result.append(record("claude-code", cid, path.stem, messages, str(path),
                             "main" if len(paths) == 1 else leaf, warnings + ["execution_log_text_only"],
                             created=messages[0]["timestamp"], updated=messages[-1]["timestamp"],
                             completeness="partial"))
    return result


ROLE = re.compile(r"^(?:#{1,6}\s*)?(User|Human|Assistant|System|Developer|Tool|用户|助手)(?:\s*[:：]\s*(.*)|\s*)$", re.I)


def plain(text, path):
    messages, body, start, role, fence = [], [], 1, "unknown", None

    def flush():
        value = "\n".join(body).strip()
        if value:
            messages.append(make_message(str(start), role, value, None, str(path) + ":" + str(start)))

    for line, value in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", value)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and value.strip() == token:
                fence = None
            body.append(value)
            continue
        match = ROLE.match(value.strip()) if fence is None else None
        if match:
            flush()
            body = [match.group(2)] if match.group(2) else []
            start, role = line, match.group(1).lower()
        else:
            body.append(value)
    flush()
    return [record("text", digest(str(path))[:24], path.stem, messages, str(path),
                   warnings=["transcript_completeness_unknown"], completeness="unknown")]


def load(path, max_bytes=100 * 1024 * 1024):
    path = Path(path).expanduser().resolve()
    before = path.stat()
    if not path.is_file() or before.st_size > max_bytes:
        raise ImportFailure("Not a regular file or exceeds import size limit")
    text = path.read_text(encoding="utf-8-sig")
    after = path.stat()
    if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
        raise ImportFailure("File changed while reading; retry after session settles")
    if path.suffix.lower() in (".md", ".txt"):
        return plain(text, path)
    if path.suffix.lower() == ".jsonl":
        rows = [(i, json.loads(line)) for i, line in enumerate(text.splitlines(), 1) if line.strip()]
        if not rows or any(not isinstance(r, dict) for _, r in rows):
            raise ImportFailure("Invalid JSONL events")
        if any(r.get("type") in ("session_meta", "response_item", "event_msg") for _, r in rows):
            return codex_log(rows, path)
        if any(r.get("type") in ("user", "assistant") for _, r in rows):
            return claude_log(rows, path)
        raise ImportFailure("Unsupported JSONL format")
    if path.suffix.lower() != ".json":
        raise ImportFailure("Use .json, .jsonl, .md or .txt")
    data = json.loads(text)
    if isinstance(data, dict) and data.get("schema_version") == 1 and data.get("kind") == "second-look-corpus":
        return [validate_record(item) for item in data.get("conversations", [])]
    items = data.get("conversations", [data]) if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        raise ImportFailure("Expected a non-empty conversation array")
    records = []
    for item in items:
        if not isinstance(item, dict):
            raise ImportFailure("Invalid conversation object")
        if "mapping" in item:
            records.extend(chatgpt(item, path))
        elif isinstance(item.get("chat_messages"), list):
            records.extend(claude_export(item, path))
        else:
            raise ImportFailure("Unsupported JSON conversation shape")
    return records
