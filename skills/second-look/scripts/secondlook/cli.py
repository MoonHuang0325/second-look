"""Explicit local I/O only; stdout is JSON, errors are nonzero and actionable."""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from . import __version__
from .history import load
from .store import Store, private_directory


def parser():
    p = argparse.ArgumentParser(description="Second Look: private history and review ledger; no model/API calls.")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--store", default=os.environ.get("SECOND_LOOK_DATA_DIR", str(Path.home() / ".local/share/second-look")),
                   help="Private directory outside the public repository/installed skill")
    sub = p.add_subparsers(dest="command", required=True)
    cap = sub.add_parser("capabilities", help="Report helper capabilities, without opening a database")
    cap.add_argument("--local", action="store_true", help="Check known local transcript directory existence only")
    sub.add_parser("status", help="Find pending runs, exclusions, reviewed goals and source count")
    imp = sub.add_parser("import", help="Import explicitly selected transcript files, atomically per file")
    imp.add_argument("paths", nargs="+")
    imp.add_argument("--max-mb", type=int, default=100)
    candidate = sub.add_parser("candidates")
    candidate.add_argument("--limit", type=int, default=100)
    candidate.add_argument("--query")
    candidate.add_argument("--include-inspected", action="store_true")
    candidate.add_argument("--include-excluded", action="store_true")
    read = sub.add_parser("read")
    read.add_argument("key")
    inspect = sub.add_parser("inspected")
    inspect.add_argument("keys", nargs="+")
    for name in ("eligible", "record"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--goal", required=True)
        cmd.add_argument("--keys", nargs="+", required=True)
        cmd.add_argument("--model", help="Observed identifier only; omit if unknown")
        cmd.add_argument("--context", default="", help="Explicit changed circumstances, not generic invocation wording")
        cmd.add_argument("--retry", action="store_true", help="User explicitly requested re-review of this goal")
        if name == "record":
            cmd.add_argument("--outcome", required=True, choices=("supported_improvement", "direction_to_test", "retain_original"))
            cmd.add_argument("--summary", required=True)
            cmd.add_argument("--evidence", nargs="+", required=True)
            cmd.add_argument("--artifact", required=True, help="Already delivered result file/message locator")
    feedback = sub.add_parser("feedback")
    feedback.add_argument("--target", required=True)
    feedback.add_argument("--scope", required=True, choices=("goal", "source"))
    feedback.add_argument("--value", required=True, choices=("exclude", "include", "closed", "accepted", "dismissed"))
    run = sub.add_parser("run")
    run.add_argument("--id")
    run.add_argument("--checkpoint", help="JSON object with progress/cursors, not executable instructions")
    run.add_argument("--finish", action="store_true")
    export = sub.add_parser("export-ledger")
    export.add_argument("--output", required=True, help="New private JSON file; never overwritten")
    restore = sub.add_parser("restore-ledger")
    restore.add_argument("path")
    return p


def capabilities(local=False):
    result = {"version": __version__, "native_history_tools": "host must discover actual exposed tools",
              "formats": ["ChatGPT mapping JSON", "Claude chat_messages JSON", "Codex JSONL",
                          "Claude Code JSONL", "Markdown/TXT", "second-look-corpus v1"],
              "network": False, "telemetry": False, "background_scheduler": False}
    if local:
        codex = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        result["local_candidates"] = [{"path": str(path), "exists": path.is_dir(), "transcripts_read": False}
                                      for path in (codex / "sessions", codex / "archived_sessions", Path.home() / ".claude/projects")]
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    store = None
    code = 0
    try:
        if args.command == "capabilities":
            result = capabilities(args.local)
        else:
            store = Store(args.store)
            if args.command == "status":
                result = store.status()
            elif args.command == "import":
                if args.max_mb <= 0:
                    raise ValueError("--max-mb must be positive")
                result = {"files": [], "errors": []}
                for path in args.paths:
                    try:
                        records = load(path, args.max_mb * 1024 * 1024)
                        result["files"].append({"path": path, "counts": store.ingest(records),
                                                 "keys": [r["key"] for r in records]})
                    except (ValueError, OSError, KeyError, TypeError) as exc:
                        result["errors"].append({"path": path, "error": str(exc)})
                        code = 1
            elif args.command == "candidates":
                result = store.candidates(args.limit, args.query, args.include_inspected, args.include_excluded)
            elif args.command == "read":
                result = store.read(args.key)
            elif args.command == "inspected":
                store.inspect(args.keys)
                result = {"inspected": args.keys}
            elif args.command in ("eligible", "record"):
                options = dict(model=args.model, context=args.context, retry=args.retry)
                if args.command == "eligible":
                    result = store.eligible(args.goal, args.keys, **options)
                else:
                    result = store.review(args.goal, args.keys, args.outcome, args.summary, args.evidence, args.artifact, **options)
            elif args.command == "feedback":
                store.feedback(args.target, args.scope, args.value)
                result = {"target": args.target, "scope": args.scope, "value": args.value}
            elif args.command == "run":
                checkpoint = json.loads(args.checkpoint) if args.checkpoint else None
                if checkpoint is not None and not isinstance(checkpoint, dict):
                    raise ValueError("Checkpoint must be a JSON object")
                if args.finish and not args.id:
                    raise ValueError("--finish requires --id")
                result = store.run(args.id, checkpoint, args.finish)
            elif args.command == "export-ledger":
                output = Path(args.output).expanduser()
                private_directory(output.parent)
                # Exclusive creation prevents overwrites/symlink traversal; permissions before content.
                fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(store.ledger(), f, ensure_ascii=False, indent=2)
                    f.write("\n")
                result = {"output": str(output), "contains_raw_transcripts": False, "private": True}
            elif args.command == "restore-ledger":
                store.restore(json.loads(Path(args.path).read_text(encoding="utf-8")))
                result = {"restored": True}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return code
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    finally:
        if store:
            store.close()
