"""Transactional private corpus and goal-level review ledger."""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .history import digest, validate_record


def now():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def private_directory(path):
    path = Path(path).expanduser().resolve()
    skill_root = Path(__file__).resolve().parents[2]
    if path == skill_root or skill_root in path.parents:
        raise ValueError("Private data must be outside the installed skill")
    for parent in (path, *path.parents):
        if (parent / ".second-look-public").exists():
            raise ValueError("Private data must be outside the public source repository")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


class Store:
    def __init__(self, directory):
        self.directory = private_directory(directory)
        db_path = self.directory / "history.sqlite3"
        if db_path.is_symlink():
            raise ValueError("Refusing a symlinked database")
        # Create with restrictive permissions before SQLite writes any content.
        fd = os.open(str(db_path), os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        self.db = sqlite3.connect(str(db_path), timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=15000")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.db.close()
            raise ValueError("Unsupported database version; use a newer Second Look")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                key TEXT PRIMARY KEY, source TEXT NOT NULL, cid TEXT NOT NULL,
                branch TEXT NOT NULL, fingerprint TEXT NOT NULL, data TEXT NOT NULL,
                inspected_at TEXT, inspected_fingerprint TEXT);
            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY, goal TEXT NOT NULL, signature TEXT NOT NULL,
                model TEXT, context TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS feedback (
                target TEXT NOT NULL, scope TEXT NOT NULL, value TEXT NOT NULL,
                updated_at TEXT NOT NULL, PRIMARY KEY (target, scope));
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, status TEXT NOT NULL, data TEXT NOT NULL, updated_at TEXT NOT NULL);
            PRAGMA user_version=1;
        """)

    def close(self):
        self.db.close()

    def status(self):
        return {"conversation_count": self.db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0],
                "feedback": [dict(r) for r in self.db.execute("SELECT * FROM feedback")],
                "pending_runs": [{"id": r["id"], "checkpoint": json.loads(r["data"]), "updated_at": r["updated_at"]}
                                 for r in self.db.execute("SELECT * FROM runs WHERE status='pending'")],
                "reviewed_goals": [{k: data[k] for k in ("id", "goal", "sources", "outcome", "model", "context", "created_at")}
                                   for data in (json.loads(r[0]) for r in self.db.execute("SELECT data FROM reviews"))]}

    def ingest(self, records):
        records = [validate_record(r) for r in records]
        if not records:
            raise ValueError("No conversations to import")
        by_key = {}
        for r in records:
            if r["key"] in by_key and by_key[r["key"]]["fingerprint"] != r["fingerprint"]:
                raise ValueError("Conflicting duplicate conversation in one import")
            by_key[r["key"]] = r
        stats = {"added": 0, "updated": 0, "unchanged": 0, "retired_branches": 0}
        groups = {}
        for r in by_key.values():
            groups.setdefault((r["source"], r["id"]), set()).add(r["key"])
        with self.db:
            for (source, cid), keys in groups.items():
                old_keys = [row[0] for row in self.db.execute(
                    "SELECT key FROM conversations WHERE source=? AND cid=?", (source, cid))]
                for key in old_keys:
                    if key not in keys:
                        self.db.execute("DELETE FROM conversations WHERE key=?", (key,))
                        stats["retired_branches"] += 1
            for key, r in by_key.items():
                old = self.db.execute("SELECT fingerprint FROM conversations WHERE key=?", (key,)).fetchone()
                stats["added" if old is None else "unchanged" if old[0] == r["fingerprint"] else "updated"] += 1
                self.db.execute("""INSERT INTO conversations(key,source,cid,branch,fingerprint,data)
                    VALUES(?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET
                    fingerprint=excluded.fingerprint,data=excluded.data""",
                                (key, r["source"], r["id"], r["branch"], r["fingerprint"], encode(r)))
        return stats

    def read(self, key):
        row = self.db.execute("SELECT data FROM conversations WHERE key=?", (key,)).fetchone()
        if not row:
            raise ValueError("Unknown conversation key: " + key)
        return json.loads(row[0])

    def candidates(self, limit=100, query=None, include_inspected=False, include_excluded=False):
        if not 1 <= limit <= 100:
            raise ValueError("Candidate limit must be 1–100")
        eligible = []
        for row in self.db.execute("SELECT * FROM conversations"):
            record = json.loads(row["data"])
            feedback = self.feedback_value(row["key"], "source")
            if not include_excluded and feedback in ("exclude", "closed"):
                continue
            seen = row["inspected_fingerprint"] == row["fingerprint"]
            if seen and not include_inspected:
                continue
            if query and query.casefold() not in (record["title"] + "\n" + "\n".join(m["text"] for m in record["messages"])).casefold():
                continue
            record["inspected_at"] = row["inspected_at"]
            eligible.append(record)
        # Deterministic interleaving of recent and older unseen work; not semantic ranking.
        eligible.sort(key=lambda r: (r.get("updated_at") or r.get("created_at") or "", r["key"]))
        total = len(eligible)
        chosen = []
        while eligible and len(chosen) < limit:
            chosen.append(eligible.pop() if len(chosen) % 3 != 2 else eligible.pop(0))
        result = []
        for r in chosen:
            result.append({k: r.get(k) for k in ("key", "source", "id", "branch", "title", "project",
                                                "created_at", "updated_at", "completeness", "warnings", "locator")})
            result[-1].update({"fingerprint": r["fingerprint"], "message_count": len(r["messages"]),
                               "preview": "\n".join(m["text"] for m in r["messages"] if m["role"] == "user")[:800]})
        return {"candidates": result, "eligible_count": total, "returned": len(result),
                "coverage": "Imported corpus only; previews are not full evidence; no semantic ranking."}

    def inspect(self, keys):
        with self.db:
            for key in keys:
                self.read(key)
                self.db.execute("UPDATE conversations SET inspected_at=?,inspected_fingerprint=fingerprint WHERE key=?", (now(), key))

    def feedback_value(self, target, scope):
        row = self.db.execute("SELECT value FROM feedback WHERE target=? AND scope=?", (target, scope)).fetchone()
        return row[0] if row else None

    def feedback(self, target, scope, value):
        if scope not in ("source", "goal") or value not in ("exclude", "include", "closed", "accepted", "dismissed"):
            raise ValueError("Invalid feedback scope/value")
        if not target:
            raise ValueError("Feedback target is required")
        if scope == "source":
            self.read(target)
        with self.db:
            self.db.execute("""INSERT INTO feedback VALUES(?,?,?,?) ON CONFLICT(target,scope)
                DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""", (target, scope, value, now()))

    def signature(self, keys):
        if not keys or len(set(keys)) != len(keys):
            raise ValueError("Provide unique source keys")
        return digest(sorted((key, self.read(key)["fingerprint"]) for key in keys))

    def eligible(self, goal, keys, model=None, context="", retry=False):
        if not goal:
            raise ValueError("A stable goal ID is required")
        signature = self.signature(keys)
        blocked = self.feedback_value(goal, "goal") in ("exclude", "closed") or any(
            self.feedback_value(k, "source") in ("exclude", "closed") for k in keys)
        if blocked and not retry:
            return {"eligible": False, "reason": "explicit_exclusion", "signature": signature}
        if retry:
            return {"eligible": True, "reason": "explicit_retry", "signature": signature}
        # Unknown model is not a change signal. Any matching review prevents duplication.
        rows = self.db.execute("SELECT model FROM reviews WHERE goal=? AND signature=? AND context=?",
                               (goal, signature, context)).fetchall()
        matched = any(model is None or row["model"] is None or model == row["model"] for row in rows)
        return {"eligible": not matched, "reason": "unchanged_reviewed_goal" if matched else "new_or_changed",
                "signature": signature}

    def review(self, goal, keys, outcome, summary, evidence, artifact, model=None, context="", retry=False):
        if outcome not in ("supported_improvement", "direction_to_test", "retain_original"):
            raise ValueError("Invalid review outcome")
        if not summary.strip() or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
            raise ValueError("Review needs a summary and observed evidence locators")
        if not artifact or not artifact.strip():
            raise ValueError("Record only after delivery; provide a result file/message locator")
        check = self.eligible(goal, keys, model, context, retry)
        if not check["eligible"]:
            raise ValueError(check["reason"])
        rid = str(uuid.uuid4())
        data = {"id": rid, "goal": goal, "sources": [{"key": k, "fingerprint": self.read(k)["fingerprint"]} for k in keys],
                "outcome": outcome, "summary": summary, "evidence": evidence, "artifact": artifact,
                "model": model, "context": context, "created_at": now()}
        with self.db:
            self.db.execute("INSERT INTO reviews VALUES(?,?,?,?,?,?,?)",
                            (rid, goal, check["signature"], model, context, encode(data), data["created_at"]))
        return data

    def run(self, rid=None, checkpoint=None, finish=False):
        if rid is None:
            rid = str(uuid.uuid4())
            with self.db:
                self.db.execute("INSERT INTO runs VALUES(?,?,?,?)", (rid, "pending", encode(checkpoint or {}), now()))
        else:
            row = self.db.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
            if not row:
                raise ValueError("Unknown run ID")
            if checkpoint is not None or finish:
                if row["status"] == "complete":
                    raise ValueError("Completed run is immutable; start another run")
                with self.db:
                    self.db.execute("UPDATE runs SET status=?,data=?,updated_at=? WHERE id=?",
                                    ("complete" if finish else "pending", encode(checkpoint) if checkpoint is not None else row["data"], now(), rid))
        row = self.db.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
        return {"id": rid, "status": row["status"], "checkpoint": json.loads(row["data"]), "updated_at": row["updated_at"]}

    def ledger(self):
        # No raw transcript text. Still private: summaries, paths, and feedback can be sensitive.
        return {"kind": "second-look-ledger", "schema_version": 1,
                "sources": [dict(r) for r in self.db.execute("SELECT key,fingerprint,inspected_at,inspected_fingerprint FROM conversations")],
                "reviews": [dict(r) for r in self.db.execute("SELECT * FROM reviews")],
                "feedback": [dict(r) for r in self.db.execute("SELECT * FROM feedback")],
                "runs": [dict(r) for r in self.db.execute("SELECT * FROM runs")]}

    def restore(self, ledger):
        if ledger.get("kind") != "second-look-ledger" or ledger.get("schema_version") != 1:
            raise ValueError("Unsupported ledger")
        # A transaction makes a malformed restore all-or-nothing. Restore only into an empty ledger.
        if any(self.db.execute("SELECT 1 FROM " + table + " LIMIT 1").fetchone() for table in ("reviews", "feedback", "runs")):
            raise ValueError("Restore requires an empty ledger; use a new store and import sources first")
        with self.db:
            for r in ledger.get("reviews", []):
                data = json.loads(r["data"])
                if data.get("id") != r["id"] or data.get("goal") != r["goal"]:
                    raise ValueError("Invalid review in ledger")
                self.db.execute("INSERT INTO reviews VALUES(?,?,?,?,?,?,?)", tuple(r[k] for k in
                                ("id", "goal", "signature", "model", "context", "data", "created_at")))
            for r in ledger.get("feedback", []):
                if r["scope"] not in ("goal", "source") or r["value"] not in ("exclude", "include", "closed", "accepted", "dismissed"):
                    raise ValueError("Invalid feedback in ledger")
                self.db.execute("INSERT INTO feedback VALUES(?,?,?,?)", tuple(r[k] for k in ("target", "scope", "value", "updated_at")))
            for r in ledger.get("runs", []):
                if r["status"] not in ("pending", "complete"):
                    raise ValueError("Invalid run status")
                json.loads(r["data"])
                self.db.execute("INSERT INTO runs VALUES(?,?,?,?)", tuple(r[k] for k in ("id", "status", "data", "updated_at")))
            for r in ledger.get("sources", []):
                self.db.execute("UPDATE conversations SET inspected_at=?,inspected_fingerprint=? WHERE key=? AND fingerprint=?",
                                (r["inspected_at"], r["inspected_fingerprint"], r["key"], r["fingerprint"]))
